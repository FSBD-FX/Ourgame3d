"""Independent real two-process Run-only proof verifier. No Unreal import/run.

Full native Codec bytes and actual published bundle/marker are inspected; role
reports' passed flags alone never establish a restore. No profile fallback.
"""
from pathlib import Path
import argparse
import hashlib
import json
import math
import struct
import uuid
import zlib


def require(value, why):
    if not value:
        raise ValueError(why)


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, "Duplicate JSON key: " + key)
        result[key] = value
    return result


def parse(raw):
    return json.loads(raw.decode("utf-8-sig"), object_pairs_hook=unique_object,
                      parse_constant=lambda x: (_ for _ in ()).throw(ValueError(x)))


def read(path):
    raw = Path(path).read_bytes()
    require(len(raw) <= 64*1024*1024, "Artifact exceeds bound")
    return raw


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def uint(value):
    require(isinstance(value, str) and value.isascii() and value.isdecimal()
            and (value == "0" or not value.startswith("0")), "Noncanonical uint")
    result = int(value)
    require(0 <= result <= (1 << 64)-1, "uint64 overflow")
    return result


def guid(value):
    parsed = uuid.UUID(value)
    require(parsed.int != 0, "Invalid zero GUID")
    return parsed.hex


def codec_guid(value):
    require(isinstance(value, dict) and set(value) == {"A", "B", "C", "D"}, "Not canonical native FGuid words")
    words = [uint(value[key]) for key in ("A", "B", "C", "D")]
    require(all(word <= 0xffffffff for word in words), "FGuid uint32 overflow")
    return guid("".join(f"{word:08x}" for word in words))


def f64(bits):
    require(isinstance(bits, str) and len(bits) == 16 and bits == bits.lower(), "Not exact double bits")
    value = struct.unpack(">d", bytes.fromhex(bits))[0]
    require(math.isfinite(value), "Nonfinite double")
    return value


def file_fact(path):
    raw = read(path)
    return {"path": str(Path(path).resolve()), "bytes": len(raw), "sha256": sha(raw)}


def check_fact(row, root):
    path = Path(row["path"]).resolve()
    require(path.is_relative_to(root), "Proof artifact escapes session")
    actual = file_fact(path)
    require(actual["bytes"] == row["bytes"] and actual["sha256"] == row["sha256"], "Artifact fact differs: " + str(path))
    return read(path)


def no_run(facts):
    for name in ("pristine_api", "player_null", "controller_pawn_null", "inventory_null", "run_guid_invalid",
                 "controller_local", "controller_authoritative", "controller_input_present", "controller_player_state_present",
                 "default_pawn_class_null", "spectator_class_null", "world_begun_play"):
        require(facts[name] is True, "Pristine admission missing: " + name)
    for name in ("equipment_bound", "scene_active", "rewards_bound", "world_run_valid", "audio_run_valid", "controller_only_spectator"):
        require(facts[name] is False, "Unexpected published owner: " + name)
    for name in ("native_pawns", "native_fighters", "restart_serial", "combat_seed", "next_crit_draw", "fog_rooms", "world_bindings", "audio_records"):
        require(uint(facts[name]) == 0, "Pristine nonzero: " + name)
    require(uint(facts["gate"]) == 3 and facts["simulation_time_bits"] == "0000000000000000", "Pristine gate/clock differs")


def code_run(raw):
    document = parse(raw)
    require(document["codec"] == "bound-run-v1" and set(document) == {"codec", "snapshot"}, "Not whole Run Codec")
    value = document["snapshot"]
    require(value["Schema"] == "1" and value["Scope"] == "1", "Unknown Run schema/scope")
    require(value["Fighters"] and value["Fighters"][0]["Player"] is not None, "Actual player owner absent")
    return value


def key_counts(report, expected):
    events = report["normal_input_requests"]
    require(all(uint(e["process_id"]) == uint(report["process_id"]) for e in events), "Input process identity mismatch")
    for key, count in expected.items():
        selected = [e for e in events if e["key"] == key]
        require(sum(e["down"] is True for e in selected) == count and sum(e["down"] is False for e in selected) == count,
                "Missing real key edges: " + key)
        held = False
        for event in selected:
            require(event["down"] is not held, "Repeated unpaired key edge")
            held = event["down"]
        require(not held, "Key remains down")


