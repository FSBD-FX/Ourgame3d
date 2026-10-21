"""Prepare component-kit inputs only; Root source review/call gate remains closed."""
from pathlib import Path
import hashlib,json,shutil,subprocess

ROOT=Path('F:/Ourgame');OWN=Path(__file__).resolve().parent
OLD=ROOT/'source-assets/production/fairytale-guard-v001/art-preparation-v001'
ORIG=OLD/'move-leg-rig-seven-components-generation-ready-v001'
CORRECTED=OLD/'move-leg-rig-static-prompts-corrected-v002'
OUT=OWN/'near-far-after-Rest249-context-input-v001'
MEDIA=ROOT/'过程图稿与视频/2026-10-18_裂岩守卫NearFar三件kit共用Rest249比例参考输入_v001'
REST=OWN/'rest1-extraction-v001/run-rest249-shared-HD-v001/curated/frame-0.png'
READY=OLD/'armed-ready4-extraction-v001/run-ready209-shared-HD-v001'
SG=Path('C:/Users/22499/.codex/skills/sprite-gen');PY=SG/'.venv/Scripts/python.exe'

def pin(p):
 b=Path(p).read_bytes();return dict(path=Path(p).as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def write(p,v):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('x',encoding='utf-8',newline='\n') as f:f.write(v if isinstance(v,str) else json.dumps(v,ensure_ascii=False,indent=2)+'\n')
 return p

assert not OUT.exists() and not MEDIA.exists()
assert pin(REST)['sha256']=='a43c1d78446bef50f3a9e0f05b6cbf1ffa83f4bdac606c7e6f50052b1aee7387'
OUT.mkdir(parents=True)
groups=[]
for group,state in [('near3kit','move_near_kit'),('far3kit','move_far_kit')]:
 dst=OUT/group;dst.mkdir();oldrun=ORIG/group/f'run-guard-move-leg-rig-{group}-v001';run=dst/f'run-guard-{group}-Rest249-context-v001'
 request=dst/'official-request-input-exact-v001.json';shutil.copy2(ORIG/group/'standard-request-input-v001.json',request)
 argv=[str(PY),'-B','-X','utf8',str(SG/'scripts/prepare_sprite_run.py'),'--out-dir',str(run),'--character-id','ENM-STN-003-Move-LegRig-PILOT-components-v001','--base-image',str(oldrun/'base-source.png'),'--chroma-key','#FF00FF','--request',str(request)]
 result=subprocess.run(argv,capture_output=True,text=True,encoding='utf-8');log=write(dst/'logs/official-prepare.log',result.stdout+result.stderr)
 prepare=write(dst/'logs/official-prepare-command.json',dict(argv=argv,actual_exit_code=result.returncode,log=pin(log)));assert result.returncode==0
 assert (run/'sprite-request.json').read_bytes()==(oldrun/'sprite-request.json').read_bytes()
 (run/'raw/right').mkdir(parents=True,exist_ok=True);shutil.copy2(READY/'raw/right/idle.png',run/'raw/right/idle.png')
 srcprompt=CORRECTED/group/'native-fullprompt-static-components-v002.txt';before=srcprompt.read_text(encoding='utf-8')
 old='The other attached images are production layout/part-role guides ONLY, not character/style or measured anatomy references.'
 new='The additional extracted Rest249 image is only pelvis/upperbody construction and approximate part-proportion context for the SAME acceptedReady209 identity; it is not a new identity, measured anatomy, motion pose or ground/standing-height reference. The two guide images are layout/role only.'
 assert before.count(old)==1
 prelude='''Reference ownership/order for this static kit: image 1 is accepted ArmedReady209 frame0, the ONLY character/fixedaxe/camera identity and the full-body leg-proportion reference. Image 2 is the actual extracted legless Rest249 component, used ONLY as same-identity pelvis/overlap-construction and approximate part-proportion context. Image 3 is the official three-slot layout. Image 4 is the generic part-role guide. Do not copy the Rest image as a full-body/leg pose or redefine the identity from it. The PNG canvas sizes and alpha-box heights are fitting artifacts, not a common physical scale: do not shorten the legs because Rest is legless, and do not enlarge parts to match image2 canvas bounds. Exact socket pivots, fixed lengths and cross-kit art-unit conversions will be authored from actual reviewed component sources later; no measured anatomy is supplied. Generate only the three expressly named separated limb components below, with one consistent illustration density inside this kit.\n\n'''
 prompt=write(dst/'Root-native-fullprompt-Rest249-context-v001.txt',prelude+before.replace(old,new))
 audit=write(dst/'prompt-minimal-adaptation-audit-v001.json',dict(source_E416_prompt=pin(srcprompt),adapted_prompt=pin(prompt),changes=[dict(kind='prepend',text=prelude),dict(before=old,after=new,count=1)],all_other_E416_prompt_text_preserved=True,request_numbers_and_gates_unchanged=True))
 refs_dir=dst/'references';refs_dir.mkdir();names=[('01-acceptedReady2090.png',READY/'curated/frame-0.png'),('02-Rest249-construction-context.png',REST),('03-official3layout.png',run/f'references/layout-guides/right/{state}.png'),('04-generic-partrole-guide.png',oldrun/f'references/layout-guides/right/{group}-PART-ROLE-PRODUCTION-GUIDE.png')]
 refs=[]
 roles=['ONLY canonical acceptedReady209 body/fixedaxe/camera identity; existing fullbody legs supply appearance and apparent proportions.','Actual extracted leglessRest249 same-identity construction/approximate part-proportion context ONLY; not an identity reset, standing scale, measured hip or final accepted rig.','Official3slot count/spacing/safe padding ONLY.','Generic thigh/shin/foot roles left-to-right ONLY; not character art, physical anatomy or hiddenbone data.']
 for i,(name,source) in enumerate(names):
  dest=refs_dir/name;shutil.copy2(source,dest);refs.append(dict(file=pin(dest),role=roles[i],already_retained=False if i==1 else True))
 refs_path=write(dst/'references-PENDING-Rest-E-source-review-v001.json',dict(references_in_order=refs,not_native_call_ready=True,reason='Rest249 newcurated is pending RootE549 and actualsource review. Root must then retain this entire new F input batch; new fullytrue references JSON must be created only after those facts.'))
 raw=OWN/f'process-batches/2026-10-18-Guard-Move-{group}-native-v001/raw/{state}.png'
 groups.append(dict(group=group,roles=[f'{group[:-4]}_thigh',f'{group[:-4]}_shin',f'{group[:-4]}_foot'],official_prepared_run=run.as_posix(),official_request=pin(run/'sprite-request.json'),prepare=pin(prepare),prompt=pin(prompt),audit=pin(audit),pending_references=pin(refs_path),expected_raw=raw.as_posix(),generated_components=0,call_ready=False,actual_native_id=None))

contract=json.loads((ORIG/'seven-source-components-eighteen-author-markers-and-contact-pilot-contract-v001.json').read_text(encoding='utf-8-sig'))
assert all(v is None for p in contract['parts'] for v in p['artist_markers'].values())
handoff=write(OUT/'Root-Near3-Far3-Rest249-context-preparation-PENDING-v001.json',dict(schema='Guard-NearFar-threepart-Rest249-context-inputs-PENDING-v001',groups=groups,
 Ready209_identity=pin(READY/'curated/frame-0.png'),Rest249_context=pin(REST),Rest249_source_index=pin(OWN/'rest1-extraction-v001/Rest249-single-curated-source-index-v001.json'),
 Root_source_review=None,Rest249_E_retention=None,new_input_E_retention=None,call_ready=False,
 rationale='Reuse correctedE416 static3component specifications. NewRest context helps consistent pelvic cap/upperbody construction without competing wholebody stance; Ready209 remains soleidentity. No motionrow/failedMove/Readyidentity reset.',
 requests_unchanged=True,component_canvas=[512,512],safe_margin=[48,48],min_used_pixels=512,shared_scale_inside_each3kit=True,
 full_18_artist_markers=[dict(part=p['part'],artist_markers=p['artist_markers']) for p in contract['parts']],markers_authored=0,
 actual_leg_lengths=None,actual_crosskit_unit_conversions=None,full_standing_basis=None,
 first_milestone='Two opposite contacts with actualsources/fixedauthorlengths,0/64 of128actualacceptedMovement; no wholebodyMove6/native/footlock claim.',
 native_calls_by_worker=0,actual_Source_Content_tools_ledger_E_modified=False,new_images_viewed=False,TrialAllowed=False,FinalAccepted=False))
write(OUT/'HANDOFF.md','Fresh officialNear3/Far3 prepare exit0; requests remain exactE416 originals,512safe48/min512 unchanged. Only nativeprompt adaptation adds actualRest249 as construction/approximate part-proportion context; canonicalReady209 alone retains identity and fullbody appearance. No actor/ground/hip/length values inferred from leglessRest alpha. Rest-curated/E549/source review and newinputE gate pending: refs deliberately retain Rest already_retained=false and handoff call_ready=false. After actualRootsource decision, write new confirmed refs/handoff; do not edit this pendingfreeze.18author markers/lengths/conversions stillnull. No nativecalls or realSource edits.\n')
freeze=write(OUT/'NearFar-context-pending-input-freeze-v001.json',dict(schema='Guard-NearFar-context-input-PENDING-freeze-v001',files=[pin(p) for p in sorted(OUT.rglob('*')) if p.is_file()],script=pin(__file__),call_ready=False,new_images_viewed=False))
(MEDIA/'原件').mkdir(parents=True);shutil.copytree(OUT,MEDIA/'原件/完整输入包');(MEDIA/'展示副本').mkdir()
for g in groups:
 for p in (OUT/g['group']/'references').iterdir():shutil.copy2(p,MEDIA/'展示副本'/f"{g['group']}-{p.name}")
write(MEDIA/'source-version-status-index.json',dict(schema='F-dated-source-version-status-v001',source=OUT.as_posix(),handoff=pin(handoff),freeze=pin(freeze),files=[pin(p) for p in sorted(MEDIA.rglob('*')) if p.is_file()],status='Prepared only;pendingRestsource/E549 and newinputRootE review; no new native/rig/markers.',call_ready=False,new_images_viewed=False,Root_E_retention_pending=True))
print(json.dumps(dict(F_batch=MEDIA.as_posix(),handoff=pin(handoff),freeze=pin(freeze),groups=groups,call_ready=False),ensure_ascii=False,indent=2))
