"""Preserve the actual v145 build, six saved SoundWaves and honest import recovery."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, shutil
R=Path('F:/Ourgame')
EV=R/'docs/production/first-batch-v2/evidence/HeroLocomotionAudio-v145-v001'
O=R/'source-assets/production/backups/v145-HeroLocomotionAudio303-1425-203GREEN-v001'
def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def pin(p,absolute=False):
 p=Path(p).resolve(); b=p.read_bytes()
 return dict(path=p.as_posix() if absolute else p.relative_to(R).as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def check(row): assert pin(row['path'] if Path(row['path']).is_absolute() else R/row['path'],Path(row['path']).is_absolute())==row,row['path']
def new(p,v):
 with Path(p).open('x',encoding='utf-8') as f: json.dump(v,f,ensure_ascii=False,indent=2)
admitp=EV/'Root-source-admission-v001/actual-source-admission.json'; a=read(admitp)
repairp=EV/'Root-own-first-header-repair-v001/actual-source-repair-admission.json'; repair=read(repairp)
assert a['RootApproved'] and a['actual_applied'] and not a['is_template']
assert repair['RootApproved'] and repair['actual_applied'] and repair['diagnostic_build_actual_exit_code']==0
check(a['predecessor_compiled_manifest']); old=read(a['predecessor_compiled_manifest']['path'])
changed={p['path']:p for p in a['after_files']}; after=repair['after']; check(after)
changed[Path(after['path']).relative_to(R).as_posix()]=pin(after['path'])
ip=EV/'Root-staged-UE-import-v001/reports/ue-import-20261018T203004266177Z.json'; imp=read(ip)
iexitp=EV/'Root-staged-UE-import-v001/exit-receipt-v001.json'; iexit=read(iexitp)
vp=EV/'Root-existing-six-readonly-verify-v001/readonly-verification-v001.json'; verify=read(vp)
vexitp=EV/'Root-existing-six-readonly-verify-v001/process-receipt-v001.json'; vexit=read(vexitp)
assert imp['success'] and imp['actual_imported']==imp['actual_saved']==6
assert iexit['exit_code']==1 and vexit['exit_code']==0 and vexit['os_exit_confirmed']
assert verify['passed'] and not verify['actual_asset_mutations'] and not verify['playback_performed'] and len(verify['rows'])==6
added={}
for item in imp['rows']:
 p=Path(item['saved_uasset']).resolve(); row=pin(p)
 assert row['bytes']==item['saved_bytes'] and row['sha256']==item['saved_sha256']
 matched=[v for v in verify['rows'] if v['cue']==item['cue']]; assert len(matched)==1
 v=matched[0]; assert v['saved_uasset_sha256']==row['sha256'] and v['complete_source_PCM_byte_equal']
 assert v['final_codec']=='ADPCM' and v['final_loading']=='FORCE_INLINE'
 assert p.is_relative_to(R/'UnrealGame/Content/Production/HeroLocomotion/v001/Audio')
 added[row['path']]=row
source=sorted(p for p in (R/'UnrealGame/Source').rglob('*') if p.is_file())
production=sorted(p for p in (R/'UnrealGame/Content/Production').rglob('*') if p.is_file())
olds={p['path'] for p in old['files'] if p['path'].startswith('UnrealGame/Source/')}
oldp={p['path'] for p in old['files'] if p['path'].startswith('UnrealGame/Content/Production/')}
assert {p.relative_to(R).as_posix() for p in source}==olds|set(changed)
assert len(set(changed)-olds)==a['new_source_files']==3 and len(source)==a['actual_source_files']==303
assert {p.relative_to(R).as_posix() for p in production}==oldp|set(added) and len(production)==1425
for row in old['files']:
 if row['path'].startswith(('UnrealGame/Source/','UnrealGame/Content/Production/')) and row['path'] not in changed: check(row)
for row in changed.values(): check(row)
build=R/'UnrealGame/Saved/Bootstrap/last-build.json'; bd=read(build); log=Path(bd['Log'])
assert bd['ExitCode']==0 and log.name=='build-editor-20261019-042828.log'
assert 'Expected DungeonHeroLocomotionAudioNativeV001.h to be first header' not in log.read_text(encoding='utf-8-sig')
suite=R/'UnrealGame/Saved/Automation/FirstRoomNativeRHI-20261019-043415/index.json'; tests=read(suite)
assert tuple(tests[k] for k in ('succeeded','succeededWithWarnings','failed','notRun','inProcess'))==(203,0,0,0,0)
assert len(tests['tests'])==len({t['fullTestPath'] for t in tests['tests']})==203
assert {t['fullTestPath'] for t in tests['tests']}=={t['fullTestPath'] for t in read(old['full_suite']['path'])['tests']}
for t in tests['tests']: assert t['state']=='Success' and t['warnings']==t['errors']==0 and not any(e['event']['type'] in ('Error','Warning') for e in t['entries'])
assert all(d['rHI']=='DirectX 11' for d in tests['devices'])
dll=R/'UnrealGame/Binaries/Win64/UnrealEditor-CodexDungeon.dll'
assert pin(dll)['sha256']=='28926232b808267a164f11524d1bc4828d794d9ffc4645f5d62ae6fd8007b6a7'
assert not O.exists(); O.mkdir()
receipt=O/'actual-six-SoundWave-import-recovery-admission.json'
new(receipt,dict(schema='Root-six-SoundWave-import-recovery-admission-v001',utc=datetime.now(timezone.utc).isoformat(),actual_import_process_exit_code=1,actual_saved_assets=6,initial_import_clean_exit=False,import_receipt=pin(ip,True),import_process_receipt=pin(iexitp,True),fresh_readonly_verification=pin(vp,True),fresh_readonly_process=pin(vexitp,True),fresh_readonly_exit_code=0,original_1419_production_unchanged=True,new_asset_type='SoundWave',added=list(added.values()),runtime_ADPCM_decode_verified=False,native_cue_mix_verified=False,FinalAccepted=False))
files=source+production+[dll,build,log,suite]; pins=[pin(p) for p in files]; copies=[]
for p in source+[R/k for k in added]+[dll,build,log,suite,admitp,repairp,ip,iexitp,vp,vexitp]:
 dst=O/'snapshot'/p.relative_to(R); dst.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(p,dst)
 assert pin(p)['sha256']==pin(dst)['sha256']; copies.append(dict(source=pin(p),copy=pin(dst)))
for _ in range(2):
 for row in pins: check(row)
cm=O/'compiled-source-manifest.json'
new(cm,dict(schema='Root-hero-locomotion-audio-full203-GREEN-build-v001',utc=datetime.now(timezone.utc).isoformat(),source_files=len(source),production_files=len(production),production_textures=1419,production_new_SoundWaves=6,registered_tests=203,passed=203,failed=0,notRun=0,full_suite=pin(suite,True),build=pin(build,True),build_log=pin(log,True),files=pins,copies=copies,source_admission_pin=pin(admitp,True),source_repair_admission_pins=[pin(repairp,True)],content_admission_pin=pin(receipt,True),verification_passes=2,twoSHA_mismatches=0,old203_tests_unchanged=True,native_audio_verified=False,formal_complete_units=0,completed_combinations=0,FinalAccepted=False))
print(json.dumps(pin(cm,True),ensure_ascii=False))
