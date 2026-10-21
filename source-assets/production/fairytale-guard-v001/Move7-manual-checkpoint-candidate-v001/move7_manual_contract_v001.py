"""v012 read-only gates: preserve v011 and add the exact typed Move7 chain."""
from pathlib import Path
import ast,copy,hashlib,json,runpy,sys
R=Path('F:/Ourgame').resolve();HERE=Path(__file__).resolve().parent
OLD=R/'source-assets/production/fairytale-hero-state-gap-v001/dodge-manual-checkpoint-candidate-v001'
MOVE=R/'source-assets/production/fairytale-guard-v001/Move7-native-observer-candidate-v001/tool-contract-fix-v002'
sys.path.insert(0,str(OLD));import dodge_manual_contract_v001 as dodge
sys.path.insert(0,str(MOVE/'tooling'));import move7_native_contract_v001 as move
need=dodge.need;read=dodge.read;resolve=dodge.resolve;pin=dodge.pin;check=dodge.check
STAGE_NEW=dodge.STAGE_NEW;PROD_NEW=dodge.PROD_NEW;OBSERVER_NEW=dodge.OBSERVER_NEW;COMMON=dodge.COMMON
DODGE_TESTS=dodge.DODGE_TESTS
MANUAL_SCHEMA='Move7-Root-manual-input-v001';FREEZE_NAME='Move7-manual-tooling-freeze-v001.json'

def inputs():
 d=read(HERE/'immutable-input-pins-v001.json')['files']
 extra=read(HERE/'proof-geometry-repair-input-pins-v001.json')['files']
 need(set(extra)=={'Move7_proof_geometry_freeze','Move7_proof_geometry_checker','Move7_proof_geometry_contract'}and not set(extra)&set(d),'Only named supplemental proof pins permitted');d.update(extra)
 for x in d.values():check(x)
 dodge.inputs();dodge.frozen(check(d['v011_freeze']));move.frozen(check(d['Move7_tool_contract_freeze']))
 repair=check(d['Move7_proof_geometry_freeze']);move.frozen(repair)
 need(read(repair)['schema']=='Move7-proof-geometry-repair-freeze-v003'and pin(repair)['sha256']=='c8713135fc0a98f4b06cb63a2dbe7166f0deccf469a66a636da4083d3c7298de','Only exact separately frozen numeric proof repair permitted')
 need(read(repair)['old_tool_contract_fix_freeze_pin']==d['Move7_tool_contract_freeze']and read(repair)['old_tool_contract_fix_checker_pin']==d['Move7_source_oracle'],'Numeric repair must preserve old typed tool milestone pins')
 return d

def proof_api():return runpy.run_path(str(check(inputs()['Move7_proof_geometry_contract'])))

def supplemental(p,independent=None,session=None):
 deps=inputs()
 for key,dep in [('proof_geometry_repair_freeze_pin','Move7_proof_geometry_freeze'),('proof_geometry_repair_checker_pin','Move7_proof_geometry_checker')]:
  need(key in p and move.equalpin(p[key],deps[dep]),'Missing or foreign supplemental proof lineage: '+key)
  if independent is not None:need(key in independent and move.equalpin(independent[key],p[key]),'Independent supplemental proof lineage differs: '+key)
 if session is not None:
  need(session['proof_geometry_repair_freeze_sha256']==p['proof_geometry_repair_freeze_pin']['sha256']and session['proof_geometry_repair_checker_sha256']==p['proof_geometry_repair_checker_pin']['sha256'],'Session supplemental proof lineage differs')
 return True

def project196(suite):
 # Only the exact four independently added Move7 targets are projected out.
 # The full200 gate separately rejects missing/duplicate/failed targets.
 old=read(check(inputs()['base_v140_snapshot']));old_suite=read(check(old['full_suite']))
 names={x['fullTestPath']for x in old_suite['tests']}
 move.strict_suite(suite,names|move.TESTS)
 projected=copy.deepcopy(suite);projected['tests']=[x for x in suite['tests']if x['fullTestPath']not in move.TESTS]
 projected.update(succeeded=196)
 need(len(projected['tests'])==196 and {x['fullTestPath']for x in projected['tests']}==names,'Exact unchanged old196 projection differs')
 return projected

def preserve193(suite,old_names,new_names):return dodge.preserve193(project196(suite),old_names,new_names)
def old_api():return dodge.old_api()
def runtime_trial(m,cm):return dodge.runtime_trial(m,cm)

