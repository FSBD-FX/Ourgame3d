from pathlib import Path
import hashlib,json,sys
ROOT=Path(__file__).resolve().parent
WORKSPACE=ROOT.parents[3]
def pin(p):
 b=p.read_bytes();return len(b),hashlib.sha256(b).hexdigest()
freeze=ROOT/'presentation-freeze-v001.json'
if freeze.exists():
 for f in json.loads(freeze.read_text(encoding='utf-8'))['files']:
  assert pin(ROOT/f['path'])==(f['bytes'],f['sha256']),f['path']
base=json.loads((ROOT/'baseline-source-pins.json').read_text(encoding='utf-8'))
for f in base['files']:
 assert pin(WORKSPACE/f['path'])==(f['bytes'],f['sha256']),'Actual baseline changed: '+f['path']
M=json.loads((ROOT/'registration-proposals-and-import-map-v001.json').read_text(encoding='utf-8'))
assert len(M['rows'])==3 and sum(len(x['frames']) for x in M['rows'])==16
for R in M['rows']:
 assert not R['trial_allowed'] and not R['final_accepted'] and not R['trial_approval_record']
 assert R['ONE_row_display_px_per_source_px']==100.8/R['standing_body_extent_px']
 E=R['registration_evidence'];assert pin(WORKSPACE/E['path'])==(E['bytes'],E['sha256'])
 for F in R['frames']:
  S=F['source'];assert pin(Path(S['path']))==(S['bytes'],S['sha256']),S['path']
  assert F['floor_pivot_source_px']==[int(F['measured_paired_shoe_midpoint_x']+.5),464]
assert (ROOT/'stage0/DungeonFairytaleGuardPresentationTests.cpp').read_bytes()==(ROOT/'tests/DungeonFairytaleGuardPresentationTests.cpp').read_bytes()
assert json.loads((ROOT/'stage0/result.json').read_text())['run_exit']==1
assert json.loads((ROOT/'tests/result.json').read_text())['run_exit_code']==0
print('Candidate/source/art pins verified; Stage0 and production UE tests identical. NOT UE or visible fit verification.')
