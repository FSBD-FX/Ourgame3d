"""Unapplied combo-only proof tooling. Root capture/technical verification only.
Original Source, native PNGs, clocks and original RGBA stay unchanged; no art acceptance.
"""
from pathlib import Path
import argparse, hashlib, json, math, os, subprocess, zlib
from urllib.parse import quote
import imageio_ffmpeg
import numpy as np
from PIL import Image
ROOT = Path("F:/Ourgame").resolve()
CLIPS = ("Ready", "Primary1", "Primary2", "Primary3")
COMPONENTS = ("Chest", "ShoulderNear", "ShoulderFar")
NEW_NS = {"Ready":"/Game/Production/ArtTrials/EV048/v012/HeroLeatherReady/", "Primary1":"/Game/Production/ArtTrials/EV048/v013/HeroLeatherPrimary1/", "Primary2":"/Game/Production/ArtTrials/EV048/v014/HeroLeatherPrimary2/", "Primary3":"/Game/Production/ArtTrials/EV048/v015/HeroLeatherPrimary3/"}
OLD_NS = {"Ready":"/Game/Production/ArtTrials/EV048/v006/HeroSwordArmorReady/", "Primary1":"/Game/Production/ArtTrials/EV048/v007/HeroSwordArmorPrimary1/", "Primary2":"/Game/Production/ArtTrials/EV048/v010/HeroSwordPrimary2Armor/", "Primary3":"/Game/Production/ArtTrials/EV048/v011/HeroSwordPrimary3/"}
BODY_NS = {"Ready":"/Game/Production/ArtTrials/EV048/v005/HeroSwordBody/", "Primary1":"/Game/Production/ArtTrials/EV048/v005/HeroSwordBody/", "Primary2":"/Game/Production/ArtTrials/EV048/v009/HeroSwordPrimary2/", "Primary3":"/Game/Production/ArtTrials/EV048/v011/HeroSwordPrimary3/"}
SWORD = "/Game/Production/FirstBatch/v002/CandidateComponents/T_military_sword_v002.T_military_sword_v002"
CANVAS = 72. * 512. / 416.
PHASES = ["start", "baseline_no_armor", "light_pending_cancel", "light_canceled", "light_pickup_commit", "light_ready", "light_three_stage"]
NATIVE_NAMES = ("DungeonFairytaleSwordPresentation.cpp", "DungeonFairytaleSwordPrimary2ArmorV001.inl", "DungeonFairytaleSwordPrimary3V001.inl", "DungeonFairytaleEquipmentBoundProbe.h", "DungeonFairytaleEquipmentBoundProbe.cpp")
TOOL_FILES = ("capture-leather-combo-trial-v001.ps1", "postprocess-leather-combo-trial-v001.py", "verify-leather-combo-proof-v001.py", "verify-native-bound-capture-pixels-v001.py")
COMBO_SCOPE = 'Opt-in soft-leather combo-only trial: normal Enter/E/A cancel/E single actual LGT commit, normal J three-stage chain, actual post-chain Ready, native chain expiry, normal opposite direction, second fresh normal J three-stage chain and final actual Ready. Six actual distinct attack IDs, each facing/stage mask63; original body layers plus matching new3 armor per clip. No forced pose/frame/clock/gear or invented phase counters. QA registered source is not lawful loot/shop/reward. No full unit, all actions, armor compatibility, complete equip animation, grasp/clearance, audio or Save acceptance. Default proof remains separate.'

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


def expected_stack(frame, stage=-1):
    clip = "Ready" if stage < 0 else "Primary" + str(stage + 1)
    components = ["BodyRest", "ShoulderFar", "Chest", "NearArmWithoutHand", "ShoulderNear"]
    if stage >= 0: components.append("HelmetForeground")
    components.append("NearHand")
    result = []
    for component in components:
        if component == "NearHand": result.append(SWORD)
        armor = component in COMPONENTS
        result.append(object_path(NEW_NS[clip] if armor else OLD_NS[clip], f"T_Fairytale_{'Leather' if armor else 'Sword'}{clip}{component}_{frame:03d}_v001"))
    return result

def body_path(clip, frame):
    name = f"T_Fairytale_Sword{clip}{'Body' if clip == 'Primary3' else ''}_{frame:03d}_{'v001' if clip == 'Primary3' else 'v002'}"
    return object_path(BODY_NS[clip], name)

def identifier(value, label, allow_zero=False):
    require(isinstance(value,str) and value.isascii() and value.isdigit() and str(int(value)) == value and (0 if allow_zero else 1) <= int(value) <= 2**64-1, "Invalid canonical native ID: " + label)
    return int(value)

def pin_path(pin, label, snapshot_rows=None):
    require(isinstance(pin, dict) and {"path", "bytes", "sha256"} <= set(pin), "Missing exact " + label + " pin")
    path = (ROOT / pin["path"]).resolve()
    require(path.is_relative_to(ROOT) and type(pin["bytes"]) is int and pin["bytes"] > 0 and isinstance(pin["sha256"], str) and len(pin["sha256"]) == 64, "Unsafe/invalid " + label + " pin")
    same_pin(path, pin)
    if snapshot_rows is not None:
        key = path.relative_to(ROOT).as_posix()
        require(key in snapshot_rows and snapshot_rows[key]["bytes"] == pin["bytes"] and snapshot_rows[key]["sha256"] == pin["sha256"], label + " is not a frozen compiled input")
    return path


