"""204 closed NearHand six-source extraction; fit and actual grips remain unaccepted."""
from pathlib import Path
from datetime import datetime
import importlib.util,json,hashlib,sys,shutil
import numpy as np
from PIL import Image,ImageDraw,ImageFont
HERE=Path(__file__).resolve().parent;FAMILY=HERE.parent;ROOT=Path('F:/Ourgame');OLD=FAMILY/'walk-leather-extraction-v001'
spec=importlib.util.spec_from_file_location('walk_tools',OLD/'extract-walk-leather-v001.py');t=importlib.util.module_from_spec(spec);spec.loader.exec_module(t)
assert Path(sys.executable).resolve()==t.PYTHON.resolve();t.OUT=HERE;t.WATCHED={}
SOURCE=FAMILY/'walk-nearhand-closed-only-v004/run-nearhand-walk-closed-only-v004';STATE='sword_walk_nearhand'
ap=SOURCE.parent/'walk-nearhand-native-input-approved-v004.json';a=json.loads(ap.read_text(encoding='utf-8'));assert t.pin(ap)['sha256']=='a3d2b322e997ad39f74d05828f4a30992311c9a27d2b6bee2c5275764352040b'
rp=FAMILY/'generation-control-v001/generation-receipt204-v001.json';r=json.loads(rp.read_text(encoding='utf-8'));assert t.pin(SOURCE/f'raw/{STATE}.png')==r['canonical_raw'];assert r['canonical_raw']['sha256']=='54ddc46a1b611012e8d3bd0315f80c5dcaebfdbf44383188a300f6eb8c1e0bf5'
assert r['source_handoff']==t.pin(ap) and a['rows'][0]['request']==t.pin(SOURCE/'sprite-request.json')
q=json.loads((SOURCE/'sprite-request.json').read_text(encoding='utf-8'));assert q['chroma_key']['rgb']==[0,255,0] and q['states'][STATE]['durations_ms']==[83]*6 and q['fit']['pixel_unfake'] is False and q['fit']['shared_row_scale'] is True
assert q['cell']['width']-2*q['cell']['safe_margin_x']==q['cell']['height']-2*q['cell']['safe_margin_y']==90
for p in [ap,rp,SOURCE.parent/'standard-prepared-before-durations-v004.json']:t.copy_exact(p,HERE/'original-input'/p.name)
bridge=FAMILY/'primary3-leather-extraction-v001/shared-HD-fit-explicit-component-min-v001.py';t.copy_exact(bridge,HERE/'shared-HD-fit-existing-exact.py')
runs=[];export=None
for mode in ['standard-baseline','shared-HD']:
 run=HERE/f'run-hand204-{mode}-v001'
 for rel in [f'raw/{STATE}.png','sprite-request.json','base-source.png',f'prompts/{STATE}.txt']:t.copy_exact(SOURCE/rel,run/rel)
 argv=[str(t.PYTHON),'-B','-X','utf8',str(t.SG/'scripts/extract_sprite_row_frames.py' if mode=='standard-baseline' else HERE/'shared-HD-fit-existing-exact.py'),'--run-dir',str(run)]
 if mode=='shared-HD':argv+=['--min-used-pixels','512']
 ex=t.command(f'extract-hand204-{mode}-v001',argv)
 ins=t.command(f'inspect-hand204-{mode}-v001',[str(t.PYTHON),'-B','-X','utf8',str(t.SG/'scripts/inspect_sprite_run.py'),'--run-dir',str(run),'--states',STATE,'--report',str(run/'inspect-report.json')])
 assert ex['actual_exit_code']==ins['actual_exit_code']==0
 fm=json.loads((run/'frames/frames-manifest.json').read_text(encoding='utf-8'));entry={'mode':mode,'extract':ex,'inspect':ins,'frames_manifest':t.pin(run/'frames/frames-manifest.json'),'shared_row_fit':fm['rows'][0].get('shared_row_fit'),'inspect_warnings':json.loads((run/'inspect-report.json').read_text(encoding='utf-8'))['warnings']};runs.append(entry)
 if mode=='shared-HD':
  co=t.command('compose-hand204-shared-HD-v001',[str(t.PYTHON),'-B','-X','utf8',str(t.SG/'scripts/compose_sprite_atlas.py'),'--run-dir',str(run),'--min-used-pixels','512']);assert co['actual_exit_code']==0;entry['compose']=co
  cm=json.loads((run/'manifest.json').read_text(encoding='utf-8'));assert cm['animation']['rows'][STATE]['durations_ms']==[83]*6
  export=t.curate_shared_run(run,STATE);entry['curated_export']=export;shared=run
