#include "DungeonRunInstaller.h"
#include "DungeonFighter.h"
#include "DungeonGameMode.h"
#include "Components/BoxComponent.h"
#include "Components/SceneComponent.h"
#include "Engine/Engine.h"
#include "Engine/World.h"
#include "PhysicsEngine/BodyInstance.h"

namespace
{
bool Fail(FString& Why,const TCHAR* Message){Why=Message;return false;}
bool OwnerFail(FString& Why,const TCHAR* Owner,const FString& Detail)
{Why=FString(Owner)+TEXT(": ")+Detail;return false;}
bool ExactTransform(const FTransform& A,const FTransform& B)
{return A.GetTranslation()==B.GetTranslation()&&A.GetRotation()==B.GetRotation()&&A.GetScale3D()==B.GetScale3D();}
bool WorldUsable(const ADungeonGameMode& Game)
{
    const auto* World=Game.GetWorld();
    return IsInGameThread()&&IsValid(&Game)&&World&&!World->bIsTearingDown&&GEngine
        &&GEngine->GetWorldContextFromWorld(World)&&World->GetAuthGameMode<ADungeonGameMode>()==&Game;
}
FDungeonFighterRestoreContext FighterContext(const FDungeonRunSnapshot& S,uint64 Entity,
    const FDungeonEquipmentRuntimeSnapshot& Equipment,const FDungeonWeaponWorldState& World)
{
    FDungeonFighterRestoreContext C;C.RunGuid=S.RunGuid;C.RoomInstanceId=S.RoomInstanceId;C.EntityId=Entity;
    C.SimulationTime=S.SimulationTime;C.GameOver=S.GameOver;C.Equipment=&Equipment;C.WeaponWorld=&World;return C;
}
FDungeonRunRewardValidationContext RewardContext(const FDungeonRunSnapshot& S,const FDungeonWeaponWorldState& World)
{
    FDungeonRunRewardValidationContext C;C.RunGuid=S.RunGuid;C.OwnerId=S.OwnerId;C.RoomInstanceId=S.RoomInstanceId;
    C.SimulationTime=S.SimulationTime;C.PlayerCoins=S.Fighters[0].Coins;C.WeaponWorld=&World;
    for(const auto& F:S.Fighters)
    {
        const bool Claimed=F.Knight.IsSet()?F.Knight.GetValue().RewardClaimed:F.Bat.IsSet()?F.Bat.GetValue().RewardClaimed:false;
        C.CurrentActors.Add({F.EntityId,F.RoomInstanceId,F.Kind==EDungeonFighterOwnerKind::BoundPlayer?TEXT("player"):F.EnemyContentId,
            F.Enemy,F.Dead,F.DeathReported,Claimed});
    }
    return C;
}
bool CheckStageActor(const AActor* Actor,const UWorld* World,FString& Why)
{
    if(!IsValid(Actor)||Actor->IsActorBeingDestroyed()||Actor->GetWorld()!=World||!Actor->IsHidden()
        ||Actor->IsActorTickEnabled()||Actor->GetActorEnableCollision())
        return Fail(Why,TEXT("Staged actor lost its independent hidden/tick-off/collision-off lifecycle"));
    return true;
}
bool CheckGeometry(const FDungeonRunInstallGroup& G,FString& Why)
{
    const auto* S=G.SavedValues();if(!S||!G.Game.IsValid())return Fail(Why,TEXT("Staging has no sealed geometry scope"));
    if(S->Geometry.Kind==EDungeonRunGeometryKind::FlatBoundsV1)
        return G.GeometryActors.IsEmpty()?true:Fail(Why,TEXT("Flat staged Run unexpectedly contains Scene geometry"));
    if(S->Geometry.Kind!=EDungeonRunGeometryKind::SceneExplorationV1||!S->Scene.CurrentRoom.Active
        ||G.GeometryActors.Num()!=1||!G.GeometryActors[0].IsValid())
        return Fail(Why,TEXT("Staged supported Scene barrier is missing or ambiguous"));
    const auto* A=G.GeometryActors[0].Get();const auto* Box=Cast<UBoxComponent>(A->GetRootComponent());
    const auto& B=S->Scene.CurrentRoom.Layout.Barrier;const auto Center=B.GetCenter(),Half=B.GetExtent();
    if(!CheckStageActor(A,G.Game->GetWorld(),Why)||A->GetClass()!=AActor::StaticClass()||!Box
        ||Box->GetClass()!=UBoxComponent::StaticClass()||!Box->IsRegistered()||Box->GetAttachParent()
        ||A->GetActorLocation()!=FVector(Center.X,Center.Y,40.)||A->GetActorQuat()!=FQuat::Identity
        ||A->GetActorScale3D()!=FVector::OneVector||Box->GetUnscaledBoxExtent()!=FVector(Half.X,Half.Y,80.)
        ||Box->GetCollisionObjectType()!=ECC_WorldStatic||Box->GetCollisionResponseToChannels()!=FCollisionResponseContainer(ECR_Block))
        return Fail(Why,TEXT("Native staged Scene barrier readback differs from the sealed authored layout"));
    // Include every owned primitive, even if it is not registered yet: enabling
    // the published actor must not activate geometry absent from the sealed Run.
    TInlineComponentArray<UPrimitiveComponent*> Primitives;
    A->GetComponents(Primitives,false);
    if(Primitives.Num()!=1||Primitives[0]!=Box)
        return Fail(Why,TEXT("Staged Scene barrier owns primitives outside its exact sealed root Box set"));
    // The public component getter checks its owner's disabled collision override.
    // Read the existing native stored policy without enabling the staged actor,
    // allocating a body setup or touching the old Run's query geometry.
    const auto* Body=Box->GetBodyInstance(NAME_None,false);
    if(!Body||Body->GetCollisionEnabled(false)!=ECollisionEnabled::QueryOnly)
        return Fail(Why,TEXT("Staged barrier did not retain its real stored QueryOnly collision policy"));
    return true;
}
bool StageGeometry(FDungeonRunInstallGroup& G,FString& Why)
{
    const auto& S=*G.SavedValues();if(S.Geometry.Kind==EDungeonRunGeometryKind::FlatBoundsV1)return true;
    if(S.Geometry.Kind!=EDungeonRunGeometryKind::SceneExplorationV1||!S.Scene.CurrentRoom.Active)
        return Fail(Why,TEXT("Unknown staged geometry scope"));
    auto* World=G.Game->GetWorld();FActorSpawnParameters P;P.ObjectFlags|=RF_Transient;
    auto* A=World->SpawnActor<AActor>(P);if(!A)return Fail(Why,TEXT("Native Scene barrier actor creation failed"));
    G.StagedActors.Add(A);G.GeometryActors.Add(A);
    A->SetActorTickEnabled(false);A->SetActorHiddenInGame(true);A->SetActorEnableCollision(false);
    auto* Box=NewObject<UBoxComponent>(A,NAME_None,RF_Transient);
    if(!Box)return Fail(Why,TEXT("Native Scene barrier component creation failed"));
    A->SetRootComponent(Box);A->AddInstanceComponent(Box);
    const auto& B=S.Scene.CurrentRoom.Layout.Barrier;const auto Half=B.GetExtent(),Center=B.GetCenter();
    Box->SetBoxExtent(FVector(Half.X,Half.Y,80.),false);
    Box->SetCollisionEnabled(ECollisionEnabled::QueryOnly);Box->SetCollisionObjectType(ECC_WorldStatic);
    Box->SetCollisionResponseToAllChannels(ECR_Block);Box->RegisterComponent();
    Box->SetWorldLocationAndRotationNoPhysics(FVector(Center.X,Center.Y,40.),FRotator::ZeroRotator);
    Box->UpdateComponentToWorld(EUpdateTransformFlags::SkipPhysicsUpdate,ETeleportType::TeleportPhysics);
    return CheckGeometry(G,Why);
}
bool CheckGroup(FDungeonRunInstallGroup& G,FString& Why)
{
    const auto* S=G.SavedValues();
    if(!S||!G.Game.IsValid()||!WorldUsable(*G.Game)||!G.Token||G.Committed
        ||!G.Equipment||!G.Scene||!G.Rewards||!G.Exploration||G.Fighters.Num()!=S->Fighters.Num()
        ||G.EntityIds.Num()!=S->Fighters.Num()||G.StagedActors.Num()!=G.Fighters.Num()+G.GeometryActors.Num())
        return Fail(Why,TEXT("Staged complete group has an invalid scope, lifetime or owner set"));
    if(!CheckGeometry(G,Why))return false;
    FDungeonRunSnapshot Readback=*S;
    Readback.Equipment=G.Equipment->Capture();Readback.Scene=G.Scene->Capture();
    Readback.WeaponWorld=DungeonWorldSnapshot::Capture(G.WeaponWorld);Readback.Rewards=G.Rewards->Capture();
    Readback.Exploration=G.Exploration->Capture();Readback.Fighters.Reset();
    auto* World=G.Game->GetWorld();
    for(int32 I=0;I<G.Fighters.Num();++I)
    {
        const auto& Saved=S->Fighters[I];auto* F=G.Fighters[I].Get();
        if(!CheckStageActor(F,World,Why)||F->GetClass()!=ADungeonFighter::StaticClass()
            ||!F->GetRootComponent()||!F->GetRootComponent()->IsRegistered()
            ||G.EntityIds.FindRef(F)!=Saved.EntityId)return Fail(Why,TEXT("Staged current fighter identity/order or native lifecycle changed"));
        const auto Context=FighterContext(*S,Saved.EntityId,Readback.Equipment,G.WeaponWorld);
        FDungeonFighterOwnerSnapshot Actual;
        if(!F->CaptureOwnerSnapshot(Actual,Why,&Context))return OwnerFail(Why,TEXT("Staged fighter native Capture"),Why);
        auto* Muzzle=F->GetWeaponMuzzleComponent();auto* Anchor=Muzzle?Muzzle->GetAttachParent():nullptr;
        if(Actual.Schema!=Saved.Schema||Actual.Kind!=Saved.Kind||Actual.GroundPosition!=Saved.GroundPosition
            ||Actual.Health!=Saved.Health||Actual.MaxHealth!=Saved.MaxHealth||Actual.JumpHeight!=Saved.JumpHeight
            ||Actual.JumpVelocity!=Saved.JumpVelocity||Actual.Facing!=Saved.Facing||Actual.Dead!=Saved.Dead
            ||Actual.DeathReported!=Saved.DeathReported||Actual.Coins!=Saved.Coins||!Anchor||!Anchor->IsRegistered()
            ||!Muzzle||!Muzzle->IsRegistered()
            ||!ExactTransform(Anchor->GetRelativeTransform(),Saved.HeightAnchorRelative)
            ||Actual.CustomMuzzle!=Saved.CustomMuzzle
            ||Saved.CustomMuzzle&&(!Muzzle||!ExactTransform(Muzzle->GetRelativeTransform(),Saved.CustomMuzzleRelative)))
            return Fail(Why,TEXT("Staged native body/HP/terminal/actual-anchor/custom-muzzle values were not installed exactly"));
        Readback.Fighters.Add(MoveTemp(Actual));
    }
    if(G.ActionAudio.RunGuid!=S->RunGuid||G.ActionAudio.RoomInstanceId!=S->RoomInstanceId
        ||!G.ActionAudio.Records.IsEmpty()||G.AudioCursors.Num()!=S->Audio.WeaponCursors.Num())
        return Fail(Why,TEXT("Staging attempted to install a transient audio history or omitted continuation cursors"));
    Readback.Audio.RunGuid=G.ActionAudio.RunGuid;Readback.Audio.RoomInstanceId=G.ActionAudio.RoomInstanceId;
    Readback.Audio.NextActionSequence=G.ActionAudio.NextSequence;
    Readback.Audio.WorldHistoryThrough=G.WeaponWorld.NextEventSequence-1;Readback.Audio.WeaponCursors.Reset();
    for(const auto& C:G.AudioCursors)Readback.Audio.WeaponCursors.Add({C.Key,C.Value});
    Readback.Audio.WeaponCursors.Sort([](const auto& A,const auto& B){return A.OwnerId<B.OwnerId;});
    Readback.Audio.StoneSeeds.Reset();
    for(const auto& F:Readback.Fighters)if(F.Knight.IsSet())Readback.Audio.StoneSeeds.Add({F.EntityId,F.Knight.GetValue().NextEventId});
    // Each owner's actual Capture is read back through the already certified
    // whole-root validator. No live GM binding, Step, RNG draw or replay is used.
    FDungeonValidatedRun Checked;
    if(!FDungeonRunAggregate::Validate(Readback,Checked,Why))return OwnerFail(Why,TEXT("Staged all-owner readback"),Why);
    return true;
}
}

