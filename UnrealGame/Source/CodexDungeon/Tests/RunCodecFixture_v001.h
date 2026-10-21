#pragma once
// Test-only fixture and independent fieldwise signature, adapted from the
// accepted RunInstall positive-control lifecycle. No production codec is used
// to construct expected values. Original tests remain unchanged.
#include "../DungeonRunAggregate.h"
#include "../DungeonFighter.h"
#include "../DungeonGameMode.h"
#include "../DungeonHUD.h"
#include "Components/SceneComponent.h"
#include "Engine/Engine.h"
#include "Engine/GameInstance.h"
#include "Engine/World.h"
#include "GameFramework/PlayerController.h"
#include "GameFramework/PlayerInput.h"
#include "InputCoreTypes.h"
#include "Kismet/GameplayStatics.h"
#include <algorithm>
#include <cmath>
#include <type_traits>
#include "Dom/JsonObject.h"
#include "Serialization/JsonReader.h"
#include "Serialization/JsonSerializer.h"
namespace
{
namespace FC=DungeonContentCombat;
namespace WA=DungeonWeaponActions;
namespace DK=DungeonDodge;
namespace KN=DungeonStoneKnight;
namespace BT=DungeonStoneBat;
namespace IV=DungeonEquipmentInventory;
using FS=FDungeonFighterOwnerSnapshot;

// Test-only fieldwise value signature. No C++ padding, object addresses,
// production encoder or RNG computes the expected value.
struct FSignature
{
    TArray<uint8> Bytes;
    template<class T>void One(T X){static_assert(std::is_arithmetic_v<T>||std::is_enum_v<T>);Bytes.Append(reinterpret_cast<const uint8*>(&X),sizeof(X));}
    template<class... T>void V(T... X){(One(X),...);}
    void String(const FString& X){FTCHARToUTF8 U(*X,X.Len());V(uint64(U.Length()));Bytes.Append(reinterpret_cast<const uint8*>(U.Get()),U.Length());}
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
            S.ComboReady,S.PendingPrimary,S.Grounded,S.AirPrimarySpent,S.Dead);CombatAction(S.Action);
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
struct FCodecWorld
{
    FAutomationTestBase& Test;
    UWorld* World=nullptr;ADungeonGameMode* Game=nullptr;ADungeonFighter* Player=nullptr;APlayerController* Controller=nullptr;
    ADungeonHUD* HUD=nullptr;
    explicit FCodecWorld(FAutomationTestBase& T):Test(T){}
    ~FCodecWorld(){if(World){World->DestroyWorld(false);if(GEngine)GEngine->DestroyWorldContext(World);}}
    bool FailCreate(const TCHAR* Stage)
    {
        const auto* Selected=Game?UGameplayStatics::GetPlayerController(Game,0):nullptr;
        Test.AddInfo(FString::Printf(TEXT("RunCodec Create stage=%s world=%s initialized=%d netMode=%d game=%s player=%s controller=%s local=%d localPlayer=%d selectedPCsame=%d pawnSame=%d playerInput=%d HUD=%s controllerHUD=%s bound=%d sceneActive=%d enemies=%d knight=%d waiting=%d sim=%.17g"),
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
// Independent test-only wire oracle. It does not call production Encode or
// Decode. The owning value signature above is a second, non-JSON oracle.
using JO=TSharedRef<FJsonObject>;
using JV=TSharedPtr<FJsonValue>;
struct FCodecOracle
{
    static JO Obj(){return MakeShared<FJsonObject>();}
    static JV Value(bool X){return MakeShared<FJsonValueBoolean>(X);}
    static JV Null(){return MakeShared<FJsonValueNull>();}
    template<class T>static JV Value(T X)
    {
        if constexpr(std::is_enum_v<T>)return Value(static_cast<std::underlying_type_t<T>>(X));
        else if constexpr(std::is_floating_point_v<T>)
        {
            static_assert(sizeof(T)==4||sizeof(T)==8);FString Bits;
            if constexpr(sizeof(T)==4){uint32 B;FMemory::Memcpy(&B,&X,4);Bits=FString::Printf(TEXT("%08x"),B);}
            else {uint64 B;FMemory::Memcpy(&B,&X,8);Bits=FString::Printf(TEXT("%016llx"),static_cast<unsigned long long>(B));}
            return MakeShared<FJsonValueString>(Bits);
        }
        else if constexpr(std::is_signed_v<T>)return MakeShared<FJsonValueString>(FString::Printf(TEXT("%lld"),static_cast<long long>(X)));
        else return MakeShared<FJsonValueString>(FString::Printf(TEXT("%llu"),static_cast<unsigned long long>(X)));
    }
    static JV Value(const FString& X){return MakeShared<FJsonValueString>(X);}
    static JV Value(const std::string& X){FUTF8ToTCHAR C(X.data(),int32(X.size()));return Value(FString(C.Length(),C.Get()));}
    static JV Value(FName X){return Value(X.ToString());}
    static JV Value(const JO& X){return MakeShared<FJsonValueObject>(X);}
    template<class... Ts>static void Scalars(JO O,const char* Names,Ts... X)
    {
        TArray<FString> Keys;FString(UTF8_TO_TCHAR(Names)).ParseIntoArray(Keys,TEXT(","),false);int32 I=0;
        const auto One=[&](auto V)
        {
            FString K=Keys[I++].TrimStartAndEnd();int32 Dot;
            if(K.FindLastChar(TEXT('.'),Dot))K=K.Mid(Dot+1);O->SetField(K,Value(V));
        };
        (One(X),...);
    }
    template<class Range,class Fn>static void Array(JO O,const TCHAR* Key,const Range& R,Fn F)
    {TArray<JV> A;for(const auto& X:R)A.Add(Value(F(X)));O->SetArrayField(Key,A);}
    template<class Range>static void Values(JO O,const TCHAR* Key,const Range& R)
    {Array(O,Key,R,[](const auto& X){return X;});}
    template<class T>static JO Point(const T& P){auto O=Obj();Scalars(O,"X,Y",P.X,P.Y);return O;}
    static JO Point3(const BT::FPoint& P){auto O=Obj();Scalars(O,"X,Y,Z",P.X,P.Y,P.Z);return O;}
    static JO Origin(const WA::FOrigin& P){auto O=Obj();Scalars(O,"X,Y,Height",P.X,P.Y,P.Height);return O;}
    static JO Guid(const FGuid& G){auto O=Obj();Scalars(O,"A,B,C,D",G.A,G.B,G.C,G.D);return O;}
    static JO Transform(const FTransform& T)
    {
        auto O=Obj();const auto P=T.GetTranslation(),S=T.GetScale3D();const auto Q=T.GetRotation();
        auto PO=Obj();Scalars(PO,"X,Y,Z",P.X,P.Y,P.Z);O->SetObjectField(TEXT("Translation"),PO);
        auto SO=Obj();Scalars(SO,"X,Y,Z",S.X,S.Y,S.Z);O->SetObjectField(TEXT("Scale"),SO);
        auto QO=Obj();Scalars(QO,"X,Y,Z,W",Q.X,Q.Y,Q.Z,Q.W);O->SetObjectField(TEXT("Rotation"),QO);return O;
    }
    static JO Key(const FDungeonWorldWeaponKey& K){auto O=Obj();Scalars(O,"OwnerId,ActionId,EventId,SubhitId,RoomInstanceId",K.OwnerId,K.ActionId,K.EventId,K.SubhitId,K.RoomInstanceId);return O;}
#define J(...) Scalars(O,#__VA_ARGS__,__VA_ARGS__)
#define N(K,V) O->SetObjectField(TEXT(K),V)
#define AR(K,R,F) Array(O,TEXT(K),R,F)
#define VA(K,R) Values(O,TEXT(K),R)
    static JO CombatAction(const FC::FActionState& S)
    {
        auto O=Obj();J(S.Active,S.Locked,S.StartedAirborne,S.WindowIssued,S.Phase,S.Weapon,S.WeaponInstanceId,S.AttackId,S.Stage,
            S.Facing,S.Start,S.LockTime,S.ActiveStart,S.ActiveEnd,S.End,S.Damage,S.Stagger,S.MinRange,S.Range,S.Depth,
            S.MoveMultiplier,S.ActionSpeedPct,S.Shape,S.Critical,S.CritMultiplier);return O;
    }
    static JO Combat(const FC::FCombatState& S)
    {
        auto O=Obj();J(S.Version,S.Weapon,S.WeaponInstanceId,S.NextAttackId,S.NextEventId,S.Time,S.ComboExpiry,S.NextComboStage,
            S.ComboReady,S.PendingPrimary,S.Grounded,S.AirPrimarySpent,S.Dead);N("Action",CombatAction(S.Action));
        AR("IssuedWindows",S.IssuedWindows,[](const auto& W){auto O=Obj();J(W.AttackId,W.EventId,W.SubhitId,W.Start,W.End);N("FrozenAction",CombatAction(W.FrozenAction));return O;});
        AR("HitReceipts",S.HitReceipts,[](const auto& H){auto O=Obj();J(H.AttackId,H.TargetId,H.SubhitId);return O;});
        AR("PendingEvents",S.PendingEvents,[](const auto& E){auto O=Obj();J(E.EventId,E.AttackId,E.Stage,E.SubhitId,E.Kind,E.AtTime,E.WindowEnd);N("Action",CombatAction(E.Action));return O;});return O;
    }
    static JO Action(const WA::FAction& S)
    {
        auto O=Obj();J(S.Type,S.Phase,S.Weapon,S.InstanceId,S.ActionId,S.Active,S.Locked,S.StartedAirborne,S.ForwardStepIssued,S.NextSubhit,
            S.Facing,S.Start,S.LockAt,S.ActiveAt,S.ActiveEnd,S.End,S.SpeedPct,S.DamagePct,S.StaggerPct,S.ReachPct,S.CritMultiplier,
            S.AmmoCost,S.FocusCost,S.CooldownDuration,S.ReloadSpeedPct,S.FocusCostPct,S.SkillCooldownPct,S.Critical,S.Terminal);return O;
    }
    static JO Instance(const WA::FInstance& S){auto O=Obj();J(S.Weapon,S.InstanceId,S.Ammo,S.ReservedAmmo,S.CooldownDeadline);return O;}
    static JO Event(const WA::FEvent& S)
    {
        auto O=Obj();J(S.EventId,S.ActionId,S.InstanceId,S.SubhitId,S.Kind,S.AtTime,S.WindowEnd,S.Damage,S.Stagger,S.MinRange,S.Range,S.Depth,
            S.ProjectileSpeed,S.SecondTargetRatio,S.BurnDps,S.BurnDuration,S.ForwardStep,S.AmmoConsumed,S.FocusConsumed,S.MaxTargets,S.Shape,S.OriginPolicy);
        N("Origin",Origin(S.Origin));N("Action",Action(S.Action));return O;
    }
    static JO Weapon(const WA::FState& S)
    {
        auto O=Obj();J(S.Version,S.Time,S.LastReloadCancelTime,S.EquippedId,S.NextActionId,S.NextEventId,S.AutoReloadPendingId);
        const auto& B=S.Budget;auto BO=Obj();Scalars(BO,"Focus,ReservedFocus,LastActualSpend,HasActualSpend,Grounded,AirPrimarySpent,Dead",B.Focus,B.ReservedFocus,B.LastActualSpend,B.HasActualSpend,B.Grounded,B.AirPrimarySpent,B.Dead);N("Budget",BO);
        N("Action",Action(S.Action));AR("Instances",S.Instances,[](const auto& I){return Instance(I);});
        AR("PendingEvents",S.PendingEvents,[](const auto& E){return Event(E);});AR("Issued",S.Issued,[](const auto& E){return Event(E);});
        J(S.InitialFocus,S.AccruedFocus,S.NextFocusMutationId);
        AR("FocusHistory",S.FocusHistory,[](const auto& R){auto O=Obj();J(R.MutationId,R.ReceiptId,R.Kind,R.AtTime,R.Requested,R.Applied,R.Before,R.After,R.ReservedBefore,R.RegeneratedBefore);return O;});
        AR("Registrations",S.Registrations,[](const auto& R){auto O=Obj();J(R.Kind,R.AtTime,R.ReceiptId,R.ActionCursor,R.EventCursor);N("Initial",Instance(R.Initial));return O;});
        J(S.NextImportReceiptId);AR("WeaponRuntimeHistory",S.WeaponRuntimeHistory,[](const auto& R){auto O=Obj();J(R.EventId,R.Kind,R.AtTime,R.BeforeAmmo,R.AfterAmmo,R.BeforeCooldown,R.AfterCooldown,R.SubhitId);N("Action",Action(R.Action));return O;});return O;
    }
    static JO PositionReceipt(const DK::FPositionReceipt& S){auto O=Obj();J(S.Id,S.AfterActionId,S.AtTime);N("Position",Point(S.Position));return O;}
    static JO Dodge(const DK::FState& S)
    {
        auto O=Obj();J(S.Version,S.OwnerId,S.NextActionId,S.NextEventId,S.DeathEventId,S.NextPositionReceiptId,S.InitialTime,S.Time,S.ReadyAt,S.DeadAt,S.Phase);
        N("InitialPosition",Point(S.InitialPosition));N("Position",Point(S.Position));
        AR("Records",S.Records,[](const auto& R){auto O=Obj();J(R.ActionId,R.StartEventId,R.BlockEventId,R.FinishEventId,R.Start,R.End,R.ReadyAt,R.Travelled,R.BlockedAt,R.FinishedAt,R.Block,R.Finish);
            N("Origin",Point(R.Origin));N("Direction",Point(R.Direction));N("OriginReceipt",PositionReceipt(R.OriginReceipt));return O;});N("LastPositionReceipt",PositionReceipt(S.LastPositionReceipt));return O;
    }
    static JO KnightAction(const KN::FAction& S)
    {
        auto O=Obj();J(S.AttackId,S.Kind,S.InProgress,S.Locked,S.ActiveIssued,S.Start,S.LockAt,S.ActiveAt,S.PlannedActiveEnd,S.ActiveEnd,S.RecoveryEnd,S.Damage,S.Stagger,S.Stop);
        N("Origin",Point(S.Origin));N("Target",Point(S.Target));N("Direction",Point(S.Direction));return O;
    }
    static JO Knight(const KN::FState& S)
    {
        auto O=Obj();J(S.Version,S.EntityId,S.NextAttackId,S.NextEventId,S.Time,S.HP,S.PoiseAccum,S.LastPoiseAt,S.ProtectionUntil,S.StunUntil,
            S.CombatStartedAt,S.WakeStartedAt,S.WakeEnd,S.ChargeReadyAt,S.ShieldReadyAt,S.WakeQueued,S.Awakened,S.RewardClaimed,S.Phase);
        N("Position",Point(S.Position));N("Action",KnightAction(S.Action));
        AR("ActiveReceipts",S.ActiveReceipts,[](const auto& R){auto O=Obj();J(R.End,R.EventId);N("FrozenAction",KnightAction(R.FrozenAction));return O;});
        AR("HitReceipts",S.HitReceipts,[](const auto& H){auto O=Obj();J(H.AttackId,H.TargetId);return O;});return O;
    }
    static JO BatAction(const BT::FAction& S)
    {
        auto O=Obj();J(S.AttackId,S.StartEventId,S.LockEventId,S.WindowEventId,S.FinishEventId,S.Kind,S.InProgress,S.Locked,S.Emitted,S.Interrupted,
            S.Missed,S.PathBlocked,S.EndpointFound,S.Start,S.LockAt,S.ActiveAt,S.ActiveEnd,S.NominalEnd,S.CooldownDeadline,S.InterruptedAt,
            S.CompletedAt,S.Damage,S.Stagger,S.RadiusX,S.RadiusY,S.HorizontalBudget,S.HorizontalSpeed);
        N("Origin",Point3(S.Origin));N("LockedTarget",Point3(S.LockedTarget));N("Endpoint",Point3(S.Endpoint));return O;
    }
    static JO Bat(const BT::FState& S)
    {
        auto O=Obj();J(S.Version,S.EntityId,S.NextAttackId,S.NextEventId,S.LastDamageReceiptId,S.InitialTime,S.Time,S.HP,S.PoiseAccum,S.PoiseDecayOrigin,
            S.LastPoiseAt,S.ProtectionUntil,S.StunUntil,S.CombatStartedAt,S.WakeStartedAt,S.WakeEnd,S.PeckReadyAt,S.WingReadyAt,S.LowStartedAt,
            S.LowReadyAt,S.RiseStartedAt,S.HighIdleEligibleSince,S.WakeQueued,S.Awakened,S.PendingLow,S.RewardClaimed,S.LowLegal,S.Phase,S.ResumePhase);
        N("InitialPosition",Point3(S.InitialPosition));N("Position",Point3(S.Position));N("RiseOrigin",Point3(S.RiseOrigin));N("Action",BatAction(S.Action));
        AR("Actions",S.Actions,[](const auto& A){return BatAction(A);});
        AR("ReceivedHits",S.ReceivedHits,[](const auto& H){auto O=Obj();J(H.ReceiptId,H.AtTime,H.HPLoss,H.Stagger);return O;});
        AR("HitReceipts",S.HitReceipts,[](const auto& H){auto O=Obj();J(H.AttackId,H.TargetId,H.AtTime);return O;});
        AR("Issued",S.Issued,[](const auto& E){auto O=Obj();J(E.EventId,E.EntityId,E.TargetId,E.Kind,E.AtTime,E.EndTime,E.Amount);N("From",Point3(E.From));N("To",Point3(E.To));N("Action",BatAction(E.Action));return O;});return O;
    }
    static JO Pose(const DungeonWeaponPoseSocket::FResolved& S)
    {
        auto O=Obj();J(S.Supported,S.CustomOverride,S.GroundPoseFallback,S.Clip,S.Frame,S.WeaponStateIndex,S.SampleTime,S.InstanceId,S.ActionId,S.Facing,
            S.RootX,S.RootY,S.BodySize,S.GripX,S.GripY,S.SupportX,S.SupportY,S.ComponentSupportX,S.ComponentSupportY,S.ComponentEmitX,
            S.ComponentEmitY,S.ComponentGripX,S.ComponentGripY,S.EmitX,S.EmitY,S.Angle,S.Scale);
        N("ActorOrigin",Origin(S.ActorOrigin));N("CombatOrigin",Origin(S.CombatOrigin));N("PresentationOrigin",Origin(S.PresentationOrigin));return O;
    }
    static JO Owner(const FS& S)
    {
        auto O=Obj();J(S.Schema,S.RoomInstanceId,S.EntityId,S.Kind,S.Health,S.MaxHealth,S.JumpHeight,S.JumpVelocity,S.Facing,S.Enemy,S.AIEnabled,S.Dead,S.DeathReported,S.Coins,
            S.EnemyContentId,S.WeaponId,S.ArmorId,S.FocusMirror,S.InvulnerableTime,S.HurtTime,S.AttackCooldown,S.PoiseAccumulation,S.PoiseDecayDelay,S.PoiseProtection,
            S.AirPrimarySpent,S.LastSkillEventId,S.AttackElapsed,S.ArmorChangeRemaining,S.FocusConsumeAge,S.AttackResolved,S.HasAxe,S.PendingArmorId,S.AttackTime,S.HitFlash,
            S.AnimationTime,S.LandingVisualAge,S.ComboStage,S.Moving,S.AnimationName,S.AttackPhase,S.CustomMuzzle,S.BatObservedHeight);
        N("RunGuid",Guid(S.RunGuid));N("GroundPosition",Point(S.GroundPosition));N("HurtProtectionSource",Key(S.HurtProtectionSource));
        AR("EmissionPoseSockets",S.EmissionPoseSockets,[](const auto& P){auto O=Obj();J(P.EventId,P.ActionId,P.SubhitId);N("Pose",Pose(P.Pose));return O;});
        AR("SkillWindows",S.SkillWindows,[](const auto& E){return Event(E);});
        AR("SkillHitReceipts",S.SkillHitReceipts,[](const auto& H){auto O=Obj();J(H.ActionId,H.SubhitId,H.TargetId);return O;});
        N("HeightAnchorRelative",Transform(S.HeightAnchorRelative));N("CustomMuzzleRelative",Transform(S.CustomMuzzleRelative));
        if(S.Player.IsSet()){const auto& P=S.Player.GetValue();auto PO=Obj();PO->SetObjectField(TEXT("Combat"),Combat(P.Combat));PO->SetObjectField(TEXT("WeaponActions"),Weapon(P.WeaponActions));PO->SetObjectField(TEXT("Dodge"),Dodge(P.Dodge));O->SetObjectField(TEXT("Player"),PO);}else O->SetField(TEXT("Player"),MakeShared<FJsonValueNull>());
        O->SetField(TEXT("Knight"),S.Knight.IsSet()?Value(Knight(S.Knight.GetValue())):Null());
        O->SetField(TEXT("Bat"),S.Bat.IsSet()?Value(Bat(S.Bat.GetValue())):Null());return O;
    }
    static JO Quantile(const DungeonEquipmentStats::FQuantile& S){auto O=Obj();J(S.Numerator,S.Denominator);return O;}
    static JO Item(const IV::FItem& S)
    {
        auto O=Obj();J(S.InstanceId,S.Version,S.ContentId,S.Grade,S.Package,S.Tier,S.Ammo,S.SkillCooldownDeadline);
        AR("Affixes",S.Affixes,[](const auto& A){auto O=Obj();J(A.Id,A.Magnitude);N("OriginalQ",Quantile(A.OriginalQ));return O;});return O;
    }
    static JO Plan(const IV::FPlan& S){auto O=Obj();J(S.Action,S.Slot,S.BaseRevision,S.SourceId,S.SourceVersion,S.InstanceId,S.InstanceVersion,S.ReplacedId);return O;}
    static JO Result(const IV::FResult& S){auto O=Obj();J(S.Error,S.Replayed,S.Revision,S.AcquiredId,S.DroppedId,S.DroppedSourceId,S.ActiveSlot);return O;}
    static JO Inventory(const IV::FState& S)
    {
        auto O=Obj();J(S.Schema,S.RunId,S.OwnerId,S.Revision,S.StarterId,S.Armor,S.ActiveSlot,S.NextRuntimeReceiptId);VA("Weapons",S.Weapons);N("InitialStarter",Item(S.InitialStarter));
        AR("Items",S.Items,[](const auto& I){return Item(I);});
        AR("Sources",S.Sources,[](const auto& R){auto O=Obj();J(R.SourceId,R.Version,R.InstanceId,R.Available,R.CreatedRevision);N("SpawnItem",Item(R.SpawnItem));return O;});
        AR("Operations",S.Operations,[](const auto& R){auto O=Obj();J(R.OperationId,R.DropSourceId);N("Request",Plan(R.Request));N("Result",Result(R.Result));return O;});
        AR("RuntimeUpdates",S.RuntimeUpdates,[](const auto& R){auto O=Obj();J(R.ReceiptId,R.BaseRevision,R.InstanceId,R.BeforeVersion,R.AfterVersion,R.AtTime,R.BeforeAmmo,R.Ammo,R.BeforeCooldown,R.SkillCooldownDeadline);N("Result",Result(R.Result));return O;});return O;
    }
    static JO Stats(const DungeonEquipmentStats::FResolved& S)
    {
        auto O=Obj();J(S.Error,S.DamageMultiplier,S.StaggerMultiplier,S.ActionTimeScale,S.ReachMultiplier,S.CritChancePct,S.CritMultiplier,
            S.SkillCooldownMultiplier,S.FocusCostMultiplier,S.ReloadSeconds,S.PrimaryFocusCost,S.SkillFocusCost,S.Armor,S.Ward,S.Poise,S.PhysicalMitigation,
            S.MagicMitigation,S.MaxHP,S.CurrentHP,S.IdleMoveMultiplier,S.MoveSpeed,S.FocusRegen,S.FocusDelay,S.HealingMultiplier,S.PhysicalVulnerabilityMultiplier,S.MagicVulnerabilityMultiplier);
        auto Raw=Obj();Values(Raw,TEXT("Values"),S.RawBonus.Values);N("RawBonus",Raw);
        auto Final=Obj();Values(Final,TEXT("Values"),S.Final.Values);N("Final",Final);return O;
    }
    static JO Equipment(const FDungeonEquipmentRuntimeSnapshot& S)
    {
        auto O=Obj();J(S.Schema,S.HasInventory,S.PendingHasDrop);N("InventoryState",Inventory(S.InventoryState));N("PendingPlan",Plan(S.PendingPlan));N("PendingDropPosition",Point(S.PendingDropPosition));
        auto VO=Obj();const auto& E=S.View;Scalars(VO,"Bound,Config,RunAlias,OwnerId,RoomInstanceId,Revision,ActiveSlot,SelectedSourceId,NeedsSlotSelection,SelectionSlot,LastFailure,FailureText,NextInstanceId,NextSourceId,NextOperationId,NextEquipmentActionId,NextRuntimeReceiptId,NextImportReceiptId,NextFocusReceiptId,CombatSeed,NextCritDraw",E.Bound,E.Config,E.RunAlias,E.OwnerId,E.RoomInstanceId,E.Revision,E.ActiveSlot,E.SelectedSourceId,E.NeedsSlotSelection,E.SelectionSlot,E.LastFailure,E.FailureText,E.NextInstanceId,E.NextSourceId,E.NextOperationId,E.NextEquipmentActionId,E.NextRuntimeReceiptId,E.NextImportReceiptId,E.NextFocusReceiptId,E.CombatSeed,E.NextCritDraw);
        VO->SetObjectField(TEXT("RunGuid"),Guid(E.RunGuid));VO->SetObjectField(TEXT("Stats"),Stats(E.Stats));Values(VO,TEXT("DeveloperCatalogIds"),E.DeveloperCatalogIds);
        Array(VO,TEXT("Slots"),E.Slots,[](const auto& L){auto O=Obj();J(L.InstanceId,L.Version,L.ContentId,L.Grade,L.Tier,L.Package,L.Ammo,L.CooldownDeadline);AR("Affixes",L.Affixes,[](const auto& A){auto O=Obj();J(A.Id,A.Magnitude);N("OriginalQ",Quantile(A.OriginalQ));return O;});return O;});
        {const auto& A=E.Action;auto AO=Obj();Scalars(AO,"Kind,Active,ActionId,OperationId,SourceId,InstanceId,Slot,Start,Deadline",A.Kind,A.Active,A.ActionId,A.OperationId,A.SourceId,A.InstanceId,A.Slot,A.Start,A.Deadline);VO->SetObjectField(TEXT("Action"),AO);}N("View",VO);
        AR("Sources",S.Sources,[](const auto& R){auto O=Obj();J(R.SourceId,R.InstanceId,R.Version,R.RoomInstanceId,R.LogicalKey,R.Settled,R.Consumed);N("Position",Point(R.Position));N("Item",Item(R.Item));return O;});
        AR("CritReceipts",S.CritReceipts,[](const auto& R){auto O=Obj();J(R.WeaponAction,R.ActionId,R.EventId,R.Draw,R.Bits,R.AtTime,R.ChancePct,R.Critical);return O;});return O;
    }
    static JO Layout(const DungeonRoomLayout::FDescription& S)
    {
        auto O=Obj();J(S.Id,S.Version);N("Entry",Point(S.Entry));N("Exit",Point(S.Exit));N("ExitHalfExtent",Point(S.ExitHalfExtent));N("Survey",Point(S.Survey));
        auto B=Obj();B->SetObjectField(TEXT("Min"),Point(S.Barrier.Min));B->SetObjectField(TEXT("Max"),Point(S.Barrier.Max));Scalars(B,"bIsValid",S.Barrier.bIsValid);N("Barrier",B);return O;
    }
    static JO SceneRoom(const FDungeonSceneRoomView& S)
    {
        auto O=Obj();J(S.Active,S.RoomInstanceId);N("RunGuid",Guid(S.RunGuid));N("Layout",Layout(S.Layout));
        AR("Objects",S.Objects,[](const auto& R){auto O=Obj();J(R.ObjectId,R.RoomInstanceId,R.Kind,R.Surveyed,R.SurveyCount);N("Position",Point(R.Position));return O;});return O;
    }
    static JO Scene(const FDungeonSceneObjectsSnapshot& S)
    {
        auto O=Obj();J(S.Schema);N("CurrentRoom",SceneRoom(S.CurrentRoom));TArray<uint64> Keys;S.Rooms.GetKeys(Keys);Keys.Sort();
        AR("Rooms",Keys,[&](uint64 K){auto O=Obj();O->SetField(TEXT("Key"),Value(K));N("Value",SceneRoom(S.Rooms[K]));return O;});
        const auto& A=S.Interaction;auto AO=Obj();Scalars(AO,"Pending,NeedsConfirmation,Kind,RoomInstanceId,ObjectId,AtTime,LastFailure",A.Pending,A.NeedsConfirmation,A.Kind,A.RoomInstanceId,A.ObjectId,A.AtTime,A.LastFailure);N("Interaction",AO);return O;
    }
    static JO World(const FDungeonWeaponWorldSnapshot& S)
    {
        auto O=Obj();J(S.Schema);const auto& W=S.State;auto WO=Obj();Scalars(WO,"RoomInstanceId,Time,NextEventSequence,NextEntityId",W.RoomInstanceId,W.Time,W.NextEventSequence,W.NextEntityId);WO->SetObjectField(TEXT("RunGuid"),Guid(W.RunGuid));
        Array(WO,TEXT("ActorBindings"),W.ActorBindings,[](const auto& B){auto O=Obj();J(B.EntityId,B.RoomInstanceId,B.ContentId);return O;});
        Array(WO,TEXT("Projectiles"),W.Projectiles,[](const auto& P){auto O=Obj();J(P.Traveled,P.Active,P.Stop,P.HasPoseSocket,P.UsesActorRangeAnchor,P.LaunchForwardDistance,P.LaunchClearancePending,P.LaunchObstructed);N("Key",Key(P.Key));N("Source",Event(P.Source));N("Position",Point(P.Position));N("PoseSocket",Pose(P.PoseSocket));N("RangeAnchor",Origin(P.RangeAnchor));return O;});
        Array(WO,TEXT("Windows"),W.Windows,[](const auto& P){auto O=Obj();J(P.Active);N("Key",Key(P.Key));N("Source",Event(P.Source));return O;});
        Array(WO,TEXT("HitReceipts"),W.HitReceipts,[](const auto& H){auto O=Obj();J(H.TargetId,H.AtTime,H.Damage,H.Stagger,H.Magic,H.HasPoseSocket,H.LaunchObstructed);N("Key",Key(H.Key));N("PoseSocket",Pose(H.PoseSocket));N("RangeAnchor",Origin(H.RangeAnchor));return O;});
        Array(WO,TEXT("Burns"),W.Burns,[](const auto& B){auto O=Obj();J(B.TargetId,B.Dps,B.AppliedAt,B.ExpiresAt,B.NextTickAt,B.Active);N("Key",Key(B.Key));return O;});
        Array(WO,TEXT("Events"),W.Events,[](const auto& E){auto O=Obj();J(E.Sequence,E.Kind,E.TargetId,E.AtTime,E.Height,E.Damage,E.Stagger,E.ActualHPLoss,E.Magic,E.HasPoseSocket,E.LaunchObstructed);N("Key",Key(E.Key));N("Position",Point(E.Position));N("PoseSocket",Pose(E.PoseSocket));N("RangeAnchor",Origin(E.RangeAnchor));return O;});N("State",WO);return O;
    }
    static JO RewardActor(const FDungeonRunRewardActorFact& S){auto O=Obj();J(S.EntityId,S.RoomInstanceId,S.ContentId,S.Enemy,S.Dead,S.DeathReported,S.RewardClaimed);return O;}
    static JO Rewards(const FDungeonRunRewardSnapshot& S)
    {
        auto O=Obj();J(S.Schema,S.Bound,S.OwnerId,S.CurrentRoomInstanceId,S.NextSourceId,S.NextObjectId,S.NextOperationId,S.InitialCoins);N("RunGuid",Guid(S.RunGuid));
        AR("Deaths",S.Deaths,[](const auto& F){auto O=Obj();const auto& D=F.Death;auto DO=Obj();Scalars(DO,"EntityId,RoomInstanceId,ContentId,AtTime,FirstDeath,RoomCleared",D.EntityId,D.RoomInstanceId,D.ContentId,D.AtTime,D.FirstDeath,D.RoomCleared);DO->SetObjectField(TEXT("Position"),Point(D.Position));N("Death",DO);VA("SourceIds",F.SourceIds);return O;});
        AR("Sources",S.Sources,[](const auto& R){auto O=Obj();J(R.SourceId,R.ObjectId,R.EntityId,R.RoomInstanceId,R.Kind,R.AtTime);return O;});
        AR("Objects",S.Objects,[](const auto& R){auto O=Obj();J(R.ObjectId,R.SourceId,R.RoomInstanceId,R.Kind,R.ResolvedAmount,R.Consumed,R.Retired,R.CollectionOperationId,R.RetiredAt);N("Position",Point(R.Position));return O;});
        AR("Collections",S.Collections,[](const auto& C){auto O=Obj();J(C.AfterCoins);const auto& R=C.Request;auto RO=Obj();Scalars(RO,"OperationId,ObjectId,SourceId,OwnerId,RoomInstanceId,AtTime,BeforeCoins",R.OperationId,R.ObjectId,R.SourceId,R.OwnerId,R.RoomInstanceId,R.AtTime,R.BeforeCoins);N("Request",RO);return O;});
        AR("RetiredEntities",S.RetiredEntities,[](const auto& R){auto O=Obj();J(R.RetiredAt);N("Actor",RewardActor(R.Actor));return O;});
        AR("RoomExits",S.RoomExits,[](const auto& R){auto O=Obj();J(R.RoomInstanceId,R.NextRoomInstanceId,R.AtTime);VA("EntityIds",R.EntityIds);VA("ObjectIds",R.ObjectIds);return O;});return O;
    }
    static JO Exploration(const FDungeonRunExplorationSnapshot& S)
    {
        auto O=Obj();J(S.Schema,S.CurrentRoomInstanceId);N("RunGuid",Guid(S.RunGuid));
        AR("Rooms",S.Rooms,[](const auto& R){auto O=Obj();J(R.RoomInstanceId,R.RoomNumber);const auto& F=R.State;auto FO=Obj();Scalars(FO,"Schema,RoomId",F.Schema,F.RoomId);auto B=Obj();Scalars(B,"MinX,MaxX,MinY,MaxY",F.Bounds.MinX,F.Bounds.MaxX,F.Bounds.MinY,F.Bounds.MaxY);FO->SetObjectField(TEXT("Bounds"),B);Values(FO,TEXT("Memory"),F.Memory);N("State",FO);return O;});return O;
    }
    static JO Audio(const FDungeonRunAudioContinuation& S)
    {
        auto O=Obj();J(S.Schema,S.RoomInstanceId,S.NextActionSequence,S.WorldHistoryThrough);N("RunGuid",Guid(S.RunGuid));
        AR("WeaponCursors",S.WeaponCursors,[](const auto& W){auto O=Obj();J(W.OwnerId);const auto& C=W.Cursor;auto CO=Obj();Scalars(CO,"Attached,DrawObserved,InsertObserved,LastEventId,RuntimeReceiptCount,LastObservedTime",C.Attached,C.DrawObserved,C.InsertObserved,C.LastEventId,C.RuntimeReceiptCount,C.LastObservedTime);CO->SetObjectField(TEXT("Reload"),Action(C.Reload));N("Cursor",CO);return O;});
        AR("StoneSeeds",S.StoneSeeds,[](const auto& K){auto O=Obj();J(K.EntityId,K.NextEventId);return O;});return O;
    }
    static JO Snapshot(const FDungeonRunSnapshot& S)
    {
        auto O=Obj();J(S.Schema,S.Scope,S.OwnerId,S.RoomInstanceId,S.RoomNumber,S.SimulationTime,S.LastStoneWakeStartedAt,S.RoomCleared,S.GameOver,S.WaitingForStart,S.SceneCommitRequested,S.SceneEquipmentTargetLost,S.LastMessage,S.SceneEncounterEntityId);
        N("RunGuid",Guid(S.RunGuid));{auto G=Obj();Scalars(G,"Schema,Kind",S.Geometry.Schema,S.Geometry.Kind);N("Geometry",G);}
        N("Equipment",Equipment(S.Equipment));N("Scene",Scene(S.Scene));N("WeaponWorld",World(S.WeaponWorld));AR("Fighters",S.Fighters,[](const auto& F){return Owner(F);});VA("EnemyOrder",S.EnemyOrder);N("Rewards",Rewards(S.Rewards));
        AR("Pickups",S.Pickups,[](const auto& P){auto O=Obj();J(P.Kind,P.Consumed,P.ObjectId,P.SourceId,P.RoomInstanceId);N("Position",Point(P.Position));N("RunGuid",Guid(P.RunGuid));return O;});N("Exploration",Exploration(S.Exploration));N("Audio",Audio(S.Audio));return O;
    }
    static JO Document(const FDungeonRunSnapshot& S){auto O=Obj();O->SetStringField(TEXT("codec"),TEXT("bound-run-v1"));N("snapshot",Snapshot(S));return O;}
#undef J
#undef N
#undef AR
#undef VA
    static FString Quote(const FString& S)
    {
        FString R=TEXT("\"");for(int32 I=0;I<S.Len();++I)
        {
            const TCHAR C=S[I];if(C==TEXT('"'))R+=TEXT("\\\"");else if(C==TEXT('\\'))R+=TEXT("\\\\");
            else if(uint32(C)<32)R+=FString::Printf(TEXT("\\u%04x"),uint32(C));else R.AppendChar(C);
        }
        return R+TEXT("\"");
    }
    static FString Canonical(const JV& V)
    {
        if(V->Type==EJson::Null)return TEXT("null");if(V->Type==EJson::Boolean)return V->AsBool()?TEXT("true"):TEXT("false");
        if(V->Type==EJson::String)return Quote(V->AsString());
        // Deliberately malformed test documents can inject a JSON number to
        // prove Decode rejects its token type. No Value() overload above ever
        // produces EJson::Number for a valid owning snapshot or expected wire.
        if(V->Type==EJson::Number)return FString::Printf(TEXT("%.17g"),V->AsNumber());
        if(V->Type==EJson::Array){FString R=TEXT("[");bool First=true;for(const auto& X:V->AsArray()){if(!First)R+=TEXT(",");First=false;R+=Canonical(X);}return R+TEXT("]");}
        if(V->Type==EJson::Object){FString R=TEXT("{");TArray<FString> Keys;V->AsObject()->Values.GetKeys(Keys);Keys.Sort([](const FString& A,const FString& B){return A.Compare(B,ESearchCase::CaseSensitive)<0;});bool First=true;for(const auto& K:Keys){if(!First)R+=TEXT(",");First=false;R+=Quote(K)+TEXT(":")+Canonical(V->AsObject()->Values[K]);}return R+TEXT("}");}
        checkNoEntry();return TEXT("INVALID-NUMERIC-JSON");
    }
    static TArray<uint8> Bytes(const JO& O){const auto S=Canonical(Value(O));FTCHARToUTF8 U(*S,S.Len());TArray<uint8> B;B.Append(reinterpret_cast<const uint8*>(U.Get()),U.Length());return B;}
    static TArray<uint8> Bytes(const FDungeonRunSnapshot& S){return Bytes(Document(S));}
};
}


namespace
{
// Complete typed-value signature, independent of Prepare/Install or a future codec.
// Codec preserves PendingPrimary as a saved value; installer input policy is separate.
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
    {String(L.Id.ToString());V(L.Version);Point(L.Entry);Point(L.Exit);Point(L.ExitHalfExtent);Point(L.Barrier.Min);Point(L.Barrier.Max);V(L.Barrier.bIsValid);Point(L.Survey);}
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
        Equipment(S.Equipment);Scene(S.Scene);World(S.WeaponWorld);V(S.Fighters.Num());for(const auto& F:S.Fighters)Owner(F,true);
        V(S.EnemyOrder.Num());for(uint64 I:S.EnemyOrder)V(I);Rewards(S.Rewards);V(S.Pickups.Num());for(const auto& P:S.Pickups){Point(P.Position);String(P.Kind.ToString());V(P.Consumed);Guid(P.RunGuid);V(P.ObjectId,P.SourceId,P.RoomInstanceId);}Exploration(S.Exploration);Audio(S.Audio);
    }
};
TArray<uint8> CodecSignature(const FDungeonRunSnapshot& S){FRunSignature B;B.Run(S);return B.Bytes;}
bool CodecSeal(FCodecWorld& F,FDungeonRunSnapshot& S,FDungeonValidatedRun& V,const TCHAR* Label)
{
    if(!F.Capture(Label,S))return false;FString Why;
    const bool Ok=FDungeonRunAggregate::Validate(S,V,Why);
    if(!Ok)F.Test.AddInfo(FString(Label)+TEXT(" independent Aggregate positive control: ")+Why);
    return F.Test.TestTrue(TEXT("Codec fixture passes independent complete Aggregate validation before codec"),Ok&&V.IsValid());
}
}
