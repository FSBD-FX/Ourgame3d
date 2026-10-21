#include "DungeonGameMode.h"
#include "DungeonCombatRules.h"
#include "DungeonFighter.h"
#include "DungeonRoomLayout.h"
#include "DungeonHUD.h"
#include "DungeonRunAggregate.h"
#include "DungeonNativeGeometryGuards.h"
#include "DungeonRunInstaller.h"
#include "Engine/Engine.h"
#include "Engine/Brush.h"
#include "Engine/Level.h"
#include "Engine/World.h"
#include "EngineUtils.h"
#include "Model.h"
#include "GameFramework/GameStateBase.h"
#include "GameFramework/PlayerController.h"
#include "GameFramework/PlayerState.h"
#include "GameFramework/SpectatorPawn.h"
#include "InputCoreTypes.h"
#include "Kismet/GameplayStatics.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
#include "CollisionQueryParams.h"
#include "CollisionShape.h"
#include "Components/BoxComponent.h"
#include "Components/BrushComponent.h"
#include "Components/PrimitiveComponent.h"
#include "PhysicsEngine/BodyInstance.h"
#include "Sound/SoundBase.h"
#include "HAL/PlatformTime.h"
#include <cmath>

namespace
{
bool PristineReject(FString& Why,const TCHAR* Message){Why=Message;return false;}
bool PristineDefaultStats(const DungeonEquipmentStats::FResolved& Value)
{
    const DungeonEquipmentStats::FResolved Empty;
    return Value.Error==Empty.Error&&Value.RawBonus.Values==Empty.RawBonus.Values&&Value.Final.Values==Empty.Final.Values
        &&Value.DamageMultiplier==Empty.DamageMultiplier&&Value.StaggerMultiplier==Empty.StaggerMultiplier
        &&Value.ActionTimeScale==Empty.ActionTimeScale&&Value.ReachMultiplier==Empty.ReachMultiplier
        &&Value.CritChancePct==Empty.CritChancePct&&Value.CritMultiplier==Empty.CritMultiplier
        &&Value.SkillCooldownMultiplier==Empty.SkillCooldownMultiplier&&Value.FocusCostMultiplier==Empty.FocusCostMultiplier
        &&Value.ReloadSeconds==Empty.ReloadSeconds&&Value.PrimaryFocusCost==Empty.PrimaryFocusCost&&Value.SkillFocusCost==Empty.SkillFocusCost
        &&Value.Armor==Empty.Armor&&Value.Ward==Empty.Ward&&Value.Poise==Empty.Poise
        &&Value.PhysicalMitigation==Empty.PhysicalMitigation&&Value.MagicMitigation==Empty.MagicMitigation
        &&Value.MaxHP==Empty.MaxHP&&Value.CurrentHP==Empty.CurrentHP&&Value.IdleMoveMultiplier==Empty.IdleMoveMultiplier&&Value.MoveSpeed==Empty.MoveSpeed
        &&Value.FocusRegen==Empty.FocusRegen&&Value.FocusDelay==Empty.FocusDelay&&Value.HealingMultiplier==Empty.HealingMultiplier
        &&Value.PhysicalVulnerabilityMultiplier==Empty.PhysicalVulnerabilityMultiplier&&Value.MagicVulnerabilityMultiplier==Empty.MagicVulnerabilityMultiplier;
}
bool PristineEmptyEquipment(const FDungeonEquipmentRuntimeSnapshot& Snapshot)
{
    const auto& View=Snapshot.View;const auto& Action=View.Action;const auto& Plan=Snapshot.PendingPlan;
    if(Snapshot.Schema!=1||Snapshot.HasInventory||View.Bound||View.Config!=EDungeonEquipmentRunConfig::IntegrationPreview
        ||View.RunGuid.IsValid()||View.RunAlias||View.OwnerId||View.RoomInstanceId||View.Revision||View.ActiveSlot
        ||View.SelectedSourceId||View.NeedsSlotSelection||View.SelectionSlot!=-1||View.LastFailure!=EDungeonEquipmentFailure::Unbound||!View.FailureText.IsEmpty()
        ||View.NextInstanceId!=1||View.NextSourceId!=1||View.NextOperationId!=1||View.NextEquipmentActionId!=1
        ||View.NextRuntimeReceiptId!=1||View.NextImportReceiptId!=1||View.NextFocusReceiptId!=1
        ||View.CombatSeed||View.NextCritDraw||!View.DeveloperCatalogIds.IsEmpty()||!PristineDefaultStats(View.Stats)
        ||Action.Kind!=EDungeonEquipmentActionKind::None||Action.Active||Action.ActionId||Action.OperationId||Action.SourceId||Action.InstanceId
        ||Action.Slot!=-1||Action.Start!=0.||Action.Deadline!=0.||!Snapshot.Sources.IsEmpty()||!Snapshot.CritReceipts.IsEmpty()
        ||Plan.Action!=DungeonEquipmentInventory::EAction::Pickup||Plan.Slot!=-1||Plan.BaseRevision||Plan.SourceId||Plan.SourceVersion
        ||Plan.InstanceId||Plan.InstanceVersion||Plan.ReplacedId||Snapshot.PendingHasDrop||Snapshot.PendingDropPosition!=FVector2D::ZeroVector)return false;
    for(const auto& Slot:View.Slots)
        if(Slot.InstanceId||Slot.Version||!Slot.ContentId.IsEmpty()||Slot.Grade||Slot.Tier||Slot.Package!=DungeonEquipmentStats::EPackage::None
            ||!Slot.Affixes.IsEmpty()||Slot.Ammo!=0.||Slot.CooldownDeadline!=0.)return false;
    return true;
}
bool PristineEmptyScene(const FDungeonSceneObjectsSnapshot& Scene)
{
    const auto& Room=Scene.CurrentRoom;const auto& Interaction=Scene.Interaction;
    const DungeonRoomLayout::FDescription Empty;const auto& Layout=Room.Layout;
    return Scene.Schema==1&&!Room.Active&&!Room.RunGuid.IsValid()&&!Room.RoomInstanceId&&Room.Objects.IsEmpty()&&Scene.Rooms.IsEmpty()
        &&!Interaction.Pending&&!Interaction.NeedsConfirmation&&Interaction.Kind==EDungeonSceneInteractionKind::None
        &&!Interaction.RoomInstanceId&&!Interaction.ObjectId&&Interaction.AtTime==0.&&Interaction.LastFailure==EDungeonSceneFailure::None
        &&Layout.Id.ToString().Equals(Empty.Id.ToString(),ESearchCase::CaseSensitive)&&Layout.Version==Empty.Version
        &&Layout.Entry==Empty.Entry&&Layout.Exit==Empty.Exit&&Layout.ExitHalfExtent==Empty.ExitHalfExtent&&Layout.Survey==Empty.Survey
        &&Layout.Barrier.Min==Empty.Barrier.Min&&Layout.Barrier.Max==Empty.Barrier.Max&&Layout.Barrier.bIsValid==Empty.Barrier.bIsValid;
}
// Exactly the existing Aggregate empty-builder exception; no actor names,
// blanket brush exemption, or registered collision component whitelist.
bool PristineKnownEmptyWorldBuilder(const UWorld* World,const AActor* Actor,const UPrimitiveComponent* Component)
{
    if(!World||!World->PersistentLevel||!World->PersistentLevel->Actors.IsValidIndex(1)
        ||World->PersistentLevel->Actors[1]!=Actor||Actor->GetClass()!=ABrush::StaticClass()
        ||Component->GetClass()!=UBrushComponent::StaticClass())return false;
    const auto* Builder=static_cast<const ABrush*>(Actor);const auto* Brush=Builder->GetBrushComponent();
    const auto* Model=Builder->Brush.Get();
    if(!Brush||Brush!=Component||Actor->GetRootComponent()!=Component||Builder->BrushType!=Brush_Default
        ||!Builder->IsNotForClientOrServer()||!Model||Brush->Brush!=Model
        ||!Model->Nodes.IsEmpty()||!Model->Verts.IsEmpty()||!Model->Points.IsEmpty()||!Model->Surfs.IsEmpty()
        ||Brush->BrushBodySetup)return false;
    if(World->GetDefaultBrush()!=Builder)return false;
    const auto* Body=Component->GetBodyInstance(NAME_None,false);
    return !Body||!Body->IsValidBodyInstance();
}
bool SkillClip(double P0, double P1, double Low, double High, double& Entry, double& Exit)
{
    const double D = P1-P0;
    if (D == 0.0) return P0 >= Low && P0 <= High;
    double A = (Low-P0)/D, B = (High-P0)/D;
    if (A > B) Swap(A,B);
    Entry = FMath::Max(Entry,A); Exit = FMath::Min(Exit,B);
    return Entry <= Exit && Entry <= 1.0 && Exit >= 0.0;
}
FCollisionObjectQueryParams SkillWallObjects()
{
    FCollisionObjectQueryParams Objects;
    Objects.AddObjectTypesToQuery(ECC_WorldStatic); Objects.AddObjectTypesToQuery(ECC_WorldDynamic);
    return Objects;
}
FVector2D ObservedPosition(const FDungeonKnightBody& B,double From,double To,double At)
{
    for (int32 I=B.MotionSegments.Num()-1;I>=0;--I)
    {
        const auto& M=B.MotionSegments[I];
        if (At>=M.FromTime && (At<M.ToTime || (!M.bEndExclusive && At==M.ToTime)))
            return FMath::Lerp(M.From,M.To,M.ToTime>M.FromTime?(At-M.FromTime)/(M.ToTime-M.FromTime):1.0);
    }
    return FMath::Lerp(B.Start,B.End,To>From?FMath::Clamp((At-From)/(To-From),0.0,1.0):1.0);
}
double BatObservedBodyHeight(const FDungeonKnightBody& B,double From,double To,double At)
{
    for(int32 I=B.MotionSegments.Num()-1;I>=0;--I){const auto& M=B.MotionSegments[I];
        if(At>=M.FromTime&&(At<M.ToTime||(!M.bEndExclusive&&At==M.ToTime)))return FMath::Lerp(M.FromHeight,M.ToHeight,M.ToTime>M.FromTime?(At-M.FromTime)/(M.ToTime-M.FromTime):1.);}
    return FMath::Lerp(B.StartHeight,B.EndHeight,To>From?FMath::Clamp((At-From)/(To-From),0.,1.):1.);
}
bool LeavesNativeZeroDepthBoxFace(const FHitResult& Hit,FVector2D Delta)
{
    if(Hit.Time!=0.f||!Hit.bStartPenetrating||Hit.PenetrationDepth!=0.f)return false;
    const auto Box=Cast<UBoxComponent>(Hit.GetComponent());
    if(!Box||Box->GetCollisionObjectType()!=ECC_WorldStatic)return false;
    const auto Q=Box->GetComponentQuat();
    if(Q.X!=0.||Q.Y!=0.||Q.Z!=0.||FMath::Abs(Q.W)!=1.)return false;
    const auto N=Hit.ImpactNormal;
    const bool AxisFace=N.Z==0.&&((FMath::Abs(N.X)==1.&&N.Y==0.)||(FMath::Abs(N.Y)==1.&&N.X==0.));
    // Native zero depth identifies a touching face. Linear movement away from
    // or along an unrotated box face cannot enter that face. Positive depth,
    // other geometry and later contacts retain the conservative wall rule.
    return AxisFace&&FVector2D::DotProduct(Delta,FVector2D(N.X,N.Y))>=0.;
}
}

ADungeonGameMode::ADungeonGameMode()
{
    PrimaryActorTick.bCanEverTick = true;
    DefaultPawnClass = ADungeonFighter::StaticClass();
    HUDClass = ADungeonHUD::StaticClass();
    EquipmentRuntime = MakeUnique<FDungeonEquipmentRuntime>();
    RunRewards = MakeUnique<FDungeonRunRewards>();
    RunExploration = MakeUnique<FDungeonRunExploration>();
    SceneObjects = MakeUnique<FDungeonSceneObjects>();
}

void ADungeonGameMode::InitGame(const FString& MapName,const FString& Options,FString& ErrorMessage)
{
    // Establish the private process origin before Super's InitGame broadcasts
    // and before native Login/HandleStartingNewPlayer can create a Pawn.
    if(!bRunInitGameSeen)
    {
        bRunInitGameSeen=true;
        if(UGameplayStatics::HasOption(Options,TEXT("DungeonContinuePristine")))
        {
            bPristineContinueOrigin=true;RunInstallGate=EDungeonRunInstallGate::PristineBootstrap;
            DefaultPawnClass=nullptr;SpectatorClass=nullptr;bStartPlayersAsSpectators=true;
        }
    }
    Super::InitGame(MapName,Options,ErrorMessage);
}
bool ADungeonGameMode::IsPristineContinueBootstrap(FString& Why) const
{
    if(RunInstallGate!=EDungeonRunInstallGate::PristineBootstrap||ActiveRunInstallToken||ActivePreparationPristine)
        return PristineReject(Why,TEXT("Target is not at its closed pristine startup boundary"));
    return CheckPristineUnpublishedState(nullptr,Why);
}
bool ADungeonGameMode::CheckPristineUnpublishedState(const FDungeonRunInstallGroup* Staged,FString& Why) const
{
    auto* World=GetWorld();
    if(!IsInGameThread()||!IsValid(this)||!World||World->bIsTearingDown||!GEngine||!GEngine->GetWorldContextFromWorld(World)
        ||World->GetAuthGameMode<ADungeonGameMode>()!=this||!bRunInitGameSeen||!bPristineContinueOrigin||bPristineContinueConsumed
        ||bRunTickActive||bSimulationBatch||bSimulatingMotion||!PendingDamage.IsEmpty())
        return PristineReject(Why,TEXT("Pristine preparation requires its original completed authoritative startup World"));
    if(Staged&&(RunInstallGate!=EDungeonRunInstallGate::Preparing||!ActivePreparationPristine||!Staged->PristineOrigin
        ||Staged->Game.Get()!=this||!Staged->Token||Staged->Token!=ActiveRunInstallToken))
        return PristineReject(Why,TEXT("Pristine prepared resources have no matching closed-origin token"));
    if(DefaultPawnClass||SpectatorClass||!bStartPlayersAsSpectators||!World->GetGameState()||World->GetGameState()->SpectatorClass)
        return PristineReject(Why,TEXT("Native automatic Pawn/spectator startup was not disabled at initialization"));
    if(PlayerFighter||!Enemies.IsEmpty()||!Pickups.IsEmpty()||!WorldEntityIds.IsEmpty()||!SceneWorldActors.IsEmpty()
        ||RunRestartSerial||RunPresentationEpoch||SimulationTime!=0.||LastStoneWakeStartedAt!=-1.
        ||RoomNumber!=1||bRoomCleared||bGameOver||!bWaitingForStart||!LastMessage.IsEmpty()
        ||SceneEncounterEntityId||bSceneCommitRequested||bSceneEquipmentTargetLost||bManualWeaponPreview||ManualWeaponPreviewRunGuid.IsValid()
        ||bFairytaleLookdevPreview||FairytaleLookdevEpoch!=0.||FairytaleLookdevFacing!=1
        ||!SkillBatchBodies.IsEmpty()||!MotionBatchBodies.IsEmpty()||!SkillOldIframeUntil.IsEmpty()||SkillBatchFrom!=0.||SkillBatchTo!=0.)
        return PristineReject(Why,TEXT("Target has already admitted gameplay owners, clocks, history or a new-Run boundary"));
    if(!EquipmentRuntime||EquipmentRuntime->GetInventoryState()||!PristineEmptyEquipment(EquipmentRuntime->Capture())
        ||!SceneObjects||!PristineEmptyScene(SceneObjects->Capture())||!RunRewards||!RunExploration)
        return PristineReject(Why,TEXT("Pristine equipment/scene containers are absent, bound or changed from empty construction"));
    const auto Rewards=RunRewards->Capture();const auto Fog=RunExploration->Capture();
    if(Rewards.Schema!=1||Rewards.Bound||Rewards.RunGuid.IsValid()||Rewards.OwnerId||Rewards.CurrentRoomInstanceId
        ||Rewards.NextSourceId!=1||Rewards.NextObjectId!=1||Rewards.NextOperationId!=1||Rewards.InitialCoins
        ||!Rewards.Deaths.IsEmpty()||!Rewards.Sources.IsEmpty()||!Rewards.Objects.IsEmpty()||!Rewards.Collections.IsEmpty()
        ||!Rewards.RetiredEntities.IsEmpty()||!Rewards.RoomExits.IsEmpty()||Fog.Schema!=1||Fog.RunGuid.IsValid()
        ||Fog.CurrentRoomInstanceId||!Fog.Rooms.IsEmpty()||RunExploration->CurrentView())
        return PristineReject(Why,TEXT("Pristine rewards/exploration contain a Run identity, allocation or memory history"));
    if(WeaponWorld.RunGuid.IsValid()||WeaponWorld.RoomInstanceId||WeaponWorld.Time!=0.||WeaponWorld.NextEventSequence!=1||WeaponWorld.NextEntityId!=2
        ||!WeaponWorld.ActorBindings.IsEmpty()||!WeaponWorld.Projectiles.IsEmpty()||!WeaponWorld.Windows.IsEmpty()||!WeaponWorld.HitReceipts.IsEmpty()
        ||!WeaponWorld.Burns.IsEmpty()||!WeaponWorld.Events.IsEmpty()||ActionAudioState.RunGuid.IsValid()||ActionAudioState.RoomInstanceId
        ||ActionAudioState.NextSequence!=1||!ActionAudioState.Records.IsEmpty()||!ActionAudioWeaponCursors.IsEmpty())
        return PristineReject(Why,TEXT("Pristine world/audio have already admitted entities, logical IDs or event history"));
    auto* Controller=UGameplayStatics::GetPlayerController(this,0);int32 Controllers=0;
    for(TActorIterator<APlayerController> It(World);It;++It)if(IsValid(*It)&&!It->IsActorBeingDestroyed())++Controllers;
    if(Controllers!=1||!IsValid(Controller)||Controller->GetWorld()!=World||!Controller->HasAuthority()||!Controller->IsLocalController()
        ||!Controller->GetLocalPlayer()||!Controller->PlayerInput||!Controller->PlayerState||Controller->PlayerState->IsOnlyASpectator()
        ||Controller->GetPawn()||Controller->GetSpectatorPawn()||!Cast<ADungeonHUD>(Controller->GetHUD()))
        return PristineReject(Why,TEXT("Pristine target needs one real local authoritative PC/Input/HUD with no existing Pawn or only-spectator restriction"));
    TSet<const AActor*> StagedActors;
    if(Staged)for(const auto& Reference:Staged->StagedActors)
    {
        const auto* Actor=Reference.Get();
        if(!IsValid(Actor)||Actor->IsActorBeingDestroyed()||Actor->GetWorld()!=World||!Actor->IsHidden()
            ||Actor->IsActorTickEnabled()||Actor->GetActorEnableCollision())
            return PristineReject(Why,TEXT("Pristine staging contains a released, foreign or externally activated actor"));
        StagedActors.Add(Actor);
    }
    for(TActorIterator<AActor> It(World);It;++It)
    {
        const auto* Actor=*It;if(!IsValid(Actor)||Actor->IsActorBeingDestroyed())continue;
        if(Actor->IsA<APawn>()&&!StagedActors.Contains(Actor))
            return PristineReject(Why,TEXT("Pristine World already contains an unrelated native Pawn/Fighter"));
        // Match Aggregate's actual collision boundary, including its exact
        // empty builder test. Disabled staging is not a blanket wall whitelist.
        if(!Actor->GetActorEnableCollision())continue;
        TInlineComponentArray<UPrimitiveComponent*> Components;Actor->GetComponents(Components);
        for(const auto* Component:Components)if(IsValid(Component)&&Component->IsRegistered()
            &&Component->GetCollisionEnabled()!=ECollisionEnabled::NoCollision)
        {
            if(PristineKnownEmptyWorldBuilder(World,Actor,Component))continue;
            if(DungeonNativeGeometryGuards::IsNativeGameplayDebuggerDrawOnly(World,Actor,Component))continue;
            Why=FString::Printf(TEXT("Pristine target refuses external collision: actorClass=%s actor=%s componentClass=%s component=%s"),
                *Actor->GetClass()->GetPathName(),*Actor->GetPathName(),*Component->GetClass()->GetPathName(),*Component->GetPathName());return false;
        }
    }
    Why.Reset();return true;
}

FDungeonEquipmentRuntimeSnapshot ADungeonGameMode::CaptureEquipmentSnapshot() const
{
    return EquipmentRuntime ? EquipmentRuntime->Capture() : FDungeonEquipmentRuntimeSnapshot{};
}

FDungeonRunRewardSnapshot ADungeonGameMode::CaptureRunRewardsSnapshot() const
{
    return RunRewards ? RunRewards->Capture() : FDungeonRunRewardSnapshot{};
}

FDungeonRunExplorationSnapshot ADungeonGameMode::CaptureRunExplorationSnapshot() const
{return !bRunTickActive&&RunExploration?RunExploration->Capture():FDungeonRunExplorationSnapshot{};}
const DungeonExploration::FExploration* ADungeonGameMode::GetCurrentRunExplorationView() const
{
    const auto& V=EquipmentRuntime->View;
    return V.Bound&&RunExploration&&RunExploration->Matches(V.RunGuid,V.RoomInstanceId)?RunExploration->CurrentView():nullptr;
}
void ADungeonGameMode::ObserveRunExploration()
{
    const auto& V=EquipmentRuntime->View;
    if(V.Bound&&RunExploration&&IsValid(PlayerFighter))
    {FString Why;RunExploration->Reveal(V.RunGuid,V.RoomInstanceId,RoomNumber,PlayerFighter->GetGroundPosition(),Why);}
}
bool ADungeonGameMode::CaptureRunSnapshot(FDungeonRunSnapshot& Out,FString& Why) const
{return FDungeonRunAggregate::Capture(*this,Out,Why);}

