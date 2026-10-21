#if WITH_DEV_AUTOMATION_TESTS
#include "Misc/AutomationTest.h"
#include "../DungeonFairytaleGuardPose.h"
#include "../DungeonFairytaleGuardProfile.h"
namespace
{
namespace G=DungeonStoneGuard;namespace P=DungeonFairytaleGuard;
G::FWorldInput GuardVisualWorld(double X=150.)
{G::FWorldInput W;W.HasTarget=true;W.Target={X,0,0};W.Sweep=[](const G::FSweepRequest&){return G::FSweepResult{};};return W;}
}
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FGuardVisualNativeClock,
 "CodexDungeon.Content.FairytaleGuardPresentation.NativeClockMaterialAndDeath",
 EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FGuardVisualNativeClock::RunTest(const FString&)
{
 G::FGuardKernel K(88001);auto W=GuardVisualWorld();
 if(!TestTrue(TEXT("Actual kernel begins genuine Wake"),K.BeginCombat()&&K.StepTo(0.,W).Accepted))return false;
 auto R=P::Select(K.State());
 if(!TestTrue(TEXT("Stage0: actual Wake selects Wake0 rather than Ready"),R.Valid&&R.Clip==P::EClip::Wake&&R.Frame==0))return false;
 for(const double T:{.167,.333,.5,.667,.833})
 {if(!K.StepTo(T,W).Accepted)return false;R=P::Select(K.State());TestTrue(TEXT("Wake phase derives from actual immutable WakeStarted / WakeEnd"),R.Clip==P::EClip::Wake&&R.IntervalStart==0.&&R.IntervalEnd==1.);}
 TestEqual(TEXT("Actual Wake .833 selects final authored phase"),R.Frame,5);
 if(!K.ApplyResolvedHit(1,1.,0.,W).Accepted)return false;R=P::Select(K.State());
 TestTrue(TEXT("Ordinary actual 1HP receipt only permits material tint, never Stunned pose"),R.Clip==P::EClip::Wake&&R.MaterialHit&&R.MaterialEventId>0);
 if(!K.StepTo(1.,W).Accepted||!K.TryStartAttack(G::EAttack::AxeSweep,W).Accepted)return false;
 const auto A=K.State().Action;if(!K.StepTo(A.ActiveAt,W).Accepted)return false;R=P::Select(K.State());
 TestTrue(TEXT("Actual native active boundary owns follow frame0, not a private timer"),R.Clip==P::EClip::AxeFollow&&R.Frame==0&&R.IntervalStart==A.ActiveAt);
 if(!K.StepTo(A.ActiveEnd,W).Accepted)return false;R=P::Select(K.State());
 TestTrue(TEXT("Actual ActiveEnd owns first recovery frame2"),R.Clip==P::EClip::AxeFollow&&R.Frame==2&&R.IntervalEnd==A.RecoveryEnd);
 if(!K.ApplyResolvedHit(2,184.,0.,W).Accepted||!K.StepTo(K.State().Time+1.5,W).Accepted)return false;R=P::Select(K.State());
 TestTrue(TEXT("Real Died clock completes six phases and holds final frame without delaying gameplay"),R.Clip==P::EClip::Death&&R.Frame==5&&R.SourceEventId>0);
 const auto Saved=K.Capture();G::FGuardKernel Copy(88001);
 if(!TestTrue(TEXT("Actual native Restore accepts complete genuine death history"),Copy.Restore(Saved)))return false;
 const auto B=P::Select(Copy.State());TestTrue(TEXT("Repeated read/restore cannot invent another event or restart death"),B.Clip==R.Clip&&B.Frame==R.Frame&&B.SourceEventId==R.SourceEventId&&Copy.State().NextEventId==Saved.NextEventId);
 return true;
}
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FGuardVisualAcceptedDistance,
 "CodexDungeon.Content.FairytaleGuardPresentation.Accepted128DistanceAndBlocked",
 EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FGuardVisualAcceptedDistance::RunTest(const FString&)
{
 G::FGuardKernel K(88002);auto W=GuardVisualWorld(450.);W.CanStartAttack=false;
 if(!K.BeginCombat()||!K.NotifyOtherAcceptedEnemiesCleared()||!K.StepTo(0.,W).Accepted)return false;
 const double Distance[]={2.,24.,46.,68.,90.,112.,134.};const int32 Expected[]={0,1,2,3,4,5,0};P::FSelection R;
 for(int32 I=0;I<7;++I)
 {
  if(!TestTrue(TEXT("Actual central kernel accepts movement boundary"),K.StepTo(1.+Distance[I]/160.,W).Accepted))return false;R=P::Select(K.State());
  if(!TestTrue(TEXT("Stage0: only accepted native path advances exact 128world six-phase cycle"),R.Valid&&R.Clip==P::EClip::Move&&R.Frame==Expected[I]
    &&FMath::IsNearlyEqual(R.AcceptedDistance,Distance[I],1.e-8)))return false;
 }
 const double Before=R.AcceptedDistance;W.Target=K.State().Position;
 if(!K.StepTo(K.State().Time+.5,W).Accepted)return false;R=P::Select(K.State());
 TestTrue(TEXT("Stopped positive wall time owns Ready and unchanged accepted path"),R.Clip==P::EClip::Ready&&R.AcceptedDistance==Before);
 W.Target={450,0,0};W.Sweep=[](const G::FSweepRequest&){return G::FSweepResult{true,0.,G::EStop::Wall};};
 if(!K.StepTo(K.State().Time+.1,W).Accepted)return false;R=P::Select(K.State());
 TestTrue(TEXT("Real zero-distance wall receipt cannot select Move or advance gait"),R.Clip==P::EClip::Ready&&R.AcceptedDistance==Before);
 return true;
}
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FGuardVisualInterruptAndRows,
 "CodexDungeon.Content.FairytaleGuardPresentation.InterruptedDeadlineAndPartialRows",
 EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FGuardVisualInterruptAndRows::RunTest(const FString&)
{
 G::FGuardKernel K(88003);auto W=GuardVisualWorld();K.BeginCombat();
 if(!K.StepTo(1.,W).Accepted||!K.TryStartAttack(G::EAttack::AxeSweep,W).Accepted)return false;
 const auto A=K.State().Action;
 if(!K.StepTo(A.ActiveAt-.1,W).Accepted||!K.ApplyResolvedHit(1,1.,85.,W).Accepted)return false;
 auto R=P::Select(K.State());
 if(!TestTrue(TEXT("Stage0: genuine poise85 owns Stunned0, never early interrupted recovery"),R.Valid&&R.Clip==P::EClip::Stunned&&R.Frame==0))return false;
 const double Until=K.State().StunUntil;TestTrue(TEXT("Native stun lasts actual .4"),FMath::IsNearlyEqual(Until-K.State().Time,.4,1.e-12));
 if(!K.StepTo(Until,W).Accepted)return false;R=P::Select(K.State());
 TestTrue(TEXT("Recovery starts only after Stun; original occupied deadline remains"),R.Clip==P::EClip::InterruptedRecovery&&R.Frame==0&&R.IntervalStart==Until&&R.IntervalEnd==A.RecoveryEnd);
 if(!K.StepTo(A.RecoveryEnd,W).Accepted)return false;R=P::Select(K.State());
 TestTrue(TEXT("No new active window and no extended interrupted interval"),R.Clip!=P::EClip::InterruptedRecovery&&K.State().Windows.empty()&&K.State().HitReceipts.empty());
 // Actual compiled profile is read-only. Default partial trial needs an explicit Root record.
 for(const auto& Row:P::Profile())
 {
  TestTrue(TEXT("Native211 can never be registered by this candidate"),Row.NativeSourceId!=211);
  if(Row.TrialAllowed)TestTrue(TEXT("Any Root trial opt-in has a concrete approval record"),!Row.TrialApprovalRecord.IsEmpty());
 }
 const auto* Ready=P::FindRow(P::EClip::Ready);const auto* Wake=P::FindRow(P::EClip::Wake);const auto* Axe=P::FindRow(P::EClip::AxeWindup);
 if(!TestTrue(TEXT("Exact measured source registration proposals exist independently per row"),Ready&&Wake&&Axe))return false;
 TestTrue(TEXT("Body-only ONE row scale stays 100.8 / 415, 398, 273"),Ready->Scale()==100.8/415.&&Wake->Scale()==100.8/398.&&Axe->Scale()==100.8/273.);
 const int32 ReadyX[]={235,234,244,236};for(int32 I=0;I<4;++I)
 {
  R.Valid=true;R.Clip=P::EClip::Ready;R.Frame=I;R.Facing=1;const auto Right=P::Plan(R);
  R.Facing=-1;const auto Left=P::Plan(R);
  TestTrue(TEXT("Production geometry uses per-frame measured support mirrored around width"),Right.DisplayPivotX==ReadyX[I]
    &&Left.DisplayPivotX==512.-ReadyX[I]&&Right.SourcePivot.Y==464.&&Left.SourcePivot.Y==464.);
  TestTrue(TEXT("Fixed axe wholebody plan contains exactly one source layer, no separate weapon/grips"),Right.WholebodyLayers.Num()==1
    &&Left.WholebodyLayers.Num()==1&&Right.WholebodyLayers[0]==Ready->Frames[I].TexturePath&&Left.WholebodyLayers[0]==Right.WholebodyLayers[0]);
 }
 // No synthetic texture/profile override: inspect real missing Move / follow row policy.
 R.Valid=true;R.Clip=P::EClip::Move;R.Frame=3;R.Facing=1;const auto Missing=P::Plan(R);
 TestTrue(TEXT("Missing Move remains Move with explicit gap and zero sprite layers; never Ready"),Missing.AssetClip==P::EClip::Move&&!Missing.Valid&&!Missing.MissingReason.IsEmpty()&&Missing.WholebodyLayers.IsEmpty());
 R.Clip=P::EClip::Dormant;R.Frame=0;const auto Dormant=P::Plan(R);
 TestTrue(TEXT("Dormant is an explicit Wake0 asset alias even when trial gate closed"),Dormant.AssetClip==P::EClip::Wake&&Dormant.Frame==0);
 TestTrue(TEXT("Dormant shares exactly one Wake0 source layer; registration gate does not invent a distinct frame"),Dormant.WholebodyLayers.Num()==1&&Dormant.WholebodyLayers[0]==Wake->Frames[0].TexturePath);
 return true;
}
#endif
