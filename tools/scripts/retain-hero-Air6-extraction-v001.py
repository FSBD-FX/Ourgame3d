"""Preserve the exact Air6 extraction candidate; neither accepts nor imports it."""
from pathlib import Path
import hashlib, json, shutil

R = Path('F:/Ourgame')
S = R/'source-assets/production/fairytale-hero-state-gap-v001/air-state-preparation-v001/extraction-v001/run-Air6-shared-HD-v001'
O = R/'过程图稿与视频/2026-10-18_钟盔非攻击跳跃六相切帧审阅_v001'
assert S.is_dir() and not O.exists()
(O/'原件').mkdir(parents=True)
(O/'展示副本').mkdir()
def pin(p):
    d=p.read_bytes()
    return dict(path=p.as_posix(), bytes=len(d), sha256=hashlib.sha256(d).hexdigest())
rows=[]
for p in sorted(S.rglob('*')):
    if not p.is_file(): continue
    dst=O/'原件'/p.relative_to(S)
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(p,dst)
    assert pin(p)['sha256']==pin(dst)['sha256']
    rows.append(dict(source=pin(p), copy=pin(dst), role='unaccepted extracted source/QA'))
for p in sorted((S/'frames/jump_nonattack').glob('frame-*.png')):
    dst=O/'展示副本'/p.name
    shutil.copy2(p,dst)
    rows.append(dict(source=pin(p), copy=pin(dst), role='unchanged presentation copy'))
for name in ['jump_nonattack-contact.png','jump_nonattack.gif']:
    p=S/'qa'/name; dst=O/'展示副本'/name
    shutil.copy2(p,dst)
    rows.append(dict(source=pin(p), copy=pin(dst), role='SDK author preview, not runtime/physics'))
script=Path(__file__).resolve(); shutil.copy2(script,O/'原件'/script.name)
rows.append(dict(source=pin(script),copy=pin(O/'原件'/script.name),role='retention script'))
(O/'source-version-status-index.json').write_text(json.dumps(dict(schema='Root-Air6-extraction-retention-v001',files=rows,status='pending anatomical, source-root, sword and armor review',accepted=False,imported=False,source_request=253,shared_scale=True,per_pose_fit=False,preview_10fps_is_not_gameplay_clock=True,formal_complete_units=0,completed_combinations=0),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(O/'README.md').write_text('第253次钟盔非攻击跳跃六相切帧候选。标准 sprite-gen 实际分帧、共同缩放、图集、检查与10fps作者预览原件全部保留。不是游戏运行录像；未接受、未导入。身体根点、握持点、轻甲适配及真实起落衔接仍待检查；E留档和双重大小/SHA核验完成后才查看。\n',encoding='utf-8')
print(json.dumps(dict(archive=O.as_posix(),files=len(rows)),ensure_ascii=False))
