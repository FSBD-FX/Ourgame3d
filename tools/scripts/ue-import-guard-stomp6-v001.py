"""Exact six approved Stomp Texture2D imports; preserve all old1326 packages."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, sys

R = Path('F:/Ourgame').resolve()
M = R/'source-assets/production/fairytale-guard-v001/root-Stomp6-import-v001/import-manifest.json'

def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def pin(p):
    p = Path(p).resolve()
    return dict(path=p.as_posix(), bytes=p.stat().st_size,
                sha256=hashlib.sha256(p.read_bytes()).hexdigest())
def need(v, why):
    if not v: raise ValueError(why)
def check(x): need(pin(x['path']) == x, 'Pin changed: '+x['path'])

m = read(M)
need(m['schema'] == 'Root-GuardStomp6-import-v001', 'Wrong manifest')
need((m['expected_old_count'], m['expected_new_count'], m['expected_final_count']) == (1326, 6, 1332), 'Wrong scope')
need(len(m['assets']) == len({x['object_path'] for x in m['assets']}) == 6, 'Exactly six unique assets required')
need(sorted((x['component'], x['frame']) for x in m['assets']) ==
     [('StompActive', 0), ('StompActive', 1)] + [('StompRecovery', i) for i in range(4)], 'Wrong phases')
for key in ['root_trial_registration', 'source_manifest', 'old_compiled_snapshot']: check(m[key])
trial = read(m['root_trial_registration']['path'])
need(trial['limited_import_approved'] is True and trial['FinalAccepted'] is False, 'Explicit limited Root import required')
for x in m['assets']:
    check(x['source']); check(x['retained_E'])
    need(x['source']['sha256'] == x['retained_E']['sha256'], 'Retained source mismatch')

def verify_old():
    need(len(m['old_production_files']) == 1326, 'Old1326 pins required')
    for x in m['old_production_files']:
        p = R/x['path']
        need(p.stat().st_size == x['bytes'] and pin(p)['sha256'] == x['sha256'], 'Old package changed: '+x['path'])
def exact_final():
    actual = {p.resolve() for p in (R/'UnrealGame/Content/Production').rglob('*') if p.is_file()}
    expected = {(R/x['path']).resolve() for x in m['old_production_files']} | {Path(x['saved_path']).resolve() for x in m['assets']}
    need(actual == expected and len(actual) == 1332, 'Exact old1326 + new6 required')

if '--verify-receipt' in sys.argv:
    rp = Path(sys.argv[sys.argv.index('--verify-receipt')+1]); rec = read(rp)
    need(rec['success'] and rec['manifest'] == pin(M) and len(rec['assets']) == 6, 'Invalid actual receipt')
    for repeat in range(2):
        verify_old(); exact_final()
        for x in rec['assets']: check(x['saved'])
    out = M.parent/('independent-import-verification-'+datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S-%f')+'.json')
    with out.open('x', encoding='utf-8') as f:
        json.dump(dict(schema='Stomp6-independent-import-twoSHA-v001', success=True,
                       manifest=pin(M), receipt=pin(rp), old1326_unchanged=True, old1326_unchanged_twice=True,
                       new6_saved=True, new6_saved_twice=True, actual_total=1332, exact_total=1332,
                       verification_passes=2, hash_mismatches=0,
                       native_draw_verified=False, FinalAccepted=False), f, ensure_ascii=False, indent=2)
    print(json.dumps(dict(success=True, receipt=pin(out)))); raise SystemExit(0)

verify_old(); verify_old()
need(len([p for p in (R/'UnrealGame/Content/Production').rglob('*') if p.is_file()]) == 1326, 'Fresh old1326 required')
need(all(not Path(x['saved_path']).exists() for x in m['assets']), 'Never replace packages')
if '--validate-only' in sys.argv:
    from PIL import Image
    for x in m['assets']:
        with Image.open(x['source']['path']) as im:
            need(im.mode == 'RGBA' and im.size == (512, 512) and im.getchannel('A').getbbox(), 'Nonempty RGBA512 required')
            need(hashlib.sha256(im.tobytes()).hexdigest() == x['source_RGBA_sha256'], 'RGBA changed')
    print(json.dumps(dict(source6_RGBA512=True, old1326_unchanged_twice=True, UE_started=False)))
    raise SystemExit(0)

import unreal
need(Path(unreal.Paths.project_dir()).resolve().parent == R, 'Wrong actual project')
rp = R/'UnrealGame/Saved/Bootstrap'/('guard-Stomp6-import-'+datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S-%f')+'.json')
rec = dict(schema='guard-Stomp6-actual-import-v001', manifest=pin(M), importer=pin(__file__), assets=[], success=False)
try:
    need(not unreal.EditorAssetLibrary.list_assets(m['namespace'], recursive=True, include_folder=False), 'Namespace occupied')
    tasks = []
    for x in m['assets']:
        need(not unreal.EditorAssetLibrary.does_asset_exist(x['package_path']), 'Object already exists')
        task = unreal.AssetImportTask()
        for k, v in [('filename', x['source']['path']), ('destination_path', m['namespace']),
                     ('destination_name', x['name']), ('automated', True), ('save', False), ('replace_existing', False)]:
            task.set_editor_property(k, v)
        tasks.append(task)
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks(tasks)
    settings = dict(compression_settings=unreal.TextureCompressionSettings.TC_EDITOR_ICON,
                    mip_gen_settings=unreal.TextureMipGenSettings.TMGS_NO_MIPMAPS,
                    lod_group=unreal.TextureGroup.TEXTUREGROUP_UI, never_stream=True, srgb=True,
                    filter=unreal.TextureFilter.TF_BILINEAR)
    for x, task in zip(m['assets'], tasks):
        need(list(task.get_editor_property('imported_object_paths')) == [x['object_path']], 'Imported path mismatch')
        tex = unreal.load_asset(x['package_path'])
        need(isinstance(tex, unreal.Texture2D) and tex.get_path_name() == x['object_path'], 'Wrong Texture2D')
        need([tex.blueprint_get_size_x(), tex.blueprint_get_size_y()] == [512, 512], 'Wrong dimensions')
        filenames = list(tex.get_editor_property('asset_import_data').extract_filenames())
        need(len(filenames) == 1 and Path(filenames[0]).resolve() == Path(x['source']['path']).resolve(), 'Wrong provenance')
        for k, v in settings.items():
            tex.set_editor_property(k, v); need(tex.get_editor_property(k) == v, 'Wrong setting: '+k)
        need(unreal.EditorAssetLibrary.save_loaded_asset(tex, False), 'Save failed')
        rec['assets'].append(dict(component=x['component'], frame=x['frame'], source=x['source'],
                                 actual_object_path=tex.get_path_name(), actual_class=tex.get_class().get_name(),
                                 actual_dimensions=[512,512], actual_import_filenames=filenames,
                                 actual_settings={k: str(tex.get_editor_property(k)) for k in settings}, saved=pin(x['saved_path'])))
    need(set(unreal.EditorAssetLibrary.list_assets(m['namespace'], recursive=True, include_folder=False)) ==
         {x['object_path'] for x in m['assets']}, 'Native registry mismatch')
    verify_old(); verify_old(); exact_final()
    rec.update(success=True, actual_total=1332, verification_passes=2, old1326_unchanged=True,
               native_draw_verified=False, FinalAccepted=False)
except Exception as error:
    rec['failure'] = str(error); raise
finally:
    with rp.open('x', encoding='utf-8') as f: json.dump(rec, f, ensure_ascii=False, indent=2)
    unreal.log('Guard Stomp6 actual import receipt: '+str(rp))
