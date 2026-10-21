"""Six new Air poses only: unchanged v002 body + integer-only armor + rigid SWD.
No UE, game asset import, paint, body warp, per-pose scale or View.
"""
from pathlib import Path
import datetime as dt
import hashlib
import importlib.util
import json
import math

import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path('F:/Ourgame')
OUT = Path(__file__).resolve().parent
MEDIA = ROOT / '过程图稿与视频/2026-10-19_钟盔Air253九层整数棕皮甲军剑有限试装_v001'
BASE = OUT.parent / 'source-body-partition-SWD-candidate-v001/build-Air253-own-partition-SWD050-v001.py'
BODY_DIR = OUT.parent / 'source-body-partition-SWD-candidate-v002'
BODY_CONTRACT = BODY_DIR / 'Air253-own-five-partitions-SWD050-belt-root-candidate-v002.json'
BODY_FREEZE = BODY_DIR / 'Air253-own-partition-SWD-belt-root-freeze-v002.json'
ARMOR_BASE = ROOT / 'source-assets/production/fairytale-hero-state-gap-v001/air-state-preparation-v001/armor-process-runs-v001'
SWORD = ROOT / 'source-assets/production/first-unit-animation-v002/components/military-sword-clean-v001.png'
READY = ROOT / 'source-assets/production/fairytale-sword-v001/run-ready-v002/curated/frame-0.png'
STACK = ['BodyRest','ShoulderFar','Chest','NearArmWithoutHand','ShoulderNear','HelmetForeground','IndependentSword','FarHandForeground','NearHand']
OWNERS = ['BodyRest','NearArmWithoutHand','HelmetForeground','NearHand','FarHandForeground']
ROLES = {'chest':'Chest','nearshoulder':'ShoulderNear','farshoulder':'ShoulderFar'}
K = 72.0/416.0
assert hashlib.sha256(BASE.read_bytes()).hexdigest() == 'e881159ae6571c6bb0dc22e0ce35faf1921e4e0ac854ebf2fbdecf2544a8db8e'
spec = importlib.util.spec_from_file_location('air253_exact_frozen_utilities', BASE)
h = importlib.util.module_from_spec(spec)
spec.loader.exec_module(h)
h.OUT = OUT
pin, read, write, save, copy_exclusive = h.pin, h.read, h.write, h.save, h.copy_exclusive

# Source and destination are visible author points, not physical sockets/bones.
# Independently viewed source points; Apex B is right belt edge, not obscured buckle.
CHEST_SOURCE = [[[274,243],[258,279]],[[274,246],[258,280]],[[272,251],[282,287]],
                [[270,243],[261,280]],[[276,252],[262,281]],[[270,240],[260,280]]]
CHEST_BODY = [[[286,261],[264,297]],[[271,307],[252,339]],[[267,338],[275,370]],
              [[282,257],[261,293]],[[255,333],[234,368]],[[278,262],[258,301]]]
NEAR_SOURCE = [[[263,248],[238,263]] for _ in range(6)]
NEAR_BODY = list(zip([[204,223],[190,277],[187,316],[194,226],[174,296],[206,243]],
                     [[180,240],[163,291],[160,334],[169,243],[147,316],[181,265]]))
FAR_SOURCE = list(zip([[252,249],[252,250],[252,255],[252,249],[252,251],[252,249]],
                     [[260,263],[260,263],[260,264],[260,264],[260,265],[260,264]]))
FAR_BODY = list(zip([[307,257],[295,291],[291,319],[306,248],[288,338],[306,259]],
                   [[315,279],[298,315],[294,340],[314,273],[304,356],[313,282]]))
BOOT_ROIS = [[[130,350,230,464],[220,342,300,422]],[[175,396,240,464],[225,398,279,453]],
             [[179,399,241,464],[236,405,292,460]],[[200,343,294,464]],
             [[122,405,197,464],[251,403,345,464]],[[135,386,219,464],[258,382,348,464]]]


