"""Deterministic diagnostic display of retained whole RGBA. Never edits source art.
New media must be retained by Root on E before anyone Views these outputs.
"""
from pathlib import Path
import hashlib,json,shutil
import numpy as np
from PIL import Image,ImageDraw,ImageFont
R=Path('F:/Ourgame');A=R/'source-assets/production/fairytale-guard-v001/art-preparation-v001';O=Path(__file__).resolve().parent
F=R/'过程图稿与视频/2026-10-18_裂岩守卫跺击原像素统一尺度配准对照_v001'
REGS=[A/'move221-rejection-stomp222-far-foot-review-v001/Stomp222-FAR-lift-NEAR-support-body-root-registration-v001.json',A/'stomp224-active2-registration-and-join-risk-v001/Stomp224-one-row-NEAR-support-registration-and-WU-A-join-risk-v001.json',A/'stomp225-recovery4-registration-and-join-risk-v001/Stomp225-one-row-NEAR-support-registration-and-A-Rec-Ready-join-risks-v001.json']
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def pin(p):
 b=p.read_bytes();return dict(path=p.as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def foot(a,old):
 rect=old.get('artist_visible_ROI_xyxy',old.get('artist_visible_shoe_ROI_xyxy'));x0,y0,x1,y1=rect
 ys,xs=np.where(a[y0:y1,x0:x1,3]>=128);by=int(ys.max()+y0)
 band=a[by-3:by+1,x0:x1,3].astype(float);cx=float((band*np.arange(x0,x1)[None,:]).sum()/band.sum())
 assert by==old['core_bottom_y'] and abs(cx-old['bottom_band_alpha_centroid_x'])<1e-8
 return dict(artist_ROI=rect,actual_core_bottom_y=by,actual_bottom4_alpha_centroid_x=cx)
def eye(a,roi):
 x0,y0,x1,y1=roi;q=a[y0:y1,x0:x1].astype(np.int32);r,g,b,al=q[:,:,0],q[:,:,1],q[:,:,2],q[:,:,3]
 ok=(r>220)&(g>110)&(g<250)&(b<60)&(r-b>140)&(g-b>70)&(al>=128);ys,xs=np.where(ok);assert len(xs)>0
 return dict(artist_ROI=roi,amber_pixels=int(len(xs)),centroid_xy=[float(xs.mean()+x0),float(ys.mean()+y0)],bbox_xyxy=[int(xs.min()+x0),int(ys.min()+y0),int(xs.max()+x0+1),int(ys.max()+y0+1)],authority='Visible amber pixels inside authored ROI; no hidden joint/bone')
inv=read(O/'retained-source-inventory-v001.json');frames=[]
old_scales=[100.8/388,100.8/385,100.8/401]
common=100.8/388
for group,(regpath,item) in enumerate(zip(REGS,inv['rows'])):
 reg=read(regpath)
 for rr,ff in zip(reg['rows'],item['frames']):
  p=Path(ff['source']['path']);assert pin(p)==ff['source'];im=Image.open(p).convert('RGBA');a=np.array(im);assert hashlib.sha256(im.tobytes()).hexdigest()==ff['RGBA_sha256']
  feet=rr.get('feet_diagnostics',rr.get('feet'));near=foot(a,feet[0]);far=foot(a,feet[1]);e=eye(a,[200,80,350,250] if group<2 else [200,80,370,300])
  floor=near['actual_core_bottom_y']+1
  root=rr.get('artist_support_delta_propagated_ground_pivot_xy',rr.get('artist_NEAR_support_locked_WU_offset_groundpivot_xy',rr.get('artist_NEAR_support_propagated_ground_pivot_xy')))
  assert root[1]==floor
  frames.append(dict(label=('WU222','A224','R225')[group]+'.'+str(rr['frame']),source=ff['source'],RGBA_sha256=ff['RGBA_sha256'],image=im,near=near,far=far,eye=e,old_density=old_scales[group],old_root=root,common_density=common,common_support_root=root,body_root=None,TrialAllowed=False))
ready=A/'armed-ready4-extraction-v001/run-ready209-shared-HD-v001/curated/frame-0.png';rim=Image.open(ready).convert('RGBA');ra=np.array(rim);re=eye(ra,[200,80,370,300]);ready_density=100.8/415;ready_root=[235,464]
ready_fact=pin(ready);assert ready_fact['sha256']=='54df5fe718a98e1568513193dbde479aff6fd393d623755feb77813cacb4e804'
eroot=Path('E:/OurGame/Knight/过程图稿与视频/2026-10-18-OurgameUE-guard209-curated-v363');em=read(eroot/'source-size-SHA256.json');assert em['verification_passes']==2 and em['source_and_target_hash_mismatches']==0
ef=next(x for x in em['files'] if x['bytes']==ready_fact['bytes'] and x['sha256']==ready_fact['sha256']);assert (eroot/Path(ef['retained_relative'])).read_bytes()==ready.read_bytes()
rb=ra[460:464,81:211,3].astype(float);ready_near_x=float((rb*np.arange(81,211)[None,:]).sum()/rb.sum())
# This third control is explicit authored whole-body display placement, not a
# measured actor joint or an attempt to claim planted support. It preserves the
# already admitted WU roots, eye-aligned A onset, and a visible recovery drift
# toward the existing Ready eye projection. Foot relocation remains measurable.
wu5=frames[5];start_x=(wu5['eye']['centroid_xy'][0]-wu5['old_root'][0])*common
ready_x=(re['centroid_xy'][0]-ready_root[0])*ready_density
for i,f in enumerate(frames):
 if i<6:f['body_root']=f['old_root'][:];continue
 target=start_x if i<8 else start_x+(ready_x-start_x)*(i-8)/3
 f['body_root']=[round(f['eye']['centroid_xy'][0]-target/common),f['old_root'][1]]
 f['author_eye_projection_target_display_x']=target

def point(f,mode,xy):
 d=f['old_density'] if mode==0 else common;root=f['body_root'] if mode==2 else f['old_root'];return [(xy[0]-root[0])*d,(xy[1]-root[1])*d]
def diag(f,mode):
 return dict(label=f['label'],density=f['old_density'] if mode==0 else common,authorRoot=f['body_root'] if mode==2 else f['old_root'],eye_from_root=point(f,mode,f['eye']['centroid_xy']),near_from_root=point(f,mode,[f['near']['actual_bottom4_alpha_centroid_x'],f['near']['actual_core_bottom_y']+1]),far_visible_from_root=point(f,mode,[f['far']['actual_bottom4_alpha_centroid_x'],f['far']['actual_core_bottom_y']+1]))
joins=[]
for mode in range(3):
 rows=[diag(f,mode) for f in frames];b=[]
 for left,right in [(5,6),(7,8)]:
  b.append(dict(join=frames[left]['label']+' -> '+frames[right]['label'],eye_delta=[rows[right]['eye_from_root'][k]-rows[left]['eye_from_root'][k] for k in range(2)],near_delta=[rows[right]['near_from_root'][k]-rows[left]['near_from_root'][k] for k in range(2)]))
 b.append(dict(join='R225.3 -> Ready209.0',eye_delta=[ready_x-rows[-1]['eye_from_root'][0],(re['centroid_xy'][1]-ready_root[1])*ready_density-rows[-1]['eye_from_root'][1]]))
 joins.append(dict(mode=mode,frames=rows,joins=b))
v_wu=common*(wu5['eye']['centroid_xy'][0]-wu5['near']['actual_bottom4_alpha_centroid_x']);v_a=common*(frames[6]['eye']['centroid_xy'][0]-frames[6]['near']['actual_bottom4_alpha_centroid_x'])
metadata=dict(schema='Guard-Stomp-retained-RGBA-uniform-display-authorRoot-controls-v001',input_inventory=pin(O/'retained-source-inventory-v001.json'),registration_inputs=[pin(p) for p in REGS],actual_old12_View_after_E=True,source_art_modified=False,control0='Prior independent row densities + prior NEAR-support roots',control1='ONE common100.8/388 display density + prior NEAR-support roots',control2='ONE common100.8/388 density + explicit visible-eye authored body root; NEAR shoe relocation disclosed, not planted support or a measured bone',ONE_common_canvas_display_side=512*common,ONE_common_density=common,uniform_XY_scale=True,perframe_height_normalization=False,control2_TrialAllowed=False,Root_authorization_or_native_acceptance=False,physical_density_limit='Same display density is a finite comparison, not proof the independently generated source rows have identical head/body/axe physical proportions.',translation_invariant_counterexample=dict(WU5_near_to_eye_display_x=v_wu,A0_near_to_eye_display_x=v_a,intrinsic_difference=v_a-v_wu,minimum_worst_horizontal_residual_if_both_features_are_required=abs(v_a-v_wu)/2,statement='One whole RGBA translation moves both landmarks equally; it cannot zero both mismatches at one fixed density.'),all_controls=joins,kernel_phase_ms=[900,150,1500],kernel_frame_durations_ms=[[150]*6,[75]*2,[375]*4],proof_limits=['ExistingRoot source acceptance is not runtime motion acceptance.','Control2 is not a successful planted-support correction and must not be admitted without Root visual decision/explicit semantics.','Original Active prompt says NEAR support remains planted; moving that shoe does not pass that original cross-phase intent.','No actor transform, gameplay deadline or source pixels changed.','No Source/Content/Roottools/ledger/UE/imagegen/E modified.','New diagnostic media NOT Viewed before Root E.'],FinalAccepted=False)
public_frames=[]
for f in frames:public_frames.append({k:v for k,v in f.items() if k!='image'})
metadata['source_frames']=public_frames;metadata['Ready_reference']=dict(source=pin(ready),density=ready_density,root=ready_root,eye=re,role='Join diagnostic only; never replaces actual Stomp poses')
assert not F.exists();(F/'原件').mkdir(parents=True);(F/'展示副本').mkdir()
fontpath='C:/Windows/Fonts/arial.ttf';font=ImageFont.truetype(fontpath,16);small=ImageFont.truetype(fontpath,13)
def cell(f,mode,width,height,zoom=1):
 out=Image.new('RGBA',(width,height),(35,38,44,255));dr=ImageDraw.Draw(out);floor=height-65;cx=width/2;d=(f['old_density'] if mode==0 else common)*zoom;root=f['body_root'] if mode==2 else f['old_root']
 dr.line((0,floor,width,floor),fill=(125,130,135),width=1);dr.line((cx,38,cx,floor+8),fill=(68,73,80),width=1)
 layer=f['image'].transform((width,height),Image.Transform.AFFINE,(1/d,0,root[0]-cx/d,0,1/d,root[1]-floor/d),resample=Image.Resampling.BICUBIC)
 out.alpha_composite(layer);dr=ImageDraw.Draw(out);dr.text((8,8),f['label'],font=font,fill=(235,235,235));dr.text((8,height-55),'Root '+str(root),font=small,fill=(210,210,210))
 nr=point(f,mode,[f['near']['actual_bottom4_alpha_centroid_x'],f['near']['actual_core_bottom_y']+1]);er=point(f,mode,f['eye']['centroid_xy']);nx=cx+nr[0]*zoom;ey=(cx+er[0]*zoom,floor+er[1]*zoom)
 dr.line((nx-3,floor,nx+3,floor),fill=(255,105,105),width=2);dr.ellipse((ey[0]-2,ey[1]-2,ey[0]+2,ey[1]+2),outline=(255,230,70));dr.text((8,height-35),f"EyeX {er[0]:+.1f} / NearX {nr[0]:+.1f}",font=small,fill=(210,210,210));return out
plate=Image.new('RGBA',(12*190,3*250+95),(24,26,31,255));dr=ImageDraw.Draw(plate)
for mode,title in enumerate([metadata['control0'],metadata['control1'],metadata['control2']]):
 y=30+mode*250;dr.text((8,y),title,font=font,fill=(240,240,240))
 for i,f in enumerate(frames):plate.alpha_composite(cell(f,mode,190,215),dest=(i*190,y+25))
dr.text((8,800),'Exact retained whole RGBA, display only. Native body target100.8px. Control2 moves NEAR shoe; not foot-lock, not approved runtime.',font=font,fill=(255,190,110))
plate.convert('RGB').save(F/'原件/Stomp12-three-registration-controls-native-size-v001.png')
boundary=Image.new('RGBA',(6*310,3*380+100),(24,26,31,255));dr=ImageDraw.Draw(boundary)
selected=[5,6,7,8,11]
for mode in range(3):
 y=30+mode*380;dr.text((8,y),metadata['control'+str(mode)],font=font,fill=(240,240,240))
 for c,i in enumerate(selected):boundary.alpha_composite(cell(frames[i],mode,310,340,2),dest=(c*310,y+25))
 # Ready remains its actual independent profile density/ground reference.
 rf=dict(label='Ready209.0 REFERENCE',image=rim,old_density=ready_density,old_root=ready_root,body_root=ready_root,eye=re,near=dict(actual_bottom4_alpha_centroid_x=ready_near_x,actual_core_bottom_y=463))
 # cell mode0 uses Ready scale. No Ready replacement is exported.
 boundary.alpha_composite(cell(rf,0,310,340,2),dest=(5*310,y+25))
dr.text((8,1180),'Boundary controls at2x identical XY zoom. Yellow=visible eye; red=NEAR support surface. Grayline=author ground. Not skeleton markers.',font=font,fill=(255,190,110))
boundary.convert('RGB').save(F/'原件/Stomp-boundaries-three-registration-controls-2x-v001.png')
meta=O/'uniform-density-author-root-controls-v001.json';assert not meta.exists();meta.write_text(json.dumps(metadata,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');shutil.copy2(meta,F/'原件'/meta.name)
for p in (F/'原件').glob('*.png'):shutil.copy2(p,F/'展示副本'/p.name)
index=dict(schema='F-dated-media-source-version-status-v001',source_audit=pin(meta),files=[pin(p) for p in sorted(F.rglob('*')) if p.is_file()],status='NEW deterministic diagnostic display only; Root E515 retention BEFORE View; no art/runtime/final admission.',new_media_viewed=False,source_art_changed=False,FinalAccepted=False)
(F/'source-version-status-index.json').write_text(json.dumps(index,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
for f in frames:assert pin(Path(f['source']['path']))==f['source']
print(json.dumps(dict(F_batch=F.as_posix(),index=pin(F/'source-version-status-index.json'),metadata=pin(meta),join_controls=joins,source_images_unchanged=True,new_media_viewed=False),ensure_ascii=False))
