"""Checkpoint actual captures/imports; retain failed attempts and scope limits."""
from pathlib import Path
from datetime import datetime,timezone
import json

root=Path('F:/Ourgame')
p=root/'docs/production/first-batch-v2/progress.json'
j=json.loads(p.read_text(encoding='utf-8-sig'))
j['updated_utc']=datetime.now(timezone.utc).isoformat()
j['current_compiled_snapshot']='source-assets/production/backups/2026-10-15_walk66imported-same83DLL-v046'
j['current_build']='UnrealGame/Saved/Bootstrap/build-editor-20261015-160925.log'
j['current_build_exit_code']=0
j['latest_strict_UE_automation']=dict(report='UnrealGame/Saved/Automation/FirstRoom-20261015-161022/index.json',registered=83,succeeded=83,failed=0,notRun=0,warnings=0,status='Actual83GREEN; v00429/capturepassed but equipment-hold visualP2 found; current HUD correction awaiting new build/test/capture')
j['ue_current_working_source_verified']=False
j['current_source_uncompiled_changes']=['DungeonHUD.cpp: native XBW supportedReady equipment hold and no generic sword fallback; new build pending']
j['production_texture_count_actual']=831
j['production_texture_count_scope']='Actual T_*.uasset files: FirstBatch826 + RoomArt3 + SceneExploration2 =831; complete Production850 includes17 SW_ audio and2 M_ material packages. Historical/current both retained.'
j['production_uasset_package_count_actual']=850
j['current_task']='EV042 visual scale/fog/roundhelmet preserved; four-armor29v004 and full1825pixelcapture passed, actual23unique frames reveal equipment white-sword P2 now under minimalHUD correction; new0.96walk66 imported/saved, Actor/HUDwalk not wired, formal0/15.'
w=j['xbw_walk_pending']
w.update(actual_UE_imported=True,imported=True,imported_version='common-walk-v002/armor-walk-v002, uniform0.96',
         uniform_096_revision_status='ActualUE imported/saved body18+armor48 with fresh exact registry receipts; actual source preflight842refs/66RGBA/18gates; runtime not wired',
         actual_body_import_receipt='UnrealGame/Saved/Bootstrap/xbw-walk-v002-import-20261015-081700-258216.json',
         actual_armor_import_receipt='UnrealGame/Saved/Bootstrap/xbw-armor-walk-v002-import-20261015-081825-243347.json',
         actual_body_imported=18,actual_body_saved=18,actual_armor_imported=48,actual_armor_saved=48,
         registry_exact_set_passed=True,runtime_grip_verified=False,four_armor_runtime_verified=False,
         legacy_v001_fields_scope='common_manifest/sha256/armor_manifest/old neutral failure and58reference fields refer to preserved unimported0.94 candidate; new imports exclusively use explicit v002 fields')
for clip in j['xbw_armor_layers'].values():
    clip['runtime_verified']=True
    clip['runtime_scope']='v004 normal29 exact six stacks/bothfacings; limited actual visual samples, not full clothes/mechanical/all-state acceptance; equipment-hold P2 tracked separately'
f=j['xbw_four_armor_runtime']
f.update(status='v004 normal29+native1825CRC/FIFO/reserved/drain/audio-sync passed, actual23unique viewed; equipment-hold white-sword P2 requires new corrected capture',
         compiled_snapshot='source-assets/production/backups/2026-10-15_asyncReserved-UE83-GREEN-v045',
         formal_four_armor_complete=False,visual_review_unique_originals=23,
         visual_review='docs/production/first-batch-v2/xbw-four-armor-visual-review-v004.md',
         equipment_hold_regression_verified=False,
         equipment_hold_actual_RED='docs/production/first-batch-v2/evidence/xbw-equipment-hold-v001/actual-v004-RED.json')
assert not any(t['version']=='v004' for t in f['attempts'])
f['attempts'].append(dict(version='v004',archive='过程图稿与视频/2026-10-15_猎弩四甲双向射击装填实际换装运行_v004',
                         whole_passed=False,normal_profile_passed=True,required=29,executed=29,passed=29,
                         movie_frames=1824,native_PNGs_CRC_verified=1825,audio_sync_passed=True,
                         capture_complete=True,actual_shots=8,reload_commits=8,global_retry_shots_used=0,
                         actual_viewed_unique_PNGs=23,equipment_hold_visual_P2=True,
                         E_batch='2026-10-15-OurgameUE-四甲双向射击装填29项-v034',
                         retention_status='F/E actual1839files6770389176B twoSHA0'))
j['async_capture_pipeline'].update(status='Actualv004 exact1824movie/prewarm1 CRC/unique/reservation/FIFO/drain passed after CREATE_NEW repair; v003 overwrite failure preserved',
                                   actual29_verified=True,actual83_verified=True,actual_performance_verified=False,
                                   actual_verified_movie_frames=1824,actual_verified_original_PNGs=1825,
                                   peak_pending_BGRA_bytes=195379200,peak_pending_jobs=53,
                                   scope='Native pixel/capture integrity only; no full-process memory or performance benchmark claim')
j['next_work']=['Finish actual HUD equipment-hold P2 regression without changing29/55/global2; preserve v004 diagnosis.',
                'Wire imported0.96 XBWwalk Actor/HUD using each -1/0/3 matrix and real movement/animation clock; actual newRED thenGREEN/runtime and footlock/coverage checks.',
                'Continue5weapons/4armor/5ordinary/Boss allstates/audio/VFX/20mix/formal acquisition/drop/aux15/D13; formal0/15.']
p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Progress checkpoint v046: capture29 passed with visible P2; walk66 imported; correctedHUD verification pending; formal0/15.')
