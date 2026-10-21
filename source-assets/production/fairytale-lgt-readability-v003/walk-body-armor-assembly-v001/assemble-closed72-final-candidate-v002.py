"""48-file closed-hand/armor import CANDIDATE. Local visible-pixel ownership only."""
from pathlib import Path
from datetime import datetime
import hashlib,json,shutil,math
import numpy as np
from PIL import Image,ImageDraw,ImageFont

ROOT=Path('F:/Ourgame');FAM=ROOT/'source-assets/production/fairytale-lgt-readability-v003';HERE=Path(__file__).resolve().parent
OUT=HERE/'2026-10-18-closed72-final48-candidate-v002';MEDIA=ROOT/'过程图稿与视频/2026-10-18_Walk闭握72三甲分层全六试拼_v002'
HAND_BASE=FAM/'walk-hand204-fit-v001/2026-10-18-derived204205-shared72-phase-b-v001'
HAND_INDEX=HAND_BASE/'hand204205-shared72-source-index-v001.json'
OLD=ROOT/'source-assets/production/fairytale-hero-v001/sprite-run-walk-v008/curated'
OLD_GUIDE=FAM/'walk-body-layers-v001/old-nearhand-guide-v002'
HAND90_REPORT=FAM/'walk-hand204-fit-v001/2026-10-18-cuff-measurement-phase-a-v001/hand204-cuff-grip-fit-observations-v001.json'
ARMOR_A=HERE/'2026-10-18-armor18-fit-phase-a-v001'
ARMOR_REPORT=ARMOR_A/'armor18-visible-A-B-integer-trial-proof-v001.json'

# NEW measurement on E340-retained final72 source512. No old90 coordinate multiplication.
SEAMS=[[[244,247],[250,247],[258,251],[267,257],[274,264]],
 [[236,254],[245,249],[254,247],[264,248],[274,253]],
 [[237,271],[239,260],[245,253],[253,249],[262,247]],
 [[230,271],[234,260],[241,253],[251,250],[261,251]],
 [[235,254],[243,250],[252,248],[262,249],[272,253],[278,258]],
 [[243,245],[251,246],[258,250],[268,257],[276,265]]]
AA=[[258,251],[254,248],[245,253],[241,253],[252,248],[258,250]]
BB=[[155,306],[174,322],[302,301],[319,301],[183,328],[164,308]]
FIST_POLYS=[[[220,294],[220,263],[232,252]]+SEAMS[0]+[[280,274],[290,294]],
 [[227,294],[227,259]]+SEAMS[1]+[[284,262],[284,294]],
 [[235,294]]+SEAMS[2]+[[276,252],[291,267],[291,294]],
 [[227,294]]+SEAMS[3]+[[275,257],[288,270],[288,294]],
 [[227,294],[227,261]]+SEAMS[4]+[[284,266],[284,294]],
 [[219,294],[219,261],[232,249]]+SEAMS[5]+[[283,274],[293,294]]]
KNUCKLES=[[236,266],[267,269],[273,265],[269,270],[266,269],[235,264]]
GRIPS=[[246,270],[256,270],[263,269],[259,270],[253,271],[245,269]]
AXIS=[0.8,-0.6] # Root-authorized artist bladehold screen-right/up, not a bone axis.

