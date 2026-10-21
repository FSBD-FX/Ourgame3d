"""Real native-art crop/matte/normalization and repeat QC; no raw-art drawing."""
from pathlib import Path
import importlib.util
import json
from PIL import Image,ImageChops,ImageStat

P=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('record',P/'production-record.py')
r=importlib.util.module_from_spec(s);s.loader.exec_module(r)
def save(im,path,status):
 if path.exists():raise ValueError('Prior version is immutable: '+str(path))
 im.save(path);r.archive(path,path.relative_to(P),status)

def main():
 man=r.read(P/'manifests/import-subset-v004.json')
 old=Path(man['layers'][1]['file']);mid=Image.open(old).convert('RGBA')
 pix=mid.load();removed=0
 # Alpha-only despill after resampling; targets magenta residue, adds no artwork.
 for y in range(mid.height):
  for x in range(mid.width):
   rr,g,b,a=pix[x,y]
   if a and rr>60 and b>60 and rr>g+15 and b>g+15:
    pix[x,y]=(0,0,0,0);removed+=1
 alpha=mid.getchannel('A');assert alpha.crop((0,323,1280,720)).getextrema()==(0,0)
 residue=sum(q[3]>0 and q[0]>60 and q[2]>60 and q[0]>q[1]+15 and q[2]>q[1]+15 for q in mid.getdata());assert residue==0
 mp=P/'processed/dungeon-mid-stage-1280x720-v004.png'
 save(mid,mp,'final_alpha_only_magenta_residue_cleanup_no_new_generation')
 m=man['layers'][1];m.update(file=str(mp),sha256=r.sha(mp),nontransparent_bbox_px=list(alpha.getbbox()),
  status='final_palette_safe_matte_candidate_pixel_qc_pass_pending_runtime',
  post_resample_magenta_residue_alpha_pixel_count=residue,
  supersedes_processed_file=str(old),superseded_reason='removed_lowalpha_magenta_residue_after_resample')
 m['normalization']['post_resample_alpha_cleanup']={'predicate':'A>0 and R>60 and B>60 and R>G+15 and B>G+15 -> alpha0','removed_pixels':removed,'adds_or_repaints_pixels':False}
 src=P/'raw/27-dungeon-stone-floor-v001.png';raw=Image.open(src).convert('RGB');assert raw.width==raw.height
 tile=raw.resize((512,512),Image.Resampling.LANCZOS).convert('RGBA')
 fp=P/'processed/dungeon-floor-tile-512-v001.png';save(tile,fp,'uniform_square_resample_stable_ground_material')
 rgb=tile.convert('RGB')
 def mae(a,b):return sum(ImageStat.Stat(ImageChops.difference(a,b)).mean)/3
 seams={'x_edge_mae_rgb':mae(rgb.crop((0,0,1,512)),rgb.crop((511,0,512,512))),
  'y_edge_mae_rgb':mae(rgb.crop((0,0,512,1)),rgb.crop((0,511,512,512))),
  'near_x_edge_adjacent_mae_rgb':mae(rgb.crop((0,0,1,512)),rgb.crop((1,0,2,512))),
  'near_y_edge_adjacent_mae_rgb':mae(rgb.crop((0,0,512,1)),rgb.crop((0,1,512,2)))}
 repeated=Image.new('RGBA',(1024,1024))
 for y in [0,512]:
  for x in [0,512]:repeated.alpha_composite(tile,(x,y))
 save(repeated,P/'reviews/floor-2x2-repeat-preview-v001.png','real_repeat_without_blend_or_generated_seam_repair')
 layer={'id':'floor','ue_asset_name':'T_RoomFloor_v001','ue_destination':'/Game/Production/RoomArt/v001/',
  'file':str(fp),'sha256':r.sha(fp),'source_file':str(src),'source_sha256':r.sha(src),
  'source_dimensions_px':list(raw.size),'normalized_dimensions_px':[512,512],
  'display_dimensions_px':[256,256],'display_dimensions_kind':'proposed_world_grid_skin_tile_not_fullcanvas',
  'normalization':{'method':'single_uniform_LANCZOS_square_resample','scale':512/raw.width,'crop_box_source_px':[0,0,raw.width,raw.height],'seam_blend_applied':False},
  'mode':'RGBA','alpha_extrema':list(tile.getchannel('A').getextrema()),'anchor':'world_grid_top_left','anchor_px':[0,0],
  'stage_floor_start_y':323,'render_order':-10,'scroll_factors':[1,1],
  'repeat':{'x':True,'y':True,'seamless_certified':False,'review_preview':str(P/'reviews/floor-2x2-repeat-preview-v001.png')},
  'runtime_zoom':'follow_existing_world_grid_not_parallax_plate','collision_role':'none_material_only',
  'source_request_number':27,'source_prompt':str(P/'prompts/27-repeat-stone-floor.txt'),
  'reference_files':next(e for e in r.read(r.LEDGER)['requests'] if e['request_number']==27)['references'],
  'repeat_qc':seams,'status':'stable_ground_material_candidate_repeat_visual_review_pending',
  'limitations':['no_collision_from_pixels','not_a_platform_or_terrain_chunk','existing_walkable_belt_bounds_remain_authority','seamless_not_assumed_from_prompt']}
 man['layers'].append(layer);man.update(version=5,previous_frozen_manifest=str(P/'manifests/import-subset-v004.json'))
 man['accounting'].update(cumulative_EV039_onward_requests=27,current_window_requested=3,lifetime_requests=51)
 man['limitations']=['three_background_material_layers_not_complete_map','no_scene_hooks_or_gameplay_geometry_changed','parallax_camera_bounds_and_zoom_require_runtime_review','floor_repeat_seams_need_runtime_material_check']
 dest=P/'manifests/import-subset-v005.json';r.write(dest,man);r.archive(dest,dest.relative_to(P),'frozen_far_finalmid_floor_candidate_contract')
 stage=Image.open(Path(man['layers'][0]['file'])).convert('RGBA');stage.alpha_composite(mid)
 floor=Image.new('RGBA',(1280,397))
 small=tile.resize((256,256),Image.Resampling.LANCZOS)
 for y in range(0,397,256):
  for x in range(0,1280,256):floor.alpha_composite(small,(x,y))
 stage.alpha_composite(floor,(0,323))
 save(stage,P/'reviews/far-mid-floor-composed-stage-preview-v001.png','finished_layer_composition_material_scale_proposal_not_runtime')
 checks=[]
 for e in man['layers']:
  checks.append({'id':e['id'],'sha_matches':r.sha(Path(e['file']))==e['sha256']})
 assert all(e['sha_matches'] for e in checks)
 print(json.dumps({'manifest':str(dest),'manifest_sha':r.sha(dest),'mid_sha':r.sha(mp),'floor_sha':r.sha(fp),'mid_residue_removed_after_resize':removed,'seams':seams,'source_hash_checks':checks},ensure_ascii=False))

if __name__=='__main__':main()
