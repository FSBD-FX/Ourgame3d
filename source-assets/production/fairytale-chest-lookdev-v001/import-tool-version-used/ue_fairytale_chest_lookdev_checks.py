"""Pinned four-component source trial. Never grants full armor acceptance."""
from pathlib import Path
import hashlib
import importlib.util
import json

ROOT=Path(__file__).resolve().parents[2]
MANIFEST=ROOT/'source-assets/production/fairytale-chest-lookdev-v001/manifests/import-chest-lookdev-v001.json'
MANIFEST_SHA='166ff2779047d93c1f84e3099421267b47c66efe7d57c6ed0c72843616f17baa'
NAMESPACE='/Game/Production/ArtTrials/EV048/v001/HeroChestIdle'
DISK=ROOT/'UnrealGame/Content/Production/ArtTrials/EV048/v001/HeroChestIdle'
BASE=ROOT/'source-assets/production/fairytale-armor-v001/independent-idle-components-v001'
DECODER=Path(__file__).with_name('ue-import-armor-primary2-four-v001.py')
DECODER_SHA='5c667edbeb81eac54648d14ff92b8883d1b15a39a05cc3b56c17933dd29eb49a'

def require(condition,why):
    if not condition:raise ValueError(why)

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def old_packages_unchanged():
    rows=json.loads((MANIFEST.parent/'old-production869-before-import.json').read_text(encoding='utf-8'))['files']
    require(len(rows)==869,'Wrong protected package inventory')
    for row in rows:
        p=ROOT/row['path']
        require(p.stat().st_size==row['bytes'] and sha(p)==row['sha256'],'Protected package changed: '+str(p))
    return len(rows)

def imported_packages_unchanged(document):
    pointer=json.loads((MANIFEST.parent/'actual-import-receipt-ref.json').read_text(encoding='utf-8'))
    p=Path(pointer['path']);require(sha(p)==pointer['sha256'],'Native import receipt changed')
    d=json.loads(p.read_text(encoding='utf-8'))
    require(d['success'] and d['actual_count']==d['saved_count']==4 and d['manifest_sha256']==MANIFEST_SHA,'Unsuccessful actual import')
    require(len(d['assets'])==4,'Wrong imported set')
    for a,b in zip(document['assets'],d['assets']):
        p=Path(b['saved_uasset'])
        require(a['object_path']==b['object_path'] and a['source_sha256']==b['source_sha256'],'Import source binding changed')
        require(p.resolve()==(DISK/(a['name']+'.uasset')).resolve() and p.stat().st_size==b['saved_bytes'] and sha(p)==b['saved_sha256'],'Native package changed')
    require({p.name for p in DISK.iterdir() if p.is_file()}=={a['name']+'.uasset' for a in document['assets']},'Unexpected imported file')
    return 4

def preflight(require_unused=True):
    require(sha(MANIFEST)==MANIFEST_SHA and sha(DECODER)==DECODER_SHA,'Frozen manifest/decoder changed')
    d=json.loads(MANIFEST.read_text(encoding='utf-8'))
    require(d['schema']=='frozen-fairytale-chest-lookdev-four-v1' and d['frozen'] and d['asset_count']==4,'Wrong source contract')
    require(d['namespace']==NAMESPACE and d['canvas_px']==[512,512] and d['durations_ms']==[167]*4 and d['native_facing']==1 and d['loop'],'Wrong source timing/direction')
    require(d['display_pivot_px']==[256,464] and d['preview_canvas_size']==72*512/416 and not d['per_frame_resize'],'Wrong shared display registration')
    require(not d['runtime_verified'] and not d['full_motion_accepted'] and d['formal_complete_units']==0,'Import cannot grant acceptance')
    for v in d['references'].values():
        p=Path(v['path']);require(p.resolve().is_relative_to(BASE.resolve()) and p.stat().st_size==v['bytes'] and sha(p)==v['sha256'],'Source provenance changed')
    f=json.loads(Path(d['references']['frames']['path']).read_text(encoding='utf-8'))
    require(f['ok'] and not f['errors'] and not f['warnings'] and len(f['rows'])==1,'Native extraction QA failed')
    row=f['rows'][0];require(row['method']=='components' and row['frames']==4 and row['shared_row_fit']['scale']==60/271,'Shared row extraction changed')
    reg=json.loads(Path(d['references']['registration']['path']).read_text(encoding='utf-8'))
    require(not reg['registration_resampling'] and not reg['per_frame_scaling'] and not reg['repainted'],'Registration may only translate original components')
    spec=importlib.util.spec_from_file_location('chest_native_decoder',DECODER);decoder=importlib.util.module_from_spec(spec);spec.loader.exec_module(decoder)
    require([a['frame'] for a in d['assets']]==list(range(4)),'Missing/reordered components')
    for i,a in enumerate(d['assets']):
        p=Path(a['source']);name=f'T_Fairytale_ChestIdle_{i:03d}_v001'
        require(p.resolve()==(BASE/f'registration-proposed-v001/armor-front/frame-{i}.png').resolve(),'Unexpected component source')
        require(p.stat().st_size==a['source_bytes'] and sha(p)==a['source_sha256'],'Component source changed')
        require((a['name'],a['package_path'],a['object_path'])==(name,NAMESPACE+'/'+name,NAMESPACE+'/'+name+'.'+name),'Import destination changed')
        q=decoder.inspect_rgba_png(p.read_bytes())
        require(q['nonempty'] and q['corners_transparent'] and q['alpha_extrema']==[0,255] and q['bbox_px']==a['source_bbox'],'Invalid transparent component')
        require(reg['frames'][i]['cropped_RGBA_unchanged'] and reg['frames'][i]['body_input_byte_identical_to_original'] and reg['frames'][i]['nontransparent_clipped_pixels']==0,'Original pixels changed/clipped')
    require(len({a['source_sha256'] for a in d['assets']})==4,'Duplicated component poses')
    if require_unused:require(not DISK.exists() or not any(p.is_file() for p in DISK.rglob('*')),'Never replace an existing namespace')
    else:imported_packages_unchanged(d)
    old_packages_unchanged()
    return d
