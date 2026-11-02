"""Exercise E031's real Git consumer and refusal paths without cloud mutations.

The filesystem mount/provider identities are mocked. Tiny Git repositories and
the exact rendered private source consumer are real. No original disk is touched.
"""
import base64
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT=Path(__file__).absolute().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import e031_launch as launch
from e024_coverage import binding


class Launch(unittest.TestCase):
    def test_actual_private_bundle_import_checks_bytes_prerequisites_head_and_clean_checkout(self):
        with tempfile.TemporaryDirectory() as folder:
            p=Path(folder);source=p/'source';receiver=p/'receiver/repo';source.mkdir();receiver.parent.mkdir()
            def git(path,*args):
                return subprocess.check_output(['git',*args],cwd=path,text=True,stderr=subprocess.PIPE).strip()
            git(source,'init','-b','main');git(source,'config','user.name','Engineering fixture');git(source,'config','user.email','fixture@example.invalid')
            (source/'old').write_text('accepted source');git(source,'add','old');git(source,'commit','-m','test: own base')
            base=git(source,'rev-parse','HEAD');git(p,'clone',str(source),str(receiver))
            git(source,'checkout','-b',launch.BRANCH);(source/'new').write_text('new operational adapter')
            git(source,'add','new');git(source,'commit','-m','test: own new source');head=git(source,'rev-parse','HEAD')
            packet=p/'source.bundle';git(source,'bundle','create',str(packet),'refs/heads/'+launch.BRANCH,'^'+base)
            transport=dict(kind='private_exact_Git_bundle',path=str(packet),bundle=binding(packet),base=base,source=head)
            ident=dict(repo=str(receiver),source=head)
            code=launch.source_code(ident,transport);compile(code,'actual-source-consumer','exec')
            with patch('os.path.ismount',return_value=True),patch('os.cpu_count',return_value=8):exec(code,{})
            self.assertEqual(git(receiver,'rev-parse','HEAD'),head)
            self.assertEqual(git(receiver,'status','--porcelain'),'')
            self.assertEqual((receiver/'new').read_text(),'new operational adapter')
            packet.write_bytes(packet.read_bytes()+b'corrupt')
            with self.assertRaisesRegex(ValueError,'transport differs'):launch.source_code(ident,transport)

    def test_actual_scratch_consumer_refuses_nonempty_or_wrong_size_before_formatting(self):
        for size,signature in [(40*1024**3,'existing-signature'),(300*1024**3,'')]:
            with self.subTest(size=size,signature=signature),tempfile.TemporaryDirectory() as folder:
                ident=dict(root=str(Path(folder)/'new-mount'),scratch=dict(name='e031-bridge-scratch-fixture'))
                calls=[]
                def run(argv,**kwargs):
                    calls.append(argv)
                    class Result:returncode=1
                    return Result()
                def output(argv,**kwargs):
                    if argv[0]=='lsblk':return 'disk '+str(size)
                    if 'wipefs' in argv:return signature
                    raise AssertionError(argv)
                with patch.object(Path,'exists',return_value=True),patch.object(subprocess,'run',side_effect=run),patch.object(subprocess,'check_output',side_effect=output):
                    with self.assertRaisesRegex(ValueError,'not empty|type/size'):exec(launch.scratch_mount_code(ident),{})
                self.assertFalse(any('mkfs.ext4' in argv for argv in calls))

    def test_all_actual_remote_consumers_compile_and_no_original_format_route(self):
        with tempfile.TemporaryDirectory() as folder:
            p=Path(folder);wheel=p/'wheel';wheel.write_bytes(b'fixture-wheel')
            ident=dict(root='/srv/dl_binner/experiments/e031/bridge-fixture',repo='/srv/dl_binner/repo',scratch=dict(name='e031-bridge-scratch-fixture'))
            financial=dict(wheel_path=str(wheel),wheel_binding=binding(wheel))
            for code in [launch.inventory_code(ident),launch.host_code(ident,financial),launch.scratch_mount_code(ident),launch.release_code(ident,{})]:
                compile(code,'rendered-native-consumer','exec')
            mount=launch.scratch_mount_code(ident)
            self.assertIn("if signatures:raise ValueError",mount)
            self.assertIn("str(40*1024**3)",mount)
            self.assertNotIn('dl-binner-work',mount)
            self.assertNotIn('f76283ed',mount)
            self.assertIn('filesystem_device',launch.host_code(ident,financial))
            self.assertIn('allocation_start_epoch',Path(launch.__file__).read_text())


if __name__=='__main__':unittest.main()
