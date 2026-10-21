from pathlib import Path
import hashlib,json
R=Path('F:/Ourgame')
B=R/'source-assets/production/fairytale-sword-primary2-v001'
def desc(p):
    b=p.read_bytes();return {'path':p.as_posix(),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
handoff=B/'handoffs/primary2-native-input-v003.json'
h=json.loads(handoff.read_text(encoding='utf-8-sig'))
for ref in h['rows'][0]['reference_images_in_order']:
    assert desc(Path(ref['file']['path']))==ref['file']
ret=R.parent/'unused'
e=Path('E:/OurGame/Knight/过程图稿与视频/2026-10-16-OurgameUE-primary2-short-elbow-input-v202/source-size-SHA256.json')
proof=json.loads(e.read_text(encoding='utf-8-sig'));assert proof['source_and_target_hash_mismatches']==0 and proof['verification_passes']==2
review=B/'root-input-review-v004.json';assert not review.exists()
review.write_text(json.dumps({'source_handoff':desc(handoff),'retention':desc(e),'all_five_references_explicitly_viewed':True,
    'fact':'Canonical131 and low guard/source159 boundaries retain identity. Design guide shows low elbow and rising wrist instead of horizontal punch.',
    'inference':'Concise new rising-cut request is suitable for one bounded native generation. Actual body pose, hand, feet, blade clearance and armor are unknown.',
    'risk':'Diagram points are proposed and cannot certify native output. No finalmotion or fullunit acceptance.',
    'native_generation_ready':True,'source_event':'EV-048','authorization':['EV-040','EV-041']},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
h.update({'generation_ready':True,'root_review_required_before_generation':False,'root_input_review':desc(review)})
approved=B/'handoffs/primary2-native-input-root-reviewed-v004.json';assert not approved.exists()
approved.write_text(json.dumps(h,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
# Keep the old request writer immutable; this new version obtains scope from the actual reviewed row.
p=R/'tools/scripts/native-fairytale-sword-primary2-v001.py';q=R/'tools/scripts/native-fairytale-sword-primary2-v002.py'
assert not q.exists()
text=p.read_text(encoding='utf-8')
old="'scope':'Canonical131 Primary2 body-only six; actual Stage1 timing75/75/60/60/135/135; shortarm forward horizontalcut. Targets are design only; allstates/armor/equipment/runtime remain unfinished',"
assert text.count(old)==1
q.write_text(text.replace(old,"'scope':row['generation_scope'],"),encoding='utf-8')
print(json.dumps({'approved_handoff':desc(approved),'review':desc(review),'writer':desc(q)},ensure_ascii=False))
