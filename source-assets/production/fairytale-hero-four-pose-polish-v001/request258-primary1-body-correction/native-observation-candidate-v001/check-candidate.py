"""Stable local snapshot checks; --against-current is only for pre-admit."""
from pathlib import Path
import ast,hashlib,json,re,sys
HERE=Path(__file__).resolve().parent;sha=lambda b:hashlib.sha256(b).hexdigest();NAME='DungeonHeroLandingPriorityProbeV001.cpp'
m=json.loads((HERE/'exact-seams.json').read_text(encoding='utf-8'));before=(HERE/m['before_snapshot']).read_bytes();after=(HERE/m['projected_source']).read_bytes();assert sha(before)==m['source_sha256'] and sha(after)==m['result_sha256'];assert len(before)==m['source_bytes'] and len(after)==m['result_bytes']
if '--against-current' in sys.argv:assert Path(m['historical_actual_source']).read_bytes()==before,'Current probe drift before admit'
nl='\r\n' if m['line_ending']=='CRLF' else '\n';text=before.decode('utf-8');additions=[]
for op in m['operations']:
 a=op['before'].replace('\n',nl);b=op['after'].replace('\n',nl);assert b.endswith(a) and text.count(a)==1;text=text.replace(a,b,1);additions.append(op['after'][:-len(op['before'])])
assert text.encode('utf-8')==after
for op in reversed(m['operations']):
 a=op['before'].replace('\n',nl);b=op['after'].replace('\n',nl);assert text.count(b)==1;text=text.replace(b,a,1)
assert text.encode('utf-8')==before,'All e73 source/audio telemetry must restore byte for byte'
new='\n'.join(additions)
for name in ['Need','PlaySound2D','SpawnSound','InputKey','SetActorLocation','StartJump','TryBeginDodge','LoadObject','FinishCompilation','BeginStop','RequestExit','SetGamePaused']:
 assert re.search(r'\b'+name+r'\s*\(',new) is None,('New control/play/load/failure call',name)
contract=(HERE/'before/expected-two-frame-draws-v001.json').read_bytes();assert sha(contract)=='f85284dc25d0a5f0be5bf09aa7b9f7dbdf2a62bccbb61e4ca0c5ce0ef1238f6e'
manifest=json.loads((HERE/'before/import-manifest-v001.json').read_text(encoding='utf-8'));frames=json.loads(contract)['frames'];assets=manifest['assets'];assert len(assets)==14
assert {a['object_path'] for a in assets}=={p for f in frames for i,p in enumerate(f['draw_stack']) if i!=6}
for a in assets:
 b=Path(a['source']['path']).read_bytes();assert len(b)==a['source']['bytes'] and sha(b)==a['source']['sha256'];assert a['object_path'] in new and a['source']['sha256'] in new
normalized=after.decode('utf-8').replace('\r\n','\n');assert (HERE/'tests/brown-under-test.inc').read_text(encoding='utf-8')==normalized[normalized.index('bool Brown('):normalized.index('JO DodgeDraw(')]
assert (HERE/'tests/readback-under-test.inc').read_text(encoding='utf-8')==(HERE/'fragments/readback.inc').read_text(encoding='utf-8')
for p in HERE.rglob('*.py'):ast.parse(p.read_text(encoding='utf-8'),filename=str(p))
print(json.dumps({'insertions':len(m['operations']),'all_e73_bytes_and_audio_telemetry_roundtrip':True,'new_control_play_load_completion_failure_calls':0,'frozen_source_PNGs_verified':len(assets),'exact_contract_objects':True,'host_test_uses_actual_projected_Brown':True,'current_probe_checked':'--against-current' in sys.argv,'UE_run':False,'actual_source_written':False,'images_viewed':0}))
