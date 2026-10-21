#if WITH_DEV_AUTOMATION_TESTS
#include "Misc/AutomationTest.h"
#include "../DungeonRunInstaller.h"
#include "../DungeonFighter.h"
#include "../DungeonGameMode.h"
#include "../DungeonHUD.h"
#include "Components/BoxComponent.h"
#include "Components/SceneComponent.h"
#include "Engine/Engine.h"
#include "Engine/GameInstance.h"
#include "Engine/World.h"
#include "EngineUtils.h"
#include "GameFramework/PlayerController.h"
#include "GameFramework/PlayerInput.h"
#include "InputCoreTypes.h"
#include "Kismet/GameplayStatics.h"
#include "PhysicsEngine/BodyInstance.h"
#include <algorithm>
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
struct FInstallWorld
{
    FAutomationTestBase& Test;
    UWorld* World=nullptr;ADungeonGameMode* Game=nullptr;ADungeonFighter* Player=nullptr;APlayerController* Controller=nullptr;
    ADungeonHUD* HUD=nullptr;
    explicit FInstallWorld(FAutomationTestBase& T):Test(T){}
    ~FInstallWorld(){if(World){World->DestroyWorld(false);if(GEngine)GEngine->DestroyWorldContext(World);}}
    bool FailCreate(const TCHAR* Stage)
    {
        const auto* Selected=Game?UGameplayStatics::GetPlayerController(Game,0):nullptr;
        Test.AddInfo(FString::Printf(TEXT("RunInstall Create stage=%s world=%s initialized=%d netMode=%d game=%s player=%s controller=%s local=%d localPlayer=%d selectedPCsame=%d pawnSame=%d playerInput=%d HUD=%s controllerHUD=%s bound=%d sceneActive=%d enemies=%d knight=%d waiting=%d sim=%.17g"),
            Stage,*GetNameSafe(World),World?int32(World->AreActorsInitialized()):-1,World?int32(World->GetNetMode()):-1,
            *GetNameSafe(Game),*GetNameSafe(Player),*GetNameSafe(Controller),Controller?int32(Controller->IsLocalController()):-1,
            Controller?int32(Controller->GetLocalPlayer()!=nullptr):-1,int32(Controller&&Selected==Controller),
            int32(Controller&&Controller->GetPawn()==Player),int32(Controller&&Controller->PlayerInput),*GetNameSafe(HUD),
            *GetNameSafe(Controller?Controller->GetHUD():nullptr),Game?int32(Game->GetEquipmentView().Bound):-1,
            Game?int32(Game->GetSceneRoomView().Active):-1,Game?Game->Enemies.Num():-1,
            int32(Game&&Game->Enemies.Num()==1&&Game->Enemies[0]&&Game->Enemies[0]->GetStoneKnightDriver()),
            Game?int32(Game->bWaitingForStart):-1,Game?Game->GetSimulationTime():-1.));
        return false;
    }
    bool Create()
    {
        if(!GEngine)return FailCreate(TEXT("GEngine"));
        const auto Settings=UWorld::InitializationValues().AllowAudioPlayback(false).CreatePhysicsScene(true).RequiresHitProxies(false)
            .CreateNavigation(false).CreateAISystem(false).ShouldSimulatePhysics(false).SetTransactional(false);
        World=UWorld::CreateWorld(EWorldType::Game,false,NAME_None,nullptr,true,ERHIFeatureLevel::Num,&Settings);
        if(!World)return FailCreate(TEXT("CreateWorld"));GEngine->CreateNewWorldContext(EWorldType::Game).SetCurrentWorld(World);
        World->SetGameInstance(NewObject<UGameInstance>(GEngine));FURL URL;URL.AddOption(TEXT("game=/Script/CodexDungeon.DungeonGameMode"));
        if(!World->SetGameMode(URL))return FailCreate(TEXT("SetGameMode"));
        Game=World->GetAuthGameMode<ADungeonGameMode>();Player=World->SpawnActor<ADungeonFighter>();Controller=World->SpawnActor<APlayerController>();
        if(!Game||!Player||!Controller)return FailCreate(TEXT("SpawnGamePlayerController"));
        World->AddController(Controller);Controller->Possess(Player);
        if(!Controller->PlayerInput)Controller->PlayerInput=NewObject<UPlayerInput>(Controller);
        if(!Controller->IsLocalController())return FailCreate(TEXT("IsLocalController"));
        if(UGameplayStatics::GetPlayerController(Game,0)!=Controller)return FailCreate(TEXT("PlayerControllerSelection"));
        Game->PlayerFighter=Player;
        // One genuine new Run; no restore/reset shortcut or writable identity map.
        if(!Game->BeginSceneExplorationPreview())return FailCreate(TEXT("BeginSceneExplorationPreview"));
        if(Game->Enemies.Num()!=1)return FailCreate(TEXT("ActualSceneEnemyCount"));
        if(!Game->Enemies[0]->GetStoneKnightDriver())return FailCreate(TEXT("ActualSceneKnightDriver"));
        Game->Enemies[0]->bAIEnabled=false; // Same explicit initial combat-AI control as the existing actual Scene tests.
        Controller->ClientSetHUD_Implementation(ADungeonHUD::StaticClass());HUD=Cast<ADungeonHUD>(Controller->GetHUD());
        if(!HUD)return FailCreate(TEXT("ClientSetHUD/GetHUD"));
        if(!HUD->HasActorBegunPlay())HUD->DispatchBeginPlay();HUD->Tick(0.f);
        if(!Pulse(EKeys::Enter))return FailCreate(TEXT("NormalEnterInput"));
        if(Game->bWaitingForStart)return FailCreate(TEXT("NormalEnterStartTransition"));
        if(!BankAdmitted())return FailCreate(TEXT("ActualCompletedTickExplorationBank"));
        return true;
    }
    void Frame(float Dt)
    {
        Game->Tick(Dt);Controller->PlayerInput->Tick(Dt);TArray<UInputComponent*> Stack;
        Controller->PlayerInput->ProcessInputStack(Stack,Dt,false);if(HUD)HUD->Tick(Dt);
    }
    bool Key(FKey K,bool Down)
    {
        Controller->InputKey(FInputKeyParams(K,Down?IE_Pressed:IE_Released,Down?1.:0.));
        Controller->PlayerInput->Tick(.005f);TArray<UInputComponent*> Stack;
        Controller->PlayerInput->ProcessInputStack(Stack,.005f,false);return Controller->IsInputKeyDown(K)==Down;
    }
    bool Pulse(FKey K)
    {
        if(!Key(K,true)||!Controller->WasInputKeyJustPressed(K))return false;
        Frame(.005f);if(!Key(K,false))return false;Frame(.005f);return true;
    }
    bool AdvanceTo(double At)
    {
        if(At<Game->GetSimulationTime())return false;
        for(int32 N=0;N<64&&Game->GetSimulationTime()<At;++N)
        {
            const double Before=Game->GetSimulationTime(),Left=At-Before;
            float Dt=float(FMath::Min(.05,Left));if(double(Dt)>Left)Dt=std::nextafter(Dt,0.f);
            if(!(Dt>0.f))return false;Frame(Dt);if(Game->GetSimulationTime()<=Before)return false;
        }
        return Game->GetSimulationTime()==At&&!Game->bGameOver;
    }
    bool Move(double Target,bool X)
    {
        for(int32 N=0;N<1600;++N)
        {
            const auto P=Player->GetGroundPosition();const double Delta=Target-(X?P.X:P.Y);
            if(FMath::Abs(Delta)<.002){Frame(.005f);return true;}
            const FKey K=X?(Delta>0.?EKeys::D:EKeys::A):(Delta>0.?EKeys::W:EKeys::S);
            if(!Key(K,true))return false;Frame(float(FMath::Min(.02,FMath::Abs(Delta)/double(Player->GetMoveSpeed()))));
            if(!Key(K,false)||Game->bGameOver)return false;
        }
        Test.AddError(TEXT("Real Run Capture movement failed to reach its waypoint"));return false;
    }
    bool BankAdmitted()
    {
        // Independent source precondition. Missing/stub bank cannot be papered
        // over by a default empty fog state inside the aggregate.
        const auto B=Game->CaptureRunExplorationSnapshot();const auto& V=Game->GetEquipmentView();
        const auto* Current=B.Rooms.FindByPredicate([&](const auto& R){return R.RoomInstanceId==V.RoomInstanceId;});
        const bool Actual=Current&&Current->RoomNumber==Game->RoomNumber&&Current->State.RoomId==Game->RoomNumber
            &&!Current->State.Memory.empty()&&std::any_of(Current->State.Memory.begin(),Current->State.Memory.end(),[](double X){return X>0.;});
        return Test.TestTrue(TEXT("Real completed GameMode ticks admitted same-Run/room nonempty observed exploration without Canvas"),
            B.Schema==1&&B.RunGuid==V.RunGuid&&B.CurrentRoomInstanceId==V.RoomInstanceId&&Actual);
    }
    bool Capture(const TCHAR* Label,FDungeonRunSnapshot& Out)
    {
        FString Why;const bool Ok=Game->CaptureRunSnapshot(Out,Why);
        if(!Ok)Test.AddInfo(FString(Label)+TEXT(" aggregate diagnosis: ")+Why);
        return Test.TestTrue(Label,Ok);
    }
    bool KillKnight()
    {
        if(!Move(220.,true))return false;auto Knight=Game->Enemies[0].Get();
        for(int32 I=0;I<12&&!Knight->bDead;++I)if(!Pulse(EKeys::J)||!AdvanceTo(Game->GetSimulationTime()+.8))return false;
        return Knight->bDead&&Knight->bDeathReported&&Game->bRoomCleared&&Player->Coins==5;
    }
    bool ReachExit()
    {
        return Move(80.,false)&&Move(1180.,true)&&Move(0.,false)&&Pulse(EKeys::E)
            &&Game->GetSceneInteractionView().Pending&&Game->GetSceneInteractionView().NeedsConfirmation;
    }
};
}


