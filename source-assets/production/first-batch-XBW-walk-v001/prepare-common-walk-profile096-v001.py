"""One new0.96 pass from native117 raw; all three actual weapon states, no art/API/engine."""
from pathlib import Path
import importlib.util,math
from PIL import Image,ImageDraw,ImageChops,ImageOps
P=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('rec',P/'production-record.py');w=importlib.util.module_from_spec(s);s.loader.exec_module(w);r=w.r
sp=Path('C:/Users/22499/.codex/skills/generate2dsprite/scripts/generate2dsprite.py');s=importlib.util.spec_from_file_location('processor',sp);skill=importlib.util.module_from_spec(s);s.loader.exec_module(skill)
SCALE=.96;LIMIT=3.129
oldpath=P/'manifests/import-XBW-common-walk-v001.json';assert r.sha(oldpath)=='7185df2ad077ec92d020788f84f2f9b890dc7d042ceb7656d0a9576177d471a5';old=r.read(oldpath)
ledger=r.read(r.LEDGER);e=next(x for x in ledger['requests']if x['request_number']==117);rawpath=Path(e['raw_path']);assert r.sha(rawpath)==e['sha256'];raw=Image.open(rawpath).convert('RGBA');assert raw.size==(1536,1024)
life=P.parent/'first-batch-weapon-actions-v001/manifests/weapon-state-lifecycle-v001.json';lc=r.read(life)
wc=P.parent/'first-batch-weapon-components-v001/manifests/import-weapon-components-v001.json';wn=r.read(wc)['weapons']['WPN-XBW-001']
neutral={'state_index':-1,'path':wn['path'],'sha256':wn['sha256'],'stock_grip_px':wn['primary_grip_px'],'support_grip_px':wn['support_grip_px'],'emit_px':wn['emit_px'],'marker_numeric_uncertainty_px':None}
states=[neutral,lc['states'][0],lc['states'][3]]
def mask(poly):
 m=Image.new('L',(512,512));ImageDraw.Draw(m).polygon(poly,fill=255);return m
def select(src,m):
 im=src.copy();im.putalpha(ImageChops.multiply(src.getchannel('A'),m));im.putdata([p if p[3]else(0,0,0,0)for p in im.get_flattened_data()]);return im
def save(im,q,status):
 q.parent.mkdir(parents=True,exist_ok=True);assert not q.exists();im.save(q);r.archive(q,q.relative_to(P),status)
 return {'path':str(q),'sha256':r.sha(q),'canvas_px':list(im.size),'mode':im.mode,'alpha_extrema':list(im.getchannel('A').getextrema())if im.mode=='RGBA'else None,'bbox_px':list(im.getchannel('A').getbbox())if im.mode=='RGBA'else None,'corner_alpha':[im.getpixel(p)[3]for p in[(0,0),(511,0),(0,511),(511,511)]]if im.mode=='RGBA'else None}
