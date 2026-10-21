from pathlib import Path
import hashlib,json
R=Path('F:/Ourgame');F=R/'source-assets/production/fairytale-lgt-readability-v003';B=F/'ready-integer-assembly-v001';O=F/'ready-import-v001'
assert not O.exists();O.mkdir()
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def desc(p):
 b=p.read_bytes();return dict(path=p.as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
freeze=B/'assembly-freeze-v001.json';assert desc(freeze)['sha256']=='804ec889a031fd0cffec806ce5764eb701fa4be0c20dc767b9ed797f13aaa682'
for row in read(freeze)['files']:
 p=B/row['path'];d=desc(p);assert (d['bytes'],d['sha256'])==(row['bytes'],row['sha256'])
review=dict(status='Root static trial-fit review completed, native/sword fit still pending; no human style acceptance claimed',actually_viewed=[f'right-{i}.png' for i in range(4)]+[f'left-{i}.png' for i in range(4)],retained_before_review='E:/OurGame/Knight/过程图稿与视频/2026-10-17-OurgameUE-leather-integer-fit-v278/source-size-SHA256.json',findings={'helmet_and_eye_windows':'remain fully readable in all eight static composites','neck':'dark undercollar retained below bellhelmet','near_hand':'unchanged last body layer remains visible in front of jerkin; hand/armor overlap is intended depth, sword fit pending','far_hand':'retained exposed hand; narrow far tab stays at upper shoulder','waist':'new belt sits at existing waist; pouch partly behind near hand; no obvious floating gap','silhouette':'asymmetric short near cap and narrow far tab make leather silhouette clearer than gray base'},not_accepted=['new walk/equip/hurt/death/attack armor states','sword grip and live layering','audio','formal unit completion'],formal_complete_units=0)
reviewp=O/'root-static-fit-review-v001.json';reviewp.write_text(json.dumps(review,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
snap=R/'source-assets/production/backups/2026-10-17_StoneGuardNative-Coin-full154GREEN-beforeLeather-v123/compiled-source-manifest.json'
old=[x for x in read(snap)['files'] if x['path'].startswith('UnrealGame/Content/Production/')];assert len(old)==1085
(O/'old-production1085-before-import.json').write_text(json.dumps(dict(files=old),indent=2)+'\n',encoding='utf-8')
ns='/Game/Production/ArtTrials/EV048/v012/HeroLeatherReady';assets=[]
for candidate,runtime in [('Chest','Chest'),('NearShoulder','ShoulderNear'),('FarShoulder','ShoulderFar')]:
 for i in range(4):
  p=B/'armor-layers'/candidate/f'frame-{i}.png';d=desc(p);n=f'T_Fairytale_LeatherReady{runtime}_{i:03d}_v001'
  assets.append(dict(component=runtime,frame=i,source=p.as_posix(),source_bytes=d['bytes'],source_sha256=d['sha256'],name=n,package_path=ns+'/'+n,object_path=ns+'/'+n+'.'+n))
m=O/'import-leather-ready-v001.json';m.write_text(json.dumps(dict(schema='frozen-leather-ready-12-v1',namespace=ns,asset_count=12,assets=assets,canvas_px=[512,512],display_root=[256,464],preview_canvas_size=72*512/416,frame_seconds=.167,native_facing=1,references=dict(assembly=desc(freeze),static_review=desc(reviewp)),full_motion_accepted=False,formal_complete_units=0),ensure_ascii=False,indent=2)+'\n',encoding='utf-8');mh=desc(m)['sha256']
template=(R/'tools/scripts/ue_sword_armor_ready_v001_checks.py').read_text(encoding='utf-8')
template=template.replace('fairytale-sword-armor-ready-runtime-v001/manifests/import-sword-armor-ready-v001.json','fairytale-lgt-readability-v003/ready-import-v001/import-leather-ready-v001.json').replace('337947c6995e81cd9114b95367970a72e9f443b47468298c45aca48897da2a7e',mh).replace('/EV048/v006/HeroSwordArmorReady','/EV048/v012/HeroLeatherReady').replace('old-production917-before-import.json','old-production1085-before-import.json').replace('917','1085').replace('frozen-sword-ready-armor-24-v1','frozen-leather-ready-12-v1').replace('==24','==12').replace('Actual24','Actual12').replace("['BodyRest','ShoulderFar','Chest','NearArmWithoutHand','ShoulderNear','NearHand']","['ShoulderFar','Chest','ShoulderNear']").replace('T_Fairytale_SwordReady','T_Fairytale_LeatherReady').replace('return 24','return 12')
(R/'tools/scripts/ue_leather_ready_v001_checks.py').write_text(template,encoding='utf-8',newline='\n')
importer=(R/'tools/scripts/ue-import-sword-armor-ready-v001.py').read_text(encoding='utf-8').replace('ue_sword_armor_ready_v001_checks.py','ue_leather_ready_v001_checks.py').replace('actual ten','actual12 new').replace('24','12').replace('917','1085').replace('sword-armor-ready-v001','leather-ready-v001').replace('sword-ready-armor-12-native-import-v1','leather-ready-12-native-import-v1').replace('Sword Ready12','Leather Ready12').replace('Ready4 only; visual armor candidates, not equipment IDs or attack armor fit. Far original central feature contract false; separate actual topstrap rivet trial.','Ready4 opt-in native fit trial only. Exact integer-translated new3 armor components; original common body unchanged. All other action states and complete unit remain unaccepted.')
(R/'tools/scripts/ue-import-leather-ready-v001.py').write_text(importer,encoding='utf-8',newline='\n')
wrapper=(R/'tools/scripts/import-sword-armor-ready-v001.ps1').read_text(encoding='utf-8').replace('sword-armor-ready-v001','leather-ready-v001').replace('24','12').replace('917','1085').replace('ten-source','12-source').replace('Native ten','Native12')
(R/'tools/scripts/import-leather-ready-v001.ps1').write_text(wrapper,encoding='utf-8-sig',newline='\r\n')
print(json.dumps(dict(manifest=desc(m),count=12,namespace=ns,baseline_packages=1085,actual_import_not_yet=True)))
