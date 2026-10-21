"""Native160 rejected-facing row: standard shared extraction, no flips or import."""
from pathlib import Path
import datetime, hashlib, json, subprocess, sys
from PIL import Image

R = Path(__file__).resolve().parent
SG = Path('C:/Users/22499/.codex/skills/sprite-gen')
RUN = R / 'run-chest-ready-v002'
OUT = R / 'chest-extraction-v002'
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
assert desc(raw)['sha256'] == '4ced46774ab5731c1696949934b534faf6653c9510929cebe4c0108671a7e376'
assert raw.stat().st_size == 1279139
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
                   'native_facing_visual_status_from_raw': 'wrong/opposite3of4' if i == 3 else 'right-facing candidate only',
                   'actual_component_A': None, 'actual_component_attachment_accepted': False,
                   'unscaled_diagnostic': desc(crop), 'new_alpha_explicitly_viewed': False})

write('actual-raw-facing-rejection-v001.md', '''# Native160 Chest4：固定朝向失败，保留拒绝

2026-10-16，scale_tests。E148保全后实际独立view原2172×724 raw（工具显示时缩至2048×683，未据此作像素挂点量测）。0–2片外展肩带、较大的侧armhole集中在image-LEFT；第4片相反，在image-RIGHT，板体压缩侧同时交换。属于透视/朝向逆转，不能当呼吸变化或仅换明暗。固定nativeFacing+1四片合同失败，整row拒绝导入；不mirror第4片，不覆盖raw/原prompt/旧freeze。

本次只按原request标准shared-row提取四片、atlas、curated、preview。结构QA不能推翻视觉拒绝。新派生待另批E保全才view；actual component A均null。原0可在保全/审阅后仅作下一次正向造型/材料参考，不能宣称当前四帧已可用。现胸两侧strap bolt不是body中央cloth A259271的同一feature，不把左bolt盲贴中央或以bbox-center造假；下一候选若加入清晰中央boss须生成后再测。无导入/UE/Source/台账/新native调用，完整内容仍0/15。
''')
receipt = {'schema': 'native160-chest4-shared-extraction-rejected-facing-v2',
           'created_local': datetime.datetime.now().astimezone().isoformat(), 'native_request': 160,
           'raw': desc(raw), 'request': desc(RUN / 'sprite-request.json'), 'commands': commands,
           'frames': frames, 'frames_manifest': desc(RUN / 'frames/frames-manifest.json'),
           'QA_errors': manifest['errors'], 'QA_warnings': manifest['warnings'],
           'shared_row_ratio': shared['scale'], 'shared_row_fit': shared, 'durations_ms': [167] * 4,
           'row_visual_status': 'REJECTED: frame3 opposite perspective/nativeFacing',
           'raw_explicitly_viewed_after_E148': True, 'new_outputs_explicitly_viewed': False,
           'mirrored_or_pose_repaired': False, 'request_modified': False,
           'actual_component_A': [None] * 4, 'alignment_or_fit_accepted': False,
           'ue_import_called': False, 'native_called': False, 'formal_complete_units': 0}
rp = write('extraction-receipt-v001.json', receipt)
files = sorted([p for p in RUN.rglob('*') if p.is_file()] + [p for p in OUT.rglob('*') if p.is_file()] + [Path(__file__).resolve()])
fp = write('extracted-freeze-v001.json', {'schema': 'native160-rejected-chest-extraction-freeze-v2',
           'created_local': datetime.datetime.now().astimezone().isoformat(), 'file_count': len(files),
           'total_bytes': sum(p.stat().st_size for p in files), 'files': [desc(p) for p in files],
           'row_visual_status': receipt['row_visual_status'], 'new_outputs_explicitly_viewed': False,
           'accepted': False, 'component_A_measured': False, 'import_permitted': False})
print(json.dumps({'freeze': desc(fp), 'receipt': desc(rp), 'files': len(files),
                  'bytes': sum(p.stat().st_size for p in files), 'shared_ratio': shared['scale'],
                  'frames': frames, 'visual_status': receipt['row_visual_status']}, ensure_ascii=False))
