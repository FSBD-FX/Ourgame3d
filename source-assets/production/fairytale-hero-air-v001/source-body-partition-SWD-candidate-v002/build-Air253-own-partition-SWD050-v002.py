"""NEW v002 author-boundary/axis derivative; preserves frozen v001.

Reuses the exact frozen v001 integer RGBA partition and rigid-sword pipeline.
Changes only six artist helmet polygons and five artist sword axes.
No View, UE, per-pose scale, alpha dilation, paint or body warp.
"""
from pathlib import Path
import hashlib
import importlib.util
import json
import math

HERE = Path(__file__).resolve().parent
BASE = HERE.parent / 'source-body-partition-SWD-candidate-v001/build-Air253-own-partition-SWD050-v001.py'
BASE_SHA = 'e881159ae6571c6bb0dc22e0ce35faf1921e4e0ac854ebf2fbdecf2544a8db8e'
V001_FREEZE = BASE.parent / 'Air253-own-partition-SWD-belt-root-freeze-v001.json'
assert hashlib.sha256(BASE.read_bytes()).hexdigest() == BASE_SHA
assert hashlib.sha256(V001_FREEZE.read_bytes()).hexdigest() == 'e2c63f2a26c0f819569ca2758690860f3b2d9d81afbcd776971b2d4b931ff9f1'
spec = importlib.util.spec_from_file_location('air253_frozen_v001_pipeline', BASE)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
m.OUT = HERE
m.MEDIA = m.ROOT / '过程图稿与视频/2026-10-19_钟盔Air253整盔边界军剑25度复核候选_v002'
m.__file__ = __file__
original_read, original_write = m.read, m.write

# Hand-authored upper silhouette envelopes: blank source area above helmet is harmless.
# Lower chains follow the original warm helmet/black edge before the gray cloth begins.
# No mask dilation, RGB segmentation, local erase, new surface or body transform.
LOWER_LEFT_TO_RIGHT = [
    [[140,197],[200,197],[220,205],[240,214],[260,220],[280,229],[300,237],[320,246],[340,253],[360,255],[374,254],[385,249],[420,249]],
    [[140,249],[178,249],[200,258],[220,264],[240,267],[260,273],[280,278],[300,283],[320,287],[340,287],[355,282],[380,282]],
    [[140,292],[171,292],[180,296],[200,303],[220,306],[240,307],[260,311],[280,314],[300,318],[320,319],[340,318],[356,313],[390,313]],
    [[140,201],[190,201],[210,209],[220,213],[240,219],[250,222],[270,230],[280,234],[300,240],[310,244],[330,248],[340,249],[360,247],[375,240],[410,240]],
    [[140,279],[172,279],[180,284],[200,294],[220,303],[240,311],[260,320],[280,327],[300,334],[320,339],[340,340],[357,335],[375,330],[410,330]],
    [[140,201],[177,201],[200,210],[220,215],[240,219],[260,224],[280,230],[300,235],[320,238],[340,238],[356,233],[375,228],[410,228]],
]
POLYGONS = [[[chain[0][0], 0], [chain[-1][0], 0]] + list(reversed(chain)) for chain in LOWER_LEFT_TO_RIGHT]
AXIS25 = [math.cos(math.radians(25)), math.sin(math.radians(25))]
author_path = None


