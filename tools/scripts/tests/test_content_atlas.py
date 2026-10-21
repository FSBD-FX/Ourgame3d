"""Real PNG/manifest fixtures for the scoped first-unit atlas contract.

Each negative case removes one observable guarantee. Images are tiny synthetic
test fixtures in TemporaryDirectory; no project artwork is changed or repaired.
"""
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from PIL import Image


SCRIPT = Path(__file__).resolve().parents[1] / 'validate-content-atlas.py'


def load_validator():
    spec = importlib.util.spec_from_file_location('content_atlas_validator', SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.validate_manifest


class ContentAtlasTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.validate = load_validator()
        self.license = self.root / 'LICENSE.txt'
        self.license.write_text('Synthetic test fixture authored for validator tests.\n', encoding='utf-8')
        self.image = self.root / 'part.png'
        self.write_image(self.image)
        digest = self.digest(self.image)
        self.manifest = {
            'schema_version': 1, 'profile': 'first-unit-v2',
            'status': 'production_candidate', 'placeholder': False,
            'units': ['WPN-SWD-001', 'ARM-LGT-001', 'ENM-STN-001'],
            'provenance': {'test_source': {
                'license': 'LicenseRef-TestFixture', 'origin': 'original',
                'source_path': 'part.png', 'source_sha256': digest,
                'license_evidence_path': 'LICENSE.txt', 'license_evidence_sha256': self.digest(self.license),
            }},
            'actors': [],
        }
        player_actions = {
            'idle': None, 'walk': None, 'jump': None, 'fall': None,
            'land': None, 'dodge': None, 'hurt': None, 'death': None,
            'primary_1': (0.17, 0.12, 0.31), 'primary_2': (0.15, 0.12, 0.27),
            'primary_3': (0.22, 0.12, 0.32), 'secondary': (0.20, 0.10, 0.38),
            'air_primary_1': (0.17, 0.12, 0.31),
        }
        stone_actions = {
            'dormant': None, 'wake': None, 'idle': None, 'walk': None,
            'charge': (0.90, 0.80, 1.60), 'shield_bash': (0.70, 0.12, 0.90),
            'recovery': None, 'hurt': None, 'death': None,
        }
        for role, definitions, layers in (
            ('player', player_actions, ['body_far', 'armor', 'weapon', 'body_near']),
            ('stone_knight', stone_actions, ['body', 'shield']),
        ):
            actor = {
                'role': role, 'canvas_px': [16, 16], 'ground_pivot_px': [8, 14],
                'required_layers': layers, 'actions': [],
                'facings': {
                    'right': {'source_facing': 'right', 'baked_mirror_count': 0, 'runtime_mirror_count': 0},
                    'left': {'source_facing': 'right', 'baked_mirror_count': 0, 'runtime_mirror_count': 1},
                },
            }
            if role == 'player':
                actor.update(weapon_id='WPN-SWD-001', armor_id='ARM-LGT-001',
                             weapon_compatible_armors=['ARM-LGT-001'], armor_compatible_weapons=['WPN-SWD-001'])
            else:
                actor['enemy_id'] = 'ENM-STN-001'
            for name, timing in definitions.items():
                duration = sum(timing) if timing else 1.0
                if timing:
                    ends = [timing[0], timing[0] + timing[1], duration]
                    phases = [{'id': phase, 'start_s': start, 'end_s': end}
                              for phase, start, end in zip(('windup', 'active', 'recovery'), (0.0, *ends[:2]), ends)]
                    times = [0.0, ends[0], ends[1]]
                else:
                    phases = [{'id': 'pose', 'start_s': 0.0, 'end_s': duration}]
                    times = [0.0, 0.3, 0.7]
                frames = []
                for index, time in enumerate(times):
                    frames.append({
                        'index': index, 'time_s': time,
                        'canvas_px': [16, 16], 'ground_pivot_px': [8, 14],
                        'markers_px': {'ground_root': [8, 14], 'hand_near': [10, 8],
                                       'grip_primary': [10, 8], 'weapon_tip': [14, 6],
                                       'shield_contact': [13, 8], 'emitter_primary': [14, 6]},
                        'layers': {layer: {'path': 'part.png', 'sha256': digest,
                                           'provenance_id': 'test_source', 'placeholder': False,
                                           'baked_mirror_count': 0, 'runtime_mirror_count': 0}
                                   for layer in layers},
                    })
                actor['actions'].append({'id': name, 'duration_s': duration,
                                         'geometry_kind': 'melee' if timing else 'none',
                                         'phases': phases, 'frame_count': 3, 'frames': frames})
            self.manifest['actors'].append(actor)

    @staticmethod
    def digest(path):
        return hashlib.sha256(path.read_bytes()).hexdigest()

    @staticmethod
    def write_image(path, mode='RGBA', size=(16, 16), opaque=False, empty=False):
        image = Image.new(mode, size, (0, 0, 0, 0) if mode == 'RGBA' else (0, 0, 0))
        if not empty:
            if opaque and mode == 'RGBA':
                image.paste((60, 80, 100, 255), (0, 0, *size))
            else:
                image.paste((60, 80, 100, 255) if mode == 'RGBA' else (60, 80, 100), (2, 2, 10, 12))
        image.save(path, format='PNG')

    def action(self, name='primary_1'):
        return next(action for action in self.manifest['actors'][0]['actions'] if action['id'] == name)

    def save_and_validate(self):
        path = self.root / 'manifest.json'
        path.write_text(json.dumps(self.manifest), encoding='utf-8')
        return self.validate(path, self.root)

    def assert_rejected(self, code):
        result = self.save_and_validate()
        self.assertFalse(result['passed'], result)
        self.assertIn(code, [item['code'] for item in result['errors']], result)

    def replace_frame_image(self, path):
        layer = self.action()['frames'][0]['layers']['weapon']
        layer.update(path=path.name, sha256=self.digest(path))

    def test_complete_real_png_contract_passes_without_runtime_claim(self):
        result = self.save_and_validate()
        self.assertTrue(result['passed'], result)
        self.assertIs(result['engine_executed'], False)
        self.assertEqual(result.get('runtime_status', 'not_evaluated'), 'not_evaluated')

    def test_missing_required_combo_action_rejected(self):
        self.manifest['actors'][0]['actions'].remove(self.action('primary_3'))
        self.assert_rejected('MISSING_ACTION')

    def test_air_primary_requires_its_own_layer_frame_binding(self):
        self.manifest['actors'][0]['actions'].remove(self.action('air_primary_1'))
        self.assert_rejected('MISSING_ACTION')

    def test_missing_required_frame_rejected(self):
        self.action()['frames'].pop()
        self.assert_rejected('FRAME_COUNT')

    def test_missing_real_file_rejected(self):
        self.action()['frames'][0]['layers']['weapon']['path'] = 'missing.png'
        self.assert_rejected('FILE_MISSING')

    def test_corrupt_png_with_matching_hash_rejected(self):
        path = self.root / 'corrupt.png'
        path.write_bytes(b'not a PNG despite the filename')
        self.replace_frame_image(path)
        self.assert_rejected('PNG_DECODE')

    def test_rgb_png_rejected(self):
        path = self.root / 'rgb.png'
        self.write_image(path, mode='RGB')
        self.replace_frame_image(path)
        self.assert_rejected('PNG_RGBA8')

    def test_fully_opaque_rgba_rejected(self):
        path = self.root / 'opaque.png'
        self.write_image(path, opaque=True)
        self.replace_frame_image(path)
        self.assert_rejected('PNG_ALPHA')

    def test_empty_transparent_rgba_rejected(self):
        path = self.root / 'empty.png'
        self.write_image(path, empty=True)
        self.replace_frame_image(path)
        self.assert_rejected('PNG_ALPHA')

    def test_actual_png_canvas_mismatch_rejected(self):
        path = self.root / 'wide.png'
        self.write_image(path, size=(20, 16))
        self.replace_frame_image(path)
        self.assert_rejected('CANVAS_MISMATCH')

    def test_frame_ground_pivot_drift_rejected(self):
        self.action()['frames'][1]['ground_pivot_px'] = [8, 13]
        self.assert_rejected('PIVOT_MISMATCH')

    def test_phase_relative_time_reset_rejected(self):
        self.action()['phases'][1]['start_s'] = 0.0
        self.assert_rejected('PHASE_TIMELINE')

    def test_source_combat_duration_mismatch_rejected(self):
        action = self.action()
        action['duration_s'] = 0.7
        action['phases'][-1]['end_s'] = 0.7
        self.assert_rejected('SOURCE_TIMING')

    def test_nonmonotonic_frame_time_rejected(self):
        self.action()['frames'][2]['time_s'] = 0.1
        self.assert_rejected('FRAME_TIME')

    def test_all_combat_frames_stuck_in_windup_rejected(self):
        for frame, time in zip(self.action()['frames'], (0.0, 0.02, 0.05)):
            frame['time_s'] = time
        self.assert_rejected('FRAME_PHASE_COVERAGE')

    def test_null_units_report_rejection_instead_of_crashing(self):
        self.manifest['units'] = None
        try:
            self.assert_rejected('UNITS')
        except TypeError:
            self.fail('Validator crashed instead of returning a structured UNITS rejection')

    def test_missing_grip_marker_rejected(self):
        del self.action()['frames'][0]['markers_px']['grip_primary']
        self.assert_rejected('MARKER_MISSING')

    def test_grip_detached_from_hand_rejected(self):
        self.action()['frames'][0]['markers_px']['grip_primary'] = [5, 8]
        self.assert_rejected('GRIP_ALIGNMENT')

    def test_emission_requires_emitter_marker(self):
        action = self.action()
        action['geometry_kind'] = 'emission'
        del action['frames'][0]['markers_px']['emitter_primary']
        self.assert_rejected('MARKER_MISSING')

    def test_unknown_geometry_kind_cannot_bypass_emitter_rule(self):
        self.action()['geometry_kind'] = 'emisson'
        self.assert_rejected('SCHEMA')

    def test_one_frame_missing_armor_layer_rejected(self):
        del self.action()['frames'][1]['layers']['armor']
        self.assert_rejected('LAYER_SET')

    def test_double_mirror_on_facing_rejected(self):
        self.manifest['actors'][0]['facings']['left']['baked_mirror_count'] = 1
        self.assert_rejected('MIRROR_CONTRACT')

    def test_extra_weapon_layer_mirror_rejected(self):
        self.action()['frames'][0]['layers']['weapon']['runtime_mirror_count'] = 1
        self.assert_rejected('MIRROR_CONTRACT')

    def test_missing_left_facing_rejected(self):
        del self.manifest['actors'][0]['facings']['left']
        self.assert_rejected('FACING_MISSING')

    def test_weapon_armor_incompatible_rejected(self):
        self.manifest['actors'][0]['armor_compatible_weapons'] = ['WPN-GSW-001']
        self.assert_rejected('EQUIPMENT_COMPATIBILITY')

    def test_png_hash_mismatch_rejected(self):
        self.action()['frames'][0]['layers']['weapon']['sha256'] = '0' * 64
        self.assert_rejected('HASH_MISMATCH')

    def test_missing_provenance_rejected(self):
        self.action()['frames'][0]['layers']['weapon']['provenance_id'] = 'missing'
        self.assert_rejected('PROVENANCE')

    def test_unknown_license_rejected(self):
        self.manifest['provenance']['test_source']['license'] = 'unknown'
        self.assert_rejected('LICENSE')

    def test_generated_source_requires_backend_and_prompt_provenance(self):
        self.manifest['provenance']['test_source']['origin'] = 'generated'
        self.assert_rejected('PROVENANCE_GENERATION')

    def test_license_evidence_hash_mismatch_rejected(self):
        self.license.write_text('changed evidence', encoding='utf-8')
        self.assert_rejected('HASH_MISMATCH')

    def test_placeholder_layer_cannot_pass_formal_gate(self):
        self.action()['frames'][0]['layers']['weapon']['placeholder'] = True
        self.assert_rejected('PLACEHOLDER')

    def test_known_prototype_directory_cannot_be_relabelled_formal(self):
        folder = self.root / 'source-assets/prototype/first-room-v1'
        folder.mkdir(parents=True)
        path = folder / 'part.png'
        path.write_bytes(self.image.read_bytes())
        self.action()['frames'][0]['layers']['weapon']['path'] = path.relative_to(self.root).as_posix()
        self.assert_rejected('PLACEHOLDER')

    def test_template_manifest_cannot_pass_formal_gate(self):
        self.manifest['status'] = 'template_unfulfilled'
        self.assert_rejected('STATUS')

    def test_source_path_cannot_escape_root(self):
        self.action()['frames'][0]['layers']['weapon']['path'] = '../outside.png'
        self.assert_rejected('PATH_OUTSIDE_ROOT')

    def test_validator_does_not_repair_or_rewrite_inputs(self):
        path = self.root / 'manifest.json'
        path.write_text(json.dumps(self.manifest), encoding='utf-8')
        before = {path.name: path.read_bytes() for path in self.root.iterdir() if path.is_file()}
        self.validate(path, self.root)
        self.assertEqual(set(before), {path.name for path in self.root.iterdir() if path.is_file()})
        for name, content in before.items():
            self.assertEqual((self.root / name).read_bytes(), content)


if __name__ == '__main__':
    unittest.main()
