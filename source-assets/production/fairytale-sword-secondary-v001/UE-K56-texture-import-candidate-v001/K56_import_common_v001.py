"""Small shared K56 gates. No unreal import and no project mutation."""
from pathlib import Path
import hashlib,json,re,subprocess,sys
sys.dont_write_bytecode=True
ROOT=Path('F:/Ourgame');HERE=Path(__file__).resolve().parent
NAMESPACE='/Game/Production/ArtTrials/SWDSecondary/v001'
DISK=ROOT/'UnrealGame/Content/Production/ArtTrials/SWDSecondary/v001'
CM=ROOT/'source-assets/production/backups/v147-SWDStepAudio303-1439-203GREEN-v001/compiled-source-manifest.json'
CM_SHA='ae00569bad81eae953b989b964ed2592e6f1e8e0dff43b81163358c43bb3007a'
OWNERS=('BodyRest','ShoulderFar','Chest','NearArmWithoutHand','ShoulderNear','HelmetForeground','NearHand')
SETTINGS={'compression_settings':'TC_EDITOR_ICON','mip_gen_settings':'TMGS_NO_MIPMAPS','lod_group':'TEXTUREGROUP_UI','filter':'TF_BILINEAR','never_stream':True,'srgb':True}
OLD_RECEIPT=ROOT/'docs/production/first-batch-v2/evidence/HeroPrimary1Bridge258-v146-v001/Root-native-import-v001/import-receipt.json'

