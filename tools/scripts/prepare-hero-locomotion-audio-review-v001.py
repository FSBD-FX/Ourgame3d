"""Root preserve six LOCAL audio candidates before preview; no UE or events."""
from pathlib import Path
from datetime import datetime, timezone
import array, hashlib, json, math, shutil, subprocess, sys, wave
R=Path('F:/Ourgame'); C=R/'source-assets/production/hero-locomotion-audio-candidate-v001'
def pin(p):
    p=Path(p).resolve(); b=p.read_bytes()
    return dict(path=p.as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def new(p,d):
    with Path(p).open('x',encoding='utf-8') as f:
        if isinstance(d,str):f.write(d)
        else:json.dump(d,f,ensure_ascii=False,indent=2);f.write('\n')
freeze=C/'HeroLocomotionAudio-Candidate-freeze-v001.json'; index=C/'HeroLocomotionAudio-Candidate-index-v001.json'
assert pin(freeze)['sha256']=='cf63ec47a15855f17703f72540471d8cba2a7a952a26bfc7bc03acd0b2f216ac'
f=read(freeze); i=read(index); expected={x['relative_path'] for x in f['files']}|{freeze.name,index.name}
assert {x.relative_to(C).as_posix() for x in C.rglob('*') if x.is_file()}==expected
for repeat in range(2):
    for row in f['files']:
        q=pin(C/row['relative_path']); assert (q['bytes'],q['sha256'])==(row['bytes'],row['sha256'])
assert f['file_count']==67 and len(i['assets'])==6
out=R/'过程图稿与视频/2026-10-19_钟盔轻甲六条本地音效试音候选_v001'
out.mkdir(); (out/'原件').mkdir();(out/'展示副本').mkdir()
shutil.copytree(C,out/'原件/candidate')
qa=[]
for row in i['assets']:
    source=C/row['relative_path']; target=out/'展示副本'/source.name
    shutil.copy2(source,target)
    assert source.read_bytes()==target.read_bytes()
    with wave.open(str(target),'rb') as w:
        assert (w.getframerate(),w.getnchannels(),w.getsampwidth(),w.getcomptype())==(48000,1,2,'NONE')
        count=w.getnframes(); pcm=w.readframes(count); assert len(pcm)==count*2 and w.readframes(1)==b''
    samples=array.array('h');samples.frombytes(pcm)
    if sys.byteorder!='little':samples.byteswap()
    peak=max(abs(x) for x in samples)/32768; rms=math.sqrt(math.fsum(x*x for x in samples)/len(samples))/32768
    assert count>0 and peak>0 and samples[0]==samples[-1]==0 and all(abs(x)<32767 for x in samples)
    qa.append(dict(source=pin(source),presentation=pin(target),frames=count,seconds=count/48000,peak=peak,rms=rms,clipped_samples=0,first_last_zero=True,full_PCM_read=True,auditioned=False))
for row in f['files']:
    copy=pin(out/'原件/candidate'/row['relative_path']);assert (copy['bytes'],copy['sha256'])==(row['bytes'],row['sha256'])
audit=R/'.superpowers/sdd/2026-10-19-hero-air-disk-restore-v144/hero-audio-gap-audit-v001.md'
addendum=R/'docs/superpowers/specs/2026-10-19-hero-air-disk-restore-audio-addendum-v001.md'
shutil.copy2(audit,out/'原件'/audit.name);shutil.copy2(addendum,out/'原件'/addendum.name)
record=dict(schema='Root-hero-locomotion-audio-audition-preparation-v001',utc=datetime.now(timezone.utc).isoformat(),candidate_freeze=pin(freeze),candidate_index=pin(index),source_members=67,source_SHA_passes=2,source_SHA_mismatches=0,exact_candidate_membership=True,assets=qa,source_audit=pin(audit),target_capture_policy=pin(addendum),Root_approved_for_trial_preparation=True,auditioned=False,stone_boot_material_audibly_verified=False,final_mix_approved=False,UE_imported=False,event_bound=False,actual_v144_audio_unchanged=True,Source_Content_unchanged=True,external_API_calls=0,image_generation_calls=0,formal_complete_units=0,FinalAccepted=False)
record_path=out/'原件/Root-preparation-verification-v001.json';new(record_path,record)
shutil.copy2(record_path,out/'展示副本/Root-preparation-verification-v001.json')
new(out/'README.md','钟盔轻甲的6条LOCAL音效试音候选：轻脚步2、起跳、轻落地、较重落地、短闪避。来自本地Kenney素材处理，完整来源／许可／配方及失败历史在原件candidate中。展示WAV与候选逐字节一致。泛用脚步的石地／皮靴材质、听感、最终混音、UE导入和真实事件绑定仍未验收；不计完整内容单元。当前v144恢复录音实验不播放或使用这些候选。\n')
new(out/'来源-版本-状态索引.json',dict(schema='Root-local-audio-trial-source-version-status-v001',Root_record=pin(record_path),files=[pin(p) for p in sorted(out.rglob('*')) if p.is_file()],auditioned=False,UE_imported=False,event_bound=False,FinalAccepted=False))
retainer=R/'source-assets/production/fairytale-hero-air-v001/native-retention-solid-candidate-v001/retain-native-media-lossless-solid-tar-xz-v001.py'
batch='2026-10-19-本项目E626-钟盔轻甲六条LOCAL音效试音候选-v001'
subprocess.run([str(R/'tools/runtime/asset-gen/Scripts/python.exe'),'-B','-X','utf8',str(retainer),'--source',str(out),'--batch',batch,'--preset','3'],check=True)
E=Path('E:/OurGame/Knight/过程图稿与视频')/batch/'E-retention-index-v001.json';assert read(E)['verification_passes']==2
EV=R/'docs/production/first-batch-v2/evidence/HeroLandingPriority-v143-v001'
prior_path=EV/'current298-GREEN-four-native-reviewed-status-v003/current-status.json';s=read(prior_path)
O=EV/'current298-four-native-audio-candidates-status-v004';O.mkdir();(O/'before').mkdir()
s.update(schema='Root-current-four-native-local-audio-candidates-v004',utc=record['utc'],prior_status_pin=pin(prior_path),local_audio_trial=pin(record_path),local_audio_trial_E=pin(E),local_audio_candidates=6,local_audio_listened=False,local_audio_UE_imported=False,local_audio_event_bound=False,last_E_batch=626,next_E_batch=627,audio_gap_audit=pin(audit),target_audio_policy_addendum=pin(addendum))
new(O/'current-status.json',s)
files=[R/'README.md',R/'docs/production/first-batch-v2/progress.json',R/'项目需求台账.md',R/'source-assets/production/first-unit-animation-v003/generation-ledger.json']
for p in files:
    dest=O/'before'/p.relative_to(R);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest)
