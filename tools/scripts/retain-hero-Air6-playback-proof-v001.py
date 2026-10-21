from pathlib import Path
import hashlib,json,shutil
R=Path('F:/Ourgame');M=R/'过程图稿与视频/2026-10-19_钟盔跳跃缺口完整播放证明_v001'
def pin(p):return dict(path=p.as_posix(),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())
state=M/'原件/browser-playback-end-state.txt';screen=M/'原件/browser-playback-ended.png';text=state.read_text(encoding='utf-8');assert text.count('"ended": true')==2 and text.count('"playbackRate": 1')==2 and text.count('"loop": false')==2 and text.count('"error": null')==2
shutil.copy2(screen,M/'展示副本'/screen.name)
shutil.copy2(Path(__file__),M/'原件'/Path(__file__).name)
(M/'source-version-status-index.json').write_text(json.dumps(dict(schema='Root-Air6-baseline-full-browser-playback-proof-v001',browser='ChatGPT IAB2/tab5',url='http://127.0.0.1:56250/player.html',player_media='F:/Ourgame/过程图稿与视频/2026-10-19_钟盔跳跃缺口双侧播放器_v001',left=dict(native_frames=158,duration=2.304,ended=True),right=dict(native_frames=165,duration=2.320347,ended=True),playbackRate=1,loop=False,muted=False,errors=None,actual_browser_playback_to_end=True,Root_source_and_six_phase_boards_reviewed=True,all_video_frames_individually_visually_reviewed=False,audio_audition_accepted=False,new_Air_art_accepted=False,formal_complete_units=0,files=[pin(p) for p in sorted(M.rglob('*')) if p.is_file()]),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(M/'README.md').write_text('Root实际操作浏览器左/右播放按钮，1倍速无循环到ended；保留实际AX终态和截图。原158/165帧已全部解码，六相原生采样板已审。不是逐帧全视觉/声音听感、新Air美术或完整内容单元验收。截图E保全后才View。\n',encoding='utf-8')
print(json.dumps(dict(archive=M.as_posix(),files=sum(p.is_file() for p in M.rglob('*'))),ensure_ascii=False))
