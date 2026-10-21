"""Continue v001 after exact-byte test check stopped on mixed CRLF from git apply."""
from pathlib import Path
import hashlib,json,os,shutil
R=Path('F:/Ourgame');B=R/'source-assets/production/stone-guard-feedback-v001/room-persistence-review-v001/owner-died-binding-v001'
P=R/'source-assets/production/stone-guard-room-reward-v001/room-native-proof-candidate-v001'
O=R/'docs/production/first-batch-v2/evidence/guard-room-v001/root-repair-proof-admission-v002'
OLD=O.with_name('root-repair-proof-admission-v001')
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def pin(p):
 b=p.read_bytes();return dict(path=p.as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
assert OLD.is_dir() and not O.exists();O.mkdir(parents=True)
for freeze in [B/'owner-died-binding-freeze-v001.json',P/'proof-candidate-freeze-v001.json']:
 for row in read(freeze)['files']:
  src=(B/row['path']) if not Path(row['path']).is_absolute() else Path(row['path'])
  assert src.stat().st_size==row['bytes'] and pin(src)['sha256']==row['sha256'],src
fixture=read(B/'fixture-admission-v002-pins.json');normalization=[]
for row in fixture['files']:
 dst=R/row['actual_source'];src=Path(row['candidate'])
 assert dst.read_text(encoding='utf-8-sig')==src.read_text(encoding='utf-8-sig'),'Only EOL normalization is authorized'
 before=pin(dst);shutil.copy2(dst,O/('before-normalization-'+dst.name))
 shutil.copy2(src,dst);os.utime(dst,None)
 assert dst.stat().st_size==row['after_bytes'] and pin(dst)['sha256']==row['after_sha256']
 normalization.append(dict(before=before,after=pin(dst),decoded_text_identical=True))
fighter=R/'UnrealGame/Source/CodexDungeon/DungeonFighter.cpp'
runtime=R/'UnrealGame/Source/CodexDungeon/DungeonFirstBatchGuardRoomRuntime.inl'
assert 'OriginalDeath->AtTime==D.Death.AtTime' in fighter.read_text(encoding='utf-8-sig')
assert 'Q.AtTime=E.AtTime;++DeathEvents;' in runtime.read_text(encoding='utf-8-sig')
for n in ['DungeonHUD.h','DungeonHUD.cpp']:
 assert 'RenderedNativeGuardEntityIds' in (R/'UnrealGame/Source/CodexDungeon'/n).read_text(encoding='utf-8-sig')
new=[]
for src in sorted((P/'new-source').iterdir()):
 if src.is_file():
  dst=R/'UnrealGame/Source/CodexDungeon'/src.name;assert not dst.exists();shutil.copy2(src,dst);os.utime(dst,None);assert src.read_bytes()==dst.read_bytes();new.append(pin(dst))
for name in ['capture-guard-room-native-flow-v001.ps1','verify-guard-room-native-flow-v001.py','prepare-guard-room-native-media-v001.py','launch-guard-room-native-trial-v001.ps1']:
 src=P/name;dst=R/'tools/scripts'/name;assert not dst.exists();shutil.copy2(src,dst);assert src.read_bytes()==dst.read_bytes();new.append(pin(dst))
source=[pin(p) for p in sorted((R/'UnrealGame/Source').rglob('*')) if p.is_file()]
record=dict(prior_partial_admission=str(OLD),diagnosis='Original git apply preserved CRLF on old lines; candidate test files use LF. Both decoded C++ texts were identical. Canonical frozen candidate bytes installed; no assertion/deadline change.',fixture_normalization=normalization,originalDiedFix=[pin(fighter),pin(runtime)],proof_new=new,actual_Source=source,actual_compile=None,actual176GREEN=None,native_proof=None,formal_complete_units=0)
(O/'admission.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
p=R/'docs/production/first-batch-v2/progress.json';s=read(p);s['guard_room_v001']['repair_proof_admission']=pin(O/'admission.json');s.update(goal_status='active',ue_current_working_source_compiled=False,ue_current_working_source_verified=False,current_source_uncompiled_changes='Original Died/reward exact binding, frozen legal fixtures v002 with decoded C++ unchanged after EOL canonicalization, and opt-in native flow proof. UBT/176GREEN/runtime pending.')
p.write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(fixture_decoded_text_identical=True,production_fix_files=2,new_source=2,new_tools=4,source_count=len(source),next='UBT then176 then native proof')))
