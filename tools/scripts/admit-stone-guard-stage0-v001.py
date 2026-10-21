from pathlib import Path
import datetime,hashlib,json,shutil
R=Path('F:/Ourgame');D=R/'docs/production/first-batch-v2'
F=D/'evidence/stone-guard-kernel-v001/ue-stage0-admission-freeze-v001.json'
O=D/'evidence/stone-guard-kernel-v001/root-stage0-admission-v001'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def desc(p):
 b=p.read_bytes();return dict(path=p.as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
assert not O.exists();assert desc(F)['sha256']=='241297d26dc7b1cf01b437893e925d8669c36b019dc38207216b7922c113055b'
v=read(F);assert v['registered_count']==3 and len(v['files'])==4
m=read(R/'source-assets/production/backups/2026-10-16_PendingGear-MeleeAudio-full144GREEN-beforeNative-v121/compiled-source-manifest.json')
source={x['path']:x for x in m['files'] if x['path'].startswith('UnrealGame/Source/')}
actual={p.relative_to(R).as_posix():p for p in (R/'UnrealGame/Source').rglob('*') if p.is_file()}
assert set(source)==set(actual)
for k,p in actual.items():
 d=desc(p);assert d['bytes']==source[k]['bytes'] and d['sha256']==source[k]['sha256'],p
for row in v['files']:
 p=Path(row['path']);d=desc(p);assert d['bytes']==row['bytes'] and d['sha256']==row['sha256']
 assert not (R/row['destination']).exists()
O.mkdir(parents=True);shutil.copy2(D/'progress.json',O/'before-progress.json')
(O/'plan.md').write_text('STN003纯战斗核准入：先只加冻结四NEW文件，实际UBT编译0后跑3组stub语义RED；再仅替换生产CPP，原3tests保持，跑完整147。首次compile/include问题另留档，不算RED。之后才推进真实Driver/LOS/sweep/HP同步/伤害奖励及存续；纯核通过不算敌人单元完成。当前造型工作只有179参考，不改共同body或盔甲资源。\n',encoding='utf-8')
after=[]
for row in v['files']:
 p=R/row['destination'];shutil.copy2(row['path'],p);assert p.read_bytes()==Path(row['path']).read_bytes();after.append(desc(p))
(O/'admission.json').write_text(json.dumps(dict(freeze=desc(F),added_files=after,existing_source_files_checked=len(actual),old_Source_unchanged=True,production_applied=False,actual_UE_compile=None,actual_UE_RED=None,prospective_full_count=147,formal_complete_units=0),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
v=read(D/'progress.json');v['current_task']='EV048 art179 source/reference pending component work; actual STN003 fourNEW Stage0 kernel/test files admitted after sourcev121 pin check. Source now changed/uncompiled; old144/nativev121 historical. No native GuardDriver or full enemy completion.';v['ue_current_working_source_compiled']=False;v['ue_current_working_source_verified']=False;v['current_source_uncompiled_changes']='Four NEW StoneGuard Stage0 h/stubCpp/three registered UE tests/oracle. Production implementation not yet admitted.';v['stone_guard_kernel_v001']=dict(stage0=desc(O/'admission.json'),actual_Source_admitted=True,production_applied=False,actual_UE_RED=None,actual_UE_GREEN=None,actual_native_driver=None,formal_unit_complete=False);v['goal_status']='active';v['completed_content_units']=0;v['updated_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();(D/'progress.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(added_Source=4,registered_tests=3,production_applied=False,old_source_unchanged=True,next='actual compile and3cleanRED'),ensure_ascii=False))