font=ImageFont.load_default(size=13);rows=[];close=np.zeros((256,384,4),dtype=np.uint8)
for i,m in enumerate(export['metrics']):
 p=Path(m['source']['path']);im=Image.open(p);arr=np.asarray(im);bg=Image.new('RGBA',(608,608),(28,31,35,255));bg.alpha_composite(im,(48,48));ov=Image.new('RGBA',(608,608),(0,0,0,0));d=ImageDraw.Draw(ov)
 for v in range(0,513,16):
  major=v%64==0;d.line([(48+v,48),(48+v,560)],fill=(60,210,220,80 if major else 27),width=1);d.line([(48,48+v),(560,48+v)],fill=(60,210,220,80 if major else 27),width=1)
  if major:d.text((v+38,28),str(v),fill='white',font=font);d.text((12,v+41),str(v),fill='white',font=font)
 d.text((48,7),f'204 CLOSED HAND {i} | source512; xy=shown-48',fill='white',font=font)
 d.text((48,575),'Cuff/grip NOT assigned; frame5 wrist direction TRIAL.',fill='white',font=font)
 gp=HERE/'measurement-guides'/f'frame-{i}-source-coordinate-grid-v001.png';gp.parent.mkdir(exist_ok=True);Image.alpha_composite(bg,ov).save(gp)
 crop=arr[192:320,192:320];close[(i//3)*128:(i//3+1)*128,(i%3)*128:(i%3+1)*128]=crop
 rows.append({'frame':i,'duration_ms':83,**m,'source_grid':t.pin(gp),'visible_cuff_seam_A_candidate':None,'visible_knuckle_crease_candidate':None,'weapon_grip_artist_design_candidate':None,'actual_hidden_wrist_bone':None,'target_body_B':None,'integer_delta':None,'reason_actual_points_pending':'New final512/grid must be E-retained before actual feature inspection; no bbox center or scaledraw guessed landmark.','wrist_fit_accepted':False,'risk':'index5 cuff-to-fist direction may conflict with oldback arm; translation cannot correct orientation.' if i==5 else 'Closed fist semantic pass is not actual weapon grasp or bodyfit acceptance.'})
cp=HERE/'measurement-guides/hand204-six-close-UNSCALED-sourceRect192-320-v001.png';Image.fromarray(close).save(cp)
idx=t.write('hand204-six-source-index-v001.json',{'schema':'Walk204-closed-NearHand-six-source-extraction-v001','rows':rows,'frame_count':6,'source_raw':t.pin(SOURCE/f'raw/{STATE}.png'),'source_approved':t.pin(ap),'receipt':t.pin(rp),'shared_fit':runs[1]['shared_row_fit'],'source_close_contact':t.pin(cp),'close_contact_coordinates':'3x2 cropped128 cells, every originalRGBA copied; source coords=local+192. No scale/new landmark.','fit_grip_or_full_motion_accepted':False,'new_outputs_viewed':False,'new_composite_body_target_pending':True,'202_203_rejected_hands_not_extracted':True})
proof=t.write('extraction-proof-v001.json',{'schema':'Walk204-hand-extraction-proof-v001','runs':runs,'source_index':t.pin(idx),'standard_compose_durations_ms':[83]*6,'timing_note':'498ms sequence metadata vs nominalfps12 period500ms; no runtime sync claim.','old_body_source_modified':False,'new_body_composite_assembled':False,'new_outputs_viewed':False,'all_source_AB_null_pending_actual_feature_review':True})
t.write('HANDOFF.md','204 six closed NearHand source candidates, standardextract/inspect/compose/curated actualexit0; shared90x90/HD one scale, lowmotion retained. Unknown actual cuff/grip/bone/bodyB/delta remainnull until RootE retained grids/finalsource allow actual feature view. Closecontact unscaled crop[192,192,320,320] per frame0..5; sourcexy=local+192. Frame5 wristdirection TRIAL; do not accept fullfit or actualSwordgrasp. Source/raw/oldBody/SourceUE/tools/ledger unchanged, no newoutput View.\n')
for p,b in t.WATCHED.items():assert t.pin(p,False)==b
files=[t.pin(p,False) for p in sorted(HERE.rglob('*')) if p.is_file()]
for d in files:d['path']=Path(d['path']).relative_to(HERE).as_posix()
f=t.write('extraction-freeze-v001.json',{'schema':'Walk204-six-closed-hand-extraction-freeze-v001','files':files,'new_outputs_viewed':False,'fit_or_grasp_accepted':False,'frame_count':6})
print(json.dumps({'freeze':t.pin(f),'index':t.pin(idx),'proof':t.pin(proof),'closecontact':t.pin(cp),'sharedscale':runs[1]['shared_row_fit']['scale'],'warnings':[x['inspect_warnings'] for x in runs]},ensure_ascii=False,indent=2))
