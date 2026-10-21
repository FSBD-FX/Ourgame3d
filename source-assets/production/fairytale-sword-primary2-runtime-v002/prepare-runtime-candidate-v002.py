"""Prepare native171 exact-pixel runtime/data candidates in this new family only.
No Unreal import, Source installation, image resampling, preview or display.
"""
from pathlib import Path
from datetime import datetime
import hashlib
import importlib.util
import json
import math
import sys

sys.dont_write_bytecode=True
ROOT=Path('F:/Ourgame')
HERE=Path(__file__).resolve().parent
FAMILY=ROOT/'source-assets/production/fairytale-sword-primary2-v001'
MEASUREMENT=FAMILY/'primary2-measurement-v003/measurement-v003.json'
MEASUREMENT_FREEZE=FAMILY/'primary2-measurement-v003/measurement-freeze-v003.json'
EXTRACTION_FREEZE=FAMILY/'primary2-extraction-v004/extracted-freeze-v004.json'
NAMESPACE='/Game/Production/ArtTrials/EV048/v009/HeroSwordPrimary2'
DISK=ROOT/'UnrealGame/Content/Production/ArtTrials/EV048/v009/HeroSwordPrimary2'
DECODER=ROOT/'tools/scripts/ue-import-armor-primary2-four-v001.py'
DECODER_SHA='5c667edbeb81eac54648d14ff92b8883d1b15a39a05cc3b56c17933dd29eb49a'
AXES=[[.94,-.341],[.35,.937],[.8,.6],[.9,-.436],[.95,-.312],[.94,-.341]]
DURATIONS=[75,75,60,60,135,135]


def require(value,why):
    if not value: raise RuntimeError(why)


