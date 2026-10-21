from pathlib import Path
import json,hashlib,shutil,os
R=Path('F:/Ourgame');B=R/'source-assets/production/leather-primary1-proof-tooling-v001/primary1-native-source-v003';F=B/'source-freeze-v003.json';O=R/'docs/production/first-batch-v2/evidence/leather-primary1-v001/root-source-admission-v003';assert not O.exists()
def pin(p):
 b=p.read_bytes();return dict(path=p.as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
assert pin(F)['sha256']=='d7abd41da2930c331a6fab82fc3341923385569ccf964922742b0c1fb5325406';v=json.loads(F.read_text(encoding='utf-8-sig'))
for r in v['files']:
 d=pin(Path(r['path']));assert (d['bytes'],d['sha256'])==(r['bytes'],r['sha256'])
p=Path(v['input']['path']);assert pin(p)==v['input'];c=B/'DungeonFairytaleEquipmentBoundProbe.cpp'
before={q:pin(q) for q in (R/'UnrealGame/Source').rglob('*') if q.is_file()};O.mkdir(parents=True);shutil.copy2(p,O/'before-Probe.cpp');assert p.read_bytes()==(O/'before-Probe.cpp').read_bytes();shutil.copy2(c,p);os.utime(p,None);assert p.read_bytes()==c.read_bytes();assert {q for q,d in before.items() if pin(q)!=d}=={p}
(O/'admission.json').write_text(json.dumps(dict(source_freeze=pin(F),admitted=pin(p),all_other_Source_unchanged=True,actual_second_attack_once_reset=True,compiled=False),ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(dict(admitted=pin(p),incremental_build_pending=True),ensure_ascii=False))
