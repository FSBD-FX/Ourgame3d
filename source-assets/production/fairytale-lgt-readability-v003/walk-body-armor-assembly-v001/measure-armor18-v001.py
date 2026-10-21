"""Observed source512 armor A/B and old-body ownership trials; source art is read-only."""
from pathlib import Path
from datetime import datetime
import hashlib,json,shutil
import numpy as np
from PIL import Image,ImageDraw,ImageFont

ROOT=Path('F:/Ourgame');HERE=Path(__file__).resolve().parent;OUT=HERE/'2026-10-18-armor18-fit-phase-a-v001'
OLD=ROOT/'source-assets/production/fairytale-hero-v001/sprite-run-walk-v008/curated'
SOURCE_INDEX=ROOT/'source-assets/production/fairytale-lgt-readability-v003/walk-far201-min256-v002/walk-eighteen-source-index-v002.json'
GUIDE=ROOT/'source-assets/production/fairytale-lgt-readability-v003/walk-body-layers-v001/old-nearhand-guide-v002'

# Feature-matched artist design points, measured on retained source512; NOT bones.
AA={'Chest':[[268,279]]*6,'NearShoulder':[[251,252]]*6,'FarShoulder':[[255,254]]*6}
BB={'Chest':[[274,307],[269,311],[270,306],[271,317],[275,312],[274,311]],
 'NearShoulder':[[210,250],[214,257],[244,257],[244,260],[211,258],[209,251]],
 'FarShoulder':[[291,258],[290,262],[205,254],[201,259],[292,262],[294,261]]}
ARMS=[
 [[223,231],[232,237],[235,249],[228,263],[211,273],[195,281],[183,296],[175,304],[149,289],[155,272],[170,253],[191,239],[207,232]],
 [[220,241],[231,246],[235,256],[230,268],[214,284],[201,306],[155,309],[158,289],[170,270],[183,253],[202,244]],
 [[234,237],[248,237],[263,246],[275,261],[283,270],[298,278],[315,284],[303,321],[285,319],[270,309],[257,300],[244,290],[233,278],[222,262],[223,249]],
 [[234,241],[249,241],[264,248],[276,260],[288,272],[303,277],[331,282],[318,324],[298,323],[279,317],[260,305],[244,295],[231,280],[220,263],[222,250]],
 [[223,242],[232,248],[235,258],[229,274],[215,289],[207,309],[160,313],[165,291],[173,270],[189,252],[207,244]],
 [[224,237],[234,243],[237,254],[229,267],[210,281],[195,300],[183,308],[148,300],[151,281],[164,262],[184,248],[207,238]]]
# Lower-rim source ownership contours. Empty outer area is harmless; live pixels stay exact.
RIMS=[
 [[173,204],[191,212],[207,218],[230,222],[259,228],[279,232],[300,235],[320,236],[333,234],[340,230]],
 [[174,214],[192,220],[212,225],[238,230],[260,236],[282,240],[306,242],[324,241],[337,237],[340,233]],
 [[173,210],[191,216],[216,221],[242,226],[262,232],[286,237],[308,239],[325,238],[338,234]],
 [[174,210],[191,216],[216,222],[241,227],[261,233],[282,238],[304,241],[324,240],[337,235]],
 [[174,214],[193,220],[216,225],[239,230],[260,236],[281,240],[304,242],[324,241],[337,237]],
 [[175,212],[191,217],[213,223],[239,229],[261,235],[284,239],[305,240],[325,239],[340,235]]]

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
def sample(a,q):return {'point_source512':q,'actual_RGBA':a[q[1],q[0]].tolist(),'alpha_is_visible':bool(a[q[1],q[0],3]>0)}
def owned(a,m):
 out=np.zeros_like(a);out[m]=a[m];return out

