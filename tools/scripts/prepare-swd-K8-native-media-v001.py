"""Preserve the first actual K pilot and derive an all-frame native-timed review copy."""
from pathlib import Path
import hashlib, importlib.util, json, shutil, subprocess
from datetime import datetime, timezone
from PIL import Image, ImageDraw, ImageFont
import imageio_ffmpeg

ROOT = Path('F:/Ourgame')
A = ROOT / '过程图稿与视频/2026-10-19_军剑K右侧前踏首次原生试验_v001'
O = A / '原件'
D = A / '展示副本'
P = ROOT / 'docs/production/first-batch-v2/evidence/HeroSwordSecondary-v147-v001/Root-first-K-pilot-prereg-v001/full-right.json'
C = ROOT / 'source-assets/production/fairytale-sword-secondary-v001'

def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))

def pin(path):
    path = Path(path)
    return dict(path=path.as_posix(), bytes=path.stat().st_size,
                sha256=hashlib.sha256(path.read_bytes()).hexdigest())

def save(path, value):
    with Path(path).open('x', encoding='utf-8') as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write('\n')

def load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def copy_exact(source, target):
    assert not target.exists()
    shutil.copy2(source, target)
    assert pin(source)['sha256'] == pin(target)['sha256']
    return dict(source=pin(source), retained=pin(target))

assert pin(P)['sha256'] == '30b7508cd9d96248a6d227a2f0ef19bc4e8c776ac48c1a0ac000e870b2298dad'
assert pin(O / 'runtime-report.json')['sha256'] == '4859516b15302d00b597991a9eedc759f6f840c52a8ba5e56a8aed8b7308d69f'
assert not D.exists() and not (A / 'source-version-status-index-v001.json').exists()
prereg = read(P)
report = read(O / 'runtime-report.json')
native = read(A / 'native-check-result.json')
assert native['pilot_checks_passed'] and not native['errors']
assert read(A / 'process-exit.json')['exit_code'] == 0
assert report['process_id'] == read(A / 'process-started.json')['process_id'] == '52592'
assert report['secondary_frame_mask'] == 255 and report['flow_complete']
assert not report['normal_route_native_verified'] and not report['formal_accepted']
pixel_module = load_module(C / 'K8-native-pixel-checker-candidate-v002/verify-K8-native-pixels-v002.py', 'K8actualpixels')
pixel = pixel_module.audit(A, prereg)
assert pixel['passed'] and pixel['actual_native_pixel_composition_verified']
save(A / 'independent-K8-native-pixel-audit-v002.json', pixel)
D.mkdir()
provenance = O / 'Root-provenance-v001'
provenance.mkdir()
retained = [copy_exact(P, provenance / 'launched-prereg-full-right.json')]
for key, name in [('compiled_manifest', 'compiled-source-manifest.json'),
                  ('source_admission', 'actual-source-admission.json'),
                  ('review_report', 'source-independent-review.md')]:
    row = prereg[key]
    assert pin(row['path']) == row
    retained.append(copy_exact(Path(row['path']), provenance / name))
log = ROOT / 'UnrealGame/Saved/Logs/CodexDungeon.log'
assert str(P).replace('\\', '/') in log.read_text('utf-8-sig', errors='replace').replace('\\', '/')
retained.append(copy_exact(log, provenance / 'actual-native-engine.log'))
retained.append(copy_exact(Path(__file__), provenance / Path(__file__).name))
obs = report['observations']
frames = sorted(O.glob('MovieFrame*.png'))
t = report['capture_timing']
offsets = t['frame_wall_offsets_s']
duration = t['capture_stop_monotonic_s'] - t['capture_start_monotonic_s']
assert not t['use_fixed_time_step'] and len(frames) == len(obs) == len(offsets) == 90
assert offsets == [o['wall_offset_s'] for o in obs] and all(b > a for a, b in zip(offsets, offsets[1:]))
encoder_path = ROOT / 'source-assets/production/fairytale-guard-v001/stomp-native-media-candidate-v001/tooling/retained-microsecond-VFR-v001.py'
encoder = load_module(encoder_path, 'exactNativeVFR')
work = O / '派生编码日志-v001'
work.mkdir()
silent, last, timing, decoded = encoder.encode_vfr(work, frames, offsets, duration)
video = D / 'SWD001-K-right-native-timing-original-mix-v001.mp4'
ff = imageio_ffmpeg.get_ffmpeg_exe()
command = [ff, '-hide_banner', '-loglevel', 'error', '-n', '-itsoffset', f'{offsets[0]:.9f}',
           '-i', str(silent), '-i', str(O / 'audio-v001/runtime-mix.wav'),
           '-map', '0:v:0', '-map', '1:a:0', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k',
           '-video_track_timescale', '1000000', '-movflags', '+faststart', str(video)]
