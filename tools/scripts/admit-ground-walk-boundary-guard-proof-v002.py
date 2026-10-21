from pathlib import Path
import hashlib,json,shutil,os,subprocess
R=Path('F:/Ourgame');B=R/'source-assets/production/fairytale-lgt-readability-v003/walk-runtime-candidate-v001'
E=R/'docs/production/first-batch-v2/evidence/ground-walk-v001';O=E/'root-boundary-repair-guard-admission-v002';RED=E/'root-original-threeGREEN-boundaryRED-v001'
assert not O.exists() and not RED.exists()
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def desc(p):
 b=p.read_bytes();return dict(path=p.relative_to(R).as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def valid(p,row):
 d=desc(p);assert (d['bytes'],d['sha256'])==(row['bytes'],row['sha256']),p
report=R/'UnrealGame/Saved/Automation/FirstRoom-20261018-090231';d=read(report/'index.json')
assert len(d['tests'])==4 and d['succeeded']==3 and d['failed']==1 and all(d[k]==0 for k in ['succeededWithWarnings','notRun','inProcess'])
for t in d['tests']:
 assert t['warnings']==0
 if '.Boundaries.' in t['fullTestPath']:
  assert t['state']=='Fail' and t['errors']==1
  assert [x['event']['message'] for x in t['entries'] if x['event']['type']=='Error']==["Expected 'Idle endpoint cannot reclassify final dodge displacement as WalkDistance' to be true."]
 else:assert t['state']=='Success' and t['errors']==0
build=R/'UnrealGame/Saved/Bootstrap/last-build.json';assert read(build)['ExitCode']==0
RED.mkdir(parents=True);rows=[]
files=[p for p in (R/'UnrealGame/Source').rglob('*') if p.is_file()]+[build,Path(read(build)['Log']),R/'UnrealGame/Binaries/Win64/UnrealEditor-CodexDungeon.dll']+[p for p in report.rglob('*') if p.is_file()]
for p in files:
 q=RED/'compiled-overlay'/p.relative_to(R);q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q);assert p.read_bytes()==q.read_bytes();rows.append(dict(desc(p),retained=q.relative_to(RED).as_posix()))
(RED/'manifest.json').write_text(json.dumps(dict(files=rows,original_three_strict_GREEN=True,additional_true_dodge_boundary_RED=True,profile_configured=False),ensure_ascii=False,indent=2),encoding='utf-8')
repair=B/'review-20261018-v001/production-repair-v002';f=read(repair/'freeze-v002.json');src=R/'UnrealGame/Source/CodexDungeon'
valid(R/f['candidate']['path'],f['candidate']);valid(src/'DungeonGameMode.cpp',f['original_production'])
guard=R/'source-assets/production/stone-guard-owner-v002/guard-two-process-candidate-v001';g=read(guard/'candidate-freeze-v001.json')
for row in g['files']:valid(guard/row['path'],row)
for row in g['base_critical_source_pins']:valid(R/row['path'],row)
patch=guard/'patches/hud-guard-process-spawn-v001.patch';subprocess.run(['git','apply','--check',str(patch)],cwd=R,check=True)
config=B/'review-20261018-v001/configured-label-test-v002/DungeonFairytaleGroundWalkConfiguredTests.cpp'
assert hashlib.sha256(config.read_bytes()).hexdigest()=='37296072e3c81ef734cb0a87b17f7b62433b03e8864afe23163bb2d8c61c195a'
test=src/'Tests/DungeonFairytaleGroundWalkTests.cpp';testbytes=test.read_bytes()
O.mkdir();before={p.relative_to(R).as_posix():desc(p) for p in (R/'UnrealGame/Source').rglob('*') if p.is_file()}
shutil.copy2(R/f['candidate']['path'],src/'DungeonGameMode.cpp');os.utime(src/'DungeonGameMode.cpp',None)
subprocess.run(['git','apply',str(patch)],cwd=R,check=True);os.utime(src/'DungeonHUD.cpp',None)
new=[]
for p,q in [(guard/'candidate-source/DungeonGuardRunContinueProbe.h',src/'DungeonGuardRunContinueProbe.h'),(guard/'candidate-source/DungeonGuardRunContinueProbe.cpp',src/'DungeonGuardRunContinueProbe.cpp'),(config,src/'Tests/DungeonFairytaleGroundWalkConfiguredTests.cpp')]:
 assert not q.exists();shutil.copy2(p,q);os.utime(q,None);assert p.read_bytes()==q.read_bytes();new.append(desc(q))
assert test.read_bytes()==testbytes
changed={rel for rel,x in before.items() if desc(R/rel)!=x}
assert changed=={'UnrealGame/Source/CodexDungeon/DungeonGameMode.cpp','UnrealGame/Source/CodexDungeon/DungeonHUD.cpp'},changed
hud=(src/'DungeonHUD.cpp').read_text(encoding='utf-8-sig');assert 'DungeonFairytaleSwordWalkTextures.inl' in hud and 'SpawnActor<ADungeonGuardRunContinueProbe>()' in hud
receipt=dict(previous_boundary_RED=desc(RED/'manifest.json'),repair_freeze=desc(repair/'freeze-v002.json'),guard_freeze=desc(guard/'candidate-freeze-v001.json'),configured_test_source=desc(config),new_source=new,changed_existing=sorted(changed),original_three_tests_unchanged=True,walk_HUD_preserved=True,profile_configured=False,actual_compile=False,registered_tests=169)
(O/'admission.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
p=R/'docs/production/first-batch-v2/progress.json';d=read(p);d.update(ue_current_working_source_compiled=False,ue_current_working_source_verified=False,actual_registered_test_count_current=169,current_source_uncompiled_changes='Walk production admitted, real threeGREEN/additional Dodge boundaryRED preserved. Interval-start repair + Guard two-process proof and configured-label test admitted; profile still pending.');d['ground_walk_v001'].update(actual_RED=desc(E/'root-threeRED-v001/manifest.json'),original_three_GREEN_and_boundary_RED=desc(RED/'manifest.json'),boundary_repair_admission=desc(O/'admission.json'));p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(dict(boundary_RED_retained=len(rows),repair_and_guard_and_config_admitted=True,existing_changed=sorted(changed),new_files=len(new),registered_tests=169)))
