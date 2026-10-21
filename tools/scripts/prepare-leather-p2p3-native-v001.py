"""Root review admission and automatic accounting window rollover, no generation."""
from pathlib import Path
import copy, datetime, hashlib, json
R=Path('F:/Ourgame'); B=R/'source-assets/production/fairytale-lgt-readability-v003'
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def desc(p):
 b=p.read_bytes();return dict(path=p.as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def write(p,v):
 assert not p.exists(),p
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
L=R/'source-assets/production/first-unit-animation-v003/generation-ledger.json';l=load(L)
assert l['requested_count']==192 and l['remaining_batch_requests']==0
assert l['automatic_follow_on_batches_authorized'] and l['current_window']['number']==8 and l['current_window']['requested_count']==24
assert [x['request_number'] for x in l['requests']]==list(range(1,193))
checks=[]
for x in l['requests'][-24:]:
 assert x['status']!='requested_pending'
 p=x['canonical_raw'];assert desc(Path(p['path']))==p
 checks.append(dict(request_number=x['request_number'],status=x['status'],canonical_raw=p))
review=B/'generation-control-v001/window008-close-review-v001.json'
write(review,dict(created_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),requests=checks,zero_source_mismatch=True,formal_complete_units=0,acceptance='Status preserved per request; raw availability is not full animation acceptance'))
frozen=L.with_name('generation-ledger-window008-frozen.json');write(frozen,l)
closed=copy.deepcopy(l['current_window']);closed.update(status='closed_full24_raw_sources_verified',frozen_ledger=desc(frozen),review=desc(review));l['completed_windows'].append(closed)
l['current_window']=dict(number=9,first_request_number=193,last_request_number=216,request_limit=24,requested_count=0,status='auto_authorized_active')
l['accounting_window_id']='window009';l['batch_requested_count']=0;l['remaining_batch_requests']=24
L.write_text(json.dumps(l,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
write(B/'generation-control-v001/window009-open-v001.json',dict(authorization_events=['EV-040','EV-041'],automatic_authorization_already_given=True,ledger=desc(L),external_api_calls=0,host_fee_usd=None))
for clip in (2,3):
 base=B/f'primary{clip}-leather-input-v001';draft=base/f'primary{clip}-leather-native-input-draft-v001.json';d=load(draft)
 for row in d['rows']:
  assert row['standard_prepare_exit_code']==0 and row['frame_count']==6 and len(row['reference_images_in_order'])==2
  assert row['future_component_A']==row['future_body_target_B']==row['future_integer_delta']==[None]*6
  for ref in row['reference_images_in_order']:assert desc(Path(ref['file']['path']))==ref['file']
  assert desc(Path(row['prompt']['path']))==row['prompt']
  for pin in row['actual_runtime_body_pins']:assert desc(Path(pin['path']))==pin
  row.update(generation_ready=True,target_mounts_are_measured=False,root_edit_target_and_anchor_view_required_before_generation=False)
 d.update(generation_ready=True,root_review_required_before_generation=False,root_review=dict(frozen_draft=desc(draft),actual_reference_images_viewed=True,review='Root viewed six motion references plus three sole Ready identities after E303 two-hash retention. Brown waist-length jerkin and separate short near cap/tiny far tab; all six preserve camera/physical pouch side. Generation only; new A/B/fit/motion not accepted.',retention_batch='2026-10-17-OurgameUE-leather-p2p3-input-v303'))
 write(base/f'primary{clip}-leather-native-input-approved-v001.json',d)
old=R/'tools/scripts/native-fairytale-leather-primary1-v003.py';new=R/'tools/scripts/native-fairytale-leather-p2p3-v001.py';assert not new.exists()
s=old.read_text(encoding='utf-8')
s=s.replace("assert row.get('generation_ready',True) is True","assert document.get('generation_ready') is True and document.get('root_review_required_before_generation') is False\n    assert row.get('generation_ready') is True and row['clip'] in ('sword_primary_2','sword_primary_3')")
s=s.replace('prior accepted same-component Primary1 row is motion/geometry basis only. Six grounded Primary1 component poses','prior actual same-component Primary2/3 row is motion/geometry basis only. Six grounded same-clip component poses')
new.write_text(s,encoding='utf-8')
print(json.dumps(dict(window=9,next_request=193,approved_clips=[2,3],raw_verified=24,helper=desc(new)),ensure_ascii=False))
