"""Local, isolated Kenney CC0 derivatives. No playback, network or UE mutation.

All writes are CREATE_NEW and restricted to this candidate directory. Sources are
byte-copied before full float decode. A second render is compared in memory.
"""
from __future__ import annotations

import hashlib
import io
import json
import math
from pathlib import Path
import platform
import re
import subprocess
import sys
import wave
import zipfile

import numpy as np
import scipy
from scipy.signal import butter, sosfilt

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PACK = ROOT / 'source-assets/third-party/preparation-2026-10-10-v1/kenney-rpg-audio'
AUDIT = ROOT / '.superpowers/sdd/2026-10-19-hero-air-disk-restore-v144/hero-audio-gap-audit-v001.md'
AUDIT_SHA = 'f383db7dc82f3b57053f097e96b311a392cd019f1717b3b5e1f731c89a84253c'
ZIP_SHA = '6dbeaf8544da958d8f2adcb4a4a4b76c1ade34a05f8ab9edccd327da7375f38b'
LICENSE_SHA = '5735dfd72cb64cbbceda4ebc00c380c41ca680edb82ff153aa7c9ab97614c539'
FFMPEG = ROOT / 'tools/runtime/asset-gen/Lib/site-packages/imageio_ffmpeg/binaries/ffmpeg-win-x86_64-v7.1.exe'
RATE = 48000
FALSE_STATES = {
    'auditioned': False, 'listened': False, 'listening_approved': False,
    'final_mix_approved': False, 'stone_surface_audibly_verified': False,
    'field_recording_claimed': False, 'voice_or_human_performance_claimed': False,
    'UE_imported': False, 'runtime_event_bound': False, 'middleware_configured': False,
    'spatialization_verified': False, 'gameplay_capture_contains_candidates': False,
    'formal_unit_complete': False, 'root_approved': False,
}
NAMES = [
    'footstep00.ogg', 'footstep03.ogg', 'footstep05.ogg', 'cloth1.ogg',
    'cloth2.ogg', 'handleSmallLeather.ogg', 'dropLeather.ogg', 'metalClick.ogg',
]


def sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def pin(path: Path) -> dict:
    data = path.read_bytes()
    return {'path': str(path), 'bytes': len(data), 'sha256': sha_bytes(data)}


def write_new(path: Path, data: bytes) -> None:
    path = path.resolve()
    assert path.is_relative_to(HERE), f'Write outside ownership: {path}'
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('xb') as handle:
        handle.write(data)


def jwrite(path: Path, data: object) -> None:
    write_new(path, (json.dumps(data, ensure_ascii=False, indent=2, allow_nan=False) + '\n').encode('utf-8'))


def run_pipe(argv: list[str], name: str) -> tuple[bytes, dict]:
    result = subprocess.run(argv, capture_output=True, check=False)
    log = HERE / 'provenance' / f'{name}.log'
    write_new(log, result.stderr)
    rec = {'argv': argv, 'exit_code': result.returncode, 'stderr': pin(log),
           'stdout_bytes': len(result.stdout), 'stdout_sha256': sha_bytes(result.stdout)}
    assert result.returncode == 0, rec
    return result.stdout, rec


def metric(samples: np.ndarray) -> dict:
    a = np.asarray(samples, dtype=np.float64)
    assert a.ndim == 1 and a.size and np.isfinite(a).all()
    peak = float(np.max(np.abs(a)))
    rms = float(np.sqrt(np.mean(a * a)))
    edge = 240
    db = lambda v: 20.0 * math.log10(v) if v > 0 else None
    return {
        'frames': int(a.size), 'sample_rate_hz': RATE, 'channels': 1,
        'duration_s': a.size / RATE, 'sample_peak_linear': peak,
        'sample_peak_dbfs': db(peak), 'RMS_linear': rms, 'RMS_dbfs': db(rms),
        'DC_mean': float(a.mean()), 'samples_abs_ge_1': int(np.count_nonzero(np.abs(a) >= 1)),
        'first_sample': float(a[0]), 'last_sample': float(a[-1]),
        'first_adjacent_delta_abs': float(abs(a[1] - a[0])),
        'last_adjacent_delta_abs': float(abs(a[-1] - a[-2])),
        'first_5ms_RMS': float(np.sqrt(np.mean(a[:edge] ** 2))),
        'last_5ms_RMS': float(np.sqrt(np.mean(a[-edge:] ** 2))),
        'all_finite': True,
    }


