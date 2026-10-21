"""Versioned tool-only correction: compare exact normalized source AxisArtist.
The original b705 source, compiled inputs and every other oracle remain unchanged.
"""
from pathlib import Path
import argparse,ast,json,math,sys
C=Path(__file__).resolve().parent.parent;BASE=C.parent
OWN='Dodge-proof-repair-freeze-v002.json'
REPAIR_SCOPE='Exact normalized source AxisArtist RHS plus original completed-action Ready-to-Walk qualification only; all other v001 gates preserved'

def source_axis(spec):
 raw=spec['Axis_artist_raw_xy'];length=math.sqrt(sum(x*x for x in raw))
 if len(raw)!=2 or not math.isfinite(length)or length<=0:raise ValueError('Invalid retained author direction')
 return [x/length for x in raw]

def post_ready_walk_window(a,b,r,i,first_completed):
 if first_completed is None or i<first_completed or a['phase']not in[10,11]or b['phase']!=11:return False
 for o in[a,b]:
  d=o['dodge_record']
  if d['record_count']!=1 or d['action']!=r['dodge_action']or d['finish']!=1 or d['finished_at']!=r['dodge_end']:return False
 return True

def base_api():
 source=BASE/'tooling/verify-Dodge-native-v001.py';scope={'__file__':str(source),'__name__':'Dodge_v001_immutable_oracle'}
 exec(compile(source.read_text(encoding='utf-8-sig'),str(source),'exec'),scope)
 scope['frozen'](BASE/'Dodge-native-observer-freeze-v001.json')
 tree=ast.parse(source.read_text(encoding='utf-8-sig'));fn=next(x for x in tree.body if isinstance(x,ast.FunctionDef)and x.name=='verify_draw');edits=0
 for node in ast.walk(fn):
  if isinstance(node,ast.Assign)and len(node.targets)==1 and isinstance(node.targets[0],ast.Name)and node.targets[0].id=='axis':
   assert ast.dump(node.value)==ast.dump(ast.parse("spec['Axis_artist_raw_xy']",mode='eval').body),'Unexpected old axis contract'
   node.value=ast.parse('source_axis(spec)',mode='eval').body;edits+=1
 assert edits==1,'Exactly one normalized source-axis RHS correction required'
 scope['source_axis']=source_axis;exec(compile(ast.fix_missing_locations(ast.Module(body=[fn],type_ignores=[])),str(source),'exec'),scope)
 vf=next(x for x in tree.body if isinstance(x,ast.FunctionDef)and x.name=='verify');join_edits=0
 original=ast.parse('join(a,r,False)and join(b,r,True)',mode='eval').body
 for node in ast.walk(vf):
  if isinstance(node,ast.If)and ast.dump(node.test)==ast.dump(original):
   node.test=ast.BoolOp(op=ast.And(),values=[node.test,ast.parse('post_ready_walk_window(a,b,r,i,first_completed)',mode='eval').body]);join_edits+=1
 assert join_edits==1,'Exactly one completed-action Ready→Walk qualification required'
 scope['post_ready_walk_window']=post_ready_walk_window;exec(compile(ast.fix_missing_locations(ast.Module(body=[vf],type_ignores=[])),str(source),'exec'),scope)
 return scope

def preflight(snapshot,prereg):
 a=base_api();p=a['read'](prereg);need=a['need'];pin=a['pin'];fact=a['fact']
 need(p['schema']=='hero-Dodge4-Root-proof-amendment-v002'and p['is_template']is False and p['RootApproved']is True and p['pre_registered_before_capture']is True and p['FinalAccepted']is False,'Explicit actual Root proof repair amendment required')
 a['frozen'](C/OWN);need(p['proof_repair_freeze_pin']==fact(C/OWN)and p['proof_repair_checker_pin']==fact(C/'tooling/verify-Dodge-native-v002.py'),'Root repair freeze/checker differs');pin(p['proof_repair_freeze_pin']);pin(p['proof_repair_checker_pin'])
 need(p['base_observer_freeze_pin']==fact(BASE/'Dodge-native-observer-freeze-v001.json')and p['source_probe_freeze_pin']==fact(BASE/'Dodge-observer-source-freeze-v001.json'),'Source/observer unchanged binding differs')
 fixed=a['read'](C/'immutable-input-pins-v002.json')
 for key in ['base_observer_freeze','source_probe_freeze','old_checker','same_compiled_manifest','same_manual_input']:pin(fixed[key])
 need(p['compiled_manifest_pin']==fixed['same_compiled_manifest']and p['manual_input_pin']==fixed['same_manual_input'],'This repair is limited to the exact actual v140 CM/manual')
 original=pin(p['base_Root_prereg_pin']);m,b,profile,manifest,gate=a['preflight'](snapshot,original)
 need(p['compiled_manifest_pin']==b['compiled_manifest_pin']and p['manual_input_pin']==b['manual_input_pin']and p['approach_side']==b['approach_side']and p['repair_scope']==REPAIR_SCOPE,'Amendment exceeds same CM/manual/side and two precise oracle repairs')
 return a,m,b,profile,manifest,p

def verify(archive,snapshot,prereg):
 a,m,b,profile,manifest,p=preflight(snapshot,prereg);index=a['read'](archive/'index.json')
 a['need'](index['proof_repair_freeze_sha256']==p['proof_repair_freeze_pin']['sha256']and index['proof_repair_checker_sha256']==p['proof_repair_checker_pin']['sha256'],'New native session not bound to repair checker/freeze')
 result=a['verify'](archive,b,profile,manifest,prereg)
 report=a['read'](archive/'原件/runtime-report.json');obs=report['observations'];excluded=[]
 for i in range(len(obs)-1):
  x,y=obs[i:i+2]
  if x['dodge_record']['record_count']==0 and y['dodge_record']['record_count']==0 and a['join'](x,report,False)and a['join'](y,report,True):excluded.append(dict(kind='pre_action_staging_Ready_to_Walk_no_recovery_credit',from_observation=i,to_observation=i+1))
 result.update(schema='hero-Dodge4-independent-native-v002',proof_repair_freeze_pin=p['proof_repair_freeze_pin'],proof_repair_checker_pin=p['proof_repair_checker_pin'],base_Root_prereg_pin=p['base_Root_prereg_pin'],source_probe_unchanged=True,normalized_source_axis_exact=True,excluded_pre_action_ready_walk_edges=excluded)
 return result

def main():
 a=argparse.ArgumentParser();a.add_argument('--snapshot',required=True);a.add_argument('--root-prereg',required=True);a.add_argument('--archive');a.add_argument('--source-only',action='store_true');a.add_argument('--write-receipt',action='store_true');q=a.parse_args();api=base_api();snapshot=api['path'](q.snapshot);prereg=api['path'](q.root_prereg)
 if q.source_only:
  _,m,b,_,_,_=preflight(snapshot,prereg);print(json.dumps(dict(compiled_inputs_verified=True,strict_registry=196,production_files=1364,source_files=m['source_files'],Dodge_source32=32,approach_side=b['approach_side'],proof_repair_v002=True,UE_started=False)));return
 api['need'](q.archive,'New actual native archive required');archive=api['path'](q.archive);result=verify(archive,snapshot,prereg)
 if q.write_receipt:
  with(archive/'原件/Dodge-independent-native-verification-v002.json').open('x',encoding='utf-8')as f:json.dump(result,f,ensure_ascii=False,indent=2);f.write('\n')
 print(json.dumps(result,ensure_ascii=False))
if __name__=='__main__':main()
