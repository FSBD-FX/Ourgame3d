#!/usr/bin/env python3
"""Create deterministic original candidate SFX without playback or external APIs.

Python standard library only. Existing output directories are never overwritten.
These renders are engineering candidates, not approved sound design.
"""

import argparse
import array
import hashlib
import io
import json
import math
from pathlib import Path
import random
import sys
import wave


SAMPLE_RATE = 48000
DEFAULT_SEED = 20261014
GENERATOR_VERSION = "1.0.0"


def cue_specs():
    """The declared 17-cue scope, with every synthesis parameter in the manifest."""
    specs = []

    def add(identifier, family, kind, duration, start, end, highpass, tone,
            tone_mix, grains, peak, note, event):
        specs.append({
            "id": identifier,
            "family": family,
            "event_candidate": event,
            "purpose": note,
            "parameters": {
                "kind": kind,
                "duration_s": duration,
                "filter_start_hz": start,
                "filter_end_hz": end,
                "highpass_hz": highpass,
                "tone_start_hz": tone,
                "tone_end_ratio": 0.48,
                "tone_mix": tone_mix,
                "grain_count": grains,
                "grain_duration_range_s": [0.004, 0.028],
                "grain_frequency_range_hz": [430.0, 3200.0],
                "grain_decay_rate": 8.0,
                "grain_mix": 0.18 if grains else 0.0,
                "envelope_power": 1.6 if kind == "whoosh" else 0.7,
                "decay_rate": 9.0 if kind == "string" else 4.5,
                "fade_in_ms": 8.0,
                "fade_out_ms": 15.0,
                "sample_peak_target_linear": peak,
                "dc_remove_before_fades": True,
            },
        })

    for variant in range(3):
        add(f"AUD-SWD-WHOOSH-{variant + 1:02d}", "sword_light", "whoosh",
            0.19 + 0.02 * variant, 4700 + 350 * variant, 1300 + 150 * variant,
            440, 190, 0.025, 0, 0.48,
            "Short balanced air sweep; no baked target contact.", "AUD-WPN-SWING")
        add(f"AUD-GSW-WHOOSH-{variant + 1:02d}", "greatsword_heavy", "whoosh",
            0.34 + 0.04 * variant, 2400 + 220 * variant, 530 + 70 * variant,
            110, 83 + 8 * variant, 0.16, 0, 0.53,
            "Broader low air sweep; weight is cosmetic, never an extra shockwave.",
            "AUD-WPN-SWING")
        add(f"AUD-SPR-THRUST-{variant + 1:02d}", "spear_thrust", "whoosh",
            [0.075, 0.085, 0.09][variant], 6500 + 350 * variant, 2100,
            900, 320, 0.015, 0, 0.45,
            "Short narrow thrust; supports separate real subhits 100 ms apart.",
            "AUD-WPN-SWING")

    add("AUD-XBW-RELEASE-01", "crossbow_release", "string", 0.20,
        6200, 1100, 450, 185, 0.75, 4, 0.50,
        "Synthetic string snap candidate, not gunfire or reload completion.",
        "AUD-WPN-RELEASE")
    add("AUD-FIRE-LAUNCH-01", "fire_launch", "fire", 0.30,
        4100, 1250, 170, 115, 0.08, 10, 0.48,
        "One actual fireball or fire-line release; no implied extra explosion.",
        "AUD-WPN-RELEASE")
    add("AUD-FIRE-BURN-SHORT-01", "fire_burn_short", "fire", 0.48,
        2800, 2400, 280, 90, 0.0, 16, 0.40,
        "Short existing burn-tick texture; not a looping damage source.",
        "AUD-DAMAGE-DOT")
    add("AUD-STONE-AWAKE-01", "stone_awake", "stone", 0.65,
        1800, 720, 60, 118, 0.26, 22, 0.50,
        "Stone-body wake texture for one authoritative WakeEventID.",
        "AUD-DORMANT-AWAKE")
    add("AUD-STONE-WING-01", "stone_wing", "whoosh", 0.28,
        2900, 850, 220, 146, 0.12, 7, 0.47,
        "Stone-wing movement candidate; real movement presentation hook required.",
        None)
    add("AUD-STONE-ARMOR-SCRAPE-01", "stone_armor_scrape", "stone", 0.32,
        3300, 1250, 480, 225, 0.10, 15, 0.46,
        "Stone armor or shield scrape; not a confirmed block or damage receipt.",
        None)
    add("AUD-STONE-CHARGE-BRAKE-01", "stone_charge_brake", "stone", 0.34,
        2400, 480, 75, 79, 0.38, 16, 0.52,
        "Charge stop texture; authoritative stop hook and cleanup still required.",
        None)
    add("AUD-STONE-FRACTURE-01", "stone_fracture", "stone", 0.50,
        4200, 1100, 150, 142, 0.19, 28, 0.53,
        "Stone fracture material candidate; death and poise break need distinct routing.",
        "AUD-ACTOR-DEATH / AUD-POISE-BREAK")
    return specs


