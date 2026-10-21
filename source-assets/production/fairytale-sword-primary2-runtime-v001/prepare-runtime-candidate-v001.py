"""Prepare six native169 exact-pixel import/data candidates. Never imports Unreal.
Writes only this fresh family; existing artwork, C++ and frozen input remain readonly.
"""
from pathlib import Path
from datetime import datetime
import hashlib
import importlib.util
import json
import math
import shutil
import sys

sys.dont_write_bytecode = True
sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path("F:/Ourgame")
HERE = Path(__file__).resolve().parent
FAMILY = ROOT / "source-assets/production/fairytale-sword-primary2-v001"
MEASUREMENT = FAMILY / "primary2-measurement-v001/measurement-v001.json"
DESIGN = FAMILY / "primary2-design-contract-v002.json"
NAMESPACE = "/Game/Production/ArtTrials/EV048/v008/HeroSwordPrimary2"
DISK = ROOT / "UnrealGame/Content/Production/ArtTrials/EV048/v008/HeroSwordPrimary2"
DECODER = ROOT / "tools/scripts/ue-import-armor-primary2-four-v001.py"
DECODER_SHA = "5c667edbeb81eac54648d14ff92b8883d1b15a39a05cc3b56c17933dd29eb49a"


def require(condition, why):
    if not condition:
        raise RuntimeError(why)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fact(path):
    return {"path": path.as_posix(), "bytes": path.stat().st_size, "sha256": sha(path)}


