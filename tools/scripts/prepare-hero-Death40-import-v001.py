"""Root pin exact approved Death40 source and the unchanged current1286 packages."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json
from PIL import Image

R=Path('F:/Ourgame')
B=R/'source-assets/production/fairytale-hero-state-gap-v001/death-state-preparation-v001'
C=B/'Death40-native-ready-author-candidate-v002'
O=B/'Root-Death40-import-v001'
F=C/'native-ready-author-freeze-v002.json'
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def pin(p): return dict(path=p.as_posix(),bytes=p.stat().st_size,sha256=sha(p))
def check(x):
 p=Path(x['path']);assert p.stat().st_size==x['bytes'] and sha(p)==x['sha256'],p
assert sha(F)=='5f6506b609440d8cfda40b493b7ce9b23131b0f83aa09add333f8d8e74ef788c'
for x in read(F)['files']+read(F)['source40']: check(x)
manifest=C/'Death40-source-manifest-author-candidate-v002.json';m=read(manifest)
assert len(m['assets'])==40 and m['namespace']=='/Game/Production/ArtTrials/EV048/v019/HeroLeatherDeath'
snapshot=R/'source-assets/production/backups/v137-range187G/compiled-source-manifest.json'
old=[x for x in read(snapshot)['files'] if x['path'].startswith('UnrealGame/Content/Production/')]
assert len(old)==1286
oldset={R/x['path'] for x in old}
assert oldset=={q for q in (R/'UnrealGame/Content/Production').rglob('*') if q.is_file()}
for repeat in range(2):
 for x in old: check(dict(x,path=(R/x['path']).as_posix()))
assets=[]
for x in m['assets']:
 p=Path(x['source']);assert p.stat().st_size==x['source_bytes'] and sha(p)==x['source_sha256']
 with Image.open(p) as im:
  assert im.mode=='RGBA' and im.size==(512,512) and im.getchannel('A').getbbox()
  assert hashlib.sha256(im.tobytes()).hexdigest()==x['source_RGBA_sha256']
  assert sum(v>0 for v in im.getchannel('A').getdata())==x['source_alpha_nonzero_pixels']
 retained=x['actual_E_retained_member']; check(retained['manifest']);check(retained['file'])
 assert retained['file']['sha256']==x['source_sha256']
 saved=R/'UnrealGame/Content'/Path(x['package_path'].removeprefix('/Game/')+'.uasset')
 assert not saved.exists(),saved
 assets.append(dict(component=x['component'],frame=x['frame'],name=x['name'],source=pin(p),
  destination_path=m['namespace'],package_path=x['package_path'],object_path=x['object_path'],
  saved_path=saved.as_posix(),source_RGBA_sha256=x['source_RGBA_sha256'],
  alpha_nonzero_pixels=x['source_alpha_nonzero_pixels'],retained_E=retained['file']))
assert len({x['object_path'] for x in assets})==40
assert not (R/'UnrealGame/Content/Production/ArtTrials/EV048/v019/HeroLeatherDeath').exists()
assert not O.exists();O.mkdir(parents=True)
trial=dict(schema='ROOT_SCOPED_DEATH40_IMPORT_AND_NATIVE_TRIAL',utc=datetime.now(timezone.utc).isoformat(),
 source_freeze=pin(F),source_manifest=pin(manifest),runtime_profile=pin(C/'Death-runtime-profile-author-candidate-v002.json'),
 source_review=pin(B.parent/'Root-Death40-source-review-native-preparation-v001.json'),
 scope='SWD001 LGT001 Death5 limited native test;40 exact source layers; no art revision or gameplay change',
 source_allowed_for_limited_import=True,actual_native_render_verified=False,FinalAccepted=False,formal_complete_units=0)
trialpath=O/'Root-Death40-scoped-trial-v001.json';trialpath.write_text(json.dumps(trial,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
out=dict(schema='Root-Death40-native-import-v001',expected_old_count=1286,expected_new_count=40,
 expected_final_count=1326,namespace=m['namespace'],replace_existing=False,
 root_trial_registration=pin(trialpath),candidate_freeze=pin(F),source_manifest=pin(manifest),
 old_compiled_snapshot=pin(snapshot),old_production_files=old,assets=assets,
 runtime_verified=False,FinalAccepted=False,formal_complete_units=0)
p=O/'import-manifest.json';p.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(manifest=pin(p),old1286_unchanged_twice=True,source40_RGBA_verified=True,import_started=False)))
