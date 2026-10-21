"""Execute the real v002 native() against explicit synthetic Unreal API doubles.
No UE process or actual Content writes; each success/failure fixture is retained.
"""
from pathlib import Path
from datetime import datetime, timezone
import importlib.util
import json
import sys
import types
import unittest
from unittest.mock import patch
import air48_import_contract_v001 as C

HERE = Path(__file__).resolve().parent
RUN = HERE / 'validation-runs' / ('m' + datetime.now(timezone.utc).strftime('%H%M%S%f'))
spec = importlib.util.spec_from_file_location('air48_v002_actual_native_source', HERE / 'ue-import-hero-Air48-v001.py')
U = importlib.util.module_from_spec(spec); spec.loader.exec_module(U)


class FakeTexture:
    def __init__(self, env, obj, source, sword=False):
        self.env, self.obj, self.source, self.sword = env, obj, source, sword
        self.ready, self.settings_changed = False, False
        self.settings = {}

    def get_path_name(self): return self.obj
    def get_class(self): return types.SimpleNamespace(get_name=lambda: 'Texture2D')
    def size(self):
        if not self.ready: return 32
        if self.sword and self.env.failure == 'old_dimensions': return 256
        if not self.sword and not self.settings_changed and self.env.failure == 'new_dimensions': return 256
        if not self.sword and self.settings_changed and self.env.failure == 'after_settings_dimensions': return 256
        return 512
    def blueprint_get_size_x(self): return self.size()
    def blueprint_get_size_y(self): return self.size()
    def get_editor_property(self, key):
        if key == 'asset_import_data': return types.SimpleNamespace(extract_filenames=lambda: [self.source])
        return self.settings[key]
    def set_editor_property(self, key, value):
        self.env.events.append(('setting', self.obj, key))
        self.settings[key] = value
        self.ready = False; self.settings_changed = True


class FakeTask:
    def __init__(self): self.props = {}
    def set_editor_property(self, key, value): self.props[key] = value
    def get_editor_property(self, key): return self.props[key]


class FakeEnvironment:
    def __init__(self, root, manifest, failure):
        self.root, self.manifest, self.failure = root, manifest, failure
        self.events, self.textures, self.saved, self.import_calls = [], {}, [], 0
        sword = FakeTexture(self, U.SWORD_OBJECT, 'HOST_SYNTHETIC_OLD_SWORD', True)
        self.textures[U.SWORD_OBJECT] = sword
        self.unreal = types.SimpleNamespace(
            Texture2D=FakeTexture, AssetImportTask=FakeTask,
            Paths=types.SimpleNamespace(project_dir=lambda: str(root / 'UnrealGame')),
            SystemLibrary=types.SimpleNamespace(execute_console_command=self.finish),
            EditorAssetLibrary=types.SimpleNamespace(list_assets=self.list_assets,
                does_asset_exist=lambda package: package in self.textures, save_loaded_asset=self.save),
            AssetToolsHelpers=types.SimpleNamespace(get_asset_tools=lambda: types.SimpleNamespace(import_asset_tasks=self.import_tasks)),
            TextureCompressionSettings=types.SimpleNamespace(TC_EDITOR_ICON='<TextureCompressionSettings.TC_EDITOR_ICON: 7>'),
            TextureMipGenSettings=types.SimpleNamespace(TMGS_NO_MIPMAPS='<TextureMipGenSettings.TMGS_NO_MIPMAPS: 13>'),
            TextureGroup=types.SimpleNamespace(TEXTUREGROUP_UI='<TextureGroup.TEXTUREGROUP_UI: 16>'),
            TextureFilter=types.SimpleNamespace(TF_BILINEAR='<TextureFilter.TF_BILINEAR: 1>'),
            load_asset=lambda path: self.textures[path], log=lambda text: self.events.append(('log', text)))

    def finish(self, world, command):
        assert world is None and command == 'Editor.AsyncTextureCompilationFinishAll'
        self.events.append(('finish', command))
        if self.failure == 'finish_exception': raise RuntimeError('SYNTHETIC finish failure')
        for texture in self.textures.values(): texture.ready = True

    def list_assets(self, namespace, **kwargs):
        return [x['object_path'] for x in self.manifest['assets'] if x['package_path'] in self.textures]

    def import_tasks(self, tasks):
        self.import_calls += 1; self.events.append(('import', len(tasks)))
        assert len(tasks) == 48 and self.textures[U.SWORD_OBJECT].ready
        for row, task in zip(self.manifest['assets'], tasks):
            assert task.props['replace_existing'] is False and task.props['save'] is False
            task.props['imported_object_paths'] = [row['object_path']]
            texture = FakeTexture(self, row['object_path'], row['source']['path'])
            self.textures[row['package_path']] = texture

    def save(self, texture, only_if_dirty):
        assert only_if_dirty is False and texture.ready and texture.settings_changed and texture.size() == 512
        assert self.events[-1][0] == 'finish', 'Finish must follow setting changes and precede save'
        row = next(x for x in self.manifest['assets'] if x['object_path'] == texture.obj)
        p = Path(row['saved_path']); p.parent.mkdir(parents=True, exist_ok=True)
        with p.open('xb') as f: f.write(b'HOST_SYNTHETIC_ONLY_NOT_A_UE_PACKAGE')
        self.saved.append(texture.obj); self.events.append(('save', texture.obj))
        return True


