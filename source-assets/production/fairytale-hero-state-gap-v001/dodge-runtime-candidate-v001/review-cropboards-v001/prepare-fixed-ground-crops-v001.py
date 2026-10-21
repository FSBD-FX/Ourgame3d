from pathlib import Path
import datetime
import hashlib
import json
import math
import shutil
from PIL import Image, ImageDraw, ImageFont

ROOT = Path('F:/Ourgame')
BASE = ROOT / '过程图稿与视频'
OUT = BASE / '2026-10-18_钟盔侧闪四相与接续固定窗裁切_v001'
JOINS = ['Dodge0_to_Dodge1','Dodge1_to_Dodge2','Dodge2_to_Dodge3','Dodge3_to_Ready','Ready_to_Walk']
CELL = 160

def pin(p):
    b = p.read_bytes()
    return {'path':p.as_posix(),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}

def check(ref):
    p = Path(ref['path'])
    actual = pin(p)
    assert actual['bytes'] == ref['bytes'] and actual['sha256'] == ref['sha256'], str(p)
    return p

def load(p):
    return json.loads(p.read_text(encoding='utf-8-sig'))

def copy_exact(p, q):
    q.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(p,q)
    assert pin(p)['sha256'] == pin(q)['sha256']
    return pin(q)

assert not OUT.exists(), 'Refuse to overwrite any previous F media version'
inputs = []
for side in ['left','right']:
    ip = BASE / f'2026-10-18_钟盔侧闪左右实录审阅_{side}_v002' / 'source-version-status-index.json'
    m = load(ip)
    assert m['schema'] == 'Hero-Dodge4-native-review-media-source-version-status-v002'
    assert m['native_bindings']['official_readonly_rerun_passed'] is True
    rp = check(m['native_bindings']['native_report'])
    vp = check(m['native_bindings']['independent'])
    report, verified = load(rp), load(vp)
    assert report['passed'] is True and verified['passed'] is True
    assert report['player_or_Guard_public_damage_used'] is False and report['HP_poise_clock_actor_writes'] is False
    check(verified['native_report_pin'])
    assert pin(rp)['sha256'] == verified['native_report_pin']['sha256']
    assert m['actual_side'] == (-1 if side == 'left' else 1)
    assert len(m['samples']) == 4 and [s['Dodge_draw']['frame'] for s in m['samples']] == [0,1,2,3]
    assert len(m['actual_adjacent_joins']) == 5 and [j['kind'] for j in m['actual_adjacent_joins']] == JOINS
    items = [(f'Dodge{n}',s,'phase',n,None) for n,s in enumerate(m['samples'])]
    for n,j in enumerate(m['actual_adjacent_joins']):
        assert j['to_observation'] == j['from_observation']+1 and len(j['pair']) == 2
        assert [x['observation'] for x in j['pair']] == [j['from_observation'],j['to_observation']]
        for k,s in enumerate(j['pair']):
            items.append((f'{j["kind"]}-{"from" if k == 0 else "to"}',s,'join',n,k))
    for _,s,_,_,_ in items:
        check(s['source']);check(s['copy'])
        assert s['source']['sha256'] == s['copy']['sha256']
        assert s['resized'] is False and s['pixels_edited'] is False
    inputs.append((side,ip,pin(ip),m,rp,vp,report,items))

