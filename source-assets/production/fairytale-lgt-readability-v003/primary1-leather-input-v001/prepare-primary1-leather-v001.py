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
OLD = PROJECT / "source-assets/production/fairytale-armor-sword-primary1-v001"
SG = Path("C:/Users/22499/.codex/skills/sprite-gen")
PYTHON = SG / ".venv/Scripts/python.exe"
TIMES = [85, 85, 60, 60, 155, 155]
REGISTRATION = OLD / "macro-registration-primary1-v001/feature-measurement-registration-v001.json"
IMPORT = OLD / "macro-registration-primary1-v001/candidate-import-v001.json"
WATCHED = {}
COMPONENTS = [
    {"component": "Chest", "token": "chest", "runtime": "Chest", "old_version": "v001", "old_state": "armor_chest_sword_primary1", "old_native": 164,
     "ready_native": 184, "ready_png": FAMILY / "chest184-extraction-v001/run-shared-diagnostic-v001/frames/leather_chest_sword_ready/frame-0.png",
     "ready_sha": "9c1f63e4f710223c567a9e1fd9795490513aa88ee2ee4cd05425833a33af1312", "window": [90, 90], "min_used": 512, "planned": 188},
    {"component": "NearShoulder", "token": "nearshoulder", "runtime": "ShoulderNear", "old_version": "v001", "old_state": "armor_shoulder_near_sword_primary1", "old_native": 165,
     "ready_native": 186, "ready_png": FAMILY / "near186-extraction-v001/run-shared-diagnostic-v001/frames/leather_nearshoulder_sword_ready/frame-0.png",
     "ready_sha": "0aa081a7d3ae814827c654c545b86dcc3a0e4bc0f5b32e04c0541509a1d0bd8c", "window": [60, 44], "min_used": 512, "planned": 189},
    {"component": "FarShoulder", "token": "farshoulder", "runtime": "ShoulderFar", "old_version": "v003", "old_state": "armor_shoulder_far_sword_primary1", "old_native": 167,
     "ready_native": 187, "ready_png": FAMILY / "far187-extraction-v001/run-shared-smallcomponent-v002/frames/leather_farshoulder_sword_ready/frame-0.png",
     "ready_sha": "032e2bf4e4e2537191531ace4c90076aed3d899ac931db9be3c3b99aaaf267f0", "window": [32, 30], "min_used": 256, "planned": 190},
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


def component_instruction(component):
    if component == "Chest":
        return "Retain ONLY a waist-length supple brown leather chest/waist jerkin, its round golden front clasp, belt and one small ATTACHED pouch, as in the Ready184 appearance anchor. Extend the garment to its leather waist construction instead of keeping the old tiny hard chest plate. Remove old grey metal, raised metal boss and ALL shoulder caps. Never include grey undercloth, sleeve, torso/body or a detached pouch. The six jerkin views follow the old row's different torso turns, not six copies of the Ready pose."
    if component == "NearShoulder":
        return "Retain ONLY a SHORT rounded foreground/near brown leather shoulder cap matching Ready186. Keep the six distinct near-cap turns and foreshortenings of the old action row, but discard its metal plate/boss identity. No torso, chest, waist, pouch, second/far cap, grey sleeve/inner lining, dangling oval ring, arm, hand or finger. Do not turn any cap into a complete vest."
    return "Retain ONLY a TINY NARROW curved far-side brown leather tab matching Ready187's compressed silhouette and material. Use the six old far-row views only for action timing/orientation; discard the broad metal pauldron silhouette. NEVER substitute a broad near/front shoulder or mirror the near cap. No chest, collar, adjoining torso seam, pouch, grey lining, arm/hand or long hanging oval ring. Preserve six distinct compressed FAR perspectives, not six cloned Ready tabs."


def main():
    if Path(sys.executable).resolve() != PYTHON.resolve():
        raise RuntimeError("Use sprite-gen venv")
    if OUT != FAMILY / "primary1-leather-input-v001" or list(OUT.glob("run-*")):
        raise RuntimeError("Unexpected or existing output")
    registration = json.loads(REGISTRATION.read_text(encoding="utf-8"))
    imported = json.loads(IMPORT.read_text(encoding="utf-8"))
    pin(REGISTRATION)
    pin(IMPORT)
    old_provenance = []
    rows = []
    for component in COMPONENTS:
        name, token = component["component"], component["token"]
        old_run = OLD / f"run-{token}-primary1-{component['old_version']}"
        old_request_path = old_run / "sprite-request.json"
        old_request = json.loads(old_request_path.read_text(encoding="utf-8"))
        old_state = component["old_state"]
        if old_request["states"][old_state]["frames"] != 6 or old_request["states"][old_state]["durations_ms"] != TIMES:
            raise RuntimeError("Old real Primary1 recipe differs")
        old_raw = old_run / f"raw/{old_state}.png"
        old_frames_manifest_path = old_run / "frames/frames-manifest.json"
        old_manifest = json.loads(old_frames_manifest_path.read_text(encoding="utf-8"))
        shared = old_manifest["rows"][0]["shared_row_fit"]
        if shared["policy"] != "one_raw_component_max_extent_scale_for_entire_row" or shared["per_frame_scale_normalization"] is not False:
            raise RuntimeError("Old actual extraction was not shared-row fit")
        with Image.open(old_raw) as image:
            raw_size, raw_mode = list(image.size), image.mode
        anchor = component["ready_png"]
        if pin(anchor)["sha256"] != component["ready_sha"]:
            raise RuntimeError("New Ready appearance identity pin differs")
        with Image.open(anchor) as image:
            if image.mode != "RGBA" or image.size != (512, 512):
                raise RuntimeError("Ready appearance anchor must be actual transparent 512 RGBA")
        old_sources = []
        for frame in range(6):
            feature = next(row for row in registration["feature_rows"] if row["component"] == name and row["frame"] == frame)
            existing = next(row for row in imported["textures"] if row["component"] == component["runtime"] and row["frame"] == frame)
            checked(feature["source"])
            checked(feature["registered_source"])
            if checked(existing["source"]).read_bytes() != Path(feature["registered_source"]["path"]).read_bytes():
                raise RuntimeError("Old registered/import candidate source differs")
            old_sources.append({"frame": frame, "old_curated_source": feature["source"], "old_integer_registered_source": feature["registered_source"],
                                "old_integer_translation_xy_history_only": feature["integer_translation_xy"],
                                "old_frame_common_scale": feature["raw_component_provenance"]["common_row_scale"],
                                "old_feature_or_body_target_reused_for_new_leather": False})
        old_provenance.append({"component": name, "old_native_request": component["old_native"], "old_run": old_run.as_posix(),
                               "raw": pin(old_raw), "raw_canvas_px": raw_size, "raw_mode": raw_mode,
                               "request": pin(old_request_path), "frames_manifest": pin(old_frames_manifest_path),
                               "shared_row_fit": shared, "existing_registered_sources": old_sources,
                               "authority": "Six-phase motion/perspective/relative geometry basis ONLY, never old grey-metal item identity or new A/B"})

        state = f"leather_{token}_sword_primary1"
        window = component["window"]
        margins = [(512 - size) // 2 for size in window]
        action = f"Edit six existing {name} Primary1 component views into the same new brown soft-leather {name} as the attached actual Ready{component['ready_native']} anchor; preserve phase order and perspective, no whole character."
        seed = {"version": 1, "kind": "sprite-gen-request", "engine": "component-row",
                "states": {state: {"frames": 6, "fps": 10, "loop": False, "action": action, "durations_ms": TIMES}},
                "cell": {"width": 512, "height": 512, "safe_margin_x": margins[0], "safe_margin_y": margins[1]},
                "motion_phase_guides": False,
                "fit": {"pixel_unfake": False, "resample": "lanczos", "align_x": "bbox-center", "align_y": "bottom",
                        "ground_frames": False, "segmentation": "components", "shared_row_scale": True},
                "chroma": {"mode": "rgb", "unmix_reach": 4, "spill_max_fraction": 0.005}}
        seed_path = write(f"requests/{token}-numeric-input-v001.json", seed)
        run = OUT / f"run-{token}-primary1-v001"
        argv = [str(PYTHON), "-B", "-X", "utf8", str(SG / "scripts/prepare_sprite_run.py"), "--out-dir", str(run),
                "--character-id", f"fairytale-soft-leather-{token}-primary1-v001", "--base-image", str(anchor),
                "--description", action, "--style", f"Use the actual isolated Ready{component['ready_native']} component as sole soft-leather appearance identity. Old action row is motion basis only.",
                "--cell-size", "512", "--chroma-key", "#00FF00", "--request", str(seed_path)]
        result = subprocess.run(argv, capture_output=True, text=True, encoding="utf-8")
        log = write(f"logs/prepare-{token}-v001.log", result.stdout + result.stderr)
        write(f"logs/prepare-{token}-command-v001.json", {"argv": argv, "exit_code": result.returncode, "log": pin(log)})
        if result.returncode != 0:
            raise RuntimeError(f"Standard prepare failed: {log}")
        request = run / "sprite-request.json"
        before = copy_exact(request, f"standard-output-before-explicit/{token}-sprite-request.json")
        q = json.loads(request.read_text(encoding="utf-8"))
        changes = {}
        for key in ("fit", "chroma", "motion_phase_guides"):
            if q.get(key) != seed[key]:
                changes[key] = {"before": q.get(key), "after": seed[key]}
                q[key] = seed[key]
        if q["states"][state].get("durations_ms") != TIMES:
            changes[f"states.{state}.durations_ms"] = {"before": q["states"][state].get("durations_ms"), "after": TIMES}
            q["states"][state]["durations_ms"] = TIMES
        request.write_text(json.dumps(q, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        write(f"requests/{token}-explicit-fields-v001.json", {"standard_before": pin(before), "changes": changes, "final": pin(request)})
        if q["states"][state]["frames"] != 6 or q["states"][state]["durations_ms"] != TIMES:
            raise RuntimeError("Six-phase timing not preserved")
        target_copy = copy_exact(old_raw, f"run-{token}-primary1-v001/references/edit-target-old-primary1.png")
        appearance_copy = run / "base-source.png"
        if pin(appearance_copy)["sha256"] != component["ready_sha"]:
            raise RuntimeError("Standard prepare appearance copy changed")
        prompt = run / f"prompts/{state}.txt"
        copy_exact(prompt, f"standard-output-before-explicit/{token}-standard-prompt.txt")
        text = f"""EDIT THE FIRST IMAGE ONLY: the old {name} Primary1 row ({raw_size[0]} x {raw_size[1]}). The SECOND image is the actual isolated Ready{component['ready_native']} component, the SOLE appearance/material identity. The first image supplies ONLY six action perspectives, motion order and geometry; discard its grey metal, boss and obsolete ornament. Do not reattach a full-character base.

{component_instruction(name)}

Keep exactly {q['states'][state]['frames']} distinct separated components in the original left-to-right phase order: windup0/1, strike2/3, recovery4/5. Preserve each old action view's orientation/foreshortening and row spacing, while carrying the new Ready component construction consistently through the action. Do not clone the idle reference six times or deform one pasted cap. Keep coarse ink and warm brown/tan leather planes, not grey plate.

Replace all unwanted pixels with flat opaque GREEN #00FF00. No whole person, helmet, head, eyes, body, arms, hands, weapon, ground, shadows, grey undercloth, second armor component, text or boxes. Output only this component row, opaque on green.

Timing metadata {q['states'][state]['durations_ms']} ms. Later use one common {window[0]} x {window[1]} fit window in512 cells for the whole six-frame row, never normalize each pose. New generated A, matching body B and integer delta are UNKNOWN/null in all six phases; no bbox-centre attachment guesses. No fit/motion/runtime acceptance is implied.
"""
        if len(text.split()) >= 350:
            raise RuntimeError("Component edit prompt is too long")
        prompt.write_text(text, encoding="utf-8")
        qa = write(f"requests/{token}-extraction-configuration-proposal-v001.json", {
            "proposed_component_min_used_pixels": component["min_used"], "applies_only_when_Root_runs_future_extraction": True,
            "not_yet_executed_or_passed": True, "subject_relabelled_effect": False,
            "reason": "Explicit small rigid far-tab floor256, consistent with actual Ready187 narrow-part diagnostics; other chroma/edge/count gates stay unchanged." if name == "FarShoulder" else "Retain standard512 whole-cell sparse floor until real component extraction is reviewed.",
            "future_cli": ["--min-used-pixels", str(component["min_used"])],
            "shared_fit_window_design_px": window, "one_scale_entire_six_frame_row": True, "per_frame_scale_normalization": False,
            "new_raw_scale_measured": None, "window_is_an_accepted_fit": False,
        })
        rows.append({"component": name, "runtime_component": component["runtime"], "state": state, "clip": "sword_primary_1",
                     "run_dir": run.as_posix(), "raw_output_path": (run / f"raw/{state}.png").as_posix(),
                     "prompt": pin(prompt), "request": pin(request), "prompt_word_count": len(text.split()),
                     "reference_images_in_order": [{"role": "FIRST_exact_old_same_component_primary1_edit_target_motion_geometry_only", "file": pin(target_copy)},
                                                   {"role": "SECOND_actual_new_same_component_Ready_appearance_anchor_ONLY", "file": pin(appearance_copy)}],
                     "reference_count": 2, "frame_count": 6, "durations_ms": TIMES, "fit_window_design_px": window,
                     "shared_row_scale": True, "extraction_configuration_proposal": pin(qa),
                     "old_primary1_native_request": component["old_native"], "new_Ready_appearance_native_request": component["ready_native"],
                     "future_component_A": [None] * 6, "future_body_target_B": [None] * 6, "future_integer_delta": [None] * 6,
                     "target_mounts_are_measured": False, "native_request_number": None, "planned_native_number_if_original_order": component["planned"],
                     "standard_prepare_command": argv, "standard_prepare_exit_code": result.returncode,
                     "transparent_background": False, "background_hex": "#00FF00", "generation_ready": False,
                     "root_edit_target_and_anchor_view_required_before_generation": True,
                     "standard_layout_guide_not_attached_to_editor": True})
    provenance = write("old-primary1-source-and-registration-provenance-v001.json", {
        "schema": "old-primary1-components-for-new-leather-motion-basis-only-v001", "rows": old_provenance,
        "registration_authority": pin(REGISTRATION), "old_candidate_import": pin(IMPORT),
        "old_primary1_static_stack_without_weapon": registration["static_stack_without_weapon"],
        "old_hidden_body_target_trial": registration["hidden_target_trial_design"],
        "new_body_or_helmet_ownership_created": False, "old_A_B_or_integer_delta_reused_as_new": False})
    toolchain = write("toolchain-v001.json", {"python_executable": sys.executable, "python_version": platform.python_version(),
        "pillow_version": PIL.__version__, "numpy_version": np.__version__,
        "tools": [pin(SG / "scripts/prepare_sprite_run.py"), pin(SG / "sprite_gen/gen/prepare.py"), pin(SG / "SKILL.md")],
        "installed_tools_modified": False})
    handoff = write("primary1-leather-native-input-draft-v001.json", {
        "schema": "primary1-leather-three-component-six-phase-native-input-draft-v001", "created_local": datetime.datetime.now().astimezone().isoformat(),
        "source_event": "EV-048", "rows": rows, "generation_ready": False, "root_review_required_before_generation": True,
        "original179_or131_full_body_attached": False, "only_component_Ready_anchors_as_appearance_identity": True,
        "old_source_provenance": pin(provenance), "toolchain": pin(toolchain),
        "native_called": False, "UE_or_import_called": False, "new_guides_or_media_viewed": False,
        "new_A_B_delta_all_null": True, "planned_188_190_are_not_ledger_reservations": True,
        "helper_compatibility": "Row fields match native-fairytale-leather-ready-v002.py, but Root MUST version its helper to v003 and replace the stale Ready4/native179 scope with Primary1 six-phase edit scope before generation. No helper/ledger changes made here.",
        "scope": "Three component-only Primary1 six-phase input preparations. Root first retains and views exact edit targets/Ready anchors; future generation, extraction, A/B measurement, fit, occlusion, motion and actual native integration remain pending.",
        "formal_complete_units": 0})
    mismatches = [path.as_posix() for path, original in WATCHED.items() if pin(path, False) != original]
    if mismatches:
        raise RuntimeError(f"Read-only source changed: {mismatches}")
    write("preparation-verification-v001.json", {"standard_prepare_runs": 3, "standard_prepare_exit_codes": [row["standard_prepare_exit_code"] for row in rows],
        "read_only_source_rechecks": len(WATCHED), "source_mismatches": [], "new_raw_files": [path.as_posix() for path in OUT.glob("run-*/raw/*") if path.is_file()],
        "new_guides_viewed": False, "generated": False, "all_future_A_B_delta_null": True, "handoff": pin(handoff)})
    write("HANDOFF.md", """# Primary1软皮三组件六相输入 v001

三次标准prepare已实际执行。每行仅2引用：旧同组件Primary1 raw为第一编辑target（动作/几何），新Ready184/186/187的同组件frame0为第二appearance identity。没有重新附179/131整人、没有body接管或新guides引用。Root先E282留档并实际看这些目标/anchor，再保留approved。

六相timing保持85/85/60/60/155/155ms（总600ms）。建议窗口Chest90×90（替代旧70×50小金属胸板）、Near60×44、Far32×30（已有Primary1窗口），整行共scale；原灰甲已登记source/整数delta及实际shared scale仅作历史索引，新A/B/delta18帧均null，不能借旧扣件或bboxcentre。显式后续min建议Chest512/Near512/Far256，Far为窄刚性附件，不标effect，不改其它QA。尚未提取所以无新实测scale/通过结论。

`primary1-leather-native-input-draft-v001.json` rows兼容Root helper字段，但helper旧scope写Ready4/native179，必须Root版本化v003后改成Primary1六相。计划188—190未ledger预留。generator_ready=false，标准layout guide新输出未查看；没有生成、工具/Source/UE/ledger/README/媒体目录改动。

旧Primary1有HelmetForeground单独层及隐藏body-target试装设计，不能直接复用Ready三body层当Primary1适配证明。后续仍要新组件实际A/B、整数登记、全stack遮挡与真实六相原生验证。本批仅输入准备，不扩展QA系统。
""")
    files = [pin(path, False) for path in sorted(OUT.rglob("*")) if path.is_file()]
    for item in files:
        item["path"] = Path(item["path"]).relative_to(OUT).as_posix()
    freeze = write("input-freeze-v001.json", {"schema": "primary1-leather-input-freeze-v001", "files": files,
        "file_count_excluding_manifest": len(files), "total_bytes_excluding_manifest": sum(item["bytes"] for item in files),
        "generation_ready": False, "generated": False, "viewed": False})
    print(json.dumps({"handoff": pin(handoff), "freeze": pin(freeze), "prepare_exit_codes": [row["standard_prepare_exit_code"] for row in rows],
        "prompt_words": [row["prompt_word_count"] for row in rows], "frozen_files": len(files), "frozen_bytes": sum(item["bytes"] for item in files),
        "source_rechecks": len(WATCHED), "source_mismatches": [], "generation_ready": False}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
