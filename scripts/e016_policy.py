"""Pure configuration admission for the stdlib workflow parent; no numerical imports."""
def validate_policy(cfg, bank_policy):
    """Admit only declared training additions to an unchanged retained view bank."""
    extra = {'positive_only', 'predictor_hidden', 'ema_base', 'collapse_rows',
             'collapse_min_std', 'collapse_min_rank'}
    if set(cfg) != set(bank_policy) | extra or any(cfg[k] != v for k, v in bank_policy.items()):
        raise ValueError('Retained bank or positive-only training policy differs')
    if (cfg['positive_only'] is not True or cfg['predictor_hidden'] != 128 or
            cfg['ema_base'] != .996 or cfg['collapse_rows'] != 8192 or
            cfg['collapse_min_std'] != .001 or cfg['collapse_min_rank'] != 2):
        raise ValueError('Unfrozen positive-only defaults')
