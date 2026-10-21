import argparse,hashlib,json,sys
from pathlib import Path
from datetime import datetime,timezone
import numpy as np
from PIL import Image
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;C=HERE.parent
ORDER=['BodyRest','ShoulderFar','Chest','NearArmWithoutHand','ShoulderNear','HelmetForeground','NearHand'];OWNERS=['BodyRest','NearArmWithoutHand','HelmetForeground','NearHand'];ARMOR=['ShoulderFar','Chest','ShoulderNear'];DEP={}
def pin(p):
 p=Path(p).resolve();b=p.read_bytes();r={'path':p.as_posix(),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()};DEP[r['path']]=r;return r
def check(r):assert pin(r['path'])==r

def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def arr(p):
 pin(p);im=Image.open(p);assert im.size==(512,512) and im.mode=='RGBA';return np.array(im)
def box(m):
 y,x=np.where(m);return [int(x.min()),int(y.min()),int(x.max()+1),int(y.max()+1)] if len(x) else None
def write(p,d):
 with p.open('x',encoding='utf-8',newline='\n') as f:json.dump(d,f,ensure_ascii=False,indent=2);f.write('\n')
def compose(aa):
 im=Image.new('RGBA',(512,512))
 for a in aa:im=Image.alpha_composite(im,Image.fromarray(a))
 return np.array(im)