def layer(name: str, start: int, count: int, speed: float, offset: int,
          gain: float, hp: float, lp: float, fade_in: int = 96, fade_out: int = 720) -> dict:
    return {
        'source_name': name, 'crop_start_frame48k': start, 'crop_frame_count48k': count,
        'playback_speed_source_frames_per_output_frame': speed,
        'pitch_semitones_derived_no_time_stretch': 12 * math.log2(speed),
        'output_offset_frame48k': offset,
        'peak_reference_after_crop_speed_filter_envelope': 1.0,
        'relative_linear_gain_after_peak_reference': gain,
        'high_pass_hz': hp, 'low_pass_hz': lp,
        'filter_kind': 'causal Butterworth, order2 HP then order2 LP, zero initial state',
        'HP_SOS': butter(2, hp, btype='highpass', fs=RATE, output='sos').tolist(),
        'LP_SOS': butter(2, lp, btype='lowpass', fs=RATE, output='sos').tolist(),
        'fade_in_frames48k': fade_in, 'fade_out_frames48k': fade_out,
        'fade_shape': 'linear endpoint inclusive, first and last exactly zero',
    }


def recipes() -> list[dict]:
    return [
        {'cue_id': 'AUD-HERO-STEP-LIGHT-01', 'label_zh': '轻脚步变体一', 'frames': 11520,
         'role': 'generic footstep adapted toward a small leather-boot stone-floor candidate',
         'global_fade_in_frames': 96, 'global_fade_out_frames': 864,
         'layers': [
             layer('footstep00.ogg', 1056, 8640, 1.08, 0, .34, 90, 7800),
             layer('handleSmallLeather.ogg', 1344, 9600, 1.03, 576, .055, 220, 5000),
             layer('metalClick.ogg', 0, 6720, 1.10, 864, .010, 1800, 7000),
         ]},
        {'cue_id': 'AUD-HERO-STEP-LIGHT-02', 'label_zh': '轻脚步变体二', 'frames': 12480,
         'role': 'second generic footstep source; small articulation variation, material unverified',
         'global_fade_in_frames': 96, 'global_fade_out_frames': 864,
         'layers': [
             layer('footstep03.ogg', 576, 10320, 1.04, 0, .34, 95, 7600),
             layer('handleSmallLeather.ogg', 1824, 8640, .98, 768, .050, 220, 4800),
             layer('metalClick.ogg', 0, 6720, 1.18, 1200, .009, 1800, 6800),
         ]},
        {'cue_id': 'AUD-HERO-TAKEOFF-LIGHT-01', 'label_zh': '轻甲起跳', 'frames': 12480,
         'role': 'light push-off contact plus short cloth movement; not an aerial loop',
         'global_fade_in_frames': 96, 'global_fade_out_frames': 960,
         'layers': [
             layer('footstep05.ogg', 480, 8160, 1.10, 0, .22, 100, 7000),
             layer('cloth1.ogg', 3600, 12480, 1.28, 480, .13, 300, 7200, 192, 960),
             layer('handleSmallLeather.ogg', 960, 7680, 1.15, 720, .045, 200, 5000),
             layer('metalClick.ogg', 0, 6240, 1.15, 1680, .009, 1800, 7000),
         ]},
        {'cue_id': 'AUD-HERO-LAND-LIGHT-01', 'label_zh': '轻落地', 'frames': 14400,
         'role': 'one real ground contact, small body; Land5 must not retrigger',
         'global_fade_in_frames': 96, 'global_fade_out_frames': 1200,
         'layers': [
             layer('footstep03.ogg', 576, 10800, .98, 0, .41, 70, 6900),
             layer('dropLeather.ogg', 0, 13920, 1.08, 288, .095, 90, 4600),
             layer('cloth2.ogg', 2400, 9600, 1.08, 1248, .035, 260, 5600),
             layer('metalClick.ogg', 0, 6240, 1.04, 1056, .014, 1500, 6400),
         ]},
        {'cue_id': 'AUD-HERO-LAND-FIRM-01', 'label_zh': '较重落地', 'frames': 19200,
         'role': 'firmer small-hero landing, not heavy stone enemy or damage impact',
         'global_fade_in_frames': 96, 'global_fade_out_frames': 1680,
         'layers': [
             layer('footstep00.ogg', 960, 10080, .88, 0, .50, 65, 6200),
             layer('footstep05.ogg', 480, 10560, .93, 672, .13, 65, 3400),
             layer('dropLeather.ogg', 0, 17280, .95, 240, .16, 70, 4300),
             layer('cloth1.ogg', 3600, 11520, 1.04, 2160, .06, 240, 5200),
             layer('metalClick.ogg', 0, 8160, .97, 1392, .018, 1400, 6200),
         ]},
        {'cue_id': 'AUD-HERO-DODGE-SHORT-01', 'label_zh': '轻甲短闪避', 'frames': 14400,
         'role': 'cloth and leather motion with a light floor contact, not weapon whoosh',
         'global_fade_in_frames': 144, 'global_fade_out_frames': 1200,
         'layers': [
             layer('cloth1.ogg', 3360, 14400, 1.14, 0, .14, 400, 7200, 240, 960),
             layer('handleSmallLeather.ogg', 960, 10560, 1.22, 288, .055, 240, 5000),
             layer('footstep05.ogg', 480, 6720, 1.25, 720, .13, 160, 5600),
             layer('metalClick.ogg', 0, 6240, 1.20, 960, .009, 2000, 6500),
         ]},
    ]


