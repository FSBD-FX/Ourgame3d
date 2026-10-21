"""Retain original 22 method bodies; append narrow relative-freeze boundary tests."""
from pathlib import Path
import ast
import hashlib
import importlib.util
import json
import sys
import unittest
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('bridge258_original22_child',HERE/'run-host-tests-v001.py')
OLD=importlib.util.module_from_spec(s);s.loader.exec_module(OLD);V=OLD.V
FIXTURES=HERE/'freeze-entry-fixtures'


def frozen(name):
    return V.freeze_members(V.pin(FIXTURES/(name+'.json')))


class RelativeFreezeBoundaries(unittest.TestCase):
    def test_23_actual_f6514_relative_dependencies(self):
        path=V.LOADED['binding_freeze'].parent.parent/'native-observation-review-fix-v002/candidate-freeze-v002.json'
        row=V.pin(path)
        self.assertEqual(row['sha256'],'f6514ba40fdafcc605d294e1d9d0568dbe4fcf5302ace7f0c9388db2272ecaac')
        data,members=V.freeze_members(row)
        self.assertEqual(len(members),57);self.assertEqual(len(data['dependencies']),4)
    def test_24_relative_dependency_positive(self):
        _,members=frozen('good');self.assertEqual(len(members),1)
    def test_25_wrong_relative_dependency_sha(self):
        with self.assertRaises(ValueError):frozen('wrong-sha')
    def test_26_missing_relative_dependency(self):
        with self.assertRaises(ValueError):frozen('missing')
    def test_27_escape_relative_dependency(self):
        with self.assertRaises(ValueError):frozen('escape')
    def test_28_absolute_in_relative_field(self):
        with self.assertRaises(ValueError):frozen('absolute')
    def test_29_dot_alias_relative_dependency(self):
        with self.assertRaises(ValueError):frozen('dot-alias')
    def test_30_double_slash_alias_dependency(self):
        with self.assertRaises(ValueError):frozen('duplicate-slash')
    def test_31_backslash_relative_dependency(self):
        with self.assertRaises(ValueError):frozen('backslash')
    def test_32_both_path_fields_rejected(self):
        with self.assertRaises(ValueError):frozen('both-keys')
    def test_33_external_C_absolute_dependency_retained(self):
        frozen('external-absolute')
    def test_34_original22_test_method_bodies_exact(self):
        def bodies(path):
            data=path.read_bytes();lines=data.splitlines(keepends=True)
            tree=ast.parse(data.decode('utf-8-sig'));cls=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='Boundaries')
            return {n.name:b''.join(lines[n.lineno-1:n.end_lineno]) for n in cls.body if isinstance(n,ast.FunctionDef) and n.name.startswith('test_')}
        original=bodies(HERE.parent/'run-host-tests-v001.py');current=bodies(HERE/'run-host-tests-v001.py')
        self.assertEqual(len(original),22);self.assertEqual(current,original)


if __name__=='__main__':
    suite=unittest.TestSuite([unittest.defaultTestLoader.loadTestsFromTestCase(OLD.Boundaries),
                             unittest.defaultTestLoader.loadTestsFromTestCase(RelativeFreezeBoundaries)])
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    raise SystemExit(0 if result.wasSuccessful() else 1)
