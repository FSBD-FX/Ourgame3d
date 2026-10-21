"""One pass from native armor raws via common coordinate change. No old delivery resampling."""
from pathlib import Path
import importlib.util,math
from PIL import Image,ImageChops,ImageFilter,ImageOps
P=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('rec',P/'production-record.py');w=importlib.util.module_from_spec(s);s.loader.exec_module(w);r=w.r
sp=Path('C:/Users/22499/.codex/skills/generate2dsprite/scripts/generate2dsprite.py');s=importlib.util.spec_from_file_location('processor',sp);skill=importlib.util.module_from_spec(s);s.loader.exec_module(skill)
newcp=P/'manifests/import-XBW-common-walk-v002.json';oldcp=P/'manifests/import-XBW-common-walk-v001.json';oldap=P/'manifests/import-XBW-walk-four-armors-v001.json'
assert r.sha(newcp)=='901e9e307a0654ae8c6f8385af2a9b4be94b063e06bfde2ca77cf43db1d1deab'and r.sha(oldcp)=='7185df2ad077ec92d020788f84f2f9b890dc7d042ceb7656d0a9576177d471a5'and r.sha(oldap)=='35b3a0cffc9fb731a40ff4a08cde7d5e89b5f7fceff67824feb08f31849e7ff4'
base=r.read(newcp);old=r.read(oldcp);armor=r.read(oldap);ledger=r.read(r.LEDGER)
def select(im,m):
 q=im.copy();q.putalpha(ImageChops.multiply(im.getchannel('A'),m));q.putdata([p if p[3]else(0,0,0,0)for p in q.get_flattened_data()]);return q
def save(im,q,status):
 q.parent.mkdir(parents=True,exist_ok=True);assert not q.exists();im.save(q);r.archive(q,q.relative_to(P),status)
 return {'path':str(q),'sha256':r.sha(q),'canvas_px':list(im.size),'mode':im.mode,'alpha_extrema':list(im.getchannel('A').getextrema())if im.mode=='RGBA'else None,'bbox_px':list(im.getchannel('A').getbbox())if im.mode=='RGBA'else None,'corner_alpha':[im.getpixel(p)[3]for p in[(0,0),(511,0),(0,511),(511,511)]]if im.mode=='RGBA'else None}
def transform_inverse(m):
 a,b,c,d,e,f=m;det=a*e-b*d;return(e/det,-b/det,(b*f-e*c)/det,-d/det,a/det,(d*c-a*f)/det)
