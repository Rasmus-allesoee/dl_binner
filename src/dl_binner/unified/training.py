"""One frozen learning policy with GLM availability propagated through all stages.

Both bootstrap and marker-informed student use the declared context or hybrid
encoder, actual parent-depth branch, real view bank and identical exposure and
schedule. No historical teacher, pair proposal, labels or bin identity enters.
"""
import json
from pathlib import Path

from ..relational.pairs import policy as pair_policy
from ..relational.evidence import require


def configuration(glm=False, engineering=False, epochs=None):
    """Return the single common default; only bounded fixtures may alter epochs."""
    require(type(glm) is bool and type(engineering) is bool, 'Explicit Boolean GLM/engineering modes required')
    # Configuration is also needed by graph-only workers. Keep tensor libraries
    # out of that process; exactly match the inherited validated defaults.
    from ..multiview.views import config as view_config
    from ..context.tokens import policy as context_policy
    from ..hybrid.bank import policy as hybrid_policy
    cfg = dict(view_config(), positive_only=True, predictor_hidden=128, ema_base=.996,
        collapse_rows=8192, collapse_min_std=.001, collapse_min_rank=2, context=context_policy())
    if glm: cfg['hybrid'] = hybrid_policy()
    if epochs is not None:
        require(engineering and type(epochs) is int and 1 <= epochs <= 20,
                'Only tiny engineering schedules may differ')
        cfg['epochs'] = epochs
    return cfg


def bootstrap(features, views, tokens, frozen, output, cfg, threads=4):
    """Fit one fresh self-view teacher with the same availability as its student."""
    require(('hybrid' in cfg) == (frozen is not None), 'Bootstrap GLM availability differs')
    if frozen is None:
        from ..context import model as context
        return context.train(features, views, tokens, output, cfg, threads)
    from ..hybrid import model as hybrid
    return hybrid.train(features, views, tokens, frozen, output, cfg, threads)


def reload_bootstrap(features, views, tokens, frozen, checkpoint, output, threads=4):
    """Require native exact same-runtime reload; no portability tolerance change."""
    if frozen is None:
        from ..context import model as context
        return context.embed(features, views, tokens, checkpoint, output, threads)
    from ..hybrid import model as hybrid
    return hybrid.embed(features, views, tokens, frozen, checkpoint, output, threads)


def student(features, views, tokens, frozen, pairs, output, cfg, threads=4):
    """Train the reliable signed-marker student on its own fresh bootstrap pairs."""
    require(('hybrid' in cfg) == (frozen is not None), 'Student GLM availability differs')
    from ..relational import model as relational
    return relational.train(features, views, tokens, frozen, pairs, output,
                            dict(cfg, relational=pair_policy()), threads)


def information_contract(glm, verified_learning_reuse=False):
    """Describe information from teacher through proposals, rather than student flags alone."""
    return dict(version=1, sequence='retained real full-parent/crop composition and eight bounded context tokens',
        depth='ten genuine full-parent read-derived means; positive-evidence dropout; zeros observed, not missing',
        frozen_GLM=bool(glm), bootstrap_GLM=bool(glm), proposal_teacher_GLM=bool(glm),
        student_GLM=bool(glm), identical_accepted_learning_reused=bool(verified_learning_reuse),
        undeclared_historical_teacher_reused=False, truth_accessed=False,
        student_initialized_from_bootstrap=False,
        marker_pairs='cached reliable physical loci plus fresh teacher reciprocal neighbors and composition/depth context',
        common_source_defaults=True, seed=11, epochs=20, batch_size=256)
