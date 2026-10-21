"""Standard independent native162/163 shoulder rows; no A invention or import."""
from pathlib import Path
import argparse, datetime, hashlib, json, subprocess, sys
from PIL import Image

R = Path(__file__).resolve().parent
SG = Path('C:/Users/22499/.codex/skills/sprite-gen')
parser = argparse.ArgumentParser()
parser.add_argument('--component', choices=['NearShoulder', 'FarShoulder'], required=True)
args = parser.parse_args()
SPECS = {
    'NearShoulder': {'native': 162, 'key': 'nearshoulder', 'state': 'armor_shoulder_near_sword_ready',
        'sha': '444e33013b8d964478d1e5db08e70cd1ff245e99c74a8e0a876d110648c5af57', 'bytes': 1340248,
        'raw_note': 'Wide cap with a top leather strap and visible central round front mounting rivet. Body upper-sleeve fit/helmet/neck/hand clearance remain unproved.',
        'central_feature_observed_from_retained_raw': True},
    'FarShoulder': {'native': 163, 'key': 'farshoulder', 'state': 'armor_shoulder_far_sword_ready',
        'sha': '9daa4e916b662c1057dd26f2e6a8028286e82618af666d61902fb415d8114f5f', 'bytes': 1256441,
        'raw_note': 'Short compressed cap has a visible circular top-strap rivet; no obvious central raised boss on the front plane. This deviates from the actual central-A prompt. A real strap feature may support a new trial design, not retrospective central-contract success.',
        'central_feature_observed_from_retained_raw': False}}
S = SPECS[args.component]
RUN = R / f'run-{S["key"]}-ready-v002'
OUT = R / f'{S["key"]}-extraction-v002'
STATE = S['state']
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
assert desc(raw)['sha256'] == S['sha'] and raw.stat().st_size == S['bytes']
generation = R / f'generation-control-v001/generation-request{S["native"]}-v001.json'
gj = json.loads(generation.read_text(encoding='utf-8'))
assert 'CENTRAL raised round mounting rivet' in gj['prompt']
before = (RUN / 'sprite-request.json').read_bytes()
(OUT / 'sprite-request-before-extraction.json').write_bytes(before)
request = json.loads(before)
assert request['states'][STATE]['frames'] == 4 and request['states'][STATE]['durations_ms'] == [167] * 4
wrapper = Path('F:/Ourgame/tools/scripts/extract-sprite-shared-row-scale.py')
assert desc(wrapper)['sha256'] == '2d7464dc2e8dd962a7d4dc170c0a7401d09cf1a626415309b4921b7d89d88aa3'
commands = []
for name, tool, extra in [('extract-shared-row', wrapper, []),
                          ('compose-atlas', SG / 'scripts/compose_sprite_atlas.py', []),
                          ('export-curated', SG / 'scripts/export_curated_pngs.py', ['--state', STATE]),
                          ('preview', SG / 'scripts/preview_animation.py', [])]:
    argv = [sys.executable, '-X', 'utf8', '-B', str(tool), '--run-dir', str(RUN)] + extra
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
        bbox = im.getchannel('A').getbbox(); assert bbox
        crop = OUT / f'diagnostics-v001/frame-{i}-actual-alpha-bbox.png'
        crop.parent.mkdir(parents=True, exist_ok=True); im.crop(bbox).save(crop)
        assert Image.open(crop).tobytes() == im.crop(bbox).tobytes()
    frames.append({'frame': i, 'source': desc(p), 'alpha_bbox_px': list(bbox),
                   'visible_bbox_size_px': [bbox[2] - bbox[0], bbox[3] - bbox[1]],
                   'actual_component_A': None, 'alternate_actual_strap_feature_A': None,
                   'unscaled_diagnostic': desc(crop), 'new_alpha_explicitly_viewed': False})
gif = RUN / 'qa' / f'{STATE}.gif'; delays = []
with Image.open(gif) as im:
    for i in range(im.n_frames):
        im.seek(i); delays.append(im.info.get('duration'))
