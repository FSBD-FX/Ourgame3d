"""Root's separately invoked bounded approval: import7, never enable runtime here."""
from pathlib import Path
from datetime import datetime, timezone
import argparse, hashlib, json, subprocess, sys
R=Path('F:/Ourgame');C=R/'source-assets/production/fairytale-guard-v001/Move7-import-candidate-v001'
P=R/'source-assets/production/fairytale-guard-v001/move-leg-rig-generation-v001/Move7-profile-preparation-v001'
def read(q):return json.loads(q.read_text(encoding='utf-8-sig'))
def pin(q):return dict(path=q.as_posix(),bytes=q.stat().st_size,sha256=hashlib.sha256(q.read_bytes()).hexdigest())
def check(x,base=R):
 q=Path(x['path']);q=q if q.is_absolute()else base/q
 assert(q.stat().st_size,hashlib.sha256(q.read_bytes()).hexdigest())==(x['bytes'],x['sha256']),q
 return q
p=argparse.ArgumentParser();p.add_argument('--approve-limited-import',action='store_true');a=p.parse_args()
assert a.approve_limited_import,'Explicit Root bounded import approval required'
freeze=C/'Move7-import-candidate-freeze-v001.json'
assert pin(freeze)['sha256']=='bd0b72ab6c32bc5506ae6e263d534dea528d7d4513c875e8c44ea2b59345b7fa'
for x in read(freeze)['files']:check(x,C)
profile=P/'GuardMove7-runtime-profile-candidate-v001.json'
assert pin(profile)['sha256']=='03156e971171f597ca504e9c0176d5a2fdf3c31c09b3eddae2995e2245193b51'
assert read(P/'host-reference-verification-v002.json')['all_checks_passed']
cm=R/'source-assets/production/backups/v140-Dodge196G/compiled-source-manifest.json'
assert pin(cm)['sha256']=='c3bae7da14020ededd624bb2bc9469f322d60ff3189dda4b9e0f865eb1fa2778'
for repeat in range(2):
 for x in read(cm)['files']:
  if x['path'].startswith('UnrealGame/Source/'):check(x)
assert len([q for q in(R/'UnrealGame/Source').rglob('*')if q.is_file()])==273
out=R/'source-assets/production/fairytale-guard-v001/Root-Move7-import-v001';assert not out.exists()
subprocess.run([sys.executable,'-B','-X','utf8',str(C/'prepare-Move7-import-v001.py'),'--old-snapshot',str(cm),'--write-prepared','--output-dir',str(out)],cwd=R,check=True)
manifest=out/'import-manifest.json';m=read(manifest);approval=read(out/'Root-limited-import-approval-TEMPLATE-v001.json')
approval.update(is_template=False,RootApproved=True,limited_import_approved=True,approval_method='Root CLI --approve-limited-import',
 utc=datetime.now(timezone.utc).isoformat(),Root_approval_tool=pin(Path(__file__)),profile_review_pin=pin(profile),
 scope='Import only seven original component sources, preserving old1364. No runtime trial or six-raster Move acceptance.',
 source_only_preflight_observed=True,old273_source_unchanged_twice=True,source7_RGBA512_and_E_members_verified=True,
 generation_calls=0,external_API_calls=0)
assert approval['manifest_pin']==pin(manifest)and m['presentation_type']=='GuardMoveSevenComponentRigDerived'
target=out/'Root-limited-import-approval-v001.json'
with target.open('x',encoding='utf-8')as f:json.dump(approval,f,ensure_ascii=False,indent=2);f.write('\n')
subprocess.run([sys.executable,'-B','-X','utf8',str(C/'ue-import-GuardMove7-v001.py'),'--manifest',str(manifest),'--root-approval',str(target),'--validate-only'],cwd=R,check=True)
print(json.dumps(dict(manifest=pin(manifest),approval=pin(target),Source=273,Production=1364,UE_started=False,RuntimeTrialAllowed=False,FinalAccepted=False)))
