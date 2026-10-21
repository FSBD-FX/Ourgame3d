"""Native171 four-owner pixel partition candidate; never redraw/resample source.
New derived layers/diagnostics MUST be retained by Root before explicit viewing.
"""
from pathlib import Path
import datetime,hashlib,json
import numpy as np
from PIL import Image,ImageDraw
HERE=Path(__file__).resolve().parent
FAMILY=Path('F:/Ourgame/source-assets/production/fairytale-sword-primary2-v001')
SOURCE=FAMILY/'run-primary2-v004/curated'
MEASUREMENT=FAMILY/'primary2-measurement-v003/measurement-v003.json'
NAMES=['BodyRest','HelmetForeground','NearArmWithoutHand','NearHand']
# Fresh original171 lower-rim / collar seam choices, including source outer ink.
# Envelope outside the head contains only original transparent coordinates;
# this is not a y-band, bbox anatomy, material threshold or old159/158 mask.
HELMET_LOWER=[
 [[170,202],[180,207],[190,210],[200,213],[210,215],[220,217],[225,217],[230,216],[240,218],[250,220],[260,222],[270,225],[280,225],[290,230],[300,233],[310,234],[320,234],[330,233],[340,231],[350,227],[360,220]],
 [[170,212],[180,218],[190,221],[200,225],[210,227],[220,228],[230,228],[240,228],[250,230],[260,232],[270,235],[280,236],[290,240],[300,242],[310,243],[320,243],[330,242],[340,240],[350,235],[360,227]],
 [[170,207],[180,211],[190,215],[200,217],[210,220],[220,222],[230,220],[240,222],[250,224],[260,226],[270,229],[280,230],[290,235],[300,238],[310,239],[320,239],[330,238],[340,236],[350,231],[360,223]],
 [[170,204],[180,207],[190,210],[200,213],[210,214],[220,216],[230,215],[240,214],[250,215],[260,216],[270,220],[280,220],[290,224],[300,225],[310,225],[320,225],[330,224],[340,224],[350,218],[360,213]],
 [[170,206],[180,210],[190,214],[200,216],[210,218],[220,219],[230,218],[240,218],[250,220],[260,221],[270,225],[280,226],[290,230],[300,230],[310,231],[320,230],[330,230],[340,228],[350,223],[360,217]],
 [[170,205],[180,210],[190,214],[200,216],[210,218],[220,219],[230,217],[240,219],[250,221],[260,223],[270,226],[280,227],[290,232],[300,235],[310,236],[320,236],[330,235],[340,234],[350,228],[360,221]],
]
ARM=[
 [[204,227],[215,228],[225,235],[230,246],[228,257],[220,273],[214,285],[207,282],[198,277],[185,275],[173,279],[163,286],[163,274],[171,256],[181,243],[191,233]],
 [[213,239],[224,241],[230,248],[225,260],[213,272],[200,281],[191,294],[187,302],[181,295],[171,291],[159,292],[148,297],[150,283],[160,271],[174,259],[191,248],[204,242]],
 [[216,231],[228,230],[238,237],[244,249],[244,262],[253,277],[255,289],[244,286],[235,287],[229,294],[228,306],[216,297],[209,286],[206,272],[204,255],[206,241]],
 [[215,225],[228,226],[239,234],[247,246],[258,252],[272,249],[268,259],[267,270],[276,282],[264,289],[250,288],[238,282],[227,274],[216,262],[209,248],[206,237],[209,229]],
 [[215,232],[227,231],[237,238],[243,249],[244,264],[239,274],[235,278],[233,290],[240,304],[230,310],[217,310],[207,306],[201,298],[199,287],[201,271],[202,252],[206,240]],
 [[204,228],[215,229],[225,236],[230,246],[228,257],[221,273],[215,285],[207,283],[198,278],[185,276],[173,280],[164,286],[163,275],[171,257],[181,244],[192,234]],
]
# Complete visible brown cuff + glove + original edge; not the +/-4 palm replay polygon.
HAND=[
 [[163,283],[172,276],[184,273],[195,274],[205,278],[211,286],[213,293],[223,297],[231,302],[236,309],[238,317],[235,324],[230,331],[222,334],[213,334],[207,332],[202,337],[194,337],[185,332],[179,325],[175,313],[168,308],[162,302],[160,294],[160,288]],
 [[148,294],[156,289],[169,289],[182,292],[189,300],[188,312],[188,321],[195,331],[197,341],[190,349],[184,356],[171,359],[158,357],[148,352],[142,343],[141,332],[143,321],[144,311],[143,301]],
 [[229,292],[234,285],[243,283],[254,287],[261,295],[271,293],[284,293],[296,298],[304,305],[309,313],[309,321],[304,327],[298,332],[289,338],[280,342],[270,343],[260,339],[253,333],[248,326],[238,326],[230,323],[226,315],[226,305]],
 [[279,247],[288,243],[289,235],[294,228],[301,223],[311,222],[323,226],[331,233],[336,243],[338,253],[335,262],[330,269],[323,275],[313,280],[302,282],[297,287],[287,294],[276,291],[268,279],[264,265],[265,253],[270,247]],
 [[243,270],[257,270],[257,264],[259,256],[265,249],[275,244],[286,244],[297,252],[304,261],[307,273],[305,284],[299,293],[291,299],[282,303],[273,301],[265,304],[264,310],[254,317],[244,313],[237,303],[232,291],[231,278],[235,271]],
 [[163,283],[172,277],[184,274],[196,275],[206,279],[212,287],[213,293],[223,297],[232,303],[237,310],[239,318],[236,325],[230,332],[222,335],[213,336],[207,333],[202,338],[193,337],[184,331],[178,324],[174,312],[167,307],[162,301],[160,293],[160,288]],
]
SLEEVE_CUFF=[
 [[163,283],[172,276],[184,273],[195,274],[205,278],[211,286],[213,293]],
 [[148,294],[156,289],[169,289],[182,292],[189,300],[188,312]],
 [[229,292],[234,285],[243,283],[254,287],[261,295]],
 [[279,247],[270,247],[265,253],[264,265],[268,279],[276,291]],
 [[243,270],[235,271],[231,278],[232,291],[237,303],[244,313],[254,317]],
 [[163,283],[172,277],[184,274],[196,275],[206,279],[212,287],[213,293]],
]
INNER_ARM=[
 [[215,228],[225,235],[230,246],[228,257],[220,273],[214,285]],
 [[224,241],[230,248],[225,260],[213,272],[200,281],[191,294]],
 [[228,230],[238,237],[244,249],[244,262],[253,277],[255,289]],
 [[228,226],[239,234],[247,246],[258,252],[272,249]],
 [[227,231],[237,238],[243,249],[244,264],[239,274],[235,278]],
 [[215,229],[225,236],[230,246],[228,257],[221,273],[215,285]],
]
HAND_INNER=[
 [[231,302],[236,309],[238,317],[235,324],[230,331],[222,334],[213,334],[207,332],[202,337]],
 [[188,312],[188,321],[195,331],[197,341],[190,349],[184,356]],
 [[309,313],[309,321],[304,327],[298,332],[289,338],[280,342],[270,343],[260,339],[253,333],[248,326]],
 [[301,223],[311,222],[323,226],[331,233],[336,243],[338,253],[335,262],[330,269]],
 [[291,299],[282,303],[273,301],[265,304],[264,310],[254,317]],
 [[232,303],[237,310],[239,318],[236,325],[230,332],[222,335],[213,336],[207,333],[202,338]],
]
RISKS=[
 'Low glove/cuff joins belt and trouser ink; inner glove edge is a candidate split, not semantic acceptance. Full brown cuff is assigned to NearHand.',
 'New closed low fist is small; cuff top/grey sleeve ink and glove/left leg AA are uncertain. Hand includes brown cuff, not old170 open-finger pixels.',
 'Folded near sleeve crosses torso and cuff meets low fist. Grey/grey inner elbow seam is ambiguous; original far arm/hand stays BodyRest.',
 'Raised fist lies under helmet; tiny original ink/AA can be shared at fist top/helmet lower rim. NearHand has final priority. No hidden chest/far shoulder invented.',
 'Near cuff lower-right is adjacent to belt buckle. Belt/buckle must remain BodyRest; review the273,301 ->265,304 ->264,310 candidate curve.',
 'Low return differs from phase0 source; boundaries are independently listed. Glove/trouser shared ink and collar/helmet seam remain uncertain.',
]

