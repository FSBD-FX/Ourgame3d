"""No rendering; actual shared241 aperture vs visible authored buckle/body targets."""
from pathlib import Path
import ast,hashlib,json,sys
from collections import deque
import numpy as np
from PIL import Image,ImageDraw
HERE=Path(__file__).resolve().parent;SG=Path('C:/Users/22499/.codex/skills/sprite-gen')
assert Path(sys.executable).resolve()==(SG/'.venv/Scripts/python.exe').resolve()
sys.path.insert(0,str(SG));import sprite_gen.frames.extract as native
OUT=HERE/'Chest241-postextract-two-point-feasibility-v001';assert not OUT.exists() or not any(OUT.iterdir());OUT.mkdir(exist_ok=True)
def pin(p):
 b=p.read_bytes();return {'path':p.as_posix(),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,v):
 with p.open('x',encoding='utf-8',newline='\n') as f:json.dump(v,f,ensure_ascii=False,indent=2);f.write('\n')
 return p
SOURCE=HERE/'analyze-Chest241-edit-preservation-and-targets-v001.py'
assert pin(SOURCE)['sha256']=='67f910e06885afb0318bed5ff998b311dc334421d92b240cc50e9aa509be59eb'
# Reuse read-only numeric helper definitions only; no top-level output mutation.
tree=ast.parse(SOURCE.read_text(encoding='utf-8-sig'));tree.body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['closed','gold_buckle']]
scope={'np':np,'Image':Image,'ImageDraw':ImageDraw,'deque':deque,'native':native};exec(compile(tree,str(SOURCE),'exec'),scope)
REC=HERE/'official-process-runs-v001/chest-native241/run-shared-HD-v001/extraction-receipt-v001.json';rec=read(REC)
PROOF=HERE/'Chest241-local-raw240-edit-input-v001/actual240-raw-curated-inverse-and-outside-target-proof-v001.json';proof=read(PROOF)
OLDREC=HERE/'official-process-runs-v001/chest-native240/run-shared-HD-v001/extraction-receipt-v001.json';oldrec=read(OLDREC)
FIT=HERE/'LGT240-235-236-original-owner-integer-fit-v001/Dodge218-Chest240-Near235-Far236-original-owner-SWD050-integer-fit-candidate-v001.json';fit=read(FIT)
oldraw=np.array(Image.open(oldrec['F_raw']['path']).convert('RGBA'));newraw=np.array(Image.open(rec['F_raw']['path']).convert('RGBA'))
assert pin(Path(rec['F_raw']['path']))==rec['F_raw']
key=native.remove_chroma_background(Image.fromarray(newraw),(0,255,0),96.,180.,18.,unmix_reach=4,spill_max_fraction=.005)
seeds=sorted(sorted(native.connected_components(key),key=lambda x:x['area'],reverse=True)[:4],key=lambda x:x['center_x'])
rows=[]
for i in range(4):
 old=oldrec['shared_row_fit']['frame_records'][i];o=proof['rows'][i];f=fit['frames'][i]['armor_integer_fits']['Chest'];Aold=np.array(f['A_artist_visible_component_xy'],float)
 oldeff=np.array(old['resampled_size'],float)/old['source_component_size'];oldBraw=np.array(o['raw_component_bbox_xyxy'][:2])+(Aold-np.array(old['placement_xy'])+.5)/oldeff-.5
 g=[scope['gold_buckle'](a,oldBraw) for a in [oldraw,newraw]];gd=np.array(g[1]['centroid_xy'])-g[0]['centroid_xy'];Braw=oldBraw+gd
 nr=rec['shared_row_fit']['frame_records'][i];eff=np.array(nr['resampled_size'],float)/nr['source_component_size'];origin=np.array(seeds[i]['bbox'][:2]);place=np.array(nr['placement_xy']);A=(Braw-origin+.5)*eff-.5+place
 cp=Path(rec['frames'][i]['curated']['path']);im=Image.open(cp).convert('RGBA');a=np.array(im);assert hashlib.sha256(a.tobytes()).hexdigest()==rec['frames'][i]['RGBA_sha256']
 h=scope['closed'](a);C=h[0]['centroid'];B=np.array(f['B_artist_visible_body_surface_xy'],float);J=np.array(f['visible_source_sleeve_torso_junction_artist_xy'],float)
 D=np.rint(B-A).astype(int);res=C+D-J;belt=A+D-B
 choices=[]
 for dx in range(int(D[0])-40,int(D[0])+41):
  for dy in range(int(D[1])-40,int(D[1])+41):
   d=np.array([dx,dy]);jr=C+d-J;br=A+d-B;score=max(np.linalg.norm(jr),np.linalg.norm(br));choices.append((float(score),int(dx),int(dy),jr,br))
 best=min(choices,key=lambda x:(x[0],np.linalg.norm(x[3])+np.linalg.norm(x[4]),x[1],x[2]))
 rows.append({'frame':i,'curated':pin(cp),'curated_RGBA_sha256':hashlib.sha256(a.tobytes()).hexdigest(),'actual_near_hole_centroid_source_xy':C.tolist(),'actual_neck_hole_centroid_source_xy':h[1]['centroid'].tolist(),'old_raw_buckle_artist_xy':oldBraw.tolist(),'visible_gold_feature_delta_raw_xy':gd.tolist(),'tracked_buckle_raw_artist_xy':Braw.tolist(),'tracked_buckle_curated_artist_xy':A.tolist(),'marker_authority':'artist point transported only by actual local gold feature displacement; +-3raw pixels material tracking uncertainty; no hidden bones or measured handle axis','actual_shared_density':rec['shared_row_fit']['scale'],'actual_rounded_scale_xy':eff.tolist(),'body_buckle_artist_xy':B.tolist(),'body_near_sleeve_junction_artist_xy':J.tolist(),'belt_anchored_integer_delta':D.tolist(),'belt_residual_source_xy':belt.tolist(),'nearhole_junction_residual_source_xy':res.tolist(),'source_armhole_to_buckle_vector_xy':(A-C).tolist(),'desired_body_J_to_B_vector_xy':(B-J).tolist(),'best_finite_integer_two_point_fit':{'delta_xy':[best[1],best[2]],'max_residual_source_px':best[0],'junction_residual_xy':best[3].tolist(),'belt_residual_xy':best[4].tolist()},'estimate_at72_over416_display':{'belt_anchored_junction_error_px':float(np.linalg.norm(res)*72/416),'best_two_point_max_error_px':float(best[0]*72/416)},'sourcefit_accepted':False})
out={'schema':'Chest241-actual-shared-extraction-two-visible-point-feasibility-v001','receipt241':pin(REC),'receipt240':pin(OLDREC),'sourcefit240':pin(FIT),'target_proof':pin(PROOF),'readonly_helpers':pin(SOURCE),'shared_row_scale_constant':rec['shared_row_fit']['scale'],'no_individual_frame_resize':True,'no_body_or_armor_pixels_modified':True,'newmedia_View':False,'rows':rows,'TrialAllowed':False,'FinalAccepted':False,'conclusion':'Actual241 improves nearholes, but two-point mismatch remains. Integer translation cannot make both authored sleeve junction and buckle exact; source material drift and all original warnings remain. A finite original-owner preview is review evidence only, not repair or acceptance.'}
p=write(OUT/'Chest241-actual-shared-aperture-buckle-body-two-point-feasibility-v001.json',out)
write(OUT/'feasibility-files-freeze-v001.json',{'script':pin(Path(__file__)),'files':[pin(p)],'rendered_media':False})
print(json.dumps({'report':pin(p),'rows':rows},ensure_ascii=False,indent=2))
