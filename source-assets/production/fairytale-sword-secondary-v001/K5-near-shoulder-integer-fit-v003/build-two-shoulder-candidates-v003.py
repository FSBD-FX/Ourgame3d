import argparse,hashlib,json,shutil,sys
from pathlib import Path
from datetime import datetime,timezone
import numpy as np
from PIL import Image
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;C=HERE.parent;V2=C/'K5-LGT-depth-correction-v002';BODY=C/'K5-body-owner-correction-v002';OLD=C/'K4K5K7-LGT-fit-candidate-v001'
ORDER=['BodyRest','ShoulderFar','Chest','NearArmWithoutHand','ShoulderNear','HelmetForeground','NearHand'];OWNERS=['BodyRest','NearArmWithoutHand','HelmetForeground','NearHand'];ARMOR=['ShoulderFar','Chest','ShoulderNear'];PLANS={'A':(-45,-15),'B':(-50,-21)};DEP={}
def pin(p):
 p=Path(p).resolve();b=p.read_bytes();r={'path':p.as_posix(),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()};DEP[r['path']]=r;return r
def exact(r):assert pin(r['path'])==r

def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def arr(p):
 pin(p);im=Image.open(p);assert im.mode=='RGBA' and im.size==(512,512);return np.array(im)
def box(m):
 y,x=np.where(m);return [int(x.min()),int(y.min()),int(x.max()+1),int(y.max()+1)] if len(x) else None
def validate_freeze(p,sha):
 assert pin(p)['sha256']==sha;d=read(p)
 for r in d.get('members',[])+d.get('dependency_pins',[]):
  q=Path(r.get('path',r.get('relative_path','')))
  if not q.is_absolute():assert '..' not in q.parts;q=(p.parent/q).resolve();assert q.is_relative_to(p.parent)
  b=q.read_bytes();assert len(b)==r['bytes'] and hashlib.sha256(b).hexdigest()==r['sha256']
 return d

def compose(aa):
 im=Image.new('RGBA',(512,512))
 for o in ORDER:im=Image.alpha_composite(im,Image.fromarray(aa[o]))
 return np.array(im)
def depth(aa):
 later=np.ones((512,512),float);result={}
 for o in reversed(ORDER):
  alpha=aa[o][:,:,3].astype(float)/255;w=alpha*later
  if o in ARMOR:result[o]={'positive_source_contribution_pixels':int((w>0).sum()),'at_least_half_source_contribution_pixels':int((w>=.5).sum()),'effective_alpha_sum':round(float(w.sum()),6),'positive_bbox':box(w>0)}
  later*=1-alpha
 return result

def save(p,a,check):
 if check:assert np.array_equal(np.array(Image.open(p)),a)
 else:
  p.parent.mkdir(parents=True,exist_ok=True)
  with p.open('xb') as h:Image.fromarray(a).save(h,format='PNG')
def copy(p,q,check):
 if check:assert q.read_bytes()==p.read_bytes()
 else:q.parent.mkdir(parents=True,exist_ok=True);assert not q.exists();shutil.copyfile(p,q)
 assert q.read_bytes()==p.read_bytes()
def write(p,d):
 with p.open('x',encoding='utf-8',newline='\n') as f:json.dump(d,f,ensure_ascii=False,indent=2);f.write('\n')
