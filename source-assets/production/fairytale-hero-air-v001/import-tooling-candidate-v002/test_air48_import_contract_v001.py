"""Host-only executable contract cases; synthetic fixtures are not UE evidence.

All fixtures/logs remain in a NEW validation-runs directory. Tests never access
actual Content, start UE, create Root approval, or delete prior failure output.
"""
from pathlib import Path
from datetime import datetime, timezone
import copy
import hashlib
import importlib.util
import io
import json
import unittest
from unittest.mock import patch
import zipfile
from PIL import Image
import air48_import_contract_v001 as C

HERE = Path(__file__).resolve().parent
RUN = HERE / 'validation-runs' / ('t' + datetime.now(timezone.utc).strftime('%H%M%S%f'))


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    return C.write_new(path, value)


def fixture(root, e_root):
    candidate = root / 'source-assets/production/H/n'
    archive = root / '过程图稿与视频/HOST_SYNTHETIC_ONLY'
    edir = e_root / 'HOST_SYNTHETIC_ONLY'
    candidate.mkdir(parents=True)
    edir.mkdir(parents=True)
    assets, e_rows = [], []
    for f in range(6):
        for ci, component in enumerate(C.LAYER_ORDER):
            name, package, obj = C.identity(component, f)
            source = candidate / 'sources48' / (name + '.png')
            source.parent.mkdir(exist_ok=True)
            im = Image.new('RGBA', (512, 512), (ci + 1, f + 1, 90, 255))
            im.save(source, format='PNG')
            source_pin = C.pin(source)
            facts = dict(source_RGBA_sha256=hashlib.sha256(im.tobytes()).hexdigest(), source_mode='RGBA',
                         source_canvas=[512, 512], source_alpha_nonzero_pixels=262144,
                         source_alpha128_pixels=262144, source_alpha255_pixels=262144,
                         source_alpha_bbox=[0, 0, 512, 512])
            folder = 'body-layers' if component in C.BODY_COMPONENTS else 'armor-layers'
            member = f'原件/SYNTHETIC/{folder}/{component}/frame-{f}.png'
            original = archive / Path(member)
            original.parent.mkdir(parents=True, exist_ok=True)
            original.write_bytes(source.read_bytes())
            e_rows.append(dict(source=original.as_posix(), member=member, bytes=source_pin['bytes'], sha256=source_pin['sha256']))
            assets.append(dict(component=component, frame=f, name=name, package_path=package, object_path=obj,
                               source=source.as_posix(), source_filename=source.name, source_bytes=source_pin['bytes'],
                               source_sha256=source_pin['sha256'], known_optional_empty=False, empty_reason=None,
                               expected_object_class='Texture2D', **facts))
    sword_path = candidate / 'existing-sword-source49/military-sword-clean-v001.png'
    sword_path.parent.mkdir()
    im = Image.new('RGBA', (512, 512), (250, 90, 0, 255))
    im.save(sword_path)
    sword = dict(source=C.pin(sword_path), object_path=C.SWORD_OBJECT, import_new=False, reuses_existing_object=True,
                 source_RGBA_sha256=hashlib.sha256(im.tobytes()).hexdigest(), source_mode='RGBA', source_canvas=[512, 512],
                 source_alpha_nonzero_pixels=262144, source_alpha128_pixels=262144, source_alpha255_pixels=262144,
                 source_alpha_bbox=[0, 0, 512, 512])
    member = '原件/SYNTHETIC/source-copied/military-sword-clean-v001.png'
    original = archive / Path(member)
    original.parent.mkdir(parents=True)
    original.write_bytes(sword_path.read_bytes())
    e_rows.append(dict(source=original.as_posix(), member=member, bytes=sword['source']['bytes'], sha256=sword['source']['sha256']))
    packet = edir / '原件与展示副本-逐字节无损.zip'
    with zipfile.ZipFile(packet, 'x', compression=zipfile.ZIP_DEFLATED, compresslevel=1) as z:
        for row in e_rows:
            z.write(row['source'], row['member'])
    ei = dict(schema='native-media-exact-original-zip-retention-v001', retainer_version='v002', compression_level=1,
              packet=C.pin(packet), source_archive=archive.as_posix(), files=e_rows, file_count=len(e_rows),
              source_bytes=sum(v['bytes'] for v in e_rows), verification_passes=2,
              source_and_member_hash_mismatches=0, source_deleted=False, reencoded_originals=False)
    ei_pin = write(edir / 'E-retention-index-v001.json', ei)
    for row, erow in zip([*assets, sword], e_rows):
        row['retention'] = dict(E_index=ei_pin, E_packet=C.pin(packet), E_member=erow['member'],
                                E_member_bytes=erow['bytes'], E_member_sha256=erow['sha256'],
                                current_twoSHA_byte_equal=True, individual_E_PNG_path=None)
    descriptor = dict(schema='Air49-exact-source-typed-profile-closure-v001', namespace=C.NAMESPACE,
                      ProfileId='HOST_SYNTHETIC_ONLY', assets48=assets, existing_sword49=sword)
    closure_path = candidate / 'closure.json'
    closure_path.write_bytes(C.canonical_bytes(descriptor))
    prepared = dict(schema='frozen-Air48-scoped-native-import-prepared-v001', namespace=C.NAMESPACE,
                    profile_id='HOST_SYNTHETIC_ONLY', asset_count=48, assets=assets, existing_sword=sword,
                    unique_mandatory_texture_total=49, source_closure=C.pin(closure_path),
                    source_closure_descriptor=C.pin(closure_path), source_closure_digest=C.pin(closure_path)['sha256'],
                    native_imported=False, GPU_ready=False, FinalAccepted=False)
    manifest_pin = write(candidate / 'manifest.json', prepared)
    members = [C.pin(p) for p in sorted(candidate.rglob('*')) if p.is_file()]
    freeze_pin = write(candidate / 'freeze.json', dict(schema='Air48-native-ready-freeze-v001', members=members,
                                                      member_count=len(members), two_SHA_verification_passes=2,
                                                      mismatches=0, native_imports=0, FinalAccepted=False,
                                                      source_closure_digest=prepared['source_closure_digest']))
    imported_assets = []
    for row in assets:
        imported_assets.append(dict(component=row['component'], frame=row['frame'], name=row['name'],
                                    package_path=row['package_path'], object_path=row['object_path'],
                                    destination_path=C.NAMESPACE, source=dict(path=row['source'], bytes=row['source_bytes'], sha256=row['source_sha256']),
                                    source_RGBA_sha256=row['source_RGBA_sha256'], known_optional_empty=False,
                                    saved_path=C.saved_path(row['package_path'], root).as_posix(), retention=row['retention']))
    old = []
    for i in range(C.OLD_COUNT):
        rel = f'UnrealGame/Content/Production/SYNTHETIC/Old{i:04d}.uasset'
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(f'HOST_SYNTHETIC_NOT_UE_{i}'.encode())
        v = C.pin(path)
        old.append(dict(path=rel, bytes=v['bytes'], sha256=v['sha256']))
    snap = dict(source_files=292, production_files=1371, registered_tests=203, passed=200, failed=3, notRun=0,
                old200_all_green=True, three_unique_expected_TARGET_RED=True, files=old)
    snap_pin = write(root / 'source-assets/production/backups/HOST_SYNTHETIC_ONLY/compiled-source-manifest.json', snap)
    approval = dict(schema='Root-Air48-limited-source-import-approval-v001', RootApproved=True, limited_import_approved=True,
                    is_template=False, source_manifest=manifest_pin, candidate_freeze=freeze_pin,
                    source_closure_digest=prepared['source_closure_digest'], namespace=C.NAMESPACE,
                    expected_old_count=1371, expected_new_count=48, expected_final_count=1419,
                    TrialAllowed=False, FinalAccepted=False, HOST_SYNTHETIC_ONLY=True)
    output = root / 'source-assets/production/H/i'
    approval_pin = write(output / 'SYNTHETIC-approval-not-Root-authorization.json', approval)
    host = dict(schema='Air48-host-source-validation-v001', success=True, source_manifest=manifest_pin,
                candidate_freeze=freeze_pin, Root_source_approval=approval_pin,
                source_closure_digest=prepared['source_closure_digest'], source48_RGBA512_decoded=True,
                existing_sword_source_RGBA512_decoded=True, actual_E_ZIPmember_twoSHA_verified=True,
                UE_started=False, contract=C.pin(C.__file__), preparer=C.pin(HERE / 'prepare-Air48-Root-import-v001.py'),
                **{k: False for k in C.SCOPE_FALSE})
    host_pin = write(output / 'host.json', host)
    m = dict(schema='Root-Air48-native-import-v001', expected_old_count=1371, expected_new_count=48, expected_final_count=1419,
             namespace=C.NAMESPACE, replace_existing=False, assets=imported_assets, source_manifest=manifest_pin,
             candidate_freeze=freeze_pin, Root_source_approval=approval_pin, source_closure_digest=prepared['source_closure_digest'],
             host_source_validation=host_pin, old_compiled_snapshot=snap_pin, old_production_files=old,
             **{k: False for k in C.SCOPE_FALSE})
    import_pin = write(output / 'import-manifest.json', m)
    return dict(manifest=m, prepared=prepared, source_manifest=manifest_pin, freeze=freeze_pin,
                approval=approval, index=ei, snapshot=snap_pin, import_pin=import_pin)