def check_automation(automation, expected):
    count, names = expected["expected_count"], expected["full_test_paths"]
    require(type(count) is int and count >= 157 and isinstance(names, list) and len(names) == len(set(names)) == count and all(isinstance(name, str) and name for name in names), "Explicit current complete test-name set/count invalid")
    tests = automation["tests"]
    require(automation["succeeded"] == len(tests) == count and {row["fullTestPath"] for row in tests} == set(names), "Current automation differs from explicit frozen full test-name set")
    require(all(automation.get(key, 0) == 0 for key in ("failed", "succeededWithWarnings", "notRun", "inProcess")), "Current full suite incomplete or RED")
    require(all(row["state"] == "Success" and row["errors"] == row["warnings"] == 0 for row in tests), "Current full suite entries not clean Success")
    return count


def verify_sources(snapshot, index):
    manifest_path = snapshot / "compiled-source-manifest.json"
    manifest = read(manifest_path)
    require(index["source_manifest_SHA256"] == desc(manifest_path)["sha256"] and (ROOT / index["snapshot"]).resolve() == snapshot, "Capture/snapshot binding differs")
    rows = manifest["files"]; by_path = {row["path"]: row for row in rows}
    require(len(rows) == len(by_path) > 0 and manifest["mismatches"] == 0, "Empty/duplicate/unclean current snapshot")
    for row in rows:
        relative = Path(row["path"])
        require(not relative.is_absolute() and ".." not in relative.parts and relative.as_posix() == row["path"], "Unsafe/noncanonical snapshot path")
        for base in (ROOT, snapshot):
            path = (base / relative).resolve(); require(path.is_relative_to(base), "Snapshot path escapes root"); same_pin(path, row)
    for prefix in ("UnrealGame/Source/", "UnrealGame/Config/", "UnrealGame/Content/Production/"):
        actual = {path.relative_to(ROOT).as_posix() for path in (ROOT / prefix).rglob("*") if path.is_file()}
        require(actual == {key for key in by_path if key.startswith(prefix)}, "Current snapshot omits/invents inputs: " + prefix)
    require("UnrealGame/Binaries/Win64/UnrealEditor-CodexDungeon.dll" in by_path, "Current compiled DLL missing")
    for name in TOOL_FILES:
        require("tools/scripts/" + name in by_path, "Combo tool absent from frozen inputs: " + name)
    same_pin(Path(__file__), by_path["tools/scripts/postprocess-leather-combo-trial-v001.py"])
    contract_path = pin_path(manifest.get("combo_proof_contract"), "combo_proof_contract", by_path)
    contract = read(contract_path)
    require(contract["schema"] == "leather-combo-runtime-proof-contract-v001" and contract["template_only"] is False, "Concrete Root-filled combo runtime contract required")
    require(contract["scope"] == "Ready/P1/P2/P3 matching leather, normal two-facing six-attack proof only", "Wrong runtime contract scope")
    base_path = pin_path(contract["base_snapshot_manifest"], "historical v125 baseline", by_path)
    base = read(base_path)
    old = {row["path"]: row for row in base["files"] if row["path"].startswith("UnrealGame/Content/Production/")}
    production = {key: row for key, row in by_path.items() if key.startswith("UnrealGame/Content/Production/")}
    expected = contract["production"]
    require(len(old) == base["production_packages"] == expected["baseline_count"] == 1115, "Historical v125 old1115 baseline differs")
    require(all(production.get(key) == row for key, row in old.items()), "Historical old1115 package bytes changed")
    require(manifest["production_packages"] == len(production) == expected["expected_total"] and expected["new_packages"] == len(production) - len(old), "Current production count differs from explicit frozen contract")
    require(manifest["old_production_unchanged"] is True and manifest["old_production_packages"] == len(old) and manifest["new_production_packages"] == len(production) - len(old), "Snapshot production delta audit differs")
    native_freeze_path = pin_path(contract["native_source_freeze"], "combo native source freeze", by_path)
    native_freeze = read(native_freeze_path)
    source_candidates = {Path(item["path"]).name: item for item in native_freeze["files"] if Path(item["path"]).resolve().parent == native_freeze_path.parent and Path(item["path"]).name in NATIVE_NAMES}
    require(set(source_candidates) == set(NATIVE_NAMES), "Combo native source freeze missing five production candidates")
    for name, pin in source_candidates.items():
        key = "UnrealGame/Source/CodexDungeon/" + name
        require(key in by_path and by_path[key]["bytes"] == pin["bytes"] and by_path[key]["sha256"] == pin["sha256"], "Current native Source is not exact combo candidate: " + name)
        pin_path(pin, "native source candidate " + name, by_path)
    # Parallel Guard work is allowed when its exact current changes are explicit.
    base_code = {row["path"]: row for row in base["files"] if row["path"].startswith(("UnrealGame/Source/", "UnrealGame/Config/"))}
    current_code = {key: row for key, row in by_path.items() if key.startswith(("UnrealGame/Source/", "UnrealGame/Config/"))}
    require(set(base_code) <= set(current_code), "Historical Source/Config was removed without a new contract")
    native_keys = {"UnrealGame/Source/CodexDungeon/" + name for name in NATIVE_NAMES}
    changed = {key for key, row in current_code.items() if base_code.get(key) != row} - native_keys
    additions = contract["additional_source_pins"]
    require(len({item["path"] for item in additions}) == len(additions) and {item["path"] for item in additions} == changed, "Current non-combo Source changes need explicit additional_source_pins")
    for item in additions: pin_path(item, "additional current Source", by_path)
    report_path = pin_path(contract["current_automation"]["report"], "current full automation report", by_path)
    count = check_automation(read(report_path), contract["current_automation"])
    require((ROOT / manifest["current_automation_report"]).resolve() == report_path and manifest["current_automation_succeeded"] == count and len(manifest["actual_expected_test_names"]) == count and set(manifest["actual_expected_test_names"]) == set(contract["current_automation"]["full_test_paths"]), "Current snapshot/report/test-name contract differs")
    require(set(contract["assemblies"]) == set(CLIPS), "All four assembly source freezes required")
    assembly_sources, assembly_members = [], {}
    for clip, pin in contract["assemblies"].items():
        path = pin_path(pin, clip + " assembly freeze", by_path); assembly = read(path)
        require(assembly["files"] and len({item["path"] for item in assembly["files"]}) == len(assembly["files"]), "Empty/duplicate assembly source freeze")
        assembly_members[clip] = set()
        for item in assembly["files"]:
            relative = Path(item["path"]); source = (path.parent / relative).resolve()
            require(not relative.is_absolute() and ".." not in relative.parts and source.is_relative_to(path.parent), "Unsafe assembly source path")
            current = desc(source); require(current["bytes"] == item["bytes"] and current["sha256"] == item["sha256"], "Assembly source bytes changed")
            pin_path(current, clip + " assembly member", by_path)
            assembly_members[clip].add(source); assembly_sources.append(current)
    imports = contract["imports"]
    require(set(imports) == set(CLIPS), "All four Ready/P1/P2/P3 import pins are required")
    require(imports["Ready"] == base["ready_production_import_receipt"] and imports["Primary1"] == base["new_production_import_receipt"], "Historical actual Ready/P1 receipt pins changed")
    receipt_groups = {}
    for clip, pin in imports.items():
        path = pin_path(pin, clip + " import receipt", by_path)
        receipt_groups.setdefault(path, []).append(clip)
    new_packages, rgba_sources, receipts = set(), [], []
    for path, clips in receipt_groups.items():
        imported = read(path); assets = imported["assets"]
        expected_objects = {object_path(NEW_NS[clip], f"T_Fairytale_Leather{clip}{component}_{frame:03d}_v001") for clip in clips for component in COMPONENTS for frame in range(4 if clip == "Ready" else 6)}
        require(imported["success"] is True and imported["actual_count"] == imported["saved_count"] == imported["expected_count"] == len(assets) == len(expected_objects), "Actual import did not save its full explicit stage set")
        require({asset["object_path"] for asset in assets} == expected_objects, "Receipt object set differs from its referenced clip namespaces")
        for asset in assets:
            clip = next(clip for clip in clips if asset["object_path"].startswith(NEW_NS[clip]))
            require(type(asset["frame"]) is int and asset["component"] in COMPONENTS and asset["actual_object_type"] == "Texture2D", "Actual imported component/frame/type invalid")
            require(asset["object_path"] == object_path(NEW_NS[clip], f"T_Fairytale_Leather{clip}{asset['component']}_{asset['frame']:03d}_v001"), "Imported object metadata differs")
            source = Path(asset["source"]).resolve(); require(source.is_relative_to(ROOT / "source-assets/production") and source in assembly_members[clip], "RGBA import source outside corresponding frozen assembly")
            same_pin(source, {"bytes": asset["source_bytes"], "sha256": asset["source_sha256"]})
            with Image.open(source) as image: require(image.format == "PNG" and image.mode == "RGBA" and image.size == (512, 512), "Original import source is not untouched512 RGBA")
            rgba_sources.append(desc(source)); package = package_file(asset["object_path"])
            require(package in production and production[package]["bytes"] == asset["saved_bytes"] and production[package]["sha256"] == asset["saved_sha256"], "Actual package/receipt bytes differ")
            if clip in ("Primary2", "Primary3"):
                require(package not in old, "New leather stage overwrites historical package"); new_packages.add(package)
        receipts.append(desc(path))
    require(len(new_packages) == expected["new_packages"] == 36 and new_packages == set(production) - set(old) and expected["expected_total"] == expected["baseline_count"] + len(new_packages), "Current new package delta is not exact receipted P2/P3 set")
    return manifest, by_path, {"snapshot": snapshot.as_posix(), "snapshot_files": len(rows), "source_endpoint_checks": 2 * len(rows), "source_mismatches": 0,
        "runtime_proof_contract": desc(contract_path), "base_snapshot_manifest": desc(base_path), "native_source_freeze": desc(native_freeze_path),
        "production_packages": len(production), "old_production_packages_unchanged": len(old), "new_receipted_P2_P3_packages": len(new_packages),
        "current_full_automation_succeeded": count, "actual_complete_test_names": sorted(contract["current_automation"]["full_test_paths"]),
        "actual_import_receipts": receipts, "original_RGBA_source_pins": rgba_sources, "assembly_source_pins": assembly_sources,
        "explicit_additional_source_count": len(additions), "source_and_DLL_unchanged_during_proof": True, "formal_complete_units": 0}


