"""Native175 deterministic shared-row pipeline; never view, repair, or import images."""
from pathlib import Path
from datetime import datetime
import difflib
import hashlib
import json
import subprocess
import sys

from PIL import Image

ROOT = Path('F:/Ourgame/source-assets/production/fairytale-sword-primary3-v001')
SG = Path('C:/Users/22499/.codex/skills/sprite-gen')
RUN = ROOT / 'run-primary3-v001'
OUT = ROOT / 'primary3-extraction-v001'
STATE = 'sword_primary_3'
RAW = RUN / 'raw' / f'{STATE}.png'
WRAPPER = Path('F:/Ourgame/tools/scripts/extract-sprite-shared-row-scale.py')
DURATIONS = [110,110,60,60,160,160]


def fact(path):
    data = path.read_bytes()
    return dict(path=path.as_posix(),bytes=len(data),sha256=hashlib.sha256(data).hexdigest())


def write(path, value):
    assert not path.exists(), f'Refuse evidence overwrite: {path}'
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(value if isinstance(value,str) else json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')


def main():
    assert Path(sys.executable).resolve() == (SG/'.venv/Scripts/python.exe').resolve()
    assert not OUT.exists(), 'Fresh extraction only; no retry or overwrite.'
    assert not any((RUN/'frames').rglob('*.png'))
    assert not any(p.is_file() for directory in ['frames','curated','qa'] for p in (RUN/directory).rglob('*')), 'No existing derived output may be overwritten.'
    assert not any((RUN/name).exists() for name in ['manifest.json','sprite-sheet-alpha.png','sprite-sheet-alpha.report.json'])
    OUT.mkdir()
    request_path = RUN/'sprite-request.json'
    before_request = request_path.read_bytes()
    backup = OUT/'sprite-request-before-extraction-exact.json'
    backup.write_bytes(before_request)
    commands, frames = [], []
    failure = None
    metadata = {}
    request_changed = False
    frozen_before = json.loads((ROOT/'preparation-freeze-v001.json').read_text(encoding='utf-8'))
    try:
        for row in frozen_before['files']:
            assert fact(Path(row['path'])) == row, f'Frozen preparation changed: {row["path"]}'
        assert fact(ROOT/'preparation-freeze-v001.json')['sha256'] == '271bea83aa00fe057a6b8ca8f3c417fc0bc7858f8f9319ee2d00201e4dc645e8'
        approved_path=ROOT/'handoffs/primary3-native-input-approved-v001.json'
        assert fact(approved_path)['sha256']=='dafa0fc3ab65aa1a67022a96d265f41396986610ffeb9959a2c42ce706462bfa'
        approved=json.loads(approved_path.read_text(encoding='utf-8-sig'));assert approved['generation_ready'] is True and approved['root_review_required_before_generation'] is False
        row=approved['rows'][0];assert len(approved['rows'])==1 and row['component']=='SwordPrimary3Body' and row['state']==STATE and row['run_dir']==RUN.as_posix()
        assert fact(Path(approved['root_input_review']['path']))==approved['root_input_review']
        assert fact(Path(row['request']['path']))==row['request'] and fact(Path(row['prompt']['path']))==row['prompt']
        for reference in row['reference_images_in_order']:assert fact(Path(reference['file']['path']))==reference['file']
        native_receipt=json.loads((ROOT/'generation-control-v001/generation-receipt175-v001.json').read_text(encoding='utf-8-sig'))
        assert native_receipt['request_number']==175 and native_receipt['component']=='SwordPrimary3Body' and native_receipt['status']=='generated_retained_pending_extraction'
        assert native_receipt['canonical_raw']==fact(RAW) and native_receipt['source_handoff']==fact(approved_path)
        assert native_receipt['prompt_file_sha256']==row['prompt']['sha256'] and native_receipt['reference_images']==row['reference_images_in_order']
        assert fact(RAW)['bytes']==1500738
        assert fact(RAW)['sha256'] == '2fc43b327ee464673954bd39f139fbee334d1ccb1bf17f976a072ad31e88e6f7'
        assert fact(WRAPPER)['sha256'] == '2d7464dc2e8dd962a7d4dc170c0a7401d09cf1a626415309b4921b7d89d88aa3'
        request = json.loads(before_request)
        assert request['states'][STATE]['frames'] == 6
        assert request['states'][STATE]['durations_ms'] == DURATIONS
        assert request['states'][STATE]['loop'] is False
        assert request['fit']['shared_row_scale'] is True
        for name, tool, extra in [
            ('extract-shared-row',WRAPPER,[]),
            ('compose-atlas',SG/'scripts/compose_sprite_atlas.py',[]),
            ('export-curated',SG/'scripts/export_curated_pngs.py',['--state',STATE]),
            ('preview',SG/'scripts/preview_animation.py',[]),
        ]:
            argv = [sys.executable,'-X','utf8','-B',str(tool),'--run-dir',str(RUN)] + extra
            result = subprocess.run(argv,capture_output=True,text=True,encoding='utf-8')
            log = OUT/f'{name}-v001.log'
            write(log,result.stdout+result.stderr)
            commands.append(dict(name=name,argv=argv,tool=fact(tool),exit_code=result.returncode,log=fact(log)))
            after = request_path.read_bytes()
            if after != before_request:
                request_changed = True
                (OUT/'sprite-request-after-auto-change-exact.json').write_bytes(after)
                write(OUT/'request-auto-change.patch',''.join(difflib.unified_diff(before_request.decode('utf-8-sig').splitlines(True),after.decode('utf-8-sig').splitlines(True),fromfile='frozen-before',tofile='native-auto-change')))
                raise RuntimeError('Native tool altered frozen request: exact before/after retained; stopped, no silent restoration or continuation.')
            changed_inputs=[r['path'] for r in frozen_before['files'] if not Path(r['path']).is_file() or fact(Path(r['path']))!=r]
            if changed_inputs:raise RuntimeError('Native tool changed frozen preparation inputs; stopped: '+str(changed_inputs))
            if result.returncode != 0:
                raise RuntimeError(f'{name} failed with exit {result.returncode}; no following tool/QA relaxation.')
        manifest = json.loads((RUN/'frames/frames-manifest.json').read_text(encoding='utf-8'))
        atlas_report = json.loads((RUN/'sprite-sheet-alpha.report.json').read_text(encoding='utf-8'))
        assert manifest['ok'] and not manifest['errors'] and not manifest['warnings']
        assert atlas_report['ok']
        assert len(manifest['rows']) == 1
        shared = manifest['rows'][0]['shared_row_fit']
        assert not shared['per_frame_scale_normalization']
        runtime = json.loads((RUN/'manifest.json').read_text(encoding='utf-8'))
        atlas_timing = runtime['animation']['rows'][STATE]['durations_ms']
        assert runtime['animation']['rows'][STATE]['loop'] is False
        with Image.open(RUN/f'qa/{STATE}.gif') as gif:
            gif_timing = []
            for i in range(gif.n_frames):
                gif.seek(i)
                gif_timing.append(gif.info.get('duration'))
        assert len(atlas_timing)==len(gif_timing)==6
        timing_passed = atlas_timing == DURATIONS and gif_timing == DURATIONS
        for i in range(6):
            path = RUN/f'curated/frame-{i}.png'
            with Image.open(path) as image:
                assert image.mode == 'RGBA' and image.size == (512,512)
                bbox = image.getchannel('A').getbbox()
                assert bbox and bbox[3]-bbox[1]<=416
                diagnostics = []
                for role, roi in [('hands-body-inspection',[80,100,440,390]),('feet',[128,415,388,465]),('whole-alpha-bbox',list(bbox))]:
                    target = OUT/f'diagnostics-v001/frame-{i}-{role}.png'
                    target.parent.mkdir(parents=True,exist_ok=True)
                    assert not target.exists()
                    crop = image.crop(roi)
                    crop.save(target)
                    assert crop.tobytes() == image.crop(roi).tobytes()
                    diagnostics.append(dict(role=role,source_roi_px=roi,file=fact(target),resampled=False,source_pixel_bytes_preserved=True,semantic_mask=False,art_asset=False))
                frames.append(dict(frame=i,file=fact(path),source_canvas_px=[512,512],alpha_bbox_px=list(bbox),alpha_bbox_size_px=[bbox[2]-bbox[0],bbox[3]-bbox[1]],diagnostics=diagnostics,actual_grip_px=None,actual_axis_xy=None,actual_thumb_contour=None,actual_foot_roots_px=None,actual_body_armor_target_points=None,measurement_status='No new derived image viewed. Actual features and finishing-down-cut/anatomy judgment await E retention and review; no design/old markers transplanted.'))
        assert len({x['file']['sha256'] for x in frames}) == 6
        metadata = dict(frames_manifest=fact(RUN/'frames/frames-manifest.json'),atlas_report=fact(RUN/'sprite-sheet-alpha.report.json'),QA_errors=manifest['errors'],QA_warnings=manifest['warnings'],shared_row_ratio=shared['scale'],shared_row_fit=shared,actual_atlas_durations_ms=atlas_timing,actual_gif_durations_ms=gif_timing,timing_contract_passed=timing_passed,unique_frame_png_count=6)
        write(OUT/'standard-timing-diagnosis-v001.json',dict(request_durations_ms=DURATIONS,request_total_ms=sum(DURATIONS),actual_atlas_durations_ms=atlas_timing,actual_atlas_total_ms=sum(atlas_timing),actual_gif_durations_ms=gif_timing,actual_gif_total_ms=sum(gif_timing),timing_contract_passed=timing_passed,known_tool_scope='Standard compose/preview may use equal fps timing. Source request remains unchanged. Shape QA is separate from this nonuniform timing failure.',compose_implementation=fact(SG/'sprite_gen/compose/compose_atlas.py'),preview_implementation=fact(SG/'sprite_gen/qa/preview.py'),shared_tools_modified=False,preview_retimed=False,motion_rhythm_accepted=False))
    except Exception as error:
        failure = dict(type=type(error).__name__,message=str(error))
    final_request = request_path.read_bytes()
    preparation_mismatches = [x['path'] for x in frozen_before['files'] if not Path(x['path']).is_file() or fact(Path(x['path'])) != x]
    if preparation_mismatches and failure is None:
        failure=dict(type='FrozenPreparationChanged',message=str(preparation_mismatches))
    receipt = dict(schema='fairytale-native175-primary3-shared-extraction-v1',created_local=datetime.now().astimezone().isoformat(),component='SwordPrimary3Body',native_request=175,raw=fact(RAW),handoff=fact(ROOT/'handoffs/primary3-native-input-approved-v001.json'),preparation_freeze=fact(ROOT/'preparation-freeze-v001.json'),request=fact(request_path),request_before=fact(backup),request_exact_unchanged=final_request==before_request,request_auto_changed=request_changed,frozen_preparation_mismatches=preparation_mismatches,commands=commands,frames=frames,failure=failure,shape_pipeline_passed=failure is None,durations_ms=DURATIONS,loop=False,metadata=metadata,preview_scope='Unmodified standard600ms shape preview, not proof of660ms kernel /110/110/60/60/160/160ms, true kernel timing or continuous motion.',root_reported_raw_concern='Native175 body-only finishing down-cut candidate is retained. Derived closed grasp, short elbow, downward wrist arc, identity and continuity require E retention and review; no prior visual markers are transplanted.',new_outputs_viewed=False,raw_viewed_by_this_reviewer=False,native_called=False,ue_import_called=False,motion_accepted=False,formal_complete_units=0)
    write(OUT/'extraction-receipt-v001.json',receipt)
    provenance=[ROOT/'preparation-freeze-v001.json',ROOT/'handoffs/primary3-native-input-approved-v001.json',ROOT/'generation-control-v001/generation-receipt175-v001.json']
    files = sorted(set([p for p in RUN.rglob('*') if p.is_file()]+[p for p in OUT.rglob('*') if p.is_file()]+[Path(__file__).resolve(),*provenance]))
    freeze = OUT/('extracted-freeze-v001.json' if failure is None else 'extracted-failure-freeze-v001.json')
    write(freeze,dict(schema='fairytale-primary3-extracted-freeze-v1',created_local=datetime.now().astimezone().isoformat(),file_count=len(files),total_bytes=sum(p.stat().st_size for p in files),files=[fact(p) for p in files],failure=failure,shape_pipeline_passed=failure is None,timing_contract_passed=metadata.get('timing_contract_passed',False),new_outputs_viewed=False,registration_proposed=False,accepted=False,formal_complete_units=0))
    print(json.dumps(dict(freeze=fact(freeze),receipt=fact(OUT/'extraction-receipt-v001.json'),files=len(files),bytes=sum(p.stat().st_size for p in files),failure=failure,request_exact_unchanged=final_request==before_request,frozen_preparation_mismatches=preparation_mismatches,metadata=metadata,frames=[dict(frame=x['frame'],alpha_bbox_px=x['alpha_bbox_px'],file=x['file']) for x in frames]),ensure_ascii=False))
    return 0 if failure is None else 1


if __name__ == '__main__':
    raise SystemExit(main())
