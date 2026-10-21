"""Prepare 24 immutable candidate textures; this tool does not invoke Unreal."""
from pathlib import Path
import argparse,hashlib,json
R=Path('F:/Ourgame');O=R/'source-assets/production/fairytale-sword-armor-ready-runtime-v001'
p=argparse.ArgumentParser();p.add_argument('--candidate',required=True);p.add_argument('--freeze',required=True);a=p.parse_args()
assert not O.exists(),O
def desc(p):
 b=p.read_bytes();return {'path':p.as_posix(),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def new(p,d):
 assert not p.exists(),p
 p.parent.mkdir(parents=True,exist_ok=True)
 p.write_text(d if isinstance(d,str) else json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
c=Path(a.candidate).resolve();f=Path(a.freeze).resolve()
assert c.is_relative_to(R) and f.is_relative_to(R)
frozen=json.loads(f.read_text(encoding='utf-8-sig'))
for row in frozen['files']:
 d=desc(Path(row['path']));assert d['bytes']==row['bytes'] and d['sha256']==row['sha256'],row['path']
candidate=json.loads(c.read_text(encoding='utf-8-sig'))
namespace='/Game/Production/ArtTrials/EV048/v006/HeroSwordArmorReady'
assets=[]
for row in candidate['textures']:
 component=row['component'];frame=row['frame'];source=Path(row['source']['path'])
 assert component in ['BodyRest','ShoulderFar','Chest','NearArmWithoutHand','ShoulderNear','NearHand'] and frame in range(4)
 assert desc(source)==row['source']
 name=f'T_Fairytale_SwordReady{component}_{frame:03d}_v001'
 assets.append({'component':component,'frame':frame,'source':source.as_posix(),'source_bytes':row['source']['bytes'],'source_sha256':row['source']['sha256'],'name':name,'package_path':namespace+'/'+name,'object_path':namespace+'/'+name+'.'+name})
assert len(assets)==24 and len({(r['component'],r['frame']) for r in assets})==24
assets.sort(key=lambda r:(r['component'],r['frame']))
old=[]
for path in sorted((R/'UnrealGame/Content/Production').rglob('*')):
 if path.is_file():d=desc(path);d['path']=path.relative_to(R).as_posix();old.append(d)
assert len(old)==917,'Prior production inventory must be exactly917'
manifest={'schema':'frozen-sword-ready-armor-24-v1','namespace':namespace,'asset_count':24,'canvas_px':[512,512],
 'native_facing':1,'display_root':[256,464],'preview_canvas_size':72*512/416,'frame_seconds':.167,
 'source_requests':[158,161,162,163],'references':{'candidate':desc(c),'freeze':desc(f)},'assets':assets,
 'draw_stack':['BodyRest','ShoulderFar','Chest','NearArmWithoutHand','ShoulderNear','independent_sword','NearHand'],
 'scope':'Ready4 only; visual armor candidates, not equipment IDs or attack armor fit. Far original central feature contract false; separate actual topstrap rivet trial.',
 'source_pixels_modified':False,'local_integer_placement_only':True,'full_motion_accepted':False,'formal_complete_units':0}
m=O/'manifests/import-sword-armor-ready-v001.json';new(m,manifest)
new(m.parent/'old-production917-before-import.json',{'files':old})
# New tools use distinct names and a distinct namespace. No old importer is edited.
checks='''from pathlib import Path
import hashlib,importlib.util,json
ROOT=Path(__file__).resolve().parents[2]
MANIFEST=ROOT/'source-assets/production/fairytale-sword-armor-ready-runtime-v001/manifests/import-sword-armor-ready-v001.json'
MANIFEST_SHA='__SHA__'
NAMESPACE='/Game/Production/ArtTrials/EV048/v006/HeroSwordArmorReady'
DISK=ROOT/'UnrealGame/Content/Production/ArtTrials/EV048/v006/HeroSwordArmorReady'
DECODER=Path(__file__).with_name('ue-import-armor-primary2-four-v001.py')
def require(v,why):
 if not v:raise ValueError(why)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def old_packages_unchanged():
 rows=json.loads((MANIFEST.parent/'old-production917-before-import.json').read_text(encoding='utf-8'))['files']
 require(len(rows)==917,'Prior917 inventory wrong')
 for r in rows:
  p=ROOT/r['path'];require(p.stat().st_size==r['bytes'] and sha(p)==r['sha256'],'Old package changed: '+str(p))
 return len(rows)
def imported_packages_unchanged(d):
 ptr=json.loads((MANIFEST.parent/'actual-import-receipt-ref.json').read_text(encoding='utf-8'))
 require(sha(ptr['path'])==ptr['sha256'],'Import receipt changed')
 r=json.loads(Path(ptr['path']).read_text(encoding='utf-8-sig'))
 require(r['success'] and r['actual_count']==r['saved_count']==24 and r['manifest_sha256']==MANIFEST_SHA and len(r['assets'])==24,'Actual24 not proven')
 for source,actual in zip(d['assets'],r['assets']):
  p=Path(actual['saved_uasset'])
  require(source['object_path']==actual['object_path'] and source['source_sha256']==actual['source_sha256'],'Wrong actual source')
  require(p.resolve()==(DISK/(source['name']+'.uasset')).resolve() and p.stat().st_size==actual['saved_bytes'] and sha(p)==actual['saved_sha256'],'Saved asset changed')
 require({p.name for p in DISK.iterdir() if p.is_file()}=={a['name']+'.uasset' for a in d['assets']},'Wrong namespace disk set')
 return 24
def preflight(require_unused=True):
 require(sha(MANIFEST)==MANIFEST_SHA,'Pinned manifest changed')
 require(sha(DECODER)=='5c667edbeb81eac54648d14ff92b8883d1b15a39a05cc3b56c17933dd29eb49a','Decoder changed')
 d=json.loads(MANIFEST.read_text(encoding='utf-8'))
 require(d['schema']=='frozen-sword-ready-armor-24-v1' and d['namespace']==NAMESPACE and d['asset_count']==len(d['assets'])==24,'Wrong contract')
 require(d['canvas_px']==[512,512] and d['display_root']==[256,464] and d['preview_canvas_size']==72*512/416 and d['native_facing']==1 and d['frame_seconds']==.167,'Registration changed')
 require(not d['full_motion_accepted'] and d['formal_complete_units']==0,'Source cannot grant acceptance')
 for ref in d['references'].values():
  p=Path(ref['path']);require(p.is_relative_to(ROOT) and p.stat().st_size==ref['bytes'] and sha(p)==ref['sha256'],'Candidate reference changed')
 s=importlib.util.spec_from_file_location('armor_rgba_decoder',DECODER);dec=importlib.util.module_from_spec(s);s.loader.exec_module(dec)
 require({(a['component'],a['frame']) for a in d['assets']}=={(c,i) for c in ['BodyRest','ShoulderFar','Chest','NearArmWithoutHand','ShoulderNear','NearHand'] for i in range(4)},'Wrong phase/component set')
 for a in d['assets']:
  p=Path(a['source']);name=f'T_Fairytale_SwordReady{a["component"]}_{a["frame"]:03d}_v001'
  require(p.is_relative_to(ROOT) and p.stat().st_size==a['source_bytes'] and sha(p)==a['source_sha256'],'Source changed')
  require((a['name'],a['package_path'],a['object_path'])==(name,NAMESPACE+'/'+name,NAMESPACE+'/'+name+'.'+name),'Wrong target path')
  q=dec.inspect_rgba_png(p.read_bytes());require(q['nonempty'] and q['corners_transparent'] and q['alpha_extrema']==[0,255],'Invalid source RGBA')
 if require_unused:require(not DISK.exists() or not any(p.is_file() for p in DISK.rglob('*')),'No overwrite of prior namespace')
 else:imported_packages_unchanged(d)
 old_packages_unchanged();return d
'''.replace('__SHA__',desc(m)['sha256'])
tool=R/'tools/scripts/ue_sword_armor_ready_v001_checks.py';compile(checks,str(tool),'exec');new(tool,checks)
template=(R/'tools/scripts/ue-import-fairytale-sword-body-v002.py').read_text(encoding='utf-8-sig')
for a,b in [('ue_fairytale_sword_body_v002_checks.py','ue_sword_armor_ready_v001_checks.py'),('fairytale-sword-body-ten-native-import-v2','sword-ready-armor-24-native-import-v1'),('fairytale-sword-body-v002-import-','sword-armor-ready-v001-import-'),('158Ready and159Primary1 sourcebody trial only; no complete actions/thumb/equipment acceptance',manifest['scope']),('"sources":10','"sources":24'),('"old_packages_unchanged":907','"old_packages_unchanged":917'),('"expected_count":10','"expected_count":24'),('len(registered)==10','len(registered)==24'),('Fairytale limb ten import receipt:','Sword Ready24 import receipt:')]:template=template.replace(a,b)
importer=R/'tools/scripts/ue-import-sword-armor-ready-v001.py';compile(template,str(importer),'exec');new(importer,template)
ps=(R/'tools/scripts/import-fairytale-sword-body-v002.ps1').read_text(encoding='utf-8-sig')
for a,b in [('ue-import-fairytale-sword-body-v002.py','ue-import-sword-armor-ready-v001.py'),('fairytale-sword-body-v002-import-','sword-armor-ready-v001-import-'),(' -ne 10',' -ne 24'),(' -ne 907',' -ne 917'),('limb-ten','sword-armor24'),('old907','old917'),('saved ten','saved24')]:ps=ps.replace(a,b)
wrapper=R/'tools/scripts/import-sword-armor-ready-v001.ps1';new(wrapper,ps)
for path in [tool,importer,wrapper]:new(O/'import-tool-version-used'/path.name,path.read_text(encoding='utf-8-sig'))
new(O/'preimport-freeze-v001.json',{'manifest':desc(m),'candidate':desc(c),'freeze':desc(f),'files':[desc(x) for x in [Path(__file__),tool,importer,wrapper,m,m.parent/'old-production917-before-import.json',*sorted((O/'import-tool-version-used').iterdir())]],'UE_import_called':False,'formal_complete_units':0})
print(json.dumps({'manifest':desc(m),'assets':len(assets),'old_packages':len(old),'preimport_freeze':desc(O/'preimport-freeze-v001.json')},ensure_ascii=False))
