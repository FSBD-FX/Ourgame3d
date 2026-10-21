"""Preserve frozen source manifests under flat filenames before E retention."""
from pathlib import Path
import argparse,hashlib,json,shutil
p=argparse.ArgumentParser();p.add_argument('--source-name',required=True);p.add_argument('--manifest',action='append',required=True);p.add_argument('--present',action='append',default=[]);p.add_argument('--status',required=True);a=p.parse_args()
root=Path('F:/Ourgame').resolve();parent=root/'过程图稿与视频';out=(parent/a.source_name).resolve()
assert out.parent==parent and not out.exists()
def desc(path):
 b=path.read_bytes();return {'path':path.as_posix(),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
files=[]
for name in a.manifest:
 m=Path(name).resolve();assert m.is_relative_to(root);d=json.loads(m.read_text(encoding='utf-8-sig'))
 for r in d.get('files_excluding_this_manifest',d.get('files',[])):
  q=Path(r['path']);q=q.resolve() if q.is_absolute() else (root/q).resolve();assert q.is_relative_to(root)
  actual=desc(q);assert actual['bytes']==r['bytes'] and actual['sha256']==r['sha256'],q
  files.append(q)
 files.append(m)
files=list(dict.fromkeys(files));(out/'原件').mkdir(parents=True);(out/'展示副本').mkdir();rows=[]
for i,q in enumerate(files):
 t=out/'原件'/f'{i:03d}-{q.name}';shutil.copy2(q,t);assert q.read_bytes()==t.read_bytes();rows.append(dict(desc(q),retained_relative=t.relative_to(out).as_posix()))
for i,name in enumerate(a.present):
 q=Path(name).resolve();assert q in files
 t=out/'展示副本'/f'{i:02d}-{q.name}';shutil.copy2(q,t);assert q.read_bytes()==t.read_bytes()
(out/'source-version-status-index.json').write_text(json.dumps({'files':rows,'status':a.status,'flat_mapping_avoids_deep_copy_path_limit':True,'formal_complete_units':0},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(out/'README.md').write_text(a.status+'\nExact flat source mapping; old versions retained. Local preservation does not imply acceptance/publication.\n',encoding='utf-8')
print(json.dumps({'archive':out.as_posix(),'original_files':len(files),'original_bytes':sum(x['bytes'] for x in rows)},ensure_ascii=False))
