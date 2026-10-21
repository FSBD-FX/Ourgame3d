"""Audit the completed native window before opening the already auto-authorized next one."""
from pathlib import Path
import importlib.util,json,collections
from PIL import Image
P=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('record_wrapper',P/'production-record.py');w=importlib.util.module_from_spec(s);s.loader.exec_module(w);r=w.r
ledger=r.read(r.LEDGER);assert ledger['requested_count']==96 and ledger['current_window']['number']==4 and ledger['current_window']['requested_count']==24
entries=[e for e in ledger['requests'] if e.get('window_number')==4];assert [x['request_number'] for x in entries]==list(range(73,97)) and not any(x['status']=='requested' for x in ledger['requests'])
errors=[];source_records=[];reference_count=0
for e in entries:
 paths=[e['tool_original_path'],e['raw_path']]+e['archive_paths'];assert len(paths)==6
 for path in paths:
  p=Path(path)
  if not p.exists() or r.sha(p)!=e['sha256']:errors.append({'kind':'raw_retention_hash','request':e['request_number'],'path':str(p)})
 with Image.open(e['raw_path']) as im:assert list(im.size)==e['image_size'] and im.mode==e['mode']
 assert Path(e['prompt_path']).exists() and Path(e['prompt_path']).read_text('utf-8')==e['prompt']
 for ref in e['references']:
  reference_count+=1;p=Path(ref['path'])
  if not p.exists() or r.sha(p)!=ref['sha256']:errors.append({'kind':'reference_hash','request':e['request_number'],'path':str(p)})
 source_records.append({'request':e['request_number'],'asset':e['asset'],'status':e['status'],'raw_path':e['raw_path'],'raw_sha256':e['sha256'],'raw_size':e['image_size'],'retention_paths_verified':paths,'prompt_path':e['prompt_path'],'prompt_sha256':r.sha(Path(e['prompt_path']))})
assert not errors,errors
root=P.parent;manifests=[root/'first-batch-weapon-components-v001/manifests/import-weapon-components-v001.json',root/'first-batch-weapon-actions-v001/manifests/import-XBW-ready-idle-v001.json',root/'first-batch-weapon-actions-v001/manifests/import-XBW-primary-v001.json',root/'first-batch-weapon-actions-v001/manifests/import-XBW-reload-four-keyposes-v001.json',P/'manifests/import-stone-bat-subset-v001.json']
files=[];manifest_records=[]
for p in manifests:
 j=r.read(p);selected=[]
 if 'weapons' in j:
  selected=[x for key,x in j['weapons'].items() if key!='WPN-SWD-001']
 elif 'frames' in j:
  for frame in j['frames']:
   selected.extend(frame[key] for key in ['body_far','body_support','body_near'])
   if j.get('action')=='reload':selected.append(frame['weapon'])
 else:
  for action in ['hover','peck']:selected.extend(j['actions'][action]['frames'])
 for item in selected:
  q=Path(item['path']);assert r.sha(q)==item['sha256'];im=Image.open(q);assert im.mode=='RGBA' and im.size==(512,512) and im.getchannel('A').getextrema()==(0,255)
  assert all(im.getpixel(pt)[3]==0 for pt in[(0,0),(511,0),(0,511),(511,511)]);files.append({'path':str(q),'sha256':item['sha256']})
 manifest_records.append({'path':str(p),'sha256':r.sha(p),'source_candidate_PNG_path_count':len(selected),'runtime_or_formal_complete_claim':False})
