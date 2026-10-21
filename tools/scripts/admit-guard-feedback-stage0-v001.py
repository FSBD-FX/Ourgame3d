from pathlib import Path
import hashlib,json,os,shutil,subprocess
R=Path('F:/Ourgame');B=R/'source-assets/production/stone-guard-feedback-v001'
O=R/'docs/production/first-batch-v2/evidence/guard-room-v001/root-threeRED-v001'
F=R/'docs/production/first-batch-v2/evidence/guard-feedback-v001/root-stage0-admission-v001'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def pin(p):
 b=p.read_bytes();return dict(path=p.as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
report=R/'UnrealGame/Saved/Automation/FirstRoom-20261018-095203/index.json';r=read(report)
assert (r['failed'],r['succeeded'],r['succeededWithWarnings'],r['notRun'],r['inProcess'])==(3,0,0,0,0)
freeze=read(R/'source-assets/production/stone-guard-room-reward-v001/stage0-freeze-v001.json')
assert set(x['fullTestPath'] for x in r['tests'])==set(freeze['test_groups'])
messages=[]
for t in r['tests']:
 assert t['state']=='Fail' and t['errors']==1 and t['warnings']==0
 errors=[e['event']['message'] for e in t['entries'] if e['event']['type']=='Error']
 assert len(errors)==1 and any(m in errors[0] for m in freeze['expected_first_semantic_RED'])
 messages.append(dict(test=t['fullTestPath'],error=errors[0]))
assert not O.exists();O.mkdir(parents=True)
for p in [report,R/'UnrealGame/Saved/Bootstrap/build-editor-20261018-094921.log',R/'UnrealGame/Saved/Bootstrap/first-room-tests-20261018-095203.log']:
 shutil.copy2(p,O/p.name)
source=[]
for p in sorted((R/'UnrealGame/Source').rglob('*')):
 if p.is_file():
  target=O/'compiled-Source'/p.relative_to(R/'UnrealGame/Source');target.parent.mkdir(parents=True,exist_ok=True)
  shutil.copy2(p,target);assert p.read_bytes()==target.read_bytes();source.append(pin(p))
(O/'manifest.json').write_text(json.dumps(dict(actual_report=pin(report),three_semantic_RED=messages,compiled_source=source),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
stage=B/'stage0-freeze-v002.json';v=read(stage);assert v['registered_tests']==3
for row in v['files']:
 p=B/row['path'];assert p.stat().st_size==row['bytes'] and pin(p)['sha256']==row['sha256']
patch=B/'patches/stage0-public-interfaces.patch'
check=subprocess.run(['git','apply','--check',str(patch)],cwd=R,capture_output=True,text=True,encoding='utf-8');assert check.returncode==0,(check.stdout,check.stderr)
assert not F.exists();F.mkdir(parents=True)
for n in ['DungeonFighter.h','DungeonHUD.h']:shutil.copy2(R/'UnrealGame/Source/CodexDungeon'/n,F/('before-'+n))
run=subprocess.run(['git','apply',str(patch)],cwd=R,capture_output=True,text=True,encoding='utf-8');assert run.returncode==0,(run.stdout,run.stderr)
new=[]
for row in v['files'][:3]:
 src=B/row['path'];rel=Path(row['path']).relative_to('stage0-v002-source');dst=R/'UnrealGame/Source/CodexDungeon'/rel
 assert not dst.exists();shutil.copy2(src,dst);os.utime(dst,None);assert src.read_bytes()==dst.read_bytes();new.append(pin(dst))
for n in ['DungeonFighter.h','DungeonHUD.h']:os.utime(R/'UnrealGame/Source/CodexDungeon'/n,None)
shutil.copy2(stage,F/stage.name)
(F/'admission.json').write_text(json.dumps(dict(stage0_freeze=pin(stage),new=new,actual_compile=None,actual_RED=None),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
p=R/'docs/production/first-batch-v2/progress.json';s=read(p)
s['guard_room_v001']['actual_RED']=pin(O/'manifest.json');s['guard_feedback_v001']=dict(stage0=pin(F/'admission.json'),actual_RED=None,actual_GREEN=None,complete=False)
s.update(goal_status='active',ue_current_working_source_compiled=False,ue_current_working_source_verified=False,current_source_uncompiled_changes='Guard feedback Stage0: three frozen semantic tests and public empty journal/HUD getters; Room Stage0 actual threeRED preserved.')
p.write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(room_actual_threeRED=messages,compiled_source_preserved=len(source),feedback_new=3,feedback_changed=2,next='Compile actual feedback Stage0 then3nativeRED'),ensure_ascii=False))