def derivative_read(path):
    global author_path
    result = original_read(path)
    if Path(path).resolve() == m.OLD.resolve():
        old_result = json.loads(json.dumps(result))
        changes = []
        for i, row in enumerate(result['frames']):
            old_poly = row['artist_visible_polygon_by_owner']['HelmetForeground']
            old_axis = row['axis_artist_directed']
            row['artist_visible_polygon_by_owner']['HelmetForeground'] = POLYGONS[i]
            if i < 5:
                row['axis_artist_directed'] = AXIS25.copy()
            changes.append({'frame': i, 'old_HelmetForeground_polygon': old_poly,
                            'new_HelmetForeground_polygon': POLYGONS[i],
                            'old_Axis': old_axis, 'new_Axis': row['axis_artist_directed'],
                            'source_RGBA_or_Grip_or_Root_or_scale_changed': False,
                            'author_lower_edge_uncertainty_source_px': 2,
                            'new_polygon_actual_partition_View': False})
        # Called only after inherited run() exclusive-output assertions pass.
        author_path = original_write('Air253-v002-parent-requested-helmet-Axis-author-overrides.json',
                         {'schema': 'Air253-v002-parent-requested-helmet-Axis-author-overrides',
                          'frozen_base_script': m.pin(BASE), 'frozen_v001': m.pin(V001_FREEZE),
                          'original_proposal': m.pin(m.OLD), 'changes': changes,
                          'source_author_View_basis': 'Original source six plus E592-retained v001 owner board. This v002 output remains unviewed.',
                          'lower_edge_basis': 'Manual source View and explicit original RGBA column samples; warm helmet/black edge before gray cloth. Not automated color segmentation.',
                          'independent_original_column_advice_applied': [
                              {'frame':0,'vertex':[260,220],'original_RGBA':[4,2,1,255],'avoided_gray_vertex':[260,222],'avoided_original_RGBA':[78,61,70,255]},
                              {'frame':5,'vertex':[260,224],'original_RGBA':[0,0,0,255],'avoided_gray_vertex':[260,225],'avoided_original_RGBA':[52,43,44,255]}],
                          'axis0to4_directed_author_degrees': 25, 'axis5_Ready_unchanged': True,
                          'alpha_dilation': False, 'local_RGBA_changes': False,
                          'remaining_risk': 'Exact reconstruction cannot prove the semantic helmet/gray-cloth boundary or natural sword tip clearance; Root E/View still required.',
                          'FinalAccepted': False})
        m.copy_exclusive(BASE, HERE / 'source-copied/frozen-v001-builder.py')
        assert old_result['frames'][0]['artist_visible_polygon_by_owner']['HelmetForeground'] != POLYGONS[0]
    return result


