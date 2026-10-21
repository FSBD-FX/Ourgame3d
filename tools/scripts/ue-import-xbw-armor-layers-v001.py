"""Shared native-only four-armor XBW importer, invoked by a frozen job wrapper."""
from pathlib import Path
from datetime import datetime, timezone
import importlib.util
import json

ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location("xbw_source_checks",Path(__file__).with_name("ue-import-xbw-primary-v001.py"))
primary=importlib.util.module_from_spec(spec);spec.loader.exec_module(primary)
helper,require=primary.helper,primary.require
ARMORS=("ARM-LGT-001","ARM-MED-001","ARM-HVY-001","ARM-ROB-001")

def verify_references(node,hashes,tool_originals):
    if isinstance(node,dict):
        for key,value in node.items():
            hash_key='sha256' if key=='path' else key[:-5]+'_sha256' if key.endswith('_path') else key+'_sha256'
            if isinstance(value,str) and hash_key in node:
                path=Path(value).resolve();expected=node[hash_key]
                if path in tool_originals:
                    require(expected==tool_originals[path],'Tool provenance hash differs')
                elif path!=(ROOT/'docs/design/equipment-v1/weapons.json').resolve():
                    path=helper.source_path(value)
                require(path not in hashes or hashes[path]==expected,'Contradictory source references')
                if path not in hashes:helper.checked_hash(path,expected);hashes[path]=expected
            verify_references(value,hashes,tool_originals)
    elif isinstance(node,list):
        for value in node:verify_references(value,hashes,tool_originals)


def preflight(clip,sha,package,family,frames):
    manifest_path=ROOT/f"source-assets/production/first-batch-XBW-armor-layers-v001/manifests/import-XBW-{clip}-four-armors-v001.json"
    m=json.loads(helper.checked_hash(manifest_path,sha).decode("utf-8-sig"))
    require(m['frozen'] and m['schema']=='frozen-XBW-pose-armor-layer-subset-v1'
            and m['weapon_id']=='WPN-XBW-001' and m['clip']==clip,"Wrong frozen XBW armor clip")
    require(m['frame_count']==frames and m['armor_texture_count_new']==4*frames*2
            and m['common_body_texture_count_reused']==3*frames and m['canvas_px']==[512,512]
            and m['root_px']==[256,472],"Changed native count/root")
    require(m['draw_order']==['body_far','armor_far','independent_weapon','body_support','armor_near','body_near'],"Changed layer order")
    require(m['body_geometry_transform']=='none' and m['armor_per_frame_geometry_transform']=='none',"No source geometry transformation allowed")
    require(set(m['armors'])==set(ARMORS),"Changed armor identities")
    tool_originals={}
    for source in m['source_provenance']:
        original=Path(source['tool_original_path']).resolve()
        require(original.is_relative_to(Path('C:/Users/22499/.codex/generated_images').resolve()),'Unexpected tool provenance root')
        require(source['tool_original_sha256']==source['raw_sha256'],'Tool/raw provenance mismatch')
        helper.checked_hash(original,source['raw_sha256'])
        helper.checked_hash(helper.source_path(source['raw_path']),source['raw_sha256'])
        tool_originals[original]=source['raw_sha256']
    hashes,rows={},[];verify_references(m,hashes,tool_originals)
    body=json.loads(helper.checked_hash(Path(m['source_body_contract_path']),m['source_body_contract_sha256']).decode('utf-8-sig'))
    require(len(m['common_body'])==frames and len(body['frames'])==frames,"Missing common native bodies")
    for current,frozen in zip(m['common_body'],body['frames']):
        require(current['index']==frozen['index'] and current['ground_root_px']==[256,472],"Changed common frame/root")
        for track in ('body_far','body_support','body_near'):
            require(current[track]['sha256']==frozen[track]['sha256'] and current[track]['path']==frozen[track]['path'],"Replaced shared source body")
    for armor in ARMORS:
        require([f['index'] for f in m['armors'][armor]]==list(range(frames)),"Missing/reordered armor pose")
        for frame in m['armors'][armor]:
            require(frame['root_px']==[256,472] and frame['armor_hidden_back'] is None,"Invented back or changed origin")
            for track in ('armor_far','armor_near'):
                item=frame[track];source=helper.source_path(item['path'])
                pixels=helper.inspect_rgba_png(helper.checked_hash(source,item['sha256']))
                for key in ('canvas_px','mode','alpha_extrema','bbox_px'):
                    require(pixels[key]==item[key],"Actual PNG differs: "+track)
                require(pixels['nonempty'] and pixels['corners_transparent'] and pixels['alpha_extrema']==[0,255],"Invalid transparent garment")
                name=f"T_XBWArmor{family}_{armor.replace('-','_')}_{track}_{frame['index']:03d}_v001"
                rows.append({'armor_id':armor,'clip':clip,'frame':frame['index'],'track':track,'source':str(source),
                    'source_sha256':item['sha256'],'name':name,'package_path':package+'/'+name,'object_path':package+'/'+name+'.'+name})
    require(len(rows)==8*frames and len({r['source'] for r in rows})==len(rows),"Repeated/missing native garment")
    return manifest_path,rows,hashes


