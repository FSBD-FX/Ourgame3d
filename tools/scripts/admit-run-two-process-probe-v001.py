from pathlib import Path
import hashlib,json,shutil
R=Path('F:/Ourgame');B=R/'docs/production/first-batch-v2/evidence/run-pristine-bootstrap-v001/two-process-tooling-v001'
E=R/'docs/production/first-batch-v2/evidence/run-pristine-bootstrap-v001/two-process-admission-v001';assert not E.exists();E.mkdir()
def desc(p):
    b=p.read_bytes();return {'path':p.as_posix(),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
snap=R/'source-assets/production/backups/2026-10-16_PristineBootstrap-nativeGeometry-full138GREEN-v112'
m=json.loads((snap/'compiled-source-manifest.json').read_text(encoding='utf-8-sig'));rows=[x for x in m['files'] if x['path'].startswith('UnrealGame/Source/')]
for row in rows:
    assert all(desc(R/row['path'])[k]==row[k] for k in ['bytes','sha256'])
pins={'DungeonRunContinueProbe.h':'2fe0b62fbb6692457e0e16fd03c6bd68a11691b0386588af05ed389fdfb13197',
      'DungeonRunContinueProbe.cpp':'cee3818f690b592b63397477e8311b00d2df0ee94ddba7835a87abbde1c170cf'}
out=[]
for name,sha in pins.items():
    p=B/'candidate-source'/name;q=R/'UnrealGame/Source/CodexDungeon'/name
    assert desc(p)['sha256']==sha and not q.exists()
    shutil.copy2(p,q);assert p.read_bytes()==q.read_bytes();out.append(desc(q))
p=R/'UnrealGame/Source/CodexDungeon/DungeonHUD.cpp';q=E/'DungeonHUD-before-admission.cpp';shutil.copy2(p,q);assert p.read_bytes()==q.read_bytes()
(E/'admission-v001.json').write_text(json.dumps({'new_sources':out,'HUD_before':desc(q),'source_baseline':'v112 actual full138GREEN',
    'baseline_source_pins_verified':len(rows),'scope':'Proof-only flags; existing HUD default unchanged. Minimal include and optional actor spawn patch applied separately.',
    'actual_UBT':False,'actual_two_process_Continue':False,'formal_complete_units':0},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'new_sources':out,'baseline_source_pins_verified':len(rows),'HUD_before':desc(q)},ensure_ascii=False))
