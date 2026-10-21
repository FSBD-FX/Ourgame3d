"""Build only text candidates from pinned sources; no bitmap, AI, UE, or Source writes."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
PROJECT = Path("F:/Ourgame")
SKILL = Path("C:/Users/22499/.codex/skills/sprite-gen")
sys.path.insert(0, str(SKILL))
from PIL import Image
from sprite_gen.gen.prepare import row_prompt, normalize_states


def pin(path):
    data = path.read_bytes()
    return {"path": path.as_posix(), "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}


def write(name, value):
    path = HERE / name
    if path.exists():
        raise ValueError("Never overwrite a frozen candidate: " + str(path))
    path.parent.mkdir(parents=True, exist_ok=True)
    text = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n"
    path.write_text(text, encoding="utf-8")


def main():
    if Path(sys.executable).resolve() != (SKILL / ".venv/Scripts/python.exe").resolve():
        raise ValueError("Use installed sprite-gen venv")
    root = PROJECT / "source-assets/production"
    manifest = root / "fairytale-sword-runtime-v002/manifests/import-sword-body-v002.json"
    imported = json.loads(manifest.read_text(encoding="utf-8-sig"))
    ready0 = next(row for row in imported["assets"] if row["clip"] == "Ready" and row["frame"] == 0)
    anchor = Path(ready0["source"])
    anchor_pin = pin(anchor)
    assert anchor_pin["bytes"] == 121133
    assert anchor_pin["sha256"] == "d3f766506a9cc623c38787836a9c23c0126d185d1bdf7e8946181efd554338c5"
    with Image.open(anchor) as im:
        assert im.mode == "RGBA" and im.size == (512, 512)
        rgba = im.tobytes()
        anchor_geometry = {"mode": im.mode, "size": list(im.size),
                           "alpha_bbox": list(im.getchannel("A").getbbox()),
                           "actual_decoded_RGBA_sha256": hashlib.sha256(rgba).hexdigest()}
        opaque = [tuple(rgba[i:i+4]) for i in range(0, len(rgba), 4) if rgba[i+3] >= 128]
        green_min_distance = min(sum((p[i] - (0, 255, 0)[i]) ** 2 for i in range(3)) ** .5 for p in opaque)
    assert green_min_distance > 96
    phases = {
        "dodge": [
            "Immediate distinct compact brace: real slight knee bend, pelvis lowers, connected elbows/wrists draw close; preserve the helmet volume and facing",
            "Lowest guarded travel pose: knees and ankle angles change, short limbs tuck under the body, balanced torso; no rolling whole sprite or fixed copied hands",
            "Second visibly different travel pose: one knee begins to open, hips and elbows change while the body remains compact; do not imply native translation has stopped",
            "Recover support readiness: legs reopen and torso rises partway toward Ready; hand and wrist orientation changes naturally, no freeze/paste of Ready0",
        ],
        "hurt": [
            "Immediate actual impact compression: shoulders fold and knees flex, rigid helmet tilts as one solid shape; connected hands react naturally",
            "Peak recoil: real torso/hip offset and elbow/wrist response, two distinct separate arms, no new anatomy or stretched helmet",
            "Rebalance: leg/hip support and shoulder positions move back, hands remain anatomically attached with a distinct new wrist angle",
            "Recovery toward the accepted Ready silhouette: smaller residual knee/torso displacement; not a copied Ready0 frame",
        ],
        "death": [
            "Immediate loss of strength: visibly distinct slack shoulders and bent knees; recognizable rigid clock helmet remains attached",
            "Knees buckle and torso drops: hips rotate, both boots and hand/wrist configuration change; no whole-body image rotation",
            "Body falls with real articulated anatomy: torso and thighs rotate relative to each other, helmet remains rigid, hands/forearms are not detached",
            "Ground impact and settling: authentic supported body contact, limbs finish folding, helmet and boots fit wholly within the same source cell",
            "Stable recognizable corpse: relaxed supported silhouette, true final separate hand/wrist and helmet contours; remains the terminal pose indefinitely",
        ],
    }
    common_action = (
        "Fixed native RIGHT-facing three-quarter camera from the attached accepted SwordReady v002 frame0. "
        "The row owns motion only. Bare charcoal/grey cloth shirt and trousers, original belt, brown gloves and boots; "
        "rigid squat crooked bell/clock helmet, original knob and face opening with two contained amber eyes. "
        "Preserve the accepted anchor's actual shapes, proportions, palette and hand-ink weight. "
        "Same common drawing scale through the complete row: 416-source-pixel standing-equivalent body is a design target on 512 cells, "
        "not a demand that crouched/lying bboxes be 416 high. Never normalize, lengthen limbs, stretch the helmet or enlarge a small pose. "
        "The future weapon and armor are modular; paint only genuine connected body/glove/boot pixels. "
        "No sword/handle/rod/shield/staff/crossbow, no chest or shoulder armor, bracer or shin plate. "
        "Hands must be genuinely drawn with connected short upper arm, elbow, forearm, wrist and believable thumb/fingers. "
        "Near/far arms stay distinct; no fixed copied grip coordinate, no invented identical socket, no technical dots/axes. "
        "Near glove may naturally close around an invisible later handle, but never force it to an old socket or copy an old hand. "
        "Actual grip/axis, body contacts, crown and module occlusion are unknown until generated pixels are measured. "
        "Native actor translation is external; do not draw floor, trails, shadows, displaced duplicates, dust, glow or speed effects. "
        "Do not attach old v006 body art, canonical131 original sheet or any alternate identity. "
    )
    states = {}
    timing = {}
    for state, seq in phases.items():
        count, fps = len(seq), 5 if state == "death" else 10
        duration = 1. / fps
        order = " ".join(f"Pose {i}: {pose}." for i, pose in enumerate(seq))
        extra = {
            "dodge": "This is one guarded evasive slip, not a somersault. Facing stays fixed while native MoveIntent may move forward, backward or along depth; keep horizontal lean modest and do not bake a single world travel vector. No art easing changes native 462.5 world speed. Blocked native dodge still lasts its original .40 seconds; art does not fake movement past a wall.",
            "hurt": "This is actual nonlethal player poise-break Hurt, not every hit. Native Hurt is .40 seconds and must not loop. A normal accepted HP-loss HitFlash is separate and does not authorize this action.",
            "death": "A nonloop articulated collapse, not a rotated standing cutout. The final fifth corpse starts at .80 seconds and holds until state changes. There is no .80 gameplay death deadline. Keep a natural near hand suitable for a later measured retained-weapon grip; do not paint a dropped weapon or imply an inventory drop. Corpse orientation is body pose only and never moves the actor root.",
        }[state]
        states[state] = {"frames": count, "fps": fps, "loop": False,
                         "action": common_action + extra + " Exact ordered pose progression: " + order}
        slots = []
        for index, pose in enumerate(seq):
            start = index * duration
            slots.append({"frame": index, "art_key_age_seconds": round(start, 8),
                          "display_end_exclusive_seconds": None if state == "death" and index == count - 1 else round(start + duration, 8),
                          "pose_semantics": pose,
                          "actual_source_png": None, "actual_png_sha256": None,
                          "actual_floor_contact": None, "actual_body_support_contacts": None,
                          "actual_root_px": None, "actual_crown_px": None,
                          "actual_near_grip_px": None, "actual_grip_axis_xy": None,
                          "actual_hand_replay_mask": None, "actual_armor_attachment_px": None})
        timing[state] = {"count": count, "fps": fps, "loop": False, "frames": slots}
        guide = {"schema": "standard-layout-guide-text-recipe-v001", "state": state,
                 "purpose": "Count/spacing/safe padding only; no measured skeleton/foot/grip points",
                 "raster_status": "NOT_GENERATED; Root may run deferred standard draw_guide then E-retain before View",
                 "standard_draw_guide_call": {"state": state, "frames": count, "motion_phase_guides": False},
                 "canvas_px": [512 * count, 512], "cells": [
                     {"frame": i, "rect": [i * 512, 0, 512, 512],
                      "safe_inner_rect": [i * 512 + 48, 48, 416, 416],
                      "meaning": slots[i]["pose_semantics"]} for i in range(count)],
                 "does_not_establish_actual_floor_or_root": True}
        write(f"references/layout-guides/{state}.guide.json", guide)
    request = {"version": 1, "kind": "sprite-gen-request", "engine": "component-row",
               "character": {"id": "fairytale-clock-hero-body-states-v001",
                             "description": "The exact currently accepted body-only SwordReady v002 frame0 identity, fixed native right three-quarter view; common bare grey/charcoal cloth body and original brown gloves/boots",
                             "base_image": None},
               "cell": {"shape": "square", "width": 512, "height": 512,
                        "safe_margin_x": 48, "safe_margin_y": 48, "size": 512, "safe_margin": 48},
               "chroma_key": {"name": "green", "hex": "#00FF00", "rgb": [0, 255, 0], "selection": "manual_measured_against_current_opaque_anchor"},
               "states": states, "style": "EXACT accepted current SwordReady v002 hand-inked grotesque dark-fairytale squat clock/bell-helmet identity; body-only no weapons/armor, not pixel art, no style redesign",
               "motion_phase_guides": False, "layout": "taxonomy/v1",
               "fit": {"pixel_unfake": False, "resample": "lanczos", "align_x": "bbox-center",
                       "align_y": "bottom", "ground_frames": False, "segmentation": "components", "shared_row_scale": True}}
    assert normalize_states(states) == states
    write("sprite-request.json", request)
    for state, entry in states.items():
        write(f"prompts/{state}.txt", row_prompt(request, state, entry).rstrip() + "\n")
    write("runtime-timing-annotations-v001.json", {
        "schema": "hero-state-body-art-timing-v001", "status": "PROPOSED_ART_SAMPLING_NO_RUNTIME_IMPLEMENTATION",
        "accepted_input_scope": "Root authorized 4/.40 Dodge, 4/.40 Hurt, 5 with .80 corpse onset; media not generated or accepted",
        "states": timing,
        "dodge_authority": {"duration_seconds": .40, "distance_world": 185., "speed_world_per_second": 462.5,
                            "direct_iframe_start_inclusive": .06, "direct_iframe_end_exclusive": .20,
                            "cooldown_seconds": 1.20, "block_does_not_end_action": True,
                            "interruptions": ["real PoiseBreak outside protected interval", "Death"],
                            "sample_clock": "actual GetDodgeState.Time - accepted Record.Start; phase selects action",
                            "move_direction": "actual normalized MoveIntent, or Facing fallback only when intent zero; Facing is not changed by TryBeginDodge"},
        "hurt_authority": {"duration_seconds": .40, "trigger": "actual accepted direct poise break for living player",
                           "ordinary_positive_hp_loss": "HitFlash .22, no automatic Hurt interrupt",
                           "nonlethal_damage_over_time": "no new hurt/poise/push", "lethal_direct_or_dot": "Death",
                           "sample_clock": "public actual AnimationName/hurt + AnimationTime; state transition wins at endpoint"},
        "death_authority": {"gameplay_deadline_seconds": None, "art_final_pose_starts_seconds": .80,
                            "final_pose_holds": "until restart/install/restore changes real state",
                            "sample_clock": "actual AnimationTime advanced by terminal presentation even while SimulationTime freezes",
                            "no_new_combat_or_resource_tick": True,
                            "body_collision": "Death excluded from new combat/live-body admission; no collision mutation proposed here",
                            "world_root_and_inventory_drop": "no mutation; final weapon attachment awaits actual measured grip/occlusion"},
        "design_display_pivot_px": [256, 464], "pivot_role": "Current authored display pivot, NOT measured physical floor or foot contact",
        "all_actual_markers_status": "NULL until actual source pixels + measured registration + Root review",
        "SDK_timing_boundary": "Only integer fps/frames/loop in request; no durations_ms key that prepare silently drops or compose ignores. Death five frames @5fps preview has finite 1s, while runtime proposal holds fifth from .8 indefinitely."})
    legacy = json.loads((HERE.parent / "legacy-state-reference-inventory-v001.json").read_text(encoding="utf-8"))
    old_refs = [row for row in legacy["frames"] if row["action"] in ("dodge", "hurt", "death")]
    source_files = ["DungeonDodge.h", "DungeonFighter.cpp", "DungeonGameMode.cpp", "DungeonHUD.cpp", "DungeonFairytaleSwordPresentation.cpp", "DungeonFairytaleSwordEquipmentBinding.cpp"]
    files = [{"role": "SOLE_CURRENT_ACCEPTED_DIRECTION_IDENTITY", "file": anchor_pin}]
    paths = [manifest, anchor.parent.parent / "sprite-request.json",
             root / "fairytale-sword-v001/generation-control-v001/generation-receipt158-v001.json",
             root / "fairytale-sword-v001/ready-extraction-v002/extracted-freeze-v001.json",
             HERE.parent / "audit-freeze-v001.json", HERE.parent / "exact-v128-source-content-pins-v001.json",
             HERE.parent / "equipment20-boundary-v001.json",
             root / "fairytale-hero-v001/sprite-run-idle-v002/curated/frame-0.png",
             PROJECT / "tools/scripts/extract-sprite-shared-row-scale.py",
             SKILL / "SKILL.md", SKILL / "sprite_gen/gen/prepare.py", SKILL / "sprite_gen/frames/extract.py",
             SKILL / "docs/states-and-frames.md", SKILL / "docs/directional-anchor-workflow.md",
             SKILL / "docs/layer-tracks.md", SKILL / "docs/chroma-alpha.md",
             SKILL / "sprite_gen/compose/compose_atlas.py"]
    paths += [PROJECT / "UnrealGame/Source/CodexDungeon" / name for name in source_files]
    for path in paths:
        files.append({"role": "READ_ONLY_CONTRACT_OR_LINEAGE_NOT_A_MODEL_IMAGE_REFERENCE", "file": pin(path)})
    for row in old_refs:
        actual = pin(Path(row["source"]["path"]))
        assert actual == row["source"]
        files.append({"role": "OLD_V006_TIMING_ONLY_NEVER_ATTACH_AS_IDENTITY_OR_BODY", "file": actual})
    write("reference-pins-v001.json", {"schema": "hero-state-input-reference-pins-v001",
          "identity_anchor": anchor_pin, "identity_geometry": anchor_geometry,
          "sole_model_identity_reference": anchor.as_posix(),
          "approval_provenance": "Parent Root explicitly authorized current accepted SwordReady v002 frame0 in this task; current v128 import manifest independently pins the same source",
          "old_canonical131_lineage_attachment": False, "old_v006_model_attachment": False,
          "green_key_min_opaque_subject_distance": green_min_distance,
          "minimum_hard_erase_distance_required": 96, "files": files})
    write("direction-and-modules-v001.json", {"schema": "hero-state-direction-modular-scope-v001",
          "first_generated_direction": "native_right_same_accepted_three_quarter_view",
          "unique_identity_image": anchor_pin, "left_generation_requests": 0,
          "left_plan": "Current runtime mirror once, after right body motion + actual measured modules are accepted; mirror body, Root/Grip/Axis, masks and all equipment together. Near/far anatomical roles remain owned; do not mirror twice or swap labels.",
          "left_art_acceptance": False,
          "if_mirror_fails": "Root records the exact defect, then separately approves left direction anchor/paired row; right row supplies timing only, never left identity",
          "dodge_move_vectors": "Forward, backward and depth/diagonal are actual legal native routes; first row is a compact direction-neutral slip. All vectors remain visual QA obligations, especially real opposite-facing Shift proof.",
          "body_scope": "Common bare cloth body; no weapon, armor, fixed old grip or baked equipment",
          "candidate_components_after_pixels_exist": ["BodyRest", "NearArmWithoutHand", "HelmetForeground if actual depth requires", "NearHand", "separate weapon", "separate far shoulder", "separate chest", "separate near shoulder"],
          "module_data_required": ["actual source/decoded RGBA pins", "exclusive body partitions with no double pixels", "actual Root/Crown/support contacts", "actual NearGrip/Axis and original-pixel hand replay mask", "pose-specific chest/shoulder attachment/depth masks", "mirrored registration/overlap proof"],
          "first_runtime_slice_proposal": "SWD + None/LGT, only after actual new source and modules exist; current partial Binding remains untouched",
          "equipment_20": {"weapons": ["WPN-SWD-001", "WPN-GSW-001", "WPN-SPR-001", "WPN-XBW-001", "WPN-STF-001"],
                           "armors": ["ARM-LGT-001", "ARM-MED-001", "ARM-HVY-001", "ARM-ROB-001"],
                           "cells": 20, "NoArmor_outside_20": True, "all_state_art_accepted": 0,
                           "current_partial_cell": "SWD+LGT ground Ready/Walk/P1/P2/P3 only",
                           "body_reuse_is_not_20_support": True,
                           "missing_per_family": "GSW two-hand silhouette, SPR shaft grip, XBW two-hand/reload, STF spell grip and actual family actions; MED/HVY plate silhouettes and ROB sleeves/cloth need actual authored modules. Do not stretch existing LGT or remove Binding validation to claim support."}})
    write("handoff-v001.json", {"schema": "hero-state-standard-text-input-handoff-v001",
          "status": "TEXT_READY_STANDARD_GUIDE_RASTERS_PENDING_ROOT_PREPARE_AND_E_RETENTION",
          "generation_calls": 0, "Source_changes": 0, "UE_calls": 0, "new_media_viewed": False,
          "numeric_SSoT": (HERE / "sprite-request.json").as_posix(),
          "timing_contract": (HERE / "timing-contract-v001.py").as_posix(),
          "rows": [{"state": state, "frame_count": entry["frames"], "fps": entry["fps"], "loop": False,
                    "prompt": (HERE / "prompts" / (state + ".txt")).as_posix(),
                    "guide_recipe": (HERE / "references/layout-guides" / (state + ".guide.json")).as_posix(),
                    "model_refs_in_order_after_Root_prepare": [anchor.as_posix(), "NEW_BATCH/references/layout-guides/" + state + ".png"],
                    "raw_output_after_Root_generation": "NEW_BATCH/raw/" + state + ".png",
                    "all_actual_source_floor_grip_markers": None} for state, entry in states.items()],
          "next_order": ["Root verifies text/pins in sprite-gen venv", "Root chooses NEW candidate process-batch path and runs deferred standard layout writer",
                         "Root E-retains guide originals and presentation/index before any View or generation attachment",
                         "Root generates each requested component row using exactly anchor + row guide and generated standard prompt; preserve original raw",
                         "Root uses pinned existing shared-row-scale extractor; never default per-frame fitting, slot fallback, cloned Ready or local redraw",
                         "Measure actual per-frame body contacts/Root/Grip/Axis/masks and rigid helmet/body scale against accepted anchor; reject identity drift/cropping",
                         "Root E-retains actual extracted/preview media before View; review right, mirrored left and native opposite-facing Shift",
                         "Only then plan modular armor/weapon adaptation + minimal real native RED/Source implementation; no import or runtime profile is configured here"],
          "E_retention_root": "E:/OurGame/Knight/过程图稿与视频",
          "F_process_batch_parent": (HERE / "process-batches").as_posix(),
          "unconfigured": ["new PNGs and SHA", "real source floor/support", "Root/Grip/Axis/masks", "pose-specific LGT/new armor modules", "texture object paths/runtime label/profile version"],
          "not_complete": "No new visual generation, native actual playback, all-state72 acceptance or 20-combination art acceptance"})
    print(json.dumps({"text_candidate_dir": HERE.as_posix(), "row_frames": {s: e["frames"] for s, e in states.items()},
                      "identity": anchor_pin, "new_images_written": 0, "AI_called": False, "UE_called": False}, ensure_ascii=False))


if __name__ == "__main__":
    main()
