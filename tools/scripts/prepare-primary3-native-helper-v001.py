from pathlib import Path
import hashlib,json
R=Path('F:/Ourgame');p=R/'tools/scripts/native-fairytale-sword-primary2-v002.py';q=R/'tools/scripts/native-fairytale-sword-primary3-v001.py'
assert not q.exists();s=p.read_text(encoding='utf-8')
assert s.count("fairytale-sword-primary2-v001")==1
s=s.replace('fairytale-sword-primary2-v001','fairytale-sword-primary3-v001')
compile(s,str(q),'exec');q.write_text(s,encoding='utf-8')
def d(x):
 b=x.read_bytes();return dict(path=x.as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
E=R/'docs/production/first-batch-v2/evidence/sword-primary3-native-tooling-v001';E.mkdir(parents=True,exist_ok=True)
f=E/'helper-version-v001.json';assert not f.exists()
f.write_text(json.dumps(dict(original=d(p),new=d(q),scope='Same single-writer one-native-request-at-a-time body accounting; onlyfamily literal changed, no ledger mutation or generation',generation_called=False,formal_complete_units=0),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(helper=d(q),proof=d(f)),ensure_ascii=False))