def member(r,base):
 p=Path(r.get('path',r.get('relative_path','')))
 if not p.is_absolute():
  assert '..' not in p.parts;p=(base/p).resolve();assert p.is_relative_to(base)
 b=p.read_bytes();assert len(b)==r['bytes'] and hashlib.sha256(b).hexdigest()==r['sha256']
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--body-owner-freeze',required=True,type=Path);ap.add_argument('--check-only',action='store_true');args=ap.parse_args();bodyfreeze=args.body_owner_freeze.resolve();worker=(C/'K4K5K7-body-owner-candidate-v001').resolve();assert bodyfreeze.parent==worker
 prep=read(HERE/'nine-armor-source-recipe-v001.json')
 for r in prep['dependencies']:check(r)
 wf=read(bodyfreeze);pin(bodyfreeze);members=wf.get('members',wf.get('files',[]));assert members
 for r in members:member(r,worker)
 for r in wf.get('dependency_pins',wf.get('dependencies',[])):member(r,worker)
 frames=[]
 for f in (4,5,7):
  source=prep['selected_body_sources'][str(f)];check(source);body=arr(source['path']);aa={o:arr(worker/f'body-layers/{o}/K{f}.png') for o in OWNERS};combined=np.zeros_like(body);counts=np.zeros((512,512),np.uint8)
  for a in aa.values():
   m=a[:,:,3]>0;assert np.array_equal(a[m],body[m]);counts+=m;combined[m]=a[m]
  assert (counts<=1).all() and np.array_equal(combined,body)
  farpath=worker/f'protection-masks/FarHandWarmHullHeuristic/K{f}.png';pin(farpath);farim=Image.open(farpath);assert farim.size==(512,512);farmask=np.array(farim.convert('L'))>0;nearmask=aa['NearHand'][:,:,3]>0;helmet=aa['HelmetForeground'][:,:,3]>0
  layerrows=[]
  for r in [r for r in prep['layers'] if r['K_frame']==f]:
   original=arr(r['source']['path']);p=HERE/r['candidate']['relative_path'];out=arr(p);dx,dy=r['transform']['integer_translation_xy'];sx=max(0,-dx);sy=max(0,-dy);ex=min(512,512-dx);ey=min(512,512-dy);expected=np.zeros_like(original);expected[sy+dy:ey+dy,sx+dx:ex+dx]=original[sy:ey,sx:ex];restored=np.zeros_like(original);restored[sy:ey,sx:ex]=out[sy+dy:ey+dy,sx+dx:ex+dx];assert np.array_equal(expected,out) and np.array_equal(restored,original)
   if f==7:assert dx==dy==0 and p.read_bytes()==Path(r['source']['path']).read_bytes()
   aa[r['owner']]=out;vis=out[:,:,3]>0
   layerrows.append({'owner':r['owner'],'source':r['source'],'candidate':r['candidate'],'transform':r['transform'],'raw_alpha1_overlap_near_hand_owner':int((vis&nearmask).sum()),'raw_alpha1_overlap_far_hand_heuristic':int((vis&farmask).sum()),'raw_alpha1_overlap_helmet_owner':int((vis&helmet).sum()),'canonical_K7_PNG_bytes_exact':f==7})
  final=compose([aa[o] for o in ORDER]);dest=HERE/f'diagnostic-assembly-no-sword/K{f}.png'
  if args.check_only:assert np.array_equal(final,arr(dest))
  else:
   dest.parent.mkdir(parents=True,exist_ok=True)
   with dest.open('xb') as h:Image.fromarray(final).save(h,format='PNG')
  near_changed=nearmask&np.any(final!=body,axis=2);far_changed=farmask&(body[:,:,3]>0)&np.any(final!=body,axis=2)
  later=np.ones((512,512),float);contrib={}
  for o in reversed(ORDER):
   alpha=aa[o][:,:,3].astype(float)/255;w=alpha*later
   if o in ARMOR:contrib[o]={'positive_source_contribution_pixels':int((w>0).sum()),'at_least_half_contribution_pixels':int((w>=.5).sum()),'effective_alpha_sum':round(float(w.sum()),6),'positive_bbox':box(w>0)}
   later*=1-alpha
  assemblypin=pin(dest);del DEP[assemblypin['path']]
  frames.append({'K_frame':f,'source_body':source,'body_stats':{'alpha1_bbox':box(body[:,:,3]>0),'alpha128_bbox':box(body[:,:,3]>=128)},'body_owners':{o:pin(worker/f'body-layers/{o}/K{f}.png') for o in OWNERS},'owner_source_RGBA_exclusive_reassembly_exact':True,'far_hand_protection':pin(farpath),'far_hand_protection_role':'Worker warm component convex hull + padding clipped source-alpha heuristic; not approved full anatomical hand segmentation.','draw_order_no_sword':ORDER,'armor_layers':layerrows,'assembly':assemblypin,'assembly_alpha1_bbox':box(final[:,:,3]>0),'near_hand_final_RGBA_changed_pixels':int(near_changed.sum()),'far_hand_heuristic_final_RGBA_changed_pixels':int(far_changed.sum()),'near_hand_changed_bbox':box(near_changed),'far_hand_changed_bbox':box(far_changed),'visible_armor_contribution':contrib,'hand_protection_numeric_clear':not near_changed.any() and not far_changed.any(),'wear_fit_accepted':False})
 # Candidate armor PNGs belong to this freeze, not external dependency list.
 for path in list(DEP):
  if Path(path).is_relative_to(HERE):del DEP[path]
 deps=list(DEP.values())
 report={'schema':'K4K5K7-LGT-nine-layer-three-assembly-integer-fit-candidate-v001','created_utc':datetime.now(timezone.utc).isoformat(),'selection':prep['selection'],'body_owner_freeze':pin(bodyfreeze),'source_recipe':{'path':(HERE/'nine-armor-source-recipe-v001.json').as_posix(),'scope':'Earlier source selection preparation; its pending notes superseded here.'},'armor_layer_count':9,'diagnostic_no_sword_assemblies':3,'all_existing_RGBA_translations_reversible':True,'all_nonzero_RGBA_clipped_pixels':0,'canonical_K7_all3_Ready0_PNG_bytes_exact':True,'K6_alias_K0_no_new_layers_or_imports':True,'frames':frames,'hand_masks_numeric_clear_all':all(r['hand_protection_numeric_clear'] for r in frames),'input_dependency_pins':deps,'images_viewed':False,'new_art_generation_calls':0,'wear_fit_accepted':False,'runtime_imported':False,'FinalAccepted':False,'open':['All body-owner semantic boundaries and existing component orientation need Root View after F/E retention.','K4 local foot positions remain offset versusK3; no corrective X move or native foot-lock acceptance.','Far hand protection uses supplied heuristic; numeric clear does not prove full hand silhouette.','Source-over at owner boundaries is measured using supplied masks; no GPU/resource/native optical claim.','IndependentSword is omitted and Grip/Axis unapproved; no motion/audio/complete equipment unit claim.','Canonical K7 Ready0 shoulder overhang is retained unchanged, not trimmed or refitted to improve numeric overlap.']}
 for _ in range(2):
  for r in deps:check(r)
 if args.check_only:
  existing=read(HERE/'LGT-fit-final-metrics-v001.json');assert existing['frames']==frames
  frozen=read(HERE/'LGT-fit-freeze-v001.json')
  for r in frozen['members']:member(r,HERE)
  for r in frozen['dependency_pins']:check(r)
 else:
  write(HERE/'LGT-fit-final-metrics-v001.json',report)
  handoff=['# K4/K5/K7 LGT source-pixel fit candidate v001','','9 existing armor layers; 3 source-order no-sword diagnostic assemblies. K7 is exact Ready0 armor PNG byte copies at (0,0); K6 aliases existing K0 and has no new asset.','',
   'K4: oldJ3 Far(-95,-43), Chest(+9,+3); oldJ2 Near(+65,+8). K5: oldJ2 Far(-116,-28), Chest(-17,-6), Near(+29,-4). All source RGBA inverse translations exact, no clipped nonzeroRGBA, no scale/rotation/painting/warp.','',
   'K4/5 six layers alpha128 outside-body count0. K7 canonical NearShoulder retains original115 alpha128 outside-body pixels and107 alpha>0 outside pixels; no refit or trimming. Exact sources/bboxes/overlaps and source feature coordinates are in nine-armor-source-recipe-v001.json.','',
   'Source-order: BodyRest -> ShoulderFar -> Chest -> NearArmWithoutHand -> ShoulderNear -> HelmetForeground -> NearHand. IndependentSword omitted. Body owner source reassembly exact. Body semantics and far hand warm-hull heuristic need Root visual approval. Numeric clear does not prove a complete anatomical mask.']
  for r in frames:handoff.append(f"K{r['K_frame']}: final near-hand owner RGBA changed {r['near_hand_final_RGBA_changed_pixels']}; final far-hand supplied heuristic RGBA changed {r['far_hand_heuristic_final_RGBA_changed_pixels']}.")
  handoff+=['','K4 foot position drift13/21sourcepx remains untouched; native feet and K3/K4/K5/K6/Ready continuity remain OPEN. Armor shape orientation, glove/helmet scale and sleeve/chest owner seams require Root retained View; no automatic wear acceptance.','',
   'No View/image generation/UE/actual Source Content tools E ledger status writes. Root must retain F original+presentation and E indexed copies before viewing diagnostic-assembly-no-sword/K4,K5,K7.png. All fit/semantic/runtime/FinalAccepted=false.','',
   'Read-only recheck: run this script --body-owner-freeze <same pinned freeze> --check-only.']
  with (HERE/'HANDOFF-v001.md').open('x',encoding='utf-8',newline='\n') as h:h.write('\n'.join(handoff)+'\n')
  members=[pin(p) for p in sorted(HERE.rglob('*')) if p.is_file()]
  for _ in range(2):
   for r in members+deps:check(r)
  write(HERE/'LGT-fit-freeze-v001.json',{'schema':'K4K5K7-LGT-nine-existing-armor-pixel-fit-freeze-v001','members':members,'dependency_pins':deps,'member_count':len(members),'dependency_count':len(deps),'verification_passes':2,'twoSHA_mismatches':0,'armor_layers':9,'diagnostic_no_sword_assemblies':3,'canonical_K7_Ready0_PNG_bytes_exact':True,'K6_no_new_assets':True,'source_pixels_reversible':True,'images_viewed':False,'wear_fit_accepted':False,'runtime_imported':False,'FinalAccepted':False})
 print(json.dumps({'freeze':pin(HERE/'LGT-fit-freeze-v001.json'),'armor_layers':9,'assemblies':3,'deps':len(deps),'hands_numeric_clear':report['hand_masks_numeric_clear_all'],'hand_deltas':[{'K':r['K_frame'],'near':r['near_hand_final_RGBA_changed_pixels'],'far':r['far_hand_heuristic_final_RGBA_changed_pixels']} for r in frames],'check_only':args.check_only}))
if __name__=='__main__':main()
