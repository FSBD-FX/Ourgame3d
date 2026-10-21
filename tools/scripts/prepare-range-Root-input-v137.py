"""New actual checkpoint request. Old successful and failed records stay immutable."""
from pathlib import Path
from datetime import datetime, timezone
import json, hashlib
R=Path('F:/Ourgame'); G=R/'source-assets/production/fairytale-guard-v001'
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def pin(p):
 p=Path(p); return dict(path=p.as_posix(),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())
q=read(G/'Root-Hurt1286-checkpoint-request-v136-v001.json')
new_tool=G/'combat-range-debug-tooling-candidate-v002/combat-range-tooling-freeze-v002.json'
assert new_tool.is_file(), 'Wait for independent corrected tooling freeze'
q.update(full_suite_pin=pin(R/'UnrealGame/Saved/Automation/FirstRoom-20261018-170150/index.json'),last_build_pin=pin(R/'UnrealGame/Saved/Bootstrap/last-build.json'),DLL_pin=pin(R/'UnrealGame/Binaries/Win64/UnrealEditor-CodexDungeon.dll'),snapshot_output='source-assets/production/backups/v137-range187G',registration_output='source-assets/production/fairytale-guard-v001/root-Hurt1286-checkpoint-v002')
q['additional_admitted_candidate_freeze_pins'] += [pin(G/'root-combat-range-source-v001/combat-range-source-freeze-v001.json'),pin(new_tool)]
q['additional_admitted_source_paths'] += ['UnrealGame/Source/CodexDungeon/'+n for n in ['DungeonHUD.h','DungeonHUD.cpp','DungeonFairytaleGuardFullPresentationV003.cpp','DungeonFairytaleGuardPresentation.cpp']]
q['additional_admitted_source_paths']=sorted(set(q['additional_admitted_source_paths']))
q['additional_pinned_inputs']=[pin(Path(__file__)),pin(R/'docs/superpowers/plans/2026-10-18-combat-range-cleanup-and-terminal-gear.md')]
p=G/'Root-Hurt1286-checkpoint-request-v137-v001.json'; assert not p.exists(); p.write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n',encoding='utf-8'); print(p.as_posix())
