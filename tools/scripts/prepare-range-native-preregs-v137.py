"""Pre-register fresh default-left/default-right and debug-left real-Axe captures."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
R=Path('F:/Ourgame'); H=R/'source-assets/production/fairytale-hero-state-gap-v001'; G=R/'source-assets/production/fairytale-guard-v001/root-Hurt1286-checkpoint-v002'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def pin(p):return dict(path=p.as_posix(),bytes=p.stat().st_size,sha256=sha(p))
mfile=R/'source-assets/production/backups/v137-range187G/compiled-source-manifest.json';m=read(mfile)
assert (m['strict_registered_tests'],m['source_files'],m['production_files'])==(187,246,1286)
rows={x['path']:x for x in m['files']}
for side,name in [(-1,'left'),(1,'right')]:
 p=read(H/('Root-Hurt4-prereg-v136-'+name+'-v001.json'))
 paths=set(x['path'] for x in p['admitted_source_files'])|{'UnrealGame/Source/CodexDungeon/'+n for n in ['DungeonFairytaleGuardFullPresentationV003.cpp','DungeonFairytaleGuardPresentation.cpp']}
 p.update(compiled_manifest_sha256=sha(mfile),Guard_profile_prereg_pin=pin(G/'guard-known44-source-profile-prereg-Hurt1286-v001.json'),production_extension_approval_pin=pin(G/'production-extension-Root-approval-Hurt1286-v001.json'),admitted_source_files=[rows[n] for n in sorted(paths)],registered_at_utc=datetime.now(timezone.utc).isoformat(),notes='Fresh actual compiled v137 default-range-off checkpoint, full187/Source246/Production1286. Unchanged official real-Axe Hurt observer, optical and CRC checks. Default0 and debug1 controlled captures; no final-art acceptance.')
 out=H/('Root-Hurt4-prereg-v137-'+name+'-v001.json');assert not out.exists();out.write_text(json.dumps(p,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(out.as_posix())
