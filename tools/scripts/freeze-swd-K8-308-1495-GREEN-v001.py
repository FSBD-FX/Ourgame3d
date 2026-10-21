"""Freeze actual current K8 source/content and new successful D3D11 regression."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,json,shutil
R=Path('F:/Ourgame');E=R/'docs/production/first-batch-v2/evidence/HeroSwordSecondary-v147-v001'
O=R/'source-assets/production/backups/v148-SWDSecondary8-308-1495-203GREEN-v001'
def need(b,s):
 if not b:raise ValueError(s)
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def pin(p,relative=False):
 p=Path(p);b=p.read_bytes();return dict(path=p.relative_to(R).as_posix() if relative else p.as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def checked(x):
 p=Path(x['path']);p=p if p.is_absolute() else R/p;z=pin(p);need(z['bytes']==x['bytes'] and z['sha256']==x['sha256'],'actual pin differs '+str(p));return p
def utc(s):return datetime.fromisoformat(s.replace('Z','+00:00'))
a=argparse.ArgumentParser();a.add_argument('--suite',required=True,type=Path);a.add_argument('--native-log',required=True,type=Path);n=a.parse_args()
need(not O.exists(),'never overwrite or repeat a compiled snapshot')
adp=E/'Root-K8-source-admission-v001/actual-source-admission.json';need(pin(adp)['sha256']=='fe3adc65ffb903fb8b2dfdc9f7d57ca72ee0ac7d31844ac29a0259a898d01a67','actual reviewed source admission required');ad=read(adp)
need(ad['actual_Source_admitted'] is True and ad['source_after']==308 and ad['verification_passes']==2 and ad['twoSHA_mismatches']==0,'actual successful308 source admission required')
old=read(checked(ad['predecessor_compiled_manifest']));changed={x['path']:x['actual'] for x in ad['files']};added={x['path'] for x in ad['files'] if x['new_file']}
for row in old['files']:
 if row['path'].startswith(('UnrealGame/Source/','UnrealGame/Content/Production/')):checked(changed.get(row['path'],row))
for x in ad['files']:checked(x['actual'])
vpath=checked(ad['actual_Content_verification']);v=read(vpath)
need(v['verified'] is True and v['same_PID_exit0'] is True and v['actual_Production1495'] is True,'real56 Content import proof required')
for x in v['saved_uasset_pins']:checked(x)
source=sorted(p for p in (R/'UnrealGame/Source').rglob('*') if p.is_file());content=sorted(p for p in (R/'UnrealGame/Content/Production').rglob('*') if p.is_file())
need(len(source)==308 and len(content)==1495,'actual Source308/Production1495 membership required')
need({p.relative_to(R).as_posix() for p in source}=={x['path'] for x in old['files'] if x['path'].startswith('UnrealGame/Source/')}|added,'actual308 closed source set differs')
need({p.relative_to(R).as_posix() for p in content}=={x['path'] for x in old['files'] if x['path'].startswith('UnrealGame/Content/Production/')}|{checked(x).relative_to(R).as_posix() for x in v['saved_uasset_pins']},'actual1495 closed Content set differs')
suite=n.suite.resolve();need(suite.is_relative_to(R/'UnrealGame/Saved/Automation'),'actual Automation report path required');q=read(suite)
need([q[k] for k in ('succeeded','succeededWithWarnings','failed','notRun','inProcess')]==[203,0,0,0,0],'actual full203 all GREEN required')
oldq=read(checked(old['full_suite']));need(len(q['tests'])==203 and len({x['fullTestPath'] for x in q['tests']})==203 and {x['fullTestPath'] for x in q['tests']}=={x['fullTestPath'] for x in oldq['tests']},'all original203 exact test IDs required')
for t in q['tests']:need(t['state']=='Success' and t['warnings']==t['errors']==0 and not any(e['event']['type'] in ('Error','Warning') for e in t['entries']),'individual actual test not clean Success')
need(q['devices'] and all(x['rHI']=='DirectX 11' and x['renderMode']=='D3D11_SM5' for x in q['devices']),'actual D3D11 device report required')
native_log=n.native_log.resolve();need(native_log.is_relative_to(R/'UnrealGame/Saved/Bootstrap') and 'LogD3D11RHI' in native_log.read_text('utf-8-sig',errors='replace'),'actual native D3D11 log required')
build=R/'UnrealGame/Saved/Bootstrap/last-build.json';b=read(build);need(b['ExitCode']==0 and b['Target']=='CodexDungeonEditor','real successful Editor build required')
need(utc(b['Utc'])>=utc(ad['utc']),'build must follow actual source admission')
report_time=datetime.strptime(q['reportCreatedOn'],'%Y.%m.%d-%H.%M.%S').replace(tzinfo=timezone.utc)
need(report_time>=utc(b['Utc']) and suite!=checked(old['full_suite']),'new original203 report must follow current build')
log=Path(b['Log']);need(log.is_relative_to(R/'UnrealGame/Saved/Bootstrap') and log.is_file(),'actual build log required')
dll=R/'UnrealGame/Binaries/Win64/UnrealEditor-CodexDungeon.dll';project=R/'UnrealGame/CodexDungeon.uproject'
files=source+content+[build,log,suite,dll,project];pins=[pin(p,True) for p in files];need(len({x['path'] for x in pins})==len(pins),'snapshot duplicate membership')
O.mkdir()
for p in source+[build,log,suite,dll,project,adp,vpath,native_log]:
 target=O/'snapshot'/p.relative_to(R);target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,target);need(pin(target)['sha256']==pin(p)['sha256'],'snapshot copy differs')
for _ in range(2):
 for row in pins:need(pin(R/row['path'],True)==row,'actual compiled input changed during freeze')
out=O/'compiled-source-manifest.json'
j=dict(schema='Root-SWDSecondary8-current308-1495-full203-GREEN-v001',utc=datetime.now(timezone.utc).isoformat(),source_files=308,production_files=1495,production_textures=1489,SoundWaves=6,registered_tests=len(q['tests']),passed=q['succeeded'],failed=q['failed'],notRun=q['notRun'],inProcess=q['inProcess'],warnings=q['succeededWithWarnings'],succeededWithWarnings=q['succeededWithWarnings'],build=pin(build),build_log=pin(log),full_suite=pin(suite),native_RHI_log=pin(native_log),source_admission_pin=pin(adp),actual_Content_verification=pin(vpath),files=pins,verification_passes=2,twoSHA_mismatches=0,old203_test_IDs_preserved=True,regression_GREEN=True,new_K_runtime_compiled=True,actual_native_K_capture_verified=False,formal_complete_units=0,completed_combinations=0,FinalAccepted=False)
with out.open('x',encoding='utf-8') as f:json.dump(j,f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps(dict(manifest=pin(out),Source=308,Production=1495,compiled_files=len(pins),passed=203,notRun=q['notRun'],inProcess=q['inProcess'],warnings=q['succeededWithWarnings'],actual_native_K_capture_verified=False),ensure_ascii=False))
