from pathlib import Path
import hashlib,json,shutil
R=Path('F:/Ourgame');B=R/'source-assets/production/fairytale-sword-equipment-binding-v001';S=R/'UnrealGame/Source/CodexDungeon'
def desc(p):
    b=p.read_bytes();return {'path':p.as_posix(),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
f=B/'stage0-freeze-v001.json';assert desc(f)['sha256']=='11176294207c76c2a42c561ed7d12488211e8c1dc0ebec01f452adacffcad45f'
for pin in json.loads(f.read_text(encoding='utf-8'))['files']:
    actual=desc(B/pin['path']);assert actual['bytes']==pin['bytes'] and actual['sha256']==pin['sha256']
names=['DungeonFairytaleSwordEquipmentBinding.h','DungeonFairytaleSwordEquipmentBinding.cpp','Tests/DungeonFairytaleSwordEquipmentBindingTests.cpp']
for name in names:assert not (S/name).exists()
rows=[]
for name in names:
    p=B/'candidate-source'/name;q=S/name;shutil.copy2(p,q);assert p.read_bytes()==q.read_bytes();rows.append({'candidate':desc(p),'actual_source':desc(q)})
out=B/'root-stage0-source-admission-v001.json';assert not out.exists()
out.write_text(json.dumps({'stage0_freeze':desc(f),'files':rows,'scope':'Only three new independent files; honest false resolver+real positive/negative tests. No presentation/kernel/assets/ledger edits. RED not yet run.','formal_complete_units':0},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'admitted':len(rows),'manifest':desc(out)},ensure_ascii=False))
