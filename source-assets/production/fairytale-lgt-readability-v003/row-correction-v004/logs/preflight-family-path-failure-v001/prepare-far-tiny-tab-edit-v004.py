"""Prepare a single-target original182 tiny far-tab edit; no generation or art processing."""
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
FAMILY = Path("F:/Ourgame/source-assets/production/fairytale-lgt-readability-v004")
SG = Path("C:/Users/22499/.codex/skills/sprite-gen")
PYTHON = SG / ".venv/Scripts/python.exe"
SOURCE_RUN = FAMILY / "row-preparation-v001/run-farshoulder-ready-v001"
STATE = "leather_farshoulder_sword_ready"
TARGET = SOURCE_RUN / f"raw/{STATE}.png"
TARGET_SHA = "eaa352de4a9eba6386985d48c5c7a07e59a70f1bc969f63ca2b1667ac5e9e4d1"
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
    if OUT != FAMILY / "row-correction-v004" or list(OUT.glob("run-*")):
        raise RuntimeError("Unexpected or existing output")
    target_pin = pin(TARGET)
    if target_pin["sha256"] != TARGET_SHA:
        raise RuntimeError("Actual182 target pin mismatch")
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
    if [cell["width"] - 2 * cell["safe_margin_x"], cell["height"] - 2 * cell["safe_margin_y"]] != [30, 28]:
        raise RuntimeError("Actual Far window changed")
    action = "Selective edit of original182: retain only the four original tiny image-RIGHT far leather tabs at recorded locator ROIs; remove every other garment pixel without changing their compressed perspective or scale."
    seed = {"version": 1, "kind": "sprite-gen-request", "engine": "component-row",
            "cell": cell, "states": {STATE: {"frames": len(durations), "fps": 6, "loop": True,
                                            "action": action, "durations_ms": durations}},
            "motion_phase_guides": False, "fit": old["fit"], "chroma": old["chroma"]}
    seed_path = write("requests/far-tiny-tab-numeric-input-v004.json", seed)
    run = OUT / "run-far-tiny-tab-ready-v004"
    argv = [str(PYTHON), "-B", "-X", "utf8", str(SG / "scripts/prepare_sprite_run.py"),
            "--out-dir", str(run), "--character-id", "fairytale-lgt-far-tiny-tab-edit-v004",
            "--base-image", str(TARGET), "--description", action,
            "--style", "Preserve original182 tiny compressed far tabs, their own brown leather, ink edges and exact four perspectives; never reuse near caps.",
            "--cell-size", "512", "--chroma-key", "#00FF00", "--request", str(seed_path)]
    result = subprocess.run(argv, capture_output=True, text=True, encoding="utf-8")
    log = write("logs/prepare-far-tiny-tab-v004.log", result.stdout + result.stderr)
    command = write("logs/prepare-far-tiny-tab-command-v004.json", {"argv": argv, "exit_code": result.returncode, "log": pin(log)})
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
    write("requests/explicit-fields-v004.json", {"standard_before": pin(before), "changes": changes,
                                                "final": pin(request), "reason": "Restore explicit HD/shared fit, chroma and four 167ms durations after standard prepare whitelist."})
    prompt = run / f"prompts/{STATE}.txt"
    before_prompt = OUT / "standard-output-before-explicit/standard-prompt.txt"
    shutil.copy2(prompt, before_prompt)
    count = q["states"][STATE]["frames"]
    text = f"""EDIT ONLY the attached original182 image, canvas 2172 x 724. Keep ONLY each vest's tiny, narrow, curved BROWN leather tab at its far IMAGE-RIGHT edge, outside the chest-side seam. Preserve all {count} original tabs' compressed perspective, own black edge ink, position, scale and left-to-right order.

Zero-based [left,top,right,bottom) locator ROIs: [419,219,480,310], [918,211,979,303], [1438,220,1499,311], [1946,215,2007,311]. Boundaries have about +/-8px uncertainty. These are locating windows, NOT crop masks, not attachment points. Retain only the actual thin far tab inside each window. Remove adjoining torso pixels and the torso's side seam; retain only the tab's own edge ink. Do not expand the region into a rectangle.

Replace EVERY other foreground pixel with flat opaque GREEN #00FF00: remove all chest, collar, pouch, grey undercloth and the broad IMAGE-LEFT near caps. Do not redraw or mirror a near shoulder, enlarge a tab into a broad front cover, add any long hanging oval/ring, change the canvas, or rearrange/rescale components. Keep four tiny original RIGHT tabs only, fully opaque, with no text or boxes.

Metadata: {q['states'][STATE]['durations_ms']} ms; later 30 x 28 shared extraction fit in512 cells. Future A remains null; no sizing change during editing.
"""
    prompt.write_text(text, encoding="utf-8")
    if len(text.split()) >= 250:
        raise RuntimeError("Correction prompt is not short")
    base = run / "base-source.png"
    if pin(base)["sha256"] != TARGET_SHA:
        raise RuntimeError("Editing copy changed")
    draft = write("lgt-far-tiny-tab-edit-input-draft-v004.json", {
        "schema": "near183-lining-selective-edit-input-draft-v004",
        "created_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(), "created_local": datetime.datetime.now().astimezone().isoformat(), "source_event": "EV-048",
        "rows": [{"component": "FarShoulder", "runtime_component": "ShoulderFar", "state": STATE,
                  "run_dir": run.as_posix(), "raw_output_path": (run / f"raw/{STATE}.png").as_posix(),
                  "prompt": pin(prompt), "request": pin(request),
                  "reference_images_in_order": [{"role": "single_exact_native183_edit_target_only", "file": pin(base)}],
                  "reference_count": 1, "transparent_background": False, "background_hex": "#00FF00",
                  "frame_count": count, "durations_ms": durations, "fit_window_design_px": [30, 28],
                  "shared_row_scale": True, "per_frame_scale_normalization": False,
                  "future_component_A": [None] * count, "native_request_number": None,
                  "planned_native_number_if_next": 187, "generation_ready": False,
                  "failed_raw_native_number": 182, "failed_target": target_pin,
                  "target_mode": source_mode, "target_canvas_px": source_size,
                  "standard_prepare_exit_code": result.returncode, "standard_prepare_command": argv}],
        "generation_ready": False, "root_review_required_before_generation": True,
        "planned_187_is_not_a_ledger_reservation": True,
        "source_root_review_report": "Original182 retained E257 and185 retained E269 were actually viewed by this producer in the prior far185 perspective review.185 failed by substituting broad near-style caps and dangling rings. Only original182 tiny image-RIGHT tabs are valid next editing targets.",
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
    write("preparation-verification-v004.json", {"prepare_exit_code": result.returncode,
           "read_only_source_rechecks": len(WATCHED), "source_mismatches": mismatches,
           "raw_created": list(str(path) for path in run.glob("raw/*") if path.is_file()),
           "future_A_all_null": True, "generation_called": False, "viewed": False})
    write("HANDOFF.md", "# 原182 tiny far-tab编辑输入 v004\n\n标准 sprite-gen prepare 实际 exit0。唯一target是最初182原raw逐字节copy，不引用185。短prompt小于250词，四个2172×724坐标ROI仅定位±8px，不是mask/A；保留原far右侧极窄弯tab自身透视/边墨，删除邻接躯干黑缝、左宽cap和长环。\n\n4×167ms，30×28共同窗口，future A全null。计划187未ledger预留。generation_ready=false，未生成、导入、绘制、裁切或查看新guide，Root先审输入并E留档。\n")
    files = [pin(path, False) for path in sorted(OUT.rglob("*")) if path.is_file()]
    for item in files:
        item["path"] = Path(item["path"]).relative_to(OUT).as_posix()
    freeze = write("preparation-freeze-v004.json", {"schema": "far-tiny-tab-preparation-freeze-v004", "files": files,
                   "file_count_excluding_manifest": len(files), "total_bytes_excluding_manifest": sum(item["bytes"] for item in files),
                   "generation_ready": False, "viewed": False})
    print(json.dumps({"draft": pin(draft), "freeze": pin(freeze), "prepare_exit_code": result.returncode,
                      "prompt_words": len(text.split()), "frozen_files": len(files),
                      "frozen_bytes": sum(item["bytes"] for item in files), "generation_ready": False}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
