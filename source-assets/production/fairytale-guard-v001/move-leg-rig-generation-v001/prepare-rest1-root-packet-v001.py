"""Prepare only; no native generation, source admission, or asset import."""
from pathlib import Path
import hashlib, json, shutil, subprocess, sys
import numpy as np
from PIL import Image

ROOT=Path('F:/Ourgame')
OLD=ROOT/'source-assets/production/fairytale-guard-v001/art-preparation-v001'
OWN=Path(__file__).resolve().parent
PACK=OWN/'rest1-root-call-packet-v001'
RUN=PACK/'run-guard-move-rest1-component-source-v001'
MEDIA=ROOT/'过程图稿与视频/2026-10-18_裂岩守卫Move七组件首组Rest1调用准备_v001'
SG=Path('C:/Users/22499/.codex/skills/sprite-gen')
PY=SG/'.venv/Scripts/python.exe'
ORIGINAL=OLD/'move-leg-rig-seven-components-generation-ready-v001/rest1/run-guard-move-leg-rig-rest1-v001'
CORRECTED=OLD/'move-leg-rig-static-prompts-corrected-v002'
READY=OLD/'armed-ready4-extraction-v001/run-ready209-shared-HD-v001'
E416=Path('E:/OurGame/Knight/过程图稿与视频/2026-10-18-OurgameUE-guard-Move-rig7-corrected-input-v416/source-size-SHA256.json')
RAW=OWN/'process-batches/2026-10-18-Guard-MoveRest1-native-v001/raw/move_bodyrest.png'

def data(p):
    return Path('\\\\?\\'+str(Path(p).resolve())).read_bytes()

def pin(p):
    b=data(p)
    return dict(path=Path(p).as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())

def load(p):
    return json.loads(data(p).decode('utf-8-sig'))

def write(p,v):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('x',encoding='utf-8',newline='\n') as f:
        f.write(v if isinstance(v,str) else json.dumps(v,ensure_ascii=False,indent=2)+'\n')
    return p

def retained_exact(p,retention=E416):
    b=data(p);pp=pin(p);r=load(retention)
    assert r['verification_passes']==2 and r['source_and_target_hash_mismatches']==0
    matches=[x for x in r['files'] if x['sha256']==pp['sha256'] and x['bytes']==pp['bytes']]
    assert matches,p
    assert data(retention.parent/matches[0]['retained_relative'])==b

assert not PACK.exists() and not MEDIA.exists() and not RAW.exists()
PACK.mkdir(parents=True)
accepted=READY/'curated/frame-0.png'
assert pin(accepted)['sha256']=='54df5fe718a98e1568513193dbde479aff6fd393d623755feb77813cacb4e804'
anchor=ORIGINAL/'base-source.png'
im=Image.open(accepted).convert('RGBA');crop=im.getbbox()
assert np.array_equal(np.array(im.crop(crop)),np.array(Image.open(anchor)))
retained_exact(accepted);retained_exact(anchor)

# Numeric request is unchanged. Its right_idle4 is carried accepted209, not a call.
request=PACK/'official-request-input-exact-v001.json'
shutil.copy2(OLD/'move-leg-rig-seven-components-generation-ready-v001/rest1/standard-request-input-v001.json',request)
argv=[str(PY),'-B','-X','utf8',str(SG/'scripts/prepare_sprite_run.py'),
      '--out-dir',str(RUN),'--character-id','ENM-STN-003-Move-LegRig-PILOT-components-v001',
      '--base-image',str(anchor),'--chroma-key','#FF00FF','--request',str(request)]
result=subprocess.run(argv,capture_output=True,text=True,encoding='utf-8')
log=write(PACK/'logs/official-prepare.log',result.stdout+result.stderr)
prepare=write(PACK/'logs/official-prepare-command.json',dict(argv=argv,actual_exit_code=result.returncode,log=pin(log)))
assert result.returncode==0
assert data(RUN/'sprite-request.json')==data(ORIGINAL/'sprite-request.json')

