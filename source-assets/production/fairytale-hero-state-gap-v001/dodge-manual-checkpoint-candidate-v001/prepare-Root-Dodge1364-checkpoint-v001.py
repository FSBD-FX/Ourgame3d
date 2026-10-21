"""Root fill helper: actual196/1364 and bounded admissions only; no UE/build/import."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,copy,json,importlib.util
from dodge_manual_contract_v001 import *

def write(p,v):
 with p.open('x',encoding='utf-8',newline='\n') as f:json.dump(v,f,ensure_ascii=False,indent=2);f.write('\n')
def current_pins(names,files):
 need(len(names)==len(set(names)),'Repeated source name')
 for n in names:need(n in files,'Required Source absent: '+n);check(files[n])
 return [copy.deepcopy(files[n]) for n in sorted(names)]

def main():
 ap=argparse.ArgumentParser()
 for name in ['snapshot','full-suite','stage0-admission','production-admission','observer-admission','import-manifest','native-import','independent-import']:ap.add_argument('--'+name,required=True)
 ap.add_argument('--approve-limited-runtime',action='store_true')
 ap.add_argument('--output-dir',default='source-assets/production/fairytale-hero-state-gap-v001/root-Dodge1364-checkpoint-v001')
 args=ap.parse_args();need(args.approve_limited_runtime,'Root must explicitly approve source-only limited runtime trial')
 deps=inputs();own=HERE/'Dodge1364-manual-tooling-freeze-v001.json';frozen(own)
 snapshot=resolve(args.snapshot);mp=snapshot/'compiled-source-manifest.json';cm=read(mp);files={x['path']:x for x in cm['files']}
 need(len(files)==len(cm['files']) and cm['strict_registered_tests']==196 and cm['production_files']==1364 and cm['source_verification_passes']==2 and cm['source_hash_mismatches']==0,'Fresh actual196/1364/twoSHA0 required')
 need(cm['source_files']==len([n for n in files if n.startswith('UnrealGame/Source/')]),'Dynamic Source count differs')
 for x in files.values():check(x)
 full=resolve(args.full_suite);need(check(cm['full_suite'])==full,'Explicit196 report does not match selected snapshot')
 old_suite=read(check(deps['base193_full_suite']));preserve193(read(full),{x['fullTestPath'] for x in old_suite['tests']},set(DODGE_TESTS))
 build=read(check(cm['current_build']));need(build['ExitCode']==0 and build['Target']=='CodexDungeonEditor','Actual successful Editor build required')
 old=read(check(deps['v139_manual']));m=copy.deepcopy(old)
 for role in ['stage0','production','observer']:m['Dodge_'+role+'_Source_admission_pin']=pin(resolve(getattr(args,role+'_admission')))
 source_chain(m,files)
 ip=pin(resolve(args.import_manifest));np=pin(resolve(args.native_import));vp=pin(resolve(args.independent_import))
 now=datetime.now(timezone.utc).isoformat();compiled_sha=pin(mp)['sha256']
 ext=dict(schema='Dodge1364-Root-production-extension-v001',is_template=False,RootApproved=True,
  compiled_manifest_sha256=compiled_sha,expected_old_base=1332,expected_new_count=32,expected_total=1364,
  base_Stomp1332_approval_pin=copy.deepcopy(old['production_extension_approval_pin']),
  Dodge32_import_manifest_pin=ip,Dodge32_native_receipt_pin=np,Dodge32_independent_twoSHA_pin=vp,
  automatic_inputs=False,diagnostic_damage=False,FinalAccepted=False,registered_at_utc=now)
 # Validate actual import/current1364 and the original Hurt/Death/Stomp gates
 # before creating any approved output directory.
 spec=importlib.util.spec_from_file_location('Dodge_extension_fill',HERE/'validate-Dodge1364-production-extension-v001.py');extension=importlib.util.module_from_spec(spec);spec.loader.exec_module(extension)
 # The callback accepts a real approval file; use a read-only preflight
 # overload so no temporary RootApproved file has to be invented.
 extension.validate_document(ext,files,old,compiled_sha)
 production_receipt=read(check(m['Dodge_production_Source_admission_pin']))
 trial=dict(schema='Root-Dodge33-runtime-trial-registration-v001',is_template=False,RootApproved=True,TrialAllowed=True,
  FinalAccepted=False,compiled_manifest_sha256=compiled_sha,flag='DungeonFairytaleSwordDodgePreview',
  profile_id='EV048-v018-HeroLeatherDodge-v001',prepared_profile_pin=copy.deepcopy(deps['Dodge_prepared_profile']),
  Dodge32_import_manifest_pin=ip,Dodge32_native_receipt_pin=np,Dodge32_independent_twoSHA_pin=vp,
  runtime_candidate_freeze_pin=copy.deepcopy(production_receipt['candidate_freeze']),resource_preload_total=33,
  declared_draw_slots=9,manual_source_only=True,actual_GPU_preload_receipt=None,native_or_visual_acceptance=False,
  approval_method='Root CLI --approve-limited-runtime after fresh196 and boundedSource checks',registered_at_utc=now)
 overlay=copy.deepcopy(read(check(old['Stomp50_row_approval_pin'])));overlay.update(compiled_manifest_sha256=compiled_sha,registered_at_utc=now)
 prereg=copy.deepcopy(read(check(old['source_profile_prereg_pin'])));prereg.update(compiled_manifest_sha256=compiled_sha,
  strict_registered_tests=196,source_files=cm['source_files'],production_files=1364,registered_at_utc=now,
  status='MANUAL_SOURCE_ONLY_DODGE_REBIND_NO_NATIVE_CAPTURE_CLAIM')
 needed={x['path'] for x in prereg['admitted_source_files']}|STAGE_NEW|PROD_NEW|OBSERVER_NEW|COMMON
 prereg['admitted_source_files']=current_pins(needed,files)
 m.update(schema='Dodge1364-Root-manual-input-v001',is_template=False,RootApproved=True,snapshot_directory=snapshot.as_posix(),
  snapshot_manifest_pin=pin(mp),checkpoint_tooling_freeze_pin=pin(own),full_suite_pin=copy.deepcopy(cm['full_suite']),
  last_build_pin=copy.deepcopy(cm['current_build']),DLL_pin=copy.deepcopy(files['UnrealGame/Binaries/Win64/UnrealEditor-CodexDungeon.dll']),
  strict_registered_tests=196,source_files=cm['source_files'],production_files=1364,
  production_extension_checker_pin=pin(HERE/'validate-Dodge1364-production-extension-v001.py'),Dodge_imported_textures=32,
  Dodge_preload_total=33,Dodge_flag='DungeonFairytaleSwordDodgePreview',registered_at_utc=now)
 for key in ['admitted_Death_source_files','admitted_Hurt_source_files','admitted_Stomp_source_files']:m[key]=current_pins({x['path'] for x in old[key]},files)
 m['admitted_Dodge_source_files']=current_pins(STAGE_NEW|PROD_NEW|OBSERVER_NEW|COMMON,files)
 out=resolve(args.output_dir);need(not out.exists(),'New output directory required; no overwrite');out.mkdir(parents=True)
 passed=False;failure=''
 try:
  write(out/'Dodge33-runtime-Root-trial-registration-v001.json',trial);m['Dodge_runtime_trial_registration_pin']=pin(out/'Dodge33-runtime-Root-trial-registration-v001.json')
  write(out/'Stomp50-overlay-source-rebind-v011.json',overlay);m['Stomp50_row_approval_pin']=pin(out/'Stomp50-overlay-source-rebind-v011.json');ext['Stomp50_row_approval_pin']=m['Stomp50_row_approval_pin']
  write(out/'production-extension-Root-approval-Dodge1364-v001.json',ext);ep=pin(out/'production-extension-Root-approval-Dodge1364-v001.json');prereg['production_extension_pin']=ep;m['production_extension_approval_pin']=ep
  write(out/'guard-known44-source-profile-prereg-Dodge1364-v001.json',prereg);m['source_profile_prereg_pin']=pin(out/'guard-known44-source-profile-prereg-Dodge1364-v001.json')
  write(out/'manual-input-v001.json',m)
  api=runpy.run_path(str(HERE/'verify-Dodge1364-manual-input-v001.py'));result=api['verify'](out/'manual-input-v001.json',snapshot);passed=True
 except Exception as error:failure=str(error);raise
 finally:
  write(out/'preparation-receipt-v001.json',dict(schema='Root-Dodge1364-checkpoint-preparation-v001',success=passed,failure=failure,
   snapshot=pin(mp),full196=pin(full),actual_import_manifest=ip,actual_native_import=np,actual_independent_import=vp,
   source_admissions={r:m['Dodge_'+r+'_Source_admission_pin'] for r in ['stage0','production','observer']},
   outputs=[pin(p) for p in sorted(out.iterdir()) if p.is_file()],UE_started=False,automatic_inputs=False,
   diagnostic_damage=False,new_native_capture_claimed=False,FinalAccepted=False))
 print(json.dumps(dict(success=True,manual_input=pin(out/'manual-input-v001.json'),strict_registry=196,source_files=cm['source_files'],production_files=1364,UE_started=False)))
if __name__=='__main__':main()
