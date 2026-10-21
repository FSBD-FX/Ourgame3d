from pathlib import Path
import json,hashlib
R=Path('F:/Ourgame');B=R/'source-assets/production/fairytale-lgt-readability-v003/row-correction-v002'
def desc(p):
 b=p.read_bytes();return dict(path=p.as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,v):
 assert not p.exists();p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
p=B/'lgt-ready-correction-input-draft-v002.json';f=B/'preparation-freeze-v002.json'
assert desc(p)['sha256']=='cbe04bb8249fa4eaa18745169250a89b232a24fbfc0195a1fb3e7f1c537427a5'
assert desc(f)['sha256']=='e08b2c5368f429ec39c4c393837761431d3528975febb3dd908ce2c4366ad1b1'
v=read(p);row=next(r for r in v['rows'] if r['component']=='NearShoulder')
assert row['generation_ready'] is False and row['standard_prepare_exit_code']==0 and row['reference_count']==1
assert row['frame_count']==4 and row['durations_ms']==[167]*4 and row['future_component_A']==[None]*4
assert desc(Path(row['prompt']['path']))==row['prompt']
for ref in row['reference_images_in_order']:assert desc(Path(ref['file']['path']))==ref['file']
row['generation_ready']=True;row['native_request_number']=183;v['rows']=[row]
review=B/'root-near-edit-input-review183-v001.json'
write(review,dict(source_draft=desc(p),source_freeze=desc(f),failed_native181_actual_viewed_after_retention='E256',failed_semantic='Complete vest instead of isolated near cap; not admitted or extracted',approved_scope='One native edit retaining only four image-LEFT near caps from failed181; replace everything else pure green. No local artwork cutout. Single target only. NewA unknown.',remaining_two_rows_not_requested=True,formal_complete_units=0))
v['root_input_review']=desc(review);write(B/'lgt-near-edit-input-approved183-v003.json',v)
print(json.dumps(dict(handoff=(B/'lgt-near-edit-input-approved183-v003.json').as_posix(),rows=1,request183_not_yet_reserved=True)))