FDungeonPreparedRun::FDungeonPreparedRun()=default;
FDungeonPreparedRun::~FDungeonPreparedRun(){FDungeonRunInstaller::Release(*this);}
FDungeonPreparedRun::FDungeonPreparedRun(FDungeonPreparedRun&& Other):Group(MoveTemp(Other.Group)){}
FDungeonPreparedRun& FDungeonPreparedRun::operator=(FDungeonPreparedRun&& Other)
{
    if(this!=&Other){FDungeonRunInstaller::Release(*this);Group=MoveTemp(Other.Group);}return *this;
}
bool FDungeonPreparedRun::IsReady() const {return Group&&Group->Validated.IsValid()&&Group->Token&&!Group->Committed;}
const FDungeonRunSnapshot* FDungeonPreparedRun::GetSavedSnapshot() const {return Group?Group->SavedValues():nullptr;}
const TArray<TWeakObjectPtr<AActor>>& FDungeonPreparedRun::GetStagedActors() const
{static const TArray<TWeakObjectPtr<AActor>> Empty;return Group?Group->StagedActors:Empty;}
void FDungeonRunInstaller::Release(FDungeonPreparedRun& Prepared)
{
    if(!Prepared.Group)return;auto Group=MoveTemp(Prepared.Group);
    if(Group->Committed)return;
    // Destruction callbacks are still behind this group's preparation gate.
    // Never destroy old/current GM actors or a group already handed to GameMode.
    for(const auto& W:Group->StagedActors)if(auto* A=W.Get())
    {
        const auto* World=A->GetWorld();
        if(!A->IsActorBeingDestroyed()&&World&&!World->bIsTearingDown&&GEngine&&GEngine->GetWorldContextFromWorld(World))
        {A->SetActorTickEnabled(false);A->SetActorEnableCollision(false);A->SetActorHiddenInGame(true);A->Destroy();}
    }
    if(Group->Game.IsValid()&&Group->Token)Group->Game->AbortRunInstallPreparation(Group->Token);
}
bool FDungeonRunInstaller::Prepare(ADungeonGameMode& Game,const FDungeonValidatedRun& Saved,
    FDungeonPreparedRun& Out,FString& Diagnostic)
{
    if(!WorldUsable(Game)||!Saved.IsValid()||!Saved.Get())return Fail(Diagnostic,TEXT("Preparation requires a real game-thread target World and a sealed complete Run"));
    FDungeonValidatedRun Sealed;
    if(!FDungeonRunAggregate::Validate(*Saved.Get(),Sealed,Diagnostic))return false;
    // The target itself must be at a supported complete boundary; this read
    // neither consumes input nor reconstructs missing target state.
    FDungeonRunSnapshot Old;
    if(!FDungeonRunAggregate::Capture(Game,Old,Diagnostic))return OwnerFail(Diagnostic,TEXT("Preparation target"),Diagnostic);
    return PrepareValidated(Game,Sealed,Out,false,Diagnostic);
}
bool FDungeonRunInstaller::PrepareValidated(ADungeonGameMode& Game,const FDungeonValidatedRun& Sealed,
    FDungeonPreparedRun& Out,bool Pristine,FString& Diagnostic)
{
    FDungeonPreparedRun Candidate;Candidate.Group=MakeUnique<FDungeonRunInstallGroup>();auto& G=*Candidate.Group;
    G.Game=&Game;G.Validated=Sealed;G.PristineOrigin=Pristine;
    if(Pristine)
    {if(!Game.BeginPristineRunInstallPreparation(G.Token,Diagnostic))return false;}
    else if(!Game.BeginRunInstallPreparation(G.Token,Diagnostic))return false;
    const auto& S=*G.SavedValues();
    G.Equipment=MakeUnique<FDungeonEquipmentRuntime>();G.Scene=MakeUnique<FDungeonSceneObjects>();
    G.Rewards=MakeUnique<FDungeonRunRewards>();G.Exploration=MakeUnique<FDungeonRunExploration>();
    if(!G.Equipment->Restore(S.Equipment,Diagnostic))return OwnerFail(Diagnostic,TEXT("Equipment staging"),Diagnostic);
    if(!G.Scene->Restore(S.Scene,Diagnostic))return OwnerFail(Diagnostic,TEXT("Scene staging"),Diagnostic);
    FDungeonWeaponWorldRestoreContext WC;WC.RunGuid=S.RunGuid;WC.RoomInstanceId=S.RoomInstanceId;WC.OwnerId=S.OwnerId;
    WC.SimulationTime=S.SimulationTime;WC.PlayerActions=&S.Fighters[0].Player.GetValue().WeaponActions;
    if(!DungeonWorldSnapshot::Restore(S.WeaponWorld,WC,G.WeaponWorld,Diagnostic))return OwnerFail(Diagnostic,TEXT("WeaponWorld staging"),Diagnostic);
    const auto RC=RewardContext(S,G.WeaponWorld);
    if(!G.Rewards->Restore(S.Rewards,RC,Diagnostic))return OwnerFail(Diagnostic,TEXT("Reward staging"),Diagnostic);
    if(!G.Exploration->Restore(S.Exploration,Diagnostic))return OwnerFail(Diagnostic,TEXT("Exploration staging"),Diagnostic);
    if(!StageGeometry(G,Diagnostic))return false;
    const auto Equipment=G.Equipment->Capture();auto* World=Game.GetWorld();
    for(const auto& F:S.Fighters)
    {
        FActorSpawnParameters P;P.ObjectFlags|=RF_Transient;
        auto* Actor=World->SpawnActor<ADungeonFighter>(P);
        if(!Actor)return Fail(Diagnostic,TEXT("Native staging fighter creation failed"));
        G.StagedActors.Add(Actor);G.Fighters.Add(Actor);G.EntityIds.Add(Actor,F.EntityId);
        Actor->SetActorTickEnabled(false);Actor->SetActorHiddenInGame(true);Actor->SetActorEnableCollision(false);
        const auto Context=FighterContext(S,F.EntityId,Equipment,G.WeaponWorld);
        if(!Actor->RestoreOwnerSnapshot(F,Context,Diagnostic))return OwnerFail(Diagnostic,TEXT("Native fighter staging Restore"),Diagnostic);
    }
    G.ActionAudio.RunGuid=S.RunGuid;G.ActionAudio.RoomInstanceId=S.RoomInstanceId;G.ActionAudio.NextSequence=S.Audio.NextActionSequence;
    for(const auto& C:S.Audio.WeaponCursors)G.AudioCursors.Add(C.OwnerId,C.Cursor);
    if(!CheckGroup(G,Diagnostic))return false;
    if(Pristine&&!Game.CheckPristineUnpublishedState(&G,Diagnostic))return false;
    Out=MoveTemp(Candidate);Diagnostic.Reset();return true;
}
bool FDungeonRunInstaller::PreparePristine(ADungeonGameMode& Game,const FDungeonValidatedRun& Saved,
    FDungeonPreparedRun& Out,FString& Diagnostic)
{
    if(!WorldUsable(Game)||!Saved.IsValid()||!Saved.Get())
        return Fail(Diagnostic,TEXT("Pristine preparation requires a real target World and sealed complete Run"));
    if(!Game.IsPristineContinueBootstrap(Diagnostic))return false;
    FDungeonValidatedRun Sealed;
    if(!FDungeonRunAggregate::Validate(*Saved.Get(),Sealed,Diagnostic))return false;
    return PrepareValidated(Game,Sealed,Out,true,Diagnostic);
}
bool FDungeonRunInstaller::Install(ADungeonGameMode& Game,FDungeonPreparedRun& Prepared,FString& Diagnostic)
{
    if(!WorldUsable(Game)||!Prepared.IsReady()||Prepared.Group->Game.Get()!=&Game
        ||Game.GetRunInstallGate()!=EDungeonRunInstallGate::Preparing)
        return Fail(Diagnostic,TEXT("Installation requires this target's still-ready sealed preparation token"));
    auto& G=*Prepared.Group;
    // Native resources may have been invalidated since Prepare. Every fallible
    // owner/geometry readback remains before the single GameMode root swap.
    if(!CheckGroup(G,Diagnostic))return false;
    if(!Game.CommitPreparedRunGroup(G,Diagnostic))return false;
    G.Committed=true;Prepared.Group.Reset();Diagnostic.Reset();return true;
}
