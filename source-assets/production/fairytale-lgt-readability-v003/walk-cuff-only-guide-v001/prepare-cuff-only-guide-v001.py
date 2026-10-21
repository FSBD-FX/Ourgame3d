"""Conservative cuff-only motion references. No new hand artwork or image-generation."""
from pathlib import Path
from datetime import datetime
import json,hashlib,shutil
import numpy as np
from PIL import Image,ImageDraw
ROOT=Path('F:/Ourgame');HERE=Path(__file__).resolve().parent;BODY=HERE.parent/'walk-body-layers-v001/source-body';OLD=HERE.parent/'walk-body-layers-v001/old-nearhand-guide-v002'
POLYS=[
 [[144,280],[151,282],[159,286],[168,291],[177,295],[172,300],[166,303],[157,301],[148,298],[140,296]],
 [[160,301],[167,299],[176,300],[186,303],[195,308],[195,317],[186,316],[177,315],[164,317],[158,314],[158,306]],
 [[295,280],[303,282],[309,286],[302,291],[296,299],[294,306],[285,306],[281,301],[283,293],[288,285]],
 [[303,278],[313,280],[319,283],[313,291],[308,301],[307,309],[295,309],[296,300],[299,287]],
 [[169,306],[177,303],[187,305],[197,309],[205,314],[203,323],[193,320],[183,319],[173,321],[168,322],[167,315]],
 [[154,287],[161,284],[169,286],[178,289],[186,295],[190,301],[183,305],[175,303],[166,301],[157,301],[151,304],[151,295]],
]
def pin(p):
 b=p.read_bytes();return {'path':p.as_posix(),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def new(n,d):
 p=HERE/n;p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('x',encoding='utf-8',newline='\n') as f:f.write(d if isinstance(d,str) else json.dumps(d,ensure_ascii=False,indent=2)+'\n')
 return p
def save(p,a):
 p.parent.mkdir(parents=True,exist_ok=True);assert not p.exists();Image.fromarray(a).save(p);assert np.array_equal(np.asarray(Image.open(p)),a);return p
oldindex=json.loads((OLD/'old-nearhand-visible-contours-candidate-v001.json').read_text(encoding='utf-8'));sourcepins=[];rows=[];cuffs=[]
for i,poly in enumerate(POLYS):
 p=BODY/f'frame-{i}.png';sourcepin=pin(p);assert sourcepin==oldindex['frames'][i]['source'];sourcepins.append(sourcepin);a=np.asarray(Image.open(p)).copy()
 im=Image.new('L',(512,512),0);ImageDraw.Draw(im).polygon([tuple(q) for q in poly],fill=255);m=np.asarray(im)>0
 oldmask=np.asarray(Image.open(OLD/f'old-nearhand-mask/frame-{i}.png'))>0
 assert not np.any(m&~oldmask),'Cuff must stay within actual old NearHand candidate, no body or far hand pixels added'
 cuff=np.zeros_like(a);cuff[m]=a[m];cuffs.append(cuff);mp=save(HERE/f'masks/frame-{i}.png',(m*255).astype(np.uint8));cp=save(HERE/f'cuff-only/frame-{i}.png',cuff)
 yy,xx=np.nonzero(cuff[:,:,3]>0);bbox=[int(xx.min()),int(yy.min()),int(xx.max()+1),int(yy.max()+1)]
 rows.append({'frame':i,'source':sourcepin,'old_nearhand_mask':pin(OLD/f'old-nearhand-mask/frame-{i}.png'),'new_cuff_mask':pin(mp),'cuff_only':pin(cp),'new_conservative_cuff_polygon':poly,'source_visible_bbox_NOT_ANCHOR':bbox,'source_RGBA_selected_exact':True,'nonzero_alpha_pixels':int((cuff[:,:,3]>0).sum()),'core128_pixels':int((cuff[:,:,3]>=128).sum()),'near_side':['LEFT','LEFT','RIGHT','RIGHT','LEFT','LEFT'][i],'distal_edge_policy':'Conservative inset into actual cuff; remove all old palm/finger/thumb silhouette, not a complete final cuff or a new painted wrist opening.','actual_hidden_wrist_bone':None,'new_hand_A':None,'Root_confirmed_cuff_semantics':False})
row=np.zeros((512,3072,4),dtype=np.uint8);tight=np.zeros((128,768,4),dtype=np.uint8)
for i,(a,r) in enumerate(zip(cuffs,rows)):
 row[:,512*i:512*(i+1)]=a;x0,y0,x1,y1=r['source_visible_bbox_NOT_ANCHOR'];crop=a[y0:y1,x0:x1];h,w=crop.shape[:2];ox=(128-w)//2;oy=(128-h)//2;tight[oy:oy+h,128*i+ox:128*i+ox+w]=crop
 r['tight_guide_only_crop_rect']=[x0,y0,x1,y1];r['tight_guide_only_offset']=[ox,oy];r['tight_crop_is_NOT_new_mount']=True
rp=save(HERE/'原件/walk-cuff-six-native-512cells-v001.png',row);tp=save(HERE/'原件/walk-cuff-six-tight-UNSCALED-v001.png',tight)
for p in [rp,tp]:
 dst=HERE/'展示副本'/p.name;dst.parent.mkdir(exist_ok=True);shutil.copyfile(p,dst);assert pin(dst)['sha256']==pin(p)['sha256']
ready=HERE.parent/'ready-integer-assembly-v001/body-layers/NearHand/frame-0.png';ref=HERE/'references/Ready158-NearHand-frame-0.png';ref.parent.mkdir(exist_ok=True);shutil.copyfile(ready,ref);assert pin(ref)['sha256']==pin(ready)['sha256']
idx=new('cuff-source-mask-index-v001.json',{'schema':'Walk6-cuff-only-no-open-hand-motion-guide-v001','created_local':datetime.now().astimezone().isoformat(),'actual_source_view':'Only original sixBody viewed afterE319 authorization; generated guides NOT viewed until RootE332.','frames':rows,'references':{'sole_closed_grip_appearance_Ready158':pin(ref),'original_Ready158_source':pin(ready),'cuff_motion_native_cells':pin(rp),'cuff_motion_tight_UNSCALED':pin(tp)},'palm_digits_thumb_shapes_kept_in_guide':False,'selection_basis':'Conservative per-phase cuff proximal pixels from actually viewed Body0..5; distal seam is intentionally inset to exclude all palm/digit silhouettes. Not automated brown threshold or copied other clip masks.','new_outputs_viewed':False,'root_semantic_cuff_acceptance':False,'new_fist_drawn_generated_recolored_or_resampled':False,'original_body_changed':False})
new('HANDOFF.md','204 reference only: sole closed-fist appearance=Ready158NearHand0. Cuff-only sixguide follows actual old wrist/cuff directions and contains no palm/finger/thumb silhouette by conservative original-source selection. Distal margins are inset, so this is not a complete native final cuff. All selected pixels exactoriginal; sixsourceBody unchanged. 3072x512 nativecells and768x128 tightguide both no scaling. New outputs not viewed; RootE332 first then actual review. No local fist/repair/recolor/Source/UE/tools/ledger.\n')
files=[pin(p) for p in sorted(HERE.rglob('*')) if p.is_file()];freeze=new('cuff-guide-freeze-v001.json',{'schema':'Walk6-cuff-only-guide-freeze-v001','files':files,'source_body_pins':sourcepins,'new_outputs_viewed':False,'native_closed_hand_generated':False,'Root_semantic_acceptance':False})
for d in sourcepins:assert pin(Path(d['path']))==d
media=ROOT/'过程图稿与视频/2026-10-17_Walk六相仅袖口闭握引导_v001';media.mkdir(exist_ok=False);copies=[]
for p in sorted(HERE.rglob('*')):
 if not p.is_file() or '展示副本' in p.relative_to(HERE).parts:continue
 dst=media/'原件'/p.relative_to(HERE);dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,dst);assert pin(dst)['sha256']==pin(p)['sha256'];copies.append({'source':pin(p),'copy':pin(dst)})
