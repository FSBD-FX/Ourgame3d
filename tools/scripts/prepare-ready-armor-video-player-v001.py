from pathlib import Path
import hashlib,json,shutil
R=Path('F:/Ourgame');S=R/'过程图稿与视频/2026-10-16_钟盔军剑低位胸肩真实按键试装_v002'
A=R/'过程图稿与视频/2026-10-16_低位军剑胸肩试装播放复核_v001'
assert not A.exists();(A/'原件').mkdir(parents=True);(A/'展示副本').mkdir()
def desc(p):
 b=p.read_bytes();return {'path':p.as_posix(),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
entries=[]
v=S/'展示副本/fairytale-sword-lowguard-armor-ready-silent.mp4'
assert desc(v)['sha256']=='b09be9ee852ffd4e46e98a80cf3953cd6d742dd6c91af6f80afb50aa0ead95a1'
t=A/'展示副本/ready-armor-real-input-silent.mp4';shutil.copy2(v,t);assert desc(t)['sha256']==desc(v)['sha256']
entries.append({'source':desc(v),'retained':desc(t)})
frames=json.loads((S/'原件/selected-frame-source-map-v001.json').read_text(encoding='utf-8-sig'))['frames']
for i,label in [(16,'ready-right'),(6,'ready-left'),(12,'attack-right-no-armor')]:
 src=Path(frames[i]['unscaled_crop']['path']);target=A/'展示副本'/(label+'.png')
 assert desc(src)==frames[i]['unscaled_crop'];shutil.copy2(src,target);assert desc(src)['sha256']==desc(target)['sha256']
 entries.append({'source':desc(src),'retained':desc(target),'resampled':False})
html='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>怪诞钟盔 · 胸肩持剑实景试样</title><style>body{margin:24px;background:#141b21;color:#edf0df;font:16px system-ui}video{display:block;width:1280px;max-width:100%;background:#000}button{margin:16px 8px 16px 0;padding:10px 20px}p{max-width:980px;line-height:1.65}.crops{display:flex;gap:16px;flex-wrap:wrap}figure{margin:12px 0}figure img{display:block;width:240px;height:150px}figcaption{margin-top:8px;font-size:14px;color:#c0c5bc}</style><h1>怪诞钟盔：胸甲与双肩实景试样</h1><p>UE5真实按键录像。人物身体最高72px、游戏UI隐藏；胸甲、近肩与远肩已分层穿回持剑待机。已修正首次切帧角色消失的问题。</p><video id="v" controls preload="auto" src="展示副本/ready-armor-real-input-silent.mp4"></video><button onclick="v.currentTime=0;v.play()">从头播放</button><button onclick="v.pause()">暂停</button><p>本版是画风与穿戴候选：甲只覆盖四帧待机，攻击时会卸下，动作适配仍未完成。三段连招、全状态与音效继续制作。录像无声。</p><div class="crops"><figure><img src="展示副本/ready-right.png"><figcaption>右待机 · 原生像素裁切，未放大</figcaption></figure><figure><img src="展示副本/ready-left.png"><figcaption>左待机 · 原生像素裁切，未放大</figcaption></figure><figure><img src="展示副本/attack-right-no-armor.png"><figcaption>出剑尚无甲层 · 未完成的适配边界</figcaption></figure></div></html>'''
(A/'review-player.html').write_text(html,encoding='utf-8')
(A/'index.json').write_text(json.dumps({'files':entries,'source_capture_index':desc(S/'index.json'),'status':'Postfix recording actual checks pass; playback review pending, art and attack armor unaccepted','formal_complete_units':0,'audio_recorded':False,'snapshot':'v101'},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(A/'README.md').write_text('胸肩待机甲修复后真实录制的本地播放页。视频与局部裁切均按字节复制；展示前同步E，未经放大/重绘/重定时。甲适配仅待机，首斩无甲，不等完整装备单元。\n',encoding='utf-8')
print(json.dumps({'archive':A.as_posix(),'video':desc(t),'presented_crops':3},ensure_ascii=False))