def verify_flow(report, index, package_rows):
    require(report["schema"] == "fairytale-equipment-bound-native-flow-v1" and report["leather_combo_only_trial"] is True and report["leather_primary1_only_trial"] is False and report["leather_ready_only_trial"] is False, "Only explicit combo-only native flow accepted")
    require(report["scope"] == COMBO_SCOPE and report["passed"] is True and report["flow_complete"] is True and report["reason"] == report["failure"] == "" and report["mismatches"] == [], "Native combo flow not clean or wrong scope")
    require(index["runtime_passed"] is True and index["exit_code"] == 0 and report["formal_complete_units"] == 0 and report["silent_video"] is True and report["audio_recorded"] is False and report["native_async_capture_writes_flushed"] is True, "Native process/flush/silent/acceptance contract differs")
    require(report["capture_timing"]["use_fixed_time_step"] is False and all(report.get(key, False) is False for key in ("forced_pose", "forced_frame", "forced_clock", "direct_gear_writes", "fake_attack_ids", "simulation_pacing_changed")), "Fixed or forced/fake proof forbidden")
    require(report["leather_combo_masks_left_right_by_stage"] == [[63, 63, 63], [63, 63, 63]] and report["light_primary_phase_masks"] == [63, 63, 63] and report["leather_ready_phase_masks_left_right"] == [0, 0] and report["leather_primary1_masks_left_right"] == [0, 0], "Combo native masks differ")
    first_side = report["leather_combo_first_side"]
    require(type(first_side) is int and first_side in (0, 1) and report["leather_combo_normal_turn_requested"] is True and report["leather_combo_second_sequence_normal_J_requested"] is True, "Actual first side/normal second-sequence requests missing")
    require(all(identifier(report[key], key, True) == 0 for key in ("medium_instance_id", "medium_source_id", "original_light_drop_source")), "Combo-only entered medium/drop flow")
    light = identifier(report["light_instance_id"], "light_instance_id"); identifier(report["light_source_id"], "light_source_id")
    ids = report["leather_combo_attack_ids_left_right_by_stage"]
    require(isinstance(ids, list) and len(ids) == 2 and all(isinstance(side, list) and len(side) == 3 for side in ids), "Need two by three actual attack IDs")
    actual_ids = [[identifier(value, "actual stage ID") for value in side] for side in ids]
    require(len({value for side in actual_ids for value in side}) == 6 and all(side[0] < side[1] < side[2] for side in actual_ids), "Six distinct increasing actual stage IDs required")
    obs = report["observations"]; duration = report["duration_s"]
    require(obs and index["observations"] == len(obs) and finite(duration) and duration > 0, "Observation count/duration invalid")
    inputs = report["normal_input_requests"]
    require(inputs == report["inputevents"], "Input aliases differ")
    downs = [row for row in inputs if row["down"] is True]; keys = [row["key"] for row in downs]
    require(len(keys) == 11 and keys[:7] == ["Enter", "E", "A", "E", "J", "J", "J"] and keys[7] in ("A", "D") and keys[8:] == ["J", "J", "J"], "Normal Enter/E/A/E/J3/turn/J3 input order differs")
    held = set(); prior_wall = -1.; prior_sim = -1.
    for row in inputs:
        require(row["key"] in ("Enter", "E", "A", "D", "J") and type(row["down"]) is bool and finite(row["wall_offset_s"]) and prior_wall <= row["wall_offset_s"] <= duration and finite(row["sim"]) and row["sim"] >= prior_sim, "Input key/clock/order invalid")
        require((row["key"] not in held and not held) if row["down"] else row["key"] in held, "Unpaired/overlapping normal input")
        if row["down"]: held.add(row["key"])
        else: held.remove(row["key"])
        prior_wall, prior_sim = row["wall_offset_s"], row["sim"]
    require(not held, "Capture ended with held key")
    phases = report["phasechecks"]
    require([(row["step"], row["phase"]) for row in phases] == list(enumerate(PHASES)), "Unexpected phase transitions")
    require(all(finite(row["sim"]) and finite(row["wall_offset_s"]) and 0 <= row["wall_offset_s"] <= duration for row in phases) and all(b["sim"] >= a["sim"] and b["wall_offset_s"] >= a["wall_offset_s"] for a, b in zip(phases, phases[1:])), "Phase clocks invalid/rewound")
    require(phases[0]["sim"] >= downs[0]["sim"] and phases[0]["wall_offset_s"] >= downs[0]["wall_offset_s"], "Start precedes Enter")
    for phase, request in ((1, 1), (2, 2), (3, 3), (5, 4)):
        require(phases[phase]["sim"] == downs[request]["sim"] and phases[phase]["wall_offset_s"] >= downs[request]["wall_offset_s"], "Phase not paired to actual normal request")
    first, last = obs[0], obs[-1]
    fields = ("run", "run_alias", "owner_id", "committed_weapon_id", "committed_weapon_version", "active_slot")
    constant = tuple(first[key] for key in fields)
    require(isinstance(constant[0], str) and len(constant[0]) == 32 and all(c in "0123456789abcdef" for c in constant[0]) and int(constant[0], 16) > 0, "Native run GUID missing")
    for key, value in zip(fields[1:5], constant[1:5]): identifier(value, key)
    require(type(constant[5]) is int and constant[5] in (0, 1), "Active slot invalid")
    initial_ops = identifier(first["operation_count"], "operations", True); initial_next = identifier(first["next_operation_id"], "next operation")
    require(identifier(last["operation_count"], "final operations", True) == initial_ops + 1 and identifier(last["next_operation_id"], "final next operation") == initial_next + 1, "Exactly one actual LGT commit required")
    selected, attacks = {}, {}; masks = {(side, stage): 0 for side in range(2) for stage in range(3)}
    ready_counts = [0, 0]; seen_steps, versions, pending_steps = set(), set(), set(); deadlines = {}
    last_draw = identifier(first["draw_id"], "draw ID") - 1; last_ops = initial_ops; last_wall = -1.; last_sim = -1.; last_step = -1
    for i, row in enumerate(obs):
        require(tuple(row[key] for key in fields) == constant, "Run/owner/sword/version/slot changed")
        step = row["flow_step"]
        require(type(step) is int and step in range(7) and step >= last_step and row["flow_phase"] == PHASES[step], "Flow step/phase differs or rewinds")
        seen_steps.add(step); last_step = step
        require(row["active"] is True and row["texture_ready"] is True and row["interface_visible"] is False and row["text_calls"] == 0, "Readiness/UI-off differs")
        require(finite(row["canvas_size"]) and math.isclose(row["canvas_size"], CANVAS, rel_tol=0., abs_tol=1e-9) and row["body_max_contract"] == 72, "Native body72/canvas changed")
        require(finite(row["sim"]) and finite(row["actual_sim"]) and math.isclose(row["sim"], row["actual_sim"], rel_tol=0., abs_tol=1e-9) and row["actual_sim"] >= last_sim and finite(row["wall_offset_s"]) and last_wall < row["wall_offset_s"] < duration, "Native/draw/event clocks differ")
        last_wall, last_sim = row["wall_offset_s"], row["actual_sim"]
        require(row["wall_offset_s"] <= phases[step]["wall_offset_s"] and row["actual_sim"] <= phases[step]["sim"] and (step == 0 or (row["wall_offset_s"] >= phases[step-1]["wall_offset_s"] and row["actual_sim"] >= phases[step-1]["sim"])), "Observation outside actual phase interval")
        require(type(row["facing"]) is int and row["facing"] in (-1, 1) and type(row["frame"]) is int and type(row["stage"]) is int and type(row["melee_pending_primary"]) is bool, "Native facing/frame/stage/pending invalid")
        require(row["weapon_mirror"] == "WPN-SWD-001" and row["clip"] in ("sword_ready_idle", "sword_primary_1", "sword_primary_2", "sword_primary_3"), "Unsupported weapon/clip")
        draw = identifier(row["draw_id"], "draw ID"); require(draw > last_draw, "Draw ID rewind"); last_draw = draw
        ops = identifier(row["operation_count"], "operations", True)
        require(ops in (initial_ops, initial_ops+1) and ops >= last_ops and identifier(row["next_operation_id"], "operation cursor") == initial_next + ops - initial_ops, "Actual operation cursor differs"); last_ops = ops
        armor = identifier(row["committed_armor_id"], "armor", True)
        require(armor in (0, light) and ((step >= 5) == (armor == light) if step != 4 else True), "Committed armor differs from single cancel/commit flow")
        require(row["expected_armor_mode"] == ("light_armor" if armor else "no_armor") and row["armor_mirror"] == ("ARM-LGT-001" if armor else ""), "Committed armor mirror/mode differs")
        if armor:
            versions.add(identifier(row["committed_armor_version"], "armor version")); require(ops == initial_ops+1, "Armor drawn before commit")
        else: require(identifier(row["committed_armor_version"], "empty armor version", True) == 0 and ops == initial_ops, "Empty armor version/operation differs")
        pending = row["pending_equipment_action"] is True and row["pending_equipment_kind"] == 2 and row["animation"] == "equip_armor"
        require(type(row["supported"]) is bool and pending == row["committed_gear_placeholder_expected"], "Pending placeholder derived expectation differs")
        if pending:
            require(row["supported"] is False and row["frame"] == 0 and identifier(row["pending_instance_id"], "pending target") == light and finite(row["equipment_deadline"]), "Pending pickup lies about support/target")
            if step in (2, 4): pending_steps.add(step); deadlines.setdefault(step, row["equipment_deadline"]); require(deadlines[step] == row["equipment_deadline"], "Pickup deadline changed")
        primary = row["clip"] != "sword_ready_idle"; stage = row["stage"]; side = 0 if row["facing"] < 0 else 1
        action = identifier(row["action_id"], "action", True)
        require((primary and step == 6 and stage in range(3) and row["frame"] in range(6) and row["clip"] == f"sword_primary_{stage+1}" and action > 0 and row["supported"] is True and not pending and armor == light)
                or (not primary and stage == -1 and row["frame"] in range(4) and action == 0 and row["melee_pending_primary"] is False), "Actual stage/clip/frame/action not valid combo or Ready")
        clip = "Primary" + str(stage+1) if primary else "Ready"; body = body_path(clip, row["frame"])
        require(row["texture"] == body, "Original whole-body source selector changed")
        stack = row["draw_stack"]; require(isinstance(stack, list) and all(isinstance(path, str) for path in stack), "Draw stack invalid")
        has_armor = any("Shoulder" in path or "Chest" in path for path in stack)
        require(has_armor == row["draw_stack_has_armor"], "Stack metadata differs")
        gear = row["supported"] or pending
        if not gear: require(stack == [body] and row["armor_drawn"] is False and not has_armor and row["weapon"] == "", "Unsupported pose leaks gear")
        elif not armor: require(stack == [body, SWORD, body] and row["armor_drawn"] is False and not has_armor and row["weapon"] == SWORD, "Unarmored row substituted gear")
        else:
            require(row["armor_drawn"] is True and row["armor_ready"] is True and row["armor_preview"] is True and row["weapon"] == SWORD and stack == expected_stack(row["frame"], stage) and sum(path.startswith(NEW_NS[clip]) for path in stack) == 3, "Exact matching new3armor/oldbody/Sword stack differs")
        if gear: require(row["instance_id"] == row["committed_weapon_id"] and finite(row["weapon_scale"]) and math.isclose(row["weapon_scale"], .5, rel_tol=0., abs_tol=1e-12), "Independent sword identity/scale differs")
        for resource in set(stack + [body]): require(package_file(resource) in package_rows, "Actual drawn resource missing in snapshot")
        for key in ("root", "grip", "grip_screen"): require(isinstance(row[key], list) and len(row[key]) == 2 and all(finite(v) for v in row[key]), "Native crop marker invalid")
        if primary:
            times = tuple(row[key] for key in ("start", "active_at", "active_end", "end"))
            require(all(finite(t) for t in times) and times[0] < times[1] < times[2] < times[3] and times[0] <= row["actual_sim"] <= times[3], "Actual stage schedule invalid")
            require(action == actual_ids[side][stage], "Observed actual action differs from report side/stage ID")
            if action not in attacks: attacks[action] = {"side": side, "stage": stage, "times": times, "first": i, "last": i}; ready_counts[side] = 0
            entry = attacks[action]; require(entry["side"] == side and entry["stage"] == stage and entry["times"] == times, "Actual attack changed side/stage/times"); entry["last"] = i
            masks[(side, stage)] |= 1 << row["frame"]; selected.setdefault((row["facing"], stage, row["frame"]), i)
            if row["melee_pending_primary"]:
                request = downs[(5 if side == first_side else 9) + stage] if stage < 2 else None
                require(request is not None and row["actual_sim"] >= request["sim"] and row["wall_offset_s"] >= request["wall_offset_s"], "Queued primary not backed by this stage's normal recovery J")
        if armor and row["supported"]:
            expected_side = first_side if row["wall_offset_s"] < downs[7]["wall_offset_s"] else 1-first_side
            if not primary and step == 6 and row["pending_equipment_action"] is False and row["needs_slot_selection"] is False and row["animation"] == "idle" and side == expected_side and all(masks[(side, s)] == 63 for s in range(3)):
                require(row["actual_sim"] >= attacks[actual_ids[side][2]]["times"][3], "Ready counter before actual final action End"); ready_counts[side] += 1
            require(row["leather_combo_side"] == side and type(row["leather_combo_fresh_ready_seen_this_side"]) is int and row["leather_combo_fresh_ready_seen_this_side"] == ready_counts[side], "Native fresh Ready counter differs from independent actual observations")
    require(seen_steps == set(range(7)) and pending_steps == {2, 4} and all(value == 63 for value in masks.values()) and len(selected) == 36 and len(attacks) == 6, "Actual complete two-facing three-stage coverage missing")
    require(len(versions) == 1 and identifier(last["committed_armor_id"], "final armor") == light, "Actual LGT identity/version changed")
    require(downs[2]["sim"] >= deadlines[2]-.4 and downs[2]["sim"] < deadlines[2]-.08 and phases[3]["sim"] > deadlines[2]+.02, "Normal cancel outside actual pickup window")
    ordered = sorted(attacks.values(), key=lambda a: a["first"])
    require([(a["side"], a["stage"]) for a in ordered] == [(side, stage) for side in (first_side, 1-first_side) for stage in range(3)] and all(a["last"] < b["first"] for a, b in zip(ordered, ordered[1:])), "Actual side/stage sequence overlaps or differs")
    for side in range(2):
        chain = [attacks[actual_ids[side][stage]] for stage in range(3)]; requests = downs[4:7] if side == first_side else downs[8:11]
        require(requests[0]["sim"] <= chain[0]["times"][0] and requests[0]["wall_offset_s"] <= obs[chain[0]["first"]]["wall_offset_s"], "Fresh chain not backed by normal J")
        for stage in (1, 2):
            previous, current, request = chain[stage-1], chain[stage], requests[stage]
            require(current["times"][0] == previous["times"][3] and max(previous["times"][2], previous["times"][3]-.10) <= request["sim"] <= previous["times"][3] and obs[previous["first"]]["wall_offset_s"] <= request["wall_offset_s"] <= obs[current["first"]]["wall_offset_s"], "Next actual stage not backed by native recovery-window buffered J")
    first_end = attacks[actual_ids[first_side][2]]["times"][3]; second_end = attacks[actual_ids[1-first_side][2]]["times"][3]
    require(downs[7]["key"] == ("D" if first_side == 0 else "A") and downs[7]["sim"] >= first_end+.46 and downs[8]["sim"] >= first_end+.46 and attacks[actual_ids[1-first_side][0]]["times"][0] >= first_end+.46, "Normal turn/fresh second chain bypassed real expiry")
    def ready(row, side, step=6):
        return row["flow_step"] == step and row["supported"] is True and row["clip"] == "sword_ready_idle" and row["action_id"] == "0" and row["stage"] == -1 and row["pending_equipment_action"] is False and row["needs_slot_selection"] is False and row["melee_pending_primary"] is False and row["animation"] == "idle" and row["committed_armor_id"] == str(light) and row["facing"] == (-1 if side == 0 else 1)
    baseline = [row for row in obs if ready(row, first_side, 5) and row["wall_offset_s"] < downs[4]["wall_offset_s"]]
    first_ready = [row for row in obs if ready(row, first_side) and row["actual_sim"] >= first_end and row["wall_offset_s"] < downs[7]["wall_offset_s"]]
    final_ready = [row for row in obs if ready(row, 1-first_side) and row["actual_sim"] >= second_end and row["wall_offset_s"] > downs[8]["wall_offset_s"]]
    require(len(baseline) >= 3 and len(first_ready) >= 3 and len(final_ready) >= 3 and all(ready(row, 1-first_side) for row in obs[-3:]), "Actual Ready>=3 per completed side and fresh final Ready required")
    require(report["leather_combo_fresh_ready_seen_left_right"] == ready_counts and all(value >= 3 for value in ready_counts), "Report Ready counts differ from independently counted actual frames")
    return selected, {"flow_complete": True, "observations": len(obs), "actual_light_instance_id": str(light), "actual_light_version": str(next(iter(versions))),
        "actual_weapon_instance_id": constant[3], "operations_committed": 1, "normal_key_down_order": keys, "actual_combo_masks_left_right_by_stage": [[63]*3, [63]*3],
        "actual_combo_attack_ids_left_right_by_stage": ids, "actual_fresh_ready_left_right": ready_counts, "selected_native_phase_facing_pairs": 36,
        "mismatches": [], "scope": "Actual same leather Ready/P1/P2/P3 two-facing six-attack combo only", "art_review_pending": True,
        "full_motion_accepted": False, "full_equipment_accepted": False, "whole_game_audio_accepted": False, "formal_complete_units": 0}


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


