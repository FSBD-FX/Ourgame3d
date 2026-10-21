"""Index both complete browser playbacks before E retention and viewing screenshots."""
from pathlib import Path
import hashlib,json,shutil
R=Path('F:/Ourgame');D=R/'过程图稿与视频/2026-10-18_钟盔倒地实录播放审阅_v001'
M=R/'过程图稿与视频/2026-10-18_钟盔倒地五相左右实录审阅_v001'
def pin(p):return dict(path=p.as_posix(),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())
rows=[]
for side in ['left','right']:
 p=D/'原件'/(side+'-playback.json');v=json.loads(p.read_text(encoding='utf-8'))
 assert v['ended'] and v['paused'] and v['error'] is None and v['loop'] is False and v['readyState']==4 and v['currentTime']==v['duration']
 im=D/'原件'/(side+'-ended.png');dest=D/'展示副本'/im.name;assert not dest.exists();shutil.copy2(im,dest)
 rows.append(dict(side=side,playback=pin(p),screenshot=pin(im),presentation=pin(dest),source_video=pin(M/side/'展示副本/hero-Death5-native-DIAGNOSTIC-silent-v001.mp4'),observed=v))
index=dict(schema='HeroDeath138-two-complete-browser-playbacks-v001',source_version='v138-HeroDeath190G',rows=rows,
 full_playbacks_observed=True,source_video_audio=False,Root_view_screenshots_after_E=True,
 review='Both five-phase original source witnesses and adjacent Ready-stack/Death0 pairs reviewed. Player gear is retained and corpse final phase readable. Guard Stomp still visibly switches to gray geometric placeholder; not a complete enemy art acceptance.',
 formal_complete_units=0,FinalAccepted=False)
for name in ['index.json','source-version-status-index.json']:
 p=D/name;assert not p.exists();p.write_text(json.dumps(index,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(D/'README.md').write_text('两侧完整静音视频已在浏览器播放到ended，loop=false/error=null。图像截取后先F保存，E双SHA保全后再View。守卫跺击仍几何占位；玩家倒地有限状态已审，完整内容单元未验收。\n',encoding='utf-8')
print(json.dumps(dict(full_playbacks=2,left_duration=rows[0]['observed']['duration'],right_duration=rows[1]['observed']['duration'],E_before_View_pending=True)))
