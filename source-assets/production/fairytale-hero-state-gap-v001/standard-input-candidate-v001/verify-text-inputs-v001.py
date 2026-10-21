"""Candidate authoring validation only; no UE/native tests, media, or gameplay writes."""
from __future__ import annotations
import ast
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
PROJECT = Path("F:/Ourgame")


def pin(path):
    data = path.read_bytes()
    return {"path": path.as_posix(), "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}


def write_new(path, value):
    if path.exists():
        raise ValueError("Never overwrite authoring evidence: " + str(path))
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main():
    refs = json.loads((HERE / "reference-pins-v001.json").read_text(encoding="utf-8"))
    for record in refs["files"]:
        assert pin(Path(record["file"]["path"])) == record["file"]
    audit_path = HERE.parent / "audit-freeze-v001.json"
    audit = json.loads(audit_path.read_text(encoding="utf-8"))
    for record in audit["files"]:
        assert pin(Path(record["path"])) == record
    request = json.loads((HERE / "sprite-request.json").read_text(encoding="utf-8"))
    timeline = json.loads((HERE / "runtime-timing-annotations-v001.json").read_text(encoding="utf-8"))
    assert [(s, e["frames"], e["fps"]) for s, e in request["states"].items()] == [("dodge", 4, 10), ("hurt", 4, 10), ("death", 5, 5)]
    assert request["character"]["base_image"] is None and "rig" not in request
    for state, entry in request["states"].items():
        assert entry["loop"] is False and "durations_ms" not in entry
        guide = json.loads((HERE / f"references/layout-guides/{state}.guide.json").read_text(encoding="utf-8"))
        assert len(guide["cells"]) == entry["frames"] and guide["canvas_px"] == [512 * entry["frames"], 512]
        for index, cell in enumerate(guide["cells"]):
            assert cell["frame"] == index and cell["rect"] == [512 * index, 0, 512, 512]
        frames = timeline["states"][state]["frames"]
        assert len(frames) == entry["frames"]
        for row in frames:
            assert all(value is None for key, value in row.items() if key.startswith("actual_"))
    python_files = sorted(HERE.glob("*.py"))
    for path in python_files:
        ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    spec = importlib.util.spec_from_file_location("candidate_timing", HERE / "timing-contract-v001.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    checks = []
    for age, protected in [(.059, False), (.06, True), (.199, True), (.20, False)]:
        result = module.sample({"state": "dodge", "record_start_seconds": 0., "kernel_time_seconds": age,
                                "kernel_phase": "Dodging", "finish": "None"})
        assert result["direct_contact_protected_at_observation"] == protected
        checks.append({"role": "synthetic absolute-time boundary example", "age": age, "result": result})
    long_start = 100000.
    result = module.sample({"state": "dodge", "record_start_seconds": long_start,
                            "kernel_time_seconds": long_start + .06, "kernel_phase": "Dodging"})
    assert result["direct_contact_protected_at_observation"] is True
    checks.append({"role": "absolute Start+iframe boundary example; no cancellation epsilon", "result": result})
    result = module.sample({"state": "dodge", "record_start_seconds": 0., "kernel_time_seconds": .4,
                            "kernel_phase": "Idle", "finish": "Completed", "record_finished_at_seconds": .4})
    assert result["frame"] is None and result["travel_world"] == 185.
    checks.append({"role": "completed native endpoint example; no last dodge frame after Idle", "result": result})
    result = module.sample({"state": "dodge", "record_start_seconds": 0., "kernel_time_seconds": .3,
                            "kernel_phase": "Dodging", "block": "Wall", "actual_record_travelled_world": 12.})
    assert result["active"] is True and result["travel_world"] == 12.
    checks.append({"role": "synthetic blocked example, never a real travel measurement", "result": result})
    for age, frame, hold in [(.0, 0, False), (.2, 1, False), (.4, 2, False), (.6, 3, False), (.8, 4, True), (30., 4, True)]:
        result = module.sample({"state": "death", "age_seconds": age, "bDead": True})
        assert (result["frame"], result["settled_visual_hold"]) == (frame, hold)
        checks.append({"role": "synthetic death art sampling example, not gameplay duration", "age": age, "result": result})
    assert "HitFlash" in module.hit_presentation({"hp_before": 100, "hp_after": 99, "accepted": True, "actual_poise_broken": False})
    assert "Hurt .40" in module.hit_presentation({"hp_before": 100, "hp_after": 99, "accepted": True, "actual_poise_broken": True})
    assert "No Hurt" in module.hit_presentation({"hp_before": 100, "hp_after": 99, "accepted": True, "damage_over_time": True})
    assert "Death" in module.hit_presentation({"hp_before": 1, "hp_after": 0, "accepted": True, "damage_over_time": True})
    sections = [
        ("DungeonDodge.h", 11, 15, "Native duration, travel, iframe and cooldown constants"),
        ("DungeonDodge.h", 58, 61, "Protected uses absolute Start+ boundaries and clips at actual interruption"),
        ("DungeonDodge.h", 138, 148, "Normalized MoveIntent or zero-intent Facing fallback; no facing mutation"),
        ("DungeonDodge.h", 149, 167, "Blocked travel freezes, completion only at unchanged native End"),
        ("DungeonDodge.h", 172, 183, "Poise/death interruptions and protected direct contact restriction"),
        ("DungeonFighter.cpp", 766, 790, "Real dodge admission, shared equipment/attack gates and successful action interrupts"),
        ("DungeonFighter.cpp", 795, 803, "Public native Dodge state drives position and presentation age"),
        ("DungeonFighter.cpp", 1325, 1330, "Dead/dodge/hurt/exclusive actions reject new attack admission"),
        ("DungeonFighter.cpp", 1435, 1441, "Dead or unaccepted protected direct contacts do not newly apply hit"),
        ("DungeonFighter.cpp", 1486, 1529, "DoT vs direct hit, poise break/Hurt, lethal interrupts"),
        ("DungeonFighter.cpp", 1799, 1805, "Terminal display clock continues without gameplay tick"),
        ("DungeonFighter.cpp", 1815, 1829, "Hurt countdown; dead branch advances only death presentation and height"),
        ("DungeonFighter.cpp", 1897, 1904, "State selection after authority transitions"),
        ("DungeonGameMode.cpp", 1205, 1228, "Actual body capture carries bAlive=false after death"),
        ("DungeonGameMode.cpp", 1328, 1336, "Shared resolved movement/dodge sweep skips nonliving bodies"),
        ("DungeonGameMode.cpp", 1660, 1668, "Weapon skill forward sweep skips nonliving bodies"),
        ("DungeonGameMode.cpp", 1888, 1896, "Game-over uses terminal animation, does not advance SimulationTime"),
        ("DungeonGameMode.cpp", 2329, 2339, "Player death sets game-over once; restart is separate input route"),
        ("DungeonHUD.cpp", 1118, 1132, "Old6 sampling is legacy display reference only; no new-body authority"),
    ]
    evidence = []
    for name, first, last, meaning in sections:
        path = PROJECT / "UnrealGame/Source/CodexDungeon" / name
        lines = path.read_text(encoding="utf-8-sig").splitlines()
        evidence.append({"source": pin(path), "first_line": first, "last_line": last, "meaning": meaning,
                         "exact_lines": [{"line": n, "text": lines[n-1]} for n in range(first, last+1)]})
    write_new(HERE / "source-rule-evidence-v001.json", {"schema": "hero-state-source-rule-evidence-v001", "sections": evidence})
    report = {"schema": "hero-state-text-authoring-validation-v001", "scope": "AUTHORING_SANITY_ONLY_SYNTHETIC_INPUTS_NO_NATIVE_TEST_RUN",
              "original_audit_files_unchanged": len(audit["files"]), "reference_pins_verified": len(refs["files"]),
              "python_AST_files": len(python_files), "numeric_rows_and_unknown_marker_fields_verified": True,
              "guide_rasters_written": 0, "native_or_UE_tests_run": 0, "image_generation_calls": 0,
              "synthetic_contract_examples": checks, "art_accepted": False, "runtime_implemented": False}
    write_new(HERE / "input-authoring-validation-v001.json", report)
    print(json.dumps({"scope": report["scope"], "audit_files_unchanged": len(audit["files"]),
                      "reference_pins": len(refs["files"]), "new_images": 0, "native_tests": 0}))


if __name__ == "__main__":
    main()
