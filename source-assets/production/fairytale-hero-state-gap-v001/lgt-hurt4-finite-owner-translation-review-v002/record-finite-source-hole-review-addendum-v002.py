from pathlib import Path
import hashlib,json,shutil
from PIL import Image
import numpy as np
BASE=Path('F:/Ourgame/source-assets/production/fairytale-hero-state-gap-v001')
OLD=BASE/'lgt-hurt4-integer-SWD-assembly-v001/candidate-v001'
NEW=Path(__file__).resolve().parent/'candidate-v002'
MEDIA=Path('F:/Ourgame/过程图稿与视频/2026-10-18_钟盔Hurt轻甲有限真实遮挡与整数位移复核_v002')
def pin(p):
 b=p.read_bytes();return {'path':p.as_posix(),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def bbox(m):
 y,x=np.where(m);return None if not len(x) else [int(x.min()),int(y.min()),int(x.max()+1),int(y.max()+1)]
roi=[[226,225,247,258],[213,225,240,263],[226,225,249,259],[226,224,245,260]]
rows=[]
for i in range(4):
 versions=[]
 for version,out in [('v001_E439_actual_View',OLD),('v002_UNVIEWED_finite_candidate',NEW)]:
  c=json.loads((out/'Hurt227-own-five-partition-12-integer-armor-mounts-SWD050-contract-v001.json').read_text(encoding='utf-8'));r=c['rows'][i];mt=r['armor_mounts'][0];ga=np.array(Image.open(mt['source']['path']));a=np.array(Image.open(r['body_source']['path']));x0,y0,x1,y1=roi[i];yy,xx=np.indices((512,512));hole=(xx>=x0)&(xx<x1)&(yy>=y0)&(yy<y1)&(ga[:,:,3]>=128)&np.all(ga[:,:,:3]<20,axis=2);dx,dy=mt['integer_delta'];mapped=np.zeros((512,512),bool);hy,hx=np.where(hole);mapped[hy+dy,hx+dx]=True;hidden=np.zeros_like(mapped)
  for name in ['NearArmWithoutHand','ShoulderNear','HelmetForeground','FarHandForeground','SWD','NearHand']:
   if name in ['ShoulderNear']:p=out/f'armor-layers/{name}/frame-{i}.png'
   elif name=='SWD':p=out/f'weapon-layers/SWD/frame-{i}.png'
   else:p=out/f'body-layers/{name}/frame-{i}.png'
   hidden|=np.array(Image.open(p))[:,:,3]>=128
  remaining=mapped&~hidden;warmglove=(a[:,:,0].astype(int)-a[:,:,1]>=30)&(a[:,:,1].astype(int)-a[:,:,2]>=15)
  versions.append({'version':version,'Chest_delta':mt['integer_delta'],'source_opaque_black_ROI':roi[i],'source_opaque_black_core_count':int(hole.sum()),'not_full_blackoutline_or_neck_metric':True,'remaining_not_core_occluded_count':int(remaining.sum()),'remaining_bbox':bbox(remaining),'remaining_over_body_alpha128':int(np.count_nonzero(remaining&(a[:,:,3]>=128))),'remaining_over_actual_warm_glove_candidate':int(np.count_nonzero(remaining&warmglove)),'count_is_not_semantic_pass':True})
 rows.append({'frame':i,'versions':versions})
data={'schema':'Hurt4-LGT-finite-owner-translation-review-amendment-v002','version':'v002','original_v001_retained_E439_not_modified':True,'v002_legacy_leaf_filenames':'Reused deterministicbuilder emits leaf-v001 filenames, but this independentparentfolder/canonicalbatch/schema arev002. Do not confuse oldE439freeze withnewcandidate. Originalindex/freeze remainpreserved andthisaddendumisappend-only.','original_builder':pin(BASE/'lgt-hurt4-integer-SWD-assembly-v001/build-Hurt-own-partition-three-LGT-and-SWD-v001.py'),'v002_adapter':pin(Path(__file__).resolve().parent/'make-and-run-finite-review-v002.py'),'v001_actual_Viewed_after_E439':['full4plate','torso2xplate','Readyjoin','HelmetForeground0/1/2/3','NearArm1','FarHand0'],'actual_findings':['Chest228 nearapertures containopaque[0,0,0,255], nottransparentholes. Frame1 maps source[225240] onto originalgray[241245] andrequires87pxwaistmisalignmentifmovedtoneararm.','v001Helmet1 maskwronglyincludesgraycollar/band andsmallfarwrist; sourceownerassignmentfailure, pixelsnotlost. NEWv002 clipsownactualhelmetbottominklandmarks.','v001Helmet2 sourceownership omittedlowerjaw; NEWv002 sourceROIenlarged, nohelmetpixelsdrawn orchanged.','NEWv002 ownNearArm1/2 captureactualvisibleuppersleeve; NearHand2 includesactualsourceglovetop previouslyoutsideoldhandpolygon. OriginalE422handpixelsretained, SWDlayerunchanged.','Chest2/3 tryonly8/14pxleftintegertranslations; Far0/2/3 trycloseractualsurfaceB. Thesearefinitecandidatefixes, notacceptedsemanticcoverage.'],'opaque_black_analysis':rows,'Hurt1_Chest_source_rejection_still_blocks_full4':True,'minimum_current_admission':'AlreadyRootreviewedE422SWD4 sourcefit mayproceedseparately; thisnewLGTfull4 remainsclosed. Near/Faroriginalsourcesneednotregenerate, buttheirregistration/depthstillawaitreview.','new_v002_media_Viewed':False,'new_v002_media_E_retained':False,'TrialAllowed':False,'no_opaque_black_erasure_or_gray_lining_drawn':True,'no_armor_resample_rotate_mirror':True}
p=NEW/'有限源孔归因与版本差异补充-v002.json';assert not p.exists();p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
shutil.copyfile(p,MEDIA/'原件/四相LGT军剑整数试装完整包'/p.name)
index=MEDIA/'版本差异追加索引-v002.json';assert not index.exists();index.write_text(json.dumps({'version':'v002','append_only_addendum':pin(p),'original_index_preserved':pin(MEDIA/'来源-版本-状态索引.json'),'newmedia_View':False,'files_current':[pin(p) for p in sorted(MEDIA.rglob('*')) if p.is_file()]},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'F_canonical':MEDIA.as_posix(),'files':sum(p.is_file() for p in MEDIA.rglob('*')),'bytes':sum(p.stat().st_size for p in MEDIA.rglob('*') if p.is_file()),'addendum':pin(p),'hole_counts':rows,'newmedia_View':False},ensure_ascii=False,indent=2))
