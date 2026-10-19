"""Ordinary installed positive-only gradient/EMA/geometry contracts; no assets."""
import copy
import unittest

import numpy as np
import torch
from torch import nn
from torch.nn import functional as F

from dl_binner.multiview.model import Encoder
from dl_binner.multiview.positive import initialize, update_target, pair_loss, geometry
from dl_binner.multiview.views import config
from dl_binner.model import configure_torch


def policy():
    """Return the prospective defaults over the accepted parent/view policy."""
    return config() | dict(positive_only=True, predictor_hidden=128, ema_base=.996,
                          collapse_rows=8192, collapse_min_std=.001, collapse_min_rank=2)


class PositiveContracts(unittest.TestCase):
    def setUp(self):
        configure_torch(4)

    def test_ragged_pair_oracle_no_cross_parent_labels_stopped_target_and_singletons(self):
        torch.manual_seed(11)
        z = torch.randn(6, 8, requires_grad=True)
        target = torch.randn(6, 8, requires_grad=True)
        owners = torch.tensor([0, 1, 0, 2, 1, 0]); weights = torch.tensor([.7, 2., 1.])
        head = nn.Linear(8, 8)
        actual = pair_loss(z, target, owners, weights, head)
        q = F.normalize(head(z), dim=1); t = F.normalize(target.detach(), dim=1)
        per = []
        for parent in [0, 1]:
            ix = torch.where(owners == parent)[0]
            per.append(torch.stack([(q[i]-t[j]).square().sum() for i in ix for j in ix if i != j]).mean())
        oracle = (per[0]*weights[0]+per[1]*weights[1])/weights[:2].sum()
        torch.testing.assert_close(actual, oracle)
        actual.backward()
        self.assertIsNone(target.grad)
        self.assertGreater(float(z.grad.abs().sum()), 0)
        self.assertEqual(float(z.grad[3].abs().sum()), 0)  # singleton
        different = target.detach().clone(); different[3] *= 100
        torch.testing.assert_close(pair_loss(z, different, owners, weights, head), actual.detach())
        single = torch.randn(1, 8, requires_grad=True)
        loss = pair_loss(single, single, torch.tensor([0]), torch.ones(1), head)
        self.assertEqual(loss.item(), 0); loss.backward()
        self.assertEqual(float(single.grad.abs().sum()), 0)
        with self.assertRaisesRegex(ValueError, 'axes'):
            pair_loss(z, target[:2], owners, weights, head)

    def test_exact_encoder_initialization_target_stop_and_named_buffer_EMA(self):
        cfg = policy()
        for samples in [0, 10]:
            torch.manual_seed(11); old = Encoder(samples, cfg)
            torch.manual_seed(11); online, teacher, predictors = initialize(samples, cfg)
            for key in old.state_dict():
                self.assertTrue(torch.equal(old.state_dict()[key], online.state_dict()[key]), key)
                self.assertTrue(torch.equal(online.state_dict()[key], teacher.state_dict()[key]), key)
            self.assertFalse(teacher.training)
            self.assertTrue(all(not p.requires_grad for p in teacher.parameters()))
            self.assertTrue(all(p.requires_grad for p in predictors.parameters()))
        a = nn.Sequential(nn.Linear(4, 3), nn.BatchNorm1d(3)); b = copy.deepcopy(a)
        with torch.no_grad():
            for p in a.parameters(): p.add_(2)
            a[1].running_mean.add_(4); a[1].num_batches_tracked.add_(7)
        before = {k: v.clone() for k, v in b.state_dict().items()}
        update_target(a, b, .75)
        for k, v in b.state_dict().items():
            if v.is_floating_point(): torch.testing.assert_close(v, .75*before[k]+.25*a.state_dict()[k])
            else: self.assertTrue(torch.equal(v, a.state_dict()[k]))

    def test_noncollapse_monitor_rejects_constant_and_rank_one_units(self):
        cfg = policy(); rng = np.random.default_rng(11)
        values = rng.normal(size=(256, 64)); values /= np.linalg.norm(values, axis=1, keepdims=True)
        good = geometry(values, cfg)
        self.assertGreater(good['effective_rank'], 20)
        for x in [np.tile(values[0], (256, 1)), np.tile(values[0], (256, 1))*np.where(np.arange(256)[:, None] % 2, 1, -1)]:
            with self.assertRaisesRegex(ValueError, 'collapse'): geometry(x, cfg)
        bad = values.copy(); bad[0, 0] = float('nan')
        with self.assertRaisesRegex(ValueError, 'unit vectors'): geometry(bad, cfg)

    def test_masked_depth_cannot_leak_and_sequence_only_branch_exists(self):
        cfg=policy();torch.manual_seed(11)
        for samples in [0,10]:
            model,teacher,_=initialize(samples,cfg)
            x=F.normalize(torch.randn(5,136),dim=1);mask=torch.zeros(5,dtype=torch.bool)
            d=torch.randn(5,samples);other=torch.randn(5,samples)*1000
            for m in [model,teacher]:
                a=m(x,d,mask);b=m(x,other,mask)
                for v,w in zip(a,b):
                    self.assertTrue(torch.equal(v,w));torch.testing.assert_close(v.norm(dim=1),torch.ones(5))


if __name__ == '__main__': unittest.main()
