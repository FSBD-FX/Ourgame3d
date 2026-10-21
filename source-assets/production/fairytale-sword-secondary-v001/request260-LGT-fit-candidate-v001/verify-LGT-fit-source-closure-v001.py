import argparse, hashlib, json, sys
from pathlib import Path
import numpy as np
from PIL import Image
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def pin(p):
 p=Path(p).resolve();b=p.read_bytes();return {'path':p.as_posix(),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def check(r):
 actual=pin(r['path']);assert actual==r, ('pin mismatch',actual,r)
def arr(p):
 im=Image.open(p);assert im.size==(512,512) and im.mode=='RGBA';return np.array(im)
def bbox(m):
 y,x=np.where(m);return [int(x.min()),int(y.min()),int(x.max()+1),int(y.max()+1)] if len(x) else None
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--check-only',action='store_true');args=ap.parse_args()
 d=read(HERE/'LGT-fit-metrics-v001.json');inputs=read(HERE/'LGT-source-inputs-v001.json')['dependencies']
 for _ in range(2):
  for r in inputs:check(r)
 assert len(d['layers'])==12
 results=[]
 for frame in d['frames']:
  f=frame['K_frame'];body=arr(frame['body']['path']);order=frame['source_order_without_independent_sword']
  aa={o:arr(v['path']) for o,v in frame['body_owners'].items()}
  armorrows=[r for r in d['layers'] if r['K_frame']==f]
  for r in armorrows:
   a=arr(r['source']['path']);out=arr(HERE/r['candidate']['relative_path']);dx,dy=r['transform']['integer_translation_xy'];expected=np.zeros_like(a)
   sy=max(0,-dy);sx=max(0,-dx);ey=min(512,512-dy);ex=min(512,512-dx)
   expected[sy+dy:ey+dy,sx+dx:ex+dx]=a[sy:ey,sx:ex]
   restored=np.zeros_like(a);restored[sy:ey,sx:ex]=out[sy+dy:ey+dy,sx+dx:ex+dx]
   assert np.array_equal(out,expected) and np.array_equal(restored,a)
   aa[r['owner']]=out
  product=np.ones((512,512),float);layers={}
  for o in reversed(order):
   a=aa[o][:,:,3].astype(float)/255;w=a*product
   layers[o]={'positive_source_contribution_pixels':int((w>0).sum()),'source_contribution_at_least_half_pixels':int((w>=0.5).sum()),'effective_alpha_sum':round(float(w.sum()),6),'positive_contribution_bbox':bbox(w>0)}
   if o in ('ShoulderFar','Chest','ShoulderNear'):
    layers[o]['raw_overlap_with_each_body_owner_gt0']={k:int(((aa[o][:,:,3]>0)&(a2[:,:,3]>0)).sum()) for k,a2 in aa.items() if k in frame['body_owners']}
   product*=1-a
  canvas=Image.new('RGBA',(512,512))
  for o in order:canvas=Image.alpha_composite(canvas,Image.fromarray(aa[o]))
  final=np.array(canvas);assert np.array_equal(final,arr(HERE/frame['assembly']['relative_path']))
  near=aa['NearHand'][:,:,3]>0;far=np.array(Image.open(frame['far_hand_protection']['path']).convert('L'))>0
  assert np.array_equal(final[near],body[near]) and np.array_equal(final[far],body[far])
  features=[]
  for r in armorrows:
   sx,sy=r['source_visible_feature_px'];tx,ty=r['candidate_same_feature_px'];a=arr(r['source']['path']);out=aa[r['owner']]
   assert np.array_equal(a[sy,sx],out[ty,tx])
   features.append({'owner':r['owner'],'source_px':[sx,sy],'translated_px':[tx,ty],'RGBA':a[sy,sx].tolist(),'exact_RGBA':True})
  results.append({'K_frame':f,'assembly_alpha_gt0_bbox':bbox(final[:,:,3]>0),'body_alpha_gt0_bbox':bbox(body[:,:,3]>0),'body_foot_alpha_boundary':bbox(body[:,:,3]>0)[3],'assembly_foot_alpha_boundary':bbox(final[:,:,3]>0)[3],'armor_contributions':{o:layers[o] for o in ('ShoulderFar','Chest','ShoulderNear')},'source_visible_features':features,'full_order_recomposite_RGBA_exact':True,'near_hand_supplied_owner_RGBA_exact':True,'far_hand_supplied_heuristic_RGBA_exact':True})
 report={'schema':'request260-LGT-source-closure-and-depth-qc-v001','dependency_pin_passes':2,'dependency_pin_mismatches':0,'layers_reverse_RGBA_exact':12,'four_source_order_assemblies_RGBA_exact':True,'body_worker_semantic_mask_still_unaccepted':True,'no_independent_sword':True,'frames':results,'fit_accepted':False,'images_viewed':False,'GPU_native_motion_audio_closure':'OPEN'}
 if not args.check_only:
  with (HERE/'LGT-depth-source-closure-v001.json').open('x',encoding='utf-8',newline='\n') as f:json.dump(report,f,ensure_ascii=False,indent=2);f.write('\n')
 print(json.dumps({'verified_layers':12,'verified_frames':4,'pins':len(inputs),'pin_passes':2,'mismatches':0,'visible_armor':[{'K':r['K_frame'],'owners':{o:v['positive_source_contribution_pixels'] for o,v in r['armor_contributions'].items()}} for r in results]}))
if __name__=='__main__':main()
