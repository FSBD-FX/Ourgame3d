from pathlib import Path
import hashlib,json
R=Path('F:/Ourgame');S=R/'source-assets/production/backups/2026-10-16_RunTwoProcessProbe-admitted-full138GREEN-v113'
O=R/'docs/production/first-batch-v2/evidence/run-pristine-bootstrap-v001/actual-two-process-v113-audit-v001.json';assert not O.exists()
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def pin(p):
    b=p.read_bytes();return {'path':p.as_posix(),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
m=read(S/'compiled-source-manifest.json');assert len(m['files'])==1589
for row in m['files']:
    for p in [R/row['path'],S/row['path']]:
        assert all(pin(p)[k]==row[k] for k in ['bytes','sha256']),p
session=R/'UnrealGame/Saved/RunPristineProofs/20261016-163507-native-two-process-v002'
p=read(session/'two-process-session.json');assert p['status'].startswith('two_real_processes_run_only_passed') and p['sources_unchanged']
module='UnrealGame/Binaries/Win64/UnrealEditor-CodexDungeon.dll'
modulepin=next(r for r in m['files'] if r['path']==module)
assert modulepin['sha256']==p['module_sha256_before']==p['module_sha256_after']
sourcepins=[r for r in m['files'] if r['path'].startswith('UnrealGame/Source/CodexDungeon/')]
assert len(sourcepins)==len(p['source_sha256_before'])==len(p['source_sha256_after'])
for row in sourcepins:
    key=row['path'].replace('/','\\');assert p['source_sha256_before'][key]==p['source_sha256_after'][key]==row['sha256']
report=read(R/'UnrealGame/Saved/Automation/FirstRoom-20261016-162940/index.json')
assert report['succeeded']==138 and len(report['tests'])==138 and all(report[k]==0 for k in ['failed','succeededWithWarnings','notRun','inProcess'])
assert all(t['state']=='Success' and t['errors']==0 and t['warnings']==0 for t in report['tests'])
previous=read(R/'UnrealGame/Saved/Automation/FirstRoom-20261016-161855/index.json')
assert {t['fullTestPath'] for t in previous['tests']}=={t['fullTestPath'] for t in report['tests']}
assert '[int]$ExpectedTests = 138' in (R/'tools/scripts/test-first-room.ps1').read_text(encoding='utf-8-sig')
receipt=read(session/'two-process-verification-v001.json');assert receipt['passed'] and receipt['source_pid']==44460 and receipt['restore_pid']==52000
out={'files':1589,'endpoint_checks':3178,'differences':0,'source_pins':len(sourcepins),'compiled_source_and_DLL_match_actual_two_processes':True,
    'full138_report':pin(R/'UnrealGame/Saved/Automation/FirstRoom-20261016-162940/index.json'),
    'two_process_session':pin(session/'two-process-session.json'),'receipt':pin(session/'two-process-verification-v001.json'),
    'default_runner':138,'Scope':'BoundDevelopmentRunV1 only, full D13 / visual / device audio / menu pending','formal_complete_units':0}
O.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'audit':pin(O),'endpoint_checks':3178,'differences':0,'source_pins':len(sourcepins),'actual_two_processes':True},ensure_ascii=False))
