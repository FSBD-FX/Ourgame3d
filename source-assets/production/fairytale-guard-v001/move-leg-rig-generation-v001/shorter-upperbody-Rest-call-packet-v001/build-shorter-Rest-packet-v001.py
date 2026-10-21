"""Prepare inputs only. No provider, ledger, E write, UE, or existing-file edits."""
from pathlib import Path
import hashlib, json, shutil, subprocess, zipfile
from datetime import datetime, timezone
from PIL import Image

R = Path('F:/Ourgame')
O = R/'source-assets/production/fairytale-guard-v001/move-leg-rig-generation-v001'
A = R/'source-assets/production/fairytale-guard-v001/art-preparation-v001'
C = Path(__file__).resolve().parent
BATCH = R/'过程图稿与视频/2026-10-18_裂岩守卫短上身Rest单组件原生请求准备_v001'
RUN = C/'run-guard-shorter-upperbody-rest1-v001'
SG = Path('C:/Users/22499/.codex/skills/sprite-gen')
PY = SG/'.venv/Scripts/python.exe'

def rb(p):
    return Path('\\\\?\\'+str(Path(p).resolve())).read_bytes()
def pin(p):
    p=Path(p); b=rb(p)
    return {'path':p.as_posix(),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def read(p):
    return json.loads(rb(p).decode('utf-8-sig'))
def new(p, data):
    p=Path(p); p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('x',encoding='utf-8',newline='\n') as f:
        f.write(data if isinstance(data,str) else json.dumps(data,ensure_ascii=False,indent=2)+'\n')
def copy(src,dst):
    dst=Path(dst); assert not dst.exists(),dst
    dst.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(src,dst)
    assert rb(src)==rb(dst)
def retained(source, index):
    d=read(index); p=pin(source)
    assert d['verification_passes']==2
    matches=[x for x in d['files'] if x['sha256']==p['sha256'] and x['bytes']==p['bytes']]
    assert matches,(source,index)
    if 'packet' in d:
        assert d['source_and_member_hash_mismatches']==0
        zpath=Path(d['packet']['path'])
        assert pin(zpath)==d['packet']
        with zipfile.ZipFile(zpath) as z:
            assert any(z.read(x['member'])==rb(source) for x in matches)
    else:
        assert d['source_and_target_hash_mismatches']==0
        assert any(rb(index.parent/x['retained_relative'])==rb(source) for x in matches)
    return {'source':p,'retention_index':pin(index),'matching_members':matches,
            'independent_current_byte_equal':True,'verification_passes':2}

assert not RUN.exists() and not BATCH.exists()
rest=O/'rest1-extraction-v001/run-rest249-shared-HD-v001/curated/frame-0.png'
ready=A/'armed-ready4-extraction-v001/run-ready209-shared-HD-v001/curated/frame-0.png'
guide=O/'rest1-root-call-packet-v001/run-guard-move-rest1-component-source-v001/references/layout-guides/right/move_bodyrest.png'
anchor=A/'move-leg-rig-seven-components-generation-ready-v001/rest1/run-guard-move-leg-rig-rest1-v001/base-source.png'
readyraw=A/'armed-ready4-extraction-v001/run-ready209-shared-HD-v001/raw/right/idle.png'
markers=O/'two-contact-pilot-v001/surface-markers-and-fixed-conversions-v001.json'
e=Path('E:/OurGame/Knight/过程图稿与视频')
checks=[retained(rest,e/'2026-10-18-OurgameUE-GuardMoveRest249-extraction-v549/E-retention-index-v001.json'),
        retained(ready,e/'2026-10-18-OurgameUE-guard209-curated-v363/source-size-SHA256.json'),
        retained(guide,e/'2026-10-18-OurgameUE-GuardMoveRest1-inputs-v546/E-retention-index-v001.json')]
new(C/'existing-reference-retention-byte-verification-v001.json',{'checks':checks,'new_packet_retention':None})

prompt='''Create ONE redesigned legless upperbody component, with its complete held fixed axe, on flat pure #FF00FF. This is source art for a later 2D leg rig, not a full walking character or animation sheet.

Reference 1 is the accepted Rest249 component and the construction/edit target. Reference 2, accepted ArmedReady209, is the sole character, camera, helmet, armor and axe identity; its full-body stance is NOT a pose template. Reference 3 is only the official one-cell layout guide. Do not paint its lines or labels.

SHORTEN ONLY THE CHEST–ABDOMEN–PELVIS DESIGN: raise the pelvis hem and the two underside thigh attachment surfaces closer to the helmet. At matching helmet and shoulder width, the visible crown-to-hip-attachment distance should be approximately 80% of reference 1, giving future legs more of the full character's height. Make the abdomen visibly shorter through newly designed compact stone plates, rather than shrinking the whole character or vertically squashing the reference. Keep the broad helmet/head size, shoulder width, tiny amber eye window, sparse foreground moss, coarse ink and large low-detail warm stone planes. Preserve the same shallow elevated three-quarter side view facing screen right. Do not redraw a taller chest or wide-legged Ready stance.

Keep both closed fists naturally gripping the SAME continuous straight shaft: foreground moss arm at the buttward lower grip, far arm at the headward upper grip. Preserve the complete single stone axe head, shaft length, buttcap, and their proportions relative to the helmet; do not compress or enlarge the axe. Adjust arm placement naturally only as needed for the shorter torso. Keep two distinct opaque underside pelvis overlap surfaces, with simple hideable seams for the unchanged Near/Far thigh kit.

OMIT all thighs, knees, shins and shoes. No limb stubs, fake black leg silhouettes, spare parts, extra hands, shadows or ground line. Empty space below the pelvis is magenta. One complete connected component, generous clear surround on every edge, entire axe uncropped. Do not fill the cell by enlarging the torso. No numeric labels, colored markers or guide strokes. This is a new authored torso design; exact pixel preservation is not assumed.
'''
promptpath=C/'Root-native-shorter-upperbody-Rest1-v001.txt'
new(promptpath,prompt)
request=read(O/'rest1-root-call-packet-v001/official-request-input-exact-v001.json')
request['states']['right_move_bodyrest']['action']=prompt
request['style']='AcceptedArmedReady209 remains sole identity/camera. Authorized compact chest-abdomen-pelvis redesign relative to accepted Rest249 only; helmet/shoulder width and fixed axe identity preserved. Static legless component, not a standing body or Move phase.'
requestpath=C/'official-request-input-v001.json';new(requestpath,request)
argv=[str(PY),'-B','-X','utf8',str(SG/'scripts/prepare_sprite_run.py'),'--out-dir',str(RUN),
      '--character-id','ENM-STN-003-Move-LegRig-shorter-Rest1-candidate-v001','--base-image',str(anchor),
      '--chroma-key','#FF00FF','--request',str(requestpath)]
p=subprocess.run(argv,cwd=R,capture_output=True,text=True,encoding='utf-8')
new(C/'logs/official-prepare.log',p.stdout+p.stderr)
new(C/'logs/official-prepare-command.json',{'argv':argv,'actual_exit_code':p.returncode})
assert p.returncode==0,p.stdout+p.stderr
newguide=RUN/'references/layout-guides/right/move_bodyrest.png'
assert rb(newguide)==rb(guide),'Official Rest1 guide must remain byte-identical'
copy(readyraw,RUN/'raw/right/idle.png')
roles=[(rest,'01-Rest249-CONSTRUCTION-EDIT-TARGET.png','Construction/edit target only; accepted static component, not sole identity or a standing-height measurement.'),
       (ready,'02-Ready209-SOLE-IDENTITY.png','Sole accepted character, camera, helmet/armor/fixed-axe identity; no full-body stance transfer.'),
       (newguide,'03-Official-Rest1-LAYOUT-ONLY.png','Same exact official single-cell layout guide; no identity or anatomy authority; never paint guide lines.')]
refs=[]
for src,name,role in roles:
    dst=C/'references'/name;copy(src,dst)
    refs.append({'file':pin(dst),'role':role,'already_retained':True})
refpath=C/'Root-native-helper-references-shorter-Rest1-v001.json'
new(refpath,{'references_in_order':refs,'already_retained_basis':'Each image is byte-identical to independently verified prior E-retained source; Root must retain this NEW complete packet before reserve/call.',
             'sole_identity_native_id':209,'construction_target_native_id':249})

mp=read(markers);body=mp['parts'][0];im=Image.open(rest).convert('RGBA')
for m in body['artist_surface_markers'].values():
    assert list(im.getpixel(tuple(m['xy'])))==m['actual_RGBA']
head_roi=[220,100,290,180]
ys=[y for y in range(head_roi[1],head_roi[3]) for x in range(head_roi[0],head_roi[2]) if im.getpixel((x,y))[3]>=224]
crown=min(ys)
assert crown==125
hips={k:body['artist_surface_markers'][k]['xy'] for k in ['near_hip_socket','far_hip_socket']}
spans={k:v[1]-crown for k,v in hips.items()}
new(C/'geometry-design-constraints-v001.json',{
 'schema':'Guard-shorter-Rest-native-design-constraints-v001','status':'DESIGN_TARGET_NOT_NEW_SOURCE_MEASUREMENT',
 'old_Rest':pin(rest),'old_marker_authority':pin(markers),'old_core_crown_y':crown,
 'old_core_crown_measurement':{'head_ROI':head_roi,'alpha_at_least':224,'minimum_y':crown},
 'old_artist_surface_hips':hips,'old_crown_to_artist_hip_source_px':spans,
 'old_mean_crown_to_hip_source_px':sum(spans.values())/2,
 'new_target_ratio_at_matching_helmet_and_shoulder_width':0.8,
 'target_old_Rest_equivalent_units':{k:v*.8 for k,v in spans.items()},
 'target_mean_old_Rest_equivalent_units':sum(spans.values())*.4,
 'interpretation':'Compare only after one uniform width-density normalization to unchanged helmet/shoulder size. These are old-source equivalent design units, not mandatory new raw/canvas coordinates. No local anisotropic compression. New source may differ naturally and requires actual source review.',
 'preserve':['helmet/head dimensions and broad shoulder width','camera and physical foreground moss shoulder','single fixed axe visual identity and length relative to helmet','two closed fists on one shaft, near butt/far head','two distinct pelvis underside overlap surfaces'],
 'redesign':['shorter chest/abdomen stone-plate arrangement','pelvis/hem raised relative to crown','natural arm placement if necessary to maintain the same grips'],
 'body_alpha_bbox_not_standing_height':list(im.getbbox()),
 'future_final_whole_rig_display_height_target':100.8,'cycle_accepted_distance_world_target':128,
 'step_accepted_distance_world_target':64,'old_v003_best_max_knee_flexion_degrees_at_reach_boundary':[93.556,99.637],
 'inference':'Old proportion failed visible heavy-walk readability; reach alone was insufficient. Compact torso gives more final-height budget to unchanged legs. The 0.8 design goal is not proof of sufficient improvement or a valid rig.',
 'new_body_measurements':None,'new_Rest_author_root_crown_nearhip_farhip':None,
 'old_Rest_four_points_inherited':False,'unchanged_leg_components':[x for x in mp['parts'] if x['part']!='bodyrest_fixedaxe'],
 'new_cross_sheet_density':None,'new_final_uniform_scale':None,'new_total_standing_height':None,
 'no_per_part_or_per_pose_rescale':True,'no_parameter_search_or_media_render_here':True,
 'TrialAllowed':False,'FinalAccepted':False,'formal_complete_units':0})

post=read(O/'rest1-root-call-packet-v001/official-five-step-postraw-processing-contract-v001.json')
post.update(prepared_run=RUN.as_posix(),processing_run='NEW shorter-Rest extraction run AFTER actual raw and Root E gate; never write this prepared freeze',
            status='PENDING_RAW_AND_ROOT_RETENTION; five postraw commands NOT run')
post['source_checks'].extend(['Measure actual crown/helmet/shoulder/underside authored hip proportions at consistent width density; reject a merely scaled or unchanged long torso.',
 'Preserve Near250 and Far251 six original source images and each whole-kit fixed conversion until actual new Rest registration is authored; no inherited old Rest points.',
 'Do not call the legless alpha height standing height. New total-height and C128 heavy-walk readability remain pending.'])
new(C/'official-five-step-postraw-processing-contract-v001.json',post)
out=O/'process-batches/2026-10-18-Guard-Move-shorter-upperbody-Rest-native-v001/raw/move_bodyrest.png'
assert not out.exists()
metapath=C/'shorter-Rest-source-metainfo-PENDING-v001.json'
new(metapath,{'schema':'Guard-shorter-Rest1-source-metainfo-pending-v001','state':'right_move_bodyrest',
 'source_kind':'ONE newly native-authored connected legless upperbody+fixedaxe static component',
 'native_request_number':None,'native_receipt':None,'raw_source_pin':None,'raw_size':None,'raw_mode':None,
 'expected_raw_path':out.as_posix(),'prepared_request':pin(RUN/'sprite-request.json'),
 'custom_native_prompt_is_call_authority':pin(promptpath),'generated_official_prompt_archive_only':pin(RUN/'prompts/right/move_bodyrest.txt'),
 'generic_prompt_not_sent':'Native custom prompt replaces generic pure-profile/full-body/state-animation boilerplate; official numeric request/guide unchanged.',
 'source_identity':pin(ready),'construction_target':pin(rest),'old_Rest_Root_source_component_lock':pin(O/'Root-Rest249-single-component-source-fit-v001.json'),
 'old_Rest_lock_does_not_accept_new_source':True,'carried_Ready4_raw':pin(RUN/'raw/right/idle.png'),
 'Ready4_carried_exact_raw':rb(readyraw)==rb(RUN/'raw/right/idle.png'),'requested_new_components':1,
 'requested_new_Move_animation_frames':0,'expected_canvas':[512,512],'safe_margins':[48,48],
 'min_used_pixels':512,'min_gate_changed':False,'shared_row_density':True,'pixel_unfake':False,
 'actual_extract_QA':None,'actual_inspect_QA':None,'actual_curated':None,'actual_RGBA_sha256':None,
 'bodybasis':None,'author_points':None,'standing_floor':None,'new_cross_kit_conversion':None,
 'Source_UE_imported':False,'TrialAllowed':False,'FinalAccepted':False,'formal_complete_units':0})
handoff=C/'Root-shorter-Rest1-single-native-call-handoff-v001.json'
new(handoff,{'schema':'Guard-Move-shorter-Rest1-one-native-call-packet-v001',
 'topic':'guard-move-shorter-upperbody-rest1-static-component-v001','prompt':pin(promptpath),'references_json':pin(refpath),
 'output':out.as_posix(),'current_call_scope':'Exactly ONE newly authored compact chest-abdomen-pelvis legless Rest component with fixed axe; keep Ready209 sole identity, unchanged Near250/Far251 six source components; no Ready4 or Move6 generation; no native ID preassigned.',
 'official_prepared_run':RUN.as_posix(),'source_metainfo':pin(metapath),
 'geometry_constraints':pin(C/'geometry-design-constraints-v001.json'),
 'official_five_steps':pin(C/'official-five-step-postraw-processing-contract-v001.json'),
 'F_retention_batch':BATCH.as_posix(),'Root_E_inputs':None,'native_request_number':None,
 'reserve_helper':pin(R/'tools/scripts/reserve-guard-move-native-request-v001.py'),
 'save_helper':pin(R/'tools/scripts/save-guard-native-generated-image-v001.py'),
 'helper_invoked':False,'no_generation_invoked':True,'new_packet_View':False,
 'permission':'Root alone reserves, generates, saves/updates ledger and retains E under existing automatic authorization; worker prepares only.',
 'TrialAllowed':False,'FinalAccepted':False})
new(C/'HANDOFF.md','''# Shorter upperbody Rest1 — prepared only

One new source component; no native call or source acceptance. Root may use the existing reserve helper with `Root-shorter-Rest1-single-native-call-handoff-v001.json` after retaining this complete F batch. The helper schema is unchanged; prompt/ref pins were checked, output does not exist. Save uses the Root-assigned request number, never a preassigned ID.

References in order: Rest249 construction target, accepted Ready209 identity, identical official single-cell guide. Native call uses the short custom prompt; the official generated prompt remains archival. Ready4 raw is carried byte-exact, not regenerated. The new component is authorized to shorten chest/abdomen/pelvis, not globally squash the helmet or axe. Old core-crown→artist hips 295/291 sourcepx become a design goal of 236/232.8 old-Rest-equivalent units at matching helmet/shoulder width. These are visible authored surfaces, not bones. A 339px alpha box containing axe is not standing height.

New raw/QA/curated/Rest4 markers, cross-kit density, final uniform scale and total standing height remain null. Near250/Far251 six images are unchanged; old Rest four markers are not inherited. Final height 100.8, distance cycle 128 and step distance 64 remain future design constraints, not certified motion. Source review must precede a new limited rig trial. Old E557/E558 media, rejected parameter proposals, old Rest and all freezes are preserved.
''')

members=[pin(x) for x in sorted(C.rglob('*')) if x.is_file() and x.name!='shorter-Rest-input-packet-freeze-v001.json']
freeze=C/'shorter-Rest-input-packet-freeze-v001.json'
new(freeze,{'schema':'Guard-shorter-Rest1-prepared-input-freeze-v001','created_utc':datetime.now(timezone.utc).isoformat(),
 'members':members,'source_pixel_edits':False,'old_files_overwritten':False,'native_calls':0,
 'canonical_and_F_copy_two_SHA_passes_required':2,'Root_E_retention_pending':True,'new_View_done':False,
 'TrialAllowed':False,'FinalAccepted':False})
for src in sorted(C.rglob('*')):
    if src.is_file():copy(src,BATCH/'原件'/src.relative_to(C))
for ref in refs:
    src=Path(ref['file']['path']);copy(src,BATCH/'展示副本'/src.name)
copy(promptpath,BATCH/'展示副本'/promptpath.name)
copy(C/'HANDOFF.md',BATCH/'展示副本/HANDOFF.md')
copy(C/'geometry-design-constraints-v001.json',BATCH/'展示副本/geometry-design-constraints-v001.json')
for _ in range(2):
    for src in C.rglob('*'):
        if src.is_file():assert rb(src)==rb(BATCH/'原件'/src.relative_to(C))
    for ref in refs:
        src=Path(ref['file']['path']);assert rb(src)==rb(BATCH/'展示副本'/src.name)
new(BATCH/'index.json',{'schema':'Guard-shorter-Rest1-F-input-source-version-status-v001',
 'status':'PREPARED_ONLY_PENDING_ROOT_E_AND_VIEW_AND_RESERVATION','candidate':C.as_posix(),'handoff':pin(handoff),'freeze':pin(freeze),
 'files':[pin(x) for x in sorted(BATCH.rglob('*')) if x.is_file()],
 'verification_passes':2,'canonical_and_presentation_copy_hash_mismatches':0,
 'new_raw':None,'new_media_View_done':False,'source_accepted':False,'runtime_imported':False,'FinalAccepted':False})
print(json.dumps({'handoff':pin(handoff),'prompt':pin(promptpath),'references_json':pin(refpath),'freeze':pin(freeze),
 'F_batch':BATCH.as_posix(),'F_index':pin(BATCH/'index.json'),'reference_count':len(refs),
 'official_prepare_exit':p.returncode,'official_guide_exact':True,'new_output_absent':not out.exists(),
 'native_calls':0},ensure_ascii=False,indent=2))
