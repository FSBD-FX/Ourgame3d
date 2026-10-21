"""Read-only K0..7 actual native source/GPU/typed-slot/PNG audit.
No historical wrapper import, registration search, media mutation or UE launch.
"""
from pathlib import Path
import argparse, ast, hashlib, importlib.util, json, math, sys, zlib
import numpy as np
from PIL import Image
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
ROOT=Path('F:/Ourgame')
BASE=ROOT/'source-assets/production/fairytale-sword-secondary-v001'
CONTRACT=dict(path=(BASE/'K8-production-contract-builder-candidate-v001/output/source-contract-package-v001/source-contract-v001.json').as_posix(),bytes=156178,sha256='ef1d2418b7bae89da963fe6d3963c250fa84f89b7108581058dbf06d12be1d4b')
RESOURCES=dict(path=(BASE/'Root-native-resource-inputs-v001/K57-plus-Ready24-source-uasset-pins-v001.json').as_posix(),bytes=72590,sha256='b5f3d6689ed3cb43ded9f4bbbd25036352bf948270b123bae3c21e1521574961')
SAMPLER=dict(path=(ROOT/'source-assets/production/fairytale-hero-state-gap-v001/dodge-native-observer-candidate-v001/tooling/verify-Dodge-source-pixels-v001.py').as_posix(),bytes=5843,sha256='cee49fb96e9d6750a12c69babaeb9d1d2a87f4aaebd2048f7ff238b1db256727')
OBSERVER=dict(path=(BASE/'forward-step-observer-name-fix-candidate-v003/projected/UnrealGame/Source/CodexDungeon/DungeonSwdForwardStepProbeV002.cpp').as_posix(),bytes=47014,sha256='5f0d0a978a4defb61ec338bc4d77a31ae51f45a68bba1b284d143eecb60044a9')
DRIVER=dict(path=(BASE/'forward-step-native-observer-candidate-v002/drive-swd-forward-step-native-v002.py').as_posix(),bytes=9258,sha256='7b1cb6789658b9f6337ec5be0f61a3e43590952272570046202b61a0c2db7197')
OWNERS=['BodyRest','ShoulderFar','Chest','NearArmWithoutHand','ShoulderNear','HelmetForeground','IndependentSword','NearHand']

def need(ok,why):
 if not ok:raise ValueError(why)
def pin(row):
 need(isinstance(row,dict) and {'path','bytes','sha256'}<=row.keys(),'Missing immutable file pin')
 p=Path(row['path']);need(p.is_absolute() or ('..' not in p.parts and p.parts and not p.drive),'Relative pin must stay under Root');p=p if p.is_absolute() else ROOT/p
 b=p.read_bytes();need(type(row['bytes']) is int and len(b)==row['bytes'] and hashlib.sha256(b).hexdigest()==row['sha256'],'File pin differs: '+str(p));return p
def load_module(path,name):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m
P=load_module(HERE/'original-pure-functions-v001.py','K8_original_pure')
pixel=load_module(pin(SAMPLER),'K8_original_sampler')

def pure_provenance():
 proof=P.read(HERE/'original-pure-function-provenance-v001.json');new=(HERE/'original-pure-functions-v001.py').read_text(encoding='utf8');nn={n.name:n for n in ast.parse(new).body if isinstance(n,ast.FunctionDef)};nl=new.splitlines(keepends=True)
 for row in proof['functions']:
  src=pin(row['original']).read_text(encoding='utf-8-sig');nodes={n.name:n for n in ast.parse(src).body if isinstance(n,ast.FunctionDef)};node=nodes[row['function']];body=''.join(src.splitlines(keepends=True)[node.lineno-1:node.end_lineno]);n=nn[row['function']];copy=''.join(nl[n.lineno-1:n.end_lineno])
  need(body==copy and hashlib.sha256(body.encode()).hexdigest()==row['exact_definition_utf8_sha256'],'Original pure function changed')
 return len(proof['functions'])