namespace
{
namespace IV=DungeonEquipmentInventory;
// Complete typed-value signature, independent of Prepare/Install or a future codec.
// The only deliberately omitted physical request is Combat.PendingPrimary.
struct FRunSignature:FSignature
{
    void Guid(const FGuid& G){V(G.A,G.B,G.C,G.D);}
    void Std(const std::string& S){V(uint64(S.size()));Bytes.Append(reinterpret_cast<const uint8*>(S.data()),int32(S.size()));}
    template<class R>void Ids(const R& Ranges){V(uint64(Ranges.size()));for(const auto I:Ranges)V(I);}
    void Item(const IV::FItem& I)
    {V(I.InstanceId,I.Version);Std(I.ContentId);V(I.Grade,I.Package,I.Tier,I.Ammo,I.SkillCooldownDeadline,uint64(I.Affixes.size()));
        for(const auto& A:I.Affixes){Std(A.Id);V(A.Magnitude,A.OriginalQ.Numerator,A.OriginalQ.Denominator);}}
    void Plan(const IV::FPlan& P){V(P.Action,P.Slot,P.BaseRevision,P.SourceId,P.SourceVersion,P.InstanceId,P.InstanceVersion,P.ReplacedId);}
    void Result(const IV::FResult& R){V(R.Error,R.Replayed,R.Revision,R.AcquiredId,R.DroppedId,R.DroppedSourceId,R.ActiveSlot);}
    void Inventory(const IV::FState& S)
    {
        V(S.Schema,S.RunId,S.OwnerId,S.Revision,S.StarterId,S.Weapons[0],S.Weapons[1],S.Armor,S.ActiveSlot);
        V(uint64(S.Items.size()));for(const auto& I:S.Items)Item(I);
        V(uint64(S.Sources.size()));for(const auto& R:S.Sources){V(R.SourceId,R.Version,R.InstanceId,R.Available,R.CreatedRevision);Item(R.SpawnItem);}
        V(uint64(S.Operations.size()));for(const auto& O:S.Operations){V(O.OperationId,O.DropSourceId);Plan(O.Request);Result(O.Result);}
        Item(S.InitialStarter);V(S.NextRuntimeReceiptId,uint64(S.RuntimeUpdates.size()));
        for(const auto& R:S.RuntimeUpdates){V(R.ReceiptId,R.BaseRevision,R.InstanceId,R.BeforeVersion,R.AfterVersion,R.AtTime,R.BeforeAmmo,R.Ammo,R.BeforeCooldown,R.SkillCooldownDeadline);Result(R.Result);}
    }
    void Stats(const DungeonEquipmentStats::FResolved& S)
    {
        V(S.Error);for(double X:S.RawBonus.Values)V(X);for(double X:S.Final.Values)V(X);
        V(S.DamageMultiplier,S.StaggerMultiplier,S.ActionTimeScale,S.ReachMultiplier,S.CritChancePct,S.CritMultiplier,
            S.SkillCooldownMultiplier,S.FocusCostMultiplier,S.ReloadSeconds,S.PrimaryFocusCost,S.SkillFocusCost,
            S.Armor,S.Ward,S.Poise,S.PhysicalMitigation,S.MagicMitigation,S.MaxHP,S.CurrentHP,S.IdleMoveMultiplier,S.MoveSpeed,
            S.FocusRegen,S.FocusDelay,S.HealingMultiplier,S.PhysicalVulnerabilityMultiplier,S.MagicVulnerabilityMultiplier);
    }
    void Equipment(const FDungeonEquipmentRuntimeSnapshot& S)
    {
        const auto& E=S.View;V(S.Schema,E.Bound,E.Config);Guid(E.RunGuid);V(E.RunAlias,E.OwnerId,E.RoomInstanceId,E.Revision,E.ActiveSlot);
        for(const auto& L:E.Slots){V(L.InstanceId,L.Version);String(L.ContentId);V(L.Grade,L.Tier,L.Package,L.Ammo,L.CooldownDeadline,L.Affixes.Num());
            for(const auto& A:L.Affixes){String(A.Id);V(A.Magnitude,A.OriginalQ.Numerator,A.OriginalQ.Denominator);}}
        V(E.SelectedSourceId,E.NeedsSlotSelection,E.SelectionSlot);
        const auto& A=E.Action;V(A.Kind,A.Active,A.ActionId,A.OperationId,A.SourceId,A.InstanceId,A.Slot,A.Start,A.Deadline);
        V(E.LastFailure);String(E.FailureText);Stats(E.Stats);
        V(E.NextInstanceId,E.NextSourceId,E.NextOperationId,E.NextEquipmentActionId,E.NextRuntimeReceiptId,E.NextImportReceiptId,E.NextFocusReceiptId,E.CombatSeed,E.NextCritDraw);
        V(E.DeveloperCatalogIds.Num());for(const auto& I:E.DeveloperCatalogIds)String(I);
        V(S.HasInventory);Inventory(S.InventoryState);V(S.Sources.Num());
        for(const auto& R:S.Sources){V(R.SourceId,R.InstanceId,R.Version,R.RoomInstanceId);String(R.LogicalKey);Point(R.Position);V(R.Settled,R.Consumed);Item(R.Item);}
        Plan(S.PendingPlan);Point(S.PendingDropPosition);V(S.PendingHasDrop,S.CritReceipts.Num());
        for(const auto& R:S.CritReceipts)V(R.WeaponAction,R.ActionId,R.EventId,R.Draw,R.Bits,R.AtTime,R.ChancePct,R.Critical);
    }
    void Layout(const DungeonRoomLayout::FDescription& L)
    {String(L.Id.ToString());V(L.Version);Point(L.Entry);Point(L.Exit);Point(L.ExitHalfExtent);Point(L.Barrier.Min);Point(L.Barrier.Max);Point(L.Survey);}
    void SceneRoom(const FDungeonSceneRoomView& R)
    {V(R.Active);Guid(R.RunGuid);V(R.RoomInstanceId);Layout(R.Layout);V(R.Objects.Num());
        for(const auto& O:R.Objects){V(O.ObjectId,O.RoomInstanceId,O.Kind);Point(O.Position);V(O.Surveyed,O.SurveyCount);}}
    void Scene(const FDungeonSceneObjectsSnapshot& S)
    {V(S.Schema);SceneRoom(S.CurrentRoom);TArray<uint64> Keys;S.Rooms.GetKeys(Keys);Keys.Sort();V(Keys.Num());for(uint64 I:Keys){V(I);SceneRoom(S.Rooms[I]);}
        const auto& A=S.Interaction;V(A.Pending,A.NeedsConfirmation,A.Kind,A.RoomInstanceId,A.ObjectId,A.AtTime,A.LastFailure);}
    void World(const FDungeonWeaponWorldSnapshot& S)
    {
        V(S.Schema);const auto& W=S.State;Guid(W.RunGuid);V(W.RoomInstanceId,W.Time,W.NextEventSequence,W.NextEntityId,W.ActorBindings.Num());
        for(const auto& B:W.ActorBindings){V(B.EntityId,B.RoomInstanceId);String(B.ContentId);}
        V(W.Projectiles.Num());for(const auto& P:W.Projectiles){Key(P.Key);Event(P.Source);Point(P.Position);V(P.Traveled,P.Active,P.Stop,P.HasPoseSocket);Pose(P.PoseSocket);Origin(P.RangeAnchor);V(P.UsesActorRangeAnchor,P.LaunchForwardDistance,P.LaunchClearancePending,P.LaunchObstructed);}
        V(W.Windows.Num());for(const auto& P:W.Windows){Key(P.Key);Event(P.Source);V(P.Active);}
        V(W.HitReceipts.Num());for(const auto& H:W.HitReceipts){Key(H.Key);V(H.TargetId,H.AtTime,H.Damage,H.Stagger,H.Magic,H.HasPoseSocket);Pose(H.PoseSocket);Origin(H.RangeAnchor);V(H.LaunchObstructed);}
        V(W.Burns.Num());for(const auto& B:W.Burns){Key(B.Key);V(B.TargetId,B.Dps,B.AppliedAt,B.ExpiresAt,B.NextTickAt,B.Active);}
        V(W.Events.Num());for(const auto& E:W.Events){V(E.Sequence,E.Kind);Key(E.Key);V(E.TargetId,E.AtTime);Point(E.Position);V(E.Height,E.Damage,E.Stagger,E.ActualHPLoss,E.Magic,E.HasPoseSocket);Pose(E.PoseSocket);Origin(E.RangeAnchor);V(E.LaunchObstructed);}
    }
    void RewardActor(const FDungeonRunRewardActorFact& A)
    {V(A.EntityId,A.RoomInstanceId);String(A.ContentId);V(A.Enemy,A.Dead,A.DeathReported,A.RewardClaimed);}
    void Rewards(const FDungeonRunRewardSnapshot& S)
    {
        V(S.Schema,S.Bound);Guid(S.RunGuid);V(S.OwnerId,S.CurrentRoomInstanceId,S.NextSourceId,S.NextObjectId,S.NextOperationId,S.InitialCoins,S.Deaths.Num());
        for(const auto& F:S.Deaths){const auto& D=F.Death;V(D.EntityId,D.RoomInstanceId);String(D.ContentId);V(D.AtTime);Point(D.Position);V(D.FirstDeath,D.RoomCleared,F.SourceIds.Num());for(uint64 I:F.SourceIds)V(I);}
        V(S.Sources.Num());for(const auto& R:S.Sources)V(R.SourceId,R.ObjectId,R.EntityId,R.RoomInstanceId,R.Kind,R.AtTime);
        V(S.Objects.Num());for(const auto& O:S.Objects){V(O.ObjectId,O.SourceId,O.RoomInstanceId,O.Kind);Point(O.Position);V(O.ResolvedAmount,O.Consumed,O.Retired,O.CollectionOperationId,O.RetiredAt);}
        V(S.Collections.Num());for(const auto& C:S.Collections){const auto& R=C.Request;V(R.OperationId,R.ObjectId,R.SourceId,R.OwnerId,R.RoomInstanceId,R.AtTime,R.BeforeCoins,C.AfterCoins);}
        V(S.RetiredEntities.Num());for(const auto& R:S.RetiredEntities){RewardActor(R.Actor);V(R.RetiredAt);}
        V(S.RoomExits.Num());for(const auto& R:S.RoomExits){V(R.RoomInstanceId,R.NextRoomInstanceId,R.AtTime,R.EntityIds.Num());for(uint64 I:R.EntityIds)V(I);V(R.ObjectIds.Num());for(uint64 I:R.ObjectIds)V(I);}
    }
    void Exploration(const FDungeonRunExplorationSnapshot& S)
    {V(S.Schema);Guid(S.RunGuid);V(S.CurrentRoomInstanceId,S.Rooms.Num());for(const auto& R:S.Rooms){V(R.RoomInstanceId,R.RoomNumber,R.State.Schema,R.State.RoomId,R.State.Bounds.MinX,R.State.Bounds.MaxX,R.State.Bounds.MinY,R.State.Bounds.MaxY,uint64(R.State.Memory.size()));for(double X:R.State.Memory)V(X);}}
    void Audio(const FDungeonRunAudioContinuation& S)
    {V(S.Schema);Guid(S.RunGuid);V(S.RoomInstanceId,S.NextActionSequence,S.WorldHistoryThrough,S.WeaponCursors.Num());for(const auto& W:S.WeaponCursors){const auto& C=W.Cursor;V(W.OwnerId,C.Attached,C.DrawObserved,C.InsertObserved,C.LastEventId,uint64(C.RuntimeReceiptCount),C.LastObservedTime);Action(C.Reload);}V(S.StoneSeeds.Num());for(const auto& K:S.StoneSeeds)V(K.EntityId,K.NextEventId);}
    void Run(const FDungeonRunSnapshot& S)
    {
        V(S.Schema,S.Scope);Guid(S.RunGuid);V(S.OwnerId,S.RoomInstanceId,S.RoomNumber,S.SimulationTime,S.LastStoneWakeStartedAt,S.RoomCleared,S.GameOver,S.WaitingForStart,S.SceneCommitRequested,S.SceneEquipmentTargetLost);String(S.LastMessage);V(S.SceneEncounterEntityId,S.Geometry.Schema,S.Geometry.Kind);
        Equipment(S.Equipment);Scene(S.Scene);World(S.WeaponWorld);V(S.Fighters.Num());for(const auto& F:S.Fighters)Owner(F,false);
        V(S.EnemyOrder.Num());for(uint64 I:S.EnemyOrder)V(I);Rewards(S.Rewards);V(S.Pickups.Num());for(const auto& P:S.Pickups){Point(P.Position);String(P.Kind.ToString());V(P.Consumed);Guid(P.RunGuid);V(P.ObjectId,P.SourceId,P.RoomInstanceId);}Exploration(S.Exploration);Audio(S.Audio);
    }
};
TArray<uint8> RunSignature(const FDungeonRunSnapshot& S){FRunSignature B;B.Run(S);return B.Bytes;}
bool Seal(FInstallWorld& F,FDungeonRunSnapshot& S,FDungeonValidatedRun& V)
{
    if(!F.Capture(TEXT("Actual completed bound Run captures before installer is exercised"),S))return false;
    FString Why;const bool Ok=FDungeonRunAggregate::Validate(S,V,Why);if(!Ok)F.Test.AddInfo(TEXT("Seal diagnosis: ")+Why);
    return F.Test.TestTrue(TEXT("Actual complete Run independently validates into sealed owning values"),Ok&&V.IsValid());
}
bool Resume(FInstallWorld& F)
{
    FString Why;F.Frame(.005f); // real all-neutral observation while still technically paused
    if(!F.Pulse(EKeys::Enter))return false;
    return F.Test.TestTrue(TEXT("Only real neutral then fresh Enter opens the technical gate"),F.Game->GetRunInstallGate()==EDungeonRunInstallGate::Open);
}
bool InstallSaved(FInstallWorld& Target,const FDungeonRunSnapshot& Saved,const FDungeonValidatedRun& Sealed)
{
    FDungeonRunSnapshot Before;if(!Target.Capture(TEXT("Genuine target Run before staging"),Before))return false;
    const auto BeforeBytes=RunSignature(Before);TWeakObjectPtr<ADungeonFighter> OldPlayer=Target.Player;
    TArray<TWeakObjectPtr<ADungeonFighter>> OldEnemies;for(auto E:Target.Game->Enemies)OldEnemies.Add(E.Get());
    FDungeonPreparedRun Prepared;FString Why;
    const bool Ready=FDungeonRunInstaller::Prepare(*Target.Game,Sealed,Prepared,Why);
    if(!Ready)Target.Test.AddInfo(TEXT("Prepare diagnosis: ")+Why);
    if(!Target.Test.TestTrue(TEXT("Sealed complete Run prepares a hidden independent group without resetting the old Run"),Ready&&Prepared.IsReady()))return false;
    Target.Test.TestTrue(TEXT("Staging closes technical gate while original live identities stay installed"),
        Target.Game->GetRunInstallGate()==EDungeonRunInstallGate::Preparing&&Target.Game->PlayerFighter==OldPlayer.Get()
        &&Target.Game->GetEquipmentView().RunGuid==Before.RunGuid&&Prepared.GetSavedSnapshot()
        &&RunSignature(*Prepared.GetSavedSnapshot())==RunSignature(Saved));
    Target.Test.TestEqual(TEXT("Exactly current player/enemies and the authored one-barrier geometry are staged"),Prepared.GetStagedActors().Num(),Saved.Fighters.Num()+1);
    for(const auto& A:Prepared.GetStagedActors())Target.Test.TestTrue(TEXT("Every real staged actor is hidden, tick-off and collision-off"),
        A.IsValid()&&A->IsHidden()&&!A->IsActorTickEnabled()&&!A->GetActorEnableCollision());
    Target.Frame(.25f);FDungeonRunSnapshot During;
    if(Target.Capture(TEXT("Old complete Run remains capturable while preparation gate is closed"),During))
        Target.Test.TestTrue(TEXT("Preparation did not advance or change any authoritative field/ID/RNG/memory"),RunSignature(During)==BeforeBytes);
    const bool Installed=FDungeonRunInstaller::Install(*Target.Game,Prepared,Why);
    if(!Installed)Target.Test.AddInfo(TEXT("Install diagnosis: ")+Why);
    if(!Target.Test.TestTrue(TEXT("One grouped installation consumes the prepared resources"),Installed&&!Prepared.IsReady()))return false;
    Target.Player=Target.Game->PlayerFighter;
    Target.Test.TestTrue(TEXT("New player is possessed and old actors are destroyed only after successful group swap"),
        Target.Player&&Target.Player!=OldPlayer.Get()&&Target.Controller->GetPawn()==Target.Player
        &&(!OldPlayer.IsValid()||OldPlayer->IsActorBeingDestroyed()));
    for(const auto& A:OldEnemies)Target.Test.TestTrue(TEXT("Every superseded enemy is released after the successful swap"),!A.IsValid()||A->IsActorBeingDestroyed());
    FDungeonRunSnapshot After;
    if(!Target.Capture(TEXT("Installed paused complete Run captures through real current owner bindings"),After))return false;
    Target.Test.TestTrue(TEXT("All typed saved fields are exact, including native anchors, all owners/history, pickups, fog, RNG and future audio cursors"),RunSignature(After)==RunSignature(Saved));
    Target.Test.TestTrue(TEXT("Install keeps saved start/game-over flags separate from AwaitExplicitContinue"),
        Target.Game->GetRunInstallGate()==EDungeonRunInstallGate::AwaitExplicitContinue&&Target.Game->bWaitingForStart==Saved.WaitingForStart&&Target.Game->bGameOver==Saved.GameOver);
    int32 Barriers=0;const auto& B=Saved.Scene.CurrentRoom.Layout.Barrier;
    for(TActorIterator<AActor> It(Target.World);It;++It)if(auto* Box=Cast<UBoxComponent>(It->GetRootComponent()))
    {
        if(!It->GetActorEnableCollision()||Box->GetCollisionEnabled()==ECollisionEnabled::NoCollision)continue;++Barriers;
        Target.Test.TestTrue(TEXT("Installed Scene query geometry is registered at exact saved layout with all32 stored channels blocking"),
            Box->IsRegistered()&&It->GetActorLocation()==FVector(B.GetCenter().X,B.GetCenter().Y,40.)
            &&Box->GetUnscaledBoxExtent()==FVector(B.GetExtent().X,B.GetExtent().Y,80.)
            &&Box->GetCollisionEnabled()==ECollisionEnabled::QueryOnly&&Box->GetCollisionObjectType()==ECC_WorldStatic
            &&Box->GetCollisionResponseToChannels()==FCollisionResponseContainer(ECR_Block));
    }
    Target.Test.TestEqual(TEXT("Exactly one current authored query barrier exists after old geometry release"),Barriers,1);
    Target.Frame(.75f);FDungeonRunSnapshot Paused;
    if(Target.Capture(TEXT("Paused observation after wall-time-like Tick"),Paused))
        Target.Test.TestTrue(TEXT("Technical pause freezes all owner clocks and terminal presentation, not merely the root clock"),RunSignature(Paused)==RunSignature(Saved));
    return true;
}
}

