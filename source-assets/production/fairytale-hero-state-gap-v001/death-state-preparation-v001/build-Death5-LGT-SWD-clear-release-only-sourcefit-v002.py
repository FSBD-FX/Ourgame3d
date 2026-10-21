"""Five finite author fits using exact Death220 owners and actual237/238/239.

Armor is integer translated, never repainted/rescaled/rotated. Sword is the
existing independent source rendered with an explicit visual-release transform.
All new media must be retained by Root on E before View. No runtime acceptance.
"""
from pathlib import Path
import json,hashlib,math,shutil,sys
import numpy as np
from PIL import Image,ImageDraw,ImageFont
C=Path(__file__).resolve().parent;ROOT=Path('F:/Ourgame')
BODY=C/'candidate-v004-late-owner-semantic-correction'
O=C/'LGT237-239-Death5-limited-integer-sourcefit-v002'
F=ROOT/'过程图稿与视频/2026-10-18_钟盔Death220三甲原40不变与清楚离掌落剑试拼_v002'
PY=Path('C:/Users/22499/.codex/skills/sprite-gen/.venv/Scripts/python.exe')
OWNERS=['BodyRest','NearArmWithoutHand','HelmetForeground','FarHandForeground','NearHand']
GEAR={'Chest':237,'ShoulderNear':238,'ShoulderFar':239}
MOUNTS={
 'Chest':{'A':[[263,287],[261,270],[245,270],[260,269],[260,275]],'B':[[254,299],[275,302],[237,338],[241,361],[234,372]],'role':['visible original belt material sample','visible gray torso surface','visible gray back/torso surface','visible gray torso surface','visible gray torso surface']},
 'ShoulderNear':{'A':[[250,252],[250,253],[250,260],[250,265],[250,269]],'B':[[201,232],[220,251],[249,324],[230,355],[225,365]],'role':['visible near upper-arm graycloth sample']*5},
 'ShoulderFar':{'A':[[253,249],[253,252],[253,257],[253,261],[253,265]],'B':[[298,259],[322,322],[334,378],[380,400],[375,400]],'role':['visible far-arm graycloth sample','visible far-arm graycloth sample','visible far-arm cloth/ink edge sample','hidden attachment unknown; explicit artist placement behind helmet only','hidden attachment unknown; explicit artist placement behind helmet only']}}
