#if WITH_DEV_AUTOMATION_TESTS
#include "Misc/AutomationTest.h"
#include "StoneGuardOwnerFixture_v002.h"
#include "../DungeonFairytaleGuardFullProfileV003.h"
#include "../DungeonFairytaleGuardProfile.h"
#include "../DungeonStoneGuardFeedback.h"
namespace
{
namespace G=DungeonStoneGuard;namespace F=DungeonFairytaleGuardFullV003;namespace L=DungeonFairytaleGuard;
G::FWorldInput FullWorld(double X=150.)
{G::FWorldInput W;W.HasTarget=true;W.Target={X,0,0};W.Sweep=[](const G::FSweepRequest&){return G::FSweepResult{};};return W;}
bool NativeAttack(G::FGuardKernel& K,G::FWorldInput& W,G::EAttack Kind)
{return K.BeginCombat()&&K.StepTo(0.,W).Accepted&&K.StepTo(1.,W).Accepted&&K.TryStartAttack(Kind,W).Accepted;}
}
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FGuardFullNativeSplit,
 "CodexDungeon.Content.FairytaleGuardFullV003.NativeAxe4Recovery4AndStomp6_2_4",
 EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FGuardFullNativeSplit::RunTest(const FString&)
{
 G::FGuardKernel K(93001);auto W=FullWorld(-150.);
 if(!TestTrue(TEXT("Actual native kernel starts left-facing axe after real Wake"),NativeAttack(K,W,G::EAttack::AxeSweep)))return false;
 const auto A=K.State().Action;
 if(!K.StepTo(A.ActiveAt,W).Accepted)return false;auto S=F::SelectFull(K.State());
 if(!TestTrue(TEXT("Stage0: actual Axe Active owns its own four-frame row and original .2 interval"),S.Valid&&S.Clip==F::EClip::AxeActive&&S.Frame==0&&S.IntervalStart==A.ActiveAt&&S.IntervalEnd==A.ActiveEnd&&S.Facing==-1&&S.SourceEventId>0))return false;
 const double Active[]={0.,.05,.1,.15};
 for(int32 I=0;I<4;++I)
 {
  if(!K.StepTo(A.ActiveAt+Active[I],W).Accepted)return false;S=F::SelectFull(K.State());
  TestTrue(TEXT("v005 actual Active samples0/50/100/150ms select four phases without extending window"),S.Clip==F::EClip::AxeActive&&S.Frame==I&&S.IntervalEnd==A.ActiveEnd&&S.Facing==-1);
  if(I==1){const auto Body=F::PlanFull(S);TestTrue(TEXT("Actual left-facing Active1 has exactly one fixed-axe source layer and mirrored measured floor"),Body.AssetClip==F::EClip::AxeActive&&Body.Frame==1&&Body.WholebodyLayers.Num()==1&&Body.SourcePivot==FVector2D(190.,463.)&&Body.DisplayPivotX==322.);}

 }
 const double Recovery[]={0.,.35,.7,1.05};
 for(int32 I=0;I<4;++I)
 {
  if(!K.StepTo(A.ActiveEnd+Recovery[I],W).Accepted)return false;S=F::SelectFull(K.State());
  TestTrue(TEXT("ActiveEnd switches to separate Recovery0; all four350ms phases retain original1.4 end"),S.Clip==F::EClip::AxeRecovery&&S.Frame==I&&S.IntervalStart==A.ActiveEnd&&S.IntervalEnd==A.RecoveryEnd&&S.SourceEventId>0);
 }
 const auto Before=GuardOwnerTests::StateSig(K.State());for(int32 I=0;I<8;++I)F::SelectFull(K.State());
 TestTrue(TEXT("Read-only full selection cannot emit/replay a window or mutate any native producer history"),Before==GuardOwnerTests::StateSig(K.State())&&K.State().Windows.size()==1&&K.State().HitReceipts.empty());
 if(!K.StepTo(A.RecoveryEnd,W).Accepted)return false;TestTrue(TEXT("Original RecoveryEnd exits row with unchanged idle/cooldown gates"),F::SelectFull(K.State()).Clip==F::EClip::Ready&&K.State().IdleReadyAt==A.RecoveryEnd+.3&&K.State().AxeReadyAt==A.CooldownEnd);
 G::FGuardKernel T(93002);auto TW=FullWorld(55.);
 if(!TestTrue(TEXT("Fresh actual extremely-close native policy starts Stomp"),NativeAttack(T,TW,G::EAttack::Stomp)))return false;const auto B=T.State().Action;
 const double Windup[]={0.,.15,.3,.45,.6,.75};for(int32 I=0;I<6;++I)
 {if(!T.StepTo(B.Start+Windup[I],TW).Accepted)return false;S=F::SelectFull(T.State());TestTrue(TEXT("Real Stomp Windup6 holds original900ms / .45 lock"),S.Clip==F::EClip::StompWindup&&S.Frame==I&&S.IntervalEnd==B.ActiveAt);}
 for(int32 I=0;I<2;++I)
 {if(!T.StepTo(B.ActiveAt+double(I)*.075,TW).Accepted)return false;S=F::SelectFull(T.State());TestTrue(TEXT("Stomp actual .15 active owns exactly two75ms phases"),S.Clip==F::EClip::StompActive&&S.Frame==I&&S.IntervalStart==B.ActiveAt&&S.IntervalEnd==B.ActiveEnd);}
 const double StompRecovery[]={0.,.375,.75,1.125};for(int32 I=0;I<4;++I)
 {if(!T.StepTo(B.ActiveEnd+StompRecovery[I],TW).Accepted)return false;S=F::SelectFull(T.State());TestTrue(TEXT("Consistent v005 Stomp Recovery uses four375ms phases to actual1.5 end"),S.Clip==F::EClip::StompRecovery&&S.Frame==I&&S.IntervalEnd==B.RecoveryEnd);}
 TestTrue(TEXT("Split art rows never fabricate second native damage window"),T.State().Windows.size()==1&&T.State().Windows[0].Kind==G::EAttack::Stomp&&T.State().HitReceipts.empty());
 return true;
}
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FGuardFullMotionInterrupt,
 "CodexDungeon.Content.FairytaleGuardFullV003.AcceptedPath128AndOriginalInterruptedInterval",
 EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FGuardFullMotionInterrupt::RunTest(const FString&)
{
 G::FGuardKernel K(93003);auto W=FullWorld(450.);W.CanStartAttack=false;
 if(!K.BeginCombat()||!K.NotifyOtherAcceptedEnemiesCleared()||!K.StepTo(0.,W).Accepted)return false;
 DungeonGuardFeedback::FJournal Journal;if(!Journal.Begin(K.State()))return false;
 const double D[]={2.,24.,46.,68.,90.,112.,134.};const int32 Expected[]={0,1,2,3,4,5,0};F::FSelection S;
 for(int32 I=0;I<7;++I)
 {
  const auto B=K.StepTo(1.+D[I]/160.,W);if(!B.Accepted||!Journal.Observe(B.Events,K.State().Position))return false;S=F::SelectFull(K.State());
  if(!TestTrue(TEXT("Stage0: full Move six phases derive only from accepted native128world path"),S.Valid&&S.Clip==F::EClip::Move&&S.Frame==Expected[I]&&FMath::IsNearlyEqual(S.AcceptedDistance,D[I],1.e-8)))return false;
 }
 int32 Steps=0;for(const auto& E:Journal.Entries())if(E.Cue==DungeonGuardFeedback::ECue::Step)++Steps;
 TestEqual(TEXT("Existing real journal emits only64/128world contacts3/0; selection adds no sound"),Steps,2);
 const auto LegacyMove=L::Select(K.State());const auto LegacyPlan=L::Plan(LegacyMove);
 TestTrue(TEXT("Legacy v001 missing-Move assertion remains true; full data never expands partial profile"),LegacyMove.Clip==L::EClip::Move&&!LegacyPlan.Valid&&LegacyPlan.AssetClip==L::EClip::Move&&LegacyPlan.WholebodyLayers.IsEmpty());
 const double Before=S.AcceptedDistance;W.Target=K.State().Position;if(!K.StepTo(K.State().Time+.5,W).Accepted)return false;S=F::SelectFull(K.State());
 TestTrue(TEXT("Stopped elapsed native time selects Ready and cannot advance gait"),S.Clip==F::EClip::Ready&&S.AcceptedDistance==Before);
 W.Target={450.,0.,0.};W.Sweep=[](const G::FSweepRequest&){return G::FSweepResult{true,0.,G::EStop::Wall};};if(!K.StepTo(K.State().Time+.1,W).Accepted)return false;S=F::SelectFull(K.State());
 TestTrue(TEXT("Collision blocked zero path cannot select Move"),S.Clip==F::EClip::Ready&&S.AcceptedDistance==Before);
 G::FGuardKernel I(93004);auto IW=FullWorld();if(!NativeAttack(I,IW,G::EAttack::AxeSweep))return false;const auto A=I.State().Action;
 if(!I.StepTo(A.Start+.25,IW).Accepted||!I.ApplyResolvedHit(1,1.,0.,IW).Accepted)return false;S=F::SelectFull(I.State());
 TestTrue(TEXT("Ordinary actual Damaged receipt leaves Windup pose and only material feedback"),S.Clip==F::EClip::AxeWindup&&S.MaterialHit);
 if(!I.ApplyResolvedHit(2,1.,85.,IW).Accepted)return false;const double BrokenAt=I.State().Time,Until=I.State().StunUntil;
 for(int32 J=0;J<4;++J)
 {if(!I.StepTo(BrokenAt+double(J)*.1,IW).Accepted)return false;S=F::SelectFull(I.State());TestTrue(TEXT("Poise85 actual .4 stun owns all four phases over interrupted recovery"),S.Clip==F::EClip::Stunned&&S.Frame==J&&S.IntervalEnd==Until);}
 const double U[]={.125,.375,.625,.875};for(int32 J=0;J<4;++J)
 {if(!I.StepTo(Until+(A.RecoveryEnd-Until)*U[J],IW).Accepted)return false;S=F::SelectFull(I.State());TestTrue(TEXT("Full IR maps positive remaining original interval, never replays Active"),S.Clip==F::EClip::InterruptedRecovery&&S.Frame==J&&S.IntervalStart==Until&&S.IntervalEnd==A.RecoveryEnd);}
 if(!I.StepTo(A.RecoveryEnd,IW).Accepted)return false;
 TestTrue(TEXT("Early cancelled action finishes at original occupied end with no native active window"),F::SelectFull(I.State()).Clip!=F::EClip::InterruptedRecovery&&I.State().Windows.empty());
 G::FGuardKernel Late(93005);auto LW=FullWorld();if(!NativeAttack(Late,LW,G::EAttack::AxeSweep))return false;const auto C=Late.State().Action;
 if(!Late.StepTo(C.RecoveryEnd-.1,LW).Accepted||!Late.ApplyResolvedHit(1,1.,85.,LW).Accepted)return false;
 const double LateEnd=Late.State().StunUntil;if(!Late.StepTo(LateEnd,LW).Accepted)return false;S=F::SelectFull(Late.State());
 TestTrue(TEXT("Late break whose action ends during stun has no positive IR interval or new Active"),S.Clip!=F::EClip::InterruptedRecovery&&S.Clip!=F::EClip::AxeActive&&Late.State().Windows.size()==1&&Late.State().Closures.size()==1);
 return true;
}
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FGuardFullDeathProfileIsolation,
 "CodexDungeon.Content.FairytaleGuardFullV003.RealTerminalClockAndVersionedProfileIsolation",
 EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FGuardFullDeathProfileIsolation::RunTest(const FString&)
{
 using namespace GuardOwnerTests;
 FGuardWorld W(*this);if(!W.Create())return false;
 W.Guard=W.Game->SpawnStoneGuard(W.Player->GetGroundPosition()+FVector2D(150.,0.));
 if(!TestTrue(TEXT("Actual public Guard actor has genuine native owner in test world"),W.Guard&&W.Guard->GetStoneGuardDriver()))return false;
 W.Frame(.01f);W.Guard->ApplyCombatHit(100000.f,W.Player,0.f);
 if(!TestTrue(TEXT("Actual public lethal mitigation creates unique native Died / dead actor"),W.Guard->bDead&&W.State().HP==0.&&W.State().Phase==G::EPhase::Dead))return false;
 auto S=F::SelectFull(W.State(),double(W.Guard->AnimationTime));
 if(!TestTrue(TEXT("Stage0: full Death starts from actual Died and actual actor presentation clock"),S.Valid&&S.Clip==F::EClip::Death&&S.Frame==0&&S.DeathAfterglow&&S.SourceEventId>0))return false;
 const auto Saved=W.State();const auto Signature=StateSig(Saved);const uint64 DiedId=S.SourceEventId;
 auto Attacker=W.Game->Enemies[0].Get();W.Player->ApplyCombatHit(100000.f,Attacker,85.f);
 if(!TestTrue(TEXT("Real public player lethal source enters actual GameMode terminal gate"),W.Player->bDead&&W.Game->bGameOver))return false;
 const double RootTime=W.Game->GetSimulationTime();W.Frame(.8f);
 S=F::SelectFull(W.State(),double(W.Guard->AnimationTime));
 TestTrue(TEXT("Actual central terminal presentation advances Death to final hold and expires tint/afterglow while native clocks stay frozen"),S.Clip==F::EClip::Death&&S.Frame==5&&!S.DeathAfterglow&&!S.MaterialHit&&S.MaterialEventId==0&&S.TerminalPresentation&&S.SourceEventId==DiedId
  &&W.Game->GetSimulationTime()==RootTime&&StateSig(W.State())==Signature&&W.Guard->AnimationTime>=.8f);
 G::FGuardKernel Copy(Saved.EntityId,Saved.InitialTime,Saved.InitialPosition);
 if(!TestTrue(TEXT("Actual native Restore accepts genuine frozen dead history"),Copy.Restore(Saved)))return false;
 const auto Same=F::SelectFull(Copy.State(),double(W.Guard->AnimationTime));
 TestTrue(TEXT("Restored source keeps same original death event and last frame, no resumed afterglow"),Same.Clip==S.Clip&&Same.Frame==S.Frame&&Same.SourceEventId==DiedId&&!Same.DeathAfterglow&&!Same.MaterialHit&&StateSig(Copy.State())==Signature);
 TestEqual(TEXT("Versioned full contract declares thirteen rows and57logical entries"),F::ProfileFull().Num(),13);TestEqual(TEXT("Full native phase logical budget is57 including one Dormant alias"),F::LogicalFrameBudget(),57);
 TestTrue(TEXT("Only one declared alias leaves maximum56unique source bindings"),F::AvailableUniqueBindingsFull()<=56);
 const auto* Active=F::FindRowFull(F::EClip::AxeActive);const auto* Death=F::FindRowFull(F::EClip::Death);const auto* Alias=F::FindRowFull(F::EClip::Dormant);
 if(!TestTrue(TEXT("Available independent Active / Death and explicit Dormant alias proposals exist"),Active&&Death&&Alias))return false;
 TestTrue(TEXT("Blade below shoe does not move Active2/3 floor to alpha464; ONE342body basis stays"),Active->StandingExtent==342.&&Active->Frames[2].FloorPivot.Y==432.&&Active->Frames[3].FloorPivot.Y==432.&&Active->Scale()==100.8/342.);
 TestTrue(TEXT("Death uses upright365basis and v002 standing-root propagation, never collapsed pile center"),Death->StandingExtent==365.&&Death->Frames[2].FloorPivot==FVector2D(290.,453.)&&Death->Frames[5].FloorPivot==FVector2D(243.,453.)
  &&Death->Frames[2].PivotAuthority==F::EPivotAuthority::ArtistStandingRootPropagation&&Death->Scale()==100.8/365.);
 TestTrue(TEXT("Only Dormant has Wake0 alias; zero unique source textures"),Alias->AliasTarget==F::EClip::Wake&&Alias->AliasFrame==0&&Alias->Frames.IsEmpty());
 const auto* StompWU=F::FindRowFull(F::EClip::StompWindup);
 if(!TestTrue(TEXT("Root222 future source/registration populated independently of runtime trial gate"),StompWU&&StompWU->NativeSourceId==222&&StompWU->SourcePoseApproved&&StompWU->Frames.Num()==6))return false;
 TestTrue(TEXT("FAR lift retains original paired reference by NEAR-support delta, ONE388body scale, not raised-foot average"),
  StompWU->StandingExtent==388.&&StompWU->Scale()==100.8/388.&&StompWU->Frames[0].FloorPivot==FVector2D(251.,464.)
  &&StompWU->Frames[5].FloorPivot==FVector2D(309.,463.)&&StompWU->Frames[5].PivotAuthority==F::EPivotAuthority::ArtistNearSupportDeltaPropagation
  &&(!StompWU->TrialAllowed||!StompWU->TrialApprovalRecord.IsEmpty()));
 for(const auto& Row:F::ProfileFull())
 {
  TestTrue(TEXT("Rejected211/221/223 never enter full source table"),Row.NativeSourceId!=211&&Row.NativeSourceId!=221&&Row.NativeSourceId!=223);
  if(Row.TrialAllowed)TestTrue(TEXT("Full trial requires its own actual Root row record"),!Row.TrialApprovalRecord.IsEmpty());
 }
 // Unaccepted row policy is exercised with real native phase samples, never fabricated FState/pose frames.
 const auto CheckGap=[this](const F::FSelection& Q)
 {const auto Row=F::FindRowFull(Q.Clip);if(!Row)return TestTrue(TEXT("Actual native phase has a declared full profile row"),false);
  if(Row->SourcePoseApproved)return true;const auto Missing=F::PlanFull(Q);
  return TestTrue(TEXT("Unaccepted actual native full phase preserves requested clip with explicit zero-layer gap, never Ready"),Q.Valid&&!Missing.Valid&&Missing.AssetClip==Q.Clip&&!Missing.MissingReason.IsEmpty()&&Missing.WholebodyLayers.IsEmpty());};
 G::FGuardKernel M(93006);auto MW=FullWorld(450.);MW.CanStartAttack=false;
 if(!M.BeginCombat()||!M.NotifyOtherAcceptedEnemiesCleared()||!M.StepTo(1.2,MW).Accepted||!CheckGap(F::SelectFull(M.State())))return false;
 G::FGuardKernel Stomp(93007);auto SW=FullWorld(55.);if(!NativeAttack(Stomp,SW,G::EAttack::Stomp)||!CheckGap(F::SelectFull(Stomp.State())))return false;
 const auto SA=Stomp.State().Action;if(!Stomp.StepTo(SA.ActiveAt+.075,SW).Accepted||!CheckGap(F::SelectFull(Stomp.State())))return false;
 if(!Stomp.StepTo(SA.ActiveEnd+.375,SW).Accepted||!CheckGap(F::SelectFull(Stomp.State())))return false;
 const auto* LegacyMove=L::FindRow(L::EClip::Move);TestTrue(TEXT("Full source table does not fill legacy partial missing Move"),LegacyMove&&LegacyMove->Frames.IsEmpty());
 return true;
}
#endif
