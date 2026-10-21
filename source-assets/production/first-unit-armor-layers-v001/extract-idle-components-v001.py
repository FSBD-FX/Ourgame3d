"""Manual visible-surface selections from native sources; never paints new art."""
from pathlib import Path
import importlib.util
from PIL import Image,ImageDraw
P=Path(__file__).resolve().parent
OLD=P.parent/'first-unit-animation-v003'
s=importlib.util.spec_from_file_location('record',P/'production-record.py')
r=importlib.util.module_from_spec(s);s.loader.exec_module(r)

# Coordinates are manually traced on the actual 512px sources, not generated anatomy.
POLYGONS={
 'clothing_replace':[(143,279),(148,265),(160,254),(172,247),(190,248),(208,253),(227,259),(252,259),(277,257),(292,263),(300,274),(309,295),(309,315),(296,323),(290,339),(304,383),(290,397),(176,393),(174,377),(183,357),(198,345),(192,325),(165,318),(141,307)],
 'head_preserve':[(166,193),(175,153),(202,130),(237,123),(264,132),(290,151),(300,182),(299,219),(296,241),(286,259),(247,260),(210,250),(175,241),(167,221)],
 'near_forearm_hand':[(147,300),(160,303),(171,309),(187,316),(199,323),(205,338),(202,352),(192,365),(173,366),(163,359),(153,343),(144,329),(140,315)],
 'far_wrist_hand_preserve':[(301,327),(317,337),(330,350),(340,365),(337,376),(323,383),(309,377),(301,365),(295,347)],
 'belt_preserve':[(197,328),(289,326),(294,347),(229,353),(204,351),(193,344)],
 'pouch_preserve':[(192,332),(228,333),(234,346),(225,370),(213,375),(186,369),(186,350)],
 'armor_near_shoulder':[(150,276),(154,267),(169,252),(194,248),(211,262),(207,280),(194,292),(164,290),(148,286)],
 'armor_far_shoulder':[(281,257),(292,256),(303,264),(309,276),(300,290),(290,287),(284,275)],
 'armor_torso':[(207,254),(228,260),(272,258),(290,264),(300,280),(297,318),(291,337),(206,336),(193,321),(196,296),(208,280)],
 'armor_front_hem':[(202,344),(283,345),(298,360),(304,389),(265,396),(251,385),(242,396),(177,390),(180,377),(190,359)],
 'armor_back_hem_fragment':[(173,366),(184,357),(195,362),(198,390),(187,394),(173,387)],
}
SHIFTS=[(0,0),(0,-1),(0,0),(0,1),(0,1),(1,1)]

def mask(name,shift):
 q=Image.new('L',(512,512),0);ImageDraw.Draw(q).polygon([(x+shift[0],y+shift[1]) for x,y in POLYGONS[name]],fill=255);return q

def extract(source,selection):
 out=Image.new('RGBA',(512,512),(0,0,0,0));out.paste(source,(0,0),selection)
 # Canonical transparent RGB; all visible color is byte-identical to source.
 px=out.load()
 for y in range(512):
  for x in range(512):
   if px[x,y][3]==0:px[x,y]=(0,0,0,0)
 return out

