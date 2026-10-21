from pathlib import Path
import hashlib,json,os,shutil,subprocess
R=Path('F:/Ourgame');out=R/'docs/production/first-batch-v2/evidence/guard-art-v001/root-wake-production-fix-v007';assert not out.exists();out.mkdir()
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def pin(p):return dict(path=p.relative_to(R).as_posix(),bytes=p.stat().st_size,sha256=sha(p))
report=R/'UnrealGame/Saved/Automation/FirstRoom-20261018-114243/index.json';r=read(report);assert len(r['tests'])==1 and r['tests'][0]['state']=='Fail' and r['tests'][0]['errors']==1 and r['tests'][0]['warnings']==0
messages=[e['event'] for e in r['tests'][0]['entries']];errors=[e['message'] for e in messages if e['type']=='Error']
assert len(errors)==1 and 'Actual legal replanned interval must be accepted' in errors[0]
assert any('LEGAL REPLANNED REJECTION' in e['message'] and 'actualNativeInside=1' in e['message'] for e in messages)
build=R/'UnrealGame/Saved/Bootstrap/last-build.json';b=read(build);assert b['ExitCode']==0
test=R/'UnrealGame/Source/CodexDungeon/Tests/DungeonGuardWakeEntryRoundingV003Tests.cpp';assert sha(test)=='d2b662c1eb18287122e7d76e8f83a8981b6bce1d26f888db188d71ed2eb7bebf'
files=sorted(p for p in (R/'UnrealGame/Source').rglob('*') if p.is_file());assert len(files)==223
files += [report,build,Path(b['Log']),R/'UnrealGame/Binaries/Win64/UnrealEditor-CodexDungeon.dll',Path(__file__)]
rows=[]
for p in files:
 row=pin(p);d=out/'actual-semantic-RED/files'/row['path'];d.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,d);rows.append(row)
for repeat in range(2):
 for row in rows:
  p=R/row['path'];d=out/'actual-semantic-RED/files'/row['path'];assert pin(p)==row and d.stat().st_size==row['bytes'] and sha(d)==row['sha256']
(out/'actual-semantic-RED/manifest.json').write_text(json.dumps(dict(status='ACTUAL_NATIVE_LEGAL_INTERVAL_REJECTED_TARGET_SEMANTIC_RED',errors=errors,driver_fix_applied=False,files=rows,verification_passes=2),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
admissions=[]
for folder,freeze_name,expected_sha,source_name in [
 ('presentation-observer-fix-candidate-v007','wake-driver-open-slice-fix-freeze-v007.json','c8b45b620bb12e20bfe9e9f7a1c3f77814c420f70e9c8f84c07f96a35a252bf0','DungeonStoneGuardDriver.cpp'),
 ('presentation-observer-failfast-candidate-v004','observer-failfast-freeze-v004.json','f3450800d6986688e29bd1b3a0ca0ee53b5a2deec635b06dbeb131441e368d9d','DungeonGuardArtPartialProbe.cpp')]:
 C=R/'source-assets/production/fairytale-guard-v001'/folder;freeze=C/freeze_name;assert sha(freeze)==expected_sha
 frozen=read(freeze)['files'];patches=[]
 for row in frozen:
  p=C/row['path'];assert p.stat().st_size==row['bytes'] and sha(p)==row['sha256']
  if p.suffix=='.patch':patches.append(p)
 assert len(patches)==1
 source=R/'UnrealGame/Source/CodexDungeon'/source_name;before=pin(source)
 patch=patches[0]
 for mode in ['--check',None]:
  args=['git','apply']+([mode] if mode else [])+[str(patch)];result=subprocess.run(args,cwd=R,capture_output=True,text=True,encoding='utf-8');(out/(source_name+('-check.log' if mode else '-apply.log'))).write_text(result.stdout+result.stderr,encoding='utf-8');assert result.returncode==0
 os.utime(source,None);admissions.append(dict(source=source_name,before=before,after=pin(source),candidate_freeze=pin(freeze),patch=pin(patch)))
assert sha(test)=='d2b662c1eb18287122e7d76e8f83a8981b6bce1d26f888db188d71ed2eb7bebf'
(out/'admission.json').write_text(json.dumps(dict(status='ACTUAL_SEMANTIC_RED_RETAINED_MINIMAL_DRIVER_FIX_AND_SEPARATE_OBSERVER_FAILFAST_ADMITTED',admissions=admissions,same_native_regression_unchanged=pin(test),expected_registry=181,source_files=223,production_files=1226,formal_complete_units=0),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(driver_fixed=True,observer_failfast=True,test_unchanged=True,source_files=223,actual_semantic_RED_preserved=True)))
