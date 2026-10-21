from pathlib import Path
import json,hashlib,shutil
R=Path('F:/Ourgame');A=R/'过程图稿与视频/2026-10-17_软皮轻甲左右待机试装_v001'
P=A/'review-player.html';assert not P.exists()
P.write_text('''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>软皮轻甲 · 实景试穿</title>
<style>body{margin:20px;background:#151a20;color:#ece8d9;font:16px system-ui}h1{font-size:24px;margin:0 0 10px}p{line-height:1.65;max-width:1120px}video{display:block;width:1280px;max-width:100%;height:auto;background:#000}button{padding:9px 16px;margin:0 10px 14px 0;background:#3c342a;color:#f6e9ce;border:1px solid #91794f;border-radius:4px}button:focus-visible{outline:3px solid #f5c369}small{color:#c9c2b1}</style>
<h1>软皮轻甲 · 实景试穿</h1>
<p>保留小比例钟盔与怪诞手绘，增强棕色胸衣和不对称短肩甲。片中通过实际拾取换上轻甲，再转身查看左右待机。</p>
<button id="new" onclick="v.src='展示副本/leather-ready-trial-silent.mp4';v.load();v.play()">播放新版皮甲试穿</button>
<button id="pause" onclick="v.pause()">暂停</button>
<button id="old" onclick="v.src='展示副本/existing-combo-flow-silent.mp4';v.load();v.play()">查看现有三段攻击流程（旧甲外观）</button>
<video id="v" controls preload="auto" src="展示副本/leather-ready-trial-silent.mp4"></video>
<p><small>新版只覆盖四帧待机，走路、攻击、受击、换装动作和声音继续制作。视频为 UE 实际运行的静音记录；地面拾取白框仍是占位。没有把待机试穿计为完整装备完成。</small></p></html>''',encoding='utf-8')
src=R/'过程图稿与视频/2026-10-17_军剑真实换装绑定_v006-guardCoinGREEN/展示副本/equipment-bound-flow-green-silent.mp4';q=A/'展示副本/existing-combo-flow-silent.mp4';assert not q.exists();shutil.copy2(src,q);assert src.read_bytes()==q.read_bytes()
v=dict(schema='leather-ready-live-review-player-v001',player=P.as_posix(),default_flow_source=src.as_posix(),default_flow_copy=q.as_posix(),default_flow_copy_sha256=hashlib.sha256(q.read_bytes()).hexdigest(),browser_playback='pending',formal_complete_units=0)
(A/'原件/review-player-source-v001.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(player=P.as_posix(),default_video_copy_byte_exact=True,new_video_must_exist_before_open=True),ensure_ascii=False))
