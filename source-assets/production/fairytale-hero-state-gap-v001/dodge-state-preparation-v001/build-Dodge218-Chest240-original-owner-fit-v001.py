"""New candidate only: reuse proven deterministic builder with explicit pinned edits.
Old234 source, original owner controls and every prior freeze stay unchanged.
"""
from pathlib import Path
import ast,hashlib,json
HERE=Path(__file__).resolve().parent
SOURCE=HERE/'build-Dodge218-LGT234-236-SWD-limited-fit-v001.py'
source=SOURCE.read_text(encoding='utf-8-sig');changes=[]
def edit(before,after):
 global source
 assert source.count(before)==1,(before,source.count(before))
 source=source.replace(before,after);changes.append({'before':before,'after':after,'count':1})
edit("OUT=HERE/'LGT234-236-own-source-integer-fit-v001'","OUT=HERE/'LGT240-235-236-original-owner-integer-fit-v001'")
edit("MEDIA=ROOT/'过程图稿与视频/2026-10-18_钟盔Dodge218棕皮三层军剑有限试拼_v001'","MEDIA=ROOT/'过程图稿与视频/2026-10-18_钟盔Dodge218胸衣240原分区四相军剑试拼_v001'")
edit("ARMOR={'Chest':('chest',234,477),'ShoulderNear':('nearshoulder',235,478),'ShoulderFar':('farshoulder',236,480)}","ARMOR={'Chest':('chest',240,501),'ShoulderNear':('nearshoulder',235,478),'ShoulderFar':('farshoulder',236,480)}")
edit('CHEST_A=[[265,286],[262,289],[261,287],[266,285]]','CHEST_A=[[267,282],[264,284],[267,283],[267,282]]')
edit('collar=poly_mask(COLLARS[i])&alive','collar=np.zeros((512,512),bool) # original helmet-only owner; no added gray torso/collar overlay')
edit("if owner=='HelmetForeground':m|=collar","if owner=='HelmetForeground':pass # intentionally no gray collar/torso union")
edit('hole=holes(original_ch[:,:,3]>=128);hy,hx=np.where(hole)','hole,neck_hole,hole_records=select_separate_actual_arm_and_neck_holes(holes(original_ch[:,:,3]>=128));hy,hx=np.where(hole)')
edit("'actual_true_hole_pixels':int(hole.sum()),","'actual_true_armhole_pixels':int(hole.sum()),'actual_true_neckhole_pixels':int(neck_hole.sum()),'separate_closed_hole_records':hole_records,'all_holes_centroid_averaged':False,'neck_aperture_exterior_connected':False,")
edit("'opaque_neck_prompt_deviation_preserved':True","'neck_and_arm_true_transparent_apertures_actual':True,'dark_neck_ROI_includes_original_outline_not_opaque_backing':True")
edit("'HelmetForeground_includes_actual_visible_gray_collar_only'","'HelmetForeground_original_helmet_only_no_added_gray_torso'")
edit("'artist_polygon':COLLARS[i]","'additional_gray_collar_polygon':None")
edit("'source_neck_prompt_failure'","'source_aperture_status'")
edit("'Chest234 still has opaque black neck interior. Original request and source failure preserved; proposed original gray collar/helmet foreground MAY legally cover it, subject to actual full/closeup review. This is not declaring original negative-aperture spec passed.'","'Chest240 has separate true transparent arm/neck holes and no234 opaque backing. Neck is a closed negative-space loop rather than an exterior-connected U-cut; preserve this construction fact. Original234 rejection remains. No added gray torso/collar foreground is used; actual pose geometry still requires review.'")
edit("'Dodge218-LGT234-236-own-source-integer-fit-candidate-v001'","'Dodge218-LGT240-235-236-original-owner-integer-fit-candidate-v001'")
edit("'Dodge218-LGT234-236-own-five-layers-SWD050-integer-fit-candidate-v001.json'","'Dodge218-Chest240-Near235-Far236-original-owner-SWD050-integer-fit-candidate-v001.json'")
edit("'Dodge-LGT-SWD-limited-sourcefit-freeze-v001.json'","'Dodge-LGT240-original-owner-sourcefit-freeze-v001.json'")
edit("torso=Image.new('RGB',(1600,650)","torso=Image.new('RGB',(2560,488)")
edit('.resize((400,600),Image.Resampling.NEAREST);torso.paste(torso_crop,(400*i,40),torso_crop);dt.text((400*i+8,8)', '.resize((640,440),Image.Resampling.NEAREST);torso.paste(torso_crop,(640*i,40),torso_crop);dt.text((640*i+8,8)')
edit("f'Dodge{i}: own collar partition'","f'Dodge{i}: original helmet-only partition'")
edit("'presentation/Dodge4-own-collar-five-partitions.png'","'presentation/Dodge4-original-helmet-only-five-partitions.png'")
edit("'newmedia_View':False},ensure_ascii=False,indent=2))","'newmedia_View':False,'four_armhole_to_belt_actual_vectors':[r['armor_integer_fits']['Chest']['actual_armhole_to_buckle_vector_xy'] for r in rows],'four_finite_best_integer_max_errors':[r['armor_integer_fits']['Chest']['finite_grid_best_max_residual_source_px'] for r in rows]},ensure_ascii=False,indent=2))")

