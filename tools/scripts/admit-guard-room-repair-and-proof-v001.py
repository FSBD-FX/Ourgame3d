from pathlib import Path
import hashlib,json,os,re,shutil,subprocess
R=Path('F:/Ourgame');B=R/'source-assets/production/stone-guard-feedback-v001/room-persistence-review-v001/owner-died-binding-v001'
P=R/'source-assets/production/stone-guard-room-reward-v001/room-native-proof-candidate-v001'
O=R/'docs/production/first-batch-v2/evidence/guard-room-v001/root-repair-proof-admission-v001'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def pin(p):
 b=p.read_bytes();return dict(path=p.as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
red=R/'docs/production/first-batch-v2/evidence/guard-room-v001/root-full176-174G-twoRED-v001/manifest.json'
assert read(red)['green']==174 and read(red)['red']==2
fixfreeze=B/'owner-died-binding-freeze-v001.json';fix=read(fixfreeze)
for row in fix['files']:
 p=B/row['path'];assert p.stat().st_size==row['bytes'] and pin(p)['sha256']==row['sha256'],p
proofFreeze=P/'proof-candidate-freeze-v001.json';proof=read(proofFreeze)
for row in proof['files']:
 p=Path(row['path']);assert p.stat().st_size==row['bytes'] and pin(p)['sha256']==row['sha256'],p
fixture=read(B/'fixture-admission-v002-pins.json')
for row in fixture['files']:
 p=R/row['actual_source'];assert p.stat().st_size==row['before_bytes'] and pin(p)['sha256']==row['before_sha256']
 q=Path(row['candidate']);assert q.stat().st_size==row['after_bytes'] and pin(q)['sha256']==row['after_sha256']
patches=[B/'settled-guard-died-binding.patch',B/'fixture-admission-v002.patch',P/'HUD-probe-dispatch-v001.patch']
for patch in patches:
 check=subprocess.run(['git','apply','--ignore-space-change','--check',str(patch)],cwd=R,capture_output=True,text=True,encoding='utf-8');assert check.returncode==0,(patch,check.stdout,check.stderr)
assert not O.exists();O.mkdir(parents=True)
shutil.copy2(fixfreeze,O/fixfreeze.name);shutil.copy2(proofFreeze,O/proofFreeze.name)
changed=set()
for patch in patches:
 changed.update(re.findall(r'^--- a/(.+)$',patch.read_text(encoding='utf-8-sig'),flags=re.M))
for rel in changed:
 src=R/rel;dst=O/'before'/rel;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dst)
for patch in patches:
 run=subprocess.run(['git','apply','--ignore-space-change',str(patch)],cwd=R,capture_output=True,text=True,encoding='utf-8');assert run.returncode==0,(patch,run.stdout,run.stderr)
for rel in changed:os.utime(R/rel,None)
for row in fixture['files']:
 p=R/row['actual_source'];assert p.stat().st_size==row['after_bytes'] and pin(p)['sha256']==row['after_sha256']
new=[]
for src in sorted((P/'new-source').iterdir()):
 if not src.is_file():continue
 dst=R/'UnrealGame/Source/CodexDungeon'/src.name;assert not dst.exists();shutil.copy2(src,dst);os.utime(dst,None);assert src.read_bytes()==dst.read_bytes();new.append(pin(dst))
scripts=['capture-guard-room-native-flow-v001.ps1','verify-guard-room-native-flow-v001.py','prepare-guard-room-native-media-v001.py','launch-guard-room-native-trial-v001.ps1']
for name in scripts:
 src=P/name;dst=R/'tools/scripts'/name;assert not dst.exists();shutil.copy2(src,dst);assert src.read_bytes()==dst.read_bytes();new.append(pin(dst))
record=dict(actual174G2RED=pin(red),owner_source_binding_fix=pin(fixfreeze),fixture_only_repairs=fixture,proof=pin(proofFreeze),changed=[pin(R/rel) for rel in sorted(changed)],new=new,actual_compile=None,actual176GREEN=None,native_proof=None,formal_complete_units=0)
(O/'admission.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
p=R/'docs/production/first-batch-v2/progress.json';s=read(p);s['guard_room_v001']['repair_proof_admission']=pin(O/'admission.json');s.update(goal_status='active',ue_current_working_source_compiled=False,ue_current_working_source_verified=False,current_source_uncompiled_changes='Original Died/reward exact binding (2 production files), two legal fixture repairs, opt-in normal-room native flow proof (2 newSource/HUD observation); actual UBT/176GREEN/runtime pending.')
p.write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(changed=len(changed),new_source=2,new_tools=4,registry_still176=True,fix_proved_RED=True,next='UBT then strict176 then native normal room proof')))
