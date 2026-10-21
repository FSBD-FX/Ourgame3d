"""Read-only verifier for the isolated silent idle lookdev capture (never old combat gates)."""
from pathlib import Path
import argparse
import json
import math
import hashlib
import zlib

PREFIX = "/Game/Production/ArtTrials/EV047/v001/"
ROOTS = {"hero": [[256, 464]] * 4, "stone": [[260, 464], [257, 464], [264, 464], [265, 464]]}
CANVAS = {"hero": 72 * 512 / 416, "stone": 93.6 * 512 / 386.5}
NATIVE = {"hero": 1, "stone": -1}


def expected_path(actor, frame):
    folder, name = ("HeroCommonIdle", "HeroIdle") if actor == "hero" else ("StoneIdle", "StoneIdle")
    name = f"T_Fairytale_{name}_{frame:03d}_v001"
    return f"{PREFIX}{folder}/{name}.{name}"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def validate_observations(report):
    require(report.get("schema") == "fairytale-lookdev-capture-v1", "Wrong/missing independent schema")
    require(report.get("profile") == "fairytale_idle_observation_silent" and report.get("passed") is True, "Lookdev profile failed")
    require(report.get("silent_video") is True and report.get("audio_capture_started") is False, "Silent profile must not claim recorded audio")
    require(report.get("native_async_flush_after_audio_stop") is False, "No fictitious audio-stop boundary")
    require(report.get("formal_complete_units") == 0 and report.get("new_style_accepted") is False
            and report.get("motion_reviewed") is False and report.get("auditioned") is False, "Capture is not review/acceptance")
    timing = report["capture_timing"]
    offsets = timing["frame_wall_offsets_s"]
    observations = report["observations"]
    require(len(observations) == len(offsets) >= 300, "Missing/short actual draw observations")
    require(timing["use_fixed_time_step"] is False, "Fixed-step capture forbidden")
    duration = timing["capture_stop_monotonic_s"] - timing["capture_start_monotonic_s"]
    require(6 <= duration <= 8 and abs(duration - timing["requested_video_wall_duration_s"]) < 1e-6, "Independent duration mismatch")
    require(0 < offsets[0] <= .1 and all(b > a for a, b in zip(offsets, offsets[1:])), "Invalid frame clock")
    require(offsets[-1] <= duration and duration - offsets[-1] < .15, "Capture tail missing")
    prewarm = report["prewarm_screenshot"]
    require(prewarm["requested"] is True and prewarm["completed_file_received"] is True
            and prewarm["used_as_recording_frame"] is False, "Prewarm is not a movie frame")
    require(0 < prewarm["request_monotonic_s"] <= prewarm["complete_monotonic_s"] <= timing["capture_start_monotonic_s"], "Prewarm ordering")
    baseline = report["baseline_game"]
    require(baseline["available"] and baseline["mode"] and baseline["waiting"]
            and not baseline["player_tick_enabled"], "Not a frozen independent mode")
    require(all(not e["tick_enabled"] and not e["ai_enabled"] for e in baseline["enemies"]), "Enemy tick/AI not frozen")
    masks = {(actor, side): 0 for actor in ("hero", "stone") for side in (-1, 1)}
    loops = dict.fromkeys(masks, 0)
    previous = {}
    serial = -1
    epoch = None
    for row, offset in zip(observations, offsets):
        require(abs(row["wall_offset_s"] - offset) < 1e-8, "Observation/capture clock mismatch")
        require(row["hud_available"] and row["active"] and row["configuration_confirmed"], "Missing actual lookdev draw")
        require(row["game"] == baseline, "Game state advanced while observing new idle")
        require(not row["interface_visible"] and row["text_draw_calls"] == row["legacy_stack_count"] == row["action_audio_requests"] == 0
                and not row["legacy_weapon_used"], "Interface/old identity/audio request leaked")
        require(row["viewport"] == [1280, 720] and abs(row["ui_scale"] - 1) < 1e-7, "Unexpected viewport scaling")
        current = int(row["draw_serial"])
        require(current > serial, "Same/stale HUD draw reused")
        serial = current
        capture_wall = timing["capture_start_monotonic_s"] + offset
        require(0 <= capture_wall - row["draw_wall"] < .1, "HUD observation is not current to screenshot")
        elapsed = row["animation_elapsed_s"]
        require(math.isfinite(elapsed) and elapsed >= 0, "Invalid independent animation clock")
        current_epoch = row["draw_wall"] - elapsed
        if epoch is None:
            epoch = current_epoch
        require(abs(current_epoch - epoch) < 1e-6 and epoch <= timing["capture_start_monotonic_s"], "Independent animation epoch changed")
        sample = math.floor(elapsed / .167)
        expected_hero_facing = -1 if row["input_A"] and not row["input_D"] else 1 if row["input_D"] and not row["input_A"] else None
        for actor in ("hero", "stone"):
            draw = row[actor]
            frame, side = draw["frame"], draw["facing"]
            require(frame == sample % 4 and int(draw["sample"]) == sample, "167ms manifest sampling mismatch")
            require(side in (-1, 1) and draw["native_facing"] == NATIVE[actor], "Native facing mismatch")
            if expected_hero_facing is not None:
                require(side == (expected_hero_facing if actor == "hero" else -expected_hero_facing), "Normal A/D did not control display direction")
            require(draw["texture_ready"] and draw["path"] == expected_path(actor, frame), "Missing/new identity replaced by fallback")
            require(draw["root"] == ROOTS[actor][frame] and abs(draw["canvas_size"] - CANVAS[actor]) < 1e-7, "Measured root/fixed scale changed")
            flipped = side != NATIVE[actor]
            require(draw["flipped"] == flipped, "Wrong native-facing mirroring")
            x, y = draw["ground_screen"]
            require(abs(x - (435.2 if actor == "hero" else 819.2)) < 1e-3 and abs(y - 540) < 1e-3, "Observation anchor drift")
            camera = row["camera_ground_center"]
            world = draw["ground"]
            require(abs(x - (640 + (world[0] - camera[0]) * .65)) < 1e-3
                    and abs(y - (490 - world[1] * .38)) < 1e-3, "Ground projection mismatch")
            root_x = 512 - draw["root"][0] if flipped else draw["root"][0]
            top = [x - CANVAS[actor] * root_x / 512, y - CANVAS[actor] * draw["root"][1] / 512]
            require(all(abs(a - b) < 1e-3 for a, b in zip(top, draw["top_screen"])), "Feet root/top/mirror mismatch")
            key = (actor, side)
            masks[key] |= 1 << frame
            last = previous.get(actor)
            if last and last[0] == side and last[1] == 3 and frame == 0 and sample == last[2] + 1:
                loops[key] += 1
            previous[actor] = (side, frame, sample)
    require(all(v == 15 for v in masks.values()), "All four poses in both facings not observed")
    require(all(v >= 2 for v in loops.values()), "Two real 3→0 wraps per facing/actor not observed")
    requests = report["normal_input_requests"]
    for key in ("A", "D", "W", "S", "J", "K", "E", "Q", "T", "R", "Enter", "SpaceBar", "LeftShift"):
        require(any(r["key"] == key and r["down"] for r in requests)
                and any(r["key"] == key and not r["down"] for r in requests), f"Normal input stress missing: {key}")
    return {"observations": len(observations), "duration_s": duration,
            "pose_masks": {f"{a}_{s}": v for (a, s), v in masks.items()},
            "wraps_3_to_0": {f"{a}_{s}": v for (a, s), v in loops.items()}}


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def validate_native(archive, report):
    """Same native CRC/FIFO/exclusive reservation contracts, with an honest silent stop boundary."""
    import numpy as np
    from PIL import Image
    original = archive / "原件"
    metadata = json.loads((original / "native-lossless-capture.json").read_text(encoding="utf-8-sig"))
    require(metadata["mode"] == "native_viewport_BGRA8_lossless_PNG_zlib0", "Native mode missing")
    require(all(metadata[k] is False for k in ("pixel_mutations", "simulation_pacing_changed", "audio_changed")), "Helper changed pixels/pacing/audio")
    require(metadata["async_movie_writer_requested"] and metadata["async_movie_writer_active"] and metadata["prewarm_synchronous"], "Async/prewarm contract missing")
    require(metadata["movie_filename_reservation"] == "Windows_CreateFileW_CREATE_NEW_exact_engine_request_before_enqueue", "Exclusive native reservation absent")
    rows = [json.loads(line) for line in (original / "native-frame-pixels.jsonl").read_text(encoding="utf-8-sig").splitlines() if line]
    names = [r["file"] for r in rows]
    actual = {p.name for p in original.glob("MovieFrame*.png")} | {"prewarm-viewport.png"}
    require(len(names) == len(set(names)) and set(names) == actual, "Native receipt must cover originals exactly once")
    for row in rows:
        require(row["saved"] is True and Path(row["file"]).name == row["file"], "Unsafe/failed native write")
        with Image.open(original / row["file"]) as image:
            require(image.format == "PNG" and image.size == (row["width"], row["height"]) == (1280, 720), "Native PNG size/format")
            rgba = np.asarray(image.convert("RGBA"))
            require(bool(np.all(rgba[:, :, 3] == 255)), "Native alpha changed")
            crc = zlib.crc32(rgba[:, :, [2, 1, 0, 3]].tobytes()) & 0xffffffff
            require(crc == row["native_BGRA8_crc32"], f"Viewport CRC mismatch: {row['file']}")
    movie = [r for r in rows if r["file"].startswith("MovieFrame")]
    count = len(movie)
    require(count > 0 and [r["file"] for r in movie] == sorted(r["file"] for r in movie), "FIFO filenames reordered")
    require([r["writer_sequence"] for r in movie] == list(range(1, count + 1)), "Writer sequence gap/reorder")
    require(next(r for r in rows if r["file"] == "prewarm-viewport.png").get("async_writer", False) is False, "Prewarm must complete synchronously")
    summary = json.loads((original / "native-async-write-summary.json").read_text(encoding="utf-8-sig"))
    require(all(summary[k] is True for k in ("requested", "active", "closed", "flushed", "success")), "Native queue not sealed/drained")
    require(all(summary[k] == count for k in ("movie_reserved", "movie_enqueued", "movie_saved", "movie_completed", "receipts_saved")), "Native count mismatch")
    require(all(summary[k] == 0 for k in ("movie_reservation_failed", "movie_failed", "rejected", "pending")), "Native failures/pending jobs")
    require(report["native_async_capture_requested"] and report["native_async_capture_writes_flushed"]
            and report["capture_stop_before_flush"], "Silent capture stop/drain missing")
    timing = report["capture_timing"]
    require(len(timing["frame_wall_offsets_s"]) == count, "Actual PNG/callback count mismatch")
    for row, offset in zip(movie, timing["frame_wall_offsets_s"]):
        require(row["async_writer"] and row["copy_crc_matches"] and row["filename_reserved"]
                and row["filename_reservation_mode"] == "Windows_CreateFileW_CREATE_NEW", "Unsafe asynchronous frame")
        require(row["copied_BGRA8_crc32"] == row["native_BGRA8_crc32"], "Deep copy CRC changed")
        capture, reserved, queued = (row[k] for k in ("capture_callback_monotonic_s", "reservation_completed_monotonic_s", "enqueued_monotonic_s"))
        started, completed = row["save_started_monotonic_s"], row["save_completed_monotonic_s"]
        require(0 < capture <= reserved <= queued <= started <= completed, "Native event ordering")
        require(capture <= timing["capture_start_monotonic_s"] + offset + 1e-6, "Save completion substituted for capture event")
        require(abs(row["save_wall_s"] - (completed - started)) < 1e-6, "Native save timing mismatch")
    require(summary["last_save_completed_monotonic_s"] <= summary["flush_completed_monotonic_s"] <= report["flush_completed_monotonic_s"], "Flush completion order")
    require(timing["capture_stop_monotonic_s"] <= summary["flush_completed_monotonic_s"], "Writer flushed before capture stopped")
    require(abs(summary["first_capture_callback_monotonic_s"] - movie[0]["capture_callback_monotonic_s"]) < 1e-6
            and abs(summary["last_capture_callback_monotonic_s"] - movie[-1]["capture_callback_monotonic_s"]) < 1e-6, "Native endpoint clocks")
    require(not list(original.glob("runtime-mix*.wav")), "Silent profile unexpectedly contains runtime audio")
    return {"verified_original_PNG_count": len(rows), "native_async_writer_verified": True,
            "every_source_viewport_pixel_crc_matches": True, "capture_stop_before_flush": True}


