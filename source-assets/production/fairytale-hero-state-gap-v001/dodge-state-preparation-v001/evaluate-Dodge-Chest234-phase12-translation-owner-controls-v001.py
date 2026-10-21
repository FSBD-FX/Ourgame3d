from pathlib import Path
import hashlib,json,shutil
import numpy as np
from PIL import Image,ImageDraw,ImageFont
ROOT=Path('F:/Ourgame');HERE=Path(__file__).resolve().parent
OUT=HERE/'Chest234-phase12-translation-owner-controls-v001'
MEDIA=ROOT/'过程图稿与视频/2026-10-18_钟盔Dodge胸衣234一二相有限平移原分区对照_v001'
assert not OUT.exists() and not MEDIA.exists();OUT.mkdir()
OLD_BODY=HERE/'own-partition-SWD-fit-v001'
FULL=HERE/'LGT234-236-own-source-integer-fit-v001'
CONTRACT=FULL/'Dodge218-LGT234-236-own-five-layers-SWD050-integer-fit-candidate-v001.json'
def pin(p):
 b=p.read_bytes();return {'path':p.as_posix(),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(rel,v):
 p=OUT/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');return p
def translate(a,delta):
 dx,dy=delta;v=np.zeros_like(a);sx0=max(0,-dx);sy0=max(0,-dy);sx1=min(512,512-dx);sy1=min(512,512-dy)
 v[sy0+dy:sy1+dy,sx0+dx:sx1+dx]=a[sy0:sy1,sx0:sx1]
 assert np.count_nonzero(v[:,:,3])==np.count_nonzero(a[:,:,3]);return v
data=read(CONTRACT);rows=[];font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',20)
sheet=Image.new('RGB',(1920,944),(45,48,54));ds=ImageDraw.Draw(sheet)
for rowindex,i in enumerate([1,2]):
 r=data['frames'][i];cf=r['armor_integer_fits']['Chest'];source=Path(r['Dodge218_source']['path']);a=np.array(Image.open(source).convert('RGBA'))
 body={n:np.array(Image.open(OLD_BODY/f'body-layers/{n}/frame-{i}.png').convert('RGBA')) for n in ['BodyRest','NearArmWithoutHand','HelmetForeground','FarHandForeground','NearHand']}
 assert np.array_equal(np.stack([v.astype(np.uint16) for v in body.values()]).sum(axis=0),a)
 chsource=Path(cf['source']['path']);ch=np.array(Image.open(chsource).convert('RGBA'))
 A_belt=np.array(cf['A_artist_visible_component_xy'],float);B_belt=np.array(cf['B_artist_visible_body_surface_xy'],float)
 A_hole=np.array(cf['actual_hole_centroid_xy'],float);B_hole=np.array(cf['visible_source_sleeve_torso_junction_artist_xy'],float)
 d_belt=B_belt-A_belt;d_hole=B_hole-A_hole;difference=d_belt-d_hole;lower=float(np.linalg.norm(difference)/2)
 xs,ys=np.meshgrid(np.arange(-70,1),np.arange(0,101));candidates=np.column_stack([xs.ravel(),ys.ravel()])
 belt_error=np.linalg.norm(candidates-d_belt,axis=1);hole_error=np.linalg.norm(candidates-d_hole,axis=1);objective=np.maximum(belt_error,hole_error)
 index=int(np.argmin(objective));best=candidates[index].tolist()
 variants=[('belt_exact',d_belt.astype(int).tolist()),('armhole_nearest',np.rint(d_hole).astype(int).tolist()),('best_integer_minimax',best)]
 near=np.array(Image.open(r['armor_integer_fits']['ShoulderNear']['adjusted']['path']).convert('RGBA'));far=np.array(Image.open(r['armor_integer_fits']['ShoulderFar']['adjusted']['path']).convert('RGBA'));sword=np.array(Image.open(r['author_binding']['sword_layer']['path']).convert('RGBA'))
 vr=[]
 for col,(name,delta) in enumerate(variants):
  adjusted=translate(ch,delta);whole=Image.new('RGBA',(512,512))
  for v in [body['BodyRest'],far,adjusted,body['NearArmWithoutHand'],near,body['HelmetForeground'],sword,body['FarHandForeground'],body['NearHand']]:whole=Image.alpha_composite(whole,Image.fromarray(v))
  dst=OUT/f'phase-{i}/{name}.png';dst.parent.mkdir(exist_ok=True);whole.save(dst)
  p_belt=A_belt+delta-B_belt;p_hole=A_hole+delta-B_hole
  rec={'name':name,'integer_delta_xy':delta,'belt_residual_xy':p_belt.tolist(),'belt_residual_length':float(np.linalg.norm(p_belt)),'visible_junction_residual_xy':p_hole.tolist(),'visible_junction_residual_length':float(np.linalg.norm(p_hole)),'maximum_two_target_residual':float(max(np.linalg.norm(p_belt),np.linalg.norm(p_hole))),'whole_control':pin(dst),'source_component_all_alpha_pixels_preserved':True,'body_original_RGBA_reconstruction_exact':True,'broad_gray_collar_overlay_used':False,'sourcefit_accepted':False}
  vr.append(rec)
  y0=255 if i==1 else 200;crop=whole.crop((100,y0,420,y0+220));zoom=crop.resize((640,440),Image.Resampling.NEAREST);sheet.paste(zoom,(640*col,472*rowindex+32),zoom)
  ds.text((640*col+8,472*rowindex+6),f'Dodge{i} {name} delta{delta}; uniform2x',font=font,fill='white')
 rows.append({'phase':i,'body_source':pin(source),'chest234_original_curated':pin(chsource),'A_belt_artist_visible':A_belt.tolist(),'B_belt_artist_visible':B_belt.tolist(),'A_actual_true_hole_centroid':A_hole.tolist(),'B_visible_sleeve_torso_junction_artist':B_hole.tolist(),'target_authority':'Visible source-art proposals, not skeleton/socket. BodyB and buckleA marker uncertainty3px. Geometric bounds are conditional on these documented targets.','translation_invariant_two_target_discrepancy_xy':difference.tolist(),'any_real_translation_minimax_residual_lower_bound_source_px':lower,'grid_domain':{'dx_integer':[-70,0],'dy_integer':[0,100],'count':len(candidates)},'actual_best_integer_delta':best,'actual_best_integer_minimax_residual':float(objective[index]),'robust_lower_bound_after_6px_per_target_error_budget':max(0.,lower-6.),'variants':vr})
pp=OUT/'Dodge-Chest234-phase12-original-helmet-only-three-translation-controls-UNIFORM2x.png';sheet.save(pp)
report=write('finite-translation-and-original-owner-feasibility-v001.json',{'schema':'Dodge-Chest234-phase12-finite-translation-owner-controls-v001','previous_frozen_fullfit':pin(CONTRACT),'previous_frozen_body_source_partition':pin(OLD_BODY/'Dodge218-own-five-partitions-SWD050-Grip-Axis-ground-candidate-v001.json'),'worker_actual_E491_E493_review':'Full4, uniform2x torso, fists, ownership and Readyjoin actually viewed after twoSHA0. Phase1/2 broad gray strip cuts vest into upper/lower fragments. Gray collar foreground selection in that candidate intruded into actual gray torso and is not a valid fix for Chest234. Original source pixels and freeze preserved.','new_control':'Use original own218 helmet-only foreground; no added gray torso/collar masking. Compare exact waist, exact rounded aperture and finite best integer minimax. Armor unchanged except integer translation. Near/Far/Sword fixed across variants.','source_semantics':'Chest234 opaque neck interior violates original true-green aperture prompt. Original reports/spec failure remain; no paint/erase or fake lining. Finite translations cannot change the aperture-to-buckle vector.','rows':rows,'presentation':pin(pp),'presentation_scale_xy':[2,2],'newmedia_View':False,'newmedia_E_retained':False,'TrialAllowed':False,'native_actual_receipts':None,'preliminary_conclusion':'Phase1/2 cannot satisfy both documented visible-art targets with an integer translation. Source contour/orientation correction is needed if actual controls confirm visible mismatch; no automatic generation invoked. Near235/Far236 and existingSword remain independent reusable candidates.'})
freeze=write('finite-owner-translation-controls-freeze-v001.json',{'script':pin(Path(__file__)),'files':[pin(p) for p in sorted(OUT.rglob('*')) if p.is_file()],'newmedia_View':False,'sourcefit_accepted':False})
(MEDIA/'原件').mkdir(parents=True);shutil.copytree(OUT,MEDIA/'原件/有限平移原分区对照完整包');(MEDIA/'展示副本').mkdir();shutil.copyfile(pp,MEDIA/'展示副本'/pp.name)
ip=MEDIA/'来源-版本-状态索引.json';ip.write_text(json.dumps({'date':'2026-10-18','topic':'钟盔Dodge胸衣234一二相有限平移原分区对照','version':'v001','status':'UNVIEWED deterministic controls pending RootE; no fullrow/sourcefit/native acceptance','report':pin(report),'freeze':pin(freeze),'files':[pin(p) for p in sorted(MEDIA.rglob('*')) if p.is_file()]},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'canonical_F_media':MEDIA.as_posix(),'files':sum(p.is_file() for p in MEDIA.rglob('*')),'bytes':sum(p.stat().st_size for p in MEDIA.rglob('*') if p.is_file()),'report':pin(report),'freeze':pin(freeze),'actual_best_integer_fits':[{'phase':r['phase'],'delta':r['actual_best_integer_delta'],'max_residual':r['actual_best_integer_minimax_residual']} for r in rows],'newmedia_View':False},ensure_ascii=False,indent=2))