result = subprocess.run(command, capture_output=True, text=True, encoding='utf-8')
(work / 'mux-native-audio.log').write_text(result.stdout + result.stderr, encoding='utf-8')
assert result.returncode == 0, result.stderr
full_decode = subprocess.run([ff, '-hide_banner', '-loglevel', 'info', '-i', str(video),
                             '-map', '0:v:0', '-map', '0:a:0', '-f', 'null', '-'],
                            capture_output=True, text=True, encoding='utf-8')
(work / 'full-audio-video-decode.log').write_text(full_decode.stdout + full_decode.stderr, encoding='utf-8')
assert full_decode.returncode == 0, full_decode.stderr
md5 = subprocess.run([ff, '-hide_banner', '-loglevel', 'error', '-i', str(video),
                      '-map', '0:v:0', '-enc_time_base', '1:1000000', '-fps_mode', 'passthrough',
                      '-f', 'framemd5', '-'], capture_output=True, text=True, encoding='utf-8')
assert md5.returncode == 0
decoded_rows = [line for line in md5.stdout.splitlines() if line and not line.startswith('#')]
assert len(decoded_rows) == len(frames)
(work / 'muxed-video-full-framemd5.txt').write_text(md5.stdout, encoding='utf-8')
samples = []
before = [i for i, o in enumerate(obs) if o['common_draw'].get('clip') == 'sword_ready_idle' and o['sim'] < report['accepted_action']['start']]
after = [i for i, o in enumerate(obs) if o['common_draw'].get('clip') == 'sword_ready_idle' and o['sim'] >= report['accepted_action']['end']]
assert before and len(after) >= 2
choices = [('Ready-before', before[-1])] + [(f"K{row['frame']}", row['callback_index']) for row in pixel['K8_native_pixel_witnesses']] + [('Ready-after', after[0])]
board = Image.new('RGB', (1100, 452), (35, 39, 45))
draw = ImageDraw.Draw(board)
font = ImageFont.truetype('C:/Windows/Fonts/arial.ttf', 13)
for k, (label, i) in enumerate(choices):
    source = frames[i]
    target = D / f'{k:02d}-{label}-native-1280x720.png'
    pair = copy_exact(source, target)
    crop_box = (80, 350, 280, 540)
    crop = Image.open(source).convert('RGB').crop(crop_box)
    x, y = (k % 5) * 220 + 10, (k // 5) * 226
    board.paste(crop, (x, y + 32))
    draw.text((x, y + 2), f'{label}  callback {i}', fill='white', font=font)
    draw.text((x, y + 17), f"wall {offsets[i]:.6f}s / native 1:1 crop", fill='white', font=font)
    samples.append(dict(label=label, callback_index=i, wall_offset_s=offsets[i],
                        full_frame=pair, diagnostic_crop_box=crop_box, crop_scale=1))
board_path = D / 'K8-and-Ready-native-UNSCALED-crop-board-v001.png'
board.save(board_path)
(A / 'README.md').write_text('UE5.5.4实际正常Enter/E/K输入的军剑右向前踏首次试验。90张原生1280×720帧、81资源的162份GPU/editor原字节、游戏混音及真实placement witness全部保留。前踏30cm、K0至7与原End回待机、独立像素核对通过；探索试验不等正式内容单元验收。MP4按真实回调微秒时间编码，全部90帧与原游戏混音保留，AAC仅为有损展示副本；诊断板只裁原像素，未放大角色。未连续播放审阅、未听音、未测设备延迟；左向、None换甲、partial/zero、合法获取、完整单位仍待。原件与展示副本长期保全到E后才View；保全不等用户接受。\n', encoding='utf-8')
save(A / 'source-version-status-index-v001.json', dict(
    schema='Root-first-K8-native-media-v001', utc=datetime.now(timezone.utc).isoformat(),
    runtime=pin(O / 'runtime-report.json'), prereg=pin(P), native_checks=pin(A / 'native-check-result.json'),
    independent_pixels=pin(A / 'independent-K8-native-pixel-audit-v002.json'),
    status='first full_right actual pilot collection and K8 pixels pass; E and Root visual review pending',
    source_files=308, production_files=1495, formal_complete_units=0,
    actual_committed_cm=30, actual_8_K_poses=True, actual_End_to_Ready=True,
    all_native_frames_kept=True, native_frames=len(frames), video=pin(video), VFR_timing=timing,
    video_full_decode_passed=True, decoded_video_frames=len(decoded_rows),
    original_audio_payload_preserved=True, AAC_is_lossy_presentation=True,
    no_audio_trim_or_replacement=True, first_callback_offset_s=offsets[0],
    encoder=pin(encoder_path), tool=pin(Path(__file__)), provenance=retained,
    samples=samples, diagnostic_board=pin(board_path), original_full_frames=[pin(f) for f in frames],
    visual_reviewed=False, full_realtime_playback_reviewed=False, audio_listened=False,
    device_onset_measured=False, FinalAccepted=False,
    files=[pin(f) for f in sorted(A.rglob('*')) if f.is_file()]))
print(json.dumps(dict(archive=A.as_posix(), native_frames=len(frames), video=pin(video),
                      actual_K8_pixels_passed=True, E_before_View=True), ensure_ascii=False))