def source_chain(m,files):
 deps=dodge.inputs();base=read(check(deps['base_v139_snapshot']))
 expected={x['path']:x for x in base['files']if x['path'].startswith('UnrealGame/Source/')}
 need(len(expected)==base['source_files']==262,'Wrong genuine v139 source baseline')
 roles=[]
 for role in ['stage0','production','observer']:
  receipt=read(check(m['Dodge_'+role+'_Source_admission_pin']));dodge.frozen(check(receipt['candidate_freeze']));roles.append((role,receipt))
  if role=='stage0':need(check(receipt['candidate_freeze'])==check(deps['Dodge_stage0_freeze']),'Dodge Stage0 frozen candidate differs')
 expected=dodge.apply_chain(expected,roles)
 v140=read(check(inputs()['base_v140_snapshot']))
 base273={x['path']:x for x in v140['files']if x['path'].startswith('UnrealGame/Source/')}
 need(expected==base273 and len(expected)==273,'Historical Dodge three-step chain is not exact compiled v140273')
 left=read(check(m['Move7_native_prereg_pins']['left']));expected=move.source_chain(left,v140)
 need({n:x for n,x in files.items()if n.startswith('UnrealGame/Source/')}==expected,'Current Source is not exact Dodge273 plus typed five-stage Move7 chain')
 for x in expected.values():check(x)
 return expected

def core_adapter():
 # Retain the complete original Death/Hurt/Known44 verifier. Only final
 # registry/Production, schema, own-freeze and extension-helper identity change.
 deps=dodge.inputs();old=check(deps['v009_checker']);tree=ast.parse(old.read_text(encoding='utf-8-sig'))
 class Bounded(ast.NodeTransformer):
  def visit_Constant(self,n):
   if type(n.value)is int and n.value in[190,1326]:return ast.copy_location(ast.Constant({190:200,1326:1371}[n.value]),n)
   names={'Death1326-manual-tooling-freeze-v001.json':FREEZE_NAME,'Death1326-Root-manual-input-v001':MANUAL_SCHEMA,'validate-Death1326-production-extension-v001.py':'validate-Move7-production-extension-v001.py'}
   if type(n.value)is str and n.value in names:return ast.copy_location(ast.Constant(names[n.value]),n)
   return n
 scope={'__file__':str(HERE/'verify-Move7-manual-input-v001.py'),'__name__':'Move7_bounded_manual_core'}
 exec(compile(ast.fix_missing_locations(Bounded().visit(tree)),str(old),'exec'),scope);scope['C']=HERE
 return scope

def inherited_verify(path,snapshot=None):
 # Execute the frozen v011 function, preserving all its statements except its
 # two final result count literals. Its named seams above have narrow extensions.
 old=check(inputs()['v011_checker']);tree=ast.parse(old.read_text(encoding='utf-8-sig'))
 fn=next(x for x in tree.body if isinstance(x,ast.FunctionDef)and x.name=='verify')
 class Counts(ast.NodeTransformer):
  def visit_Constant(self,n):
   if type(n.value)is int and n.value in[196,1364]:return ast.copy_location(ast.Constant({196:200,1364:1371}[n.value]),n)
   return n
 scope=dict(globals());exec(compile(ast.fix_missing_locations(ast.Module(body=[Counts().visit(fn)],type_ignores=[])),str(old),'exec'),scope)
 return scope['verify'](path,snapshot)

