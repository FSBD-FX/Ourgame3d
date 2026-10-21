from pathlib import Path
import json
R=Path('F:/Ourgame');T=R/'tools/scripts'
report=R/'docs/production/first-batch-v2/evidence/armor-primary2-retention-failure-v001.json';assert not report.exists()
report.write_text(json.dumps({'fact':'Initial input retainer assumed lowercase files/path/bytes/sha256; actual frozen schema uses Files/Path/Bytes/SHA256. KeyError occurred before any copy.',
    'F_partial':'过程图稿与视频/2026-10-16_军剑上挑胸甲双肩输入_v001','E212_status':'empty diagnostic copy, 0 source files; not successful input retention',
    'source_assets_changed':False,'remediation':'New version2 archive and explicit frozen schema normalization; generic version3 retainer rejects empty sources before destination creation.'},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
p=T/'retain-armor-primary2-inputs-v001.py';q=T/'retain-armor-primary2-inputs-v002.py';assert not q.exists()
s=p.read_text(encoding='utf-8').replace('军剑上挑胸甲双肩输入_v001','军剑上挑胸甲双肩输入_v002')
s=s.replace("f=json.loads(F.read_text(encoding='utf-8'));h=", "f=json.loads(F.read_text(encoding='utf-8'));f['files']=[{'path':Path(row['Path']).as_posix(),'bytes':int(row['Bytes']),'sha256':row['SHA256']} for row in f['Files']];assert len(f['files'])==40;h=")
q.write_text(s,encoding='utf-8')
p=T/'retain-ue-process-media-v002.py';q=T/'retain-ue-process-media-v003.py';assert not q.exists()
s=p.read_text(encoding='utf-8');old="assert source.parent==" # New version keeps all old path/hash rules; only empty-source admission changes.
anchor='    assert not source.is_symlink()\n';assert s.count(anchor)==1
s=s.replace(anchor,anchor+"    assert any(p.is_file() for p in source.rglob('*')), f'Empty source batch is not retention: {source}'\n")
q.write_text(s,encoding='utf-8')
print(json.dumps({'failed_empty_batch_preserved':'E212','new_archive_version':'v002','new_retainer':'retain-ue-process-media-v003.py'}))