def pin(p):
 b=p.read_bytes();return {'path':p.as_posix(),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def write(name,data):
 p=OUT/name;p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('x',encoding='utf-8',newline='\n') as f:f.write(data if isinstance(data,str) else json.dumps(data,ensure_ascii=False,indent=2)+'\n')
 return p
def save(name,a):
 p=OUT/name;p.parent.mkdir(parents=True,exist_ok=True);assert not p.exists();Image.fromarray(a).save(p);assert np.array_equal(np.asarray(Image.open(p)),a);return p
def poly(points):
 im=Image.new('L',(512,512));ImageDraw.Draw(im).polygon([tuple(p) for p in points],fill=255);return np.asarray(im)>0
def shift(a,d):
 dx,dy=d;out=np.zeros_like(a);xs=max(0,-dx);ys=max(0,-dy);xe=min(512,512-dx);ye=min(512,512-dy)
 out[ys+dy:ye+dy,xs+dx:xe+dx]=a[ys:ye,xs:xe];assert int((a[:,:,3]>0).sum())==int((out[:,:,3]>0).sum());return out
def over(a,b):return np.asarray(Image.alpha_composite(Image.fromarray(a),Image.fromarray(b))).copy()
def owned(a,m):
 out=np.zeros_like(a);out[m]=a[m];return out
def sample(a,q):
 rgba=a[q[1],q[0]].tolist();assert rgba[3]>=128,(q,rgba);return {'point_source512':q,'actual_RGBA':rgba}
def bbox(m):
 yy,xx=np.nonzero(m);return [int(xx.min()),int(yy.min()),int(xx.max()+1),int(yy.max()+1)]

OUT.mkdir(exist_ok=False);assert not MEDIA.exists();font=ImageFont.load_default(size=13)
handindex=json.loads(HAND_INDEX.read_text(encoding='utf-8'));armorproof=json.loads(ARMOR_REPORT.read_text(encoding='utf-8'));hand90=json.loads(HAND90_REPORT.read_text(encoding='utf-8'))
sources=[pin(p) for p in [HAND_INDEX,ARMOR_REPORT,HAND90_REPORT,OLD.parent/'sprite-request.json']]
bodyrows=[];markers=[];originals=[];wholes=[];assemblies=[];art=[]
for ar in armorproof['armor18']:
 p=Path(ar['output']['path']);assert pin(p)==ar['output'];sources.append(pin(p));src=Path(ar['source']['path']);sources.append(pin(src));assert pin(src)==ar['source']
 a=np.asarray(Image.open(p)).copy();op=save(f'import-candidate-48/Armor/{ar["component"]}/frame-{ar["frame"]}.png',a)
 art.append({**ar,'final48_output':pin(op)})
for i in range(6):
 op=OLD/f'frame-{i}.png';old=np.asarray(Image.open(op)).copy();sources.append(pin(op))
 hr=handindex['rows'][i];hp=Path(hr['source']['path']);assert pin(hp)==hr['source'];source=np.asarray(Image.open(hp)).copy();sources.append(pin(hp))
 mp=OLD_GUIDE/'old-nearhand-mask'/f'frame-{i}.png';oldmask=np.asarray(Image.open(mp))>0;sources.append(pin(mp))
 gm=poly(hand90['frames'][i]['old_glove_removal_polygon'])&oldmask&(old[:,:,3]>0)
 oldcuffmask=oldmask&~gm&(old[:,:,3]>0)
 fm=poly(FIST_POLYS[i])&(source[:,:,3]>0);fist=owned(source,fm)
 delta=[BB[i][0]-AA[i][0],BB[i][1]-AA[i][1]];placed=shift(fist,delta);support=placed[:,:,3]>0
 remainder=old.copy();remainder[gm]=0;oldcuff=owned(old,oldcuffmask)
 revised=over(remainder,placed);revised=over(revised,oldcuff)
 allowed=oldmask|support;outside=int(np.any(revised[~allowed]!=old[~allowed],axis=1).sum());assert outside==0
 arm_mp=ARMOR_A/'ownership-masks/NearArmWithoutHand'/f'frame-{i}.png';helm_mp=ARMOR_A/'ownership-masks/HelmetForeground'/f'frame-{i}.png'
 arm=np.asarray(Image.open(arm_mp))>0;helm=np.asarray(Image.open(helm_mp))>0;sources.extend([pin(arm_mp),pin(helm_mp)])
 handowner=support&~oldcuffmask;helmowner=helm&~handowner;armowner=(arm|oldcuffmask)&~handowner&~helmowner;restowner=~handowner&~helmowner&~armowner
 masks={'BodyRest':restowner,'NearArmWithoutHand':armowner,'HelmetForeground':helmowner,'NearHand':handowner}
 layers={name:owned(revised,m) for name,m in masks.items()};sumrgba=sum(a.astype(np.uint16) for a in layers.values())
 assert np.array_equal(sumrgba,revised.astype(np.uint16));pair=sum(int((masks[a]&masks[b]).sum()) for a in masks for b in masks if a<b);assert pair==0
 alpha_pair=sum(int(((layers[a][:,:,3]>0)&(layers[b][:,:,3]>0)).sum()) for a in layers for b in layers if a<b);assert alpha_pair==0
 exports={name:pin(save(f'import-candidate-48/BodyLayers/{name}/frame-{i}.png',a)) for name,a in layers.items()}
 wholep=save(f'import-candidate-48/RevisedWhole/frame-{i}.png',revised);wholes.append(revised)
 save(f'proof-masks/old-glove-removed/frame-{i}.png',(gm*255).astype(np.uint8));save(f'proof-masks/new-fist-placed/frame-{i}.png',(support*255).astype(np.uint8));save(f'proof-masks/original-cuff-retained/frame-{i}.png',(oldcuffmask*255).astype(np.uint8))
 placedp=save(f'placed-fist-sourceRGBA/frame-{i}.png',placed)
 sourcebb=bbox(fm);oldbb=bbox(gm);ratio=(sourcebb[2]-sourcebb[0])/(oldbb[2]-oldbb[0])
 actualA=sample(source,AA[i]);actualB=sample(old,BB[i]);grip=sample(source,GRIPS[i]);knuckle=sample(source,KNUCKLES[i]);placedgrip=[GRIPS[i][0]+delta[0],GRIPS[i][1]+delta[1]]
 mb={'frame':i,'duration_ms':83,'native_request':hr['native_source_cell']['native_request'],'canvas_px':[512,512],
     'ground_pivot_px':[256,464],'ground_pivot_role':'display canvas anchor from source request512 safe_margin48 and bottom alignment; not measured support foot/root or foot lock',
     'actual_source_alpha_bottom_exclusive':int(np.nonzero(old[:,:,3]>0)[0].max()+1),'revised_alpha_bottom_exclusive':int(np.nonzero(revised[:,:,3]>0)[0].max()+1),
     'visible_cuff_A':actualA,'old_visible_cuff_B':actualB,'integer_delta_xy':delta,
     'Grip_artist_design_source':grip,'Grip_canvas_px':placedgrip,'knuckle_visible_candidate':knuckle,
     'Axis_artist_bladehold_screen_xy':AXIS,'Axis_angle_clockwise_from_screen_right_deg':math.degrees(math.atan2(AXIS[1],AXIS[0])),
     'Axis_role':'Explicit low hand, raised-tip bladehold artist design. No bone inference or weapon grasp proof; Root may tune during runtime sword.50 review.',
     'hidden_wrist_bone':None,'actual_weapon_grasp_accepted':False,'body_world_height_profile':72,'sword_world_scale_profile':0.50,
     'locomotion_world_speed_design':80,'cycle_seconds_design':0.498,'motion_profile_role':'Explicit tuning values, not stride measurement or foot-lock proof'}
 markers.append(mb)
 armor={part:np.asarray(Image.open(OUT/f'import-candidate-48/Armor/{part}/frame-{i}.png')).copy() for part in ['Chest','NearShoulder','FarShoulder']}
 assembled=np.zeros_like(revised)
 for a in [layers['BodyRest'],armor['FarShoulder'],armor['Chest'],layers['NearArmWithoutHand'],armor['NearShoulder'],layers['HelmetForeground'],layers['NearHand']]:assembled=over(assembled,a)
 ap=save(f'QA-noSword-assembly-six/frame-{i}.png',assembled);assemblies.append(assembled)
 bodyrows.append({'frame':i,'source_body':pin(op),'source_hand':pin(hp),'native_source_cell':hr['native_source_cell'],'new_source_visible_seam_polyline':SEAMS[i],
  'source_fist_cut_polygon':FIST_POLYS[i],'old_glove_removal_polygon':hand90['frames'][i]['old_glove_removal_polygon'],'old_nearhand_mask':pin(mp),
  'old_brown_cuff_retained_pixel_count':int(oldcuffmask.sum()),'source_fist_bbox_diagnostic':sourcebb,'old_glove_bbox_diagnostic':oldbb,'fist_to_old_glove_width_ratio':ratio,
  'placed_fist_sourceRGBA':pin(placedp),'revised_whole':pin(wholep),'exclusive_body_layers':exports,'noSword_assembly_QA':pin(ap),
  'outside_oldhandmask_union_newhandalpha_RGBA_mismatch_pixels':outside,'four_layers_revisedwhole_RGBA_mismatch_pixels':0,'exclusive_owner_mask_pair_intersection_pixels':pair,'exclusive_layer_alpha_pair_intersection_pixels':alpha_pair,
  'source_fist_draw_resample_rotation_mirror_recolor':False,'source_body_equals_revisedbody_claim':False,'candidate_semantic_edges_uncertainty_px':2,'accepted':False})
 # Actual full source512 marker diagram; sword is a design axis line, not painted asset art.
 canvas=Image.new('RGBA',(608,608),(27,29,32,255));canvas.alpha_composite(Image.fromarray(revised),(48,48));draw=ImageDraw.Draw(canvas)
 for k in range(0,513,32):
  draw.line([(48+k,48),(48+k,560)],fill=(60,200,210,70),width=1);draw.line([(48,48+k),(560,48+k)],fill=(60,200,210,70),width=1)
  if k%64==0:draw.text((38+k,29),str(k),fill='white',font=font);draw.text((12,41+k),str(k),fill='white',font=font)
 x,y=placedgrip;draw.ellipse((x+44,y+44,x+52,y+52),outline=(255,230,70,255),width=1);draw.line([(x+48,y+48),(x+48+40,y+48-30)],fill=(255,230,70,255),width=2)
 draw.line([(299,512),(309,512)],fill=(100,255,130,255),width=2);draw.line([(304,507),(304,517)],fill=(100,255,130,255),width=2)
 draw.text((48,7),f'CLOSED72 BODY {i} | source512 marker TRIAL',fill='white',font=font)
 draw.text((48,578),f'Grip{placedgrip}; display pivot[256,464]; blade Axis design[.8,-.6]',fill='white',font=font)
 originals.append(save(f'原件/closed72-{i}-Grip-Axis-grid-v001.png',np.asarray(canvas)))
 # Cuff/width diagnostics stay at native1x, no artwork resampling.
 canv=Image.new('RGBA',(768,256),(27,29,32,255));draw=ImageDraw.Draw(canv)
 for j,(a,rect,title) in enumerate([(old,[oldbb[0]-18,oldbb[1]-30,oldbb[0]+110,oldbb[1]+98],'OLD glove + cuff'),(source,[192,208,320,336],'NEW unified72 source'),(revised,[oldbb[0]-18,oldbb[1]-30,oldbb[0]+110,oldbb[1]+98],'NEW72 cuff-retained TRIAL')]):
  canv.alpha_composite(Image.fromarray(a).crop(tuple(rect)),(j*256+64,64));draw.text((j*256+5,5),title,fill='white',font=font);draw.text((j*256+5,226),f'source origin{rect[:2]} /1x',fill='white',font=font)
 draw.text((6,242),f'FRAME{i}: width ratio {ratio:.3f}; exact outside allowed union; visible split +/-2px',fill=(255,200,90,255),font=font)
 originals.append(save(f'原件/closed72-cuff-fit-{i}-UNSCALED-v001.png',np.asarray(canv)))
for title,frames in [('revised-whole-six-UNSCALED-v001',wholes),('noSword-armor-six-UNSCALED-v001',assemblies)]:
 contact=np.zeros((1024,1536,4),np.uint8)
 for i,a in enumerate(frames):contact[(i//3)*512:(i//3+1)*512,(i%3)*512:(i%3+1)*512]=a
 originals.append(save(f'原件/{title}.png',contact))
for name in ['BodyRest','NearArmWithoutHand','HelmetForeground','NearHand']:
 contact=np.zeros((512,3072,4),np.uint8)
 for i in range(6):contact[:,512*i:512*(i+1)]=np.asarray(Image.open(OUT/f'import-candidate-48/BodyLayers/{name}/frame-{i}.png'))
 originals.append(save(f'原件/layer-{name}-six-UNSCALED-v001.png',contact))
for p in originals:
 q=OUT/'展示副本'/p.name;q.parent.mkdir(exist_ok=True);shutil.copyfile(p,q);assert pin(q)['sha256']==pin(p)['sha256']
for s in sources:assert pin(Path(s['path']))==s
count=len(list((OUT/'import-candidate-48').rglob('*.png')));assert count==48
markerpath=write('walk-six-Grip-Axis-ground-display-markers-v001.json',{'schema':'Walk6-canvas512-visible-Grip-artist-Axis-display-pivot-candidate-v001','frames':markers,'durations_ms':[83]*6,'no_actual_wrist_bone_claim':True,'artist_design_profile_not_footlock_proof':True})
proof=write('closed72-final48-source-and-pixel-proof-v001.json',{'schema':'Walk6-closed72-armor18-exclusive24-revisedwhole6-CANDIDATE-v001','created_local':datetime.now().astimezone().isoformat(),'source_view_retention':'E340 shared72 final6 before actualView; E341 armor18/oldbody ownership before view; E319 oldbody; E339 old90 cuff trials.','source_pins':sources,'body6':bodyrows,'adjusted_armor18':art,'markers':pin(markerpath),'import_candidate_png_count':count,'import_breakdown':{'armor18':18,'exclusive_body_layers':24,'revised_whole6':6},'noSword_QA_composites':6,'source_RGBA_changed':False,'newbody_explicitly_differs_from_oldbody':True,'new_media_viewed':False,'fit_semantic_runtime_acceptance':False,'native_generation_calls':0})
write('HANDOFF.md','48 PNG import candidates: Armor18 + exclusive BodyRest/NearArmWithoutHand/HelmetForeground/NearHand24 + RevisedWhole6. RevisedWhole explicitly includes new closed72 fists; never equals oldBody. Pixels outside oldhandmask UNION placednewhandalpha are exact oldRGBA; all six outside mismatches0. Four layers sum to revisedWhole RGBA byte-exact and alpha supports never overlap. Armor18 retains frozen source scale and only prior integer A/B translations, same pouch side and physical shoulder chain. Native source204 cells0..4 and205 cell5, ONE unifiedshared72 extraction. Grip is visible source-face artist handle design; Axis[.8,-.6] is Root-authorized artist low-hand raised-tip bladehold, not bone/weapon grasp proof. Groundpivot[256,464] is canvas display anchor, not footroot. Bodyworld72/sword.50/speed80/cycle.498 explicit tuning, not foot lock. New F canonical media must be E-retained before actualView; no Source/UE/tools/ledger/import changes.\n')
write('final48-freeze-v001.json',{'schema':'Walk6-final48-candidate-freeze-v001','files':[pin(p) for p in sorted(OUT.rglob('*')) if p.is_file()],'source_pins_rechecked':len(sources),'source_mismatches':0,'new_media_viewed':False,'accepted_or_imported':False})
(MEDIA/'原件').mkdir(parents=True);shutil.copytree(OUT,MEDIA/'原件/候选包');shutil.copytree(OUT/'展示副本',MEDIA/'展示副本')
with (MEDIA/'来源-版本-状态索引.json').open('x',encoding='utf-8',newline='\n') as f:json.dump({'date':'2026-10-18','topic':'Walk闭握72三甲分层全六试拼','version':'v002','status':'CANDIDATE-unviewed-not-imported','source_candidate':OUT.as_posix(),'proof':pin(proof),'markers':pin(markerpath),'original_and_presentation_files':[pin(p) for p in sorted(MEDIA.rglob('*')) if p.is_file()]},f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps({'out':OUT.as_posix(),'canonical_media':MEDIA.as_posix(),'import_candidates':count,'body_outside_union_mismatches':[r['outside_oldhandmask_union_newhandalpha_RGBA_mismatch_pixels'] for r in bodyrows],'fist_width_ratios':[round(r['fist_to_old_glove_width_ratio'],3) for r in bodyrows],'Grip_canvas_px':[m['Grip_canvas_px'] for m in markers],'markers':pin(markerpath),'proof':pin(proof),'new_media_viewed':False},ensure_ascii=False,indent=2))