def main():
 out=P/'components/idle-selection-v001'
 if out.exists() and any(out.iterdir()):raise ValueError('Do not overwrite selection source')
 out.mkdir(exist_ok=True);rows=[];sheets={name:Image.new('RGBA',(1536,1024),(0,0,0,0)) for name in ['base_common','body_far','body_near','armor_back','armor_far_shoulder','armor_torso','armor_front']}
 for i,shift in enumerate(SHIFTS):
  frozen=OLD/f'processed/round-knight-idle-body-v003/idle-{i+1}.png'
  orig=Image.open(frozen).convert('RGBA');common=Image.open(P/f'processed/call45-fixed-canvas-v002/frame-{i}.png').convert('RGBA')
  armored=Image.open(P/f'processed/call48-fixed-canvas-v002/frame-{i}.png').convert('RGBA')
  masks={name:mask(name,shift) for name in POLYGONS}
  preserve=['head_preserve','near_forearm_hand','far_wrist_hand_preserve','belt_preserve','pouch_preserve']
  cloth=masks['clothing_replace'].copy();pix=cloth.load()
  for q in preserve:
   for y in range(512):
    for x in range(512):
     if masks[q].getpixel((x,y)):pix[x,y]=0
  base=orig.copy();base.paste(common,(0,0),cloth)
  base=extract(base,Image.new('L',(512,512),255)) # zero invisible RGB only
  near=extract(base,masks['near_forearm_hand']);complement=masks['near_forearm_hand'].point(lambda x:255-x);far=extract(base,complement)
  reconstructed=far.copy();reconstructed.alpha_composite(near)
  assert reconstructed.tobytes()==base.tobytes()
  # Preserve the entire frozen hand/wrist selection, not merely a socket point.
  for q in ['head_preserve','near_forearm_hand','far_wrist_hand_preserve']:
   assert extract(base,masks[q]).tobytes()==extract(orig,masks[q]).tobytes()
  arm_masks={}
  for name in ['armor_back','armor_far_shoulder','armor_torso','armor_front']:
   source_names={'armor_back':['armor_back_hem_fragment'],'armor_far_shoulder':['armor_far_shoulder'],
    'armor_torso':['armor_torso'],'armor_front':['armor_near_shoulder','armor_front_hem']}[name]
   q=Image.new('L',(512,512),0);draw=ImageDraw.Draw(q)
   for source_name in source_names:draw.polygon([(x+shift[0],y+shift[1]) for x,y in POLYGONS[source_name]],fill=255)
   # Real armor surfaces may not include the original head/skin/hands/belt/pouch.
   px=q.load()
   for y in range(512):
    for x in range(512):
     if any(masks[k].getpixel((x,y)) for k in preserve):px[x,y]=0
   arm_masks[name]=q
  # Assign overlap exactly once, in visual front-to-back priority.
  taken=Image.new('L',(512,512),0)
  for name in ['armor_front','armor_torso','armor_far_shoulder','armor_back']:
   q=arm_masks[name];px=q.load();used=taken.load()
   for y in range(512):
    for x in range(512):
     if used[x,y]:px[x,y]=0
     elif px[x,y]:used[x,y]=255
  parts={'base_common':base,'body_far':far,'body_near':near}
  parts.update({name:extract(armored,q) for name,q in arm_masks.items()})
  paths={};mask_paths={}
  for name,image in parts.items():
   f=out/f'{name}-{i}.png';image.save(f);r.archive(f,Path('components')/out.name/f.name,'actual_native_pixel_selection_candidate_not_semantic_or_runtime_pass')
   paths[name]={'path':str(f),'sha256':r.sha(f),'bbox':list(image.getchannel('A').getbbox()) if image.getchannel('A').getbbox() else None}
   sheets[name].alpha_composite(image,((i%3)*512,(i//3)*512))
  for name,q in dict(clothing_replace=cloth,body_near=masks['near_forearm_hand'],**arm_masks).items():
   f=P/f'masks/idle-{name}-{i}-v001.png';q.save(f);r.archive(f,Path('masks')/f.name,'binary_manual_visible_surface_selection_mask_not_raw_art');mask_paths[name]={'path':str(f),'sha256':r.sha(f)}
  rows.append({'index':i,'parts':paths,'masks':mask_paths,'source_frozen':str(frozen),'source_frozen_sha256':r.sha(frozen),
   'source_common':str(P/f'processed/call45-fixed-canvas-v002/frame-{i}.png'),
   'source_armored':str(P/f'processed/call48-fixed-canvas-v002/frame-{i}.png'),
   'body_near_far_reconstruct_exactly':True,'frozen_head_and_hands_preserved_exactly':True})
 for name,sheet in sheets.items():
  f=P/f'reviews/idle-{name}-selection-v001.png';sheet.save(f);r.archive(f,Path('reviews')/f.name,'selected_layer_isolated_review_pending')
 report={'schema':'manual_visible_component_selection_v1','frames':rows,'polygons':POLYGONS,'per_frame_manual_shifts':SHIFTS,
  'all_layers_canvas':[512,512],'source_frame_transforms':'none','new_raw_art_created_by_code':False,
  'selection_operation':'binary_masks_select_existing_generated_pixels_only_no_paint_or_fill',
  'back_layer_scope':'visible_far_side_hem_fragment_only_not_invented_hidden_back',
  'body_near_scope':'actually_visible_near_forearm_wrap_hand_not_complete_hidden_arm',
  'semantic_layer_review_passed':False,'runtime_verified':False,'armor_complete':False}
 q=P/'manifests/idle-component-selection-v001.json';r.write(q,report);r.archive(q,Path('manifests')/q.name,'manual_component_source_and_reconstruction_evidence_pending_review')
 print({'frames':6,'body_exact_reconstruction':True,'source_hands_preserved':True,'semantic_review_pending':True})

if __name__=='__main__':main()
