"""Fill a new concrete Root checkpoint request from actual187 GREEN and actual imports."""
from pathlib import Path
import json,hashlib
R=Path('F:/Ourgame');G=R/'source-assets/production/fairytale-guard-v001';H=R/'source-assets/production/fairytale-hero-state-gap-v001';C=G/'current-Hurt1286-checkpoint-tooling-candidate-v001'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def pin(p):return dict(path=p.as_posix(),bytes=p.stat().st_size,sha256=sha(p))
for f,want in [(C/'checkpoint-tooling-freeze-v001.json','a1a5f6f81b12d1113d135de0dfcd866ee94843cf76d13232693cee4d38515d5c'),(H/'hurt-native-observer-candidate-v001/Hurt-native-observer-freeze-v001.json','8100c1bd3022cdbcb4bf84e8162b4aa21198e6731fcb4c72ec120909ff37eb97')]:
 assert sha(f)==want
 for x in read(f)['files']:
  p=Path(x['path']);p=p if p.is_absolute() else f.parent/p;assert p.stat().st_size==x['bytes'] and sha(p)==x['sha256']
q=read(C/'root-templates/Root-checkpoint-input-TEMPLATE-v001.json')
q.update(is_template=False,RootApproved=True,full_suite_pin=pin(R/'UnrealGame/Saved/Automation/FirstRoom-20261018-162637/index.json'),last_build_pin=pin(R/'UnrealGame/Saved/Bootstrap/last-build.json'),DLL_pin=pin(R/'UnrealGame/Binaries/Win64/UnrealEditor-CodexDungeon.dll'),snapshot_output='source-assets/production/backups/v136-Hurt187G',checkpoint_tooling_freeze_pin=pin(C/'checkpoint-tooling-freeze-v001.json'),Hurt_production_candidate_freeze_pin=pin(H/'hurt-runtime-production-candidate-v001/Hurt-production-freeze-v001.json'),additional_admitted_candidate_freeze_pins=[pin(H/'hurt-native-observer-candidate-v001/Hurt-native-observer-freeze-v001.json')],Hurt_actual_native_import_receipt_pin=pin(R/'UnrealGame/Saved/Bootstrap/hurt32-v002-import-20261018-080500-460471.json'),Hurt_independent_twoSHA_verification_pin=pin(H/'hurt-runtime-prepared-v002/validation-runs/independent-import-verification-20261018-080516-753883.json'),additional_admitted_source_paths=['UnrealGame/Source/CodexDungeon/DungeonHeroHurtProbeV001.h','UnrealGame/Source/CodexDungeon/DungeonHeroHurtProbeV001.cpp'],additional_pinned_inputs=[pin(Path(__file__)),pin(R/'docs/production/first-batch-v2/evidence/Hurt-production-v001/independent-static-review-v001.md'),pin(R/'UnrealGame/Saved/Automation/FirstRoom-20261018-162524/index.json')])
p=G/'Root-Hurt1286-checkpoint-request-v136-v001.json';assert not p.exists();p.write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(p.as_posix())
