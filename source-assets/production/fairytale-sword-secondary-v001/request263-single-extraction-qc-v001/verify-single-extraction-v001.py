from pathlib import Path
import hashlib,json,sys
from PIL import Image
import numpy as np
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
def pin(p):
 p=Path(p).resolve();b=p.read_bytes();return {'path':p.as_posix(),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def main():
 r=json.loads((HERE/'K4-single-extraction-qc-v001.json').read_text());assert r['source_label']=='request263' and r['actual_pose_count']==1 and r['actual_grid'] is None
 for _ in range(2):
  for x in r['inputs']:assert pin(x['path'])==x
 raw=np.array(Image.open(r['inputs'][0]['path']));assert raw.shape==(1254,1254,3);assert np.array_equal(raw,np.array(Image.open(HERE/'source1254/K4-source-full-RGB.png')))
 key=Image.open(HERE/'chroma1254/K4-chroma-full-RGBA.png');assert key.mode=='RGBA' and key.size==(1254,1254)
 a=np.array(key.resize((512,512),Image.Resampling.LANCZOS));assert np.array_equal(a,np.array(Image.open(HERE/'uniform-resize512/K4-unshifted-RGBA.png')))
 clean=a.copy();clean[a[:,:,3]<=8]=0
 dy=r['frame']['transform']['y_integer_shift'];assert r['frame']['transform']['scale_denominator']==1254 and r['frame']['transform']['x_shift']==0
 sy=max(0,-dy);ey=min(512,512-dy);expected=np.zeros_like(clean);expected[sy+dy:ey+dy]=clean[sy:ey]
 actual=np.array(Image.open(HERE/'aligned512/K4-body-footline464-RGBA.png'));assert np.array_equal(expected,actual)
 assert np.array_equal(np.array(Image.open(HERE/'alpha1254/K4-keyed-alpha.png')),np.array(key)[:,:,3])
 assert np.array_equal(np.array(Image.open(HERE/'alpha512/K4-unshifted-alpha.png')),a[:,:,3]);assert np.array_equal(np.array(Image.open(HERE/'alpha512/K4-aligned-alpha.png')),actual[:,:,3])
 assert np.array_equal(np.array(Image.open(HERE/'edge-cleanup-masks512/K4-unshifted-low-alpha-zeroed.png')),((a[:,:,3]>0)&(a[:,:,3]<=8))*255)
 print(json.dumps({'source_label':'request263','single_full1254_to512':True,'x_shift':0,'y_shift':dy,'inverse_source_pipeline_RGBA_exact':True,'inputs_twoSHA_passes':2,'input_mismatches':0,'art_fit_accepted':False}))
if __name__=='__main__':main()