for p in [rp,tp,ref]:
 dst=media/'展示副本'/p.name;dst.parent.mkdir(exist_ok=True);shutil.copyfile(p,dst);assert pin(dst)['sha256']==pin(p)['sha256'];copies.append({'source':pin(p),'copy':pin(dst)})
mi=media/'source-version-status-index.json';mi.write_text(json.dumps({'schema':'Walk6-cuff-only-guide-media-index-v001','files':copies,'source_copy_SHA_size_mismatches':0,'new_outputs_viewed':False,'Root_E332_retention_and_actual_review':'PENDING','scope':'Only cuff motion, no old open hand silhouette. Ready158 unique closed-grip appearance. Reference trial only.'},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(media/'README.md').write_text('204原生闭握纠正参考：六仅袖口原像素/方向，整掌指轮廓移除；远端保守内缩。Ready158闭拳为唯一外观。尚未查看新输出，先E332保全再Root看；不是最终手部/握剑或完整动作通过。\n',encoding='utf-8')
print(json.dumps({'native_row':pin(rp),'tight_guide':pin(tp),'freeze':pin(freeze),'media':media.as_posix(),'media_index':pin(mi),'source_visible_bboxes':[r['source_visible_bbox_NOT_ANCHOR'] for r in rows]},ensure_ascii=False,indent=2))