def fact(path):
    path=Path(path); data=path.read_bytes()
    return {'path':path.as_posix(),'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()}


def load(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def write_json(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('x',encoding='utf-8',newline='\n') as stream:
        stream.write(json.dumps(value,ensure_ascii=False,indent=2)+'\n')


def verify_freeze(path):
    document=load(path)
    for row in document['files']:
        actual=fact(row['path'])
        require(actual['bytes']==row['bytes'] and actual['sha256']==row['sha256'],'Frozen file changed: '+row['path'])
    return {'manifest':fact(path),'files_checked':len(document['files']),'mismatches':0}


def production_inventory():
    rows=[]
    for p in sorted((ROOT/'UnrealGame/Content/Production').rglob('*')):
        if p.is_file():
            row=fact(p);row['path']=p.relative_to(ROOT).as_posix();rows.append(row)
    require(sum(row['path'].endswith('.uasset') for row in rows)==989,'Expected current989 packages, ask Root if baseline changed')
    return {'schema':'readonly-production989-before-native171-import-v2','created_local':datetime.now().astimezone().isoformat(),'file_count':len(rows),'uasset_count':989,'total_bytes':sum(x['bytes'] for x in rows),'files':rows,'scope':'Real disk inventory, not a UE registry query/import receipt'}


def fv(point):
    return f'FVector2D({float(point[0])!r}, {float(point[1])!r})'


def main():
    require(not (HERE/'curated').exists() and not (HERE/'manifests').exists(),'Refuse candidate overwrite')
    require(not DISK.exists() or not any(DISK.rglob('*')),'Candidate disk namespace must be unused')
    require(not (ROOT/'UnrealGame/Source/CodexDungeon/DungeonFairytaleSwordPrimary2V003.inl').exists(),'Candidate Source include name already exists')
    require(fact(DECODER)['sha256']==DECODER_SHA,'NativePNG decoder changed')
    require(fact(MEASUREMENT_FREEZE)['sha256']=='e03de5b66bb17e9e89d9f0487361b24635682c4124b957104e1bf43ff8c30f19','Measurement freeze pin changed')
    require(fact(MEASUREMENT)['sha256']=='9a776415005eb1a71228360d7b14f468bc6d34db76afa554555d87bdafd2e8e4','Measurement pin changed')
    require(fact(EXTRACTION_FREEZE)['sha256']=='2c4051b8b3e0b190d501ee28324e767c5e882c5fe57e708b1f1bb991485c7521','Extraction freeze changed')
    freezes=[FAMILY/'preparation-freeze-v004.json',EXTRACTION_FREEZE,MEASUREMENT_FREEZE,ROOT/'source-assets/production/fairytale-sword-primary2-runtime-v001/ready-for-root-import-freeze-v001.json']
    before=[verify_freeze(p) for p in freezes]
    measured=load(MEASUREMENT)
    require(measured['source_native']==171 and len(measured['frames'])==6,'Actual171 six phases required')
    require(measured['timing']['kernel']==DURATIONS and measured['timing']['standard_preview']==[100]*6,'Do not retime/falsify preview')
    require(measured['display_contract']['root']==[256,464] and measured['display_contract']['maximum_body_height']==72,'Fixed body contract changed')
    inventory=production_inventory();baseline=HERE/'manifests/old-production989-before-import.json';write_json(baseline,inventory)
    spec=importlib.util.spec_from_file_location('readonly_native171_png_decoder',DECODER)
    decoder=importlib.util.module_from_spec(spec);spec.loader.exec_module(decoder)
    (HERE/'curated').mkdir()
    assets=[];markers=[];pixel_checks=[]
    for index,frame in enumerate(measured['frames']):
        require(frame['frame']==index,'Ordered0..5 actual frames required')
        source=FAMILY/f'run-primary2-v004/curated/frame-{index}.png'
        require(Path(frame['source']['path']).resolve()==source.resolve() and fact(source)==frame['source'],'Actual171 source mismatch')
        target=HERE/f'curated/frame-{index}.png'
        with target.open('xb') as out:out.write(source.read_bytes())
        require(target.read_bytes()==source.read_bytes(),'Candidate must preserve whole PNG bytes')
        pixels=decoder.inspect_rgba_png(target.read_bytes())
        require(pixels['canvas_px']==[512,512] and pixels['mode']=='RGBA' and pixels['alpha_extrema']==[0,255] and pixels['nonempty'] and pixels['corners_transparent'],'NativeCRC/512RGBA/alpha failed')
        bbox=pixels['bbox_px'];height=bbox[3]-bbox[1]
        require(height<=416,'Fixed maximum visible height416 exceeded')
        name=f'T_Fairytale_SwordPrimary2_{index:03d}_v002'
        assets.append({'clip':'Primary2','frame':index,'source':target.as_posix(),'source_bytes':target.stat().st_size,'source_sha256':fact(target)['sha256'],'source_bbox':bbox,'canonical_curated':fact(source),'name':name,'package_path':NAMESPACE+'/'+name,'object_path':NAMESPACE+'/'+name+'.'+name})
        grip=frame['grip_candidate'];hand=frame['visible_near_hand_polygon_candidate']
        require(grip['type'].startswith('MANUAL actual visible') and grip['uncertainty_plus_minus_px']==3,'Use actual171 palm candidate, no old/guide/bbox replacement')
        require(hand['uncertainty_plus_minus_px']==4 and not hand['binary_ownership_or_complete_reconstruction'],'Hand mask must remain uncertain candidate')
        axis=AXES[index];require(all(math.isfinite(x) for x in axis) and math.hypot(*axis)>0,'Invalid axis design')
        markers.append({'frame':index,'source':fact(source),'display_root_px':[256,464],'grip_candidate_px':grip['xy'],'grip_uncertainty_plus_minus_px':3,'grip_actual_rgba_samples':grip['source_rgba_samples'],'near_hand_polygon_candidate_px':hand['points'],'polygon_uncertainty_plus_minus_px':4,'polygon_complete_ownership_mask':False,'actual_thumb_contour':None,'actual_blade_axis':None,'actual_grasp_cylinder':None,'axis_design_only':axis,'axis_angle_degrees_design':math.degrees(math.atan2(axis[1],axis[0])),'axis_origin':'Root explicit native171 fit design, unchanged/un-normalized; not native171 measurement, guide inference or bone axis','near_fist_replay_policy':'Replay current original body texture with same original UV within this uncertain polygon after independent Sword; bounded visual fit trial, not binary AA ownership','not':'Visible palm patch, not whole-hand bbox or measured handle centre'})
        pixel_checks.append({'frame':index,'canonical':fact(source),'copy':fact(target),'byte_equal':True,'native_decoder':pixels,'visible_height_px':height})
    require(len({a['source_sha256'] for a in assets})==6,'Six unique native171 source PNGs required')
    refs={'native171_raw':fact(FAMILY/'run-primary2-v004/raw/sword_primary_2.png'),'native171_receipt':fact(FAMILY/'generation-control-v001/generation-receipt171-v001.json'),'input_freeze':fact(freezes[0]),'extract_freeze':fact(EXTRACTION_FREEZE),'extract_receipt':fact(FAMILY/'primary2-extraction-v004/extraction-receipt-v004.json'),'measurement_freeze':fact(MEASUREMENT_FREEZE),'measurement':fact(MEASUREMENT),'source_retention_verification':fact(FAMILY/'primary2-measurement-v003/source-verification-v003.json'),'known_standard_timing_diagnosis':fact(FAMILY/'primary2-extraction-v004/standard-timing-diagnosis-v004.json')}
    require(refs['native171_raw']['sha256']=='527f93f7838c9a95f69c1ac16ecb7095c3aeda3e5a9190088aed6bdc89b1af85','Native171 raw pin changed')
    design_risks=['Phase1 low palm167,333 with downward design axis(.35,.937) may put the independent blade below the display sole; estimate only, actual running fit required. Using prior approximate383px front blade at scale.50 gives tip near234,512, about8.3planned screen pixels below displayroot464. Do not silently alter axis.','Phase3 shallower forward axis is intended to reduce helmet clearance risk, not proof of no helmet/hand overlap.','Phases0/5 differ slightly from P1 boundary source; no continuous-fit acceptance.','Hand polygon +/-4px may include pixels on either side of glove/cuff/belt shared ink. OriginalUV replay remains a bounded trial, not exact semantic ownership.']
    marker_path=HERE/'data/primary2-marker-candidate-v002.json'
    write_json(marker_path,{'schema':'fairytale-primary2-native171-runtime-marker-candidate-v2','references':refs,'clip':'sword_primary_2','frame_count':6,'native_facing':1,'display_pivot_px':[256,464],'preview_canvas_size':72*512/416,'body_display_height':72,'sword_scale':.50,'independent_sword_source_grip_px':[99,256],'durations_ms':DURATIONS,'markers':markers,'axis_accepted':False,'thumb_accepted':False,'grip_accepted':False,'foot_lock_accepted':False,'full_motion_accepted':False,'runtime_verified':False,'armor_present':False,'formal_complete_units':0,'design_risks':design_risks})
    inl=HERE/'data/DungeonFairytaleSwordPrimary2V003.inl'
    lines=['#pragma once','#include "DungeonFairytaleSwordBodyV001.inl"','','// STATIC DATA CANDIDATE ONLY: retained native171 body; not installed in UnrealGame/Source.','// V001 supplies FMarker TYPE only. No old human/body/grip/axis DATA is reused.','// Actual171 visible palm candidate +/-3px; uncertain glove polygon +/-4px, NOT complete AA ownership.','// Actual thumb/handle/blade axis remain null. Axis below is Root explicit DESIGN only, not bone.','// Body then independent Sword then current-body same-original-UV near-fist replay: bounded fit trial.','// Root256,464 / maximum body72 / SwordScale.50 / independent sourceGrip99,256 fixed.','// KernelStage1 durations75/75/60/60/135/135ms; standard100x6 preview does NOT pass timing.','// P1->P2 boundaries, grip, helmet clearance, foot-lock and full motion remain unaccepted.',f'// MarkerJSON SHA256: {fact(marker_path)["sha256"]}',f'// Measurement SHA256: {fact(MEASUREMENT)["sha256"]}','namespace DungeonFairytaleSwordPrimary2V003','{','using FMarker = DungeonFairytaleSwordBodyV001::FMarker;','inline constexpr double CanvasSize = 72. * 512. / 416.;','inline constexpr double SwordScale = 0.50;','inline FVector2D IndependentSwordGrip() { return FVector2D(99., 256.); }','inline int32 Count(const FString& Clip) { return Clip == TEXT("sword_primary_2") ? 6 : 0; }','inline const FMarker* Find(const FString& Clip, int32 Index)','{','    if (Clip != TEXT("sword_primary_2") || Index < 0 || Index >= 6) return nullptr;','    static const FMarker Markers[] =','    {']
    for m in markers:
        poly=', '.join(fv(p) for p in m['near_hand_polygon_candidate_px'])
        lines += [f'        // Frame{m["frame"]} SourceSHA256: {m["source"]["sha256"]}; Grip +/-3px; polygon +/-4px.',f'        FMarker{{{fv(m["display_root_px"])}, {fv(m["grip_candidate_px"])}, {fv(m["axis_design_only"])}, TArray<FVector2D>{{{poly}}}}},']
    lines+=['    };','    return &Markers[Index];','}','} // namespace DungeonFairytaleSwordPrimary2V003','']
    with inl.open('x',encoding='utf-8',newline='\n') as out:out.write('\n'.join(lines))
    manifest_path=HERE/'manifests/import-sword-primary2-v002.json'
    write_json(manifest_path,{'schema':'frozen-fairytale-sword-primary2-six-v2','frozen':True,'ready_for_root_import':True,'namespace':NAMESPACE,'asset_count':6,'clip':'sword_primary_2','source_native':171,'canvas_px':[512,512],'display_pivot_px':[256,464],'preview_canvas_size':72*512/416,'body_display_height':72,'visible_body_height_upper_bound_px':416,'native_facing':1,'per_frame_resize':False,'pixel_transform':'none; exact entirePNG byte copies','mirror_policy':'Runtime flip entire body/sword/hand drawing once for -X; native source remains+1','durations_ms':{'Primary2':DURATIONS},'durations_origin':'Existing SWD001 kernelStage1 GetPrimaryPoseFrame; no new clock/input/timing adjustment','standard_preview_durations_ms':[100]*6,'standard_preview_timing_passed':False,'sword_scale':.50,'independent_sword_source_grip_px':[99,256],'references':refs,'marker_json':fact(marker_path),'marker_inl_candidate':fact(inl),'old_production_disk_inventory':fact(baseline),'assets':assets,'recommended_texture_settings':{'compression_settings':'TC_EDITOR_ICON','mip_gen_settings':'TMGS_NO_MIPMAPS','lod_group':'TEXTUREGROUP_UI','never_stream':True,'srgb':True},'source_import_checks_required':['Pinned manifest/references/source sizeSHA','NativePNG CRC/512RGBA/alpha/bbox6unique/max416','Unused actual UE registry AND disk namespace; replace_existing=False','Actual imported_object_paths exactset6; Texture2D dimensions/settings readback; save/readback file hashes','Registry+disk exactset6 and original989package hashes unchanged'],'near_fist_replay_policy':'CurrentBody -> independentSword -> same original texture UV uncertain near-hand polygon, bounded visual trial','axis_design_only':True,'design_risks':design_risks,'actual_UE_registry_unused':None,'runtime_verified':False,'imported':False,'armor_present':False,'full_motion_accepted':False,'continuous_P1_fit_accepted':False,'thumb_accepted':False,'grip_accepted':False,'foot_lock_accepted':False,'formal_complete_units':0,'scope':'Native171 bounded independent-sword fit candidate, no armour or full-content/motion acceptance'})
    after=[verify_freeze(p) for p in freezes];require(before==after,'Frozen sources changed during preparation')
    inventory_after=production_inventory();require(inventory['files']==inventory_after['files'],'Original989 packages changed during readonly candidate preparation')
    write_json(HERE/'source-preflight-v002.json',{'schema':'native171-primary2-runtime-readonly-preflight-v2','created_local':datetime.now().astimezone().isoformat(),'manifest':fact(manifest_path),'native_decoder':fact(DECODER),'native_crc_and_rgba_checks':pixel_checks,'source_unique_count':6,'maximum_visible_height_px':max(x['visible_height_px'] for x in pixel_checks),'frozen_source_lists_before':before,'frozen_source_lists_after':after,'source_lists_same_before_after':True,'original989packages_before_after_unchanged':True,'candidate_disk_namespace_unused':True,'candidate_inl_name_not_in_Source':True,'actual_UE_registry_unused':None,'Root_registry_preflight_required':True,'candidate_inl_compiled':False,'unreal_called':False,'imported':False,'runtime_verified':False,'source_pixels_modified':False,'new_preview_or_media_created':False,'axis_design_only':True})
    readme='''# Native171第二段：独立剑拟合候选 v002

六张curated是171原512RGBA的完整PNG逐字节副本，没有重画、缩放、旋转、镜像、warp或移脚。nativePNG CRC/alpha/六帧唯一/最高416和来源SHA已预检；目前Production实际989包逐SHA前后不变。v009隔离磁盘路径未占用，UE registry须Root实际导入前核对；本候选没有导入/运行/编译。

导入manifest：`manifests/import-sword-primary2-v002.json`，schema `frozen-fairytale-sword-primary2-six-v2`。目标 `/Game/Production/ArtTrials/EV048/v009/HeroSwordPrimary2` 六名 `T_Fairytale_SwordPrimary2_000_v002`…`005_v002`。保留旧989包，实际registry/disk exactset、imported paths、Texture设置、save/readback均由Root执行。assets沿旧source/bytes/SHA/bbox/name/package/object格式，不把旧six-v1 importer原样调用到新manifest。

`data/DungeonFairytaleSwordPrimary2V003.inl`/同名namespace只是候选，不写Source。仅借旧FMarker类型，不借旧坐标。Find只支持sword_primary_2六相。256,464显示pivot、最高72px、Canvas72*512/416、独立剑.50及剑源Grip99,256不变。实际171棕掌候选207313/167333/281318/311253/280275/207313±3；近手polygon±4，不是完整AA ownership或已接受握柄/拇指。currentBody→独立Sword→同原UV近拳回绘仅为有限试装。

六轴原样采用Root新设计：(.94,-.341)/(.35,.937)/(.8,.6)/(.9,-.436)/(.95,-.312)/(.94,-.341)。它们不是测出的骨/柄/刃轴，不归一化偷改。相3较ArcB浅向前是避盔设计意图，未证明无重叠。相1下向轴可能把刀尖放到脚线下：沿旧约383源px前刃、.50估算tip约234,512，低于root464约48源px≈8.3展示px；这是旧tip近似的设计估算，必须实景检查，不擅自换轴。0/5与P1边界像素不同，不宣称连续fit。

75/75/60/60/135/135来自既有SWD001第二段内核；standard预览仍100×6=600ms，未重时/未通过timingQA。只有身体与独立剑的候选，本段无甲；连续动作、持剑、脚锁、音效和完整内容均未接受。所有新文件只在本family，没有新展示图或视频。
'''
    with (HERE/'README.md').open('x',encoding='utf-8',newline='\n') as out:out.write(readme)
    files=[fact(p) for p in sorted(HERE.rglob('*')) if p.is_file()]
    freeze=HERE/'ready-for-root-import-freeze-v002.json'
    write_json(freeze,{'schema':'fairytale-primary2-native171-runtime-candidate-freeze-v2','created_local':datetime.now().astimezone().isoformat(),'file_count':len(files),'total_bytes':sum(x['bytes'] for x in files),'files':files,'status':'ready-for-Root-import candidate; not imported','unreal_called':False,'armor_present':False,'full_motion_accepted':False,'formal_complete_units':0,'source_frozen_lists_and_original989_unchanged':True,'new_media_created':False})
    for row in files:require(fact(row['path'])==row,'Fresh candidate freeze mismatch')
    print(json.dumps({'freeze':fact(freeze),'manifest':fact(manifest_path),'marker_json':fact(marker_path),'marker_inl':fact(inl),'file_count_excluding_freeze':len(files),'bytes_excluding_freeze':sum(x['bytes'] for x in files),'file_count_including_freeze':len(files)+1,'bytes_including_freeze':sum(x['bytes'] for x in files)+freeze.stat().st_size,'actual_curated_count':6,'source_unique_count':6,'maximum_visible_height':max(x['visible_height_px'] for x in pixel_checks),'original_packages_unchanged':989,'imported':False},ensure_ascii=False,indent=2))

if __name__=='__main__':main()