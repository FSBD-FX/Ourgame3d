"""Prepare immutable Primary1 42Texture import inputs; no Unreal invocation."""
from pathlib import Path
import argparse,hashlib,json,re
R=Path('F:/Ourgame');O=R/'source-assets/production/fairytale-sword-armor-primary1-runtime-v001'
p=argparse.ArgumentParser();p.add_argument('--candidate',required=True);p.add_argument('--freeze',required=True);a=p.parse_args()
assert not O.exists(),O
def desc(p):
 b=p.read_bytes();return {'path':p.as_posix(),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def new(p,d):
 assert not p.exists(),p
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(d if isinstance(d,str) else json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
c=Path(a.candidate).resolve();f=Path(a.freeze).resolve();assert c.is_relative_to(R) and f.is_relative_to(R)
for row in json.loads(f.read_text(encoding='utf-8-sig'))['files']:assert desc(Path(row['path']))==row
candidate=json.loads(c.read_text(encoding='utf-8-sig'));components=['BodyRest','ShoulderFar','Chest','NearArmWithoutHand','ShoulderNear','HelmetForeground','NearHand']
namespace='/Game/Production/ArtTrials/EV048/v007/HeroSwordArmorPrimary1';assets=[]
for row in candidate['textures']:
 component=row['component'];frame=row['frame'];source=Path(row['source']['path'])
 assert component in components and frame in range(6) and desc(source)==row['source']
 name=f'T_Fairytale_SwordPrimary1{component}_{frame:03d}_v001'
 assets.append({'component':component,'frame':frame,'source':source.as_posix(),'source_bytes':row['source']['bytes'],'source_sha256':row['source']['sha256'],'name':name,'package_path':namespace+'/'+name,'object_path':namespace+'/'+name+'.'+name})
assert len(assets)==42 and {(r['component'],r['frame']) for r in assets}=={(v,i) for v in components for i in range(6)}
assets.sort(key=lambda r:(r['component'],r['frame']));old=[]
for path in sorted((R/'UnrealGame/Content/Production').rglob('*')):
 if path.is_file():d=desc(path);d['path']=path.relative_to(R).as_posix();old.append(d)
assert len(old)==941,'Prior Production inventory must be exactly941'
scope='Six actual159 grounded Primary1 phases with native164Chest/165Near/167Far, explicit32x30 common far extent and design-only hidden body targets; exclusive original four-body partitions. Candidate armor only, no actual equipment ID/fullmotion/thumb/allstates acceptance.'
manifest={'schema':'frozen-sword-primary1-armor-42-v1','namespace':namespace,'asset_count':42,'canvas_px':[512,512],
 'native_facing':1,'display_root':[256,464],'preview_canvas_size':72*512/416,'phase_durations_ms':[85,85,60,60,155,155],
 'source_requests':[159,164,165,167],'references':{'candidate':desc(c),'freeze':desc(f)},'assets':assets,
 'draw_stack':['BodyRest','ShoulderFar','Chest','NearArmWithoutHand','ShoulderNear','HelmetForeground','independent_sword','NearHand'],
 'scope':scope,'source_pixels_modified':False,'local_integer_placement_only':True,'full_motion_accepted':False,'formal_complete_units':0}
m=O/'manifests/import-sword-armor-primary1-v001.json';new(m,manifest);new(m.parent/'old-production941-before-import.json',{'files':old})
# Reuse the inspected importer protocol via a distinctly pinned new tool version.
checks=(R/'tools/scripts/ue_sword_armor_ready_v001_checks.py').read_text(encoding='utf-8-sig')
replacements=[('fairytale-sword-armor-ready-runtime-v001','fairytale-sword-armor-primary1-runtime-v001'),('import-sword-armor-ready-v001.json','import-sword-armor-primary1-v001.json'),('/EV048/v006/HeroSwordArmorReady','/EV048/v007/HeroSwordArmorPrimary1'),('old-production917-before-import.json','old-production941-before-import.json'),('frozen-sword-ready-armor-24-v1','frozen-sword-primary1-armor-42-v1'),("d['frame_seconds']==.167","d['phase_durations_ms']==[85,85,60,60,155,155]"),('SwordReady','SwordPrimary1'),("'ShoulderNear','NearHand'","'ShoulderNear','HelmetForeground','NearHand'"),('range(4)','range(6)')]
for before,after in replacements:checks=checks.replace(before,after)
checks=re.sub(r'\b24\b','42',checks);checks=re.sub(r'\b917\b','941',checks)
checks=checks.replace('337947c6995e81cd9114b95367970a72e9f443b47468298c45aca48897da2a7e',desc(m)['sha256'])
assert desc(m)['sha256'] in checks and 'MANIFEST_SHA=' in checks and 'range(6)' in checks
tool=R/'tools/scripts/ue_sword_armor_primary1_v001_checks.py';compile(checks,str(tool),'exec');new(tool,checks)
importer=(R/'tools/scripts/ue-import-sword-armor-ready-v001.py').read_text(encoding='utf-8-sig')
for before,after in [('ue_sword_armor_ready_v001_checks.py','ue_sword_armor_primary1_v001_checks.py'),('sword-ready-armor-24-native-import-v1','sword-primary1-armor-42-native-import-v1'),('sword-armor-ready-v001-import-','sword-armor-primary1-v001-import-'),('Ready4 only; visual armor candidates, not equipment IDs or attack armor fit. Far original central feature contract false; separate actual topstrap rivet trial.',scope),('Sword Ready24 import receipt:','Sword Primary1-42 import receipt:')]:importer=importer.replace(before,after)
importer=re.sub(r'\b24\b','42',importer);importer=re.sub(r'\b917\b','941',importer)
it=R/'tools/scripts/ue-import-sword-armor-primary1-v001.py';compile(importer,str(it),'exec');new(it,importer)
ps=(R/'tools/scripts/import-sword-armor-ready-v001.ps1').read_text(encoding='utf-8-sig')
for before,after in [('ue-import-sword-armor-ready-v001.py','ue-import-sword-armor-primary1-v001.py'),('sword-armor-ready-v001-import-','sword-armor-primary1-v001-import-'),('old917','old941'),('sword-armor24','sword-armor42'),('saved24','saved42')]:ps=ps.replace(before,after)
ps=re.sub(r'\b24\b','42',ps);ps=re.sub(r'\b917\b','941',ps)
wrapper=R/'tools/scripts/import-sword-armor-primary1-v001.ps1';new(wrapper,ps)
for path in [tool,it,wrapper]:new(O/'import-tool-version-used'/path.name,path.read_text(encoding='utf-8-sig'))
new(O/'preimport-freeze-v001.json',{'files':[desc(x) for x in [Path(__file__),tool,it,wrapper,m,m.parent/'old-production941-before-import.json',*sorted((O/'import-tool-version-used').iterdir())]],'candidate':desc(c),'freeze':desc(f),'UE_import_called':False,'formal_complete_units':0})
print(json.dumps({'manifest':desc(m),'asset_count':42,'old_packages':941,'preimport':desc(O/'preimport-freeze-v001.json')}))
