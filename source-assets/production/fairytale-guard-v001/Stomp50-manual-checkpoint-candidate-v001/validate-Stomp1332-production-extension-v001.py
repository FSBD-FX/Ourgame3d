"""Read-only old1326 + exactly six Root-approved Stomp packages; no UE launch."""
from pathlib import Path
import ast,hashlib,json
from PIL import Image
R=Path('F:/Ourgame').resolve()
OLD=R/'source-assets/production/fairytale-hero-state-gap-v001/death-state-preparation-v001/Death40-manual-checkpoint-tooling-candidate-v001/validate-Death1326-production-extension-v001.py'
OLD_SHA='0794c9af75dd341e708fead84e12f922daaddcc772c99f81a43d8a19cd9e8125'
def need(v,why):
 if not v:raise ValueError(why)
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def resolve(p):
 p=Path(p);p=(p if p.is_absolute() else R/p).resolve();need(p.is_relative_to(R),'Path escapes project');return p
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def check(x):
 need(type(x) is dict and set(x)=={'path','bytes','sha256'},'Exact real pin required');p=resolve(x['path']);b=p.read_bytes()
 need(type(x['bytes']) is int and len(b)==x['bytes'] and hashlib.sha256(b).hexdigest()==x['sha256'],'Pinned dependency changed: '+str(p));return p
def approval(x):need(x.get('is_template') is False and x.get('RootApproved') is True,'Actual non-template Root approval required')
def source(row):
 p=check(row['source'])
 with Image.open(p) as im:
  need(im.mode=='RGBA' and im.size==(512,512),'Exact512RGBA Stomp source required')
  need(hashlib.sha256(im.tobytes()).hexdigest()==row['RGBA_sha256'],'Stomp decodedRGBA differs')
  need(im.getchannel('A').getbbox() is not None and sum(im.getchannel('A').histogram()[128:])>0,'Empty Stomp source forbidden')
 return p
def rows(approval_doc):
 approval(approval_doc);need(approval_doc['schema']=='Stomp1332-Root-production-extension-v001','Typed Stomp extension required')
 need((approval_doc['expected_old_base'],approval_doc['expected_new_count'],approval_doc['expected_total'])==(1326,6,1332),'Exact1326+6 required')
 for k in ['automatic_inputs','diagnostic_damage','FinalAccepted']:need(approval_doc[k] is False,'Manual extension cannot imply injection/final acceptance')
 return approval_doc
def base_adapter(extra_paths):
 # Preserve the entire proven1254+Hurt32+Death40 gate. Only its live set
 # comparison projects out these six explicitly approved new packages.
 need(sha(OLD)==OLD_SHA,'Original frozen1326 extension helper changed')
 text=OLD.read_text(encoding='utf-8-sig');before="current={q.relative_to(R).as_posix() for q in (R/'UnrealGame/Content/Production').rglob('*') if q.is_file()}"
 after=before+'-STOMP_EXTRA_PATHS';need(text.count(before)==1,'Original extension AST shape differs')
 scope={'__file__':str(OLD),'__name__':'Stomp50_readonly_base1326_adapter','STOMP_EXTRA_PATHS':set(extra_paths)}
 exec(compile(ast.parse(text.replace(before,after)),str(OLD),'exec'),scope);return scope['validate_production_set']
