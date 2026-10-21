from pathlib import Path
import hashlib,json
R=Path('F:/Ourgame');B=R/'source-assets/production/fairytale-hero-state-gap-v001/death-state-preparation-v001'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def pin(p):return dict(path=p.as_posix(),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())
freeze=B/'armor-input-Far-tiny-floor-amendment-v002/Far-tiny-floor-amendment-freeze-v002.json'
assert pin(freeze)['sha256']=='62578161f10a035da7bc53fefdd0ec1cba90cbbacd0f863bb55ec28371f884f4'
for row in read(freeze)['files']:
 p=Path(row['path']);p=p if p.is_absolute() else freeze.parent/p;assert pin(p)['bytes']==row['bytes'] and pin(p)['sha256']==row['sha256']
q=read(B/'Root-native-armor-Death5-v001/input/ShoulderFar-Root-native-references-AFTER-E471-v001.json')
q.update(Root_pre_generation_component_floor_amendment=pin(freeze),minimum_used_pixels_extract=256,minimum_used_pixels_compose=256,canonical_component_alpha_pixels=367,no_scale_inflation_to_pass=True)
out=B/'Root-native-armor-Death5-v001/input/ShoulderFar-Root-native-references-AFTER-E471-v002.json';assert not out.exists();out.write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(out.as_posix())
