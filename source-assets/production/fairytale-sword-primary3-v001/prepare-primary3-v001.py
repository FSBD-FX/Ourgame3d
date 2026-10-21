"""Prepare only a new Primary3 component-row input; no native call or media view."""
from pathlib import Path
from datetime import datetime
import difflib, hashlib, json, re, shutil, subprocess, sys
from PIL import Image

ROOT=Path('F:/Ourgame')
OUT=Path(__file__).resolve().parent
SG=Path('C:/Users/22499/.codex/skills/sprite-gen')
RUN=OUT/'run-primary3-v001'
STATE='sword_primary_3'
DURATIONS=[110,110,60,60,160,160]
V115=ROOT/'source-assets/production/backups/2026-10-16_Primary2Armor42-fit-full138GREEN-v115'
NUMERIC=ROOT/'docs/production/first-batch-v2/evidence/sword-primary3-preparation-v001/primary3-numeric-constraints-v001.json'
CANON=ROOT/'source-assets/production/fairytale-hero-v001/sprite-run-idle-v002/curated/frame-0.png'
PAIRED=ROOT/'source-assets/production/fairytale-armor-sword-primary2-v001/guides/native171-six-original512-contact-v001.png'
P2=ROOT/'source-assets/production/fairytale-sword-primary2-v001/run-primary2-v004'

def require(ok,why):
    if not ok:raise ValueError(why)
def fact(p):
    p=Path(p).resolve();b=p.read_bytes();return {'path':p.as_posix(),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def load(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p,value):
    p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('x',encoding='utf-8',newline='\n') as f:f.write(value if isinstance(value,str) else json.dumps(value,ensure_ascii=False,indent=2)+'\n')
def copy(source,dest):
    require(not dest.exists(),'No overwrite');dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,dest)
    require(source.read_bytes()==dest.read_bytes(),'Copied source changed');return dest

require(Path(sys.executable).resolve()==(SG/'.venv/Scripts/python.exe').resolve(),'Dedicated sprite-gen Python required')
require(not RUN.exists() and not (OUT/'preparation-freeze-v001.json').exists(),'Fresh preparation only')
require(fact(NUMERIC)['sha256']=='c6f85749f3b4390ad9e4c92822c0dbeed189ea97dd0d6a543080bdd6c24cfef4','Frozen Stage2 numeric contract changed')
numeric=load(NUMERIC);require(numeric['facts']['six_pose_durations_ms']==DURATIONS and sum(DURATIONS)==660,'Real kernel timing required')
manifest=load(V115/'compiled-source-manifest.json')
source_checks=[]
for f in manifest['files']:
    if not f['path'].startswith('UnrealGame/Source/'):continue
    live=ROOT/f['path'];backup=V115/f['path'];expected=(f['bytes'],f['sha256'])
    require((fact(live)['bytes'],fact(live)['sha256'])==expected and (fact(backup)['bytes'],fact(backup)['sha256'])==expected,'Current Source or v115 copied Source mismatch: '+f['path'])
    source_checks.append({'source':fact(live),'v115_copy':fact(backup)})
require(len(source_checks)>100,'Must inspect actual v115 Source set, not an empty match')
for reference in numeric['references'].values():
    f=reference['file'];require(fact(f['path'])==f,'Source-grounded numeric reference changed')
require(fact(CANON)['sha256']=='f931dec698967ae497daf85d8bfd2a9c49d59ca34fd56a96a6167e677c3de718','Accepted canonical131 idle identity changed')
require(fact(PAIRED)['sha256']=='0462a3379dfedf159767a360bd573a86523376b3814ef9ea7ca2d0a6caaf36fb','Retained actual171 paired motion contact changed')
extract=load(P2.parent/'primary2-extraction-v004/extracted-freeze-v004.json')
require(fact(P2.parent/'primary2-extraction-v004/extracted-freeze-v004.json')['sha256']=='2c4051b8b3e0b190d501ee28324e767c5e882c5fe57e708b1f1bb991485c7521','Actual171 extraction freeze changed')
for f in extract['files']:require(fact(f['path'])=={k:f[k] for k in ['path','bytes','sha256']},'Actual171 frozen source changed')
contact=Image.new('RGB',(3072,512),'#eeeeee')
six=[]
for i in range(6):
    p=P2/f'curated/frame-{i}.png'
    with Image.open(p) as body:
        require(body.mode=='RGBA' and body.size==(512,512),'Actual171 original512 RGBA required')
        contact.paste(body,(i*512,0),body)
    six.append(fact(p))
