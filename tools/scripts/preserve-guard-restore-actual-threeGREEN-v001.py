from pathlib import Path
import json,hashlib,shutil
R=Path('F:/Ourgame');D=R/'docs/production/first-batch-v2';O=D/'evidence/stone-guard-restore-v001/root-actual-threeGREEN-v001';assert not O.exists();O.mkdir(parents=True)
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def pin(p):
 b=p.read_bytes();return dict(path=p.as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
report=R/'UnrealGame/Saved/Automation/FirstRoom-20261017-020948/index.json';v=read(report)
assert v['succeeded']==len(v['tests'])==3 and len({t['fullTestPath'] for t in v['tests']})==3
assert all(v.get(k,0)==0 for k in ['failed','succeededWithWarnings','notRun','inProcess']) and all(t['state']=='Success' and t['errors']==t['warnings']==0 for t in v['tests'])
receipt=R/'UnrealGame/Saved/Bootstrap/last-build.json';last=read(receipt);build=Path(last['Log']);assert last['ExitCode']==0 and build.name=='build-editor-20261017-020436.log'
paths=[p for p in (R/'UnrealGame/Source').rglob('*') if p.is_file()]+[R/'UnrealGame/Binaries/Win64/UnrealEditor-CodexDungeon.dll',build,report,receipt,R/'source-assets/production/stone-guard-restore-v001/production-freeze-v001.json']
rows=[]
for p in paths:
 q=O/'compiled-overlay'/p.relative_to(R);q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q);assert p.read_bytes()==q.read_bytes();rows.append(dict(source=pin(p),retained=pin(q)))
(O/'manifest.json').write_text(json.dumps(dict(actual_build_exit=0,actual_three_GREEN=True,warnings=0,full157_not_yet_run=True,files=rows,build_history_receipt=pin(O/'compiled-overlay'/receipt.relative_to(R)),formal_complete_units=0,native_owner_persistence=False),ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(dict(actual_three_GREEN_preserved=True,files=len(rows),build_history_receipt=pin(O/'compiled-overlay'/receipt.relative_to(R))),ensure_ascii=False))
