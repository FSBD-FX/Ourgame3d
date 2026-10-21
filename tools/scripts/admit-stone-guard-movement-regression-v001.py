from pathlib import Path
import hashlib, json, os, shutil

R=Path('F:/Ourgame')
B=R/'source-assets/production/stone-guard-kernel-v001/movement-split-v002'
O=R/'docs/production/first-batch-v2/evidence/stone-guard-kernel-v001/root-movement-regression-admission-v001'
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def desc(p):
    b=p.read_bytes(); return dict(path=p.as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
f=B/'regression-admission-freeze-v001.json'
assert desc(f)['sha256']=='b79b33fe7418d4073e3044d0c2629d6395acc8725b173a7a1ac0942fa9f4f2ac'
v=read(f); assert v['new_UE_registration_count']==1
cpp=R/'UnrealGame/Source/CodexDungeon/DungeonStoneGuard.cpp'
assert desc(cpp)['sha256']=='4de8ffab4f8b8a6ac4400c268199b84adf630bdaf1943803c548ff05851dd061'
before=[desc(p) for p in sorted((R/'UnrealGame/Source').rglob('*')) if p.is_file()]
assert not O.exists();O.mkdir(parents=True)
shutil.copy2(f,O/f.name)
shutil.copy2(R/'docs/production/first-batch-v2/progress.json',O/'before-progress.json')
added=[]
for row in v['admit_only']:
    p=Path(row['path']);assert desc(p)=={k:row[k] for k in ['path','bytes','sha256']}
    q=R/row['destination'];assert not q.exists();shutil.copy2(p,q)
    if q.name=='StoneGuardMovementCases.h':
        b=q.read_bytes();assert b.count(b'#include "DungeonStoneGuard.h"')==1
        q.write_bytes(b.replace(b'#include "DungeonStoneGuard.h"',b'#include "../DungeonStoneGuard.h"'))
    os.utime(q,None);added.append(desc(q))
for row in before: assert desc(Path(row['path']))==row
os.utime(cpp,None)
(O/'admission.json').write_text(json.dumps(dict(source_freeze=desc(f),existing_source_checked=len(before),existing_source_bytes_unchanged=True,added_files=added,include_correction='UE Tests subdirectory requires ../DungeonStoneGuard.h; semantics unchanged',production_cpp=desc(cpp),source_mtime_touched=True,actual_compile=None,actual_RED=None,expected_old_tests=3,expected_new_movement_RED=1,prospective_full_count=148,formal_complete_units=0),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(added_files=len(added),old_source_bytes_unchanged=True,expected_kernel_tests=4,next='compile original production and test new regression'),ensure_ascii=False))
