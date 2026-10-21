"""Root-only fill helper. Worker did not execute this file. No UE/build/import.

Read actual approved inputs; write one NEW checkpoint, then run the immutable
manual read-only verifier. Existing files and frozen tooling are never edited.
"""
from pathlib import Path
from datetime import datetime,timezone
import argparse,copy,hashlib,json,runpy

R=Path('F:/Ourgame').resolve()
MEDIA=Path('E:/OurGame/Knight/过程图稿与视频').resolve()
C=Path(__file__).resolve().parent.parent
V138=R/'source-assets/production/fairytale-hero-state-gap-v001/death-state-preparation-v001/root-Death1326-checkpoint-v001'
MANUAL_FREEZE_SHA='f93bbb1ade7432341d69e5ef26c6c8d8d9c0a89d422e2a856b5f1dd653c8eb3d'
AUTHORITY={'VisibleShoeSupport':1,'ArtistStandingRootPropagation':2,'ArtistNearSupportDeltaPropagation':3}
HURT_FILES=tuple('UnrealGame/Source/CodexDungeon/'+n for n in ['DungeonHeroHurtProbeV001.h','DungeonHeroHurtProbeV001.cpp','DungeonFairytaleSwordHurtDrawState.h','DungeonFairytaleSwordHurtPresentation.cpp','DungeonFairytaleSwordHurtTextures.inl','DungeonFairytaleSwordHurtPlan.h','DungeonFairytaleSwordHurtPlan.cpp','DungeonFairytaleSwordHurtProfile.h','DungeonFairytaleSwordHurtProfile.cpp','DungeonHUD.h','DungeonHUD.cpp','DungeonFighter.h','DungeonFighter.cpp','Tests/DungeonFairytaleSwordHurtV001Tests.cpp'])
def need(value,why):
 if not value:raise ValueError(why)
def read(path):return json.loads(Path(path).read_text(encoding='utf-8-sig'))
def resolve(path,allow_media=False):
 path=Path(path);path=(path if path.is_absolute() else R/path).resolve();need(path.is_relative_to(R) or (allow_media and path.is_relative_to(MEDIA)),'Input/output escapes project or approved retained media root');return path