def load(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_json(path, value):
    require(not path.exists(), f"Refuse overwrite {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def verify_freeze(path):
    document = load(path)
    for row in document["files"]:
        actual = fact(Path(row["path"]))
        require(actual["bytes"] == row["bytes"] and actual["sha256"] == row["sha256"], f"Frozen reference changed {row['path']}")
    return {"manifest": fact(path), "files_checked": len(document["files"]), "mismatches": 0}


def production_inventory():
    files = []
    for p in sorted((ROOT/"UnrealGame/Content/Production").rglob("*")):
        if p.is_file():
            row = fact(p)
            row["path"] = p.relative_to(ROOT).as_posix()
            files.append(row)
    require(len([r for r in files if r["path"].endswith(".uasset")]) == 983, "Current983 baseline changed; ask Root before preparing")
    return {"schema": "readonly-production983-before-primary2-import-v1", "created_local": datetime.now().astimezone().isoformat(),
            "file_count": len(files), "uasset_count": 983, "total_bytes": sum(r["bytes"] for r in files), "files": files,
            "scope": "Actual disk inventory only; not an Unreal registry query or an import receipt"}


def fvector(point):
    return f"FVector2D({float(point[0])!r}, {float(point[1])!r})"


def main():
    require(not (HERE/"manifests").exists() and not (HERE/"curated").exists(), "Candidate family already prepared; use new version")
    require(sha(DECODER) == DECODER_SHA, "Pinned native CRC/RGBA decoder changed")
    require(not DISK.exists() or not any(DISK.rglob("*")), "Unused candidate disk namespace required; no replacements")
    freeze_paths = [FAMILY/"preparation-freeze-v001.json", FAMILY/"preparation-freeze-v002.json",
                    FAMILY/"primary2-extraction-v001/extracted-freeze-v001.json",
                    FAMILY/"primary2-extraction-v002/extracted-freeze-v002.json",
                    FAMILY/"primary2-measurement-v001/measurement-freeze-v001.json"]
    before = [verify_freeze(p) for p in freeze_paths]
    require(sha(MEASUREMENT) == "08fedc585b5a839775b71f2ae394393b342c168f3d1b070da6400acc9fb75972", "Measurement pin changed")
    require(sha(DESIGN) == "cfddab3009c1b9054a6aa1610a26495bb071346b8bd8529f33cd935c75d71a88", "Input design pin changed")
    measurement, design = load(MEASUREMENT), load(DESIGN)
    require(len(measurement["frames"]) == len(design["poses"]) == 6, "Exactly six actual source phases required")
    require(design["timing"]["durations_ms"] == [75,75,60,60,135,135], "KernelStage1 durations changed")
    spec = importlib.util.spec_from_file_location("readonly_primary2_native_rgba_decoder", DECODER)
    decoder = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(decoder)
    inventory = production_inventory()
    baseline_path = HERE/"manifests/old-production983-before-import.json"
    write_json(baseline_path, inventory)
    (HERE/"curated").mkdir()
    assets, markers, pixel_checks = [], [], []
    for index, (measured, pose) in enumerate(zip(measurement["frames"], design["poses"])):
        require(measured["frame"] == pose["frame"] == index, "Source phases must remain ordered")
        source = Path(measured["source"]["path"])
        require(source.resolve() == (FAMILY/"run-primary2-v002/curated"/f"frame-{index}.png").resolve(), "Unexpected source family")
        require(fact(source) == measured["source"], "Actual curated source changed")
        copy = HERE/"curated"/f"frame-{index}.png"
        shutil.copyfile(source,copy)
        require(source.read_bytes() == copy.read_bytes(), "Runtime input must be an exact byte copy")
        pixels = decoder.inspect_rgba_png(copy.read_bytes())
        require(pixels["canvas_px"] == [512,512] and pixels["mode"] == "RGBA" and pixels["alpha_extrema"] == [0,255]
                and pixels["nonempty"] and pixels["corners_transparent"], "Actual512RGBA/native alpha checks failed")
        bbox = pixels["bbox_px"]
        require(bbox[3]-bbox[1] <= 416, "Source visible height exceeds fixed416")
        name = f"T_Fairytale_SwordPrimary2_{index:03d}_v001"
        assets.append({"clip": "Primary2", "frame": index, "source": copy.as_posix(),
                       "source_bytes": copy.stat().st_size, "source_sha256": sha(copy), "source_bbox": bbox,
                       "canonical_curated": fact(source), "name": name, "package_path": NAMESPACE+"/"+name,
                       "object_path": NAMESPACE+"/"+name+"."+name})
        require(measured["grip_candidate"]["type"].startswith("MANUAL visible"), "Grip cannot be replaced by guide/bbox")
        axis = pose["invisible_blade_axis_design_xy"]
        require(math.hypot(*axis) > 0 and all(math.isfinite(x) for x in axis), "Invalid design axis")
        markers.append({"frame": index, "source": fact(source), "display_root_px": [256,464],
                        "grip_candidate_px": measured["grip_candidate"]["xy"],
                        "grip_uncertainty_plus_minus_px": measured["grip_candidate"]["uncertainty_plus_minus_px"],
                        "grip_actual_rgba_samples": measured["grip_candidate"]["source_rgba_samples"],
                        "near_hand_polygon_candidate_px": measured["near_hand_polygon_candidate"]["vertices_xy"],
                        "polygon_uncertainty_plus_minus_px": measured["near_hand_polygon_candidate"]["uncertainty_plus_minus_px"],
                        "polygon_complete_ownership_mask": False, "actual_thumb_contour": None, "actual_blade_axis": None,
                        "actual_grasp_cylinder": None, "axis_design_only": axis,
                        "axis_origin": "Frozen original input contract poses[].invisible_blade_axis_design_xy; no normalization/sign inference",
                        "not": "Grip is visible palm candidate, not whole-hand bbox or measured physical handle center"})
        pixel_checks.append({"frame": index, "canonical": fact(source), "copy": fact(copy), "byte_equal": True,
                             "native_decoder": pixels, "visible_height_px": bbox[3]-bbox[1]})
    require(len({r["source_sha256"] for r in assets}) == 6, "Six unique source phases required")
    refs = {
        "native169_raw": fact(FAMILY/"run-primary2-v002/raw/sword_primary_2.png"),
        "native169_receipt": fact(FAMILY/"generation-control-v001/generation-receipt169-v001.json"),
        "input_freeze": fact(FAMILY/"preparation-freeze-v002.json"),
        "original_input_design": fact(DESIGN), "extract_freeze": fact(freeze_paths[3]),
        "extract_receipt": fact(FAMILY/"primary2-extraction-v002/extraction-receipt-v002.json"),
        "measurement_freeze": fact(freeze_paths[4]), "measurement": fact(MEASUREMENT)}
    marker_path = HERE/"data/primary2-marker-candidate-v001.json"
    write_json(marker_path, {"schema": "fairytale-primary2-native169-runtime-marker-candidate-v1", "references": refs,
        "clip": "sword_primary_2", "frame_count": 6, "native_facing": 1, "display_pivot_px": [256,464],
        "preview_canvas_size": 72*512/416, "body_display_height": 72, "sword_scale": 0.50, "independent_sword_source_grip_px": [99,256],
        "durations_ms": [75,75,60,60,135,135], "markers": markers,
        "axis_accepted": False, "thumb_accepted": False, "grip_accepted": False, "foot_lock_accepted": False,
        "full_motion_accepted": False, "runtime_verified": False, "formal_complete_units": 0,
        "measurement_p2_axis_proposal_unused": "Measurement contains separate [1,0] fitting proposal; Root selected frozen original input[.98,.20] for this candidate. Neither axis is measured or accepted."})
    inl_path = HERE/"data/DungeonFairytaleSwordPrimary2V001.inl"
    lines = ['#pragma once', '#include "DungeonFairytaleSwordBodyV001.inl"', '',
        '// STATIC DATA CANDIDATE ONLY: retained native169 source; not installed in UnrealGame/Source.',
        '// V001 supplies FMarker TYPE only. No old human/source marker DATA is reused.',
        '// Grip is visible-palm MANUAL candidate (+/-3 or4px), not an actual grasp-cylinder center.',
        '// FistPolygon is an uncertain visible-glove outline (+/-4px), NOT exact ownership/thumb mask.',
        '// Axis is copied from frozen v002 INPUT DESIGN, never measured from this weapon-free body.',
        '// Pivot256,464 / body72 / SwordScale.50 / sword sourceGrip99,256 remain fixed.',
        '// Actual kernelStage1 timing75/75/60/60/135/135ms; standard100x6 preview FAILED timing.',
        f'// MarkerJSON SHA256: {sha(marker_path)}',
        f'// Measurement SHA256: {sha(MEASUREMENT)}',
        'namespace DungeonFairytaleSwordPrimary2V001', '{',
        'using FMarker = DungeonFairytaleSwordBodyV001::FMarker;',
        'inline constexpr double CanvasSize = 72. * 512. / 416.;',
        'inline constexpr double SwordScale = 0.50;',
        'inline FVector2D IndependentSwordGrip() { return FVector2D(99., 256.); }',
        'inline int32 Count(const FString& Clip) { return Clip == TEXT("sword_primary_2") ? 6 : 0; }',
        'inline const FMarker* Find(const FString& Clip, int32 Index)', '{',
        '    if (Clip != TEXT("sword_primary_2") || Index < 0 || Index >= 6) return nullptr;',
        '    static const FMarker Markers[] =', '    {']
    for marker in markers:
        poly = ', '.join(fvector(p) for p in marker['near_hand_polygon_candidate_px'])
        lines += [f"        // Frame{marker['frame']} SourceSHA256: {marker['source']['sha256']}; Grip +/-{marker['grip_uncertainty_plus_minus_px']}px; polygon +/-4px.",
                  f"        FMarker{{{fvector(marker['display_root_px'])}, {fvector(marker['grip_candidate_px'])}, {fvector(marker['axis_design_only'])}, TArray<FVector2D>{{{poly}}}}},"]
    lines += ['    };', '    return &Markers[Index];', '}', '} // namespace DungeonFairytaleSwordPrimary2V001', '']
    inl_path.write_text('\n'.join(lines),encoding='utf-8')
    manifest_path = HERE/"manifests/import-sword-primary2-v001.json"
    manifest = {"schema": "frozen-fairytale-sword-primary2-six-v1", "frozen": True, "ready_for_root_import": True,
        "namespace": NAMESPACE, "asset_count": 6, "clip": "sword_primary_2", "source_native": 169,
        "canvas_px": [512,512], "display_pivot_px": [256,464], "preview_canvas_size": 72*512/416,
        "body_display_height": 72, "visible_body_height_upper_bound_px": 416,
        "native_facing": 1, "per_frame_resize": False, "pixel_transform": "none; exact byte copies",
        "mirror_policy": "Runtime mirror entire actor once for -X; source files remain native+1",
        "durations_ms": {"Primary2": [75,75,60,60,135,135]},
        "durations_origin": "Existing SWD001 kernel stage1 GetPrimaryPoseFrame, not a new preview clock or input override",
        "standard_preview_durations_ms": [100,100,100,100,100,100], "standard_preview_timing_passed": False,
        "sword_scale": 0.50, "independent_sword_source_grip_px": [99,256],
        "references": refs, "marker_json": fact(marker_path), "marker_inl_candidate": fact(inl_path),
        "old_production_disk_inventory": fact(baseline_path), "assets": assets,
        "recommended_texture_settings": {"compression_settings": "TC_EDITOR_ICON", "mip_gen_settings": "TMGS_NO_MIPMAPS", "lod_group": "TEXTUREGROUP_UI", "never_stream": True, "srgb": True},
        "source_import_checks_required": ["Pinned manifest/source/reference bytes and SHA", "Native PNG CRC/512RGBA/alpha/bbox6unique/max416", "Unused disk namespace and actual UE registry namespace", "replace_existing=False", "Actual imported_object_paths exactset6", "Texture2D actual512/settings readback", "Save6 and reread package bytes/SHA", "Registry+disk exactset6 and original983packages unchanged"],
        "runtime_verified": False, "imported": False, "armor_present": False, "full_motion_accepted": False,
        "thumb_accepted": False, "grip_accepted": False, "foot_lock_accepted": False, "formal_complete_units": 0,
        "scope": "Bounded independent-sword fit trial input only; no armor, fullstate/continuousmotion or complete equipment acceptance"}
    write_json(manifest_path,manifest)
    after = [verify_freeze(p) for p in freeze_paths]
    require(before == after, "Frozen source changed during preparation")
    require(inventory["files"] == production_inventory()["files"], "Original983 disk packages changed during readonly preparation")
    write_json(HERE/"source-preflight-v001.json", {"schema": "fairytale-primary2-runtime-readonly-preflight-v1", "created_local": datetime.now().astimezone().isoformat(),
        "manifest": fact(manifest_path), "native_decoder": fact(DECODER), "native_crc_and_rgba_checks": pixel_checks,
        "source_unique_count": 6, "maximum_visible_height_px": max(r["visible_height_px"] for r in pixel_checks),
        "old_source_freezes": after, "old_source_files_checked_each_pass": 136,
        "measurement_files_checked_each_pass": len(load(freeze_paths[4])["files"]),
        "original983packages_before_after_unchanged": True, "candidate_disk_namespace_unused": True,
        "actual_UE_registry_unused": None, "UE_registry_check_required_by_root_before_import": True,
        "candidate_inl_compiled": False, "unreal_called": False, "imported": False, "runtime_verified": False,
        "source_pixels_modified": False, "axis_design_only": True})
    (HERE/"README.md").write_text("""# Native169第二段：Root导入/独立剑拟合候选

六张curated是原169标准512RGBA的逐字节副本；未重画、缩放、移脚、镜像或warp。真实PNG CRC/alpha/六帧唯一/最高416及来源SHA均已只读预检。只检查了新namespace磁盘未占用，**UE registry仍须Root实际核对**；没有导入、运行、编译或验收。

导入入口数据为`manifests/import-sword-primary2-v001.json`，沿现有body-v002的assets格式：source/source_bytes/source_sha256/source_bbox/name/package_path/object_path。Root新checks应固定schema、namespace、六项顺序和manifest SHA，复用原nativePNG decoder，保留旧983包、registry/disk exactset、save/readback和Texture设置门；不得调用原ten-v2 importer硬套六项。导入工具可接受`--manifest <绝对manifest路径> --expected-manifest-sha256 <本次SHA> --require-unused --validate-only`方案，实际入口由Root另写；这些参数不是已存在的CLI。

`data/DungeonFairytaleSwordPrimary2V001.inl`只是静态候选，尚未写入Source。仅借V001的FMarker类型，不借旧人类/旧姿势坐标；Find仅支持sword_primary_2六相。Root/pivot256464、Canvas72*512/416、SwordScale.50、剑源Grip99256不变。近掌六候选224318/252274/358277/345277/250301/224318来自实测可见手套，±3–4px；手轮廓±4px不是完整ownership或thumb mask。六刃轴来自原v002输入设计，p2明确[.98,.20]，不采用measurement另提[1,0]；实际刃轴/握柄/拇指仍null、未接受。

75/75/60/60/135/135ms来自现有SWD001 Stage1内核；原standard atlas/GIF仍100×6ms，timing QA没有通过，也没有改图或retime。未来须用真实J连击触发第二段及GetPrimaryPoseFrame，不改变内核/输入/clock；当前只为独立剑拟合，不适配Ready或Primary1甲、不宣称连续运动、足锁、音效或完整内容。
""", encoding="utf-8")
    files = [fact(p) for p in sorted(HERE.rglob("*")) if p.is_file()]
    freeze_path = HERE/"ready-for-root-import-freeze-v001.json"
    write_json(freeze_path, {"schema": "fairytale-primary2-runtime-candidate-freeze-v1", "created_local": datetime.now().astimezone().isoformat(),
        "file_count": len(files), "total_bytes": sum(r["bytes"] for r in files), "files": files,
        "status": "ready-for-Root-import candidate, not imported", "unreal_called": False, "armor_present": False,
        "full_motion_accepted": False, "source_136_and_measurement_22_unchanged": True})
    print(json.dumps({"freeze": fact(freeze_path), "manifest": fact(manifest_path), "marker_inl": fact(inl_path),
        "files_excluding_freeze": len(files), "bytes_excluding_freeze": sum(r["bytes"] for r in files),
        "actual_curated_count": len(assets), "old_packages_unchanged": 983, "source_unique_count": 6,
        "maximum_visible_height": max(r["visible_height_px"] for r in pixel_checks), "imported": False},ensure_ascii=False,indent=2))


if __name__ == "__main__":
    main()