// Catches: copying values but leaving an old player/clock/map, resetting an active
// reload, normalizing native sockets, replaying elapsed audio, or double refill.
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRunInstallReload,
    "CodexDungeon.Content.RunInstall.AcceptedReloadNativeAndPausedInstall",
    EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FRunInstallReload::RunTest(const FString&)
{
    FInstallWorld Source(*this),Target(*this);if(!TestTrue(TEXT("Two real bound Scene/PC/HUD runs are admitted"),Source.Create()&&Target.Create()))return false;
    DungeonEquipmentInventory::FItem X;X.ContentId="WPN-XBW-001";X.Ammo=0.;
    const auto R=Source.Game->RegisterEquipmentSource(TEXT("run.install.real.empty-xbw"),X,Source.Player->GetGroundPosition()+FVector2D(30.,0.),true);
    if(!TestTrue(TEXT("Normal E pickup and original deadline acquire empty crossbow"),R.Ok()&&Source.Pulse(EKeys::E)
        &&Source.Game->GetEquipmentView().Action.Active&&Source.AdvanceTo(Source.Player->GetEquipmentActionDeadline())
        &&Source.Player->WeaponId==TEXT("WPN-XBW-001")&&Source.Pulse(EKeys::T)))return false;
    const auto Reload=Source.Player->GetWeaponActionsState().Action;
    Source.Player->GetWeaponMuzzleComponent()->SetRelativeLocation(FVector(24.,7.,65.));
    const bool ReachedInsertBoundary=Source.AdvanceTo(Reload.Start+.65);
    AddInfo(FString::Printf(TEXT("Actual reload fixture start=%.17g end=%.17g target=%.17g sim=%.17g reached=%d active=%d type=%d HUDdraw=%d HUDinsert=%d HUDcomplete=%d journalRecords=%d nextSequence=%llu"),
        Reload.Start,Reload.End,Reload.Start+.65,Source.Game->GetSimulationTime(),int32(ReachedInsertBoundary),
        int32(Source.Player->GetWeaponActionsState().Action.Active),int32(Source.Player->GetWeaponActionsState().Action.Type),
        Source.HUD->GetActionAudioPlayRequests(TEXT("XBW_RELOAD_DRAW_01")),Source.HUD->GetActionAudioPlayRequests(TEXT("XBW_RELOAD_INSERT_01")),
        Source.HUD->GetActionAudioPlayRequests(TEXT("XBW_RELOAD_COMPLETE_01")),Source.Game->GetActionAudioState().Records.Num(),Source.Game->GetActionAudioState().NextSequence));
    if(!TestTrue(TEXT("Real active reload reaches post-insert/pre-complete boundary with actual HUD requests"),
        Reload.Active&&Reload.Type==WA::EAction::Reload&&ReachedInsertBoundary
        &&Source.HUD->GetActionAudioPlayRequests(TEXT("XBW_RELOAD_DRAW_01"))==1
        &&Source.HUD->GetActionAudioPlayRequests(TEXT("XBW_RELOAD_INSERT_01"))==1))return false;
    FDungeonRunSnapshot Saved;FDungeonValidatedRun Sealed;if(!Seal(Source,Saved,Sealed))return false;
    if(!InstallSaved(Target,Saved,Sealed))return false;
    TestTrue(TEXT("First paused consumer attachment does not replay elapsed draw/insert requests"),
        Target.HUD->GetActionAudioPlayReceipts().IsEmpty()&&Target.Game->GetActionAudioState().Records.IsEmpty());
    const auto Updates=Saved.Equipment.InventoryState.RuntimeUpdates.size();const auto Draw=Saved.Equipment.View.NextCritDraw;
    if(!Resume(Target)||!Target.AdvanceTo(Reload.End))return false;
    const auto& A=Target.Player->GetWeaponActionsState();const auto* I=Target.Game->GetEquipmentInventoryState();
    TestTrue(TEXT("Original absolute reload end performs one real matching refill without new action/crit draw"),
        A.Action.ActionId==Reload.ActionId&&!A.Action.Active&&I&&I->RuntimeUpdates.size()==Updates+1
        &&I->RuntimeUpdates.back().InstanceId==R.InstanceId&&I->RuntimeUpdates.back().BeforeAmmo==0.
        &&I->RuntimeUpdates.back().Ammo==1.&&Target.Game->GetEquipmentView().NextCritDraw==Draw
        &&Target.HUD->GetActionAudioPlayRequests(TEXT("XBW_RELOAD_COMPLETE_01"))==1
        &&Target.HUD->GetActionAudioPlayRequests(TEXT("XBW_RELOAD_DRAW_01"))==0
        &&Target.HUD->GetActionAudioPlayRequests(TEXT("XBW_RELOAD_INSERT_01"))==0);
    Target.Frame(.2f);TestEqual(TEXT("Later normal ticks do not replay the committed reload completion"),Target.HUD->GetActionAudioPlayRequests(TEXT("XBW_RELOAD_COMPLETE_01")),1);
    return true;
}

