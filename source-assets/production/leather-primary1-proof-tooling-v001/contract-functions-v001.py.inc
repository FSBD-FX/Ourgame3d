def expected_stack(frame, primary=True, ready_namespace=READY_NEW):
    namespace, stem = (PRIMARY_OLD, "Primary1") if primary else (READY_OLD, "Ready")
    armor_namespace = PRIMARY_NEW if primary else ready_namespace
    def old(component):
        return object_path(namespace, f"T_Fairytale_Sword{stem}{component}_{frame:03d}_v001")
    def armor(component):
        prefix = "Leather" if armor_namespace in (PRIMARY_NEW, READY_NEW) else "Sword"
        return object_path(armor_namespace, f"T_Fairytale_{prefix}{stem}{component}_{frame:03d}_v001")
    result = [old("BodyRest"), armor("ShoulderFar"), armor("Chest"), old("NearArmWithoutHand"), armor("ShoulderNear")]
    if primary:
        result.append(old("HelmetForeground"))
    return result + [SWORD, old("NearHand")]


def root_pin(pin, label):
    require(isinstance(pin, dict) and set(("path", "bytes", "sha256")).issubset(pin), f"Missing {label} exact pin")
    path = (ROOT / pin["path"]).resolve()
    require(path.is_relative_to(ROOT), f"{label} outside project")
    require(type(pin["bytes"]) is int and pin["bytes"] > 0 and isinstance(pin["sha256"], str) and len(pin["sha256"]) == 64, f"Invalid {label} exact pin")
    same_pin(path, pin)
    return path