bool ADungeonGameMode::BeginRunInstallPreparation(uint64& Token,FString& Why)
{
    if(!IsInGameThread()||bRunTickActive||bSimulationBatch||bSimulatingMotion||!PendingDamage.IsEmpty()
        ||RunInstallGate!=EDungeonRunInstallGate::Open||!NextRunInstallToken||NextRunInstallToken==MAX_uint64)
    {Why=TEXT("Run preparation requires an open completed game-thread boundary");return false;}
    ActiveRunInstallToken=NextRunInstallToken++;Token=ActiveRunInstallToken;
    ActivePreparationPristine=false;
    RunInstallGate=EDungeonRunInstallGate::Preparing;
    RunInstallNeutralArmed=false;RunInstallPreviousEnter=false;Why.Reset();return true;
}
bool ADungeonGameMode::BeginPristineRunInstallPreparation(uint64& Token,FString& Why)
{
    if(!IsPristineContinueBootstrap(Why))return false;
    if(!NextRunInstallToken||NextRunInstallToken==MAX_uint64)
        return PristineReject(Why,TEXT("Pristine preparation process token is exhausted"));
    ActiveRunInstallToken=NextRunInstallToken++;Token=ActiveRunInstallToken;ActivePreparationPristine=true;
    RunInstallGate=EDungeonRunInstallGate::Preparing;
    RunInstallNeutralArmed=false;RunInstallPreviousEnter=false;Why.Reset();return true;
}
void ADungeonGameMode::AbortRunInstallPreparation(uint64 Token)
{
    if(RunInstallGate==EDungeonRunInstallGate::Preparing&&Token&&Token==ActiveRunInstallToken)
    {
        const bool ReturnPristine=ActivePreparationPristine;ActiveRunInstallToken=0;ActivePreparationPristine=false;
        RunInstallGate=ReturnPristine?EDungeonRunInstallGate::PristineBootstrap:EDungeonRunInstallGate::Open;
    }
}
bool ADungeonGameMode::CommitPreparedRunGroup(FDungeonRunInstallGroup& Group,FString& Why)
{
    const auto* Saved=Group.SavedValues();
    if(!IsInGameThread()||bRunTickActive||bSimulationBatch||bSimulatingMotion||!PendingDamage.IsEmpty()
        ||RunInstallGate!=EDungeonRunInstallGate::Preparing||Group.Game.Get()!=this
        ||!Group.Token||Group.Token!=ActiveRunInstallToken||Group.Committed||!Saved||Group.PristineOrigin!=ActivePreparationPristine
        ||!Group.Equipment||!Group.Scene||!Group.Rewards||!Group.Exploration
        ||Group.Fighters.Num()!=Saved->Fighters.Num()||Group.Fighters.IsEmpty()||RunPresentationEpoch==MAX_uint64)
    {Why=TEXT("Prepared group is not owned by this closed completed installation boundary");return false;}
    if(Group.PristineOrigin&&!CheckPristineUnpublishedState(&Group,Why))return false;
    for(const auto& Actor:Group.StagedActors)
        if(!Actor.IsValid()||Actor->GetWorld()!=GetWorld()||Actor->IsActorBeingDestroyed()
            ||!Actor->IsHidden()||Actor->IsActorTickEnabled()||Actor->GetActorEnableCollision())
        {Why=TEXT("A staged native resource was released or externally activated");return false;}
    auto* Controller=IsValid(PlayerFighter)?Cast<APlayerController>(PlayerFighter->GetController()):nullptr;
    if(!Controller)Controller=UGameplayStatics::GetPlayerController(this,0);
    if(!Controller||Controller->GetWorld()!=GetWorld()||!Controller->HasAuthority()
        ||!IsValid(Group.Fighters[0])||Group.Fighters[0]->GetController())
    {Why=TEXT("Installation requires a real authoritative controller and independent staged player");return false;}
    TArray<FDungeonPickup> NewPickups;
    for(const auto& P:Saved->Pickups)
    {FDungeonPickup N;N.Position=P.Position;N.Kind=P.Kind;N.bConsumed=P.Consumed;N.RunGuid=P.RunGuid;
        N.ObjectId=P.ObjectId;N.SourceId=P.SourceId;N.RoomInstanceId=P.RoomInstanceId;NewPickups.Add(MoveTemp(N));}
    TArray<TObjectPtr<ADungeonFighter>> NewEnemies;
    for(int32 I=1;I<Group.Fighters.Num();++I)NewEnemies.Add(Group.Fighters[I]);
    const auto OldPlayer=PlayerFighter;const auto OldEnemies=Enemies;const auto OldGeometry=SceneWorldActors;
    // Possession has no bool API. Observe the real native receiver before the
    // root swap; on rejection the still-installed old player regains control.
    Controller->Possess(Group.Fighters[0]);
    if(Controller->GetPawn()!=Group.Fighters[0])
    {if(IsValid(OldPlayer))Controller->Possess(OldPlayer);Why=TEXT("Native staged player possession was rejected");return false;}
    // All ordinary fallible owner/native work precedes this single closed-gate
    // publication. No Reset/BeginRun, actor admission, ID draw or simulation.
    EquipmentRuntime=MoveTemp(Group.Equipment);SceneObjects=MoveTemp(Group.Scene);
    RunRewards=MoveTemp(Group.Rewards);RunExploration=MoveTemp(Group.Exploration);
    WeaponWorld=MoveTemp(Group.WeaponWorld);WorldEntityIds=MoveTemp(Group.EntityIds);
    ActionAudioState=MoveTemp(Group.ActionAudio);ActionAudioWeaponCursors=MoveTemp(Group.AudioCursors);
    PlayerFighter=Group.Fighters[0];Enemies=MoveTemp(NewEnemies);Pickups=MoveTemp(NewPickups);
    SceneWorldActors=MoveTemp(Group.GeometryActors);
    SimulationTime=Saved->SimulationTime;LastStoneWakeStartedAt=Saved->LastStoneWakeStartedAt;
    RoomNumber=Saved->RoomNumber;bRoomCleared=Saved->RoomCleared;bGameOver=Saved->GameOver;
    bWaitingForStart=Saved->WaitingForStart;LastMessage=Saved->LastMessage;
    SceneEncounterEntityId=Saved->SceneEncounterEntityId;bSceneCommitRequested=Saved->SceneCommitRequested;
    bSceneEquipmentTargetLost=Saved->SceneEquipmentTargetLost;
    PendingDamage.Reset();SkillBatchBodies.Reset();MotionBatchBodies.Reset();SkillOldIframeUntil.Reset();
    bSimulationBatch=false;bSimulatingMotion=false;SkillBatchFrom=SkillBatchTo=SimulationTime;
    bManualWeaponPreview=false;ManualWeaponPreviewRunGuid.Invalidate();bFairytaleLookdevPreview=false;
    Group.Committed=true;ActiveRunInstallToken=0;ActivePreparationPristine=false;
    if(Group.PristineOrigin)bPristineContinueConsumed=true;
    RunInstallGate=EDungeonRunInstallGate::AwaitExplicitContinue;
    RunInstallNeutralArmed=false;RunInstallPreviousEnter=Controller->IsInputKeyDown(EKeys::Enter);
    SuppressRestoreContinueEnter=true;++RunPresentationEpoch;
    for(const auto& F:Group.Fighters){F->SetActorHiddenInGame(false);F->SetActorTickEnabled(false);F->SetActorEnableCollision(false);}
    for(const auto& G:SceneWorldActors)if(G.IsValid()){G->SetActorHiddenInGame(false);G->SetActorTickEnabled(false);G->SetActorEnableCollision(true);}
    if(auto* HUD=Cast<ADungeonHUD>(Controller->GetHUD()))HUD->AttachRestoredRunPresentation(Saved->Audio,RunPresentationEpoch);
    if(IsValid(OldPlayer)){OldPlayer->SetActorEnableCollision(false);OldPlayer->SetActorTickEnabled(false);OldPlayer->Destroy();}
    for(const auto& F:OldEnemies)if(IsValid(F)){F->SetActorEnableCollision(false);F->SetActorTickEnabled(false);F->Destroy();}
    for(const auto& G:OldGeometry)if(G.IsValid()){G->SetActorEnableCollision(false);G->SetActorTickEnabled(false);G->Destroy();}
    Why.Reset();return true;
}
namespace
{
bool RunInstallControlsNeutral(APlayerController* C,bool IgnoreEnter=false)
{
    if(!C||!C->IsLocalController()||!C->PlayerInput)return false;
    const FKey Keys[]={EKeys::W,EKeys::A,EKeys::S,EKeys::D,EKeys::Up,EKeys::Down,EKeys::Left,EKeys::Right,
        EKeys::J,EKeys::K,EKeys::E,EKeys::Q,EKeys::T,EKeys::R,EKeys::Tab,EKeys::Escape,EKeys::SpaceBar,
        EKeys::LeftShift,EKeys::RightShift,EKeys::LeftMouseButton,EKeys::RightMouseButton};
    for(FKey K:Keys)if(C->IsInputKeyDown(K))return false;
    if(!IgnoreEnter&&C->IsInputKeyDown(EKeys::Enter))return false;
    TArray<FKey> AllKeys;EKeys::GetAllKeys(AllKeys);
    for(const FKey& K:AllKeys)if(K.IsGamepadKey()&&(C->IsInputKeyDown(K)||C->GetInputAnalogKeyState(K)!=0.f))return false;
    return true;
}
}
bool ADungeonGameMode::RequestExplicitContinue(FString& Why)
{
    auto* C=UGameplayStatics::GetPlayerController(this,0);
    if(RunInstallGate!=EDungeonRunInstallGate::AwaitExplicitContinue||!RunInstallNeutralArmed
        ||!RunInstallControlsNeutral(C,true)||!C->IsInputKeyDown(EKeys::Enter)
        ||RunInstallPreviousEnter||!C->WasInputKeyJustPressed(EKeys::Enter))
    {Why=TEXT("Release all gameplay controls, then press a fresh real Enter to continue");return false;}
    RunInstallGate=EDungeonRunInstallGate::Open;RunInstallNeutralArmed=false;
    RunInstallPreviousEnter=true;SuppressRestoreContinueEnter=true;Why.Reset();return true;
}
void ADungeonGameMode::ObserveRunInstallInput()
{
    auto* C=UGameplayStatics::GetPlayerController(this,0);
    if(!C||!RunInstallControlsNeutral(C,true))RunInstallNeutralArmed=false;
    else if(!C->IsInputKeyDown(EKeys::Enter))RunInstallNeutralArmed=true;
    FString Why;if(C&&C->IsInputKeyDown(EKeys::Enter))RequestExplicitContinue(Why);
    RunInstallPreviousEnter=C&&C->IsInputKeyDown(EKeys::Enter);
}

FDungeonRunRewardCollectResult ADungeonGameMode::TryCollectRunReward(uint64 ObjectId, uint64 OperationId)
{
    if(IsRunInstallGated())return {};
    FDungeonRunRewardCollectResult Failed;Failed.Status=EDungeonRunRewardStatus::Unbound;
    const auto& V=EquipmentRuntime->View;
    if(!V.Bound||!RunRewards)return Failed;
    const auto Saved=RunRewards->Capture();
    if(!Saved.Bound||Saved.RunGuid!=V.RunGuid||Saved.OwnerId!=V.OwnerId
        ||Saved.CurrentRoomInstanceId!=V.RoomInstanceId){Failed.Status=EDungeonRunRewardStatus::WrongScope;return Failed;}
    // A retry reads the original result, even after movement/death/room exit.
    // It must never rewrite the current wallet to the historical AfterCoins.
    if(OperationId)
        if(const auto* Old=Saved.Collections.FindByPredicate([OperationId](const auto& X){return X.Request.OperationId==OperationId;}))
        {
            if(Old->Request.ObjectId!=ObjectId){Failed.Status=EDungeonRunRewardStatus::Conflict;return Failed;}
            FString Why;return RunRewards->CollectCoin(Old->Request,Why);
        }
    const auto* Object=Saved.Objects.FindByPredicate([ObjectId](const auto& X){return X.ObjectId==ObjectId;});
    if(!Object){Failed.Status=EDungeonRunRewardStatus::NotFound;return Failed;}
    if(Object->Retired){Failed.Status=EDungeonRunRewardStatus::Retired;return Failed;}
    if(Object->RoomInstanceId!=V.RoomInstanceId){Failed.Status=EDungeonRunRewardStatus::WrongScope;return Failed;}
    if(Object->Consumed){Failed.Status=EDungeonRunRewardStatus::AlreadyConsumed;return Failed;}
    if(Object->Kind!=EDungeonRunRewardKind::Coin){Failed.Status=EDungeonRunRewardStatus::Unsupported;return Failed;}
    auto* Physical=Pickups.FindByPredicate([ObjectId](const auto& X){return X.ObjectId==ObjectId;});
    if(!Physical||Physical->RunGuid!=V.RunGuid||Physical->SourceId!=Object->SourceId||Physical->RoomInstanceId!=V.RoomInstanceId
        ||Physical->Kind!=TEXT("coin")||Physical->Position!=Object->Position||Physical->bConsumed)
    {Failed.Status=EDungeonRunRewardStatus::Conflict;return Failed;}
    if(!IsValid(PlayerFighter)||PlayerFighter->GetRuntimeEntityId()!=V.OwnerId||PlayerFighter->bDead
        ||!FMath::IsFinite(PlayerFighter->Health)||PlayerFighter->Health<=0.f||bGameOver||bWaitingForStart||bSimulationBatch||bSimulatingMotion
        ||!FMath::IsFinite(PlayerFighter->JumpHeight)||!FMath::IsFinite(PlayerFighter->JumpVelocity)
        ||PlayerFighter->JumpHeight!=0.f||PlayerFighter->JumpVelocity>0.f)
    {Failed.Status=EDungeonRunRewardStatus::AdmissionRejected;return Failed;}
    const auto P=PlayerFighter->GetGroundPosition();const auto Delta=Object->Position-P;
    if(!FMath::IsFinite(P.X)||!FMath::IsFinite(P.Y)||FMath::Abs(Delta.X)>60.||FMath::Abs(Delta.Y)>30.)
    {Failed.Status=EDungeonRunRewardStatus::AdmissionRejected;return Failed;}
    FCollisionQueryParams Params(SCENE_QUERY_STAT(RunRewardCurrencyLOS),false);Params.AddIgnoredActor(PlayerFighter);
    FHitResult Hit;
    if(GetWorld()->LineTraceSingleByObjectType(Hit,FVector(P.X,P.Y,0.),FVector(Object->Position.X,Object->Position.Y,0.),SkillWallObjects(),Params)
        &&Hit.bBlockingHit){Failed.Status=EDungeonRunRewardStatus::AdmissionRejected;return Failed;}
    FDungeonRunRewardCollectRequest Q;Q.OperationId=OperationId?OperationId:Saved.NextOperationId;
    Q.ObjectId=ObjectId;Q.SourceId=Object->SourceId;Q.OwnerId=V.OwnerId;Q.RoomInstanceId=V.RoomInstanceId;
    Q.AtTime=SimulationTime;Q.BeforeCoins=PlayerFighter->Coins;FString Why;
    const auto Result=RunRewards->CollectCoin(Q,Why);
    if(Result.Ok()&&!Result.Replayed)
    {
        Physical->bConsumed=true;PlayerFighter->Coins=Result.AfterCoins;LastMessage=TEXT("拾取金币 +5");
    }
    return Result;
}

void ADungeonGameMode::CollectAutomaticRunRewards()
{
    if(!EquipmentRuntime->View.Bound)return;
    // Stable IDs were assigned at birth. Unsupported prototypes remain on ground.
    TArray<uint64> Coins;
    for(const auto& P:Pickups)if(!P.bConsumed&&P.Kind==TEXT("coin")&&P.ObjectId)Coins.Add(P.ObjectId);
    for(uint64 Id:Coins)TryCollectRunReward(Id);
}

bool ADungeonGameMode::RetireRunRewardRoom()
{
    const auto& V=EquipmentRuntime->View;if(!V.Bound)return true;
    if(!RunRewards)return false;
    FDungeonRunRewardRoomExit Exit;Exit.RoomInstanceId=V.RoomInstanceId;Exit.NextRoomInstanceId=V.RoomInstanceId+1;
    Exit.AtTime=SimulationTime;TArray<FDungeonRunRewardActorFact> Actors;
    for(auto Enemy:Enemies)if(IsValid(Enemy))
    {
        FDungeonRunRewardActorFact A;A.EntityId=FindWorldEntityId(Enemy);A.RoomInstanceId=V.RoomInstanceId;
        A.ContentId=Enemy->EnemyContentId.IsEmpty()?TEXT("QA-PROTOTYPE-ENEMY"):Enemy->EnemyContentId;
        A.Enemy=Enemy->bEnemy;A.Dead=Enemy->bDead;A.DeathReported=Enemy->bDeathReported;
        A.RewardClaimed=Enemy->StoneKnight?Enemy->StoneKnight->State().RewardClaimed
            :Enemy->StoneBat?Enemy->StoneBat->State().RewardClaimed:Enemy->bDeathReported;
        Actors.Add(A);Exit.EntityIds.Add(A.EntityId);
    }
    const auto Snapshot=RunRewards->Capture();
    for(const auto& O:Snapshot.Objects)if(O.RoomInstanceId==V.RoomInstanceId)Exit.ObjectIds.Add(O.ObjectId);
    FString Why;
    if(!RunRewards->RetireRoom(Exit,Actors,Why)){LastMessage=TEXT("离房奖励记录不一致：")+Why;return false;}
    return true;
}

bool ADungeonGameMode::BeginEquipmentRun(EDungeonEquipmentRunConfig Config, uint64 CombatSeed)
{
    if(IsRunInstallGated())return false;
    if (!IsValid(PlayerFighter) || PlayerFighter->StoneKnight || PlayerFighter->StoneBat || PlayerFighter->StoneGuard) return false;
    const FVector2D InitialPosition = PlayerFighter->GetGroundPosition();
    // This is the explicit new-Run boundary, never a transfer or continue operation.
    auto Runtime = MakeUnique<FDungeonEquipmentRuntime>();
    auto& V = Runtime->View;
    V.RunGuid = FGuid::NewGuid(); V.RunAlias = 1; V.OwnerId = 1; V.RoomInstanceId = 1;
    V.Config = Config; V.CombatSeed = CombatSeed; V.NextInstanceId = 2;
    V.DeveloperCatalogIds = {TEXT("WPN-SWD-001"),TEXT("WPN-GSW-001"),TEXT("WPN-SPR-001"),TEXT("WPN-XBW-001"),TEXT("WPN-STF-001"),
        TEXT("ARM-LGT-001"),TEXT("ARM-MED-001"),TEXT("ARM-HVY-001"),TEXT("ARM-ROB-001")};
    DungeonEquipmentInventory::FItem Starter; Starter.InstanceId = 1; Starter.ContentId = "WPN-SWD-001";
    Runtime->Inventory = MakeUnique<DungeonEquipmentInventory::FEquipmentInventory>(V.RunAlias,V.OwnerId,Starter);
    V.Stats = Runtime->Inventory->ResolveStats({},100.0);
    if (!V.Stats.Ok()) return false;
    auto RewardRuntime=MakeUnique<FDungeonRunRewards>();FString RewardWhy;
    const int32 InitialCoins=Config==EDungeonEquipmentRunConfig::FirstBatch?20:0;
    if(!RewardRuntime->Begin(V.RunGuid,V.OwnerId,V.RoomInstanceId,InitialCoins,RewardWhy))return false;
    auto ExplorationRuntime=MakeUnique<FDungeonRunExploration>();FString ExplorationWhy;
    if(!ExplorationRuntime->Begin(V.RunGuid,V.RoomInstanceId,1,ExplorationWhy))return false;
    bManualWeaponPreview=false;ManualWeaponPreviewRunGuid.Invalidate();
    ClearSceneWorldActors();SceneEncounterEntityId=0;bSceneEquipmentTargetLost=false;bSceneCommitRequested=false;
    SceneObjects->Reset();
    EquipmentRuntime = MoveTemp(Runtime); // Unbind old Run before the genuine initialization reset.
    RunRewards=MoveTemp(RewardRuntime);
    RunExploration=MoveTemp(ExplorationRuntime);
    WeaponWorld={};WeaponWorld.RunGuid=V.RunGuid;WeaponWorld.RoomInstanceId=V.RoomInstanceId;
    ActionAudioState={};ActionAudioState.RunGuid=V.RunGuid;ActionAudioState.RoomInstanceId=V.RoomInstanceId;
    ActionAudioWeaponCursors.Reset();
    WorldEntityIds.Reset();WorldEntityIds.Add(PlayerFighter,V.OwnerId);
    WeaponWorld.ActorBindings.Add({V.OwnerId,V.RoomInstanceId,TEXT("player")});
    for (auto Enemy : Enemies) if (IsValid(Enemy)) Enemy->Destroy();
    Enemies.Reset(); Pickups.Reset(); PendingDamage.Reset(); bSimulationBatch = false;
    SimulationTime = 0; LastStoneWakeStartedAt = -1; RoomNumber = 1; ++RunRestartSerial;
    bGameOver = false; bWaitingForStart = false; bRoomCleared = false;
    PlayerFighter->MaxHealth = 100; PlayerFighter->WeaponId = TEXT("WPN-SWD-001");
    PlayerFighter->ArmorId.Reset(); PlayerFighter->bHasAxe = false; PlayerFighter->bEnemy = false;
    PlayerFighter->ResetFighter(InitialPosition);
    PlayerFighter->Combat = DungeonContentCombat::FCombatKernel(DungeonContentCombat::EWeapon::SWD001,Starter.InstanceId);
    PlayerFighter->WeaponSkills = DungeonWeaponActions::FWeaponActionsKernel(DungeonContentCombat::EWeapon::SWD001,Starter.InstanceId,0,100);
    PlayerFighter->Dodge = DungeonDodge::FDodgeKernel(V.OwnerId,0,{InitialPosition.X,InitialPosition.Y});
    PlayerFighter->Coins = InitialCoins;
    V.Bound = true; EquipmentRuntime->Fail(EDungeonEquipmentFailure::None,TEXT(""));
    EquipmentRuntime->RefreshView(); UpdateEquipmentMirrors();
    SeedActionAudioWeapon(PlayerFighter);
    return true;
}

