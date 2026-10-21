from pathlib import Path
import hashlib,importlib.util,json
ROOT=Path(__file__).resolve().parents[2]
MANIFEST=ROOT/'source-assets/production/fairytale-lgt-readability-v003/ready-import-v001/import-leather-ready-v001.json'
MANIFEST_SHA='f6c8a947158c1f957cc77ad5412362a2c1cadb0acc18685e85278033936d6b36'
NAMESPACE='/Game/Production/ArtTrials/EV048/v012/HeroLeatherReady'
DISK=ROOT/'UnrealGame/Content/Production/ArtTrials/EV048/v012/HeroLeatherReady'
DECODER=Path(__file__).with_name('ue-import-armor-primary2-four-v001.py')
def require(v,why):
 if not v:raise ValueError(why)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def old_packages_unchanged():
 rows=json.loads((MANIFEST.parent/'old-production1085-before-import.json').read_text(encoding='utf-8'))['files']
 require(len(rows)==1085,'Prior1085 inventory wrong')
 for r in rows:
  p=ROOT/r['path'];require(p.stat().st_size==r['bytes'] and sha(p)==r['sha256'],'Old package changed: '+str(p))
 return len(rows)
def imported_packages_unchanged(d):
 ptr=json.loads((MANIFEST.parent/'actual-import-receipt-ref.json').read_text(encoding='utf-8'))
 require(sha(ptr['path'])==ptr['sha256'],'Import receipt changed')
 r=json.loads(Path(ptr['path']).read_text(encoding='utf-8-sig'))
 require(r['success'] and r['actual_count']==r['saved_count']==12 and r['manifest_sha256']==MANIFEST_SHA and len(r['assets'])==12,'Actual12 not proven')
 for source,actual in zip(d['assets'],r['assets']):
  p=Path(actual['saved_uasset'])
  require(source['object_path']==actual['object_path'] and source['source_sha256']==actual['source_sha256'],'Wrong actual source')
  require(p.resolve()==(DISK/(source['name']+'.uasset')).resolve() and p.stat().st_size==actual['saved_bytes'] and sha(p)==actual['saved_sha256'],'Saved asset changed')
 require({p.name for p in DISK.iterdir() if p.is_file()}=={a['name']+'.uasset' for a in d['assets']},'Wrong namespace disk set')
 return 12
def preflight(require_unused=True):
 require(sha(MANIFEST)==MANIFEST_SHA,'Pinned manifest changed')
 require(sha(DECODER)=='5c667edbeb81eac54648d14ff92b8883d1b15a39a05cc3b56c17933dd29eb49a','Decoder changed')
 d=json.loads(MANIFEST.read_text(encoding='utf-8'))
 require(d['schema']=='frozen-leather-ready-12-v1' and d['namespace']==NAMESPACE and d['asset_count']==len(d['assets'])==12,'Wrong contract')
 require(d['canvas_px']==[512,512] and d['display_root']==[256,464] and d['preview_canvas_size']==72*512/416 and d['native_facing']==1 and d['frame_seconds']==.167,'Registration changed')
 require(not d['full_motion_accepted'] and d['formal_complete_units']==0,'Source cannot grant acceptance')
 for ref in d['references'].values():
  p=Path(ref['path']);require(p.is_relative_to(ROOT) and p.stat().st_size==ref['bytes'] and sha(p)==ref['sha256'],'Candidate reference changed')
 s=importlib.util.spec_from_file_location('armor_rgba_decoder',DECODER);dec=importlib.util.module_from_spec(s);s.loader.exec_module(dec)
 require({(a['component'],a['frame']) for a in d['assets']}=={(c,i) for c in ['ShoulderFar','Chest','ShoulderNear'] for i in range(4)},'Wrong phase/component set')
 for a in d['assets']:
  p=Path(a['source']);name=f'T_Fairytale_LeatherReady{a["component"]}_{a["frame"]:03d}_v001'
  require(p.is_relative_to(ROOT) and p.stat().st_size==a['source_bytes'] and sha(p)==a['source_sha256'],'Source changed')
  require((a['name'],a['package_path'],a['object_path'])==(name,NAMESPACE+'/'+name,NAMESPACE+'/'+name+'.'+name),'Wrong target path')
  q=dec.inspect_rgba_png(p.read_bytes());require(q['nonempty'] and q['corners_transparent'] and q['alpha_extrema']==[0,255],'Invalid source RGBA')
 if require_unused:require(not DISK.exists() or not any(p.is_file() for p in DISK.rglob('*')),'No overwrite of prior namespace')
 else:imported_packages_unchanged(d)
 old_packages_unchanged();return d