with Image.open(PAIRED) as retained:
    require(retained.mode=='RGB' and retained.size==(3072,512) and retained.tobytes()==contact.tobytes(),'Retained contact must exactly be original171 unresampled pixels composited over gray')
identity=copy(CANON,OUT/'sources/canonical131-accepted-idle0.png')
paired=copy(PAIRED,OUT/'sources/native171-six-original512-motion-contact.png')

action='Six distinct one-handed short-elbow finishing DOWN-CUT body poses: low guard with inward load, visible shoulder-outside bent-arm load and compressed knees, two different-height downward wrist arc strikes, low brake, low guard return. Never a spin, punch, lunge or two unchanged Ready poses.'
seed={'states':{STATE:{'frames':6,'fps':10,'loop':False,'action':action}},
    'cell':{'width':512,'height':512,'safe_margin_x':48,'safe_margin_y':48},
    'fit':{'pixel_unfake':False,'resample':'lanczos','align_x':'bbox-center','align_y':'bottom','ground_frames':False,'segmentation':'components','shared_row_scale':True}}
seed_path=OUT/'requests/primary3-numeric-input-v001.json';write(seed_path,seed)
prepare=SG/'scripts/prepare_sprite_run.py'
argv=[sys.executable,'-X','utf8','-B',str(prepare),'--out-dir',str(RUN),'--character-id','fairytale-common-hero-sword-primary3-v001',
    '--base-image',str(identity),'--description',action,'--style','Accepted canonical131 grotesque inked bell helmet, charcoal cloth, squat short limbs; same identity and fixed3/4right throughout.',
    '--cell-size','512','--safe-margin','48','--chroma-key','#00FF00','--request',str(seed_path)]
