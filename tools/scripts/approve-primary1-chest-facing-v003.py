from pathlib import Path
import json,hashlib
R=Path('F:/Ourgame');B=R/'source-assets/production/fairytale-lgt-readability-v003';D=B/'primary1-chest-view4-input-v003'
def pin(p):
 b=p.read_bytes();return dict(path=p.as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
f=D/'input-freeze-v003.json';assert pin(f)['sha256']=='c3f63ff1c3a14548b9a5c7264c91dd34c3af10ad68f209202c5e2b9f93482bd2'
for r in json.loads(f.read_text(encoding='utf-8-sig'))['files']:
 p=D/r['path'];d=pin(p);assert (d['bytes'],d['sha256'])==(r['bytes'],r['sha256'])
h=D/'chest-view4-native-input-draft-v003.json';v=json.loads(h.read_text(encoding='utf-8-sig'));v['generation_ready']=True;v['root_review_required_before_generation']=False
v['root_review']='191 remains wrong perspective and rejected after E292; this request allows all six redraw and requires fresh measurement. Actual188 and Ready184 references already viewed.'
v['root_input_freeze']=pin(f)
for r in v['rows']:r['generation_ready']=True;r['root_edit_target_and_anchor_view_required_before_generation']=False
o=B/'primary1-chest-facing-approved-v004.json';assert not o.exists();o.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(handoff=o.as_posix(),prompt=Path(v['rows'][0]['prompt']['path']).read_text(encoding='utf-8'),refs=[x['file']['path'] for x in v['rows'][0]['reference_images_in_order']]),ensure_ascii=False))