// Catches: filtering dead current actors, respawning old-room tombstones, losing
// pickup receipts/fog lineage, or spending the Continue Enter on a saved exit.
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRunInstallHistory,
    "CodexDungeon.Content.RunInstall.CrossRoomDeadAndRetiredHistory",
    EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FRunInstallHistory::RunTest(const FString&)
{
    FInstallWorld Source(*this),Target(*this);if(!TestTrue(TEXT("Real normal J kill/automatic currency and two bound runs"),Source.Create()&&Target.Create()&&Source.KillKnight()&&Source.ReachExit()))return false;
    FDungeonRunSnapshot Dead;FDungeonValidatedRun DeadSealed;if(!Seal(Source,Dead,DeadSealed))return false;
    if(!TestTrue(TEXT("Saved source has current dead knight, consumed coin receipt and a truly unconfirmed exit"),
        Dead.Fighters.Num()==2&&Dead.Fighters[1].Dead&&Dead.Rewards.Collections.Num()==1
        &&Dead.Pickups.Num()==3&&Dead.Pickups[0].Consumed&&Dead.Scene.Interaction.Pending&&Dead.Scene.Interaction.NeedsConfirmation))return false;
    if(!InstallSaved(Target,Dead,DeadSealed)||!Resume(Target))return false;
    TestTrue(TEXT("Fresh Continue was consumed and did not confirm the saved exit or restart this Run"),
        Target.Game->RoomNumber==1&&Target.Game->GetSceneInteractionView().Pending&&Target.Game->GetSceneInteractionView().NeedsConfirmation
        &&Target.Game->GetEquipmentView().RunGuid==Dead.RunGuid&&Target.Player->Coins==5);
    if(!TestTrue(TEXT("Original source normal Enter transfers to room2 without a fake clear or reset"),Source.Pulse(EKeys::Enter)&&Source.Game->RoomNumber==2&&Source.BankAdmitted()))return false;
    auto* Bat=Source.Game->SpawnStoneBat({800.,80.});
    if(!TestTrue(TEXT("Normal public room2 bat admission creates a real third current owner"),Bat&&Bat->GetStoneBatDriver()))return false;
    Source.Frame(.01f);FDungeonRunSnapshot Next;FDungeonValidatedRun NextSealed;if(!Seal(Source,Next,NextSealed))return false;
    if(!TestTrue(TEXT("Source room2 has player birth binding, retired dead source, consumed/retired coin and old fog"),
        Next.Fighters.Num()==3&&Next.EnemyOrder.Num()==2&&Next.Rewards.RetiredEntities.Num()==1
        &&Next.Rewards.RetiredEntities[0].Actor.EntityId==Dead.Fighters[1].EntityId
        &&Next.Rewards.Objects[0].Consumed&&Next.Rewards.Objects[0].Retired&&Next.Exploration.Rooms.Num()==2
        &&Next.WeaponWorld.State.ActorBindings[0].RoomInstanceId==1&&Next.RoomInstanceId==2))return false;
    if(!InstallSaved(Target,Next,NextSealed))return false;
    TestTrue(TEXT("Only saved current player/knight/bat are instantiated; old dead binding stays historical"),
        Target.Game->Enemies.Num()==2&&Target.Game->Enemies[0]->GetStoneKnightDriver()&&Target.Game->Enemies[1]->GetStoneBatDriver()
        &&Target.Game->CaptureRunRewardsSnapshot().Deaths.Num()==1&&Target.Player->Coins==5&&Target.Game->Pickups.IsEmpty());
    return true;
}

