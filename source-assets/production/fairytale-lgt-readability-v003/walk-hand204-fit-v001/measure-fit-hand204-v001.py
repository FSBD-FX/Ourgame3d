"""Read-only source observations and integer/cuff-cut assembly TRIAL, not acceptance."""
from pathlib import Path
from datetime import datetime
import hashlib,json,shutil
import numpy as np
from PIL import Image,ImageDraw,ImageFont

ROOT=Path('F:/Ourgame'); HERE=Path(__file__).resolve().parent
OUT=HERE/'2026-10-18-cuff-measurement-phase-a-v001'
OLD=ROOT/'source-assets/production/fairytale-hero-v001/sprite-run-walk-v008/curated'
HAND=ROOT/'source-assets/production/fairytale-lgt-readability-v003/walk-hand204-extraction-v001/run-hand204-shared-HD-v001/curated'
GUIDE=ROOT/'source-assets/production/fairytale-lgt-readability-v003/walk-body-layers-v001/old-nearhand-guide-v002'

# Artist observations of VISIBLE cuff-to-glove ink, +/-2px, not wrist bones.
NEW_SEAMS=[[[242,245],[250,243],[258,245],[268,250],[277,257],[283,266]],
 [[233,249],[242,243],[252,241],[263,242],[274,246],[283,253]],
 [[232,270],[234,258],[242,247],[251,242],[263,241]],
 [[226,272],[230,260],[238,251],[248,246],[262,248]],
 [[226,252],[235,246],[246,243],[257,243],[268,246],[277,251]],
 [[231,271],[234,259],[242,249],[252,243],[263,242]]]
OLD_SEAMS=[[[136,304],[145,303],[155,306],[165,310],[175,309]],
 [[153,326],[163,322],[174,321],[184,323],[194,329]],
 [[315,283],[307,290],[301,301],[298,312],[302,320]],
 [[331,282],[324,290],[319,301],[317,312],[319,321]],
 [[159,332],[171,327],[183,327],[196,331],[205,336]],
 [[145,311],[153,307],[164,307],[176,310],[189,317]]]
AA=[[258,245],[252,242],[242,247],[238,251],[246,244],[242,249]]
BB=[[155,306],[174,322],[302,301],[319,301],[183,328],[164,308]]
KNUCKLE=[[235,264],[270,270],[277,264],[272,270],[267,269],[276,265]]
GRIP=[[244,270],[259,272],[266,271],[261,274],[254,273],[265,272]]
# Semantic cut preserves the fist side of the observed arch. It never paints new pixels.
FIST_POLYS=[[[212,301],[212,261],[224,250]]+NEW_SEAMS[0]+[[300,301]],
 [[219,301],[219,258]]+NEW_SEAMS[1]+[[293,261],[293,301]],
 [[231,301]]+NEW_SEAMS[2]+[[280,245],[300,260],[300,301]],
 [[222,301]]+NEW_SEAMS[3]+[[278,253],[295,268],[295,301]],
 [[219,301],[219,259]]+NEW_SEAMS[4]+[[293,260],[293,301]],
 [[230,301]]+NEW_SEAMS[5]+[[280,246],[300,263],[300,301]]]
# Old glove-side selection intersects the prior source ownership mask. Old cuff stays.
OLD_GLOVE_POLYS=[[[121,357],[121,313]]+OLD_SEAMS[0]+[[181,318],[185,357]],
 [[149,373],[149,333]]+OLD_SEAMS[1]+[[205,339],[205,373]],
 [[302,340],[298,312],[301,301],[307,290],[315,283],[356,283],[356,340]],
 [[319,338],[317,312],[319,301],[324,290],[331,282],[372,282],[372,338]],
 [[155,379],[155,339]]+OLD_SEAMS[4]+[[213,345],[213,379]],
 [[133,365],[133,323]]+OLD_SEAMS[5]+[[196,328],[196,365]]]

