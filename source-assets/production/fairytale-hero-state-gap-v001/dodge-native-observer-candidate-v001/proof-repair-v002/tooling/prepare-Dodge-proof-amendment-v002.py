"""Root CLI amendment: same compiled Source/manual; explicit new proof checker pin."""
from pathlib import Path
import argparse,json,runpy
C=Path(__file__).resolve().parent.parent;A=runpy.run_path(str(C/'tooling/verify-Dodge-native-v002.py'))

def main():
 p=argparse.ArgumentParser();p.add_argument('--snapshot',required=True);p.add_argument('--left-base-prereg',required=True);p.add_argument('--right-base-prereg',required=True);p.add_argument('--out-dir',required=True);p.add_argument('--approve-proof-amendment',action='store_true');q=p.parse_args();api=A['base_api']();need=api['need'];fact=api['fact'];path=api['path']
 need(q.approve_proof_amendment,'Root explicit proof amendment CLI approval required')
 snapshot=path(q.snapshot);out=path(q.out_dir);need(not out.exists(),'New amendment directory required, retain all old prereg/evidence');api['frozen'](C/A['OWN']);rows=[]
 for side,name,source in [(-1,'left',q.left_base_prereg),(1,'right',q.right_base_prereg)]:
  base=path(source);m,b,_,_,_=api['preflight'](snapshot,base);need(b['approach_side']==side,'Base prereg side differs')
  d=dict(schema='hero-Dodge4-Root-proof-amendment-v002',is_template=False,RootApproved=True,pre_registered_before_capture=True,FinalAccepted=False,approach_side=side,
   compiled_manifest_pin=b['compiled_manifest_pin'],manual_input_pin=b['manual_input_pin'],base_Root_prereg_pin=fact(base),base_observer_freeze_pin=fact(A['BASE']/'Dodge-native-observer-freeze-v001.json'),source_probe_freeze_pin=fact(A['BASE']/'Dodge-observer-source-freeze-v001.json'),proof_repair_freeze_pin=fact(C/A['OWN']),proof_repair_checker_pin=fact(C/'tooling/verify-Dodge-native-v002.py'),repair_scope=A['REPAIR_SCOPE'],source_unchanged=True,compiled_snapshot_unchanged=True,old_failed_archive_reclassified=False,audio_recorded=False,formal_complete_units=0)
  rows.append((name,d))
 need(rows[0][1]['compiled_manifest_pin']==rows[1][1]['compiled_manifest_pin']and rows[0][1]['manual_input_pin']==rows[1][1]['manual_input_pin'],'Both new sessions must bind same compiled/manual input')
 out.mkdir(parents=True)
 for name,d in rows:
  target=out/f'Root-Dodge4-proof-amendment-{name}-v002.json'
  with target.open('x',encoding='utf-8')as f:json.dump(d,f,indent=2);f.write('\n')
  A['preflight'](snapshot,target)
 with(out/'preparation-receipt-v002.json').open('x',encoding='utf-8')as f:json.dump(dict(schema='Root-Dodge4-proof-amendment-preparation-v002',source_only_passed=True,UE_started=False,native_passed=False,Source_changed=False,old_failed_archive_changed=False,FinalAccepted=False),f,indent=2);f.write('\n')
 print(out.as_posix())
if __name__=='__main__':main()
