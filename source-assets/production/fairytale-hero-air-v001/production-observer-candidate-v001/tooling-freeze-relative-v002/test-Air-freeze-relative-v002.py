"""Small actual immutable-closure tests; no UE or regenerated GPU fixtures."""
from pathlib import Path
from datetime import datetime, timezone
import ast
import hashlib
import json
import unittest
import air_production_contract_v001 as C

HERE=Path(__file__).resolve().parent
RUN=HERE/'validation-runs'/('r'+datetime.now(timezone.utc).strftime('%H%M%S%f'))
IC=C.import_contract()
OLD=HERE.with_name('tooling')
FULL=C.AIR/'production-candidate-v001/full-production-v001/HeroAir-full-production-candidate-freeze-v001.json'
FULL_SHA='7197705254448e380d643edbef4b31fe3adf4f95a7b3c9d389ad574adea532e6'


def fixture(name,edit):
    directory=RUN/name;directory.mkdir()
    source=directory/'item.bin';source.write_bytes(b'HOST_SYNTHETIC_ONLY')
    p=IC.pin(source);p['path']='item.bin';edit(p)
    fp=IC.write_new(directory/'freeze.json',dict(members=[p]))
    return fp


class FreezeRelativeTests(unittest.TestCase):
    def test_01_actual_full42_relative_members_twice(self):
        self.assertEqual(IC.pin(FULL)['sha256'],FULL_SHA)
        result=C.frozen(IC.pin(FULL),IC)
        self.assertEqual(len(result['members']),42)
        self.assertEqual(result['members'][0]['path'],'before-source/DungeonFairytaleSwordAirV001.cpp')

    def test_02_actual_absolute_parent_source14_twice(self):
        p=C.LEAF/'HeroAir-production-observer-source-freeze-v001.json'
        self.assertEqual(IC.pin(p)['sha256'],'e7b9f44fe53fa2c827d962b359494badf2efbf1ffb8d2e2face8dd2449fa6140')
        self.assertEqual(len(C.frozen(IC.pin(p),IC)['members']),14)

    def test_03_wrong_bytes_rejected(self):
        p=fixture('wrong-bytes',lambda r:r.update(bytes=r['bytes']+1))
        with self.assertRaises(ValueError):C.frozen(p,IC)

    def test_04_missing_bytes_rejected(self):
        p=fixture('missing-bytes',lambda r:r.pop('bytes'))
        with self.assertRaises(ValueError):C.frozen(p,IC)

    def test_05_missing_relative_file_rejected(self):
        p=fixture('missing-file',lambda r:r.update(path='not-existing.bin'))
        with self.assertRaises(FileNotFoundError):C.frozen(p,IC)

    def test_06_poison_relative_path_rejected(self):
        for i,path in enumerate(('../item.bin','item.bin:stream','a/./item.bin')):
            p=fixture('poison-'+str(i),lambda r:r.update(path=path))
            with self.assertRaises(ValueError):C.frozen(p,IC)

    def test_07_precise_frozen_base_delta_and_AST_equivalence_elsewhere(self):
        old=(OLD/'air_production_contract_v001.py').read_text(encoding='utf-8')
        new=(HERE/'air_production_contract_v001.py').read_text(encoding='utf-8')
        line='            c.check(row)\n'
        self.assertEqual(old.count(line),1)
        a,b=ast.parse(old),ast.parse(new)
        changed={'frozen','preflight','candidate_source_rows','candidate_source_matches'}
        old_nodes={n.name:ast.dump(n,include_attributes=False) for n in a.body if isinstance(n,(ast.FunctionDef,ast.ClassDef)) and n.name not in changed}
        new_nodes={n.name:ast.dump(n,include_attributes=False) for n in b.body if isinstance(n,(ast.FunctionDef,ast.ClassDef)) and n.name not in changed}
        self.assertEqual(old_nodes,new_nodes)
        old_frozen=next(n for n in a.body if isinstance(n,ast.FunctionDef) and n.name=='frozen')
        new_frozen=next(n for n in b.body if isinstance(n,ast.FunctionDef) and n.name=='frozen')
        self.assertEqual(ast.get_source_segment(new,new_frozen),ast.get_source_segment(old,old_frozen).replace('c.check(row)','c.check(row, root=p.parent)'))
        old_pre=ast.get_source_segment(old,next(n for n in a.body if isinstance(n,ast.FunctionDef) and n.name=='preflight'))
        new_pre=ast.get_source_segment(new,next(n for n in b.body if isinstance(n,ast.FunctionDef) and n.name=='preflight'))
        old_rows="        candidate_rows = source_freeze.get('source_files')\n        if not isinstance(candidate_rows, list):\n            candidate_rows = source_freeze.get('members', source_freeze.get('files', []))\n"
        old_match="            need(any(Path(x['path']).name == Path(r['path']).name and (x['bytes'], x['sha256']) == (r['bytes'], r['sha256'])\n                     for x in candidate_rows if isinstance(x, dict) and 'path' in x), 'Actual admitted Source bytes differ from frozen candidate')"
        new_match="            need(candidate_source_matches(source_freeze, r), 'Actual admitted Source bytes differ from frozen admitted-after candidate')"
        self.assertEqual(old_pre.count(old_rows),1);self.assertEqual(old_pre.count(old_match),1)
        self.assertEqual(new_pre,old_pre.replace(old_rows,'').replace(old_match,new_match))
        for name in ('verify-Air-production-native-v001.py','test-Air-production-host-v001.py','Root-Air6-prereg-TEMPLATE-v001.json'):
            self.assertEqual((HERE/name).read_bytes(),(OLD/name).read_bytes())
        r=IC.read(OLD/'validation-runs/h170133089542/host-tests-result.json')
        self.assertTrue(r['passed'] and r['sources_unchanged']);self.assertEqual(r['tests'],13)

    def test_08_retained_LEAF_root_and_original_v001_freeze(self):
        self.assertEqual(C.LEAF,HERE.parent)
        self.assertEqual(C.AIR,C.LEAF.parent)
        p=OLD/'Air-production-proof-checker-freeze-v001.json'
        self.assertEqual(IC.pin(p)['sha256'],'0883605a2d612fc979d3adb68e3df8191969d288e196db3dd2424efe061a34b6')
        for row in IC.read(p)['members']:IC.check(row)

    def test_09_actual_full7_after_candidates_and_Root_final6_plus_observer3(self):
        production=IC.read(FULL)
        observer=IC.read(C.LEAF/'HeroAir-production-observer-source-freeze-v001.json')
        rows=C.candidate_source_rows(production);self.assertEqual(len(rows),7)
        six=[r for r in rows if Path(r['path']).name!='DungeonHUD.cpp'];self.assertEqual(len(six),6)
        three=C.candidate_source_rows(observer);self.assertEqual(len(three),3)
        for freeze,after in ((production,six),(observer,three)):
            for row in after:
                compiled=dict(row,path='UnrealGame/Source/CodexDungeon/'+Path(row['path']).name)
                self.assertTrue(C.candidate_source_matches(freeze,compiled))

    def test_10_before_source_oldbytes_cannot_satisfy_after_admission(self):
        production=IC.read(FULL)
        old=[r for r in production['members'] if r['path'] in ('before-source/DungeonHUD.h','before-source/DungeonFighter.cpp')]
        self.assertEqual(len(old),2)
        for row in old:
            compiled=dict(row,path='UnrealGame/Source/CodexDungeon/'+Path(row['path']).name)
            self.assertFalse(C.candidate_source_matches(production,compiled))


