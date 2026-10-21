"""Append legible nonoverlapping diagnostic crops; keep v001 board and index."""
from pathlib import Path
import argparse,hashlib,json
from PIL import Image,ImageDraw,ImageFont
R=Path('F:/Ourgame');ap=argparse.ArgumentParser();ap.add_argument('--side',choices=['left','right'],required=True);a=ap.parse_args()
M=R/f'过程图稿与视频/2026-10-19_钟盔跳跃旧渲染缺口实录_{a.side}_v001';D=M/'展示副本';idx=M/'source-version-status-index.json';q=json.loads(idx.read_text(encoding='utf-8'))
p=D/'six-native-physical-phases-CROPPED-diagnostic-v002.png';assert not p.exists()
board=Image.new('RGB',(1536,740),(45,48,54));draw=ImageDraw.Draw(board);font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',18)
for k,s in enumerate(q['samples']):
 x=s['observation'];g=x['ground'];c=x['camera_ground'];sx=round(640+(g[0]-c[0])*.65);sy=490
 box=(max(0,sx-110),sy-240,min(1280,sx+110),sy+80);crop=Image.open(s['source']['path']).crop(box);col=k%3;row=k//3;board.paste(crop,(col*512+140,row*370+35))
 draw.text((col*512+8,row*370+7),f"phase{s['phase']} H{x['jump_height']:.2f} V{x['vertical_velocity']:.1f} age{x['landing_visual_age']:.3f}",font=font,fill='white')
board.save(p)
def pin(p):return dict(path=p.as_posix(),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())
rec=M/'diagnostic-board-append-v002.json';assert not rec.exists();rec.write_text(json.dumps(dict(schema='Root-Air6-baseline-diagnostic-board-v002',new=pin(p),original_index=pin(idx),old_board_preserved=True,reason='v001 canvas530 tall let320-high crops overlap265 row pitch. v002 row370 and canvas740 retains disjoint original crops.',pixel_resized=False,source_pixels_changed=False,viewed=False),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(board=pin(p),viewed=False),ensure_ascii=False))
