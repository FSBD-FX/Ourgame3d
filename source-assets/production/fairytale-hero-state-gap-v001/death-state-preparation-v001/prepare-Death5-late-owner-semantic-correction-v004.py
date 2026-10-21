"""NEW source-pixel partition only; late visible gloves separated from copper helmet.

This is an author mask candidate, not an anatomy/contact measurement. Frozen
v001 layers and mask-support v002 remain untouched. All output needs Root E/View.
"""
from pathlib import Path
import hashlib,json,shutil,importlib.util
import numpy as np
from PIL import Image,ImageDraw,ImageFilter
C=Path(__file__).resolve().parent
O=C/'candidate-v004-late-owner-semantic-correction'
F=Path('F:/Ourgame/过程图稿与视频/2026-10-18_钟盔Death220晚两相近手指背分区纠正_v004')
spec=importlib.util.spec_from_file_location('old_partition',C/'prepare-Death5-exclusive-owners-v001.py');old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old)
OWNERS=old.OWNERS
NEAR={
3:[[211,421],[217,411],[229,403],[242,405],[252,413],[257,416],[271,414],[284,418],[296,424],[307,434],[316,447],[314,457],[308,462],[297,464],[287,461],[279,460],[269,461],[257,457],[246,454],[235,452],[222,452],[215,445],[209,434]],
4:[[207,422],[213,412],[222,404],[235,407],[244,414],[249,417],[262,414],[276,418],[290,425],[302,435],[310,448],[308,457],[302,463],[293,464],[281,462],[272,461],[261,462],[248,457],[236,455],[221,453],[212,446],[205,434]]}
FAR={
3:[[371,435],[385,432],[393,420],[404,413],[415,417],[425,425],[436,434],[445,447],[444,456],[437,462],[427,460],[418,455],[409,457],[399,452],[389,457],[378,456],[370,449]],
4:[[371,434],[387,429],[397,418],[408,412],[419,417],[429,427],[439,438],[446,449],[442,461],[432,463],[422,457],[414,456],[405,452],[395,455],[384,454],[374,452],[369,444]]}
def pin(p):
 p=Path(p).resolve();b=p.read_bytes();return dict(path=p.as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def write(p,v):
 assert not p.exists(),str(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(v if isinstance(v,str)else json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def save(p,im):
 assert not p.exists(),str(p);p.parent.mkdir(parents=True,exist_ok=True);im.save(p)
def glove(a,points):
 # Separates visible brown glove samples from copper/ivory helmet samples;
 # ROI excludes amber eyes. No hidden glove area or body pixels are synthesized.
 q=a.astype(np.int16);r=q[:,:,0];g=q[:,:,1];b=q[:,:,2];roi=old.poly(points)
 seed=(r>=60)&(g>=25)&(r-g>=26)&(g-b>=12)&(100*g<67*r)&(100*b<48*r)&(q[:,:,3]>0)&roi
 im=Image.fromarray(np.where(seed,255,0).astype(np.uint8)).filter(ImageFilter.MaxFilter(5))
 ImageDraw.floodfill(im,(0,0),128);v=np.asarray(im)
 return ((v==255)|(v==0))&roi&(a[:,:,3]>0)
def main():
 assert not O.exists() and not F.exists();O.mkdir()
 previous=json.loads((C/'candidate-v001/Death220-exclusive-owners-registration-and-released-SWD-proposal-v001.json').read_text(encoding='utf-8-sig'))
 rows=[];annotations=[];before=[]
 for row in previous['rows']:
  i=row['frame'];src=Path(row['source']['path']);assert pin(src)==row['source'];a=np.asarray(Image.open(src).convert('RGBA'));alpha=a[:,:,3]>0
  oldm={x['owner']:np.asarray(Image.open(x['source_RGBA_layer']['path']))[:,:,3]>0 for x in row['body_owners']}
  for x in row['body_owners']:assert pin(x['source_RGBA_layer']['path'])==x['source_RGBA_layer'];before.append(x['source_RGBA_layer'])
  if i<3:masks=oldm
  else:
   near=glove(a,NEAR[i]);far=glove(a,FAR[i])&~near
   helmet=old.filled_warm_region(a,old.HELMET[i],9)&~near&~far
   arm=old.poly(old.NEARARM[i])&alpha&~near&~far&~helmet
   rest=alpha&~(near|far|helmet|arm)
   masks=dict(BodyRest=rest,NearArmWithoutHand=arm,HelmetForeground=helmet,FarHandForeground=far,NearHand=near)
  assert np.array_equal(np.sum(np.stack(list(masks.values())),axis=0),alpha.astype(np.int64))
  recon=Image.new('RGBA',(512,512));annotation=np.zeros_like(a);items=[]
  for name,color in zip(OWNERS,[(80,90,110,255),(80,180,255,255),(225,200,80,255),(180,90,225,255),(245,130,60,255)]):
   layer=np.where(masks[name][:,:,None],a,0).astype(np.uint8);lp=O/f'body-layers/{name}/frame-{i}.png';mp=O/f'body-masks/{name}/frame-{i}.png'
   if i<3:lp.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(next(x['source_RGBA_layer']['path']for x in row['body_owners']if x['owner']==name),lp)
   else:save(lp,Image.fromarray(layer))
   save(mp,Image.fromarray(np.where(masks[name],255,0).astype(np.uint8)))
   assert np.array_equal(np.asarray(Image.open(lp)),layer);assert np.array_equal(np.asarray(Image.open(mp))>0,layer[:,:,3]>0)
   assert np.count_nonzero(masks[name])>0
   recon=Image.alpha_composite(recon,Image.fromarray(layer));annotation[masks[name]]=color
   items.append(dict(owner=name,source_RGBA_layer=pin(lp),mask=pin(mp),visible_pixels=int(np.count_nonzero(masks[name])),bbox=old.bbox(masks[name]),added_pixels=int(np.count_nonzero(masks[name]&~oldm[name])),removed_pixels=int(np.count_nonzero(oldm[name]&~masks[name])),known_optional_empty=False,semantic_author_review='UNVIEWED_NEW_CANDIDATE'))
  assert np.array_equal(np.asarray(recon),a);save(O/f'reconstruction/frame-{i}.png',recon);save(O/f'diagnostics/owner-colors-frame-{i}.png',Image.fromarray(annotation));annotations.append(Image.fromarray(annotation))
  rows.append(dict(frame=i,source=row['source'],layers=items,source_RGBA_reconstruction_exact=True,exclusive_alpha_support_exact=True,source_pixels_added_or_repainted=0,actual_hidden_bones_or_grip=None,hand_helmet_contour_uncertainty_source_px=2 if i>=3 else None,physical_ground_root=None,display_root_author_proposal=[242,464],source0_to2_RGBA_files_byte_unchanged=i<3))
 sheet=Image.new('RGBA',(2560,512))
 for i,im in enumerate(annotations):sheet.paste(im,(i*512,0))
 save(O/'presentation/Death220-exclusive-owner-annotation-row-v004.png',sheet)
 write(O/'Death220-late-visible-owner-correction-v004.json',dict(schema='Death220-late-visible-owner-semantic-candidate-v004',old_RGBA_partition=pin(C/'Death5-body-source-partition-freeze-v001.json'),old_mask_support=pin(C/'mask-alpha-support-correction-v002/mask-support-freeze-v002.json'),change_scope='Only late frames3/4 visible owner assignments; frames0/1/2 RGBA copied byte-exact. All25 support masks equal source-layer alpha>0.',reason='v003 actual E494 View still showed a narrow glove-colored crescent in Helmet3/4; only late near-hand upper contour is expanded to the visible finger-back edge. Strict glove seeds and the eye-excluding ROI remain; no source pixel repaint.',source_pixels_added_or_repainted=0,WholeBody_as_BodyRest=False,body_canvas=[512,512],body_display_scale=72/416,no_perframe_alpha_height_scale=True,hand_contact_or_hidden_axes=None,semantic_acceptance=False,occlusion_acceptance=False,new_images_Viewed=False,Root_E_before_View_required=True,TrialAllowed=False,FinalAccepted=False,rows=rows))
 write(O/'before-layer-pins-v001.json',before)
 write(O/'HANDOFF.md','NEW author semantic partition, not anatomy/contact or final layer acceptance. v001 broad warm classification visibly included orange glove samples in Helmet3/4 and removed copper rim. Only3/4 source pixels are reassigned;0..2 layers byte-exact. All25 exclusive support masks and source RGBA reconstruction verified. New layers/annotation UNVIEWED pending Root E gate; boundary uncertainty2 sourcepx, actual Grip/Axis/physicalRoot null. Review glove edges/copper rim after E, then sourcefit armor occlusion; no repaint/new anatomy. Existing release/root proposals unchanged and still author-only.\n')
 write(O/'source-layer-freeze-v004.json',dict(script=pin(Path(__file__)),files=[pin(p)for p in sorted(O.rglob('*'))if p.is_file()],new_images_Viewed=False,TrialAllowed=False))
 orig=F/'原件/晚两相语义分区完整候选';orig.parent.mkdir(parents=True);shutil.copytree(O,orig);show=F/'展示副本';show.mkdir();shutil.copy2(O/'presentation/Death220-exclusive-owner-annotation-row-v004.png',show/'Death220-exclusive-owner-annotation-row-v004.png')
 for name in ['HelmetForeground','NearHand','FarHandForeground']:shutil.copytree(O/f'body-layers/{name}',show/name)
 write(F/'README.md','Death220 exact-source owner reassignment candidate v004. NEW media UNVIEWED pending Root E preservation before View. Exact reconstruction is numerical closure only; semantic/armor occlusion, grip/axes and native are not accepted.\n')
 write(F/'source-version-status-index.json',dict(schema='Death220-late-owner-F-index-v004',status='UNVIEWED_AWAIT_ROOT_E_GATE',candidate=O.as_posix(),files=[pin(p)for p in sorted(F.rglob('*'))if p.is_file()],TrialAllowed=False))
 print(json.dumps(dict(candidate=O.as_posix(),freeze=pin(O/'source-layer-freeze-v004.json'),F_canonical=F.as_posix(),F_files=len([p for p in F.rglob('*')if p.is_file()]),F_bytes=sum(p.stat().st_size for p in F.rglob('*')if p.is_file()),late_changes=[{'frame':r['frame'],'layers':[{k:x[k]for k in ['owner','visible_pixels','added_pixels','removed_pixels']}for x in r['layers']]}for r in rows if r['frame']>=3],new_images_Viewed=False),ensure_ascii=False))
if __name__=='__main__':main()
