"""Actual sprite-gen five steps for three already retained Air6 armor candidates."""
from pathlib import Path
import hashlib,json,shutil,subprocess,sys
import numpy as np
from PIL import Image
R=Path('F:/Ourgame');B=R/'source-assets/production/fairytale-hero-state-gap-v001/air-state-preparation-v001'
SG=Path('C:/Users/22499/.codex/skills/sprite-gen');PY=SG/'.venv/Scripts/python.exe';assert Path(sys.executable).resolve()==PY.resolve()
hand=json.loads((B/'armor-standard-input-v001/input-handoff-v001.json').read_text(encoding='utf-8'))
M=R/'过程图稿与视频/2026-10-19_钟盔Air6棕皮18件共享提取_v001';assert not M.exists();(M/'原件').mkdir(parents=True);(M/'展示副本').mkdir()
wrapper=R/'source-assets/production/fairytale-hero-state-gap-v001/lgt-hurt4-process-runs-v001/process-inputs-v001/shared-HD-fit-explicit-component-min-UNCHANGED.py'
assert hashlib.sha256(wrapper.read_bytes()).hexdigest()=='61085b282e1f18d0195cad5f65355b67eda287a98e54a19f27c8d662f9d079f4'
def pin(p):return dict(path=p.as_posix(),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())
receipts=[]
for row in hand['rows']:
 token={'Chest':'chest','ShoulderNear':'nearshoulder','ShoulderFar':'farshoulder'}[row['component']];state=row['state'];run=B/'armor-process-runs-v001'/token/'run-shared-HD-v001';assert not run.exists()
 shutil.copytree(Path(row['run']),run);raw=Path(row['output']);target=run/'raw'/f'{state}.png';target.parent.mkdir(exist_ok=True);shutil.copy2(raw,target)
 assert pin(Path(row['request']['path']))==row['request'] and (run/'sprite-request.json').read_bytes()==Path(row['request']['path']).read_bytes()
 minimum=row['min_used_pixels'];assert minimum=={'Chest':512,'ShoulderNear':512,'ShoulderFar':256}[row['component']]
 cmds=[('extract',[str(PY),'-B','-X','utf8',str(wrapper),'--run-dir',str(run),'--min-used-pixels',str(minimum)]),('compose',[str(PY),'-B','-X','utf8',str(SG/'scripts/compose_sprite_atlas.py'),'--run-dir',str(run),'--min-used-pixels',str(minimum)]),('curated',[str(PY),'-B','-X','utf8',str(SG/'scripts/export_curated_pngs.py'),'--run-dir',str(run),'--state',state]),('preview',[str(PY),'-B','-X','utf8',str(SG/'scripts/preview_animation.py'),'--run-dir',str(run)]),('inspect',[str(PY),'-B','-X','utf8',str(SG/'scripts/inspect_sprite_run.py'),'--run-dir',str(run)])]
 receipt=dict(component=row['component'],raw=pin(raw),run=run.as_posix(),shared_scale=True,per_pose_fit=False,min_used_pixels=minimum,commands=[],accepted=False,imported=False)
 try:
  for name,argv in cmds:
   r=subprocess.run(argv,capture_output=True,text=True,encoding='utf-8',errors='replace');log=run/'pipeline-logs'/f'{name}.log';log.parent.mkdir(exist_ok=True);log.write_text(r.stdout+r.stderr,encoding='utf-8');receipt['commands'].append(dict(stage=name,exit_code=r.returncode,log=pin(log)));assert r.returncode==0,(token,name,r.stderr)
  fm=json.loads((run/'frames/frames-manifest.json').read_text(encoding='utf-8'));qa=json.loads((run/'sprite-inspect.report.json').read_text(encoding='utf-8'));assert fm['ok'] and not fm['errors'] and qa['ok'] and not qa['errors']
  assert fm['rows'][0]['frames']==6 and not fm['rows'][0]['shared_row_fit']['per_frame_scale_normalization']
  receipt.update(extraction=fm,inspect=qa,success=True,frames=[])
  for i in range(6):
   p=run/'curated'/f'frame-{i}.png';a=np.array(Image.open(p));assert a.shape==(512,512,4);receipt['frames'].append(dict(frame=i,file=pin(p),rgba_sha256=hashlib.sha256(a.tobytes()).hexdigest(),alpha_nonzero=int(np.count_nonzero(a[:,:,3]))))
 except BaseException as ex:receipt.update(success=False,failure=repr(ex));raise
 finally:
  rp=run/'Root-five-step-process-receipt-v001.json';rp.write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');receipts.append(pin(rp));shutil.copytree(run,M/'原件'/token)
  for p in (run/'qa').glob('*'):
   if p.is_file():shutil.copy2(p,M/'展示副本'/(token+'-'+p.name))
shutil.copy2(Path(__file__),M/'原件'/Path(__file__).name)
(M/'source-version-status-index.json').write_text(json.dumps(dict(status='18 exact extracted candidate component PNGs; source fitting and E/View pending',receipts=receipts,accepted=False,imported=False,files=[pin(p) for p in sorted(M.rglob('*')) if p.is_file()]),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(M/'README.md').write_text('钟盔非攻击Air6配套胸衣/近肩/远肩，共18件候选。实际sprite-gen五步、全行共同缩放；预声明Chest/Near512、Far256像素下限保持。作者预览不是游戏时钟。原始检查警告保留，未试装或导入。E两SHA后才可View。\n',encoding='utf-8')
print(json.dumps(dict(archive=M.as_posix(),components=3,frames=18,receipts=receipts),ensure_ascii=False))
