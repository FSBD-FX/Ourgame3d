from pathlib import Path
import argparse,hashlib,json,shutil
R=Path('F:/Ourgame');p=argparse.ArgumentParser();p.add_argument('--source',required=True);p.add_argument('--freeze',required=True);p.add_argument('--freeze-sha',required=True);p.add_argument('--handoff',required=True);p.add_argument('--topic',required=True);a=p.parse_args();B=(R/a.source).resolve();A=(R/'过程图稿与视频'/a.topic).resolve();assert B.is_relative_to(R/'source-assets') and A.parent==R/'过程图稿与视频' and not A.exists()
def desc(p):
 b=p.read_bytes();return dict(path=p.as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
f=B/a.freeze;assert desc(f)['sha256']==a.freeze_sha
for row in json.loads(f.read_text(encoding='utf-8-sig'))['files']:
 q=Path(row['path']);q=q if q.is_absolute() else B/q;d=desc(q);assert (d['bytes'],d['sha256'])==(row['bytes'],row['sha256'])
(A/'原件').mkdir(parents=True);(A/'展示副本').mkdir();rows=[]
for q in sorted(B.rglob('*')):
 if q.is_file():
  o=A/'原件'/q.relative_to(B);o.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(q,o);assert q.read_bytes()==o.read_bytes();rows.append(dict(source=desc(q),retained=o.relative_to(A).as_posix()))
for row in json.loads((B/a.handoff).read_text(encoding='utf-8-sig'))['rows']:
 for i,ref in enumerate(row['reference_images_in_order']):
  q=Path(ref['file']['path']);assert q.is_relative_to(R) and desc(q)==ref['file'];o=A/'展示副本'/f'{row["component"]}-{i}-{q.name}';shutil.copy2(q,o);assert q.read_bytes()==o.read_bytes()
(A/'source-version-status-index.json').write_text(json.dumps(dict(files=rows,status='input candidate; Root approval/generation/extraction/fit pending; newA/Bnull; originals and exact presentation references preserved',formal_complete_units=0),ensure_ascii=False,indent=2)+'\n',encoding='utf-8');(A/'README.md').write_text('完整保留所指冻结输入原件及逐字节参考展示副本，不覆盖前版。新生成/贴合/运行尚未验收，Root E归档后再看新媒体。\n',encoding='utf-8');print(A.as_posix())
