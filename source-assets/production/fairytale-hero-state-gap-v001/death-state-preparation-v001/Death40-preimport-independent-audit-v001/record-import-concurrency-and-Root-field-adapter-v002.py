"""Append-only clarification: Root import started before strict preimport audit completed."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,sys
ROOT=Path('F:/Ourgame');OUT=Path(__file__).resolve().parent
assert Path(sys.executable).resolve()==(ROOT/'tools/runtime/asset-gen/Scripts/python.exe').resolve()
def pin(p):
 p=Path(p);b=p.read_bytes();return {'path':p.as_posix(),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(name,v):
 p=OUT/name
 with p.open('x',encoding='utf-8',newline='\n') as f:json.dump(v,f,ensure_ascii=False,indent=2);f.write('\n')
 return p
ORIGINAL=OUT/'Death40-preimport-independent-audit-report-v001.json';OLD_FREEZE=OUT/'independent-audit-freeze-v001.json';r=read(ORIGINAL)
AUTHOR=ROOT/'source-assets/production/fairytale-hero-state-gap-v001/death-state-preparation-v001/Death40-native-ready-author-candidate-v002/Death40-source-manifest-author-candidate-v002.json';author=read(AUTHOR)
MAN=ROOT/'source-assets/production/fairytale-hero-state-gap-v001/death-state-preparation-v001/Root-Death40-import-v001/import-manifest.json';m=read(MAN)
IMPORTER=ROOT/'tools/scripts/ue-import-hero-Death40-v001.py'
assert pin(MAN)['sha256']=='37571e6b149c74a6468bac9fb93f2971652af10f35f68333c3356fabcf50bb82'
scope_errors=[e for e in r['errors'] if not(e.startswith('Target package already exists: ')or e=='v019 target namespace not absent/empty'or e.startswith('CurrentProduction1286 mismatch pass'))]
assert not scope_errors
assert len(r['source_rows'])==40 and r['counts']['nonempty40'] and r['counts']['E505_exact40']
assert r['baseline_production1286']['lineage_matches_compiledv137']
passes=r['baseline_production1286']['twoSHA_passes'];assert all(not p['missing'] and not p['changed'] for p in passes)
assert all(p['current_file_count']==1326 and len(p['extra'])==40 for p in passes)
assert passes[0]['inventory_digest']==passes[1]['inventory_digest']
assert (m['expected_old_count'],m['expected_new_count'],m['expected_final_count'])==(1286,40,1326)
assert m['namespace']==author['namespace'] and len(m['assets'])==40
assert m['source_manifest']==pin(AUTHOR) and m['candidate_freeze']==r['inputs']['native_ready_freeze']
a={(x['component'],x['frame']):x for x in author['assets']};maps=[]
for x in m['assets']:
 y=a[x['component'],x['frame']];assert x['source']=={'path':y['source'],'bytes':y['source_bytes'],'sha256':y['source_sha256']}
 assert x['source_RGBA_sha256']==y['source_RGBA_sha256'] and x['retained_E']==y['actual_E_retained_member']['file']
 for k in ['name','package_path','object_path']:assert x[k]==y[k]
 expected_saved=ROOT/'UnrealGame/Content'/Path(x['package_path'][6:]+'.uasset');assert Path(x['saved_path']).resolve()==expected_saved.resolve()
 maps.append({'component':x['component'],'frame':x['frame'],'source_preserved':True,'E505_preserved':True,'source_RGBA_preserved':True,'namespace_name_object_preserved':True,'predicted_saved_path':expected_saved.as_posix()})
extra_expected=sorted(Path(x['saved_path']).relative_to(ROOT).as_posix() for x in m['assets'])
assert all(sorted(p['extra'])==extra_expected for p in passes)
baseline={x['path']:{'bytes':x['bytes'],'sha256':x['sha256']} for x in read(r['inputs']['compiledv137']['path'])['files'] if x['path'].startswith('UnrealGame/Content/Production/')}
assert {x['path']:{'bytes':x['bytes'],'sha256':x['sha256']} for x in m['old_production_files']}==baseline
code=IMPORTER.read_text(encoding='utf-8-sig')
for token in ['unreal.TextureCompressionSettings.TC_EDITOR_ICON','unreal.TextureMipGenSettings.TMGS_NO_MIPMAPS','unreal.TextureGroup.TEXTUREGROUP_UI','never_stream=True','srgb=True','unreal.TextureFilter.TF_BILINEAR',"('replace_existing',False)"]:
 assert token in code,token
out={'schema':'Death40-preimport-audit-concurrent-Root-import-status-addendum-v002','created_at_utc':datetime.now(timezone.utc).isoformat(),'original_strict_preimport_report_unchanged':pin(ORIGINAL),'original_freeze_unchanged':pin(OLD_FREEZE),'Root_context_update':'Root explicitly reported UE actual import in progress PID3340 and requested comparing original1286 members rather than requiring directorytotal1286. Newly added40 native packages are outside this source audit validation scope.','scope_verdict':'PASS source40/E505/naming and original1286 member preservation. Original exactdirectory1286/v019empty precondition is SUPERSEDED_BY_ROOT_IMPORT_IN_PROGRESS, not a source failure or oldmember hash failure.','source40_audit_pass':True,'source40_errors':scope_errors,'source40_all_actual512RGBA_nonempty':True,'source40_current_E505_twoSHA_byte_exact':True,'old1286_members_unchanged_twoSHA':True,'old1286_missing_counts':[len(p['missing']) for p in passes],'old1286_changed_counts':[len(p['changed']) for p in passes],'current_directory_counts_at_original_audit':[p['current_file_count'] for p in passes],'extra40_paths_exactly_match_Root_import_targets':True,'Root_new_import_manifest':pin(MAN),'Root_importer_read_only_pin':pin(IMPORTER),'Root_import_manifest_mapping40':maps,'Root_old1286_matches_compiledv137_exact':True,'Root_native_enum_adapter_static_check':{'TC_EDITOR_ICON':True,'TMGS_NO_MIPMAPS':True,'TEXTUREGROUP_UI':True,'never_stream':True,'srgb':True,'TF_BILINEAR':True,'replace_existing_false':True,'kind':'Staticread of actualRootimporter only. Not native property verification.'},'actual_added40_Texture2D_source_filename_UI_save_receipt_independent_validation':'PENDING_OUTSIDE_THIS_SOURCE_AUDIT; Root owns import and receipts','actual_GPU_finish_verification':None,'actual_native_runtime_verification':None,'Dodge_newmedia_View':False,'any_Source_Content_tools_ledger_write':False,'UE_started_by_audit':False,'imagegen_calls':0,'FinalAccepted':False}
p=write('Death40-concurrent-import-source-baseline-audit-addendum-v002.json',out)
f=write('independent-audit-freeze-v002.json',{'schema':'Death40-independent-audit-append-only-freeze-v002','script':pin(Path(__file__)),'base_freeze':pin(OLD_FREEZE),'addendum':pin(p),'original_report_and_all_source_files_modified':False,'source_and_baseline_scope_passed':True,'native_import_validation_claimed':False})
print(json.dumps({'success_source_and_oldmembers':True,'addendum':pin(p),'freeze':pin(f),'old1286_twoSHA_unchanged':True,'40source_E505_exact':True,'extra40_native_validation':'pending','Rootfieldadapter_static_check':True},ensure_ascii=False,indent=2))
