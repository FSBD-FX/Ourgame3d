"""Near183 deterministic extraction diagnostics; candidate only, never art acceptance."""
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
SOURCE_RUN = FAMILY / "row-correction-v002/run-nearshoulder-ready-v002"
SG = Path("C:/Users/22499/.codex/skills/sprite-gen")
PYTHON = SG / ".venv/Scripts/python.exe"
STATE = "leather_nearshoulder_sword_ready"
RAW_SHA = "a3c9a4ea3b5d4be00fc489807c0c61d086081b7d757e219894e3b30c319c9d27"
EXTRACT_IMPL_SHA = "f2a7902f01069668340d14217bd05c777f5c01853284102e211aba1013a45539"
SHARED_WRAPPER_SHA = "2d7464dc2e8dd962a7d4dc170c0a7401d09cf1a626415309b4921b7d89d88aa3"
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


def main() -> None:
    if Path(sys.executable).resolve() != PYTHON.resolve():
        raise RuntimeError(f"Use sprite-gen venv: {PYTHON}")
    if OUT != FAMILY / "near183-extraction-v001" or list(OUT.glob("run-*")):
        raise RuntimeError("Unexpected or existing output")
    raw = SOURCE_RUN / f"raw/{STATE}.png"
    request_path = SOURCE_RUN / "sprite-request.json"
    q = json.loads(request_path.read_text(encoding="utf-8-sig"))
    if pin(raw)["sha256"] != RAW_SHA:
        raise RuntimeError("Actual183 raw changed")
    if q["fit"].get("pixel_unfake") is not False or q["fit"].get("shared_row_scale") is not True:
        raise RuntimeError("Explicit HD/shared-row fit required")
    if q["states"][STATE]["durations_ms"] != [167] * 4 or q["states"][STATE]["frames"] != 4:
        raise RuntimeError("Actual request timing changed")
    if [q["cell"]["width"] - 2 * q["cell"]["safe_margin_x"], q["cell"]["height"] - 2 * q["cell"]["safe_margin_y"]] != [60, 44]:
        raise RuntimeError("Actual fit-window changed")
    extract = SG / "scripts/extract_sprite_row_frames.py"
    inspect = SG / "scripts/inspect_sprite_run.py"
    extract_impl = SG / "sprite_gen/frames/extract.py"
    shared = PROJECT / "tools/scripts/extract-sprite-shared-row-scale.py"
    if pin(extract_impl)["sha256"] != EXTRACT_IMPL_SHA or pin(shared)["sha256"] != SHARED_WRAPPER_SHA:
        raise RuntimeError("Pinned extractor or project shared hook changed")
    write("toolchain-v001.json", {
        "python_executable": sys.executable, "python_version": platform.python_version(),
        "pillow_version": PIL.__version__, "numpy_version": np.__version__,
        "tools": [pin(path) for path in [extract, inspect, extract_impl, SG / "sprite_gen/qa/inspect.py", shared]],
        "installed_tools_modified": False,
        "standard_extract_limitation": "The installed extract_component_frames calls fit_to_cell once per component and does not consume shared_row_scale. Preserve that baseline separately. The existing project wrapper replaces only its fit hook and calls the same installed extractor main with original segmentation, chroma and QA.",
    })
    origins = []
    for relative in [f"raw/{STATE}.png", "sprite-request.json", "base-source.png", f"prompts/{STATE}.txt"]:
        origins.append(copy_source(SOURCE_RUN / relative, OUT / "original-input" / relative))
    write("source-input-pins-v001.json", {"actual_native_request": 183, "copies": origins,
          "root_reported_visual_status": "Four isolated near caps; torso/pouch/far cap removed. Grey-dark opening lining remains, semantic mask/fit/A unaccepted.",
          "root_reported_retention": "E261", "producer_viewed_raw_or_outputs": False})
    results = []
    for mode in ["standard-baseline", "shared-diagnostic"]:
        run = OUT / f"run-{mode}-v001"
        inputs = []
        for relative in [f"raw/{STATE}.png", "sprite-request.json", "base-source.png", f"prompts/{STATE}.txt"]:
            inputs.append(copy_source(SOURCE_RUN / relative, run / relative))
        before = pin(run / "sprite-request.json")
        command = [str(PYTHON), "-B", "-X", "utf8", str(extract if mode == "standard-baseline" else shared), "--run-dir", str(run)]
        extraction = run_tool(f"extract-{mode}-v001", command)
        after = pin(run / "sprite-request.json")
        inspect_command = [str(PYTHON), "-B", "-X", "utf8", str(inspect), "--run-dir", str(run), "--states", STATE,
                           "--report", str(run / "inspect-report.json")]
        inspection = run_tool(f"inspect-{mode}-v001", inspect_command)
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
            "no_palette_quantization": not (run / "palette.lock.json").exists() and q["fit"]["pixel_unfake"] is False,
            "semantic_acceptance": False, "engine_imported": False, "future_component_A": [None] * 4,
        }
        results.append(result)
    mismatches = [path.as_posix() for path, old in WATCHED.items() if pin(path, False) != old]
    report = write("numeric-diagnostic-v001.json", {
        "schema": "near183-numeric-extraction-diagnostic-v001", "actual_native_request": 183,
        "created_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "runs": results, "read_only_sources_rechecked": len(WATCHED), "source_mismatches": mismatches,
        "display_and_timing_contract": {"cell": [512, 512], "shared_fit_window": [60, 44], "durations_ms": [167] * 4},
        "accepted_candidate_for_future_pixel_review": "run-shared-diagnostic-v001 only if extraction succeeds; baseline is comparison evidence, not shared-scale output",
        "semantic_mask_or_lining_material_accepted": False, "actual_fit_or_attachment_A_accepted": False,
        "native_animation_or_common_body_accepted": False, "engine_imported": False,
        "producer_viewed_or_screenshot": False, "generation_called": False,
        "limitations": [
            "This process keys chroma and separates existing components deterministically. It does not semantically erase grey-dark material inside a retained component.",
            "The original base-source.png is the prior native181 editing target (whole vests). Standard inspect style similarity compares against it and is diagnostic only, not a canonical-base lock.",
            "Successful numeric extraction/inspect does not prove the requested component semantics, valid mask, measured A, rig compatibility or animation continuity.",
            "Root must retain this complete candidate under E before viewing any newly extracted frame. No curated/final asset or runtime texture is published here.",
        ],
    })
    if mismatches:
        raise RuntimeError(f"Read-only source changed: {mismatches}")
    brief = []
    for result in results:
        brief.append(f"- {result['mode']}: extract exit {result['extraction']['exit_code']}; inspect exit {result['inspection']['exit_code']}; frames {result['frame_count']}; manifest ok={result['frames_manifest_ok']}; inspect ok={result['inspect_ok']}.")
    write("HANDOFF.md", "# Near183 提取诊断 v001\n\n" + "\n".join(brief) + "\n\n" +
          "标准 extract 的逐帧 fit 基线与既有项目共同 scale hook 结果分开保存；共同版调用同一安装标准 extractor 的 chroma、components、QA 路径，仅替换已锁定的 HD fit hook，没有修改安装工具。所有原始输入按字节保留，没有新 prepare 或输入字段改写。\n\n" +
          "供 Root 未来逐像素检查的是 `run-shared-diagnostic-v001/frames/`。原生183开口灰暗材质没有被本地语义切除，组件语义、mask、实际fit、A及动画均未验收；全部 A=null。没有生成、导入、UE、ledger、人工裁切/绘制，也未浏览/截图新输出。Root 必须先 E 归档再查看。\n\n" +
          "详见 `numeric-diagnostic-v001.json` 的真实命令、退出码、共同 scale 与每帧尺寸 / alpha / 颜色数；不得把自动 QA 等同于最终装备通过。\n")
    files = [pin(path, False) for path in sorted(OUT.rglob("*")) if path.is_file()]
    for value in files:
        value["path"] = Path(value["path"]).relative_to(OUT).as_posix()
    freeze = write("extraction-freeze-v001.json", {
        "schema": "near183-extraction-diagnostic-freeze-v001", "files": files,
        "file_count_excluding_manifest": len(files), "total_bytes_excluding_manifest": sum(value["bytes"] for value in files),
        "semantic_acceptance": False, "viewed": False, "engine_imported": False,
    })
    print(json.dumps({"report": pin(report), "freeze": pin(freeze), "runs": brief,
                      "files_excluding_freeze": len(files), "bytes_excluding_freeze": sum(value["bytes"] for value in files),
                      "source_mismatches": mismatches, "semantic_acceptance": False, "viewed": False}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
