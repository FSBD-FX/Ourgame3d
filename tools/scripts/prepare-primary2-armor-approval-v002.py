from pathlib import Path
import datetime,hashlib,json
R=Path('F:/Ourgame')
def desc(p):
    b=p.read_bytes();return dict(path=p.as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def write(p,v):
    assert not p.exists(),p;p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
B=R/'source-assets/production/fairytale-armor-sword-primary2-v001';D=B/'generation-prompts-v002'
draft=json.loads((D/'draft-handoff-v002.json').read_text());original=B/'primary2-macro-native-handoff-draft-v001.json'
assert desc(original)==draft['original_handoff'];handoff=json.loads(original.read_text(encoding='utf-8-sig'))
for row in handoff['rows']:
    revised=next(x for x in draft['rows'] if x['component']==row['component'])
    assert [x['file'] for x in row['reference_images_in_order']]==[x['file'] for x in revised['reference_images_in_order']]
    row['original_prepared_prompt']=row['prompt'];row['prompt']=revised['prompt']
    row['reference_images_in_order']=revised['reference_images_in_order']
    assert desc(Path(row['prompt']['path']))==row['prompt']
    for ref in row['reference_images_in_order']:assert desc(Path(ref['file']['path']))==ref['file']
    row['generation_ready']=True
review=B/'root-three-armor-input-review-v002.json'
write(review,dict(created_local=datetime.datetime.now().astimezone().isoformat(),
    canonical_prompts=[desc(D/n) for n in ['chest-canonical-v002.txt','nearshoulder-canonical-v002.txt','farshoulder-canonical-v002.txt']],
    draft=desc(D/'draft-handoff-v002.json'),original=desc(original),
    explicit_reference_review='Root viewed all11 references after F/E214 retention; read all3 canonical prompts fully',
    approval_scope='one native six-view row each Chest/NearShoulder/FarShoulder; existing native171 body only',
    input_precondition_correction='v001 compared revised role descriptions too; v002 requires identical ordered file/path/size/SHA and adopts reviewed concise roles',
    far_family='approved topstrap rivet; old163 centralboss failure retained',
    future_feature_A_measured=False,geometry_design_only=True,formal_complete_units=0,
    host_fee_usd=None,external_api_calls=0,authorization_events=['EV-040','EV-041']))
handoff['generation_ready']=True;handoff['root_review_required_before_generation']=False
handoff['root_input_review']=desc(review);handoff['concise_prompt_draft']=desc(D/'draft-handoff-v002.json')
approved=B/'primary2-macro-native-handoff-approved-v002.json';write(approved,handoff)
print(json.dumps(dict(approved_handoff=desc(approved),root_review=desc(review)),ensure_ascii=False))