def native_evidence(m,cm):
 deps=inputs();visual=read(check(m['Move7_Root_visual_review_pin']))
 need(visual['schema']=='Root-GuardMove7-native-and-visible-review-v141-v001'and visual['is_template']is False and visual['RootApproved']is True and visual['FinalAccepted']is False and visual['limited_manual_trial_allowed']is True,'Actual limited Root native/visual review required')
 need(move.equalpin(visual['compiled_manifest_pin'],m['snapshot_manifest_pin']),'Root visual review binds another build')
 for k in['actual_both_facings_viewed','actual_six_distance_windows_viewed','actual_adjacent_joins_viewed','both_complete_silent_videos_viewed']:need(visual[k]is True,'Root visual review incomplete: '+k)
 need({x['side']for x in visual['native']}=={-1,1}and len(visual['native'])==2,'Root review must bind exactly two actual sides')
 evidence=[]
 for name,side in [('left',-1),('right',1)]:
  prereg=check(m['Move7_native_prereg_pins'][name]);manifest,p,profile,imp,trial=proof_api()['preflight'](resolve(m['snapshot_directory']),prereg)
  supplemental(p)
  need(move.equalpin(m['Move7_proof_geometry_repair_freeze_pin'],p['proof_geometry_repair_freeze_pin'])and move.equalpin(m['Move7_proof_geometry_repair_checker_pin'],p['proof_geometry_repair_checker_pin']),'Manual supplemental proof lineage differs')
  need(manifest==cm and p['approach_side']==side,'Manual side prereg/current build differs')
  archive=resolve(m['Move7_native_archives'][name]);receipt_path=archive/'原件/Move7-independent-native-verification-v001.json'
  independent=read(check(m['Move7_independent_native_pins'][name]));report_path=archive/'原件/runtime-report.json';report=read(report_path);session_path=archive/'index.json';session=read(session_path)
  need(check(m['Move7_independent_native_pins'][name])==receipt_path,'Independent receipt is not from the selected original archive')
  need(independent['schema']=='guard-Move7-independent-native-v001'and independent['passed']is True and report['passed']is True and session['independent_passed']is True and session['exit_code']==0,'Actual native and independent verification must both pass')
  need(independent['process_id']==int(report['process_id'])==session['process_id']and independent['actual_facing']==p['approach_side']==side,'Independent native PID/side differs')
  need(move.equalpin(independent['native_report_pin'],move.fact(report_path))and session['snapshot_manifest_sha256']==m['snapshot_manifest_pin']['sha256']and session['root_prereg_sha256']==move.fact(prereg)['sha256'],'Actual native report/prereg/current compiled pin differs')
  need(move.equalpin(independent['tool_contract_fix_freeze_pin'],p['tool_contract_fix_freeze_pin'])and move.equalpin(independent['tool_contract_fix_checker_pin'],p['tool_contract_fix_checker_pin']),'Native verifier derivative differs from prereg')
  supplemental(p,independent,session)
  need(independent['accepted_cycle_distance']>=128. and independent['six_distance_window_mask']==63 and independent['complete7GPU_and_submitted_floatquads']is True and independent['original_clock_and_source_projection']is True and independent['native_PNG_CRC_FIFO_verified']is True and independent['optical_source_projection']['passed']is True,'Actual full cycle/resource/source/optical evidence incomplete')
  need([x['kind']for x in independent['actual_adjacent_joins']]==['Move7_to_native_Windup','native_Recovery_to_Ready_stop'],'Actual combat/Ready native joins incomplete')
  need(report['guard_final_HP']==185 and report['guard_incoming_count']==0 and report['requested_approach_side']==report['actual_approach_side']==side,'Native Guard185/no incoming/real side differs')
  for k in['Hurt_Stun_native_covered','historical_block_cause_verified','footlock','audio_recorded','visual_reviewed','FinalAccepted']:need(independent[k]is False,'Independent scope falsely expanded: '+k)
  expected=dict(side=side,archive=archive.as_posix(),report_pin=move.fact(report_path),independent_pin=move.fact(receipt_path),prereg_pin=move.fact(prereg),session_pin=move.fact(session_path),process_id=int(report['process_id']))
  actual=next(x for x in visual['native']if x['side']==side)
  need(actual==expected,'Root visual review must bind exact native/archive/prereg/session bytes')
  retained=m['Move7_native_evidence_files'][name];need(len({x['path']for x in retained})==len(retained),'Repeated native evidence member')
  need({resolve(x['path'])for x in retained}=={x.resolve()for x in archive.rglob('*')if x.is_file()},'Native archive members added/removed since Root manual registration')
  for _ in range(2):
   for x in retained:check(x)
  evidence.append(expected)
 need(evidence[0]['process_id']!=evidence[1]['process_id'],'Both sides must be distinct actual UE processes')
 return evidence

def verify(path,snapshot=None):
 m=read(resolve(path));need(m.get('schema')==MANUAL_SCHEMA and m.get('is_template')is False and m.get('RootApproved')is True,'Actual non-template Root Move7 manual checkpoint required')
 inputs();result=inherited_verify(resolve(path),snapshot);cm=read(check(m['snapshot_manifest_pin']))
 need(cm['source_files']==283 and cm['production_files']==1371 and cm['strict_registered_tests']==200,'Current bounded283/1371/200 checkpoint required')
 required=move.STAGE|move.INTERFACE|{move.FOURTH}|move.PROD_ALLOWED|move.PROBE
 admitted=m['admitted_Move7_source_files'];current={x['path']:x for x in cm['files']}
 need(len(admitted)==len({x['path']for x in admitted})and{x['path']for x in admitted}==required,'Exact Move7 presentation/query/frozen-test/observer interface list required')
 for x in admitted:need(current.get(x['path'])==x,'Move7 admitted interface is not current compiled bytes');check(x)
 native=native_evidence(m,cm)
 need(m['Move7_flag']=='DungeonFairytaleGuardMoveRigPreview'and m['Move7_parts']==m['Move7_required_resources']==7 and m['Move7_presentation_type']=='GuardMoveSevenComponentRigDerived','Move7 typed manual scope differs')
 need(m['completed_combinations']==m['formal_complete_units']==0 and m['Move7_leg_occlusion_outline_accepted']is False,'Manual checkpoint cannot certify units/contact/leg outlines')
 result.update(Move7_parts=7,Move7_required_resources=7,Move7_flag=m['Move7_flag'],actual_two_native_sides_bound=True,limited_Root_visible_review_bound=True,footlock=False,FinalAccepted=False)
 return result
