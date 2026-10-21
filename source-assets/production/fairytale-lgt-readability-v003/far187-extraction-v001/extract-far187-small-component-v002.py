"""Far187 deterministic extraction diagnostics; candidate only, never art acceptance."""
from __future__ import annotations

import datetime
import hashlib
import json
import platform
import shutil
import subprocess
import sys
from pathlib import Path

import PIL
import numpy as np
from PIL import Image


OUT = Path(__file__).resolve().parent
PROJECT = Path("F:/Ourgame")
FAMILY = PROJECT / "source-assets/production/fairytale-lgt-readability-v003"
SOURCE_RUN = FAMILY / "row-correction-v004/run-far-tiny-tab-ready-v004"
SG = Path("C:/Users/22499/.codex/skills/sprite-gen")
PYTHON = SG / ".venv/Scripts/python.exe"
STATE = "leather_farshoulder_sword_ready"
RAW_SHA = "e536b124651e695e904d6636202cc025145f4acadbae9702656f3d4744be777c"
EXTRACT_IMPL_SHA = "f2a7902f01069668340d14217bd05c777f5c01853284102e211aba1013a45539"
SHARED_WRAPPER_SHA = "ebe0e28a55db0378db89e8ba4c207b1e4a896aec80555ff3cc5558c9e87ede1e"
WATCHED = {}