def fixture(case):
    root = RUN / case / 'F'; output = root / 'source-assets/production/M/run'
    output.mkdir(parents=True)
    rows = []
    for frame in range(6):
        for component in C.COMPONENTS:
            name, package, obj = C.identity(component, frame)
            source = root / 'source-assets/production/M/sources48' / (name + '.png')
            rows.append(dict(component=component, frame=frame, name=name, package_path=package,
                             object_path=obj, destination_path=C.NAMESPACE, source=dict(path=source.as_posix(), bytes=1, sha256='a' * 64),
                             source_RGBA_sha256='b' * 64, known_optional_empty=False,
                             saved_path=C.saved_path(package, root).as_posix()))
    m = dict(schema='Root-Air48-native-import-v001', namespace=C.NAMESPACE, replace_existing=False,
             expected_old_count=1371, expected_new_count=48, expected_final_count=1419,
             assets=rows, old_production_files=[], HOST_SYNTHETIC_ONLY=True)
    mp = output / 'manifest.json'; C.write_new(mp, m)
    return root, m, mp, output / 'native-receipt.json'


class CompilationBarrierTests(unittest.TestCase):
    def execute(self, name, failure=None):
        root, m, mp, rp = fixture(name); env = FakeEnvironment(root, m, failure)
        def native_metadata(manifest, receipt): C.validate_receipt_assets(manifest, receipt, root)
        with patch.dict(sys.modules, {'unreal': env.unreal}), patch.object(U, 'ROOT', root), \
             patch.object(U, 'verify_old', lambda *args: None), patch.object(U, 'exact_membership', lambda *args: None), \
             patch.object(U, 'validate_receipt_assets', native_metadata):
            if failure:
                with self.assertRaises((ValueError, RuntimeError)): U.native(mp, m, rp)
            else: U.native(mp, m, rp)
        r = C.read(rp)
        self.assertEqual(r['success'], not bool(failure))
        self.assertTrue(rp.exists() and rp.with_name(rp.stem + '-claim.json').exists())
        return env, r

    def test_01_actual_native_flow_finishes_before_dimensions_and_after_settings(self):
        env, r = self.execute('ok')
        barriers = r['texture_compilation_barriers']
        self.assertEqual(len(barriers), 97)
        self.assertEqual(barriers[0]['before_dimensions'], [32, 32])
        self.assertTrue(all(x['after_dimensions'] == [512, 512] and x['command_requested'] is True for x in barriers))
        self.assertEqual([x['stage'] for x in barriers[1:]], ['new_texture_before_dimension_gate', 'new_texture_after_settings_before_save'] * 48)
        self.assertEqual(len(env.saved), 48)
        self.assertEqual(env.events[0], ('finish', 'Editor.AsyncTextureCompilationFinishAll'))
        self.assertEqual(env.import_calls, 1)
        self.assertTrue(all(x['actual_dimensions'] == [512, 512] for x in r['assets']))

    def test_02_still_wrong_old_sword_dimensions_reject_before_tasks(self):
        env, r = self.execute('old_bad', 'old_dimensions')
        self.assertEqual(env.import_calls, 0); self.assertFalse(env.saved)
        self.assertEqual(r['texture_compilation_barriers'][0]['after_dimensions'], [256, 256])
        self.assertIn('existing_sword_before_dimension_gate', r['failure'])

    def test_03_still_wrong_new_dimensions_reject_before_saving(self):
        env, r = self.execute('new_bad', 'new_dimensions')
        self.assertEqual(env.import_calls, 1); self.assertFalse(env.saved)
        self.assertEqual(r['texture_compilation_barriers'][-1]['after_dimensions'], [256, 256])
        self.assertIn('new_texture_before_dimension_gate', r['failure'])

    def test_04_settings_recompile_wrong_dimensions_reject_before_saving(self):
        env, r = self.execute('settings_bad', 'after_settings_dimensions')
        self.assertEqual(env.import_calls, 1); self.assertFalse(env.saved)
        self.assertEqual(r['texture_compilation_barriers'][-1]['after_dimensions'], [256, 256])
        self.assertIn('new_texture_after_settings_before_save', r['failure'])

    def test_05_finish_exception_preserves_unacknowledged_diagnostic_and_failure(self):
        env, r = self.execute('command_bad', 'finish_exception')
        self.assertEqual(env.import_calls, 0); self.assertFalse(env.saved)
        self.assertIs(r['texture_compilation_barriers'][0]['command_requested'], False)
        self.assertIsNone(r['texture_compilation_barriers'][0]['after_dimensions'])
        self.assertIn('SYNTHETIC finish failure', r['failure'])

    def test_06_unchanged_contract_tools_bind_original_26case_pass(self):
        before = HERE.with_name('import-tooling-candidate-v001')
        for name in ('air48_import_contract_v001.py', 'prepare-Air48-Root-import-v001.py',
                     'import-hero-Air48-v001.ps1', 'test_air48_import_contract_v001.py'):
            self.assertEqual((HERE / name).read_bytes(), (before / name).read_bytes())
        r = C.read(before / 'validation-runs/t164512126431/host-contract-result.json')
        self.assertTrue(r['success'] and r['sources_unchanged_while_running']); self.assertEqual(r['tests_run'], 26)


