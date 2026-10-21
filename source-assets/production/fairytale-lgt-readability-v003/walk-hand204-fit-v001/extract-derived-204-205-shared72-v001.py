"""Root-authorized exact six source-cell curation, then ONE shared72 extraction."""
from pathlib import Path
from datetime import datetime
import hashlib,importlib.util,json,shutil,sys
import numpy as np
from PIL import Image,ImageDraw,ImageFont

ROOT=Path('F:/Ourgame');FAMILY=ROOT/'source-assets/production/fairytale-lgt-readability-v003';HERE=Path(__file__).resolve().parent
OUT=HERE/'2026-10-18-derived204205-shared72-phase-b-v001';STATE='sword_walk_nearhand'
MEDIA=ROOT/'过程图稿与视频/2026-10-18_Walk204205统一72提取候选_v001'
SRC204=FAMILY/'walk-nearhand-closed-only-v004/run-nearhand-walk-closed-only-v004'
SRC205=FAMILY/'walk-nearhand-last-correction-v005/run-nearhand-last-correction-v005'
SG=Path('C:/Users/22499/.codex/skills/sprite-gen');PY=SG/'.venv/Scripts/python.exe'
assert Path(sys.executable).resolve()==PY.resolve()
spec=importlib.util.spec_from_file_location('walk_extract_existing',FAMILY/'walk-leather-extraction-v001/extract-walk-leather-v001.py');t=importlib.util.module_from_spec(spec);spec.loader.exec_module(t);t.OUT=OUT;t.WATCHED={}
OUT.mkdir(exist_ok=False);assert not MEDIA.exists()
raws={204:SRC204/f'raw/{STATE}.png',205:SRC205/f'raw/{STATE}.png'}
assert t.pin(raws[204])['sha256']=='54ddc46a1b611012e8d3bd0315f80c5dcaebfdbf44383188a300f6eb8c1e0bf5'
assert t.pin(raws[205])['sha256']=='e724e8e6466450518a2cd77ab357beae9e1c5c10da6b09dad0f5b1bf36b4ad30'
images={n:Image.open(p) for n,p in raws.items()}
for im in images.values():assert im.mode=='RGB' and im.size==(2172,724)
derived=Image.new('RGB',(2172,724),(0,255,0));cells=[]
for i in range(6):
 n=204 if i<5 else 205;rect=(362*i,0,362*(i+1),724);cell=images[n].crop(rect);derived.paste(cell,(362*i,0))
 cells.append({'frame':i,'native_request':n,'source_raw':t.pin(raws[n]),'source_rect_ltrb_exclusive':list(rect),'source_cell_RGB_sha256':hashlib.sha256(np.asarray(cell).tobytes()).hexdigest(),'crop_paste_only':True,'resampled_mirrored_rotated_painted':False})
run=OUT/'run-derived204205-shared72-v001';rawout=run/f'raw/{STATE}.png';rawout.parent.mkdir(parents=True);derived.save(rawout)
actual=Image.open(rawout);assert actual.mode=='RGB' and actual.size==(2172,724)
for c in cells:
 rect=c['source_rect_ltrb_exclusive'];src=np.asarray(images[c['native_request']].crop(rect));dst=np.asarray(actual.crop(rect))
 c['derived_cell_RGB_sha256']=hashlib.sha256(dst.tobytes()).hexdigest();c['RGB_pixel_mismatch_count']=int(np.any(src!=dst,axis=2).sum());assert c['RGB_pixel_mismatch_count']==0
