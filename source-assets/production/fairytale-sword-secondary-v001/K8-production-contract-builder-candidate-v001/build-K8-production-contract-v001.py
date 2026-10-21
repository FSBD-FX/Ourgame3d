"""Generate real K8 source data only. Never imports Content or enables RuntimeReady."""
from pathlib import Path
import argparse,hashlib,json,math,os,re,sys,tempfile
import numpy as np
from PIL import Image
HERE=Path(__file__).resolve().parent
ROOT=Path('F:/Ourgame')
C=ROOT/'source-assets/production/fairytale-sword-secondary-v001'
OWNERS=('BodyRest','ShoulderFar','Chest','NearArmWithoutHand','ShoulderNear','HelmetForeground','NearHand')
BODY=('BodyRest','NearArmWithoutHand','HelmetForeground','NearHand')
TARGET='/Game/Production/ArtTrials/SWDSecondary/v001'
PROFILE_ID='SWD001_K8_SourceTrial_v001'
SWORD_OBJECT='/Game/Production/FirstBatch/v002/CandidateComponents/T_military_sword_v002.T_military_sword_v002'
SETTINGS=dict(compression_settings='TC_EDITOR_ICON',mip_gen_settings='TMGS_NO_MIPMAPS',lod_group='TEXTUREGROUP_UI',filter='TF_BILINEAR',never_stream=True,srgb=True)
def need(ok,why):
 if not ok:raise ValueError(why)
def canonical(j):return (json.dumps(j,ensure_ascii=False,sort_keys=True,indent=2,allow_nan=False)+'\n').encode('utf-8')
def pin(path):
 p=Path(path).resolve(strict=True);raw=p.read_bytes();return dict(path=p.as_posix(),bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest())
def verify(p):
 need(isinstance(p,dict) and set(('path','bytes','sha256'))<=set(p),'actual path/bytes/SHA pin required')
 need(type(p['bytes']) is int and p['bytes']>0 and isinstance(p['sha256'],str) and re.fullmatch('[0-9a-f]{64}',p['sha256']),'invalid pin bytes/SHA')
 got=pin(p['path']);need(got['bytes']==p['bytes'] and got['sha256']==p['sha256'],'pin mismatch: '+p['path']);return got
def read(p):return json.loads(Path(verify(p)['path']).read_text(encoding='utf-8-sig'))
def samepin(a,b):return verify(a)==verify(b)
def relative(p):
 path=Path(p).resolve(strict=True);need(path.is_relative_to(ROOT/'source-assets'),'SourceRelativePath must be a real source-assets path');return path.relative_to(ROOT).as_posix()
def member_map(freeze):
 doc=read(freeze);base=Path(freeze['path']).parent;out={}
 for row in doc['members']:
  q=Path(row['path']) if 'path' in row else base/row['relative_path'];k=q.resolve(strict=True).as_posix();need(k not in out,'duplicate freeze member');out[k]=dict(path=k,bytes=row['bytes'],sha256=row['sha256'])
 return out
def member(members,path):
 key=Path(path).resolve(strict=True).as_posix();need(key in members,'selected source is not frozen member: '+key);return verify(members[key])
def source_png(p):
 p=verify(p);relative(p['path'])
 with Image.open(p['path']) as im:
  need(im.format=='PNG' and im.size==(512,512) and im.mode=='RGBA','source must be actual PNG512 RGBA: '+p['path']);im.load();rgba=np.array(im)
 return rgba
def bbox(mask):
 y,x=np.nonzero(mask);return [int(x.min()),int(y.min()),int(x.max())+1,int(y.max())+1] if len(x) else None
def image_facts(rgba):
 a=rgba[:,:,3];need(np.any(a>0),'empty rendered owner layer')
 return dict(canvas=[512,512],layer_alpha1_bbox=bbox(a>0),layer_alpha128_bbox=bbox(a>=128),alpha1_pixels=int(np.count_nonzero(a)),alpha128_pixels=int(np.count_nonzero(a>=128)),root_author=[256,464])
def finite_pair(v,label):
 need(isinstance(v,list) and len(v)==2 and all(type(n) in (int,float) and math.isfinite(n) for n in v),'finite pair required: '+label);return list(v)
