from pathlib import Path
import hashlib,json,shutil
R=Path('F:/Ourgame');A=R/'过程图稿与视频/2026-10-16_换装装备保持播放复核_v001'
assert not A.exists();(A/'原件').mkdir(parents=True);(A/'展示副本').mkdir();copies=[]
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def desc(p):
 b=p.read_bytes();return dict(path=p.as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def copy(p,q):
 d=desc(p);shutil.copy2(p,q);assert desc(q)['sha256']==d['sha256'];copies.append(dict(source=d,copy=desc(q),resampled=False,retimed=False))
for version,kind in [('v003-pendingRED','red'),('v004-pendingGREEN','green')]:
 s=R/f'过程图稿与视频/2026-10-16_军剑真实换装绑定_{version}'
 v=read(s/'原件/runtime-report.json');assert v['flow_complete'] and not v['reason'] and v['passed']==(kind=='green')
 assert len(v['mismatches'])==(6 if kind=='red' else 0)
 copy(s/f'展示副本/equipment-bound-flow-{kind}-silent.mp4',A/f'展示副本/{kind}-native-silent.mp4')
 for n in ['runtime-report.json','independent-bound-flow-verification-v001.json','source-and-snapshot-binding-verification-v001.json','video-presentation-receipt-v001.json']:
  copy(s/'原件'/n,A/'原件'/f'{kind}-{n}')
s=R/'过程图稿与视频/2026-10-16_军剑真实换装绑定_v004-pendingGREEN'
m=read(s/'原件/selected-native-source-map-v001.json')
for key,label in [('flow:baseline_no_armor','no-armor'),('flow:light_pending_cancel','pending-no-armor'),('flow:light_ready','light-armor'),('flow:medium_commit','pending-light-armor'),('flow:medium_unsupported_ready','unsupported-medium'),('flow:original_light_retaken_ready','retaken-light')]:
 row=next(x for x in m['frames'] if x['kind']==key);copy(Path(row['unscaled_crop']['path']),A/f'展示副本/{label}.png')
html='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>换装装备保持 · 实景复核</title>
<style>body{margin:24px;background:#141b21;color:#edf0df;font:16px system-ui}video{display:block;width:1280px;max-width:100%;background:#000}button{margin:16px 8px 16px 0;padding:10px 20px}p{max-width:1050px;line-height:1.65}.crops{display:flex;gap:20px;flex-wrap:wrap}figure{margin:12px 0}figure img{display:block;width:240px;height:160px}figcaption{margin-top:8px;font-size:14px;color:#c0c5bc}</style>
<h1>拾取时保留原来的军剑与轻甲</h1>
<p>当前UE实景：无甲 → 取消一次拾取 → 穿上轻甲 → 三段攻击 → 换中甲 → 重拾原轻甲。保留怪诞钟盔和小比例，换装尚未提交时继续显示已穿戴的装备。</p>
<video id="v" controls preload="auto" src="展示副本/green-native-silent.mp4"></video>
<button onclick="v.currentTime=0;v.play()">当前版从头播放</button><button onclick="v.pause()">暂停</button>
<button onclick="v.src='展示副本/red-native-silent.mp4';v.load();v.play()">查看修正前记录</button><button onclick="v.src='展示副本/green-native-silent.mp4';v.load();v.play()">切回当前版</button>
<p>本轮解决装备临时消失。拾取姿势仍借用待机帧，中甲未适配；场景道具标记仍为占位。当前144项回归通过，近战音频事件检查通过；这段录像静音，完整动作与音色、混音仍在制作。</p>
<div class="crops">
<figure><img src="展示副本/no-armor.png"><figcaption>无甲</figcaption></figure>
<figure><img src="展示副本/pending-no-armor.png"><figcaption>拾取未提交 · 保留军剑</figcaption></figure>
<figure><img src="展示副本/light-armor.png"><figcaption>轻甲已提交</figcaption></figure>
<figure><img src="展示副本/pending-light-armor.png"><figcaption>再次换装途中 · 保留原轻甲</figcaption></figure>
<figure><img src="展示副本/unsupported-medium.png"><figcaption>中甲 · 尚未适配外观</figcaption></figure>
<figure><img src="展示副本/retaken-light.png"><figcaption>重拾原轻甲</figcaption></figure></div></html>'''
(A/'review-player.html').write_text(html,encoding='utf-8')
(A/'index.json').write_text(json.dumps(dict(type='actual-pending-gear-before-after-review',copies=copies,source_snapshots=['v119 pending6RED','v121 current144GREEN/native pending0mismatch'],game_runs=2,formal_complete_units=0,audio_recorded=False,browser_playback='pending',art_review='NEEDS_WORK: pickup Ready0 placeholder, MED unavailable; full states and audio audition unfinished'),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(A/'README.md').write_text('实际普通输入换装静音录像原字节复制，待提交期间保留当前已提交装备，仅身份占位保持，并不接受完整拾取动作。当前原生140观察141原PNG/144回归，只有PickupArmor实景，PickupWeapon仍待另证；无新图像生成。\n',encoding='utf-8')
print(json.dumps(dict(archive=A.as_posix(),copied_files=len(copies),formal_complete_units=0),ensure_ascii=False))
