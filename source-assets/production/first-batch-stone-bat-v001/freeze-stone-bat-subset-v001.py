"""Freeze only source candidates actually reviewed; failed wake and near-edge hover remain out."""
from pathlib import Path
import importlib.util,copy,json
from PIL import Image
P=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('record_wrapper',P/'production-record.py');w=importlib.util.module_from_spec(s);s.loader.exec_module(w);r=w.r
ledger=r.read(r.LEDGER);profile=P/'manifests/stone-bat-identity-profile-v001.json';markers=P/'reviews/peck-six-pivot-measurement-v001.json';pivots=r.read(markers)['frames'];actions={};files=[]
for action,number,indices in [('hover',94,[0,1,3,4,5]),('peck',96,list(range(6)))]:
 report=P/f'processed/call{number}-{action}-fixed-canvas-v001/processing-report.json';data=r.read(report);frames=[]
 for play_index,source_index in enumerate(indices):
  frame=copy.deepcopy(data['frames'][source_index]);p=Path(frame['path']);im=Image.open(p);assert r.sha(p)==frame['sha256'] and im.mode=='RGBA' and im.size==(512,512)
  assert im.getchannel('A').getextrema()==(0,255) and not frame['output_edge_touch'] and frame['minimum_output_margin_px']>=8
  assert all(im.getpixel(pt)[3]==0 for pt in[(0,0),(511,0),(0,511),(511,511)])
  copies=r.archive(p,p.relative_to(P),'frozen_stone_bat_source_candidate_not_complete_enemy_or_engine_acceptance');assert all(r.sha(Path(x))==frame['sha256'] for x in copies)
  frame.update(play_index=play_index,source_index=source_index,source_request_number=number,source_body_scale='native512_no_fit_no_resize',body_root_px=[256,280] if action=='hover' else pivots[source_index]['source_pivot_px'],
    root_kind='same_chest_stone_junction_center_manual_source_origin_not_ground_feet',root_uncertainty_source_px=6 if action=='peck' else 4,source_layout_stable_claim=action=='hover',
    image_emitted_damage_events=[],body_or_hurtbox_from_bbox=False,track_kind='full_body_creature',corner_rgba=[list(im.getpixel(pt)) for pt in[(0,0),(511,0),(0,511),(511,511)]])
  if action=='hover':frame.update(phase='hover',start_s=play_index*.12,end_s=(play_index+1)*.12)
  else:
   phase=['windup','windup','active','active','low_recovery','low_recovery'][source_index]
   frame.update(phase=phase,phase_sample_index=source_index%2,phase_sample_count=2)
  frames.append(frame);files.append({'path':str(p),'sha256':frame['sha256']})
 actions[action]={'frames':frames,'frame_count':len(frames),'source_request_number':number,'source_processing_report':str(report),'source_processing_report_sha256':r.sha(report),
  'loop':action=='hover','duration_s':.6 if action=='hover' else 3.15,'runtime_verified':False,'status':'static_motion_candidate_not_full_animation_acceptance'}
actions['low_recovery']={'frame_count':2,'frames':[{'reference_action':'peck','reference_play_index':i,'alias_no_new_PNG':True,'phase_start_s':j*.9,'phase_end_s':(j+1)*.9} for j,i in enumerate([4,5])],
 'duration_s':1.8,'clock':'actual_legal_low_arrival_then_authoritative_LowStarted; blocked_or_hurt_cases_do_not_fake_arrival','loop':False,'hold_last_until_low_obligation_satisfied':True}
actions['rise']={'frame_count':1,'frames':[{'reference_action':'hover','reference_play_index':4,'alias_no_new_PNG':True}],'duration_s':.3,
 'clock':'actual_actor_rise_after_true1.8low; no_world_height_baked_in_source','loop':False}
assert len(files)==len({x['path'] for x in files})==len({x['sha256'] for x in files})==11
provenance=[]
for number in [93,94,96]:
 e=next(x for x in ledger['requests'] if x['request_number']==number)
 for p in [e['tool_original_path'],e['raw_path']]+e['archive_paths']:assert r.sha(Path(p))==e['sha256']
 provenance.append({'request_number':number,'raw_path':e['raw_path'],'raw_sha256':e['sha256'],'tool_original_path':e['tool_original_path'],
  'prompt_path':e['prompt_path'],'prompt_sha256':r.sha(Path(e['prompt_path'])),'references':e['references'],'backend':'image_gen.imagegen','host_fee_usd':None,'external_api_calls':0})
 r.archive(Path(e['prompt_path']),Path(e['prompt_path']).relative_to(P),'frozen_source_prompt_with_actual_native_references')
