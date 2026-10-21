from pathlib import Path
import hashlib,json,math,sys
from PIL import Image
import numpy as np
HERE=Path(__file__).resolve().parent;OUT=HERE/'prepared-v001';assert not OUT.exists();OUT.mkdir()
ROOT=Path('F:/Ourgame');BASE=ROOT/'source-assets/production/fairytale-hero-state-gap-v001'
SRC=BASE/'lgt-Hurt4-Chest233-unified-assembly-v001/candidate-v003'
CONTRACT=SRC/'Hurt227-own-five-partition-12-integer-armor-mounts-SWD050-contract-v001.json'
REVIEW=SRC.parent/'independent-actual-sourcefit-review-after-E454-v003.json'
HANDOFF=SRC/'Root-unifiedChest233-own-correctmask-LGT-SWD-fourfit-handoff-v003.json'
NAMESPACE='/Game/Production/ArtTrials/EV048/v017/HeroLeatherHurt'
SWORD=ROOT/'source-assets/production/first-unit-animation-v002/components/military-sword-clean-v001.png'
SWORD_OBJECT='/Game/Production/FirstBatch/v002/CandidateComponents/T_military_sword_v002.T_military_sword_v002'
STACK=['BodyRest','ShoulderFar','Chest','NearArmWithoutHand','ShoulderNear','HelmetForeground','FarHandForeground','IndependentSword','NearHand']
BODY=['BodyRest','NearArmWithoutHand','HelmetForeground','FarHandForeground','NearHand']
ARMOR=['ShoulderFar','Chest','ShoulderNear']
def pin(p):
 b=p.read_bytes();return {'path':p.as_posix(),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def write(name,v):
 p=OUT/name;assert not p.exists();p.write_text(v if isinstance(v,str) else json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');return p
def bbox(m):
 y,x=np.where(m);return None if not len(x) else [int(x.min()),int(y.min()),int(x.max()+1),int(y.max()+1)]
def rgba(p):
 with Image.open(p)as im:assert im.size==(512,512)and im.mode=='RGBA';return np.array(im)
def shaRGBA(a):return hashlib.sha256(a.tobytes()).hexdigest()
assert pin(CONTRACT)['sha256']=='b7e7a27454160e8ec40f15a6f2d3327f60b63015199de240f7d448ff7656192a'
assert pin(REVIEW)['sha256']=='a8a2c4c236d9c98c9ba128ee0612485b8f323da17b4b6bdf6d2b7589c3efa473'
assert pin(HANDOFF)['sha256']=='80c9f222a8811d95aa8b0af913ef39950818a553f22978b931775a395961bf61'
assert pin(SWORD)['sha256']=='2efb5519fb3c7ed5a63e58d00c84e39aa02355274af36b43c1775570badded5a'
c=json.loads(CONTRACT.read_text(encoding='utf-8'));review=json.loads(REVIEW.read_text(encoding='utf-8'));assert not review['blocking_source_static_findings']
ep=Path(review['E_gate']['manifest']['path']);assert pin(ep)==review['E_gate']['manifest'];records=[]
def walk(v):
 if isinstance(v,dict):
  if 'sha256'in v and'retained_relative'in v:records.append(v)
  for z in v.values():walk(z)
 elif isinstance(v,list):
  for z in v:walk(z)
walk(json.loads(ep.read_text(encoding='utf-8')))
assert not (ROOT/'UnrealGame/Content/Production/ArtTrials/EV048/v017/HeroLeatherHurt').exists()
assets=[];frames=[];bodyproof=[];usednames=set()
for row in c['rows']:
 i=row['frame'];assert row['duration_ms']==100 and row['body_canvas_constant']==72*512/416 and row['standing_height_basis']==416
 bodyentries={e['owner']:e for e in row['body_partition']};armorentries={e['component']:e for e in row['armor_mounts']};assert set(bodyentries)==set(BODY)and set(armorentries)==set(ARMOR)
 originals=rgba(Path(row['body_source']['path']));assert pin(Path(row['body_source']['path']))==row['body_source']
 bodyarrays=[];masks=[];framepaths={};rawRGBA={}
 for name in BODY+ARMOR:
  pp=bodyentries[name]['layer']if name in BODY else armorentries[name]['translated'];p=Path(pp['path']);assert pin(p)==pp;a=rgba(p)
  suffix=p.relative_to(SRC).as_posix();hits=[x for x in records if x['sha256']==pp['sha256']and Path(x['retained_relative']).as_posix().endswith(suffix)];assert hits,(name,i)
  e=ep.parent/hits[0]['retained_relative'];assert p.read_bytes()==e.read_bytes();empty=bool(not np.any(a[:,:,3]));expectedempty=name=='FarHandForeground'and i>0;assert empty==expectedempty
  n=f'T_Fairytale_Hurt_{name}_{i:03d}_v001';assert n not in usednames;usednames.add(n);package=NAMESPACE+'/'+n;op=package+'.'+n;framepaths[name]=op;rawRGBA[name]=shaRGBA(a)
  assets.append({'component':name,'family':'body_source_partition'if name in BODY else'brown_LGT_armor','frame':i,'native_source_ids':[227]if name in BODY else[{'Chest':233,'ShoulderNear':229,'ShoulderFar':231}[name]],'source':p.as_posix(),'source_bytes':pp['bytes'],'source_sha256':pp['sha256'],'source_RGBA_sha256':rawRGBA[name],'source_mode':'RGBA','source_canvas':[512,512],'source_alpha_nonzero_pixels':int(np.count_nonzero(a[:,:,3])),'source_alpha128_pixels':int(np.count_nonzero(a[:,:,3]>=128)),'source_alpha_bbox':bbox(a[:,:,3]>0),'known_optional_empty':empty,'empty_reason':'Exhaustiveexclusivebodypartition; no visiblefarhandforegroundinthispose. Notmissing/generationfallback.'if empty else None,'E454_retained_relative':hits[0]['retained_relative'],'E454_byte_exact':True,'name':n,'package_path':package,'object_path':op,'expected_object_class':'Texture2D'})
  if name in BODY:
   mp=Path(bodyentries[name]['mask']['path']);assert pin(mp)==bodyentries[name]['mask'];m=np.array(Image.open(mp));assert set(np.unique(m)).issubset({0,255});masks.append(m>0);bodyarrays.append(a.astype(np.uint16))
 assert np.all(np.sum(np.stack(masks),axis=0)==1);assert np.array_equal(np.sum(np.stack(bodyarrays),axis=0),originals.astype(np.uint16))
 b=row['author_Grip_Axis'];g=b['Grip_xy'];axis=b['Axis_xy'];unit=[math.cos(math.atan2(axis[1],axis[0])),math.sin(math.atan2(axis[1],axis[0]))];root=row['pairedshoe_root'];assert b['weapon_scale_constant']==.50 and originals[g[1],g[0],3]>=128
 rendered=[n for n in STACK if not(n=='FarHandForeground'and i>0)]
 frames.append({'frame':i,'duration_ms':100,'sample_interval_ms':[i*100,(i+1)*100],'textures':framepaths,'ground_root_source_xy':root,'Grip_source_xy':g,'Axis_artist_raw_xy':axis,'Axis_artist_unit_xy':unit,'Axis_clockwise_y_down_degrees':math.degrees(math.atan2(axis[1],axis[0])),'axis_role':'Authoredbladeholdangle; no hiddenbone/shaftaxis measuredfrombarebody. Normalizeangle/axis; neveruse rawaxislengthasweaponscale.','weapon_scale':.50,'optional_empty':{'FarHandForeground':i>0},'declared_stack_slots':9,'expected_nonempty_render_layers':rendered,'expected_nonempty_draw_count_including_sword':len(rendered),'source_body':row['body_source'],'source_body_RGBA_sha256':shaRGBA(originals)})
 bodyproof.append({'frame':i,'exclusive_owner_count_one_all512canvas':True,'sum_5layers_all_RGBA_exact_to227':True,'source_whole_RGBA_sha256':shaRGBA(originals)})
assert len(assets)==32 and len(frames)==4 and sum(a['known_optional_empty']for a in assets)==3
sourceclosure=hashlib.sha256(json.dumps([{'component':a['component'],'frame':a['frame'],'PNG_SHA':a['source_sha256'],'RGBA_SHA':a['source_RGBA_sha256'],'object_path':a['object_path']}for a in assets],sort_keys=True,separators=(',',':')).encode('utf-8')).hexdigest()
lock=write('Hurt-source-review-lock-and-32-source-proof-v001.json',{'schema':'Hurt-source-static-review-runtime-preparation-lock-v001','source_contract':pin(CONTRACT),'source_handoff':pin(HANDOFF),'worker_independent_actual_E454_review':pin(REVIEW),'Root_E454_review':'Root actualfull4/torso/Readyjoin acceptedfornextscopednative trialcandidate; noFinalAccepted/no-pop. RootnowexplicitlyrequestsHurt4nativeintegration preparation.','E454_manifest':pin(ep),'E454_Root_twoSHA_zero_difference':True,'all_32_F_E_bytes_exact':True,'source_closure_digest':sourceclosure,'four_body_RGBA_reconstruction':bodyproof,'original_frozen_trialallowed_false_not_modified':True,'Root_requested_runtime_preparation':True,'runtime_activated_by_this_bundle':False,'actual_import_receipt':None,'FinalAccepted':False,'residuals_preserved':{'Hurt1_new_minus_old_buckle_source_px':[-10,14],'Ready_minus_Hurt3_clasp_display_px':[-1.0167999740253666,2.687937062937068],'oldmotionwarnings_preserved':True,'notfootlock_notbone_notzeroPop':True}})
manifest=write('import-Hurt32-v001.json',{'schema':'frozen-Hurt32-scoped-native-import-prepared-v001','namespace':NAMESPACE,'asset_count':32,'assets':assets,'canvas_px':[512,512],'replace_existing':False,'texture_settings':{'compression_settings':'TC_EDITOR_ICON','mip_gen_settings':'TMGS_NO_MIPMAPS','lod_group':'TEXTUREGROUP_UI','never_stream':True,'srgb':True},'scope':'Only32alreadyE454retainedbody/LGTtextures. ExistingindependentSwordisreused. Whole4/offlineSword4/proofsarenotimportassets.','Root_static_review_lock':pin(lock),'source_closure_digest':sourceclosure,'namespace_actual_content_absent_at_prepare':True,'expected_optional_empty_assets':3,'import_permitted_for_Root_scoped_trial_preparation':True,'actual_import_performed':False,'actual_import_receipt':None,'runtime_accepted':False,'FinalAccepted':False})
profile=write('Hurt-runtime-profile-data-v001.json',{'schema':'Hurt-fourphase-rawsource-profile-prepared-v001','profile_id':'EV048-v017-HeroLeatherHurt-v001','state':'Hurt','scope':'SWD+LGT Hurt4 only','namespace':NAMESPACE,'import_manifest':pin(manifest),'source_review_lock':pin(lock),'source_closure_digest':sourceclosure,'canvas_source_px':[512,512],'standing_height_source_px':416,'standing_display_height_px':72.,'body_canvas_display_px':72*512/416,'source_to_display_scale':72/416,'body_scale_constant_all_frames':True,'source_body_heights_not_perframe_normalized':True,'native_facing':1,'durations_ms':[100]*4,'duration_ms':400,'loop':False,'timeline':'UseactualkernelHurtstate/eventage. [0,100),[100,200),[200,300),[300,400) sample0..3. At400ms followexistingstatepriority/transition; profilemustnotdelaygameplayorloop/hold. Death/interruptpriorityownedbykernel/HUDagent.','stack_back_to_front':STACK,'body_and_armor_texture_slots_per_frame':8,'declared_total_slots_including_independent_sword':9,'known_optional_empty_policy':{'component':'FarHandForeground','frames':[1,2,3],'texture_source_exists_and_imported':True,'load_validate_source_empty_then_skip_draw':True,'never_count_empty_as_rendered':True,'never_treat_missing_texture_as_known_empty':True},'whole_body_fallback':'No WholeBody texture imported. BodyRest isapartition, neveraWholeBody surrogate. Missingmandatorylayer/profilemustclose thiscandidatepath, notfakecompletion.','independent_sword':{'source':pin(SWORD),'object_path':SWORD_OBJECT,'source_grip_xy':[99,256],'native_blade_axis':[1,0],'weapon_scale':.50,'new_sword_raster_imported':False},'facing_and_geometry':{'body_all_layers_mirrored_together':True,'NearFar_semantic_layer_order_not_swapped':True,'right_world_point':'Ground + (72/416) * (HeroSourcePoint - GroundRootSource)','left_world_point':'Ground + (72/416) * (-(HeroSourcePoint.x-GroundRoot.x), HeroSourcePoint.y-GroundRoot.y)','sword_HeroSourcePoint':'Grip + .50 * R(atan2(artistAxis.y,artistAxis.x)) * (SwordSourcePoint-[99,256])','facing_sword_transform':'ApplysameactorXreflectiontocompleteweaponmatrix/texture; mirroredaxis alonewithouttexturereflection isnotassumed equivalent. Displayaxis=(Facing*UnitAxis.x,UnitAxis.y).','ground_root_role':'Pairedvisible-soleartistregistrationfromE422; notbone/COM/footlock ormovementposition.'},'frames':frames,'native_receipt':None,'compiled_profile_receipt':None,'actual_runtime_trial_activated':False,'FinalAccepted':False})
def arr(name,rows):return 'inline constexpr double '+name+'[4][2] = {\n'+''.join('    {'+', '.join(format(float(x),'.17g')for x in row)+'},\n'for row in rows)+'};\n'
inl='// Prepared data only; not included in actual Source. JSON is the profile SSoT.\nnamespace FairytaleHurtPreparedV001 {\ninline constexpr int FrameCount = 4;\ninline constexpr double DurationSeconds = .4;\ninline constexpr double FrameSeconds = .1;\ninline constexpr double SourceCanvasSize = 512.;\ninline constexpr double StandingSourceHeight = 416.;\ninline constexpr double StandingDisplayHeight = 72.;\ninline constexpr double BodyCanvasDisplay = 72. * 512. / 416.;\ninline constexpr double SwordScale = .50;\n'+arr('GroundRoot',[f['ground_root_source_xy']for f in frames])+arr('Grip',[f['Grip_source_xy']for f in frames])+arr('ArtistAxisRaw',[f['Axis_artist_raw_xy']for f in frames])+arr('ArtistAxisUnit',[f['Axis_artist_unit_xy']for f in frames])+'inline constexpr bool FarHandOptionalEmpty[4] = {false,true,true,true};\ninline constexpr int ExpectedNonemptyDrawCountWithSword[4] = {9,8,8,8};\n} // No engine hook, clock, assetload orstatepriority is authored here.\n'
constants=write('Hurt-frame-constants-prepared-v001.inl',inl)
handoff=write('HANDOFF.md',f'''32 textures only, exact E454 originals, no PNG duplication. Proposed unique namespace `{NAMESPACE}`; it was absent in actual Content at preparation. Root must recheck before import and use replace_existing=false.

Import table: import-Hurt32-v001.json. Profile SSoT: Hurt-runtime-profile-data-v001.json. Data-only C++ constants are provided for the HUD owner; nothing is written into actual Source. Each frame has five exclusive body layers plus Chest/Near/Far, with the existing independent military sword .50 inserted before NearHand. FarHandForeground1..3 are declared empty source owners: all32 assets still exist/load; skip those three draws, never fabricate rendered counts. Slots9; nonempty counts9/8/8/8. No WholeBody/offlineSword raster import or BodyRest-as-WholeBody fallback.

Ground roots, source grips and authored axes are copied from reviewed contracts. Body512canvas uses416standing→72display, one88.6153846canvas acrossfourposes. Source axes are artistic choices, not bone measurements. Facing must reflect all texture geometry and the complete sword transform together; keep near/far layer order. Actual Hurt age and priority come from gameplay/HUD, not a new animationclock.400ms nonloop4x100 is presentation sampling, never gameplay delay.

All32source PNG SHA/RGBA SHA and E454 retention paths are recorded. Body5layers reconstruct each227 RGBA exactly. Original warnings, readonly-mask amendment and pose/join residuals remain in source references. This is resource/profile preparation for Root's scoped trial, not actual import, native proof, FinalAccepted, zero-pop or foot-lock. No UE/API/actualSource/Content/tools/ledger edits.
''')
freeze=write('prepared-package-freeze-v001.json',{'schema':'Hurt32-small-runtime-prepared-freeze-v001','files':[pin(p)for p in sorted(OUT.iterdir())if p.is_file()],'script':pin(Path(__file__)),'sourcePNGcopies':0,'new_visual_media':0,'actualSource_Content_Roottools_ledger_UE_modified':False,'native_API_calls':0})
print(json.dumps({'folder':OUT.as_posix(),'manifest':pin(manifest),'profile':pin(profile),'source_lock':pin(lock),'constants':pin(constants),'freeze':pin(freeze),'assets':len(assets),'optional_empty':3,'file_count':sum(p.is_file()for p in OUT.iterdir()),'bytes':sum(p.stat().st_size for p in OUT.iterdir()if p.is_file()),'namespace':NAMESPACE,'new_visual_media':0,'actual_import_performed':False},ensure_ascii=False,indent=2))
