"""Run the prepared asset intake and a real graphical Play In Editor probe.

Launch using unreal-verify-editor.ps1. This uses the engine's existing Python
plugin and official LevelEditorSubsystem APIs, without remote execution.
The editor remains open after the probe. This verifies infrastructure only.
"""
from datetime import datetime, timezone
from pathlib import Path
import json
import os
import runpy
import time
import traceback

import unreal


unreal.EditorPythonScripting.set_keep_python_script_alive(True)
PROJECT = Path(unreal.Paths.project_dir()).resolve()
ROOT = PROJECT.parent
SAVED = PROJECT / "Saved" / "Bootstrap"
SAVED.mkdir(parents=True, exist_ok=True)
RUN_ID = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
REPORT_PATH = SAVED / "pie-report.json"
HISTORY_PATH = SAVED / ("pie-report-" + RUN_ID + ".json")
FRAME_DIRECTORY = SAVED / "proof" / ("asset-intake-pie-" + RUN_ID)
FRAME_DIRECTORY.mkdir(parents=True, exist_ok=True)
PROOF_PATH = FRAME_DIRECTORY / "frame-000.png"
REPORT = {
    "run_id_utc": RUN_ID,
    "editor_pid": os.getpid(),
    "engine_version": unreal.SystemLibrary.get_engine_version(),
    "map": "/Game/Tests/Preparation/AssetIntake",
    "mode": "graphical_editor_play_in_editor",
    "status": "starting",
    "scope": "Preparation infrastructure only; no player combat or game loop.",
    "events": [],
    "screenshot_path": str(PROOF_PATH),
    "capture_scope": "Six nominal 1 FPS samples of real PIE; actual request/save times recorded per frame. No real-time recording or gameplay claim.",
    "sample_frames": [],
}


def record(event, **details):
    REPORT["events"].append({"utc": datetime.now(timezone.utc).isoformat(), "event": event, **details})
    REPORT_PATH.write_text(json.dumps(REPORT, ensure_ascii=False, indent=2), encoding="utf-8")
    unreal.log("[CodexPIE] " + event + " " + json.dumps(details))


LEVEL = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
EDITOR = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
ACTORS = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
HANDLE = None
STARTED = time.monotonic()
PLAY_STARTED = None
STOP_REQUESTED = None
SCREENSHOT_TASK = None
NEXT_FRAME_INDEX = 0
LAST_FRAME_REQUESTED = None
IN_TICK = False
ANIMATED_COMPONENTS = []


def observe_component(label, component):
    origin, extent, radius = unreal.SystemLibrary.get_component_bounds(component)
    actor_rotation = component.get_owner().get_actor_rotation()
    relative_rotation = component.get_editor_property("relative_rotation")
    root_name = component.get_bone_name(0)
    root = component.get_socket_transform(root_name, unreal.RelativeTransformSpace.RTS_COMPONENT)
    selected_bones = [component.get_bone_name(index) for index in range(component.get_num_bones())
                      if any(part in str(component.get_bone_name(index)).casefold() for part in ("head", "torso", "foot"))]
    bone_positions = {}
    for name in selected_bones:
        transform = component.get_socket_transform(name, unreal.RelativeTransformSpace.RTS_COMPONENT)
        bone_positions[str(name)] = [transform.translation.x, transform.translation.y, transform.translation.z]
    return {"label": label, "playing": component.is_playing(), "position_seconds": component.get_position(),
            "actor_rotation_pitch_yaw_roll": [actor_rotation.pitch, actor_rotation.yaw, actor_rotation.roll],
            "component_rotation_pitch_yaw_roll": [relative_rotation.pitch, relative_rotation.yaw, relative_rotation.roll],
            "reported_component_world_bounds_origin_cm": [origin.x, origin.y, origin.z],
            "reported_component_world_dimensions_cm_xyz": [extent.x * 2, extent.y * 2, extent.z * 2],
            "bounds_scope": "Engine component bounds; can fall back to reference bounds without a physics asset, not a posed vertex measurement.",
            "bone_component_positions_cm": bone_positions,
            "root_bone": str(root_name),
            "root_component_translation_cm": [root.translation.x, root.translation.y, root.translation.z],
            "root_component_rotation_quat_xyzw": [root.rotation.x, root.rotation.y, root.rotation.z, root.rotation.w]}