source=Path('F:/Ourgame/docs/design/enemies-v1/stone-forest.json');bat=next(x for x in r.read(source)['enemies'] if x['id']=='ENM-STN-002');attack=next(x for x in bat['attacks'] if x['id']=='ENM-STN-002-A1');assert [attack[x] for x in['windup_s','active_s','recovery_s']]==[.8,.25,2.1]
manifest={'schema':'frozen-stone-bat-motion-subset-v1','frozen':True,'version':1,'actor_id':'ENM-STN-002','name':'灰翼石蝠','status':'hover_and_peck_source_candidates; complete_enemy_visual_unfulfilled',
 'canvas_px':[512,512],'recommended_trial_display_canvas_px':128,'identity_profile':str(profile),'identity_profile_sha256':r.sha(profile),'actions':actions,
 'runtime_unique_Texture_PNGs_new':11,'logical_play_positions_including_explicit_aliases':14,'actual_new_art_action_frames':{'hover':5,'peck':6},'source_frame_not_imported':{'hover94':[2],'wake95':[0,1,2,3,4,5]},
 'exclusion_reasons':['Hover94source2 left wing margin2px, although complete/no outputedge, excluded conservatively rather than shrink entire creature.',
  'Wake95 obvious head/body scale drift and first-row placement drop; preserved as failed source, no runtime wake/dormant frozen.'],
 'sprite_origin_contract':'perframe source body_root_px maps to actual ActorXYZ projected centre; do not add fake Z from bbox/feet; hero footroot256472 is inapplicable to this flying chest-origin sprite',
 'shadow_contract':'independent groundXY shadow follows actual actorZ; no baked source shadow','depth_sort':'actual groundY only; worldZ visual offset never changes ground depth order',
 'mirror_policy':'canonical_right; one shared mirror for texture and source origin about canvas center; continuous source xleft=512-x; do_not_flip_twice',
 'phase_mapping':{'hover':'real awake high idle;5 sampled wing poses/.60s loop only a presentation candidate',
  'PeckWindup':'peck0/1 by actual windup normalized halves (.8nominal,lock.4 stays authority)',
  'PeckActive':'peck2/3 by actual active normalized halves (.25nominal); actual attackerZ and kernel sweep/gate65 decide damage, sprite does not',
  'SeekingLow':'hold peck4 if appropriate; do not visually snap entity toZ20 or start low clock from art',
  'LowRecovery':'explicit peck4/5 reuse,2×.9 nominal,actual low-obligation clock must govern',
  'Rise':'hover source5 explicit alias, actual .3rise worldZ controls projection'},
 'manual_review':{'hover_all6_and_peck_raw_all6_viewed':True,'peck_pivot_aligned_actual_pixel_assembly_viewed':True,'peck_source_layout_stable':False,
  'peck_actual_source_origin_report':str(markers),'peck_actual_source_origin_report_sha256':r.sha(markers),
  'result':'recognizable_stone_bat_wingbeat_and_fold_thrust_droop_sequence_candidates',
  'limits':['Peck source2→3 whole-image vertical shift44px is openly corrected through measured sprite origins only; original PNGs not changed/scaled.',
   'Chest origin estimate has4to6sourcepx uncertainty; this is not a bone rig or certified stable world contact.',
   'Hover downstroke source3 exists but the omitted intervening near-edge source2 makes loop5coarse; smooth wingbeat unverified.',
   'Wake/dormant/wingattack/hurt/death still lack accepted art; do not map hover/peck to every state and call complete.']},
 'timing_and_rule_source':{'path':str(source),'sha256':r.sha(source),'actor_id':'ENM-STN-002','attack_id':'ENM-STN-002-A1','nominal_phase_s':[.8,.25,2.1],
  'actual_height_cm':{'high':90,'low':20,'body_ground_enable_max':40,'ground_attack_gate_max':65},'low_anchor_s':1.8,'rise_s':.3,'all_read_only_existing_rules':True},
 'provenance_kind':'host_native_original_visual_candidate_not_third_party_CC0','source_provenance':provenance,'host_generation_fee_usd':None,'external_api_calls':0,
 'F_E_source_track_copies_verified':44,'generation_accounting_snapshot':{'ledger':str(r.LEDGER),'requested_count':ledger['requested_count'],'window':ledger['current_window'],'remaining':ledger['remaining_batch_requests']},
 'runtime_verified':False,'full_enemy_actions_complete':False,'full_enemy_complete':False}
q=P/'manifests/import-stone-bat-subset-v001.json';assert not q.exists();r.write(q,manifest);r.archive(q,q.relative_to(P),'frozen_actual11texture_hover5_peck6_candidate_explicit_aliases_and_gaps')
j=P/'reviews/import-stone-bat-subset-v001-verification.json';r.write(j,{'manifest':str(q),'manifest_sha256':r.sha(q),'files':files,'actual_unique_PNGs':11,'F_E_copies_verified':44,'errors':[],'engine_executed':False});r.archive(j,j.relative_to(P),'actual_source_PNG_alpha_hash_retention_gate_not_running_game')
for script in['process-six-state-grid-v001.py','prepare-anchor93-v001.py','review-bat-peck-pivots96-v001.py',Path(__file__).name]:r.archive(P/script,Path('scripts')/script,'frozen_source_preserving_processing_or_manual_anchor_measurement_script')
for number in[94,96]:
 e=next(x for x in ledger['requests'] if x['request_number']==number);e.update(status='stone_bat_subset_candidate_frozen_runtime_unfulfilled',reviewed_utc=r.now(),review_notes='Hover94selected0,1,3,4,5; source2near-edge retained/excluded. Peck96six genuine poses with explicit manual chest origins for native layout drift; no body rescale. Actual11PNG/14logicalrefs including low2+rise1 aliases. Wake95failed and fullBat still unfulfilled.')
ledger.setdefault('derived_deliveries',[]).append({'kind':'stone_bat_hover5_peck6_source_candidate','manifest':str(q),'sha256':r.sha(q),'recorded_utc':r.now(),'actual_unique_PNGs':11,'logical_refs':14,'full_enemy_complete':False})
r.write(r.LEDGER,ledger)
for folder in r.ARCHIVES:r.write(folder/'generation-ledger-snapshot.json',ledger)
print(json.dumps({'manifest':str(q),'sha256':r.sha(q),'unique_PNGs':11,'logical_refs':14,'F_E_copies':44,'requested':ledger['requested_count'],'remaining':ledger['remaining_batch_requests']}))
