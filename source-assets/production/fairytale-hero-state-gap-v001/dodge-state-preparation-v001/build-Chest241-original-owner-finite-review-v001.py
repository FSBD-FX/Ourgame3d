"""Small review set only: original218 owners +235/236+rigidSword; Chest241 integer fit."""
from pathlib import Path
import hashlib,json,shutil,sys,ast
from collections import deque
import numpy as np
from PIL import Image,ImageDraw,ImageFont
ROOT=Path('F:/Ourgame');HERE=Path(__file__).resolve().parent
SG=Path('C:/Users/22499/.codex/skills/sprite-gen');assert Path(sys.executable).resolve()==(SG/'.venv/Scripts/python.exe').resolve()
OUT=HERE/'LGT241-original-owner-finite-review-v001';MEDIA=ROOT/'过程图稿与视频/2026-10-18_钟盔Dodge胸衣241原分区有限配准与真实72展示_v001'
assert not OUT.exists() and not MEDIA.exists();OUT.mkdir()
def pin(p):
 b=p.read_bytes();return {'path':p.as_posix(),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(rel,v):
 p=OUT/rel;p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('x',encoding='utf-8',newline='\n') as f:f.write(v if isinstance(v,str) else json.dumps(v,ensure_ascii=False,indent=2)+'\n')
 return p
def save(rel,im):
 p=OUT/rel;p.parent.mkdir(parents=True,exist_ok=True);assert not p.exists();im.save(p);return p
def load(v):
 p=Path(v['path']);assert pin(p)==v;im=Image.open(p).convert('RGBA');assert im.size==(512,512);return im
def translate(a,d):
 dx,dy=map(int,d);v=np.zeros_like(a);x0=max(0,-dx);x1=min(512,512-dx);y0=max(0,-dy);y1=min(512,512-dy)
 v[y0+dy:y1+dy,x0+dx:x1+dx]=a[y0:y1,x0:x1]
 assert np.count_nonzero(v[:,:,3])==np.count_nonzero(a[:,:,3]),'No nontransparent component pixel may be clipped'
 assert np.array_equal(v[y0+dy:y1+dy,x0+dx:x1+dx],a[y0:y1,x0:x1])
 return v
def retained(v,idx):
 p=Path(v['path']);assert pin(p)==v;j=read(idx);assert j['verification_passes']==2 and j['source_and_target_hash_mismatches']==0
 row=next(x for x in j['files'] if x['sha256']==v['sha256']);e=idx.parent/row['retained_relative']
 for _ in range(2):assert p.read_bytes()==e.read_bytes()
def place(im,root,ground,out):
 k=72/416;aff=(1/k,0,float(root[0]-ground[0]/k),0,1/k,float(root[1]-ground[1]/k))
 return im.convert('RGBa').transform(out,Image.Transform.AFFINE,aff,resample=Image.Resampling.BICUBIC).convert('RGBA')
BASE=HERE/'LGT240-235-236-original-owner-integer-fit-v001/Dodge218-Chest240-Near235-Far236-original-owner-SWD050-integer-fit-candidate-v001.json'
FEAS=HERE/'Chest241-postextract-two-point-feasibility-v001/Chest241-actual-shared-aperture-buckle-body-two-point-feasibility-v001.json'
MEAS=HERE/'Chest241-edit-readonly-measurement-v001/Chest241-actual-protectedcells-fixedbuckle-aperture-target-measurement-v001.json'
REC=HERE/'official-process-runs-v001/chest-native241/run-shared-HD-v001/extraction-receipt-v001.json'
base=read(BASE);feas=read(FEAS);rec=read(REC);meas=read(MEAS)
assert pin(BASE)['sha256']=='bb3d5be1ac1ab48ab6d18eaf71ae74a426dcc37fdca498c2e3d27b54b2cc8921'
assert pin(FEAS)['sha256']=='702ce11a1d495ca60bcf373aba068e09ee66fedddd396d4a44b0bd7b61a40316'
E508=next(Path('E:/OurGame/Knight/过程图稿与视频').glob('*v508/source-size-SHA256.json'));E502=next(Path('E:/OurGame/Knight/过程图稿与视频').glob('*v502/source-size-SHA256.json'))
FONT=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',18)
rows=[];wholes=[];best_wholes={}
for i in range(4):
 b=base['frames'][i];f=feas['rows'][i];chpin=rec['frames'][i]['curated'];retained(chpin,E508);ch=np.array(load(chpin));layers={n:np.array(load(v)) for n,v in b['five_body_layers'].items()}
 for v in b['five_body_layers'].values():retained(v,E502)
 src=np.array(load(b['Dodge218_source']));masks=np.stack([x[:,:,3]>0 for x in layers.values()]);assert masks.sum(axis=0).max()<=1
 assert np.array_equal(sum(x.astype(np.uint16) for x in layers.values()),src.astype(np.uint16))
 for n,a in layers.items():assert np.array_equal(a[a[:,:,3]>0],src[a[:,:,3]>0])
 armor={n:np.array(load(b['armor_integer_fits'][n]['adjusted'])) for n in ['ShoulderFar','ShoulderNear']};swd=np.array(load(b['author_binding']['sword_layer']))
 for n in armor:retained(b['armor_integer_fits'][n]['adjusted'],E502)
 retained(b['author_binding']['sword_layer'],E502)
 d=f['belt_anchored_integer_delta'];A=f['tracked_buckle_curated_artist_xy'];B=f['body_buckle_artist_xy'];J=f['body_near_sleeve_junction_artist_xy'];ar=np.rint(A).astype(int)
 assert ch[ar[1],ar[0],3]>=128
 def composite(delta):
  moved=translate(ch,delta);stack={'BodyRest':layers['BodyRest'],'ShoulderFar':armor['ShoulderFar'],'Chest':moved,'NearArmWithoutHand':layers['NearArmWithoutHand'],'ShoulderNear':armor['ShoulderNear'],'HelmetForeground':layers['HelmetForeground'],'IndependentSword':swd,'FarHandForeground':layers['FarHandForeground'],'NearHand':layers['NearHand']}
  assert list(stack)==b['nine_slot_order'];out=Image.new('RGBA',(512,512))
  for v in stack.values():out=Image.alpha_composite(out,Image.fromarray(v))
  fore=np.zeros((512,512),bool)
  for n in b['nine_slot_order'][3:]:fore|=stack[n][:,:,3]>=128
  x0,y0,x1,y1=b['armor_integer_fits']['Chest']['body_original_brown_belt_ROI'];oldbelt=np.zeros((512,512),bool);v=src[y0:y1,x0:x1]
  oldbelt[y0:y1,x0:x1]=(v[:,:,3]>=128)&(v[:,:,0]>90)&(v[:,:,0]>1.25*v[:,:,1])&(v[:,:,1]>30)&(v[:,:,2]<100)
  return out,{'old_belt_color_pixels_still_exposed':int(np.count_nonzero(oldbelt&~(moved[:,:,3]>=128)&~fore)),'all241_nontransparent_pixels_preserved':True,'integer_translation_xy':list(map(int,delta)),'extra_scale':1,'rotation':0,'nearhole_junction_residual_source_xy':(np.array(f['actual_near_hole_centroid_source_xy'])+delta-J).tolist(),'tracked_buckle_residual_source_xy':(np.array(A)+delta-B).tolist()}
 whole,diag=composite(d);wp=save(f'whole-belt-anchored/frame-{i}-LGT-SWD.png',whole);wholes.append(whole)
 row={'frame':i,'body_source':b['Dodge218_source'],'body_layers_reused':b['five_body_layers'],'source_body_RGBA_exclusive_reconstruction_exact':True,'HelmetForeground_original_helmet_only_no_gray_band':True,'chest_source241':chpin,'chest_A_artist_tracked_xy':A,'chest_A_rounded_pixel_xy':ar.tolist(),'chest_A_actual_RGBA':ch[ar[1],ar[0]].tolist(),'body_B_artist_xy':B,'body_B_actual_RGBA':src[int(B[1]),int(B[0])].tolist(),'body_J_artist_xy':J,'J_B_are_visible_artist_surface_targets_not_bone_or_axis':True,'tracked_marker_uncertainty_raw_px':3,'belt_anchored':diag,'whole':pin(wp),'armor_near_far_unchanged_from_sourcefit240':{n:b['armor_integer_fits'][n] for n in armor},'independent_sword_binding_unchanged':b['author_binding'],'nine_slot_order':b['nine_slot_order'],'root_proposal':b['root_proposal'],'row_scale':{'source_standing_height':416,'display_height':72,'scale':72/416,'per_frame_normalized':False},'sourcefit_accepted':False,'TrialAllowed':False}
 if i in [1,2]:
  bd=f['best_finite_integer_two_point_fit']['delta_xy'];bi,bdiag=composite(bd);bp=save(f'finite-best-controls/frame-{i}-LGT-SWD.png',bi);best_wholes[i]=bi;row['best_integer_control']={'whole':pin(bp),'diagnostic':bdiag,'numerical_basis':f['best_finite_integer_two_point_fit'],'fit_success_asserted':False}
 rows.append(row)
plate=Image.new('RGB',(2048,560),(45,48,54));dp=ImageDraw.Draw(plate)
for i,im in enumerate(wholes):plate.paste(im,(512*i,40),im);dp.text((512*i+10,10),f'Phase{i} belt-anchored / source1x',font=FONT,fill='white')
save('presentation/Chest241-four-whole-belt-anchored-SOURCE1x.png',plate)
torso=Image.new('RGB',(2560,488),(45,48,54));dt=ImageDraw.Draw(torso)
for i,im in enumerate(wholes):
 y0=255 if i==1 else 200;crop=im.crop((100,y0,420,y0+220)).resize((640,440),Image.Resampling.NEAREST);torso.paste(crop,(640*i,40),crop);dt.text((640*i+8,10),f'Phase{i} belt-anchored / uniform2x',font=FONT,fill='white')
save('presentation/Chest241-four-torso-belt-anchored-UNIFORM2x.png',torso)
controls=Image.new('RGB',(2560,488),(45,48,54));dc=ImageDraw.Draw(controls)
for col,(i,kind) in enumerate([(1,'belt'),(1,'best'),(2,'belt'),(2,'best')]):
 im=wholes[i] if kind=='belt' else best_wholes[i];y0=255 if i==1 else 200;crop=im.crop((100,y0,420,y0+220)).resize((640,440),Image.Resampling.NEAREST);controls.paste(crop,(640*col,40),crop);dc.text((640*col+8,10),f'Phase{i} {kind} / original owner / uniform2x',font=FONT,fill='white')
save('presentation/Chest241-phase12-belt-vs-best-UNIFORM2x.png',controls)
display=Image.new('RGBA',(1280,720),(45,48,54,255));dd=ImageDraw.Draw(display)
for i,im in enumerate(wholes):
 ground=(160+320*i,500);display=Image.alpha_composite(display,place(im,rows[i]['root_proposal'],ground,display.size));dd=ImageDraw.Draw(display);dd.text((320*i+32,535),f'Phase{i} body standing72',font=FONT,fill='white')
dd.text((24,24),'OFFLINE fixed 72/416 all4, own pairedshoe Root proposal / not native or footlock',font=FONT,fill='white')
save('presentation/Chest241-four-real72-groundregistered-OFFLINE.png',display.convert('RGB'))
contract=write('Chest241-original-owner-finite-review-contract-v001.json',{'schema':'Chest241-small-original-owner4-and-phase12-controls-v001','base240_original_owner':pin(BASE),'actual241_shared_receipt':pin(REC),'E508':pin(E508),'E502_reused_owners_armor_sword':pin(E502),'actual241_protection_failure_report':pin(MEAS),'actual241_two_point_feasibility':pin(FEAS),'new_source_QA_errors':rec['inspect_errors'],'new_source_QA_original_warnings':rec['inspect_warnings'],'numeric_thresholds_not_lowered':True,'raw_edit_protected0_3_RGBA_preservation_failed':not meas['protected_cells_pixel_preservation_pass'],'raw_neck_and_buckle_drift_retained':True,'old234_240_rejections_not_overturned':True,'new_curated_actual_View_after_E508':True,'all_new_composite_media_unviewed':True,'rows':rows,'unique_new_import_or_runtime_assets':0,'source_pixel_repairs':False,'new_native_calls':0,'TrialAllowed':False,'FinalAccepted':False,'verdict':'Review evidence only. Neither original exact-local-edit protection nor J/B exact geometry passed. Finite integer controls trade buckle alignment for sleeve alignment; no success inferred from reduced minimax residual.'})
write('HANDOFF.md','原218自身helmet-only五分区、Near235/Far236和Sword.50严格复用240原owner候选已保全源，排他RGBA重构逐像素相等。仅241Chest在512curated后做整数平移，无灰band/局部擦色/补内衬/整图缩放。4相为扣锚定；1/2额外best整数对照，不是可选修图。真实72展示全四以416→72常量及原pairedshoe作者Root定位，非native/足锁。原241保护0/3失败、扣与neck漂移、motionwarning与旧失败均保留。未准入，RootE后实际View可判可见接合，不能凭两点残差减小称成功。\n')
freeze=write('Chest241-original-owner-finite-review-freeze-v001.json',{'schema':'Chest241-finite-review-freeze-v001','script':pin(Path(__file__)),'files':[pin(p) for p in sorted(OUT.rglob('*')) if p.is_file()],'newmedia_View':False,'TrialAllowed':False})
(MEDIA/'原件').mkdir(parents=True);shutil.copytree(OUT,MEDIA/'原件/有限源配准完整包');shutil.copyfile(Path(__file__),MEDIA/'原件'/Path(__file__).name);(MEDIA/'展示副本').mkdir()
for p in sorted((OUT/'presentation').glob('*.png')):shutil.copyfile(p,MEDIA/'展示副本'/p.name)
index={'date':'2026-10-18','topic':'钟盔Dodge胸衣241原分区有限配准与真实72展示','version':'v001','status':'Unviewed newreview, exactedit/geometry acceptance closed, RootE before View','contract':pin(contract),'freeze':pin(freeze),'files':[pin(p) for p in sorted(MEDIA.rglob('*')) if p.is_file()]}
with (MEDIA/'来源-版本-状态索引.json').open('x',encoding='utf-8',newline='\n') as f:json.dump(index,f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps({'canonical_F_media':MEDIA.as_posix(),'files':sum(p.is_file() for p in MEDIA.rglob('*')),'bytes':sum(p.stat().st_size for p in MEDIA.rglob('*') if p.is_file()),'contract':pin(contract),'freeze':pin(freeze),'newmedia_View':False,'rows':[{k:r[k] for k in ['frame','belt_anchored','best_integer_control'] if k in r} for r in rows]},ensure_ascii=False,indent=2))
