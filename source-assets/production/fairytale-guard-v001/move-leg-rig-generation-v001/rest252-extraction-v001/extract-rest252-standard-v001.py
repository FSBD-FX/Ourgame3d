"""Official component extraction/inspect/compose/curate/preview; no generation."""
from pathlib import Path
import hashlib, json, shutil, subprocess, sys, zipfile
import numpy as np
from PIL import Image

R=Path('F:/Ourgame');OWN=R/'source-assets/production/fairytale-guard-v001/move-leg-rig-generation-v001';OUT=Path(__file__).resolve().parent
A=R/'source-assets/production/fairytale-guard-v001/art-preparation-v001';SG=Path('C:/Users/22499/.codex/skills/sprite-gen');PY=SG/'.venv/Scripts/python.exe'
PREP=OWN/'shorter-upperbody-Rest-call-packet-v001';SRC=PREP/'run-guard-shorter-upperbody-rest1-v001';READY=A/'armed-ready4-extraction-v001/run-ready209-shared-HD-v001'
RAW=OWN/'process-batches/2026-10-18-Guard-Move-shorter-upperbody-Rest-native-v001/raw/move_bodyrest.png';RUN=OUT/'run-rest252-shared-HD-v001'
MEDIA=R/'过程图稿与视频/2026-10-18_裂岩守卫短上身Rest252单组件透明提取与身份漂移诊断_v001'
E562=Path('E:/OurGame/Knight/过程图稿与视频/2026-10-18_E562-GuardMove-shorter-Rest252-raw-v001/E-retention-index-v001.json')
assert Path(sys.executable).resolve()==PY.resolve()
assert not RUN.exists() and not MEDIA.exists()