def fact(path):
 path=resolve(path,allow_media=True);b=path.read_bytes();return dict(path=path.as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def check(pin):
 need(type(pin)is dict and set(pin)=={'path','bytes','sha256'},'Exact immutable pin required');path=resolve(pin['path'],allow_media=True);actual=fact(path)
 need(actual['bytes']==pin['bytes'] and actual['sha256']==pin['sha256'],'Pinned input differs: '+str(path));return path
def write(path,value):
 with path.open('x',encoding='utf-8',newline='\n') as stream:json.dump(value,stream,ensure_ascii=False,indent=2);stream.write('\n')
def copy_exact(source,destination):
 with destination.open('xb') as stream:stream.write(Path(source).read_bytes())
def source_pins(paths,files):
 need(len(paths)==len(set(paths)),'Required source list repeats a path')
 result=[]
 for name in sorted(paths):need(name in files,'Required compiled source absent: '+name);check(files[name]);result.append(copy.deepcopy(files[name]))
 return result
def normalized_row(row):
 # Preserve the eleven old rows; only map field names/author enum. Do not infer
 # empty Move frames, hidden bones, source pixels or new trial permission.
 clip=row['clip'];out=dict(clip=clip,native_source_id=row['native_source_id'],trial_allowed=row['trial_allowed'],final_accepted=row['final_accepted'],trial_approval_record=row['trial_approval_record'],frames=[])
 if clip=='Move':need(row['frames']==[] and row['trial_allowed']is False,'Move gap was admitted');out['gap_reason']=row['gap_reason'];return out
 if clip=='Dormant':need(row['alias']=='Wake' and row['alias_frame']==0 and row['frames']==[],'Dormant alias changed');out.update(alias_target='Wake',alias_frame=0,alias_evidence=copy.deepcopy(row['alias_evidence']));return out
 out.update(canvas=copy.deepcopy(row['canvas_source_px']),standing_extent=row['standing_body_extent_px'],target_body_height=row['target_standing_body_height_px'],registration_evidence=copy.deepcopy(row['registration_evidence']),source_index=copy.deepcopy(row['source_index']))
 for frame in row['frames']:
  need(frame['pivot_authority'] in AUTHORITY,'Unknown artist/measured pivot authority')
  out['frames'].append(dict(frame=frame['frame'],object_path=frame['object_path'],source=copy.deepcopy(frame['source']),RGBA_sha256=frame['RGBA_sha256'],floor_pivot=copy.deepcopy(frame['floor_pivot_source_px']),pivot_authority=AUTHORITY[frame['pivot_authority']]))
 return out
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--snapshot',required=True);parser.add_argument('--full-suite',required=True);parser.add_argument('--source-rows',required=True);parser.add_argument('--import-manifest',required=True);parser.add_argument('--native-import',required=True);parser.add_argument('--independent-import',required=True);parser.add_argument('--data-admission',required=True);parser.add_argument('--output-dir',default='source-assets/production/fairytale-guard-v001/root-Stomp1332-checkpoint-v001');args=parser.parse_args()
 out=resolve(args.output_dir);need(not out.exists(),'Never overwrite a previous Root checkpoint')
 own=C/'Stomp50-manual-tooling-freeze-v001.json';need(fact(own)['sha256']==MANUAL_FREEZE_SHA,'Frozen manual candidate changed')
 for entry in read(own)['files']:check(entry)
 manual_api=runpy.run_path(str(C/'verify-Stomp1332-manual-input-v001.py'));scope=manual_api['adapter']();extension_api=runpy.run_path(str(C/'validate-Stomp1332-production-extension-v001.py'))
 immutable=read(C/'immutable-v009-input-pins-v001.json')
 snapshot=resolve(args.snapshot);manifest_path=snapshot/'compiled-source-manifest.json';cm=read(manifest_path);files={x['path'].replace('\\','/'):x for x in cm['files']};need(len(files)==len(cm['files']),'Snapshot duplicates files')
 need(cm['strict_registered_tests']==193 and cm['production_files']==1332 and cm['source_verification_passes']==2 and cm['source_hash_mismatches']==0,'Actual fresh193/1332/twoSHA0 required')
 source_set={x for x in files if x.startswith('UnrealGame/Source/')};content_set={x for x in files if x.startswith('UnrealGame/Content/Production/')};need(cm['source_files']==len(source_set) and len(content_set)==1332,'Actual snapshot counts differ')
 for path,pin in files.items():check(pin)
 suite_path=resolve(args.full_suite);need(check(cm['full_suite'])==suite_path,'Explicit full193 does not match selected snapshot');suite=read(suite_path);scope['strict_suite'](suite);manual_api['required_stomp'](suite)
 prior=read(check(immutable['prior190_full_suite_pin']));need({x['fullTestPath'] for x in suite['tests']}=={x['fullTestPath'] for x in prior['tests']}|set(manual_api['STOMP_TESTS']),'Fresh193 omitted/replaced an old190 target')
 build=read(check(cm['current_build']));need(build['ExitCode']==0 and build['Target']=='CodexDungeonEditor','Actual successful Editor build required')
 dll_path='UnrealGame/Binaries/Win64/UnrealEditor-CodexDungeon.dll';need(dll_path in files,'Compiled current DLL absent');check(files[dll_path])
 approved_path=resolve(args.source_rows);approved=read(approved_path);need(approved['schema']=='Root-GuardStomp6-preimport-source-rows-v001' and approved['RootApproved']is True and approved['FinalAccepted']is False,'Actual Root approved preimport source rows required')
 approved_rows=approved['rows'];need([x['clip'] for x in approved_rows]==['StompActive','StompRecovery'] and [len(x['frames']) for x in approved_rows]==[2,4],'Only actual approvedA2/R4 allowed')
 im_path=resolve(args.import_manifest);im=read(im_path);native_path=resolve(args.native_import);native=read(native_path);ind_path=resolve(args.independent_import);ind=read(ind_path)
 need(im['schema']=='Root-GuardStomp6-import-v001' and im['namespace']=='/Game/Production/FirstBatch/GuardWhole_stomp_v004' and (im['expected_old_count'],im['expected_new_count'],im['expected_final_count'])==(1326,6,1332),'Wrong actual import scope')
 trial_path=check(im['root_trial_registration']);trial=read(trial_path);need(trial['RootApproved']is True and trial['is_template']is False and trial['limited_import_approved']is True and trial['FinalAccepted']is False,'Actual limited Root import approval absent')
 need(check(trial['source_fit_approval'])==approved_path and trial['source_manifest']==im['source_manifest'],'Actual import approval binds another source decision')
 sm=read(check(im['source_manifest']));need(sm['schema']=='GuardStomp6-selected-source-manifest-v001' and check(sm['Root_source_approval'])==approved_path and sm['rows']==approved_rows and sm['assets']==im['assets'],'Prepared source manifest is not exact approved rows/assets')
 need(native['schema']=='guard-Stomp6-actual-import-v001' and native['success']is True and native['actual_total']==1332 and native['manifest']==fact(im_path),'Actual successful native six import required; no handfilled success')
 need(ind['schema']=='Stomp6-independent-import-twoSHA-v001' and ind['success']is True and ind['verification_passes']==2 and ind['hash_mismatches']==0 and ind['old1326_unchanged_twice']is True and ind['new6_saved_twice']is True and ind['exact_total']==1332 and ind['manifest']==fact(im_path) and ind['receipt']==fact(native_path),'Actual independent old/new twoSHA result required')
 check(native['importer']);need(len(im['assets'])==len(native['assets'])==6,'Exact six assets required')
 data_path=resolve(args.data_admission);data=read(data_path);scope['approval'](data);need(data['schema']=='Root-GuardStomp-approved-Data-admission-v001' and data['success']is True and data['FinalAccepted']is False,'Actual oneData Root admission required')
 manual_api['controlled_source'](scope,dict(stage0_Source_admission_pin=immutable['stage0_Source_admission_pin'],observer_Source_admission_pin=immutable['observer_Source_admission_pin'],approved_Data_Source_admission_pin=fact(data_path)),files)
 # All RootApproved output values are now justified by actual approved rows,
 # actual native receipts, actual193GREEN and current controlled Source facts.
 now=datetime.now(timezone.utc).isoformat();rows=copy.deepcopy(approved_rows)
 overlay=read(C/'Root-Stomp50-overlay-rows-TEMPLATE-NOT-APPROVED-v001.json');overlay.update(is_template=False,RootApproved=True,compiled_manifest_sha256=fact(manifest_path)['sha256'],native_import_trial_record_pin=copy.deepcopy(im['root_trial_registration']),source_manifest_pin=copy.deepcopy(im['source_manifest']),rows=rows,registered_at_utc=now)
 overlay.pop('frame_fact_shape_NOT_AN_APPROVED_FRAME',None);manual_api['overlay_rows'](overlay)
 for row in rows:
  for key in ['registration_evidence','source_index','Root_source_fit_approval','E_retention_index']:check(row[key])
  retained=read(check(row['E_retention_index']));need(retained['verification_passes']==2 and retained['source_and_target_hash_mismatches']==0,'Actual source F/E retention proof differs')
  for frame in row['frames']:extension_api['source'](frame)
 old_profile_path=V138/'guard-known44-source-profile-prereg-Death1326-v001.json';old_profile=read(old_profile_path);old_manual=read(V138/'manual-input-v001.json')
 check(old_manual['source_profile_prereg_pin']);need(check(old_manual['source_profile_prereg_pin'])==old_profile_path,'Oldv138 source profile provenance differs')
 allrows=copy.deepcopy(old_profile['all_profile_rows']);need(len(allrows)==13 and sum(len(x['frames']) for x in allrows)==44,'Old44 source facts changed')
 added={x['clip']:x for x in rows};native_rows=[normalized_row(added.get(x['clip'],x)) for x in allrows];need(len(native_rows)==13 and sum(len(x['frames']) for x in native_rows)==50,'Normalized profile is not exact44+6')
 native_profile=dict(schema='Root-GuardStomp50-profile-contract-v001',is_template=False,RootApproved=True,profile_id='GuardStomp50V004',source_count=50,logical_budget=57,rows=native_rows,FinalAccepted=False,source_preimport_approval_pin=fact(approved_path),actual_import_manifest_pin=fact(im_path),registered_at_utc=now)
 output_names=dict(manual='manual-input-v001.json',extension='production-extension-Root-approval-Stomp1332-v001.json',overlay='Stomp50-overlay-Root-approval-v001.json',data_copy='Root-approved-Data-admission-actual-copy-v001.json',import_copy='Root-Stomp6-import-manifest-actual-copy-v001.json',known44='guard-known44-source-profile-prereg-Stomp1332-v001.json',profile50='Native-Stomp50-profile-contract-v001.json')
 extension=read(C/'Root-Stomp1332-production-extension-TEMPLATE-NOT-APPROVED-v001.json');extension.update(is_template=False,RootApproved=True,compiled_manifest_sha256=fact(manifest_path)['sha256'],Stomp6_import_manifest_pin=fact(im_path),Stomp6_actual_receipt_pin=fact(native_path),Stomp6_independent_twoSHA_pin=fact(ind_path),actual_receipt_schema=native['schema'],registered_at_utc=now);extension.pop('fill_instructions',None)
 manual=read(C/'Root-Stomp1332-manual-input-TEMPLATE-NOT-APPROVED-v001.json');manual.update(is_template=False,RootApproved=True,snapshot_directory=snapshot.as_posix(),snapshot_manifest_pin=fact(manifest_path),checkpoint_tooling_freeze_pin=fact(own),full_suite_pin=copy.deepcopy(cm['full_suite']),last_build_pin=copy.deepcopy(cm['current_build']),DLL_pin=copy.deepcopy(files[dll_path]),strict_registered_tests=cm['strict_registered_tests'],source_files=cm['source_files'],production_files=cm['production_files'],approved_Data_Source_admission_pin=fact(data_path),registered_at_utc=now)
 for key in ['Death_runtime_candidate_freeze_pin','Death_observer_candidate_freeze_pin','candidate_source_admissions']:manual[key]=copy.deepcopy(old_manual[key])
 manual['admitted_Death_source_files']=source_pins(scope['DEATH_FILES'],files);manual['admitted_Hurt_source_files']=source_pins(HURT_FILES,files);manual['admitted_Stomp_source_files']=source_pins(manual_api['NEW_SOURCE'],files);manual.pop('fill_instructions',None)
 known44=copy.deepcopy(old_profile);known44.update(compiled_manifest_sha256=fact(manifest_path)['sha256'],strict_registered_tests=193,source_files=cm['source_files'],production_files=1332,registered_at_utc=now,status='MANUAL_SOURCE_ONLY_REBIND_NO_NATIVE_CAPTURE_CLAIM')
 known44.pop('fill_instructions',None);known44['scope']='Fresh manual193/1332 Source-only rebind: original44 facts unchanged; newStomp6 belongs to separate50 overlay; no newAxe/Stun/Death capture claim.'
 known44['admitted_source_files']=source_pins({x['path'] for x in old_profile['admitted_source_files']}|set(manual_api['NEW_SOURCE'])|set(HURT_FILES)|set(scope['DEATH_FILES']),files)
 known44['manual_checkpoint_rebinding']=dict(previous_profile_pin=fact(old_profile_path),controlled_admission_pins=[copy.deepcopy(immutable['stage0_Source_admission_pin']),copy.deepcopy(immutable['observer_Source_admission_pin']),fact(data_path)],old44_profile_facts_unchanged=True,old13_all_profile_rows_unchanged=True,new_overlay_kept_separate=True,new_native_capture_claimed=False)
 need(known44['profile_facts']==old_profile['profile_facts'] and known44['all_profile_rows']==old_profile['all_profile_rows'],'Old44 facts were altered')
 # No directory or outputs exist until the genuine input gates above passed.
 out.mkdir(parents=True,exist_ok=False)
 passed=False;failure=''
 try:
  write(out/output_names['overlay'],overlay);overlay_pin=fact(out/output_names['overlay']);extension['Stomp50_row_approval_pin']=overlay_pin
  write(out/output_names['extension'],extension);extension_pin=fact(out/output_names['extension']);known44['production_extension_pin']=extension_pin
  write(out/output_names['known44'],known44);write(out/output_names['profile50'],native_profile)
  copy_exact(data_path,out/output_names['data_copy']);copy_exact(im_path,out/output_names['import_copy'])
  manual.update(Stomp50_row_approval_pin=overlay_pin,production_extension_approval_pin=extension_pin,source_profile_prereg_pin=fact(out/output_names['known44']))
  write(out/output_names['manual'],manual)
  # This calls the immutable f93bbb manual checker, including exact Source
  # admissions, all193 targets, metadata/import13rows and live twoSHA checks.
  verified=manual_api['verify'](out/output_names['manual'],snapshot);passed=True
 except Exception as error:
  failure=str(error);raise
 finally:
  receipt=dict(schema='Root-Stomp1332-checkpoint-preparation-v001',success=passed,failure=failure,input_pins=dict(snapshot=fact(manifest_path),full193=fact(suite_path),approved_source_rows=fact(approved_path),import_manifest=fact(im_path),actual_native_import=fact(native_path),actual_independent_import=fact(ind_path),actual_Data_admission=fact(data_path)),manual_tooling_freeze_pin=fact(own),output_pins=[fact(x) for x in sorted(out.iterdir()) if x.is_file()],UE_started=False,automatic_inputs=False,diagnostic_damage=False,new_native_capture_claimed=False,FinalAccepted=False)
  write(out/'preparation-receipt-v001.json',receipt)
 print(json.dumps(dict(success=True,manual_input=fact(out/output_names['manual']),Native_Stomp50_profile_contract=fact(out/output_names['profile50']),strict_registry=193,source_files=cm['source_files'],production_files=1332,UE_started=False),ensure_ascii=False))
if __name__=='__main__':main()
