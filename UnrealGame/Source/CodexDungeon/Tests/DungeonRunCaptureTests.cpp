#if WITH_DEV_AUTOMATION_TESTS
#include "Misc/AutomationTest.h"
#include "../DungeonRunAggregate.h"
#include "../DungeonFighter.h"
#include "../DungeonGameMode.h"
#include "Components/BoxComponent.h"
#include "Components/SceneComponent.h"
#include "Components/BrushComponent.h"
#include "Engine/Brush.h"
#include "Engine/Engine.h"
#include "Engine/GameInstance.h"
#include "Engine/World.h"
#include "EngineUtils.h"
#include "GameFramework/PlayerController.h"
#include "GameFramework/PlayerInput.h"
#include "InputCoreTypes.h"
#include "Kismet/GameplayStatics.h"
#include "PhysicsEngine/BodySetup.h"
#include <algorithm>
#include <cmath>
#include <limits>

namespace
{
bool SameFog(const FDungeonRunExplorationSnapshot& A,const FDungeonRunExplorationSnapshot& B)
{
    if(A.Schema!=B.Schema||A.RunGuid!=B.RunGuid||A.CurrentRoomInstanceId!=B.CurrentRoomInstanceId||A.Rooms.Num()!=B.Rooms.Num())return false;
    for(int32 I=0;I<A.Rooms.Num();++I)
    {
        const auto& X=A.Rooms[I];const auto& Y=B.Rooms[I];
        if(X.RoomInstanceId!=Y.RoomInstanceId||X.RoomNumber!=Y.RoomNumber||X.State.Schema!=Y.State.Schema
            ||X.State.RoomId!=Y.State.RoomId||X.State.Bounds.MinX!=Y.State.Bounds.MinX||X.State.Bounds.MaxX!=Y.State.Bounds.MaxX
            ||X.State.Bounds.MinY!=Y.State.Bounds.MinY||X.State.Bounds.MaxY!=Y.State.Bounds.MaxY||X.State.Memory!=Y.State.Memory)return false;
    }
    return true;
}
const FDungeonFighterOwnerSnapshot* Fighter(const FDungeonRunSnapshot& S,uint64 Id)
{return S.Fighters.FindByPredicate([Id](const auto& X){return X.EntityId==Id;});}
bool SameTransform(const FTransform& A,const FTransform& B)
{return A.GetTranslation()==B.GetTranslation()&&A.GetRotation()==B.GetRotation()&&A.GetScale3D()==B.GetScale3D();}
struct FCaptureWorld
{
    FAutomationTestBase& Test;
    UWorld* World=nullptr;ADungeonGameMode* Game=nullptr;ADungeonFighter* Player=nullptr;APlayerController* Controller=nullptr;
    explicit FCaptureWorld(FAutomationTestBase& T):Test(T){}
    ~FCaptureWorld(){if(World){World->DestroyWorld(false);if(GEngine)GEngine->DestroyWorldContext(World);}}
    bool Create()
    {
        if(!GEngine)return false;
        const auto Settings=UWorld::InitializationValues().AllowAudioPlayback(false).CreatePhysicsScene(true).RequiresHitProxies(false)
            .CreateNavigation(false).CreateAISystem(false).ShouldSimulatePhysics(false).SetTransactional(false);
        World=UWorld::CreateWorld(EWorldType::Game,false,NAME_None,nullptr,true,ERHIFeatureLevel::Num,&Settings);
        if(!World)return false;GEngine->CreateNewWorldContext(EWorldType::Game).SetCurrentWorld(World);
        World->SetGameInstance(NewObject<UGameInstance>(GEngine));FURL URL;URL.AddOption(TEXT("game=/Script/CodexDungeon.DungeonGameMode"));
        if(!World->SetGameMode(URL))return false;
        Game=World->GetAuthGameMode<ADungeonGameMode>();Player=World->SpawnActor<ADungeonFighter>();Controller=World->SpawnActor<APlayerController>();
        if(!Game||!Player||!Controller)return false;
        World->AddController(Controller);Controller->Possess(Player);
        if(!Controller->PlayerInput)Controller->PlayerInput=NewObject<UPlayerInput>(Controller);
        if(!Controller->IsLocalController()||UGameplayStatics::GetPlayerController(Game,0)!=Controller)return false;
        Game->PlayerFighter=Player;
        // One genuine new Run; no restore/reset shortcut or writable identity map.
        if(!Game->BeginSceneExplorationPreview()||Game->Enemies.Num()!=1||!Game->Enemies[0]->GetStoneKnightDriver())return false;
        Game->Enemies[0]->bAIEnabled=false; // Same explicit initial combat-AI control as the existing actual Scene tests.
        return Pulse(EKeys::Enter)&&!Game->bWaitingForStart&&BankAdmitted();
    }
    void Frame(float Dt)
    {
        Game->Tick(Dt);Controller->PlayerInput->Tick(Dt);TArray<UInputComponent*> Stack;
        Controller->PlayerInput->ProcessInputStack(Stack,Dt,false);
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
            float Dt=float(Left);if(double(Dt)>Left)Dt=std::nextafter(Dt,0.f);
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
    void Observe(const FDungeonRunSnapshot& S)
    {
        const auto& V=Game->GetEquipmentView();const auto& W=Game->GetWeaponWorldState();
        Test.TestTrue(TEXT("Aggregate root is the actual bound completed Run scope and master clock"),
            S.Schema==1&&S.Scope==EDungeonRunScope::BoundDevelopmentV1&&S.RunGuid==V.RunGuid
            &&S.OwnerId==V.OwnerId&&S.RoomInstanceId==V.RoomInstanceId&&S.RoomNumber==Game->RoomNumber
            &&S.SimulationTime==Game->GetSimulationTime()&&S.RoomCleared==Game->bRoomCleared
            &&S.GameOver==Game->bGameOver&&S.WaitingForStart==Game->bWaitingForStart&&S.LastMessage==Game->LastMessage);
        Test.TestTrue(TEXT("Complete owners retain equipment allocation/crit and authoritative world histories"),
            S.Equipment.HasInventory&&S.Equipment.View.RunGuid==V.RunGuid&&S.Equipment.View.Revision==V.Revision
            &&S.Equipment.View.NextInstanceId==V.NextInstanceId&&S.Equipment.View.NextOperationId==V.NextOperationId
            &&S.Equipment.View.NextCritDraw==V.NextCritDraw&&S.Equipment.InventoryState.Operations.size()==Game->GetEquipmentInventoryState()->Operations.size()
            &&S.WeaponWorld.Schema==1&&S.WeaponWorld.State.RunGuid==W.RunGuid&&S.WeaponWorld.State.Time==W.Time
            &&S.WeaponWorld.State.ActorBindings.Num()==W.ActorBindings.Num()&&S.WeaponWorld.State.NextEntityId==W.NextEntityId
            &&S.WeaponWorld.State.NextEventSequence==W.NextEventSequence&&S.WeaponWorld.State.Events.Num()==W.Events.Num()
            &&S.WeaponWorld.State.Projectiles.Num()==W.Projectiles.Num()&&S.WeaponWorld.State.HitReceipts.Num()==W.HitReceipts.Num()
            &&S.WeaponWorld.State.Burns.Num()==W.Burns.Num());
        Test.TestTrue(TEXT("Actual Scene/layout/interaction and real bank are captured without an empty substitute"),
            S.Geometry.Schema==1&&S.Geometry.Kind==EDungeonRunGeometryKind::SceneExplorationV1
            &&S.Scene.CurrentRoom.RunGuid==Game->GetSceneRoomView().RunGuid
            &&S.Scene.CurrentRoom.RoomInstanceId==Game->GetSceneRoomView().RoomInstanceId
            &&S.Scene.CurrentRoom.Layout.Entry==Game->GetSceneRoomView().Layout.Entry
            &&S.Scene.Interaction.Pending==Game->GetSceneInteractionView().Pending
            &&SameFog(S.Exploration,Game->CaptureRunExplorationSnapshot()));
        const auto& AcceptedScene=Game->GetSceneInteractionView();
        Test.TestTrue(TEXT("Completed normal Tick retains the real Scene commit obligation and cleared input-generation target-loss marker"),
            S.SceneCommitRequested==(AcceptedScene.Pending&&!AcceptedScene.NeedsConfirmation)&&!S.SceneEquipmentTargetLost);
        Test.TestTrue(TEXT("All current actors and their real traversal order include dead actors"),
            S.Fighters.Num()==Game->Enemies.Num()+1&&S.EnemyOrder.Num()==Game->Enemies.Num());
        const auto CheckActor=[&](ADungeonFighter* Actor)
        {
            const auto* Saved=Fighter(S,Actor->GetRuntimeEntityId());auto* Muzzle=Actor->GetWeaponMuzzleComponent();
            Test.TestTrue(TEXT("Owner capture retains actual Schema2 body/HP/terminal/native anchor values"),
                Saved&&Saved->Schema==2&&Saved->GroundPosition==Actor->GetGroundPosition()&&Saved->Health==Actor->Health
                &&Saved->JumpHeight==Actor->JumpHeight&&Saved->Dead==Actor->bDead&&Saved->DeathReported==Actor->bDeathReported
                &&Muzzle&&Muzzle->GetAttachParent()&&SameTransform(Saved->HeightAnchorRelative,Muzzle->GetAttachParent()->GetRelativeTransform()));
        };
        CheckActor(Player);
        for(int32 I=0;I<Game->Enemies.Num();++I)
        {CheckActor(Game->Enemies[I]);if(S.EnemyOrder.IsValidIndex(I))Test.TestEqual(TEXT("Enemy order is the original actor array order"),S.EnemyOrder[I],Game->Enemies[I]->GetRuntimeEntityId());}
        Test.TestEqual(TEXT("Complete native pickup projection keeps current physical order, including consumed"),S.Pickups.Num(),Game->Pickups.Num());
        for(int32 I=0;I<S.Pickups.Num()&&I<Game->Pickups.Num();++I)
        {
            const auto& A=S.Pickups[I];const auto& B=Game->Pickups[I];
            Test.TestTrue(TEXT("Stable pickup identity/kind/position/consumption is copied at its original index"),
                A.RunGuid==B.RunGuid&&A.ObjectId==B.ObjectId&&A.SourceId==B.SourceId&&A.RoomInstanceId==B.RoomInstanceId
                &&A.Kind==B.Kind&&A.Position==B.Position&&A.Consumed==B.bConsumed);
        }
        const auto R=Game->CaptureRunRewardsSnapshot();
        Test.TestTrue(TEXT("Reward owner carries real wallet operations and retired death/source history"),
            S.Rewards.RunGuid==R.RunGuid&&S.Rewards.CurrentRoomInstanceId==R.CurrentRoomInstanceId
            &&S.Rewards.NextSourceId==R.NextSourceId&&S.Rewards.NextOperationId==R.NextOperationId
            &&S.Rewards.Deaths.Num()==R.Deaths.Num()&&S.Rewards.Objects.Num()==R.Objects.Num()
            &&S.Rewards.Collections.Num()==R.Collections.Num()&&S.Rewards.RetiredEntities.Num()==R.RetiredEntities.Num());
        Test.TestTrue(TEXT("Audio contains future-phase adapter cursors and consumed-history tail seeds without sound queues"),
            S.Audio.Schema==1&&S.Audio.RunGuid==V.RunGuid&&S.Audio.RoomInstanceId==V.RoomInstanceId
            &&S.Audio.NextActionSequence==Game->GetActionAudioState().NextSequence
            &&S.Audio.WorldHistoryThrough==W.NextEventSequence-1
            &&S.Audio.WeaponCursors.ContainsByPredicate([&](const auto& X){return X.OwnerId==V.OwnerId&&X.Cursor.Attached;}));
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

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRunCaptureAccepted,
    "CodexDungeon.Content.RunCapture.AcceptedMeleePickupAndReload",
    EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FRunCaptureAccepted::RunTest(const FString&)
{
    FCaptureWorld F(*this);if(!TestTrue(TEXT("Genuine Scene/Enter and completed-tick bank fixture"),F.Create()))return false;
    if(!TestTrue(TEXT("Normal J begins accepted starter melee"),F.Pulse(EKeys::J)&&F.Player->GetMeleeCombatState().Action.Active))return false;
    const auto M=F.Player->GetMeleeCombatState().Action;
    if(!TestTrue(TEXT("Real melee reaches lock before capture"),F.AdvanceTo(M.LockTime)))return false;
    FDungeonRunSnapshot Melee;
    if(F.Capture(TEXT("Capture accepts real locked melee without an idle restriction"),Melee))
    {
        F.Observe(Melee);const auto* P=Fighter(Melee,F.Player->GetRuntimeEntityId());
        TestTrue(TEXT("Melee action/accepted crit draw and queued obligations are the real owner values"),
            P&&P->Player.IsSet()&&P->Player.GetValue().Combat.Action.Active&&P->Player.GetValue().Combat.Action.Locked
            &&P->Player.GetValue().Combat.Action.AttackId==M.AttackId&&P->Player.GetValue().Combat.Action.End==M.End
            &&Melee.Equipment.View.NextCritDraw==F.Game->GetEquipmentView().NextCritDraw&&Melee.Equipment.CritReceipts.Num()==1);
    }
    if(!TestTrue(TEXT("Original melee normally finishes before a new exclusive action"),F.AdvanceTo(M.End)))return false;
    if(!TestTrue(TEXT("Fresh Shift starts genuine accepted dodge"),F.Pulse(EKeys::LeftShift)
        &&F.Player->GetDodgeState().Phase==DungeonDodge::EPhase::Dodging))return false;
    const auto DodgeStart=F.Player->GetDodgeState().Records.back().Start;
    if(!TestTrue(TEXT("Normal timeline reaches actual dodge protection before capture"),F.AdvanceTo(DodgeStart+.1)
        &&F.Player->IsDodgeInvulnerableAt(F.Game->GetSimulationTime())))return false;
    FDungeonRunSnapshot Dodge;
    if(F.Capture(TEXT("Capture preserves an accepted protected dodge"),Dodge))
    {
        F.Observe(Dodge);const auto* P=Fighter(Dodge,F.Player->GetRuntimeEntityId());
        TestTrue(TEXT("Saved dodge position/records are current protected kernel values"),
            P&&P->Player.IsSet()&&P->Player.GetValue().Dodge.Phase==DungeonDodge::EPhase::Dodging
            &&P->Player.GetValue().Dodge.Records.size()==F.Player->GetDodgeState().Records.size());
    }
    if(!TestTrue(TEXT("Real dodge finishes normally"),F.AdvanceTo(F.Player->GetDodgeState().Records.back().End)))return false;
    DungeonEquipmentInventory::FItem Crossbow;Crossbow.ContentId="WPN-XBW-001";Crossbow.Ammo=0.;
    const auto X=F.Game->RegisterEquipmentSource(TEXT("run.capture.actual.crossbow"),Crossbow,F.Player->GetGroundPosition()+FVector2D(30.,0.),true);
    if(!TestTrue(TEXT("Real source registration and fresh E start accepted empty-slot pickup"),X.Ok()&&F.Pulse(EKeys::E)
        &&F.Game->GetEquipmentView().Action.Active))return false;
    const auto E=F.Game->GetEquipmentView().Action;
    if(!TestTrue(TEXT("Real pickup reaches a still-pending middle point"),F.AdvanceTo(E.Start+.125)))return false;
    FDungeonRunSnapshot Pickup;
    if(F.Capture(TEXT("Capture keeps accepted pending equipment transaction before commit"),Pickup))
    {
        F.Observe(Pickup);
        TestTrue(TEXT("Original plan/source/reserved IDs are retained without granting the pending weapon"),
            Pickup.Equipment.View.Action.Active&&Pickup.Equipment.PendingPlan.SourceId==X.SourceId
            &&Pickup.Equipment.PendingPlan.InstanceId==X.InstanceId&&Pickup.Equipment.InventoryState.Weapons[1]==0
            &&Pickup.Equipment.View.Action.Deadline==E.Deadline);
    }
    if(!TestTrue(TEXT("Pickup finishes then normal T begins actual empty-magazine reload"),F.AdvanceTo(E.Deadline)
        &&F.Player->WeaponId==TEXT("WPN-XBW-001")&&F.Pulse(EKeys::T)
        &&F.Player->GetWeaponActionsState().Action.Type==DungeonWeaponActions::EAction::Reload))return false;
    const auto Reload=F.Player->GetWeaponActionsState().Action;
    F.Player->GetWeaponMuzzleComponent()->SetRelativeLocation(FVector(24.,7.,65.));
    if(!TestTrue(TEXT("Real central timeline reaches post-insert/pre-complete reload"),F.AdvanceTo(Reload.Start+.65)
        &&F.Player->GetWeaponActionsState().Action.Active&&F.Game->GetActionAudioState().NextSequence>=3))return false;
    FDungeonRunSnapshot Loading;
    if(F.Capture(TEXT("Capture preserves reload obligation and actual custom native muzzle"),Loading))
    {
        F.Observe(Loading);const auto* P=Fighter(Loading,F.Player->GetRuntimeEntityId());
        const auto* C=Loading.Audio.WeaponCursors.FindByPredicate([&](const auto& Q){return Q.OwnerId==F.Player->GetRuntimeEntityId();});
        TestTrue(TEXT("Elapsed draw/insert are consumed while original reload completion remains pending"),
            P&&P->Player.IsSet()&&P->Player.GetValue().WeaponActions.Action.ActionId==Reload.ActionId
            &&P->Player.GetValue().WeaponActions.Action.End==Reload.End&&C&&C->Cursor.DrawObserved&&C->Cursor.InsertObserved
            &&C->Cursor.Reload.ActionId==Reload.ActionId&&C->Cursor.Reload.End==Reload.End);
        TestTrue(TEXT("Custom numerical native origin is preserved instead of derived from a default pose"),
            P&&P->CustomMuzzle&&SameTransform(P->CustomMuzzleRelative,F.Player->GetWeaponMuzzleComponent()->GetRelativeTransform()));
    }
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRunCaptureHistory,
    "CodexDungeon.Content.RunCapture.DeadActorsAndCrossRoomRewards",
    EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FRunCaptureHistory::RunTest(const FString&)
{
    FCaptureWorld F(*this);if(!TestTrue(TEXT("Actual Scene/normal J death/automatic coin fixture"),F.Create()&&F.KillKnight()))return false;
    const uint64 Old=F.Game->Enemies[0]->GetRuntimeEntityId();const auto Run=F.Game->GetEquipmentView().RunGuid;
    FDungeonRunSnapshot Dead;
    const bool CapturedDead=F.Capture(TEXT("Capture includes the actual still-current dead knight and all ground objects"),Dead);
    if(CapturedDead)
    {
        F.Observe(Dead);const auto* K=Fighter(Dead,Old);
        TestTrue(TEXT("Death is not filtered or converted to a live spawn and coin receipt is retained"),
            K&&K->Dead&&K->DeathReported&&K->Knight.IsSet()&&K->Knight.GetValue().RewardClaimed
            &&Dead.Fighters.Num()==2&&Dead.Rewards.Objects.Num()==3&&Dead.Rewards.Collections.Num()==1
            &&Dead.Pickups.Num()==3&&Dead.Pickups[0].Consumed&&Dead.SceneEncounterEntityId==Old);
    }
    if(!TestTrue(TEXT("Normal E/Enter really moves the same Run to Room2 and preserves5 coins"),
        F.ReachExit()&&F.Pulse(EKeys::Enter)&&F.Game->RoomNumber==2
        &&F.Game->GetEquipmentView().RunGuid==Run&&F.Player->Coins==5&&F.BankAdmitted()))return false;
    FDungeonRunSnapshot Next;
    if(F.Capture(TEXT("Capture after actual transfer preserves current and historical scopes"),Next))
    {
        F.Observe(Next);const auto New=F.Game->Enemies[0]->GetRuntimeEntityId();
        TestTrue(TEXT("Old binding/dead tombstone survives while only the two actual current actors are saved"),
            Next.Fighters.Num()==2&&!Fighter(Next,Old)&&Fighter(Next,New)&&Next.EnemyOrder.Num()==1&&Next.EnemyOrder[0]==New
            &&Next.WeaponWorld.State.ActorBindings.Num()==3&&Next.Rewards.RetiredEntities.Num()==1
            &&Next.Rewards.RetiredEntities[0].Actor.EntityId==Old&&Next.Rewards.RetiredEntities[0].Actor.Dead
            &&Next.Rewards.Objects.Num()==3&&Next.Rewards.Objects[0].Retired&&Next.Rewards.Objects[0].Consumed
            &&Next.Rewards.Collections.Num()==1&&Next.Pickups.IsEmpty()&&Next.Exploration.Rooms.Num()==2);
        if(CapturedDead)TestEqual(TEXT("Global historical wake marker survives the transfer despite a new dormant knight"),Next.LastStoneWakeStartedAt,Dead.LastStoneWakeStartedAt);
        FDungeonValidatedRun Validated;FString Why;
        const bool Valid=FDungeonRunAggregate::Validate(Next,Validated,Why);
        if(!Valid)AddInfo(TEXT("Whole cross-room candidate diagnosis: ")+Why);
        TestTrue(TEXT("Pure whole-root validator accepts real source history with the player's old birth binding"),Valid&&Validated.IsValid());
    }
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRunCaptureFog,
    "CodexDungeon.Content.RunCapture.ExactExplorationAndReadOnlyCapture",
    EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FRunCaptureFog::RunTest(const FString&)
{
    FCaptureWorld F(*this);if(!TestTrue(TEXT("Actual bound bank admitted by completed ticks"),F.Create()))return false;
    if(!TestTrue(TEXT("Normal west bypass reaches the real survey area without a fake Reveal"),F.Move(300.,false)&&F.Move(-920.,true)&&F.BankAdmitted()))return false;
    const auto Bank=F.Game->CaptureRunExplorationSnapshot();const double At=F.Game->GetSimulationTime();
    const auto Position=F.Player->GetGroundPosition();const auto Draw=F.Game->GetEquipmentView().NextCritDraw;
    FDungeonRunSnapshot A,B;
    const bool First=F.Capture(TEXT("Capture owns every actual fog memory double"),A);
    const bool Second=F.Capture(TEXT("Repeated Capture observes the same completed boundary"),B);
    if(First&&Second)
    {
        F.Observe(A);F.Observe(B);
        TestTrue(TEXT("Capture neither reveals, steps, draws RNG nor resets historical exploration"),
            SameFog(A.Exploration,Bank)&&SameFog(B.Exploration,Bank)&&SameFog(Bank,F.Game->CaptureRunExplorationSnapshot())
            &&F.Game->GetSimulationTime()==At&&F.Player->GetGroundPosition()==Position&&F.Game->GetEquipmentView().NextCritDraw==Draw);
    }
    if(!TestTrue(TEXT("Actual normal return path continues observations"),F.Move(-1180.,true)&&F.Move(0.,false)))return false;
    const auto Later=F.Game->CaptureRunExplorationSnapshot();
    if(First)TestTrue(TEXT("Earlier captured bank is a deep owning value unaffected by later real movement"),SameFog(A.Exploration,Bank));
    TestTrue(TEXT("Real current-room memory never loses an earlier observed vertex"),Later.Rooms.Num()==Bank.Rooms.Num()
        &&Later.Rooms[0].State.Memory.size()==Bank.Rooms[0].State.Memory.size());
    if(Later.Rooms.Num()==Bank.Rooms.Num()&&Later.Rooms[0].State.Memory.size()==Bank.Rooms[0].State.Memory.size())
        for(std::size_t I=0;I<Bank.Rooms[0].State.Memory.size();++I)
            if(Later.Rooms[0].State.Memory[I]<Bank.Rooms[0].State.Memory[I]){AddError(TEXT("Completed-tick exploration lost observed memory"));break;}
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRunCaptureReject,
    "CodexDungeon.Content.RunCapture.WholeCandidateRejectionIsAtomic",
    EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FRunCaptureReject::RunTest(const FString&)
{
    FCaptureWorld F(*this);if(!TestTrue(TEXT("Genuine nonempty dead/reward/fog source fixture"),F.Create()&&F.KillKnight()))return false;
    FDungeonRunSnapshot Saved;
    if(!F.Capture(TEXT("Whole-root rejection uses a real captured baseline"),Saved))return false;
    if(!TestTrue(TEXT("Independent captured baseline retains the actual two actors, enemy, coin/potion/axe"),
        Saved.Fighters.Num()==2&&Saved.EnemyOrder.Num()==1&&Saved.Pickups.Num()==3))return false;
    FDungeonValidatedRun Sealed;FString Why;
    if(!TestTrue(TEXT("Pure validator seals a complete real baseline"),FDungeonRunAggregate::Validate(Saved,Sealed,Why)&&Sealed.IsValid()))
    {AddInfo(TEXT("Valid whole candidate diagnosis: ")+Why);return false;}
    const auto* Original=Sealed.Get();const auto Bank=F.Game->CaptureRunExplorationSnapshot();
    const auto At=F.Game->GetSimulationTime();const auto Draw=F.Game->GetEquipmentView().NextCritDraw;
    const auto Reject=[&](const TCHAR* Label,auto Mutate)
    {
        auto Bad=Saved;Mutate(Bad);FString Invalid;
        TestFalse(*(FString(Label)+TEXT(" rejected as a whole")),FDungeonRunAggregate::Validate(Bad,Sealed,Invalid));
        TestTrue(*(FString(Label)+TEXT(" leaves the sealed original and real source unchanged")),
            !Invalid.IsEmpty()&&Sealed.Get()==Original&&F.Game->GetSimulationTime()==At
            &&F.Game->GetEquipmentView().NextCritDraw==Draw&&SameFog(Bank,F.Game->CaptureRunExplorationSnapshot())&&F.Player->Coins==5);
    };
    Reject(TEXT("Unknown complete Run schema"),[](auto& S){S.Schema=99;});
    Reject(TEXT("Mismatched enclosing Run"),[](auto& S){S.RunGuid.Invalidate();});
    Reject(TEXT("Wrong enclosing room"),[](auto& S){++S.RoomInstanceId;});
    Reject(TEXT("Duplicated enemy traversal identity"),[](auto& S){const uint64 Id=S.EnemyOrder[0];S.EnemyOrder.Add(Id);});
    Reject(TEXT("Missing current dead owner"),[](auto& S){S.Fighters.RemoveAt(1);});
    Reject(TEXT("Unknown old fighter schema lacking actual native anchor"),[](auto& S){S.Fighters[0].Schema=1;});
    Reject(TEXT("Nonfinite actual native anchor"),[](auto& S){S.Fighters[0].HeightAnchorRelative.SetTranslation(FVector(0.,0.,std::numeric_limits<double>::quiet_NaN()));});
    Reject(TEXT("Consumed coin without the original wallet receipt"),[](auto& S){S.Rewards.Collections.Reset();});
    Reject(TEXT("Wrong physical source projection identity"),[](auto& S){++S.Pickups[0].SourceId;});
    Reject(TEXT("Missing observed bank history cannot become default empty fog"),[](auto& S){S.Exploration.Rooms.Reset();});
    Reject(TEXT("Invalid audio consumed-history sequence"),[](auto& S){S.Audio.NextActionSequence=0;});
    Reject(TEXT("Unknown reconstruction geometry"),[](auto& S){S.Geometry.Kind=EDungeonRunGeometryKind::Unsupported;});
    // The actual authored barrier's full native response container remains an
    // exact gate: changing a real stored channel must still reject Capture.
    UBoxComponent* ActualBarrier=nullptr;
    const auto& BarrierBounds=F.Game->GetSceneRoomView().Layout.Barrier;
    const auto BarrierCenter=BarrierBounds.GetCenter(),BarrierHalf=BarrierBounds.GetExtent();
    for(TActorIterator<AActor> It(F.World);It;++It)
    {
        auto CandidateBarrier=Cast<UBoxComponent>(It->GetRootComponent());
        if(CandidateBarrier&&It->GetActorLocation()==FVector(BarrierCenter.X,BarrierCenter.Y,40.)
            &&CandidateBarrier->GetUnscaledBoxExtent()==FVector(BarrierHalf.X,BarrierHalf.Y,80.)
            &&CandidateBarrier->GetCollisionObjectType()==ECC_WorldStatic)
        {
            if(ActualBarrier){AddError(TEXT("Actual authored Scene barrier is ambiguous"));return false;}
            ActualBarrier=CandidateBarrier;
        }
    }
    if(!TestNotNull(TEXT("Normal Scene owns its actual native barrier"),ActualBarrier))return false;
    const auto NativeResponses=ActualBarrier->GetCollisionResponseToChannels();
    if(!TestTrue(TEXT("Baseline actual barrier blocks every stored native channel"),NativeResponses==FCollisionResponseContainer(ECR_Block)))return false;
    ActualBarrier->SetCollisionResponseToChannel(ECC_Visibility,ECR_Ignore);
    auto ChannelOutput=Saved;FString ChannelWhy;
    TestFalse(TEXT("Actual Visibility Ignore refuses Capture without weakening any native stored channel"),F.Game->CaptureRunSnapshot(ChannelOutput,ChannelWhy));
    TestTrue(TEXT("Refused real response mutation retains the original output and live Run memory/time/resources"),
        !ChannelWhy.IsEmpty()&&ChannelOutput.RunGuid==Saved.RunGuid&&ChannelOutput.SimulationTime==Saved.SimulationTime
        &&ChannelOutput.EnemyOrder==Saved.EnemyOrder&&SameFog(ChannelOutput.Exploration,Saved.Exploration)
        &&ChannelOutput.Audio.NextActionSequence==Saved.Audio.NextActionSequence&&F.Game->GetSimulationTime()==At
        &&F.Game->GetEquipmentView().NextCritDraw==Draw&&F.Player->Coins==5&&SameFog(Bank,F.Game->CaptureRunExplorationSnapshot()));
    ActualBarrier->SetCollisionResponseToChannels(NativeResponses);
    FDungeonRunSnapshot RestoredResponses;
    if(!F.Capture(TEXT("Restoring exactly the original native barrier responses admits Capture again"),RestoredResponses))return false;
    F.Observe(RestoredResponses);
    auto DefaultBuilder=F.World->GetDefaultBrush();
    if(!TestNotNull(TEXT("The actual World retains its native default builder"),DefaultBuilder))return false;
    auto DefaultBrushComponent=DefaultBuilder->GetBrushComponent();
    if(!TestNotNull(TEXT("The native default builder owns its actual brush component"),DefaultBrushComponent))return false;
    const auto OriginalBodySetup=DefaultBrushComponent->BrushBodySetup;
    if(!TestTrue(TEXT("Actual known default builder has no game BodySetup"),OriginalBodySetup==nullptr))return false;
    auto AddedSetup=NewObject<UBodySetup>(DefaultBrushComponent);
    if(!TestNotNull(TEXT("Independent unsupported BodySetup control"),AddedSetup))return false;
    DefaultBrushComponent->BrushBodySetup=AddedSetup; // No physics/model build or gameplay event is invoked.
    auto BuilderOutput=Saved;FString BuilderWhy;
    TestFalse(TEXT("Even the exact default builder with a real BodySetup refuses Capture"),F.Game->CaptureRunSnapshot(BuilderOutput,BuilderWhy));
    TestTrue(TEXT("Refused builder body preserves output and all observed live Run facts without removing the supplied body"),
        !BuilderWhy.IsEmpty()&&BuilderOutput.RunGuid==Saved.RunGuid&&BuilderOutput.SimulationTime==Saved.SimulationTime
        &&BuilderOutput.EnemyOrder==Saved.EnemyOrder&&SameFog(BuilderOutput.Exploration,Saved.Exploration)
        &&BuilderOutput.Audio.NextActionSequence==Saved.Audio.NextActionSequence&&F.Game->GetSimulationTime()==At
        &&F.Game->GetEquipmentView().NextCritDraw==Draw&&F.Player->Coins==5&&SameFog(Bank,F.Game->CaptureRunExplorationSnapshot())
        &&DefaultBrushComponent->BrushBodySetup==AddedSetup);
    DefaultBrushComponent->BrushBodySetup=OriginalBodySetup;
    FDungeonRunSnapshot RestoredBuilder;
    if(!F.Capture(TEXT("Restoring the native empty builder BodySetup admits Capture again"),RestoredBuilder))return false;
    F.Observe(RestoredBuilder);
    auto Extra=F.World->SpawnActor<AActor>();if(!TestNotNull(TEXT("Independent foreign collision actor"),Extra))return false;
    auto Box=NewObject<UBoxComponent>(Extra);if(!TestNotNull(TEXT("Actual foreign collision component"),Box))return false;
    Extra->SetRootComponent(Box);
    Box->SetBoxExtent(FVector(2.,2.,80.));Box->SetCollisionEnabled(ECollisionEnabled::QueryOnly);
    Box->SetCollisionObjectType(ECC_WorldStatic);Box->SetCollisionResponseToAllChannels(ECR_Block);Box->RegisterComponentWithWorld(F.World);
    Extra->SetActorLocation(FVector(-600.,300.,40.));
    auto Output=Saved;FString Unsupported;
    TestFalse(TEXT("Capture refuses an unknown real collision object instead of silently discarding it"),F.Game->CaptureRunSnapshot(Output,Unsupported));
    TestTrue(TEXT("Rejected capture retains its previous real output scope and complete observed fog"),
        !Unsupported.IsEmpty()&&Output.RunGuid==Saved.RunGuid&&Output.SimulationTime==Saved.SimulationTime
        &&Output.EnemyOrder==Saved.EnemyOrder&&SameFog(Output.Exploration,Saved.Exploration));
    Extra->SetActorEnableCollision(false);Extra->Destroy();
    // Actual Scene Spawn occurs inside the normal Enter Tick. This callback
    // observes the public capture gate; it does not alter any gameplay facts.
    bool SawSpawn=false,RejectedHalfTick=true;FString BoundaryWhy;
    const auto Handle=F.World->AddOnActorSpawnedHandler(FOnActorSpawned::FDelegate::CreateLambda([&](AActor*)
    {
        SawSpawn=true;FDungeonRunSnapshot Mid=Saved;
        RejectedHalfTick&=!F.Game->CaptureRunSnapshot(Mid,BoundaryWhy)&&Mid.RunGuid==Saved.RunGuid
            &&Mid.SimulationTime==Saved.SimulationTime&&SameFog(Mid.Exploration,Saved.Exploration);
    }));
    const bool Entered=F.ReachExit()&&F.Pulse(EKeys::Enter);
    F.World->RemoveOnActorSpawnedHandler(Handle);
    TestTrue(TEXT("Real normal transfer rejects reentrant capture during an incomplete Tick"),
        Entered&&SawSpawn&&RejectedHalfTick&&!BoundaryWhy.IsEmpty());
    return true;
}
#endif
