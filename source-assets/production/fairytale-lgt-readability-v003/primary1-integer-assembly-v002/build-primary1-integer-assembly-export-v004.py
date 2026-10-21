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
OLD = Path("F:/Ourgame/source-assets/production/fairytale-armor-sword-primary1-v001")
DURATIONS = [85,85,60,60,155,155]
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
    """Standard curated export from exact pre-curation copies; no geometric edit here."""
    name = component["component"]
    state = component["state"]
    original_run = Path(component["frames"][0]["source"]["path"]).parents[2]
    run = OUT / "selected-runs-canonical-v002" / name
    for relative in ["sprite-request.json", "frames/frames-manifest.json", f"raw/{state}.png"]:
        copy_exact(original_run / relative, f"selected-runs-canonical-v002/{name}/{relative}")
    for row in component["frames"]:
        copy_exact(require_pin(row["source"]), f"selected-runs-canonical-v002/{name}/frames/{state}/frame-{row['frame']}.png")
    sys.path.insert(0, str(SG))
    from sprite_gen.curate.curation import load_curation, stamp_curation, state_plan, frame_variant, pixel_snap_scale
    if load_curation(run) is not None:
        raise RuntimeError("Unexpected prior selection")
    payload = stamp_curation(run, {"version": 1, "kind": "sprite-gen-curation",
        "states": {state: {"selected": list(range(6)), "transforms": {}}}})
    write(f"selected-runs-canonical-v002/{name}/curation.json", payload)
    loaded = load_curation(run)
    request = json.loads((run / "sprite-request.json").read_text("utf-8-sig"))
    if frame_variant(loaded, state) != "pixel" or pixel_snap_scale(request) is not None or request["fit"]["pixel_unfake"] is not False:
        raise RuntimeError("Expected canonical HD frame files with no pixel snapping")
    order, transforms = state_plan(loaded, state, 6)
    if order != list(range(6)) or transforms:
        raise RuntimeError("Curation selection changed pixels/order")
    argv = [str(PYTHON), "-B", "-X", "utf8", str(SG / "scripts/export_curated_pngs.py"),
        "--run-dir", str(run), "--state", state, "--selected-only"]
    result = subprocess.run(argv, capture_output=True, text=True, encoding="utf-8")
    log = write(f"logs-retry-v002/export-curated-{name}-v001.log", result.stdout + result.stderr)
    record = write(f"logs-retry-v002/export-curated-{name}-command-v001.json", {"argv": argv,
        "actual_exit_code": result.returncode, "log": pin(log)})
    if result.returncode:
        raise RuntimeError(f"Standard curated export failed: {name}, exit {result.returncode}")
    exported = {}
    for row in component["frames"]:
        frame = row["frame"]
        original = require_pin(row["source"])
        output = run / "curated" / f"frame-{frame}.png"
        if not np.array_equal(rgba(original), rgba(output)):
            raise RuntimeError("Identity curated export changed RGBA")
        exported[frame] = {"pre_curation_source": pin(original), "exact_local_frame_copy": pin(run / "frames" / state / f"frame-{frame}.png"),
            "curated_export": pin(output), "curation_sidecar": pin(run / "curation.json"),
            "export_command_record": pin(record), "selected_index": frame, "canonical_file_variant_label": "pixel", "fit_pixel_unfake": False, "pixel_snap_scale": None, "identity_export_RGBA_equal": True,
            "selection_role": "Root selected all six actual components for integer fit trial, not final art/motion acceptance"}
    return exported


