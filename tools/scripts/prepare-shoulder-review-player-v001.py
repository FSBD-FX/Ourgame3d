"""A local player for the retained actual MP4. Does not edit any media."""
from pathlib import Path
import hashlib,json,shutil
root=Path('F:/Ourgame');media=root/'过程图稿与视频';out=media/'2026-10-16_肩甲实景复核播放页_v001';assert not out.exists();out.mkdir()
video=media/'2026-10-16_暗黑童话双肩甲明暗双向真实观察_v001/展示副本/fairytale-shoulder-lookdev-silent.mp4'
assert hashlib.sha256(video.read_bytes()).hexdigest()=='22850a1bb713e8700a7e81a95050406f1dbf242fa397cad662ea5ecbd85e9366'
html='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>双肩甲实际运行复核</title>
<style>body{margin:0;background:#12171b;color:#d7d9da;font:15px system-ui}main{max-width:1280px;margin:16px auto}video{width:100%;display:block}p{line-height:1.6}button{margin-right:8px;padding:6px 12px}output{font-variant-numeric:tabular-nums}</style>
<main><p>实际 UE 录像 · 72px角色 · UI隐藏 · 胸甲常显 · 双肩与单肩对照。明暗为背景位置变化。无声音；待机观察不代表完整装备或战斗验收。</p>
<video id="proof" controls preload="auto" playsinline src="../2026-10-16_暗黑童话双肩甲明暗双向真实观察_v001/展示副本/fairytale-shoulder-lookdev-silent.mp4"></video>
<p><button id="play">从头播放</button><button id="pause">暂停</button><output id="status">待播放</output></p>
<p id="phase"></p></main><script>
const v=document.querySelector('video'),s=document.querySelector('output'),p=document.querySelector('#phase');
const phases=['亮场/右/胸甲基础','亮场/右/双肩','亮场/左/胸甲基础','亮场/左/双肩','暗场/右/胸甲基础','暗场/右/双肩','暗场/左/胸甲基础','暗场/左/双肩','亮场/右/近肩单独','亮场/右/远肩单独','亮场/左/近肩单独','亮场/左/远肩单独'];
document.querySelector('#play').onclick=()=>{v.currentTime=0;v.play()};document.querySelector('#pause').onclick=()=>v.pause();
v.ontimeupdate=()=>{s.textContent=v.currentTime.toFixed(3)+' / '+v.duration.toFixed(3)+' 秒 · '+(v.paused?'暂停':'播放');p.textContent=phases[Math.min(11,Math.floor(v.currentTime/2.1))]};
</script></html>'''
(out/'index.html').write_text(html,encoding='utf-8')
refs=[root/'docs/production/first-batch-v2/evidence/fairytale-shoulder-runtime-v001/selected-original48-v001.json',
 root/'docs/production/first-batch-v2/fairytale-shoulder150-static-review-v001.md',
 root/'docs/production/first-batch-v2/evidence/run-exploration-v001/independent-hud-boundary-review-v001.md',
 root/'docs/production/first-batch-v2/evidence/run-exploration-v001/independent-owner-review-v001/independent-run-exploration-owner-review-v001.md']
rows=[]
for i,src in enumerate(refs):
 dst=out/f'{i:02d}-{src.name}';shutil.copy2(src,dst);assert src.read_bytes()==dst.read_bytes()
 rows.append({'source':src.as_posix(),'retained_relative':dst.name,'sha256':hashlib.sha256(src.read_bytes()).hexdigest()})
(out/'source-version-status-index.json').write_text(json.dumps({'files':rows,'video':video.as_posix(),'video_sha256':'22850a1bb713e8700a7e81a95050406f1dbf242fa397cad662ea5ecbd85e9366','video_already_retained':'E106','status':'Technical local review player, no media edits; runtime visual review pending','formal_complete_units':0},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(out/'README.md').write_text('Playback UI only. Source video unchanged and already retained under E106. Selection and static/bank reviews preserved; playback has not yet been performed. Not in-game UI or acceptance.\n',encoding='utf-8')
print(json.dumps({'archive':out.as_posix(),'html':(out/'index.html').as_posix(),'video_unchanged':True},ensure_ascii=False))
