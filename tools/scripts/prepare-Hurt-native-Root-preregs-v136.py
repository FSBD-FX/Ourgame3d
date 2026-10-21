"""Register both fresh scoped real-Axe Hurt trials against actual compiled187/1286."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
R=Path('F:/Ourgame');H=R/'source-assets/production/fairytale-hero-state-gap-v001';C=H/'hurt-native-observer-candidate-v001';G=R/'source-assets/production/fairytale-guard-v001/root-Hurt1286-checkpoint-v001'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def pin(p):return dict(path=p.as_posix(),bytes=p.stat().st_size,sha256=sha(p))
mfile=R/'source-assets/production/backups/v136-Hurt187G/compiled-source-manifest.json';m=read(mfile);assert m['strict_registered_tests']==187 and m['source_files']==246 and m['production_files']==1286
paths=['DungeonHeroHurtProbeV001.h','DungeonHeroHurtProbeV001.cpp','DungeonFairytaleSwordHurtDrawState.h','DungeonFairytaleSwordHurtPresentation.cpp','DungeonFairytaleSwordHurtTextures.inl','DungeonFairytaleSwordHurtPlan.h','DungeonFairytaleSwordHurtPlan.cpp','DungeonFairytaleSwordHurtProfile.h','DungeonFairytaleSwordHurtProfile.cpp','DungeonHUD.h','DungeonHUD.cpp','DungeonFighter.h','DungeonFighter.cpp','Tests/DungeonFairytaleSwordHurtV001Tests.cpp','DungeonFairytaleSwordPresentation.cpp','DungeonFairytaleSwordDrawState.h']
rows={x['path']:x for x in m['files']}
for side,name in [(-1,'left'),(1,'right')]:
 p=read(C/'Root-Hurt4-prereg-TEMPLATE-NOT-APPROVED-v001.json')
 p.update(is_template=False,RootApproved=True,pre_registered_before_capture=True,approach_side=side,compiled_manifest_sha256=sha(mfile),candidate_freeze_pin=pin(C/'Hurt-native-observer-freeze-v001.json'),Guard_profile_prereg_pin=pin(G/'guard-known44-source-profile-prereg-Hurt1286-v001.json'),production_extension_approval_pin=pin(G/'production-extension-Root-approval-Hurt1286-v001.json'),admitted_source_files=[rows['UnrealGame/Source/CodexDungeon/'+n] for n in paths],actual_native_import_receipt_pin=pin(R/'UnrealGame/Saved/Bootstrap/hurt32-v002-import-20261018-080500-460471.json'),registered_at_utc=datetime.now(timezone.utc).isoformat(),notes='Root scoped trial after actual3RED→3GREEN/full187/Source246+Production1286 compiled snapshot2172 and independent source profile. GPU/native/visual proof pending; no final-art acceptance.')
 out=H/('Root-Hurt4-prereg-v136-'+name+'-v001.json');assert not out.exists();out.write_text(json.dumps(p,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(out.as_posix())