def own_freeze(prereg):
 row=prereg['checker_dependencies']['K_pixel_composition_freeze'];f=pin(row);need(f.resolve()==(HERE/'candidate-freeze-v001.json').resolve(),'Wrong independent K pixel candidate freeze');d=P.read(f)
 need(d['schema']=='K8-native-pixel-checker-candidate-freeze-v001','Wrong K pixel checker freeze schema')
 files=d['files'];need(len({x['relative_path'] for x in files})==len(files),'Duplicate checker members')
 for member in files:
  p=P.file_under(HERE,member['relative_path']);pin(dict(member,path=p.as_posix()))
 actual={p.relative_to(HERE).as_posix() for p in HERE.rglob('*') if p.is_file() and p!=f};need(actual=={x['relative_path'] for x in files},'Exact checker candidate membership differs')
 for dep in d['dependencies']:pin(dep)
 script=prereg['checker_dependencies']['K_pixel_composition'];need(pin(script).resolve()==Path(__file__).resolve(),'Prereg K pixel script differs')
 return row

def source_inputs():
 pure_provenance();pin(OBSERVER);c=P.read(pin(CONTRACT));r=P.read(pin(RESOURCES));need(r['source_contract']==CONTRACT,'Resource table contract lineage differs')
 rows=r['resources'];need(len(rows)==81 and len({x['texture'] for x in rows})==81 and sum(x['group']=='K' for x in rows)==57 and sum(x['group']=='Ready' for x in rows)==24,'Actual K57/Ready24 distinct resources incomplete')
 need(len(c['layers'])==56 and c['texture_settings']['srgb'] is True,'Frozen source contract changed')
 bypath={x['texture']:x for x in rows};sources={}
 for l in c['layers']:
  p=bypath[l['object_path']];need(p['group']=='K' and p['frame']==l['frame'] and p['owner']==l['owner'] and p['source_png']==l['source']['path'] and p['bytes']==l['source']['bytes'] and p['sha256']==l['source']['sha256'] and p['rgba_sha256']==l['source_rgba_sha256'],'K resource does not exactly match frozen layer')
 sword=c['reused_sword'];p=bypath[sword['object_path']];need(p['component']==6 and p['source_png']==sword['source']['path'] and p['sha256']==sword['source']['sha256'] and p['rgba_sha256']==sword['source_rgba_sha256'],'Independent sword resource changed')
 for p in rows:
  f=pin(dict(path=p['source_png'],bytes=p['bytes'],sha256=p['sha256']));pin(p['uasset'])
  with Image.open(f) as im:
   need(im.format=='PNG' and im.mode=='RGBA' and im.size==(512,512),'Actual source must be PNG512 RGBA');rgba=np.asarray(im).copy()
  need(hashlib.sha256(rgba.tobytes()).hexdigest()==p['rgba_sha256'],'Full source RGBA pin differs')
  sources[p['texture']]=rgba
 return c,rows,sources

def frame_stack(contract,frame):
 layers={x['owner']:x['object_path'] for x in contract['layers'] if x['frame']==frame}
 return [contract['reused_sword']['object_path'] if owner=='IndependentSword' else layers[owner] for owner in OWNERS]
def pair(v):
 need(isinstance(v,(list,tuple)) and len(v)==2 and all(P.finite(x) for x in v),'Actual finite XY required');return list(v)
def point(v):return pair([v['x'],v['y']])
def close(a,b,tol=1e-4):return P.near(a,b,tol)
def samepair(a,b):return all(close(x,y) for x,y in zip(pair(a),pair(b)))
def expected_geometry(frame,face,ground,ui):
 need(face in (-1,1) and P.finite(ui) and ui>0,'Unsupported actual facing/UI scale');ground=pair(ground);root=pair(frame['Root']);grip=pair(frame['Grip']);axis=pair(frame['Axis']);need(root==[256.,464.],'Author root changed')
 width=72.*512./416.*ui;sw=width*.5;scale=width/512.;top=[ground[0]-256.*scale,ground[1]-464.*scale];gs=[ground[0]+face*(grip[0]-256.)*scale,ground[1]+(grip[1]-464.)*scale];pivot=[1.-99./512. if face<0 else 99./512.,.5]
 return dict(body_top=top,grip_screen=gs,sword_top=[gs[0]-pivot[0]*sw,gs[1]-pivot[1]*sw],sword_pivot=pivot,body_width=width,sword_width=sw,angle=math.degrees(math.atan2(axis[1],axis[0]))*(-1 if face<0 else 1),u=1. if face<0 else 0.,du=-1. if face<0 else 1.)

