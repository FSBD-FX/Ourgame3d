from pathlib import Path
import hashlib,json,shutil
R=Path('F:/Ourgame');B=R/'source-assets/production/fairytale-sword-primary2-v001'
f=B/'primary2-extraction-v004/extracted-freeze-v004.json'
def desc(p):
    b=p.read_bytes();return {'path':p.as_posix(),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
m=json.loads(f.read_text(encoding='utf-8'))
assert m['shape_pipeline_passed'] and not m['timing_contract_passed']
A=R/'过程图稿与视频/2026-10-16_军剑闭合握姿原生171标准派生_v004';assert not A.exists()
(A/'原件').mkdir(parents=True);(A/'展示副本').mkdir()
entries=[]
for i,row in enumerate(m['files']+[desc(f)]):
    p=Path(row['path']);assert desc(p)==row
    q=A/'原件'/f'{i:03d}-{p.name}';shutil.copy2(p,q);assert p.read_bytes()==q.read_bytes()
    entries.append({'source':row,'copy':desc(q)})
for p in [*(B/'run-primary2-v004/curated').glob('*.png'),B/'run-primary2-v004/qa/sword_primary_2-contact.png',B/'run-primary2-v004/qa/sword_primary_2.gif']:
    q=A/'展示副本'/p.name;shutil.copy2(p,q);assert p.read_bytes()==q.read_bytes()
    entries.append({'source':desc(p),'copy':desc(q)})
(A/'index.json').write_text(json.dumps({'files':entries,'source_version':'native171/extractionv004','status':'shapeQA passed; six derived frames pending explicit review, targeted phase1 grasp correction pending review; no import/motion acceptance',
    'shape_pipeline_passed':True,'timing_contract_passed':False,'standard_preview_ms':[100]*6,'actual_kernel_requested_ms':[75,75,60,60,135,135],
    'per_frame_normalization':False,'retimed':False,'formal_complete_units':0},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(A/'README.md').write_text('内置170原稿经未改动标准sprite-gen/shared-row提取、compose/export/preview。原件和展示副本逐字节保存；先E保留再审。标准预览600ms不符合540ms内核请求，保留该失败；未重时、未改源像素、未导入或验收动作。\n',encoding='utf-8')
print(json.dumps({'archive':A.as_posix(),'source_files':len(m['files'])+1,'copies':len(entries)},ensure_ascii=False))
