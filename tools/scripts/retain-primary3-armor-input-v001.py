from pathlib import Path
import hashlib,json,shutil
R=Path('F:/Ourgame');B=R/'source-assets/production/fairytale-sword-primary3-v001/armor-input-v001'
def desc(p):
    b=p.read_bytes();return {'path':p.as_posix(),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
f=B/'preparation-freeze-v001.json';m=json.loads(f.read_text(encoding='utf-8'));h=json.loads((B/'primary3-three-armor-input-draft-v001.json').read_text(encoding='utf-8'))
files=[Path(r['path']) for r in m['files']]+[f,Path('F:/Ourgame/tools/scripts/prepare-primary3-three-armor-v001.py')]
refs={}
for row in h['rows']:
    for r in row['reference_images_in_order']:
        p=Path(r['file']['path']);assert desc(p)==r['file'];refs[p.as_posix()]=p
files+=list(refs.values())
for r in m['files']:assert desc(Path(r['path']))==r
A=R/'过程图稿与视频/2026-10-16_军剑终结斩三甲输入_v001';assert not A.exists()
(A/'原件').mkdir(parents=True);(A/'展示副本').mkdir();rows=[]
for i,p in enumerate(dict.fromkeys(files)):
    q=A/'原件'/f'{i:03d}-{p.name}';shutil.copy2(p,q);assert q.read_bytes()==p.read_bytes();rows.append({'source':desc(p),'copy':desc(q)})
for i,p in enumerate(refs.values()):
    q=A/'展示副本'/f'{i:02d}-{p.parent.parent.name}-{p.name}';shutil.copy2(p,q);assert q.read_bytes()==p.read_bytes()
(A/'source-version-status-index.json').write_text(json.dumps({'files':rows,'reference_source_order':list(refs),'status':'Three isolated armor input drafts. Actual175 motion only; all body cloth targets and future physical A null. No generation or registration.','formal_complete_units':0},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(A/'README.md').write_text('第三刀胸甲和双肩输入草稿。标准prepare已执行；未知甲片A/身体锚点保持null，独立配准、动作/装备验收待做。原件和原样展示副本保留。\n',encoding='utf-8')
print(json.dumps({'archive':A.as_posix(),'reference_order':list(refs),'files':len(rows)},ensure_ascii=False))
