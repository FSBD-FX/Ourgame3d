"""Root-executed Stomp review media. Readonly native archives; NEW external output only."""
from pathlib import Path
import argparse, hashlib, json, math, runpy, shutil, subprocess, sys
from PIL import Image, ImageDraw

R=Path('F:/Ourgame').resolve()
C=Path(__file__).resolve().parent.parent
CLIPS=[('StompWindup',6),('StompActive',2),('StompRecovery',4)]
JOIN_NAMES=['Ready-to-StompWU0','StompWU5-to-Active0','StompActive1-to-Recovery0','StompRecovery3-to-actual-Ready']

def need(value,why):
 if not value:raise ValueError(why)

def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))

def resolve(p):
 p=Path(p);return(p if p.is_absolute()else R/p).resolve()

def pin(p):
 p=resolve(p);h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return dict(path=p.as_posix(),bytes=p.stat().st_size,sha256=h.hexdigest())

def checked(x,base=R):
 need(isinstance(x,dict)and set(x)=={'path','bytes','sha256'},'Exact actual pin required')
 p=Path(x['path']);p=(p if p.is_absolute()else base/p).resolve();a=pin(p);need(a['bytes']==x['bytes']and a['sha256']==x['sha256'],'Pinned input changed: '+str(p));return p

def same_pin(a,b):return pin(checked(a))==pin(checked(b))

def dump_new(p,v):
 with Path(p).open('x',encoding='utf-8')as f:json.dump(v,f,ensure_ascii=False,indent=2);f.write('\n')

def dependencies():
 for x in read(C/'Stomp-native-media-freeze-v001.json')['files']:checked(x,C)
 contract=read(C/'media-input-contract-v001.json')
 for key in ['official_checker','official_observer_freeze','VFR_reference_helper','VFR_reference_freeze']:checked(contract[key])
 for x in read(checked(contract['official_observer_freeze']))['files']:checked(x,checked(contract['official_observer_freeze']).parent)
 return contract

def guard_draw(o,entity):
 found=[d for d in o.get('guard_draws',[])if d['EntityId']==entity]
 need(len(found)==1,'Expected one actual Guard draw for this original callback');return found[0]

