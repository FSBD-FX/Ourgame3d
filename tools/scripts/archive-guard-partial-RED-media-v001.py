from pathlib import Path
import hashlib,json,shutil
R=Path('F:/Ourgame');src=R/'过程图稿与视频/2026-10-18_石守卫三行整身原生试样_v001';out=R/'过程图稿与视频/2026-10-18_石守卫苏醒漏帧失败诊断展示_v001'
assert not out.exists();(out/'原件').mkdir(parents=True);(out/'展示副本').mkdir()
def pin(p):return dict(path=p.as_posix(),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())
rows=[]
for q in sorted((src/'展示副本').iterdir()):
 if not q.is_file():continue
 d=out/'展示副本'/q.name;shutil.copy2(q,d);assert pin(q)['sha256']==pin(d)['sha256'];rows.append(dict(source=pin(q),retained=pin(d)))
for q in [src/'index.json',src/'source-version-status-index.json',src/'原件/runtime-report.json',R/'tools/scripts/prepare-guard-partial-native-media-v001.py',Path(__file__)]:
 d=out/'原件'/q.name;shutil.copy2(q,d);assert pin(q)['sha256']==pin(d)['sha256'];rows.append(dict(source=pin(q),retained=pin(d)))
for q in sorted((src/'展示副本').glob('*UNSCALED-native.png')):
 d=out/'原件'/q.name;shutil.copy2(q,d);assert pin(q)['sha256']==pin(d)['sha256']
index=dict(schema='partial-guard-actual-RED-presentation-v001',status='FAILED_NATIVE_COVERAGE_PRESERVED_NOT_ACCEPTED',source_original_archive=src.as_posix(),full_original_retention='E:/OurGame/Knight/过程图稿与视频/2026-10-18-OurgameUE-guard-partial-native-RED-v392',failure='WakeMask61 missing frame1; actual ensure rejected authoritative interval stall requires diagnosis',visual_reviewed=False,formal_complete_units=0,files=rows)
(out/'source-version-status-index.json').write_text(json.dumps(index,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(out/'README.md').write_text('真实运行失败诊断展示：Wake缺第1帧，未通过完整原生覆盖。原始1537电影帧与预热帧/报告已E392保全，本批保存53.52秒原时序静音录像及17张未缩放阶段实景。不是成功验收。\n',encoding='utf-8')
print(json.dumps(dict(archive=out.as_posix(),files=len(rows),formal_complete_units=0)))