OUT.mkdir()
font_path = Path('C:/Windows/Fonts/segoeui.ttf')
font = ImageFont.truetype(str(font_path),12) if font_path.exists() else ImageFont.load_default()
titlefont = ImageFont.truetype(str(font_path),16) if font_path.exists() else font
side_results = []
for side,ip,ipin,m,rp,vp,report,items in inputs:
    evidence = OUT / '原件' / side
    display = OUT / '展示副本' / side
    evidence.mkdir(parents=True);display.mkdir(parents=True)
    source_copies = [copy_exact(ip,evidence/'source-version-status-index.json'),
                     copy_exact(rp,evidence/'native-runtime-report.json'),
                     copy_exact(vp,evidence/'native-independent-receipt.json')]
    # Fixed framing: actual ground is always at crop pixel (80,130).
    # No pose alpha bbox, source pivot/Grip, optical fit or search is consulted.
    board = Image.new('RGBA',(736,1424),(25,28,33,255))
    draw = ImageDraw.Draw(board)
    draw.text((16,8),f'{side.upper()} | 100% native pixels | 160x160 fixed ground window',font=titlefont,fill=(242,229,203,255))
    draw.text((16,31),'4 actual Dodge phases; 5 adjacent callback joins. Labels are outside source rectangles.',font=font,fill=(200,205,214,255))
    tiles = []
    for label,s,kind,n,k in items:
        idx = s['observation'];o = report['observations'][idx]
        source = check(s['source']);media_copy = check(s['copy'])
        assert o['sim'] == s['simulation_time'] and o['animation'] == s['actual_animation']
        assert o['wall_offset_s'] == s['wall_offset_s']
        indexed = m['source_frames'][idx]
        assert indexed['observation'] == idx and indexed['native_original']['sha256'] == s['source']['sha256']
        gx,gy = o['ground'];cx,cy = o['camera_ground']
        sx,sy = 640.+(gx-cx)*.65,490.-gy*.38
        assert all(math.isfinite(x) for x in [gx,gy,cx,cy,sx,sy])
        ax,ay = math.floor(sx+.5),math.floor(sy+.5)
        box = [ax-80,ay-130,ax+80,ay+30]
        with Image.open(source) as image:
            assert image.size == (1280,720)
            assert box[0]>=0 and box[1]>=0 and box[2]<=1280 and box[3]<=720, 'No padding/clamp allowed'
            raw = image.convert('RGBA')
            crop = raw.crop(box)
        exact_copy = evidence / f'{label}-obs{idx:05d}-original1280.png'
        copy_exact(source,exact_copy)
        crop_path = display / f'{label}-obs{idx:05d}-CROP160-NATIVE100PCT.png'
        crop.save(crop_path)
        with Image.open(crop_path) as saved:
            assert saved.size==(160,160) and saved.convert('RGBA').tobytes()==crop.tobytes()
        if kind == 'phase':
            bx,by = 16+n*176,82
        else:
            bx,by = 16+k*352,318+n*218
        draw.text((bx,by-34),label,font=font,fill=(242,229,203,255))
        draw.text((bx,by-18),f'obs {idx} | {o["animation"]}',font=font,fill=(205,211,222,255))
        board.paste(crop,(bx,by))  # No alpha mask, resampling, or paint inside source pixels.
        draw.text((bx,by+165),f'groundPx ({sx:.3f},{sy:.3f})',font=font,fill=(185,195,208,255))
        draw.text((bx,by+180),f'crop [{box[0]},{box[1]},{box[2]},{box[3]})',font=font,fill=(185,195,208,255))
        tiles.append({'label':label,'kind':kind,'phase_or_join_index':n,'join_pair_side':k,
            'observation':idx,'original_native_source':s['source'],'indexed_media_full_source':s['copy'],
            'retained_full_original':pin(exact_copy),'published_ground':o['ground'],'published_camera_ground':o['camera_ground'],
            'projection_ground_screen_double':[sx,sy],'rounded_ground_pixel':[ax,ay],
            'crop_box_left_top_right_bottom_exclusive':box,'crop_dimensions':[160,160],
            'ground_pixel_in_crop':[80,130],'wall_offset_s':o['wall_offset_s'],'simulation_time':o['sim'],
            'actual_animation':o['animation'],'actual_animation_time':o['animation_time'],'callback_phase':o['phase'],
            'actual_Dodge_record':o['dodge_record'],'actual_Dodge_draw':o['dodge_draw'],
            'actual_ordinary_join_draw':o['join_draw'],'crop':pin(crop_path),
            'crop_decoded_RGBA_sha256':hashlib.sha256(crop.tobytes()).hexdigest(),
            'board_rect_left_top_right_bottom_exclusive':[bx,by,bx+160,by+160],
            'exact_crop_pixels_preserved':True,'resize_or_bbox_normalization':False})
    board_path = display / f'{side}-4phase-10join-CROP160-NATIVE100PCT-board-v001.png'
    board.save(board_path)
    with Image.open(board_path) as saved:
        for tile in tiles:
            rect=tile['board_rect_left_top_right_bottom_exclusive']
            with Image.open(tile['crop']['path']) as cell:
                assert saved.crop(rect).convert('RGBA').tobytes()==cell.convert('RGBA').tobytes()
    diagnostic_path = display / f'{side}-4phase-10join-CROP160-DIAGNOSTIC-2X-NEAREST-board-v001.png'
    board.resize((board.width*2,board.height*2),Image.Resampling.NEAREST).save(diagnostic_path)
    side_results.append({'side':side,'actual_side':m['actual_side'],'source_media_index':ipin,
        'native_report':m['native_bindings']['native_report'],'independent_receipt':m['native_bindings']['independent'],
        'native_frame_count':m['native_frame_count'],'exact_copied_source_evidence':source_copies,
        'tiles':tiles,'phase_tiles':4,'join_tiles':10,'board_native100pct':pin(board_path),
        'board_2x_nearest_diagnostic_only':pin(diagnostic_path)})
    assert pin(ip)==ipin, 'Native/media input index changed during read-only crop preparation'

