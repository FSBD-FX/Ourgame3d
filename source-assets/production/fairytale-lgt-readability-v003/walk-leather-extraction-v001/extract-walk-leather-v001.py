"""Extract native199/200/201 component candidates; no image viewing or fitting."""
from pathlib import Path
import datetime
import hashlib
import json
import platform
import shutil
import subprocess
import sys

import PIL
import numpy as np
from PIL import Image


OUT = Path(__file__).resolve().parent
PROJECT = Path("F:/Ourgame")
FAMILY = PROJECT / "source-assets/production/fairytale-lgt-readability-v003"
INPUT = FAMILY / "walk-leather-input-v001"
SG = Path("C:/Users/22499/.codex/skills/sprite-gen")
PYTHON = SG / ".venv/Scripts/python.exe"
TIMES = [83, 83, 83, 83, 83, 83]
EXTRACT_SHA = "f2a7902f01069668340d14217bd05c777f5c01853284102e211aba1013a45539"
WRAPPER_SHA = "2d7464dc2e8dd962a7d4dc170c0a7401d09cf1a626415309b4921b7d89d88aa3"
COMPONENTS = [
 ("Chest","chest",199,[90,90],512,"0a5aa5e1dc42854eb32db328bfbe1f9f19ccb73b9e528f3435d04547e28fa15a"),
 ("NearShoulder","nearshoulder",200,[60,44],512,"720e12d53d53221d0c01dba464796fa795543d7e954aade4e099d38ad167ced8"),
 ("FarShoulder","farshoulder",201,[32,30],512,"315ba1c2276d9dce2b0672d5fdd83b0386df85ff6b2afd837f327a10eb03d34c"),
]
WATCHED = {}