def pin(path: Path, watch: bool = True) -> dict:
    data = path.read_bytes()
    value = {"path": path.as_posix(), "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}
    if watch and not path.is_relative_to(OUT):
        WATCHED[path] = value
    return value


def write(relative: str, data: dict | str) -> Path:
    path = OUT / relative
    if not path.is_relative_to(OUT):
        raise RuntimeError("Ownership boundary")
    path.parent.mkdir(parents=True, exist_ok=True)
    text = data if isinstance(data, str) else json.dumps(data, ensure_ascii=False, indent=2) + "\n"
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(text)
    return path


def copy_source(source: Path, target: Path) -> dict:
    original = pin(source)
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        raise RuntimeError(f"Existing output: {target}")
    shutil.copy2(source, target)
    copied = pin(target)
    if copied["sha256"] != original["sha256"] or copied["bytes"] != original["bytes"]:
        raise RuntimeError("Copy mismatch")
    return {"source": original, "copy": copied, "byte_identical": True}


def run_tool(name: str, argv: list[str]) -> dict:
    result = subprocess.run(argv, capture_output=True, text=True, encoding="utf-8")
    log = write(f"logs/{name}.log", result.stdout + result.stderr)
    record = {"argv": argv, "exit_code": result.returncode, "log": pin(log)}
    path = write(f"logs/{name}-command.json", record)
    record["record"] = pin(path)
    return record


def frame_metrics(path: Path) -> dict:
    with Image.open(path) as image:
        if image.mode != "RGBA" or image.size != (512, 512):
            raise RuntimeError(f"Expected 512 RGBA: {path}")
        array = np.asarray(image)
        alpha = array[:, :, 3]
        solid = alpha >= 128
        colors = array[:, :, :3][solid]
        core_bbox = image.getchannel("A").point(lambda value: 255 if value >= 128 else 0).getbbox()
        any_bbox = image.getchannel("A").getbbox()
        return {
            "file": pin(path), "mode": image.mode, "size": list(image.size),
            "alpha_nonzero_bbox_ltrb_exclusive": list(any_bbox) if any_bbox else None,
            "alpha_core128_bbox_ltrb_exclusive": list(core_bbox) if core_bbox else None,
            "nonzero_alpha_pixels": int(np.count_nonzero(alpha)),
            "solid128_alpha_pixels": int(np.count_nonzero(solid)),
            "partial_alpha_pixels": int(np.count_nonzero((alpha > 0) & (alpha < 255))),
            "distinct_core_rgb_colors": int(len(np.unique(colors, axis=0))),
            "exact_green_nonzero_alpha_pixels": int(np.count_nonzero((alpha > 0) & (array[:, :, 0] == 0) & (array[:, :, 1] == 255) & (array[:, :, 2] == 0))),
            "semantic_mask_accepted": False, "attachment_A": None,
        }



def build_source_inventory():
    old_family = PROJECT / "source-assets/production/fairytale-armor-sword-ready-v002"
    partition = old_family / "body-partition-v002"
    registered = old_family / "macro-registration-proposed-v001"
    body_run = PROJECT / "source-assets/production/fairytale-sword-v001/run-ready-v002"
    measure_path = old_family / "measurement-candidate-v002.json"
    partition_proof = partition / "proof-v001.json"
    old_contract = registered / "macro-measurement-registration-v001.json"
    measurement = json.loads(measure_path.read_text(encoding="utf-8"))
    old = json.loads(old_contract.read_text(encoding="utf-8"))
    entries = []
    for frame in range(4):
        source = body_run / f"curated/frame-{frame}.png"
        actual_body = pin(source)
        expected = measurement["frames"][frame]["source"]
        if actual_body != expected:
            raise RuntimeError("Common body source pin changed")
        bodies = []
        for owner in ["BodyRest", "NearArmWithoutHand", "NearHand"]:
            current = registered / f"textures/{owner}/frame-{frame}.png"
            original = partition / f"layers/{owner}/frame-{frame}.png"
            mask = partition / f"masks/{owner}/frame-{frame}.png"
            if current.read_bytes() != original.read_bytes():
                raise RuntimeError("Existing body texture no longer matches partition bytes")
            with Image.open(mask) as image:
                pixels = np.asarray(image)
                if image.mode != "L" or image.size != (512, 512) or not set(np.unique(pixels)).issubset({0, 255}):
                    raise RuntimeError("Existing binary ownership mask changed")
            bodies.append({"owner": owner, "current_texture": pin(current), "partition_layer": pin(original),
                           "ownership_mask": pin(mask), "texture_matches_partition_byte_exact": True,
                           "mask_role": "Source-coordinate binary ownership, not an accepted armor coverage/protection semantic mask"})
        armor = []
        for component, native, folder, state in [
            ("Chest", 184, FAMILY / "chest184-extraction-v001", "leather_chest_sword_ready"),
            ("NearShoulder", 186, FAMILY / "near186-extraction-v001", "leather_nearshoulder_sword_ready"),
            ("FarShoulder", 187, OUT, STATE),
        ]:
            run = folder / ("run-shared-smallcomponent-v002" if native == 187 else "run-shared-diagnostic-v001")
            source = run / f"frames/{state}/frame-{frame}.png"
            with Image.open(source) as image:
                if image.mode != "RGBA" or image.size != (512, 512):
                    raise RuntimeError("Candidate component expected 512 RGBA")
                bbox = image.getchannel("A").getbbox()
            armor.append({"component": component, "native_request": native, "diagnostic_png": pin(source),
                          "alpha_bbox_diagnostic_only": list(bbox), "candidate_request": pin(run / "sprite-request.json"),
                          "candidate_frames_manifest": pin(run / "frames/frames-manifest.json"),
                          "duration_ms": 167, "component_A_source_px": None, "body_target_B_source_px": None,
                          "integer_translation_delta_xy": None, "semantic_mask_accepted": False,
                          "registered_or_imported": False})
        entries.append({"frame": frame, "duration_ms": 167, "common_body158": actual_body,
                        "existing_body_layers_to_keep_unchanged": bodies, "armor_candidates_for_root_measurement": armor})
    mismatches = [path.as_posix() for path, prior in WATCHED.items() if pin(path, False) != prior]
    if mismatches:
        raise RuntimeError(f"Read-only inventory source changed: {mismatches}")
    return write("ready-three-component-source-list-v001.json", {
        "schema": "ready-three-leather-components-await-actual-A-B-source-list-v001",
        "created_local": datetime.datetime.now().astimezone().isoformat(),
        "status": "SOURCE_INDEX_ONLY_A_B_AND_INTEGER_FIT_PENDING_ROOT", "frames": entries,
        "frame_count": 4, "durations_ms": [167] * 4, "native_facing": 1,
        "maximum_hero_height_screen_px": 72, "whole_parent_mirror_once": True,
        "legacy_contract_sources": {"body_measurement_candidates": pin(measure_path), "ownership_proof": pin(partition_proof),
                                    "static_registration_contract": pin(old_contract)},
        "legacy_layer_order_reference": old["future_runtime_layer_order"],
        "future_Sword_handling": "Independent actual Root grip/sword, between NearShoulder and NearHand. No new Sword transform specified here.",
        "all_new_component_A_body_B_and_delta_null": True,
        "old_design_body_sites_reused_as_new_B": False, "old_metal_clasp_or_rivet_reused_as_new_A": False,
        "new_body_pixels_or_masks_written": False, "new_composite_or_integer_fit_images_written": False,
        "producer_viewed_new_outputs": False, "source_mismatches": mismatches,
        "limits": ["A must refer to an actually observed feature of the new component, not a bbox center.",
                   "B must be supplied/accepted by Root for this matching Body158 frame; old visible-cloth sites are uncertain design candidates, not new equipment fit proof.",
                   "Old source ownership masks do not certify forbidden armor coverage over helmet, eyes, neck, far hand, waist or hidden joints.",
                   "No registration/compositing occurs until Root provides the new measured A/B; integer translation only must preserve all source RGBA/AA without clipping."],
    })

def main() -> None:
    if Path(sys.executable).resolve() != PYTHON.resolve():
        raise RuntimeError(f"Use sprite-gen venv: {PYTHON}")
    if OUT != FAMILY / "far187-extraction-v001" or (OUT / "run-standard-smallcomponent-v002").exists() or (OUT / "run-shared-smallcomponent-v002").exists():
        raise RuntimeError("Unexpected or existing output")
    raw = SOURCE_RUN / f"raw/{STATE}.png"
    request_path = SOURCE_RUN / "sprite-request.json"
    q = json.loads(request_path.read_text(encoding="utf-8-sig"))
    if pin(raw)["sha256"] != RAW_SHA:
        raise RuntimeError("Actual187 raw changed")
    if q["fit"].get("pixel_unfake") is not False or q["fit"].get("shared_row_scale") is not True:
        raise RuntimeError("Explicit HD/shared-row fit required")
    if q["states"][STATE]["durations_ms"] != [167] * 4 or q["states"][STATE]["frames"] != 4:
        raise RuntimeError("Actual request timing changed")
    if [q["cell"]["width"] - 2 * q["cell"]["safe_margin_x"], q["cell"]["height"] - 2 * q["cell"]["safe_margin_y"]] != [30, 28]:
        raise RuntimeError("Actual fit-window changed")
    extract = SG / "scripts/extract_sprite_row_frames.py"
    inspect = SG / "scripts/inspect_sprite_run.py"
    extract_impl = SG / "sprite_gen/frames/extract.py"
    shared = OUT / "shared-row-fit-explicit-min-v001.py"
    if pin(extract_impl)["sha256"] != EXTRACT_IMPL_SHA or pin(shared)["sha256"] != SHARED_WRAPPER_SHA:
        raise RuntimeError("Pinned extractor or project shared hook changed")
    write("toolchain-v002.json", {
        "python_executable": sys.executable, "python_version": platform.python_version(),
        "pillow_version": PIL.__version__, "numpy_version": np.__version__,
        "tools": [pin(path) for path in [extract, inspect, extract_impl, SG / "sprite_gen/qa/inspect.py", shared]],
        "installed_tools_modified": False,
        "standard_extract_limitation": "The installed extract_component_frames calls fit_to_cell once per component and does not consume shared_row_scale. Preserve that baseline separately. The existing project wrapper replaces only its fit hook and calls the same installed extractor main with original segmentation, chroma and QA.",
    })
    origins = []
    for relative in [f"raw/{STATE}.png", "sprite-request.json", "base-source.png", f"prompts/{STATE}.txt"]:
        origins.append(copy_source(SOURCE_RUN / relative, OUT / "original-input-v002" / relative))
    write("source-input-pins-v002.json", {"actual_native_request": 187, "copies": origins,
          "root_reported_visual_status": "Four narrow curved image-RIGHT far tabs preserved; broad near covers and long rings removed, reported by Root after E274 review. Semantic mask/fit/A still unaccepted.",
          "root_reported_retention": "E274", "producer_viewed_raw_or_outputs": False})
    results = []
    for mode in ["standard-smallcomponent", "shared-smallcomponent"]:
        run = OUT / f"run-{mode}-v002"
        inputs = []
        for relative in [f"raw/{STATE}.png", "sprite-request.json", "base-source.png", f"prompts/{STATE}.txt"]:
            inputs.append(copy_source(SOURCE_RUN / relative, run / relative))
        before = pin(run / "sprite-request.json")
        command = [str(PYTHON), "-B", "-X", "utf8", str(extract if mode == "standard-smallcomponent" else shared), "--run-dir", str(run), "--min-used-pixels", "256"]
        extraction = run_tool(f"extract-{mode}-v002", command)
        after = pin(run / "sprite-request.json")
        inspect_command = [str(PYTHON), "-B", "-X", "utf8", str(inspect), "--run-dir", str(run), "--states", STATE,
                           "--report", str(run / "inspect-report.json")]
        inspection = run_tool(f"inspect-{mode}-v002", inspect_command)
        frames = sorted((run / f"frames/{STATE}").glob("frame-*.png"))
        manifest_path = run / "frames/frames-manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8-sig")) if manifest_path.exists() else None
        inspect_path = run / "inspect-report.json"
        inspect_report = json.loads(inspect_path.read_text(encoding="utf-8-sig")) if inspect_path.exists() else None
        result = {
            "mode": mode, "run_dir": run.as_posix(), "input_copies": inputs,
            "request_before": before, "request_after": after,
            "working_request_byte_unchanged_after_extraction": before["sha256"] == after["sha256"],
            "extraction": extraction, "inspection": inspection,
            "frame_count": len(frames), "frame_metrics": [frame_metrics(frame) for frame in frames],
            "frames_manifest": pin(manifest_path) if manifest_path.exists() else None,
            "frames_manifest_ok": manifest.get("ok") if manifest else None,
            "frames_manifest_errors": manifest.get("errors") if manifest else None,
            "frames_manifest_warnings": manifest.get("warnings") if manifest else None,
            "shared_row_fit": manifest["rows"][0].get("shared_row_fit") if manifest and manifest.get("rows") else None,
            "inspect_report": pin(inspect_path) if inspect_path.exists() else None,
            "inspect_ok": inspect_report.get("ok") if inspect_report else None,
            "inspect_errors": inspect_report.get("errors") if inspect_report else None,
            "inspect_warnings": inspect_report.get("warnings") if inspect_report else None,
            "explicit_component_min_used_pixels": 256,
            "minimum_override_scope": "Only this Far187 30x28 narrow rigid component, authorized by Root; original character512 default failed and is retained.",
            "no_palette_quantization": not (run / "palette.lock.json").exists() and q["fit"]["pixel_unfake"] is False,
            "semantic_acceptance": False, "engine_imported": False, "future_component_A": [None] * 4,
        }
        results.append(result)
    mismatches = [path.as_posix() for path, old in WATCHED.items() if pin(path, False) != old]
    similarity_correction = write("inspect-similarity-fact-correction-v001.json", {"created_local": datetime.datetime.now().astimezone().isoformat(), "correct_fact": "Installed standard inspect compares extracted frames to one another, not to base-source.png.", "code_reference": "sprite_gen/qa/inspect.py:_similarity_summary(frames)", "old_frozen_reports_not_overwritten": True, "measured_QA_or_exit_codes_changed": False})
    report = write("numeric-diagnostic-v002.json", {
        "schema": "far187-numeric-extraction-diagnostic-v001", "actual_native_request": 187,
        "created_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(), "created_local": datetime.datetime.now().astimezone().isoformat(),
        "runs": results, "read_only_sources_rechecked": len(WATCHED), "source_mismatches": mismatches,
        "display_and_timing_contract": {"cell": [512, 512], "shared_fit_window": [30, 28], "durations_ms": [167] * 4},
        "accepted_candidate_for_future_pixel_review": "run-shared-smallcomponent-v002 only; strict 512-floor baseline failures remain preserved. This is a rigid-attachment micro-breathing diagnostic, not full animation acceptance.",
        "semantic_mask_or_lining_material_accepted": False, "actual_fit_or_attachment_A_accepted": False,
        "native_animation_or_common_body_accepted": False, "engine_imported": False,
        "producer_viewed_or_screenshot": False, "generation_called": False,
        "limitations": [
            "This process keys chroma and separates existing components deterministically. It does not certify component material semantics or semantically edit retained foreground pixels.",
            "Correction to earlier diagnostic limitations: standard inspect compares the extracted frames against one another (histogram/dHash/motion); it does not compare to base-source.png. The exact original182 input remains only an editing provenance file, not an accepted component base.",
            "Successful numeric extraction/inspect does not prove the requested component semantics, valid mask, measured A, rig compatibility or animation continuity.",
            "Root must retain this complete candidate under E before viewing any newly extracted frame. No curated/final asset or runtime texture is published here.",
        ],
    })
    if mismatches:
        raise RuntimeError(f"Read-only source changed: {mismatches}")
    brief = []
    for result in results:
        brief.append(f"- {result['mode']}: extract exit {result['extraction']['exit_code']}; inspect exit {result['inspection']['exit_code']}; frames {result['frame_count']}; manifest ok={result['frames_manifest_ok']}; inspect ok={result['inspect_ok']}.")
    write("HANDOFF-v002.md", "# Far187 提取诊断 v001\n\n" + "\n".join(brief) + "\n\n" +
          "标准 extract 的逐帧 fit 基线与既有项目共同 scale hook 结果分开保存；共同版调用同一安装标准 extractor 的 chroma、components、QA 路径，仅替换已锁定的 HD fit hook，没有修改安装工具。所有原始输入按字节保留，没有新 prepare 或输入字段改写。\n\n" +
          "供 Root 未来逐像素检查的是 `run-shared-smallcomponent-v002/frames/`。原生187现在保留窄弯右缘tab，组件边缘仍需 Root 实际像素检查，仅此窄刚性附件显式256稀疏面积配置；默认512失败保留。低motion警告保留，组件语义、mask、实际fit、A及完整动画均未验收；全部 A=null。没有生成、导入、UE、ledger、人工裁切/绘制，也未浏览/截图新输出。Root 必须先 E 归档再查看。\n\n" +
          "详见 `numeric-diagnostic-v001.json` 的真实命令、退出码、共同 scale 与每帧尺寸 / alpha / 颜色数；不得把自动 QA 等同于最终装备通过。\n")
    inventory = build_source_inventory()
    write("ready-three-component-source-handoff-v001.md", "# Ready 四帧三组件 Source 清单\n\n详见 `ready-three-component-source-list-v001.json`：Chest184 / Near186 / Far187 各四张共同scale诊断PNG及Body158、既有BodyRest/NearArmWithoutHand/NearHand、原ownership masks，均记录SHA。所有新甲 A / Body target B / integer delta仍null，等待Root实际测量提供，不能用bbox中心或旧灰甲特征自动填值。\n\n旧binary ownership masks只记录源RGBA归属，不是盔甲可覆盖区域/隐藏关节/头盔手指保护语义的验收；旧设计site有不确定性，不能冒充新B。预期层序BodyRest→FarShoulder→Chest→NearArmWithoutHand→NearShoulder→Sword→NearHand，Sword仍由Root独立处理。\n\n没有新合成、整数贴合、mask改写或试装PNG。Root先E保全并查看诊断部件，再以实际A/B决定整数translation；完整保留共同Body158和三旧body层像素。\n")
    files = [pin(path, False) for path in sorted(OUT.rglob("*")) if path.is_file()]
    for value in files:
        value["path"] = Path(value["path"]).relative_to(OUT).as_posix()
    freeze = write("extraction-freeze-v002.json", {
        "schema": "far187-extraction-diagnostic-freeze-v001", "files": files,
        "file_count_excluding_manifest": len(files), "total_bytes_excluding_manifest": sum(value["bytes"] for value in files),
        "semantic_acceptance": False, "viewed": False, "engine_imported": False,
    })
    print(json.dumps({"report": pin(report), "freeze": pin(freeze), "runs": brief,
                      "files_excluding_freeze": len(files), "bytes_excluding_freeze": sum(value["bytes"] for value in files),
                      "source_mismatches": mismatches, "semantic_acceptance": False, "viewed": False}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
