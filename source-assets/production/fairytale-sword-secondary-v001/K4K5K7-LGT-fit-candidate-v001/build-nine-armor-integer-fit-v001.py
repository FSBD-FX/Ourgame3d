import hashlib,json,shutil,sys
from pathlib import Path
from datetime import datetime,timezone
import numpy as np
from PIL import Image
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;C=HERE.parent;P=C.parent
SELECTION=C/'K8-body-selection-v001/source-body-selection.json'
M={'Ready':P/'fairytale-lgt-readability-v003/ready-import-v001/import-leather-ready-v001.json','oldJ':P/'fairytale-lgt-readability-v003/primary1-import-v001/import-leather-primary1-v001.json'}
PLANS=[(4,'oldJ',3,'ShoulderFar',-95,-43),(4,'oldJ',3,'Chest',9,3),(4,'oldJ',2,'ShoulderNear',65,8),(5,'oldJ',2,'ShoulderFar',-116,-28),(5,'oldJ',2,'Chest',-17,-6),(5,'oldJ',2,'ShoulderNear',29,-4),(7,'Ready',0,'ShoulderFar',0,0),(7,'Ready',0,'Chest',0,0),(7,'Ready',0,'ShoulderNear',0,0)]
FEATURES={('oldJ',3,'ShoulderFar'):[294,264],('oldJ',3,'Chest'):[270,275],('oldJ',2,'ShoulderFar'):[299,260],('oldJ',2,'Chest'):[270,266],('oldJ',2,'ShoulderNear'):[245,260],('Ready',0,'ShoulderFar'):[294,253],('Ready',0,'Chest'):[259,271],('Ready',0,'ShoulderNear'):[207,265]}
DEPS={}
def pin(p):
 p=Path(p).resolve();b=p.read_bytes();r={'path':p.as_posix(),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()};DEPS[r['path']]=r;return r
def exact(r):assert pin(r['path'])==r
def arr(p):
 pin(p);im=Image.open(p);assert im.mode=='RGBA' and im.size==(512,512);return np.array(im)
def box(m):
 y,x=np.where(m);return [int(x.min()),int(y.min()),int(x.max()+1),int(y.max()+1)] if len(x) else None
def stat(a):return {'bbox_alpha1':box(a[:,:,3]>0),'bbox_alpha128':box(a[:,:,3]>=128),'alpha1_area':int((a[:,:,3]>0).sum()),'alpha128_area':int((a[:,:,3]>=128).sum()),'RGBA_sha256':hashlib.sha256(a.tobytes()).hexdigest()}
def write(n,d):
 with (HERE/n).open('x',encoding='utf-8',newline='\n') as f:json.dump(d,f,ensure_ascii=False,indent=2);f.write('\n')
