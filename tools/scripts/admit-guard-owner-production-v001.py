from pathlib import Path
import argparse,hashlib,json,os,shutil,subprocess
R=Path('F:/Ourgame');B=R/'source-assets/production/stone-guard-owner-v002/production-v001';F=B/'production-freeze-v001.json';p=argparse.ArgumentParser();p.add_argument('--mode',choices=['core','adapter'],required=True);p.add_argument('--execute',action='store_true');a=p.parse_args();O=R/f'docs/production/first-batch-v2/evidence/stone-guard-owner-v002/root-production-{a.mode}-admission-v001'
def desc(p):
 b=p.read_bytes();return dict(path=p.as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def check(x):
 p=Path(x['path']);d=desc(p);assert(d['bytes'],d['sha256'])==(x['bytes'],x['sha256'])
v=json.loads(F.read_text(encoding='utf-8-sig'));assert desc(F)['sha256']=='1721cc4d85432a033af0fb519a38b7e7cccb29a37b21889968ccb9cb416f58d9'
for x in v['files']+v['evidence']:check(x)
inputs={Path(x['path']).name:x for x in v['exact_existing_source_inputs']}
candidates=[]
for x in v['candidate_files']:
 c=Path(x['path']);relative=c.relative_to(B/'candidate-source');is_adapter=c.name=='DungeonRunSaveAdapter.cpp'
 if is_adapter!=(a.mode=='adapter'):continue
 dest=R/'UnrealGame/Source/CodexDungeon'/relative
 if c.name in inputs:check(inputs[c.name])
 else:assert not dest.exists()
 candidates.append((c,dest))
assert len(candidates)==(8 if a.mode=='core' else 1)
if not a.execute:print(json.dumps(dict(plan=True,mode=a.mode,source_files=len(candidates))));raise SystemExit(0)
assert not O.exists();(O/'before').mkdir(parents=True);before={q:desc(q) for q in (R/'UnrealGame/Source').rglob('*') if q.is_file()}
for c,dest in candidates:
 if dest.exists():q=O/'before'/dest.name;shutil.copy2(dest,q);assert q.read_bytes()==dest.read_bytes()
 dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(c,dest);assert c.read_bytes()==dest.read_bytes();os.utime(dest,None)
assert {q for q,x in before.items() if desc(q)!=x}=={d for c,d in candidates if d in before}
assert {q for q in (R/'UnrealGame/Source').rglob('*') if q.is_file() and q not in before}=={d for c,d in candidates if d not in before}
(O/'admission.json').write_text(json.dumps(dict(mode=a.mode,freeze=desc(F),before=[x for q,x in before.items() if q in {d for c,d in candidates}],after=[desc(d) for c,d in candidates],other_source_unchanged=True,source_mtime_refreshed=True,compiled=False,new_registered_tests_expected=161),ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(dict(admitted=a.mode,count=len(candidates),compile_required=True)))
