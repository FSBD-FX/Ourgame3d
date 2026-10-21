"""Measured shoulder-feature integer candidates and24 untouched-pixel trial textures."""
from pathlib import Path
import datetime, hashlib, json, shutil
import numpy as np
from PIL import Image

R = Path(__file__).resolve().parent
OUT = R / 'macro-registration-proposed-v001'
assert not OUT.exists(), OUT
OUT.mkdir()
MEASURE = R / 'measurement-candidate-v002.json'
M = json.loads(MEASURE.read_text(encoding='utf-8'))
SPECS = {
 'NearShoulder': {'key': 'nearshoulder', 'native': 162, 'A': [[257,261],[259,261],[258,261],[259,261]],
     'targets': [[207,248],[205,244],[205,249],[204,244]], 'feature': 'actual central round metal washer/rivet black mounting-hole center',
     'old_central_feature_requirement': 'central feature present, fit not certified',
     'measurement_basis': 'Manual inspection of the retained actual central washer ring and black hole; source ink/AA contour ambiguity approximately2px, not a whole-component bbox.'},
 'FarShoulder': {'key': 'farshoulder', 'native': 163, 'A': [[251,252],[253,252],[254,252],[254,252]],
     'targets': [[300,266],[302,270],[300,267],[298,264]], 'feature': 'NEW TopStrapRivetTrialV1: actual top leather-strap circular metal rivet center',
     'old_central_feature_requirement': 'FAILED: original central front boss absent; alternative strap-feature trial does not satisfy it',
     'measurement_basis': 'Manual visible top-strap rivet ellipse/ink boundary, excluding bright highlight. Small feature and adjoining strap ink give approximately2px ambiguity. No bbox-center substitution.'}}

def desc(p):
    b = p.read_bytes()
    return {'path': p.as_posix(), 'bytes': len(b), 'sha256': hashlib.sha256(b).hexdigest()}

def shift_rgba(a, dx, dy):
    h,w = a.shape[:2]; b = np.zeros_like(a)
    sx0,sx1 = max(0,-dx),min(w,w-dx); sy0,sy1 = max(0,-dy),min(h,h-dy)
    b[sy0+dy:sy1+dy,sx0+dx:sx1+dx] = a[sy0:sy1,sx0:sx1]
    return b

textures = []; registrations = []; by_frame = [dict() for _ in range(4)]
for component,S in SPECS.items():
    E = json.loads((R / f'{S["key"]}-extraction-v002/extraction-receipt-v001.json').read_text(encoding='utf-8'))
    for i,actual_A in enumerate(S['A']):
        f = E['frames'][i]; p = Path(f['source']['path']); assert desc(p) == f['source']
        target = S['targets'][i]
        assert M['frames'][i]['body_attachment_design_A'][component]['point'] == target
        a = np.asarray(Image.open(p)).copy(); assert a.shape == (512,512,4)
        assert a[actual_A[1],actual_A[0],3] > 0
        dx,dy = target[0]-actual_A[0],target[1]-actual_A[1]
        b = shift_rgba(a,dx,dy); ys,xs = np.where(np.any(a != 0,axis=2))
        assert np.all((xs+dx>=0)&(xs+dx<512)&(ys+dy>=0)&(ys+dy<512))
        assert np.array_equal(b[ys+dy,xs+dx],a[ys,xs])
        assert np.array_equal(shift_rgba(b,-dx,-dy),a)
        assert np.array_equal(a.sum(axis=(0,1),dtype=np.uint64),b.sum(axis=(0,1),dtype=np.uint64))
        q = OUT / f'textures/{component}/frame-{i}.png'; q.parent.mkdir(parents=True,exist_ok=True)
        Image.fromarray(b).save(q); assert np.array_equal(np.asarray(Image.open(q)),b)
        by_frame[i][component] = q
        textures.append({'component':component,'frame':i,'file':desc(q),'kind':'integer translated originalRGBA'})
        bbox = Image.fromarray(b).getchannel('A').getbbox()
        registrations.append({'component':component,'native_request':S['native'],'frame':i,'source':desc(p),
          'actual_feature_name':S['feature'],'actual_component_A_candidate':actual_A,'uncertainty_source_px':2,
          'measurement_basis':S['measurement_basis'],'original_central_A_contract_status':S['old_central_feature_requirement'],
          'original_central_A_contract_passed':False if component=='FarShoulder' else None,
          'actual_rgba_at_selected_A':a[actual_A[1],actual_A[0]].tolist(),
          'body_design_target_A_unchanged':target,'body_target_uncertainty_source_px':5 if component=='FarShoulder' else 3,
          'body_target_is_bone_fact':False,'integer_translation':[dx,dy],
          'registered':desc(q),'registered_alpha_bbox_px':list(bbox),'source_shared_ratio_unchanged':E['shared_row_ratio'],
          'inverse_integer_translation_RGBA_exact':True,'clipped_nonzero_RGBA_coordinates':0,
          'rescaled_rotated_warped_recolored':False,'selected_A_maps_to_target_exactly_not_fit_proof':True,
          'new_registered_explicitly_viewed':False})

