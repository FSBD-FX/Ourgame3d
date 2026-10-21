"""Trace four real reload costume poses; reuse exact frozen manipulation-hand tracks."""
from pathlib import Path
import importlib.util,json
from PIL import Image,ImageChops,ImageFilter
P=Path(__file__).resolve().parent;B=P.parent/'first-batch-weapon-actions-v001'
s=importlib.util.spec_from_file_location('primary_selection_util',P/'extract-primary-four-armors-v003.py');u=importlib.util.module_from_spec(s);s.loader.exec_module(u);r=u.r
HEADS=[[(163,120),(238,120),(273,137),(293,166),(300,201),(300,229),(285,253),(266,260),(232,261),(196,247),(175,239),(164,220),(160,187),(161,151)],
[(165,119),(239,119),(273,138),(293,167),(301,201),(301,232),(286,255),(266,262),(232,263),(197,249),(175,240),(165,220),(161,187),(162,152)],
[(163,120),(240,120),(273,138),(294,167),(301,201),(301,232),(287,255),(267,263),(232,263),(196,250),(174,239),(163,218),(159,185),(160,150)],
[(166,120),(241,120),(274,139),(294,168),(301,201),(301,231),(286,255),(267,263),(233,263),(198,250),(176,240),(165,220),(162,187),(163,151)]]
NEAR=[[(150,236),(182,233),(210,247),(235,260),(278,263),(281,308),(233,315),(194,303),(163,288),(147,265)],
[(120,237),(154,231),(181,240),(207,259),(212,300),(181,317),(148,302),(125,278)],
[(148,235),(177,234),(202,248),(223,264),(225,302),(203,318),(169,305),(149,285)],
[(138,240),(169,234),(197,247),(214,271),(221,307),(207,337),(174,334),(146,313),(133,284)]]
BARE=[[(207,268),(264,266),(273,278),(268,296),(222,298),(207,288)],[(135,263),(174,267),(182,283),(173,297),(143,291)],[(170,272),(213,272),(223,285),(214,301),(179,300)],[(147,288),(181,289),(190,306),(178,321),(151,313)]]
def main():
 contract=B/'manifests/import-XBW-reload-four-keyposes-v001.json';assert r.sha(contract)=='9a0f99a5b32a5b898b9fa98d4b40812daf5e532a73954f13df91a7c166297ee8';base=r.read(contract)
 out=P/'components/XBW-reload-four-armors-v002';assert not out.exists();out.mkdir(parents=True)
 armor_rows={f'ARM-{k}-001':[] for k in ['LGT','MED','HVY','ROB']};sheets={(key,kind):Image.new('RGBA',(1024,1024),(0,0,0,0)) for key in ['LGT','MED','HVY','ROB'] for kind in ['armor_far','armor_near','native_selected','assembled_right','assembled_left']}
 for i,f in enumerate(base['frames']):
  near_mask=Image.open(B/f'components/XBW-reload-four-keyposes-v002/near-selection-mask-{i}.png').convert('L');support_mask=Image.open(B/f'components/XBW-reload-four-keyposes-v002/support-selection-mask-{i}.png').convert('L')
  belt=u.union([[(174,322),(228,323),(280,322),(286,340),(274,350),(230,350),(224,345),(174,345)],[(178,332),(203,330),(226,333),(228,355),(219,369),(177,367),(172,351)]])
  wraps=[[(265,263),(300,262),(307,275),(304,295),(269,300),(262,284)],[(164,263),(195,260),(216,264),(217,294),(175,298),(164,286)],[(207,266),(240,265),(253,272),(251,293),(219,299),(208,289)],[(170,294),(201,295),(213,300),(212,320),(192,326),(174,321),(168,308)]]
  protected=ImageChops.lighter(u.poly(HEADS[i]),ImageChops.lighter(u.poly(wraps[i]),ImageChops.lighter(near_mask,ImageChops.lighter(support_mask,belt)))).filter(ImageFilter.MaxFilter(9))
  upper=u.poly([(120,231),(177,230),(228,244),(273,241),(312,255),(338,283),(347,317),(331,345),(288,353),(169,354),(141,330),(120,293)])
  nm=u.poly(NEAR[i]);bare=u.poly(BARE[i]);farbody=Image.open(f['body_far']['path']).convert('RGBA');hands=[Image.open(f[k]['path']).convert('RGBA') for k in ['body_support','body_near']]
  weapon=Image.open(f['weapon']['path']).convert('RGBA');m=f['component_to_body_affine_2x3'];a,b,tx=m[0];c,d,ty=m[1];det=a*d-b*c
  render=weapon.transform((512,512),Image.Transform.AFFINE,(d/det,-b/det,(b*ty-d*tx)/det,-c/det,a/det,(c*tx-a*ty)/det),resample=Image.Resampling.BICUBIC)
  for key,n in [('LGT',108),('MED',109),('HVY',110),('ROB',111)]:
   src=P/f'processed/call{n}-fixed-canvas-v002/frame-{i}.png';source=Image.open(src).convert('RGBA')
   if key=='ROB':hems=[[(171,348),(240,348),(234,446),(164,435)],[(254,348),(295,348),(317,436),(269,448)],[(167,344),(181,352),(156,433),(144,422)]]
   elif key=='MED':hems=[[(173,348),(239,348),(231,388),(218,407),(171,397)],[(252,348),(292,348),(307,383),(295,395),(267,405),(246,386)]]
   elif key=='HVY':hems=[[(171,348),(294,348),(310,385),(285,399),(255,394),(234,399),(170,383)],[(168,399),(207,398),(222,410),(216,446),(199,454),(162,446)],[(258,398),(295,399),(310,413),(310,450),(270,456),(256,438)]]
   else:hems=[[(174,348),(292,348),(305,381),(277,393),(240,384),(225,394),(174,383)]]
   selection=ImageChops.subtract(ImageChops.lighter(upper,u.union(hems)),protected);mp=selection.load();sp=source.load();bp=bare.load()
   for y in range(512):
    for x in range(512):
     rr,gg,bb,aa=sp[x,y]
     if mp[x,y] and aa and ((rr>gg+30 and bb>gg+30) or (bb>gg*1.035 and gg>rr*1.03) or (key!='ROB' and bp[x,y])):mp[x,y]=0
   selected=u.extract(source,selection);near=u.extract(source,ImageChops.darker(selection,nm));far=u.extract(source,ImageChops.subtract(selection,nm));rebuilt=far.copy();rebuilt.alpha_composite(near);assert rebuilt.tobytes()==selected.tobytes()
   assert not ImageChops.multiply(selected.getchannel('A'),protected).getbbox()
   assert all(p==q for p,q in zip(selected.get_flattened_data(),source.get_flattened_data()) if p[3])
   parts={name:u.save(im,out/f'ARM-{key}-001-{name}-{i}.png','actual_native_reload_costume_layer_pixels_fixed_pose_candidate') for name,im in [('armor_far',far),('armor_near',near)]}
   masks={}
   for name,im in [('garment',selection),('near',nm),('protected',protected)]:
    q=P/f'masks/XBW-reload-ARM-{key}-001-{name}-{i}-v002.png';q.parent.mkdir(exist_ok=True);assert not q.exists();im.save(q);r.archive(q,q.relative_to(P),'manual_reload_costume_source_selection_and_original_hand_protection');masks[name]={'path':str(q),'sha256':r.sha(q)}
   assembled=farbody.copy();assembled.alpha_composite(far);assembled.alpha_composite(render);assembled.alpha_composite(hands[0]);assembled.alpha_composite(near);assembled.alpha_composite(hands[1])
   for kind,im in [('armor_far',far),('armor_near',near),('native_selected',selected),('assembled_right',assembled),('assembled_left',assembled.transpose(Image.Transpose.FLIP_LEFT_RIGHT))]:sheets[(key,kind)].alpha_composite(im,((i%2)*512,(i//2)*512))
   armor_rows[f'ARM-{key}-001'].append({'index':i,**parts,'armor_hidden_back':None,'hidden_back_policy':'no_invented_unseen_surfaces','root_px':f['ground_root_px'],'primary_grip_px':f['primary_stock_grip_px'],'support_grip_px':f['body_support_contact_px'],'manipulation_contact_px':f['body_manipulation_contact_px'],'source_path':str(src),'source_sha256':r.sha(src),'selection_masks':masks,'source_pixels_only':True,'far_near_exact_selected_reconstruction':True,'protected_original_head_hands_belt_excluded':True,'body_geometry_transform':'none','phase':f['stage'],'time_start_s':f['time_start_s'],'time_end_s':f['time_end_s'],'runtime_verified':False,'semantic_review_passed':False})
 for (key,kind),im in sheets.items():u.save(im,P/f'reviews/XBW-reload-ARM-{key}-001-{kind}-selection-v002.png','actual_reload4_costume_static_assembly_candidate_pending_review')
 q=P/'manifests/XBW-reload-four-armors-selection-candidate-v002.json';assert not q.exists();r.write(q,{'schema':'XBW-pose-specific-armor-source-candidate-v1','clip':'reload','source_body_contract_path':str(contract),'source_body_contract_sha256':r.sha(contract),'canvas_px':[512,512],'frame_count':4,'armors':armor_rows,'draw_order':['body_far','armor_far','independent_weapon','body_support','armor_near','body_near'],'source_requests':[108,109,110,111],'body_geometry_transform':'none','per_frame_armor_geometry_transform':'none','semantic_review_passed':False,'runtime_verified':False,'full_armor_complete':False});r.archive(q,q.relative_to(P),'reload4_four_armor_actual_source_selections_candidate_not_runtime')
 print(json.dumps({'candidate':str(q),'sha256':r.sha(q),'armor_pngs':32,'common_original_body_pngs_reused':12,'source_calls':4,'runtime_verified':False}))
if __name__=='__main__':main()
