"""Preserve original Hurt/Death/Stomp checks and add exact32 Dodge packages."""
from pathlib import Path
import ast,importlib.util
from dodge_manual_contract_v001 import *

def validate_production_set(base1254,files,p,workspace,checker_path):
 need(Path(workspace).resolve()==R,'Wrong workspace')
 a=read(check(p['production_extension_pin']))
 return validate_document(a,files,None,p['compiled_manifest_sha256'],base1254,checker_path)

def validate_document(a,files,old_manual,compiled_sha,base1254=None,checker_path=None):
 deps=inputs();p=dict(compiled_manifest_sha256=compiled_sha)
 if base1254 is None:
  need(old_manual is not None,'Actual historical manual context required')
  known44=read(check(old_manual['source_profile_prereg_pin']))
  guard_receipt=read(check(known44['actual_native_import_receipt_pin']))
  guard_manifest=read(check(guard_receipt['manifest']))
  base1254={check(x).relative_to(R).as_posix() for x in guard_manifest['old_production_files']}|{check(x['saved']).relative_to(R).as_posix() for x in guard_receipt['assets']}
 need(len(base1254)==1254,'Exact historical Guard1254 required')
 need(a['schema']=='Dodge1364-Root-production-extension-v001' and a['RootApproved'] is True and a['is_template'] is False,'Actual Root Dodge extension approval required')
 need(a['compiled_manifest_sha256']==compiled_sha and (a['expected_old_base'],a['expected_new_count'],a['expected_total'])==(1332,32,1364),'Wrong new snapshot/count binding')
 for k in ['automatic_inputs','diagnostic_damage','FinalAccepted']:need(a[k] is False,'Manual scope changed')
 spec=importlib.util.spec_from_file_location('frozen_Dodge32_import_contract',check(deps['Dodge_import_contract']));api=importlib.util.module_from_spec(spec);spec.loader.exec_module(api)
 mp=check(a['Dodge32_import_manifest_pin']);m=api.load_manifest(mp)
 receipt_pin=a['Dodge32_native_receipt_pin'];receipt=read(check(receipt_pin));proof=read(check(a['Dodge32_independent_twoSHA_pin']))
 need(receipt['schema']=='hero-Dodge32-native-import-v001' and receipt['success'] is True and receipt['manifest']==pin(mp) and receipt['actual_total']==receipt['total_production_files']==1364,'Actual native Dodge32 receipt required')
 api.validate_receipt_assets(m,receipt)
 need(proof['schema']=='Dodge32-independent-import-twoSHA-v001' and proof['success'] is True and proof['old1332_unchanged_twice'] is True and proof['new32_saved_twice'] is True and proof['verification_passes']==2 and proof['hash_mismatches']==0 and proof['exact_total']==1364 and proof['manifest']==pin(mp) and proof['receipt']==receipt_pin,'Actual independent Dodge32/old1332 proof required')
 check(receipt['importer']);check(receipt['contract']);check(proof['verifier'])
 old_snapshot=read(check(deps['base_v139_snapshot']));base_rows={x['path']:x for x in old_snapshot['files'] if x['path'].startswith('UnrealGame/Content/Production/')}
 need({x['path']:x for x in m['old_production_files']}==base_rows,'Dodge import did not preserve exact v1391332 pins')
 extra=set()
 for x in receipt['assets']:
  saved=check(x['saved']);rel=saved.relative_to(R).as_posix();need(rel not in base_rows and rel not in extra,'Dodge package overlaps old/another source');extra.add(rel)
  need(files.get(rel)==dict(x['saved'],path=rel),'Actual new saved package not equal fresh compiled pin')
 need(len(extra)==32 and {n for n in files if n.startswith('UnrealGame/Content/Production/')}==set(base_rows)|extra,'Current compiled set is not exact1332+32')
 # Keep historical1332 checks intact. Only project these exact32 paths from
 # both historical live-set comparisons; metadata/bindings/source gates stay.
 old_helper=check(deps['v010_extension']);text=old_helper.read_text(encoding='utf-8-sig')
 before="need({x.relative_to(R).as_posix() for x in (R/'UnrealGame/Content/Production').rglob('*') if x.is_file()}==expected"
 need(text.count(before)==1 and text.count('base_adapter(extra)(base1254')==1,'Frozen historical helper shape changed')
 text=text.replace(before,before.replace('}==expected','}-DODGE_EXTRA_PATHS==expected')).replace('base_adapter(extra)(base1254','base_adapter(extra|DODGE_EXTRA_PATHS)(base1254')
 historical_pin=a['base_Stomp1332_approval_pin'];historical=read(check(historical_pin));old_p=dict(p,production_extension_pin=historical_pin,compiled_manifest_sha256=historical['compiled_manifest_sha256'])
 scope={'__file__':str(old_helper),'__name__':'Dodge32_historical_1332_projection','DODGE_EXTRA_PATHS':extra}
 exec(compile(ast.parse(text),str(old_helper),'exec'),scope)
 scope['validate_production_set'](base1254,{n:x for n,x in files.items() if n not in extra},old_p,R,checker_path)
 for repeat in range(2):
  api.verify_old(m['old_production_files']);api.exact_membership(m,True)
  for x in receipt['assets']:check(x['saved'])
 return dict(old_base=1332,Dodge=32,total=1364,old_and_new_current_twoSHA=True)
