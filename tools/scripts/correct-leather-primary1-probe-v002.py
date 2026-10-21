from pathlib import Path
import json,hashlib,difflib
R=Path('F:/Ourgame');F=R/'source-assets/production/fairytale-lgt-readability-v003';B=F/'primary1-native-source-v001';O=F/'primary1-native-source-v002';assert not O.exists();O.mkdir()
def desc(p):
 b=p.read_bytes();return dict(path=p.as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
v=json.loads((B/'source-freeze-v001.json').read_text(encoding='utf-8'))
for d in v['inputs']+v['files']:assert desc(Path(d['path']))==d
files=[];patch=[]
for n in ['DungeonFairytaleSwordPresentation.cpp','DungeonFairytaleEquipmentBoundProbe.h','DungeonFairytaleEquipmentBoundProbe.cpp']:
 p=B/n;s=p.read_text(encoding='utf-8');old=(R/'UnrealGame/Source/CodexDungeon'/n).read_text(encoding='utf-8')
 if n.endswith('Probe.cpp'):
  a='                else Pulse(EKeys::J);';b='                else if(Pulse(EKeys::J))ReadySeen[6]=0; // Require fresh actual Ready observations after second attack.';assert s.count(a)==1;s=s.replace(a,b)
 q=O/n;q.write_text(s,encoding='utf-8',newline='\n');files.append(desc(q));rel='UnrealGame/Source/CodexDungeon/'+n
 patch.extend(difflib.unified_diff(old.splitlines(True),s.splitlines(True),fromfile='a/'+rel,tofile='b/'+rel))
p=O/'primary1-trial-v002.patch';p.write_text(''.join(patch),encoding='utf-8',newline='\n');files.append(desc(p))
v.update(schema='leather-primary1-source-candidate-v002',supersedes=desc(B/'source-freeze-v001.json'),fix='Reset accumulated ReadySeen[6] only upon real second J request, so finish requires fresh post-second native Ready observations; no counter or action fake',files=files)
(O/'source-freeze-v002.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(v002=O.as_posix(),actual_Source_unchanged=True)))