native_prompt=PACK/'Root-native-fullprompt-rest1-exact-E416-v002.txt'
shutil.copy2(CORRECTED/'rest1/native-fullprompt-static-components-v002.txt',native_prompt)
assert pin(native_prompt)['sha256']=='81608e59d7e7ebc63fa5fa59e4dff603e69f3c22d4321c57d69fd6348e73fef4'
retained_exact(native_prompt)
refs=[]
oldrefs=load(OLD/'move-leg-rig-seven-components-generation-ready-v001/rest1/native-helper-references-ready-AFTER-ROOT-E-v001.json')
for i,row in enumerate(oldrefs['references_in_order']):
    source=Path(row['file']['path']);assert pin(source)==row['file'];retained_exact(source)
    dest=PACK/'references'/f'{i+1:02d}-{source.name}';dest.parent.mkdir(exist_ok=True);shutil.copy2(source,dest)
    refs.append(dict(file=pin(dest),role=row['role'],already_retained=True))
refs_path=write(PACK/'Root-native-helper-references-rest1-v001.json',dict(
    references_in_order=refs,
    declaration='All three images independently byte-verified against E416 before this exact copy. Root will additionally retain this new F packet before View/call. No new image pixels authored.',
    no_competing_motion_or_preidle_base=True))

# Preserve the fixed Ready209 row for later official extraction comparison.
(RUN/'raw/right').mkdir(parents=True,exist_ok=True)
shutil.copy2(READY/'raw/right/idle.png',RUN/'raw/right/idle.png')
assert pin(RUN/'raw/right/idle.png')['sha256']=='018f7b735794871959d5dc5adc7dc3e040feb159480cde768439d44f92704316'
ready_pins=[pin(READY/f'curated/frame-{i}.png') for i in range(4)]
E363=Path('E:/OurGame/Knight/过程图稿与视频/2026-10-18-OurgameUE-guard209-curated-v363/source-size-SHA256.json')
for p in ready_pins:retained_exact(p['path'],E363)
for name in ['move_bodyrest.png','idle.png']:
    assert data(RUN/f'references/layout-guides/right/{name}')==data(ORIGINAL/f'references/layout-guides/right/{name}')

bridge=OLD/'stomp224-active2-extraction-v001/shared-HD-fit-existing-exact.py'
five=write(PACK/'official-five-step-postraw-processing-contract-v001.json',dict(
    status='PENDING_RAW_ROOT_RETENTION; these commands have NOT run',
    prepared_run=RUN.as_posix(),processing_run='NEW processing copy after actual raw/E gate; do not write this prepared freeze',
    raw_source_pin=None,native_source_id=None,
    expected_generated_state='right_move_bodyrest',expected_component_roles=['bodyrest_fixedaxe'],
    requested_components=1,runtime_animation_frames=0,
    canvas=[512,512],safe_margin=[48,48],min_used_pixels=512,min_gate_changed=False,
    HD_shared_fit_bridge=pin(bridge),
    commands_after_input_copy=[
      dict(step='extract',script=bridge.as_posix(),arguments=['--run-dir','PROCESS_RUN','--min-used-pixels','512'],note='Existing approved HD shared-row adapter wraps official chroma/components/extraction; no per-part/per-pose normalization'),
      dict(step='inspect',script=(SG/'scripts/inspect_sprite_run.py').as_posix(),arguments=['--run-dir','PROCESS_RUN','--states','right_idle,right_move_bodyrest','--report','PROCESS_RUN/inspect-report.json']),
      dict(step='compose',script=(SG/'scripts/compose_sprite_atlas.py').as_posix(),arguments=['--run-dir','PROCESS_RUN','--min-used-pixels','512']),
      dict(step='curate/export',script=(SG/'scripts/export_curated_pngs.py').as_posix(),arguments=['--run-dir','PROCESS_RUN','--state','right_move_bodyrest','--selected-only'],note='Stamp only selected[0], no transform. Check outputRGBA exact to extracted frame.'),
      dict(step='preview',script=(SG/'scripts/preview_animation.py').as_posix(),arguments=['--run-dir','PROCESS_RUN'],note='Static source preview only; fps1 is not Move animation timing')],
    actual_exit_codes=None,QA=None,curated_source_pin=None,
    source_checks=['One complete connected legless upperbody+pelvishem+same fixedaxe; both closed hands nearbutt/farhead unchanged.',
      'No residual legs, shoes, thigh stubs, thirdboots, disconnected spare parts, visible guide stroke, sourceedge crop.',
      'Verify moss/stone/amber colors survive keying; preserve original reports and rejection.',
      'Ready209 carried4 re-extractedRGBA must equal accepted4; do not generate them.',
      'Publish sourceindex/QA/Fdated originals+presentation; Root E and actualView before measurements or source acceptance.'],
    component_bottom_is_ground_floor=False,
    body_standing_extent=None,component_display_density=None,authorRoot=None,
    authority='The legless component has no shoe floor or full standing-height measurement. Future hip sockets are authored2D markers, not recovered bones.'
))