rows={k:[]for k in armor['armors']};sheets={(k,n):Image.new('RGBA',(1536,1024))for k in rows for n in['native_selected','armor_far','armor_near','neutral_right','neutral_left','empty0_right','empty0_left','loaded3_right','loaded3_left']}
total_hand_cut=0;total_frames=0
for i,nf in enumerate(base['frames']):
 of=old['frames'][i];N=nf['source_body_transform_2x3'];O=of['source_body_transform_2x3'];ratio=N[0]/O[0];T=[ratio,0,N[2]-ratio*O[2],0,ratio,N[5]-ratio*O[5]]
 assert abs(T[0]-.96/.94)<1e-12 and abs(T[2]-256*(1-ratio))<1e-10 and abs(T[5]-472*(1-ratio))<1e-10
 inv=transform_inverse(T);parts={k:Image.open(nf[k]['path']).convert('RGBA')for k in['body_far','body_support','body_near']}
 actual_hands=ImageChops.lighter(parts['body_support'].getchannel('A'),parts['body_near'].getchannel('A')).point(lambda a:255 if a else 0).filter(ImageFilter.MaxFilter(3))
 weapons={}
 for st in nf['weapon_state_mappings']:weapons[st['state_index']]=Image.open(st['path']).convert('RGBA').transform((512,512),Image.Transform.AFFINE,transform_inverse(st['component_to_body_affine_2x3']),resample=Image.Resampling.BICUBIC)
 for key,num in[('ARM-LGT-001',118),('ARM-MED-001',119),('ARM-HVY-001',120),('ARM-ROB-001',121)]:
  af=armor['armors'][key][i];e=next(e for e in ledger['requests']if e['request_number']==num);rawp=Path(e['raw_path']);assert r.sha(rawp)==e['sha256'];raw=Image.open(rawp).convert('RGBA');assert raw.size==(1536,1024)
  box=(i%3*512,i//3*512,(i%3+1)*512,(i//3+1)*512);native=skill.clean_edges(skill.remove_bg_magenta(raw.crop(box),threshold=90,edge_threshold=140),depth=3)
  assert r.sha(Path(af['source_path']))==af['source_sha256']and native.tobytes()==Image.open(af['source_path']).convert('RGBA').tobytes()
  transformed=native.transform((512,512),Image.Transform.AFFINE,inv,resample=Image.Resampling.BICUBIC);fringe=sum(p[3]>0 and p[0]>p[1]+30 and p[2]>p[1]+30 for p in transformed.get_flattened_data());transformed.putdata([p if p[3]and not(p[0]>p[1]+30 and p[2]>p[1]+30)else(0,0,0,0)for p in transformed.get_flattened_data()])
  nativefile=save(transformed,P/f'processed/armor-profile096-v001/{key}-source-{i}.png','single_transform_from_native_raw_armor_not_old_layer_PNG')
  masks={}
  for name in['garment','near','protected']:
   om=af['selection_masks'][name];assert r.sha(Path(om['path']))==om['sha256'];masks[name]=Image.open(om['path']).convert('L').transform((512,512),Image.Transform.AFFINE,inv,resample=Image.Resampling.NEAREST)
  before=masks['garment'];original_intersection=ImageChops.multiply(before,actual_hands);cut=sum(1 for p in original_intersection.get_flattened_data()if p);total_hand_cut+=cut
  masks['protected']=ImageChops.lighter(masks['protected'],actual_hands);masks['garment']=ImageChops.subtract(masks['garment'],masks['protected'])
  # Same semantic parts share exactly the same one global transform; actual new hand alpha remains protected.
  selected=select(transformed,masks['garment']);near=select(transformed,ImageChops.darker(masks['garment'],masks['near']));far=select(transformed,ImageChops.subtract(masks['garment'],masks['near']));rb=far.copy();rb.alpha_composite(near);assert rb.tobytes()==selected.tobytes()
  assert not ImageChops.multiply(selected.getchannel('A'),actual_hands).getbbox()and not ImageChops.multiply(selected.getchannel('A'),masks['protected']).getbbox()
  files={k:save(im,P/f'components/XBW-walk-four-armors-v005/{key}-{k}-{i}.png','new096_source_derived_armor_layer_same_common_transform')for k,im in[('armor_far',far),('armor_near',near)]};maskfiles={}
  for name,m in masks.items():
   q=P/f'masks/XBW-walk-{key}-{name}-{i}-v005.png';save(m,q,'old_semantic_boundary_new_common_transform_plus_actual_new_hand_guard');maskfiles[name]={'path':str(q),'sha256':r.sha(q),'source_mask_path':af['selection_masks'][name]['path'],'source_mask_sha256':af['selection_masks'][name]['sha256']}
  for st,weapon in weapons.items():
   assembled=parts['body_far'].copy();assembled.alpha_composite(far);assembled.alpha_composite(weapon);assembled.alpha_composite(parts['body_support']);assembled.alpha_composite(near);assembled.alpha_composite(parts['body_near']);label={-1:'neutral',0:'empty0',3:'loaded3'}[st]
   for side,im in[('right',assembled),('left',ImageOps.mirror(assembled))]:sheets[(key,f'{label}_{side}')].alpha_composite(im,((i%3)*512,(i//3)*512))
  for k,im in[('native_selected',selected),('armor_far',far),('armor_near',near)]:sheets[(key,k)].alpha_composite(im,((i%3)*512,(i//3)*512))
  rows[key].append({'index':i,**files,'armor_hidden_back':None,'hidden_back_policy':'visible_back_only_in_far_unseen_null','root_px':[256,472],'primary_grip_px':nf['primary_grip_px'],'support_grip_px':nf['support_grip_px'],'source_path':nativefile['path'],'source_sha256':nativefile['sha256'],'raw_source_path':str(rawp),'raw_source_sha256':r.sha(rawp),'raw_cell_box_px':list(box),'source_geometry_transform_2x3':T,'transform_derivation':'NewBodyAffine096 × inverse(OldBodyAffine094); same_global_root_centered096/094transform_for_all_body_armor_pose_surfaces','native_raw_single_resampling':True,'old_delivery_RGBA_used_as_resampling_input':False,'source_transformed_pixels_only':True,'source_native_RGBA_pixel_identity':False,'source_native_identity_reason':'one_explicit_uniform_resampling; pixels equal transformed_native_source_not_unresampled_original','post_transform_chroma_fringe_pixels_removed':fringe,'selection_masks':maskfiles,'extra_actual_new_hand_guard_cut_mask_pixels':cut,'body_geometry_transform':'none_relative_to_frozen_new096_common','armor_geometry_transform':'one_shared096/094_from_native_raw_no_framefit_or_pose_deform','phase':'walk','time_start_s':nf['time_start_s'],'time_end_s':nf['time_end_s'],'runtime_verified':False,'semantic_full_armor_acceptance':False});total_frames+=1
previews=[]
for(key,k),im in sheets.items():
 q=P/f'reviews/XBW-walk-{key}-{k}-selection-v005.png';save(im,q,'new096_fourarmor_three_actualstates_bothdirections_static_source_candidate');previews.append({'armor_id':key,'kind':k,'path':str(q),'sha256':r.sha(q)})
q=P/'manifests/XBW-walk-four-armors-selection-candidate-v005.json';assert not q.exists();r.write(q,{'schema':'XBW-pose-specific-armor-source-candidate-v2','version':5,'clip':'walk','source_body_contract_path':str(newcp),'source_body_contract_sha256':r.sha(newcp),'prior_armor_contract_path':str(oldap),'prior_armor_contract_sha256':r.sha(oldap),'common_body':base['frames'],'frame_count':6,'canvas_px':[512,512],'armors':rows,'previews':previews,'draw_order':['body_far','armor_far','independent_weapon','body_support','armor_near','body_near'],'source_requests_reused':[118,119,120,121],'new_generation_calls':0,'armor_texture_count_new':48,'common_body_texture_count_reused':18,'shared_armor_raw_transform_scale':.96/.94,'all24pose_transform_is_same_root_centered_uniform':True,'actual_hand_overlap_pixels_after_guard':0,'total_extra_actual_new_hand_guard_mask_pixels':total_hand_cut,'runtime_verified':False,'footlock_certified':False,'semantic_full_armor_acceptance':False});r.archive(q,q.relative_to(P),'new096_actual_same_source_armor48_candidate_no_runtime_claim')
print({'candidate':str(q),'sha256':r.sha(q),'armor_PNGs':48,'pose_combinations':total_frames,'actual_hand_overlap':0,'extra_hand_guard_cut_mask_pixels':total_hand_cut,'generation_calls':0})
