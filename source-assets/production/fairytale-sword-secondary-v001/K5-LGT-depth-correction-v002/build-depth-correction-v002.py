import argparse,hashlib,json,shutil,sys
from pathlib import Path
from datetime import datetime,timezone
import numpy as np
from PIL import Image
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;C=HERE.parent;OLD=C/'K4K5K7-LGT-fit-candidate-v001'
ORDER=['BodyRest','ShoulderFar','Chest','NearArmWithoutHand','ShoulderNear','HelmetForeground','NearHand'];OWNERS=['BodyRest','NearArmWithoutHand','HelmetForeground','NearHand'];ARMOR=['ShoulderFar','Chest','ShoulderNear'];DEPS={}
def pin(p):
 p=Path(p).resolve();b=p.read_bytes();r={'path':p.as_posix(),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()};DEPS[r['path']]=r;return r
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def exact(r):assert pin(r['path'])==r

def arr(p):
 pin(p);im=Image.open(p);assert im.size==(512,512) and im.mode=='RGBA';return np.array(im)
def box(m):
 y,x=np.where(m);return [int(x.min()),int(y.min()),int(x.max()+1),int(y.max()+1)] if len(x) else None
def write(p,d):
 with p.open('x',encoding='utf-8',newline='\n') as f:json.dump(d,f,ensure_ascii=False,indent=2);f.write('\n')
def members(freeze):
 d=read(freeze);pin(freeze)
 for r in d.get('members',d.get('files',[]))+d.get('dependency_pins',d.get('dependencies',[])):
  q=Path(r.get('path',r.get('relative_path','')))
  if not q.is_absolute():assert '..' not in q.parts;q=(freeze.parent/q).resolve();assert q.is_relative_to(freeze.parent)
  b=q.read_bytes();assert len(b)==r['bytes'] and hashlib.sha256(b).hexdigest()==r['sha256']
 return d
def compose(aa):
 im=Image.new('RGBA',(512,512))
 for o in ORDER:im=Image.alpha_composite(im,Image.fromarray(aa[o]))
 return np.array(im)
def depth(aa):
 later=np.ones((512,512),float);d={};mask=None
 for o in reversed(ORDER):
  alpha=aa[o][:,:,3].astype(float)/255;w=alpha*later
  if o in ARMOR:d[o]={'positive_source_contribution_pixels':int((w>0).sum()),'source_contribution_at_least_half_pixels':int((w>=.5).sum()),'effective_alpha_sum':round(float(w.sum()),6),'positive_bbox':box(w>0)}
  if o=='Chest':mask=np.rint(w*255).astype(np.uint8)
  later*=1-alpha
 return d,mask