// Catches: held pre-load input leaking into actions, R restart, movement, exit
// confirmation, or caller-fabricated continuation before real neutral/fresh edge.
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRunInstallHeld,
    "CodexDungeon.Content.RunInstall.HeldInputsRequireNeutralAndFreshContinue",
    EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FRunInstallHeld::RunTest(const FString&)
{
    FInstallWorld Source(*this),Target(*this);if(!TestTrue(TEXT("Actual PC/Input/Scene runs and accepted source melee"),Source.Create()&&Target.Create()&&Source.Pulse(EKeys::J)))return false;
    const auto M=Source.Player->GetMeleeCombatState().Action;
    if(!TestTrue(TEXT("Saved melee is really active and locked before staging"),M.Active&&Source.AdvanceTo(M.LockTime)))return false;
    FDungeonRunSnapshot Saved;FDungeonValidatedRun Sealed;if(!Seal(Source,Saved,Sealed))return false;
    const FKey Held[]={EKeys::J,EKeys::T,EKeys::E,EKeys::Enter,EKeys::R,EKeys::K,EKeys::SpaceBar,EKeys::LeftShift,EKeys::D};
    for(FKey K:Held)if(!TestTrue(TEXT("Actual held physical key is present before Prepare"),Target.Key(K,true)))return false;
    if(!InstallSaved(Target,Saved,Sealed))return false;
    FString Why;TestFalse(TEXT("Public continuation cannot fabricate a fresh UI press while controls are held"),Target.Game->RequestExplicitContinue(Why));
    Target.Frame(1.f);FDungeonRunSnapshot Still;if(Target.Capture(TEXT("Held keys after install remain paused"),Still))
        TestTrue(TEXT("Held gameplay keys do not restart/move/cancel accepted melee or spend IDs/RNG"),RunSignature(Still)==RunSignature(Saved));
    if(!Target.Key(EKeys::Enter,false))return false;Target.Frame(.005f);
    if(!Target.Pulse(EKeys::Enter))return false;
    TestTrue(TEXT("A fresh Enter still cannot resume while other gameplay controls remain held"),Target.Game->GetRunInstallGate()==EDungeonRunInstallGate::AwaitExplicitContinue);
    for(FKey K:Held)if(!Target.Key(K,false))return false;Target.Frame(.005f);
    TestFalse(TEXT("Neutral alone is not a continuation edge"),Target.Game->RequestExplicitContinue(Why));
    if(!Resume(Target)||!Target.AdvanceTo(M.End))return false;
    TestTrue(TEXT("Accepted melee continues at its original action/end without repeated pre-load J"),
        !Target.Player->GetMeleeCombatState().Action.Active&&Target.Player->GetMeleeCombatState().Action.AttackId==M.AttackId
        &&Target.Game->GetEquipmentView().NextCritDraw==Saved.Equipment.View.NextCritDraw
        &&Target.Game->GetEquipmentView().RunGuid==Saved.RunGuid&&Target.Game->RoomNumber==Saved.RoomNumber);
    return true;
}

