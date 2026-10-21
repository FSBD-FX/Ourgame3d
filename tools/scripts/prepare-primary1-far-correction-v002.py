"""New native Far row input: retain failed166, use actual163 raw as identity."""
from pathlib import Path
import copy, hashlib, json, subprocess
R=Path('F:/Ourgame'); B=R/'source-assets/production/fairytale-armor-sword-primary1-v001'
S=Path('C:/Users/22499/.codex/skills/sprite-gen')
def desc(p):
 b=p.read_bytes();return {'path':p.as_posix(),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def new(p,v):
 assert not p.exists(),p
 p.parent.mkdir(parents=True,exist_ok=True)
 p.write_text(v if isinstance(v,str) else json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
h=B/'primary1-macro-native-handoff-reviewed-v002.json'; d=json.loads(h.read_text(encoding='utf-8-sig'))
row=copy.deepcopy(next(x for x in d['rows'] if x['component']=='FarShoulder'))
run=B/'run-farshoulder-primary1-v002';assert not run.exists()
cmd=copy.deepcopy(row['standard_prepare_command'])
cmd[cmd.index('--out-dir')+1]=str(run)
cmd[cmd.index('--character-id')+1]='fairytale-native159-armor-farshoulder-v002'
out=subprocess.run(cmd,capture_output=True,text=True,encoding='utf-8',errors='replace')
new(B/'far-correction-prepare-v002.log',out.stdout+out.stderr);assert out.returncode==0
req=run/'sprite-request.json'; q=json.loads(req.read_text(encoding='utf-8-sig'))
q['states'][row['state']]['durations_ms']=[85,85,60,60,155,155]
req.write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
raw163=R/'source-assets/production/fairytale-armor-sword-ready-v002/run-farshoulder-ready-v002/raw/armor_shoulder_far_sword_ready.png'
prompt=Path(row['prompt']['path']).read_text(encoding='utf-8')
prompt=prompt.replace('Ref3 is the corresponding retained Ready armor component0:', 'Ref3 is the full-resolution retained native163 Ready far-shoulder row with FOUR existing views (identity only, not output count):')
prompt += '\nCORRECTION PRIORITY: Reference3 is the ONLY far-shell construction authority. It has ONE little rivet on its TOP LEATHER STRAP and NO circular washer, hole, eye, boss or disk on the broad front metal face. The broad metal face must remain plain shaded metal with the existing restrained crease. Keep this top-strap-only construction in ALL SIX new poses. Do not copy a central round disk from the character helmet or the near shoulder. Output exactly SIX new FarShoulder views, not the FOUR reference views. This deliberately corrects failed native166; native166 is not a reference.\n'
p=B/'prompts/farshoulder-primary1-correction-v003.txt';new(p,prompt)
row.update(run_dir=run.as_posix(),raw_output_path=(run/'raw'/f"{row['state']}.png").as_posix(),prompt=desc(p),standard_prepare_command=cmd,standard_prepare_exit_code=0,standard_request=desc(req),generation_ready=True)
row['reference_images_in_order'][2]={'role':'actual_native163_far_shell_topstrap_only_identity_four_views_not_output_count','file':desc(raw163)}
row['reference_images_in_order'][4]['file']=desc(run/'references/layout-guides'/f"{row['state']}.png")
row['prior_native166_identity_passed']=False
row['new_guide_explicitly_viewed']=False
d.update(schema='root-primary1-far-correction-input-v3',rows=[row],generation_ready=True,native_called=False,native_request_reserved=False,new_guides_explicitly_viewed=False,prior_frozen_handoff=desc(h))
handoff=B/'primary1-far-correction-native-handoff-v003.json';new(handoff,d)
new(B/'far-correction-input-freeze-v003.json',{'files':[desc(x) for x in [Path(__file__),handoff,p,req,run/'base-source.png',run/'references/layout-guides'/f"{row['state']}.png",B/'far-correction-prepare-v002.log']], 'status':'new input, not generated or fit-accepted','formal_complete_units':0})
print(json.dumps({'handoff':desc(handoff),'run':run.as_posix(),'prepare_exit':out.returncode,'failed166_preserved':True}))
