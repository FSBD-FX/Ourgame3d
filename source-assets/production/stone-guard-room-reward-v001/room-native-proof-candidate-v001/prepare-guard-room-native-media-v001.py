"""Root-only post-capture media preparation. No image viewing or UE launch."""
from pathlib import Path
import argparse,hashlib,json,shutil,subprocess
import imageio_ffmpeg

def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def fact(p):
    b=p.read_bytes();return dict(path=p.as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def need(v,why):
    if not v: raise ValueError(why)

p=argparse.ArgumentParser();p.add_argument('--archive',required=True);p.add_argument('--retain-name',required=True);a=p.parse_args()
archive=Path(a.archive).resolve();original=archive/'原件';show=archive/'展示副本';show.mkdir(exist_ok=True)
report=read(original/'runtime-report.json');proof=read(original/'independent-room-native-proof-v001.json')
need(report['passed'] and proof['passed'] and proof['normal_J_full_clear'] is False,'Only independently checked diagnostic flow proceeds; preserve failure originals separately')
frames=sorted(original.glob('MovieFrame*.png'));timing=report['capture_timing'];offsets=timing['frame_wall_offsets_s'];duration=report['duration_s']
need(len(frames)==len(offsets)==len(report['observations']) and duration>offsets[-1],'Actual native frame timing incomplete')
concat=show/'guard-room-native-timing-v001.ffconcat';video=show/'guard-room-native-flow-DIAGNOSTIC-silent-v001.mp4'
need(not concat.exists() and not video.exists(),'Never overwrite media preparation')
lines=['ffconcat version 1.0']
for i,f in enumerate(frames):
    dt=(offsets[i+1] if i+1<len(frames) else duration)-offsets[i];need(dt>0,'Native capture times not increasing')
    lines += ["file '"+f.as_posix().replace("'","'\\''")+"'",f'duration {dt:.12f}']
lines.append("file '"+frames[-1].as_posix().replace("'","'\\''")+"'");concat.write_text('\n'.join(lines)+'\n',encoding='utf-8')
ffmpeg=imageio_ffmpeg.get_ffmpeg_exe()
commands=[('encode-v001.log',[ffmpeg,'-hide_banner','-loglevel','error','-n','-f','concat','-safe','0','-i',str(concat),'-vsync','vfr','-t',f'{duration-offsets[0]:.9f}','-c:v','libx264','-crf','18','-pix_fmt','yuv420p','-an',str(video)]),('decode-v001.log',[ffmpeg,'-hide_banner','-loglevel','error','-i',str(video),'-f','null','-'])]
for name,cmd in commands:
    result=subprocess.run(cmd,capture_output=True,text=True,encoding='utf-8');(show/name).write_text(result.stdout+result.stderr,encoding='utf-8');need(result.returncode==0,name+' failed; preserve outputs')
samples=[]
for label,phase in [('normal-J','normal_J_combat'),('native-dodge','normal_Shift_retreat'),('bat-warning','bat_future_warning_birth'),('native-bat','native_bat_then_diagnostic_HP'),('guard-warning','guard_future_warning_birth'),('native-guard','native_guard_then_diagnostic_HP'),('restored-pause','grouped_install_pause'),('continued','complete')]:
    choices=[i for i,x in enumerate(report['observations']) if x['phase']==phase]
    if 'warning' in label:
        slot=1 if label=='bat-warning' else 2
        choices=[i for i,x in enumerate(report['observations']) if len(x.get('slots',[]))==3 and int(x['slots'][slot]['stage'])==1 and x['slots'][slot]['slot'] in x['rendered_warning_slots']]
    if label=='native-dodge':choices=[i for i in choices if report['observations'][i]['native_dodge_phase']==1]
    if label=='normal-J':choices=[i for i in choices if report['observations'][i]['native_melee_active']]
    need(bool(choices),'Actual sample phase absent: '+phase);i=choices[len(choices)//2];src=frames[i];dest=show/(label+'-UNSCALED-native.png');need(not dest.exists(),'Never overwrite sample');shutil.copy2(src,dest);samples.append(dict(source=fact(src),presentation=fact(dest),frame_index=i,resized=False))
index=dict(schema='guard-room-native-diagnostic-media-v001',status='TECHNICAL_DIAGNOSTIC_PASSED_VISUAL_REVIEW_PENDING',video=fact(video),report=fact(original/'runtime-report.json'),independent=fact(original/'independent-room-native-proof-v001.json'),samples=samples,normal_J_full_clear=False,diagnostic_damage=True,same_process_grouped_RootV2_only=True,audio_recorded=False,visual_reviewed=False,formal_complete_units=0)
(archive/'source-version-status-index.json').write_text(json.dumps(index,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(archive/'README.md').write_text('真实UE原生窗口流程诊断：正常房间URL、公共展示轻甲源与真实E换装、正常移动/J伤害与Shift，余血通过公开ApplyCombatHit推进；三个敌人由真实房间计划串行预警与出生，地面7/4/9金币正常拾取，RootV2同进程分组恢复。不是正常J全通关、双进程磁盘、可听音频、最终美术或完整单元验收。原件/原时间戳静音录像/未缩放原帧展示副本保留；视觉待Root审阅。\n',encoding='utf-8')
retain_base=Path('E:/OurGame/Knight/过程图稿与视频').resolve();need(Path(a.retain_name).name==a.retain_name and a.retain_name[:10].count('-')==2,'Require one dated topic/version retention folder name')
target=retain_base/a.retain_name;need(not target.exists(),'Never overwrite E retention');target.mkdir()
mapping=[]
for source in sorted(x for x in archive.rglob('*') if x.is_file()):
    before=fact(source);dest=target/source.relative_to(archive);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,dest)
    actual=fact(dest);need(fact(source)==before and all(before[k]==actual[k] for k in ['bytes','sha256']),'E retained bytes differ');mapping.append(dict(source=before,retained=actual))
(target/'E-retention-index-v001.json').write_text(json.dumps(dict(schema='guard-room-native-E-retention-v001',status='DIAGNOSTIC_MEDIA_RETAINED_BEFORE_ROOT_VIEW',source_archive=archive.as_posix(),files=mapping,total_bytes=sum(x['retained']['bytes'] for x in mapping),visual_reviewed=False,normal_J_full_clear=False),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(E_archive=target.as_posix(),video=fact(target/video.relative_to(archive)),samples=[(target/Path(x['presentation']['path']).relative_to(archive)).as_posix() for x in samples],root_view_still_required=True),ensure_ascii=False))
