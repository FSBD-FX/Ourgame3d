"""Tooling unit fixtures only. No UE, original PNG, capture or pass receipt is created."""
from pathlib import Path
import copy
import importlib.util
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("p1_candidate", HERE / "postprocess-leather-primary1-trial-v001.py")
tool = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tool)


def fixture():
    downs = [("Enter", .01, 0.), ("E", .2, .6), ("A", .35, .75), ("E", .8, 1.2), ("J", 1.4, 1.8), ("D", 3.3, 3.7), ("J", 3.5, 3.9)]
    inputs = []
    for key, wall, sim in downs:
        inputs += [{"key": key, "down": True, "wall_offset_s": wall, "sim": sim}, {"key": key, "down": False, "wall_offset_s": wall + .08, "sim": sim + .08}]
    rows = []
    def row(step, sim, wall, light=False, pending=False, supported=True, facing=-1, frame=0, action=0, times=(0, 0, 0, 0)):
        primary = action > 0
        body = tool.object_path(tool.BODY, f"T_Fairytale_Sword{'Primary1' if primary else 'Ready'}_{frame:03d}_v002")
        gear = supported or pending
        stack = tool.expected_stack(frame, primary) if light and gear else [body, tool.SWORD, body] if gear else [body]
        result = {"run": "a" * 32, "run_alias": "1", "owner_id": "9", "committed_weapon_id": "7", "committed_weapon_version": "2", "active_slot": 0,
            "draw_id": str(100 + len(rows)), "active": True, "supported": supported, "texture_ready": True, "armor_ready": light and gear,
            "armor_drawn": light and gear, "armor_preview": light, "sim": sim, "actual_sim": sim, "wall_offset_s": wall,
            "flow_step": step, "flow_phase": tool.PHASES[step], "body_max_contract": 72, "canvas_size": tool.CANVAS,
            "interface_visible": False, "text_calls": 0, "facing": facing, "frame": frame, "stage": 0 if primary else -1,
            "action_id": str(action), "clip": "sword_primary_1" if primary else "sword_ready_idle", "weapon_mirror": "WPN-SWD-001",
            "armor_mirror": "ARM-LGT-001" if light else "", "committed_armor_id": "8" if light else "0", "committed_armor_version": "2" if light else "0",
            "operation_count": "1" if light else "0", "next_operation_id": "2" if light else "1", "expected_armor_mode": "light_armor" if light else "no_armor",
            "pending_equipment_action": pending, "pending_equipment_kind": 2 if pending else 0, "pending_instance_id": "8" if pending else "0",
            "equipment_deadline": 1.1 if step == 2 else 1.7 if step == 4 else 0., "animation": "equip_armor" if pending else "idle" if supported else "walk",
            "committed_gear_placeholder_expected": pending, "melee_pending_primary": False, "texture": body, "draw_stack": stack,
            "draw_stack_has_armor": light and gear, "weapon": tool.SWORD if gear else "", "instance_id": "7", "weapon_scale": .5,
            "root": [256., 350.], "grip": [260., 300.], "grip_screen": [640., 350.],
            "start": times[0], "active_at": times[1], "active_end": times[2], "end": times[3]}
        rows.append(result)
    row(0, .4, .04); row(1, .5, .12); row(2, .65, .25, pending=True, supported=False)
    row(3, .9, .5, supported=False); row(4, 1.3, .9, pending=True, supported=False)
    for sim, wall in ((1.72, 1.32), (1.75, 1.35), (1.78, 1.38)): row(5, sim, wall, light=True)
    for frame, sim in enumerate((1.81, 2.01, 2.11, 2.3, 2.6, 2.9)): row(6, sim, sim - .4, light=True, frame=frame, action=10, times=(1.8, 2., 2.2, 3.))
    for sim in (3.05, 3.15, 3.25): row(6, sim, sim - .4, light=True)
    for frame, sim in enumerate((3.91, 4.12, 4.2, 4.4, 4.7, 5.)): row(6, sim, sim - .4, light=True, facing=1, frame=frame, action=11, times=(3.9, 4.1, 4.3, 5.1))
    for sim in (5.15, 5.25, 5.35): row(6, sim, sim - .4, light=True, facing=1)
    phases = [{"step": i, "phase": tool.PHASES[i], "sim": sim, "wall_offset_s": wall} for i, sim, wall in
              ((0, .4, .11), (1, .6, .2001), (2, .75, .3501), (3, 1.2, .8001), (4, 1.7, 1.3), (5, 1.8, 1.4001), (6, 5.36, 4.96))]
    report = {"schema": "fairytale-equipment-bound-native-flow-v1", "leather_primary1_only_trial": True, "leather_ready_only_trial": False,
        "scope": tool.PRIMARY1_SCOPE, "passed": True, "flow_complete": True, "reason": "", "failure": "", "mismatches": [], "formal_complete_units": 0,
        "silent_video": True, "audio_recorded": False, "native_async_capture_writes_flushed": True, "leather_primary1_masks_left_right": [63, 63],
        "light_primary_phase_masks": [63, 0, 0], "leather_ready_phase_masks_left_right": [0, 0], "medium_instance_id": "0", "medium_source_id": "0",
        "original_light_drop_source": "0", "light_instance_id": "8", "light_source_id": "4", "leather_primary1_attack_ids_left_right": ["10", "11"],
        "observations": rows, "normal_input_requests": inputs, "inputevents": copy.deepcopy(inputs), "phasechecks": phases, "duration_s": 5.1}
    index = {"runtime_passed": True, "exit_code": 0, "observations": len(rows)}
    packages = {tool.package_file(path): {} for entry in rows for path in entry["draw_stack"] + [entry["texture"]]}
    return report, index, packages


