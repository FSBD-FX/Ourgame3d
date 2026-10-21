"""Exact48 native texture preparation or independent host byte verification.

No mode defaults to import. Native mode requires explicit --native-import or the
Root launcher's DUNGEON_AIR48_NATIVE=1, immutable approval, and host decode proof.
Any partial package, receipt, claim or log is retained; no retries/rollback.
"""
from pathlib import Path
from datetime import datetime, timezone
import argparse
import json
import os
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from air48_import_contract_v001 import (
    ROOT, NAMESPACE, SWORD_OBJECT, OLD_COUNT, NEW_COUNT, FINAL_COUNT, SCOPE_FALSE,
    need, read, resolve, pin, check, write_new, load_import, verify_old,
    exact_membership, validate_receipt_assets)


def verify_saved(manifest_path, m, receipt_path, output_path):
    receipt_path = resolve(receipt_path, within=Path(manifest_path).parent)
    receipt = read(receipt_path)
    need(receipt['schema'] == 'hero-Air48-native-import-v001' and receipt['success'] is True,
         'Actual import success receipt missing')
    need(receipt['manifest'] == pin(manifest_path) and receipt['importer'] == pin(__file__)
         and receipt['contract'] == pin(Path(__file__).with_name('air48_import_contract_v001.py')),
         'Receipt binds different manifest/importer/contract')
    need(receipt['actual_new_saved'] == NEW_COUNT and receipt['actual_total'] == FINAL_COUNT
         and receipt['verification_passes'] == 2 and receipt['old1371_unchanged'] is True,
         'Receipt totals/old preservation changed')
    need(receipt['imported_object_paths'] == [[x['object_path']] for x in m['assets']], 'Native imported48 task paths differ')
    claim = read(check(receipt['claim'], within=Path(manifest_path).parent))
    need(claim['schema'] == 'Air48-native-import-claim-v001' and claim['manifest'] == pin(manifest_path)
         and claim['replace_existing'] is False and claim['actual_import_completed'] is False,
         'Native exclusive claim differs')
    need(all(receipt[k] is False for k in SCOPE_FALSE), 'Import receipt exceeds limited scope')
    need(receipt['existing_sword_readonly']['actual_class'] == 'Texture2D'
         and receipt['existing_sword_readonly']['actual_object_path'] == SWORD_OBJECT
         and receipt['existing_sword_readonly']['actual_dimensions'] == [512, 512]
         and all(receipt['existing_sword_readonly'][k] is False for k in ('modified', 'saved', 'reimported')), 'Existing sword metadata differs')
    validate_receipt_assets(m, receipt, ROOT)
    for repeat in range(2):
        verify_old(m['old_production_files'], ROOT)
        exact_membership(m, True, ROOT)
        for a in receipt['assets']:
            check(a['saved'], within=ROOT / 'UnrealGame/Content/Production')
    output_path = resolve(output_path, within=Path(manifest_path).parent)
    proof = dict(schema='Air48-independent-saved-byte-twoSHA-v001', success=True,
                 manifest=pin(manifest_path), native_receipt=pin(receipt_path), verifier=pin(__file__),
                 old1371_exact_membership_unchanged_twice=True, new48_saved_pins_verified_twice=True,
                 actual_total=FINAL_COUNT, actual_new_saved=NEW_COUNT, verification_passes=2, hash_mismatches=0,
                 native_metadata_receipt_checked=True,
                 scope='Fresh independent host file-byte checks plus exact native metadata receipt contract; no fresh UE metadata readback, draw or visual acceptance.',
                 **{k: False for k in SCOPE_FALSE})
    proof_pin = write_new(output_path, proof)
    print(json.dumps(dict(success=True, independent_verification=proof_pin, actual_total=FINAL_COUNT)))


