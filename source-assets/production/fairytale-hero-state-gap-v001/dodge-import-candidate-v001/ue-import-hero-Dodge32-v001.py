"""Exact32 native import / read-only host checks. No Source or gameplay mutation."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,json,os,sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from dodge32_import_contract_v001 import ROOT,read,pin,check,need,load_manifest,verify_old,exact_membership,validate_receipt_assets

DEFAULT=ROOT/'source-assets/production/fairytale-hero-state-gap-v001/dodge-state-preparation-v001/Root-Dodge32-import-v001/import-manifest.json'

def independent(manifest_path,m,receipt_path):
    receipt=read(receipt_path)
    need(receipt['schema']=='hero-Dodge32-native-import-v001' and receipt['success'] is True,'Actual Dodge32 import receipt did not pass')
    need(receipt['manifest']==pin(manifest_path),'Receipt binds different import manifest')
    need(receipt['actual_total']==receipt['total_production_files']==1364 and receipt['verification_passes']==2,'Wrong actual import totals')
    need(receipt['old1332_unchanged'] is True and receipt['TrialAllowed'] is False and receipt['FinalAccepted'] is False,'Receipt scope changed')
    validate_receipt_assets(m,receipt)
    for repeat in range(2):
        verify_old(m['old_production_files']);exact_membership(m,True)
        for x in receipt['assets']:check(x['saved'])
    out=manifest_path.parent/('independent-import-verification-'+datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S-%f')+'.json')
    proof=dict(schema='Dodge32-independent-import-twoSHA-v001',success=True,manifest=pin(manifest_path),
        receipt=pin(receipt_path),verifier=pin(__file__),old1332_unchanged=True,old1332_unchanged_twice=True,
        new32_saved=True,new32_saved_twice=True,actual_total=1364,total_production_files=1364,exact_total=1364,
        verification_passes=2,hash_mismatches=0,native_metadata_receipt_checked=True,
        sourceScope='Original native Texture2D/provenance/settings receipt checked; two new host saved-package byte passes, no fresh UE metadata reread',
        runtime_verified=False,native_draw_verified=False,TrialAllowed=False,FinalAccepted=False,formal_complete_units=0)
    with out.open('x',encoding='utf-8',newline='\n') as f:json.dump(proof,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps(dict(success=True,independent_receipt=pin(out),actual_total=1364)))

def native(manifest_path,m):
    import unreal
    need(Path(unreal.Paths.project_dir()).resolve().parent==ROOT,'Wrong actual Unreal project')
    out=ROOT/'UnrealGame/Saved/Bootstrap'/('hero-Dodge32-v001-import-'+datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S-%f')+'.json')
    receipt=dict(schema='hero-Dodge32-native-import-v001',manifest=pin(manifest_path),importer=pin(__file__),
        contract=pin(Path(__file__).resolve().parent/'dodge32_import_contract_v001.py'),assets=[],success=False,
        runtime_verified=False,native_draw_verified=False,geometry_risks_preserved=True,
        TrialAllowed=False,FinalAccepted=False,formal_complete_units=0)
    try:
        need(not unreal.EditorAssetLibrary.list_assets(m['namespace'],recursive=True,include_folder=False),'Native destination namespace occupied')
        tasks=[]
        for x in m['assets']:
            need(not unreal.EditorAssetLibrary.does_asset_exist(x['package_path']),'Native object already exists')
            task=unreal.AssetImportTask()
            for key,value in [('filename',x['source']['path']),('destination_path',m['namespace']),('destination_name',x['name']),
                ('automated',True),('save',False),('replace_existing',False)]:task.set_editor_property(key,value)
            tasks.append(task)
        unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks(tasks)
        settings=dict(compression_settings=unreal.TextureCompressionSettings.TC_EDITOR_ICON,
            mip_gen_settings=unreal.TextureMipGenSettings.TMGS_NO_MIPMAPS,lod_group=unreal.TextureGroup.TEXTUREGROUP_UI,
            never_stream=True,srgb=True,filter=unreal.TextureFilter.TF_BILINEAR)
        for x,task in zip(m['assets'],tasks):
            need(list(task.get_editor_property('imported_object_paths'))==[x['object_path']],'Unexpected imported object')
            tex=unreal.load_asset(x['package_path'])
            need(isinstance(tex,unreal.Texture2D) and tex.get_path_name()==x['object_path'],'Actual Texture2D object mismatch')
            dimensions=[tex.blueprint_get_size_x(),tex.blueprint_get_size_y()];need(dimensions==[512,512],'Actual dimensions changed')
            filenames=list(tex.get_editor_property('asset_import_data').extract_filenames())
            need(len(filenames)==1 and Path(filenames[0]).resolve()==Path(x['source']['path']).resolve(),'Wrong import filename readback')
            for key,value in settings.items():
                tex.set_editor_property(key,value);need(tex.get_editor_property(key)==value,'Texture setting readback differs: '+key)
            need(unreal.EditorAssetLibrary.save_loaded_asset(tex,False),'Texture save failed')
            receipt['assets'].append(dict(component=x['component'],frame=x['frame'],source=x['source'],
                actual_object_path=tex.get_path_name(),actual_class=tex.get_class().get_name(),actual_dimensions=dimensions,
                actual_import_filenames=filenames,actual_settings={k:str(tex.get_editor_property(k)) for k in settings},saved=pin(x['saved_path'])))
        need(set(unreal.EditorAssetLibrary.list_assets(m['namespace'],recursive=True,include_folder=False))=={x['object_path'] for x in m['assets']},'Native exact32 registry changed')
        validate_receipt_assets(m,receipt)
        verify_old(m['old_production_files']);verify_old(m['old_production_files']);exact_membership(m,True)
        receipt.update(success=True,old1332_unchanged=True,verification_passes=2,actual_total=1364,total_production_files=1364)
    except Exception as error:
        receipt['failure']=str(error);raise
    finally:
        with out.open('x',encoding='utf-8',newline='\n') as f:json.dump(receipt,f,ensure_ascii=False,indent=2);f.write('\n')
        unreal.log('Dodge32 actual import receipt: '+str(out))

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--manifest',default=os.environ.get('DUNGEON_DODGE32_IMPORT_MANIFEST',str(DEFAULT)))
    parser.add_argument('--validate-only',action='store_true')
    parser.add_argument('--verify-receipt')
    args=parser.parse_args();need(not(args.validate_only and args.verify_receipt),'Choose one host mode')
    manifest_path=Path(args.manifest).resolve()
    # Native UE uses the host-decoded, pinned source closure without requiring
    # Pillow in Unreal's embedded Python. Host modes decode all32 again.
    m=load_manifest(manifest_path,decode_rgba=bool(args.validate_only or args.verify_receipt))
    if args.verify_receipt:independent(manifest_path,m,Path(args.verify_receipt).resolve());return
    verify_old(m['old_production_files']);verify_old(m['old_production_files']);exact_membership(m,False)
    need(all(not Path(x['saved_path']).exists() for x in m['assets']),'Never replace existing package')
    if args.validate_only:
        print(json.dumps(dict(schema='Dodge32-import-preflight-v001',success=True,source32_RGBA512=True,
            body20_E502=True,armor12_E510=True,old1332_unchanged_twice=True,expected_total=1364,UE_started=False,
            runtime_verified=False,TrialAllowed=False,FinalAccepted=False)));return
    native(manifest_path,m)

if __name__=='__main__':main()
