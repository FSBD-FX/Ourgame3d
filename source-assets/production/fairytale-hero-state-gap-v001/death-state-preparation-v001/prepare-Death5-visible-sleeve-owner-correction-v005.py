"""Reassign only visible old waist/gray-back contamination from NearArm to BodyRest.
No pixel repaint/erase. Other v004 foreground owners remain byte-exact.
"""
from pathlib import Path
import json,hashlib,shutil
import numpy as np
from PIL import Image,ImageDraw
C=Path(__file__).resolve().parent;P=C/'candidate-v004-late-owner-semantic-correction';O=C/'candidate-v005-visible-sleeve-owner-correction';F=Path('F:/Ourgame/过程图稿与视频/2026-10-18_钟盔Death220袖缝与旧腰带owner纠正_v005')
OWNERS=['BodyRest','NearArmWithoutHand','HelmetForeground','FarHandForeground','NearHand']
SLEEVE={
2:[[253,312],[265,314],[275,322],[281,335],[284,350],[294,372],[297,383],[291,392],[278,400],[260,400],[251,390],[253,377],[248,366],[245,351],[245,336],[247,323]],
3:[[237,345],[255,348],[267,358],[274,372],[270,382],[258,398],[245,414],[231,427],[213,416],[207,408],[206,395],[213,383],[216,370],[222,360]],
4:[[224,350],[240,350],[254,363],[260,377],[251,397],[237,415],[218,425],[204,413],[197,396],[204,380],[210,366]]}
def pin(p):
 p=Path(p).resolve();b=p.read_bytes();return dict(path=p.as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p,v):
 assert not p.exists(),str(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(v if isinstance(v,str)else json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def save(p,im):
 assert not p.exists(),str(p);p.parent.mkdir(parents=True,exist_ok=True);im.save(p)
def poly(points):
 im=Image.new('L',(512,512));ImageDraw.Draw(im).polygon(list(map(tuple,points)),fill=255);return np.asarray(im)>0
def bbox(m):
 y,x=np.where(m);return [int(x.min()),int(y.min()),int(x.max()+1),int(y.max()+1)]if len(x)else None
def main():
 assert not O.exists()and not F.exists();O.mkdir();previous=read(P/'Death220-late-visible-owner-correction-v004.json');rows=[];control=[]
 for oldrow in previous['rows']:
  i=oldrow['frame'];src=Path(oldrow['source']['path']);assert pin(src)==oldrow['source'];a=np.asarray(Image.open(src).convert('RGBA'));alpha=a[:,:,3]>0;oldm={}
  for x in oldrow['layers']:assert pin(x['source_RGBA_layer']['path'])==x['source_RGBA_layer'];oldm[x['owner']]=np.asarray(Image.open(x['source_RGBA_layer']['path']))[:,:,3]>0
  masks={k:v.copy()for k,v in oldm.items()}
  if i>=2:
   # Keep only the current source-visible sleeve region; all pixels outside it
   # go back to BodyRest, so no geometry is invented or gray torso erased.
   arm=oldm['NearArmWithoutHand']&poly(SLEEVE[i]);rest=oldm['BodyRest']|(oldm['NearArmWithoutHand']&~arm);masks['NearArmWithoutHand']=arm;masks['BodyRest']=rest
  assert np.array_equal(np.sum(np.stack(list(masks.values())),axis=0),alpha.astype(np.int64))
  recon=Image.new('RGBA',(512,512));items=[]
  for n in OWNERS:
   arr=np.where(masks[n][:,:,None],a,0).astype(np.uint8);lp=O/f'body-layers/{n}/frame-{i}.png';mp=O/f'body-masks/{n}/frame-{i}.png';oldlayer=next(x['source_RGBA_layer']for x in oldrow['layers']if x['owner']==n)
   changed=not np.array_equal(masks[n],oldm[n])
   if changed:save(lp,Image.fromarray(arr))
   else:lp.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(oldlayer['path'],lp)
   save(mp,Image.fromarray(np.where(masks[n],255,0).astype(np.uint8)));assert np.array_equal(np.asarray(Image.open(lp)),arr);assert np.count_nonzero(masks[n])>0
   recon=Image.alpha_composite(recon,Image.fromarray(arr));items.append(dict(owner=n,source_RGBA_layer=pin(lp),mask=pin(mp),visible_pixels=int(np.count_nonzero(masks[n])),bbox=bbox(masks[n]),byte_exact_to_v004=not changed,source_pixels_added_or_repainted=0))
  assert np.array_equal(np.asarray(recon),a);save(O/f'reconstruction/frame-{i}.png',recon)
  moved=oldm['NearArmWithoutHand']&~masks['NearArmWithoutHand'];diagnostic=Image.fromarray(a.copy());d=ImageDraw.Draw(diagnostic)
  if i>=2:d.line([tuple(x)for x in SLEEVE[i]]+[tuple(SLEEVE[i][0])],fill=(0,230,255,255),width=1)
  save(O/f'diagnostics/frame-{i}-actual-sleeve-author-contour.png',diagnostic)
  change=np.zeros_like(a);change[moved]=a[moved];save(O/f'diagnostics/frame-{i}-NearArm-to-BodyRest-exact-source-pixels.png',Image.fromarray(change))
  # Old and new arm are separate source-exact surfaces for actual visual control.
  plate=Image.new('RGBA',(1536,560),(40,43,49,255));plate.alpha_composite(Image.fromarray(a),(0,40));plate.alpha_composite(Image.open(next(x['source_RGBA_layer']['path']for x in oldrow['layers']if x['owner']=='NearArmWithoutHand')).convert('RGBA'),(512,40));plate.alpha_composite(Image.open(O/f'body-layers/NearArmWithoutHand/frame-{i}.png').convert('RGBA'),(1024,40));d=ImageDraw.Draw(plate);d.text((8,10),f'Death{i} ORIGINAL',fill='white');d.text((520,10),'v004 arm includes sourcewaist/back edge',fill='white');d.text((1032,10),'v005 visible-sleeve-only author candidate',fill='white');save(O/f'presentation/Death-{i}-source-and-NearArm-control-v005.png',plate.convert('RGB'))
  rows.append(dict(frame=i,source=oldrow['source'],layers=items,source_RGBA_reconstruction_exact=True,exclusive_alpha_support_exact=True,source_pixels_added_or_repainted=0,actual_hidden_bones_or_grip=None,hand_helmet_contour_uncertainty_source_px=2 if i>=3 else None,physical_ground_root=None,display_root_author_proposal=[242,464],NearArm_to_BodyRest_reassigned_pixels=int(np.count_nonzero(moved)),sleeve_contour_author_uncertainty_source_px=3 if i>=2 else None))
 write(O/'Death220-visible-sleeve-owner-correction-v005.json',dict(schema='Death220-visible-sleeve-owner-semantic-candidate-v005',old_partition=pin(P/'source-layer-freeze-v004.json'),change_scope='Only NearArm/BodyRest2..4 repartition visible sourcewaist/back edges; other19 sourceRGBA layers copied byte-exact fromv004. No newhand/helmet mask and no artwork repaint.',reason='Actual E497 standaloneNearArm2..4 exposes original waist/buckle samples and frame2 grayback above visible sleeve. These do not belong to a foreground sleeve over newChest.',source_pixels_added_or_repainted=0,WholeBody_as_BodyRest=False,body_canvas=[512,512],body_display_scale=72/416,no_perframe_alpha_height_scale=True,semantic_acceptance=False,new_images_Viewed=False,Root_E_before_View_required=True,TrialAllowed=False,FinalAccepted=False,rows=rows))
 write(O/'HANDOFF.md','NEW v005 narrow sourceowner repair after actual E497 bodyrest/neararm View. Only NearArm/BodyRest2..4 changed: old brown waist/gray-back edges move behindChest. Current19otherRGBA layers byte-exact to v004 including accepted-limited hand/helmet3/4. All25 masks match alpha support and exact sourceRGBA recomposition; no graybody erasure/new pixels/hidden skeleton. Sleeve contours author±3px not final semantic acceptance. New3 control plates, exactmovedpixels and25layers UNVIEWED pendingRootE.\n')
 write(O/'source-layer-freeze-v005.json',dict(script=pin(Path(__file__)),files=[pin(p)for p in sorted(O.rglob('*'))if p.is_file()],new_images_Viewed=False,TrialAllowed=False))
 orig=F/'原件/袖缝owner纠正完整候选';orig.parent.mkdir(parents=True);shutil.copytree(O,orig);show=F/'展示副本';show.mkdir()
 for i in [2,3,4]:shutil.copy2(O/f'presentation/Death-{i}-source-and-NearArm-control-v005.png',show/f'Death-{i}-source-and-NearArm-control-v005.png')
 write(F/'README.md','Death220 actual visible sleeve/oldwaist owner control v005. No repaint/bodyerasure. NEW media UNVIEWED awaitingRootE beforeView; no sourcefit/native/Trial acceptance.\n');write(F/'source-version-status-index.json',dict(schema='Death220-sleeve-owner-F-index-v005',status='UNVIEWED_AWAIT_ROOT_E_GATE',candidate=O.as_posix(),files=[pin(p)for p in sorted(F.rglob('*'))if p.is_file()],TrialAllowed=False))
 print(json.dumps(dict(candidate=O.as_posix(),freeze=pin(O/'source-layer-freeze-v005.json'),F_canonical=F.as_posix(),F_files=len([p for p in F.rglob('*')if p.is_file()]),F_bytes=sum(p.stat().st_size for p in F.rglob('*')if p.is_file()),moved=[{'frame':r['frame'],'NearArm_to_BodyRest':r['NearArm_to_BodyRest_reassigned_pixels']}for r in rows],newmedia_Viewed=False),ensure_ascii=False))
if __name__=='__main__':main()
