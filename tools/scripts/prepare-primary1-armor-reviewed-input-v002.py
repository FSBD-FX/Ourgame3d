"""Root's explicit hidden registration choices; do not convert them into facts."""
from pathlib import Path
import hashlib,json
R=Path('F:/Ourgame');B=R/'source-assets/production/fairytale-armor-sword-primary1-v001'
def desc(p):
 b=p.read_bytes();return {'path':p.as_posix(),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def new(p,v):
 assert not p.exists(),p
 p.parent.mkdir(parents=True,exist_ok=True)
 p.write_text(v if isinstance(v,str) else json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
draft=B/'primary1-macro-native-handoff-draft-v001.json'
assert desc(draft)['sha256']=='7c63c053340167c81e00ef5e485734ac696b809e07175a9dd2c11258f43c1638'
d=json.loads(draft.read_text(encoding='utf-8-sig'))
choices={'schema':'root-primary1-hidden-registration-design-v2','author':'root','source_body_request':159,
 'source_visible_measurements_unchanged':True,'future_actual_component_A_still_unknown':True,
 'hidden_body_target_measurement_remains_null':True,
 'trial_targets':[{'component':'Chest','phase':2,'trial_body_A':[268,270],'source_px_uncertainty':8,'kind':'Root design choice behind crossing forearm; not observed cloth/rivet/bone'},
                  {'component':'Chest','phase':3,'trial_body_A':[269,276],'source_px_uncertainty':8,'kind':'Root design choice at lowered torso/front-arm area; not observed hidden joint'},
                  {'component':'FarShoulder','phase':2,'trial_body_A':[308,268],'source_px_uncertainty':10,'kind':'Root back-shoulder design choice behind crossing near arm; not an observed rivet'}],
 'registration_policy':'After native extraction, measure actual visible component boss/washer/topstrap features. Integer translation only into separately labelled trial body targets. Review all poses in real layer stack before accepting fit.',
 'layer_stack':['BodyRest','FarShoulder','Chest','NearArmWithoutHand','NearShoulder','HelmetForeground','independentSword','NearHand'],
 'helmet_layer_policy':'Exact original159 helmet/eyes/topknob/ink+AA pixels, exclusive owner, no new painting; draw before sword and after caps. This does not legitimize a wrong cap shape.',
 'root_viewed_existing_E168_guides':3,'root_viewed_actual159_original512_phases':[2,3],
 'generation_ready_is_input_review_only':True,'full_motion_or_equipment_accepted':False,'formal_complete_units':0}
decision=B/'root-hidden-registration-design-v002.json';new(decision,choices)
identity='Canonical131 is the sole character/style identity. Ref2 actual159 six-body poses is the only pose/depth/order authority. Ref3 is the corresponding retained Ready armor component0: keep the SAME metal object construction, material, silhouette language and scale family. Ref4 is a technical body guide only; its null labels honestly mark hidden/unmeasured cloth points and must not be copied into the art. Ref5 gives SIX horizontal slots/count only.'
specific={
 'Chest':'The SAME compact broad chestplate as reference3: warm gray metal, restrained dark edge, short shoulder straps, one clearly raised ROUND CENTRAL boss. The small side strap bolts are not the central boss. Maintain the approximate broad1.4–1.5:1 plate family. It lies over the torso behind the near forearm; do not bake a hand, arm, collar or belt into it. In phases2 and3 show the whole independent rigid plate as it is oriented on that torso; later real near-arm pixels occlude it. Do not cut an arm-shaped hole or replace it with a blank slot.',
 'NearShoulder':'The SAME near shoulder shell as reference3, with its central front washer/dark round mounting hole, coarse turned rim and short top strap. Follow the actual upper sleeve: phase1 has the near arm raised toward image LEFT, so genuinely redraw the shell projection and rim direction for that raised upper arm; phase2 arm crosses forward, phase3 points down. Keep a compact low top strap; the original helmet will be in front at the overlap, but do not use this to justify a giant misplaced shell. Avoid a flat strap plate or big heavy squared pauldron.',
 'FarShoulder':'The SAME short compressed far shoulder shell as reference3, with the actual little TOP STRAP rivet used in the explicitly new163 trial. Keep that physical feature identifiable, connected to the shell, and the far shell distinctly shorter/narrower than the near shell. Do not invent a central front boss or mirrored near shell. In phase2 it is behind the crossing near arm; output its whole independent rigid shape in the correct depth projection, not a blank slot or baked limb.'}
limits={'Chest':(70,50),'NearShoulder':(60,44),'FarShoulder':(30,28)}
for row in d['rows']:
 c=row['component'];w,h=limits[c]
 prompt=f'''Generate ONE production source row for a hand-drawn grotesque fairytale 2.5D game: exactly SIX isolated connected {c} armor views in a single horizontal row on flat opaque saturated GREEN #00FF00. Clear gaps, no grid or labels. This is a new row of the same armor object fitted to the six actual159 first-sword-cut body poses, not six random item designs.

REFERENCE ROLES: {identity}

OBJECT IDENTITY: {specific[c]}

POSE ORDER:0 low sword guard entry;1 loading/backswing with near arm raised out toward imageLEFT;2 the forward cut with near forearm crossing the torso;3 the low downward follow-through with near forearm descending across the torso;4 return toward the low guard;5 low guard exit.0/4/5 share the same rigid object construction and similar orientation. Preserve plausible rigidity; minor orientation changes are allowed, not rubber breathing, stretched metal, new camera views or arbitrary ornament drift. Phase1/2/3 must reflect the actual changed body/upper-arm orientation. Keep the character facing imageRIGHT in every phase; no local mirrored phase.

STYLE/SCALE: match reference3 warm-gray matte metal, broad simple planes, chunky dark ink and restrained warm edges. No tiny decorative detail added. The planned common extraction window for this component is at most{w}x{h} at the original512 body-source canvas; body display stays72px. One shared scale for the whole row, not separate normalization of each piece. Foreshortened views can be smaller. Keep the same item construction and preserve the independent feature used for measurement.

OUTPUT: ONLY six {c} components, each one connected opaque metal/strap object, one per slot. No body, cloth, helmet, face, glowing eye, neck, sleeve, cuff, hand, finger, sword/handle, boot, other armor, shadow, scenery, UI, text, marks, checkerboard or transparent/background tricks. Do not copy the technical colors or labels. Components must be new drawings for these poses, not cut-and-moved Ready pixels. Do not hide difficult phases as blanks.

REGISTRATION: the actual component attachment feature coordinates are unknown until extraction. Some torso points under the arm remain unmeasured; root's separate TRIAL choices (not bones or observations) are chestphase2[268,270], chestphase3[269,276], farphase2[308,268]. These guide later placement only and must not appear in the output. Native output does not grant fit approval. Future composition is BodyRest>FarShoulder>Chest>NearArmWithoutHand>NearShoulder>originalHelmetForeground>separateSword>NearHand; no body pixels baked into this component.

Six source phases correspond to85/85/60/60/155/155ms, total600ms non-looping. The image is six shapes; the game will sample actual combat phases, not a separate animation timer. Keep all six components fully inside the image with clear green padding.
'''
 p=B/f'prompts/{c.lower()}-primary1-reviewed-v002.txt';new(p,prompt)
 row['prompt']=desc(p);row['generation_ready']=True;row['target_mounts_are_measured']=False
 row['future_component_A']=[None]*6;row['root_hidden_targets_are_design_only']=True
 row['helmet_foreground_is_original_source_layer']=True
 for ref in row['reference_images_in_order']:assert desc(Path(ref['file']['path']))==ref['file']
 assert row['standard_prepare_exit_code']==0 and not Path(row['raw_output_path']).exists()
d['schema']='root-reviewed-native159-primary1-three-armor-rows-input-v2'
d['root_design_decisions']=desc(decision);d['prior_frozen_draft']=desc(draft)
d['generation_ready_is_not_fit_acceptance']=True
handoff=B/'primary1-macro-native-handoff-reviewed-v002.json';new(handoff,d)
helper=(R/'tools/scripts/native-fairytale-armor-ready-v002.py').read_text(encoding='utf-8-sig')
helper=helper.replace("fairytale-armor-sword-ready-v002","fairytale-armor-sword-primary1-v001")
helper=helper.replace('Canonical131 identity and actual158 pose; independent macro armor component Ready4 only. Actual component mount/fit/runtime/full equipment states remain unaccepted','Canonical131 identity and actual159 six Primary1 poses; independent macro armor component six only. Explicit hidden body targets are trial designs, not measured joints. Actual component A, all fit/motion/equipment states remain unaccepted')
helper=helper.replace("files=[handoff,prompt,request_path,control/f'ledger-before-request{number}.json',after,Path(__file__)]", "files=[handoff,prompt,Path(document['root_design_decisions']['path']),request_path,control/f'ledger-before-request{number}.json',after,Path(__file__)]")
tool=R/'tools/scripts/native-fairytale-armor-primary1-v001.py';compile(helper,str(tool),'exec');new(tool,helper)
new(B/'root-reviewed-input-freeze-v002.json',{'files':[desc(p) for p in [Path(__file__),decision,handoff,tool,*sorted((B/'prompts').glob('*reviewed-v002.txt'))]],'native_called':False,'formal_complete_units':0})
print(json.dumps({'reviewed_handoff':desc(handoff),'decision':desc(decision),'helper':desc(tool),'rows':3,'generation_ready':True,'fit_accepted':False},ensure_ascii=False))