def native(manifest_path, m, receipt_path):
    import unreal
    need(resolve(unreal.Paths.project_dir()) == ROOT / 'UnrealGame', 'Wrong actual Unreal project')
    receipt_path = resolve(receipt_path, within=Path(manifest_path).parent)
    need(receipt_path.parent.is_dir() and not receipt_path.exists(), 'Fresh receipt path required')
    # Claim before the first native mutation, exclusive-create and preserve forever.
    claim_path = receipt_path.with_name(receipt_path.stem + '-claim.json')
    claim_pin = write_new(claim_path, dict(schema='Air48-native-import-claim-v001',
                                         manifest=pin(manifest_path), actual_import_completed=False,
                                         replace_existing=False, **{k: False for k in SCOPE_FALSE}))
    receipt = dict(schema='hero-Air48-native-import-v001', utc=datetime.now(timezone.utc).isoformat(),
                   manifest=pin(manifest_path), importer=pin(__file__),
                   contract=pin(Path(__file__).with_name('air48_import_contract_v001.py')),
                   claim=claim_pin, assets=[], imported_object_paths=[], success=False,
                   automatic_retry_allowed=False, **{k: False for k in SCOPE_FALSE})
    try:
        need(not unreal.EditorAssetLibrary.list_assets(NAMESPACE, recursive=True, include_folder=False),
             'Native destination namespace occupied')
        need(not (ROOT / 'UnrealGame/Content' / NAMESPACE[6:]).exists(), 'Disk namespace exists')
        for repeat in range(2):
            verify_old(m['old_production_files'])
            exact_membership(m, False)
        sword = unreal.load_asset(SWORD_OBJECT)
        need(isinstance(sword, unreal.Texture2D) and sword.get_path_name() == SWORD_OBJECT,
             'Existing independent sword must be native Texture2D')
        sword_size = [sword.blueprint_get_size_x(), sword.blueprint_get_size_y()]
        need(sword_size == [512, 512], 'Existing sword native dimensions differ')
        receipt['existing_sword_readonly'] = dict(actual_class=sword.get_class().get_name(),
                                                actual_object_path=sword.get_path_name(), actual_dimensions=sword_size,
                                                modified=False, saved=False, reimported=False)
        tasks = []
        for x in m['assets']:
            need(not Path(x['saved_path']).exists() and not unreal.EditorAssetLibrary.does_asset_exist(x['package_path']),
                 'Native target already exists')
            task = unreal.AssetImportTask()
            for key, value in (('filename', x['source']['path']), ('destination_path', NAMESPACE),
                               ('destination_name', x['name']), ('automated', True), ('save', False),
                               ('replace_existing', False), ('replace_existing_settings', False)):
                task.set_editor_property(key, value)
            tasks.append(task)
        unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks(tasks)
        receipt['imported_object_paths'] = [list(t.get_editor_property('imported_object_paths')) for t in tasks]
        settings = dict(compression_settings=unreal.TextureCompressionSettings.TC_EDITOR_ICON,
                        mip_gen_settings=unreal.TextureMipGenSettings.TMGS_NO_MIPMAPS,
                        lod_group=unreal.TextureGroup.TEXTUREGROUP_UI, never_stream=True, srgb=True,
                        filter=unreal.TextureFilter.TF_BILINEAR)
        for x, task in zip(m['assets'], tasks):
            need(list(task.get_editor_property('imported_object_paths')) == [x['object_path']], 'Unexpected imported object path')
            tex = unreal.load_asset(x['package_path'])
            need(isinstance(tex, unreal.Texture2D) and tex.get_path_name() == x['object_path'], 'Actual Texture2D object differs')
            dims = [tex.blueprint_get_size_x(), tex.blueprint_get_size_y()]
            need(dims == [512, 512], 'Actual texture dimensions differ')
            import_data = tex.get_editor_property('asset_import_data')
            need(import_data is not None, 'Native source import data missing')
            filenames = list(import_data.extract_filenames())
            need(len(filenames) == 1 and resolve(filenames[0]) == resolve(x['source']['path']), 'Import filename readback differs')
            for key, value in settings.items():
                tex.set_editor_property(key, value)
                need(tex.get_editor_property(key) == value, 'Texture setting readback differs: ' + key)
            # UE SavePackage lacks atomic CREATE_NEW: Root runs this in an isolated
            # sequential editor. Recheck immediately; no preexisting target is saved.
            need(not Path(x['saved_path']).exists(), 'Target appeared before save; preserve failure')
            need(unreal.EditorAssetLibrary.save_loaded_asset(tex, False), 'Native save failed')
            actual_settings = {k: bool(tex.get_editor_property(k)) if k in ('never_stream', 'srgb')
                               else str(tex.get_editor_property(k)) for k in settings}
            receipt['assets'].append(dict(component=x['component'], frame=x['frame'], source=x['source'],
                                           actual_object_path=tex.get_path_name(), actual_class=tex.get_class().get_name(),
                                           actual_dimensions=dims, actual_import_filenames=filenames,
                                           actual_settings=actual_settings, saved=pin(x['saved_path'])))
        need(set(unreal.EditorAssetLibrary.list_assets(NAMESPACE, recursive=True, include_folder=False))
             == {x['object_path'] for x in m['assets']}, 'Native exact48 namespace membership differs')
        validate_receipt_assets(m, receipt)
        for repeat in range(2):
            verify_old(m['old_production_files'])
            exact_membership(m, True)
            for a in receipt['assets']:
                check(a['saved'])
        receipt.update(success=True, old1371_unchanged=True, actual_new_saved=NEW_COUNT,
                       actual_total=FINAL_COUNT, verification_passes=2)
    except Exception as error:
        receipt['failure'] = repr(error)
        raise
    finally:
        # Exclusive output. A failed write is retained and never replaced.
        write_new(receipt_path, receipt)
        unreal.log('Air48 native import receipt: ' + str(receipt_path))


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--manifest', default=os.environ.get('DUNGEON_AIR48_IMPORT_MANIFEST'))
    modes = p.add_mutually_exclusive_group()
    modes.add_argument('--validate-only', action='store_true')
    modes.add_argument('--verify-receipt')
    modes.add_argument('--native-import', action='store_true')
    p.add_argument('--receipt-output', default=os.environ.get('DUNGEON_AIR48_RECEIPT_OUTPUT'))
    p.add_argument('--verification-output')
    a = p.parse_args()
    native_mode = a.native_import or (os.environ.get('DUNGEON_AIR48_NATIVE') == '1'
                                     and not a.validate_only and not a.verify_receipt)
    need(a.manifest and (a.validate_only or a.verify_receipt or native_mode), 'Explicit manifest and mode required')
    manifest_path = resolve(a.manifest, within=ROOT / 'source-assets/production')
    # Unreal has no Pillow dependency. Exact host receipt is checked and every
    # frozen input/source/E member is hashed again inside embedded Python.
    m = load_import(manifest_path, decode_rgba=not native_mode)
    if a.verify_receipt:
        need(a.verification_output, 'NEW independent verification output required')
        verify_saved(manifest_path, m, a.verify_receipt, a.verification_output)
        return
    for repeat in range(2):
        verify_old(m['old_production_files'])
        exact_membership(m, False)
    need(not (ROOT / 'UnrealGame/Content' / NAMESPACE[6:]).exists()
         and all(not Path(x['saved_path']).exists() for x in m['assets']), 'New namespace/packages must be absent')
    if a.validate_only:
        print(json.dumps(dict(success=True, source48_RGBA512=True, actual_E_ZIPmember_twoSHA=True,
                              old1371_unchanged_twice=True, expected_final_count=FINAL_COUNT, UE_started=False,
                              **{k: False for k in SCOPE_FALSE})))
        return
    need(a.receipt_output, 'NEW native receipt output required')
    native(manifest_path, m, a.receipt_output)


if __name__ == '__main__':
    main()