void ADungeonGameMode::AppendActionAudio(const TCHAR* Cue, double AtTime, uint64 OwnerId,
    uint64 ActionId, uint64 InstanceId, uint64 OperationId, uint64 Revision)
{
    const auto& V=EquipmentRuntime->View;
    if(!V.Bound||ActionAudioState.RunGuid!=V.RunGuid||!Cue||!OwnerId||!ActionId||!InstanceId||!Revision
        ||!FMath::IsFinite(AtTime)||AtTime<0.||!ActionAudioState.NextSequence
        ||ActionAudioState.NextSequence==TNumericLimits<uint64>::Max())return;
    ActionAudioState.RoomInstanceId=V.RoomInstanceId;
    FDungeonActionAudioRecord R;R.Sequence=ActionAudioState.NextSequence++;R.Cue=Cue;R.AtTime=AtTime;
    R.RunGuid=V.RunGuid;R.RoomInstanceId=V.RoomInstanceId;R.OwnerId=OwnerId;R.ActionId=ActionId;
    R.InstanceId=InstanceId;R.OperationId=OperationId;R.Revision=Revision;
    ActionAudioState.Records.Add(MoveTemp(R));
    // Keep a bounded presentation window. Sequence/cursors still prevent replay.
    if(ActionAudioState.Records.Num()>256)ActionAudioState.Records.RemoveAt(0);
}

void ADungeonGameMode::SeedActionAudioWeapon(ADungeonFighter* Fighter)
{
    if(!IsValid(Fighter)||!Fighter->IsEquipmentBound())return;
    const auto& S=Fighter->WeaponSkills.State();
    auto& Cursor=ActionAudioWeaponCursors.FindOrAdd(Fighter->GetRuntimeEntityId());Cursor={};
    Cursor.Attached=true;Cursor.LastEventId=S.NextEventId-1;
    Cursor.RuntimeReceiptCount=S.WeaponRuntimeHistory.size();Cursor.LastObservedTime=S.Time;
    if(S.Action.Active&&S.Action.Type==DungeonWeaponActions::EAction::Reload
        &&S.Action.Weapon==DungeonContentCombat::EWeapon::XBW001)
    {
        Cursor.Reload=S.Action;
        Cursor.DrawObserved=S.Time>=S.Action.Start+(S.Action.End-S.Action.Start)*(.20/1.10);
        Cursor.InsertObserved=S.Time>=S.Action.Start+(S.Action.End-S.Action.Start)*(.60/1.10);
    }
}

void ADungeonGameMode::ObservePendingActionAudio(ADungeonFighter* Fighter)
{
    if(IsValid(Fighter))ObserveActionAudio(Fighter,Fighter->WeaponSkills.State().PendingEvents);
}

void ADungeonGameMode::ObserveActionAudio(ADungeonFighter* Fighter,
    const std::vector<DungeonWeaponActions::FEvent>& Events, bool RuntimeSynchronized)
{
    namespace WA=DungeonWeaponActions;
    auto& V=EquipmentRuntime->View;
    if(!IsValid(Fighter)||!Fighter->IsEquipmentBound()||!V.Bound)return;
    const auto& S=Fighter->WeaponSkills.State();const uint64 AudioOwnerId=Fighter->GetRuntimeEntityId();
    if(ActionAudioState.RunGuid!=V.RunGuid)
    {
        ActionAudioState={};ActionAudioState.RunGuid=V.RunGuid;ActionAudioState.RoomInstanceId=V.RoomInstanceId;
        ActionAudioWeaponCursors.Reset();SeedActionAudioWeapon(Fighter);return;
    }
    ActionAudioState.RoomInstanceId=V.RoomInstanceId;
    auto& Cursor=ActionAudioWeaponCursors.FindOrAdd(AudioOwnerId);
    if(!Cursor.Attached||S.Time<Cursor.LastObservedTime||S.NextEventId<=Cursor.LastEventId
        ||S.WeaponRuntimeHistory.size()<Cursor.RuntimeReceiptCount)
    {SeedActionAudioWeapon(Fighter);return;}
    TArray<const WA::FWeaponRuntimeReceipt*> NewReloadReceipts;
    for(std::size_t I=Cursor.RuntimeReceiptCount;I<S.WeaponRuntimeHistory.size();++I)
        if(S.WeaponRuntimeHistory[I].Kind==WA::EWeaponMutation::ReloadCompleted)
            NewReloadReceipts.Add(&S.WeaponRuntimeHistory[I]);
    Cursor.RuntimeReceiptCount=S.WeaponRuntimeHistory.size();
    const auto ObservePhases=[this,&Cursor,&V,AudioOwnerId](double Cutoff,bool Inclusive)
    {
        const auto& A=Cursor.Reload;
        if(!A.ActionId)return;
        const double At[]={A.Start+(A.End-A.Start)*(.20/1.10),A.Start+(A.End-A.Start)*(.60/1.10)};
        bool* Observed[]={&Cursor.DrawObserved,&Cursor.InsertObserved};
        const TCHAR* Cues[]={TEXT("XBW_RELOAD_DRAW_01"),TEXT("XBW_RELOAD_INSERT_01")};
        for(int32 I=0;I<2;++I)if(!*Observed[I]&&(Inclusive?At[I]<=Cutoff:At[I]<Cutoff))
        {
            AppendActionAudio(Cues[I],At[I],AudioOwnerId,A.ActionId,A.InstanceId,0,V.Revision);
            *Observed[I]=true;
        }
    };
    for(const auto& E:Events)
    {
        if(E.EventId<=Cursor.LastEventId)continue;
        Cursor.LastEventId=E.EventId;
        if(E.Action.Type!=WA::EAction::Reload||E.Action.Weapon!=DungeonContentCombat::EWeapon::XBW001)continue;
        if(E.Kind==WA::EEvent::ReloadStarted)
        {
            Cursor.Reload=E.Action;Cursor.DrawObserved=false;Cursor.InsertObserved=false;
        }
        if(E.ActionId!=Cursor.Reload.ActionId||E.InstanceId!=Cursor.Reload.InstanceId)continue;
        if(E.Kind==WA::EEvent::ReloadCancelled||E.Kind==WA::EEvent::Interrupted)
        {
            // Damage/cancellation already won this endpoint. Only strictly
            // earlier actual phases may produce a presentation fact.
            ObservePhases(E.AtTime,false);Cursor.Reload={};
        }
        else if(E.Kind==WA::EEvent::ReloadCompleted)
        {
            ObservePhases(E.AtTime,true);
            const WA::FWeaponRuntimeReceipt* Receipt=nullptr;
            for(const auto* R:NewReloadReceipts)
                if(R->EventId==E.EventId&&R->Action.ActionId==E.ActionId&&R->Action.InstanceId==E.InstanceId
                    &&R->AtTime==E.AtTime&&R->AtTime==R->Action.End&&R->Action.Start==Cursor.Reload.Start
                    &&R->Action.End==Cursor.Reload.End&&R->Action.Type==WA::EAction::Reload
                    &&R->Action.Weapon==DungeonContentCombat::EWeapon::XBW001&&!R->Action.Active
                    &&R->Action.Terminal==WA::EEvent::ReloadCompleted&&R->BeforeAmmo<R->AfterAmmo&&R->AfterAmmo==1.)Receipt=R;
            const auto* Item=EquipmentRuntime->FindItem(E.InstanceId);
            const auto* Instance=Fighter->WeaponSkills.Instance(E.InstanceId);
            if(RuntimeSynchronized&&Receipt&&Item&&Instance&&Item->Ammo==Receipt->AfterAmmo
                &&Instance->Ammo==Receipt->AfterAmmo&&Item->ContentId=="WPN-XBW-001")
                AppendActionAudio(TEXT("XBW_RELOAD_COMPLETE_01"),E.AtTime,AudioOwnerId,E.ActionId,E.InstanceId,0,V.Revision);
            Cursor.Reload={};
        }
    }
    if(Cursor.Reload.ActionId&&S.Action.Active&&S.Action.Type==WA::EAction::Reload
        &&S.Action.ActionId==Cursor.Reload.ActionId&&S.Action.InstanceId==Cursor.Reload.InstanceId)
        ObservePhases(S.Time,true);
    Cursor.LastObservedTime=S.Time;
}
bool ADungeonGameMode::BeginManualWeaponPreview()
{
    if(IsRunInstallGated())return false;
    if(bManualWeaponPreview&&EquipmentRuntime->View.Bound&&ManualWeaponPreviewRunGuid==EquipmentRuntime->View.RunGuid)return true;
    return SetupManualWeaponPreviewRun();
}

bool ADungeonGameMode::BeginSceneExplorationPreview()
{
    if(IsRunInstallGated())return false;
    const auto& Room=SceneObjects->Current();
    if(Room.Active&&EquipmentRuntime->View.Bound&&Room.RunGuid==EquipmentRuntime->View.RunGuid)return true;
    return SetupSceneExplorationPreviewRun();
}

bool ADungeonGameMode::SetupSceneExplorationPreviewRun()
{
    if(!IsValid(PlayerFighter)||PlayerFighter->StoneKnight||PlayerFighter->StoneBat||PlayerFighter->StoneGuard||!GetWorld())return false;
    const auto Layout=DungeonRoomLayout::ExplorationPreview();
    PlayerFighter->SetActorLocation(FVector(Layout.Entry.X,Layout.Entry.Y,0.));
    if(!BeginEquipmentRun(EDungeonEquipmentRunConfig::IntegrationPreview,1))return false;
    PlayerFighter->SetActorTickEnabled(false);
    if(!SceneObjects->BeginRoom(EquipmentRuntime->View.RunGuid,EquipmentRuntime->View.RoomInstanceId))return false;
    if(!SpawnSceneExplorationRoom())return false;
    bWaitingForStart=true;
    LastMessage=TEXT("沿侧路调查遗迹，击败守卫后前往出口。Enter开始。");
    return true;
}

const FDungeonSceneRoomView& ADungeonGameMode::GetSceneRoomView() const { return SceneObjects->Current(); }
const FDungeonSceneRoomView* ADungeonGameMode::FindSceneRoomView(uint64 RoomInstanceId) const { return SceneObjects->FindRoom(RoomInstanceId); }
const FDungeonSceneInteractionView& ADungeonGameMode::GetSceneInteractionView() const { return SceneObjects->Interaction; }
void ADungeonGameMode::ClearSceneWorldActors()
{
    for(const auto& Actor:SceneWorldActors)if(Actor.IsValid()){Actor->SetActorEnableCollision(false);Actor->Destroy();}
    SceneWorldActors.Reset();
}

bool ADungeonGameMode::SpawnSceneExplorationRoom()
{
    const auto& Room=SceneObjects->Current();
    if(!Room.Active||!EquipmentRuntime->View.Bound||Room.RunGuid!=EquipmentRuntime->View.RunGuid
        ||Room.RoomInstanceId!=EquipmentRuntime->View.RoomInstanceId||!GetWorld())return false;
    ClearSceneWorldActors();SceneEncounterEntityId=0;
    const auto& Wall=Room.Layout.Barrier;
    auto WallActor=GetWorld()->SpawnActor<AActor>();if(!WallActor)return false;
    auto Box=NewObject<UBoxComponent>(WallActor);WallActor->SetRootComponent(Box);
    const auto Half=Wall.GetExtent(),Center=Wall.GetCenter();
    Box->SetBoxExtent(FVector(Half.X,Half.Y,80.));Box->SetCollisionEnabled(ECollisionEnabled::QueryOnly);
    Box->SetCollisionObjectType(ECC_WorldStatic);Box->SetCollisionResponseToAllChannels(ECR_Block);
    Box->RegisterComponentWithWorld(GetWorld());WallActor->SetActorLocation(FVector(Center.X,Center.Y,40.));
    SceneWorldActors.Add(WallActor);
    auto Knight=GetWorld()->SpawnActor<ADungeonFighter>();if(!Knight)return false;
    Knight->bEnemy=true;Knight->EnemyContentId=TEXT("ENM-STN-001");
    Knight->SetActorTickEnabled(false);Knight->ResetFighter({300.,0.});Enemies.Add(Knight);AdmitWorldFighters();
    const uint64 Entity=FindWorldEntityId(Knight);
    if(!Entity||!Knight->InitializeStoneKnight(Entity,SimulationTime))return false;
    SceneEncounterEntityId=Entity;bRoomCleared=false;return true;
}

bool ADungeonGameMode::CanBeginSceneInteraction() const
{
    const auto F=PlayerFighter;const auto& V=EquipmentRuntime->View;const auto& Room=SceneObjects->Current();
    return Room.Active&&V.Bound&&Room.RunGuid==V.RunGuid&&Room.RoomInstanceId==V.RoomInstanceId
        &&IsValid(F)&&!bGameOver&&!bWaitingForStart&&!F->bDead&&!V.Action.Active&&!V.NeedsSlotSelection
        &&F->HurtTime<=0.f&&F->JumpHeight==0.f&&F->JumpVelocity<=0.f&&!F->Combat.State().Action.Active
        &&!F->WeaponSkills.State().Action.Active&&F->AttackTime<=0.f&&F->AttackCooldown<=0.f&&F->ArmorChangeRemaining<=0.f
        &&F->Dodge.State().Phase==DungeonDodge::EPhase::Idle&&F->ReadMoveIntent().IsNearlyZero();
}

EDungeonSceneFailure ADungeonGameMode::SceneObjectAdmission(const FDungeonSceneObjectView& Object) const
{
    const auto& Room=SceneObjects->Current();
    if(!Room.Active||Room.RunGuid!=EquipmentRuntime->View.RunGuid||Object.RoomInstanceId!=Room.RoomInstanceId
        ||Room.RoomInstanceId!=EquipmentRuntime->View.RoomInstanceId)return EDungeonSceneFailure::InvalidRoom;
    if(!CanBeginSceneInteraction())return EDungeonSceneFailure::Busy;
    const auto P=PlayerFighter->GetGroundPosition(),Delta=Object.Position-P;
    if(FMath::Abs(Delta.X)>80.||FMath::Abs(Delta.Y)>40.)return EDungeonSceneFailure::NotInRange;
    FCollisionQueryParams Params(SCENE_QUERY_STAT(SceneObjectLOS),false);Params.AddIgnoredActor(PlayerFighter);FHitResult Hit;
    if(GetWorld()->LineTraceSingleByObjectType(Hit,FVector(P.X,P.Y,0.),FVector(Object.Position.X,Object.Position.Y,0.),SkillWallObjects(),Params)
        &&Hit.bBlockingHit)return EDungeonSceneFailure::NoLineOfSight;
    if(Object.Kind==EDungeonSceneObjectKind::Survey&&Object.Surveyed)return EDungeonSceneFailure::AlreadySurveyed;
    if(Object.Kind==EDungeonSceneObjectKind::Exit)
    {
        const auto Encounter=FindWorldFighter(SceneEncounterEntityId);
        if(!SceneEncounterEntityId||!IsValid(Encounter)||!Encounter->bDead||!Encounter->bDeathReported||!bRoomCleared)
            return EDungeonSceneFailure::RoomNotCleared;
        for(const auto Enemy:Enemies)if(IsValid(Enemy)&&!Enemy->bDead)return EDungeonSceneFailure::RoomNotCleared;
        if(RoomNumber==MAX_int32||Room.RoomInstanceId==MAX_uint64)return EDungeonSceneFailure::InvalidRoom;
    }
    return EDungeonSceneFailure::None;
}

bool ADungeonGameMode::TryInteractScene()
{
    auto& I=SceneObjects->Interaction;
    if(I.Pending)return false; // E only opens; it never confirms a live layer.
    I={};
    const auto& Room=SceneObjects->Current();const FDungeonSceneObjectView* Best=nullptr;double Score=TNumericLimits<double>::Max();
    if(!CanBeginSceneInteraction())
    {
        I.LastFailure=EDungeonSceneFailure::Busy;LastMessage=TEXT("请落地站定，并结束当前动作后再交互。");return false;
    }
    for(const auto& Object:Room.Objects)
    {
        const auto D=Object.Position-PlayerFighter->GetGroundPosition();
        if(FMath::Abs(D.X)>80.||FMath::Abs(D.Y)>40.)continue;
        const double Distance=FMath::Square(D.X/80.)+FMath::Square(D.Y/40.);
        if(Distance<Score||(Distance==Score&&Best&&Object.ObjectId<Best->ObjectId)){Best=&Object;Score=Distance;}
    }
    if(!Best){I.LastFailure=EDungeonSceneFailure::NoTarget;return false;}
    EquipmentRuntime->Fail(EDungeonEquipmentFailure::None,TEXT(""));
    I.LastFailure=SceneObjectAdmission(*Best);
    if(I.LastFailure!=EDungeonSceneFailure::None)
    {
        if(I.LastFailure==EDungeonSceneFailure::RoomNotCleared)LastMessage=TEXT("战斗尚未结束，出口封闭。");
        else if(I.LastFailure==EDungeonSceneFailure::NoLineOfSight)LastMessage=TEXT("路线被遮挡，无法调查或离开。");
        else if(I.LastFailure==EDungeonSceneFailure::AlreadySurveyed)LastMessage=TEXT("此处已经调查。");
        return false;
    }
    I.Pending=true;I.NeedsConfirmation=Best->Kind==EDungeonSceneObjectKind::Exit;
    I.Kind=I.NeedsConfirmation?EDungeonSceneInteractionKind::Exit:EDungeonSceneInteractionKind::Survey;
    I.RoomInstanceId=Room.RoomInstanceId;I.ObjectId=Best->ObjectId;I.AtTime=SimulationTime;
    bSceneCommitRequested=!I.NeedsConfirmation;
    EquipmentRuntime->Fail(EDungeonEquipmentFailure::None,TEXT(""));
    if(I.NeedsConfirmation)LastMessage=TEXT("离开后无法返回，遗留物品不会带走。Enter离开，Esc继续探索。");
    return true;
}

bool ADungeonGameMode::ConfirmSceneInteraction(bool FreshPress)
{
    if(IsRunInstallGated())return false;
    auto& I=SceneObjects->Interaction;
    if(!FreshPress||!I.Pending||!I.NeedsConfirmation||I.Kind!=EDungeonSceneInteractionKind::Exit)return false;
    ValidateSceneConfirmation();if(!I.Pending)return false;
    I.NeedsConfirmation=false;I.AtTime=SimulationTime;bSceneCommitRequested=true;return true;
}

void ADungeonGameMode::CancelSceneInteraction()
{
    if(IsRunInstallGated())return;
    const auto& Pending=SceneObjects->Interaction;
    const bool WasCurrentExit=Pending.Pending&&Pending.Kind==EDungeonSceneInteractionKind::Exit
        &&SceneObjects->Current().Active&&Pending.RoomInstanceId==SceneObjects->Current().RoomInstanceId;
    bSceneCommitRequested=false;SceneObjects->Interaction={};
    if(WasCurrentExit&&!bGameOver&&IsValid(PlayerFighter)&&!PlayerFighter->bDead)
        LastMessage=TEXT("继续探索。靠近出口按E可再次查看离开提示。");
}

void ADungeonGameMode::ValidateSceneConfirmation()
{
    auto& I=SceneObjects->Interaction;if(!I.Pending)return;
    const FDungeonSceneObjectView* Target=nullptr;
    const auto& Room=SceneObjects->Current();
    if(I.RoomInstanceId==Room.RoomInstanceId)for(const auto& Object:Room.Objects)if(Object.ObjectId==I.ObjectId){Target=&Object;break;}
    const auto Failure=Target?SceneObjectAdmission(*Target):EDungeonSceneFailure::InvalidRoom;
    if(Failure!=EDungeonSceneFailure::None){CancelSceneInteraction();I.LastFailure=Failure;}
}

void ADungeonGameMode::CommitSceneInteraction()
{
    if(!bSceneCommitRequested)return;
    bSceneCommitRequested=false;
    const auto Request=SceneObjects->Interaction;
    ValidateSceneConfirmation();if(!SceneObjects->Interaction.Pending)return;
    // All old and newly emitted same-point damage/death has already committed.
    // This point is neither advanced by epsilon nor restored after a query.
    CancelSceneInteraction();
    if(Request.Kind==EDungeonSceneInteractionKind::Survey)
    {
        if(SceneObjects->MarkSurvey(Request.RoomInstanceId,Request.ObjectId))LastMessage=TEXT("碑文：旧城守卫仍守着东门，碎墙西侧还有旧路。");
    }
    else if(Request.Kind==EDungeonSceneInteractionKind::Exit)NextRoom();
}

bool ADungeonGameMode::SetupManualWeaponPreviewRun()
{
    if(!IsValid(PlayerFighter)||PlayerFighter->StoneKnight||PlayerFighter->StoneBat||PlayerFighter->StoneGuard||!GetWorld())return false;
    PlayerFighter->SetActorLocation(FVector(-460.,0.,0.));
    if(!BeginEquipmentRun(EDungeonEquipmentRunConfig::IntegrationPreview,1))return false;
    PlayerFighter->SetActorTickEnabled(false);
    DungeonEquipmentInventory::FItem Crossbow;Crossbow.ContentId="WPN-XBW-001";Crossbow.Ammo=1.;
    // A deliberately loaded development source, transferred by normal E. No
    // opening equip, refill, formal loot provenance or persistence is implied.
    const auto Source=RegisterEquipmentSource(TEXT("qa.manual.weapon.xbw"),Crossbow,{-420.,0.},true);
    if(!Source.Ok())return false;
    auto Knight=GetWorld()->SpawnActor<ADungeonFighter>();if(!Knight)return false;
    Knight->bEnemy=true;Knight->bAIEnabled=false;Knight->EnemyContentId=TEXT("ENM-STN-001");
    Knight->SetActorTickEnabled(false);Knight->ResetFighter({300.,0.});Enemies.Add(Knight);AdmitWorldFighters();
    const uint64 Entity=FindWorldEntityId(Knight);
    if(!Entity||!Knight->InitializeStoneKnight(Entity,SimulationTime))
    {
        Enemies.Remove(Knight);WorldEntityIds.Remove(Knight);
        WeaponWorld.ActorBindings.RemoveAll([Entity](const FDungeonWorldActorBinding& B){return B.EntityId==Entity;});Knight->Destroy();return false;
    }
    bManualWeaponPreview=true;ManualWeaponPreviewRunGuid=EquipmentRuntime->View.RunGuid;
    bWaitingForStart=true;UpdateEquipmentTarget();
    LastMessage=TEXT("开发QA武器预览：Enter开始，E拾取猎弩，Q切换，J射击，T装填，R重开。猎弩为测试来源，本预览不存档。");
    return true;
}

