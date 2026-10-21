"""Prepare component-only editing drafts; no generation, image repair or preview."""
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
OLD = FAMILY / "row-preparation-v001"
SG = Path("C:/Users/22499/.codex/skills/sprite-gen")
PYTHON = SG / ".venv/Scripts/python.exe"
DURATIONS = [167, 167, 167, 167]
ROWS = [
    ("Chest", "chest", "Chest", 180, 183, [90, 90],
     "b1a1b1f493786ed6f9fbd8012421f2b2d93f48becbd49ec36c18d50ba23262b4"),
    ("NearShoulder", "nearshoulder", "ShoulderNear", 181, 184, [60, 44],
     "4bd66b64404ee030a58d9bba2e335f74b1a005d984533273b2964bfc7b93ecf7"),
    ("FarShoulder", "farshoulder", "ShoulderFar", 182, 185, [30, 28],
     "eaa352de4a9eba6386985d48c5c7a07e59a70f1bc969f63ca2b1667ac5e9e4d1"),
]
WATCHED: dict[Path, dict] = {}


def descriptor(path: Path, watch: bool = True) -> dict:
    data = path.read_bytes()
    pin = {"path": path.as_posix(), "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}
    if watch and not path.is_relative_to(OUT):
        WATCHED[path] = pin
    return pin


def write(relative: str, value: dict | str) -> Path:
    path = OUT / relative
    if not path.is_relative_to(OUT):
        raise RuntimeError(f"Write outside ownership: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False, indent=2) + "\n"
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(payload)
    return path


def correction_instructions(component: str) -> str:
    if component == "Chest":
        return """KEEP ONLY the connected soft-leather chest / waist jerkin panel and its attached small pouch in each of the four views. Keep their actual left-to-right perspective differences, coarse dark ink contours, tawny highlights, reddish-brown leather planes, existing soft folds, clasp and pouch construction. REMOVE BOTH shoulder caps completely: the larger image-LEFT cap and the smaller image-RIGHT cap. REMOVE all grey undercloth, grey neck or sleeve interior, grey collar-hole filling, body, neck, arms, gloves and any unrelated pixels. Do not fill removed shoulder areas with a new sleeve or pauldron. Preserve the leather torso / waist edge and the attached pouch as one connected chest component; do not detach the pouch or leave a floating fastener. Green must show through openings where grey undercloth was removed. The result is four isolated sleeveless chest-and-waist leather components, not four complete vests with shoulder caps."""
    if component == "NearShoulder":
        return """KEEP ONLY the short brown soft-leather shoulder cap on the IMAGE-LEFT side of EACH existing vest. This is the larger foreground / near cap, not an anatomical-left instruction. Preserve each of those four actual image-LEFT caps' own perspective, curved cut edge, coarse ink outline, warm leather planes, folds and seam. REMOVE EVERY PIXEL of the torso, chest front, neck/collar, waist/belt, pouch, fasteners belonging to the torso, image-RIGHT far shoulder, sleeves, body and grey undercloth. REMOVE grey or dark cloth filling inside a shoulder opening: replace non-leather interior / hole filling with pure green. Do not leave a chest strip, a collar bridge, a pouch, a complete vest, a ghost torso or a second cap. The four outputs must be only four compact IMAGE-LEFT near-shoulder leather caps. Do not redesign, mirror, rotate or synthesize another cap; do not turn the crop selection into a full garment."""
    return """KEEP ONLY the small compressed brown soft-leather shoulder cap on the IMAGE-RIGHT side of EACH existing vest. This is the deeper / far cap, not an anatomical-right instruction. Preserve each of those four actual image-RIGHT caps' own compressed perspective, small curved silhouette, coarse ink outline, restrained warm highlight, leather planes and seam. REMOVE EVERY PIXEL of the torso, chest front, neck/collar, waist/belt, pouch, fasteners belonging to the torso, image-LEFT near shoulder, sleeves, body and grey undercloth. REMOVE grey or dark cloth filling inside the shoulder opening: replace non-leather interior / hole filling with pure green. Do not leave a chest strip, a collar bridge, a pouch, a complete vest, a ghost torso or a second cap. The four outputs must be only four small IMAGE-RIGHT far-shoulder leather caps. NEVER mirror or reuse the image-LEFT near cap; keep the actual four far-cap views from this exact target."""


def main() -> None:
    if Path(sys.executable).resolve() != PYTHON.resolve():
        raise RuntimeError(f"Use sprite-gen venv: {PYTHON}; got {sys.executable}")
    if OUT != FAMILY / "row-correction-v002":
        raise RuntimeError("Unexpected ownership root")
    if (OUT / "lgt-ready-correction-input-draft-v002.json").exists():
        raise RuntimeError("Existing version cannot be overwritten")
    if list(OUT.glob("run-*")):
        raise RuntimeError("Existing runs cannot be overwritten")

    tools = [SG / "SKILL.md", SG / "docs/chroma-alpha.md", SG / "docs/layer-tracks.md",
             SG / "scripts/prepare_sprite_run.py", SG / "sprite_gen/gen/prepare.py"]
    toolchain = write("toolchain-provenance-v002.json", {
        "python_executable": sys.executable, "python_version": platform.python_version(),
        "pillow_version": PIL.__version__, "numpy_version": np.__version__,
        "tools": [descriptor(path) for path in tools], "tools_modified": False,
        "preparation_only": True, "generation_called": False,
    })
    old_draft = json.loads((OLD / "lgt-ready-native-input-approved-v002.json").read_text(encoding="utf-8-sig"))
    descriptor(OLD / "lgt-ready-native-input-approved-v002.json")
    rows = []
    for component, token, runtime_key, failed_number, draft_number, window, expected_sha in ROWS:
        state = f"leather_{token}_sword_ready"
        target = OLD / f"run-{token}-ready-v001/raw/{state}.png"
        target_pin = descriptor(target)
        if target_pin["sha256"] != expected_sha:
            raise RuntimeError(f"Target pin mismatch: {target}")
        with Image.open(target) as image:
            target_size = list(image.size)
            target_mode = image.mode
        existing = next(row for row in old_draft["rows"] if row["component"] == component)
        margins = [(512 - size) // 2 for size in window]
        action = f"Edit the four existing native{failed_number} views; retain ONLY the {component} leather component, removing every other garment/body component. Preserve the corresponding four actual perspectives."
        seed = {
            "version": 1, "kind": "sprite-gen-request", "engine": "component-row",
            "states": {state: {"frames": len(DURATIONS), "fps": 6, "loop": True,
                               "action": action, "durations_ms": DURATIONS}},
            "cell": {"width": 512, "height": 512,
                     "safe_margin_x": margins[0], "safe_margin_y": margins[1]},
            "motion_phase_guides": False,
            "fit": {"pixel_unfake": False, "resample": "lanczos", "align_x": "bbox-center",
                    "align_y": "bottom", "ground_frames": False, "segmentation": "components",
                    "shared_row_scale": True},
            "chroma": {"mode": "rgb", "unmix_reach": 4, "spill_max_fraction": 0.005},
        }
        seed_path = write(f"requests/{token}-correction-numeric-input-v002.json", seed)
        run = OUT / f"run-{token}-ready-v002"
        argv = [str(PYTHON), "-X", "utf8", "-B", str(SG / "scripts/prepare_sprite_run.py"),
                "--out-dir", str(run), "--character-id", f"fairytale-lgt-{token}-ready-correction-v002",
                "--base-image", str(target), "--description", action,
                "--style", "Preserve the exact supplied editing target's coarse hand-ink and warm soft-leather material; isolate the requested existing component only.",
                "--cell-size", "512", "--chroma-key", "#00FF00", "--request", str(seed_path)]
        result = subprocess.run(argv, capture_output=True, text=True, encoding="utf-8")
        command_path = write(f"logs/prepare-{token}-ready-command-v002.json", {"argv": argv, "exit_code": result.returncode})
        log_path = write(f"logs/prepare-{token}-ready-v002.log", result.stdout + result.stderr)
        if result.returncode != 0:
            raise RuntimeError(f"Standard prepare failed ({result.returncode}): {log_path}")

        request_path = run / "sprite-request.json"
        before_path = OUT / f"standard-output-before-explicit/{token}-sprite-request.json"
        before_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(request_path, before_path)
        q = json.loads(request_path.read_text(encoding="utf-8-sig"))
        changes = {}
        for key in ("fit", "chroma", "motion_phase_guides"):
            if q.get(key) != seed[key]:
                changes[key] = {"before": q.get(key), "after": seed[key]}
                q[key] = seed[key]
        cfg = q["states"][state]
        if cfg.get("durations_ms") != DURATIONS:
            changes[f"states.{state}.durations_ms"] = {"before": cfg.get("durations_ms"), "after": DURATIONS}
            cfg["durations_ms"] = DURATIONS
        request_path.write_text(json.dumps(q, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        if q["cell"]["safe_margin_x"] != margins[0] or q["cell"]["safe_margin_y"] != margins[1]:
            raise RuntimeError("Shared fit-window margins changed")
        if cfg["frames"] != len(DURATIONS) or cfg["durations_ms"] != DURATIONS:
            raise RuntimeError("Frame timing changed")
        base_copy = run / "base-source.png"
        if descriptor(base_copy)["sha256"] != target_pin["sha256"]:
            raise RuntimeError("Editing-target byte copy changed")
        write(f"requests/{token}-explicit-request-fields-v002.json", {
            "standard_before": descriptor(before_path), "changes": changes,
            "final": descriptor(request_path),
            "reason": "Standard prepare whitelists request fields. Restore explicit project chroma, shared-row fit and four 167ms durations; preserve its real output first.",
        })

        prompt_path = run / f"prompts/{state}.txt"
        standard_prompt_copy = OUT / f"standard-output-before-explicit/{token}-standard-prompt.txt"
        shutil.copy2(prompt_path, standard_prompt_copy)
        prompt = f"""EDIT THE ONE ATTACHED IMAGE. It is the exact native{failed_number} failed raw target, not an approved component: it wrongly shows complete vests. Perform a selective image edit that removes unwanted garment parts. Do not generate a new full vest or a new character.

The numeric request declares exactly {cfg['frames']} corresponding views in one horizontal row, in the SAME left-to-right order as the attached target. Preserve those four actual perspective differences, their existing image-space placements and canvas aspect ratio ({target_size[0]} x {target_size[1]}). Remove pixels around the retained parts instead of enlarging the retained part to fill the original vest. Do not duplicate a selected cap into all slots, invent another pose, mirror a view, add a fifth piece or rearrange the row.

{correction_instructions(component)}

All unwanted foreground pixels must be replaced with flat opaque GREEN #00FF00, including the original background, interior empty openings and removed garment/body areas. Keep leather interiors opaque. No transparency, checkerboard, gradients, shadows, outline of a deleted torso, retained undercloth, labels, frames, guide marks, new ornament or detached effects. Retain the existing ink/material of the selected component; do not change it to metal, recolor it or repaint a complete vest. The visual result must be FOUR mutually separated components of ONLY this one requested type. A complete vest is a FAIL even if its shoulder is correct.

Preparation cell is {q['cell']['width']} x {q['cell']['height']}; later common extraction fit window is {window[0]} x {window[1]} design pixels, using ONE shared scale for the entire row, never per-frame normalization. This is extraction metadata, not a request to resize or move the selected source parts while editing. Durations are {cfg['durations_ms']} ms, total {sum(cfg['durations_ms'])} ms; no timing labels in the picture. Future generated attachment feature A is UNKNOWN / null in every frame and must be measured after semantic review. Do not manufacture an attachment point from a bbox center.

Return the edited row image only. No full hero or complete armor, no additional visual reference and no new scene. This is a component-correction candidate, not animation acceptance or an engine import.
"""
        if len(prompt.split()) > 800:
            raise RuntimeError("Prompt exceeds 800 words")
        prompt_path.write_text(prompt, encoding="utf-8")
        write(f"requests/{token}-prompt-replacement-v002.json", {
            "standard_prompt_preserved": descriptor(standard_prompt_copy),
            "final_prompt": descriptor(prompt_path), "word_count": len(prompt.split()),
            "derived_frame_count": cfg["frames"], "derived_durations_ms": cfg["durations_ms"],
            "reason": "Exact-target semantic correction; generic full-body generation prompt is not suitable for deletion-only component isolation.",
        })

        mounts = existing["mount_candidates"]
        for mount in mounts:
            if mount["future_generated_component_A"] is not None or mount["hidden_joint"] is not None:
                raise RuntimeError("Future attachment or joint falsely measured")
        rows.append({
            "component": component, "runtime_component": runtime_key, "state": state,
            "draft_label": f"{draft_number}-{component}",
            "suggested_native_number_if_original_order": draft_number,
            "native_request_number": None,
            "failed_raw_native_number": failed_number,
            "failed_target": target_pin,
            "target_mode": target_mode, "target_canvas_px": target_size,
            "target_semantic_verdict": "FAIL: whole vest instead of isolated component (reported by Root; not visually reviewed by this producer)",
            "run_dir": run.as_posix(), "raw_output_path": (run / f"raw/{state}.png").as_posix(),
            "request": descriptor(request_path), "prompt": descriptor(prompt_path),
            "reference_images_in_order": [{"role": "single_exact_failed_raw_edit_target_only", "file": descriptor(base_copy)}],
            "reference_count": 1, "transparent_background": False,
            "background_hex": "#00FF00", "frame_count": cfg["frames"],
            "durations_ms": cfg["durations_ms"], "fit_window_design_px": window,
            "shared_row_scale": True, "per_frame_scale_normalization": False,
            "future_component_A": [None] * cfg["frames"], "mount_candidates": mounts,
            "target_mounts_are_measured": False,
            "standard_prepare_command": argv, "standard_prepare_exit_code": result.returncode,
            "prepare_command_record": descriptor(command_path), "prepare_log": descriptor(log_path),
            "standard_layout_guide_not_attached_to_edit": True,
            "base_source_role_override": "Exact failed multi-view editing target. Mechanical prepare copy only; not a newly accepted canonical base/anchor.",
            "generation_ready": False,
        })

    handoff = write("lgt-ready-correction-input-draft-v002.json", {
        "schema": "lgt-ready-single-target-semantic-correction-input-v002",
        "created_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "source_event": "EV-048", "preparation_toolchain": descriptor(toolchain),
        "root_reported_failed_targets": [180, 181, 182],
        "parent_reported_retention_batches": ["E255", "E256", "E257"],
        "producer_visually_reviewed_targets": False, "producer_viewed_new_guides": False,
        "rows": rows, "generation_ready": False, "root_review_required_before_generation": True,
        "suggested_first_trial": "NearShoulder draft184 OR Chest draft183, only one first; no automatic three-row batch",
        "suggested_numbers_are_not_ledger_reservations": True,
        "numbering_note": "Root assigns the next real ledger number when reserving a call. Choosing Near first may change real numbering; draft labels are not evidence of a generation.",
        "input_role_exception": "Root explicitly requested one exact failed raw as the sole editing target. This mechanical prepare is a correction draft, not a base-lock or identity acceptance. Do not attach old131,179, body contact, old metal rows or the generated layout guide to the editor call.",
        "preparation_only": True, "native_called": False, "ue_or_import_called": False,
        "local_art_repair_or_component_crop_called": False,
        "no_final_asset_or_animation_pass_claimed": True, "formal_complete_units": 0,
    })
    mismatches = [path.as_posix() for path, pin in WATCHED.items() if descriptor(path, False) != pin]
    if mismatches:
        raise RuntimeError(f"Read-only source mismatch: {mismatches}")
    write("preparation-verification-v002.json", {
        "standard_prepare_runs": len(rows), "standard_prepare_exit_codes": [row["standard_prepare_exit_code"] for row in rows],
        "read_only_sources_rechecked": len(WATCHED), "source_mismatches": mismatches,
        "one_reference_per_edit": all(row["reference_count"] == 1 for row in rows),
        "durations_all_four_167ms": all(row["durations_ms"] == DURATIONS for row in rows),
        "future_A_all_null": all(row["future_component_A"] == [None] * 4 for row in rows),
        "raw_files_created": [p.as_posix() for p in OUT.glob("run-*/raw/*") if p.is_file()],
        "local_png_art_operations": "None. Standard prepare generated technical layout guides and copied exact source PNGs only.",
        "viewed_or_screenshot": False, "generation_called": False, "ue_or_import_called": False,
        "draft": descriptor(handoff),
    })
    write("HANDOFF.md", """# 软皮轻甲 Ready 单一编辑目标纠错 v002

三次标准 sprite-gen prepare 已实际执行，退出码均为 0。每组仅引用对应 180 / 181 / 182 错误原图的逐字节副本作为编辑 target，不附加 layout guide 或其余旧参考。技术 guide 保留用于记录标准 prepare，不代表造型通过。

- Chest 草案183：保留软皮胸/腰及附着小袋；删除两侧肩 cap 和灰 undercloth。
- Near 草案184：仅保留每个原背心的图像 LEFT 短皮肩 cap；删除躯干、腰袋、远肩和灰 innerhole。
- Far 草案185：仅保留每个原背心的图像 RIGHT 小 cap；删除其余内容，不镜像近肩。
- 每行 4×167ms；Chest / Near / Far 共同缩放窗口为 90×90 / 60×44 / 30×28，整行统一 scale，future A 全部 null。
- 输出要求不透明平绿 #00FF00；这是下一次原生图像编辑，不能在本地裁切整背心伪称分层成功。

`lgt-ready-correction-input-draft-v002.json` 为交接入口，各行的 `prompt.path` 都在其 run 的 `prompts/<state>.txt`，帧数及 durations 从 request 派生。标准 request / prompt 修改前副本和明确字段恢复记录保留。草案编号不是 ledger 预留，Root 先选择 Near 或 Chest 单次试验时按实际下一编号落账。

generation_ready=false。Root 完成输入检查和 E 归档后，才可浏览新 guide；未经语义检查不可导入。执行者未生成、未改 ledger / ActualSource / README / progress / 过程媒体，未浏览、截图或绘制/裁切最终图。180—182 的 FAIL 来自 Root 实际审图报告，不是执行者自行看图结论。
""")
    pins = [descriptor(path, False) for path in sorted(OUT.rglob("*")) if path.is_file()]
    for pin in pins:
        pin["path"] = Path(pin["path"]).relative_to(OUT).as_posix()
    freeze = write("preparation-freeze-v002.json", {
        "schema": "lgt-ready-correction-preparation-freeze-v002",
        "created_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "status": "PREPARED_ONLY_REQUIRES_ROOT_REVIEW_AND_RETENTION",
        "generation_ready": False, "files": pins, "file_count_excluding_this_manifest": len(pins),
        "total_bytes_excluding_this_manifest": sum(pin["bytes"] for pin in pins),
        "generation_called": False, "ue_called": False, "viewed": False,
    })
    print(json.dumps({"draft": descriptor(handoff), "freeze": descriptor(freeze),
                      "prepare_exit_codes": [row["standard_prepare_exit_code"] for row in rows],
                      "frozen_files": len(pins), "frozen_bytes": sum(pin["bytes"] for pin in pins),
                      "source_rechecks": len(WATCHED), "source_mismatches": [],
                      "generation_ready": False, "viewed": False}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
