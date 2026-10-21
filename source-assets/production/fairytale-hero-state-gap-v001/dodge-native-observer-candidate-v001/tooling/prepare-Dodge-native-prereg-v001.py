"""Root-executed fill helper. Reads actual fresh manual checkpoint; never launches UE."""
from pathlib import Path
import argparse,json,runpy,sys
HERE=Path(__file__).resolve().parent;C=HERE.parent
sys.path.insert(0,str(HERE))
api=runpy.run_path(str(HERE/'verify-Dodge-native-v001.py'))
read,pin,fact,need,path=[api[k]for k in ['read','pin','fact','need','path']]

def main():
 p=argparse.ArgumentParser();p.add_argument('--snapshot',required=True);p.add_argument('--manual-input',required=True);p.add_argument('--out-dir',required=True);p.add_argument('--approve-limited-native',action='store_true');a=p.parse_args()
 need(a.approve_limited_native,'Root explicit limited native prereg approval required')
 snapshot=path(a.snapshot);manual=path(a.manual_input);out=path(a.out_dir);need(not out.exists(),'New Root prereg directory required, preserve earlier versions')
 api['frozen'](C/api['OWN']);api['frozen'](C/api['SOURCE'])
 result=runpy.run_path(str(api['MANUAL']/'verify-Dodge1364-manual-input-v001.py'))['verify'](manual,snapshot)
 cm=snapshot/'compiled-source-manifest.json';m=read(cm);mm=read(manual);need(pin(mm['snapshot_manifest_pin'])==cm.resolve(),'Fresh manual and snapshot differ')
 d=read(C/'read-only-input-pins-v001.json')['inputs']
 base=dict(schema='hero-Dodge4-Root-prereg-v001',is_template=False,RootApproved=True,pre_registered_before_capture=True,FinalAccepted=False,
  compiled_manifest_pin=fact(cm),compiled_manifest_sha256=fact(cm)['sha256'],expected_source_files=m['source_files'],expected_production_files=m['production_files'],expected_strict_registered_tests=m['strict_registered_tests'],
  manual_input_pin=fact(manual),candidate_freeze_pin=fact(C/api['OWN']),source_probe_freeze_pin=fact(C/api['SOURCE']),
  Dodge_production_candidate_freeze_pin=d['Dodge_production_candidate_freeze_pin'],prepared_profile_pin=d['prepared_profile_pin'],Dodge_source_manifest_pin=d['Dodge_source_manifest_pin'],
  scope='One outward normal Shift/unblocked185 native trial per fresh side, source/GPU/optical review limited; no backwards/blocked visual claim.',audio_recorded=False,formal_complete_units=0)
 out.mkdir(parents=True)
 for side,name in [(-1,'left'),(1,'right')]:
  q=out/f'Root-Dodge4-prereg-{name}-v001.json';d={**base,'approach_side':side}
  with q.open('x',encoding='utf-8')as f:json.dump(d,f,indent=2);f.write('\n')
  api['preflight'](snapshot,q)
 with(out/'preparation-receipt-v001.json').open('x',encoding='utf-8')as f:json.dump(dict(schema='Root-Dodge4-native-prereg-preparation-v001',source_only_passed=True,UE_started=False,native_passed=False,manual_result=result,FinalAccepted=False),f,indent=2);f.write('\n')
 print(out.as_posix())
if __name__=='__main__':main()
