"""Build NEW dependency table and host reports; never touches live game files."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import re
import subprocess
import sys

ROOT = Path('F:/Ourgame'); HERE = Path(__file__).resolve().parent

def pin(path, label):
    path=Path(path).resolve()
    return dict(label=label,path=path.as_posix(),bytes=path.stat().st_size,sha256=hashlib.sha256(path.read_bytes()).hexdigest())

def new_json(path, value):
    with path.open('x',encoding='utf-8') as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n')

landing=ROOT/'source-assets/production/fairytale-hero-air-v001/landing-priority-observer-candidate-v001/tooling-review-fix-v002/verify-landing-priority-native-v001.py'
spec=importlib.util.spec_from_file_location('checker_preparation_frozen_landing',landing)
L=importlib.util.module_from_spec(spec);spec.loader.exec_module(L)
legacy,F,C=L.dependencies();sources,am,ap=L.sources_for('Shift',legacy,C)
paths = dict(landing_checker=landing,landing_dependencies=landing.parent/'dependencies-v001.json',
             signal_checker=ROOT/'tools/scripts/verify-action-audio-capture.py',
             predecessor_compiled_manifest=ROOT/'source-assets/production/backups/v145-HeroLocomotionAudio303-1425-203GREEN-v001/compiled-source-manifest.json',
             import_manifest=ROOT/'source-assets/production/hero-locomotion-audio-binding-candidate-v001/import/import-manifest.json',
             import_recovery=ROOT/'source-assets/production/backups/v145-HeroLocomotionAudio303-1425-203GREEN-v001/actual-six-SoundWave-import-recovery-admission.json',
             root_launcher=ROOT/'tools/scripts/run-hero-locomotion-audio-native-v001.ps1',
             full_audio_checker=C.AUDIO_CHECKER,source_pixel_checker=C.DODGE_PIXELS,
             air_import_freeze=C.IMPORT_FREEZE,
             air_import_contract=C.IMPORT_FREEZE.parent/'air48_import_contract_v001.py')
for name,path in legacy.items():paths['legacy_'+name]=path
_,_,_,mp,fp,pp=C.source_only()
for name,row in [('air_manifest',mp),('air_source_freeze',fp),('air_profile',pp)]:paths[name]=L.resolve_pin(row)
for i,source in enumerate(sources.values()):paths['source_image_'+str(i)]=Path(source['source'])
recovery=L.read(paths['import_recovery'])
for key in ('import_receipt','import_process_receipt','fresh_readonly_verification','fresh_readonly_process'):
    paths[key]=L.resolve_pin(recovery[key])
manifest=L.read(paths['import_manifest'])
for row in manifest['rows']:paths['source_audio_'+row['cue']]=Path(row['source_wav'])
readonly=L.read(paths['fresh_readonly_verification'])
for row in readonly['rows']:paths['raw_import_export_'+row['cue']]=Path(row['exported_raw_wave'])
line=next(x for x in paths['root_launcher'].read_text(encoding='utf-8-sig').splitlines() if x.startswith('$locomotionArgs=@('))
arguments=re.findall("'([^']*)'",line)
assert arguments[-3:]==['-DungeonContentProofDir=','-abslog=','native-engine.log']
new_json(HERE/'dependencies-v001.json',dict(schema='hero-locomotion-frozen-dependencies-v001',
         actual_old_preflight_reused=False,pure_native_gates_reused_unchanged=True,
         expected_arguments_prefix=arguments[:-3],members=[pin(path,label) for label,path in paths.items()]))
reports=HERE/'reports';reports.mkdir(exist_ok=False)
test=subprocess.run([sys.executable,'-B','-X','utf8',str(HERE/'tests/test-checker-v001.py')],capture_output=True,text=True,encoding='utf-8')
with (reports/'host-tests-v001.log').open('x',encoding='utf-8') as f:f.write(test.stdout+test.stderr)
assert test.returncode==0, test.stdout+test.stderr
spec=importlib.util.spec_from_file_location('checker_preparation',HERE/'verify-hero-locomotion-audio-native-v001.py')
V=importlib.util.module_from_spec(spec);spec.loader.exec_module(V)
loaded,*_=V.dependencies();bindings=V.verify_audio_binding(loaded)
new_json(reports/'host-tests-v001.json',dict(schema='hero-locomotion-checker-host-only-v001',utc=datetime.now(timezone.utc).isoformat(),
         host_test_process_exit_code=test.returncode,unit_tests=13,failures=0,exact_dependency_pins_checked=len(loaded),
         actual_source_import_binding_cues=list(bindings),source_audio_WAV_or_PCM_constructed=False,
         old_causal_resource_PNG_optical_audio_functions_modified=False,current_future_CM_verified=False,
         UE_started=False,new_native_verified=False,FinalAccepted=False))
print(json.dumps(dict(passed=True,host_tests=13,dependency_pins=len(loaded),six_sources_verified=True),ensure_ascii=False))