def pin(path, watch=True):
    data = path.read_bytes()
    value = {"path": path.as_posix(), "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}
    if watch and not path.is_relative_to(OUT):
        WATCHED[path] = value
    return value


def write(relative, data):
    path = OUT / relative
    if not path.is_relative_to(OUT):
        raise RuntimeError("Ownership boundary")
    path.parent.mkdir(parents=True, exist_ok=True)
    text = data if isinstance(data, str) else json.dumps(data, ensure_ascii=False, indent=2) + "\n"
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(text)
    return path


def copy_exact(source, target):
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        raise RuntimeError("Existing output cannot be overwritten")
    source_pin = pin(source)
    shutil.copy2(source, target)
    copied = pin(target)
    if source_pin["sha256"] != copied["sha256"] or source_pin["bytes"] != copied["bytes"]:
        raise RuntimeError("Input byte copy changed")
    return {"source": source_pin, "copy": copied}


def command(label, argv):
    result = subprocess.run(argv, capture_output=True, text=True, encoding="utf-8")
    log = write(f"logs/{label}.log", result.stdout + result.stderr)
    record = {"argv": argv, "actual_exit_code": result.returncode, "log": pin(log)}
    path = write(f"logs/{label}-command.json", record)
    return {**record, "command_record": pin(path)}


def pixel_metrics(path):
    with Image.open(path) as image:
        if image.mode != "RGBA" or image.size != (512, 512):
            raise RuntimeError("Expected candidate source 512 RGBA")
        array = np.asarray(image).copy()
        alpha = array[:, :, 3]
        core = alpha >= 128
        edge = np.zeros(alpha.shape, dtype=bool)
        edge[:4, :] = edge[-4:, :] = True
        edge[:, :4] = edge[:, -4:] = True
        box = image.getchannel("A").getbbox()
        core_box = image.getchannel("A").point(lambda a: 255 if a >= 128 else 0).getbbox()
        return {"source": pin(path), "mode": image.mode, "canvas_px": list(image.size),
                "RGBA_pixels_sha256": hashlib.sha256(array.tobytes()).hexdigest(),
                "alpha_nonzero_bbox_ltrb_exclusive": list(box) if box else None,
                "core128_bbox_ltrb_exclusive": list(core_box) if core_box else None,
                "nonzero_alpha_pixels": int(np.count_nonzero(alpha)),
                "core128_RGBA_pixels": int(np.count_nonzero(core)),
                "core128_RGBA_row_major_sha256": hashlib.sha256(array[core].tobytes()).hexdigest(),
                "partial_alpha_pixels": int(np.count_nonzero((alpha > 0) & (alpha < 255))),
                "distinct_core_RGB_colors": int(len(np.unique(array[:, :, :3][core], axis=0))),
                "pure_green_core128_pixels": int(np.count_nonzero(core & np.all(array[:, :, :3] == [0, 255, 0], axis=2))),
                "pure_green_nonzero_alpha_pixels": int(np.count_nonzero((alpha > 0) & np.all(array[:, :, :3] == [0, 255, 0], axis=2))),
                "edge_nonzero_alpha_pixels_margin4": int(np.count_nonzero((alpha > 0) & edge)),
                "bodyfreecount": None, "bodyfreecount_measured": False,
                "bodyfree_semantic_note": "RGBA/chroma/edge counts cannot count anatomical bodies, hands or helmets. No semantic mask or detector was supplied; do not turn six connected components into a claim of body-free art.",
                "new_component_A": None, "matching_body_B": None, "integer_delta_xy": None}


def curate_shared_run(run, state):
    sys.path.insert(0,str(SG))
    from sprite_gen.curate.curation import load_curation, stamp_curation, state_plan, frame_variant, pixel_snap_scale
    if load_curation(run) is not None:raise RuntimeError("Unexpected old sidecar")
    # HD canonical frame-N.png is selected; false sidecar variant would wrongly
    # select nonexistent .plain twins. Request fit.pixel_unfake stays false.
    payload=stamp_curation(run,{"version":1,"kind":"sprite-gen-curation","states":{state:{"selected":list(range(6)),"transforms":{}}}})
    sidecar=write(run.relative_to(OUT)/"curation.json",payload)
    loaded=load_curation(run);order,transforms=state_plan(loaded,state,6)
    request=json.loads((run/"sprite-request.json").read_text("utf-8-sig"))
    if order!=list(range(6)) or transforms or frame_variant(loaded,state)!="pixel" or pixel_snap_scale(request) is not None or request["fit"]["pixel_unfake"] is not False:
        raise RuntimeError("Explicit canonical HD identity selection failed")
    result=command(f"export-curated-{state}-v001",[str(PYTHON),"-B","-X","utf8",str(SG/"scripts/export_curated_pngs.py"),"--run-dir",str(run),"--state",state,"--selected-only"])
    if result["actual_exit_code"]:raise RuntimeError("Actual standard curated export failed; preserved log")
    metrics=[];provenance=[]
    for frame in range(6):
        before=run/f"frames/{state}/frame-{frame}.png";after=run/f"curated/frame-{frame}.png"
        with Image.open(before) as a,Image.open(after) as b:
            if not np.array_equal(np.asarray(a.convert("RGBA")),np.asarray(b.convert("RGBA"))):raise RuntimeError("Identity export changed RGBA")
        metric=pixel_metrics(after);metric["pre_curation_source"]=pin(before);metric["curated_export_RGBA_equal"]=True
        metric["curation_sidecar"]=pin(sidecar);metrics.append(metric)
        provenance.append({"frame":frame,"pre_curation_source":pin(before),"curated_export":pin(after),"curation":pin(sidecar),"RGBA_equal":True,"selected_index":frame,"pixel_snap_scale":None,"canonical_variant_filename_label":"pixel","fit_pixel_unfake":False,"A_B_delta_measured":False})
    return {"command":result,"sidecar":pin(sidecar),"provenance":provenance,"metrics":metrics,"selection_role":"Root authorized all six for extraction/feature trial; not fit, full animation or final install acceptance"}


def main():
 if Path(sys.executable).resolve()!=PYTHON.resolve():raise RuntimeError('Use sprite-gen venv')
 if OUT!=FAMILY/'walk-leather-extraction-v001' or list(OUT.glob('run-*')):raise RuntimeError('Unexpected/existing candidate')
 extract=SG/'sprite_gen/frames/extract.py';shared=PROJECT/'tools/scripts/extract-sprite-shared-row-scale.py'
 assert pin(extract)['sha256']==EXTRACT_SHA and pin(shared)['sha256']==WRAPPER_SHA
 approved_path=INPUT/'walk-leather-native-input-approved-v001.json';approved_pin=pin(approved_path)
 assert approved_pin['sha256']=='073a3b6e21c68c134dc68ffca63742426d10366762a82eeeb691261a6b595792'
 approved=json.loads(approved_path.read_text(encoding='utf-8-sig'));copy_exact(approved_path,OUT/'inputs/approved-handoff-exact.json')
 original_bridge=FAMILY/'primary3-leather-extraction-v001/shared-HD-fit-explicit-component-min-v001.py';copy_exact(original_bridge,OUT/'tool-provenance/shared-HD-fit-existing-exact.py')
 wrapper_text=original_bridge.read_text(encoding='utf-8')
 needle='        evidence.append(record)'
 replacement='''        import numpy as np
        memory=[]
        for i,p in enumerate(frames):
            a=np.asarray(p);al=a[:,:,3];core=al>=128;yy,xx=np.nonzero(core)
            memory.append({"frame":i,"alpha_bbox":list(p.getbbox()),"nonzero_alpha_pixels":int((al>0).sum()),"core128_pixels":int(core.sum()),"core128_bbox":[int(xx.min()),int(yy.min()),int(xx.max()+1),int(yy.max()+1)] if len(xx) else None,"RGBA_sha256":hashlib.sha256(a.tobytes()).hexdigest(),"pure_green_core":int((core&np.all(a[:,:,:3]==[0,255,0],axis=2)).sum())})
        record["numeric_only_fit_memory_before_native_QA"]=memory
        evidence.append(record)'''
 assert wrapper_text.count(needle)==1;wrapper_text=wrapper_text.replace(needle,replacement)
 needle='        native.extract_component_frames, sys.argv = original_hook, original_argv'
 replacement=needle+'\n        (run/"shared-fit-memory-numeric-v001.json").write_text(json.dumps({"scope":"Numerical observation only; failed extraction produces no accepted frames.","rows":evidence},indent=2)+"\\n",encoding="utf-8")'
 assert wrapper_text.count(needle)==1;wrapper_text=wrapper_text.replace(needle,replacement)
 wrapper=write('shared-HD-fit-memory-observer-v001.py',wrapper_text)
 tools=[SG/'scripts/extract_sprite_row_frames.py',extract,SG/'scripts/inspect_sprite_run.py',SG/'scripts/compose_sprite_atlas.py',SG/'sprite_gen/compose/compose_atlas.py',SG/'scripts/export_curated_pngs.py',SG/'sprite_gen/curate/curation.py',shared,original_bridge]
 write('toolchain-v001.json',{'python_executable':sys.executable,'python_version':platform.python_version(),'PIL':PIL.__version__,'NumPy':np.__version__,'installed_and_existing_tools':[pin(p) for p in tools],'candidate_wrapper':pin(wrapper),'tools_modified':False,'wrapper_changes':'Only observe exact returned shared frames numerically before native QA; min forwarding and all chroma/component/fitting/edge/count gates retained.'})
 runs=[];source_rows=[];diffs=[]
 for name,token,native,window,minimum,raw_sha in COMPONENTS:
  ar=next(x for x in approved['rows'] if x['component']==name);source_run=Path(ar['run_dir']);state=ar['state'];raw=Path(ar['raw_output_path']);request=source_run/'sprite-request.json'
  receiptpath=FAMILY/f'generation-control-v001/generation-receipt{native}-v001.json';receipt=json.loads(receiptpath.read_text(encoding='utf-8-sig'));pin(receiptpath)
  assert pin(raw)['sha256']==raw_sha and pin(raw)==receipt['canonical_raw'] and receipt['source_handoff']==approved_pin
  assert pin(request)==ar['request'] and ar['durations_ms']==TIMES
  im=Image.open(raw);assert list(im.size)==receipt['raw_size']==[2172,724] and im.mode==receipt['raw_mode']=='RGB'
  q=json.loads(request.read_text(encoding='utf-8-sig'));assert q['states'][state]['frames']==6 and q['states'][state]['fps']==12
  assert q['chroma_key']['rgb']==[0,255,255] and q['fit']['pixel_unfake'] is False and q['fit']['shared_row_scale'] is True
  assert [q['cell']['width']-2*q['cell']['safe_margin_x'],q['cell']['height']-2*q['cell']['safe_margin_y']]==window
  for item in ar['actual_runtime_body_pins']:assert pin(Path(item['path']))==item
  for item in ar['reference_images_in_order']:assert pin(Path(item['file']['path']))==item['file']
  originals=[]
  for rel in [f'raw/{state}.png','sprite-request.json','base-source.png',f'prompts/{state}.txt']:originals.append(copy_exact(source_run/rel,OUT/f'original-input/{token}'/rel))
  write(f'original-input/{token}/source-receipt-pin.json',{'native':native,'receipt':pin(receiptpath),'source_copies':originals})
  qgreen=json.loads(json.dumps(q));qgreen['chroma_key']={'name':'green','hex':'#00FF00','rgb':[0,255,0],'selection':'manual','selection_reason':'Root-approved diagnostic correction: raw/prompt green; original auto-CYAN request preserved.'};qgreen['states'][state]['durations_ms']=TIMES
  diffs.append({'component':name,'source_request':pin(request),'changes':[{'path':'chroma_key','before':q['chroma_key'],'after':qgreen['chroma_key']},{'path':f'states.{state}.durations_ms','before':q['states'][state].get('durations_ms'),'after':TIMES}],'raw_modified':False,'original_prepared_request_modified':False,'authorization':'Root explicit collaboration approval; NEW working requests only.'})
  curated=None
  for mode in ['original-CYAN-baseline','GREEN-standard-baseline','GREEN-shared-HD']:
   run=OUT/f'run-{token}-{mode}-v001'
   for rel in [f'raw/{state}.png','base-source.png',f'prompts/{state}.txt']:copy_exact(source_run/rel,run/rel)
   if mode=='original-CYAN-baseline':copy_exact(request,run/'sprite-request.json')
   else:write(run.relative_to(OUT)/'sprite-request.json',qgreen)
   before=pin(run/'sprite-request.json');argv=[str(PYTHON),'-B','-X','utf8',str(wrapper if mode=='GREEN-shared-HD' else SG/'scripts/extract_sprite_row_frames.py'),'--run-dir',str(run)]
   if mode=='GREEN-shared-HD':argv+=['--min-used-pixels',str(minimum)]
   result=command(f'extract-{token}-{mode}-v001',argv)
   inspect=command(f'inspect-{token}-{mode}-v001',[str(PYTHON),'-B','-X','utf8',str(SG/'scripts/inspect_sprite_run.py'),'--run-dir',str(run),'--states',state,'--report',str(run/'inspect-report.json')])
   fm_path=run/'frames/frames-manifest.json';insp_path=run/'inspect-report.json';fm=json.loads(fm_path.read_text(encoding='utf-8')) if fm_path.exists() else None;ir=json.loads(insp_path.read_text(encoding='utf-8')) if insp_path.exists() else None
   paths=sorted((run/'frames'/state).glob('frame-*.png'));memorypath=run/'shared-fit-memory-numeric-v001.json';memory=json.loads(memorypath.read_text(encoding='utf-8')) if memorypath.exists() else None
   e={'component':name,'native':native,'mode':mode,'run_dir':run.as_posix(),'extract':result,'inspect':inspect,'frames_published':len(paths),'frame_metrics':[pixel_metrics(x) for x in paths],'manifest_ok':fm.get('ok') if fm else None,'manifest_errors':fm.get('errors') if fm else None,'inspect_ok':ir.get('ok') if ir else None,'inspect_errors':ir.get('errors') if ir else None,'inspect_warnings':ir.get('warnings') if ir else None,'request_before':before,'request_after':pin(run/'sprite-request.json'),'min_used_pixels':minimum if mode=='GREEN-shared-HD' else 512,'shared_row_fit':fm['rows'][0].get('shared_row_fit') if fm and fm.get('rows') else None,'fit_memory_numeric':memory,'semantic_fit_or_full_animation_accepted':False};runs.append(e)
   if mode=='GREEN-shared-HD':
    available=result['actual_exit_code']==0 and fm is not None and fm['ok'] is True and len(paths)==6
    if available:
     compose=command(f'compose-{token}-GREEN-shared-HD-v001',[str(PYTHON),'-B','-X','utf8',str(SG/'scripts/compose_sprite_atlas.py'),'--run-dir',str(run),'--min-used-pixels',str(minimum)]);e['standard_compose']=compose
     if compose['actual_exit_code']!=0:raise RuntimeError('Actual standard compose failed; logs preserved')
     cm=json.loads((run/'manifest.json').read_text(encoding='utf-8'));actualdur=cm['animation']['rows'][state]['durations_ms'];assert actualdur==TIMES
     e['actual_composed_durations_ms']=actualdur;e['actual_nominal_fps']=12;e['timing_note']='Compose rounds1000/12 to83ms each; manifest498ms vs nominalfps12 cycle500ms. Runtime sync unaccepted.'
     curated=curate_shared_run(run,state);e['curated_export']=curated
    source_rows.append({'component':name,'native_request':native,'state':state,'shared_fit_window':window,'explicit_min_used_pixels':minimum,'available_for_Root_feature_measurement':available,'shared_row_fit':e['shared_row_fit'],'frames':[{'frame':i,'duration_ms':83,**m} for i,m in enumerate(curated['metrics'] if curated else [])],'new_A_B_delta_all_null':True,'body_reference':'Old CommonWalkv008 torso geometry only; NEW native-closed-hand composite Body target awaits freeze.','curated_export':curated['sidecar'] if curated else None})
 write('working-request-corrections-v001.json',{'originals_preserved':True,'Root_authorized_new_working_GREEN_and83ms':True,'rows':diffs})
 mismatches=[p.as_posix() for p,before in WATCHED.items() if pin(p,False)!=before];assert not mismatches,mismatches
 idx=write('walk-three-armor-source-index-v001.json',{'schema':'Walk6-three-soft-leather-source-extraction-candidate-v001','components':source_rows,'actual_available_frame_count':sum(len(x['frames']) for x in source_rows),'expected_frame_count':18,'durations_ms':TIMES,'all_new_A_B_delta_null':True,'oldBody_v008_is_motion_reference_only':True,'new_closed_hand_body_target_pending':True,'extracted_202_rejected_hand':False,'new_outputs_viewed':False,'fit_accepted':False,'imported':False,'semantic_bodyfreecount_known':False,'raw_review_retention':'Root E326/327/328 retained/actual viewed199/200/201 before extraction authorization.','next_boundary':'Root E-retains new outputs then measures actual features; no assembly/import/new-hand acceptance here.'})
 report=write('extraction-numeric-report-v001.json',{'schema':'Walk6-three-soft-leather-extraction-numeric-v001','runs':runs,'source_index':pin(idx),'readonly_sources_rechecked':len(WATCHED),'source_mismatches':[],'min_floor_policy':'Every attempt512; Far-specific lower floor requires Root decision, no195160 borrowing.','new_media_viewed':False,'tools_Source_UE_ledger_media_modified':False,'original_AUTO_CYAN_failures_preserved':True,'working_GREEN_and83_diffs_explicit':True,'bodyfreecount_or_A_fabricated':False})
 lines=[f"{x['component']} {x['mode']}: extract{x['extract']['actual_exit_code']}, inspect{x['inspect']['actual_exit_code']}, published{x['frames_published']}, warnings={x['inspect_warnings']}" for x in runs]
 write('HANDOFF.md','Walk199/200/201 extraction candidates only.\n\n'+'\n'.join(lines)+'\n\nOriginal raw/request/CYAN retained unchanged. Only NEW GREEN working request+83x6 declared; shared90x90/60x44/32x30. All512 failures retained, no generic/195160 relaxation. Low motion warnings retained. Standard compose/source durations83ms each=498ms vsfps12 nominal500ms explicitly recorded; no runtime sync acceptance. Stamped selected0..5 standardcurated export exactRGBA. A/B/delta null; new closed-hand Body target pending; no202 extraction, views or Source/UE/tools/ledger/media changes. Root E first then view.\n')
 files=[pin(p,False) for p in sorted(OUT.rglob('*')) if p.is_file()]
 for x in files:x['path']=Path(x['path']).relative_to(OUT).as_posix()
 f=write('extraction-freeze-v001.json',{'schema':'Walk6-three-soft-leather-extraction-freeze-v001','files':files,'file_count':len(files),'actual_available_frame_count':sum(len(x['frames']) for x in source_rows),'fit_or_motion_accepted':False,'new_outputs_viewed':False})
 print(json.dumps({'freeze':pin(f),'source_index':pin(idx),'report':pin(report),'available_frame_count':sum(len(x['frames']) for x in source_rows),'runs':[{'component':x['component'],'mode':x['mode'],'extract':x['extract']['actual_exit_code'],'inspect':x['inspect']['actual_exit_code'],'frames':x['frames_published'],'warnings':x['inspect_warnings']} for x in runs]},ensure_ascii=False,indent=2))

if __name__=='__main__':main()