pilot=load(OLD/'move-leg-rig-seven-components-generation-ready-v001/seven-source-components-eighteen-author-markers-and-contact-pilot-contract-v001.json')
dependency=write(PACK/'Near3-Far3-after-Rest-dependency-contract-v001.json',dict(
    status='BLOCKED_ON_ACTUAL_REST_SOURCE; NOT_NATIVE_CALL_READY',
    canonical_identity=pin(accepted),
    baseline_prompts=[dict(group=g,prompt=pin(CORRECTED/f'{g}/native-fullprompt-static-components-v002.txt')) for g in ['near3kit','far3kit']],
    accepted_Rest_curated_source=None,Root_Rest_source_review=None,
    required_inputs_after_Rest=['Actual retained+reviewed leglessRest curvedpelvis/overlap surfaces and complete upperbody/fixedaxe.',
      'Visible NEAR/FAR socket regions, cap-width targets and authored art-unit density established from real source; no hidden anatomy inference.',
      'NEW reference order/ownership adapter: Ready209 remains sole character identity; actualRest is only accepted construction/cap interface reference; official3cell and role guides remain layout.',
      'Measure kits after shared extraction; keep one conversion inside each3part kit, freeze explicit crosskit mapping only after actual review.'],
    parts=pilot['parts'],
    marker_count_required=18,marker_count_currently_authored=0,
    first_milestone='Only two opposite Near/Far leading contacts at actual acceptedDistance0/64, fixed authored lengths, complete seams, same fixedaxe,100.8 target. No full6 or runtime before this succeeds.',
    cycle_distance_world=128,NativeSourceId=None,
    three_initial_native_call_priority='Rest1 then Near3/Far3 only after Root-approved Rest input dependency; no retries or extra native call by worker.',
    source_mode='Future genuine authored2D skeletal/IK Move pilot, not AI wholebodyMove6; existing Full positiveNativeID gate must not be bypassed.',
    TrialAllowed=False,FinalAccepted=False))

metadata=write(PACK/'Rest1-source-metainfo-pending-v001.json',dict(
    schema='Guard-Move-Rest1-static-source-before-native-v001',
    accepted_idle_anchor=pin(accepted),accepted_anchor_role='Root E363 actualcuratedReady2090 internal source identity/direction lock; not neutral207/base206 or finalvisualacceptance.',
    accepted_anchor_Ready4=ready_pins,
    prepare_only_derived_direction_anchor=dict(file=pin(anchor),crop_from_accepted512=list(crop),exact_RGBA_crop=True,attached_to_native_call=False),
    actual_native_references='Three explicit referencesJSON only: exactReady2090, official1layout, generic1partroleguide. No base206/neutral207/standalone208/badMove rows.',
    carried_Ready209_raw=pin(RUN/'raw/right/idle.png'),
    official_prepare=pin(prepare),official_request=pin(RUN/'sprite-request.json'),
    helper_native_prompt=pin(native_prompt),
    generated_official_prompt_archived_but_not_call_prompt=pin(RUN/'prompts/right/move_bodyrest.txt'),
    raw_expected_path=RAW.as_posix(),actual_native_id=None,actual_raw_pin=None,
    component_roles=['bodyrest_fixedaxe'],runtime_frames=0,canvas=[512,512],min_used_pixels=512,
    exact_component_density=None,full_standing_extent=None,author_markers=pilot['parts'][0]['artist_markers'],
    no_new_final_character_pixels=True,no_generation_or_UE=True,TrialAllowed=False,FinalAccepted=False))

