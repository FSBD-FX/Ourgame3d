from pathlib import Path
from collections import deque
import hashlib,json
import numpy as np
from PIL import Image,ImageDraw
HERE=Path(__file__).resolve().parent;OUT=HERE/'method-correction-v001';assert not OUT.exists();OUT.mkdir()
BASE=Path('F:/Ourgame/source-assets/production/fairytale-hero-state-gap-v001')
def pin(p):
 b=p.read_bytes();return {'path':p.as_posix(),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def independent_holes(opaque):
 bg=~opaque;outside=np.zeros_like(bg);q=deque();h,w=bg.shape
 for y,x in [(0,x)for x in range(w)]+[(h-1,x)for x in range(w)]+[(y,0)for y in range(h)]+[(y,w-1)for y in range(h)]:
  if bg[y,x] and not outside[y,x]:outside[y,x]=True;q.append((y,x))
 while q:
  y,x=q.popleft()
  for ny,nx in [(y+1,x),(y-1,x),(y,x+1),(y,x-1)]:
   if 0<=ny<h and 0<=nx<w and bg[ny,nx] and not outside[ny,nx]:outside[ny,nx]=True;q.append((ny,nx))
 return bg&~outside
def proper(opaque):
 im=Image.fromarray(np.where(opaque,255,0).astype(np.uint8)).copy();assert im.readonly==0 and not opaque[0,0]
 ImageDraw.floodfill(im,(0,0),128);assert im.getpixel((0,0))==128;holes=np.array(im)==0
 assert np.array_equal(holes,independent_holes(opaque))
 assert not (holes[0].any()or holes[-1].any()or holes[:,0].any()or holes[:,-1].any())
 return holes
def cc(mask):
 m=mask.copy();out=[]
 while m.any():
  yy,xx=np.where(m);y,x=int(yy[0]),int(xx[0]);q=deque([(y,x)]);m[y,x]=False;ys=[];xs=[]
  while q:
   y,x=q.popleft();ys.append(y);xs.append(x)
   for ny,nx in [(y+1,x),(y-1,x),(y,x+1),(y,x-1)]:
    if 0<=ny<m.shape[0] and 0<=nx<m.shape[1] and m[ny,nx]:m[ny,nx]=False;q.append((ny,nx))
  if len(xs)>20:out.append({'pixels':len(xs),'bbox':[min(xs),min(ys),max(xs)+1,max(ys)+1],'centroid':[float(np.mean(xs)),float(np.mean(ys))]})
 return out
toy=np.zeros((32,32),np.uint8);toy[6:26,6:26]=255;toy[10:14,10:14]=0;toy[18:23,20:26]=0
old=Image.fromarray(toy);assert old.readonly==1;before=np.array(old).copy();ImageDraw.floodfill(old,(0,0),128);oldholes=np.array(old)==0
assert np.array_equal(before,np.array(old)) and oldholes[0,0] and oldholes[20,23]
newholes=proper(toy>=128);expected=np.zeros((32,32),bool);expected[10:14,10:14]=True
assert np.array_equal(newholes,expected) and newholes.sum()==16 and not newholes[20,23]
actual=[]
for row,p in [('232',BASE/'lgt-Hurt1-chest232-extraction-v001/run-Hurt1-Chest-native232-HD-v001/curated/frame-0.png')]+[(str(i),BASE/f'lgt-Hurt4-Chest233-extraction-v001/run-Hurt4-Chest-native233-shared-HD-v001/curated/frame-{i}.png')for i in range(4)]:
 a=np.array(Image.open(p));holes=proper(a[:,:,3]>=128);actual.append({'row':row,'source':pin(p),'independent_graph_flood_exact':True,'no_exterior_pixels_or_edge_in_holes':True,'holes':cc(holes)})
data={'schema':'readonly-floodfill-diagnostic-correction-v001','status':'TOY_EXPECTED_OLD_FAILURE_NEW_COPY_PASS_AND_ACTUAL_INDEPENDENT_GRAPH_MATCH','toy':{'canvas':[32,32],'opaque_rect_xyxy':[6,6,26,26],'closed_hole_xyxy':[10,10,14,14],'open_cavity_xyxy':[20,18,26,23],'open_cavity_connects_exterior_at_x':26,'old_Image_fromarray_readonly':True,'old_floodfill_did_not_mutate':True,'old_false_hole_includes_exterior_corner':True,'old_false_hole_includes_open_cavity':True,'new_copy_writable':True,'new_only_closed_hole_pixels':16,'new_open_cavity_excluded':True,'new_exterior_excluded':True,'independent_expected_closed4x4_exact':True},'actual_sources':actual,'old_records_preserved':'Do notrewriteE439/E445/E448orprepared233windowevidence. BodyRGBAreconstructionwastrue,butoldHelmetmethodactuallyusedwholeROIbecausereadonlyfloodfillfailed; sourceownersemanticreviewmustusenewcorrectpartition.','withdrawn_claims':['232negative-aperturecenter[220.4328,249.9492] wasROIcontaminated; replacefornewdiagnosticwithactualclosedhole[224.4840764,244.2675159].','9.43px preciseleftedge-to-closedholemargin withdrawn; actual232closedholeleftmargin224.4841-211=13.4841px.'], 'window_limit':'KeepRootauthorizedpredeclared128x100 andoriginal512gate. Originalallowancegeometryisartistdesigninference, notphysicalproof; corrected232allowances13.484+90+27=130.484differby2.484fromwindow. Do notsilentlychangeitaftergenerationorforcefit. New233actualsourcefit andphysicaldensityreview determinecompatibility.','new_body_partition_required':True,'new_Helmet_mask_must_use_writable_copy_then_independent_graph_check':True,'Source_Content_UE_modified':False,'AI_calls':0}
p=OUT/'readonly-oldfailure-writable-copy-independent-toy-and-actual-hole-amendment-v001.json';p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps({'report':pin(p),'toy_new_closed_hole':int(newholes.sum()),'old_false_hole_pixels':int(oldholes.sum()),'actual':actual},ensure_ascii=False,indent=2))
