"""Actual ready-idle costume selections over unchanged frozen two-hand body pixels."""
from pathlib import Path
import importlib.util,json,math
from PIL import Image,ImageChops,ImageFilter
P=Path(__file__).resolve().parent;B=P.parent/'first-batch-weapon-actions-v001'
s=importlib.util.spec_from_file_location('selection_util',P/'extract-primary-four-armors-v003.py');u=importlib.util.module_from_spec(s);s.loader.exec_module(u);r=u.r
def main():
 contract=B/'manifests/import-XBW-ready-idle-v001.json';assert r.sha(contract)=='21c8ff90c59c411bfdbcabcfee0292881d77e4e652cc2fde46cab35e99373813';base=r.read(contract)
 out=P/'components/XBW-ready_idle-four-armors-v001';assert not out.exists();out.mkdir(parents=True)
 rows={f'ARM-{k}-001':[] for k in ['LGT','MED','HVY','ROB']};sheets={(k,n):Image.new('RGBA',(1536,1024),(0,0,0,0)) for k in ['LGT','MED','HVY','ROB'] for n in ['armor_far','armor_near','native_selected','assembled_right','assembled_left']}
 nearhand=Image.open(B/'masks/XBW-ready-idle-near-v001.png').convert('L');supporthand=Image.open(B/'masks/XBW-ready-idle-support-v001.png').convert('L')
 belt=u.union([[(175,322),(228,323),(279,322),(285,340),(274,348),(231,350),(224,344),(175,344)],[(178,332),(202,330),(226,333),(228,355),(219,368),(178,367),(173,351)]])
 protected=ImageChops.lighter(u.poly(u.HEADS[0]),ImageChops.lighter(belt,ImageChops.lighter(u.union(u.BLUE_WRAPS[0]),ImageChops.lighter(nearhand,supporthand)))).filter(ImageFilter.MaxFilter(9))
 upper=u.poly([(137,235),(181,230),(229,245),(274,243),(312,253),(329,280),(342,319),(327,334),(294,335),(288,351),(172,351),(149,328),(137,294)])
 neararea=u.poly(u.NEAR_SLEEVES[0]);bare=u.poly(u.BARE_PATCHES[0]).filter(ImageFilter.MaxFilter(9))
 weapon=Image.open(base['weapon_component']['path']).convert('RGBA');wp=base['weapon_component']['primary_grip_px'];scale=.48;angle=math.radians(-5);co=math.cos(angle);si=math.sin(angle);g=[224,316]
 render=weapon.transform((512,512),Image.Transform.AFFINE,(co/scale,si/scale,wp[0]-(co*g[0]+si*g[1])/scale,-si/scale,co/scale,wp[1]-(-si*g[0]+co*g[1])/scale),resample=Image.Resampling.BICUBIC)
 for i,f in enumerate(base['frames']):
  farbody=Image.open(f['body_far']['path']).convert('RGBA');support=Image.open(f['body_support']['path']).convert('RGBA');hand=Image.open(f['body_near']['path']).convert('RGBA')
  for key,n in [('LGT',112),('MED',113),('HVY',114),('ROB',115)]:
   src=P/f'processed/call{n}-fixed-canvas-v001/frame-{i}.png';native=Image.open(src).convert('RGBA')
   if key=='ROB':hems=[[(173,348),(242,348),(237,446),(165,435)],[(254,348),(296,348),(318,437),(269,449)],[(168,344),(184,352),(158,433),(150,422)]]
   elif key=='MED':hems=[[(170,348),(237,348),(233,388),(219,408),(169,398)],[(252,348),(293,348),(308,383),(296,397),(267,406),(247,386)]]
   elif key=='HVY':hems=[[(171,348),(294,348),(310,385),(285,399),(255,394),(234,399),(170,383)],[(168,399),(207,398),(222,410),(216,446),(199,454),(162,446)],[(258,398),(295,399),(310,413),(310,450),(270,456),(256,438)]]
   else:hems=[[(171,348),(293,348),(308,381),(278,393),(240,384),(225,394),(171,383)]]
   selection=ImageChops.subtract(ImageChops.lighter(upper,u.union(hems)),protected);sp=native.load();mp=selection.load();bp=bare.load()
   for y in range(512):
    for x in range(512):
     rr,gg,bb,aa=sp[x,y]
     if mp[x,y] and aa and ((rr>gg+30 and bb>gg+30) or (bb>gg*1.035 and gg>rr*1.03) or (key!='ROB' and bp[x,y])):mp[x,y]=0
   selected=u.extract(native,selection);near=u.extract(native,ImageChops.darker(selection,neararea));far=u.extract(native,ImageChops.subtract(selection,neararea));rebuilt=far.copy();rebuilt.alpha_composite(near);assert rebuilt.tobytes()==selected.tobytes()
   assert not ImageChops.multiply(selected.getchannel('A'),protected).getbbox();assert all(p==q for p,q in zip(selected.get_flattened_data(),native.get_flattened_data()) if p[3])
   parts={name:u.save(im,out/f'ARM-{key}-001-{name}-{i}.png','actual_native_ready_idle_costume_surface_fixed_frozen_body_candidate') for name,im in [('armor_far',far),('armor_near',near)]};masks={}
   for name,im in [('garment',selection),('near',neararea),('protected',protected)]:
    q=P/f'masks/XBW-ready_idle-ARM-{key}-001-{name}-{i}-v001.png';assert not q.exists();im.save(q);r.archive(q,q.relative_to(P),'actual_ready_pose_manual_garment_selection_and_anatomy_protection');masks[name]={'path':str(q),'sha256':r.sha(q)}
   assembled=farbody.copy();assembled.alpha_composite(far);assembled.alpha_composite(render);assembled.alpha_composite(support);assembled.alpha_composite(near);assembled.alpha_composite(hand)
   for kind,im in [('armor_far',far),('armor_near',near),('native_selected',selected),('assembled_right',assembled),('assembled_left',assembled.transpose(Image.Transpose.FLIP_LEFT_RIGHT))]:sheets[(key,kind)].alpha_composite(im,((i%3)*512,(i//3)*512))
   rows[f'ARM-{key}-001'].append({'index':i,**parts,'armor_hidden_back':None,'hidden_back_policy':'actual_visible_back_only_in_far_unseen_null','root_px':f['ground_root_px'],'primary_grip_px':f['primary_grip_px'],'support_grip_px':f['support_grip_px'],'source_path':str(src),'source_sha256':r.sha(src),'selection_masks':masks,'source_pixels_only':True,'far_near_exact_selected_reconstruction':True,'protected_original_head_hands_belt_excluded':True,'body_geometry_transform':'none','phase':'ready_idle','time_start_s':f['time_start_s'],'time_end_s':f['time_end_s'],'semantic_review_passed':False,'runtime_verified':False})
 for (key,kind),im in sheets.items():u.save(im,P/f'reviews/XBW-ready_idle-ARM-{key}-001-{kind}-selection-v001.png','actual_ready_idle_four_armor_static_assembly_pending_manual_review')
 q=P/'manifests/XBW-ready_idle-four-armors-selection-candidate-v001.json';assert not q.exists();r.write(q,{'schema':'XBW-pose-specific-armor-source-candidate-v1','clip':'ready_idle','source_body_contract_path':str(contract),'source_body_contract_sha256':r.sha(contract),'canvas_px':[512,512],'frame_count':6,'armors':rows,'draw_order':['body_far','armor_far','independent_weapon','body_support','armor_near','body_near'],'source_requests':[112,113,114,115],'body_geometry_transform':'none','per_frame_armor_geometry_transform':'none','semantic_review_passed':False,'runtime_verified':False,'full_armor_complete':False});r.archive(q,q.relative_to(P),'ready_idle_four_armor_actual_source_selections_candidate_not_runtime')
 print(json.dumps({'candidate':str(q),'sha256':r.sha(q),'armor_pngs':48,'reused_body_pngs':18,'native_calls':4,'runtime_verified':False}))
if __name__=='__main__':main()
