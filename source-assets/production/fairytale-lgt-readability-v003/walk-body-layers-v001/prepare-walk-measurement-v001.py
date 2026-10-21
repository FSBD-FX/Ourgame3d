"""Deterministic Walk source copies and technical measurement aids only."""
from pathlib import Path
from datetime import datetime
import hashlib,json,shutil
import numpy as np
from PIL import Image,ImageDraw,ImageFont
ROOT=Path('F:/Ourgame');HERE=Path(__file__).resolve().parent
MANIFEST=ROOT/'source-assets/production/fairytale-walk-lookdev-v001/manifests/import-walk-lookdev-v001.json'
RECEIPT=ROOT/'UnrealGame/Saved/Bootstrap/fairytale-walk-lookdev-v001-import-20261015-193357-409584.json'
REG=ROOT/'source-assets/production/fairytale-hero-v001/sprite-run-walk-v008/source-cell-registration-receipt.json'
def pin(p):
 b=p.read_bytes();return {'path':p.as_posix(),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def new(n,value):
 p=HERE/n;p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('x',encoding='utf-8',newline='\n') as f:f.write(value if isinstance(value,str) else json.dumps(value,ensure_ascii=False,indent=2)+'\n')
 return p
def png(p,a):
 p.parent.mkdir(parents=True,exist_ok=True);assert not p.exists();Image.fromarray(a).save(p)
 assert np.array_equal(np.asarray(Image.open(p)),a)
 return p
manifest=json.loads(MANIFEST.read_text(encoding='utf-8-sig'));receipt=json.loads(RECEIPT.read_text(encoding='utf-8-sig'));reg=json.loads(REG.read_text(encoding='utf-8-sig'))
assert pin(MANIFEST)['sha256']==receipt['manifest_sha256']
font=ImageFont.load_default(size=13)
rows=[];arrays=[];outputs=[]
for i,a in enumerate(manifest['assets']):
 assert a['frame']==i
 source=Path(a['source']);sourcepin=pin(source);assert sourcepin['bytes']==a['source_bytes'] and sourcepin['sha256']==a['source_sha256']
 dst=HERE/'source-body'/f'frame-{i}.png';dst.parent.mkdir(parents=True,exist_ok=True);assert not dst.exists();shutil.copyfile(source,dst);assert pin(dst)['sha256']==sourcepin['sha256']
 im=Image.open(dst);assert im.mode=='RGBA' and im.size==(512,512);rgba=np.asarray(im).copy();arrays.append(rgba)
 def bbox(mask):
  yy,xx=np.nonzero(mask);return [int(xx.min()),int(yy.min()),int(xx.max()+1),int(yy.max()+1)] if len(xx) else None
 rows.append({'frame':i,'native_request':reg['records'][i]['native_request'],'source':sourcepin,'byte_exact_copy':pin(dst),'RGBA_sha256':hashlib.sha256(rgba.tobytes()).hexdigest(),'canvas':[512,512],'nonzero_alpha_pixels':int((rgba[:,:,3]>0).sum()),'core_alpha_ge128_pixels':int((rgba[:,:,3]>=128).sum()),'alpha_nonzero_bbox_DIAGNOSTIC_NOT_LANDMARK':bbox(rgba[:,:,3]>0),'core_bbox_DIAGNOSTIC_NOT_LANDMARK':bbox(rgba[:,:,3]>=128),'display_pivot_NOT_MEASURED_ROOT':[256,464],'timing_ms':83,'actual_landmarks':{k:None for k in ['root','crown','helmet_lower_rim_polyline','helmet_outer_polygon','near_shoulder','far_shoulder','near_arm_polygon','near_sleeve_cuff_polyline','near_hand_full_cuff_glove_polygon','near_palm','far_hand_visible_polygon','chest_mount_B_artist_design','near_shoulder_mount_B_artist_design','far_shoulder_mount_B_artist_design','near_hip','near_knee','near_ankle','near_heel','near_toe','far_hip','far_knee','far_ankle','far_heel','far_toe','weapon_axis_artist_design']},'root_confirmed':False,'semantic_ownership_accepted':False})
 # Rulers/grid are technical overlays, never a source frame or a final asset.
 yy,xx=np.indices((608,608));checker=((xx//16+yy//16)%2)*12+28
 bg=np.stack([checker,checker,checker,np.full_like(checker,255)],axis=2).astype(np.uint8)
 canvas=Image.fromarray(bg);canvas.alpha_composite(im,(48,48))
 overlay=Image.new('RGBA',(608,608),(0,0,0,0));d=ImageDraw.Draw(overlay)
 for q in range(0,513,16):
  xy=48+q;major=q%64==0
  d.line([(xy,48),(xy,560)],fill=(55,210,220,95 if major else 32),width=1)
  d.line([(48,xy),(560,xy)],fill=(55,210,220,95 if major else 32),width=1)
  if major:
   d.text((xy-10,28),str(q),fill=(230,245,245,255),font=font)
   d.text((15,xy-7),str(q),fill=(230,245,245,255),font=font)
 d.text((48,6),f'WALK FRAME {i} | native 512 RGBA + technical grid',fill=(240,240,240,255),font=font)
 d.text((48,575),'Source x/y = shown x/y minus 48. No landmarks assigned.',fill=(240,240,240,255),font=font)
 technical=np.asarray(Image.alpha_composite(canvas,overlay));p=png(HERE/'原件'/f'measure-frame-{i}-native-grid-v001.png',technical);outputs.append(p)
contact=np.zeros((1024,1536,4),dtype=np.uint8)
for i,a in enumerate(arrays):contact[(i//3)*512:(i//3+1)*512,(i%3)*512:(i%3+1)*512]=a
cp=png(HERE/'原件/body-six-contact-native-RGBA-v001.png',contact);outputs.insert(0,cp)
for i,a in enumerate(arrays):assert np.array_equal(contact[(i//3)*512:(i//3+1)*512,(i%3)*512:(i%3+1)*512],a)
for p in outputs:
 dst=HERE/'展示副本'/p.name;dst.parent.mkdir(exist_ok=True);assert not dst.exists();shutil.copyfile(p,dst);assert pin(dst)['sha256']==pin(p)['sha256']
landmarks=new('walk-landmarks-root-confirmation-draft-v001.json',{'schema':'Walk6-visible-feature-root-confirmation-DRAFT-v001','created_local':datetime.now().astimezone().isoformat(),'purpose':'Not a rig/layer pipeline request; missing actual points deliberately null. Root must retain/view originals and confirm per-frame contours.','source_selection':'actual imported CommonWalk v008 only; not rejected old walk rows or Sword Ready/P1 masks.','layer_plan':['BodyRest','NearArmWithoutHand','HelmetForeground','NearHand'],'assignment_policy_candidate':'NearHand > HelmetForeground > NearArmWithoutHand > BodyRest, exact source-coordinate ownership only. Needs actual per-frame contours; no P2/P3 mask reuse.','required_per_frame_root_inputs':['helmet_outer_polygon','helmet_lower_rim_polyline','near_arm_polygon','near_hand_full_cuff_glove_polygon'],'null_is_not_an_inferred_joint':True,'display_pivot_is_not_foot_root':True,'frames':rows,'generation_or_import_ready':False,'semantic_accepted':False,'new_outputs_viewed':False})
idx=new('source-version-status-index-v001.json',{'schema':'Walk6-source-and-measurement-aid-index-v001','source_manifest':pin(MANIFEST),'actual_import_receipt':pin(RECEIPT),'registration_receipt':pin(REG),'source_bodies':[r['byte_exact_copy'] for r in rows],'technical_originals':[pin(p) for p in outputs],'presentation_copies':[pin(HERE/'展示副本'/p.name) for p in outputs],'body_contact_policy':'3 columns x 2 rows, frames0..5, each512RGBA copied with no resample, every RGBA byte including alpha0RGB preserved. Contact has no anatomy labels.','measurement_grid_policy':'608px image: original512 at offset48, 16px grid/64px numbered ticks. Technical overlay only, never finalart; subtract48 for actual source coordinates.','landmark_draft':pin(landmarks),'layers_created':0,'new_media_viewed':False,'E_retention_and_root_review':'PENDING; do not browse/view new outputs until Root confirms retention.','Source_UE_tools_ledger_modified':False,'formal_complete_units':0})
new('HANDOFF-preparation-v001.md','Six source-body PNGs are byte-exact copies of imported CommonWalk v008 curated0..5. 原件/body-six-contact-native-RGBA-v001.png is a 1536x1024 unscaled RGBA contact in0..5 order. Six608px measurement grids place the512 source at48,48 and deliberately assign no anatomy. 原件 and 展示副本 are exact copies of each technical helper. Root must E-retain before anyone views them. Landmarks remain null; four-owner24 layers require new actual Walk contours, no P2/P3 mask reuse. No new media viewed, no generation/UE/Source/tools/ledger/README changes.\n')
files=[pin(p) for p in sorted(HERE.rglob('*')) if p.is_file()]
freeze=new('preparation-freeze-v001.json',{'schema':'Walk6-pre-layer-measurement-preparation-freeze-v001','files':files,'source_manifest':pin(MANIFEST),'actual_import_receipt':pin(RECEIPT),'source_originals':[r['source'] for r in rows],'six_source_files_byte_exact':True,'contact_six_RGBA_cells_equal':True,'layer_count':0,'landmarks_confirmed':False,'new_outputs_viewed':False})
for r in rows:assert pin(Path(r['source']['path']))==r['source']
for f in files:assert pin(Path(f['path']))==f
print(json.dumps({'contact':pin(cp),'freeze':pin(freeze),'technical_grid_count':6,'body_copies':6,'layers_created':0,'source_mismatches':0},ensure_ascii=False,indent=2))
