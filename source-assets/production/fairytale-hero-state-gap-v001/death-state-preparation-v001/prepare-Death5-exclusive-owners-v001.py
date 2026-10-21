"""NEW candidate only: exact retained Death220 source partition; no generation, repaint or runtime writes."""
from pathlib import Path
import hashlib,json,math,shutil,sys
import numpy as np
from PIL import Image,ImageDraw,ImageFilter,ImageFont
C=Path(__file__).resolve().parent
ROOT=Path('F:/Ourgame')
OUT=C/'candidate-v001'
MEDIA=ROOT/'过程图稿与视频/2026-10-18_钟盔Death220五相源分区与落剑注册_v001'
OWNERS=['BodyRest','NearArmWithoutHand','HelmetForeground','FarHandForeground','NearHand']
# Authored visible source-contour ROIs, not skeletons/hidden sockets. Polygon
# masks classify existing source samples only; never paint replacement pixels.
NEARHAND=[
 [[153,257],[174,251],[198,257],[211,271],[215,291],[217,312],[213,328],[199,340],[178,338],[160,329],[153,309]],
 [[187,292],[205,282],[228,287],[239,305],[256,312],[270,329],[266,347],[248,365],[227,366],[207,352],[198,336],[188,319]],
 [[255,391],[273,381],[292,385],[305,402],[306,416],[322,425],[338,442],[337,459],[321,466],[299,463],[280,457],[270,444],[264,422],[254,409]],
 [[213,415],[229,402],[249,408],[260,423],[279,426],[297,437],[316,451],[312,465],[289,466],[270,460],[250,454],[230,450],[217,435]],
 [[207,417],[222,406],[241,411],[254,426],[272,431],[294,443],[311,455],[303,466],[284,465],[261,459],[240,454],[223,448],[209,433]]]
FARHAND=[
 [[296,286],[317,280],[331,288],[338,307],[350,313],[363,332],[366,352],[358,369],[343,368],[333,354],[324,347],[313,328],[300,315]],
 [[318,326],[335,318],[354,325],[362,342],[377,350],[392,374],[393,393],[383,410],[369,411],[354,401],[352,383],[342,374],[330,361]],
 [[335,396],[354,384],[371,391],[383,409],[398,415],[413,430],[427,448],[421,460],[404,460],[388,453],[368,454],[358,442],[352,424],[337,413]],
 [[391,418],[405,413],[420,421],[435,434],[444,450],[435,461],[415,461],[398,454],[387,439]],
 [[391,416],[405,412],[422,420],[438,434],[445,450],[434,462],[415,461],[396,451],[386,437]]]
HELMET=[
 [[282,45],[338,45],[343,86],[363,105],[378,140],[383,177],[376,211],[359,224],[361,244],[333,249],[293,235],[254,219],[218,200],[190,175],[200,159],[216,146],[227,126],[254,104],[278,91]],
 [[362,102],[404,104],[407,133],[392,146],[411,170],[419,210],[414,248],[398,269],[395,296],[368,302],[334,282],[303,258],[275,236],[248,213],[229,190],[236,177],[258,170],[277,149],[310,135],[345,137]],
 [[293,225],[338,218],[367,223],[389,235],[391,212],[398,198],[430,200],[435,226],[419,242],[429,269],[438,303],[432,337],[408,352],[398,379],[373,394],[346,384],[320,365],[295,340],[273,313],[257,284],[250,260],[268,252]],
 [[308,296],[343,300],[373,309],[400,322],[411,317],[417,306],[433,306],[448,320],[437,339],[421,343],[432,365],[434,393],[423,417],[409,433],[399,453],[372,464],[335,457],[308,445],[286,427],[274,405],[265,381],[261,350],[262,325],[279,315],[290,321]],
 [[270,310],[287,309],[314,314],[343,323],[371,332],[396,347],[405,341],[418,330],[434,334],[446,348],[439,367],[422,371],[412,389],[403,413],[393,432],[377,446],[351,457],[329,466],[298,462],[283,445],[275,423],[270,397],[268,365]]]
