"""Root pins current observer binary and genuine semantic RED before native input."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,json
R=Path('F:/Ourgame');p=argparse.ArgumentParser();p.add_argument('--side',choices=['left','right'],required=True);a=p.parse_args()
M=R/f'过程图稿与视频/2026-10-19_钟盔跳跃旧渲染缺口实录_{a.side}_v001';assert not M.exists()
def pin(p):return dict(path=p.relative_to(R).as_posix(),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())
test=R/'UnrealGame/Saved/Automation/FirstRoom-20261019-001119/index.json';q=json.loads(test.read_text(encoding='utf-8-sig'));assert (q['succeeded'],q['failed'],q['notRun'])==(200,3,0)
bad=[x for x in q['tests'] if x['state']!='Success'];assert len(bad)==3
for x in bad:
 errors=[e['event']['message'] for e in x['entries'] if e['event']['type']=='Error'];assert len(errors)==1 and 'TARGET Stage0 RED:' in errors[0] and x['fullTestPath'].startswith('CodexDungeon.Content.FairytaleSwordAirV001.')
source=[p for p in sorted((R/'UnrealGame/Source').rglob('*')) if p.is_file()];prod=[p for p in sorted((R/'UnrealGame/Content/Production').rglob('*')) if p.is_file()];assert len(source)==292 and len(prod)==1371
build=R/'UnrealGame/Saved/Bootstrap/last-build.json';b=json.loads(build.read_text(encoding='utf-8-sig'));assert b['ExitCode']==0 and Path(b['Log']).name=='build-editor-20261019-000959.log'
files=[pin(p) for p in source+prod+[R/'UnrealGame/Binaries/Win64/UnrealEditor-CodexDungeon.dll',build,Path(b['Log']),test]]
for _ in range(2):
 for x in files:assert pin(R/x['path'])==x
(M/'原件').mkdir(parents=True);(M/'展示副本').mkdir()
reg=dict(schema='Root-HeroAir6-current-renderer-gap-prereg-v001',utc=datetime.now(timezone.utc).isoformat(),side=a.side,source_files=292,production_files=1371,current_full_suite=pin(test),old200_GREEN=True,three_unique_TARGET_RED=True,files=files,twoSHA_mismatches=0,expected='Normal Enter/E/side/Space, then a second fresh Space during original landing. Current native renderer remains elevated bare Ready0/no sword or armor. This is gap evidence, not new source acceptance.',real_audio_helper=True,audio_signal_or_listening_accepted=False,explicit_Knight_public_clearance=True,player_guard_position_HP_AI_clock_writes=False,new_Air_art_imported=False,formal_complete_units=0,completed_combinations=0)
rp=M/'preregistration-v001.json';rp.write_text(json.dumps(reg,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(M/'README.md').write_text('当前旧渲染缺口诊断原生记录。Source292/Production1371；旧200GREEN＋三真正TARGET RED。正常Enter/E/朝向/Space两跳，前置Knight按明确诊断标志public ApplyCombatHit清理；不修改主角/Guard或时间。不是新Air美术通过片，不是手动整房通关或音效听感验收。完成后原件/展示副本/索引及E保全才可查看。\n',encoding='utf-8')
print(json.dumps(dict(media=M.as_posix(),preregistration=pin(rp)),ensure_ascii=False))