def validate_production_set(base1254,files,p,workspace,checker_path):
 need(Path(workspace).resolve()==R,'Wrong workspace');a=rows(read(check(p['production_extension_pin'])))
 need(a['compiled_manifest_sha256']==p['compiled_manifest_sha256'],'Stomp approval binds another snapshot')
 manifest_pin=a['Stomp6_import_manifest_pin'];manifest=read(check(manifest_pin));receipt_pin=a['Stomp6_actual_receipt_pin'];receipt=read(check(receipt_pin));proof=read(check(a['Stomp6_independent_twoSHA_pin']))
 need(manifest['schema']=='Root-GuardStomp6-import-v001','Actual bounded Stomp import manifest required')
 need((manifest['expected_old_count'],manifest['expected_new_count'],manifest['expected_final_count'])==(1326,6,1332),'Stomp import counts differ')
 trial=read(check(manifest['root_trial_registration']));need(trial['limited_import_approved'] is True and trial['FinalAccepted'] is False,'Explicit limited Root native import approval required')
 check(manifest['source_manifest']);old_snapshot=read(check(manifest['old_compiled_snapshot']));need(old_snapshot['production_files']==1326,'Native import must preserve actual1326 baseline')
 need(a['actual_receipt_schema']==receipt['schema']=='guard-Stomp6-actual-import-v001' and receipt['success'] is True and receipt['manifest']==manifest_pin and receipt['actual_total']==1332 and receipt['FinalAccepted'] is False,'Actual six native import receipt differs')
 check(receipt['importer'])
 need(len(manifest['assets'])==len(receipt['assets'])==6,'Exactly six actual imported assets required')
 need(proof['schema']=='Stomp6-independent-import-twoSHA-v001' and proof['success'] is True and proof['verification_passes']==2 and proof['hash_mismatches']==0 and proof['old1326_unchanged_twice'] is True and proof['new6_saved_twice'] is True and proof['exact_total']==1332 and proof['receipt']==receipt_pin and proof['manifest']==manifest_pin,'Independent old/new twoSHA receipt differs')
 row_approval=read(check(a['Stomp50_row_approval_pin']));approval(row_approval);need(row_approval['schema']=='Stomp50-Root-overlay-rows-v001','Actual Stomp row approval required')
 need(row_approval['native_import_trial_record_pin']==manifest['root_trial_registration'] and row_approval['source_manifest_pin']==manifest['source_manifest'],'Scoped row facts do not bind the actual native import approval/source manifest')
 new_sources={f['object_path']:f for row in row_approval['rows'] for f in row['frames']};need(len(new_sources)==6,'Row approval six unique sources required')
 sources={x['object_path']:x for x in manifest['assets']};need(len(sources)==6 and set(sources)==set(new_sources),'Import exact mappings differ from Root-approved row source facts')
 for obj,asset in sources.items():
  frame=new_sources[obj];need(asset['component']==frame['clip'] and asset['frame']==frame['frame'] and asset['source']==frame['source'] and asset['source_RGBA_sha256']==frame['RGBA_sha256'],'Native import source/phase facts differ from approved row')
  ep=Path(asset['retained_E']['path']).resolve();need(ep.is_relative_to(Path('E:/OurGame/Knight/过程图稿与视频').resolve()),'Retained Stomp source must remain in E media root');eb=ep.read_bytes();need(len(eb)==asset['retained_E']['bytes'] and hashlib.sha256(eb).hexdigest()==asset['retained_E']['sha256']==frame['source']['sha256'],'Source retained F/E pins differ')
 need({x['actual_object_path'] for x in receipt['assets']}==set(sources),'Native imported six exact paths differ')
 old_rows={}
 for x in manifest['old_production_files']:
  rel=check(x).relative_to(R).as_posix();old_rows[rel]=dict(x,path=rel)
 need(len(old_rows)==len(manifest['old_production_files'])==1326,'Exact old1326 package pins required')
 need(old_rows=={x['path']:x for x in old_snapshot['files'] if x['path'].startswith('UnrealGame/Content/Production/')},'Native import old1326 differs from its pinned compiled snapshot')
 extra=set();saved_rows={}
 for x in receipt['assets']:
  f=new_sources[x['actual_object_path']];src=source(f);saved=check(x['saved']);rel=saved.relative_to(R).as_posix()
  need(rel.startswith('UnrealGame/Content/Production/') and rel not in old_rows and rel not in extra,'New package overlaps old1326/another source')
  expected_rel='UnrealGame/Content/'+x['actual_object_path'].split('.',1)[0].removeprefix('/Game/')+'.uasset'
  need(rel==expected_rel,'Saved package differs from object path');extra.add(rel);saved_rows[rel]=x['saved']
  need(x['component']==f['clip'] and x['frame']==f['frame'] and x['source']==f['source'] and x['actual_class']=='Texture2D' and x['actual_dimensions']==[512,512] and len(x['actual_import_filenames'])==1 and Path(x['actual_import_filenames'][0]).resolve()==src,'Actual class/dimensions/importsource differs')
  settings=x['actual_settings']
  for k,v in [('compression_settings','TC_EDITOR_ICON'),('mip_gen_settings','TMGS_NO_MIPMAPS'),('lod_group','TEXTUREGROUP_UI'),('filter','TF_BILINEAR')]:need(v in settings[k],'Actual Stomp native texture setting differs: '+k)
  need(settings['never_stream']=='True' and settings['srgb']=='True','Actual native stream/sRGB differs')
 expected=set(old_rows)|extra;need(len(expected)==1332 and {n for n in files if n.startswith('UnrealGame/Content/Production/')}==expected,'Compiled Production is not exact old1326+approved6')
 # This is explicitly a historical base validation, not a claim that the new
 # compiled snapshot has1326 packages. The fresh1332 set is checked above/below.
 old_pin=a['base_Death1326_approval_pin'];old=read(check(old_pin));old_p=dict(p,production_extension_pin=old_pin,compiled_manifest_sha256=old['compiled_manifest_sha256'])
 base_files={k:v for k,v in files.items() if k not in extra};base_adapter(extra)(base1254,base_files,old_p,R,checker_path)
 for repeat in range(2):
  for k in ['Stomp6_import_manifest_pin','Stomp6_actual_receipt_pin','Stomp6_independent_twoSHA_pin','Stomp50_row_approval_pin','base_Death1326_approval_pin']:check(a[k])
  need({x.relative_to(R).as_posix() for x in (R/'UnrealGame/Content/Production').rglob('*') if x.is_file()}==expected,'Current exact1332 set changed')
  for rel in expected:
   b=(R/rel).read_bytes();v=files[rel];need(len(b)==v['bytes'] and hashlib.sha256(b).hexdigest()==v['sha256'],'Current compiled package changed: '+rel)
  for rel,v in old_rows.items():need(files[rel]==v,'Old1326 package not retained byte-identically');check(v)
  for rel,v in saved_rows.items():need(files[rel]==dict(v,path=rel),'New saved package not equal compiled pin');check(v)
  for f in new_sources.values():source(f)
 return {'old_base':1326,'Stomp':6,'total':1332,'old_and_new_current_twoSHA':True}
