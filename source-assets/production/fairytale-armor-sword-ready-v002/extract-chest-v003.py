"""Native161 standard shared-row extraction; preserve request and report GIF timing."""
from pathlib import Path
import datetime, hashlib, json, subprocess, sys
from PIL import Image

R = Path(__file__).resolve().parent
SG = Path('C:/Users/22499/.codex/skills/sprite-gen')
RUN = R / 'run-chest-ready-v003'
OUT = R / 'chest-extraction-v003'
STATE = 'armor_chest_sword_ready'
assert not OUT.exists(), OUT
OUT.mkdir()

def desc(p):
    b = p.read_bytes()
    return {'path': p.as_posix(), 'bytes': len(b), 'sha256': hashlib.sha256(b).hexdigest()}

def write(name, value):
    p = OUT / name
    assert not p.exists(), p
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(value if isinstance(value, str) else json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return p

raw = RUN / 'raw' / f'{STATE}.png'
assert desc(raw)['sha256'] == '1b7d246938c1a7d5ac4122366699b23c8072f6d42566e492b82f09f6bdb09371'
assert raw.stat().st_size == 1332406
before = (RUN / 'sprite-request.json').read_bytes()
(OUT / 'sprite-request-before-extraction.json').write_bytes(before)
request = json.loads(before)
assert request['states'][STATE]['frames'] == 4 and request['states'][STATE]['durations_ms'] == [167] * 4
wrapper = Path('F:/Ourgame/tools/scripts/extract-sprite-shared-row-scale.py')
assert desc(wrapper)['sha256'] == '2d7464dc2e8dd962a7d4dc170c0a7401d09cf1a626415309b4921b7d89d88aa3'
commands = []
for name, tool, args in [('extract-shared-row', wrapper, []),
                         ('compose-atlas', SG / 'scripts/compose_sprite_atlas.py', []),
                         ('export-curated', SG / 'scripts/export_curated_pngs.py', ['--state', STATE]),
                         ('preview', SG / 'scripts/preview_animation.py', [])]:
    argv = [sys.executable, '-X', 'utf8', '-B', str(tool), '--run-dir', str(RUN)] + args
    result = subprocess.run(argv, capture_output=True, text=True, encoding='utf-8')
    log = write(f'{name}-v001.log', result.stdout + result.stderr)
    commands.append({'argv': argv, 'tool': desc(tool), 'exit_code': result.returncode, 'log': desc(log)})
    assert result.returncode == 0, (name, result.stderr)
assert before == (RUN / 'sprite-request.json').read_bytes()
manifest = json.loads((RUN / 'frames/frames-manifest.json').read_text(encoding='utf-8'))
assert manifest['errors'] == [] and manifest['warnings'] == []
shared = manifest['rows'][0]['shared_row_fit']
assert not shared['per_frame_scale_normalization']
frames = []
for i in range(4):
    p = RUN / f'curated/frame-{i}.png'
    with Image.open(p) as im:
        assert im.size == (512, 512) and im.mode == 'RGBA'
        bbox = im.getchannel('A').getbbox()
        assert bbox
        crop = OUT / f'diagnostics-v001/frame-{i}-actual-alpha-bbox.png'
        crop.parent.mkdir(parents=True, exist_ok=True)
        im.crop(bbox).save(crop)
        assert Image.open(crop).tobytes() == im.crop(bbox).tobytes()
    frames.append({'frame': i, 'source': desc(p), 'alpha_bbox_px': list(bbox),
                   'visible_bbox_size_px': [bbox[2] - bbox[0], bbox[3] - bbox[1]],
                   'actual_central_boss_A': None, 'actual_component_attachment_accepted': False,
                   'unscaled_diagnostic': desc(crop), 'new_alpha_explicitly_viewed': False})

gif = RUN / 'qa' / f'{STATE}.gif'
delays = []
with Image.open(gif) as im:
    for i in range(im.n_frames):
        im.seek(i); delays.append(im.info.get('duration'))
timing = {'requested_durations_ms': [167] * 4, 'request_fps': request['states'][STATE]['fps'],
          'actual_standard_gif_delays_ms': delays, 'gif': desc(gif),
          'exact_requested_timing_proved_by_standard_preview': delays == [167] * 4,
          'implementation': desc(SG / 'sprite_gen/qa/preview.py'),
          'basis': 'preview.py119/126-129 computes duration from fps (unless delay_ticks), not request durations_ms; GIF uses10ms units.',
          'request_unchanged': True, 'gif_retimed': False, 'gif_played': False}
write('standard-preview-timing-v001.json', timing)
write('raw-review-and-timing-limit-v001.md', '''# Native161宽胸候选：raw同向，挂点待实测

2026-10-16，scale_tests。E153后独立view原2171×724 raw（工具显示缩至2048×683，未据显示图量精确挂点）。四片均与正向160C0同样3/4透视，较大近带/侧开口在image-LEFT，压缩远侧在image-RIGHT；四片都有单独中央raised round boss，较旧160更横宽。这里只确认raw候选方向/可辨feature存在，不接受四帧fit、位置或动作；160失败全保留，无局部mirror。

本次标准shared-row extract→atlas→curated→preview，无逐帧scale/rotate/warp，原request4×167ms/raw不改。标准preview实现由fps计算统一duration，GIF10ms单位也不能编码精确167ms，因此结构preview文件并非request时序证明；actual GIF metadata另列，未播放、未重定时，不能拿它认证运行循环节奏。

新curated/诊断/QA先freeze等待新E保全开放才显式view。四片actual中央boss A仍null，必须看真实绘制圆boss边界取中心，不能bbox-center、highlight中心或side strapbolt替代。随后如获准，仅将实际A整数平移至158衣面设计target[259271等]±3px，保存独立registered文件，原curated与共同ratio不变。无导入/UE/Source/台账/新native调用，完整内容0/15。
''')
receipt = {'schema': 'native161-chest4-shared-extraction-v3', 'created_local': datetime.datetime.now().astimezone().isoformat(),
           'native_request': 161, 'raw': desc(raw), 'request': desc(RUN / 'sprite-request.json'),
           'commands': commands, 'frames': frames, 'frames_manifest': desc(RUN / 'frames/frames-manifest.json'),
           'QA_errors': manifest['errors'], 'QA_warnings': manifest['warnings'],
           'shared_row_ratio': shared['scale'], 'shared_row_fit': shared, 'durations_ms': [167] * 4,
           'standard_preview_timing': timing, 'raw_facing_status': 'four consistent same3/4RIGHT candidates; central boss visible',
           'raw_explicitly_viewed_after_E153': True, 'new_outputs_explicitly_viewed': False,
           'request_modified': False, 'actual_central_boss_A': [None] * 4, 'alignment_or_fit_accepted': False,
           'ue_import_called': False, 'native_called': False, 'formal_complete_units': 0}
rp = write('extraction-receipt-v001.json', receipt)
files = sorted([p for p in RUN.rglob('*') if p.is_file()] + [p for p in OUT.rglob('*') if p.is_file()] + [Path(__file__).resolve()])
fp = write('extracted-freeze-v001.json', {'schema': 'native161-chest-extraction-freeze-v3',
           'created_local': datetime.datetime.now().astimezone().isoformat(), 'file_count': len(files),
           'total_bytes': sum(p.stat().st_size for p in files), 'files': [desc(p) for p in files],
           'new_outputs_explicitly_viewed': False, 'accepted': False, 'central_boss_A_measured': False,
           'runtime_timing_accepted': False, 'import_permitted': False})
print(json.dumps({'freeze': desc(fp), 'receipt': desc(rp), 'files': len(files),
                  'bytes': sum(p.stat().st_size for p in files), 'shared_ratio': shared['scale'],
                  'gif_delays_ms': delays, 'frames': frames}, ensure_ascii=False))