def pt(m,p):return[m[0]*p[0]+m[1]*p[1]+m[2],m[3]*p[0]+m[4]*p[1]+m[5]]
rows=[];sheets={k:Image.new('RGBA',(1536,1024))for k in['body','body_far','body_support','body_near','neutral_right','neutral_left','empty0_right','empty0_left','loaded3_right','loaded3_left']}
for i,oldf in enumerate(old['frames']):
 box=[i%3*512,i//3*512,(i%3+1)*512,(i//3+1)*512];native=skill.clean_edges(skill.remove_bg_magenta(raw.crop(tuple(box)),threshold=90,edge_threshold=140),depth=3)
 # Confirm source matte against the historical unscaled native cell, never read old0.94 body pixels as input.
 assert native.tobytes()==Image.open(oldf['source_native_body_path']).convert('RGBA').tobytes()
 nf=save(native,P/f'processed/call117-native-matte-v003/frame-{i}.png','fresh_native_raw_cell_matte_no_resampling')
 sole=oldf['source_sole_px'];tx=256-SCALE*256;ty=472-SCALE*sole[1];m=[SCALE,0,tx,0,SCALE,ty]
 body=native.transform((512,512),Image.Transform.AFFINE,(1/SCALE,0,-tx/SCALE,0,1/SCALE,-ty/SCALE),resample=Image.Resampling.BICUBIC)
 fringe=sum(p[3]>0 and p[0]>p[1]+30 and p[2]>p[1]+30 for p in body.get_flattened_data());body.putdata([p if p[3]and not(p[0]>p[1]+30 and p[2]>p[1]+30)else(0,0,0,0)for p in body.get_flattened_data()])
 ng=oldf['native_primary_grip_px'];nh=oldf['native_support_grip_px'];g=pt(m,ng);h=pt(m,nh)
 nearpoly=[pt(m,(ng[0]+dx,ng[1]+dy))for dx,dy in[(-28,-15),(-12,-21),(3,-20),(16,-14),(20,-4),(18,13),(8,21),(-8,20),(-22,13),(-28,4)]]
 supportpoly=[pt(m,(nh[0]+dx,nh[1]+dy))for dx,dy in[(-28,-14),(-10,-21),(4,-20),(16,-14),(19,-4),(16,16),(4,24),(-12,22),(-23,14),(-28,3)]]
 near=mask(nearpoly);support=mask(supportpoly);assert not ImageChops.multiply(near,support).getbbox()
 parts={'body_far':select(body,ImageChops.invert(ImageChops.lighter(near,support))),'body_support':select(body,support),'body_near':select(body,near)}
 rb=parts['body_far'].copy();rb.alpha_composite(parts['body_support']);rb.alpha_composite(parts['body_near']);assert rb.tobytes()==body.tobytes()
 files={k:save(im,P/f'components/XBW-common-walk-v003/{k}-{i}.png','new096_native_derived_three_body_tracks_candidate_not_footlock')for k,im in parts.items()}
 bf=save(body,P/f'processed/call117-common-profile-v003/body-{i}.png','single096_resampling_from_native117_not_old094')
 nm=P/f'masks/XBW-common-walk-near-{i}-v003.png';sm=P/f'masks/XBW-common-walk-support-{i}-v003.png';save(near,nm,'same_native_anatomy_polygon_new096_transform');save(support,sm,'same_native_anatomy_polygon_new096_transform')
 sr=[]
 for state in states:
  vector=[state['support_grip_px'][j]-state['stock_grip_px'][j]for j in[0,1]];angle=math.atan2(h[1]-g[1],h[0]-g[0])-math.atan2(vector[1],vector[0]);co=.48*math.cos(angle);si=.48*math.sin(angle);anchor=state['stock_grip_px'];cm=[co,-si,g[0]-co*anchor[0]+si*anchor[1],si,co,g[1]-si*anchor[0]-co*anchor[1]]
  actual=pt(cm,state['support_grip_px']);error=math.dist(actual,h);assert error<=LIMIT
  det=co*co+si*si;inv=(co/det,si/det,-(co*cm[2]+si*cm[5])/det,-si/det,co/det,-(-si*cm[2]+co*cm[5])/det);assert r.sha(Path(state['path']))==state['sha256'];render=Image.open(state['path']).convert('RGBA').transform((512,512),Image.Transform.AFFINE,inv,resample=Image.Resampling.BICUBIC)
  assembly=parts['body_far'].copy();assembly.alpha_composite(render);assembly.alpha_composite(parts['body_support']);assembly.alpha_composite(parts['body_near']);key={-1:'neutral',0:'empty0',3:'loaded3'}[state['state_index']]
  for side,im in[('right',assembly),('left',ImageOps.mirror(assembly))]:sheets[f'{key}_{side}'].alpha_composite(im,((i%3)*512,(i//3)*512))
  sr.append({'state_index':state['state_index'],'path':state['path'],'sha256':state['sha256'],'stock_grip_px':anchor,'support_grip_px':state['support_grip_px'],'virtual_emit_px':state['emit_px'],'component_to_body_affine_2x3':cm,'weapon_scale':.48,'weapon_angle_image_clockwise_deg':math.degrees(angle),'transformed_stock_px':pt(cm,anchor),'transformed_support_px':actual,'support_alignment_error_px':error,'support_fit_gate_px':LIMIT,'support_fit_gate_passed':True,'transformed_virtual_emit_body_px':pt(cm,state['emit_px']),'emit_is_virtual_not_opaque_or_combat_Z':True,'runtime_verified':False})
 for k,im in[('body',body),*parts.items()]:sheets[k].alpha_composite(im,((i%3)*512,(i//3)*512))
 rows.append({'index':i,'raw_source_path':str(rawpath),'raw_source_sha256':r.sha(rawpath),'raw_cell_box_px':box,'source_native_body_path':nf['path'],'source_native_body_sha256':nf['sha256'],'source_body_path':bf['path'],'source_body_sha256':bf['sha256'],'source_body_transform_2x3':m,'source_geometry_transform':'one_shared0.96_native117_scale_then_rigid_sole_proxy_translation','source_sole_px':sole,'source_sole_measurement':oldf['source_sole_measurement'],'sole_measurement_uncertainty_px':oldf['sole_measurement_uncertainty_px'],'transformed_sole_px':pt(m,sole),'ground_root_px':[256,472],'root_px':[256,472],'root_kind':oldf['root_kind'],'primary_grip_px':g,'grip_px':g,'support_grip_px':h,'native_primary_grip_px':ng,'native_support_grip_px':nh,'grip_measurement_uncertainty_native_px':3,'near_hand_polygon_px':nearpoly,'support_hand_polygon_px':supportpoly,'selection_masks':{'near':{'path':str(nm),'sha256':r.sha(nm)},'support':{'path':str(sm),'sha256':r.sha(sm)}},**files,'weapon_state_mappings':sr,'weapon_scale':.48,'post_transform_chroma_fringe_pixels_removed':fringe,'phase':'walk','time_start_s':oldf['time_start_s'],'time_end_s':oldf['time_end_s'],'weapon_visible':True,'body_three_track_exact_source_reconstruction':True,'runtime_verified':False})
previews=[]
for k,im in sheets.items():
 q=P/f'reviews/XBW-common-walk-{k}-v003.png';save(im,q,'new096_static_three_actual_component_states_both_directions_not_runtime');previews.append({'kind':k,'path':str(q),'sha256':r.sha(q)})
q=P/'manifests/XBW-common-walk-candidate-v003.json';assert not q.exists();r.write(q,{'schema':'XBW-common-walk-three-body-track-candidate-v2','version':3,'frozen':False,'frame_count':6,'canvas_px':[512,512],'root_px':[256,472],'frames':rows,'previews':previews,'prior_body_contract_path':str(oldpath),'prior_body_contract_sha256':r.sha(oldpath),'weapon_lifecycle_contract_path':str(life),'weapon_lifecycle_contract_sha256':r.sha(life),'neutral_component_contract_path':str(wc),'neutral_component_contract_sha256':r.sha(wc),'draw_order':['body_far','independent_weapon','body_support','body_near'],'duration_s':.6,'loop':True,'new_body_PNGs':18,'body_shared_scale':SCALE,'body_scale_ratio_from_prior':SCALE/.94,'body_from_native_raw_single_resampling':True,'fixed_weapon_scale':.48,'support_fit_gate_px':LIMIT,'all18_pose_state_fit_gates_passed':True,'max_support_alignment_error_px':max(x['support_alignment_error_px']for f in rows for x in f['weapon_state_mappings']),'processor_path':str(sp),'processor_sha256':r.sha(sp),'new_generation_calls':0,'source_request':117,'initial_Ammo1_neutral_minus1_preserved':True,'BodySize160_changed':False,'movespeed_changed':False,'runtime_verified':False,'footlock_certified':False,'manual_assembly_review_passed':False});r.archive(q,q.relative_to(P),'new096_common_body_candidate_all18_math_gates_true_not_runtime')
print({'candidate':str(q),'sha256':r.sha(q),'new_body_PNGs':18,'all18_pose_state_fit_gates':True,'perframe_errors':[{s['state_index']:round(s['support_alignment_error_px'],9)for s in f['weapon_state_mappings']}for f in rows],'max_error':max(x['support_alignment_error_px']for f in rows for x in f['weapon_state_mappings']),'generation_calls':0})
