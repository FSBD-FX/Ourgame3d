from pathlib import Path
import json,hashlib,shutil,datetime
R=Path('F:/Ourgame');D=R/'docs/production/first-batch-v2';O=D/'evidence/stone-guard-restore-v001/root-actual-threeRED-v001';assert not O.exists();O.mkdir(parents=True)
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def desc(p):
 b=p.read_bytes();return dict(path=p.as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
report=R/'UnrealGame/Saved/Automation/FirstRoom-20261017-013106/index.json';v=read(report);assert v['succeeded']==0 and v['failed']==len(v['tests'])==3 and all(v.get(k,0)==0 for k in ['succeededWithWarnings','notRun','inProcess'])
freeze=D/'evidence/stone-guard-restore-v001/stage0-admission-freeze-v001.json';f=read(freeze);expected=set(f['expected_clean_RED_assertions'])
assert all(t['state']=='Fail' and t['errors']==1 and t['warnings']==0 and len(t['entries'])==1 for t in v['tests'])
assert {t['entries'][0]['event']['message'] for t in v['tests']}=={"Expected '"+s+"' to be true." for s in expected}
last=read(R/'UnrealGame/Saved/Bootstrap/last-build.json');build=Path(last['Log']);assert last['ExitCode']==0 and build.name=='build-editor-20261017-012801.log'
paths=[p for p in (R/'UnrealGame/Source').rglob('*') if p.is_file()]+[R/'UnrealGame/Binaries/Win64/UnrealEditor-CodexDungeon.dll',build,report,freeze]
rows=[]
for p in paths:
 q=O/'compiled-overlay'/p.relative_to(R);q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q);assert p.read_bytes()==q.read_bytes();rows.append(desc(p))
(O/'manifest.json').write_text(json.dumps(dict(actual_build_exit=0,actual_three_clean_semantic_RED=True,each_group_errors=1,warnings=0,full_suite_not_run=True,files=rows,base_full_GREEN='v124154',formal_complete_units=0),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
p=D/'progress.json';v=read(p);v['ue_current_working_source_compiled']=True;v['ue_current_working_source_verified']=False;v['current_source_uncompiled_changes']='Guard Restore Stage0 actualcompiled3 clean semanticRED preserved; production Restore pending. Historicalv124full154/manual does not bind changedSource.';v['stone_guard_restore_v001'].update(actual_UE_RED=desc(report),compiled_RED_preserved=desc(O/'manifest.json'));v['updated_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(actual_threeRED_preserved=True,files=len(rows),every_fixture_prerequisite_passed=True,production_not_yet=True)))
