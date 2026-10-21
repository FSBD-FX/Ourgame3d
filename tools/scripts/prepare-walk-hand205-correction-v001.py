from pathlib import Path
import hashlib,json,shutil,subprocess
R=Path('F:/Ourgame');B=R/'source-assets/production/fairytale-lgt-readability-v003'
O=B/'walk-nearhand-last-correction-v005';assert not O.exists();O.mkdir()
old=B/'walk-nearhand-closed-only-v004/run-nearhand-walk-closed-only-v004'
def desc(p):
 b=p.read_bytes();return dict(path=p.as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def write(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8')
req=json.loads((old/'sprite-request.json').read_text(encoding='utf-8-sig'))
req['character']['id']='fairytale-walk-last-closedhand-correction-v005'
state='sword_walk_nearhand';req['states'][state]['action']='Correct only final back-swing closed gripping hand to actual final cuff direction.'
inp=O/'request-input-v005.json';write(inp,req)
run=O/'run-nearhand-last-correction-v005'
SG=Path('C:/Users/22499/.codex/skills/sprite-gen')
args=[str(SG/'.venv/Scripts/python.exe'),'-B','-X','utf8',str(SG/'scripts/prepare_sprite_run.py'),'--out-dir',str(run),'--character-id',req['character']['id'],'--base-image',str(old/'base-source.png'),'--request',str(inp),'--chroma-key','#00FF00']
r=subprocess.run(args,cwd=R,capture_output=True,text=True,encoding='utf-8');(O/'prepare-v005.log').write_text(r.stdout+r.stderr,encoding='utf-8');assert r.returncode==0,r.stderr
prepared=run/'sprite-request.json';shutil.copy2(prepared,O/'standard-prepared-before-duration-v005.json')
d=json.loads(prepared.read_text(encoding='utf-8-sig'));assert d['chroma_key']['hex']=='#00FF00';d['states'][state]['durations_ms']=[83]*6;write(prepared,d)
refs=run/'references';refs.mkdir(exist_ok=True)
target=refs/'native204-target-six-fists.png';shutil.copy2(old/'raw/sword_walk_nearhand.png',target)
guide=refs/'actual-six-cuff-fragments-direction-only.png';shutil.copy2(B/'walk-cuff-only-guide-v001/原件/walk-cuff-six-tight-UNSCALED-v001.png',guide)
prompt=('EDIT Image1, a six-component horizontal animation row. Image2 is the sole brown glove/closed-grasp identity reference. Image3 has SIX actual original cuff-only fragments, direction/shape guide only. The FINAL fragment in Image3 is the exact target direction for the FINAL hand in Image1.\n\n'
'Correct ONLY the SIXTH/rightmost fist in Image1. It is currently wrong: it points down-right like the third fist. The sixth phase is the BACK SWING, with the wrist at the UPPER-RIGHT side of the hand and the compact closed palm/curled knuckles pointing DOWN-LEFT. Its cuff mouth should be a shallow slightly-down-right slash, like the last cuff fragment in Image3, not the steep down-right-facing wrist currently shown. Make the sixth closed fist and cuff an anatomically coherent brown leather sword grasp facing down-left. Show thumb across curled fingers, no hanging fingers or open palm. Do not mirror the whole sheet, do not produce a right-pointing sixth fist.\n\n'
'Preserve the first FIVE hand components, their orientation, size, ink style, positions and spacing. Preserve exactly six separated fists on one horizontal row, no grid/text/labels. Opaque flat GREEN #00FF00 outside components. Only hands with short cuff, absolutely no forearm/person/helmet/sword/hilt/effects. Keep same physical glove scale; no enlarged sixth hand. A separate sword will later attach through the grip.\n\n'
'Source intervals six83ms; standard shared-row90x90 final512pixel fit. The actual accepted output will curate ONLY this corrected sixth component together with the unmodified earlier five native204 components; preserving other pixels is still requested. No baked handle.\n')
pp=run/'prompts'/f'{state}.txt';pp.write_text(prompt,encoding='utf-8')
row=dict(component='NearHand',runtime_component='NearHand',clip='sword_walk',state=state,run_dir=run.as_posix(),raw_output_path=(run/'raw'/f'{state}.png').as_posix(),prompt=desc(pp),request=desc(prepared),reference_images_in_order=[dict(role='FIRST_EDIT_TARGET_native204_sixfists_only_finalcellchanges',file=desc(target)),dict(role='SECOND_Ready158_closedgrasp_soleidentity',file=desc(run/'base-source.png')),dict(role='THIRD_actualsixcuffs_lastfragment_exactbackswingshape',file=desc(guide))],standard_prepare_exit_code=0,frame_count=6,durations_ms=[83]*6,fit_window_design_px=[90,90],shared_row_scale=True,generation_ready=True,target_mounts_are_measured=False,future_component_A=[None]*6,future_body_target_B=[None]*6,future_integer_delta=[None]*6)
out=O/'walk-nearhand-native-input-approved-v005.json';write(out,dict(schema='Walk6-finalcell-native-correction-input-v005',rows=[row],generation_ready=True,root_review_required_before_generation=False,root_review=dict(actual_E335_native204_viewed=True,actual_E333_cuffguide_viewed=True,index5_direction_rejected=True,only_new_frame5_to_curate=True),formal_complete_units=0))
print(json.dumps({'handoff':str(out),'standard_prepare_exit':0,'references':3,'native_generation_called':False}))
