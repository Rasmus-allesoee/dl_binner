"""Strict label-free admission of the two reconstruction-weight override."""
CONTROL_KEYS={'composition_reconstruction_weight','depth_reconstruction_weight'}


def validate_control(cfg,bank_policy):
    """Permit exactly two zeroed weights; refuse any other bank/schedule mismatch."""
    if set(cfg)!=set(bank_policy) or any(type(cfg[k]) not in (int,float) or cfg[k]!=0 for k in CONTROL_KEYS):
        raise ValueError('Exactly two zero reconstruction weights required')
    changed={k for k in cfg if cfg[k]!=bank_policy[k]}
    if changed!=CONTROL_KEYS or any(bank_policy[k]<=0 for k in CONTROL_KEYS):
        raise ValueError('Retained view policy differs beyond the two reconstruction weights')
