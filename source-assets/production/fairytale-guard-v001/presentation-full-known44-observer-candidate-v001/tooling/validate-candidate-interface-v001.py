"""Read-only static adversarial interface checks; never launches UE or creates native evidence."""
from pathlib import Path
import ast,copy,hashlib,json,runpy,sys
C=Path(__file__).resolve().parent.parent
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
for row in read(C/'source-AxeCycle-freeze-v001.json')['files']:
 p=C/row['path'];assert p.stat().st_size==row['bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==row['sha256']
for p in (C/'tooling').glob('*.py'):ast.parse(p.read_text(encoding='utf-8-sig'))
ns=runpy.run_path(str(C/'tooling/verify-known44-axecycle-v001.py'))
template=read(C/'root-templates/known44-AxeCycle-Root-prereg-TEMPLATE-v001.json')
known={r['clip']:r for r in read(C.parent/'presentation-full-candidate-v003/source-registration-resource-map-v003.json')['rows'] if r['source_pose_approved']}
cases=[]
def ok(name,p):
 assert len(ns['profile_facts'](p,known))==10
 cases.append(dict(case=name,result='accepted_static_interface_only'))
def bad(name,change):
 p=copy.deepcopy(template);change(p)
 try:ns['profile_facts'](p,known)
 except (ValueError,KeyError):cases.append(dict(case=name,result='rejected'))
 else:raise AssertionError('Counterexample accepted: '+name)
ok('10 known facts plus all13 with3 closed gaps',template)
p=copy.deepcopy(template);p['profile_facts']=copy.deepcopy(p['all_profile_rows']);ok('13 profile facts plus identical all13',p)
bad('duplicate known clip',lambda p:p['profile_facts'].append(copy.deepcopy(p['profile_facts'][0])))
bad('unknown all14 clip',lambda p:p['all_profile_rows'].append(dict(clip='Invented')))
bad('missing explicit13 table',lambda p:p.pop('all_profile_rows'))
bad('known tables differ',lambda p:p['all_profile_rows'][0].update(trial_allowed=False))
for clip in ['Move','StompActive','StompRecovery']:
 for key,value in [('native_source_id',225),('trial_allowed',True),('source_pose_approved',True),('frames',[{}])]:
  bad(clip+' forbidden '+key,lambda p,clip=clip,key=key,value=value:next(r for r in p['all_profile_rows'] if r['clip']==clip).update({key:value}))
strict=ns['strict_approach'];credit=ns['spatial_credit']
assert strict([-650,-160],[-800,-160],1) and strict([-950,-160],[-800,-160],-1)
assert not strict([-798.3977,-116],[-800,-160],1)
cases.append(dict(case='old right-facing overlap dx1.6023 dy44',result='rejected'))
o=dict(phase='normal_guard_approach_and_cycles',player_ground=[-650,-260],approach_spatial=dict(route_reached=True),guard_native=dict(ground=[-800,-160],attack_id='7',attack_kind=1,interrupted=False,phase=4,locked=True,lock_at=10.,active_end=10.7))
d=dict(Selection=dict(Clip='AxeActive',Facing=1,AttackId='7',Frame=0,SampleTime=10.5))
assert credit(o,d,1,7) and not credit(o,d,1,8)
cases.append(dict(case='later AttackId cannot fill selected Active mask',result='rejected'))
o['guard_native']['locked']=False;assert not credit(o,d,1,7)
cases.append(dict(case='unlocked Active cannot earn coverage',result='rejected'))
pixel=ast.parse((C/'tooling/verify-known44-native-pixels-v001.py').read_text(encoding='utf-8-sig'))
gate=next(x for x in pixel.body if isinstance(x,ast.Assert) and "report['schema']" in ast.unparse(x.test))
code=compile(ast.Expression(gate.test),'<exact-native-schema-and-scenario>','eval');protocol=read(C/'proof-protocol-v001.json')
for schema,scenario,expected in [(protocol['runtime_report_schema'],'AxeCycle',True),('guard-art-partial-native-observer-v009','AxeCycle',False),('guard-art-partial-native-observer-v002','AxeCycle',False),(protocol['runtime_report_schema'],'StunIR',False)]:
 assert eval(code,{},dict(report=dict(schema=schema,scenario=scenario),protocol=protocol)) is expected
 cases.append(dict(case='pixel schema '+schema+'/'+scenario,result='accepted_static_gate_only' if expected else 'rejected'))
old=ast.parse((C.parent/'presentation-observer-route-tooling-candidate-v010/tooling/verify-native-pixels-v010.py').read_text(encoding='utf-8-sig'))
def remaining_asserts(tree):return [ast.dump(x,include_attributes=False) for x in ast.walk(tree) if isinstance(x,ast.Assert)][1:]
assert remaining_asserts(old)==remaining_asserts(pixel)
cases.append(dict(case='native CRC/FIFO/stop-flush assert AST after versioned schema gate',result='identical_to_frozen_v010'))
source=(C/'new-source/DungeonGuardArtKnown44Probe.cpp').read_text(encoding='utf-8-sig')
assert not any(x in source for x in ['StepTo(','SetActorLocation(','TryStartAttack(','ApplyResolvedHit('])
assert 'E&&!E->GetStoneGuardDriver()' in source
result=dict(schema='known44-AxeCycle-static-interface-validation-v001',passed=True,UE_started=False,UBT_started=False,actual_native_execution=False,visual_reviewed=False,formal_complete_units=0,source_frozen_files_unchanged=True,python_AST_parsed=len(list((C/'tooling').glob('*.py'))),static_cases=cases,limitation='Static interface/adversarial oracle checks only; no native success, rendered coverage or visual acceptance follows.')
if '--write-receipt' in sys.argv:
 p=C/'static-interface-validation-v001.json';assert not p.exists(),'Never overwrite static receipt'
 p.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result,ensure_ascii=False))
