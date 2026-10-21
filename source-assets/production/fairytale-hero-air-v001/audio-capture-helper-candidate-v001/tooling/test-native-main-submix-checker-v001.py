"""Host-only checker tests. Real historical WAVs read; no WAV written or played."""
from pathlib import Path
import ast, copy, hashlib, json, runpy, struct

C = Path(__file__).resolve().parent.parent
R = Path('F:/Ourgame')
api = runpy.run_path(str(C / 'tooling/check-native-main-submix-v001.py'))
checks = []
def good(name, condition):
    if not condition: raise AssertionError(name)
    checks.append(dict(name=name, passed=True))
def reject(name, call):
    try: call()
    except (ValueError, KeyError, TypeError, AssertionError):
        checks.append(dict(name=name, passed=True)); return
    raise AssertionError('Accepted negative: ' + name)
def pin(p):
    p = Path(p); return dict(path=p.as_posix(), bytes=p.stat().st_size, sha256=hashlib.sha256(p.read_bytes()).hexdigest())

real_sources = []
for topic in ['2026-10-15_三近战连段运行_v005', '2026-10-15_猎弩四甲双向射击装填实际换装运行_v007']:
    folder = R / '过程图稿与视频' / topic / '原件'
    original, canonical = folder / 'runtime-mix-engine-export.wav', folder / 'runtime-mix.wav'
    result = api['validate_pcm_bytes'](original.read_bytes(), canonical.read_bytes())
    good(topic + '_real_complete_payload_and_signal', result['full_decode_passed'] and result['non_silent'] and result['PCM_payload_unchanged'] and result['header_block_align_repaired'])
    real_sources.append(dict(original=pin(original), canonical=pin(canonical), independent_decoded_metrics=result))
base = R / '过程图稿与视频/2026-10-15_猎弩四甲双向射击装填实际换装运行_v007/原件'
original, canonical = (base / 'runtime-mix-engine-export.wav').read_bytes(), (base / 'runtime-mix.wav').read_bytes()
reject('truncated_canonical', lambda: api['validate_pcm_bytes'](original, canonical[:-2]))
reject('trailing_canonical', lambda: api['validate_pcm_bytes'](original, canonical + b'\0\0'))
bad = bytearray(canonical); bad[44] ^= 1
reject('changed_one_actual_PCM_byte', lambda: api['validate_pcm_bytes'](original, bytes(bad)))
bad = bytearray(canonical); bad[32:34] = struct.pack('<H', 2)
reject('uncorrected_stereo_alignment', lambda: api['validate_pcm_bytes'](original, bytes(bad)))
bad = bytearray(original); bad[32:34] = struct.pack('<H', 3)
reject('unproven_engine_alignment_bug_value3', lambda: api['validate_pcm_bytes'](bytes(bad), canonical))
bad = bytearray(canonical); bad[20:22] = struct.pack('<H', 3)
reject('float_WAV_substitution', lambda: api['validate_pcm_bytes'](original, bytes(bad)))
silent_path = R / '过程图稿与视频/2026-10-14_三近战连段运行_v003/原件/runtime-mix.wav'
silent_original = silent_path.read_bytes()
silent_canonical = bytearray(silent_original)
silent_canonical[32:34] = struct.pack('<H', struct.unpack_from('<H', silent_original, 22)[0] * 2)
# Historical confirmed header defect corrected in memory ONLY. Its actual all0
# PCM is still rejected, never used as a new sound or an accepted recording.
reject('actual_historical_allzero_mix_rejected', lambda: api['validate_pcm_bytes'](silent_original, bytes(silent_canonical)))
silent_metrics = api['validate_pcm_bytes'](silent_original, bytes(silent_canonical), False)
good('actual_historical_allzero_diagnosed_without_acceptance', not silent_metrics['non_silent'] and silent_metrics['nonzero_samples'] == 0)
mono_path = R / 'source-assets/production/stone-guard-feedback-v001/audio-v001/SW_AUD_GUARD_STEP_01_v001.wav'
mono_bytes = mono_path.read_bytes(); mono = api['validate_pcm_bytes'](mono_bytes, mono_bytes)
good('already_correct_mono_header_needs_no_repair', mono['channels'] == 1 and not mono['header_block_align_repaired'])

