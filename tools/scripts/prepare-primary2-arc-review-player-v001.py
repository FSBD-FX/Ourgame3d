from pathlib import Path
import hashlib
import json
import shutil

R = Path('F:/Ourgame')
A = R / '过程图稿与视频/2026-10-16_军剑第二段上挑连续出招播放复核_v001'
assert not A.exists(), A
(A / '原件').mkdir(parents=True)
(A / '展示副本').mkdir()

def desc(p):
    b = p.read_bytes()
    return {'path': p.as_posix(), 'bytes': len(b), 'sha256': hashlib.sha256(b).hexdigest()}

entries = []
for version, sha in [('001', '84ffc500ef95a745ad13452169d8ed8047a832a59977b28395d07c36250131dd'),
                     ('002', '51058cb8508debaeb0bed9518db2a25d2fde9295fad778286371a94759628c90')]:
    source = R / f'过程图稿与视频/2026-10-16_钟盔军剑第二段真实连击试装_v{version}'
    video = source / '展示副本/fairytale-sword-primary2-fit-silent.mp4'
    assert desc(video)['sha256'] == sha
    target = A / f'展示副本/primary2-arc-v{version}-native-silent.mp4'
    shutil.copy2(video, target)
    assert desc(target)['sha256'] == sha
    entries.append({'source': desc(video), 'copy': desc(target), 'resampled': False, 'retimed': False})
    p = source / 'index.json'
    q = A / f'原件/capture-v{version}-index.json'
    shutil.copy2(p, q)
    entries.append({'source': desc(p), 'copy': desc(q)})

source = R / '过程图稿与视频/2026-10-16_钟盔军剑第二段真实连击试装_v002/展示副本'
for name, target_name in [('crop-23-MovieFrame00053.png', 'low-windup.png'),
                          ('crop-24-MovieFrame00055.png', 'low-cut.png'),
                          ('crop-25-MovieFrame00057.png', 'high-cut.png')]:
    p, q = source / name, A / '展示副本' / target_name
    shutil.copy2(p, q)
    assert desc(p)['sha256'] == desc(q)['sha256']
    entries.append({'source': desc(p), 'copy': desc(q), 'resampled': False})

html = '''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>钟盔军剑 · 第二段连击试装</title>
<style>body{margin:24px;background:#141b21;color:#edf0df;font:16px system-ui}video{display:block;width:1280px;max-width:100%;background:#000}button{margin:16px 8px 16px 0;padding:10px 20px}p{max-width:1000px;line-height:1.65}.crops{display:flex;gap:16px;flex-wrap:wrap}figure{margin:12px 0}figure img{display:block;width:240px;height:150px}figcaption{margin-top:8px;font-size:14px;color:#c0c5bc}</style>
<h1>钟盔军剑：第二段上挑试装</h1><p>UE5真实按键录像，左右各一组连续出招。人物身体最高72px、游戏UI隐藏；第二段从低位抬剑上斩，第一段直接衔接第二段。</p>
<video id="v" controls preload="auto" src="展示副本/primary2-arc-v002-native-silent.mp4"></video>
<button onclick="v.currentTime=0;v.play()">新版从头播放</button><button onclick="v.pause()">暂停</button>
<button onclick="v.src='展示副本/primary2-arc-v001-native-silent.mp4';v.load();v.play()">查看上一版</button>
<button onclick="v.src='展示副本/primary2-arc-v002-native-silent.mp4';v.load();v.play()">切回新版</button>
<p>这是动作试装：第二段胸肩甲尚未接入，抬剑与头盔下沿、握剑和脚步仍在打磨；第三段及其他状态继续制作。录像无声。</p>
<div class="crops"><figure><img src="展示副本/low-windup.png"><figcaption>低位起手</figcaption></figure><figure><img src="展示副本/low-cut.png"><figcaption>向前切入</figcaption></figure><figure><img src="展示副本/high-cut.png"><figcaption>向上斩出 · 原生裁图未放大</figcaption></figure></div></html>'''
(A / 'review-player.html').write_text(html, encoding='utf-8')
(A / 'index.json').write_text(json.dumps({'sources': entries, 'status': 'native captures and 32 crops reviewed; continuous player review pending',
    'source_snapshots': {'old': 'v108', 'new': 'v110'}, 'new_pristine_tests_at_capture': '3 failed / 6 errors / 0 warnings',
    'not_full_suite_green': True, 'formal_complete_units': 0, 'native_generation_calls': 0,
    'armor_primary2_present': False, 'audio_recorded': False}, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
(A / 'README.md').write_text('两版军剑第二段真实UE实录与原生裁图，按字节复制。新版连续输入及上挑角度候选，第二段胸肩甲与完整动作未完成；录像静音，非正式内容验收。原件、展示副本、source/version/status索引保留，旧版不覆盖。\n', encoding='utf-8')
print(json.dumps({'archive': A.as_posix(), 'copied_media': len(entries), 'playback_review_pending': True}, ensure_ascii=False))
