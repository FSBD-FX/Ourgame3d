"""Root-run candidate: fourteen exclusive new Texture2D assets; never pixel edits.

Host --validate-only decodes original RGBA and checks exact body-owner union.
Native --native-import requires that pinned host proof. No implicit import,
reimport, retry, rollback, overwrite, SaveSource, source-code or config mutation.
"""
from pathlib import Path
from datetime import datetime, timezone
import argparse
import hashlib
import json
import sys

sys.dont_write_bytecode = True
ROOT = Path('F:/Ourgame')
CANDIDATE = Path(__file__).resolve().parent.parent
MANIFEST = CANDIDATE / 'import/import-manifest-v001.json'


def need(value, message):
    if not value:
        raise AssertionError(message)


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def pin(path):
    path = Path(path).resolve()
    data = path.read_bytes()
    return dict(path=path.as_posix(), bytes=len(data), sha256=hashlib.sha256(data).hexdigest())


def check(row, base=None):
    path = Path(row['path'])
    if not path.is_absolute():
        need(base is not None, 'Relative pin has no explicit root')
        path = base / path
    actual = pin(path)
    need(actual['bytes'] == row['bytes'] and actual['sha256'] == row['sha256'], 'Byte pin mismatch: ' + str(path))
    return path.resolve()


def write_new(path, value):
    path = Path(path).resolve()
    need(path.parent.is_dir(), 'Receipt parent must already exist')
    with path.open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write('\n')
    return pin(path)


def baseline_rows(m):
    cm = read(check(m['baseline_compiled_manifest']))
    rows = [x for x in cm['files'] if x['path'].startswith('UnrealGame/Content/Production/')]
    need(len(rows) == 1425 and cm['production_files'] == 1425, 'Baseline Production count differs')
    return rows


def verify_production(m, imported=False):
    rows = baseline_rows(m)
    for row in rows:
        check(row, ROOT)
    expected = {(ROOT / x['path']).resolve() for x in rows}
    if imported:
        expected |= {Path(x['saved_path']).resolve() for x in m['assets']}
    actual = {x.resolve() for x in (ROOT / 'UnrealGame/Content/Production').rglob('*') if x.is_file()}
    need(actual == expected, 'Production exact membership differs')
    return len(actual)


def load_manifest(decode=False):
    m = read(MANIFEST)
    need(m['schema'] == 'request258-Primary1-14-new-textures-import-manifest-v001', 'Manifest schema differs')
    need(len(m['assets']) == 14 and m['new_texture_count'] == 14, 'Fourteen sources required')
    need(m['baseline_production_count'] == 1425 and m['expected_final_production_count'] == 1439, 'Manifest counts differ')
    need(m['texture_settings'] == dict(compression_settings='TC_EDITOR_ICON', mip_gen_settings='TMGS_NO_MIPMAPS',
         lod_group='TEXTUREGROUP_UI', filter='TF_BILINEAR', never_stream=True, srgb=True), 'Settings contract differs')
    need(m['native_source_dimensions'] == [512, 512] and m['source_pixel_edits'] is False, 'Source dimensions/edit policy differs')
    mf = read(check(m['matte_freeze']))
    need(len(mf['members']) == 23 and len(mf['dependency_pins']) == 32, 'Matte freeze closure differs')
    for row in mf['members'] + mf['dependency_pins']:
        check(row)
    fm = read(check(m['source_frame_map']))
    source_names = {'ShoulderFar': 'FarShoulder', 'ShoulderNear': 'NearShoulder'}
    components = ('BodyRest', 'ShoulderFar', 'Chest', 'NearArmWithoutHand', 'ShoulderNear', 'HelmetForeground', 'NearHand')
    expected_keys = {(frame, component) for frame in (0, 1) for component in components}
    need({(x['frame'], x['component']) for x in m['assets']} == expected_keys, 'Missing/duplicate texture frame-owner')
    need(len({x['object_path'] for x in m['assets']}) == 14, 'Duplicate target object')
    for x in m['assets']:
        source_component = source_names.get(x['component'], x['component'])
        need(x['source_component'] == source_component and x['source'] == fm['frames'][x['frame']]['component_sources'][source_component], 'Source mapping differs')
        check(x['source'])
        name = f'T_Fairytale_Bridge258_{x["component"]}_{x["frame"]:03d}_v001'
        package = m['namespace'] + '/' + name
        need(x['name'] == name and x['package_path'] == package and x['object_path'] == package + '.' + name, 'Target path differs')
        need(Path(x['saved_path']).resolve() == Path(m['disk_namespace']).resolve() / (name + '.uasset'), 'Target disk path differs')
    if decode:
        from PIL import Image
        import numpy as np
        for x in m['assets']:
            with Image.open(x['source']['path']) as im:
                im.load()
                need(im.mode == 'RGBA' and im.size == (512, 512), 'Source must be native RGBA512')
                alpha = np.asarray(im)[..., 3]
                need(int(alpha.min()) == 0 and int(alpha.max()) > 0, 'Layer lacks transparent background or visible source')
        for frame in (0, 1):
            owners = [x for x in m['assets'] if x['frame'] == frame and x['component'] in ('BodyRest', 'NearArmWithoutHand', 'HelmetForeground', 'NearHand')]
            arrays = [np.asarray(Image.open(x['source']['path']).convert('RGBA')) for x in owners]
            occupied = np.stack([a[..., 3] > 0 for a in arrays])
            need(int(occupied.sum(axis=0).max()) == 1, 'Body owners overlap')
            reconstructed = np.zeros((512, 512, 4), dtype=np.uint8)
            for a in arrays:
                visible = a[..., 3] > 0
                reconstructed[visible] = a[visible]
            target = np.asarray(Image.open(check(fm['frames'][frame]['body_source'])).convert('RGBA'))
            visible = target[..., 3] > 0
            need(np.array_equal(reconstructed[..., 3], target[..., 3]), 'Body alpha union differs')
            need(np.array_equal(reconstructed[visible], target[visible]), 'Visible cleaned RGBA body union differs')
            need(fm['frames'][frame]['Root'] == [256, 464], 'Root differs')
            need(fm['frames'][frame]['Grip'] == ([211, 343] if frame == 0 else [159, 213]), 'Grip differs')
            need(fm['frames'][frame]['Axis'] == ([.94, -.341] if frame == 0 else [-.2, -.98]), 'Axis differs')
    return m


