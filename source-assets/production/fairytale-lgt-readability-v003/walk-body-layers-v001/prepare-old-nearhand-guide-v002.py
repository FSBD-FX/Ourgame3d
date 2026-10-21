"""Extract visible old Walk near-hand pixels by new per-phase candidate ownership contours."""
from pathlib import Path
from datetime import datetime
import json,hashlib,shutil
import numpy as np
from PIL import Image,ImageDraw,ImageFont
HERE=Path(__file__).resolve().parent;OUT=HERE/'old-nearhand-guide-v002';OUT.mkdir(exist_ok=False)
ROOT=Path('F:/Ourgame');REF=ROOT/'source-assets/production/fairytale-lgt-readability-v003/ready-integer-assembly-v001/body-layers/NearHand/frame-0.png'
POLYGONS=[
 [[143,276],[149,277],[155,280],[161,283],[167,287],[174,290],[181,292],[185,294],[184,302],[176,310],[180,326],[178,345],[166,356],[149,357],[132,350],[122,337],[121,317],[129,303],[136,298],[136,283]],
 [[154,299],[160,296],[168,295],[177,296],[187,299],[196,303],[202,307],[201,320],[197,328],[204,341],[203,357],[194,370],[179,373],[161,368],[150,352],[149,335],[153,324],[152,313]],
 [[295,274],[306,277],[315,284],[320,291],[333,290],[346,297],[355,308],[356,321],[347,332],[335,339],[321,339],[307,332],[299,322],[281,317],[277,307],[276,298],[278,291],[282,284],[287,278]],
 [[302,272],[315,275],[326,281],[333,281],[345,282],[358,287],[369,296],[372,307],[367,319],[357,328],[345,337],[334,337],[322,331],[316,321],[304,321],[289,317],[289,306],[291,296],[293,287],[296,280],[298,275]],
 [[165,300],[174,297],[184,299],[194,301],[204,306],[211,312],[211,326],[204,334],[211,349],[210,364],[202,374],[186,379],[169,374],[158,363],[155,346],[158,334],[160,327],[160,314]],
 [[151,284],[160,281],[168,282],[178,285],[185,290],[192,295],[196,303],[191,313],[188,319],[192,335],[190,350],[181,360],[165,365],[148,360],[136,350],[133,336],[136,321],[143,311],[146,307],[146,294]],
]
CUFF_SEAMS=[
 [[143,276],[149,277],[155,280],[161,283],[167,287],[174,290],[181,292]],
 [[154,299],[160,296],[168,295],[177,296],[187,299],[196,303],[202,307]],
 [[295,274],[287,278],[282,284],[278,291],[276,298],[277,307],[281,317]],
 [[302,272],[298,275],[296,280],[293,287],[291,296],[289,306],[289,317]],
 [[165,300],[174,297],[184,299],[194,301],[204,306],[211,312]],
 [[151,284],[160,281],[168,282],[178,285],[185,290],[192,295]],
]
CUFF_POINTS=[[162,294],[175,310],[292,296],[308,296],[185,316],[171,299]]
PALM_POINTS=[[148,326],[176,343],[325,311],[338,306],[182,351],[159,333]]
NEAR_SIDES=['imageLEFT/back','imageLEFT/low','imageRIGHT/front','imageRIGHT/front','imageLEFT/low','imageLEFT/back']
def pin(p):
 b=p.read_bytes();return {'path':p.as_posix(),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def new(name,data):
 p=OUT/name;p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('x',encoding='utf-8',newline='\n') as f:f.write(data if isinstance(data,str) else json.dumps(data,ensure_ascii=False,indent=2)+'\n')
 return p
def save(p,a):
 p.parent.mkdir(parents=True,exist_ok=True);assert not p.exists();Image.fromarray(a).save(p);assert np.array_equal(np.asarray(Image.open(p)),a);return p
index=json.loads((HERE/'source-version-status-index-v001.json').read_text(encoding='utf-8'));font=ImageFont.load_default(size=13)
rows=[];hands=[];originals=[]
for i in range(6):
 p=HERE/'source-body'/f'frame-{i}.png';assert pin(p)==index['source_bodies'][i]
 a=np.asarray(Image.open(p)).copy();mim=Image.new('L',(512,512),0);ImageDraw.Draw(mim).polygon([tuple(q) for q in POLYGONS[i]],fill=255);mask=np.asarray(mim)>0
 hand=np.zeros_like(a);hand[mask]=a[mask];rest=a.copy();rest[mask]=0
 assert np.array_equal(hand.astype(np.uint16)+rest.astype(np.uint16),a.astype(np.uint16))
 hp=save(OUT/'old-nearhand'/f'frame-{i}.png',hand);rp=save(OUT/'old-body-minus-nearhand'/f'frame-{i}.png',rest);mp=save(OUT/'old-nearhand-mask'/f'frame-{i}.png',(mask*255).astype(np.uint8))
 # Visible samples are observations/proposals only, never bone centers or approved mounts.
 samples={}
 for role,q in [('visible_brown_cuff_candidate',CUFF_POINTS[i]),('visible_palm_candidate',PALM_POINTS[i])]:
  x,y=q;assert a[y,x,3]>=128 and mask[y,x],(i,role,q,a[y,x].tolist());samples[role]={'point':q,'actual_original_RGBA':a[y,x].tolist(),'root_confirmed':False}
 yy,xx=np.nonzero(hand[:,:,3]>0);bbox=[int(xx.min()),int(yy.min()),int(xx.max()+1),int(yy.max()+1)]
 # Numerical material check is diagnostic, never the mask algorithm or semantic pass.
 rr,gg,bb,aa=hand.astype(np.int32).transpose(2,0,1);gray=(aa>=128)&(rr>45)&(np.maximum.reduce([rr,gg,bb])-np.minimum.reduce([rr,gg,bb])<28)&(rr<1.4*gg)
 gray_count=int(gray.sum())
 bg=Image.new('RGBA',(608,608),(26,29,33,255));bg.alpha_composite(Image.fromarray(a),(48,48));overlay=Image.new('RGBA',(608,608),(0,0,0,0));draw=ImageDraw.Draw(overlay)
 for q in range(0,513,32):
  draw.line([(48+q,48),(48+q,560)],fill=(60,200,210,55),width=1);draw.line([(48,48+q),(560,48+q)],fill=(60,200,210,55),width=1)
  if q%64==0:draw.text((q+38,29),str(q),fill='white',font=font);draw.text((12,q+41),str(q),fill='white',font=font)
 draw.line([(q[0]+48,q[1]+48) for q in POLYGONS[i]+[POLYGONS[i][0]]],fill=(255,120,80,255),width=1)
 draw.line([(q[0]+48,q[1]+48) for q in CUFF_SEAMS[i]],fill=(255,230,80,255),width=2)
 for role,sm in samples.items():
  x,y=sm['point'];draw.ellipse((x+46,y+46,x+50,y+50),outline=(100,255,140,255),width=1)
 draw.text((48,7),f'OLD NEAR HAND {i}: {NEAR_SIDES[i]} | candidate contour',fill='white',font=font)
 draw.text((48,575),'Cuff seam +/-2px TRIAL; source xy = shown xy -48.',fill='white',font=font)
 gp=save(OUT/'原件'/f'old-nearhand-{i}-contour-grid-v001.png',np.asarray(Image.alpha_composite(bg,overlay)))
 originals.append(gp);hands.append(hand)
 rows.append({'frame':i,'source':pin(p),'actual_source_view_record':'Root E319 two-SHA retained; this worker viewed actual six original Body PNGs with view_image original detail after authorization.','near_hand_tracking':NEAR_SIDES[i],'selection_basis':'Track actual larger foreground shoulder-arm-cuff chain across phases; near is not a fixed image side.','new_manual_contour_polygon_candidate':POLYGONS[i],'visible_sleeve_cuff_seam_candidate':CUFF_SEAMS[i],'seam_uncertainty_source_px':2,'actual_hidden_wrist_joint':None,'actual_new_grip_A':None,'actual_new_hand_mount_B':None,'visible_samples':samples,'observed_cuff_to_palm_vector_NOT_bone_axis':[PALM_POINTS[i][0]-CUFF_POINTS[i][0],PALM_POINTS[i][1]-CUFF_POINTS[i][1]],'old_nearhand':pin(hp),'old_body_minus_nearhand':pin(rp),'old_mask':pin(mp),'visible_bbox_DIAGNOSTIC_ONLY':bbox,'nonzero_alpha_count':int((hand[:,:,3]>0).sum()),'core_alpha_ge128_count':int((hand[:,:,3]>=128).sum()),'gray_like_core_pixels_DIAGNOSTIC_NOT_SELECTOR':gray_count,'whole_source_RGBA_reconstruction_mismatch_bytes':0,'outside_mask_body_RGBA_mismatch_bytes':0,'grid':pin(gp),'semantic_contour_or_wrist_accepted':False,'new_outputs_viewed':False})
row=np.zeros((512,3072,4),dtype=np.uint8)
for i,a in enumerate(hands):row[:,512*i:512*(i+1)]=a
rowpath=save(OUT/'原件/old-nearhand-six-row-512cells-v001.png',row);originals.insert(0,rowpath)
# Direct crop montage is a technical guide only; equal 128cells, no scaling/recolor.
close=np.zeros((128,768,4),dtype=np.uint8);crop_provenance=[]
for i,(a,r) in enumerate(zip(hands,rows)):
 x0,y0,x1,y1=r['visible_bbox_DIAGNOSTIC_ONLY'];crop=a[y0:y1,x0:x1];h,w=crop.shape[:2];ox=(128-w)//2;oy=(128-h)//2;close[oy:oy+h,128*i+ox:128*i+ox+w]=crop
 crop_provenance.append({'frame':i,'source_rect_DIAGNOSTIC_ONLY':[x0,y0,x1,y1],'diagnostic_offset':[ox,oy],'resampled':False,'new_mount_or_pivot':False})
closepath=save(OUT/'原件/old-nearhand-six-tight-guide-UNSCALED-v001.png',close);originals.insert(1,closepath)
refdst=OUT/'references/Ready158-NearHand-frame-0.png';refdst.parent.mkdir(exist_ok=True);shutil.copyfile(REF,refdst);assert pin(refdst)['sha256']==pin(REF)['sha256']
for p in originals:
 dst=OUT/'展示副本'/p.name;dst.parent.mkdir(exist_ok=True);shutil.copyfile(p,dst);assert pin(dst)['sha256']==pin(p)['sha256']
measure=new('old-nearhand-visible-contours-candidate-v001.json',{'schema':'Walk6-old-open-nearhand-source-extraction-TRIAL-v001','created_local':datetime.now().astimezone().isoformat(),'actual_whole_body_source_viewed':True,'retention':'E319 prior to original Body view','frame_count':6,'near_side_by_phase':NEAR_SIDES,'frames':rows,'appearance_reference':{'actual_Ready158_NearHand_source':pin(REF),'byte_exact_copy':pin(refdst),'role':'closed-grip appearance/construction ONLY; not Walk wrist pose, source mask or fitted attachment.'},'tight_guide_crop_provenance':crop_provenance,'root_semantic_acceptance':False,'actual_wrist_bones_grip_A_or_new_mount_B':None,'new_generated_closed_fist':False,'new_outputs_viewed':False,'future_target':'After native closed-hand edit, reconstruction target must explicitly be NEW native-hand composite Body; only pixels outside old-mask UNION new-hand affected support must equal original Body. Never claim new hand Body equals original wholeBody.','source_pixel_policy':'Every selected old near-hand RGBA copied unchanged; old remainder plus old hand exactly restores original. No local closed-fist drawing, color repair, mask from P2/P3 or duplicate-pose hand.'})
new('HANDOFF-old-nearhand-v001.md','Old NearHand6 exports preserve512 coordinates and exact original RGBA; larger foreground near-arm chain is LEFT in0/1/4/5, RIGHT in2/3. Newly traced candidate contours include original brown cuff+open glove; cuff/sleeve shared ink +/-2px remains Root review. Wrist bone/new grip/mount are null. Ready158 NearHand0 source copied byte-exact as closed-grip appearance only. Original6Body unchanged. New row/tight guide/contour grids are not viewed; Root must retain before view. Native new closed hand must later define an explicit new composite Body; old hand/rest restoration proof does not prove new composite equals old body.\n')
files=[pin(p) for p in sorted(OUT.rglob('*')) if p.is_file()]
f=new('guide-freeze-v001.json',{'schema':'Walk6-old-nearhand-guide-freeze-v001','files':files,'source_body_pins':index['source_bodies'],'actual_Ready158_hand_source':pin(REF),'source_BODY_and_Ready_hand_unchanged':True,'new_closed_fist_or_native_generation_calls':0,'root_semantic_review_pending':True,'new_outputs_viewed':False})
for p0 in index['source_bodies']:assert pin(Path(p0['path']))==p0
for d in files:assert pin(Path(d['path']))==d
print(json.dumps({'row_guide':pin(rowpath),'tight_guide':pin(closepath),'Ready158_copy':pin(refdst),'contour_json':pin(measure),'freeze':pin(f),'frame_stats':[{k:r[k] for k in ['frame','near_hand_tracking','visible_bbox_DIAGNOSTIC_ONLY','nonzero_alpha_count','gray_like_core_pixels_DIAGNOSTIC_NOT_SELECTOR']} for r in rows]},ensure_ascii=False,indent=2))
