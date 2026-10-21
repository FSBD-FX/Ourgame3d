"""Preserve successful-with-IWYU-diagnostic build and add the cpp's own first include."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,shutil
R=Path('F:/Ourgame');EV=R/'docs/production/first-batch-v2/evidence/HeroLocomotionAudio-v145-v001';O=EV/'Root-own-first-header-repair-v001'
def pin(p):
 p=Path(p).resolve();b=p.read_bytes();return dict(path=p.as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
p=R/'UnrealGame/Source/CodexDungeon/DungeonHeroLocomotionAudioNativeV001.cpp';before=pin(p)
ad=json.loads((EV/'Root-source-admission-v001/actual-source-admission.json').read_text(encoding='utf-8'))
row=next(row for row in ad['after_files'] if Path(row['path']).name==p.name);assert(before['bytes'],before['sha256'])==(row['bytes'],row['sha256'])
build=R/'UnrealGame/Saved/Bootstrap/last-build.json';data=json.loads(build.read_text(encoding='utf-8-sig'));log=Path(data['Log']);assert data['ExitCode']==0
assert 'Expected DungeonHeroLocomotionAudioNativeV001.h to be first header included.' in log.read_text(encoding='utf-8-sig')
source=p.read_bytes();assert source.startswith(b'#include "DungeonGameMode.h"') and b'#include "DungeonHeroLocomotionAudioNativeV001.h"' not in source
nl=b'\r\n' if source.count(b'\r\n')==source.count(b'\n') else b'\n';after=b'#include "DungeonHeroLocomotionAudioNativeV001.h"'+nl+source
assert not O.exists();O.mkdir();shutil.copy2(p,O/'before.cpp');shutil.copy2(build,O/'diagnostic-build.json');shutil.copy2(log,O/log.name)
with (O/'after-preview.cpp').open('xb') as f:f.write(after)
p.write_bytes(after)
for _ in range(2):assert p.read_bytes()==after
receipt=dict(schema='Root-hero-locomotion-own-first-header-repair-v001',utc=datetime.now(timezone.utc).isoformat(),RootApproved=True,is_template=False,actual_applied=True,before=before,after=pin(p),before_backup=pin(O/'before.cpp'),source_admission=pin(EV/'Root-source-admission-v001/actual-source-admission.json'),diagnostic_build=pin(O/'diagnostic-build.json'),diagnostic_log=pin(O/log.name),diagnostic_build_actual_exit_code=0,reason='UE own-first-header diagnostic despite successful UBT exit0; add own header before GameMode, all existing bytes preserved after this line.',gameplay_logic_changed=False,frozen_candidate_edited=False,verification_passes=2,current_build_after_repair_pending=True,FinalAccepted=False)
out=O/'actual-source-repair-admission.json'
with out.open('x',encoding='utf-8') as f:json.dump(receipt,f,ensure_ascii=False,indent=2)
print(json.dumps(pin(out),ensure_ascii=False))
