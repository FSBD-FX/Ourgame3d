import argparse, hashlib, json, platform, sys
from datetime import datetime, timezone
from pathlib import Path
import numpy as np
from PIL import Image, __version__ as PIL_VERSION
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
C = HERE.parent
P = C.parent
OWNERS = ('BodyRest','NearArmWithoutHand','HelmetForeground','NearHand')
ARMOR = ('ShoulderFar','Chest','ShoulderNear')
ORDER = ('BodyRest','ShoulderFar','Chest','NearArmWithoutHand','ShoulderNear','HelmetForeground','NearHand')
MANIFESTS = {
 'Ready': P/'fairytale-lgt-readability-v003/ready-import-v001/import-leather-ready-v001.json',
 '258J1': P/'fairytale-hero-four-pose-polish-v001/request258-primary1-body-correction/UE-import-binding-candidate-v001/import/import-manifest-v001.json',
 'oldJ2': P/'fairytale-lgt-readability-v003/primary1-import-v001/import-leather-primary1-v001.json'}
# These are unviewed numerical placement proposals, not measured skeletal attachment points.
PLANS = [
 (0,'Ready',0,'ShoulderFar',6,2),(0,'Ready',0,'Chest',1,1),(0,'Ready',0,'ShoulderNear',0,0),
 (1,'258J1',1,'ShoulderFar',-9,-16),(1,'258J1',1,'Chest',-15,-12),(1,'258J1',1,'ShoulderNear',-19,-30),
 (2,'258J1',1,'ShoulderFar',2,-14),(2,'258J1',1,'Chest',-8,-12),(2,'258J1',1,'ShoulderNear',-7,-42),
 (3,'oldJ2',2,'ShoulderFar',-112,-40),(3,'oldJ2',2,'Chest',-15,-18),(3,'oldJ2',2,'ShoulderNear',50,-14)]
FEATURES = {'Ready':{'Chest':[259,271],'ShoulderFar':[294,253],'ShoulderNear':[207,265]},
 '258J1':{'Chest':[266,278],'ShoulderFar':[301,271],'ShoulderNear':[205,273]},
 'oldJ2':{'Chest':[270,266],'ShoulderFar':[299,260],'ShoulderNear':[245,260]}}
DEP = {}
def pin(path):
 p=Path(path).resolve();b=p.read_bytes();r={'path':p.as_posix(),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()};DEP[r['path']]=r;return r
def verify_pin(r):
 p=Path(r['path']);assert p.is_absolute();actual=pin(p);assert actual==r, ('pin mismatch',actual,r)
def load(path):
 pin(path);im=Image.open(path);assert im.mode=='RGBA' and im.size==(512,512),(path,im.mode,im.size);return np.array(im)
def bbox(mask):
 yy,xx=np.where(mask);return [int(xx.min()),int(yy.min()),int(xx.max()+1),int(yy.max()+1)] if len(xx) else None
def stats(a):
 return {'canvas':[512,512],'alpha_gt0_bbox':bbox(a[:,:,3]>0),'alpha128_bbox':bbox(a[:,:,3]>=128),'alpha_gt0_pixels':int((a[:,:,3]>0).sum()),'alpha128_pixels':int((a[:,:,3]>=128).sum()),'RGBA_decoded_sha256':hashlib.sha256(a.tobytes()).hexdigest()}
