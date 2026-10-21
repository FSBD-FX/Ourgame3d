"""Static test-oracle regression against the real full184 report; never UE launch."""
from pathlib import Path
import ast,copy,hashlib,json,runpy,sys
C=Path(__file__).resolve().parent.parent;R=C.parents[3]
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def pin(p):return dict(path=p.as_posix(),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())
for p in (C/'tooling').glob('*.py'):ast.parse(p.read_text(encoding='utf-8-sig'))
old=C.parent/'presentation-full-known44-observer-candidate-v001'
for row in read(old/'known44-AxeCycle-freeze-v001.json')['files']:
 p=old/row['path'];assert p.stat().st_size==row['bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==row['sha256']
for row in read(C/'source-AxeCycle-freeze-v001.json')['files']:
 p=C/row['path'];assert p.stat().st_size==row['bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==row['sha256']
ns=runpy.run_path(str(C/'tooling/verify-known44-axecycle-v002.py'))
snap=R/'source-assets/production/backups/v132-guard-known44-184G/compiled-source-manifest.json';m=read(snap);report=R/m['full_suite']['path'];s=read(report)
assert s['succeeded']==m['strict_registered_tests']==184 and all(s[k]==0 for k in ['failed','succeededWithWarnings','notRun','inProcess'])
assert len(s['tests'])==len({x['fullTestPath'] for x in s['tests']})==184 and all(t['state']=='Success' and t['errors']==t['warnings']==0 for t in s['tests'])
check=ns['require_native_guard_tests'];cases=[];check(s);cases.append(dict(case='actual full184 including legal fourth legacy-prefix terminal test',result='accepted'))
extra=dict(fullTestPath='CodexDungeon.Content.FairytaleGuardPresentation.AdditionalLegalCoverage',state='Success',errors=0,warnings=0)
p=copy.deepcopy(s);p['tests'].append(extra);check(p);cases.append(dict(case='isolated exact-name gate permits another legal same-prefix extension',result='accepted_static_gate_only'))
target=ns['REQUIRED_NATIVE_GUARD_TESTS'][0]
def bad(name,change):
 p=copy.deepcopy(s);change(p)
 try:check(p)
 except ValueError:cases.append(dict(case=name,result='rejected'))
 else:raise AssertionError('Accepted invalid required target: '+name)
bad('missing required target',lambda p:p.update(tests=[x for x in p['tests'] if x['fullTestPath']!=target]))
bad('duplicate required target',lambda p:p['tests'].append(copy.deepcopy(next(x for x in p['tests'] if x['fullTestPath']==target))))
for key,value in [('state','Fail'),('errors',1),('warnings',1),('errors',False)]:
 bad('required target invalid '+key+'='+str(value),lambda p,key=key,value=value:next(x for x in p['tests'] if x['fullTestPath']==target).update({key:value}))
prefix='CodexDungeon.Content.FairytaleGuardPresentation.';legacy_count=sum(x['fullTestPath'].startswith(prefix) for x in s['tests']);assert legacy_count==4
result=dict(schema='known44-exact-six-test-oracle-static-regression-v002',passed=True,actual_full_suite=pin(report),actual_snapshot=pin(snap),actual_registry=184,original_v001_wrong_prefix_count_required=3,actual_legacy_prefix_count=legacy_count,required_exact_test_names=list(ns['REQUIRED_NATIVE_GUARD_TESTS']),static_cases=cases,original_candidate_pins_unchanged=True,copied_actor_protocol_sourcefreeze_exact=True,UE_started=False,UBT_started=False,actual_capture_started=False,formal_complete_units=0)
if '--write-receipt' in sys.argv:
 p=C/'native-test-oracle-static-regression-v002.json';assert not p.exists();p.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result,ensure_ascii=False))