# Preserve previous Chest construction and actual source-owned body pixels byte-for-byte.
for i in range(4):
    for component in ['Chest','BodyRest','NearArmWithoutHand','NearHand']:
        source = R / f'chest-registration-proposed-v001/registered/frame-{i}.png' if component=='Chest' else R / f'body-partition-v002/layers/{component}/frame-{i}.png'
        q = OUT / f'textures/{component}/frame-{i}.png'; q.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(source,q); assert source.read_bytes()==q.read_bytes()
        by_frame[i][component] = q
        textures.append({'component':component,'frame':i,'file':desc(q),'source':desc(source),'kind':'exact original/candidate file copy; no transform'})
assert len(textures)==24 and len({(x['component'],x['frame']) for x in textures})==24

STATIC_ORDER = ['BodyRest','FarShoulder','Chest','NearArmWithoutHand','NearShoulder','NearHand']
FUTURE_ORDER = ['BodyRest','FarShoulder','Chest','NearArmWithoutHand','NearShoulder','Sword','NearHand']
def compose(i,omit=None):
    result = Image.new('RGBA',(512,512),(0,0,0,0))
    for c in STATIC_ORDER:
        if c != omit: result = Image.alpha_composite(result,Image.open(by_frame[i][c]))
    return result

assemblies = []; contact = Image.new('RGBA',(2048,512),(0,0,0,0))
for i in range(4):
    body = np.zeros((512,512,4),dtype=np.uint16)
    for c in ['BodyRest','NearArmWithoutHand','NearHand']: body += np.asarray(Image.open(by_frame[i][c]),dtype=np.uint16)
    source_body = Path(M['frames'][i]['source']['path'])
    assert np.array_equal(body,np.asarray(Image.open(source_body),dtype=np.uint16))
    im = compose(i); a = np.asarray(im)
    p = OUT / f'assemblies/frame-{i}-macro-no-sword.png'; p.parent.mkdir(parents=True,exist_ok=True); im.save(p)
    contact.paste(im,(i*512,0))
    contribution = {}
    for c in ['Chest','NearShoulder','FarShoulder']:
        other = np.asarray(compose(i,c))
        contribution[c] = int(np.count_nonzero(np.any(a!=other,axis=2)))
    assemblies.append({'frame':i,'source_body':desc(source_body),'body_three_layers_RGBA_exact_reconstruction':True,
        'stack':[{'layer':c,'file':desc(by_frame[i][c])} for c in STATIC_ORDER],
        'static_assembly':desc(p),'actual_static_visible_difference_pixel_counts_vs_omit_one':contribution,
        'contribution_counts_are_not_readability_or_runtime_acceptance':True,'sword_present':False,
        'new_assembly_explicitly_viewed':False})
