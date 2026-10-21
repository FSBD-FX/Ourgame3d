from pathlib import Path
import hashlib,json,shutil,subprocess,re,sys
import numpy as np
from PIL import Image,ImageDraw,ImageFont,ImageFilter

ROOT=Path('F:/Ourgame');BASE=ROOT/'source-assets/production/fairytale-hero-state-gap-v001';HERE=Path(__file__).resolve().parent
OUT=HERE/'candidate-v001';MEDIA=ROOT/'过程图稿与视频/2026-10-18_钟盔Hurt227棕皮三层与军剑四相整数试装_v001'
SG=Path('C:/Users/22499/.codex/skills/sprite-gen');PY=SG/'.venv/Scripts/python.exe'
SWD=BASE/'hurt227-SWD-four-fit-v002/candidate-v002'
LEATHER=BASE/'lgt-hurt4-process-runs-v001/process-inputs-v001/runs'
FAR=BASE/'lgt-hurt4-far231-extraction-v001/run-Hurt4-far-native231-shared-HD-v001'
READY=ROOT/'source-assets/production/fairytale-lgt-readability-v003/ready-integer-assembly-v001'
CANVAS=72.*512./416.;K=CANVAS/512.
OWNERS=['BodyRest','NearArmWithoutHand','HelmetForeground','FarHandForeground','NearHand']
STACK=['BodyRest','ShoulderFar','Chest','NearArmWithoutHand','ShoulderNear','HelmetForeground','FarHandForeground','SWD','NearHand']
NEARARM=[[[171,235],[186,228],[204,232],[218,247],[213,264],[217,279],[211,292],[209,310],[197,326],[180,326],[170,317],[162,304],[155,287],[154,269],[159,249]],[[130,268],[143,260],[161,262],[176,267],[184,277],[180,290],[175,304],[166,315],[153,316],[142,313],[132,306],[128,293]],[[148,253],[160,249],[177,250],[190,259],[197,269],[190,280],[180,289],[176,301],[165,308],[153,304],[146,294],[141,280],[141,266]],[[186,228],[201,223],[218,228],[227,242],[219,256],[207,270],[202,287],[191,297],[186,311],[175,313],[166,304],[159,290],[158,275],[164,256]]]
HELMET=[[[180,90],[385,90],[385,294],[338,294],[314,285],[290,278],[269,267],[253,252],[234,238],[213,222],[197,208],[185,197]],[[95,60],[300,60],[309,224],[287,228],[264,215],[240,221],[216,230],[190,246],[153,264],[116,275],[107,256]],[[175,85],[375,85],[385,275],[346,280],[322,270],[301,258],[278,247],[257,236],[233,227],[211,210],[191,189],[179,176]],[[155,35],[351,35],[352,229],[324,235],[302,230],[276,224],[246,218],[218,214],[190,210],[166,203]]]
FARHAND0=[[270,295],[282,288],[292,290],[300,297],[306,307],[308,320],[302,328],[291,336],[278,336],[269,331],[263,322],[259,310],[263,300]]
MOUNTS={
 'Chest':{'A':[[270,246],[274,268],[263,280],[265,282]],'B':[[282,283],[290,273],[242,306],[264,303]],'A_role':['visible upper gold fastening','visible belt buckle surface','visible belt buckle surface','visible belt buckle surface'],'B_role':['visible gray torso below helmet (far buckle hidden by hands)','visible existing belt buckle surface','visible existing belt buckle surface','visible existing belt buckle surface']},
 'ShoulderNear':{'A':[[247,258]]*4,'B':[[194,248],[154,264],[179,243],[203,244]],'A_role':['visible curved inner leather surface; author surface landmark']*4,'B_role':['visible near upper-arm gray cloth surface']*4},
 'ShoulderFar':{'A':[[251,250],[251,249],[251,250],[253,248]],'B':[[314,290],[291,228],[308,283],[304,267]],'A_role':['visible upper inner thin-tab surface']*4,'B_role':['visible far arm ink/cloth seam','visible far shoulder gray cloth','visible far arm ink/cloth seam','visible far shoulder gray cloth']}}