text=files[0].read_text(encoding='utf-8-sig');head,rest=text.split('\n\n',1)
head=head.replace('current298-GREEN-four-native-reviewed-status-v003','current298-four-native-audio-candidates-status-v004').replace('E617–625完整保全','E617–626完整保全')
head+=' 已准备6条本地脚步／起跳／落地／闪避音效候选并保全来源，试听／游戏事件绑定未完成。'
files[0].write_text(head+'\n\n'+rest,encoding='utf-8')
q=read(files[1]);q.update(current_status_authority=pin(O/'current-status.json'),current_local_hero_audio_trial=pin(record_path),current_local_hero_audio_candidates=6);files[1].write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
with files[2].open('a',encoding='utf-8') as w:w.write('\n2026-10-19：继续完善首批内容；6条脚步／起跳／落地／闪避LOCAL音效候选已准备，原Kenney包／8源OGG／许可／配方／完整PCM结构记录E626双SHA保全。泛用脚步材质与听感、UE导入、动作事件及最终混音未验收，未接入v144录音测试，正式计数仍0。\n')
g=read(files[3]);g.setdefault('derived_deliveries',[]).append(dict(id='EV048-parallel-local-hero-locomotion-audio-candidates-v001',utc=record['utc'],Root_trial=pin(record_path),E_retention=pin(E),WAV_candidates=6,local_processing_only=True,image_generation_calls=0,external_API_calls=0,UE_imported=False,event_bound=False,auditioned=False,formal_complete_units=0,FinalAccepted=False));files[3].write_text(json.dumps(g,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
new(O/'status-sync-receipt.json',dict(status=pin(O/'current-status.json'),after=[pin(p) for p in files],before_backups_preserved=True,Source_Content_unchanged=True,FinalAccepted=False))
print(json.dumps(dict(status=pin(O/'current-status.json'),Root_trial=pin(record_path),E_retention=pin(E),assets=[x['presentation'] for x in qa],next_E=627,auditioned=False,FinalAccepted=False),ensure_ascii=False))
