"""Exact-byte native-media solid TAR.XZ candidate. Standard library only.
No media decoding/reencoding, extraction, deletion, UE, network or approval.
Root exclusively owns actual E execution; --sample-frames writes only HERE.
"""
from pathlib import Path, PurePosixPath
import argparse
import hashlib
import json
import lzma
import os
import re
import stat
import sys
import tarfile
import time
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
SOURCE_ROOT=Path('F:/Ourgame/过程图稿与视频').resolve()
E_ROOT=Path('E:/OurGame/Knight/过程图稿与视频').resolve()
CHUNK=1024*1024
PACKET_NAME='原件与展示副本-逐字节无损-solid.tar.xz'
INDEX_NAME='E-retention-index-v001.json'


def need(ok,why):
 if not ok:raise ValueError(why)


def read_json(p):
 def unique(items):
  d={}
  for k,v in items:
   need(k not in d,'Duplicate JSON key');d[k]=v
  return d
 return json.loads(Path(p).read_text(encoding='utf-8-sig'),object_pairs_hook=unique,
                   parse_constant=lambda _:(_ for _ in ()).throw(ValueError('Nonfinite JSON')))


def digest(p):
 h=hashlib.sha256();n=0
 with Path(p).open('rb') as f:
  for chunk in iter(lambda:f.read(CHUNK),b''):h.update(chunk);n+=len(chunk)
 return n,h.hexdigest()


def pin(p):
 p=Path(p);n,h=digest(p);return dict(path=p.resolve().as_posix(),bytes=n,sha256=h)


def no_alias(p):
 p=Path(p);s=p.lstat()
 need(not p.is_symlink() and not (getattr(s,'st_file_attributes',0)&0x400), 'Symlink/reparse source or destination boundary forbidden')
 return s


def member_name(s):
 need(isinstance(s,str) and s and '\\' not in s and ':' not in s and '\x00' not in s
      and not s.startswith('/') and all(x not in ('','.','..') for x in s.split('/'))
      and PurePosixPath(s).as_posix()==s,'Unsafe TAR member path')
 return s


def batch_name(s):
 need(isinstance(s,str) and s.startswith('2026-') and Path(s).name==s
      and not any(x in s for x in '/\\:*?"<>|') and s[-1] not in '. ', 'Unsafe or unversioned batch name')
 return s


def source_members(source,source_root):
 source=Path(source).absolute();source_root=Path(source_root).resolve()
 no_alias(source);need(source.resolve().parent==source_root and source.is_dir(),'Source must be one direct native archive leaf')
 result={}
 for p in sorted(source.rglob('*')):
  s=no_alias(p)
  if stat.S_ISDIR(s.st_mode):continue
  need(stat.S_ISREG(s.st_mode),'Nonregular source member')
  name=member_name(p.relative_to(source).as_posix())
  need(name not in result,'Duplicate source member');result[name]=p
 need(result,'Empty source archive')
 return source.resolve(),result


def snapshot(source,source_root,selected=None):
 source,files=source_members(source,source_root)
 names=sorted(files) if selected is None else sorted(selected)
 need(names and len(names)==len(set(names)) and set(names)<=set(files),'Selected member absent/duplicate')
 rows=[]
 for name in names:
  n,h=digest(files[name]);need(n==files[name].stat().st_size,'Source size changed during snapshot')
  rows.append(dict(source=files[name].resolve().as_posix(),member=name,bytes=n,sha256=h))
 return source,rows,sorted(files)


def check_sources(source,source_root,rows,all_names):
 _,files=source_members(source,source_root)
 need(sorted(files)==all_names,'Source full membership drifted after snapshot')
 for row in rows:
  need(files[row['member']].resolve().as_posix()==row['source'],'Source path binding changed')
  need(digest(files[row['member']])==(row['bytes'],row['sha256']),'Source bytes/SHA drifted')


def write_new(p,obj):
 b=(json.dumps(obj,ensure_ascii=False,indent=2,allow_nan=False)+'\n').encode('utf-8') if not isinstance(obj,bytes) else obj
 with Path(p).open('xb') as f:f.write(b);f.flush();os.fsync(f.fileno())


def pack(packet,rows,preset):
 # One XZ stream for ALL tar files: compression can reuse preceding frames.
 # Tar.addfile copies incrementally from each source handle; no whole-frame read.
 with Path(packet).open('xb') as raw:
  with lzma.LZMAFile(raw,'w',format=lzma.FORMAT_XZ,check=lzma.CHECK_CRC64,preset=preset) as compressed:
   with tarfile.open(fileobj=compressed,mode='w|',format=tarfile.PAX_FORMAT) as archive:
    for row in rows:
     path=Path(row['source']);no_alias(path)
     info=tarfile.TarInfo(member_name(row['member']));info.size=row['bytes'];info.mtime=0;info.mode=0o644
     with path.open('rb') as f:archive.addfile(info,f)
  raw.flush();os.fsync(raw.fileno())