OUT.mkdir(exist_ok=False);font=ImageFont.load_default(size=13);index=json.loads(SOURCE_INDEX.read_text(encoding='utf-8'))
sources=[pin(SOURCE_INDEX)];armor={};observations=[];originals=[];bodyobs=[];layers={};composites=[]
for component in index['components']:
 part=component['component'];armor[part]=[]
 for f in component['frames']:
  i=f['frame'];p=Path(f['source']['path']);assert pin(p)==f['source'];sources.append(pin(p))
  a=np.asarray(Image.open(p)).copy();op=OLD/f'frame-{i}.png';old=np.asarray(Image.open(op)).copy()
  qA=AA[part][i];qB=BB[part][i];delta=[qB[0]-qA[0],qB[1]-qA[1]];out=shift(a,delta)
  outp=save(f'adjusted-armor18/{part}/frame-{i}.png',out);armor[part].append(out)
  # Reverse integer shift confirms every RGBA input byte survives, including transparent RGB.
  reverse=shift(out,[-delta[0],-delta[1]]);assert np.array_equal(a,reverse)
  role={'Chest':'visible belt buckle center / keeps pouch on source physical side','NearShoulder':'visible crown area of near cap / actual foreground shoulder chain','FarShoulder':'visible face of far cap / actual far shoulder chain'}[part]
  observations.append({'component':part,'frame':i,'native_request':component['native_request'],'source':pin(p),'A_visible_feature_artist_design':sample(a,qA),'B_matching_body_feature_artist_design':sample(old,qB),'feature_role':role,'integer_delta_xy':delta,'output':pin(outp),'all_RGBA_reverse_translation_mismatch_pixels':0,'resampled':False,'mirrored':False,'rotated':False,'pouch_side_unchanged':True,'actual_hidden_joint':None,'semantic_A_B_uncertainty_source_px':3,'accepted':False})
for i in range(6):
 p=OLD/f'frame-{i}.png';sources.append(pin(p));old=np.asarray(Image.open(p)).copy()
 mp=GUIDE/'old-nearhand-mask'/f'frame-{i}.png';sources.append(pin(mp));hm=np.asarray(Image.open(mp))>0
 rim=RIMS[i];hp=[[0,0],[512,0],[512,rim[-1][1]]]+list(reversed(rim))+[[0,rim[0][1]]]
 helmet=poly(hp)&~hm;arm=poly(ARMS[i])&~hm&~helmet;rest=~hm&~helmet&~arm
 masks={'BodyRest':rest,'NearArmWithoutHand':arm,'HelmetForeground':helmet,'NearHand':hm}
 owns={name:owned(old,m) for name,m in masks.items()};sumrgba=sum(a.astype(np.uint16) for a in owns.values())
 assert np.array_equal(sumrgba,old.astype(np.uint16));assert all(int((masks[a]&masks[b]).sum())==0 for a in masks for b in masks if a<b)
 for name,a in owns.items():save(f'oldbody-ownership-TRIAL/{name}/frame-{i}.png',a)
 save(f'ownership-masks/NearArmWithoutHand/frame-{i}.png',(arm*255).astype(np.uint8));save(f'ownership-masks/HelmetForeground/frame-{i}.png',(helmet*255).astype(np.uint8))
 layers[i]=owns
 # Preview has the ORIGINAL OPEN HANDS: geometry and layer order trial only.
 stack=[owns['BodyRest'],armor['FarShoulder'][i],armor['Chest'][i],owns['NearArmWithoutHand'],armor['NearShoulder'][i],owns['HelmetForeground'],owns['NearHand']]
 whole=np.zeros_like(old)
 for a in stack:whole=over(whole,a)
 cp=save(f'noSword-OLD-HAND-diagnostic/frame-{i}.png',whole);composites.append(whole)
 bodyobs.append({'frame':i,'source':pin(p),'new_near_arm_polygon_candidate':ARMS[i],'helmet_lower_rim_polyline_candidate':RIMS[i],'helmet_foreground_polygon_candidate':hp,'mask_uncertainty_source_px':2,'actual_hidden_shoulder_or_wrist_bone':None,'oldbody_fourlayers_reconstruction_RGBA_mismatch_pixels':0,'exclusive_mask_pair_intersection_count':0,'old_open_hand_intentionally_present':True,'not_final_closed_hand_import':True,'diagnostic_composite':pin(cp),'semantic_ownership_accepted':False})
 # Full-res overlay plus actual source points; this is measurement media, not new art.
 canvas=Image.new('RGBA',(608,608),(27,29,32,255));canvas.alpha_composite(Image.fromarray(old),(48,48));draw=ImageDraw.Draw(canvas)
 for k in range(0,513,32):
  draw.line([(48+k,48),(48+k,560)],fill=(60,200,210,75),width=1);draw.line([(48,48+k),(560,48+k)],fill=(60,200,210,75),width=1)
  if k%64==0:draw.text((38+k,29),str(k),fill='white',font=font);draw.text((12,41+k),str(k),fill='white',font=font)
 draw.line([(q[0]+48,q[1]+48) for q in ARMS[i]+[ARMS[i][0]]],fill=(255,110,80,255),width=1)
 draw.line([(q[0]+48,q[1]+48) for q in RIMS[i]],fill=(255,230,80,255),width=1)
 for part,color in [('Chest',(255,200,80,255)),('NearShoulder',(100,255,140,255)),('FarShoulder',(100,190,255,255))]:
  x,y=BB[part][i];draw.ellipse((x+45,y+45,x+51,y+51),outline=color,width=1);draw.text((x+52,y+43),part,fill=color,font=font)
 draw.text((48,7),f'BODY {i} | new ownership and armor B TRIAL',fill='white',font=font)
 draw.text((48,578),'source xy = shown -48; approximate visible features, NOT bones.',fill='white',font=font)
 originals.append(save(f'原件/body-{i}-ownership-armor-B-grid-v001.png',np.asarray(canvas)))
