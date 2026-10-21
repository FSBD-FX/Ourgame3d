"""Fresh4pose recovery from only actualActive2451; officialprepare, no native calls."""
from pathlib import Path
import json,hashlib,shutil,subprocess,sys
import numpy as np
from PIL import Image
R=Path('F:/Ourgame');A=R/'source-assets/production/fairytale-guard-v001/art-preparation-v001';H=Path(__file__).resolve().parent;O=H/'stomp248-single-A2451-fresh-recovery-input-v001'
SG=Path('C:/Users/22499/.codex/skills/sprite-gen');PY=SG/'.venv/Scripts/python.exe';assert Path(sys.executable).resolve()==PY.resolve();assert not O.exists();O.mkdir()
MEDIA=R/'过程图稿与视频/2026-10-18_裂岩守卫248仅245末姿态四相起身收招标准输入_v001';assert not MEDIA.exists()
START=H/'active245-extraction-review-v001/run-stomp245-active2-shared-HD-v001/curated/frame-1.png';READY=A/'armed-ready4-extraction-v001/run-ready209-shared-HD-v001/curated/frame-0.png';ANCHOR=A/'move6-stomp-W6-A2-R4-generation-ready-v001/accepted209-anchor-readcopy/references/anchors/right-anchor-x1.png'
RAW247=H/'process-batches/2026-10-18-Guard-StompRecovery4-native247-v001/raw/stomp_recovery.png';RAW246=H/'process-batches/2026-10-18-Guard-StompRecovery4-native246-v001/raw/stomp_recovery.png'
def pin(p):
 b=p.read_bytes();return dict(path=p.as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def write(n,v):
 p=O/n;p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('x',encoding='utf-8',newline='\n') as f:f.write(v if isinstance(v,str) else json.dumps(v,ensure_ascii=False,indent=2)+'\n')
 return p
assert pin(START)['sha256']=='e74a17645e2e469bfd994a1225bcd623a0f5fb2ac0c9fc10905fcc7ccc66eda4';assert pin(RAW247)['sha256']=='39b6da4705c67096f917f943fb7b6aaa586273c69a18b01c745df1c3e74b57ce'
short='''Use this ONE exact StompActive245 frame1 image as the sole pose-edit target. Create FOUR successive recovery poses in one spacious horizontal row. Inherit its existing character, stone armor and fixed axe; do not rebuild a wide Ready stance.

Pose0 preserves the reference's loaded head, torso, knee plate, closed hands and compact NEAR shoe below the hip. Keep its NEAR-shoe-to-eye horizontal geometry, about79pixels in this512reference. It is the same settled contact, not an additional deeper crouch or forward thrust. Pose1 rises moderately from it. Pose2 straightens to stand. Pose3 holds steadily with a small heavy settling change. Both soles stay grounded throughout; no backward NEAR step, relift, third boot or second stomp.

Maintain exactly two contiguous hip→knee→ankle→ground-shoe chains. Preserve NEAR moss-arm→buttward grip and FAR arm→headward grip on one continuous shaft; no hand swap, regrip, swing or axe resizing.

Same shallow elevated three-quarter right-facing view, coarse grotesque stone/moss/ink identity and one shared body/axe density across all four poses. Complete uncropped connected silhouettes, generous spacing and padding, uniform magenta background. No grid, separator, labels, effects, shadows or scenery.
'''
words=len(short.split());assert 170<=words<=205
req=json.loads((H/'stomp246-recovery4-input-v001/standard-request-input-v001.json').read_text(encoding='utf-8-sig'));req['states']['right_stomp_recovery']['action']=short
req['style']='ExistingGuard209 identity inherited through actualActive2451. ONEimage actualA2451 supplies allposegeometry and existingidentity. FreshRecovery4, not editing or copying rejected246/247; no Ready/guide/oldstrip nativeattachment. Samefixedaxe, coarsewarmstone, sparsemoss, thickcartoonink.'
inp=write('standard-request-input-v001.json',req);run=O/'run-guard-stomp-recovery4-single-A2451-fresh-v001'
argv=[str(PY),'-B','-X','utf8',str(SG/'scripts/prepare_sprite_run.py'),'--out-dir',str(run),'--character-id','ENM-STN-003-fixed-heavyaxe-armed-v001','--base-image',str(ANCHOR),'--chroma-key','#FF00FF','--request',str(inp)]
r=subprocess.run(argv,capture_output=True,text=True,encoding='utf-8');log=write('official-prepare.log',r.stdout+r.stderr);write('official-prepare-command-v001.json',dict(argv=argv,actual_exit_code=r.returncode,log=pin(log)));assert r.returncode==0
request=run/'sprite-request.json';j=json.loads(request.read_text(encoding='utf-8-sig'));write('official-request-before-native-duration-label-v001.json',j);j['states']['right_idle']['durations_ms']=[250]*4;j['states']['right_stomp_recovery']['durations_ms']=[375]*4;request.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
official=run/'prompts/right/stomp_recovery.txt';prompt=write('Root-native-short-single-A2451-prompt-v001.txt',short)
edit=run/'references/EXACT-Active245-frame1-SOLE-MOTION-EDIT-TARGET.png';shutil.copy2(START,edit)
refs=write('native-helper-references-Root-after-E-TEMPLATE-v001.json',dict(schema='Guard248-after-Root-E-single-A2451-reference-template-v001',is_template=True,requires_Root_E_before_consumption=True,references_in_order=[dict(file=pin(edit),role='1 ONLYexactActive2451 motionEDITtarget: actualloaded head/torso/kneepad/NEARshoe-eyegeometry, sameexistingGuard+axe identity. E529 source retained. NoReady/old246/247/guide competing image.',already_retained=True)]))
a=np.array(Image.open(RAW246).convert('RGBA'));b=np.array(Image.open(RAW247).convert('RGBA'));assert a.shape==b.shape==(724,2172,4);protect=[]
for i in [2,3]:
 old=a[:,i*543:(i+1)*543];new=b[:,i*543:(i+1)*543];protect.append(dict(cell=i,RGBA_exact_equal=bool(np.array_equal(old,new)),changed_RGBA_pixels=int(np.any(old!=new,axis=2).sum()),total_pixels=393132))
rejection=write('native247-raw-motion-and-pixel-protection-rejection-v001.json',dict(schema='Guard247-raw-rejection-v001',raw=pin(RAW247),target246=pin(RAW246),retention='RootE5362SHA0; worker independently exactretainedbytes compared then actualrawView.',actual_raw_View_by=['Root','worker'],motion_result='Firsttwo remainnearbehindleft/widesupport and forward/deepcrouch as246; no closeA2451startinggeometry. Rejected withoutfive-step repeat.',requested_lasttwo_pixel_protection=protect,pixel_count_limit='FullRGBA includes backgroundcolor drift; counts prove exactprotectionfailure but do not assert allthese are repaintedbodypixels.',TrialAllowed=False,FinalAccepted=False))
contract=write('single-source-motion-identity-and-phase-contract-v001.json',dict(schema='Guard248-singleA2451-FRESH-Recovery4-contract-v001',sole_motion_edit_target=pin(START),existing_Ready209_identity_pin_ONLY=pin(READY),native_reference_count=1,old246_247_Ready_guide_NOT_attached=True,officialguide_and_longprompt_archival_only=True,fresh_fourpose_row=True,pose_order=['A2451samecontactsettle/noextradeepcrouch','moderatelyrise','standstraight','steadyholdwithsmallsettle'],first_pose_near_eye_source512_dx=79.09362649169259,first_pose_near_eye_display_dx=19.16499411144859,first_geometry_authority='ActualvisibleA2451source surfaces only; no bone/wrist/COM inferred.',native_frames=4,native_phase_ms=1500,native_durations_ms=[375]*4,native_sample_start_ms=[0,375,750,1125],SG_uniform_preview_only_ms=[333]*4,shared_row_scale=True,min_used_pixels512_unchanged=True,perframe_height_normalization=False,source_actor_XY_deadlines_damage_unchanged=True,requested_source_preservation_not_guaranteed=True,new_native_raw=None,old225_246_247_not_preaccepted=True,TrialAllowed=False,FinalAccepted=False))
target=H/'process-batches/2026-10-18-Guard-StompRecovery4-native248-v001/raw/stomp_recovery.png'
hand=write('Root-native-generation-ready-v001.json',dict(schema='Guard248-official-FRESH-fourframe-singleA2451-handoff-v001',run_dir=run.as_posix(),prompt=pin(prompt),official_long_prompt_ARCHIVE_ONLY=pin(official),request=pin(request),refs_json=pin(refs),output=target.as_posix(),identity_motion_phase_contract=pin(contract),rejected247=pin(rejection),native_prompt_words=words,worker_native_calls=0,new_guides_viewed=False,Root_E_input_retention_required_before_native=True))
freeze=write('official-input-freeze-v001.json',dict(schema='Guard248-singleA2451-FRESH-official-input-freeze-v001',files=[pin(p) for p in sorted(O.rglob('*')) if p.is_file()],native_called=False,new_media_viewed=False,FinalAccepted=False))
(MEDIA/'原件').mkdir(parents=True);shutil.copytree(O,MEDIA/'原件/标准输入包');(MEDIA/'展示副本').mkdir();shutil.copy2(edit,MEDIA/'展示副本/actualA2451-SOLEmotion-EDITtarget.png')
(MEDIA/'source-version-status-index.json').write_text(json.dumps(dict(schema='F-dated-source-version-status-v001',source=O.as_posix(),handoff=pin(hand),files=[pin(p) for p in sorted(MEDIA.rglob('*')) if p.is_file()],status='Officialprepare only; fresh4pose singleA2451 EDITtarget, noReady/oldstrip/guideattachment. Root E beforeView/native.',new_media_viewed=False,Root_E_retention_pending=True),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(F_batch=MEDIA.as_posix(),handoff=pin(hand),prompt=pin(prompt),words=words,refs=pin(refs),raw_output=target.as_posix(),freeze=pin(freeze),native_called=False),ensure_ascii=False))
