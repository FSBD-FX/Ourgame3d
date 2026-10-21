from pathlib import Path
import hashlib,json
R=Path('F:/Ourgame');S=R/'source-assets/production/backups/2026-10-16_PristineBootstrap-nativeGeometry-full138GREEN-v112'
OUT=R/'docs/production/first-batch-v2/evidence/run-pristine-bootstrap-v001/actual-full138-v112-audit-v001.json'
assert not OUT.exists()
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def pin(p):
    b=p.read_bytes();return {'path':p.as_posix(),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
m=read(S/'compiled-source-manifest.json');assert len(m['files'])==1587
for row in m['files']:
    for p in [R/row['path'],S/row['path']]:
        q=pin(p);assert all(q[k]==row[k] for k in ['bytes','sha256']),p
reports=[];docs=[]
for rel,count in [('161619',1),('161755',3),('161855',138)]:
    p=R/f'UnrealGame/Saved/Automation/FirstRoom-20261016-{rel}/index.json';d=read(p)
    assert d['succeeded']==count and len(d['tests'])==count
    assert all(d[k]==0 for k in ['failed','notRun','inProcess','succeededWithWarnings'])
    assert all(t['state']=='Success' and t['errors']==0 and t['warnings']==0 for t in d['tests'])
    reports.append({'file':pin(p),'succeeded':count,'errors':0,'warnings':0,'notRun':0,'inProcess':0});docs.append(d)
old=read(R/'UnrealGame/Saved/Automation/FirstRoom-20261016-142409/index.json')
oldnames={t['fullTestPath'] for t in old['tests']};names={t['fullTestPath'] for t in docs[-1]['tests']}
assert len(oldnames)==134 and len(names)==138 and not oldnames-names
newnames={t['fullTestPath'] for d in docs[:2] for t in d['tests']};assert names-oldnames==newnames
red=read(R/'UnrealGame/Saved/Automation/FirstRoom-20261016-160830/index.json')
assert red['failed']==1 and red['succeeded']==0 and red['tests'][0]['errors']==4 and red['tests'][0]['warnings']==0
rb=[e['event']['message'] for e in red['tests'][0]['entries'] if e['event']['message'].startswith('NativeGeometryReadback')]
assert len(rb)==5
assert all('rawBodyValid=0' in s and 'physicsStateCreated=1' in s and 'rawBodySetup=None' in s for s in rb if 'componentClass=/Script/GameplayDebugger.GameplayDebuggerRenderingComponent' in s)
assert all('rawBodyValid=1' in s for s in rb if 'componentClass=/Script/Engine.BoxComponent' in s)
assert '[int]$ExpectedTests = 134' in (R/'tools/scripts/test-first-room.ps1').read_text(encoding='utf-8-sig')
o={'snapshot_manifest':pin(S/'compiled-source-manifest.json'),'files':1587,'endpoint_checks':3174,'differences':0,
   'actual_reports':reports,'original134_names_preserved':True,'new4_names':sorted(newnames),
   'actual_RED':{'report':'FirstRoom-20261016-160830','failed':1,'errors':4,'warnings':0,'readbacks':rb},
   'current_default_runner_before_update':134,'actual_full_command_expected_count':138,
   'actual_two_process_Continue':False,'full_D13':False,'formal_complete_units':0,'goal_status':'active'}
OUT.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'audit':pin(OUT),'endpoint_checks':3174,'differences':0,'actual_full':138,'old_names_preserved':134,'formal_complete_units':0},ensure_ascii=False))