def finish(status, **details):
    global HANDLE
    REPORT["status"] = status
    REPORT.update(details)
    REPORT["finished_utc"] = datetime.now(timezone.utc).isoformat()
    record("probe_finished", status=status)
    HISTORY_PATH.write_bytes(REPORT_PATH.read_bytes())
    if HANDLE is not None:
        unreal.unregister_slate_post_tick_callback(HANDLE)
        HANDLE = None


def tick(delta_seconds):
    global PLAY_STARTED, STOP_REQUESTED, SCREENSHOT_TASK, NEXT_FRAME_INDEX, LAST_FRAME_REQUESTED, IN_TICK
    # Screenshot preparation can pump Slate while synchronously loading shaders.
    # Do not re-enter this state machine from those nested engine ticks.
    if IN_TICK:
        return
    IN_TICK = True
    try:
        now = time.monotonic()
        playing = LEVEL.is_in_play_in_editor()
        if PLAY_STARTED is None:
            if playing:
                PLAY_STARTED = now
                world = EDITOR.get_game_world()
                if world:
                    cameras = unreal.GameplayStatics.get_all_actors_of_class(world, unreal.CameraActor)
                    camera = next((actor for actor in cameras if actor.get_actor_label() == "Foundation Camera"), None)
                    controller = unreal.GameplayStatics.get_player_controller(world, 0)
                    if camera and controller:
                        controller.set_view_target_with_blend(camera, 0.0)
                    for actor in unreal.GameplayStatics.get_all_actors_of_class(world, unreal.SkeletalMeshActor):
                        label = actor.get_actor_label()
                        if label.startswith("Intake "):
                            component = actor.get_component_by_class(unreal.SkeletalMeshComponent)
                            animation = component.get_editor_property("animation_data").get_editor_property("anim_to_play")
                            component.play_animation(animation, True)
                            ANIMATED_COMPONENTS.append((label, component))
                REPORT["status"] = "play_observed"
                record("play_observed", is_in_play_in_editor=playing,
                       game_world=world.get_path_name() if world else None,
                       animations=[observe_component(label, component) for label, component in ANIMATED_COMPONENTS])
            elif now - STARTED > 90:
                finish("failed_begin_play_timeout", is_in_play_in_editor=False)
            return
        if STOP_REQUESTED is None:
            if not playing:
                finish("failed_play_ended_early", is_in_play_in_editor=False)
                return
            for frame in REPORT["sample_frames"]:
                if "saved_utc" not in frame and Path(frame["path"]).is_file() and Path(frame["path"]).stat().st_size:
                    frame["saved_utc"] = datetime.now(timezone.utc).isoformat()
                    frame["save_observed_play_seconds"] = now - PLAY_STARTED
                    record("sample_frame_saved", index=frame["index"], path=frame["path"])
            previous_saved = not REPORT["sample_frames"] or "saved_utc" in REPORT["sample_frames"][-1]
            task_done = SCREENSHOT_TASK is None or SCREENSHOT_TASK.is_task_done()
            interval_elapsed = LAST_FRAME_REQUESTED is None or now - LAST_FRAME_REQUESTED >= 1.0
            if NEXT_FRAME_INDEX < 6 and now - PLAY_STARTED >= 2 and previous_saved and task_done and interval_elapsed:
                frame_index = NEXT_FRAME_INDEX
                NEXT_FRAME_INDEX += 1
                LAST_FRAME_REQUESTED = now
                frame_path = FRAME_DIRECTORY / ("frame-%03d.png" % frame_index)
                REPORT["sample_frames"].append({"index": frame_index, "path": str(frame_path),
                    "requested_utc": datetime.now(timezone.utc).isoformat(), "request_play_seconds": now - PLAY_STARTED,
                    "animations": [observe_component(label, component) for label, component in ANIMATED_COMPONENTS]})
                record("sample_frame_requested", index=frame_index, is_in_play_in_editor=True)
                SCREENSHOT_TASK = unreal.AutomationLibrary.take_high_res_screenshot(
                    1280, 720, str(frame_path), camera=None, delay=0.2)
                record("screenshot_task_created", task_returned=SCREENSHOT_TASK is not None)
            now = time.monotonic()
            capture_complete = len(REPORT["sample_frames"]) == 6 and all("saved_utc" in frame for frame in REPORT["sample_frames"])
            if now - PLAY_STARTED >= 8 and (capture_complete or now - PLAY_STARTED >= 90):
                REPORT["observed_play_seconds"] = now - PLAY_STARTED
                REPORT["capture_complete"] = capture_complete
                STOP_REQUESTED = now
                record("animation_progress_observed", animations=[observe_component(label, component) for label, component in ANIMATED_COMPONENTS])
                LEVEL.editor_request_end_play()
                record("end_play_requested", is_in_play_in_editor=True)
            return
        if not playing:
            finish("passed", is_in_play_in_editor_after_stop=False,
                   screenshot_exists=PROOF_PATH.is_file(),
                   editor_actor_count_after_stop=len(ACTORS.get_all_level_actors()))
        elif now - STOP_REQUESTED > 60:
            finish("failed_end_play_timeout", is_in_play_in_editor_after_stop=True)
    except Exception:
        if LEVEL.is_in_play_in_editor():
            LEVEL.editor_request_end_play()
        finish("failed_python_exception", traceback=traceback.format_exc())
    finally:
        IN_TICK = False