def save_png(p,a,check):
 if check:assert np.array_equal(np.array(Image.open(p)),a)
 else:
  p.parent.mkdir(parents=True,exist_ok=True)
  with p.open('xb') as f:Image.fromarray(a).save(f,format='PNG')
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--body-owner-freeze',required=True,type=Path);ap.add_argument('--check-only',action='store_true');args=ap.parse_args()
 oldfreeze=OLD/'LGT-fit-freeze-v001.json';assert pin(oldfreeze)['sha256']=='a686aaec79ad737ca473d79a9a86d8dfac9adc3f73caee3115b2920b90c8b7c1';members(oldfreeze)
 worker=(C/'K5-body-owner-correction-v002').resolve();bf=args.body_owner_freeze.resolve();assert bf.parent==worker;members(bf)
 oldreport=read(OLD/'LGT-fit-final-metrics-v001.json');pin(OLD/'LGT-fit-final-metrics-v001.json');old=next(r for r in oldreport['frames'] if r['K_frame']==5);source=old['source_body'];exact(source);body=arr(source['path'])
 aa_old={o:arr(old['body_owners'][o]['path']) for o in OWNERS};aa={o:arr(worker/f'body-layers/{o}/K5.png') for o in OWNERS};assert np.array_equal(aa['HelmetForeground'],aa_old['HelmetForeground']), 'Unexpected helmet change outside correction scope'
 for layers in (aa_old,aa):
  combined=np.zeros_like(body);counts=np.zeros((512,512),np.uint8)
  for a in layers.values():
   m=a[:,:,3]>0;assert np.array_equal(a[m],body[m]);combined[m]=a[m];counts+=m
  assert (counts<=1).all() and np.array_equal(combined,body)
 armor=[]
 for o in ARMOR:
  sourcearmor=OLD/f'armor-layers/{o}/K5.png';dest=HERE/f'armor-layers/{o}/K5.png';s=pin(sourcearmor)
  if args.check_only:assert dest.read_bytes()==sourcearmor.read_bytes()
  else:dest.parent.mkdir(parents=True,exist_ok=True);assert not dest.exists();shutil.copyfile(sourcearmor,dest)
  assert pin(dest)['sha256']==s['sha256'];aa[o]=arr(dest);aa_old[o]=arr(sourcearmor)
  armor.append({'owner':o,'old_frozen_K5_PNG':s,'new_copy':pin(dest),'PNG_bytes_exact':True,'decoded_RGBA_exact':True,'additional_translation_xy':[0,0],'scale_xy':[1,1],'rotation':0})
 oldimage=compose(aa_old);exact(old['assembly']);assert np.array_equal(oldimage,arr(old['assembly']['path']));image=compose(aa)
 olddepth,oldmask=depth(aa_old);newdepth,newmask=depth(aa);assert olddepth['Chest']['positive_source_contribution_pixels']==602
 save_png(HERE/'diagnostic-assembly-no-sword/K5.png',image,args.check_only)
 save_png(HERE/'qc/K5-old-v001-left-new-v002-right-unscaled.png',np.concatenate([oldimage,image],axis=1),args.check_only)
 save_png(HERE/'qc/Chest-contribution-alpha-old-v001.png',oldmask,args.check_only);save_png(HERE/'qc/Chest-contribution-alpha-new-v002.png',newmask,args.check_only)
 near=aa['NearHand'][:,:,3]>0;oldnear=aa_old['NearHand'][:,:,3]>0
 farpath=worker/'protection-masks/FarHandWarmHullHeuristic/K5.png';pin(farpath);farim=Image.open(farpath);assert farim.size==(512,512);far=np.array(farim.convert('L'))>0
 def changed(mask):
  m=mask&(body[:,:,3]>0)&np.any(image!=body,axis=2);return {'changed_source_RGBA_pixels':int(m.sum()),'bbox':box(m)}
 counts=[]
 for name,rect in [('Root_front_chest_reference_ROI',[236,235,276,286]),('Root_near_arm_reference_ROI',[183,220,231,287])]:
  x0,y0,x1,y1=rect;region=np.zeros((512,512),bool);region[y0:y1,x0:x1]=True;region&=body[:,:,3]>0
  counts.append({'name':name,'rectangle_xyxy':rect,'role':'Root reference region, not automated anatomical segmentation','source_visible_pixels':int(region.sum()),'old_owner_pixels':{o:int((region&(aa_old[o][:,:,3]>0)).sum()) for o in OWNERS},'new_owner_pixels':{o:int((region&(aa[o][:,:,3]>0)).sum()) for o in OWNERS}})
 transitions={}
 for oldowner in OWNERS:
  for newowner in OWNERS:
   n=int(((aa_old[oldowner][:,:,3]>0)&(aa[newowner][:,:,3]>0)).sum())
   if n:transitions[oldowner+' -> '+newowner]=n
 chestraw=aa['Chest'][:,:,3]>0
 hand={'new_supplied_NearHand_owner':changed(near),'new_supplied_far_warm_hull_heuristic':changed(far),'old_broader_NearHand_owner_region_diagnostic':changed(oldnear),'old_NearHand_removed_visible_coordinates':int((oldnear&~near).sum()),'new_NearHand_added_visible_coordinates':int((near&~oldnear).sum()),'near_hand_mask_semantics':'Corrected worker supplied ownership; old broader mask may contain belt. Difference cannot all be called hand loss. Actual semantics still require Root View.','raw_Chest_newNearHand_overlap':int((chestraw&near).sum()),'raw_Chest_newNearArm_overlap':int((chestraw&(aa['NearArmWithoutHand'][:,:,3]>0)).sum()),'raw_Chest_far_heuristic_overlap':int((chestraw&far).sum())}
 # Do not pin outputs as external dependencies; the local freeze owns all outputs.
 for q in list(DEPS):
  if Path(q).is_relative_to(HERE):del DEPS[q]
 deps=list(DEPS.values())
 result={'schema':'K5-LGT-depth-owner-correction-v002','created_utc':datetime.now(timezone.utc).isoformat(),'source_body':source,'old_frozen_fit':pin(oldfreeze),'new_body_owner_freeze':pin(bf),'armor':armor,'draw_order_no_sword':ORDER,'source_RGBA_and_alpha_reassembly_exact':True,'helmet_decoded_RGBA_unchanged':True,'armor_position_and_pixels_unchanged':True,'old_visible_armor':olddepth,'new_visible_armor':newdepth,'Chest_positive_pixel_increase':newdepth['Chest']['positive_source_contribution_pixels']-602,'Chest_effective_alpha_increase':round(newdepth['Chest']['effective_alpha_sum']-olddepth['Chest']['effective_alpha_sum'],6),'hands':hand,'reference_ROI_owner_counts':counts,'source_visible_owner_transitions':transitions,'old_source_body_alpha1_bbox':box(body[:,:,3]>0),'new_assembly_alpha1_bbox':box(image[:,:,3]>0),'new_assembly_alpha128_bbox':box(image[:,:,3]>=128),'input_dependency_pins':deps,'images_viewed':False,'art_generation_calls':0,'wear_fit_accepted':False,'runtime_imported':False,'FinalAccepted':False,'open':['Only the body owner correction changes depth. Armor source and placement remain identical to rejected v001.','Corrected NearHand and far-hand mask semantics need Root retained View; supplied-mask pixel closure is not anatomical approval.','If armor orientation or coverage still fails after owner correction, report it separately instead of relocating armor in this task.','K5 boot and glove identity/native feet/real-time joining/sword markers remain outside this technical comparison.','No independent Sword, GPU/native viewport, motion, audio or complete equipment claim.']}
 for _ in range(2):
  for r in deps:exact(r)
 if args.check_only:
  existing=read(HERE/'K5-depth-comparison-v002.json')
  for key in ['armor','old_visible_armor','new_visible_armor','hands','reference_ROI_owner_counts','source_visible_owner_transitions']:assert existing[key]==result[key]
  members(HERE/'depth-correction-freeze-v002.json')
 else:
  write(HERE/'K5-depth-comparison-v002.json',result)
  lines=['# K5 LGT depth correction candidate v002','','The three armor PNGs are exact byte copies of rejected a686… K5 armor, at identical source coordinates. No movement, scale, rotation, alpha edit, resampling or new art. Only the supplied new body owner split changes source-over depth.','',f"Chest positive visible source contribution: old602 -> new{newdepth['Chest']['positive_source_contribution_pixels']}; effective alpha old{olddepth['Chest']['effective_alpha_sum']} -> new{newdepth['Chest']['effective_alpha_sum']}.",f"Corrected near hand source RGBA changes{hand['new_supplied_NearHand_owner']['changed_source_RGBA_pixels']}; far supplied heuristic changes{hand['new_supplied_far_warm_hull_heuristic']['changed_source_RGBA_pixels']}.",'','Old broader NearHand region differences include deliberately reassigned belt; do not describe all differences as hand damage. Exact owner transition/ROI/source alpha closure and raw Chest overlaps are in K5-depth-comparison-v002.json. Semantic correctness and armor direction still need Root View.','',
   'Diagnostic qc/K5-old-v001-left-new-v002-right-unscaled.png uses old left/new right, no resizing. The two Chest contribution L masks show source-over contribution alpha; they are diagnostics, not replacement game assets.','',
   'Root F original/presentation + E indexed retention required before View. This agent did not View/useUE/change actual Source Content tools E status ledger or any old frozen file. No sword in this diagnostic; seven body/armor slots use the existing eight-slot sequence with Sword omitted. Fit/runtime/FinalAccepted=false.','',
   'Read-only repeat: this script --body-owner-freeze <same pinned freeze> --check-only.']
  with (HERE/'HANDOFF-v002.md').open('x',encoding='utf-8',newline='\n') as h:h.write('\n'.join(lines)+'\n')
  mm=[pin(p) for p in sorted(HERE.rglob('*')) if p.is_file()]
  for _ in range(2):
   for r in mm+deps:exact(r)
  write(HERE/'depth-correction-freeze-v002.json',{'schema':'K5-LGT-three-armor-depth-correction-freeze-v002','members':mm,'dependency_pins':deps,'member_count':len(mm),'dependency_count':len(deps),'verification_passes':2,'twoSHA_mismatches':0,'three_armor_PNG_bytes_unchanged':True,'additional_armor_transform':False,'body_source_RGBA_alpha_exact':True,'images_viewed':False,'wear_fit_accepted':False,'runtime_imported':False,'FinalAccepted':False})
 print(json.dumps({'freeze':pin(HERE/'depth-correction-freeze-v002.json'),'old_Chest':602,'new_Chest':newdepth['Chest']['positive_source_contribution_pixels'],'Chest_effective_alpha':newdepth['Chest']['effective_alpha_sum'],'near_hand_delta':hand['new_supplied_NearHand_owner']['changed_source_RGBA_pixels'],'far_hand_delta':hand['new_supplied_far_warm_hull_heuristic']['changed_source_RGBA_pixels'],'check_only':args.check_only}))
if __name__=='__main__':main()
