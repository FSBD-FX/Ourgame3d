"""Retain native square raw; explicit one whole-grid uniform normalization only."""
from pathlib import Path
import argparse,importlib.util,json
from PIL import Image
P=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('record',P/'production-record.py');w=importlib.util.module_from_spec(s);s.loader.exec_module(w);r=w.r
sp=Path('C:/Users/22499/.codex/skills/generate2dsprite/scripts/generate2dsprite.py');s=importlib.util.spec_from_file_location('skill_processor',sp);skill=importlib.util.module_from_spec(s);s.loader.exec_module(skill)
def main(number):
 ledger=r.read(r.LEDGER);e=next(x for x in ledger['requests'] if x['request_number']==number);src=Path(e['raw_path']);assert r.sha(src)==e['sha256'] and src.parent.parent==P
 raw=Image.open(src).convert('RGBA');assert raw.width==raw.height and raw.width%2==0
 out=P/f'processed/call{number}-fixed-canvas-v002';assert not out.exists();out.mkdir(parents=True)
 matte=skill.clean_edges(skill.remove_bg_magenta(raw.copy(),threshold=90,edge_threshold=140),depth=3)
 erased=sum(b[3]>0 and a[3]==0 and not(b[0]>b[1]+30 and b[2]>b[1]+30) for b,a in zip(raw.get_flattened_data(),matte.get_flattened_data()))
 q=out/'matte-native.png';matte.save(q);r.archive(q,q.relative_to(P),'native_square_costume_matte_before_any_normalization')
 normalized=matte.resize((1024,1024),Image.Resampling.LANCZOS) if matte.size!=(1024,1024) else matte.copy()
 px=normalized.load();chroma_removed=0
 for y in range(1024):
  for x in range(1024):
   rr,gg,bb,aa=px[x,y]
   if rr>gg+30 and bb>gg+30 and aa:px[x,y]=(0,0,0,0);chroma_removed+=1
   elif not aa:px[x,y]=(0,0,0,0)
 frames=[]
 for i in range(4):
  x,y=(i%2)*512,(i//2)*512;cell=normalized.crop((x,y,x+512,y+512));assert cell.getchannel('A').getbbox() and cell.getchannel('A').getextrema()==(0,255)
  corners=[cell.getpixel(p)[3] for p in[(0,0),(511,0),(0,511),(511,511)]];assert corners==[0]*4
  q=out/f'frame-{i}.png';cell.save(q);r.archive(q,q.relative_to(P),'whole_grid_uniform_normalized_native_costume_cell_not_pose_refit')
  frames.append({'index':i,'path':str(q),'sha256':r.sha(q),'canvas_px':[512,512],'mode':'RGBA','alpha_extrema':[0,255],'corner_alpha':corners,'bbox_px':list(cell.getchannel('A').getbbox()),'no_per_frame_scale_translation_or_bbox_fit':True})
 q=out/'sheet-transparent.png';normalized.save(q);r.archive(q,q.relative_to(P),'one_whole_grid_uniform_normalization_not_per_pose_fit')
 report=out/'processing-report.json';r.write(report,{'schema':'XBW-square-grid-uniform-matte-v2','request_number':number,'raw_path':str(src),'raw_sha256':r.sha(src),'native_size_px':list(raw.size),'output_grid_size_px':[1024,1024],'shared_whole_grid_scale':1024/raw.width,'resample':'one_whole_canvas_LANCZOS_only','native_cell_size_px':[raw.width//2]*2,'canvas_px':[512,512],'frames':frames,'processor_path':str(sp),'processor_sha256':r.sha(sp),'matte':'remove_bg_magenta(90,140)+clean_edges(3); post_resample_chroma_selection_only','non_chroma_erased_native_pixels':erased,'post_resample_chroma_pixels_removed':chroma_removed,'per_frame_geometry_transform':'none','bbox_fit':False,'static_alpha_pass':True,'material_retention_pass':erased==0,'runtime_verified':False});r.archive(report,report.relative_to(P),'explicit_actual_native_to_output_shared_scale_and_pixel_report')
 e.setdefault('processing_revisions',[]).append({'report':str(report),'sha256':r.sha(report),'mode':'shared_whole_square_grid_uniform_scale','per_frame_refit':False});r.write(r.LEDGER,ledger)
 print(json.dumps({'request':number,'native_px':list(raw.size),'whole_grid_scale':1024/raw.width,'frames':4,'erased_non_chroma':erased,'bbox':[f['bbox_px'] for f in frames]}))
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--number',type=int,required=True);v=a.parse_args();main(v.number)
