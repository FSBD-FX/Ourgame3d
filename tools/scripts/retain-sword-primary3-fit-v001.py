"""Root-only explicit E retention. Default reports a plan; never runs UE or edits E-root README."""
from pathlib import Path
import argparse,hashlib,json,os,shutil

ROOT=Path('F:/Ourgame')
E_ROOT=Path('E:/OurGame/Knight/过程图稿与视频')
DEFAULT_ARCHIVE='过程图稿与视频/2026-10-16_钟盔军剑三段真实连击试装_v001'
DEFAULT_BATCH='2026-10-16-OurgameUE-primary3-real-threeJ-fit-v240'

def io_path(path):
    path=Path(path)
    return Path('\\\\?\\'+str(path.resolve())) if os.name=='nt' else path
def desc(path):
    data=io_path(path).read_bytes();return {'path':path.as_posix(),'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()}
def load(path):return json.loads(io_path(path).read_text(encoding='utf-8-sig'))
def new(path,data):
    with io_path(path).open('x',encoding='utf-8') as handle:handle.write(data if isinstance(data,str) else json.dumps(data,ensure_ascii=False,indent=2)+'\n')

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--archive',default=DEFAULT_ARCHIVE)
    parser.add_argument('--snapshot',required=True);parser.add_argument('--batch-name',default=DEFAULT_BATCH)
    parser.add_argument('--execute',action='store_true');args=parser.parse_args()
    assert Path(args.batch_name).name==args.batch_name and '/' not in args.batch_name and '\\' not in args.batch_name
    archive=(ROOT/args.archive).resolve();snapshot=(ROOT/args.snapshot).resolve()
    assert archive.is_relative_to((ROOT/'过程图稿与视频').resolve())
    assert snapshot.is_relative_to((ROOT/'source-assets/production/backups').resolve())
    target=E_ROOT/args.batch_name
    assert args.batch_name not in ('.','..') and target.resolve().parent==E_ROOT.resolve(), 'E batch must be one contained directory'
    assert not io_path(target).exists(), 'Retain prior batches; use a fresh Root-assigned name'
    if not args.execute:
        print(json.dumps({'executed':False,'source_archive':archive.as_posix(),'snapshot':snapshot.as_posix(),
            'planned_E_batch':target.as_posix(),'actual_files':None,'actual_bytes':None,'actual_mismatches':None,
            'E_root_README_will_be_edited':False},ensure_ascii=False));return
    runtime=load(archive/'原件/runtime-report.json')
    verification=load(archive/'原件/sword-primary3-fit-runtime-verification-v001.json')
    assert runtime['passed'] and runtime['primary3_armor_trial'] and verification['passed']
    assert load(archive/'原件/native-pixel-verification.json')['every_source_viewport_pixel_crc_matches']
    assert load(archive/'原件/compiled-source-binding-audit-v001.json')['mismatches']==0
    assert load(archive/'原件/video-presentation-receipt-v001.json')['full_decode_exit']==0
    files=[(p,p.relative_to(archive)) for p in archive.rglob('*') if p.is_file()]
    files.append((snapshot/'compiled-source-manifest.json',Path('原件/provenance/compiled-source-manifest.json')))
    for name in ('DungeonHUD.cpp','DungeonFairytaleSwordPresentation.cpp','DungeonFairytaleSwordProbe.cpp',
        'DungeonFairytaleSwordPrimary3V001.inl','DungeonFairytaleSwordPrimary2V003.inl','DungeonFairytaleSwordPrimary2ArmorV001.inl',
        'DungeonFairytaleSwordDrawState.h','DungeonProofScreenshots.cpp','DungeonProofScreenshots.h'):
        files.append((snapshot/'UnrealGame/Source/CodexDungeon'/name,Path('原件/provenance/Source')/name))
    files.append((Path(__file__).resolve(),Path('原件/provenance/tool-retain-sword-primary3-fit-v001.py')))
    assert len({rel.as_posix().casefold() for source,rel in files})==len(files)
    source_values=[(source,rel,desc(source)) for source,rel in files]
    root_readme=E_ROOT/'README.md';readme_before=desc(root_readme)
    io_path(target).mkdir();rows=[]
    for source,rel,pin in source_values:
        out=target/rel;io_path(out.parent).mkdir(parents=True,exist_ok=True)
        assert not io_path(out).exists();shutil.copy2(io_path(source),io_path(out))
        got=desc(out);assert io_path(source).read_bytes()==io_path(out).read_bytes() and got['bytes']==pin['bytes'] and got['sha256']==pin['sha256']
        rows.append({'source':pin,'copy':got})
    # A second independent pass verifies every actual endpoint without trusting copy results.
    for row in rows:
        for kind in ('source','copy'):
            assert desc(Path(row[kind]['path']))==row[kind]
    assert desc(root_readme)==readme_before
    result={'schema':'primary3-real-three-stage-E-retention-v001','executed':True,'source_archive':archive.as_posix(),
        'target':target.as_posix(),'files':rows,'file_count':len(rows),'bytes':sum(x['copy']['bytes'] for x in rows),
        'first_pass_mismatches':0,'second_pass_mismatches':0,'E_root_README_unchanged':True,
        'retention_is_not_publication_or_visual_acceptance':True,'formal_complete_units':0}
    new(target/'retention-verification-v001.json',result)
    new(target/'retention-README-v001.md','Root明确执行的第三段实景保全；全部原件、展示副本和Source provenance原字节复制，两遍大小/SHA一致。保留不代表画面、握柄、足锁、命中、音效或完整内容验收；E根README未改。\n')
    print(json.dumps({k:v for k,v in result.items() if k!='files'},ensure_ascii=False))

if __name__=='__main__':main()
