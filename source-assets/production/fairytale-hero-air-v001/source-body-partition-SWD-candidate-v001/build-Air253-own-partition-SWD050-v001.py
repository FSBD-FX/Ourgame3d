"""Offline, exclusive-output source partition and rigid weapon candidate. No UE or View.

Original body RGBA is assigned without color/alpha change to one of five owners.
Only the independent sword and presentation layout undergo declared resampling.
"""
from pathlib import Path
import datetime as dt
import hashlib
import json
import math
import shutil

import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path('F:/Ourgame')
OUT = Path(__file__).resolve().parent
MEDIA = ROOT / '过程图稿与视频/2026-10-19_钟盔Air253自身五分区军剑腰带投影候选_v001'
OLD = ROOT / 'source-assets/production/fairytale-hero-air-v001/source-body-review-candidate-v001/Air253-five-bodyparts-author-proposal-v001.json'
SOURCE_MANIFEST = ROOT / 'source-assets/production/fairytale-hero-state-gap-v001/air-state-preparation-v001/extraction-v001/run-Air6-shared-HD-v001/frames/frames-manifest.json'
SWORD = ROOT / 'source-assets/production/first-unit-animation-v002/components/military-sword-clean-v001.png'
READY = ROOT / 'source-assets/production/fairytale-sword-v001/run-ready-v002/curated/frame-0.png'
READY_MARKERS = ROOT / 'source-assets/production/fairytale-sword-v001/ready-measurement-v002/ready-marker-proposal-v002.json'
K = 72.0 / 416.0
WEAPON_SCALE = .50
SWORD_GRIP = np.array([99., 256.])
BELTS = [[267, 300], [253, 343], [252, 373], [255, 292], [242, 370], [267, 305]]
READY_BELT = [264, 307]
READY_ROOT = [256, 464]
BELT_ROOT_OFFSET = [-8, 157]
OWNERS = ['BodyRest', 'NearArmWithoutHand', 'HelmetForeground', 'NearHand', 'FarHandForeground']
PRIORITY = ['NearHand', 'FarHandForeground', 'HelmetForeground', 'NearArmWithoutHand']
STACK = ['BodyRest', 'NearArmWithoutHand', 'HelmetForeground', 'IndependentSword', 'FarHandForeground', 'NearHand']
COLORS = {'BodyRest': (150, 150, 150), 'NearArmWithoutHand': (230, 95, 100), 'HelmetForeground': (235, 205, 85), 'NearHand': (95, 215, 160), 'FarHandForeground': (100, 155, 245)}


