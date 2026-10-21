from pathlib import Path
import ast,hashlib,json,re
R=Path(__file__).resolve().parent
W=R.parents[3]
def pin(p,row):
 b=p.read_bytes();assert len(b)==row['bytes'] and hashlib.sha256(b).hexdigest()==row['sha256'],str(p)
for row in json.loads((R/'source-freeze-v002.json').read_text())['files']:pin(R/row['path'],row)
freeze=R/'observer-freeze-v002.json'
if freeze.exists():
 for row in json.loads(freeze.read_text())['files']:pin(R/row['path'],row)
for p in (R/'tooling').glob('*.py'):ast.parse(p.read_text(encoding='utf-8'))
cpp=(R/'new-source/DungeonGuardArtPartialProbe.cpp').read_text(encoding='utf-8')
stripped=re.sub(r'"(?:\\.|[^"\\])*"','""',cpp)
stripped=re.sub(r'//[^\n]*','',stripped)
for forbidden in ['SpawnStoneGuard','SetActorLocation','SetActorTransform','SetState','StepTo','GameTick','SetFixedTimeStep']:
 assert not re.search(r'\b'+forbidden+r'\s*\(',stripped),forbidden
assert stripped.count('E->ApplyCombatHit(')==1 and 'E&&!E->GetStoneGuardDriver()' in stripped
old=W/'tools/scripts/verify-native-bound-capture-pixels-v001.py'
assert (R/'tooling/verify-native-pixels-v002.py').read_text()==old.read_text(encoding='utf-8-sig').replace("'fairytale-equipment-bound-native-flow-v1'","'guard-art-partial-native-observer-v002'")
print('Candidate/source freeze, Python syntax, forbidden gameplay-mutation scan and exact CRC/FIFO checker reuse passed. NOT UE/native/media verification.')
