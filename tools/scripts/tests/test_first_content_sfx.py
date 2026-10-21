"""Behavioral checks for the local candidate audio generator; no playback."""

import array
import hashlib
import io
import json
import math
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import wave


SCRIPT = Path(__file__).resolve().parents[1] / "make-first-content-sfx.py"


class FirstContentSfxTests(unittest.TestCase):
    def generate(self, output, seed=20261014):
        result = subprocess.run(
            [sys.executable, "-B", str(SCRIPT), "--output", str(output), "--seed", str(seed)],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads((output / "manifest.json").read_text(encoding="utf-8"))

    def decoded(self, path):
        with wave.open(str(path), "rb") as audio:
            self.assertEqual(audio.getnchannels(), 1)
            self.assertEqual(audio.getframerate(), 48000)
            self.assertEqual(audio.getsampwidth(), 2)
            self.assertEqual(audio.getcomptype(), "NONE")
            frames = audio.getnframes()
            samples = array.array("h", audio.readframes(frames))
        if sys.byteorder != "little":
            samples.byteswap()
        self.assertEqual(len(samples), frames)
        return samples

    def test_outputs_decode_with_headroom_and_faded_edges(self):
        # Catches wrong format, clipping, empty renders and hard nonzero endpoints.
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "candidates"
            manifest = self.generate(output)
            self.assertGreaterEqual(len(manifest["cues"]), 16)
            self.assertLessEqual(len(manifest["cues"]), 20)
            for cue in manifest["cues"]:
                with self.subTest(cue=cue["id"]):
                    samples = self.decoded(output / cue["file"])
                    peak = max(abs(value) for value in samples)
                    self.assertGreater(peak, 1000)
                    self.assertLessEqual(peak, 18023)  # <= 0.55 of full scale.
                    self.assertEqual(samples[0], 0)
                    self.assertEqual(samples[-1], 0)
                    self.assertLess(max(map(abs, samples[:32])), peak * 0.04)
                    self.assertLess(max(map(abs, samples[-32:])), peak * 0.04)
                    self.assertGreaterEqual(len(samples), 2880)  # >= 60 ms.
                    self.assertLessEqual(len(samples), 38400)  # <= 800 ms.

    def test_fixed_seed_reproduces_bytes_and_variants_differ(self):
        # Catches ambient RNG/time dependence and accidentally duplicated variants.
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            first = self.generate(base / "first")
            second = self.generate(base / "second")
            changed = self.generate(base / "changed", seed=20261015)
            self.assertEqual(first, second)
            self.assertNotEqual(
                [cue["sha256"] for cue in first["cues"]],
                [cue["sha256"] for cue in changed["cues"]],
            )
            for family in ("sword_light", "greatsword_heavy", "spear_thrust"):
                selected = [cue for cue in first["cues"] if cue["family"] == family]
                self.assertEqual(len(selected), 3)
                self.assertEqual(len({cue["sha256"] for cue in selected}), 3)
            for cue in first["cues"]:
                self.assertEqual(
                    (base / "first" / cue["file"]).read_bytes(),
                    (base / "second" / cue["file"]).read_bytes(),
                )

    def test_manifest_matches_real_pcm_and_keeps_audition_pending(self):
        # Catches stale metrics, hashes, omitted synthesis parameters and false acceptance.
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "candidates"
            manifest = self.generate(output)
            self.assertEqual(manifest["actual_count"], len(list(output.glob("*.wav"))))
            self.assertFalse(manifest["auditioned"])
            self.assertFalse(manifest["final_audio_accepted"])
            self.assertEqual(manifest["third_party_sources"], [])
            self.assertEqual(manifest["generation"]["master_seed"], 20261014)
            self.assertEqual(
                manifest["generation"]["script_sha256"],
                hashlib.sha256(SCRIPT.read_bytes()).hexdigest(),
            )
            for cue in manifest["cues"]:
                path = output / cue["file"]
                samples = self.decoded(path)
                peak = max(map(abs, samples)) / 32768
                rms = math.sqrt(sum((value / 32768) ** 2 for value in samples) / len(samples))
                self.assertEqual(cue["sha256"], hashlib.sha256(path.read_bytes()).hexdigest())
                self.assertEqual(cue["frames"], len(samples))
                self.assertAlmostEqual(cue["duration_s"], len(samples) / 48000, places=6)
                self.assertAlmostEqual(cue["sample_peak_dbfs"], 20 * math.log10(peak), places=4)
                self.assertAlmostEqual(cue["rms_dbfs"], 20 * math.log10(rms), places=4)
                self.assertTrue(cue["parameters"])
                self.assertIsInstance(cue["seed"], int)
                self.assertFalse(cue["auditioned"])
                self.assertFalse(cue["final_audio_accepted"])

    def test_existing_output_is_refused_without_changing_any_file(self):
        # Catches overwrite of either a completed version or an empty reserved directory.
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "version"
            self.generate(output)
            before = {path.name: path.read_bytes() for path in output.iterdir()}
            result = subprocess.run(
                [sys.executable, "-B", str(SCRIPT), "--output", str(output)],
                capture_output=True,
            )
            self.assertEqual(result.returncode, 2)
            self.assertEqual(before, {path.name: path.read_bytes() for path in output.iterdir()})
            empty = Path(temporary) / "reserved"
            empty.mkdir()
            result = subprocess.run(
                [sys.executable, "-B", str(SCRIPT), "--output", str(empty)],
                capture_output=True,
            )
            self.assertEqual(result.returncode, 2)
            self.assertEqual(list(empty.iterdir()), [])


if __name__ == "__main__":
    unittest.main()