NEARARM=[
 [[191,211],[214,202],[232,219],[229,238],[215,257],[203,273],[183,279],[161,267],[157,250],[168,235]],
 [[215,230],[239,226],[256,242],[252,264],[236,282],[220,301],[201,312],[181,303],[179,280],[190,259]],
 [[230,307],[251,307],[267,323],[283,346],[296,378],[293,397],[270,411],[249,395],[237,373],[225,358],[215,339]],
 [[225,340],[248,340],[266,355],[274,377],[259,403],[242,427],[218,430],[199,416],[197,393],[207,367]],
 [[210,345],[233,344],[251,357],[263,377],[252,402],[235,424],[213,431],[197,415],[191,394],[198,371]]]

def pin(p):
 p=Path(p);b=p.read_bytes();return dict(path=p.as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def write(p,v):
 assert not p.exists(),str(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(v if isinstance(v,str)else json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def save(p,im):assert not p.exists(),str(p);p.parent.mkdir(parents=True,exist_ok=True);im.save(p)
def poly(points):
 im=Image.new('L',(512,512));ImageDraw.Draw(im).polygon([tuple(x)for x in points],fill=255);return np.asarray(im)>0

def filled_warm_region(a,points,expand):
 roi=poly(points);q=a.astype(np.int16);warm=(q[:,:,0]>=75)&(q[:,:,1]>=48)&(q[:,:,0]-q[:,:,1]>=10)&(q[:,:,1]-q[:,:,2]>=6)&(q[:,:,3]>0)&roi
 im=Image.fromarray(np.where(warm,255,0).astype(np.uint8)).filter(ImageFilter.MaxFilter(expand));ImageDraw.floodfill(im,(0,0),128);v=np.asarray(im);return ((v==255)|(v==0))&roi&(a[:,:,3]>0)
def bbox(m):
 y,x=np.where(m);return [int(x.min()),int(y.min()),int(x.max()+1),int(y.max()+1)]if len(x)else None
def native_preview(im,root):
 k=72/416.;aff=(1/k,0,root[0]-640/k,0,1/k,root[1]-490/k)
 return im.convert('RGBa').transform((1280,720),Image.Transform.AFFINE,aff,resample=Image.Resampling.BICUBIC).convert('RGBA')
def sword_preview(sword,root,hilt,angle):
 k=72/416.;w=k*.5;t=math.radians(angle);cs=math.cos(t);sn=math.sin(t);gx=640+(hilt[0]-root[0])*k;gy=490+(hilt[1]-root[1])*k
 aff=(cs/w,sn/w,99-(cs*gx+sn*gy)/w,-sn/w,cs/w,256+(sn*gx-cs*gy)/w)
 return sword.convert('RGBa').transform((1280,720),Image.Transform.AFFINE,aff,resample=Image.Resampling.BICUBIC).convert('RGBA')

def main():
 assert Path(sys.executable).resolve()==(ROOT/'tools/runtime/asset-gen/Scripts/python.exe').resolve()
 assert not OUT.exists() and not MEDIA.exists();OUT.mkdir()
 source_rows=json.loads((C/'retained-Death5-E394-reverification-before-View-v001.json').read_text(encoding='utf-8'))['rows']
 refs=json.loads((C/'retained-Ready002-and-independent-SWD-before-View-v001.json').read_text(encoding='utf-8'))
 for row in source_rows:
  for n in ['F_source','E_source']:
   f=pin(Path(row[n]));assert f['bytes']==row['bytes'] and f['sha256']==row['sha256']
 for row in refs:assert pin(Path(row['F']['path']))==row['F'] and pin(Path(row['E']['path']))==row['E']
 sword=Image.open(refs[1]['F']['path']).convert('RGBA');sa=np.asarray(sword);yy,xx=np.where(sa[:,:,3]>=128);bottom=float(np.max(yy-256)+1)*.5
 root=[242.,464.];hilts=[[183.,311.],[238.,408.],[345.,464.-bottom],[345.,464.-bottom],[345.,464.-bottom]];angles=[-20.,-8.,0.,0.,0.]
 records=[];sheets=[];owner_sheets=[];display=[]
 for i,row in enumerate(source_rows):
  src=Path(row['F_source']);im=Image.open(src).convert('RGBA');a=np.asarray(im);alpha=a[:,:,3]>0
  near=filled_warm_region(a,NEARHAND[i],5);far=filled_warm_region(a,FARHAND[i],5)&~near
  helmet=filled_warm_region(a,HELMET[i],9)&~near&~far;arm=poly(NEARARM[i])&alpha&~near&~far&~helmet
  rest=~(near|far|helmet|arm);masks=dict(BodyRest=rest,NearArmWithoutHand=arm,HelmetForeground=helmet,FarHandForeground=far,NearHand=near)
  count=np.sum(np.stack(list(masks.values())),axis=0);assert np.all(count==1)
  layers={n:np.where(m[:,:,None],a,0).astype(np.uint8)for n,m in masks.items()};assert np.array_equal(np.sum(np.stack(list(layers.values())),axis=0,dtype=np.uint16),a.astype(np.uint16))
  reconstructed=Image.new('RGBA',(512,512));owner=np.zeros_like(a);colors=[(80,90,110,255),(80,180,255,255),(225,200,80,255),(180,90,225,255),(245,130,60,255)];items=[]
  for name,color in zip(OWNERS,colors):
   layer=Image.fromarray(layers[name]);mp=OUT/f'body-masks/{name}/frame-{i}.png';lp=OUT/f'body-layers/{name}/frame-{i}.png';save(mp,Image.fromarray(np.where(masks[name],255,0).astype(np.uint8)));save(lp,layer)
   visible=masks[name]&alpha;assert np.count_nonzero(visible)>0,(i,name,'Do not silently declare an owner empty')
   owner[visible]=color;reconstructed=Image.alpha_composite(reconstructed,layer);items.append(dict(owner=name,mask=pin(mp),source_RGBA_layer=pin(lp),visible_pixels=int(np.count_nonzero(visible)),bbox=bbox(visible),known_optional_empty=False))
  assert np.array_equal(np.asarray(reconstructed),a),'Exclusive layers must alpha-compose byte-exact source'
  rp=OUT/f'reconstruction/frame-{i}.png';save(rp,reconstructed);op=OUT/f'diagnostics/owner-colors-frame-{i}.png';save(op,Image.fromarray(owner));sheets.append(im);owner_sheets.append(Image.fromarray(owner))
  dest=OUT/f'source-readcopies/Death220/frame-{i}.png';dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dest);assert pin(dest)['sha256']==row['sha256']
  bg=Image.new('RGBA',(1280,720),(24,27,32,255));bg=Image.alpha_composite(bg,sword_preview(sword,root,hilts[i],angles[i]));bg=Image.alpha_composite(bg,native_preview(im,root))
  dr=ImageDraw.Draw(bg);dr.text((30,25),f'AUTHORED SOURCE-ONLY PREVIEW Death{i} / body72 standing-equivalent / released Sword .50 / NO LGT / NOT NATIVE',fill='white');dr.line((500,490,790,490),fill=(80,85,92,255),width=1)
  dp=OUT/f'presentation/Death-{i}-body-and-released-SWD-author-proposal-1280.png';save(dp,bg);display.append(pin(dp))
  records.append(dict(frame=i,key_age_s=i*.2,source=pin(src),source_RGBA_SHA256=hashlib.sha256(a.tobytes()).hexdigest(),alpha_nonzero=int(np.count_nonzero(alpha)),alpha_bbox=bbox(alpha),alpha128_bbox=bbox(a[:,:,3]>=128),body_owners=items,source_union_RGBA_exact=True,alpha_composite_RGBA_exact=True,reconstruction=pin(rp),standing_root_measured=[242,464]if i==0 else None,ground_root_author_proposal=root,ground_root_author_choice_not_foot_lock=True,actual_hand_contact_grip=None,actual_hidden_axis=None,armor_attachments=None,weapon_released=True,weapon_author_hilt_root=hilts[i],weapon_author_clockwise_y_down_degrees=angles[i],weapon_source_grip=[99,256],weapon_scale=.5,weapon_source_contact_measured=False,terminal_weapon_floor_registration='source alpha128 rotated-core lower EDGE to sourceY464 author floor'if i>=2 else'author falling pose, no physical contact claim'))
 for row in refs:
  f=Path(row['F']['path']);dest=OUT/'source-readcopies'/((row['role']+'.png'));shutil.copy2(f,dest)
 for name,ims in [('Death220-original-row',sheets),('Death220-exclusive-owner-annotation-row',owner_sheets)]:
  sheet=Image.new('RGBA',(2560,512));
  for i,im in enumerate(ims):sheet.paste(im,(512*i,0))
  save(OUT/f'presentation/{name}.png',sheet)
 contract=dict(schema='Death220-exclusive-source-owners-and-visual-release-author-candidate-v001',source_scope='SWD001+LGT001 preparation only, no source/Content admission',native_facing=1,source_frame_count=5,source_canvas=[512,512],standing_equivalent_source_height=416,standing_display_height=72,body_scale_constant_all5=True,no_perframe_alpha_height_normalization=True,owner_order=OWNERS,body_source_layers=25,body_source_pixels_added_or_repainted=0,whole_body_used_as_BodyRest=False,exclusive_pixel_sum_and_composition_exact=True,frame_keys_s=[0,.2,.4,.6,.8],last_frame_policy='Hold actual Death frame4 from .8 until actual state exit; no gameplay death deadline',time_authority='Actual Fighter AnimationTime advanced by existing terminal presentation; no kernel/SimulationTime advance or added timer',root_policy='frame0 visible shoe-supported [242,464]; frames1..4 fixed root is an EXPLICIT AUTHOR registration proposal, not measured late standing root/COM/foot lock',weapon_inventory_unchanged=True,visual_weapon_release_only=True,no_pickup_entity_or_reward_or_damage_or_collision_change=True,weapon_source=refs[1],weapon_source_pivot=[99,256],weapon_scale=.5,weapon_floor_alpha128_lower_edge_offset_at_zero_degrees_source_px=bottom,armor_source_gap='Death-specific Chest/ShoulderNear/ShoulderFar projected5-row sources absent; minimum15 new component poses required before LGT claim',armor_stack_provisional=['IndependentSwordReleasedGround','BodyRest','ShoulderFar','Chest','NearArmWithoutHand','ShoulderNear','HelmetForeground','FarHandForeground','NearHand'],armor_stack_validated=False,rows=records,presentation_previews=display,source_pose_prior_Root_candidate_approval=True,new_layers_and_previews_Viewed=False,E_before_View_required=True,TrialAllowed=False,FinalAccepted=False)
 write(OUT/'Death220-exclusive-owners-registration-and-released-SWD-proposal-v001.json',contract)
 originals=MEDIA/'原件/源分区完整候选';originals.parent.mkdir(parents=True);shutil.copytree(OUT,originals)
 show=MEDIA/'展示副本';show.mkdir();
 for f in sorted((OUT/'presentation').glob('*.png')):shutil.copy2(f,show/f.name)
 write(MEDIA/'README.md','Death220 retained source5 partition and released sword AUTHOR proposal. Body pixels are source-exact; no LGT sources or native draw accepted. NEW media UNVIEWED; Root E preservation required before any View. No foot-lock/bone/real grip claim.\n')
 write(MEDIA/'source-version-status-index.json',dict(schema='Death220-partition-new-F-process-index-v001',status='UNVIEWED_AWAIT_ROOT_E_GATE',candidate=OUT.as_posix(),original_package=originals.as_posix(),body_source_exact=True,source5_original_generation_id=220,no_new_generation=True,armor_sources_pending=15,source_and_version_files=[pin(f)for f in sorted(MEDIA.rglob('*'))if f.is_file()],TrialAllowed=False,FinalAccepted=False))
 print(json.dumps(dict(candidate=OUT.as_posix(),F_process=MEDIA.as_posix(),body25_layer_RGBA_exact=True,new_images_Viewed=False,armor_sources_pending=15,rows=[dict(frame=r['frame'],owners=[(x['owner'],x['visible_pixels'])for x in r['body_owners']])for r in records]),ensure_ascii=False))

if __name__=='__main__':main()