def pin(p):
 p=Path(p).resolve();b=p.read_bytes();return dict(path=p.as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p,v):
 assert not p.exists(),str(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(v if isinstance(v,str)else json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def save(p,im):
 assert not p.exists(),str(p);p.parent.mkdir(parents=True,exist_ok=True);im.save(p)
def bbox(m):
 y,x=np.where(m);return [int(x.min()),int(y.min()),int(x.max()+1),int(y.max()+1)]if len(x)else None
def translate(a,d):
 dx,dy=d;out=np.zeros_like(a);sx0=max(0,-dx);sx1=min(512,512-dx);sy0=max(0,-dy);sy1=min(512,512-dy)
 out[sy0+dy:sy1+dy,sx0+dx:sx1+dx]=a[sy0:sy1,sx0:sx1]
 back=np.zeros_like(a);back[sy0:sy1,sx0:sx1]=out[sy0+dy:sy1+dy,sx0+dx:sx1+dx]
 assert np.array_equal(back,a),'Integer translation clipped original component RGBA'
 return out
def pad(im):
 out=Image.new('RGBA',(1024,1024));out.paste(im,(256,256));return out
def sword_rigid(sword,anchor,deg):
 # Author renderer preview only; original512 source remains the runtime texture.
 # One premultiplied-alpha affine, fixed.50 and full1024 frame to avoid clipping.
 angle=math.radians(deg);c=math.cos(angle);s=math.sin(angle);scale=.50;gx,gy=anchor[0]+256,anchor[1]+256
 aff=(c/scale,s/scale,99-(c*gx+s*gy)/scale,-s/scale,c/scale,256+(s*gx-c*gy)/scale)
 return sword.convert('RGBa').transform((1024,1024),Image.Transform.AFFINE,aff,resample=Image.Resampling.BICUBIC).convert('RGBA')
def actual_scale(im,ground=(640,490)):
 k=72/416;rx,ry=242+256,464+256;gx,gy=ground
 aff=(1/k,0,rx-gx/k,0,1/k,ry-gy/k)
 return im.convert('RGBa').transform((1280,720),Image.Transform.AFFINE,aff,resample=Image.Resampling.BICUBIC).convert('RGBA')
def main():
 assert Path(sys.executable).resolve()==PY.resolve();assert not O.exists()and not F.exists();O.mkdir()
 body=read(BODY/'Death220-late-visible-owner-correction-v004.json')
 for row in read(BODY/'source-layer-freeze-v004.json')['files']:assert pin(row['path'])==row
 release=read(C/'candidate-v001/Death220-exclusive-owners-registration-and-released-SWD-proposal-v001.json');swordsrc=Path(release['weapon_source']['F']['path']);assert pin(swordsrc)==release['weapon_source']['F'];sword=Image.open(swordsrc).convert('RGBA')
 before=[];qareports=[]
 for name,n in GEAR.items():
  run=C/f'process-runs-v001/run-Death5-{name}-native{n}-shared-HD-v001';receipt=read(run/'extraction-receipt-v001.json');assert len(receipt['commands'])==5 and all(x['exit_code']==0 for x in receipt['commands'])
  assert receipt['shared_row_fit']['per_frame_scale_normalization']is False
  qareports.append({'component':name,'receipt':pin(run/'extraction-receipt-v001.json'),'official_original_QA':pin(run/'sprite-inspect.report.json'),'warnings_unchanged':read(run/'sprite-inspect.report.json')['warnings'],'warning_threshold_changed':False})
  for x in receipt['frames']:assert pin(x['source']['path'])==x['source'];before.append(x['source'])
 rows=[];wholes=[];actual=[];font=lambda n:ImageFont.truetype('C:/Windows/Fonts/arial.ttf',n)
 for i,br in enumerate(body['rows']):
  source=Path(br['source']['path']);assert pin(source)==br['source'];a=np.asarray(Image.open(source).convert('RGBA'));alpha=a[:,:,3]>0;layers={};bp=[];gearunion=np.zeros((512,512),bool)
  for x in br['layers']:
   p=Path(x['source_RGBA_layer']['path']);assert pin(p)==x['source_RGBA_layer'];im=Image.open(p).convert('RGBA');arr=np.asarray(im);layers[x['owner']]=pad(im);target=O/f'body-layers/{x["owner"]}/frame-{i}.png';target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,target);assert pin(target)['sha256']==pin(p)['sha256'];bp.append({'owner':x['owner'],'source':pin(p),'sourcefit_layer':pin(target),'body_RGBA_byte_exact':True})
  reconstruction=Image.new('RGBA',(512,512))
  for n in OWNERS:reconstruction=Image.alpha_composite(reconstruction,layers[n].crop((256,256,768,768)))
  assert np.array_equal(np.asarray(reconstruction),a),'All body source pixels must survive their own partition'
  mounts=[]
  for name,num in GEAR.items():
   sourcegear=C/f'process-runs-v001/run-Death5-{name}-native{num}-shared-HD-v001/curated/frame-{i}.png';ga=np.asarray(Image.open(sourcegear).convert('RGBA'));A=MOUNTS[name]['A'][i];B=MOUNTS[name]['B'][i];assert ga[A[1],A[0],3]>=128
   hidden=name=='ShoulderFar'and i>=3
   if not hidden:assert a[B[1],B[0],3]>=128
   delta=[B[0]-A[0],B[1]-A[1]];shifted=translate(ga,delta);layers[name]=pad(Image.fromarray(shifted));dest=O/f'armor-layers/{name}/frame-{i}.png';save(dest,Image.fromarray(shifted));gearunion|=shifted[:,:,3]>0
   mounts.append({'component':name,'source':pin(sourcegear),'A_actual_material_pixel':A,'A_RGBA':ga[A[1],A[0]].tolist(),'B_visible_body_pixel':None if hidden else B,'B_RGBA':None if hidden else a[B[1],B[0]].tolist(),'B_role':MOUNTS[name]['role'][i],'author_target_for_translation':B,'integer_delta':delta,'translated_layer':pin(dest),'translated_bbox':bbox(shifted[:,:,3]>0),'reversible_RGBA_exact':True,'scale':1,'local_rotation_or_repaint':False,'actual_hidden_attachment':None,'visible_landmark_author_uncertainty_px':3,'core_over_source_body':int(np.count_nonzero((shifted[:,:,3]>=128)&(a[:,:,3]>=128))),'core_outside_source_body':int(np.count_nonzero((shifted[:,:,3]>=128)&(a[:,:,3]<128))),'sourcefit_accepted':False})
  sr=release['rows'][i];anchor=[[183.,311.],[296.,430.],[480.,442.],[480.,442.],[480.,442.]][i];angle=[-20.,0.,0.,0.,0.][i];swd=sword_rigid(sword,anchor,angle);layers['IndependentSword']=swd;save(O/f'weapon-preview-only/visual-release-{i}-1024.png',swd)
  base=['BodyRest','ShoulderFar','Chest','NearArmWithoutHand','ShoulderNear','HelmetForeground','FarHandForeground','NearHand']
  stack=base[:-1]+['IndependentSword','NearHand']if i==0 else ['IndependentSword']+base
  whole=Image.new('RGBA',(1024,1024))
  for name in stack:whole=Image.alpha_composite(whole,layers[name])
  wa=np.asarray(whole.crop((256,256,768,768)));su=np.asarray(swd.crop((256,256,768,768)))[:,:,3]>0;outside=alpha&~(gearunion|su);assert np.array_equal(wa[outside],a[outside]),'Uncovered body source pixels must remain unchanged'
  # Ground-sword presentation can extend beyond the body's512canvas:768is only
  # a preview surface; no cropped sword texture or enlarged body is imported.
  wp=O/f'whole-preview-only/Death-{i}-LGT237-239-SWD-1024.png';save(wp,whole);wholes.append(whole)
  bg=Image.new('RGBA',(1280,720),(34,37,43,255));bg=Image.alpha_composite(bg,actual_scale(whole));d=ImageDraw.Draw(bg);d.text((24,20),f'OFFLINE AUTHOR Death{i} / body220 + Chest237 Near238 Far239 + independent SWD .50',font=font(21),fill='white');d.text((24,54),'Standing72/416 fixed scale; no late-frame enlargement; Root/contact/hidden attachment not measured.',font=font(19),fill='white');d.line((500,490,800,490),fill=(85,89,97),width=1);view=bg.convert('RGB');save(O/f'preview-frames/actual-scale-{i:03d}.png',view);actual.append(view)
  bodymark=Image.fromarray(a.copy());d=ImageDraw.Draw(bodymark)
  for m in mounts:
   B=m['B_visible_body_pixel']
   if B is not None:d.ellipse((B[0]-3,B[1]-3,B[0]+3,B[1]+3),outline=(0,230,255,255),width=2)
  save(O/f'diagnostics/frame-{i}-visible-B-author-marks.png',bodymark)
  rows.append({'frame':i,'nominal_key_age_s':i*.2,'body_source':br['source'],'body_partition':bp,'all_body_pixels_reconstruct_original_RGBA':True,'visible_body_outside_gear_and_weapon_RGBA_exact':True,'no_source_body_erased':True,'armor_mounts':mounts,'stack_bottom_to_top':stack,'known_empty_slots':[],'ground_root_author_proposal':[242,464],'physical_root_or_footlock_measured':False,'actual_hand_contact_grip':None,'actual_hidden_axis':None,'Sword_source':pin(swordsrc),'Sword_scale':.50,'Sword_visual_anchor_author_xy':anchor,'Sword_clockwise_y_down_degrees':angle,'Sword_direction_author_axis':[math.cos(math.radians(angle)),math.sin(math.radians(angle))],'Sword_visual_release':i>=1,'Sword_inventory_or_gameplay_drop_changed':False,'body_and_armor_scale_per_frame':1,'whole_diagnostic_preview':pin(wp),'native_accepted':False,'semantic_fit_accepted':False})
 plate=Image.new('RGBA',(5120,1090),(34,37,43,255));d=ImageDraw.Draw(plate)
 for i,im in enumerate(wholes):plate.alpha_composite(im,(i*1024,45));d.text((i*1024+12,10),f'Death{i} / OWN source + three armor / visual Sword',font=font(21),fill='white')
 save(O/'presentation/Death5-LGT-SWD-all-full-preview-UNVIEWED.png',plate.convert('RGB'))
 close=Image.new('RGBA',(3500,590),(34,37,43,255));d=ImageDraw.Draw(close)
 for i,im in enumerate(wholes):
  crop=im.crop((376,436,726,696)).resize((700,520),Image.Resampling.NEAREST);close.alpha_composite(crop,(i*700,45));d.text((i*700+10,10),f'Death{i} own body/armor x2 diagnostic',font=font(20),fill='white')
 save(O/'presentation/Death5-torso-layer-boundaries-2x-nearest-UNVIEWED.png',close.convert('RGB'))
 gp=O/'presentation/Death5-LGT-SWD-finite-nominal1000ms-NOLOOP-offline.gif';actual[0].save(gp,save_all=True,append_images=actual[1:],duration=[200]*5,disposal=2,optimize=False)
 with Image.open(gp)as check:
  ds=[]
  for i in range(check.n_frames):check.seek(i);ds.append(check.info['duration'])
  assert check.n_frames==5 and ds==[200]*5 and'loop'not in check.info
 contract=O/'Death220-LGT237-239-five-integer-mounts-and-visual-release-author-contract-v002.json'
 write(contract,dict(schema='Death220-LGT237-239-clear-release-sourcefit-v002',body_source_partition=pin(BODY/'source-layer-freeze-v004.json'),body_partition_semantic_review='v004 actually Viewed after E497, limited author-source candidate only; v005 separate sleeve correction is deliberately not applied in this release-only v002',official_armor_before_View=pin(C/'actual-raw-admissions-v001/curated15-E489-E490-E492-before-View-two-pass-v001.json'),all15_armor_curated_actually_Viewed_after_E=True,all_original_QA_warnings_retained=qareports,body_source_textures=25,armor_source_textures=15,independent_reused_Sword_textures=1,noWholeBody_as_BodyRest=True,body_canvas=[512,512],preview_canvas=[1024,1024],preview_padding_only=[256,256],body_standing_source_height=416,body_standing_display_height=72,no_perframe_alpha_height_normalization=True,armor_all_integer_translation_only=True,actual_armor_mounts_or_contact_measured=False,actual_hidden_bones_or_axes=None,inventory_or_gameplay_equipment_drop=False,weapon_pickup_entity_or_damage_or_collision_added=False,framekeys_s=[0,.2,.4,.6,.8],last_frame4_hold='Runtime proposal from.8 until actual Death state exit; no added gameplay deadline. OfflineGIF ends after one nominal1s sequence, not native death duration.',rows=rows,explicit_risks=['Whole generated Chest perspective may not fit actual collapsed body through integer translation; actualsource torso coverage/pouch/belt/neckline must be reviewed, no gray-body erasure workaround.','Far3/4 shoulder is hidden: actualattachment null; proposed tab is behind actualHelmet only, not a measured socket.','v004 is only a limited source candidate; separate sleeve-owner diagnostic v005 remains independent and is not silently applied in this40unchanged release-only v002.','Initial Sword near relaxed hand and release trajectory are author-only; no truehiltcontact/physicalfloor/noPop proof.','Endpoint still source-only; inventory persists logically and no collectible or damage entity is made.'],newmedia_Viewed=False,sourcefit_accepted=False,TrialAllowed=False,FinalAccepted=False,Source_Content_tools_tests_ledger_UE_modified=False))
 write(O/'HANDOFF.md','Five finite exact-source fits, not native or accepted art. Body25 own layers reconstruct source220; no hidden torso erasure. Armor237/238/239 official shared-row sources use15 reversible integer translations only; original3 motion warnings retained. Body512 scale72/416 fixed all5. Independent originalSword uses constant.50 visual-release author transform, full1024 diagnostic canvas avoids blade clipping; originalruntime sword texture unchanged. Near-hand/Helmet latev004 is unviewed at preparation and still requires actual E/View. Far3/4 actualshoulder/Grip/hiddenAxis/physicalRoot remain null; author placement behindHelmet is explicit. Five full previews, torso boundaries, actualscale5 and nominal1s nonloop GIF are NEW F beforeE/View. No Source/Content/tests/tools/ledger/UE writes, no AI calls.\n')
 oldfit=C/'LGT237-239-Death5-limited-integer-sourcefit-v001';same40=[]
 for sub in ['body-layers','armor-layers']:
  for oldfile in sorted((oldfit/sub).rglob('*.png')):
   newfile=O/oldfile.relative_to(oldfit);assert pin(oldfile)['sha256']==pin(newfile)['sha256'];same40.append({'old':pin(oldfile),'new':pin(newfile),'bytes_unchanged':True})
 assert len(same40)==40
 write(O/'original40-RGBA-unchanged-release-only-proof-v002.json',dict(schema='Death5-original40-byteidentity-clear-release-v002',old_sourcefit=pin(oldfit/'sourcefit-candidate-freeze-v001.json'),source40=same40,change_scope='Only explicit author Sword anchor/angle and preview padding1024; original25body+15armorRGBA bytes unchanged. No sourceBodyScale/armor/stock/gameplay changes.',author_anchors=[[183,311],[296,430],[480,442],[480,442],[480,442]],author_angles=[-20,0,0,0,0],physical_contact_or_socket_or_floor=None))
 write(O/'sourcefit-candidate-freeze-v002.json',dict(script=pin(Path(__file__)),files=[pin(p)for p in sorted(O.rglob('*'))if p.is_file()],newmedia_Viewed=False,TrialAllowed=False))
 orig=F/'原件/Death5完整源试拼候选';orig.parent.mkdir(parents=True);shutil.copytree(O,orig);show=F/'展示副本';show.mkdir()
 for p in sorted((O/'presentation').iterdir()):shutil.copy2(p,show/p.name)
 shutil.copytree(O/'preview-frames',show/'actual-scale-1280')
 write(F/'README.md','Death5 body220+actualLGT237-239+independentSword limited author fit. Original components/QA kept, no body erasure/rescale. NEW previews UNVIEWED awaiting RootE beforeView. Sourcefit/Grip/ground/native not accepted.\n')
 write(F/'source-version-status-index.json',dict(schema='Death5-LGT-SWD-clear-release-F-index-v002',status='UNVIEWED_AWAIT_ROOT_E_GATE',candidate=O.as_posix(),files=[pin(p)for p in sorted(F.rglob('*'))if p.is_file()],TrialAllowed=False))
 print(json.dumps(dict(candidate=O.as_posix(),freeze=pin(O/'sourcefit-candidate-freeze-v002.json'),F_canonical=F.as_posix(),F_files=len([p for p in F.rglob('*')if p.is_file()]),F_bytes=sum(p.stat().st_size for p in F.rglob('*')if p.is_file()),newmedia_Viewed=False,TrialAllowed=False),ensure_ascii=False))
if __name__=='__main__':main()
