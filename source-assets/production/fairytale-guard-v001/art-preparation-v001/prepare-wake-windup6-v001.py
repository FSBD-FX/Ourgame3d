"""Two independent standard nextrows from acceptedArmedReady209 alone; no generation."""
from pathlib import Path
from datetime import datetime
import hashlib,json,subprocess,shutil,sys
import numpy as np
from PIL import Image
HERE=Path(__file__).resolve().parent;ROOT=Path('F:/Ourgame');SG=Path('C:/Users/22499/.codex/skills/sprite-gen');PY=SG/'.venv/Scripts/python.exe'
OLD=HERE/'armed-ready4-extraction-v001/run-ready209-shared-HD-v001';READY=OLD/'curated/frame-0.png'
OUT=HERE/'wake6-and-axe-windup6-generation-ready-v001';MEDIA=ROOT/'过程图稿与视频/2026-10-18_裂岩守卫Wake6与斧蓄力6标准输入_v001'
assert Path(sys.executable).resolve()==PY.resolve();OUT.mkdir(exist_ok=False);assert not MEDIA.exists()
def pin(p):
 b=p.read_bytes();return {'path':p.as_posix(),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def write(n,v):
 p=OUT/n;p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('x',encoding='utf-8',newline='\n') as f:f.write(v if isinstance(v,str) else json.dumps(v,ensure_ascii=False,indent=2)+'\n')
 return p
def command(n,args):
 r=subprocess.run(args,capture_output=True,text=True,encoding='utf-8');log=write('logs/'+n+'.log',r.stdout+r.stderr);rec={'argv':args,'actual_exit_code':r.returncode,'log':pin(log)};write('logs/'+n+'-command.json',rec);assert r.returncode==0,rec;return rec
rp=pin(READY);assert rp['sha256']=='54df5fe718a98e1568513193dbde479aff6fd393d623755feb77813cacb4e804'
COPY=OUT/'accepted209-anchor-readcopy';COPY.mkdir()
for rel in ['sprite-request.json','curation.json']:shutil.copyfile(OLD/rel,COPY/rel)
shutil.copytree(OLD/'frames',COPY/'frames')
anchorcmd=command('anchor-acceptedReady209',[str(PY),'-B','-X','utf8','-m','sprite_gen.cli','anchor','--run-dir',str(COPY),'--direction','right','--scale','1'])
ANCHOR=COPY/'references/anchors/right-anchor-x1.png';im=Image.open(READY);assert np.array_equal(np.asarray(im.crop(im.getbbox())),np.asarray(Image.open(ANCHOR)))
q=json.loads((HERE/'action-contracts-v002-fixed-axe-whole/next-Wake6-AxeWindup6-AxeFollow6-native-action-drafts-v001.json').read_text(encoding='utf-8'));D={r['state']:r for r in q['rows']}
style='Match attached acceptedArmedReady209 identity exactly: the SAME broad squat slabhelmet/stonebody, small recessedambereyes, sparseolivepauldronmoss, thickirregularink and SAME fixed singleheadedheavyaxe/straightwoodshaft/stonebuttcap. Body and axe identity belong only to this accepted equippedanchor. Broad warmgrey/tan stoneplanes, reduce tinyspots, no photorealgrain/pixelgrid/vectorgloss.'
carry='CARRIED acceptedArmedReady209 four existing right_idle frames. This is the existing equipmentdirectionanchor row; do NOT generate it or spend a newcall. Source raw andcuratedreferences are copied exact from frozenReady209. New nativecalls target only the namedaction row.'
handoffs=[]
for STATE,label in [('right_wake','wake6'),('right_axe_windup','axe-windup6')]:
 run=OUT/f'run-guard-{label}-v001';draft=D[STATE]
 action=draft['action_prompt']+' Keep all6 complete body+axe silhouettes separate inside their invisiblecells, feet at commonsolebaseline. Pose compression is real motion, not rescaledbody. Never allow horizontalaxeextent to shrink thebody versusanchor; use coherentpose/camera withcompleteweapon visible. No stepping/roottranslation duringthisrow.'
 request={'cell':{'shape':'square','width':512,'height':512,'safe_margin_x':48,'safe_margin_y':48},'states':{'right_idle':{'frames':4,'fps':4,'loop':True,'action':carry},STATE:{'frames':6,'fps':6,'loop':False,'action':action}},'directions':{'set':['right'],'mirror':{'left':'right'}},'style':style,'motion_phase_guides':False,'fit':{'pixel_unfake':False,'resample':'lanczos','align_x':'bbox-center','align_y':'bottom','ground_frames':True,'segmentation':'components','shared_row_scale':True}}
 inp=write(label+'/standard-request-input-v001.json',request)
 prep=command('prepare-'+label,[str(PY),'-B','-X','utf8',str(SG/'scripts/prepare_sprite_run.py'),'--out-dir',str(run),'--character-id','ENM-STN-003-fixed-heavyaxe-armed-v001','--base-image',str(ANCHOR),'--chroma-key','#FF00FF','--request',str(inp)])
 req=run/'sprite-request.json';prepared=json.loads(req.read_text(encoding='utf-8'));assert set(prepared['states'])=={'right_idle',STATE};write(label+'/standard-prepared-before-duration.json',prepared)
 prepared['states']['right_idle']['durations_ms']=[250]*4;prepared['states'][STATE]['durations_ms']=draft['durations_ms_NATIVE_ART_MAPPING'];req.write_text(json.dumps(prepared,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 # Already-generatedanchor row is carried through the declared SG request, never re-generated.
 carried=run/'raw/right/idle.png';carried.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(OLD/'raw/right/idle.png',carried)
 prompt=run/('prompts/right/wake.txt' if STATE=='right_wake' else 'prompts/right/axe_windup.txt');oldtext=prompt.read_text(encoding='utf-8');write(label+'/standard-original-before-camera-override.txt',oldtext)
 fixed=oldtext.replace('pure side profile view facing camera-right','same shallow elevated three-quarter side view as acceptedArmedReady209, facing screen-right; not pure90-degree profile')
 assert fixed!=oldtext and 'pure side profile view facing camera-right' not in fixed
 prompt.write_text(fixed,encoding='utf-8',newline='\n')
 guide=run/('references/layout-guides/right/wake.png' if STATE=='right_wake' else 'references/layout-guides/right/axe_windup.png')
 shutil.copyfile(ANCHOR,run/'references/accepted-ArmedReady209-anchor-x1.png')
 refs=write(label+'/native-helper-references-ready-v001.json',{'references_in_order':[{'file':pin(run/'references/accepted-ArmedReady209-anchor-x1.png'),'role':'Only canonical acceptedArmedReady209 fullbody+fixedaxe identity/direction, E363Rootinternal lock. Standardcuratedanchor1x exactalpha-bboxcrop; no206base/207neutral/independent208 attached.','already_retained':True},{'file':pin(guide),'role':'Standard6slot layout/count/spacing/safepadding only; newguide requiresRootEretention beforeView/nativegeneration.','already_retained':True}]})
 expected=run/('raw/right/wake.png' if STATE=='right_wake' else 'raw/right/axe_windup.png')
 mapping=write(label+'/native-art-time-sampling-v001.json',{'state':STATE,'frames':6,'kernel_clock':draft['clock_authority'],'durations_ms_NATIVE_ART_MAPPING':draft['durations_ms_NATIVE_ART_MAPPING'],'sample_start_ms':draft['sample_start_ms'],'native_span_ms':1000,'SG_preview':{'fps':6,'uniform_duration_ms_per_frame':167,'total_ms':1002,'label':'Uniformstandardpreviewonly, not native1000ms timing. compose_atlas currently ignores requestdurationoverride; do not pretend exactnativeclock.'},'gameplay_modified':False})
 hand=write(label+'/Root-native-generation-ready-v001.json',{'schema':'Guard-armed-next-state-standard-generation-ready-v001','state':STATE,'frames':6,'run_dir':run.as_posix(),'prompt':pin(prompt),'references_json':pin(refs),'request':pin(req),'output':expected.as_posix(),'source_acceptedReady0':rp,'anchor_derivation':{'command':anchorcmd,'pixel_equal_to_curated_alpha_bbox_crop':True,'scale':1},'existing_idle_carry':{'raw':pin(carried),'source':pin(OLD/'raw/right/idle.png'),'frame_count':4,'not_generated_or_charged':True,'later_extraction_proof':'Samechroma/sharedfit/canvas must exactlyreconstruct the accepted4RGBA beforehandoff. Targetrow plus existingidle row formsindependentrun.'},'standard_prepare':prep,'timing':pin(mapping),'camera_only_override_original_preserved':True,'old206_207_208_refs_attached':False,'new_guide_viewed':False,'generation_owner':'Rootserialreserve maydispatch Wake andWindup nativecalls concurrently after bothinputsretained; no callsbyworker','retention_gate':'Refs already_retainedtrue intendedforpost-Einputbatch use; newguide currentlyunviewed/unretained.','Follow_dependency':'AxeFollow6 waitsactualacceptedWindup raw+curated basis; notincludedhere.','runtime_or_final_art_accepted':False})
 handoffs.append({'state':STATE,'handoff':pin(hand),'prompt':prompt.as_posix(),'references':refs.as_posix(),'output':expected.as_posix()})
assert pin(READY)==rp
write('Root-Ready209-internal-lock-and-next-two-rows-v001.json',{'authority':'RootafterE363 actualtransparentall4View explicitReady0internallock','acceptedReady0':rp,'not_final_aesthetic_dynamic_runtime_acceptance':True,'worker_view':'ActualReady0transparent afterE363; bodycrown/coretop49, nearsolecoremax463/farsole455; shallow3/4closedtwohandheldaxe. No axecrop.','standing_body_crown_to_nearsole_extent_px_candidate':415,'displaygroundpivot_artist_candidate_xy':[256,464],'displaypivot_not_bone_or_footlock':True,'crown_source_ROI_measurement':'corealpha>=128 withinx190..310/y<90; nearsolerange x80..215/y>420. ROIextrema diagnosevisiblebodylandmarks, axeexcluded.','source_density_role':'One standingbodybasis forfuturepresentation; target100.8pxinitialcandidate. Never normalizeeachposeheight orwholehorizontalaxealphaextent.','future_identity_refs':'acceptedReady209only; no206/207neutral/208propagain.','next_rows':handoffs})
write('HANDOFF.md','Two independent standardgenerationreadyinputs: Wake6 andAxeWindup6, eachonly acceptedArmedReady209 materializedcuratedanchor +own6slotguide. Rootserialreserve thenmayconcurrentnative2calls. Existingright_idle4 raw iscarriedexactinto eachrun and mustnotregenerate; laterstandardextractionproves accepted4RGBA unchanged. No base206/207neutral/standalone208refs. Follow waitsrealWindupbasis. Both1000msnative; SG6fpspreview1002ms explicitlyseparate. Bodydensity/crownsolebasis fromReady0, horizontalaxeextentcannotshrinkbody. Allnewguides unviewed untilRootE. No native/UE/Source/tools changes.\n')
write('preparation-freeze-v001.json',{'schema':'Guard-Wake6-AxeWindup6-generation-input-freeze-v001','files':[pin(p) for p in sorted(OUT.rglob('*')) if p.is_file()],'acceptedReady_source_unchanged':True,'native_calls':0,'new_guides_viewed':False})
(MEDIA/'原件').mkdir(parents=True);shutil.copytree(OUT,MEDIA/'原件/标准输入包');(MEDIA/'展示副本').mkdir()
for label,rel in [('wake6','wake'),('axe-windup6','axe_windup')]:shutil.copyfile(OUT/f'run-guard-{label}-v001/references/layout-guides/right/{rel}.png',MEDIA/f'展示副本/{label}-layout.png')
with (MEDIA/'来源-版本-状态索引.json').open('x',encoding='utf-8',newline='\n') as f:json.dump({'date':'2026-10-18','topic':'裂岩守卫Wake6与斧蓄力6标准输入','version':'v001','status':'two-independent-standard-inputs-unviewed','source':OUT.as_posix(),'handoffs':handoffs,'files':[pin(p) for p in sorted(MEDIA.rglob('*')) if p.is_file()]},f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps({'canonical_media':MEDIA.as_posix(),'handoffs':handoffs},ensure_ascii=False,indent=2))