def derivative_write(rel, value):
    # Only new output filenames/schemas change; original input pins remain byte-exact.
    output_rel = rel.replace('-v001.json', '-v002.json')
    if isinstance(value, dict):
        if 'schema' in value and value['schema'].endswith('-v001'):
            value['schema'] = value['schema'][:-5] + '-v002'
        if rel == 'Air253-own-five-partitions-SWD050-belt-root-candidate-v001.json':
            value['v002_author_overrides'] = m.pin(author_path)
            value['v002_frozen_v001_lineage'] = m.pin(V001_FREEZE)
            value['source_polygon_semantics'] = 'NEW manual whole-helmet upper envelopes replace only HelmetForeground; lower edge still a candidate. No alpha dilation or gray-cloth fill.'
            value['sword_axis_semantics'] = 'Air0..4 parent author direction25deg forward/down, Air5 existing Ready axis; .50 rigid source sword. Tip/far-hand/boots clearance remains unviewed.'
            old_contract = original_read(BASE.parent / 'Air253-own-five-partitions-SWD050-belt-root-candidate-v001.json')
            sword_a = m.np.asarray(m.Image.open(m.SWORD).convert('RGBA'))
            yy, xx = m.np.indices((512, 512))
            tip_source = ((sword_a[:, :, 3] > 0) & (xx >= 450)).astype(m.np.uint8)*255
            boot_rois = [
                [[130,350,230,464],[220,342,300,422]],
                [[175,396,240,464],[225,398,279,453]],
                [[179,399,241,464],[236,405,292,460]],
                [[200,343,294,464]],
                [[122,405,197,464],[251,403,345,464]],
                [[135,386,219,464],[258,382,348,464]],
            ]
            diagnostics = []
            for i, row in enumerate(value['frames']):
                moved = {}
                for owner in m.OWNERS:
                    before = m.np.asarray(m.Image.open(old_contract['frames'][i]['body_layers'][owner]['path']).convert('RGBA'))
                    after = m.np.asarray(m.Image.open(row['body_layers'][owner]['path']).convert('RGBA'))
                    moved[owner] = int(m.np.count_nonzero(m.np.any(before != after, axis=2)))
                tip = m.np.asarray(m.Image.fromarray(tip_source).transform((512,512), m.Image.Transform.AFFINE,
                              row['author_binding']['inverse_affine'], resample=m.Image.Resampling.NEAREST)) > 0
                far = m.np.asarray(m.Image.open(row['masks']['FarHandForeground']['path'])) > 0
                body = m.np.asarray(m.Image.open(row['source']['path']).convert('RGBA'))
                boot_roi_mask = m.np.zeros((512,512), bool)
                for x0,y0,x1,y1 in boot_rois[i]:
                    boot_roi_mask[y0:y1,x0:x1] = True
                tx,ty = row['author_binding']['tip_reference_source_xy']
                diagnostics.append({'frame':i,'v001_to_v002_changed_owner_RGBA_pixels':moved,
                    'tip_source_region': 'original sword alpha>0 and source x>=450; nearest rigid .50 projection',
                    'tip_pixels_over_actual_farhand_owner': int(m.np.count_nonzero(tip & far)),
                    'artist_visible_boot_ROIs_xyxy':boot_rois[i],
                    'tip_pixels_over_original_alpha_inside_artist_boot_ROI':int(m.np.count_nonzero(tip & boot_roi_mask & (body[:,:,3]>0))),
                    'tip_reference_source_xy':[tx,ty],
                    'rounded_tip_sample_original_RGBA':body[round(ty),round(tx)].tolist(),
                    'boot_ROIs_are_visible_author_regions_not_semantic_boot_segmentation':True,
                    'pixel_overlap_diagnostic_not_accepted_visual_clearance':True})
            dp = original_write('v002-helmet-owner-delta-and-sword-tip-clearance-diagnostic.json',
                           {'schema':'Air253-v002-owner-delta-and-tip-diagnostic', 'old_v001_contract':m.pin(BASE.parent / 'Air253-own-five-partitions-SWD050-belt-root-candidate-v001.json'),
                            'frames':diagnostics,'newmedia_View':False,'FinalAccepted':False})
            value['v002_helmet_and_tip_diagnostic'] = m.pin(dp)
        if rel == 'Air253-own-partition-SWD-belt-root-freeze-v001.json':
            value['frozen_v001_lineage'] = m.pin(V001_FREEZE)
            value['derivative_changes_only'] = 'Six manual HelmetForeground polygon envelopes and Air0..4 author sword axis25deg; inherited integer RGBA/sword pipeline frozen.'
    elif rel == 'HANDOFF.md':
        value = ('NEW v002：只替换六相HelmetForeground作者polygon（包含整块帽檐/旋钮外沿、按原下沿排除灰衣肩），并将Air0..4作者持剑轴统一25°前下，Air5保持Ready方向。旧v001不动。没有alpha dilation、身体重生成、局部擦除或变形。整盔边界和剑尖/远拳/靴足距离仍待Root E后视觉复核。\n\n' + value)
    return original_write(output_rel, value)


m.read = derivative_read
m.write = derivative_write
original_json_dump = json.dump


def derivative_index_dump(value, stream, *args, **kwargs):
    if Path(stream.name).resolve() == (m.MEDIA / '来源-版本-状态索引.json').resolve():
        value['topic'] = '钟盔Air253整盔边界军剑25度复核候选'
        value['version'] = 'v002'
        value['status'] = 'NEW manual helmet polygon and author SWD25deg derivative; exact RGBA/rigid .50 host proof only, unviewed pending Root E retention.'
        value['frozen_v001_lineage'] = m.pin(V001_FREEZE)
    return original_json_dump(value, stream, *args, **kwargs)


json.dump = derivative_index_dump
if __name__ == '__main__':
    m.run()
