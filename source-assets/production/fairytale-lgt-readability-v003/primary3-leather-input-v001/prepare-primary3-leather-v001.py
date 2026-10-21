"""Prepare three six-phase component-only leather edit inputs, without generation."""
from pathlib import Path
import datetime
import hashlib
import json
import platform
import shutil
import subprocess
import sys

import PIL
import numpy as np
from PIL import Image


OUT = Path(__file__).resolve().parent
PROJECT = Path("F:/Ourgame")
FAMILY = PROJECT / "source-assets/production/fairytale-lgt-readability-v003"
SG = Path("C:/Users/22499/.codex/skills/sprite-gen")
PYTHON = SG / ".venv/Scripts/python.exe"
CLIP = int(OUT.name.split("-")[0].replace("primary", ""))
TIMES = [75,75,60,60,135,135] if CLIP == 2 else [110,110,60,60,160,160]
WATCHED = {}
OWNERS = ["BodyRest","NearArmWithoutHand","HelmetForeground","NearHand"]
COMPONENTS = [
    {"component":"Chest","token":"chest","runtime":"Chest","ready_native":184,"ready_png":FAMILY/"chest184-extraction-v001/run-shared-diagnostic-v001/frames/leather_chest_sword_ready/frame-0.png","ready_sha":"9c1f63e4f710223c567a9e1fd9795490513aa88ee2ee4cd05425833a33af1312","window":[90,90],"min_used":512},
    {"component":"NearShoulder","token":"nearshoulder","runtime":"ShoulderNear","ready_native":186,"ready_png":FAMILY/"near186-extraction-v001/run-shared-diagnostic-v001/frames/leather_nearshoulder_sword_ready/frame-0.png","ready_sha":"0aa081a7d3ae814827c654c545b86dcc3a0e4bc0f5b32e04c0541509a1d0bd8c","window":[60,44],"min_used":512},
    {"component":"FarShoulder","token":"farshoulder","runtime":"ShoulderFar","ready_native":187,"ready_png":FAMILY/"far187-extraction-v001/run-shared-smallcomponent-v002/frames/leather_farshoulder_sword_ready/frame-0.png","ready_sha":"032e2bf4e4e2537191531ace4c90076aed3d899ac931db9be3c3b99aaaf267f0","window":[32,30],"min_used":256},
]