readme = '''# 钟盔侧闪固定窗口裁切板 v001（未审）

每侧一张100%原像素板：上行四个实际Dodge相位，下方五组严格相邻原回调接续，每组from/to两格。另存2x nearest整板，仅为diagnostic放大，不能替代100%原像素判读。

每格固定160×160，窗口只依据原observation.ground和camera_ground：x=640+(groundX-cameraX)*.65，y=490-groundY*.38；round=floor(value+.5)，crop=[roundX-80,roundY-130,roundX+80,roundY+30)。实际ground始终落在窗内(80,130)。不按alpha bbox、逐相身体高度、Grip或shader像素搜位置；不Resize原格、不重绘、不调色、不补帧，标签全部位于矩形外。

原件保留两侧media index、native runtime report、independent receipt，以及四相和十个join格所用的全部1280×720原PNG逐字节副本。总28个原幅copy可含同源重复；每一格的原observation/ground/camera/完整源SHA/新cropSHA/board位置在source-version-status-index.json。所有crop及board源矩形均已逐RGBA核对相等。

范围仅为两侧一次正常向外Shift的有限试样。作者身体Root/Grip/Axis不等同真实骨socket、hilt接触或物理足锁；裁切定位是已发布角色地面坐标，不是测量鞋底。原件native与独立checker PASS不代替视觉验收。此新稿未View、未E保全，FinalAccepted=false。必须Root完成E双SHA保全后再View。
'''
(OUT/'README.md').write_text(readme,encoding='utf-8')
index={'schema':'Hero-Dodge4-fixed-ground-native-cropboards-v001','created_UTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),
       'status':'F_ORIGINALS_AND_DISPLAY_PREPARED_ROOT_E_BEFORE_VIEW','generator':pin(Path(__file__).resolve()),
       'projection':'x=640+(ground.x-camera_ground.x)*.65; y=490-ground.y*.38',
       'rounding':'floor(value+.5)','fixed_crop_window':[-80,-130,80,30],'source_pixel_scale':1,
       'side_results':side_results,'native_or_old_media_modified':False,'Source_Content_tools_ledger_E_modified':False,
       'new_drafts_viewed':False,'author_floor_hidden_socket_physical_footlock_measured':False,
       'FinalAccepted':False,'E_before_View_required':True}
(OUT/'source-version-status-index.json').write_text(json.dumps(index,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
allpins=[pin(q) for q in sorted(OUT.rglob('*')) if q.is_file()]
(OUT/'F-size-SHA256-v001.json').write_text(json.dumps({'schema':'Dodge-fixed-cropboards-F-file-pins-v001','files':allpins},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'output':OUT.as_posix(),'left_tiles':14,'right_tiles':14,'full_source_copies':28,
                  'file_count':len(allpins)+1,'index':pin(OUT/'source-version-status-index.json'),
                  'F_manifest':pin(OUT/'F-size-SHA256-v001.json'),'E_before_View_required':True},ensure_ascii=False))
