from pathlib import Path
from PIL import Image
import hashlib,json
R=Path('F:/Ourgame');B=R/'source-assets/production/fairytale-lgt-readability-v003';O=B/'combo-visible-mounts-v001';assert not O.exists();O.mkdir()
def desc(p):
 b=p.read_bytes();return dict(path=p.as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
A={2:{'Chest':[(269,243),(269,244),(277,245),(278,250),(269,244),(269,244)],'NearShoulder':[(258,241),(265,245),(262,242),(250,247),(253,245),(260,242)],'FarShoulder':[(248,249),(251,251),(251,254),(250,249),(251,248),(248,248)]},3:{'Chest':[(270,246),(273,247),(276,252),(277,260),(280,262),(271,246)],'NearShoulder':[(254,265),(255,259),(250,263),(249,263),(251,263),(254,265)],'FarShoulder':[(248,249),(249,248),(247,248),(249,247),(249,250),(249,249)]}}
T={2:{'Chest':[(269,268),(269,275),(275,266),(279,269),(272,274),(269,268)],'NearShoulder':[(210,246),(211,257),(218,248),(221,237),(213,246),(210,246)],'FarShoulder':[(295,251),(296,254),(296,255),(292,249),(294,253),(295,251)]},3:{'Chest':[(270,268),(270,268),(277,269),(291,277),(294,285),(267,267)],'NearShoulder':[(208,253),(209,246),(220,242),(245,257),(244,269),(206,252)],'FarShoulder':[(296,255),(297,252),(297,257),(298,265),(300,275),(294,253)]}}
allrows=[];indices=[]
for clip,I in [(2,B/'primary2-far195-small-tab-v002/primary2-eighteen-source-index-v002.json'),(3,B/'primary3-leather-extraction-v001/primary3-eighteen-source-index-v002.json')]:
 d=load(I);indices.append(desc(I));handoff=load(B/f'primary{clip}-leather-input-v001/primary{clip}-leather-native-input-approved-v001.json');bodypins=handoff['rows'][0]['actual_runtime_body_pins'];rows=[]
 for c in d['components']:
  for f in c['frames']:
   i=f['frame'];p=Path(f['source']['path']);assert desc(p)==f['source'];im=Image.open(p).convert('RGBA');a=A[clip][c['component']][i];t=T[clip][c['component']][i];rgba=im.getpixel(a);assert rgba[3]>=128,(clip,c['component'],i,a,rgba)
   body=bodypins[i];assert desc(Path(body['path']))==body
   hidden=(clip==2 and ((c['component']=='Chest' and i in (3,4)) or (c['component']=='FarShoulder' and i==3))) or (clip==3 and ((c['component']=='Chest' and i==2) or (c['component']=='FarShoulder' and i in (2,3,4))))
   rows.append(dict(clip=clip,frame=i,component=c['component'],source=f['source'],A_source_px=a,A_observed_rgba=rgba,A_feature={'Chest':'actual visible round golden front-clasp feature','NearShoulder':('actual upper strap/rivet seam' if clip==2 else 'actual lower stitched diamond/rivet seam'),'FarShoulder':('actual narrow tab upper seam/contour' if clip==2 else 'actual top tab rivet/outer seam')}[c['component']],A_manual_visual_uncertainty_px=3,body=body,B_body_design_source_px=t,B_role=('HIDDEN TRIAL artist placement only; anatomical attachment occluded, not reconstructed or measured' if hidden else 'Root artist proposal against actually viewed current body and retained four body layers; not a measured bone'),B_design_uncertainty_px=8 if hidden else 5,integer_delta_xy=[t[0]-a[0],t[1]-a[1]],duration_ms=f['duration_ms'],fit_accepted=False))
  assert len(c['frames'])==6
 q=O/f'primary{clip}-all18-mounts-v001.json';q.write_text(json.dumps(dict(schema='root-new-leather-component-observed-A-artist-B-v1',source_index=desc(I),root_viewed_after_E=[310,311 if clip==3 else 312],rows=rows,method='A manually selected from original512 unscaled component crops; sample verifies actual opacity, uncertainty retained. B separate artist proposal; occluded B explicitly HIDDEN TRIAL. Integer translation only; no per-frame scaling/repaint or accepted fit.',fit_accepted=False,imported=False,formal_complete_units=0),ensure_ascii=False,indent=2)+'\n',encoding='utf-8');allrows.append(desc(q))
f=O/'mounts-freeze-v001.json';f.write_text(json.dumps(dict(files=allrows+[desc(Path(__file__).resolve())],source_indices=indices,total_actual_component_As=36,body_Bs_are_artist_proposals=True,formal_complete_units=0),ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(dict(freeze=desc(f),mounts=allrows),ensure_ascii=False))
