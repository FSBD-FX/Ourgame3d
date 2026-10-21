from pathlib import Path
import datetime,hashlib,json,shutil
R=Path('F:/Ourgame');D=R/'docs/production/first-batch-v2';O=D/'evidence/stone-guard-owner-v002/root-actual-threeRED-v002';assert not O.exists()
report=R/'UnrealGame/Saved/Automation/FirstRoom-20261017-033513/index.json';d=json.loads(report.read_text(encoding='utf-8-sig'))
assert (d['succeeded'],d['failed'],d['notRun'],d['inProcess'],d['succeededWithWarnings'])==(0,3,0,0,0)
for t in d['tests']:
 assert t['state']=='Fail' and t['errors']==1 and t['warnings']==0
 errs=[e['event']['message'] for e in t['entries'] if e['event']['type']=='Error'];assert len(errs)==1 and 'Actual003 owner captures its complete supported variant (Stage0 semantic RED)' in errs[0]
build=R/'UnrealGame/Saved/Bootstrap/last-build.json';bd=json.loads(build.read_text(encoding='utf-8-sig'));assert bd['ExitCode']==0 and Path(bd['Log']).name=='build-editor-20261017-033340.log'
paths=[report,build,Path(bd['Log']),R/'UnrealGame/Saved/Bootstrap/first-room-tests-20261017-033513.log',R/'UnrealGame/Binaries/Win64/UnrealEditor-CodexDungeon.dll']
paths += [p for parent in [R/'UnrealGame/Source',R/'UnrealGame/Config',report.parent] for p in parent.rglob('*') if p.is_file()];rows=[]
for p in dict.fromkeys(paths):
 q=O/'compiled-overlay'/p.relative_to(R);q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q);b=p.read_bytes();assert b==q.read_bytes();rows.append(dict(path=p.as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest(),retained=q.relative_to(O).as_posix()))
v=dict(files=rows,actual_UE_compile_exit=0,actual_tests=3,failed=3,errors_each=1,warnings_each=0,classification='three_clean_Capture_semantic_RED_after_real_fixture',production_authorized=True,expected_capture_RED_observed=True,codec_installer_downstream_RED_observed=False)
(O/'manifest.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
p=D/'progress.json';x=json.loads(p.read_text(encoding='utf-8-sig'));x.update(ue_current_working_source_compiled=True,ue_current_working_source_verified=False,current_source_uncompiled_changes=None,updated_utc=datetime.datetime.now(datetime.timezone.utc).isoformat());x['stone_guard_owner_v002'].update(actual_RED=(O/'manifest.json').as_posix(),production_applied=False);p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(dict(preserved_files=len(rows),semantic_RED=3)))
