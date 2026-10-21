"""Root-only fresh pre-view retention of native175 standard Primary3 derivatives."""
from pathlib import Path
import hashlib,json,shutil
R=Path('F:/Ourgame');B=R/'source-assets/production/fairytale-sword-primary3-v001'
f=B/'primary3-extraction-v001/extracted-freeze-v001.json'
def desc(p):
    b=p.read_bytes();return {'path':p.as_posix(),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def write(p,d):
    with p.open('x',encoding='utf-8',newline='\n') as stream:stream.write(d if isinstance(d,str) else json.dumps(d,ensure_ascii=False,indent=2)+'\n')
m=json.loads(f.read_text(encoding='utf-8-sig'))
assert m['shape_pipeline_passed'] and not m['timing_contract_passed']
receipt=B/'primary3-extraction-v001/extraction-receipt-v001.json';e=json.loads(receipt.read_text(encoding='utf-8-sig'))
assert e['native_request']==175 and e['component']=='SwordPrimary3Body' and e['durations_ms']==[110,110,60,60,160,160]
assert e['shape_pipeline_passed'] and e['request_exact_unchanged'] and not e['request_auto_changed'] and e['frozen_preparation_mismatches']==[]
assert e['metadata']['actual_atlas_durations_ms']==e['metadata']['actual_gif_durations_ms']==[100]*6
assert len(e['frames'])==6 and len({x['file']['sha256'] for x in e['frames']})==6
A=R/'过程图稿与视频/2026-10-16_军剑终结斩原生175标准派生_v001'
assert not A.exists()
# Verify the full frozen set before creating the archive. No source or ledger changes.
for row in m['files']:assert desc(Path(row['path']))==row
(A/'原件').mkdir(parents=True);(A/'展示副本').mkdir()
entries=[]
for i,row in enumerate(m['files']+[desc(f),desc(Path(__file__).resolve())]):
    p=Path(row['path']);assert desc(p)==row
    q=A/'原件'/f'{i:03d}-{p.name}';shutil.copy2(p,q);assert p.read_bytes()==q.read_bytes()
    entries.append({'source':row,'copy':desc(q)})
for p in [*(B/'run-primary3-v001/curated').glob('*.png'),B/'run-primary3-v001/qa/sword_primary_3-contact.png',B/'run-primary3-v001/qa/sword_primary_3.gif']:
    q=A/'展示副本'/p.name;assert not q.exists();shutil.copy2(p,q);assert p.read_bytes()==q.read_bytes()
    entries.append({'source':desc(p),'copy':desc(q)})
write(A/'index.json',{'files':entries,'source_version':'native175/Primary3/extractionv001','status':'Standard shapeQA passed; new six finishing-down-cut frames pending explicit E-retained review; no grasp, anatomy, fit, timing or motion acceptance.',
    'shape_pipeline_passed':True,'timing_contract_passed':False,'standard_preview_ms':[100]*6,'standard_preview_total_ms':600,'actual_kernel_requested_ms':[110,110,60,60,160,160],'kernel_total_ms':660,
    'per_frame_normalization':False,'retimed':False,'derived_images_explicitly_viewed_by_tool':False,'formal_complete_units':0})
write(A/'README.md','内置175终结下斩原稿经未改动sprite-gen/shared-row提取、compose/export/preview。原件和展示副本逐字节保存；先E保全后再审。标准预览600ms不符合660ms内核请求，原失败单列保留；未重时、未改源像素、未导入，也未接受掌心/握柄/下弧/动作/完整装备。\n')
print(json.dumps({'archive':A.as_posix(),'source_files':len(m['files'])+2,'copies':len(entries),'shapeQA':True,'standard600_vs_kernel660_timing_passed':False},ensure_ascii=False))
