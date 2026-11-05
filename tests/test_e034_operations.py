"""Real engineering state/transport/schema contracts, without cloud mutations."""
import copy,io,json,sys,tarfile,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).absolute().parents[1];sys.path.insert(0,str(ROOT/'scripts'))

class OralGLMState(unittest.TestCase):
    def test_state_optimizer_zero_residual_and_reload(self):
        import torch
        from dl_binner.context.model import initialize,config
        from dl_binner.hybrid.model import Encoder
        from e034_glm_extension import extend
        torch.set_num_threads(4);torch.manual_seed(11);cfg=config();old,ema,predictors=initialize(10,cfg)
        opt=torch.optim.AdamW(list(old.parameters())+list(predictors.parameters()),lr=cfg['learning_rate'],weight_decay=cfg['weight_decay'])
        sum(p.square().sum() for p in list(old.parameters())+list(predictors.parameters())).backward();opt.step();opt.zero_grad(set_to_none=True)
        saved=dict(kind='context_checkpoint',config=cfg,samples=[str(i) for i in range(10)],model_state=copy.deepcopy(old.state_dict()),target_state=ema.state_dict(),predictor_state=predictors.state_dict(),optimizer_state=copy.deepcopy(opt.state_dict()),ema_updates=1)
        rng=torch.get_rng_state().clone();model,target,preds,anchor,newopt,r=extend(saved);self.assertTrue(torch.equal(rng,torch.get_rng_state()));self.assertFalse(r['community_execution']);self.assertFalse(target.training)
        for n,v in old.state_dict().items():self.assertTrue(torch.equal(model.state_dict()[n],v))
        n=3;t=cfg['context']['tokens'];args=[torch.randn(n,136),torch.randn(n,10),torch.ones(n,dtype=torch.bool),torch.randn(n,t,136),torch.randn(n,t,3),torch.ones((n,t),dtype=torch.bool)]
        old.eval();model.eval()
        with torch.no_grad():
            expected=old(*args);actual=model(*args,torch.randn(n,768),torch.randn(n,2))
        for a,b in zip(expected,actual):self.assertTrue(torch.equal(a,b))
        self.assertEqual(len(newopt.param_groups),2);self.assertTrue(all(p not in newopt.state for p in newopt.param_groups[1]['params']))
        snapshot=copy.deepcopy(model.state_dict());again=Encoder(10,dict(cfg,hybrid=__import__('dl_binner.hybrid.bank',fromlist=['policy']).policy()));again.load_state_dict(snapshot,strict=True)
        self.assertTrue(all(torch.equal(v,again.state_dict()[k]) for k,v in snapshot.items()))
        self.assertTrue(all(not p.requires_grad for p in target.parameters()));self.assertTrue(all(not p.requires_grad for p in anchor.parameters()))

class Sources(unittest.TestCase):
    def test_content_bound_workflow_and_new_no_truth_restore_selection(self):
        from e034_restore import needed
        self.assertTrue(needed('work/E009-GLM/embed/embeddings.json','bootstrap'))
        self.assertTrue(needed('work/oral-noGLM/graph/result/graph.json','bootstrap'))
        self.assertFalse(needed('work/E009-GLM/student/result/checkpoint.pt','bootstrap'))
        self.assertFalse(needed('evidence/truth.json','measurements'))
        source=(ROOT/'scripts/e034_control.py').read_text();self.assertIn("binding(p['snakefile'])['sha256']",source)
        self.assertNotIn('chain=',(ROOT/'experiments/E034-genome-graph/Snakefile').read_text())


