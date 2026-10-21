from pathlib import Path
import importlib.util
from PIL import Image,ImageDraw
P=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('record',P/'production-record.py');r=importlib.util.module_from_spec(s);s.loader.exec_module(r)
sheet=Image.open(P/'reviews/XBW-reload-four-keyposes-assembled_right-v001.png').convert('RGBA')
canvas=Image.new('RGB',(1024,576),(35,41,45));d=ImageDraw.Draw(canvas)
for i in range(4):
 cell=sheet.crop((i%2*512,i//2*512,i%2*512+512,i//2*512+512));crop=cell.crop((196,242,396,354)).resize((512,286),Image.Resampling.NEAREST)
 canvas.paste(crop,(i%2*512,i//2*288),crop);d.text((i%2*512+3,i//2*288+3),f'KEY{i} actual composed source pixels 2.56x',fill='white')
q=P/'reviews/XBW-reload-actual-contact-crops-v001.png';assert not q.exists();canvas.save(q);r.archive(q,q.relative_to(P),'actual_four_keypose_contact_crops_not_new_art_or_engine_capture')
canvas=Image.new('RGB',(640,672),(35,41,45));d=ImageDraw.Draw(canvas)
for i in range(4):
 im=Image.open(P/f'processed/call91-four-body-keyposes-v001/body-{i}.png').convert('RGBA');box=[(260,250,360,310),(168,250,268,310),(210,250,310,310),(170,286,270,346)][i]
 crop=im.crop(box).resize((400,240),Image.Resampling.NEAREST);ox=i%2*320;oy=i//2*336
 # Crops are displayed at3x to fit the page, retaining nearest-neighbor actual pixels.
 crop=im.crop(box).resize((300,180),Image.Resampling.NEAREST);canvas.paste(crop,(ox,oy+32),crop)
 for xx in range(box[0],box[2],10):d.line((ox+(xx-box[0])*3,oy+32,ox+(xx-box[0])*3,oy+211),fill=(55,65,65));d.text((ox+(xx-box[0])*3+1,oy+33),str(xx),fill='white')
 for yy in range(box[1],box[3],10):d.line((ox,oy+32+(yy-box[1])*3,ox+299,oy+32+(yy-box[1])*3),fill=(55,65,65));d.text((ox+1,oy+33+(yy-box[1])*3),str(yy),fill='white')
 d.text((ox+3,oy+3),f'KEY{i} actual near hand/cuff',fill='white')
q=P/'reviews/XBW-reload-near-hand-boundary-crops-v001.png';assert not q.exists();canvas.save(q);r.archive(q,q.relative_to(P),'actual_body_near_hand_boundary_measurement_not_new_pose_art')
