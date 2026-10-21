"""Host structural validation only; never compiles/runs UE or changes Source."""
from pathlib import Path
import ast,hashlib,json,re,sys
HERE=Path(__file__).resolve().parent;sha=lambda b:hashlib.sha256(b).hexdigest()
pins=json.loads((HERE/'before-source-pins.json').read_text(encoding='utf-8'))
assert sha(Path(pins['base_compiled_source_manifest']).read_bytes())==pins['base_compiled_source_manifest_sha256']
for r in pins['pins']:
 b=(HERE/r['snapshot_relative_path']).read_bytes();assert len(b)==r['bytes'] and sha(b)==r['sha256'],r['snapshot_relative_path']
 if '--against-current' in sys.argv:
  actual=Path(r['historical_actual_path']).read_bytes();assert actual==b,('Current source drift before admit',r['historical_actual_path'])
m=json.loads((HERE/'exact-seams.json').read_text(encoding='utf-8'));before=(HERE/'before/DungeonHeroLandingPriorityProbeV001.cpp').read_bytes();after=Path(m['projected_source']).read_bytes()
assert sha(before)==m['source_sha256'] and sha(after)==m['result_sha256']
nl='\r\n' if m['line_ending']=='CRLF' else '\n';text=before.decode('utf-8')
for op in m['operations']:
 a=op['before'].replace('\n',nl);b=op['after'].replace('\n',nl);assert b.endswith(a) and text.count(a)==1; text=text.replace(a,b,1)
assert text.encode('utf-8')==after
for op in reversed(m['operations']):
 a=op['before'].replace('\n',nl);b=op['after'].replace('\n',nl);assert text.count(b)==1;text=text.replace(b,a,1)
assert text.encode('utf-8')==before,'Removing insertions must restore all original code bytes'
added='\n'.join(op['after'][:-len(op['before'])] for op in m['operations'])
assert (HERE/'fragments/portable-cursor.inc').read_text(encoding='utf-8') in added
for name in ['PlaySound2D','PlaySoundAtLocation','SpawnSound','InputKey','SetActorLocation','StartJump','TryBeginDodge','SetGamePaused','RequestExit','BeginStop','Need']:
 assert re.search(r'\b'+name+r'\s*\(',added) is None,('Added forbidden control/play/failure call',name)
for p in HERE.rglob('*.py'):ast.parse(p.read_text(encoding='utf-8'),filename=str(p))
print(json.dumps({'snapshot_pins_verified':len(pins['pins']),'current_sources_checked':'--against-current' in sys.argv,'insertions':len(m['operations']),'original_code_byte_roundtrip':True,'portable_test_fragment_equals_projected':True,'new_control_play_failure_calls':0,'python_syntax':True,'actual_source_count_before_observed':m['actual_source_count_observed'],'actual_production_files_before_observed':m['actual_production_file_count_observed'],'actual_source_written':False,'UE_run':False}))
