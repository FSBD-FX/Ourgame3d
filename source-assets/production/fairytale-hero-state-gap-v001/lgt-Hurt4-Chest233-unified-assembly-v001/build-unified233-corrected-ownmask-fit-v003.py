from pathlib import Path
from collections import deque
import ast,hashlib,json,shutil
import numpy as np
from PIL import Image,ImageDraw
BASE=Path('F:/Ourgame/source-assets/production/fairytale-hero-state-gap-v001')
SOURCE=BASE/'lgt-hurt4-integer-SWD-assembly-v001/build-Hurt-own-partition-three-LGT-and-SWD-v001.py'
METHOD=Path(__file__).resolve().parent/'method-correction-v001/readonly-oldfailure-writable-copy-independent-toy-and-actual-hole-amendment-v001.json'
assert hashlib.sha256(METHOD.read_bytes()).hexdigest()=='56c5206978ddea77b71485ca76436493e88de24343062fa12a24f8f572c8b1d5'
code=SOURCE.read_text(encoding='utf-8')
changes=[
 ("OUT=HERE/'candidate-v001';MEDIA=ROOT/'过程图稿与视频/2026-10-18_钟盔Hurt227棕皮三层与军剑四相整数试装_v001'","OUT=HERE/'candidate-v003';MEDIA=ROOT/'过程图稿与视频/2026-10-18_钟盔Hurt233统一胸衣与自身正确分层军剑试装_v003'"),
 ("LEATHER/'run-Hurt4-chest-native228-shared-HD-v001'","CHEST_RUN"),
 ("('Chest',CHEST_RUN,431)","('Chest',CHEST_RUN,453)"),
 ("'Chest228','ShoulderNear229','ShoulderFar231'","'Chest233','ShoulderNear229','ShoulderFar231'"),
 ("Chest228 Near229 Far231","Chest233 Near229 Far231"),
 ("228+229+231","233+229+231"),
 ("alpha=a[:,:,3]>0;fh=poly(FARHAND0)&alpha&~near if i==0 else np.zeros((512,512),bool)","alpha=a[:,:,3]>0\n  if i==2:near=poly([[174,270],[182,263],[193,259],[205,260],[219,263],[229,272],[234,283],[235,292],[231,301],[225,307],[217,314],[207,319],[194,318],[182,313],[174,305],[170,296],[170,284]])&alpha\n  fh=poly(FARHAND0)&alpha&~near if i==0 else np.zeros((512,512),bool)"),
 ("helmet=fillholes(dil)&hp&alpha&~near&~fh","helmet=fillholes(dil)&hp&alpha&~near&~fh\n  if i==1:assert not helmet[260,150] and not helmet[236,198] and not helmet[217,280], 'Wrong graycloth includedin Helmet1'\n  if i==2:assert helmet[275,325], 'Actual lowerjaw missing from Helmet2'"),
 ("assert np.array_equal(layers['NearHand'],np.array(Image.open(Path(srow['source_hand']['foreground_exact_RGBA']['path']))))","oldhand=np.array(Image.open(Path(srow['source_hand']['foreground_exact_RGBA']['path'])))\n  assert np.array_equal(layers['NearHand'][oldhand[:,:,3]>0],oldhand[oldhand[:,:,3]>0])"),
 ("'NearHand_RGBA_exact_to_E422_own_Hurt_mask':True","'NearHand_own_E422_pixels_preserved_frame2_actualsource_topboundary_expanded':True"),
 ("Visible tan material seed inside own frame ROI, 4px Chebyshev envelope + enclosed ink-hole fill, clipped to source alpha. Segmentation only; all originalRGBA retained under exclusive owners. Boundary semantic review pending.","Own-frame visible tan seed and4px envelope, WRITABLE.copy floodfill independentlymatchedtoBFS exteriorgraph; onlyenclosedinkholes filled, then actualownROI/sourcealpha clipped. NotROIwholefill. Segmentation only, allRGBA retained; semanticreviewpending."),
 ("'schema':'Hurt227-LGT-threecomponents-SWD-sourcefit-v001'","'schema':'Hurt233-unified-Chest-correct-ownmask-sourcefit-v003'"),
 ("'newmedia_Viewed':False,'sourcefit_motion_accepted':False","'Chest233_allfour_one_shared_native_scale':0.32894736842105265,'predeclared_Chest233_common_max_window':[128,100],'correct_floodfill_method_toy_and_independent_graph_report':pin(METHOD),'all_old_frozen_records_preserved':True,'newmedia_Viewed':False,'sourcefit_motion_accepted':False"),
 ("Root permits NEW Chest228/Near229 sourcefit after independent clarification inspect report.ok uses errors; all0E1W and FAILED_NO_ACCEPTANCE preserved. E43839files1942846B2SHA0 permits actual231curated View and thirdcomponent fitting.","Root E453 permits actual233curated View andNEWuniformChest233+Near229/Far231 sourcefit; originalwarnings/oldFAILEDremain. Correctreadonlyfloodfill methodrequired withtoyandindependentgraphcheck; oldcandidatefreezesunmodified."),
 ("'actual_original_228_229_curated_View_after_E431_E432':True","'actual_233_229_curated_View_after_E453_E432':True"),
 ("# Root explicitly allowed NEW source fit despite original warnings/old strict FAILED records; no report rewriting.","# New233 is one fourphase native row. No old228/232 frame or old falsehole method is reused. No report rewriting.")]
