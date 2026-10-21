"""Preserve exact native PNG bytes in a lossless ZIP plus plain presentation copies.

F originals remain untouched. E's root README and prior batches remain untouched.
Every source/retained endpoint is checked twice; ZIP member bytes are the originals.
"""
from pathlib import Path
import argparse,datetime,hashlib,json,os,shutil,zipfile
R=Path('F:/Ourgame/过程图稿与视频');E=Path('E:/OurGame/Knight/过程图稿与视频')
def io(p):return Path('\\\\?\\'+str(p.resolve())) if os.name=='nt' else p
def value(p):
    b=io(p).read_bytes();return len(b),hashlib.sha256(b).hexdigest()
ap=argparse.ArgumentParser();ap.add_argument('--source',required=True);ap.add_argument('--batch',required=True);a=ap.parse_args()
S=(R/a.source).resolve();assert S.parent==R.resolve() and io(S).is_dir()
assert Path(a.batch).name==a.batch and '/' not in a.batch and '\\' not in a.batch
T=E/a.batch;assert T.resolve().parent==E.resolve() and not io(T).exists()
root_before=value(E/'README.md')
paths=[Path(str(p)[4:]) if str(p).startswith('\\\\?\\') else p for p in io(S).rglob('*') if p.is_file()]
assert paths and not any(p.is_symlink() for p in paths)
packed=[p for p in paths if p.parent==S/'原件' and p.suffix=='.png' and (p.name.startswith('MovieFrame') or p.name=='prewarm-viewport.png')]
plain=[p for p in paths if p not in set(packed)]
assert packed and len(packed)+len(plain)==len(paths)
io(T/'原件').mkdir(parents=True);io(T/'.gdignore').write_bytes(b'')
Z=T/'原件/native-originals.zip';rows=[]
with zipfile.ZipFile(io(Z),'x',compression=zipfile.ZIP_DEFLATED,compresslevel=3,allowZip64=True) as z:
    for i,p in enumerate(sorted(packed)):
        rel=p.relative_to(S).as_posix();b=io(p).read_bytes();size=len(b);sha=hashlib.sha256(b).hexdigest()
        zi=zipfile.ZipInfo.from_file(io(p),arcname=rel);zi.compress_type=zipfile.ZIP_DEFLATED
        z.writestr(zi,b,compresslevel=3)
        assert value(p)==(size,sha)
        rows.append(dict(source=p.as_posix(),relative=rel,bytes=size,sha256=sha,retention='lossless ZIP member; original bytes preserved',zip='原件/native-originals.zip'))
        if (i+1)%100==0:print(f'Packed {i+1}/{len(packed)} exact native PNGs',flush=True)
for p in sorted(plain):
    rel=p.relative_to(S);q=T/rel;io(q.parent).mkdir(parents=True,exist_ok=True);assert not io(q).exists()
    size,sha=value(p);shutil.copy2(io(p),io(q));assert value(q)==value(p)==(size,sha)
    rows.append(dict(source=p.as_posix(),relative=rel.as_posix(),bytes=size,sha256=sha,retention='plain exact copy'))
for checkpass in [1,2]:
    with zipfile.ZipFile(io(Z),'r') as z:
        assert len(z.namelist())==len(packed) and len(set(z.namelist()))==len(packed)
        for row in rows:
            assert value(Path(row['source']))==(row['bytes'],row['sha256'])
            if row['retention'].startswith('lossless'):
                b=z.read(row['relative']);assert len(b)==row['bytes'] and hashlib.sha256(b).hexdigest()==row['sha256']
            else:assert value(T/row['relative'])==(row['bytes'],row['sha256'])
    assert value(E/'README.md')==root_before
    print(f'Actual source/retained endpoint size/SHA pass {checkpass}: zero mismatches',flush=True)
result=dict(schema='lossless-native-PNG-ZIP-plus-plain-presentation-retention-v001',date=datetime.datetime.now().astimezone().isoformat(),canonical_source=S.as_posix(),target=T.as_posix(),original_source_files=len(rows),packed_native_pngs=len(packed),plain_copies=len(plain),unpacked_source_bytes=sum(x['bytes'] for x in rows),stored_media_bytes=value(Z)[0]+sum(x['bytes'] for x in rows if x['retention']=='plain exact copy'),zip_sha256=value(Z)[1],verification_passes=2,source_and_retained_size_SHA_mismatches=0,E_root_README_unchanged=True,F_originals_unchanged=True,not_publication_or_acceptance=True,files=rows)
io(T/'retention-verification-v001.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
io(T/'retention-README-v001.md').write_text('原始PNG的文件字节完整保存在原件/native-originals.zip相同相对路径成员中；不是重编码、重采样或修改像素。F原PNG保持，展示副本及索引为普通逐字节副本。两遍解包读取核对每项大小/SHA一致。为控制长期留档占用采用无损ZIP；不删除旧批次或修改E根README，不代表美术、声音或完整游戏验收。\n',encoding='utf-8')
print(json.dumps({k:v for k,v in result.items() if k!='files'},ensure_ascii=False))