def stable_seed(master_seed, identifier):
    payload = f"first-content-sfx-v1:{master_seed}:{identifier}".encode("utf-8")
    return int.from_bytes(hashlib.sha256(payload).digest()[:8], "big")


def synthesize(parameters, seed):
    """Filtered seeded noise, swept partials and deterministic short grains."""
    p = parameters
    duration = p["duration_s"]
    count = round(duration * SAMPLE_RATE)
    rng = random.Random(seed)
    grains = []
    for _ in range(p["grain_count"]):
        grains.append((
            rng.uniform(0.015, duration * 0.91),
            rng.uniform(*p["grain_duration_range_s"]),
            rng.uniform(*p["grain_frequency_range_hz"]),
            rng.uniform(0.25, 1.0),
        ))

    values = []
    low = 0.0
    low_dc = 0.0
    phase = 0.0
    highpass_alpha = 1 - math.exp(-2 * math.pi * p["highpass_hz"] / SAMPLE_RATE)
    for index in range(count):
        time_s = index / SAMPLE_RATE
        fraction = index / (count - 1)
        cutoff = p["filter_start_hz"] * (
            p["filter_end_hz"] / p["filter_start_hz"]
        ) ** fraction
        alpha = 1 - math.exp(-2 * math.pi * cutoff / SAMPLE_RATE)
        low += alpha * (rng.uniform(-1.0, 1.0) - low)
        low_dc += highpass_alpha * (low - low_dc)
        noise = low - low_dc
        frequency = p["tone_start_hz"] * p["tone_end_ratio"] ** fraction
        phase += 2 * math.pi * frequency / SAMPLE_RATE
        tone = (math.sin(phase) + 0.30 * math.sin(2.73 * phase)) / 1.3

        if p["kind"] == "whoosh":
            envelope = math.sin(math.pi * fraction) ** p["envelope_power"]
        elif p["kind"] == "fire":
            envelope = math.sin(math.pi * fraction) ** p["envelope_power"]
            envelope *= 0.75 + 0.25 * math.sin(2 * math.pi * 18 * time_s) ** 2
        else:
            envelope = math.exp(-p["decay_rate"] * fraction)

        value = ((1 - p["tone_mix"]) * noise + p["tone_mix"] * tone) * envelope
        for onset, length, grain_frequency, strength in grains:
            position = (time_s - onset) / length
            if 0 <= position <= 1:
                grain_envelope = math.sin(math.pi * position) ** 2
                grain_envelope *= math.exp(-p["grain_decay_rate"] * position)
                grain = math.sin(2 * math.pi * grain_frequency * (time_s - onset))
                value += p["grain_mix"] * strength * grain * grain_envelope
        values.append(value)

    mean = math.fsum(values) / count if p["dc_remove_before_fades"] else 0.0
    fade_in = max(1, round(p["fade_in_ms"] * SAMPLE_RATE / 1000))
    fade_out = max(1, round(p["fade_out_ms"] * SAMPLE_RATE / 1000))
    for index, value in enumerate(values):
        start_gain = math.sin(math.pi / 2 * min(1.0, index / fade_in)) ** 2
        end_gain = math.sin(math.pi / 2 * min(1.0, (count - 1 - index) / fade_out)) ** 2
        values[index] = (value - mean) * start_gain * end_gain
    peak = max(map(abs, values))
    if not peak or not all(math.isfinite(value) for value in values):
        raise ValueError("Invalid silent or nonfinite synthesis")
    gain = p["sample_peak_target_linear"] / peak
    samples = array.array("h", (round(value * gain * 32767) for value in values))
    if max(map(abs, samples)) > 18023:
        raise ValueError("Rendered PCM exceeds the candidate headroom contract")
    return samples


def wav_bytes(samples):
    encoded = array.array("h", samples)
    if sys.byteorder != "little":
        encoded.byteswap()
    output = io.BytesIO()
    with wave.open(output, "wb") as audio:
        audio.setnchannels(1)
        audio.setsampwidth(2)
        audio.setframerate(SAMPLE_RATE)
        audio.writeframes(encoded.tobytes())
    return output.getvalue()