def typed_slots(o,r,contract,resources):
 d=o['secondary'];s=d['sample'];f=s['frame'];face=r['requested_facing'];need(type(f) is int and 0<=f<8 and s['facing']==face and s['decision']==2 and s['reason']==0,'Actual sampled K frame/facing required')
 need(all(d[k] is True for k in ('opt_in','owns_branch','profile_ready','atomic_preflight_ready','drawn')) and d['missing_reason']=='','Actual complete K8 draw required')
 need(d['profile_id']==contract['profile_id'] and d['source_contract_sha256']==CONTRACT['sha256'],'Actual draw source contract differs')
 b=d['binding'];need(d['player_entity_id']==r['owner'] and all(b[k]==r[k] for k in ('run','owner','weapon_instance','armor_instance','armor_version')) and b['weapon_version'] in (r['weapon_version'],r['weapon_version_end']) and b['armor']==1 and b['weapon_content']=='SWD-001' and b['armor_content']=='ARM-LGT-001','Actual player/weapon/light-armor binding differs')
 stack=frame_stack(contract,f);slots=d['slots'];common=o['common_draw'];need(d['expected_draw_count']==8 and len(slots)==8 and d['actual_stack']==stack and common['actual_stack']==stack and common['draw_id']==d['draw_id'] and common['clip']=='sword_secondary' and common['frame']==f and common['facing']==face and common['supported'] is True and common['gear_placeholder'] is False,'Typed/common actual eight-slot draw differs')
 residents=d['residents'];need(len(residents)==57 and len({x['texture'] for x in residents})==57 and {x['texture'] for x in residents}=={p['texture'] for p in resources if p['group']=='K'},'Actual 57 UE residents differ')
 need(all(x['ready'] is True and x['pending_initialization'] is False and x['class']=='Texture2D' and x['width']==x['height']==512 for x in residents),'Actual resource readiness incomplete')
 g=d['geometry'];need(close(g['ui_scale'],1.,1e-6),'Actual1280x720 baseline requires original UI scale1');expected=expected_geometry(contract['frames'][f],face,point(g['ground_screen']),g['ui_scale'])
 for k,v in expected.items():need(samepair(point(g[k]),v) if isinstance(v,list) else close(g[k],v),'Actual marker geometry differs: '+k)
 for i,q in enumerate(slots):
  need(type(q['slot']) is int and q['slot']==i and type(q['component']) is int and q['component']==i and q['texture']==stack[i] and all(q[k] is True for k in ('selected','texture_ready','drawn')),'Actual K slot/depth/source differs')
  sword=i==6;top=expected['sword_top'] if sword else expected['body_top'];width=expected['sword_width'] if sword else expected['body_width']
  need(samepair(q['top'],top) and samepair(q['size'],[width,width]) and samepair(q['uv'],[expected['u'],0.]) and samepair(q['uv_size'],[expected['du'],1.]),'Actual submitted float quad or single facing UV differs')
  need(close(q['rotation'],expected['angle'] if sword else 0.) and samepair(q['rotation_pivot'],expected['sword_pivot'] if sword else [0.,0.]),'Actual submitted rotation/pivot differs')
  need(q['draw_scale']==1. and q['scale_position'] is False and q['tint']==[1.,1.,1.,1.],'Unmeasured scale-position/tint blend unsupported; preserve native failure')
 return slots

def resource_metadata(x,p,readback_stop):
 need(x['texture']==p['texture'] and x['frame']==p['frame'] and x['component']==p['component'] and x['source_SHA_metadata']==p['sha256'] and x['source_RGBA_SHA_metadata']==p['rgba_sha256'],'Actual readback source identity differs')
 need(x['resource_ready'] is True and x['pending_initialization'] is False and x['class']=='Texture2D' and x['width']==x['height']==512 and x['sRGB'] is True and x['RHI_format'] in (2,37) and x['editor_source_format']=='TSF_BGRA8','Actual uncompressed sRGB Texture2D512 readback required')
 need(x['read_flags']=='RCM_UNorm/Mip0/LinearToGamma=false; BGRA8/RGBA8 UNORM(_SRGB) byte copy','Unsupported actual readback flags')
 need(all(P.finite(x[k]) for k in ('read_start_monotonic_s','read_stop_monotonic_s')) and 0<x['read_start_monotonic_s']<=x['read_stop_monotonic_s']<=readback_stop,'Actual startup readback clocks differ')
def full_readback_bytes(data,expected,crc):
 need(len(data)==1048576 and data==expected and type(crc) is int and zlib.crc32(data)&0xffffffff==crc,'Actual original GPU/editor bytes or CRC differ from full source')
