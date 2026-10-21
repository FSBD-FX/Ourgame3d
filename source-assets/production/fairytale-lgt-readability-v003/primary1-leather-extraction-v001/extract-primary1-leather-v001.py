"""Extract native188/189/190 component candidates; no image viewing or fitting."""
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
INPUT = FAMILY / "primary1-leather-input-v001"
SG = Path("C:/Users/22499/.codex/skills/sprite-gen")
PYTHON = SG / ".venv/Scripts/python.exe"
TIMES = [85, 85, 60, 60, 155, 155]
EXTRACT_SHA = "f2a7902f01069668340d14217bd05c777f5c01853284102e211aba1013a45539"
WRAPPER_SHA = "2d7464dc2e8dd962a7d4dc170c0a7401d09cf1a626415309b4921b7d89d88aa3"
COMPONENTS = [
    ("Chest", "chest", 188, [90, 90], 512, "7b07f7c624e7c9bd930fbecb6db7e77051a9f9447f9af59686388e710ed5f46f"),
    ("NearShoulder", "nearshoulder", 189, [60, 44], 512, "952a67f9a5218a08d9aa41b6c7956ab9bfcbb9178f45e55a7a039a2f7e987657"),
    ("FarShoulder", "farshoulder", 190, [32, 30], 256, "ca5fb453f4e78058fc363f19364d3f4ded08f29abe2425e6c6b5d1a5c5eb641b"),
]
WATCHED = {}