def rounded_half_away(v):
    return (np.sign(v)*np.floor(np.abs(v)+.5)).astype(int)


def translate_rgba_exact(a, offset):
    dx,dy = map(int, offset)
    sx0,sy0,sx1,sy1 = max(0,-dx),max(0,-dy),min(512,512-dx),min(512,512-dy)
    retained = np.zeros((512,512), bool)
    retained[sy0:sy1,sx0:sx1] = True
    assert not np.any(a[~retained]), 'Integer translation clips nonzero original RGBA; retain failure.'
    out = np.zeros_like(a)
    out[sy0+dy:sy1+dy,sx0+dx:sx1+dx] = a[sy0:sy1,sx0:sx1]
    assert np.array_equal(out[sy0+dy:sy1+dy,sx0+dx:sx1+dx], a[sy0:sy1,sx0:sx1])
    assert np.count_nonzero(a[:,:,3]) == np.count_nonzero(out[:,:,3])
    return out


def author_point_sample(a, xy):
    x,y = xy
    v = a[y-3:y+4,x-3:x+4]
    assert v.shape == (7,7,4)
    return {'xy':list(xy),'center_RGBA':a[y,x].tolist(),'author_uncertainty_source_px_each_axis':3,
            'actual_7x7_RGBA_rows':v.tolist(),'alpha_nonzero_samples':int(np.count_nonzero(v[:,:,3])),
            'anatomical_or_physical_socket':False}


def coverage_report(name, arrays, masks, original_body):
    a = arrays[name]
    alive = a[:,:,3]>0
    transmission = np.ones((512,512),float)
    for higher in STACK[STACK.index(name)+1:]:
        transmission *= 1-arrays[higher][:,:,3].astype(float)/255.
    contribution = a[:,:,3].astype(float)/255.*transmission
    dark = alive & (a[:,:,3]>=192) & (a[:,:,:3].max(axis=2)<=24)
    return {'source_nonzero_alpha_pixels':int(np.count_nonzero(alive)),
            'intersections_with_unchanged_body_owners':{o:int(np.count_nonzero(alive&masks[o])) for o in OWNERS},
            'pixels_outside_original_body_alpha':int(np.count_nonzero(alive & (original_body[:,:,3]==0))),
            'pixels_fully_occluded_by_higher_layers':int(np.count_nonzero(alive & (transmission==0))),
            'pixels_with_nonzero_final_contribution':int(np.count_nonzero(contribution>0)),
            'final_contribution_alpha_sum':float(contribution.sum()),
            'original_opaque_dark_pixels_preserved':int(np.count_nonzero(dark)),
            'preserved_dark_pixels_with_visible_contribution':int(np.count_nonzero(dark & (contribution>0))),
            'all_dark_pixels_mouth_or_hole_semantics':False,
            'coverage_is_numerical_not_visual_acceptance':True}