def resource_readbacks(original,r,prereg,rows,sources):
 need(prereg['resource_pins']==rows,'Preregistered resources differ from actual import-backed 81 table')
 seen=r['startup_resource_readbacks'];stop=r['startup_readback_stop_monotonic_s'];start=r['capture_timing']['capture_start_monotonic_s'];need(r['startup_readback_complete'] is True and P.finite(stop) and 0<stop<start and len(seen)==81 and len({x['texture'] for x in seen})==81,'Actual startup readback must finish before capture')
 need([x['texture'] for x in seen]==[p['texture'] for p in rows],'Exact preregistered readback ordering differs');files=[]
 for x,p in zip(seen,rows):
  resource_metadata(x,p,stop)
  expected=sources[p['texture']][...,[2,1,0,3]].tobytes()
  for field,crc in [('GPU_file','GPU_BGRA8_CRC32'),('editor_source_file','editor_source_BGRA8_CRC32')]:
   f=P.file_under(original,x[field]);data=f.read_bytes();full_readback_bytes(data,expected,x[crc]);files.append(f.resolve())
 need(len(set(files))==162 and set(files)=={p.resolve() for p in (original/'texture-readback').rglob('*') if p.is_file()},'Exact 162 startup readback originals required')
 return dict(actual_source_GPU_editor_resources=81,original_binary_files=162,all_source_RGBA_exact=True,srgb=True)

def runtime_binding(archive,prereg,r):
 need(prereg['schema']=='swd-forward-step-native-readiness-v002' and prereg['ready'] is True and all(prereg[k] is True for k in ('K_profile_runtime_ready','observer_editor_compile_verified','observer_fresh_review_approved','placement_witness_source_ready')),'Root admitted compiled prereg required')
 need(r['schema']=='swd-forward-step-native-observer-v002' and r['passed'] is True and r['flow_complete'] is True and r['failure']=='' and r['formal_accepted'] is False and r['checker_accepted'] is False,'Actual completed native observer required')
 need(r['player_enemy_HP_position_AI_clock_writes'] is False and r['enemy_diagnostic_used'] is False and r['route_mode']==prereg['route_mode'],'Forced gameplay or route-mode mismatch')
 launch=P.read(archive/'launch-argv.json');started=P.read(archive/'process-started.json');exited=P.read(archive/'process-exit.json');need(exited['exit_code']==0 and exited['native_run_attempted'] is True and started['native_run_attempted'] is True and started['process_id']==r['process_id'],'Actual successful original process required')
 paths=[a.split('=',1)[1] for a in launch['argv'] if a.startswith('-DungeonSwdForwardStepPrereg=')];need(len(paths)==1,'Exact launch prereg path missing');actual=Path(paths[0]);need(P.read(actual)==prereg,'Passed prereg differs from actual launched bytes');sha=hashlib.sha256(actual.read_bytes()).hexdigest();need(sha==launch['prereg_sha256']==started['prereg_sha256'],'Actual native launch/prereg pin differs')
 # Use the frozen real launcher argv builder, never duplicate/reinvent UE flags.
 driver=load_module(pin(DRIVER),'K8_native_argv');expected=driver.launch_args(prereg,pin(prereg['editor_executable']),pin(prereg['uproject']),archive/'原件',r['case'],actual)
 need([a.replace('\\','/') for a in launch['argv']]==[a.replace('\\','/') for a in expected],'Unexpected UE argument or evidence directory');pin(prereg['game_dll']);pin(prereg['review_report'])
 cm=P.read(pin(prereg['compiled_manifest']));suite=P.read(pin(cm['full_suite']));need(cm['failed']==0 and cm['passed']==cm['registered_tests'] and suite['succeeded']==cm['passed'] and all(suite[k]==0 for k in ('failed','notRun','inProcess','succeededWithWarnings')),'Actual complete native regression suite not GREEN')
 members=cm['files'];need(len({x['path'] for x in members})==len(members),'Compiled manifest path aliases');[pin(x) for x in members];pin(cm['source_admission_pin'])
 for folder in ('UnrealGame/Source','UnrealGame/Content/Production'):
  recorded={x['path'].replace('\\','/') for x in members if x['path'].replace('\\','/').startswith(folder+'/')};actualmembers={p.relative_to(ROOT).as_posix() for p in (ROOT/folder).rglob('*') if p.is_file()};need(recorded==actualmembers,'Compiled manifest actual file membership differs: '+folder)
 observer=[x for x in members if x['path'].replace('\\','/')=='UnrealGame/Source/CodexDungeon/DungeonSwdForwardStepProbeV002.cpp'];need(len(observer)==1 and observer[0]['sha256']==OBSERVER['sha256'],'Compiled actual observer serializer differs')
 return dict(prereg=dict(path=actual.as_posix(),bytes=actual.stat().st_size,sha256=sha),compiled_manifest=prereg['compiled_manifest'],native_process=r['process_id'],original_OS_exit=0)

