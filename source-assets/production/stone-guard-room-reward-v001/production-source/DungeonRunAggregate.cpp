#include "DungeonRunAggregate.h"
#include "DungeonNativeGeometryGuards.h"
#include "DungeonGameMode.h"
#include "DungeonFighter.h"
#include "DungeonRoomLayout.h"
#include "Components/BoxComponent.h"
#include "Components/PrimitiveComponent.h"
#include "Components/BrushComponent.h"
#include "Engine/Brush.h"
#include "Engine/Level.h"
#include "Engine/World.h"
#include "EngineUtils.h"
#include "Model.h"
#include "PhysicsEngine/BodyInstance.h"
#include <limits>

namespace
{
namespace WA=DungeonWeaponActions;
bool Fail(FString& Why,const TCHAR* Message){Why=Message;return false;}
bool OwnerFailure(FString& Why,const TCHAR* Owner,const FString& Detail)
{Why=FString(Owner)+TEXT(": ")+Detail;return false;}
bool FiniteTime(double At){return FMath::IsFinite(At)&&At>=0.;}
bool SameAction(const WA::FAction& A,const WA::FAction& B)
{
    if(A.Type!=B.Type||A.Phase!=B.Phase||A.Weapon!=B.Weapon||A.InstanceId!=B.InstanceId||A.ActionId!=B.ActionId
        ||A.Active!=B.Active||A.Locked!=B.Locked||A.StartedAirborne!=B.StartedAirborne||A.ForwardStepIssued!=B.ForwardStepIssued
        ||A.NextSubhit!=B.NextSubhit||A.Critical!=B.Critical||A.Terminal!=B.Terminal)return false;
    const double X[]={A.Facing,A.Start,A.LockAt,A.ActiveAt,A.ActiveEnd,A.End,A.SpeedPct,A.DamagePct,A.StaggerPct,A.ReachPct,
        A.CritMultiplier,A.AmmoCost,A.FocusCost,A.CooldownDuration,A.ReloadSpeedPct,A.FocusCostPct,A.SkillCooldownPct};
    const double Y[]={B.Facing,B.Start,B.LockAt,B.ActiveAt,B.ActiveEnd,B.End,B.SpeedPct,B.DamagePct,B.StaggerPct,B.ReachPct,
        B.CritMultiplier,B.AmmoCost,B.FocusCost,B.CooldownDuration,B.ReloadSpeedPct,B.FocusCostPct,B.SkillCooldownPct};
    for(int32 I=0;I<UE_ARRAY_COUNT(X);++I)if(!FMath::IsFinite(X[I])||!FMath::IsFinite(Y[I])||X[I]!=Y[I])return false;
    return true;
}
const FDungeonFighterOwnerSnapshot* FindFighter(const FDungeonRunSnapshot& S,uint64 Id)
{return S.Fighters.FindByPredicate([Id](const auto& F){return F.EntityId==Id;});}
FDungeonRunRewardActorFact RewardActor(const FDungeonFighterOwnerSnapshot& F)
{
    const bool Claimed=F.Knight.IsSet()?F.Knight.GetValue().RewardClaimed:F.Bat.IsSet()?F.Bat.GetValue().RewardClaimed:F.Guard.IsSet()?F.Guard.GetValue().Kernel.RewardClaimed:false;
    return {F.EntityId,F.RoomInstanceId,F.Kind==EDungeonFighterOwnerKind::BoundPlayer?TEXT("player"):F.EnemyContentId,
        F.Enemy,F.Dead,F.DeathReported,Claimed};
}
FName PickupName(EDungeonRunRewardKind Kind)
{
    switch(Kind)
    {
    case EDungeonRunRewardKind::Coin:return TEXT("coin");
    case EDungeonRunRewardKind::Potion:return TEXT("potion");
    case EDungeonRunRewardKind::Axe:return TEXT("axe");
    default:return NAME_None;
    }
}
bool ValidateAudio(const FDungeonRunSnapshot& S,FString& Why)
{
    const auto& Audio=S.Audio;const auto& W=S.WeaponWorld.State;
    const auto* Player=FindFighter(S,S.OwnerId);
    if(Audio.Schema!=1||Audio.RunGuid!=S.RunGuid||Audio.RoomInstanceId!=S.RoomInstanceId||!Audio.NextActionSequence
        ||Audio.WorldHistoryThrough!=W.NextEventSequence-1||!Player||!Player->Player.IsSet()
        ||Audio.WeaponCursors.Num()!=1||Audio.WeaponCursors[0].OwnerId!=S.OwnerId)
        return Fail(Why,TEXT("Audio continuation scope, consumed tail or owner set conflicts"));
    const auto& A=Player->Player.GetValue().WeaponActions;const auto& Cursor=Audio.WeaponCursors[0].Cursor;
    if(!Cursor.Attached||Cursor.LastEventId!=A.NextEventId-1||Cursor.RuntimeReceiptCount!=A.WeaponRuntimeHistory.size()
        ||!FiniteTime(Cursor.LastObservedTime)||Cursor.LastObservedTime!=A.Time||Cursor.InsertObserved&&!Cursor.DrawObserved)
        return Fail(Why,TEXT("Audio adapter cursor is not the complete accepted weapon boundary"));
    const bool Reload=A.Action.Active&&A.Action.Type==WA::EAction::Reload&&A.Action.Weapon==DungeonContentCombat::EWeapon::XBW001;
    if(Reload)
    {
        const double DrawAt=A.Action.Start+(A.Action.End-A.Action.Start)*(.20/1.10);
        const double InsertAt=A.Action.Start+(A.Action.End-A.Action.Start)*(.60/1.10);
        if(!SameAction(Cursor.Reload,A.Action)||Cursor.DrawObserved!=(A.Time>=DrawAt)||Cursor.InsertObserved!=(A.Time>=InsertAt))
            return Fail(Why,TEXT("Audio reload continuation lost the accepted phase/deadline or consumed stages"));
    }
    else if(!SameAction(Cursor.Reload,WA::FAction{}))
        return Fail(Why,TEXT("Audio has a completion obligation for an absent/cancelled reload"));
    TSet<uint64> Seeds;int32 Knights=0;
    for(const auto& F:S.Fighters)if(F.Knight.IsSet())
    {
        ++Knights;const auto* Seed=Audio.StoneSeeds.FindByPredicate([&](const auto& X){return X.EntityId==F.EntityId;});
        if(!Seed||Seed->NextEventId!=F.Knight.GetValue().NextEventId)
            return Fail(Why,TEXT("Stone consumer seed differs from the saved current owner event boundary"));
    }
    for(const auto& Seed:Audio.StoneSeeds)
        if(!Seed.EntityId||!Seed.NextEventId||Seeds.Contains(Seed.EntityId))return Fail(Why,TEXT("Ambiguous stone consumer seed"));
        else Seeds.Add(Seed.EntityId);
    if(Knights!=Audio.StoneSeeds.Num())return Fail(Why,TEXT("Stone consumer seeds contain an unknown or historical actor"));
    return true;
}
bool KnownEmptyWorldBuilder(const UWorld* World,const AActor* Actor,const UPrimitiveComponent* Component)
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
    // GetDefaultBrush is a read of Actors[1]; its native checks are safe only
    // after the component/model checks above. Editor Polys are not a game body.
    if(World->GetDefaultBrush()!=Builder)return false;
    const auto* Body=Component->GetBodyInstance(NAME_None,false);
    return !Body||!Body->IsValidBodyInstance();
}
// Only the currently authored query geometry is reconstructible. The caller
// supplies the actual cache; this function never treats its names as authority.
bool CaptureGeometry(const ADungeonGameMode& Game,const TArray<TWeakObjectPtr<AActor>>& SceneActors,
    const FDungeonSceneObjectsSnapshot& Scene,FDungeonRunGeometrySnapshot& Out,FString& Why)
{
    auto* World=Game.GetWorld();if(!World)return Fail(Why,TEXT("Capture has no real World"));
    TSet<const UPrimitiveComponent*> Approved;
    if(Scene.CurrentRoom.Active)
    {
        if(SceneActors.Num()!=1||!SceneActors[0].IsValid())return Fail(Why,TEXT("Scene geometry cache is incomplete or ambiguous"));
        const auto* Actor=SceneActors[0].Get();const auto* Box=Cast<UBoxComponent>(Actor->GetRootComponent());
        const auto& Barrier=Scene.CurrentRoom.Layout.Barrier;const auto Half=Barrier.GetExtent(),Center=Barrier.GetCenter();
        if(!Box||!Box->IsRegistered()||!Actor->GetActorEnableCollision()||Box->GetAttachParent()
            ||Actor->GetActorLocation()!=FVector(Center.X,Center.Y,40.)||Actor->GetActorQuat()!=FQuat::Identity
            ||Actor->GetActorScale3D()!=FVector::OneVector||Box->GetUnscaledBoxExtent()!=FVector(Half.X,Half.Y,80.)
            ||Box->GetCollisionEnabled()!=ECollisionEnabled::QueryOnly||Box->GetCollisionObjectType()!=ECC_WorldStatic)
            return Fail(Why,TEXT("Actual Scene geometry differs from its immutable supported barrier"));
        // ECC_MAX also includes a deprecated pseudochannel which has no stored
        // response slot. Compare every native stored channel without indexing it.
        if(Box->GetCollisionResponseToChannels()!=FCollisionResponseContainer(ECR_Block))
            return Fail(Why,TEXT("Actual Scene barrier has unknown query response semantics"));
        Approved.Add(Box);Out.Kind=EDungeonRunGeometryKind::SceneExplorationV1;
    }
    else
    {
        if(!SceneActors.IsEmpty())return Fail(Why,TEXT("Flat geometry contains an unrepresented Scene cache"));
        Out.Kind=EDungeonRunGeometryKind::FlatBoundsV1;
    }
    for(TActorIterator<AActor> It(World);It;++It)
    {
        const auto* Actor=*It;if(!IsValid(Actor)||!Actor->GetActorEnableCollision())continue;
        TInlineComponentArray<UPrimitiveComponent*> Components;Actor->GetComponents(Components);
        for(const auto* Component:Components)if(IsValid(Component)&&Component->IsRegistered()
            &&Component->GetCollisionEnabled()!=ECollisionEnabled::NoCollision&&!Approved.Contains(Component))
        {
            if(KnownEmptyWorldBuilder(World,Actor,Component))continue;
            if(DungeonNativeGeometryGuards::IsNativeGameplayDebuggerDrawOnly(World,Actor,Component))continue;
            Why=FString::Printf(TEXT("Capture refuses an external collision component outside supported geometry: actorClass=%s actor=%s componentClass=%s component=%s registered=%d enabled=%d objectType=%d"),
                *Actor->GetClass()->GetPathName(),*Actor->GetPathName(),*Component->GetClass()->GetPathName(),*Component->GetPathName(),
                int32(Component->IsRegistered()),int32(Component->GetCollisionEnabled()),int32(Component->GetCollisionObjectType()));
            return false;
        }
    }
    return true;
}
}

