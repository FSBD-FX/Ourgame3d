"""Prepare one exclusive Root default EquipmentBound Ready-entry session; never launch UE."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,importlib.util,json,re,sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('ready_prereg_checker',HERE/'verify-ready-entry-native-v001.py');V=importlib.util.module_from_spec(spec);spec.loader.exec_module(V)
ap=argparse.ArgumentParser();ap.add_argument('--version',required=True);ap.add_argument('--checker-freeze',required=True);ap.add_argument('--compiled-manifest',required=True);ap.add_argument('--source-admission',required=True);a=ap.parse_args()
V.need(re.fullmatch(r'v[0-9]{3}',a.version) is not None,'Unique vNNN required')
f=V.read(V.check(V.pin(a.checker_freeze)))
for row in f['members']+f['dependency_pins']:V.check(row)
for name in ('verify-ready-entry-native-v001.py','prepare-ready-entry-prereg-v001.py','run-ready-entry-native-v001.ps1','ready-entry-source-contract-v001.json','required-pins-v001.json'):
 V.need(any(V.same(x,V.pin(HERE/name)) for x in f['members']),'Required actual tool/config missing from selected freeze')
pre=V.preflight(a.compiled_manifest,a.source_admission)
archive=V.ROOT/('过程图稿与视频/'+datetime.now().strftime('%Y-%m-%d')+'_钟盔258Ready入口_'+a.version)
V.need(not archive.exists(),'Never overwrite any previous native archive')
archive.mkdir();(archive/'原件').mkdir();(archive/'展示副本').mkdir()
value=dict(schema='Root-primary1-bridge258-ready-entry-prereg-v001',RootApproved=True,is_template=False,pre_registered_before_capture=True,
 created_utc=datetime.now(timezone.utc).isoformat(),run_directory=archive.as_posix(),compiled_manifest_pin=pre['compiled_manifest_pin'],source_admission_pin=pre['source_admission_pin'],
 checker_freeze_pin=V.pin(a.checker_freeze),checker_pin=V.pin(HERE/'verify-ready-entry-native-v001.py'),launcher_pin=V.pin(HERE/'run-ready-entry-native-v001.ps1'),
 source_screen_contract_pin=V.pin(HERE/'ready-entry-source-contract-v001.json'),arguments=V.expected_arguments(archive),
 expected_default_side=-1,QA_registered_sources=True,lawful_source_acceptance=False,isolated_J1_to_Ready=False,
 expected_full_flow='Enter/E/A cancel/E commit/3Ready/J1 all6/J2 all6/J3 all6/3Ready/MED replace/original LGT retake',
 Knight_cleanup=False,forced_pose_HP_AI_position_time=False,maximum_render_FPS=30,fixed_time_step=False,audio_recorded=False,OPEN=list(V.OPEN),FinalAccepted=False)
path=archive/'preregistration-v001.json'
with path.open('x',encoding='utf-8') as file:json.dump(value,file,ensure_ascii=False,indent=2);file.write('\n')
print(json.dumps(dict(archive=archive.as_posix(),preregistration=V.pin(path)),ensure_ascii=False))
