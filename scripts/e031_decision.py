#!/usr/bin/env python3
"""Frozen integer-denominator E031 decisions; no evaluator, fitting or selection.

Inputs are admitted student recovery summaries. This function cannot select bins,
thresholds, features or a different policy per dataset. Practical thresholds are
scoped development criteria, not biological or statistical significance claims.
"""
from fractions import Fraction

UNITS=['E009-noGLM','E009-GLM','oral-noGLM']
REFERENCES={'E009-noGLM':554661890,'E009-GLM':554661890,'oral-noGLM':2083072211}


def metric(value,unit):
    """Validate full provided denominators and integer recovered source unions."""
    if (set(value)!={'recovered_bp','reference_bp','target_90'} or
            any(type(v) is not int for v in value.values()) or value['reference_bp']!=REFERENCES[unit] or
            not 0<=value['recovered_bp']<=value['reference_bp'] or
            not 0<=value['target_90']<=(799 if unit=='oral-noGLM' else 156)):
        raise ValueError('Full-denominator integer recovery contract differs')
    return Fraction(value['recovered_bp'],value['reference_bp'])


def disposition(comparison,old,new,anchors):
    """Return unchanged KEEP/MODIFY/ABANDON with all three modes accounted for."""
    if comparison not in ['bridge','learning'] or set(old)!=set(UNITS) or set(new)!=set(UNITS):
        raise ValueError('All three fixed modes required; no winner routing')
    before={u:metric(old[u],u) for u in UNITS};after={u:metric(new[u],u) for u in UNITS}
    nonregression=all(after[u]>=before[u] and new[u]['target_90']>=old[u]['target_90'] for u in UNITS)
    if comparison=='bridge':
        meaningful=after['oral-noGLM']-before['oral-noGLM']>=Fraction(1,200)
        keep=nonregression and meaningful
        examined=['E009-noGLM','oral-noGLM']
    else:
        if set(anchors)!={'E009-GLM','oral-noGLM'}:raise ValueError('Both fixed historical anchors required')
        meaningful=any(after[u]>=metric(anchors[u],u) for u in anchors)
        keep=nonregression and meaningful
        examined=['E009-GLM','oral-noGLM']
    abandon=not any(after[u]>before[u] or new[u]['target_90']>old[u]['target_90'] for u in examined)
    return dict(disposition='KEEP' if keep else 'ABANDON' if abandon else 'MODIFY',
        all_mode_nonregression=nonregression,practical_criterion=meaningful,
        gains={u:dict(recovered_bp=new[u]['recovered_bp']-old[u]['recovered_bp'],
                      R95_percentage_points=float((after[u]-before[u])*100),
                      target_90=new[u]['target_90']-old[u]['target_90']) for u in UNITS},
        primary_rule_changed=False,truth_selected_routing=False)