def pin(p):
 b=p.read_bytes();return {'path':p.as_posix(),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def write(name,data):
 p=OUT/name;p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('x',encoding='utf-8',newline='\n') as f:f.write(data if isinstance(data,str) else json.dumps(data,ensure_ascii=False,indent=2)+'\n')
 return p
def save(name,a):
 p=OUT/name;p.parent.mkdir(parents=True,exist_ok=True);assert not p.exists();Image.fromarray(a).save(p);assert np.array_equal(np.asarray(Image.open(p)),a);return p
def mask(poly):
 im=Image.new('L',(512,512));ImageDraw.Draw(im).polygon([tuple(p) for p in poly],fill=255);return np.asarray(im)>0
def bbox(a):
 yy,xx=np.nonzero(a);return [int(xx.min()),int(yy.min()),int(xx.max()+1),int(yy.max()+1)] if len(xx) else None
def sample(a,q):return {'point_source512':q,'actual_RGBA':a[q[1],q[0]].tolist(),'alpha_is_visible':bool(a[q[1],q[0],3]>0)}
def shift(a,d):
 dx,dy=d;out=np.zeros_like(a);xs=max(0,-dx);ys=max(0,-dy);xe=min(512,512-dx);ye=min(512,512-dy)
 out[ys+dy:ye+dy,xs+dx:xe+dx]=a[ys:ye,xs:xe];return out
def over(a,b):return np.asarray(Image.alpha_composite(Image.fromarray(a),Image.fromarray(b))).copy()

OUT.mkdir(exist_ok=False);font=ImageFont.load_default(size=13);obs=[];originals=[];sources=[];whole=[]
for i in range(6):
 oldp=OLD/f'frame-{i}.png';handp=HAND/f'frame-{i}.png';maskp=GUIDE/'old-nearhand-mask'/f'frame-{i}.png'
 old=np.asarray(Image.open(oldp)).copy();new=np.asarray(Image.open(handp)).copy();oldmask=np.asarray(Image.open(maskp))>0
 sources.extend([pin(oldp),pin(handp),pin(maskp)])
 fm=mask(FIST_POLYS[i])&(new[:,:,3]>0);newf=new.copy();newf[~fm]=0
 gm=mask(OLD_GLOVE_POLYS[i])&oldmask&(old[:,:,3]>0)
 delta=[BB[i][0]-AA[i][0],BB[i][1]-AA[i][1]];placed=shift(newf,delta);support=placed[:,:,3]>0
 # Retain original cuff and all other source pixels; source cuff occludes new fist where they meet.
 remainder=old.copy();remainder[gm]=0
 oldcuff=np.zeros_like(old);oldcuff[oldmask&~gm]=old[oldmask&~gm]
 merged=over(remainder,placed);merged=over(merged,oldcuff)
 allowed=oldmask|support;outside=int(np.any(old[~allowed]!=merged[~allowed],axis=1).sum());assert outside==0
 # Candidate touched support may gain transparent RGB through alpha composition: report exact scope.
 nbb=bbox(fm);obb=bbox(gm);ow=obb[2]-obb[0];nw=nbb[2]-nbb[0]
 intersection=int((support&(oldcuff[:,:,3]>0)).sum())
 row={'frame':i,'status':'direction_rejected_no_export' if i==5 else 'TRIAL_cuff_retained_no_scale_no_rotation',
      'source_hand':pin(handp),'source_body':pin(oldp),'old_hand_mask':pin(maskp),
      'A_visible_cuff_glove_seam':sample(new,AA[i]),'B_visible_old_cuff_glove_seam':sample(old,BB[i]),
      'source_new_seam_polyline_artist_observed':NEW_SEAMS[i],'target_old_seam_polyline_artist_observed':OLD_SEAMS[i],
      'seam_uncertainty_source_px':2,'integer_translation_xy':delta,
      'visible_knuckle_crease_candidate':sample(new,KNUCKLE[i]),
      'weapon_grip_artist_design_candidate':sample(new,GRIP[i]),
      'placed_grip_artist_design_candidate':[GRIP[i][0]+delta[0],GRIP[i][1]+delta[1]],
      'actual_hidden_wrist_bone':None,'actual_weapon_held_or_axis':None,
      'new_fist_source_cut_polygon':FIST_POLYS[i],'old_glove_removal_polygon':OLD_GLOVE_POLYS[i],
      'old_cuff_retained':True,'source_fist_bbox_diagnostic':nbb,'old_glove_bbox_diagnostic':obb,
      'new_fist_width_px':nw,'old_glove_width_px':ow,'fist_to_old_glove_width_ratio':nw/ow,
      'new_fist_pixels_occluded_by_original_cuff':intersection,
      'outside_oldhandmask_union_newalpha_mismatch_pixels':outside,
      'source_resampled_rotated_mirrored_recolored':False,'wrist_fit_accepted':False,'new_outputs_viewed':False}
 if i<5:
  row['placed_fist']=pin(save(f'placed-NearHand-trial/frame-{i}.png',placed));row['revised_whole']=pin(save(f'revised-whole-trial/frame-{i}.png',merged))
  whole.append(merged)
 # Technical no-resampling close-ups with explicit source xy translation only.
 canvas=Image.new('RGBA',(768,256),(27,29,32,255));draw=ImageDraw.Draw(canvas)
 for col,(a,rect,title) in enumerate([(old,[int(obb[0])-10,int(obb[1])-30,int(obb[0])+118,int(obb[1])+98],'OLD cuff and glove'),(new,[192,208,320,336],'204 source cuff and fist'),(merged,[int(obb[0])-10,int(obb[1])-30,int(obb[0])+118,int(obb[1])+98],'TRIAL integer + cuff retained')]):
  tile=Image.fromarray(a).crop(tuple(rect));canvas.alpha_composite(tile,(col*256+64,64));draw.text((col*256+5,5),title,fill='white',font=font)
  draw.text((col*256+5,226),f'source origin {rect[:2]} / 1x',fill='white',font=font)
  for k in range(0,129,16):
   draw.line([(col*256+64+k,64),(col*256+64+k,192)],fill=(60,200,210,80),width=1)
   draw.line([(col*256+64,64+k),(col*256+192,64+k)],fill=(60,200,210,80),width=1)
 draw.text((6,242),f'FRAME {i}: '+('REJECTED DIRECTION; NOT EXPORTED' if i==5 else f'width ratio {nw/ow:.3f}; cuff split candidate +/-2px'),fill=(255,200,90,255),font=font)
 p=save(f'原件/hand-cuff-fit-{i}-UNSCALED-v001.png',np.asarray(canvas));originals.append(p);obs.append(row)

# The contact contains 0..4 only; frame5 remains explicitly absent until native205.
contact=np.zeros((512,2560,4),np.uint8)
for i,a in enumerate(whole):contact[:,i*512:(i+1)*512]=a
originals.append(save('原件/revised-whole-five-trial-UNSCALED-v001.png',contact))
for p in originals:
 q=OUT/'展示副本'/p.name;q.parent.mkdir(exist_ok=True);shutil.copyfile(p,q);assert pin(p)['sha256']==pin(q)['sha256']
report=write('hand204-cuff-grip-fit-observations-v001.json',{'schema':'Walk204-cuff-Grip-source512-TRIAL-v001','created_local':datetime.now().astimezone().isoformat(),'source_view_authorization':'Root E336 retained originals and source grids, 2SHA0 before actual views. Oldbody sources retained E319.','source_pins':sources,'frames':obs,'direction_decision':{'204_frame5':'Rejected: fist extends down-right; oldbody5 near chain extends down-left. Native205 requested by Root.','204_frame0_reuse_for_body5':'Whole cuff translation rejected (outer seam slope differs); cuff splitting might allow direction, but no reuse/export accepted. Native205 preferred.','local_fix':'No draw, recolor, resize, rotation or mirror; deterministic visible pixel cut with old cuff retained only.'},'root_acceptance':False,'final_six_import_ready':False,'new_outputs_viewed':False})
for s in sources:assert pin(Path(s['path']))==s
write('HANDOFF.md','Five TRIALs only: 204 0..4 integer shift, source cuff split, original cuff retained. Source5 measured but rejected and not exported. Visible seam A/B and artist Grip are not wrist bones or a proven sword grip. Wide fist ratios require visual taste review. Original and presentation images are unviewed; Root must retain to E with two SHA checks before any View.\n')
write('source-version-status-index-v001.json',{'date':'2026-10-18','topic':'walk204-cuff-fit','version':'phase-a-v001','status':'TRIAL-unviewed-not-imported','originals':[pin(p) for p in originals],'presentation':[pin(OUT/'展示副本'/p.name) for p in originals],'report':pin(report),'all_sources_unchanged':True,'files':[pin(p) for p in sorted(OUT.rglob('*')) if p.is_file()]})
print(json.dumps({'out':OUT.as_posix(),'report':pin(report),'width_ratios':[round(o['fist_to_old_glove_width_ratio'],3) for o in obs],'sources_unchanged':True,'new_outputs_viewed':False},ensure_ascii=False,indent=2))