def pin(p):
    p = Path(p)
    data = p.read_bytes()
    return {'path': p.as_posix(), 'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()}


def read(p):
    return json.loads(Path(p).read_text(encoding='utf-8-sig'))


def write(rel, value):
    p = OUT / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open('x', encoding='utf-8', newline='\n') as f:
        f.write(value if isinstance(value, str) else json.dumps(value, ensure_ascii=False, indent=2) + '\n')
    return p


def save(rel, im):
    p = OUT / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open('xb') as f:
        im.save(f, format='PNG')
    return p


def copy_exclusive(src, dst):
    dst.parent.mkdir(parents=True, exist_ok=True)
    with Path(src).open('rb') as rf, dst.open('xb') as wf:
        shutil.copyfileobj(rf, wf)
    assert pin(src)['sha256'] == pin(dst)['sha256']
    return dst


def bbox(m):
    y, x = np.where(m)
    return None if not len(x) else [int(x.min()), int(y.min()), int(x.max() + 1), int(y.max() + 1)]


def poly_mask(polygon):
    m = Image.new('L', (512, 512), 0)
    ImageDraw.Draw(m).polygon([tuple(q) for q in polygon], fill=255)
    return np.asarray(m) > 0


def sample_neighborhood(a, xy):
    x, y = xy
    v = a[y-3:y+4, x-3:x+4]
    assert v.shape == (7, 7, 4)
    return {'source_xy': xy, 'center_RGBA': a[y, x].tolist(),
            'author_uncertainty_source_px_each_axis': 3,
            'uncertainty_region_inclusive_xyxy': [x-3, y-3, x+3, y+3],
            'actual_7x7_RGBA_rows': v.tolist(),
            'actual_7x7_RGBA_min': v.min(axis=(0, 1)).tolist(),
            'actual_7x7_RGBA_max': v.max(axis=(0, 1)).tolist(),
            'alpha_nonzero_samples': int(np.count_nonzero(v[:, :, 3])),
            'alpha255_samples': int(np.count_nonzero(v[:, :, 3] == 255)),
            'uncertainty_is_artist_not_physical_bone': True,
            'pixel_color_does_not_establish_anatomical_belt_location': True}


def rigid_sword(grip, axis, sword):
    angle = math.atan2(axis[1], axis[0])
    c, s = math.cos(angle), math.sin(angle)
    g = np.asarray(grip, float)
    aff = (c/WEAPON_SCALE, s/WEAPON_SCALE,
           float(SWORD_GRIP[0]-(c*g[0]+s*g[1])/WEAPON_SCALE),
           -s/WEAPON_SCALE, c/WEAPON_SCALE,
           float(SWORD_GRIP[1]-(-s*g[0]+c*g[1])/WEAPON_SCALE))
    # Premultiplication prevents a transparent RGB fringe. Only this sword is resampled.
    im = sword.convert('RGBa').transform((512, 512), Image.Transform.AFFINE, aff,
                                         resample=Image.Resampling.BICUBIC).convert('RGBA')

    def tp(q):
        return (g + WEAPON_SCALE * np.array([[c, -s], [s, c]]) @ (np.asarray(q, float)-SWORD_GRIP)).tolist()

    assert np.allclose(tp(SWORD_GRIP), g, rtol=0, atol=1e-12)
    return im, aff, math.degrees(angle), tp


def composite(layers, swd):
    out = Image.new('RGBA', (512, 512))
    for owner in STACK:
        layer = swd if owner == 'IndependentSword' else Image.fromarray(layers[owner])
        out = Image.alpha_composite(out, layer)
    return out


def place(im, root, out_size, display_root, scale):
    aff = (1/scale, 0., float(root[0]-display_root[0]/scale),
           0., 1/scale, float(root[1]-display_root[1]/scale))
    return im.convert('RGBa').transform(out_size, Image.Transform.AFFINE, aff,
                                      resample=Image.Resampling.BICUBIC).convert('RGBA')


def font(size):
    return ImageFont.truetype('C:/Windows/Fonts/arial.ttf', size)


def board_paste(board, im, xy):
    board.alpha_composite(im, dest=xy)


def run():
    assert not MEDIA.exists(), 'Exclusive NEW F media folder already exists; do not overwrite.'
    assert not (OUT / 'Air253-own-five-partitions-SWD050-belt-root-candidate-v001.json').exists()
    assert set(p.name for p in OUT.iterdir()) == {Path(__file__).name}, 'Candidate has prior output; preserve and stop.'
    assert pin(OLD)['sha256'] == '5dd3e07690fd9733e007b88fcf58298f543298fdeaad879f4c5f75c8a7e1108e'
    assert pin(SWORD)['sha256'] == '2efb5519fb3c7ed5a63e58d00c84e39aa02355274af36b43c1775570badded5a'
    assert pin(READY)['sha256'] == 'd3f766506a9cc623c38787836a9c23c0126d185d1bdf7e8946181efd554338c5'
    assert pin(SOURCE_MANIFEST)['sha256'] == '03e176c5eb4b8edf65363530be2d4758975b60f2ddbaee1b1075ea88342184bd'
    old = read(OLD)
    assert len(old['frames']) == 6
    sword = Image.open(SWORD).convert('RGBA')
    assert sword.size == (512, 512)
    source_paths = [Path(r['source']['path']) for r in old['frames']] + [READY, SWORD, OLD, READY_MARKERS, SOURCE_MANIFEST]
    source_pins_before = [pin(p) for p in source_paths]
    copy_mapping = []
    for i, r in enumerate(old['frames']):
        assert pin(r['source']['path']) == r['source']
        dst = copy_exclusive(r['source']['path'], OUT / f'source-copied/Air253/frame-{i}.png')
        copy_mapping.append({'original': r['source'], 'copy': pin(dst)})
    for p, rel in [(READY, 'Ready158-reference-only.png'), (SWORD, 'military-sword-clean-v001.png'),
                   (OLD, OLD.name), (READY_MARKERS, READY_MARKERS.name), (SOURCE_MANIFEST, SOURCE_MANIFEST.name)]:
        dst = copy_exclusive(p, OUT / 'source-copied' / rel)
        copy_mapping.append({'original': pin(p), 'copy': pin(dst)})
    rows, wholes, owner_panels, roots, layer_arrays, original_arrays = [], [], [], [], [], []
    for i, prior in enumerate(old['frames']):
        a = np.asarray(Image.open(prior['source']['path']).convert('RGBA'))
        assert a.shape == (512, 512, 4)
        original_arrays.append(a)
        alive = a[:, :, 3] > 0
        claimed = np.zeros((512, 512), bool)
        masks, layers, layer_pins, mask_pins = {}, {}, {}, {}
        for owner in PRIORITY:
            m = poly_mask(prior['artist_visible_polygon_by_owner'][owner]) & alive & ~claimed
            claimed |= m
            masks[owner] = m
        # Also owns alpha-zero RGB bytes, allowing exact full-RGBA reconstruction.
        masks['BodyRest'] = ~claimed
        for owner in OWNERS:
            layers[owner] = np.where(masks[owner][:, :, None], a, 0).astype(np.uint8)
            layer_pins[owner] = pin(save(f'body-layers/{owner}/frame-{i}.png', Image.fromarray(layers[owner])))
            mask_pins[owner] = pin(save(f'masks/{owner}/frame-{i}-mask-L.png', Image.fromarray(np.where(masks[owner] & alive, 255, 0).astype(np.uint8))))
        rgba_sum = np.stack([layers[o].astype(np.uint16) for o in OWNERS]).sum(axis=0)
        occupancy = np.stack([layers[o][:, :, 3] > 0 for o in OWNERS]).sum(axis=0)
        assert np.array_equal(rgba_sum, a)
        assert np.all(occupancy[alive] == 1) and not np.any(occupancy[~alive])
        reconstructed = Image.new('RGBA', (512, 512))
        for owner in OWNERS:
            reconstructed = Image.alpha_composite(reconstructed, Image.fromarray(layers[owner]))
        # Alpha compositing canonicalizes RGB of alpha-zero pixels; preserve/check them separately.
        reconstructed_a = np.asarray(reconstructed)
        assert np.array_equal(reconstructed_a[alive], a[alive])
        reconstructed_full = np.asarray(rgba_sum, np.uint8)
        rp = save(f'reconstruction/frame-{i}-exact-original-RGBA.png', Image.fromarray(reconstructed_full))
        assert np.array_equal(np.asarray(Image.open(rp).convert('RGBA')), a)
        root = [BELTS[i][0]+BELT_ROOT_OFFSET[0], BELTS[i][1]+BELT_ROOT_OFFSET[1]] if i < 4 else READY_ROOT.copy()
        roots.append(root)
        grip, axis = prior['grip_source_artist'], prior['axis_artist_directed']
        gx, gy = grip
        assert masks['NearHand'][gy, gx] and a[gy, gx, 3] >= 192
        swd, inverse_affine, angle, tp = rigid_sword(grip, axis, sword)
        swd_a = np.asarray(swd)
        swd_mask = swd_a[:, :, 3] > 0
        edge = int(swd_mask[0, :].sum() + swd_mask[-1, :].sum() + swd_mask[:, 0].sum() + swd_mask[:, -1].sum())
        assert edge == 0, 'Rigid sword cropped at source canvas edge; retain failure rather than refit.'
        whole = composite(layers, swd)
        wa = np.asarray(whole)
        outside_visible = ~swd_mask & alive
        delta_outside = int(np.count_nonzero(np.any(wa[outside_visible] != a[outside_visible], axis=1)))
        assert delta_outside == 0
        near_core = masks['NearHand'] & (a[:, :, 3] == 255)
        near_core_changed = int(np.count_nonzero(np.any(wa[near_core] != a[near_core], axis=1)))
        assert near_core_changed == 0
        sb = sample_neighborhood(a, BELTS[i])
        sb['author_intent'] = 'Parent explicitly selected visible belt projection reference; color sampling is an audit, not an anatomical detection.'
        swd_path = save(f'sword-layers/frame-{i}-SWD-rigid050.png', swd)
        whole_path = save(f'composites/frame-{i}-Air253-SWD-held-candidate.png', whole)
        owner_color = np.zeros_like(a)
        for o in OWNERS:
            m = masks[o] & alive
            owner_color[m, :3] = COLORS[o]
            owner_color[m, 3] = a[m, 3]
        owner_path = save(f'owner-diagnostic/frame-{i}-five-owner-colors.png', Image.fromarray(owner_color))
        polygon_overlaps = {o: int(np.count_nonzero(poly_mask(prior['artist_visible_polygon_by_owner'][o]) & alive & ~masks[o])) for o in PRIORITY}
        row = {'frame': i, 'pose_label': prior['pose_label'], 'source': prior['source'],
               'body_RGBA_sha256': hashlib.sha256(a.tobytes()).hexdigest(), 'source_alpha_bbox': bbox(alive),
               'body_layers': layer_pins, 'masks': mask_pins, 'owner_color_diagnostic': pin(owner_path),
               'artist_visible_polygon_by_owner': prior['artist_visible_polygon_by_owner'],
               'body_partition_proof': {'all_RGBA_exact_sum_reconstruction': True, 'full_saved_RGBA_exact': True,
                   'all_nontransparent_pixels_exactly_one_owner': True, 'overlap_pixels': int(np.count_nonzero(occupancy > 1)),
                   'unowned_nontransparent_pixels': int(np.count_nonzero(alive & (occupancy != 1))),
                   'alpha_zero_nonzero_RGB_source_pixels': int(np.count_nonzero(~alive & np.any(a[:, :, :3] != 0, axis=2))),
                   'all_transparent_RGB_bytes_preserved_by_BodyRest': True, 'source_RGBA_resampled': False,
                   'owner_alpha_pixel_counts': {o: int(np.count_nonzero(layers[o][:, :, 3])) for o in OWNERS},
                   'priority_excluded_polygon_alpha_pixels': polygon_overlaps,
                   'exact_reconstruction': pin(rp), 'semantic_boundaries_viewed_after_cut': False},
               'author_belt_reference': sb,
               'author_Root': {'xy': root, 'rule': 'belt+[-8,+157]' if i < 4 else 'fixed [256,464] preserving landing compression',
                   'parent_explicit_rule': True, 'may_be_outside_canvas': True, 'outside_source_canvas': not (0 <= root[0] < 512 and 0 <= root[1] < 512),
                   'virtual_projection_reference_not_bone_or_floor': True,
                   'actual_belt_minus_Root_xy': [BELTS[i][0]-root[0], BELTS[i][1]-root[1]],
                   'root_uncertainty_source_px_each_axis': 3 if i < 4 else None,
                   'root_uncertainty_note': 'Air Root inherits author belt +/-3px; Land fixed contract has no inferred point confidence.'},
               'author_binding': {'Grip_xy': grip, 'Grip_RGBA': a[gy, gx].tolist(), 'Grip_owner': 'NearHand',
                   'Grip_uncertainty_source_px': 6, 'Axis_xy': axis, 'angle_degrees': angle,
                   'axis_measured_from_handle': False, 'actual_physical_grip_or_socket': False,
                   'weapon_scale': WEAPON_SCALE, 'source_Grip_xy': SWORD_GRIP.tolist(),
                   'inverse_affine': list(inverse_affine), 'tip_reference_source_xy': tp([482, 256]),
                   'sword_alpha_bbox': bbox(swd_mask), 'canvas_edge_sword_alpha_pixels': edge,
                   'sword_alpha_pixels_under_nearhand': int(np.count_nonzero(swd_mask & masks['NearHand'])),
                   'nearhand_alpha255_changed_pixels': near_core_changed,
                   'body_visible_RGBA_changed_outside_sword_alpha': delta_outside,
                   'nearhand_last_in_stack': True, 'sword_layer': pin(swd_path)},
               'SWD_composite': pin(whole_path), 'TrialAllowed': False, 'FinalAccepted': False}
        rows.append(row)
        wholes.append(whole)
        owner_panels.append(Image.fromarray(owner_color))
        layer_arrays.append(layers)
    ra = np.asarray(Image.open(READY).convert('RGBA'))
    rm = read(READY_MARKERS)['frames'][0]
    assert rm['source'] == pin(READY) and rm['source_root_px'] == READY_ROOT
    ready_hand = poly_mask(rm['visible_fist_replay_polygon_candidate_px']) & (ra[:, :, 3] > 0)
    ready_sword, _, ready_angle, ready_tp = rigid_sword(rm['grip_candidate_px'], rm['handle_axis_candidate_xy'], sword)
    ready_without_hand = Image.fromarray(np.where(ready_hand[:, :, None], 0, ra).astype(np.uint8))
    ready_hand_layer = Image.fromarray(np.where(ready_hand[:, :, None], ra, 0).astype(np.uint8))
    ready_whole = Image.alpha_composite(Image.alpha_composite(ready_without_hand, ready_sword), ready_hand_layer)
    ready_whole_path = save('reference-only/Ready158-SWD050-existing-author-binding-only.png', ready_whole)
    ready_belt = sample_neighborhood(ra, READY_BELT)
    ready_reference = {'source': pin(READY), 'original_marker_contract': pin(READY_MARKERS),
                       'author_belt_reference': ready_belt, 'Root_xy': READY_ROOT,
                       'belt_to_Root_xy': BELT_ROOT_OFFSET, 'Grip_xy': rm['grip_candidate_px'],
                       'Axis_xy': rm['handle_axis_candidate_xy'], 'angle_degrees': ready_angle,
                       'tip_reference_source_xy': ready_tp([482, 256]), 'SWD_reference': pin(ready_whole_path),
                       'reference_only': True, 'Ready_own_hand_mask_never_used_for_Air': True,
                       'Ready_source_RGBA_modified': False, 'Ready_runtime_or_contract_changed': False}
    sequence = [{'label': 'Ready158 reference', 'root': READY_ROOT, 'grip': rm['grip_candidate_px'], 'tip': ready_tp([482, 256]), 'angle': ready_angle}]
    sequence += [{'label': f'Air{i} {r["pose_label"]}', 'root': roots[i], 'grip': r['author_binding']['Grip_xy'],
                  'tip': r['author_binding']['tip_reference_source_xy'], 'angle': r['author_binding']['angle_degrees']} for i, r in enumerate(rows)]
    sequence.append(sequence[0].copy())
    joins = []
    for prev, nxt in zip(sequence, sequence[1:]):
        dgrip = (np.asarray(nxt['grip'])-nxt['root']-(np.asarray(prev['grip'])-prev['root']))*K
        dtip = (np.asarray(nxt['tip'])-nxt['root']-(np.asarray(prev['tip'])-prev['root']))*K
        joins.append({'from': prev['label'], 'to': nxt['label'], 'constant_K': K,
                      'next_minus_previous_root_relative_grip_display_xy': dgrip.tolist(),
                      'root_relative_grip_display_distance_px': float(np.linalg.norm(dgrip)),
                      'next_minus_previous_root_relative_tip_display_xy': dtip.tolist(),
                      'next_minus_previous_author_angle_degrees': nxt['angle']-prev['angle'],
                      'actual_physics_height_applied': False, 'native_transition_or_zero_pop_proved': False})
    join_path = write('Ready-Air0-Air1-Apex-Fall-Land4-Land5-Ready-author-join-diagnostic-v001.json',
                      {'schema': 'Air253-source-author-projection-join-diagnostic-v001', 'Ready_reference': ready_reference,
                       'sequence': sequence, 'joins': joins, 'footlock': False, 'physics_or_hidden_anatomy_measured': False})
    # Native source-resolution boards: arrangement and titles only; no body fit/warp.
    full = Image.new('RGBA', (1536, 1128), (45, 48, 54, 255))
    owner_board = Image.new('RGBA', full.size, (45, 48, 54, 255))
    for i in range(6):
        x, y = (i % 3)*512, (i // 3)*564
        board_paste(full, wholes[i], (x, y+48))
        board_paste(owner_board, owner_panels[i], (x, y+48))
        title = f'Air{i} {rows[i]["pose_label"]} / SWD .50 / Root {roots[i]}'
        for b in [full, owner_board]:
            ImageDraw.Draw(b).text((x+8, y+10), title, font=font(16), fill='white')
    save('presentation/Air6-full512-SWD050-candidates.png', full.convert('RGB'))
    save('presentation/Air6-five-owner-color-diagnostic.png', owner_board.convert('RGB'))
    actual_parts = Image.new('RGBA', (3072, 2770), (45, 48, 54, 255))
    draw = ImageDraw.Draw(actual_parts)
    for j, owner in enumerate(OWNERS):
        y = j*554
        for i in range(6):
            x = i*512
            board_paste(actual_parts, Image.fromarray(layer_arrays[i][owner]), (x, y+38))
            draw.text((x+8, y+9), f'Air{i} {owner}', font=font(19), fill='white')
    save('presentation/Air6-five-owner-native512-parts-board.png', actual_parts.convert('RGB'))
    fists = Image.new('RGBA', (2400, 432), (45, 48, 54, 255))
    fists_marked = fists.copy()
    fist_rois = []
    for i in range(6):
        gx, gy = rows[i]['author_binding']['Grip_xy']
        roi = [gx-50, gy-45, gx+50, gy+45]
        fist_rois.append({'frame': i, 'source_ROI_xyxy': roi, 'presentation_integer_zoom': 4, 'resampler': 'NEAREST'})
        cropped = wholes[i].crop(roi).resize((400, 360), Image.Resampling.NEAREST)
        for b in [fists, fists_marked]:
            board_paste(b, cropped, (i*400, 46))
            ImageDraw.Draw(b).text((i*400+8, 10), f'Air{i} near glove / .50 / 4x nearest', font=font(18), fill='white')
        dm = ImageDraw.Draw(fists_marked)
        center = (i*400+200, 46+180)
        unit = np.asarray(rows[i]['author_binding']['Axis_xy'], float)
        unit /= np.linalg.norm(unit)
        dm.line((center[0]-8, center[1], center[0]+8, center[1]), fill=(80, 230, 255), width=2)
        dm.line((center[0], center[1]-8, center[0], center[1]+8), fill=(80, 230, 255), width=2)
        dm.line((center[0], center[1], center[0]+unit[0]*110, center[1]+unit[1]*110), fill=(80, 230, 255), width=2)
    save('presentation/Air6-nearhand-fistcloseups-4x-nearest-unmarked.png', fists.convert('RGB'))
    save('presentation/Air6-nearhand-fistcloseups-4x-nearest-author-markers.png', fists_marked.convert('RGB'))
    join_images = [ready_whole] + wholes + [ready_whole]
    join_roots = [READY_ROOT] + roots + [READY_ROOT]
    labels = ['Ready reference', 'Air0 RiseEarly', 'Air1 RiseLate', 'Air2 Apex', 'Air3 Fall', 'Land4 impact', 'Land5 settle', 'Ready reference']
    # Both boards place the same virtual Root on a shared line. No H(t) or time interpolation.
    native_join = Image.new('RGBA', (4096, 700), (45, 48, 54, 255))
    for i, (im, root, label) in enumerate(zip(join_images, join_roots, labels)):
        native_join = Image.alpha_composite(native_join, place(im, root, native_join.size, (256+i*512, 600), 1.))
        d = ImageDraw.Draw(native_join)
        d.text((i*512+12, 12), label+f' / author Root {root}', font=font(21), fill='white')
        d.line((i*512+246, 600, i*512+266, 600), fill=(80, 200, 255), width=2)
        d.line((i*512+256, 590, i*512+256, 610), fill=(80, 200, 255), width=2)
    ImageDraw.Draw(native_join).text((12, 664), 'ALL source units 1:1, common virtual Root; no physics height, no fitted body, no timing or footlock claim.', font=font(23), fill='white')
    save('presentation/Ready-Air0-Air1-Apex-Fall-Land4-Land5-Ready-common-source-scale.png', native_join.convert('RGB'))
    display_join = Image.new('RGBA', (1280, 720), (45, 48, 54, 255))
    for i, (im, root, label) in enumerate(zip(join_images, join_roots, labels)):
        center = (80+160*i, 400)
        display_join = Image.alpha_composite(display_join, place(im, root, display_join.size, center, K))
        d = ImageDraw.Draw(display_join)
        d.text((i*160+12, 430), label, font=font(15), fill='white')
        d.line((center[0]-5, center[1], center[0]+5, center[1]), fill=(80, 200, 255), width=1)
        d.line((center[0], center[1]-5, center[0], center[1]+5), fill=(80, 200, 255), width=1)
    dd = ImageDraw.Draw(display_join)
    dd.text((24, 24), 'Offline candidate / 416 source units -> 72 display px / SWD .50 / common virtual Root', font=font(23), fill='white')
    dd.text((24, 62), 'Ready is reference only. No actual jump height, interpolation, runtime, anatomy or acceptance proof.', font=font(20), fill='white')
    dd.text((24, 660), 'Land4/5 retain fixed Root [256,464] and natural compression. Air0..3 use parent author belt+[-8,+157].', font=font(19), fill='white')
    save('presentation/Ready-Air6-Ready-common-display72-scale.png', display_join.convert('RGB'))
    write('source-copy-manifest-v001.json', {'source_before': source_pins_before, 'copies': copy_mapping})
    verification = {'schema': 'Air253-source-partition-and-rigid-SWD-host-proof-v001', 'six_frame_RGBA_reconstruction_PASS': True,
                    'six_frame_nontransparent_single_owner_PASS': True, 'overlap_pixels_all_six': [r['body_partition_proof']['overlap_pixels'] for r in rows],
                    'six_nearhand_opaque_pixels_unchanged_PASS': True, 'sword_grip_transform_error_tolerance_source_px': 1e-12,
                    'all_sword_scale': [.50]*6, 'all_sword_edge_alpha_pixels': [r['author_binding']['canvas_edge_sword_alpha_pixels'] for r in rows],
                    'source_SHA_two_pass_mismatches': [], 'source_inputs_unchanged_two_SHA_pass': True,
                    'fistcloseups': fist_rois, 'newmedia_View': False, 'native_calls': 0, 'source_pixels_warped_or_painted': False,
                    'Alpha_RGBA_checks_do_not_prove_semantic_boundaries_or_visible_hand_grip': True}
    for n in range(2):
        for p, expected in zip(source_paths, source_pins_before):
            assert pin(p) == expected, f'Source changed on verification pass {n+1}: {p}'
    check_path = write('host-verification-v001.json', verification)
    contract = write('Air253-own-five-partitions-SWD050-belt-root-candidate-v001.json',
                     {'schema': 'Air253-own-five-partitions-SWD050-author-belt-Root-candidate-v001',
                      'created_utc': dt.datetime.now(dt.timezone.utc).isoformat(), 'source_native_request': 253,
                      'old_frozen_author_polygon_proposal': pin(OLD), 'source_manifest': pin(SOURCE_MANIFEST),
                      'body_owners': OWNERS, 'exclusive_priority': PRIORITY+['BodyRest_remaining_original_RGBA'],
                      'current_SWD_stack': STACK, 'future_LGT_stack': ['BodyRest', 'ShoulderFar', 'Chest', 'NearArmWithoutHand', 'ShoulderNear', 'HelmetForeground', 'IndependentSword', 'FarHandForeground', 'NearHand'],
                      'body_scale': {'standing_basis_source_units': 416, 'display_height_px': 72, 'constant_source_to_display': K,
                                     'canvas_display_px': 512*K, 'per_frame_rescale_or_body_warp': False},
                      'independent_sword': pin(SWORD), 'weapon_scale': .50,
                      'author_Root_contract': {'Ready_author_belt': READY_BELT, 'Ready_existing_Root': READY_ROOT,
                            'belt_to_Root_offset': BELT_ROOT_OFFSET, 'six_parent_author_belt_points': BELTS,
                            'Air0to3_Root': roots[:4], 'Land4to5_Root': roots[4:],
                            'Air2_apex_virtual_Root_y530_outside_canvas_legal': True,
                            'belt_uncertainty_each_source_axis_px': 3, 'meaning': 'Explicit parent author belt projection reference. Not a measured bone, floor, contact or footlock. Land compression intentionally retained.'},
                      'frames': rows, 'Ready_reference_only': ready_reference, 'join_diagnostic': pin(join_path), 'host_verification': pin(check_path),
                      'newmedia_View': False, 'newmedia_E_retained': False, 'semantic_partition_reviewed': False,
                      'LGT_armor_fit': None, 'native_import': None, 'runtime_actual_receipts': None,
                      'actual_Source_Content_tools_E_ledger_changed': False, 'TrialAllowed': False, 'FinalAccepted': False})
    write('HANDOFF.md', '''Air253 六帧实际原RGBA按旧作者polygon排他切出五个owner；近手、远手、盔甲前景、近臂依次优先，BodyRest仅持有剩余原RGBA（含alpha0的原RGB字节）。全部非透明像素唯一owner、重叠0；五层整数RGBA总和及保存重构逐字节相同。BodyRest没有整身冒充、全帧没有局部擦除/补画/warp/fit；语义边界仍需Root在E后实际审图。

本NEW metadata采用Root明确给定的作者腰带投影参考，不覆盖旧冻结建议。Ready belt[264,307]→Root[256,464]给offset[-8,157]；Air0..3 Root分别[259,457]/[245,500]/[244,530]/[247,449]。Apex虚拟RootY530可在透明画布之外；Land4/5保持[256,464]，保留原压缩。所有七个belt点均记录中心及±3px完整7x7原RGBA；取样不等于识别骨点或证明腰带拓扑。Grip沿旧建议，方向为作者选择，原空拳没有柄轴可实测。

现有军剑原件固定.50，仅刚体旋转/平移+BICUBIC预乘采样；五身体层不重采样。叠放BodyRest/NearArmWithoutHand/HelmetForeground/IndependentSword/FarHandForeground/NearHand，近手最前。军剑持握、胸肩适配、起落接续均尚未视觉验收。Ready仅用自己的原源及原手polygon生成参考试装，不向Air复制任何Ready mask，也没有改变Ready合同或运行资源。

静态full6/30原尺寸owner板/彩色owner诊断/近手4x最近邻特写/Ready-Air6-Ready共同尺度source1:1与72px板已保存至NEW F媒体。无视频、无物理高度/插帧/时钟证据、无UE运行。所有新媒体View=false，请Root先E独立保全两SHA后审看。Source/Content/Roottools/E/ledger未写。
''')
    # Decode every generated/copy PNG without displaying; include exact decoded RGBA pins.
    decode_rows = []
    for p in sorted(OUT.rglob('*.png')):
        with Image.open(p) as im:
            im.load()
            decode_rows.append({'file': pin(p), 'mode': im.mode, 'size': list(im.size),
                                'decoded_bytes_sha256': hashlib.sha256(np.asarray(im).tobytes()).hexdigest()})
    decode = write('all-PNG-decode-without-View-v001.json', {'PNG_count': len(decode_rows), 'all_decoded': True, 'View': False, 'files': decode_rows})
    freeze_members = [pin(p) for p in sorted(OUT.rglob('*')) if p.is_file()]
    for _ in range(2):
        assert [pin(r['path']) for r in freeze_members] == freeze_members
    freeze = write('Air253-own-partition-SWD-belt-root-freeze-v001.json',
                   {'schema': 'Air253-own-partition-SWD-belt-root-freeze-v001', 'members': freeze_members,
                    'member_count': len(freeze_members), 'two_SHA_verification_passes': 2, 'mismatches': 0,
                    'source_inputs_two_SHA_unchanged': True, 'host_proof': pin(check_path), 'PNG_decode': pin(decode),
                    'newmedia_View': False, 'runtime_or_accepted': False})
    (MEDIA / '原件/五分区军剑腰带投影候选完整包').mkdir(parents=True)
    for p in sorted(OUT.rglob('*')):
        if p.is_file():
            copy_exclusive(p, MEDIA / '原件/五分区军剑腰带投影候选完整包' / p.relative_to(OUT))
    for p in sorted((OUT / 'presentation').glob('*.png')):
        copy_exclusive(p, MEDIA / '展示副本' / p.name)
    media_members = [pin(p) for p in sorted(MEDIA.rglob('*')) if p.is_file()]
    for _ in range(2):
        assert [pin(r['path']) for r in media_members] == media_members
    index = {'date': '2026-10-19', 'topic': '钟盔Air253自身五分区军剑腰带投影候选', 'version': 'v001',
             'status': 'Exact RGBA partition/rigid .50 SWD static candidate; semantic fit/join unviewed pending Root E retention.',
             'candidate': OUT.as_posix(), 'contract': pin(contract), 'freeze': pin(freeze),
             'newmedia_View': False, 'newmedia_E_retained': False, 'FinalAccepted': False,
             'two_SHA_verification_passes': 2, 'mismatches': 0, 'files': media_members}
    with (MEDIA / '来源-版本-状态索引.json').open('x', encoding='utf-8', newline='\n') as f:
        json.dump(index, f, ensure_ascii=False, indent=2)
        f.write('\n')
    print(json.dumps({'candidate': OUT.as_posix(), 'media': MEDIA.as_posix(), 'contract': pin(contract), 'freeze': pin(freeze),
                      'media_file_count': len(media_members)+1, 'media_bytes': sum(p.stat().st_size for p in MEDIA.rglob('*') if p.is_file()),
                      'belt_RGBA': [r['author_belt_reference']['center_RGBA'] for r in rows], 'Ready_belt_RGBA': ready_belt['center_RGBA'],
                      'Root': roots, 'newmedia_View': False, 'native_calls': 0}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    run()
