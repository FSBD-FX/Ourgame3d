"""Freeze manually reviewed existing weapon states/sockets; no new art or gameplay authority."""
from pathlib import Path
import importlib.util,math,json
from PIL import Image
P=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('record',P/'production-record.py');r=importlib.util.module_from_spec(s);s.loader.exec_module(r)
def main():
 path=P/'manifests/import-XBW-reload-four-keyposes-v001.json';assert r.sha(path)=='9a0f99a5b32a5b898b9fa98d4b40812daf5e532a73954f13df91a7c166297ee8';reload=r.read(path)
 states=[]
 for i,f in enumerate(reload['frames']):
  p=Path(f['weapon']['path']);assert r.sha(p)==f['weapon']['sha256'];im=Image.open(p).convert('RGBA');stock=[138,308 if i<2 else 274];support=f['component_support_grip_px'];emit=f['component_emit_px']
  assert im.size==(512,512) and im.getpixel(tuple(stock))[3]==im.getpixel(tuple(support))[3]==255
  assert [support[j]-stock[j] for j in range(2)]==[206,12]
  visible_edge=[507 if i==0 else 505 if i==2 else 504,emit[1]];assert im.getpixel(tuple(visible_edge))[3]>=128
  diag=P/f'reviews/XBW-weapon-state-{i}-stock-support-virtual-emit-v001.png';assert diag.exists()
  states.append({'state_index':i,'visual_state':['empty_relaxed_string','drawn_no_bolt','placing_bolt','loaded_seated_bolt'][i],
   'path':str(p),'sha256':r.sha(p),'canvas_px':[512,512],'stock_grip_px':stock,'stock_grip_rgba':list(im.getpixel(tuple(stock))),
   'stock_grip_measurement':'manual_visible_leather_grip_contact_center; 4sourcepx_uncertainty_not_skeletal_joint',
   'support_grip_px':support,'support_grip_rgba':list(im.getpixel(tuple(support))),'support_grip_measurement':'inherited_manual_visible_underbarrel_handle; 4sourcepx_uncertainty',
   'emit_px':emit,'emit_kind':'inherited_virtual_rail_exit_not_required_to_be_opaque_not_loaded_arrow_tip','emit_rgba':list(im.getpixel(tuple(emit))),
   'visible_front_rail_edge_px':visible_edge,'visible_front_rail_edge_rgba':list(im.getpixel(tuple(visible_edge))),
   'visible_front_rail_edge_uncertainty_source_px':3,'visible_bolt_tip_px':None if i<2 else [506,172] if i==2 else [483,205],
   'bolt_tip_measurement':'manual_visible_tip_estimate_3sourcepx_uncertainty; placement_state2_not_seated' if i>=2 else 'not_present',
   'shared_stock_anchor_px':[138,274],'native_canvas_offset_from_shared_anchor_px':[0,34 if i<2 else 0],
   'shared_offset_kind':'socket-coordinate_equivalence_not_byte_identical_native_art_translation',
   'stock_to_support_px':[206,12],'stock_to_emit_px':[368,-45],
   'reload_frame_index':i,'reload_frozen_component_to_body_affine_2x3':f['component_to_body_affine_2x3'],
   'reload_stock_in_body_px':[sum(f['component_to_body_affine_2x3'][j][k]*stock[k] for k in range(2))+f['component_to_body_affine_2x3'][j][2] for j in range(2)],
   'reload_stock_contact_certification':'only_frame3_is_handheld_primary_stock; frames0to2_near_hand_manipulates_elsewhere',
   'diagnostic_path':str(diag),'diagnostic_sha256':r.sha(diag),'runtime_verified':False})
 poses=[];contracts=[]
 for action,digest in [('ready-idle','21c8ff90c59c411bfdbcabcfee0292881d77e4e652cc2fde46cab35e99373813'),('primary','79fd2508eabfdab26f4dcb1cc21682d08b2518d37bbc0111fc38655869eeb11f')]:
  q=P/f'manifests/import-XBW-{action}-v001.json';assert r.sha(q)==digest;d=r.read(q);contracts.append({'path':str(q),'sha256':digest})
  for f in d['frames']:
   g=f['primary_grip_px'];h=f['support_grip_px'];angle=math.atan2(h[1]-g[1],h[0]-g[0])-math.atan2(12,206);co=math.cos(angle);si=math.sin(angle);scale=.48;maps=[]
   for state in states:
    stock=state['stock_grip_px'];tx=g[0]-scale*(co*stock[0]-si*stock[1]);ty=g[1]-scale*(si*stock[0]+co*stock[1]);m=[[scale*co,-scale*si,tx],[scale*si,scale*co,ty]]
    def point(p):return [m[j][0]*p[0]+m[j][1]*p[1]+m[j][2] for j in range(2)]
    actual=point(state['support_grip_px']);emit=point(state['emit_px']);error=math.dist(actual,h);assert math.dist(point(stock),g)<1e-9
    maps.append({'state_index':state['state_index'],'component_to_body_affine_2x3':m,'actual_stock_grip_body_px':point(stock),'actual_support_body_px':actual,'support_alignment_error_body_source_px':error,'virtual_emit_body_px':emit})
   assert max(math.dist(maps[0]['virtual_emit_body_px'],x['virtual_emit_body_px']) for x in maps)<1e-9
   poses.append({'action':action,'frame_index':f['index'],'root_px':f['ground_root_px'],'body_primary_grip_px':g,'body_support_grip_px':h,'fixed_weapon_uniform_scale':scale,'weapon_angle_image_clockwise_deg':math.degrees(angle),'alignment_policy':'primary_stock_exact; direction_fitted_to_two_frozen_hands; support_length_residual_retained_no_body_or_weapon_stretch','state_transforms':maps,'runtime_verified':False})
 report={'schema':'XBW-weapon-state-lifecycle-source-v1','version':1,'frozen':True,'status':'existing_native_states_and_socket_reuse_candidate_runtime_unfulfilled','weapon_id':'WPN-XBW-001',
  'reload_contract_path':str(path),'reload_contract_sha256':r.sha(path),'ready_primary_contracts':contracts,'states':states,'ready_primary_pose_state_transforms':poses,
  'shared_anchor_contract':{'coordinate_space':'512source_xright_ydown','canonical_stock_px':[138,274],'stock_to_support_px':[206,12],'stock_to_virtual_emit_px':[368,-45],'uniform_scale':.48,'neutral_component_pivot_reuse_forbidden':[128,253],'body_transforms':'none','runtime_mirror':'parent_once_about_ground_root_for_component_and_all_sockets_together'},
  'lifecycle_visual_selection_proposal':{'outside_reload':'actual_ammo_positive_select_state3_loaded_else_state0_empty','primary_windup':'keep_loaded_state3_until_actor_reports_real_projectile_emission','after_actual_emission':'select_empty_state0_after_real_actor_commit_not_according_to_image_frame_or_HUD_guess','reload':'render_4_existing_keyposes_by_actual_reload_elapsed_ratio; state3_last_keypose_is_visual_pending_commit','reload_complete':'only_actual_successful_kernel_ReloadComplete_updates_ammo_and_latches_loaded_state3','cancel_or_failure':'read_actual_actor_ammo/state; do_not_grant_loaded_ammo_or_undo_real_emission_from_image','authority':'proposal_to_runtime_owner_not_implemented_here; gameplay_actor/kernel_remains_sole_authority'},
  'socket_authority_contract':'renderer_and_producer_read_the_same_selected_native_weapon_state_and_same_component_to_body_matrix; imageY_is_not_direct_combatZ',
  'new_generation_calls':0,'runtime_verified':False,'producer_socket_verified':False,'full_weapon_actions_complete':False,
  'limitations':['Stock/support are actual visible contact-center measurements with ~4sourcepx uncertainty, not exact anatomical joints. Existing texture patches are not byte-identical translations; only numeric socket offsets are shared.',
   'At fixed.48, support residual is~2.076body-sourcepx for ready and~1.972..3.129px for primary. Primary stock contact is exact; original hand anatomy and component size remain unchanged.',
   'Inherited virtual Emit has alpha255/2/13/0 across states0..3. It is a numeric front-rail exit, not an opaque-pixel certificate or arrow-tip location.',
   'Loaded state3 visible bolt tip~[483,205] is24sourcepx above inherited rail-exit y229. Native art does not certify a straight mechanical bolt-flight axis; runtime visual review remains necessary.',
   'The old neutral128253 stock pivot belongs to a different component and is forbidden for these four states. Original frozen ready/primary/reload manifests remain untouched.',
   'No runtime selection,ammo transaction,world Emit Height/ground-plane semantics or actual shot handoff is implemented or verified in this source task.']}
 q=P/'manifests/weapon-state-lifecycle-v001.json';assert not q.exists();r.write(q,report);r.archive(q,q.relative_to(P),'frozen_actual_native_weapon_state_socket_reuse_and_honest_virtual_emit_contract_not_runtime_authority')
 print(json.dumps({'manifest':str(q),'sha256':r.sha(q),'states':4,'reused_textures':4,'new_generation_calls':0,'stock_points':[x['stock_grip_px'] for x in states],'ready_support_error':poses[0]['state_transforms'][0]['support_alignment_error_body_source_px'],'primary_support_error':[x['state_transforms'][0]['support_alignment_error_body_source_px'] for x in poses if x['action']=='primary']}))
if __name__=='__main__':main()
