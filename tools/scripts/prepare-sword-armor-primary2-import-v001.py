"""Root-owned P2 42Texture import preparation; no Unreal invocation."""
from pathlib import Path
import argparse,hashlib,json,re
R=Path('F:/Ourgame');O=R/'source-assets/production/fairytale-armor-sword-primary2-runtime-v001'
p=argparse.ArgumentParser();p.add_argument('--candidate',required=True);p.add_argument('--freeze',required=True);p.add_argument('--root-review',required=True);a=p.parse_args()
def d(p):
 b=p.read_bytes();return dict(path=p.as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def new(p,v):
 assert not p.exists(),p;p.parent.mkdir(parents=True,exist_ok=True)
 p.write_text(v if isinstance(v,str) else json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
c=Path(a.candidate).resolve();f=Path(a.freeze).resolve();review=Path(a.root_review).resolve();assert c.is_relative_to(O) and f.is_relative_to(O) and review.is_relative_to(O)
rv=json.loads(review.read_text());assert rv['import_permitted'] is True and rv['candidate_SHA256']==d(c)['sha256'] and rv['delivery_freeze_SHA256']==d(f)['sha256'] and rv['formal_complete_units']==0
for entry in json.loads(f.read_text(encoding='utf-8-sig'))['files']:assert d(Path(entry['path']))==entry
candidate=json.loads(c.read_text(encoding='utf-8-sig'));components=['BodyRest','ShoulderFar','Chest','NearArmWithoutHand','ShoulderNear','HelmetForeground','NearHand']
namespace='/Game/Production/ArtTrials/EV048/v010/HeroSwordPrimary2Armor';assets=[]
for row in candidate['textures']:
 component=row['component'];frame=row['frame'];source=Path(row['source']['path'])
 assert component in components and frame in range(6) and d(source)==row['source']
 name=f'T_Fairytale_SwordPrimary2{component}_{frame:03d}_v001'
 assets.append(dict(component=component,frame=frame,source=source.as_posix(),source_bytes=row['source']['bytes'],source_sha256=row['source']['sha256'],name=name,package_path=namespace+'/'+name,object_path=namespace+'/'+name+'.'+name))
assert len(assets)==42 and {(x['component'],x['frame']) for x in assets}=={(c,i) for c in components for i in range(6)}
assets.sort(key=lambda x:(x['component'],x['frame']));old=[]
for q in sorted((R/'UnrealGame/Content/Production').rglob('*')):
 if q.is_file():row=d(q);row['path']=q.relative_to(R).as_posix();old.append(row)
assert len(old)==995,'Production before this import must be995'
scope='Native171 six Primary2 risingcut phases,172Chest/173Near/174Far with independently measured visible physical features and explicit cloth DESIGN/hiddenTRIAL offsets; original four-owner body pixels. Armor trial only; no fullmotion/grip/unit acceptance.'
m=O/'manifests/import-sword-armor-primary2-v001.json'
new(m,dict(schema='frozen-sword-primary2-armor-42-v1',namespace=namespace,asset_count=42,canvas_px=[512,512],native_facing=1,display_root=[256,464],preview_canvas_size=72*512/416,phase_durations_ms=[75,75,60,60,135,135],source_requests=[171,172,173,174],references=dict(candidate=d(c),freeze=d(f),root_review=d(review)),assets=assets,draw_stack=['BodyRest','ShoulderFar','Chest','NearArmWithoutHand','ShoulderNear','HelmetForeground','independent_sword','NearHand'],scope=scope,source_pixels_modified=False,local_integer_placement_only=True,full_motion_accepted=False,formal_complete_units=0))
new(m.parent/'old-production995-before-import.json',dict(files=old))
checks=(R/'tools/scripts/ue_sword_armor_primary1_v001_checks.py').read_text(encoding='utf-8-sig')
checks=checks.replace('fairytale-sword-armor-primary1-runtime-v001','fairytale-armor-sword-primary2-runtime-v001').replace('primary1','primary2').replace('Primary1','Primary2')
checks=checks.replace('/EV048/v007/HeroSwordArmorPrimary2','/EV048/v010/HeroSwordPrimary2Armor')
checks=checks.replace('old-production941','old-production995').replace('len(rows)==941','len(rows)==995').replace('Prior917 inventory wrong','Prior995 inventory wrong').replace('Actual24 not proven','Actual42 not proven')
checks=checks.replace('[85,85,60,60,155,155]','[75,75,60,60,135,135]')
checks=re.sub(r"MANIFEST_SHA='[0-9a-f]{64}'", "MANIFEST_SHA='"+d(m)['sha256']+"'",checks)
assert namespace in checks and 'len(rows)==995' in checks and '[75,75,60,60,135,135]' in checks and 'v007' not in checks
ct=R/'tools/scripts/ue_sword_armor_primary2_v001_checks.py';compile(checks,str(ct),'exec');new(ct,checks)
importer=(R/'tools/scripts/ue-import-sword-armor-primary1-v001.py').read_text(encoding='utf-8-sig')
old_scope=importer.split('"scope":"',1)[1].split('"}',1)[0]
importer=importer.replace(old_scope,scope).replace('primary1','primary2').replace('Primary1','Primary2').replace('"old_packages_unchanged":941','"old_packages_unchanged":995').replace('actual ten Texture2D','actual42 Texture2D')
it=R/'tools/scripts/ue-import-sword-armor-primary2-v001.py';compile(importer,str(it),'exec');new(it,importer)
ps=(R/'tools/scripts/import-sword-armor-primary1-v001.ps1').read_text(encoding='utf-8-sig').replace('primary1','primary2').replace('941','995').replace('Frozen ten-source','Frozen42-source').replace('Native ten import','Native42 import')
pt=R/'tools/scripts/import-sword-armor-primary2-v001.ps1';new(pt,ps)
for q in [ct,it,pt]:new(O/'import-tool-version-used'/q.name,q.read_text(encoding='utf-8-sig'))
new(O/'preimport-freeze-v001.json',dict(files=[d(q) for q in [Path(__file__).resolve(),ct,it,pt,m,m.parent/'old-production995-before-import.json',*sorted((O/'import-tool-version-used').iterdir())]],candidate=d(c),freeze=d(f),UE_import_called=False,formal_complete_units=0))
print(json.dumps(dict(manifest=d(m),old_packages=995,new_assets=42,preimport=d(O/'preimport-freeze-v001.json')),ensure_ascii=False))
