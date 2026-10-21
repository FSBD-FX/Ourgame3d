"""Fail-closed normal-input native K driver. Default prereg is intentionally NotReady."""
from pathlib import Path
import argparse, hashlib, json, subprocess, sys
ROOT=Path('F:/Ourgame');HERE=Path(__file__).resolve().parent
class NotReady(ValueError): pass
def need(ok,why):
    if not ok: raise NotReady(why)
def pin(p):
    need(isinstance(p,dict) and set(('path','bytes','sha256'))<=set(p),'missing immutable path pin');path=Path(p['path']);path=path if path.is_absolute() else ROOT/path;b=path.read_bytes();need(len(b)==p['bytes'] and hashlib.sha256(b).hexdigest()==p['sha256'],'pin mismatch: '+str(path));return path
FLAGS=['-game','-d3d11','-windowed','-ResX=1280','-ResY=720','-unattended','-nosplash','-NoLiveCoding','-AudioMixer','-DungeonSwdForwardStepProofV001','-DungeonContentProof','-DungeonFastLosslessCapture','-DungeonAsyncLosslessCapture','-DungeonCandidateSprites','-DungeonFairytaleSwordEquipmentBoundPreview','-DungeonFairytaleLeatherReadyPreview','-DungeonFairytaleSwordSecondaryPreview','-DungeonFairytaleSwordWalkPreview','-DungeonFairytaleSwordHurtPreview','-DungeonFairytaleSwordDeathPreview']
def launch_args(p,exe,project,original,case,prereg):
    return [str(exe),str(project),p['map']]+FLAGS+['-DungeonContentProofDir='+original.as_posix(),'-DungeonSwdForwardStepCase='+case,'-DungeonSwdForwardStepPrereg='+Path(prereg).resolve().as_posix()]
def preflight(path,case):
    p=json.loads(Path(path).read_text(encoding='utf-8-sig'));need(p.get('schema')=='swd-forward-step-native-readiness-v001','wrong readiness schema');need(p.get('ready') is True,'; '.join(p.get('pending',[])) or 'candidate not admitted')
    need(case in p['cases'],'case not preregistered');route=p['cases'][case];need(route['normal_route_native_verified'] is True,'actual normal-input obstacle route not verified');need(route['enemy_diagnostic_used'] is False,'candidate excludes enemy diagnostics')
    if case.startswith('blocked_zero'):raise NotReady('No independent actual zero-placement commit reader admitted')
    need(p['K_profile_runtime_ready'] is True and p['observer_editor_compile_verified'] is True and p['observer_fresh_review_approved'] is True,'runtime/profile/observer compilation and review pending')
    pin(p['review_report']);cmfile=pin(p['compiled_manifest']);cm=json.loads(cmfile.read_text(encoding='utf-8-sig'));need(cm['failed']==cm['notRun']==0 and cm['passed']==cm['registered_tests'],'fresh compiled-manifest test gate not GREEN')
    actual=sorted(str(x.relative_to(ROOT)).replace('\\','/') for x in (ROOT/'UnrealGame/Source').rglob('*') if x.is_file());rows=[x for x in cm['files'] if x['path'].replace('\\','/').startswith('UnrealGame/Source/')];need(sorted(x['path'].replace('\\','/') for x in rows)==actual,'compiled manifest is not current complete Source tree')
    for row in cm['files']:pin(row)
    required={'DungeonSwdForwardStepProbeV001.cpp','DungeonSwdForwardStepProbeV001.h','DungeonFairytaleSwordSecondaryDrawStateV001.h','DungeonFairytaleSwordSecondaryPlanV001.h','DungeonActionAudioFeedback.h','DungeonWorldProjectiles.cpp','DungeonHUD.cpp'};need(required<={Path(x).name for x in actual},'actual observer/K8/audio Source admission missing')
    exe=pin(p['editor_executable']);dll=pin(p['game_dll']);project=pin(p['uproject']);need(dll.name=='UnrealEditor-CodexDungeon.dll','exact current game DLL pin required')
    pins=p['resource_pins'];need(len(pins)==81 and len({x['texture'] for x in pins})==81,'exact K57 + Ready24 source closure required')
    need(sum(x['group']=='K' for x in pins)==57 and sum(x['group']=='Ready' for x in pins)==24,'resource groups incomplete')
    for row in pins:pin(dict(path=row['source_png'],bytes=row['bytes'],sha256=row['sha256']));pin(row['uasset'])
    for row in p['checker_dependencies'].values():pin(row)
    need(p['map']=='/Game/Maps/FirstRoom?DungeonFirstBatchGuardRoom','actual route map must be fixed')
    return p,exe,project
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--prereg',type=Path,default=HERE/'readiness-v001.json');ap.add_argument('--case',choices=['full_right','full_left','partial_right','partial_left','blocked_zero_right','blocked_zero_left'],default='full_right');ap.add_argument('--run',action='store_true');ap.add_argument('--archive',type=Path);ns=ap.parse_args()
    try:
        p,exe,project=preflight(ns.prereg,ns.case)
        if not ns.run:print(json.dumps(dict(status='ReadyForNativeRun',passed=True,native_run_attempted=False)));sys.exit(0)
        need(ns.archive is not None and ns.archive.is_absolute() and not ns.archive.exists(),'one new absolute archive required');ns.archive.mkdir(parents=True,exist_ok=False);original=ns.archive/'原件';original.mkdir()
        args=launch_args(p,exe,project,original,ns.case,ns.prereg)
        with (ns.archive/'launch-argv.json').open('x',encoding='utf-8') as f:json.dump(dict(schema='swd-normal-K-launch-v001',argv=args,prereg_sha256=hashlib.sha256(ns.prereg.read_bytes()).hexdigest(),listened=False),f,ensure_ascii=False,indent=2)
        # Root must explicitly invoke --run after scoped source review and admission.
        proc=subprocess.Popen(args,cwd=ROOT,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
        with (ns.archive/'process-started.json').open('x',encoding='utf-8') as f:json.dump(dict(process_id=str(proc.pid),prereg_sha256=hashlib.sha256(ns.prereg.read_bytes()).hexdigest(),native_run_attempted=True),f,indent=2)
        code=proc.wait(timeout=120)
        if code:raise ValueError('Native process failed with '+str(code)+'; evidence retained')
        checked=subprocess.run([sys.executable,'-B','-X','utf8',str(HERE/'check-swd-forward-step-native-v001.py'),'--archive',str(ns.archive),'--prereg',str(ns.prereg)],capture_output=True,text=True,encoding='utf-8')
        with (ns.archive/'native-check-result.json').open('x',encoding='utf-8') as f:f.write(checked.stdout)
        print(checked.stdout);sys.exit(checked.returncode)
    except (NotReady,OSError,KeyError,TypeError) as e:print(json.dumps(dict(status='NotReady',passed=False,reason=str(e),native_run_attempted=False),ensure_ascii=False));sys.exit(2)
    except (ValueError,subprocess.TimeoutExpired) as e:print(json.dumps(dict(status='NeedsFixes',passed=False,reason=str(e),evidence_preserved=True),ensure_ascii=False));sys.exit(3)
