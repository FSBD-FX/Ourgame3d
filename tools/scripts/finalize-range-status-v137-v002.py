"""Refresh all current accounting aliases and source-preparation facts, preserving old evidence."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,re,shutil
R=Path('F:/Ourgame');D=R/'docs/production/first-batch-v2';H=R/'source-assets/production/fairytale-hero-state-gap-v001'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def pin(p):return dict(path=p.as_posix(),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())
out=D/'evidence/combat-range-cleanup-v001/source-preparation-status-v137-v002';assert not out.exists();out.mkdir(parents=True)
shutil.copy2(D/'progress.json',out/'before-progress.json')
p=read(D/'progress.json');l=read(R/'source-assets/production/first-unit-animation-v003/generation-ledger.json')
assert l['requested_count']>=240 and not any(x['status']=='requested_pending' for x in l['requests'])
ret=[]
for f in Path('E:/OurGame/Knight/过程图稿与视频').glob('2026-10-18-OurgameUE-*'):
 match=re.search(r'-v(\d+)$',f.name)
 if not match or int(match.group(1))<469:continue
 index=next((f/n for n in ['source-size-SHA256.json','retention-verification-v001.json'] if (f/n).is_file()),None);assert index,f
 ret.append(dict(number=int(match.group(1)),index=pin(index)))
ret.sort(key=lambda x:x['number']);assert ret and ret[0]['number']==469
known=[x['number'] for x in ret];assert known==list(range(469,known[-1]+1))
account=dict(requested=l['requested_count'],window=l['current_window'],remaining=l['remaining_batch_requests'],lifetime=l['lifetime_requested_count'],external_api_calls=l['external_api_calls'],host_fee_usd=l['host_fee_usd'],automatic_follow_on_batches_authorized=l['automatic_follow_on_batches_authorized'])
p['current_generation_accounting']=account
p['generation_accounting_current']=dict(requested_count=l['requested_count'],current_window_number=l['current_window']['number'],window_requested=l['current_window']['requested_count'],window_remaining=l['remaining_batch_requests'],lifetime_requested_count=l['lifetime_requested_count'],external_api_calls=0,host_fee_usd=None,all_native_outputs_retained=True)
p['generation'].update(current_window=l['current_window'],current_window_remaining=l['remaining_batch_requests'],EV039_and_later_requested=l['requested_count'],production_generation_requested_excluding_initial_references=l['lifetime_requested_count'],total_host_image_requests_including_initial3_references=l['lifetime_requested_count']+3,generation_count_observed_at=datetime.now(timezone.utc).isoformat(),current_single_visual_writer='/root',legacy_setup_batch_fields_are_historical=True)
p.update(next_native_request=l['requested_count']+1,next_media_retention_batch=known[-1]+1,next_retention_batch=known[-1]+1,updated_utc=datetime.now(timezone.utc).isoformat(),current_task='默认Guard范围线清理已完整验证；继续Dodge腋孔局部编辑配准及Death40装备源接入准备，新增动作源未导入')
p['current_turn_media_retention']=dict(first='E469',last='E'+str(known[-1]),batches=len(ret),two_size_SHA_passes=True,mismatches=0,E_root_README_unchanged=True,large_native_originals='E479/E481/E486 exact ZIP members; F originals unchanged')
p['current_turn_media_retained']=dict(F_E_batches=['E'+str(x) for x in known],hash_mismatches=0,verification_passes=2,root_readme_unchanged=True,large_originals_lossless_ZIP=True)
p['previous_current_retention_batches_before_v137']=p.get('current_retention_batches',[]);p['current_retention_batches']=[x['index'] for x in ret]
state=p['current_hero_Dodge_Death_equipment_sources']
state.update(native_ids=list(range(234,l['requested_count']+1)),new_native_calls=l['requested_count']-233,generated_component_poses_including_corrections=27+4*(l['requested_count']-239),logical_component_poses=27,Production_imported=False,Dodge_current_sourcefit_accepted=False,Death_current_sourcefit_accepted=False,Dodge_known_defect='Chest234 and240 phase1/2 armhole-to-fixed-buckle mismatch remains under actual original-owner controls;240 truegreen apertures improved butgeometry rejected. Local native edit241 has been generated and retained; post-edit preservation and fit still require evidence.',Death_known_defect='Late own-hand/helmet and sleeve segmentation corrected in candidatev005; rendered sourcefitv003+clear-releasev002 viewed and allowed as limited native-ready preparation only. Native integration and transitions still pending.',Death40_native_ready_author_freeze=pin(H/'death-state-preparation-v001/Death40-native-ready-author-candidate-v002/native-ready-author-freeze-v002.json'),Death_limited_sourcefit_review_passed_for_native_preparation=True,Root_Death40_source_review=pin(H/'Root-Death40-source-review-native-preparation-v001.json'),Death_runtime_current_gap='Current fairytale equipment presentation owns dead pawn but uses bare Ready0 fallback. Existing terminal AnimationTime continues while sim/kernel stops; requires distinct Death5 render branch. Real inventory/drop must stay unchanged.',next='Finish actual localized241 preservation/sourcefit review. Then Death40 native actual import/terminal display/real HP0 tests and bilateral proof.',body_pixels_repainted=False,full_state_runtime_accepted=False)
report=dict(schema='v137-source-preparation-and-current-accounting-status-v002',UTC=p['updated_utc'],Source=246,Production=1286,compiled_snapshot='v137-range187G',strict_UE187_unchanged=True,accounting=account,retention=ret,source_preparation=state,formal_complete_units=0,goal_status='active')
(out/'source-preparation-and-accounting-v002.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(D/'progress.json').write_text(json.dumps(p,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(requested=l['requested_count'],window=l['current_window']['number'],window_used=l['current_window']['requested_count'],last_E=known[-1],retained_batches=len(ret),source_runtime_unchanged=True,formal_complete_units=0),ensure_ascii=False))
