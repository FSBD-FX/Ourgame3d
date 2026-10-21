from pathlib import Path
import hashlib,json,os,re,shutil,subprocess
R=Path('F:/Ourgame');B=R/'source-assets/production/stone-guard-room-reward-v001'
O=R/'docs/production/first-batch-v2/evidence/guard-room-v001/root-production-admission-v001'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def pin(p):
 b=p.read_bytes();return dict(path=p.as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
freeze=B/'production-freeze-v001.json';v=read(freeze)
for row in v['files']:
 p=Path(row['path']);assert p.stat().st_size==row['bytes'] and pin(p)['sha256']==row['sha256'],p
test=R/'UnrealGame/Source/CodexDungeon/Tests/DungeonFirstBatchGuardRoomTests.cpp'
assert pin(test)['sha256']==v['frozen_test']['sha256']
assert not O.exists();O.mkdir(parents=True);shutil.copy2(freeze,O/freeze.name)
patch=B/'production-from-stage0-v001.patch';text=patch.read_text(encoding='utf-8-sig')
sections=['--- a/'+x for x in re.split(r'^--- a/',text,flags=re.M)[1:]]
paths=[s.splitlines()[0].removeprefix('--- a/') for s in sections];assert len(paths)==9
gmrel='UnrealGame/Source/CodexDungeon/DungeonGameMode.cpp'
filtered=''.join(s for s in sections if not s.startswith('--- a/'+gmrel+'\n'))
assert filtered.count('--- a/')==8
partial=O/'room-eight-files.patch';partial.write_text(filtered,encoding='utf-8')
check=subprocess.run(['git','apply','--check',str(partial)],cwd=R,capture_output=True,text=True,encoding='utf-8');assert check.returncode==0,(check.stdout,check.stderr)
merge_inputs=[]
for name,p in [('current',R/gmrel),('base',B/'stage0-source/DungeonGameMode.cpp'),('room',B/'production-source/DungeonGameMode.cpp')]:
 out=O/('merge-'+name+'.cpp');out.write_text(p.read_text(encoding='utf-8-sig'),encoding='utf-8');merge_inputs.append(out)
merge=subprocess.run(['git','merge-file','-p']+[str(p) for p in merge_inputs],cwd=R,capture_output=True,text=True,encoding='utf-8')
(O/'merged-GameMode.cpp').write_text(merge.stdout,encoding='utf-8')
(O/'merge-status.txt').write_text(str(merge.returncode)+'\n'+merge.stderr,encoding='utf-8')
assert merge.returncode==0,'Real merge conflicts preserved, no Room Source mutation'
for witness in ['GuardFeedback.ConfirmHit','GuardFeedback.Observe','GuardFeedbackEventId','DungeonFirstBatchGuardRoomRuntime.inl']:
 assert witness in merge.stdout,witness
for rel in paths:
 src=R/rel;dst=O/'before'/rel;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dst)
run=subprocess.run(['git','apply',str(partial)],cwd=R,capture_output=True,text=True,encoding='utf-8');assert run.returncode==0,(run.stdout,run.stderr)
(R/gmrel).write_text(merge.stdout,encoding='utf-8')
new=[]
for src in sorted((B/'new-source').iterdir()):
 if not src.is_file():continue
 dst=R/'UnrealGame/Source/CodexDungeon'/src.name
 if dst.exists():assert dst.read_bytes()==src.read_bytes(),dst
 else:shutil.copy2(src,dst);os.utime(dst,None);new.append(pin(dst))
for rel in paths:os.utime(R/rel,None)
# The independently frozen feedback v002 only makes the TObjectPtr explicit.
F=R/'source-assets/production/stone-guard-feedback-v001';vf=read(F/'production-freeze-v002.json')
for row in vf['files']:
 p=F/row['path'];assert p.stat().st_size==row['bytes'] and pin(p)['sha256']==row['sha256'],p
src=F/'production-v002-source/DungeonStoneGuardFeedbackPresentation.cpp';dst=R/'UnrealGame/Source/CodexDungeon'/src.name
shutil.copy2(dst,O/'before-feedback-v001-presentation.cpp');shutil.copy2(src,dst);os.utime(dst,None);assert dst.read_bytes()==src.read_bytes()
# Minimal world-arrival cue remains separate from traditional HUD/UI.
warning=R/'source-assets/production/stone-guard-room-warning-root-v002/world-warning.patch'
checkw=subprocess.run(['git','apply','--check',str(warning)],cwd=R,capture_output=True,text=True,encoding='utf-8');assert checkw.returncode==0,(checkw.stdout,checkw.stderr)
for n in ['DungeonHUD.h','DungeonHUD.cpp']:shutil.copy2(R/'UnrealGame/Source/CodexDungeon'/n,O/('before-warning-'+n))
runw=subprocess.run(['git','apply',str(warning)],cwd=R,capture_output=True,text=True,encoding='utf-8');assert runw.returncode==0,(runw.stdout,runw.stderr)
for n in ['DungeonHUD.h','DungeonHUD.cpp']:os.utime(R/'UnrealGame/Source/CodexDungeon'/n,None)
assert pin(test)['sha256']==v['frozen_test']['sha256']
ftest=R/'UnrealGame/Source/CodexDungeon/Tests/DungeonStoneGuardFeedbackTests.cpp'
assert pin(ftest)['sha256']=='6d94cdafeda9fa8057274cd9e73b544dca73483c020698088ceb8454a80ebbe0'
actual=[pin(p) for p in sorted((R/'UnrealGame/Source').rglob('*')) if p.is_file()]
record=dict(room_freeze=pin(freeze),three_way_GameMode_merge=True,feedback_preserved=True,feedback_v002=pin(dst),world_warning=pin(warning),new_room_sources=new,actual_Source=actual,original6_tests_unchanged=True,actual_compile=None,actual_GREEN=None)
(O/'admission.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
p=R/'docs/production/first-batch-v2/progress.json';s=read(p);s['guard_room_v001']['production']=pin(O/'admission.json');s.update(goal_status='active',ue_current_working_source_compiled=False,ue_current_working_source_verified=False,current_source_uncompiled_changes='Room production/explicit Rewards2 and GuardOwner2, preserved feedback production-v002 and visible world-warning candidate; actual UBT and unchanged original6tests pending.')
p.write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(room_existing=9,room_new=len(new),source_files=len(actual),feedback_preserved=True,warning_applied=True,compile_pending=True)))
