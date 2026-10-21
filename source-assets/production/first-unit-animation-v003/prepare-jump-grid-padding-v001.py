"""Layout-only calibration: pad native 443px cells, never resize any sprite pixel."""
from pathlib import Path
import importlib.util
import json
import subprocess
import sys
from PIL import Image
P=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('record',P/'production-record.py')
r=importlib.util.module_from_spec(s);s.loader.exec_module(r)

def main():
 source=P/'raw/34-round-knight-jump-family-body-v003.png'
 derived=P/'derived/34-jump-512cell-padding-v001.png'
 out=P/'processed/round-knight-jump-family-padded-v001'
 if derived.exists() or out.exists():raise ValueError('Do not overwrite calibration evidence')
 im=Image.open(source).convert('RGB');assert im.size==(1774,887)
 # Match the prior processor's integer source boxes exactly. Verify discarded
 # trailing columns/row are only background, not character pixels.
 discarded=[im.getpixel((x,y)) for y in range(887) for x in range(1774) if x>=1772 or y>=886]
 assert all(px[0]>=230 and px[2]>=230 and px[1]<=40 for px in discarded)
 canvas=Image.new('RGB',(2048,1024),(255,0,255));cells=[]
 for row in range(2):
  for col in range(4):
   box=[col*443,row*443,(col+1)*443,(row+1)*443]
   pos=[col*512+34,row*512+34]
   canvas.paste(im.crop(tuple(box)),tuple(pos))
   assert canvas.crop((pos[0],pos[1],pos[0]+443,pos[1]+443)).tobytes()==im.crop(tuple(box)).tobytes()
   cells.append({'source_box':box,'destination_xy':pos,'scale':1.0,'padding_left_top':34,'padding_right_bottom':35})
 derived.parent.mkdir(exist_ok=True);canvas.save(derived)
 r.archive(derived,Path('derived')/derived.name,'derived_layout_padding_only_all_subject_pixels_unchanged_not_new_generation')
 cmd=[sys.executable,'-X','utf8','-B',
  'C:/Users/22499/.codex/skills/generate2dsprite/scripts/generate2dsprite.py','process',
  '--input',str(derived),'--target','player','--mode','jump','--rows','2','--cols','4',
  '--output-dir',str(out),'--scale-profile',str(P/'profiles/round-knight-airborne-profile-v001.json'),
  '--threshold','180','--edge-threshold','260','--strict-qc','--max-profile-scale-drift','.08','--duration','100']
 result=subprocess.run(cmd,capture_output=True,text=True,encoding='utf-8')
 log=P/'reviews/jump-512cell-padding-processor-v001.txt'
 log.write_text('COMMAND '+json.dumps(cmd)+'\nEXIT '+str(result.returncode)+'\nSTDOUT\n'+result.stdout+'\nSTDERR\n'+result.stderr,encoding='utf-8')
 r.archive(log,Path('reviews')/log.name,'real_processor_calibration_execution_log')
 for f in sorted(out.iterdir()):
  if f.is_file():r.archive(f,Path('processed')/out.name/f.name,'shared_scale_jump_calibration_pending_rigid_part_review')
 meta=r.read(out/'pipeline-meta.json')
 frames=[]
 for f in sorted(out.glob('jump-*.png')):
  q=Image.open(f);alpha=q.getchannel('A');corners=[q.getpixel(pt)[3] for pt in [(0,0),(511,0),(0,511),(511,511)]]
  frames.append({'path':str(f),'sha256':r.sha(f),'canvas':list(q.size),'mode':q.mode,
   'alpha_extrema':list(alpha.getextrema()),'corner_alpha':corners,'bbox':list(alpha.getbbox())})
 report={'source_path':str(source),'source_sha256':r.sha(source),'native_size':[1774,887],
  'derived_path':str(derived),'derived_sha256':r.sha(derived),'derived_size':[2048,1024],
  'operation':'exact_443cell_copy_with_uniform34px_left_top_padding_35px_right_bottom_no_subject_resize',
  'cells':cells,'discarded_trailing_background_pixel_count':len(discarded),
  'discarded_background_rgb_extrema':[[min(px[i] for px in discarded),max(px[i] for px in discarded)] for i in range(3)],
  'profile_unchanged':True,'raw_source_unchanged':True,'generation_calls_added':0,
  'source_to_output_scales':[f['source_to_output_scale'] for f in meta['frames']],
  'previous_source_to_output_scale':.9886896551724137,
  'processor_exit_code':result.returncode,'qc_summary':meta['qc_summary'],'frames':frames,
  'pixel_pass':len(frames)==8 and all(f['canvas']==[512,512] and f['mode']=='RGBA' and f['alpha_extrema']==[0,255] and f['corner_alpha']==[0,0,0,0] for f in frames),
  'rigid_helmet_review_pending':True,'runtime_accepted':False}
 q=P/'reviews/jump-grid-padding-calibration-v001.json';r.write(q,report)
 r.archive(q,Path('reviews')/q.name,'zero_call_layout_calibration_not_visual_or_runtime_acceptance')
 ledger=r.read(P/'generation-ledger.json');entry=next(e for e in ledger['requests'] if e['request_number']==34)
 entry.setdefault('processing_revisions',[]).append({'report_path':str(q),'report_sha256':r.sha(q),
  'generated_new_image':False,'status':'layout_padding_calibration_pending_manual_helmet_review'})
 r.write(P/'generation-ledger.json',ledger)
 print({k:report[k] for k in ['processor_exit_code','pixel_pass','source_to_output_scales','qc_summary']})
 return result.returncode

if __name__=='__main__':raise SystemExit(main())
