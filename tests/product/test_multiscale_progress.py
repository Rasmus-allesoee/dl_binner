"""Exercise the real long-training progress branch, which tiny fits cannot reach."""
import ast
import contextlib
import inspect
import io
import json
from pathlib import Path
import random
import unittest
import numpy as np
import torch
from dl_binner.multiscale import model


class Progress(unittest.TestCase):
    def branch(self,at,teacher):
        """Execute the actual production conditional/logger without a scientific fit."""
        tree=ast.parse(inspect.getsource(model.train))
        nodes=[n for n in ast.walk(tree) if isinstance(n,ast.If) and any(
            isinstance(call,ast.Call) and call.args and isinstance(call.args[0],ast.Constant)
            and call.args[0].value=='multiscale_training_progress'
            for statement in n.body for call in ast.walk(statement))]
        self.assertEqual(len(nodes),1)
        context=dict(model.__dict__,at=at,teacher=teacher,epoch=0,updates=64,
                     seen=16384,indices=range(20000))
        log=io.StringIO()
        with contextlib.redirect_stdout(log):
            exec(compile(ast.Module(body=[nodes[0]],type_ignores=[]),'actual-progress-branch','exec'),context)
        return [json.loads(line) for line in log.getvalue().splitlines()]

    def test_first_real_64_update_boundary_both_roles_and_no_RNG_change(self):
        for teacher,role in [(None,'teacher'),(Path('/unused/teacher.pt'),'student')]:
            before=torch.get_rng_state().clone();py=random.getstate();npstate=np.random.get_state()
            rows=self.branch(63,teacher)
            self.assertEqual(len(rows),1)
            self.assertEqual(rows[0]['stage'],'multiscale_training_progress')
            self.assertEqual(rows[0]['role'],role)
            self.assertEqual(rows[0]['optimizer_updates'],64)
            self.assertEqual(rows[0]['parents_seen_this_epoch'],16384)
            self.assertTrue(torch.equal(before,torch.get_rng_state()))
            self.assertEqual(py,random.getstate())
            after=np.random.get_state();self.assertEqual(npstate[0],after[0]);np.testing.assert_array_equal(npstate[1],after[1]);self.assertEqual(npstate[2:],after[2:])

    def test_no_spurious_message_before_or_after_boundary(self):
        self.assertEqual(self.branch(62,None),[])
        self.assertEqual(self.branch(64,None),[])
        self.assertEqual(len(self.branch(127,None)),1)


if __name__=='__main__':unittest.main()