def main():
 assert pin(SELECTION)['sha256']=='d81bf3eebfbbd3238359a61a5972ec6f16639b43461d44e00f6b4b38aa30d951';assert pin(SELECTION)['bytes']==5246
 sel=json.loads(SELECTION.read_text());assert sel['frame6_reuses0'] and sel['frame7_uses_original_ready']
 selected={r['frame']:r for r in sel['frames']};assert set(selected)==set(range(8))
 for f in (4,5,7):exact(selected[f]['source'])
 manifests={k:json.loads(v.read_text()) for k,v in M.items()}
 for v in M.values():pin(v)
 for q in [P/'fairytale-lgt-readability-v003/ready-visible-mounts-v001/mounts-v001.json',P/'fairytale-lgt-readability-v003/primary1-visible-mounts-v001/all18-mounts-v002.json']:pin(q)
 rows=[]
 for f,family,sf,owner,dx,dy in PLANS:
  source=next(r for r in manifests[family]['assets'] if r['frame']==sf and r['component']==owner);sr={'path':source['source'],'bytes':source['source_bytes'],'sha256':source['source_sha256']};exact(sr);a=arr(sr['path']);body=arr(selected[f]['source']['path'])
  sx=max(0,-dx);sy=max(0,-dy);ex=min(512,512-dx);ey=min(512,512-dy);out=np.zeros_like(a);out[sy+dy:ey+dy,sx+dx:ex+dx]=a[sy:ey,sx:ex]
  restored=np.zeros_like(a);restored[sy:ey,sx:ex]=out[sy+dy:ey+dy,sx+dx:ex+dx];assert np.array_equal(restored,a)
  dest=HERE/f'armor-layers/{owner}/K{f}.png';dest.parent.mkdir(parents=True,exist_ok=True)
  if f==7:
   assert (dx,dy)==(0,0);assert not dest.exists();shutil.copyfile(sr['path'],dest);assert dest.read_bytes()==Path(sr['path']).read_bytes()
  else:
   with dest.open('xb') as h:Image.fromarray(out).save(h,format='PNG')
  assert np.array_equal(np.array(Image.open(dest)),out)
  rgb=body[:,:,:3].astype(int);neutral=(body[:,:,3]>=128)&(rgb.max(2)-rgb.min(2)<=35)&(rgb[:,:,0]>=30)&(rgb[:,:,0]<=170);solid=out[:,:,3]>=128;vis=out[:,:,3]>0
  feature=FEATURES[family,sf,owner];target=[feature[0]+dx,feature[1]+dy];assert np.array_equal(a[feature[1],feature[0]],out[target[1],target[0]])
  b=dest.read_bytes();candidate={'relative_path':dest.relative_to(HERE).as_posix(),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
  rows.append({'K_frame':f,'owner':owner,'existing_family':family,'existing_frame':sf,'source':sr,'existing_object_path':source['object_path'],'source_stats':stat(a),'candidate':candidate,'candidate_stats':stat(out),'transform':{'integer_translation_xy':[dx,dy],'rotation_degrees':0,'scale_xy':[1,1],'inverse_translation_RGBA_byte_exact':True,'nonzero_RGBA_clipped_pixels':0},'canonical_Ready0_source_PNG_byte_identical':f==7,'source_feature_px':feature,'same_feature_candidate_px':target,'feature_source_and_candidate_RGBA':a[feature[1],feature[0]].tolist(),'source_feature_role':'Existing visible clasp/stitch/tip. Destination is unviewed numerical cloth proposal, not measured skeleton.','preliminary_metrics':{'alpha128_outside_body_alpha128':int((solid&(body[:,:,3]<128)).sum()),'alpha1_outside_body_alpha1':int((vis&(body[:,:,3]==0)).sum()),'neutral_cloth_color_heuristic_overlap':int((solid&neutral).sum())},'source_pixels_modified':False,'fit_accepted':False})
 deps=list(DEPS.values())
 for _ in range(2):
  for r in deps:exact(r)
 report={'schema':'K4K5K7-LGT-nine-integer-layers-preparation-v001','created_utc':datetime.now(timezone.utc).isoformat(),'selection':pin(SELECTION),'selected_body_sources':{str(f):selected[f]['source'] for f in (4,5,7)},'K6':'Alias already prepared K0 body and armor; no K6 file/import created.','armor_layer_count':9,'layers':rows,'dependencies':deps,'source_pin_verification_passes':2,'source_pin_mismatches':0,'no_scale_warp_generation_painting':True,'all_RGBA_inverse_translations_exact':True,'canonical_K7_Ready0_all3_PNG_bytes_exact':True,'future_source_order_no_sword':['BodyRest','ShoulderFar','Chest','NearArmWithoutHand','ShoulderNear','HelmetForeground','NearHand'],'owner_mask_check':'PENDING separate frozen K4/K5/K7 four-body-owner candidate; raw overlay cannot prove correct hand or helmet occlusion.','assemblies':'PENDING body owner freeze; no temporary whole-body overpaint presented as final.','images_viewed':False,'source_Content_tools_E_status_ledger_changed':False,'fit_accepted':False,'runtime_imported':False,'FinalAccepted':False}
 write('nine-armor-source-recipe-v001.json',report)
 print(json.dumps({'layers':9,'deps':len(deps),'all_RGBA_reversible':True,'K7_source_PNG_byte_exact':True,'preliminary':[{'K':r['K_frame'],'owner':r['owner'],'source':r['existing_family']+str(r['existing_frame']),'delta':r['transform']['integer_translation_xy'],'metrics':r['preliminary_metrics']} for r in rows]}))
if __name__=='__main__':main()
