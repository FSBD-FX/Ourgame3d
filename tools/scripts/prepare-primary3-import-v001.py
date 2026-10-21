from pathlib import Path
import hashlib,json,re
R=Path('F:/Ourgame');O=R/'source-assets/production/fairytale-sword-primary3-runtime-v001'
def desc(p):
    d=p.read_bytes();return {'path':p.as_posix(),'bytes':len(d),'sha256':hashlib.sha256(d).hexdigest()}
def write(p,d):
    assert not p.exists();p.parent.mkdir(parents=True,exist_ok=True);p.write_text(d if isinstance(d,str) else json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
c=O/'candidate-import-v001.json';f=O/'delivery-freeze-v001.json';candidate=json.loads(c.read_text(encoding='utf-8'))
for pin in json.loads(f.read_text(encoding='utf-8'))['files']:assert desc(Path(pin['path']))==pin
review=O/'root-bounded-import-review-v001.json';write(review,{'candidate_SHA256':desc(c)['sha256'],'delivery_freeze_SHA256':desc(f)['sha256'],'retention':'2026-10-16-OurgameUE-primary3-armor-runtime-candidate-v239','all_six_no_sword_assemblies_actually_viewed':True,'import_permitted':True,'observed':'Same warm-metal chest and near/far cap through actual175 poses; chest appropriately mostly obscured by near sleeve2, outside cap1 turns open. No naked eye window obstruction or disconnected armor obvious in these no-sword images.','limits':'Third-body pose0 anticipation weak; fist1 close to helmet, hand overlap2, partial visibility of farcap, future blade/hand/ground clearance and72px motion remain unaccepted. PhysicalA/cloth are candidates and hidden offsets trial only. Not equipment identity/render integration or complete unit.','formal_complete_units':0})
components=['Body','BodyRest','ShoulderFar','Chest','NearArmWithoutHand','ShoulderNear','HelmetForeground','NearHand'];namespace='/Game/Production/ArtTrials/EV048/v011/HeroSwordPrimary3';assets=[]
for row in candidate['textures']:
    co=row['component'];i=row['frame'];p=Path(row['source']['path']);assert co in components and i in range(6) and desc(p)==row['source'];name=f'T_Fairytale_SwordPrimary3{co}_{i:03d}_v001'
    assets.append({'component':co,'frame':i,'source':p.as_posix(),'source_bytes':p.stat().st_size,'source_sha256':desc(p)['sha256'],'name':name,'package_path':namespace+'/'+name,'object_path':namespace+'/'+name+'.'+name})
assert len(assets)==48 and {(x['component'],x['frame']) for x in assets}=={(x,i) for x in components for i in range(6)};assets.sort(key=lambda x:(x['component'],x['frame']))
old=[]
for p in sorted((R/'UnrealGame/Content/Production').rglob('*')):
    if p.is_file():d=desc(p);d['path']=p.relative_to(R).as_posix();old.append(d)
assert len(old)==1037
scope='Native175 third finishing downcut six body phases with176Chest/177Near/178Far under true Stage2 660ms. Six whole bodies plus42 same512 integer-registered body/armor layers. PhysicalA/palms candidates and hidden cloth trials retain uncertainty. No grip/clearance/fullmotion/audio/equipment/unit acceptance.'
m=O/'manifests/import-sword-armor-primary3-v001.json';write(m,{'schema':'frozen-sword-primary3-armor-48-v1','namespace':namespace,'asset_count':48,'canvas_px':[512,512],'native_facing':1,'display_root':[256,464],'preview_canvas_size':72*512/416,'phase_durations_ms':[110,110,60,60,160,160],'source_requests':[175,176,177,178],'references':{'candidate':desc(c),'freeze':desc(f),'root_review':desc(review)},'assets':assets,'draw_stack':['BodyRest','ShoulderFar','Chest','NearArmWithoutHand','ShoulderNear','HelmetForeground','independent_sword','NearHand'],'scope':scope,'source_pixels_modified':False,'local_integer_placement_only':True,'full_motion_accepted':False,'formal_complete_units':0})
write(m.parent/'old-production1037-before-import.json',{'files':old})
checks=(R/'tools/scripts/ue_sword_armor_primary2_v001_checks.py').read_text(encoding='utf-8')
checks=checks.replace('fairytale-armor-sword-primary2-runtime-v001','fairytale-sword-primary3-runtime-v001').replace('/EV048/v010/HeroSwordPrimary2Armor','/EV048/v011/HeroSwordPrimary3').replace('primary2','primary3').replace('Primary2','Primary3')
checks=checks.replace("with_name('ue-import-armor-primary3-four-v001.py')","with_name('ue-import-armor-primary2-four-v001.py')")
checks=checks.replace('old-production995','old-production1037').replace('len(rows)==995','len(rows)==1037').replace('Prior995','Prior1037').replace('[75,75,60,60,135,135]','[110,110,60,60,160,160]').replace("['BodyRest','ShoulderFar'","['Body','BodyRest','ShoulderFar'")
checks=re.sub(r'\b42\b','48',checks).replace('Actual42','Actual48');checks=re.sub(r"MANIFEST_SHA='[0-9a-f]{64}'","MANIFEST_SHA='"+desc(m)['sha256']+"'",checks)
assert namespace in checks and "len(rows)==1037" in checks and "ue-import-armor-primary2-four-v001.py" in checks and "['Body','BodyRest'" in checks
ct=R/'tools/scripts/ue_sword_armor_primary3_v001_checks.py';compile(checks,str(ct),'exec');write(ct,checks)
imp=(R/'tools/scripts/ue-import-sword-armor-primary2-v001.py').read_text(encoding='utf-8');oldscope=imp.split('"scope":"',1)[1].split('"}',1)[0];imp=imp.replace(oldscope,scope).replace('primary2','primary3').replace('Primary2','Primary3').replace('"old_packages_unchanged":995','"old_packages_unchanged":1037');imp=re.sub(r'\b42\b','48',imp).replace('actual42','actual48')
it=R/'tools/scripts/ue-import-sword-armor-primary3-v001.py';compile(imp,str(it),'exec');write(it,imp)
ps=(R/'tools/scripts/import-sword-armor-primary2-v001.ps1').read_text(encoding='utf-8').replace('primary2','primary3').replace('995','1037').replace('42','48');pt=R/'tools/scripts/import-sword-armor-primary3-v001.ps1';write(pt,ps)
for p in [ct,it,pt]:write(O/'import-tool-version-used'/p.name,p.read_text(encoding='utf-8'))
write(O/'preimport-freeze-v001.json',{'files':[desc(p) for p in [Path(__file__).resolve(),m,m.parent/'old-production1037-before-import.json',review,ct,it,pt]],'UE_import_called':False,'formal_complete_units':0})
print(json.dumps({'manifest':desc(m),'new_assets':48,'old_packages':1037,'root_review':desc(review)},ensure_ascii=False))
