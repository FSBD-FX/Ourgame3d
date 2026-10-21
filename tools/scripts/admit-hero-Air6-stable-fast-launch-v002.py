from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,shutil
R=Path('F:/Ourgame');S=R/'Playables/钟盔轻甲-v142-CM52f906';C=R/'source-assets/production/fairytale-hero-air-v001/stable-fast-launch-candidate-v002';O=R/'source-assets/production/fairytale-hero-air-v001/root-stable-fast-admission-v002'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def pin(p,local=False):
 p=Path(p).resolve();b=p.read_bytes();return dict(path=p.relative_to(S).as_posix() if local else p.as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def write(p,d):
 with p.open('x',encoding='utf-8') as f:json.dump(d,f,ensure_ascii=False,indent=2)
freeze=C/'HeroAir6-stable-fast-launch-candidate-freeze-v002.json';assert pin(freeze)['sha256']=='45d6bb7faa2f00b21fad4b04bc42f8e22aa19c0d9da2e90f30b0c9b7663e8fe7'
for n in range(2):
 for row in read(freeze)['members']:
  p=Path(row['path']);q=pin(p);assert (q['bytes'],q['sha256'])==(row['bytes'],row['sha256'])
ix=read(C/'Root-admit-index-v002.json');parent=S/ix['parent_runtime_manifest_pin']['path'];assert pin(parent,True)==ix['parent_runtime_manifest_pin'];pm=read(parent)
assert read(S/'_proof/Root-stable-approval-v001.json')['RootApproved'] is True
oldmeta=[pin(S/x['path'],True) for x in pm['metadata_files']];assert oldmeta==pm['metadata_files']
assert not O.exists();O.mkdir()
src=C/'launch-stable-preview-v002.ps1';dst=S/ix['new_staged_source'];assert not dst.exists();shutil.copy2(src,dst);assert pin(dst)['sha256']==ix['source']['sha256']
df=S/'_proof/evidence/fast-launch-candidate-freeze-v002.json';assert not df.exists();shutil.copy2(freeze,df)
manifest=dict(pm);manifest.update(parent_runtime_manifest_pin=pin(parent,True),metadata_files=pm['metadata_files']+[pin(dst,True),pin(df,True)],launcher_metadata_derivation='Append v002 fast path-query verifier only. Identical1778runtime/engine/CM and oldmetadata; native174/copy proof remains bound to actual v001 parent.',derivation_utc=datetime.now(timezone.utc).isoformat())
mp=S/ix['new_staged_manifest'];write(mp,manifest)
approval=dict(read(S/'_proof/Root-stable-approval-v001.json'));approval.update(utc=datetime.now(timezone.utc).isoformat(),runtime_manifest_pin=pin(mp,True),metadata_only_derivation=True,parent_runtime_manifest_pin=pin(parent,True),new_gate_actual_timed_validation_pending=True)
ap=S/ix['new_staged_approval'];write(ap,approval)
wrapper=Path(ix['new_Root_wrapper'])
with wrapper.open('x',encoding='utf-8') as f:f.write("param([switch]$ValidateOnly)\n& 'F:/Ourgame/Playables/钟盔轻甲-v142-CM52f906/_proof/tools/launch-stable-preview-v002.ps1' -LightArtTrial -GuardFullArt -ValidateOnly:$ValidateOnly\n")
entry=Path(ix['new_Root_alias'])
with entry.open('xb') as f:f.write(b'@echo off\r\ncd /d "%~dp0"\r\npwsh -NoProfile -ExecutionPolicy Bypass -File "%~dp0tools\\scripts\\launch-hero-stable-preview-v002.ps1"\r\npause\r\n')
assert [pin(S/x['path'],True) for x in pm['metadata_files']]==oldmeta
result=dict(schema='Root-stable-fast-launch-actual-admission-v002',utc=datetime.now(timezone.utc).isoformat(),actual_applied=True,candidate_freeze=pin(freeze),new_launcher=pin(dst),new_runtime_manifest=pin(mp),new_approval=pin(ap),wrapper=pin(wrapper),entry=pin(entry),original_parent_unchanged=pin(parent),original_copy_native_proofs_unchanged=True,original_runtime_files_changed=False,old_metadata_files_changed=False,actual_fast_validation_pending=True,FinalAccepted=False)
write(O/'actual-fast-launch-admission-v002.json',result);print(json.dumps(result,ensure_ascii=False))
