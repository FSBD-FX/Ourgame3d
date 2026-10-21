"""Fill NEW Root preregs from actual inputs; no source/approval/media/UE writes.
Root explicitly acknowledges pre-registration, never inferred from elapsed time.
"""
import argparse,json
from move7_native_contract_v001 import *
def main():
 a=argparse.ArgumentParser();a.add_argument('--snapshot',required=True);a.add_argument('--production-admission',required=True);a.add_argument('--observer-admission',required=True);a.add_argument('--runtime-approval',required=True);a.add_argument('--output',required=True);a.add_argument('--approve-prereg',action='store_true');q=a.parse_args()
 need(q.approve_prereg,'Root explicit --approve-prereg required; source-only candidate cannot approve itself');output=path(q.output);need(not output.exists(),'NEW output leaf required; never overwrite Root preregs')
 snapshot=path(q.snapshot);cm=snapshot/'compiled-source-manifest.json';m=read(cm);template=read(C/'Root-Move7-native-prereg-TEMPLATE-v001.json');results=[]
 # Validate in memory before creating any output, using the same public gate.
 for side in[-1,1]:
  d=dict(template);d['source_extension_chain']=[dict(x)for x in template['source_extension_chain']];d.update(is_template=False,RootApproved=True,pre_registered_before_capture=True,approval_method='Root CLI --approve-prereg',approach_side=side,expected_source_files=m['source_files'],compiled_manifest_pin=fact(cm),candidate_freeze_pin=fact(C/'Move7-native-observer-freeze-v001.json'),source_probe_freeze_pin=fact(SOURCE_FREEZE),runtime_trial_approval_pin=fact(q.runtime_approval))
  d['source_extension_chain'][3]['receipt_pin']=fact(q.production_admission);d['source_extension_chain'][4]['receipt_pin']=fact(q.observer_admission);results.append((side,d))
 # Temporary NEW candidate-only files are not written. Gate read() is narrowly
 # adapted for the future output path; all other path reads stay real read-only.
 import move7_native_contract_v001 as api
 oldread=api.read
 try:
  for side,d in results:
   destination=output/('Root-Move7-'+('left'if side<0 else'right')+'-prereg-v001.json')
   api.read=lambda p,d=d,destination=destination:d if path(p)==destination else oldread(p)
   api.preflight(snapshot,destination)
 finally:api.read=oldread
 output.mkdir(parents=True,exist_ok=False)
 for side,d in results:
  destination=output/('Root-Move7-'+('left'if side<0 else'right')+'-prereg-v001.json')
  with destination.open('x',encoding='utf-8')as f:json.dump(d,f,ensure_ascii=False,indent=2);f.write('\n')
 print(json.dumps(dict(pre_registered=True,source_only_verified=True,outputs=[fact(p)for p in output.glob('*.json')],UE_started=False,native_passed=False,FinalAccepted=False),ensure_ascii=False))
if __name__=='__main__':main()
