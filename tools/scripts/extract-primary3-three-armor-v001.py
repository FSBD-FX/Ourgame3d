from pathlib import Path
from PIL import Image
import hashlib,json,subprocess,sys
R=Path('F:/Ourgame');B=R/'source-assets/production/fairytale-sword-primary3-v001';A=B/'armor-input-v001';SG=Path('C:/Users/22499/.codex/skills/sprite-gen')
assert Path(sys.executable).resolve()==(SG/'.venv/Scripts/python.exe').resolve()
WRAPPER=R/'tools/scripts/extract-sprite-shared-row-scale.py';D=[110,110,60,60,160,160]
def desc(p):
    d=p.read_bytes();return {'path':p.as_posix(),'bytes':len(d),'sha256':hashlib.sha256(d).hexdigest()}
def write(p,d):
    assert not p.exists();p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
hp=A/'primary3-three-armor-input-approved-v001.json';h=json.loads(hp.read_text(encoding='utf-8'))
assert desc(hp)['sha256']=='9dce3201cdadd573d2c2bc6fd50443210d12fe79fd33222607a65192a0d92d70'
assert desc(WRAPPER)['sha256']=='2d7464dc2e8dd962a7d4dc170c0a7401d09cf1a626415309b4921b7d89d88aa3'
prep=A/'preparation-freeze-v001.json';pins=json.loads(prep.read_text(encoding='utf-8'))['files']
def check_inputs():
    for pin in pins:assert desc(Path(pin['path']))==pin
check_inputs();out=A/'standard-extraction-v001';assert not out.exists();out.mkdir()
specs={'Chest':(176,'6016fcc0dab99adcf40dc57f2ca6569337e340b6ae1f055a5dc8af376ed2dc99'),'NearShoulder':(177,'4a030b2ad2dec2c1146f6a83e31e156d421631b5cc320119789f057ce1ee40d2'),'FarShoulder':(178,'11fc1079abea4bb0b3e6edef8b061eb51dcba42e08316d922c22d3793262b5d7')}
receipts=[];failure=None
try:
    for row in h['rows']:
        component=row['component'];number,sha=specs[component];run=Path(row['run_dir']);state=row['state'];raw=Path(row['raw_output_path']);req=Path(row['request']['path'])
        assert desc(raw)['sha256']==sha and desc(req)==row['request']
        native=B/f'generation-control-v001/generation-receipt{number}-v001.json';nr=json.loads(native.read_text(encoding='utf-8'))
        assert nr['request_number']==number and nr['component']==component and nr['canonical_raw']==desc(raw) and nr['source_handoff']==desc(hp)
        assert nr['prompt_file_sha256']==row['prompt']['sha256'] and nr['reference_images']==row['reference_images_in_order']
        assert not any(p.is_file() for n in ['frames','curated','qa'] for p in (run/n).rglob('*'))
        assert not any((run/n).exists() for n in ['manifest.json','sprite-sheet-alpha.png','sprite-sheet-alpha.report.json'])
        before=req.read_bytes();(out/f'{component}-request-before.json').write_bytes(before)
        commands=[]
        for name,tool,extra in [('extract-shared-row',WRAPPER,[]),('compose-atlas',SG/'scripts/compose_sprite_atlas.py',[]),('export-curated',SG/'scripts/export_curated_pngs.py',['--state',state]),('preview',SG/'scripts/preview_animation.py',[])]:
            argv=[sys.executable,'-B','-X','utf8',str(tool),'--run-dir',str(run)]+extra
            p=subprocess.run(argv,capture_output=True,text=True,encoding='utf-8');log=out/f'{component}-{name}.log';log.write_text(p.stdout+p.stderr,encoding='utf-8')
            commands.append({'name':name,'argv':argv,'tool':desc(tool),'exit_code':p.returncode,'log':desc(log)})
            if req.read_bytes()!=before:
                (out/f'{component}-request-after-CHANGED.json').write_bytes(req.read_bytes());raise RuntimeError('Frozen request changed; preserved and stopped')
            check_inputs();assert p.returncode==0,(component,name,p.returncode)
        fm=json.loads((run/'frames/frames-manifest.json').read_text(encoding='utf-8'));ar=json.loads((run/'sprite-sheet-alpha.report.json').read_text(encoding='utf-8'));rm=json.loads((run/'manifest.json').read_text(encoding='utf-8'))
        assert fm['ok'] and not fm['errors'] and not fm['warnings'] and ar['ok'] and len(fm['rows'])==1
        shared=fm['rows'][0]['shared_row_fit'];assert not shared['per_frame_scale_normalization']
        frames=[]
        for i in range(6):
            p=run/f'curated/frame-{i}.png'
            with Image.open(p) as im:
                assert im.mode=='RGBA' and im.size==(512,512);box=im.getchannel('A').getbbox();assert box
                assert box[2]-box[0]<=row['fit_window_design_px'][0] and box[3]-box[1]<=row['fit_window_design_px'][1]
                roi=[max(0,box[0]-4),max(0,box[1]-4),min(512,box[2]+4),min(512,box[3]+4)]
                crop=im.crop(roi);cp=out/f'inspection/{component}-frame-{i}.png';cp.parent.mkdir(parents=True,exist_ok=True);assert not cp.exists();crop.save(cp)
                assert Image.open(cp).tobytes()==crop.tobytes()
                frames.append({'frame':i,'file':desc(p),'alpha_bbox_px':list(box),'physical_feature_A':None,'source_body_target':None,'inspection_crop':desc(cp),'inspection_roi_original512':roi,'resampled':False})
        assert len({x['file']['sha256'] for x in frames})==6
        atlas=rm['animation']['rows'][state]['durations_ms']
        with Image.open(run/f'qa/{state}.gif') as gif:
            times=[]
            for i in range(gif.n_frames):gif.seek(i);times.append(gif.info.get('duration'))
        receipt={'component':component,'native_request':number,'raw':desc(raw),'request':desc(req),'commands':commands,'frames':frames,'shape_pipeline_passed':True,'request_unchanged':req.read_bytes()==before,'shared_row_fit':shared,'requested_ms':D,'actual_atlas_ms':atlas,'actual_gif_ms':times,'timing_contract_passed':atlas==D and times==D,'retimed':False,'motion_accepted':False,'new_outputs_viewed':False}
        write(out/f'{component}-receipt-v001.json',receipt);receipts.append(receipt)
except Exception as e:failure={'type':type(e).__name__,'message':str(e)}
write(out/'extraction-summary-v001.json',{'rows':receipts,'failure':failure,'shape_pipeline_passed':failure is None and len(receipts)==3,'requested_kernel_total_ms':660,'standard_preview_is_not_kernel_timing_proof':True,'formal_complete_units':0})
files=sorted(p for p in A.rglob('*') if p.is_file())+[Path(__file__).resolve()]
freeze=out/('extracted-freeze-v001.json' if failure is None else 'extracted-FAILURE-freeze-v001.json');write(freeze,{'files':[desc(p) for p in files],'failure':failure,'new_outputs_viewed':False,'formal_complete_units':0})
print(json.dumps({'freeze':desc(freeze),'failure':failure,'rows':[{'component':r['component'],'shared_scale':r['shared_row_fit']['scale'],'shapeQA':r['shape_pipeline_passed'],'atlas_ms':r['actual_atlas_ms'],'gif_ms':r['actual_gif_ms'],'timing_passed':r['timing_contract_passed']} for r in receipts]},ensure_ascii=False))
raise SystemExit(0 if failure is None else 1)