q=json.loads((SRC204/'sprite-request.json').read_text(encoding='utf-8-sig'));oldq=json.loads(json.dumps(q))
q['character']['id']='walk-crossnative204205-unified-shared72-candidate-v001'
q['cell']['safe_margin_x']=q['cell']['safe_margin_y']=q['cell']['safe_margin']=220
assert q['cell']['width']-2*q['cell']['safe_margin_x']==q['cell']['height']-2*q['cell']['safe_margin_y']==72
q['project_curation_source_cells']=cells;q['project_raw_role']='Exact RGB source cell curation: 204 cells0..4 +205 cell5. ONE shared row72 extraction.'
q['states'][STATE]['durations_ms']=[83]*6
t.write(run.relative_to(OUT)/'sprite-request.json',q)
t.copy_exact(SRC204/'base-source.png',run/'base-source.png')
for n,source in [(204,SRC204),(205,SRC205)]:
 for rel in ['sprite-request.json',f'prompts/{STATE}.txt']:
  t.copy_exact(source/rel,OUT/f'original-input/native{n}'/rel)
t.write(run.relative_to(OUT)/f'prompts/{STATE}.txt','CURATION/EXTRACTION ONLY; no generation call. Exact RGB source selection204[0..4]+205[5], request shared fit72x72. Original paid-generation prompts preserved under original-input.\n')
bridge=FAMILY/'walk-hand204-extraction-v001/shared-HD-fit-existing-exact.py';t.copy_exact(bridge,OUT/'shared-HD-fit-existing-exact.py')
request_diff=t.write('new-working-request-diff-v001.json',{'authorization':'Root explicit 2026-10-18: preserve90; NEW unified shared72 request; six exact native sourcecells, then ONE shared extraction.','original_204_request':t.pin(SRC204/'sprite-request.json'),'new_request':t.pin(run/'sprite-request.json'),'before_cell':oldq['cell'],'after_cell':q['cell'],'frames_per_frame_rescale':False,'native_generation_calls':0,'original_source_requests_changed':False})
curationproof=t.write('derived-raw-six-source-cells-RGB-proof-v001.json',{'schema':'Walk204205-exact-sourcecell-curation-v001','derived_raw':t.pin(rawout),'native_source_pins':[t.pin(p) for p in raws.values()],'source_cell_size':[362,724],'cells':cells,'all_six_cell_RGB_mismatches':0,'single_extraction_row':True,'request_diff':t.pin(request_diff)})
extract=t.command('extract-crossnative204205-shared72-v001',[str(PY),'-B','-X','utf8',str(OUT/'shared-HD-fit-existing-exact.py'),'--run-dir',str(run),'--min-used-pixels','512']);assert extract['actual_exit_code']==0
inspect=t.command('inspect-crossnative204205-shared72-v001',[str(PY),'-B','-X','utf8',str(SG/'scripts/inspect_sprite_run.py'),'--run-dir',str(run),'--states',STATE,'--report',str(run/'inspect-report.json')]);assert inspect['actual_exit_code']==0
compose=t.command('compose-crossnative204205-shared72-v001',[str(PY),'-B','-X','utf8',str(SG/'scripts/compose_sprite_atlas.py'),'--run-dir',str(run),'--min-used-pixels','512']);assert compose['actual_exit_code']==0
export=t.curate_shared_run(run,STATE)
fm=json.loads((run/'frames/frames-manifest.json').read_text(encoding='utf-8'));shared=fm['rows'][0]['shared_row_fit'];assert len({f['shared_scale'] for f in shared['frame_records']})==1
cm=json.loads((run/'manifest.json').read_text(encoding='utf-8'));assert cm['animation']['rows'][STATE]['durations_ms']==[83]*6
font=ImageFont.load_default(size=13);close=np.zeros((256,384,4),np.uint8);rows=[];grids=[]
for i,m in enumerate(export['metrics']):
 p=Path(m['source']['path']);im=Image.open(p);a=np.asarray(im);close[(i//3)*128:(i//3+1)*128,(i%3)*128:(i%3+1)*128]=a[192:320,192:320]
 bg=Image.new('RGBA',(608,608),(27,29,32,255));bg.alpha_composite(im,(48,48));draw=ImageDraw.Draw(bg)
 for k in range(0,513,16):
  draw.line([(48+k,48),(48+k,560)],fill=(60,200,210,70 if k%64==0 else 25),width=1);draw.line([(48,48+k),(560,48+k)],fill=(60,200,210,70 if k%64==0 else 25),width=1)
  if k%64==0:draw.text((38+k,29),str(k),fill='white',font=font);draw.text((12,41+k),str(k),fill='white',font=font)
 draw.text((48,7),f'72 SHARED HAND {i} | native{cells[i]["native_request"]} | xy=shown-48',fill='white',font=font);draw.text((48,578),'Visible cuff/Grip A remains null until E-retained actual512 review.',fill='white',font=font)
 gp=OUT/'measurement-guides'/f'hand72-{i}-source512-grid-v001.png';gp.parent.mkdir(exist_ok=True);bg.save(gp);grids.append(gp)
 rows.append({'frame':i,'duration_ms':83,'native_source_cell':cells[i],**m,'grid':t.pin(gp),'visible_cuff_seam_A':None,'matching_body_cuff_B':None,'knuckle_candidate':None,'Grip_artist_design_candidate':None,'integer_delta':None,'hidden_wrist_bone':None,'fit_accepted':False})
cp=OUT/'measurement-guides/hand72-six-UNSCALED-sourceRect192-320-v001.png';Image.fromarray(close).save(cp)
idx=t.write('hand204205-shared72-source-index-v001.json',{'schema':'Walk-crossnative204205-shared72-source-index-v001','source_curation':t.pin(curationproof),'rows':rows,'frame_count':6,'one_shared_row_scale':shared,'frame_timing_ms':[83]*6,'actual_cuff_or_grip_fit_accepted':False,'new_outputs_viewed':False,'old90_preserved':True})
proof=t.write('extraction-proof-v001.json',{'schema':'Walk-crossnative204205-shared72-actual-command-proof-v001','extract':extract,'inspect':inspect,'compose':compose,'export':export,'source_index':t.pin(idx),'shared_row_fit':shared,'native_generation_calls':0,'new_source204205_curated_cells':True,'new_outputs_viewed':False})
for p,old in t.WATCHED.items():assert t.pin(p,False)==old
t.write('HANDOFF.md','Exact rawRGB six-cell curation2040..4+2055; all6 RGB mismatch0. ONE native shared-row component extraction, shared72 fit, inspect/compose/curated exit0. No per-frame scale. All source art/old90 unchanged; new A/B/Grip pending actual512 review. Not imported or accepted. Root must retain canonical media E before view.\n')
t.write('extraction-freeze-v001.json',{'schema':'Walk-crossnative204205-shared72-freeze-v001','files':[t.pin(p,False) for p in sorted(OUT.rglob('*')) if p.is_file()],'sourcepins_unchanged':[t.pin(p,False) for p in t.WATCHED],'new_outputs_viewed':False})
(MEDIA/'原件').mkdir(parents=True);shutil.copytree(OUT,MEDIA/'原件/提取包');(MEDIA/'展示副本').mkdir()
for p in grids+[cp]:shutil.copyfile(p,MEDIA/'展示副本'/p.name)
media_files=[]
for p in sorted(MEDIA.rglob('*')):
 if p.is_file():media_files.append(t.pin(p,False))
with (MEDIA/'来源-版本-状态索引.json').open('x',encoding='utf-8',newline='\n') as f:json.dump({'date':'2026-10-18','topic':'Walk204205统一72提取候选','version':'v001','status':'candidate-unviewed-not-imported','source_candidate':OUT.as_posix(),'source_index':t.pin(idx,False),'source_curation':t.pin(curationproof,False),'old90_preserved':True,'originals_and_presentation':media_files},f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps({'out':OUT.as_posix(),'canonical_media':MEDIA.as_posix(),'index':t.pin(idx,False),'shared_scale':shared['scale'],'raw_sourcecell_RGB_mismatches':0,'warnings':json.loads((run/'inspect-report.json').read_text(encoding='utf-8'))['warnings'],'new_outputs_viewed':False},ensure_ascii=False,indent=2))
