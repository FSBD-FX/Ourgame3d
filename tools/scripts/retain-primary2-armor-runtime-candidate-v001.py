from pathlib import Path
import hashlib,json,shutil
R=Path('F:/Ourgame');B=R/'source-assets/production/fairytale-armor-sword-primary2-runtime-v001'
A=R/'过程图稿与视频/2026-10-16_军剑上挑穿甲注册候选_v001';assert not A.exists()
def d(p):
 b=p.read_bytes();return dict(path=p.as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
freeze=B/'delivery-freeze-v001.json';f=json.loads(freeze.read_text());files=[]
for row in f['files']:
 p=Path(row['path']);assert d(p)==row;files.append(p)
files.append(freeze);files.append(Path(__file__).resolve())
(A/'原件').mkdir(parents=True);(A/'展示副本').mkdir();index=[]
for i,p in enumerate(files):
 q=A/'原件'/f'{i:03d}-{p.parent.name}-{p.name}';assert not q.exists();shutil.copy2(p,q);assert d(p)['sha256']==d(q)['sha256']
 index.append(dict(source=d(p),copy=d(q)))
for i in range(6):
 p=B/f'assemblies/frame-{i}-armor-no-sword.png';q=A/'展示副本'/p.name;shutil.copy2(p,q);assert d(p)['sha256']==d(q)['sha256']
(A/'source-version-status-index.json').write_text(json.dumps(dict(files=index,status='42 source textures and six static noSword assemblies; original bodyRGBA exact, 18 integer reversible translations; semantic visual/nativefit pending',formal_complete_units=0),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(A/'README.md').write_text('171原四归属身体加172/173/174轻甲六相；42纹理/18整数可逆平移无裁切、原身体RGBA重建一致。展示6张静态无剑组合，仅待检候选，不是游戏实景或握柄/运动/整件装备验收。\n',encoding='utf-8')
print(json.dumps(dict(archive=A.as_posix(),original_files=len(index),presentation=6),ensure_ascii=False))
