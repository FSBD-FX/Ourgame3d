"""Standard shared component extraction only; no generation/import or visual display."""
from pathlib import Path
import argparse, datetime, hashlib, json, subprocess, sys
from PIL import Image

root=Path(__file__).resolve().parent
sg=Path('C:/Users/22499/.codex/skills/sprite-gen')
parser=argparse.ArgumentParser()
parser.add_argument('--component',choices=['primary1'],default='primary1')
key=parser.parse_args().component
handoff=json.loads((root/f'handoffs/{key}-native-input-v002.json').read_text(encoding='utf-8'))['rows'][0]
run=Path(handoff['run_dir']);state=handoff['state']
evidence=root/f'{key}-extraction-v002'
assert not evidence.exists(), 'Never overwrite extraction evidence'
evidence.mkdir()
def desc(p):
    p=Path(p);data=p.read_bytes()
    return {'path':p.as_posix(),'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()}
def write(p,v):
    assert not p.exists(),p
    p.write_text(v if isinstance(v,str) else json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
wrapper=Path('F:/Ourgame/tools/scripts/extract-sprite-shared-row-scale.py')
assert desc(wrapper)['sha256']=='2d7464dc2e8dd962a7d4dc170c0a7401d09cf1a626415309b4921b7d89d88aa3'
before=(run/'sprite-request.json').read_bytes()
(evidence/'sprite-request-before-extraction.json').write_bytes(before)
commands=[]
for name,tool,args in [('extract-shared-row',wrapper,[]),
                       ('compose-atlas',sg/'scripts/compose_sprite_atlas.py',[]),
                       ('export-curated',sg/'scripts/export_curated_pngs.py',['--state',state]),
                       ('preview',sg/'scripts/preview_animation.py',[])]:
    argv=[sys.executable,'-X','utf8','-B',str(tool),'--run-dir',str(run)]+args
    result=subprocess.run(argv,capture_output=True,text=True,encoding='utf-8')
    log=evidence/f'{name}-v001.log';write(log,result.stdout+result.stderr)
    commands.append({'argv':argv,'exit_code':result.returncode,'tool':desc(tool),'log':desc(log)})
    assert result.returncode==0,(name,result.returncode)
assert before==(run/'sprite-request.json').read_bytes(), 'Frozen request modified'
manifest=json.loads((run/'frames/frames-manifest.json').read_text(encoding='utf-8'))
frames=[]
for i in range(handoff['frame_count']):
    p=run/f'curated/frame-{i}.png'
    with Image.open(p) as im:
        assert im.mode=='RGBA' and im.size==(512,512)
        alpha=im.getchannel('A');bbox=alpha.getbbox()
        frames.append({'frame':i,'file':desc(p),'alpha_bbox_px':list(bbox),
                       'alpha_bbox_size_px':[bbox[2]-bbox[0],bbox[3]-bbox[1]],
                       'A_actual_px':None,'A_status':'Not located; wait root E preservation then actual crop/frame review.'})
unique_count=len({x['file']['sha256'] for x in frames})
write(evidence/'extraction-receipt-v001.json',{
    'schema':'fairytale-sword-body-standard-shared-extraction-v1','created_local':datetime.datetime.now().astimezone().isoformat(),
    'component':handoff['component'],'raw':desc(Path(handoff['raw_output_path'])),
    'request':desc(run/'sprite-request.json'),'commands':commands,'frames':frames,
    'frames_manifest':desc(run/'frames/frames-manifest.json'),'QA_errors':manifest['errors'],'QA_warnings':manifest['warnings'],'unique_frame_png_count':unique_count,
    'fit_window_px':handoff['fit_window_px'],'durations_ms':handoff['durations_ms'],'timing_modified':False,
    'alpha_contact_composites_viewed':False,'native_called':False,'ue_import_called':False,'formal_complete_units':0})
files=sorted([p for p in run.rglob('*') if p.is_file()]+[p for p in evidence.rglob('*') if p.is_file()]+[Path(__file__)])
freeze=evidence/'extracted-freeze-v001.json'
write(freeze,{'schema':'fairytale-sword-body-extracted-freeze-v1','created_local':datetime.datetime.now().astimezone().isoformat(),
              'component':handoff['component'],'file_count':len(files),'total_bytes':sum(p.stat().st_size for p in files),
              'files':[desc(p) for p in files],'new_outputs_viewed':False,'registration_proposed':False,'accepted':False})
print(json.dumps({'freeze':desc(freeze),'files':len(files),'bytes':sum(p.stat().st_size for p in files),
                  'frames':frames,'qa':manifest.get('qa')},ensure_ascii=False))
