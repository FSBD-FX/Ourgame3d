"""Readonly actual HUD range-log/native-observation proof; unchanged official Hurt oracle rerun."""
from pathlib import Path
import argparse,hashlib,json,math,re,subprocess,sys
R=Path('F:/Ourgame').resolve();C=Path(__file__).resolve().parent.parent
OFFICIAL=R/'source-assets/production/fairytale-hero-state-gap-v001/hurt-native-observer-candidate-v001'
PATTERN=re.compile(r'CombatRangeProof frame=(\d+) sim=([-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?) enabled=([01]) lines=(\d+)(?=\s|$)')
def need(v,why):
 if not v:raise ValueError(why)
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def resolve(p):
 p=Path(p);return (p if p.is_absolute() else R/p).resolve()
def fact(p):
 p=Path(p).resolve();h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return dict(path=p.as_posix(),bytes=p.stat().st_size,sha256=h.hexdigest())
def check(x):
 need(type(x) is dict and set(x)=={'path','bytes','sha256'},'Exact pin required');p=resolve(x['path']);actual=fact(p);need(all(actual[k]==x[k] for k in ['bytes','sha256']),'Pinned tool/source changed: '+str(p));return p
def tooling():
 f=C/'combat-range-tooling-freeze-v002.json'
 for x in read(f)['files']:check(dict(x,path=str(C/x['path'])))
 inputs=read(C/'read-only-input-pins-v001.json')
 for x in inputs.values():
  if type(x) is dict and set(x)=={'path','bytes','sha256'}:check(x)
 for x in read(OFFICIAL/'Hurt-native-observer-freeze-v001.json')['files']:check(x)
 return f
def parse_log(text):
 rows=[]
 for line_number,line in enumerate(text.splitlines(),1):
  if not re.search(r'(?<![A-Za-z0-9_-])CombatRangeProof(?=\s|$)',line):continue
  matches=list(PATTERN.finditer(line));need(len(matches)==1,'Malformed/ambiguous actual CombatRangeProof line '+str(line_number));m=matches[0]
  row=dict(log_line=line_number,frame=int(m[1]),sim=float(m[2]),enabled=int(m[3]),lines=int(m[4]))
  need(math.isfinite(row['sim']) and row['sim']>=0,'Invalid real HUD simulation time');rows.append(row)
 need(rows,'Actual -DungeonCombatRangeProof log is absent')
 need(all(b['frame']>=a['frame'] and b['sim']>=a['sim'] for a,b in zip(rows,rows[1:])),'HUD frame/sim order reversed; never align by nearest time')
 return rows
def correlate(report,rows,mode):
 need(mode in ['default0','debug1'],'Explicit known range proof mode required');enabled=int(mode=='debug1')
 need(all(x['enabled']==enabled for x in rows),'Actual enabled field differs from requested mode')
 if not enabled:need(all(x['lines']==0 for x in rows),'Default game submitted a combat range line')
 else:need(all(x['lines'] in [0,4,32] for x in rows),'Actual range helper count is not one native rectangle/circle or zero')
 lookup={}
 for x in rows:lookup.setdefault(x['sim'],[]).append(x)
 focus={'AxeWindup':[],'AxeActive':[]};matched=[]
 for i,o in enumerate(report['observations']):
  stamp=o['sim'];need(math.isfinite(stamp) and stamp in lookup,'Original observation lacks exact same-sim HUD log: '+str(i));logs=lookup[stamp]
  need(len({(x['enabled'],x['lines']) for x in logs})==1,'Repeated same-sim HUD draws disagree; do not choose a favorable draw')
  witness=dict(observation=i,sim=stamp,HUD_frames=[x['frame'] for x in logs],log_lines=[x['log_line'] for x in logs],submitted_range_lines=logs[0]['lines']);matched.append(witness)
  a=o.get('guard_action')
  if not a or str(a['attack_id'])!=str(report['hit_attack']) or a['kind']!=1 or not a['in_progress'] or a['interrupted']:continue
  phase='AxeWindup' if a['start']<=stamp<a['active_at'] else 'AxeActive' if a['active_at']<=stamp<a['active_end'] else None
  if phase:
   if enabled:need(all(x['lines']>=4 for x in logs),'Original same-Aid Axe WU/Active lacks real submitted range lines')
   focus[phase].append(witness)
 need(focus['AxeWindup'] and focus['AxeActive'],'Original actual hit AttackId has no matched WU/Active observations')
 return dict(mode=mode,enabled=enabled,HUD_log_rows=len(rows),native_observations=len(matched),all_observations_exact_sim_matched=True,nearest_time_tolerance_used=False,repeated_sim_draws_checked_consistently=True,maximum_submitted_lines=max(x['lines'] for x in rows),original_hit_attack=report['hit_attack'],focus_witnesses=focus,observation_log_witnesses=matched)
