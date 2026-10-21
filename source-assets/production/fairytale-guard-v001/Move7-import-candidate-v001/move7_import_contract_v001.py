"""Bounded seven-component import contracts. No UE or writes at module load."""
from pathlib import Path
import hashlib,json,re,zipfile
HERE=Path(__file__).resolve().parent;ROOT=Path('F:/Ourgame').resolve()
NAMESPACE='/Game/Production/ArtTrials/EV048/v019/GuardMoveRig'
COMPONENTS=('BodyRest','NearThigh','NearShin','NearFoot','FarThigh','FarShin','FarFoot')
PARTS=('bodyrest_fixedaxe','near_thigh','near_shin','near_foot','far_thigh','far_shin','far_foot')
SOURCE_IDS=(252,250,250,250,251,251,251)
TYPE='GuardMoveSevenComponentRigDerived'

def need(v,why):
 if not v:raise ValueError(why)
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def resolve(p,root=ROOT):
 p=Path(p);return(p if p.is_absolute()else root/p).resolve()
def pin(p):
 p=Path(p).resolve();h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return dict(path=p.as_posix(),bytes=p.stat().st_size,sha256=h.hexdigest())
def check(x,root=ROOT):
 p=resolve(x['path'],root);a=pin(p);need((a['bytes'],a['sha256'])==(x['bytes'],x['sha256']),'Pinned bytes changed: '+str(p));return p
def frozen(p):
 p=Path(p)
 for x in read(p)['files']:check(x,p.parent)

def old_contracts():
 d=read(HERE/'input-pins-v001.json')['files']
 for x in d.values():check(x)
 cm=read(check(d['old_compiled_snapshot']));m=read(check(d['old_manual_input']));ext=read(check(d['old_production_extension']))
 need(cm['production_files']==1364 and cm['strict_registered_tests']==196 and cm['source_files']==273,'Actual v1401364/196/273 baseline required')
 need(m['snapshot_manifest_pin']==d['old_compiled_snapshot']and ext['compiled_manifest_sha256']==d['old_compiled_snapshot']['sha256'],'Historical Dodge/Guard profile not bound to exact old CM')
 need(m['source_profile_prereg_pin']==d['old_Guard_known44_prereg']and m['Stomp50_row_approval_pin']==ext['Stomp50_row_approval_pin']==d['old_Guard_Stomp50_approval'],'Old Guard44/50 contracts changed')
 need(ext['schema']=='Dodge1364-Root-production-extension-v001'and ext['is_template']is False and ext['RootApproved']is True and ext['expected_total']==1364 and ext['FinalAccepted']is False,'Actual historical Dodge1364 approval changed')
 for k in ['Dodge32_import_manifest_pin','Dodge32_native_receipt_pin','Dodge32_independent_twoSHA_pin']:need(ext[k]==d[k],'Historical Dodge import changed')
 receipt=read(check(d['Dodge32_native_receipt_pin']));independent=read(check(d['Dodge32_independent_twoSHA_pin']))
 need(receipt['success']is True and receipt['total_production_files']==1364 and independent['success']is True and independent['exact_total']==1364 and independent['old1332_unchanged_twice']is True and independent['new32_saved_twice']is True,'Actual old Dodge import evidence changed')
 old=[x for x in cm['files']if x['path'].startswith('UnrealGame/Content/Production/')]
 return old,d

def validate_layout(m,root=ROOT):
 need(m['schema']=='Root-GuardMove7-native-import-v001'and m['presentation_type']==TYPE,'Exact derived seven-component manifest type required')
 need((m['expected_old_count'],m['expected_new_count'],m['expected_final_count'])==(1364,7,1371),'Exact1364+7=1371 required')
 need(m['namespace']==NAMESPACE and m['replace_existing']is False,'Exact new namespace/no replacement required')
 assets=m['assets'];need(len(assets)==7 and tuple(x['component']for x in assets)==COMPONENTS,'Exact seven component owners/order required')
 need(len({x['object_path']for x in assets})==len({x['saved_path']for x in assets})==7,'Duplicate package/object identity')
 for c,p,nid,x in zip(COMPONENTS,PARTS,SOURCE_IDS,assets):
  name=f'T_GuardMoveRig_{c}_v001';package=NAMESPACE+'/'+name
  need(x['source_part']==p and type(x['source_native_batch_id'])is int and x['source_native_batch_id']==nid and 'frame'not in x and 'NativeSourceId'not in x,'Component source owner cannot become a whole-body animation frame/native ID')
  need((x['name'],x['destination_path'],x['package_path'],x['object_path'])==(name,NAMESPACE,package,package+'.'+name),'Destination identity changed')
  need(resolve(x['saved_path'],root)==root/'UnrealGame/Content'/Path(package.removeprefix('/Game/')+'.uasset'),'Package substituted outside bounded destination')

