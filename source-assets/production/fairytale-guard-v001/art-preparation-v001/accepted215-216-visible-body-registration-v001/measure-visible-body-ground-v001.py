from pathlib import Path
import hashlib,json,math
from PIL import Image
import numpy as np
ROOT=Path('F:/Ourgame/source-assets/production/fairytale-guard-v001/art-preparation-v001')
OUT=ROOT/'accepted215-216-visible-body-registration-v001'
SRC=ROOT/'axe215-216-extraction-v001'
SPEC={
'axe-active4':[
([205,120,300,175],[[80,405,195,470],[220,405,345,470]],[[326,249],[367,171]],[[342,217],[350,198]]),
([185,140,290,200],[[48,405,158,470],[210,405,327,470]],[[245,325],[347,335]],[[284,328],[306,330]]),
([220,150,305,200],[[54,390,160,438],[208,390,328,438]],[[245,327],[342,368]],[[286,344],[300,349]]),
([225,150,315,205],[[63,390,168,438],[225,390,340,438]],[[263,326],[345,365]],[[290,339],[312,348]])],
'axe-recovery4':[
([190,120,330,175],[[48,405,178,470],[210,405,345,470]],[[155,356],[345,363]],[[213,356],[285,358]]),
([215,130,345,200],[[70,405,198,470],[215,405,347,470]],[[183,376],[336,385]],[[237,379],[288,381]]),
([190,95,300,155],[[95,405,225,470],[247,405,380,470]],[[186,324],[328,295]],[[236,320],[275,305]]),
([200,95,315,150],[[90,405,225,470],[247,405,380,470]],[[177,350],[319,297]],[[226,332],[265,320]])]}
def pin(p):
 b=p.read_bytes();return {'path':p.as_posix(),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def pixel(a,p):return {'artist_visible_xy':p,'actual_RGBA':a[p[1],p[0]].tolist(),'uncertainty_px':4,'not_bone_or_hidden_shaft_center':True}
results={}
for state,frames in SPEC.items():
 rows=[]
 for i,(cr,feet,fists,axis) in enumerate(frames):
  p=SRC/f'run-{state}-shared-HD-v001/curated/frame-{i}.png';a=np.array(Image.open(p).convert('RGBA'))
  x0,y0,x1,y1=cr;ys,xs=np.where(a[y0:y1,x0:x1,3]>=128);crown=int(ys.min()+y0)
  ff=[]
  for rect in feet:
   x0,y0,x1,y1=rect;ys,xs=np.where(a[y0:y1,x0:x1,3]>=128);by=int(ys.max()+y0)
   band=a[by-3:by+1,x0:x1,3].astype(float);pos=np.arange(x0,x1)[None,:]
   cx=float((band*pos).sum()/band.sum());corexs=np.where((band>=128).any(axis=0))[0]+x0
   ff.append({'artist_visible_shoe_ROI_xyxy':rect,'core_bottom_y':by,'bottom4row_core_xrange':[int(corexs.min()),int(corexs.max())],'bottom_band_alpha_centroid_x':cx})
  floor=max(f['core_bottom_y'] for f in ff)+1;mid=sum(f['bottom_band_alpha_centroid_x'] for f in ff)/2
  ap=[pixel(a,p) for p in axis];fp=[pixel(a,p) for p in fists]
  for t in ap+fp:assert t['actual_RGBA'][3]==255
  v=np.array(axis[1],float)-np.array(axis[0],float);v=v/np.linalg.norm(v)
  bbox=Image.fromarray(a[:,:,3]).getbbox();safe=[bbox[0],bbox[1],512-bbox[2],512-bbox[3]]
  rows.append({'frame':i,'source':pin(p),'actual_View':'Root and worker actual each frame after Root E380 two-copy SHA zero difference retention.','body_only_crown_ROI_xyxy':cr,'visible_body_crown_core_top_y':crown,'near_far_shoes':ff,'visible_body_crown_to_near_lowest_sole_extent_px':floor-crown,'visible_paired_shoe_midpoint_x':mid,'artist_display_ground_pivot_xy':[round(mid),floor],'floor_reference':'Lowest visible shoe core bottom + 1; not whole axe alpha bbox. Far sole may be slightly higher in shallow elevated camera.','physical_near_butt_fist_surface':fp[0],'physical_far_head_fist_surface':fp[1],'visible_wood_surface_axis_samples_buttward_to_headward':ap,'artist_projected_shaft_direction_butt_to_head_xy':v.tolist(),'axis_limit':'Direction from two visible wood-surface artist points, not hidden grip, bone, physical weapon axis or exact shaft center.','alpha_bbox_not_body_height':list(bbox),'safe_transparent_canvas_margins_ltrb':safe,'actual_component_review':'Complete whole body and fixed axe; no foreign neighbor component or visible crop. Near moss shoulder→foreground arm→buttward fist, far arm→headward fist remain.','source_pixels_unchanged':True})
 basisframe=0 if state=='axe-active4' else 3;basis=rows[basisframe]['visible_body_crown_to_near_lowest_sole_extent_px'];scale=100.8/basis
 doc={'schema':'Guard215216-visible-body-row-registration-proposal-v001','state':state,'status':'Source pose candidate and measured registration proposal only; Root trial lock/runtime/full unit/final user acceptance pending.','source_index':pin(SRC/f'{state}-six-curated-source-index-v001.json'),'source_layout_status':'Native equal-width nominal slot layout FAILED and remains failed. Independent complete component curated poses only; no direct-strip atlas admission.','rows':rows,'standing_equivalent_basis_frame':basisframe,'standing_equivalent_body_extent_px':basis,'basis_reason':'Active0 high-ready beginning is least compressed actual body pose; Recovery3 returns toward accepted Ready. Both are visible-body artist comparison bases, not a skeletal physical standing height. Raised axe/head and lowered blade never define body crown or floor.','body_display_height_px_candidate':100.8,'ONE_row_display_px_per_source_px':scale,'ONE_row_canvas_display_px':[512*scale,512*scale],'perframe_ground_pivot_candidates':[x['artist_display_ground_pivot_xy'] for x in rows],'perframe_display_body_height_diagnostic':[x['visible_body_crown_to_near_lowest_sole_extent_px']*scale for x in rows],'height_normalization_perframe':False,'registration_strategy':'One row density. Use actual perframe visible shoe-ground pivots to compensate whole-axe bbox centering and blade-below-sole offsets; equivalent integer canvas translation is possible without changing original pixels. Do not use one 256 center or one alpha-bottom464 for all frames.','claim_limits':['No inferred wristbone, hidden shaft center, COM or occluded foot.','Source proportions/perspective differ naturally and possibly artistically across native rows; a body-height basis alone does not prove head-size identity.','Actual native scene joins Ready→Windup→Active→Recovery→Ready must be viewed; no foot-lock or zero-pop claim.','No kernel timing, movement, actor XY/Z or accepted input path changes.']}
 f=OUT/f'{state}-body-crown-shoe-floor-registration-v001.json';f.write_text(json.dumps(doc,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');results[state]=doc;print(json.dumps(pin(f)))
a=results['axe-active4'];r=results['axe-recovery4'];ar=a['rows'][3];rr=r['rows'][0]
join={'schema':'Guard215216-visible-grips-join-limit-review-v001','retention_and_review':'E380 both copies SHA zero; Root and worker all eight actual Views. Ready209 frame0 and Windup212 frame5 re-opened only to assess new joins, not repeat old art acceptance.','all_eight_source_pose_review':'Complete body+axe; near moss shoulder arm remains buttward, far arm remains headward. Active is one forward-down sweep, no hand swap or extra strike; Recovery quiet return.','registration_files':[pin(OUT/'axe-active4-body-crown-shoe-floor-registration-v001.json'),pin(OUT/'axe-recovery4-body-crown-shoe-floor-registration-v001.json')],'Active3_to_Recovery0':{'Active3_visible_axis_xy':ar['artist_projected_shaft_direction_butt_to_head_xy'],'Recovery0_visible_axis_xy':rr['artist_projected_shaft_direction_butt_to_head_xy'],'axis_angle_difference_degrees':math.degrees(math.acos(float(np.clip(np.dot(ar['artist_projected_shaft_direction_butt_to_head_xy'],rr['artist_projected_shaft_direction_butt_to_head_xy']),-1,1)))),'body_display_crown_to_floor_px_proposed':[a['perframe_display_body_height_diagnostic'][3],r['perframe_display_body_height_diagnostic'][0]],'crown_height_change_px_proposed':r['perframe_display_body_height_diagnostic'][0]-a['perframe_display_body_height_diagnostic'][3],'interpretation':'Active3 low diagonal-down axe and compressed body → Recovery0 near-horizontal axe and taller but forward-leaning body. This is a pose discontinuity candidate to review in native timing, not zero-pop. Do not conceal by perframe scaling, source painting or actor XY movement.'},'Recovery3_to_Ready0':'Similar two-hand low diagonal held-axe stance and near/far ownership. Native rows have different body pixel density; ONE row standing-equivalent registration can match intended height only, head/weapon proportion/foot position still require native scene trial.','Windup212_5_to_Active215_0':'Both retain raised-head-upper-right starting swing ownership but different arm projection and body presentation; actual source grip ownership passes, dynamic continuity awaits native scene.','raw_layout_failure_remains':True,'new_visual_media_generated':False,'all_actual_source_pixels_unchanged':True,'final_acceptance':False}
f=OUT/'eight-pose-actual-review-and-A3-R0-join-limits-v001.json';f.write_text(json.dumps(join,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(pin(f)))
