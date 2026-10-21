from pathlib import Path
import hashlib,json,shutil
R=Path('F:/Ourgame');B=R/'source-assets/production/fairytale-armor-sword-primary2-v001';F=B/'input-freeze-v001.json'
def desc(p):
    b=p.read_bytes();return {'path':p.as_posix(),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
assert desc(F)['sha256']=='2f02f4dafd67f6bf14b22ac18627e9c2dc1e9a93308df477f19331edadc1dbcc'
f=json.loads(F.read_text(encoding='utf-8'));h=json.loads((B/'primary2-macro-native-handoff-draft-v001.json').read_text(encoding='utf-8'))
assert not h['generation_ready'] and len(h['rows'])==3
A=R/'过程图稿与视频/2026-10-16_军剑上挑胸甲双肩输入_v001';assert not A.exists();(A/'原件').mkdir(parents=True);(A/'展示副本').mkdir()
entries=[];paths=[Path(row['path']) for row in f['files']]+[F,Path(__file__)]
for i,p in enumerate(paths):
    if i<len(f['files']):assert desc(p)==f['files'][i]
    q=A/'原件'/f'{i:03d}-{p.name}';shutil.copy2(p,q);assert p.read_bytes()==q.read_bytes();entries.append({'source':desc(p),'copy':desc(q)})
refs=list(dict.fromkeys(Path(ref['file']['path']) for row in h['rows'] for ref in row['reference_images_in_order']))
for i,p in enumerate(refs):
    q=A/'展示副本'/f'{i:02d}-{p.name}';shutil.copy2(p,q);assert p.read_bytes()==q.read_bytes()
(A/'index.json').write_text(json.dumps({'files':entries,'display_refs':[desc(p) for p in refs],
    'status':'Three standard independent lightarmor rows draft; new guides not explicitly viewed yet; no generation',
    'source_version':'native171/Primary2/lightarmor-preparation-v001','new_outputs_viewed':False,'generation_ready':False,'formal_complete_units':0},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(A/'README.md').write_text('胸甲/近肩/远肩三条独立row输入与原技术图，保留原件、展示副本、来源版本索引。先E保留再审；隐藏TRIAL点独立于null测量，未来组件A未知；未生成、未导入或验收。\n',encoding='utf-8')
print(json.dumps({'archive':A.as_posix(),'originals':len(paths),'reference_images':len(refs)},ensure_ascii=False))