def verify_sources(snapshot, index, expected_automation=157):
    require(type(expected_automation) is int and expected_automation >= 157, "P1 snapshot requires full157 or explicit later full count")
    manifest_path = snapshot / "compiled-source-manifest.json"
    manifest = read(manifest_path)
    require(index["source_manifest_SHA256"] == desc(manifest_path)["sha256"], "Capture/snapshot manifest hash differs")
    require((ROOT / index["snapshot"]).resolve() == snapshot, "Capture names another snapshot")
    rows = manifest["files"]
    by_path = {row["path"]: row for row in rows}
    require(len(by_path) == len(rows) > 0, "Duplicate or empty snapshot paths")
    for row in rows:
        relative = Path(row["path"])
        require(not relative.is_absolute() and ".." not in relative.parts and relative.as_posix() == row["path"], "Unsafe or noncanonical snapshot-relative path")
        for base in (ROOT, snapshot):
            path = (base / relative).resolve()
            require(path.is_relative_to(base), "Snapshot path escapes its root")
            same_pin(path, row)
    for path, pin in NATIVE_SOURCE_PINS.items():
        require(path in by_path and by_path[path]["bytes"] == pin["bytes"] and by_path[path]["sha256"] == pin["sha256"], "Compiled native source is not exact approved P1 Source: " + path)
    require("UnrealGame/Binaries/Win64/UnrealEditor-CodexDungeon.dll" in by_path, "Compiled native DLL absent from snapshot")
    tool_path = "tools/scripts/postprocess-leather-primary1-trial-v001.py"
    require(tool_path in by_path, "Actual P1 postprocessor is not a frozen snapshot input")
    same_pin(Path(__file__), by_path[tool_path])
    actual_code = {p.relative_to(ROOT).as_posix() for directory in ("UnrealGame/Source", "UnrealGame/Config") for p in (ROOT / directory).rglob("*") if p.is_file()}
    require(actual_code == {key for key in by_path if key.startswith(("UnrealGame/Source/", "UnrealGame/Config/"))}, "Snapshot omits or invents current Source/Config inputs")
    production = {key: value for key, value in by_path.items() if key.startswith("UnrealGame/Content/Production/")}
    actual_production = {p.relative_to(ROOT).as_posix() for p in (ROOT / "UnrealGame/Content/Production").rglob("*") if p.is_file()}
    require(set(production) == actual_production and manifest["production_packages"] == len(production) == 1115, "P1 Production set must be unchanged1097 plus new18")
    require(manifest.get("mismatches") == 0 and manifest.get("old_production_unchanged") is True, "Snapshot input audit is not clean")
    require("base_snapshot" in manifest, "Missing explicit old1097 baseline snapshot")
    base = (ROOT / manifest["base_snapshot"]).resolve()
    require(base.is_relative_to(ROOT / "source-assets/production/backups"), "Base snapshot outside project backups")
    base_manifest_path = base / "compiled-source-manifest.json"
    before = read(base_manifest_path)
    old = {row["path"]: row for row in before["files"] if row["path"].startswith("UnrealGame/Content/Production/")}
    require(len(old) == manifest["old_production_packages"] == 1097 and all(production.get(key) == value for key, value in old.items()), "Old1097 package bytes changed or baseline differs")
    require(manifest["new_production_packages"] == len(production) - len(old) == 18, "Actual new package count differs from18")
    automation_path = (ROOT / manifest["current_automation_report"]).resolve()
    require(automation_path.is_relative_to(ROOT) and automation_path.relative_to(ROOT).as_posix() in by_path, "Actual automation report not in compiled snapshot")
    automation = read(automation_path)
    require(type(manifest["current_automation_succeeded"]) is int and manifest["current_automation_succeeded"] == automation["succeeded"] == expected_automation, "Current full automation count differs")
    tests = automation["tests"]
    require(len(tests) == expected_automation and len({item["fullTestPath"] for item in tests}) == expected_automation, "Automation tests are not unique/current")
    require(all(automation.get(key, 0) == 0 for key in ("failed", "succeededWithWarnings", "notRun", "inProcess")), "Automation has failures or incomplete tests")
    require(all(item["state"] == "Success" and item["errors"] == item["warnings"] == 0 for item in tests), "Automation entries are not all clean Success")
    receipt_pin = manifest["new_production_import_receipt"]
    receipt_path = root_pin(receipt_pin, "P1 import receipt")
    require(receipt_path.relative_to(ROOT).as_posix() in by_path, "Import receipt is not compiled-snapshot input")
    imported = read(receipt_path)
    require(imported["success"] is True and imported["namespace"] == PRIMARY_NEW.rstrip("/") and imported["actual_count"] == imported["saved_count"] == imported["expected_count"] == 18, "Actual P1 import is not clean18 textures")
    require(type(imported["old_packages_unchanged"]) is int and imported["old_packages_unchanged"] == 1097, "Import did not preserve all old1097 packages")
    assets = imported["assets"]
    expected = {(component, frame) for component in ("Chest", "ShoulderNear", "ShoulderFar") for frame in range(6)}
    require(len(assets) == 18 and {(row["component"], row["frame"]) for row in assets} == expected, "Actual P1 import component/frame set differs")
    new_packages, source_pins = set(), []
    for asset in assets:
        require(type(asset["frame"]) is int and asset["actual_object_type"] == "Texture2D", "Actual import frame/type differs")
        name = f"T_Fairytale_LeatherPrimary1{asset['component']}_{asset['frame']:03d}_v001"
        require(asset["object_path"] == object_path(PRIMARY_NEW, name), "Imported P1 object path differs")
        source = Path(asset["source"]).resolve()
        require(source.is_relative_to(ROOT / "source-assets/production"), "Import source outside production candidates")
        same_pin(source, {"bytes": asset["source_bytes"], "sha256": asset["source_sha256"]})
        with Image.open(source) as image:
            require(image.format == "PNG" and image.mode == "RGBA" and image.size == (512, 512), "Imported original armor PNG must remain512 RGBA")
        source_pins.append(desc(source))
        package = package_file(asset["object_path"])
        require(package in by_path and package not in old, "New P1 texture missing from snapshot or overwrites old package")
        require(by_path[package]["bytes"] == asset["saved_bytes"] and by_path[package]["sha256"] == asset["saved_sha256"], "Imported texture bytes differ from native receipt")
        new_packages.add(package)
    require(new_packages == set(production) - set(old), "Snapshot contains an unreceipted new package")
    # Root supplies this exact reference from finalmanifest.references; never
    # guess an assembly directory or silently fall back to Ready's source.
    assembly_pin = imported.get("assembly_freeze")
    assembly_freeze = root_pin(assembly_pin, "explicit assembly_freeze")
    relative = assembly_freeze.relative_to(ROOT).as_posix()
    require(relative in by_path and by_path[relative]["bytes"] == assembly_pin["bytes"] and by_path[relative]["sha256"] == assembly_pin["sha256"], "Assembly freeze is not exact compiled-snapshot input")
    assembly, assembly_manifest = assembly_freeze.parent, read(assembly_freeze)
    assembly_sources = []
    require(len({item["path"] for item in assembly_manifest["files"]}) == len(assembly_manifest["files"]), "Duplicate assembly source entries")
    for item in assembly_manifest["files"]:
        source = (assembly / item["path"]).resolve()
        require(not Path(item["path"]).is_absolute() and ".." not in Path(item["path"]).parts and source.is_relative_to(assembly), "Unsafe assembly source path")
        same_pin(source, item)
        assembly_sources.append(desc(source))
    require(assembly_sources, "Empty assembly source freeze")
    return manifest, by_path, {"snapshot": snapshot.as_posix(), "snapshot_files": len(rows), "source_endpoint_checks": 2 * len(rows),
        "source_mismatches": 0, "base_snapshot_manifest": desc(base_manifest_path), "production_packages": len(production), "old_production_packages_unchanged": 1097,
        "current_full_automation_succeeded": expected_automation, "actual_new_primary1_textures": 18,
        "assembly_freeze": desc(assembly_freeze), "assembly_source_checks": len(assembly_sources),
        "imported_original_RGBA_pins": source_pins, "assembly_original_source_pins": assembly_sources,
        "source_and_DLL_unchanged": True, "body_source_repainting_asserted": False}