def need(v,message):
 if not v:raise AssertionError(message)
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def pin(p):
 p=Path(p).resolve();b=p.read_bytes();return {'path':p.as_posix(),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def shape_pin(r):
 need(set(r)=={'path','bytes','sha256'} and Path(r['path']).is_absolute(),'Pin must be absolute path/bytes/SHA256')
 need(type(r['bytes']) is int and r['bytes']>0 and re.fullmatch('[0-9a-f]{64}',r['sha256']) is not None,'Malformed byte pin')
def checked(r,base=None):
 p=Path(r['path'])
 if not p.is_absolute():
  need(base is not None and '..' not in p.parts,'Relative pin requires confined explicit root');p=(base/p).resolve();need(p.is_relative_to(base.resolve()),'Escaped pin')
 q=pin(p);need(q['bytes']==r['bytes'] and q['sha256']==r['sha256'],'Pin mismatch: '+str(p));return p.resolve()
def write_new(p,d):
 p=Path(p).resolve();need(p.parent.is_dir() and not p.exists(),'Fresh output and existing parent required')
 with p.open('x',encoding='utf-8',newline='\n') as f:json.dump(d,f,ensure_ascii=False,indent=2);f.write('\n')
 return pin(p)
def tool_pins():return [pin(HERE/n) for n in ('K56_import_common_v001.py','ue-import-K56-v001.py','verify-K56-import-v001.py','run-K56-native-import-v001.ps1')]
def validate_shape(m,c):
 need(m['schema']=='SWD001-K8-texture-import-manifest-v001','Wrong manifest schema');shape_pin(m['source_contract'])
 need(m['expected_new_texture_count']==56 and m['destination_root']==NAMESPACE and m['replace_existing'] is False,'Exclusive56 target contract differs')
 need(m['texture_settings']==SETTINGS,'Texture settings must equal actual old14 SRGBtrue contract')
 rows=m['textures'];need(len(rows)==56 and len(c['layers'])==56,'Exactly56 rows required')
 expected={(f,o) for f in range(8) for o in OWNERS};keys=[(r['frame'],r['owner']) for r in rows];ckeys=[(r['frame'],r['owner']) for r in c['layers']]
 need(set(keys)==expected and len(set(keys))==56 and set(ckeys)==expected and len(set(ckeys))==56,'Missing/duplicate owner/frame')
 contract={k:r for k,r in zip(ckeys,c['layers'])}
 need(len(c['frames'])==8 and {r['frame'] for r in c['frames']}==set(range(8)),'Contract frame8 coverage differs')
 frames={r['frame']:r for r in c['frames']}
 for r in rows:
  f,o=r['frame'],r['owner'];need(type(f) is int,'Frame must be integer');shape_pin(r['source'])
  need(re.fullmatch('[0-9a-f]{64}',r['source_rgba_sha256']) is not None,'Source RGBA digest missing')
  name=f'T_SWD001_K_{o}_{f:02d}_v001';pkg=NAMESPACE+'/'+name
  need(r['asset_name']==name and r['package_name']==pkg and r['object_path']==pkg+'.'+name,'Target naming/path differs')
  need(r['class']=='Texture2D' and r['canvas']==[512,512],'Only Texture2D RGBA512 allowed')
  for k in ('frame','owner','source','source_rgba_sha256','asset_name','package_name','object_path','class','canvas','source_frame','source_alias_frame'):
   need(r[k]==contract[f,o][k],'SourceContract lineage differs: '+str((f,o,k)))
  sf=0 if f==6 else f;alias=0 if f==6 else None
  need(r['source_frame']==sf and r['source_alias_frame']==alias,'Source alias semantics differ')
  need(frames[f]['source_frame']==sf and frames[f]['source_alias_frame']==alias and frames[f]['canonical_ready']==(f==7),'Frame alias/canonicalReady differs')
 for o in OWNERS:
  a=next(r for r in rows if r['frame']==0 and r['owner']==o);b=next(r for r in rows if r['frame']==6 and r['owner']==o)
  need(a['source']==b['source'] and a['source_rgba_sha256']==b['source_rgba_sha256'],'K6 must use exact K0 source')
 sword=m['reused_sword'];shape_pin(sword['source']);need(sword['pivot']==[99,256] and sword['scale']==.5,'Existing sword pivot/scale differs')
 need(not sword['object_path'].startswith(NAMESPACE+'/') and sword['object_path'] not in {r['object_path'] for r in rows},'Sword must only be reused')
 return sorted(rows,key=lambda r:(r['frame'],OWNERS.index(r['owner'])))
def saved_path(r):return DISK/(r['asset_name']+'.uasset')
def load_inputs(manifest,manifest_sha,compiled_manifest,compiled_sha,decode=False):
 manifest=Path(manifest).resolve();need(re.fullmatch('[0-9a-f]{64}',manifest_sha) is not None and pin(manifest)['sha256']==manifest_sha,'Actual manifest pin required')
 compiled_manifest=Path(compiled_manifest).resolve();need(compiled_manifest==CM.resolve() and compiled_sha==CM_SHA and pin(CM)['bytes']==421789 and pin(CM)['sha256']==CM_SHA,'Current pinned CM ae00569b required')
 m=read(manifest);c=read(checked(m['source_contract']));rows=validate_shape(m,c)
 for r in rows:
  p=checked(r['source']);need(p.is_relative_to((ROOT/'source-assets').resolve()),'PNG source must be in project source-assets')
 checked(m['reused_sword']['source'])
 if decode:
  from PIL import Image
  import numpy as np
  for r in rows:
   with Image.open(r['source']['path']) as im:
    im.load();need(im.format=='PNG' and im.mode=='RGBA' and im.size==(512,512),'Native source must be PNG RGBA512');a=np.array(im);need(int(a[:,:,3].min())==0 and int(a[:,:,3].max())>0,'Transparent visible source layer required')
   need(hashlib.sha256(a.tobytes()).hexdigest()==r['source_rgba_sha256'],'Decoded source RGBA SHA differs')
  for fr in c['frames']:
   f=fr['frame'];body=Image.open(checked(fr['canonical_body']));need(body.mode=='RGBA' and body.size==(512,512),'Canonical body must be RGBA512');target=np.array(body);union=np.zeros_like(target);occupancy=np.zeros((512,512),np.uint8)
   for o in ('BodyRest','NearArmWithoutHand','HelmetForeground','NearHand'):
    r=next(r for r in rows if r['frame']==f and r['owner']==o);a=np.array(Image.open(r['source']['path']));mask=a[:,:,3]>0;occupancy+=mask;union[mask]=a[mask]
   need((occupancy<=1).all() and np.array_equal(union,target),'Canonical body RGBA/alpha exclusive source union differs')
   need(fr['Root']==[256,464] and fr['alpha_root']['canvas']==[512,512],'Source root/canvas differs')
 return m,c,rows

def baseline(after_rows=None):
 cm=read(CM);need((cm['source_files'],cm['production_files'],cm['registered_tests'],cm['passed'],cm['failed'])==(303,1439,203,203,0),'CM baseline counts/GREEN differ')
 need(len(cm['files'])==1746 and cm['verification_passes']==2 and cm['twoSHA_mismatches']==0,'CM closed files differ')
 expected_source=set();expected_prod=set()
 for r in cm['files']:
  p=checked(r,ROOT)
  if r['path'].startswith('UnrealGame/Source/'):expected_source.add(p)
  if r['path'].startswith('UnrealGame/Content/Production/'):expected_prod.add(p)
 need(len(expected_source)==303 and len(expected_prod)==1439,'CM membership role counts differ')
 actual_source={p.resolve() for p in (ROOT/'UnrealGame/Source').rglob('*') if p.is_file()};need(actual_source==expected_source,'Source303 exact membership differs')
 if after_rows is not None:expected_prod|={saved_path(r).resolve() for r in after_rows}
 actual_prod={p.resolve() for p in (ROOT/'UnrealGame/Content/Production').rglob('*') if p.is_file()};need(actual_prod==expected_prod,'Production exact membership differs')
 return {'source_files':len(actual_source),'production_files':len(actual_prod),'old1439_SHA_unchanged':True,'all1746_baseline_pins_unchanged':True}
def content_snapshot():return [pin(p) for p in sorted((ROOT/'UnrealGame/Content').rglob('*')) if p.is_file()]
def check_content(before,rows=None):
 for r in before:checked(r)
 expected={Path(r['path']).resolve() for r in before}
 if rows is not None:expected|={saved_path(r).resolve() for r in rows}
 actual={p.resolve() for p in (ROOT/'UnrealGame/Content').rglob('*') if p.is_file()};need(actual==expected,'Global Content changed outside exact56 files')
 return len(actual)
def no_ue_processes():
 code="@(Get-Process -Name UnrealEditor,UnrealEditor-Cmd,UnrealBuildTool -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Id) | ConvertTo-Json -Compress"
 p=subprocess.run(['powershell','-NoProfile','-NonInteractive','-Command',code],capture_output=True,text=True,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0));need(p.returncode==0,'Cannot establish no-UE process gate');s=p.stdout.strip();ids=[] if not s else json.loads(s);ids=ids if isinstance(ids,list) else [ids];need(not ids,'No active UE/UBT process allowed before launch');return ids

def freeze_check(path,sha):
 path=Path(path).resolve();need(path==HERE/'candidate-freeze-v001.json' and pin(path)['sha256']==sha,'Pinned tool freeze required');d=read(path)
 actual={p.resolve() for p in HERE.rglob('*') if p.is_file() and p!=path};need(actual=={Path(r['path']).resolve() for r in d['members']},'Tool candidate exact membership differs')
 for r in d['members']+d['dependency_pins']:checked(r)
 return pin(path)
def old_actual_settings():
 r=read(OLD_RECEIPT);need(r['success'] is True and r['actual_count']==14 and r['saved_count']==14,'Actual old14 receipt not successful');s=r['assets'][0]['actual_settings'];need(all(x['actual_settings']==s for x in r['assets']) and s['srgb'] is True and s['never_stream'] is True,'Actual old14 settings differ');return s

def validate_exit(native_pid,launch,ex):
 need(ex['schema']=='Root-K56-native-import-exit-v001' and ex['os_exit_confirmed'] is True and type(ex['exit_code']) is int and ex['exit_code']==0,'Missing/nonzero OS exit is not success')
 need(type(native_pid) is int and native_pid==launch['process_id']==ex['process_id'],'Same native/launch/exit PID required')
 return True