def write_whole_phase_view(path, maps):
    entries = []
    for item in maps:
        entry = dict(item)
        entry["whole_url"] = quote(os.path.relpath(item["source_whole"]["path"], path.parent).replace("\\", "/"), safe="/")
        entry["crop_url"] = quote(os.path.relpath(item["unscaled_crop"]["path"], path.parent).replace("\\", "/"), safe="/")
        entries.append(entry)
    payload = json.dumps(entries, ensure_ascii=False).replace("<", "\\u003c")
    new(path, '''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>实际软皮三段连击 原生阶段视图</title>
<style>body{font:15px system-ui;margin:20px;background:#16191c;color:#eee}button{margin:3px;padding:7px}img{display:block;max-width:none}pre{white-space:pre-wrap}section{overflow:auto;border:1px solid #555;margin-top:12px}p{max-width:1000px}</style>
<h1>实际软皮三段连击：左右各三段、每段六阶段</h1><p>仅选择原生 PNG，完整画面1280×720，裁图240×160均无缩放重采样。技术验证不代表美术接受；全动作、音频、完整装备和完整敌人/单位未接受。</p>
<nav id="buttons"></nav><pre id="label"></pre><a id="source">打开原始 PNG</a><section><img id="whole" width="1280" height="720" alt="原生完整画面"></section><h2>原生尺寸局部</h2><img id="crop" width="240" height="160" alt="无缩放裁图">
<script>const entries=''' + payload + ''';const byId=id=>document.getElementById(id);function select(i){const e=entries[i];byId('whole').src=e.whole_url;byId('crop').src=e.crop_url;byId('source').href=e.whole_url;byId('label').textContent=JSON.stringify({facing:e.facing,stage:e.stage,frame:e.frame,actual_attack_id:e.actual_attack_id,wall_offset_s:e.wall_offset_s,writer_sequence:e.writer_sequence,native_BGRA8_crc32:e.native_BGRA8_crc32,source_sha256:e.source_whole.sha256,crop_sha256:e.unscaled_crop.sha256,actually_viewed:false},null,2);}entries.forEach((e,i)=>{const b=document.createElement('button');b.textContent=(e.facing<0?'左':'右')+' / P'+(e.stage+1)+' / '+e.frame;b.onclick=()=>select(i);byId('buttons').appendChild(b)});select(0);</script></html>\n''')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", required=True)
    parser.add_argument("--snapshot", required=True)
    args = parser.parse_args()
    archive, snapshot = (ROOT / args.archive).resolve(), (ROOT / args.snapshot).resolve()
    require(archive.is_relative_to(ROOT / "过程图稿与视频") and snapshot.is_relative_to(ROOT / "source-assets/production/backups"), "Archive/snapshot outside authorized project roots")
    original, presentation = archive / "原件", archive / "展示副本"
    require(original.is_dir() and presentation.is_dir(), "Actual capture archive is missing")
    require(not (original / "independent-leather-combo-verification-v001.json").exists(), "Never overwrite prior postprocess; retain a new version")
    report, index = read(original / "runtime-report.json"), read(archive / "index.json")
    capture_input_pins = [desc(path) for path in [archive / "index.json"] + [original / name for name in
        ("runtime-report.json", "native-lossless-capture.json", "native-frame-pixels.jsonl", "native-async-write-summary.json", "native-pixel-verification.json")]]
    manifest, package_rows, source_audit = verify_sources(snapshot, index)
    selection, flow_audit = verify_flow(report, index, package_rows)
    movies, pixel_rows, fingerprints, offsets, duration = verify_pixels(original, report)
    # No derived output exists before the complete technical validation above.
    # PNGs, Source/DLL/packages and imported original RGBA are never rewritten.
    maps = []
    for facing in (-1, 1):
        for stage in range(3):
            for frame in range(6):
                i = selection[(facing, stage, frame)]
                row = report["observations"][i]
                scale = row["canvas_size"] / 512.0
                root_x = row["grip_screen"][0] - facing * (row["grip"][0] - row["root"][0]) * scale
                root_y = row["grip_screen"][1] - (row["grip"][1] - row["root"][1]) * scale
                left = max(0, min(1040, math.floor(root_x) - 110))
                top = max(0, min(560, math.floor(root_y) - 130))
                destination = presentation / f"leather-combo-{'left' if facing < 0 else 'right'}-stage-{stage+1}-phase-{frame}-{movies[i].name}"
                require(not destination.exists(), "Never overwrite presentation crop")
                with Image.open(movies[i]) as image:
                    crop = image.crop((left, top, left + 240, top + 160))
                    expected_mode, expected_bytes = crop.mode, crop.tobytes()
                    crop.save(destination)
                with Image.open(destination) as crop:
                    require(crop.size == (240, 160) and crop.mode == expected_mode and crop.tobytes() == expected_bytes, "Unscaled crop pixel round-trip differs")
                maps.append({"observation_index": i, "writer_sequence": pixel_rows[i]["writer_sequence"], "native_BGRA8_crc32": pixel_rows[i]["native_BGRA8_crc32"],
                    "wall_offset_s": offsets[i], "flow_phase": row["flow_phase"], "flow_step": row["flow_step"], "clip": row["clip"], "stage": row["stage"], "frame": frame, "facing": facing,
                    "actual_attack_id": row["action_id"], "actual_light_instance_id": row["committed_armor_id"], "draw_stack": row["draw_stack"], "source_whole": desc(movies[i]),
                    "unscaled_crop": desc(destination), "crop_rect_xywh_px": [left, top, 240, 160], "crop_resampled": False, "actually_viewed": False})
    whole_view = presentation / "leather-combo-whole-phase-view-v001.html"
    write_whole_phase_view(whole_view, maps)
    concat = original / "leather-combo-wall-timed-frames-v001.txt"
    lines = []
    for i, path in enumerate(movies):
        left = 0.0 if i == 0 else offsets[i]
        right = offsets[i + 1] if i + 1 < len(movies) else duration
        require(right > left and "'" not in path.as_posix(), "Invalid concat interval/path")
        lines.extend(["file '" + path.as_posix() + "'", f"duration {right - left:.12f}"])
    lines.append("file '" + movies[-1].as_posix() + "'")
    new(concat, "\n".join(lines) + "\n")
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    video = presentation / "leather-combo-trial-silent.mp4"
    require(not video.exists(), "Never overwrite review video")
    encode = [ffmpeg, "-hide_banner", "-loglevel", "warning", "-f", "concat", "-safe", "0", "-i", str(concat),
              "-vf", "fps=30", "-t", f"{duration:.12f}", "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p", "-an", str(video)]
    encoded = subprocess.run(encode, capture_output=True, text=True)
    new(original / "leather-combo-video-encode.log", encoded.stdout + encoded.stderr)
    require(encoded.returncode == 0 and video.is_file() and video.stat().st_size > 0, "Review video encode failed; preserve failed outputs")
    decode = [ffmpeg, "-hide_banner", "-v", "error", "-i", str(video), "-map", "0:v:0", "-an", "-progress", "pipe:1", "-nostats", "-f", "null", os.devnull]
    decoded = subprocess.run(decode, capture_output=True, text=True)
    new(original / "leather-combo-video-full-decode.log", decoded.stdout + decoded.stderr)
    progress = {}
    for line in decoded.stdout.splitlines():
        if "=" in line:
            key, value = line.split("=", 1); progress[key] = value.strip()
    require(decoded.returncode == 0 and not decoded.stderr.strip() and int(progress.get("frame", "0")) > 0 and progress.get("progress") == "end", "Full review-video decode failed")
    for item in fingerprints + capture_input_pins: same_pin(Path(item["path"]), item)
    _, _, final_source_audit = verify_sources(snapshot, index)
    require(source_audit == final_source_audit, "Postprocess changed frozen source/DLL/package/original RGBA audit")
    source_audit["endpoint_checks_before_and_after_postprocess"] = 2 * source_audit["source_endpoint_checks"]
    flow_audit.update({"original_PNGs": len(fingerprints), "movie_frames": len(movies), "duration_s": duration,
        "every_movie_observation_FIFO_CRC_bound": True, "native_async_stop_flush_verified": True, "art_review_pending": True})
    new(original / "leather-combo-source-binding-verification-v001.json", source_audit)
    new(original / "independent-leather-combo-verification-v001.json", flow_audit)
    new(original / "leather-combo-selected-source-map-v001.json", {"frames": maps, "whole_phase_view": desc(whole_view), "selection_is_not_art_review": True})
    new(original / "leather-combo-pixel-FIFO-binding-v001.json", {"movies": [{"file": movies[i].name, "observation_index": i,
        "writer_sequence": row["writer_sequence"], "native_BGRA8_crc32": row["native_BGRA8_crc32"], "wall_offset_s": offsets[i]} for i, row in enumerate(pixel_rows)],
        "whole_PNG_fingerprints_before_and_after_equal": fingerprints, "capture_metadata_pins_before_and_after_equal": capture_input_pins,
        "source_pixels_mutated": False, "event_clock_note": "Use ScreenshotProcessed event offsets, never asynchronous save completion for playback timing."})
    new(original / "leather-combo-video-receipt-v001.json", {"video": desc(video), "encode_argv": encode, "encode_exit": encoded.returncode,
        "full_decode_argv": decode, "full_decode_exit": decoded.returncode, "decoded_frame_count": int(progress["frame"]), "audio_recorded": False,
        "presentation_policy": "Actual processed-event wall offsets; first frame held from zero, final held to duration; final concat sentinel; CFR30 quantization/duration cap; original clocks/PNGs/positions unchanged.",
        "motion_or_audio_accepted": False})
    provenance = original / "leather-combo-postprocess-provenance-v001"
    require(not provenance.exists(), "Never overwrite postprocess provenance")
    provenance.mkdir()
    (provenance / "compiled-source-manifest.json").write_bytes((snapshot / "compiled-source-manifest.json").read_bytes())
    (provenance / Path(__file__).name).write_bytes(Path(__file__).read_bytes())
    new(archive / "source-version-status-index.json", {"status": "actual_leather_combo_36_phases_technical_verified_visual_review_pending", "snapshot": snapshot.as_posix(),
        "runtime_report": desc(original / "runtime-report.json"), "independent_verification": desc(original / "independent-leather-combo-verification-v001.json"),
        "source_binding": desc(original / "leather-combo-source-binding-verification-v001.json"), "selected_unscaled_crops": 36, "whole_phase_view": desc(whole_view), "video": desc(video),
        "default_full_bound_flow_claimed": False, "complete_equipment_or_full_motion_accepted": False, "formal_complete_units": 0})
    new(archive / "README.md", "真实软皮Ready/P1/P2/P3连击技术留档：正常Enter/E/A取消/E单次提交LGT；每面正常J三段缓冲连击，六个不同实际ActionId，左右每段6阶段。首面实际Ready>=3、链过期后正常转向并重新J；另一面末段结束后实际Ready>=3。36张原生无缩放裁图、完整阶段视图和墙钟CFR30静音视频仅供实看。原PNG、Source/DLL、1151包合同和原始RGBA均前后绑定。技术通过不授予美术、完整装备、全动作、音频、存档或完整单位接受。\n")
    print(json.dumps({"observations": len(report["observations"]), "original_PNGs": len(fingerprints), "snapshot_files": source_audit["snapshot_files"],
        "production_packages": source_audit["production_packages"], "current_full_automation_succeeded": source_audit["current_full_automation_succeeded"],
        "source_mismatches": 0, "operations_committed": 1, "actual_combo_masks_left_right_by_stage": report["leather_combo_masks_left_right_by_stage"], "selected_unscaled_crops": len(maps),
        "whole_phase_view": desc(whole_view), "video": desc(video), "art_review_pending": True, "formal_complete_units": 0}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