FDungeonEquipmentRegistration ADungeonGameMode::RegisterEquipmentSource(const FString& LogicalKey,
    const DungeonEquipmentInventory::FItem& Prototype, FVector2D Position, bool Settled)
{
    if(IsRunInstallGated())return {};
    auto& R = *EquipmentRuntime; auto& V = R.View;
    if (!V.Bound) return {};
    if (LogicalKey.IsEmpty() || Prototype.InstanceId != 0 || Prototype.Version != 1
        || !V.NextInstanceId || V.NextInstanceId==TNumericLimits<uint64>::Max() || !V.NextSourceId || V.NextSourceId==TNumericLimits<uint64>::Max()
        || !FMath::IsFinite(Position.X) || !FMath::IsFinite(Position.Y)
        || Position.X<DungeonRoomLayout::MinX || Position.X>DungeonRoomLayout::MaxX || Position.Y<DungeonRoomLayout::MinY || Position.Y>DungeonRoomLayout::MaxY
        || !V.DeveloperCatalogIds.Contains(FString(UTF8_TO_TCHAR(Prototype.ContentId.c_str()))))
        return {false,false,0,0,EDungeonEquipmentFailure::InvalidRequest};
    for (const auto& Existing : R.Sources)
        if (Existing.RoomInstanceId == V.RoomInstanceId && Existing.LogicalKey == LogicalKey)
        {
            auto CandidateItem = Prototype; CandidateItem.InstanceId = Existing.InstanceId;
            auto Candidate = *R.Inventory;
            const auto Result = Candidate.RegisterWorldSource(Existing.SourceId,CandidateItem);
            const bool Same = Result.Ok() && Existing.Position == Position && Existing.Settled == Settled;
            return {Same,Same,Same?Existing.SourceId:0,Same?Existing.InstanceId:0,
                Same?EDungeonEquipmentFailure::None:EDungeonEquipmentFailure::SourceConflict};
        }
    auto Item = Prototype; Item.InstanceId = V.NextInstanceId;
    auto Candidate = *R.Inventory;
    const auto Result = Candidate.RegisterWorldSource(V.NextSourceId,Item);
    if (!Result.Ok()) return {false,false,0,0,EDungeonEquipmentFailure::InvalidRequest};
    const uint64 SourceId = V.NextSourceId;
    *R.Inventory = MoveTemp(Candidate);
    R.Sources.Add({SourceId,Item.InstanceId,1,V.RoomInstanceId,LogicalKey,Position,Settled,false,Item});
    ++V.NextInstanceId; ++V.NextSourceId; R.RefreshView(); UpdateEquipmentTarget();
    return {true,false,SourceId,Item.InstanceId,EDungeonEquipmentFailure::None};
}
const FDungeonEquipmentView& ADungeonGameMode::GetEquipmentView() const { return EquipmentRuntime->GetView(); }
const TArray<FDungeonEquipmentSourceView>& ADungeonGameMode::GetEquipmentSources() const { return EquipmentRuntime->GetSources(); }
const DungeonEquipmentInventory::FState* ADungeonGameMode::GetEquipmentInventoryState() const { return EquipmentRuntime->GetInventoryState(); }
bool ADungeonGameMode::CanBeginEquipmentAction(bool Switching) const
{
    const auto F = PlayerFighter;
    if (!EquipmentRuntime->View.Bound || !IsValid(F) || bGameOver || bWaitingForStart || F->bDead
        || EquipmentRuntime->View.Action.Active || F->HurtTime > 0 || F->JumpHeight > 0 || F->JumpVelocity > 0
        || F->Combat.State().Action.Active || (F->AttackTime > 0 && !(Switching && F->WeaponSkills.State().Action.Active && F->WeaponSkills.State().Action.Type==DungeonWeaponActions::EAction::Reload))
        || F->AttackCooldown > 0 || F->ArmorChangeRemaining > 0
        || F->Dodge.State().Phase != DungeonDodge::EPhase::Idle || !F->ReadMoveIntent().IsNearlyZero()) return false;
    if (!EquipmentRuntime->View.NextEquipmentActionId || EquipmentRuntime->View.NextEquipmentActionId==TNumericLimits<uint64>::Max()
        || !EquipmentRuntime->View.NextOperationId || EquipmentRuntime->View.NextOperationId==TNumericLimits<uint64>::Max()) return false;
    const auto& A = F->WeaponSkills.State().Action;
    return !A.Active || (Switching && A.Type == DungeonWeaponActions::EAction::Reload);
}
EDungeonEquipmentFailure ADungeonGameMode::EquipmentSourceAdmission(const FDungeonEquipmentSourceView& Source) const
{
    if (!IsValid(PlayerFighter) || Source.Consumed || Source.RoomInstanceId != EquipmentRuntime->View.RoomInstanceId || !Source.Settled
        || !FMath::IsFinite(Source.Position.X) || !FMath::IsFinite(Source.Position.Y)
        || Source.Position.X<DungeonRoomLayout::MinX || Source.Position.X>DungeonRoomLayout::MaxX
        || Source.Position.Y<DungeonRoomLayout::MinY || Source.Position.Y>DungeonRoomLayout::MaxY)
        return EDungeonEquipmentFailure::InvalidSource;
    const auto P = PlayerFighter->GetGroundPosition(), D = Source.Position-P;
    if (FMath::Abs(D.X) > 80 || FMath::Abs(D.Y) > 40) return EDungeonEquipmentFailure::NotInRange;
    FCollisionQueryParams Params(SCENE_QUERY_STAT(EquipmentSourceLOS),false); Params.AddIgnoredActor(PlayerFighter);
    FHitResult Hit;
    if (GetWorld()->LineTraceSingleByObjectType(Hit,FVector(P.X,P.Y,0),FVector(Source.Position.X,Source.Position.Y,0),SkillWallObjects(),Params)
        && Hit.bBlockingHit) return EDungeonEquipmentFailure::NoLineOfSight;
    return EDungeonEquipmentFailure::None;
}
void ADungeonGameMode::UpdateEquipmentTarget()
{
    auto& R = *EquipmentRuntime; auto& V = R.View;
    if (!V.Bound || V.Action.Active || V.NeedsSlotSelection || !IsValid(PlayerFighter)) return;
    if (const auto* Selected = R.FindSource(V.SelectedSourceId))
        if (EquipmentSourceAdmission(*Selected) == EDungeonEquipmentFailure::None) return;
    if(V.SelectedSourceId&&SceneObjects->Current().Active)bSceneEquipmentTargetLost=true;
    V.SelectedSourceId = 0; double Best = TNumericLimits<double>::Max();
    for (const auto& Source : R.Sources) if (EquipmentSourceAdmission(Source) == EDungeonEquipmentFailure::None)
    {
        const auto D = Source.Position-PlayerFighter->GetGroundPosition();
        const double Score = FMath::Square(D.X/80)+FMath::Square(D.Y/40);
        if (Score < Best || (Score == Best && Source.SourceId < V.SelectedSourceId)) {Best=Score;V.SelectedSourceId=Source.SourceId;}
    }
}
bool ADungeonGameMode::SelectEquipmentSource(uint64 SourceId)
{
    if(IsRunInstallGated())return false;
    auto& R = *EquipmentRuntime;
    const auto* Source = R.FindSource(SourceId);
    if (!R.View.Bound || R.View.Action.Active || !Source || Source->Consumed || Source->RoomInstanceId != R.View.RoomInstanceId) return false;
    CancelEquipmentSelection(); R.View.SelectedSourceId = SourceId;bSceneEquipmentTargetLost=false;return true;
}
bool ADungeonGameMode::CycleEquipmentTarget()
{
    if(IsRunInstallGated())return false;
    auto& R = *EquipmentRuntime; auto& V = R.View;
    if (!V.Bound || V.Action.Active || V.NeedsSlotSelection) return false;
    TArray<uint64> Eligible;
    for (const auto& S : R.Sources) if (EquipmentSourceAdmission(S)==EDungeonEquipmentFailure::None) Eligible.Add(S.SourceId);
    Eligible.Sort([this,&R](uint64 A,uint64 B)
    {
        const auto P=PlayerFighter->GetGroundPosition(); const auto DA=R.FindSource(A)->Position-P,DB=R.FindSource(B)->Position-P;
        const double SA=FMath::Square(DA.X/80)+FMath::Square(DA.Y/40),SB=FMath::Square(DB.X/80)+FMath::Square(DB.Y/40);
        return SA==SB ? A<B : SA<SB;
    });
    if (Eligible.IsEmpty()) {V.SelectedSourceId=0;return false;}
    const int32 Index=Eligible.Find(V.SelectedSourceId); V.SelectedSourceId=Eligible[(Index+1)%Eligible.Num()];bSceneEquipmentTargetLost=false;return true;
}
bool ADungeonGameMode::TryInteractEquipment()
{
    if(IsRunInstallGated())return false;
    auto& R = *EquipmentRuntime; auto& V = R.View;
    if (!V.Bound) return false;
    if (!CanBeginEquipmentAction()) {R.Fail(EDungeonEquipmentFailure::Busy,TEXT("现在无法拾取。"));return false;}
    if (V.NeedsSlotSelection) return false; // Opening E cannot confirm the layer.
    if (!V.SelectedSourceId) UpdateEquipmentTarget();
    const auto* Source=R.FindSource(V.SelectedSourceId);
    if (!Source) {R.Fail(EDungeonEquipmentFailure::NoTarget,TEXT("附近没有装备。"));return false;}
    const auto Admission=EquipmentSourceAdmission(*Source);
    if (Admission!=EDungeonEquipmentFailure::None) {R.Fail(Admission,TEXT("目标距离、落地或视线条件不满足。"));return false;}
    const auto Prepared=R.Inventory->PreparePickup(Source->SourceId);
    if (Prepared.Error==DungeonEquipmentInventory::EError::SelectionRequired)
    {
        V.NeedsSlotSelection=true;
        V.SelectionSlot=DungeonEquipmentStats::FindTemplate(Source->Item.ContentId)->Kind==DungeonEquipmentStats::EKind::Armor?2:V.ActiveSlot;
        R.Fail(EDungeonEquipmentFailure::SelectionRequired,TEXT("方向键选槽，Enter确认，Esc取消。"));return false;
    }
    if (!Prepared.Ok()) {R.Fail(EDungeonEquipmentFailure::InvalidSlot,TEXT("没有合法装备槽。"));return false;}
    return StartEquipmentPickup(Prepared.Plan.Slot);
}
bool ADungeonGameMode::ConfirmEquipmentSlot(int32 Slot, bool FreshPress)
{
    if(IsRunInstallGated())return false;
    if (!FreshPress || !EquipmentRuntime->View.NeedsSlotSelection) return false;
    return StartEquipmentPickup(Slot);
}
void ADungeonGameMode::CancelEquipmentSelection()
{
    if(IsRunInstallGated())return;
    EquipmentRuntime->View.NeedsSlotSelection=false; EquipmentRuntime->View.SelectionSlot=-1;
}
void ADungeonGameMode::CancelEquipmentAction()
{
    auto& R=*EquipmentRuntime;
    if (!R.View.Bound) return;
    R.View.Action.Active=false; CancelEquipmentSelection();
}
bool ADungeonGameMode::StartEquipmentPickup(int32 Slot)
{
    auto& R=*EquipmentRuntime;auto& V=R.View;
    if (!CanBeginEquipmentAction()) return false;
    const auto* Source=R.FindSource(V.SelectedSourceId);
    if (!Source || EquipmentSourceAdmission(*Source)!=EDungeonEquipmentFailure::None)
    {CancelEquipmentSelection();R.Fail(EDungeonEquipmentFailure::InvalidSource,TEXT("来源已失效。"));return false;}
    const auto Prepared=R.Inventory->PreparePickup(Source->SourceId,Slot);
    if (!Prepared.Ok()) {R.Fail(EDungeonEquipmentFailure::InvalidSlot,TEXT("所选槽位不适用。"));return false;}
    FVector2D DropPosition=FVector2D::ZeroVector;
    if (Prepared.Plan.ReplacedId && !FindEquipmentDropPoint(DropPosition))
    {R.Fail(EDungeonEquipmentFailure::NoDropPoint,TEXT("没有可放下旧装备的地面。"));return false;}
    auto NextCombat=PlayerFighter->Combat;auto NextActions=PlayerFighter->WeaponSkills;
    if (!NextCombat.Interrupt(DungeonContentCombat::EInterruptReason::ExclusiveAction)
        || !NextActions.Interrupt(DungeonWeaponActions::EInterrupt::ExclusiveAction)) return false;
    const bool Armor=Slot==2;
    V.Action={Armor?EDungeonEquipmentActionKind::PickupArmor:EDungeonEquipmentActionKind::PickupWeapon,true,
        V.NextEquipmentActionId++,V.NextOperationId,Source->SourceId,Source->InstanceId,Slot,SimulationTime,SimulationTime+(Armor?.50:.35)};
    R.PendingPlan=Prepared.Plan;R.PendingHasDrop=Prepared.Plan.ReplacedId!=0;R.PendingDropPosition=DropPosition;CancelEquipmentSelection();
    PlayerFighter->Combat=MoveTemp(NextCombat);PlayerFighter->WeaponSkills=MoveTemp(NextActions);
    ObservePendingActionAudio(PlayerFighter);
    PlayerFighter->ClearPendingAttackInput();PlayerFighter->AnimationName=Armor?TEXT("equip_armor"):TEXT("equip_weapon");PlayerFighter->AnimationTime=0;
    R.Fail(EDungeonEquipmentFailure::None,TEXT(""));return true;
}
bool ADungeonGameMode::TrySwitchEquipment()
{
    if(IsRunInstallGated())return false;
    auto& R=*EquipmentRuntime;auto& V=R.View;
    if (!CanBeginEquipmentAction(true)) return false;
    const auto Prepared=R.Inventory->PrepareSwitch();if (!Prepared.Ok()) return false;
    auto NextCombat=PlayerFighter->Combat;auto NextActions=PlayerFighter->WeaponSkills;
    if (!NextCombat.Interrupt(DungeonContentCombat::EInterruptReason::ExclusiveAction)
        || !NextActions.Interrupt(DungeonWeaponActions::EInterrupt::ExclusiveAction)) return false;
    V.Action={EDungeonEquipmentActionKind::SwitchWeapon,true,V.NextEquipmentActionId++,V.NextOperationId,0,
        Prepared.Plan.InstanceId,Prepared.Plan.Slot,SimulationTime,SimulationTime+.35};
    R.PendingPlan=Prepared.Plan;R.PendingHasDrop=false;CancelEquipmentSelection();
    PlayerFighter->Combat=MoveTemp(NextCombat);PlayerFighter->WeaponSkills=MoveTemp(NextActions);PlayerFighter->ClearPendingAttackInput();
    ObservePendingActionAudio(PlayerFighter);
    PlayerFighter->AnimationName=TEXT("equip_weapon");PlayerFighter->AnimationTime=0;
    R.Fail(EDungeonEquipmentFailure::None,TEXT(""));return true;
}

bool ADungeonGameMode::SyncEquipmentRuntime()
{
    auto& R=*EquipmentRuntime; if (!R.View.Bound || !IsValid(PlayerFighter)) return true;
    auto Candidate=*R.Inventory;
    for (const uint64 Id : Candidate.State().Weapons)
    {
        if (!Id) continue;
        const auto* Runtime=PlayerFighter->WeaponSkills.Instance(Id);
        const DungeonEquipmentInventory::FItem* Item=nullptr;
        for (const auto& I:Candidate.State().Items) if (I.InstanceId==Id) {Item=&I;break;}
        if (!Item || !Runtime) return false;
        if (Item->Ammo==Runtime->Ammo && Item->SkillCooldownDeadline==Runtime->CooldownDeadline) continue;
        const auto Result=Candidate.CommitResolvedWeaponRuntime(PlayerFighter->WeaponSkills.State().Time,Id,Item->Version,
            Runtime->Ammo,Runtime->CooldownDeadline,Candidate.State().NextRuntimeReceiptId);
        if (!Result.Ok()) return false;
    }
    *R.Inventory=MoveTemp(Candidate);R.RefreshView();
    R.View.NextImportReceiptId=PlayerFighter->WeaponSkills.State().NextImportReceiptId;
    UpdateEquipmentMirrors();return true;
}
void ADungeonGameMode::UpdateEquipmentMirrors()
{
    auto& V=EquipmentRuntime->View;if (!V.Bound || !IsValid(PlayerFighter)) return;
    PlayerFighter->WeaponId=V.Slots[V.ActiveSlot].ContentId;PlayerFighter->ArmorId=V.Slots[2].ContentId;
    PlayerFighter->Focus=float(PlayerFighter->WeaponSkills.State().Budget.Focus);
    V.Stats.CurrentHP=PlayerFighter->Health;
    PlayerFighter->SyncWeaponMuzzleTransform(SimulationTime);
}
bool ADungeonGameMode::FindEquipmentDropPoint(FVector2D& Position) const
{
    // Current room is a bounded flat floor. Loot is nonblocking and may overlap loot/actors.
    const FVector2D Offsets[]={{0,0},{24,0},{-24,0},{0,16},{0,-16},{24,16},{-24,-16}};
    const auto Origin=PlayerFighter->GetGroundPosition();
    for (const auto Offset:Offsets)
    {
        const auto P=Origin+Offset;
        if (!IsEquipmentDropPointLegal(P)) continue;
        Position=P;return true;
    }
    return false;
}
bool ADungeonGameMode::IsEquipmentDropPointLegal(FVector2D Position) const
{
    if (Position.X<DungeonRoomLayout::MinX || Position.X>DungeonRoomLayout::MaxX || Position.Y<DungeonRoomLayout::MinY || Position.Y>DungeonRoomLayout::MaxY) return false;
    const auto Origin=PlayerFighter->GetGroundPosition();
    FCollisionQueryParams Params(SCENE_QUERY_STAT(EquipmentDropPoint),false);Params.AddIgnoredActor(PlayerFighter);FHitResult Hit;
    if (GetWorld()->LineTraceSingleByObjectType(Hit,FVector(Origin.X,Origin.Y,0),FVector(Position.X,Position.Y,0),SkillWallObjects(),Params) && Hit.bBlockingHit) return false;
    return !GetWorld()->OverlapAnyTestByObjectType(FVector(Position.X,Position.Y,0),FQuat::Identity,SkillWallObjects(),FCollisionShape::MakeBox(FVector(1,1,.5)),Params);
}
void ADungeonGameMode::CommitEquipmentAction()
{
    namespace EquipInv=DungeonEquipmentInventory;
    auto& R=*EquipmentRuntime;auto& V=R.View;
    if (!V.Bound || !V.Action.Active || SimulationTime<V.Action.Deadline) return;
    const auto Action=V.Action;const auto BoundPlan=R.PendingPlan;
    const auto Reject=[this,&R](EDungeonEquipmentFailure Failure,const TCHAR* Text)
    {CancelEquipmentAction();R.Fail(Failure,Text);};
    if (!IsValid(PlayerFighter) || PlayerFighter->bDead || bGameOver || PlayerFighter->HurtTime>0
        || PlayerFighter->JumpHeight>0 || PlayerFighter->JumpVelocity>0 || !PlayerFighter->ReadMoveIntent().IsNearlyZero())
    {Reject(EDungeonEquipmentFailure::Busy,TEXT("动作条件已改变。"));return;}
    if (Action.Kind!=EDungeonEquipmentActionKind::SwitchWeapon)
    {
        const auto* Source=R.FindSource(Action.SourceId);
        if (!Source || EquipmentSourceAdmission(*Source)!=EDungeonEquipmentFailure::None)
        {Reject(EDungeonEquipmentFailure::InvalidSource,TEXT("来源已失效。"));return;}
    }
    auto NextInventory=*R.Inventory;
    const auto Prepared=Action.Kind==EDungeonEquipmentActionKind::SwitchWeapon
        ? NextInventory.PrepareSwitch() : NextInventory.PreparePickup(Action.SourceId,Action.Slot);
    if (!Prepared.Ok() || Prepared.Plan.InstanceId!=BoundPlan.InstanceId || Prepared.Plan.InstanceVersion!=BoundPlan.InstanceVersion
        || Prepared.Plan.SourceVersion!=BoundPlan.SourceVersion || Prepared.Plan.ReplacedId!=BoundPlan.ReplacedId || Prepared.Plan.Slot!=BoundPlan.Slot)
    {Reject(EDungeonEquipmentFailure::StaleState,TEXT("来源或装备版本已改变。"));return;}
    const FVector2D DropPosition=R.PendingDropPosition;
    if (Prepared.Plan.ReplacedId && (!R.PendingHasDrop || !IsEquipmentDropPointLegal(DropPosition)
        || !V.NextSourceId || V.NextSourceId==TNumericLimits<uint64>::Max()))
    {Reject(EDungeonEquipmentFailure::NoDropPoint,TEXT("没有可放下旧装备的地面。"));return;}
    const uint64 DropSource=Prepared.Plan.ReplacedId?V.NextSourceId:0;
    const auto Result=NextInventory.Commit(Action.OperationId,Prepared.Plan,{true,true},DropSource);
    if (!Result.Ok()) {Reject(EDungeonEquipmentFailure::InternalConsistency,TEXT("装备事务被拒绝。"));return;}
    auto NextActions=PlayerFighter->WeaponSkills;auto NextCombat=PlayerFighter->Combat;
    const auto FindNext=[&NextInventory](uint64 Id)->const EquipInv::FItem*
    {for (const auto& I:NextInventory.State().Items) if (I.InstanceId==Id) return &I;return nullptr;};
    const auto WeaponEnum=[](const std::string& Id)
    {
        for (int32 I=0;I<5;++I) if (Id==DungeonContentCombat::GetWeaponDefinition(DungeonContentCombat::EWeapon(I))->ContentId) return DungeonContentCombat::EWeapon(I);
        return DungeonContentCombat::EWeapon::SWD001;
    };
    for (const uint64 Id:NextInventory.State().Weapons)
    {
        const auto* Item=FindNext(Id);if (!Item) continue;
        if (!NextActions.Instance(Id))
        {
            const auto Imported=NextActions.ImportResolvedWeapon(SimulationTime,{WeaponEnum(Item->ContentId),Id,Item->Ammo,0,Item->SkillCooldownDeadline},NextActions.State().NextImportReceiptId);
            if (!Imported.Accepted) {Reject(EDungeonEquipmentFailure::InternalConsistency,TEXT("武器实例导入失败。"));return;}
        }
        else if (NextActions.Instance(Id)->Ammo!=Item->Ammo || NextActions.Instance(Id)->CooldownDeadline!=Item->SkillCooldownDeadline)
        {Reject(EDungeonEquipmentFailure::StaleState,TEXT("武器运行数据不一致。"));return;}
    }
    const auto* Active=FindNext(NextInventory.State().Weapons[NextInventory.State().ActiveSlot]);
    const auto Stats=NextInventory.ResolveStats({},PlayerFighter->Health);
    if (!Active || !Stats.Ok() || !NextActions.EquipCompleted(Active->InstanceId)
        || ((NextCombat.State().WeaponInstanceId!=Active->InstanceId || NextCombat.State().Weapon!=WeaponEnum(Active->ContentId))
            && !NextCombat.ChangeWeapon(WeaponEnum(Active->ContentId),Active->InstanceId)))
    {Reject(EDungeonEquipmentFailure::InternalConsistency,TEXT("最终装备属性无效。"));return;}
    // Install all candidates together, after this boundary's accepted damage and old-rate regen.
    *R.Inventory=MoveTemp(NextInventory);PlayerFighter->WeaponSkills=MoveTemp(NextActions);PlayerFighter->Combat=MoveTemp(NextCombat);
    if (Result.DroppedId)
    {
        const auto* Old=R.FindItem(Result.DroppedId);
        R.Sources.Add({DropSource,Result.DroppedId,1,V.RoomInstanceId,FString::Printf(TEXT("equipment.operation.%llu.drop"),Action.OperationId),DropPosition,true,false,*Old});
        ++V.NextSourceId;
    }
    ++V.NextOperationId;V.NextImportReceiptId=PlayerFighter->WeaponSkills.State().NextImportReceiptId;
    V.Stats=Stats;PlayerFighter->MaxHealth=float(Stats.MaxHP);PlayerFighter->Health=float(Stats.CurrentHP);
    V.Action.Active=false;V.SelectedSourceId=0;bSceneEquipmentTargetLost=false;CancelEquipmentSelection();R.RefreshView();UpdateEquipmentMirrors();UpdateEquipmentTarget();
    R.Fail(EDungeonEquipmentFailure::None,TEXT(""));
    if(Action.Kind==EDungeonEquipmentActionKind::PickupArmor&&!Result.Replayed
        &&Action.Slot==2&&R.Inventory->State().Armor==Action.InstanceId)
    {
        const auto* Item=R.FindItem(Action.InstanceId);
        if(Item&&PlayerFighter->ArmorId==UTF8_TO_TCHAR(Item->ContentId.c_str()))
        {
            const TCHAR* Cue=Item->ContentId=="ARM-LGT-001"||Item->ContentId=="ARM-ROB-001"?TEXT("EQUIP_ARMOR_CLOTH_01")
                :Item->ContentId=="ARM-MED-001"||Item->ContentId=="ARM-HVY-001"?TEXT("EQUIP_ARMOR_METAL_01"):nullptr;
            if(Cue)AppendActionAudio(Cue,SimulationTime,V.OwnerId,Action.ActionId,Action.InstanceId,Action.OperationId,Result.Revision);
        }
    }
    if (PlayerFighter->PoiseProtection<=0 && PlayerFighter->PoiseAccumulation>=Stats.Poise)
    {
        PlayerFighter->PoiseAccumulation=0;PlayerFighter->PoiseProtection=1;PlayerFighter->HurtTime=.4f;
        PlayerFighter->Combat.Interrupt(DungeonContentCombat::EInterruptReason::PoiseBreak);
        PlayerFighter->WeaponSkills.Interrupt(DungeonWeaponActions::EInterrupt::PoiseBreak);
        ObservePendingActionAudio(PlayerFighter);
    }
}

