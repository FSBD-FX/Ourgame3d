"""Preserve manually chosen points on real sprites; diagnostics are not asset art."""
from pathlib import Path
import importlib.util
from PIL import Image, ImageDraw

P = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('record', P/'production-record.py')
r = importlib.util.module_from_spec(spec); spec.loader.exec_module(r)
CONFIG = [
 ('hurt',31,'hurt',[(176,345),(183,345),(171,357),(184,340),(180,343),(177,340)],[35]*6),
 ('dodge',32,'dodge',[(184,363),(179,366),(179,380),(146,336),(188,342),(182,358)],[20,20,10,0,20,20]),
 ('secondary',35,'attack',[(149,232),(141,187),(270,353),(333,386),(129,231),(162,270)],[-130,-60,25,25,-110,-70]),
 ('air-primary1',36,'attack',[(174,155),(205,108),(329,251),(332,336),(250,323),(237,327)],[-125,-25,20,25,25,-35]),
 ('equip',37,'idle',[(186,344),(181,344),(182,344),(186,343),(181,341),(184,344)],[35]*6),
]
BELTS = [(262,306),(260,311),(272,307),(269,288),(273,301),(288,292)]

def main():
 out=P/'reviews/manual-state-grip-measurements-v004.json'
 if out.exists():raise ValueError('Frozen manual measurement; use new version')
 data={'schema':'manual-sprite-point-measurements-v1','version':4,
  'measurement_method':'human_visual_coordinates_on_processed_512px_frames_not_inferred_from_prompt',
  'measurement_precision_px':3,'runtime_verified':False,
  'reference_idle_belt_center_px':[261,340],'reference_ground_root_px':[256,472],
  'belt_to_virtual_ground_offset_px':[-5,132],
  'virtual_root_limit':'belt proxy preserves torso placement; actorZ alone supplies jump height; not a recovered physical skeleton',
  'actions':[]}
 for slug,request,prefix,points,angles in CONFIG:
  folder=P/f'processed/round-knight-{slug}-body-v003'
  sheet=Image.new('RGBA',(1536,1024),(238,230,214,255)); frames=[]
  for i,(point,angle) in enumerate(zip(points,angles)):
   f=folder/f'{prefix}-{i+1}.png';im=Image.open(f).convert('RGBA')
   d=ImageDraw.Draw(im);x,y=point
   d.line((x-10,y,x+10,y),fill=(255,0,0,255),width=2)
   d.line((x,y-10,x,y+10),fill=(255,0,0,255),width=2)
   d.text((8,8),f'{slug} {i+1} grip {point} angle {angle}',fill=(30,30,30,255))
   item={'frame_index':i,'frame_path':str(f),'frame_sha256':r.sha(f),'grip_px':list(point),
         'weapon_angle_image_clockwise_deg':angle,'weapon_scale':.4,
         'measurement_status':'manual_visual_coordinate_pending_diagnostic_review'}
   if slug=='air-primary1':
    b=BELTS[i];root=[b[0]-5,b[1]+132]
    item.update(belt_proxy_px=list(b),root_px=root,root_kind='virtual_ground_proxy')
    d.ellipse((b[0]-4,b[1]-4,b[0]+4,b[1]+4),outline=(0,170,255,255),width=2)
    d.line((root[0]-12,root[1],root[0]+12,root[1]),fill=(0,110,255,255),width=3)
   else:item.update(root_px=[256,472],root_kind='grounded_profile_contact_estimate')
   sheet.alpha_composite(im,((i%3)*512,(i//3)*512));frames.append(item)
  diagnostic=P/f'reviews/{slug}-grip-diagnostic-v004.png';sheet.save(diagnostic)
  r.archive(diagnostic,Path('reviews')/diagnostic.name,'manual_coordinate_diagnostic_not_runtime_asset')
  data['actions'].append({'action':slug,'source_request_number':request,'frames':frames,'diagnostic':str(diagnostic)})
 r.write(out,data);r.archive(out,Path('reviews')/out.name,'manual_coordinate_measurements_pending_visual_review')
 print({'path':str(out),'sha256':r.sha(out),'source_frames':30})

if __name__=='__main__':main()
