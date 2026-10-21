"""Read-only independent actual GuardV2 two-process/full-codec/native-pixel verifier.

No engine is launched, and report booleans alone never establish a restore.
The final receipt leaves visual review, formal encounter/reward/audio and D13 pending.
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
    require(document["codec"] == "bound-run-v2" and set(document) == {"codec", "snapshot"}, "Not whole Run Codec")
    value = document["snapshot"]
    require(value["Schema"] == "2" and value["Scope"] == "2", "Unknown Run schema/scope")
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



def native_capture(directory, report):
    from PIL import Image
    metadata = parse(read(directory/"native-lossless-capture.json"))
    require(metadata["mode"] == "native_viewport_BGRA8_lossless_PNG_zlib0", "Native capture mode differs")
    require(all(metadata[k] is False for k in ("pixel_mutations", "simulation_pacing_changed", "audio_changed")), "Capture changed pixels/pacing/audio")
    require(all(metadata[k] is True for k in ("async_movie_writer_requested", "async_movie_writer_active", "prewarm_synchronous")), "Native async/prewarm missing")
    require(metadata["movie_filename_reservation"] == "Windows_CreateFileW_CREATE_NEW_exact_engine_request_before_enqueue", "Native exclusive filename reservation missing")
    receipts = [parse(line.encode("utf-8")) for line in read(directory/"native-frame-pixels.jsonl").decode("utf-8-sig").splitlines() if line]
    actual = {p.name for p in directory.glob("MovieFrame*.png")} | {"prewarm-viewport.png"}
    names = [r["file"] for r in receipts]
    require(len(names) == len(set(names)) and set(names) == actual, "Native receipts omit/repeat originals")
    for row in receipts:
        require(row["saved"] is True and Path(row["file"]).name == row["file"], "Failed or unsafe screenshot receipt")
        with Image.open(directory/row["file"]) as image:
            require(image.format == "PNG" and image.size == (row["width"],row["height"]) == (1280,720), "Viewport dimensions/PNG differ")
            rgba = image.convert("RGBA")
            require(rgba.getchannel("A").getextrema() == (255,255), "Viewport alpha differs")
            require(zlib.crc32(rgba.tobytes("raw","BGRA"))&0xffffffff == row["native_BGRA8_crc32"], "Original native BGRA pixel CRC differs: "+row["file"])
    movie = [r for r in receipts if r["file"].startswith("MovieFrame")]
    count = len(movie)
    require(count > 0 and [r["file"] for r in movie] == sorted(r["file"] for r in movie), "Native movie filenames not FIFO")
    require([r["writer_sequence"] for r in movie] == list(range(1,count+1)), "Native movie writer sequence differs")
    require(next(r for r in receipts if r["file"] == "prewarm-viewport.png").get("async_writer",False) is False, "Prewarm was not synchronous")
    summary = parse(read(directory/"native-async-write-summary.json"))
    require(all(summary[k] is True for k in ("requested","active","closed","flushed","success")), "Native queue not sealed/drained")
    require(all(summary[k] == count for k in ("movie_reserved","movie_enqueued","movie_saved","movie_completed","receipts_saved")), "Native count differs")
    require(all(summary[k] == 0 for k in ("movie_reservation_failed","movie_failed","rejected","pending")), "Native pending/drop/failure")
    require(report["native_async_capture_requested"] and report["native_async_capture_writes_flushed"] and report["capture_stop_before_flush"], "Native stop/drain report absent")
    timing = report["capture_timing"]; offsets = timing["frame_wall_offsets_s"]; observations = report["observations"]
    require(timing["use_fixed_time_step"] is False and len(offsets) == len(observations) == count, "Native ordinary-pacing capture/observation count differs")
    require(all(0 <= a <= b for a,b in zip(offsets,offsets[1:])), "Observation time reversed")
    require(abs(report["duration_s"] - (timing["capture_stop_monotonic_s"]-timing["capture_start_monotonic_s"])) < 1e-6, "Capture duration differs")
    for index,(row,offset,observation) in enumerate(zip(movie,offsets,observations)):
        require(observation["index"] == index and observation["wall_offset_s"] == offset and uint(observation["process_id"]) == uint(report["process_id"]), "Actual processed viewport observation differs")
        require(row["async_writer"] and row["copy_crc_matches"] and row["filename_reserved"] and row["filename_reservation_mode"] == "Windows_CreateFileW_CREATE_NEW", "Unsafe async frame")
        require(row["copied_BGRA8_crc32"] == row["native_BGRA8_crc32"], "Copied viewport pixels changed")
        capture,reserved,queued,started,completed=(row[k] for k in ("capture_callback_monotonic_s","reservation_completed_monotonic_s","enqueued_monotonic_s","save_started_monotonic_s","save_completed_monotonic_s"))
        require(0 < capture <= reserved <= queued <= started <= completed, "Native event order differs")
        require(capture <= timing["capture_start_monotonic_s"]+offset+1e-6, "Save completion substituted for capture")
        require(abs(row["save_wall_s"]-(completed-started)) < 1e-6, "Native save time differs")
    require(timing["capture_stop_monotonic_s"] <= summary["flush_completed_monotonic_s"] <= report["flush_completed_monotonic_s"], "Capture stop/flush ordering differs")
    require(summary["last_save_completed_monotonic_s"] <= summary["flush_completed_monotonic_s"], "Native flush preceded final write")
    require(abs(summary["first_capture_callback_monotonic_s"]-movie[0]["capture_callback_monotonic_s"]) < 1e-6 and abs(summary["last_capture_callback_monotonic_s"]-movie[-1]["capture_callback_monotonic_s"]) < 1e-6, "Native capture endpoint clocks differ")
    require(not list(directory.glob("runtime-mix*.wav")), "Silent proof unexpectedly has recorded audio")
    return {"original_PNGs":len(receipts),"movie_frames":count,"pixel_crc_all_verified":True,"FIFO_unique_flush_verified":True}


def guards(snapshot):
    selected = [fighter for fighter in snapshot["Fighters"] if fighter.get("Guard") is not None]
    require(len(selected) == 2 and all(f["Schema"] == "3" and f["EnemyContentId"] == "ENM-STN-003" for f in selected), "Not exact two legal native003 Guard owners")
    require(len({f["EntityId"] for f in selected}) == 2, "Guard IDs repeated")
    return {f["EntityId"]:f for f in selected}


def dead_invariant(before,after):
    require(before["EntityId"] == after["EntityId"] and after["Dead"] and not after["DeathReported"] and after["Guard"]["DeathObserved"], "Native dead observer/formal split changed")
    old,new = before["Guard"]["Kernel"],after["Guard"]["Kernel"]
    require(old["RewardClaimed"] and new["RewardClaimed"] and new["HP"] == "0000000000000000", "Local dead claim lost")
    require({k:v for k,v in old.items() if k != "Time"} == {k:v for k,v in new.items() if k != "Time"}, "Dead histories/cursors/claim/action changed")
    require(f64(new["Time"]) >= f64(old["Time"]), "Dead clock reversed")


def fact_matches_guard(fact,fighter):
    kernel=fighter["Guard"]["Kernel"]; action=kernel["Action"]
    mapping={"entity_id":"EntityId","phase":"Phase","next_attack_id":"NextAttackId","time_bits":"Time","hp_bits":"HP","initial_time_bits":"InitialTime","next_event_id":"NextEventId","last_damage_receipt_id":"LastDamageReceiptId"}
    require(all(fact[k] == kernel[v] for k,v in mapping.items()), "Viewport Guard owner/cursor bits differ from whole Codec")
    for name in ("AttackId","Kind","ActiveAt","ActiveEnd","RecoveryEnd","Start","LockAt"):
        report_key={"AttackId":"attack_id","Kind":"attack_kind","ActiveAt":"active_at_bits","ActiveEnd":"active_end_bits","RecoveryEnd":"recovery_end_bits","Start":"action_start_bits","LockAt":"lock_at_bits"}[name]
        require(fact[report_key] == action[name], "Viewport original action bits differ: "+name)
    require(fact["content_id"] == fighter["EnemyContentId"] and fact["dead"] == fighter["Dead"] and fact["formal_death_reported"] == fighter["DeathReported"] and fact["death_observed"] == fighter["Guard"]["DeathObserved"] and fact["local_reward_claimed"] == kernel["RewardClaimed"], "Viewport Guard native mirrors differ")
    require(all(uint(fact[key]) == len(kernel[name]) for key,name in (("windows","Windows"),("closures","Closures"),("hits","HitReceipts"),("received","ReceivedHits"),("issued","Issued"))), "Viewport history counts differ")


def verify(session):
    session = Path(session).resolve()
    process = parse(read(session/"two-process-session.json"))
    require(process["schema"] == "guard-disk-v2-two-native-processes-v1", "Wrong Guard coordinator schema")
    require(len(process["processes"]) == 2 and process["sources_unchanged"] is True, "Not two frozen sequential processes")
    first,second = process["processes"]
    require(first["role"] == "source" and second["role"] == "restore" and first["pid"] != second["pid"] and min(first["pid"],second["pid"]) > 0, "Distinct actual source/restore PIDs required")
    require(first["exit_code"] == second["exit_code"] == 0 and first["exited_before_next_launch"] is True, "Source did not exit before restore")
    require(first["started_utc"] < first["exited_utc"] <= second["started_utc"] < second["exited_utc"], "Native process lifetimes overlap")
    require(first["module_sha256"] == second["module_sha256"] == process["module_sha256_before"] == process["module_sha256_after"], "DLL changed across processes")
    require(process["source_sha256_before"] == process["source_sha256_after"] and process["source_sha256_before"], "Source pins changed")
    for native_process in (first,second):
        native_log=check_fact(native_process["native_log"],session).decode("utf-8-sig",errors="replace")
        require("Guard DiskV2 two-process "+native_process["role"]+" proof complete" in native_log, "Actual native log lacks Guard completion")
    source=parse(read(session/"source/runtime-report.json")); restored=parse(read(session/"restore/runtime-report.json"))
    for report,native,role in ((source,first,"source"),(restored,second,"restore")):
        require(report["schema"] == "guard-disk-v2-two-process-role-v1" and report["role"] == role and uint(report["process_id"]) == native["pid"], "Native role/PID differs")
        require(report["passed"] is True and report["failure"] == "", "Native role failed")
        require(guid(report["profile_id"]) == guid(process["profile_id"]) and report["build_id"] == process["module_sha256_before"], "Profile/actual build pin differs")
        require(report["public_spawn_setup_only"] is True and all(report[k] is False for k in ("formal_room_encounter_complete","formal_reward_consumer_complete","guard_audio_complete","audio_device_auditioned","visual_running_proof_reviewed","audio_recorded","game_tick_called_manually")) and report["formal_complete_units"] == 0, "Proof scope widened")
    key_counts(source,{"Enter":1});key_counts(restored,{"R":1,"Enter":1})
    require({e["key"] for e in source["normal_input_requests"]} == {"Enter"} and {e["key"] for e in restored["normal_input_requests"]} == {"R","Enter"}, "Unexpected input setup")
    require(source["writer_status"] == "0" and source["commit"]["status"] == "0" and source["commit"]["generation_id"] == "1" and not source["commit"]["replayed"] and not source["commit"]["publication_may_have_succeeded"], "No actual acknowledged gen1parent0 writer Commit")
    require(restored["load_status"] == "0" and restored["all_staged_hidden_tick_collision_off"] is True and uint(restored["staged_actor_count"]) > 0, "Native pristine preparation absent")
    no_run(restored["initial_pristine"]);no_run(restored["after_real_R"])
    require(restored["initial_pristine"] == restored["after_real_R"], "Real R changed actual no-Run world")
    raw=check_fact(source["codec"],session)
    require(raw == check_fact(restored["installed_codec"],session) == check_fact(restored["paused_codec"],session), "Whole Codec bytes differ across Install/pause")
    saved=code_run(raw);deadline=code_run(check_fact(restored["deadline_codec"],session));final=code_run(check_fact(restored["continued_codec"],session))
    reentry_raw=check_fact(restored["death_reentry_before_codec"],session)
    require(reentry_raw == check_fact(restored["death_reentry_after_codec"],session) and restored["dead_observer_whole_codec_unchanged"] and restored["explicit_dead_observer_reentry_unchanged"], "Twice death observer/repeated local claim changed whole Run")
    after_hit=code_run(reentry_raw)
    require(restored["paused_wall_seconds"] >= .2 and uint(restored["installed_gate"]) == 2 and restored["controller_possesses_restored_player"] and restored["neutral_before_fresh_enter"], "Actual paused possession/neutral edge absent")
    require(uint(restored["final_gate"]) == uint(restored["restart_serial"]) == 0 and restored["late_wait_seconds"] >= .2, "Continue restarted or late wait absent")
    live_id=source["live_guard_id"];dead_id=source["dead_guard_id"]
    require((live_id,dead_id) == (restored["live_guard_id"],restored["dead_guard_id"]) and live_id != dead_id, "Stable live/dead IDs lost")
    original=guards(saved);at_end=guards(deadline);after_damage=guards(after_hit);continued=guards(final)
    old=original[live_id]["Guard"]["Kernel"];end=at_end[live_id]["Guard"]["Kernel"];hit=after_damage[live_id]["Guard"]["Kernel"];new=continued[live_id]["Guard"]["Kernel"]
    require(f64(old["HP"]) == 184. and old["Phase"] == "4" and old["Action"]["InProgress"] and old["Action"]["WindowIssued"] and uint(old["Action"]["AttackId"]) > 1, "Saved real later active Guard premise absent")
    require(all(old[key] for key in ("Windows","Closures","HitReceipts","ReceivedHits","Issued")), "Source lacks one of five actual Guard histories")
    require(old["ReceivedHits"][-1]["ActualHPLoss"] == "3ff0000000000000" and f64(old["ReceivedHits"][-1]["Stagger"]) == 85. and len(old["ReceivedHits"]) == 1, "Source actual1HP/85stagger receipt differs")
    require(old["Closures"][0]["AttackId"] == "1" and any(e["Kind"] == "9" for e in old["Issued"]) and any(e["Kind"] == "10" for e in old["Issued"]), "Source actual interrupt closure/break absent")
    require(f64(old["Action"]["ActiveAt"]) <= f64(saved["SimulationTime"]) < f64(old["Action"]["ActiveEnd"]) <= f64(deadline["SimulationTime"]), "Original active deadline premise/observation absent")
    require(end["Phase"] == new["Phase"] == "5" and old["Action"] == end["Action"] == new["Action"], "Original action identity/absolute deadlines changed")
    require(end["HitReceipts"] == old["HitReceipts"] == new["HitReceipts"] and end["Windows"] == old["Windows"] == new["Windows"] and end["Closures"] == old["Closures"] == new["Closures"], "Saved outgoing window/hit/closure replayed")
    require(end["ReceivedHits"] == old["ReceivedHits"] and end["LastDamageReceiptId"] == old["LastDamageReceiptId"], "Unexpected damage receipt before original end")
    require(end["Issued"][:-1] == old["Issued"] and end["Issued"][-1]["Kind"] == "5" and end["Issued"][-1]["AtTime"] == old["Action"]["ActiveEnd"], "Original recovery event not unique/exact deadline")
    require(hit["ReceivedHits"][:-1] == old["ReceivedHits"] and len(hit["ReceivedHits"]) == len(old["ReceivedHits"])+1 and hit["ReceivedHits"][-1]["ActualHPLoss"] == "3ff0000000000000" and f64(hit["ReceivedHits"][-1]["Stagger"]) == 0. and uint(hit["LastDamageReceiptId"]) == uint(old["LastDamageReceiptId"])+1 and f64(hit["HP"]) == f64(old["HP"])-1., "Next real receipt cursor/mitigation differs")
    require(new["ReceivedHits"] == hit["ReceivedHits"] and new["LastDamageReceiptId"] == hit["LastDamageReceiptId"] and new["Issued"] == hit["Issued"], "Late ticks duplicated receipt/events")
    require(hit["Issued"][:-1] == end["Issued"] and hit["Issued"][-1]["Kind"] == "8", "Next actual hit did not emit exactly one Damaged event")
    for snapshot,group in ((deadline,at_end),(after_hit,after_damage),(final,continued)):
        dead_invariant(original[dead_id],group[dead_id])
        require(snapshot["RunGuid"] == saved["RunGuid"] and snapshot["OwnerId"] == saved["OwnerId"] and snapshot["EnemyOrder"] == saved["EnemyOrder"], "Run/owner/enemy order changed")
        require(snapshot["Rewards"] == saved["Rewards"] and snapshot["Pickups"] == saved["Pickups"] and snapshot["Fighters"][0]["Coins"] == saved["Fighters"][0]["Coins"], "Formal rewards/physical pickups/coins changed")
        require(snapshot["Equipment"]["View"]["CombatSeed"] == saved["Equipment"]["View"]["CombatSeed"] and snapshot["Equipment"]["View"]["NextCritDraw"] == saved["Equipment"]["View"]["NextCritDraw"], "Combat RNG changed")
    fact_matches_guard(source["saved_live_guard"],original[live_id]);fact_matches_guard(source["saved_dead_guard"],original[dead_id]);fact_matches_guard(restored["original_deadline_observed"],at_end[live_id]);fact_matches_guard(restored["final_live_guard"],continued[live_id]);fact_matches_guard(restored["final_dead_guard"],continued[dead_id])
    for report,last_phase,snapshot in ((source,"6",saved),(restored,"7",final)):
        require(report["observations"][-1]["phase"] == last_phase, "Final native screenshot lacks final boundary")
        require(report["observations"][-1]["simulation_time_bits"] == snapshot["SimulationTime"], "Final captured viewport clock differs from Codec")
        group=guards(snapshot)
        fact_matches_guard(report["observations"][-1]["live_guard"],group[live_id]);fact_matches_guard(report["observations"][-1]["dead_guard"],group[dead_id])
    profiles = Path(process["profiles_directory"]).resolve()
    require(profiles.name == "BoundRunOnly-v2" and profiles.is_relative_to(session), "Wrong isolated namespace")
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
            == ("bound-run-generation-v2","bound-development-guard-v2","world-cm-v1"), "Unknown versions")
    require(struct.pack('>d',bundle["run_sim_time_or_null"]).hex() == saved["SimulationTime"] and bundle["build_id"] == process["module_sha256_before"], "Actual header clock/build mismatch")
    envelope = bundle["payload"]
    require(envelope["adapter"] == "bound-run-only-v2" and envelope["scope"] == "BoundDevelopmentRunV2"
            and envelope["generationId"] == "1" and envelope["parentGeneration"] == "0"
            and guid(envelope["profileId"]) == guid(process["profile_id"])
            and guid(envelope["runGuid"]) == codec_guid(saved["RunGuid"])
            and envelope["runSimulationTime"] == saved["SimulationTime"]
            and envelope["run"] == parse(raw), "Whole actual bundle envelope is not saved source")
    require(bundle["restored_from_generation"] == "0" and envelope["buildId"] == bundle["build_id"]
            and envelope["versions"] == {"schema":"bound-run-generation-v2","contentRules":"bound-development-guard-v2","coordinates":"world-cm-v1"},
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

    captures={role:native_capture(session/role,report) for role,report in (("source",source),("restore",restored))}
    return {"schema":"independent-guard-disk-v2-two-process-verification-v1","passed":True,
            "source_pid":first["pid"],"restore_pid":second["pid"],"full_codec_byte_equal":True,
            "actual_published_bundle_length_sha_crc_marker_verified":True,"initial_no_run_and_R_preserved":True,
            "original_guard_active_deadline_and_unique_recovery":True,"next_actual_damage_receipt_continued":True,
            "saved_dead_native_observer_and_local_claim_no_replay":True,"dead_reentry_whole_codec_byte_equal":True,
            "captures":captures,"codec":file_fact(source["codec"]["path"]),"bundle":file_fact(profile/"slot-A.bundle.json"),
            "marker":file_fact(profile/"slot-A.commit.json"),"snapshot_scope":"BoundDevelopmentRunV2 only",
            "public_spawn_setup_only":True,"formal_room_encounter_complete":False,"formal_reward_consumer_complete":False,
            "guard_audio_complete":False,"not_full_D13_profile":True,"audio_device_auditioned":False,"visual_running_proof_reviewed":False,
            "formal_complete_units":0}


if __name__ == "__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--session",required=True)
    parser.add_argument("--write-receipt",action="store_true")
    args=parser.parse_args()
    result=verify(args.session)
    if args.write_receipt:
        with (Path(args.session)/"two-process-verification-v001.json").open("x",encoding="utf-8") as stream:
            json.dump(result,stream,ensure_ascii=False,indent=2);stream.write("\n")
    print(json.dumps(result,ensure_ascii=False))
