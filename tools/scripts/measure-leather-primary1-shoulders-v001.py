from pathlib import Path
import json,hashlib
from PIL import Image
R=Path('F:/Ourgame');D=R/'source-assets/production/fairytale-lgt-readability-v003';B=D/'primary1-visible-mounts-v001';B.mkdir(exist_ok=False)
def pin(p):
 b=p.read_bytes();return dict(path=p.as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
idx=D/'primary1-leather-extraction-v001/primary1-eighteen-source-index-v001.json';assert pin(idx)['sha256']=='799b18baea21626900cab0e1fc728d6124496b468e5d9869894a1507fa8bac30'
data=json.loads(idx.read_text(encoding='utf-8-sig'))
# Actual manually selected source pixels, after Root viewed all six E289 sheets.
# Target B is a proposed artist placement, never a measured bone or hidden joint.
points={
 'NearShoulder':dict(A=[(263,264),(258,264),(269,261),(258,264),(263,261),(258,264)],B=[(207,265),(220,249),(245,260),(242,273),(207,265),(207,265)],feature='visible diamond stitch in lower part of the leather cap'),
 'FarShoulder':dict(A=[(250,247),(252,243),(251,244),(248,251),(253,247),(255,246)],B=[(294,253),(306,265),(299,273),(300,291),(294,253),(294,253)],feature='visible upper tip of the narrow leather tab at its ink/leather boundary')}
rows=[]
for c in data['components']:
 if c['component'] not in points:continue
 p=points[c['component']]
 for i,f in enumerate(c['frames']):
  q=Path(f['source']['path']);assert pin(q)==f['source'];aa=p['A'][i];bb=p['B'][i];rgba=Image.open(q).getpixel(aa);assert rgba[3]>0
  body=R/f'source-assets/production/fairytale-sword-v001/run-primary1-v001/curated/frame-{i}.png'
  rows.append(dict(frame=i,component=c['component'],source=pin(q),A_source_px=aa,A_observed_rgba=rgba,A_feature=p['feature'],A_manual_visual_uncertainty_px=3,B_body_design_source_px=bb,B_role='Root artist proposal against actually viewed Body159; not measured bones; hidden source features remain unmeasured',B_design_uncertainty_px=8 if i in [1,2,3] else 3,integer_delta_xy=[bb[0]-aa[0],bb[1]-aa[1]],body=pin(body),duration_ms=[85,85,60,60,155,155][i]))
out=B/'shoulder-mounts-v001.json';out.write_text(json.dumps(dict(schema='primary1-actual-shoulder-feature-mounts-v001',source_index=pin(idx),source_feature_review='F:/Ourgame/过程图稿与视频/2026-10-17_软皮第一刀十八帧挂点审阅_v001',E_feature_retention='E:/OurGame/Knight/过程图稿与视频/2026-10-17-OurgameUE-leather-primary1-extracted-features-v289/source-size-SHA256.json',root_actually_viewed_all_six=True,rows=rows,Chest_pending_new192=True,fit_accepted=False,imported=False,formal_complete_units=0),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(pin(out),ensure_ascii=False))
