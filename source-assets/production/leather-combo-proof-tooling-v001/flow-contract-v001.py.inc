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
