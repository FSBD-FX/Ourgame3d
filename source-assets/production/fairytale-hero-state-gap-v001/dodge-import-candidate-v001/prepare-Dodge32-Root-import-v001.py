"""Root-only import preparation. --validate-only writes nothing and starts no UE."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,json
from dodge32_import_contract_v001 import ROOT,NAMESPACE,read,pin,need,load_sources,verify_old,exact_membership

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--old-snapshot',required=True)
    parser.add_argument('--output-dir',default=str(ROOT/'source-assets/production/fairytale-hero-state-gap-v001/dodge-state-preparation-v001/Root-Dodge32-import-v001'))
    parser.add_argument('--validate-only',action='store_true')
    parser.add_argument('--approve-limited-import',action='store_true')
    args=parser.parse_args()
    snapshot=Path(args.old_snapshot).resolve()
    if snapshot.is_dir():snapshot=snapshot/'compiled-source-manifest.json'
    baseline=read(snapshot);old=[x for x in baseline['files'] if x['path'].startswith('UnrealGame/Content/Production/')]
    need(baseline['production_files']==1332,'Fresh frozen1332 Production baseline required')
    assets,inputs,review,prepared=load_sources()
    manifest=dict(schema='Root-Dodge32-native-import-v001',expected_old_count=1332,expected_new_count=32,
        expected_final_count=1364,namespace=NAMESPACE,replace_existing=False,
        source_manifest=inputs['files']['prepared_manifest'],candidate_freeze=inputs['files']['prepared_freeze'],
        Root_source_review=inputs['files']['Root_after_E510_review'],old_compiled_snapshot=pin(snapshot),
        old_production_files=old,assets=assets,source_closure_digest=prepared['source_closure_digest'],
        source32_RGBA512_host_verified=True,runtime_verified=False,TrialAllowed=False,FinalAccepted=False)
    verify_old(old);verify_old(old);exact_membership(manifest,False)
    need(all(not Path(x['saved_path']).exists() for x in assets),'Never replace existing saved package')
    if args.validate_only:
        print(json.dumps(dict(schema='Dodge32-import-preflight-v001',success=True,source32_RGBA512=True,
            body20_E502=True,armor12_E510=True,old1332_unchanged_twice=True,expected_total_after_import=1364,
            outputs_written=False,UE_started=False,runtime_verified=False,FinalAccepted=False)));return
    need(args.approve_limited_import,'Root must explicitly pass --approve-limited-import before creating import approval')
    out=Path(args.output_dir).resolve();need(out.is_relative_to(ROOT/'source-assets/production'),'Root output must stay in production source-assets')
    need(not out.exists(),'New output directory required; no overwrite')
    out.mkdir(parents=True)
    trial=dict(schema='Root-Dodge32-limited-import-trial-v001',utc=datetime.now(timezone.utc).isoformat(),
        RootApproved=True,is_template=False,limited_import_approved=True,approval_method='Root CLI --approve-limited-import',
        source_manifest=manifest['source_manifest'],candidate_freeze=manifest['candidate_freeze'],Root_source_review=manifest['Root_source_review'],
        scope='Save exact32 into empty v018 HeroLeatherDodge namespace; preserve1332 old packages; finite native preparation only',
        sourcefit_completely_accepted=False,geometry_risks_preserved=True,actual_import_completed=False,
        runtime_verified=False,TrialAllowed=False,FinalAccepted=False,formal_complete_units=0)
    trial_path=out/'Root-Dodge32-limited-import-trial-v001.json'
    with trial_path.open('x',encoding='utf-8',newline='\n') as f:json.dump(trial,f,ensure_ascii=False,indent=2);f.write('\n')
    manifest['root_trial_registration']=pin(trial_path)
    manifest_path=out/'import-manifest.json'
    with manifest_path.open('x',encoding='utf-8',newline='\n') as f:json.dump(manifest,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps(dict(success=True,manifest=pin(manifest_path),import_started=False,runtime_verified=False,FinalAccepted=False)))

if __name__=='__main__':main()
