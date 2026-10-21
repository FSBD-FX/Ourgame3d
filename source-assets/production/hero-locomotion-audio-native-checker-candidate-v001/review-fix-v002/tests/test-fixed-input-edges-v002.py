"""Actual historical edge positive plus tiny hostile schema edits; no native run."""
from pathlib import Path
import copy
import hashlib
import importlib.util
import json
import unittest

HERE=Path(__file__).resolve().parent.parent
spec=importlib.util.spec_from_file_location('review_fix_checker',HERE/'verify-hero-locomotion-audio-native-v001.py')
V=importlib.util.module_from_spec(spec);spec.loader.exec_module(V)
FIXTURE=json.loads((HERE/'actual-historical-input-fixture-pin-v002.json').read_text(encoding='utf-8-sig'))
P=Path(FIXTURE['path']);assert P.stat().st_size==FIXTURE['bytes'] and hashlib.sha256(P.read_bytes()).hexdigest()==FIXTURE['sha256']
ACTUAL=json.loads(P.read_text(encoding='utf-8-sig'))['normal_inputs']
EXPECTED=[('Enter',True),('Enter',False),('D',True),('D',False),('D',True),('D',False),
          ('E',True),('E',False),('SpaceBar',True),('SpaceBar',False),('LeftShift',True),('LeftShift',False)]

def check(rows):
    # Before the fix there is no fixed-input gate: accepting without inspection
    # is precisely the review's reproduced behavior, not a mocked native PASS.
    if hasattr(V,'verify_fixed_normal_inputs'):
        return V.verify_fixed_normal_inputs(dict(normal_inputs=rows))

class FixedInputEdges(unittest.TestCase):
    def reject(self,edit):
        rows=copy.deepcopy(ACTUAL);edit(rows)
        with self.assertRaisesRegex(ValueError,'Exact fixed Shift_right normal-input edges required'):check(rows)
    def test_actual_historical_12_edges(self):
        self.assertEqual([(x['key'],x['down']) for x in ACTUAL],EXPECTED)
        if hasattr(V,'verify_fixed_normal_inputs'):self.assertTrue(check(ACTUAL)['passed'])
    def test_extra_f1(self):self.reject(lambda a:a.extend([dict(key='F1',down=True),dict(key='F1',down=False)]))
    def test_reenter(self):self.reject(lambda a:a.extend([dict(key='Enter',down=True),dict(key='Enter',down=False)]))
    def test_duplicate_edge(self):self.reject(lambda a:a.insert(3,copy.deepcopy(a[2])))
    def test_missing_release(self):self.reject(lambda a:a.pop(11))
    def test_reordered_edges(self):self.reject(lambda a:a.__setitem__(slice(2,4),list(reversed(a[2:4]))))
    def test_reversed_edge(self):self.reject(lambda a:a[3].update(down=True))
    def test_numeric_bool_is_not_bool(self):self.reject(lambda a:a[0].update(down=1))
    def test_gate_is_in_native_session_function(self):
        import ast
        tree=ast.parse((HERE/'verify-hero-locomotion-audio-native-v001.py').read_text(encoding='utf-8-sig'))
        session=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='verify_session')
        self.assertTrue(any(isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='verify_fixed_normal_inputs' for n in ast.walk(session)))

if __name__=='__main__':unittest.main(verbosity=2)
