"""Pinned native169 body/actual palm data for a bounded UE fit trial."""
from pathlib import Path
import hashlib
import importlib.util
import json

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / 'source-assets/production/fairytale-sword-primary2-runtime-v001'
MANIFEST = BASE / 'manifests/import-sword-primary2-v001.json'
MANIFEST_SHA = '7297932b9cbd299ea52efb6c304bdfb799547a8851dda4044b79d65a3fd3a749'
FREEZE = BASE / 'ready-for-root-import-freeze-v001.json'
FREEZE_SHA = '2c0156cc3f72b80f08832f2cb2a1690c19c868012098a20ab67ae79786e250be'
NAMESPACE = '/Game/Production/ArtTrials/EV048/v008/HeroSwordPrimary2'
DISK = ROOT / 'UnrealGame/Content/Production/ArtTrials/EV048/v008/HeroSwordPrimary2'
DECODER = Path(__file__).with_name('ue-import-armor-primary2-four-v001.py')
DECODER_SHA = '5c667edbeb81eac54648d14ff92b8883d1b15a39a05cc3b56c17933dd29eb49a'

def require(value, why):
    if not value: raise ValueError(why)

def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def checked(row):
    p = Path(row['path']).resolve()
    require(p.is_relative_to(ROOT), 'Foreign source pin')
    require(p.stat().st_size == row['bytes'] and sha(p) == row['sha256'], 'Pinned file changed: ' + str(p))

def old_packages_unchanged():
    p = BASE / 'manifests/old-production983-before-import.json'
    rows = json.loads(p.read_text(encoding='utf-8-sig'))['files']
    require(len(rows) == 983, 'Wrong prior package count')
    for row in rows:
        checked({**row, 'path': (ROOT / row['path']).as_posix()})
    return len(rows)

def imported_packages_unchanged(document):
    pointer = json.loads((BASE / 'manifests/actual-import-receipt-ref.json').read_text(encoding='utf-8-sig'))
    checked(pointer)
    receipt = json.loads(Path(pointer['path']).read_text(encoding='utf-8-sig'))
    require(receipt['success'] and receipt['actual_count'] == receipt['saved_count'] == 6
            and receipt['manifest_sha256'] == MANIFEST_SHA, 'Six actual imports not proven')
    require(len(receipt['assets']) == 6, 'Wrong actual receipt rows')
    for source, actual in zip(document['assets'], receipt['assets']):
        require(source['object_path'] == actual['object_path'] and source['source_sha256'] == actual['source_sha256'], 'Actual source mismatch')
        p = Path(actual['saved_uasset'])
        require(p.resolve() == (DISK / (source['name'] + '.uasset')).resolve(), 'Wrong native saved path')
        checked({'path': str(p), 'bytes': actual['saved_bytes'], 'sha256': actual['saved_sha256']})
    require({p.name for p in DISK.iterdir() if p.is_file()} == {r['name'] + '.uasset' for r in document['assets']}, 'Unexpected namespace files')
    return 6

def preflight(require_unused=True):
    require(sha(MANIFEST) == MANIFEST_SHA and sha(FREEZE) == FREEZE_SHA and sha(DECODER) == DECODER_SHA, 'Frozen input mismatch')
    for row in json.loads(FREEZE.read_text(encoding='utf-8-sig'))['files']: checked(row)
    d = json.loads(MANIFEST.read_text(encoding='utf-8-sig'))
    require(d['schema'] == 'frozen-fairytale-sword-primary2-six-v1' and d['frozen'] and d['ready_for_root_import'], 'Wrong frozen candidate')
    require(d['asset_count'] == 6 and d['namespace'] == NAMESPACE and d['canvas_px'] == [512,512] and d['native_facing'] == 1, 'Wrong native layout')
    require(d['display_pivot_px'] == [256,464] and d['preview_canvas_size'] == 72*512/416 and not d['per_frame_resize'], 'Wrong display geometry')
    require(d['durations_ms'] == {'Primary2': [75,75,60,60,135,135]} and d['standard_preview_durations_ms'] == [100]*6
            and not d['standard_preview_timing_passed'], 'Timing provenance changed')
    require(not any(d[k] for k in ('runtime_verified','imported','armor_present','full_motion_accepted','thumb_accepted','grip_accepted','foot_lock_accepted'))
            and d['formal_complete_units'] == 0, 'Candidate cannot grant acceptance')
    for row in d['references'].values(): checked(row)
    for key in ('marker_json','marker_inl_candidate','old_production_disk_inventory'): checked(d[key])
    spec = importlib.util.spec_from_file_location('primary2_native_png_decoder', DECODER)
    decoder = importlib.util.module_from_spec(spec); spec.loader.exec_module(decoder)
    require([(r['clip'],r['frame']) for r in d['assets']] == [('Primary2',i) for i in range(6)], 'Wrong six-frame set/order')
    for row in d['assets']:
        path = Path(row['source'])
        checked({'path': str(path), 'bytes': row['source_bytes'], 'sha256': row['source_sha256']})
        checked(row['canonical_curated'])
        require(path.read_bytes() == Path(row['canonical_curated']['path']).read_bytes(), 'Native source was altered')
        name = f'T_Fairytale_SwordPrimary2_{row["frame"]:03d}_v001'
        require((row['name'],row['package_path'],row['object_path']) == (name,NAMESPACE+'/'+name,NAMESPACE+'/'+name+'.'+name), 'Destination mismatch')
        pixels = decoder.inspect_rgba_png(path.read_bytes())
        require(pixels['nonempty'] and pixels['corners_transparent'] and pixels['alpha_extrema'] == [0,255]
                and pixels['bbox_px'] == row['source_bbox'] and row['source_bbox'][3]-row['source_bbox'][1] <= 416, 'Native PNG source mismatch')
    require(len({r['source_sha256'] for r in d['assets']}) == 6, 'Duplicate phase pixels')
    if require_unused:
        require(not DISK.exists() or not any(p.is_file() for p in DISK.rglob('*')), 'Do not overwrite a prior namespace')
    else: imported_packages_unchanged(d)
    old_packages_unchanged()
    return d
