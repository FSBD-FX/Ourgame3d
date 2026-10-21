"""Create a new local player from two actually prepared and retained native videos."""
from pathlib import Path
import hashlib,json,shutil
from urllib.parse import quote
R=Path('F:/Ourgame');O=R/'过程图稿与视频/2026-10-18_裂岩守卫七件步态双侧播放器_v001'
assert not O.exists();(O/'原件').mkdir(parents=True);(O/'展示副本').mkdir()
def pin(p):return dict(path=p.as_posix(),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())
clips={};inputs=[]
for side in ['left','right']:
 m=R/f'过程图稿与视频/2026-10-18_裂岩守卫七件步态与入战实录审阅_{side}_v001/source-version-status-index.json'
 d=json.loads(m.read_text(encoding='utf-8-sig'));v=Path(d['video']['path']);assert pin(v)==d['video']
 assert d['native_frame_count']==d['presentation_frame_retention']['decoded_frames'] and d['required_sample_count']==6 and d['required_join_count']==2
 clips[side]='http://127.0.0.1:56249/'+quote(v.relative_to(R).as_posix())
 inputs.append(dict(side=side,index=pin(m),video=pin(v)))
html='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>裂岩守卫七件步态 · 左右实录</title><style>body{margin:0;background:#101820;color:#e6e9df;font:16px system-ui}header{padding:12px 18px}button{font:inherit;padding:8px 14px;margin-right:10px;cursor:pointer}small{display:block;padding-top:8px;color:#b6c0b6}video{display:block;width:100%;max-width:1280px;margin:auto}#status{margin-left:12px}</style><header><button onclick="loadClip('left')">播放左侧完整实录</button><button onclick="loadClip('right')">播放右侧完整实录</button><span id="status">待播放</span><small>静音实录 · 实际行走→停步挥斧→回待机 · Knight／Bat前置诊断清理 · 步态和动作衔接试样</small></header><video id="clip" controls playsinline preload="metadata"></video><script>const clips=CLIPS;const v=document.getElementById('clip');function loadClip(side){v.src=clips[side];v.loop=false;v.playbackRate=1;v.load();v.play();document.getElementById('status').textContent=side==='left'?'左侧完整实录':'右侧完整实录';}v.addEventListener('ended',()=>document.getElementById('status').textContent+=' · 播放结束');</script></html>'''.replace('CLIPS',json.dumps(clips,ensure_ascii=False))
p=O/'原件/player.html';p.write_text(html,encoding='utf-8');shutil.copy2(p,O/'展示副本/player.html')
d=dict(schema='Root-Move7-two-side-review-player-v001',inputs=inputs,files=[pin(p),pin(O/'展示副本/player.html')],visual_reviewed=False,audio_recorded=False,FinalAccepted=False)
(O/'source-version-status-index.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(O/'README.md').write_text('完整静音双侧真实实录播放器。原视频与全PNG原件分别在已独立保全的媒体和原生目录，播放器只引用这些本地文件；没有上传。完整内容、声音、足锁及最终美术未验收。须保全本播放器后再打开。\n',encoding='utf-8')
print(json.dumps(dict(player=pin(O/'展示副本/player.html'),url='http://127.0.0.1:56249/'+quote((O/'展示副本/player.html').relative_to(R).as_posix())),ensure_ascii=False))
