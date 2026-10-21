"""Add bounded source candidates and refine measured origins; immutable v001 retained."""
from pathlib import Path
import importlib.util,copy,json
from PIL import Image,ImageDraw
P=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('record_wrapper',P/'production-record.py');w=importlib.util.module_from_spec(s);s.loader.exec_module(w);r=w.r
old=P/'manifests/import-stone-bat-subset-v001.json';assert r.sha(old)=='38dc4d88880b49239e5ae0416e4e98216009362777763b27932994c8dd6dc89b'
manifest=copy.deepcopy(r.read(old));ledger=r.read(r.LEDGER);assert ledger['requested_count']==101 and ledger['current_window']['number']==5 and ledger['current_window']['requested_count']==5
actions=manifest['actions'];new_files=[]
def real_frame(item,number,index,root,uncertainty=4):
 frame=copy.deepcopy(item);p=Path(frame['path']);im=Image.open(p);assert r.sha(p)==frame['sha256'] and im.mode=='RGBA' and im.size==(512,512)
 assert im.getchannel('A').getextrema()==(0,255) and all(im.getpixel(pt)[3]==0 for pt in[(0,0),(511,0),(0,511),(511,511)])
 bbox=im.getchannel('A').getbbox();assert min(bbox[0],bbox[1],512-bbox[2],512-bbox[3])>=8
 frame.update(source_request_number=number,source_index=index,body_root_px=root,root_kind='visible_gold_chest_Yfork_plus8x9; fragments_use_fixed_fracture_origin',
  root_uncertainty_source_px=uncertainty,canvas_px=[512,512],mode='RGBA',track_kind='full_body_creature',corner_rgba=[list(im.getpixel(pt)) for pt in[(0,0),(511,0),(0,511),(511,511)]],
  image_emitted_damage_events=[],body_or_hurtbox_from_bbox=False,source_body_scale='native_wholecell_only_no_fit_or_perframe_zoom',source_pixels_modified_for_origin=False)
 return frame
# The hover reference's visible gold Yfork is approximately248271; existing centre256280 is +8,+9.
peck_roots=[[256,283],[252,296],[292,307],[291,254],[253,254],[247,255]]
old_peck_roots=[x['body_root_px'] for x in actions['peck']['frames']]
for i,frame in enumerate(actions['peck']['frames']):
 frame['body_root_px']=peck_roots[i];frame['root_uncertainty_source_px']=4;frame['root_erratum_v001_prior_estimate_px']=old_peck_roots[i]
 frame['root_kind']='same_visible_gold_chest_Yfork_plus8x9_offset_from_hover_reference; manually_refined_from_actual20px_coordinate_crop'
origin_rows=[{'action':'peck','source_index':i,'source_pivot_px':pivot,'previous_v001_pivot_px':old_peck_roots[i],'uncertainty_px':4} for i,pivot in enumerate(peck_roots)]
for number,action in[(97,'dormant'),(98,'wake-quarter')]:
 report=P/f'processed/call{number}-{action}-single-v001/processing-report.json';item=r.read(report);frame=real_frame(item,number,0,[259,279]);frame['play_index']=0;new_files.append({'path':frame['path'],'sha256':frame['sha256']})
 if number==97:actions['dormant']={'frames':[frame],'frame_count':1,'loop':True,'duration_s':None,'status':'one_static_dormant_keypose_candidate_not_loop_motion','runtime_verified':False}
 else:wakequarter=frame
actions['wake']={'frames':[{'reference_action':'dormant','reference_play_index':0,'alias_no_new_PNG':True,'start_s':0,'end_s':.2},dict(wakequarter,play_index=1,start_s=.2,end_s=.4),
  {'reference_action':'hover','reference_play_index':1,'alias_no_new_PNG':True,'start_s':.4,'end_s':.6},{'reference_action':'hover','reference_play_index':0,'alias_no_new_PNG':True,'start_s':.6,'end_s':.8}],
 'frame_count':4,'loop':False,'duration_s':.8,'temporal_sampling':'four_curated_real_keyposes_from97_98_and_two_existing_hover94frames_not_four_native_continuous_samples',
 'clock':'authoritative_existing_complete_wake_clock; no attack_before_complete; image_not_HP_or_wake_authority','runtime_verified':False,'status':'coarse_wake4_candidate'}
