"""Existing skill matte + exact canvas cells. No bbox fit or component centering."""
from pathlib import Path
import argparse
import importlib.util
from PIL import Image
P=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('record',P/'production-record.py')
r=importlib.util.module_from_spec(s);s.loader.exec_module(r)
skill_path=Path('C:/Users/22499/.codex/skills/generate2dsprite/scripts/generate2dsprite.py')
s=importlib.util.spec_from_file_location('skill_processor',skill_path)
skill=importlib.util.module_from_spec(s);s.loader.exec_module(skill)

def process(number,revision,threshold,edge_threshold):
 ledger=r.read(r.LEDGER);entry=next(e for e in ledger['requests'] if e['request_number']==number)
 source=Path(entry['raw_path']);assert source.parent.parent==P and r.sha(source)==entry['sha256']
 out=P/'processed'/f'call{number:02}-fixed-canvas-v{revision:03}'
 if out.exists():raise ValueError('No output overwrite')
 im=Image.open(source).convert('RGBA');assert im.size==(1536,1024),'Reject geometry change; no silent resize'
 out.mkdir();atlas=Image.new('RGBA',im.size,(0,0,0,0));frames=[]
 for i in range(6):
  x=(i%3)*512;y=(i//3)*512
  rawcell=im.crop((x,y,x+512,y+512))
  cell=skill.remove_bg_magenta(rawcell.copy(),threshold=threshold,edge_threshold=edge_threshold)
  cell=skill.clean_edges(cell,depth=3)
  alpha=cell.getchannel('A');corners=[cell.getpixel(pt)[3] for pt in [(0,0),(511,0),(0,511),(511,511)]]
  opaque=[px for px in cell.get_flattened_data() if px[3]>=128]
  bad=sum(px[0]>180 and px[2]>150 and px[1]<120 for px in opaque)
  # Color retention is separate from mere alpha validity: neutral grey steel and
  # brown leather are not magenta and must not be flood-erased through AA gaps.
  erased_non_chroma=sum(1 for before,after in zip(rawcell.get_flattened_data(),cell.get_flattened_data())
   if before[3]>0 and after[3]==0 and not (before[0]>before[1]+30 and before[2]>before[1]+30))
  assert alpha.getbbox() and alpha.getextrema()==(0,255) and corners==[0,0,0,0]
  assert bad/max(1,len(opaque))<.001
  f=out/f'frame-{i}.png';cell.save(f);atlas.alpha_composite(cell,(x,y))
  frames.append({'index':i,'path':str(f),'sha256':r.sha(f),'canvas':[512,512],'mode':'RGBA',
   'alpha_extrema':list(alpha.getextrema()),'corner_alpha':corners,'bbox':list(alpha.getbbox()),
   'opaque_magenta_fraction':bad/max(1,len(opaque)),'source_box':[x,y,x+512,y+512],
   'erased_non_chroma_pixels':erased_non_chroma,
   'source_to_output_scale':1.0,'translation':[0,0],'bbox_fit_applied':False})
 q=out/'sheet-transparent.png';atlas.save(q)
 report={'schema':'fixed_canvas_skill_matte_v1','request_number':number,'source':str(source),
  'source_sha256':r.sha(source),'native_size':[1536,1024],'cell':[512,512],'frames':frames,
  'matte_function':f'generate2dsprite.remove_bg_magenta({threshold},{edge_threshold})+clean_edges(3)',
  'processor_script':str(skill_path),'processor_script_sha256':r.sha(skill_path),
  'no_geometry_transform':True,'all_parts_kept_not_largest_component':True,
  'static_pixels_pass':True,'material_retention_pass':all(f['erased_non_chroma_pixels']==0 for f in frames),
  'semantic_layer_or_fit_accepted':False,'runtime_verified':False}
 q=out/'fixed-canvas-report.json';r.write(q,report)
 for f in sorted(out.iterdir()):
  if f.is_file():r.archive(f,Path('processed')/out.name/f.name,'real_fixed_canvas_matte_not_semantic_layer_acceptance')
 entry.setdefault('processing_revisions',[]).append({'report':str(q),'sha256':r.sha(q),'mode':'fixed_canvas_no_alpha_centering','static_pixels_pass':True})
 r.write(r.LEDGER,ledger)
 print({'number':number,'revision':revision,'real_frames':6,'pixel_pass':True,
  'material_retention_pass':report['material_retention_pass'],
  'erased_non_chroma':[f['erased_non_chroma_pixels'] for f in frames],'bbox':[f['bbox'] for f in frames]})

if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--numbers',nargs='+',type=int,required=True)
 ap.add_argument('--revision',type=int,default=2);ap.add_argument('--threshold',type=int,default=90)
 ap.add_argument('--edge-threshold',type=int,default=140);a=ap.parse_args()
 for n in a.numbers:process(n,a.revision,a.threshold,a.edge_threshold)