void ADungeonGameMode::StartPlay()
{
    Super::StartPlay();
    // Native Actor BeginPlay still runs. This opt-in origin never constructs a
    // starter Run, including a failed/contaminated startup or a repeated call.
    if(bPristineContinueOrigin)return;
    bFairytaleLookdevPreview=FParse::Param(FCommandLine::Get(),TEXT("DungeonFairytaleLookdevPreview"));
    if(bFairytaleLookdevPreview)
    {
        RestartRun();bWaitingForStart=true;FairytaleLookdevEpoch=FPlatformTime::Seconds();
        if(PlayerFighter)PlayerFighter->SetActorTickEnabled(false);
        for(auto Enemy:Enemies)if(IsValid(Enemy)){Enemy->SetActorTickEnabled(false);Enemy->bAIEnabled=false;}
        return;
    }
    RestartRun();
    bWaitingForStart = FParse::Param(FCommandLine::Get(),TEXT("DungeonManualWeaponPreview"))
        || FParse::Param(FCommandLine::Get(),TEXT("DungeonSceneExplorationPreview"))
        || (!FParse::Param(FCommandLine::Get(),TEXT("DungeonProof"))
        && !FParse::Param(FCommandLine::Get(),TEXT("DungeonContentProof")));
}

ADungeonFighter* ADungeonGameMode::GetPlayerFighter() const
{
    return PlayerFighter;
}

ADungeonFighter* ADungeonGameMode::SpawnStoneBat(FVector2D GroundPosition)
{
    if(IsRunInstallGated())return nullptr;
    if(!EquipmentRuntime->View.Bound||!IsValid(PlayerFighter)||bGameOver||!FMath::IsFinite(GroundPosition.X)||!FMath::IsFinite(GroundPosition.Y)
        ||!DungeonRoomLayout::CenterBounds().IsInsideOrOn(GroundPosition))return nullptr;
    auto Bat=GetWorld()->SpawnActor<ADungeonFighter>();if(!Bat)return nullptr;
    Bat->bEnemy=true;Bat->bAIEnabled=false;Bat->EnemyContentId=TEXT("ENM-STN-002");Bat->ResetFighter(GroundPosition);
    Enemies.Add(Bat);AdmitWorldFighters();
    const uint64 Id=FindWorldEntityId(Bat);
    if(!Id||!Bat->InitializeStoneBat(Id,SimulationTime))
    {
        Enemies.Remove(Bat);WorldEntityIds.Remove(Bat);
        WeaponWorld.ActorBindings.RemoveAll([Id](const FDungeonWorldActorBinding& B){return B.EntityId==Id;});
        Bat->Destroy();return nullptr;
    }
    return Bat;
}

TArray<FDungeonKnightBody> ADungeonGameMode::CaptureKnightBodies() const
{
    TArray<FDungeonKnightBody> Bodies;
    const auto Capture = [this,&Bodies](ADungeonFighter* Fighter)
    {
        if (!IsValid(Fighter)||!Fighter->GetRuntimeEntityId()) return;
        FDungeonKnightBody B;
        B.Fighter = Fighter; B.EntityId = Fighter->GetRuntimeEntityId();
        B.Start = B.End = Fighter->GetGroundPosition();
        B.StartHeight = B.EndHeight = Fighter->GetCombatHeight();
        B.BodyHalfExtent = Fighter->GetCombatBodyHalfExtent();
        B.bBlocksBody = !Fighter->StoneBat || B.StartHeight<=40.;
        B.bAlive = !Fighter->bDead;
        B.bCanTakeDamage = Fighter->CanReceiveDirectHit();
        B.bUseTimedDamageAdmission=true;
        if (Fighter->InvulnerableTime>0.f)
            B.DirectInvulnerabilityIntervals.Add({SimulationTime,SimulationTime+double(Fighter->InvulnerableTime)});
        for (const auto& I:Fighter->Dodge.DirectInvulnerabilityIntervals())
            B.DirectInvulnerabilityIntervals.Add({I.Start,I.EndExclusive});
        Bodies.Add(B);
    };
    Capture(PlayerFighter);
    for (ADungeonFighter* Enemy : Enemies) Capture(Enemy);
    return Bodies;
}

FDungeonKnightFrame ADungeonGameMode::MakeKnightFrame(ADungeonFighter* Knight, double FromTime, double ToTime,
    const TArray<FDungeonKnightBody>& Bodies) const
{
    FDungeonKnightFrame Frame;
    Frame.FromTime = FromTime; Frame.ToTime = ToTime;
    Frame.Target = PlayerFighter;
    Frame.CenterBounds = DungeonRoomLayout::CenterBounds();
    Frame.Bodies = Bodies;
    for (auto& B : Frame.Bodies)
        B.bSameTeam = B.Fighter.IsValid() && B.Fighter->bEnemy == Knight->bEnemy;
    Frame.bCanStartAttack = !bGameOver && !bWaitingForStart && Knight->bAIEnabled;
    // One whole-room wake warning may begin per second, including real-damage triggers.
    Frame.bCanBeginWake = LastStoneWakeStartedAt < 0.0 || FromTime >= LastStoneWakeStartedAt+1.0;
    return Frame;
}

FDungeonKnightFrame ADungeonGameMode::MakeKnightDamageFrame(ADungeonFighter* Knight) const
{
    const double Now = Knight->StoneKnight->State().Time;
    return MakeKnightFrame(Knight, Now, Now, CaptureKnightBodies());
}

void ADungeonGameMode::AcceptKnightBatch(ADungeonFighter* Knight, const FDungeonKnightBatch& Batch)
{
    if (!Batch.Accepted) return;
    // Both StepTo and ApplyResolvedHit arrive here. Record the real post-batch
    // kernel position, before actor mirroring; feedback has no authority side effects.
    ensureMsgf(Knight->StoneFeedback.Observe(Batch.Events, Knight->StoneKnight->State().Position),
        TEXT("Stone feedback rejected an inconsistent real kernel event batch."));
    for (const auto& Event : Batch.Events)
        if (Event.Kind == DungeonStoneKnight::EEventKind::WakeStarted)
            LastStoneWakeStartedAt = Event.AtTime;
    // Driver queries have already admitted and deduplicated each hit against this batch's
    // old invulnerability. Only the normal PendingDamage commit may change actor HP.
    for (const auto& Hit : Batch.Hits)
        if (bSimulationBatch && Hit.Target.IsValid())
            PendingDamage.Add({Knight, Hit.Target.Get(), float(Hit.Damage), float(Hit.Stagger),Hit.AtTime});
}

void ADungeonGameMode::AcceptBatBatch(ADungeonFighter* Bat,const FDungeonBatBatch& Batch)
{
    if(!Batch.Accepted)return;
    for(const auto& E:Batch.Events)if(E.Kind==DungeonStoneBat::EEventKind::WakeStarted)LastStoneWakeStartedAt=E.AtTime;
    for(const auto& H:Batch.Hits)if(bSimulationBatch&&H.Target.IsValid())PendingDamage.Add({Bat,H.Target.Get(),float(H.Damage),float(H.Stagger),H.AtTime});
}

FVector2D ADungeonGameMode::SkillPositionAt(ADungeonFighter* Fighter, double AtTime) const
{
    FVector2D P = Fighter->GetGroundPosition();
    for (const auto& B : SkillBatchBodies)
        if (B.Fighter.Get() == Fighter)
        {
            P = ObservedPosition(B,SkillBatchFrom,SkillBatchTo,AtTime); break;
        }
    if (Fighter->BatchSkillStepAt >= 0.0 && AtTime >= Fighter->BatchSkillStepAt) P += Fighter->BatchSkillStepDelta;
    return P;
}

DungeonDodge::FSweepResult ADungeonGameMode::QueryResolvedMovement(ADungeonFighter* Fighter,FVector2D From,FVector2D To,
    double FromTime,double ToTime,const TArray<FDungeonKnightBody>& Bodies) const
{
    DungeonDodge::FSweepResult R;
    if (!IsValid(Fighter) || !FMath::IsFinite(From.X)||!FMath::IsFinite(From.Y)||!FMath::IsFinite(To.X)||!FMath::IsFinite(To.Y)
        ||!FMath::IsFinite(FromTime)||!FMath::IsFinite(ToTime)||ToTime<FromTime) { R.Accepted=false; return R; }
    const FVector2D D=To-From;
    const auto ReceiverPosition=[Fighter,From,To,ToTime](double Fraction)
    {
        const auto& State=Fighter->Dodge.State();
        if (State.Phase==DungeonDodge::EPhase::Dodging && !State.Records.empty()
            && State.Records.back().Block==DungeonDodge::EBlock::None)
        {
            const auto& Record=State.Records.back();
            const double MoveEnd=FMath::Min(ToTime,Record.End);
            const double TargetTravel=MoveEnd>=Record.End?DungeonDodge::Distance
                :FMath::Clamp((MoveEnd-Record.Start)*DungeonDodge::Speed,0.0,DungeonDodge::Distance);
            const double Travel=Fraction==1.0?TargetTravel:Record.Travelled+(TargetTravel-Record.Travelled)*Fraction;
            // FDodgeKernel stores this cumulative-travel reconstruction, not Q.Lerp.
            return FVector2D(Record.Origin.X+Record.Direction.X*Travel,Record.Origin.Y+Record.Direction.Y*Travel);
        }
        return FMath::Lerp(From,To,Fraction);
    };
    const auto Wall=[&R](double A){R.HitWall=true;R.WallFraction=FMath::Min(R.WallFraction,FMath::Clamp(A,0.0,1.0));};
    const auto Bounds=DungeonRoomLayout::CenterBounds();
    if (!Bounds.IsInsideOrOn(From)) Wall(0.0);
    if (To.X<Bounds.Min.X&&D.X<0) Wall((Bounds.Min.X-From.X)/D.X);
    if (To.X>Bounds.Max.X&&D.X>0) Wall((Bounds.Max.X-From.X)/D.X);
    if (To.Y<Bounds.Min.Y&&D.Y<0) Wall((Bounds.Min.Y-From.Y)/D.Y);
    if (To.Y>Bounds.Max.Y&&D.Y>0) Wall((Bounds.Max.Y-From.Y)/D.Y);
    if (!D.IsNearlyZero(1.e-12))
    {
        FCollisionQueryParams Params(SCENE_QUERY_STAT(DungeonResolvedMovement),false); Params.AddIgnoredActor(Fighter);
        TArray<FHitResult> Hits;
        GetWorld()->SweepMultiByObjectType(Hits,FVector(From.X,From.Y,0),FVector(To.X,To.Y,0),FQuat::Identity,
            SkillWallObjects(),FCollisionShape::MakeBox(FVector(18.0,16.0,1.0)),Params);
        for (const auto& H:Hits) if (H.bBlockingHit && FMath::Abs(H.ImpactNormal.Z)<.5
            &&!LeavesNativeZeroDepthBoxFace(H,D)) Wall(H.Time);
    }
    double FirstBodyRawFraction=1.0;
    for (const auto& B:Bodies)
    {
        if (!B.bAlive||!B.bBlocksBody||!B.Fighter.IsValid()||B.Fighter.Get()==Fighter) continue;
        const auto Extent=B.BodyHalfExtent+FVector2D(18,16);
        const auto P0=ObservedPosition(B,FromTime,ToTime,FromTime)-From;
        const auto P1=ObservedPosition(B,FromTime,ToTime,ToTime)-To;
        double Entry=0,Exit=1;
        if(B.Fighter->StoneBat&&!SkillClip(B.StartHeight,B.EndHeight,0.,40.,Entry,Exit))continue;
        const double HeightAdmission=Entry;
        if (!SkillClip(P0.X,P1.X,-Extent.X,Extent.X,Entry,Exit)||!SkillClip(P0.Y,P1.Y,-Extent.Y,Extent.Y,Entry,Exit)) continue;
        if (Entry==0.0 && FMath::Abs(P0.X)<Extent.X && FMath::Abs(P0.Y)<Extent.Y)
        {
            // A pre-existing overlap may recover along/away from its nearest face.
            // Test signed relative motion, so crossing through the opposite face is
            // never mistaken for separation. No contact/depth tolerance is widened.
            const auto Motion=P1-P0;
            const bool NearestX=Extent.X-FMath::Abs(P0.X)<=Extent.Y-FMath::Abs(P0.Y);
            if (NearestX ? P0.X*Motion.X>=0.0 : P0.Y*Motion.Y>=0.0) continue;
        }
        else if (Entry==0.0)
        {
            const auto Inside=FMath::Lerp(P0,P1,FMath::Min(Exit*.5,1.e-6));
            if (Exit<=0||!(FMath::Abs(Inside.X)<Extent.X&&FMath::Abs(Inside.Y)<Extent.Y)) continue;
        }
        const auto RelativeAt=[&B,FromTime,ToTime,&ReceiverPosition](double Fraction)
            {
                const double At=Fraction==1.0?ToTime:FromTime+(ToTime-FromTime)*Fraction;
                return ObservedPosition(B,FromTime,ToTime,At)-ReceiverPosition(Fraction);
            };
        const double SafeFraction=DungeonContactGeometry::ConservativeBodyFraction(HeightAdmission,Entry,RelativeAt(HeightAdmission),P1,Extent,RelativeAt);
        if (!R.HitBody || Entry<FirstBodyRawFraction)
        {R.HitBody=true;FirstBodyRawFraction=Entry;R.BodyFraction=SafeFraction;}
        else if (Entry==FirstBodyRawFraction) R.BodyFraction=FMath::Min(R.BodyFraction,SafeFraction);
    }
    // Dodge's wall-before-body tie remains based on the unrounded contacts.
    if (R.HitWall && R.HitBody && R.WallFraction<=FirstBodyRawFraction)
    {R.HitBody=false;R.BodyFraction=1.0;}
    return R;
}

TArray<FDungeonKnightBody> ADungeonGameMode::PredictMotionBodies(double FromTime,double ToTime) const
{
    auto Bodies=CaptureKnightBodies();
    const double Dt=ToTime-FromTime;
    for (auto& B:Bodies) if (auto A=B.Fighter.Get())
    {
        B.End=A->PredictGroundPosition(Dt);
        if (!A->StoneKnight && !A->StoneBat && !A->StoneGuard && (A->JumpHeight>0.f||A->JumpVelocity>0.f))
            B.EndHeight=double(float(FMath::Max(0.0,double(A->JumpHeight)+double(A->JumpVelocity)*Dt-900.0*Dt*Dt)));
        if (A->Dodge.State().Phase==DungeonDodge::EPhase::Dodging)
        {
            auto Preview=A->Dodge;
            Preview.StepTo(ToTime);
            B.End={Preview.State().Position.X,Preview.State().Position.Y};
        }
    }
    // Predict knight motion with a throwaway driver, never journal/HP/actor effects.
    for (auto& B:Bodies) if (auto A=B.Fighter.Get()) if (A->StoneKnight && !A->bDead)
    {
        auto Preview=*A->StoneKnight;
        if (Preview.StepTo(ToTime,MakeKnightFrame(A,FromTime,ToTime,Bodies)).Accepted)
            B.End={Preview.State().Position.X,Preview.State().Position.Y};
    }
    for(auto& B:Bodies)if(auto A=B.Fighter.Get())if(A->StoneBat&&!A->bDead)
    {
        auto Preview=*A->StoneBat;const auto Batch=Preview.StepTo(ToTime,MakeKnightFrame(A,FromTime,ToTime,Bodies));
        if(Batch.Accepted){const auto& P=Preview.State().Position;B.End={P.X,P.Y};B.EndHeight=P.Z;B.MotionSegments=Batch.MotionSegments;
            // This batch is split at every actual Z40 crossing before ordinary movement is admitted.
            B.bBlocksBody=B.StartHeight<=40.||B.EndHeight<=40.;}
    }
    for(auto& B:Bodies)if(auto A=B.Fighter.Get())if(A->StoneGuard&&!A->bDead)
    {
        auto Preview=*A->StoneGuard;const auto Batch=Preview.StepTo(ToTime,MakeKnightFrame(A,FromTime,ToTime,Bodies));
        if(Batch.Accepted){const auto& P=Preview.State().Position;B.End={P.X,P.Y};B.EndHeight=P.Z;B.MotionSegments=Batch.MotionSegments;}
    }
    const auto Unresolved=Bodies;
    for (auto& B:Bodies) if (auto A=B.Fighter.Get())
    {
        if (A->StoneKnight || A->StoneBat || A->StoneGuard) continue;
        if (A->Dodge.State().Phase==DungeonDodge::EPhase::Dodging)
        {
            auto Preview=A->Dodge;
            const auto R=Preview.StepTo(ToTime,[this,A,&Unresolved](const DungeonDodge::FSweepRequest& Q)
            {return QueryResolvedMovement(A,{Q.From.X,Q.From.Y},{Q.To.X,Q.To.Y},Q.FromTime,Q.ToTime,Unresolved);});
            if (!R.Accepted) continue;
            B.End={Preview.State().Position.X,Preview.State().Position.Y};
            const auto& Record=Preview.State().Records.back();
            if (Record.BlockedAt>FromTime && Record.BlockedAt<ToTime)
            {
                B.MotionSegments.Add({FromTime,Record.BlockedAt,B.Start,B.End,B.StartHeight,B.EndHeight,false});
                B.MotionSegments.Add({Record.BlockedAt,ToTime,B.End,B.End,B.EndHeight,B.EndHeight,false});
            }
        }
        else
        {
            const auto R=QueryResolvedMovement(A,B.Start,B.End,FromTime,ToTime,Unresolved);
            const double Fraction=FMath::Min(R.HitWall?R.WallFraction:1.0,R.HitBody?R.BodyFraction:1.0);
            B.End=FMath::Lerp(B.Start,B.End,Fraction);
        }
    }
    return Bodies;
}

