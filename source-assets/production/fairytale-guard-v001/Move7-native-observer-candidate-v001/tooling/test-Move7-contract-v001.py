"""Host-only rejecting gates and immutable algorithm checks; no UE/media."""
import ast,copy,json,math,runpy,sys
from move7_native_contract_v001 import *
def reject(fn):
 try:fn()
 except(ValueError,AssertionError,KeyError,TypeError):return
 raise AssertionError('Invalid fixture unexpectedly accepted')
fixed=read(C/'read-only-input-pins-v001.json')['inputs'];base=read(pin(fixed['base_compiled_manifest']));old=read(pin(base['full_suite']));names={x['fullTestPath']for x in old['tests']};need(len(names)==196 and not names&TESTS,'Actual historical registry changed')
# Deliberately synthetic GREEN envelope tests only the registry gate, not UE.
suite=copy.deepcopy(old);suite['tests']+=[dict(fullTestPath=n,state='Success',errors=0,warnings=0,entries=[])for n in sorted(TESTS)];suite['succeeded']=200
strict_suite(suite,names|TESTS);count=1
for kind in ['missing','duplicate','failed','error','warning','counter']:
 s=copy.deepcopy(suite)
 if kind=='missing':s['tests'].pop()
 elif kind=='duplicate':s['tests'].append(copy.deepcopy(s['tests'][-1]))
 elif kind=='failed':s['tests'][-1]['state']='Fail'
 elif kind=='error':s['tests'][-1]['errors']=1
 elif kind=='warning':s['tests'][-1]['entries']=[dict(event=dict(type='Warning'))]
 else:s['notRun']=1
 reject(lambda:strict_suite(s,names|TESTS));count+=1
reject(lambda:preflight(ROOT/'source-assets/production/backups/v140-Dodge196G',C/'Root-Move7-native-prereg-TEMPLATE-v001.json'));count+=1
own=ast.parse((C/'tooling/verify-Move7-native-pixels-v001.py').read_text(encoding='utf-8-sig'));ref=ast.parse(pin(fixed['native_pixel_helper_reference']).read_text(encoding='utf-8-sig'))
own.body.pop(0);ref.body.pop(0);need(ast.dump(own)==ast.dump(ref),'Native CRC/FIFO/stop-flush algorithm changed');count+=1
api=runpy.run_path(str(C/'tooling/verify-Move7-native-v001.py'));need(len({f['object_path']for row in api['legacy_rows']().values()for f in row['frames']})==50,'Old known44 plus Stomp6 source facts changed');count+=1;need(api['float_near'](640.,640.)and not api['float_near'](640.01,640.)and not api['float_near'](math.nan,0.),'Declared float numerical comparison invalid');count+=1
dx=5.4473444223403931;q=dict(facing=1,**{'from':[0.,0.],'to':[dx,0.],'direction':[dx*(1/dx),0.]});need(q['direction'][0]!=1 and api['straight_move'](q,[140,0],[0,0],1),'Legal UE reciprocal-multiply direction rejected');count+=1
for key,value in [('facing',-1),('to',[dx,1.]),('to',[-dx,0.])]:
 b=copy.deepcopy(q);b[key]=value;need(not api['straight_move'](b,[140,0],[0,0],1),'Wrong facing/Y/X direction earned straight cycle credit');count+=1
solver=runpy.run_path(str(pin(fixed['host_solver'])))['ReferenceSolver'](pin(fixed['prepared_profile']),PROFILE_SHA);profile=solver.profile
for side in [-1,1]:
 for distance in [0.,21.5,43.,64.,85.5,107.,128.]:
  req=dict(owner_entity_id=7,accepted_path_owner_entity_id=7,accepted_distance_world=distance,actual_facing=side,screen_ground_px=[640.,490.],ui_scale=1,source_snapshot_sha256=SNAPSHOT_SHA,profile_sha256=PROFILE_SHA,atomic_texture_ready_paths=[x['texture_object_path']for x in profile['source7']]);result=solver.solve(req);need(result['valid_reference_plan']and result['part_count']==7 and result['reflection_count']==int(side<0),'Frozen host solver reference unavailable');count+=1
  if distance==0:
   bad=copy.deepcopy(req);bad['atomic_texture_ready_paths'].pop();need(not solver.solve(bad)['valid_reference_plan'],'Incomplete source7 host request accepted');count+=1
print(json.dumps(dict(schema='Move7-observer-host-contract-checks-v001',passed=True,checks=count,strict_suite_fixture='Synthetic gate-only envelope; actual old196 pins verified, no new UE GREEN claimed',actual_native_run=False,UE_started=False,media_created=False)))
