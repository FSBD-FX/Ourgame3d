from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,re
HERE=Path(__file__).resolve().parent;ROOT=Path('F:/Ourgame')
def pin(p):
 p=Path(p).resolve();b=p.read_bytes();return {'path':p.as_posix(),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(name,v):
 with (HERE/name).open('x',encoding='utf-8') as f:json.dump(v,f,ensure_ascii=False,indent=2);f.write('\n')
j=read(HERE/'exact-seams-v001.json');rel=j['path'];before=(HERE/'before'/rel).read_bytes();after=(HERE/'projected'/rel).read_bytes()
assert len(before)==j['before']['bytes'] and hashlib.sha256(before).hexdigest()==j['before']['sha256']
assert len(after)==j['after']['bytes'] and hashlib.sha256(after).hexdigest()==j['after']['sha256']
actual=(ROOT/rel).read_bytes();assert actual==before,'Actual source changed before Root admission'
composed=before
for op in j['operations']:
 a=op['anchor'].encode();x=op['addition'].encode();assert composed.count(a)==1
 composed=composed.replace(a,x+a if op['kind']=='insert_before' else a+x if op['kind']=='insert_after' else x,1)
assert composed==after
inverse=after
for op in reversed(j['operations']):
 a=op['anchor'].encode();x=op['addition'].encode();r=x+a if op['kind']=='insert_before' else a+x if op['kind']=='insert_after' else x
 assert inverse.count(r)==1;inverse=inverse.replace(r,a,1)
assert inverse==before
assert re.findall(rb'"CodexDungeon\.[^"\r\n]+"',before)==re.findall(rb'"CodexDungeon\.[^"\r\n]+"',after)
assert (HERE/'evidence/failed-index-062104.json').read_bytes()==(ROOT/'UnrealGame/Saved/Automation/FirstRoomNativeRHI-20261019-062104/index.json').read_bytes()
assert 'checks=50 failures=0' in (HERE/'evidence/real-event-order-host-v001.txt').read_text(encoding='utf-8-sig')
deps=[ROOT/rel,ROOT/'UnrealGame/Saved/Automation/FirstRoomNativeRHI-20261019-062104/index.json',ROOT/'UnrealGame/Saved/Bootstrap/build-editor-20261019-061304.log']
for name in ['DungeonActionAudioFeedback.h','DungeonWorldProjectiles.cpp','DungeonHUD.cpp','DungeonHUD.h','DungeonFighter.h','DungeonGameMode.h','DungeonGameMode.cpp','DungeonWeaponActions.h','DungeonContentCombat.h','DungeonWorldProjectiles.h']:
 deps.append(ROOT/'UnrealGame/Source/CodexDungeon'/name)
dependency_pins=[pin(p) for p in deps]
write('evidence/final-projection-check-v001.json',{'schema':'forward-step-regression-projection-check-v001','utc':datetime.now(timezone.utc).isoformat(),'five_exact_seams':True,'inverse_roundtrip_all_old_bytes':True,'original_test_source_unchanged':True,'existing_source_test_IDs_unchanged':True,'original203_report_saved_exact':True,'real_portable_kernel_host_checks':50,'real_portable_kernel_host_failures':0,'projected_UE_build_run':False,'projected_UE_test_run':False,'native_run':False,'FinalAccepted':False})
members=[pin(p) for p in sorted(HERE.rglob('*')) if p.is_file() and p.name!='candidate-freeze-v001.json']
for _ in range(2):
 for r in members+dependency_pins:assert pin(r['path'])==r
write('candidate-freeze-v001.json',{'schema':'forward-step-regression-test-source-candidate-freeze-v001','members':members,'dependency_pins':dependency_pins,'verification_passes':2,'twoSHA_mismatches':0,'modified_existing_source_files_if_admitted':1,'new_Unreal_source_files':0,'new_Unreal_test_IDs':0,'preserved_existing_suite_test_IDs':203,'preserved_existing_melee_test_IDs':3,'projected_UE_build_run':False,'projected_UE_test_run':False,'native_run':False,'RootApproved':False,'FinalAccepted':False})
print(json.dumps({'freeze':pin(HERE/'candidate-freeze-v001.json'),'projected':pin(HERE/'projected'/rel),'handoff':pin(HERE/'HANDOFF-v001.md'),'member_count':len(members),'dependency_count':len(dependency_pins),'twoSHA_mismatches':0,'actual_source_unchanged':True,'UE_native_run':False}))
