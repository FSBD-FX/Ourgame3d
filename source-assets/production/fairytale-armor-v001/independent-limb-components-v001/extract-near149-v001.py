"""Run the unchanged standard component pipeline; do not view or repaint outputs."""
from pathlib import Path
import datetime, hashlib, json, subprocess, sys

ROOT=Path(__file__).resolve().parent
RUN=ROOT/'run-shoulder-near-idle-v001'
OUT=ROOT/'near149-extraction-v001'
if OUT.exists():raise RuntimeError('Never overwrite extraction evidence')
OUT.mkdir()
SG=Path('C:/Users/22499/.codex/skills/sprite-gen')
RAW=RUN/'raw/armor_shoulder_near_idle.png'
assert hashlib.sha256(RAW.read_bytes()).hexdigest()=='4e90e3e9cabd4d02c152eb008c0b4c620a6dff291b9e832a0a7195bb632aa8d3'
def meta(p):return {'path':p.as_posix(),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
request=RUN/'sprite-request.json'
(OUT/'sprite-request-before-extraction.json').write_bytes(request.read_bytes())
commands=[('extract-shared-row-v001.log',Path('F:/Ourgame/tools/scripts/extract-sprite-shared-row-scale.py'),[]),
          ('compose-atlas-v001.log',SG/'scripts/compose_sprite_atlas.py',[]),
          ('export-curated-v001.log',SG/'scripts/export_curated_pngs.py',['--state','armor_shoulder_near_idle']),
          ('preview-v001.log',SG/'scripts/preview_animation.py',[])]
records=[]
for log,tool,extra in commands:
    argv=[sys.executable,'-X','utf8','-B',str(tool),'--run-dir',str(RUN)]+extra
    result=subprocess.run(argv,capture_output=True,text=True,encoding='utf-8')
    (OUT/log).write_text(result.stdout+result.stderr,encoding='utf-8')
    records.append({'argv':argv,'exit_code':result.returncode,'tool':meta(tool),'log':meta(OUT/log)})
    if result.returncode:raise RuntimeError(log+' failed')
fm=json.loads((RUN/'frames/frames-manifest.json').read_text(encoding='utf-8'))
assert fm['ok'] and not fm['errors'] and not fm['warnings']
assert request.read_bytes()==(OUT/'sprite-request-before-extraction.json').read_bytes()
receipt={'schema':'native149-near4-extraction-receipt-v1','created_local':datetime.datetime.now().astimezone().isoformat(),
         'raw':meta(RAW),'request':meta(request),'commands':records,'frames_manifest':meta(RUN/'frames/frames-manifest.json'),
         'QA_errors':fm['errors'],'QA_warnings':fm['warnings'],'timing_modified':False,
         'new_alpha_contact_GIF_viewed':False,'native_called':False,'ue_import_called':False,'formal_complete_units':0}
(OUT/'extraction-receipt-v001.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'ok':True,'receipt':meta(OUT/'extraction-receipt-v001.json'),'shared_row_fit':fm['rows'][0]['shared_row_fit']}))
