"""Actual five-receipt Source283 check + narrow AST/negative tests. No UE."""
import argparse,ast,copy,hashlib,json,runpy
import move7_native_contract_v001 as a
def fn(tree,name):return next(x for x in tree.body if isinstance(x,ast.FunctionDef)and x.name==name)
def dump(node):return ast.dump(node,include_attributes=False)
def tree(p):return ast.parse(p.read_text(encoding='utf-8-sig'))
def reject(call):
 try:call()
 except(ValueError,KeyError,TypeError,AssertionError):return
 raise AssertionError('Invalid named-closure input accepted')
def check(observer_receipt):
 old=tree(a.C/'tooling/move7_native_contract_v001.py');new=tree(a.D/'tooling/move7_native_contract_v001.py');same=['need','path','read','fact','pin','equalpin','keyed','bytes_equal','strict_suite','source_chain']
 for name in same:a.need(dump(fn(old,name))==dump(fn(new,name)),'Unrelated contract function changed: '+name)
 x=fn(old,'frozen');y=fn(new,'frozen');a.need(dump(x.body[0])==dump(y.body[0])and[dump(n)for n in x.body[1:]]==[dump(n)for n in y.body[2:]],'Original files[] frozen loop changed')
 before=fn(old,'preflight');after=copy.deepcopy(fn(new,'preflight'));removed=[]
 for s in list(after.body):
  if isinstance(s,ast.Expr)and ('DERIVATIVE_FREEZE'in dump(s)or'tool_contract_fix_freeze_pin'in dump(s)):
   removed.append(s);after.body.remove(s)
 a.need(len(removed)==2 and dump(before)==dump(after),'Preflight differs beyond two derivative binding statements')
 old=tree(a.C/'tooling/verify-Move7-native-v001.py');new=tree(a.D/'tooling/verify-Move7-native-v001.py')
 for name in [n.name for n in old.body if isinstance(n,ast.FunctionDef)and n.name!='verify']:a.need(dump(fn(old,name))==dump(fn(new,name)),'Native geometry/threshold helper changed: '+name)
 before=fn(old,'verify');after=copy.deepcopy(fn(new,'verify'));removed=0
 for s in list(after.body):
  if isinstance(s,ast.Expr)and'Native session derivative tool binding differs'in dump(s):after.body.remove(s);removed+=1
 changes={'paths':0,'metadata':0}
 class Transparent(ast.NodeTransformer):
  def visit_BinOp(self,n):
   if isinstance(n.left,ast.Name)and n.left.id=='D'and isinstance(n.right,ast.Constant)and n.right.value in['tooling/verify-Move7-native-pixels-v001.py','tooling/verify-Move7-source-pixels-v001.py']:n.left.id='C';changes['paths']+=1
   return self.generic_visit(n)
  def visit_Call(self,n):
   if isinstance(n.func,ast.Name)and n.func.id=='dict':
    for k in list(n.keywords):
     if k.arg in['tool_contract_fix_freeze_pin','tool_contract_fix_checker_pin']:n.keywords.remove(k);changes['metadata']+=1
   return self.generic_visit(n)
 after=Transparent().visit(after);a.need(removed==1 and changes==dict(paths=2,metadata=2)and dump(before)==dump(after),'Native oracle differs beyond execution path and derivative binding metadata')
 a.need((a.C/'tooling/verify-Move7-source-pixels-v001.py').read_bytes()==(a.D/'tooling/verify-Move7-source-pixels-v001.py').read_bytes(),'Optical algorithm/thresholds changed')
 old=tree(a.C/'tooling/verify-Move7-native-pixels-v001.py');new=tree(a.D/'tooling/verify-Move7-native-pixels-v001.py');oldassign=next(x for x in old.body if isinstance(x,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='protocol'for t in x.targets));newassign=next(x for x in new.body if isinstance(x,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='protocol'for t in x.targets));newassign.value=copy.deepcopy(oldassign.value);a.need(dump(old)==dump(new),'CRC/FIFO/stop-flush algorithm changed')
 old=tree(a.C/'tooling/fill-Move7-native-prereg-v001.py');new=tree(a.D/'tooling/fill-Move7-native-prereg-v001.py');removed=0
 for n in ast.walk(new):
  if isinstance(n,ast.Call)and isinstance(n.func,ast.Attribute)and n.func.attr=='update':
   for k in list(n.keywords):
    if k.arg in['tool_contract_fix_freeze_pin','tool_contract_fix_checker_pin']:n.keywords.remove(k);removed+=1
 a.need(removed==2 and dump(old)==dump(new),'Root fill helper differs beyond derivative pins')
 a.frozen(a.C/'Move7-native-observer-freeze-v001.json')
 p=a.read(a.C/'Root-Move7-native-prereg-TEMPLATE-v001.json');p['source_extension_chain'][-1]['receipt_pin']=a.fact(observer_receipt);base=a.read(a.read(a.C/'read-only-input-pins-v001.json')['inputs']['base_compiled_manifest']['path'])
 original=runpy.run_path(str(a.C/'tooling/move7_native_contract_v001.py'));old_failed=False
 try:original['source_chain'](p,base)
 except KeyError as ex:old_failed=ex.args==('files',)
 a.need(old_failed,'Original exact files[] incompatibility no longer reproduced')
 expected=a.source_chain(p,base);actual=a.keyed([a.fact(x)for x in(a.ROOT/'UnrealGame/Source').rglob('*')if x.is_file()]);a.need(actual==expected,'Actual current Source differs from exact five-receipt map')
 receipt=a.read(a.pin(p['source_extension_chain'][1]['receipt_pin']));typed=a.read(a.pin(receipt['candidate_freeze']));a.fourth_test_closure(typed);negatives=0
 for key in ['test_source','exact_beforepins','stage0_v001_freeze']:
  bad=copy.deepcopy(typed);bad[key]['sha256']='0'*64;reject(lambda:a.fourth_test_closure(bad));negatives+=1
 bad=copy.deepcopy(typed);bad['schema']='unknown-files-free-closure';reject(lambda:a.fourth_test_closure(bad));negatives+=1
 bad=copy.deepcopy(typed);bad['independent_backend_sources'][0]['path']=str(a.ROOT/'UnrealGame/Source/CodexDungeon/DungeonHUD.cpp');reject(lambda:a.fourth_test_closure(bad));negatives+=1
 bad=copy.deepcopy(typed);bad['independent_backend_sources'][0]['sha256']='0'*64;reject(lambda:a.fourth_test_closure(bad));negatives+=1
 return dict(schema='Move7-tool-contract-fix-actual-source-chain-review-v002',passed=True,actual_source_count=len(expected),five_actual_admissions=[x['role']for x in p['source_extension_chain']],all_current_Source_members_match=True,original_contract_KeyError_files_reproduced=True,typed_fourth_named_closure_verified=True,actual_test_source_pin=typed['test_source'],historical_exact_before_count=278,exact_engine_backend_source_pins=typed['independent_backend_sources'],negative_tests_rejected=negatives,original_files_closure_loop_AST_unchanged=True,source_chain_AST_unchanged=True,old_native_oracle_AST_unchanged_except_derivative_routing_and_pins=True,CRC_FIFO_stop_flush_AST_unchanged_except_protocol_path=True,optics_byte_identical=True,old28_freeze_members_unchanged=True,full_native_preflight_performed=False,final283_full200_GREEN_claimed=False,UE_started=False,Source_written=False)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--observer-admission',required=True);p.add_argument('--output');q=p.parse_args();result=check(a.path(q.observer_admission))
 if q.output:
  with a.path(q.output).open('x',encoding='utf-8')as f:json.dump(result,f,ensure_ascii=False,indent=2);f.write('\n')
 print(json.dumps(result,ensure_ascii=False))