contact_path = OUT / 'assemblies/macro-no-sword-four-contact.png'; contact.save(contact_path)
data = {'schema':'native158-ready-macro24-static-trial-candidate-v1','created_local':datetime.datetime.now().astimezone().isoformat(),
    'author':'scale_tests','source_views_after_retention':'E160: all8 shoulder curated and all8 unscaled-alpha crops; all4 previous chest-only assemblies',
    'source_body_measurement':desc(MEASURE),'previous_chest_registration':desc(R/'chest-registration-proposed-v001/measurement-and-registration-v001.json'),
    'script':desc(Path(__file__).resolve()),'textures':textures,'texture_count':24,'armor_texture_count':12,'body_texture_count':12,
    'shoulder_registration_candidates':registrations,'frames':assemblies,'static_contact':desc(contact_path),
    'source_canvas_px':[512,512],'native_facing':1,'display_root_px':[256,464],
    'display_root_is_exact_foot_center':False,'max_body_height_screen_px':72,'fixed_display_canvas':72*512/416,
    'durations_ms':[167]*4,'static_layer_order_no_sword':STATIC_ORDER,'future_runtime_layer_order':FUTURE_ORDER,
    'future_Sword_slot':{'included_in_static':False,'after':'NearShoulder','before':'NearHand','asset':None,
        'require_actual158_grip_markers_from_root':True,'not_155_or157_marker_fallback':True,'weapon_occlusion_accepted':False},
    'body_target_adjusted':False,'source_curated_or_original_partition_changed':False,
    'new_outputs_explicitly_viewed':False,'semantic_body_partition_accepted':False,
    'helmet_neck_hand_waist_fit_accepted':False,'four_armor_equipment_accepted':False,
    'runtime_or_motion_accepted':False,'native_called':False,'ue_or_import_called':False,'formal_complete_units':0}
rp = OUT / 'macro-measurement-registration-v001.json'; rp.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
notes = OUT / 'trial-boundaries-v001.md'
notes.write_text('''# 实际肩特征＋24原像素候选

E160后实际view近/远各4curated＋各4原像素bbox crop和胸only四组合。胸only未见明显大块压盔/手/腰，但这是512静态观察，不是72px运行或语义零覆盖。近肩central washer/黑圆孔center候选257261/259261/258261/259261；远肩NEW TopStrapRivetTrialV1候选251252/253252/254252/254252，人工墨线/小椭圆AA误差±2px。远肩原prompt中央boss不存在，保持未满足，topstrap是明确新试装feature，不改旧prompt或把它叫中央boss，不取全甲bbox/亮点中心。

首轮body衣面设计target保持，Near207248/205244/205249/204244（±3），Far300266/302270/300267/298264（±5），非骨/实际body rivet事实；仅整数平移，无perframe scale/rotate/warp。Near顶部strap在盔下邻近区，原点精确映射不代表零穿插，必须新E保全后实际审全stack；当前不暗改target。如需移动必须保本版并明确新target trial。

输出24个512RGBA：Chest4为此前整数registered文件逐字节copy，Near4/Far4为原curated整数平移，另BodyRest/NearArmWithoutHand/NearHand各4为source ownership候选逐字节copy。三body层在无甲时全RGBA exact复原原158；各新甲逆平移全RGBA exact，所有非零RGBA/AA无裁切。精确只指源像素/构造保真，分层语义仍候选。

静态无剑层序BodyRest→FarShoulder→Chest→NearArmWithoutHand→NearShoulder→NearHand；各甲与omit-one比较的实际差异像素数只证明此候选static stack有可见贡献，不证明好看、attach正确或UE真的画出。future Sword在NearShoulder之后/NearHand之前，需root绑定158实际新grip数据；本输出没有剑，不借155/157回退或宣称武器遮挡已验。新组合未显式view，等保全。72px/整装一次mirror/四pose同167ms/旧原件均保持；无Source/UE/import/ledger/native写入，完整内容0/15。
''',encoding='utf-8')
files = sorted([p for p in OUT.rglob('*') if p.is_file()]+[Path(__file__).resolve()])
fp = OUT/'registered-freeze-v001.json'; fp.write_text(json.dumps({'schema':'ready-macro24-static-trial-freeze-v1',
    'file_count':len(files),'total_bytes':sum(p.stat().st_size for p in files),'files':[desc(p) for p in files],
    'texture_count':24,'new_outputs_explicitly_viewed':False,'accepted':False,'import_permitted':False},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'freeze':desc(fp),'manifest':desc(rp),'files':len(files),'bytes':sum(p.stat().st_size for p in files),
    'textures':24,'visible_counts':[f['actual_static_visible_difference_pixel_counts_vs_omit_one'] for f in assemblies]},ensure_ascii=False))
