"""Freeze this small NEW candidate and exactly its required read-only inputs."""
from pathlib import Path
from datetime import datetime,timezone
import ast,hashlib,json
HERE=Path(__file__).resolve().parent
output=HERE/'ReadyPrimary1Bridge258-entry-tooling-freeze-v001.json'
assert not output.exists()
def pin(path):
 path=path.resolve();b=path.read_bytes();return dict(path=path.as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def check(row):
 p=Path(row['path']);a=pin(p);assert (a['bytes'],a['sha256'])==(row['bytes'],row['sha256']),str(p)
for p in HERE.glob('*.py'):ast.parse(p.read_text(encoding='utf-8-sig'))
green=json.loads((HERE/'reports/host-final-GREEN-v001.json').read_text());assert green['actual_exit_code']==green['failures']==0 and green['tests']==12
assert json.loads((HERE/'reports/PowerShell-parser-v001.json').read_text())['errors']==0
rows=list(json.loads((HERE/'required-pins-v001.json').read_text())['pins'].values())+[x['source'] for x in json.loads((HERE/'ready-entry-source-contract-v001.json').read_text())['sources']]
deps={Path(x['path']).resolve():x for x in rows if not Path(x['path']).resolve().is_relative_to(HERE)}
members=[pin(p) for p in sorted(HERE.rglob('*')) if p.is_file() and '__pycache__' not in p.parts]
for _ in range(2):
 for row in members+list(deps.values()):check(row)
value=dict(schema='request258-ready-entry-zero-Cpp-tooling-freeze-v001',created_utc=datetime.now(timezone.utc).isoformat(),members=members,dependency_pins=list(deps.values()),member_count=len(members),dependency_pin_count=len(deps),verification_passes=2,twoSHA_mismatches=0,
 host_tests=12,host_failures=0,PowerShell_parse_errors=0,new_current_dynamic_CM_AD_preflight='PENDING_Root_after_residency',
 live_DLL_or_mutable_Source_dependency_pinned=False,CM_AD_are_mandatory_dynamic_inputs=True,source_PNG_count=67,
 actual_Source_Content_tools_E_status_mutations=0,UE_runs=0,media_generated_or_viewed=0,GPU_source_readback='OPEN',MainMix='OPEN',isolated_J1_to_Ready='OPEN_full_chain_intervenes',new_native_verified=False,formal_complete_units=0,FinalAccepted=False)
with output.open('x',encoding='utf-8') as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps(pin(output)));print('members',len(members),'dependencies',len(deps))