def pin(p):
 b=Path(p).read_bytes();return dict(path=Path(p).as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def write(n,v):
 p=OUT/n;p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('x',encoding='utf-8',newline='\n') as f:f.write(v if isinstance(v,str) else json.dumps(v,ensure_ascii=False,indent=2)+'\n')
 return p
def command(n,args):
 result=subprocess.run(args,capture_output=True,text=True,encoding='utf-8');log=write('logs/'+n+'.log',result.stdout+result.stderr)
 record=dict(argv=args,actual_exit_code=result.returncode,log=pin(log));write('logs/'+n+'-command.json',record);assert result.returncode==0,record;return record

rawpin=pin(RAW);assert rawpin['sha256']=='8f2f5c3c39f9cb98e749c5440e9127a461a32a8cb0a5ed50ad42e90583532bbd' and rawpin['bytes']==1555934
assert Image.open(RAW).mode=='RGB' and Image.open(RAW).size==(1254,1254)
ret=json.loads(E562.read_text(encoding='utf-8-sig'));assert ret['verification_passes']==2 and ret['source_and_member_hash_mismatches']==0
member=next(x for x in ret['files'] if x['sha256']==rawpin['sha256'] and x['bytes']==rawpin['bytes'])
with zipfile.ZipFile(ret['packet']['path']) as z:assert z.read(member['member'])==RAW.read_bytes()
preparedpin=pin(SRC/'sprite-request.json');freezepin=pin(PREP/'shorter-Rest-input-packet-freeze-v001.json')
actualprompt=PREP/'Root-native-shorter-upperbody-Rest1-v001.txt';assert pin(actualprompt)['sha256']=='394b5d0b05068f1802713d4e8034aef51a20287bc38af172ffa61eb9951e9662'
assert any(x['sha256']==pin(actualprompt)['sha256'] for x in ret['files'])
prepare=command('prepare',[str(PY),'-B','-X','utf8',str(SG/'scripts/prepare_sprite_run.py'),'--out-dir',str(RUN),'--character-id','ENM-STN-003-Move-LegRig-shorter-Rest1-candidate-v001','--base-image',str(SRC/'base-source.png'),'--chroma-key','#FF00FF','--request',str(PREP/'official-request-input-v001.json')]);
shutil.copy2(RAW,RUN/'raw/right/move_bodyrest.png');shutil.copy2(READY/'raw/right/idle.png',RUN/'raw/right/idle.png')
shutil.copy2(actualprompt,RUN/'prompts/right/move_bodyrest.txt')
bridge=OUT/'shared-HD-fit-existing-exact.py';shutil.copy2(A/'stomp224-active2-extraction-v001/shared-HD-fit-existing-exact.py',bridge)
commands=[command('extract',[str(PY),'-B','-X','utf8',str(bridge),'--run-dir',str(RUN),'--min-used-pixels','512'])]
commands.append(command('inspect',[str(PY),'-B','-X','utf8',str(SG/'scripts/inspect_sprite_run.py'),'--run-dir',str(RUN),'--states','right_idle,right_move_bodyrest','--report',str(RUN/'inspect-report.json')]))
commands.append(command('compose',[str(PY),'-B','-X','utf8',str(SG/'scripts/compose_sprite_atlas.py'),'--run-dir',str(RUN),'--min-used-pixels','512']))
sys.path.insert(0,str(SG));from sprite_gen.curate.curation import stamp_curation,load_curation,state_plan
from sprite_gen.frames import extract as native
assert load_curation(RUN) is None
payload=stamp_curation(RUN,dict(version=1,kind='sprite-gen-curation',states=dict(right_idle=dict(selected=[0,1,2,3],transforms={}),right_move_bodyrest=dict(selected=[0],transforms={}))))
write(RUN.relative_to(OUT)/'curation.json',payload);assert state_plan(load_curation(RUN),'right_move_bodyrest',1)==([0],{})
commands.append(command('export-curated',[str(PY),'-B','-X','utf8',str(SG/'scripts/export_curated_pngs.py'),'--run-dir',str(RUN),'--state','right_move_bodyrest','--selected-only']))
commands.append(command('preview',[str(PY),'-B','-X','utf8',str(SG/'scripts/preview_animation.py'),'--run-dir',str(RUN)]))
fm=json.loads((RUN/'frames/frames-manifest.json').read_text(encoding='utf-8'));ir=json.loads((RUN/'inspect-report.json').read_text(encoding='utf-8'))
assert fm['ok'] and fm['errors']==fm['warnings']==[]
carried=[]
for i in range(4):
 old=READY/f'frames/right/idle/frame-{i}.png';new=RUN/f'frames/right/idle/frame-{i}.png';assert np.array_equal(np.array(Image.open(old)),np.array(Image.open(new)))
 carried.append(dict(frame=i,accepted=pin(old),reextracted=pin(new),RGBA_equal=True))
p=RUN/'curated/frame-0.png';im=Image.open(p).convert('RGBA');a=np.array(im);assert im.size==(512,512) and np.array_equal(a,np.array(Image.open(RUN/'frames/right/move_bodyrest/frame-0.png')))
al=a[:,:,3];mag=np.all(a[:,:,:3]==[255,0,255],axis=2);box=list(im.getbbox())
keyed=native.remove_chroma_background(Image.open(RAW),(255,0,255),96.,180.,18.,unmix_reach=4,spill_max_fraction=.005);ka=np.array(keyed)[:,:,3]
edges={k:dict(nonzero_alpha_pixels=int((v>0).sum()),core128_pixels=int((v>=128).sum())) for k,v in dict(left=ka[:,0],right=ka[:,-1],top=ka[0,:],bottom=ka[-1,:]).items()}
shared=next(x['shared_row_fit'] for x in fm['rows'] if x['state']=='right_move_bodyrest')
row=dict(component='bodyrest_fixedaxe',source=pin(p),RGBA_sha256=hashlib.sha256(a.tobytes()).hexdigest(),curated_RGBA_equal=True,
 alpha_bbox_COMPONENT_ONLY_NOT_STANDING=box,safe_canvas_margins_ltrb=[box[0],box[1],512-box[2],512-box[3]],
 alpha_nonzero_pixels=int((al>0).sum()),alpha128_pixels=int((al>=128).sum()),alpha255_pixels=int((al==255).sum()),
 pure_magenta_any_alpha=int((mag&(al>0)).sum()),pure_magenta_core128=int((mag&(al>=128)).sum()),
 actual_transparent_View=False,source_pose_or_seam_acceptance=False,
 author_markers=dict(root=None,crown=None,near_hip_socket=None,far_hip_socket=None),full_standing_extent=None,foot_floor=None,component_display_density=None)
index=write('Rest252-single-curated-source-index-v001.json',dict(schema='Guard-Rest252-official-shared-single-source-index-v001',state='right_move_bodyrest',native_source_id=252,
 native_raw=rawpin,native_raw_pixel_size=[1254,1254],native_raw_mode='RGB',raw_retention=dict(index=pin(E562),actual_zip_member_byte_equal=True),
 actual_native_prompt=pin(actualprompt),official_prepared_request=preparedpin,official_prepared_freeze=freezepin,
 components=[row],runtime_animation_frames=0,component_count=1,shared_row_fit=shared,exact_existingReady209_four_RGBA=carried,
 source_outer_edge_checks=edges,source_outer_edges_clear=all(x['nonzero_alpha_pixels']==0 for x in edges.values()),
 QA=dict(extract=fm['ok'],extract_errors=fm['errors'],extract_warnings=fm['warnings'],inspect_ok=ir['ok'],inspect_errors=ir['errors'],inspect_warnings=ir['warnings']),
 source_definition='A new generated legless upperbody/pelvis with fixedaxe, not an exact pixel partition of acceptedReady209 and not a wholebodyMove6.',
 source_pixels_not_painted=True,per_component_frame_normalization=False,
 raw_actual_View_after_E562=True,raw_identity_review=dict(large_oval_eyes=True,thicker_ink=True,identity_accepted=False),new_body_proportions_review_pending=True,
 authority='Component bottom is a generated pelvis/hem boundary, never ground or standingbodyheight. Hip/root/crown marker points remainunmeasured until actual E/View and explicit artist authorship.',
 status='Technical pipeline candidate only; raw eyes became two large amber ovals and outlines grew thicker, identity drift NOT accepted; new transparent source pending Root E retention and actualView. No body-part/rig source acceptance inferred.',
 new_Rest_four_markers_pending_legs_unchanged=True,TrialAllowed=False,FinalAccepted=False,new_images_viewed=False))
proof=write('Rest252-five-step-proof-v001.json',dict(schema='Guard-Rest252-standard-five-step-proof-v001',official_prepare=prepare,commands=commands,source_index=pin(index),
 native_calls=0,source_raw_unchanged=pin(RAW)==rawpin,prepared_request_unchanged=pin(SRC/'sprite-request.json')==preparedpin,
 prepared_freeze_unchanged=pin(PREP/'shorter-Rest-input-packet-freeze-v001.json')==freezepin,Source_Content_tools_ledger_modified=False,new_images_viewed=False))
write('HANDOFF.md','Rest252 official prepare plus standard five steps completed; raw large oval eyes and thicker ink are identity drift, not accepted.  one transparent512 bodyrest component, exact carriedReady2094RGBA. This generated leglesscomponent is not an exactReady source partition and has no shoe floor/standingheight; author marker/density/seam fields remainnull. Raw/E562 ZIP exactbyte comparison recorded. Native static sourcefps1 preview is not locomotion. Newtransparent and preview must be RootRoot E retention retained before View; Do not trial assemble the unchanged Near250/Far251 source kit until actualRootreview decides the new component identity and geometry.  No Source/Content/tools/ledger/E or nativecalls.\n')
freeze=write('Rest252-extraction-freeze-v001.json',dict(schema='Guard-Rest252-standard-extraction-freeze-v001',files=[pin(p) for p in sorted(OUT.rglob('*')) if p.is_file()],new_images_viewed=False,native_called=False,TrialAllowed=False))
(MEDIA/'原件').mkdir(parents=True);shutil.copytree(OUT,MEDIA/'原件/提取包');(MEDIA/'展示副本').mkdir()
for p in (RUN/'qa').iterdir():
 if p.is_file() and p.suffix.lower() in ['.png','.gif']:shutil.copy2(p,MEDIA/'展示副本'/p.name)
shutil.copy2(RUN/'curated/frame-0.png',MEDIA/'展示副本/Rest252-component-SOURCE512.png')
write_media=MEDIA/'source-version-status-index.json';write_media.write_text(json.dumps(dict(schema='F-dated-source-version-status-v001',source=OUT.as_posix(),source_index=pin(index),proof=pin(proof),freeze=pin(freeze),
 files=[pin(p) for p in sorted(MEDIA.rglob('*')) if p.is_file()],status='Unviewed singletransparent source awaiting RootRoot E retention, not rig or runtime acceptance.',Root_E_retention_pending=True,new_images_viewed=False),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(F_batch=MEDIA.as_posix(),source_index=pin(index),proof=pin(proof),freeze=pin(freeze),shared_row=shared,curated=pin(RUN/'curated/frame-0.png'),QA=ir,new_images_viewed=False),ensure_ascii=False,indent=2))
