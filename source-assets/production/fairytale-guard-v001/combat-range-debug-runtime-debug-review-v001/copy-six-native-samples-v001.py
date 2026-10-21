"""Copy six original native frames only; exact existing proofs/CRC/log binding; never View."""
from pathlib import Path
import hashlib,json,shutil,zlib
from PIL import Image
R=Path('F:/Ourgame');C=Path(__file__).resolve().parent
T=R/'source-assets/production/fairytale-guard-v001/combat-range-debug-tooling-candidate-v002'
D=R/'source-assets/production/fairytale-guard-v001/combat-range-debug-runtime-review-v001'
show=R/'过程图稿与视频/2026-10-18_守卫范围默认关闭与显式调试六帧对照_v001'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def pin(p):
 b=p.read_bytes();return dict(path=p.as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
assert not show.exists();assert not(C/'six-native-samples-source-binding-v001.json').exists()
sessions=[('defaultL','default_left_v001',D/'default-left-readonly-v002-replay.json','default0',0),('defaultR','default_right_v001',D/'default-right-readonly-v002-replay.json','default0',0),('debugL','debug_left_v001',C/'debug-left-readonly-v002-replay.json','debug1',4)]
prepared=[];bound=[]
for label,version,replay_path,mode,lines_expected in sessions:
 archive=R/f'过程图稿与视频/2026-10-18_守卫范围默认关闭与显式调试Hurt试样_{version}';orig=archive/'原件'
 report_path=orig/'runtime-report.json';pixels_path=orig/'native-frame-pixels.jsonl';range_path=orig/'combat-range-debug-verification-v001.json';log_path=archive/'runtime.log';session_path=archive/'index.json'
 before=[pin(p)for p in [report_path,pixels_path,range_path,log_path,session_path,replay_path]]
 r=read(report_path);v=read(replay_path);idx=read(session_path)
 assert v==read(range_path) and v['passed']is True and r['passed']is True and r['flow_complete']is True and idx['exit_code']==0 and idx['combat_range_independent_passed']is True
 assert v['mode']==mode and r['hit_attack']==v['original_hit_attack']=='1' and idx['process_id']==int(r['process_id'])
 rows=[json.loads(line)for line in pixels_path.read_text(encoding='utf-8-sig').splitlines()if line];movie=[x for x in rows if x['file'].startswith('MovieFrame')];obs=r['observations'];assert len(movie)==len(obs)
 loglines=log_path.read_text(encoding='utf-8-sig',errors='replace').splitlines()
 for phase in ['AxeWindup','AxeActive']:
  witnesses=v['focus_witnesses'][phase];assert witnesses
  first=obs[witnesses[0]['observation']]['guard_action'];target=(first['start']+first['active_at'])/2 if phase=='AxeWindup'else(first['active_at']+first['active_end'])/2
  w=min(witnesses,key=lambda x:(abs(x['sim']-target),x['observation']));i=w['observation'];o=obs[i];a=o['guard_action'];x=movie[i];source=orig/x['file']
  assert o['sim']==w['sim'] and a['attack_id']=='1' and a['kind']==1 and a['in_progress']and not a['interrupted']
  assert (a['start']<=o['sim']<a['active_at'])if phase=='AxeWindup'else(a['active_at']<=o['sim']<a['active_end'])
  assert w['submitted_range_lines']==lines_expected and x['width']==1280 and x['height']==720 and x['saved']is True and x['copy_crc_matches']is True and x['native_BGRA8_crc32']==x['copied_BGRA8_crc32'] and x['writer_sequence']==i+1
  with Image.open(source)as im:
   assert im.format=='PNG' and im.size==(1280,720)
   actual_crc=zlib.crc32(im.convert('RGBA').tobytes('raw','BGRA'))&0xffffffff
  assert actual_crc==x['native_BGRA8_crc32']
  logs=[]
  for logline,frame in zip(w['log_lines'],w['HUD_frames']):
   text=loglines[logline-1];assert f'frame={frame} 'in text and f'enabled={int(mode=="debug1")} lines={lines_expected}'in text
   stamp=float(text.split(' sim=',1)[1].split(' ',1)[0]);assert stamp==o['sim']
   logs.append(dict(log_line=logline,HUD_frame=frame,sim=stamp,enabled=int(mode=='debug1'),lines=lines_expected,actual_log_text=text))
  prepared.append(dict(label=label,mode=mode,phase=phase,process_id=r['process_id'],actual_approach_side=r['actual_approach_side'],actual_hit_AttackId='1',selection='Nearest actual eligible observation to original half-open native window midpoint; sample selection only, no clock/pixel/timing changes',native_window_midpoint=target,observation=i,sim=o['sim'],wall_offset_s=o['wall_offset_s'],source=pin(source),native_pixels_row=x,decoded_BGRA8_crc32=actual_crc,exact_sim_log_witnesses=logs,actual_native_observation=o,whole_range_readonly_proof=pin(replay_path)))
 after=[pin(p)for p in [report_path,pixels_path,range_path,log_path,session_path,replay_path]];assert before==after;bound.extend(before)
assert len(prepared)==6
(show/'原件').mkdir(parents=True);(show/'展示副本').mkdir()
for item in prepared:
 source=Path(item['source']['path']);filename=f'{item["label"]}-{item["phase"]}-mid-UNSCALED-native-v001.png'
 destinations=[show/'原件'/filename,show/'展示副本'/filename]
 for dest in destinations:
  assert not dest.exists();shutil.copy2(source,dest);assert pin(dest)['sha256']==item['source']['sha256']
 item['original_copy']=pin(destinations[0]);item['presentation_copy']=pin(destinations[1]);item['byte_identical_both_copies']=True;item['resized']=False;item['pixels_edited']=False
 assert pin(source)==item['source']
index=dict(schema='combat-range-six-native-samples-source-version-status-v001',status='ACTUAL_NATIVE_AND_INDEPENDENT_PASS_SAMPLES_COPIED_E_RETENTION_AND_VIEW_PENDING',source_topic='three fresh native Hurt sessions: default left/right and explicit debug left',version='v001',sample_count=6,dimensions=[1280,720],all_same_original_hit_AttackId='1',samples=prepared,source_bindings=bound,additional_tooling_freeze=pin(T/'combat-range-tooling-freeze-v002.json'),raw_archives_modified=False,pixels_edited=False,resized=False,synthetic_image_created=False,source_native_variable_time_unchanged=True,E_retained_by_worker=False,E_before_View_required=True,View_used=False,audio_recorded=False,visual_accepted=False,FinalAccepted=False,formal_complete_units=0)
text=json.dumps(index,ensure_ascii=False,indent=2)+'\n'
(show/'source-version-status-index.json').write_text(text,encoding='utf-8',newline='\n');(C/'six-native-samples-source-binding-v001.json').write_text(text,encoding='utf-8',newline='\n')
(show/'README.md').write_text('三份真实Hurt原生实录同一实际命中AttackId1的中段Windup与Active，共六张1280×720原幅PNG。原件与展示副本各一份，均与archive源PNG字节SHA相同；无裁切、缩放、改像素或拼图。索引逐张绑定原observation、native BGRA8 CRC32/FIFO、原sim与HUD范围提交日志；defaultL/defaultR日志lines0，debugL日志lines4。只读核验通过不等于实际视觉验收；本目录尚待Root复制E保全和View，不声明黄色框外观、默认框视觉消失或最终美术完成。\n',encoding='utf-8')
print(json.dumps(dict(topic=show.as_posix(),index=pin(show/'source-version-status-index.json'),samples=[{k:x[k]for k in ['label','phase','process_id','observation','sim','decoded_BGRA8_crc32','exact_sim_log_witnesses']}for x in prepared],Source_or_archive_written=False,View_used=False),ensure_ascii=False,indent=2))
