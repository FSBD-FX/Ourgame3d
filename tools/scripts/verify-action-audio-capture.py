"""Read-only audit of one normal four-armor capture; never constructs audio.

Checks stop-frozen game facts against independent resource/equipment receipts.
Optional normalized template search in the SAME captured engine WAV is signal
evidence only: neither listening nor device-onset/latency certification.
"""
from pathlib import Path
from collections import Counter
import argparse
import hashlib
import json
import math
import struct
import wave


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def pcm(path):
    import numpy as np
    with wave.open(str(path), "rb") as wav:
        assert wav.getsampwidth() == 2 and wav.getcomptype() == "NONE", path
        rate, channels = wav.getframerate(), wav.getnchannels()
        samples = np.frombuffer(wav.readframes(wav.getnframes()), dtype="<i2")
    return samples.astype(np.float64).reshape(-1, channels).mean(axis=1) / 32768., rate


def wave_payload(path):
    data = Path(path).read_bytes()
    assert data[:4] == b"RIFF" and data[8:12] == b"WAVE", path
    at = 12
    while at + 8 <= len(data):
        tag, size = data[at:at + 4], struct.unpack_from("<I", data, at + 4)[0]
        if tag == b"data":
            assert at + 8 + size <= len(data)
            return data[at + 8:at + 8 + size]
        at += 8 + size + (size & 1)
    raise ValueError("No WAVE data chunk")