handoff=write(PACK/'Root-Rest1-single-native-call-handoff-v001.json',dict(
    schema='Guard-Move-Rest1-one-native-call-packet-v001',
    topic='guard-move-rest1-static-component-v001',prompt=pin(native_prompt),references_json=pin(refs_path),
    output=RAW.as_posix(),official_prepared_run=RUN.as_posix(),source_metainfo=pin(metadata),
    official_five_steps=pin(five),next_NearFar_dependency=pin(dependency),
    E416_old_inputs=pin(E416),F_retention_batch=MEDIA.as_posix(),
    current_call_scope='Exactly one new leglessbodyrest-with-fixedaxe source, not Ready4 or Move6; no native ID preassigned.',
    rationale='Separate fixed upperbody/axe from independently authored legs so two distinct hipchains can actually alternate. Preserve same approved identity; source QA and component/rig review still pending.',
    permission='Root owns automatic authorized nativecall/ledger/E. This worker prepares inputs only.',
    no_generation_invoked=True,new_packet_View=False,TrialAllowed=False,FinalAccepted=False))
write(PACK/'HANDOFF.md','Rest1 only: use Root-Rest1-single-native-call-handoff-v001.json. Prompt is byte-exact E416 corrected-v002; native references are exactReady2090 + standard1layout + genericroleguide, all independently E416 verified. Fresh officialprepare exit0 and request/guides equal original prepared run. Right_idle4 is carried209 raw only, never regenerate. Nativeoutput is intermediate; process in a NEW run after RootE gate, keep512 floor/sharedrow and source-edge/identity checks. No authored bone/hip/standingroot/density exists yet. Near3/Far3 are blocked pending real Rest source/interface review, then reuse their corrected-v002 specifications with explicit Rest-construction reference ownership. No Source/Content/tools/ledger/E or nativecalls.\n')
freeze=write(PACK/'Rest1-input-packet-freeze-v001.json',dict(schema='Guard-Move-Rest1-input-freeze-v001',files=[pin(p) for p in sorted(PACK.rglob('*')) if p.is_file()],script=pin(__file__),new_packet_View=False,generated_sources=0,TrialAllowed=False))
(MEDIA/'原件').mkdir(parents=True)
shutil.copytree(PACK,MEDIA/'原件/Rest1完整输入包')
(MEDIA/'展示副本').mkdir()
for p in (PACK/'references').iterdir():shutil.copy2(p,MEDIA/'展示副本'/p.name)
write(MEDIA/'source-version-status-index.json',dict(schema='F-dated-source-version-status-v001',source=PACK.as_posix(),handoff=pin(handoff),freeze=pin(freeze),
    files=[pin(p) for p in sorted(MEDIA.rglob('*')) if p.is_file()],status='Prepared only; exactpreexistingE416 references copied; newFpacket awaiting Rootretention beforeView/call; no generatedRest or markers.',Root_E_retention_pending=True,new_packet_View=False))
print(json.dumps(dict(handoff=pin(handoff),freeze=pin(freeze),F_batch=MEDIA.as_posix(),prompt=pin(native_prompt),references_json=pin(refs_path),output=RAW.as_posix(),prepare_exit=result.returncode,new_packet_View=False),ensure_ascii=False,indent=2))