def run():
    assert CHEST_SOURCE is not None and CHEST_BODY is not None, 'Await actual-source Chest author advice.'
    assert not MEDIA.exists() and set(p.name for p in OUT.iterdir()) == {Path(__file__).name}
    assert pin(BODY_CONTRACT)['sha256'] == '11f4d4cd04cc0808c9a67ee9e58f3f070664babd576519242ac1c07d2cc0d196'
    assert pin(BODY_FREEZE)['sha256'] == '341932dcef0f88eaf7d12a38a7fffa67abbcbee5394a5f5711b08af008611a8d'
    bc, bf = read(BODY_CONTRACT), read(BODY_FREEZE)
    for _ in range(2):
        assert [pin(r['path']) for r in bf['members']] == bf['members']
    sword = Image.open(SWORD).convert('RGBA')
    src_sources = [BODY_CONTRACT,BODY_FREEZE,BASE,SWORD,READY]
    copy_exclusive(BASE,OUT/'source-copied/frozen-v001-partition-sword-utilities.py')
    copy_exclusive(BODY_CONTRACT,OUT/'source-copied/v002-body-contract.json')
    copy_exclusive(BODY_FREEZE,OUT/'source-copied/v002-body-freeze.json')
    copy_exclusive(SWORD,OUT/'source-copied/military-sword-clean-v001.png')
    copy_exclusive(READY,OUT/'source-copied/Ready158-reference-only.png')
    armor_src = {}
    for source_role,role in ROLES.items():
        armor_src[role] = []
        for i in range(6):
            p = ARMOR_BASE/source_role/f'run-shared-HD-v001/curated/frame-{i}.png'
            src_sources.append(p)
            copy_exclusive(p,OUT/f'source-copied/armor/{role}/frame-{i}.png')
            armor_src[role].append(p)
        for rel in ['manifest.json','frames/frames-manifest.json']:
            p = ARMOR_BASE/source_role/'run-shared-HD-v001'/rel
            src_sources.append(p)
            copy_exclusive(p,OUT/f'source-copied/armor/{role}'/rel)
    points = {'Chest':(CHEST_SOURCE,CHEST_BODY),'ShoulderNear':(NEAR_SOURCE,NEAR_BODY),'ShoulderFar':(FAR_SOURCE,FAR_BODY)}
    source_pins_before = [pin(p) for p in src_sources]
    rows, wholes, all_arrays = [], [], []
    sa = np.asarray(sword)
    yy,xx = np.indices((512,512))
    tip_source = ((sa[:,:,3]>0)&(xx>=450)).astype(np.uint8)*255
    for i, prior in enumerate(bc['frames']):
        original_path = Path(prior['source']['path'])
        src_sources.append(original_path)
        source_pins_before.append(pin(original_path))
        copy_exclusive(original_path,OUT/f'source-copied/Air253/frame-{i}.png')
        original = np.asarray(Image.open(original_path).convert('RGBA'))
        arrays, masks, body_pins, mask_pins = {}, {}, {}, {}
        for owner in OWNERS:
            source_layer = Path(prior['body_layers'][owner]['path'])
            source_mask = Path(prior['masks'][owner]['path'])
            for src in [source_layer,source_mask]:
                src_sources.append(src)
                source_pins_before.append(pin(src))
            lp = copy_exclusive(source_layer,OUT/f'body-layers/{owner}/frame-{i}.png')
            mp = copy_exclusive(source_mask,OUT/f'masks/{owner}/frame-{i}-mask-L.png')
            arrays[owner] = np.asarray(Image.open(lp).convert('RGBA'))
            masks[owner] = np.asarray(Image.open(mp))>0
            body_pins[owner],mask_pins[owner] = pin(lp),pin(mp)
            assert pin(lp)['sha256'] == prior['body_layers'][owner]['sha256']
        reconstructed = np.stack([arrays[o].astype(np.uint16) for o in OWNERS]).sum(axis=0)
        assert np.array_equal(reconstructed,original)
        occ = np.stack([arrays[o][:,:,3]>0 for o in OWNERS]).sum(axis=0)
        assert not np.any(occ>1) and np.array_equal(occ>0,original[:,:,3]>0)
        armor_rows = {}
        for role in ['Chest','ShoulderNear','ShoulderFar']:
            source = armor_src[role][i]
            a = np.asarray(Image.open(source).convert('RGBA'))
            sp,bp = points[role][0][i],points[role][1][i]
            source_ab,body_ab = np.asarray(sp,int),np.asarray(bp,int)
            per_point_deltas = body_ab-source_ab
            offset = rounded_half_away(per_point_deltas.mean(axis=0))
            transformed = translate_rgba_exact(a,offset)
            arrays[role] = transformed
            placed_path = save(f'armor-layers/{role}/frame-{i}.png',Image.fromarray(transformed))
            residual = source_ab+offset-body_ab
            samples = {'source':[author_point_sample(a,q) for q in sp],
                       'body':[author_point_sample(original,q) for q in bp]}
            assert all(s['center_RGBA'][3]>0 for key in samples for s in samples[key])
            armor_rows[role] = {'source':pin(source),'placed':pin(placed_path),
                'author_A_B':samples,'author_source_to_body_delta_by_point':per_point_deltas.tolist(),
                'author_point_meanings': (
                    {'A':'Visible source chest gold fastener highlight -> explicit author-selected gray-cloth chest installation point, not an existing body buckle or bone.',
                     'B':('Visible source right belt edge -> actual visible body right belt strip; Apex buckle is obscured by tucked leg, no buckle center inferred.' if i==2 else 'Visible source buckle upper-left bright edge -> actual visible body buckle upper-left edge. Body projection belt point is separate.')} if role=='Chest' else
                    {'A':'Visible upper shoulder armor patch -> author-selected visible upper sleeve installation point.',
                     'B':'Visible lower/rear armor edge -> visible sleeve/cuff or side-sleeve reference. Shape mismatch retained as author residual.'}),
                'translation_integer_xy':offset.tolist(),'translation_rule':'Two author point translation deltas mean; nearest integer, half away from zero. No rotation, scale, warp, mask or erase.',
                'transformed_source_minus_body_author_point_residual_xy':residual.tolist(),
                'author_point_residual_distances_source_px':np.linalg.norm(residual,axis=1).tolist(),
                'source_bbox':h.bbox(a[:,:,3]>0),'placed_bbox':h.bbox(transformed[:,:,3]>0),
                'source_RGBA_preserved_exact_integer_copy':True,'original_alpha_pixel_count':int(np.count_nonzero(a[:,:,3])),
                'translated_alpha_pixel_count':int(np.count_nonzero(transformed[:,:,3])),
                'all_source_dark_holes_and_antialias_preserved':True,'pixels_painted_or_erased':0,
                'author_fit_measured_socket_or_bone':False,'fit_View':False}
        axis = [1.,.2] if i==4 else prior['author_binding']['Axis_xy']
        swd,aff,angle,tp = h.rigid_sword(prior['author_binding']['Grip_xy'],axis,sword)
        arrays['IndependentSword'] = np.asarray(swd)
        sword_path = save(f'sword-layers/frame-{i}-SWD050-final-author-axis.png',swd)
        if i!=4:
            assert np.array_equal(arrays['IndependentSword'],np.asarray(Image.open(prior['author_binding']['sword_layer']['path']).convert('RGBA')))
        whole = Image.new('RGBA',(512,512))
        for layer in STACK:
            whole = Image.alpha_composite(whole,Image.fromarray(arrays[layer]))
        wa = np.asarray(whole)
        union = np.stack([arrays[n][:,:,3]>0 for n in ['Chest','ShoulderNear','ShoulderFar','IndependentSword']]).any(axis=0)
        outside = ~union & (original[:,:,3]>0)
        assert np.array_equal(wa[outside],original[outside])
        near_core = arrays['NearHand'][:,:,3]==255
        far_core = arrays['FarHandForeground'][:,:,3]==255
        assert np.array_equal(wa[near_core],original[near_core]) and np.array_equal(wa[far_core],original[far_core])
        for role in armor_rows:
            armor_rows[role]['coverage'] = coverage_report(role,arrays,masks,original)
        tip = np.asarray(Image.fromarray(tip_source).transform((512,512),Image.Transform.AFFINE,aff,resample=Image.Resampling.NEAREST))>0
        boot_mask = np.zeros((512,512),bool)
        for x0,y0,x1,y1 in BOOT_ROIS[i]:
            boot_mask[y0:y1,x0:x1] = True
        edge = arrays['IndependentSword'][:,:,3]>0
        assert not edge[0,:].any() and not edge[-1,:].any() and not edge[:,0].any() and not edge[:,-1].any()
        comp_path = save(f'composites/frame-{i}-Air253-nine-layer-candidate.png',whole)
        row = {'frame':i,'pose_label':prior['pose_label'],'source':prior['source'],
               'body_layers_v002_byte_identical':body_pins,'masks_v002_byte_identical':mask_pins,
               'body_exact_RGBA_reconstruction':True,'body_single_owner_overlap0':True,
               'Root':prior['author_Root'],'author_belt_reference':prior['author_belt_reference'],
               'armor':armor_rows,'Grip_xy':prior['author_binding']['Grip_xy'],
               'axis_final_author':axis,'angle_final_author_degrees':angle,
               'axis_v002_original_author':prior['author_binding']['Axis_xy'],
               'angle_v002_original_author_degrees':prior['author_binding']['angle_degrees'],
               'parent_author_override':({'frame':4,'reason':'E596 Root actual View rejects v00225deg Land4 tip over far boot; restore v001 direction[1,.2] for NEW finite fit only. v002 immutable.',
                                         'v002_tip_over_bootROI_pixels':155,'new_raw_Axis':[1.,.2]} if i==4 else None),
               'weapon_scale':.50,'sword_inverse_affine':list(aff),'sword_layer':pin(sword_path),
               'tip_reference_source_xy':tp([482,256]),
               'tip_region_source_x_ge450_overlap_farhand_pixels':int(np.count_nonzero(tip&masks['FarHandForeground'])),
               'tip_region_source_x_ge450_overlap_original_alpha_in_author_bootROI_pixels':int(np.count_nonzero(tip&boot_mask&(original[:,:,3]>0))),
               'tip_ROIs_are_diagnostic_not_visual_acceptance':True,
               'opaque_original_near_and_far_hand_RGBA_unchanged':True,
               'whole':pin(comp_path),'newmedia_View':False,'FinalAccepted':False}
        rows.append(row)
        wholes.append(whole)
        all_arrays.append(arrays)
    joins = []
    for i in range(5):
        a,b = rows[i],rows[i+1]
        gd = ((np.asarray(b['Grip_xy'])-b['Root']['xy'])-(np.asarray(a['Grip_xy'])-a['Root']['xy']))*K
        td = ((np.asarray(b['tip_reference_source_xy'])-b['Root']['xy'])-(np.asarray(a['tip_reference_source_xy'])-a['Root']['xy']))*K
        joins.append({'from':i,'to':i+1,'actual_final_author_angle_delta_degrees':b['angle_final_author_degrees']-a['angle_final_author_degrees'],
                      'root_relative_Grip_delta_display_px':gd.tolist(),'root_relative_tip_delta_display_px':td.tolist(),
                      'actual_physics_height_or_timing_applied':False,'native_join_accepted':False})
    font = lambda s: ImageFont.truetype('C:/Windows/Fonts/arial.ttf',s)
    full = Image.new('RGBA',(1536,1128),(45,48,54,255))
    for i,im in enumerate(wholes):
        x,y = (i%3)*512,(i//3)*564
        full.alpha_composite(im,dest=(x,y+48))
        ImageDraw.Draw(full).text((x+8,y+9),f'Air{i} nine layers / SWD .50 / {rows[i]["angle_final_author_degrees"]:.2f}deg',font=font(20),fill='white')
    save('presentation/Air6-full512-nine-layer-limited-fit.png',full.convert('RGB'))
    layers_board = Image.new('RGBA',(3072,4986),(45,48,54,255))
    for j,name in enumerate(STACK):
        for i in range(6):
            x,y=i*512,j*554
            layers_board.alpha_composite(Image.fromarray(all_arrays[i][name]),dest=(x,y+38))
            ImageDraw.Draw(layers_board).text((x+8,y+9),f'Air{i} {name}',font=font(19),fill='white')
    save('presentation/Air6-nine-native512-layers-board.png',layers_board.convert('RGB'))
    # Inspect torso and near fist without resampling source/armor: exact integer4x presentation crops only.
    for kind in ['torso','nearhand']:
        close = Image.new('RGBA',(2400,650 if kind=='torso' else 440),(45,48,54,255))
        for i,im in enumerate(wholes):
            cx,cy = rows[i]['author_belt_reference']['source_xy'] if kind=='torso' else rows[i]['Grip_xy']
            roi = (cx-50,cy-110,cx+50,cy+40) if kind=='torso' else (cx-50,cy-45,cx+50,cy+45)
            patch = im.crop(roi).resize((400,600 if kind=='torso' else 360),Image.Resampling.NEAREST)
            close.alpha_composite(patch,dest=(i*400,40))
            ImageDraw.Draw(close).text((i*400+8,9),f'Air{i} {kind} / 4x nearest',font=font(20),fill='white')
        save(f'presentation/Air6-{kind}-4x-nearest-nine-layer.png',close.convert('RGB'))
    display = Image.new('RGBA',(1280,720),(45,48,54,255))
    for i,im in enumerate(wholes):
        display = Image.alpha_composite(display,h.place(im,rows[i]['Root']['xy'],display.size,(140+i*200,430),K))
        ImageDraw.Draw(display).text((80+i*200,455),f'Air{i} {rows[i]["pose_label"]}',font=font(17),fill='white')
    d = ImageDraw.Draw(display)
    d.text((24,24),'OFFLINE Air6 nine layers / body416->72 / armor translation only / source SWD .50',font=font(23),fill='white')
    d.text((24,60),'Common virtual author Root; no actual jump height, runtime, interpolation, audio or acceptance proof.',font=font(20),fill='white')
    d.text((24,664),'Final axes: Air0..3=25deg, Land4=atan2(.2,1), Land5=current Ready axis. Body v002 unchanged.',font=font(20),fill='white')
    save('presentation/Air6-common-display72-nine-layer.png',display.convert('RGB'))
    for _ in range(2):
        assert [pin(p) for p in src_sources] == source_pins_before
    verification = write('host-integer-fit-and-source-unchanged-v001.json',
        {'six_bodies_v002_30layers_byte_identical':True,'six_RGBA_exact_reconstruction':True,'all_nontransparent_pixels_one_owner_overlap0':True,
         'armor18_source_RGBA_exact_integer_translation':True,'armor18_scale_rotation_warp_or_erasure':False,
         'armor_black_holes_and_alpha_antialias_preserved':True,'opaque_near_far_hand_source_RGBA_unchanged':True,
         'source_inputs_two_SHA_passes_unchanged':True,'source_pins':source_pins_before,
         'Axis4_only_override':True,'all_final_angle_deltas_computed_from_actual_final_axes':True,
         'newmedia_View':False,'native_calls':0,'sourcefit_accepted':False})
    contract = write('Air253-nine-layer-integer-armor-and-SWD-limited-fit-candidate-v001.json',
        {'schema':'Air253-nine-layer-integer-armor-and-SWD-limited-fit-candidate-v001','created_utc':dt.datetime.now(dt.timezone.utc).isoformat(),
         'scope':'Only new six Air poses, preparing the project49-slot candidate; does not mean all49 states or formal units complete.',
         'frozen_v002_body_contract':pin(BODY_CONTRACT),'frozen_v002_body_freeze':pin(BODY_FREEZE),
         'source_Frame253_body_and_armor_actual_View':True,'armor_source_E593_Root_confirmed_two_SHA0':True,
         'body_v002_E596_Root_accepted_for_finite_fit_only':True,'body_parts_changed_from_v002':False,
         'nine_layer_stack':STACK,'body_scale_source_to_display':K,'standing_basis':416,'display_body_height':72,
         'armor_source_scale':1,'per_frame_scaling_or_warp':False,'weapon_scale':.50,
         'author_points_are_visible_translation_designs_not_socket_or_bone_measurements':True,
         'armor_fit_residuals_do_not_authorize_rotation_scaling_or_erasure':True,
         'frames':rows,'join_diagnostics':joins,'host_verification':pin(verification),
         'newmedia_View':False,'newmedia_E_retained':False,'runtime_imported':False,'TrialAllowed':False,'FinalAccepted':False})
    write('HANDOFF.md','''NEW六相九层有限fit：只复制E596 v002五身体层，30PNG逐字节不变，仍精确重构Air253原RGBA。18甲源已实际View；各片仅源RGBA整数平移，不旋转/逐相缩放/warp/擦黑口。两对显式作者点的整数平移残差与原7x7RGBA、各owner覆盖/高层遮挡/黑像素贡献均记录；不是物理socket或fit视觉通过。

Root明确NEW覆盖仅Land4 Axis回[1,.2]（v00225°尖压远靴155px不接受），0..3继续25°，Land5既有Ready轴；v002原合同/PNG不改。所有相邻角度差从最终轴atan2实算。独立SWD仍.50刚体，NearHand最后；军剑与靴/远手交叠继续报原ROI诊断，不自动接受。静态whole、九层板、4x胸肩/近拳、共同72px尺度均待NEW F→Root E两SHA后View。本包不改变Source/Content/Roottools/E/ledger/UE，不代表49状态或正式内容单元完成。
''')
    decoded = []
    for p in sorted(OUT.rglob('*.png')):
        with Image.open(p) as im:
            im.load()
            decoded.append({'file':pin(p),'size':list(im.size),'mode':im.mode,'decoded_bytes_sha256':hashlib.sha256(np.asarray(im).tobytes()).hexdigest()})
    decode_path = write('all-PNG-decode-without-View-v001.json',{'PNG_count':len(decoded),'all_decoded':True,'View':False,'files':decoded})
    members = [pin(p) for p in sorted(OUT.rglob('*')) if p.is_file()]
    for _ in range(2):
        assert [pin(r['path']) for r in members] == members
    freeze = write('Air253-nine-layer-integer-fit-freeze-v001.json',{'schema':'Air253-nine-layer-integer-fit-freeze-v001','members':members,'member_count':len(members),
                   'verification_passes':2,'mismatches':0,'host_verification':pin(verification),'PNG_decode':pin(decode_path),'newmedia_View':False,'FinalAccepted':False})
    for p in sorted(OUT.rglob('*')):
        if p.is_file():
            copy_exclusive(p,MEDIA/'原件/六相九层整数试装候选完整包'/p.relative_to(OUT))
    for p in sorted((OUT/'presentation').glob('*.png')):
        copy_exclusive(p,MEDIA/'展示副本'/p.name)
    files = [pin(p) for p in sorted(MEDIA.rglob('*')) if p.is_file()]
    for _ in range(2):
        assert [pin(r['path']) for r in files] == files
    with (MEDIA/'来源-版本-状态索引.json').open('x',encoding='utf-8',newline='\n') as f:
        json.dump({'date':'2026-10-19','topic':'钟盔Air253九层整数棕皮甲军剑有限试装','version':'v001','status':'Static integer-only fit and byte proofs; unviewed pending Root E.',
                   'candidate':OUT.as_posix(),'contract':pin(contract),'freeze':pin(freeze),'newmedia_View':False,'newmedia_E_retained':False,
                   'FinalAccepted':False,'two_SHA_verification_passes':2,'mismatches':0,'files':files},f,ensure_ascii=False,indent=2)
        f.write('\n')
    print(json.dumps({'contract':pin(contract),'freeze':pin(freeze),'F_media':MEDIA.as_posix(),'F_files':len(files)+1,
                      'F_bytes':sum(p.stat().st_size for p in MEDIA.rglob('*') if p.is_file()),
                      'translations':[{role:r['armor'][role]['translation_integer_xy'] for role in ['Chest','ShoulderNear','ShoulderFar']} for r in rows],
                      'Land4_tip_over_bootROI':rows[4]['tip_region_source_x_ge450_overlap_original_alpha_in_author_bootROI_pixels'],
                      'Land4_to_Land5_final_angle_delta':joins[4]['actual_final_author_angle_delta_degrees'],'View':False,'native_calls':0},ensure_ascii=False,indent=2))


if __name__ == '__main__':
    run()
