from pathlib import Path
import datetime,hashlib,json,re,shutil,subprocess
R=Path('F:/Ourgame');S=R/'UnrealGame/Source/CodexDungeon'
C=R/'docs/production/first-batch-v2/evidence/fairytale-equipment-bound-native-plan-v001'
O=R/'docs/production/first-batch-v2/evidence/equipment-bound-execution-v001/probe-root-admission-v001'
assert not O.exists()
def desc(p):
 b=p.read_bytes();return dict(path=p.as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
freeze=C/'native-plan-freeze-v001.json'
assert desc(freeze)['sha256']=='9c726dc46813bde9a7463f9b6c96156a0bfc66e3049fb0cf156dac243dbd147b'
v=json.loads(freeze.read_text(encoding='utf-8'))
for row in v['files']:
 p=Path(row['path']);p=p if p.is_absolute() else C/p
 got=desc(p);assert got['bytes']==row['bytes'] and got['sha256']==row['sha256']
assert desc(S/'DungeonHUD.cpp')['sha256']=='b938adc86036a5a8693ac0799d0dd32645e513ce52cb60ff2078a69731bfc39f'
for name in ['DungeonFairytaleEquipmentBoundProbe.h','DungeonFairytaleEquipmentBoundProbe.cpp']:assert not (S/name).exists()
patch=C/'patch/add-native-probe-plus-HUD-hook-v001.patch'
assert desc(patch)['sha256']=='065113dcddd672aa826a80739e67fc431c2908b89daf5559c378700e73cfc600'
allowed={'UnrealGame/Source/CodexDungeon/'+n for n in ['DungeonHUD.cpp','DungeonFairytaleEquipmentBoundProbe.h','DungeonFairytaleEquipmentBoundProbe.cpp']}
assert set(re.findall(r'^\+\+\+ b/(.+)$',patch.read_text(encoding='utf-8'),re.M))==allowed
check=subprocess.run(['git','apply','--check','--ignore-space-change',str(patch)],cwd=R,text=True,capture_output=True)
assert check.returncode==0,check.stderr
correction=C/'correction-v002';cf=correction/'correction-freeze-v002.json'
assert desc(cf)['sha256']=='26e32f1e25e3b8be197d2957536102380055ecc1774135e3b87c6f6aafc2683b'
for row in json.loads(cf.read_text(encoding='utf-8'))['files']:
 got=desc(correction/row['path']);assert got['bytes']==row['bytes'] and got['sha256']==row['sha256']
fixed=correction/'DungeonFairytaleEquipmentBoundProbe.cpp';ft=fixed.read_text(encoding='utf-8')
base=(C/'candidate-source/DungeonFairytaleEquipmentBoundProbe.cpp').read_text(encoding='utf-8')
old='FMath::IsNearlyEqual(D.CanvasSize,72.,1.e-9)';assert base.count(old)==1
expected=base.replace('#include "DungeonFairytaleSwordEquipmentBinding.h"','#include "DungeonFairytaleSwordEquipmentBinding.h"\n#include "DungeonFairytaleSwordBodyV001.inl"').replace(old,'FMath::IsNearlyEqual(D.CanvasSize,DungeonFairytaleSwordBodyV001::CanvasSize,1.e-9)').replace('72px_UIoff_contract_changed','source_canvas_or_UIoff_contract_changed')
field='    R->SetNumberField(TEXT("body_max_contract"),72.);\n'
assert ft.count(field)==1 and ft.replace(field,'')==expected
(O/'before').mkdir(parents=True);shutil.copy2(S/'DungeonHUD.cpp',O/'before/DungeonHUD.cpp');shutil.copy2(freeze,O/freeze.name)
apply=subprocess.run(['git','apply','--ignore-space-change',str(patch)],cwd=R,text=True,capture_output=True)
assert apply.returncode==0,apply.stderr
cpp=S/'DungeonFairytaleEquipmentBoundProbe.cpp';original=cpp.read_bytes();(O/'probe-before-canvas-oracle-correction.cpp').write_bytes(original)
t=original.decode('utf-8');old='FMath::IsNearlyEqual(D.CanvasSize,72.,1.e-9)'
assert t.count(old)==1 and t.count('#include "DungeonFairytaleSwordEquipmentBinding.h"')==1
assert t.replace('\r\n','\n')==base
shutil.copy2(fixed,cpp);shutil.copy2(cf,O/cf.name)
after=[desc(S/name) for name in ['DungeonHUD.cpp','DungeonFairytaleEquipmentBoundProbe.h','DungeonFairytaleEquipmentBoundProbe.cpp']]
receipt=dict(time=datetime.datetime.now(datetime.timezone.utc).isoformat(),candidate_freeze=desc(freeze),actual_small_patch=desc(patch),actual_patch_exit=apply.returncode,after=after,Root_oracle_correction='D.CanvasSize equals 72*512/416=88.61538461538461, not content-height72; independently verified actual v116 native observations. Actual rendering size unchanged.',production_renderer_consumer_applied=False,axis_V002_applied=False,compiled=False,native_run=False,formal_complete_units=0)
(O/'admission.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
p=R/'docs/production/first-batch-v2/progress.json';shutil.copy2(p,O/'before/progress.json');m=json.loads(p.read_text(encoding='utf-8'))
m['current_task']='EV048 actual nativeBound QA probe admitted on old v116 renderer for meaningful RED; no consumer/axis yet. Source changed, build/native pending.'
m['ue_current_working_source_compiled']=False;m['ue_current_working_source_verified']=False;m['current_source_uncompiled_changes']=[x['path'] for x in after]
m['next_retention_batch']='E243';m['current_retention_batches']=list(dict.fromkeys(m['current_retention_batches']+['E242']))
m['current_turn_progress_classification']='progress: current audio/source audits, actual lossless format retention, now3Source probe admission; actual build/native RED pending.'
m['goal_status']='active';m['completed_content_units']=0;m['updated_utc']=receipt['time']
p.write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(receipt,ensure_ascii=False))