def projection(slots,sources):
 corners=[P.project(q,uv) for q in slots for uv in ((0,0),(512,0),(0,512),(512,512))];xs,ys=zip(*corners);x0=max(0,math.floor(min(xs))-1);x1=min(1280,math.ceil(max(xs))+1);y0=max(0,math.floor(min(ys))-1);y1=min(720,math.ceil(max(ys))+1);need(x0<x1 and y0<y1,'Actual submitted quad outside native viewport')
 yy,xx=np.mgrid[y0:y1,x0:x1];color=np.zeros((*xx.shape,3));alpha=np.zeros(xx.shape);visible=[]
 for q in slots:
  src=sources[q['texture']].astype(np.float64)/255.;src[...,:3]=pixel.linear(src[...,:3]);rgba=pixel.sample(src,q,xx,yy);a=rgba[...,3];color=rgba[...,:3]*a[...,None]+color*(1.-a[...,None]);alpha=a+alpha*(1.-a);visible=[v*(1.-a) for v in visible]+[a]
 expected=np.rint(pixel.srgb(color)*255).astype(np.uint8)
 return [x0,y0,x1,y1],expected,alpha,visible
def optical_one(original,movie,index,o,slots,sources):
 roi,expected,alpha,visible=projection(slots,sources);x0,y0,x1,y1=roi
 with Image.open(P.file_under(original,movie[index]['file'])) as im:actual=np.asarray(im.convert('RGB'))[y0:y1,x0:x1]
 error=np.mean(np.abs(actual.astype(float)-expected.astype(float)),axis=-1);opaque=(alpha>=.999)&(np.max(expected,axis=-1)>=32);blade=(visible[6]>=.98)&(np.min(expected,axis=-1)>=45)
 bc,sc,bm,bg,sm,sg=P.fixed_optical_gate(error,opaque,blade)
 components=component_evidence(error,opaque,visible)
 return dict(frame=o['secondary']['sample']['frame'],callback_index=index,native_draw_id=o['secondary']['draw_id'],original_PNG=movie[index]['file'],original_PNG_native_BGRA8_CRC32=movie[index]['native_BGRA8_crc32'],submitted_quad_ROI=roi,body_opaque_pixels=bc,body_median_RGB_error=bm,body_fraction_RGB_error_le55=bg,exposed_blade_pixels=sc,blade_median_RGB_error=sm,blade_fraction_RGB_error_le65=sg,component_visible_ROIs=components)
def component_evidence(error,opaque,visible):
 components=[]
 # Reuse original body error limits (40/.60 at error55) on sufficiently visible
 # owner interiors. Eight is the original blade witness minimum. Small/occluded
 # owners stay explicitly low-evidence, never magically count as independent proof.
 for i,v in enumerate(visible):
  roi=(v>=.98)&opaque;n=int(np.count_nonzero(roi));median=float(np.median(error[roi])) if n else None;fraction=float(np.mean(error[roi]<=55)) if n else None
  if i!=6 and n>=8:need(median<=40 and fraction>=.60,'Actual independently visible '+OWNERS[i]+' ROI fails original body error limits; preserve native failure')
  components.append(dict(slot=i,owner=OWNERS[i],visible_interior_pixels=n,median_RGB_error=median,fraction_RGB_error_le55=fraction,ROI_error_gate_applied=i!=6 and n>=8,low_evidence_less_than8_pixels=n<8,independent_owner_attribution='composite ROI only; identical/occluded source pixels do not identify a unique owner'))
 return components

