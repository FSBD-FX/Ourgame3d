from pathlib import Path
import json,hashlib
R=Path('F:/Ourgame');B=R/'source-assets/production/fairytale-lgt-readability-v003/row-correction-v003'
def desc(p):
 b=p.read_bytes();return dict(path=p.as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
p=B/'lgt-near-lining-edit-input-draft-v003.json';assert desc(p)['sha256']=='9bbef28449eadee26177e07b49007971efbb2d19e9e5e799859d3749c0818461'
v=json.loads(p.read_text(encoding='utf-8-sig'));row=v['rows'][0]
assert row['component']=='NearShoulder' and row['standard_prepare_exit_code']==0 and len(row['reference_images_in_order'])==1
assert row['durations_ms']==[167]*4 and row['future_component_A']==[None]*4 and row['generation_ready'] is False
assert desc(Path(row['prompt']['path']))==row['prompt']
for ref in row['reference_images_in_order']:assert desc(Path(ref['file']['path']))==ref['file']
review=B/'root-near-lining-review186-v001.json';assert not review.exists()
review.write_text(json.dumps(dict(source_draft=desc(p),actual_prior_views=['183 raw/E261','183 shared frame0/E265'],scope='Single target183 native edit removes low oval lining/ring; preserves four brown cap bodies, perspective and dimensions. Generation only, A/fit/runtime unknown.',formal_complete_units=0),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
row.update(generation_ready=True,target_mounts_are_measured=False,native_request_number=186);v['generation_ready']=True;v['root_input_review']=desc(review)
q=B/'lgt-near-lining-approved186-v004.json';assert not q.exists();q.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(handoff=q.as_posix(),request186_not_reserved=True)))