def save(rel,a):
 p=HERE/rel;p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('xb') as f: Image.fromarray(a).save(f,format='PNG')
 return {'relative_path':rel,'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def dump(rel,d):
 p=HERE/rel
 with p.open('x',encoding='utf-8',newline='\n') as f:json.dump(d,f,ensure_ascii=False,indent=2);f.write('\n')
def translate(a,dx,dy):
 assert type(dx) is int and type(dy) is int
 o=np.zeros_like(a);sx=max(0,-dx);sy=max(0,-dy);ex=min(512,512-dx);ey=min(512,512-dy)
 o[sy+dy:ey+dy,sx+dx:ex+dx]=a[sy:ey,sx:ex]
 kept=np.zeros((512,512),bool);kept[sy:ey,sx:ex]=True
 clipped=int((np.any(a!=0,axis=2)&~kept).sum());assert clipped==0
 restored=np.zeros_like(a);restored[sy:ey,sx:ex]=o[sy+dy:ey+dy,sx+dx:ex+dx]
 assert np.array_equal(restored,a)
 return o,{'integer_translation_xy':[dx,dy],'rotation_degrees':0,'scale_xy':[1,1],'canvas_crop_nonzero_RGBA_pixels':clipped,'inverse_translation_RGBA_byte_exact':True}
def compose(arrays):
 o=Image.new('RGBA',(512,512))
 for a in arrays:o=Image.alpha_composite(o,Image.fromarray(a))
 return np.array(o)
def full_overlay_evidence(base,layer,protected):
 # Exact PIL source-over delta at supplied source pixel mask; do not infer anatomical meaning.
 result=compose([base,layer]);m=protected&(base[:,:,3]>0);changed=m&np.any(result!=base,axis=2)
 return {'mask_pixels':int(m.sum()),'source_RGBA_changed_pixels_after_overlay':int(changed.sum()),'changed_bbox':bbox(changed)}
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--body-owner-freeze',type=Path,required=True);args=ap.parse_args()
 worker=C/'request260-body-owner-candidate-v001'
 assert args.body_owner_freeze.resolve().parent==worker.resolve()
 wf=json.loads(args.body_owner_freeze.read_text(encoding='utf-8-sig'));pin(args.body_owner_freeze)
 # Worker freeze is provenance and is validated without weakening its own relative/absolute membership schema.
 members=wf.get('files',wf.get('members',[]));assert members, 'body owner freeze has no members'
 for r in members:
  path=Path(r.get('path',r.get('relative_path','')))
  if not path.is_absolute():
   assert '..' not in path.parts
   path=(worker/path).resolve();assert path.is_relative_to(worker.resolve())
  assert path.is_file();b=path.read_bytes();assert len(b)==r['bytes'] and hashlib.sha256(b).hexdigest()==r['sha256']
 manifests={k:json.loads(v.read_text(encoding='utf-8-sig')) for k,v in MANIFESTS.items()}
 for p in MANIFESTS.values():pin(p)
 renderer=P.parent.parent/'UnrealGame/Source/CodexDungeon/DungeonFairytaleSwordPresentation.cpp'
 pin(renderer)
 for p in [P/'fairytale-lgt-readability-v003/ready-visible-mounts-v001/mounts-v001.json',P/'fairytale-lgt-readability-v003/primary1-visible-mounts-v001/all18-mounts-v002.json',C/'request260-extraction-qc-v001/request260-extraction-final-freeze-v001.json']:pin(p)
 rows=[];frames=[];out={}
 for f in range(4):
  body=load(C/f'request260-extraction-qc-v001/aligned512/K{f}-body-footline464-RGBA.png')
  owner_arrays={o:load(worker/f'body-layers/{o}/K{f}.png') for o in OWNERS}
  union=np.zeros((512,512),np.uint8)
  for a in owner_arrays.values():
   m=a[:,:,3]>0;union+=m;assert np.array_equal(a[m],body[m])
  assert (union<=1).all() and np.array_equal(union>0,body[:,:,3]>0)
  merged=np.zeros_like(body)
  for a in owner_arrays.values():merged[a[:,:,3]>0]=a[a[:,:,3]>0]
  assert np.array_equal(merged,body), 'body owners fail source union'
  far_path=worker/f'protection-masks/FarHandWarmHullHeuristic/K{f}.png'
  assert far_path.is_file(), ('Need actual far hand protection mask and role',far_path)
  far_im=Image.open(far_path);assert far_im.size==(512,512)
  pin(far_path);far_mask=np.array(far_im.convert('L'))>0
  near_mask=owner_arrays['NearHand'][:,:,3]>0
  helmet_mask=owner_arrays['HelmetForeground'][:,:,3]>0
  rgb=body[:,:,:3].astype(int);grey=(body[:,:,3]>=128)&(rgb.max(2)-rgb.min(2)<=35)&(rgb[:,:,0]>=30)&(rgb[:,:,0]<=170)
  arrays={**owner_arrays};frame_rows=[]
  for _,family,sf,component,dx,dy in [r for r in PLANS if r[0]==f]:
   r=next(r for r in manifests[family]['assets'] if r['frame']==sf and r['component']==component)
   src=r['source'];sp=Path(src if isinstance(src,str) else src['path'])
   expected=src if isinstance(src,dict) else {'path':sp.as_posix(),'bytes':r['source_bytes'],'sha256':r['source_sha256']}
   verify_pin(expected);a=load(sp);translated,proof=translate(a,dx,dy)
   dest=save(f'armor-layers/{component}/K{f}.png',translated);arrays[component]=translated
   solid=translated[:,:,3]>=128;vis=translated[:,:,3]>0
   feature=FEATURES[family][component];target=[feature[0]+dx,feature[1]+dy]
   row={'K_frame':f,'owner':component,'existing_family':family,'existing_frame':sf,'source':expected,'existing_object_path':r['object_path'],'source_stats':stats(a),'candidate':dest,'candidate_stats':stats(translated),'transform':proof,
    'source_visible_feature_px':feature,'candidate_same_feature_px':target,'placement_role':'Unviewed numerical cloth/hand-aware proposal. Existing source feature is visible clasp/stitch/tip, not skeleton or measured new attachment.',
    'fit_metrics':{'armor_alpha128_outside_body_alpha128_pixels':int((solid&(body[:,:,3]<128)).sum()),'armor_gt0_outside_body_gt0_pixels':int((vis&(body[:,:,3]==0)).sum()),'neutral_cloth_color_heuristic_alpha128_overlap_pixels':int((solid&grey).sum()),'near_hand_owner_alpha_gt0_overlap_pixels':int((vis&near_mask).sum()),'far_hand_protection_mask_overlap_pixels':int((vis&far_mask).sum()),'helmet_owner_alpha_gt0_overlap_pixels':int((vis&helmet_mask).sum())},
    'source_pixels_modified':False,'fit_accepted':False}
   rows.append(row);frame_rows.append(row)
  diagnostic=compose([arrays[o] for o in ORDER]);assembly=save(f'diagnostic-assembly-no-sword/K{f}.png',diagnostic)
  # Full stack keeps near hand last; far hand remains BodyRest and needs a real clear mask.
  near_evidence=full_overlay_evidence(body,compose([arrays[o] for o in ORDER[1:] if o not in OWNERS]),near_mask)
  # Compare exact final pixels, not only raw overlap, to expose source-over edge behavior.
  near_final=near_mask&np.any(diagnostic!=body,axis=2)
  far_final=far_mask&(body[:,:,3]>0)&np.any(diagnostic!=body,axis=2)
  frames.append({'K_frame':f,'body':pin(C/f'request260-extraction-qc-v001/aligned512/K{f}-body-footline464-RGBA.png'),'body_stats':stats(body),'owner_union_exclusive_and_RGBA_exact':True,'body_owners':{o:pin(worker/f'body-layers/{o}/K{f}.png') for o in OWNERS},'far_hand_protection':pin(far_path),'far_hand_mask_role':'Worker warm color convex hull heuristic clipped to source alpha; not approved full hand anatomy.','source_order_without_independent_sword':list(ORDER),'assembly':assembly,'near_hand_final_RGBA_changed_pixels':int(near_final.sum()),'near_hand_final_alpha255_RGBA_changed_pixels':int((near_final&(body[:,:,3]==255)).sum()),'far_hand_final_RGBA_changed_pixels':int(far_final.sum()),'far_hand_changed_bbox':bbox(far_final),'armor_alone_behind_near_hand_evidence':near_evidence,'fit_accepted':False})
 report={'schema':'request260-reused-LGT-integer-fit-candidate-v001','created_utc':datetime.now(timezone.utc).isoformat(),'scope':'Twelve existing armor PNG layers translated on 512 canvas; four diagnostic no-sword source-order assemblies; no generation, painting, alpha cleanup, resampling or rotation.',
 'toolchain':{'python':platform.python_version(),'pillow':PIL_VERSION,'numpy':np.__version__},'renderer_readonly_pin':pin(renderer),'renderer_contract':{'Ready_three_armor_owners_namespace':'/Game/Production/ArtTrials/EV048/v012/HeroLeatherReady','Primary1_J0_J1_258_optin_namespace':'/Game/Production/ArtTrials/Request258/v001/HeroPrimary1Bridge','Primary1_J2_to5_namespace':'/Game/Production/ArtTrials/EV048/v013/HeroLeatherPrimary1','armor_owners':list(ARMOR),'native_facing':1,'source_canvas':[512,512],'display_root':[256,464],'independent_sword_omitted':True},'body_owner_freeze':pin(args.body_owner_freeze),'layers':rows,'frames':frames,
 'all_12_inverse_translation_RGBA_byte_exact':all(r['transform']['inverse_translation_RGBA_byte_exact'] for r in rows),'all_nonzero_RGBA_clipped_pixels':sum(r['transform']['canvas_crop_nonzero_RGBA_pixels'] for r in rows),'art_fit_accepted':False,'formal_complete_units':0,'Root_F_E_retention_required_before_View':True,'images_viewed':False,'runtime_imported':False,
 'open':['Source integer closure only proves original pixels and geometry were retained, not anatomical fit.','Far hand protection mask semantics are the body worker proposal and need Root visual review; no automatic full hand guarantee.','K3 old J2 shoulder shapes retain their existing orientation; translation cannot resolve a wrong perspective or silhouette.','Near hand is restored last but source-over of partial alpha boundaries can change edge RGBA; separately measured.','Independent sword and K Grip / Axis markers are omitted and unapproved.','No timing, GPU, native viewport, motion continuity, audio or full equipment unit closure is claimed.']}
 assert len(rows)==12 and report['all_nonzero_RGBA_clipped_pixels']==0
 dump('LGT-fit-metrics-v001.json',report)
 dependencies=list(DEP.values())
 for _ in range(2):
  for r in dependencies:verify_pin(r)
 dump('source-pin-verification-v001.json',{'schema':'request260-LGT-source-pin-verification-v001','passes':2,'mismatches':0,'source_pixel_reversible_layers':12,'dependency_count':len(dependencies),'Source_Content_tools_E_ledger_status_mutated':False})
 dump('LGT-source-inputs-v001.json',{'schema':'request260-LGT-input-pins-v001','dependencies':dependencies})
 print(json.dumps({'layers':12,'frames':4,'nonzero_RGBA_clipped':0,'rows':[{'K':r['K_frame'],'owner':r['owner'],'family':r['existing_family'],'delta':r['transform']['integer_translation_xy'],'metrics':r['fit_metrics']} for r in rows],'hand_final':[{'K':r['K_frame'],'near_RGBA':r['near_hand_final_RGBA_changed_pixels'],'near_opaque':r['near_hand_final_alpha255_RGBA_changed_pixels'],'far_RGBA':r['far_hand_final_RGBA_changed_pixels']} for r in frames]},ensure_ascii=False))
if __name__=='__main__':main()