for before,after in changes:
 assert before in code,before;code=code.replace(before,after)
tree=ast.parse(code);tree.body=[n for n in tree.body if not isinstance(n,ast.If)]
scope={'__file__':str(Path(__file__).resolve()),'__name__':'unified233_sourcefit_v003','METHOD':METHOD}
exec(compile(tree,str(Path(__file__).resolve()),'exec'),scope)
scope['CHEST_RUN']=BASE/'lgt-Hurt4-Chest233-extraction-v001/run-Hurt4-Chest-native233-shared-HD-v001'
def filled_correct(m):
 im=Image.fromarray(np.where(m,255,0).astype(np.uint8)).copy();assert im.readonly==0 and not m[0,0]
 ImageDraw.floodfill(im,(0,0),128);assert im.getpixel((0,0))==128
 holes=np.array(im)==0;bg=~m;outside=np.zeros_like(bg);q=deque();h,w=m.shape
 for y,x in [(0,x)for x in range(w)]+[(h-1,x)for x in range(w)]+[(y,0)for y in range(h)]+[(y,w-1)for y in range(h)]:
  if bg[y,x] and not outside[y,x]:outside[y,x]=True;q.append((y,x))
 while q:
  y,x=q.popleft()
  for ny,nx in [(y+1,x),(y-1,x),(y,x+1),(y,x-1)]:
   if 0<=ny<h and 0<=nx<w and bg[ny,nx] and not outside[ny,nx]:outside[ny,nx]=True;q.append((ny,nx))
 assert np.array_equal(holes,bg&~outside) and not holes[0].any() and not holes[-1].any()
 return m|holes
scope['fillholes']=filled_correct
scope['HELMET'][1]=[[95,30],[320,30],[320,170],[294,170],[285,184],[270,191],[247,200],[220,210],[194,221],[170,233],[155,240],[145,246],[130,251],[110,251]]
scope['HELMET'][2]=[[175,85],[375,85],[385,290],[346,295],[322,285],[301,273],[278,262],[257,251],[233,242],[211,225],[191,204],[179,191]]
scope['NEARARM'][1]=[[137,268],[147,259],[160,251],[178,243],[193,244],[204,253],[198,267],[185,279],[176,297],[171,313],[154,316],[142,313],[132,306],[128,293]]
scope['NEARARM'][2]=[[153,244],[168,231],[185,224],[202,228],[218,239],[214,251],[204,264],[194,277],[180,289],[176,301],[165,308],[153,304],[146,294],[141,280],[141,260]]
scope['MOUNTS']['Chest']={'A':[[225,241],[202,238],[269,288],[270,285]],'B':[[206,260],[200,251],[242,306],[264,303]],'A_role':['actualneararm-aperture leftinkcontour','actualneararm-aperture leftleathercontour','actualvisiblebuckle surface','actualvisiblebuckle surface'],'B_role':['ownvisiblegrayupperarmsurface; waistbuckleoccluded','ownvisiblegrayupperarmsurface, authorattachmentproposalnotbone','ownvisiblebeltbucklesurface','ownvisiblebeltbucklesurface']}
scope['MOUNTS']['ShoulderNear']['B'][1]=[164,253]
scope['MOUNTS']['ShoulderFar']['B']=[[299,289],[291,228],[297,278],[304,255]]
scope['MOUNTS']['ShoulderFar']['B_role']=['visiblefararm/neck grayedge','visiblefarshouldergraycloth','visiblefararminkseam','visiblefarshouldergraycloth']
scope['main']()