def receipt_for(m):
    return dict(assets=[dict(component=x['component'], frame=x['frame'], source=copy.deepcopy(x['source']),
                            actual_object_path=x['object_path'], actual_class='Texture2D', actual_dimensions=[512, 512],
                            actual_import_filenames=[x['source']['path']],
                            actual_settings=dict(compression_settings='<TextureCompressionSettings.TC_EDITOR_ICON: 7>',
                                                 mip_gen_settings='<TextureMipGenSettings.TMGS_NO_MIPMAPS: 13>',
                                                 lod_group='<TextureGroup.TEXTUREGROUP_UI: 16>', never_stream=True, srgb=True,
                                                 filter='<TextureFilter.TF_BILINEAR: 1>'),
                            saved=dict(path=x['saved_path'], bytes=1, sha256='c' * 64)) for x in m['assets']])


class Air48ContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root, cls.e_root = RUN / 'F', RUN / 'E'
        cls.f = fixture(cls.root, cls.e_root)

    def test_01_valid_exact48_layout_and_native_receipt_contract(self):
        m = self.f['manifest']
        C.validate_layout(m, self.root)
        C.validate_receipt_assets(m, receipt_for(m), self.root)

    def test_02_full_source49_actual_png_zip_and_freeze_closure(self):
        prepared, assets = C.load_prepared(self.f['source_manifest'], self.f['freeze'], self.root, self.e_root)
        self.assertEqual(prepared, self.f['prepared'])
        self.assertEqual(assets, self.f['manifest']['assets'])

    def test_03_full_import_binding_host_decode_and_synthetic_baseline(self):
        with patch.object(C, 'BASELINE_SHA256', self.f['snapshot']['sha256']):
            self.assertEqual(C.load_import(self.f['import_pin']['path'], self.root, self.e_root), self.f['manifest'])
            C.verify_old(self.f['manifest']['old_production_files'], self.root)
            C.exact_membership(self.f['manifest'], False, self.root)

    def test_04_missing48_and_duplicate_phase_rejected(self):
        for fn in (lambda m: m['assets'].pop(), lambda m: m['assets'].__setitem__(47, copy.deepcopy(m['assets'][0]))):
            m = copy.deepcopy(self.f['manifest']); fn(m)
            with self.assertRaises(ValueError): C.validate_layout(m, self.root)

    def test_05_wrong_old_new_final_counts_rejected(self):
        for field, value in (('expected_old_count', 1332), ('expected_new_count', 32), ('expected_final_count', 1364)):
            m = copy.deepcopy(self.f['manifest']); m[field] = value
            with self.assertRaises(ValueError): C.validate_layout(m, self.root)

    def test_06_duplicate_source_and_saved_paths_rejected(self):
        for field in ('source', 'saved_path'):
            m = copy.deepcopy(self.f['manifest']); m['assets'][1][field] = copy.deepcopy(m['assets'][0][field])
            with self.assertRaises(ValueError): C.validate_layout(m, self.root)

    def test_07_outside_saved_package_and_source_substitution_rejected(self):
        for field, value in (('saved_path', str(self.root / 'UnrealGame/Content/Production/EXISTING.uasset')),
                             ('object_path', '/Game/Production/Other.Other')):
            m = copy.deepcopy(self.f['manifest']); m['assets'][0][field] = value
            with self.assertRaises(ValueError): C.validate_layout(m, self.root)
        m = copy.deepcopy(self.f['manifest']); m['assets'][0]['source']['path'] = str(self.root / 'other.png')
        with self.assertRaises(ValueError): C.validate_layout(m, self.root)

    def test_08_traversal_ads_unc_reserved_and_control_paths_rejected(self):
        for value in ('../outside', 'F:relative.png', 'F:/x.png:stream', '//server/share/x', 'x/CON.png',
                      'x/../y.png', 'x/./y.png', 'x/trailing./file', 'x/evil\n.png'):
            with self.subTest(value=value):
                with self.assertRaises(ValueError): C.resolve(value, self.root)

    def test_09_bool_frame_unknown_component_and_replacement_rejected(self):
        for field, value in (('frame', True), ('component', 'IndependentSword')):
            m = copy.deepcopy(self.f['manifest']); m['assets'][0][field] = value
            with self.assertRaises(ValueError): C.validate_layout(m, self.root)
        m = copy.deepcopy(self.f['manifest']); m['replace_existing'] = True
        with self.assertRaises(ValueError): C.validate_layout(m, self.root)

    def test_10_actual_decoded_rgba_hash_and_alpha_facts_rejected(self):
        row = copy.deepcopy(self.f['prepared']['assets'][0])
        row['source_RGBA_sha256'] = '0' * 64
        with self.assertRaises(ValueError): C.decode_png(row['source'], row)
        row = copy.deepcopy(self.f['prepared']['assets'][0]); row['source_alpha_nonzero_pixels'] -= 1
        with self.assertRaises(ValueError): C.decode_png(row['source'], row)

    def test_11_empty_and_non_rgba_png_rejected(self):
        for mode, color, name in (('RGBA', (0, 0, 0, 0), 'empty.png'), ('RGB', (1, 2, 3), 'rgb.png')):
            p = RUN / name; Image.new(mode, (512, 512), color).save(p)
            with self.assertRaises(ValueError): C.decode_png(p, self.f['prepared']['assets'][0])

    def test_12_forged_e_packet_pin_and_loose_png_claim_rejected(self):
        x = self.f['manifest']['assets'][0]
        for change in ('packet', 'loose', 'unchecked', 'member'):
            r = copy.deepcopy(x['retention'])
            if change == 'packet': r['E_packet']['sha256'] = '0' * 64
            elif change == 'loose': r['individual_E_PNG_path'] = 'E:/FAKE.png'
            elif change == 'unchecked': r['current_twoSHA_byte_equal'] = False
            else: r['E_member'] = '../fake.png'
            with self.subTest(change=change):
                with self.assertRaises(ValueError): C.verify_e_retention([(x['source'], r, '/body-layers/BodyRest/frame-0.png')], self.root, self.e_root)

    def test_13_valid_e_claim_does_not_hide_missing_actual_member(self):
        x = self.f['manifest']['assets'][0]; r = copy.deepcopy(x['retention'])
        r['E_member'] = '原件/FAKE/body-layers/BodyRest/frame-0.png'
        with self.assertRaises(ValueError): C.verify_e_retention([(x['source'], r, '/body-layers/BodyRest/frame-0.png')], self.root, self.e_root)

    def test_14_swapped_retained_component_member_rejected(self):
        x = self.f['manifest']['assets'][0]; r = copy.deepcopy(self.f['manifest']['assets'][1]['retention'])
        with self.assertRaises(ValueError): C.verify_e_retention([(x['source'], r, '/body-layers/BodyRest/frame-0.png')], self.root, self.e_root)

    def test_15_unlisted_freeze_member_rejected(self):
        # Use a NEW standalone candidate so original valid fixture is untouched.
        candidate = self.root / 'source-assets/production/H/bad-freeze'
        mp = write(candidate / 'manifest.json', {'synthetic': True})
        write(candidate / 'unlisted.json', {'preserve': True})
        fp = write(candidate / 'freeze.json', dict(schema='Air48-native-ready-freeze-v001', members=[mp], member_count=1,
                                                 two_SHA_verification_passes=2, mismatches=0, native_imports=0, FinalAccepted=False))
        with self.assertRaises(ValueError): C.verify_freeze(fp, Path(mp['path']), self.root)

    def test_16_wrong_baseline_pin_rejected_even_with_similar_counts(self):
        with self.assertRaises(ValueError): C.baseline(self.f['snapshot'], self.root)

    def test_17_explicit_approval_scope_and_pins_required(self):
        for field, value in (('RootApproved', False), ('is_template', True), ('TrialAllowed', True),
                             ('FinalAccepted', True), ('source_closure_digest', '0' * 64), ('expected_new_count', 32)):
            approval = copy.deepcopy(self.f['approval']); approval[field] = value
            with self.assertRaises(ValueError):
                C.validate_approval(approval, self.f['source_manifest'], self.f['freeze'], self.f['prepared']['source_closure_digest'], self.root)

    def test_18_receipt_missing_duplicate_and_wrong_class_dimensions_rejected(self):
        changes = (lambda r: r['assets'].pop(), lambda r: r['assets'].__setitem__(47, copy.deepcopy(r['assets'][0])),
                   lambda r: r['assets'][0].update(actual_class='Texture'),
                   lambda r: r['assets'][0].update(actual_dimensions=[256, 512]))
        for change in changes:
            r = receipt_for(self.f['manifest']); change(r)
            with self.assertRaises(ValueError): C.validate_receipt_assets(self.f['manifest'], r, self.root)

    def test_19_receipt_wrong_import_source_saved_path_and_settings_rejected(self):
        changes = (lambda r: r['assets'][0].update(actual_import_filenames=['F:/FAKE.png']),
                   lambda r: r['assets'][0]['saved'].update(path=str(self.root / 'OUTSIDE.uasset')),
                   lambda r: r['assets'][0]['actual_settings'].update(srgb=False),
                   lambda r: r['assets'][0]['actual_settings'].update(filter='<TextureFilter.TF_NEAREST: 0>'),
                   lambda r: r['assets'][0]['actual_settings'].update(never_stream='True'))
        for change in changes:
            r = receipt_for(self.f['manifest']); change(r)
            with self.assertRaises(ValueError): C.validate_receipt_assets(self.f['manifest'], r, self.root)

    def test_20_changed_file_pin_and_invalid_hash_rejected(self):
        value = copy.deepcopy(self.f['source_manifest']); value['sha256'] = '0' * 64
        with self.assertRaises(ValueError): C.check(value, self.root)
        value['sha256'] = 'A' * 64
        with self.assertRaises(ValueError): C.check(value, self.root)

    def test_21_json_duplicate_keys_nonfinite_rejected(self):
        for text, name in (('{"x":1,"x":2}', 'duplicate.json'), ('{"x":NaN}', 'nan.json')):
            p = RUN / name; p.write_text(text, encoding='utf-8')
            with self.assertRaises(ValueError): C.read(p)

    def test_22_exclusive_output_retains_first_bytes(self):
        p = RUN / 'exclusive.json'; original = write(p, {'first': True})
        with self.assertRaises(FileExistsError): write(p, {'overwritten': True})
        self.assertEqual(C.pin(p), original)

    def test_23_exact_membership_detects_extra_file_and_old_byte_change(self):
        root = RUN / 'membership-isolated'
        old = []
        for i in range(C.OLD_COUNT):
            rel = f'UnrealGame/Content/Production/Test/{i}.uasset'; p = root / rel
            p.parent.mkdir(parents=True, exist_ok=True); p.write_bytes(b'synthetic')
            v = C.pin(p); old.append(dict(path=rel, bytes=v['bytes'], sha256=v['sha256']))
        m = dict(old_production_files=old, assets=[])
        C.exact_membership(m, False, root)
        extra = root / 'UnrealGame/Content/Production/Test/UNLISTED.uasset'; extra.write_bytes(b'extra')
        with self.assertRaises(ValueError): C.exact_membership(m, False, root)
        wrong = copy.deepcopy(old); wrong[0]['sha256'] = '0' * 64
        with self.assertRaises(ValueError): C.verify_old(wrong, root)

    def test_24_module_load_does_not_import_unreal_or_start_native(self):
        import sys
        self.assertNotIn('unreal', sys.modules)

    def test_25_independent_saved_byte_proof_and_forged_receipt_rejections(self):
        # Deliberately synthetic .uasset bytes: exercises the host verifier only,
        # not an Unreal import or a claim that these bytes are native packages.
        spec = importlib.util.spec_from_file_location('air_import_host_fixture', HERE / 'ue-import-hero-Air48-v001.py')
        module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
        m = self.f['manifest']; manifest_path = Path(self.f['import_pin']['path'])
        r = receipt_for(m)
        for i, a in enumerate(r['assets']):
            p = Path(a['saved']['path']); p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(f'HOST_SYNTHETIC_PACKAGE_BYTES_ONLY_{i}'.encode())
            a['saved'] = C.pin(p)
        claim_pin = write(manifest_path.parent / 'synthetic-claim.json', dict(schema='Air48-native-import-claim-v001',
                         manifest=C.pin(manifest_path), replace_existing=False, actual_import_completed=False))
        r.update(schema='hero-Air48-native-import-v001', success=True, manifest=C.pin(manifest_path),
                 importer=C.pin(module.__file__), contract=C.pin(C.__file__), actual_new_saved=48, actual_total=1419,
                 verification_passes=2, old1371_unchanged=True, claim=claim_pin,
                 imported_object_paths=[[a['object_path']] for a in m['assets']],
                 existing_sword_readonly=dict(actual_class='Texture2D', actual_object_path=C.SWORD_OBJECT,
                                              actual_dimensions=[512, 512], modified=False, saved=False, reimported=False),
                 HOST_SYNTHETIC_ONLY=True, **{k: False for k in C.SCOPE_FALSE})
        receipt_pin = write(manifest_path.parent / 'synthetic-native-metadata-NOT-UE-proof.json', r)
        with patch.object(module, 'ROOT', self.root):
            module.verify_saved(manifest_path, m, receipt_pin['path'], manifest_path.parent / 'synthetic-host-byte-proof.json')
            for i, (field, value) in enumerate((('success', False), ('actual_total', 1364), ('TrialAllowed', True),
                                                ('imported_object_paths', []), ('manifest', self.f['source_manifest']))):
                bad = copy.deepcopy(r); bad[field] = value
                bad_pin = write(manifest_path.parent / f'bad-native-receipt-{i}.json', bad)
                output = manifest_path.parent / f'NEVER-created-{i}.json'
                with self.assertRaises(ValueError): module.verify_saved(manifest_path, m, bad_pin['path'], output)
                self.assertFalse(output.exists())
            bad = copy.deepcopy(r); bad['assets'][0]['saved']['sha256'] = '0' * 64
            bad_pin = write(manifest_path.parent / 'bad-saved-byte-pin.json', bad)
            with self.assertRaises(ValueError):
                module.verify_saved(manifest_path, m, bad_pin['path'], manifest_path.parent / 'NEVER-created-saved.json')

    def test_26_embedded_style_import_disables_bytecode_without_host_B_flag(self):
        import subprocess
        import sys
        need_cache_absent = HERE / '__pycache__'
        self.assertFalse(need_cache_absent.exists())
        code = ('import runpy,sys; assert not sys.dont_write_bytecode; '
                + 'runpy.run_path(' + repr(str(HERE / 'ue-import-hero-Air48-v001.py')) + ',run_name="air48_no_main"); '
                + 'assert sys.dont_write_bytecode')
        result = subprocess.run([sys.executable, '-X', 'utf8', '-c', code], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertFalse(need_cache_absent.exists())


if __name__ == '__main__':
    RUN.mkdir(parents=True, exist_ok=False)
    source_pins_before = [C.pin(HERE / n) for n in ('test_air48_import_contract_v001.py', 'air48_import_contract_v001.py',
                                                  'prepare-Air48-Root-import-v001.py', 'ue-import-hero-Air48-v001.py')]
    with (RUN / 'host-contract.log').open('x', encoding='utf-8') as stream:
        result = unittest.TextTestRunner(stream=stream, verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Air48ContractTests))
    report = dict(schema='Air48-host-contract-test-run-v001', success=result.wasSuccessful(), tests_run=result.testsRun,
                  failures=len(result.failures), errors=len(result.errors), skipped=len(result.skipped),
                  synthetic_fixtures_only=True, UE_started=False, actual_content_writes=0,
                  actual_Root_approval_created=False, native_metadata_proved=False, FinalAccepted=False,
                  test_script=C.pin(__file__), contract=C.pin(C.__file__), log=C.pin(RUN / 'host-contract.log'))
    report['source_pins_before'] = source_pins_before
    report['sources_unchanged_while_running'] = [C.pin(p['path']) for p in source_pins_before] == source_pins_before
    report['success'] = report['success'] and report['sources_unchanged_while_running']
    proof = write(RUN / 'host-contract-result.json', report)
    print(json.dumps(dict(**report, result_pin=proof), ensure_ascii=False))
    raise SystemExit(0 if result.wasSuccessful() else 1)
