"""Root's performed bounded visual review; preserve and sync actual v143 facts."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, shutil, subprocess

R = Path('F:/Ourgame')
M = R / '过程图稿与视频'
EV = R / 'docs/production/first-batch-v2/evidence/HeroLandingPriority-v143-v001'
E = Path('E:/OurGame/Knight/过程图稿与视频')
def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def pin(p):
    p = Path(p).resolve(); b = p.read_bytes()
    return dict(path=p.as_posix(), bytes=len(b), sha256=hashlib.sha256(b).hexdigest())
def new(p, value):
    with Path(p).open('x', encoding='utf-8') as f:
        if isinstance(value, str): f.write(value)
        else: json.dump(value, f, ensure_ascii=False, indent=2); f.write('\n')

prior_path = EV / 'current298-GREEN-stable-fast142-status-v002/current-status.json'
prior = read(prior_path)
assert pin(prior['compiled_manifest']['path']) == prior['compiled_manifest']
ind_path = EV / 'Root-four-native-independent-v001/four-native-independent-verification-v001.json'
ind = read(ind_path)
assert ind['passed'] and len(ind['cases']) == 4
assert pin(ind_path)['sha256'] == '3e4bc7046a701d9cb7fedd1dd6778114ebb83ba075494356c17ef762675dbd11'
retentions = []
for n in range(617, 625):
    matches = list(E.glob(f'2026-10-19-本项目E{n}-*/E-retention-index-v001.json'))
    assert len(matches) == 1
    d = read(matches[0])
    assert d['verification_passes'] == 2 and d['kind'] == 'full' and d['full_source_member_retention'] and d['is_actual_E_retention']
    retentions.append(dict(batch=n, index=pin(matches[0]), files=d['file_count'], source_bytes=d['source_bytes'], packet=d['packet']))

cases = []; reviewed_images = []
for a, side in [('J', 'left'), ('J', 'right'), ('Shift', 'left'), ('Shift', 'right')]:
    archive = M / f'2026-10-19_钟盔落地{a}_{side}_v001'
    presentation = M / f'2026-10-19_钟盔落地{a}实录与接续_{side}_v001'
    runtime_path = archive / '原件/runtime-report.json'; r = read(runtime_path)
    index_path = presentation / '来源-版本-状态索引.json'; d = read(index_path); enc = d['presentation_encoding']
    prereg_path = archive / 'preregistration-v001.json'; prereg_pin = pin(prereg_path)
    verified = [x for x in ind['cases'] if Path(x['root_prereg_pin']['path']).resolve() == prereg_path.resolve() and (x['root_prereg_pin']['bytes'], x['root_prereg_pin']['sha256']) == (prereg_pin['bytes'], prereg_pin['sha256'])]
    assert len(verified) == 1 and verified[0]['native_PNG_FIFO_CRC_verified'] and r['passed'] and r['flow_complete']
    assert r['initial_hp'] == r['capture_final_hp'] == 100
    assert d['actual_action'] == a and d['actual_process_id'] == r['process_id']
    assert enc['full_AV_decoded'] is True and enc['frames_dropped_or_added'] is False
    assert enc['muxed_VFR']['decoded_frames'] == len(r['observations'])
    images = ['Air-Land-action-Ready-all-UNSCALED-crops-v001.png', f'JOIN-previous_callback_to_first_{a}-UNSCALED-crops-v001.png', f'JOIN-last_{a}_to_first_Ready-UNSCALED-crops-v001.png']
    reviewed_images.extend(pin(presentation / '展示副本' / name) for name in images)
    cases.append(dict(action=a, facing=r['requested_facing'], process_id=r['process_id'], native_callbacks=len(r['observations']), runtime=pin(runtime_path), media_index=pin(index_path), video=enc['video'], native_independent=verified[0], boundaries=d['callback_boundaries'], initial_hp=100, final_hp=100))
reviewed_images.append(pin(M / '2026-10-19_钟盔落地J_right_v001/原件/MovieFrame00159.png'))
assert len(reviewed_images) == 13 and sum(c['native_callbacks'] for c in cases) == 763

out = M / '2026-10-19_钟盔落地动作四案有限审阅_v001'
out.mkdir(); (out / '原件').mkdir(); (out / '展示副本').mkdir()
report = dict(schema='Root-hero-landing-four-limited-visual-review-v001', utc=datetime.now(timezone.utc).isoformat(), actual_source_files=298, actual_production_files=1419, compiled_manifest=prior['compiled_manifest'], independent_four_case_proof=pin(ind_path), cases=cases, reviewed_images=reviewed_images, original_and_presentation_E_retention_before_View=retentions,
    performed_scope='Root viewed four all-pose unscaled boards, eight actual adjacent start/end boards, and one full native viewport. Native all763 PNGs/CRC/FIFO/source geometry and pixels/mainmix independently checked; all763 movie frames and complete AV decoded.',
    facts=['Both facing cases retain small helmet/leather/sword identities; no missing armor layer observed in reviewed images.', 'Full viewport retains hidden HUD/range debug and the small character scale.', 'All four native runs keep HP100 and return Ready; J six poses and Dodge four poses are present.'],
    visual_refinement_open=['Land4 crouch to Primary0 or Dodge0 has a visible abrupt rise; acceptance of trigger timing does not close pose continuity.', 'Primary1 torso/shoulder silhouette changes are modest in the sampled six poses; anticipation and impact strength remain for temporal/art refinement.', 'Dodge and Ready helmet/shoulder volume changes need further consistency review.', 'Earlier firstRise/Ready, Apex hem/knee and Land4/Land5 refinement remains open.'],
    limited_visual_review_performed=True, full_realtime_playback_reviewed=False, audio_listened=False, final_art_accepted=False, actual_disk_restore='OPEN_v144_new_candidate_only', formal_complete_units=0, completed_combinations=0, FinalAccepted=False)
report_path = out / '原件/Root-limited-review-v001.json'; new(report_path, report)
shutil.copy2(report_path, out / '展示副本/Root-limited-review-v001.json')
for p in (ind_path, R / '.superpowers/sdd/2026-10-19-hero-landing-priority-v143/task-2-scoped-review-fix1-v001.md', R / '.superpowers/sdd/2026-10-19-hero-landing-priority-v143/media-scoped-review-v001.md'):
    shutil.copy2(p, out / '原件' / p.name)
new(out / 'README.md', '四案运行与有限画面审阅记录。全763帧结构／资源／像素／原混音核验通过；实际看13张审阅图，原速完整播放和听感未完成。落地起身及轮廓精修仍OPEN，正式内容0/15、搭配0/20。原视频与原PNG已经E617–624完整双SHA保全；本记录另行E保全。\n')
new(out / '来源-版本-状态索引.json', dict(schema='Root-landing-review-source-version-status-v001', report=pin(report_path), files=[pin(p) for p in sorted(out.rglob('*')) if p.is_file()], final_art_accepted=False, FinalAccepted=False))
retainer = R / 'source-assets/production/fairytale-hero-air-v001/native-retention-solid-candidate-v001/retain-native-media-lossless-solid-tar-xz-v001.py'
batch = '2026-10-19-本项目E625-钟盔落地四案有限审阅-v001'
subprocess.run([str(R/'tools/runtime/asset-gen/Scripts/python.exe'), '-B', '-X', 'utf8', str(retainer), '--source', str(out), '--batch', batch, '--preset', '3'], check=True)
review_E = E / batch / 'E-retention-index-v001.json'; assert read(review_E)['verification_passes'] == 2

status_dir = EV / 'current298-GREEN-four-native-reviewed-status-v003'
status_dir.mkdir(); (status_dir / 'before').mkdir()
s = dict(prior)
s.update(schema='Root-current-landing-four-native-reviewed-v143-status-v003', utc=report['utc'], prior_status_pin=pin(prior_path), native_landing_J_Shift='PASS_four_fresh_native_cases_and_limited_keyframe_review; pose_polish_and_full_playback_listening_OPEN', native_four_case_proof=pin(ind_path), native_frames_total=763, limited_root_visual_review=pin(report_path), limited_root_review_E=pin(review_E), native_and_media_E_retention=retentions, last_E_batch=625, next_E_batch=626, next_task='v144 source-save/true-pristine-target real-disk Air Apex restore; NEW protocol/source/checker candidates only', v144_spec=pin(R/'docs/superpowers/specs/2026-10-19-hero-air-disk-restore-v144.md'), actual_v144_native_verified=False)
new(status_dir/'current-status.json', s)
files=[R/'README.md', R/'docs/production/first-batch-v2/progress.json', R/'项目需求台账.md', R/'source-assets/production/first-unit-animation-v003/generation-ledger.json']
for p in files:
    dest=status_dir/'before'/p.relative_to(R); dest.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(p,dest)
text=files[0].read_text(encoding='utf-8-sig'); _,rest=text.split('\n\n',1)
head='2026-10-19 当前进行中（EV048，v143）：左右落地接攻击／闪避四个真实进程已完成，763个原生回调，独立资源／像素／PNG／混音及完整视频解码通过；E617–625完整保全。Root审4张全姿态板、8处真实相邻接续和1张全景，落地起身偏硬、闪避／待机盔甲体积及攻击力量感仍待精修。开发Source298／Production1419，真实D3D11完整203项严格通过。[快捷试玩](钟盔轻甲快捷试玩.cmd)保留独立v142（完整启动校验约5.8秒）；[当前状态](docs/production/first-batch-v2/evidence/HeroLandingPriority-v143-v001/current298-GREEN-four-native-reviewed-status-v003/current-status.json)。下一项v144验证空中顶点存盘后新进程真正pristine恢复，候选准备中、尚未实录。完整原速播放／试听、动作精修仍OPEN，正式0/15、搭配0/20；目标active。本轮无生成，256／窗口11用16余8、外部API0。'
files[0].write_text(head+'\n\n'+rest,encoding='utf-8')
q=read(files[1]); q.update(current_status_authority=pin(status_dir/'current-status.json'), current_task=s['next_task'], current_v143_four_native_proof=pin(ind_path), current_v143_limited_visual_review=pin(report_path)); files[1].write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
with files[2].open('a',encoding='utf-8') as f:f.write('\n2026-10-19 EV048：落地接普通攻击／闪避左右四案实际通过，763原生帧与完整AV解码，13张有限画面审阅，E617–625双SHA保全；落地起身偏硬与动作轮廓变化仍待精修，原速完整播放／试听未完成，不计完整内容单元。v144新双进程顶点磁盘恢复候选开始准备，无新增图像调用。\n')
g=read(files[3]); g.setdefault('derived_deliveries',[]).append(dict(id='EV048-v143-four-native-landing-limited-review-v001', utc=s['utc'], native_proof=pin(ind_path), limited_review=pin(report_path), current_status=pin(status_dir/'current-status.json'), image_generation_calls=0, external_API_calls=0, formal_complete_units=0, FinalAccepted=False)); files[3].write_text(json.dumps(g,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
new(status_dir/'status-sync-receipt.json', dict(status=pin(status_dir/'current-status.json'), after=[pin(p) for p in files], before_backups_preserved=True, Source_Content_unchanged=True, FinalAccepted=False))
with (R/'.superpowers/sdd/2026-10-19-hero-landing-priority-v143/progress.md').open('a',encoding='utf-8') as f:f.write('\nTask3 bounded proof COMPLETE: four independent fresh PID cases/all763 native PNG and full AV/source pixels/mix PASS, E617–625 retained, Root13 performed images. Actual Source298/1419/CM5ddd unchanged. Formal art/units/full realtime/listening remain OPEN. v144 NEW source/protocol/checker work started, no actual v144 integration.\n')
print(json.dumps(dict(status=pin(status_dir/'current-status.json'), review=pin(report_path), review_E=pin(review_E), videos=[c['video'] for c in cases], last_E=625, next_E=626, FinalAccepted=False),ensure_ascii=False))