def profile_function(contract,sha):
 # Real FProfile/FFrame/FLayer/FSourcePin types; this complete value remains disabled.
 def point(v):return '{'+','.join(repr(float(x)) for x in v)+'}'
 def layer(row):
  s=row['source'];return 'FLayer{'+json.dumps(row['object_path'])+',FSourcePin{'+json.dumps(relative(s['path']))+','+json.dumps(s['sha256'])+','+str(s['bytes'])+'ULL}}'
 lines=['const FProfile& Profile()','{',' // Metadata complete; NOT a Content import receipt or runtime admission.',' static const FProfile MetadataComplete=[](){','  FProfile P;P.RuntimeReady=false;','  P.ProfileId='+json.dumps(PROFILE_ID)+';','  P.SourceContractSha256='+json.dumps(sha)+';']
 for f in contract['frames']:
  n=f['frame'];lines+=['  P.Frames['+str(n)+'].Root='+point(f['Root'])+';','  P.Frames['+str(n)+'].Grip='+point(f['Grip'])+';','  P.Frames['+str(n)+'].Axis='+point(f['Axis'])+';','  P.Frames['+str(n)+'].Layers={{']
  lines += ['   '+layer(next(r for r in contract['layers'] if r['frame']==n and r['owner']==owner))+(',' if i<6 else '') for i,owner in enumerate(OWNERS)];lines+=['  }};']
 lines+=['  P.Sword='+layer(contract['reused_sword'])+';','  return P;',' }();',' return MetadataComplete;','}'];return '\n'.join(lines)+'\n'
def profile_span(text):
 start=text.index('const FProfile& Profile()');brace=text.index('{',start);depth=0
 for n in range(brace,len(text)):
  if text[n]=='{':depth+=1
  elif text[n]=='}':
   depth-=1
   if depth==0:return start,n+1
 raise ValueError('baseline complete Profile function not found')
