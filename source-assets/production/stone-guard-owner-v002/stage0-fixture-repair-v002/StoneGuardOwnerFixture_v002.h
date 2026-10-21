#pragma once
// Independent test-only Guard signatures and V2 wire oracle. The legacy V1
// fixture is immutable; no production codec constructs an expected value.
#include "RunCodecFixture_v001.h"
#include "../DungeonRunInstaller.h"
#include "../DungeonRunSnapshotCodec.h"
namespace GuardOwnerTests
{
namespace G=DungeonStoneGuard;
struct FGuardSignature:FRunSignature
{
 void PointG(const G::FPoint& P){V(P.X,P.Y,P.Z);}
 void GuardAction(const G::FAction& A)
 {
  V(A.AttackId,A.Kind,A.InProgress,A.Locked,A.WindowIssued,A.Interrupted,A.Start,A.LockAt,A.ActiveAt,A.ActiveEnd,
    A.RecoveryEnd,A.CooldownEnd,A.InterruptedAt,A.CompletedAt,A.Damage,A.Stagger);
  PointG(A.Origin);PointG(A.LockedCenter);PointG(A.Target);V(A.Facing);
 }
 void GuardState(const G::FState& S)
 {
  // All 33 FState fields; five ordered histories. No padding/hash of structs.
  V(S.Version,S.EntityId,S.NextAttackId,S.NextEventId,S.LastDamageReceiptId,S.InitialTime,S.Time,S.HP,S.PoiseAccum,
    S.PoiseDecayOrigin,S.LastPoiseAt,S.ProtectionUntil,S.StunUntil,S.CombatStartedAt,S.WakeStartedAt,S.WakeEnd,
    S.AxeReadyAt,S.StompReadyAt,S.OccupiedUntil,S.IdleReadyAt,S.WakeQueued,S.Awakened,S.RewardClaimed,S.Phase);
  PointG(S.InitialPosition);PointG(S.Position);V(S.Facing);GuardAction(S.Action);
  V(uint64(S.Windows.size()));for(const auto& W:S.Windows)
  {V(W.AttackId,W.EventId,W.Kind,W.Start,W.End,W.Damage,W.Stagger);PointG(W.Center);V(W.Facing);}
  V(uint64(S.Closures.size()));for(const auto& C:S.Closures)V(C.AttackId,C.AtTime);
  V(uint64(S.HitReceipts.size()));for(const auto& H:S.HitReceipts)V(H.AttackId,H.TargetId,H.AtTime);
  V(uint64(S.ReceivedHits.size()));for(const auto& H:S.ReceivedHits)V(H.ReceiptId,H.AtTime,H.ActualHPLoss,H.Stagger);
  V(uint64(S.Issued.size()));for(const auto& E:S.Issued)
  {V(E.EventId,E.EntityId,E.TargetId,E.Kind,E.AtTime,E.EndTime,E.Amount);PointG(E.From);PointG(E.To);GuardAction(E.Action);}
 }
 void GuardOwner(const FDungeonStoneGuardOwnerSnapshot& S)
 {V(S.Schema,S.Policy.ExtremelyCloseRadius,S.DeathObserved);GuardState(S.Kernel);}
 void CompleteOwner(const FDungeonFighterOwnerSnapshot& S)
 {Owner(S);V(S.Guard.IsSet());if(S.Guard.IsSet())GuardOwner(S.Guard.GetValue());}
 void CompleteRun(const FDungeonRunSnapshot& S)
 {Run(S);V(S.Fighters.Num());for(const auto& F:S.Fighters){V(F.Guard.IsSet());if(F.Guard.IsSet())GuardOwner(F.Guard.GetValue());}}
};
inline TArray<uint8> StateSig(const G::FState& S){FGuardSignature B;B.GuardState(S);return B.Bytes;}
inline TArray<uint8> OwnerSig(const FDungeonFighterOwnerSnapshot& S){FGuardSignature B;B.CompleteOwner(S);return B.Bytes;}
inline TArray<uint8> RunSig(const FDungeonRunSnapshot& S){FGuardSignature B;B.CompleteRun(S);return B.Bytes;}
struct FGuardWire:FCodecOracle
{
 static JO PointG(const G::FPoint& P){auto O=Obj();Scalars(O,"X,Y,Z",P.X,P.Y,P.Z);return O;}
 static JO GuardAction(const G::FAction& A)
 {
  auto O=Obj();Scalars(O,"AttackId,Kind,InProgress,Locked,WindowIssued,Interrupted,Start,LockAt,ActiveAt,ActiveEnd,RecoveryEnd,CooldownEnd,InterruptedAt,CompletedAt,Damage,Stagger,Facing",
   A.AttackId,A.Kind,A.InProgress,A.Locked,A.WindowIssued,A.Interrupted,A.Start,A.LockAt,A.ActiveAt,A.ActiveEnd,A.RecoveryEnd,A.CooldownEnd,A.InterruptedAt,A.CompletedAt,A.Damage,A.Stagger,A.Facing);
  O->SetObjectField(TEXT("Origin"),PointG(A.Origin));O->SetObjectField(TEXT("LockedCenter"),PointG(A.LockedCenter));O->SetObjectField(TEXT("Target"),PointG(A.Target));return O;
 }
 static JO GuardState(const G::FState& S)
 {
  auto O=Obj();Scalars(O,"Version,EntityId,NextAttackId,NextEventId,LastDamageReceiptId,InitialTime,Time,HP,PoiseAccum,PoiseDecayOrigin,LastPoiseAt,ProtectionUntil,StunUntil,CombatStartedAt,WakeStartedAt,WakeEnd,AxeReadyAt,StompReadyAt,OccupiedUntil,IdleReadyAt,WakeQueued,Awakened,RewardClaimed,Phase,Facing",
   S.Version,S.EntityId,S.NextAttackId,S.NextEventId,S.LastDamageReceiptId,S.InitialTime,S.Time,S.HP,S.PoiseAccum,S.PoiseDecayOrigin,S.LastPoiseAt,S.ProtectionUntil,S.StunUntil,S.CombatStartedAt,S.WakeStartedAt,S.WakeEnd,S.AxeReadyAt,S.StompReadyAt,S.OccupiedUntil,S.IdleReadyAt,S.WakeQueued,S.Awakened,S.RewardClaimed,S.Phase,S.Facing);
  O->SetObjectField(TEXT("InitialPosition"),PointG(S.InitialPosition));O->SetObjectField(TEXT("Position"),PointG(S.Position));O->SetObjectField(TEXT("Action"),GuardAction(S.Action));
  Array(O,TEXT("Windows"),S.Windows,[](const auto& W){auto J=Obj();Scalars(J,"AttackId,EventId,Kind,Start,End,Damage,Stagger,Facing",W.AttackId,W.EventId,W.Kind,W.Start,W.End,W.Damage,W.Stagger,W.Facing);J->SetObjectField(TEXT("Center"),PointG(W.Center));return J;});
  Array(O,TEXT("Closures"),S.Closures,[](const auto& C){auto J=Obj();Scalars(J,"AttackId,AtTime",C.AttackId,C.AtTime);return J;});
  Array(O,TEXT("HitReceipts"),S.HitReceipts,[](const auto& H){auto J=Obj();Scalars(J,"AttackId,TargetId,AtTime",H.AttackId,H.TargetId,H.AtTime);return J;});
  Array(O,TEXT("ReceivedHits"),S.ReceivedHits,[](const auto& H){auto J=Obj();Scalars(J,"ReceiptId,AtTime,ActualHPLoss,Stagger",H.ReceiptId,H.AtTime,H.ActualHPLoss,H.Stagger);return J;});
  Array(O,TEXT("Issued"),S.Issued,[](const auto& E){auto J=Obj();Scalars(J,"EventId,EntityId,TargetId,Kind,AtTime,EndTime,Amount",E.EventId,E.EntityId,E.TargetId,E.Kind,E.AtTime,E.EndTime,E.Amount);J->SetObjectField(TEXT("From"),PointG(E.From));J->SetObjectField(TEXT("To"),PointG(E.To));J->SetObjectField(TEXT("Action"),GuardAction(E.Action));return J;});return O;
 }
 static JO GuardOwner(const FDungeonStoneGuardOwnerSnapshot& S)
 {auto O=Obj();Scalars(O,"Schema,DeathObserved",S.Schema,S.DeathObserved);auto P=Obj();Scalars(P,"ExtremelyCloseRadius",S.Policy.ExtremelyCloseRadius);O->SetObjectField(TEXT("Policy"),P);O->SetObjectField(TEXT("Kernel"),GuardState(S.Kernel));return O;}
 static JO DocumentV2(const FDungeonRunSnapshot& S)
 {
  auto D=Document(S);D->SetStringField(TEXT("codec"),TEXT("bound-run-v2"));auto R=D->GetObjectField(TEXT("snapshot"));TArray<JV> Actors;
  for(const auto& F:S.Fighters){auto A=Owner(F);A->SetField(TEXT("Guard"),F.Guard.IsSet()?Value(GuardOwner(F.Guard.GetValue())):Null());Actors.Add(Value(A));}
  R->SetArrayField(TEXT("Fighters"),Actors);return D;
 }
};
struct FGuardWorld:FCodecWorld
{
 ADungeonFighter* Guard=nullptr;
 explicit FGuardWorld(FAutomationTestBase& T):FCodecWorld(T){}
 const G::FState& State()const{return Guard->GetStoneGuardDriver()->State();}
 void Diagnostic(const TCHAR* Stage) const
 {
  const auto P=Player->GetGroundPosition(),A=Guard->GetGroundPosition(),Delta=P-A;const auto& S=State();
  Test.AddInfo(FString::Printf(TEXT("GuardOwnerFixture stage=%s playerXY=(%.17g,%.17g) guardXY=(%.17g,%.17g) deltaXY=(%.17g,%.17g) wakeEllipseR2=%.17g rootTime=%.17g guardTime=%.17g birth=%.17g combatStart=%.17g wakeStart=%.17g wakeEnd=%.17g phase=%d awakened=%d queued=%d AI=%d waiting=%d gameOver=%d playerHP=%.17g actionId=%llu actionKind=%d actionActive=%d gate=%d windows=%llu closures=%llu hits=%llu received=%llu issued=%llu"),
   Stage,P.X,P.Y,A.X,A.Y,Delta.X,Delta.Y,FMath::Square(Delta.X/235.)+FMath::Square(Delta.Y/110.),
   Game->GetSimulationTime(),S.Time,S.InitialTime,S.CombatStartedAt,S.WakeStartedAt,S.WakeEnd,int32(S.Phase),int32(S.Awakened),int32(S.WakeQueued),int32(Guard->bAIEnabled),int32(Game->bWaitingForStart),int32(Game->bGameOver),double(Player->Health),
   static_cast<unsigned long long>(S.Action.AttackId),int32(S.Action.Kind),int32(S.Action.InProgress),int32(Game->GetRunInstallGate()),static_cast<unsigned long long>(S.Windows.size()),static_cast<unsigned long long>(S.Closures.size()),static_cast<unsigned long long>(S.HitReceipts.size()),static_cast<unsigned long long>(S.ReceivedHits.size()),static_cast<unsigned long long>(S.Issued.size())));
 }
 bool Rich()
 {
  // The accepted Scene fixture starts at its real Layout.Entry, not at0.
  // Preserve the known150cm axe/wake relation without relocating the player.
  const FVector2D GuardSpawn=Player->GetGroundPosition()-FVector2D(150.,0.);
  Guard=Game->SpawnStoneGuard(GuardSpawn);
  if(!Test.TestTrue(TEXT("Genuine admitted003 native driver uses actual current Run/room/entity,185HP and40x28 body"),Guard&&Guard->GetStoneGuardDriver()
    &&Guard->GetRuntimeEntityId()!=Game->GetEquipmentView().OwnerId&&Guard->Health==185&&Guard->GetCombatBodyHalfExtent()==FVector2D(40,28)))return false;
  const auto& Bindings=Game->GetWeaponWorldState().ActorBindings;
  if(!Test.TestTrue(TEXT("Actual stable003 World binding is present without a fabricated owner snapshot"),Bindings.ContainsByPredicate([&](const auto& B){return B.EntityId==Guard->GetRuntimeEntityId()&&B.RoomInstanceId==Game->GetEquipmentView().RoomInstanceId&&B.ContentId==TEXT("ENM-STN-003");})))return false;
  Diagnostic(TEXT("admitted-before-tick"));
  for(int32 N=0;N<400&&!State().Action.InProgress&&!Game->bGameOver;++N)Frame(.01f);
  if(!Test.TestTrue(TEXT("Real GameMode clock starts Guard axe after genuine wake"),State().Action.InProgress&&State().Action.Kind==G::EAttack::AxeSweep)){Diagnostic(TEXT("failed-first-axe"));return false;}
  if(!AdvanceTo(State().Action.ActiveAt+.001))return Test.TestTrue(TEXT("Real complete batch reaches active boundary"),false);
  if(!Test.TestTrue(TEXT("Actual immutable window and native once-hit receipt exist before Owner API"),!State().Windows.empty()&&!State().HitReceipts.empty()&&Player->Health<100))return false;
  Guard->ApplyCombatHit(1.6f,Player,85.f);
  if(!Test.TestTrue(TEXT("Real mitigation,receipt and independent closure created by public native damage path"),State().HP==184&&State().ReceivedHits.size()==1&&State().ReceivedHits.front().ActualHPLoss==1
    &&State().Closures.size()==1&&State().Phase==G::EPhase::Stunned&&!State().Issued.empty()))return false;
  // Preserve five nonempty histories, then reach a later genuine live action.
  const uint64 OldAttack=State().Action.AttackId;
  for(int32 N=0;N<650&&State().Action.AttackId==OldAttack&&!Game->bGameOver;++N)Frame(.01f);
  if(!Test.TestTrue(TEXT("Second real attack leaves previous closure/history intact"),State().Action.InProgress&&State().Action.AttackId>OldAttack))return false;
  Diagnostic(TEXT("second-action-before-active"));
  return AdvanceTo(State().Action.ActiveAt+.001)&&Test.TestTrue(TEXT("Every native producer history remains nonempty at complete current root time"),
   State().Time==Game->GetSimulationTime()&&!State().Windows.empty()&&!State().Closures.empty()&&!State().HitReceipts.empty()&&!State().ReceivedHits.empty()&&!State().Issued.empty());
 }
 bool CaptureGuard(FDungeonFighterOwnerSnapshot& Out)
 {
  FString Why;const auto Before=StateSig(State()),OutBefore=OwnerSig(Out);const bool Ok=Guard->CaptureOwnerSnapshot(Out,Why);
  if(!Ok){Test.AddInfo(TEXT("Guard Stage0 exact diagnosis: ")+Why);Test.TestTrue(TEXT("Failed native Guard Capture leaves entire caller owning value unchanged"),OwnerSig(Out)==OutBefore);}
  Test.TestTrue(TEXT("Failed/successful native Capture never changes real Guard producer history"),Before==StateSig(State()));
  return Test.TestTrue(TEXT("Actual003 owner captures its complete supported variant (Stage0 semantic RED)"),Ok);
 }
 FDungeonFighterRestoreContext Context(const FDungeonEquipmentRuntimeSnapshot& E)const
 {FDungeonFighterRestoreContext C;C.RunGuid=E.View.RunGuid;C.RoomInstanceId=E.View.RoomInstanceId;C.EntityId=Guard->GetRuntimeEntityId();C.SimulationTime=Game->GetSimulationTime();C.GameOver=Game->bGameOver;C.Equipment=&E;C.WeaponWorld=&Game->GetWeaponWorldState();return C;}
};
inline bool SealGuard(FGuardWorld& F,FDungeonRunSnapshot& Saved,FDungeonValidatedRun& Sealed)
{
 FDungeonFighterOwnerSnapshot Native;if(!F.CaptureGuard(Native))return false;
 FString Why;if(!F.Test.TestTrue(TEXT("Actual full guarded Run captures through every real current actor"),F.Game->CaptureRunSnapshot(Saved,Why))){F.Test.AddInfo(Why);return false;}
 const bool Ok=FDungeonRunAggregate::Validate(Saved,Sealed,Why);if(!Ok)F.Test.AddInfo(TEXT("Guard aggregate diagnosis: ")+Why);
 return F.Test.TestTrue(TEXT("Real Schema2/BoundV2 guarded aggregate independently seals"),Ok&&Sealed.IsValid()&&Saved.Schema==2&&Saved.Scope==EDungeonRunScope::BoundDevelopmentV2);
}
inline const FDungeonFighterOwnerSnapshot* FindGuard(const FDungeonRunSnapshot& S,uint64 Id)
{return S.Fighters.FindByPredicate([Id](const auto& F){return F.EntityId==Id&&F.Kind==EDungeonFighterOwnerKind::StoneGuard;});}
}
