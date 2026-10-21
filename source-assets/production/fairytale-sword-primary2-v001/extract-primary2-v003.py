"""Native170 deterministic shared-row pipeline; never view, repair, or import images."""
from pathlib import Path
from datetime import datetime
import difflib
import hashlib
import json
import subprocess
import sys

from PIL import Image

ROOT = Path(__file__).resolve().parent
SG = Path('C:/Users/22499/.codex/skills/sprite-gen')
RUN = ROOT / 'run-primary2-v003'
OUT = ROOT / 'primary2-extraction-v003'
STATE = 'sword_primary_2'
RAW = RUN / 'raw' / f'{STATE}.png'
WRAPPER = Path('F:/Ourgame/tools/scripts/extract-sprite-shared-row-scale.py')
DURATIONS = [75,75,60,60,135,135]


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
    OUT.mkdir()
    request_path = RUN/'sprite-request.json'
    before_request = request_path.read_bytes()
    backup = OUT/'sprite-request-before-extraction-exact.json'
    backup.write_bytes(before_request)
    commands, frames = [], []
    failure = None
    metadata = {}
    request_changed = False
    frozen_before = json.loads((ROOT/'preparation-freeze-v003.json').read_text(encoding='utf-8'))
    try:
        for row in frozen_before['files']:
            assert fact(Path(row['path'])) == row, f'Frozen preparation changed: {row["path"]}'
        assert fact(RAW)['sha256'] == '6963752d95b58592d7b736088904879e8811dd207d268272e4ab4e3cee9a6bdd'
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
            log = OUT/f'{name}-v003.log'
            write(log,result.stdout+result.stderr)
            commands.append(dict(name=name,argv=argv,tool=fact(tool),exit_code=result.returncode,log=fact(log)))
            after = request_path.read_bytes()
            if after != before_request:
                request_changed = True
                (OUT/'sprite-request-after-auto-change-exact.json').write_bytes(after)
                write(OUT/'request-auto-change.patch',''.join(difflib.unified_diff(before_request.decode('utf-8-sig').splitlines(True),after.decode('utf-8-sig').splitlines(True),fromfile='frozen-before',tofile='native-auto-change')))
                raise RuntimeError('Native tool altered frozen request: exact before/after retained; stopped, no silent restoration or continuation.')
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
        timing_passed = atlas_timing == DURATIONS and gif_timing == DURATIONS
        for i in range(6):
            path = RUN/f'curated/frame-{i}.png'
            with Image.open(path) as image:
                assert image.mode == 'RGBA' and image.size == (512,512)
                bbox = image.getchannel('A').getbbox()
                assert bbox
                diagnostics = []
                for role, roi in [('hands-body-inspection',[80,100,440,390]),('feet',[128,415,388,465]),('whole-alpha-bbox',list(bbox))]:
                    target = OUT/f'diagnostics-v003/frame-{i}-{role}.png'
                    target.parent.mkdir(parents=True,exist_ok=True)
                    assert not target.exists()
                    crop = image.crop(roi)
                    crop.save(target)
                    assert crop.tobytes() == image.crop(roi).tobytes()
                    diagnostics.append(dict(role=role,source_roi_px=roi,file=fact(target),resampled=False,source_pixel_bytes_preserved=True,semantic_mask=False,art_asset=False))
                frames.append(dict(frame=i,file=fact(path),source_canvas_px=[512,512],alpha_bbox_px=list(bbox),alpha_bbox_size_px=[bbox[2]-bbox[0],bbox[3]-bbox[1]],diagnostics=diagnostics,actual_grip_px=None,actual_axis_xy=None,actual_thumb_contour=None,actual_foot_roots_px=None,actual_body_armor_target_points=None,measurement_status='No new derived image viewed. Actual features and rising-cut/anatomy judgment await E retention and review; no design/old markers transplanted.'))
        assert len({x['file']['sha256'] for x in frames}) == 6
        metadata = dict(frames_manifest=fact(RUN/'frames/frames-manifest.json'),atlas_report=fact(RUN/'sprite-sheet-alpha.report.json'),QA_errors=manifest['errors'],QA_warnings=manifest['warnings'],shared_row_ratio=shared['scale'],shared_row_fit=shared,actual_atlas_durations_ms=atlas_timing,actual_gif_durations_ms=gif_timing,timing_contract_passed=timing_passed,unique_frame_png_count=6)
        write(OUT/'standard-timing-diagnosis-v003.json',dict(request_durations_ms=DURATIONS,request_total_ms=sum(DURATIONS),actual_atlas_durations_ms=atlas_timing,actual_atlas_total_ms=sum(atlas_timing),actual_gif_durations_ms=gif_timing,actual_gif_total_ms=sum(gif_timing),timing_contract_passed=timing_passed,known_tool_scope='Standard compose/preview may use equal fps timing. Source request remains unchanged. Shape QA is separate from this nonuniform timing failure.',compose_implementation=fact(SG/'sprite_gen/compose/compose_atlas.py'),preview_implementation=fact(SG/'sprite_gen/qa/preview.py'),shared_tools_modified=False,preview_retimed=False,motion_rhythm_accepted=False))
    except Exception as error:
        failure = dict(type=type(error).__name__,message=str(error))
    final_request = request_path.read_bytes()
    preparation_mismatches = [x['path'] for x in frozen_before['files'] if fact(Path(x['path'])) != x]
    receipt = dict(schema='fairytale-native170-primary2-shared-extraction-v3',created_local=datetime.now().astimezone().isoformat(),component='SwordPrimary2Body',native_request=170,raw=fact(RAW),handoff=fact(ROOT/'handoffs/primary2-native-input-v003.json'),preparation_freeze=fact(ROOT/'preparation-freeze-v003.json'),request=fact(request_path),request_before=fact(backup),request_exact_unchanged=final_request==before_request,request_auto_changed=request_changed,frozen_preparation_mismatches=preparation_mismatches,commands=commands,frames=frames,failure=failure,shape_pipeline_passed=failure is None,durations_ms=DURATIONS,loop=False,metadata=metadata,preview_scope='Unmodified standard shape preview, not proof of75/75/60/60/135/135ms, true kernel timing or continuous motion.',root_reported_raw_concern='Root saw a genuinely bent low elbow and rising wrist in170 raw, but phase1 glove appears open. Derived views must be reviewed before pose/grip acceptance.',new_outputs_viewed=False,raw_viewed_by_this_reviewer=False,native_called=False,ue_import_called=False,motion_accepted=False,formal_complete_units=0)
    write(OUT/'extraction-receipt-v003.json',receipt)
    files = sorted([p for p in RUN.rglob('*') if p.is_file()]+[p for p in OUT.rglob('*') if p.is_file()]+[Path(__file__).resolve()])
    freeze = OUT/('extracted-freeze-v003.json' if failure is None else 'extracted-failure-freeze-v003.json')
    write(freeze,dict(schema='fairytale-primary2-extracted-freeze-v3',created_local=datetime.now().astimezone().isoformat(),file_count=len(files),total_bytes=sum(p.stat().st_size for p in files),files=[fact(p) for p in files],failure=failure,shape_pipeline_passed=failure is None,timing_contract_passed=metadata.get('timing_contract_passed',False),new_outputs_viewed=False,registration_proposed=False,accepted=False,formal_complete_units=0))
    print(json.dumps(dict(freeze=fact(freeze),receipt=fact(OUT/'extraction-receipt-v003.json'),files=len(files),bytes=sum(p.stat().st_size for p in files),failure=failure,request_exact_unchanged=final_request==before_request,frozen_preparation_mismatches=preparation_mismatches,metadata=metadata,frames=[dict(frame=x['frame'],alpha_bbox_px=x['alpha_bbox_px'],file=x['file']) for x in frames]),ensure_ascii=False))
    return 0 if failure is None else 1


if __name__ == '__main__':
    raise SystemExit(main())