double ADungeonGameMode::NextSimulationBoundary(double Limit) const
{
    const double From=SimulationTime;
    if(bSceneCommitRequested)return From;
    const auto Bound=[From,&Limit](double At){if (At>From) Limit=FMath::Min(Limit,At);};
    const auto FighterBoundary=[&Bound,From](ADungeonFighter* F)
    {
        if (!IsValid(F)||F->bDead) return;
        if (F->InvulnerableTime>0.f) Bound(From+double(F->InvulnerableTime));
        if (F->HurtTime>0.f) Bound(From+double(F->HurtTime));
        if (F->ArmorChangeRemaining>0.f) Bound(From+double(F->ArmorChangeRemaining));
        const auto& A=F->Combat.State().Action;
        if (A.Active) {Bound(A.LockTime);Bound(A.ActiveStart);Bound(A.ActiveEnd);Bound(A.End);}
        const auto& W=F->WeaponSkills.State().Action;
        if (W.Active)
        {
            Bound(W.LockAt);Bound(W.ActiveAt);Bound(W.ActiveEnd);Bound(W.End);
            if (W.Type==DungeonWeaponActions::EAction::Skill)
            {
                const auto& Skill=DungeonContentCombat::GetWeaponDefinition(W.Weapon)->Skill;
                for (uint32 N=0;N<Skill.SubhitCount;++N)
                {const double At=W.Start+Skill.SubhitTimes[N]/(1+W.SpeedPct/100.);Bound(At);Bound(At+Skill.SubhitDurations[N]/(1+W.SpeedPct/100.));}
            }
        }
        if (F->Dodge.State().Phase==DungeonDodge::EPhase::Dodging)
        {
            const auto& D=F->Dodge.State().Records.back();Bound(D.Start+.06);Bound(D.Start+.20);Bound(D.End);
        }
        if (F->StoneKnight)
        {
            const auto& S=F->StoneKnight->State();
            if (S.Phase==DungeonStoneKnight::EPhase::Waking) Bound(S.WakeEnd);
            if (S.Phase==DungeonStoneKnight::EPhase::Stunned) Bound(S.StunUntil);
            if (S.Action.InProgress) {Bound(S.Action.LockAt);Bound(S.Action.ActiveAt);Bound(S.Action.ActiveEnd);Bound(S.Action.RecoveryEnd);}
        }
        if(F->StoneGuard)
        {
            using GP=DungeonStoneGuard::EPhase;const auto& S=F->StoneGuard->State();const auto& GuardAction=S.Action;
            if(!S.Awakened&&S.WakeStartedAt>=0.)Bound(S.WakeEnd);
            if(S.Phase==GP::Dormant&&S.CombatStartedAt>=0.)Bound(S.CombatStartedAt+12.);
            if(S.Phase==GP::Stunned)Bound(S.StunUntil);
            if(S.Phase==GP::Idle){Bound(S.IdleReadyAt);Bound(S.AxeReadyAt);Bound(S.StompReadyAt);}
            if(S.Phase==GP::Windup){Bound(GuardAction.LockAt);Bound(GuardAction.ActiveAt);}if(S.Phase==GP::Active)Bound(GuardAction.ActiveEnd);
            if(S.Phase==GP::Recovery||(GuardAction.Interrupted&&GuardAction.CompletedAt<0.))Bound(S.OccupiedUntil);
        }
        if(F->StoneBat)
        {
            using BP=DungeonStoneBat::EPhase;using BA=DungeonStoneBat::EAttack;const auto& S=F->StoneBat->State();const auto& BatAction=S.Action;
            if(!S.Awakened&&S.WakeStartedAt>=0.)Bound(S.WakeEnd);if(S.Phase==BP::Dormant&&S.CombatStartedAt>=0.)Bound(S.CombatStartedAt+12.);
            if(S.Phase==BP::HighIdle&&S.HighIdleEligibleSince>=0.)Bound(S.HighIdleEligibleSince+2.4);
            if(S.Phase==BP::Stunned)Bound(S.StunUntil);if(S.PendingLow&&S.LowStartedAt>=0.)Bound(S.LowReadyAt);
            if(S.Phase==BP::Windup){Bound(BatAction.LockAt);Bound(BatAction.ActiveAt);}if(S.Phase==BP::Active||S.Phase==BP::SeekingLow)Bound(BatAction.ActiveEnd);
            const auto Heights=[&Bound](DungeonStoneBat::FPoint P,DungeonStoneBat::FPoint Q,double Begin,double End)
            {if(P.Z!=Q.Z)for(double Z:{65.,40.,20.,90.})if(Z>=FMath::Min(P.Z,Q.Z)&&Z<=FMath::Max(P.Z,Q.Z))Bound(Begin+(End-Begin)*(Z-P.Z)/(Q.Z-P.Z));};
            if(S.Phase==BP::Active&&BatAction.Kind==BA::Peck&&!BatAction.PathBlocked)Heights(BatAction.Origin,BatAction.Endpoint,BatAction.ActiveAt,BatAction.ActiveEnd);
            if(S.Phase==BP::Windup&&BatAction.Locked&&BatAction.Kind==BA::Wing&&!BatAction.PathBlocked)Heights(BatAction.Origin,BatAction.Endpoint,BatAction.LockAt,BatAction.ActiveAt);
            if(S.Phase==BP::Rising){auto Q=S.RiseOrigin;Q.Z=90.;const double End=S.RiseStartedAt+(90.-S.RiseOrigin.Z)/(70./.3);Bound(End);Heights(S.RiseOrigin,Q,S.RiseStartedAt,End);}
        }
        if (!F->IsEquipmentBound()&&!F->IsContentMelee()&&!F->StoneKnight&&!F->StoneBat&&!F->StoneGuard&&F->AttackTime>0&&!F->bAttackResolved)
            Bound(From+FMath::Max(0.0,double((F->bEnemy?.46f:F->WeaponId==TEXT("axe")?.31f:.17f)-F->AttackElapsed)));
    };
    FighterBoundary(PlayerFighter);
    if(LastStoneWakeStartedAt>=0.)Bound(LastStoneWakeStartedAt+1.);
    for (ADungeonFighter* Enemy:Enemies) FighterBoundary(Enemy);
    if (EquipmentRuntime->View.Bound && EquipmentRuntime->View.Action.Active) Bound(EquipmentRuntime->View.Action.Deadline);
    for (const auto& B:WeaponWorld.Burns) if (B.Active) {Bound(B.NextTickAt);Bound(B.ExpiresAt);}
    if (IsValid(PlayerFighter)&&(PlayerFighter->JumpHeight>0||PlayerFighter->JumpVelocity>0))
    {
        const double V=PlayerFighter->JumpVelocity,H=PlayerFighter->JumpHeight;
        Bound(From+(V+FMath::Sqrt(V*V+3600.0*H))/1800.0);
    }
    return Limit;
}

double ADungeonGameMode::EarliestContact(double ToTime,const TArray<FDungeonKnightBody>& Bodies)
{
    double Earliest=ToTime;
    for(ADungeonFighter* E:Enemies)if(IsValid(E)&&E->StoneGuard&&!E->bDead)
    {
        auto Preview=*E->StoneGuard;const auto Batch=Preview.StepTo(ToTime,MakeKnightFrame(E,SimulationTime,ToTime,Bodies));
        if(Batch.Accepted)
        {
            for(const auto& H:Batch.Hits)Earliest=FMath::Min(Earliest,H.AtTime);
            for(const auto& Event:Batch.Events)if(Event.AtTime>SimulationTime)Earliest=FMath::Min(Earliest,Event.AtTime);
        }
    }

    for(ADungeonFighter* E:Enemies)if(IsValid(E)&&E->StoneBat&&!E->bDead)
    {
        auto Preview=*E->StoneBat;const auto Batch=Preview.StepTo(ToTime,MakeKnightFrame(E,SimulationTime,ToTime,Bodies));
        if(Batch.Accepted){for(const auto& H:Batch.Hits)Earliest=FMath::Min(Earliest,H.AtTime);
            for(const auto& Event:Batch.Events)if(Event.AtTime>SimulationTime)Earliest=FMath::Min(Earliest,Event.AtTime);}
    }
    for (ADungeonFighter* E:Enemies) if (IsValid(E)&&E->StoneKnight&&!E->bDead)
    {
        auto Preview=*E->StoneKnight;
        const auto Batch=Preview.StepTo(ToTime,MakeKnightFrame(E,SimulationTime,ToTime,Bodies));
        if (Batch.Accepted) for (const auto& H:Batch.Hits) Earliest=FMath::Min(Earliest,H.AtTime);
    }
    if (IsValid(PlayerFighter))
    {
        const auto OldBodies=SkillBatchBodies;const double OldFrom=SkillBatchFrom,OldTo=SkillBatchTo;
        SkillBatchBodies=Bodies;SkillBatchFrom=SimulationTime;SkillBatchTo=ToTime;
        const auto PreviewWindow=[this,&Earliest](const DungeonWeaponActions::FEvent& W)
        {
            for (ADungeonFighter* Target:Enemies)
            {double At=0;if (FindWeaponSkillContact(PlayerFighter,Target,W,At)) Earliest=FMath::Min(Earliest,At);}
        };
        if (EquipmentRuntime->View.Bound)
        {
            for (const auto& W:WeaponWorld.Windows) if (W.Active&&W.Key.RoomInstanceId==WeaponWorld.RoomInstanceId) PreviewWindow(W.Source);
            for (const auto& P:WeaponWorld.Projectiles) if (P.Active)
            {
                auto ProjectileOwner=FindWorldFighter(P.Key.OwnerId);
                const auto Hit=DungeonWorldProjectiles::QueryContact(P,SimulationTime,ToTime,Bodies,WeaponWorld.HitReceipts,ProjectileOwner,GetWorld(),
                    [this,&P](const FDungeonKnightBody& B,double At){return WorldDamageAdmission(B,At,P.Key);});
                if (Hit.Found) Earliest=FMath::Min(Earliest,Hit.AtTime);
            }
        }
        else for (const auto& W:PlayerFighter->SkillWindows) PreviewWindow(W);
        SkillBatchBodies=OldBodies;SkillBatchFrom=OldFrom;SkillBatchTo=OldTo;
    }
    return FMath::Max(SimulationTime,Earliest);
}

void ADungeonGameMode::CommitPendingDamage()
{
    PendingDamage.StableSort([](const FPendingDamage& A,const FPendingDamage& B){return A.AtTime<B.AtTime;});
    const auto Accepted=MoveTemp(PendingDamage); PendingDamage.Reset();
    TArray<FPendingDamage> BurnApplications;
    TArray<double> BatLoss;BatLoss.Init(0.,Accepted.Num());TSet<ADungeonFighter*> BatTargets;
    // All accepted same-point losses enter one pure batch before a new bat window.
    for(int32 I=0;I<Accepted.Num();++I)
    {
        auto Bat=Accepted[I].Target;if(!IsValid(Bat)||!Bat->StoneBat||Bat->bDead||BatTargets.Contains(Bat))continue;BatTargets.Add(Bat);
        std::vector<DungeonStoneBat::FIncomingHit> Hits;uint64 Receipt=Bat->StoneBat->State().LastDamageReceiptId;double Remaining=Bat->StoneBat->State().HP;
        for(int32 J=I;J<Accepted.Num();++J)if(Accepted[J].Target==Bat)
        {
            const auto& H=Accepted[J];if(!FMath::IsFinite(H.Damage)||H.Damage<=0.f)continue;
            const float Rating=FMath::Max(0.f,Bat->GetArmorRating(H.Magic));const float Actual=H.Damage*(1.f-FMath::Min(.6f,Rating/(100.f+Rating)));
            const float Stagger=H.DamageOverTime?0.f:H.Stagger>=0.f?H.Stagger:H.Attacker?H.Attacker->GetAttackStagger():13.f;
            if(!FMath::IsFinite(Stagger)||Stagger<0.f)continue;const double Loss=FMath::Min(Remaining,double(Actual));Remaining-=Loss;BatLoss[J]=Loss;
            Hits.push_back({++Receipt,H.AtTime,Loss,Stagger});
        }
        const auto Frame=MakeKnightFrame(Bat,Bat->StoneBat->State().Time,SimulationTime,SkillBatchBodies);
        const auto Batch=Bat->StoneBat->StepTo(SimulationTime,Frame,Hits);
        ensureMsgf(Batch.Accepted,TEXT("Stone bat rejected accepted damage batch; preserve its authority and diagnostics."));
        if(!Batch.Accepted){for(int32 J=I;J<Accepted.Num();++J)if(Accepted[J].Target==Bat)BatLoss[J]=0.;continue;}
        Bat->HitFlash=.22f;AcceptBatBatch(Bat,Batch);Bat->SyncStoneBatState();if(Bat->bDead)OnFighterDied(Bat);
    }
    TArray<double> GuardLoss;GuardLoss.Init(0.,Accepted.Num());TSet<ADungeonFighter*> GuardTargets;
    for(int32 I=0;I<Accepted.Num();++I)
    {
        auto Guard=Accepted[I].Target;if(!IsValid(Guard)||!Guard->StoneGuard||Guard->bDead||GuardTargets.Contains(Guard))continue;
        GuardTargets.Add(Guard);std::vector<DungeonStoneGuard::FIncomingHit> Hits;
        uint64 Receipt=Guard->StoneGuard->State().LastDamageReceiptId;double Remaining=Guard->StoneGuard->State().HP;
        for(int32 J=I;J<Accepted.Num();++J)if(Accepted[J].Target==Guard)
        {
            const auto& H=Accepted[J];if(!FMath::IsFinite(H.Damage)||H.Damage<=0.f)continue;
            const float Rating=FMath::Max(0.f,Guard->GetArmorRating(H.Magic));
            const float Actual=H.Damage*(1.f-FMath::Min(.6f,Rating/(100.f+Rating)));
            const float Stagger=H.DamageOverTime?0.f:H.Stagger>=0.f?H.Stagger:H.Attacker?H.Attacker->GetAttackStagger():13.f;
            if(!FMath::IsFinite(Actual)||Actual<0.f||!FMath::IsFinite(Stagger)||Stagger<0.f)continue;
            const double Loss=FMath::Min(Remaining,double(Actual));Remaining-=Loss;GuardLoss[J]=Loss;
            Hits.push_back({++Receipt,H.AtTime,Loss,Stagger});
        }
        const auto Frame=MakeKnightFrame(Guard,Guard->StoneGuard->State().Time,SimulationTime,SkillBatchBodies);
        const auto Batch=Guard->StoneGuard->StepTo(SimulationTime,Frame,Hits);
        ensureMsgf(Batch.Accepted,TEXT("Stone Guard rejected resolved receipts; never reset its authority or apply generic damage."));
        if(!Batch.Accepted){for(int32 J=I;J<Accepted.Num();++J)if(Accepted[J].Target==Guard)GuardLoss[J]=0.;continue;}
        Guard->HitFlash=.22f;AcceptGuardBatch(Guard,Batch);Guard->SyncStoneGuardState();if(Guard->bDead)OnFighterDied(Guard);
    }
    for(int32 I=0;I<Accepted.Num();++I)if(IsValid(Accepted[I].Target))
    {
        const auto& H=Accepted[I];
        const float Before=H.Target->Health;
        const auto& Old=H.Target->HurtProtectionSource;
        const bool SameAction=H.Source.OwnerId&&Old.OwnerId==H.Source.OwnerId&&Old.ActionId==H.Source.ActionId;
        if(!H.Target->StoneBat&&!H.Target->StoneGuard)H.Target->ApplyCombatHitInternal(H.Damage,H.Attacker,H.Stagger,true,H.Magic,H.DamageOverTime,SameAction);
        const double Loss=H.Target->StoneGuard?GuardLoss[I]:H.Target->StoneBat?BatLoss[I]:FMath::Max(0.0,double(Before)-H.Target->Health);
        if (H.Source.OwnerId&&Loss>0.0)
        {
            if (!H.DamageOverTime&&!H.Target->StoneKnight&&!H.Target->StoneBat&&!H.Target->StoneGuard) H.Target->HurtProtectionSource=H.Source;
            FDungeonWorldWeaponEvent Fact;Fact.Kind=H.DamageOverTime?EDungeonWorldWeaponEventKind::BurnTickCommitted:EDungeonWorldWeaponEventKind::DirectHitCommitted;
            Fact.Key=H.Source;Fact.TargetId=H.Target->GetRuntimeEntityId();Fact.AtTime=H.AtTime;
            Fact.Position=H.ImpactPosition;Fact.Height=H.ImpactHeight;Fact.Damage=H.Damage;Fact.Stagger=H.Stagger;
            Fact.ActualHPLoss=Loss;Fact.Magic=H.Magic;
            for(const auto& Receipt:WeaponWorld.HitReceipts)if(Receipt.TargetId==Fact.TargetId&&Receipt.AtTime==H.AtTime
                &&Receipt.Key.OwnerId==H.Source.OwnerId&&Receipt.Key.ActionId==H.Source.ActionId
                &&Receipt.Key.EventId==H.Source.EventId&&Receipt.Key.SubhitId==H.Source.SubhitId
                &&Receipt.Key.RoomInstanceId==H.Source.RoomInstanceId)
            {
                Fact.HasPoseSocket=Receipt.HasPoseSocket;Fact.PoseSocket=Receipt.PoseSocket;
                Fact.RangeAnchor=Receipt.RangeAnchor;Fact.LaunchObstructed=Receipt.LaunchObstructed;break;
            }
            AppendWeaponWorldEvent(Fact);
            if (!H.DamageOverTime&&H.BurnDps>0) BurnApplications.Add(H);
        }
    }
    if(!PendingDamage.IsEmpty())CommitPendingDamage();
    for (const auto& H:BurnApplications) ApplyWorldBurn(H);
    ExpireWorldBurns(SimulationTime);
}

FVector2D ADungeonGameMode::SweepWeaponStep(ADungeonFighter* Fighter, double SignedDistance, double AtTime) const
{
    const FVector2D From = SkillPositionAt(Fighter,AtTime), Delta(SignedDistance,0.0), To = From+Delta;
    double Fraction = 1.0;
    const auto Bounds = DungeonRoomLayout::CenterBounds();
    if (From.X < Bounds.Min.X || From.X > Bounds.Max.X || From.Y < Bounds.Min.Y || From.Y > Bounds.Max.Y) return FVector2D::ZeroVector;
    if (To.X > Bounds.Max.X && Delta.X > 0.0) Fraction = FMath::Min(Fraction,(Bounds.Max.X-From.X)/Delta.X);
    if (To.X < Bounds.Min.X && Delta.X < 0.0) Fraction = FMath::Min(Fraction,(Bounds.Min.X-From.X)/Delta.X);
    FCollisionQueryParams Params(SCENE_QUERY_STAT(SwordSkillForwardStep),false);
    Params.AddIgnoredActor(Fighter);
    TArray<FHitResult> Walls;
    GetWorld()->SweepMultiByObjectType(Walls,FVector(From.X,From.Y,0),FVector(To.X,To.Y,0),FQuat::Identity,
        SkillWallObjects(),FCollisionShape::MakeBox(FVector(18.0,16.0,1.0)),Params);
    for (const auto& Wall : Walls)
        if (Wall.bBlockingHit && FMath::Abs(Wall.ImpactNormal.Z) < .5) Fraction = FMath::Min(Fraction,double(Wall.Time));
    for (const auto& B : SkillBatchBodies)
    {
        if (!B.bAlive || !B.bBlocksBody || !B.Fighter.IsValid() || B.Fighter.Get() == Fighter) continue;
        if(B.Fighter->StoneBat&&BatObservedBodyHeight(B,SkillBatchFrom,SkillBatchTo,AtTime)>40.)continue;
        const FVector2D Relative = SkillPositionAt(B.Fighter.Get(),AtTime)-From;
        const FVector2D Extent = B.BodyHalfExtent+FVector2D(18.0,16.0);
        double Entry = 0.0, Exit = 1.0;
        if (!SkillClip(Relative.X,Relative.X-Delta.X,-Extent.X,Extent.X,Entry,Exit)
            || !SkillClip(Relative.Y,Relative.Y-Delta.Y,-Extent.Y,Extent.Y,Entry,Exit)) continue;
        // A touch moving away or sliding on a body edge does not authorize a false block.
        if (Entry==0.0 && FMath::Abs(Relative.X)<Extent.X && FMath::Abs(Relative.Y)<Extent.Y)
        {
            const auto Motion=-Delta;
            const bool NearestX=Extent.X-FMath::Abs(Relative.X)<=Extent.Y-FMath::Abs(Relative.Y);
            if (NearestX ? Relative.X*Motion.X>=0.0 : Relative.Y*Motion.Y>=0.0) continue;
        }
        else if (Entry==0.0)
        {
            const auto Inside = Relative-Delta*FMath::Min(Exit*.5,1.e-6);
            if (Exit <= 0.0 || !(FMath::Abs(Inside.X) < Extent.X && FMath::Abs(Inside.Y) < Extent.Y)) continue;
        }
        const double SafeFraction=DungeonContactGeometry::ConservativeBodyFraction(0.0,Entry,Relative,Relative-Delta,Extent,
            [this,&B,AtTime,From,Delta](double Part)
            {
                // ConsumeWeaponSkillEvents commits ActorPosition + SignedStep*Part.
                return SkillPositionAt(B.Fighter.Get(),AtTime)-(From+Delta*Part);
            });
        Fraction = FMath::Min(Fraction,SafeFraction);
    }
    return Delta*FMath::Clamp(Fraction,0.0,1.0);
}

void ADungeonGameMode::ConsumeWeaponSkillEvents(ADungeonFighter* Fighter, const std::vector<DungeonWeaponActions::FEvent>& Events)
{
    if (!bSimulationBatch || !IsValid(Fighter)) return;
    if (Fighter->IsEquipmentBound()) {ConsumeBoundWeaponEvents(Fighter,Events);return;}
    for (const auto& E : Events)
    {
        if (E.EventId <= Fighter->LastSkillEventId) continue;
        Fighter->LastSkillEventId = E.EventId;
        if (E.Kind == DungeonWeaponActions::EEvent::ForwardStep)
        {
            const auto Delta = SweepWeaponStep(Fighter,E.ForwardStep,E.AtTime);
            const auto End = Fighter->GetGroundPosition()+Delta;
            Fighter->BatchSkillStepAt = E.AtTime; Fighter->BatchSkillStepDelta += Delta;
            Fighter->SetActorLocation(FVector(End.X,End.Y,0.0));
        }
        else if (E.Kind == DungeonWeaponActions::EEvent::ActiveWindow)
        {
            Fighter->SkillWindows.push_back(E);
            const TCHAR* Family=E.Action.Weapon==DungeonContentCombat::EWeapon::GSW001?TEXT("GSW")
                :E.Action.Weapon==DungeonContentCombat::EWeapon::SPR001?TEXT("SPR"):TEXT("SWD");
            const TCHAR* Cue=E.Action.Weapon==DungeonContentCombat::EWeapon::SPR001?TEXT("THRUST"):TEXT("WHOOSH");
            const FString Name=FString::Printf(TEXT("SW_AUD_%s_%s_03_v001"),Family,Cue);
            const FString Path=FString::Printf(TEXT("/Game/Production/FirstBatch/v001/Audio/%s.%s"),*Name,*Name);
            if (USoundBase* Whoosh = LoadObject<USoundBase>(nullptr,*Path))
                UGameplayStatics::PlaySound2D(Fighter,Whoosh,.25f);
        }
    }
    ResolveWeaponSkillWindows(Fighter);
}

