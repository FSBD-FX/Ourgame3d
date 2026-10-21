from pathlib import Path
import hashlib,json,shutil
R=Path('F:/Ourgame');M=R/'过程图稿与视频/2026-10-19_钟盔跳跃缺口双侧播放器_v001';assert not M.exists();(M/'原件').mkdir(parents=True);(M/'展示副本').mkdir()
def pin(p):return dict(path=p.as_posix(),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())
rows=[]
for side in ['left','right']:
 source=R/f'过程图稿与视频/2026-10-19_钟盔跳跃旧渲染缺口实录_{side}_v001/展示副本/hero-Air-baseline-native-mix-DIAGNOSTIC-v001.mp4'
 for folder in ['原件','展示副本']:
  p=M/folder/(side+'.mp4');shutil.copy2(source,p);assert pin(source)['sha256']==pin(p)['sha256'];rows.append(dict(source=pin(source),copy=pin(p)))
html='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>钟盔跳跃 · 原生缺口核对</title><style>body{background:#17191d;color:#eee;font:16px system-ui;margin:24px}h1{font-size:24px}section{display:grid;grid-template-columns:1fr 1fr;gap:16px}video{width:100%;background:#000}button{padding:12px;margin:12px 12px 12px 0}p,small{color:#b7bbc2}pre{white-space:pre-wrap}</style><h1>钟盔跳跃 · 原生缺口核对</h1><p>这是替换动作前的诊断记录：空中武器／轻甲缺失已复现，尚未接入六相新美术。保留原生混音，未作音效听感验收。</p><button id="left-play" onclick="playOne('left')">完整播放左侧</button><button id="right-play" onclick="playOne('right')">完整播放右侧</button><section><div><h2>左侧</h2><video id="left" controls preload="metadata" playsinline src="left.mp4"></video></div><div><h2>右侧</h2><video id="right" controls preload="metadata" playsinline src="right.mp4"></video></div></section><pre id="status">等待完整播放</pre><small>正常Enter／E／朝向／Space两次跳跃；Knight明确诊断清理，主角100HP。1倍速、无循环；原始PNG与PCM保留。</small><script>function status(){document.querySelector('#status').textContent=JSON.stringify([...document.querySelectorAll('video')].map(v=>({id:v.id,currentTime:v.currentTime,duration:v.duration,ended:v.ended,paused:v.paused,playbackRate:v.playbackRate,loop:v.loop,muted:v.muted,error:v.error?.message??null})),null,2)}function playOne(id){for(const v of document.querySelectorAll('video'))v.pause();const v=document.getElementById(id);v.currentTime=0;v.playbackRate=1;v.loop=false;v.muted=false;v.play().catch(e=>document.querySelector('#status').textContent=e.message)}for(const v of document.querySelectorAll('video'))for(const e of ['loadedmetadata','timeupdate','play','ended','error'])v.addEventListener(e,status);</script></html>'''
for folder in ['原件','展示副本']:(M/folder/'player.html').write_text(html,encoding='utf-8')
shutil.copy2(Path(__file__),M/'原件'/Path(__file__).name)
(M/'source-version-status-index.json').write_text(json.dumps(dict(schema='Root-Air6-baseline-player-v001',files=rows+ [dict(copy=pin(M/f/'player.html')) for f in ['原件','展示副本']],status='retained diagnostic originals; actual full playback pending',published=False,formal_complete_units=0),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(M/'README.md').write_text('左右原生缺口录像的本机审阅播放器。两份MP4逐字节复制，保留实际混音但未听感验收；不是新Air美术通过片。展示前E两SHA保全，之后实际1倍速播放至末尾另存审阅。仅127.0.0.1本机服务，无上传或发布。\n',encoding='utf-8')
print(json.dumps(dict(media=M.as_posix(),videos=2),ensure_ascii=False))