def verify_archive(packet,rows):
 expected={member_name(r['member']):r for r in rows}
 need(len(expected)==len(rows) and rows,'Expected members empty/duplicate')
 seen=set();total=0
 with Path(packet).open('rb') as raw:
  with lzma.LZMAFile(raw,'r',format=lzma.FORMAT_XZ) as compressed:
   # ignore_zeros scans standard final padding through XZ EOF rather than
   # stopping at the first TAR zero record; XZ CRC64/trailer is actually read.
   with tarfile.open(fileobj=compressed,mode='r|',ignore_zeros=True,errorlevel=2) as archive:
    for info in archive:
     name=member_name(info.name)
     need(info.isfile() and not info.linkname and info.sparse is None,'Only regular non-sparse original TAR files allowed')
     need(name in expected and name not in seen,'Extra/duplicate TAR member');seen.add(name);row=expected[name]
     need(info.size==row['bytes'],'TAR member declared size differs')
     f=archive.extractfile(info);need(f is not None,'TAR member stream absent')
     h=hashlib.sha256();n=0
     with f:
      for chunk in iter(lambda:f.read(CHUNK),b''):h.update(chunk);n+=len(chunk)
     need((n,h.hexdigest())==(row['bytes'],row['sha256']),'TAR member stream bytes/SHA differs')
     total+=n
   while compressed.read(CHUNK):pass
 need(seen==set(expected),'TAR member missing')
 return dict(file_count=len(seen),member_bytes=total,all_member_bytes_SHA_verified=True,
             maximum_IO_read_bytes=CHUNK,extracted_to_disk=False,whole_clip_read_to_memory=False)


def retain(source,storage_root,batch,source_root,selected=None,preset=6,kind='full'):
 need(type(preset) is int and 0<=preset<=9,'XZ preset range0..9')
 need(selected is None or kind!='full','Full retention cannot select a subset of source members')
 batch_name(batch);storage_root=Path(storage_root).absolute();no_alias(storage_root)
 need(storage_root.is_dir(),'Existing storage root required')
 source,rows,all_names=snapshot(source,source_root,selected)
 root_readme=storage_root/'README.md';no_alias(root_readme);root_before=pin(root_readme)
 dest=storage_root/batch
 need(not dest.exists() and not dest.is_symlink(),'Existing target batch must never be overwritten')
 need(not dest.resolve().is_relative_to(source),'Destination cannot be inside source')
 dest.mkdir();packet=dest/PACKET_NAME;started=time.perf_counter();stage='pack'
 try:
  t=time.perf_counter();pack(packet,rows,preset);pack_s=time.perf_counter()-t;packet_pin=pin(packet)
  passes=[];stage='verify'
  for repeat in range(2):
   t=time.perf_counter();check_sources(source,source_root,rows,all_names)
   proof=verify_archive(packet,rows)
   need(pin(packet)==packet_pin,'Solid packet bytes drifted during verification')
   need(pin(root_readme)==root_before,'Storage root README changed')
   passes.append(dict(pass_number=repeat+1,elapsed_s=time.perf_counter()-t,**proof))
  sample=kind!='full'
  receipt=dict(schema='native-media-exact-original-solid-tar-xz-retention-v001',retainer_version='candidate-v001',
   source_archive=source.as_posix(),source_root=Path(source_root).resolve().as_posix(),storage_root=storage_root.resolve().as_posix(),
   status='SAMPLE_EXACT_BYTES_VERIFIED_NOT_FULL_E_RETENTION' if sample else 'EXACT_ORIGINALS_AND_PRESENTATION_RETAINED_BEFORE_REVIEW',
   kind=kind,full_source_member_retention=not sample,is_actual_E_retention=not sample and storage_root.resolve()==E_ROOT,
   packet=packet_pin,files=rows,source_full_member_names=all_names,source_bytes=sum(r['bytes'] for r in rows),file_count=len(rows),
   compression='one_solid_TAR_stream_in_XZ_LZMA2_CRC64',compression_preset=preset,pack_elapsed_s=pack_s,
   verification_passes=2,verification=passes,source_and_member_hash_mismatches=0,
   root_README_before=root_before,storage_root_README_unchanged=True,
   E_root_README_unchanged=True if storage_root.resolve()==E_ROOT else None,source_deleted=False,reencoded_originals=False,
   extraction_performed=False,publication=False,visual_reviewed=False,media_View=False,formal_complete_units=0,FinalAccepted=False)
  write_new(dest/'README.md',('原文件留在F原位；TAR.XZ成员保持每个源文件原字节。单一solid压缩流，没有图像/音频/视频重编码；两遍逐成员流式大小/SHA核验，不解压落盘、不覆盖旧批。保全不代表审阅或验收。\n'+
   ('本批仅少量真实PNG压缩样本，不是完整native片或实际E保全。\n' if sample else '')).encode('utf-8'))
  need(pin(root_readme)==root_before,'Storage root README changed before final index')
  receipt['total_elapsed_s']=time.perf_counter()-started;write_new(dest/INDEX_NAME,receipt)
  return receipt
 except BaseException as exc:
  failure=dict(schema='native-solid-retention-failure-v001',passed=False,stage=stage,exception_type=type(exc).__name__,reason=str(exc),
   source_archive=source.as_posix(),packet_path=packet.as_posix(),partial_outputs_preserved=True,source_deleted=False,
   E_retention_success_claimed=False,visual_reviewed=False,FinalAccepted=False)
  try:write_new(dest/'retention-failure-v001.json',failure)
  except Exception:pass
  raise


