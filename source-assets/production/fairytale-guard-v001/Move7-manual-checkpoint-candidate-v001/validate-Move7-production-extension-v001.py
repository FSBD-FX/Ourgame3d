"""Exact old1364 plus seven Move7 packages, retaining every v011 asset gate."""
from pathlib import Path
import ast,copy
from move7_manual_contract_v001 import *

def projected_exact_membership(api,manifest,after):
 # Retain the original exact-membership function and insert one subtraction of
 # the seven previously verified new saved package paths before its assertion.
 tree=ast.parse(check(inputs()['Dodge_import_contract']).read_text(encoding='utf-8-sig'))
 fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='exact_membership')
 assigned=[i for i,n in enumerate(fn.body)if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='actual'for t in n.targets)]
 need(len(assigned)==1,'Frozen Dodge live membership AST shape changed')
 fn.body.insert(assigned[0]+1,ast.parse('actual=actual-MOVE7_EXTRA_ABSOLUTE').body[0])
 scope=dict(api.__dict__,MOVE7_EXTRA_ABSOLUTE={resolve(x)for x in ACTIVE_EXTRA})
 exec(compile(ast.fix_missing_locations(ast.Module(body=[fn],type_ignores=[])),str(check(inputs()['Dodge_import_contract'])),'exec'),scope)
 return scope['exact_membership'](manifest,after)

def historical_dodge_validate(base1254,files,extra,compiled_sha):
 global ACTIVE_EXTRA;ACTIVE_EXTRA=set(extra)
 deps=inputs();old_helper=check(deps['v011_extension']);text=old_helper.read_text(encoding='utf-8-sig')
 changes=[
  ('api.exact_membership(m,True)','projected_exact_membership(api,m,True)'),
  ("before.replace('}==expected','}-DODGE_EXTRA_PATHS==expected')","before.replace('}==expected','}-DODGE_EXTRA_PATHS-MOVE7_EXTRA_PATHS==expected')"),
  ("'base_adapter(extra|DODGE_EXTRA_PATHS)(base1254'","'base_adapter(extra|DODGE_EXTRA_PATHS|MOVE7_EXTRA_PATHS)(base1254'"),
  ("'DODGE_EXTRA_PATHS':extra}","'DODGE_EXTRA_PATHS':extra,'MOVE7_EXTRA_PATHS':MOVE7_EXTRA_PATHS}")]
 for before,after in changes:need(text.count(before)==1,'Frozen v011 extension seam changed: '+before);text=text.replace(before,after)
 scope={'__file__':str(old_helper),'__name__':'Move7_exact_saved7_historical_Dodge_projection','MOVE7_EXTRA_PATHS':set(extra),'projected_exact_membership':projected_exact_membership}
 exec(compile(ast.parse(text),str(old_helper),'exec'),scope)
 old_manual=read(check(deps['v011_manual']));historical_pin=old_manual['production_extension_approval_pin'];historical=read(check(historical_pin))
 old_files={n:x for n,x in files.items()if n not in extra}
 need(len([n for n in old_files if n.startswith('UnrealGame/Content/Production/')])==1364,'Only seven exact saved paths may be projected')
 return scope['validate_document'](historical,old_files,old_manual,historical['compiled_manifest_sha256'],base1254,None)

def move_extra(files,prereg,snapshot):
 cm,p,profile,imp,trial=move.preflight(resolve(snapshot),check(prereg))
 need(move.keyed(cm['files'])==move.keyed(list(files.values())),'Production helper is bound to another actual compiled map')
 native=read(move.pin(p['native_import_pin']));extra=set()
 for asset in native['assets']:
  saved=move.pin(asset['saved']);rel=saved.relative_to(R).as_posix()
  need(rel not in extra and rel.startswith('UnrealGame/Content/Production/'),'Repeated or foreign Move7 saved package')
  need(files.get(rel)==dict(asset['saved'],path=rel),'Move7 native saved package differs from current compiled bytes');extra.add(rel)
 need(len(extra)==7,'Exactly seven Move7 new saved packages required')
 old=read(check(inputs()['base_v140_snapshot']));oldprod={x['path']:x for x in old['files']if x['path'].startswith('UnrealGame/Content/Production/')}
 need({n:x for n,x in files.items()if n.startswith('UnrealGame/Content/Production/')and n not in extra}==oldprod and len(oldprod)==1364,'Old1364 bytes changed or non-Move7 package added')
 return extra

def validate_production_set(base1254,files,p,workspace,checker_path):
 need(Path(workspace).resolve()==R,'Wrong workspace');a=read(check(p['production_extension_pin']))
 return validate_document(a,files,p['compiled_manifest_sha256'],base1254)

def validate_document(a,files,compiled_sha,base1254):
 need(a['schema']=='Move7-Root-production-extension-v001'and a['RootApproved']is True and a['is_template']is False,'Actual Root Move7 production extension required')
 need(a['compiled_manifest_sha256']==compiled_sha and(a['expected_old_base'],a['expected_new_count'],a['expected_total'])==(1364,7,1371),'Exact current1364+7=1371 binding required')
 for k in['automatic_inputs','diagnostic_damage','FinalAccepted']:need(a[k]is False,'Manual extension scope expanded: '+k)
 deps=inputs();old_manual=read(check(deps['v011_manual']))
 need(a['base_Dodge1364_approval_pin']==old_manual['production_extension_approval_pin'],'Historical Dodge approval replaced')
 oldext=read(check(a['base_Dodge1364_approval_pin']))
 for k in['Dodge32_import_manifest_pin','Dodge32_native_receipt_pin','Dodge32_independent_twoSHA_pin']:need(a[k]==oldext[k],'Historical Dodge provenance changed')
 extra=move_extra(files,a['Move7_native_prereg_pin'],a['snapshot_directory'])
 need({x['path']for x in a['Move7_saved_packages']}==extra and len(a['Move7_saved_packages'])==7,'Explicit seven saved package closure differs')
 for x in a['Move7_saved_packages']:need(files[x['path']]==x,'Explicit saved7 pin differs');check(x)
 result=historical_dodge_validate(base1254,files,extra,compiled_sha)
 for _ in range(2):
  need({x.relative_to(R).as_posix()for x in(R/'UnrealGame/Content/Production').rglob('*')if x.is_file()}=={n for n in files if n.startswith('UnrealGame/Content/Production/')},'Actual1371 live membership changed')
  for n,x in files.items():
   if n.startswith('UnrealGame/Content/Production/'):check(x)
 return dict(old_base=1364,Move7=7,total=1371,old_and_new_current_twoSHA=True,old_Dodge_Hurt_Death_Stomp_checks=result)
