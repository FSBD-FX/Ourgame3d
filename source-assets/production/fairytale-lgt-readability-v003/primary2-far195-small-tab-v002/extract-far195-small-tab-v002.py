"""Extract native193/194/195 component candidates; no image viewing or fitting."""
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
INPUT = FAMILY / "primary2-leather-input-v001"
SG = Path("C:/Users/22499/.codex/skills/sprite-gen")
PYTHON = SG / ".venv/Scripts/python.exe"
TIMES = [75, 75, 60, 60, 135, 135]
EXTRACT_SHA = "f2a7902f01069668340d14217bd05c777f5c01853284102e211aba1013a45539"
WRAPPER_SHA = "2d7464dc2e8dd962a7d4dc170c0a7401d09cf1a626415309b4921b7d89d88aa3"
COMPONENTS = [
    ("Chest", "chest", 193, [90, 90], 512, "1bcc602bae05b9d313d508fb01cfbdf995a18d581debda09548e824a5ae2d380"),
    ("NearShoulder", "nearshoulder", 194, [60, 44], 512, "df59d491a1f939fa9138094917ba58aa86617b7f9069e20a6ff77f270948ce60"),
    ("FarShoulder", "farshoulder", 195, [32, 30], 256, "5b4300b99e42c715060c0fa523774586d612bc877791e36f215cecc175dba5ca"),
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
    if Path(sys.executable).resolve()!=PYTHON.resolve() or OUT!=FAMILY/'primary2-far195-small-tab-v002' or list(OUT.glob('run-*')):raise RuntimeError('Unexpected output/interpreter')
    olddir=FAMILY/'primary2-leather-extraction-v001'
    oldfreeze=olddir/'extraction-freeze-v001.json';oldindex=olddir/'primary2-eighteen-source-index-v001.json'
    for row in json.loads(oldfreeze.read_text('utf-8-sig'))['files']:
        actual=pin(olddir/row['path'])
        if (actual['bytes'],actual['sha256'])!=(row['bytes'],row['sha256']):raise RuntimeError('Frozen baseline evidence changed')
    receiptpath=FAMILY/'generation-control-v001/generation-receipt195-v001.json';receipt=json.loads(receiptpath.read_text('utf-8-sig'));pin(receiptpath)
    source=INPUT/'run-farshoulder-primary2-v001';state='leather_farshoulder_sword_primary2';raw=source/f'raw/{state}.png'
    if pin(raw)!=receipt['canonical_raw'] or receipt['raw_size']!=[2171,724]:raise RuntimeError('Wrong actual195 raw')
    approved=Path(receipt['source_handoff']['path'])
    if pin(approved)!=receipt['source_handoff']:raise RuntimeError('Approved195 input changed')
    old_wrapper=PROJECT/'tools/scripts/extract-sprite-shared-row-scale.py'
    if pin(old_wrapper)['sha256']!=WRAPPER_SHA or pin(SG/'sprite_gen/frames/extract.py')['sha256']!=EXTRACT_SHA:raise RuntimeError('Pinned tool changed')
    text=old_wrapper.read_text('utf-8-sig')
    text=text.replace('    args = parser.parse_args()', '    parser.add_argument("--min-used-pixels",type=int,required=True)\n    args = parser.parse_args()\n    require(args.min_used_pixels==160,"160 is authorized ONLY for this isolated195 diagnostic")',1)
    text=text.replace('        sys.argv = [str(EXTRACT), "--run-dir", str(run)]','        sys.argv = [str(EXTRACT), "--run-dir", str(run), "--min-used-pixels", str(args.min_used_pixels)]',1)
    wrapper=write('shared-HD-fit-195-only-min160-v002.py',text)
    run=OUT/'run-farshoulder-shared-HD-min160-v002';copies=[]
    for rel in [f'raw/{state}.png','sprite-request.json','base-source.png',f'prompts/{state}.txt']:
        copies.append(copy_exact(source/rel,run/rel))
    request=json.loads((run/'sprite-request.json').read_text('utf-8-sig'))
    if request['fit']['pixel_unfake'] is not False or request['fit']['shared_row_scale'] is not True or request['states'][state]['durations_ms']!=TIMES:raise RuntimeError('HD/timing changed')
    if [request['cell']['width']-2*request['cell']['safe_margin_x'],request['cell']['height']-2*request['cell']['safe_margin_y']]!=[32,30]:raise RuntimeError('Original shared extent changed')
    extraction=command('extract-far195-min160-v002',[str(PYTHON),'-B','-X','utf8',str(wrapper),'--run-dir',str(run),'--min-used-pixels','160'])
    inspection=command('inspect-far195-min160-v002',[str(PYTHON),'-B','-X','utf8',str(SG/'scripts/inspect_sprite_run.py'),'--run-dir',str(run),'--states',state,'--report',str(run/'inspect-report.json')])
    if extraction['actual_exit_code'] or inspection['actual_exit_code']:raise RuntimeError('Real extraction/inspect failed; preserve logs')
    fm=run/'frames/frames-manifest.json';manifest=json.loads(fm.read_text('utf-8-sig'));shared=manifest['rows'][0]['shared_row_fit']
    if shared['scale']!=0.2803738317757009 or shared['source_max_extent']!=[81,107] or shared['per_frame_scale_normalization'] is not False:raise RuntimeError('Prior exact fit no longer matches')
    observed_path=olddir/'far195-floor-review-v001/far195-vs-ready187-floor-numeric-v001.json';observed=json.loads(observed_path.read_text('utf-8-sig'));pin(observed_path)
    extracted=[pixel_metrics(run/f'frames/{state}/frame-{i}.png') for i in range(6)]
    for frame,(metric,prior) in enumerate(zip(extracted,observed['captures'][0]['frame_metrics'])):
        if metric['RGBA_pixels_sha256']!=prior['RGBA_memory_sha256']:raise RuntimeError('Only floor may change; RGBA differs from original256 failure in-memory fit')
        if metric['core128_RGBA_pixels']<128:raise RuntimeError('Root dedicated core>=128pixel-count gate failed')
    export=curate_shared_run(run,state)
    far={'component':'FarShoulder','native_request':195,'state':state,'shared_fit_window':[32,30],'explicit_min_used_pixels':160,'root_min_core128_pixel_count':128,'root_alpha_core_threshold':128,'available_for_Root_feature_measurement':True,'shared_row_fit':shared,'frames':[{'frame':i,'duration_ms':TIMES[i],**metric} for i,metric in enumerate(export['metrics'])],'new_A_B_delta_all_null':True,'curated_export':export['sidecar'],'actual_body171_run_primary2_v004_fit_review_required':True,'only_195_floor_design_exception':True}
    old=json.loads(oldindex.read_text('utf-8-sig'));components=[c for c in old['components'] if c['component'] in ['Chest','NearShoulder']]+[far]
    if sum(len(c['frames']) for c in components)!=18:raise RuntimeError('Exact18 new combined selection required')
    index=write('primary2-eighteen-source-index-v002.json',{'schema':'primary2-only193Chest194Near195Far-curated-source-index-v002','created_local':datetime.datetime.now().astimezone().isoformat(),'components':components,'expected_frame_count':18,'actual_available_frame_count':18,'all_three_rows_available':True,'durations_ms':TIMES,'all_A_B_delta_null':True,'old_Chest_Near_entries_unchanged':True,'old12_index':pin(oldindex),'old512_256_failure_freeze':pin(oldfreeze),'actual_body171_source_version_mapping':old['actual_body171_source_version_mapping'],'fit_accepted':False,'imported':False,'new_media_viewed':False})
    inspect=json.loads((run/'inspect-report.json').read_text('utf-8-sig'))
    policy=write('Root-195-only-small-tab-design-boundary-v002.json',{'native_request':195,'scope':'Only this isolated narrow far shoulder tab row, not a general floor relaxation','Root_decision':'Keep actual compressed perspective frame2 instead of enlarging/redrawing for generic sparse floor. Root allows only new160minimum, core(alpha>=128) count>=128.','min_used_pixels':160,'min_core128_pixels':128,'shared_window':[32,30],'shared_scale_unchanged':True,'source_canvas_unchanged':[2171,724],'source_colors_edges_component_count_QA_unchanged':True,'no_effect_relabel_fill_or_per_frame_scale':True,'frame2_nonzero_bbox':[248,252,263,271],'frame2_nonzero_pixels':191,'frame2_core128_pixels':130,'source_projection_scale_derived':72/416,'frame2_expected_screen_dimensions_px':[15*72/416,19*72/416],'screen_size_is_contract_derivation_not_new_native_screenshot_measurement':True,'readability_responsibility':'Chest and NearShoulder carry main armor readability. Far tab is about2.6x3.3px in this phase; fit/readability still await actual native review.','previous512_256_failures_preserved':pin(oldfreeze),'previous_floor_numeric_comparison':pin(observed_path),'fit_or_full_animation_accepted':False})
    mismatches=[str(p) for p,before in WATCHED.items() if pin(p,False)!=before]
    if mismatches:raise RuntimeError('Read-only source changed')
    report=write('extraction-small-tab-report-v002.json',{'native_request':195,'source_copies':copies,'actual_extraction':extraction,'actual_inspection':inspection,'frames_manifest':pin(fm),'shared_row_fit':shared,'pre_curated_metrics':extracted,'curated_export':export,'Root_design_boundary':pin(policy),'combined18_index':pin(index),'exact_RGBA_equal_to_min256_failed_fit':True,'Root_core128_count_gate_passed':True,'inspect_warnings':inspect.get('warnings'),'read_only_source_rechecks':len(WATCHED),'source_mismatches':[],'fit_accepted':False,'new_outputs_viewed':False})
    write('HANDOFF.md','# P2 Far195独立窄片提取v002\n\n仅按Root实际附件设计，对195用min160与core(alpha>=128)像素数>=128。原32×30共同scale/2171×724原图/色键/边缘/六组件门不变。六帧RGBA逐项等于先前256失败时的内存fit；无放大/填像素/标effect。标准curated显式selected0..5、identity export后RGBA相等。\n\n新18索引只引用原Chest193/Near194的12curated源与本Far195六curated源。全部A/B/delta仍null，旧512/256失败及freeze保留。最小Far仅约2.6×3.3屏幕像素（由72/416合同推导，非新native测量）；主要装备辨识由胸甲/近肩承担，Far fit待Root E归档后实际审阅。未查看新图，无Source/UE/import/工具/ledger/进度/媒体改动。\n')
    files=[pin(p,False) for p in sorted(OUT.rglob('*')) if p.is_file()]
    for item in files:item['path']=Path(item['path']).relative_to(OUT).as_posix()
    freeze=write('extraction-freeze-v002.json',{'files':files,'file_count_excluding_manifest':len(files),'total_bytes_excluding_manifest':sum(f['bytes'] for f in files),'actual_curated_frames':6,'combined18_source_index':pin(index),'new_media_viewed':False,'fit_accepted':False})
    print(json.dumps({'report':pin(report),'combined18_index':pin(index),'freeze':pin(freeze),'actual_exit_codes':[extraction['actual_exit_code'],inspection['actual_exit_code'],export['command']['actual_exit_code']],'nonzero':[m['nonzero_alpha_pixels'] for m in extracted],'core128':[m['core128_RGBA_pixels'] for m in extracted],'warnings':inspect.get('warnings'),'read_only_sources':len(WATCHED),'source_mismatches':[]},indent=2))

if __name__=='__main__':main()
