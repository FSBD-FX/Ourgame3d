"""Prepare a single-target Near183 lining edit; no generation or art processing."""
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
FAMILY = Path("F:/Ourgame/source-assets/production/fairytale-lgt-readability-v003")
SG = Path("C:/Users/22499/.codex/skills/sprite-gen")
PYTHON = SG / ".venv/Scripts/python.exe"
SOURCE_RUN = FAMILY / "row-correction-v002/run-nearshoulder-ready-v002"
STATE = "leather_nearshoulder_sword_ready"
TARGET = SOURCE_RUN / f"raw/{STATE}.png"
TARGET_SHA = "a3c9a4ea3b5d4be00fc489807c0c61d086081b7d757e219894e3b30c319c9d27"
WATCHED = {}


def pin(path, watch=True):
    data = path.read_bytes()
    result = {"path": path.as_posix(), "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}
    if watch and not path.is_relative_to(OUT):
        WATCHED[path] = result
    return result


def write(relative, value):
    path = OUT / relative
    if not path.is_relative_to(OUT):
        raise RuntimeError("Ownership boundary")
    path.parent.mkdir(parents=True, exist_ok=True)
    text = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False, indent=2) + "\n"
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(text)
    return path


def main():
    if Path(sys.executable).resolve() != PYTHON.resolve():
        raise RuntimeError("Use sprite-gen venv")
    if OUT != FAMILY / "row-correction-v003" or list(OUT.glob("run-*")):
        raise RuntimeError("Unexpected or existing output")
    target_pin = pin(TARGET)
    if target_pin["sha256"] != TARGET_SHA:
        raise RuntimeError("Actual183 target pin mismatch")
    source_request = SOURCE_RUN / "sprite-request.json"
    old = json.loads(source_request.read_text(encoding="utf-8-sig"))
    pin(source_request)
    with Image.open(TARGET) as image:
        source_size, source_mode = list(image.size), image.mode
    durations = old["states"][STATE]["durations_ms"]
    if durations != [167] * 4 or old["states"][STATE]["frames"] != 4:
        raise RuntimeError("Actual timing changed")
    if old["fit"]["pixel_unfake"] is not False or old["fit"]["shared_row_scale"] is not True:
        raise RuntimeError("HD shared-row fit required")
    cell = old["cell"]
    if [cell["width"] - 2 * cell["safe_margin_x"], cell["height"] - 2 * cell["safe_margin_y"]] != [60, 44]:
        raise RuntimeError("Actual Near window changed")
    action = "Selective edit of the four existing Near183 shoulder caps: remove only grey/charcoal under-cap lining and the low hanging oval ring; preserve the brown leather cap and ink outline."
    seed = {"version": 1, "kind": "sprite-gen-request", "engine": "component-row",
            "cell": cell, "states": {STATE: {"frames": len(durations), "fps": 6, "loop": True,
                                            "action": action, "durations_ms": durations}},
            "motion_phase_guides": False, "fit": old["fit"], "chroma": old["chroma"]}
    seed_path = write("requests/near-lining-numeric-input-v003.json", seed)
    run = OUT / "run-nearshoulder-lining-ready-v003"
    argv = [str(PYTHON), "-B", "-X", "utf8", str(SG / "scripts/prepare_sprite_run.py"),
            "--out-dir", str(run), "--character-id", "fairytale-lgt-near-lining-edit-v003",
            "--base-image", str(TARGET), "--description", action,
            "--style", "Preserve this exact target's warm brown soft-leather cap, coarse dark ink outline and existing four perspectives.",
            "--cell-size", "512", "--chroma-key", "#00FF00", "--request", str(seed_path)]
    result = subprocess.run(argv, capture_output=True, text=True, encoding="utf-8")
    log = write("logs/prepare-near-lining-v003.log", result.stdout + result.stderr)
    command = write("logs/prepare-near-lining-command-v003.json", {"argv": argv, "exit_code": result.returncode, "log": pin(log)})
    if result.returncode != 0:
        raise RuntimeError(f"Standard prepare failed: {log}")
    request = run / "sprite-request.json"
    before = OUT / "standard-output-before-explicit/sprite-request.json"
    before.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(request, before)
    q = json.loads(request.read_text(encoding="utf-8-sig"))
    changes = {}
    for key in ("fit", "chroma", "motion_phase_guides"):
        if q.get(key) != seed[key]:
            changes[key] = {"before": q.get(key), "after": seed[key]}
            q[key] = seed[key]
    if q["states"][STATE].get("durations_ms") != durations:
        changes[f"states.{STATE}.durations_ms"] = {"before": q["states"][STATE].get("durations_ms"), "after": durations}
        q["states"][STATE]["durations_ms"] = durations
    request.write_text(json.dumps(q, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write("requests/explicit-fields-v003.json", {"standard_before": pin(before), "changes": changes,
                                                "final": pin(request), "reason": "Restore explicit HD/shared fit, chroma and four 167ms durations after standard prepare whitelist."})
    prompt = run / f"prompts/{STATE}.txt"
    before_prompt = OUT / "standard-output-before-explicit/standard-prompt.txt"
    shutil.copy2(prompt, before_prompt)
    count = q["states"][STATE]["frames"]
    text = f"""EDIT ONLY THE ONE ATTACHED IMAGE, the actual native183 row of {count} isolated near-shoulder caps. It already has the correct brown leather cap bodies. Keep all {count} original views, canvas aspect ratio ({source_size[0]} x {source_size[1]}), positions, perspective, scale, brown leather planes, curved cap edges, seams and black ink contours exactly as they are.

Remove ONLY the grey/charcoal under-cap lining and the low dangling oval ring beneath each brown cap. Replace those unwanted under-cap areas with flat opaque GREEN #00FF00. Preserve the brown cap itself and the dark ink boundary directly outlining it; do not erase leather shadows or add new leather to fill the removed lining. No hanging grey oval, inner sleeve, fabric throat or ghost ring may remain below the cap.

Do not redraw, enlarge, move, rotate, mirror or duplicate any cap. Do not add a torso, complete vest, collar, pouch, other shoulder, body or new ornament. Leave every other existing pixel and the four-view order unchanged. Output the edited row only, fully opaque on flat #00FF00, with no text, checkerboard or transparency.

Request timing is {q['states'][STATE]['durations_ms']} ms. Later extraction uses one shared 60 x 44 window in 512 x 512 cells; this does not authorize resizing during editing. Future attachment A remains null in all {count} views. This is an unaccepted correction candidate, not a completed armor or animation.
"""
    prompt.write_text(text, encoding="utf-8")
    if len(text.split()) > 350:
        raise RuntimeError("Correction prompt is not short")
    base = run / "base-source.png"
    if pin(base)["sha256"] != TARGET_SHA:
        raise RuntimeError("Editing copy changed")
    draft = write("lgt-near-lining-edit-input-draft-v003.json", {
        "schema": "near183-lining-selective-edit-input-draft-v003",
        "created_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(), "source_event": "EV-048",
        "rows": [{"component": "NearShoulder", "runtime_component": "ShoulderNear", "state": STATE,
                  "run_dir": run.as_posix(), "raw_output_path": (run / f"raw/{STATE}.png").as_posix(),
                  "prompt": pin(prompt), "request": pin(request),
                  "reference_images_in_order": [{"role": "single_exact_native183_edit_target_only", "file": pin(base)}],
                  "reference_count": 1, "transparent_background": False, "background_hex": "#00FF00",
                  "frame_count": count, "durations_ms": durations, "fit_window_design_px": [60, 44],
                  "shared_row_scale": True, "per_frame_scale_normalization": False,
                  "future_component_A": [None] * count, "native_request_number": None,
                  "planned_native_number_if_next": 186, "generation_ready": False,
                  "failed_raw_native_number": 183, "failed_target": target_pin,
                  "target_mode": source_mode, "target_canvas_px": source_size,
                  "standard_prepare_exit_code": result.returncode, "standard_prepare_command": argv}],
        "generation_ready": False, "root_review_required_before_generation": True,
        "planned_186_is_not_a_ledger_reservation": True,
        "source_root_review_report": "Native183 was retained in E261 and viewed by Root. Isolated caps are present but grey-charcoal under-cap lining/low oval ring remains unaccepted. This producer did not view it.",
        "layout_guide_not_attached_to_editor": True,
        "base_source_role_override": "Exact multi-view selective-edit target, not a newly accepted canonical base or mother-body lock.",
        "producer_viewed_or_screenshot": False, "generation_called": False, "ue_or_import_called": False,
        "semantic_mask_fit_A_or_motion_accepted": False, "formal_complete_units": 0,
        "standard_prompt_before_override": pin(before_prompt), "prompt_word_count": len(text.split()),
        "toolchain": {"python_executable": sys.executable, "python_version": platform.python_version(),
                      "pillow_version": PIL.__version__, "numpy_version": np.__version__,
                      "prepare": pin(SG / "scripts/prepare_sprite_run.py"), "prepare_implementation": pin(SG / "sprite_gen/gen/prepare.py"),
                      "installed_tools_modified": False}, "prepare_command_record": pin(command)})
    mismatches = [path.as_posix() for path, old_pin in WATCHED.items() if pin(path, False) != old_pin]
    if mismatches:
        raise RuntimeError(f"Read-only input changed: {mismatches}")
    write("preparation-verification-v003.json", {"prepare_exit_code": result.returncode,
           "read_only_source_rechecks": len(WATCHED), "source_mismatches": mismatches,
           "raw_created": list(str(path) for path in run.glob("raw/*") if path.is_file()),
           "future_A_all_null": True, "generation_called": False, "viewed": False})
    write("HANDOFF.md", "# Near183 内衬纠错输入 v003\n\n标准 sprite-gen prepare 实际 exit 0。唯一编辑 target 是183原raw的逐字节副本；短prompt只移除 cap 下灰炭内衬与低垂 oval ring，保留brown cap、边缘、黑墨轮廓、四视图布局/透视/大小。\n\n4×167ms，60×44共同窗口，future A全null。不附加guide；计划186仅草案，Root按真实ledger编号。generation_ready=false。未生成、未绘制/裁切、未导入、未浏览新guide，Root先审输入并E归档。\n")
    files = [pin(path, False) for path in sorted(OUT.rglob("*")) if path.is_file()]
    for item in files:
        item["path"] = Path(item["path"]).relative_to(OUT).as_posix()
    freeze = write("preparation-freeze-v003.json", {"schema": "near-lining-preparation-freeze-v003", "files": files,
                   "file_count_excluding_manifest": len(files), "total_bytes_excluding_manifest": sum(item["bytes"] for item in files),
                   "generation_ready": False, "viewed": False})
    print(json.dumps({"draft": pin(draft), "freeze": pin(freeze), "prepare_exit_code": result.returncode,
                      "prompt_words": len(text.split()), "frozen_files": len(files),
                      "frozen_bytes": sum(item["bytes"] for item in files), "generation_ready": False}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
