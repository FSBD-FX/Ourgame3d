"""Manually traced actual native garment surfaces over frozen XBW bodies, never paint."""
from pathlib import Path
import importlib.util,json,math
from PIL import Image,ImageDraw,ImageChops
P=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('record',P/'production-record.py');w=importlib.util.module_from_spec(s);s.loader.exec_module(w);r=w.r
B=P.parent/'first-batch-weapon-actions-v001'
HEADS=[[(165,123),(239,123),(272,140),(292,167),(301,199),(301,228),(288,250),(269,260),(235,262),(198,249),(175,240),(165,219),(161,188),(162,153)],
[(166,123),(241,123),(275,141),(294,168),(303,199),(303,229),(289,251),(270,261),(237,262),(201,249),(177,239),(165,218),(162,187),(163,153)],
[(159,126),(237,126),(271,143),(291,170),(299,201),(300,231),(286,253),(266,263),(232,264),(195,250),(172,242),(160,222),(156,190),(157,156)],
[(161,116),(235,116),(269,133),(287,160),(294,193),(294,222),(280,245),(260,255),(226,255),(191,242),(169,233),(159,211),(156,180),(158,146)],
[(171,116),(245,116),(279,134),(296,161),(303,193),(304,223),(289,245),(270,255),(235,256),(200,243),(177,233),(167,211),(164,180),(166,146)],
[(165,122),(239,122),(273,140),(293,167),(301,199),(301,229),(287,251),(267,262),(233,263),(198,249),(175,240),(165,219),(161,188),(162,153)]]
# Near garment is real shoulder/sleeve. Distal fist/wrist pixels remain the frozen body track.
NEAR_SLEEVES=[[(146,245),(179,240),(205,254),(219,276),(220,302),(214,343),(184,344),(156,322),(146,296)],
[(151,237),(178,232),(203,242),(224,249),(237,278),(216,292),(190,297),(157,283),(150,263)],
[(147,239),(176,235),(201,244),(226,252),(239,281),(221,298),(191,304),(156,291),(147,268)],
[(147,231),(173,228),(199,235),(221,247),(233,277),(214,296),(188,299),(155,284),(146,260)],
[(151,241),(179,237),(205,250),(226,270),(233,307),(212,334),(180,329),(153,312),(145,286)],
[(146,245),(179,240),(205,254),(219,276),(220,302),(214,343),(184,344),(156,322),(146,296)]]
BARE_PATCHES=[[(154,289),(183,291),(192,306),(185,322),(164,318),(153,309)],
[(161,266),(184,270),(193,282),(183,294),(164,287)],
[(158,270),(182,273),(193,289),(182,302),(161,293)],
[(154,264),(180,269),(191,284),(180,297),(157,287)],
[(155,287),(180,289),(188,305),(181,318),(159,310)],
[(154,289),(183,291),(192,306),(185,322),(164,318),(153,309)]]
def poly(points):
 im=Image.new('L',(512,512),0);ImageDraw.Draw(im).polygon(points,fill=255);return im
def union(polygons):
 im=Image.new('L',(512,512),0)
 for p in polygons:im=ImageChops.lighter(im,poly(p))
 return im
def extract(source,mask):
 out=source.copy();out.putalpha(ImageChops.multiply(source.getchannel('A'),mask));out.putdata([p if p[3] else(0,0,0,0) for p in out.get_flattened_data()]);return out
def save(im,q,status):
 assert not q.exists();q.parent.mkdir(parents=True,exist_ok=True);im.save(q);r.archive(q,q.relative_to(P),status)
 return {'path':str(q),'sha256':r.sha(q),'canvas_px':list(im.size),'mode':im.mode,'alpha_extrema':list(im.getchannel('A').getextrema()),'corner_alpha':[im.getpixel(p)[3] for p in[(0,0),(511,0),(0,511),(511,511)]],'bbox_px':list(im.getchannel('A').getbbox()) if im.getchannel('A').getbbox() else None}
