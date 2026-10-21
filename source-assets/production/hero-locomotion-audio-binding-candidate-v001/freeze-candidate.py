"""Freeze only this NEW candidate directory; never read/write UE state."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json
HERE=Path(__file__).resolve().parent
OUT=HERE/'HeroLocomotionAudioBindingCandidate-freeze-v001.json'
assert not OUT.exists(),'Refusing overwrite'
files=[]
for p in sorted(HERE.rglob('*')):
 if p.is_file() and p!=OUT:
  b=p.read_bytes();files.append({'relative_path':p.relative_to(HERE).as_posix(),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()})
obj={'schema':'HeroLocomotionAudioBindingCandidateFreeze-v001','created_utc':datetime.now(timezone.utc).isoformat(),'status':'CANDIDATE_ONLY_HOST_GREEN_NOT_UE_COMPILED_NOT_IMPORTED_NOT_AUDITIONED','ownership':'Only NEW F:/Ourgame/source-assets/production/hero-locomotion-audio-binding-candidate-v001','scope':'Six named locomotion cues; GameMode managed real PlayerFighter only; no hurt/death/mix acceptance','base_compiled_manifest_sha256':'fb225bef1e9b2e3584a16d3eff192bd39587867b68c0fcdb525a4d876324e59a','source_audio_freeze_sha256':'cf63ec47a15855f17703f72540471d8cba2a7a952a26bfc7bc03acd0b2f216ac','host_checks':59,'host_failures':0,'red_checks':59,'red_expected_failures':13,'ue_runs':0,'api_calls':0,'actual_source_content_tools_E_media_ledger_writes':0,'files':files,'file_count':len(files),'member_total_bytes':sum(r['bytes'] for r in files),'excluded':'This freeze file only; no self-hash'}
with OUT.open('x',encoding='utf-8',newline='\n') as f:json.dump(obj,f,ensure_ascii=False,indent=2);f.write('\n')
b=OUT.read_bytes();print(json.dumps({'freeze':str(OUT),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest(),'file_count':len(files),'member_total_bytes':obj['member_total_bytes']}))
