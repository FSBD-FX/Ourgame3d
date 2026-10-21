from pathlib import Path
import hashlib,json
R=Path('F:/Ourgame');B=R/'source-assets/production/fairytale-lgt-readability-v003'
def desc(p):
 b=p.read_bytes();return dict(path=p.as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,v):
 assert not p.exists();p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
d=B/'row-preparation-v001/lgt-ready-native-input-draft-v001.json'
assert desc(d)['sha256']=='6d437440d6e3d5fcee19f296283d13565f4fd63b4df621e1efc340d06d4f857a'
v=load(d)
assert len(v['rows'])==3
for row in v['rows']:
 assert row['standard_prepare_exit_code']==0 and row['generation_ready'] is False
 for ref in row['reference_images_in_order']:assert desc(Path(ref['file']['path']))==ref['file']
 assert desc(Path(row['prompt']['path']))==row['prompt']
 assert row['future_component_A']==[None]*4
 row['generation_ready']=True
review=B/'row-preparation-v001/root-ready-input-review-v001.json'
write(review,dict(draft=desc(d),actual_viewed=['native179','chest-ready-body-design-v001.png','nearshoulder-ready-body-design-v001.png','farshoulder-ready-body-design-v001.png'],reference_retention=['E250','E251'],approved_scope='Three isolated soft-leather Ready4 component raw rows only; native179 garment construction; native158 actual pose; canonical131 accepted idle ink identity. Common body remains unchanged. Exact feature A/mounts/occlusion and small-scale runtime review remain pending.',rejected_scope=['replace common body with assembled179','old grey metal as light-armor material authority','full walk/equip/combo/all20 acceptance'],future_A_unknown=True,formal_complete_units=0))
v['root_input_review']=desc(review)
v['status']='Root reviewed three guides after E251; generation inputs approved only'
write(B/'row-preparation-v001/lgt-ready-native-input-approved-v002.json',v)
old=R/'tools/scripts/native-fairytale-armor-ready-v002.py'
new=R/'tools/scripts/native-fairytale-leather-ready-v001.py'
assert not new.exists()
t=old.read_text(encoding='utf-8-sig')
t=t.replace("base=root/'source-assets/production/fairytale-armor-sword-ready-v002'","base=root/'source-assets/production/fairytale-lgt-readability-v003'")
t=t.replace('independent macro armor component Ready4 only','native179 soft leather independent component Ready4 only')
new.write_text(t,encoding='utf-8')
print(json.dumps(dict(approved_rows=3,handoff=(B/'row-preparation-v001/lgt-ready-native-input-approved-v002.json').as_posix(),helper=new.as_posix(),formal_complete_units=0)))