def verify(archive,snapshot,prereg,mode):
 own=tooling();archive=resolve(archive);snapshot=resolve(snapshot);prereg=resolve(prereg);index=read(archive/'index.json');original=archive/'原件';report=read(original/'runtime-report.json')
 need(index['schema']=='hero-Hurt4-native-session-v001' and report['schema']=='hero-SWD-LGT-Hurt4-native-observer-v001' and report['scenario']=='GuardAxeToHeroHurt4','Original native protocol differs')
 need(index['candidate_freeze_sha256']==fact(OFFICIAL/'Hurt-native-observer-freeze-v001.json')['sha256'] and index['combat_range_tooling_freeze_sha256']==fact(own)['sha256'],'Official observer/additional tooling freeze binding differs')
 need(index['combat_range_mode']==mode and index['combat_range_debug_enabled'] is(mode=='debug1') and index['combat_range_proof_requested'] is True,'Actual session lacks explicit range flags/mode')
 expected=['-DungeonCombatRangeProof']+(['-DungeonCombatRangeDebug'] if mode=='debug1' else [])
 need(index['combat_range_extra_flags']==expected,'Actual launch range flags differ')
 need(index['process_id']==int(report['process_id']) and index['exit_code']==0 and report['passed'] is True and report['flow_complete'] is True and index['native_reported_passed'] is True and index['independent_passed'] is True,'Fresh PID/native/official independent PASS required')
 need(index['snapshot_manifest_sha256']==fact(snapshot/'compiled-source-manifest.json')['sha256'] and resolve(index['root_prereg'])==prereg and index['root_prereg_sha256']==fact(prereg)['sha256'],'Fresh compiled snapshot/Root prereg binding differs')
 need(read(snapshot/'compiled-source-manifest.json')['strict_registered_tests']==187,'Fresh actual strict187 snapshot required')
 if mode=='debug1':need(report['requested_approach_side']==report['actual_approach_side']==-1,'Positive Debug1 control must use real left-side Hurt fixture')
 checker=OFFICIAL/'tooling/verify-Hurt-native-v001.py'
 rerun=subprocess.run([sys.executable,'-B','-X','utf8',str(checker),'--snapshot',str(snapshot),'--root-prereg',str(prereg),'--archive',str(archive)],capture_output=True,text=True,encoding='utf-8')
 need(rerun.returncode==0,'Unchanged official Hurt checker RED: '+rerun.stderr)
 official=json.loads(rerun.stdout);receipt=read(original/'Hurt-independent-native-verification-v001.json');need(official==receipt and official['passed'] is True,'Readonly official rerun differs from actual original independent receipt')
 log=archive/'runtime.log';rows=parse_log(log.read_text(encoding='utf-8-sig',errors='replace'));result=correlate(report,rows,mode)
 # Launcher finalizes its status/range-pass fields only after this readonly check.
 # Bind every stable session input/result field, not a premature whole-file SHA.
 session_binding={k:v for k,v in index.items() if k not in ['status','combat_range_independent_passed','failure']}
 result.update(passed=True,schema='combat-range-native-log-verification-v001',process_id=report['process_id'],run=report['run'],actual_approach_side=report['actual_approach_side'],native_report=fact(original/'runtime-report.json'),session_path=str(archive/'index.json'),session_stable_binding=session_binding,session_stable_binding_sha256=hashlib.sha256(json.dumps(session_binding,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode('utf-8')).hexdigest(),excluded_finalizing_session_fields=['status','combat_range_independent_passed','failure'],runtime_log=fact(log),official_independent_receipt=fact(original/'Hurt-independent-native-verification-v001.json'),compiled_manifest=fact(snapshot/'compiled-source-manifest.json'),Root_prereg=fact(prereg),additional_tooling_freeze=fact(own),official_Hurt_checker_unchanged_rerun_equal=True,original_HP_loss=report['actual_HP_loss'],original_hit_at=report['hit_at'],HurtMask=report['HurtMask'],optical_thresholds_changed=False,source_or_archive_written=False,UE_started=False,visual_reviewed=False,FinalAccepted=False,formal_complete_units=0)
 return result
def main():
 p=argparse.ArgumentParser();p.add_argument('--archive',required=True);p.add_argument('--snapshot',required=True);p.add_argument('--root-prereg',required=True);p.add_argument('--expected-mode',required=True,choices=['default0','debug1']);a=p.parse_args();print(json.dumps(verify(a.archive,a.snapshot,a.root_prereg,a.expected_mode),ensure_ascii=False))
if __name__=='__main__':main()
