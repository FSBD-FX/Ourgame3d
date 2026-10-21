from pathlib import Path
import argparse,hashlib,json,shutil
R=Path('F:/Ourgame');p=argparse.ArgumentParser()
p.add_argument('--freeze',required=True);p.add_argument('--sha256',required=True);p.add_argument('--topic',required=True);a=p.parse_args()
assert Path(a.topic).name==a.topic and a.topic.startswith('2026-')
A=R/'过程图稿与视频'/a.topic;assert not A.exists(),A
(A/'原件').mkdir(parents=True);(A/'展示副本').mkdir()
def desc(p):
 b=p.read_bytes();return {'path':p.as_posix(),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
f=Path(a.freeze).resolve();assert f.is_relative_to(R) and desc(f)['sha256']==a.sha256
data=json.loads(f.read_text(encoding='utf-8-sig'));rows=data['files']+[desc(f)];entries=[]
for i,row in enumerate(rows):
 s=Path(row['path']);d=desc(s);assert d['bytes']==row['bytes'] and d['sha256']==row['sha256'],s
 t=A/'原件'/f'{i:03d}-{s.name}';assert not t.exists();shutil.copy2(s,t)
 assert desc(t)['sha256']==d['sha256']
 entries.append({'source':d,'retained':desc(t)})
 if s.parent.name=='assemblies' and s.name.startswith('frame-') and s.suffix=='.png':
  target=A/'展示副本'/s.name;assert not target.exists();shutil.copy2(s,target);assert desc(target)['sha256']==d['sha256']
(A/'index.json').write_text(json.dumps({'freeze':desc(f),'files':entries,'status':'Frozen candidate, before explicit review. No acceptance or publication','formal_complete_units':0},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(A/'README.md').write_text('显式冻包展示前保全。保留原件与候选展示副本；本地保留不表示导入、运行、动作或正式单元完成。源图不覆盖，实际审阅后另留报告。\n',encoding='utf-8')
print(json.dumps({'archive':A.as_posix(),'frozen_files':len(entries),'bytes':sum(e['retained']['bytes'] for e in entries),'sha_mismatches':0},ensure_ascii=False))
