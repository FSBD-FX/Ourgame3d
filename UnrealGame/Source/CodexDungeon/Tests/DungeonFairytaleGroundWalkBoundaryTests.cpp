#if WITH_DEV_AUTOMATION_TESTS
#include "Misc/AutomationTest.h"
#include "../DungeonCompletedGroundMotion.h"
#include "../DungeonDodge.h"
#include "RunCodecFixture_v001.h"
#include <limits>

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FFairytaleWalkDodgeCompletionExclusion,
 "CodexDungeon.Content.FairytaleGroundWalk.Boundaries.DodgeCompletionExcludesFinalSegment",
 EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FFairytaleWalkDodgeCompletionExclusion::RunTest(const FString&)
{
 FCodecWorld W(*this);
 if(!TestTrue(TEXT("Real bound Scene and safe normal-input dodge start"),W.Create()&&W.Move(-920.,true)
  &&W.Key(EKeys::D,true)&&W.Key(EKeys::LeftShift,true)))return false;
 W.Frame(.005f);
 if(!TestTrue(TEXT("Fresh actual Shift starts a genuine active dodge"),
  W.Player->GetDodgeState().Phase==DungeonDodge::EPhase::Dodging&&!W.Player->GetDodgeState().Records.empty()))return false;
 if(!W.Key(EKeys::LeftShift,false))return false;
 const double End=W.Player->GetDodgeState().Records.back().End;
 if(!TestTrue(TEXT("Advance through real held D to just before original dodge completion"),W.AdvanceTo(End-.003)))return false;
 const double BeforeTime=W.Game->GetSimulationTime();const auto BeforePosition=W.Player->GetGroundPosition();
 if(!TestTrue(TEXT("Final interval begins while dodge still owns movement"),
  W.Player->GetDodgeState().Phase==DungeonDodge::EPhase::Dodging&&BeforeTime<End))return false;
 float FinalDt=float(End-BeforeTime);
 if(double(FinalDt)<End-BeforeTime)FinalDt=std::nextafter(FinalDt,std::numeric_limits<float>::infinity());
 W.Frame(FinalDt);
 FDungeonCompletedGroundMotion M;
 if(!TestTrue(TEXT("Actual completed frame publishes owner-bound endpoint witness"),W.Player->QueryCompletedGroundMotion(M)))return false;
 const auto& D=W.Player->GetDodgeState();
 TestTrue(TEXT("Same genuine dodge completes at its promised deadline without reset"),D.Phase==DungeonDodge::EPhase::Idle
  &&D.Records.back().Finish==DungeonDodge::EFinish::Completed&&D.Records.back().FinishedAt==End&&W.Game->GetSimulationTime()>=End);
 TestTrue(TEXT("Accepted endpoint displacement includes the positive final dodge segment"),M.From==BeforePosition
  &&M.To==W.Player->GetGroundPosition()&&M.FromTime==BeforeTime&&M.ToTime==W.Game->GetSimulationTime()
  &&M.AcceptedDistance>.1&&FMath::IsNearlyEqual(M.AcceptedDistance,(M.To-M.From).Size(),1.e-7));
 // Float Tick input may exceed End by <1 float ulp. Only that ordinary tail
 // can contribute; the positive pre-End dodge displacement must stay excluded.
 const double MaximumOrdinaryTail=FMath::Max(0.,M.ToTime-End)*double(W.Player->GetMoveSpeed());
 TestTrue(TEXT("Idle endpoint cannot reclassify final dodge displacement as WalkDistance"),!M.OrdinaryEligible
  &&M.WalkDistance>=0.&&M.WalkDistance<=MaximumOrdinaryTail+1.e-6&&M.WalkDistance<M.AcceptedDistance-.1);
 if(!W.Key(EKeys::D,false))return false;
 W.Frame(.005f);FDungeonRunSnapshot S;FString Why;
 TestTrue(TEXT("Completed action boundary remains capturable after genuine input release"),W.Game->CaptureRunSnapshot(S,Why));
 return true;
}
#endif
