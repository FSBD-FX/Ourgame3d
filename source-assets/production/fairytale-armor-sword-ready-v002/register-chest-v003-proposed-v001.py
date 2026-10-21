"""Measured native161 central boss -> unchanged158 cloth design A, integer only."""
from pathlib import Path
import datetime, hashlib, json
import numpy as np
from PIL import Image

R = Path(__file__).resolve().parent
OUT = R / 'chest-registration-proposed-v001'
assert not OUT.exists(), OUT
OUT.mkdir()
measurement = R / 'measurement-candidate-v002.json'
M = json.loads(measurement.read_text(encoding='utf-8'))
E = json.loads((R / 'chest-extraction-v003/extraction-receipt-v001.json').read_text(encoding='utf-8'))
# Manual measurements of this retained central boss outer ink/AA contour only.
# Opposed outer feature edges: xmin,xmax,ymin,ymax, INCLUSIVE source coordinates.
BOSS_EDGES = [[258, 270, 255, 267], [257, 269, 255, 267], [256, 268, 254, 266], [257, 269, 254, 266]]
BOSS_A = [[264, 261], [263, 261], [262, 260], [263, 260]]
BODY_TARGETS = [[259, 271], [259, 267], [259, 271], [259, 267]]

def desc(p):
    b = p.read_bytes()
    return {'path': p.as_posix(), 'bytes': len(b), 'sha256': hashlib.sha256(b).hexdigest()}

def shift_rgba(a, dx, dy):
    h, w = a.shape[:2]
    b = np.zeros_like(a)
    sx0, sx1 = max(0, -dx), min(w, w - dx)
    sy0, sy1 = max(0, -dy), min(h, h - dy)
    b[sy0 + dy:sy1 + dy, sx0 + dx:sx1 + dx] = a[sy0:sy1, sx0:sx1]
    return b