try:
    record("asset_import_begin")
    runpy.run_path(str(ROOT / "tools" / "scripts" / "ue-import-prepared-assets.py"), run_name="__main__")
    record("asset_import_returned", report=str(SAVED / "asset-import-report.json"))
    font_script = ROOT / "tools" / "scripts" / "ue-import-prepared-font.py"
    if font_script.is_file():
        runpy.run_path(str(font_script), run_name="__main__")
        record("font_import_returned", report=str(SAVED / "font-import-report.json"))
    intake_report = json.loads((SAVED / "asset-import-report.json").read_text(encoding="utf-8"))
    if intake_report["status"] != "completed_intake_inspection":
        raise RuntimeError("Asset intake did not pass: " + intake_report["status"])
    if os.environ.get("CODEX_CHARACTER_AXIS_DIAGNOSTIC") == "1":
        runpy.run_path(str(ROOT / "tools" / "scripts" / "ue-diagnose-character-axis.py"), run_name="__main__")
        record("character_axis_diagnostic_returned", report=str(SAVED / "character-axis-diagnostic-report.json"))
        if os.environ.get("CODEX_CHARACTER_AXIS_APPLY_CANONICAL") == "1":
            axis_repair = json.loads((SAVED / "character-axis-repair-report.json").read_text(encoding="utf-8"))
            if axis_repair.get("canonical_alignment_passed") is not True:
                raise RuntimeError("Canonical character root alignment did not pass: " + axis_repair["status"])
    runpy.run_path(str(PROJECT / "Content" / "Python" / "bootstrap_foundation.py"), run_name="__main__")
    runpy.run_path(str(ROOT / "tools" / "scripts" / "unreal-build-asset-validation.py"), run_name="__main__")
    record("asset_validation_map_returned", report=str(SAVED / "asset-validation-map-report.json"))
    REPORT["editor_actor_count_before_play"] = len(ACTORS.get_all_level_actors())
    REPORT["status"] = "begin_play_requested"
    STARTED = time.monotonic()
    HANDLE = unreal.register_slate_post_tick_callback(tick)
    LEVEL.editor_request_begin_play()
    record("begin_play_requested", is_in_play_in_editor=LEVEL.is_in_play_in_editor())
except Exception:
    finish("failed_setup_exception", traceback=traceback.format_exc())
