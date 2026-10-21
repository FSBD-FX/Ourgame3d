"""Freeze actual292/1371/200G3R and two native gap captures without art approval."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,shutil
R=Path('F:/Ourgame');O=R/'source-assets/production/backups/v142-HeroAir6-Baseline292-200G3R-v001';assert not O.exists()
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def pin(p):return dict(path=p.relative_to(R).as_posix(),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())
source=[p for p in sorted((R/'UnrealGame/Source').rglob('*')) if p.is_file()];prod=[p for p in sorted((R/'UnrealGame/Content/Production').rglob('*')) if p.is_file()];assert len(source)==292 and len(prod)==1371
suite=R/'UnrealGame/Saved/Automation/FirstRoom-20261019-001119/index.json';q=read(suite);assert(q['succeeded'],q['failed'],q['notRun'])==(200,3,0)
for x in q['tests']:
 if x['state']!='Success':
  errors=[e['event']['message'] for e in x['entries'] if e['event']['type']=='Error'];assert len(errors)==1 and 'TARGET Stage0 RED:' in errors[0]
build=R/'UnrealGame/Saved/Bootstrap/last-build.json';b=read(build);assert b['ExitCode']==0 and Path(b['Log']).name=='build-editor-20261019-000959.log'
native=[]
for side,n in [('left',158),('right',165)]:
 M=R/f'过程图稿与视频/2026-10-19_钟盔跳跃旧渲染缺口实录_{side}_v001';rp=M/'原件/runtime-report.json';ni=M/'native-independent-verification-v001.json';au=M/'audio-independent-verification-v001.json'
 assert read(rp)['passed'] and not read(rp)['new_air_passed'] and len(read(rp)['observations'])==n and read(ni)['passed'] and read(au)['passed'];native.extend([rp,ni,au])
files=source+prod+[R/'UnrealGame/Binaries/Win64/UnrealEditor-CodexDungeon.dll',build,Path(b['Log']),suite]+native
pins=[pin(p) for p in files];O.mkdir(parents=True);copies=[]
for p in source+[R/'UnrealGame/Binaries/Win64/UnrealEditor-CodexDungeon.dll',build,Path(b['Log']),suite]:
 dst=O/'snapshot'/p.relative_to(R);dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dst);assert pin(p)['sha256']==pin(dst)['sha256'];copies.append(dict(source=pin(p),copy=pin(dst)))
for _ in range(2):
 for x in pins:assert pin(R/x['path'])==x
report=dict(schema='Root-HeroAir6-baseline-current-build-v001',utc=datetime.now(timezone.utc).isoformat(),mode='semantic_RED_with_native_gap_and_nonzero_mix',source_files=292,production_files=1371,registered_tests=203,passed=200,failed=3,notRun=0,old200_all_green=True,three_unique_expected_TARGET_RED=True,full_suite=pin(suite),build=pin(build),files=pins,copies=copies,twoSHA_mismatches=0,native_gap_fresh_both_sides=True,new_air_art_imported=False,formal_complete_units=0,completed_combinations=0)
p=O/'compiled-source-manifest.json';p.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(dict(manifest=pin(p),Source=292,Production=1371,old200_GREEN=True,target_RED=3),ensure_ascii=False))