bool FDungeonRunAggregate::Capture(const ADungeonGameMode& Game,FDungeonRunSnapshot& Out,FString& Diagnostic)
{
    if(Game.bRunTickActive||Game.bSimulationBatch||Game.bSimulatingMotion||!Game.PendingDamage.IsEmpty())
        return Fail(Diagnostic,TEXT("Run Capture requires the end of the complete input/motion/damage/interaction Tick"));
    if(Game.bFairytaleLookdevPreview||!Game.EquipmentRuntime||!Game.SceneObjects||!Game.RunRewards||!Game.RunExploration
        ||!IsValid(Game.PlayerFighter)||!Game.GetWorld())return Fail(Diagnostic,TEXT("Run Capture has an unsupported or incomplete authoritative owner set"));
    FDungeonRunSnapshot Candidate;
    Candidate.Equipment=Game.EquipmentRuntime->Capture();const auto& V=Candidate.Equipment.View;
    if(!V.Bound)return Fail(Diagnostic,TEXT("Run Capture requires a bound development Run"));
    Candidate.Scope=EDungeonRunScope::BoundDevelopmentV1;Candidate.RunGuid=V.RunGuid;
    Candidate.OwnerId=V.OwnerId;Candidate.RoomInstanceId=V.RoomInstanceId;Candidate.RoomNumber=Game.RoomNumber;
    Candidate.SimulationTime=Game.SimulationTime;Candidate.LastStoneWakeStartedAt=Game.LastStoneWakeStartedAt;
    Candidate.RoomCleared=Game.bRoomCleared;Candidate.GameOver=Game.bGameOver;Candidate.WaitingForStart=Game.bWaitingForStart;
    Candidate.SceneCommitRequested=Game.bSceneCommitRequested;Candidate.SceneEquipmentTargetLost=Game.bSceneEquipmentTargetLost;
    Candidate.LastMessage=Game.LastMessage;Candidate.SceneEncounterEntityId=Game.SceneEncounterEntityId;
    Candidate.Scene=Game.SceneObjects->Capture();Candidate.WeaponWorld=DungeonWorldSnapshot::Capture(Game.WeaponWorld);
    Candidate.Rewards=Game.RunRewards->Capture();Candidate.Exploration=Game.RunExploration->Capture();
    if(!CaptureGeometry(Game,Game.SceneWorldActors,Candidate.Scene,Candidate.Geometry,Diagnostic))return false;
    TSet<const ADungeonFighter*> CurrentActors;
    const auto AddActor=[&](const ADungeonFighter* Actor,bool Player)
    {
        if(!IsValid(Actor)||Actor->GetWorld()!=Game.GetWorld()||CurrentActors.Contains(Actor))
            return Fail(Diagnostic,TEXT("Current actor order contains an absent, foreign or duplicate actor"));
        FDungeonFighterOwnerSnapshot F;
        if(!Actor->CaptureOwnerSnapshot(F,Diagnostic))return false;
        if((F.EntityId==V.OwnerId)!=Player)return Fail(Diagnostic,TEXT("Actual actor order disagrees with its admitted stable owner identity"));
        CurrentActors.Add(Actor);if(!Player)Candidate.EnemyOrder.Add(F.EntityId);
        Candidate.Fighters.Add(MoveTemp(F));return true;
    };
    if(!AddActor(Game.PlayerFighter,true))return false;
    for(const auto& Enemy:Game.Enemies)if(!AddActor(Enemy,false))return false;
    if(Candidate.Rewards.Schema==2||Candidate.Fighters.ContainsByPredicate([](const auto& F){return F.Guard.IsSet();}))
    {Candidate.Schema=2;Candidate.Scope=EDungeonRunScope::BoundDevelopmentV2;}
    for(const auto& Entry:Game.WorldEntityIds)if(Entry.Key.IsValid()&&!CurrentActors.Contains(Entry.Key.Get()))
        return Fail(Diagnostic,TEXT("A live admitted world actor is absent from the current owner array"));
    for(const auto& P:Game.Pickups)Candidate.Pickups.Add({P.Position,P.Kind,P.bConsumed,P.RunGuid,P.ObjectId,P.SourceId,P.RoomInstanceId});
    Candidate.Audio.RunGuid=Game.ActionAudioState.RunGuid;Candidate.Audio.RoomInstanceId=Game.ActionAudioState.RoomInstanceId;
    Candidate.Audio.NextActionSequence=Game.ActionAudioState.NextSequence;
    Candidate.Audio.WorldHistoryThrough=Game.WeaponWorld.NextEventSequence?Game.WeaponWorld.NextEventSequence-1:0;
    for(const auto& Cursor:Game.ActionAudioWeaponCursors)Candidate.Audio.WeaponCursors.Add({Cursor.Key,Cursor.Value});
    Candidate.Audio.WeaponCursors.Sort([](const auto& A,const auto& B){return A.OwnerId<B.OwnerId;});
    for(const auto& F:Candidate.Fighters)if(F.Knight.IsSet())Candidate.Audio.StoneSeeds.Add({F.EntityId,F.Knight.GetValue().NextEventId});
    FDungeonValidatedRun Sealed;if(!Validate(Candidate,Sealed,Diagnostic))return false;
    Out=MoveTemp(Candidate);Diagnostic.Reset();return true;
}