contact=np.zeros((1024,1536,4),np.uint8)
for i,a in enumerate(composites):contact[(i//3)*512:(i//3+1)*512,(i%3)*512:(i%3+1)*512]=a
originals.append(save('原件/noSword-six-OLD-OPEN-HAND-diagnostic-UNSCALED-v001.png',contact))
for part in armor:
 contact=np.zeros((512,3072,4),np.uint8)
 for i,a in enumerate(armor[part]):contact[:,512*i:512*(i+1)]=a
 originals.append(save(f'原件/adjusted-{part}-six-UNSCALED-v001.png',contact))
for p in originals:
 q=OUT/'展示副本'/p.name;q.parent.mkdir(exist_ok=True);shutil.copyfile(p,q);assert pin(q)['sha256']==pin(p)['sha256']
for s in sources:assert pin(Path(s['path']))==s
report=write('armor18-visible-A-B-integer-trial-proof-v001.json',{'schema':'Walk199-200-201-armor18-actual-visible-AB-TRIAL-v001','created_local':datetime.now().astimezone().isoformat(),'source_view_authorization':'Root E336 all armor18 retained 2SHA0; oldbody E319 sources reviewed at original detail.','source_pins':sources,'armor18':observations,'body6_ownership_candidates':bodyobs,'stack_order_back_to_front':['BodyRest','FarShoulder','Chest','NearArmWithoutHand','NearShoulder','HelmetForeground','NearHand'],'source_scale_policy':'Frozen existing shared HD; far201 explicit min256 retained. No new resampling.','physical_pouch_side':'source left side maintained for all6; no phase flip','fit_accepted':False,'native205_closed_hand_pending':True,'old_hand_preview_warning':'Six current diagnostic composites use OLD OPEN hands; not the six closed-hand product or import.','new_outputs_viewed':False})
write('HANDOFF.md','Armor18 candidates use only integer translation, with actual visible feature A/B samples and exact reverse-RGBA proofs. Physical pouch side and near/far shoulder chain are preserved. Four exclusive old-body ownership layers close oldBody byte-exact, but semantic borders remain +/-2px TRIAL. Six diagnostic composites deliberately retain ORIGINAL OPEN hands; final closed-hand Body6 layers/import await native205 and review of 204 fist width. New media are unviewed; retain originals and presentation copies to E before View.\n')
write('source-version-status-index-v001.json',{'date':'2026-10-18','topic':'walk-armor18-AB-ownership','version':'phase-a-v001','status':'TRIAL-unviewed-not-imported','originals':[pin(p) for p in originals],'presentation':[pin(OUT/'展示副本'/p.name) for p in originals],'report':pin(report),'all_sources_unchanged':True,'files':[pin(p) for p in sorted(OUT.rglob('*')) if p.is_file()]})
print(json.dumps({'out':OUT.as_posix(),'adjusted_armor_pngs':18,'oldbody_ownership_trial_pngs':24,'old_open_hand_diagnostic_composites':6,'report':pin(report),'new_outputs_viewed':False},ensure_ascii=False,indent=2))
