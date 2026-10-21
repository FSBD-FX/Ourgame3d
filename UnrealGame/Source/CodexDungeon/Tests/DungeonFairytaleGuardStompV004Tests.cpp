#if WITH_DEV_AUTOMATION_TESTS
#include "Misc/AutomationTest.h"
#include "StoneGuardOwnerFixture_v002.h"
#include "../DungeonFairytaleGuardStompProfileV004.h"
#include <cmath>
#include <limits>
namespace
{
namespace SG=DungeonStoneGuard;
namespace SF=DungeonFairytaleGuardFullV003;
namespace SO=DungeonFairytaleGuardStompV004;
SG::FWorldInput StompWorld(int32 Side)
{SG::FWorldInput W;W.HasTarget=true;W.Target={double(Side)*65.,0.,0.};W.Sweep=[](const SG::FSweepRequest&){return SG::FSweepResult{};};return W;}
bool BeginNativeStomp(SG::FGuardKernel& Kernel,const SG::FWorldInput& World)
{return Kernel.BeginCombat()&&Kernel.StepTo(0.,World).Accepted&&Kernel.StepTo(1.,World).Accepted
 &&Kernel.ChooseAttack(World)==SG::EAttack::Stomp&&Kernel.TryStartAttack(SG::EAttack::Stomp,World).Accepted;}
const SG::FEvent* StompEvent(const SG::FState& State,SG::EEventKind Kind,uint64 AttackId)
{const SG::FEvent* Found=nullptr;for(const auto& Event:State.Issued)if(Event.Kind==Kind&&Event.Action.AttackId==AttackId){if(Found)return nullptr;Found=&Event;}return Found;}
const SF::FRow* OverlayRow(const TArray<SF::FRow>& Rows,SF::EClip Clip)
{for(const auto& Row:Rows)if(Row.Clip==Clip)return &Row;return nullptr;}
int32 CountBindings(const TArray<SF::FRow>& Rows)
{int32 Count=0;for(const auto& Row:Rows)Count+=Row.Frames.Num();return Count;}
TArray<uint8> RowSignature(const SF::FRow& Row)
{
 GuardOwnerTests::FGuardSignature Sig;
 Sig.V(Row.Clip,Row.AliasTarget,Row.AliasFrame,Row.NativeSourceId,Row.PendingNativeCandidateId,
  Row.StandingBasisFrame,Row.StandingCrownY,Row.StandingSoleY,Row.CanvasWidth,Row.CanvasHeight,
  Row.StandingExtent,Row.TargetBodyHeight,Row.SourcePoseApproved,Row.TrialAllowed,Row.FinalAccepted,Row.IndependentPoseOnly);
 Sig.String(Row.TrialApprovalRecord);Sig.String(Row.RegistrationEvidenceSHA256);Sig.String(Row.SourceIndexSHA256);Sig.String(Row.GapReason);
 Sig.V(Row.Frames.Num());for(const auto& Frame:Row.Frames)
 {Sig.String(Frame.TexturePath);Sig.String(Frame.SourceSHA256);Sig.String(Frame.SourceRGBASHA256);Sig.Point(Frame.FloorPivot);Sig.V(Frame.PivotAuthority);}
 return Sig.Bytes;
}
}
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FGuardStompV004NativeClock,
 "CodexDungeon.Content.FairytaleGuardStompV004.RealNativeHalfOpenClockAndEventIdentity",
 EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FGuardStompV004NativeClock::RunTest(const FString&)
{
 for(const int32 Side:{-1,1})
 {
  SG::FGuardKernel Kernel(Side<0?94001:94002);auto World=StompWorld(Side);
  if(!TestTrue(TEXT("Independent premise: actual native extremely-close policy chooses Stomp after real Wake"),BeginNativeStomp(Kernel,World)))return false;
  const auto Action=Kernel.State().Action;
  if(!TestTrue(TEXT("Independent premise: original Stomp deadlines remain .9/.45/.15/1.5/3 and fixed start-facing"),
   Action.Kind==SG::EAttack::Stomp&&Action.LockAt==Action.Start+.45&&Action.ActiveAt==Action.Start+.9
   &&Action.ActiveEnd==Action.ActiveAt+.15&&Action.RecoveryEnd==Action.ActiveEnd+1.5&&Action.CooldownEnd==Action.Start+3.
   &&Action.Facing==Side&&Kernel.State().OccupiedUntil==Action.RecoveryEnd))return false;
  const double WindupStarts[]={0.,.15,.3,.45,.6,.75};
  for(int32 Frame=0;Frame<6;++Frame)
  {
   if(!TestTrue(TEXT("Real kernel reaches original Windup boundary"),Kernel.StepTo(Action.Start+WindupStarts[Frame],World).Accepted))return false;
   const auto Selection=SF::SelectFull(Kernel.State());const auto Started=StompEvent(Kernel.State(),SG::EEventKind::AttackStarted,Action.AttackId);
   TestTrue(TEXT("Existing WU222 six150ms phases retain exact original AttackStarted identity"),Started&&Selection.Valid&&Selection.Clip==SF::EClip::StompWindup&&Selection.Frame==Frame
    &&Selection.Facing==Side&&Selection.SourceEventId==Started->EventId&&Selection.AttackId==Action.AttackId&&Selection.IntervalEnd==Action.ActiveAt);
  }
  if(!TestTrue(TEXT("Kernel accepts last representable Windup sample"),Kernel.StepTo(std::nextafter(Action.ActiveAt,-std::numeric_limits<double>::infinity()),World).Accepted))return false;
  TestTrue(TEXT("WU6 is half-open through the actual predecessor of ActiveAt"),SF::SelectFull(Kernel.State()).Clip==SF::EClip::StompWindup&&SF::SelectFull(Kernel.State()).Frame==5);
  if(!TestTrue(TEXT("Independent premise: exact ActiveAt issues one genuine Stomp window"),Kernel.StepTo(Action.ActiveAt,World).Accepted&&Kernel.State().Windows.size()==1))return false;
  const auto ActiveSelection=SF::SelectFull(Kernel.State());const auto ActivePlan=SO::PlanStompV004(ActiveSelection);
  if(!TestTrue(TEXT("TARGET Stage0: real original Stomp Active0 consumes newly approved one-layer overlay while old44 stays closed"),
   ActivePlan.Valid&&ActivePlan.AssetClip==SF::EClip::StompActive&&ActivePlan.Frame==0&&ActivePlan.Row&&ActivePlan.Row->NativeSourceId>0&&ActivePlan.WholebodyLayers.Num()==1
   &&!SF::PlanFull(ActiveSelection).Valid))return false;
  const auto ActiveEvent=StompEvent(Kernel.State(),SG::EEventKind::ActiveWindow,Action.AttackId);
  const auto Locked=StompEvent(Kernel.State(),SG::EEventKind::AimLocked,Action.AttackId);
  const auto& Window=Kernel.State().Windows.front();
  TestTrue(TEXT("Actual AimLocked/ActiveWindow/Window agree on original time, center, facing, entity and distinct event identity"),
   Locked&&ActiveEvent&&Locked->AtTime==Action.LockAt&&ActiveEvent->AtTime==Action.ActiveAt&&ActiveEvent->EndTime==Action.ActiveEnd
   &&ActiveEvent->EntityId==Kernel.State().EntityId&&ActiveEvent->Action.Kind==SG::EAttack::Stomp
   &&ActiveSelection.SourceEventId==ActiveEvent->EventId&&Window.EventId==ActiveEvent->EventId&&Window.AttackId==Action.AttackId
   &&Window.Start==Action.ActiveAt&&Window.End==Action.ActiveEnd&&Window.Center.X==Locked->Action.LockedCenter.X&&Window.Center.Y==Locked->Action.LockedCenter.Y&&Window.Facing==Side);
  SG::FTarget Target;Target.EntityId=94901;Target.Position=World.Target;
  TestTrue(TEXT("Original native ellipse produces one actual hit and rejects repeat"),Kernel.TryHit(Target).Accepted&&!Kernel.TryHit(Target).Accepted);
  const double ActiveOne=Action.ActiveAt+.075;
  if(!Kernel.StepTo(std::nextafter(ActiveOne,-std::numeric_limits<double>::infinity()),World).Accepted)return false;
  TestTrue(TEXT("Before75ms boundary Active0 still owns the sample"),SF::SelectFull(Kernel.State()).Frame==0);
  if(!Kernel.StepTo(ActiveOne,World).Accepted)return false;
  TestTrue(TEXT("Exact75ms boundary selects Active1 with same immutable window"),SF::SelectFull(Kernel.State()).Frame==1&&SO::PlanStompV004(SF::SelectFull(Kernel.State())).Valid);
  const double RecoveryStarts[]={0.,.375,.75,1.125};
  for(int32 Frame=0;Frame<4;++Frame)
  {
   if(!Kernel.StepTo(Action.ActiveEnd+RecoveryStarts[Frame],World).Accepted)return false;
   const auto Selection=SF::SelectFull(Kernel.State());const auto Event=StompEvent(Kernel.State(),SG::EEventKind::RecoveryStarted,Action.AttackId);const auto Plan=SO::PlanStompV004(Selection);
   TestTrue(TEXT("Exact ActiveEnd switches to Recovery0; four375ms frames use original RecoveryStarted/end and one new approved layer"),
    Event&&Selection.Valid&&Selection.Clip==SF::EClip::StompRecovery&&Selection.Frame==Frame&&Selection.SourceEventId==Event->EventId
    &&Event->AtTime==Action.ActiveEnd&&Event->EndTime==Action.RecoveryEnd&&Selection.IntervalEnd==Action.RecoveryEnd&&Plan.Valid&&Plan.Row->NativeSourceId>0&&Plan.WholebodyLayers.Num()==1);
  }
  const auto Signature=GuardOwnerTests::StateSig(Kernel.State());for(int32 Read=0;Read<8;++Read)SO::PlanStompV004(SF::SelectFull(Kernel.State()));
  TestTrue(TEXT("Shared plan selection never changes native clocks/HP/history/receipt ownership"),Signature==GuardOwnerTests::StateSig(Kernel.State()));
  if(!Kernel.StepTo(Action.RecoveryEnd,World).Accepted)return false;
  const auto Ready=SF::SelectFull(Kernel.State());const int32 ExpectedReady=int32(std::floor(std::fmod(Kernel.State().Time-Kernel.State().WakeEnd,1.)/.25));
  TestTrue(TEXT("RecoveryEnd returns original running Ready clock without new attack/window or resetting Ready0"),Ready.Clip==SF::EClip::Ready&&Ready.Frame==ExpectedReady
   &&Kernel.State().Windows.size()==1&&Kernel.State().HitReceipts.size()==1&&Kernel.State().StompReadyAt==Action.CooldownEnd&&Kernel.State().IdleReadyAt==Action.RecoveryEnd+.3);
 }
 return true;
}
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FGuardStompV004ProfileIsolation,
 "CodexDungeon.Content.FairytaleGuardStompV004.Versioned50BindingsAndAtomicMirroredFloor",
 EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FGuardStompV004ProfileIsolation::RunTest(const FString&)
{
 const auto& Old=SF::ProfileFull();const auto& Overlay=SO::ProfileStompV004();
 if(!TestTrue(TEXT("Independent premise: oldKnown44/13rows/57logical and missingMove remain unchanged"),CountBindings(Old)==44&&Old.Num()==13&&SF::LogicalFrameBudget()==57
  &&SF::FindRowFull(SF::EClip::Move)&&SF::FindRowFull(SF::EClip::Move)->Frames.IsEmpty()))return false;
 if(!TestTrue(TEXT("TARGET Stage0: isolated new profile contains exactly50 unique bindings; old44 count is not relaxed"),Overlay.Num()==13&&CountBindings(Overlay)==50))return false;
 for(const auto& Row:Old)
 {
  if(Row.Clip==SF::EClip::StompActive||Row.Clip==SF::EClip::StompRecovery)continue;
  const auto Copy=OverlayRow(Overlay,Row.Clip);TestTrue(TEXT("All eleven unaffected rows retain complete fieldwise metadata/source/gates bytevalues"),Copy&&RowSignature(Row)==RowSignature(*Copy));
 }
 SG::FGuardKernel Kernel(94003);auto World=StompWorld(-1);if(!BeginNativeStomp(Kernel,World)||!Kernel.StepTo(Kernel.State().Action.ActiveAt,World).Accepted)return false;
 const auto Selection=SF::SelectFull(Kernel.State());const auto Plan=SO::PlanStompV004(Selection);
 TestTrue(TEXT("Actual left Active0 mirrors the registered floor once, retains100.8ONErow density and one fixed axe layer"),Plan.Valid&&Plan.Row&&Plan.Row->StandingExtent>0.
  &&Plan.Row->TargetBodyHeight==100.8&&Plan.Row->Frames.Num()==2&&Plan.SourcePivot==Plan.Row->Frames[0].FloorPivot
  &&Plan.DisplayPivotX==512.-Plan.SourcePivot.X&&Plan.WholebodyLayers.Num()==1
  &&Plan.Row->Scale()==100.8/Plan.Row->StandingExtent&&Plan.PivotAuthority!=SF::EPivotAuthority::Unconfigured);
 const auto Signature=GuardOwnerTests::StateSig(Kernel.State());
 const auto RejectWith=[&](int32 Which)
 {
  auto Copy=Overlay;auto Row=Copy.FindByPredicate([](const SF::FRow& R){return R.Clip==SF::EClip::StompActive;});if(!Row)return false;
  if(Which==0)Row->Frames.RemoveAt(1);if(Which==1)Row->TrialApprovalRecord.Empty();if(Which==2)Row->TrialAllowed=false;
  if(Which==3)Row->Frames[1].SourceRGBASHA256=TEXT("bad");if(Which==4)Row->Frames[1].FloorPivot.X=513.;
  const auto Rejected=SF::PlanFullInProfile(Selection,Copy);
  return !Rejected.Valid&&Rejected.RequestedClip==SF::EClip::StompActive&&Rejected.AssetClip==SF::EClip::StompActive&&!Rejected.MissingReason.IsEmpty();
 };
 for(int32 Which=0;Which<5;++Which)TestTrue(TEXT("Incomplete/off/unapproved/mismatched full-row registration fails closed; never substitutes Ready or the old44 plan"),RejectWith(Which));
 TestTrue(TEXT("Negative registration queries cannot mutate real producer state"),Signature==GuardOwnerTests::StateSig(Kernel.State()));
 TestTrue(TEXT("Existing old44 StompA/R still contain no pixels or trial permission"),!SF::FindRowFull(SF::EClip::StompActive)->SourcePoseApproved&&!SF::FindRowFull(SF::EClip::StompRecovery)->SourcePoseApproved
  &&SF::FindRowFull(SF::EClip::StompActive)->Frames.IsEmpty()&&SF::FindRowFull(SF::EClip::StompRecovery)->Frames.IsEmpty());
 return true;
}
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FGuardStompV004RealActor,
 "CodexDungeon.Content.FairytaleGuardStompV004.RealActorReceiptRecoveryAndInterruptedExclusion",
 EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FGuardStompV004RealActor::RunTest(const FString&)
{
 GuardOwnerTests::FGuardWorld World(*this);if(!World.Create())return false;
 // Public-spawn test fixture only, distinct from the later formal-room native
 // capture. No guard/player relocation, clock write or fabricated state.
 World.Guard=World.Game->SpawnStoneGuard(World.Player->GetGroundPosition()+FVector2D(65.,0.));
 if(!TestTrue(TEXT("Independent premise: actual Guard actor owns a genuine native driver"),World.Guard&&World.Guard->GetStoneGuardDriver()))return false;
 for(int32 Frame=0;Frame<400&&!World.State().Action.InProgress&&!World.Game->bGameOver;++Frame)World.Frame(.01f);
 if(!TestTrue(TEXT("Independent premise: actual GameMode world naturally chooses Stomp inside native70world policy"),World.State().Action.InProgress&&World.State().Action.Kind==SG::EAttack::Stomp))
 {World.Diagnostic(TEXT("StompV004-natural-start-failed"));return false;}
 const auto Action=World.State().Action;const float BeforeHP=World.Player->Health;
 if(!TestTrue(TEXT("Independent premise: genuine driver reaches Active and issues player hit receipt"),World.AdvanceTo(Action.ActiveAt+.001)
  &&World.State().Windows.size()==1&&World.State().HitReceipts.size()==1&&World.State().HitReceipts.front().TargetId==World.Player->GetRuntimeEntityId()&&World.Player->Health<BeforeHP))return false;
 if(!TestTrue(TEXT("Independent premise: same actual native actor enters original Recovery1"),World.AdvanceTo(Action.ActiveEnd+.4)))return false;
 const auto Selection=SF::SelectFull(World.State());const auto Plan=SO::PlanStompV004(Selection);
 if(!TestTrue(TEXT("TARGET Stage0: actual actor recovery after genuine18damage Stomp hit consumes newly approved one-layer plan on originalclock"),
  Selection.Clip==SF::EClip::StompRecovery&&Selection.Frame==1&&Selection.AttackId==Action.AttackId&&Plan.Valid&&Plan.Row&&Plan.Row->NativeSourceId>0&&Plan.WholebodyLayers.Num()==1))return false;
 const auto Signature=GuardOwnerTests::StateSig(World.State());const double Sim=World.Game->GetSimulationTime();
 SO::PlanStompV004(SF::SelectFull(World.State()));
 TestTrue(TEXT("Actor visual query never changes real HP, original window/receipt histories or root simulation time"),Signature==GuardOwnerTests::StateSig(World.State())&&Sim==World.Game->GetSimulationTime());
 if(!World.AdvanceTo(Action.RecoveryEnd))return false;
 TestTrue(TEXT("Actual native actor finishes at original occupied deadline and no repeated hit"),SF::SelectFull(World.State()).Clip==SF::EClip::Ready&&World.State().HitReceipts.size()==1&&World.State().Windows.size()==1);
 SG::FGuardKernel Interrupted(94004);auto Input=StompWorld(1);if(!BeginNativeStomp(Interrupted,Input))return false;const auto Original=Interrupted.State().Action;
 if(!Interrupted.StepTo(Original.Start+.2,Input).Accepted||!Interrupted.ApplyResolvedHit(1,1.,85.,Input).Accepted)return false;
 TestTrue(TEXT("Actual85break selects Stunned before either Stomp follow row"),SF::SelectFull(Interrupted.State()).Clip==SF::EClip::Stunned);
 if(!Interrupted.StepTo(Interrupted.State().StunUntil,Input).Accepted)return false;const auto IR=SF::SelectFull(Interrupted.State());
 TestTrue(TEXT("After real stun original positive interval selects IR0, never StompA/R or a new Active"),IR.Clip==SF::EClip::InterruptedRecovery&&IR.Frame==0&&IR.IntervalEnd==Original.RecoveryEnd&&Interrupted.State().Windows.empty());
 if(!Interrupted.StepTo(Original.RecoveryEnd,Input).Accepted)return false;
 TestTrue(TEXT("Interrupted Stomp ends at original occupied deadline without any resurrected damage window"),SF::SelectFull(Interrupted.State()).Clip==SF::EClip::Ready&&Interrupted.State().Windows.empty());
 return true;
}
#endif
