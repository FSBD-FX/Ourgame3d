"""Five schema/pin boundary cases; no UE, image mutation or asset import."""
from pathlib import Path
import importlib.util,json,copy,hashlib,tempfile
P=Path(__file__).resolve().parents[1]
s=importlib.util.spec_from_file_location('builder',P/'build-K8-production-contract-v001.py');b=importlib.util.module_from_spec(s);s.loader.exec_module(b)
C=P.parent
markers=C/'Root-K8-binding-decisions-v001/Root-8-markers-v001.json'
choice=C/'Root-K8-binding-decisions-v001/Root-K5-near-shoulder-choice-v001.json'
shoulder=C/'K5-near-shoulder-integer-fit-v003/near-shoulder-candidates/A/K5.png'
def p(x):
 raw=x.read_bytes();return dict(path=x.as_posix(),bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest())
inputs=dict(markers=p(markers),choice=p(choice),chosen=p(shoulder))
out=P/'tests/never-written-validation-package-v001';checks=[]
def run(name,fn):
 try:fn();checks.append(dict(name=name,passed=True))
 except Exception as e:checks.append(dict(name=name,passed=False,error=repr(e)))
def positive():
 pack=b.prepare(inputs,out);c=pack['source-contract-v001.json'];m=pack['texture-import-manifest-v001.json'];need=lambda v:(_ for _ in ()).throw(AssertionError()) if not v else None
 need(len(c['layers'])==len(m['textures'])==56);need(len({v['object_path'] for v in m['textures']})==56);need('RuntimeReady=false' in pack['profile-whole-value-v001.inl']);need(not out.exists())
 for owner in b.OWNERS:
  z=next(v for v in c['layers'] if v['frame']==0 and v['owner']==owner);s=next(v for v in c['layers'] if v['frame']==6 and v['owner']==owner);need(z['source']==s['source'] and z['object_path']!=s['object_path'] and s['source_alias_frame']==0)
def negative(change):
 x=copy.deepcopy(inputs);change(x)
 try:b.prepare(x,out)
 except (ValueError,OSError,KeyError):assert not out.exists();return
 raise AssertionError('invalid input accepted')
run('real Root inputs produce 56 distinct phase packages, K6 aliases source0 only, runtime false, no output',positive)
run('wrong chosen SHA rejected before output',lambda:negative(lambda x:x['chosen'].update(sha256='0'*64)))
run('missing chosen pin rejected before output',lambda:negative(lambda x:x.pop('chosen')))
run('wrong marker SHA rejected before output',lambda:negative(lambda x:x['markers'].update(sha256='0'*64)))
# A new JSON fixture only; immutable Root inputs and all PNGs stay untouched.
original=json.loads(markers.read_text());original['frames']=original['frames'][:-1]
f=P/'tests/missing-K7-markers-fixture.json'
data=json.dumps(original)
if f.exists():assert f.read_text(encoding='utf-8')==data
else:
 with f.open('x',encoding='utf-8') as z:z.write(data)
run('missing K7 marker rejected before output',lambda:negative(lambda x:x.update(markers=p(f))))
print(json.dumps(dict(schema='K8-builder-required-boundaries-v001',passed=sum(t['passed'] for t in checks),failed=sum(not t['passed'] for t in checks),cases=checks,UE_run=False,imported=False),indent=2));raise SystemExit(any(not t['passed'] for t in checks))
