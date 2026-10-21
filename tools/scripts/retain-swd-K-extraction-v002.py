from pathlib import Path
import argparse,hashlib,json,shutil
R=Path('F:/Ourgame');ap=argparse.ArgumentParser();ap.add_argument('--freeze',required=True);ap.add_argument('--sha256',required=True);ap.add_argument('--topic',required=True);a=ap.parse_args()
def d(p):
 b=p.read_bytes();return dict(path=p.as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
freeze=Path(a.freeze).resolve();assert freeze.is_relative_to(R) and d(freeze)['sha256']==a.sha256
data=json.loads(freeze.read_text(encoding='utf-8-sig'));A=R/'过程图稿与视频'/a.topic;assert A.parent==R/'过程图稿与视频' and not A.exists();(A/'原件').mkdir(parents=True);(A/'展示副本').mkdir();rows=[]
for row in data['members']+[d(freeze)]:
 p=Path(row['path']);assert d(p)==row,p
 rel=p.relative_to(freeze.parent);t=A/'原件'/rel;t.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,t);assert d(t)['sha256']==row['sha256'];rows.append(dict(source=row,retained=d(t)))
 if p.parent.name=='aligned512':
  v=A/'展示副本'/p.name;shutil.copy2(p,v);assert d(v)['sha256']==row['sha256']
(A/'source-version-status-index.json').write_text(json.dumps(dict(schema='K-technical-extraction-before-review-v002',files=rows,freeze=d(freeze),status='Technical extraction; Root processed-image review pending; no runtime admission',formal_complete_units=0),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(A/'README.md').write_text('完整冻结提取包及4张原字节512展示副本保留。统一缩放和整数Y偏移以原QC为准，禁止逐帧缩放隐藏漂移。先E逐字节保全后Root审阅；本地保留不是正式美术、运行或完整内容验收。\n',encoding='utf-8')
print(json.dumps(dict(archive=A.as_posix(),members=len(data['members']),source_hash_mismatches=0),ensure_ascii=False))
