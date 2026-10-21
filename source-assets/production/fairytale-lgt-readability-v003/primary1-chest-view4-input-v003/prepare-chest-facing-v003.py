"""Prepare native192 complete six-phase Chest facing redraw; no generation."""
from pathlib import Path
import datetime
import hashlib
import json
import shutil
import subprocess
import sys


OUT = Path(__file__).resolve().parent
FAMILY = Path("F:/Ourgame/source-assets/production/fairytale-lgt-readability-v003")
SG = Path("C:/Users/22499/.codex/skills/sprite-gen")
PYTHON = SG / ".venv/Scripts/python.exe"
STATE = "leather_chest_sword_primary1"
OLD_RUN = FAMILY / "primary1-leather-input-v001/run-chest-primary1-v001"
TARGET = OLD_RUN / f"raw/{STATE}.png"
ANCHOR = FAMILY / "chest184-extraction-v001/run-shared-diagnostic-v001/frames/leather_chest_sword_ready/frame-0.png"
TIMES = [85, 85, 60, 60, 155, 155]


def pin(path):
    data = path.read_bytes()
    return {"path": path.as_posix(), "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}


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
        raise RuntimeError("Existing copy")
    shutil.copy2(source, path)
    if source.read_bytes() != path.read_bytes():
        raise RuntimeError("Source copy changed")
    return path


def main():
    if Path(sys.executable).resolve() != PYTHON.resolve() or OUT != FAMILY / "primary1-chest-view4-input-v003":
        raise RuntimeError("Wrong interpreter/ownership")
    if list(OUT.glob("run-*")):
        raise RuntimeError("Preserve prior versions")
    target_pin, anchor_pin = pin(TARGET), pin(ANCHOR)
    if target_pin["sha256"] != "7b07f7c624e7c9bd930fbecb6db7e77051a9f9447f9af59686388e710ed5f46f":
        raise RuntimeError("Actual188 edit target changed")
    if anchor_pin["sha256"] != "9c1f63e4f710223c567a9e1fd9795490513aa88ee2ee4cd05425833a33af1312":
        raise RuntimeError("Ready184 appearance anchor changed")
    old_request = OLD_RUN / "sprite-request.json"
    old_request_pin = pin(old_request)
    old = json.loads(old_request.read_text(encoding="utf-8"))
    if old["states"][STATE]["durations_ms"] != TIMES or old["states"][STATE]["frames"] != 6:
        raise RuntimeError("Actual six-phase recipe changed")
    action = "Redraw all six actual188 Chest action views with one consistent right-facing construction: large armhole IMAGE-LEFT, pouch IMAGE-LEFT, front gold clasp IMAGE-RIGHT. Phase4 keeps recovery lean without torso rotation or mirroring."
    seed = {"version": 1, "kind": "sprite-gen-request", "engine": "component-row", "cell": old["cell"],
            "states": {STATE: {"frames": 6, "fps": 10, "loop": False, "action": action, "durations_ms": TIMES}},
            "motion_phase_guides": False, "fit": old["fit"], "chroma": old["chroma"]}
    if [seed["cell"]["width"] - 2 * seed["cell"]["safe_margin_x"], seed["cell"]["height"] - 2 * seed["cell"]["safe_margin_y"]] != [90, 90]:
        raise RuntimeError("Chest90x90 fit window changed")
    request_input = write("requests/chest-view4-numeric-input-v003.json", seed)
    run = OUT / "run-chest-primary1-facing-v003"
    argv = [str(PYTHON), "-B", "-X", "utf8", str(SG / "scripts/prepare_sprite_run.py"), "--out-dir", str(run),
            "--character-id", "fairytale-leather-chest-primary1-facing-v003", "--base-image", str(ANCHOR),
            "--description", action, "--style", "Actual Ready184 brown leather jerkin appearance; six same-right-facing action views, never a torso mirror or complete character.",
            "--cell-size", "512", "--chroma-key", "#00FF00", "--request", str(request_input)]
    result = subprocess.run(argv, capture_output=True, text=True, encoding="utf-8")
    log = write("logs/prepare-chest-view4-v003.log", result.stdout + result.stderr)
    write("logs/prepare-chest-view4-command-v003.json", {"argv": argv, "actual_exit_code": result.returncode, "log": pin(log)})
    if result.returncode != 0:
        raise RuntimeError("Standard prepare failed")
    request = run / "sprite-request.json"
    before = copy_exact(request, "standard-output-before-explicit/sprite-request.json")
    q = json.loads(request.read_text(encoding="utf-8"))
    changes = {}
    for key in ("fit", "chroma", "motion_phase_guides"):
        if q.get(key) != seed[key]:
            changes[key] = {"before": q.get(key), "after": seed[key]}
            q[key] = seed[key]
    if q["states"][STATE].get("durations_ms") != TIMES:
        changes["durations_ms"] = {"before": q["states"][STATE].get("durations_ms"), "after": TIMES}
        q["states"][STATE]["durations_ms"] = TIMES
    request.write_text(json.dumps(q, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write("requests/explicit-fields-v003.json", {"before": pin(before), "changes": changes, "final": pin(request),
          "extraction_min_used_pixels_proposed": 512, "extraction_not_executed": True, "no_effect_relabel": True})
    prompt = run / f"prompts/{STATE}.txt"
    copy_exact(prompt, "standard-output-before-explicit/standard-prompt.txt")
    text = """REDRAW ALL SIX Chest components in the FIRST image, using its windup0/1, strike2/3 and recovery4/5 motion order and lean changes. The SECOND image is the SOLE Ready184 leather-jerkin appearance reference, not another output pose.

Every component must use the SAME RIGHT-FACING torso construction: LARGE ARMHOLE on IMAGE-LEFT, attached POUCH on IMAGE-LEFT, round GOLD FRONT CLASP just IMAGE-RIGHT of centre. Keep those physical sides through ALL SIX poses. In the FIFTH component(index4), keep only the recovery lean; do NOT rotate the torso to a rear/left-facing view. Redraw the perspective rather than horizontally flipping a frame or copying another pose.

All six may be redrawn; exact preservation of the previous five is neither required nor promised. Keep six distinct separated poses, their left-to-right order, canvas2172x724 and clear gaps. Use warm brown supple leather, the consistent belt/pouch/clasp and coarse ink. Opaque GREEN #00FF00 background. No shoulders, grey lining, whole person, head/helmet, arms/hands, weapon, ground, text or boxes. Return only the six-component row.
"""
    words = len(text.split())
    if not 130 <= words <= 180:
        raise RuntimeError(f"Expected short130-180word prompt, got{words}")
    prompt.write_text(text, encoding="utf-8")
    target_copy = copy_exact(TARGET, "run-chest-primary1-facing-v003/references/actual188-edit-target.png")
    appearance = run / "base-source.png"
    if pin(appearance)["sha256"] != anchor_pin["sha256"]:
        raise RuntimeError("Appearance reference copy changed")
    draft = write("chest-view4-native-input-draft-v003.json", {
        "schema": "primary1-chest-six-phase-same-facing-redraw-input-v003", "created_local": datetime.datetime.now().astimezone().isoformat(),
        "source_event": "EV-048", "rows": [{"component": "Chest", "runtime_component": "Chest", "state": STATE, "clip": "sword_primary_1",
            "run_dir": run.as_posix(), "raw_output_path": (run / f"raw/{STATE}.png").as_posix(), "prompt": pin(prompt), "prompt_word_count": words,
            "request": pin(request), "reference_images_in_order": [
                {"role": "FIRST_actual188_six_action_motion_basis_all_six_may_redraw", "file": pin(target_copy)},
                {"role": "SECOND_actualReady184_Chest_appearance_only", "file": pin(appearance)}],
            "reference_count": 2, "frame_count": 6, "durations_ms": TIMES, "fit_window_design_px": [90, 90],
            "shared_row_scale": True, "future_extraction_min_used_pixels": 512,
            "future_component_A": [None] * 6, "future_body_target_B": [None] * 6, "future_integer_delta": [None] * 6,
            "target_mounts_are_measured": False, "standard_prepare_exit_code": result.returncode, "standard_prepare_command": argv,
            "transparent_background": False, "background_hex": "#00FF00", "generation_ready": False,
            "planned_native_number_if_next": 192, "native_request_number": None,
            "root_edit_target_and_anchor_view_required_before_generation": True}],
        "generation_ready": False, "root_review_required_before_generation": True, "planned192_is_not_ledger_reservation": True,
        "root_review_basis": "Root viewed Body159 and components after E289, then retained and viewed native191 at E292.191 still has reversed phase4(large armholeRIGHT, pouchRIGHT, claspLEFT), so191 is rejected without extraction.192 must redraw the six-phase row from188 motion plus Ready184 appearance, all same right-facing torso; no guarantee or requirement of preserving exact other-five pixels.",
        "old_fullBody_or179_reference_attached": False, "standard_guide_not_attached": True,
        "all_six_must_be_remeasured_after_generation": True, "exact_preserve_other_five_promised": False,
        "generator_called": False, "UE_or_import_called": False, "new_guide_or_media_viewed": False,
        "fit_or_full_animation_accepted": False, "formal_complete_units": 0})
    if pin(TARGET) != target_pin or pin(ANCHOR) != anchor_pin or pin(old_request) != old_request_pin:
        raise RuntimeError("Read-only source changed")
    write("HANDOFF.md", "# Chest六相统一朝向重画输入 v003\n\n一次标准prepare实际exit0；2refs仅真实188整行motion＋Ready184Chest appearance。191经Root在E292实际审图判反向失败，不提取。新prompt允许全部6帧原生重画，统一armholeLEFT/pouchLEFT/goldclaspRIGHT；第五相只保留recovery lean，不转身/镜像/复制替帧。无法保证原生编辑逐像素保住其它五帧，因此不再要求preserve-five，输出6帧均重新实看和测A/B。\n\n6相timing85/85/60/60/155/155，90×90 shared-HD、future min512，新A/B/delta全null。generation_ready=false；计划192仅草案，Root授权生成及ledger自管。未生成、reserve、提取、查看新guide或修改旧冻结。\n\n备选边界：可独立生成/提取一个phase4组件，但本安装版HD非pixel-unfake行不支持takes合并，且当前内置编辑接口无像素mask或锁五槽参数，尚无已验证的无损单槽替换路径。不能据此承诺精确保留五槽，更不能本地flip/复制其它pose凑图。若整行再次失败，需另立单pose标准run并显式记录runtime phase4来源映射/新测量，先验证该路径；本批不执行、不把它称可靠现成方案。\n")
    files = [pin(path) for path in sorted(OUT.rglob("*")) if path.is_file()]
    for item in files:
        item["path"] = Path(item["path"]).relative_to(OUT).as_posix()
    freeze = write("input-freeze-v003.json", {"schema": "chest-primary1-view4-input-freeze-v003", "files": files,
        "file_count_excluding_manifest": len(files), "total_bytes_excluding_manifest": sum(item["bytes"] for item in files),
        "generation_ready": False, "generated": False, "viewed": False})
    print(json.dumps({"draft": pin(draft), "freeze": pin(freeze), "raw_output_path": (run / f"raw/{STATE}.png").as_posix(),
        "prepare_exit_code": result.returncode, "prompt_words": words, "frozen_files": len(files),
        "frozen_bytes": sum(item["bytes"] for item in files), "generation_ready": False}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