class NativeProducer(unittest.TestCase):
    def fixture(self,folder):
        import time
        from e024_coverage import binding
        r=Path(folder);w=r/'dl_binner-0.1.0.dev10-py3-none-any.whl';w.write_bytes(b'engineering wheel');b=r/'source.bundle';b.write_bytes(b'source');now=time.time()
        i=dict(source='a'*40,repo='/srv/dl_binner/repo',phase='graph-test',root='/srv/dl_binner/experiments/e034/graph-test',user='research',service_name='e034-graph-test',setup_timer='e034-setup-test',archive_prefix='gs://dl-binner-archive-167650584170/e034/test/',vm_start_epoch=now)
        f=dict(coverage_status='PASS_FOR_SPECIFIED_ORDINARY_FIRST_PARTY_PRODUCTS_ONLY',real_money_authorized=False,checked_epoch=now,credit_checked_epoch=now,estimated_complete_gross_USD=13,ceiling_USD=15,credit_valid_until_epoch=1799712000,storage_valid_until_epoch=1794351600,wheel_path=str(w),wheel_binding=binding(w),native_pysam_path='/srv/retained/pysam.whl',pysam_binding=dict(bytes=1,sha256='0'*64),source_transport=dict(kind='private_exact_Git_bundle',path=str(b),bundle=binding(b),base='b'*40))
        return i,f
    def test_actual_schema_and_rendered_disk_source_release_programs(self):
        import ast
        from e034_launch import config_value,render_host,render_release,render_inventory,source_sync
        from e034_phase import validate_config
        from e034_arm import validate_config as arm
        with tempfile.TemporaryDirectory()as t:
            i,f=self.fixture(t);c=config_value(i,f,100,200);validate_config(c);arm(c)
            plan=json.loads((ROOT/'experiments/E034-genome-graph/runtime-plan.json').read_text().replace('NEW_PHASE',i['phase']))
            self.assertEqual(plan['python'],c['python']);self.assertEqual(plan['work'],c['task_filesystem']+'/science')
            for k in c:
                bad=dict(c);del bad[k]
                with self.assertRaises(ValueError):validate_config(bad)
            for disk in [None,dict(name='e034-task-123')]:
                code=render_host(i,f,disk);compile(code,'host','exec');tree=ast.parse(code)
                inner=next(n.value for n in ast.walk(tree)if isinstance(n,ast.Constant)and isinstance(n.value,str)and n.value.startswith('import os,pathlib,subprocess,json,pwd'))
                for a,b in [('@@TASK@@',repr(i['root']+'/task')),('@@NAME@@',repr('e034-task-123')),('@@USER@@',repr('research'))]:inner=inner.replace(a,b)
                compile(inner,'exact new-empty-disk program','exec');self.assertIn('100*1024**3',inner);self.assertIn('blkid',inner)
            for code in [render_release(i,{}),render_inventory(i),source_sync(i,f['source_transport'])]:compile(code,'actual program','exec')
            self.assertIn('watchdog_verified=True',render_release(i,{}));self.assertIn('refs/heads/genome-graph-representation',source_sync(i,f['source_transport']))

class StreamAndCollection(unittest.TestCase):
    def test_actual_restore_reader_with_selected_alias_and_corruption_refusal(self):
        import base64,hashlib
        import e032_restore as r
        from e034_restore import needed
        for corrupt in [False,True]:
            value=b'closed tiny cache';b=dict(bytes=len(value),sha256=hashlib.sha256(value).hexdigest());name='work/E009-noGLM/embed/embeddings.npz';alias='work/E009-GLM/embed/embeddings.npz'
            inv=dict(members={name:b},all_work_members={name[5:]:b,alias[5:]:b},aliases={alias:dict(b,canonical=name)},omitted_retained_on_disk={})
            raw=io.BytesIO()
            with tarfile.open(fileobj=raw,mode='w:gz')as tar:
                for n,v in [('inventory.json',json.dumps(inv).encode()),(name,value+(b'x'if corrupt else b''))]:
                    h=tarfile.TarInfo(n);h.size=len(v);tar.addfile(h,io.BytesIO(v))
            payload=raw.getvalue();meta=dict(size=len(payload),generation='123',md5_hash=base64.b64encode(hashlib.md5(payload).digest()).decode());expected=dict(bytes=len(payload),sha256=hashlib.sha256(payload).hexdigest())
            old=r.needed;r.needed=lambda n:needed(n,'bootstrap')
            try:
                with tempfile.TemporaryDirectory()as t:
                    out=Path(t)/'restored'
                    if corrupt:
                        with self.assertRaisesRegex(ValueError,'member differs'):r.stream_restore(io.BytesIO(payload),meta,expected,out,reserve=0)
                        self.assertFalse((out/'work/restore-admission.json').exists())
                    else:
                        proof=r.stream_restore(io.BytesIO(payload),meta,expected,out,reserve=0);self.assertTrue(proof['every_member_verified']);self.assertEqual((out/name).stat().st_ino,(out/alias).stat().st_ino)
            finally:r.needed=old
    def test_actual_two_GiB_collection_cap_and_complete_verifier(self):
        from e034_collect import pack
        from e033_collect import verify
        with tempfile.TemporaryDirectory()as t:
            root=Path(t);w=root/'w';e=root/'e';w.mkdir();e.mkdir();(w/'one').write_bytes(b'exact duplicate');(w/'two').write_bytes(b'exact duplicate')
            proof=pack(w,e,root/'return');self.assertEqual(len(proof['aliases']),1)
            self.assertEqual(json.loads((root/'return/inventory.json').read_text())['compressed_hard_ceiling_bytes'],2*1024**3)
            self.assertTrue(verify(root/'return/e033-evidence.tar.gz',proof['archive'])['every_member_verified'])

if __name__=='__main__':unittest.main()
