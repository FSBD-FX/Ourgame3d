"""Register supplied visible A to artist B by integer RGBA translation only."""
from pathlib import Path
import argparse
import subprocess
import datetime
import hashlib
import json
import platform
import shutil
import sys

import PIL
import numpy as np
from PIL import Image


OUT = Path(__file__).resolve().parent
FAMILY = Path("F:/Ourgame/source-assets/production/fairytale-lgt-readability-v003")
PROJECT = Path("F:/Ourgame")
CLIP = int(OUT.name.split("-")[0].replace("primary",""))
NAMESPACE = f"/Game/Production/ArtTrials/EV048/v{CLIP+12:03d}/HeroLeatherPrimary{CLIP}"
DURATIONS = [75,75,60,60,135,135] if CLIP==2 else [110,110,60,60,160,160]
SG = Path("C:/Users/22499/.codex/skills/sprite-gen")
RUNTIME_NAMES = {"Chest":"Chest", "NearShoulder":"ShoulderNear", "FarShoulder":"ShoulderFar"}
PYTHON = Path("C:/Users/22499/.codex/skills/sprite-gen/.venv/Scripts/python.exe")
BODY_NAMES = ["BodyRest", "NearArmWithoutHand", "HelmetForeground", "NearHand"]
ARMOR_NAMES = ["FarShoulder", "Chest", "NearShoulder"]
STATIC_ORDER = ["BodyRest", "FarShoulder", "Chest", "NearArmWithoutHand", "NearShoulder", "HelmetForeground", "NearHand"]
WATCHED = {}


