#if WITH_DEV_AUTOMATION_TESTS
#include "Misc/AutomationTest.h"
#include "../DungeonFairytaleGuardPose.h"

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FGuardVisualTerminalMaterialReview,
 "CodexDungeon.Content.FairytaleGuardPresentation.TerminalDeathMaterialClockReview",
 EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FGuardVisualTerminalMaterialReview::RunTest(const FString&)
{
 namespace G=DungeonStoneGuard;namespace P=DungeonFairytaleGuard;
 G::FGuardKernel K(88004);G::FWorldInput W;W.HasTarget=true;W.Target={150.,0.,0.};
 W.CanStartAttack=false;W.Sweep=[](const G::FSweepRequest&){return G::FSweepResult{};};
 if(!TestTrue(TEXT("Real native kernel admits Wake before the clock-freeze observation"),
  K.BeginCombat()&&K.StepTo(0.,W).Accepted&&K.StepTo(.5,W).Accepted))return false;
 if(!TestTrue(TEXT("Real ordinary one HP loss remains living Waking, not a forged hurt/death state"),
  K.ApplyResolvedHit(1,1.,0.,W).Accepted&&K.State().HP==184.&&K.State().Phase==G::EPhase::Waking))return false;
 const auto AliveSaved=K.Capture();const auto Alive=P::Select(K.State());const auto AliveLate=P::Select(K.State(),2.);
 if(!TestTrue(TEXT("A supplied terminal age cannot advance alive Wake or expire its frozen native material clock"),
  Alive.Valid&&Alive.Clip==P::EClip::Wake&&Alive.Frame==3&&Alive.MaterialHit
  &&AliveLate.Clip==Alive.Clip&&AliveLate.Frame==Alive.Frame&&AliveLate.MaterialHit==Alive.MaterialHit
  &&AliveLate.MaterialEventId==Alive.MaterialEventId&&!AliveLate.TerminalPresentation
  &&AliveLate.SampleTime==AliveSaved.Time&&K.State().Time==AliveSaved.Time
  &&K.State().NextEventId==AliveSaved.NextEventId&&K.State().HP==AliveSaved.HP))return false;
 if(!TestTrue(TEXT("Real lethal remaining HP loss creates native unique Died at the same frozen boundary"),
  K.ApplyResolvedHit(2,184.,0.,W).Accepted&&K.State().HP==0.&&K.State().Phase==G::EPhase::Dead))return false;
 const auto DeadSaved=K.Capture();uint64 DiedId=0;int32 DiedCount=0;
 for(const auto& E:DeadSaved.Issued)if(E.Kind==G::EEventKind::Died){DiedId=E.EventId;++DiedCount;}
 if(!TestTrue(TEXT("Genuine death has exactly one original event and frozen native Time"),
  DiedCount==1&&DiedId>0&&DeadSaved.Time==.5))return false;
 const auto Initial=P::Select(K.State(),0.);const auto Warm=P::Select(K.State(),.219);
 if(!TestTrue(TEXT("Initial lethal tint is visible only during its original finite .22 display interval"),
  Initial.Valid&&Initial.Clip==P::EClip::Death&&Initial.Frame==0&&Initial.MaterialHit
  &&Warm.Clip==P::EClip::Death&&Warm.MaterialHit&&Warm.SourceEventId==DiedId))return false;
 const auto Expired=P::Select(K.State(),.22);
 // First RED witness on the frozen v001 production selector: its S.Time-based
 // tint remains warm forever even while the same real death row advances.
 if(!TestTrue(TEXT("Terminal .22 endpoint expires lethal material tint while native Time stays frozen"),
  Expired.Valid&&Expired.Clip==P::EClip::Death&&!Expired.MaterialHit&&Expired.MaterialEventId==0
  &&Expired.SourceEventId==DiedId&&Expired.TerminalPresentation&&Expired.SampleTime==DeadSaved.Time
  &&K.State().Time==DeadSaved.Time&&K.State().NextEventId==DeadSaved.NextEventId))return false;
 const auto Corpse=P::Select(K.State(),.8);const auto Held=P::Select(K.State(),2.);
 if(!TestTrue(TEXT("Frozen native death reaches and holds its actual final visual frame without restarting tint"),
  Corpse.Clip==P::EClip::Death&&Corpse.Frame==5&&!Corpse.MaterialHit
  &&Held.Clip==P::EClip::Death&&Held.Frame==5&&!Held.MaterialHit
  &&Held.SourceEventId==DiedId&&Held.SampleTime==DeadSaved.Time))return false;
 G::FGuardKernel Restored(88004);
 if(!TestTrue(TEXT("Actual native Restore accepts the genuine saved death history"),Restored.Restore(DeadSaved)))return false;
 const auto RestoredHeld=P::Select(Restored.State(),2.);
 TestTrue(TEXT("Restored same-event corpse stays final and clear without any new event, kernel tick or damage"),
  RestoredHeld.Clip==Held.Clip&&RestoredHeld.Frame==Held.Frame&&!RestoredHeld.MaterialHit
  &&RestoredHeld.MaterialEventId==0&&RestoredHeld.SourceEventId==DiedId
  &&Restored.State().Time==DeadSaved.Time&&Restored.State().NextEventId==DeadSaved.NextEventId
  &&Restored.State().HP==DeadSaved.HP&&Restored.State().ReceivedHits.size()==DeadSaved.ReceivedHits.size());
 return true;
}
#endif
