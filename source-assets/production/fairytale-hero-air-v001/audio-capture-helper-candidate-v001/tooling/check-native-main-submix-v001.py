"""Read-only native export/PCM/signal/timing checks; never constructs audio.

No cue identification, listening, device-onset or formal acceptance claim.
Optional --output writes one NEW JSON receipt, never an audio file.
"""
from pathlib import Path
import argparse, hashlib, io, json, math, struct, wave
import numpy as np

def need(value, reason):
    if not value:
        raise ValueError(reason)

def number(value):
    return type(value) in (int, float) and math.isfinite(value)

def pin(path):
    path = Path(path).resolve()
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return dict(path=path.as_posix(), bytes=path.stat().st_size, sha256=h.hexdigest())

def native_header(data, canonical=False):
    need(len(data) > 44 and data[:4] == b'RIFF' and data[8:16] == b'WAVEfmt ' and data[36:40] == b'data', 'Exact native UE fixed44 PCM16 WAV required')
    riff_size, fmt_size = struct.unpack_from('<I', data, 4)[0], struct.unpack_from('<I', data, 16)[0]
    fmt, channels, rate, byte_rate, align, bits = struct.unpack_from('<HHIIHH', data, 20)
    data_size = struct.unpack_from('<I', data, 40)[0]
    expected_align = channels * 2
    need(riff_size + 8 == len(data) and data_size + 44 == len(data) and data_size > 0, 'Truncated, trailing or empty native PCM payload')
    need(fmt_size == 16 and fmt == 1 and bits == 16 and 1 <= channels <= 8 and 8000 <= rate <= 192000, 'Invalid native PCM16 format')
    need(byte_rate == rate * expected_align and data_size % expected_align == 0, 'Invalid native byte rate/payload alignment')
    need(align == expected_align if canonical else align in (2, expected_align), 'Unsupported native BlockAlign; only confirmed UE value2 or correct alignment allowed')
    return dict(channels=channels, sample_rate_hz=rate, block_align=align, expected_block_align=expected_align, pcm_bits=bits, frames=data_size // expected_align, duration_s=data_size / byte_rate, payload=data[44:])

def validate_pcm_bytes(original, canonical, require_non_silent=True):
    old, new = native_header(original), native_header(canonical, True)
    need(len(original) == len(canonical) and original[:32] == canonical[:32] and original[34:] == canonical[34:], 'Only BlockAlign bytes32/33 may differ; no PCM/header replacement')
    need(old['payload'] == new['payload'], 'Engine and canonical PCM payload differ')
    with wave.open(io.BytesIO(canonical), 'rb') as decoded:
        need(decoded.getcomptype() == 'NONE' and decoded.getsampwidth() == 2 and decoded.getnchannels() == new['channels'] and decoded.getframerate() == new['sample_rate_hz'] and decoded.getnframes() == new['frames'], 'Full independent standard WAV decoder disagrees')
        payload = decoded.readframes(decoded.getnframes())
        need(payload == new['payload'] and decoded.readframes(1) == b'', 'WAV decoder did not consume the exact entire native payload')
    samples = np.frombuffer(payload, dtype='<i2').astype(np.int32)
    peak = int(np.max(np.abs(samples)))
    rms = math.sqrt(float(np.mean(samples.astype(np.float64) ** 2))) / 32768.
    peak_linear = peak / 32768.
    non_silent = peak_linear >= .001 and rms >= .00001
    if require_non_silent:
        need(non_silent, 'Actual complete PCM is silent or below existing recorded-signal thresholds; never audio acceptance')
    return dict(channels=new['channels'], sample_rate_hz=new['sample_rate_hz'], pcm_bits=16, frames=new['frames'], duration_s=new['duration_s'], full_decode_passed=True, non_silent=non_silent, non_silence_rule='sample peak>=-60dBFS and whole-file RMS>=-100dBFS; not listening', sample_peak_linear=peak_linear, sample_peak_dbfs=20 * math.log10(peak_linear) if peak else None, rms_dbfs=20 * math.log10(rms) if rms else None, nonzero_samples=int(np.count_nonzero(samples)), fullscale_samples=int(np.count_nonzero(np.abs(samples) >= 32767)), original_block_align=old['block_align'], canonical_block_align=new['block_align'], header_block_align_repaired=old['block_align'] != new['block_align'], only_header_alignment_bytes_may_differ=True, PCM_payload_unchanged=True, PCM_payload_sha256=hashlib.sha256(payload).hexdigest())

def validate_capture_receipt(capture):
    need(capture['schema'] == 'native-main-submix-capture-v001' and capture['phase'] == 'Complete' and capture['failure'] == '', 'Actual completed helper receipt required; pending/failed is preserved, not PASS')
    for name in ['start_requested', 'stop_requested', 'export_callback_received', 'new_directory_exclusively_created', 'engine_wav_present', 'canonical_wav_ready', 'PCM_payload_unchanged', 'controls_configured', 'controls_restore_requested', 'app_volume_restored', 'submix_auto_disable_request_queued', 'submix_restore_request_queued', 'stop_audio_command_fence_completed']:
        need(capture[name] is True, 'Required real helper receipt missing: ' + name)
    for name in ['abort_drain_requested', 'submix_effective_auto_disable_read_back', 'non_silence_checked_by_helper', 'auditioned', 'final_mix_accepted']:
        need(capture[name] is False, 'Capture scope changed: ' + name)
    need(type(capture['formal_complete_units']) is int and capture['formal_complete_units'] == 0, 'No formal completion from a WAV export')
    need(type(capture['native_audio_device_id']) is int and 0 <= capture['native_audio_device_id'] < 2**32 - 1, 'Actual bound native audio device ID required')
    start, stop = capture['start_monotonic_s'], capture['stop_monotonic_s']
    need(number(start) and number(stop) and 0 < start < stop and number(capture['requested_wall_duration_s']) and abs((stop - start) - capture['requested_wall_duration_s']) <= 1e-6, 'Invalid real monotonic request interval')
    need(number(capture['audio_clock_start_s']) and number(capture['audio_clock_stop_s']) and 0 <= capture['audio_clock_start_s'] <= capture['audio_clock_stop_s'], 'Invalid native mixer clock observations')
    for key in ['primary_volume_start', 'primary_volume_stop']:
        need(number(capture[key]) and capture[key] > 0, 'Actual native primary volume must remain positive')
    for key in ['disable_app_volume_start', 'disable_app_volume_stop']:
        need(type(capture[key]) is int and capture[key] == 1, 'Actual process app-volume bypass required during isolated recording')
    priority = capture['previous_disable_app_volume_set_by']
    need(type(priority) is int and priority >= 0, 'Original process CVar priority required')
    for key in ['disable_app_volume_set_by_start', 'disable_app_volume_set_by_stop', 'disable_app_volume_set_by_restored']:
        need(type(capture[key]) is int and capture[key] == priority, 'Process CVar priority must be preserved and restored, not silently raised to Code')
    return stop - start

def validate_frame_timing(report, capture, duration):
    timing = report['capture_timing']
    offsets = timing['frame_wall_offsets_s']
    need(timing['use_fixed_time_step'] is False and timing['capture_start_monotonic_s'] == capture['start_monotonic_s'] and timing['capture_stop_monotonic_s'] == capture['stop_monotonic_s'], 'Video/audio must share the exact real helper origin/stop; no independent clock or fixed-step pacing')
    need(offsets and all(number(t) and 0 <= t < duration for t in offsets) and all(b > a for a, b in zip(offsets, offsets[1:])), 'Original callback offsets must be finite, strictly increasing and inside the recording')
    need(offsets[0] <= .10, 'Actual first recorded frame exceeds unchanged100ms synchronization gate')
    observations = report['observations']
    need(len(observations) == len(offsets) and all(o['wall_offset_s'] == t for o, t in zip(observations, offsets)), 'One actual observation per wall-timed callback required')
    return dict(frame_timing_checked=True, native_callback_count=len(offsets), first_frame_offset_s=offsets[0], maximum_first_frame_offset_s=.10, maximum_inter_callback_gap_s=max((b - a for a, b in zip(offsets, offsets[1:])), default=0.), exact_helper_origin_and_stop=True, simulation_time_used_for_audio_sync=False, native_PNG_CRC_verified_by_this_checker=False)

def audit(report_path, capture_field='main_submix_capture', require_frame_timing=False):
    report_path = Path(report_path).resolve()
    report = json.loads(report_path.read_text(encoding='utf-8-sig'))
    capture = report if report.get('schema') == 'native-main-submix-capture-v001' else report[capture_field]
    duration = validate_capture_receipt(capture)
    directory = Path(capture['output_directory'])
    need(directory.is_absolute(), 'Absolute actual helper output directory required')
    directory = directory.resolve()
    need(directory.is_relative_to(report_path.parent), 'WAV must belong to this report archive; another capture cannot substitute')
    original, canonical = Path(capture['engine_original_wav']), Path(capture['canonical_wav'])
    need(original.is_absolute() and canonical.is_absolute() and original.resolve() == directory / 'runtime-mix-engine-export.wav' and canonical.resolve() == directory / 'runtime-mix.wav', 'Exact engine/canonical paths inside this helper-owned leaf required')
    decoded = validate_pcm_bytes(original.read_bytes(), canonical.read_bytes())
    need(capture['channels'] == decoded['channels'] and capture['sample_rate_hz'] == decoded['sample_rate_hz'] and capture['pcm_frames'] == decoded['frames'] and capture['header_block_align_repaired'] is decoded['header_block_align_repaired'], 'Helper native PCM/header observations differ from actual independently decoded bytes')
    difference = abs(decoded['duration_s'] - duration)
    need(difference <= .15, 'Actual WAV/wall duration exceeds unchanged150ms gate; no stretching, filling or replacement')
    timing = validate_frame_timing(report, capture, duration) if require_frame_timing else dict(frame_timing_checked=False, reason='Not requested; no audio/video synchronization claim')
    return dict(schema='native-main-submix-independent-audio-check-v001', passed=True, scope='Actual preserved export/PCM/capture-receipt/signal and optional timing checks only', native_report=pin(report_path), engine_original=pin(original), canonical=pin(canonical), decoded_PCM=decoded, capture_wall_duration_s=duration, actual_WAV_wall_duration_difference_s=difference, maximum_duration_difference_s=.15, frame_timing=timing, audio_modified=False, offline_audio_constructed=False, gameplay_event_request_chain_verified=False, each_cue_signal_verified=False, device_onset_or_latency_measured=False, auditioned=False, final_mix_accepted=False, formal_complete_units=0)

def main():
    p = argparse.ArgumentParser(); p.add_argument('--report', required=True); p.add_argument('--capture-field', default='main_submix_capture'); p.add_argument('--require-frame-timing', action='store_true'); p.add_argument('--output')
    args = p.parse_args()
    result = audit(args.report, args.capture_field, args.require_frame_timing)
    if args.output:
        with Path(args.output).open('x', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2); f.write('\n')
    print(json.dumps(result, ensure_ascii=False))

if __name__ == '__main__':
    main()
