from pathlib import Path
import datetime,hashlib,json,os,shutil,subprocess
R=Path('F:/Ourgame');B=R/'source-assets/production/stone-guard-owner-v002';F=B/'stage0-freeze-v001.json';O=R/'docs/production/first-batch-v2/evidence/stone-guard-owner-v002/root-stage0-admission-v001';assert not O.exists()
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def desc(p):
 b=p.read_bytes();return dict(path=p.as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def check(p,row):
 d=desc(p);assert (d['bytes'],d['sha256'])==(row['bytes'],row['sha256']),p
v=load(F);assert desc(F)['sha256']=='de71f290e508ff1b2e443f75884f60203958e0d60a986b6aa653a7b2f4aaf8bf'
for x in v['files']+v['evidence']:check(Path(x['path']),x)
for x in v['exact_source_inputs']+v['read_only_dependencies']:check(R/x['path'],x)
check(Path(v['base_snapshot']['path']),v['base_snapshot']);snap=load(Path(v['base_snapshot']['path']))
for x in snap['files']:
 if x['path'].startswith(('UnrealGame/Source/','UnrealGame/Config/','UnrealGame/Content/Production/')):check(R/x['path'],x)
patch=B/'patches/stage0-model-and-stubs-v001.patch';subprocess.run(['git','apply','--check',str(patch)],cwd=R,check=True)
before={p:desc(p) for p in (R/'UnrealGame/Source').rglob('*') if p.is_file()};O.mkdir(parents=True)
for p in [R/x['path'] for x in v['exact_source_inputs']]+[R/'UnrealGame/Binaries/Win64/UnrealEditor-CodexDungeon.dll',R/'UnrealGame/Saved/Bootstrap/last-build.json',R/'docs/production/first-batch-v2/progress.json']:
 q=O/'before'/p.relative_to(R);q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q);assert p.read_bytes()==q.read_bytes()
subprocess.run(['git','apply',str(patch)],cwd=R,check=True)
dest=[]
for c in sorted((B/'stage0-source').rglob('*')):
 if not c.is_file():continue
 p=R/'UnrealGame/Source/CodexDungeon'/c.relative_to(B/'stage0-source')
 if c.parent.name=='Tests':assert not p.exists();shutil.copy2(c,p)
 assert p.read_bytes().replace(b'\r\n',b'\n')==c.read_bytes().replace(b'\r\n',b'\n');os.utime(p,None);dest.append(desc(p))
expected={R/x['path'] for x in v['exact_source_inputs']};assert {p for p,x in before.items() if desc(p)!=x}==expected
out=dict(freeze=desc(F),source_before=list(before.values()),admitted=dest,source_mtime_refreshed=True,other_source_unchanged=True,compiled=False,expected_semantic_RED_count=3,downstream_codec_installer_RED_observed=False)
(O/'admission.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
p=R/'docs/production/first-batch-v2/progress.json';d=load(p);d.update(ue_current_working_source_compiled=False,ue_current_working_source_verified=False,current_source_uncompiled_changes='Guard Owner Stage0: 6 model/API/stub files plus 2 NEW test files admitted. Compile/3 honest Capture RED pending.',actual_registered_test_count_current=160,updated_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),next_native_request=199,next_media_retention_batch=312)
g=load(R/'source-assets/production/first-unit-animation-v003/generation-ledger.json');d['generation_accounting_current']=dict(requested_count=g['requested_count'],window_number=9,window_requested_count=6,window_limit=24,remaining_in_window=18,lifetime_requested_count=g['lifetime_requested_count'],external_api_calls=0,fee_unknown=True)
d['stone_guard_owner_v002']=dict(stage0_admission=desc(O/'admission.json'),actual_RED=None,actual_GREEN=None,formal_complete_units=0);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(dict(admitted=len(dest),compile_pending=True,formal_complete_units=0)))
