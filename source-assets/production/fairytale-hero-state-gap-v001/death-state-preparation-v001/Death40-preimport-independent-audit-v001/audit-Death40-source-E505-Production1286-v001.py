"""Independent read-only Death40 source/namespace/E505 + current1286 baseline audit.
Writes audit JSON/text only in this new directory; never invokes UE/import/generation.
"""
from pathlib import Path
from datetime import datetime,timezone
from collections import Counter
import hashlib,json,sys
from PIL import Image
import numpy as np
ROOT=Path('F:/Ourgame');OUT=Path(__file__).resolve().parent
assert Path(sys.executable).resolve()==(ROOT/'tools/runtime/asset-gen/Scripts/python.exe').resolve()
BASE=ROOT/'source-assets/production/fairytale-hero-state-gap-v001/death-state-preparation-v001'
CAND=BASE/'Death40-native-ready-author-candidate-v002'
MAN=CAND/'Death40-source-manifest-author-candidate-v002.json'
FREEZE=CAND/'native-ready-author-freeze-v002.json'
E505=next(Path('E:/OurGame/Knight/过程图稿与视频').glob('*v505/source-size-SHA256.json'))
COMPILED=ROOT/'source-assets/production/backups/v137-range187G/compiled-source-manifest.json'
HURTREC=ROOT/'UnrealGame/Saved/Bootstrap/hurt32-v002-import-20261018-080500-460471.json'
GUARDMAN=ROOT/'source-assets/production/fairytale-guard-v001/root-full-registration-v001/import-manifest.json'
GUARDREC=ROOT/'UnrealGame/Saved/Bootstrap/guard-full28-v001-import-20261018-045754-597733.json'
NS='/Game/Production/ArtTrials/EV048/v019/HeroLeatherDeath'
CONTENT=ROOT/'UnrealGame/Content/Production';TARGET=ROOT/'UnrealGame/Content/Production/ArtTrials/EV048/v019/HeroLeatherDeath'
START=datetime.now(timezone.utc).isoformat();errors=[];notes=[]
def pin(p):
 p=Path(p);b=p.read_bytes();return {'path':p.as_posix(),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def need(v,msg):
 if not v:errors.append(msg)
 return bool(v)
def write(rel,v):
 p=OUT/rel;assert not p.exists()
 with p.open('x',encoding='utf-8',newline='\n') as f:f.write(v if isinstance(v,str) else json.dumps(v,ensure_ascii=False,indent=2)+'\n')
 return p
def bbox(a):
 y,x=np.where(a);return None if not len(x) else [int(x.min()),int(y.min()),int(x.max()+1),int(y.max()+1)]
need(pin(MAN)['sha256']=='0889b31d32a7485c482f565d857526eac422bee8dfd086166df43f862c159df8','Manifest frozen SHA differs')
need(pin(FREEZE)['sha256']=='5f6506b609440d8cfda40b493b7ce9b23131b0f83aa09add333f8d8e74ef788c','Native-ready freeze SHA differs')
m=read(MAN);fr=read(FREEZE);ei=read(E505);cm=read(COMPILED)
need(ei['verification_passes']==2 and ei['source_and_target_hash_mismatches']==0,'E505 retention is not2passes0diff')
need(m['namespace']==NS and m['asset_count']==40 and len(m['assets'])==40 and m['body25_count']==25 and m['armor15_count']==15,'Expected Death40 namespace/counts differ')
need(m['replace_existing'] is False and m['Root_actual_import_receipt'] is None and m['TrialAllowed'] is False and m['FinalAccepted'] is False,'Candidate must remain no-overwrite/unimported/unaccepted')
need(pin(m['sourcefit_freeze']['path'])==m['sourcefit_freeze'],'Pinned sourcefit freeze changed')
for p in fr['files']:need(pin(p['path'])==p,'Frozen metadata changed: '+p['path'])
owners=['BodyRest','NearArmWithoutHand','HelmetForeground','FarHandForeground','NearHand'];armor=['Chest','ShoulderNear','ShoulderFar'];names=owners+armor
expected={(i,n) for i in range(5) for n in names};actual={(r['frame'],r['component']) for r in m['assets']}
need(actual==expected,'Exact5x8 component-frame set differs')
need(len({r['name'] for r in m['assets']})==40 and len({r['object_path'] for r in m['assets']})==40 and len({r['package_path'] for r in m['assets']})==40,'Duplicate target names/objects/packages')
need(len({r['source'] for r in m['assets']})==40,'Duplicate source path')
sfset={(p['path'],p['bytes'],p['sha256']) for p in fr['source40']}
need(sfset=={(r['source'],r['source_bytes'],r['source_sha256']) for r in m['assets']},'Frozen40 source set differs from manifest')
rows=[]
for r in m['assets']:
 p=Path(r['source']);v=pin(p);actual_pin={'path':p.as_posix(),'bytes':r['source_bytes'],'sha256':r['source_sha256']};ok=need(v==actual_pin,'SourcePNG pin differs: '+p.as_posix())
 need(p.is_relative_to(BASE/'LGT237-239-Death5-sleeve-control-sourcefit-v003'),'Source escaped unified reviewed assembly: '+p.as_posix())
 need(p.name==f"frame-{r['frame']}.png" and p.parent.name==r['component'],'Source filename/component differs: '+p.as_posix())
 name=f"T_Fairytale_Death_{r['component']}_{r['frame']:03d}_v001";package=NS+'/'+name;obj=package+'.'+name
 need(r['name']==name and r['package_path']==package and r['object_path']==obj,'Target namespace/name construction differs: '+r['name'])
 saved=ROOT/'UnrealGame/Content'/Path(package[6:]+'.uasset');need(saved.is_relative_to(TARGET),'Target escapedv019 namespace')
 need(not saved.exists(),'Target package already exists: '+saved.as_posix())
 with Image.open(p) as im:
  need(im.mode=='RGBA' and im.size==(512,512),'Actual source not512RGBA: '+p.as_posix());a=np.array(im.convert('RGBA'))
  sha=hashlib.sha256(a.tobytes()).hexdigest();used=int(np.count_nonzero(a[:,:,3]));core=int(np.count_nonzero(a[:,:,3]>=128));box=bbox(a[:,:,3]>0)
  need(sha==r['source_RGBA_sha256'] and used==r['source_alpha_nonzero_pixels'] and core==r['source_alpha128_pixels'] and box==r['source_alpha_bbox'],'DecodedRGBA/alpha metadata differs: '+p.as_posix())
  need(r['source_mode']=='RGBA' and r['source_canvas']==[512,512] and r['expected_object_class']=='Texture2D','Declared source or class differs: '+p.as_posix())
  need(used>0 and core>0 and r['known_optional_empty'] is False and r['empty_reason'] is None,'Empty/optional layer illegal forDeath40: '+p.as_posix())
 e=r['actual_E_retained_member'];need(e['manifest']==pin(E505),'Per-source E505 index pin differs: '+p.as_posix());ep=E505.parent/e['retained_relative']
 need(pin(ep)==e['file'] and e['file']['bytes']==v['bytes'] and e['file']['sha256']==v['sha256'],'Per-source retained file differs: '+p.as_posix())
 hits=[t for t in ei['files'] if t['retained_relative']==e['retained_relative'] and t['sha256']==v['sha256'] and t['bytes']==v['bytes']]
 need(len(hits)==1,'Exact retained_relative record not unique inE505: '+p.as_posix())
 for repeat in range(2):need(p.read_bytes()==ep.read_bytes() and pin(p)['sha256']==pin(ep)['sha256'],'Current F/E505 bytes not equal twice: '+p.as_posix())
 rows.append({'component':r['component'],'frame':r['frame'],'source':v,'RGBA_sha256':sha,'nonzero_alpha':used,'core128':core,'alpha255':int(np.count_nonzero(a[:,:,3]==255)),'bbox':box,'E505_retained_relative':e['retained_relative'],'E505_twoSHA_byte_exact':True,'expected_package_path':package,'expected_object_path':obj,'predicted_saved_file':saved.as_posix(),'source_and_target_metadata_ok':ok})
need(not TARGET.exists() or not any(TARGET.rglob('*')),'v019 target namespace not absent/empty')
baseline=[r for r in cm['files'] if r['path'].startswith('UnrealGame/Content/Production/')]
need(cm['production_files']==1286 and len(baseline)==1286,'Compiledv137 baseline is not1286')
need(cm['source_verification_passes']==2 and cm['source_hash_mismatches']==0,'Compiled baseline prior verification invalid')
base_map={r['path']:{'bytes':r['bytes'],'sha256':r['sha256']} for r in baseline};need(len(base_map)==1286,'Duplicate compiledProductionpath')
# Independently derive the same1286 set from preserved1226+Guard28+Hurt32 native lineage.
gm=read(GUARDMAN);gr=read(GUARDREC);hr=read(HURTREC)
need(gr['success'] and hr['success'] and len(gr['assets'])==28 and len(hr['assets'])==32,'Native import lineage invalid')
lineage={r['path']:{'bytes':r['bytes'],'sha256':r['sha256']} for r in gm['old_production_files']}
need(len(lineage)==1226,'Old1226 lineage differs')
for receipt in [gr,hr]:
 for r in receipt['assets']:
  s=r['saved'];rel=Path(s['path']).relative_to(ROOT).as_posix();need(rel not in lineage,'Duplicate native-saved lineagepackage');lineage[rel]={'bytes':s['bytes'],'sha256':s['sha256']}
need(lineage==base_map,'Old1226+actualGuard28+actualHurt32 differs from compiledv137 Production1286')
passes=[]
for repeat in range(2):
 current={p.relative_to(ROOT).as_posix():p for p in CONTENT.rglob('*') if p.is_file()};missing=sorted(set(base_map)-set(current));extra=sorted(set(current)-set(base_map));bad=[];measured={}
 for rel,p in sorted(current.items()):
  v=pin(p);measured[rel]={'bytes':v['bytes'],'sha256':v['sha256']}
  if rel in base_map and measured[rel]!=base_map[rel]:bad.append({'path':rel,'expected':base_map[rel],'actual':measured[rel]})
 digest=hashlib.sha256(json.dumps(measured,sort_keys=True,separators=(',',':')).encode()).hexdigest()
 passes.append({'pass':repeat+1,'measured_at_utc':datetime.now(timezone.utc).isoformat(),'current_file_count':len(current),'missing':missing,'extra':extra,'changed':bad,'inventory_digest':digest,'bytes':sum(x['bytes'] for x in measured.values())});need(not missing and not extra and not bad,f'CurrentProduction1286 mismatch pass{repeat+1}')
need(passes[0]['inventory_digest']==passes[1]['inventory_digest'],'Production inventory changed during independent2pass audit')
props={'size_x':512,'size_y':512,'lod_group':'TEXTUREGROUP_UI','compression':'TC_EDITOR_ICON','mip_gen':'TMGS_NoMipmaps','never_stream':True,'sRGB':True}
need(m['texture_properties']==props,'Author textureproperties unexpectedly changed')
adapter={'schema':'Death40-author-to-scoped-import-field-map-audit-v001','author_manifest':pin(MAN),'source_count':40,'direct_Hurt32_importer_compatible':False,'reason':'Hurt importer hardcodes32/v017/4frames/3knownempty and expects texture_settings/canvas_px/source_closure_digest. Death author manifest intentionally uses texture_properties and5frames, so Root must construct a new scoped40 config/adapter. Do not run unchanged Hurt importer or overwrite original author manifest.','explicit_mapping':{'namespace':'copy exact /Game/Production/ArtTrials/EV048/v019/HeroLeatherDeath','asset_count':40,'assets':'Copy exact40 retained rows without changing source SHA/RGBA/path/name/package/object/class. Source_filename can be Path(source).name; verify actual Unreal import filenames equal resolvedsource.','canvas_px':[512,512],'texture_settings':{'compression_settings':'TC_EDITOR_ICON','mip_gen_settings':'TMGS_NO_MIPMAPS','lod_group':'TEXTUREGROUP_UI','never_stream':True,'srgb':True},'filter':'TF_BILINEAR if following proven Guard/Hurt native UI policy; absent from author manifest so Root must explicitly set+verify rather than claim field exists.','replace_existing':False,'expected_optional_empty_assets':0,'expected_before_Production':1286,'expected_added_unique_packages':40,'expected_after_Production_if_only_this_import':1326,'old_baseline':'Exactly pinned1286 existingfiles unchanged twice, no arbitraryextras.'},'source_fields_author':'source,source_bytes,source_sha256,source_RGBA_sha256,source_mode,source_canvas,source_alpha_nonzero_pixels,source_alpha128_pixels,source_alpha_bbox,known_optional_empty,empty_reason,name,package_path,object_path,expected_object_class,actual_E_retained_member','author_receipt_status':{'Root_actual_import_receipt':None,'TrialAllowed':False,'FinalAccepted':False},'native_validation_pending':['Texture2D actualclass,size512×512','Actual import filename=exactresolvedsource','Actual UI typedsettings inclfilter','Eachnew saved.uasset size/SHA twice','Exact1286 old+40 new union1326, onlynamespace targets','GPU FinishCompilation/Flush/residency separate from import receipt'],'Root_owns_execution':True,'actual_import_performed_by_audit':False}
ap=write('Death40-import-field-adapter-spec-v001.json',adapter)
report={'schema':'Death40-preimport-independent-audit-v001','started_at_utc':START,'finished_at_utc':datetime.now(timezone.utc).isoformat(),'success':not errors,'errors':errors,'scope':'Read-only author40 PNG/E505/name/namespace/Production1286 audit, noView/noUE/native/import or actualedits','inputs':{'manifest':pin(MAN),'native_ready_freeze':pin(FREEZE),'sourcefit_freeze':m['sourcefit_freeze'],'E505':pin(E505),'compiledv137':pin(COMPILED),'old1226manifest':pin(GUARDMAN),'actualGuard28receipt':pin(GUARDREC),'actualHurt32receipt':pin(HURTREC)},'counts':{'sources':len(rows),'body25':sum(r['component'] in owners for r in rows),'armor15':sum(r['component'] in armor for r in rows),'unique_names':len({r['name'] for r in m['assets']}),'nonempty40':all(r['nonzero_alpha']>0 and r['core128']>0 for r in rows),'E505_exact40':len(rows)==40},'namespace':NS,'namespace_physically_absent_at_audit':not TARGET.exists(),'source_rows':rows,'baseline_production1286':{'lineage_matches_compiledv137':lineage==base_map,'twoSHA_passes':passes,'unchanged':all(not p['missing'] and not p['extra'] and not p['changed'] and p['current_file_count']==1286 for p in passes)},'import_field_adapter_spec':pin(ap),'findings':[{'severity':'REQUIRED_ADAPTER_NOT_SOURCE_BLOCK','fact':'Author field schema differs from import executable. New Root adapter must map texture_properties keys and TMGS_NoMipmaps text to actualenum TMGS_NO_MIPMAPS and exact5×8/noempty40, preserving all sources and nooverwrite.'}],'newDodge_media_Viewed':False,'any_new_media_generated':False,'actual_import_receipt':None,'actual_GPU_finish_receipt':None,'native_runtime_verified':False,'FinalAccepted':False}
rp=write('Death40-preimport-independent-audit-report-v001.json',report)
write('HANDOFF.md',('PASS' if not errors else 'FAIL')+'：独立只读核40 PNG源及decodedRGBA/alpha元数据、五相八组件命名/v019包路径、无空层、E505每项current两遍byte/SHA、原freeze40源集；Production1286两遍当前SHA与compiledv137和1226+Guard28+Hurt32lineage同时一致。\n\n导入构造须注意author manifest不是Hurt importer直接输入：texture_properties→texture_settings；compression→compression_settings，mip_gen TMGS_NoMipmaps→mip_gen_settings TMGS_NO_MIPMAPS，sRGB→srgb，补显式canvas_px512²。Hurt脚本硬编码v017/32/4/3empty不能直接重用执行。新Death须exactv019/40/5/0empty，old1286不变+40=1326仅为本次唯一新增条件，Root导入前freshset/nooverwrite还需核。filter未在author字段，沿provenTF_BILINEAR需Root显式set/verify。原source/metadata不改，GPUfinish/native/Final均未验证。\n')
freeze=write('independent-audit-freeze-v001.json',{'schema':'Death40-preimport-independent-audit-freeze-v001','script':pin(Path(__file__)),'files':[pin(p) for p in sorted(OUT.glob('*')) if p.is_file() and p.name!=Path(__file__).name],'source_inputs_readonly':True,'any_Content_Source_tools_ledger_write':False,'UE_started':False,'imagegen_calls':0})
print(json.dumps({'success':not errors,'errors':errors,'report':pin(rp),'adapter':pin(ap),'freeze':pin(freeze),'sources40':len(rows),'empty_layers':sum(r['nonzero_alpha']==0 for r in rows),'Production_counts':[p['current_file_count'] for p in passes],'Production1286_unchanged':report['baseline_production1286']['unchanged'],'v019_absent':not TARGET.exists()},ensure_ascii=False,indent=2))
