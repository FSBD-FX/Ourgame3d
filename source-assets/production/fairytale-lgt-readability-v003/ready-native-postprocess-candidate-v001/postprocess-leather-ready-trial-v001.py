"""Verify one actual Ready-only native capture and derive review copies.

Run only after capture/flush. No UE launch, source mutation or art acceptance.
"""
from pathlib import Path
import argparse
import hashlib
import json
import math
import os
import subprocess
import zlib

import imageio_ffmpeg
import numpy as np
from PIL import Image


ROOT = Path("F:/Ourgame").resolve()
NEW = "/Game/Production/ArtTrials/EV048/v012/HeroLeatherReady/"
OLD = "/Game/Production/ArtTrials/EV048/v006/HeroSwordArmorReady/"
BODY = "/Game/Production/ArtTrials/EV048/v005/HeroSwordBody/"
SWORD = "/Game/Production/FirstBatch/v002/CandidateComponents/T_military_sword_v002.T_military_sword_v002"
CANVAS = 72.0 * 512.0 / 416.0
PHASES = ["start", "baseline_no_armor", "light_pending_cancel", "light_canceled", "light_pickup_commit", "light_ready"]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def desc(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return {"path": path.as_posix(), "bytes": path.stat().st_size, "sha256": digest.hexdigest()}


def new(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False, indent=2) + "\n"
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(payload)


def same_pin(path, pin):
    actual = desc(path)
    require(actual["bytes"] == pin["bytes"] and actual["sha256"] == pin["sha256"], f"SHA/size mismatch: {path}")


def finite(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def object_path(namespace, name):
    return namespace + name + "." + name


def package_file(object_name):
    require(object_name.startswith("/Game/") and "." in object_name, "Invalid texture object path")
    package, name = object_name.rsplit(".", 1)
    require(package.rsplit("/", 1)[-1] == name, "Object/package name differs")
    return "UnrealGame/Content/" + package[len("/Game/"):] + ".uasset"


def expected_stack(frame):
    def old(component):
        return object_path(OLD, f"T_Fairytale_SwordReady{component}_{frame:03d}_v001")
    def armor(component):
        return object_path(NEW, f"T_Fairytale_LeatherReady{component}_{frame:03d}_v001")
    return [old("BodyRest"), armor("ShoulderFar"), armor("Chest"), old("NearArmWithoutHand"), armor("ShoulderNear"), SWORD, old("NearHand")]


def verify_sources(snapshot, index):
    manifest_path = snapshot / "compiled-source-manifest.json"
    manifest = read(manifest_path)
    require(index["source_manifest_SHA256"] == desc(manifest_path)["sha256"], "Capture/snapshot manifest hash differs")
    require((ROOT / index["snapshot"]).resolve() == snapshot, "Capture names another snapshot")
    rows = manifest["files"]
    by_path = {row["path"]: row for row in rows}
    require(len(by_path) == len(rows) > 0, "Duplicate or empty snapshot paths")
    for row in rows:
        relative = Path(row["path"])
        require(not relative.is_absolute() and ".." not in relative.parts, "Unsafe snapshot-relative path")
        for base in (ROOT, snapshot):
            path = (base / relative).resolve()
            require(path.is_relative_to(base), "Snapshot path escapes its root")
            same_pin(path, row)
    production = {key: value for key, value in by_path.items() if key.startswith("UnrealGame/Content/Production/")}
    require(production and manifest["production_packages"] == len(production), "Dynamic Production count differs from frozen file list")
    require(manifest.get("mismatches") == 0 and manifest.get("old_production_unchanged") is True, "Snapshot input audit is not clean")
    if manifest.get("base_snapshot"):
        base = Path(manifest["base_snapshot"]).resolve()
        require(base.is_relative_to(ROOT / "source-assets/production/backups"), "Base snapshot outside project backups")
        before = read(base / "compiled-source-manifest.json")
        old = {row["path"]: row for row in before["files"] if row["path"].startswith("UnrealGame/Content/Production/")}
        require(all(production.get(key) == value for key, value in old.items()), "Existing Production package bytes changed")
        require(manifest["old_production_packages"] == len(old), "Dynamic old Production count differs")
        require(manifest["new_production_packages"] == len(production) - len(old), "Dynamic new Production count differs")
    automation = read(ROOT / manifest["current_automation_report"])
    count = manifest["current_automation_succeeded"]
    require(isinstance(count, int) and count > 0 and automation["succeeded"] == count, "Current automation count differs")
    tests = automation["tests"]
    require(len(tests) == count and len({item["fullTestPath"] for item in tests}) == count, "Automation tests are not unique/current")
    require(all(automation.get(key, 0) == 0 for key in ("failed", "succeededWithWarnings", "notRun", "inProcess")), "Automation has failures or incomplete tests")
    require(all(item["state"] == "Success" and item["errors"] == item["warnings"] == 0 for item in tests), "Automation entries are not all clean Success")
    receipt_pin = manifest["new_production_import_receipt"]
    receipt_path = ROOT / receipt_pin["path"]
    require(receipt_pin["path"] in by_path, "Import receipt is not compiled-snapshot input")
    same_pin(receipt_path, receipt_pin)
    imported = read(receipt_path)
    require(imported["namespace"] == NEW.rstrip("/") and imported["actual_count"] == imported["saved_count"] == imported["expected_count"] == 12, "Actual Ready import is not twelve textures")
    assets = imported["assets"]
    expected = {(component, frame) for component in ("Chest", "ShoulderNear", "ShoulderFar") for frame in range(4)}
    require(len(assets) == 12 and {(row["component"], row["frame"]) for row in assets} == expected, "Actual import component/frame set differs")
    for asset in assets:
        require(asset["actual_object_type"] == "Texture2D", "Actual imported object is not Texture2D")
        source = Path(asset["source"]).resolve()
        require(source.is_relative_to(ROOT / "source-assets/production"), "Import source outside production candidates")
        same_pin(source, {"bytes": asset["source_bytes"], "sha256": asset["source_sha256"]})
        package = package_file(asset["object_path"])
        require(package in by_path, "Imported texture is missing from the compiled snapshot")
        require(by_path[package]["bytes"] == asset["saved_bytes"] and by_path[package]["sha256"] == asset["saved_sha256"], "Imported texture bytes differ from native receipt")
    assembly = ROOT / "source-assets/production/fairytale-lgt-readability-v003/ready-integer-assembly-v001"
    assembly_freeze = assembly / "assembly-freeze-v001.json"
    require(assembly_freeze.relative_to(ROOT).as_posix() in by_path, "Assembly source freeze is not snapshot input")
    assembly_manifest = read(assembly_freeze)
    for item in assembly_manifest["files"]:
        require(".." not in Path(item["path"]).parts, "Unsafe assembly source path")
        same_pin(assembly / item["path"], item)
    return manifest, by_path, {"snapshot": snapshot.as_posix(), "snapshot_files": len(rows), "source_endpoint_checks": 2 * len(rows),
        "source_mismatches": 0, "production_packages": len(production), "current_full_automation_succeeded": count,
        "actual_new_ready_textures": len(assets), "assembly_source_checks": len(assembly_manifest["files"]),
        "source_and_DLL_unchanged": True, "body_source_repainting_asserted": False}


def verify_flow(report, index, package_rows):
    require(report["schema"] == "fairytale-equipment-bound-native-flow-v1" and report["leather_ready_only_trial"] is True, "This script accepts only the explicit leather Ready-only trial")
    require(report["passed"] is True and report["flow_complete"] is True and report["reason"] == report["failure"] == "" and report["mismatches"] == [], "Native Ready trial did not pass cleanly")
    require(index["runtime_passed"] is True and index["exit_code"] == 0, "Native process/index failed")
    require(report["silent_video"] is True and report["audio_recorded"] is False and report["native_async_capture_writes_flushed"] is True, "Silent/flush contract differs")
    require(report["leather_ready_phase_masks_left_right"] == [15, 15], "Native Ready4/facing masks incomplete")
    require(report["light_primary_phase_masks"] == [0, 0, 0], "Ready-only proof unexpectedly attacked")
    require(all(int(report[key]) == 0 for key in ("medium_instance_id", "medium_source_id", "original_light_drop_source")), "Ready-only proof unexpectedly entered medium/drop flow")
    obs = report["observations"]
    require(obs and index["observations"] == len(obs), "Observation/index count differs")
    inputs = report["normal_input_requests"]
    require(inputs == report["inputevents"], "Input aliases differ")
    downs = [row["key"] for row in inputs if row["down"] is True]
    require(len(downs) == 5 and downs[:4] == ["Enter", "E", "A", "E"] and downs[4] in ("A", "D"), "Expected normal Enter/E/A cancel/E commit/direction turn only")
    held = set()
    prior = -1.0
    for row in inputs:
        require(row["key"] in ("Enter", "E", "A", "D") and type(row["down"]) is bool and finite(row["wall_offset_s"]) and row["wall_offset_s"] >= prior, "Input order/key differs")
        require((row["key"] not in held) if row["down"] else (row["key"] in held), "Unpaired/duplicate normal input")
        if row["down"]:
            held.add(row["key"])
        else:
            held.remove(row["key"])
        prior = row["wall_offset_s"]
    require(not held, "Native trial ended with a held input")
    require([(row["step"], row["phase"]) for row in report["phasechecks"]] == list(enumerate(PHASES)), "Ready-only phase transitions differ")
    light = str(report["light_instance_id"])
    require(int(light) > 0 and int(report["light_source_id"]) > 0, "Actual registered light identity missing")
    first, last = obs[0], obs[-1]
    constant = (first["run"], first["run_alias"], first["owner_id"], first["committed_weapon_id"], first["committed_weapon_version"])
    require(int(constant[2]) > 0 and int(constant[3]) > 0, "Actual player/sword identity missing")
    require(int(last["operation_count"]) - int(first["operation_count"]) == 1 and int(last["next_operation_id"]) - int(first["next_operation_id"]) == 1, "Ready trial must commit exactly once")
    selected = {}
    masks = {-1: 0, 1: 0}
    seen_steps = set()
    light_versions = set()
    pending_count = 0
    last_ops = int(first["operation_count"])
    last_draw = int(first["draw_id"]) - 1
    for i, row in enumerate(obs):
        require((row["run"], row["run_alias"], row["owner_id"], row["committed_weapon_id"], row["committed_weapon_version"]) == constant, "Actual run/player/sword identity changed")
        require(row["flow_step"] in range(6) and row["flow_phase"] == PHASES[row["flow_step"]], "Observation came from another flow")
        seen_steps.add(row["flow_step"])
        require(row["active"] is True and row["texture_ready"] is True and row["interface_visible"] is False and row["text_calls"] == 0, "Draw/readiness/UI-off contract differs")
        require(math.isclose(row["canvas_size"], CANVAS, abs_tol=1e-9) and row["body_max_contract"] == 72, "Actual source canvas/body-size contract changed")
        require(math.isclose(row["sim"], row["actual_sim"], abs_tol=1e-9), "Draw and native owner clocks differ")
        require(row["facing"] in (-1, 1) and row["frame"] in range(4) and row["stage"] == -1 and int(row["action_id"]) == 0 and row["melee_pending_primary"] is False, "Ready-only row contains attack/stage/invalid frame")
        require(row["clip"] == "sword_ready_idle" and row["weapon_mirror"] == "WPN-SWD-001", "Unexpected clip or actual sword content")
        require(int(row["draw_id"]) > last_draw, "Observation draw IDs are not increasing")
        last_draw = int(row["draw_id"])
        operation = int(row["operation_count"])
        require(operation in (int(first["operation_count"]), int(first["operation_count"]) + 1) and operation >= last_ops, "Operation receipt changed unexpectedly")
        last_ops = operation
        armor_id = str(row["committed_armor_id"])
        require(armor_id in ("0", light), "Unexpected committed armor in Ready-only proof")
        mode = "no_armor" if armor_id == "0" else "light_armor"
        require(row["expected_armor_mode"] == mode, "Draw mode is not actual committed armor")
        require(row["armor_mirror"] == ("" if armor_id == "0" else "ARM-LGT-001"), "Actual armor content mirror differs")
        if armor_id != "0":
            light_versions.add(str(row["committed_armor_version"]))
        else:
            require(int(row["committed_armor_version"]) == 0, "Unarmored slot has a committed version")
        # Derive process-only pickup retention separately from draw flags. This
        # controlled grounded trial contains only PickupArmor, never a skill.
        pending = row["pending_equipment_action"] is True and row["pending_equipment_kind"] == 2 and row["animation"] == "equip_armor"
        require(pending == row["committed_gear_placeholder_expected"], "Pending committed-identity expectation differs")
        if pending:
            pending_count += 1
            require(row["supported"] is False and row["frame"] == 0 and str(row["pending_instance_id"]) == light, "Pickup was relabeled as a supported pose or lost target")
        draw_gear = row["supported"] is True or pending
        stack = row["draw_stack"]
        has_armor = any("Shoulder" in path or "Chest" in path for path in stack)
        require(has_armor == row["draw_stack_has_armor"], "Armor stack metadata differs")
        expected_body = object_path(BODY, f"T_Fairytale_SwordReady_{row['frame']:03d}_v002")
        require(row["texture"] == expected_body, "Common original Body158 Ready texture path changed")
        if not draw_gear:
            require(stack == [expected_body] and not row["armor_drawn"] and not has_armor and row["weapon"] == "", "Unsupported pose leaks armor or sword")
        elif mode == "no_armor":
            require(stack == [expected_body, SWORD, expected_body] and not row["armor_drawn"] and not has_armor and row["weapon"] == SWORD, "No-armor row is dressed or lost independent sword")
        else:
            require(row["armor_drawn"] is True and row["armor_ready"] is True and has_armor and row["weapon"] == SWORD and stack == expected_stack(row["frame"]), "Actual LGT does not use three new armor/three old body/sword seven-stack")
            require(sum(path.startswith(NEW) for path in stack) == 3, "Actual seven-stack does not contain exactly three new Ready layers")
        if draw_gear:
            require(str(row["instance_id"]) == str(row["committed_weapon_id"]) and math.isclose(row["weapon_scale"], .5, abs_tol=1e-12), "Independent sword identity/scale changed")
        for resource in set(stack + [expected_body]):
            require(package_file(resource) in package_rows, "Actual drawn resource is missing from source snapshot")
        if row["flow_step"] == 5 and mode == "light_armor" and row["supported"] is True and not row["pending_equipment_action"] and row["animation"] == "idle":
            masks[row["facing"]] |= 1 << row["frame"]
            selected.setdefault((row["facing"], row["frame"]), i)
    require(seen_steps == set(range(6)) and pending_count > 0, "Actual cancel/commit observations missing")
    require(masks == {-1: 15, 1: 15} and len(selected) == 8, "Independent actual Ready4/facing selection is incomplete")
    require(len(light_versions) == 1 and int(next(iter(light_versions))) > 0 and str(last["committed_armor_id"]) == light, "Committed light instance/version changed")
    return selected, {"flow_complete": True, "observations": len(obs), "actual_light_instance_id": light,
        "actual_weapon_instance_id": constant[3], "operations_committed": 1, "normal_key_down_order": downs,
        "actual_ready_masks_left_right": [masks[-1], masks[1]], "pending_pickup_observations": pending_count,
        "mismatches": [], "scope": "Actual normal cancel/one commit/Ready4 both facings only", "full_motion_accepted": False,
        "whole_game_audio_accepted": False, "formal_complete_units": 0}


def verify_pixels(original, report):
    metadata = read(original / "native-lossless-capture.json")
    require(metadata["mode"] == "native_viewport_BGRA8_lossless_PNG_zlib0", "Capture mode is not native lossless")
    require(all(metadata[key] is False for key in ("pixel_mutations", "simulation_pacing_changed", "audio_changed")), "Capture mutated pixels/pacing/audio")
    require(metadata.get("async_movie_writer_requested") is True and metadata.get("async_movie_writer_active") is True and metadata.get("prewarm_synchronous") is True, "Native async writer/prewarm contract differs")
    require(metadata["movie_filename_reservation"] == "Windows_CreateFileW_CREATE_NEW_exact_engine_request_before_enqueue", "Movie reservation contract differs")
    receipts = [json.loads(line) for line in (original / "native-frame-pixels.jsonl").read_text(encoding="utf-8-sig").splitlines() if line]
    names = [row["file"] for row in receipts]
    movies = sorted(original.glob("MovieFrame*.png"))
    require(len(names) == len(set(names)) and set(names) == {p.name for p in movies} | {"prewarm-viewport.png"}, "Every original PNG needs exactly one native receipt")
    movie_receipts = [row for row in receipts if row["file"].startswith("MovieFrame")]
    timing = report["capture_timing"]
    offsets = timing["frame_wall_offsets_s"]
    obs = report["observations"]
    count = len(movies)
    require(count == len(obs) == len(offsets) == len(movie_receipts) > 0, "Movie/observation/offset/receipt counts differ")
    require([row["file"] for row in movie_receipts] == [p.name for p in movies] and [row["writer_sequence"] for row in movie_receipts] == list(range(1, count + 1)), "Native movie FIFO sequence differs")
    duration = timing["requested_video_wall_duration_s"]
    start, stop = timing["capture_start_monotonic_s"], timing["capture_stop_monotonic_s"]
    require(timing["use_fixed_time_step"] is False and finite(duration) and duration > 0 and math.isclose(duration, stop - start, abs_tol=1e-6) and math.isclose(duration, report["duration_s"], abs_tol=1e-9), "Actual nonfixed wall-clock duration differs")
    require(all(finite(offset) for offset in offsets) and 0 <= offsets[0] and offsets[-1] < duration and all(b > a for a, b in zip(offsets, offsets[1:])), "Frame wall offsets are not strict real-time events")
    summary = read(original / "native-async-write-summary.json")
    require(all(summary[key] is True for key in ("requested", "active", "closed", "flushed", "success")), "Native writer did not stop/flush")
    require(all(summary[key] == count for key in ("movie_reserved", "movie_enqueued", "movie_saved", "movie_completed", "receipts_saved")), "Native FIFO counts differ")
    require(all(summary[key] == 0 for key in ("movie_reservation_failed", "movie_failed", "rejected", "pending")), "Native writer reports incomplete frames")
    require(summary["flush_completed_monotonic_s"] >= stop and summary["last_save_completed_monotonic_s"] <= summary["flush_completed_monotonic_s"], "Native stop/flush clock differs")
    fingerprints = []
    by_name = {row["file"]: row for row in receipts}
    for row in receipts:
        require(row["saved"] is True and Path(row["file"]).name == row["file"], "Unsafe or unsaved native PNG")
        path = original / row["file"]
        with Image.open(path) as image:
            require(image.format == "PNG" and image.size == (row["width"], row["height"]) == (1280, 720), "Original native dimensions differ")
            array = np.asarray(image.convert("RGBA"))
            require(np.all(array[:, :, 3] == 255), "Native viewport alpha is not fully opaque")
            crc = zlib.crc32(array[:, :, [2, 1, 0, 3]].tobytes()) & 0xffffffff
            require(crc == row["native_BGRA8_crc32"], "Native viewport BGRA CRC differs")
        fingerprints.append(desc(path))
    for i, row in enumerate(movie_receipts):
        require(row["async_writer"] is True and row["copy_crc_matches"] is True and row["filename_reserved"] is True and row["filename_reservation_mode"] == "Windows_CreateFileW_CREATE_NEW", "Native movie copy/reservation contract differs")
        require(row["copied_BGRA8_crc32"] == row["native_BGRA8_crc32"], "Native BGRA copy CRC differs")
        callback, reserved, queued, began, ended = [row[key] for key in ("capture_callback_monotonic_s", "reservation_completed_monotonic_s", "enqueued_monotonic_s", "save_started_monotonic_s", "save_completed_monotonic_s")]
        require(0 < callback <= reserved <= queued <= began <= ended, "Native event/write clocks reordered")
        require(callback <= start + offsets[i] + 1e-6 and math.isclose(row["save_wall_s"], ended - began, abs_tol=1e-6), "Save completion replaced capture-event time")
        require(math.isclose(obs[i]["wall_offset_s"], offsets[i], abs_tol=1e-12), "Observation is not paired to its actual processed-event wall offset")
        # screenshot_request is legitimately empty in the actual automatic movie
        # profile. Pair by FIFO/sequence + event timing + CRC, not that HUD field.
    require(by_name["prewarm-viewport.png"].get("async_writer", False) is False, "Prewarm must remain synchronous")
    require(math.isclose(summary["first_capture_callback_monotonic_s"], movie_receipts[0]["capture_callback_monotonic_s"], abs_tol=1e-6) and math.isclose(summary["last_capture_callback_monotonic_s"], movie_receipts[-1]["capture_callback_monotonic_s"], abs_tol=1e-6), "Native first/last callback summary differs")
    existing = read(original / "native-pixel-verification.json")
    require(existing["every_source_viewport_pixel_crc_matches"] is True and existing["native_async_writer_verified"] is True and existing["verified_original_PNG_count"] == count + 1, "Capture CRC receipt differs from independent verification")
    return movies, movie_receipts, fingerprints, offsets, duration


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", required=True)
    parser.add_argument("--snapshot", required=True)
    args = parser.parse_args()
    archive, snapshot = (ROOT / args.archive).resolve(), (ROOT / args.snapshot).resolve()
    require(archive.is_relative_to(ROOT / "过程图稿与视频") and snapshot.is_relative_to(ROOT / "source-assets/production/backups"), "Archive/snapshot outside authorized project roots")
    original, presentation = archive / "原件", archive / "展示副本"
    require(original.is_dir() and presentation.is_dir(), "Actual capture archive is missing")
    require(not (original / "independent-leather-ready-verification-v001.json").exists(), "Never overwrite a prior postprocess; retain a new version")
    report, index = read(original / "runtime-report.json"), read(archive / "index.json")
    manifest, package_rows, source_audit = verify_sources(snapshot, index)
    selection, flow_audit = verify_flow(report, index, package_rows)
    movies, pixel_rows, fingerprints, offsets, duration = verify_pixels(original, report)
    # Validate everything above before creating crops/video. Native originals
    # stay untouched; no generated or selected frame is substituted for them.
    maps = []
    for facing in (-1, 1):
        for frame in range(4):
            i = selection[(facing, frame)]
            row = report["observations"][i]
            scale = row["canvas_size"] / 512.0
            root_x = row["grip_screen"][0] - facing * (row["grip"][0] - row["root"][0]) * scale
            root_y = row["grip_screen"][1] - (row["grip"][1] - row["root"][1]) * scale
            left = max(0, min(1040, math.floor(root_x) - 110))
            top = max(0, min(560, math.floor(root_y) - 130))
            destination = presentation / f"leather-ready-{'left' if facing < 0 else 'right'}-frame-{frame}-{movies[i].name}"
            require(not destination.exists(), "Never overwrite an existing presentation crop")
            with Image.open(movies[i]) as image:
                crop = image.crop((left, top, left + 240, top + 160))
                crop.save(destination)
                expected_bytes = crop.tobytes()
            with Image.open(destination) as crop:
                require(crop.size == (240, 160) and crop.tobytes() == expected_bytes, "Unscaled crop pixel round-trip differs")
            maps.append({"observation_index": i, "writer_sequence": pixel_rows[i]["writer_sequence"], "native_BGRA8_crc32": pixel_rows[i]["native_BGRA8_crc32"],
                "wall_offset_s": offsets[i], "flow_phase": row["flow_phase"], "flow_step": row["flow_step"], "clip": row["clip"], "frame": frame, "facing": facing,
                "actual_light_instance_id": row["committed_armor_id"], "draw_stack": row["draw_stack"], "source_whole": desc(movies[i]),
                "unscaled_crop": desc(destination), "crop_rect_xywh_px": [left, top, 240, 160], "crop_resampled": False, "actually_viewed": False})
    concat = original / "leather-ready-wall-timed-frames-v001.txt"
    lines = []
    for i, path in enumerate(movies):
        left = 0.0 if i == 0 else offsets[i]
        right = offsets[i + 1] if i + 1 < len(movies) else duration
        require(right > left and "'" not in path.as_posix(), "Invalid concat interval/path")
        lines.extend(["file '" + path.as_posix() + "'", f"duration {right - left:.12f}"])
    lines.append("file '" + movies[-1].as_posix() + "'")
    new(concat, "\n".join(lines) + "\n")
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    video = presentation / "leather-ready-trial-silent.mp4"
    require(not video.exists(), "Never overwrite prior review video")
    encode = [ffmpeg, "-hide_banner", "-loglevel", "warning", "-f", "concat", "-safe", "0", "-i", str(concat),
              "-vf", "fps=30", "-t", f"{duration:.12f}", "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p", "-an", str(video)]
    encoded = subprocess.run(encode, capture_output=True, text=True)
    new(original / "leather-ready-video-encode.log", encoded.stdout + encoded.stderr)
    require(encoded.returncode == 0 and video.is_file() and video.stat().st_size > 0, "Review video encoding failed; preserve failed outputs")
    decode = [ffmpeg, "-hide_banner", "-v", "error", "-i", str(video), "-map", "0:v:0", "-an", "-progress", "pipe:1", "-nostats", "-f", "null", os.devnull]
    decoded = subprocess.run(decode, capture_output=True, text=True)
    new(original / "leather-ready-video-full-decode.log", decoded.stdout + decoded.stderr)
    progress = {}
    for line in decoded.stdout.splitlines():
        if "=" in line:
            key, value = line.split("=", 1)
            progress[key] = value.strip()
    require(decoded.returncode == 0 and not decoded.stderr.strip() and int(progress.get("frame", "0")) > 0 and progress.get("progress") == "end", "Full review-video decode failed")
    for item in fingerprints:
        same_pin(Path(item["path"]), item)
    # Recheck every current and frozen Source/DLL/package endpoint after encoding.
    _, _, final_source_audit = verify_sources(snapshot, index)
    require(source_audit == final_source_audit, "Postprocess changed compiled input audit")
    source_audit["endpoint_checks_before_and_after_postprocess"] = 2 * source_audit["source_endpoint_checks"]
    flow_audit.update({"original_PNGs": len(fingerprints), "movie_frames": len(movies), "duration_s": duration,
                      "every_movie_observation_FIFO_CRC_bound": True, "native_async_stop_flush_verified": True,
                      "selected_actual_frame_facing_pairs": 8, "art_review_pending": True})
    new(original / "leather-ready-source-binding-verification-v001.json", source_audit)
    new(original / "independent-leather-ready-verification-v001.json", flow_audit)
    new(original / "leather-ready-selected-source-map-v001.json", {"frames": maps, "selection_is_not_art_review": True})
    new(original / "leather-ready-pixel-FIFO-binding-v001.json", {"movies": [{"file": movies[i].name, "observation_index": i,
        "writer_sequence": row["writer_sequence"], "native_BGRA8_crc32": row["native_BGRA8_crc32"], "wall_offset_s": offsets[i]} for i, row in enumerate(pixel_rows)],
        "whole_PNG_fingerprints_before_and_after_equal": fingerprints, "source_pixels_mutated": False,
        "event_clock_note": "Offsets are native ScreenshotProcessed events; writer capture callback can precede them. Save completion is never used for playback timing."})
    new(original / "leather-ready-video-receipt-v001.json", {"video": desc(video), "encode_argv": encode, "encode_exit": encoded.returncode,
        "full_decode_argv": decode, "full_decode_exit": decoded.returncode, "decoded_frame_count": int(progress["frame"]), "audio_recorded": False,
        "presentation_policy": "Actual processed-event wall offsets; first frame held from zero, final frame held to native duration; final concat sentinel; CFR30 quantization and duration cap. Original clocks/PNG/positions unchanged.",
        "motion_or_audio_accepted": False})
    provenance = original / "leather-ready-postprocess-provenance-v001"
    require(not provenance.exists(), "Never overwrite prior postprocess provenance")
    provenance.mkdir()
    (provenance / "compiled-source-manifest.json").write_bytes((snapshot / "compiled-source-manifest.json").read_bytes())
    (provenance / Path(__file__).name).write_bytes(Path(__file__).read_bytes())
    new(archive / "source-version-status-index.json", {"status": "actual_leather_Ready4_both_facings_passed_visual_review_pending", "snapshot": snapshot.as_posix(),
        "runtime_report": desc(original / "runtime-report.json"), "independent_verification": desc(original / "independent-leather-ready-verification-v001.json"),
        "source_binding": desc(original / "leather-ready-source-binding-verification-v001.json"), "selected_unscaled_crops": 8, "video": desc(video),
        "default_full_bound_flow_claimed": False, "complete_equipment_or_full_motion_accepted": False, "formal_complete_units": 0})
    new(archive / "README.md", "真实软皮轻甲Ready-only试装：正常Enter/E/A取消/E提交一次，正常A/D转向，同一实际LGT实例左右各Ready4。新3甲层/旧3body层/独立军剑7层逐帧验证；无甲不画甲、不支持动作不漏甲剑。原PNG及实际墙钟保持，8张无缩放裁图与CFR30静音视频仅供Root留档后实看。未验证攻击、完整换装/走跑/受击/死亡、全状态/全部适配、正式来源、存档或音效；不冒用默认全绑定三提交流程。\n")
    print(json.dumps({"observations": len(report["observations"]), "original_PNGs": len(fingerprints), "snapshot_files": source_audit["snapshot_files"],
        "production_packages": source_audit["production_packages"], "current_full_automation_succeeded": source_audit["current_full_automation_succeeded"],
        "source_mismatches": 0, "operations_committed": 1, "actual_ready_masks_left_right": [15, 15], "selected_unscaled_crops": len(maps),
        "video": desc(video), "art_review_pending": True, "formal_complete_units": 0}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