frames = []; contact = Image.new('RGBA', (2048, 512), (0, 0, 0, 0))
for i, (edges, actual_A, target) in enumerate(zip(BOSS_EDGES, BOSS_A, BODY_TARGETS)):
    f = E['frames'][i]; p = Path(f['source']['path'])
    assert desc(p) == f['source']
    assert M['frames'][i]['body_attachment_design_A']['Chest']['point'] == target
    assert actual_A == [(edges[0] + edges[1]) // 2, (edges[2] + edges[3]) // 2]
    source = np.asarray(Image.open(p)).copy()
    assert source.shape == (512, 512, 4)
    dx, dy = target[0] - actual_A[0], target[1] - actual_A[1]
    registered = shift_rgba(source, dx, dy)
    ys, xs = np.where(np.any(source != 0, axis=2))
    assert np.all((xs + dx >= 0) & (xs + dx < 512) & (ys + dy >= 0) & (ys + dy < 512))
    assert np.array_equal(registered[ys + dy, xs + dx], source[ys, xs])
    assert np.array_equal(shift_rgba(registered, -dx, -dy), source)
    assert np.array_equal(source.sum(axis=(0, 1), dtype=np.uint64), registered.sum(axis=(0, 1), dtype=np.uint64))
    q = OUT / f'registered/frame-{i}.png'; q.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(registered).save(q)
    assert np.array_equal(np.asarray(Image.open(q)), registered)
    bbox = Image.fromarray(registered).getchannel('A').getbbox()
    cp = OUT / f'diagnostics/frame-{i}-central-boss-source-crop.png'; cp.parent.mkdir(parents=True, exist_ok=True)
    roi = [edges[0] - 3, edges[2] - 3, edges[1] + 4, edges[3] + 4]
    Image.open(p).crop(roi).save(cp)
    # Actual source-only body partition; no Far/near shoulder or sword invented.
    layer_sources = []
    composite = Image.new('RGBA', (512, 512), (0, 0, 0, 0))
    for name in ['BodyRest', 'Chest', 'NearArmWithoutHand', 'NearHand']:
        lp = q if name == 'Chest' else R / f'body-partition-v002/layers/{name}/frame-{i}.png'
        layer_sources.append({'layer': name, 'source': desc(lp)})
        composite = Image.alpha_composite(composite, Image.open(lp))
    ap = OUT / f'assemblies/frame-{i}-chest-only-proposed.png'; ap.parent.mkdir(parents=True, exist_ok=True)
    composite.save(ap); contact.paste(composite, (512 * i, 0))
    frames.append({'frame': i, 'source': desc(p), 'boss_feature': 'Actual central raised round boss outer ink/AA contour',
        'manual_opposed_boss_contour_edges_inclusive': edges, 'actual_component_A_candidate': actual_A,
        'actual_A_uncertainty_source_px': 2, 'not_component_bbox_or_highlight_center': True,
        'body_design_target_A_unchanged': target, 'body_design_target_uncertainty_source_px': 3,
        'body_target_is_bone_or_existing_rivet': False, 'integer_translation': [dx, dy],
        'selected_A_maps_exactly_to_selected_target': [actual_A[0] + dx, actual_A[1] + dy] == target,
        'mapping_exact_is_not_fit_or_physical_error_proof': True, 'registered': desc(q), 'registered_alpha_bbox_px': list(bbox),
        'all_original_payload_RGBA_preserved': True, 'inverse_integer_translation_RGBA_exact': True,
        'clipped_nonzero_RGBA_coordinates': 0, 'resized_rotated_warped_or_recolored': False,
        'boss_diagnostic_crop': desc(cp), 'boss_diagnostic_crop_source_ROI': roi,
        'candidate_body_stack_sources': layer_sources, 'static_chest_only_assembly': desc(ap),
        'new_registered_or_assembly_explicitly_viewed': False,
        'near_and_far_targets_for_later_comparison': {k: M['frames'][i]['body_attachment_design_A'][k] for k in ['NearShoulder', 'FarShoulder']}})
contact_path = OUT / 'assemblies/chest-only-four-contact-proposed.png'; contact.save(contact_path)
rp = OUT / 'measurement-and-registration-v001.json'
rp.write_text(json.dumps({'schema': 'native161-central-boss-integer-registration-proposed-v1',
    'created_local': datetime.datetime.now().astimezone().isoformat(), 'author': 'scale_tests',
    'source_viewed_after_retention': 'E158 four original512RGBA and four unscaled actual-alpha crops',
    'body_measurement': desc(measurement), 'source_extraction': desc(R / 'chest-extraction-v003/extracted-freeze-v001.json'),
    'script': desc(Path(__file__).resolve()), 'shared_extraction_ratio_unchanged': E['shared_row_ratio'],
    'frames': frames, 'static_contact': desc(contact_path), 'source_request_durations_ms': [167] * 4,
    'source_curated_changed': False, 'new_outputs_explicitly_viewed': False,
    'semantic_body_partition_accepted': False, 'helmet_neck_hand_and_belt_clearance_accepted': False,
    'body_target_adjusted': False, 'runtime_fit_or_motion_accepted': False,
    'native_called': False, 'ue_import_called': False, 'formal_complete_units': 0}, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
notes = OUT / 'measurement-limit-v001.md'
notes.write_text('''# 中央boss实际候选与整数试装

E158后实际看四原512RGBA及原像素alpha-bbox crops，选择中央圆boss自身外墨圈/抗锯齿对向边，不是全甲bbox中心、highlight中心或左strapbolt。4候选A264261/263261/262260/263260，边界约±1–2px；所取outer ink extents见JSON，物理boss投影并非理想精确圆，故不声称骨/像素真值零误差。

原158衣面设计target259271/259267/259271/259267保持，±3px且不是骨/原铆钉。整数平移-5+10/-4+6/-3+11/-4+7，没有新缩放/旋转/warp/重色。共同ratio保持.1937984496124031。全部非零原RGBA和AA字节不丢，逆整数平移恢复原curated全RGBA exact，selected A对target零残差只证明构造，不能等同实际穿戴误差0。

registered独立存放，原curated不动。实际源BodyRest→Chest→NearArmWithoutHand→NearHand静态合成仅候选：没有虚构肩片/剑，原body partition语义仍候选。bbox腰上有数px余量只是定位辅助，领口/strap/近袖/手/腰保护须保全后实看；未新view，不暗改target迎合。若真实边缘压领口再提出明确设计点修订，保本版。静图不能证明72px运行、四甲/动作或完整装备。
''', encoding='utf-8')
files = sorted([p for p in OUT.rglob('*') if p.is_file()] + [Path(__file__).resolve()])
fp = OUT / 'registered-freeze-v001.json'
fp.write_text(json.dumps({'schema': 'native161-proposed-registration-freeze-v1', 'file_count': len(files),
    'total_bytes': sum(p.stat().st_size for p in files), 'files': [desc(p) for p in files],
    'new_outputs_explicitly_viewed': False, 'accepted': False, 'import_permitted': False}, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'freeze': desc(fp), 'receipt': desc(rp), 'files': len(files), 'bytes': sum(p.stat().st_size for p in files),
                  'actual_A_candidates': BOSS_A, 'body_targets_unchanged': BODY_TARGETS,
                  'integer_offsets': [f['integer_translation'] for f in frames]}, ensure_ascii=False))
