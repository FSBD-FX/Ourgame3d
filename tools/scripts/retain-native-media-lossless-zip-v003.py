"""Exact-byte original+presentation retention with two source/member SHA passes."""
from pathlib import Path
import argparse,hashlib,json,zipfile
S=Path('F:/Ourgame/过程图稿与视频').resolve();E=Path('G:/OurGameArchive').resolve()
p=argparse.ArgumentParser();p.add_argument('--source',required=True);p.add_argument('--batch',required=True);a=p.parse_args()
source=Path(a.source).resolve();assert source.parent==S and source.is_dir() and not source.is_symlink()
assert a.batch.startswith('2026-') and Path(a.batch).name==a.batch and '/' not in a.batch and '\\' not in a.batch
dest=E/a.batch;assert not dest.exists()
def digest(path):
 h=hashlib.sha256()
 with path.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
root_readme=digest(E/'README.md');files=sorted(p for p in source.rglob('*') if p.is_file());assert files
rows=[]
for f in files:
 assert not f.is_symlink();rows.append(dict(source=f.as_posix(),member=f.relative_to(source).as_posix(),bytes=f.stat().st_size,sha256=digest(f)))
dest.mkdir();packet=dest/'原件与展示副本-逐字节无损.zip'
with zipfile.ZipFile(packet,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=6,allowZip64=True) as z:
 for row in rows:z.write(row['source'],row['member'])
for repeat in range(2):
 with zipfile.ZipFile(packet,'r') as z:
  assert set(z.namelist())=={r['member'] for r in rows} and len(z.namelist())==len(rows)
  for row in rows:
   f=Path(row['source']);assert f.stat().st_size==row['bytes'] and digest(f)==row['sha256']
   data=z.read(row['member']);assert len(data)==row['bytes'] and hashlib.sha256(data).hexdigest()==row['sha256']
assert digest(E/'README.md')==root_readme
receipt=dict(schema='native-media-exact-original-zip-retention-v003',source_archive=source.as_posix(),status='EXACT_ORIGINALS_AND_PRESENTATION_RETAINED_BEFORE_REVIEW',packet=dict(path=packet.as_posix(),bytes=packet.stat().st_size,sha256=digest(packet)),files=rows,source_bytes=sum(r['bytes'] for r in rows),file_count=len(rows),verification_passes=2,source_and_member_hash_mismatches=0,archive_root_README_unchanged=True,source_deleted=False,reencoded_originals=False,publication=False,formal_complete_units=0)
(dest/'E-retention-index-v001.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(dest/'README.md').write_text('原始文件留在F原位，原件/展示副本全部按原字节无损ZIP保全；每个ZIP成员与F源文件大小/SHA256独立复核两次。未重编码原图/原片，未覆盖旧批次；保全不代表视觉或完整内容验收。\n',encoding='utf-8')
print(json.dumps(dict(G_archive=dest.as_posix(),source_bytes=receipt['source_bytes'],packet_bytes=receipt['packet']['bytes'],files=len(rows),verification_passes=2,hash_mismatches=0)))
