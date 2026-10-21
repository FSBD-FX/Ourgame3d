from pathlib import Path
import hashlib,json
B=Path('F:/Ourgame/source-assets/production/fairytale-sword-primary3-v001/armor-input-v001')
def desc(p):
    b=p.read_bytes();return {'path':p.as_posix(),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
draft=B/'primary3-three-armor-input-draft-v001.json';d=json.loads(draft.read_text(encoding='utf-8'))
assert desc(draft)['sha256']=='d3e8f6ca53a2ae7f1500f0b8ee0d95efe7cc3b4a108a381e618ac00af5072234'
assert len(d['rows'])==3 and not d['generation_ready']
for r in d['rows']:
    assert r['target_mounts_are_measured'] is False and r['future_feature_A']==r['future_cloth_targets']==[None]*6
    assert r['durations_ms']==[110,110,60,60,160,160]
    for item in [r['prompt'],r['request']]+[x['file'] for x in r['reference_images_in_order']]:assert desc(Path(item['path']))==item
review=B/'root-input-review-v001.json';approved=B/'primary3-three-armor-input-approved-v001.json'
assert not review.exists() and not approved.exists()
review.write_text(json.dumps({'draft':desc(draft),'retention':'2026-10-16-OurgameUE-primary3-armor-input-v229','all_eight_distinct_refs_actually_viewed':True,'six_original175_bodies_viewed':True,'prompt_review':'Root authored/read three concise isolated-component prompts. Single Ready item only construction, actual175 only motion, null body targets/physicalA, same416/72 hero size and independent armor preserved.','body_trial_limits':'Phase0 load subtle, phase1 glove close to helmet ink, phase2 hand overlap/horizontal sleeve remain explicit watchpoints. New armor rows and native weapon clearance are trial work, not acceptance.','generation_allowed':'One native row per Chest/NearShoulder/FarShoulder; no external API, no fullunit claim','formal_complete_units':0},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
d['generation_ready']=True;d['root_review_required_before_generation']=False;d['root_input_review']=desc(review)
approved.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'approved':desc(approved)},ensure_ascii=False))