assert len(files)==len({x['path'] for x in files})==67
review={'schema':'native_visual_window_review_v1','window_number':4,'requests':[73,96],'actual_native_calls':24,'lifetime_EV039_plus_followons':96,'EV038_prior_separate':24,'lifetime_all_native':120,
 'completed_utc':r.now(),'single_visual_writer':'/root/assets_prepare','status':'reviewed_closed_sources_retained_not_full15_acceptance','tool_and_F_E_source_paths_checked':144,
 'reference_hashes_checked':reference_count,'source_records':source_records,'frozen_candidate_manifests':manifest_records,'actual_new_frozen_candidate_PNG_paths':67,
 'actual_new_frozen_candidate_unique_content_hashes':len({x['sha256'] for x in files}),'source_candidate_files':files,
 'semantic_boundary':{'props':4,'XBW_ready_idle_body_tracks':18,'XBW_primary_body_tracks':18,'XBW_reload_four_keypose_body_tracks':12,'XBW_reload_weapon_states':4,'StoneBat_hover5_peck6':11,
  'all_candidates_runtime_acceptance':False,'full_armor_weapon20_combinations':False,'formal_units_completed_by_this_audit':0},
 'retained_failures_or_limits':['Hurt armor73..76 are native sources without frozen same-pose surface selection; do not count full new armor clips.',
  'Reload83/84/85 and native90 cable fix not accepted; mechanical86..89 guide sources not independent runtime animations.',
  'Reload91/92 four true keyposes only; .1.10s holds require running contact/cancel/instance-state verification.',
  'StoneBat94source2 margin2px excluded; hover5loop coarse;95wake scale/layout drift rejected.96chest pivots explicitly compensate native placement drift, no perframe rescale.',
  'StoneBat accepted-source subset lacks wake/dormant/wingattack/hurt/death; full Bat not complete.'],
 'next_window_plan':['Pose-first dormant/wake scale-matched correction with actual94head/body guide; no blind full-loop retries.',
  'StoneBat wing attack and real low-recovery/hurt/death sources at consistent scale; actual ActorXYZ drives flight.',
  'Continue weapon-specific absent actions after Bat minimum set; do not expand Armor repeated surface clips first.'],
 'paid_external_API_calls':0,'host_native_fee_usd':None,'pending_generation_calls':0,'errors':errors,'engine_executed_by_writer':False,
 'authorization':'EV039/040/041 automatic same-scope native visual production;24call audit windows, no unlimited blind retries'}
j=P/'reviews/window004-review-and-source-verification-v001.json';assert not j.exists();r.write(j,review);r.archive(j,j.relative_to(P),'completed_window4_24calls144rawpaths_reference_hash_and_candidate_scope_audit')
freeze=r.LEDGER.parent/'generation-ledger-window004-frozen.json';assert not freeze.exists()
ledger['current_window']['status']='reviewed_closed';ledger.setdefault('completed_windows',[]).append({'number':4,'first_request_number':73,'last_request_number':96,'request_limit':24,'requested_count':24,'status':'reviewed_closed','review':str(j),'review_sha256':r.sha(j),'frozen_ledger':str(freeze)})
r.write(freeze,ledger);r.archive(freeze,Path('bookkeeping')/freeze.name,'frozen_window004_ledger_after_actual_QC_before_followon_window')
ledger['completed_windows'][-1]['frozen_ledger_sha256']=r.sha(freeze)
ledger['current_window']={'number':5,'first_request_number':97,'last_request_number':120,'request_limit':24,'requested_count':0,'status':'active_auto_authorized_after_window004_review'}
ledger['batch_requested_count']=0;ledger['remaining_batch_requests']=24;ledger['phase']='window005_stone_bat_missing_actions_pose_first_then_weapon_specific_actions'
r.write(r.LEDGER,ledger)
for folder in r.ARCHIVES:r.write(folder/'generation-ledger-snapshot.json',ledger)
print(json.dumps({'review':str(j),'review_sha256':r.sha(j),'frozen_ledger':str(freeze),'frozen_ledger_sha256':r.sha(freeze),'raw_paths_verified':144,'references_verified':reference_count,'new_candidate_PNG_paths':67,'candidate_unique_content_hashes':review['actual_new_frozen_candidate_unique_content_hashes'],'requested':96,'window5_used':0,'window5_remaining':24}))
