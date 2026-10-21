from pathlib import Path
import hashlib,json
root=Path('F:/Ourgame');base=root/'source-assets/production/fairytale-sword-primary3-v001'
def desc(p):
    b=p.read_bytes();return {'path':p.as_posix(),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
draft=base/'handoffs/primary3-native-input-draft-v001.json'
d=json.loads(draft.read_text(encoding='utf-8'));r=d['rows'][0]
assert not d['generation_ready'] and d['root_review_required_before_generation']
for item in [r['prompt'],r['request'],r['numeric_contract']]+[x['file'] for x in r['reference_images_in_order']]:
    assert desc(Path(item['path']))==item
contract=json.loads(Path(r['numeric_contract']['path']).read_text(encoding='utf-8'))
assert contract['durations_ms']==[110,110,60,60,160,160] and contract['total_kernel_ms']==660
assert all(p['actual_or_design_palm_point'] is None and p['actual_or_design_blade_axis'] is None for p in contract['phases'])
review=base/'handoffs/root-input-review-v001.json';approved=base/'handoffs/primary3-native-input-approved-v001.json'
assert not review.exists() and not approved.exists()
review.write_text(json.dumps({'source_draft':desc(draft),'all_three_retained_refs_explicitly_viewed':True,'retention_batch':'2026-10-16-OurgameUE-primary3-input-v225','canonical_identity_only':True,'prompt_read_and_approved_for_one_body_row':True,'scope':'Short bent-elbow downward finisher, six body-only poses. Shared row extraction, measured grip, independent armor and native runtime review remain required. No weapon/armor baked into body.','numeric_contract':desc(Path(r['numeric_contract']['path'])),'no_measured_grip_or_bones_claimed':True,'formal_complete_units':0},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
d['generation_ready']=True;d['root_review_required_before_generation']=False;d['root_input_review']=desc(review)
approved.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'approved':desc(approved),'review':desc(review)},ensure_ascii=False))
