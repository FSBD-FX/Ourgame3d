"""Read-only exact Production extension gate; no UE, receipt writes, or source edits."""
from pathlib import Path
import hashlib,json,runpy

HURT_NAMESPACE='/Game/Production/ArtTrials/EV048/v017/HeroLeatherHurt'
HURT_MANIFEST_SHA='bca13780eec91568e53609e366aa06b201efeeed9256c53ef83d6a6d2ad9eb1f'
HURT_CONFIG_SHA='2fe5f9cbd9a781ba81951b922fce035d9882b9cfd6137af005b1776e849dfac6'
HURT_IMPORTER_SHA='1f8bd0919d47c9a68898820f5b7f430cf84a3b4a541f12e25dfba66f5e823058'
APPROVAL_SCHEMA='guard-known44-Root-production-extension-Hurt32-v004'

def need(value,why):
 if not value:raise ValueError(why)
def read(path):return json.loads(Path(path).read_text(encoding='utf-8-sig'))
def fact(path):
 path=Path(path).resolve();data=path.read_bytes()
 return {'path':path.as_posix(),'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()}
def resolve(workspace,path):
 path=Path(path);return (path if path.is_absolute()else workspace/path).resolve()
def checked_pin(workspace,pin):
 need(type(pin)is dict and set(pin)=={'path','bytes','sha256'},'Actual extension pin missing or malformed')
 p=resolve(workspace,pin['path']);actual=fact(p)
 need(actual['bytes']==pin['bytes']and actual['sha256']==pin['sha256'],'Extension pinned input changed: '+str(p))
 return p

def validate_production_set(baseline1254,compiled_files,prereg,workspace,checker_path):
 """Called only in place of the old line100 set equality, with all other checks intact."""
 workspace=Path(workspace).resolve();prefix='UnrealGame/Content/Production/'
 base=set(baseline1254);compiled={n for n in compiled_files if n.startswith(prefix)}
 need(len(base)==1254 and all(n.startswith(prefix)for n in base),'Expected exact validated old1254 baseline')
 extpin=prereg.get('production_extension_pin')
 if extpin is None:
  need(compiled==base,'Production extras require explicit Root-approved extension pin')
  return {'production_extension_used':False,'production_files':1254,'Hurt_native_receipt':None}
 approval_path=checked_pin(workspace,extpin);approval=read(approval_path)
 need(approval['schema']==APPROVAL_SCHEMA and approval['RootApproved']is True and approval['is_template']is False,'Root actual production extension approval absent')
 need(fact(checked_pin(workspace,approval['profile_source_checker_pin']))==fact(checker_path)and fact(checked_pin(workspace,approval['extension_validator_pin']))==fact(__file__),'Root extension checker/validator binding differs')
 need(approval['compiled_manifest_sha256']==prereg['compiled_manifest_sha256'],'Extension approval binds another compiled snapshot')
 need(approval['baseline_files']==1254 and approval['extension_files']==32 and approval['final_files']==1286 and approval['namespace']==HURT_NAMESPACE,'Exact approved extension counts/namespace differ')
 need(approval['baseline_guard_import_receipt_pin']==prereg['actual_native_import_receipt_pin']and approval['baseline_guard_twoSHA_pin']==prereg['independent_import_two_pass_receipt_pin'],'Extension approval binds another Guard baseline')
 for key in ['baseline_guard_import_receipt_pin','baseline_guard_twoSHA_pin']:checked_pin(workspace,approval[key])
 importer_pin=approval['Hurt_importer_pin'];config_pin=approval['Hurt_import_validator_config_pin'];manifest_pin=approval['Hurt_import_manifest_pin']
 importer=checked_pin(workspace,importer_pin);config=checked_pin(workspace,config_pin);manifest=checked_pin(workspace,manifest_pin)
 need(importer_pin['sha256']==HURT_IMPORTER_SHA and config_pin['sha256']==HURT_CONFIG_SHA and manifest_pin['sha256']==HURT_MANIFEST_SHA,'Unreviewed Hurt import preparation substituted')
 # These pins MUST be real future artifacts. Null template fields fail before any admission.
 native_pin=approval['Hurt_actual_native_import_receipt_pin'];twoSHA_pin=approval['Hurt_independent_twoSHA_verification_pin']
 native_path=checked_pin(workspace,native_pin);proof_path=checked_pin(workspace,twoSHA_pin)
 # Reuse only the already reviewed host input/RGBA functions. main() is never invoked.
 host=runpy.run_path(str(importer));cfg,m,old,targets,objects=host['load']();host['source_RGBA'](m)
 need(fact(config)==fact(host['CONFIG'])and cfg['import_manifest']==manifest_pin,'Hurt importer/config/manifest chain differs')
 need({resolve(workspace,p).relative_to(workspace).as_posix()for p in old}==base,'Hurt baseline differs from validated Guard old1254')
 rc=read(native_path);proof=read(proof_path)
 need(rc['schema']=='Hurt32-actual-native-import-v002'and rc['success']is True and len(rc['assets'])==32,'Actual successful native Hurt32 import absent')
 need(rc['manifest']==manifest_pin and rc['config']==config_pin and rc['importer']==importer_pin,'Actual Hurt32 receipt binds other inputs')
 need(rc['old1254_twoSHA_unchanged']is True and rc['total_production_files']==1286 and rc['loaded_and_saved_Texture2D_objects']==32,'Actual Hurt import baseline/count incomplete')
 preflight=read(checked_pin(workspace,rc['host_RGBA_preflight']))
 need(preflight['schema']=='Hurt32-host-source-preflight-v002'and preflight['success']is True and preflight['config']==config_pin and preflight['manifest']==manifest_pin and preflight['importer']==importer_pin and preflight['source_PNG_and_decoded_RGBA32_exact']is True,'Actual import host source/RGBA preflight differs')
 need(proof['schema']=='Hurt32-independent-native-receipt-verification-v002'and proof['success']is True and proof['old1254_twoSHA_unchanged']is True and proof['new32_saved_twoSHA_unchanged']is True and proof['exact_total']==1286 and proof['receipt']==native_pin,'Actual independent old1254/new32 twoSHA proof absent')
 need({r['actual_object_path']for r in rc['assets']}==objects,'Actual native Hurt32 object set differs')
 byobject={r['object_path']:r for r in m['assets']};extra=set()
 for r in rc['assets']:
  e=byobject[r['actual_object_path']]
  need(r['actual_class']=='Texture2D'and r['actual_dimensions']==[512,512]and r['native_UI_settings_verified']is True,'Actual native Hurt texture class/dimensions/UI verification differs')
  need(r['actual_settings_raw']==cfg['expected_native_settings_raw'],'Actual native Hurt UI settings differ')
  need(r['actual_import_filenames']==[str(resolve(workspace,e['source']))],'Actual native Hurt source filename differs')
  need(r['source_png_sha256']==e['source_sha256']and r['source_RGBA_sha256']==e['source_RGBA_sha256']and r['known_optional_empty']is e['known_optional_empty'],'Hurt source metadata or optional-empty status differs')
  saved=checked_pin(workspace,r['saved']);need(saved==Path(e['saved_path']).resolve()and saved in targets,'Hurt saved target escaped approved namespace')
  name=saved.relative_to(workspace).as_posix();extra.add(name)
  need(name in compiled_files and all(compiled_files[name][k]==r['saved'][k]for k in ['bytes','sha256']),'Saved Hurt package differs from actual compiled snapshot')
 need(len(extra)==32 and not base&extra and compiled==base|extra,'Compiled Production is not exact old1254 plus approved Hurt32')
 # Independently recheck actual disk and every frozen old/new byte/SHA twice now.
 host['old_twice'](old,set(map(Path,old))|targets)
 for repeat in range(2):
  for r in rc['assets']:checked_pin(workspace,r['saved'])
 return {'production_extension_used':True,'approval_pin':extpin,'Hurt_native_receipt':native_pin,'Hurt_twoSHA_proof':twoSHA_pin,'production_files':1286,'extension_textures':32,'Guard_known_unique_unchanged':44,'GPU_compile_finish_claimed':False,'FinalAccepted':False}