def main():
    parser = argparse.ArgumentParser(description="Candidate only; requires corrected mounts against actual runtime v003 body.")
    parser.add_argument("--mounts", required=True, type=Path)
    parser.add_argument("--mounts-sha256", required=True)
    parser.add_argument("--mounts-freeze", required=True, type=Path)
    parser.add_argument("--mounts-freeze-sha256", required=True)
    args = parser.parse_args()
    if Path(sys.executable).resolve() != PYTHON.resolve():
        raise RuntimeError("Use sprite-gen venv")
    if OUT != FAMILY / "primary1-integer-assembly-v002" or (OUT / "assembly-proof-v002.json").exists():
        raise RuntimeError("Unexpected/existing output")
    mounts_path = args.mounts.resolve()
    mount_freeze_path = args.mounts_freeze.resolve()
    if mounts_path == FAMILY / "primary1-visible-mounts-v001/all18-mounts-v001.json":
        raise RuntimeError("Rejected v001 B was designed against wrong body generation; new corrected mounts required")
    if pin(mounts_path)["sha256"] != args.mounts_sha256 or pin(mount_freeze_path)["sha256"] != args.mounts_freeze_sha256:
        raise RuntimeError("Corrected mounts/freeze hash mismatch")
    mount_freeze = json.loads(mount_freeze_path.read_text("utf-8-sig"))
    for entry in mount_freeze["files"]:
        require_pin(entry)
    if pin(mounts_path) not in mount_freeze["files"]:
        raise RuntimeError("Corrected mounts not in supplied freeze")
    mounts = json.loads(mounts_path.read_text("utf-8-sig"))
    if mounts["fit_accepted"] is not False or len(mounts["rows"]) != 18:
        raise RuntimeError("Expected 18 corrected trial mounts, not fit acceptance")
    index_path = require_pin(mounts["source_index"])
    inventory = json.loads(index_path.read_text("utf-8-sig"))
    if inventory["selected_native_by_component"] != {"Chest":192,"NearShoulder":189,"FarShoulder":190}:
        raise RuntimeError("Wrong native rows selected")
    keyed = {(row["frame"], row["component"]):row for row in mounts["rows"]}
    if set(keyed) != {(i,n) for i in range(6) for n in ARMOR_NAMES}:
        raise RuntimeError("Duplicate/missing mounts")
    selected = {(row["frame"],component["component"]):row for component in inventory["components"] for row in component["frames"]}
    old_registration = json.loads((OLD / "macro-registration-primary1-v001/feature-measurement-registration-v001.json").read_text("utf-8-sig"))
    partition_path = require_pin(old_registration["body_partition_proof"])
    partition = json.loads(partition_path.read_text("utf-8-sig"))
    old_candidate_path = OLD / "macro-registration-primary1-v001/candidate-import-v001.json"
    old_candidate = json.loads(old_candidate_path.read_text("utf-8-sig"))
    current_body = {(r["frame"],r["component"]):r["source"] for r in old_candidate["textures"] if r["component"] in BODY_NAMES}
    native_source = FAMILY / "primary1-native-source-v002/DungeonFairytaleSwordPresentation.cpp"
    source_text = native_source.read_text("utf-8-sig")
    if 'T_Fairytale_LeatherPrimary1%s_%03d_v001' not in source_text or '/Game/Production/ArtTrials/EV048/v013/HeroLeatherPrimary1/' not in source_text:
        raise RuntimeError("v013 package proposal disagrees with source-v002")
    pin(native_source)
    # Validate every actual body and A/B mapping before creating any PNG.
    for frame in range(6):
        actual_body = partition["frames"][frame]["source"]
        if '/run-primary1-v003/curated/' not in actual_body["path"]:
            raise RuntimeError("Unexpected current body generation")
        require_pin(actual_body)
        for name in ARMOR_NAMES:
            row = keyed[frame,name]
            if row["body"] != actual_body or row["duration_ms"] != DURATIONS[frame]:
                raise RuntimeError("B review reference must be actual unchanged v003 runtime body")
            if row["source"] != selected[frame,name]["source"]:
                raise RuntimeError("Mounted source not selected pre-curation source")
            array = rgba(require_pin(row["source"]))
            a,b,delta = row["A_source_px"],row["B_body_design_source_px"],row["integer_delta_xy"]
            if not all(type(x) is int for x in a+b+delta) or delta != [b[0]-a[0],b[1]-a[1]]:
                raise RuntimeError("Invalid explicit integer feature registration")
            if array[a[1],a[0]].tolist()!=row["A_observed_rgba"] or array[a[1],a[0],3]<128:
                raise RuntimeError("Actual visible A source pixel changed")
            placed=translate(array,*delta)
            if not np.array_equal(translate(placed,-delta[0],-delta[1]),array):
                raise RuntimeError("Translation clips/changes RGBA")
    copy_exact(mounts_path,"inputs-retry-v002/corrected18-mounts.json")
    copy_exact(mount_freeze_path,"inputs-retry-v002/corrected18-mounts-freeze.json")
    copy_exact(index_path,"inputs-retry-v002/selected18-pre-curation-index.json")
    copy_exact(partition_path,"inputs-retry-v002/original-four-body-partition-proof.json")
    copy_exact(old_candidate_path,"inputs-retry-v002/original-P1-runtime-texture-index.json")
    export_records={c["component"]:export_selection(c) for c in inventory["components"]}
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
                "B_design_uncertainty_px":row["B_design_uncertainty_px"],"actual_runtime_body":original_body_pin,
                "B_original_body_RGBA_diagnostic_only":original_body[b[1],b[0]].tolist(),"integer_delta_xy":delta,
                "A_maps_exactly_to_B":placed[b[1],b[0]].tolist()==array[a[1],a[0]].tolist(),
                "source_nonzero_RGBA_bbox":pixel_bbox(array),"translated_nonzero_RGBA_bbox":pixel_bbox(placed),
                "clipped_nonzero_RGBA_pixels":0,"inverse_full_RGBA_equal":bool(np.array_equal(array,inverse)),
                "source_RGBA_sha256":hashlib.sha256(array.tobytes()).hexdigest(),"inverse_RGBA_sha256":hashlib.sha256(inverse.tobytes()).hexdigest(),
                "rescaled_rotated_recolored_drawn":False,"intersections":intersections,"fit_accepted":False}
            registrations.append(registration)
            runtime=RUNTIME_NAMES[name];asset=f"T_Fairytale_LeatherPrimary1{runtime}_{frame:03d}_v001"
            package='/Game/Production/ArtTrials/EV048/v013/HeroLeatherPrimary1/'+asset
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
    if mismatches:raise RuntimeError(f"Read-only source changed: {mismatches}")
    report=write("assembly-proof-v002.json",{"schema":"primary1-soft-leather-integer-curated-export-assembly-v002",
        "created_local":datetime.datetime.now().astimezone().isoformat(),"script":pin(Path(__file__).resolve()),"mounts":pin(mounts_path),
        "mounts_freeze":pin(mount_freeze_path),"source_index":pin(index_path),"native_source_naming_contract":pin(native_source),
        "frames":frames,"registrations":registrations,"armor_count":18,"body_byte_copies":24,"static_right_count":6,"static_left_count":6,
        "durations_ms":DURATIONS,"static_layer_order_no_sword":STATIC_ORDER,
        "future_Sword_slot":{"after":"HelmetForeground","before":"NearHand","included":False},
        "all_integer_translations_reversible_RGBA":True,"clipped_nonzero_RGBA_pixels":0,"all_body_original_bytes_unchanged":True,
        "explicit_curation_standard_export_count":18,"pre_curation_to_curated_RGBA_exact":True,"source_mismatches":mismatches,
        "read_only_source_count":len(WATCHED),"toolchain":{"python":sys.executable,"Pillow":PIL.__version__,"numpy":np.__version__},
        "new_outputs_viewed":False,"fit_accepted":False,"semantic_protection_accepted":False,"imported":False,"full_animation_or_unit_accepted":False,
        "limitations":["Actual visible A is verified against pinned RGBA. B is Root artist proposal against actual runtime v003, not a measured bone or accepted fit.",
        "Integer reversibility and exact old four-layer ownership prove pixel fidelity only; mask is not semantic protection. Helmet, eyes, neck, both hands, belt/waist require actual review.",
        "Static images omit Sword, mirrored diagnostic is the whole composite once. This does not prove runtime/motion continuity or all equipment/action compatibility.",
        "Previous standard-inspect low-motion warnings remain in extraction reports. Chest192 frame2 RGBA[0,255,0,1] at(223,248) is preserved, not silently erased.",
        "Pre-curation frames are not installed: selected 0..5, stamped curation, standard identity exports then exact integer placement. Export selection is for fit trial only."]})
    manifest=write("candidate-import-draft-without-freeze-v013-v002.json",{"schema":"leather-primary1-curated-integer18-import-candidate-v001","namespace":"/Game/Production/ArtTrials/EV048/v013/HeroLeatherPrimary1",
        "assets":assets,"asset_count":18,"body_assets_reused_unchanged":24,"canvas_px":[512,512],"native_facing":1,"display_root":[256,464],
        "preview_canvas_size":72*512/416,"durations_ms":DURATIONS,"source_native_requests":[192,189,190],"assembly_proof":pin(report),
        "fit_accepted":False,"import_permitted":False,"Root_static_review_required":True,"runtime_import_called":False,"formal_complete_units":0})
    write("HANDOFF.md","""# Primary1软皮六相整数试装候选

18组件经过显式全六帧选择、stamp_curation及标准export_curated_pngs，导出RGBA与提取源相等，再按Root新挂点作整数平移。24个既有v003身体四层逐字节复制；无裁切/重画/缩放/改色。六个右向无剑静态组合和六个整体镜像只供贴合审阅。Sword槽在HelmetForeground之后、NearHand之前，当前未接。

`assembly-proof-v002.json`保存原始提取→明确选择→curated导出→整数位移来源，实际A像素与artistB/误差、可逆RGBA与数值交集。ownership不是语义保护mask；头盔、眼、颈、双手、腰带仍待Root实际审图。Chest192一处alpha1绿像素保留，低motion警告未消失。

`candidate-import-v013-v002.json`仅拟18新Texture，名字对齐native-source-v002；fit/import均false，先E保全再Root审图。执行者未查看新图，无Source/UE/ledger/进度/媒体改动。v001旧B因参照错误body而拒绝，不能再用。
""")
    files=[pin(q,False) for q in sorted(OUT.rglob('*')) if q.is_file()]
    for row in files:row['path']=Path(row['path']).relative_to(OUT).as_posix()
    freeze=write("assembly-freeze-v002.json",{"schema":"primary1-integer-assembly-freeze-v002","files":files,"file_count_excluding_manifest":len(files),
        "total_bytes_excluding_manifest":sum(x['bytes'] for x in files),"fit_accepted":False,"new_outputs_viewed":False,"imported":False})
    final_assets=[]
    for asset in assets:
        source=asset["source"]
        final_assets.append({k:v for k,v in asset.items() if k not in {"source","registration"}} | {
            "source":source["path"],"source_bytes":source["bytes"],"source_sha256":source["sha256"],
            "registered_source":source,"registration_proof":pin(report)})
    final=json.loads(manifest.read_text("utf-8-sig"))
    final["assets"]=final_assets
    final["references"]={"assembly_freeze":pin(freeze),"assembly_proof":pin(report),"corrected_mounts":pin(mounts_path),
        "corrected_mounts_freeze":pin(mount_freeze_path),"pre_curation_selection_index":pin(index_path),"native_source_v002":pin(native_source)}
    final["assembly_freeze"]=pin(freeze)
    final["assembly_freeze_excludes_final_import_manifest_to_avoid_hash_cycle"]=True
    manifest=write("candidate-import-v013-v002.json",final)
    delivery_files=[pin(q,False) for q in sorted(OUT.rglob('*')) if q.is_file()]
    for entry in delivery_files:entry["path"]=Path(entry["path"]).relative_to(OUT).as_posix()
    delivery_freeze=write("delivery-freeze-v002.json",{"schema":"primary1-integer-assembly-delivery-freeze-v002", "files":delivery_files,
        "assembly_freeze":pin(freeze),"candidate_import":pin(manifest),"fit_accepted":False,"new_outputs_viewed":False})
    print(json.dumps({"report":pin(report),"candidate_import":pin(manifest),"freeze":pin(freeze),"delivery_freeze":pin(delivery_freeze),"armor_count":18,"body_byte_copies":24,
        "right_static":6,"left_static":6,"read_only_sources":len(WATCHED),"mismatches":[],"new_outputs_viewed":False},indent=2))


if __name__=="__main__":main()
