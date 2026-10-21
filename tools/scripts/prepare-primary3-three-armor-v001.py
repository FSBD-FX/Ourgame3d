from pathlib import Path
from PIL import Image
import hashlib,json,subprocess,sys
R=Path('F:/Ourgame');B=R/'source-assets/production/fairytale-sword-primary3-v001';A=B/'armor-input-v001'
SG=Path('C:/Users/22499/.codex/skills/sprite-gen');assert Path(sys.executable).resolve()==(SG/'.venv/Scripts/python.exe').resolve()
assert not A.exists();A.mkdir()
D=[110,110,60,60,160,160]
def desc(p):
    b=p.read_bytes();return {'path':p.as_posix(),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def write(p,d):
    assert not p.exists();p.parent.mkdir(parents=True,exist_ok=True);p.write_text(d if isinstance(d,str) else json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
sourcefreeze=B/'primary3-extraction-v001/extracted-freeze-v001.json'
assert desc(sourcefreeze)['sha256']=='24542c755d6a31123756249542506392e2d8250fa59fc683b5352cef6a71de38'
for pin in json.loads(sourcefreeze.read_text(encoding='utf-8'))['files']:assert desc(Path(pin['path']))==pin
canon=R/'source-assets/production/fairytale-hero-v001/sprite-run-idle-v002/curated/frame-0.png'
contact=Image.new('RGB',(3072,512),'#eeeeee');sources=[]
for i in range(6):
    p=B/f'run-primary3-v001/curated/frame-{i}.png';sources.append(desc(p))
    with Image.open(p) as im:assert im.size==(512,512) and im.mode=='RGBA';contact.paste(im,(512*i,0),im)
cp=A/'native175-six-original512-contact-v001.png';contact.save(cp)
specs=[
 ('Chest',[70,50],161,'run-chest-ready-v003','central raised round chest boss','Broad compact chest plate, same single raised central circular boss, warm gray metal and brown straps. In phase1 the torso stays upright; phase2 near sleeve crosses the chest; phase3/4 torso leans and arm crosses low. Keep rigid foreshortening and broad collar/belt clearance.'),
 ('NearShoulder',[60,44],162,'run-nearshoulder-ready-v002','central cap washer dark-hole center','Larger near/image-left cap. Phase1 bent upper arm lifts outside helmet, so cap opening turns upward/outward; phase2 upper sleeve sweeps across torso; phase3/4 points down-forward; phase5 returns low. Preserve actual open cap, central washer/hole and volume; do not turn it into a forearm guard or fist.'),
 ('FarShoulder',[32,30],163,'run-farshoulder-ready-v002','small top-strap end rivet, not a central circular boss','Small compressed far/image-right back cap, same top strap and tiny end rivet construction. Never mirror or inflate near cap. Vary opening and flange depth with torso lean. Some phases are later obscured by real body layers, but draw a complete isolated component for every slot. The approved family uses a strap rivet, not a central round face boss.')]
rows=[]
for component,window,native,runold,feature,construction in specs:
    state='armor_'+component.lower()+'_sword_primary3';run=A/f'run-{component.lower()}-primary3-v001'
    margin=[(512-window[0])//2,(512-window[1])//2]
    fit={'pixel_unfake':False,'resample':'lanczos','align_x':'bbox-center','align_y':'bottom','ground_frames':False,'segmentation':'components','shared_row_scale':True}
    seed={'states':{state:{'frames':6,'fps':10,'loop':False,'action':f'Six isolated rigid {component} views matching actual175 third downward-finisher body phases, no body or weapon.'}},'cell':{'width':512,'height':512,'safe_margin_x':margin[0],'safe_margin_y':margin[1]},'fit':fit}
    seedp=A/f'requests/{component}-numeric-input-v001.json';write(seedp,seed)
    argv=[sys.executable,'-B','-X','utf8',str(SG/'scripts/prepare_sprite_run.py'),'--out-dir',str(run),'--character-id',f'fairytale175-{component.lower()}-primary3-v001','--base-image',str(canon),'--description',seed['states'][state]['action'],'--style','Canonical131 grotesque inked fairytale; isolated rigid armor in the retained161162163 same-item construction family.','--cell-size','512','--chroma-key','#00FF00','--request',str(seedp)]
    result=subprocess.run(argv,capture_output=True,text=True,encoding='utf-8');write(A/f'logs/prepare-{component}-v001.log',result.stdout+result.stderr);assert result.returncode==0
    reqp=run/'sprite-request.json';req=json.loads(reqp.read_text(encoding='utf-8'));write(A/f'standard-output/{component}-request-before-explicit-fields.json',req)
    req['fit'].update(fit);req['states'][state]['durations_ms']=D;req['chroma']={'mode':'rgb','unmix_reach':4,'spill_max_fraction':.005};reqp.write_text(json.dumps(req,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    pp=run/f'prompts/{state}.txt';write(A/f'standard-output/{component}-standard-prompt.txt',pp.read_text(encoding='utf-8'))
    family=R/f'source-assets/production/fairytale-armor-sword-ready-v002/{runold}/curated/frame-0.png'
    prompt=f'''Create exactly SIX separated complete standalone {component} light-armor pieces, one horizontal row, not the hero. Same grotesque matte warm-gray painted metal, heavy dark ink and a few broad planes that remain readable on a small72px character. No realistic microtexture.

Reference1 accepted canonical131 is style/identity only. Reference2 is the six actual native175 original512 bodies in phase order and the ONLY motion/perspective authority. Reference3 is the same item's retained Ready{native} construction/material only, not attack geometry or reusable pixels. Reference4 is standard six-slot spacing/count/padding only. Never copy labels or gray guide backgrounds. No old second-cut poses or old coordinates are authority.

{construction}

Actual175 body phases:0 compact low single-hand guard with subtle inward load;1 short bent near arm raised at the outside image-left shoulder beside helmet;2 near sleeve and closed hand sweep forward/down across torso;3 lower down-cut and leaning knees;4 low brake with folded elbow;5 low-guard return. Author six genuinely different rigid perspective/opening views following these poses. Keep the same object/volume across all six, rather than six translated copies, six idle views, local warps, or arbitrary enlargement. Do not clip or leave an obscured phase blank; future source-body partition controls occlusion.

Draw one clear physical feature in every component: {feature}. Its future measured coordinate A is UNKNOWN/null; do not draw point markers, bone joints, sockets or convenient replacement bolts. Source-body cloth attachment targets also remain UNKNOWN in this generation input; registration will be separately measured/designed after extraction. No unmeasured coordinates are claimed authoritative.

Exactly six complete CONNECTED component views with generous gaps on uniform opaque GREEN #00FF00. No body, cloth, helmet, face, eyes, neck, glove, cuff, arm, fingers, legs, boots, sword/handle, other armor, VFX, blur, floor, cast/contact shadow, text, grid or checkerboard. Do not render the reference body under the plate. Do not cut/repaint/rotate/warp Ready pixels into fake new views.

Later512 square cells use a {window[0]}x{window[1]} source-pixel fit ceiling (margins{margin[0]}/{margin[1]}), one shared row scale and unchanged small hero scale. This ceiling is a design envelope, not an accepted fit. Requested six nonlooping kernel durations are110/110/60/60/160/160ms, total660; do not print timing. The standard fps10 shape preview currently yields600ms and does not prove660ms rhythm. No retiming is requested.

The later stack is BodyRest, FarShoulder, Chest, NearArmWithoutHand, NearShoulder, exactHelmet, separateSword, exactNearHand. This request produces only isolated {component} artwork. OriginalRGBA ownership, actual physical-feature measurement, integer registration, body/weapon clearance, mirrored runtime motion, sounds and equipment binding remain separate checks; no final equipment acceptance follows from this row.
'''
    pp.write_text(prompt,encoding='utf-8')
    refs=[('sole_identity_style_131',canon),('only_motion_actual175_six_original512',cp),(f'same_item_Ready{native}_construction_only',family),('standard_count_spacing_only',run/f'references/layout-guides/{state}.png')]
    rows.append({'component':component,'state':state,'run_dir':run.as_posix(),'raw_output_path':(run/f'raw/{state}.png').as_posix(),'prompt':desc(pp),'request':desc(reqp),'reference_images_in_order':[{'role':role,'file':desc(p)} for role,p in refs],'standard_prepare_exit_code':0,'target_mounts_are_measured':False,'future_feature_A':[None]*6,'future_cloth_targets':[None]*6,'fit_window_design_px':window,'feature_contract':feature,'durations_ms':D,'generation_scope':f'One six-view isolated {component} row for actual175 Primary3 downward finisher; no body/weapon. Unknown physical A and body targets until later review.'})
handoff=A/'primary3-three-armor-input-draft-v001.json';write(handoff,{'generation_ready':False,'root_review_required_before_generation':True,'rows':rows,'source175_frames':sources,'source175_extraction_freeze':desc(sourcefreeze),'native_called':False,'external_api_calls':0,'formal_complete_units':0})
files=sorted(p for p in A.rglob('*') if p.is_file());freeze=A/'preparation-freeze-v001.json';write(freeze,{'files':[desc(p) for p in files],'generation_ready':False,'new_images_viewed':False,'formal_complete_units':0})
print(json.dumps({'handoff':desc(handoff),'freeze':desc(freeze),'standard_prepares':3,'source_body_feature_targets_known':False},ensure_ascii=False))
