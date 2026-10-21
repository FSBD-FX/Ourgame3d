"""Fill only a NEW Root checkpoint after real both-side native and visible review."""
from datetime import datetime,timezone
import argparse,copy,json,runpy
from move7_manual_contract_v001 import *

def write(p,d):
 with p.open('x',encoding='utf-8',newline='\n')as f:json.dump(d,f,ensure_ascii=False,indent=2);f.write('\n')
def current(names,files):
 need(len(names)==len(set(names)),'Duplicate current source names')
 for n in names:need(n in files,'Compiled Source missing: '+n);check(files[n])
 return[copy.deepcopy(files[n])for n in sorted(names)]

def main():
 p=argparse.ArgumentParser()
 for n in['snapshot','left-prereg','right-prereg','left-archive','right-archive','root-visual-review','output-dir']:p.add_argument('--'+n,required=True)
 p.add_argument('--approve-manual-checkpoint',action='store_true');a=p.parse_args()
 need(a.approve_manual_checkpoint,'Root explicit --approve-manual-checkpoint required after actual native and visible review')
 deps=inputs();own=HERE/FREEZE_NAME;dodge.frozen(own)
 snapshot=resolve(a.snapshot);mp=snapshot/'compiled-source-manifest.json';cm=read(mp);files={x['path']:x for x in cm['files']}
 need(pin(mp)==deps['green_snapshot'],'Select the exact Root-reviewed283/200GREEN compiled manifest')
 need(cm['mode']=='green'and(cm['source_files'],cm['production_files'],cm['passed'],cm['failed'],cm['strict_registered_tests'])==(283,1371,200,0,200),'Actual283/1371/full200 strict GREEN required')
 old=read(check(deps['v011_manual']));m=copy.deepcopy(old);now=datetime.now(timezone.utc).isoformat();compiled=pin(mp)['sha256']
 m.update(schema=MANUAL_SCHEMA,is_template=False,RootApproved=True,snapshot_directory=snapshot.as_posix(),snapshot_manifest_pin=pin(mp),checkpoint_tooling_freeze_pin=pin(own),full_suite_pin=copy.deepcopy(cm['full_suite']),last_build_pin=copy.deepcopy(cm['current_build']),DLL_pin=copy.deepcopy(files['UnrealGame/Binaries/Win64/UnrealEditor-CodexDungeon.dll']),strict_registered_tests=200,source_files=283,production_files=1371,production_extension_checker_pin=pin(HERE/'validate-Move7-production-extension-v001.py'),Move7_flag='DungeonFairytaleGuardMoveRigPreview',Move7_parts=7,Move7_required_resources=7,Move7_presentation_type='GuardMoveSevenComponentRigDerived',Move7_leg_occlusion_outline_accepted=False,completed_combinations=0,registered_at_utc=now)
 m['Move7_native_prereg_pins']={n:pin(resolve(getattr(a,n+'_prereg')))for n in['left','right']}
 m['Move7_proof_geometry_repair_freeze_pin']=copy.deepcopy(deps['Move7_proof_geometry_freeze']);m['Move7_proof_geometry_repair_checker_pin']=copy.deepcopy(deps['Move7_proof_geometry_checker'])
 m['Move7_native_archives']={n:resolve(getattr(a,n+'_archive')).as_posix()for n in['left','right']}
 m['Move7_independent_native_pins']={n:pin(resolve(m['Move7_native_archives'][n])/'原件/Move7-independent-native-verification-v001.json')for n in['left','right']}
 m['Move7_native_evidence_files']={n:[pin(x)for x in sorted(resolve(m['Move7_native_archives'][n]).rglob('*'))if x.is_file()]for n in['left','right']}
 m['Move7_Root_visual_review_pin']=pin(resolve(a.root_visual_review))
 # These complete real gates run before the output leaf exists. No passed
 # native receipt, Root visual opinion, snapshot or import receipt is invented.
 source_chain(m,files);project196(read(check(cm['full_suite'])));native_evidence(m,cm)
 for key in['admitted_Death_source_files','admitted_Hurt_source_files','admitted_Stomp_source_files','admitted_Dodge_source_files']:m[key]=current({x['path']for x in old[key]},files)
 m['admitted_Move7_source_files']=current(move.STAGE|move.INTERFACE|{move.FOURTH}|move.PROD_ALLOWED|move.PROBE,files)
 trial=copy.deepcopy(read(check(old['Dodge_runtime_trial_registration_pin'])));trial.update(compiled_manifest_sha256=compiled,registered_at_utc=now)
 overlay=copy.deepcopy(read(check(old['Stomp50_row_approval_pin'])));overlay.update(compiled_manifest_sha256=compiled,registered_at_utc=now)
 prereg=copy.deepcopy(read(check(old['source_profile_prereg_pin'])));prereg.update(compiled_manifest_sha256=compiled,strict_registered_tests=200,source_files=283,production_files=1371,registered_at_utc=now,status='MANUAL_V012_MOVE7_WITH_ACTUAL_NATIVE_AND_ROOT_VISIBLE_REVIEW_BOUND_SEPARATELY')
 prereg['admitted_source_files']=current({x['path']for x in prereg['admitted_source_files']}|{x['path']for x in m['admitted_Move7_source_files']},files)
 oldext=read(check(old['production_extension_approval_pin']))
 ext=dict(schema='Move7-Root-production-extension-v001',is_template=False,RootApproved=True,compiled_manifest_sha256=compiled,expected_old_base=1364,expected_new_count=7,expected_total=1371,base_Dodge1364_approval_pin=copy.deepcopy(old['production_extension_approval_pin']),snapshot_directory=snapshot.as_posix(),Move7_native_prereg_pin=m['Move7_native_prereg_pins']['left'],automatic_inputs=False,diagnostic_damage=False,FinalAccepted=False,registered_at_utc=now)
 for k in['Dodge32_import_manifest_pin','Dodge32_native_receipt_pin','Dodge32_independent_twoSHA_pin']:ext[k]=copy.deepcopy(oldext[k])
 pleft=read(check(m['Move7_native_prereg_pins']['left']));native=read(move.pin(pleft['native_import_pin']))
 ext['Move7_saved_packages']=current({resolve(x['saved']['path']).relative_to(R).as_posix()for x in native['assets']},files)
 output=resolve(a.output_dir);need(not output.exists(),'New output directory required; never overwrite previous checkpoint')
 output.mkdir(parents=True,exist_ok=False);success=False;failure=''
 try:
  write(output/'Dodge33-runtime-source-rebind-v012.json',trial);m['Dodge_runtime_trial_registration_pin']=pin(output/'Dodge33-runtime-source-rebind-v012.json')
  write(output/'Stomp50-row-source-rebind-v012.json',overlay);m['Stomp50_row_approval_pin']=pin(output/'Stomp50-row-source-rebind-v012.json');ext['Stomp50_row_approval_pin']=m['Stomp50_row_approval_pin']
  write(output/'Move7-production-extension-Root-approval-v001.json',ext);m['production_extension_approval_pin']=pin(output/'Move7-production-extension-Root-approval-v001.json');prereg['production_extension_pin']=m['production_extension_approval_pin']
  write(output/'Known44-source-profile-prereg-v012.json',prereg);m['source_profile_prereg_pin']=pin(output/'Known44-source-profile-prereg-v012.json')
  write(output/'manual-input-v001.json',m);facts=verify(output/'manual-input-v001.json',snapshot);success=True
 except Exception as e:failure=str(e);raise
 finally:write(output/'preparation-receipt-v001.json',dict(schema='Root-Move7-v012-manual-checkpoint-preparation-v001',success=success,failure=failure,compiled_manifest=pin(mp),outputs=[pin(x)for x in sorted(output.iterdir())if x.is_file()],actual_native_receipts_created=False,Root_visual_review_created=False,automatic_inputs=False,diagnostic_damage=False,UE_started=False,FinalAccepted=False))
 print(json.dumps(dict(success=True,manual_input=pin(output/'manual-input-v001.json'),facts=facts,UE_started=False),ensure_ascii=False))
if __name__=='__main__':main()