def actual_inputs(archive,snapshot,prereg,profile,side,contract):
 original=archive/'原件';report_path=original/'runtime-report.json';proof_path=original/contract['independent_receipt']
 r,v,session=read(report_path),read(proof_path),read(archive/'index.json')
 need(r['schema']==contract['native_report_schema']and r['scenario']=='FirstNaturalStompAid2Cycle'and r['passed']is True and r['flow_complete']is True,'Actual terminal native Stomp PASS required')
 need(v['schema']==contract['independent_schema']and v['passed']is True and v['cycle_attack_id']==r['cycle_attack_id']=='2','Actual independent same first Aid2 PASS required')
 need(session['schema']==contract['native_session_schema']and session['exit_code']==0 and session['native_reported_passed']is True and session['independent_passed']is True and str(session['process_id'])==str(r['process_id'])==str(v['process_id']),'Actual terminal native/session/independent PID/exit PASS required')
 need(session['requested_approach_side']==r['requested_approach_side']==r['actual_approach_side']==side,'Archive belongs to another actual requested side')
 p=read(prereg);need(p['approach_side']==side and same_pin(p['profile_contract_pin'],pin(profile))and same_pin(p['compiled_manifest_pin'],pin(snapshot/'compiled-source-manifest.json')),'Actual prereg does not bind selected side/profile/fresh snapshot')
 need(pin(prereg)['sha256']==session['root_prereg_sha256']and pin(snapshot/'compiled-source-manifest.json')['sha256']==session['snapshot_manifest_sha256']and resolve(session['root_prereg'])==prereg and resolve(session['snapshot'])==snapshot,'Actual session prereg/snapshot identity differs')
 need(same_pin(v['native_report'],pin(report_path))and same_pin(v['Root_prereg'],pin(prereg))and same_pin(v['compiled_manifest'],pin(snapshot/'compiled-source-manifest.json'))and same_pin(v['candidate_freeze'],contract['official_observer_freeze'])and session['candidate_freeze_sha256']==contract['official_observer_freeze']['sha256'],'Independent receipt native/source provenance differs')
 need(v['actual_complete50_resident']is True and v['actual_quad_source_floor_and_mirror_verified']is True and v['native_CRC_FIFO_verified']is True and v['source_phase_frames']==12 and v['actual_adjacent_joins']==r['joins'],'Actual50/quad/CRC/12phase/four joins gates absent')
 optics=v['optical_source_projection'];need(optics['passed']is True and optics['registration_search_used']is False and optics['actual_pixels_modified']is False,'Actual fixed source projection PASS required')
 need(r['silent_video']is True and r['audio_recorded']is False and v['audio_recorded']is False and r['visual_reviewed']is False and v['visual_reviewed']is False and v['FinalAccepted']is False and r['formal_complete_units']==0,'Silent unaccepted native proof scope differs')
 checker=checked(contract['official_checker'])
 rerun=subprocess.run([sys.executable,'-B','-X','utf8',str(checker),'--snapshot',str(snapshot),'--root-prereg',str(prereg),'--archive',str(archive)],capture_output=True,text=True,encoding='utf-8')
 need(rerun.returncode==0,'Readonly official Stomp checker rejected actual inputs: '+rerun.stderr);need(json.loads(rerun.stdout)==v,'Retained independent receipt differs from exact readonly rerun')
 receipts=[json.loads(x)for x in(original/'native-frame-pixels.jsonl').read_text(encoding='utf-8-sig').splitlines()if x]
 movie=[x for x in receipts if x['file'].startswith('MovieFrame')];frames=[original/x['file']for x in movie]
 need(frames and len({f.name for f in frames})==len(frames)and[f.name for f in frames]==sorted(f.name for f in frames)and{f.name for f in frames}=={p.name for p in original.glob('MovieFrame*.png')},'Actual original movie PNG sequence missing/duplicated/reordered')
 obs=r['observations'];timing=r['capture_timing'];offsets=timing['frame_wall_offsets_s'];duration=timing['capture_stop_monotonic_s']-timing['capture_start_monotonic_s']
 need(len(frames)==len(obs)==len(offsets)and all(math.isfinite(t)for t in offsets)and all(b>a for a,b in zip(offsets,offsets[1:]))and duration>offsets[-1]>=offsets[0]>=0 and timing['use_fixed_time_step']is False and all(o['wall_offset_s']==t for o,t in zip(obs,offsets)),'Original callback wall timeline differs; never use simulation time for encoding')
 witnesses=optics['source_registered_native_witnesses'];need(len(witnesses)==12,'Independent source optics lacks twelve original witnesses');samples=[]
 for clip,count in CLIPS:
  for frame in range(count):
   found=[w for w in witnesses if w['clip']==clip and w['frame']==frame];need(len(found)==1,'Missing/duplicate optical phase witness');w=found[0];i=w['observation'];need(type(i)is int and 0<=i<len(frames)and frames[i].name==w['original_PNG'],'Optical witness does not name its original callback PNG')
   d=guard_draw(obs[i],r['guard_entity']);s=d['Selection'];need(d['DrawId']==w['native_draw_id']and s['AttackId']==w['AttackId']=='2'and s['Clip']==d['AssetClip']==clip and s['Frame']==d['AssetFrame']==frame,'Optical witness was substituted by another actual source frame/Aid/draw')
   match=[z for z in v['coverage_witnesses']if z['observation']==i and z['DrawId']==d['DrawId']and z['clip']==clip and z['frame']==frame and z['AttackId']=='2'and z['SourceEventId']==s['SourceEventId']];need(len(match)==1,'Optical witness is not actual independent native coverage')
   typed=next(row for row in read(profile)['rows']if row['clip']==clip)['frames'][frame]
   need(typed['object_path']==d['TexturePath']and typed['source']['sha256']==d['SourceSHA256']and typed['RGBA_sha256']==d['SourceRGBASHA256'],'Actual sample differs from the shared typed source binding')
   samples.append(dict(clip=clip,frame=frame,observation=i,independent_optical_witness=w,draw=d,typed_source_binding=typed))
 joins=r['joins'];need(len(joins)==4 and{x['name']for x in joins}==set(JOIN_NAMES),'Four original adjacent joins required')
 for j in joins:
  i,k=j['before_observation'],j['after_observation'];need(type(i)is int and type(k)is int and 0<=i<k<len(obs)and k==i+1,'Join is not strictly adjacent original callback')
  before,after=guard_draw(obs[i],r['guard_entity']),guard_draw(obs[k],r['guard_entity']);need(j['before_draw']==before and j['after_draw']==after,'Join metadata differs from actual original draw callbacks')
  for d in [before,after]:need(d['Drawn']is True and d['QuadSubmitted']is True and d['ProfileId']=='GuardStomp50V004','Actual joined quad was not submitted')
  need(after['Selection']['AttackId']=='2','Join advances another attack')
  if j['name']=='Ready-to-StompWU0':need(before['Selection']['Clip']=='Ready'and before['Selection']['AttackId']=='1','Before-Ready must retain actual first Axe1, not a fabricated Stomp2 Ready')
  else:need(before['Selection']['AttackId']=='2','Internal/return join spliced a different attack')
 bindings=dict(archive=archive.as_posix(),report=pin(report_path),independent=pin(proof_path),session=pin(archive/'index.json'),official_checker=pin(checker),official_observer_freeze=contract['official_observer_freeze'],Root_prereg=pin(prereg),compiled_manifest=pin(snapshot/'compiled-source-manifest.json'),typed_profile=pin(profile),official_readonly_rerun_passed=True)
 return dict(archive=archive,report=r,proof=v,frames=frames,offsets=offsets,duration=duration,samples=samples,joins=joins,bindings=bindings)

