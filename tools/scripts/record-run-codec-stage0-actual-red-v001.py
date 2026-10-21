"""Actual completed semantic RED is distinct from prior compile/oracle defects."""
from pathlib import Path
import hashlib,json
R=Path('F:/Ourgame');D=R/'docs/production/first-batch-v2';E=D/'evidence/run-codec-v001'
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def desc(p):
 b=p.read_bytes();return {'path':p.as_posix(),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def new(p,v):
 assert not p.exists(),p
 p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
report=R/'UnrealGame/Saved/Automation/FirstRoom-20261016-123141/index.json';r=load(report)
assert (r['succeeded'],r['failed'],r['notRun'],r['inProcess'])==(0,4,0,0)
assert len(r['tests'])==4 and all(t['warnings']==0 and t['state']=='Fail' for t in r['tests'])
assert sum(t['errors'] for t in r['tests'])==9
snap=R/'source-assets/production/backups/2026-10-16_RunCodecStage0-actual4RED-v102';m=load(snap/'compiled-source-manifest.json')
for row in m['files']:
 actual=desc(snap/row['path']);assert actual['bytes']==row['bytes'] and actual['sha256']==row['sha256'],row['path']
old=load(R/'source-assets/production/backups/2026-10-16_SwordReadyArmor24-preloadFix-actual126GREEN-v101/compiled-source-manifest.json')
tests=[x for x in old['files'] if x['path'].startswith('UnrealGame/Source/CodexDungeon/Tests/')]
for x in tests:
 a=desc(R/x['path']);assert a['bytes']==x['bytes'] and a['sha256']==x['sha256']
proof={'build':desc(R/'UnrealGame/Saved/Bootstrap/build-editor-20261016-122948.log'),'build_exit':0,'actual_report':desc(report),
 'filter':'CodexDungeon.Content.RunCodec','actual_tests':4,'failed':4,'succeeded':0,'not_run':0,'in_process':0,'warnings':0,'semantic_error_count':9,
 'positive_fixture_and_negative_premise_failures':0,'reason':'All errors are honest unimplemented Encode/Decode positive-control or mandatory Store Decode callback; prior C4456 and test numeric-oracle crash are separately retained, not counted as semanticRED',
 'compiled_source_snapshot':desc(snap/'compiled-source-manifest.json'),'snapshot_files_checked':len(m['files']),'snapshot_bytes':m['bytes'],'immutable_snapshot_hash_mismatches':0,
 'prior_test_source_files_unchanged':len(tests),'new_production_implementation_authorized_after_actual_RED':True,'root_HUD_preview_changes_after_snapshot':True,'current_working_source_compiled':False,'disk_continue_complete':False,'formal_complete_units':0}
new(E/'actual4-semanticRED-v102-audit-v001.json',proof)
p=D/'progress.json';d=load(p)
d.update(current_build='UnrealGame/Saved/Bootstrap/build-editor-20261016-122948.log',current_build_exit_code=0,
 current_compiled_snapshot=snap.relative_to(R).as_posix(),ue_current_working_source_compiled=False,ue_current_working_source_verified=False,
 current_source_uncompiled_changes='After actual v102 four semanticRED: production Codec under implementation plus new opt-in Ready4/Primary1six HUD armor presentation. No new compiled test/render validation yet.',
 next_snapshot='v103',next_retention_batch='E180',next_native_request=168)
d['last_full_UE_automation_before_new_codec_stage0']=d['latest_strict_UE_automation']
d['latest_strict_UE_automation']={'report':report.relative_to(R).as_posix(),'filter':'CodexDungeon.Content.RunCodec','registered_in_filter':4,'succeeded':0,'failed':4,'notRun':0,'inProcess':0,'warnings':0,'scope':'Actual complete four-group expected semanticRED against honest unimplemented Codec; prior126 fullGREEN is historical, no current full130 claim','formal_complete_units':0}
d['run_codec_current_v001']={'stage0_freeze':'stage0-v003','compile0':True,'actual_semantic_RED':4,'snapshot':'v102','immutable_snapshot_audit':desc(E/'actual4-semanticRED-v102-audit-v001.json'),'production_implementation_in_progress':True,'Store_semantic_live_adapter_bound':False,'new_process_Continue_complete':False,'formal_complete_units':0}
d['fairytale_sword_primary1_armor_current_v001'].update(standard_derived_sources=[164,165,167],source_derived_retention=['E178','E179'],old_native167_30x28_QA='RED495<512 preserved',new_native167_whole_row_extent=[32,30],QA_thresholds_changed=False,source_frames_root_viewed=18,HUD_optin_wiring_written_uncompiled=True,new_Texture2Ds_imported=0)
p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(proof,ensure_ascii=False))
