from pathlib import Path
import ast,hashlib,json,shutil
R=Path('F:/Ourgame');D=R/'docs/production/first-batch-v2/evidence/sword-primary3-fit-tooling-v001'
def desc(p):
    d=p.read_bytes();return {'path':p.as_posix(),'bytes':len(d),'sha256':hashlib.sha256(d).hexdigest()}
f=D/'tooling-freeze-v001.json';assert desc(f)['sha256']=='74328d480f46ad09f69cd033620d686b6a1625b9fd6d624c8c26766b81aea585'
document=json.loads(f.read_text(encoding='utf-8'))
for pin in document['files']:
    p=Path(pin['path']);p=p if p.is_absolute() else D/p;a=desc(p);assert a['bytes']==pin['bytes'] and a['sha256']==pin['sha256']
names=['verify-sword-primary3-fit-v001.py','verify-sword-primary3-fit-v001.ps1','postprocess-sword-primary3-fit-v001.py','freeze-sword-primary3-fit-build-v001.py','verify-ready-primary3-body-pixel-presence-v001.py','retain-sword-primary3-fit-v001.py']
for n in names:
    assert not (R/'tools/scripts'/n).exists()
    if n.endswith('.py'):ast.parse((D/n).read_text(encoding='utf-8'))
rows=[]
for n in names:
    p=D/n;q=R/'tools/scripts'/n;shutil.copy2(p,q);assert q.read_bytes()==p.read_bytes();rows.append({'candidate':desc(p),'admitted':desc(q)})
out=D/'root-tool-admission-v001.json';assert not out.exists();out.write_text(json.dumps({'files':rows,'candidate_freeze':desc(f),'root_review':'Reviewed actual phase andfour exacttransition/pending gates,141/1085/snapshot/currentSource/DLL/texturestack/CRC/async/72/UIoff/.50. Existing fixed warmROI20 retained as presenceonly; not fullhead or blade clearance. Runtime must follow actual capture, all new media retained before view.','formal_complete_units':0},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'admitted':len(rows),'freeze':desc(f)},ensure_ascii=False))
