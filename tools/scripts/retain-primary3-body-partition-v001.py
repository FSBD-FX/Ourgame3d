from pathlib import Path
import hashlib,json,shutil
R=Path('F:/Ourgame');B=R/'source-assets/production/fairytale-sword-primary3-body-partition-v001'
def desc(p):
    d=p.read_bytes();return {'path':p.as_posix(),'bytes':len(d),'sha256':hashlib.sha256(d).hexdigest()}
f=B/'partition-freeze-v001.json';m=json.loads(f.read_text(encoding='utf-8'));assert desc(f)['sha256']=='b7393d7d1a8640e356be7f7e944ccae9e8f3dbe6ba06a06f16b20fd8858eba3e'
for pin in m['files']:assert desc(Path(pin['path']))==pin
A=R/'过程图稿与视频/2026-10-16_军剑终结斩四归属身体_v001';assert not A.exists();(A/'原件').mkdir(parents=True);(A/'展示副本').mkdir();rows=[]
for i,pin in enumerate(m['files']+[desc(f),desc(Path(__file__).resolve())]):
    p=Path(pin['path']);q=A/'原件'/f'{i:03d}-{p.name}';shutil.copy2(p,q);assert p.read_bytes()==q.read_bytes();rows.append({'source':pin,'copy':desc(q)})
for n in ['BodyRest','NearArmWithoutHand','HelmetForeground','NearHand']:
    for i in range(6):
        p=B/f'layers/{n}/frame-{i}.png';q=A/'展示副本'/f'{n}-frame-{i}.png';shutil.copy2(p,q);assert p.read_bytes()==q.read_bytes()
(A/'source-version-status-index.json').write_text(json.dumps({'files':rows,'status':'Original175 four-owner numeric reconstruction exact. New24 layers pending explicit Root review; semantic ownership, grip and armor fit not accepted.','formal_complete_units':0},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(A/'README.md').write_text('第三刀原RGBA四归属候选；全部原件与24张未修改展示层保留。数学重组通过不等于边界/动作/武器配准或装备验收。\n',encoding='utf-8')
print(json.dumps({'archive':A.as_posix(),'originals':len(rows),'presentation_layers':24},ensure_ascii=False))
