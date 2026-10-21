"""Prepare a bounded manifest only. Default validates; approval output always rejects."""
from pathlib import Path
import argparse,json
from move7_import_contract_v001 import *

def main():
 p=argparse.ArgumentParser();p.add_argument('--old-snapshot',required=True);p.add_argument('--output-dir');p.add_argument('--write-prepared',action='store_true');p.add_argument('--validate-only',action='store_true');a=p.parse_args()
 old,inputs=old_contracts();snapshot=resolve(a.old_snapshot)
 if snapshot.is_dir():snapshot=snapshot/'compiled-source-manifest.json'
 need(pin(snapshot)==inputs['old_compiled_snapshot'],'Only actual v140-Dodge196G baseline accepted')
 assets,_,review,digest=load_sources();m=dict(schema='Root-GuardMove7-native-import-v001',presentation_type=TYPE,expected_old_count=1364,expected_new_count=7,expected_final_count=1371,namespace=NAMESPACE,replace_existing=False,old_compiled_snapshot=inputs['old_compiled_snapshot'],old_production_files=old,source_table_pin=inputs['source7_surface18'],Root_source_review_pin=inputs['Root_preparation_review'],historical_Dodge_and_Guard_contract_pins={k:inputs[k]for k in ['old_manual_input','old_production_extension','old_Guard_known44_prereg','old_Guard_Stomp50_approval','Dodge32_import_manifest_pin','Dodge32_native_receipt_pin','Dodge32_independent_twoSHA_pin']},source_closure_digest=digest,assets=assets,source7_RGBA512_host_verified=True,component_owner_native_batches=[252,250,251],derived_rig_has_whole_body_native_source_id=False,runtime_verified=False,TrialAllowed=False,FinalAccepted=False)
 validate_layout(m);verify_old(old);verify_old(old);exact_membership(m,False);need(all(not Path(x['saved_path']).exists()for x in assets),'Never replace an existing package')
 if a.validate_only or not a.write_prepared:
  print(json.dumps(dict(schema='GuardMove7-import-source-preflight-v001',success=True,source7_RGBA512_verified=True,E565_E553_E556_members_verified_twice=True,old1364_exactset_unchanged_twice=True,expected_final_count=1371,RootApproved=False,outputs_written=False,UE_started=False,runtime_verified=False,TrialAllowed=False,FinalAccepted=False)));return
 need(a.output_dir,'NEW explicit prepared output directory required');out=resolve(a.output_dir);need(out.is_relative_to(ROOT/'source-assets/production')and not out.exists(),'New production source-assets output required, never overwrite')
 freeze=HERE/'Move7-import-candidate-freeze-v001.json';frozen(freeze);m['import_tool_candidate_freeze']=pin(freeze);out.mkdir(parents=True)
 target=out/'import-manifest.json'
 with target.open('x',encoding='utf-8')as f:json.dump(m,f,ensure_ascii=False,indent=2);f.write('\n')
 template=dict(schema='Root-GuardMove7-limited-import-approval-v001',is_template=True,RootApproved=False,limited_import_approved=False,approval_method='PENDING_ROOT_CLI',manifest_pin=pin(target),source_closure_digest=digest,Root_source_review_pin=m['Root_source_review_pin'],expected_old_count=1364,expected_new_count=7,expected_final_count=1371,replace_existing=False,TrialAllowed=False,RuntimeTrialAllowed=False,FinalAccepted=False,actual_import_completed=False,formal_complete_units=0)
 with(out/'Root-limited-import-approval-TEMPLATE-v001.json').open('x',encoding='utf-8')as f:json.dump(template,f,ensure_ascii=False,indent=2);f.write('\n')
 print(json.dumps(dict(manifest=pin(target),RootApproved=False,approval_template_rejects=True,UE_started=False,import_started=False,FinalAccepted=False)))
if __name__=='__main__':main()
