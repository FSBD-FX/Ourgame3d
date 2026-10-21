"""Freeze honest walking body candidates and state socket matrices, source-only."""
from pathlib import Path
import importlib.util,ast
from PIL import Image
P=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('rec',P/'production-record.py');w=importlib.util.module_from_spec(s);s.loader.exec_module(w);r=w.r
q=P/'manifests/XBW-common-walk-candidate-v002.json';d=r.read(q);hashes=set()
for f in d['frames']:
 for key in ['body_far','body_support','body_near']:
  x=f[key];src=Path(x['path']);assert r.sha(src)==x['sha256'];Image.open(src).verify();im=Image.open(src).convert('RGBA');assert im.size==(512,512) and im.getchannel('A').getextrema()==(0,255)
  assert all(im.getpixel(p)[3]==0 for p in[(0,0),(511,0),(0,511),(511,511)])
  assert not any(px[3] and px[0]>px[1]+30 and px[2]>px[1]+30 for px in im.get_flattened_data());hashes.add(x['sha256'])
  x.update(corner_alpha=[0,0,0,0],actual_PNG_verified=True)
 f['time_start_s']=round(f['time_start_s'],6);f['time_end_s']=round(f['time_end_s'],6)
 f['weapon_visible']=True
assert len(hashes)==18
ledger=r.read(r.LEDGER);e=next(x for x in ledger['requests'] if x['request_number']==117)
for p in [e['tool_original_path'],e['raw_path']]+e['archive_paths']:assert r.sha(Path(p))==e['sha256']
d.update(schema='frozen-XBW-walk-three-body-track-subset-v1',version=1,frozen=True,status='candidate_alternating_legs_and_two_hand_carry_pending_runtime_contact_review',weapon_id='WPN-XBW-001',clip='walk',source_candidate_path=str(q),source_candidate_sha256=r.sha(q),manual_assembly_review_passed=True,mirror_policy='single_parent_horizontal_flip_of_body_weapon_and_all_sockets',phase_intervals_s=[{'phase':'walk','start_s':0,'end_s':.6}],source_generation_calls=2,source_requests=[116,117],failed_request_116_retained=True,body_texture_count_new=18,body_source_pose_count=6,gameplay_move_speed_changed=False,source_provenance={'request_number':117,'raw_path':e['raw_path'],'raw_sha256':e['sha256'],'tool_original_path':e['tool_original_path'],'tool_original_sha256':e['sha256'],'prompt_path':e['prompt_path'],'prompt_sha256':r.sha(Path(e['prompt_path'])),'references':e['references']},limitations=['All six bodies originate from native request117, never modified Sword arm bitmaps; anatomy was processed only by one .94 shared scale, rigid per-frame sole/proxy translation, and deterministic magenta cleanup. Native source retained.','Frames1 and4 (zero-based) have extended-stride toe/contact proxies, not demonstrated flat support soles. Root256472 is nominal; no footlock/no-slip or body-bob acceptance.','Fists are manually measured source-image contact centers with3nativepx uncertainty, not skeleton joints. Existing state0/3 scale.48 preserved; maximum support residual2.113614px is below prior lifecycle maximum3.129px. No arm stretch or threshold relaxation.','VirtualEmit is an image-space rail socket, not a visible loaded arrow tip, not CombatHeight/ActorZ. Producer and renderer must select the same component state and matrix; actual ammo/lifecycle remains kernel-owned.','Brown underclothes remain composite; separate four-armor garment surfaces are not part of this body-only subset.','Static both-direction assembly review does not certify runtime pose selection,20equipment combinations,walk contact or weapon actions.'],runtime_verified=False,footlock_certified=False,full_weapon_actions_complete=False)
out=P/'manifests/import-XBW-common-walk-v001.json';assert not out.exists();r.write(out,d);r.archive(out,out.relative_to(P),'frozen_true_XBW_carry_walk_body_candidate_not_runtime_footlock')
plate=Image.new('RGBA',(1536,1024),(255,0,255,255))
for f in d['frames']:plate.alpha_composite(Image.open(f['source_body_path']).convert('RGBA'),((f['index']%3)*512,(f['index']//3)*512))
ref=P/'references/frozen-XBW-common-walk-pose-plate-v001.png';plate.save(ref);r.archive(ref,ref.relative_to(P),'exact_frozen_new_XBW_walk_pose_reference_for_garment_edit')
ledger.setdefault('derived_deliveries',[]).append({'kind':'XBW_common_walk_body_candidate','manifest':str(out),'sha256':r.sha(out),'actual_body_PNGs':18,'source_poses':6,'new_native_calls':2,'recorded_utc':r.now(),'runtime_verified':False,'footlock_certified':False})
e.update(status='XBW_common_walk_source_candidate_frozen_runtime_unfulfilled',review_notes='True opposite leg halfcycles and two-hand carrying candidate; shared0.94+rigid contact/proxy alignment,18real body tracks, state0/3 fixed.48 residualmax2.113614. Footlock unaccepted.');r.write(r.LEDGER,ledger)
for a in r.ARCHIVES:r.write(a/'generation-ledger-snapshot.json',ledger)
for f in P.glob('*.py'):ast.parse(f.read_text('utf-8'));r.archive(f,Path('scripts')/f.name,'actual_source_processing_provenance')
for f in (P/'prompts').glob('*.txt'):r.archive(f,f.relative_to(P),'handwritten_native_prompt')
print({'manifest':str(out),'sha256':r.sha(out),'body_PNGs':18,'max_support_error':d['max_support_alignment_error_px'],'ledger':ledger['requested_count']})
