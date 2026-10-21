"""Read-only exact1254+Hurt32+Death40 production gate used by unchanged Known44 checks."""
from pathlib import Path
import hashlib,json
from PIL import Image
R=Path('F:/Ourgame').resolve()
def need(v,why):
 if not v:raise ValueError(why)
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def resolve(p):
 p=Path(p);p=(p if p.is_absolute() else R/p).resolve();need(p.is_relative_to(R),'Dependency escapes project');return p
def fact(p):
 p=resolve(p);b=p.read_bytes();return dict(path=p.as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def check(x):
 need(type(x) is dict and set(x)=={'path','bytes','sha256'},'Exact real pin required');p=resolve(x['path']);v=fact(p);need(v['bytes']==x['bytes'] and v['sha256']==x['sha256'],'Pinned dependency changed: '+str(p));return p
def retained_check(x):
 need(type(x) is dict and set(x)=={'path','bytes','sha256'},'Exact retained pin required');p=Path(x['path']).resolve();need(p.is_relative_to(Path('E:/OurGame/Knight/过程图稿与视频').resolve()),'Death retained source must stay in E media root')
 b=p.read_bytes();need(len(b)==x['bytes'] and hashlib.sha256(b).hexdigest()==x['sha256'],'E-retained source changed');return p
def native_settings(s):
 for k,v in [('compression_settings','TC_EDITOR_ICON'),('mip_gen_settings','TMGS_NO_MIPMAPS'),('lod_group','TEXTUREGROUP_UI'),('filter','TF_BILINEAR')]:need(v in s.get(k,''),'Native texture setting differs: '+k)
 need(s.get('never_stream')=='True' and s.get('srgb')=='True','Native stream/sRGB differs')
def source_rgba(row):
 p=resolve(row['source']);need(fact(p)['bytes']==row['source_bytes'] and fact(p)['sha256']==row['source_sha256'],'Source PNG changed')
 with Image.open(p) as im:
  need(im.mode=='RGBA' and im.size==(512,512),'Source must be512RGBA');need(hashlib.sha256(im.tobytes()).hexdigest()==row['source_RGBA_sha256'],'Decoded sourceRGBA changed')
  h=im.getchannel('A').histogram();used=sum(h[1:]);core=sum(h[128:]);need(used==row['source_alpha_nonzero_pixels'] and core==row['source_alpha128_pixels'],'Source alpha metadata changed')
  need((list(im.getchannel('A').getbbox()) if used else None)==row['source_alpha_bbox'],'Source alpha bbox changed')
  empty=row['known_optional_empty'];need((used==core==0) if empty else used>0 and core>0,'Unexpected empty source')
 return p
def validate_production_set(base1254,files,p,workspace,checker_path):
 need(Path(workspace).resolve()==R and len(base1254)==1254,'Exact Guard base1254 required')
 approval=read(check(p['production_extension_pin']))
 need(approval['schema']=='Death1326-Root-production-extension-v001' and approval['RootApproved'] is True and approval['is_template'] is False,'Real Root1326 extension approval required')
 need(approval['compiled_manifest_sha256']==p['compiled_manifest_sha256'] and approval['expected_old_base']==1254 and approval['expected_total']==1326,'Extension binds wrong snapshot/count')
 need(approval['automatic_inputs'] is False and approval['diagnostic_damage'] is False and approval['FinalAccepted'] is False,'Manual preparation cannot imply native/final acceptance')
 hm=read(check(approval['Hurt32_manifest_pin']));hrp=check(approval['Hurt32_actual_receipt_pin']);hr=read(hrp);hv=read(check(approval['Hurt32_independent_twoSHA_pin']))
 need(hm['asset_count']==32 and hm['namespace']=='/Game/Production/ArtTrials/EV048/v017/HeroLeatherHurt' and len(hm['assets'])==32,'Hurt exact32 scope differs')
 need(hr['success'] is True and len(hr['assets'])==32 and hr['manifest']==approval['Hurt32_manifest_pin'],'Hurt native receipt differs')
 need(hv['success'] is True and hv['old1254_twoSHA_unchanged'] is True and hv['new32_saved_twoSHA_unchanged'] is True and hv['exact_total']==1286 and hv['receipt']==approval['Hurt32_actual_receipt_pin'],'Hurt twoSHA receipt differs')
 dm=read(check(approval['Death40_Root_import_manifest_pin']));am=read(check(approval['Death40_author_source_manifest_pin']));dr=read(check(approval['Death40_actual_receipt_pin']));dv=read(check(approval['Death40_independent_twoSHA_pin']))
 check(approval['Death40_author_freeze_pin']);need(dm['candidate_freeze']==approval['Death40_author_freeze_pin'] and dm['source_manifest']==approval['Death40_author_source_manifest_pin'],'Death source/author freeze differs')
 need(dm['namespace']==am['namespace']=='/Game/Production/ArtTrials/EV048/v019/HeroLeatherDeath' and (dm['expected_old_count'],dm['expected_new_count'],dm['expected_final_count'])==(1286,40,1326),'Death scope/count differs')
 need(len(dm['assets'])==len(am['assets'])==len(dr['assets'])==40 and am['replace_existing'] is False and dm['replace_existing'] is False,'Exact40/nooverwrite differs')
 need(dr['success'] is True and dr['manifest']==approval['Death40_Root_import_manifest_pin'] and dr['total_production_files']==1326,'Death actual receipt absent/different')
 need(dv['success'] is True and dv['old1286_unchanged_twice'] is True and dv['new40_saved_twice'] is True and dv['exact_total']==1326 and dv['verification_passes']==2 and dv['hash_mismatches']==0 and dv['receipt']==approval['Death40_actual_receipt_pin'] and dv['manifest']==approval['Death40_Root_import_manifest_pin'],'Death independent twoSHA receipt absent/different')
 expected=set(base1254);saved_rows=[]
 for manifest,receipt in [(hm,hr),(am,dr)]:
  sources={x['object_path']:x for x in manifest['assets']};need(len(sources)==len(manifest['assets']),'Duplicate sourceobject')
  need({x['actual_object_path'] for x in receipt['assets']}==set(sources),'Native exact object set differs')
  for x in receipt['assets']:
   a=sources[x['actual_object_path']];source=source_rgba(a)
   need(x['actual_class']=='Texture2D' and x['actual_dimensions']==[512,512] and len(x['actual_import_filenames'])==1 and Path(x['actual_import_filenames'][0]).resolve()==source,'Native class/dimensions/importfilename differs')
   native_settings(x.get('actual_settings_raw',x.get('actual_settings',{})))
   saved=check(x['saved']);rel=saved.relative_to(R).as_posix();need(rel not in expected,'Production extension duplicates base/another package');expected.add(rel);saved_rows.append((rel,x['saved']))
   if manifest is am:
    need(a['known_optional_empty'] is False,'Death empty layer forbidden');z=next(t for t in dm['assets'] if t['object_path']==a['object_path']);need(z['source']==fact(source) and z['source_RGBA_sha256']==a['source_RGBA_sha256'],'Root Death source differs fromauthor')
 need(len(expected)==1326 and {n for n in files if n.startswith('UnrealGame/Content/Production/')}==expected,'Compiled Production must be exact Guard1254+Hurt32+Death40')
 for repeat in range(2):
  for key in ['Hurt32_manifest_pin','Hurt32_actual_receipt_pin','Hurt32_independent_twoSHA_pin','Death40_Root_import_manifest_pin','Death40_author_source_manifest_pin','Death40_actual_receipt_pin','Death40_independent_twoSHA_pin','Death40_author_freeze_pin']:check(approval[key])
  for a in hm['assets']:source_rgba(a)
  for a in am['assets']:
   source=source_rgba(a);z=next(t for t in dm['assets'] if t['object_path']==a['object_path']);ep=retained_check(z['retained_E']);need(source.read_bytes()==ep.read_bytes(),'Death source40 F/E byte comparison differs')
  current={q.relative_to(R).as_posix() for q in (R/'UnrealGame/Content/Production').rglob('*') if q.is_file()};need(current==expected,'Current Production has missing/arbitrary extras')
  for rel in expected:
   v=fact(R/rel);row=files[rel];need(v['bytes']==row['bytes'] and v['sha256']==row['sha256'],'Compiled Production live pin changed')
  for rel,row in saved_rows:check(row);need(row['bytes']==files[rel]['bytes'] and row['sha256']==files[rel]['sha256'],'New package differs fromactual saved receipt')
 return dict(old_base=1254,Hurt=32,Death=40,total=1326,old_and_new_current_twoSHA=True)
