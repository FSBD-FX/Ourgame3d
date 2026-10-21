"""Read-only preparation checks. No native acceptance/checkpoint outputs."""
from pathlib import Path
import ast,copy,json,re,runpy,subprocess,argparse
from move7_manual_contract_v001 import *

def reject(fn):
 try:fn()
 except(ValueError,KeyError,TypeError,FileNotFoundError):return True
 raise AssertionError('Invalid input accepted')
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--output');args=parser.parse_args()
 checks=[]
 def ck(label,v):need(v,label);checks.append(label)
 deps=inputs()
 for p in HERE.glob('*.py'):ast.parse(p.read_text(encoding='utf-8-sig'));checks.append('Python AST '+p.name)
 old=read(check(deps['v011_manual']));cm=read(check(deps['green_snapshot']));files={x['path']:x for x in cm['files']}
 prereg=R/'docs/production/first-batch-v2/evidence/GuardMove7-v141-v001/root-native-prereg-v003/Root-Move7-left-prereg-v001.json'
 m=copy.deepcopy(old);m['Move7_native_prereg_pins']={'left':pin(prereg)}
 result=source_chain(m,files);ck('actual historical Dodge273 plus typed five receipt Source283',len(result)==283)
 suite=read(check(cm['full_suite']));projected=project196(suite);ck('current strict200 preserves exact old196',projected['succeeded']==196)
 d=dodge.inputs();base193=read(check(d['base193_full_suite']));preserve193(suite,{x['fullTestPath']for x in base193['tests']},set(DODGE_TESTS));checks.append('old193 plus Dodge3 registry gate retained')
 for label,edit in [('missingMove',lambda s:s['tests'].__setitem__(next(i for i,x in enumerate(s['tests'])if x['fullTestPath']in move.TESTS),s['tests'][0])),('warning',lambda s:s['tests'][0].update(warnings=1)),('hiddenerror',lambda s:s['tests'][0].update(entries=[{'event':{'type':'Error'}}])),('old196counter',lambda s:s.update(succeeded=196))]:
  bad=copy.deepcopy(suite);edit(bad);ck('reject '+label,reject(lambda:project196(bad)))
 ck('reject unapproved manual template',reject(lambda:verify(HERE/'Root-Move7-manual-input-TEMPLATE-NOT-APPROVED-v001.json')))
 fresh=R/'docs/production/first-batch-v2/evidence/GuardMove7-v141-v001/root-native-prereg-geometry-v003/Root-Move7-left-prereg-v001.json'
 freshdoc=read(fresh);ck('actual fresh supplemental prereg binds frozen repair',supplemental(freshdoc))
 for key in['proof_geometry_repair_freeze_pin','proof_geometry_repair_checker_pin']:
  bad=copy.deepcopy(freshdoc);bad.pop(key);ck('reject absent supplemental '+key,reject(lambda:supplemental(bad)))
  bad=copy.deepcopy(freshdoc);bad[key]['sha256']='0'*64;ck('reject changed supplemental '+key,reject(lambda:supplemental(bad)))
 ck('old v001 prereg cannot bypass supplemental repair',reject(lambda:supplemental(read(prereg))))
 core=core_adapter();ck('retained core requires Death tests and full200',set(core['DEATH_TESTS'])==set(dodge.core_adapter()['DEATH_TESTS'])and len(core['strict_suite'](suite))==200)
 # Run every original asset gate on current real1371 with only real saved7
 # projected. The historical Root1364 approval is read unchanged; no synthetic
 # approved extension/Root checkpoint is created by this host preparation test.
 api=runpy.run_path(str(HERE/'validate-Move7-production-extension-v001.py'))
 extra=api['move_extra'](files,pin(prereg),check(deps['green_snapshot']).parent)
 preregold=read(check(old['source_profile_prereg_pin']));guardreceipt=read(check(preregold['actual_native_import_receipt_pin']));guardmanifest=read(check(guardreceipt['manifest']))
 base1254={check(x).relative_to(R).as_posix()for x in guardmanifest['old_production_files']}|{check(x['saved']).relative_to(R).as_posix()for x in guardreceipt['assets']}
 historical=api['historical_dodge_validate'](base1254,files,extra,deps['green_snapshot']['sha256'])
 ck('all actual old asset gates pass exact saved7 projection',historical['total']==1364 and len(extra)==7 and len(base1254)==1254)
 # Explicit supplement is pending. No native success/visual acceptance is
 # inferred from these Source/asset checks or from the failed first archive.
 oldps=check(deps['v011_launcher']).read_text(encoding='utf-8-sig');newps=(HERE/'launch-guard-room-native-trial-v012.ps1').read_text(encoding='utf-8-sig')
 oldflags=set(re.findall(r"'(-Dungeon[^']+)'",oldps));newflags=set(re.findall(r"'(-Dungeon[^']+)'",newps))
 ck('all old launch flags retained plus only Move7',newflags==oldflags|{'-DungeonFairytaleGuardMoveRigPreview'})
 ck('manual launch no proof/autoinput/diagnostics',not any(x in newps for x in['-DungeonContentProof','-DungeonGuardMoveProof','-DungeonGuardMoveApproachSide','-unattended','-ExecCmds','-DungeonCombatRangeDebug']))
 ck('ValidateOnly returns before GetProcess/StartProcess/log creation',newps.index('if($ValidateOnly)')<newps.index('Get-Process')<newps.index('$log=')<newps.index('Start-Process'))
 astps=subprocess.run(['pwsh','-NoProfile','-Command',"$tokens=$null;$errors=$null;[void][Management.Automation.Language.Parser]::ParseFile('"+(HERE/'launch-guard-room-native-trial-v012.ps1').as_posix()+"',[ref]$tokens,[ref]$errors);if($errors.Count){$errors|Out-String;exit 1};'PowerShell AST pass'"],capture_output=True,text=True)
 ck('PowerShell AST parser clean',astps.returncode==0)
 result=dict(schema='Move7-manual-v012-host-preparation-checks-v001',passed=True,checks=checks,check_count=len(checks),actual_Source283_typed_chain_verified=True,actual_Production1371_with_original1364_gates_verified=True,strict_registry200_verified=True,native_passed_claimed=False,Root_visual_review_claimed=False,Root_checkpoint_created=False,UE_started=False,actual_tools_Source_Content_E_ledger_written=False,FinalAccepted=False)
 if args.output:
  output=Path(args.output).resolve();need(output.is_relative_to(HERE),'Candidate-only host output required')
  with output.open('x',encoding='utf-8')as f:json.dump(result,f,ensure_ascii=False,indent=2);f.write('\n')
 print(json.dumps(result,ensure_ascii=False))
if __name__=='__main__':main()
