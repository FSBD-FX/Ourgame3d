#if WITH_DEV_AUTOMATION_TESTS
#include "Misc/AutomationTest.h"
#include "../DungeonCompletedGroundMotion.h"
#include "../DungeonGroundWalkPhase.h"
#include "../DungeonRoomLayout.h"
#include "../DungeonRunSnapshotCodec.h"
#include "../DungeonRunInstaller.h"
#include "RunCodecFixture_v001.h"

namespace
{
DungeonGroundWalk::FPolicy SyntheticPolicy()
{
 // Numeric fixture only: not an art source, stride measurement or production default.
 DungeonGroundWalk::FPolicy P;P.CycleDistance=120.;P.CycleSeconds=.6;P.Durations={.1,.1,.1,.1,.1,.1};return P;
}
bool Motion(FCodecWorld& W,FDungeonCompletedGroundMotion& M)
{
 if(!W.Test.TestTrue(TEXT("Expected production completed-ground-motion witness after actual normal-input Tick"),W.Player->QueryCompletedGroundMotion(M)))return false;
 const auto& V=W.Game->GetEquipmentView();
 W.Test.TestTrue(TEXT("Witness is actual committed owner/room/time and current endpoint, independent of HUD draw"),M.Published&&M.RunGuid==V.RunGuid&&M.OwnerId==V.OwnerId
  &&M.RoomInstanceId==V.RoomInstanceId&&M.ToTime==W.Game->GetSimulationTime()&&M.To==W.Player->GetGroundPosition()&&M.FromTime<M.ToTime);
 return true;
}
bool Light(FCodecWorld& W,uint64& Id)
{
 IV::FItem Item;Item.ContentId="ARM-LGT-001";const auto R=W.Game->RegisterEquipmentSource(TEXT("walk.actual.light"),Item,W.Player->GetGroundPosition()+FVector2D(30,0),true);
 if(!R.Ok()||!W.Game->SelectEquipmentSource(R.SourceId))return false;W.Game->TryInteractEquipment();Id=R.InstanceId;
 return W.Game->GetEquipmentView().Action.Active;
}
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FFairytaleWalkRealDisplacement,
 "CodexDungeon.Content.FairytaleGroundWalk.CompletedNormalMovementAndDistancePhase",
 EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FFairytaleWalkRealDisplacement::RunTest(const FString&)
{
 FCodecWorld W(*this);if(!TestTrue(TEXT("Real bound Scene and normal Enter control"),W.Create()))return false;
 const auto Start=W.Player->GetGroundPosition();if(!W.Key(EKeys::D,true))return false;W.Frame(.04f);
 FDungeonCompletedGroundMotion M;if(!Motion(W,M))return false;
 TestTrue(TEXT("Only completed actual ordinary movement drives the measured distance"),M.Grounded&&M.OrdinaryEligible&&M.HadMoveIntent&&M.From==Start
  &&M.AcceptedDistance>0.&&FMath::IsNearlyEqual(M.AcceptedDistance,(M.To-M.From).Size(),1.e-7)&&M.WalkDistance==M.AcceptedDistance&&W.Player->AnimationName==TEXT("walk"));
 W.Key(EKeys::D,false);W.Frame(.01f);const auto DiagonalStart=W.Player->GetGroundPosition();W.Key(EKeys::D,true);W.Key(EKeys::W,true);W.Frame(.04f);
 if(!Motion(W,M))return false;
 TestTrue(TEXT("Normal diagonal remains normalized and witness follows actual displacement"),M.From==DiagonalStart&&M.AcceptedDistance>0.
  &&FMath::IsNearlyEqual(M.AcceptedDistance,double(W.Player->GetMoveSpeed())*(M.ToTime-M.FromTime),1.e-4));
 W.Key(EKeys::D,false);W.Key(EKeys::W,false);
 const auto P=SyntheticPolicy();double Whole=-9.,Split=-8.,First=-7.;
 TestTrue(TEXT("Explicit numeric phase policy advances from actual completed distance"),DungeonGroundWalk::Advance(.05,M.WalkDistance,P,Whole));
 TestTrue(TEXT("Split completed distances equal one advancement with the same policy"),DungeonGroundWalk::Advance(.05,M.WalkDistance*.4,P,First)
  &&DungeonGroundWalk::Advance(First,M.WalkDistance*.6,P,Split)&&FMath::IsNearlyEqual(Whole,Split,1.e-12));
 int Frame=-1;TestTrue(TEXT("Six authored intervals select a legitimate frame without wall-clock pacing"),DungeonGroundWalk::Frame(Whole,P,Frame)&&Frame>=0&&Frame<6);
 W.Frame(.02f);TestTrue(TEXT("Actual input release returns to Idle"),W.Player->AnimationName==TEXT("idle"));
 return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FFairytaleWalkWallClipping,
 "CodexDungeon.Content.FairytaleGroundWalk.RealWallBlockedAndClippedMovement",
 EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FFairytaleWalkWallClipping::RunTest(const FString&)
{
 FCodecWorld W(*this);if(!W.Create()||!W.Move(-920.,true)||!W.Key(EKeys::W,true))return false;W.Frame(.5f);
 FDungeonCompletedGroundMotion M;if(!Motion(W,M))return false;
 const auto Wall=W.Player->GetGroundPosition();W.Frame(.08f);if(!Motion(W,M))return false;
 TestTrue(TEXT("Held normal W against real Scene barrier has zero completed distance and Idle pose"),M.HadMoveIntent&&M.OrdinaryEligible&&M.From==Wall&&M.To==Wall
  &&M.AcceptedDistance==0.&&M.WalkDistance==0.&&W.Player->AnimationName==TEXT("idle"));
 double Frozen=-1.;const auto P=SyntheticPolicy();TestTrue(TEXT("Zero completed distance cannot advance the gait phase"),DungeonGroundWalk::Advance(.23,0.,P,Frozen)&&Frozen==.23);
 W.Key(EKeys::W,false);W.Key(EKeys::S,true);W.Frame(.073f);W.Key(EKeys::S,false);W.Key(EKeys::D,true);W.Key(EKeys::W,true);
 bool Clipped=false;
 for(int I=0;I<64&&!Clipped;++I)
 {
  W.Frame(.005f);if(!Motion(W,M))return false;const double Requested=double(W.Player->GetMoveSpeed())*(M.ToTime-M.FromTime);
  Clipped=M.AcceptedDistance>1.e-7&&M.AcceptedDistance<Requested-1.e-5;
 }
 TestTrue(TEXT("Diagonal collision completion reports the clipped distance, not requested speed times time"),Clipped&&M.WalkDistance==M.AcceptedDistance
  &&FMath::IsNearlyEqual(M.AcceptedDistance,(M.To-M.From).Size(),1.e-6));
 W.Key(EKeys::W,false);W.Key(EKeys::D,false);return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FFairytaleWalkTransitionsAndCapture,
 "CodexDungeon.Content.FairytaleGroundWalk.ActionsTransactionsAndSavedContinuity",
 EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FFairytaleWalkTransitionsAndCapture::RunTest(const FString&)
{
 FCodecWorld W(*this);if(!W.Create()||!W.Key(EKeys::D,true))return false;W.Frame(.04f);
 FDungeonCompletedGroundMotion M;if(!Motion(W,M))return false;W.Key(EKeys::D,false);W.Frame(.01f);
 const uint64 Sword=W.Game->GetEquipmentView().Slots[W.Game->GetEquipmentView().ActiveSlot].InstanceId;
 if(!W.Pulse(EKeys::J))return false;uint64 Ids[3]={};
 for(int Stage=0;Stage<3;++Stage)
 {
  const auto A=W.Player->GetMeleeCombatState().Action;Ids[Stage]=A.AttackId;
  if(!TestTrue(TEXT("Normal J chain retains actual SWD stage/instance and action pose"),A.Active&&int(A.Stage)==Stage&&A.WeaponInstanceId==Sword&&W.Player->GetPrimaryPoseFrame()>=0))return false;
  if(Stage<2)
  {
   if(!W.AdvanceTo(A.End-.08)||!W.Pulse(EKeys::J)||!W.AdvanceTo(A.End+.002))return false;
  }
  else if(!W.AdvanceTo(A.End+.47))return false;
 }
 TestTrue(TEXT("All actual stages are fresh and finish in Idle"),Ids[0]<Ids[1]&&Ids[1]<Ids[2]&&W.Player->AnimationName==TEXT("idle"));
 uint64 LightId=0;if(!TestTrue(TEXT("Normal registered LGT pickup begins actual transaction"),Light(W,LightId)))return false;
 const double OldEnd=W.Player->GetEquipmentActionDeadline();W.Key(EKeys::D,true);W.Frame(.01f);W.Key(EKeys::D,false);W.Frame(.01f);
 TestTrue(TEXT("Normal walking cancels pickup without early armor or replay at old deadline"),!W.Game->GetEquipmentView().Action.Active&&W.Game->GetEquipmentInventoryState()->Armor==0&&W.AdvanceTo(OldEnd+.01));
 uint64 Source=0;for(const auto& S:W.Game->GetEquipmentSources())if(!S.Consumed&&S.InstanceId==LightId)Source=S.SourceId;
 if(!TestTrue(TEXT("Same real unconsumed LGT source restarts and commits normally"),Source&&W.Game->SelectEquipmentSource(Source)))return false;
 W.Game->TryInteractEquipment();if(!W.AdvanceTo(W.Player->GetEquipmentActionDeadline()))return false;
 TestTrue(TEXT("Actual commit keeps original sword and equips same light identity"),W.Game->GetEquipmentInventoryState()->Armor==LightId&&W.Game->GetEquipmentView().Slots[W.Game->GetEquipmentView().ActiveSlot].InstanceId==Sword);
 W.Key(EKeys::D,true);W.Frame(.04f);W.Key(EKeys::D,false);
 FDungeonRunSnapshot Saved;FString Why;if(!TestTrue(TEXT("Completed actual motion boundary can capture Run"),W.Game->CaptureRunSnapshot(Saved,Why)))return false;
 TArray<uint8> Bytes;FDungeonValidatedRun Decoded;
 TestTrue(TEXT("Existing codec preserves exact saved AnimationName/AnimationTime/Moving without a new owner field"),DungeonRunSnapshotCodec::Encode(Saved,Bytes,Why)
  &&DungeonRunSnapshotCodec::Decode(Bytes,Decoded,Why)&&Decoded.IsValid()&&Decoded.Get()->Fighters[0].AnimationName==Saved.Fighters[0].AnimationName
  &&Decoded.Get()->Fighters[0].AnimationTime==Saved.Fighters[0].AnimationTime&&Decoded.Get()->Fighters[0].Moving==Saved.Fighters[0].Moving);
 FCodecWorld Target(*this);if(!Target.Create()||!Decoded.IsValid())return false;FDungeonPreparedRun Prepared;
 if(!TestTrue(TEXT("Real hidden-group preparation and installation restores the actual walking Run"),FDungeonRunInstaller::Prepare(*Target.Game,Decoded,Prepared,Why)
  &&FDungeonRunInstaller::Install(*Target.Game,Prepared,Why)))return false;
 Target.Player=Target.Game->PlayerFighter;
 const auto SavedPhase=Saved.Fighters[0].AnimationTime;Target.Frame(.05f);
 TestTrue(TEXT("Install gate preserves saved walking phase without ticking or counting placement"),Target.Player->AnimationName==Saved.Fighters[0].AnimationName
  &&Target.Player->AnimationTime==SavedPhase&&Target.Player->GetGroundPosition()==Saved.Fighters[0].GroundPosition);
 FDungeonCompletedGroundMotion InstalledMotion;TestFalse(TEXT("Install cannot publish the teleport as completed walking"),Target.Player->QueryCompletedGroundMotion(InstalledMotion));
 Target.Frame(.005f);if(!Target.Pulse(EKeys::Enter)||Target.Game->GetRunInstallGate()!=EDungeonRunInstallGate::Open)return false;
 const auto ResumedFrom=Target.Player->GetGroundPosition();Target.Key(EKeys::D,true);Target.Frame(.02f);Target.Key(EKeys::D,false);
 if(!Motion(Target,InstalledMotion))return false;
 TestTrue(TEXT("Fresh resumed ordinary movement starts at saved placement and counts only new displacement"),InstalledMotion.From==ResumedFrom
  &&FMath::IsNearlyEqual(InstalledMotion.AcceptedDistance,(InstalledMotion.To-InstalledMotion.From).Size(),1.e-6));
 // Public direct motion is an existing call path, not a forced actor teleport.
 W.Player->MoveOnGround({1,0},.01f);FDungeonRunSnapshot Sentinel;Sentinel.SimulationTime=123.;const auto Before=Sentinel.SimulationTime;
 TestFalse(TEXT("Unconsumed movement accumulation cannot escape through Run Capture"),W.Game->CaptureRunSnapshot(Sentinel,Why));
 TestTrue(TEXT("Refused pending motion capture is atomic"),Sentinel.SimulationTime==Before);
 W.Frame(.01f);TestTrue(TEXT("Actions consumes the pending movement before later Capture"),W.Game->CaptureRunSnapshot(Sentinel,Why));
 return true;
}
#endif
