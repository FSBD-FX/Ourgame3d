from pathlib import Path
import hashlib,json,shutil
R=Path('F:/Ourgame');B=R/'source-assets/production/fairytale-sword-primary3-v001/armor-input-v001';O=B/'standard-extraction-v001'
def desc(p):
    b=p.read_bytes();return {'path':p.as_posix(),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
f=O/'extracted-freeze-v001.json';m=json.loads(f.read_text(encoding='utf-8'));s=json.loads((O/'extraction-summary-v001.json').read_text(encoding='utf-8'))
assert m['failure'] is None and s['shape_pipeline_passed'] and len(s['rows'])==3
for pin in m['files']:assert desc(Path(pin['path']))==pin
A=R/'过程图稿与视频/2026-10-16_军剑终结斩三甲标准派生_v001';assert not A.exists();(A/'原件').mkdir(parents=True);(A/'展示副本').mkdir()
rows=[];cropmap=[]
for i,pin in enumerate(m['files']+[desc(f),desc(Path(__file__).resolve())]):
    p=Path(pin['path']);q=A/'原件'/f'{i:03d}-{p.name}';shutil.copy2(p,q);assert desc(p)['sha256']==desc(q)['sha256'];rows.append({'source':pin,'copy':desc(q)})
for row in s['rows']:
    assert row['request_unchanged'] and row['shape_pipeline_passed'] and not row['timing_contract_passed']
    for frame in row['frames']:
        p=Path(frame['inspection_crop']['path']);q=A/'展示副本'/p.name;shutil.copy2(p,q);assert q.read_bytes()==p.read_bytes()
        cropmap.append({'component':row['component'],'frame':frame['frame'],'source':frame['file'],'source_roi_original512':frame['inspection_roi_original512'],'crop':desc(q),'resampled':False,'physical_feature_A':None})
(A/'crop-source-map-v001.json').write_text(json.dumps(cropmap,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(A/'source-version-status-index.json').write_text(json.dumps({'files':rows,'native_requests':[176,177,178],'status':'Twelve standard tool executions shapeQA passed; 18 unique original512 components. All physical A still null until explicit review. Standard600 differs kernel660; no retime, registration, UE import or complete unit.','formal_complete_units':0},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(A/'README.md').write_text('第三刀三甲标准派生；原件和18张原RGBA无缩放裁图保留。标准600ms不代表660ms内核；未知实际甲锚点、身体配准、动作仍待实测及运行。\n',encoding='utf-8')
print(json.dumps({'archive':A.as_posix(),'originals':len(rows),'inspection_crops':len(cropmap)},ensure_ascii=False))