def translated(a,dx,dy):
 out=np.zeros_like(a);sx=max(0,-dx);sy=max(0,-dy);ex=min(512,512-dx);ey=min(512,512-dy);out[sy+dy:ey+dy,sx+dx:ex+dx]=a[sy:ey,sx:ex];back=np.zeros_like(a);back[sy:ey,sx:ex]=out[sy+dy:ey+dy,sx+dx:ex+dx];assert np.array_equal(back,a)
 assert np.array_equal(np.bincount(a[:,:,3].ravel(),minlength=256),np.bincount(out[:,:,3].ravel(),minlength=256))
 return out

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--check-only',action='store_true');args=ap.parse_args()
 vf=V2/'depth-correction-freeze-v002.json';bf=BODY/'four-owner-freeze-v002.json';validate_freeze(vf,'f6bc5502968995c99674e3d42a217c336791b1fa3e73c32a8692bdd3b9ae506b');validate_freeze(bf,'08185a5d8f0f70b5ecd0b43cdf71dbd0b809a6762a25a5e7756ee3d7b713bfe4')
 olddepth=read(V2/'K5-depth-comparison-v002.json');pin(V2/'K5-depth-comparison-v002.json');source=olddepth['source_body'];exact(source);body=arr(source['path']);layers={o:arr(BODY/f'body-layers/{o}/K5.png') for o in OWNERS}
 merged=np.zeros_like(body);counts=np.zeros((512,512),np.uint8)
 for a in layers.values():
  m=a[:,:,3]>0;counts+=m;merged[m]=a[m];assert np.array_equal(a[m],body[m])
 assert (counts<=1).all() and np.array_equal(merged,body)
 references=[]
 for o in ARMOR:
  p=V2/f'armor-layers/{o}/K5.png';q=HERE/f'unchanged-reference-armor/{o}/K5.png';copy(p,q,args.check_only);layers[o]=arr(p);references.append({'owner':o,'source':pin(p),'copy_PNG_bytes_exact':True,'reference_copy':q.relative_to(HERE).as_posix()})
 originalnear=layers['ShoulderNear'].copy()
 pin(OLD/'nine-armor-source-recipe-v001.json');origrecipe=next(r for r in read(OLD/'nine-armor-source-recipe-v001.json')['layers'] if r['K_frame']==5 and r['owner']=='ShoulderNear');exact(origrecipe['source']);j2=arr(origrecipe['source']['path']);assert origrecipe['transform']['integer_translation_xy']==[29,-4];assert np.array_equal(translated(j2,29,-4),originalnear)
 baseline=compose(layers);assert np.array_equal(baseline,arr(V2/'diagnostic-assembly-no-sword/K5.png'));basedepth=depth(layers);assert basedepth['Chest']['positive_source_contribution_pixels']==1342
 nearhand=layers['NearHand'][:,:,3]>0;helmet=layers['HelmetForeground'][:,:,3]>0;arm1=layers['NearArmWithoutHand'][:,:,3]>0;arm128=layers['NearArmWithoutHand'][:,:,3]>=128
 farpath=BODY/'protection-masks/FarHandWarmHullHeuristic/K5.png';pin(farpath);far=np.array(Image.open(farpath).convert('L'))>0
 results=[];images=[]
 for name,(dx,dy) in PLANS.items():
  moved=translated(originalnear,dx,dy);save(HERE/f'near-shoulder-candidates/{name}/K5.png',moved,args.check_only);aa={**layers,'ShoulderNear':moved};image=compose(aa);save(HERE/f'diagnostic-assembly-no-sword/{name}/K5.png',image,args.check_only);images.append(image)
  solid=moved[:,:,3]>=128;vis=moved[:,:,3]>0;d=depth(aa);near_changed=nearhand&np.any(image!=body,axis=2);far_changed=far&(body[:,:,3]>0)&np.any(image!=body,axis=2)
  result={'candidate':name,'position_role':'Exact Root proposal; numerical comparison only, no wear selection','additional_integer_translation_xy':[dx,dy],'underlying_original_J2_source':origrecipe['source'],'total_translation_from_original_J2':[29+dx,-4+dy],'source_near_shoulder_alpha1_bbox':box(originalnear[:,:,3]>0),'candidate_alpha1_bbox':box(vis),'candidate_alpha128_bbox':box(solid),'RGBA_inverse_translation_exact':True,'source_alpha_histogram_exact':True,'source_RGBA_nonzero_clipped_pixels':0,'scale_xy':[1,1],'rotation':0,'solid_pixels':int(solid.sum()),'alpha1_pixels':int(vis.sum()),'arm_overlap_alpha128':int((solid&arm128).sum()),'arm_overlap_alpha1':int((vis&arm1).sum()),'arm_solid_overlap_fraction':float((solid&arm128).sum()/solid.sum()),'solid_outside_supplied_arm_owner_pixels':int((solid&~arm128).sum()),'solid_outside_whole_source_body_pixels':int((solid&(body[:,:,3]<128)).sum()),'alpha1_outside_whole_source_body_pixels':int((vis&(body[:,:,3]==0)).sum()),'raw_overlap_helmet_alpha1':int((vis&helmet).sum()),'raw_overlap_near_hand_alpha1':int((vis&nearhand).sum()),'raw_overlap_far_hand_heuristic_alpha1':int((vis&far).sum()),'raw_overlap_Chest_alpha1':int((vis&(layers['Chest'][:,:,3]>0)).sum()),'near_hand_final_source_RGBA_changed_pixels':int(near_changed.sum()),'far_hand_heuristic_final_source_RGBA_changed_pixels':int(far_changed.sum()),'visible_armor_contributions':d,'Chest_visible_positive_delta_to_v002':d['Chest']['positive_source_contribution_pixels']-1342,'final_alpha1_bbox':box(image[:,:,3]>0),'final_alpha128_bbox':box(image[:,:,3]>=128),'new_source_body_edits':0,'fit_accepted':False}
  results.append(result)
 save(HERE/'qc/K5-original-v002-left-A-middle-B-right-unscaled.png',np.concatenate([baseline,*images],axis=1),args.check_only)
 for p in list(DEP):
  if Path(p).is_relative_to(HERE):del DEP[p]
 deps=list(DEP.values())
 report={'schema':'K5-near-shoulder-two-integer-comparisons-v003','created_utc':datetime.now(timezone.utc).isoformat(),'baseline_depth_freeze':pin(vf),'fixed_body_freeze':pin(bf),'fixed_body_source':source,'source_body_owners_RGBA_alpha_reassembly_exact':True,'unchanged_reference_armor':references,'body_far_Chest_hand_helmet_unchanged':True,'source_order_no_sword':ORDER,'baseline_visible_armor':basedepth,'historical_Chest_v001_positive':602,'baseline_Chest_v002_positive':1342,'candidates':results,'additional_C_created':False,'additional_C_reason':'Both Root proposals have zero whole-body solid/alpha1 overshoot, substantial existing arm support and clear supplied hand masks. No need to invent a third candidate to force numerical improvement.','dependencies':deps,'images_viewed':False,'new_art_generation_calls':0,'wear_fit_accepted':False,'runtime_imported':False,'FinalAccepted':False,'open':['A/B source closure and supplied masks do not approve anatomy, silhouette or armor fit; Root selects after F/E672 retained View.','B has a small raw head overlap to inspect; HelmetForeground later draws over it.','Pixels outside the supplied NearArm owner but inside the body are measured separately from true whole-body overshoot; body masks were not expanded.','Far hand mask is the existing warm-hull heuristic, not fully approved anatomical segmentation.','Independent sword/native feet/action joining/GPU/audio/full unit closure not included.']}
 for _ in range(2):
  for r in deps:exact(r)
 if args.check_only:
  existing=read(HERE/'two-shoulder-candidates-metrics-v003.json');assert existing['candidates']==results and existing['baseline_visible_armor']==basedepth
  f=HERE/'near-shoulder-fit-freeze-v003.json';validate_freeze(f,pin(f)['sha256'])
 else:
  write(HERE/'two-shoulder-candidates-metrics-v003.json',report)
  lines=['# K5 near-shoulder integer comparison v003','','Body frozen08185… is unchanged. Three original K5 armor PNGs are retained as exact byte reference copies; only ShoulderNear is translated into A/B. Far/Chest/body/hand/helmet pixels and positions remain unchanged.','',
   'A: relative current(-45,-15), originalJ2(-16,-19). B: relative current(-50,-21), originalJ2(-21,-25). Full512 canvas, original RGBA exactly reversible, original alpha histogram exact, nonzeroRGBA clipping0, no scaling/rotation/painting or body-mask expansion.','']
  for r in results:lines.append(f"{r['candidate']}: bbox{r['candidate_alpha128_bbox']}; arm solid overlap{r['arm_overlap_alpha128']}/{r['solid_pixels']}; body solid overshoot{r['solid_outside_whole_source_body_pixels']}; head raw overlap{r['raw_overlap_helmet_alpha1']}px; final near/far mask sourceRGBA changes{r['near_hand_final_source_RGBA_changed_pixels']}/{r['far_hand_heuristic_final_source_RGBA_changed_pixels']}; Chest positive contribution{r['visible_armor_contributions']['Chest']['positive_source_contribution_pixels']} (v002 baseline1342, oldv001602).")
  lines+=['','Both have real existing arm support and no whole-body overshoot; no extraC was created. A/B still need silhouette/perspective and sleeve-chest junction review. Numerical 0 is not wear acceptance.','',
   'qc/K5-original-v002-left-A-middle-B-right-unscaled.png: left originalv002, middleA, rightB; three full512 images pasted without resize. Root must retain F originals/presentation and E672 indexed copy before View. This agent did not View or runUE, generate art, alter old freezes or actual Source/Content/tools/E/status/ledger.','',
   'Read-only repeat: build-two-shoulder-candidates-v003.py --check-only. All fit/runtime/FinalAccepted=false.']
  with (HERE/'HANDOFF-v003.md').open('x',encoding='utf-8',newline='\n') as h:h.write('\n'.join(lines)+'\n')
  mm=[pin(p) for p in sorted(HERE.rglob('*')) if p.is_file()]
  for _ in range(2):
   for r in mm+deps:exact(r)
  write(HERE/'near-shoulder-fit-freeze-v003.json',{'schema':'K5-near-shoulder-AB-integer-fit-freeze-v003','members':mm,'dependency_pins':deps,'member_count':len(mm),'dependency_count':len(deps),'verification_passes':2,'twoSHA_mismatches':0,'body_Far_Chest_hand_helmet_unchanged':True,'source_RGBA_alpha_reversible':True,'source_nonzero_RGBA_clipped_pixels':0,'candidate_count':2,'images_viewed':False,'wear_fit_accepted':False,'runtime_imported':False,'FinalAccepted':False})
 print(json.dumps({'freeze':pin(HERE/'near-shoulder-fit-freeze-v003.json'),'candidates':[{'name':r['candidate'],'arm':r['arm_overlap_alpha128'],'overshoot':r['solid_outside_whole_source_body_pixels'],'Chest':r['visible_armor_contributions']['Chest']['positive_source_contribution_pixels'],'near_delta':r['near_hand_final_source_RGBA_changed_pixels'],'far_delta':r['far_hand_heuristic_final_source_RGBA_changed_pixels']} for r in results],'check_only':args.check_only}))
if __name__=='__main__':main()