for action,number,folder,indices,roots,uncertainties in[
 ('wing',99,'call99-wing-fixed-canvas-v001',list(range(6)),[[263,309],[261,309],[292,311],[266,254],[261,254],[261,254]],[4,4,12,4,4,4]),
 ('hurt',100,'call100-hurt-four-v001',list(range(4)),[[300,295],[260,324],[302,273],[280,273]],[4]*4),
 ('death',101,'call101-death-fixed-canvas-v001',[0,3,4,5],[[260,291],[256,280],[256,280],[256,280]],[6,12,12,12])]:
 report=P/f'processed/{folder}/processing-report.json';data=r.read(report);frames=[]
 for play,idx in enumerate(indices):
  frame=real_frame(data['frames'][idx],number,idx,roots[play],uncertainties[play]);frame['play_index']=play
  frame['phase']=['windup','windup','active','active','low_recovery','low_recovery'][play] if action=='wing' else action
  if action=='wing':frame.update(phase_sample_index=play%2,phase_sample_count=2,source_layout_stable_claim=False)
  if action=='hurt':frame.update(start_s=play*.1,end_s=(play+1)*.1,only_actual_poise_break=True)
  if action=='death':frame.update(start_s=play*.15,end_s=(play+1)*.15,fracture_pose_aware=True,anatomical_pivot_available=play==0)
  frames.append(frame);new_files.append({'path':frame['path'],'sha256':frame['sha256']});origin_rows.append({'action':action,'source_index':idx,'source_pivot_px':roots[play],'uncertainty_px':uncertainties[play],
   'measurement':'same_gold_Yfork_plus8x9' if action!='death' else 'initial_chest_then_fixed_fracture_center_not_live_bone'})
 actions[action]={'frames':frames,'frame_count':len(frames),'loop':False,'duration_s':3.1 if action=='wing' else .4 if action=='hurt' else .6,
  'source_request_number':number,'source_processing_report':str(report),'source_processing_report_sha256':r.sha(report),'runtime_verified':False,
  'status':'static_action_source_candidate_not_timing_shape_or_running_acceptance'}
actions['low_recovery_wing']={'frames':[{'reference_action':'wing','reference_play_index':i,'alias_no_new_PNG':True,'phase_start_s':j*.9,'phase_end_s':(j+1)*.9} for j,i in enumerate([4,5])],
 'frame_count':2,'duration_s':1.8,'loop':False,'clock':'actual_LowStarted_after_active_end_and_legal_Z20_arrival; no_hurt_or_collision_shortcut'}
def resolve(frame):return resolve(actions[frame['reference_action']]['frames'][frame['reference_play_index']]) if 'reference_action' in frame else frame
all_files={}
for action in actions.values():
 for frame in action['frames']:
  f=resolve(frame);all_files[f['path']]=f
assert len(all_files)==27 and len(new_files)==16 and len({x['sha256'] for x in all_files.values()})==27
for f in all_files.values():
 p=Path(f['path']);assert r.sha(p)==f['sha256'];copies=r.archive(p,p.relative_to(P),'frozen_extended_stone_bat_candidate27_sources_no_formal_acceptance');assert all(r.sha(Path(x))==f['sha256'] for x in copies)
