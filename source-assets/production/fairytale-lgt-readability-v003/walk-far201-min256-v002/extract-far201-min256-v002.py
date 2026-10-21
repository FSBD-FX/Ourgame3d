"""Root-authorized201Far min256 only, original geometry and old failures unchanged."""
from pathlib import Path
import importlib.util,json,hashlib,sys,numpy as np
from PIL import Image
HERE=Path(__file__).resolve().parent;FAMILY=HERE.parent;OLD=FAMILY/'walk-leather-extraction-v001'
spec=importlib.util.spec_from_file_location('walk_extraction',OLD/'extract-walk-leather-v001.py');t=importlib.util.module_from_spec(spec);spec.loader.exec_module(t)
assert Path(sys.executable).resolve()==t.PYTHON.resolve();t.OUT=HERE;t.WATCHED={}
oldfreeze=json.loads((OLD/'extraction-freeze-v001.json').read_text(encoding='utf-8'))
for name in ['extract-walk-leather-v001.py','shared-HD-fit-memory-observer-v001.py','walk-three-armor-source-index-v001.json']:
 p=OLD/name;d=next(x for x in oldfreeze['files'] if x['path']==name);b=p.read_bytes();assert len(b)==d['bytes'] and hashlib.sha256(b).hexdigest()==d['sha256']
run=HERE/'run-farshoulder-GREEN-shared-HD-min256-v002';state='leather_farshoulder_sword_walk'
source=OLD/'run-farshoulder-GREEN-shared-HD-v001'
for rel in [f'raw/{state}.png','sprite-request.json','base-source.png',f'prompts/{state}.txt']:t.copy_exact(source/rel,run/rel)
wrapper=HERE/'shared-HD-fit-memory-observer-exact-v001.py';t.copy_exact(OLD/'shared-HD-fit-memory-observer-v001.py',wrapper)
t.write('Root-min256-decision-v001.json',{'scope':'Only201Far NEW run; min256; old512 failures retained.','authorization':'Root collaboration message: same32x30/sharedscale/raw, core295+ sufficient.','request_and_raw_changed':False,'effect_relabel_or_fill_or_shape_resize':False})
extract=t.command('extract-far201-min256-v002',[str(t.PYTHON),'-B','-X','utf8',str(wrapper),'--run-dir',str(run),'--min-used-pixels','256'])
inspect=t.command('inspect-far201-min256-v002',[str(t.PYTHON),'-B','-X','utf8',str(t.SG/'scripts/inspect_sprite_run.py'),'--run-dir',str(run),'--states',state,'--report',str(run/'inspect-report.json')])
assert extract['actual_exit_code']==inspect['actual_exit_code']==0
fm=json.loads((run/'frames/frames-manifest.json').read_text(encoding='utf-8'));oldmemory=json.loads((source/'shared-fit-memory-numeric-v001.json').read_text(encoding='utf-8'))['rows'][0]
assert fm['rows'][0]['shared_row_fit']['scale']==oldmemory['scale']==0.23255813953488372
for i,m in enumerate(oldmemory['numeric_only_fit_memory_before_native_QA']):
 a=np.asarray(Image.open(run/f'frames/{state}/frame-{i}.png'));assert hashlib.sha256(a.tobytes()).hexdigest()==m['RGBA_sha256']
compose=t.command('compose-far201-min256-v002',[str(t.PYTHON),'-B','-X','utf8',str(t.SG/'scripts/compose_sprite_atlas.py'),'--run-dir',str(run),'--min-used-pixels','256']);assert compose['actual_exit_code']==0
cm=json.loads((run/'manifest.json').read_text(encoding='utf-8'));assert cm['animation']['rows'][state]['durations_ms']==[83]*6
export=t.curate_shared_run(run,state)
oldindexpath=OLD/'walk-three-armor-source-index-v001.json';oldindex=json.loads(oldindexpath.read_text(encoding='utf-8'));rows=oldindex['components'][:2]
for row in rows:
 for frame in row['frames']:assert t.pin(Path(frame['source']['path']))==frame['source']
far={'component':'FarShoulder','native_request':201,'state':state,'shared_fit_window':[32,30],'explicit_min_used_pixels':256,'available_for_Root_feature_measurement':True,'shared_row_fit':fm['rows'][0]['shared_row_fit'],'frames':[{'frame':i,'duration_ms':83,**m} for i,m in enumerate(export['metrics'])],'new_A_B_delta_all_null':True,'body_reference':'OldCommonWalkv008 geometry only; new native closed-hand composite target still pending.','curated_export':export['sidecar']}
rows.append(far)
idx=t.write('walk-eighteen-source-index-v002.json',{'schema':'Walk6-eighteen-soft-leather-source-index-v002','components':rows,'actual_available_frame_count':18,'expected_frame_count':18,'durations_ms':[83]*6,'old_Chest_Near12_index':t.pin(oldindexpath),'old_12_freeze':t.pin(OLD/'extraction-freeze-v001.json'),'all_new_A_B_delta_null':True,'new_closed_hand_body_target_pending':True,'fit_accepted':False,'imported':False,'new_outputs_viewed':False,'202_203_hands_rejected_not_extracted':True})
report=t.write('far201-min256-proof-v002.json',{'schema':'Walk201Far-only-explicit256-proof-v002','extract':extract,'inspect':inspect,'compose':compose,'export':export,'same_shared_row_scale':oldmemory['scale'],'all_six_RGBA_match_old512_failed_fit_memory':True,'old512_failure_freeze':t.pin(OLD/'extraction-freeze-v001.json'),'min_core128_pixels':min(m['core128_RGBA_pixels'] for m in export['metrics']),'GREEN_chroma_and83ms_working_request_unchanged':True,'timing_note':'Standardcompose durations83x6=498ms; fps12 nominal500ms remains explicit, no runtime sync acceptance.','old_12_curated_sources_exact':True,'new_A_B_null':True,'new_outputs_viewed':False,'semantic_or_motion_accepted':False})
t.write('HANDOFF.md','Only201Far explicitmin256 authorized by Root. Same32x30 window/shared0.2325581395 and native raw; all6 RGBA equal old512-failed numeric fit. Default failures/CYAN failures unchanged. Standardextract/inspect/compose/export actualexit0; lowmotion retained. Combined18 index references exact oldChest/Near12+newFar6. A/B/null, new closed-hand Body pending, no view/import/Source/UE/ledger/tools.\n')
for p,before in t.WATCHED.items():assert t.pin(p,False)==before
files=[t.pin(p,False) for p in sorted(HERE.rglob('*')) if p.is_file()]
for d in files:d['path']=Path(d['path']).relative_to(HERE).as_posix()
f=t.write('delivery-freeze-v002.json',{'schema':'Walk201Far-min256-and-combined18-delivery-freeze-v002','files':files,'available_armor_frames':18,'newFar_frames':6,'new_outputs_viewed':False,'fit_or_motion_accepted':False})
print(json.dumps({'freeze':t.pin(f),'index':t.pin(idx),'report':t.pin(report),'warnings':json.loads((run/'inspect-report.json').read_text(encoding='utf-8'))['warnings'],'readonly_sources':len(t.WATCHED)},ensure_ascii=False,indent=2))
