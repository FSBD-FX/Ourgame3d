"""Supplement frozen Air verifier with actual staged process/module and runtime bytes."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,importlib.util,json,hashlib
R=Path('F:/Ourgame');S=R/'Playables/钟盔轻甲-v142-CM52f906'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def pin(p):
 p=Path(p).resolve();h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return dict(path=p.as_posix(),bytes=p.stat().st_size,sha256=h.hexdigest())
ap=argparse.ArgumentParser();ap.add_argument('--archive',required=True);a=ap.parse_args();M=Path(a.archive).resolve()
native=read(M/'native-independent-verification-v004.json');idx=read(M/'index.json');run=read(M/'原件/runtime-report.json');launch=read(M/'launch-receipt-v001.json');mod=read(M/'actual-loaded-staged-module-v001.json')
assert native['passed'] is True and run['passed'] is True and run['flow_complete'] is True and idx['exit_code']==0
pid=int(run['process_id']);assert pid==idx['process_id']==launch['process_id']==mod['process_id']==native['process_id']
assert Path(mod['actual_loaded_DLL']).resolve()==(S/'Binaries/Win64/UnrealEditor-CodexDungeon.dll').resolve()
assert mod['module_pin']==pin(S/'Binaries/Win64/UnrealEditor-CodexDungeon.dll')
assert Path(launch['arguments'][0]).resolve()==(S/'CodexDungeon.uproject').resolve()==Path(mod['staged_project_path']).resolve()
manual=read(R/'source-assets/production/fairytale-hero-air-v001/root-manual-v013/manual-input-v013.json')
required=['-DungeonCandidateSprites','-DungeonFairytaleSwordBodyPreview','-DungeonFairytaleSwordBodyV002Preview','-DungeonFairytaleSwordArmorPrimary1Preview','-DungeonFairytaleSwordPrimary2Preview','-DungeonFairytaleSwordPrimary2BodyPreview','-DungeonFairytaleSwordPrimary2ArmorPreview','-DungeonFairytaleSwordPrimary3ArmorPreview','-DungeonFairytaleLeatherReadyPreview','-DungeonFairytaleLeatherPrimary1Preview','-DungeonFairytaleLeatherPrimary2Preview','-DungeonFairytaleLeatherPrimary3Preview','-DungeonFairytaleSwordEquipmentBoundPreview','-DungeonFairytaleSwordWalkPreview','-DungeonFairytaleSwordHurtPreview','-DungeonFairytaleSwordDeathPreview','-DungeonFairytaleSwordDodgePreview','-DungeonFairytaleSwordAirPreview','-DungeonFairytaleGuardFullPreview','-DungeonFairytaleGuardStompPreview','-DungeonFairytaleGuardMoveRigPreview']
assert all(x in launch['arguments'] for x in required)
assert '-DungeonShowInterface' not in launch['arguments'] and '-DungeonCombatRangeDebug' not in launch['arguments']
candidate=R/'source-assets/production/fairytale-hero-air-v001/stable-preview-candidate-v001/stage-stable-preview-v001.py'
assert pin(candidate)['sha256']=='6537c2c8fa0d19117e0c71c712bdeb0e8cc00a034c4a682def8e304221fd9fc5'
spec=importlib.util.spec_from_file_location('staged_copy_readonly',candidate);c=importlib.util.module_from_spec(spec);spec.loader.exec_module(c)
snapshot=read(S/'_proof/runtime-snapshot-manifest-v001.json')
for buffered in (False,True):
 c.verify_rows(S,snapshot['runtime_files']+snapshot['metadata_files'],buffered);c.exact_runtime(S,snapshot['runtime_files'])
assert (snapshot['runtime_count'],snapshot['runtime_bytes'])==(1778,143122086)
result=dict(schema='Root-staged-Air6-independent-supplement-v001',passed=True,utc=datetime.now(timezone.utc).isoformat(),actual_process_id=pid,staged_project=pin(S/'CodexDungeon.uproject'),actual_loaded_DLL=mod,compiled_manifest_pin=native['compiled_manifest_pin'],native_independent_pin=pin(M/'native-independent-verification-v004.json'),runtime_manifest_pin=pin(S/'_proof/runtime-snapshot-manifest-v001.json'),native_before_after_runtime_checked_by_launcher=True,post_native_runtime_full_two_pass_verified=True,runtime_files=1778,runtime_bytes=143122086,exact_runtime_membership_verified=True,manual_visual_flags_verified=required,capture_control='Fresh staged Editor-game process uses automatic normal Enter/E/Space and explicit predecessor Knight diagnostic; ordinary manual launcher has no automation/diagnostic.',human_playtest=False,full_realtime_playback_reviewed=False,audio_listened=False,FinalAccepted=False)
out=M/'staged-native-supplement-v001.json'
with out.open('x',encoding='utf-8') as f:json.dump(result,f,ensure_ascii=False,indent=2)
print(json.dumps(pin(out),ensure_ascii=False))