def prepare(inputs,output):
 # All validations complete in memory before any final/staging output is created.
 for key in ('markers','choice','chosen'):verify(inputs[key])
 locks=json.loads((HERE/'source-locks-v001.json').read_text());freezes=locks['freezes'];maps={k:member_map(p) for k,p in freezes.items()}
 for row in locks['runtime_baseline'].values():verify(row)
 cm=read(locks['baseline_cm']);need(cm['source_files']==303 and cm['production_files']==1439 and cm['registered_tests']==cm['passed']==203 and cm['failed']==0 and cm['regression_GREEN'] is True,'baseline CM is not actual303/1439/203GREEN');suite=read(cm['full_suite']);need(len(suite['tests'])==203 and all(t['state']=='Success' for t in suite['tests']),'baseline full203 report has an unpassed ID')
 markers=read(inputs['markers']);choice=read(inputs['choice']);chosen=verify(inputs['chosen'])
 need(markers['schema']=='Root-K8-source-fit-markers-approved-for-first-native-trial-v001' and markers['RootApproved_for_source_import'] is True,'explicit Root full marker input required')
 need(choice['schema']=='Root-K5-integer-near-shoulder-choice-v001' and choice['RootApproved_for_source_import'] is True,'Root chosen K5 shoulder input required')
 need(choice['chosen_variant'] in ('A','B') and samepin(choice['chosen_near_shoulder'],chosen),'chosen actual PNG pin differs from Root choice')
 expected=C/'K5-near-shoulder-integer-fit-v003/near-shoulder-candidates'/choice['chosen_variant']/'K5.png';need(chosen==member(maps['shoulder5'],expected),'K5 shoulder is not frozen integer fit A/B')
 need(samepin(choice['frame5_corrected_body_freeze'],freezes['body5']) and samepin(choice['parent_fit_freeze'],freezes['shoulder5']),'K5 decision has stale body/shoulder parent')
 need(markers['canvas']==[512,512] and markers['display_standing_pixels']==72 and markers['authored_standing_height']==416 and markers['sword_scale']==.5 and markers['sword_pivot']==[99,256],'Root marker canvas/standing/sword constants conflict with runtime')
 marker_frames=markers['frames'];need(len(marker_frames)==8 and [f['frame'] for f in marker_frames]==list(range(8)),'all eight explicit ordered marker frames required')
 verify(markers['proof_pin'])
 b03=read(member(maps['body03'],C/'request260-body-owner-candidate-v001/four-owner-proof-v001.json'))
 b47=read(member(maps['body47'],C/'K4K5K7-body-owner-candidate-v001/four-owner-proof-v001.json'))
 b5=read(member(maps['body5'],C/'K5-body-owner-correction-v002/four-owner-proof-v002.json'))
 frames=[];rows=[]
 for k,m in enumerate(marker_frames):
  src=0 if k==6 else k;family='body03' if src<4 else 'body5' if src==5 else 'body47'
  proof=b5 if src==5 else next(f for f in (b03 if src<4 else b47)['frames'] if f['frame']==src)
  body_pin=verify(proof['source']);need(samepin(m['source_body'],body_pin) and samepin(m['body_owner_freeze'],freezes[family]),'marker canonical body/freeze source mismatch at K'+str(k))
  need(m['RootApproved_for_first_native_trial'] is True,'Root frame approval missing');root=finite_pair(m['Root'],'Root');grip=finite_pair(m['Grip'],'Grip');axis=finite_pair(m['Axis'],'Axis')
  need(root==[256,464] and all(0<=n<=512 for n in grip) and math.hypot(*axis)>1.e-6 and abs(math.hypot(*axis)-1.)<1.e-8,'ProfileValid marker constraints failed at K'+str(k))
  body=source_png(body_pin);body_stats=image_facts(body);need(body_stats['layer_alpha1_bbox'][3]==464,'canonical body alpha footline differs from Root464')
  layer_receipts=proof['layers'] if src==5 else proof['layer_receipts'];parts={};mask_pins={};sum_rgba=np.zeros((512,512,4),np.uint16);sum_mask=np.zeros((512,512),np.uint16)
  for owner in BODY:
   ref=next(t for t in layer_receipts if t['owner']==owner);p=member(maps[family],ref['layer']['path']);need(samepin(ref['layer'],p),'body proof layer pin differs');arr=source_png(p);mask_pin=member(maps[family],ref['binary_mask']['path'])
   with Image.open(mask_pin['path']) as mi:
    need(mi.size==(512,512) and mi.mode=='L','actual binary owner mask required');mask=np.array(mi)
   need(np.all((mask==0)|(mask==255)) and np.all(arr[mask==0]==0) and np.array_equal(arr[mask==255],body[mask==255]),'owner mask/RGBA source mismatch')
   sum_rgba+=arr;sum_mask+=mask;parts[owner]=(p,arr);mask_pins[owner]=mask_pin
  need(np.array_equal(sum_rgba,body) and np.all(sum_mask==255),'four body owners do not reconstruct all source RGBA exactly')
  need(samepin(m['source_near_hand'],parts['NearHand'][0]),'Root grip NearHand source pin mismatch');gx,gy=[int(round(v)) for v in grip];need(0<=gx<512 and 0<=gy<512 and int(parts['NearHand'][1][gy,gx,3])>=128,'Grip is not inside actual NearHand alpha>=128')
  af='armor03' if src<4 else 'armor457'
  for owner in ('ShoulderFar','Chest','ShoulderNear'):
   p=chosen if src==5 and owner=='ShoulderNear' else member(maps[af],Path(freezes[af]['path']).parent/'armor-layers'/owner/('K'+str(src)+'.png'))
   parts[owner]=(p,source_png(p))
  frame=dict(frame=k,source_frame=src,source_alias_frame=0 if k==6 else None,canonical_ready=k==7,Root=root,Grip=grip,Axis=axis,canonical_body=body_pin,body_owner_freeze=freezes[family],body_owner_masks=[dict(owner=o,source=mask_pins[o]) for o in BODY],alpha_root=dict(canvas=[512,512],root_author=[256,464],canonical_alpha1_bbox=body_stats['layer_alpha1_bbox'],canonical_alpha128_bbox=body_stats['layer_alpha128_bbox'],foot_alpha1=464),marker_provenance=dict(source_document=verify(inputs['markers']),approved_for_first_native_trial=m['RootApproved_for_first_native_trial'],physical_grip_axis_measured=m['physical_grip_axis_measured'],axis_is_authored_direction=markers['axis_is_authored_direction_not_measurement_of_unpainted_blade']),layer_keys=[str(k)+':'+o for o in OWNERS])
  frames.append(frame)
  for owner in OWNERS:
   p,arr=parts[owner];asset='T_SWD001_K_'+owner+'_'+format(k,'02d')+'_v001';package=TARGET+'/'+asset;parent=freezes[family if owner in BODY else 'shoulder5' if src==5 and owner=='ShoulderNear' else af]
   prov=dict(source_role='body_owner' if owner in BODY else 'integer_fitted_armor',source_png_relative=relative(p['path']),new_art_generated_by_builder=False,art_identity_role='existing_K_pose_source' if k not in (6,7) else 'K0_source_alias' if k==6 else 'canonical_Ready0_source',K6_source_alias_of_frame=0 if k==6 else None,K7_canonical_Ready0_reuse=k==7,owner_mask=mask_pins.get(owner),Root_choice_document=verify(inputs['choice']) if src==5 and owner=='ShoulderNear' else None)
   rows.append(dict(frame=k,owner=owner,source=p,source_rgba_sha256=hashlib.sha256(arr.tobytes()).hexdigest(),asset_name=asset,package_name=package,object_path=package+'.'+asset,**{'class':'Texture2D'},canvas=[512,512],source_frame=src,source_alias_frame=0 if k==6 else None,parent_freeze=parent,alpha_root=image_facts(arr),provenance=prov))
 need(len(rows)==56 and len({r['object_path'] for r in rows})==56,'56 independent target packages required')
 # K6 aliases art only: each phase keeps a distinct real target path, never invented new art.
 for owner in OWNERS:
  a=next(r for r in rows if r['frame']==0 and r['owner']==owner);b=next(r for r in rows if r['frame']==6 and r['owner']==owner);need(a['source']==b['source'] and a['object_path']!=b['object_path'],'K6 alias source/phase target inconsistency')
 sword_source=verify(locks['sword']);sword_rgba=source_png(sword_source);sword=dict(object_path=SWORD_OBJECT,source=sword_source,source_rgba_sha256=hashlib.sha256(sword_rgba.tobytes()).hexdigest(),canvas=[512,512],pivot=[99,256],scale=.5,import_new_texture=False)
 contract=dict(schema='SWD001-K8-source-contract-v001',profile_id=PROFILE_ID,owner_order=list(OWNERS),frames=frames,layers=rows,reused_sword=sword,texture_settings=SETTINGS,parents=[*freezes.values(),verify(inputs['markers']),verify(inputs['choice']),verify(markers['proof_pin'])],provenance=dict(object_paths_semantics='56 planned new phase Texture2D targets, not yet imported',source_approval='Root source-fit approval for first native trial only',K6='source art alias K0; separate phase06 targets; no new art identity',K7='canonical Ready0 source and armor reuse; separate phase07 targets',sword='existing independently rendered military sword; no new import',runtime_imported=False,FinalAccepted=False))
 raw=canonical(contract);sha=hashlib.sha256(raw).hexdigest();cp=dict(path=(Path(output)/'source-contract-v001.json').resolve().as_posix(),bytes=len(raw),sha256=sha)
 fields=('frame','owner','source','source_rgba_sha256','asset_name','package_name','object_path','class','canvas','source_frame','source_alias_frame')
 manifest=dict(schema='SWD001-K8-texture-import-manifest-v001',source_contract=cp,expected_new_texture_count=56,destination_root=TARGET,replace_existing=False,texture_settings=SETTINGS,textures=[{key:r[key] for key in fields} for r in rows],reused_sword=sword,baseline_compiled_manifest=locks['baseline_cm'],runtime_imported=False,FinalAccepted=False)
 function=profile_function(contract,sha);baseline=(HERE/'baseline/DungeonFairytaleSwordSecondaryPresentationV001.cpp').read_bytes().decode('utf-8');start,end=profile_span(baseline);eol='\r\n' if '\r\n' in baseline else '\n';projection=baseline[:start]+function.rstrip('\n').replace('\n',eol)+baseline[end:]
 pstart,pend=profile_span(projection);need(projection[:pstart]+baseline[start:end]+projection[pend:]==baseline,'whole Profile replacement changed unrelated runtime bytes')
 need(function.count('P.RuntimeReady=false;')==1 and 'RuntimeReady=true' not in function and sha not in raw.decode('utf-8'),'metadata/runtime gate or source-contract self-pin conflict')
 return {'source-contract-v001.json':contract,'texture-import-manifest-v001.json':manifest,'profile-whole-value-v001.inl':function,'projected/UnrealGame/Source/CodexDungeon/DungeonFairytaleSwordSecondaryPresentationV001.cpp':projection,'package-receipt-v001.json':dict(schema='K8-metadata-complete-package-v001',metadata_complete=True,source_contract=cp,layer_rows=56,distinct_new_texture_targets=56,source_art_frames=7,K6_alias0=True,K7_canonicalReady=True,closure_with_reused_sword=57,texture_settings=SETTINGS,profile_runtime_ready=False,actual_content_imported=False,actual_source_admitted=False,native_proven=False,FinalAccepted=False,runtime_baseline_pins=locks['runtime_baseline'])}
