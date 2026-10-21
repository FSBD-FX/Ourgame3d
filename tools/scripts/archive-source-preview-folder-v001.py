from pathlib import Path
import argparse,hashlib,json,shutil
R=Path('F:/Ourgame').resolve();ap=argparse.ArgumentParser();ap.add_argument('--source',required=True);ap.add_argument('--topic',required=True);ap.add_argument('--presentation-subdir',required=True);ap.add_argument('--status',required=True);a=ap.parse_args()
C=Path(a.source).resolve();A=R/'过程图稿与视频'/a.topic;assert C.is_relative_to(R/'source-assets') and C.is_dir() and not C.is_symlink();assert A.parent==R/'过程图稿与视频' and not A.exists()
def pin(p):
 b=p.read_bytes();return dict(path=p.as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
files=sorted(p for p in C.rglob('*') if p.is_file());assert files and all(not p.is_symlink() for p in files);(A/'原件').mkdir(parents=True);(A/'展示副本').mkdir();rows=[]
for p in files:
 t=A/'原件'/p.relative_to(C);t.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,t);assert pin(t)['sha256']==pin(p)['sha256'];rows.append(dict(source=pin(p),retained=pin(t)))
 if p.parent.name==a.presentation_subdir and p.suffix=='.png':
  v=A/'展示副本'/p.name;assert not v.exists();shutil.copy2(p,v);assert pin(v)['sha256']==pin(p)['sha256']
(A/'source-version-status-index.json').write_text(json.dumps(dict(files=rows,status=a.status,new_image_generation_calls=0,formal_complete_units=0),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(A/'README.md').write_text(a.status+'\n源目录原件与展示副本逐字节保留，先E保全后Root审阅。技术候选，不等于UE截图、运行、正式接受或发布；未重绘源素材。\n',encoding='utf-8')
print(json.dumps(dict(archive=A.as_posix(),files=len(files),mismatches=0),ensure_ascii=False))
