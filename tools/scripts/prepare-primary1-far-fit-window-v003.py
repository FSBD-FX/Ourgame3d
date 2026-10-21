"""Explicit new common far-cap extent, same native167 bytes; old RED preserved."""
from pathlib import Path
import copy,hashlib,json,subprocess,shutil
R=Path('F:/Ourgame');B=R/'source-assets/production/fairytale-armor-sword-primary1-v001'
def desc(p):
 b=p.read_bytes();return {'path':p.as_posix(),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def new(p,v):
 assert not p.exists(),p
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(v if isinstance(v,str) else json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
old=B/'run-farshoulder-primary1-v002/raw/armor_shoulder_far_sword_primary1.png';assert desc(old)['sha256']=='c51acdb26481672b9022882ab8ead56f09c3b8b6ce10526b75f09b1a7141d3a9'
q=json.loads((B/'requests/farshoulder-numeric-input-v001.json').read_text(encoding='utf-8-sig'))
q['cell'].update(safe_margin_x=240,safe_margin_y=241)
q['chroma']={'mode':'rgb','unmix_reach':4,'spill_max_fraction':.005}
for state in q['states'].values():state['durations_ms']=[85,85,60,60,155,155]
recipe=B/'requests/farshoulder-numeric-input-v003.json';new(recipe,q)
d=json.loads((B/'primary1-far-correction-native-handoff-v003.json').read_text(encoding='utf-8-sig'));row=d['rows'][0]
run=B/'run-farshoulder-primary1-v003';assert not run.exists()
cmd=copy.deepcopy(row['standard_prepare_command']);cmd[cmd.index('--out-dir')+1]=str(run);cmd[cmd.index('--character-id')+1]='fairytale-native159-armor-farshoulder-fit32x30-v003';cmd[cmd.index('--request')+1]=str(recipe)
out=subprocess.run(cmd,capture_output=True,text=True,encoding='utf-8',errors='replace');new(B/'far-fit32x30-prepare-v003.log',out.stdout+out.stderr);assert out.returncode==0
request=run/'sprite-request.json';actual=json.loads(request.read_text(encoding='utf-8-sig'));actual['chroma']=q['chroma']
for state in actual['states'].values():state['durations_ms']=[85,85,60,60,155,155]
request.write_text(json.dumps(actual,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
raw=run/'raw'/old.name;raw.parent.mkdir(exist_ok=True);shutil.copy2(old,raw);assert desc(raw)['sha256']==desc(old)['sha256']
report=B/'far-fit32x30-design-v003.json';new(report,{'schema':'root-common-display-extent-design-v3','source_native_request':167,'source':desc(old),'new_raw_exact_copy':desc(raw),'old_extent':[30,28],'new_common_extent':[32,30],
 'reason':'EV048 requests stronger armor/silhouette at fixed72px body. Original common30x28 extraction made oblique phase2 smaller than the legitimate pixel-area gate and visually small far cap remains weak. Use a separately versioned modestly wider/taller whole-row trial, preserving every native pose proportion. No individual pose scaling.',
 'old_identity_failed_native166_preserved':True,'old_30x28_native167_QA_RED_preserved':True,'QA_threshold_changed':False,'native_pixels_repainted_or_warped':False,'shared_scale_all6':True,'hidden_body_targets_remain_design_not_bones':True,'future_integer_mounts_not_yet_measured':True,'runtime_fit_accepted':False,'formal_complete_units':0})
new(B/'far-fit32x30-input-freeze-v003.json',{'files':[desc(x) for x in [Path(__file__),recipe,request,run/'base-source.png',run/'references/layout-guides/armor_shoulder_far_sword_primary1.png',raw,report,B/'far-fit32x30-prepare-v003.log']], 'status':'new deterministic whole-row32x30 trial; same native167, no additional generation, extraction pending','formal_complete_units':0})
print(json.dumps({'run':run.as_posix(),'raw':desc(raw),'recipe':desc(request),'design':desc(report),'new_native_calls':0,'QA_changed':False}))
