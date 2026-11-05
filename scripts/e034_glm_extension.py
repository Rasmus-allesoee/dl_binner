#!/usr/bin/env python3
"""Prepare an explicit future Oral GLM state extension, never execute extraction.

This is a local engineering adapter, outside E034 graph training. The caller must
separately admit a full view-matched bank, source-blind GLM-aware teacher and pair
proposals before a future community fit. No old checkpoint is relabelled in place.
"""
import copy


def extend(saved):
    """Preserve context weights/EMA/predictors/Adam slots; append zero GLM residual.

    Input is a validated no-GLM bootstrap checkpoint dictionary. Returns new online,
    stopped EMA, predictors, frozen anchor, optimizer and an engineering receipt.
    New GLM parameters have no manufactured Adam moments. Old bytes are read-only.
    """
    import torch
    from dl_binner.bootstrap.model import initialize,state_digest
    from dl_binner.hybrid.model import Encoder
    from dl_binner.hybrid.bank import policy
    if saved.get('kind')!='context_checkpoint' or 'hybrid' in saved['config']:
        raise ValueError('Explicit no-GLM bootstrap required; do not silently extend another topology')
    before=torch.get_rng_state().clone()
    with torch.random.fork_rng(devices=[]):
        old,old_target,predictors,old_anchor,old_optimizer=initialize(saved)
        cfg=dict(saved['config'],hybrid=policy());model=Encoder(len(saved['samples']),cfg)
        new_keys=set(model.state_dict())-set(old.state_dict())
        if not new_keys or any(not k.startswith('frozen_') for k in new_keys):
            raise ValueError('Extension changed existing topology')
        state=model.state_dict();state.update(old.state_dict());model.load_state_dict(state,strict=True)
        target=copy.deepcopy(model).requires_grad_(False).eval()
        state=target.state_dict();state.update(old_target.state_dict());target.load_state_dict(state,strict=True)
        old_names=dict(old.named_parameters());names=dict(model.named_parameters());predictor_params=list(predictors.parameters())
        existing=[names[n] for n in old_names]+predictor_params
        group=copy.deepcopy({k:v for k,v in old_optimizer.param_groups[0].items() if k!='params'})
        optimizer=torch.optim.AdamW([dict(group,params=existing)])
        pairs=[(p,names[n]) for n,p in old_names.items()]+[(p,p) for p in predictor_params]
        for src,dst in pairs:
            if src in old_optimizer.state:optimizer.state[dst]=copy.deepcopy(old_optimizer.state[src])
        added=[p for n,p in names.items() if n not in old_names]
        optimizer.add_param_group(dict(group,params=added))
        anchor=copy.deepcopy(model).requires_grad_(False).eval()
        if any(not torch.equal(model.state_dict()[n],v) for n,v in old.state_dict().items()):raise ValueError('Old online state changed')
        if any(not torch.equal(target.state_dict()[n],v) for n,v in old_target.state_dict().items()):raise ValueError('Old EMA state changed')
        for src,dst in pairs:
            if (src in old_optimizer.state)!=(dst in optimizer.state):raise ValueError('Adam state availability changed')
            if src in old_optimizer.state and any(not torch.equal(v,optimizer.state[dst][k]) for k,v in old_optimizer.state[src].items()):raise ValueError('Adam slot/step changed')
        if any(p in optimizer.state for p in added):raise ValueError('New GLM Adam slots invented')
        receipt=dict(status='ENGINEERING_ONLY',old_online=state_digest(old),old_target=state_digest(old_target),old_predictors=state_digest(predictors),
            new_parameters=sorted(new_keys),old_parameter_slots_preserved=True,new_Adam_state='absent_until_exercised',
            stopped_target=True,full_GLM_bank_admitted=False,GLM_teacher_and_proposals_admitted=False,community_execution=False)
    if not torch.equal(before,torch.get_rng_state()):raise ValueError('Extension consumed caller RNG')
    return model,target,predictors,anchor,optimizer,receipt