bool ADungeonGameMode::FindWeaponSkillContact(ADungeonFighter* Fighter,ADungeonFighter* Target,
    const DungeonWeaponActions::FEvent& E,double& HitTime) const
{
    if (!IsValid(Fighter)||!IsValid(Target)||Target->bDead||Target->bEnemy==Fighter->bEnemy) return false;
    const uint64 TargetId=Target->GetRuntimeEntityId();
    if (Fighter->IsEquipmentBound())
    {
        const auto Key=WorldWeaponKey(Fighter,E);uint32 Count=0;
        for (const auto& R:WeaponWorld.HitReceipts)
            if (R.Key.OwnerId==Key.OwnerId&&R.Key.ActionId==E.ActionId&&R.Key.SubhitId==E.SubhitId)
            {if (R.TargetId==TargetId) return false;++Count;}
        if (E.MaxTargets&&Count>=E.MaxTargets) return false;
    }
    for (const auto& R:Fighter->SkillHitReceipts)
        if (R.ActionId==E.ActionId&&R.SubhitId==E.SubhitId&&R.TargetId==TargetId) return false;
    double Begin=FMath::Max(SkillBatchFrom,E.AtTime),End=FMath::Min(SkillBatchTo,E.WindowEnd);
    const auto& Protection=Target->HurtProtectionSource;
    const bool OwnAction=Fighter->IsEquipmentBound()&&Protection.OwnerId==Fighter->GetRuntimeEntityId()&&Protection.ActionId==E.ActionId;
    if (!OwnAction) if (const auto* Until=SkillOldIframeUntil.Find(TargetId)) Begin=FMath::Max(Begin,*Until);
    if (Begin>End||Begin>=E.WindowEnd) return false;
    if (End==E.WindowEnd) End=std::nextafter(End,Begin); // Half-open window, never extend it with a tolerance.
    if (Begin>End) return false;
    const bool Ground=E.OriginPolicy==DungeonWeaponActions::EOriginPolicy::GroundProjection;
    const auto OriginAt=[this,Fighter,&E,Ground](double At){return Ground?FVector2D(E.Origin.X,E.Origin.Y):SkillPositionAt(Fighter,At);};
    const auto R0=SkillPositionAt(Target,Begin)-OriginAt(Begin);
    const auto R1=SkillPositionAt(Target,End)-OriginAt(End);
    const double X0=R0.X*E.Action.Facing,X1=R1.X*E.Action.Facing;
    double Entry=0.0,Exit=1.0;
    if (E.Range<=0.0||E.Depth<=0.0||!SkillClip(X0,X1,E.MinRange,E.Range,Entry,Exit)) return false;
    if (E.Shape==DungeonContentCombat::EShape::ForwardEllipse)
    {
        const FVector2D P(X0/E.Range,R0.Y/E.Depth),D((X1-X0)/E.Range,(R1.Y-R0.Y)/E.Depth);
        const double A=D.SizeSquared(),B=2.0*FVector2D::DotProduct(P,D),C=P.SizeSquared()-1.0;
        if (A==0.0) { if (C>0.0) return false; }
        else
        {
            const double Disc=B*B-4*A*C;if (Disc<0.0) return false;
            Entry=FMath::Max(Entry,(-B-FMath::Sqrt(Disc))/(2*A));
            Exit=FMath::Min(Exit,(-B+FMath::Sqrt(Disc))/(2*A));
            if (Entry>Exit||Entry>1.0||Exit<0.0) return false;
        }
    }
    else if (!SkillClip(R0.Y,R1.Y,-E.Depth,E.Depth,Entry,Exit)) return false;
    const auto HeightAt=[this](ADungeonFighter* Actor,double At)
    {
        for (const auto& B:SkillBatchBodies) if (B.Fighter.Get()==Actor)
        {
            if(Actor->StoneBat)return BatObservedBodyHeight(B,SkillBatchFrom,SkillBatchTo,At);
            const double T=SkillBatchTo>SkillBatchFrom?FMath::Clamp((At-SkillBatchFrom)/(SkillBatchTo-SkillBatchFrom),0.0,1.0):1.0;
            return FMath::Lerp(B.StartHeight,B.EndHeight,T);
        }
        return Actor->GetCombatHeight();
    };
    if (!SkillClip(HeightAt(Target,Begin)-(Ground?0.0:HeightAt(Fighter,Begin)),HeightAt(Target,End)-(Ground?0.0:HeightAt(Fighter,End)),-65,65,Entry,Exit)) return false;
    const double First=FMath::Lerp(Begin,End,Entry),Last=FMath::Lerp(Begin,End,Exit);
    FCollisionQueryParams Params(SCENE_QUERY_STAT(SwordSkillLineOfSight),false);
    Params.AddIgnoredActor(Fighter);Params.AddIgnoredActor(Target);
    const auto Visible=[this,Fighter,Target,&Params,&OriginAt,&E](double At)
    {
        if (Fighter->IsEquipmentBound())
        {
            const auto Key=WorldWeaponKey(Fighter,E);
            for (const auto& B:SkillBatchBodies) if (B.Fighter.Get()==Target&&!WorldDamageAdmission(B,At,Key)) return false;
        }
        const auto P=OriginAt(At),T=SkillPositionAt(Target,At);
        return !GetWorld()->LineTraceTestByObjectType(FVector(P.X,P.Y,0),FVector(T.X,T.Y,0),SkillWallObjects(),Params);
    };
    HitTime=First;
    if (!Visible(HitTime))
    {
        // Reconsider the remaining legal geometry interval. A blocked entry is not a spent window.
        // Query several real positions, including its last representable point; then bisect
        // the first observed blocked->clear bracket. No damage or actor mutation occurs here.
        double Blocked=First;bool Found=false;
        for (int I=1;I<=16;++I)
        {
            const double Probe=FMath::Lerp(First,Last,double(I)/16.0);
            if (Visible(Probe))
            {
                double Clear=Probe;
                for (int J=0;J<48;++J) { const double Mid=(Blocked+Clear)*.5;if (Mid==Blocked||Mid==Clear) break;
                    if (Visible(Mid)) Clear=Mid;else Blocked=Mid; }
                HitTime=Clear;Found=true;break;
            }
            Blocked=Probe;
        }
        if (!Found) return false;
    }
    return HitTime<E.WindowEnd;
}

void ADungeonGameMode::ResolveWeaponSkillWindows(ADungeonFighter* Fighter)
{
    if (Fighter->IsEquipmentBound())
    {
        for (auto& W:WeaponWorld.Windows)
        {
            if (!W.Active||W.Key.OwnerId!=Fighter->GetRuntimeEntityId()||W.Key.RoomInstanceId!=WeaponWorld.RoomInstanceId) continue;
            struct FCandidate {ADungeonFighter* Target;double At;double Distance;};TArray<FCandidate> Candidates;
            for (ADungeonFighter* Target:Enemies)
            {
                double At=0;if (!FindWeaponSkillContact(Fighter,Target,W.Source,At)) continue;
                const auto Origin=W.Source.OriginPolicy==DungeonWeaponActions::EOriginPolicy::GroundProjection
                    ?FVector2D(W.Source.Origin.X,W.Source.Origin.Y):SkillPositionAt(Fighter,At);
                Candidates.Add({Target,At,(SkillPositionAt(Target,At)-Origin).SizeSquared()});
            }
            Candidates.Sort([](const FCandidate& A,const FCandidate& B)
            {return A.At!=B.At?A.At<B.At:A.Distance!=B.Distance?A.Distance<B.Distance:A.Target->GetRuntimeEntityId()<B.Target->GetRuntimeEntityId();});
            uint32 Count=0;for (const auto& R:WeaponWorld.HitReceipts)
                if (R.Key.OwnerId==W.Key.OwnerId&&R.Key.ActionId==W.Key.ActionId&&R.Key.SubhitId==W.Key.SubhitId) ++Count;
            for (const auto& C:Candidates)
            {
                if (W.Source.MaxTargets&&Count>=W.Source.MaxTargets) break;
                const bool Magic=W.Source.Action.Weapon==DungeonContentCombat::EWeapon::STF001;
                WeaponWorld.HitReceipts.Add({W.Key,C.Target->GetRuntimeEntityId(),C.At,W.Source.Damage,W.Source.Stagger,Magic});++Count;
                FPendingDamage H{Fighter,C.Target,float(W.Source.Damage),float(W.Source.Stagger),C.At};
                H.Magic=Magic;H.Source=W.Key;H.ImpactPosition=SkillPositionAt(C.Target,C.At);H.ImpactHeight=C.Target->JumpHeight;
                H.BurnDps=W.Source.BurnDps;H.BurnDuration=W.Source.BurnDuration;PendingDamage.Add(H);
            }
            if (SkillBatchTo>=W.Source.WindowEnd||(W.Source.MaxTargets&&Count>=W.Source.MaxTargets)) W.Active=false;
        }
        return;
    }
    for (const auto& E:Fighter->SkillWindows) for (ADungeonFighter* Target:Enemies)
    {
        double HitTime=0.0;
        if (!FindWeaponSkillContact(Fighter,Target,E,HitTime)) continue;
        Fighter->SkillHitReceipts.push_back({E.ActionId,E.SubhitId,Target->GetRuntimeEntityId()});
        PendingDamage.Add({Fighter,Target,float(E.Damage),float(E.Stagger),HitTime});
    }
    Fighter->SkillWindows.erase(std::remove_if(Fighter->SkillWindows.begin(),Fighter->SkillWindows.end(),
        [this](const DungeonWeaponActions::FEvent& E){return SkillBatchTo>=E.WindowEnd;}),Fighter->SkillWindows.end());
}

void ADungeonGameMode::Tick(float DeltaSeconds)
{
    TGuardValue<bool> RunTickGuard(bRunTickActive,true);
    Super::Tick(DeltaSeconds);
    if(IsRunInstallGated()){if(RunInstallGate==EDungeonRunInstallGate::AwaitExplicitContinue)ObserveRunInstallInput();return;}
    if(SuppressRestoreContinueEnter)
        if(auto* C=UGameplayStatics::GetPlayerController(this,0))
            if(!C->IsInputKeyDown(EKeys::Enter))SuppressRestoreContinueEnter=false;
    if(bFairytaleLookdevPreview)
    {
        // Independent display direction only. No Fighter input/kernel/AI clock advances.
        bWaitingForStart=true;
        if(auto Controller=UGameplayStatics::GetPlayerController(this,0))
        {
            const bool Left=Controller->IsInputKeyDown(EKeys::A),Right=Controller->IsInputKeyDown(EKeys::D);
            if(Left!=Right)FairytaleLookdevFacing=Left?-1:1;
        }
        return;
    }
    if (APlayerController* Controller = UGameplayStatics::GetPlayerController(this, 0))
    {
        if (bWaitingForStart && ((!SuppressRestoreContinueEnter&&Controller->WasInputKeyJustPressed(EKeys::Enter)) || Controller->WasInputKeyJustPressed(EKeys::SpaceBar)))
        {
            bWaitingForStart = false;
            if(SceneObjects->Current().Active)LastMessage=TEXT("沿侧路调查遗迹，击败守卫后前往出口。");
        }
        if (Controller->WasInputKeyJustPressed(EKeys::R))
        {
            RestartRun();
        }
    }
    if (!PlayerFighter || !FMath::IsFinite(DeltaSeconds) || DeltaSeconds <= 0.f) return;
    if (bGameOver)
    {
        PlayerFighter->AdvanceTerminalPresentation(DeltaSeconds);
        for (ADungeonFighter* Enemy : Enemies)
            if (IsValid(Enemy)) Enemy->AdvanceTerminalPresentation(DeltaSeconds);
        return;
    }
    if (bWaitingForStart) {ObserveRunExploration();return;}
    AdmitWorldFighters();
    if (EquipmentRuntime->View.Bound) {UpdateEquipmentMirrors();UpdateEquipmentTarget();}
    // Fresh input is admitted once at the real frame start. Subdivision never creates
    // new presses or consumes the same physical edge a second time.
    PlayerFighter->UpdatePlayerInput(0.f,true);
    // The just-invalidated displayed equipment target consumed this input
    // generation. The refreshed target is now observable before a later E.
    bSceneEquipmentTargetLost=false;
    const double FrameEnd=SimulationTime+double(DeltaSeconds);
    int32 ZeroBatches=0;
    while (SimulationTime<FrameEnd && !bGameOver)
    {
        const double FromTime=SimulationTime;
        PlayerFighter->UpdatePlayerInput(0.f,false); // Held-direction cancellation, without replaying fresh edges.
        PlayerFighter->BatchSkillStepAt=-1.0; PlayerFighter->BatchSkillStepDelta=FVector2D::ZeroVector;
        PlayerFighter->CommitIdleDodgePosition();
        SkillOldIframeUntil.Reset();
        for (const auto& B:CaptureKnightBodies()) if (B.Fighter.IsValid())
            SkillOldIframeUntil.Add(B.EntityId,FromTime+double(FMath::Max(0.f,B.Fighter->InvulnerableTime)));
        double ToTime=NextSimulationBoundary(FMath::Min(FrameEnd,FromTime+.005));
        auto Predicted=PredictMotionBodies(FromTime,ToTime);
        // Read-only preview finds an earlier physical/valid-window contact. Re-evaluate
        // shorter motion rather than advancing a real kernel then rolling it backwards.
        for (int I=0;I<12;++I)
        {
            const double Contact=EarliestContact(ToTime,Predicted);
            if (Contact>=ToTime) break;
            ToTime=Contact;Predicted=PredictMotionBodies(FromTime,ToTime);
        }
        const float Step=float(ToTime-FromTime);
        const auto BeforeMotion=CaptureKnightBodies();
        MotionBatchBodies=Predicted;bSimulatingMotion=true;
        if (PlayerFighter->Dodge.State().Phase!=DungeonDodge::EPhase::Dead)
        {
            const auto R=PlayerFighter->Dodge.StepTo(ToTime,[this,&Predicted](const DungeonDodge::FSweepRequest& Q)
            {return QueryResolvedMovement(PlayerFighter,{Q.From.X,Q.From.Y},{Q.To.X,Q.To.Y},Q.FromTime,Q.ToTime,Predicted);});
            ensureMsgf(R.Accepted,TEXT("Dodge rejects inconsistent motion observations instead of resetting its authority."));
            if (PlayerFighter->Dodge.State().Phase==DungeonDodge::EPhase::Dodging
                ||(!R.Events.empty()&&R.Events.back().Kind==DungeonDodge::EEventKind::Completed))
            {
                const auto& D=PlayerFighter->Dodge.State();PlayerFighter->SetActorLocation(FVector(D.Position.X,D.Position.Y,0));
            }
        }
        const auto CommitMotion=[Step,&Predicted](ADungeonFighter* Fighter)
        {
            if (!IsValid(Fighter)) return;
            // Timers, existing resources and ballistic velocity advance exactly once.
            // XY is the already resolved query result, not a second movement attempt.
            Fighter->bSuppressOrdinaryMovement=true;Fighter->SimulateMotion(Step,false);Fighter->bSuppressOrdinaryMovement=false;
            if (Fighter->StoneKnight || Fighter->StoneGuard) return;
            for (const auto& P:Predicted) if (P.Fighter.Get()==Fighter)
            {
                if (Fighter->Dodge.State().Phase==DungeonDodge::EPhase::Dodging)
                {const auto& D=Fighter->Dodge.State();Fighter->SetActorLocation(FVector(D.Position.X,D.Position.Y,0));}
                else Fighter->SetActorLocation(FVector(P.End.X,P.End.Y,0));
                if(Fighter->StoneBat)Fighter->BatObservedHeight=P.EndHeight;
                if (!Fighter->bDead) Fighter->JumpHeight=float(P.EndHeight);
                if (!Fighter->bDead && P.EndHeight<=0.0 && P.StartHeight>0.0 && Fighter->JumpVelocity<0.f)
                {
                    Fighter->JumpVelocity=0.f;Fighter->LandingVisualAge=0.f;Fighter->bAirPrimarySpent=false;
                    Fighter->Combat.NotifyLand();
                    if (!Fighter->IsEquipmentBound()) Fighter->WeaponSkills.NotifyLand();
                }
                Fighter->bMoving=!P.Start.Equals(P.End,1.e-9);
                break;
            }
        };
        CommitMotion(PlayerFighter);
        for (ADungeonFighter* Enemy:Enemies) CommitMotion(Enemy);
        bSimulatingMotion=false;
        PlayerFighter->CommitIdleDodgePosition();
        auto Bodies=CaptureKnightBodies();
        for (auto& B:Bodies) for (const auto& Before:BeforeMotion) if (Before.EntityId==B.EntityId)
        {
            B.Start=Before.Start;B.StartHeight=Before.StartHeight;B.bAlive=Before.bAlive;B.bCanTakeDamage=Before.bCanTakeDamage;
            B.DirectInvulnerabilityIntervals=Before.DirectInvulnerabilityIntervals;
            for (const auto& P:Predicted) if (P.EntityId==B.EntityId) {B.MotionSegments=P.MotionSegments;break;}
            break;
        }
        SkillBatchBodies=Bodies;SkillBatchFrom=FromTime;SkillBatchTo=ToTime;
        PendingDamage.Reset();bSimulationBatch=true;
        std::vector<DungeonWeaponActions::FEvent> DeferredSkillEvents;
        PlayerFighter->SimulateActionsTo(ToTime,Step,&DeferredSkillEvents);
        // Existing windows precede any new endpoint step. Their contact time was included
        // in the preview above; receipts are admitted against the same frozen observations.
        ResolveWeaponSkillWindows(PlayerFighter);
        ResolveWorldProjectiles(FromTime,ToTime,Bodies);
        for (ADungeonFighter* Enemy:Enemies)
        {
            if (!IsValid(Enemy)) continue;
            if (Enemy->StoneKnight)
            {
                const auto Batch=Enemy->StoneKnight->StepTo(ToTime,MakeKnightFrame(Enemy,FromTime,ToTime,Bodies));
                ensureMsgf(Batch.Accepted,TEXT("Stone knight rejected authoritative simulation interval; never reset its state to repair it."));
                AcceptKnightBatch(Enemy,Batch);Enemy->SyncStoneKnightState();
            }
            else if(!Enemy->StoneBat&&!Enemy->StoneGuard)Enemy->SimulateActionsTo(ToTime,Step);
        }
        SimulationTime=ToTime;
        if (EquipmentRuntime->View.Bound) WeaponWorld.Time=ToTime;
        QueueWorldBurnTicks(ToTime);
        // All same-point accepted contacts share the old admission. New hurt protection
        // never rejects another already accepted hit in this same committed point.
        CommitPendingDamage();
        // Bat Pump follows all old world/player damage at this endpoint. Its
        // accepted old contacts still precede new bound-player emission.
        for(ADungeonFighter* Enemy:Enemies)if(IsValid(Enemy)&&Enemy->StoneBat)
        {
            const auto Batch=Enemy->StoneBat->StepTo(ToTime,MakeKnightFrame(Enemy,Enemy->StoneBat->State().Time,ToTime,Bodies));
            ensureMsgf(Batch.Accepted,TEXT("Stone bat rejected authoritative interval; do not reset or advance past its obligation."));
            AcceptBatBatch(Enemy,Batch);Enemy->SyncStoneBatState();if(Enemy->bDead)OnFighterDied(Enemy);
        }
        for(ADungeonFighter* Enemy:Enemies)if(IsValid(Enemy)&&Enemy->StoneGuard)
        {
            const auto Batch=Enemy->StoneGuard->StepTo(ToTime,MakeKnightFrame(Enemy,Enemy->StoneGuard->State().Time,ToTime,Bodies));
            ensureMsgf(Batch.Accepted,TEXT("Stone Guard rejected authoritative interval; preserve state, never reset or masquerade as generic AI."));
            if(Batch.Accepted){AcceptGuardBatch(Enemy,Batch);Enemy->SyncStoneGuardState();if(Enemy->bDead)OnFighterDied(Enemy);}
        }
        CommitPendingDamage();
        if (PlayerFighter->IsEquipmentBound())
        {
            bool RuntimeSynchronized=false;
            PlayerFighter->AdvanceWeaponSkillTo(ToTime,&DeferredSkillEvents,&RuntimeSynchronized);
            // Observe even a real death/cancellation before the gameplay-event
            // guard. This cannot release a hit, spend, or change a deadline.
            ObserveActionAudio(PlayerFighter,DeferredSkillEvents,RuntimeSynchronized);
        }
        if (!bGameOver && !PlayerFighter->bDead
            && PlayerFighter->WeaponSkills.State().Action.Terminal!=DungeonWeaponActions::EEvent::Interrupted)
        {
            // No forward step/active window can escape an earlier real interruption.
            ConsumeWeaponSkillEvents(PlayerFighter,DeferredSkillEvents);
            PlayerFighter->CommitIdleDodgePosition();
            PlayerFighter->SyncWeaponSkillAction();
            CommitPendingDamage();
        }
        bSimulationBatch=false;
        // Every old/bat/new-player damage and death at this point has drained.
        // Currency precedes equipment/scene commits and has no idle requirement.
        CollectAutomaticRunRewards();
        if (EquipmentRuntime->View.Bound)
        {
            CommitEquipmentAction();UpdateEquipmentMirrors();UpdateEquipmentTarget();
        }
        ValidateSceneConfirmation();CommitSceneInteraction();
        if (ToTime==FromTime)
        {
            if (++ZeroBatches>16) {ensureMsgf(false,TEXT("Contact subdivision made no authority progress; do not skip a pending contact."));break;}
        }
        else ZeroBatches=0;
    }
    bSceneEquipmentTargetLost=false;
    ObserveRunExploration(); // One observation per completed Tick, independent of Canvas.
}

