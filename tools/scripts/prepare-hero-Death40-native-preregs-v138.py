"""Bind both explicit spatial-side trials to the actual fresh190/1326 build."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json
R=Path('F:/Ourgame');B=R/'source-assets/production/fairytale-hero-state-gap-v001/death-state-preparation-v001'
C=B/'Death40-native-observer-candidate-v001';O=B/'Root-Death40-native-registration-v138-v001'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def pin(p):return dict(path=p.as_posix(),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())
def check(x):
 p=Path(x['path']);assert pin(p)==x,p
f=C/'Death-native-observer-freeze-v001.json'
assert pin(f)['sha256']=='8c9715b9792d5751a8c21dc9f94f1a32cfa2bd1ed356a6a5e47449de3c355ac8'
for x in read(f)['files']:
 p=Path(x['path']);p=p if p.is_absolute() else C/p
 assert p.stat().st_size==x['bytes'] and pin(p)['sha256']==x['sha256']
sm=R/'source-assets/production/backups/v138-HeroDeath190G/compiled-source-manifest.json';m=read(sm)
assert m['strict_registered_tests']==190 and m['source_files']==257 and m['production_files']==1326 and m['source_hash_mismatches']==0
roles=read(C/'read-only-input-pins-v001.json')['inputs']
for x in roles.values():check(x)
admission=read(Path(roles['Root_source_admission']['path']))
sources=admission['new_source_files']+admission['existing_modified_files'];assert len(sources)==16
actual={x['path']:x for x in m['files']}
for x in sources:
 check(x);k=Path(x['path']).relative_to(R).as_posix();assert actual[k]['bytes']==x['bytes'] and actual[k]['sha256']==x['sha256']
assert not O.exists();O.mkdir(parents=True)
out=[]
for side,label in [(-1,'left'),(1,'right')]:
 p=read(C/'Root-Death5-prereg-TEMPLATE-NOT-APPROVED-v001.json')
 p.update(is_template=False,RootApproved=True,pre_registered_before_capture=True,registered_at_utc=datetime.now(timezone.utc).isoformat(),
  candidate_freeze_pin=pin(f),source_probe_freeze_pin=pin(C/'Death-observer-source-freeze-v001.json'),
  compiled_manifest_sha256=pin(sm)['sha256'],compiled_manifest_pin=pin(sm),expected_source_files=m['source_files'],
  expected_production_files=1326,expected_strict_registered_tests=190,approach_side=side,
  Root_scoped_trial_pin=roles['Root_scoped_trial'],actual_import_receipt_pin=roles['actual_import_receipt'],
  independent_import_receipt_pin=roles['independent_import_receipt'],
  Death40_production_candidate_freeze_pin=pin(B/'Death40-runtime-production-v001/Death40-production-freeze-v001.json'),
  Root_source_admission_pin=roles['Root_source_admission'],admitted_source_files=sources,FinalAccepted=False)
 dest=O/('hero-Death5-Root-prereg-'+label+'-v001.json')
 dest.write_text(json.dumps(p,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');out.append(pin(dest))
print(json.dumps(dict(preregs=out,strict190=True,Source=257,Production=1326,native_started=False,formal_complete_units=0)))
