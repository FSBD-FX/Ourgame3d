from pathlib import Path
import hashlib,json,shutil
R=Path('F:/Ourgame');B=R/'source-assets/production/fairytale-sword-primary3-runtime-v001'
def desc(p):
    d=p.read_bytes();return {'path':p.as_posix(),'bytes':len(d),'sha256':hashlib.sha256(d).hexdigest()}
f=B/'delivery-freeze-v001.json';m=json.loads(f.read_text(encoding='utf-8'));assert desc(f)['sha256']=='7ae1ac0736b1b4a43935738b213a3e7d120ce190ef15ece4fc5d771b5ef59e26'
for pin in m['files']:assert desc(Path(pin['path']))==pin
A=R/'过程图稿与视频/2026-10-16_军剑终结斩穿甲注册候选_v001';assert not A.exists();(A/'原件').mkdir(parents=True);(A/'展示副本').mkdir();rows=[]
for i,pin in enumerate(m['files']+[desc(f),desc(Path(__file__).resolve())]):
    p=Path(pin['path']);q=A/'原件'/f'{i:03d}-{p.name}';shutil.copy2(p,q);assert p.read_bytes()==q.read_bytes();rows.append({'source':pin,'copy':desc(q)})
for i in range(6):
    p=B/f'assemblies/frame-{i}-armor-no-sword.png';q=A/'展示副本'/p.name;shutil.copy2(p,q);assert p.read_bytes()==q.read_bytes()
(A/'source-version-status-index.json').write_text(json.dumps({'files':rows,'status':'48Texture candidate, including6 whole bodies and42 sourcebody/armor layers. Six no-sword assemblies pending Root review; no import/grip/actualaxis/fullmotion/equipment acceptance.','formal_complete_units':0},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(A/'README.md').write_text('第三刀穿甲注册候选。只按新175可见布面设计或独立隐藏TRIAL作整数平移；原RGBA逆向重组不失。尚未审组合、导入或接受武器/动作。\n',encoding='utf-8')
print(json.dumps({'archive':A.as_posix(),'originals':len(rows),'assemblies':6},ensure_ascii=False))
