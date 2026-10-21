"""Small host-only regressions for the two independently reproduced v001 gaps."""
from pathlib import Path
from datetime import datetime, timezone
import copy, importlib.util, json, sys, unittest
sys.dont_write_bytecode = True
P = Path(__file__).resolve().parent
OLD = P.with_name('air-disk-restore-tooling-candidate-v001')
sys.path.insert(0, str(P))
import air_disk_contract_v001 as C
spec = importlib.util.spec_from_file_location('review_fix_checker', P/'verify-air-disk-restore-native-v001.py')
M = importlib.util.module_from_spec(spec)
spec.loader.exec_module(M)
OLD_FREEZE = OLD/'HeroAirDiskRestore-tooling-freeze-v001.json'

class Checks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dep = M.dependencies()
        cls.am = C.read(P.parent/'native-ready-candidate-v001/import-Air48-v001.json')
        cls.ap = C.read(P.parent/'native-ready-candidate-v001/Air-runtime-profile-data-v001.json')
        cls.wm = C.read(cls.dep[1]['walk_manifest'])
        cls.wp = C.read(cls.dep[1]['walk_profile'])
        origins = C.read(P.parent/'landing-priority-observer-candidate-v001/tooling-review-fix-v002/geometry-fixture-origins-v002.json')
        cls.origin = next(x for x in origins['members'] if x['kind']=='Air' and x['side']=='right')
        report = C.read(C.resolve_pin(cls.origin))
        cls.obs = next(copy.deepcopy(x) for x in report['observations'] if x['new_air_draw']['drawn'] and x['new_air_draw']['slot_count']==9 and x['physical_visual_key']==2 and x['new_air_draw']['armor_kind']==1)
        cls.obs['has_player'] = True
        cls.empty = P/'regression-fixtures-v002'/'intentional-empty-runtime-mix.wav'
        cls.empty.parent.mkdir(exist_ok=True)
        if not cls.empty.exists():
            with cls.empty.open('xb'): pass
        cls.empty_pin = C.pin(cls.empty)

    def inspect(self, o):
        r = dict(role='target', observations=[o])
        return M.inspect_draws(r,self.dep,self.am,self.ap,self.wm,self.wp)

    def test_actual_full_605_member_executable_freeze_with_six_empty_fixtures(self):
        frozen = M.freeze(C.pin(OLD_FREEZE))
        self.assertEqual(len(frozen['members']),605)
        self.assertEqual(sum(x['bytes']==0 for x in frozen['members']),6)
        self.assertTrue(any(Path(x['path']).name=='verify-air-disk-restore-native-v001.py' for x in frozen['members']))

    def test_empty_actual_evidence_stays_rejected(self):
        self.assertEqual(self.empty_pin['bytes'],0)
        with self.assertRaisesRegex(ValueError,'Complete bytes/SHA pin required'):
            C.resolve_pin(self.empty_pin)
        with self.assertRaisesRegex(ValueError,'Complete bytes/SHA pin required'):
            C.confined_pin(self.empty_pin,self.empty.parent)

    def test_freeze_member_size_and_SHA_stay_exact(self):
        self.assertEqual(M.frozen_member(self.empty_pin),self.empty.resolve())
        for changes in (dict(bytes=-1),dict(bytes=True),dict(sha256='0'*64),dict(bytes=1)):
            with self.assertRaises(ValueError):M.frozen_member(dict(self.empty_pin,**changes))

    def test_current_Air_draw_matches_same_completed_callback(self):
        o = copy.deepcopy(self.obs)
        self.assertEqual(o['old_draw']['draw_id'],o['new_air_draw']['draw_id'])
        counts,slots = self.inspect(o)
        self.assertEqual(counts['Air9'],1)
        self.assertEqual(len(slots[0]),9)

    def test_only_Air_draw_id_zero_cannot_replay_prior_trace(self):
        o = copy.deepcopy(self.obs)
        o['new_air_draw']['draw_id'] = '0'
        with self.assertRaises(ValueError):self.inspect(o)

    def test_only_Air_draw_id_positive_stale_cannot_replay_prior_trace(self):
        o = copy.deepcopy(self.obs)
        old = int(o['old_draw']['draw_id'])
        o['new_air_draw']['draw_id'] = str(old+1)
        with self.assertRaises(ValueError):self.inspect(o)

    def test_missing_Air_draw_id_rejected(self):
        o = copy.deepcopy(self.obs)
        del o['new_air_draw']['draw_id']
        with self.assertRaises(ValueError):self.inspect(o)

if __name__=='__main__':
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromModule(sys.modules[__name__]))
    report=dict(schema='v144-review-fix-host-tests-v002',created_utc=datetime.now(timezone.utc).isoformat(),run=result.testsRun,failures=len(result.failures),errors=len(result.errors),passed=result.wasSuccessful(),old_full_freeze_pin=C.pin(OLD_FREEZE),checker_pin=C.pin(P/'verify-air-disk-restore-native-v001.py'),contract_pin=C.pin(P/'air_disk_contract_v001.py'),tests_pin=C.pin(Path(__file__)),historical_geometry_origin=Checks.origin,authority='HOST_DATA_ONLY_NOT_NATIVE_OR_APPROVAL',UE_started=False,actual_preflight_run=False,new_native_run=False,RootApproved=False,FinalAccepted=False)
    out=P/('review-fix-host-'+datetime.now().strftime('%Y%m%d-%H%M%S-%f')+'.json')
    with out.open('x',encoding='utf-8') as f:json.dump(report,f,indent=2);f.write('\n')
    raise SystemExit(0 if result.wasSuccessful() else 1)
