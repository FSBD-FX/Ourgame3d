"""Truthful in-progress checkpoint: imported sources are not a running-game result."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib,json,shutil
R=Path('F:/Ourgame');B=R/'source-assets/production/fairytale-hero-state-gap-v001'
O=R/'docs/production/first-batch-v2/evidence/hero-Death40-v001/root-import-and-source-review-v001'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def pin(p):return dict(path=p.as_posix(),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())
def save(p,j):
 assert not p.exists();p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
assert not O.exists();O.mkdir(parents=True)
p=R/'docs/production/first-batch-v2/progress.json';shutil.copy2(p,O/'progress-before.json')
rc=R/'UnrealGame/Saved/Bootstrap/hero-Death40-v001-import-20261018-101737-970622.json'
iv=B/'death-state-preparation-v001/Root-Death40-import-v001/independent-import-verification-20261018-101758-824520.json'
assert read(rc)['success'] and read(iv)['success'] and read(iv)['exact_total']==1326
df=B/'dodge-state-preparation-v001/Dodge32-native-ready-v001/Dodge32-native-ready-freeze-v001.json'
if not df.exists():
 df=next((B/'dodge-state-preparation-v001/Dodge32-native-ready-v001').glob('*freeze*.json'))
e=Path('E:/OurGame/Knight/过程图稿与视频/2026-10-18_钟盔Dodge32原身体与棕皮军剑原生准备候选_v001/source-size-SHA256.json')
assert read(e)['source_and_target_hash_mismatches']==0 and read(e)['verification_passes']==2
names=['Chest-standalone4-SOURCE1x.png','ShoulderNear-standalone4-SOURCE1x.png','ShoulderFar-standalone4-SOURCE1x.png']
viewed=[pin(R/'过程图稿与视频/2026-10-18_钟盔Dodge32原身体与棕皮军剑原生准备候选_v001/展示副本'/n) for n in names]
review=dict(utc=datetime.now(timezone.utc).isoformat(),Dodge_source_freeze=pin(df),E510_actual_retention=pin(e),
 actually_viewed_standalone_plates=viewed,source_preparation_only=True,
 comments='Three standalone rows are visible and nonempty. Tiny far shoulder is deliberate current identity. Joint/middle-frame geometry and protected-cell failures remain; only later finite native preparation permitted.',
 TrialAllowed=False,FinalAccepted=False,actual_imported=False,actual_native_verified=False)
save(O/'Dodge32-Root-after-E510-source-review-v001.json',review)
v=read(p);v.update(current_source_uncompiled_changes=True,ue_current_working_source_compiled=False,ue_current_working_source_verified=False,
 current_snapshot_pending='Hero Death40 imported exact1326. Stage0 RED/source implementation/build/full190/native both sides pending; v137 is historical Source246/Production1286.',
 current_hero_Death40_import=dict(receipt=pin(rc),independent=pin(iv),old1286_unchanged=True,new40_imported=True,current_production_files=1326,native_verified=False,formal_complete_units=0),
 current_Dodge32_native_preparation=dict(freeze=pin(df),retention=pin(e),source_review=pin(O/'Dodge32-Root-after-E510-source-review-v001.json'),actual_imported=False,actual_native_verified=False),
 next_E_retention_number=511)
p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
save(O/'import-status-v001.json',dict(import_receipt=pin(rc),independent_receipt=pin(iv),source_count_at_record=sum(q.is_file() for q in (R/'UnrealGame/Source').rglob('*')),production_files=1326,actual_compiled=False,actual_native=False,formal_complete_units=0))
print(json.dumps(dict(imported40=True,old1286_unchanged=True,total1326=True,Dodge32_E510_reviewed=True,new_generation_calls=0,compile_native_pending=True)))