helpers='''
def select_separate_actual_arm_and_neck_holes(closed):
 from collections import deque
 remain=closed.copy();parts=[]
 while remain.any():
  sy,sx=np.argwhere(remain)[0];q=deque([(int(sy),int(sx))]);remain[sy,sx]=False;coords=[]
  while q:
   y,x=q.popleft();coords.append((x,y))
   for ny,nx in [(y-1,x),(y+1,x),(y,x-1),(y,x+1)]:
    if 0<=ny<512 and 0<=nx<512 and remain[ny,nx]:remain[ny,nx]=False;q.append((ny,nx))
  points=np.array(coords);mask=np.zeros((512,512),bool);mask[points[:,1],points[:,0]]=True
  parts.append({'area':len(points),'bbox':bbox(mask),'centroid':points.mean(axis=0).tolist(),'mask':mask})
 significant=sorted([r for r in parts if r['area']>=32],key=lambda r:-r['area'])
 assert len(significant)==2
 arm,neck=significant;assert arm['centroid'][0]<neck['centroid'][0]
 records=[]
 for label,r in [('actual_near_arm_aperture',arm),('actual_neck_aperture',neck)]:records.append({'role':label,'area':r['area'],'bbox':r['bbox'],'centroid_xy':r['centroid'],'authority':'Actual E501-viewed hole contour; separate connected closed background component, no averaged twohole centroid/ROI filling.'})
 for r in parts:
  if r['area']<32:records.append({'role':'small_closed_interstice_not_arm_or_neck','area':r['area'],'bbox':r['bbox'],'centroid_xy':r['centroid']})
 return arm['mask'],neck['mask'],records
'''
edit('audit=read(AUDIT);old_rows=',helpers+'\naudit=read(AUDIT);old_rows=')
finite='''
 actual_vector=np.array(CHEST_A[i],float)-np.array(center)
 target_vector=np.array(CHEST_B[i],float)-np.array(VISIBLE_ARM_JUNCTION_B[i],float)
 d_belt=np.array([dx,dy],float);d_hole=np.array(VISIBLE_ARM_JUNCTION_B[i],float)-center
 fxx,fyy=np.meshgrid(np.arange(-80,1),np.arange(0,101));ds=np.column_stack([fxx.ravel(),fyy.ravel()])
 be=np.linalg.norm(ds-d_belt,axis=1);he=np.linalg.norm(ds-d_hole,axis=1);obj=np.maximum(be,he);best_index=int(np.argmin(obj));best_delta=ds[best_index].tolist()
 fits['Chest'].update({'actual_armhole_to_buckle_vector_xy':actual_vector.tolist(),'target_visible_junction_to_buckle_vector_xy':target_vector.tolist(),'two_target_translation_invariant_discrepancy_xy':(target_vector-actual_vector).tolist(),'any_translation_minimax_lower_bound_source_px':float(np.linalg.norm(target_vector-actual_vector)/2),'finite_grid_domain':{'dx':[-80,0],'dy':[0,100],'integer_count':len(ds)},'finite_grid_best_integer_delta_xy':best_delta,'finite_grid_best_max_residual_source_px':float(obj[best_index]),'finite_grid_best_belt_residual_xy':(np.array(CHEST_A[i])+best_delta-CHEST_B[i]).tolist(),'finite_grid_best_junction_residual_xy':(np.array(center)+best_delta-VISIBLE_ARM_JUNCTION_B[i]).tolist()})
'''
edit(" fits['ShoulderFar']['core_pixels_outside_original_body']=int(np.count_nonzero(far_core&~(a[:,:,3]>=128)))",finite+"\n fits['ShoulderFar']['core_pixels_outside_original_body']=int(np.count_nonzero(far_core&~(a[:,:,3]>=128)))")
alternatives='''
 if i in [1,2]:
  alt=Image.new('RGBA',(512,512));best_ch=translate(original_ch,best_delta[0],best_delta[1])
  for name,value in stack:alt=Image.alpha_composite(alt,Image.fromarray(best_ch if name=='Chest' else value))
  altp=save(f'finite-controls/phase-{i}-actual-best-integer-original-owner.png',alt)
  fits['Chest']['finite_grid_best_whole_control']=pin(altp)
'''
edit(" swd_whole=Image.new('RGBA',(512,512))",alternatives+"\n swd_whole=Image.new('RGBA',(512,512))")
control_sheet='''
controls=Image.new('RGB',(1280,488),(45,48,54));cd=ImageDraw.Draw(controls)
for col,i in enumerate([1,2]):
 im=Image.open(OUT/f'finite-controls/phase-{i}-actual-best-integer-original-owner.png').convert('RGBA');y0=255 if i==1 else 200;crop=im.crop((100,y0,420,y0+220)).resize((640,440),Image.Resampling.NEAREST);controls.paste(crop,(640*col,40),crop);fr=rows[i]['armor_integer_fits']['Chest'];cd.text((640*col+8,9),f'Dodge{i} actualbest{fr["finite_grid_best_integer_delta_xy"]} / uniform2x',font=font(20),fill='white')
save('presentation/Dodge1-2-Chest240-best-integer-original-owner-controls-UNIFORM2x.png',controls)
'''
edit("jc=Image.new('RGBA',(1280,640)",control_sheet+"\njc=Image.new('RGBA',(1280,640)")
provenance="""
write('Chest240-original-owner-adapter-provenance-v001.json',ADAPTER_PROVENANCE)
"""
edit("freeze=write('Dodge-LGT240-original-owner-sourcefit-freeze-v001.json'",provenance+"\nfreeze=write('Dodge-LGT240-original-owner-sourcefit-freeze-v001.json'")

