"""Existing generate2dsprite matte, exact grid cells; no bbox fitting or pose change."""
from pathlib import Path
import argparse,importlib.util,json
from PIL import Image
P=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('record',P/'production-record.py');w=importlib.util.module_from_spec(s);s.loader.exec_module(w);r=w.r
sp=Path('C:/Users/22499/.codex/skills/generate2dsprite/scripts/generate2dsprite.py');s=importlib.util.spec_from_file_location('skill_processor',sp);skill=importlib.util.module_from_spec(s);s.loader.exec_module(skill)
def main(number,columns,count):
 ledger=r.read(r.LEDGER);e=next(x for x in ledger['requests'] if x['request_number']==number);src=Path(e['raw_path']);assert r.sha(src)==e['sha256'] and src.parent.parent==P
 im=Image.open(src).convert('RGBA');expected=(columns*512,((count+columns-1)//columns)*512);assert im.size==expected,('geometry_mismatch',im.size,expected)
 out=P/f'processed/call{number}-fixed-canvas-v001';assert not out.exists();out.mkdir(parents=True)
 frames=[];sheet=Image.new('RGBA',expected,(0,0,0,0))
 for i in range(count):
  x,y=(i%columns)*512,(i//columns)*512;raw=im.crop((x,y,x+512,y+512));cell=skill.clean_edges(skill.remove_bg_magenta(raw.copy(),threshold=90,edge_threshold=140),depth=3)
  erased=sum(b[3]>0 and a[3]==0 and not(b[0]>b[1]+30 and b[2]>b[1]+30) for b,a in zip(raw.get_flattened_data(),cell.get_flattened_data()))
  assert cell.getchannel('A').getbbox() and cell.getchannel('A').getextrema()==(0,255)
  corners=[cell.getpixel(p)[3] for p in [(0,0),(511,0),(0,511),(511,511)]];assert corners==[0]*4
  q=out/f'frame-{i}.png';cell.save(q);r.archive(q,q.relative_to(P),'actual_native_XBW_costume_edit_cell_not_layer_or_pose_acceptance');sheet.alpha_composite(cell,(x,y))
  frames.append({'index':i,'path':str(q),'sha256':r.sha(q),'canvas_px':[512,512],'mode':'RGBA','alpha_extrema':[0,255],'corner_alpha':corners,'bbox_px':list(cell.getchannel('A').getbbox()),'non_chroma_erased_pixels':erased,'source_box_px':[x,y,x+512,y+512]})
 q=out/'sheet-transparent.png';sheet.save(q);r.archive(q,q.relative_to(P),'actual_native_costume_grid_matte_only')
 report=out/'processing-report.json';r.write(report,{'schema':'XBW-costume-fixed-canvas-matte-v1','request_number':number,'raw_path':str(src),'raw_sha256':r.sha(src),'native_size_px':list(im.size),'canvas_px':[512,512],'grid_columns':columns,'frame_count':count,'frames':frames,'processor_path':str(sp),'processor_sha256':r.sha(sp),'matte':'remove_bg_magenta(90,140)+clean_edges(3)','no_geometry_transform':True,'bbox_fit':False,'material_retention_pass':all(x['non_chroma_erased_pixels']==0 for x in frames),'source_semantic_layer_pass':False,'runtime_verified':False});r.archive(report,report.relative_to(P),'fixed_canvas_actual_matte_pixel_report_not_costume_fit_acceptance')
 e.setdefault('processing_revisions',[]).append({'report':str(report),'sha256':r.sha(report),'no_geometry_transform':True});r.write(r.LEDGER,ledger)
 print(json.dumps({'request':number,'frames':count,'material_erased':[x['non_chroma_erased_pixels'] for x in frames],'bbox':[x['bbox_px'] for x in frames]}))
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--number',type=int,required=True);a.add_argument('--columns',type=int,default=3);a.add_argument('--count',type=int,default=6);v=a.parse_args();main(v.number,v.columns,v.count)
