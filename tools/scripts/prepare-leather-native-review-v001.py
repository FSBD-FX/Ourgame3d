from pathlib import Path
import hashlib,json,shutil
from PIL import Image,ImageDraw
R=Path('F:/Ourgame');B=R/'过程图稿与视频/2026-10-17_软皮轻甲左右待机试装_v001';A=R/'过程图稿与视频/2026-10-17_软皮轻甲实景播放复核_v001';assert not A.exists()
(A/'原件').mkdir(parents=True);(A/'展示副本').mkdir();rows=[]
def desc(p):
 b=p.read_bytes();return dict(path=p.as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def copy(p,q):
 shutil.copy2(p,q);assert p.read_bytes()==q.read_bytes();rows.append(dict(source=desc(p),copy=desc(q),resampled=False))
sheet=Image.new('RGB',(960,360),(29,32,37));draw=ImageDraw.Draw(sheet)
for j,side in enumerate(['left','right']):
 for i in range(4):
  matches=list((B/'展示副本').glob(f'leather-ready-{side}-frame-{i}-*.png'));assert len(matches)==1;p=matches[0]
  q=A/'原件'/p.name;copy(p,q)
  im=Image.open(p).convert('RGB');assert im.size==(240,160);sheet.paste(im,(i*240,j*180+20));draw.text((i*240+6,j*180+4),f'{side} / actual Ready {i} / 1:1 crop',fill=(235,231,213))
sheet.save(A/'展示副本/native-ready-eight-frames-unscaled.png')
copy(B/'原件/MovieFrame00055.png',A/'展示副本/native-ready-right-whole.png')
copy(B/'展示副本/leather-ready-right-frame-0-MovieFrame00055.png',A/'展示副本/native-ready-right-crop.png')
copy(B/'展示副本/leather-ready-left-frame-0-MovieFrame00036.png',A/'展示副本/native-ready-left-crop.png')
copy(B/'展示副本/leather-ready-trial-silent.mp4',A/'展示副本/leather-ready-trial-silent.mp4')
for name in ['runtime-report.json','leather-ready-source-binding-verification-v001.json','independent-leather-ready-verification-v001.json','leather-ready-selected-source-map-v001.json','leather-ready-video-receipt-v001.json']:
 copy(B/'原件'/name,A/'原件'/name)
(A/'source-version-status-index.json').write_text(json.dumps(dict(type='actual native trial review copies and exact-pixel contact sheet',copies=rows,snapshot='v124',native_scope='Ready4 both facings only, one genuine light commit from QA source',audio_recorded=False,browser_playback='pending',art_review='pending all-eight native review; two Ready0 directions and whole scene viewed after E280; final full motion remains NEEDS_WORK',formal_complete_units=0),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(A/'README.md').write_text('只读复制已E280留存的实际UE静音试穿。八格表逐像素粘贴原240x160裁图，不放大/重采样/改色。整景1280x720原件、视频、源映射和检查报告逐字节保持。Root浏览器截图/播放结果另存原件，E281后才查看新展示。Ready之外动作及整套装备未完成。\n',encoding='utf-8')
print(json.dumps(dict(review_archive=A.as_posix(),copies=len(rows),new_contact_sheet_needs_E_before_view=True),ensure_ascii=False))