def audit(archive,prereg):
 archive=Path(archive).resolve();original=archive/'原件';freeze=own_freeze(prereg);r=P.read(original/'runtime-report.json');contract,rows,sources=source_inputs();binding=runtime_binding(archive,prereg,r);resources=resource_readbacks(original,r,prereg,rows,sources)
 offsets=r['capture_timing']['frame_wall_offsets_s'];obs=r['observations'];need(r['capture_timing']['use_fixed_time_step'] is False and len(offsets)==len(obs)>1 and [o['callback_index'] for o in obs]==list(range(len(obs))) and all(P.finite(v) and v>=0 for v in offsets) and all(x<y for x,y in zip(offsets,offsets[1:])) and all(close(o['wall_offset_s'],offsets[i],1e-6) for i,o in enumerate(obs)),'Actual callback/PNG real wall FIFO differs')
 movie=P.verify_png_fifo(original,r);active=[(i,o) for i,o in enumerate(obs) if o['secondary']['owns_branch']];need(active,'No actual typed K branch')
 byframe={f:[] for f in range(8)}
 a=r['accepted_action'];need(a['type']==2 and a['weapon']==0 and a['instance_id']==r['weapon_instance'] and a['facing']==r['requested_facing'] and a['started_airborne'] is False,'Actual SWD grounded Skill identity required')
 bounds=[a['start'],a['lock_at'],a['start']+.14,a['active_at'],a['start']+.25,a['active_end'],a['start']+.42,a['start']+.55,a['end']]
 for i,o in active:
  s=o['secondary']['sample'];f=s['frame'];action=s['action'];need(type(f) is int and 0<=f<8 and len(s['boundaries'])==9 and all(close(x,y,1e-6) for x,y in zip(s['boundaries'],bounds)) and bounds[f]<=o['sim']<bounds[f+1],'Actual K deadlines/callback frame differ')
  need(all(action[k]==a[k] for k in ('action_id','instance_id','start','lock_at','active_at','active_end','end')) and close(action['sample_time'],o['sim'],1e-6) and o['action']['active'] is True and o['action']['action_id']==a['action_id'] and o['height']==o['vertical_velocity']==0 and o['weapon_grounded'] is o['melee_grounded'] is True,'Typed K source action/time/grounded callback differs')
  byframe[f].append((i,o,typed_slots(o,r,contract,rows)))
 ids=[o['secondary']['draw_id'] for i,o in active];need(all(isinstance(v,str) and v.isascii() and v.isdecimal() and str(int(v))==v and 0<int(v)<2**64 for v in ids) and all(int(x)<int(y) for x,y in zip(ids,ids[1:])),'Actual typed native draw identities repeat or regress')
 need(all(byframe.values()) and r['secondary_frame_mask']==255,'All eight actual typed frames required')
 results=[]
 for frame,choices in byframe.items():
  i,o,slots=choices[len(choices)//2];results.append(optical_one(original,movie,i,o,slots,sources))
 return dict(schema='K8-independent-actual-native-pixel-audit-v001',passed=True,actual_native_pixel_composition_verified=True,scope='K0..7 fixed-registration composite source-pixel witnesses + actual typed eight-slot geometry + full K57/Ready24 source/GPU closure',checker_freeze=freeze,binding=binding,resources=resources,all_K_typed_callbacks_checked=len(active),original_PNG_FIFO_count=len(movie),K8_native_pixel_witnesses=results,registration_search_used=False,actual_pixels_modified=False,original_fixed_optical_gate_unchanged=True,Ready_optical_composition_verified=False,Ready_optical_status='OPEN: common_draw only; no actual typed Ready quads in this serializer',individual_owner_unique_pixel_attribution=False,UI_hidden_independently_verified=False,placement_causal_verified_by_this_helper=False,main_mix_verified_by_this_helper=False,listened=False,device_onset_measured=False,art_accepted=False,formal_accepted=False,FinalAccepted=False)

if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--archive',type=Path);ap.add_argument('--prereg',type=Path);ap.add_argument('--source-preflight',action='store_true');ns=ap.parse_args()
 try:
  if ns.source_preflight:
   c,rows,sources=source_inputs();out=dict(status='SourceInputsVerified',actual_source_uasset_resources=len(rows),source_contract=CONTRACT,resource_table=RESOURCES,original_functions_unchanged=pure_provenance(),native_run_attempted=False,actual_native_pixel_composition_verified=False,FinalAccepted=False)
  else:need(ns.archive is not None and ns.prereg is not None,'Archive and original prereg required');out=audit(ns.archive,P.read(ns.prereg))
  code=0
 except (ValueError,KeyError,TypeError,OSError,AssertionError,IndexError) as e:out=dict(status='NeedsFixes',passed=False,reason=str(e),actual_native_pixel_composition_verified=False,FinalAccepted=False);code=3
 print(json.dumps(out,ensure_ascii=False,indent=2));sys.exit(code)
