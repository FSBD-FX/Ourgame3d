from pathlib import Path
import json,hashlib
R=Path('F:/Ourgame');B=R/'source-assets/production/fairytale-lgt-readability-v003/row-correction-v004'
def desc(p):
 b=p.read_bytes();return dict(path=p.as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
p=B/'lgt-far-tiny-tab-edit-input-draft-v004.json';assert desc(p)['sha256']=='4d6057722e58befa7f7539d22d1b220de42d5c7c1e8f2e81f02cb39c9369f369'
v=json.loads(p.read_text(encoding='utf-8-sig'));row=v['rows'][0]
assert row['component']=='FarShoulder' and row['standard_prepare_exit_code']==0 and len(row['reference_images_in_order'])==1
assert row['durations_ms']==[167]*4 and row['future_component_A']==[None]*4 and row['generation_ready'] is False
assert desc(Path(row['prompt']['path']))==row['prompt']
for ref in row['reference_images_in_order']:
 assert desc(Path(ref['file']['path']))==ref['file'] and ref['file']['sha256']=='eaa352de4a9eba6386985d48c5c7a07e59a70f1bc969f63ca2b1667ac5e9e4d1'
 ref['role']='single_exact_original_native182_edit_target_only'
review=B/'root-far-tiny-tab-review187-v001.json';assert not review.exists()
review.write_text(json.dumps(dict(source_draft=desc(p),actual_prior_views=['182 raw/E257','185 raw/E269'],independent_perspective_review=desc(R/'source-assets/production/fairytale-lgt-readability-v003/far185-perspective-review-v001/perspective-review-v001.json'),scope='One native edit of original182 rightmost tiny far tabs, 4 locator ROIs±8px not masks. Broad near cap/long ring rejected. No A or runtime acceptance.',producer_metadata_carryover_corrected=['near183 schema','183 ref role','186 planned label','source_root_review_report'],formal_complete_units=0),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
row.update(generation_ready=True,target_mounts_are_measured=False,native_request_number=187)
v.update(schema='far182-tiny-right-tabs-edit-approved187-v005',generation_ready=True,root_input_review=desc(review),source_root_review_report='Root and independent reviewer actually viewed E257 original182 and E269 failed185; edit original182 with four approximate ROI locator windows. Not a mask or an attachment point.')
v.pop('planned_186_is_not_a_ledger_reservation',None);v['planned_187_is_not_a_ledger_reservation']=True
q=B/'lgt-far-tiny-tab-approved187-v005.json';assert not q.exists();q.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(handoff=q.as_posix(),target_native=182,planned_native187=True)))