origins=P/'reviews/stone-bat-origins-v002.json';assert not origins.exists();r.write(origins,{'schema':'stone_bat_manual_source_origins_v2','reference_hover_source0_gold_Yfork_px':[248,271],'reference_body_origin_px':[256,280],'uniform_offset_px':[8,9],
 'rows':origin_rows,'source_pixels_changed':False,'source_scale_changed':False,'old_manifest_preserved':str(old),'old_manifest_sha256':r.sha(old),
 'errata':['v001Peck centre estimates were not all tied to exactly the same visible Yfork. Corrected measured origins in v002 only; old PNGs and manifest untouched.',
  'v00144px active source-drop description was an initial estimate; refined same-anatomical-point measurements vary by53px vertically between peck2/3. This does not assert that every pixel is a rigid53px translation.',
  'Wing active2 Yfork is occluded by the real near-wing; its origin is inferred with12px uncertainty, not visible pixel certification.'],
 'coordinate_crop_sources':[{'path':str(p),'sha256':r.sha(p)} for p in[P/'reviews/anchor-dormant-quarterwake-chest-grid-v001.png',P/'reviews/peck-actual-chest-coordinate-grids-v002.png',P/'reviews/wing-actual-chest-coordinate-grids-v001.png',P/'reviews/hurt-actual-chest-coordinate-grids-v001.png']],
 'runtime_verified':False});r.archive(origins,origins.relative_to(P),'explicit_origin_measurement_refinement_and_v001_errata_without_source_overwrite')
