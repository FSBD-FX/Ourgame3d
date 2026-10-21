from pathlib import Path
import hashlib,json,shutil
R=Path('F:/Ourgame');A=R/'过程图稿与视频/2026-10-16_军剑真实换装绑定播放复核_v001';assert not A.exists()
(A/'原件').mkdir(parents=True);(A/'展示副本').mkdir();copies=[]
def desc(p):
 b=p.read_bytes();return dict(path=p.as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def copy(p,q):
 d=desc(p);shutil.copy2(p,q);assert desc(q)['sha256']==d['sha256'];copies.append(dict(source=d,copy=desc(q),resampled=False,retimed=False))
for version,kind,sha in [('v001-RED','red','b3693edd2b03bab57076a57e4c687fd32e2a633c64031c15ffae31d0a0a09d39'),('v002-GREEN','green','048aff329a21a7c2e6448a90698cf90200c5b90b5dfb7d19182fa92d4444b7cf')]:
 s=R/f'过程图稿与视频/2026-10-16_军剑真实换装绑定_{version}';p=s/f'展示副本/equipment-bound-flow-{kind}-silent.mp4';assert desc(p)['sha256']==sha
 copy(p,A/f'展示副本/{kind}-native-silent.mp4')
 for n in ['runtime-report.json','independent-bound-flow-verification-v001.json','source-and-snapshot-binding-verification-v001.json','video-presentation-receipt-v001.json']:
  copy(s/'原件'/n,A/'原件'/f'{kind}-{n}')
s=R/'过程图稿与视频/2026-10-16_军剑真实换装绑定_v002-GREEN';m=json.loads((s/'原件/selected-native-source-map-v001.json').read_text(encoding='utf-8'))
for key,label in [('flow:baseline_no_armor','no-armor'),('flow:light_ready','light-armor'),('flow:original_light_retaken_ready','retaken-light'),('combo:2:3','low-finish')]:
 row=next(x for x in m['frames'] if x['kind']==key);copy(Path(row['unscaled_crop']['path']),A/f'展示副本/{label}.png')
html='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>军剑 · 真实装备绑定复核</title>
<style>body{margin:24px;background:#141b21;color:#edf0df;font:16px system-ui}video{display:block;width:1280px;max-width:100%;background:#000}button{margin:16px 8px 16px 0;padding:10px 20px}p{max-width:1050px;line-height:1.65}.crops{display:flex;gap:20px;flex-wrap:wrap}figure{margin:12px 0}figure img{display:block;width:240px;height:160px}figcaption{margin-top:8px;font-size:14px;color:#c0c5bc}</style>
<h1>军剑：真实拾取、取消、换甲与重拾</h1>
<p>UE5实际输入录像。无甲起步 → 取消一次轻甲拾取 → 提交轻甲 → 三段攻击 → 中甲替换 → 重拾原来的轻甲。当前画面由实际提交的装备实例控制；小比例、钟盔和无游戏UI保持。</p>
<video id="v" controls preload="auto" src="展示副本/green-native-silent.mp4"></video>
<button onclick="v.currentTime=0;v.play()">当前版从头播放</button><button onclick="v.pause()">暂停</button>
<button onclick="v.src='展示副本/red-native-silent.mp4';v.load();v.play()">查看修正前记录</button><button onclick="v.src='展示副本/green-native-silent.mp4';v.load();v.play()">切回当前版</button>
<p>片中的道具来源用于受控交互核验。换装动作与中甲仍为占位表现；中甲不会被替画成轻甲。第三刀调整了抬剑和低位收刀角度，握姿、轮廓、完整状态、敌人和音效继续制作。录像静音。</p>
<div class="crops"><figure><img src="展示副本/no-armor.png"><figcaption>真实无甲</figcaption></figure><figure><img src="展示副本/light-armor.png"><figcaption>提交轻甲后</figcaption></figure><figure><img src="展示副本/retaken-light.png"><figcaption>同实例重拾后</figcaption></figure><figure><img src="展示副本/low-finish.png"><figcaption>第三刀低位收刀 · 原比例裁图</figcaption></figure></div></html>'''
(A/'review-player.html').write_text(html,encoding='utf-8')
(A/'index.json').write_text(json.dumps(dict(type='actual-native-transaction-before-after-review',copies=copies,source_snapshots=['v117 semanticRED','v118 current141GREEN/native transaction0mismatch'],game_runs=2,formal_complete_units=0,audio_recorded=False,browser_playback='pending',art_review='NEEDS_WORK: pending/medium placeholders; all motion/audio incomplete'),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(A/'README.md').write_text('两份实际换装流程静音实录原字节复制。v117六处错误显示与v118零错误保留，三提交/同实例重拾仅受控QA事务证据。新低剑尖和握姿仍需美术审阅，全状态、其他装备/敌人和音效未完成。\n',encoding='utf-8')
print(json.dumps(dict(archive=A.as_posix(),copied_files=len(copies),formal_complete_units=0),ensure_ascii=False))
