"""Reproducible local CC0 derivative preparation; no playback/network/UE.

Refuses to overwrite every output. Float decoding precedes gain and PCM16.
"""
from pathlib import Path
from datetime import datetime, timezone
from array import array
import hashlib
import json
import math
import shutil
import struct
import subprocess
import wave

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
FFMPEG = ROOT / 'tools/runtime/asset-gen/Lib/site-packages/imageio_ffmpeg/binaries/ffmpeg-win-x86_64-v7.1.exe'
INVENTORY = ROOT / 'docs/production/first-batch-v1/audio-preflight.json'
INVENTORY_SHA = 'd70898b60a39d7fb8b20a2441b42dfbf2feeb2968934bd08c718cf18bf9b5688'
PACKAGE = '/Game/Production/FirstBatch/v024/AudioDedicated'
ARCHIVE_TOPIC = '2026-10-15_猎弩装填与换甲专用音效_v002'
ARCHIVES = [ROOT / '过程图稿与视频' / ARCHIVE_TOPIC, Path('E:/OurGame/Knight/过程图稿与视频') / ARCHIVE_TOPIC]
PACKS = {
    'rpg': {
        'audio': ROOT / 'source-assets/third-party/preparation-2026-10-10-v1/kenney-rpg-audio/extracted/Audio',
        'license': ROOT / 'source-assets/third-party/preparation-2026-10-10-v1/kenney-rpg-audio/extracted/License.txt',
        'license_sha256': '5735dfd72cb64cbbceda4ebc00c380c41ca680edb82ff153aa7c9ab97614c539',
        'zip': ROOT / 'source-assets/third-party/preparation-2026-10-10-v1/kenney-rpg-audio/kenney_rpg-audio.zip',
        'zip_sha256': '6dbeaf8544da958d8f2adcb4a4a4b76c1ade34a05f8ab9edccd327da7375f38b',
        'official_source_url_from_local_record': 'https://kenney.nl/assets/rpg-audio',
    },
    'impact': {
        'audio': ROOT / 'source-assets/third-party/kenney/2026-10-10/kenney-impact-sounds/Audio',
        'license': ROOT / 'source-assets/third-party/kenney/2026-10-10/kenney-impact-sounds/License.txt',
        'license_sha256': 'b49aa9c56b04528b95913de13e506a0f7c5e807b9925db9bfef86af1f91120db',
        'zip': ROOT / 'source-assets/third-party/kenney/2026-10-10/kenney_impact-sounds.zip',
        'zip_sha256': '029d734af1582474edf3a694d1b0cebc97c1c152f2f39fa34d4c2bafc5de77f8',
        'official_source_url_from_local_record': 'https://kenney.nl/assets/impact-sounds',
    },
}
CONFIG = [
    ('AUD-XBW-RELOAD-DRAW-01', 'rpg', 'creak3.ogg', .32, 'crossbow_draw_string', 'ActiveReload phase crossing base .20/1.10 of actual duration; presentation only'),
    ('AUD-XBW-RELOAD-INSERT-01', 'rpg', 'metalClick.ogg', .18, 'crossbow_insert_bolt', 'ActiveReload phase crossing base .60/1.10 of actual duration; no ammo commit'),
    ('AUD-XBW-RELOAD-COMPLETE-01', 'rpg', 'metalLatch.ogg', .24, 'crossbow_reload_complete', 'Actual ReloadCompleted event plus matching successful resource receipt only'),
    ('AUD-EQUIP-ARMOR-CLOTH-01', 'rpg', 'cloth2.ogg', .40, 'equip_cloth_armor', 'Successful actual equipment commit for cloth/leather material; not menu open'),
    ('AUD-EQUIP-ARMOR-METAL-01', 'impact', 'impactPlate_light_000.ogg', .32, 'equip_metal_armor', 'Successful actual equipment commit for metal material; not menu open'),
]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_new(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        assert path.read_bytes() == data, 'Existing differing bytes; refuse overwrite: '+str(path)
        return
    with path.open('xb') as f:
        f.write(data)


def write_json(path, data):
    write_new(path, json.dumps(data, ensure_ascii=False, indent=2).encode('utf-8'))


def db(x):
    return 20 * math.log10(x) if x else None


def metrics(samples, rate, channels):
    assert samples and len(samples) % channels == 0
    assert all(math.isfinite(x) for x in samples)
    peak = max(abs(x) for x in samples)
    rms = math.sqrt(math.fsum(x*x for x in samples) / len(samples))
    return {'sample_rate_hz': rate, 'channels': channels, 'frames': len(samples)//channels,
            'duration_s': len(samples)/channels/rate, 'sample_peak_linear': peak,
            'sample_peak_dbfs': db(peak), 'rms_linear': rms, 'rms_dbfs': db(rms),
            'dc_mean': math.fsum(samples)/len(samples), 'samples_abs_ge_1': sum(abs(x)>=1 for x in samples),
            'first_sample_absmax': max(abs(x) for x in samples[:channels]),
            'last_sample_absmax': max(abs(x) for x in samples[-channels:])}


def float_data(path):
    data = path.read_bytes()
    assert len(data) % 4 == 0
    return [x[0] for x in struct.iter_unpack('<f', data)]


def command(args, log_path):
    Path(args[-1]).parent.mkdir(parents=True, exist_ok=True)
    result = subprocess.run(args, capture_output=True, check=False)
    write_new(log_path, result.stderr)
    assert result.returncode == 0, (result.returncode, result.stderr.decode('utf-8', 'replace'))
    return {'argv': [str(x) for x in args], 'exit_code': result.returncode,
            'stderr_path': str(log_path), 'stderr_sha256': digest(log_path)}


def main():
    assert not (HERE/'manifest.json').exists(), 'Preserve frozen source: use a new version'
    assert digest(INVENTORY) == INVENTORY_SHA
    inventory = json.loads(INVENTORY.read_text('utf-8-sig'))['audio_inventory']
    inv = {Path(x['path']).name: x for x in inventory}
    for label, pack in PACKS.items():
        assert digest(pack['license']) == pack['license_sha256']
        assert digest(pack['zip']) == pack['zip_sha256']
        assert 'CC0' in pack['license'].read_text('utf-8-sig')
        copy = HERE/'licenses'/f'Kenney-{label}-License.txt'
        write_new(copy, pack['license'].read_bytes())
        pack['license_copy_path'], pack['license_copy_sha256'] = str(copy), digest(copy)
    tool_sha = digest(FFMPEG)
    version = subprocess.run([str(FFMPEG), '-hide_banner', '-version'], capture_output=True, check=True).stdout
    write_new(HERE/'provenance/ffmpeg-version.txt', version)
    cues = []
    for cue_id, label, filename, length, role, binding in CONFIG:
        pack = PACKS[label]
        original = pack['audio']/filename
        entry = inv[filename]
        assert (ROOT/entry['path']).resolve() == original.resolve()
        assert digest(original) == entry['sha256']
        retained = HERE/'originals'/label/filename
        write_new(retained, original.read_bytes())
        rate, channels = entry['sample_rate_hz'], entry['channels']
        assert channels == 2
        stereo = HERE/'decoded-float'/f'{cue_id}__stereo-original-rate.f32le'
        cmd1 = command([str(FFMPEG), '-nostdin', '-hide_banner', '-loglevel', 'error', '-n', '-i', str(retained), '-map', '0:a:0', '-vn', '-ar', str(rate), '-ac', '2', '-c:a', 'pcm_f32le', '-f', 'f32le', str(stereo)], HERE/'provenance'/f'{cue_id}__decode-v002.log')
        source_float = metrics(float_data(stereo), rate, channels)
        mono = HERE/'decoded-float'/f'{cue_id}__mono48k-pretrim.f32le'
        cmd2 = command([str(FFMPEG), '-nostdin', '-hide_banner', '-loglevel', 'error', '-n', '-f', 'f32le', '-ar', str(rate), '-ac', '2', '-i', str(stereo), '-af', 'pan=mono|c0=0.5*c0+0.5*c1', '-ar', '48000', '-ac', '1', '-c:a', 'pcm_f32le', '-f', 'f32le', str(mono)], HERE/'provenance'/f'{cue_id}__downmix.log')
        whole = float_data(mono)
        frames = round(length*48000)
        assert len(whole) >= frames
        samples = whole[:frames]
        fade_in, fade_out = round(.005*48000), round(.020*48000)
        for i in range(frames):
            envelope = min(1., i/(fade_in-1), (frames-1-i)/(fade_out-1))
            samples[i] *= max(0., envelope)
        pre_gain = metrics(samples, 48000, 1)
        gain = 10**(-4.5/20)/pre_gain['sample_peak_linear']
        boosted = [x*gain for x in samples]
        assert max(abs(x) for x in boosted) < 1
        pcm = [round(x*32767) for x in boosted]
        assert max(abs(x) for x in pcm) < 32767 and pcm[0] == pcm[-1] == 0
        output = HERE/'wav'/f'{cue_id}__v002.wav'
        output.parent.mkdir(parents=True, exist_ok=True)
        with output.open('xb') as stream:
            with wave.open(stream, 'wb') as writer:
                writer.setnchannels(1); writer.setsampwidth(2); writer.setframerate(48000)
                writer.writeframes(struct.pack('<'+'h'*len(pcm), *pcm))
        final = metrics([x/32768 for x in pcm], 48000, 1)
        assert -6 <= final['sample_peak_dbfs'] <= -3 and final['samples_abs_ge_1'] == 0
        assert final['duration_s'] <= .5
        copies = []
        for archive in ARCHIVES:
            for category in ('原件', '展示副本'):
                copies.append({'path': str(archive/category/output.relative_to(HERE)), 'sha256': digest(output)})
        name = 'SW_'+cue_id.replace('-', '_')+'_v002'
        cues.append({'id': cue_id, 'role': role, 'file': str(output), 'sha256': digest(output),
                     'bytes': output.stat().st_size, 'ue_name': name, 'object_path': PACKAGE+'/'+name+'.'+name,
                     'source': {'original_path': str(original), 'original_sha256': digest(original),
                                'retained_original_path': str(retained), 'retained_original_sha256': digest(retained),
                                'license_id': 'CC0-1.0', 'pack': label, **{k:str(v) for k,v in pack.items() if k!='audio'}},
                     'processing': {'commands': [cmd1, cmd2], 'source_float_path': str(stereo), 'source_float_sha256': digest(stereo),
                                    'source_float_metrics': source_float, 'mono48k_path': str(mono), 'mono48k_sha256': digest(mono),
                                    'mono48k_metrics': metrics(whole, 48000, 1), 'trim_start_frame': 0, 'trim_end_frame_exclusive': frames,
                                    'fade_in_frames': fade_in, 'fade_out_frames': fade_out, 'envelope': 'min(1,i/(fadeIn-1),(N-1-i)/(fadeOut-1)); endpoints exactly zero',
                                    'pre_gain_metrics': pre_gain, 'gain_linear': gain, 'gain_db': db(gain), 'target_sample_peak_dbfs': -4.5,
                                    'quantization': 'round(sample*gain*32767) PCM signed16 little-endian; no clipping/limiter/dither'},
                     'metrics': final, 'retained_copies': copies, 'binding_hint': binding,
                     'binding_authoritative': False, 'engine_imported': False, 'runtime_bound': False,
                     'auditioned': False, 'final_mix_accepted': False,
                     'source_fitness': 'filename/material-based candidate; no listening or real crossbow recording claimed'})
    manifest = {'schema': 'first-batch-dedicated-audio-source-v2', 'frozen': True, 'utc': datetime.now(timezone.utc).isoformat(),
                'package': PACKAGE, 'actual_count': 5, 'cues': cues,
                'inventory_path': str(INVENTORY), 'inventory_sha256': INVENTORY_SHA,
                'processing_source_path': str(Path(__file__).resolve()), 'processing_source_sha256': digest(Path(__file__)),
                'tool_path': str(FFMPEG), 'tool_sha256': tool_sha,
                'tool_version_path': str(HERE/'provenance/ffmpeg-version.txt'), 'tool_version_sha256': digest(HERE/'provenance/ffmpeg-version.txt'),
                'reproduction_command': ['F:/Ourgame/tools/runtime/asset-gen/Scripts/python.exe', '-X', 'utf8', '-B', str(Path(__file__).resolve())],
                'archive_roots': [str(x) for x in ARCHIVES], 'external_api_calls': 0, 'paid_supplier_calls': 0, 'image_generation_calls': 0,
                'auditioned': False, 'engine_imported': False, 'runtime_bound': False, 'final_mix_accepted': False,
                'timing_authority_changed': False, 'old17_replaced': False,
                'metric_definitions': 'decoded sample peak and RMS dBFS, not true peak dBTP/LUFS; PCM16 metrics divide by32768',
                'limitations': ['OGG decoding does not recover original recording fidelity.', 'Material-based assignments require retained audition and actual runtime submix review.', 'No source/Actor/HUD/authority or timeline changes; completed-event binding still absent.', 'Five cues only; cancellation cue is intentionally not supplied.']}
    write_json(HERE/'manifest.json', manifest)
    # Every source and presentation copy precedes any possible playback.
    originals = [p for p in HERE.rglob('*') if p.is_file()]
    for archive in ARCHIVES:
        for category in ('原件', '展示副本'):
            for p in originals:
                destination = archive/category/p.relative_to(HERE)
                write_new(destination, p.read_bytes())
                assert digest(destination) == digest(p)
    print(json.dumps({'prepared_wavs': len(cues), 'manifest_sha256': digest(HERE/'manifest.json'),
                      'numeric_metrics': {x['id']:x['metrics'] for x in cues}, 'archive_copies_SHA_verified':len(originals)*4,
                      'auditioned':False,'UE_imported':False}, ensure_ascii=False))


if __name__ == '__main__':
    main()
