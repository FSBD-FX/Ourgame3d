"""Correct visually inspected airborne belt/fist points; retain v004 evidence."""
from pathlib import Path
import importlib.util
from PIL import Image, ImageDraw
P=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('record',P/'production-record.py')
r=importlib.util.module_from_spec(s);s.loader.exec_module(r)

def main():
 out=P/'reviews/manual-state-grip-measurements-v005.json'
 if out.exists():raise ValueError('Do not overwrite measurements')
 d=r.read(P/'reviews/manual-state-grip-measurements-v004.json')
 d.update(version=5,previous_measurements=str(P/'reviews/manual-state-grip-measurements-v004.json'),
  revision_reason='Actual single-frame review corrected air4/5/6 belt proxies and air5/6 fist centers; pixels unchanged',
  diagnostic_review_status='crosses_on_actual_near_fists_all30_manually_viewed')
 air=next(a for a in d['actions'] if a['action']=='air-primary1')
 belts=[(262,306),(260,311),(272,307),(253,305),(270,309),(257,304)]
 air['frames'][4]['grip_px']=[246,337];air['frames'][5]['grip_px']=[237,323]
 for i,f in enumerate(air['frames']):
  f.update(belt_proxy_px=list(belts[i]),root_px=[belts[i][0]-5,belts[i][1]+132])
 for action in d['actions']:
  sheet=Image.new('RGBA',(1536,1024),(238,230,214,255))
  for f in action['frames']:
   im=Image.open(f['frame_path']).convert('RGBA');draw=ImageDraw.Draw(im);x,y=f['grip_px']
   draw.line((x-10,y,x+10,y),fill=(255,0,0,255),width=2);draw.line((x,y-10,x,y+10),fill=(255,0,0,255),width=2)
   if 'belt_proxy_px' in f:
    bx,by=f['belt_proxy_px'];rx,ry=f['root_px']
    draw.ellipse((bx-4,by-4,bx+4,by+4),outline=(0,170,255,255),width=2)
    draw.line((rx-12,ry,rx+12,ry),fill=(0,110,255,255),width=3)
   f['measurement_status']='manual_processed_pixel_measurement_corrected_and_reviewed_pending_runtime'
   i=f['frame_index'];sheet.alpha_composite(im,((i%3)*512,(i//3)*512))
  q=P/f"reviews/{action['action']}-grip-diagnostic-v005.png";sheet.save(q)
  r.archive(q,Path('reviews')/q.name,'corrected_manual_coordinate_diagnostic_not_runtime')
  action['diagnostic']=str(q)
 r.write(out,d);r.archive(out,Path('reviews')/out.name,'corrected_manual_measurements_runtime_pending')
 print({'path':str(out),'sha256':r.sha(out)})

if __name__=='__main__':main()
