"""Freeze NEW candidate and metadata F copies only; no approval, engine or media."""
from pathlib import Path
import json,sys,shutil,subprocess,hashlib
import move7_host_reference_solver_v001 as h
R=Path('F:/Ourgame');C=Path(__file__).resolve().parent
B=R/'过程图稿与视频/2026-10-18_裂岩守卫Move7固定源RuntimeProfile与HostSolver准备_v001'
assert not B.exists()
def write(p,v):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('x',encoding='utf-8',newline='\n') as f:f.write(v if isinstance(v,str) else json.dumps(v,ensure_ascii=False,indent=2)+'\n')
P=C/'GuardMove7-runtime-profile-candidate-v001.json';p=h.validate_profile_data(h.read(P));test=C/'host-reference-verification-v002.json';d=h.read(test)
assert d['all_checks_passed'] and d['check_count']==266 and d['solver']==h.pin(C/'move7_host_reference_solver_v001.py')
for _ in range(2):
 for x in p['source7']:assert h.pin(x['source']['path'])==x['source']
argv=[sys.executable,'-B','-X','utf8',str(C/'move7_host_reference_solver_v001.py'),'--profile',str(P),'--profile-sha256',h.pin(P)['sha256'],'--request',str(C/'host-reference-request-example-v001.json')]
cli=subprocess.run(argv,cwd=R,capture_output=True,text=True,encoding='utf-8');result=json.loads(cli.stdout)
assert cli.returncode==0 and result['valid_reference_plan'] and result['part_count']==7 and not result['native_runtime_approved']
write(C/'host-CLI-entrypoint-proof-v001.json',dict(argv=argv,exit_code=cli.returncode,response_sha256=hashlib.sha256(cli.stdout.encode('utf-8')).hexdigest(),part_count=7,
 no_images=True,no_UE=True,no_provider=True,native_approved=False))
handoff=C/'Root-Move7-profile-and-host-handoff-v001.json'
write(handoff,dict(schema='Guard-Move7-profile-host-preparation-handoff-v001',profile=h.pin(P),solver=h.pin(C/'move7_host_reference_solver_v001.py'),
 verification=h.pin(test),precision_note=h.pin(C/'DrawTexture-mixed-precision-boundary-note-v001.md'),CPP_boundary_doc=h.pin(C/'C++-input-output-and-boundaries-v001.md'),
 source_snapshot_sha256=p['source_snapshot_sha256'],source7_count=7,artist_surface_point_count=18,source7_two_SHA_verification_passes=2,source7_mismatches=0,
 presentation_type=p['presentation_type'],Root_preparation_review=p['frozen_inputs']['Root_preparation_review'],
 pending_runtime=dict(compiled_snapshot=None,current_source_admission=None,actual_import_receipt=None,actual_GPU_preload_or_finish_receipt=None),
 F_batch=B.as_posix(),new_images_rendered=False,Root_E_required_before_new_media_View=False,
 native_generation_calls=0,Source_Content_tools_ledger_E_modified=False,RuntimeTrialAllowed=False,FinalAccepted=False))
freeze=C/'Move7-profile-host-preparation-freeze-v001.json'
write(freeze,dict(schema='Guard-Move7-profile-host-preparation-freeze-v001',files=[h.pin(q) for q in sorted(C.rglob('*')) if q.is_file()],
 current_profile=h.pin(P),current_solver=h.pin(C/'move7_host_reference_solver_v001.py'),current_verification=h.pin(test),
 historical_report='host-reference-verification-v001.json pins the earlier265-check solver; usev002 for final current solver.',
 source7_two_SHA_passes=2,source7_hash_mismatches=0,no_media=True,RuntimeTrialAllowed=False,FinalAccepted=False))
for q in C.rglob('*'):
 if q.is_file():
  dst=B/'原件'/q.relative_to(C);dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(q,dst)
for q in [P,test,handoff,C/'C++-input-output-and-boundaries-v001.md',C/'DrawTexture-mixed-precision-boundary-note-v001.md']:
 dst=B/'展示副本'/q.name;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(q,dst)
for _ in range(2):
 for q in C.rglob('*'):
  if q.is_file():assert h.rb(q)==h.rb(B/'原件'/q.relative_to(C))
write(B/'index.json',dict(schema='F-Move7-profile-host-source-version-status-v001',status='PREPARATION_ONLY_NO_NEW_MEDIA_OR_NATIVE_APPROVAL',profile=h.pin(P),handoff=h.pin(handoff),freeze=h.pin(freeze),
 files=[h.pin(q) for q in sorted(B.rglob('*')) if q.is_file()],verification_passes=2,canonical_copy_hash_mismatches=0,new_images_rendered=False,RuntimeTrialAllowed=False,FinalAccepted=False))
print(json.dumps(dict(profile=h.pin(P),solver=h.pin(C/'move7_host_reference_solver_v001.py'),verification=h.pin(test),handoff=h.pin(handoff),freeze=h.pin(freeze),F_batch=B.as_posix()),ensure_ascii=False,indent=2))
