"""Record actual190, both native Death5 trials, visible review and playable entry."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,shutil
R=Path('F:/Ourgame');E=Path('E:/OurGame/Knight/过程图稿与视频');B=R/'source-assets/production/fairytale-hero-state-gap-v001/death-state-preparation-v001'
O=R/'docs/production/first-batch-v2/evidence/hero-Death40-v001/root-checkpoint-v138-v001'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def pin(p):return dict(path=p.as_posix(),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())
sm=R/'source-assets/production/backups/v138-HeroDeath190G/compiled-source-manifest.json';s=read(sm)
assert s['strict_registered_tests']==190 and s['source_files']==257 and s['production_files']==1326 and s['source_hash_mismatches']==0
report=R/s['full_suite']['path'];q=read(report);assert q['succeeded']==190 and all(q[k]==0 for k in ['failed','succeededWithWarnings','notRun','inProcess'])
manual=R/'docs/production/first-batch-v2/evidence/hero-Death40-v001/root-manual-adoption-v138-v001/adoption-receipt-v001.json';assert read(manual)['ValidateOnly_exit_code']==0
browser=R/'过程图稿与视频/2026-10-18_钟盔倒地实录播放审阅_v001/index.json';assert read(browser)['full_playbacks_observed']
retention=[E/'2026-10-18_钟盔Dodge32原身体与棕皮军剑原生准备候选_v001/source-size-SHA256.json',
 E/'2026-10-18-OurgameUE-HeroDeath-left-native-v511/E-retention-index-v001.json',
 E/'2026-10-18-OurgameUE-HeroDeath-right-native-v512/E-retention-index-v001.json',
 E/'2026-10-18-OurgameUE-HeroDeath-visible-review-v513/source-size-SHA256.json',
 E/'2026-10-18-OurgameUE-HeroDeath-browser-review-v514/source-size-SHA256.json']
for p in retention:
 j=read(p);assert j['verification_passes']==2 and (j.get('source_and_target_hash_mismatches',j.get('source_and_member_hash_mismatches'))==0)
native=[]
for side,expected in [('left',803),('right',831)]:
 d=R/('过程图稿与视频/2026-10-18_钟盔真实守卫自然致死Death五相试样_native_'+side+'_v001')
 index=read(d/'index.json');r=read(d/'原件/runtime-report.json');assert index['independent_passed'] and r['passed'] and len(r['observations'])==expected
 receipts=list((d/'原件').glob('*independent*.json'));assert len(receipts)==1
 v=read(receipts[0]);assert v['passed'] and v['native_Death_frames']==[0,1,2,3,4] and v['actual41resident_and9slots_verified']
 native.append(dict(side=side,observations=expected,index=pin(d/'index.json'),runtime=pin(d/'原件/runtime-report.json'),
  independent=pin(receipts[0]),actual_guard_hits=v['actual_guard_committed_hits'],Death_draws=v['native_Death_draws'],
  hold_callbacks=v['actual_hold_callbacks'],terminal_max_age=v['real_terminal_max_age'],
  video=pin(R/('过程图稿与视频/2026-10-18_钟盔倒地五相左右实录审阅_v001/'+side+'/展示副本/hero-Death5-native-DIAGNOSTIC-silent-v001.mp4'))))
assert not O.exists();O.mkdir(parents=True)
for name in ['README.md','项目需求台账.md','docs/production/first-batch-v2/progress.json']:
 p=R/name;shutil.copy2(p,O/(p.name+'.before'))
viewed=[]
for side in ['left','right']:
 for name in ['Death5-NATIVE-PIXEL-CROP-contact-v001.png','JOIN-LiveReadyStack-to-Death0-native-unscaled-pair-v001.png']:
  viewed.append(pin(R/('过程图稿与视频/2026-10-18_钟盔倒地五相左右实录审阅_v001/'+side+'/展示副本/'+name)))
 viewed.append(pin(R/('过程图稿与视频/2026-10-18_钟盔倒地实录播放审阅_v001/展示副本/'+side+'-ended.png')))
review=dict(schema='Root-HeroDeath-v138-actual-native-and-visible-review-v001',utc=datetime.now(timezone.utc).isoformat(),
 snapshot=pin(sm),strict190=True,Source=257,Production=1326,native=native,retention=[pin(p) for p in retention],
 actually_viewed=viewed,both_full_playbacks=pin(browser),manual_adoption=pin(manual),
 limited_SWD_LGT_Death_state_native_reviewed=True,full_unit_accepted=False,
 visible_findings=['Player fivephase fall/armor retention and finalhold are readable at current small scale.',
 'Both literal adjacent Ready-stack to Death0 transitions show Guard switching from accepted art to gray Stomp geometric placeholder; this is a visible enemy art gap and next priority.',
 'Source floor/contact/socket are author positions, not measured physics. Blade can be partially occluded by Guard.',
 'Source phase joins/footlock and all other equipment/state combinations remain incomplete. Audio is absent from proof videos.'],
 baseline_Ready_DTO_and_DrawId_recorded=False,diagnostic_predecessor_Knight_Bat=True,hero_or_Guard_public_damage=False,
 formal_complete_units=0,complete_equipment_combinations=0,goal_status='active',FinalAccepted=False)
rp=O/'actual-native-and-visible-review-v001.json';rp.write_text(json.dumps(review,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
p=R/'docs/production/first-batch-v2/progress.json';j=read(p)
j['previous_checkpoint_before_HeroDeath_v138']={k:j.get(k) for k in ['current_task','current_build','current_compiled_snapshot','current_status_authority','current_hero_Dodge_Death_equipment_sources']}
j.update(current_task='SWD/LGT Death五相实际接入与两侧自然Guard致死已验，完整190GREEN；优先修Guard跺击/Move视觉缺口，再推进Dodge接合与其它搭配',
 current_build='UnrealGame/Saved/Bootstrap/build-editor-20261018-183547.log',current_build_exit_code=0,
 latest_build_attempt='UnrealGame/Saved/Bootstrap/build-editor-20261018-183547.log',latest_build_attempt_exit_code=0,
 current_compiled_snapshot='source-assets/production/backups/v138-HeroDeath190G',current_compiled_snapshot_files=len(s['files']),
 current_compiled_snapshot_bytes=sum(x['bytes'] for x in s['files']),current_production_packages=1326,
 actual_registered_test_count_current=190,ue_current_working_source_compiled=True,ue_current_working_source_verified=True,current_source_uncompiled_changes=False,current_snapshot_pending=None,
 current_status_authority='v138 actual strict190 GREEN/Source257/Production1326/2047inputpins; both real naturalGuard lethal trials, Death5/41resident/9slots/terminal hold/read-only inventory verified; fivephase/join/completevideos Root-reviewed. Guard Stomp still geometric placeholder. Fullunit0/15, combos0/20; active.',
 latest_strict_UE_automation=dict(report=pin(report),succeeded=190,failed=0,warnings=0,notRun=0,inProcess=0,actual_registry=190,scope='Actual v138 full registry includes unchanged3 RED tests now GREEN'),
 current_hero_Death_runtime_v138=review,current_manual_launcher_v009=pin(manual),current_guard_room_manual_trial=pin(manual),
 latest_visual_runtime_proof=pin(rp),latest_native_review_browser_playback=pin(browser),
 next_E_retention_number=515,next_retention_batch='E515',next_media_retention_batch='E515',next_turn_priorities=['Guard跺击/Move真实动作，消除实景几何占位突变','Dodge32源接合与原生完整装备回接','其余19搭配与首批剩余单位、完整VFX/SFX验收'],
 next_work=['Guard跺击/Move真实动作，消除实景几何占位突变','Dodge32源接合与原生完整装备回接','其余19搭配与首批剩余单位、完整VFX/SFX验收'])
existing=j.get('current_retention_batches',[]);known={x['path'] for x in existing}
j['current_retention_batches']=existing+[pin(p) for p in retention if p.as_posix() not in known]
j['current_turn_media_retention']=j['current_retention_batches'];j['current_turn_media_retained']=True
j['current_hero_Death40_import']['native_verified']=True
j['current_hero_Dodge_Death_equipment_sources']['Death40_actual_imported']=True
j['current_hero_Dodge_Death_equipment_sources']['Death5_actual_native_and_Root_reviewed']=True
j['current_hero_Dodge_Death_equipment_sources']['Dodge32_actual_imported']=False
j['current_hero_Dodge_Death_equipment_sources']['FinalAccepted']=False
j['current_source_verification_scope']='Actual current257Source/1326Production exactset and DLL/full190 snapshot; current v009 complete manual twoSHA checks; separate Root native/visual receipt. Historical versioned fields retain their original scopes.'
p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(checkpoint='v138-HeroDeath190G',Source=257,Production=1326,strict190=True,observations=[803,831],both_full_videos_reviewed=True,E_last=514,formal_complete_units=0,goal='active')))