def identifier(value, label, allow_zero=False):
    require(isinstance(value, str) and value.isascii() and value.isdigit() and str(int(value)) == value, "Noncanonical native ID: " + label)
    require((0 if allow_zero else 1) <= int(value) <= 2**64 - 1, "Invalid native ID: " + label)
    return int(value)


def verify_flow(report, index, package_rows):
    require(report["schema"] == "fairytale-equipment-bound-native-flow-v1" and report["leather_primary1_only_trial"] is True and report["leather_ready_only_trial"] is False, "Only explicit P1-only native flow is accepted")
    require(report["scope"] == PRIMARY1_SCOPE, "Native report scope is not exact frozen P1 scope")
    require(report["passed"] is True and report["flow_complete"] is True and report["reason"] == report["failure"] == "" and report["mismatches"] == [], "Native P1 trial did not pass cleanly")
    require(index["runtime_passed"] is True and index["exit_code"] == 0 and report["formal_complete_units"] == 0, "Native process/index failed or claims complete unit")
    require(report["silent_video"] is True and report["audio_recorded"] is False and report["native_async_capture_writes_flushed"] is True, "Silent/flush contract differs")
    require(all(report.get(key, False) is False for key in ("forced_pose", "forced_frame", "forced_clock", "direct_gear_writes", "fake_attack_ids", "simulation_pacing_changed")), "Forced pose/frame/clock/gear or fake IDs are forbidden")
    require(report["leather_primary1_masks_left_right"] == [63, 63] and report["light_primary_phase_masks"] == [63, 0, 0] and report["leather_ready_phase_masks_left_right"] == [0, 0], "P1-only native phase masks differ")
    require(all(identifier(report[key], key, True) == 0 for key in ("medium_instance_id", "medium_source_id", "original_light_drop_source")), "P1-only proof entered medium/drop flow")
    light = identifier(report["light_instance_id"], "light_instance_id")
    identifier(report["light_source_id"], "light_source_id")
    reported_ids = [identifier(value, "P1 attack ID") for value in report["leather_primary1_attack_ids_left_right"]]
    require(len(reported_ids) == 2 and reported_ids[0] != reported_ids[1], "Two distinct actual P1 attack IDs required")
    obs = report["observations"]
    require(obs and index["observations"] == len(obs), "Observation/index count differs")
    duration = report["duration_s"]
    require(finite(duration) and duration > 0, "Invalid actual capture duration")
    inputs = report["normal_input_requests"]
    require(inputs == report["inputevents"], "Input aliases differ")
    downs = [row for row in inputs if row["down"] is True]
    keys = [row["key"] for row in downs]
    require(len(keys) == 7 and keys[:5] == ["Enter", "E", "A", "E", "J"] and keys[5] in ("A", "D") and keys[6] == "J", "Expected normal Enter/E/A cancel/E commit/J/turn/J only")
    held = set(); prior_wall = -1.; prior_sim = -1.
    for row in inputs:
        require(row["key"] in ("Enter", "E", "A", "D", "J") and type(row["down"]) is bool and finite(row["wall_offset_s"]) and prior_wall <= row["wall_offset_s"] <= duration and finite(row["sim"]) and row["sim"] >= prior_sim, "Input time/order/key differs")
        require((row["key"] not in held and not held) if row["down"] else (row["key"] in held), "Unpaired, overlapping or duplicate normal input")
        if row["down"]: held.add(row["key"])
        else: held.remove(row["key"])
        prior_wall, prior_sim = row["wall_offset_s"], row["sim"]
    require(not held, "P1 trial ended with held input")
    phases = report["phasechecks"]
    require([(row["step"], row["phase"]) for row in phases] == list(enumerate(PHASES)), "P1-only phase transitions differ")
    require(all(finite(row["sim"]) and finite(row["wall_offset_s"]) and 0 <= row["wall_offset_s"] <= duration for row in phases), "Invalid phase event clocks")
    require(all(b["sim"] >= a["sim"] and b["wall_offset_s"] >= a["wall_offset_s"] for a, b in zip(phases, phases[1:])), "Phase event clocks rewind")
    require(phases[0]["sim"] >= downs[0]["sim"] and phases[0]["wall_offset_s"] >= downs[0]["wall_offset_s"], "Start phase precedes actual Enter")
    for phase, request in ((1, 1), (2, 2), (3, 3), (5, 4)):
        require(phases[phase]["sim"] == downs[request]["sim"] and phases[phase]["wall_offset_s"] >= downs[request]["wall_offset_s"], "Phase transition is not paired to normal native request")
    first, last = obs[0], obs[-1]
    constant = tuple(first[key] for key in ("run", "run_alias", "owner_id", "committed_weapon_id", "committed_weapon_version", "active_slot"))
    require(isinstance(constant[0], str) and len(constant[0]) == 32 and all(c in "0123456789abcdef" for c in constant[0]) and int(constant[0], 16) > 0, "Actual native run GUID missing")
    for key, value in zip(("run_alias", "owner_id", "committed_weapon_id", "committed_weapon_version"), constant[1:5]): identifier(value, key)
    require(type(constant[5]) is int and constant[5] in (0, 1), "Actual active slot invalid")
    initial_ops = identifier(first["operation_count"], "operation_count", True)
    initial_next = identifier(first["next_operation_id"], "next_operation_id")
    require(identifier(last["operation_count"], "operation_count", True) == initial_ops + 1 and identifier(last["next_operation_id"], "next_operation_id") == initial_next + 1, "P1 trial must commit exactly once")
    selected, attacks = {}, {}
    masks = {-1: 0, 1: 0}; seen_steps = set(); versions = set(); pending_steps = set(); deadlines = {}
    last_draw = identifier(first["draw_id"], "draw_id") - 1; last_ops = initial_ops; last_wall = -1.; last_sim = -1.; last_step = -1
    ready_namespace = None
    for i, row in enumerate(obs):
        require(tuple(row[key] for key in ("run", "run_alias", "owner_id", "committed_weapon_id", "committed_weapon_version", "active_slot")) == constant, "Actual run/player/sword identity or version changed")
        step = row["flow_step"]
        require(type(step) is int and step in range(7) and step >= last_step and row["flow_phase"] == PHASES[step], "Observation came from another flow or rewound steps")
        last_step = step
        seen_steps.add(step)
        require(row["active"] is True and row["texture_ready"] is True and row["interface_visible"] is False and row["text_calls"] == 0, "Draw/readiness/UI-off contract differs")
        require(finite(row["canvas_size"]) and math.isclose(row["canvas_size"], CANVAS, rel_tol=0., abs_tol=1e-9) and row["body_max_contract"] == 72, "Actual source canvas/body-size contract changed")
        require(finite(row["sim"]) and finite(row["actual_sim"]) and math.isclose(row["sim"], row["actual_sim"], rel_tol=0., abs_tol=1e-9) and row["actual_sim"] >= last_sim, "Draw/native clocks differ or rewind")
        require(finite(row["wall_offset_s"]) and last_wall < row["wall_offset_s"] < duration, "Observation event clock not strictly increasing")
        last_wall, last_sim = row["wall_offset_s"], row["actual_sim"]
        require(row["wall_offset_s"] <= phases[step]["wall_offset_s"] and row["actual_sim"] <= phases[step]["sim"]
                and (step == 0 or (row["wall_offset_s"] >= phases[step - 1]["wall_offset_s"] and row["actual_sim"] >= phases[step - 1]["sim"])), "Observation lies outside its actual phase-check interval")
        require(type(row["facing"]) is int and row["facing"] in (-1, 1) and type(row["frame"]) is int and type(row["stage"]) is int, "Invalid native facing/frame/stage")
        require(row["clip"] in ("sword_ready_idle", "sword_primary_1") and row["weapon_mirror"] == "WPN-SWD-001" and row["melee_pending_primary"] is False, "Unexpected combo clip, sword or queued primary")
        draw = identifier(row["draw_id"], "draw_id"); require(draw > last_draw, "Draw IDs not strictly increasing"); last_draw = draw
        ops = identifier(row["operation_count"], "operation_count", True)
        require(ops in (initial_ops, initial_ops + 1) and ops >= last_ops and identifier(row["next_operation_id"], "next_operation_id") == initial_next + ops - initial_ops, "Operation cursor changed unexpectedly")
        last_ops = ops
        armor = identifier(row["committed_armor_id"], "committed_armor_id", True)
        require(armor in (0, light), "Unexpected committed armor")
        require((step >= 5) == (armor == light) if step != 4 else True, "Committed armor does not match cancel/commit phase")
        mode = "no_armor" if armor == 0 else "light_armor"
        require(row["expected_armor_mode"] == mode and row["armor_mirror"] == ("" if armor == 0 else "ARM-LGT-001"), "Draw mode/content differs from committed armor")
        if armor:
            versions.add(identifier(row["committed_armor_version"], "committed_armor_version"))
            require(ops == initial_ops + 1, "Light armor shown without one real commit")
        else: require(identifier(row["committed_armor_version"], "committed_armor_version", True) == 0 and ops == initial_ops, "Empty armor has version or spent operation")
        pending = row["pending_equipment_action"] is True and row["pending_equipment_kind"] == 2 and row["animation"] == "equip_armor"
        require(pending == row["committed_gear_placeholder_expected"] and type(row["supported"]) is bool, "Pending committed-gear placeholder expectation differs")
        if pending:
            require(row["supported"] is False and row["frame"] == 0 and identifier(row["pending_instance_id"], "pending_instance_id") == light and finite(row["equipment_deadline"]), "Pickup relabeled supported or lost actual target")
            if step in (2, 4):
                pending_steps.add(step); deadlines.setdefault(step, row["equipment_deadline"])
                require(deadlines[step] == row["equipment_deadline"], "Pending action deadline changed")
        draw_gear = row["supported"] is True or pending
        primary = row["clip"] == "sword_primary_1"
        action_id = identifier(row["action_id"], "action_id", True)
        require((primary and step == 6 and row["stage"] == 0 and row["frame"] in range(6) and action_id > 0 and row["supported"] is True and not pending and armor == light)
                or (not primary and row["stage"] == -1 and row["frame"] in range(4) and action_id == 0), "Only actual fresh stage0 P1 or native Ready observations allowed")
        expected_body = object_path(BODY, f"T_Fairytale_Sword{'Primary1' if primary else 'Ready'}_{row['frame']:03d}_v002")
        require(row["texture"] == expected_body, "Original common Body158 texture path changed")
        stack = row["draw_stack"]
        require(isinstance(stack, list) and all(isinstance(path, str) for path in stack), "Invalid draw stack")
        has_armor = any("Shoulder" in path or "Chest" in path for path in stack)
        require(has_armor == row["draw_stack_has_armor"], "Armor metadata differs")
        if not draw_gear:
            require(stack == [expected_body] and row["armor_drawn"] is False and not has_armor and row["weapon"] == "", "Unsupported pose leaks gear")
        elif armor == 0:
            require(stack == [expected_body, SWORD, expected_body] and row["armor_drawn"] is False and not has_armor and row["weapon"] == SWORD, "Unarmored row is dressed or loses sword")
        else:
            require(row["armor_drawn"] is True and row["armor_ready"] is True and row["armor_preview"] is True and has_armor and row["weapon"] == SWORD, "Actual committed LGT gear readiness differs")
            if primary:
                require(stack == expected_stack(row["frame"], True) and sum(path.startswith(PRIMARY_NEW) for path in stack) == 3, "P1 must use exact new3armor/old4body/independent sword eight-stack")
            else:
                matching = [namespace for namespace in (READY_NEW, READY_OLD) if stack == expected_stack(row["frame"], False, namespace)]
                require(len(matching) == 1, "Ready/pending must use one correct old or new Ready namespace seven-stack")
                ready_namespace = ready_namespace or matching[0]
                require(ready_namespace == matching[0], "Ready namespace changed mid-capture")
        if draw_gear:
            require(row["instance_id"] == row["committed_weapon_id"] and finite(row["weapon_scale"]) and math.isclose(row["weapon_scale"], .5, rel_tol=0., abs_tol=1e-12), "Independent sword identity/scale changed")
        for resource in set(stack + [expected_body]): require(package_file(resource) in package_rows, "Drawn resource missing from compiled snapshot")
        for point in ("root", "grip", "grip_screen"):
            require(isinstance(row[point], list) and len(row[point]) == 2 and all(finite(value) for value in row[point]), "Invalid native marker/screen point")
        if primary:
            times = tuple(row[key] for key in ("start", "active_at", "active_end", "end"))
            require(all(finite(value) for value in times) and times[0] < times[1] < times[2] < times[3] and times[0] <= row["actual_sim"] <= times[3], "Actual P1 timeline invalid")
            facing = row["facing"]
            require(action_id == reported_ids[0 if facing < 0 else 1], "Actual attack ID differs from facing report")
            entry = attacks.setdefault(action_id, {"facing": facing, "times": times, "first": i, "last": i})
            require(entry["facing"] == facing and entry["times"] == times, "One actual attack changed facing or schedule")
            entry["last"] = i
            masks[facing] |= 1 << row["frame"]
            selected.setdefault((facing, row["frame"]), i)
    require(seen_steps == set(range(7)) and pending_steps == {2, 4}, "Actual cancel/commit observations missing")
    require(masks == {-1: 63, 1: 63} and len(selected) == 12 and len(attacks) == 2, "Actual P1 six phases each facing incomplete")
    require(len(versions) == 1 and identifier(last["committed_armor_id"], "final light") == light, "Actual LGT identity/version changed")
    require(downs[2]["sim"] >= deadlines[2] - .4 and downs[2]["sim"] < deadlines[2] - .08 and phases[3]["sim"] > deadlines[2] + .02, "Normal cancel was not inside real .5s pickup window")
    ordered = sorted(attacks.items(), key=lambda pair: pair[1]["first"])
    first_id, a = ordered[0]; second_id, b = ordered[1]
    require(a["last"] < b["first"] and a["facing"] == -b["facing"] and downs[5]["key"] == ("D" if a["facing"] < 0 else "A"), "Attacks overlap or normal turn does not mirror facing")
    require(downs[4]["sim"] <= a["times"][0] and downs[4]["wall_offset_s"] <= obs[a["first"]]["wall_offset_s"] and downs[6]["sim"] <= b["times"][0] and downs[6]["wall_offset_s"] <= obs[b["first"]]["wall_offset_s"], "Actual attacks not paired to normal J requests")
    require(downs[5]["sim"] >= a["times"][3] + .46 and downs[6]["sim"] >= a["times"][3] + .46 and b["times"][0] >= a["times"][3] + .46, "Second attack bypassed real combo expiry End+.46")
    def actual_ready(row):
        return row["flow_step"] == 6 and row["supported"] is True and row["clip"] == "sword_ready_idle" and row["stage"] == -1 and row["action_id"] == "0" and row["pending_equipment_action"] is False and row["animation"] == "idle" and row["committed_armor_id"] == str(light)
    first_ready = [row for row in obs[:a["first"]] if row["flow_step"] == 5 and row["supported"] is True and row["clip"] == "sword_ready_idle" and row["pending_equipment_action"] is False and row["animation"] == "idle" and row["wall_offset_s"] < downs[4]["wall_offset_s"]]
    between = [row for row in obs[a["last"] + 1:b["first"]] if actual_ready(row) and row["actual_sim"] >= a["times"][3] and row["wall_offset_s"] < downs[5]["wall_offset_s"]]
    final_ready = [row for row in obs[b["last"] + 1:] if actual_ready(row) and row["actual_sim"] >= b["times"][3] and row["wall_offset_s"] > downs[6]["wall_offset_s"]]
    require(len(first_ready) >= 3 and len(between) >= 3 and len(final_ready) >= 3 and all(actual_ready(row) for row in obs[-3:]), "Need actual Ready3 before first J, Ready3 before turn, and3 fresh final Ready after second real End")
    return selected, {"flow_complete": True, "observations": len(obs), "actual_light_instance_id": str(light),
        "actual_light_version": str(next(iter(versions))), "actual_weapon_instance_id": constant[3], "operations_committed": 1,
        "normal_key_down_order": keys, "actual_primary1_masks_left_right": [63, 63],
        "actual_primary1_attack_ids_left_right": [str(value) for value in reported_ids], "ordered_actual_attack_ids": [str(first_id), str(second_id)],
        "first_actual_action_end": a["times"][3], "second_normal_J_sim": downs[6]["sim"], "fresh_final_actual_ready_observations": len(final_ready),
        "selected_native_phase_facing_pairs": 12, "ready_namespace": ready_namespace, "mismatches": [],
        "scope": "Actual new leather P1 six phases each facing only; real cancel/one commit/two fresh normal J attacks", "art_review_pending": True,
        "full_motion_accepted": False, "whole_game_audio_accepted": False, "full_equipment_accepted": False, "formal_complete_units": 0}
