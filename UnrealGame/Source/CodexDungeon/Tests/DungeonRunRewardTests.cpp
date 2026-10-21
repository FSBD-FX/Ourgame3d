#if WITH_DEV_AUTOMATION_TESTS
#include "Misc/AutomationTest.h"
#include "../DungeonRunRewards.h"
#include "../DungeonFighter.h"
#include "../DungeonGameMode.h"
#include "Components/BoxComponent.h"
#include "CollisionQueryParams.h"
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
using RS=FDungeonRunRewardSnapshot;
// Independent full value proof: no production encoder, C++ padding or pointers.
struct FRewardProof
{
    TArray<uint8> Bytes;
    template<class T>void One(T X){static_assert(std::is_arithmetic_v<T>||std::is_enum_v<T>);Bytes.Append(reinterpret_cast<const uint8*>(&X),sizeof(X));}
    template<class... T>void V(T... X){(One(X),...);}
    void Text(const FString& S){FTCHARToUTF8 U(*S);V(uint64(U.Length()));Bytes.Append(reinterpret_cast<const uint8*>(U.Get()),U.Length());}
    void Point(FVector2D P){V(P.X,P.Y);}
    void Actor(const FDungeonRunRewardActorFact& A)
    {V(A.EntityId,A.RoomInstanceId);Text(A.ContentId);V(A.Enemy,A.Dead,A.DeathReported,A.RewardClaimed);}
    void Ids(const TArray<uint64>& X){V(X.Num());for(uint64 Id:X)V(Id);}
    explicit FRewardProof(const RS& S)
    {
        V(S.Schema,S.Bound,S.RunGuid.A,S.RunGuid.B,S.RunGuid.C,S.RunGuid.D,S.OwnerId,S.CurrentRoomInstanceId,
            S.NextSourceId,S.NextObjectId,S.NextOperationId,S.InitialCoins);
        V(S.Deaths.Num());for(const auto& D:S.Deaths)
        {V(D.Death.EntityId,D.Death.RoomInstanceId);Text(D.Death.ContentId);V(D.Death.AtTime);Point(D.Death.Position);
            V(D.Death.FirstDeath,D.Death.RoomCleared);Ids(D.SourceIds);}
        V(S.Sources.Num());for(const auto& X:S.Sources)V(X.SourceId,X.ObjectId,X.EntityId,X.RoomInstanceId,X.Kind,X.AtTime);
        V(S.Objects.Num());for(const auto& X:S.Objects)
        {V(X.ObjectId,X.SourceId,X.RoomInstanceId,X.Kind);Point(X.Position);V(X.ResolvedAmount,X.Consumed,X.Retired,X.CollectionOperationId,X.RetiredAt);}
        V(S.Collections.Num());for(const auto& C:S.Collections)
        {const auto& Q=C.Request;V(Q.OperationId,Q.ObjectId,Q.SourceId,Q.OwnerId,Q.RoomInstanceId,Q.AtTime,Q.BeforeCoins,C.AfterCoins);}
        V(S.RetiredEntities.Num());for(const auto& R:S.RetiredEntities){Actor(R.Actor);V(R.RetiredAt);}
        V(S.RoomExits.Num());for(const auto& E:S.RoomExits){V(E.RoomInstanceId,E.NextRoomInstanceId,E.AtTime);Ids(E.EntityIds);Ids(E.ObjectIds);}
    }
};
bool SameReward(const RS& A,const RS& B){return FRewardProof(A).Bytes==FRewardProof(B).Bytes;}
const FDungeonRunRewardObject* Reward(const RS& S,uint64 Id)
{return S.Objects.FindByPredicate([Id](const auto& X){return X.ObjectId==Id;});}
struct FRunRewardFixture
{
    FAutomationTestBase& Test;
    UWorld* World=nullptr;
    ADungeonGameMode* Game=nullptr;
    ADungeonFighter* Player=nullptr;
    APlayerController* Controller=nullptr;
    explicit FRunRewardFixture(FAutomationTestBase& InTest):Test(InTest){}
    ~FRunRewardFixture()
    {if(World){World->DestroyWorld(false);if(GEngine)GEngine->DestroyWorldContext(World);}}
    void Trace(const FString& Label)const
    {
        if(!Game||!Player)return;
        const auto P=Player->GetGroundPosition();const auto& A=Player->GetMeleeCombatState().Action;
        const FString Head=FString::Printf(TEXT("RunRewards [%s] room=%llu sim=%.17g P=(%.17g,%.17g) HP=%.17g jump=%.17g velocity=%.17g coins=%d cleared=%d gameover=%d action=%llu active=%d air=%d start=%.17g activeAt=%.17g end=%.17g"),
            *Label,static_cast<unsigned long long>(Game->GetEquipmentView().RoomInstanceId),Game->GetSimulationTime(),
            P.X,P.Y,double(Player->Health),double(Player->JumpHeight),double(Player->GetVerticalVelocity()),Player->Coins,
            Game->bRoomCleared,Game->bGameOver,static_cast<unsigned long long>(A.AttackId),A.Active,A.StartedAirborne,A.Start,A.ActiveStart,A.End);
        Test.AddInfo(Head);UE_LOG(LogTemp,Display,TEXT("%s"),*Head);
        for(auto Actor:Game->Enemies)if(IsValid(Actor)&&Actor->GetStoneKnightDriver())
        {
            const auto Body=Actor->GetGroundPosition();const auto& K=Actor->GetStoneKnightDriver()->State();
            const FString Enemy=FString::Printf(TEXT("RunRewards [%s] K=%llu body=(%.17g,%.17g) kernel=(%.17g,%.17g) time=%.17g phase=%u HP=%.17g mirrorHP=%.17g dead=%d reported=%d claimed=%d AI=%d"),
                *Label,static_cast<unsigned long long>(Actor->GetRuntimeEntityId()),Body.X,Body.Y,K.Position.X,K.Position.Y,K.Time,
                unsigned(K.Phase),K.HP,double(Actor->Health),Actor->bDead,Actor->bDeathReported,K.RewardClaimed,Actor->bAIEnabled);
            Test.AddInfo(Enemy);UE_LOG(LogTemp,Display,TEXT("%s"),*Enemy);
        }
        const auto* Coin=Pickup(TEXT("coin"));
        if(Coin)
        {
            const auto D=P-Coin->Position;
            const FString Ground=FString::Printf(TEXT("RunRewards [%s] coin=(%.17g,%.17g) delta=(%.17g,%.17g) consumed=%d object=%llu source=%llu room=%llu"),
                *Label,Coin->Position.X,Coin->Position.Y,D.X,D.Y,Coin->bConsumed,static_cast<unsigned long long>(Coin->ObjectId),
                static_cast<unsigned long long>(Coin->SourceId),static_cast<unsigned long long>(Coin->RoomInstanceId));
            Test.AddInfo(Ground);UE_LOG(LogTemp,Display,TEXT("%s"),*Ground);
        }
        else {const FString Missing=TEXT("RunRewards [")+Label+TEXT("] coin=absent");Test.AddInfo(Missing);UE_LOG(LogTemp,Display,TEXT("%s"),*Missing);}
    }
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
        const bool Started=Pulse(EKeys::Enter)&&!Game->bWaitingForStart;Trace(TEXT("Create/Enter"));return Started;
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
        if(Code==EKeys::J)Trace(TEXT("J before"));
        if(!Key(Code,true)||!Controller->WasInputKeyJustPressed(Code))return false;
        Frame(.005f);if(!Key(Code,false))return false;Frame(.005f);
        if(Code==EKeys::J)Trace(TEXT("J after accepted input"));return true;
    }
    bool AdvanceTo(double At)
    {
        Trace(FString::Printf(TEXT("Advance before target=%.17g"),At));
        if(At<Game->GetSimulationTime())return false;
        for(int32 Count=0;Count<64&&Game->GetSimulationTime()<At;++Count)
        {
            const double Before=Game->GetSimulationTime(),Remaining=At-Before;
            float Dt=float(Remaining);if(double(Dt)>Remaining)Dt=std::nextafter(Dt,0.f);
            if(!(Dt>0.f))return false;Frame(Dt);
            if(Game->GetSimulationTime()<=Before)return false;
        }
        const bool Reached=Game->GetSimulationTime()==At&&!Game->bGameOver;Trace(TEXT("Advance after"));return Reached;
    }
    bool MoveX(double Target)
    {
        Trace(FString::Printf(TEXT("MoveX before target=%.17g"),Target));
        for(int32 Count=0;Count<1600;++Count)
        {
            const double Delta=Target-Player->GetGroundPosition().X;
            if(FMath::Abs(Delta)<.002){Frame(.005f);Trace(TEXT("MoveX after"));return true;}
            const FKey Direction=Delta>0.?EKeys::D:EKeys::A;
            if(!Key(Direction,true))return false;
            Frame(float(FMath::Min(.02,FMath::Abs(Delta)/double(Player->GetMoveSpeed()))));
            if(!Key(Direction,false)||Game->bGameOver)return false;
        }
        Trace(TEXT("MoveX failed"));Test.AddError(TEXT("Normal cross-room movement did not reach its waypoint"));return false;
    }
    bool MoveY(double Target)
    {
        Trace(FString::Printf(TEXT("MoveY before target=%.17g"),Target));
        for(int32 Count=0;Count<1600;++Count)
        {
            const double Delta=Target-Player->GetGroundPosition().Y;
            if(FMath::Abs(Delta)<.002){Frame(.005f);Trace(TEXT("MoveY after"));return true;}
            const FKey Direction=Delta>0.?EKeys::W:EKeys::S;
            if(!Key(Direction,true))return false;
            Frame(float(FMath::Min(.02,FMath::Abs(Delta)/double(Player->GetMoveSpeed()))));
            if(!Key(Direction,false)||Game->bGameOver)return false;
        }
        Trace(TEXT("MoveY failed"));Test.AddError(TEXT("Normal reward movement did not reach its Y waypoint"));return false;
    }
    AActor* CoinLOSBlocker(FVector2D CoinPosition)
    {
        auto Actor=World->SpawnActor<AActor>();if(!Actor)return nullptr;
        auto Box=NewObject<UBoxComponent>(Actor);Actor->SetRootComponent(Box);
        Box->SetBoxExtent(FVector(2.,2.,80.));Box->SetCollisionEnabled(ECollisionEnabled::QueryOnly);
        Box->SetCollisionObjectType(ECC_WorldStatic);Box->SetCollisionResponseToAllChannels(ECR_Block);
        Box->RegisterComponentWithWorld(World);
        // A small actual obstacle at the real object endpoint. No guessed
        // absolute waypoint and no mutation of the coin/player/enemy position.
        Actor->SetActorLocation(FVector(CoinPosition.X,CoinPosition.Y,40.));return Actor;
    }
    bool CoinLineBlocked(FVector2D Position,AActor* Expected=nullptr)const
    {
        const auto P=Player->GetGroundPosition();FCollisionObjectQueryParams Objects;
        Objects.AddObjectTypesToQuery(ECC_WorldStatic);Objects.AddObjectTypesToQuery(ECC_WorldDynamic);
        FCollisionQueryParams Query(SCENE_QUERY_STAT(RunRewardLOSProof),false);Query.AddIgnoredActor(Player);FHitResult Hit;
        const bool Blocked=World->LineTraceSingleByObjectType(Hit,FVector(P.X,P.Y,0.),FVector(Position.X,Position.Y,0.),Objects,Query)&&Hit.bBlockingHit;
        return Blocked&&(!Expected||Hit.GetActor()==Expected);
    }
    bool KillKnightNormally(bool RequireAirborneDeath=false)
    {
        if(!MoveX(220.))return false;auto Knight=Game->Enemies[0].Get();
        Trace(TEXT("Kill movement reached"));
        for(int32 Count=0;Count<12&&!Knight->bDead;++Count)
        {
            Trace(FString::Printf(TEXT("Kill J step=%d airControl=%d"),Count,RequireAirborneDeath));
            if(RequireAirborneDeath)
            {
                // Real Space/apex/J, not a handcrafted JumpHeight or damage.
                // The ordinary active window overlaps the falling Z65 crossing.
                if(!Pulse(EKeys::SpaceBar)||Player->GetVerticalVelocity()<=0.f)return false;
                for(int32 Step=0;Step<160&&Player->GetVerticalVelocity()>0.f;++Step)Frame(.005f);
                Trace(TEXT("Real jump apex before J"));
                if(!Test.TestTrue(TEXT("Actual apex remains airborne above the independent65cm hit-height limit"),
                    Player->JumpHeight>65.f&&Player->GetVerticalVelocity()<=0.f))return false;
                if(!Pulse(EKeys::J)||!Player->GetMeleeCombatState().Action.Active
                    ||!Player->GetMeleeCombatState().Action.StartedAirborne)return false;
                for(int32 Step=0;Step<160&&!Knight->bDead&&Player->GetMeleeCombatState().Action.Active;++Step)Frame(.005f);
                Trace(TEXT("Air primary finished or actual death first observed"));
                if(Knight->bDead&&!Test.TestTrue(TEXT("Real final air hit leaves the player airborne when its coin is first observable"),
                    Player->JumpHeight>0.f))return false;
            }
            else if(!Pulse(EKeys::J)||!AdvanceTo(Game->GetSimulationTime()+.8))return false;
        }
        Trace(TEXT("Kill final"));
        return Knight->bDead&&Knight->bDeathReported&&Knight->GetStoneKnightDriver()->State().RewardClaimed
            &&Game->bRoomCleared&&!Game->bGameOver;
    }
    bool ExitNormally()
    {
        Trace(TEXT("Exit first room before waypoints"));
        // D04 automatic currency range is 60x30. Normal travel deliberately
        // stays above old coins, then returns to the exit only when far away.
        if(!MoveY(80.)||!MoveX(1180.)||!MoveY(0.)||!Pulse(EKeys::E)||!Game->GetSceneInteractionView().Pending
            ||!Game->GetSceneInteractionView().NeedsConfirmation)return false;
        const bool Entered=Pulse(EKeys::Enter)&&Game->Enemies.Num()==1&&!Game->bRoomCleared;
        Trace(TEXT("Exit/Enter second room before AI control"));return Entered;
    }
    bool KillPostClearBatNormally(ADungeonFighter* Bat)
    {
        if(!IsValid(Bat)||!Bat->GetStoneBatDriver())return false;
        for(int32 Count=0;Count<12&&!Bat->bDead;++Count)
        {
            const auto& B=Bat->GetStoneBatDriver()->State();
            Test.AddInfo(FString::Printf(TEXT("Post-clear actual Bat J step=%d id=%llu pos=(%.17g,%.17g,%.17g) HP=%.17g time=%.17g phase=%u"),
                Count,static_cast<unsigned long long>(Bat->GetRuntimeEntityId()),B.Position.X,B.Position.Y,B.Position.Z,B.HP,B.Time,unsigned(B.Phase)));
            if(!Pulse(EKeys::SpaceBar)||Player->GetVerticalVelocity()<=0.f)return false;
            for(int32 Step=0;Step<160&&Player->GetVerticalVelocity()>0.f;++Step)Frame(.005f);
            if(!Pulse(EKeys::J)||!Player->GetMeleeCombatState().Action.Active
                ||!Player->GetMeleeCombatState().Action.StartedAirborne)return false;
            for(int32 Step=0;Step<160&&!Bat->bDead&&Player->GetMeleeCombatState().Action.Active;++Step)Frame(.005f);
        }
        Trace(TEXT("Post-clear Bat death observed before normal landing"));
        return Bat->bDead&&Bat->bDeathReported&&Bat->GetStoneBatDriver()->State().RewardClaimed
            &&Game->bRoomCleared&&AdvanceTo(Game->GetSimulationTime()+2.)&&Player->JumpHeight==0.f;
    }
    FDungeonRunRewardValidationContext Context()const
    {
        const auto& E=Game->GetEquipmentView();FDungeonRunRewardValidationContext C;
        C.RunGuid=E.RunGuid;C.OwnerId=E.OwnerId;C.RoomInstanceId=E.RoomInstanceId;
        C.SimulationTime=Game->GetSimulationTime();C.PlayerCoins=Player->Coins;C.WeaponWorld=&Game->GetWeaponWorldState();
        const auto Add=[&](ADungeonFighter* Actor)
        {
            FDungeonRunRewardActorFact A;A.EntityId=Actor->GetRuntimeEntityId();A.RoomInstanceId=E.RoomInstanceId;
            A.ContentId=Actor==Player?TEXT("player"):Actor->EnemyContentId;
            A.Enemy=Actor->bEnemy;A.Dead=Actor->bDead;A.DeathReported=Actor->bDeathReported;
            A.RewardClaimed=Actor->GetStoneKnightDriver()?Actor->GetStoneKnightDriver()->State().RewardClaimed:
                Actor->GetStoneBatDriver()?Actor->GetStoneBatDriver()->State().RewardClaimed:Actor->bDeathReported;
            C.CurrentActors.Add(A);
        };
        Add(Player);for(auto Actor:Game->Enemies)if(IsValid(Actor))Add(Actor);
        return C;
    }
    const FDungeonPickup* Pickup(FName Kind)const
    {return Game->Pickups.FindByPredicate([Kind](const auto& X){return X.Kind==Kind;});}
};
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDungeonRunRewardDeathSources,
    "CodexDungeon.Content.RunRewards.DeathSourcesAndDuplicateNotification",
    EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FDungeonRunRewardDeathSources::RunTest(const FString&)
{
    FRunRewardFixture F(*this);
    if(!TestTrue(TEXT("Real Scene/Enter/movement/J death fixture"),F.Create()&&F.KillKnightNormally()))return false;
    auto Knight=F.Game->Enemies[0].Get();
    if(!TestTrue(TEXT("Original three physical pickup values exist after actual admitted first/last death"),F.Game->Pickups.Num()==3
        &&F.Pickup(TEXT("coin"))&&F.Pickup(TEXT("potion"))&&F.Pickup(TEXT("axe"))))return false;
    const auto Anchor=Knight->GetGroundPosition();double DeathAt=-1.;
    for(const auto& R:Knight->GetStoneFeedback().Entries())if(R.Event.Kind==DungeonStoneKnight::EEventKind::Died)DeathAt=R.Event.AtTime;
    if(!TestTrue(TEXT("Real knight journal proves the death endpoint independently of new reward facts"),DeathAt>=0.))return false;
    const auto Saved=F.Game->CaptureRunRewardsSnapshot();
    TestTrue(TEXT("Capture is actual bound Run/room reward owner"),Saved.Schema==1&&Saved.Bound
        &&Saved.RunGuid==F.Game->GetEquipmentView().RunGuid&&Saved.OwnerId==F.Player->GetRuntimeEntityId()
        &&Saved.CurrentRoomInstanceId==F.Game->GetEquipmentView().RoomInstanceId&&Saved.InitialCoins==0);
    const auto* GroundCoin=F.Pickup(TEXT("coin"));const auto Delta=F.Player->GetGroundPosition()-GroundCoin->Position;
    if(!TestTrue(TEXT("Actual live grounded clear-line death placement independently admits D04 automatic currency"),
        F.Player->Health>0.f&&F.Player->JumpHeight==0.f&&FMath::Abs(Delta.X)<=60.&&FMath::Abs(Delta.Y)<=30.
        &&!F.CoinLineBlocked(GroundCoin->Position)))return false;
    TestTrue(TEXT("Grounded first death automatically credits its actual nearby coin once without E"),
        F.Player->Coins==5&&GroundCoin->bConsumed);
    TestTrue(TEXT("One true death resolved three distinct stable sources/objects with independent ID domains and one legal currency operation"),
        Saved.Deaths.Num()==1&&Saved.Sources.Num()==3&&Saved.Objects.Num()==3
        &&Saved.NextSourceId==4&&Saved.NextObjectId==4&&Saved.NextOperationId==2&&Saved.Collections.Num()==1);
    if(Saved.Deaths.Num()==1)
    {
        const auto& D=Saved.Deaths[0];TestTrue(TEXT("Death fact retains original entity/content/endpoint and first/clear decisions"),
            D.Death.EntityId==Knight->GetRuntimeEntityId()&&D.Death.RoomInstanceId==Saved.CurrentRoomInstanceId
            &&D.Death.ContentId==TEXT("ENM-STN-001")&&D.Death.AtTime==DeathAt&&D.Death.Position==Anchor
            &&D.Death.FirstDeath&&D.Death.RoomCleared&&D.SourceIds.Num()==3);
    }
    const FName Kinds[]={TEXT("coin"),TEXT("potion"),TEXT("axe")};
    const FVector2D Offsets[]={FVector2D(-18.,-12.),FVector2D(25.,15.),FVector2D(34.,14.)};
    const int32 Amounts[]={5,30,1};
    for(int32 Index=0;Index<3;++Index)
    {
        const auto* P=F.Pickup(Kinds[Index]);const uint64 Id=uint64(Index+1);const auto* O=Reward(Saved,Id);
        TestTrue(TEXT("Identity is assigned at normal birth while every original physical pickup value stays exact"),
            P&&P->RunGuid==Saved.RunGuid&&P->ObjectId==Id&&P->SourceId==Id&&P->RoomInstanceId==Saved.CurrentRoomInstanceId
            &&P->Position==Anchor+Offsets[Index]&&P->bConsumed==(Index==0)&&O&&O->SourceId==Id
            &&O->Kind==EDungeonRunRewardKind(Index)&&O->Position==P->Position&&O->ResolvedAmount==Amounts[Index]
            &&O->Consumed==(Index==0)&&!O->Retired&&O->CollectionOperationId==uint64(Index==0?1:0));
    }
    if(Saved.Collections.Num()==1)
    {
        const auto& C=Saved.Collections[0];
        TestTrue(TEXT("Same-tick death currency has one exact source/owner/room/wallet receipt after its birth"),
            C.Request.ObjectId==1&&C.Request.SourceId==1&&C.Request.OperationId==1
            &&C.Request.OwnerId==F.Player->GetRuntimeEntityId()&&C.Request.RoomInstanceId==Saved.CurrentRoomInstanceId
            &&C.Request.BeforeCoins==0&&C.AfterCoins==5&&C.Request.AtTime==DeathAt);
    }
    const auto Physical=F.Game->Pickups;F.Game->OnFighterDied(Knight);F.Game->OnFighterDied(Knight);
    TestTrue(TEXT("Repeated actual death notification neither resolves again nor reallocates a source/object"),
        SameReward(Saved,F.Game->CaptureRunRewardsSnapshot())&&F.Game->Pickups.Num()==Physical.Num()&&F.Player->Coins==5);
    FDungeonRunRewards Independent;FString Why;
    const bool Restored=Independent.Restore(Saved,F.Context(),Why);if(!Restored)AddInfo(TEXT("Death reward Restore diagnosis: ")+Why);
    TestTrue(TEXT("Independent reward owner restores complete real death facts"),Restored&&SameReward(Saved,Independent.Capture()));
    // Genuine public admission AFTER this room already cleared. No HP/phase,
    // position, death, room-clear or reward record is handcrafted.
    const uint64 PostClearRoom=F.Game->GetEquipmentView().RoomInstanceId;
    auto Bat=F.Game->SpawnStoneBat(F.Player->GetGroundPosition()+FVector2D(70.,0.));
    if(!TestTrue(TEXT("Public post-clear admission creates a distinct actual bat in the same Run/room"),
        Bat&&Bat->GetStoneBatDriver()&&Bat->GetRuntimeEntityId()!=Knight->GetRuntimeEntityId()
        &&F.Game->Enemies.Num()==2&&F.Game->GetEquipmentView().RoomInstanceId==PostClearRoom))return false;
    if(!TestTrue(TEXT("Normal Space/apex/J also truly kills the post-clear admitted bat and lands"),F.KillPostClearBatNormally(Bat)))return false;
    const auto AfterBat=F.Game->CaptureRunRewardsSnapshot();
    TestTrue(TEXT("Two actual enemy deaths keep two coin results but room-first and room-clear sources are each allocated once"),
        AfterBat.Deaths.Num()==2&&AfterBat.Sources.Num()==4&&AfterBat.Objects.Num()==4
        &&AfterBat.NextSourceId==5&&AfterBat.NextObjectId==5&&AfterBat.Collections.Num()==2
        &&AfterBat.NextOperationId==3&&F.Player->Coins==10&&F.Game->Pickups.Num()==4);
    int32 CoinSources=0,PotionSources=0,ClearSources=0;
    for(const auto& X:AfterBat.Sources)
    {
        CoinSources+=X.Kind==EDungeonRunRewardSourceKind::EnemyCoin;
        PotionSources+=X.Kind==EDungeonRunRewardSourceKind::FirstDeathPotion;
        ClearSources+=X.Kind==EDungeonRunRewardSourceKind::RoomClearAxe;
    }
    TestTrue(TEXT("Post-clear real death does not invent a second room-level potion or clear axe"),
        CoinSources==2&&PotionSources==1&&ClearSources==1);
    if(AfterBat.Deaths.Num()==2)
        TestTrue(TEXT("Later last-enemy death truthfully records room-cleared while resolving only its new enemy coin"),
            AfterBat.Deaths[1].Death.EntityId==Bat->GetRuntimeEntityId()&&AfterBat.Deaths[1].Death.RoomCleared
            &&!AfterBat.Deaths[1].Death.FirstDeath&&AfterBat.Deaths[1].SourceIds.Num()==1&&AfterBat.Deaths[1].SourceIds[0]==4);
    const bool PostClearRestored=Independent.Restore(AfterBat,F.Context(),Why);
    if(!PostClearRestored)AddInfo(TEXT("Post-clear actual history Restore diagnosis: ")+Why);
    if(TestTrue(TEXT("Independent owner preserves the full real once-per-room-source history"),
        PostClearRestored&&AfterBat.Deaths.Num()==2&&SameReward(AfterBat,Independent.Capture())))
    {
        auto Bad=AfterBat;Bad.Deaths[1].SourceIds.Add(3);FString InvalidWhy;
        TestFalse(TEXT("A later death cannot re-claim the original room-clear source"),Independent.Restore(Bad,F.Context(),InvalidWhy));
        TestTrue(TEXT("Room-clear-source alias refusal diagnoses and preserves all original results"),
            !InvalidWhy.IsEmpty()&&SameReward(AfterBat,Independent.Capture()));
    }
    F.Game->OnFighterDied(Bat);F.Game->OnFighterDied(Bat);
    TestTrue(TEXT("Post-clear duplicate actual notification cannot repeat the coin or room-level sources"),
        F.Player->Coins==10&&F.Game->Pickups.Num()==4&&SameReward(AfterBat,F.Game->CaptureRunRewardsSnapshot()));
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDungeonRunRewardCollectionTest,
    "CodexDungeon.Content.RunRewards.BoundCoinCollectionAndRetry",
    EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FDungeonRunRewardCollectionTest::RunTest(const FString&)
{
    FRunRewardFixture F(*this);
    if(!TestTrue(TEXT("Real bound coin fixture uses Scene and a normal airborne sword death"),F.Create()&&F.KillKnightNormally(true)))return false;
    const auto* PhysicalCoin=F.Pickup(TEXT("coin"));
    if(!TestNotNull(TEXT("A generated coin exists before the new pickup entrance"),PhysicalCoin))return false;
    const uint64 ObjectId=PhysicalCoin->ObjectId;const auto Before=F.Game->CaptureRunRewardsSnapshot();const int32 Coins=F.Player->Coins;
    const auto CoinPosition=PhysicalCoin->Position;
    F.Trace(TEXT("Coin first observable at actual air death"));
    if(!TestTrue(TEXT("Real airborne birth, not a guessed death distance, leaves the physical coin unconsumed"),
        F.Player->JumpHeight>0.f&&!PhysicalCoin->bConsumed&&Coins==0))return false;
    auto Blocker=F.CoinLOSBlocker(CoinPosition);
    if(!TestNotNull(TEXT("Real native WorldStatic box supplies the LOS rejection control"),Blocker))return false;
    if(!TestTrue(TEXT("Actual endpoint obstacle blocks the real coin while ordinary movement protects its unconsumed birth"),
        F.CoinLineBlocked(CoinPosition,Blocker)&&F.MoveX(CoinPosition.X-90.)))return false;
    Blocker->SetActorEnableCollision(false);
    const auto OutsideX=F.Player->GetGroundPosition()-CoinPosition;
    if(!TestTrue(TEXT("Normal movement creates an actual grounded X-outside60cm and Y-inside30cm clear-line control"),
        F.Player->JumpHeight==0.f&&FMath::Abs(OutsideX.X)>60.&&FMath::Abs(OutsideX.Y)<=30.
        &&!F.CoinLineBlocked(CoinPosition)))return false;
    F.Frame(.03f);
    TestFalse(TEXT("Bound automatic collection refuses an actual X-out-of-range object"),F.Game->TryCollectRunReward(ObjectId).Ok());
    TestTrue(TEXT("X range refusal preserves all source/object/operation/wallet facts"),SameReward(Before,F.Game->CaptureRunRewardsSnapshot())&&F.Player->Coins==Coins);
    if(!TestTrue(TEXT("Normal movement reaches X-valid but Y-outside30cm without entering currency range"),
        F.MoveY(CoinPosition.Y+80.)&&F.MoveX(CoinPosition.X-40.)))return false;
    const auto OutsideY=F.Player->GetGroundPosition()-CoinPosition;
    if(!TestTrue(TEXT("Independent Y range and native clear line isolate the Y refusal"),
        FMath::Abs(OutsideY.X)<=60.&&FMath::Abs(OutsideY.Y)>30.&&!F.CoinLineBlocked(CoinPosition)))return false;
    F.Frame(.03f);TestFalse(TEXT("Bound automatic collection refuses an actual Y-out-of-range object"),F.Game->TryCollectRunReward(ObjectId).Ok());
    TestTrue(TEXT("Y range refusal preserves ledger and wallet"),SameReward(Before,F.Game->CaptureRunRewardsSnapshot())&&F.Player->Coins==Coins);
    Blocker->SetActorEnableCollision(true);
    if(!TestTrue(TEXT("Normal movement enters both currency ranges behind the actual box"),F.MoveY(CoinPosition.Y)))return false;
    const auto Inside=F.Player->GetGroundPosition()-CoinPosition;
    if(!TestTrue(TEXT("Independent native line trace proves LOS is blocked while both60x30 limits are met"),
        FMath::Abs(Inside.X)<=60.&&FMath::Abs(Inside.Y)<=30.&&F.CoinLineBlocked(CoinPosition,Blocker)))return false;
    F.Frame(.03f);TestFalse(TEXT("Bound automatic collection refuses actual blocked LOS"),F.Game->TryCollectRunReward(ObjectId).Ok());
    TestTrue(TEXT("LOS refusal preserves all reward and wallet facts"),SameReward(Before,F.Game->CaptureRunRewardsSnapshot())&&F.Player->Coins==Coins);
    if(!TestTrue(TEXT("A fresh normal Space input starts the real airborne control"),F.Pulse(EKeys::SpaceBar)))return false;
    F.Frame(.03f);Blocker->SetActorEnableCollision(false);
    if(!TestTrue(TEXT("Normal jump and unblocked native line isolate the real airborne refusal"),
        F.Player->JumpHeight>0.f&&!F.CoinLineBlocked(CoinPosition)))return false;
    F.Frame(.03f);TestFalse(TEXT("Bound automatic collection refuses an airborne live actor within range and clear LOS"),F.Game->TryCollectRunReward(ObjectId).Ok());
    TestTrue(TEXT("Airborne refusal retains exact ledger and wallet"),SameReward(Before,F.Game->CaptureRunRewardsSnapshot())&&F.Player->Coins==Coins);
    // Keep the real line blocked through landing so the positive auto-collection
    // control can independently prove that no idle requirement is imposed.
    Blocker->SetActorEnableCollision(true);
    if(!TestTrue(TEXT("Normal central ticks complete landing while the actual line remains blocked"),
        F.AdvanceTo(F.Game->GetSimulationTime()+2.)&&F.Player->JumpHeight==0.f&&F.CoinLineBlocked(CoinPosition,Blocker)))return false;
    if(!TestTrue(TEXT("Normal movement returns outside X range before the live attacking collection control"),
        F.MoveX(CoinPosition.X-90.)&&F.Pulse(EKeys::D)))return false;
    Blocker->SetActorEnableCollision(false);Blocker->Destroy();
    const auto AttackOrigin=F.Player->GetGroundPosition()-CoinPosition;
    if(!TestTrue(TEXT("Independent grounded clear-line origin remains outside60cm before normal J"),
        F.Player->Health>0.f&&F.Player->JumpHeight==0.f&&FMath::Abs(AttackOrigin.X)>60.
        &&FMath::Abs(AttackOrigin.Y)<=30.&&!F.CoinLineBlocked(CoinPosition)))return false;
    if(!TestTrue(TEXT("Fresh normal J starts a real accepted primary outside currency range"),F.Pulse(EKeys::J)
        &&F.Player->GetMeleeCombatState().Action.Active))return false;
    const auto Attack=F.Player->GetMeleeCombatState().Action;
    if(!TestTrue(TEXT("Normal same-direction movement enters the real60x30cm clear-line range without E"),
        F.MoveX(CoinPosition.X-55.)&&FMath::Abs(F.Player->GetGroundPosition().X-CoinPosition.X)<=60.
        &&FMath::Abs(F.Player->GetGroundPosition().Y-CoinPosition.Y)<=30.&&!F.CoinLineBlocked(CoinPosition)))return false;
    F.Trace(TEXT("After normal attacking automatic collection entrance"));
    TestTrue(TEXT("Automatic currency collection requires no idle and cannot interrupt the original accepted attack"),
        F.Player->GetMeleeCombatState().Action.Active&&F.Player->GetMeleeCombatState().Action.AttackId==Attack.AttackId
        &&F.Player->GetMeleeCombatState().Action.Start==Attack.Start&&F.Player->GetMeleeCombatState().Action.End==Attack.End);
    const auto Collected=F.Game->CaptureRunRewardsSnapshot();const auto* O=Reward(Collected,ObjectId);const auto* Coin=F.Pickup(TEXT("coin"));
    TestTrue(TEXT("Normal bound coin pickup atomically gives exactly5 coins and consumes only its original ground object"),
        ObjectId!=0&&F.Player->Coins==Coins+5&&Coin&&Coin->ObjectId==ObjectId&&Coin->bConsumed
        &&O&&O->Consumed&&!O->Retired&&Collected.Collections.Num()==1&&Collected.NextOperationId==2);
    TestTrue(TEXT("Potion and axe keep their original unconsumed values without claiming formal item support"),
        F.Pickup(TEXT("potion"))&&!F.Pickup(TEXT("potion"))->bConsumed
        &&F.Pickup(TEXT("axe"))&&!F.Pickup(TEXT("axe"))->bConsumed&&F.Game->Pickups.Num()==3);
    if(Collected.Collections.Num()==1)
    {
        const auto& Receipt=Collected.Collections[0];
        TestTrue(TEXT("Collection receipt proves original source/scope/owner and actual wallet change"),
            Receipt.Request.ObjectId==ObjectId&&O&&Receipt.Request.SourceId==O->SourceId
            &&Receipt.Request.OwnerId==F.Player->GetRuntimeEntityId()&&Receipt.Request.RoomInstanceId==Collected.CurrentRoomInstanceId
            &&Receipt.Request.BeforeCoins==Coins&&Receipt.AfterCoins==Coins+5&&Receipt.Request.OperationId==1);
        const auto Retry=F.Game->TryCollectRunReward(ObjectId,Receipt.Request.OperationId);
        TestTrue(TEXT("Same operation is a read of the exact committed result without another resource change"),
            Retry.Ok()&&Retry.Replayed&&Retry.ObjectId==ObjectId&&Retry.OperationId==Receipt.Request.OperationId
            &&Retry.BeforeCoins==Coins&&Retry.AfterCoins==Coins+5&&F.Player->Coins==Coins+5
            &&SameReward(Collected,F.Game->CaptureRunRewardsSnapshot()));
        const auto* Potion=F.Pickup(TEXT("potion"));
        if(TestNotNull(TEXT("Original other object exists for operation identity conflict"),Potion))
            TestFalse(TEXT("Reusing committed operation for another object is refused"),F.Game->TryCollectRunReward(Potion->ObjectId,Receipt.Request.OperationId).Ok());
        TestTrue(TEXT("Conflicting operation cannot change the original result, wallet or other objects"),
            SameReward(Collected,F.Game->CaptureRunRewardsSnapshot())&&F.Player->Coins==Coins+5);
    }
    F.Frame(.03f);
    TestTrue(TEXT("Later normal automatic collection cannot repeat the coin or consume unsupported potion/axe"),
        F.Player->Coins==Coins+5&&SameReward(Collected,F.Game->CaptureRunRewardsSnapshot()));
    FDungeonRunRewards Independent;FString Why;
    const bool Restored=Independent.Restore(Collected,F.Context(),Why);if(!Restored)AddInfo(TEXT("Collected reward Restore diagnosis: ")+Why);
    TestTrue(TEXT("Complete independent owner restores consumed object with one exact receipt"),Restored&&SameReward(Collected,Independent.Capture()));
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDungeonRunRewardRetirement,
    "CodexDungeon.Content.RunRewards.RoomRetirementAndValidatedHistory",
    EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FDungeonRunRewardRetirement::RunTest(const FString&)
{
    FRunRewardFixture F(*this);
    if(!TestTrue(TEXT("Real first-room death and free E/Enter transition fixture"),F.Create()&&F.KillKnightNormally()))return false;
    const auto BeforeExit=F.Game->CaptureRunRewardsSnapshot();const auto Run=F.Game->GetEquipmentView().RunGuid;
    const auto FirstRoom=F.Game->GetEquipmentView().RoomInstanceId;
    const auto OldEntity=F.Game->Enemies[0]->GetRuntimeEntityId();const auto* Coin=F.Pickup(TEXT("coin"));
    if(!TestNotNull(TEXT("Original physical coin identity exists before exit even after legal automatic consumption"),Coin))return false;
    const uint64 OldObject=Coin->ObjectId;
    const auto FirstDelta=F.Player->GetGroundPosition()-Coin->Position;
    if(!TestTrue(TEXT("Actual first-room death placement independently admits automatic currency before retirement"),
        F.Player->Health>0.f&&F.Player->JumpHeight==0.f&&FMath::Abs(FirstDelta.X)<=60.
        &&FMath::Abs(FirstDelta.Y)<=30.&&!F.CoinLineBlocked(Coin->Position)))return false;
    TestTrue(TEXT("First-room nearby coin is legitimately consumed with its sole collection before exit"),
        Coin->bConsumed&&F.Player->Coins==5&&BeforeExit.Collections.Num()==1&&BeforeExit.NextOperationId==2);
    if(!TestTrue(TEXT("Normal E/Enter really enters next room without a new Run"),F.ExitNormally()
        &&F.Game->GetEquipmentView().RunGuid==Run&&F.Game->GetEquipmentView().RoomInstanceId==FirstRoom+1
        &&F.Game->Pickups.IsEmpty()))return false;
    TestTrue(TEXT("A genuine free exit keeps the already credited5-coin wallet"),F.Player->Coins==5);
    const auto Retired=F.Game->CaptureRunRewardsSnapshot();
    TestTrue(TEXT("Leaving preserves all three objects as retired facts including the one previously consumed coin"),
        Retired.Bound&&Retired.RunGuid==Run&&Retired.CurrentRoomInstanceId==FirstRoom+1
        &&Retired.Objects.Num()==3&&Retired.Sources.Num()==3&&Retired.Deaths.Num()==1
        &&Retired.NextObjectId==BeforeExit.NextObjectId&&Retired.NextSourceId==BeforeExit.NextSourceId
        &&Retired.Collections.Num()==1&&Retired.NextOperationId==2&&Retired.RoomExits.Num()==1&&Retired.RetiredEntities.Num()==1);
    for(const auto& O:Retired.Objects)TestTrue(TEXT("Room retirement is orthogonal to the original actual currency collection"),
        O.RoomInstanceId==FirstRoom&&O.Retired&&O.Consumed==(O.Kind==EDungeonRunRewardKind::Coin)
        &&O.CollectionOperationId==(O.Kind==EDungeonRunRewardKind::Coin?uint64(1):uint64(0))
        &&O.RetiredAt<=F.Game->GetSimulationTime());
    if(Retired.RetiredEntities.Num()==1)
    {
        const auto& T=Retired.RetiredEntities[0];TestTrue(TEXT("Old knight tombstone retains real death/claim/source identity rather than spawning an actor"),
            T.Actor.EntityId==OldEntity&&T.Actor.RoomInstanceId==FirstRoom&&T.Actor.ContentId==TEXT("ENM-STN-001")
            &&T.Actor.Enemy&&T.Actor.Dead&&T.Actor.DeathReported&&T.Actor.RewardClaimed&&T.RetiredAt<=F.Game->GetSimulationTime());
    }
    TestFalse(TEXT("A fresh current-room operation cannot collect a retired previous-room object again"),F.Game->TryCollectRunReward(OldObject).Ok());
    TestTrue(TEXT("Retired-object refusal cannot resurrect sources or add wallet/operation facts"),
        SameReward(Retired,F.Game->CaptureRunRewardsSnapshot())&&F.Player->Coins==5);
    auto NewKnight=F.Game->Enemies[0].Get();
    if(!TestTrue(TEXT("New room has a genuinely distinct dormant knight before any fixture AI control"),
        NewKnight->GetRuntimeEntityId()!=OldEntity&&NewKnight->GetStoneKnightDriver()
        &&NewKnight->GetStoneKnightDriver()->State().Phase==DungeonStoneKnight::EPhase::Dormant))return false;
    // Control the new room's still-dormant admission, never its HP/death/clear.
    NewKnight->bAIEnabled=false;
    F.Trace(TEXT("Second room native admitted knight after explicit AI control"));
    if(!TestTrue(TEXT("Normal movement and J also truly kill the second same-template knight"),F.KillKnightNormally()))return false;
    const auto Saved=F.Game->CaptureRunRewardsSnapshot();
    TestTrue(TEXT("Same-template second-room sources use new unique IDs while all retired first-room results remain"),
        Saved.Deaths.Num()==2&&Saved.Sources.Num()==6&&Saved.Objects.Num()==6&&Saved.NextSourceId==7&&Saved.NextObjectId==7
        &&Saved.RoomExits.Num()==1&&Saved.RetiredEntities.Num()==1&&Saved.Collections.Num()==2&&Saved.NextOperationId==3
        &&F.Player->Coins==10);
    for(const auto& O:Saved.Objects)if(O.RoomInstanceId==FirstRoom+1)
        TestTrue(TEXT("Second-room objects have new source IDs and retain their own real currency result"),
            O.ObjectId>3&&O.SourceId>3&&!O.Retired&&O.Consumed==(O.Kind==EDungeonRunRewardKind::Coin)
            &&O.CollectionOperationId==(O.Kind==EDungeonRunRewardKind::Coin?uint64(2):uint64(0)));
    FDungeonRunRewards Independent;FString Why;const auto Context=F.Context();
    const bool Accepted=Independent.Restore(Saved,Context,Why);if(!Accepted)AddInfo(TEXT("Cross-room reward Restore diagnosis: ")+Why);
    if(TestTrue(TEXT("Entire real cross-room history restores to an independent owner"),Accepted))
    {
        TestTrue(TEXT("All death/source/object/receipt/retired/transition fields survive exact deep-copy restore"),SameReward(Saved,Independent.Capture()));
        const auto Reject=[&](const TCHAR* Label,auto Mutate)
        {
            auto Bad=Saved;Mutate(Bad);FString BadWhy;
            TestFalse(*(FString(Label)+TEXT(" is rejected")),Independent.Restore(Bad,Context,BadWhy));
            TestTrue(*(FString(Label)+TEXT(" has a diagnosis and cannot partly install")),!BadWhy.IsEmpty()&&SameReward(Saved,Independent.Capture()));
        };
        Reject(TEXT("Unknown reward schema"),[](auto& Bad){Bad.Schema=99;});
        Reject(TEXT("Wrong complete Run scope"),[](auto& Bad){Bad.RunGuid.Invalidate();});
        Reject(TEXT("Aliased next object ID"),[](auto& Bad){Bad.NextObjectId=Bad.Objects.Last().ObjectId;});
        Reject(TEXT("Duplicate resolved source"),[](auto& Bad){const auto Copy=Bad.Sources[0];Bad.Sources.Add(Copy);});
        Reject(TEXT("Consumed object without collection receipt"),[](auto& Bad){Bad.Objects[1].Consumed=true;});
        Reject(TEXT("Missing original death evidence"),[](auto& Bad){Bad.Deaths.RemoveAt(0);});
        Reject(TEXT("Retired identity falsely alive after claimed death"),[](auto& Bad){Bad.RetiredEntities[0].Actor.Dead=false;});
        Reject(TEXT("Previous-room unclaimed object silently resurrected"),[](auto& Bad){Bad.Objects[0].Retired=false;Bad.Objects[0].RetiredAt=0.;});
    }
    return true;
}
#endif
