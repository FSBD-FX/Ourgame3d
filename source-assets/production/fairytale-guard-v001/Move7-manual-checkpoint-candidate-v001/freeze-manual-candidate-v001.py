"""Freeze only this NEW manual candidate; never creates an adopted checkpoint."""
from pathlib import Path
import ast,copy,json,subprocess
from move7_manual_contract_v001 import *
def write(p,d):
 with p.open('x',encoding='utf-8')as f:json.dump(d,f,ensure_ascii=False,indent=2);f.write('\n')
deps=inputs();cm=read(check(deps['green_snapshot']));source=[x for x in cm['files']if x['path'].startswith('UnrealGame/Source/')]
need(len(source)==283,'Actual compiled Source283 required')
for _ in range(2):
 for x in source:check(x)
for p in HERE.glob('*.py'):ast.parse(p.read_text(encoding='utf-8-sig'))
for p in HERE.glob('*.ps1'):
 cmd="$tokens=$null;$errors=$null;[void][Management.Automation.Language.Parser]::ParseFile('"+p.as_posix()+"',[ref]$tokens,[ref]$errors);if($errors.Count){$errors|Out-String;exit 1}"
 r=subprocess.run(['pwsh','-NoProfile','-Command',cmd],capture_output=True,text=True);need(r.returncode==0,'PowerShell parse failed: '+p.name)
# Execute the exact newly added interface-list block against real CM pins,
# without constructing a Root-approved manual document or touching native data.
tree=ast.parse((HERE/'move7_manual_contract_v001.py').read_text(encoding='utf-8-sig'));fn=next(x for x in tree.body if isinstance(x,ast.FunctionDef)and x.name=='verify')
start=next(i for i,x in enumerate(fn.body)if isinstance(x,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='required'for t in x.targets))
stop=next(i for i,x in enumerate(fn.body)if isinstance(x,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='native'for t in x.targets))
segment=ast.Module(body=fn.body[start:stop],type_ignores=[]);code=compile(ast.fix_missing_locations(segment),'<exact candidate Move7 interface block>','exec')
required=move.STAGE|move.INTERFACE|{move.FOURTH}|move.PROD_ALLOWED|move.PROBE;files={x['path']:x for x in cm['files']};base={'admitted_Move7_source_files':[copy.deepcopy(files[n])for n in sorted(required)]}
def execute(m):exec(code,dict(globals(),m=m,cm=cm))
execute(base);negative=[]
for label,edit in [('missing',lambda m:m['admitted_Move7_source_files'].pop()),('duplicate',lambda m:m['admitted_Move7_source_files'].append(m['admitted_Move7_source_files'][0])),('wronghash',lambda m:m['admitted_Move7_source_files'][0].update(sha256='0'*64)),('extra',lambda m:m['admitted_Move7_source_files'].append(files['UnrealGame/Source/CodexDungeon/DungeonStoneGuard.h']))]:
 bad=copy.deepcopy(base);edit(bad)
 try:execute(bad)
 except(ValueError,KeyError,TypeError):negative.append(label)
 else:raise ValueError('Interface negative gate accepted: '+label)
log=HERE/'ValidateOnly-template-rejection-v001.log';need(not log.exists(),'Fresh rejection log required')
run=subprocess.run(['pwsh','-NoProfile','-File',str(HERE/'launch-guard-room-native-trial-v012.ps1'),'-RootCheckpoint',str(HERE/'Root-Move7-manual-input-TEMPLATE-NOT-APPROVED-v001.json'),'-LightArtTrial','-GuardFullArt','-ValidateOnly'],capture_output=True,text=True,encoding='utf-8')
log.write_text(run.stdout+run.stderr,encoding='utf-8');need(run.returncode!=0 and 'Actual non-template Root Move7 manual checkpoint required'in(run.stdout+run.stderr),'Template ValidateOnly must reject before any UE launch')
final=HERE/'final-structural-checks-v002.json'
write(final,dict(schema='Move7-manual-final-structural-checks-v002',passed=True,all_python_AST=True,both_PowerShell_AST=True,exact_final_interface_block_executed_on_actual_CM=True,interface_negatives_rejected=negative,ValidateOnly_template_rejected=True,ValidateOnly_rejection_log=pin(log),actual_Source283_verified_twice=True,actual_Source_mismatches=0,actual_checkpoint_or_native_receipt_created=False,UE_started=False))
host=read(HERE/'host-validation-v001.json');review=read(HERE/'independent-review-v001.json')
need(host['passed']and host['check_count']==25 and not host['native_passed_claimed']and review['review_complete']and not review['blocking_findings'],'Required host/static reviews incomplete')
out=HERE/FREEZE_NAME;need(not out.exists(),'Candidate freeze already exists')
members=[pin(p)for p in sorted(HERE.rglob('*'))if p.is_file()and p!=out]
for _ in range(2):
 for x in members:check(x)
write(out,dict(schema='Move7-manual-v012-candidate-freeze-v001',candidate_only=True,actual_tools_Source_Content_E_ledger_CMD_written=False,actual_Root_checkpoint_created=False,actual_native_passed_receipt_created=False,actual_Root_visual_review_created=False,UE_started=False,expected_Source=283,expected_Production=1371,expected_strict_registry=200,compiled_manifest_pin=deps['green_snapshot'],proof_geometry_repair_freeze_pin=deps['Move7_proof_geometry_freeze'],proof_geometry_repair_checker_pin=deps['Move7_proof_geometry_checker'],old_tool_contract_fix_checker_pin=deps['Move7_source_oracle'],old_tool_contract_fix_freeze_pin=deps['Move7_tool_contract_freeze'],host_validation_pin=pin(HERE/'host-validation-v001.json'),final_structural_validation_pin=pin(final),independent_review_pin=pin(HERE/'independent-review-v001.json'),files=[dict(x,path=Path(x['path']).relative_to(HERE).as_posix())for x in members],member_count=len(members),verification_passes=2,hash_mismatches=0,actual_Source_verification_passes=2,actual_Source_hash_mismatches=0,FinalAccepted=False,formal_complete_units=0,completed_combinations=0,Root_gate='Closed until two actual independently passed fresh native sides and exact Root visual review are supplied; helper never invents those inputs'))
print(json.dumps(dict(freeze=pin(out),members=len(members),hash_mismatches=0,actual_Root_checkpoint_created=False,UE_started=False),ensure_ascii=False))