result=subprocess.run(argv,capture_output=True,text=True,encoding='utf-8')
write(OUT/'logs/standard-prepare-v001.log',result.stdout+result.stderr)
require(result.returncode==0,'Standard prepare failed; do not generate')
request=RUN/'sprite-request.json';standard=request.read_bytes()
backup=OUT/'standard-output/sprite-request-before-explicit-timing-v001.json';backup.parent.mkdir(parents=True,exist_ok=True)
with backup.open('xb') as f:f.write(standard)
final=load(request);final['states'][STATE]['durations_ms']=DURATIONS;final['fit'].update(seed['fit']);final['chroma']={'mode':'rgb','unmix_reach':4,'spill_max_fraction':.005}
request.write_text(json.dumps(final,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
write(OUT/'standard-output/request-explicit-timing-v001.patch',''.join(difflib.unified_diff(standard.decode('utf-8-sig').splitlines(True),request.read_text(encoding='utf-8').splitlines(True),fromfile='standard-prepare-output',tofile='explicit-real-kernel-Stage2-timing')))

prompt='''Create exactly SIX separated full-body poses of the SAME grotesque bell-helmet adventurer in one horizontal animation row. Reference1 is the ONLY accepted identity: preserve its bell helmet, eye window, top knob, charcoal cloth, brown gloves/boots, squat proportions, short arms, matte painted planes and heavy ink edges. Fixed three-quarter-facing-RIGHT throughout. No human face or exposed skin.

Reference2 contains the six actual native171 SECOND-CUT bodies. It supplies paired motion and the LOW GUARD ending/entry only; do not copy its six gestures as the third cut or redefine identity. The last pose shows the low single-handed guard from which this new action begins and to which it returns. Reference3 is the standard six-slot layout: count, spacing and padding only. Never copy labels, guide marks or gray background into the artwork. No discarded base or old human reference is attached.

This is a NEW THIRD-CUT FINISHER: a compact ONE-HANDED, SHORT-BENT-ELBOW downward pressing cut. Keep the torso three-quarter-right; a small hip and knee weight transfer is enough. No back-facing spin, horizontal punch, long-arm thrust, sprint, jump, lunge or giant overhead hammer. The far hand is relaxed for balance and clearly separate; it never grips a weapon or joins the near fist.

Six different ordered poses, not six copies. Pose0 begins at the previous low guard but already pulls the near elbow inward and shifts weight back slightly: readable first anticipation, not another unchanged idle. Pose1 compresses the knees more and visibly gathers the SHORT bent near arm beside the OUTSIDE of the near shoulder, with the closed gripping hand still visible below/beside the helmet rim. Do not hide the entire fist behind the helmet or make pose0 and1 identical. Pose2 releases a compact forward-and-DOWN wrist arc in front of the torso. Pose3 continues to a clearly LOWER near wrist and a different forearm angle, finishing the downward arc in front, not into the ground. These two active poses must show distinct heights and a curved cut rather than straight forward boxing. Pose4 brakes low, elbow folding, weight settling. Pose5 restores the compact LOW one-handed guard for idle or the next first cut. Two anticipation, two active, two recovery poses.

The near brown glove is CLOSED around an EMPTY cylindrical SIDE-VIEW grasp in ALL six poses, especially0,1,4,5. Curled fingers and one visible opposing thumb should imply holding a future separate handle. No open hanging fingers, reaching palm, fist aimed knuckles-first at the camera, pointing finger, claw, duplicated thumb, extra wrist or broken sleeve connection. Keep short anatomical arm lengths; create force by bent elbow, wrist turn, torso and knees, not stretched upper arms. The eye window must remain recognizable.

BODY ONLY: do not draw any sword, blade, hilt, pommel, handle, grip cylinder, stick, plug or dark object stump inside/outside the fist. No chest plate, shoulder armor, bracers, shin armor, shield or other equipment baked into the cloth body; preserve the canonical helmet and gloves. No slash trails, blur, impact effects, loose pieces, floor, cast/contact shadows, UI, text or visible grid.

Exactly six complete connected figures with generous gaps on uniform opaque GREEN #00FF00. Keep every top knob, glove and boot inside its slot, fixed camera and one anatomical scale. The later512 cells have48px safe margins, one shared row scale and a maximum standing-equivalent416px body, displayed at72px. Do not zoom/resize each pose or intentionally translate the foot baseline/root to simulate a dash. Gentle knee flex and weight transfer are allowed; no sliding boots, detached feet or expanding helmet. DisplayRoot256,464 is a later display pivot, not a measured bone.

Requested kernel timing is110/110/60/60/160/160ms, total660ms. Do not print timing. New palm coordinates, grip/axis, bones and armor attachment points are UNKNOWN; do not invent point markers or numeric sockets. The raw row remains an intermediate candidate requiring standard shared-row extraction, real hand measurement and running-game review, not accepted motion or equipment.
'''
words=len(re.findall(r"\b[A-Za-z0-9]+(?:[-'][A-Za-z0-9]+)*\b",prompt));require(words<=850,'Canonical prompt exceeds850 English words')
pp=RUN/f'prompts/{STATE}.txt'
standard_prompt=OUT/'standard-output/primary3-standard-prompt-v001.txt';standard_prompt.parent.mkdir(exist_ok=True)
with standard_prompt.open('xb') as f:f.write(pp.read_bytes())
pp.write_text(prompt,encoding='utf-8',newline='\n')
contract=OUT/'primary3-design-contract-v001.json'
phases=[]
for i,role in enumerate(['low_guard_inward_load','visible_short_elbow_shoulder_outside_load_knee_compress','front_down_arc_start','lower_wrist_down_arc_finish','low_brake','low_guard_return']):
    phases.append({'frame':i,'role_design_only':role,'duration_ms':DURATIONS[i],'actual_or_design_palm_point':None,'actual_or_design_blade_axis':None,'actual_bones':None,'actual_armor_attachment_A':{'Chest':None,'NearShoulder':None,'FarShoulder':None}})
write(contract,{'schema':'primary3-body-six-unknown-visual-points-design-v1','source_numeric_contract':fact(NUMERIC),'source_canvas':[512,512],'safe_margin':[48,48],
    'source_visible_height_upper_bound':416,'body_max_screen_height_px':72,'display_root':[256,464],'display_root_is_measured_footbone':False,
    'independent_sword_future_scale':.50,'durations_ms':DURATIONS,'total_kernel_ms':660,'kernel_stage':2,'kernel_changed':False,
    'phases':phases,'native_facing':1,'mirror_runtime_once':True,'shared_row_scale':True,'per_frame_scale_normalization':False,
    'sole_identity':fact(identity),'paired_motion':fact(paired),'paired_motion_source_original171':six,'paired_contact_policy':'Actual six original512 RGBA composited over gray with no resampling; copied referencePNG bytes exact.',
    'no_bone_or_guide_coordinates_invented':True,'formal_complete_units':0})
layout=RUN/f'references/layout-guides/{STATE}.png'
with Image.open(layout) as guide:layout_metadata={'mode':guide.mode,'size':list(guide.size),'explicitly_viewed':False}
refs=[{'role':'sole_identity_accepted_canonical131_idle_not_discarded_base','file':fact(identity)},
      {'role':'only_paired_motion_native171_secondcut_six_original512_and_last_lowguard_entry','file':fact(paired)},
      {'role':'standard_six_slot_count_spacing_padding_only_no_pose_or_bone_authority','file':fact(layout)}]
handoff=OUT/'handoffs/primary3-native-input-draft-v001.json'
write(handoff,{'generation_ready':False,'root_review_required_before_generation':True,'rows':[{'component':'SwordPrimary3Body','state':STATE,
    'run_dir':RUN.as_posix(),'raw_output_path':(RUN/'raw'/f'{STATE}.png').as_posix(),'prompt':fact(pp),'request':fact(request),
    'reference_images_in_order':refs,'standard_prepare_exit_code':result.returncode,'target_mounts_are_measured':False,
    'numeric_contract':fact(contract),'generation_scope':'One canonical131 body-only short-elbow finishing down-cut six-pose row; paired actual171 entry/exit motion only, existing660ms Stage2. No sword/handle/armor/VFX or fullmotion acceptance.'}],
    'request_number_reserved':None,'native_called':False,'external_api_calls':0,'formal_complete_units':0})
write(OUT/'preparation-readonly-proof-v001.json',{'created_local':datetime.now().astimezone().isoformat(),'standard_prepare_argv':argv,'standard_prepare_tool':fact(prepare),
    'standard_prepare_implementation':fact(SG/'sprite_gen/gen/prepare.py'),'standard_prepare_exit_code':0,'source_v115_manifest':fact(V115/'compiled-source-manifest.json'),
    'source_v115_rows_verified':len(source_checks),'source_v115_both_endpoints_mismatches':[],'source_checks':source_checks,
    'numeric_contract_checked':fact(NUMERIC),'identity_original':fact(CANON),'identity_copy':fact(identity),'paired_original':fact(PAIRED),'paired_copy':fact(paired),
    'paired_rgb_reference_exact_unresampled_gray_composite_verified':True,'layout':{'file':fact(layout),**layout_metadata},'prompt_english_word_count':words,
    'standard_request_before_explicit_patch':fact(backup),'final_request':fact(request),'standard_prompt_before_canonical_replacement':fact(standard_prompt),
    'request_explicit_extension_reason':'Pinned standard prepare STATE_KEYS_CARRIED does not preserve durations_ms. Its untouched output is retained; add exact realStage2 durations and established sharedrow/chroma recipe explicitly.',
    'known_future_standard_preview_ms':600,'real_kernel_ms':660,'standard_preview_timing_accepted':False,'new_derived_image_explicitly_viewed':False,
    'media_or_Source_or_ledger_written':False,'native_generation_approved':False,'native_called':False,'formal_complete_units':0})
write(OUT/'README.md','Primary3六相输入草稿。真实Stage2=110/110/60/60/160/160ms，总660。canonical131唯一身份，实际171六相仅paired运动/低guard入口；新掌点、轴、骨、甲A全null。SG专用venv prepare成功，原请求/提示词保留，显式补真实时轴。3参考含新标准layout尚未view，须Root先E保全再审阅。generation_ready=false且Rootreviewrequired，不预留/生成/提取/导入，不等动作、握柄或完整内容验收。\n')
for row in source_checks:require(fact(row['source']['path'])==row['source'],'Source changed during preparation')
files=[fact(p) for p in sorted(OUT.rglob('*')) if p.is_file()]
freeze=OUT/'preparation-freeze-v001.json'
write(freeze,{'schema':'primary3-standard-input-draft-freeze-v1','created_local':datetime.now().astimezone().isoformat(),'files':files,'file_count':len(files),'total_bytes':sum(f['bytes'] for f in files),
    'generation_ready':False,'root_review_required_before_generation':True,'native_called':False,'layout_explicitly_viewed':False,'formal_complete_units':0})
print(json.dumps({'handoff':fact(handoff),'freeze':fact(freeze),'prepare_exit':0,'reference_count':len(refs),'prompt_words':words,'generation_ready':False,'new_images_viewed':False},ensure_ascii=False))
