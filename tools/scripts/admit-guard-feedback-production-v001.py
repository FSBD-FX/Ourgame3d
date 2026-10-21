from pathlib import Path
import hashlib,json,os,shutil,subprocess
R=Path('F:/Ourgame');B=R/'source-assets/production/stone-guard-feedback-v001'
O=R/'docs/production/first-batch-v2/evidence/guard-feedback-v001/root-production-admission-v001'
def pin(p):
 b=p.read_bytes();return dict(path=p.as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
freeze=B/'production-freeze-v001.json';v=read(freeze)
for row in v['files']:
 p=B/row['path'];assert p.stat().st_size==row['bytes'] and pin(p)['sha256']==row['sha256'],p
red=R/v['Root_actual_stage0_evidence']['path'];assert pin(red)['sha256']==v['Root_actual_stage0_evidence']['sha256']
assert read(red)['three_actual_semantic_RED']
audio=read(B/'root-audio-import-v001/independent-import-verification.json');assert audio['success'] and audio['actual_count']==11 and audio['actual_total']==1210
patch=B/'patches/production-after-stage0-v002.patch'
check=subprocess.run(['git','apply','--check',str(patch)],cwd=R,capture_output=True,text=True,encoding='utf-8');assert check.returncode==0,(check.stdout,check.stderr)
assert not O.exists();O.mkdir(parents=True)
changed=['DungeonFighter.h','DungeonFighter.cpp','DungeonGameMode.h','DungeonGameMode.cpp','DungeonHUD.h','DungeonHUD.cpp']
for n in changed:shutil.copy2(R/'UnrealGame/Source/CodexDungeon'/n,O/('before-'+n))
shutil.copy2(R/'UnrealGame/Source/CodexDungeon/DungeonStoneGuardFeedback.h',O/'before-DungeonStoneGuardFeedback.h')
shutil.copy2(freeze,O/freeze.name)
run=subprocess.run(['git','apply',str(patch)],cwd=R,capture_output=True,text=True,encoding='utf-8');assert run.returncode==0,(run.stdout,run.stderr)
after=[]
for row in v['files']:
 if row['path'].startswith('production-source/'):
  src=B/row['path'];dst=R/'UnrealGame/Source/CodexDungeon'/src.name
  if not dst.exists() or src.read_bytes()!=dst.read_bytes():shutil.copy2(src,dst);os.utime(dst,None)
  assert src.read_bytes()==dst.read_bytes();after.append(pin(dst))
for n in changed:
 dst=R/'UnrealGame/Source/CodexDungeon'/n;os.utime(dst,None);after.append(pin(dst))
test=R/'UnrealGame/Source/CodexDungeon/Tests/DungeonStoneGuardFeedbackTests.cpp'
expected=read(B/'stage0-freeze-v002.json')['files'][2]
assert pin(test)['sha256']==expected['sha256'] and test.stat().st_size==expected['bytes']
(O/'admission.json').write_text(json.dumps(dict(freeze=pin(freeze),actual_RED=pin(red),audio=audio,after=after,frozen_tests_unchanged=pin(test),actual_compile=None,actual_GREEN=None,formal_complete_units=0),indent=2)+'\n',encoding='utf-8')
p=R/'docs/production/first-batch-v2/progress.json';s=read(p);s['guard_feedback_v001']['production']=pin(O/'admission.json')
s.update(goal_status='active',ue_current_working_source_compiled=False,ue_current_working_source_verified=False,ue_actual_total_production_files=1210,current_source_uncompiled_changes='Guard feedback production: journal, committed-material hook, once native HUD SoundWave requests and finite FX; pending actual compile and original threeGREEN. Room remains Stage0.')
p.write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(production_applied=True,changed=len(changed),new_presentation_cpp=1,original3tests_unchanged=True,native11SoundWaves_imported=True,compile_pending=True)))