def load_sources(decode_rgba=True):
 if decode_rgba:from PIL import Image
 _,inputs=old_contracts();table=read(check(inputs['source7_surface18']));review=read(check(inputs['Root_preparation_review']))
 need(review['schema']=='Root-Guard-Rest252-seven-part-author-preparation-review-v001'and review['PreparationAllowed']is True and review['RuntimeTrialAllowed']is False and review['Move6Accepted']is False and review['FinalAccepted']is False,'Root E572 preparation authority differs')
 check(review['viewed_board']);retention=read(check(review['E_retention']));need(retention['verification_passes']==2 and retention['source_and_member_hash_mismatches']==0,'E572 author trial retention failed')
 need(table['marker_count']==18 and table['source_RGBA_immutable']is True and table['TrialAllowed']is False and table['FinalAccepted']is False and table['per_part_or_per_pose_rescale']is False,'Exact source7/18 authored closure changed')
 need(tuple(x['part']for x in table['parts'])==PARTS,'Source owner table changed')
 pre=read(check(inputs['source_pre_render_freeze']));need(pre['markers']==inputs['source7_surface18']and pre['source7']==[x['source']for x in table['parts']],'Pre-render source7 pins differ')
 for x in pre['source7']:check(x)
 assets=[];packets={}
 for c,part,nid in zip(COMPONENTS,table['parts'],SOURCE_IDS):
  p=check(part['source']);need(part['native_component_source_id']==nid and part['retained_member_byte_equal']is True and part['actual_source_View_after_E']is True,'Component source approval/owner differs')
  ep=check(part['retention_index']);e=read(ep);need(e['verification_passes']==2 and e['source_and_member_hash_mismatches']==0,'Source E565/E553/E556 retention failed')
  packet=check(e['packet'])if ep not in packets else packets[ep];packets[ep]=packet
  matches=[x for x in e['files']if(x['bytes'],x['sha256'])==(part['source']['bytes'],part['source']['sha256'])and '/curated/'in x['member']]
  need(len(matches)==1,'Exactly one curated member required in source E packet');member=matches[0]['member'];need(not Path(member).is_absolute()and '..'not in Path(member).parts,'Invalid retained member')
  for repeat in range(2):
   with zipfile.ZipFile(packet)as z:b=z.read(member)
   need(len(b)==part['source']['bytes']and hashlib.sha256(b).hexdigest()==part['source']['sha256'],'Two-pass retained source member bytes changed')
  alpha=None
  if decode_rgba:
   with Image.open(p)as im:
    need(im.format=='PNG'and im.mode=='RGBA'and im.size==(512,512),'Exact original RGBA512 PNG required')
    need(hashlib.sha256(im.tobytes()).hexdigest()==part['source_RGBA_sha256'],'Source decoded RGBA changed')
    alpha=sum(v>0 for v in im.getchannel('A').getdata());need(0<alpha<512*512,'Nonempty transparent component required')
    for mark in part['artist_surface_markers'].values():need(list(im.getpixel(tuple(mark['xy'])))==mark['actual_RGBA']and mark['actual_RGBA'][3]>0,'Retained author surface-point pixel changed')
  name=f'T_GuardMoveRig_{c}_v001';package=NAMESPACE+'/'+name
  assets.append(dict(component=c,source_part=part['part'],source_native_batch_id=nid,source=part['source'],source_RGBA_sha256=part['source_RGBA_sha256'],source_pixel_sha256=part['source_RGBA_sha256'],source_mode='RGBA',source_canvas=[512,512],source_alpha_nonzero=alpha,artist_surface_markers=part['artist_surface_markers'],whole_kit_conversion_to_Rest_art_units=part['whole_kit_conversion_to_Rest_art_units'],name=name,destination_path=NAMESPACE,package_path=package,object_path=package+'.'+name,saved_path=(ROOT/'UnrealGame/Content'/Path(package.removeprefix('/Game/')+'.uasset')).as_posix(),E_retention_index=part['retention_index'],E_packet=e['packet'],E_curated_member=member))
 digest=hashlib.sha256(json.dumps([dict(component=x['component'],source=x['source'],source_RGBA_sha256=x['source_RGBA_sha256'],object_path=x['object_path'])for x in assets],sort_keys=True,separators=(',',':')).encode()).hexdigest()
 return assets,inputs,review,digest

def verify_old(old,root=ROOT):
 need(len(old)==len({x['path']for x in old})==1364,'Exact1364 distinct old packages required')
 for x in old:need(x['path'].startswith('UnrealGame/Content/Production/'),'Non-production old path');check(x,root)
