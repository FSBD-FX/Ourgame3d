"""Root precommits limited authored late recovery translation; never a footlock claim."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, math

R=Path('F:/Ourgame'); B=R/'source-assets/production/fairytale-guard-v001'
old=B/'stomp-source-fit-audit-v001/stomp248-recovery4-extraction-review-v001/post-E540-minimal-visible-registration-and-Ready4-joins-v001.json'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def pin(p): return dict(path=p.as_posix(), bytes=p.stat().st_size, sha256=sha(p))
def write(p,d):
    with p.open('x',encoding='utf-8',newline='\n') as f: json.dump(d,f,ensure_ascii=False,indent=2);f.write('\n')
assert sha(old)=='9df4311173d450bb885c3dee44d593cfa886271a4d133e7f51d3af328505bdf3'
d=json.loads(old.read_text(encoding='utf-8-sig'))
assert d['perframe_roots']==[[275,463],[282,464],[272,464],[279,464]]
roots=[[275,463],[282,464],[260,464],[256,464]]
density=d['ONE_row_density']; rows=[]
for i,f in enumerate(d['rows']):
    row={k:f[k] for k in ['frame','source','RGBA_sha256','crown_artist_ROI','crown_core_y','NEAR_floor_y','visible_body_extent','feet','eye']}
    assert pin(Path(row['source']['path']))==row['source']
    row.update(authorRoot_proposal=roots[i], original_support_root=f['authorRoot_proposal'],
               pivot_authority='ArtistNearSupportDeltaPropagation' if i<2 else 'ArtistStandingRootPropagation',
               whole_sprite_translation_from_original_display_px=[(f['authorRoot_proposal'][0]-roots[i][0])*density,0])
    row['eye_from_authored_root_display']=[(f['eye']['centroid'][j]-roots[i][j])*density for j in range(2)]
    row['near_surface_from_authored_root_display']=[(f['feet'][0]['bottom4_alpha_centroid_x']-roots[i][0])*density,(f['NEAR_floor_y']-roots[i][1])*density]
    rows.append(row)
joins=[]
for q in d['Ready209_four_joins']:
    eye=[q['eye_from_root_display'][j]-rows[3]['eye_from_authored_root_display'][j] for j in range(2)]
    near=[q['near_from_root_display'][j]-rows[3]['near_surface_from_authored_root_display'][j] for j in range(2)]
    joins.append(dict(Ready_frame=q['Ready_frame'], source=q['source'], eye_delta_display=eye,
                      eye_euclidean_display_px=math.hypot(*eye),near_surface_delta_display=near))
late=[dict(from_frame=i-1,to_frame=i,near_surface_delta_display=[rows[i]['near_surface_from_authored_root_display'][j]-rows[i-1]['near_surface_from_authored_root_display'][j] for j in range(2)]) for i in [2,3]]
out=B/'root-Stomp-source-approval-v001';out.mkdir(exist_ok=True)
reg=out/'Recovery248-Root-authored-late-return-registration-v001.json'
write(reg,dict(schema='Root-GuardRecovery248-authored-late-return-registration-v001',utc=datetime.now(timezone.utc).isoformat(),
    original_proposal=pin(old),source_index=d['source_index'],source_actual_View=d['source_actual_View'],
    bodybasis_frame=2,bodybasis_crown_y=48,bodybasis_NEAR_floor_y=464,standing_equivalent_extent_px=416,
    body_display_height_target=100.8,ONE_row_density=density,ONE_row_canvas_side=d['ONE_row_canvas_side'],
    perframe_roots=roots,rows=rows,A2451_to_R2480_unchanged=d['A2451_to_R2480'],
    Ready209_current_profile=d['Ready209_current_profile'],Ready_selection_fact=d['Ready_selection_fact'],
    Ready4_authored_joins=joins,late_discrete_near_surface_changes=late,
    authored_intent='R0/R1 retain support registration; R2/R3 translate whole sprite right to reduce ending head discontinuity. Late near shoe visibly shifts at discrete375ms frame boundaries; no painted step or footlock is claimed.',
    source_RGBA_unchanged=True,actor_XY_changed=False,perframe_scale_normalization=False,kernel_timing_changed=False,
    RegistrationLockedByRoot=True,limited_native_trial_only=True,footlock_certified=False,FinalAccepted=False))
approval=out/'Recovery248-Root-limited-source-fit-v001.json'
write(approval,dict(schema='Root-GuardStompRecovery248-limited-source-fit-v001',RootApproved=True,is_template=False,
    native_source_id=248,clip='StompRecovery',limited_import_candidate_approved=True,
    Root_actual_View_four_transparent_after_E=True,retention='E:/OurGame/Knight/过程图稿与视频/2026-10-18-OurgameUE-GuardStomp248-extraction-v540',
    retention_verification_passes=2,retention_hash_mismatches=0,source_index_sha256=d['source_index']['sha256'],
    registration_proposal_sha256=sha(reg),standing_basis_frame=2,standing_body_crown_y=48,standing_body_nearsole_y=463,
    standing_body_extent_px=416,target_standing_body_height_px=100.8,floor_pivots_source_px=roots,
    remaining_visual_risks=['Late authored whole-sprite shifts may read as sliding: near shoe changes about2.990/2.517displaypx at discrete boundaries.',
    'R3 to Ready eye horizontal difference4.913–8.830px; Ready1 Euclidean difference about10.208px. Actual clock chooses the returning Ready phase.',
    'Original support-root proposal is retained; only first two phases still use its support registration. Bilateral native-size motion remains unverified.'],
    per_frame_scale_normalization=False,non_uniform_scale_or_local_body_paint=False,kernel_timing_changed=False,
    native_stomp_verified=False,footlock_certified=False,FinalAccepted=False,formal_complete_units=0))
print(json.dumps(dict(registration=pin(reg),approval=pin(approval),ready_joins=joins,late_surface_changes=late),ensure_ascii=False))