def envelope(n: int, attack: int, release: int) -> np.ndarray:
    assert attack >= 2 and release >= 2 and attack + release < n
    t = np.arange(n, dtype=np.float64)
    return np.maximum(0.0, np.minimum(1.0, np.minimum(t / (attack - 1), (n - 1 - t) / (release - 1))))


def render(recipe: dict, mono: dict[str, np.ndarray]) -> tuple[bytes, dict]:
    mixed = np.zeros(recipe['frames'], dtype=np.float64)
    layers = []
    for spec in recipe['layers']:
        a = mono[spec['source_name']]
        start, count = spec['crop_start_frame48k'], spec['crop_frame_count48k']
        assert 0 <= start and start + count <= len(a)
        crop = np.asarray(a[start:start + count], dtype=np.float64)
        speed = spec['playback_speed_source_frames_per_output_frame']
        output_frames = math.floor((count - 1) / speed) + 1
        positions = np.arange(output_frames, dtype=np.float64) * speed
        pitched = np.interp(positions, np.arange(count, dtype=np.float64), crop)
        filtered = sosfilt(np.array(spec['HP_SOS']), pitched)
        filtered = sosfilt(np.array(spec['LP_SOS']), filtered)
        filtered *= envelope(output_frames, spec['fade_in_frames48k'], spec['fade_out_frames48k'])
        peak = float(np.abs(filtered).max())
        assert peak > 0 and np.isfinite(filtered).all()
        gain = spec['relative_linear_gain_after_peak_reference'] / peak
        processed = filtered * gain
        offset = spec['output_offset_frame48k']
        assert offset >= 0 and offset + output_frames <= mixed.size, (recipe['cue_id'], spec)
        mixed[offset:offset + output_frames] += processed
        layers.append({
            'source_name': spec['source_name'], 'rendered_frames': output_frames,
            'pre_reference_sample_peak_linear': peak,
            'actual_linear_gain_after_envelope': gain,
            'post_gain_metrics': metric(processed),
        })
    mixed *= envelope(mixed.size, recipe['global_fade_in_frames'], recipe['global_fade_out_frames'])
    pre = metric(mixed)
    # Ceiling is headroom protection only, never a claim of loudness/quality.
    ceiling = 10 ** (-8.0 / 20.0)
    master_gain = min(1.0, ceiling / pre['sample_peak_linear'])
    mastered = mixed * master_gain
    assert float(np.abs(mastered).max()) < 1.0
    q = np.rint(mastered * 32767.0).astype('<i2')
    assert q[0] == q[-1] == 0 and np.max(np.abs(q.astype(np.int32))) < 32767
    buffer = io.BytesIO()
    with wave.open(buffer, 'wb') as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(RATE)
        wav.writeframes(q.tobytes())
    detail = {
        'layers': layers, 'mix_before_master_metrics': pre,
        'master_ceiling_dbfs': -8.0, 'master_gain_linear_downward_only': master_gain,
        'pre_quantization_metrics': metric(mastered),
        'PCM16_metrics': metric(q.astype(np.float64) / 32768.0),
        'quantization': 'numpy rint(float64 * 32767), signed little-endian int16, no dither',
        'hard_clip_samples_abs_32767_or_more': int(np.count_nonzero(np.abs(q.astype(np.int32)) >= 32767)),
        'boundary_fade_applied_to_all_layers_and_final_mix': True,
        'quality_conclusion_from_metrics': False,
    }
    return buffer.getvalue(), detail


