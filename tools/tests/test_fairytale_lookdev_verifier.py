"""Synthetic verifier rejection tests. These are not actual UE capture evidence."""
import copy
import importlib.util
from pathlib import Path
import unittest
import math

spec = importlib.util.spec_from_file_location("lookdev_verifier", Path(__file__).parents[1] / "scripts/verify-fairytale-lookdev.py")
verifier = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verifier)


class ObservationRejections(unittest.TestCase):
    def fixture(self):
        baseline = {"available": True, "mode": True, "waiting": True, "player_tick_enabled": False, "enemies": []}
        report = {"schema": "fairytale-lookdev-capture-v1", "profile": "fairytale_idle_observation_silent", "passed": True,
                  "silent_video": True, "audio_capture_started": False, "native_async_flush_after_audio_stop": False,
                  "formal_complete_units": 0, "new_style_accepted": False, "motion_reviewed": False, "auditioned": False,
                  "baseline_game": baseline,
                  "capture_timing": {"capture_start_monotonic_s": 100., "capture_stop_monotonic_s": 107.22,
                                     "requested_video_wall_duration_s": 7.22, "use_fixed_time_step": False, "frame_wall_offsets_s": []},
                  "prewarm_screenshot": {"requested": True, "completed_file_received": True, "used_as_recording_frame": False,
                                         "request_monotonic_s": 99., "complete_monotonic_s": 100.},
                  "observations": [], "normal_input_requests": []}
        for n in range(432):
            offset = (n + 1) / 60
            wall = 100 + offset - .001
            elapsed = wall - 98
            sample = math.floor(elapsed / .167)
            left = 2.4 <= offset < 4.8
            row = {"wall_offset_s": offset, "hud_available": True, "active": True, "configuration_confirmed": True,
                   "game": copy.deepcopy(baseline), "interface_visible": False, "text_draw_calls": 0,
                   "legacy_stack_count": 0, "action_audio_requests": 0, "legacy_weapon_used": False,
                   "viewport": [1280, 720], "ui_scale": 1., "draw_serial": str(n + 1), "draw_wall": wall,
                   "animation_elapsed_s": elapsed, "input_A": left, "input_D": not left, "camera_ground_center": [0., 0.]}
            for actor in ("hero", "stone"):
                frame = sample % 4
                side = (-1 if left else 1) * (1 if actor == "hero" else -1)
                flipped = side != verifier.NATIVE[actor]
                root = verifier.ROOTS[actor][frame]
                x, y = (435.2 if actor == "hero" else 819.2), 540
                rx = 512 - root[0] if flipped else root[0]
                row[actor] = {"sample": str(sample), "frame": frame, "facing": side, "native_facing": verifier.NATIVE[actor],
                              "flipped": flipped, "path": verifier.expected_path(actor, frame), "texture_ready": True,
                              "root": root, "canvas_size": verifier.CANVAS[actor], "ground_screen": [x, y],
                              "ground": [(x - 640) / .65, (490 - y) / .38],
                              "top_screen": [x - verifier.CANVAS[actor] * rx / 512, y - verifier.CANVAS[actor] * root[1] / 512]}
            report["observations"].append(row)
            report["capture_timing"]["frame_wall_offsets_s"].append(offset)
        for key in ("A", "D", "W", "S", "J", "K", "E", "Q", "T", "R", "Enter", "SpaceBar", "LeftShift"):
            report["normal_input_requests"] += [{"key": key, "down": True}, {"key": key, "down": False}]
        return report

    def test_accepts_only_complete_synthetic_contract(self):
        result = verifier.validate_observations(self.fixture())
        self.assertEqual(result["observations"], 432)
        self.assertTrue(all(v >= 2 for v in result["wraps_3_to_0"].values()))

    def test_rejects_legacy_identity_even_if_report_claims_pass(self):
        report = self.fixture()
        report["observations"][55]["hero"]["path"] = "/Game/Production/FirstBatch/v016/XBWReadyIdle/body"
        with self.assertRaisesRegex(ValueError, "identity"):
            verifier.validate_observations(report)

    def test_rejects_missing_real_draws(self):
        with self.assertRaises(ValueError):
            verifier.validate_observations({"passed": True, "observations": []})

    def test_rejects_false_silent_or_simulation_claim(self):
        report = self.fixture()
        report["audio_capture_started"] = True
        with self.assertRaisesRegex(ValueError, "audio"):
            verifier.validate_observations(report)
        report = self.fixture()
        report["observations"][-1]["game"]["simulation_time"] = .001
        with self.assertRaisesRegex(ValueError, "advanced"):
            verifier.validate_observations(report)

    def test_rejects_incorrect_stone_native_mirror(self):
        report = self.fixture()
        report["observations"][180]["stone"]["flipped"] = False
        with self.assertRaisesRegex(ValueError, "mirroring"):
            verifier.validate_observations(report)

    def test_rejects_incorrect_idle_clock(self):
        report = self.fixture()
        report["observations"][180]["animation_elapsed_s"] += .167
        with self.assertRaisesRegex(ValueError, "epoch"):
            verifier.validate_observations(report)


if __name__ == "__main__":
    unittest.main()
