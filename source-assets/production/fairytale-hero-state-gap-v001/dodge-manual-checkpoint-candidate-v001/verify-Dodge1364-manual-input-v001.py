"""v011 manual-only196/1364 gate with exact v139 Source admission chain."""
from pathlib import Path
import argparse,json
from dodge_manual_contract_v001 import *

def verify(path,snapshot=None):
 m=read(resolve(path));core=core_adapter();result=core['verify'](resolve(path),snapshot)
 cm=read(check(m['snapshot_manifest_pin']));files={x['path']:x for x in cm['files']};source_chain(m,files)
 deps=inputs();old_suite=read(check(deps['base193_full_suite']));preserve193(read(check(m['full_suite_pin'])),{x['fullTestPath'] for x in old_suite['tests']},set(DODGE_TESTS))
 old=old_api();a=read(check(m['Stomp50_row_approval_pin']));old['overlay_rows'](a)
 base_manual=read(check(deps['v139_manual']));base_rows=read(check(base_manual['Stomp50_row_approval_pin']))
 need(a['rows']==base_rows['rows'] and a['compiled_manifest_sha256']==pin(check(m['snapshot_manifest_pin']))['sha256'],'Stomp six metadata or fresh binding changed')
 prereg=read(check(m['source_profile_prereg_pin']));base_profile=read(check(base_manual['source_profile_prereg_pin']))
 need(prereg['profile_facts']==base_profile['profile_facts'] and prereg['all_profile_rows']==base_profile['all_profile_rows'],'Known44/13row facts changed')
 for key in ['admitted_Hurt_source_files','admitted_Stomp_source_files','admitted_Dodge_source_files']:
  rows=m[key];need(len({x['path'] for x in rows})==len(rows),'Duplicate current Source interface pin')
  for x in rows:need(files.get(x['path'])==x,'Interface not bound to current compiled Source');check(x)
 need({x['path'] for x in m['admitted_Hurt_source_files']}=={x['path'] for x in base_manual['admitted_Hurt_source_files']},'Hurt interface omitted')
 need({x['path'] for x in m['admitted_Stomp_source_files']}=={x['path'] for x in base_manual['admitted_Stomp_source_files']},'Stomp interface omitted')
 need({x['path'] for x in m['admitted_Dodge_source_files']}==STAGE_NEW|PROD_NEW|OBSERVER_NEW|COMMON,'Dodge interfaces incomplete')
 trial=runtime_trial(m,cm);ext=read(check(m['production_extension_approval_pin']))
 need(ext['Stomp50_row_approval_pin']==m['Stomp50_row_approval_pin'],'Manual and production Stomp row bindings differ')
 for key in ['Dodge32_import_manifest_pin','Dodge32_native_receipt_pin','Dodge32_independent_twoSHA_pin']:need(trial[key]==ext[key],'Runtime and import approval provenance differ')
 need(m['Dodge_flag']==trial['flag'] and m['Dodge_imported_textures']==32 and m['Dodge_preload_total']==33,'Dodge manual scope differs')
 result.update(strict_registry=196,production_files=1364,Dodge_imported_textures=32,Dodge_preload_total=33,Dodge_flag=trial['flag'],Stomp_overlay_unique=50)
 return result

def main():
 p=argparse.ArgumentParser();p.add_argument('--manual-input',required=True);p.add_argument('--snapshot');a=p.parse_args()
 print(json.dumps(verify(a.manual_input,a.snapshot)))
if __name__=='__main__':main()
