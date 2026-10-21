"""Read-only190GREEN/dynamicSource/1326/source-profile check; never starts UE."""
from pathlib import Path
import argparse,ast,hashlib,json,math,tempfile
R=Path('F:/Ourgame').resolve()
C=R/'source-assets/production/fairytale-hero-state-gap-v001/death-state-preparation-v001/Death40-manual-checkpoint-tooling-candidate-v001'
GUARD_CHECKER=R/'source-assets/production/fairytale-guard-v001/guard-known44-profile-extension-candidate-v004/verify-known44-profile-extension-v004.py'
DEATH_TESTS=tuple('CodexDungeon.Content.FairytaleSwordDeathV001.'+n for n in ['ActualFatalTerminalFivePhasesAndExclusions','RealBindingSource40MirrorAndAtomicRejection','RealCodecPauseContinueKeepsTerminalAgeAndEquipment'])
DEATH_FILES=tuple('UnrealGame/Source/CodexDungeon/'+n for n in ['DungeonDeathPresentation.h','DungeonFairytaleSwordDeathProfile.h','DungeonFairytaleSwordDeathProfile.cpp','DungeonFairytaleSwordDeathPlan.h','DungeonFairytaleSwordDeathPlan.cpp','DungeonFairytaleSwordDeathDrawState.h','Tests/DungeonFairytaleSwordDeathV001Tests.cpp','DungeonFairytaleSwordDeathTextures.inl','DungeonFairytaleSwordDeathPresentation.cpp','DungeonHeroDeathProbeV001.h','DungeonHeroDeathProbeV001.cpp','DungeonFighter.h','DungeonFighter.cpp','DungeonHUD.h','DungeonHUD.cpp','DungeonFairytaleSwordPresentation.cpp'])
def need(v,why):
 if not v:raise ValueError(why)
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def resolve(p):
 p=Path(p);p=(p if p.is_absolute() else R/p).resolve();need(p.is_relative_to(R),'Path escapes project');return p