def fact(p):
 p=Path(p);b=p.read_bytes();return {'path':p.as_posix(),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def write(name,v):
 p=HERE/name;p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('x',encoding='utf-8',newline='\n') as f:f.write(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
 return p
def polygon(points):
 im=Image.new('L',(512,512),0);ImageDraw.Draw(im).polygon([tuple(p) for p in points],fill=255);return np.asarray(im)>0
def sample(a,p):
 x,y=p;return {'xy':list(p),'rgba':a[y,x].tolist()}
def pm(a):
 return np.concatenate([a[:,:,:3].astype(np.uint32)*a[:,:,3:4],a[:,:,3:4].astype(np.uint32)*255],axis=2)

assert not (HERE/'layers').exists() and not (HERE/'proof-v001.json').exists(),'Never overwrite a partition'
assert fact(MEASUREMENT)['sha256']=='9a776415005eb1a71228360d7b14f468bc6d34db76afa554555d87bdafd2e8e4'
measure=json.loads(MEASUREMENT.read_text(encoding='utf-8'))
freeze=FAMILY/'primary2-measurement-v003/measurement-freeze-v003.json';assert fact(freeze)['sha256']=='e03de5b66bb17e9e89d9f0487361b24635682c4124b957104e1bf43ff8c30f19'
for row in json.loads(freeze.read_text(encoding='utf-8'))['files']:assert fact(row['path'])==row
colors=np.array([[70,155,230],[75,190,100],[215,70,185],[240,190,40]],dtype=np.uint8)
receipts=[];boundaries=[]
for i in range(6):
 source_path=SOURCE/f'frame-{i}.png';assert fact(source_path)==measure['frames'][i]['source']
 source=np.asarray(Image.open(source_path).convert('RGBA')).copy();assert source.shape==(512,512,4)
 lower=HELMET_LOWER[i]
 # Upper envelope includes original shell/eyes/knob and all exterior AA.
 # Lower outline follows this phase's actual rim, excludes visible cloth collar.
 helmet_points=[[155,30],[380,30],[380,lower[-1][1]]]+list(reversed(lower))+[[155,lower[0][1]-8]]
 helmet=polygon(helmet_points);arm=polygon(ARM[i]);hand=polygon(HAND[i])
 assert HAND[i]!=measure['frames'][i]['visible_near_hand_polygon_candidate']['points']
 labels=np.zeros((512,512),dtype=np.uint8);labels[helmet]=1;labels[arm & ~helmet]=2;labels[hand]=3
 owners=[labels==k for k in range(4)]
 assert np.all(sum(x.astype(np.uint8) for x in owners)==1)
 visible=source[:,:,3]>0;partial=visible & (source[:,:,3]<255);hidden=(source[:,:,3]==0)&np.any(source[:,:,:3]!=0,axis=2)
 controls=[('actual_palm_candidate',measure['frames'][i]['grip_candidate']['xy'],3),('actual_near_shoulder_cloth_design_A',measure['frames'][i]['body_design_A_candidates']['NearShoulder']['point'],2),('visible_far_glove',[348,341],0),('visible_grey_collar',[250,[225,235,229,220,224,226][i]],0),('visible_gray_leg',[240,365],0),('brown_cuff',[[184,286],[165,302],[242,306],[276,269],[247,292],[185,285]][i],3)]
 control_records=[]
 for role,point,expected in controls:
  x,y=point;assert int(labels[y,x])==expected,(i,role,point,int(labels[y,x]),expected)
  control_records.append({'role':role,'source_sample':sample(source,point),'selected_owner':NAMES[expected],'scope':'Local sanity only, not proof of full semantic contour accuracy.'})
 layers=[];layer_records=[];mask_records=[]
 for k,name in enumerate(NAMES):
  a=np.zeros_like(source);a[owners[k]]=source[owners[k]]
  assert np.array_equal(a[owners[k]],source[owners[k]]) and not np.any(a[~owners[k]])
  p=HERE/'layers'/name/f'frame-{i}.png';p.parent.mkdir(parents=True,exist_ok=True);Image.fromarray(a).save(p)
  assert np.array_equal(np.asarray(Image.open(p)),a)
  mask=HERE/'masks'/name/f'frame-{i}.png';mask.parent.mkdir(parents=True,exist_ok=True);Image.fromarray((owners[k]*255).astype(np.uint8)).save(mask)
  layer_records.append({'owner':name,'file':fact(p),'owned_coordinates':int(owners[k].sum()),'source_visible_pixels':int((owners[k]&visible).sum()),'source_partial_alpha_pixels':int((owners[k]&partial).sum()),'source_alpha0_nonzeroRGB_pixels':int((owners[k]&hidden).sum()),'visible_alpha_bbox_diagnostic_only':Image.fromarray(a).getbbox()})
  mask_records.append({'owner':name,'file':fact(mask),'binary_assignment':True});layers.append(a)
 recovered=np.sum(np.stack(layers),axis=0,dtype=np.uint16).astype(np.uint8);assert np.array_equal(recovered,source)
 composite=Image.new('RGBA',(512,512),(0,0,0,0))
 for a in layers:composite=Image.alpha_composite(composite,Image.fromarray(a))
 assert np.array_equal(pm(np.asarray(composite)),pm(source))
 diagnostics=HERE/'diagnostics';diagnostics.mkdir(exist_ok=True)
 recovered_path=diagnostics/f'frame-{i}-reconstructed-source.png';Image.fromarray(recovered).save(recovered_path)
 labels_image=np.full((512,512,3),245,dtype=np.uint8);labels_image[visible]=colors[labels[visible]]
 label_path=diagnostics/f'frame-{i}-ownership-colors.png';Image.fromarray(labels_image).save(label_path)
 overlay=source.copy();overlay[visible,:3]=((source[visible,:3].astype(np.uint16)*2+colors[labels[visible]].astype(np.uint16))//3).astype(np.uint8)
 overlay_path=diagnostics/f'frame-{i}-ownership-overlay.png';Image.fromarray(overlay).save(overlay_path)
 band=Image.new('L',(512,512),0);draw=ImageDraw.Draw(band)
 band_specs={'helmet_collar_boundary':{'points':lower,'uncertainty_source_px':2},'arm_torso_boundary':{'points':INNER_ARM[i],'uncertainty_source_px':3},'sleeve_cuff_boundary':{'points':SLEEVE_CUFF[i],'uncertainty_source_px':3},'hand_other_body_boundary':{'points':HAND_INNER[i],'uncertainty_source_px':3}}
 for spec in band_specs.values():draw.line([tuple(p) for p in spec['points']],fill=255,width=2*spec['uncertainty_source_px']+1,joint='curve')
 band_path=diagnostics/f'frame-{i}-uncertainty-review-band.png';band.save(band_path)
 boundaries.append({'frame':i,'source':fact(source_path),'manual_polygons':{'helmet':helmet_points,'near_arm':ARM[i],'full_brown_cuff_and_near_hand':HAND[i]},'candidate_boundaries':band_specs,'source_boundary_rgba_samples':{key:[sample(source,point) for point in spec['points']] for key,spec in band_specs.items()},'source_controls':control_records,'risk':RISKS[i],'actual_hidden_bones':None,'semantic_ownership_accepted':False})
 receipts.append({'frame':i,'source':fact(source_path),'layers':layer_records,'masks':mask_records,'reconstructed_source':fact(recovered_path),'ownership_colors':fact(label_path),'ownership_overlay':fact(overlay_path),'uncertainty_review_band':fact(band_path),'source_rgba_bytes_sha256':hashlib.sha256(source.tobytes()).hexdigest(),'reconstructed_rgba_bytes_sha256':hashlib.sha256(recovered.tobytes()).hexdigest(),'rgba_all_bytes_equal':True,'premultiplied_composite_equal':True,'source_alpha0_nonzeroRGB_pixels':int(hidden.sum()),'multiple_owner_coordinates':0,'unowned_coordinates':0,'candidate_polygon_visible_overlap_counts':{'helmet_arm':int((helmet&arm&visible).sum()),'helmet_hand':int((helmet&hand&visible).sum()),'arm_hand':int((arm&hand&visible).sum())},'source_controls':control_records,'semantic_ownership_accepted':False,'new_outputs_viewed':False})

boundary_file=write('candidate-boundaries-v001.json',{'schema':'native171-four-owner-manual-boundary-candidate-v1','created_local':datetime.datetime.now().astimezone().isoformat(),'frames':boundaries,'owner_names':NAMES,'measurement':fact(MEASUREMENT),'measurement_freeze':fact(freeze),'source_retention':'E208 raw / E209 actual171 six512RGBA, all original source views preceded this task','assignment':'All coordinates begin BodyRest; explicit phase-specific helmet lower rim plus outer head envelope; near sleeve excluding helmet; full brown cuff+near glove takes final priority. No automatic semantic colour segmentation.','transparent_coordinates':'Exactly one bookkeeping owner also for alpha0 and nonzero invisible RGB; no anatomy claim from transparent polygons.','helmet_scope':'Actual original bell shell, eye window/eyes, top bolt/stem and visible ink/AA; visible grey collar remains BodyRest, no hidden neck repaint.','near_hand_scope':'Full actual brown cuff and glove, fingers and original ink/AA; new explicit polygon, not copied +/-4 palm replay polygon.','future_layer_order_candidate':['BodyRest','FarShoulder','Chest','NearArmWithoutHand','NearShoulder','HelmetForeground','independentSword','NearHand'],'no_armor_or_sword_in_layers':True,'semantic_accepted':False,'new_outputs_viewed':False})
proof_file=write('proof-v001.json',{'schema':'native171-four-owner-original-RGBA-proof-v1','created_local':datetime.datetime.now().astimezone().isoformat(),'script':fact(Path(__file__)),'candidate_boundaries':fact(boundary_file),'frames':receipts,'owner_names':NAMES,'frame_count':6,'layer_count':24,'source_canvas':[512,512],'all_source_coordinates_exactly_one_owner':True,'all_source_RGBA_reconstructions_byte_exact':True,'all_premultiplied_alpha_composites_exact':True,'alpha0_nonzeroRGB_preserved':True,'source_coordinates_shifted_resampled_mirrored':False,'source_originals_changed':False,'new_anatomy_or_hidden_pixels_painted':False,'old_masks_reused':False,'measurement_uncertain_polygon_used_directly_as_owner':False,'semantic_ownership_accepted':False,'new_outputs_explicitly_viewed':False,'armor_generated_imported':False,'UE_called':False,'formal_complete_units':0})
for i in range(6):assert fact(SOURCE/f'frame-{i}.png')==measure['frames'][i]['source']
readme='''# Native171四owner分区候选

参考P1工具的“逐坐标独占、原RGBA复制”策略，重新按171六原512的可见轮廓选取各相明确像素归属。没有复用159/158mask，没有把measurement±4拳心polygon直接当全手。NearHand包括棕袖口及完整可见glove/黑边/AA；NearArm只近侧灰袖；HelmetForeground用各相下盔沿/领圈曲线及外侧head envelope，包括原盔、眼窗、顶栓、墨边AA，灰领圈留BodyRest。BodyRest还保留躯干、腰带扣、远臂/手及腿靴。

24层+24二值坐标assignment mask+24技术诊断，所有图均新派生、尚未显式查看。每坐标恰一owner，PNG保存读回像素与各owner原值一致；四层uint16求和恢复原整张RGBA逐字节，包括alpha0非零RGB，premultiplied合成相同。这证明像素保全与独占，不证明艺术语义或甲/剑遮挡正确。

重点待Root保全后实图审查：0/5拳与裤/腰带共享墨边，1闭拳外沿/袖口和左腿边缘，2灰袖/躯干及近袖口/远手，3抬拳上缘与盔下黑线，4袖口右下贴腰带扣。每相candidate-boundaries有原RGBA采样及±2/3px风险带。局部掌/袖/远手/领圈等owner控制只是sanity；不能冒称完整边缘已接受。隐藏骨/颈/胸面全不补画。

未动Source/tools公共文件、输入、旧freeze、UE/UBT/import/nativegen或台账。没有把新技术图写到媒体目录，也没有view/emit；须Root先E保全再图审。没有动作、足锁、握柄或完整内容接受。
'''
with (HERE/'README.md').open('x',encoding='utf-8',newline='\n') as f:f.write(readme)
files=[fact(p) for p in sorted(HERE.rglob('*')) if p.is_file()]
freeze_path=write('partition-freeze-v001.json',{'schema':'native171-four-owner-partition-candidate-freeze-v1','created_local':datetime.datetime.now().astimezone().isoformat(),'file_count':len(files),'total_bytes':sum(f['bytes'] for f in files),'files':files,'layer_count':24,'source_count':6,'rgba_reconstruction_exact':True,'premultiplied_composite_exact':True,'semantic_accepted':False,'new_outputs_viewed':False,'formal_complete_units':0})
for row in files:assert fact(row['path'])==row
print(json.dumps({'freeze':fact(freeze_path),'proof':fact(proof_file),'boundaries':fact(boundary_file),'files_including_freeze':len(files)+1,'bytes_including_freeze':sum(f['bytes'] for f in files)+freeze_path.stat().st_size,'layers':24,'RGBA_exact':True,'premultiplied_exact':True,'semantic_accepted':False,'new_outputs_viewed':False,'owner_visible_counts':[[f['frame'],{x['owner']:x['source_visible_pixels'] for x in f['layers']}] for f in receipts]},ensure_ascii=False,indent=2))