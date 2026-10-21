from pathlib import Path
import json,hashlib
R=Path('F:/Ourgame');D=R/'source-assets/production/fairytale-lgt-readability-v003';A=D/'primary1-integer-assembly-v002';O=D/'primary1-import-v001';assert not O.exists();O.mkdir()
def pin(p):
 b=p.read_bytes();return dict(path=p.as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,x):assert not p.exists();p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
f=A/'delivery-freeze-v002.json';assert pin(f)['sha256']=='d97d35bebcf85d3f054377262912c1319a933cd8f325d622e579cb27978b5257'
for row in read(f)['files']:
 p=Path(row['path']);p=p if p.is_absolute() else A/p;d=pin(p);assert (d['bytes'],d['sha256'])==(row['bytes'],row['sha256'])
c=A/'candidate-import-v013-v002.json';assert pin(c)['sha256']=='22ebecabdbe08d8bc3f52d543700fecf472388be693e4e8e03db7a6cd68db99b';v=read(c)
review=O/'root-static-fit-approval-v001.json';write(review,dict(candidate=pin(c),delivery_freeze=pin(f),Root_viewed_all12_after_E297=True,Root_viewed_actual_Body159v003_and24layers_after_E296=True,scope='Eligible for optional native Primary1 fit trial only, no complete animation or human final art acceptance',review='Chest/shoulders stay on current body in the twelve static no-sword composites. Helmet/amber eyes and near hand remain visible; no alternate human head. Narrow far tab intentionally occludes behind torso. Doubled old belt remnants and new cloak-to-Ready seam still need actual motion review.',fit_eligible_for_native_trial_only=True,semantic_whole_motion_accepted=False,full_unit_complete=False,body_max_px=72,weapon_scale=.5,formal_complete_units=0))
base=R/'source-assets/production/backups/2026-10-17_LeatherReady12-GuardCoin-full154GREEN-v124/compiled-source-manifest.json';old=[r for r in read(base)['files'] if r['path'].startswith('UnrealGame/Content/Production/')];assert len(old)==1097
for r in old:
 p=R/r['path'];d=pin(p);assert (d['bytes'],d['sha256'])==(r['bytes'],r['sha256'])
inventory=O/'old-production1097-before-import.json';write(inventory,dict(files=old,base_manifest=pin(base)))
v.update(schema='frozen-leather-primary1-18-v1',fit_accepted=False,fit_eligible_for_native_trial_only=True,import_permitted=True,Root_static_review_required=False,full_motion_accepted=False)
v['references'].update(root_static_review=pin(review),old_production=pin(inventory),original_candidate=pin(c));manifest=O/'import-leather-primary1-v001.json';write(manifest,v)
tools=R/'tools/scripts'
checks=(tools/'ue_leather_ready_v001_checks.py').read_text(encoding='utf-8')
for a,b in [('ready-import-v001/import-leather-ready-v001.json','primary1-import-v001/import-leather-primary1-v001.json'),('f6c8a947158c1f957cc77ad5412362a2c1cadb0acc18685e85278033936d6b36',pin(manifest)['sha256']),('v012/HeroLeatherReady','v013/HeroLeatherPrimary1'),('1085','1097'),('12','18'),('frozen-leather-ready-18-v1','frozen-leather-primary1-18-v1'),('T_Fairytale_LeatherReady','T_Fairytale_LeatherPrimary1'),('range(4)','range(6)'),("d['frame_seconds']==.167","d['durations_ms']==[85,85,60,60,155,155]")]:
 assert a in checks,(a,'checks');checks=checks.replace(a,b)
cp=tools/'ue_leather_primary1_v001_checks.py';assert not cp.exists();cp.write_text(checks,encoding='utf-8')
s=(tools/'ue-import-leather-ready-v001.py').read_text(encoding='utf-8')
for a,b in [('ue_leather_ready_v001_checks.py','ue_leather_primary1_v001_checks.py'),('12','18'),('1085','1097'),('leather-ready','leather-primary1'),('Leather Ready18','Leather Primary1-18'),('Ready4 opt-in','Primary1 six-phase opt-in')]:
 assert a in s,(a,'import');s=s.replace(a,b)
needle='"scope":"';assert needle in s;s=s.replace(needle,'"assembly_freeze":document["references"]["assembly_freeze"],\n    '+needle)
ip=tools/'ue-import-leather-primary1-v001.py';assert not ip.exists();ip.write_text(s,encoding='utf-8')
ps=(tools/'import-leather-ready-v001.ps1').read_text(encoding='utf-8-sig')
for a,b in [('leather-ready','leather-primary1'),('12','18'),('1085','1097')]:assert a in ps;ps=ps.replace(a,b)
pp=tools/'import-leather-primary1-v001.ps1';assert not pp.exists();pp.write_text(ps,encoding='utf-8')
write(O/'import-tool-freeze-v001.json',dict(files=[pin(manifest),pin(review),pin(inventory),pin(cp),pin(ip),pin(pp)],actual_imported=False,full_animation_accepted=False))
print(json.dumps(dict(manifest=pin(manifest),review=pin(review),checks=pin(cp),importer=pin(ip),old_packages=1097,new_Texture2D_expected=18),ensure_ascii=False))
