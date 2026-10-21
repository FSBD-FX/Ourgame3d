"""Create a new local player from the complete, verified native AV copies."""
from pathlib import Path
import argparse
import hashlib
import json
import shutil

ROOT = Path('F:/Ourgame')


def pin(p):
    p = p.resolve()
    b = p.read_bytes()
    return dict(path=p.as_posix(), bytes=len(b), sha256=hashlib.sha256(b).hexdigest())


ap = argparse.ArgumentParser()
ap.add_argument('--left-presentation', required=True)
ap.add_argument('--right-presentation', required=True)
ap.add_argument('--output-name', required=True)
a = ap.parse_args()
out = ROOT / '过程图稿与视频' / a.output_name
assert out.parent == ROOT / '过程图稿与视频' and not out.exists()
(out / '原件').mkdir(parents=True)
(out / '展示副本').mkdir()
rows = []
for side, path, facing in [('left', a.left_presentation, -1), ('right', a.right_presentation, 1)]:
    source = Path(path).resolve()
    index = json.loads((source / '来源-版本-状态索引.json').read_text(encoding='utf-8-sig'))
    assert index['actual_facing'] == facing and index['native_bindings']['official_readonly_recheck_passed'] is True
    video = source / '展示副本/hero-Air6-production-full-native-mix-DIAGNOSTIC-v001.mp4'
    assert video.is_file()
    copies = []
    for folder in ['原件', '展示副本']:
        dest = out / folder / (side + '.mp4')
        shutil.copy2(video, dest)
        assert pin(video)['sha256'] == pin(dest)['sha256']
        copies.append(pin(dest))
    rows.append(dict(side=side, source=pin(video), source_index=pin(source / '来源-版本-状态索引.json'), exact_copies=copies))

html = '''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>钟盔冒险者 · 三次跳跃实录</title>
<style>body{background:#15171b;color:#eee;font:16px system-ui;margin:24px auto;max-width:1280px;padding:0 20px}h1{font-size:25px}p,small{color:#b8bec8}button{padding:11px 18px;margin:8px 12px 16px 0;background:#303841;color:#fff;border:1px solid #66717d;border-radius:6px;cursor:pointer}video{display:block;width:100%;max-width:1280px;background:#000}section[hidden]{display:none}pre{font:12px monospace;color:#aeb7c2;white-space:pre-wrap}</style>
<h1>钟盔冒险者 · 三次跳跃实录</h1><p>真实游戏录制：无甲跳跃 → 穿轻甲 → 落地再跳。保留原生混音，动作衔接仍在审阅。</p>
<button id="left-play" onclick="playOne('left')">完整播放左朝向</button><button id="right-play" onclick="playOne('right')">完整播放右朝向</button>
<section id="left-section"><video id="left" controls preload="metadata" playsinline src="left.mp4"></video></section>
<section id="right-section" hidden><video id="right" controls preload="metadata" playsinline src="right.mp4"></video></section>
<p>1倍速，无循环。原始1280×720画面与完整PCM留档；首次失败版本另存。</p><small>此段使用正常键盘输入的自动录制；前置石像骑士通过明确的诊断伤害清理。不是整房通关或完整音效验收。</small><pre id="status">等待完整播放</pre>
<script>function status(){document.querySelector('#status').textContent=JSON.stringify([...document.querySelectorAll('video')].map(v=>({id:v.id,currentTime:v.currentTime,duration:v.duration,ended:v.ended,paused:v.paused,playbackRate:v.playbackRate,loop:v.loop,muted:v.muted,error:v.error?.message??null})),null,2)}function playOne(id){for(const v of document.querySelectorAll('video'))v.pause();for(const s of document.querySelectorAll('section'))s.hidden=s.id!==id+'-section';const v=document.getElementById(id);v.currentTime=0;v.playbackRate=1;v.loop=false;v.muted=false;v.play().catch(e=>document.querySelector('#status').textContent=e.message)}for(const v of document.querySelectorAll('video'))for(const e of ['loadedmetadata','timeupdate','play','ended','error'])v.addEventListener(e,status);</script></html>'''
for folder in ['原件', '展示副本']:
    (out / folder / 'player.html').write_text(html, encoding='utf-8')
shutil.copy2(Path(__file__), out / '原件' / Path(__file__).name)
index = dict(schema='Root-Air6-production-local-player-v002', status='Verified complete AV copied exactly; E retention and actual playback pending',
             videos=rows, player_files=[pin(out / f / 'player.html') for f in ['原件', '展示副本']],
             published=False, visual_reviewed=False, audio_listened=False, formal_complete_units=0, FinalAccepted=False)
(out / 'source-version-status-index.json').write_text(json.dumps(index, ensure_ascii=False, indent=2), encoding='utf-8')
(out / 'README.md').write_text('左右完整原生视听文件逐字节复制的本机播放器。先E双SHA保全，再实际原速播放审阅。无上传、正式内容完成或音效听感通过声明。\n', encoding='utf-8')
print(json.dumps(dict(media=out.as_posix(), videos=2), ensure_ascii=False))