// Catches: destroying the old Run before staging succeeds, leaking staged
// actors/collision, overwriting a ready Out, or permitting reentrant root mutation.
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRunInstallAtomic,
    "CodexDungeon.Content.RunInstall.StagingFailureKeepsOriginalRun",
    EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FRunInstallAtomic::RunTest(const FString&)
{
    FInstallWorld Source(*this),Target(*this);if(!TestTrue(TEXT("Two real bound Runs and nonempty target accepted crit/fog state"),Source.Create()&&Target.Create()&&Target.Pulse(EKeys::J)))return false;
    FDungeonRunSnapshot Saved,Before;FDungeonValidatedRun Sealed;if(!Seal(Source,Saved,Sealed)||!Target.Capture(TEXT("Original target before any stage attempt"),Before))return false;
    const auto Bytes=RunSignature(Before);const auto PlayerBefore=Target.Player;
    FDungeonValidatedRun Unsealed;FDungeonPreparedRun Empty;FString Why;
    TestFalse(TEXT("Unsealed input cannot prepare or mutate a real Run"),FDungeonRunInstaller::Prepare(*Target.Game,Unsealed,Empty,Why));
    FDungeonPreparedRun Ready;
    if(!TestTrue(TEXT("A valid baseline genuinely stages before failure/RAII controls"),FDungeonRunInstaller::Prepare(*Target.Game,Sealed,Ready,Why)&&Ready.IsReady())){AddInfo(Why);return false;}
    const auto* ReadyValues=Ready.GetSavedSnapshot();const int32 ReadyCount=Ready.GetStagedActors().Num();
    TestFalse(TEXT("Rejected prepare preserves an already-ready Out"),FDungeonRunInstaller::Prepare(*Target.Game,Unsealed,Ready,Why));
    TestTrue(TEXT("Ready resources/sealed saved identity remain unchanged after rejection"),Ready.IsReady()&&Ready.GetSavedSnapshot()==ReadyValues&&Ready.GetStagedActors().Num()==ReadyCount);
    // Actual native counterexample: the private group is sealed, but its public
    // weak inspection view does not make the staged Actor immutable. A second
    // registered primitive must never become an unrepresented current collider.
    AActor* StageBarrier=nullptr;
    for(const auto& A:Ready.GetStagedActors())if(A.IsValid()&&Cast<UBoxComponent>(A->GetRootComponent()))StageBarrier=A.Get();
    if(!TestTrue(TEXT("The admitted ready group contains its real authored staged barrier"),StageBarrier!=nullptr))return false;
    auto* Extra=NewObject<UBoxComponent>(StageBarrier,NAME_None,RF_Transient);
    if(!TestTrue(TEXT("Actual additional native staging primitive is created"),Extra!=nullptr))return false;
    StageBarrier->AddInstanceComponent(Extra);Extra->SetupAttachment(StageBarrier->GetRootComponent());
    Extra->SetBoxExtent(FVector(8.,8.,8.),false);Extra->SetRelativeLocation(FVector(400.,0.,0.));
    Extra->SetCollisionEnabled(ECollisionEnabled::QueryOnly);Extra->SetCollisionObjectType(ECC_WorldStatic);
    Extra->SetCollisionResponseToAllChannels(ECR_Block);Extra->RegisterComponent();
    const auto* ExtraBody=Extra->GetBodyInstance(NAME_None,false);
    if(!TestTrue(TEXT("Real extra QueryOnly body is registered outside the authored barrier, while its staging Actor remains collision-off"),
        Extra->IsRegistered()&&ExtraBody&&ExtraBody->GetCollisionEnabled(false)==ECollisionEnabled::QueryOnly
        &&Extra->GetComponentLocation()==StageBarrier->GetActorLocation()+FVector(400.,0.,0.)&&!StageBarrier->GetActorEnableCollision()))return false;
    const bool InstalledExtra=FDungeonRunInstaller::Install(*Target.Game,Ready,Why);
    AddInfo(FString::Printf(TEXT("Extra primitive admission actual registered=%d storedPolicy=%d installed=%d ready=%d gate=%d diagnosis=%s"),
        int32(Extra->IsRegistered()),ExtraBody?int32(ExtraBody->GetCollisionEnabled(false)):-1,int32(InstalledExtra),int32(Ready.IsReady()),
        int32(Target.Game->GetRunInstallGate()),*Why));
    TestFalse(TEXT("Install rejects an actual extra registered primitive beyond the exact authored staging geometry set"),InstalledExtra);
    FDungeonRunSnapshot ExtraRejected;
    const bool OriginalCapturable=Target.Capture(TEXT("Original complete Run stays capturable after extra staging primitive rejection"),ExtraRejected);
    TestTrue(TEXT("Extra-primitive rejection keeps old Run, pawn binding, all IDs/RNG/fog/rewards and ready Out unchanged"),
        OriginalCapturable&&RunSignature(ExtraRejected)==Bytes&&Target.Game->PlayerFighter==PlayerBefore
        &&Target.Controller->GetPawn()==PlayerBefore&&Target.Game->GetRunInstallGate()==EDungeonRunInstallGate::Preparing
        &&Ready.IsReady()&&Ready.GetSavedSnapshot()==ReadyValues&&Ready.GetStagedActors().Num()==ReadyCount);
    // Stop on the unexpected successful swap: never erase its evidence or run
    // later controls through a stale old Player pointer after the wrong commit.
    if(InstalledExtra)return false;
    StageBarrier->RemoveInstanceComponent(Extra);Extra->DestroyComponent();
    TestTrue(TEXT("Removing only the test-added primitive preserves the original ready group and old live Run"),
        !Extra->IsRegistered()&&Ready.IsReady()&&Target.Game->PlayerFighter==PlayerBefore);
    Ready=FDungeonPreparedRun();
    FDungeonRunSnapshot Aborted;if(Target.Capture(TEXT("RAII preparation abort leaves original root capturable"),Aborted))
        TestTrue(TEXT("Aborted staging releases only its group and reopens the old Run without any authoritative changes"),
            RunSignature(Aborted)==Bytes&&Target.Game->GetRunInstallGate()==EDungeonRunInstallGate::Open&&Target.Game->PlayerFighter==PlayerBefore);
    int32 Spawned=0;TWeakObjectPtr<ADungeonFighter> First;TArray<TWeakObjectPtr<AActor>> ObservedStages;
    bool BlockedRegister=false,BlockedSpawn=false,InSpawnCallback=false;
    const auto Handle=Target.World->AddOnActorSpawnedHandler(FOnActorSpawned::FDelegate::CreateLambda([&](AActor* A)
    {
        auto* F=Cast<ADungeonFighter>(A);if(!F||InSpawnCallback)return;
        TGuardValue<bool> ReentryGuard(InSpawnCallback,true);++Spawned;ObservedStages.Add(F);
        DungeonEquipmentInventory::FItem I;I.ContentId="WPN-SPR-001";
        BlockedRegister=!Target.Game->RegisterEquipmentSource(TEXT("run.install.reentrant.forbidden"),I,{0.,0.},true).Ok();
        BlockedSpawn=Target.Game->SpawnStoneBat({600.,80.})==nullptr;
        Target.Game->RestartRun();Target.Game->TryInteract();PlayerBefore->StartJump();
        if(Spawned==1)First=F;
        // Real native receiver failure, no production fault hook or fake payload:
        // the second staged root has a parent, violating owner Restore admission.
        else if(Spawned==2&&First.IsValid())F->GetRootComponent()->AttachToComponent(First->GetRootComponent(),FAttachmentTransformRules::KeepWorldTransform);
    }));
    FDungeonPreparedRun Failed;const bool Prepared=FDungeonRunInstaller::Prepare(*Target.Game,Sealed,Failed,Why);
    Target.World->RemoveOnActorSpawnedHandler(Handle);
    TestFalse(TEXT("Actual second staged native owner admission failure rejects the whole transaction"),Prepared);
    TestTrue(TEXT("Failure was genuinely reached after real staging, with reentrant gameplay rejected"),Spawned>=2&&BlockedRegister&&BlockedSpawn&&!Failed.IsReady());
    FDungeonRunSnapshot After;if(Target.Capture(TEXT("Original complete target after real staging failure"),After))
        TestTrue(TEXT("Failure preserves full old Run/actors/geometry/IDs/RNG/fog/rewards exactly and reopens gate"),
            RunSignature(After)==Bytes&&Target.Game->PlayerFighter==PlayerBefore&&Target.Controller->GetPawn()==PlayerBefore
            &&Target.Game->GetRunInstallGate()==EDungeonRunInstallGate::Open);
    for(const auto& A:ObservedStages)TestTrue(TEXT("Every actor from the rejected preparation was destroyed without touching old actors"),!A.IsValid()||A->IsActorBeingDestroyed());
    return true;
}
#endif
