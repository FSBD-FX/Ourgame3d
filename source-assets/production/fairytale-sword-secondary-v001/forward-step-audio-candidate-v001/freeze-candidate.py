"""Exclusive candidate freeze. Never follow mutable actual Source/DLL/build pins."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json
HERE=Path(__file__).resolve().parent;ROOT=Path('F:/Ourgame');sha=lambda b:hashlib.sha256(b).hexdigest()
def pin(p,role=None):
 b=p.read_bytes();r=dict(path=p.as_posix(),bytes=len(b),sha256=sha(b))
 if role:r['role']=role
 return r
deps=[
 ('stable_compiled_manifest_before',ROOT/'source-assets/production/backups/v146-Primary1Bridge258-Residency-303-1439-203GREEN-v002/compiled-source-manifest.json'),
 ('existing_locomotion_source_freeze',ROOT/'source-assets/production/hero-locomotion-audio-candidate-v001/HeroLocomotionAudio-Candidate-freeze-v001.json'),
 ('existing_locomotion_binding_freeze',ROOT/'source-assets/production/hero-locomotion-audio-binding-candidate-v001/HeroLocomotionAudioBindingCandidate-freeze-v001.json'),
 ('readonly_existing_events_research',ROOT/'docs/production/first-batch-v2/evidence/HeroSwordSecondary-v147-v001/Root-K-audio-existing-events-v001.md')]
out=HERE/'candidate-freeze-v001.json'
members=[pin(p) for p in sorted(HERE.rglob('*')) if p.is_file() and p!=out and '__pycache__' not in p.parts]
seams=json.loads((HERE/'exact-seams.json').read_text(encoding='utf-8'))
data=dict(schema='hero-swd-successful-forward-step-audio-candidate-freeze-v001',created_utc=datetime.now(timezone.utc).isoformat(),status='CANDIDATE_ONLY_NOT_ADMITTED_NOT_UE_COMPILED_NOT_RUN',members=members,dependencies=[pin(p,role) for role,p in deps],projected_sources=[pin(HERE/r['projected']) for r in seams['files']],exact_operations=sum(len(r['operations']) for r in seams['files']),host_final_checks=17,host_final_failures=0,host_initial_RED_checks=16,host_initial_RED_expected_failures=2,host_shim_only=True,source_files_before=303,production_files_before=1439,actual_project_writes=0,UE_builds=0,UE_runs=0,images_generated_or_viewed=0,external_API_calls=0,native_audio_success_proven=False,FinalAccepted=False)
with out.open('x',encoding='utf-8',newline='\n') as f:json.dump(data,f,ensure_ascii=False,indent=2);f.write('\n')
for r in data['members']+data['dependencies']:
 b=Path(r['path']).read_bytes();assert len(b)==r['bytes'] and sha(b)==r['sha256']
print(json.dumps(dict(freeze=pin(out),members=len(members),dependencies=len(deps),all_pins_verified=True)))
