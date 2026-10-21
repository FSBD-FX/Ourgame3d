from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,shutil
R=Path('F:/Ourgame');EV=R/'docs/production/first-batch-v2/evidence/HeroAirDiskRestore-v144-v001';O=EV/'current300-native-reviewed-art258-status-v004'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def pin(p):
 p=Path(p).resolve();b=p.read_bytes();return dict(path=p.as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def new(p,v):
 with Path(p).open('x',encoding='utf-8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
C=R/'source-assets/production/fairytale-hero-four-pose-polish-v001/request258-primary1-body-correction';raw=C/'raw/primary1-bridge-correction.png'
assert pin(raw)['sha256']=='959b58c9a3150505e68e3a2a0235822de8f7a698f5a3929c735aa9bc7fd7b449'
ep=Path('E:/OurGame/Knight/过程图稿与视频/2026-10-19-本项目E636-钟盔攻击起手修片258-v001/E-retention-index-v001.json');assert read(ep)['verification_passes']==2
review_path=C/'Root-raw-review-v001.json'
review=dict(schema='Root-primary-bridge258-raw-limited-review-v001',utc=datetime.now(timezone.utc).isoformat(),raw=pin(raw),E_retained_before_Root_View=pin(ep),Root_viewed_full_raw=True,facts=['Helmet/boot/stance volume visually closer to accepted512guide than257.', 'J0moderatecompressed/J1partialrise progress toward existingJ2 in rawsheet.', 'Body-only grayunderlayer; armor/sword not baked in.'],open=['Exact helmet/feet/height/grip extraction metrics pending.', 'Owner partitions and3armor layers are not yet produced or imported.', 'Both Ready andLand4 entry routes plusJ1→oldJ2 require actual native comparison.'],UE_imported=False,final_art_accepted=False,FinalAccepted=False);new(review_path,review)
prior=EV/'current300-GREEN-native-reviewed-art257-status-v003/current-status.json';s=read(prior)
s.update(schema='Root-current-air-disk-art258-v144-status-v004',utc=review['utc'],prior_status_pin=pin(prior),last_E_batch=636,next_E_batch=637,image_generation_calls_this_turn=2,current_generation_requested=258,current_window_requested=18,current_window_remaining=6,lifetime_requested=282,hero_primary_bridge258=dict(raw=pin(raw),generation_result=pin(C/'generation258-result-v001.json'),Root_raw_review=pin(review_path),E=pin(ep),UE_imported=False,final_art_accepted=False),next_task='Finish six-cue native locomotion binding candidate/review; extract correctedJ0/J1 then fit armor with original72px',FinalAccepted=False)
O.mkdir();(O/'before').mkdir();new(O/'current-status.json',s)
files=[R/'README.md',R/'docs/production/first-batch-v2/progress.json',R/'项目需求台账.md',R/'source-assets/production/first-unit-animation-v003/generation-ledger.json']
for p in files:
 dst=O/'before'/p.relative_to(R);dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dst)
text=files[0].read_text(encoding='utf-8-sig');_,rest=text.split('\n\n',1)
head='2026-10-19 当前进行中（EV048，v144）：真实双进程空中磁盘保存／恢复175帧、完整Codec与原下落落地轨迹独立通过；Source300／Production1419编译与原有D3D11完整203严格通过，E629–635保全及有限4张画面审阅。第二版攻击起手修片258已生成并E636保全，头盔／脚位目视更接近原尺寸，正在提取量化；两版均未导入。六条本地脚步／起跳／落地／闪避音效的接入候选尚待冻结复核和实际编译。[快捷试玩](钟盔轻甲快捷试玩.cmd)保持独立v142；[当前状态](docs/production/first-batch-v2/evidence/HeroAirDiskRestore-v144-v001/current300-native-reviewed-art258-status-v004/current-status.json)。原速完整观看／试听、美术和其余内容继续，正式0/15、搭配0/20；目标active。内置请求258，窗口11用18余6，生命周期282另初始3；外部API0，内置费用未知。'
asset='| 新修片 | 内容 | 游戏内尺寸 | 路径 | 状态 |\n|---|---|---|---|---|\n| 攻击起手258 | J0/J1尺寸与压低起手修正 | 站立等效72px，源格512×512 | [完整原件](source-assets/production/fairytale-hero-four-pose-polish-v001/request258-primary1-body-correction/raw/primary1-bridge-correction.png) | 有限原图审阅，待提取／配甲／实装 |\n\n'
files[0].write_text(head+'\n\n'+asset+rest,encoding='utf-8')
q=read(files[1]);g=read(files[3]);assert g['requested_count']==258 and g['current_window']['requested_count']==18
q.update(current_status_authority=pin(O/'current-status.json'),current_task=s['next_task'],current_generation_accounting=dict(requested=258,window=g['current_window'],remaining=6,lifetime=282,external_api_calls=0,host_fee_usd=None,automatic_follow_on_batches_authorized=True),current_hero_primary_bridge258=s['hero_primary_bridge258']);files[1].write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
with files[2].open('a',encoding='utf-8') as f:f.write('\n2026-10-19 EV048：request257提取发现横向偏宽，保留未导入；request258以既有512格／头盔与脚位重新约束，已E636及有限审图，待提取／分层／轻甲适配／实机比较。内置请求258、窗口11用18余6，外部API0；正式完成口径不变。\n')
g['requests'][-1].update(status='raw_root_reviewed_numeric_extraction_pending_not_runtime',Root_raw_review=pin(review_path));g.setdefault('derived_deliveries',[]).append(dict(id='EV048-hero-primary-bridge258-raw-retained-limited-review-v001',utc=s['utc'],status=pin(O/'current-status.json'),image_generation_calls=1,external_API_calls=0,formal_complete_units=0,FinalAccepted=False));files[3].write_text(json.dumps(g,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
new(O/'status-sync-receipt.json',dict(status=pin(O/'current-status.json'),after=[pin(p) for p in files],backups_preserved=True,Source_Content_unchanged=True,FinalAccepted=False));print(json.dumps(pin(O/'current-status.json'),ensure_ascii=False))
