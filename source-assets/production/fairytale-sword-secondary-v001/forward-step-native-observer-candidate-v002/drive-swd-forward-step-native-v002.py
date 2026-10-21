"""Pinned normal-input native K launcher; exploratory collection never grants acceptance."""
from pathlib import Path
import argparse,hashlib,json,subprocess,sys,importlib.util,math
ROOT=Path('F:/Ourgame');HERE=Path(__file__).resolve().parent
class NotReady(ValueError):pass
def need(ok,why):
 if not ok:raise NotReady(why)
def pin(row):
 need(isinstance(row,dict) and {'path','bytes','sha256'}<=set(row),'missing immutable path pin');p=Path(row['path']);p=p if p.is_absolute() else ROOT/p;b=p.read_bytes();need(len(b)==row['bytes'] and hashlib.sha256(b).hexdigest()==row['sha256'],'pin mismatch: '+str(p));return p
def load(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def route_digest(route):
 d={k:route[k] for k in ['facing','enemy_diagnostic_used','waypoints']};return hashlib.sha256(json.dumps(d,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
def route_gate(p,case,mode):
 need(mode in ('strict','exploratory_pilot') and p.get('route_mode')==mode,'explicit requested mode and prereg route_mode must agree');need(case in p['cases'],'case not preregistered');r=p['cases'][case];need(r['enemy_diagnostic_used'] is False,'enemy diagnostic route prohibited');need(r['facing']==(1 if case.endswith('_right') else -1),'case facing mismatch');need(isinstance(r['normal_route_native_verified'],bool),'route status must remain an explicit real boolean')
 for w in r['waypoints']:
  need(len(w['xy'])==2 and all(type(v) in (int,float) and math.isfinite(v) for v in w['xy']) and 0<w['tolerance_cm']<=10 and type(w['allow_blocked_contact']) is bool,'finite normal-input waypoint required')
 if mode=='exploratory_pilot':return r
 need(r['normal_route_native_verified'] is True,'strict mode requires independently verified actual route')
 v=load(pin(r['route_native_verification']));need(v['schema']=='swd-normal-route-native-verification-v002' and v['actual_native_route_verified'] is True and v['case']==case and v['route_sha256']==route_digest(r),'strict route verification missing/does not match exact normal inputs');pin(v['independent_review_report']);actual=load(pin(v['native_runtime_report']));need(actual['schema']=='swd-forward-step-native-observer-v002' and actual['case']==case and actual['player_enemy_HP_position_AI_clock_writes'] is False and actual['enemy_diagnostic_used'] is False and route_digest(actual['route_input_configuration'])==route_digest(r),'route verification does not refer to actual same-route native report')
 spec=importlib.util.spec_from_file_location('placement_route_verifier_v002',HERE/'check-swd-forward-step-native-v002.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);mod.audit_placement(actual,require_case_match=True)
 return r
FLAGS=['-game','-d3d11','-windowed','-ResX=1280','-ResY=720','-unattended','-nosplash','-NoLiveCoding','-AudioMixer','-DungeonSwdForwardStepProofV002','-DungeonContentProof','-DungeonFastLosslessCapture','-DungeonAsyncLosslessCapture','-DungeonCandidateSprites','-DungeonFairytaleSwordEquipmentBoundPreview','-DungeonFairytaleLeatherReadyPreview','-DungeonFairytaleSwordSecondaryPreview','-DungeonFairytaleSwordWalkPreview','-DungeonFairytaleSwordHurtPreview','-DungeonFairytaleSwordDeathPreview']
def launch_args(p,exe,project,original,case,prereg):
 extra=['-DungeonSwdForwardStepPilotV002'] if p['route_mode']=='exploratory_pilot' else []
 return [str(exe),str(project),p['map']]+FLAGS+extra+['-DungeonContentProofDir='+original.as_posix(),'-DungeonSwdForwardStepCase='+case,'-DungeonSwdForwardStepPrereg='+Path(prereg).resolve().as_posix()]
def preflight(path,case,mode):
 p=load(path);need(p.get('schema')=='swd-forward-step-native-readiness-v002','wrong readiness schema');need(p.get('ready') is True,'; '.join(p.get('pending',[])) or 'candidate not admitted');route_gate(p,case,mode)
 need(p['K_profile_runtime_ready'] is p['observer_editor_compile_verified'] is p['observer_fresh_review_approved'] is p['placement_witness_source_ready'] is True,'actual profile/observer/getter admission, compile and fresh review required');pin(p['review_report']);cm=load(pin(p['compiled_manifest']));need(cm['failed']==cm['notRun']==0 and cm['passed']==cm['registered_tests'],'complete fresh compiled tests not GREEN')
 actual=sorted(str(x.relative_to(ROOT)).replace('\\','/') for x in (ROOT/'UnrealGame/Source').rglob('*') if x.is_file());rows=[x for x in cm['files'] if x['path'].replace('\\','/').startswith('UnrealGame/Source/')];need(sorted(x['path'].replace('\\','/') for x in rows)==actual,'compiled manifest does not cover entire actual Source tree')
 for row in cm['files']:pin(row)
 required={'DungeonSwdForwardStepProbeV002.cpp','DungeonSwdForwardStepProbeV002.h','DungeonFairytaleSwordSecondaryDrawStateV001.h','DungeonFairytaleSwordSecondaryPlanV001.h','DungeonActionAudioFeedback.h','DungeonWorldProjectiles.h','DungeonWorldProjectiles.cpp','DungeonGameMode.h','DungeonHUD.cpp'};need(required<={Path(x).name for x in actual},'actual observer/K8/placement source admission missing')
 need('QueryWeaponForwardStepPlacementV001' in (ROOT/'UnrealGame/Source/CodexDungeon/DungeonGameMode.h').read_text(encoding='utf-8-sig') and 'FDungeonWeaponForwardStepPlacementV001' in (ROOT/'UnrealGame/Source/CodexDungeon/DungeonWorldProjectiles.h').read_text(encoding='utf-8-sig'),'actual placement getter/DTO absent')
 exe=pin(p['editor_executable']);dll=pin(p['game_dll']);project=pin(p['uproject']);need(dll.name=='UnrealEditor-CodexDungeon.dll','actual compiled game DLL pin required')
 resources=p['resource_pins'];need(len(resources)==81 and len({x['texture'] for x in resources})==81,'K57+Ready24 distinct UE object closure required');need(sum(x['group']=='K' for x in resources)==57 and sum(x['group']=='Ready' for x in resources)==24,'resource groups incomplete')
 for row in resources:pin(dict(path=row['source_png'],bytes=row['bytes'],sha256=row['sha256']));pin(row['uasset'])
 for name in ('main_mix','native_png'):pin(p['checker_dependencies'][name])
 if mode=='strict':pin(p['checker_dependencies']['K_pixel_composition'])
 elif p['checker_dependencies'].get('K_pixel_composition'):pin(p['checker_dependencies']['K_pixel_composition'])
 need(p['map']=='/Game/Maps/FirstRoom?DungeonFirstBatchGuardRoom','fixed actual map required');return p,exe,project
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--prereg',type=Path,default=HERE/'prereg-exploratory-full-right-template-v002.json');ap.add_argument('--mode',choices=['strict','exploratory_pilot'],default='strict');ap.add_argument('--case',choices=['full_right','full_left','partial_right','partial_left','blocked_zero_right','blocked_zero_left'],default='full_right');ap.add_argument('--run',action='store_true');ap.add_argument('--archive',type=Path);ns=ap.parse_args();attempted=False
 try:
  p,exe,project=preflight(ns.prereg,ns.case,ns.mode)
  if not ns.run:print(json.dumps(dict(status='ReadyForNativeCollection',native_run_attempted=False,route_mode=ns.mode,formal_accepted=False,checker_accepted=False)));sys.exit(0)
  need(ns.archive is not None and ns.archive.is_absolute() and not ns.archive.exists(),'one new absolute archive directory required');ns.archive.mkdir(parents=True,exist_ok=False);original=ns.archive/'原件';original.mkdir();args=launch_args(p,exe,project,original,ns.case,ns.prereg)
  with (ns.archive/'launch-argv.json').open('x',encoding='utf8') as f:json.dump(dict(schema='swd-normal-K-launch-v002',argv=args,prereg_sha256=hashlib.sha256(ns.prereg.read_bytes()).hexdigest(),listened=False,route_mode=ns.mode,formal_accepted=False,checker_accepted=False),f,ensure_ascii=False,indent=2)
  proc=subprocess.Popen(args,cwd=ROOT,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0));attempted=True
  with (ns.archive/'process-started.json').open('x',encoding='utf8') as f:json.dump(dict(process_id=str(proc.pid),prereg_sha256=hashlib.sha256(ns.prereg.read_bytes()).hexdigest(),native_run_attempted=True),f,indent=2)
  code=proc.wait(timeout=120)
  with (ns.archive/'process-exit.json').open('x',encoding='utf8') as f:json.dump(dict(exit_code=code,native_run_attempted=True),f)
  if code and ns.mode=='strict':raise ValueError('Native strict process failed '+str(code)+'; raw evidence retained')
  need((original/'runtime-report.json').is_file(),'native runtime report missing; no placement or route inference')
  checked=subprocess.run([sys.executable,'-B','-X','utf8',str(HERE/'check-swd-forward-step-native-v002.py'),'--archive',str(ns.archive),'--prereg',str(ns.prereg)],capture_output=True,text=True,encoding='utf8')
  with (ns.archive/'native-check-result.json').open('x',encoding='utf8') as f:f.write(checked.stdout)
  print(checked.stdout);sys.exit(checked.returncode)
 except (NotReady,OSError,KeyError,TypeError) as e:print(json.dumps(dict(status='NotReady',passed=False,reason=str(e),native_run_attempted=attempted,formal_accepted=False,checker_accepted=False),ensure_ascii=False));sys.exit(2)
 except (ValueError,subprocess.TimeoutExpired) as e:print(json.dumps(dict(status='NeedsFixes',passed=False,reason=str(e),native_run_attempted=attempted,evidence_preserved=True,formal_accepted=False,checker_accepted=False),ensure_ascii=False));sys.exit(3)