previews=[]
for action_name in['wake','wing','hurt','death','peck']:
 rows=actions[action_name]['frames'];cols=3 if len(rows)>4 else 2;sheet=Image.new('RGBA',(cols*512,2*512))
 for i,ref in enumerate(rows):
  f=resolve(ref);im=Image.open(f['path']).convert('RGBA');root=f['body_root_px'];display=Image.new('RGBA',(512,512));display.alpha_composite(im,(256-root[0],280-root[1]));assert all(display.getpixel(pt)[3]==0 for pt in[(0,0),(511,0),(0,511),(511,511)])
  sheet.alpha_composite(display,(i%cols*512,i//cols*512))
 for facing,im in[('right',sheet),('left',sheet.transpose(Image.Transpose.FLIP_LEFT_RIGHT))]:
  q=P/f'reviews/{action_name}-origin-assembled-{facing}-v002.png';assert not q.exists();im.save(q);r.archive(q,q.relative_to(P),'actual_source_origin_assembly_diagnostic_not_runtime_video_or_new_art');previews.append({'action':action_name,'facing':facing,'path':str(q),'sha256':r.sha(q)})
for number in[97,98,99,100,101]:
 e=next(x for x in ledger['requests'] if x['request_number']==number)
 for p in[e['tool_original_path'],e['raw_path']]+e['archive_paths']:assert r.sha(Path(p))==e['sha256']
 manifest['source_provenance'].append({'request_number':number,'raw_path':e['raw_path'],'raw_sha256':e['sha256'],'tool_original_path':e['tool_original_path'],
  'prompt_path':e['prompt_path'],'prompt_sha256':r.sha(Path(e['prompt_path'])),'references':e['references'],'backend':'image_gen.imagegen','host_fee_usd':None,'external_api_calls':0})
 r.archive(Path(e['prompt_path']),Path(e['prompt_path']).relative_to(P),'frozen_extended_bat_source_prompt')
manifest.update(schema='frozen-stone-bat-motion-subset-v2',version=2,status='nine_semantic_states_have_source_candidates; quality_rules_audio_and_runtime_unfulfilled',
 runtime_unique_Texture_PNGs_new=27,runtime_unique_Texture_PNGs_added_after_v001=16,logical_play_positions_including_explicit_aliases=sum(len(x['frames']) for x in actions.values()),
 semantic_state_count=9,context_specific_clip_count=10,actual_new_art_action_frames={'hover':5,'peck':6,'dormant':1,'wake_quarter':1,'wing':6,'hurt':4,'death':4},
 previous_frozen_manifest={'path':str(old),'sha256':r.sha(old),'unchanged':True},origin_measurement_report=str(origins),origin_measurement_report_sha256=r.sha(origins),
 F_E_source_track_copies_verified=108,generation_accounting_snapshot={'ledger':str(r.LEDGER),'requested_count':ledger['requested_count'],'window':ledger['current_window'],'remaining':ledger['remaining_batch_requests']})
manifest['source_frame_not_imported']['death101']=[1,2]
manifest['exclusion_reasons'].append('Death101source1/2 have output-edge components from the raw grid; excluded intact, no largest-component deletion or hidden repair. Death0/3/4/5 only4curatedsamples.')
manifest['phase_mapping'].update(Dormant='real dormant state only, singleclosed-wing97; damageability remains authority',Wake='actual.80wake sampled as4curatedkeyposes; only two newsourcePNG, other2explicithoverreuse',
 WingWindup='wing0/1 actual.80 windup normalized halves; actual50percentlock remains authority',WingActive='wing2/3 actual.20 active normalized halves; one hit is authority, not frame count',
 WingLowRecovery='wing4/5 explicitcontextalias, real1.80low clock then.30rise',Hurt='hurt0..3 only real.40poise-break clock; ordinaryHP loss does not force stun and pendingLow obligation survives',
 Death='fourcuratedactualshatterstates only after realdeath; .60s proposedcosmeticduration; no collider/loot/reward/physicalworldgravity from pixels')
manifest['manual_review']['v002_origin_assembly_previews']=previews
manifest['manual_review']['v002_quality_limits']=['Wake is a four-keypose curated sequence, not six continuous native samples; smoothjoint/eye onset requires realrunning review.',
 'Wing head scale stays roughly consistent but low leg/claw extent after chest alignment is about20sourcepx farther down than originalhover. It may be pose extension; same-body anatomy/scale is not certified.',
 'Hurt pose rotates torso/neck and changes claw extent; no standing-humanoid bbox gate or perframe rescale used. Running head/body proportions still unaccepted.',
 'Some death headstone samples retain an amber eye before the final headless chunks; clear brokenbody but eye-off timing still needs artreview. No alive/dead state inferred from glow.',
 'Death fragments use a fixed estimated fracture origin after the anatomical chest is gone; they are cosmetic only, no actual debris collision/fall proof.',
 'Currentsourcecoverage is not fullenemycompletion, 20equipmentvisuals, worldorigin/audio/AIor saveacceptance.']
manifest['candidate_source_semantics_missing']=[];manifest['full_enemy_actions_complete']=False;manifest['full_enemy_complete']=False;manifest['runtime_verified']=False
q=P/'manifests/import-stone-bat-subset-v002.json';assert not q.exists();r.write(q,manifest);r.archive(q,q.relative_to(P),'extended_frozen27sourcePNG35logicalrefs_bat_candidate_quality_and_runtime_unfulfilled')
audit=P/'reviews/import-stone-bat-subset-v002-verification.json';r.write(audit,{'manifest':str(q),'manifest_sha256':r.sha(q),'actual_unique_PNGs':27,'delta_new_PNGs':16,'F_E_copies_verified':108,
 'files':[{'path':x,'sha256':y['sha256']} for x,y in all_files.items()],'old_frozen_manifest_unchanged':r.sha(old),'errors':[],'engine_executed':False});r.archive(audit,audit.relative_to(P),'actual_extended_bat_candidate_source_hash_alpha_and_retention_gate')
for number in[97,98,99,100,101]:
 e=next(x for x in ledger['requests'] if x['request_number']==number);e.update(status='stone_bat_extended_source_candidate_frozen_runtime_unfulfilled',reviewed_utc=r.now(),
  review_notes='Extendedv002 retains honest27uniquePNG/35logicalrefs. Dormant97 andquarter98 are true2newkeyposes; Wing99six/Hurt100four source candidates; Death101only0,3,4,5 selected, edge1/2retainedexcluded. Numericchestoriginmanualv2, no sourcepixel edits/scales. Wingclawextent/Deathlateeye/staticvsruntime limits explicit.')
ledger.setdefault('derived_deliveries',[]).append({'kind':'stone_bat_extended9state_source_candidate','manifest':str(q),'sha256':r.sha(q),'recorded_utc':r.now(),'actual_unique_PNGs_total':27,'delta_new_PNGs':16,'logical_refs':35,'full_enemy_complete':False})
r.write(r.LEDGER,ledger)
for folder in r.ARCHIVES:r.write(folder/'generation-ledger-snapshot.json',ledger)
print(json.dumps({'manifest':str(q),'sha256':r.sha(q),'actual_unique_PNGs':27,'new_after_v001':16,'logical_refs':manifest['logical_play_positions_including_explicit_aliases'],'origin_report':str(origins),'origin_report_sha256':r.sha(origins),'requested':ledger['requested_count'],'remaining':ledger['remaining_batch_requests']}))