def main():
 contract=B/'manifests/import-XBW-primary-v001.json';assert r.sha(contract)=='79fd2508eabfdab26f4dcb1cc21682d08b2518d37bbc0111fc38655869eeb11f';base=r.read(contract)
 weapon=Image.open(base['weapon_component']['path']).convert('RGBA')
 out=P/'components/XBW-primary-four-armors-v001';assert not out.exists();out.mkdir(parents=True)
 armor_rows={f'ARM-{k}-001':[] for k in ['LGT','MED','HVY','ROB']};sheets={}
 for key in ['LGT','MED','HVY','ROB']:
  for name in ['armor_far','armor_near','assembled_right','assembled_left','native_selected']:
   sheets[(key,name)]=Image.new('RGBA',(1536,1024),(0,0,0,0))
 for i,f in enumerate(base['frames']):
  original=Image.open(f['source_body_path']).convert('RGBA');protected=ImageChops.lighter(poly(HEADS[i]),union([f['near_hand_polygon_px'],f['support_hand_polygon_px']]))
  # Original belt and pouch stay in the immutable shared body, not in any armor.
  belt=poly([(174,321),(233,322),(285,322),(290,349),(241,353),(229,369),(177,364),(174,344)])
  protected=ImageChops.lighter(protected,belt)
  upper=poly([(137,235),(181,230),(229,245),(274,243),(312,253),(329,280),(342,319),(327,334),(294,335),(288,351),(177,351),(151,328),(137,294)])
  nm=poly(NEAR_SLEEVES[i]);nearhand=poly(f['near_hand_polygon_px']);supporthand=poly(f['support_hand_polygon_px'])
  farbody=Image.open(f['body_far']['path']).convert('RGBA');hands=[Image.open(f[k]['path']).convert('RGBA') for k in ['body_support','body_near']]
  matrix=f['component_to_body_affine_2x3'];a,b,tx,c,d,ty=matrix;det=a*d-b*c
  transformed=weapon.transform((512,512),Image.Transform.AFFINE,(d/det,-b/det,(b*ty-d*tx)/det,-c/det,a/det,(c*tx-a*ty)/det),resample=Image.Resampling.BICUBIC)
  for key,number in [('LGT',104),('MED',105),('HVY',106),('ROB',107)]:
   src=P/f'processed/call{number}-fixed-canvas-v001/frame-{i}.png';source=Image.open(src).convert('RGBA')
   if key=='ROB':hems=[[(174,349),(241,349),(232,446),(166,435)],[(256,349),(293,349),(314,436),(269,448)],[(169,345),(184,353),(159,433),(149,423)]]
   elif key=='MED':hems=[[(176,349),(237,349),(231,385),(218,405),(173,397)],[(252,349),(289,348),(305,382),(297,391),(267,403),(247,385)]]
   elif key=='HVY':hems=[[(175,349),(292,348),(309,385),(286,398),(256,393),(234,399),(171,383)],[(169,399),(208,399),(223,409),(216,444),(199,453),(164,445)],[(259,399),(296,399),(310,414),(309,450),(270,455),(257,437)]]
   else:hems=[[(177,349),(290,349),(304,380),(278,391),(241,383),(225,394),(177,381)]]
   selection=ImageChops.lighter(upper,union(hems));selection=ImageChops.subtract(selection,protected)
   # The true robe may cover the old forearm, but blue original wraps/skin are never classified as garment.
   bare=poly(BARE_PATCHES[i]);sp=source.load();mp=selection.load();np=nm.load();bp=bare.load();removed_blue=removed_skin=0
   for y in range(512):
    for x in range(512):
     rr,gg,bb,aa=sp[x,y]
     if not mp[x,y] or not aa:continue
     blue=bb>gg*1.035 and gg>rr*1.03
     skin=key!='ROB' and bp[x,y] and rr>175 and gg>125 and bb>65 and rr>gg*1.15 and gg>bb*1.3
     if blue or skin:
      mp[x,y]=0;removed_blue+=int(blue);removed_skin+=int(skin)
   selected=extract(source,selection);near=extract(source,ImageChops.darker(selection,nm));far=extract(source,ImageChops.subtract(selection,nm))
   reconstruct=far.copy();reconstruct.alpha_composite(near);assert reconstruct.tobytes()==selected.tobytes()
   for m in [poly(HEADS[i]),nearhand,supporthand,belt]:assert ImageChops.multiply(selected.getchannel('A'),m).getbbox() is None
   assert all(p==s for p,s in zip(selected.get_flattened_data(),source.get_flattened_data()) if p[3])
   parts={name:save(im,out/f'ARM-{key}-001-{name}-{i}.png','real_native_XBW_costume_pixel_selection_candidate_not_runtime_approval') for name,im in [('armor_far',far),('armor_near',near)]}
   paths={}
   for name,m in [('garment',selection),('near',nm),('protected',protected)]:
    q=P/f'masks/XBW-primary-ARM-{key}-001-{name}-{i}-v001.png';q.parent.mkdir(exist_ok=True);assert not q.exists();m.save(q);r.archive(q,q.relative_to(P),'manual_pose_specific_source_pixel_selection_not_new_art');paths[name]={'path':str(q),'sha256':r.sha(q)}
   assembled=farbody.copy();assembled.alpha_composite(far);assembled.alpha_composite(transformed);assembled.alpha_composite(hands[0]);assembled.alpha_composite(near);assembled.alpha_composite(hands[1])
   for name,im in [('armor_far',far),('armor_near',near),('native_selected',selected),('assembled_right',assembled),('assembled_left',assembled.transpose(Image.Transpose.FLIP_LEFT_RIGHT))]:sheets[(key,name)].alpha_composite(im,((i%3)*512,(i//3)*512))
   armor_rows[f'ARM-{key}-001'].append({'index':i,**parts,'armor_hidden_back':None,'hidden_back_policy':'not_visible_in_native_pose_not_invented','root_px':f['ground_root_px'],'primary_grip_px':f['primary_grip_px'],'support_grip_px':f['support_grip_px'],'source_path':str(src),'source_sha256':r.sha(src),'selection_masks':paths,'source_pixels_only':True,'far_near_exact_selected_reconstruction':True,'protected_original_head_hands_belt_excluded':True,'blue_wrap_pixels_excluded':removed_blue,'native_skin_pixels_excluded':removed_skin,'body_geometry_transform':'none','phase':f['phase'],'time_start_s':f['time_start_s'],'time_end_s':f['time_end_s'],'semantic_review_passed':False,'runtime_verified':False})
 for (key,name),im in sheets.items():save(im,P/f'reviews/XBW-primary-ARM-{key}-001-{name}-selection-v001.png','actual_pose_specific_costume_static_assembly_review_pending')
 q=P/'manifests/XBW-primary-four-armors-selection-candidate-v001.json';assert not q.exists();r.write(q,{'schema':'XBW-pose-specific-armor-source-candidate-v1','clip':'primary','source_body_contract_path':str(contract),'source_body_contract_sha256':r.sha(contract),'canvas_px':[512,512],'frame_count':6,'armors':armor_rows,'draw_order':['body_far','armor_far','independent_weapon','body_support','armor_near','body_near'],'primary_and_support_hand_authority':'unchanged_frozen_body_tracks','source_requests':[104,105,106,107],'native_art_source_full_body_edits_only_final_layers_manual_actual_garment_selections':True,'body_geometry_transform':'none','per_frame_armor_geometry_transform':'none','semantic_review_passed':False,'runtime_verified':False,'full_armor_complete':False,'limitations':['Candidate masks require per-frame visual review; native alpha/pixel source checks are not semantic or runtime acceptance.','Visible garment back surfaces belong in armor_far; unseen hidden back is null, never fabricated.','ROB cuffs are new genuine cloth surfaces over original forearms; frozen fists/short distal wrap tracks remain exact.','Inherited root472 and boots483 do not certify footlock.']} );r.archive(q,q.relative_to(P),'actual_XBW_primary_four_armor_source_selection_candidate_pending_manual_review')
 print(json.dumps({'candidate':str(q),'sha256':r.sha(q),'armor_pngs':48,'common_original_body_pngs_reused':18,'source_calls':4,'semantic_review_passed':False}))
if __name__=='__main__':main()
