from pathlib import Path
import hashlib,json,shutil
R=Path('F:/Ourgame');S=R/'过程图稿与视频/2026-10-16_钟盔军剑首斩穿甲真实按键试装_v001';A=R/'过程图稿与视频/2026-10-16_军剑首斩穿甲播放复核_v001'
assert not A.exists();(A/'原件').mkdir(parents=True);(A/'展示副本').mkdir()
def desc(p):
 b=p.read_bytes();return {'path':p.as_posix(),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
entries=[];v=S/'展示副本/fairytale-sword-primary1-armor-silent.mp4'
assert desc(v)['sha256']=='8b11160b7710d141db982f33036fcb4370980813e89a063a910f5b6cf72ca1ea'
t=A/'展示副本/primary1-armor-real-input-v103-silent.mp4';shutil.copy2(v,t);assert desc(t)['sha256']==desc(v)['sha256'];entries.append({'source':desc(v),'retained':desc(t)})
frames=json.loads((S/'原件/selected-frame-source-map-v001.json').read_text(encoding='utf-8-sig'))['frames']
for i,label in [(16,'ready-right'),(12,'cut-right'),(3,'follow-left')]:
 source=Path(frames[i]['unscaled_crop']['path']);assert desc(source)==frames[i]['unscaled_crop'];target=A/'展示副本'/(label+'.png');shutil.copy2(source,target);assert desc(source)['sha256']==desc(target)['sha256'];entries.append({'source':desc(source),'retained':desc(target),'resampled':False})
html='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>怪诞钟盔 · 穿甲首斩试装</title><style>body{margin:24px;background:#141b21;color:#edf0df;font:16px system-ui}video{display:block;width:1280px;max-width:100%;background:#000}button{margin:16px 8px 16px 0;padding:10px 20px}p{max-width:980px;line-height:1.65}.crops{display:flex;gap:16px;flex-wrap:wrap}figure{margin:12px 0}figure img{display:block;width:240px;height:150px}figcaption{margin-top:8px;font-size:14px;color:#c0c5bc}</style><h1>怪诞钟盔：穿甲首斩试装</h1><p>UE5真实按键录像。人物身体最高72px、游戏UI隐藏；胸甲和双肩甲随第一斩的六个姿势保留。</p><video id="v" controls preload="auto" src="展示副本/primary1-armor-real-input-v103-silent.mp4"></video><button onclick="v.currentTime=0;v.play()">从头播放</button><button onclick="v.pause()">暂停</button><p>当前覆盖持剑待机与地面第一斩。后两段连招、走跑、受击、死亡等状态继续制作。录像无声；肩甲细节和握剑关系仍在打磨。</p><div class="crops"><figure><img src="展示副本/ready-right.png"><figcaption>右待机 · 原生像素裁切，未放大</figcaption></figure><figure><img src="展示副本/cut-right.png"><figcaption>右首斩 · 胸肩保留，横臂遮挡</figcaption></figure><figure><img src="展示副本/follow-left.png"><figcaption>左收刀 · 原生像素裁切，未放大</figcaption></figure></div></html>'''
(A/'review-player.html').write_text(html,encoding='utf-8')
(A/'index.json').write_text(json.dumps({'files':entries,'source_capture_index':desc(S/'index.json'),'status':'Actual Ready7/Primary8 runtime/nativepixel/head checks pass; explicit video playback/art review pending','snapshot':'v103','source_codec_at_capture':'actual3GREEN1RED; NUL correction later does not rewrite video source binding','formal_complete_units':0,'audio_recorded':False},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(A/'README.md').write_text('v103首斩穿甲真实按键录像播放页；视频和裁图按字节复制，人物72px、无UI、静音。只有Ready4/Primary1six候选，不等正式装备或全动作完成。新codec修复不倒填本录像版本。\n',encoding='utf-8')
print(json.dumps({'archive':A.as_posix(),'video':desc(t),'cropped_stills':3},ensure_ascii=False))
