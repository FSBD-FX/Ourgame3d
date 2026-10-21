"""Freeze final bounded-review evidence; original reports and snapshots stay intact."""
from pathlib import Path
import hashlib,json
root=Path('F:/Ourgame');e=root/'docs/production/first-batch-v2/evidence/run-capture-v001'
out=e/'final-review-retention-manifest-v001.json';assert not out.exists()
files=[root/'docs/production/first-batch-v2/run-capture-typed-aggregate-runtime-proof-v001.md',
 e/'actual-full122-audit-v001.json',e/'independent-review-v001/review-v001.md',e/'independent-review-v001/actual-source-report-binding-v001.json',
 e/'production-v005/author-review-v005.md',e/'production-v005/manifest.json',
 root/'UnrealGame/Saved/Automation/FirstRoom-20261016-065538/index.json',root/'UnrealGame/Saved/Automation/FirstRoom-20261016-065641/index.json',
 root/'source-assets/production/backups/2026-10-16_RunExploration-and-typedAggregate-full122GREEN-v089/compiled-source-manifest.json',
 root/'source-assets/production/backups/2026-10-16_RunCapture-typed4GREEN-v088/tools/scripts/test-first-room.ps1',
 root/'tools/scripts/test-first-room.ps1',root/'tools/scripts/audit-run-aggregate-full122-v001.py',root/'tools/scripts/checkpoint-run-aggregate-full122-v001.py',Path(__file__)]
for pattern in ['actual-results-v001.json','author-final-actual-v001.md']:
 files+=list(e.rglob(pattern))
rows=[]
for p in dict.fromkeys(files):
 data=p.read_bytes();rows.append({'path':p.as_posix(),'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()})
out.write_text(json.dumps({'files':rows,'scope':'Actual122GREEN typed Capture/Validate final review; notpausedInstall/codec/Continue',
 'actual_fullrun_runner':'v088 script with explicit ExpectedTests122; default literal116 at actual execution. v089 changes default literal only afterGREEN.',
 'formal_complete_units':0},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'manifest':out.as_posix(),'files':len(rows),'formal_complete_units':0}))