def exact_membership(m,after,root=ROOT):
 expected={resolve(x['path'],root)for x in m['old_production_files']}
 if after:expected|={resolve(x['saved_path'],root)for x in m['assets']}
 actual={p.resolve()for p in(root/'UnrealGame/Content/Production').rglob('*')if p.is_file()}
 need(actual==expected and len(actual)==(1371 if after else 1364),'Production exact old1364'+('+new7'if after else'')+' membership differs')

def load_manifest(p,decode_rgba=True):
 m=read(p);validate_layout(m);assets,inputs,review,digest=load_sources(decode_rgba)
 # Embedded Unreal Python uses pinned host RGBA metrics rather than requiring Pillow.
 host=read(HERE/'Move7-source-import-contract-v001.json')['assets']
 for i,(x,y)in enumerate(zip(m['assets'],assets)):
  if not decode_rgba:y['source_alpha_nonzero']=host[i]['source_alpha_nonzero']
  need(x==y and type(x['source_alpha_nonzero'])is int and 0<x['source_alpha_nonzero']<512*512,'Exact original source7/E/author/identity differs')
 old,_=old_contracts();need(m['old_production_files']==old and m['old_compiled_snapshot']==inputs['old_compiled_snapshot']and m['historical_Dodge_and_Guard_contract_pins']=={k:inputs[k]for k in ['old_manual_input','old_production_extension','old_Guard_known44_prereg','old_Guard_Stomp50_approval','Dodge32_import_manifest_pin','Dodge32_native_receipt_pin','Dodge32_independent_twoSHA_pin']},'Old1364/Guard44+50/Dodge contracts rebound')
 need(m['source_table_pin']==inputs['source7_surface18']and m['Root_source_review_pin']==inputs['Root_preparation_review']and m['source_closure_digest']==digest and m['source7_RGBA512_host_verified']is True,'Exact source closure/host gate differs')
 frozen(check(m['import_tool_candidate_freeze']));need(m['runtime_verified']is False and m['TrialAllowed']is False and m['FinalAccepted']is False,'Import-only cannot claim runtime/final acceptance')
 return m

def approval(p,m):
 a=read(p);need(a['schema']=='Root-GuardMove7-limited-import-approval-v001'and a['is_template']is False and a['RootApproved']is True and a['limited_import_approved']is True,'Actual explicit Root approval required; candidate template rejects')
 need(a['approval_method']=='Root CLI --approve-limited-import'and a['manifest_pin']==pin(m['manifest_path'])and a['source_closure_digest']==m['source_closure_digest']and a['Root_source_review_pin']==m['Root_source_review_pin'],'Root approval not bound to exact manifest/source/E572')
 need(a['expected_old_count']==1364 and a['expected_new_count']==7 and a['expected_final_count']==1371 and a['replace_existing']is False and a['TrialAllowed']is False and a['RuntimeTrialAllowed']is False and a['FinalAccepted']is False,'Limited import scope differs')
 return a

def validate_receipt_assets(m,r):
 validate_layout(m);actual=r['assets'];need(len(actual)==7,'Native receipt needs exactly seven assets');by={x['component']:x for x in actual};need(set(by)==set(COMPONENTS)and len(by)==7,'Native receipt repeats/omits owner')
 enums={'compression_settings':('TextureCompressionSettings','TC_EDITOR_ICON'),'mip_gen_settings':('TextureMipGenSettings','TMGS_NO_MIPMAPS'),'lod_group':('TextureGroup','TEXTUREGROUP_UI'),'filter':('TextureFilter','TF_BILINEAR')}
 for x in m['assets']:
  a=by[x['component']];need(a['source']==x['source']and a['source_RGBA_sha256']==x['source_RGBA_sha256']and a['source_native_batch_id']==x['source_native_batch_id']and a['actual_object_path']==x['object_path'],'Native source owner/provenance differs')
  need(a['actual_class']=='Texture2D'and a['actual_dimensions']==[512,512],'Actual saved Texture2D512 required')
  need(len(a['actual_import_filenames'])==1 and resolve(a['actual_import_filenames'][0])==resolve(x['source']['path']),'Actual import filename differs')
  need(resolve(a['saved']['path'])==resolve(x['saved_path'])and type(a['saved']['bytes'])is int and a['saved']['bytes']>0 and re.fullmatch('[0-9a-f]{64}',a['saved']['sha256']),'Actual saved package path/pin differs')
  s=a['actual_settings'];need(set(s)==set(enums)|{'never_stream','srgb'}and s['never_stream']==s['srgb']=='True','Actual UI/sRGB/neverstream readback differs')
  for k,(enum,member)in enums.items():need(re.fullmatch(r'<'+enum+r'\.'+member+r': [0-9]+>',s[k])is not None,'Actual texture setting differs: '+k)
