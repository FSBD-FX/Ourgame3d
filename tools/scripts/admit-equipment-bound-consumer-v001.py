from pathlib import Path
import datetime,hashlib,json,shutil,subprocess
R=Path('F:/Ourgame');S=R/'UnrealGame/Source/CodexDungeon'
C=R/'source-assets/production/fairytale-sword-equipment-binding-v001/consumption-v001'
AX=R/'source-assets/production/fairytale-sword-primary3-clearance-v002'
O=R/'docs/production/first-batch-v2/evidence/equipment-bound-execution-v001/consumer-root-admission-v001';assert not O.exists()
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def desc(p):
 b=p.read_bytes();return dict(path=p.as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def verify(family,freeze,sha):
 assert desc(freeze)['sha256']==sha
 for row in read(freeze)['files']:
  p=Path(row['path']);p=p if p.is_absolute() else family/p;d=desc(p)
  assert d['bytes']==row['bytes'] and d['sha256']==row['sha256'],p
cf=C/'consumption-freeze-v001.json';af=AX/'candidate-freeze-v002.json'
verify(C,cf,'6be890d49e229c56b138dc5982eaf6c2eb8f1e70b6610e7870fb7df4425731fb')
verify(AX,af,'ca3326759de1d15f5ba7356687527a8259dd194d983973d1c327d8fe98876f97')
for row in read(C/'baseline-pins-current-P3-v001.json')['source_inputs']:
 p=Path(row['path']);d=desc(p)
 if p.name=='DungeonHUD.cpp':assert d['sha256']=='4408906f11c8d398f60dcbe03bec3f6ba048891f2fb16e7b0a00444567032252'
 else:assert d['bytes']==row['bytes'] and d['sha256']==row['sha256'],p
red=R/'过程图稿与视频/2026-10-16_军剑真实换装绑定_v001-RED'
rv=read(red/'原件/runtime-report.json');assert rv['flow_complete'] and not rv['passed'] and rv['reason']=='' and len(rv['mismatches'])==6
retention=Path('E:/OurGame/Knight/过程图稿与视频/2026-10-16-OurgameUE-equipment-bound-nativeRED-v243/retention-verification-v001.json')
ev=read(retention);assert ev['verification_passes']==2 and ev['source_and_retained_size_SHA_mismatches']==0 and ev['packed_native_pngs']==142
patch=C/'patch/bound-current-P3-consumption-v001.patch'
check=subprocess.run(['git','apply','--check','--ignore-space-change',str(patch)],cwd=R,text=True,capture_output=True);assert check.returncode==0,check.stderr
axis=AX/'DungeonFairytaleSwordPrimary3V002.inl';assert desc(axis)['sha256']=='25f09a54d1852cc6f5218a926c3ca39b9225bdf667bfd1da496eb50c194d0719'
assert not (S/axis.name).exists()
names=['DungeonHUD.h','DungeonHUD.cpp','DungeonFairytaleSwordPresentation.cpp','DungeonFairytaleSwordDrawState.h','DungeonFairytaleSwordProbe.cpp']
probe_names=['DungeonFairytaleEquipmentBoundProbe.h','DungeonFairytaleEquipmentBoundProbe.cpp']
probe_before={n:desc(S/n) for n in probe_names};old_tick=(S/'DungeonFairytaleSwordProbe.cpp').read_text(encoding='utf-8').split('void ADungeonFairytaleSwordProbe::Tick(float Dt)',1)[1].split('void ADungeonFairytaleSwordProbe::Finish',1)[0]
(O/'before').mkdir(parents=True)
for n in names:shutil.copy2(S/n,O/'before'/n)
shutil.copy2(cf,O/cf.name);shutil.copy2(af,O/af.name)
applied=subprocess.run(['git','apply','--ignore-space-change',str(patch)],cwd=R,text=True,capture_output=True);assert applied.returncode==0,applied.stderr
p=S/'DungeonFairytaleSwordPresentation.cpp';t=p.read_text(encoding='utf-8')
needle='Primary3?DungeonFairytaleSwordPrimary3V001::Find(Record.Clip,Record.Frame)';assert t.count(needle)==1
t=t.replace('#include "DungeonFairytaleSwordPrimary3V001.inl"','#include "DungeonFairytaleSwordPrimary3V001.inl"\n#include "DungeonFairytaleSwordPrimary3V002.inl"').replace(needle,'Primary3?(Record.EquipmentBoundMode?DungeonFairytaleSwordPrimary3V002::Find(Record.Clip,Record.Frame)\n        :DungeonFairytaleSwordPrimary3V001::Find(Record.Clip,Record.Frame))')
p.write_text(t,encoding='utf-8')
axistext=axis.read_text(encoding='utf-8');assert axistext.count('UNAPPLIED axis-only Root Bound-mode trial')==1
(S/axis.name).write_text(axistext.replace('UNAPPLIED axis-only Root Bound-mode trial','Axis-only Root Bound-mode trial'),encoding='utf-8')
assert desc(S/'DungeonFairytaleSwordPrimary3V001.inl')['sha256']=='6749343b607b21ae5d7d1b8d1bf959b67324d13b85c7f6b37f70097088116054'
assert all(desc(S/n)==d for n,d in probe_before.items()), 'The native RED/GREEN probe must be unchanged'
nowtick=(S/'DungeonFairytaleSwordProbe.cpp').read_text(encoding='utf-8').split('void ADungeonFairytaleSwordProbe::Tick(float Dt)',1)[1].split('void ADungeonFairytaleSwordProbe::Finish',1)[0];assert old_tick==nowtick
assert (S/'DungeonHUD.cpp').read_text(encoding='utf-8').count('SpawnActor<ADungeonFairytaleEquipmentBoundProbe>()')==1
after=[desc(S/n) for n in names+[axis.name]]
receipt=dict(time=datetime.datetime.now(datetime.timezone.utc).isoformat(),consumer_freeze=desc(cf),axis_freeze=desc(af),prior_actual_feature_RED=desc(red/'原件/runtime-report.json'),RED_retention=desc(retention),actual_git_apply_exit=applied.returncode,after=after,native_RED_GREEN_probe_unchanged=list(probe_before.values()),old_three_stage_input_tick_unchanged=True,old_V001_marker_unchanged=True,V002_selected_only_when_Bound=True,compiled=False,native_GREEN=False,formal_complete_units=0)
(O/'admission.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
p=R/'docs/production/first-batch-v2/progress.json';shutil.copy2(p,O/'before/progress.json');m=read(p)
m['current_task']='EV048 native RED full transaction6false-draw points retained E243; actual5file Bound consumer+new2axis V002 admitted, compile/full141/nativeGREEN pending. Formal0/15active.'
m['ue_current_working_source_compiled']=False;m['ue_current_working_source_verified']=False;m['current_source_uncompiled_changes']=[x['path'] for x in after]
m['current_compiled_snapshot']='source-assets/production/backups/2026-10-16_EquipmentBound-nativeRED-beforeConsumer-v117'
m['current_source_verification_scope']='v117 is historical pre-consumer compiled native feature RED; no current full-suite claim. Working consumer is uncompiled.'
m['fairytale_sword_equipment_binding_v001']['actual_renderer_consumption_applied']=True;m['fairytale_sword_equipment_binding_v001']['native_binding_draw_proof']=None
m['next_snapshot']='v118';m['next_retention_batch']='E244';m['current_retention_batches']=list(dict.fromkeys(m['current_retention_batches']+['E242','E243']))
m['goal_status']='active';m['completed_content_units']=0;m['updated_utc']=receipt['time'];p.write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(actual_consumer_files=5,new_axis_inl=1,native_RED_unchanged=True,old_tick_unchanged=True,old_V001_unchanged=True,compiled=False,native_GREEN=False),ensure_ascii=False))
