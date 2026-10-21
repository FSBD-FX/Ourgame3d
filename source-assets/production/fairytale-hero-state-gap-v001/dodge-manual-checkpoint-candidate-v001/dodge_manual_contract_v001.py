"""Bounded Dodge manual Source/test contracts. No writes or UE."""
from pathlib import Path
import ast,hashlib,json,runpy
R=Path('F:/Ourgame').resolve();HERE=Path(__file__).resolve().parent
P='UnrealGame/Source/CodexDungeon/'
STAGE_NEW={P+n for n in ['DungeonDodgePresentation.h','DungeonFairytaleSwordDodgeProfile.h','DungeonFairytaleSwordDodgeProfile.cpp','DungeonFairytaleSwordDodgePlan.h','DungeonFairytaleSwordDodgePlan.cpp','DungeonFairytaleSwordDodgeDrawState.h','Tests/DungeonFairytaleSwordDodgeV001Tests.cpp']}
COMMON={P+n for n in ['DungeonFighter.h','DungeonFighter.cpp','DungeonHUD.h','DungeonHUD.cpp','DungeonFairytaleSwordPresentation.cpp']}
PROD_NEW={P+n for n in ['DungeonFairytaleSwordDodgePresentation.cpp','DungeonFairytaleSwordDodgeTextures.inl']}
OBSERVER_NEW={P+n for n in ['DungeonHeroDodgeProbeV001.h','DungeonHeroDodgeProbeV001.cpp']}
DODGE_TESTS=tuple('CodexDungeon.Content.FairytaleSwordDodgeV001.'+n for n in ['RealShiftDoubleClockFourPhasesAndInterrupts','RealBindingSource32NineSlotsMirrorAndAtomicRejection','RealCodecPausedActiveActionKeepsClockAndGear'])
OLD=R/'source-assets/production/fairytale-guard-v001/Stomp50-manual-checkpoint-candidate-v001'
IMPORT=R/'source-assets/production/fairytale-hero-state-gap-v001/dodge-import-candidate-v001'

def need(v,why):
 if not v:raise ValueError(why)
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def resolve(p):
 p=Path(p);p=(p if p.is_absolute() else R/p).resolve();need(p.is_relative_to(R),'Project path required');return p
