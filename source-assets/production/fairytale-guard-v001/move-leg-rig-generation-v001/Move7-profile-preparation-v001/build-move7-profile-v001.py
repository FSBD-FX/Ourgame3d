"""Convert frozen author data into one candidate runtime JSON; no source edits."""
from pathlib import Path
import json,copy,sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
import move7_host_reference_solver_v001 as host
R=Path('F:/Ourgame');O=R/'source-assets/production/fairytale-guard-v001/move-leg-rig-generation-v001'
C=Path(__file__).resolve().parent;F=O/'rest252-seven-part-author-trial-v001'
REVIEW=R/'docs/production/first-batch-v2/evidence/GuardMove-v140-v001/Root-Rest252-seven-part-preparation-review-v001.json'
def write(p,v):
 with Path(p).open('x',encoding='utf-8',newline='\n') as f:f.write(v if isinstance(v,str) else json.dumps(v,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
pre=host.pin(F/'pre-render-parameters-freeze-v001.json');out=host.pin(F/'limited-author-trial-output-freeze-v001.json')
assert pre['sha256']==host.PRE_SHA and out['sha256']==host.OUTPUT_SHA
predata=host.verify(pre);old=host.verify(predata['markers']);trajectory=host.verify(predata['trajectory'])
assert host.pin(REVIEW)['sha256']=='988aad91d063be6ba0be253cbc55957fe8e145a93eca56652365c06cd50f1b79'
review=host.read(REVIEW);assert review['PreparationAllowed'] and not review['RuntimeTrialAllowed'] and not review['FinalAccepted']
e=host.verify(review['E_retention']);assert e['verification_passes']==2 and e['source_and_member_hash_mismatches']==0
records=[]
for x,name in zip(old['parts'],host.NAMES):
 texture=f'{host.NS}/T_GuardMoveRig_{name}_v001.T_GuardMoveRig_{name}_v001'
 records.append(dict(part=x['part'],source=x['source'],RGBA_sha256=x['source_RGBA_sha256'],
  decoded_pixel_sha256=x['source_RGBA_sha256'],decoded_hash_definition='512x512 RGBA8, row-major top-left, exact Image.convert(RGBA).tobytes()',
  source_size=[512,512],source_mode='RGBA',source_native_batch_id=x['native_component_source_id'],
  artist_surface_markers=x['artist_surface_markers'],component_to_rest_scale=x['whole_kit_conversion_to_Rest_art_units'],
  texture_object_path=texture,actual_import_receipt=None))
profile=dict(schema='Guard-Move7-frozen-runtime-profile-candidate-v001',presentation_type='GuardMoveSevenComponentRigDerived',
 profile_id='GuardMoveRig252_250_251_AuthorOwnHipC128_v001',source7=records,
 marker_authority='ArtistSurfaceAttachmentNotSkeletonSocket; no recovered bones, anatomy, physical lengths or COM. Legacy hip_socket labels are author-data keys only.',
 frozen_inputs=dict(pre_render=pre,output=out,original18=predata['markers'],original_formulas=predata['trajectory'],
  original_formula_script=predata['script'],original6_author_poses=host.pin(F/'one-limited-six-phase-author-trial-proof-v001.json'),
  Root_preparation_review=host.pin(REVIEW),E572=review['E_retention']),
 parameters=dict(source_ground=[250.,580.],core_crown_y=131.,standing_extent=449.,standing_display_height=100.8,
  screen_scale=100.8/449.,cycle_distance_world=128.,step_distance_world=64.,foot_half_stance_display=20.8,
  swing_lift_display=2.,body_hip_bob_display=4.,branches={'near':-1,'far':1}),
 layer_order=host.ORDER,derived_chains=host.derive_chains(records),
 formulas=dict(distance='P=positive_mod(ownerAcceptedDistance,128); h=(P>=64); u=(P-64*h)/64',
  stance='Near if h0, Far if h1; other chain swings.',
  foot_x='ownHipX+(20.8-41.6u) for stance, ownHipX+(-20.8+41.6u) for swing, in display units at UIScale1',
  foot_y='Core sole ground0 for stance; swing core sole=-2*sin(pi*u)^2 display units.',
  body_hips='BodyRest and both author hip points move UP4*sin(2*pi*P/128)^2 display units. Legs solve fixed chains toward unchanged stance floor / swing foot target.',
  IK='V=T-H; d=|V|; a=(L1^2-L2^2+d^2)/(2d); h=sqrt(L1^2-a^2); K=H+a*V/d+branch*h*perp(V/d). Reject unreachable; never clamp/stretch.',
  source_to_screen='A=UIScale*diag(actualFacing,1)*(screenScale*kitScale*R(theta)); b=screenGround+UIScale*diag(actualFacing,1)*screenScale*anchor-A*sourcePivot; screen=A*sourcePixel+b.',
  uniform_similarity='Rest1; allNear3 .36; allFar3 .36; one screenScale100.8/449; UIScale is one actual viewport factor, never pose/part normalization.',
  mirror='Reflect completed canonical hierarchy once in screenX around screenGround. Never swap Near/Far source identities or layer order. Full affine vertices use ordinary UV; equivalent DrawTexture uses left UVU1/DU-1, angle-theta, pivotUVX1-sourcePivotX/512. Choose ONE representation; do not mirror either twice.'),
 continuous_limits=dict(standing_basis_height=100.8,six_sample_max_crown_height=103.8,continuous_max_crown_height=104.8,
  nominal_stance_dx_dd=-.65,body_bob_not_ground_or_actor_motion=True,per_pose_scale=False,
  boot_pitch='Fixed source heel/toe rotation; lowest alpha>=128 core point defines author sole, not certified floor contact.'),
 input_contract=dict(owner_entity_id='uint64>0 actual instance',accepted_path_owner_entity_id='same uint64; reject owner mismatch',
  accepted_distance_world='finite double>=0 actual collision-resolved owner path; host stateless; never timer/frame/draw count or speed*time',
  actual_facing='int +1 right or -1 left from same actual owner, not inferred from distance',screen_ground_px='finite double[2] from current actual HUD/world-ground projection',
  ui_scale='one finite positive actual viewport scale; canonical rig screenScale remains fixed for every part and pose',
  profile_sha256='exact admitted JSON byte hash',source_snapshot_sha256='exact validated profile source/formula fingerprint',
  atomic_texture_ready_paths='exact7 unique object paths, all ready before any part; reference assertion is not GPU proof'),
 output_contract=dict(valid_reference_plan='bool; false => empty parts atomically',parts='7 in fixed layer_order, or0',
  source_to_screen_affine_rowmajor_2x3='[a00,a01,b0,a10,a11,b1] double, complete source512 pixel to screen map',
  source_to_screen_affine_float32='same six independently cast float32 parameters for trace comparison',
  DrawTexture_equivalent='positiveSize + pivotUV + angle; left U1/DU-1 equivalent to ONE reflection',
  DrawTexture_float32_trace='Top/Size/angle castfloat; UV exact; pivotUV double; DrawScale1/ScalePositionfalse',
  chains='visible author H/K/T positions, fixed lengths/errors, branch/sole target for diagnostics only'),
 snapshot_contract=dict(profile_file_and_source_pixels_checked=True,all_original18_points_and_fixed_lengths_checked=True,
  compiled_snapshot=None,current_Source_pins=None,Root_runtime_source_approval=None,actual_import_receipt=None,
  actual_FinishCompilation_or_GPU_residency_receipt=None,native_gate='CLOSED_PENDING_ROOT_CURRENT_ADMISSION; this host cannot approve native/GPU residency',
  rejection='Any invalid source, profile pin, source snapshot, finite/owner/facing/resource condition returns0parts; never partial quad or a Ready/grey fallback declared as this Move rig.'),
 unresolved_runtime_authorities=dict(state_entry_exit_reset='Root must derive from actual kernel; no reset/turn parameter authored here.',
  reversal_turn='Canonical straight-X formula only. Runtime must bind actual owner Facing and accepted path. Orientation reflection is geometric, not proof of continuous turn contact.',
  diagonal_worldY='Not authored or certified by this source; actual world-to-screen ground projection and kernel movement authority required.',
  blocking='No accepted path => no phase advancement; reference has no clock.',teleport_save_restore='No policy invented; Root kernel authority required.'),
 preparation_allowed_by_Root=True,RuntimeTrialAllowed=False,FinalAccepted=False,footlock=False,formal_complete_units=0)
profile['source_snapshot_sha256']=host.canonical_hash(profile)
host.validate_profile_data(profile)
path=C/'GuardMove7-runtime-profile-candidate-v001.json';write(path,profile)
base=dict(owner_entity_id=3,accepted_path_owner_entity_id=3,accepted_distance_world=0.,actual_facing=1,
 screen_ground_px=[640.125,420.875],ui_scale=1.25,source_snapshot_sha256=profile['source_snapshot_sha256'],profile_sha256=host.pin(path)['sha256'],
 atomic_texture_ready_paths=[x['texture_object_path'] for x in records])
write(C/'host-reference-request-example-v001.json',base)
write(C/'C++-input-output-and-boundaries-v001.md','''Machine contract is GuardMove7-runtime-profile-candidate-v001.json. Geometry alone is PreparationAllowed; RuntimeTrialAllowed=false. Root review988aad91… did not admit native or final art.

Inputs: same real owner uint64 and accepted-path-owner ID; actual collision-resolved AcceptedDistanceWorld double; explicit ActualFacingSign±1; current actual HUD ScreenGroundPx; one actual viewport UIScale. No frame/timer/speed input. ScreenScale100.8/449 and perkit1/.36/.36 never vary with pose. The host is stateless and owns no state entry/exit, turn, blocked movement, save or teleport resets. Root must bind these from the real kernel. Ownhip/C128 only defines canonical straight-X, not physical stride or turning/diagonal contact.

Validate the exact profile/source snapshot, all7 admitted Texture2D512 and original18 opaque author points. All7 must finish compilation and be cached resident before any quad. Runtime must use current compiledSource/Root admission/import pins; template null fields never establish native approval. The host resource-ready list is merely supplied reference input and records GPU_residency_observed=false.

Each result supplies canonical art anchor/pivot/angle and full source-to-screen double affine plus float32 parameters. Render exactly7 slots in stored layer order. Near/Far identities/order never swap with Facing. ONE mirror: use affine positions with ordinaryUV, OR equivalent positiveSize DrawTexture with mirroredUV U1/DU-1, negative angle and mirrored pivotUVX. Do not apply both full-affine reflection and UV reflection. Bodybob only moves body/hips; IK legs follow, stance core soles remain author ground0. Standing100.8 basis is fixed, continuous bob crown104.8 disclosed. The6×100ms old GIF is not runtime phase timing.

Invalid/nonfinite owner/path/facing/ground/scale, source mismatch, modified marker/limb scale, snapshot mismatch or missing any resource rejects the entire plan with0parts; no clamping/reach stretching/partial output. Actual C++ GPU/cache/DrawTexture evidence and native acceptedPath observations remain separate Root work. No ApplyCombatHit, time/Facing/actor mutation, native generation or engine calls occur here.
''')
print(json.dumps(dict(profile=host.pin(path),source_snapshot_sha256=profile['source_snapshot_sha256'],source_count=7,marker_count=18,example=host.pin(C/'host-reference-request-example-v001.json')),ensure_ascii=False,indent=2))
