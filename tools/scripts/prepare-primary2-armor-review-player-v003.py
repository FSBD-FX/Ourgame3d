from pathlib import Path
import hashlib,json,shutil
R=Path('F:/Ourgame');A=R/'过程图稿与视频/2026-10-16_军剑第二段上挑连续出招播放复核_v003'
assert not A.exists();(A/'原件').mkdir(parents=True);(A/'展示副本').mkdir()
def d(p):
 b=p.read_bytes();return dict(path=p.as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
entries=[]
for v,sha in [('003','791c63b9f19f27f23b5074856d65afe85c01153dd2a074b6a79b59f359e101a1'),('004','ed3bea998da2015b7f79e6c22f3d2e30a8da3fa5f8a6ed7622fb2d0936a9ea11')]:
 S=R/f'过程图稿与视频/2026-10-16_钟盔军剑第二段真实连击试装_v{v}'
 for p,q in [(S/'展示副本/fairytale-sword-primary2-fit-silent.mp4',A/f'展示副本/primary2-fit-v{v}-native-silent.mp4'),(S/'index.json',A/f'原件/capture-v{v}-index.json')]:
  if p.suffix=='.mp4':assert d(p)['sha256']==sha
  shutil.copy2(p,q);assert d(p)['sha256']==d(q)['sha256'];entries.append(dict(source=d(p),copy=d(q),retimed=False))
for i,n in [(23,'low-windup'),(24,'low-cut'),(25,'high-cut')]:
 S=R/'过程图稿与视频/2026-10-16_钟盔军剑第二段真实连击试装_v004/展示副本'
 p=next(S.glob(f'crop-{i:02d}-*.png'));q=A/f'展示副本/{n}.png';shutil.copy2(p,q)
 assert d(p)['sha256']==d(q)['sha256'];entries.append(dict(source=d(p),copy=d(q),resampled=False))
html='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>钟盔军剑 · 两段穿甲实景</title>
<style>body{margin:24px;background:#141b21;color:#edf0df;font:16px system-ui}video{display:block;width:1280px;max-width:100%;background:#000}button{margin:16px 8px 16px 0;padding:10px 20px}p{max-width:1000px;line-height:1.65}.crops{display:flex;gap:16px;flex-wrap:wrap}figure{margin:12px 0}figure img{display:block;width:240px;height:150px}figcaption{margin-top:8px;font-size:14px;color:#c0c5bc}</style>
<h1>钟盔军剑：两段穿甲实景</h1><p>UE5真实按键录像，左右各一组连续两段攻击。第二段已补胸甲、近肩和远肩，折臂时按前后关系遮挡；人物身体最高72px，游戏UI隐藏。</p>
<video id="v" controls preload="auto" src="展示副本/primary2-fit-v004-native-silent.mp4"></video>
<button onclick="v.currentTime=0;v.play()">新版从头播放</button><button onclick="v.pause()">暂停</button>
<button onclick="v.src='展示副本/primary2-fit-v003-native-silent.mp4';v.load();v.play()">查看补甲前</button>
<button onclick="v.src='展示副本/primary2-fit-v004-native-silent.mp4';v.load();v.play()">切回穿甲版</button>
<p>当前为两段动作试装。握柄、盔下沿间隙和脚步仍需打磨；第三段及其他状态继续制作。录像无声，尚未完成整套装备与战斗视听验收。</p>
<div class="crops"><figure><img src="展示副本/low-windup.png"><figcaption>低位起手</figcaption></figure><figure><img src="展示副本/low-cut.png"><figcaption>折臂切入</figcaption></figure><figure><img src="展示副本/high-cut.png"><figcaption>抬腕上挑 · 原生裁图未放大</figcaption></figure></div></html>'''
(A/'review-player.html').write_text(html,encoding='utf-8')
(A/'index.json').write_text(json.dumps(dict(sources=entries,status='native171+172/173/174 v115 full138GREEN; Root32crops+2whole seen, browser playback pending',source_snapshots=dict(old='v114',new='v115'),formal_complete_units=0,armor_primary2_present=True,audio_recorded=False),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(A/'README.md').write_text('同171身体补甲前v114与新v115双向连续两段静音实录逐字节复制；保持旧版。已看原比例静帧，握柄/足锁/完整动作/视听待审，不代表整套装备完成。\n',encoding='utf-8')
print(json.dumps(dict(archive=A.as_posix(),copied_media=len(entries)),ensure_ascii=False))