if __name__=='__main__':
    RUN.mkdir(parents=True,exist_ok=False)
    pins=[IC.pin(HERE/'air_production_contract_v001.py'),IC.pin(__file__)]
    with (RUN/'relative-freeze-tests.log').open('x',encoding='utf-8') as stream:
        result=unittest.TextTestRunner(stream=stream,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(FreezeRelativeTests))
    unchanged=all(IC.pin(p['path'])==p for p in pins)
    proof=dict(schema='Air-freeze-relative-actual-host-v002',passed=result.wasSuccessful() and unchanged,
               tests=result.testsRun,failures=len(result.failures),errors=len(result.errors),sources_unchanged=unchanged,
               source_pins=pins,actual_full42_freeze=IC.pin(FULL),original_v001_13_PASS=IC.pin(OLD/'validation-runs/h170133089542/host-tests-result.json'),
               actual_absolute_source14_freeze=IC.pin(C.LEAF/'HeroAir-production-observer-source-freeze-v001.json'),
               changes='freeze-relative member base and admitted-after source filter only; other function AST and main checker bytes unchanged',
               regenerated_GPU_fixture_bytes=0,UE_calls=0,actual_Source_Content_writes=0,FinalAccepted=False)
    pp=IC.write_new(RUN/'relative-freeze-tests-result.json',proof)
    print(json.dumps(dict(result=pp,**proof)))
    raise SystemExit(0 if proof['passed'] else 1)
