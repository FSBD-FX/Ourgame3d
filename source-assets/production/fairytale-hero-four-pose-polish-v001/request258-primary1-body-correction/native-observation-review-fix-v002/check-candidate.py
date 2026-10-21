"""Stable v002 snapshot/full and scoped delta checks. No UE or actual writes."""
from pathlib import Path
import ast,hashlib,json,re,sys
HERE=Path(__file__).resolve().parent;sha=lambda b:hashlib.sha256(b).hexdigest()
v1freeze=(HERE/'before/observer-candidate-freeze-v001.json').read_bytes();assert sha(v1freeze)=='0fcc6eb38e6675c48a6fa66811b371c3443e2570ce19ef6d7ddefaaf5b81c35e'
review=(HERE/'before/art258-native-observer-review-v001.md').read_bytes();assert len(review)==3859 and sha(review)=='302e6298c138cbf309f0bd61b503230757753d8f3ad5b706f4968bd0b6655a39'
members={r['relative_path']:r for r in json.loads(v1freeze)['files']}
copied=['tests/ue-small-shim.h','tests/brown-and-readback.cpp','tests/brown-under-test.inc','tests/readback-under-test.inc','tests/run-host.ps1','fragments/helper.inc','fragments/brown-branch.inc','fragments/readback.inc','fragments/report-metadata.inc']
for rel in copied:
 b=(HERE/rel).read_bytes();assert len(b)==members[rel]['bytes'] and sha(b)==members[rel]['sha256'],('v001 retained source changed',rel)
m=json.loads((HERE/'exact-seams.json').read_text(encoding='utf-8'));before=(HERE/m['before_snapshot']).read_bytes();after=(HERE/m['projected_source']).read_bytes();assert sha(before)==m['source_sha256'] and sha(after)==m['result_sha256'];assert len(after)==m['result_bytes']
if '--against-current' in sys.argv:assert Path(m['historical_actual_source']).read_bytes()==before,'Current actual probe drift'
def apply(base,ops,nl):
 text=base.decode('utf-8')
 for op in ops:
  a=op['before'].replace('\n',nl);b=op['after'].replace('\n',nl);assert b.endswith(a) and text.count(a)==1;text=text.replace(a,b,1)
 return text
nl='\r\n' if m['line_ending']=='CRLF' else '\n';text=apply(before,m['operations'],nl);assert text.encode('utf-8')==after
for op in reversed(m['operations']):
 a=op['before'].replace('\n',nl);b=op['after'].replace('\n',nl);assert text.count(b)==1;text=text.replace(b,a,1)
assert text.encode('utf-8')==before,'All e73 original/gameplay/audio must restore byte for byte'
d=json.loads((HERE/'v001-to-v002-exact-delta.json').read_text(encoding='utf-8'));v1=(HERE/d['before_snapshot']).read_bytes();assert sha(v1)==d['before_sha256'];assert apply(v1,d['operations'],nl).encode('utf-8')==after
new='\n'.join(o['after'][:-len(o['before'])] for o in d['operations'])
for name in ['Need','PlaySound2D','SpawnSound','InputKey','SetActorLocation','StartJump','TryBeginDodge','FinishCompilation','BeginStop','RequestExit','SetGamePaused','FindObject']:
 assert re.search(r'\b'+name+r'\s*\(',new) is None,('Added control/failure/find/compile call',name)
assert len(d['operations'])==2 and '#include "UObject/StrongObjectPtr.h"' in new
assert (HERE/'tests/legacy-preload-under-test.inc').read_text(encoding='utf-8')==(HERE/'fragments/legacy-preload.inc').read_text(encoding='utf-8')
normalized=after.decode('utf-8').replace('\r\n','\n');assert (HERE/'tests/brown-under-test.inc').read_text(encoding='utf-8')==normalized[normalized.index('bool Brown('):normalized.index('JO DodgeDraw(')]
for p in HERE.rglob('*.py'):ast.parse(p.read_text(encoding='utf-8'),filename=str(p))
print(json.dumps({'full_e73_insertions':len(m['operations']),'v001_delta_insertions':len(d['operations']),'all_e73_and_v001_existing_bytes_preserved':True,'retained_v001_host_and_fragments_pins':len(copied),'tested_preload_equals_projected':True,'actual_source_checked':'--against-current' in sys.argv,'new_control_play_find_compile_failure_calls':0,'UE_run':False,'actual_writes':False}))
