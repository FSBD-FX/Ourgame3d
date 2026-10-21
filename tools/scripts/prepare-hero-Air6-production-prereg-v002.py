"""Root preregisters real finite Air capture only after current296/full203 GREEN."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,json,re
R=Path('F:/Ourgame');BASE=R/'source-assets/production/fairytale-hero-air-v001';OBS=BASE/'production-observer-candidate-v001';TOOL=OBS/'tooling-freeze-relative-v002'
EV=R/'docs/production/first-batch-v2/evidence/HeroAir6-v142-v001'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def pin(p):
 p=p.resolve();b=p.read_bytes();return dict(path=p.as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def need(v,s):
 if not v:raise ValueError(s)
def write_new(p,d):
 with p.open('x',encoding='utf-8') as f:json.dump(d,f,ensure_ascii=False,indent=2)
 return pin(p)
ap=argparse.ArgumentParser();ap.add_argument('--side',choices=['left','right'],required=True);ap.add_argument('--compiled296',required=True);ap.add_argument('--version',default='v002');ap.add_argument('--observer-source-freeze',required=True);ap.add_argument('--observer-admission',required=True);ap.add_argument('--checker-directory',required=True);ap.add_argument('--checker-protocol',required=True);a=ap.parse_args();need(re.fullmatch(r'v[0-9]{3}',a.version),'Explicit version required');TOOL=Path(a.checker_directory).resolve();need(TOOL.is_relative_to(BASE),'Checker must be a retained project candidate')
cm=Path(a.compiled296).resolve();d=read(cm);need(d['source_files']==296 and d['production_files']==1419 and d['passed']==203 and d['failed']==0 and d['notRun']==0,'Fresh actual296/1419/full203 GREEN required')
suite=Path(d['full_suite']['path']);q=read(suite);need(tuple(q[k] for k in ['succeeded','succeededWithWarnings','failed','notRun','inProcess'])==(203,0,0,0,0),'Strict203 GREEN required')
rows={r['path']:r for r in d['files']};need(len(rows)==len(d['files']),'Unique compiled paths required')
for sub,n in [('UnrealGame/Source',296),('UnrealGame/Content/Production',1419)]:
 actual={p.relative_to(R).as_posix() for p in (R/sub).rglob('*') if p.is_file()};expected={r for r in rows if r.startswith(sub+'/')};need(actual==expected and len(actual)==n,'Actual compiled membership drift '+sub)
for repeat in range(2):
 for row in d['files']:
  p=R/row['path'];z=pin(p);need((z['bytes'],z['sha256'])==(row['bytes'],row['sha256']),'Actual compiled bytes changed '+row['path'])
obs_ad=Path(a.observer_admission).resolve();ob=read(obs_ad)
need(ob['RootApproved'] is True and ob['actual_applied'] is True and ob['is_template'] is False,'Actual observer Source admission required')
for row in ob['after_files']:need(rows[row['path']]==row,'Observer admission differs from current CM')
rhi=EV/'observer-RHI-link-repair-v001/actual-source-repair-admission.json';rh=read(rhi);rp=Path(rh['after']['path']);rrel=rp.relative_to(R).as_posix();need(pin(rp)==rh['after'] and (rows[rrel]['bytes'],rows[rrel]['sha256'])==(rh['after']['bytes'],rh['after']['sha256']),'Actual direct RHI source admission not current')
prod_freeze=BASE/'production-candidate-v001/full-production-v001/HeroAir-full-production-candidate-freeze-v001.json';source_probe=Path(a.observer_source_freeze).resolve();checker_freezes=list(TOOL.glob('Air-production-proof-checker-freeze-v*.json'));need(len(checker_freezes)==1,'One exact checker freeze required');checker_freeze=checker_freezes[0]
for p in [prod_freeze,source_probe,checker_freeze,BASE/'import-tooling-candidate-v002/Air48-import-tooling-freeze-v002.json']:
 f=read(p)
 for repeat in range(2):
  for row in f['members']:
   member=Path(row['path']);member=member if member.is_absolute() else p.parent/member;z=pin(member);need((z['bytes'],z['sha256'])==(row['bytes'],row['sha256']),'Frozen member changed')
bindings=EV/('Root-final-admission-bindings-'+pin(cm)['sha256'][:16]);binding=bindings/'production-six-current-source-binding.json'
ix=read(prod_freeze.parent/'full-production-admission-index-v001.json');after=[]
for row in ix['files']:
 if row['actual'].endswith('/DungeonHUD.cpp'):continue
 current=rows[row['actual']];need((current['bytes'],current['sha256'])==(row['after_bytes'],row['after_sha256']),'Production source after changed');after.append(current)
need(len(after)==6,'Six unoverlaid final production source files required')
bd=dict(schema='Root-HeroAir6-production-final-source-binding-v001',RootApproved=True,is_template=False,actual_applied=True,candidate_freeze=pin(prod_freeze),after_files=after,original_seven_source_actual_admission=pin(EV/'Root-production-admission-v001/actual-source-admission.json'),current_observer_overlay_admission=pin(obs_ad),supplemental_direct_RHI_actual_admission=pin(rhi),compiled_manifest=pin(cm),historical_HUD_overlay='FullHUD6f86936 admitted first; observerHUD02b33839 overlays it and is verified by separate three-source admission. Six remaining production files are current.',FinalAccepted=False)
if binding.exists():need(read(binding)==bd,'Existing final binding belongs to different actual build')
else:bindings.mkdir(parents=True,exist_ok=True);write_new(binding,bd)
M=R/f'过程图稿与视频/2026-10-19_钟盔装备跳跃三连实录_{a.side}_{a.version}';need(not M.exists(),'New archive/version required; preserve earlier originals')
(M/'原件').mkdir(parents=True);(M/'展示副本').mkdir()
imports=BASE/'Root-Air48-import-v002';run=imports/'native-run-20261019-005529-6566102'
reg=dict(schema='hero-Air6-Root-prereg-v001',utc=datetime.now(timezone.utc).isoformat(),RootApproved=True,is_template=False,pre_registered_before_capture=True,FinalAccepted=False,requested_facing=-1 if a.side=='left' else 1,diagnostic_clear_knight=True,root_run_directory=M.as_posix(),checker_pin=pin(TOOL/'verify-Air-production-native-v001.py'),checker_freeze_pin=pin(checker_freeze),source_probe_freeze_pin=pin(source_probe),production_candidate_freeze_pin=pin(prod_freeze),prepared_profile_pin=pin(BASE/'native-ready-candidate-v001/Air-runtime-profile-data-v001.json'),source_manifest_pin=pin(BASE/'native-ready-candidate-v001/import-Air48-v001.json'),source_freeze_pin=pin(BASE/'native-ready-candidate-v001/Air48-native-ready-freeze-v001.json'),import_tooling_freeze_pin=pin(BASE/'import-tooling-candidate-v002/Air48-import-tooling-freeze-v002.json'),compiled_manifest_pin=pin(cm),expected_source_files=296,expected_production_files=1419,strict_full203_pin=pin(suite),production_Source_admission_pin=pin(binding),observer_Source_admission_pin=pin(obs_ad),import_manifest_pin=pin(imports/'import-manifest.json'),import_native_receipt_pin=pin(run/'actual-native-import-receipt.json'),import_independent_receipt_pin=pin(run/'independent-saved-byte-verification.json'),supplemental_direct_RHI_source_admission_pin=pin(rhi),checker_protocol_pin=pin(Path(a.checker_protocol)),preparer_pin=pin(Path(__file__)),normal_inputs_automated=True,human_inputs=False,scope='Three normal Space jumps: starter None6, real display-source registration+E LGT9, original landing half-open re-jump; explicit Knight public diagnostic only; no player/Guard HP/position/AI/time writes. Additional actions/listening/final visual/formal pairs remain open.')
reg_pin=write_new(M/'preregistration-v001.json',reg)
(M/'README.md').write_text('正常输入无甲跳跃→真实显示源E穿轻甲→轻甲跳跃→原落地窗口再次起跳。Knight明确public诊断清理，不改Player/Guard或时间。新49资源/原生PNG/混音、独立核验与展示留档；未核验、未审阅时不代表美术或正式内容完成。所有图像须F原件与展示副本→E原字节保全后才查看。\n',encoding='utf-8')
print(json.dumps(dict(media=M.as_posix(),preregistration=reg_pin),ensure_ascii=False))
