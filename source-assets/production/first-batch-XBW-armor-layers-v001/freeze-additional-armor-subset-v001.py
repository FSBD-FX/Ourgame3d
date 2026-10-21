"""Freeze only the reviewed reload/ready source overlays; no engine work or image creation."""
from pathlib import Path
import argparse,ast,importlib.util,json
from PIL import Image,ImageChops
P=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('record',P/'production-record.py');w=importlib.util.module_from_spec(s);s.loader.exec_module(w);r=w.r
def main(clip):
 config={'reload':('XBW-reload-four-armors-selection-candidate-v004.json',4,[108,109,110,111],2),'ready_idle':('XBW-ready_idle-four-armors-selection-candidate-v001.json',6,[112,113,114,115],1)}
 filename,count,numbers,process_revision=config[clip];source=P/'manifests'/filename;c=r.read(source);bp=Path(c['source_body_contract_path']);assert r.sha(bp)==c['source_body_contract_sha256'];body=r.read(bp)
 assert c['frame_count']==count and set(c['armors'])=={'ARM-LGT-001','ARM-MED-001','ARM-HVY-001','ARM-ROB-001'}
 hashes=set();copies=0
 for key,rows in c['armors'].items():
  assert [x['index'] for x in rows]==list(range(count))
  for f in rows:
   native=Image.open(f['source_path']).convert('RGBA');assert r.sha(Path(f['source_path']))==f['source_sha256']
   protected=Image.open(f['selection_masks']['protected']['path']).convert('L')
   for layer in ['armor_far','armor_near']:
    q=Path(f[layer]['path']);im=Image.open(q).convert('RGBA');assert r.sha(q)==f[layer]['sha256'];assert im.size==(512,512) and im.getchannel('A').getbbox() and im.getchannel('A').getextrema()==(0,255)
    assert all(im.getpixel(p)[3]==0 for p in[(0,0),(511,0),(0,511),(511,511)])
    assert not ImageChops.multiply(im.getchannel('A'),protected).getbbox()
    assert all(a==b for a,b in zip(im.get_flattened_data(),native.get_flattened_data()) if a[3])
    assert not any(a[3] and a[0]>a[1]+30 and a[2]>a[1]+30 for a in im.get_flattened_data())
    hashes.add(f[layer]['sha256']);outputs=r.archive(q,q.relative_to(P),'frozen_actual_XBW_costume_overlay_candidate_not_full_armor_acceptance');copies+=len(outputs)
   for mask in f['selection_masks'].values():assert r.sha(Path(mask['path']))==mask['sha256']
   assert f['root_px']==[256,472]
   frozen=body['frames'][f['index']]
   assert f['support_grip_px']==frozen['body_support_contact_px' if clip=='reload' else 'support_grip_px']
   assert f['primary_grip_px']==frozen['primary_stock_grip_px' if clip=='reload' else 'primary_grip_px']
   f.update(frozen=True,static_source_layer_candidate_reviewed=True,complete_armor=False,semantic_review_passed=False,runtime_verified=False)
 previews=c.get('previews',[])
 if not previews:
  for key in c['armors']:
   for kind in ['native_selected','assembled_right','assembled_left']:
    q=P/f'reviews/XBW-{clip}-{key}-{kind}-selection-v001.png';previews.append({'armor_id':key,'kind':kind,'path':str(q),'sha256':r.sha(q)})
 for p in previews:assert r.sha(Path(p['path']))==p['sha256']
 ledger=r.read(r.LEDGER);provenance=[]
 for n in numbers:
  e=next(x for x in ledger['requests'] if x['request_number']==n)
  for q in [e['tool_original_path'],e['raw_path']]+e['archive_paths']:assert r.sha(Path(q))==e['sha256']
  report=P/f'processed/call{n}-fixed-canvas-v{process_revision:03}/processing-report.json';assert report.exists()
  provenance.append({'request_number':n,'raw_path':e['raw_path'],'raw_sha256':e['sha256'],'tool_original_path':e['tool_original_path'],'tool_original_sha256':e['sha256'],'prompt_path':e['prompt_path'],'prompt_sha256':r.sha(Path(e['prompt_path'])),'references':e['references'],'processing_report_path':str(report),'processing_report_sha256':r.sha(report)})
  e.update(status=f'XBW_{clip}_four_armor_source_candidate_frozen_runtime_unfulfilled',reviewed_utc=r.now(),review_notes='Native material-only source selections; both directions and isolation reviewed; original head/hands preserved. Underclothes/cuff/shoulder boundaries remain partial, runtime/fullarmor not accepted.')
 assert copies==4*count*2*4 and len(hashes)==4*count*2
 manifest={'schema':'frozen-XBW-pose-armor-layer-subset-v1','version':1,'frozen':True,'status':'four_armor_static_layer_candidates_pending_runtime_and_coverage_acceptance','weapon_id':'WPN-XBW-001','clip':clip,'frame_count':count,'canvas_px':[512,512],
  'source_body_contract_path':str(bp),'source_body_contract_sha256':r.sha(bp),'common_body':body['frames'],'armors':c['armors'],'draw_order':['body_far','armor_far','independent_weapon','body_support','armor_near','body_near'],'required_armor_tracks':['armor_far','armor_near'],
  'missing_layer_policy':'disable_variant_with_explicit_diagnostic_never_stretch_Sword_fallback','root_px':[256,472],'body_track_authority':'exact_frozen_XBW_body_far_support_near_originals','body_geometry_transform':'none','armor_per_frame_geometry_transform':'none','mirror_policy':'one_parent_horizontal_flip_for_body_armor_weapon_and_sockets',
  'duration_s':body['duration_s'],'phase_intervals_s':body.get('phase_intervals_s',[]),'loop':body['loop'],'source_pose_time_authority':'actor_actual_effective_elapsed_remaps_existing_clip_fractions_no_image_commits','armor_texture_count_new':4*count*2,'common_body_texture_count_reused':count*3,'armor_pose_combinations':4*count,'source_generation_calls':4,'source_requests':numbers,
  'selection_candidate_path':str(source),'selection_candidate_sha256':r.sha(source),'source_provenance':provenance,'previews':previews,
  'pixel_checks':{'actual_RGBA512':True,'transparent_corners':True,'source_pixels_only':True,'no_magenta_selected':True,'protected_original_anatomy_excluded':True,'F_E_armor_texture_copies_verified':copies},
  'manual_review':{'reviewer':'/root/assets_prepare','reviewed_all_pose_combinations_both_directions':True,'static_assembly_candidate':True,'full_coverage_accepted':False,'runtime_verified':False},
  'generation_accounting_snapshot':{'ledger_path':str(r.LEDGER),'requested_count':ledger['requested_count'],'window':ledger['current_window'],'remaining':ledger['remaining_batch_requests'],'task_max_requests':12,'task_used_requests':ledger['requested_count']-103},
  'limitations':['Frozen composite common body contains original brown underclothes; visible old collar/waist/slit cloth and some shoulder/cuff wedges remain, not a naked-body production.',
   'Original anatomy safety masks intentionally retain bare forearms for short-sleeved LGT/MED/HVY; ROB uses actual native long cloth sleeve selections, not that short-sleeve exclusion. A completely sealed ROB cuff transition remains unaccepted.',
   'Source back surface only where actually visible in far layer; hidden back null. This is not four fabricated full-body or hidden layers.',
   'Reload raw1254square is explicitly one whole-grid uniform1024/1254 normalization; no independent frame/body/armor bboxfit,translation or stretch. Native raw remains preserved.',
   'Source alpha/material/hash review does not certify running cloak/weapon contact,clip continuity,20 combinations,ammo events or producer worldEmit Height. All gameplay authority remains Actor/kernel.'],
  'semantic_full_armor_acceptance':False,'runtime_verified':False,'full_equipment_combinations_complete':False}
 q=P/f'manifests/import-XBW-{clip}-four-armors-v001.json';assert not q.exists();r.write(q,manifest);r.archive(q,q.relative_to(P),'frozen_XBW_additional_armor_layer_source_candidates_honest_partial_boundaries')
 ledger.setdefault('derived_deliveries',[]).append({'kind':f'XBW_{clip}_four_armors_candidate','manifest':str(q),'sha256':r.sha(q),'actual_armor_pngs':4*count*2,'body_pngs_reused':count*3,'new_native_calls':4,'recorded_utc':r.now(),'runtime_verified':False});r.write(r.LEDGER,ledger)
 for archive in r.ARCHIVES:r.write(archive/'generation-ledger-snapshot.json',ledger)
 for f in P.glob('*.py'):ast.parse(f.read_text('utf-8'));r.archive(f,Path('scripts')/f.name,'actual_source_selection_provenance_script')
 for f in (P/'prompts').glob('*.txt'):r.archive(f,f.relative_to(P),'handwritten_native_prompt')
 print(json.dumps({'manifest':str(q),'sha256':r.sha(q),'armor_pngs':4*count*2,'reused_body_pngs':count*3,'F_E_layer_copies':copies,'ledger':ledger['requested_count'],'runtime_verified':False}))
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--clip',choices=['reload','ready_idle'],required=True);v=a.parse_args();main(v.clip)
