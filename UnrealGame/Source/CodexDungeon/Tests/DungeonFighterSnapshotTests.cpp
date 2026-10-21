#if WITH_DEV_AUTOMATION_TESTS
#include "Misc/AutomationTest.h"
#include "../DungeonFighter.h"
#include "../DungeonGameMode.h"
#include "../DungeonFighterSnapshot.h"
#include "Components/SceneComponent.h"
#include "Engine/Engine.h"
#include "Engine/GameInstance.h"
#include "Engine/World.h"
#include <cmath>
#include <limits>
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
struct FContextValue
{
    FDungeonEquipmentRuntimeSnapshot Equipment;
    FDungeonWeaponWorldState World;
    FDungeonFighterRestoreContext Context;
    FContextValue(ADungeonGameMode* G,ADungeonFighter* F):Equipment(G->CaptureEquipmentSnapshot()),World(G->GetWeaponWorldState())
    {Context.RunGuid=Equipment.View.RunGuid;Context.RoomInstanceId=Equipment.View.RoomInstanceId;Context.EntityId=F->GetRuntimeEntityId();
        Context.SimulationTime=G->GetSimulationTime();Context.GameOver=G->bGameOver;Context.Equipment=&Equipment;Context.WeaponWorld=&World;}
    FContextValue(const FContextValue&)=delete;
};
struct FActorWorld
{
    UWorld* World=nullptr;ADungeonGameMode* Game=nullptr;ADungeonFighter* Player=nullptr;
    ~FActorWorld(){if(World){World->DestroyWorld(false);if(GEngine)GEngine->DestroyWorldContext(World);}}
    bool Create()
    {
        if(!GEngine)return false;
        const auto Settings=UWorld::InitializationValues().AllowAudioPlayback(false).CreatePhysicsScene(true).RequiresHitProxies(false)
            .CreateNavigation(false).CreateAISystem(false).ShouldSimulatePhysics(false).SetTransactional(false);
        World=UWorld::CreateWorld(EWorldType::Game,false,NAME_None,nullptr,true,ERHIFeatureLevel::Num,&Settings);if(!World)return false;
        GEngine->CreateNewWorldContext(EWorldType::Game).SetCurrentWorld(World);
        World->SetGameInstance(NewObject<UGameInstance>(GEngine));FURL URL;URL.AddOption(TEXT("game=/Script/CodexDungeon.DungeonGameMode"));
        if(!World->SetGameMode(URL))return false;Game=World->GetAuthGameMode<ADungeonGameMode>();Player=World->SpawnActor<ADungeonFighter>();if(!Game||!Player)return false;
        Player->SetActorTickEnabled(false);Player->ResetFighter({0,0});Game->PlayerFighter=Player;Game->bWaitingForStart=false;Game->bGameOver=false;
        return Game->BeginEquipmentRun(EDungeonEquipmentRunConfig::IntegrationPreview,1)&&Player->IsEquipmentBound();
    }
    bool AdvanceTo(double At)
    {
        for(int N=0;N<16&&Game->GetSimulationTime()<At;++N)
        {const double Left=At-Game->GetSimulationTime();float Step=float(Left);if(double(Step)>Left)Step=std::nextafter(Step,0.f);
            if(!(Step>0.f))return false;const double Before=Game->GetSimulationTime();Game->Tick(Step);if(Game->GetSimulationTime()<=Before)return false;}
        return Game->GetSimulationTime()==At;
    }
    template<class T>bool Until(T Predicate,int Limit=800)
    {for(int N=0;N<Limit&&!Predicate();++N)if(!AdvanceTo(Game->GetSimulationTime()+.01))return false;return Predicate();}
    bool Crossbow()
    {
        DungeonEquipmentInventory::FItem I;I.ContentId="WPN-XBW-001";I.Ammo=1.;
        const auto R=Game->RegisterEquipmentSource(TEXT("qa.fighter.snapshot.loaded-xbw"),I,{40,0});
        return R.Ok()&&Game->SelectEquipmentSource(R.SourceId)&&Game->TryInteractEquipment()
            &&AdvanceTo(Player->GetEquipmentActionDeadline())&&Player->WeaponId==TEXT("WPN-XBW-001");
    }
    ADungeonFighter* Knight(FVector2D At={200,0})
    {
        auto K=World->SpawnActor<ADungeonFighter>();if(!K)return nullptr;
        K->SetActorTickEnabled(false);K->bEnemy=true;K->bAIEnabled=false;K->EnemyContentId=TEXT("ENM-STN-001");K->ResetFighter(At);Game->Enemies.Add(K);
        if(!AdvanceTo(Game->GetSimulationTime()+.001)||!K->GetRuntimeEntityId()||!K->InitializeStoneKnight(K->GetRuntimeEntityId(),Game->GetSimulationTime()))return nullptr;
        return K;
    }
    bool Capture(FAutomationTestBase& T,ADungeonFighter* F,FS& S,const TCHAR* Label)
    {
        FString Why;const bool Captured=F->CaptureOwnerSnapshot(S,Why);
        if(!Captured)T.AddInfo(FString::Printf(TEXT("Owner capture diagnosis [%s]: %s"),Label,*Why));
        if(!T.TestTrue(*(FString(Label)+TEXT(" actual owner capture succeeds")),Captured))return false;
        const auto& V=Game->GetEquipmentView();
        T.TestTrue(*(FString(Label)+TEXT(" captures actual stable scope and public body facts")),S.Schema==2&&S.RunGuid==V.RunGuid
            &&S.RoomInstanceId==V.RoomInstanceId&&S.EntityId==F->GetRuntimeEntityId()&&S.GroundPosition==F->GetGroundPosition()
            &&S.Health==F->Health&&S.MaxHealth==F->MaxHealth&&S.JumpHeight==F->JumpHeight&&S.JumpVelocity==F->GetVerticalVelocity()
            &&S.Facing==F->Facing&&S.Dead==F->bDead&&S.DeathReported==F->bDeathReported);
        return true;
    }
    bool RoundTrip(FAutomationTestBase& T,ADungeonFighter* Source,const FS& Saved,FS& Out,const TCHAR* Label)
    {
        FContextValue C(Game,Source);const auto BeforeIds=Game->GetWeaponWorldState().NextEntityId;
        const auto BeforeSequence=Game->GetWeaponWorldState().NextEventSequence;
        const auto BeforeAudio=Game->GetActionAudioState().NextSequence;const auto BeforeRevision=Game->GetEquipmentView().Revision;
        const auto Pickups=Game->Pickups.Num();auto Target=World->SpawnActor<ADungeonFighter>();
        if(!T.TestNotNull(TEXT("Independent staging Actor exists"),Target))return false;Target->SetActorTickEnabled(false);
        FString Why;const bool Restored=Target->RestoreOwnerSnapshot(Saved,C.Context,Why);
        if(!Restored)T.AddInfo(FString::Printf(TEXT("Owner restore diagnosis [%s]: %s"),Label,*Why));
        const bool Accepted=T.TestTrue(*(FString(Label)+TEXT(" independent staging restore succeeds")),Restored);
        bool Captured=false;if(Accepted)
        {
            const bool Recaptured=Target->CaptureOwnerSnapshot(Out,Why,&C.Context);
            if(!Recaptured)T.AddInfo(FString::Printf(TEXT("Staging recapture diagnosis [%s]: %s"),Label,*Why));
            Captured=T.TestTrue(*(FString(Label)+TEXT(" explicit approved staging context recaptures complete owner")),Recaptured);
            if(Captured)
            {
                T.TestTrue(*(FString(Label)+TEXT(" full owner values remain exact except unaccepted buffered primary")),Signature(Saved,false)==Signature(Out,false));
                if(Out.Player.IsSet())T.TestFalse(TEXT("Continue does not retain an unaccepted buffered primary"),Out.Player.GetValue().Combat.PendingPrimary);
                T.TestTrue(*(FString(Label)+TEXT(" real component/body observations match restored values")),Target->GetGroundPosition()==Saved.GroundPosition
                    &&Target->Health==Saved.Health&&Target->JumpHeight==Saved.JumpHeight&&Target->GetVerticalVelocity()==Saved.JumpVelocity
                    &&Target->Facing==Saved.Facing&&Target->bDead==Saved.Dead&&Target->bDeathReported==Saved.DeathReported);
                if(Saved.Kind==EDungeonFighterOwnerKind::StoneBat)
                    T.TestTrue(TEXT("Bat physical height retains its exact double authority"),Target->GetCombatHeight()==Saved.BatObservedHeight);
                if(Saved.CustomMuzzle)T.TestTrue(TEXT("Independent native muzzle retains actual custom relative transform"),Target->GetWeaponMuzzleComponent()->GetRelativeTransform().Equals(Saved.CustomMuzzleRelative,0.));
                T.TestTrue(TEXT("Staging components are independently owned"),Target->GetWeaponMuzzleComponent()!=Source->GetWeaponMuzzleComponent());
            }
        }
        T.TestTrue(TEXT("Owner restore/capture allocates no world IDs, actions, audio facts or death rewards"),Game->GetWeaponWorldState().NextEntityId==BeforeIds
            &&Game->GetWeaponWorldState().NextEventSequence==BeforeSequence&&Game->GetActionAudioState().NextSequence==BeforeAudio
            &&Game->GetEquipmentView().Revision==BeforeRevision&&Game->Pickups.Num()==Pickups);
        Target->Destroy();return Accepted&&Captured;
    }
};
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FFighterOwnerPlayer,
    "CodexDungeon.Content.FighterOwnerSnapshot.PlayerAcceptedActionsAndProtection",
    EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FFighterOwnerPlayer::RunTest(const FString& Parameters)
{
    {
        FActorWorld F;if(!TestTrue(TEXT("Actual combo world starts bound"),F.Create()))return false;
        F.Player->BeginAttack();const auto A=F.Player->GetMeleeCombatState().Action;
        if(!TestTrue(TEXT("Real primary accepted, reaches its actual recovery buffer"),A.Active&&F.AdvanceTo(A.End-.1)))return false;
        F.Player->BeginAttack();if(!TestTrue(TEXT("Normal fresh press created only an unaccepted buffered primary"),F.Player->GetMeleeCombatState().PendingPrimary
            &&F.Player->GetMeleeCombatState().NextAttackId==2))return false;
        FS S,R;if(F.Capture(*this,F.Player,S,TEXT("Accepted melee and pending input"))&&F.RoundTrip(*this,F.Player,S,R,TEXT("Accepted melee and pending input")))
        {
            TestTrue(TEXT("Accepted attack/lock/deadlines/next IDs survive while buffer is cleared"),S.Player.IsSet()&&R.Player.IsSet()
                &&S.Player.GetValue().Combat.PendingPrimary&&!R.Player.GetValue().Combat.PendingPrimary
                &&R.Player.GetValue().Combat.Action.AttackId==A.AttackId&&R.Player.GetValue().Combat.Action.End==A.End);
            FC::FCombatKernel K;if(!TestTrue(TEXT("Restored complete combat state is accepted by real pure kernel"),K.Restore(R.Player.GetValue().Combat)))return false;
            FC::FAttackContext C;C.CanStart=false;C.Grounded=true;K.StepTo(A.End,C);
            TestTrue(TEXT("No old buffered press becomes a new accepted attack; genuine combo window remains"),K.State().NextAttackId==2
                &&K.State().ComboReady&&K.State().ComboExpiry==A.End+.45&&!K.State().Action.Active);
        }
        FActorWorld Ready;if(!TestTrue(TEXT("Independent actual combo-ready world starts"),Ready.Create()))return false;
        Ready.Player->BeginAttack();const auto End=Ready.Player->GetMeleeCombatState().Action.End;
        if(!TestTrue(TEXT("Normal first attack completes into accepted combo window"),Ready.AdvanceTo(End)&&Ready.Player->GetMeleeCombatState().ComboReady))return false;
        FS Q,U;if(Ready.Capture(*this,Ready.Player,Q,TEXT("Accepted combo window")))Ready.RoundTrip(*this,Ready.Player,Q,U,TEXT("Accepted combo window"));
    }
    {
        FActorWorld F;if(!TestTrue(TEXT("Actual dodge world starts"),F.Create())||!TestTrue(TEXT("Normal public dodge accepts fresh ground direction"),F.Player->TryBeginDodge({1,0},true))
            ||!TestTrue(TEXT("Actual GM reaches .10 protected interval"),F.AdvanceTo(.1)))return false;
        F.Player->ApplyCombatHit(5.f,nullptr,0.f);
        if(!TestTrue(TEXT("Real protected dodge rejected damage without losing health"),F.Player->Health==100.f&&F.Player->IsDodgeInvulnerableAt(.1)))return false;
        FS S,R;if(F.Capture(*this,F.Player,S,TEXT("Actual protected dodge"))&&F.RoundTrip(*this,F.Player,S,R,TEXT("Actual protected dodge")))
        {
            const auto& D=R.Player.GetValue().Dodge;DK::FDodgeKernel K(D.OwnerId,D.InitialTime,D.InitialPosition);
            if(!TestTrue(TEXT("Exact initial owner/origin permits strict dodge restore"),K.Restore(D)))return false;
            const auto Out=K.StepTo(.4,[](const DK::FSweepRequest&){return DK::FSweepResult{};});
            TestTrue(TEXT("Restored unblocked dodge completes once at original distance/cooldown"),Out.Accepted&&K.State().Position.X==185.
                &&K.State().Position.Y==0.&&K.State().ReadyAt==1.2&&K.State().Records.size()==1&&K.State().Records[0].FinishedAt==.4);
        }
    }
    {
        FActorWorld F;if(!TestTrue(TEXT("Actual hurt/poise world starts"),F.Create()))return false;
        F.Player->ApplyCombatHit(5.f,nullptr,30.f);
        if(!TestTrue(TEXT("Real hit broke base poise and rejects another direct hit"),F.Player->Health==95.f&&!F.Player->CanStartAttack()
            &&!F.Player->CanReceiveDirectHit())||!TestTrue(TEXT("Actual timers advance once through central tick"),F.AdvanceTo(.05)))return false;
        FS S,R;if(F.Capture(*this,F.Player,S,TEXT("Hurt and poise protection")))
        {
            TestTrue(TEXT("Captured remaining protection is actual nonzero state, not inferred from health"),S.InvulnerableTime>.55f&&S.HurtTime>.3f
                &&S.PoiseProtection>.9f&&S.PoiseAccumulation==0.f&&S.PoiseDecayDelay>0.f);
            F.RoundTrip(*this,F.Player,S,R,TEXT("Hurt and poise protection"));
        }
    }
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FFighterOwnerCrossbow,
    "CodexDungeon.Content.FighterOwnerSnapshot.CrossbowEmissionReloadAndFrozenOrigin",
    EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FFighterOwnerCrossbow::RunTest(const FString& Parameters)
{
    FActorWorld F;if(!TestTrue(TEXT("Actual loaded crossbow is acquired by ordinary equipment action"),F.Create()&&F.Crossbow()))return false;
    F.Player->MoveOnGround({-1,0},.01f);if(!TestTrue(TEXT("Real movement establishes left facing"),F.AdvanceTo(F.Game->GetSimulationTime()+.01)&&F.Player->Facing==-1.f))return false;
    F.Player->GetWeaponMuzzleComponent()->SetRelativeLocation({24.,7.,0.});F.Player->StartJump();
    if(!TestTrue(TEXT("Accepted jump advances to positive physical height"),F.AdvanceTo(F.Game->GetSimulationTime()+.1)
        &&F.Player->JumpHeight>0.f&&!F.Player->GetWeaponActionsState().Budget.Grounded))return false;
    F.Player->BeginAttack();const auto Shot=F.Player->GetWeaponActionsState().Action;
    if(!TestTrue(TEXT("Actual airborne left primary is accepted"),Shot.Active&&Shot.StartedAirborne&&Shot.Facing==-1.)
        ||!TestTrue(TEXT("Real emission is reached at its own boundary"),F.AdvanceTo(Shot.ActiveAt)
        &&F.Game->GetWeaponWorldState().Projectiles.Num()==1&&F.Player->GetWeaponActionsState().Issued.size()==1))return false;
    const auto FrozenProjectile=F.Game->GetWeaponWorldState().Projectiles[0];
    FS S,R;if(F.Capture(*this,F.Player,S,TEXT("Frozen airborne custom emission")))
    {
        TestTrue(TEXT("Capture includes exact accepted emission socket and physical custom definition"),S.Player.IsSet()&&S.CustomMuzzle
            &&S.CustomMuzzleRelative.GetTranslation()==FVector(24.,7.,0.)&&S.EmissionPoseSockets.size()==1
            &&S.EmissionPoseSockets[0].EventId==FrozenProjectile.Source.EventId
            &&S.EmissionPoseSockets[0].Pose.CombatOrigin.X==FrozenProjectile.Source.Origin.X
            &&S.EmissionPoseSockets[0].Pose.CombatOrigin.Y==FrozenProjectile.Source.Origin.Y
            &&S.EmissionPoseSockets[0].Pose.CombatOrigin.Height==FrozenProjectile.Source.Origin.Height);
        F.RoundTrip(*this,F.Player,S,R,TEXT("Frozen airborne custom emission"));
    }
    if(!TestTrue(TEXT("Actual primary completes and later real landing starts auto reload"),F.AdvanceTo(Shot.End)
        &&F.Until([&]{return F.Player->GetWeaponActionsState().Action.Active&&F.Player->GetWeaponActionsState().Action.Type==WA::EAction::Reload;})))return false;
    const auto Reload=F.Player->GetWeaponActionsState().Action;
    if(!TestTrue(TEXT("Real reload reaches inserted-but-unfilled stage"),F.AdvanceTo(Reload.Start+.65)
        &&F.Player->GetWeaponActionsState().Instances.back().Ammo==0.&&F.Player->Facing==-1.f))return false;
    FS L,U;if(F.Capture(*this,F.Player,L,TEXT("Real inserted reload"))&&F.RoundTrip(*this,F.Player,L,U,TEXT("Real inserted reload")))
    {
        WA::FWeaponActionsKernel K;
        if(!TestTrue(TEXT("Restored complete WA state passes independent pure validation"),K.Restore(U.Player.GetValue().WeaponActions)))return false;
        WA::FContext C;C.CanStart=false;C.Grounded=true;const auto Events=K.StepTo(Reload.End,C);int Completed=0;
        for(const auto& E:Events)Completed+=E.Kind==WA::EEvent::ReloadCompleted;
        const auto Again=K.StepTo(Reload.End,C);
        TestTrue(TEXT("Original reload deadline refills same instance once and repeated boundary has no event"),Completed==1&&Again.empty()
            &&K.Instance(Reload.InstanceId)&&K.Instance(Reload.InstanceId)->Ammo==1.&&K.State().Action.Terminal==WA::EEvent::ReloadCompleted);
        TestTrue(TEXT("Old accepted world emission origin stays frozen independently of later owner display"),L.EmissionPoseSockets.size()==1
            &&FrozenProjectile.Source.Origin.X==L.EmissionPoseSockets[0].Pose.CombatOrigin.X
            &&FrozenProjectile.Source.Origin.Y==L.EmissionPoseSockets[0].Pose.CombatOrigin.Y
            &&FrozenProjectile.Source.Origin.Height==L.EmissionPoseSockets[0].Pose.CombatOrigin.Height);
    }
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FFighterOwnerKnight,
    "CodexDungeon.Content.FighterOwnerSnapshot.KnightActionsHitsAndClaimedDeath",
    EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FFighterOwnerKnight::RunTest(const FString& Parameters)
{
    FActorWorld F;if(!TestTrue(TEXT("Actual bound knight world starts"),F.Create()))return false;
    auto K=F.Knight();if(!TestNotNull(TEXT("Actual admitted knight has driver"),K)||!TestNotNull(TEXT("Knight driver"),K->GetStoneKnightDriver()))return false;
    if(!TestTrue(TEXT("Actual statue is dormant before proximity"),K->GetStoneKnightDriver()->State().Phase==KN::EPhase::Dormant))return false;
    FS S,R;if(F.Capture(*this,K,S,TEXT("Real dormant knight")))F.RoundTrip(*this,K,S,R,TEXT("Real dormant knight"));
    F.Player->MoveOnGround({1,0},.12f);
    if(!TestTrue(TEXT("Normal proximity tick starts actual wake"),F.AdvanceTo(F.Game->GetSimulationTime()+.01)
        &&K->GetStoneKnightDriver()->State().WakeStartedAt>=0))return false;
    const auto Wake=K->GetStoneKnightDriver()->State().WakeEnd;
    FS W,U;if(F.Capture(*this,K,W,TEXT("Actual knight wake")))F.RoundTrip(*this,K,W,U,TEXT("Actual knight wake"));
    if(!TestTrue(TEXT("Real wake and distance admit charge without hand-edited kernel"),F.AdvanceTo(Wake)
        &&F.Until([&]{const auto& A=K->GetStoneKnightDriver()->State().Action;return A.InProgress&&A.Kind==KN::EAttack::Charge;})))return false;
    const auto Charge=K->GetStoneKnightDriver()->State().Action;
    if(!TestTrue(TEXT("Actual charge reaches locked active movement"),F.AdvanceTo(Charge.ActiveAt+.05)
        &&K->GetStoneKnightDriver()->State().Action.Locked&&K->GetStoneKnightDriver()->State().Phase==KN::EPhase::Active))return false;
    FS C,V;if(F.Capture(*this,K,C,TEXT("Locked active charge")))F.RoundTrip(*this,K,C,V,TEXT("Locked active charge"));
    if(!TestTrue(TEXT("Actual charge contact creates one real player hit receipt"),F.AdvanceTo(Charge.ActiveAt+.4)
        &&K->GetStoneKnightDriver()->State().HitReceipts.size()==1&&F.Player->Health<100.f))return false;
    FS H,I;if(F.Capture(*this,K,H,TEXT("Charge receipt/recovery")))F.RoundTrip(*this,K,H,I,TEXT("Charge receipt/recovery"));
    if(!TestTrue(TEXT("Actual recovery permits close shield action"),F.Until([&]{const auto& A=K->GetStoneKnightDriver()->State().Action;
        return A.InProgress&&A.Kind==KN::EAttack::Shield;})))return false;
    const auto Shield=K->GetStoneKnightDriver()->State().Action;
    if(!TestTrue(TEXT("Real shield active contact records its separate accepted hit"),F.AdvanceTo(Shield.ActiveAt+.01)
        &&K->GetStoneKnightDriver()->State().HitReceipts.size()==2))return false;
    FS B,J;if(F.Capture(*this,K,B,TEXT("Actual shield receipt")))F.RoundTrip(*this,K,B,J,TEXT("Actual shield receipt"));
    K->ApplyCombatHit(1000.f,F.Player,0.f);
    if(!TestTrue(TEXT("Actual fatal hit commits kernel death, report and one claimed reward"),K->bDead&&K->bDeathReported
        &&K->Health==0.f&&K->GetStoneKnightDriver()->State().RewardClaimed&&F.Game->Pickups.Num()==3))return false;
    FS D,O;if(F.Capture(*this,K,D,TEXT("Claimed knight death")))F.RoundTrip(*this,K,D,O,TEXT("Claimed knight death"));
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FFighterOwnerBat,
    "CodexDungeon.Content.FighterOwnerSnapshot.BatBirthAnchorMovedAndTerminalPresentation",
    EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FFighterOwnerBat::RunTest(const FString& Parameters)
{
    FActorWorld F;if(!TestTrue(TEXT("Actual bat world reaches nonzero birth time"),F.Create()&&F.AdvanceTo(2.)))return false;
    auto B=F.Game->SpawnStoneBat({150,0});if(!TestNotNull(TEXT("Public actual admitted bat spawn"),B))return false;
    B->bAIEnabled=true;
    if(!TestTrue(TEXT("Actual bat progresses through wake/attack to moved low recovery"),F.Until([&]{return B->GetStoneBatDriver()
        &&B->GetStoneBatDriver()->State().Phase==BT::EPhase::LowRecovery;})))return false;
    const auto Real=B->GetStoneBatDriver()->Capture();
    if(!TestTrue(TEXT("Real immutable birth anchor differs from current native position"),Real.InitialTime==2.&&Real.InitialPosition.X==150.
        &&Real.InitialPosition.Z==90.&&Real.Position.X!=Real.InitialPosition.X&&Real.Position.Z==20.&&Real.PendingLow))return false;
    BT::FBatKernel Pure(Real.EntityId,Real.InitialTime,Real.InitialPosition);
    if(!TestTrue(TEXT("Actual moved bat state passes existing strict pure Restore at saved origin"),Pure.Restore(Real)))return false;
    FS S,R;if(F.Capture(*this,B,S,TEXT("Actual moved low bat"))&&F.RoundTrip(*this,B,S,R,TEXT("Actual moved low bat")))
    {
        auto Staging=F.World->SpawnActor<ADungeonFighter>();if(!TestNotNull(TEXT("Independent native driver owner"),Staging))return false;
        Staging->SetActorLocation({Real.Position.X,Real.Position.Y,0.});const auto Position=Staging->GetGroundPosition();
        FDungeonStoneBatDriver Driver(Staging,Real.EntityId,Real.InitialTime,Real.InitialPosition);
        TestTrue(TEXT("New explicit-origin driver strictly restores without moving owner to its birth point"),Driver.Restore(Real)
            &&Driver.State().InitialTime==2.&&Driver.State().InitialPosition.X==150.&&Driver.State().Position.X==Real.Position.X
            &&Staging->GetGroundPosition()==Position);
        Staging->Destroy();
    }
    if(!TestTrue(TEXT("Actual bat proceeds through its pending low deadline into rise"),F.AdvanceTo(Real.LowReadyAt+.1)
        &&B->GetStoneBatDriver()->State().Phase==BT::EPhase::Rising&&B->GetCombatHeight()>20.&&B->GetCombatHeight()<90.))return false;
    FS Rise,RR;if(F.Capture(*this,B,Rise,TEXT("Exact rising bat Z")))F.RoundTrip(*this,B,Rise,RR,TEXT("Exact rising bat Z"));
    B->ApplyCombatHit(1000.f,F.Player,0.f);
    if(!TestTrue(TEXT("Actual bat fatal hit claimed death without a fresh initializer"),B->bDead&&B->bDeathReported&&B->GetStoneBatDriver()->State().RewardClaimed))return false;
    if(!TestTrue(TEXT("Real timers expire old player protection before terminal fixture"),F.AdvanceTo(F.Game->GetSimulationTime()+1.)))return false;
    F.Player->StartJump();if(!TestTrue(TEXT("Actual player jumps and starts accepted aerial melee"),F.AdvanceTo(F.Game->GetSimulationTime()+.1)&&F.Player->JumpHeight>0.f))return false;
    F.Player->BeginAttack();if(!TestTrue(TEXT("Actual aerial primary is active before lethal hit"),F.Player->GetMeleeCombatState().Action.Active))return false;
    F.Player->ApplyCombatHit(1000.f,nullptr,0.f);
    if(!TestTrue(TEXT("Actual player death ends run and retains terminal combat event queue"),F.Player->bDead&&F.Game->bGameOver
        &&!F.Player->GetMeleeCombatState().PendingEvents.empty()&&!F.Player->GetWeaponActionsState().Budget.Grounded))return false;
    const double Stop=F.Game->GetSimulationTime(),BatTime=B->GetStoneBatDriver()->State().Time,CombatTime=F.Player->GetMeleeCombatState().Time;
    const double ExactZ=B->GetCombatHeight();F.Game->Tick(.5f);
    if(!TestTrue(TEXT("Real terminal display falls while master, combat and bat clocks/height freeze"),F.Game->GetSimulationTime()==Stop
        &&B->GetStoneBatDriver()->State().Time==BatTime&&F.Player->GetMeleeCombatState().Time==CombatTime
        &&B->JumpHeight==0.f&&B->GetCombatHeight()==ExactZ&&ExactZ>0.&&F.Player->JumpHeight==0.f))return false;
    FS T,U;if(F.Capture(*this,B,T,TEXT("Legitimate fallen bat terminal display")))F.RoundTrip(*this,B,T,U,TEXT("Legitimate fallen bat terminal display"));
    FS P,Q;if(F.Capture(*this,F.Player,P,TEXT("Legitimate airborne-budget player terminal queue")))F.RoundTrip(*this,F.Player,P,Q,TEXT("Legitimate airborne-budget player terminal queue"));
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FFighterOwnerAtomic,
    "CodexDungeon.Content.FighterOwnerSnapshot.InvalidCandidateIsAtomic",
    EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FFighterOwnerAtomic::RunTest(const FString& Parameters)
{
    FActorWorld F;if(!TestTrue(TEXT("Atomic fixture uses actual acquired loaded crossbow"),F.Create()&&F.Crossbow()))return false;
    F.Player->BeginAttack();const auto Shot=F.Player->GetWeaponActionsState().Action;
    if(!TestTrue(TEXT("Actual emission exists before owner mutation counterexamples"),Shot.Active&&F.AdvanceTo(Shot.ActiveAt)
        &&F.Game->GetWeaponWorldState().Projectiles.Num()==1))return false;
    FS S;if(!F.Capture(*this,F.Player,S,TEXT("Actual atomic baseline")))return false;
    if(!TestTrue(TEXT("Actual baseline contains the complete player kernels and one real frozen emission"),S.Player.IsSet()&&S.EmissionPoseSockets.size()==1))return false;
    FContextValue C(F.Game,F.Player);
    for(double TinyOffset:{.000001,.0000000001})
    {
        auto TinyTarget=F.World->SpawnActor<ADungeonFighter>();if(!TestNotNull(TEXT("Independent tiny-offset staging target"),TinyTarget))return false;
        TinyTarget->SetActorTickEnabled(false);
        // Genuine saved owner is unchanged. Two ordinary native moves create an
        // actual staging location different from S by less than UE's real
        // location-update predicate; no journal/kernel fixture is edited.
        TinyTarget->SetActorLocation(FVector(S.GroundPosition.X+1.,S.GroundPosition.Y,0.));
        TinyTarget->SetActorLocation(FVector(S.GroundPosition.X+TinyOffset,S.GroundPosition.Y,0.));
        const auto Initial=TinyTarget->GetGroundPosition();
        AddInfo(FString::Printf(TEXT("Actual native staging precision control offset=%.17g initialX=%.17g savedX=%.17g"),TinyOffset,Initial.X,S.GroundPosition.X));
        if(!TestTrue(TEXT("Actual staging initial body differs but UE native location predicate considers the saved location unchanged"),
            Initial!=S.GroundPosition&&FVector(Initial.X,Initial.Y,0.).Equals(FVector(S.GroundPosition.X,S.GroundPosition.Y,0.))))return false;
        FString TinyWhy;
        if(TestTrue(TEXT("Genuine owner restore accepts a different tiny native staging initial position"),TinyTarget->RestoreOwnerSnapshot(S,C.Context,TinyWhy)))
        {
            FS TinyRecaptured;const bool Read=TinyTarget->CaptureOwnerSnapshot(TinyRecaptured,TinyWhy,&C.Context);
            if(!Read)AddInfo(TEXT("Tiny staging recapture diagnosis: ")+TinyWhy);
            if(TestTrue(TEXT("Tiny initial-position restore still permits complete approved-context recapture"),Read))
                TestTrue(TEXT("Restore installs exact saved body/all owner values despite UE native tiny-update suppression"),
                    TinyTarget->GetGroundPosition()==S.GroundPosition&&Signature(TinyRecaptured,false)==Signature(S,false));
        }
        TinyTarget->Destroy();
    }
    auto Target=F.World->SpawnActor<ADungeonFighter>();if(!TestNotNull(TEXT("Independent atomic target"),Target))return false;
    FString Why;if(!TestTrue(TEXT("Genuine saved root restores independent target"),Target->RestoreOwnerSnapshot(S,C.Context,Why)))return false;
    FS Baseline;if(!TestTrue(TEXT("Explicit approved context reads complete target before invalid trials"),Target->CaptureOwnerSnapshot(Baseline,Why,&C.Context)))return false;
    const auto Exact=Signature(Baseline);const auto Muzzle=Target->GetWeaponMuzzleComponent()->GetComponentTransform();
    const auto EntityCursor=F.Game->GetWeaponWorldState().NextEntityId,WorldCursor=F.Game->GetWeaponWorldState().NextEventSequence;
    const auto AudioCursor=F.Game->GetActionAudioState().NextSequence,Revision=F.Game->GetEquipmentView().Revision;
    const auto Reject=[&](const TCHAR* Label,auto Mutate)
    {
        auto Bad=S;Mutate(Bad);Why.Reset();TestFalse(*(FString(Label)+TEXT(" is rejected")),Target->RestoreOwnerSnapshot(Bad,C.Context,Why));
        TestTrue(*(FString(Label)+TEXT(" has a diagnosis")),!Why.IsEmpty());FS After;
        TestTrue(*(FString(Label)+TEXT(" permits unchanged explicit owner observation")),Target->CaptureOwnerSnapshot(After,Why,&C.Context));
        TestTrue(*(FString(Label)+TEXT(" cannot partly install body/kernel/pose state")),Signature(After)==Exact
            &&Target->GetWeaponMuzzleComponent()->GetComponentTransform().Equals(Muzzle,0.));
        TestTrue(*(FString(Label)+TEXT(" cannot allocate world/resource/audio state")),F.Game->GetWeaponWorldState().NextEntityId==EntityCursor
            &&F.Game->GetWeaponWorldState().NextEventSequence==WorldCursor&&F.Game->GetActionAudioState().NextSequence==AudioCursor
            &&F.Game->GetEquipmentView().Revision==Revision);
    };
    Reject(TEXT("Unknown owner schema"),[](auto& X){X.Schema=3;});
    Reject(TEXT("Prior owner schema lacks actual native anchor"),[](auto& X){X.Schema=1;});
    Reject(TEXT("Nonfinite native height anchor"),[](auto& X){X.HeightAnchorRelative.SetScale3D({std::numeric_limits<double>::infinity(),1.,1.});});
    Reject(TEXT("Native height anchor has unsupported horizontal offset"),[](auto& X){auto P=X.HeightAnchorRelative.GetTranslation();P.X+=1.;X.HeightAnchorRelative.SetTranslation(P);});
    Reject(TEXT("Native height anchor has unsupported scale"),[](auto& X){X.HeightAnchorRelative.SetScale3D({2.,1.,1.});});
    Reject(TEXT("Native height anchor has unsupported rotation"),[](auto& X){X.HeightAnchorRelative.SetRotation(FQuat(FVector(0.,0.,1.),.5));});
    Reject(TEXT("Kind and kernel variant conflict"),[](auto& X){X.Kind=EDungeonFighterOwnerKind::StoneKnight;});
    Reject(TEXT("Missing stable entity identity"),[](auto& X){X.EntityId=0;});
    Reject(TEXT("Wrong complete Run identity"),[](auto& X){X.RunGuid.Invalidate();});
    Reject(TEXT("Nonfinite actual HP"),[](auto& X){X.Health=std::numeric_limits<float>::quiet_NaN();});
    Reject(TEXT("Invalid facing"),[](auto& X){X.Facing=0.f;});
    Reject(TEXT("Forged Focus mirror"),[](auto& X){X.FocusMirror-=1.f;});
    Reject(TEXT("Unknown WA kernel version"),[](auto& X){X.Player.GetValue().WeaponActions.Version=99;});
    Reject(TEXT("Wrong dodge initial anchor"),[](auto& X){X.Player.GetValue().Dodge.InitialPosition.X+=1.;});
    Reject(TEXT("Native body moved outside the real engine projection predicate"),[](auto& X){X.GroundPosition.X+=1.;});
    Reject(TEXT("Impossible simultaneous dodge without accepted record"),[](auto& X){X.Player.GetValue().Dodge.Phase=DK::EPhase::Dodging;});
    Reject(TEXT("Missing accepted emission reference"),[](auto& X){X.EmissionPoseSockets[0].EventId=MAX_uint64;});
    Reject(TEXT("Forged frozen physical emission origin"),[](auto& X){X.EmissionPoseSockets[0].Pose.CombatOrigin.X+=1.;});
    Reject(TEXT("Duplicate frozen emission identity"),[](auto& X){const auto Copy=X.EmissionPoseSockets[0];X.EmissionPoseSockets.push_back(Copy);});
    Reject(TEXT("Nonfinite custom muzzle definition"),[](auto& X){X.CustomMuzzle=true;X.CustomMuzzleRelative.SetScale3D({std::numeric_limits<double>::infinity(),1.,1.});});
    TestTrue(TEXT("Genuine value still accepted after every refusal"),Target->RestoreOwnerSnapshot(S,C.Context,Why));Target->Destroy();
    {
        // Actual source, accepted emission and world history stay intact. The
        // current native custom definition may differ from the frozen old shot.
        auto MuzzleComponent=F.Player->GetWeaponMuzzleComponent();
        MuzzleComponent->SetRelativeLocation(FVector(1.,0.,0.));
        MuzzleComponent->SetRelativeLocation(FVector(.000001,0.,0.));
        const auto NativeRelative=MuzzleComponent->GetRelativeTransform();
        if(!TestTrue(TEXT("Ordinary native component moves produced a real nonzero custom definition below UE update tolerance"),
            NativeRelative.GetTranslation()!=FVector::ZeroVector&&NativeRelative.GetTranslation().Equals(FVector::ZeroVector)))return false;
        FS TinyCustom;
        if(F.Capture(*this,F.Player,TinyCustom,TEXT("Actual tiny current custom muzzle definition")))
        {
            TestTrue(TEXT("Capture retains genuine tiny native custom definition independently of historical emission geometry"),
                TinyCustom.CustomMuzzle&&TinyCustom.CustomMuzzleRelative.Equals(NativeRelative,0.));
            FS TinyCustomRead;
            F.RoundTrip(*this,F.Player,TinyCustom,TinyCustomRead,TEXT("Actual tiny current custom muzzle definition"));
        }
    }
    {
        FActorWorld J;if(!TestTrue(TEXT("Actual tiny-jump native-anchor world starts bound"),J.Create()))return false;
        J.Player->GetWeaponMuzzleComponent()->SetRelativeLocation(FVector(24.,7.,0.));
        J.Player->StartJump();J.Game->Tick(.000001f);J.Game->Tick(.00000001f);
        const auto SourceAnchor=J.Player->GetWeaponMuzzleComponent()->GetAttachParent();
        if(!TestNotNull(TEXT("Real source muzzle has native height-anchor parent"),SourceAnchor))return false;
        const auto SourceRelative=SourceAnchor->GetRelativeTransform();
        const auto SourceWorld=SourceAnchor->GetComponentTransform();const auto SourceOrigin=J.Player->GetWeaponMuzzleOrigin();
        AddInfo(FString::Printf(TEXT("Actual tiny-jump source facts: JumpHeight=%.17g nativeRelativeZ=%.17g nativeWorldZ=%.17g nativeMuzzleHeight=%.17g simulation=%.17g"),
            double(J.Player->JumpHeight),SourceRelative.GetTranslation().Z,SourceWorld.GetTranslation().Z,SourceOrigin.Height,J.Game->GetSimulationTime()));
        if(!TestTrue(TEXT("Normal Jump and central float ticks retain actual prior native anchor while actor height advances inside native update predicate"),
            J.Player->JumpHeight>0.f&&SourceRelative.GetTranslation().Z>0.
            &&SourceRelative.GetTranslation().Z!=double(J.Player->JumpHeight)
            &&SourceRelative.GetTranslation().Equals(FVector(0.,0.,double(J.Player->JumpHeight)))
            &&SourceOrigin.Height==SourceWorld.GetTranslation().Z))return false;
        FS NativeSaved;
        if(J.Capture(*this,J.Player,NativeSaved,TEXT("Actual lagged native jump anchor and physical custom origin")))
        {
            TestTrue(TEXT("Capture contains the complete actual native anchor independently of actor JumpHeight"),
                NativeSaved.HeightAnchorRelative.Equals(SourceRelative,0.)
                &&NativeSaved.HeightAnchorRelative.GetTranslation().Z!=double(NativeSaved.JumpHeight));
            FContextValue JC(J.Game,J.Player);auto Staging=J.World->SpawnActor<ADungeonFighter>();
            if(!TestNotNull(TEXT("Independent native anchor staging owner"),Staging))return false;
            Staging->SetActorTickEnabled(false);FString AnchorWhy;
            if(TestTrue(TEXT("Actual owner with independently observed native height anchor restores"),Staging->RestoreOwnerSnapshot(NativeSaved,JC.Context,AnchorWhy)))
            {
                auto RestoredAnchor=Staging->GetWeaponMuzzleComponent()->GetAttachParent();
                if(TestNotNull(TEXT("Restored muzzle keeps native parent structure"),RestoredAnchor))
                {
                    const auto Origin=Staging->GetWeaponMuzzleOrigin();
                    TestTrue(TEXT("Restore retains actual saved native anchor relative/world numerical transform rather than normalizing it to actor JumpHeight"),
                        RestoredAnchor->GetRelativeTransform().Equals(SourceRelative,0.)&&RestoredAnchor->GetComponentTransform().Equals(SourceWorld,0.));
                    TestTrue(TEXT("Restore keeps the actual same-point public custom muzzle physical origin exact"),
                        Origin.X==SourceOrigin.X&&Origin.Y==SourceOrigin.Y&&Origin.Height==SourceOrigin.Height);
                }
                FS Read;const bool Captured=Staging->CaptureOwnerSnapshot(Read,AnchorWhy,&JC.Context);
                if(!Captured)AddInfo(TEXT("Native height-anchor staging capture diagnosis: ")+AnchorWhy);
                if(TestTrue(TEXT("Native height-anchor staging still recaptures complete owner"),Captured))
                    TestTrue(TEXT("Native anchor observation never changes accepted player kernel/body snapshot values"),Signature(Read,false)==Signature(NativeSaved,false));
            }
            Staging->Destroy();
        }
    }
    FActorWorld E;if(!TestTrue(TEXT("Independent actual knight mirror counterexample world"),E.Create()))return false;
    auto K=E.Knight();if(!TestNotNull(TEXT("Actual source knight"),K))return false;FS KS;
    if(E.Capture(*this,K,KS,TEXT("Actual knight HP mirror baseline")))
    {
        FContextValue KC(E.Game,K);auto T=E.World->SpawnActor<ADungeonFighter>();if(!TestNotNull(TEXT("Independent knight target"),T))return false;
        if(TestTrue(TEXT("Actual full knight value restores"),T->RestoreOwnerSnapshot(KS,KC.Context,Why)))
        {
            FS Old;T->CaptureOwnerSnapshot(Old,Why,&KC.Context);auto Bad=KS;Bad.Health-=1.f;
            TestFalse(TEXT("Actor HP inconsistent with exact kernel float projection is rejected"),T->RestoreOwnerSnapshot(Bad,KC.Context,Why));
            FS After;T->CaptureOwnerSnapshot(After,Why,&KC.Context);TestTrue(TEXT("HP-mirror rejection preserves complete knight"),Signature(Old)==Signature(After));
        }
        T->Destroy();
    }
    return true;
}
#endif