# Synthetic gate-only receipts are in memory, never represented as game runs.
fixture = dict(schema='native-main-submix-capture-v001', phase='Complete', failure='', start_monotonic_s=100., stop_monotonic_s=101., requested_wall_duration_s=1., audio_clock_start_s=3., audio_clock_stop_s=4., primary_volume_start=1., primary_volume_stop=1., disable_app_volume_start=1, disable_app_volume_stop=1, previous_disable_app_volume_set_by=0, disable_app_volume_set_by_start=0, disable_app_volume_set_by_stop=0, disable_app_volume_set_by_restored=0, native_audio_device_id=1, formal_complete_units=0)
true_flags = ['start_requested', 'stop_requested', 'export_callback_received', 'new_directory_exclusively_created', 'engine_wav_present', 'canonical_wav_ready', 'PCM_payload_unchanged', 'controls_configured', 'controls_restore_requested', 'app_volume_restored', 'submix_auto_disable_request_queued', 'submix_restore_request_queued', 'stop_audio_command_fence_completed']
false_flags = ['abort_drain_requested', 'submix_effective_auto_disable_read_back', 'non_silence_checked_by_helper', 'auditioned', 'final_mix_accepted']
fixture.update({key: True for key in true_flags}); fixture.update({key: False for key in false_flags})
good('synthetic_gate_only_receipt_positive', api['validate_capture_receipt'](fixture) == 1.)
for key, value in [('phase', 'Arming'), ('phase', 'ExportPending'), ('phase', 'Failed'), ('export_callback_received', False), ('PCM_payload_unchanged', False), ('app_volume_restored', False), ('stop_audio_command_fence_completed', False), ('disable_app_volume_set_by_restored', 0x0D000000), ('native_audio_device_id', 2**32 - 1), ('native_audio_device_id', True), ('start_requested', 'true'), ('auditioned', True), ('final_mix_accepted', True), ('formal_complete_units', 1), ('start_monotonic_s', float('nan')), ('stop_monotonic_s', float('inf')), ('requested_wall_duration_s', .9), ('primary_volume_start', 0.), ('primary_volume_stop', float('nan')), ('disable_app_volume_start', True)]:
    bad = copy.deepcopy(fixture); bad[key] = value
    reject('synthetic_bad_receipt_' + key + '_' + str(value), lambda bad=bad: api['validate_capture_receipt'](bad))
offsets = [.01, .04, .08]
frame_fixture = dict(capture_timing=dict(use_fixed_time_step=False, capture_start_monotonic_s=100., capture_stop_monotonic_s=101., frame_wall_offsets_s=offsets), observations=[dict(wall_offset_s=t) for t in offsets])
good('synthetic_gate_only_real_origin_shape', api['validate_frame_timing'](frame_fixture, fixture, 1.)['native_callback_count'] == 3)
for key, value in [('use_fixed_time_step', True), ('capture_start_monotonic_s', 99.), ('capture_stop_monotonic_s', 102.), ('frame_wall_offsets_s', [.01, .01, .08]), ('frame_wall_offsets_s', [.100001, .2, .3]), ('frame_wall_offsets_s', [.01, .04, 1.]), ('frame_wall_offsets_s', [float('nan'), .04, .08])]:
    bad = copy.deepcopy(frame_fixture); bad['capture_timing'][key] = value
    reject('synthetic_frame_timing_' + key + '_' + str(value), lambda bad=bad: api['validate_frame_timing'](bad, fixture, 1.))
bad = copy.deepcopy(frame_fixture); bad['observations'][1]['wall_offset_s'] = .041
reject('synthetic_observation_timestamp_mismatch', lambda: api['validate_frame_timing'](bad, fixture, 1.))

for p in (C / 'tooling').glob('*.py'): ast.parse(p.read_text(encoding='utf-8'))
source = (C / 'new-source/DungeonNativeMainSubmixCaptureV001.cpp').read_text(encoding='utf-8')
good('one_real_StartRecordingOutput_call', source.count('UAudioMixerBlueprintLibrary::StartRecordingOutput(') == 1)
good('one_real_StopRecordingOutput_call', source.count('UAudioMixerBlueprintLibrary::StopRecordingOutput(') == 1)
good('no_gameplay_or_playback_API_calls', not any(x in source for x in ['ApplyCombatHit(', 'SetActorLocation(', 'PlaySound2D(', 'InputKey(', 'SimulationTime =']))
good('no_delete_or_move_cleanup', not any(x in source for x in ['DeleteFile(', 'DeleteDirectory(', 'MoveFile(']))
print(json.dumps(dict(schema='native-main-submix-helper-host-verification-v001', passed=True, checks=len(checks), check_results=checks, actual_historical_non_silent_WAV_pairs=real_sources, actual_historical_silent_WAV=pin(silent_path), current_helper_compiled=False, current_helper_native_capture_run=False, synthetic_receipts_scope='Memory-only rejecting gate fixtures; not game facts or native evidence', source_or_audio_written=False, device_playback=False, auditioned=False, final_mix_accepted=False, formal_complete_units=0), ensure_ascii=False))
