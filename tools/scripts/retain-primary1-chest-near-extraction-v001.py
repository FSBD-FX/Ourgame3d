"""Freeze both standard component runs and exact unscaled inspection crops."""
from pathlib import Path
import hashlib,json
from PIL import Image
R=Path('F:/Ourgame');B=R/'source-assets/production/fairytale-armor-sword-primary1-v001'
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def desc(p):
 b=p.read_bytes();return {'path':p.as_posix(),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def new(p,v):
 assert not p.exists(),p
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
rows=[];maps=[];C=B/'review-crops-v001';assert not C.exists();C.mkdir()
for component,sub,sha,run in [('Chest','chest-extraction-v001','8d36c172051705416398bb1937eb5b5d217c015b3540298a9d90b06fcceadb8f','run-chest-primary1-v001'),('NearShoulder','nearshoulder-extraction-v001','d315f1c283ae04e5a7e88c7e827f6df666b22e5303f33b9cc740a8f9b463f83a','run-nearshoulder-primary1-v001')]:
 freeze=B/sub/'extracted-freeze-v001.json';assert desc(freeze)['sha256']==sha
 f=load(freeze)
 for x in f['files']:assert desc(Path(x['path']))==x;rows.append(x)
 rows.append(desc(freeze))
 for i in range(6):
  source=B/run/f'curated/frame-{i}.png';im=Image.open(source).convert('RGBA');assert im.size==(512,512)
  a,b,c,d=im.getbbox();rect=[max(0,a-10),max(0,b-10),min(512,c+10),min(512,d+10)]
  out=C/f'{component}-phase-{i}.png';im.crop(tuple(rect)).save(out)
  maps.append({'component':component,'phase':i,'source':desc(source),'crop':desc(out),'source_crop_rect':rect,'resampled':False,'coordinates_for_source_measurement':'add crop origin x/y to local crop feature; bbox is diagnostic only, never a mount'})
new(C/'crop-source-map-v001.json',{'crops':maps,'shape_or_motion_accepted':False})
rows.extend(desc(p) for p in sorted(C.iterdir()))
rows.extend(desc(p) for p in [Path(__file__),B/'root-body-partition-review-v001.json',B/'root-native164-167-review-v001.json',B/'far-fit32x30-design-v003.json'])
unique={x['path']:x for x in rows}
freeze=B/'root-chest-near-derived-retention-freeze-v001.json';new(freeze,{'files':list(unique.values()),'status':'Frozen standard extracts and exact unscaled12inspection crops before explicit derived views. No runtime/fit/motion approval.','formal_complete_units':0})
print(json.dumps({'freeze':desc(freeze),'files':len(unique),'crops':len(maps),'bytes':sum(x['bytes'] for x in unique.values())}))