def verify(session):
    session = Path(session).resolve()
    process = parse(read(session/"two-process-session.json"))
    require(process["schema"] == "run-pristine-two-native-processes-v1", "Wrong coordinator session")
    require(len(process["processes"]) == 2 and process["sources_unchanged"] is True, "Not two frozen sequential processes")
    first, second = process["processes"]
    require(first["role"] == "source" and second["role"] == "restore", "Wrong process order")
    require(first["pid"] != second["pid"] and first["pid"] > 0 and second["pid"] > 0, "Distinct actual PIDs required")
    require(first["exit_code"] == second["exit_code"] == 0 and first["exited_before_next_launch"] is True, "UE did not exit successfully/sequentially")
    require(first["started_utc"] < first["exited_utc"] <= second["started_utc"] < second["exited_utc"], "Process lifetimes overlap")
    require(first["module_sha256"] == second["module_sha256"] == process["module_sha256_before"] == process["module_sha256_after"], "DLL changed across source/restore")
    require(process["source_sha256_before"] == process["source_sha256_after"] and process["source_sha256_before"], "Source pins changed")
    for native_process in (first,second):
        native_log = check_fact(native_process["native_log"],session).decode("utf-8-sig",errors="replace")
        require("Run two-process "+native_process["role"]+" proof complete" in native_log,
                "Actual independent native log has no coordinator completion")
    source = parse(read(session/"source/source-report.json"))
    restored = parse(read(session/"restore/restore-report.json"))
    for report, pid, role in ((source,first["pid"],"source"),(restored,second["pid"],"restore")):
        require(report["schema"] == "run-pristine-two-process-role-v1" and report["role"] == role and uint(report["process_id"]) == pid,
                "Native report role/PID mismatch")
        require(report["passed"] is True and report["failure"] == "", "Native role reports failure")
        require(guid(report["profile_id"]) == guid(process["profile_id"]), "Profile mismatch")
        require(report["build_id"] == process["module_sha256_before"], "Generation build is not actual pinned DLL")
    key_counts(source,{"Enter":1,"E":1,"T":1})
    key_counts(restored,{"R":1,"Enter":1})
    require(source["writer_status"] == "0" and source["commit"]["status"] == "0"
            and source["commit"]["generation_id"] == "1" and not source["commit"]["replayed"]
            and not source["commit"]["publication_may_have_succeeded"], "No acknowledged original actual writer Commit")
    require(restored["load_status"] == "0" and restored["all_staged_hidden_tick_collision_off"] is True
            and uint(restored["staged_actor_count"]) > 0, "No actual pristine hidden native staging")
    no_run(restored["initial_pristine"])
    no_run(restored["after_real_R"])
    require(restored["initial_pristine"] == restored["after_real_R"], "Real R mutated no-Run origin")
    raw = check_fact(source["codec"],session)
    paused_raw = check_fact(restored["paused_codec"],session)
    installed_raw = check_fact(restored["installed_codec"],session)
    require(raw == installed_raw == paused_raw, "Full native Codec bytes changed through pristine install/pause")
    saved = code_run(raw)
    final = code_run(check_fact(restored["continued_codec"],session))
    require(restored["paused_wall_seconds"] >= .2 and uint(restored["installed_gate"]) == 2, "Actual paused window missing")
    require(restored["controller_possesses_restored_player"] is True and restored["neutral_before_fresh_enter"] is True,
            "No actual native possession/neutral fresh edge")
    require(uint(restored["final_gate"]) == 0 and uint(restored["restart_serial"]) == 0, "Restore restarted a new Run")
    require(saved["RunGuid"] == final["RunGuid"] and saved["OwnerId"] == final["OwnerId"]
            and saved["Equipment"]["View"]["CombatSeed"] == final["Equipment"]["View"]["CombatSeed"]
            and saved["Equipment"]["View"]["NextCritDraw"] == final["Equipment"]["View"]["NextCritDraw"], "Run identity/RNG changed")
    old_player = saved["Fighters"][0]; new_player = final["Fighters"][0]
    require(old_player["CustomMuzzle"] is True and old_player["CustomMuzzleRelative"] == new_player["CustomMuzzleRelative"], "Native custom muzzle lost")
    require([f64(old_player["CustomMuzzleRelative"]["Translation"][k]) for k in ("X","Y","Z")] == [24.,7.,65.], "Actual source muzzle premise not24,7,65")
    old_wa = old_player["Player"]["WeaponActions"]; new_wa = new_player["Player"]["WeaponActions"]
    reload = old_wa["Action"]; terminal = new_wa["Action"]
    equipment = source["equipment_action"]
    require(f64(equipment["start_bits"]) < f64(equipment["deadline_bits"])
            <= f64(source["equipment_completion_observed_sim_bits"]) <= f64(reload["Start"]),
            "Genuine E/original equipment deadline premise absent")
    operations = [o for o in saved["Equipment"]["InventoryState"]["Operations"] if o["OperationId"] == equipment["operation_id"]]
    require(len(operations) == 1 and operations[0]["Request"]["SourceId"] == equipment["source_id"] == source["registered_source_id"]
            and operations[0]["Result"]["AcquiredId"] == equipment["instance_id"] == source["registered_instance_id"] == reload["InstanceId"],
            "Actual Register/E/operation/item/reload chain differs")
    require(reload["Active"] is True and uint(reload["Type"]) == 3 and terminal["Active"] is False
            and uint(terminal["Terminal"]) == 9, "Not original reload→ReloadCompleted")
    require((reload["ActionId"],reload["InstanceId"],reload["Start"],reload["End"])
            == (terminal["ActionId"],terminal["InstanceId"],terminal["Start"],terminal["End"]), "Accepted reload identity/deadline changed")
    elapsed = f64(saved["SimulationTime"])-f64(reload["Start"])
    require(.65 <= elapsed < f64(reload["End"])-f64(reload["Start"]), "Source not actual post-insert/pre-complete boundary")
    before = saved["Equipment"]["InventoryState"]["RuntimeUpdates"]
    after = final["Equipment"]["InventoryState"]["RuntimeUpdates"]
    require(after[:-1] == before and len(after) == len(before)+1, "Inventory history not exactly one appended refill")
    refill = after[-1]
    require(refill["InstanceId"] == reload["InstanceId"] and refill["AtTime"] == reload["End"]
            and f64(refill["BeforeAmmo"]) == 0. and f64(refill["Ammo"]) == 1., "Refill not original exact deadline0→1")
    old_history,new_history = old_wa["WeaponRuntimeHistory"],new_wa["WeaponRuntimeHistory"]
    require(new_history[:-1] == old_history and len(new_history) == len(old_history)+1, "WA resource history not one append")
    wr = new_history[-1]
    require(uint(wr["Kind"]) == 2 and wr["AtTime"] == reload["End"] and wr["Action"]["ActionId"] == reload["ActionId"]
            and wr["Action"]["InstanceId"] == reload["InstanceId"] and f64(wr["BeforeAmmo"]) == 0. and f64(wr["AfterAmmo"]) == 1., "WA refill receipt mismatch")
    require(source["audio_counts"] == {"draw":1,"insert":1,"complete":0}, "Source actual HUD timing premise missing")
    require(restored["paused_audio_counts"] == {"draw":0,"insert":0,"complete":0}
            and restored["final_audio_counts"] == {"draw":0,"insert":0,"complete":1}
            and restored["late_audio_counts"] == restored["final_audio_counts"], "Spent audio replayed or future complete repeated")
    require(restored["late_inventory_runtime_updates"] == str(len(after)) and restored["late_wait_seconds"] >= .2, "Late no-repeat window missing")
    journal = restored["final_audio_records"]
    require(len(journal) == 1 and journal[0]["cue"] == "XBW_RELOAD_COMPLETE_01"
            and journal[0]["at_time_bits"] == reload["End"] and journal[0]["action_id"] == reload["ActionId"]
            and journal[0]["instance_id"] == reload["InstanceId"], "Future-only audio fact not original reload")
    require(journal[0]["sequence"] == saved["Audio"]["NextActionSequence"]
            and uint(final["Audio"]["NextActionSequence"]) == uint(saved["Audio"]["NextActionSequence"])+1,
            "Future audio sequence not exactly one new original completion")
    profiles = Path(process["profiles_directory"]).resolve()
    require(profiles.name == "BoundRunOnly-v1" and profiles.is_relative_to(session), "Wrong isolated namespace")
    profile = profiles/str(uuid.UUID(process["profile_id"]))
    bundle_raw = read(profile/"slot-A.bundle.json"); marker_raw = read(profile/"slot-A.commit.json")
    require(not (profile/"slot-B.commit.json").exists(), "Unexpected replacement/fallback generation")
    bundle, marker = parse(bundle_raw),parse(marker_raw)
    require(bundle["container_version"] == marker["container_version"] == 1 and guid(bundle["ProfileID"]) == guid(marker["ProfileID"]) == guid(process["profile_id"]), "Actual header/Profile wrong")
    require(bundle["GenerationID"] == marker["GenerationID"] == "1" and bundle["parent_generation"] == marker["parent_generation"] == "0", "Not original1parent0")
    require(uint(marker["bundle_byte_length"]) == len(bundle_raw) and marker["bundle_sha256"] == sha(bundle_raw)
            and uint(marker["bundle_crc32"]) == zlib.crc32(bundle_raw)&0xffffffff, "Actual published byte/CRC/SHA mismatch")
    suffix = ',"marker_integrity_digest":"'+marker["marker_integrity_digest"]+'"}'
    text = marker_raw.decode("utf-8");require(text.endswith(suffix), "Noncanonical marker suffix")
    require(sha((text[:-len(suffix)]+'}').encode('utf-8')) == marker["marker_integrity_digest"], "Marker digest differs")
    require((bundle["schema_version"],bundle["content_rules_version"],bundle["coordinate_version"])
            == ("bound-run-generation-v1","bound-development-v1","world-cm-v1"), "Unknown versions")
    require(struct.pack('>d',bundle["run_sim_time_or_null"]).hex() == saved["SimulationTime"] and bundle["build_id"] == process["module_sha256_before"], "Actual header clock/build mismatch")
    envelope = bundle["payload"]
    require(envelope["adapter"] == "bound-run-only-v1" and envelope["scope"] == "BoundDevelopmentRunV1"
            and envelope["generationId"] == "1" and envelope["parentGeneration"] == "0"
            and guid(envelope["profileId"]) == guid(process["profile_id"])
            and guid(envelope["runGuid"]) == codec_guid(saved["RunGuid"])
            and envelope["runSimulationTime"] == saved["SimulationTime"]
            and envelope["run"] == parse(raw), "Whole actual bundle envelope is not saved source")
    require(bundle["restored_from_generation"] == "0" and envelope["buildId"] == bundle["build_id"]
            and envelope["versions"] == {"schema":"bound-run-generation-v1","contentRules":"bound-development-v1","coordinates":"world-cm-v1"},
            "Adapter metadata/recovery provenance differs from actual header")
    require(source["commit"]["bundle_sha256"] == marker["bundle_sha256"]
            and source["commit"]["bundle_crc32"] == marker["bundle_crc32"]
            and source["commit"]["bundle_byte_length"] == len(bundle_raw)
            and source["save_readback_codec_sha256"] == sha(raw), "Native Commit/readback receipts differ from actual disk")
    # Extract original nested Codec text without reencoding the object.
    payload_text = bundle_raw.decode('utf-8'); begin = payload_text.index(',"run":')+len(',"run":')
    _, end = json.JSONDecoder(object_pairs_hook=unique_object).raw_decode(payload_text,begin)
    require(payload_text[begin:end].encode('utf-8') == raw, "Store nested original Codec bytes differ")
    for native, role in ((source,"source"),(restored,"restore")):
        require(native["store_generation_id"] == "1" and native["store_observed_head"] == "1", "Native adapter did not read original published head")
        require(Path(native["profile_directory"]).resolve() == profile.resolve(), "Native IO root mismatch")
        require(Path(native["profiles_directory"]).resolve() == profiles, "Native namespace root mismatch")
    actual_files = sorted((file_fact(p) for p in profile.rglob('*') if p.is_file()),key=lambda r:r['path'].casefold())
    for native in (source,restored):
        reported = sorted(native["actual_store_files"],key=lambda r:r['path'].casefold())
        require([(Path(r['path']).resolve(),r['bytes'],r['sha256']) for r in reported]
                == [(Path(r['path']).resolve(),r['bytes'],r['sha256']) for r in actual_files], "Actual IO file set/bytes changed or omitted")
    return {"schema":"independent-run-pristine-two-process-verification-v1","passed":True,
            "source_pid":first["pid"],"restore_pid":second["pid"],"full_codec_byte_equal":True,
            "actual_published_bundle_length_sha_crc_marker_verified":True,"initial_no_run_and_R_preserved":True,
            "original_reload_id_instance_deadline_and_unique_refill":True,"future_complete_only_no_old_audio":True,
            "codec":file_fact(source["codec"]["path"]),"bundle":file_fact(profile/"slot-A.bundle.json"),
            "marker":file_fact(profile/"slot-A.commit.json"),"snapshot_scope":"BoundDevelopmentRunV1 only",
            "not_full_D13_profile":True,"audio_device_auditioned":False,"visual_running_proof_reviewed":False,
            "formal_complete_units":0}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--session",required=True)
    parser.add_argument("--write-receipt",action="store_true")
    args = parser.parse_args()
    result = verify(args.session)
    if args.write_receipt:
        output = Path(args.session)/"two-process-verification-v001.json"
        with output.open("x",encoding="utf-8") as stream:
            json.dump(result,stream,ensure_ascii=False,indent=2);stream.write("\n")
    print(json.dumps(result,ensure_ascii=False))
