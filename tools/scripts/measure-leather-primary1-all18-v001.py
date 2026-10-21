from pathlib import Path
import json,hashlib
from PIL import Image
R=Path('F:/Ourgame');D=R/'source-assets/production/fairytale-lgt-readability-v003';B=D/'primary1-visible-mounts-v001'
def pin(p):
 b=p.read_bytes();return dict(path=p.as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
idx=D/'primary1-chest192-extraction-v001/combined-18-source-index-Chest192-Near189-Far190-v001.json';assert pin(idx)['sha256']=='bf43d70c2bf066d12669a0c86096459cd159a56a8db8edae4b3f816ab1c477d8'
s=B/'shoulder-mounts-v001.json';v=json.loads(s.read_text(encoding='utf-8-sig'));rows=v['rows'];assert len(rows)==12
c=next(x for x in json.loads(idx.read_text(encoding='utf-8-sig'))['components'] if x['component']=='Chest')
As=[(262,244),(274,244),(274,247),(274,247),(269,239),(262,244)]
Bs=[(268,273),(269,264),(270,278),(272,296),(267,275),(268,273)]
for i,f in enumerate(c['frames']):
 p=Path(f['source']['path']);assert pin(p)==f['source'];aa=As[i];bb=Bs[i];rgba=Image.open(p).getpixel(aa);assert rgba[3]>0
 body=R/f'source-assets/production/fairytale-sword-v001/run-primary1-v001/curated/frame-{i}.png'
 rows.append(dict(frame=i,component='Chest',source=pin(p),A_source_px=aa,A_observed_rgba=rgba,A_feature='actual round gold front clasp, manually picked from the new192 component visible feature',A_manual_visual_uncertainty_px=3,B_body_design_source_px=bb,B_role='Root artist proposal for soft jerkin belt/hem alignment on actually viewed Body159; not copied gray breastplate boss placement and not measured skeleton',B_design_uncertainty_px=8 if i in [1,2,3,4] else 3,integer_delta_xy=[bb[0]-aa[0],bb[1]-aa[1]],body=pin(body),duration_ms=[85,85,60,60,155,155][i]))
for r in rows:assert pin(Path(r['source']['path']))==r['source'] and pin(Path(r['body']['path']))==r['body']
out=B/'all18-mounts-v001.json';assert not out.exists();out.write_text(json.dumps(dict(schema='primary1-actual18-visible-feature-mounts-v001',source_index=pin(idx),shoulder_source_mounts=pin(s),source_feature_review='F:/Ourgame/过程图稿与视频/2026-10-17_软皮第一刀192胸衣挂点审阅_v002',E_feature_retention='E:/OurGame/Knight/过程图稿与视频/2026-10-17-OurgameUE-leather-primary1-chest192-features-v295/source-size-SHA256.json',root_actually_viewed_all_six_new_Chest_and_Body159=True,root_actually_viewed_old_six_shoulders_at_E289=True,method='actual visible component feature A; artist B placement; integer translation only; no inferred hidden bone/feature',rows=sorted(rows,key=lambda r:(r['frame'],r['component'])),fit_accepted=False,semantic_protection_mask_accepted=False,imported=False,formal_complete_units=0),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
freeze=B/'mounts-freeze-v001.json';assert not freeze.exists();freeze.write_text(json.dumps(dict(files=[pin(s),pin(out)],actual_mounts=18,fit_accepted=False),ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(dict(mounts=pin(out),freeze=pin(freeze)),ensure_ascii=False))
