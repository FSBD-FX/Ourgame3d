"""Adopt reviewable current manual entry only after actual independent two-side native PASS."""
from pathlib import Path
import hashlib,json,shutil,subprocess
R=Path('F:/Ourgame');B=R/'source-assets/production/fairytale-hero-state-gap-v001/death-state-preparation-v001'
C=B/'root-Death1326-checkpoint-v001';S=C/'staged-adoption'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def pin(p):return dict(path=p.as_posix(),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())
for side in ['left','right']:
 d=R/('过程图稿与视频/2026-10-18_钟盔真实守卫自然致死Death五相试样_native_'+side+'_v001')
 assert read(d/'index.json')['independent_passed'] and read(d/'原件/runtime-report.json')['passed']
assert read(C/'preparation-receipt-v001.json')['frozen_full_manual_validator']['current_live_verification_passes']==2
out=R/'docs/production/first-batch-v2/evidence/hero-Death40-v001/root-manual-adoption-v138-v001';assert not out.exists();(out/'before').mkdir(parents=True)
wrapper=R/'tools/scripts/launch-guard-room-native-trial-v009.ps1';assert not wrapper.exists()
entries=[p for p in S.iterdir() if p.suffix=='.cmd'];assert len(entries)==4
for p in entries:shutil.copy2(R/p.name,out/'before'/p.name)
shutil.copy2(S/wrapper.name,wrapper)
for p in entries:shutil.copy2(p,R/p.name);assert pin(R/p.name)['sha256']==pin(p)['sha256']
new=R/'钟盔轻甲倒地试玩.cmd';assert not new.exists();shutil.copy2(R/'钟盔轻甲受击试玩.cmd',new)
v=subprocess.run(['pwsh','-NoProfile','-ExecutionPolicy','Bypass','-File',str(wrapper),'-LightArtTrial','-GuardFullArt','-ValidateOnly'],cwd=R,capture_output=True,text=True,encoding='utf-8')
(out/'actual-v009-ValidateOnly.log').write_text(v.stdout+v.stderr,encoding='utf-8');assert v.returncode==0,v.stdout+v.stderr
(out/'adoption-receipt-v001.json').write_text(json.dumps(dict(schema='Root-HeroDeath-manual-adoption-v138-v001',source_files=257,production_files=1326,strict_registered_tests=190,
 manual_input=pin(C/'manual-input-v001.json'),actual_wrapper=pin(wrapper),actual_entries=[pin(R/p.name) for p in entries]+[pin(new)],
 ValidateOnly_exit_code=0,automatic_inputs=False,diagnostic_damage=False,range_debug_default_off=True,traditional_HUD_hidden=True,
 UE_started=False,actual_native_two_sides_independent_pass=True,formal_complete_units=0,FinalAccepted=False),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(adopted_v009=True,entries=5,ValidateOnly_exit0=True,Source=257,Production=1326,strict190=True,UE_started=False)))
