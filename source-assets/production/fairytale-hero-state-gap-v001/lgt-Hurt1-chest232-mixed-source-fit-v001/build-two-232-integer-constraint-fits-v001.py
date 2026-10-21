from pathlib import Path
import hashlib,json,shutil
import numpy as np
from PIL import Image,ImageDraw,ImageFont
BASE=Path('F:/Ourgame/source-assets/production/fairytale-hero-state-gap-v001');HERE=Path(__file__).resolve().parent;OUT=HERE/'candidate-v001';MEDIA=Path('F:/Ourgame/过程图稿与视频/2026-10-18_钟盔Hurt1胸衣232双整数约束试装诊断_v001')
PREV=BASE/'lgt-hurt4-finite-owner-translation-review-v002/candidate-v002';CHEST=BASE/'lgt-Hurt1-chest232-extraction-v001/run-Hurt1-Chest-native232-HD-v001/curated/frame-0.png'
def pin(p):
 b=p.read_bytes();return {'path':p.as_posix(),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def save(rel,im):
 p=OUT/rel;p.parent.mkdir(parents=True,exist_ok=True);assert not p.exists();im.save(p);return p
def write(rel,v):
 p=OUT/rel;p.parent.mkdir(parents=True,exist_ok=True);assert not p.exists();p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');return p
def main():
 assert not OUT.exists() and not MEDIA.exists();OUT.mkdir()
 assert pin(CHEST)['sha256']=='0057e59b057494ba9306f9157ca6efbbbc7a7d0af056c871f49245baa6d072e2'
 c=json.loads((PREV/'Hurt227-own-five-partition-12-integer-armor-mounts-SWD050-contract-v001.json').read_text(encoding='utf-8'));r=c['rows'][1];a=np.array(Image.open(CHEST));body=np.array(Image.open(r['body_source']['path']));layers={}
 for e in r['body_partition']:layers[e['owner']]=Image.open(e['layer']['path']).convert('RGBA')
 for name in ['ShoulderNear','ShoulderFar']:layers[name]=Image.open(PREV/f'armor-layers/{name}/frame-1.png').convert('RGBA')
 layers['SWD']=Image.open(PREV/'weapon-layers/SWD/frame-1.png').convert('RGBA')
 mask=Image.fromarray(np.where(a[:,:,3]>=128,255,0).astype(np.uint8));ImageDraw.floodfill(mask,(0,0),128);holes=np.array(mask)==0;yy,xx=np.indices((512,512));hole=holes&(xx>=211)&(xx<242)&(yy>=225)&(yy<270);hy,hx=np.where(hole);assert len(hx)>100;center=[float(hx.mean()),float(hy.mean())];opening=[round(center[0]),round(center[1])]
 beltA=[274,279];beltB=[290,273];armB=[200,251];assert a[beltA[1],beltA[0],3]>=128 and body[armB[1],armB[0],3]>=128
 variants=[('belt-aligned',[beltB[0]-beltA[0],beltB[1]-beltA[1]]),('visible-upperarm-aperture-aligned',[armB[0]-opening[0],armB[1]-opening[1]])]
 rows=[];images=[];font=lambda n:ImageFont.truetype('C:/Windows/Fonts/arial.ttf',n)
 for name,delta in variants:
  shifted=np.zeros_like(a);dx,dy=delta;xs=max(0,-dx);xe=min(512,512-dx);ys=max(0,-dy);ye=min(512,512-dy);shifted[ys+dy:ye+dy,xs+dx:xe+dx]=a[ys:ye,xs:xe];assert np.count_nonzero(shifted[:,:,3])==np.count_nonzero(a[:,:,3]);save(f'armor/{name}-Chest232-integer.png',Image.fromarray(shifted));layers['Chest']=Image.fromarray(shifted)
  whole=Image.new('RGBA',(512,512))
  for layer in c['rows'][1]['stack']:whole=Image.alpha_composite(whole,layers[layer])
  p=save(f'whole/{name}-Hurt1-LGT-SWD.png',whole);images.append(whole);rows.append({'variant':name,'source':pin(CHEST),'integer_delta':delta,'new_buckle_worldsource_candidate':[beltA[0]+dx,beltA[1]+dy],'existing_visible_buckle_B':beltB,'buckle_residual_to_actual':[beltA[0]+dx-beltB[0],beltA[1]+dy-beltB[1]],'negative_aperture_center_mapped':[center[0]+dx,center[1]+dy],'visible_upperarm_artist_surface_B':armB,'aperture_residual_to_artist_surface':[center[0]+dx-armB[0],center[1]+dy-armB[1]],'whole':pin(p),'acceptance':False})
 plate=Image.new('RGBA',(1536,570),(45,48,54,255));d=ImageDraw.Draw(plate);original=Image.open(r['body_source']['path']).convert('RGBA');plate.alpha_composite(original,(0,48));d.text((12,12),'Exact227 Hurt1 body / no redraw',font=font(22),fill='white')
 for i,(name,_) in enumerate(variants):plate.alpha_composite(images[i],((i+1)*512,48));d.text(((i+1)*512+8,12),name,font=font(20),fill='white')
 save('presentation/Hurt1-232-two-constraint-sourcefits-UNREVIEWED.png',plate.convert('RGB'))
 close=Image.new('RGBA',(1440,450),(45,48,54,255));d=ImageDraw.Draw(close)
 for i,im in enumerate([original]+images):crop=im.crop((100,195,340,335)).resize((480,280),Image.Resampling.NEAREST);close.alpha_composite(crop,(i*480,45));d.text((i*480+8,10),['original227','232 belt fit','232 arm-opening fit'][i],font=font(22),fill='white')
 save('presentation/Hurt1-232-own-body-versus-two-torsofits-2x-UNREVIEWED.png',close.convert('RGB'))
 report=write('Chest232-mixednative-singlefit-two-constraints-v001.json',{'schema':'Chest232-Hurt1-mixednative-two-integer-constraint-review-v001','source_chest232':pin(CHEST),'actual_View_after_E444':True,'source_negative_armhole':{'actual_alpha128_enclosed_hole_pixels':len(hx),'centroid_xy':center,'rounded_artist_anchor':opening,'sample_RGBA':a[opening[1],opening[0]].tolist(),'method':'Enclosedtransparentalpha128componentwithinexplicitarmholeROI; no opaqueblack cavity atthiscenter.'},'visible_upperarm_artist_B':{'xy':armB,'RGBA':body[armB[1],armB[0]].tolist(),'meaning':'Actualvisiblegrayupperarmsurface fromown227partition; author proposedattachment, NOT hiddenwristbone orsocket.'},'actual_buckle_A_B':{'sourceA':beltA,'sourceRGBA':a[beltA[1],beltA[0]].tolist(),'bodyB':beltB,'bodyRGBA':body[beltB[1],beltB[0]].tolist()},'correction_to_earlier87px_inference':'Earlierbody[154264] isouterneararmcloth, not anobservedaperturesocket;87pxconstraint wasoverstatedasphysicalattachment. Thisdiagnosticusesactualupperarm200251 authorproposal, stillmustbevisuallyreviewed andnohiddenjointclaim.','variants':rows,'mixed_source_density':'Chest232independentsingle scale .17928286852589642 versusold228fourrow .26011560693641617. No claim4same native/sharedextract. Onlybodydisplaycanvas88.6153846/standing416 andSword.50constant.','near_far_sources_unchanged':[229,231],'old228_source_or_blackpixels_edited':False,'new_images_Viewed':False,'canonical_F_media':MEDIA.as_posix(),'TrialAllowed':False,'native_accepted':False})
 write('candidate-freeze-v001.json',{'files':[pin(p) for p in sorted(OUT.rglob('*')) if p.is_file()],'script':pin(Path(__file__)),'TrialAllowed':False})
 (MEDIA/'原件').mkdir(parents=True);shutil.copytree(OUT,MEDIA/'原件/单帧两约束诊断完整包');(MEDIA/'展示副本').mkdir()
 for p in (OUT/'presentation').iterdir():shutil.copyfile(p,MEDIA/'展示副本'/p.name)
 (MEDIA/'来源-版本-状态索引.json').write_text(json.dumps({'date':'2026-10-18','version':'v001','status':'UNVIEWED_NEW_SINGLE_SOURCEFIT_DIAGNOSTIC','source':OUT.as_posix(),'report':pin(report),'files':[pin(p) for p in sorted(MEDIA.rglob('*')) if p.is_file()]},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps({'F_canonical':MEDIA.as_posix(),'files':sum(p.is_file() for p in MEDIA.rglob('*')),'bytes':sum(p.stat().st_size for p in MEDIA.rglob('*') if p.is_file()),'report':pin(report),'variants':rows,'newmedia_View':False},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