bool FDungeonRunAggregate::Validate(const FDungeonRunSnapshot& Saved,FDungeonValidatedRun& Out,FString& Diagnostic)
{
    // All candidate owners are independent values. No live GameMode, Actor,
    // controller, World, event consumer or file operation is accessed here.
    const auto& S=Saved;const auto& V=S.Equipment.View;
    const bool HasGuard=S.Rewards.Schema==2||S.Fighters.ContainsByPredicate([](const auto& F){return F.Guard.IsSet();});
    if((HasGuard?(S.Schema!=2||S.Scope!=EDungeonRunScope::BoundDevelopmentV2)
                :(S.Schema!=1||S.Scope!=EDungeonRunScope::BoundDevelopmentV1))||!S.RunGuid.IsValid()||!S.OwnerId||!S.RoomInstanceId
        ||S.RoomNumber<=0||S.RoomInstanceId!=uint64(S.RoomNumber)||!FiniteTime(S.SimulationTime)
        ||!FMath::IsFinite(S.LastStoneWakeStartedAt)||(S.LastStoneWakeStartedAt!= -1.&&S.LastStoneWakeStartedAt<0.)||S.LastStoneWakeStartedAt>S.SimulationTime
        ||S.GameOver&&S.WaitingForStart||!V.Bound||V.RunGuid!=S.RunGuid||V.OwnerId!=S.OwnerId||V.RoomInstanceId!=S.RoomInstanceId)
        return Fail(Diagnostic,TEXT("Unknown complete Run schema/scope or root identity/clock/flags"));
    FString Why;FDungeonEquipmentRuntime Equipment;
    if(!Equipment.Restore(S.Equipment,Why))return OwnerFailure(Diagnostic,TEXT("Equipment"),Why);
    if(V.Action.ActionId&&V.Action.Start>S.SimulationTime||V.Action.Active&&S.SimulationTime>=V.Action.Deadline)
        return Fail(Diagnostic,TEXT("Equipment action conflicts with the complete Run clock"));
    for(const auto& R:S.Equipment.InventoryState.RuntimeUpdates)if(R.AtTime>S.SimulationTime)
        return Fail(Diagnostic,TEXT("Inventory contains a future runtime mutation"));
    if(S.Fighters.Num()!=S.EnemyOrder.Num()+1||S.Fighters.IsEmpty()||S.Fighters[0].EntityId!=S.OwnerId
        ||S.Fighters[0].Kind!=EDungeonFighterOwnerKind::BoundPlayer||!S.Fighters[0].Player.IsSet())
        return Fail(Diagnostic,TEXT("Complete Run has no unique first player and original enemy traversal order"));
    const auto& Player=S.Fighters[0];TSet<uint64> Ids;
    for(int32 I=0;I<S.Fighters.Num();++I)
    {
        const auto& F=S.Fighters[I];
        if(!F.EntityId||Ids.Contains(F.EntityId)||F.RunGuid!=S.RunGuid||F.RoomInstanceId!=S.RoomInstanceId
            ||(I>0&&(S.EnemyOrder[I-1]!=F.EntityId||F.Kind==EDungeonFighterOwnerKind::BoundPlayer)))
            return Fail(Diagnostic,TEXT("Current actors are duplicated, out of scope, reordered or missing"));
        Ids.Add(F.EntityId);
    }
    if(Player.Dead!=S.GameOver||Player.DeathReported!=Player.Dead)
        return Fail(Diagnostic,TEXT("Complete Run game-over state disagrees with the real player death fact"));
    FDungeonWeaponWorldRestoreContext WC;WC.RunGuid=S.RunGuid;WC.RoomInstanceId=S.RoomInstanceId;WC.OwnerId=S.OwnerId;
    WC.SimulationTime=S.SimulationTime;WC.PlayerActions=&Player.Player.GetValue().WeaponActions;
    FDungeonWeaponWorldState World;
    if(!DungeonWorldSnapshot::Restore(S.WeaponWorld,WC,World,Why))return OwnerFailure(Diagnostic,TEXT("WeaponWorld"),Why);
    FDungeonRunRewardValidationContext RC;RC.RunGuid=S.RunGuid;RC.OwnerId=S.OwnerId;RC.RoomInstanceId=S.RoomInstanceId;
    RC.SimulationTime=S.SimulationTime;RC.PlayerCoins=Player.Coins;RC.WeaponWorld=&World;
    for(const auto& F:S.Fighters)
    {
        FDungeonFighterRestoreContext FC;FC.RunGuid=S.RunGuid;FC.RoomInstanceId=S.RoomInstanceId;FC.EntityId=F.EntityId;
        FC.SimulationTime=S.SimulationTime;FC.GameOver=S.GameOver;FC.Equipment=&S.Equipment;FC.WeaponWorld=&World;FC.Rewards=&S.Rewards;
        if(!ADungeonFighter::ValidateOwnerSnapshot(F,FC,Why))return OwnerFailure(Diagnostic,TEXT("Fighter"),Why);
        RC.CurrentActors.Add(RewardActor(F));
        const double Wake=F.Knight.IsSet()?F.Knight.GetValue().WakeStartedAt:F.Bat.IsSet()?F.Bat.GetValue().WakeStartedAt:F.Guard.IsSet()?F.Guard.GetValue().Kernel.WakeStartedAt:-1.;
        if(Wake>S.LastStoneWakeStartedAt)return Fail(Diagnostic,TEXT("Global wake throttle precedes a current accepted stone wake"));
    }
    FDungeonRunRewards Rewards;if(!Rewards.Restore(S.Rewards,RC,Why))return OwnerFailure(Diagnostic,TEXT("Rewards"),Why);
    const bool HasClear=S.Rewards.Deaths.ContainsByPredicate([&](const auto& D)
        {return D.Death.RoomInstanceId==S.RoomInstanceId&&D.Death.RoomCleared;});
    if(S.RoomCleared!=HasClear)return Fail(Diagnostic,TEXT("Sticky room-clear flag differs from the original resolved last-enemy death"));
    int32 Index=0;
    for(const auto& Object:S.Rewards.Objects)if(Object.RoomInstanceId==S.RoomInstanceId)
    {
        if(!S.Pickups.IsValidIndex(Index))return Fail(Diagnostic,TEXT("Current physical pickups omitted an original resolved reward object"));
        const auto& P=S.Pickups[Index++];
        if(Object.Retired||P.RunGuid!=S.RunGuid||P.RoomInstanceId!=S.RoomInstanceId||P.ObjectId!=Object.ObjectId
            ||P.SourceId!=Object.SourceId||P.Position!=Object.Position||P.Kind!=PickupName(Object.Kind)||P.Kind.IsNone()||P.Consumed!=Object.Consumed)
            return Fail(Diagnostic,TEXT("Physical pickup projection/order/source/consumption differs from its stable resolved owner"));
    }
    if(Index!=S.Pickups.Num())return Fail(Diagnostic,TEXT("Unknown or historical physical pickup exists in the current room"));
    FDungeonSceneObjects Scene;if(!Scene.Restore(S.Scene,Why))return OwnerFailure(Diagnostic,TEXT("Scene"),Why);
    const auto& Room=S.Scene.CurrentRoom;const auto& Interaction=S.Scene.Interaction;
    if(S.Rewards.Schema==2&&(!Room.Active||V.Config!=EDungeonEquipmentRunConfig::FirstBatch
        ||S.Rewards.RoomPlans.ContainsByPredicate([&](const auto& P){return P.Seed!=V.CombatSeed;})))
        return Fail(Diagnostic,TEXT("Formal Bridge plan requires actual FirstBatch Scene and same immutable seed"));
    if(S.Geometry.Schema!=1||S.Geometry.Kind!=(Room.Active?EDungeonRunGeometryKind::SceneExplorationV1:EDungeonRunGeometryKind::FlatBoundsV1))
        return Fail(Diagnostic,TEXT("Unsupported reconstruction geometry or Scene scope mismatch"));
    if(Interaction.AtTime>S.SimulationTime||S.SceneCommitRequested!=(Interaction.Pending&&!Interaction.NeedsConfirmation))
        return Fail(Diagnostic,TEXT("Scene commit obligation disagrees with its accepted interaction/clock"));
    if(Room.Active)
    {
        const auto* Encounter=FindFighter(S,S.SceneEncounterEntityId);
        if(Room.RunGuid!=S.RunGuid||Room.RoomInstanceId!=S.RoomInstanceId||S.Scene.Rooms.Num()!=S.RoomNumber
            ||!Encounter||Encounter->Kind!=EDungeonFighterOwnerKind::StoneKnight)
            return Fail(Diagnostic,TEXT("Current Scene has an incomplete room lineage or missing real encounter owner"));
        for(uint64 I=1;I<=S.RoomInstanceId;++I)if(!S.Scene.Rooms.Contains(I))
            return Fail(Diagnostic,TEXT("Scene history omitted an admitted room"));
        // RoomCleared is sticky: a subsequent admitted bat may still be alive.
        // The original encounter itself must have produced the clear fact.
        if(S.RoomCleared&&(!Encounter->Dead||!Encounter->DeathReported))
            return Fail(Diagnostic,TEXT("Scene clear flag precedes its original encounter death"));
    }
    else if(S.SceneEncounterEntityId||S.SceneCommitRequested||S.SceneEquipmentTargetLost)
        return Fail(Diagnostic,TEXT("Inactive Scene retains an encounter or accepted Scene obligation"));
    FDungeonRunExploration Exploration;
    if(S.Exploration.RunGuid!=S.RunGuid||S.Exploration.CurrentRoomInstanceId!=S.RoomInstanceId
        ||S.Exploration.Rooms.Num()!=S.RoomNumber||!Exploration.Restore(S.Exploration,Why))
        return OwnerFailure(Diagnostic,TEXT("Exploration scope/history"),Why);
    if(!ValidateAudio(S,Why))return OwnerFailure(Diagnostic,TEXT("Audio continuation"),Why);
    // Only this immutable owning value is published after every owner passes.
    FDungeonValidatedRun Candidate;Candidate.Data=MakeShared<FDungeonRunSnapshot>(S);
    Out=MoveTemp(Candidate);Diagnostic.Reset();return true;
}