def template_search(mix, rate, template, source_rate, lower, upper):
    import numpy as np
    from scipy.signal import correlate, resample_poly
    if source_rate != rate:
        factor = math.gcd(source_rate, rate)
        template = resample_poly(template, rate // factor, source_rate // factor)
    # Fixed before inspecting any recording: polling interval expanded for
    # unmeasured mixer scheduling. This is a SEARCH window, not measured latency.
    start = max(0, int((lower - .10) * rate))
    end = min(len(mix), int((upper + .25) * rate) + len(template))
    segment = mix[start:end]
    if len(segment) < len(template):
        return {"search_complete": False, "reason": "template_longer_than_window"}
    template = template - template.mean()
    energy = float(np.dot(template, template))
    sums = np.r_[0., np.cumsum(segment)]
    squares = np.r_[0., np.cumsum(segment * segment)]
    n = len(template)
    window_energy = squares[n:] - squares[:-n] - (sums[n:] - sums[:-n]) ** 2 / n
    dot = correlate(segment, template, mode="valid", method="fft")
    score = dot / np.sqrt(np.maximum(window_energy * energy, 1e-30))
    at = int(np.argmax(score))
    # A displaced search in the same recording is a simple negative control;
    # it is reported rather than assumed silent or used to alter the threshold.
    background_start = max(0, start - rate)
    background = mix[background_start:background_start + len(segment)]
    background_peak = None
    if len(background) >= n:
        bsum = np.r_[0., np.cumsum(background)]
        bsq = np.r_[0., np.cumsum(background * background)]
        be = bsq[n:] - bsq[:-n] - (bsum[n:] - bsum[:-n]) ** 2 / n
        bd = correlate(background, template, mode="valid", method="fft")
        background_peak = float(np.max(bd / np.sqrt(np.maximum(be * energy, 1e-30))))
    return {"search_complete": True, "search_start_s": start / rate,
            "search_end_s": end / rate, "peak_ncc": float(score[at]),
            "candidate_template_start_s": (start + at) / rate,
            "template_duration_s": n / rate,
            "displaced_one_second_control_peak_ncc": background_peak,
            "displaced_control_start_s": background_start / rate,
            "displaced_control_end_s": (background_start + len(background)) / rate,
            "displaced_control_overlaps_search": background_start + len(background) > start,
            "displaced_control_not_asserted_negative": True,
            "strong_template_signal_candidate": bool(score[at] >= .75)}


def audit(report_path, manifest_path, import_path, mix_path=None):
    report, manifest, imported = map(load, (report_path, manifest_path, import_path))
    checks = []

    def check(name, condition, detail=None):
        checks.append({"name": name, "passed": bool(condition), "detail": detail})

    s = report["action_audio_capture"]
    required_names = ["xbw_armor_fixture_real_run_five_qa_sources_two_static_targets",
                      "xbw_armor_fresh_enter_opens_initialized_start_gate",
                      "xbw_armor_normal_e_035_commits_single_xbw_instance"]
    for token in ("lgt", "med", "hvy", "rob"):
        required_names.extend("xbw_armor_" + token + "_" + suffix for suffix in (
            "normal_e_050_commit", "ready_both_facings_all6_six_stack",
            "primary_both_facings_all6_actor_clock", "bolts_both_facings_frozen_socket_once",
            "reload_both_facings_all4_full_clock", "loaded3_only_after_real_commits"))
    required_names.extend(("xbw_armor_history_immutable_once_same_weapon_instance",
                           "xbw_armor_completed_within_55s"))
    check("normal_profile_passed", report["passed"] and len(report["checks"]) == 29
          and Counter(x["name"] for x in report["checks"]) == Counter(required_names)
          and all(x["passed"] for x in report["checks"])
          and s["profile"] == "xbw_four_armor_socket_normal_inputs")
    check("frozen_valid_before_stop", s["schema"] == 1 and s["valid"] and s["frozen"]
          and s["snapshot_taken_before_stop_request"] and not s["failures"])
    b, p = s["boundaries"], s["polling"]
    check("same_stop_boundary_as_original_recorder",
          b["capture_start_monotonic_s"] == report["capture_timing"]["capture_start_monotonic_s"]
          and b["capture_stop_boundary_monotonic_s"] == report["capture_timing"]["capture_stop_monotonic_s"])
    check("native_freeze_order", b["capture_stop_boundary_monotonic_s"]
          <= b["freeze_begin_monotonic_s"] <= b["freeze_end_monotonic_s"])
    check("untruncated_single_hud_polling", not p["poll_log_truncated"] and not p["observation_log_truncated"]
          and p["missing_game_polls"] == p["missing_hud_polls"] == p["duplicate_keys_within_poll"]
          == p["keys_seen_after_hud_rebuild"] == 0 and p["hud_generation_count"] == 1)
    facts, requests, observations = s["facts"]["records"], s["hud"]["receipts"], p["observations"]
    cue_map = {c["id"].removeprefix("AUD-").replace("-", "_"): c for c in manifest["cues"]}
    import_map = {c["id"]: c for c in imported["assets"]}
    check("exact_five_source_import_binding", len(cue_map) == len(import_map) == 5
          and imported["success"] and imported["actual_count"] == imported["saved_count"] == 5
          and imported["manifest_sha256"] == digest(manifest_path))
    source_checks = []
    for cue, source in cue_map.items():
        actual = import_map[source["id"]]
        ok = digest(source["file"]) == source["sha256"] == actual["source_sha256"]
        ok &= actual["object_path"] == source["object_path"] and actual["saved"]
        ok &= actual["actual_object_type"] == "SoundWave" and not actual["looping"]
        source_checks.append({"cue": cue, "source_wav": source["file"],
                              "source_sha256": source["sha256"], "object_path": source["object_path"], "passed": ok})
    check("source_wav_and_actual_import_exact", all(x["passed"] for x in source_checks), source_checks)
    required_ids = ("sequence", "room_instance_id", "owner_id", "action_id", "instance_id", "operation_id", "revision")
    check("lossless_uint64_ids", s["uint64_encoding"] == "decimal_string" and all(
        all(isinstance(f[k], str) and f[k].isdigit() for k in required_ids) for f in facts))
    fact_by_key = {(f["run_guid"], f["sequence"]): f for f in facts}
    request_by_key = {(r["source"]["run_guid"], r["source"]["sequence"]): r for r in requests}
    observation_by_key = {(o["request"]["source"]["run_guid"], o["request"]["source"]["sequence"]): o for o in observations}
    check("every_fact_exactly_one_request_and_poll_observation", len(fact_by_key) == len(facts)
          == len(request_by_key) == len(requests) == len(observation_by_key) == len(observations)
          and fact_by_key.keys() == request_by_key.keys() == observation_by_key.keys())
    check("journal_sequence_complete", [int(f["sequence"]) for f in facts] == list(range(1, len(facts) + 1))
          and int(s["facts"]["next_sequence"]) == len(facts) + 1)
    check("same_run_room_owner", all(f["run_guid"] == b["stop_run_guid"]
          and f["room_instance_id"] == b["stop_room_instance_id"]
          and f["owner_id"] == b["stop_owner_id"] for f in facts))
    for key, r in request_by_key.items():
        f, o = fact_by_key.get(key), observation_by_key.get(key)
        cue = r["source"]["cue"]
        check("request_source_exact_" + key[1], f == r["source"] and o is not None and o["request"] == r)
        if f is None or o is None or cue not in cue_map:
            continue
        check("request_path_and_time_" + key[1], r["sound_path"] == cue_map[cue]["object_path"]
              and f["at_time"] <= r["requested_at"] <= b["capture_stop_sim_s"]
              and r["requested_at"] - f["at_time"] <= .25 and r["pitch"] == 1 and 0 < r["volume"] <= 1)
        check("poll_interval_" + key[1], o["poll_interval_valid"] and not o["preexisting_at_capture_start"]
              and 0 <= o["previous_poll_wall_offset_s"] <= o["request_first_observed_wall_offset_s"]
              <= b["freeze_end_monotonic_s"] - b["capture_start_monotonic_s"])
    armor = s["four_armor_pickups"]
    histories = [r for r in s["resources"]["weapon_runtime_history"] if r["kind_name"] == "ReloadCompleted"]
    operations = {o["operation_id"]: o for o in s["inventory"]["operations"]}
    updates = s["inventory"]["runtime_updates"]
    sources = {o["source_id"]: o for o in s["inventory"]["sources"]}
    items = {o["instance_id"]: o for o in s["inventory"]["items"]}
    weapon_pickup = armor["weapon_pickup"]
    weapon_op = operations.get(weapon_pickup["operation_id"])
    weapon_source = sources.get(weapon_pickup["source_id"])
    weapon_item = items.get(armor["xbw_instance_id"])
    weapon_ok = weapon_op is not None and weapon_source is not None and weapon_item is not None
    if weapon_ok:
        weapon_ok &= weapon_item["content_id"] == weapon_source["spawn_item"]["content_id"] == "WPN-XBW-001"
        weapon_ok &= weapon_pickup["instance_id"] == armor["xbw_instance_id"] == weapon_item["instance_id"] == weapon_source["spawn_item"]["instance_id"]
        weapon_ok &= weapon_op["result"]["ok"] and not weapon_op["result"]["replayed"]
        weapon_ok &= weapon_op["request"]["action_name"] == "Pickup" and weapon_op["request"]["source_id"] == weapon_pickup["source_id"]
        weapon_ok &= weapon_op["result"]["acquired_id"] == armor["xbw_instance_id"] == s["resources"]["equipped_instance_id"]
    check("actual_xbw_source_pickup_and_owned_item", weapon_ok)
    n = len(histories)
    check("real_reload_count_from_resource_history", armor["enabled"] and n == armor["shot_count"]
          == 8 + armor["global_retry_shots"] and 0 <= armor["global_retry_shots"] <= 2)
    expected = {k: n for k in cue_map if k.startswith("XBW_RELOAD_")}
    expected.update(EQUIP_ARMOR_CLOTH_01=2, EQUIP_ARMOR_METAL_01=2)
    counts = Counter(f["cue"] for f in facts)
    check("all_five_cue_counts", dict(counts) == expected and dict(s["hud"]["counts"]) == expected, dict(counts))
    for h in histories:
        a = h["action"]
        rows = [f for f in facts if f["action_id"] == a["action_id"] and f["cue"].startswith("XBW_RELOAD_")]
        times = {f["cue"]: f["at_time"] for f in rows}
        target = {"XBW_RELOAD_DRAW_01": a["start"] + (a["end"] - a["start"]) * (.20 / 1.10),
                  "XBW_RELOAD_INSERT_01": a["start"] + (a["end"] - a["start"]) * (.60 / 1.10),
                  "XBW_RELOAD_COMPLETE_01": a["end"]}
        # Only this exported-number arithmetic comparison permits 1e-12 s for
        # decimal JSON round-trip; native exact event tests remain unchanged.
        ok = len(rows) == 3 and times.keys() == target.keys() and all(abs(times[k] - v) <= 1e-12 for k, v in target.items())
        ok &= h["before_ammo"] == 0 and h["after_ammo"] == 1 and h["at_time"] == a["end"]
        ok &= all(f["instance_id"] == armor["xbw_instance_id"] == a["instance_id"] for f in rows)
        matched_updates = [u for u in updates if u["instance_id"] == a["instance_id"]
                           and abs(u["at_time"] - a["end"]) <= 1e-12
                           and u["before_ammo"] == 0 and u["ammo"] == 1]
        ok &= len(matched_updates) == 1
        if len(matched_updates) == 1:
            u = matched_updates[0]
            complete = next((f for f in rows if f["cue"] == "XBW_RELOAD_COMPLETE_01"), None)
            ok &= u["result"]["ok"] and not u["result"]["replayed"]
            ok &= int(u["result"]["revision"]) == int(u["base_revision"]) + 1
            ok &= int(u["after_version"]) == int(u["before_version"]) + 1
            ok &= complete is not None and complete["revision"] == u["result"]["revision"]
        check("reload_resource_and_stages_" + a["action_id"], ok)
    for a in armor["armors"]:
        pickup = a["pickup"]
        op = operations.get(pickup["operation_id"])
        source = sources.get(a["source_id"])
        rows = [f for f in facts if f["operation_id"] == pickup["operation_id"]]
        cue = "EQUIP_ARMOR_CLOTH_01" if a["token"] in ("lgt", "rob") else "EQUIP_ARMOR_METAL_01"
        ok = a["committed"] and a["pickup_observed"] and op is not None and source is not None and len(rows) == 1
        if ok:
            f = rows[0]
            ok &= f["cue"] == cue and f["action_id"] == pickup["action_id"] and f["at_time"] == pickup["deadline"]
            ok &= f["instance_id"] == a["instance_id"] == pickup["instance_id"] == op["result"]["acquired_id"]
            ok &= op["request"]["source_id"] == a["source_id"] and op["request"]["action_name"] == "Pickup"
            ok &= op["result"]["ok"] and not op["result"]["replayed"] and f["revision"] == op["result"]["revision"]
            ok &= source["spawn_item"]["instance_id"] == a["instance_id"] and source["spawn_item"]["content_id"] == a["id"]
        check("armor_commit_material_" + a["token"], ok)
    signals = []
    if mix_path:
        expected_mix = (report_path.parent / report["audio_file"]).resolve()
        original_mix = (report_path.parent / report["audio_engine_original"]).resolve()
        check("same_capture_wav_and_original_pcm", mix_path.resolve() == expected_mix
              and report["audio_recorded"] and report["audio_PCM_payload_unchanged"]
              and original_mix.is_file() and wave_payload(mix_path) == wave_payload(original_mix))
        mix, rate = pcm(mix_path)
        for o in observations:
            cue = o["request"]["source"]["cue"]
            if cue not in cue_map or not o["poll_interval_valid"]:
                continue
            template, source_rate = pcm(cue_map[cue]["file"])
            result = template_search(mix, rate, template, source_rate,
                                     o["previous_poll_wall_offset_s"], o["request_first_observed_wall_offset_s"])
            signals.append({"cue": cue, "sequence": o["request"]["source"]["sequence"], **result})
    return {"schema": "action-audio-capture-audit-v1", "passed": all(c["passed"] for c in checks),
            "report": str(report_path), "report_sha256": digest(report_path),
            "manifest_sha256": digest(manifest_path), "import_sha256": digest(import_path),
            "mix": str(mix_path) if mix_path else None, "mix_sha256": digest(mix_path) if mix_path else None,
            "checks": checks, "source_bindings": source_checks, "counts": dict(counts),
            "signal_search": signals, "signal_candidate_threshold_fixed_before_capture": .75,
            "strong_template_candidates": sum(x.get("strong_template_signal_candidate", False) for x in signals),
            "auditioned": False, "final_mix_accepted": False, "formal_complete_units": 0,
            "limitations": ["Structural pass certifies this capture's game facts and playback requests only.",
                            "Template correlation is auxiliary signal evidence, not listening or unique sound identity proof.",
                            "Polling visibility intervals and expanded search windows do not measure audio onset/latency."]}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", required=True, type=Path)
    parser.add_argument("--manifest", type=Path, default=Path("F:/Ourgame/source-assets/production/first-batch-audio-v002/manifest.json"))
    parser.add_argument("--import-receipt", type=Path, default=Path("F:/Ourgame/UnrealGame/Saved/Bootstrap/first-batch-audio-v002-import-20261015-102740-981456.json"))
    parser.add_argument("--mix", type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    assert not args.out.exists(), "Evidence output must not overwrite a prior version"
    result = audit(args.report, args.manifest, args.import_receipt, args.mix)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"passed": result["passed"], "checks": len(result["checks"]),
                      "failed": [c["name"] for c in result["checks"] if not c["passed"]],
                      "counts": result["counts"], "strong_template_candidates": result["strong_template_candidates"],
                      "signal_searches": len(result["signal_search"]), "out": str(args.out)}, ensure_ascii=False))
    raise SystemExit(0 if result["passed"] else 1)