def quad_box(d):
 need(d['QuadRotationDegrees']==0 and d['QuadRotationPivot']==[0,0]and d['QuadDrawScale']==1 and d['QuadScalePosition']is False,'Crop requires actual ordinary wholebody quad')
 x,y=d['QuadTop'];w,h=d['QuadSize'];gx,gy=d['GroundScreen'];return[x-gx,y-gy,x+w-gx,y+h-gy]

def write_side(output,label,data):
 raw=output/'原件'/label;show=output/'展示副本'/label;raw.mkdir();show.mkdir()
 r=data['report'];obs=r['observations'];frames=data['frames'];offsets=data['offsets'];duration=data['duration']
 encoder=runpy.run_path(str(C/'tooling/retained-microsecond-VFR-v001.py'));video,last,timing,decoded=encoder['encode_vfr'](show,frames,offsets,duration)
 refs=[]
 for i,(f,t,o)in enumerate(zip(frames,offsets,obs)):
  d=next((d for d in o.get('guard_draws',[])if d['EntityId']==r['guard_entity']),None)
  refs.append(dict(observation=i,native_original=pin(f),wall_offset_s=t,decoded_PTS_s=int(decoded[i][2])/1.e6,simulation_time=o['sim'],guard_time=o.get('guard_time'),actual_guard_draw=d))
 def copy_frame(i,name):
  target=raw/name;need(not target.exists(),'Never overwrite original copy');shutil.copy2(frames[i],target);need(pin(frames[i])['sha256']==pin(target)['sha256'],'Source PNG copy changed')
  with Image.open(target)as im:need(im.format=='PNG'and im.size==(1280,720),'Original full1280x720 PNG required')
  return dict(observation=i,source=pin(frames[i]),copy=pin(target),wall_offset_s=offsets[i],simulation_time=obs[i]['sim'],guard_time=obs[i].get('guard_time'),actual_guard_draw=guard_draw(obs[i],r['guard_entity']),resized=False,pixels_edited=False)
 samples=[]
 for s in data['samples']:
  item=copy_frame(s['observation'],f'{s["clip"]}-{s["frame"]:02d}-UNSCALED-native-v001.png');item.update(clip=s['clip'],frame=s['frame'],independent_optical_witness=s['independent_optical_witness'],typed_source_binding=s['typed_source_binding']);samples.append(item)
 joins=[]
 for j in data['joins']:
  pair=[copy_frame(j[key+'_observation'],f'JOIN-{j["name"]}-{key}-UNSCALED-native-v001.png')for key in ['before','after']]
  joined=dict(name=j['name'],pair=pair,original_adjacent_callbacks=True,intervening_native_frames=0,wall_delta_s=offsets[j['after_observation']]-offsets[j['before_observation']],interpolated=False,retimed=False,source_metadata=j);joins.append(joined)
 final_native=copy_frame(len(frames)-1,'native-final-UNSCALED-v001.png')
 # One constant guard-ground-relative crop covers actual quads across all12 samples/8 join endpoints.
 items=samples+[p for j in joins for p in j['pair']];boxes=[quad_box(x['actual_guard_draw'])for x in items]
 box=[math.floor(min(q[0]for q in boxes))-8,math.floor(min(q[1]for q in boxes))-8,math.ceil(max(q[2]for q in boxes))+8,math.ceil(max(q[3]for q in boxes))+8]
 def crop(item,name):
  gx,gy=item['actual_guard_draw']['GroundScreen'];b=[math.floor(gx+box[0]),math.floor(gy+box[1]),math.ceil(gx+box[2]),math.ceil(gy+box[3])];need(0<=b[0]<b[2]<=1280 and 0<=b[1]<b[3]<=720,'Native crop would clip original viewport')
  with Image.open(item['copy']['path'])as im:cut=im.convert('RGB').crop(b)
  target=show/name;cut.save(target);return dict(observation=item['observation'],source=item['source'],crop=pin(target),source_pixel_crop_box=b,constant_ground_relative_box=box,resized=False,painted=False)
 crops=[crop(s,f'{s["clip"]}-{s["frame"]:02d}-NATIVE-PIXEL-CROP-v001.png')for s in samples]
 cw=max(q['source_pixel_crop_box'][2]-q['source_pixel_crop_box'][0]for q in crops)+2;ch=max(q['source_pixel_crop_box'][3]-q['source_pixel_crop_box'][1]for q in crops)+24
 sheet=Image.new('RGB',(4*cw,3*ch),(26,29,34));draw=ImageDraw.Draw(sheet)
 for n,(s,q)in enumerate(zip(samples,crops)):
  x,y=(n%4)*cw,(n//4)*ch;draw.text((x+3,y+5),f'{s["clip"]} {s["frame"]} | obs{s["observation"]}',fill='white')
  with Image.open(q['crop']['path'])as im:sheet.paste(im.convert('RGB'),(x,y+24))
 sheet.save(show/'Stomp12-NATIVE-PIXEL-CROP-contact-v001.png')
 full=Image.new('RGB',(4*1280,3*744),(26,29,34));draw=ImageDraw.Draw(full)
 for n,s in enumerate(samples):
  x,y=(n%4)*1280,(n//4)*744;draw.text((x+8,y+6),f'{s["clip"]} {s["frame"]} | obs{s["observation"]} | Aid2',fill='white')
  with Image.open(s['copy']['path'])as im:full.paste(im.convert('RGB'),(x,y+24))
 full.save(show/'Stomp12-FULL-native-unscaled-contact-v001.png')
 for j in joins:
  full=Image.new('RGB',(2560,744),(26,29,34));draw=ImageDraw.Draw(full);jc=[]
  for n,s in enumerate(j['pair']):
   sel=s['actual_guard_draw']['Selection'];draw.text((n*1280+8,6),f'{sel["Clip"]} {sel["Frame"]} | Aid{sel["AttackId"]} | obs{s["observation"]}',fill='white')
   with Image.open(s['copy']['path'])as im:full.paste(im.convert('RGB'),(n*1280,24))
   jc.append(crop(s,f'JOIN-{j["name"]}-{n}-NATIVE-PIXEL-CROP-v001.png'))
  full.save(show/f'JOIN-{j["name"]}-FULL-native-unscaled-pair-v001.png')
  sw=max(q['source_pixel_crop_box'][2]-q['source_pixel_crop_box'][0]for q in jc)+2;sh=max(q['source_pixel_crop_box'][3]-q['source_pixel_crop_box'][1]for q in jc)+24;contact=Image.new('RGB',(2*sw,sh),(26,29,34));draw=ImageDraw.Draw(contact)
  for n,q in enumerate(jc):
   draw.text((n*sw+3,5),f'{"before"if n==0 else "after"} obs{q["observation"]}',fill='white')
   with Image.open(q['crop']['path'])as im:contact.paste(im.convert('RGB'),(n*sw,24))
  contact.save(show/f'JOIN-{j["name"]}-NATIVE-PIXEL-CROP-pair-v001.png');j['crops']=jc
 for name in ['runtime-report.json','independent-Stomp50-native-verification-v001.json']:
  shutil.copy2(data['archive']/'原件'/name,raw/name)
 shutil.copy2(data['archive']/'index.json',raw/'native-session-index-readonly-copy.json')
 with Image.open(frames[-1])as im:native=im.convert('RGB')
 with Image.open(last)as im:decoded_last=im.convert('RGB')
 import numpy as np
 error=np.abs(np.asarray(native,dtype=np.int16)-np.asarray(decoded_last,dtype=np.int16))
 final=dict(native_original=pin(frames[-1]),native_copy=final_native,decoded_final=pin(last),native_source_index=len(frames)-1,decoded_frame_index=len(frames)-1,decode_count_equals_native=True,lossy_presentation=True,lossy_RGB_mean_absolute_error=float(np.mean(error)),lossy_RGB_max_absolute_error=int(np.max(error)),native_and_decoded_are_separate=True,lossy_video_pixel_equality_not_claimed=True,visual_reviewed=False)
 dump_new(raw/'decoded-final-source-association-v001.json',final)
 result=dict(schema='Guard-Stomp50-native-media-side-index-v001',status='NATIVE_INDEPENDENT_PASS_MEDIA_E_AND_VISUAL_REVIEW_PENDING',actual_side=r['actual_approach_side'],native_bindings=data['bindings'],native_frame_count=len(frames),source_frames=refs,video=pin(video),presentation_frame_retention=timing,phase_samples=samples,required_phase_samples=12,actual_adjacent_joins=joins,required_joins=4,crops=crops,final_frame=final,native_originals_modified=False,all_original_frames_encoded_once=True,wall_clock_used_for_video=True,simulation_or_Guard_clock_used_for_video=False,video_silent=True,audio_recorded=False,physical_floor_or_footlock_or_hidden_socket_measured=False,visual_reviewed=False,FinalAccepted=False,formal_complete_units=0,E_before_view_required=True)
 (show/'README.md').write_text('同一侧真实原生记录的完整1280×720静音VFR：Enter/E正常提交SWD+LGT，前置Knight/Bat明确诊断清除，WASD绕守卫宽体至指定侧；主角/守卫无诊断伤害、位置、朝向或时钟写入。首个自然Stomp必须Aid2，真实WU6/Active2/Recovery4与四处原回调相邻接帧。前Ready保留Axe1，回接Ready保留Stomp2；不是完整房间通关。12相来自独立固定源光学见证原PNG，full/crop/contact只原幅复制和布局，标签在原像素之外；不补姿态、不缩放原PNG、不改速、不拼动作。全帧微秒VFR按真实callback墙钟而非Guard/sim时钟，逐源帧对应一个解码帧；视频有损展示，原PNG仍以原CRC为准。末帧原/解码分开存档和索引。floor/root是已声明源注册作者参数，未冒称实测足锁/隐藏骨轴/独立斧握点。无声音/语音；本目录等待Root E双SHA保全后才能View/播放；未审阅/未FinalAccepted。\n',encoding='utf-8')
 result['output_files']=[pin(p)for folder in[raw,show]for p in sorted(folder.iterdir())if p.is_file()]
 dump_new(raw/'source-version-status-index.json',result)
 return dict(side=r['actual_approach_side'],index=pin(raw/'source-version-status-index.json'),video=pin(video),native_frames=len(frames),decoded_frames=timing['decoded_frames'],phase_samples=12,adjacent_joins=4,decoded_final=pin(last),native_final=pin(frames[-1]),native_archive_modified=False)

def main():
 parser=argparse.ArgumentParser()
 for name in ['left-archive','right-archive','snapshot','left-prereg','right-prereg','profile']:parser.add_argument('--'+name,required=True)
 parser.add_argument('--output');parser.add_argument('--validate-only',action='store_true');args=parser.parse_args();contract=dependencies();snapshot=resolve(args.snapshot);profile=resolve(args.profile)
 left=actual_inputs(resolve(args.left_archive),snapshot,resolve(args.left_prereg),profile,-1,contract);right=actual_inputs(resolve(args.right_archive),snapshot,resolve(args.right_prereg),profile,1,contract)
 need(left['archive']!=right['archive']and left['report']['process_id']!=right['report']['process_id'],'Two independent actual native processes required')
 if args.validate_only:
  print(json.dumps(dict(actual_native_and_independent_pass=True,left_frames=len(left['frames']),right_frames=len(right['frames']),phase_samples_per_side=12,adjacent_joins_per_side=4,media_written=False,UE_started=False,visual_reviewed=False),ensure_ascii=False));return
 need(args.output,'NEW absolute F dated output leaf required');output=Path(args.output);need(output.is_absolute(),'Output must be absolute');output=output.resolve();need(output.is_relative_to(R/'过程图稿与视频')and not output.exists()and output.parent.is_dir(),'Use a NEW F dated topic leaf under existing media parent')
 for data in [left,right]:need(output!=data['archive']and output not in data['archive'].parents and data['archive']not in output.parents,'Output must be outside both readonly native archives')
 output.mkdir();(output/'原件').mkdir();(output/'展示副本').mkdir();status=dict(schema='Guard-Stomp50-native-media-pair-source-version-status-v001',status='PREPARING_UNVIEWED_ROOT_E_REQUIRED',media_candidate=pin(C/'Stomp-native-media-freeze-v001.json'),sides=[],native_originals_modified=False,UE_started=False,visual_reviewed=False,FinalAccepted=False,E_before_view_required=True)
 try:
  for name,data in [('left',left),('right',right)]:status['sides'].append(write_side(output,name,data))
  status['status']='ACTUAL_NATIVE_INDEPENDENT_PASS_MEDIA_ROOT_E_AND_VISUAL_REVIEW_PENDING'
  (output/'README.md').write_text('左右两个独立PID、同一已编译快照与Root归一50profile的真实首个Stomp Aid2完整静音实录。每侧原件在原件/left、原件/right，展示在展示副本/left、展示副本/right独立保留；未把两侧或不同攻击拼成动作。每侧含12相原幅/原像素crop及四处严格相邻full/crop接帧、完整原电影帧序列VFR、帧数/微秒PTS/末帧来源索引；prewarm校验帧留在原生archive，不虚构其电影时基。Root E双SHA保全前禁止View/播放；未审阅、未足锁或FinalAccepted。\n',encoding='utf-8')
  (output/'展示副本/OPEN-AFTER-ROOT-E.md').write_text('Root E保全后分别查看left、right的完整720p视频、12相contact、四处FULL接帧和原/解码末帧。原幅样本在同主题原件/left、原件/right。原件未改；不自动打开。\n',encoding='utf-8')
  status['root_documents']=[pin(output/'README.md'),pin(output/'展示副本/OPEN-AFTER-ROOT-E.md')]
 except Exception as error:status['status']='FAILED_PRESERVED';status['failure']=str(error);raise
 finally:dump_new(output/'source-version-status-index.json',status)
 print(json.dumps(dict(output=output.as_posix(),sides=status['sides'],native_archives_modified=False,media_viewed=False,Root_E_before_view_required=True),ensure_ascii=False))
if __name__=='__main__':main()