def validate_manifest(path):
    from PIL import Image
    manifest = json.loads(Path(path).read_text(encoding="utf-8-sig"))
    require(manifest["schema"] == "frozen-fairytale-lookdev-eight-textures-v1", "Wrong source manifest")
    assets = manifest["assets"]
    require(len(assets) == 8 and {(r["actor"], r["frame"]) for r in assets}
            == {(a, f) for a in NATIVE for f in range(4)}, "Exact eight independent sources missing")
    for row in assets:
        actor, frame = row["actor"], row["frame"]
        require(row["object_path"] == expected_path(actor, frame) and row["root_px"] == ROOTS[actor][frame]
                and row["native_facing"] == NATIVE[actor] and row["duration_ms"] == 167, "Source path/root/facing/timing mismatch")
        source = Path(row["source"])
        require(source.is_absolute() and source.stat().st_size == row["source_bytes"]
                and digest(source) == row["source_sha256"], "Source provenance mismatch")
        with Image.open(source) as image:
            require(image.mode == "RGBA" and image.size == (512, 512), "Wrong source RGBA canvas")
    for actor in NATIVE:
        values = manifest["actors"][actor]
        require(values["durations_ms"] == [167] * 4 and values["native_facing"] == NATIVE[actor]
                and abs(values["preview_canvas_size_world"] - CANVAS[actor]) < 1e-7, "Actor manifest presentation mismatch")
    return {"manifest_sha256": digest(path), "verified_source_PNG_count": 8}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--archive", required=True)
    parser.add_argument("--manifest", required=True)
    args = parser.parse_args()
    archive = Path(args.archive).resolve()
    report_path = archive / "原件/runtime-report.json"
    report = json.loads(report_path.read_text(encoding="utf-8-sig"))
    result = {"schema": "fairytale-lookdev-audit-v1", "passed": True,
              **validate_manifest(args.manifest), **validate_observations(report), **validate_native(archive, report),
              "report_sha256": digest(report_path), "silent_video": True, "motion_reviewed": False,
              "auditioned": False, "new_style_accepted": False, "formal_complete_units": 0,
              "limitations": ["Actual HUD observations and native pixels only; continuous animation playback review remains pending.",
                              "Two authored idle rows only, no walk, combat, equipment adaptation or completed content unit.",
                              "Silent video has no recorded/synthetic/substituted audio or audio-stop claim."]}
    print(json.dumps(result, ensure_ascii=False))
