"""Freeze genuine 200 GREEN + 3 expected TARGET RED before observer admission."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,shutil
R=Path('F:/Ourgame');O=R/'source-assets/production/backups/v142-HeroAir6-Stage0-200G3R-v001'
assert not O.exists()
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def pin(p):return dict(path=p.relative_to(R).as_posix(),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())
test=R/'UnrealGame/Saved/Automation/FirstRoom-20261019-000252/index.json';q=read(test)
assert(q['succeeded'],q['failed'],q['notRun'],q['inProcess'])==(200,3,0,0)
bad=[x for x in q['tests'] if x['state']!='Success'];assert len(bad)==3
for x in bad:
 errors=[e['event']['message'] for e in x['entries'] if e['event']['type']=='Error']
 assert x['fullTestPath'].startswith('CodexDungeon.Content.FairytaleSwordAirV001.') and len(errors)==1 and 'TARGET Stage0 RED:' in errors[0]
old=read(R/'source-assets/production/backups/v141-GuardMove7-Observer200G-v003/compiled-source-manifest.json')
oldtests=read(R/old['full_suite']['path'])
assert {x['fullTestPath'] for x in oldtests['tests']}=={x['fullTestPath'] for x in q['tests'] if x['state']=='Success'}
source=[p for p in sorted((R/'UnrealGame/Source').rglob('*')) if p.is_file()];assert len(source)==290
production=[p for p in sorted((R/'UnrealGame/Content/Production').rglob('*')) if p.is_file()];assert len(production)==1371
for x in old['files']:
 if x['path'].startswith('UnrealGame/Content/Production/'):
  p=R/x['path'];assert pin(p)==x
build=R/'UnrealGame/Saved/Bootstrap/last-build.json';b=read(build);assert b['ExitCode']==0 and Path(b['Log']).name=='build-editor-20261018-235703.log'
binary=R/'UnrealGame/Binaries/Win64/UnrealEditor-CodexDungeon.dll'
originals=source+[binary,build,Path(b['Log']),test]
O.mkdir(parents=True);copies=[]
for p in originals:
 dst=O/'snapshot'/p.relative_to(R);dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dst);assert pin(p)['sha256']==pin(dst)['sha256'];copies.append(dict(source=pin(p),copy=pin(dst)))
files=[pin(p) for p in originals+production]
for _ in range(2):
 for x in files:assert pin(R/x['path'])==x
report=dict(schema='Root-HeroAir6-Stage0-200G3R-v001',utc=datetime.now(timezone.utc).isoformat(),mode='semantic-RED',source_files=290,production_files=1371,registered_tests=203,passed=200,failed=3,all_old200_passed=True,only_three_expected_target_errors=True,failed_targets=bad,full_suite=pin(test),build=pin(build),files=files,copies=copies,twoSHA_mismatches=0,art_imported=False,visual_or_audio_accepted=False,formal_complete_units=0,completed_combinations=0)
p=O/'compiled-source-manifest.json';p.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(dict(success=True,Source=290,Production=1371,passed=200,expected_target_red=3,manifest=pin(p)),ensure_ascii=False))