def pin(p):
 b=p.read_bytes();return {'path':p.as_posix(),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def write(rel,v):
 p=OUT/rel;assert not p.exists(),str(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(v if isinstance(v,str) else json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');return p
def save(rel,im):
 p=OUT/rel;assert not p.exists();p.parent.mkdir(parents=True,exist_ok=True);im.save(p);return p
def bbox(m):
 y,x=np.where(m);return None if not len(x) else [int(x.min()),int(y.min()),int(x.max()+1),int(y.max()+1)]
def poly(p):
 im=Image.new('L',(512,512));ImageDraw.Draw(im).polygon(list(map(tuple,p)),fill=255);return np.array(im)>0
def fillholes(m):
 im=Image.fromarray(np.where(m,255,0).astype(np.uint8));ImageDraw.floodfill(im,(0,0),128);a=np.array(im);return (a==255)|(a==0)
def compose(layers):
 im=Image.new('RGBA',(512,512))
 for name in STACK:im=Image.alpha_composite(im,Image.fromarray(layers[name]))
 return im
def translate(a,delta):
 dx,dy=delta;b=np.zeros_like(a);sx0=max(0,-dx);sx1=min(512,512-dx);sy0=max(0,-dy);sy1=min(512,512-dy)
 b[sy0+dy:sy1+dy,sx0+dx:sx1+dx]=a[sy0:sy1,sx0:sx1]
 restored=np.zeros_like(a);restored[sy0:sy1,sx0:sx1]=b[sy0+dy:sy1+dy,sx0+dx:sx1+dx]
 assert np.array_equal(restored,a),'Integer translation lost source RGBA'
 return b
def place(im,root,size=(1280,720),ground=(640,490),k=K):
 aff=(1/k,0.,root[0]-ground[0]/k,0.,1/k,root[1]-ground[1]/k)
 return im.convert('RGBa').transform(size,Image.Transform.AFFINE,aff,resample=Image.Resampling.BICUBIC).convert('RGBA')
def exactE(p,version):
 ep=next(Path('E:/OurGame/Knight/过程图稿与视频').glob(f'*v{version}/source-size-SHA256.json'));matches=[];sha=pin(p)['sha256']
 def walk(v):
  if isinstance(v,dict):
   if v.get('sha256')==sha and 'retained_relative' in v:matches.append(v)
   for x in v.values():walk(x)
  elif isinstance(v,list):
   for x in v:walk(x)
 walk(json.loads(ep.read_text(encoding='utf-8')));assert matches,(p,version)
 e=ep.parent/matches[0]['retained_relative'];assert p.read_bytes()==e.read_bytes();return {'F':pin(p),'E':pin(e),'E_manifest':pin(ep),'byte_exact':True}
def main():
 assert Path(sys.executable).resolve()==PY.resolve() and not OUT.exists() and not MEDIA.exists();OUT.mkdir()
 swdpath=SWD/'Hurt227-four-SWD-independent-masks-art-Grip-Axis-pairedshoe-registration-candidate-v002.json';swd=json.loads(swdpath.read_text(encoding='utf-8'));assert pin(swdpath)['sha256']=='68275b56c9d12bf70aa801b38c3393dbc6160abb53b6eb4d99368551436547a7'
 exactE(swdpath,422)
 reports=[]
 for name,run in [('Chest',LEATHER/'run-Hurt4-chest-native228-shared-HD-v001'),('ShoulderNear',LEATHER/'run-Hurt4-nearshoulder-native229-shared-HD-v001'),('ShoulderFar',FAR)]:
  for n in ['frames/frames-manifest.json','sprite-inspect.report.json','extraction-receipt-v001.json']:
   p=run/n;reports.append({'component':name,'file':pin(p),'data':json.loads(p.read_text(encoding='utf-8'))})
 # Root explicitly allowed NEW source fit despite original warnings/old strict FAILED records; no report rewriting.
 authority=write('Root-sourcefit-authority-original-warning-retention-v001.json',{'Root_messages':'Root permits NEW Chest228/Near229 sourcefit after independent clarification inspect report.ok uses errors; all0E1W and FAILED_NO_ACCEPTANCE preserved. E43839files1942846B2SHA0 permits actual231curated View and thirdcomponent fitting.','worker_actual231_four_View_after_E438':True,'actual_original_228_229_curated_View_after_E431_E432':True,'new_composites_Viewed':False,'warning_threshold_or_reports_modified':False,'original_reports':reports,'not_QA0':True,'TrialAllowed':False})
 rows=[];wholes=[];roots=[];display=[];allinput=[];font=lambda n:ImageFont.truetype('C:/Windows/Fonts/arial.ttf',n)
 colors={'BodyRest':[80,90,110,255],'NearArmWithoutHand':[80,180,255,255],'HelmetForeground':[225,200,80,255],'FarHandForeground':[180,90,225,255],'NearHand':[245,130,60,255]}
 for i,srow in enumerate(swd['rows']):
  p=Path(srow['source']['path']);assert pin(p)==srow['source'];bodyE=exactE(p,415);a=np.array(Image.open(p).convert('RGBA'));allinput.append(pin(p))
  hm=Path(srow['source_hand']['mask']['path']);assert pin(hm)==srow['source_hand']['mask'];near=np.array(Image.open(hm))>0
  alpha=a[:,:,3]>0;fh=poly(FARHAND0)&alpha&~near if i==0 else np.zeros((512,512),bool)
  ar=a.astype(np.int16);tan=(ar[:,:,0]>=90)&(ar[:,:,1]>=65)&(ar[:,:,0]-ar[:,:,1]>=12)&(ar[:,:,1]-ar[:,:,2]>=8)
  hp=poly(HELMET[i]);seed=tan&hp&alpha;dil=np.array(Image.fromarray(np.where(seed,255,0).astype(np.uint8)).filter(ImageFilter.MaxFilter(9)))>0
  helmet=fillholes(dil)&hp&alpha&~near&~fh
  arm=poly(NEARARM[i])&alpha&~near&~fh&~helmet
  rest=~(near|fh|helmet|arm)
  masks={'BodyRest':rest,'NearArmWithoutHand':arm,'HelmetForeground':helmet,'FarHandForeground':fh,'NearHand':near};count=np.sum(np.stack(list(masks.values())),axis=0);assert np.all(count==1)
  layers={n:np.where(m[:,:,None],a,0).astype(np.uint8) for n,m in masks.items()}
  assert np.array_equal(np.sum(np.stack(list(layers.values())),axis=0,dtype=np.uint16),a.astype(np.uint16))
  assert np.array_equal(layers['NearHand'],np.array(Image.open(Path(srow['source_hand']['foreground_exact_RGBA']['path']))))
  bodylayers=[];owner=np.zeros_like(a)
  for n,m in masks.items():
   mp=save(f'body-masks/{n}/frame-{i}.png',Image.fromarray(np.where(m,255,0).astype(np.uint8)));lp=save(f'body-layers/{n}/frame-{i}.png',Image.fromarray(layers[n]));bodylayers.append({'owner':n,'mask':pin(mp),'layer':pin(lp),'visible_pixels':int(np.count_nonzero(m&alpha)),'bbox':bbox(m&alpha),'empty_optional_owner':n=='FarHandForeground' and i>0});owner[m&alpha]=colors[n]
  save(f'diagnostics/frame-{i}-exclusive-owner-colors.png',Image.fromarray(owner))
  mounts=[];gearunion=np.zeros((512,512),bool)
  for name,run,ver in [('Chest',LEATHER/'run-Hurt4-chest-native228-shared-HD-v001',431),('ShoulderNear',LEATHER/'run-Hurt4-nearshoulder-native229-shared-HD-v001',432),('ShoulderFar',FAR,438)]:
   sp=run/f'curated/frame-{i}.png';srcE=exactE(sp,ver);ga=np.array(Image.open(sp).convert('RGBA'));A=MOUNTS[name]['A'][i];B=MOUNTS[name]['B'][i];delta=[B[0]-A[0],B[1]-A[1]];assert ga[A[1],A[0],3]>=128 and a[B[1],B[0],3]>=128
   shifted=translate(ga,delta);layers[name]=shifted;gp=save(f'armor-layers/{name}/frame-{i}.png',Image.fromarray(shifted));gearunion|=shifted[:,:,3]>0
   mounts.append({'component':name,'source':pin(sp),'source_E_gate':srcE,'A_source_actual_pixel':A,'A_RGBA':ga[A[1],A[0]].tolist(),'A_role':MOUNTS[name]['A_role'][i],'B_body_actual_pixel':B,'B_RGBA':a[B[1],B[0]].tolist(),'B_role':MOUNTS[name]['B_role'][i],'integer_delta':delta,'translated':pin(gp),'translated_bbox':bbox(shifted[:,:,3]>0),'translated_RGBA_exact_reversible':True,'resampling_rotation_mirroring':False,'visible_landmark_author_uncertainty_px':3,'not_bone_or_physical_socket_measurement':True,'core_over_original_body_core':int(np.count_nonzero((shifted[:,:,3]>=128)&(a[:,:,3]>=128))),'core_outside_original_body_core':int(np.count_nonzero((shifted[:,:,3]>=128)&(a[:,:,3]<128))),'core_over_helmet_pre_depth':int(np.count_nonzero((shifted[:,:,3]>=128)&helmet)),'semantic_fit_accepted':False})
  sword=Path(srow['author_binding']['Sword_layer']['path']);assert pin(sword)==srow['author_binding']['Sword_layer'];layers['SWD']=np.array(Image.open(sword));save(f'weapon-layers/SWD/frame-{i}.png',Image.fromarray(layers['SWD']))
  whole=compose(layers);wa=np.array(whole);union=gearunion|(layers['SWD'][:,:,3]>0)
  # Invisible source RGB is storage data; visible source pixels outside newgear/weapon must stay exact.
  outside=~union&(a[:,:,3]>0);assert np.array_equal(wa[outside],a[outside])
  cp=save(f'whole/frame-{i}-Hurt227-LGT-SWD-512RGBA.png',whole);root=srow['ground_registration']['pairedshoe_Root_artist_xy'];roots.append(root);wholes.append(whole)
  marks=Image.fromarray(a.copy());d=ImageDraw.Draw(marks)
  for mt in mounts:
   x,y=mt['B_body_actual_pixel'];d.ellipse((x-4,y-4,x+4,y+4),outline=(50,230,255,255),width=2);d.text((x+6,y-4),mt['component'],font=font(12),fill='white')
  save(f'diagnostics/frame-{i}-actual-body-B-landmarks.png',marks)
  rows.append({'frame':i,'duration_ms':100,'body_source':pin(p),'body_source_E_exact':bodyE,'body_partition':bodylayers,'neararm_artist_polygon':NEARARM[i],'helmet_artist_ROI_polygon':HELMET[i],'helmet_mask_method':'Visible tan material seed inside own frame ROI, 4px Chebyshev envelope + enclosed ink-hole fill, clipped to source alpha. Segmentation only; all originalRGBA retained under exclusive owners. Boundary semantic review pending.','farhand_polygon':FARHAND0 if i==0 else None,'FarHandForeground_role':'Own227farfist protectedfrom chest atframe0; explicitlyoptionalempty1..3, notgeneratedfallback.','exclusive_allcanvas_owner_count_one':True,'full_RGBA_body_reconstruction_exact':True,'NearHand_RGBA_exact_to_E422_own_Hurt_mask':True,'armor_mounts':mounts,'Sword_layer_exact_to_E422':pin(sword),'author_Grip_Axis':srow['author_binding'],'pairedshoe_root':root,'body_canvas_constant':CANVAS,'standing_height_basis':416,'footlock':False,'stack':STACK,'whole':pin(cp),'visible_body_RGBA_outside_gear_and_sword_unchanged':True,'semantic_coverage_accepted':False,'native_accepted':False})
  bg=Image.new('RGBA',(1280,720),(45,48,54,255));bg=Image.alpha_composite(bg,place(whole,root));dd=ImageDraw.Draw(bg);dd.text((24,20),f'OFFLINE Hurt227 + Chest228 Near229 Far231 + SWD .50 / phase{i} / {i*100}ms',font=font(23),fill='white');dd.text((24,56),'One body canvas88.6154 / standing72px. Original motion warnings retained. SOURCEFIT ONLY.',font=font(20),fill='white');im=bg.convert('RGB');save(f'preview-frames/actual-scale-{i:03d}.png',im);display.append(im)
 # Existing Ready own partition is used exclusively as the accepted Ready reference baseline.
 proof=json.loads((READY/'assembly-proof-v001.json').read_text(encoding='utf-8'));r0=proof['frames'][0];rdlayers={}
 for n in ['BodyRest','NearArmWithoutHand','NearHand']:
  p=READY/f'body-layers/{n}/frame-0.png';exactE(p,278);rdlayers[n]=Image.open(p).convert('RGBA')
 for n in ['Chest','NearShoulder','FarShoulder']:
  p=READY/f'armor-layers/{n}/frame-0.png';exactE(p,278);rdlayers[n]=Image.open(p).convert('RGBA')
 ready_body=ROOT/'source-assets/production/fairytale-sword-v001/run-ready-v002/curated/frame-0.png';ready_layer=SWD/'reference-only/Ready158-existing-binding-reconstruction-512RGBA.png';baseline_swd=np.array(Image.open(ready_layer))
 # Reproduce existing Ready sword independently using the already accepted reference transform, no Hurt masks reused.
 oldjoin=json.loads((SWD/'Hurt3-to-current-Ready158-existing-binding-join-diagnostic-v001.json').read_text(encoding='utf-8'));swordsrc=Image.open(Path(swd['independent_SWD_source']['path'])).convert('RGBa');g=np.array([212.,313.]);angle=np.arctan2(-.341,.94);c=float(np.cos(angle));s=float(np.sin(angle));aff=(c/.5,s/.5,99.-(c*g[0]+s*g[1])/.5,-s/.5,c/.5,256.-(-s*g[0]+c*g[1])/.5);rsword=swordsrc.transform((512,512),Image.Transform.AFFINE,aff,resample=Image.Resampling.BICUBIC).convert('RGBA')
 rwhole=Image.new('RGBA',(512,512))
 for n in ['BodyRest','FarShoulder','Chest','NearArmWithoutHand','NearShoulder']:
  rwhole=Image.alpha_composite(rwhole,rdlayers[n])
 rwhole=Image.alpha_composite(Image.alpha_composite(rwhole,rsword),rdlayers['NearHand']);rpath=save('reference-only/Ready158-current-LGT-existing-own-partition-SWD050.png',rwhole)
 # Plate/fullsource, owner diagnostics, body-scale, and endjoin are separate review surfaces.
 plate=Image.new('RGBA',(2048,570),(45,48,54,255));d=ImageDraw.Draw(plate)
 for i,im in enumerate(wholes):plate.alpha_composite(im,(i*512,48));d.text((i*512+10,12),f'Hurt{i} / OWN body+3LGT+SWD .50',font=font(22),fill='white')
 save('presentation/Hurt4-LGT-SWD-full512-contact-UNREVIEWED.png',plate.convert('RGB'))
 # Four independent 2x torso crops, no interpolation or changedfinalsource.
 torso=Image.new('RGBA',(2400,380),(45,48,54,255));d=ImageDraw.Draw(torso)
 for i,im in enumerate(wholes):
  crop=im.crop((100,190,400,360)).resize((600,340),Image.Resampling.NEAREST);torso.alpha_composite(crop,(i*600,36));d.text((i*600+8,8),f'Hurt{i} torso/own masks x2',font=font(22),fill='white')
 save('presentation/Hurt4-LGT-SWD-torso-2x-nearest-UNREVIEWED.png',torso.convert('RGB'))
 join=Image.new('RGBA',(1280,640),(45,48,54,255));join=Image.alpha_composite(join,place(wholes[3],roots[3],(1280,640),(320,560),1.));join=Image.alpha_composite(join,place(rwhole,[256,464],(1280,640),(960,560),1.));d=ImageDraw.Draw(join);d.text((30,12),'Hurt3 own5partition / 228+229+231',font=font(24),fill='white');d.text((670,12),'Current Ready158 + accepted LGT ownpartition',font=font(22),fill='white');d.line((20,560,1260,560),fill=(110,110,110));d.text((20,605),'Common ground. Source-size residuals and coverage require actual review. Native / zero-pop unaccepted.',font=font(20),fill='white');save('presentation/Hurt3-LGT-to-current-Ready-LGT-common-ground-UNREVIEWED.png',join.convert('RGB'))
 gif=OUT/'presentation/Hurt4-LGT-SWD-400ms-finite-NOLOOP-offline.gif';display[0].save(gif,save_all=True,append_images=display[1:],duration=[100]*4,disposal=2,optimize=False)
 with Image.open(gif) as check:
  durations=[]
  for i in range(check.n_frames):check.seek(i);durations.append(check.info['duration'])
  assert check.n_frames==4 and durations==[100]*4 and 'loop' not in check.info
 ff=ROOT/'tools/runtime/asset-gen/Lib/site-packages/imageio_ffmpeg/binaries/ffmpeg-win-x86_64-v7.1.exe';assert ff.is_file();vid=OUT/'presentation/Hurt4-LGT-SWD-400ms-finite-offline.mp4';argv=[str(ff),'-hide_banner','-framerate','10','-i',str(OUT/'preview-frames/actual-scale-%03d.png'),'-frames:v','4','-c:v','libx264','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(vid)];r=subprocess.run(argv,capture_output=True,text=True,encoding='utf-8');write('logs/ffmpeg-encode-v001.log',r.stdout+r.stderr);assert r.returncode==0
 dec=subprocess.run([str(ff),'-hide_banner','-i',str(vid),'-map','0:v:0','-f','null','-'],capture_output=True,text=True,encoding='utf-8');write('logs/ffmpeg-decode-v001.log',dec.stdout+dec.stderr);assert dec.returncode==0 and 'Duration: 00:00:00.40' in dec.stderr and int(re.findall(r'frame=\s*(\d+)',dec.stderr)[-1])==4
 contract=write('Hurt227-own-five-partition-12-integer-armor-mounts-SWD050-contract-v001.json',{'schema':'Hurt227-LGT-threecomponents-SWD-sourcefit-v001','sourcefit_authority':pin(authority),'original_SWD_contract':pin(swdpath),'components':['Chest228','ShoulderNear229','ShoulderFar231'],'oldFar230_rejected_not_used':True,'all_original_motion_warnings_and_FAILED_records_preserved':True,'rows':rows,'body_canvas_constant':CANVAS,'body_standing_height_source':416,'body_height_not_perframe_normalized':True,'weapon_scale_constant':.50,'all_armor_integer_translation_only':True,'Ready_reference':{'source':pin(rpath),'identity_component_frames':'CurrentacceptedReady0 registeredsources, notnewHurtidentity/offset truth','Ready_own_masks_never_used_on_Hurt':True,'source_assembly_proof':pin(READY/'assembly-proof-v001.json'),'root':[256,464],'existing_SWD_binding':oldjoin['Ready_original_root_grip_axis']},'explicit_risks':['Hurt1 generated chest shoulder aperture versus visible body shoulder and belt may not simultaneously fit using one integertranslation; composite must be reviewed.','Near0/2/3 similarperspectives need actual227 shoulderfit review; distinctRGBA notmotion acceptance.','ArtistNearArm/Helmet/FarHand boundary masks reconstructallRGBA exactly but require visibledepthreview.','Far thin tab maybe partlyoccludedby torso/helmet and mustmatchphysicalfar attachment.','CurrentReady endpoint artwork differs; originalSWD grip/eyejoin deltas retained, nozeroPop claim.'],'offline_preview':{'GIF':pin(gif),'loop_extension_present':False,'durations_ms':durations,'MP4':pin(vid),'duration_ms':400,'actual_decoded_frames':4,'actual_playback_reviewed':False,'not_UE_or_kernel_proof':True},'newmedia_Viewed':False,'sourcefit_motion_accepted':False,'TrialAllowed':False,'native_completed':False,'AI_calls':0,'Source_Content_Roottools_ledger_UE_modified':False})
 write('HANDOFF.md','Hurt227 own-source five exclusive body layers reconstruct every original RGBA pixel; NearHand/SWD exact to E422. Chest228/Near229/Far231 only integer translations of official curated shared-row outputs, no local repair, rescale or Ready mask reuse. Original inspect0E1W and old FAILED_NO_ACCEPTANCE receipts remain unchanged. New whole4, torso crops, 400ms finite GIF/MP4 and currentReady join are UNVIEWED before Root E retention. Body Canvas88.6153846/standing416 and each actual pairedshoe root from E422 are retained, not footlock. Root must review coverage/depth and motion; sourcefit/native/zeroPop remain unaccepted. Hurt1 chest shoulder-to-belt compatibility is an explicit risk, not automatically waived.\n')
 handoff=write('Root-Hurt4-LGT-SWD-integer-sourcefit-review-handoff-v001.json',{'schema':'Hurt4-LGT-SWD-four-sourcefit-review-v001','contract':pin(contract),'F_canonical':MEDIA.as_posix(),'whole4':[r['whole'] for r in rows],'newmedia_Viewed':False,'TrialAllowed':False,'next':'RoottwoSHAEpreservebeforeView, thenactual4full/torso/depth/400msmotion/currentReadyjoin; do notimportorclaimnative untilseparateacceptedgate.'})
 write('candidate-freeze-v001.json',{'files':[pin(p) for p in sorted(OUT.rglob('*')) if p.is_file()],'script':pin(Path(__file__)),'status':'UNVIEWED_NEW_SOURCEFIT_REVIEW_CANDIDATE','TrialAllowed':False})
 (MEDIA/'原件').mkdir(parents=True);shutil.copytree(OUT,MEDIA/'原件/四相LGT军剑整数试装完整包');(MEDIA/'展示副本').mkdir()
 for p in sorted((OUT/'presentation').iterdir()):shutil.copyfile(p,MEDIA/'展示副本'/p.name)
 ip=MEDIA/'来源-版本-状态索引.json';ip.write_text(json.dumps({'date':'2026-10-18','topic':'Hurt227棕皮三层与军剑四相整数试装','version':'v001','source':OUT.as_posix(),'handoff':pin(handoff),'status':'UNVIEWED_SOURCEFIT_CANDIDATE_NOT_QA0_NOT_NATIVE','TrialAllowed':False,'files':[pin(p) for p in sorted(MEDIA.rglob('*')) if p.is_file()]},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps({'F_canonical':MEDIA.as_posix(),'files':sum(p.is_file() for p in MEDIA.rglob('*')),'bytes':sum(p.stat().st_size for p in MEDIA.rglob('*') if p.is_file()),'handoff':pin(handoff),'contract':pin(contract),'four_body_RGBA_reconstruct':True,'12_integer_armor_translations_reversible':True,'original_warnings_preserved':True,'offline_duration_ms':400,'newmedia_View':False,'TrialAllowed':False},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
