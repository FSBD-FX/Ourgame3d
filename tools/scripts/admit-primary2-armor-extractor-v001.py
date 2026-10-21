from pathlib import Path
import hashlib,json,shutil
R=Path('F:/Ourgame');E=R/'docs/production/first-batch-v2/evidence/armor-primary2-native-tooling-v001'
p=E/'extract-armor-primary2-standard-v001.py';q=R/'tools/scripts'/p.name
def d(x):
 b=x.read_bytes();return dict(path=x.as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
assert d(p)['sha256']=='eedaf18980ce73fbb4d70cb7d8e948edf18e4d89159a84f82557ba337e8df052'
assert not q.exists();shutil.copy2(p,q);assert q.read_bytes()==p.read_bytes()
review=E/'root-extractor-admission-v001.json';assert not review.exists()
review.write_text(json.dumps(dict(candidate=d(p),admitted=d(q),root_full_read=True,actual_three_readonly_plans_exit0=True,
 scope='standard four-stage three armor row extraction with dedicated SG interpreter; no arbitrary pixel editing, generation, UE or ledger writes',
 geometry_or_feature_accepted=False,formal_complete_units=0),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(admitted=d(q),review=d(review)),ensure_ascii=False))
