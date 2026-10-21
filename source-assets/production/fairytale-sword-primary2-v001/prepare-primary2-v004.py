"""Prepare a single targeted native edit of phase1's open near hand; no call."""
from pathlib import Path
import hashlib,json,shutil,subprocess,sys
R=Path(__file__).resolve().parent;SG=Path('C:/Users/22499/.codex/skills/sprite-gen');RUN=R/'run-primary2-v004';STATE='sword_primary_2'
def desc(p):
    b=p.read_bytes();return {'path':p.as_posix(),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def write(p,x):
    assert not p.exists(),p;p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(x if isinstance(x,str) else json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');return p
assert Path(sys.executable).resolve()==(SG/'.venv/Scripts/python.exe').resolve() and not RUN.exists()
identity=R/'sources-v003/canonical131-idle0.png';target=R/'run-primary2-v003/raw/sword_primary_2.png'
assert desc(target)['sha256']=='6963752d95b58592d7b736088904879e8811dd207d268272e4ab4e3cee9a6bdd'
seed=json.loads((R/'requests/primary2-numeric-input-v003.json').read_text(encoding='utf-8'))
seed['states'][STATE]['action']='Edit native170 six-body row: only close the open near hand in the second pose; preserve bent-arm rising-cut motion and identity.'
seedpath=write(R/'requests/primary2-numeric-input-v004.json',seed)
argv=[sys.executable,'-B','-X','utf8',str(SG/'scripts/prepare_sprite_run.py'),'--out-dir',str(RUN),
    '--character-id','fairytale-common-hero-sword-primary2-v004','--base-image',str(identity),
    '--description',seed['states'][STATE]['action'],'--style','Exact accepted131 grotesque bell helmet and charcoal short body; native170 motion unchanged.',
    '--cell-size','512','--safe-margin','48','--chroma-key','#00FF00','--request',str(seedpath)]
proc=subprocess.run(argv,capture_output=True,text=True,encoding='utf-8');write(R/'logs/standard-prepare-v004.log',proc.stdout+proc.stderr);assert proc.returncode==0
request=RUN/'sprite-request.json';q=json.loads(request.read_text(encoding='utf-8'))
write(R/'standard-output/sprite-request-before-explicit-timing-v004.json',q)
q['states'][STATE]['durations_ms']=[75,75,60,60,135,135];q['fit'].update(seed['fit']);q['chroma']={'mode':'rgb','unmix_reach':4,'spill_max_fraction':.005}
request.write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
prompt='''Edit the exact SIX-POSE horizontal body-only strip in reference1. Reference1 is the actual edit target, native170. Reference2 is the accepted canonical131 identity only. Reference3 confirms exactly six slots. Preserve all six pose positions, the bent short elbows and low-to-high wrist motion, body/helmet scale, view, clothing, palette, dark outlines, both boots, far balancing hands, spacing and flat GREEN #00FF00 background.

ONE TARGETED CORRECTION: In the SECOND complete body from the LEFT, the NEAR hand on the image-LEFT side currently hangs open with loose fingers beside the rear hip. Replace only that open near glove/hand with a CLOSED CYLINDRICAL SWORD GRASP. Keep it low beside the same hip and connected naturally to the same brown cuff and short forearm. Curl four fingers inward; show one separate opposing brown thumb wrapping over the curled fingers. A narrow side-view grip, not an open reaching hand, claw, pointing index finger or flat boxing knuckle front. Leave that pose's image-RIGHT far balancing hand relaxed and open. Do not confuse the two hands.

No visible held object: no sword, handle, hilt, pommel, stick, cylinder, colored plug or black stump emerging from the fist. The empty curved glove and thumb alone imply a future separate grip. No other pose redesign. Especially preserve the genuinely low bent elbow in pose3 and the upward wrist/forearm in pose4, rather than replacing them with horizontal punches. Retain the closed near grasps of the other five poses, continuous wrist/cuff, and canonical head/eyes. Do not add armor, other limbs, new camera angles, motion blur, slash trails, floor/shadows, text, grids or disconnected marks.

Output the corrected six-full-body horizontal strip only, opaque flat pure GREEN #00FF00 between the six separated figures. All top knobs, hands and feet remain inside the row; keep equal invisible slots and generous gaps. No per-pose zoom/resize/recentering or restyling. This is a raw source edit; downstream standard shared-row extraction and actual anatomy/continuity review still determine acceptance. Preserve the visual motion; do not print timing or labels.
'''
pp=RUN/f'prompts/{STATE}.txt';write(R/'standard-output/primary2-standard-prompt-v004.txt',pp.read_text(encoding='utf-8'));pp.write_text(prompt,encoding='utf-8')
refs=[('edit_target_native170_six_pose_row',target),('sole_identity_canonical131',identity),('standard_six_slot_layout_only',RUN/f'references/layout-guides/{STATE}.png')]
review=write(R/'root-input-review-v005.json',{'fact':'Root reviewed E204 raw and all six E205 source frames: phase1 near hand is open; native170 bent elbow/rising wrist improved169.',
    'inference':'One targeted edit of only that near grasp is appropriate before new grip measurement and armor generation.',
    'risk':'Native edit may drift other pixels; do not assume pixel-identical preservation. New source must be re-extracted and reviewed. No motion acceptance.',
    'native_generation_ready':True,'source_event':'EV-048','authorization':['EV-040','EV-041'],'reference_files':[desc(p) for _,p in refs]})
h=write(R/'handoffs/primary2-native-input-root-reviewed-v005.json',{'generation_ready':True,'root_review_required_before_generation':False,'root_input_review':desc(review),
    'rows':[{'component':'SwordPrimary2Body','state':STATE,'run_dir':RUN.as_posix(),'raw_output_path':(RUN/'raw'/f'{STATE}.png').as_posix(),
    'prompt':desc(pp),'request':desc(request),'reference_images_in_order':[{'role':role,'file':desc(p)} for role,p in refs],
    'standard_prepare_exit_code':0,'target_mounts_are_measured':False,'generation_scope':'One native170 phase1 near-hand closure edit; body-only six, preserved short-elbow rising action; all new features and motion remain unaccepted.'}],
    'formal_complete_units':0})
A=Path('F:/Ourgame/过程图稿与视频/2026-10-16_军剑上挑蓄力闭合握姿输入_v004');assert not A.exists();(A/'原件').mkdir(parents=True);(A/'展示副本').mkdir()
files=[Path(__file__),seedpath,request,pp,review,h,*[p for _,p in refs]];entries=[]
for i,p in enumerate(files):
    t=A/'原件'/f'{i:02d}-{p.name}';shutil.copy2(p,t);assert p.read_bytes()==t.read_bytes();entries.append({'source':desc(p),'copy':desc(t)})
shutil.copy2(target,A/'展示副本/native170-edit-target.png');shutil.copy2(refs[-1][1],A/'展示副本/six-slot-layout.png')
write(A/'index.json',{'files':entries,'status':'targeted phase1 near-hand correction input; target already reviewed E204/205, no call yet',
    'new_slot_guide_pending_view':True,'formal_complete_units':0})
write(A/'README.md','170六帧原图为edit target，仅修第二帧近侧张开手的闭合握姿；先E保留新槽图后调用。标准prepare与原始请求/提示词/版本索引保留，不接受自动保持像素的假设，也未导入或验收动作。\n')
print(json.dumps({'handoff':desc(h),'archive':A.as_posix()},ensure_ascii=False))
