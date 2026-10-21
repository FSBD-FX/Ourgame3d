from pathlib import Path
import hashlib,json,difflib

ROOT=Path('source-assets/production/fairytale-lgt-readability-v003/walk-runtime-candidate-v001')
OUT=ROOT/'review-20261018-v001/production-repair-v002'
OUT.mkdir(parents=True,exist_ok=True)
source=ROOT/'production-source/DungeonGameMode.cpp'
before=source.read_bytes()
changes=[
 (b'        MotionBatchBodies=Predicted;bSimulatingMotion=true;\n',
  b'        MotionBatchBodies=Predicted;bSimulatingMotion=true;\n'
  b'        // Interval-start eligibility must precede Dodge.StepTo: its final segment\n'
  b'        // still belongs to dodge even when the endpoint changes Dodging to Idle.\n'
  b'        const bool PlayerOrdinaryEligibleAtStart=PlayerFighter->CanAccumulateGroundWalk();\n'),
 (b'        const auto CommitMotion=[Step,FromTime,ToTime,&Predicted](ADungeonFighter* Fighter)\n',
  b'        const auto CommitMotion=[this,Step,FromTime,ToTime,&Predicted,PlayerOrdinaryEligibleAtStart](ADungeonFighter* Fighter)\n'),
 (b'            const bool OrdinaryEligible=Fighter->CanAccumulateGroundWalk();\n',
  b'            const bool OrdinaryEligible=Fighter==PlayerFighter?PlayerOrdinaryEligibleAtStart:Fighter->CanAccumulateGroundWalk();\n'),
]
after=before
for a,b in changes:
 assert after.count(a)==1
 after=after.replace(a,b,1)
candidate=OUT/'DungeonGameMode.cpp'
candidate.write_bytes(after)
patch=''.join(difflib.unified_diff(before.decode().splitlines(True),after.decode().splitlines(True),fromfile='a/UnrealGame/Source/CodexDungeon/DungeonGameMode.cpp',tofile='b/UnrealGame/Source/CodexDungeon/DungeonGameMode.cpp'))
(OUT/'production-repair-v002.patch').write_text(patch,encoding='utf8',newline='')

test=ROOT/'review-20261018-v001/DungeonFairytaleGroundWalkBoundaryTests.cpp'
(OUT/test.name).write_bytes(test.read_bytes())
def pin(p):
 b=p.read_bytes();return {'path':p.as_posix(),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
freeze={'schema':'fairytale-ground-walk-production-repair-v002','reason':'Exclude final dodge displacement using interval-start eligibility before Dodge.StepTo can transition to Idle.',
 'original_production':pin(source),'candidate':pin(candidate),'patch':pin(OUT/'production-repair-v002.patch'),'new_test':pin(OUT/test.name),
 'original_three_tests':pin(ROOT/'new-tests/DungeonFairytaleGroundWalkTests.cpp'),
 'original_three_assertions_unchanged':True,'profile_configured':False,
 'UE_UBT_native_tests_run':False,'actual_source_mutated':False,'original_candidate_mutated':False,
 'new_test_group':'CodexDungeon.Content.FairytaleGroundWalk.Boundaries.DodgeCompletionExcludesFinalSegment',
 'other_interval_boundaries_reviewed':{
   'airborne_landing':'Eligibility now samples prior to motion; JumpHeight/Velocity/Grounded exclude start-airborne interval, and Record also requires P.StartHeight==P.EndHeight==0.',
   'hurt_expiry':'Eligibility samples HurtTime before SimulateMotion decays timer; endpoint expiry cannot count the hurt interval.',
   'legacy_armor_expiry':'Eligibility samples ArmorChangeRemaining before SimulateMotion decrements it.',
   'equipment_cancel':'Fresh/held input cancellation occurs at start boundary in UpdatePlayerInput before this eligibility sample, so subsequent normal movement is allowed; active uncancelled transaction remains excluded.',
   'primary_skill_completion':'Combat/WA actions advance after CommitMotion; active interval-start action remains excluded.',
   'endpoint_skill_step':'Separate skill placement occurs after motion/action consumption; witness discontinuity checks reject publication if endpoint changes.'},
 'status':'CANDIDATE_REQUIRES_ROOT_ADMISSION_REAL_COMPILE_AND_TEST'}
(OUT/'freeze-v002.json').write_text(json.dumps(freeze,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps(freeze,ensure_ascii=False,indent=2))