def decode_and_measure(encoded):
    """Reopen the actual output bytes and measure PCM, not synthesis floats."""
    with wave.open(io.BytesIO(encoded), "rb") as audio:
        if (audio.getnchannels(), audio.getsampwidth(), audio.getframerate(),
                audio.getcomptype()) != (1, 2, SAMPLE_RATE, "NONE"):
            raise ValueError("Unexpected WAV format")
        frames = audio.getnframes()
        samples = array.array("h", audio.readframes(frames))
        eof = audio.readframes(1)
    if sys.byteorder != "little":
        samples.byteswap()
    if len(samples) != frames or eof:
        raise ValueError("Incomplete WAV decode")
    peak = max(map(abs, samples)) / 32768
    rms = math.sqrt(math.fsum((value / 32768) ** 2 for value in samples) / frames)
    return {
        "decoded_ok": True,
        "sample_rate_hz": SAMPLE_RATE,
        "channels": 1,
        "pcm_bits": 16,
        "frames": frames,
        "duration_s": round(frames / SAMPLE_RATE, 6),
        "sample_peak_dbfs": round(20 * math.log10(peak), 6),
        "rms_dbfs": round(20 * math.log10(rms), 6),
        "sample_peak_linear": round(peak, 8),
        "clipped_pcm_samples": sum(abs(value) >= 32767 for value in samples),
        "first_sample": samples[0],
        "last_sample": samples[-1],
        "dc_mean_linear": round(math.fsum(samples) / (frames * 32768), 8),
        "sha256": hashlib.sha256(encoded).hexdigest(),
        "bytes": len(encoded),
    }


def generate(output, master_seed):
    # Atomic directory creation is the reservation. No overwrite or cleanup of
    # an existing/partially written version, even after a previous failed run.
    output.mkdir(parents=True, exist_ok=False)
    cues = []
    for spec in cue_specs():
        seed = stable_seed(master_seed, spec["id"])
        encoded = wav_bytes(synthesize(spec["parameters"], seed))
        metrics = decode_and_measure(encoded)
        filename = spec["id"] + "__v001.wav"
        with (output / filename).open("xb") as destination:
            destination.write(encoded)
        # Verify the filesystem artifact, too; not just the encoder's buffer.
        stored = (output / filename).read_bytes()
        if stored != encoded:
            raise OSError("Stored WAV differs from rendered bytes")
        cues.append({
            **spec, **metrics, "file": filename, "seed": seed,
            "auditioned": False, "final_audio_accepted": False,
            "engine_imported": False, "looping": False,
            "source_kind": "original_procedural_local_synthesis",
            "third_party_source_refs": [],
        })
    manifest = {
        "schema_version": "1.0",
        "status": "generated_numeric_checked_pending_audition_and_runtime",
        "actual_count": len(cues),
        "auditioned": False,
        "final_audio_accepted": False,
        "engine_imported": False,
        "generation": {
            "generator_version": GENERATOR_VERSION,
            "script": "tools/scripts/make-first-content-sfx.py",
            "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            "master_seed": master_seed,
            "python_version": sys.version.split()[0],
            "algorithm": "stdlib.Random seeded noise; one-pole band filtering; swept inharmonic partials; deterministic grains; DC removal; squared-sine edge fades; peak scaling; PCM16 quantization",
            "dependencies": "Python standard library only",
            "external_calls": False,
            "paid_API_calls": 0,
            "TTS_or_human_voice": False,
            "overwrite_policy": "reject_any_existing_output_directory; no automatic retry with different seed",
            "reproduction_scope": "same script hash, Python version, seed and parameters; floating-point/platform math may differ on other runtimes",
        },
        "provenance": {
            "asset_scope": "original local procedural audio; no samples from Lost Castle, third-party packs or TTS",
            "usage": "created for this project; no third-party sample license or attribution dependencies",
            "copyright_status": "no claim of universal copyright eligibility or public-domain dedication",
        },
        "third_party_sources": [],
        "measurement": {
            "sample_peak": "decoded PCM sample peak dBFS; not true-peak dBTP",
            "rms": "decoded PCM whole-file RMS dBFS; not LUFS or perceptual loudness",
            "format": "RIFF WAV, 48000 Hz mono signed PCM16 little-endian",
            "audition": "none; fades and numeric headroom do not prove absence of audible clicks, good timbre or runtime mix balance",
            "loop_points": "none; every render is a finite one-shot",
        },
        "cues": cues,
    }
    with (output / "manifest.json").open("x", encoding="utf-8", newline="\n") as destination:
        json.dump(manifest, destination, ensure_ascii=False, indent=2)
        destination.write("\n")
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path,
                        help="New version directory; an existing path is rejected")
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    arguments = parser.parse_args()
    try:
        manifest = generate(arguments.output, arguments.seed)
    except FileExistsError:
        parser.error(f"Refusing to overwrite existing output: {arguments.output}")
    print(json.dumps({"actual_count": manifest["actual_count"],
                      "output": str(arguments.output),
                      "auditioned": False,
                      "clipped_pcm_samples": sum(cue["clipped_pcm_samples"]
                                                 for cue in manifest["cues"])},
                     ensure_ascii=False))


if __name__ == "__main__":
    main()
