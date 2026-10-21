"""Freeze the narrow visual-only change against v136 before native validation."""
from pathlib import Path
import hashlib,json,shutil,difflib
R=Path('F:/Ourgame');S=R/'UnrealGame/Source/CodexDungeon';E=R/'docs/production/first-batch-v2/evidence/combat-range-cleanup-v001/root-before-v136-v001'
O=R/'source-assets/production/fairytale-guard-v001/root-combat-range-source-v001';assert not O.exists();(O/'source').mkdir(parents=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def pin(p):return dict(path=p.relative_to(O).as_posix(),bytes=p.stat().st_size,sha256=sha(p))
patch=[]
for n in ['DungeonHUD.h','DungeonHUD.cpp','DungeonFairytaleGuardFullPresentationV003.cpp','DungeonFairytaleGuardPresentation.cpp']:
 p=S/n;q=O/'source'/n;shutil.copy2(p,q)
 patch.extend(difflib.unified_diff((E/n).read_text(encoding='utf-8-sig').splitlines(True),p.read_text(encoding='utf-8-sig').splitlines(True),fromfile='a/UnrealGame/Source/CodexDungeon/'+n,tofile='b/UnrealGame/Source/CodexDungeon/'+n))
(O/'combat-range-debug-only-v001.patch').write_text(''.join(patch),encoding='utf-8')
before=json.loads((E/'before-pins.json').read_text(encoding='utf-8-sig'))
baseline=json.loads((R/'source-assets/production/backups/v136-Hurt187G/compiled-source-manifest.json').read_text(encoding='utf-8-sig'))
changes={x['path'] for x in before['files']}
for x in baseline['files']:
 if x['path'].startswith('UnrealGame/Source/') and x['path'] not in changes:
  p=R/x['path'];assert p.stat().st_size==x['bytes'] and sha(p)==x['sha256'],p
assert sum((S/n).read_text(encoding='utf-8-sig').count('DrawCombatRangeDebugLine(') for n in ['DungeonHUD.cpp','DungeonFairytaleGuardFullPresentationV003.cpp','DungeonFairytaleGuardPresentation.cpp'])==7
rows=[pin(p) for p in sorted(O.rglob('*')) if p.is_file()]
(O/'combat-range-source-freeze-v001.json').write_text(json.dumps(dict(schema='Root-Guard-Combat-Range-Visual-Source-Freeze-v001',files=rows,changed_source_count=4,unchanged_other_source_count=242,original_kernel_and_observer_unchanged=True,default_debug=False,explicit_debug_flag='DungeonCombatRangeDebug',explicit_log_flag='DungeonCombatRangeProof',native_proof_pending=True,FinalAccepted=False,formal_complete_units=0),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(freeze=(O/'combat-range-source-freeze-v001.json').as_posix(),sha256=sha(O/'combat-range-source-freeze-v001.json'),source_files=246,changed=4,unchanged=242)))