def write_package(package,output):
 output=Path(output).resolve();need(output.is_relative_to(HERE) and output!=HERE,'output must be NEW inside this owned candidate');need(not output.exists(),'never overwrite existing final package')
 output.parent.mkdir(parents=True,exist_ok=True);staging=Path(tempfile.mkdtemp(prefix='.'+output.name+'.pending-',dir=output.parent))
 for rel,value in package.items():
  path=staging/rel;path.parent.mkdir(parents=True,exist_ok=True);data=canonical(value) if isinstance(value,dict) else value.encode('utf-8')
  with path.open('xb') as f:f.write(data);f.flush();os.fsync(f.fileno())
 # Windows rename refuses an existing destination. No final path exists before full validation/write.
 need(not output.exists(),'concurrent output collision');os.rename(staging,output)
 return [pin(p) for p in sorted(output.rglob('*')) if p.is_file()]
def main():
 ap=argparse.ArgumentParser(description=__doc__)
 for key in ('markers','k5-choice','chosen-k5-near-shoulder'):
  ap.add_argument('--'+key,required=True,type=Path);ap.add_argument('--'+key+'-bytes',required=True,type=int);ap.add_argument('--'+key+'-sha256',required=True)
 ap.add_argument('--output',required=True,type=Path);ap.add_argument('--validate-only',action='store_true');a=ap.parse_args()
 def param(k):return dict(path=str(getattr(a,k)),bytes=getattr(a,k+'_bytes'),sha256=getattr(a,k+'_sha256'))
 try:
  package=prepare(dict(markers=param('markers'),choice=param('k5_choice'),chosen=param('chosen_k5_near_shoulder')),a.output)
  need(a.output.resolve().is_relative_to(HERE) and a.output.resolve()!=HERE,'owned output directory required')
  if a.validate_only and a.output.exists():
   expected=set(package);actual={p.relative_to(a.output).as_posix() for p in a.output.rglob('*') if p.is_file()};need(actual==expected,'existing package file set differs from exact output')
   for rel,v in package.items():need((a.output/rel).read_bytes()==(canonical(v) if isinstance(v,dict) else v.encode('utf-8')),'existing package differs: '+rel)
  files=[] if a.validate_only else write_package(package,a.output)
  print(json.dumps(dict(valid=True,metadata_complete=True,layer_rows=56,distinct_new_texture_targets=56,closure_with_reused_sword=57,source_contract=package['texture-import-manifest-v001.json']['source_contract'],profile_runtime_ready=False,actual_content_imported=False,final_package_written=not a.validate_only,files=files),ensure_ascii=False,indent=2));return 0
 except (ValueError,KeyError,OSError,TypeError,StopIteration) as e:
  print(json.dumps(dict(valid=False,reason=str(e),final_package_written=False,actual_content_imported=False),ensure_ascii=False));return 2
if __name__=='__main__':sys.exit(main())