new_handoff='''Dodge218自身原helmet-only五分区 + Chest240/Near235/Far236 +独立军剑.50四相有限配准，全部新媒体未View，先RootE。

原234及错误灰带owner候选冻结全保留；本候选不加任何graycollar/torso前景。实际218自身RGBA五分区排他重构完全相等，只有已Root审过的自身NearHand3边界与外指侧作者Grip，Axis/.50保持。12甲片仅整数平移，现240独立sharedscale=.3021148036253776/128x100，原512门和motionwarning .005保留。

240每相有两个真实透明孔，必须按4-connected闭背景分别登记：near-arm aperture与neck aperture，不平均两孔/不取ROI全域。现neck透明孔仍是闭loop而非提示里的外连U口，保留构造事实；不存在234的opaque填黑内面。完整4相以实际扣A→body扣B对齐，并记录真实armhole到buckle矢量、可见袖口target差及8181个integerdelta的最佳两目标残差。1/2另有最佳整数对照，不自动宣称sourcefit通过。

416→72/四实际鞋Root提案全行常量，未逐相归一。20body+12armor只是未准入候选；原Sword复用。无actualSource/Content/UE/native/import，TrialAllowed=false。新等比torso保持320x220→640x440；finite400ms4frameMP4和无loopGIF只离线审图。Readyjoin仍有姿态/握点变化，非zeroPop/native验收。
'''
class MetadataFix(ast.NodeTransformer):
 def visit_Call(self,node):
  self.generic_visit(node)
  if isinstance(node.func,ast.Name) and node.func.id=='write' and len(node.args)>1 and isinstance(node.args[0],ast.Constant) and node.args[0].value=='HANDOFF.md':node.args[1]=ast.Constant(new_handoff)
  return node
 def visit_Dict(self,node):
  self.generic_visit(node)
  for i,k in enumerate(node.keys):
   if isinstance(k,ast.Constant) and k.value=='source_preservation':node.values[i]=ast.Constant('All5bodylayers copy own218RGBA with exclusive exact reconstruction; ORIGINAL HELMET-ONLY owner, no added gray torso/collar. Chest240/Near235/Far236 only integer translated; SWD only rigid artist .50. No painting, erasure, fake lining, WholeBody BodyRest, Ready/Hurt mask reuse or perpose scale.')
   if isinstance(k,ast.Constant) and k.value=='topic' and isinstance(node.values[i],ast.Constant):node.values[i]=ast.Constant('钟盔Dodge218胸衣240原分区四相军剑试拼')
  return node
tree=ast.fix_missing_locations(MetadataFix().visit(ast.parse(source)))
provenance={'schema':'Chest240-original-owner-explicit-builder-adapter-v001','source_builder':{'path':SOURCE.as_posix(),'bytes':SOURCE.stat().st_size,'sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest()},'explicit_changes':changes,'old_builder_and_frozen_candidates_modified':False,'source_body_pixels_redrawn':False,'gray_collar_union_disabled_all4':True,'arm_neck_holes_separate_connected_components':True,'metadata_and_uniform_presentation_corrections_explicit':True}
scope={'__file__':str(Path(__file__).resolve()),'__name__':'Chest240_original_owner_sourcefit','ADAPTER_PROVENANCE':provenance}
exec(compile(tree,str(Path(__file__).resolve()),'exec'),scope)
