"""Small host fixtures only. These tests never stage the actual project or assert native success."""
import importlib.util
import json
import os
from pathlib import Path
import unittest
from unittest.mock import patch
from datetime import datetime

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('stable_copy_candidate', HERE / 'stage-stable-preview-v001.py')
M = importlib.util.module_from_spec(spec)
spec.loader.exec_module(M)
RUN_ID = datetime.now().strftime('%Y%m%d-%H%M%S-%f')
FIXTURES = HERE / ('_host-fixtures/session-' + RUN_ID)


class PhysicalCopyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        FIXTURES.mkdir(parents=True, exist_ok=False)

    def fixture(self):
        base = FIXTURES / self._testMethodName
        source = base / 'source'
        for directory in ('Config', 'Content', 'Binaries', 'Plugins'):
            (source / directory).mkdir(parents=True, exist_ok=True)
        for name, data in [('CodexDungeon.uproject', b'host fixture only'),
                           ('Content/t.bin', b'original pixels\x00\x01'), ('Config/c.ini', b'fixture=yes\n'),
                           ('Binaries/fake.dll', b'host only'), ('Plugins/Fake/fake.uplugin', b'host only')]:
            (source / name).parent.mkdir(parents=True, exist_ok=True)
            (source / name).write_bytes(data)
        rows = [M.pin(p, source) for p in sorted(source.rglob('*')) if p.is_file()]
        return source, base / 'copy', rows

    def test_physical_copy_independent_after_source_edit(self):
        source, target, rows = self.fixture()
        M.copy_snapshot(source, target, rows)
        self.assertFalse(os.path.samestat((source / 'Content/t.bin').stat(), (target / 'Content/t.bin').stat()))
        (source / 'Content/t.bin').write_bytes(b'later development')
        M.verify_rows(target, rows)
        with self.assertRaisesRegex(ValueError, 'bytes/SHA differ'):
            M.verify_rows(source, rows)

    def test_wrong_source_hash_keeps_partial_failure(self):
        source, target, rows = self.fixture()
        rows[0] = dict(rows[0], sha256='0' * 64)
        with self.assertRaisesRegex(ValueError, 'bytes/SHA differ'):
            M.copy_snapshot(source, target, rows)
        self.assertTrue(target.is_dir())
        self.assertFalse((target / rows[0]['path']).exists())

    def test_existing_destination_is_untouched(self):
        source, target, rows = self.fixture()
        target.mkdir()
        (target / 'keep.bin').write_bytes(b'never overwrite')
        with self.assertRaisesRegex(ValueError, 'already exists'):
            M.copy_snapshot(source, target, rows)
        self.assertEqual((target / 'keep.bin').read_bytes(), b'never overwrite')

    def test_target_tamper_and_extra_hidden_member_are_rejected(self):
        source, target, rows = self.fixture()
        M.copy_snapshot(source, target, rows)
        M.exact_runtime(target, rows)
        (target / 'Content/.hidden-extra.bin').write_bytes(b'extra')
        if os.name == 'nt':
            import ctypes
            self.assertTrue(ctypes.windll.kernel32.SetFileAttributesW(str(target / 'Content/.hidden-extra.bin'), 2))
        with self.assertRaisesRegex(ValueError, 'membership differs'):
            M.exact_runtime(target, rows)
        (target / 'Config/c.ini').write_bytes(b'changed')
        with self.assertRaisesRegex(ValueError, 'bytes/SHA differ'):
            M.verify_rows(target, rows)

    def test_hardlinked_source_and_escape_are_rejected(self):
        source, target, rows = self.fixture()
        os.link(source / 'Content/t.bin', source / 'Content/link.bin')
        with self.assertRaisesRegex(ValueError, 'single physical file'):
            M.copy_snapshot(source, target, rows)
        with self.assertRaisesRegex(ValueError, 'clean relative'):
            M.rel(target, '../escaped.bin')

    def test_source_change_during_copy_is_retained_and_rejected(self):
        source, target, rows = self.fixture()
        real_copy = M.copy_one
        first = [True]
        def changed_copy(src, dst, row):
            real_copy(src, dst, row)
            if first[0]:
                first[0] = False
                Path(src).write_bytes(b'changed during source readback')
        with patch.object(M, 'copy_one', side_effect=changed_copy):
            with self.assertRaisesRegex(ValueError, 'bytes/SHA differ'):
                M.copy_snapshot(source, target, rows)
        self.assertTrue(target.is_dir())
        self.assertEqual((target / rows[0]['path']).stat().st_size, rows[0]['bytes'])

    def test_false_Root_request_rejects_before_actual_stage(self):
        source, target, rows = self.fixture()
        inputs = source / 'fake-inputs.json'
        request = source / 'false-request.json'
        inputs.write_text('{}', encoding='utf-8')
        request.write_text(json.dumps(dict(schema='HeroAir6-Root-stable-stage-request-v001',
                                          RootApproved=False, is_template=True)), encoding='utf-8')
        existed = M.STAGE.exists()
        with self.assertRaisesRegex(ValueError, 'Root actual stage request required'):
            M.stage(inputs, request)
        self.assertEqual(M.STAGE.exists(), existed)


if __name__ == '__main__':
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(PhysicalCopyTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    report = dict(schema='stable-preview-small-host-tests-v001', run=result.testsRun,
                  failures=len(result.failures), errors=len(result.errors), success=result.wasSuccessful(),
                  fixtures=FIXTURES.as_posix(), fixture_authority='HOST_ONLY_NOT_NATIVE_OR_ROOT_APPROVAL',
                  actual_project_staged=False, UE_started=False, FinalAccepted=False)
    M.write_new(HERE / ('small-host-tests-result-' + RUN_ID + '.json'), report)
    raise SystemExit(0 if result.wasSuccessful() else 1)