def run(clip,sha,package,family,frames,validate_only=False):
    manifest_path,rows,hashes=preflight(clip,sha,package,family,frames)
    if validate_only:
        print(json.dumps({'source_validation_success':True,'native_layers':len(rows),'reused_body_count':frames*3,
            'verified_references':len(hashes),'manifest_sha256':sha,'destination':package,'unreal_import_run':False}));return
    import unreal
    require(Path(unreal.Paths.project_dir()).resolve().parent==ROOT,'Wrong UE project')
    destination=ROOT/'UnrealGame/Content'/package.removeprefix('/Game/')
    require(not destination.exists() or not any(p.is_file() for p in destination.rglob('*')),'Do not overwrite prior imports')
    if unreal.EditorAssetLibrary.does_directory_exist(package):
        require(not unreal.EditorAssetLibrary.list_assets(package,recursive=True,include_folder=False),'Package populated')
    receipt={'schema':'xbw-armor-layers-import-v1','clip':clip,'manifest_sha256':sha,'destination':package,
        'expected_count':len(rows),'actual_count':0,'saved_count':0,'success':False,'assets':rows,
        'verified_reference_count':len(hashes),'runtime_verified':False,'full_coverage_accepted':False,
        'scope':'Native pose-specific garment candidates only; no geometry change, full armor coverage, runtime/motion or20mix acceptance'}
    receipt_path=ROOT/'UnrealGame/Saved/Bootstrap'/('xbw-armor-'+clip+'-v001-import-'+datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S-%f')+'.json')
    try:
        tasks=[]
        for row in rows:
            require(not unreal.EditorAssetLibrary.does_asset_exist(row['package_path']),'Existing asset')
            task=unreal.AssetImportTask()
            for key,value in (('filename',row['source']),('destination_path',package),('destination_name',row['name']),('automated',True),('save',False),('replace_existing',False)):
                task.set_editor_property(key,value)
            tasks.append(task)
        unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks(tasks)
        for row,task in zip(rows,tasks):
            require(list(task.get_editor_property('imported_object_paths'))==[row['object_path']],'Wrong imported object')
            texture=unreal.load_asset(row['package_path']);require(isinstance(texture,unreal.Texture2D),'Expected Texture2D')
            for key,value in (('compression_settings',unreal.TextureCompressionSettings.TC_EDITOR_ICON),('mip_gen_settings',unreal.TextureMipGenSettings.TMGS_NO_MIPMAPS),('lod_group',unreal.TextureGroup.TEXTUREGROUP_UI),('never_stream',True),('srgb',True)):
                texture.set_editor_property(key,value);require(texture.get_editor_property(key)==value,'Wrong UE texture setting')
            require([texture.blueprint_get_size_x(),texture.blueprint_get_size_y()]==[512,512],'Changed native canvas')
            receipt['actual_count']+=1
        helper.checked_hash(manifest_path,sha)
        for path,digest in hashes.items():helper.checked_hash(path,digest)
        for row in rows:
            require(unreal.EditorAssetLibrary.save_loaded_asset(unreal.load_asset(row['package_path']),False),'Could not save new garment')
            receipt['saved_count']+=1
        require(set(unreal.EditorAssetLibrary.list_assets(package,recursive=True,include_folder=False))=={r['object_path'] for r in rows},'Wrong package contents')
        receipt['success']=receipt['actual_count']==receipt['saved_count']==len(rows)
    except Exception as error:
        receipt['error']=str(error);raise
    finally:
        with receipt_path.open('x',encoding='utf-8') as stream:json.dump(receipt,stream,ensure_ascii=False,indent=2)
        unreal.log('XBW armor receipt: '+str(receipt_path))
