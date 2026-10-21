"""Candidate manual native158 ownership. Copy source RGBA only; no artwork edits."""
from pathlib import Path
import datetime, hashlib, json
import numpy as np
from PIL import Image, ImageDraw

R = Path(__file__).resolve().parent
DATA = R / 'measurement-candidate-v001.json'
OUT = R / 'body-partition-v001'
assert not OUT.exists(), OUT
OUT.mkdir()

def desc(p):
    b = p.read_bytes()
    return {'path': p.as_posix(), 'bytes': len(b), 'sha256': hashlib.sha256(b).hexdigest()}

def write(name, value):
    p = OUT / name
    assert not p.exists(), p
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return p

def polygon(points):
    im = Image.new('L', (512, 512), 0)
    ImageDraw.Draw(im).polygon([tuple(p) for p in points], fill=255)
    return np.asarray(im) != 0

data = json.loads(DATA.read_text(encoding='utf-8'))
names = ['BodyRest', 'NearArmWithoutHand', 'NearHand']
colors = np.array([[70, 155, 230], [215, 70, 185], [240, 190, 40]], dtype=np.uint8)
receipts = []
for f in data['frames']:
    i = f['frame']; p = Path(f['source']['path'])
    assert desc(p) == f['source']
    source_im = Image.open(p)
    assert source_im.mode == 'RGBA' and source_im.size == (512, 512)
    source = np.asarray(source_im).copy()
    hand = polygon(f['candidate_near_hand_polygon'])
    arm_union = polygon(f['candidate_near_arm_union_polygon']) | hand
    labels = np.zeros((512, 512), dtype=np.uint8)
    labels[arm_union & ~hand] = 1
    labels[hand] = 2
    owners = [labels == k for k in range(3)]
    assert np.array_equal(sum(x.astype(np.uint8) for x in owners), np.ones((512, 512), dtype=np.uint8))
    layer_arrays = []; layer_files = []; mask_files = []
    for k, name in enumerate(names):
        layer = np.zeros_like(source)
        layer[owners[k]] = source[owners[k]]
        assert np.array_equal(layer[owners[k]], source[owners[k]])
        assert not np.any(layer[~owners[k]])
        q = OUT / 'layers' / name / f'frame-{i}.png'
        q.parent.mkdir(parents=True, exist_ok=True)
        Image.fromarray(layer).save(q)
        assert np.array_equal(np.asarray(Image.open(q)), layer)
        layer_files.append({'owner': name, 'file': desc(q), 'owned_coordinates': int(owners[k].sum()),
                            'owned_visible_source_pixels': int(np.count_nonzero(owners[k] & (source[:, :, 3] > 0))),
                            'owned_partial_alpha_source_pixels': int(np.count_nonzero(owners[k] & (source[:, :, 3] > 0) & (source[:, :, 3] < 255)))})
        m = OUT / 'masks' / name / f'frame-{i}.png'
        m.parent.mkdir(parents=True, exist_ok=True)
        Image.fromarray((owners[k] * 255).astype(np.uint8)).save(m)
        mask_files.append({'owner': name, 'file': desc(m), 'binary': True})
        layer_arrays.append(layer)
    # Sum is an exact ownership reconstruction, including hidden RGB under alpha0.
    recovered = np.sum(np.stack(layer_arrays), axis=0, dtype=np.uint16).astype(np.uint8)
    assert np.array_equal(recovered, source)
    recovered_file = OUT / 'diagnostics' / f'frame-{i}-reconstructed-source.png'
    recovered_file.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(recovered).save(recovered_file)
    composite = Image.new('RGBA', (512, 512), (0, 0, 0, 0))
    for layer in layer_arrays:
        composite = Image.alpha_composite(composite, Image.fromarray(layer))
    actual = np.asarray(composite)
    def premultiplied(x):
        return np.concatenate((x[:, :, :3].astype(np.uint32) * x[:, :, 3:4], x[:, :, 3:4].astype(np.uint32) * 255), axis=2)
    assert np.array_equal(premultiplied(actual), premultiplied(source))
    label_picture = np.full((512, 512, 3), 245, dtype=np.uint8)
    visible = source[:, :, 3] > 0
    label_picture[visible] = colors[labels[visible]]
    label_path = OUT / 'diagnostics' / f'frame-{i}-ownership-colors.png'
    Image.fromarray(label_picture).save(label_path)
    # Technical overlay only: colored labels, never a production sprite.
    overlay = source.copy()
    overlay[visible, :3] = ((source[visible, :3].astype(np.uint16) * 2 + colors[labels[visible]].astype(np.uint16)) // 3).astype(np.uint8)
    overlay_path = OUT / 'diagnostics' / f'frame-{i}-ownership-overlay.png'
    Image.fromarray(overlay).save(overlay_path)
    review_band = Image.new('L', (512, 512), 0)
    dr = ImageDraw.Draw(review_band)
    for boundary in f['candidate_boundaries'].values():
        dr.line([tuple(p) for p in boundary['polyline']], fill=255,
                width=2 * boundary['uncertainty_source_px'] + 1, joint='curve')
    band_path = OUT / 'diagnostics' / f'frame-{i}-uncertainty-review-band.png'
    review_band.save(band_path)
    receipts.append({'frame': i, 'source': desc(p), 'layers': layer_files, 'masks': mask_files,
                     'reconstructed_file': desc(recovered_file), 'ownership_color_diagnostic': desc(label_path),
                     'technical_overlay': desc(overlay_path), 'uncertainty_review_band': desc(band_path),
                     'rgba_all_bytes_equal': True, 'premultiplied_composite_equal': True,
                     'multiple_owner_coordinates': 0, 'unowned_coordinates': 0,
                     'source_rgba_bytes_sha256': hashlib.sha256(source.tobytes()).hexdigest(),
                     'reconstructed_rgba_bytes_sha256': hashlib.sha256(recovered.tobytes()).hexdigest(),
                     'semantic_ownership_accepted': False, 'new_outputs_explicitly_viewed': False})

proof = {'schema': 'native158-three-owner-source-copy-proof-v1', 'created_local': datetime.datetime.now().astimezone().isoformat(),
         'measurement': desc(DATA), 'script': desc(Path(__file__).resolve()), 'frames': receipts,
         'owner_names': names, 'labels_defined_for_all_source_coordinates': True,
         'method': 'Manually traced candidate near-arm/hand polygons per actual frame; binary ownership only; source RGBA copied verbatim.',
         'semantic_masks_accepted': False, 'AA_and_ink_uncertainty': 'Visible shoulder/cuff/contact boundary candidates have2–3px uncertainty bands; exact reconstruction does not certify anatomy.',
         'new_pixels_drawn_into_body_layers': False, 'source_changed': False, 'old_mask_reused': False,
         'hidden_body_reconstructed': False, 'new_outputs_explicitly_viewed': False,
         'armor_generated': False, 'runtime_accepted': False, 'formal_complete_units': 0}
pp = write('proof-v001.json', proof)
print(json.dumps({'proof': desc(pp), 'frames': len(receipts), 'all_rgba_reconstructions_exact': True,
                  'all_premultiplied_composites_exact': True, 'semantic_masks_accepted': False,
                  'new_outputs_explicitly_viewed': False}, ensure_ascii=False))
