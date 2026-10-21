"""Root actual pre-registration for one fresh landing J/Shift native case."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,json,hashlib,re
R=Path('F:/Ourgame');C=R/'source-assets/production/fairytale-hero-air-v001/landing-priority-observer-candidate-v001';T=C/'tooling'
def pin(p):
 p=Path(p);b=p.read_bytes();return dict(path=str(p),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
ap=argparse.ArgumentParser();ap.add_argument('--action',choices=['J','Shift'],required=True);ap.add_argument('--side',choices=['left','right'],required=True);ap.add_argument('--version',default='v001');ap.add_argument('--checker-freeze',required=True);a=ap.parse_args();assert re.fullmatch(r'v[0-9]{3}',a.version)
freeze=Path(a.checker_freeze).resolve();assert freeze.is_relative_to(C) and freeze.is_file(),'One explicit frozen Task2 verifier required';f=read(freeze)
for repeat in range(2):
 for row in f['members']:
  p=Path(row['path']);z=pin(p);assert (z['bytes'],z['sha256'])==(row['bytes'],row['sha256']),row['path']
lineage=read(T/'Root-actual-input-pins-v001.json')
for row in lineage.values():
 if isinstance(row,dict) and {'path','bytes','sha256'}<=row.keys():
  p=Path(row['path']);z=pin(p);assert (z['bytes'],z['sha256'])==(row['bytes'],row['sha256'])
M=R/f'过程图稿与视频/2026-10-19_钟盔落地{a.action}_{a.side}_{a.version}';assert not M.exists(),'New archive version required, preserve all failures';M.mkdir();(M/'原件').mkdir();(M/'展示副本').mkdir()
p=read(T/'Root-prereg-TEMPLATE-v001.json');p.update(RootApproved=True,is_template=False,pre_registered_before_capture=True,created_utc=datetime.now(timezone.utc).isoformat(),requested_action=a.action,requested_facing=-1 if a.side=='left' else 1,diagnostic_clear_knight=True,run_directory=str(M),checker_freeze_pin=pin(freeze),FinalAccepted=False)
for key in ('compiled_manifest_pin','source_admission_pin','source_repair_admission_pin','source_candidate_freeze_pin'):p[key]=lineage[key]
p['preparer_pin']=pin(Path(__file__).resolve());p['capture_scope']='Normal Enter/D movement/E real .50 action/completed brown Ready/Space/completed Land4/queued J or Shift/real action/Ready2; explicit predecessor Knight diagnostic. No player/Guard HP/position/AI/clock writes. Full playback/listening/final art and save restore remain open.'
out=M/'preregistration-v001.json'
with out.open('x',encoding='utf-8') as f:json.dump(p,f,ensure_ascii=False,indent=2)
with (M/'README.md').open('x',encoding='utf-8') as f:f.write('落地动作衔接原生受控实录。正常Enter/WASD/E/Space/J或Shift；真实换装时间与落地动作Start独立记录。Knight为明确public诊断清理，非整房通关；未核验／未保全前不View，完整原速播放及试听未完成，正式内容不计完成。\n')
print(json.dumps(dict(media=str(M),preregistration=pin(out)),ensure_ascii=False))