if __name__ == '__main__':
    RUN.mkdir(parents=True, exist_ok=False)
    pins = [C.pin(HERE / n) for n in ('ue-import-hero-Air48-v001.py', 'test-Air48-compilation-barriers-v002.py', 'air48_import_contract_v001.py')]
    with (RUN / 'mock-compilation-barriers.log').open('x', encoding='utf-8') as stream:
        result = unittest.TextTestRunner(stream=stream, verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(CompilationBarrierTests))
    unchanged = all(C.pin(p['path']) == p for p in pins)
    report = dict(schema='Air48-v002-compilation-barrier-mock-host-v001', success=result.wasSuccessful() and unchanged,
                  tests_run=result.testsRun, failures=len(result.failures), errors=len(result.errors), skipped=len(result.skipped),
                  source_pins=pins, sources_unchanged_while_running=unchanged, log=C.pin(RUN / 'mock-compilation-barriers.log'),
                  real_importer_function_executed=True, synthetic_Unreal_API_only=True, UE_calls=0,
                  actual_Source_Content_writes=0, actual_imports=0, FinalAccepted=False)
    rp = C.write_new(RUN / 'mock-result.json', report)
    print(json.dumps(dict(result=rp, **report)))
    raise SystemExit(0 if report['success'] else 1)