def main() -> None:
    assert HERE.name == 'hero-locomotion-audio-candidate-v001'
    assert not (HERE / 'manifest.json').exists(), 'Use a new version; preserve existing outputs'
    assert pin(AUDIT)['sha256'] == AUDIT_SHA and AUDIT.stat().st_size == 18679
    zip_path = PACK / 'kenney_rpg-audio.zip'
    license_path = PACK / 'extracted/License.txt'
    catalog_path = PACK / 'file-checksums-sha256.json'
    assert pin(zip_path)['sha256'] == ZIP_SHA
    assert pin(license_path)['sha256'] == LICENSE_SHA
    license_text = license_path.read_text('utf-8-sig')
    assert 'Creative Commons Zero, CC0' in license_text
    assert 'personal and commercial projects' in license_text
    catalog = json.loads(catalog_path.read_text('utf-8-sig'))
    by_name = {str(v['path']).replace('\\', '/'): v for v in catalog}
    write_new(HERE / 'originals/package/kenney_rpg-audio.zip', zip_path.read_bytes())
    write_new(HERE / 'licenses/Kenney-RPG-Audio-License.txt', license_path.read_bytes())
    write_new(HERE / 'provenance/local-original-file-checksums-sha256.json', catalog_path.read_bytes())
    write_new(HERE / 'provenance/hero-audio-gap-audit-v001.md', AUDIT.read_bytes())
    ffversion, ffversion_receipt = run_pipe([str(FFMPEG), '-hide_banner', '-version'], 'ffmpeg-version-stderr')
    write_new(HERE / 'provenance/ffmpeg-version.txt', ffversion)
    mono, source_records = {}, []
    with zipfile.ZipFile(zip_path) as archive:
        assert archive.read('License.txt') == license_path.read_bytes()
        for name in NAMES:
            original = PACK / 'extracted/Audio' / name
            original_data = original.read_bytes()
            recorded = by_name['Audio/' + name]
            assert len(original_data) == recorded['bytes']
            assert sha_bytes(original_data) == recorded['sha256']
            assert archive.read('Audio/' + name) == original_data
            retained = HERE / 'originals/rpg' / name
            write_new(retained, original_data)
            argv = [str(FFMPEG), '-nostdin', '-hide_banner', '-loglevel', 'info',
                    '-i', str(retained), '-map', '0:a:0', '-vn', '-ar', '48000',
                    '-ac', '2', '-c:a', 'pcm_f32le', '-f', 'f32le', 'pipe:1']
            stereo_bytes, receipt = run_pipe(argv, name + '-full-stereo-float-decode')
            stderr = Path(receipt['stderr']['path']).read_text('utf-8', errors='replace')
            native = re.search(r'Audio: vorbis, (\d+) Hz, stereo', stderr)
            assert native and int(native.group(1)) == RATE, 'Unexpected native rate/channels; no silent resampling'
            assert len(stereo_bytes) % 8 == 0 and stereo_bytes
            stereo = np.frombuffer(stereo_bytes, dtype='<f4').reshape(-1, 2)
            assert np.isfinite(stereo).all()
            # Explicit arithmetic downmix preserves all source frames. No integer stage.
            mono_data = (0.5 * stereo[:, 0].astype(np.float64) + 0.5 * stereo[:, 1].astype(np.float64)).astype('<f4')
            stereo_path = HERE / 'decoded-float' / (name + '.full-stereo48k.f32le')
            mono_path = HERE / 'decoded-float' / (name + '.full-mono48k.f32le')
            write_new(stereo_path, stereo_bytes)
            write_new(mono_path, mono_data.tobytes())
            mono[name] = np.frombuffer(mono_path.read_bytes(), dtype='<f4')
            source_records.append({
                'source_name': name, 'original': pin(original), 'retained': pin(retained),
                'ZIP_member': 'Audio/' + name, 'ZIP_member_equals_extracted_and_retained': True,
                'local_catalog_row': recorded, 'license_copy': pin(HERE / 'licenses/Kenney-RPG-Audio-License.txt'),
                'native_sample_rate_hz': RATE, 'native_channels': 2,
                'native_sample_encoding': 'OGG Vorbis decoded in full to float32; no PCM16 intermediate',
                'full_decode': receipt, 'full_stereo_float': pin(stereo_path), 'full_mono_float': pin(mono_path),
                'downmix': 'float64 arithmetic 0.5 * L + 0.5 * R, then round/store float32',
                'full_mono_metrics': metric(mono[name]),
                'material_identity': 'Generic filename category only; stone/boot/recording method not certified',
            })
    selected_recipes = recipes()
    for recipe in selected_recipes:
        recipe['sample_rate_hz'] = RATE
        recipe['channels'] = 1
        recipe['source_pins'] = [next(s['retained'] for s in source_records if s['source_name'] == name)
                                 for name in sorted({v['source_name'] for v in recipe['layers']})]
    jwrite(HERE / 'recipes-v001.json', {
        'schema': 'HeroLocomotionLocalAudioRecipes-v001', 'recipes': selected_recipes,
        'interpolation': 'linear numpy interp, positions i*speed, length floor((input_frames-1)/speed)+1',
        'randomness': None, 'synthetic_signal_added': False, 'silence_padding': 'zeros only outside exact layers',
    })
    assets = []
    for recipe in selected_recipes:
        data, metrics = render(recipe, mono)
        output = HERE / 'wav' / (recipe['cue_id'] + '__v001.wav')
        write_new(output, data)
        with wave.open(str(output), 'rb') as decoded:
            assert decoded.getparams()[:3] == (1, 2, RATE)
            assert decoded.getcomptype() == 'NONE'
            assert decoded.getnframes() == recipe['frames']
            payload = decoded.readframes(recipe['frames'] + 1)
            assert len(payload) == recipe['frames'] * 2 and not decoded.readframes(1)
        ffpcm, decode_receipt = run_pipe([
            str(FFMPEG), '-nostdin', '-hide_banner', '-loglevel', 'error', '-i', str(output),
            '-map', '0:a:0', '-vn', '-c:a', 'pcm_s16le', '-f', 's16le', 'pipe:1',
        ], recipe['cue_id'] + '-full-WAV-PCM-decode')
        assert ffpcm == payload, 'Independent full WAV decode differs from canonical PCM payload'
        # Render again from retained decoded originals and immutable recipes.
        replay_bytes, replay_metrics = render(recipe, mono)
        assert replay_bytes == output.read_bytes() and replay_metrics == metrics
        assert all(v['PCM16_metrics']['samples_abs_ge_1'] == 0 for v in [metrics])
        assets.append({
            'cue_id': recipe['cue_id'], 'label_zh': recipe['label_zh'], 'role': recipe['role'],
            'file': pin(output), 'format': 'WAV RIFF / mono / 48000 Hz / PCM16 little-endian',
            'frames': recipe['frames'], 'duration_s': recipe['frames'] / RATE,
            'recipe_index': len(assets), 'metrics_and_render': metrics,
            'full_WAV_decode_receipt': decode_receipt,
            'full_decoded_PCM_bytes': len(ffpcm), 'full_decoded_PCM_sha256': sha_bytes(ffpcm),
            'wave_and_FFmpeg_all_PCM_bytes_equal': True,
            'second_memory_render_all_WAV_bytes_equal': True, 'acceptance': FALSE_STATES.copy(),
        })
    second_source_checks = []
    with zipfile.ZipFile(HERE / 'originals/package/kenney_rpg-audio.zip') as retained_archive:
        for row in source_records:
            original_pin = pin(Path(row['original']['path']))
            retained_pin = pin(Path(row['retained']['path']))
            assert original_pin == row['original'] and retained_pin == row['retained']
            assert original_pin['bytes'] == retained_pin['bytes']
            assert original_pin['sha256'] == retained_pin['sha256']
            assert retained_archive.read(row['ZIP_member']) == Path(row['retained']['path']).read_bytes()
            second_source_checks.append({'name': row['source_name'], 'two_read_SHA_size_equal': True,
                                         'retained_ZIP_member_equal': True})
        assert retained_archive.read('License.txt') == (HERE / 'licenses/Kenney-RPG-Audio-License.txt').read_bytes()
    assert pin(license_path)['sha256'] == LICENSE_SHA
    assert pin(HERE / 'licenses/Kenney-RPG-Audio-License.txt')['sha256'] == LICENSE_SHA
    manifest = {
        'schema': 'HeroLocomotionLocalAudioCandidate-v001', 'status': 'LOCAL_CANDIDATE_STRUCTURAL_CHECKS_ONLY',
        'scope': '6 isolated asset candidates; no event/UE/capture/middleware/persistence changes',
        'authorization': 'Existing automatic authorization; no paid generation, no vendor API, no download',
        'sonic_adjectives_zh': ['轻巧', '干脆', '微有晃动'],
        'source_design_identity': 'small bell-helmet hero / brown light armor / grotesque cartoon dark fairytale',
        'design_plan': pin(HERE / '音色与来源计划-v001.md'),
        'gap_audit': pin(AUDIT), 'gap_audit_retained_copy': pin(HERE / 'provenance/hero-audio-gap-audit-v001.md'),
        'source_pack': {'name': 'Kenney RPG Audio', 'license': 'CC0 per local literal license',
                        'original_ZIP': pin(zip_path), 'retained_ZIP': pin(HERE / 'originals/package/kenney_rpg-audio.zip'),
                        'original_license': pin(license_path), 'license_copy': pin(HERE / 'licenses/Kenney-RPG-Audio-License.txt'),
                        'local_catalog': pin(catalog_path),
                        'retained_catalog': pin(HERE / 'provenance/local-original-file-checksums-sha256.json'),
                        'ZIP_and_license_SHA_match_preexisting_prior_preparation': True,
                        'independent_legal_advice_or_new_online_license_audit': False},
        'sources': source_records, 'recipes': pin(HERE / 'recipes-v001.json'), 'assets': assets,
        'toolchain': {'preparer': pin(Path(__file__)), 'python': platform.python_version(),
                      'numpy': np.__version__, 'scipy': scipy.__version__, 'ffmpeg': pin(FFMPEG),
                      'ffmpeg_version': pin(HERE / 'provenance/ffmpeg-version.txt'),
                      'ffmpeg_version_receipt': ffversion_receipt},
        'validation': {'all_6_full_decode': True, 'all_6_exact_PCM_frames': True,
                       'all_6_no_integer_hard_clip': True, 'all_6_zero_endpoint_envelopes': True,
                       'all_6_deterministic_second_render_equal': True,
                       'selected_originals_count': len(source_records), 'sources_second_checks': second_source_checks,
                       'quality_claim_from_peak_RMS': False,
                       'peak_RMS_definitions': 'decoded sample peak and RMS dBFS only; not true peak dBTP, LUFS or perceived loudness'},
        'acceptance': FALSE_STATES.copy(),
        'operations': {'new_WAV_candidates': 6, 'external_API_calls': 0, 'downloads': 0,
                       'paid_generation': 0, 'image_generations': 0, 'playback_calls': 0,
                       'UE_runs': 0, 'writes_outside_candidate': 0, 'E_retention_writes': 0,
                       'Source_Content_tools_ledger_modified': False},
        'remaining': ['Root F/E retention before audition/show', 'headphone and speaker audition',
                      'stone/leather material and volume balance acceptance', 'UE import and middleware event wiring',
                      'true locomotion event identity/cursors/restore rules', 'spatialization and voice budgets',
                      'in-game dense combat/movement mix and full unit acceptance'],
    }
    jwrite(HERE / 'manifest.json', manifest)
    jwrite(HERE / 'structural-verification-v001.json', {
        'schema': 'HeroLocomotionAudioStructuralVerification-v001', 'pass': True,
        'manifest': pin(HERE / 'manifest.json'), 'assets_checked': len(assets),
        'all_source_second_checks': second_source_checks,
        'asset_summaries': [{k: row[k] for k in ('cue_id', 'file', 'frames', 'duration_s', 'full_decoded_PCM_sha256',
                                               'wave_and_FFmpeg_all_PCM_bytes_equal',
                                               'second_memory_render_all_WAV_bytes_equal')} for row in assets],
        'acceptance': FALSE_STATES.copy(),
    })
    print(json.dumps({'status': manifest['status'], 'assets': len(assets), 'sources': len(source_records),
                      'manifest': pin(HERE / 'manifest.json'), 'acceptance': FALSE_STATES}, ensure_ascii=False))


if __name__ == '__main__':
    main()
