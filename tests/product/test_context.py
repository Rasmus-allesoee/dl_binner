"""Actual installed context token/attention/EMA contracts, without research assets."""
import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

import numpy as np
import torch
from torch.nn import functional as F

from dl_binner.candidate.model import fit_transform
from dl_binner.context.tokens import tokenize, reverse_complement, parent_coordinates, prepare, Bank, binding
from dl_binner.context.model import config, Encoder, initialize
from dl_binner.io import DNA
from dl_binner.model import configure_torch
from dl_binner.multiview.positive import pair_loss, update_target, geometry
from dl_binner.multiview.views import prepare as prepare_views, config as view_config, load


class ContextContracts(unittest.TestCase):
    """Exercise exact sequence/coordinate and numerical contracts on real tiny inputs."""

    def setUp(self):
        configure_torch(4)

    def test_strand_canonical_IUPAC_counts_and_coordinates(self):
        rng = np.random.default_rng(55)
        for length in [1, 3, 31, 255, 256, 499, 500, 767, 768, 999, 2500, 11001]:
            dna = ''.join(rng.choice(list('ACGTRYSWKMBDHVN'), length))
            a, xy, flipped = tokenize(dna)
            b, other_xy, other_flipped = tokenize(reverse_complement(dna))
            self.assertTrue(np.array_equal(a, b))
            self.assertTrue(np.array_equal(xy, other_xy))
            canonical = min(dna, reverse_complement(dna))
            from dl_binner.candidate.views import composition
            for counts, (start, stop) in zip(a, xy):
                if start < 0:
                    self.assertFalse(counts.any())
                    continue
                self.assertLessEqual(stop-start, 512)
                frequency, total = composition(canonical[start:stop])
                self.assertTrue(np.array_equal(np.rint(frequency*total).astype(np.uint16), counts))
                x, y = parent_coordinates(start, stop, 97, 97+length, flipped)
                window = dna[x-97:y-97]
                if flipped:
                    window = reverse_complement(window)
                self.assertEqual(window, canonical[start:stop])
        self.assertEqual(set(reverse_complement(''.join(sorted(DNA)))), set(DNA))
        with self.assertRaisesRegex(ValueError, 'nonempty'):
            tokenize('')
        with self.assertRaisesRegex(ValueError, 'IUPAC'):
            tokenize('ACGT-')
        with self.assertRaisesRegex(ValueError, 'coordinate'):
            parent_coordinates(0, 9, 0, 8, False)

    def test_partial_ambiguity_and_all_N_are_not_fabricated_evidence(self):
        counts, xy, _ = tokenize('N'*500)
        self.assertEqual(int(counts.sum()), 0)
        self.assertEqual(tuple(xy[0]), (0, 500))
        counts, _, _ = tokenize('A'*256+'N'*256+'C'*256)
        self.assertGreater(int(counts.sum()), 0)
        self.assertLess(int(counts.sum()), 768-3)

    def test_integer_bank_actual_reader_axes_coordinates_masks_and_corruption_refusal(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fasta = root/'tiny.fa'
            fasta.write_text('>opaque-z\n'+'ACGT'*700+'\n>opaque-a\n'+'AGCT'*160+'\n>short\nACG\n>ambiguous\n'+'N'*900+'\n')
            cfg = view_config()
            prepare_views(fasta, None, root/'features', cfg)
            features, views = root/'features/features.npz', root/'features/views.npz'
            before = {p.name: binding(p) for p in (root/'features').iterdir()}
            prepare(fasta, features, views, root/'tokens')
            data, meta, v, vm = load(features, views)
            bank = Bank(root/'tokens', features, views, data, meta, v)
            self.assertIsInstance(bank.counts, np.memmap)
            self.assertFalse(bank.counts.flags.writeable)
            self.assertEqual(bank.rows.tolist(), [0, 1])
            tokens, positions, mask = bank.batch(np.array([0, 1]), np.array([0, 0]), fit_transform(data))
            self.assertTrue(np.isfinite(tokens).all())
            self.assertTrue(np.isfinite(positions).all())
            self.assertEqual(mask.dtype, bool)
            self.assertTrue(mask.any())
            with self.assertRaisesRegex(ValueError, 'axes'):
                bank.batch(np.array([2]), np.array([0]), fit_transform(data))
            self.assertEqual(before, {p.name: binding(p) for p in (root/'features').iterdir()})
            path = root/'tokens/counts.npy'
            with path.open('r+b') as stream:
                stream.seek(-1, 2)
                stream.write(b'!')
            with self.assertRaisesRegex(ValueError, 'Corrupt'):
                Bank(root/'tokens', features, views, data, meta, v)
            self.assertFalse((root/'tokens/fallback').exists())

    def args(self, samples=10):
        """Generate finite tensors with explicit synthetic parent means and masked tokens."""
        torch.manual_seed(11)
        return [F.normalize(torch.randn(8, 136), dim=1), torch.randn(8, samples),
            torch.tensor([True, False]*4), torch.randn(8, 8, 136), torch.rand(8, 8, 3),
            torch.tensor([[True, True, False, False, False, False, False, False]]*8)]

    def test_attention_changes_with_real_local_content_and_relative_position(self):
        cfg = config()
        model = Encoder(10, cfg).eval()
        # A learned nonzero residual exposes content sensitivity; the frozen
        # initial zero residual deliberately reproduces the parent model.
        torch.nn.init.xavier_uniform_(model.context_projection.weight)
        args = self.args()
        before = model(*args)[0]
        changed = [x.clone() for x in args]
        changed[3][:, 0] *= -1
        self.assertGreater(float((model(*changed)[0]-before).abs().max()), 1e-5)
        changed = [x.clone() for x in args]
        changed[4][:, 0, 0] = 1-changed[4][:, 0, 0]
        self.assertGreater(float((model(*changed)[0]-before).abs().max()), 1e-6)
        with self.assertRaisesRegex(ValueError, 'Nonfinite'):
            changed[3][0, 0, 0] = float('nan')
            model(*changed)

    def test_padding_missing_depth_all_masked_tokens_and_sequence_only_modes(self):
        cfg = config()
        for samples in [0, 10]:
            model = Encoder(samples, cfg).eval()
            torch.nn.init.xavier_uniform_(model.context_projection.weight)
            args = self.args(samples)
            args[2][:] = False
            before = model(*args)
            changed = [x.clone() for x in args]
            changed[1][:] = 10000
            changed[3][~changed[5]] = 1234
            changed[4][~changed[5]] = -1234
            after = model(*changed)
            for a, b in zip(before, after):
                self.assertTrue(torch.equal(a, b))
                torch.testing.assert_close(a.norm(dim=1), torch.ones(8))
            args[5][:] = False
            for a in model(*args):
                self.assertTrue(torch.isfinite(a).all())
                torch.testing.assert_close(a.norm(dim=1), torch.ones(8))

    def test_real_context_gradient_stopped_target_EMA_exact_initialization(self):
        cfg = config()
        torch.manual_seed(11)
        online, teacher, heads = initialize(10, cfg)
        self.assertTrue(all(not p.requires_grad for p in teacher.parameters()))
        self.assertTrue(all(torch.equal(v, teacher.state_dict()[k]) for k, v in online.state_dict().items()))
        args = self.args()
        args[3].requires_grad_(True)
        z, _ = online(*args)
        with torch.no_grad():
            wanted, _ = teacher(*args)
        loss = pair_loss(z, wanted, torch.tensor([0, 0, 1, 1, 2, 2, 3, 3]), torch.ones(4), heads[0])
        loss.backward()
        self.assertGreater(float(online.context_projection.weight.grad.abs().sum()), 0)
        self.assertEqual(float(online.attention.in_proj_weight.grad.abs().sum()), 0)
        # The projection learns first; attention receives an actual gradient on
        # the next step. A permanent detached/dead context branch would fail.
        optimizer = torch.optim.SGD(list(online.parameters())+list(heads.parameters()), lr=.01)
        optimizer.step()
        optimizer.zero_grad(set_to_none=True)
        args[3].grad = None
        z, _ = online(*args)
        loss = pair_loss(z, wanted, torch.tensor([0, 0, 1, 1, 2, 2, 3, 3]), torch.ones(4), heads[0])
        loss.backward()
        self.assertGreater(float(online.attention.in_proj_weight.grad.abs().sum()), 0)
        self.assertGreater(float(args[3].grad[args[5]].abs().sum()), 0)
        self.assertEqual(float(args[3].grad[~args[5]].abs().sum()), 0)
        self.assertTrue(all(p.grad is None for p in teacher.parameters()))
        old = {k: v.clone() for k, v in teacher.state_dict().items()}
        with torch.no_grad():
            online.token_projection.weight.add_(.1)
        update_target(online, teacher, .75)
        for k, value in teacher.state_dict().items():
            torch.testing.assert_close(value, .75*old[k]+.25*online.state_dict()[k])
        torch.manual_seed(11)
        fresh, _, _ = initialize(10, cfg)
        torch.manual_seed(11)
        direct = Encoder(10, cfg)
        self.assertTrue(all(torch.equal(v, direct.state_dict()[k]) for k, v in fresh.state_dict().items()))
        from dl_binner.multiview.positive import initialize as parent_initialize
        torch.manual_seed(11)
        parent, _, old_predictors = parent_initialize(10, cfg)
        torch.manual_seed(11)
        preserved, _, new_predictors = initialize(10, cfg)
        self.assertTrue(all(torch.equal(v, preserved.state_dict()[k]) for k, v in parent.state_dict().items()))
        self.assertTrue(all(torch.equal(v, new_predictors.state_dict()[k]) for k, v in old_predictors.state_dict().items()))
        parent.eval(); preserved.eval()
        with torch.no_grad():
            for x, y in zip(parent(*args[:3]), preserved(*args)):
                self.assertTrue(torch.equal(x, y))
        rng = np.random.default_rng(11)
        x = rng.normal(size=(192, 64)); x /= np.linalg.norm(x, axis=1, keepdims=True)
        self.assertGreater(geometry(x, cfg)['effective_rank'], 2)
        with self.assertRaisesRegex(ValueError, 'collapse'):
            geometry(np.tile(x[0], (192, 1)), cfg)


if __name__ == '__main__':
    unittest.main()
