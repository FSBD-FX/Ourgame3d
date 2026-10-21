"""Root executes only after real build/full187. Fresh snapshot and NEW scoped records, no UE."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,os,runpy,shutil
from checkpoint_common_v001 import *
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--root-input',required=True);ap.add_argument('--validate-inputs-only',action='store_true');a=ap.parse_args()
 request_path=resolve(a.root_input);q=read(request_path);self_freeze=own_freeze()
 need(q['schema']=='Hurt1286-Root-checkpoint-input-v001' and q['RootApproved'] is True and q['is_template'] is False,'NEW actual Root request required; template never approves itself')
 need(check(q['checkpoint_tooling_freeze_pin'])==self_freeze,'Root request binds another checkpoint tool')
 report=check(q['full_suite_pin']);strict_suite(read(report));build=check(q['last_build_pin']);b=read(build);need(build==R/'UnrealGame/Saved/Bootstrap/last-build.json' and b['ExitCode']==0,'Actual current successful build receipt required')
 log=resolve(b['Log']);need(log.is_file(),'Actual current build log missing');dll=check(q['DLL_pin']);need(dll==R/'UnrealGame/Binaries/Win64/UnrealEditor-CodexDungeon.dll','Wrong current DLL')
 baseline_path=check(q['base_snapshot_manifest_pin']);base=read(baseline_path);need(base['production_files']==1254 and base['strict_registered_tests']==184,'Explicit actual old1254/184 baseline required')
 profile_base=check(q['base_source_profile_prereg_pin']);prereg=read(profile_base);need(prereg['compiled_manifest_sha256']==sha(baseline_path),'Base source-profile and baseline snapshot differ')
 ext_freeze=check(q['extension_candidate_freeze_pin']);need(ext_freeze==EXT/'candidate-freeze-v004.json','Only exact existing profile extension v004 is supported')
 production_freeze=check(q['Hurt_production_candidate_freeze_pin'])
 native=check(q['Hurt_actual_native_import_receipt_pin']);independent=check(q['Hurt_independent_twoSHA_verification_pin']);rc=read(native);proof=read(independent)
 need(rc['schema']=='Hurt32-actual-native-import-v002' and rc['success'] is True and proof['schema']=='Hurt32-independent-native-receipt-verification-v002' and proof['success'] is True and proof['receipt']==pin(native,True),'Exact actual successful Hurt32 native/independent pair required')
 out=resolve(q['snapshot_output']);reg=resolve(q['registration_output']);need(out.is_relative_to(R/'source-assets/production/backups') and reg.is_relative_to(R/'source-assets/production/fairytale-guard-v001'),'Output directory outside intended scope')
 need(not out.exists() and not reg.exists(),'Choose new snapshot/registration version; preserve prior success/failure')
 files={request_path,report,build,log,dll,R/'UnrealGame/CodexDungeon.uproject',baseline_path,profile_base,native,independent}
 for root in [self_freeze,ext_freeze,production_freeze]+[check(x) for x in q['additional_admitted_candidate_freeze_pins']]:files.update(rows_of_freeze(root))
 # Reuse only actual immutable dependency rows from v135, never its stale live Source/Content/DLL/build rows.
 for row in base['files']:
  if row['path'].startswith(('source-assets/','tools/')):files.add(check(row))
 for x in q['additional_pinned_inputs']:files.add(check(x))
 for key in ['manifest','config','importer','host_RGBA_preflight']:files.add(check(rc[key]))
 cfg=read(resolve(rc['config']['path']))
 for x in cfg.values():
  if type(x) is dict and set(x)=={'path','bytes','sha256'}:files.add(check(x))
 for asset in read(resolve(rc['manifest']['path']))['assets']:files.add(check(dict(path=asset['source'],bytes=asset['source_bytes'],sha256=asset['source_sha256'])))
 for folder in ['UnrealGame/Source','UnrealGame/Config','UnrealGame/Content']:files.update(p for p in (R/folder).rglob('*') if p.is_file())
 sources={p for p in files if p.is_relative_to(R/'UnrealGame/Source')};production={p for p in files if p.is_relative_to(R/'UnrealGame/Content/Production')}
 need(sources and len(production)==1286 and dll.stat().st_mtime>=max(p.stat().st_mtime for p in sources) and report.stat().st_mtime>=dll.stat().st_mtime,'Actual source/DLL/report freshness or Production1286 differs')
 admitted_paths=set(x['path'] for x in prereg['admitted_source_files'])|set(HURT_SOURCES)|set(q['additional_admitted_source_paths'])
 need(all(resolve(n).is_relative_to(R/'UnrealGame/Source') and resolve(n) in sources for n in admitted_paths),'Missing current compiled admitted runtime/observer Source')
 need(HURT_FLAG in '\n'.join(resolve(n).read_text(encoding='utf-8-sig') for n in HURT_SOURCES),'Actual opt-in Hurt implementation absent')
 rows=[pin(p) for p in sorted(files)];actual={x['path']:x for x in rows}
 if a.validate_inputs_only:
  print(json.dumps(dict(compiled_prerequisites_checked=True,strict_registered_tests=187,source_files=len(sources),production_files=1286,source_count_predicted=False,extension_source_preflight_completed=False,outputs_written=False,UE_started=False)));return
 out.mkdir(parents=True);reg.mkdir(parents=True);copied=0
 def io_path(p):return Path('\\\\?\\'+str(p.resolve())) if os.name=='nt' else p
 for row in rows:
  p=resolve(row['path'])
  if not p.is_relative_to(R/'UnrealGame/Content'):
   target=out/'files'/row['path'];target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(io_path(p),io_path(target));copied+=1
 for repeat in range(2):
  for row in rows:
   p=check(row)
   if not p.is_relative_to(R/'UnrealGame/Content'):
    t=out/'files'/row['path'];need(t.stat().st_size==row['bytes'] and sha(t)==row['sha256'],'Snapshot copied bytes changed')
 manifest=dict(version=out.name,strict_registered_tests=187,source_files=len(sources),production_files=1286,full_suite=pin(report),current_build=pin(build),files=rows,source_verification_passes=2,source_hash_mismatches=0,source_config_tools_build_copies=copied,content_packages_pinned_in_place=True,formal_complete_units=0,art_accepted=False)
 manifest_path=out/'compiled-source-manifest.json';write(manifest_path,manifest);stamp=datetime.now(timezone.utc).isoformat()
 approval=read(EXT/'Root-production-extension-Hurt32-TEMPLATE-NOT-APPROVED-v004.json')
 approval.update(is_template=False,RootApproved=True,compiled_manifest_sha256=sha(manifest_path),registered_at_utc=stamp,status='ROOT_ACTUAL_HURT32_IMPORTED_PRODUCTION_EXTENSION_SOURCE_ONLY')
 approval['Hurt_actual_native_import_receipt_pin']=pin(native,True);approval['Hurt_independent_twoSHA_verification_pin']=pin(independent,True)
 approval['baseline_guard_import_receipt_pin']=prereg['actual_native_import_receipt_pin'];approval['baseline_guard_twoSHA_pin']=prereg['independent_import_two_pass_receipt_pin']
 approval_path=reg/'production-extension-Root-approval-Hurt1286-v001.json';write(approval_path,approval)
 prereg.update(is_template=False,pre_registered_before_capture=True,registered_at_utc=stamp,status='ROOT_HURT1286_GUARD_SOURCE_PROFILE_ONLY_NO_NEW_AXE_STUN_DEATH_CAPTURE_CLAIM',compiled_manifest_sha256=sha(manifest_path),strict_registered_tests=187,source_files=len(sources),production_files=1286,production_extension_pin=pin(approval_path,True))
 prereg['admitted_source_files']=[actual[n] for n in sorted(admitted_paths)];profile_path=reg/'guard-known44-source-profile-prereg-Hurt1286-v001.json';write(profile_path,prereg)
 # The unchanged pinned v004 extension checker independently checks actual Source/Guard44/Hurt32 and twoSHA now.
 checker=EXT/'verify-known44-profile-extension-v004.py';runpy.run_path(str(checker))['source_check'](out,profile_path)
 bundle=dict(schema='Hurt1286-Root-manual-input-v001',is_template=False,RootApproved=True,checkpoint_root_request_pin=pin(request_path,True),checkpoint_tooling_freeze_pin=pin(self_freeze,True),snapshot_directory=out.as_posix(),snapshot_manifest_pin=pin(manifest_path,True),source_profile_prereg_pin=pin(profile_path,True),production_extension_approval_pin=pin(approval_path,True),profile_source_checker_pin=pin(checker,True),strict_registered_tests=187,source_files=len(sources),production_files=1286,admitted_Hurt_source_files=[actual[n] for n in HURT_SOURCES],Hurt_flag=HURT_FLAG,Guard_known_unique=44,Hurt_imported_textures=32,automatic_inputs=False,diagnostic_damage=False,new_native_capture_claimed=False,Hurt_runtime_visual_verified=False,actual_preload_finish_receipt=None,actual_runtime_receipt=None,FinalAccepted=False,formal_complete_units=0)
 manual_path=reg/'manual-input-v001.json';write(manual_path,bundle)
 write(reg/'checkpoint-receipt-v001.json',dict(schema='Hurt1286-Root-checkpoint-receipt-v001',source_preflight_passed=True,strict_registered_tests=187,source_files=len(sources),production_files=1286,snapshot_manifest_pin=pin(manifest_path,True),manual_input_pin=pin(manual_path,True),source_count_predicted=False,new_capture_required=False,Hurt_runtime_verified=False,FinalAccepted=False,formal_complete_units=0))
 print(json.dumps(dict(snapshot=out.as_posix(),snapshot_files=len(rows),source_files=len(sources),production_files=1286,strict_registered_tests=187,manual_input=manual_path.as_posix(),source_profile=profile_path.as_posix(),extension_approval=approval_path.as_posix(),new_native_capture_claimed=False,UE_started=False)))
if __name__=='__main__':main()