def pin(p):
 p=resolve(p);b=p.read_bytes();return dict(path=p.as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def check(x):
 p=resolve(x['path']);a=pin(p);need((a['bytes'],a['sha256'])==(x['bytes'],x['sha256']),'Pin changed: '+str(p));return p
def frozen(p):
 p=resolve(p)
 for x in read(p)['files']:
  q=Path(x['path']);q=q if q.is_absolute() else p.parent/q
  if not q.exists():q=R/x['path']
  a=pin(q);need((a['bytes'],a['sha256'])==(x['bytes'],x['sha256']),'Frozen member changed: '+str(q))
def inputs():
 d=read(HERE/'immutable-v139-input-pins-v001.json')
 for x in d['files'].values():check(x)
 frozen(check(d['files']['v010_freeze']));frozen(check(d['files']['Dodge_importer_freeze']))
 return d['files']
def old_api():return runpy.run_path(str(OLD/'verify-Stomp1332-manual-input-v001.py'))

def apply_chain(base,receipts):
 expected=dict(base)
 need([r for r,_ in receipts]==['stage0','production','observer'],'Exact three ordered Dodge admissions required')
 for role,d in receipts:
  need('dodge' in d['schema'].lower() and role in d['schema'].lower(),'Typed Dodge role receipt required')
  need(d['success'] is True and d['FinalAccepted'] is False and d['unaffected_Source_unchanged'] is True,'Actual bounded Source admission required')
  need(d['previous_Source_count']==len(expected),'Receipt skipped/reordered Source baseline')
  admitted={x['path']:x for x in d['admitted']};need(len(admitted)==len(d['admitted']),'Duplicate Source admission')
  previous={x['path']:x for x in d['previous']};need(len(previous)==len(d['previous']),'Duplicate previous pin')
  new=set(admitted)-set(expected);changed=set(admitted)&set(expected)
  if role=='stage0':
   need(set(admitted)==STAGE_NEW|{P+'DungeonFighter.h',P+'DungeonFighter.cpp',P+'DungeonHUD.h'} and new==STAGE_NEW,'Stage0 exact7+three existing interfaces required')
  elif role=='production':
   need(new==PROD_NEW and set(admitted)<=(STAGE_NEW-{P+'Tests/DungeonFairytaleSwordDodgeV001Tests.cpp'})|PROD_NEW|COMMON,'Production changed tests or a non-Dodge/kernel module')
  else:need(new==OBSERVER_NEW and set(admitted)==OBSERVER_NEW|{P+'DungeonHUD.cpp'},'Observer must only add Probe2 and narrow HUD startup')
  need(set(previous)==changed and all(previous[n]==expected[n] for n in changed),'Source previous pins do not bind exact prior stage')
  expected.update(admitted);need(d['Source_count']==len(expected),'Source count differs from actual admitted map')
 return expected

def preserve193(suite,old_names,new_names):
 need(len(old_names)==193 and len(new_names)==3 and not old_names&new_names,'Exact prior193 plus independent three targets required')
 need(type(suite.get('succeeded')) is int and suite['succeeded']==196,'Full196 required')
 need(all(type(suite.get(k)) is int and suite[k]==0 for k in ['failed','succeededWithWarnings','notRun','inProcess']),'Suite has non-green counters')
 ts=suite['tests'];names=[x['fullTestPath'] for x in ts]
 need(len(names)==len(set(names))==196 and set(names)==old_names|new_names,'Prior193 targets missing/replaced/duplicated')
 for x in ts:need(x['state']=='Success' and type(x['errors']) is int and x['errors']==0 and type(x['warnings']) is int and x['warnings']==0 and not any(e.get('event',{}).get('type') in ['Error','Warning'] for e in x.get('entries',[])),'Test is not strict Success')

def source_chain(m,files):
 deps=inputs();base=read(check(deps['base_v139_snapshot']))
 expected={x['path']:x for x in base['files'] if x['path'].startswith('UnrealGame/Source/')}
 need(len(expected)==base['source_files']==262,'Wrong real v139 baseline')
 roles=[]
 for role in ['stage0','production','observer']:
  d=read(check(m['Dodge_'+role+'_Source_admission_pin']));frozen(check(d['candidate_freeze']));roles.append((role,d))
  if role=='stage0':need(check(d['candidate_freeze'])==check(deps['Dodge_stage0_freeze']),'Stage0 admission does not bind exact frozen seven-interface candidate')
 expected=apply_chain(expected,roles)
 actual={n:x for n,x in files.items() if n.startswith('UnrealGame/Source/')}
 need(actual==expected,'Current Source not exact v139 plus three bounded Dodge admissions')
 for x in actual.values():check(x)
 return expected

def core_adapter():
 deps=inputs();old=check(deps['v009_checker']);tree=ast.parse(old.read_text(encoding='utf-8-sig'))
 class Bounded(ast.NodeTransformer):
  def visit_Constant(self,n):
   if type(n.value)is int and n.value in [190,1326]:return ast.copy_location(ast.Constant({190:196,1326:1364}[n.value]),n)
   names={'Death1326-manual-tooling-freeze-v001.json':'Dodge1364-manual-tooling-freeze-v001.json','Death1326-Root-manual-input-v001':'Dodge1364-Root-manual-input-v001','validate-Death1326-production-extension-v001.py':'validate-Dodge1364-production-extension-v001.py'}
   if type(n.value)is str and n.value in names:return ast.copy_location(ast.Constant(names[n.value]),n)
   return n
 scope={'__file__':str(HERE/'verify-Dodge1364-manual-input-v001.py'),'__name__':'Dodge1364_bounded_core'}
 exec(compile(ast.fix_missing_locations(Bounded().visit(tree)),str(old),'exec'),scope);scope['C']=HERE
 return scope

def runtime_trial(m,cm):
 deps=inputs();d=read(check(m['Dodge_runtime_trial_registration_pin']))
 need(d['schema']=='Root-Dodge33-runtime-trial-registration-v001' and d['is_template'] is False and d['RootApproved'] is True,'Root actual runtime trial registration required')
 need(d['compiled_manifest_sha256']==pin(check(m['snapshot_manifest_pin']))['sha256'],'Runtime trial binds another compiled snapshot')
 need(d['flag']=='DungeonFairytaleSwordDodgePreview' and d['profile_id']=='EV048-v018-HeroLeatherDodge-v001' and d['prepared_profile_pin']==deps['Dodge_prepared_profile'],'Runtime exact profile/flag differs')
 need(d['resource_preload_total']==33 and d['declared_draw_slots']==9 and d['TrialAllowed'] is True and d['FinalAccepted'] is False,'Limited Dodge33/nine-slot trial gate differs')
 need(d['manual_source_only'] is True and d['actual_GPU_preload_receipt'] is None,'Manual source gate cannot claim GPU or native proof')
 frozen(check(d['runtime_candidate_freeze_pin']))
 production=read(check(m['Dodge_production_Source_admission_pin']))
 need(check(d['runtime_candidate_freeze_pin'])==check(production['candidate_freeze']),'Runtime trial does not bind admitted production candidate')
 return d
