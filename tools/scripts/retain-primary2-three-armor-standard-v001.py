from pathlib import Path
from PIL import Image
import hashlib,json,shutil
R=Path('F:/Ourgame');B=R/'source-assets/production/fairytale-armor-sword-primary2-v001'
A=R/'过程图稿与视频/2026-10-16_军剑上挑三甲标准提取_v001';assert not A.exists()
def d(p):
 b=p.read_bytes();return dict(path=p.as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def new(p,v):
 assert not p.exists();p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
files={};rows=[]
for component in ['Chest','NearShoulder','FarShoulder']:
 E=B/(component.lower()+'-extraction-v001');F=E/'extracted-freeze-v001.json';f=json.loads(F.read_text())
 assert f['shape_pipeline_passed'] and f['failure'] is None
 for entry in f['files']:
  p=Path(entry['path']);assert d(p)==entry;files[p.as_posix()]=p
 files[F.as_posix()]=F
 receipt=json.loads((E/'extraction-receipt-v001.json').read_text())
 rows.append(dict(component=component,freeze=d(F),frames=receipt['frames'],metadata=receipt['metadata']))
for p in [B/'root-native172-174-raw-review-v001.json',R/'docs/production/first-batch-v2/evidence/sword-primary2-body-v001/root-partition-trial-review-v001.json',Path(__file__).resolve()]:files[p.as_posix()]=p
(A/'原件').mkdir(parents=True);(A/'展示副本').mkdir();retained=[];crops=[]
for i,p in enumerate(files.values()):
 q=A/'原件'/f'{i:03d}-{p.parent.name}-{p.name}';assert not q.exists();shutil.copy2(p,q);assert d(p)['sha256']==d(q)['sha256']
 retained.append(dict(source=d(p),copy=d(q)))
for row in rows:
 for frame in row['frames']:
  p=Path(frame['source']['path']);im=Image.open(p).convert('RGBA');assert im.size==(512,512)
  x,y,r,b=im.getchannel('A').getbbox();roi=[max(0,x-8),max(0,y-8),min(512,r+8),min(512,b+8)]
  q=A/'展示副本'/f"{row['component']}-phase-{frame['frame']}-inspection.png"
  crop=im.crop(roi);crop.save(q);assert crop.tobytes()==im.crop(roi).tobytes()
  crops.append(dict(component=row['component'],phase=frame['frame'],source=d(p),crop=d(q),source_crop_rect=roi,resampled=False,art_asset=False,source_coordinate_rule='source x/y = crop local x/y plus roi left/top',feature_A=None))
new(A/'crop-source-map-v001.json',dict(crops=crops,measured_feature_A=False))
new(A/'source-version-status-index.json',dict(files=retained,rows=rows,crops=crops,status='standard shape pipeline passed, nonuniform540ms timing not met by600ms previews; physical features/registration/runtime pending',formal_complete_units=0))
(A/'README.md').write_text('三组真正新甲片标准提取；原件逐字节保存，18张检视图仅原RGBA无重采样裁图，坐标加ROI原点。形状通过不代表实际结构特征/穿甲适配/动作或完成；标准600ms与内核540ms不同。\n',encoding='utf-8')
print(json.dumps(dict(archive=A.as_posix(),original_files=len(retained),inspection_crops=len(crops),row_facts=[dict(component=x['component'],ratio=x['metadata']['shared_row_ratio'],timing=x['metadata']['timing_contract_passed']) for x in rows]),ensure_ascii=False))