def pin(path, watch=True):
    data = path.read_bytes()
    result = {"path": path.as_posix(), "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}
    if watch and not path.is_relative_to(OUT):
        WATCHED[path] = result
    return result


def checked(expected):
    path = Path(expected["path"])
    if pin(path) != expected:
        raise RuntimeError(f"Source pin mismatch: {path}")
    return path


def write(relative, data):
    path = OUT / relative
    if not path.is_relative_to(OUT):
        raise RuntimeError("Ownership boundary")
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = data if isinstance(data, str) else json.dumps(data, ensure_ascii=False, indent=2) + "\n"
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(payload)
    return path


def copy_exact(source, relative):
    target = OUT / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        raise RuntimeError("Existing reference copy")
    shutil.copy2(source, target)
    before, after = pin(source), pin(target)
    if before["bytes"] != after["bytes"] or before["sha256"] != after["sha256"]:
        raise RuntimeError("Reference byte copy mismatch")
    return target


def load(path):
    return json.loads(Path(path).read_text("utf-8-sig"))


def rgba(path):
    with Image.open(path) as im:
        if im.mode != "RGBA" or im.size != (512,512):
            raise RuntimeError("Expected actual 512 RGBA source")
        return np.asarray(im).copy()


def verify_manifest_import(manifest_path, reference_path):
    manifest = load(manifest_path)
    reference = load(reference_path)
    receipt_path = checked(reference)
    receipt = load(receipt_path)
    if not receipt["success"] or receipt["actual_count"] != len(manifest["assets"]) or receipt["saved_count"] != len(manifest["assets"]):
        raise RuntimeError("Actual import receipt incomplete")
    if Path(receipt["manifest"]).resolve()!=manifest_path.resolve() or receipt["manifest_sha256"]!=pin(manifest_path)["sha256"]:
        raise RuntimeError("Actual receipt is not this manifest")
    receipt_assets = {(a["component"] if "component" in a else a["clip"],a["frame"]):a for a in receipt["assets"]}
    results=[]
    for asset in manifest["assets"]:
        key=(asset.get("component",asset.get("clip")),asset["frame"])
        actual=receipt_assets[key]
        for field in ["source","source_bytes","source_sha256","name","package_path","object_path"]:
            if actual[field]!=asset[field]:raise RuntimeError("Manifest/receipt source mismatch")
        if actual["actual_object_type"]!="Texture2D":raise RuntimeError("Not imported Texture2D")
        source=Path(asset["source"]);actual_source=pin(source)
        if (actual_source["bytes"],actual_source["sha256"])!=(asset["source_bytes"],asset["source_sha256"]):raise RuntimeError("Current PNG source differs from imported")
        saved=pin(Path(actual["saved_uasset"]))
        if (saved["bytes"],saved["sha256"])!=(actual["saved_bytes"],actual["saved_sha256"]):raise RuntimeError("Actual imported UAsset changed")
        results.append({"component":key[0],"frame":key[1],"source":actual_source,"object_path":asset["object_path"],"saved_uasset":saved})
    pin(reference_path)
    return manifest, {"manifest":pin(manifest_path),"actual_import_receipt":pin(receipt_path),"receipt_reference":pin(reference_path),"verified_assets":results}


def component_instruction(name):
    if name == "Chest":
        return "Draw ONLY the waist-length supple brown leather jerkin, round golden front clasp, belt and attached small pouch of Ready184. Keep the same right-facing construction: large near-arm opening on image LEFT, clasp toward image RIGHT, pouch on its original image-LEFT physical side when visible. Foreshorten for the action, without flipping the torso. Remove metal plate/boss, both shoulder caps and grey undercloth."
    if name == "NearShoulder":
        return "Draw ONLY Ready186's short rounded foreground brown leather shoulder cap. Preserve the action cap's six turns and foreshortenings. No grey inner lining, low hanging oval ring, chest, torso, waist, pouch, far cap, arm, hand or complete vest."
    return "Draw ONLY Ready187's tiny narrow curved far-side brown leather tab, with compressed FAR perspective. Preserve the action's six orientations, not the old broad metal shoulder silhouette. No broad near/front cap, mirrored near cap, long oval ring, lining, adjacent torso seam, chest, pouch or complete vest."


def main():
    if Path(sys.executable).resolve()!=PYTHON.resolve() or CLIP not in [2,3]:raise RuntimeError("Use sprite-gen venv")
    if OUT!=FAMILY/f"primary{CLIP}-leather-input-v001" or list(OUT.glob("run-*")):raise RuntimeError("Unexpected/existing candidate")
    runtime = PROJECT / "source-assets/production" / ("fairytale-armor-sword-primary2-runtime-v001" if CLIP==2 else "fairytale-sword-primary3-runtime-v001")
    candidate_path = runtime/"candidate-import-v001.json"
    manifest_path = runtime/f"manifests/import-sword-armor-primary{CLIP}-v001.json"
    manifest, import_proof = verify_manifest_import(manifest_path,runtime/"manifests/actual-import-receipt-ref.json")
    candidate=load(checked(manifest["references"]["candidate"]))
    if checked(manifest["references"]["candidate"])!=candidate_path:raise RuntimeError("Unexpected current import candidate")
    expected_native=[171,172,173,174] if CLIP==2 else [175,176,177,178]
    if manifest["source_requests"]!=expected_native or manifest["phase_durations_ms"]!=TIMES:raise RuntimeError("Real clip/native/timing differs")
    source=PROJECT/"UnrealGame/Source/CodexDungeon"
    renderer=source/"DungeonFairytaleSwordPresentation.cpp"
    inl=source/("DungeonFairytaleSwordPrimary2ArmorV001.inl" if CLIP==2 else "DungeonFairytaleSwordPrimary3V001.inl")
    renderer_text=renderer.read_text("utf-8-sig");inl_text=inl.read_text("utf-8-sig")
    if f'DungeonFairytaleSwordPrimary{CLIP}'+("ArmorV001::GetTexture" if CLIP==2 else "V001::GetTexture") not in renderer_text:raise RuntimeError("Current renderer does not route this armor")
    if manifest["namespace"]+'/' not in inl_text or f'T_Fairytale_SwordPrimary{CLIP}%s_%03d_v001' not in inl_text:raise RuntimeError("Actual renderer package naming differs")
    partition_path=PROJECT/f"source-assets/production/fairytale-sword-primary{CLIP}-body-partition-v001/proof-v001.json"
    partition=load(partition_path)
    if partition["schema"]!=f'native{expected_native[0]}-four-owner-original-RGBA-proof-v1':raise RuntimeError("Wrong actual body native")
    if CLIP==2:
        body_runtime=PROJECT/"source-assets/production/fairytale-sword-primary2-runtime-v002/axis1-correction-v001"
        body_manifest, body_import_proof=verify_manifest_import(body_runtime/"manifests/import-sword-primary2-v002.json",body_runtime/"manifests/actual-import-receipt-ref.json")
        if body_manifest["namespace"]+'/ ' in renderer_text:raise RuntimeError("Unexpected namespace formatting")
        if body_manifest["namespace"]+'/' not in renderer_text or 'const int32 Version=Second?(SecondBodyTrial?2:1)' not in renderer_text:raise RuntimeError("Current primary2 wholebody branch differs")
    else:
        body_manifest=manifest;body_import_proof=import_proof
    body_rows=[]
    by_asset={(a["component"],a["frame"]):a for a in manifest["assets"]}
    for frame in range(6):
        pframe=partition["frames"][frame];original=checked(pframe["source"]);original_rgba=rgba(original)
        expected_run='/run-primary2-v004/curated/' if CLIP==2 else '/run-primary3-v001/curated/'
        if expected_run not in original.as_posix():raise RuntimeError("Body generation version changed")
        whole_asset=body_manifest["assets"][frame] if CLIP==2 else by_asset['Body',frame]
        whole=Path(whole_asset["source"])
        if whole.read_bytes()!=original.read_bytes():raise RuntimeError("Imported full body not canonical body generation")
        layers=[];arrays=[]
        for owner in OWNERS:
            asset=by_asset[owner,frame];current=Path(asset["source"])
            layer=checked(next(r["file"] for r in pframe["layers"] if r["owner"]==owner))
            if current.read_bytes()!=layer.read_bytes():raise RuntimeError("Runtime body owner differs from original partition")
            arrays.append(rgba(current))
            layers.append({"owner":owner,"current_imported_source":pin(current),"original_partition_source":pin(layer),"object_path":asset["object_path"],"byte_exact":True})
        if not np.array_equal(np.sum(np.stack(arrays),axis=0,dtype=np.uint16),original_rgba.astype(np.uint16)):raise RuntimeError("Four runtime body layers do not reconstruct actual canonical body")
        body_rows.append({"frame":frame,"duration_ms":TIMES[frame],"actual_body_native_request":expected_native[0],"actual_canonical_body":pin(original),"current_full_body_source":pin(whole),"current_full_body_object_path":whole_asset["object_path"],"existing_runtime_four_layers_to_keep":layers,"full_RGBA_reconstruction_exact":True,"new_body_features_or_B_measured":False,"body_attached_to_image_editor":False})
    source_map={"schema":f"primary{CLIP}-actual-runtime-source-version-mapping-v001","created_local":datetime.datetime.now().astimezone().isoformat(),
        "current_renderer":pin(renderer),"current_texture_resolver":pin(inl),"actual_import":import_proof,"full_body_import":body_import_proof,
        "partition_proof":pin(partition_path),"body_native_request":expected_native[0],"body_run_version":"run-primary2-v004" if CLIP==2 else "run-primary3-v001",
        "full_body_texture_version":"v002" if CLIP==2 else "v001","full_body_namespace":body_manifest["namespace"],"armor_and_four_body_layer_namespace":manifest["namespace"],
        "marker_version":"DungeonFairytaleSwordPrimary2V003" if CLIP==2 else "DungeonFairytaleSwordPrimary3V002 in equipment-bound mode",
        "body_frames":body_rows,"native_run_Texture_and_marker_versions_are_distinct":True,"source_identity_not_inferred_from_similar_directory_name":True,
        "full_body_role":"Actual runtime geometry source and later fit reference ONLY; not an appearance identity or a generation reference","old_component_rows":[]}
    rows=[]
    for number,c in enumerate(COMPONENTS):
        name,token=c['component'],c['token'];registration=[r for r in candidate['registration'] if r['component']==name]
        old_frame_source=registration[0]['source' if CLIP==2 else 'original_component']
        old_run=Path(old_frame_source['path']).parents[1]
        request_path=old_run/'sprite-request.json';old_request=load(request_path);state=next(iter(old_request['states']))
        if old_request['states'][state]['frames']!=6 or old_request['states'][state]['durations_ms']!=TIMES:raise RuntimeError("Old same-component recipe mismatch")
        raw=old_run/f'raw/{state}.png';frames_manifest=old_run/'frames/frames-manifest.json';fm=load(frames_manifest);shared=fm['rows'][0]['shared_row_fit']
        if shared['policy']!='one_raw_component_max_extent_scale_for_entire_row' or shared['per_frame_scale_normalization'] is not False:raise RuntimeError("Unexpected old scale policy")
        receipt_path=(old_run.parent/f'{token}-extraction-v001/extraction-receipt-v001.json') if CLIP==2 else old_run.parent/f'standard-extraction-v001/{name}-receipt-v001.json'
        receipt=load(receipt_path)
        if receipt['native_request']!=expected_native[number+1] or checked(receipt['raw'])!=raw:raise RuntimeError("Same-component raw is not actual imported generation")
        old_sources=[]
        for frame in range(6):
            reg=next(r for r in registration if r['frame']==frame);before=checked(reg['source' if CLIP==2 else 'original_component']);asset=by_asset[c['runtime'],frame];current=Path(asset['source'])
            delta=reg['integer_translation_xy' if CLIP==2 else 'integer_offset'];inverse=np.roll(rgba(current),(-delta[1],-delta[0]),(0,1))
            if not np.array_equal(inverse,rgba(before)):raise RuntimeError("Imported armor does not invert to old curated component")
            old_sources.append({'frame':frame,'old_curated_component':pin(before),'old_integer_registered_import_source':pin(current),'object_path':asset['object_path'],'old_delta_history_only':delta,'inverse_RGBA_exact':True,'old_A_B_or_delta_reused_for_new_leather':False})
        with Image.open(raw) as im:raw_size=list(im.size);raw_mode=im.mode
        source_map['old_component_rows'].append({'component':name,'native_request':receipt['native_request'],'run':old_run.as_posix(),'request':pin(request_path),'raw':pin(raw),'raw_canvas_px':raw_size,'raw_mode':raw_mode,'extraction_receipt':pin(receipt_path),'frames_manifest':pin(frames_manifest),'actual_old_shared_row_fit':shared,'actual_imported_sources':old_sources,'authority':'Only six-phase motion/perspective/geometry basis; never old metal identity or new A/B'})
        anchor=c['ready_png']
        if pin(anchor)['sha256']!=c['ready_sha']:raise RuntimeError("Ready sole appearance anchor changed")
        rgba(anchor)
        new_state=f'leather_{token}_sword_primary{CLIP}';window=c['window'];margin=[(512-n)//2 for n in window]
        action=f'Edit six isolated {name} Primary{CLIP} motion views into Ready{c["ready_native"]} brown leather component, no whole body.'
        seed={'version':1,'kind':'sprite-gen-request','engine':'component-row','states':{new_state:{'frames':6,'fps':10,'loop':False,'action':action,'durations_ms':TIMES}},'cell':{'width':512,'height':512,'safe_margin_x':margin[0],'safe_margin_y':margin[1]},'motion_phase_guides':False,'fit':{'pixel_unfake':False,'resample':'lanczos','align_x':'bbox-center','align_y':'bottom','ground_frames':False,'segmentation':'components','shared_row_scale':True},'chroma':{'mode':'rgb','unmix_reach':4,'spill_max_fraction':0.005}}
        seed_path=write(f'requests/{token}-numeric-input-v001.json',seed);run=OUT/f'run-{token}-primary{CLIP}-v001'
        argv=[str(PYTHON),'-B','-X','utf8',str(SG/'scripts/prepare_sprite_run.py'),'--out-dir',str(run),'--character-id',f'fairytale-soft-leather-{token}-primary{CLIP}-v001','--base-image',str(anchor),'--description',action,'--style',f'Actual isolated Ready{c["ready_native"]} sole appearance identity; old component action row motion only.','--cell-size','512','--chroma-key','#00FF00','--request',str(seed_path)]
        result=subprocess.run(argv,capture_output=True,text=True,encoding='utf-8');log=write(f'logs/prepare-{token}-v001.log',result.stdout+result.stderr)
        command=write(f'logs/prepare-{token}-command-v001.json',{'argv':argv,'actual_exit_code':result.returncode,'log':pin(log)})
        if result.returncode:raise RuntimeError("Standard prepare failed")
        request=run/'sprite-request.json';copy_exact(request,f'standard-output-before-explicit/{token}-sprite-request.json');q=load(request);changes={}
        for key in ['fit','chroma','motion_phase_guides']:
            if q.get(key)!=seed[key]:changes[key]={'before':q.get(key),'after':seed[key]};q[key]=seed[key]
        if q['states'][new_state].get('durations_ms')!=TIMES:
            changes['durations_ms']={'before':q['states'][new_state].get('durations_ms'),'after':TIMES};q['states'][new_state]['durations_ms']=TIMES
        request.write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        write(f'requests/{token}-explicit-fields-v001.json',{'changes_after_standard_prepare':changes,'final':pin(request)})
        target=copy_exact(raw,f'run-{token}-primary{CLIP}-v001/references/edit-target-old-primary{CLIP}.png');appearance=run/'base-source.png'
        if pin(appearance)['sha256']!=c['ready_sha']:raise RuntimeError("Appearance copy is not byte exact")
        prompt=run/f'prompts/{new_state}.txt';copy_exact(prompt,f'standard-output-before-explicit/{token}-standard-prompt.txt')
        text=f"""EDIT FIRST IMAGE: the actual old {name} Primary{CLIP} row, {raw_size[0]}x{raw_size[1]}. It supplies ONLY six action perspectives, phase order and spacing. SECOND IMAGE: actual isolated Ready{c['ready_native']}, the SOLE brown leather appearance identity. Discard old grey metal, boss and ornament.

{component_instruction(name)}

Exactly six separated components, left-to-right windup0/1, strike2/3, recovery4/5. Follow the paired action's poses and foreshortening while preserving the same native right-facing identity. No back-view reversal or whole-frame mirror, no cloned idle parts. Keep coarse ink, warm brown/tan leather and consistent construction. No whole person, head/helmet, eyes, body, arms/hands, weapon, ground, cast shadow, text, boxes or another component.

Replace every unwanted pixel with flat OPAQUE GREEN #00FF00; keep row canvas and spacing. Timing metadata {TIMES} ms; later shared-HD fit {window[0]}x{window[1]} in512 cells, one scale for all six. New A/B/delta remain null; this is not fit or animation approval.
"""
        if len(text.split())>=270:raise RuntimeError("Prompt must stay concise")
        prompt.write_text(text,encoding='utf-8')
        qa=write(f'requests/{token}-extraction-configuration-proposal-v001.json',{'subject':'character','explicit_component_min_used_pixels':c['min_used'],'future_only_not_run':True,'reason':'Tiny far rigid tab: floor256 explicitly planned from actual Ready187 component evidence, retain count/chroma/edge gates; no effect relabel, fill, enlargement or per-frame normalization.' if name=='FarShoulder' else 'Keep default512 sparse floor.','ready187_component_floor_evidence':pin(FAMILY/'far187-extraction-v001/numeric-diagnostic-v002.json') if name=='FarShoulder' else None,'fit_window_design_px':window,'shared_row_scale':True,'per_frame_scale_normalization':False,'new_raw_measured_scale':None,'fit_accepted':False,'future_cli':['--min-used-pixels',str(c['min_used'])]})
        rows.append({'component':name,'runtime_component':c['runtime'],'state':new_state,'clip':f'sword_primary_{CLIP}','run_dir':run.as_posix(),'raw_output_path':(run/f'raw/{new_state}.png').as_posix(),'prompt':pin(prompt),'request':pin(request),'prompt_word_count':len(text.split()),'reference_images_in_order':[{'role':f'FIRST_actual_old_same_component_primary{CLIP}_edit_target_motion_only','file':pin(target)},{'role':'SECOND_actual_same_component_Ready_SOLE_appearance_identity','file':pin(appearance)}],'reference_count':2,'frame_count':6,'durations_ms':TIMES,'fit_window_design_px':window,'shared_row_scale':True,'extraction_configuration_proposal':pin(qa),'old_action_native_request':receipt['native_request'],'new_Ready_appearance_native_request':c['ready_native'],'actual_runtime_body_native_request':expected_native[0],'actual_runtime_body_pins':[b['actual_canonical_body'] for b in body_rows],'future_component_A':[None]*6,'future_body_target_B':[None]*6,'future_integer_delta':[None]*6,'native_request_number':None,'planned_native_number_if_original_order':None,'standard_prepare_command':argv,'standard_prepare_command_record':pin(command),'standard_prepare_exit_code':result.returncode,'transparent_background':False,'background_hex':'#00FF00','generation_ready':False,'root_edit_target_and_anchor_view_required_before_generation':True,'body_or_full_base_attached':False,'standard_layout_guide_not_attached_to_editor':True})
    mapping=write('actual-runtime-source-version-mapping-v001.json',source_map)
    toolchain=write('toolchain-v001.json',{'python_executable':sys.executable,'python_version':platform.python_version(),'Pillow':PIL.__version__,'numpy':np.__version__,'tools':[pin(SG/'scripts/prepare_sprite_run.py'),pin(SG/'sprite_gen/gen/prepare.py'),pin(SG/'SKILL.md')],'installed_tools_modified':False})
    handoff=write(f'primary{CLIP}-leather-native-input-draft-v001.json',{'schema':f'primary{CLIP}-leather-three-component-six-phase-native-input-draft-v001','created_local':datetime.datetime.now().astimezone().isoformat(),'source_event':'EV-048','rows':rows,'actual_runtime_source_version_mapping':pin(mapping),'toolchain':pin(toolchain),'generation_ready':False,'root_review_required_before_generation':True,'original179_or131_full_body_attached':False,'only_actual_Ready_component_appearance_identity':True,'new_A_B_delta_all_null':True,'native_request_numbers_not_reserved':True,'native_generated':False,'UE_import_or_Source_called':False,'new_guides_or_media_viewed':False,'helper_compatibility':'Row fields follow prior component native helper. Root must create/version a scope-specific Primary2/3 helper and review these exact targets/anchors before generation; no stale Ready4/Primary1 scope or previous approvals are carried forward.','formal_complete_units':0})
    mismatches=[str(q) for q,before in WATCHED.items() if pin(q,False)!=before]
    if mismatches:raise RuntimeError(f'Read-only inputs changed: {mismatches}')
    write('preparation-verification-v001.json',{'standard_prepare_runs':3,'actual_prepare_exit_codes':[r['standard_prepare_exit_code'] for r in rows],'read_only_source_count':len(WATCHED),'read_only_source_mismatches':[],'actual_runtime_body_frames_verified':6,'runtime_body_owner_byte_checks':24,'current_imported_armor_inverse_RGBA_checks':18,'new_raw_files':[str(p) for p in OUT.glob('run-*/raw/*') if p.is_file()],'future_A_B_delta_null':True,'generation_called':False,'new_guides_viewed':False})
    write('HANDOFF.md',f"""# Primary{CLIP} 软皮三组件六相输入

三次标准prepare实际exit0；每行仅旧同组件动作raw编辑target＋实际Ready184/186/187单组件512RGBA appearance。当前renderer→实际import manifest/receipt→现UAsset/源PNG→原四层/身体已核；精确版本见 actual-runtime-source-version-mapping-v001.json。Body{expected_native[0]}实为 {'run-primary2-v004，whole-body Texture v002/marker V003，v009全身与v010四层' if CLIP==2 else 'run-primary3-v001，v011全身与四层，Bound marker V002'}，不是依据相似目录猜测。身体仅作未来动作/fit源索引，未附编辑器，不作appearance。179/131未重新附加。

六相{TIMES} ms，总{sum(TIMES)}ms。共同行HD窗口Chest90×90/Near60×44/Far32×30，min建议512/512/显式tiny256。Far不是effect，不填像素/放大/改门；实测scale待真实提取。18新A/B/delta全null，旧灰甲特征/offset不复用。

root需先E留档查看targets/anchors与新输入，再批准相应helper版本/生成。generation_ready=false，无native预留/调用、提取、导入、UE、Source/工具/README/ledger/进度/媒体改动；未查看任何新guide。后续curated选择、feature实测、整数fit和真实动作验收仍未执行。
""")
    files=[pin(p,False) for p in sorted(OUT.rglob('*')) if p.is_file()]
    for entry in files:entry['path']=Path(entry['path']).relative_to(OUT).as_posix()
    freeze=write('input-freeze-v001.json',{'schema':f'primary{CLIP}-leather-input-freeze-v001','files':files,'file_count_excluding_manifest':len(files),'total_bytes_excluding_manifest':sum(r['bytes'] for r in files),'generation_ready':False,'generated':False,'new_media_viewed':False})
    print(json.dumps({'handoff':pin(handoff),'source_version_mapping':pin(mapping),'freeze':pin(freeze),'prepare_exit_codes':[r['standard_prepare_exit_code'] for r in rows],'prompt_words':[r['prompt_word_count'] for r in rows],'source_rechecks':len(WATCHED),'source_mismatches':[],'files_excluding_freeze':len(files),'bytes_excluding_freeze':sum(r['bytes'] for r in files),'generation_ready':False},indent=2))


if __name__=='__main__':main()
