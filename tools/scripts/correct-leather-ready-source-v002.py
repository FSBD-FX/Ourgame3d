from pathlib import Path
import hashlib,json,difflib
R=Path('F:/Ourgame');F=R/'source-assets/production/fairytale-lgt-readability-v003';A=F/'ready-native-source-v001';O=F/'ready-native-source-v002';S=R/'UnrealGame/Source/CodexDungeon';assert not O.exists();O.mkdir()
def desc(p):
 b=p.read_bytes();return dict(path=p.as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
v=json.loads((A/'source-freeze-v001.json').read_text(encoding='utf-8'))
for row in v['inputs']+v['files']:assert desc(Path(row['path']))==row
files=[];patch=[]
for name in ['DungeonFairytaleSwordPresentation.cpp','DungeonFairytaleEquipmentBoundProbe.h','DungeonFairytaleEquipmentBoundProbe.cpp']:
 old=(S/name).read_text(encoding='utf-8');new=(A/name).read_text(encoding='utf-8')
 if name=='DungeonFairytaleSwordPresentation.cpp':
  a='''    const FString Name=FString::Printf(LeatherReady?TEXT("T_Fairytale_LeatherReady%s_%03d_v001")
        :TEXT("T_Fairytale_SwordReady%s_%03d_v001"),*Component,Frame);'''
  b='''    const FString Name=LeatherReady
        ?FString::Printf(TEXT("T_Fairytale_LeatherReady%s_%03d_v001"),*Component,Frame)
        :FString::Printf(TEXT("T_Fairytale_SwordReady%s_%03d_v001"),*Component,Frame);'''
  assert new.count(a)==1;new=new.replace(a,b)
 q=O/name;q.write_text(new,encoding='utf-8',newline='\n');files.append(desc(q));rel='UnrealGame/Source/CodexDungeon/'+name
 patch.extend(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile='a/'+rel,tofile='b/'+rel))
p=O/'ready-trial-v002.patch';p.write_text(''.join(patch),encoding='utf-8',newline='\n');files.append(desc(p))
v.update(schema='leather-ready-opt-in-source-candidate-v002',supersedes=desc(A/'source-freeze-v001.json'),fix='Printf branches each use their own TEXT literal array, required by local UE5.5 UnrealString.h.inl1573-1577; original v001 preserved',files=files)
(O/'source-freeze-v002.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(candidate=O.as_posix(),actual_source_written=False)))
