from pathlib import Path
import hashlib,json
from PIL import Image
R=Path('F:/Ourgame');F=R/'source-assets/production/fairytale-lgt-readability-v003';I=F/'far187-extraction-v001/ready-three-component-source-list-v001.json'
O=F/'ready-visible-mounts-v001';assert not O.exists();O.mkdir()
def desc(p):
 b=p.read_bytes();return dict(path=p.as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
index=json.loads(I.read_text(encoding='utf-8'));rows=[]
points={'Chest':[(266,243),(268,240),(266,243),(268,241)],'NearShoulder':[(264,265),(264,265),(264,265),(264,265)],'FarShoulder':[(250,246),(250,246),(250,246),(250,246)]}
targets={'Chest':[(259,271),(259,267),(259,271),(259,267)],'NearShoulder':[(207,265),(207,261),(207,265),(207,261)],'FarShoulder':[(294,253),(294,249),(294,253),(294,249)]}
features={'Chest':'visually inspected round golden front fastening; source A picked from this actual visible clasp, not alpha bbox centre','NearShoulder':'visually inspected small lower-right diamond stitch mark; actual source detail, not a guessed shoulder joint or bbox centre','FarShoulder':'visually inspected upper leather tip below its ink edge; actual narrow-tab attachment end, not bbox centre'}
for frame in index['frames']:
 i=frame['frame']
 for c in frame['armor_candidates_for_root_measurement']:
  n=c['component'];pin=c['diagnostic_png'];p=Path(pin['path']);assert desc(p)==pin
  a=points[n][i];b=targets[n][i];im=Image.open(p).convert('RGBA');rgba=list(im.getpixel(a));assert rgba[3]>=128,(n,i,a,rgba)
  rows.append(dict(frame=i,component=n,source=pin,A_source_px=list(a),A_observed_rgba=rgba,A_feature=features[n],A_manual_visual_uncertainty_px=2,B_body_design_source_px=list(b),B_role='artist placement proposal on unchanged Body158 cloth surface; not measured skeleton/bone truth; final fit pending',B_design_uncertainty_px=3,integer_delta_xy=[b[0]-a[0],b[1]-a[1]],body=frame['common_body158'],duration_ms=167))
v=dict(schema='ready-visible-feature-mounts-v001',source_index=desc(I),source_feature_review='F:/Ourgame/过程图稿与视频/2026-10-17_软皮组件可见挂点测量_v001',E_feature_retention='E:/OurGame/Knight/过程图稿与视频/2026-10-17-OurgameUE-leather-feature-review-v277/source-size-SHA256.json',root_actually_viewed_all_four_source_feature_sheets=True,method='manual actual visible-feature picks; integer translations only; no per-frame rescale/no guessed bone points',rows=rows,fit_accepted=False,semantic_protection_mask_accepted=False,imported=False,formal_complete_units=0)
(O/'mounts-v001.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(path=(O/'mounts-v001.json').as_posix(),mounts=len(rows),all_A_on_actual_opaque_source=True,B_design_only=True)))
