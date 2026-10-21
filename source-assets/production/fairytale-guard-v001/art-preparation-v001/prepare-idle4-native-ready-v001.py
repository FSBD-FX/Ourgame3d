"""Root body lock206 permits standard Idle4 preparation; no native call or UE edits."""
from pathlib import Path
from datetime import datetime
import subprocess,json,hashlib,shutil,sys
import numpy as np
from PIL import Image

ROOT=Path('F:/Ourgame');HERE=Path(__file__).resolve().parent
OUT=HERE/'idle4-generation-ready-v001';RUN=OUT/'run-guard-right-idle-v001'
SG=Path('C:/Users/22499/.codex/skills/sprite-gen');PY=SG/'.venv/Scripts/python.exe'
BASE=ROOT/'source-assets/production/fairytale-guard-v001/identity-native206-v001/raw/guard-body-identity.png'
MEDIA=ROOT/'过程图稿与视频/2026-10-18_裂岩守卫206锁定与Idle4标准输入_v001'
assert Path(sys.executable).resolve()==PY.resolve()
def pin(p):
 b=p.read_bytes();return {'path':p.as_posix(),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def write(name,data):
 p=OUT/name;p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('x',encoding='utf-8',newline='\n') as f:f.write(data if isinstance(data,str) else json.dumps(data,ensure_ascii=False,indent=2)+'\n')
 return p
OUT.mkdir(exist_ok=False);assert not MEDIA.exists()
assert pin(BASE)['sha256']=='38e2c0b36c8da4f50d8f4caf0e5373fc8c0d057dd2f884926d69cca0dd3cb172'
basepin=pin(BASE);sys.path.insert(0,str(SG))
from sprite_gen.frames.extract import remove_chroma_background,extract_component_images
raw=Image.open(BASE);assert raw.size==(1254,1254) and raw.mode=='RGB'
keyed=remove_chroma_background(raw,(255,0,255),96.,180.,18.,unmix_reach=4,spill_max_fraction=.005)
components=extract_component_images(keyed,1);assert components and len(components)==1
a=np.asarray(keyed);al=a[:,:,3];core=al>=128;bb=keyed.getbbox();assert bb
w,h=bb[2]-bb[0],bb[3]-bb[1];shared_scale=min(416/w,416/h,1.)
sample_xy=[430,415];sample=a[sample_xy[1],sample_xy[0]].tolist();assert sample[3]>=128
measurement=write('identity206-alpha-numeric-measurement-v001.json',{'schema':'Guard206-native-alpha-measurement-NUMERIC-ONLY-v001','source':basepin,'Root_retention_before_view':'E350 bothSHA0; Rootexplicit baseLock=y; worker viewed actual original after permission.','source_canvas':list(raw.size),'source_mode':raw.mode,'key':'#FF00FF','method':'Installed SHA-pinned native remove_chroma_background+one connected component in memory. No derived image published or local drawing.','tool':pin(SG/'sprite_gen/frames/extract.py'),'component_count':len(components),'nonzero_alpha_pixels':int((al>0).sum()),'core128_pixels':int(core.sum()),'partial_alpha_pixels':int(((al>0)&(al<255)).sum()),'foreground_bbox_DIAGNOSTIC_NOT_LANDMARK':list(bb),'foreground_extent_px':[w,h],'projected_shared512_safe48_scale_PROPOSAL':shared_scale,'projected_extent_px_PROPOSAL':[round(w*shared_scale),round(h*shared_scale)],'target_visible_height_px_ART_CANDIDATE':100.8,'target_hero_height_px':72,'ratio_ART_CANDIDATE':1.4,'projected_canvas_if_416px_foreground_height':100.8*512/416,'moss_material_sample_not_joint':{'source_xy':sample_xy,'actual_keyed_RGBA':sample},'visible_ground_pivot_crown_nearGrip_farGrip_bones':None,'identity_lock_role':'Internal production baseline only; not user aesthetic/runtime acceptance.','shared_row_scale_policy':'ONE scale for all4 Idle cells; future rows preserve same canonical body height/density via measured basis. No per-frame normalization; new raw proportions must be checked.','existing_kernel_collision_unchanged_half_world':[40,28],'current_camera_body_projected_width_depth_px':[52,21.28]})
style='Match locked206 stone Guard silhouette, slab helmet, small recessed amber eyes, shoulder moss, broad warm-grey stone planes and coarse irregular black ink exactly. Body-only, no axe. Avoid adding small chips/speckles or photoreal grain; retain a few large readable planes per plate. Not pixel art, no grids/dots/vector gloss.'
action='Four distinct quiet alert-idle BODY-ONLY poses facing RIGHT. Feet planted at one common sole line, no steps or travel. Small heavy torso load settle only; stone is not rubber. Same two closed stone fists held low near the belly with same hand gap; thumbs wrap closed fingers in every frame. No axe/shaft/blade/item, no open palm. Keep helmet eye window/moss identity and original short limbs. Frame0 neutral, frame1 tiny knee/shoulder weight compression, frame2 gentle opposite shoulder settle, frame3 returns near frame0 for a clean loop. No dust, shadows, glows, text, detached effects or extra bodies.'
q={'cell':{'shape':'square','width':512,'height':512,'safe_margin_x':48,'safe_margin_y':48},'states':{'right_idle':{'frames':4,'fps':4,'loop':True,'action':action}},'directions':{'set':['right'],'mirror':{'left':'right'}},'style':style,'motion_phase_guides':False,'fit':{'pixel_unfake':False,'resample':'lanczos','align_x':'bbox-center','align_y':'bottom','ground_frames':True,'segmentation':'components','shared_row_scale':True}}
inp=write('standard-request-input-v001.json',q)
argv=[str(PY),'-B','-X','utf8',str(SG/'scripts/prepare_sprite_run.py'),'--out-dir',str(RUN),'--character-id','ENM-STN-003-fairytale-guard-body-v001','--base-image',str(BASE),'--chroma-key','#FF00FF','--request',str(inp)]
r=subprocess.run(argv,capture_output=True,text=True,encoding='utf-8');log=write('standard-prepare-v001.log',r.stdout+r.stderr);assert r.returncode==0,(r.returncode,r.stderr)
qp=RUN/'sprite-request.json';before=write('standard-prepared-before-duration-v001.json',json.loads(qp.read_text(encoding='utf-8')))
prepared=json.loads(qp.read_text(encoding='utf-8'));assert prepared['states']['right_idle']['frames']==4 and prepared['fit']['shared_row_scale'] is True and prepared['chroma_key']['rgb']==[255,0,255]
# Explicit known prepare whitelist drops duration fields. Add artist Idle timing only; native clocks remain untouched.
prepared['states']['right_idle']['durations_ms']=[250]*4
qp.write_text(json.dumps(prepared,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
prompts=list((RUN/'prompts').rglob('*.txt'));guides=list((RUN/'references/layout-guides').rglob('*.png'));assert len(prompts)==len(guides)==1
assert pin(BASE)==basepin and pin(RUN/'base-source.png')['sha256']==basepin['sha256']
lock=write('Root-identity206-base-lock-v001.json',{'schema':'RootGuard206-base-lock-v001','source':basepin,'lock':'y','authority':'Root explicit collaboration message2026-10-18 afterE350 before actualView.','internal_only':True,'not_user_final_art_acceptance':True,'review':'Complete full body right-facing, wide short stone slabs, amber eyes, closed coarse fists, sparse moss and coarse ink match existing hero. Surface speckles a little dense; do not add detail inrows.','accepted_idle_row_yet':False,'base_reference_next_allowed_use':'Idle4 only, pre-idle generation. After acceptedIdle4 freeze/curation, futureWake/attack rows use acceptedIdle anchor; do not reattach206base.'})
handoff=write('Root-next-native-idle4-generation-ready-v001.json',{'schema':'GuardIdle4-standard-generation-ready-v001','Root_next_native_id_suggestion':207,'generation_calls_by_this_worker':0,'run_dir':RUN.as_posix(),'state':'right_idle','request':pin(qp),'prompt':pin(prompts[0]),'raw_output_expected':(RUN/'raw/right/idle.png').as_posix(),'reference_images_in_order':[{'file':pin(RUN/'base-source.png'),'role':'Rootlocked206 canonical body identity PRE-IDLE only'},{'file':pin(guides[0]),'role':'Prepared exact4slots layout/safe margins only; never copy boxes/grid to finalraw'}],'standard_prepare':{'argv':argv,'actual_exit_code':r.returncode,'log':pin(log)},'before_duration':pin(before),'duration_diff':{'path':'states.right_idle.durations_ms','before':None,'after':[250]*4,'meaning':'Artist idle loop1s, no fixed kernelIdle deadline.'},'source_lock':pin(lock),'numeric_alpha_measurement':pin(measurement),'frame_count':4,'body_only':True,'no_weapon_or_guessed_grip':True,'requires_Root_E_retention_before_any_new_guide_View':True,'new_guide_viewed':False,'accepted_or_imported':False,'next_gate':'Rootnative207→canonical/E retention→actual row review→shared standardextract/inspect/curate/motion review→acceptedIdle anchor. Only then prepareWake/Axe rows.'})
write('HANDOFF.md','Root206 internal bodyLock=y (E350). Standardprepare actualexit0 createsright_idle4 body-only,512safe48,magenta,sharedrow. References exact206 base then4slot guide. ArtistIdle250msx4; no kernel change. Newguide unviewed: E retain canonical media beforeView. Raw output expectedraw/right/idle.png. This worker makes no generation/API/UE calls. After acceptedIdle4, actions must usecuratedIdle identity instead of206 base. Fullground/grip/crown/bones remainnull until actualcuratedpixels measured.\n')
write('preparation-freeze-v001.json',{'schema':'GuardIdle4-generation-ready-freeze-v001','files':[pin(p) for p in sorted(OUT.rglob('*')) if p.is_file()],'source206_unchanged':pin(BASE)==basepin,'new_guide_viewed':False,'native_generation_calls':0})
(MEDIA/'原件').mkdir(parents=True);shutil.copytree(OUT,MEDIA/'原件/标准输入包');(MEDIA/'展示副本').mkdir()
shutil.copyfile(guides[0],MEDIA/'展示副本'/guides[0].name)
with (MEDIA/'来源-版本-状态索引.json').open('x',encoding='utf-8',newline='\n') as f:json.dump({'date':'2026-10-18','topic':'裂岩守卫206锁定与Idle4标准输入','version':'v001','status':'generation-ready-guide-unviewed','source':OUT.as_posix(),'handoff':pin(handoff),'files':[pin(p) for p in sorted(MEDIA.rglob('*')) if p.is_file()]},f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps({'handoff':pin(handoff),'canonical_media':MEDIA.as_posix(),'alpha_bbox':list(bb),'shared512_scale_proposal':shared_scale,'raw_expected':(RUN/'raw/right/idle.png').as_posix(),'guide_viewed':False},ensure_ascii=False,indent=2))