def verify_index(index):
 index=Path(index);r=read_json(index)
 need(r['schema']=='native-media-exact-original-solid-tar-xz-retention-v001' and r['verification_passes']==2,'Unknown/incomplete solid retention index')
 need(r['full_source_member_retention'] is (r['kind']=='full'), 'Full/sample retention scope mismatch')
 if r['full_source_member_retention']:
  need(sorted(x['member'] for x in r['files'])==r['source_full_member_names'],'Full-retention index omits source members')
 packet=index.parent/PACKET_NAME
 need(r['packet']['path']==packet.resolve().as_posix() and pin(packet)==r['packet'],'Packet pin changed')
 need(r['file_count']==len(r['files']) and r['source_bytes']==sum(x['bytes'] for x in r['files']),'Index count/size differs')
 out=[]
 for repeat in range(2):
  check_sources(Path(r['source_archive']),Path(r['source_root']),r['files'],r['source_full_member_names'])
  out.append(verify_archive(packet,r['files']));need(pin(packet)==r['packet'],'Packet drift')
 need(pin(Path(r['root_README_before']['path']))==r['root_README_before'],'Storage root README differs')
 return dict(schema='native-solid-readonly-independent-verification-v001',passed=True,index=pin(index),packet=r['packet'],passes=2,
  files=r['file_count'],source_bytes=r['source_bytes'],all_members_streamed_twice=True,kind=r['kind'],full_source_member_retention=r['full_source_member_retention'],
  actual_E_retention=r['is_actual_E_retention'],UE_started=False,View=False,FinalAccepted=False)


def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('--source');p.add_argument('--batch');p.add_argument('--preset',type=int,default=6)
 p.add_argument('--sample-frames',type=int);p.add_argument('--verify-index')
 a=p.parse_args()
 if a.verify_index:
  need(not a.source and not a.batch and a.sample_frames is None,'Verify-only cannot archive');result=verify_index(a.verify_index)
 else:
  need(a.source and a.batch,'--source and --batch required')
  selected=None;storage=E_ROOT;kind='full'
  if a.sample_frames is not None:
   need(2<=a.sample_frames<=14,'Sample must use2..14 existing real frames')
   source,files=source_members(a.source,SOURCE_ROOT)
   selected=[n for n in files if re.fullmatch(r'原件/MovieFrame[0-9]+\.png',n)][:a.sample_frames]
   need(len(selected)==a.sample_frames,'Not enough native original MovieFrame PNGs')
   storage=HERE/'sample-storage'
   if not storage.exists():storage.mkdir();write_new(storage/'README.md',b'Synthetic local sample storage root only. This is not E retention.\n')
   kind='sample_existing_native_PNG_only'
  receipt=retain(a.source,storage,a.batch,SOURCE_ROOT,selected,a.preset,kind)
  result=dict(index=pin(storage/a.batch/INDEX_NAME),packet=receipt['packet'],source_bytes=receipt['source_bytes'],files=receipt['file_count'],
              verification_passes=2,hash_mismatches=0,kind=kind,full_source_member_retention=receipt['full_source_member_retention'],
              actual_E_retention=receipt['is_actual_E_retention'],pack_elapsed_s=receipt['pack_elapsed_s'],total_elapsed_s=receipt['total_elapsed_s'],
              UE_started=False,View=False,FinalAccepted=False)
 print(json.dumps(result,ensure_ascii=False,allow_nan=False))

if __name__=='__main__':main()
