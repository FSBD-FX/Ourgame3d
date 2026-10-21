"""Read candidate evidence and fully decode every WAV; optional CREATE_NEW report.

This verifier does not play audio, synthesize replacement signals or call UE.
It uses stdlib PCM metrics independently of the preparation code.
"""
import argparse
from array import array
import hashlib
import io
import json
import math
from pathlib import Path
import subprocess
import sys
import wave
import zipfile

HERE = Path(__file__).resolve().parent
EXPECTED = {
    'AUD-HERO-STEP-LIGHT-01': 11520,
    'AUD-HERO-STEP-LIGHT-02': 12480,
    'AUD-HERO-TAKEOFF-LIGHT-01': 12480,
    'AUD-HERO-LAND-LIGHT-01': 14400,
    'AUD-HERO-LAND-FIRM-01': 19200,
    'AUD-HERO-DODGE-SHORT-01': 14400,
}


def pin(path):
    p = Path(path)
    b = p.read_bytes()
    return {'path': str(p), 'bytes': len(b), 'sha256': hashlib.sha256(b).hexdigest()}


def pins_in(node):
    if isinstance(node, dict):
        if all(k in node for k in ('path', 'bytes', 'sha256')):
            yield {k: node[k] for k in ('path', 'bytes', 'sha256')}
        for value in node.values():
            yield from pins_in(value)
    elif isinstance(node, list):
        for value in node:
            yield from pins_in(value)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--report', type=Path)
    args = parser.parse_args()
    manifest_path = HERE / 'manifest.json'
    manifest = json.loads(manifest_path.read_text('utf-8'))
    assert manifest['schema'] == 'HeroLocomotionLocalAudioCandidate-v001'
    assert manifest['status'] == 'LOCAL_CANDIDATE_STRUCTURAL_CHECKS_ONLY'
    assert manifest['operations'] == {
        'new_WAV_candidates': 6, 'external_API_calls': 0, 'downloads': 0,
        'paid_generation': 0, 'image_generations': 0, 'playback_calls': 0,
        'UE_runs': 0, 'writes_outside_candidate': 0, 'E_retention_writes': 0,
        'Source_Content_tools_ledger_modified': False,
    }
    assert manifest['acceptance'] and all(value is False for value in manifest['acceptance'].values())
    assert len(manifest['sources']) == 8 and len(manifest['assets']) == 6
    distinct_pins = {}
    for row in pins_in(manifest):
        key = str(Path(row['path']).resolve())
        if key in distinct_pins:
            assert distinct_pins[key]['bytes'] == row['bytes']
            assert distinct_pins[key]['sha256'] == row['sha256']
        else:
            distinct_pins[key] = row
    for row in distinct_pins.values():
        assert pin(row['path']) == row, f'First SHA/size mismatch: {row["path"]}'
    archive_path = Path(manifest['source_pack']['retained_ZIP']['path'])
    catalog = json.loads(Path(manifest['source_pack']['retained_catalog']['path']).read_text('utf-8-sig'))
    catalog_by_member = {row['path'].replace('\\', '/'): row for row in catalog}
    with zipfile.ZipFile(archive_path) as archive:
        assert archive.testzip() is None
        assert archive.read('License.txt') == Path(manifest['source_pack']['license_copy']['path']).read_bytes()
        for source in manifest['sources']:
            original = Path(source['original']['path']).read_bytes()
            retained = Path(source['retained']['path']).read_bytes()
            member = source['ZIP_member']
            assert original == retained == archive.read(member)
            assert catalog_by_member[member]['bytes'] == len(retained)
            assert catalog_by_member[member]['sha256'] == hashlib.sha256(retained).hexdigest()
    assert {row['cue_id']: row['frames'] for row in manifest['assets']} == EXPECTED
    assert {p.name for p in (HERE / 'wav').glob('*.wav')} == {
        cue + '__v001.wav' for cue in EXPECTED
    }
    ffmpeg = manifest['toolchain']['ffmpeg']['path']
    summaries = []
    seen = set()
    for asset in manifest['assets']:
        cue = asset['cue_id']
        wav_path = Path(asset['file']['path'])
        assert wav_path.resolve().is_relative_to((HERE / 'wav').resolve())
        blob = wav_path.read_bytes()
        with wave.open(io.BytesIO(blob), 'rb') as decoder:
            assert decoder.getnchannels() == 1 and decoder.getsampwidth() == 2
            assert decoder.getframerate() == 48000 and decoder.getcomptype() == 'NONE'
            assert decoder.getnframes() == EXPECTED[cue]
            payload = decoder.readframes(EXPECTED[cue] + 1)
            assert not decoder.readframes(1)
        assert len(payload) == EXPECTED[cue] * 2
        result = subprocess.run([
            ffmpeg, '-nostdin', '-hide_banner', '-loglevel', 'error', '-i', str(wav_path),
            '-map', '0:a:0', '-vn', '-c:a', 'pcm_s16le', '-f', 's16le', 'pipe:1',
        ], capture_output=True, check=False)
        assert result.returncode == 0 and not result.stderr
        assert result.stdout == payload
        pcm = array('h')
        pcm.frombytes(payload)
        if sys.byteorder != 'little':
            pcm.byteswap()
        assert len(pcm) == EXPECTED[cue] and pcm[0] == pcm[-1] == 0
        peak_integer = max(abs(sample) for sample in pcm)
        assert 0 < peak_integer < 32767
        assert all(abs(sample) < 32767 for sample in pcm)
        rms = math.sqrt(math.fsum((sample / 32768.0) ** 2 for sample in pcm) / len(pcm))
        metric = asset['metrics_and_render']['PCM16_metrics']
        assert abs(metric['sample_peak_linear'] - peak_integer / 32768.0) < 1e-15
        assert abs(metric['RMS_linear'] - rms) < 1e-12
        assert metric['first_sample'] == metric['last_sample'] == 0
        assert asset['metrics_and_render']['hard_clip_samples_abs_32767_or_more'] == 0
        assert asset['metrics_and_render']['boundary_fade_applied_to_all_layers_and_final_mix'] is True
        assert asset['acceptance'] and all(value is False for value in asset['acceptance'].values())
        pcm_sha = hashlib.sha256(payload).hexdigest()
        assert pcm_sha == asset['full_decoded_PCM_sha256']
        assert pcm_sha not in seen, 'Variants unexpectedly identical'
        seen.add(pcm_sha)
        summaries.append({
            'cue_id': cue, 'WAV': pin(wav_path), 'PCM_frames': len(pcm),
            'duration_s': len(pcm) / 48000, 'all_PCM_FFmpeg_wave_equal': True,
            'PCM_sha256': pcm_sha, 'sample_peak_dbfs': 20 * math.log10(peak_integer / 32768.0),
            'RMS_dbfs': 20 * math.log10(rms), 'hard_clip_samples': 0,
            'first_sample': pcm[0], 'last_sample': pcm[-1],
            'first_boundary_delta_PCM16': abs(pcm[1] - pcm[0]),
            'last_boundary_delta_PCM16': abs(pcm[-1] - pcm[-2]),
            'decoder_exit_code': result.returncode,
        })
    for row in distinct_pins.values():
        assert pin(row['path']) == row, f'Second SHA/size mismatch: {row["path"]}'
    report = {
        'schema': 'HeroLocomotionAudioStandaloneVerification-v001', 'pass': True,
        'verifier': pin(Path(__file__)), 'manifest': pin(manifest_path),
        'unique_referenced_pins_two_SHA_size_passes': len(distinct_pins),
        'source_OGG_ZIP_catalog_license_closure': True,
        'assets': summaries, 'complete_decode_count': len(summaries),
        'all_6_distinct_PCM_payloads': len(seen) == 6,
        'metrics_independent_of_preparer': 'stdlib array and math.fsum; complete FFmpeg WAV decode',
        'sample_peak_RMS_are_quality_or_LUFS_proof': False,
        'acceptance': manifest['acceptance'],
        'playback_calls': 0, 'UE_runs': 0, 'external_API_calls': 0,
    }
    if args.report:
        target = args.report.resolve()
        assert target.is_relative_to(HERE.resolve())
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open('xb') as handle:
            handle.write((json.dumps(report, ensure_ascii=False, indent=2) + '\n').encode('utf-8'))
    print(json.dumps({'pass': True, 'full_decode': 6, 'two_SHA_pin_count': len(distinct_pins),
                      'report': pin(args.report) if args.report else None}, ensure_ascii=False))


if __name__ == '__main__':
    main()
