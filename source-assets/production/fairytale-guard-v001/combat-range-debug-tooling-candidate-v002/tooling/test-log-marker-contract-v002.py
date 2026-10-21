"""Contract-only parser regression. No Source/archive/PNG reads or native execution."""
from pathlib import Path
import ast,hashlib,importlib.util,json
P=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('range_checker',P/'verify-combat-range-log-v001.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
valid='[2026.10.18-00.00.00:000][  1]LogTemp: Display: CombatRangeProof frame=12 sim=1.25 enabled=0 lines=0'
startup='LogInit: Command Line: -DungeonHeroHurtProofV001 -DungeonCombatRangeProof -DungeonCombatRangeDebug'
cases=[]
def accepts(name,text):
 rows=m.parse_log(text);assert rows==[dict(log_line=len(text.splitlines()),frame=12,sim=1.25,enabled=0,lines=0)];cases.append(name)
def rejects(name,text):
 try:m.parse_log(text)
 except ValueError:cases.append(name);return
 raise AssertionError(name+' unexpectedly accepted')
accepts('startup_flags_are_not_proof_rows',startup+'\n'+valid)
accepts('valid_independent_marker_still_parses',valid)
accepts('identifier_and_switch_suffixes_skipped','LogInit: -DungeonCombatRangeProof\nLogInit: NotCombatRangeProof\n'+valid)
rejects('flags_only_are_not_evidence',startup)
rejects('independent_malformed_fields_still_rejected','LogTemp: Display: CombatRangeProof frame=bad sim=1.25 enabled=0 lines=0\n'+valid)
rejects('independent_marker_missing_fields_still_rejected','LogTemp: Display: CombatRangeProof broken\n'+valid)
rejects('duplicate_true_messages_same_line_rejected',valid+' '+valid)
rejects('nonfinite_sim_still_rejected','LogTemp: Display: CombatRangeProof frame=12 sim=1e999 enabled=0 lines=0')
ast.parse((P/'verify-combat-range-log-v001.py').read_text(encoding='utf-8'))
print(json.dumps(dict(schema='combat-range-v002-parser-contract-only-check',passed=True,cases=cases,synthetic_contract_only=True,UE_started=False,UBT_started=False,Source_or_archive_written=False,PNG_decoded=False,View_used=False),ensure_ascii=False))
