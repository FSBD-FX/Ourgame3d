"""Root admits independently reviewed native baseline observer after genuine RED."""
from pathlib import Path
import hashlib,json,shutil,subprocess,sys
R=Path('F:/Ourgame');C=R/'source-assets/production/fairytale-hero-air-v001/runtime-candidate-v001/observer-baseline-v001'
O=R/'docs/production/first-batch-v2/evidence/HeroAir6-v142-v001/baseline-observer-admission-v001'
CM=R/'source-assets/production/backups/v142-HeroAir6-Stage0-200G3R-v001/compiled-source-manifest.json'
def pin(p):return dict(path=p.relative_to(R).as_posix(),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())
assert pin(CM)['sha256']=='64d4eee9cca114ecd5161bf693d3091b55241370808ad2110c417984b8f5e877'
old=json.loads(CM.read_text(encoding='utf-8'));assert old['all_old200_passed'] and old['only_three_expected_target_errors']
freeze=C/'HeroAir-baseline-observer-candidate-freeze-v001.json';sha='de291c4f5ed898b9648370d1c6697f831633ccb8ac2f5310e193147c7fda9cd3';assert pin(freeze)['sha256']==sha
assert not O.exists();O.mkdir(parents=True);hud=R/'UnrealGame/Source/CodexDungeon/DungeonHUD.cpp';shutil.copy2(hud,O/'DungeonHUD.cpp.before')
r=subprocess.run([sys.executable,'-B',str(C/'root-admit-observer-v001.py'),'--admit','--freeze-sha',sha],capture_output=True,text=True,encoding='utf-8')
(O/'admission-command.log').write_text(r.stdout+r.stderr,encoding='utf-8');assert r.returncode==0,r.stderr
actual=[p for p in (R/'UnrealGame/Source').rglob('*') if p.is_file()];assert len(actual)==292
for x in old['files']:
 if x['path'].startswith('UnrealGame/Source/') and x['path']!='UnrealGame/Source/CodexDungeon/DungeonHUD.cpp':assert pin(R/x['path'])==x
receipt=dict(schema='Root-Air6-baseline-observer-admission-v001',success=True,source_before=290,source_after=292,production=1371,registered_tests=203,prior_true_semantic_RED=pin(CM),freeze=pin(freeze),HUD_before=pin(O/'DungeonHUD.cpp.before'),admitted=[pin(R/'UnrealGame/Source/CodexDungeon'/n) for n in ['DungeonHUD.cpp','DungeonHeroAirProbeV001.h','DungeonHeroAirProbeV001.cpp']],root_readonly_review='Normal Enter/E/facing/Space only; one explicitly diagnostic Knight clearance; variable pacing, actual mix origin, last callback Stop then terminal export and PNG Flush; original gap remains renderer truth. No gameplay, art or existing-test changes.',native_run=False,compiled=False,formal_complete_units=0)
p=O/'admission-receipt-v001.json';p.write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(dict(success=True,Source=292,receipt=pin(p)),ensure_ascii=False))