def pin(path, watch=True):
    data = path.read_bytes()
    value = {"path": path.as_posix(), "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}
    if watch and not path.is_relative_to(OUT):
        WATCHED[path] = value
    return value


def write(relative, data):
    path = OUT / relative
    if not path.is_relative_to(OUT):
        raise RuntimeError("Ownership boundary")
    path.parent.mkdir(parents=True, exist_ok=True)
    text = data if isinstance(data, str) else json.dumps(data, ensure_ascii=False, indent=2) + "\n"
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(text)
    return path


def copy_exact(source, target):
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        raise RuntimeError("Existing output cannot be overwritten")
    source_pin = pin(source)
    shutil.copy2(source, target)
    copied = pin(target)
    if source_pin["sha256"] != copied["sha256"] or source_pin["bytes"] != copied["bytes"]:
        raise RuntimeError("Input byte copy changed")
    return {"source": source_pin, "copy": copied}


def command(label, argv):
    result = subprocess.run(argv, capture_output=True, text=True, encoding="utf-8")
    log = write(f"logs/{label}.log", result.stdout + result.stderr)
    record = {"argv": argv, "actual_exit_code": result.returncode, "log": pin(log)}
    path = write(f"logs/{label}-command.json", record)
    return {**record, "command_record": pin(path)}


def pixel_metrics(path):
    with Image.open(path) as image:
        if image.mode != "RGBA" or image.size != (512, 512):
            raise RuntimeError("Expected candidate source 512 RGBA")
        array = np.asarray(image).copy()
        alpha = array[:, :, 3]
        core = alpha >= 128
        edge = np.zeros(alpha.shape, dtype=bool)
        edge[:4, :] = edge[-4:, :] = True
        edge[:, :4] = edge[:, -4:] = True
        box = image.getchannel("A").getbbox()
        core_box = image.getchannel("A").point(lambda a: 255 if a >= 128 else 0).getbbox()
        return {"source": pin(path), "mode": image.mode, "canvas_px": list(image.size),
                "RGBA_pixels_sha256": hashlib.sha256(array.tobytes()).hexdigest(),
                "alpha_nonzero_bbox_ltrb_exclusive": list(box) if box else None,
                "core128_bbox_ltrb_exclusive": list(core_box) if core_box else None,
                "nonzero_alpha_pixels": int(np.count_nonzero(alpha)),
                "core128_RGBA_pixels": int(np.count_nonzero(core)),
                "core128_RGBA_row_major_sha256": hashlib.sha256(array[core].tobytes()).hexdigest(),
                "partial_alpha_pixels": int(np.count_nonzero((alpha > 0) & (alpha < 255))),
                "distinct_core_RGB_colors": int(len(np.unique(array[:, :, :3][core], axis=0))),
                "pure_green_nonzero_alpha_pixels": int(np.count_nonzero((alpha > 0) & np.all(array[:, :, :3] == [0, 255, 0], axis=2))),
                "edge_nonzero_alpha_pixels_margin4": int(np.count_nonzero((alpha > 0) & edge)),
                "bodyfreecount": None, "bodyfreecount_measured": False,
                "bodyfree_semantic_note": "RGBA/chroma/edge counts cannot count anatomical bodies, hands or helmets. No semantic mask or detector was supplied; do not turn six connected components into a claim of body-free art.",
                "new_component_A": None, "matching_body_B": None, "integer_delta_xy": None}


def main():
    if Path(sys.executable).resolve() != PYTHON.resolve():
        raise RuntimeError("Use sprite-gen venv")
    if OUT != FAMILY / "primary1-leather-extraction-v001" or list(OUT.glob("run-*")):
        raise RuntimeError("Unexpected or existing output")
    installed = SG / "sprite_gen/frames/extract.py"
    old_wrapper = PROJECT / "tools/scripts/extract-sprite-shared-row-scale.py"
    if pin(installed)["sha256"] != EXTRACT_SHA or pin(old_wrapper)["sha256"] != WRAPPER_SHA:
        raise RuntimeError("Pinned extractor/fit extension changed")
    copy_exact(old_wrapper, OUT / "tool-provenance/shared-row-fit-original-v001.py")
    wrapper_text = old_wrapper.read_text(encoding="utf-8")
    parser_line = "    args = parser.parse_args()"
    if wrapper_text.count(parser_line) != 1:
        raise RuntimeError("Wrapper CLI changed")
    wrapper_text = wrapper_text.replace(parser_line, "    parser.add_argument(\"--min-used-pixels\", type=int, required=True)\n" + parser_line + "\n    require(args.min_used_pixels in (256,512), \"Only authorized explicit component floors256/512\")", 1)
    original_cli = "        sys.argv = [str(EXTRACT), \"--run-dir\", str(run)]"
    if wrapper_text.count(original_cli) != 1:
        raise RuntimeError("Native fit hook bridge changed")
    wrapper_text = wrapper_text.replace(original_cli, "        sys.argv = [str(EXTRACT), \"--run-dir\", str(run), \"--min-used-pixels\", str(args.min_used_pixels)]", 1)
    wrapper = write("shared-HD-fit-explicit-component-min-v001.py", wrapper_text)
    tools = [SG / "scripts/extract_sprite_row_frames.py", installed, SG / "scripts/inspect_sprite_run.py", SG / "sprite_gen/qa/inspect.py", old_wrapper]
    write("toolchain-v001.json", {"python_executable": sys.executable, "python_version": platform.python_version(),
          "pillow_version": PIL.__version__, "numpy_version": np.__version__, "installed_tools": [pin(path) for path in tools],
          "candidate_fit_bridge": pin(wrapper), "installed_or_project_tools_modified": False,
          "fit_bridge_change": "Only explicit min-used-pixels CLI forwarding. Original shared-HD fitting/chroma/components/edge/count logic unchanged. Subject stays character; no effect relabel.",
          "standard_extract_does_not_consume_shared_row_scale": True})
    runs = []
    source_index = []
    for name, token, native, window, minimum, raw_sha in COMPONENTS:
        source_run = INPUT / f"run-{token}-primary1-v001"
        state = f"leather_{token}_sword_primary1"
        raw = source_run / f"raw/{state}.png"
        request = source_run / "sprite-request.json"
        receipt_path = FAMILY / f"generation-control-v001/generation-receipt{native}-v001.json"
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
        if pin(raw)["sha256"] != raw_sha or pin(raw) != receipt["canonical_raw"]:
            raise RuntimeError("Actual native raw pin differs")
        pin(receipt_path)
        q = json.loads(request.read_text(encoding="utf-8"))
        if q["states"][state]["frames"] != 6 or q["states"][state]["durations_ms"] != TIMES:
            raise RuntimeError("Six-phase timing changed")
        if q["fit"]["pixel_unfake"] is not False or q["fit"]["shared_row_scale"] is not True:
            raise RuntimeError("Explicit nonquantized shared-HD fit required")
        if [q["cell"]["width"] - 2 * q["cell"]["safe_margin_x"], q["cell"]["height"] - 2 * q["cell"]["safe_margin_y"]] != window:
            raise RuntimeError("Shared fit window changed")
        originals = []
        for relative in [f"raw/{state}.png", "sprite-request.json", "base-source.png", f"prompts/{state}.txt"]:
            originals.append(copy_exact(source_run / relative, OUT / f"original-input/{token}" / relative))
        write(f"original-input/{token}/native-source-receipt-pin.json", {"native_request": native, "receipt": pin(receipt_path), "source_copies": originals})
        for mode in ["standard-baseline", "shared-HD"]:
            run = OUT / f"run-{token}-{mode}-v001"
            for relative in [f"raw/{state}.png", "sprite-request.json", "base-source.png", f"prompts/{state}.txt"]:
                copy_exact(source_run / relative, run / relative)
            before = pin(run / "sprite-request.json")
            # Baseline deliberately retains the standard whole-character512
            # floor, so any mismatch with a tiny attachment is preserved.
            argv = [str(PYTHON), "-B", "-X", "utf8", str(SG / "scripts/extract_sprite_row_frames.py" if mode == "standard-baseline" else wrapper), "--run-dir", str(run)]
            if mode == "shared-HD":
                argv.extend(["--min-used-pixels", str(minimum)])
            extraction = command(f"extract-{token}-{mode}-v001", argv)
            after = pin(run / "sprite-request.json")
            inspection = command(f"inspect-{token}-{mode}-v001", [str(PYTHON), "-B", "-X", "utf8", str(SG / "scripts/inspect_sprite_run.py"),
                                 "--run-dir", str(run), "--states", state, "--report", str(run / "inspect-report.json")])
            fm_path, inspect_path = run / "frames/frames-manifest.json", run / "inspect-report.json"
            fm = json.loads(fm_path.read_text(encoding="utf-8")) if fm_path.exists() else None
            inspect = json.loads(inspect_path.read_text(encoding="utf-8")) if inspect_path.exists() else None
            files = sorted((run / f"frames/{state}").glob("frame-*.png"))
            metrics = [pixel_metrics(path) for path in files]
            entry = {"component": name, "native_request": native, "mode": mode, "run_dir": run.as_posix(), "state": state,
                     "extraction": extraction, "inspection": inspection, "frames": len(files), "metrics": metrics,
                     "frames_manifest": pin(fm_path) if fm_path.exists() else None,
                     "manifest_ok": fm.get("ok") if fm else None, "manifest_errors": fm.get("errors") if fm else None,
                     "manifest_warnings": fm.get("warnings") if fm else None,
                     "shared_row_fit": fm["rows"][0].get("shared_row_fit") if fm and fm.get("rows") else None,
                     "inspect_report": pin(inspect_path) if inspect_path.exists() else None,
                     "inspect_ok": inspect.get("ok") if inspect else None,
                     "inspect_errors": inspect.get("errors") if inspect else None, "inspect_warnings": inspect.get("warnings") if inspect else None,
                     "actual_min_used_pixels": minimum if mode == "shared-HD" else 512,
                     "request_before": before, "request_after": after, "working_request_bytes_unchanged": before["sha256"] == after["sha256"],
                     "no_pixel_unfake_or_palette_quantization": not (run / "palette.lock.json").exists(),
                     "semantic_fit_or_full_animation_accepted": False}
            runs.append(entry)
            if mode == "shared-HD":
                available = extraction["actual_exit_code"] == 0 and fm is not None and fm["ok"] is True and len(files) == 6
                source_index.append({"component": name, "native_request": native, "state": state, "shared_fit_window": window,
                                     "explicit_min_used_pixels": minimum, "available_for_Root_feature_measurement": available,
                                     "shared_row_fit": entry["shared_row_fit"], "frames": [{"frame": i, "duration_ms": TIMES[i], **metric} for i, metric in enumerate(metrics)],
                                     "missing_frames_are_not_faked": True, "new_A_B_delta_all_null": True,
                                     "Chest_phase4_body159_perspective_review_required": name == "Chest"})
    mismatches = [path.as_posix() for path, before in WATCHED.items() if pin(path, False) != before]
    if mismatches:
        raise RuntimeError(f"Read-only source changed: {mismatches}")
    index = write("primary1-eighteen-source-index-v001.json", {"schema": "primary1-leather-six-phase-three-component-source-index-v001",
          "created_local": datetime.datetime.now().astimezone().isoformat(), "components": source_index,
          "actual_available_frame_count": sum(len(row["frames"]) for row in source_index), "expected_frame_count": 18,
          "all_three_rows_available": all(row["available_for_Root_feature_measurement"] for row in source_index),
          "durations_ms": TIMES, "all_A_B_delta_null": True, "new_media_viewed": False,
          "semantic_bodyfreecount_known": False, "fit_accepted": False, "imported": False,
          "Root_raw_review_context": "Root retained188/189/190 in E286/E287/E288 and viewed all raw rows before authorizing extraction. Chest phase4 reverse torso perspective still requires actual Body159 review.",
          "next_boundary": "Root E-retains extracted frames before viewing, then measures actual features/new A/B and verifies body159 six-phase perspective/occlusion. No automatic registration or component copy/flip for Chest4."})
    report = write("extraction-numeric-report-v001.json", {"schema": "primary1-leather-extraction-numeric-v001", "created_local": datetime.datetime.now().astimezone().isoformat(),
          "runs": runs, "source_index": pin(index), "read_only_sources_rechecked": len(WATCHED), "source_mismatches": [],
          "generated": False, "new_media_viewed": False, "Source_UE_ledger_or_media_modified": False,
          "lower_than_256_floor_attempted": False, "semantic_count_or_A_fabricated": False,
          "limitations": ["Standard and shared extraction/inspect exit codes are actual. Preserve default floor failures and low-motion warnings, even when another declared component floor produces frames.",
                         "Shared scale is computed per six-frame row; no per-frame normalization, pixel-unfake, palette quantization or manual paint/crop repair.",
                         "Body-free semantic counts cannot be inferred from RGBA/core/green/edge metrics; bodyfreecount is null without actual semantic masks/visual review.",
                         "Chest4 reverse torso direction remains an actual Body159 comparison question. Extraction is not fit or full animation acceptance."]})
    lines = [f"- {row['component']} {row['mode']}: extract exit{row['extraction']['actual_exit_code']}; inspect exit{row['inspection']['actual_exit_code']}; frames{row['frames']}; inspect warnings={row['inspect_warnings']}." for row in runs]
    write("HANDOFF.md", "# Primary1软皮六相提取诊断 v001\n\n" + "\n".join(lines) + "\n\n" +
          "供Root测feature的Source见 `primary1-eighteen-source-index-v001.json` 与 `run-{chest,nearshoulder,farshoulder}-shared-HD-v001/frames/`。全部A/B/delta仍null；无自动贴合/镜像/动作补帧。Chest4反向torso必须与实际Body159核，不能因提取通过就接受fit。\n\n" +
          "min512/512/256为本组件配置；低于256未尝试。默认baseline失败及inspect低motion全部保留。bodyfreecount无语义mask无法由通道推断，诚实为null；已给每帧coreRGBA/hash/纯绿/edge及真实共同scale。执行者未查看新输出、未生成/导入/改旧run或tools/Source/UE/ledger/媒体。Root先E留后看。\n")
    files = [pin(path, False) for path in sorted(OUT.rglob("*")) if path.is_file()]
    for item in files:
        item["path"] = Path(item["path"]).relative_to(OUT).as_posix()
    freeze = write("extraction-freeze-v001.json", {"schema": "primary1-leather-extraction-freeze-v001", "files": files,
          "file_count_excluding_manifest": len(files), "total_bytes_excluding_manifest": sum(item["bytes"] for item in files),
          "actual_available_frame_count": sum(len(row["frames"]) for row in source_index), "viewed": False, "fit_accepted": False})
    print(json.dumps({"report": pin(report), "source_index": pin(index), "freeze": pin(freeze),
          "actual_available_frame_count": sum(len(row["frames"]) for row in source_index),
          "shared_rows_available": [row["available_for_Root_feature_measurement"] for row in source_index],
          "actual_run_exits": [{"component": row["component"], "mode": row["mode"], "extract": row["extraction"]["actual_exit_code"], "inspect": row["inspection"]["actual_exit_code"]} for row in runs],
          "frozen_files": len(files), "frozen_bytes": sum(item["bytes"] for item in files), "new_media_viewed": False}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
