"""Pinned native155Ready and157Primary1 body-only trial sources."""
from pathlib import Path
import hashlib, importlib.util, json

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT/'source-assets/production/fairytale-sword-runtime-v001/manifests/import-sword-body-v001.json'
MANIFEST_SHA = '267ff08aa63dcaf35a3bdbd3c134c92b6f35bab1858293f8272ab82273e8f891'
NAMESPACE = '/Game/Production/ArtTrials/EV048/v004/HeroSwordBody'
DISK = ROOT/'UnrealGame/Content/Production/ArtTrials/EV048/v004/HeroSwordBody'
DECODER = Path(__file__).with_name('ue-import-armor-primary2-four-v001.py')
DECODER_SHA = '5c667edbeb81eac54648d14ff92b8883d1b15a39a05cc3b56c17933dd29eb49a'

def require(value, why):
    if not value: raise ValueError(why)

def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def old_packages_unchanged():
    rows = json.loads((MANIFEST.parent/'old-production897-before-import.json').read_text(encoding='utf-8'))['files']
    require(len(rows)==897, 'Wrong prior package inventory')
    for row in rows:
        path = ROOT/row['path']
        require(path.stat().st_size==row['bytes'] and sha(path)==row['sha256'], 'Prior package changed: '+str(path))
    return len(rows)

def imported_packages_unchanged(document):
    pointer = json.loads((MANIFEST.parent/'actual-import-receipt-ref.json').read_text(encoding='utf-8'))
    path = Path(pointer['path']); require(sha(path)==pointer['sha256'], 'Import receipt changed')
    receipt = json.loads(path.read_text(encoding='utf-8-sig'))
    require(receipt['success'] and receipt['actual_count']==receipt['saved_count']==10
            and receipt['manifest_sha256']==MANIFEST_SHA and len(receipt['assets'])==10, 'Ten body imports not proven')
    for source, actual in zip(document['assets'], receipt['assets']):
        path = Path(actual['saved_uasset'])
        require(source['object_path']==actual['object_path'] and source['source_sha256']==actual['source_sha256'], 'Imported source mismatch')
        require(path.resolve()==(DISK/(source['name']+'.uasset')).resolve()
                and path.stat().st_size==actual['saved_bytes'] and sha(path)==actual['saved_sha256'], 'Imported package changed')
    require({p.name for p in DISK.iterdir() if p.is_file()}=={a['name']+'.uasset' for a in document['assets']}, 'Unexpected namespace files')
    return 10

def preflight(require_unused=True):
    require(sha(MANIFEST)==MANIFEST_SHA and sha(DECODER)==DECODER_SHA, 'Frozen manifest/decoder mismatch')
    document = json.loads(MANIFEST.read_text(encoding='utf-8'))
    require(document['schema']=='frozen-fairytale-sword-body-ten-v1' and document['frozen'] and document['asset_count']==10, 'Wrong source contract')
    require(document['namespace']==NAMESPACE and document['canvas_px']==[512,512]
            and document['durations_ms']=={'Ready':[167]*4,'Primary1':[85,85,60,60,155,155]} and document['native_facing']==1, 'Source layout/timing mismatch')
    require(document['display_pivot_px']==[256,464] and document['preview_canvas_size']==72*512/416
            and not document['per_frame_resize'], 'Display registration mismatch')
    require(not document['runtime_verified'] and not document['full_motion_accepted']
            and not document['thumb_accepted'] and document['formal_complete_units']==0, 'Source manifest cannot grant acceptance')
    for row in document['references'].values():
        path=Path(row['path'])
        require(path.resolve().is_relative_to(ROOT) and path.stat().st_size==row['bytes'] and sha(path)==row['sha256'], 'Reference changed')
    spec=importlib.util.spec_from_file_location('limb_native_decoder',DECODER)
    decoder=importlib.util.module_from_spec(spec);spec.loader.exec_module(decoder)
    require([(a['clip'],a['frame']) for a in document['assets']]
            ==[(clip,i) for clip,n in [('Ready',4),('Primary1',6)] for i in range(n)], 'Component order mismatch')
    for row in document['assets']:
        path=Path(row['source']);name=f'T_Fairytale_Sword{row["clip"]}_{row["frame"]:03d}_v001'
        require(path.stat().st_size==row['source_bytes'] and sha(path)==row['source_sha256'], 'Source changed')
        require((row['name'],row['package_path'],row['object_path'])
                ==(name,NAMESPACE+'/'+name,NAMESPACE+'/'+name+'.'+name), 'Destination mismatch')
        pixels=decoder.inspect_rgba_png(path.read_bytes())
        require(pixels['nonempty'] and pixels['corners_transparent'] and pixels['alpha_extrema']==[0,255]
                and pixels['bbox_px']==row['source_bbox'], 'Invalid source RGBA')
    require(len({a['source_sha256'] for a in document['assets']})==10, 'Duplicate component frames')
    if require_unused:
        require(not DISK.exists() or not any(p.is_file() for p in DISK.rglob('*')), 'Do not replace a prior namespace')
    else: imported_packages_unchanged(document)
    old_packages_unchanged()
    return document