class CandidateContract(unittest.TestCase):
    def test_synthetic_positive_oracle_only(self):
        report, index, packages = fixture()
        selected, result = tool.verify_flow(report, index, packages)
        self.assertEqual(len(selected), 12)
        self.assertEqual(result["fresh_final_actual_ready_observations"], 3)
        self.assertEqual(result["formal_complete_units"], 0)

    def test_wrong_scope_flow_identity_inputs_and_layers_reject(self):
        mutate = [
            ("ready-only", lambda r, i, p: r.update(leather_ready_only_trial=True)),
            ("wrong native scope", lambda r, i, p: r.update(scope="full bound flow")),
            ("native red", lambda r, i, p: r.update(passed=False)),
            ("complete-unit claim", lambda r, i, p: r.update(formal_complete_units=1)),
            ("forced clock", lambda r, i, p: r.update(forced_clock=True)),
            ("unflushed", lambda r, i, p: r.update(native_async_capture_writes_flushed=False)),
            ("audio", lambda r, i, p: r.update(audio_recorded=True)),
            ("P2 mask", lambda r, i, p: r.update(light_primary_phase_masks=[63, 1, 0])),
            ("missing phase bit", lambda r, i, p: r.update(leather_primary1_masks_left_right=[31, 63])),
            ("same attack ID", lambda r, i, p: r.update(leather_primary1_attack_ids_left_right=["10", "10"])),
            ("medium flow", lambda r, i, p: r.update(medium_instance_id="3")),
            ("missing observation", lambda r, i, p: i.update(observations=1)),
            ("failed process", lambda r, i, p: i.update(exit_code=1)),
            ("input alias", lambda r, i, p: r["inputevents"][0].update(key="J")),
            ("unpaired release", lambda r, i, p: (r["normal_input_requests"][0].update(down=False), r["inputevents"][0].update(down=False))),
            ("unknown key", lambda r, i, p: (r["normal_input_requests"][0].update(key="Q"), r["inputevents"][0].update(key="Q"))),
            ("rewound phase", lambda r, i, p: r["phasechecks"][3].update(sim=.1)),
            ("wrong phase namespace", lambda r, i, p: r["observations"][8].update(flow_phase="complete")),
            ("owner", lambda r, i, p: r["observations"][-1].update(owner_id="99")),
            ("sword version", lambda r, i, p: r["observations"][-1].update(committed_weapon_version="3")),
            ("armor version", lambda r, i, p: r["observations"][-1].update(committed_armor_version="3")),
            ("second commit", lambda r, i, p: r["observations"][-1].update(operation_count="2")),
            ("UI", lambda r, i, p: r["observations"][8].update(interface_visible=True)),
            ("canvas", lambda r, i, p: r["observations"][8].update(canvas_size=72.)),
            ("nonfinite clock", lambda r, i, p: r["observations"][8].update(actual_sim=float("nan"))),
            ("wrong stage", lambda r, i, p: r["observations"][8].update(stage=1)),
            ("other attack clip", lambda r, i, p: r["observations"][8].update(clip="sword_primary_2")),
            ("queued combo", lambda r, i, p: r["observations"][8].update(melee_pending_primary=True)),
            ("pending supported lie", lambda r, i, p: r["observations"][2].update(supported=True)),
            ("wrong drawn armor", lambda r, i, p: r["observations"][8].update(committed_armor_id="999")),
            ("wrong sword scale", lambda r, i, p: r["observations"][8].update(weapon_scale=.6)),
            ("seven stack P1", lambda r, i, p: r["observations"][8]["draw_stack"].pop(5)),
            ("wrong far namespace", lambda r, i, p: r["observations"][8]["draw_stack"].__setitem__(1, r["observations"][8]["draw_stack"][1].replace("v013", "v012"))),
            ("wrong body namespace", lambda r, i, p: r["observations"][8].update(texture=r["observations"][8]["texture"].replace("v005", "v007"))),
            ("missing package", lambda r, i, p: p.pop(tool.package_file(tool.SWORD))),
            ("repeated draw", lambda r, i, p: r["observations"][8].update(draw_id="100")),
            ("final Ready not actual", lambda r, i, p: r["observations"][-1].update(animation="walk")),
            ("marker NaN", lambda r, i, p: r["observations"][8].update(root=[float("nan"), 350.])),
        ]
        for name, mutation in mutate:
            with self.subTest(name=name):
                report, index, packages = fixture(); mutation(report, index, packages)
                with self.assertRaises(ValueError): tool.verify_flow(report, index, packages)

    def test_actual_coverage_and_final_ready_not_report_masks(self):
        report, index, packages = fixture()
        target = next(row for row in report["observations"] if row["action_id"] == "10" and row["frame"] == 5)
        target["frame"] = 4
        target["texture"] = tool.object_path(tool.BODY, "T_Fairytale_SwordPrimary1_004_v002")
        target["draw_stack"] = tool.expected_stack(4)
        with self.assertRaises(ValueError): tool.verify_flow(report, index, packages)
        report, index, packages = fixture()
        for row in report["observations"]:
            if row["action_id"] == "11": row["end"] = 6.
        with self.assertRaises(ValueError): tool.verify_flow(report, index, packages)

    def test_exact_verified_pixel_function_reused(self):
        base = Path("F:/Ourgame/tools/scripts/postprocess-leather-ready-trial-v001.py").read_text(encoding="utf-8-sig")
        candidate = (HERE / "postprocess-leather-primary1-trial-v001.py").read_text(encoding="utf-8")
        self.assertEqual(base[base.index("def verify_pixels("):base.index("def main(")].strip(), candidate[candidate.index("def verify_pixels("):candidate.index("def write_whole_phase_view(")].strip())

    def test_pixel_mode_negative_before_any_output(self):
        with patch.object(tool, "read", return_value={"mode": "fake_screenshot"}):
            with self.assertRaises(ValueError): tool.verify_pixels(HERE / "NOT_AN_ACTUAL_CAPTURE", {})

    def test_assembly_reference_mandatory_and_count_not_downgraded(self):
        for pin in (None, "guessed-folder", {"path": "../escape", "bytes": 1}, {}):
            with self.subTest(pin=pin):
                with self.assertRaises(ValueError): tool.root_pin(pin, "assembly")
        with self.assertRaises(ValueError): tool.verify_sources(HERE, {}, 154)


if __name__ == "__main__":
    unittest.main(verbosity=2)