def fact(p):
 p=resolve(p);b=p.read_bytes();return dict(path=p.as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def check(x):
 need(type(x) is dict and set(x)=={'path','bytes','sha256'},'Exact real pin required');p=resolve(x['path']);v=fact(p);need(type(x['bytes']) is int and v['bytes']==x['bytes'] and v['sha256']==x['sha256'],'Pinned input changed: '+str(p));return p
def approval(m):need(m.get('is_template') is False and m.get('RootApproved') is True,'Actual non-template Root approval required')
def rows_of_freeze(p):
 p=resolve(p);j=read(p);rows=j['files'];need(type(rows) is list and rows,'Nonempty candidate freeze required')
 for x in rows:
  q=Path(x['path']);q=q if q.is_absolute() else p.parent/q
  if not q.is_file() and not Path(x['path']).is_absolute():q=R/x['path']
  v=fact(q);need(v['bytes']==x['bytes'] and v['sha256']==x['sha256'],'Frozen candidate changed: '+str(q))
 return j
def strict_suite(s):
 need(type(s.get('succeeded')) is int and s['succeeded']==190,'Full actual190 strict GREEN required')
 need(all(type(s.get(k)) is int and s[k]==0 for k in ['failed','succeededWithWarnings','notRun','inProcess']),'Full suite has non-green counters')
 ts=s['tests'];names=[t['fullTestPath'] for t in ts];need(len(ts)==len(set(names))==190,'Unique full190 registry required')
 for t in ts:
  need(t['state']=='Success' and type(t['errors']) is int and t['errors']==0 and type(t['warnings']) is int and t['warnings']==0,'Every test must be strict Success')
  need(not any(e.get('event',{}).get('type') in ['Error','Warning'] for e in t.get('entries',[])),'Hidden native Error/Warning entry')
 for n in DEATH_TESTS:need(names.count(n)==1,'Required actualDeath target absent: '+n)
 return names
def guard_source_check(snapshot,prereg,helper):
 # The entire proven Known44 source/row/alias/import checker is retained.
 # Only its final Production extension helper path and that helperSHA are adapted.
 need(fact(GUARD_CHECKER)['sha256']=='7952a162e5912ac01c4fba95993594a15fcda5db68bf99e6becf53a26d5a8978','Pinned originalKnown44 checker changed')
 code=GUARD_CHECKER.read_text(encoding='utf-8-sig');before="extension_validator=HERE/'validate-production-extension-v004.py'";after='extension_validator=Path('+repr(str(helper))+')'
 need(code.count(before)==1 and code.count('b157fba56e7ba46ed1f22e857207e98e0b417a7136b536928aae617d67625124')==1,'Known44 adapter shape changed')
 code=code.replace(before,after).replace('b157fba56e7ba46ed1f22e857207e98e0b417a7136b536928aae617d67625124',fact(helper)['sha256'])
 scope={'__file__':str(GUARD_CHECKER),'__name__':'Death1326_readonly_Known44_source_checker_adapter'};exec(compile(ast.parse(code),str(GUARD_CHECKER),'exec'),scope)
 return scope['source_check'](snapshot,prereg)
def verify(path,snapshot_arg=None):
 m=read(path);approval(m);need(m['schema']=='Death1326-Root-manual-input-v001','Typed actual manual prereg required')
 own=check(m['checkpoint_tooling_freeze_pin']);need(own==C/'Death1326-manual-tooling-freeze-v001.json','Wrong manual tooling candidate');rows_of_freeze(own)
 frozen=read(own);running=next(x for x in frozen['files'] if Path(x['path']).name==Path(__file__).name);need(fact(Path(__file__))['sha256']==running['sha256'],'Running checker bytes not bound to candidate')
 snapshot=resolve(m['snapshot_directory']);mp=check(m['snapshot_manifest_pin']);need(mp==snapshot/'compiled-source-manifest.json','Snapshot directory/manifest mismatch')
 if snapshot_arg:need(resolve(snapshot_arg)==snapshot,'Only the uniquely Root-selected Snapshot is allowed')
 cm=read(mp);files={x['path'].replace('\\','/'):x for x in cm['files']};need(len(files)==len(cm['files']),'Compiledsnapshot repeats a file')
 source_paths={n for n in files if n.startswith('UnrealGame/Source/')};prod_paths={n for n in files if n.startswith('UnrealGame/Content/Production/')}
 need(type(cm['source_files']) is int and cm['source_files']==len(source_paths)>0 and cm['production_files']==len(prod_paths)==1326 and cm['strict_registered_tests']==190,'Actual compiled dynamicSource/Production1326/full190 differ')
 need(cm['source_verification_passes']==2 and cm['source_hash_mismatches']==0,'Compiled snapshot is not actualtwoSHA0')
 for k in ['strict_registered_tests','source_files','production_files']:need(type(m[k]) is int and m[k]==cm[k],'Root prereg count differs: '+k)
 suite=check(m['full_suite_pin']);buildp=check(m['last_build_pin']);dll=check(m['DLL_pin'])
 for k,p in [('full_suite',suite),('current_build',buildp)]:need(check(cm[k])==p,'Snapshot binds another '+k)
 need(dll==R/'UnrealGame/Binaries/Win64/UnrealEditor-CodexDungeon.dll','Actual editorDLL required');drel=dll.relative_to(R).as_posix();need(drel in files and files[drel]['bytes']==fact(dll)['bytes'] and files[drel]['sha256']==fact(dll)['sha256'],'Compiled DLL pin missing/different')
 strict_suite(read(suite));build=read(buildp);need(build['ExitCode']==0 and build['Target']=='CodexDungeonEditor','Actual successful Editor build required')
 need(dll.stat().st_mtime>=max((R/n).stat().st_mtime for n in source_paths),'DLL older than current Source');need(suite.stat().st_mtime>=dll.stat().st_mtime,'Full190 suite predates current DLL')
 admitted={x['path'].replace('\\','/'):x for x in m['admitted_Death_source_files']};need(set(DEATH_FILES)<=set(admitted) and len(admitted)==len(m['admitted_Death_source_files']),'Death Source/profile/observer interface omitted or duplicate')
 for n,x in admitted.items():need(n in files and files[n]==x,'Admitted Death source not from compiledsnapshot');check(x)
 selected_freezes={}
 for role in ['Death_runtime_candidate_freeze_pin','Death_observer_candidate_freeze_pin']:
  p=check(m[role]);rows_of_freeze(p)
  selected_freezes[role]=p
  for x in read(p)['files']:
   q=Path(x['path']);q=q if q.is_absolute() else p.parent/q
   if not q.is_file() and not Path(x['path']).is_absolute():q=R/x['path']
   if q.resolve().is_relative_to(R/'UnrealGame/Source'):
    rel=q.resolve().relative_to(R).as_posix();need(rel in files and files[rel]['bytes']==x['bytes'] and files[rel]['sha256']==x['sha256'],'Candidate source not actually compiled')
 mapped=set()
 for a in m['candidate_source_admissions']:
  p=selected_freezes[a['candidate_freeze_role']];member=next(x for x in read(p)['files'] if x['path']==a['candidate_member_path']);target=a['actual_source_path'];need(target in admitted and target in files,'Candidate admission target not compiled/admitted');need(member['bytes']==files[target]['bytes'] and member['sha256']==files[target]['sha256'],'ActualSource is not byte-identical to selected candidate member');need(target not in mapped,'Duplicate candidate source admission');mapped.add(target)
 required_new={n for n in DEATH_FILES if Path(n).name not in ['DungeonFighter.h','DungeonFighter.cpp','DungeonHUD.h','DungeonHUD.cpp','DungeonFairytaleSwordPresentation.cpp']}
 need(required_new<=mapped,'NewDeath profile/plan/presentation/observer/tests not bound to actual candidate bytes')
 need(check(m['profile_source_checker_pin'])==GUARD_CHECKER,'Wrong provenKnown44 source checker')
 prereg=check(m['source_profile_prereg_pin']);extension=check(m['production_extension_approval_pin']);p=read(prereg);need(check(p['production_extension_pin'])==extension,'Guard source-profile and extension approvals differ')
 helper=check(m['production_extension_checker_pin']);need(helper==C/'validate-Death1326-production-extension-v001.py','Wrong extension checker');actual,_,_=guard_source_check(snapshot,prereg,helper)
 need(actual==cm,'Guard profile checker bound another compiledsnapshot')
 need(m['Guard_known_unique']==44 and m['Death_imported_textures']==40 and m['Death_flag']=='DungeonFairytaleSwordDeathPreview','Manual scopedart count/flag differs')
 for k in ['automatic_inputs','diagnostic_damage','new_native_capture_claimed','FinalAccepted']:need(m[k] is False,'Manual checkpoint cannot claim injection/native/finalacceptance: '+k)
 need(m['formal_complete_units']==0 and m['debug_range_enabled'] is False and m['traditional_HUD_shown'] is False,'Default hidden/debug-off policy changed')
 for repeat in range(2):
  for folder,names in [('UnrealGame/Source',source_paths),('UnrealGame/Content/Production',prod_paths)]:need({q.relative_to(R).as_posix() for q in (R/folder).rglob('*') if q.is_file()}==names,'Current exact set differs: '+folder)
  for n,x in files.items():check(x)
  for key in ['snapshot_manifest_pin','full_suite_pin','last_build_pin','DLL_pin','checkpoint_tooling_freeze_pin','source_profile_prereg_pin','production_extension_approval_pin','profile_source_checker_pin','production_extension_checker_pin','Death_runtime_candidate_freeze_pin','Death_observer_candidate_freeze_pin']:check(m[key])
 return dict(compiled_inputs_verified=True,strict_registry=190,source_files=cm['source_files'],production_files=1326,Guard_known_unique=44,Death_imported_textures=40,Death_flag=m['Death_flag'],current_live_verification_passes=2,automatic_inputs=False,diagnostic_damage=False,debug_range_enabled=False,traditional_HUD_shown=False,native_or_visual_acceptance=False,UE_started=False)
def self_test():
 import copy
 synthetic={'succeeded':190,'failed':0,'succeededWithWarnings':0,'notRun':0,'inProcess':0,'tests':[dict(fullTestPath=n,state='Success',errors=0,warnings=0,entries=[]) for n in list(DEATH_TESTS)+['HOST_SYNTHETIC_ONLY.'+str(i) for i in range(187)]]}
 strict_suite(synthetic);cases=[]
 for label,change in [('count189',lambda s:s.update(succeeded=189)),('duplicate',lambda s:s['tests'].__setitem__(3,s['tests'][0])),('warning',lambda s:s['tests'][0].update(warnings=1)),('hiddenWarning',lambda s:s['tests'][0].update(entries=[{'event':{'type':'Warning'}}])),('missingDeathTarget',lambda s:s['tests'][0].update(fullTestPath='HOST_SYNTHETIC_ONLY.wrong'))]:
  q=copy.deepcopy(synthetic);change(q)
  try:strict_suite(q)
  except ValueError:cases.append(label)
  else:raise AssertionError('Negativegate accepted '+label)
 for value in [dict(is_template=True,RootApproved=True),dict(is_template=False,RootApproved=False),dict()]:
  try:approval(value)
  except ValueError:pass
  else:raise AssertionError('Template/unapproved gate accepted')
 return dict(host_self_test=True,synthetic_report_only=True,negative_gates=cases,actual190_GREEN_claimed=False,current_Source_or_DLL_checked=False,UE_started=False)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--manual-input');ap.add_argument('--snapshot');ap.add_argument('--self-test',action='store_true');a=ap.parse_args()
 if a.self_test:print(json.dumps(self_test()));return
 need(a.manual_input,'--manual-input realRootprereg required');print(json.dumps(verify(resolve(a.manual_input),a.snapshot)))
if __name__=='__main__':main()
