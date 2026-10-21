"""Read-only spatial oracle against existing native JSON; no media decode or UE."""
from pathlib import Path
import argparse,hashlib,importlib.util,json
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('spatial_checker_v009',HERE/'verify-guard-art-partial-v009.py')
checker=importlib.util.module_from_spec(spec);spec.loader.exec_module(checker)
def audit(path):
 r=json.loads(path.read_text(encoding='utf-8-sig'));side=r['actual_approach_side'];seen=set();masks={'Ready':0,'AxeWindupEarly':0};witnesses=[]
 for oi,o in enumerate(r['observations']):
  n=o.get('guard_native')
  if not n or o['phase'] not in ['normal_guard_approach_and_cycles','complete']:continue
  for d in o['guard_draws']:
   if int(d['EntityId'])!=int(r['guard_entity']) or int(d['DrawId']) in seen:continue
   seen.add(int(d['DrawId']));s=d['Selection']
   if not d['Drawn'] or s['Facing']!=side or not checker.strict_approach(o['player_ground'],n['ground'],side):continue
   key='Ready' if s['Clip']=='Ready' else 'AxeWindupEarly' if s['Clip']=='AxeWindup' and s['Frame']<=2 else None
   if key:
    masks[key]|=1<<s['Frame'];witnesses.append({'observation':oi,'DrawId':d['DrawId'],'clip':s['Clip'],'frame':s['Frame'],'player':o['player_ground'],'guard':n['ground']})
 return {'source_report':str(path),'source_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'pid':r['process_id'],'old_report_passed':r['passed'],'side':side,'strict_position_masks':masks,'spatial_core_passed':masks=={'Ready':15,'AxeWindupEarly':7},'witness_count':len(witnesses),'witnesses':witnesses,'scope':'Existing strict position core only; does not claim new route or new full checker success.'}
def main():
 p=argparse.ArgumentParser();p.add_argument('--report',required=True);a=p.parse_args();print(json.dumps(audit(Path(a.report).resolve()),ensure_ascii=False))
if __name__=='__main__':main()
