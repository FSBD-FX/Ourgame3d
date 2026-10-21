from pathlib import Path
import ast,hashlib,json
ROOT=Path('F:/Ourgame');BASE=ROOT/'source-assets/production/fairytale-hero-state-gap-v001'
OLD=BASE/'lgt-hurt4-integer-SWD-assembly-v001/build-Hurt-own-partition-three-LGT-and-SWD-v001.py'
old=OLD.read_text(encoding='utf-8')
changes=[
 ("OUT=HERE/'candidate-v001';MEDIA=ROOT/'过程图稿与视频/2026-10-18_钟盔Hurt227棕皮三层与军剑四相整数试装_v001'","OUT=HERE/'candidate-v002';MEDIA=ROOT/'过程图稿与视频/2026-10-18_钟盔Hurt轻甲有限真实遮挡与整数位移复核_v002'"),
 ("alpha=a[:,:,3]>0;fh=poly(FARHAND0)&alpha&~near if i==0 else np.zeros((512,512),bool)","alpha=a[:,:,3]>0\n  if i==2:near=poly([[174,270],[182,263],[193,259],[205,260],[219,263],[229,272],[234,283],[235,292],[231,301],[225,307],[217,314],[207,319],[194,318],[182,313],[174,305],[170,296],[170,284]])&alpha\n  fh=poly(FARHAND0)&alpha&~near if i==0 else np.zeros((512,512),bool)"),
 ("assert np.array_equal(layers['NearHand'],np.array(Image.open(Path(srow['source_hand']['foreground_exact_RGBA']['path']))))","oldhand=np.array(Image.open(Path(srow['source_hand']['foreground_exact_RGBA']['path'])))\n  assert np.array_equal(layers['NearHand'][oldhand[:,:,3]>0],oldhand[oldhand[:,:,3]>0]),'Existing actual fist pixels lost'"),
 ("'NearHand_RGBA_exact_to_E422_own_Hurt_mask':True","'NearHand_own_E422_sourcepixels_preserved_frame2_actual_glove_boundary_expanded':True"),
 ("f'Hurt{i} / OWN body+3LGT+SWD .50'","f'Hurt{i} / finite review' if i!=1 else 'Hurt1 / CHEST REJECTED'"),
 ("authority=write('Root-sourcefit-authority-original-warning-retention-v001.json',", "authority=write('Root-sourcefit-authority-original-warning-retention-v002.json',"),
 ("'schema':'Hurt227-LGT-threecomponents-SWD-sourcefit-v001'","'schema':'Hurt227-LGT-finite-legal-owner-translation-review-v002'"),
 ("'newmedia_Viewed':False,'sourcefit_motion_accepted':False", "'finite_review_only':True,'Hurt1_Chest_rejected_pending_native_source_correction':True,'original_v001_freeze_preserved':True,'newmedia_Viewed':False,'sourcefit_motion_accepted':False")]
for before,after in changes:
 assert old.count(before)==1,(before,old.count(before));old=old.replace(before,after)
# Execute an independent NEW candidate module built from the already retained v001 source;
# no old source file, candidate, PNG, report or freeze is modified.
tree=ast.parse(old);tree.body=[n for n in tree.body if not isinstance(n,ast.If)]
scope={'__file__':str(Path(__file__).resolve()),'__name__':'finite_review_candidate_v002'}
exec(compile(tree,str(Path(__file__).resolve()),'exec'),scope)
scope['HELMET'][1]=[[95,30],[320,30],[320,170],[294,170],[285,184],[270,191],[247,200],[220,210],[194,221],[170,233],[155,240],[145,246],[130,251],[110,251]]
scope['HELMET'][2]=[[175,85],[375,85],[385,290],[346,295],[322,285],[301,273],[278,262],[257,251],[233,242],[211,225],[191,204],[179,191]]
scope['NEARARM'][1]=[[137,268],[147,259],[160,251],[178,243],[193,244],[204,253],[198,267],[185,279],[176,297],[171,313],[154,316],[142,313],[132,306],[128,293]]
scope['NEARARM'][2]=[[153,244],[168,231],[185,224],[202,228],[218,239],[214,251],[204,264],[194,277],[180,289],[176,301],[165,308],[153,304],[146,294],[141,280],[141,260]]
scope['MOUNTS']['Chest']['B'][2]=[234,306]
scope['MOUNTS']['Chest']['B'][3]=[250,303]
scope['MOUNTS']['Chest']['B_role'][2]='Visible old belt region; proposed8px left shift relative prior buckle fit, not same physical buckle center'
scope['MOUNTS']['Chest']['B_role'][3]='Visible old belt region; proposed14px left shift relative prior buckle fit, not same physical buckle center'
scope['MOUNTS']['ShoulderNear']['B'][1]=[164,253]
scope['MOUNTS']['ShoulderFar']['B']=[[299,289],[291,228],[297,278],[304,255]]
scope['MOUNTS']['ShoulderFar']['B_role']=['Visible gray fararm/neck edge; source0 prior202corepx outsidebody is notaccepted','Visible farshoulder graycloth','Visible fararm ink seam','Visible farshoulder graycloth']
scope['main']()