def pin(path, watch=True):
    data = path.read_bytes()
    result = {"path": path.as_posix(), "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}
    if watch and not path.is_relative_to(OUT):
        WATCHED[path] = result
    return result


def require_pin(expected):
    path = Path(expected["path"])
    actual = pin(path)
    if actual != expected:
        raise RuntimeError(f"Source pin changed: {path}")
    return path


def write(relative, data):
    path = OUT / relative
    if not path.is_relative_to(OUT):
        raise RuntimeError("Ownership boundary")
    path.parent.mkdir(parents=True, exist_ok=True)
    text = data if isinstance(data, str) else json.dumps(data, ensure_ascii=False, indent=2) + "\n"
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(text)
    return path


def copy_exact(source, relative):
    path = OUT / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise RuntimeError(f"Existing output: {path}")
    before = pin(source)
    shutil.copy2(source, path)
    if pin(path)["sha256"] != before["sha256"] or path.stat().st_size != before["bytes"]:
        raise RuntimeError("Byte copy changed")
    return path


def rgba(path):
    with Image.open(path) as image:
        if image.mode != "RGBA" or image.size != (512, 512):
            raise RuntimeError(f"Expected 512 RGBA: {path}")
        return np.asarray(image).copy()


def pixel_bbox(array, alpha_only=False):
    mask = array[:, :, 3] > 0 if alpha_only else np.any(array != 0, axis=2)
    ys, xs = np.where(mask)
    return [int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1] if len(xs) else None


def translate(array, dx, dy):
    height, width = array.shape[:2]
    if type(dx) is not int or type(dy) is not int or abs(dx) >= width or abs(dy) >= height:
        raise RuntimeError("Integer delta out of range")
    bbox = pixel_bbox(array)
    if bbox is None or bbox[0] + dx < 0 or bbox[1] + dy < 0 or bbox[2] + dx > width or bbox[3] + dy > height:
        raise RuntimeError("Translation would clip nonzero RGBA, including hidden RGB")
    sx0, sx1 = max(0, -dx), min(width, width - dx)
    sy0, sy1 = max(0, -dy), min(height, height - dy)
    result = np.zeros_like(array)
    result[sy0 + dy:sy1 + dy, sx0 + dx:sx1 + dx] = array[sy0:sy1, sx0:sx1]
    return result


def save_rgba(array, relative):
    path = OUT / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise RuntimeError("Existing diagnostic image")
    Image.fromarray(array).save(path)
    if not np.array_equal(rgba(path), array):
        raise RuntimeError("PNG round trip changed RGBA")
    return path


def compose(layers, omit=None):
    image = Image.new("RGBA", (512, 512), (0, 0, 0, 0))
    for name in STATIC_ORDER:
        if name != omit:
            image = Image.alpha_composite(image, Image.fromarray(layers[name]))
    return np.asarray(image).copy()



def export_selection(component):
    """Reuse already standard-curated sources and verify their explicit export provenance."""
    name,state=component['component'],component['state']
    result={}
    for row in component['frames']:
        frame=row['frame'];source=require_pin(row['source']);pre=require_pin(row['pre_curation_source']);sidecar=require_pin(row['curation_sidecar'])
        run=source.parents[1]
        if source.parent.name!='curated' or sidecar.parent!=run:raise RuntimeError('Expected existing explicit curated source, not raw frames')
        request=run/'sprite-request.json';fm=run/'frames/frames-manifest.json';pin(request);pin(fm)
        curation=json.loads(sidecar.read_text('utf-8-sig'));request_data=json.loads(request.read_text('utf-8-sig'))
        entry=curation['states'][state]
        if entry['selected']!=list(range(6)) or entry.get('transforms') or entry.get('pixels') or entry.get('clones') or entry.get('breathe'):
            raise RuntimeError('Source identity export has unexpected edits/selection')
        if request_data['fit']['pixel_unfake'] is not False:raise RuntimeError('HD source became quantized')
        command_record=run.parent/'logs'/f'export-curated-{state}-v001-command.json'
        command_data=json.loads(command_record.read_text('utf-8-sig'));pin(command_record)
        if command_data['actual_exit_code']!=0:raise RuntimeError('Original standard export did not pass')
        if not np.array_equal(rgba(source),rgba(pre)):raise RuntimeError('Existing curated export is not original source RGBA')
        local=copy_exact(source,f'curated-inputs/{name}/frame-{frame}.png')
        result[frame]={'pre_curation_source':pin(pre),'original_curated_export':pin(source),'curated_export':pin(local),'exact_local_curated_copy':pin(local),
            'curation_sidecar':pin(sidecar),'export_command_record':pin(command_record),'selected_index':frame,'identity_export_RGBA_equal':True,
            'fit_pixel_unfake':False,'pixel_snap_scale':None,'standard_export_reused_not_reextracted':True,'selection_role':'Root selected these actual curated component sources for integer fit trial, not final animation acceptance'}
    return result


def main():
    if Path(sys.executable).resolve()!=PYTHON.resolve() or CLIP not in [2,3] or OUT!=FAMILY/f'primary{CLIP}-integer-assembly-v001' or (OUT/'assembly-proof-v001.json').exists():raise RuntimeError('Unexpected/existing output/interpreter')
    mounts_path=FAMILY/f'combo-visible-mounts-v001/primary{CLIP}-all18-mounts-v001.json'
    mount_freeze_path=FAMILY/'combo-visible-mounts-v001/mounts-freeze-v001.json'
    mount_sha={2:'a10b3b6ddf3d014247c541880b8b31da65f51f22387b4946ca5560954174baaf',3:'75288377eaa310ce3fa037471bae34423cce72034f27ab74786582dcecb68ad5'}[CLIP]
    if pin(mounts_path)['sha256']!=mount_sha or pin(mount_freeze_path)['sha256']!='6e06840e8792b80a657616b42ad040918104b6f213dab771e5b906a0e682a450':raise RuntimeError('Root mounts/freeze changed')
    mount_freeze=json.loads(mount_freeze_path.read_text('utf-8-sig'))
    for entry in mount_freeze['files']+mount_freeze['source_indices']:require_pin(entry)
    mounts=json.loads(mounts_path.read_text('utf-8-sig'))
    if mounts['fit_accepted'] is not False or len(mounts['rows'])!=18:raise RuntimeError('Expected18 artist trial mounts')
    index_path=require_pin(mounts['source_index']);inventory=json.loads(index_path.read_text('utf-8-sig'))
    expected_native={2:{'Chest':193,'NearShoulder':194,'FarShoulder':195},3:{'Chest':196,'NearShoulder':197,'FarShoulder':198}}[CLIP]
    if {c['component']:c['native_request'] for c in inventory['components']}!=expected_native:raise RuntimeError('Wrong actual native components')
    mapping_path=require_pin(inventory[f'actual_body{171 if CLIP==2 else 175}_source_version_mapping'])
    mapping=json.loads(mapping_path.read_text('utf-8-sig'))
    partition_path=require_pin(mapping['partition_proof']);partition=json.loads(partition_path.read_text('utf-8-sig'))
    import_manifest_path=require_pin(mapping['actual_import']['manifest']);import_manifest=json.loads(import_manifest_path.read_text('utf-8-sig'))
    old_candidate_path=require_pin(import_manifest['references']['candidate']);old_candidate=json.loads(old_candidate_path.read_text('utf-8-sig'))
    current_body={(r['frame'],r['component']):r['source'] for r in old_candidate['textures'] if r['component'] in BODY_NAMES}
    for entry in mapping['actual_import']['verified_assets']:
        if entry['component'] in BODY_NAMES:require_pin(entry['source']);require_pin(entry['saved_uasset'])
    expected_namespace=f'/Game/Production/ArtTrials/EV048/v{10 if CLIP==2 else 11:03d}/'+('HeroSwordPrimary2Armor' if CLIP==2 else 'HeroSwordPrimary3')
    if import_manifest['namespace']!=expected_namespace:raise RuntimeError('Imported body namespace changed')
    native_source=FAMILY/'leather-combo-source-v001'/('DungeonFairytaleSwordPrimary2ArmorV001.inl' if CLIP==2 else 'DungeonFairytaleSwordPrimary3V001.inl')
    source_text=native_source.read_text('utf-8-sig');pin(native_source)
    if f'T_Fairytale_LeatherPrimary{CLIP}%s_%03d_v001' not in source_text or NAMESPACE+'/' not in source_text:raise RuntimeError('Planned native package pattern mismatch')
    keyed={(r['frame'],r['component']):r for r in mounts['rows']}
    if len(keyed)!=18 or set(keyed)!={(i,n) for i in range(6) for n in ARMOR_NAMES}:raise RuntimeError('Duplicate/missing18 mounts')
    selected={(r['frame'],c['component']):r for c in inventory['components'] for r in c['frames']}
    expected_run='/run-primary2-v004/curated/' if CLIP==2 else '/run-primary3-v001/curated/'
    for frame in range(6):
        actual_body=partition['frames'][frame]['source']
        if expected_run not in actual_body['path']:raise RuntimeError('Wrong actual canonical body version')
        require_pin(actual_body)
        for name in ARMOR_NAMES:
            row=keyed[frame,name]
            if row['clip']!=CLIP or row['body']!=actual_body or row['duration_ms']!=DURATIONS[frame] or row['source']!=selected[frame,name]['source']:raise RuntimeError('Mount source/body/timing mismatch')
            array=rgba(require_pin(row['source']));a,b,delta=row['A_source_px'],row['B_body_design_source_px'],row['integer_delta_xy']
            if not all(type(v) is int for v in a+b+delta) or delta!=[b[0]-a[0],b[1]-a[1]]:raise RuntimeError('Explicit integer A/B/delta required')
            if array[a[1],a[0]].tolist()!=row['A_observed_rgba'] or array[a[1],a[0],3]<128:raise RuntimeError('Actual visible A pixel changed')
            placed=translate(array,*delta)
            if not np.array_equal(translate(placed,-delta[0],-delta[1]),array):raise RuntimeError('Translation clips or changes RGBA')
    copy_exact(mounts_path,'inputs/root18-mounts.json');copy_exact(mount_freeze_path,'inputs/root-mounts-freeze.json')
    copy_exact(index_path,'inputs/selected18-curated-source-index.json');copy_exact(mapping_path,'inputs/actual-runtime-source-version-mapping.json')
    copy_exact(partition_path,'inputs/original-four-body-partition-proof.json');copy_exact(import_manifest_path,'inputs/current-old-body-import-manifest.json')
    export_records={c['component']:export_selection(c) for c in inventory['components']}
    registrations=[];frames=[];assets=[]
    for frame in range(6):
        original_body_pin=partition["frames"][frame]["source"]
        original_body=rgba(require_pin(original_body_pin))
        layers={};masks={};body_copies=[]
        source_partition=partition["frames"][frame]
        for name in BODY_NAMES:
            source=require_pin(current_body[frame,name])
            original=require_pin(next(x["file"] for x in source_partition["layers"] if x["owner"]==name))
            mask_path=require_pin(next(x["file"] for x in source_partition["masks"] if x["owner"]==name))
            if source.read_bytes()!=original.read_bytes():
                raise RuntimeError("Current body layer is not exact partition bytes")
            output=copy_exact(source,f"body-layers/{name}/frame-{frame}.png")
            layers[name]=rgba(output)
            with Image.open(mask_path) as image:
                values=np.asarray(image).copy()
                if image.mode!='L' or image.size!=(512,512) or not set(np.unique(values)).issubset({0,255}):
                    raise RuntimeError("Invalid ownership mask")
                masks[name]=values>0
            body_copies.append({"owner":name,"source":pin(source),"copy":pin(output),"original_partition":pin(original),
                "ownership_mask":pin(mask_path),"byte_exact":True,"semantic_protection_inference":False})
        count=np.sum(np.stack(list(masks.values())),axis=0)
        reconstructed=np.sum(np.stack(list(layers.values())),axis=0,dtype=np.uint16)
        if not np.all(count==1) or not np.array_equal(reconstructed,original_body.astype(np.uint16)):
            raise RuntimeError("Original four layers fail exhaustive source ownership/full RGBA reconstruction")
        for name in ARMOR_NAMES:
            row=keyed[frame,name];selection=export_records[name][frame]
            source=require_pin(selection["curated_export"]);array=rgba(source)
            a,b,delta=row["A_source_px"],row["B_body_design_source_px"],row["integer_delta_xy"]
            placed=translate(array,*delta);inverse=translate(placed,-delta[0],-delta[1])
            output=save_rgba(placed,f"armor-layers/{name}/frame-{frame}.png");layers[name]=placed
            intersections=[{"source_owner":owner,"ownership_coordinates_any_alpha":int(np.count_nonzero((placed[:,:,3]>0)&masks[owner])),
                "visible_source_both_any_alpha":int(np.count_nonzero((placed[:,:,3]>0)&(layers[owner][:,:,3]>0))),
                "visible_source_both_core128":int(np.count_nonzero((placed[:,:,3]>=128)&(layers[owner][:,:,3]>=128))),
                "semantic_protection_inference":False} for owner in BODY_NAMES]
            registration={"frame":frame,"component":name,"selection_export_provenance":selection,"translated":pin(output),
                "A_source_px":a,"A_observed_rgba":array[a[1],a[0]].tolist(),"A_feature":row["A_feature"],
                "A_visual_uncertainty_px":row["A_manual_visual_uncertainty_px"],"B_body_design_source_px":b,"B_role":row["B_role"],
                "B_design_uncertainty_px":row["B_design_uncertainty_px"],"B_is_HIDDEN_TRIAL":"HIDDEN TRIAL" in row["B_role"],"actual_runtime_body":original_body_pin,
                "B_original_body_RGBA_diagnostic_only":original_body[b[1],b[0]].tolist(),"integer_delta_xy":delta,
                "A_maps_exactly_to_B":placed[b[1],b[0]].tolist()==array[a[1],a[0]].tolist(),
                "source_nonzero_RGBA_bbox":pixel_bbox(array),"translated_nonzero_RGBA_bbox":pixel_bbox(placed),
                "clipped_nonzero_RGBA_pixels":0,"inverse_full_RGBA_equal":bool(np.array_equal(array,inverse)),
                "source_RGBA_sha256":hashlib.sha256(array.tobytes()).hexdigest(),"inverse_RGBA_sha256":hashlib.sha256(inverse.tobytes()).hexdigest(),
                "rescaled_rotated_recolored_drawn":False,"intersections":intersections,"fit_accepted":False}
            registrations.append(registration)
            runtime=RUNTIME_NAMES[name];asset=f"T_Fairytale_LeatherPrimary{CLIP}{runtime}_{frame:03d}_v001"
            package=NAMESPACE+'/'+asset
            assets.append({"component":runtime,"source_component":name,"frame":frame,"name":asset,"source":pin(output),
                "package_path":package,"object_path":package+'.'+asset,"registration":registration})
        composite=compose(layers)
        right=save_rgba(composite,f"diagnostics/static-no-sword/right/frame-{frame}.png")
        left=save_rgba(np.flip(composite,axis=1).copy(),f"diagnostics/static-no-sword/left-whole-image-mirror/frame-{frame}.png")
        if not np.array_equal(np.flip(rgba(left),axis=1),composite):raise RuntimeError("Whole image mirror not reversible")
        pairwise=[{"first":a,"second":b,"both_any_alpha":int(np.count_nonzero((layers[a][:,:,3]>0)&(layers[b][:,:,3]>0))),
            "both_core128":int(np.count_nonzero((layers[a][:,:,3]>=128)&(layers[b][:,:,3]>=128)))}
            for n,a in enumerate(ARMOR_NAMES) for b in ARMOR_NAMES[n+1:]]
        contributions=[{"component":name,"final_RGBA_difference_pixels_when_omitted":int(np.count_nonzero(np.any(compose(layers,name)!=composite,axis=2))),
            "semantic_acceptance_inferred":False} for name in ARMOR_NAMES]
        frames.append({"frame":frame,"duration_ms":DURATIONS[frame],"actual_runtime_body":original_body_pin,"body_layers":body_copies,
            "four_layers_reconstruct_original_full_RGBA_exact":True,"ownership_exclusive_exhaustive":True,
            "static_right":pin(right),"static_left_whole_image_mirror":pin(left),"whole_mirror_inverse_equal":True,
            "pairwise_armor_intersections":pairwise,"omit_one_numeric_contributions":contributions,
            "semantic_regions_pending_Root_actual_review":{k:None for k in ['helmet','eyes','neck','near_hand','far_hand','belt_and_waist']},"fit_accepted":False})

    mismatches=[str(q) for q,before in WATCHED.items() if pin(q,False)!=before]
    if mismatches:raise RuntimeError(f'Read-only source changed: {mismatches}')
    report=write('assembly-proof-v001.json',{'schema':f'primary{CLIP}-soft-leather-integer-curated-source-assembly-v001','created_local':datetime.datetime.now().astimezone().isoformat(),
        'script':pin(Path(__file__).resolve()),'mounts':pin(mounts_path),'mounts_freeze':pin(mount_freeze_path),'source_index':pin(index_path),'actual_body_mapping':pin(mapping_path),'planned_native_source_naming_contract':pin(native_source),
        'frames':frames,'registrations':registrations,'armor_count':18,'body_byte_copies':24,'static_right_count':6,'static_left_count':6,'durations_ms':DURATIONS,'static_layer_order_no_sword':STATIC_ORDER,
        'future_Sword_slot':{'after':'HelmetForeground','before':'NearHand','included':False},'all_integer_translations_reversible_RGBA':True,'clipped_nonzero_RGBA_pixels':0,'all_body_original_bytes_unchanged':True,
        'existing_standard_curated_export_count_reverified':18,'new_extraction_or_standard_export_called':False,'pre_curation_to_curated_RGBA_exact':True,'source_mismatches':mismatches,'read_only_source_count':len(WATCHED),
        'hidden_trial_placement_count':sum('HIDDEN TRIAL' in r['B_role'] for r in registrations),'toolchain':{'python':sys.executable,'Pillow':PIL.__version__,'numpy':np.__version__},
        'new_outputs_viewed':False,'fit_accepted':False,'semantic_protection_accepted':False,'imported':False,'full_animation_or_unit_accepted':False,
        'limitations':['Actual component A is Root visually selected and pinned RGBA sample verified. All B are artist proposals; HIDDEN TRIAL remains explicit, not measured/reconstructed bones.',
            'Original body ownership masks prove an exclusive RGBA partition, not a semantic protection mask. Helmet/eyes/neck/nearhand/farhand/belt/waist still require Root actual visual review.',
            'Numeric intersection and omission contributions do not certify fit or semantic clearance. Sword is omitted; left diagnostics whole-mirror final composites only. No full motion/action/equipment compatibility claim.',
            'All previous low-motion warnings and baseline sparse failures remain preserved in extraction candidates. P2Far195 alone has explicit160+core128pixel-count design boundary at unchanged32x30 scale; its minimum view projects to about2.6x3.3px, main readability belongs to chest/near shoulder.',
            'Already standard-curated/exported source frames are reused and reverified RGBA-identical to pre-curation. No raw frame is installed, and no new extraction/export/quantization is performed here.']})
    write('HANDOFF.md',f"""# Primary{CLIP}软皮整数试装候选

18个已标准selected/curated/export的源重核与pre-curation全RGBA相等，再按Root actual A→artist B作整数位移。隐藏B保留HIDDEN TRIAL角色与误差；不是骨点重建。旧身体24层逐字节复制并复原实际{'171/run-primary2-v004、runtimev010四层' if CLIP==2 else '175/run-primary3-v001、runtimev011四层'}。无二次缩放/旋转/改色/补画/裁切。

六张右向与六张整体镜像无剑静态诊断，层序BodyRest→Far→Chest→NearArmWithoutHand→Near→HelmetForeground→空Sword槽→NearHand。语义保护/fit/动作/导入全部未接受，数值交集不能替代Root实际审图；应先F/E留档再看。未查看新图，无Source/工具/UE/ledger/status/进度/媒体目录改动。

planned v{CLIP+12:03d}导入清单仅18新甲Texture，身体继续复用旧包。最终manifest显式引用assembly_freeze，deliveryfreeze绑定二者以避免循环SHA。原baseline失败、低motion、P2Far195专用小片设计边界不改变。
""")
    files=[pin(q,False) for q in sorted(OUT.rglob('*')) if q.is_file()]
    for entry in files:entry['path']=Path(entry['path']).relative_to(OUT).as_posix()
    freeze=write('assembly-freeze-v001.json',{'schema':f'primary{CLIP}-integer-assembly-freeze-v001','files':files,'file_count_excluding_manifest':len(files),'total_bytes_excluding_manifest':sum(x['bytes'] for x in files),'fit_accepted':False,'new_outputs_viewed':False,'imported':False})
    final_assets=[]
    for asset in assets:
        source=asset['source']
        final_assets.append({k:v for k,v in asset.items() if k not in {'source','registration'}}|{'source':source['path'],'source_bytes':source['bytes'],'source_sha256':source['sha256'],'registered_source':source,'registration_proof':pin(report)})
    manifest=write(f'candidate-import-v{CLIP+12:03d}-v001.json',{'schema':f'leather-primary{CLIP}-curated-integer18-import-candidate-v001','namespace':NAMESPACE,'asset_count':18,'assets':final_assets,
        'body_assets_reused_unchanged':24,'canvas_px':[512,512],'native_facing':1,'display_root':[256,464],'preview_canvas_size':72*512/416,'durations_ms':DURATIONS,'source_native_requests':list(expected_native.values()),
        'references':{'assembly_freeze':pin(freeze),'assembly_proof':pin(report),'mounts':pin(mounts_path),'mounts_freeze':pin(mount_freeze_path),'curated_source_index':pin(index_path),'actual_body_mapping':pin(mapping_path),'planned_native_source_contract':pin(native_source)},
        'assembly_freeze':pin(freeze),'assembly_freeze_excludes_final_import_manifest_to_avoid_hash_cycle':True,'fit_accepted':False,'import_permitted':False,'Root_static_review_required':True,'runtime_import_called':False,'formal_complete_units':0})
    delivery_files=[pin(q,False) for q in sorted(OUT.rglob('*')) if q.is_file()]
    for entry in delivery_files:entry['path']=Path(entry['path']).relative_to(OUT).as_posix()
    delivery=write('delivery-freeze-v001.json',{'schema':f'primary{CLIP}-integer-assembly-delivery-freeze-v001','files':delivery_files,'assembly_freeze':pin(freeze),'candidate_import':pin(manifest),'fit_accepted':False,'new_outputs_viewed':False})
    print(json.dumps({'clip':CLIP,'report':pin(report),'candidate_import':pin(manifest),'assembly_freeze':pin(freeze),'delivery_freeze':pin(delivery),'armor_count':18,'body_exact_copies':24,'right_static':6,'left_whole_mirror':6,'read_only_source_rechecks':len(WATCHED),'mismatches':[],'new_outputs_viewed':False},indent=2))

if __name__=='__main__':main()