void ADungeonGameMode::RestartRun()
{
    if(IsRunInstallGated())return;
    APlayerController* Controller = UGameplayStatics::GetPlayerController(this, 0);
    if (!PlayerFighter && Controller)
    {
        PlayerFighter = Cast<ADungeonFighter>(Controller->GetPawn());
    }
    if (!PlayerFighter)
    {
        PlayerFighter = GetWorld()->SpawnActor<ADungeonFighter>();
    }
    if (!PlayerFighter)
    {
        return;
    }
    if(SceneObjects->Current().Active||FParse::Param(FCommandLine::Get(),TEXT("DungeonSceneExplorationPreview")))
    {
        if(Controller)
        {
            Controller->Possess(PlayerFighter);Controller->SetInputMode(FInputModeGameOnly());Controller->bShowMouseCursor=false;
            AddTickPrerequisiteActor(Controller);
        }
        SetupSceneExplorationPreviewRun();return;
    }
    if(bManualWeaponPreview||FParse::Param(FCommandLine::Get(),TEXT("DungeonManualWeaponPreview")))
    {
        if(Controller)
        {
            Controller->Possess(PlayerFighter);Controller->SetInputMode(FInputModeGameOnly());Controller->bShowMouseCursor=false;
            AddTickPrerequisiteActor(Controller);
        }
        SetupManualWeaponPreviewRun();return; // R is the explicit fresh-Run boundary; repeated Begin is idempotent.
    }
    if (EquipmentRuntime->View.Bound)
    {
        const auto Config=EquipmentRuntime->View.Config;const uint64 Seed=EquipmentRuntime->View.CombatSeed;
        PlayerFighter->SetActorLocation(FVector(-460,0,0));
        if (BeginEquipmentRun(Config,Seed)) SpawnRoom();
        return;
    }
    ++RunRestartSerial;
    PlayerFighter->bEnemy = false;
    PlayerFighter->SetActorTickEnabled(false);
    SimulationTime = 0.0;
    LastStoneWakeStartedAt = -1.0;
    PendingDamage.Reset(); bSimulationBatch = false;
    PlayerFighter->MaxHealth = 100.f;
    PlayerFighter->Coins = 0;
    PlayerFighter->WeaponId = TEXT("sword");
    PlayerFighter->ArmorId.Reset();
    PlayerFighter->bHasAxe = false;
    PlayerFighter->ResetFighter(FVector2D(-460.f, 0.f));
    if (Controller)
    {
        Controller->Possess(PlayerFighter);
        Controller->SetInputMode(FInputModeGameOnly());
        Controller->bShowMouseCursor = false;
        AddTickPrerequisiteActor(Controller);
    }
    PlayerFighter->SetActorTickEnabled(false);
    RoomNumber = 1;
    bGameOver = false;
    bWaitingForStart = false;
    LastMessage = TEXT("清除房间中的敌人。上下移动躲开攻击，空格跳跃，J 攻击。");
    SpawnRoom();
}

void ADungeonGameMode::SpawnRoom()
{
    for (ADungeonFighter* Enemy : Enemies)
    {
        if (IsValid(Enemy))
        {
            Enemy->Destroy();
        }
    }
    Enemies.Reset();
    Pickups.Reset();
    bRoomCleared = false;
    if(SceneObjects->Current().Active)
    {
        SpawnSceneExplorationRoom();return;
    }
    if(FParse::Param(FCommandLine::Get(),TEXT("DungeonStoneBatPreview")))
    {
        if(!EquipmentRuntime->View.Bound)BeginEquipmentRun(EDungeonEquipmentRunConfig::IntegrationPreview,1);
        SpawnStoneBat(PlayerFighter->GetGroundPosition()+FVector2D(160.,0.));return;
    }
    if (FParse::Param(FCommandLine::Get(), TEXT("DungeonStoneKnightPreview")))
    {
        // Explicit development encounter; normal prototype rooms and opening equipment stay unchanged.
        if (ADungeonFighter* Enemy = GetWorld()->SpawnActor<ADungeonFighter>())
        {
            Enemy->ResetFighter(FVector2D(300.f,0.f));
            Enemies.Add(Enemy);
            Enemy->InitializeStoneKnight(uint64(Enemy->GetUniqueID()), SimulationTime); // QA identity, not D13.
        }
        return;
    }
    const FVector2D Positions[] = { FVector2D(180.f, -100.f), FVector2D(390.f, 95.f), FVector2D(580.f, -30.f) };
    for (const FVector2D& Position : Positions)
    {
        ADungeonFighter* Enemy = GetWorld()->SpawnActor<ADungeonFighter>();
        if (Enemy)
        {
            Enemy->bEnemy = true;
            Enemy->SetActorTickEnabled(false);
            Enemy->MaxHealth = 65.f + FMath::Min(RoomNumber - 1, 4) * 8.f;
            Enemy->ResetFighter(Position);
            Enemies.Add(Enemy);
        }
    }
}

void ADungeonGameMode::NextRoom()
{
    TUniquePtr<FDungeonRunExploration> ExplorationCandidate;
    if(EquipmentRuntime->View.Bound)
    {
        if(!RunExploration||!RunExploration->Matches(EquipmentRuntime->View.RunGuid,EquipmentRuntime->View.RoomInstanceId))return;
        ExplorationCandidate=MakeUnique<FDungeonRunExploration>(*RunExploration);FString Why;
        if(RoomNumber==MAX_int32||!ExplorationCandidate->EnterRoom(EquipmentRuntime->View.RoomInstanceId+1,RoomNumber+1,Why))return;
    }
    if(EquipmentRuntime->View.Bound&&!RetireRunRewardRoom())return;
    if(ExplorationCandidate)RunExploration=MoveTemp(ExplorationCandidate);
    if (EquipmentRuntime->View.Bound) ClearWorldRoomAttacks();
    ++RoomNumber;
    if (EquipmentRuntime->View.Bound)
    {
        ++EquipmentRuntime->View.RoomInstanceId;EquipmentRuntime->View.SelectedSourceId=0;CancelEquipmentSelection();
        WeaponWorld.RoomInstanceId=EquipmentRuntime->View.RoomInstanceId;
        ActionAudioState.RoomInstanceId=EquipmentRuntime->View.RoomInstanceId;
    }
    // A free ordinary-room exit relocates the same character. Character resources,
    // invulnerability, poise and absolute action clocks continue across the boundary.
    const auto Entry=SceneObjects->Current().Active?SceneObjects->Current().Layout.Entry:FVector2D(-580.,0.);
    if(SceneObjects->Current().Active)
    {
        SceneObjects->BeginRoom(EquipmentRuntime->View.RunGuid,EquipmentRuntime->View.RoomInstanceId);
        bSceneEquipmentTargetLost=false;CancelSceneInteraction();
    }
    PlayerFighter->SetActorLocation(FVector(Entry.X,Entry.Y,0.));
    PlayerFighter->CommitIdleDodgePosition();
    LastMessage = FString::Printf(TEXT("进入第 %d 房。保留金币与已拾取武器。"), RoomNumber);
    SpawnRoom();
}

void ADungeonGameMode::TryAttack(ADungeonFighter* Attacker)
{
    if(IsRunInstallGated())return;
    if (IsValid(Attacker) && !bGameOver && !bWaitingForStart)
    {
        Attacker->BeginAttack();
    }
}

void ADungeonGameMode::ResolveAttack(ADungeonFighter* Attacker)
{
    if(IsRunInstallGated())return;
    if (!IsValid(Attacker) || Attacker->bDead || Attacker->StoneKnight || Attacker->StoneBat || Attacker->StoneGuard || bGameOver)
    {
        return;
    }
    if (Attacker->IsEquipmentBound()&&!Attacker->IsContentMelee()) return; // Ranged world bodies never enter prototype melee.
    const auto Apply = [this, Attacker](ADungeonFighter* Target)
    {
        if (!Target->CanReceiveDirectHit()) return;
        if (bSimulationBatch) PendingDamage.Add({Attacker, Target, Attacker->GetAttackDamage(), Attacker->GetAttackStagger(),SkillBatchTo});
        else Target->ApplyCombatHit(Attacker->GetAttackDamage(), Attacker, Attacker->GetAttackStagger());
    };
    const auto Hit = [Attacker, &Apply](ADungeonFighter* Target)
    {
        if (Attacker->IsContentMelee())
        {
            if (IsValid(Target) && Target->CanReceiveDirectHit() && Attacker->CanContentHit(Target) && Attacker->MarkContentHit(Target))
                Apply(Target);
            return;
        }
        if (IsValid(Target) && !Target->bDead && ADungeonFighter::CanHitTarget(
            Target->GetGroundPosition() - Attacker->GetGroundPosition(), Attacker->Facing,
            Attacker->GetAttackRange(), Attacker->GetAttackDepth(), Attacker->JumpHeight, Target->JumpHeight))
        {
            Apply(Target);
        }
    };
    if (Attacker->bEnemy)
    {
        Hit(PlayerFighter);
    }
    else
    {
        if (Attacker->WeaponId == TEXT("WPN-SPR-001"))
        {
            ADungeonFighter* Nearest = nullptr;
            double Distance = TNumericLimits<double>::Max();
            for (ADungeonFighter* Enemy : Enemies)
            {
                if (!IsValid(Enemy) || !Enemy->CanReceiveDirectHit() || !Attacker->CanContentHit(Enemy)) continue;
                const double Candidate = (Enemy->GetGroundPosition()-Attacker->GetGroundPosition()).SizeSquared();
                if (Candidate < Distance || (Candidate == Distance && Nearest && Enemy->GetUniqueID() < Nearest->GetUniqueID()))
                { Nearest = Enemy; Distance = Candidate; }
            }
            if (Nearest) Hit(Nearest);
            return;
        }
        for (ADungeonFighter* Enemy : Enemies)
        {
            Hit(Enemy);
        }
    }
}

void ADungeonGameMode::OnFighterDied(ADungeonFighter* Fighter)
{
    if(IsRunInstallGated())return;
    if (!IsValid(Fighter) || !Fighter->bDead || Fighter->bDeathReported)
    {
        return;
    }
    if(Fighter->StoneGuard)
    {
        if(!Fighter->bGuardDeathObserved)
        {
            Fighter->bGuardDeathObserved=true;
            LastMessage=TEXT("裂岩守卫已死亡；正式房间奖励／存续消费者尚未接入，未发币且未结算清房。");
            for(ADungeonFighter* Stone:Enemies)
            {
                if(!IsValid(Stone)||Stone==Fighter||Stone->bDead||(!Stone->StoneKnight&&!Stone->StoneBat&&!Stone->StoneGuard))continue;
                bool Cleared=true;for(ADungeonFighter* Other:Enemies)if(IsValid(Other)&&Other!=Stone&&!Other->bDead){Cleared=false;break;}
                if(Cleared){if(Stone->StoneGuard)Stone->StoneGuard->NotifyOtherAcceptedEnemiesCleared();
                    else if(Stone->StoneKnight)Stone->StoneKnight->NotifyOtherAcceptedEnemiesCleared();else Stone->StoneBat->NotifyOtherAcceptedEnemiesCleared();}
            }
        }
        return; // bDeathReported remains false; local death eligibility is not reward settlement.
    }
    TUniquePtr<FDungeonRunRewards> RewardCandidate;
    FDungeonRunRewardDeathResult ResolvedReward;
    if(EquipmentRuntime->View.Bound)
    {
        if(!RunRewards)return;
        const auto& V=EquipmentRuntime->View;const uint64 Id=FindWorldEntityId(Fighter);
        if(Fighter==PlayerFighter)
        {if(Fighter->bEnemy||Id!=V.OwnerId)return;}
        else
        {
            const auto* Binding=WeaponWorld.ActorBindings.FindByPredicate([Id](const auto& X){return X.EntityId==Id;});
            const FString Content=Fighter->EnemyContentId.IsEmpty()?TEXT("QA-PROTOTYPE-ENEMY"):Fighter->EnemyContentId;
            if(!Fighter->bEnemy||!Enemies.Contains(Fighter)||!Id||!Binding||Binding->RoomInstanceId!=V.RoomInstanceId
                ||Binding->ContentId!=Content)return;
            int32 Alive=0,Dead=0;
            for(auto Enemy:Enemies)if(IsValid(Enemy)){if(Enemy->bDead)++Dead;else ++Alive;}
            FDungeonRunRewardDeathRequest Q;Q.EntityId=Id;Q.RoomInstanceId=V.RoomInstanceId;Q.ContentId=Content;
            Q.AtTime=Fighter->StoneKnight?Fighter->StoneKnight->State().Time:Fighter->StoneBat?Fighter->StoneBat->State().Time:SimulationTime;
            Q.Position=Fighter->GetGroundPosition();Q.FirstDeath=Dead==1;Q.RoomCleared=Alive==0;
            // Resolve a full value candidate BEFORE claiming/reporting this death.
            // An invalid scope/result cannot consume the actor's one claim.
            RewardCandidate=MakeUnique<FDungeonRunRewards>(*RunRewards);FString Why;
            ResolvedReward=RewardCandidate->ResolveDeath(Q,Why);
            if(!ResolvedReward.Ok()){LastMessage=TEXT("死亡奖励记录拒绝：")+Why;return;}
        }
    }
    if (Fighter->StoneKnight && !Fighter->StoneKnight->ClaimDeathReward()) return;
    if (Fighter->StoneBat && !Fighter->StoneBat->ClaimDeathReward()) return;
    Fighter->bDeathReported = true;
    if(RewardCandidate)RunRewards=MoveTemp(RewardCandidate);
    if (!Fighter->bEnemy)
    {
        bGameOver = true;
        LastMessage = TEXT("本次探索结束。按 R 重新开始。");
        return;
    }
    const FVector2D GroundPosition = Fighter->GetGroundPosition();
    int32 AliveCount = 0;
    int32 DeadCount = 0;
    for (ADungeonFighter* Enemy : Enemies)
    {
        if (IsValid(Enemy))
        {
            Enemy->bDead ? ++DeadCount : ++AliveCount;
        }
    }
    if(EquipmentRuntime->View.Bound)
    {
        if(!ResolvedReward.Replayed)
        {
            const auto Snapshot=RunRewards->Capture();
            for(uint64 Id:ResolvedReward.ObjectIds)if(const auto* O=Snapshot.Objects.FindByPredicate([Id](const auto& X){return X.ObjectId==Id;}))
            {
                FDungeonPickup P;P.Position=O->Position;
                P.Kind=O->Kind==EDungeonRunRewardKind::Coin?TEXT("coin"):O->Kind==EDungeonRunRewardKind::Potion?TEXT("potion"):TEXT("axe");
                P.RunGuid=Snapshot.RunGuid;P.ObjectId=O->ObjectId;P.SourceId=O->SourceId;P.RoomInstanceId=O->RoomInstanceId;
                Pickups.Add(P);
            }
        }
    }
    else
    {
        FDungeonPickup Coin;Coin.Position=GroundPosition+FVector2D(-18.f,-12.f);Coin.Kind=TEXT("coin");Pickups.Add(Coin);
    }
    // This notification follows an actual admitted enemy's death. An initial empty
    // set never counts as "all other enemies killed" and cannot wake a lone statue.
    for (ADungeonFighter* Knight : Enemies)
    {
        if (!Enemies.Contains(Fighter) || !IsValid(Knight) || Knight->bDead || (!Knight->StoneKnight&&!Knight->StoneBat&&!Knight->StoneGuard) || Knight == Fighter) continue;
        bool OthersCleared = true;
        for (ADungeonFighter* Other : Enemies)
            if (IsValid(Other) && Other != Knight && !Other->bDead) { OthersCleared = false; break; }
        if (OthersCleared){if(Knight->StoneGuard)Knight->StoneGuard->NotifyOtherAcceptedEnemiesCleared();else if(Knight->StoneKnight)Knight->StoneKnight->NotifyOtherAcceptedEnemiesCleared();else Knight->StoneBat->NotifyOtherAcceptedEnemiesCleared();}
    }
    if (DeadCount == 1&&!EquipmentRuntime->View.Bound)
    {
        FDungeonPickup Potion;
        Potion.Position = GroundPosition + FVector2D(25.f, 15.f);
        Potion.Kind = TEXT("potion");
        Pickups.Add(Potion);
    }
    if (AliveCount == 0)
    {
        bRoomCleared = true;
        if(!EquipmentRuntime->View.Bound)
        {
            FDungeonPickup Axe;Axe.Position=GroundPosition+FVector2D(34.f,14.f);Axe.Kind=TEXT("axe");Pickups.Add(Axe);
        }
        LastMessage = SceneObjects->Current().Active?TEXT("守卫已被击败。可继续调查侧路，或前往右端出口。")
            :TEXT("房间已清空！E 拾取战利品，前往右侧出口按 E 继续。");
    }
    else
    {
        LastMessage = TEXT("敌人倒下了。靠近战利品按 E 拾取。");
    }
}

void ADungeonGameMode::TryInteract()
{
    if(IsRunInstallGated())return;
    if (EquipmentRuntime->View.Bound)
    {
        if(!SceneObjects->Current().Active){TryInteractEquipment();return;}
        if(SceneObjects->Interaction.Pending)return;
        if(bSceneEquipmentTargetLost)
        {
            bSceneEquipmentTargetLost=false;
            EquipmentRuntime->Fail(EDungeonEquipmentFailure::InvalidSource,TEXT("目标已失效，请重新选择。"));return;
        }
        // A real equipment target owns this E even if its admission fails.
        // No-target routing is decided by the displayed target facts, not by
        // equipment transaction counters unrelated to a free ordinary exit.
        if(EquipmentRuntime->View.SelectedSourceId||EquipmentRuntime->View.NeedsSlotSelection){TryInteractEquipment();return;}
        UpdateEquipmentTarget();
        if(bSceneEquipmentTargetLost)
        {
            bSceneEquipmentTargetLost=false;
            EquipmentRuntime->Fail(EDungeonEquipmentFailure::InvalidSource,TEXT("目标已失效，请重新选择。"));return;
        }
        if(EquipmentRuntime->View.SelectedSourceId){TryInteractEquipment();return;}
        EquipmentRuntime->Fail(EDungeonEquipmentFailure::NoTarget,TEXT("附近没有装备。"));
        TryInteractScene();return;
    }
    if (!IsValid(PlayerFighter) || PlayerFighter->bDead || bGameOver || PlayerFighter->JumpHeight > 0.f
        || !PlayerFighter->CanStartAttack())
    {
        return;
    }
    const FVector2D Position = PlayerFighter->GetGroundPosition();
    bool bCollected = false;
    for (FDungeonPickup& Pickup : Pickups)
    {
        const FVector2D Delta = Pickup.Position - Position;
        if (Pickup.bConsumed || FMath::Abs(Delta.X) > 85.f || FMath::Abs(Delta.Y) > 45.f)
        {
            continue;
        }
        if (Pickup.Kind == TEXT("coin"))
        {
            PlayerFighter->Coins += 5;
            LastMessage = TEXT("拾取金币 +5");
        }
        else if (Pickup.Kind == TEXT("potion"))
        {
            if (PlayerFighter->Health >= PlayerFighter->MaxHealth)
            {
                LastMessage = TEXT("生命已满，药水留在地面。受伤后再来拾取。");
                continue;
            }
            PlayerFighter->Health = DungeonCombatRules::RestoreHealth(PlayerFighter->Health, PlayerFighter->MaxHealth, 30.f);
            LastMessage = TEXT("饮用生命药水：恢复 30 点生命");
        }
        else if (Pickup.Kind == TEXT("axe"))
        {
            PlayerFighter->bHasAxe = true;
            PlayerFighter->WeaponId = TEXT("axe");
            LastMessage = TEXT("拾取重斧！按 Q 可在长剑 / 重斧之间切换。");
        }
        else
        {
            continue;
        }
        Pickup.bConsumed = true;
        bCollected = true;
    }
    if (!bCollected && bRoomCleared && Position.X > 600.f && FMath::Abs(Position.Y) < 100.f)
    {
        NextRoom();
    }
}

ADungeonFighter* ADungeonGameMode::SpawnStoneGuard(FVector2D GroundPosition)
{
    if(IsRunInstallGated()||!GetWorld()||!EquipmentRuntime->View.Bound||!IsValid(PlayerFighter)||bGameOver
        ||!FMath::IsFinite(GroundPosition.X)||!FMath::IsFinite(GroundPosition.Y)
        ||!DungeonRoomLayout::CenterBounds().IsInsideOrOn(GroundPosition))return nullptr;
    auto Guard=GetWorld()->SpawnActor<ADungeonFighter>();if(!Guard)return nullptr;
    Guard->bEnemy=true;Guard->bAIEnabled=false;Guard->EnemyContentId=TEXT("ENM-STN-003");Guard->ResetFighter(GroundPosition);
    Enemies.Add(Guard);AdmitWorldFighters();const uint64 Id=FindWorldEntityId(Guard);
    if(!Id||!Guard->InitializeStoneGuard(Id,SimulationTime))
    {
        Enemies.Remove(Guard);WorldEntityIds.Remove(Guard);
        WeaponWorld.ActorBindings.RemoveAll([Id](const FDungeonWorldActorBinding& B){return B.EntityId==Id;});
        Guard->Destroy();return nullptr; // Retire any consumed ID, never silently reuse it.
    }
    bRoomCleared=false;return Guard;
}
void ADungeonGameMode::AcceptGuardBatch(ADungeonFighter* Guard,const FDungeonGuardBatch& Batch)
{
    if(!Batch.Accepted||!IsValid(Guard)||!Guard->StoneGuard)return;
    for(const auto& E:Batch.Events)if(E.Kind==DungeonStoneGuard::EEventKind::WakeStarted)LastStoneWakeStartedAt=E.AtTime;
    // Only the normal accepted PendingDamage path may change a real target's HP.
    for(const auto& H:Batch.Hits)if(bSimulationBatch&&H.Target.IsValid())
        PendingDamage.Add({Guard,H.Target.Get(),float(H.Damage),float(H.Stagger),H.AtTime});
}
