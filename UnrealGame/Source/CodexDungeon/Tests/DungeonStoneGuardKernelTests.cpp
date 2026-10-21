#if WITH_DEV_AUTOMATION_TESTS
#include "Misc/AutomationTest.h"
#include "../DungeonStoneGuard.h"
#include "StoneGuardKernelTestOracle.h"
#include <cmath>
#include <limits>
using namespace DungeonStoneGuard;
namespace StoneGuardAutomation
{
FWorldInput World(double X=150,double Y=0,double Z=0)
{FWorldInput W;W.HasTarget=true;W.Target={X,Y,Z};W.Sweep=[](const FSweepRequest&){return FSweepResult{};};return W;}
int Count(const FResult& R,EEventKind K){int N=0;for(const auto& E:R.Events)N+=E.Kind==K;return N;}
bool Awake(FAutomationTestBase& T,FGuardKernel& K,FWorldInput W=World())
{
 const auto A=K.StepTo(K.State().Time,W);
 if(!T.TestTrue(TEXT("Actual proximity starts warning"),A.Accepted&&Count(A,EEventKind::WakeStarted)==1))return false;
 const auto B=K.StepTo(K.State().WakeEnd,W);
 return T.TestTrue(TEXT("Full warning reaches awake idle"),B.Accepted&&K.State().Phase==EPhase::Idle);
}
bool Start(FAutomationTestBase& T,FGuardKernel& K,EAttack A,FWorldInput W)
{return T.TestTrue(TEXT("Real accepted attack starts once"),K.TryStartAttack(A,W).Accepted);}
bool Near(double A,double B){return std::abs(A-B)<1e-9;}
}
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDungeonStoneGuardWakeAndSchedules,
 "CodexDungeon.Content.StoneGuardKernel.WakeAndAuthoredSchedules",
 EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FDungeonStoneGuardWakeAndSchedules::RunTest(const FString& Parameters)
{
 (void)Parameters;using namespace StoneGuardAutomation;
 const auto D=FGuardKernel::Definition();
 TestTrue(TEXT("Guard has authored distinct large profile"),D.HP==185&&D.Armor==60&&D.Ward==15&&D.Poise==85&&D.MoveSpeed==160&&D.BodyHalfX==40&&D.BodyHalfY==28&&D.HurtHalfX==40&&D.HurtHalfY==28);
 FGuardKernel K(301);auto W=World();if(!Awake(*this,K,W)||!Start(*this,K,EAttack::AxeSweep,W))return false;
 TestTrue(TEXT("Axe exact warning lock and accepted-start cooldown"),K.State().Action.LockAt==1.5&&K.State().Action.ActiveAt==2&&Near(K.State().Action.ActiveEnd,2.2)&&Near(K.State().Action.RecoveryEnd,3.6)&&Near(K.State().AxeReadyAt,4.1));
 W.Target={-150,0,0};auto R=K.StepTo(1.5,W);TestTrue(TEXT("Half windup locks left exactly once"),R.Accepted&&Count(R,EEventKind::AimLocked)==1&&K.State().Action.Facing==-1);
 W.Target={150,0,0};R=K.StepTo(2,W);TestTrue(TEXT("Postlock target cannot drag attack right"),R.Accepted&&Count(R,EEventKind::ActiveWindow)==1&&K.State().Windows.size()==1&&K.State().Windows.front().Facing==-1);
 const auto Window=K.State().Windows.front();R=K.StepTo(K.State().Action.RecoveryEnd,W);
 TestTrue(TEXT("Large frame owns full recovery and one completion"),R.Accepted&&Count(R,EEventKind::RecoveryStarted)==1&&Count(R,EEventKind::AttackCompleted)==1&&K.State().Phase==EPhase::Idle);
 TestTrue(TEXT("Window immutable after completion"),K.State().Windows.front().Start==Window.Start&&K.State().Windows.front().End==Window.End&&K.State().Windows.front().Facing==Window.Facing);
 TestTrue(TEXT("No replay at equal clock"),K.StepTo(K.State().Time,W).Events.empty());
 TestFalse(TEXT("Other kind cannot bypass minimum idle gap"),K.TryStartAttack(EAttack::Stomp,World(50)).Accepted);
 K.StepTo(K.State().IdleReadyAt,World(50));TestTrue(TEXT("Stomp may start only when shared recovery and idle gap done"),K.TryStartAttack(EAttack::Stomp,World(50)).Accepted);
 const auto A=K.State().Action;TestTrue(TEXT("Stomp exact schedule and own center"),Near(A.LockAt,A.Start+.45)&&Near(A.ActiveAt,A.Start+.9)&&Near(A.ActiveEnd,A.ActiveAt+.15)&&Near(A.RecoveryEnd,A.ActiveEnd+1.5)&&A.CooldownEnd==A.Start+3);
 FGuardKernel F(302);TestTrue(TEXT("Explicit combat arms fallback once"),F.BeginCombat()&&!F.BeginCombat());R=F.StepTo(12,World(900));TestTrue(TEXT("12 second fallback retains full one second warning"),R.Accepted&&F.State().WakeStartedAt==12&&F.State().WakeEnd==13&&!F.State().Awakened);
 return true;
}
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDungeonStoneGuardGeometryAndCancellation,
 "CodexDungeon.Content.StoneGuardKernel.GeometryAndCancellation",
 EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FDungeonStoneGuardGeometryAndCancellation::RunTest(const FString& Parameters)
{
 (void)Parameters;using namespace StoneGuardAutomation;
 for(int Face:{-1,1})
 {
  FGuardKernel K(Face<0?311:312);auto W=World(Face*150.);if(!Awake(*this,K,W)||!Start(*this,K,EAttack::AxeSweep,W))return false;K.StepTo(K.State().Action.ActiveAt,W);
  TestTrue(TEXT("Left/right rectangle exact endpoint and height"),K.TryHit({500,{Face*180.,65,65}}).Accepted);
  TestFalse(TEXT("Same target not hit every frame"),K.TryHit({500,{Face*180.,65,65}}).Accepted);
  TestFalse(TEXT("Rear excluded"),K.TryHit({501,{-Face*1.,0,0}}).Accepted);
  TestFalse(TEXT("Range not inflated by target hurt box"),K.TryHit({501,{Face*180.0001,0,0}}).Accepted);
  TestFalse(TEXT("Actual jump height above65 avoids low attack"),K.TryHit({501,{Face*100.,0,65.001}}).Accepted);
  auto T=FTarget{501,{Face*100.,0,0}};T.LOS=false;TestFalse(TEXT("Wall LOS prevents hit"),K.TryHit(T).Accepted);T.LOS=true;T.Invulnerable=true;TestFalse(TEXT("Invulnerable target does not consume hit"),K.TryHit(T).Accepted);T.Invulnerable=false;TestTrue(TEXT("Admission failure left receipt unconsumed"),K.TryHit(T).Accepted);
  const auto Window=K.State().Windows.front();auto R=K.StepTo(2.1,W,{{1,2.1,1,85}});
  TestTrue(TEXT("Break closes active through independent receipt"),R.Accepted&&Count(R,EEventKind::PoiseBroken)==1&&K.State().Closures.size()==1&&K.State().Closures.front().AtTime==2.1);
  TestTrue(TEXT("Issued window not rewritten on interruption"),K.State().Windows.front().End==Window.End&&K.State().Windows.front().Start==Window.Start);
  TestFalse(TEXT("No postbreak active damage"),K.TryHit({502,{Face*100.,0,0}}).Accepted);
 }
 FGuardKernel S(313);auto W=World(0,80);if(!Awake(*this,S,W)||!Start(*this,S,EAttack::Stomp,W))return false;S.StepTo(S.State().Action.ActiveAt,World(600));
 TestTrue(TEXT("Stomp single own-center emission survives target exit"),S.State().Windows.size()==1&&S.State().Windows.front().Center.X==0&&S.State().Windows.front().Center.Y==0);
 TestTrue(TEXT("Ellipse side endpoint admitted"),S.TryHit({510,{0,90,0}}).Accepted);TestFalse(TEXT("Ellipse not bounding rectangle"),S.TryHit({511,{160,90,0}}).Accepted);
 S.StepTo(S.State().Action.ActiveEnd,W);TestTrue(TEXT("End exclusive becomes counterwindow"),S.CounterWindowOpen()&&!S.TryHit({512,{0,0,0}}).Accepted);
 return true;
}
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDungeonStoneGuardAtomicClockDeathAndObligations,
 "CodexDungeon.Content.StoneGuardKernel.AtomicClockDeathAndObligations",
 EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FDungeonStoneGuardAtomicClockDeathAndObligations::RunTest(const FString& Parameters)
{
 (void)Parameters;using namespace StoneGuardAutomation;using StoneGuardKernelTestOracle::Signature;
 FGuardKernel K(321);auto W=World();if(!Awake(*this,K,W)||!Start(*this,K,EAttack::AxeSweep,W))return false;
 const auto Before=Signature(K.Capture());TestFalse(TEXT("Rewind rejected"),K.StepTo(.5,W).Accepted);TestTrue(TEXT("Rewind all-value atomic"),Signature(K.Capture())==Before);
 TestFalse(TEXT("NaN clock rejected"),K.StepTo(std::numeric_limits<double>::quiet_NaN(),W).Accepted);TestTrue(TEXT("NaN all-value atomic"),Signature(K.Capture())==Before);
 TestFalse(TEXT("Duplicate incoming receipts reject entire batch"),K.StepTo(2,W,{{1,1.5,1,0},{1,1.8,1,0}}).Accepted);TestTrue(TEXT("Batch failure full-state atomic"),Signature(K.Capture())==Before);
 auto R=K.StepTo(3,W,{{1,2,185,100},{2,2.5,10,85}});
 TestTrue(TEXT("Death at active boundary suppresses window and later second death"),R.Accepted&&Count(R,EEventKind::Died)==1&&Count(R,EEventKind::ActiveWindow)==0&&Count(R,EEventKind::PoiseBroken)==0&&K.State().ReceivedHits.size()==2&&K.State().ReceivedHits.back().ActualHPLoss==0);
 TestFalse(TEXT("Corpse body no longer blocks"),K.GroundBodyEnabled());TestTrue(TEXT("One death eligibility without invented fixed gold"),K.ClaimDeathReward().Accepted&&!K.ClaimDeathReward().Accepted);
 const auto Dead=Signature(K.Capture());TestFalse(TEXT("Same-ID reset cannot erase reward receipt"),K.ResetForNewEntity(321,3));TestTrue(TEXT("Reset rejection atomic"),Signature(K.Capture())==Dead);
 FGuardKernel H(322);if(!Awake(*this,H,W)||!Start(*this,H,EAttack::AxeSweep,W))return false;const double End=H.State().Action.RecoveryEnd;
 R=H.StepTo(4,W,{{1,3.5,1,85}});bool Exact=false;for(const auto& E:R.Events)if(E.Kind==EEventKind::AttackCompleted)Exact=E.AtTime==End;
 TestTrue(TEXT("Break straddling recovery never drops or delays completion"),R.Accepted&&Count(R,EEventKind::AttackCompleted)==1&&Exact&&H.State().Action.CompletedAt==End&&H.State().Phase==EPhase::Idle);
 FGuardKernel B(323);if(!Awake(*this,B))return false;const auto Idle=Signature(B.Capture());W=World(600,100);W.Sweep=[](const FSweepRequest&){return FSweepResult{true,2,EStop::Wall};};
 TestFalse(TEXT("Invalid native-query result rejected"),B.StepTo(2,W).Accepted);TestTrue(TEXT("Query failure leaves events and time untouched"),Signature(B.Capture())==Idle);
 return true;
}
#endif
