"""Record performed raw art review and actual retained candidate without runtime acceptance."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,shutil
R=Path('F:/Ourgame');EV=R/'docs/production/first-batch-v2/evidence/HeroAirDiskRestore-v144-v001'
O=EV/'current300-GREEN-art257-native-pending-status-v002'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def pin(p):
 p=Path(p).resolve();b=p.read_bytes();return dict(path=p.as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def new(p,v):
 with Path(p).open('x',encoding='utf-8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
prior=EV/'current300-GREEN-native-pending-status-v001/current-status.json'
C=R/'source-assets/production/fairytale-hero-four-pose-polish-v001/request257-primary1-body'
raw=C/'raw/primary1-bridge-body.png';assert pin(raw)['sha256']=='61cc190baf284d696971f152f373c8882708849982b7ecaed00b841ccef40d22'
E=Path('E:/OurGame/Knight/过程图稿与视频')
retentions=[]
for number in (627,628):
 matches=list(E.glob('2026-10-19-本项目E'+str(number)+'-*/E-retention-index-v001.json'));assert len(matches)==1
 value=read(matches[0]);assert value['verification_passes']==2 and value['kind']=='full' and value['full_source_member_retention']
 retentions.append(dict(batch=number,index=pin(matches[0])))
review_path=C/'Root-raw-review-v001.json'
review=dict(schema='Root-primary-bridge257-raw-limited-review-v001',utc=datetime.now(timezone.utc).isoformat(),raw=pin(raw),retained_before_Root_View=retentions,Root_viewed_full_raw=True,facts=['Raw1536x1024 has six complete body poses in2rows3cols; J0moderatecrouch andJ1raised-arm preparation visible.', 'Bell helmet/no-human-face/gray inner-clothing and leather glove/boot identity retained; no sword or FX baked into body.'],open=['J0/J1 truefoot/head/helmet scale and newRoot/Grip/Axis need extraction/measurement.', 'J1 may still rise too sharply into existingJ2; ordinaryReady andLand4 entries both need native comparison.', 'Armor3layers and bodyowners are not rebuilt/imported; this raw image is not the equipped runtime silhouette.'],full_realtime_playback_reviewed=False,UE_imported=False,final_art_accepted=False,FinalAccepted=False)
new(review_path,review)
ledger=R/'source-assets/production/first-unit-animation-v003/generation-ledger.json';g=read(ledger);assert g['requested_count']==257 and g['current_window']['requested_count']==17
s=read(prior);s.update(schema='Root-current-air-disk-art257-v144-status-v002',utc=review['utc'],prior_status_pin=pin(prior),last_E_batch=628,next_E_batch=629,image_generation_calls_this_turn=1,current_generation_requested=257,current_window_requested=17,current_window_remaining=7,lifetime_requested=281,hero_primary_bridge257=dict(raw=pin(raw),generation_result=pin(C/'generation257-result-v001.json'),Root_raw_review=pin(review_path),E=retentions,UE_imported=False,final_art_accepted=False),actual_v144_native_verified=False,next_task='Scoped checker fixes review, real sequential disk source/target capture; J0/J1 extraction candidate in parallel',FinalAccepted=False)
O.mkdir();(O/'before').mkdir();new(O/'current-status.json',s)
files=[R/'README.md',R/'docs/production/first-batch-v2/progress.json',R/'项目需求台账.md',ledger]
for p in files:
 dst=O/'before'/p.relative_to(R);dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dst)
old=files[0].read_text(encoding='utf-8-sig');_,rest=old.split('\n\n',1)
head='2026-10-19 当前进行中（EV048，v144）：Source300／Production1419实际编译与原有D3D11完整203测试严格通过。双进程磁盘继续尚待执行，核验工具两处审阅问题已在新候选修复，独立复核中。新增攻击J0/J1身体修片request257已生成、F/E627–628保全并有限审图，提取／盔甲适配／实机接入尚未完成；六条本地动作音效候选也尚未导入／绑定／试听。[快捷试玩](钟盔轻甲快捷试玩.cmd)保持独立v142；[当前状态](docs/production/first-batch-v2/evidence/HeroAirDiskRestore-v144-v001/current300-GREEN-art257-native-pending-status-v002/current-status.json)。美术与动作衔接继续精修，正式0/15、搭配0/20；目标active。内置累计请求257，窗口11用17余7、生命周期281（另初始3）；外部API0，内置费用未知。'
asset='| 新候选 | 内容 | 游戏内尺寸 | 路径 | 状态 |\n|---|---|---|---|---|\n| 攻击起手修片257 | J0/J1身体起手；六格上下文 | 站立等效72px，源格512×512 | [完整原件](source-assets/production/fairytale-hero-four-pose-polish-v001/request257-primary1-body/raw/primary1-bridge-body.png) | 已生成与有限审图，未导入 |\n\n'
files[0].write_text(head+'\n\n'+asset+rest,encoding='utf-8')
q=read(files[1]);q.update(current_status_authority=pin(O/'current-status.json'),current_task=s['next_task'],current_generation_accounting=dict(requested=257,window=g['current_window'],remaining=7,lifetime=281,external_api_calls=0,host_fee_usd=None,automatic_follow_on_batches_authorized=True),current_hero_primary_bridge257=s['hero_primary_bridge257']);files[1].write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
with files[2].open('a',encoding='utf-8') as f:f.write('\n2026-10-19 EV048执行进展：为延续用户的怪诞画风、盔甲与轮廓辨识要求，新增内置request257攻击J0/J1身体修片，E627–628留存及有限原图审阅；尚未提取／分层／换甲／实装。原运行Source300与203GREEN不变，正式内容不计完成。\n')
g['requests'][-1].update(status='raw_root_reviewed_extraction_pending_not_runtime',Root_raw_review=pin(review_path));g.setdefault('derived_deliveries',[]).append(dict(id='EV048-hero-primary-bridge257-raw-retained-limited-review-v001',utc=s['utc'],status=pin(O/'current-status.json'),image_generation_calls=1,external_API_calls=0,formal_complete_units=0,FinalAccepted=False));ledger.write_text(json.dumps(g,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
new(O/'status-sync-receipt.json',dict(status=pin(O/'current-status.json'),after=[pin(p) for p in files],backups_preserved=True,Source_Content_unchanged=True,FinalAccepted=False))
print(json.dumps(pin(O/'current-status.json'),ensure_ascii=False))
