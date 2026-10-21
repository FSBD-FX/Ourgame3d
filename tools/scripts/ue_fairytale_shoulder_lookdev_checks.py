"""Pinned eight actual shoulder sources; visual fit remains a separate review."""
from pathlib import Path
import hashlib,importlib.util,json
ROOT=Path(__file__).resolve().parents[2]
MANIFEST=ROOT/'source-assets/production/fairytale-shoulder-lookdev-v001/manifests/import-shoulder-lookdev-v001.json'
MANIFEST_SHA='22afad834a1e23f0cf5452221b17fb4ceda89dc3c98a51c46650f217cc0063bd'
NAMESPACE='/Game/Production/ArtTrials/EV048/v001/HeroShoulderIdle'
DISK=ROOT/'UnrealGame/Content/Production/ArtTrials/EV048/v001/HeroShoulderIdle'
DECODER=Path(__file__).with_name('ue-import-armor-primary2-four-v001.py')
DECODER_SHA='5c667edbeb81eac54648d14ff92b8883d1b15a39a05cc3b56c17933dd29eb49a'
def require(v,why):
 if not v:raise ValueError(why)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def old_packages_unchanged():
 rows=json.loads((MANIFEST.parent/'old-production873-before-import.json').read_text(encoding='utf-8'))['files']
 require(len(rows)==873,'Wrong protected package inventory')
 for r in rows:
  p=ROOT/r['path'];require(p.stat().st_size==r['bytes'] and sha(p)==r['sha256'],'Protected package changed: '+str(p))
 return len(rows)
def imported_packages_unchanged(d):
 pointer=json.loads((MANIFEST.parent/'actual-import-receipt-ref.json').read_text(encoding='utf-8'))
 p=Path(pointer['path']);require(sha(p)==pointer['sha256'],'Receipt changed')
 r=json.loads(p.read_text(encoding='utf-8-sig'))
 require(r['success'] and r['actual_count']==r['saved_count']==8 and r['manifest_sha256']==MANIFEST_SHA,'Actual import did not save eight')
 require(len(r['assets'])==8,'Wrong actual imported set')
 for a,b in zip(d['assets'],r['assets']):
  p=Path(b['saved_uasset'])
  require(a['object_path']==b['object_path'] and a['source_sha256']==b['source_sha256'],'Source binding changed')
  require(p.resolve()==(DISK/(a['name']+'.uasset')).resolve() and p.stat().st_size==b['saved_bytes'] and sha(p)==b['saved_sha256'],'Package changed')
 require({p.name for p in DISK.iterdir() if p.is_file()}=={r['name']+'.uasset' for r in d['assets']},'Unexpected disk set')
 return 8
def preflight(require_unused=True):
 require(sha(MANIFEST)==MANIFEST_SHA and sha(DECODER)==DECODER_SHA,'Frozen manifest/decoder changed')
 d=json.loads(MANIFEST.read_text(encoding='utf-8'))
 require(d['schema']=='frozen-fairytale-shoulder-lookdev-eight-v1' and d['frozen'] and d['asset_count']==8,'Wrong eight-source contract')
 require(d['namespace']==NAMESPACE and d['canvas_px']==[512,512] and d['durations_ms']==[167]*4 and d['native_facing']==1,'Timing/canvas/facing changed')
 require(d['display_pivot_px']==[256,464] and d['preview_canvas_size']==72*512/416 and not d['per_frame_resize'],'Display registration changed')
 require(not d['runtime_verified'] and not d['full_motion_accepted'] and not d['semantic_masks_exist'] and d['formal_complete_units']==0,'Source freeze cannot grant acceptance')
 for r in d['references'].values():
  p=Path(r['path']);require(p.resolve().is_relative_to(ROOT) and p.stat().st_size==r['bytes'] and sha(p)==r['sha256'],'Provenance changed')
 s=importlib.util.spec_from_file_location('shoulder_native_decoder',DECODER);decoder=importlib.util.module_from_spec(s);s.loader.exec_module(decoder)
 require([(r['side'],r['frame']) for r in d['assets']]==[(side,i) for side in ('Near','Far') for i in range(4)],'Exact native source order changed')
 for r in d['assets']:
  p=Path(r['source']);name=f'T_Fairytale_Shoulder{r["side"]}Idle_{r["frame"]:03d}_v001'
  require(p.stat().st_size==r['source_bytes'] and sha(p)==r['source_sha256'],'Component changed')
  require((r['name'],r['package_path'],r['object_path'])==(name,NAMESPACE+'/'+name,NAMESPACE+'/'+name+'.'+name),'Destination changed')
  q=decoder.inspect_rgba_png(p.read_bytes());require(q['nonempty'] and q['corners_transparent'] and q['alpha_extrema']==[0,255] and q['bbox_px']==r['source_bbox'],'RGBA invalid')
 require(len({r['source_sha256'] for r in d['assets']})==8,'Duplicate layers')
 if require_unused:require(not DISK.exists() or not any(p.is_file() for p in DISK.rglob('*')),'Never replace namespace')
 else:imported_packages_unchanged(d)
 old_packages_unchanged();return d
