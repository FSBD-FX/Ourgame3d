from pathlib import Path
import hashlib,json,shutil
R=Path('F:/Ourgame')
A=R/'过程图稿与视频/2026-10-16_低位军剑动作播放复核_v001'
S=R/'过程图稿与视频/2026-10-16_钟盔军剑低位真实按键双向动作_v001'
assert not A.exists();(A/'原件').mkdir(parents=True);(A/'展示副本').mkdir()
def desc(p):
 b=p.read_bytes();return {'path':p.as_posix(),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
v=S/'展示副本/fairytale-sword-lowguard-normal-input-silent.mp4'
assert desc(v)['sha256']=='05f83b7f94c4d1592d196654b591e14b72d981b538fe9698eb14a7c5cd70e8b1'
t=A/'展示副本/lowguard-real-input-silent.mp4';shutil.copy2(v,t);assert desc(t)['sha256']==desc(v)['sha256']
html='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>钟盔军剑低位持握 · 真实按键试录</title><style>body{margin:24px;background:#141b21;color:#edf0df;font:16px system-ui}video{display:block;width:1280px;max-width:100%;background:#000}button{margin:16px 8px 16px 0;padding:10px 20px}p{max-width:950px;line-height:1.65}</style><h1>钟盔军剑：低位持握试样</h1><p>实际 UE5 画面，人物身体最高72px、界面隐藏。Enter 开始，J 首斩，A 换向后再 J。来源为原生截图按实测时间组成的无声视频。</p><video id="v" controls preload="auto" src="展示副本/lowguard-real-input-silent.mp4"></video><button onclick="v.currentTime=0;v.play()">从头播放</button><button onclick="v.pause()">暂停</button><p>本批只看待机和第一段斩击；尚未穿新胸肩甲。三段连招、完整状态动作、装备适配与声音仍在制作。源动作表预览的时长缺陷已另记；游戏内沿真实战斗相位取帧。</p></html>'''
(A/'review-player.html').write_text(html,encoding='utf-8')
index={'status':'Runtime structural checks passed; continuous browser review pending','source_video':desc(v),'presentation_video':desc(t),'source_capture_index':desc(S/'index.json'),'html':desc(A/'review-player.html'),'formal_complete_units':0,'audio_recorded':False,'not_final_art_acceptance':True}
(A/'index.json').write_text(json.dumps(index,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(A/'README.md').write_text('低位持剑真实按键试录的本地播放页。视频按字节复制；显示前同步E。无声、无新甲，未据此认定动作或完整单元完成。\n',encoding='utf-8')
print(json.dumps({'archive':A.as_posix(),'video':desc(t)},ensure_ascii=False))