timing = {'requested_durations_ms': [167] * 4, 'actual_standard_gif_delays_ms': delays, 'gif': desc(gif),
          'exact_requested_timing_proved_by_standard_preview': delays == [167] * 4,
          'basis': 'Standard preview.py uses fps, not durations_ms; GIF delay has10ms precision.',
          'request_unchanged': True, 'gif_retimed': False, 'gif_played': False}
write('standard-preview-timing-v001.json', timing)
write('raw-feature-contract-observation-v001.md', f'''# Native{S['native']} {args.component}：源特征与合同边界

2026-10-16，scale_tests。相应E155/E157开放后实际view已保全raw（工具显示缩小，未据显示图量精确A）。{S['raw_note']}

真实generation-request要求“CENTRAL raised round mounting rivet”作为唯一future A，不能将其他feature或bbox中心冒充该中央feature。近肩的存在性观察不等同穿戴通过；远肩没有明显中央boss，原中央A要求保持未满足。root允许后续量真实top-strap rivet只支持明确新试装设计，不能追溯改旧prompt/原合同状态。

本次只有标准shared-row提取、atlas、curated、preview，原raw/request不改，不逐帧fit/旋转/warp/mirror。每片actual A全null，派生须root新E保全才显式view。实际GIF metadata另记，标准fps preview不能证明4×167ms精确时序，未播放或重定时。

将来的bodyTargetA只是158可见衣面附件设计点±3–5px，并非隐藏骨或不可调整精确socket；必须用真实原像素试装查盔/颈/手/前臂、胸肩层序与实际可见贡献，不能盲贴压盔。无native/导入/UE/Source/台账写入，完整内容0/15。
''')
receipt = {'schema': 'native-shoulder4-shared-extraction-v2', 'created_local': datetime.datetime.now().astimezone().isoformat(),
           'native_request': S['native'], 'component': args.component, 'raw': desc(raw), 'actual_generation_request': desc(generation),
           'request': desc(RUN / 'sprite-request.json'), 'commands': commands, 'frames': frames,
           'frames_manifest': desc(RUN / 'frames/frames-manifest.json'), 'QA_errors': manifest['errors'], 'QA_warnings': manifest['warnings'],
           'shared_row_ratio': shared['scale'], 'shared_row_fit': shared, 'durations_ms': [167] * 4,
           'raw_independent_observation': S['raw_note'], 'central_feature_observed_from_retained_raw': S['central_feature_observed_from_retained_raw'],
           'original_central_A_contract_passed': False if args.component == 'FarShoulder' else None,
           'standard_preview_timing': timing, 'new_outputs_explicitly_viewed': False,
           'actual_component_A': [None] * 4, 'request_modified': False, 'alignment_or_fit_accepted': False,
           'native_called': False, 'ue_import_called': False, 'formal_complete_units': 0}
rp = write('extraction-receipt-v001.json', receipt)
files = sorted([p for p in RUN.rglob('*') if p.is_file()] + [p for p in OUT.rglob('*') if p.is_file()] + [Path(__file__).resolve()])
fp = write('extracted-freeze-v001.json', {'schema': 'native-shoulder-extraction-freeze-v2',
           'created_local': datetime.datetime.now().astimezone().isoformat(), 'native_request': S['native'], 'component': args.component,
           'file_count': len(files), 'total_bytes': sum(p.stat().st_size for p in files), 'files': [desc(p) for p in files],
           'new_outputs_explicitly_viewed': False, 'accepted': False, 'actual_A_measured': False, 'import_permitted': False})
print(json.dumps({'freeze': desc(fp), 'receipt': desc(rp), 'files': len(files), 'bytes': sum(p.stat().st_size for p in files),
                  'shared_ratio': shared['scale'], 'gif_delays_ms': delays, 'frames': frames}, ensure_ascii=False))
