"""Preserve independent component facts of a failed core flow; overall never passes."""
from pathlib import Path
import hashlib,importlib.util,json,sys
sys.dont_write_bytecode=True
R=Path('F:/Ourgame');M=R/'过程图稿与视频/2026-10-19_钟盔装备跳跃三连实录_left_v001'
P=R/'source-assets/production/fairytale-hero-air-v001/production-observer-candidate-v001/tooling-freeze-relative-v002/verify-Air-production-native-v001.py'
assert hashlib.sha256(P.read_bytes()).hexdigest()=='368fe049b5da37711730c701b7877b452a464139b22a63b2f21e243c14780895'
spec=importlib.util.spec_from_file_location('frozen_air_production_checker',P);V=importlib.util.module_from_spec(spec);spec.loader.exec_module(V);C=V.C
c,p,manifest,profile,prereg,archive=C.preflight(M/'preregistration-v001.json',P)
original=M/'原件';r=C.read(original/'runtime-report.json');assert not r['passed'] and not r['flow_complete']
checks={}
for name,fn in [
 ('actual49_GPU_and_editor_source_bytes',lambda:C.verify_gpu(original,r,manifest,profile)),
 ('original_PNG_CRC_FIFO',lambda:dict(movie_frames=len(V.verify_png_fifo(original,r)),passed=True)),
 ('original_main_mix',lambda:C.module(C.AUDIO_CHECKER,'air_failed_original_audio',C.AUDIO_CHECKER_SHA).audit(original/'runtime-report.json',require_frame_timing=True))]:
 try:checks[name]=dict(component_check_returned=True,result=fn())
 except Exception as e:checks[name]=dict(component_check_returned=False,error=repr(e))
out=dict(schema='Root-Air6-failed-core-flow-partial-components-v001',passed=False,core_native_flow_passed=False,original_failure=r['failure'],checker_pin=c.pin(P),root_component_script_pin=c.pin(__file__),native_report_pin=c.pin(original/'runtime-report.json'),checks=checks,NoArmor_pose_mask=r['starter_NoArmor_mask'],Light_pose_masks=[r['light_first_mask'],r['light_second_mask']],visual_reviewed=False,audio_listened=False,FinalAccepted=False)
target=M/'failed-core-partial-component-verification-v001.json'
with target.open('x',encoding='utf-8') as f:json.dump(out,f,ensure_ascii=False,indent=2)
print(json.dumps(dict(report=c.pin(target),overall_passed=False,components={k:v['component_check_returned'] for k,v in checks.items()})))
