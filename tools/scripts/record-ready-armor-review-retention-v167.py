from pathlib import Path
import hashlib,json
R=Path('F:/Ourgame');E=Path('E:/OurGame/Knight/过程图稿与视频/2026-10-16-OurgameUE-ready-armor24-review-failure-errata-v167/source-size-SHA256.json')
receipt=json.loads(E.read_text(encoding='utf-8-sig'))
assert receipt['file_count']==92 and receipt['bytes']==4211142 and receipt['source_and_target_hash_mismatches']==0 and receipt['verification_passes']==2 and receipt['root_readme_unchanged']
p=R/'docs/production/first-batch-v2/progress.json';d=json.loads(p.read_text(encoding='utf-8-sig'))
d['current_turn_media_retention']['review_capsule']='E167_actual_verified'
d['current_turn_media_retention']['review_capsule_files']=92;d['current_turn_media_retention']['review_capsule_bytes']=4211142
d['current_status_authority']=['current_task','current_build','current_compiled_snapshot','latest_strict_UE_automation','latest_visual_runtime_proof','generation_accounting_current','next_native_request','next_snapshot','next_retention_batch']
d['version_suffixed_status_fields_are_historical']=True
p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
out=R/'docs/production/first-batch-v2/evidence/sword-armor-ready-v001/E167-retention-verified-v001.json';assert not out.exists()
out.write_text(json.dumps({'receipt_path':E.as_posix(),'receipt_sha256':hashlib.sha256(E.read_bytes()).hexdigest(),'file_count':92,'bytes':4211142,'two_size_SHA_passes':True,'mismatches':0,'E_root_README_unchanged':True,'retained_progress_records_pre_copy_pending_state':True,'working_progress_updated_after_actual_success':True},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
plan=R/'docs/superpowers/plans/2026-10-15-bound-run-capture-restore.md'
with plan.open('a',encoding='utf-8') as f:f.write('\n## EV048 Ready-only armor visible checkpoint — 2026-10-16\n\n- [x] Native158/159 revised body sources and161/162/163 separate chest/shoulders with exact source-body split; actual24 newtextures/old917 unchanged, no equipment-ID claim.\n- [x] Preserve v100/E164 actualfirst-usebody disappearance (3 of137Ready), add visible-pixel gate, startup24preload/targetedcompilewait/existingrenderflush.111349build0→111515full126GREEN, v1011399files/2798endpoints0diff, freshsameEnter/A/J5.80775s174obs175PNG/137Ready0visiblefail, nativeCRC/phase/stack/flush/decode; E165/E166/E167 retained, root and independent original-frame reviews.\n- [ ] Match armor/body partition to actual159 first-attack six phases; then fullstates, three-stage/four-armors/20mix, sounds and actual equipment binding. Current Ready-to-attack armor disappears; full silhouette/motion acceptance pending.\n- [ ] Complete codecs/disk semantic commits and new-process normal Continue. Bounded in-memory Prepare/Install is complete as earlier126 evidence; whole save plan remains open.\n')
print('E167 actual receipt checked; mutable working status and plan synchronized, historical frozen versions preserved')