def finish_compilation(unreal, texture, receipt, stage):
    event = dict(texture=texture.get_path_name(), stage=stage,
                 command='Editor.AsyncTextureCompilationFinishAll',
                 before=[texture.blueprint_get_size_x(), texture.blueprint_get_size_y()])
    receipt.setdefault('compilation_barriers', []).append(event)
    unreal.SystemLibrary.execute_console_command(None, event['command'])
    event['after'] = [texture.blueprint_get_size_x(), texture.blueprint_get_size_y()]
    need(event['after'] == [512, 512], 'Native size differs after compilation finish')
    return event['after']


def native(m, host_proof_path, receipt_path):
    import unreal
    need(Path(unreal.Paths.project_dir()).resolve() == ROOT / 'UnrealGame', 'Wrong live project')
    freeze = read(CANDIDATE / 'candidate-freeze-v001.json')
    actual_members = {p.resolve() for p in CANDIDATE.rglob('*') if p.is_file() and p.name != 'candidate-freeze-v001.json'}
    need(actual_members == {Path(x['path']).resolve() for x in freeze['members']}, 'Frozen candidate membership differs')
    for row in freeze['members'] + freeze['dependency_pins']:
        check(row)
    need(Path(host_proof_path).resolve() == CANDIDATE / 'reports/host-preflight-v002.json', 'Use frozen exact host proof')
    proof = read(host_proof_path)
    need(proof['passed'] is True and proof['manifest'] == pin(MANIFEST) and proof['importer'] == pin(__file__), 'Exact host source-decode proof required')
    need(proof['source14_RGBA512'] is True and proof['cleaned_body_union_verified'] is True, 'Host decode gates missing')
    receipt_path = Path(receipt_path).resolve()
    need(receipt_path.is_relative_to(ROOT) and not receipt_path.is_relative_to(CANDIDATE), 'Fresh Root-owned output outside frozen candidate required')
    need(receipt_path.parent.is_dir() and not receipt_path.exists(), 'Fresh receipt path required')
    claim = write_new(receipt_path.with_name(receipt_path.stem + '-claim.json'),
                      dict(schema='request258-native-import-claim-v001', manifest=pin(MANIFEST), replace_existing=False, automatic_retry_allowed=False))
    receipt = dict(schema='request258-14-native-import-v001', utc=datetime.now(timezone.utc).isoformat(),
                   manifest=pin(MANIFEST), importer=pin(__file__), host_proof=pin(host_proof_path), claim=claim,
                   actual_count=0, saved_count=0, assets=[], success=False, automatic_retry_allowed=False,
                   runtime_verified=False, visual_accepted=False, motion_accepted=False, FinalAccepted=False)
    try:
        need(not Path(m['disk_namespace']).exists(), 'Disk namespace already exists; preserve, no retry')
        need(not unreal.EditorAssetLibrary.list_assets(m['namespace'], recursive=True, include_folder=False), 'Registry namespace occupied')
        for _ in range(2):
            verify_production(m)
        tasks = []
        for x in m['assets']:
            need(not unreal.EditorAssetLibrary.does_asset_exist(x['package_path']), 'Target object exists')
            task = unreal.AssetImportTask()
            for k, v in dict(filename=x['source']['path'], destination_path=m['namespace'], destination_name=x['name'],
                             automated=True, save=False, replace_existing=False, replace_existing_settings=False).items():
                task.set_editor_property(k, v)
            tasks.append(task)
        unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks(tasks)
        settings = dict(compression_settings=unreal.TextureCompressionSettings.TC_EDITOR_ICON,
                        mip_gen_settings=unreal.TextureMipGenSettings.TMGS_NO_MIPMAPS,
                        lod_group=unreal.TextureGroup.TEXTUREGROUP_UI, filter=unreal.TextureFilter.TF_BILINEAR,
                        never_stream=True, srgb=True)
        for x, task in zip(m['assets'], tasks):
            need(list(task.get_editor_property('imported_object_paths')) == [x['object_path']], 'Imported paths differ')
            tex = unreal.load_asset(x['package_path'])
            need(isinstance(tex, unreal.Texture2D) and tex.get_path_name() == x['object_path'], 'Not exact Texture2D')
            finish_compilation(unreal, tex, receipt, 'before_settings')
            filenames = list(tex.get_editor_property('asset_import_data').extract_filenames())
            need(len(filenames) == 1 and Path(filenames[0]).resolve() == Path(x['source']['path']).resolve(), 'Native import source path differs')
            for k, v in settings.items():
                tex.set_editor_property(k, v)
                need(tex.get_editor_property(k) == v, 'Texture property readback differs: ' + k)
            dims = finish_compilation(unreal, tex, receipt, 'after_settings_before_save')
            receipt['actual_count'] += 1
            need(not Path(x['saved_path']).exists(), 'Target appeared before save')
            need(unreal.EditorAssetLibrary.save_loaded_asset(tex, False), 'Exclusive new texture save failed')
            actual = {k: bool(tex.get_editor_property(k)) if k in ('never_stream', 'srgb') else str(tex.get_editor_property(k)) for k in settings}
            receipt['assets'].append(dict(frame=x['frame'], component=x['component'], source=x['source'], actual_object_path=tex.get_path_name(),
                 actual_class=tex.get_class().get_name(), actual_dimensions=dims, actual_settings=actual, actual_import_filenames=filenames, saved=pin(x['saved_path'])))
            receipt['saved_count'] += 1
        registered = list(unreal.EditorAssetLibrary.list_assets(m['namespace'], recursive=True, include_folder=False))
        need(len(registered) == 14 and set(registered) == {x['object_path'] for x in m['assets']}, 'Native registry exact membership differs')
        for _ in range(2):
            need(verify_production(m, imported=True) == 1439, 'Final count differs')
            for x in receipt['assets']:
                check(x['saved'])
        receipt.update(success=True, old1425_unchanged=True, verification_passes=2, final_production_count=1439)
    except Exception as error:
        receipt['failure'] = repr(error)
        raise
    finally:
        write_new(receipt_path, receipt)
        unreal.log('Request258 fourteen-texture import receipt: ' + str(receipt_path))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument('--validate-only', action='store_true')
    modes.add_argument('--native-import', action='store_true')
    parser.add_argument('--host-proof')
    parser.add_argument('--output')
    a = parser.parse_args()
    m = load_manifest(decode=a.validate_only)
    if a.validate_only:
        for _ in range(2):
            verify_production(m)
        need(not Path(m['disk_namespace']).exists(), 'Fresh destination absent gate failed')
        report = dict(schema='request258-host-preflight-v001', passed=True, manifest=pin(MANIFEST), importer=pin(__file__),
                      source14_RGBA512=True, cleaned_body_union_verified=True, old1425_unchanged_twice=True,
                      destination_absent=True, UE_started=False, new_source_admitted=False, final_art_accepted=False)
        if a.output:
            report['output_written'] = True
            print(json.dumps(write_new(a.output, report)))
        else:
            print(json.dumps(report))
        return
    need(a.host_proof and a.output, 'Native mode requires pinned host proof and fresh output')
    native(m, a.host_proof, a.output)


if __name__ == '__main__':
    main()
