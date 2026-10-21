#if WITH_DEV_AUTOMATION_TESTS
#include "Misc/AutomationTest.h"
#include "../DungeonFighter.h"
#include "../DungeonGameMode.h"
#include "../DungeonFighterSnapshot.h"
#include "Components/SceneComponent.h"
#include "Engine/Engine.h"
#include "Engine/GameInstance.h"
#include "Engine/World.h"
#include "GameFramework/PlayerController.h"
#include "GameFramework/PlayerInput.h"
#include "InputCoreTypes.h"
#include "Kismet/GameplayStatics.h"
#include <cmath>
#include <type_traits>

namespace
{
namespace FC=DungeonContentCombat;
namespace WA=DungeonWeaponActions;
namespace DK=DungeonDodge;
namespace KN=DungeonStoneKnight;
namespace BT=DungeonStoneBat;
using FS=FDungeonFighterOwnerSnapshot;

// Test-only fieldwise value signature. No C++ padding, object addresses,
// production encoder or RNG computes the expected value.
struct FSignature
{
    TArray<uint8> Bytes;
    template<class T>void One(T X){static_assert(std::is_arithmetic_v<T>||std::is_enum_v<T>);Bytes.Append(reinterpret_cast<const uint8*>(&X),sizeof(X));}
    template<class... T>void V(T... X){(One(X),...);}
    void String(const FString& X){FTCHARToUTF8 U(*X);V(uint64(U.Length()));Bytes.Append(reinterpret_cast<const uint8*>(U.Get()),U.Length());}
    template<class T>void Point(const T& P){V(P.X,P.Y);}
    void Point3(const BT::FPoint& P){V(P.X,P.Y,P.Z);}
    void Origin(const WA::FOrigin& P){V(P.X,P.Y,P.Height);}
    void Key(const FDungeonWorldWeaponKey& K){V(K.OwnerId,K.ActionId,K.EventId,K.SubhitId,K.RoomInstanceId);}
    void Transform(const FTransform& T)
    {const auto P=T.GetTranslation(),S=T.GetScale3D();const auto Q=T.GetRotation();V(P.X,P.Y,P.Z,S.X,S.Y,S.Z,Q.X,Q.Y,Q.Z,Q.W);}
    void CombatAction(const FC::FActionState& A)
    {V(A.Active,A.Locked,A.StartedAirborne,A.WindowIssued,A.Phase,A.Weapon,A.WeaponInstanceId,A.AttackId,A.Stage,
        A.Facing,A.Start,A.LockTime,A.ActiveStart,A.ActiveEnd,A.End,A.Damage,A.Stagger,A.MinRange,A.Range,A.Depth,
        A.MoveMultiplier,A.ActionSpeedPct,A.Shape,A.Critical,A.CritMultiplier);}
    void Combat(const FC::FCombatState& S,bool IncludeInput)
    {
        V(S.Version,S.Weapon,S.WeaponInstanceId,S.NextAttackId,S.NextEventId,S.Time,S.ComboExpiry,S.NextComboStage,
            S.ComboReady,IncludeInput?S.PendingPrimary:false,S.Grounded,S.AirPrimarySpent,S.Dead);CombatAction(S.Action);
        V(uint64(S.IssuedWindows.size()));for(const auto& W:S.IssuedWindows){V(W.AttackId,W.EventId,W.SubhitId,W.Start,W.End);CombatAction(W.FrozenAction);}
        V(uint64(S.HitReceipts.size()));for(const auto& H:S.HitReceipts)V(H.AttackId,H.TargetId,H.SubhitId);
        V(uint64(S.PendingEvents.size()));for(const auto& E:S.PendingEvents){V(E.EventId,E.AttackId,E.Stage,E.SubhitId,E.Kind,E.AtTime,E.WindowEnd);CombatAction(E.Action);}
    }
    void Action(const WA::FAction& A)
    {V(A.Type,A.Phase,A.Weapon,A.InstanceId,A.ActionId,A.Active,A.Locked,A.StartedAirborne,A.ForwardStepIssued,A.NextSubhit,
        A.Facing,A.Start,A.LockAt,A.ActiveAt,A.ActiveEnd,A.End,A.SpeedPct,A.DamagePct,A.StaggerPct,A.ReachPct,A.CritMultiplier,
        A.AmmoCost,A.FocusCost,A.CooldownDuration,A.ReloadSpeedPct,A.FocusCostPct,A.SkillCooldownPct,A.Critical,A.Terminal);}
    void Instance(const WA::FInstance& I){V(I.Weapon,I.InstanceId,I.Ammo,I.ReservedAmmo,I.CooldownDeadline);}
    void Event(const WA::FEvent& E)
    {V(E.EventId,E.ActionId,E.InstanceId,E.SubhitId,E.Kind,E.AtTime,E.WindowEnd,E.Damage,E.Stagger,E.MinRange,E.Range,E.Depth,
        E.ProjectileSpeed,E.SecondTargetRatio,E.BurnDps,E.BurnDuration,E.ForwardStep,E.AmmoConsumed,E.FocusConsumed,E.MaxTargets,E.Shape,E.OriginPolicy);Origin(E.Origin);Action(E.Action);}
    void Weapon(const WA::FState& S)
    {
        V(S.Version,S.Time,S.LastReloadCancelTime,S.EquippedId,S.NextActionId,S.NextEventId,S.AutoReloadPendingId);
        const auto& B=S.Budget;V(B.Focus,B.ReservedFocus,B.LastActualSpend,B.HasActualSpend,B.Grounded,B.AirPrimarySpent,B.Dead);Action(S.Action);
        V(uint64(S.Instances.size()));for(const auto& I:S.Instances)Instance(I);
        V(uint64(S.PendingEvents.size()));for(const auto& E:S.PendingEvents)Event(E);
        V(uint64(S.Issued.size()));for(const auto& E:S.Issued)Event(E);
        V(S.InitialFocus,S.AccruedFocus,S.NextFocusMutationId,uint64(S.FocusHistory.size()));
        for(const auto& R:S.FocusHistory)V(R.MutationId,R.ReceiptId,R.Kind,R.AtTime,R.Requested,R.Applied,R.Before,R.After,R.ReservedBefore,R.RegeneratedBefore);
        V(uint64(S.Registrations.size()));for(const auto& R:S.Registrations){V(R.Kind);Instance(R.Initial);V(R.AtTime,R.ReceiptId,R.ActionCursor,R.EventCursor);}
        V(S.NextImportReceiptId,uint64(S.WeaponRuntimeHistory.size()));for(const auto& R:S.WeaponRuntimeHistory)
        {V(R.EventId,R.Kind,R.AtTime,R.BeforeAmmo,R.AfterAmmo,R.BeforeCooldown,R.AfterCooldown,R.SubhitId);Action(R.Action);}
    }
    void PositionReceipt(const DK::FPositionReceipt& R){V(R.Id,R.AfterActionId,R.AtTime);Point(R.Position);}
    void Dodge(const DK::FState& S)
    {
        V(S.Version,S.OwnerId,S.NextActionId,S.NextEventId,S.DeathEventId,S.NextPositionReceiptId,S.InitialTime,S.Time,S.ReadyAt,S.DeadAt);
        Point(S.InitialPosition);Point(S.Position);V(S.Phase,uint64(S.Records.size()));
        for(const auto& R:S.Records)
        {V(R.ActionId,R.StartEventId,R.BlockEventId,R.FinishEventId);Point(R.Origin);Point(R.Direction);
            V(R.Start,R.End,R.ReadyAt,R.Travelled,R.BlockedAt,R.FinishedAt,R.Block,R.Finish);PositionReceipt(R.OriginReceipt);}
        PositionReceipt(S.LastPositionReceipt);
    }
    void KnightAction(const KN::FAction& A)
    {V(A.AttackId,A.Kind,A.InProgress,A.Locked,A.ActiveIssued,A.Start,A.LockAt,A.ActiveAt,A.PlannedActiveEnd,A.ActiveEnd,A.RecoveryEnd,A.Damage,A.Stagger);
        Point(A.Origin);Point(A.Target);Point(A.Direction);V(A.Stop);}
    void Knight(const KN::FState& S)
    {V(S.Version,S.EntityId,S.NextAttackId,S.NextEventId,S.Time,S.HP,S.PoiseAccum,S.LastPoiseAt,S.ProtectionUntil,S.StunUntil,
        S.CombatStartedAt,S.WakeStartedAt,S.WakeEnd,S.ChargeReadyAt,S.ShieldReadyAt,S.WakeQueued,S.Awakened,S.RewardClaimed,S.Phase);
        Point(S.Position);KnightAction(S.Action);V(uint64(S.ActiveReceipts.size()));for(const auto& R:S.ActiveReceipts){KnightAction(R.FrozenAction);V(R.End,R.EventId);}
        V(uint64(S.HitReceipts.size()));for(const auto& H:S.HitReceipts)V(H.AttackId,H.TargetId);}
    void BatAction(const BT::FAction& A)
    {V(A.AttackId,A.StartEventId,A.LockEventId,A.WindowEventId,A.FinishEventId,A.Kind,A.InProgress,A.Locked,A.Emitted,A.Interrupted,
        A.Missed,A.PathBlocked,A.EndpointFound,A.Start,A.LockAt,A.ActiveAt,A.ActiveEnd,A.NominalEnd,A.CooldownDeadline,A.InterruptedAt,
        A.CompletedAt,A.Damage,A.Stagger,A.RadiusX,A.RadiusY,A.HorizontalBudget,A.HorizontalSpeed);
        Point3(A.Origin);Point3(A.LockedTarget);Point3(A.Endpoint);}
    void Bat(const BT::FState& S)
    {
        V(S.Version,S.EntityId,S.NextAttackId,S.NextEventId,S.LastDamageReceiptId,S.InitialTime,S.Time,S.HP,S.PoiseAccum,S.PoiseDecayOrigin,
            S.LastPoiseAt,S.ProtectionUntil,S.StunUntil,S.CombatStartedAt,S.WakeStartedAt,S.WakeEnd,S.PeckReadyAt,S.WingReadyAt,S.LowStartedAt,
            S.LowReadyAt,S.RiseStartedAt,S.HighIdleEligibleSince,S.WakeQueued,S.Awakened,S.PendingLow,S.RewardClaimed,S.LowLegal,S.Phase,S.ResumePhase);
        Point3(S.InitialPosition);Point3(S.Position);Point3(S.RiseOrigin);BatAction(S.Action);
        V(uint64(S.Actions.size()));for(const auto& A:S.Actions)BatAction(A);
        V(uint64(S.ReceivedHits.size()));for(const auto& H:S.ReceivedHits)V(H.ReceiptId,H.AtTime,H.HPLoss,H.Stagger);
        V(uint64(S.HitReceipts.size()));for(const auto& H:S.HitReceipts)V(H.AttackId,H.TargetId,H.AtTime);
        V(uint64(S.Issued.size()));for(const auto& E:S.Issued)
        {V(E.EventId,E.EntityId,E.TargetId,E.Kind,E.AtTime,E.EndTime,E.Amount);Point3(E.From);Point3(E.To);BatAction(E.Action);}
    }
    void Pose(const DungeonWeaponPoseSocket::FResolved& P)
    {V(P.Supported,P.CustomOverride,P.GroundPoseFallback,P.Clip,P.Frame,P.WeaponStateIndex,P.SampleTime,P.InstanceId,P.ActionId,P.Facing,
        P.RootX,P.RootY,P.BodySize,P.GripX,P.GripY,P.SupportX,P.SupportY,P.ComponentSupportX,P.ComponentSupportY,P.ComponentEmitX,
        P.ComponentEmitY,P.ComponentGripX,P.ComponentGripY,P.EmitX,P.EmitY,P.Angle,P.Scale);Origin(P.ActorOrigin);Origin(P.CombatOrigin);Origin(P.PresentationOrigin);}
    void Owner(const FS& S,bool IncludeInput=true)
    {
        V(S.Schema,S.RunGuid.A,S.RunGuid.B,S.RunGuid.C,S.RunGuid.D,S.RoomInstanceId,S.EntityId,S.Kind);Point(S.GroundPosition);
        V(S.Health,S.MaxHealth,S.JumpHeight,S.JumpVelocity,S.Facing,S.Enemy,S.AIEnabled,S.Dead,S.DeathReported,S.Coins);String(S.EnemyContentId);String(S.WeaponId);String(S.ArmorId);
        V(S.FocusMirror,S.InvulnerableTime,S.HurtTime,S.AttackCooldown,S.PoiseAccumulation,S.PoiseDecayDelay,S.PoiseProtection,S.AirPrimarySpent);Key(S.HurtProtectionSource);V(S.LastSkillEventId);
        V(uint64(S.EmissionPoseSockets.size()));for(const auto& P:S.EmissionPoseSockets){V(P.EventId,P.ActionId,P.SubhitId);Pose(P.Pose);}
        V(uint64(S.SkillWindows.size()));for(const auto& E:S.SkillWindows)Event(E);
        V(uint64(S.SkillHitReceipts.size()));for(const auto& H:S.SkillHitReceipts)V(H.ActionId,H.SubhitId,H.TargetId);
        V(S.AttackElapsed,S.ArmorChangeRemaining,S.FocusConsumeAge,S.AttackResolved,S.HasAxe);String(S.PendingArmorId);
        V(S.AttackTime,S.HitFlash,S.AnimationTime,S.LandingVisualAge,S.ComboStage,S.Moving);String(S.AnimationName);String(S.AttackPhase);
        Transform(S.HeightAnchorRelative);V(S.CustomMuzzle);Transform(S.CustomMuzzleRelative);V(S.BatObservedHeight,S.Player.IsSet(),S.Knight.IsSet(),S.Bat.IsSet());
        if(S.Player.IsSet()){Combat(S.Player.GetValue().Combat,IncludeInput);Weapon(S.Player.GetValue().WeaponActions);Dodge(S.Player.GetValue().Dodge);}
        if(S.Knight.IsSet())Knight(S.Knight.GetValue());if(S.Bat.IsSet())Bat(S.Bat.GetValue());
    }
};
TArray<uint8> Signature(const FS& S,bool IncludeInput=true){FSignature X;X.Owner(S,IncludeInput);return X.Bytes;}
struct FCrossRoomOwnerFixture
{
    FAutomationTestBase& Test;
    UWorld* World=nullptr;
    ADungeonGameMode* Game=nullptr;
    ADungeonFighter* Player=nullptr;
    APlayerController* Controller=nullptr;
    explicit FCrossRoomOwnerFixture(FAutomationTestBase& InTest):Test(InTest){}
    ~FCrossRoomOwnerFixture()
    {if(World){World->DestroyWorld(false);if(GEngine)GEngine->DestroyWorldContext(World);}}
    bool Create()
    {
        if(!GEngine)return false;
        const auto Settings=UWorld::InitializationValues().AllowAudioPlayback(false).CreatePhysicsScene(true)
            .RequiresHitProxies(false).CreateNavigation(false).CreateAISystem(false)
            .ShouldSimulatePhysics(false).SetTransactional(false);
        World=UWorld::CreateWorld(EWorldType::Game,false,NAME_None,nullptr,true,ERHIFeatureLevel::Num,&Settings);
        if(!World)return false;
        GEngine->CreateNewWorldContext(EWorldType::Game).SetCurrentWorld(World);
        World->SetGameInstance(NewObject<UGameInstance>(GEngine));FURL URL;
        URL.AddOption(TEXT("game=/Script/CodexDungeon.DungeonGameMode"));
        if(!World->SetGameMode(URL))return false;
        Game=World->GetAuthGameMode<ADungeonGameMode>();
        Player=World->SpawnActor<ADungeonFighter>();Controller=World->SpawnActor<APlayerController>();
        if(!Game||!Player||!Controller)return false;
        World->AddController(Controller);Controller->Possess(Player);
        if(!Controller->PlayerInput)Controller->PlayerInput=NewObject<UPlayerInput>(Controller);
        if(!Controller->IsLocalController()||UGameplayStatics::GetPlayerController(Game,0)!=Controller)return false;
        Game->PlayerFighter=Player;
        // The only genuine new-Run initialization. Restore never calls Begin,
        // Reset, InitializeStone*, Admit or a QA identity/map setter.
        if(!Game->BeginSceneExplorationPreview()||Game->Enemies.Num()!=1
            ||!Game->Enemies[0]->GetStoneKnightDriver()||Game->GetSimulationTime()!=0.)return false;
        // Same explicit time-zero AI control as the existing real Scene/World
        // fixture. HP, positions, map, room-clear and death facts are untouched.
        Game->Enemies[0]->bAIEnabled=false;
        return Pulse(EKeys::Enter)&&!Game->bWaitingForStart;
    }
    void Frame(float Dt)
    {
        Game->Tick(Dt);Controller->PlayerInput->Tick(Dt);
        TArray<UInputComponent*> Stack;Controller->PlayerInput->ProcessInputStack(Stack,Dt,false);
    }
    bool Key(FKey Code,bool Down)
    {
        Controller->InputKey(FInputKeyParams(Code,Down?IE_Pressed:IE_Released,Down?1.:0.));
        Controller->PlayerInput->Tick(.005f);TArray<UInputComponent*> Stack;
        Controller->PlayerInput->ProcessInputStack(Stack,.005f,false);
        return Controller->IsInputKeyDown(Code)==Down;
    }
    bool Pulse(FKey Code)
    {
        if(!Key(Code,true)||!Controller->WasInputKeyJustPressed(Code))return false;
        Frame(.005f);if(!Key(Code,false))return false;Frame(.005f);return true;
    }
    bool AdvanceTo(double At)
    {
        if(At<Game->GetSimulationTime())return false;
        for(int32 Count=0;Count<64&&Game->GetSimulationTime()<At;++Count)
        {
            const double Before=Game->GetSimulationTime(),Remaining=At-Before;
            float Dt=float(Remaining);if(double(Dt)>Remaining)Dt=std::nextafter(Dt,0.f);
            if(!(Dt>0.f))return false;Frame(Dt);
            if(Game->GetSimulationTime()<=Before)return false;
        }
        return Game->GetSimulationTime()==At&&!Game->bGameOver;
    }
    bool MoveX(double Target)
    {
        for(int32 Count=0;Count<1600;++Count)
        {
            const double Delta=Target-Player->GetGroundPosition().X;
            if(FMath::Abs(Delta)<.002){Frame(.005f);return true;}
            const FKey Direction=Delta>0.?EKeys::D:EKeys::A;
            if(!Key(Direction,true))return false;
            Frame(float(FMath::Min(.02,FMath::Abs(Delta)/double(Player->GetMoveSpeed()))));
            if(!Key(Direction,false)||Game->bGameOver)return false;
        }
        Test.AddError(TEXT("Normal cross-room movement did not reach its waypoint"));return false;
    }
    bool ProveOwner(ADungeonFighter* Actor,const TCHAR* Label)
    {
        const auto Equipment=Game->CaptureEquipmentSnapshot();const auto SavedWorld=Game->GetWeaponWorldState();
        const auto AudioNext=Game->GetActionAudioState().NextSequence;
        const auto PickupCount=Game->Pickups.Num();
        FS Saved;FString Why;const bool Captured=Actor->CaptureOwnerSnapshot(Saved,Why);
        Test.AddInfo(FString::Printf(TEXT("Cross-room owner actual observation [%s]: room=%llu entity=%llu captured=%d why=%s"),
            Label,static_cast<unsigned long long>(Equipment.View.RoomInstanceId),
            static_cast<unsigned long long>(Actor->GetRuntimeEntityId()),Captured,*Why));
        if(!Test.TestTrue(*(FString(Label)+TEXT(" default actual GM-bound Capture succeeds")),Captured))return false;
        if(!Test.TestTrue(*(FString(Label)+TEXT(" keeps current snapshot scope and exact public body facts")),
            Saved.Schema==2&&Saved.RunGuid==Equipment.View.RunGuid&&Saved.RoomInstanceId==Equipment.View.RoomInstanceId
            &&Saved.EntityId==Actor->GetRuntimeEntityId()&&Saved.GroundPosition==Actor->GetGroundPosition()
            &&Saved.Health==Actor->Health&&Saved.Dead==Actor->bDead&&Saved.DeathReported==Actor->bDeathReported))return false;
        FDungeonFighterRestoreContext Context;
        Context.RunGuid=Saved.RunGuid;Context.RoomInstanceId=Saved.RoomInstanceId;Context.EntityId=Saved.EntityId;
        Context.SimulationTime=Game->GetSimulationTime();Context.GameOver=Game->bGameOver;
        Context.Equipment=&Equipment;Context.WeaponWorld=&SavedWorld;
        auto Staging=World->SpawnActor<ADungeonFighter>();
        if(!Test.TestNotNull(TEXT("Independent staging Actor has its own native components"),Staging))return false;
        Staging->SetActorTickEnabled(false);
        const bool Restored=Staging->RestoreOwnerSnapshot(Saved,Context,Why);
        if(!Restored)Test.AddInfo(FString(Label)+TEXT(" staging Restore diagnosis: ")+Why);
        const bool Accepted=Test.TestTrue(*(FString(Label)+TEXT(" restores with actual saved context without allocating a world identity")),Restored);
        if(Accepted)
        {
            FS Read;const bool Recaptured=Staging->CaptureOwnerSnapshot(Read,Why,&Context);
            if(!Recaptured)Test.AddInfo(FString(Label)+TEXT(" explicit staging Capture diagnosis: ")+Why);
            if(Test.TestTrue(*(FString(Label)+TEXT(" explicit staging Capture succeeds")),Recaptured))
                Test.TestTrue(*(FString(Label)+TEXT(" complete owner signature including native anchor stays exact")),
                    Signature(Saved,false)==Signature(Read,false)
                    &&Staging->GetGroundPosition()==Saved.GroundPosition
                    &&Staging->GetWeaponMuzzleComponent()->GetAttachParent()->GetRelativeTransform().Equals(Saved.HeightAnchorRelative,0.));
            const auto Exact=Signature(Read);const auto Native=Staging->GetWeaponMuzzleComponent()->GetComponentTransform();
            const auto RejectBinding=[&](const TCHAR* Reason,auto Mutate)
            {
                auto BadWorld=SavedWorld;Mutate(BadWorld);auto BadContext=Context;BadContext.WeaponWorld=&BadWorld;
                FString BadWhy;
                Test.TestFalse(*(FString(Label)+TEXT(" rejects ")+Reason),Staging->RestoreOwnerSnapshot(Saved,BadContext,BadWhy));
                Test.TestTrue(*(FString(Label)+TEXT(" diagnoses ")+Reason),!BadWhy.IsEmpty());
                FS After;
                if(Test.TestTrue(*(FString(Label)+TEXT(" remains observable after rejected ")+Reason),Staging->CaptureOwnerSnapshot(After,BadWhy,&Context)))
                    Test.TestTrue(*(FString(Label)+TEXT(" preserves complete owner/native state after rejected ")+Reason),
                        Signature(After)==Exact&&Staging->GetWeaponMuzzleComponent()->GetComponentTransform().Equals(Native,0.));
            };
            RejectBinding(TEXT("future-room player birth binding"),[&](auto& BadWorld)
            {for(auto& Binding:BadWorld.ActorBindings)if(Binding.EntityId==Equipment.View.OwnerId)Binding.RoomInstanceId=Equipment.View.RoomInstanceId+1;});
            RejectBinding(TEXT("wrong player content binding"),[&](auto& BadWorld)
            {for(auto& Binding:BadWorld.ActorBindings)if(Binding.EntityId==Equipment.View.OwnerId)Binding.ContentId=TEXT("ENM-STN-001");});
            if(Saved.Kind!=EDungeonFighterOwnerKind::BoundPlayer&&Saved.RoomInstanceId>1)
                RejectBinding(TEXT("past-room current enemy binding"),[&](auto& BadWorld)
                {for(auto& Binding:BadWorld.ActorBindings)if(Binding.EntityId==Saved.EntityId)Binding.RoomInstanceId=Saved.RoomInstanceId-1;});
        }
        Test.TestTrue(*(FString(Label)+TEXT(" cannot alter Run room identities, receipts, rewards or RNG")),
            Game->GetEquipmentView().RunGuid==Equipment.View.RunGuid
            &&Game->GetEquipmentView().RoomInstanceId==Equipment.View.RoomInstanceId
            &&Game->GetEquipmentView().Revision==Equipment.View.Revision
            &&Game->GetEquipmentView().NextCritDraw==Equipment.View.NextCritDraw
            &&Game->GetWeaponWorldState().NextEntityId==SavedWorld.NextEntityId
            &&Game->GetWeaponWorldState().NextEventSequence==SavedWorld.NextEventSequence
            &&Game->GetActionAudioState().NextSequence==AudioNext&&Game->Pickups.Num()==PickupCount);
        Staging->Destroy();return Accepted;
    }
};
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDungeonRunAggregateCrossRoomOwners,
    "CodexDungeon.Content.RunAggregate.CrossRoomOwners",
    EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FDungeonRunAggregateCrossRoomOwners::RunTest(const FString&)
{
    FCrossRoomOwnerFixture Fixture(*this);
    if(!TestTrue(TEXT("Actual Scene new-Run and normal Enter fixture"),Fixture.Create()))return false;
    const auto BirthRun=Fixture.Game->GetEquipmentView().RunGuid;
    const auto BirthRoom=Fixture.Game->GetEquipmentView().RoomInstanceId;
    const auto PlayerId=Fixture.Player->GetRuntimeEntityId();
    const auto OldKnight=Fixture.Game->Enemies[0].Get();const uint64 OldKnightId=OldKnight->GetRuntimeEntityId();
    if(!TestTrue(TEXT("Both initial default owner captures and independent restores are positive controls"),
        Fixture.ProveOwner(Fixture.Player,TEXT("Room1 player"))&&Fixture.ProveOwner(OldKnight,TEXT("Room1 knight"))))return false;
    if(!TestTrue(TEXT("Normal movement reaches the original knight without changing its HP or room facts"),Fixture.MoveX(220.)))return false;
    for(int32 Attacks=0;Attacks<12&&!OldKnight->bDead;++Attacks)
        if(!Fixture.Pulse(EKeys::J)||!Fixture.AdvanceTo(Fixture.Game->GetSimulationTime()+.8))return false;
    if(!TestTrue(TEXT("Normal sword input truly killed and claimed original knight and cleared the room"),
        OldKnight->bDead&&OldKnight->bDeathReported&&OldKnight->GetStoneKnightDriver()->State().RewardClaimed
        &&Fixture.Game->bRoomCleared&&!Fixture.Game->bGameOver))return false;
    if(!TestTrue(TEXT("Normal movement reaches existing scene exit"),Fixture.MoveX(1180.))||!Fixture.Pulse(EKeys::E))return false;
    if(!TestTrue(TEXT("Fresh E opens original-room exit confirmation without changing the room"),
        Fixture.Game->GetSceneInteractionView().Pending&&Fixture.Game->GetSceneInteractionView().NeedsConfirmation
        &&Fixture.Game->GetEquipmentView().RoomInstanceId==BirthRoom))return false;
    if(!TestTrue(TEXT("Fresh Enter commits actual free room transfer"),Fixture.Pulse(EKeys::Enter)))return false;
    if(!TestTrue(TEXT("Same Run player survives transfer and new real knight uses a different stable identity"),
        Fixture.Game->GetEquipmentView().RunGuid==BirthRun
        &&Fixture.Game->GetEquipmentView().RoomInstanceId==BirthRoom+1&&Fixture.Game->RoomNumber==2
        &&Fixture.Player==Fixture.Game->PlayerFighter&&Fixture.Player->GetRuntimeEntityId()==PlayerId
        &&Fixture.Game->Enemies.Num()==1&&Fixture.Game->Enemies[0]->GetStoneKnightDriver()
        &&Fixture.Game->Enemies[0]->GetRuntimeEntityId()!=OldKnightId&&!Fixture.Game->bRoomCleared))return false;
    bool PlayerBirth=false,OldKnightBinding=false,NewKnightBinding=false;int32 PlayerBindings=0;
    const auto NewKnight=Fixture.Game->Enemies[0].Get();
    for(const auto& Binding:Fixture.Game->GetWeaponWorldState().ActorBindings)
    {
        if(Binding.EntityId==PlayerId)
        {++PlayerBindings;PlayerBirth=Binding.ContentId==TEXT("player")&&Binding.RoomInstanceId==BirthRoom;}
        OldKnightBinding|=Binding.EntityId==OldKnightId&&Binding.RoomInstanceId==BirthRoom&&Binding.ContentId==TEXT("ENM-STN-001");
        NewKnightBinding|=Binding.EntityId==NewKnight->GetRuntimeEntityId()&&Binding.RoomInstanceId==BirthRoom+1&&Binding.ContentId==TEXT("ENM-STN-001");
    }
    if(!TestTrue(TEXT("Real player birth binding remains singular in room1 with old tombstone and new room2 knight"),
        PlayerBindings==1&&PlayerBirth&&OldKnightBinding&&NewKnightBinding))return false;
    // Both observations are attempted independently so actual RED identifies
    // the player-binding premise for the new knight as well as the player.
    const bool PlayerProof=Fixture.ProveOwner(Fixture.Player,TEXT("Room2 player"));
    const bool KnightProof=Fixture.ProveOwner(NewKnight,TEXT("Room2 knight"));
    return PlayerProof&&KnightProof;
}
#endif
