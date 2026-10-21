from pathlib import Path
import hashlib,json,shutil
R=Path('F:/Ourgame');E=R/'docs/production/first-batch-v2/evidence/armor-primary2-native-tooling-v001'
p=E/'native-fairytale-armor-primary2-batch-v002.py';q=R/'tools/scripts'/p.name
def d(x):
    b=x.read_bytes();return dict(path=x.as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
assert d(p)['sha256']=='d7c7206fc40fdee67c4f29e1df57f63a3e3906f0c70d0df8b848fbb13ac3ae47'
assert not q.exists();shutil.copy2(p,q);assert q.read_bytes()==p.read_bytes()
review=E/'root-admission-v002.json';assert not review.exists()
review.write_text(json.dumps(dict(candidate=d(p),admitted=d(q),Root_full_read=True,actual_readonly_plan172_passed=True,
 scope='Root only sequential172..174 reservations, arbitrary-order result retention; no generator calls in helper',
 original_v001_schema_failure_preserved=True,canonical_approved_handoff_unchanged=True,source_or_UE_modified=False,
 native_called=False,formal_complete_units=0),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(admitted=d(q),review=d(review)),ensure_ascii=False))
