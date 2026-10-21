#if WITH_DEV_AUTOMATION_TESTS
#include "Misc/AutomationTest.h"
#include "../DungeonFighter.h"
#include "../DungeonStoneKnightDriver.h"
#include "Components/BoxComponent.h"
#include "Engine/World.h"

namespace
{
struct FKnightDriverWorld
{
    UWorld* World = nullptr;
    ADungeonFighter* Owner = nullptr;
    ADungeonFighter* Player = nullptr;
    ~FKnightDriverWorld() { if (World) World->DestroyWorld(false); }
    bool Create()
    {
        const auto Settings = UWorld::InitializationValues().AllowAudioPlayback(false).CreatePhysicsScene(true)
            .RequiresHitProxies(false).CreateNavigation(false).CreateAISystem(false).ShouldSimulatePhysics(false).SetTransactional(false);
        World = UWorld::CreateWorld(EWorldType::Game, false, NAME_None, nullptr, true, ERHIFeatureLevel::Num, &Settings);
        if (!World) return false;
        Owner = World->SpawnActor<ADungeonFighter>();
        Player = World->SpawnActor<ADungeonFighter>();
        if (!Owner || !Player) return false;
        Owner->bEnemy = true; Owner->bAIEnabled = false; Owner->MaxHealth = 110.f; Owner->ResetFighter({0,0});
        Player->ResetFighter({900,0});
        return true;
    }
    FDungeonKnightFrame Frame(double From, double To, FVector2D PlayerPosition = {900,0})
    {
        Player->SetActorLocation(FVector(PlayerPosition.X,PlayerPosition.Y,0));
        FDungeonKnightFrame F; F.FromTime=From; F.ToTime=To; F.Target=Player;
        FDungeonKnightBody B; B.Fighter=Player; B.EntityId=99; B.Start=B.End=PlayerPosition;
        F.Bodies.Add(B); return F;
    }
    AActor* AddWall()
    {
        auto Wall=World->SpawnActor<AActor>();
        auto Box=NewObject<UBoxComponent>(Wall);
        Wall->SetRootComponent(Box); Box->SetBoxExtent({10,150,100});
        Box->SetCollisionEnabled(ECollisionEnabled::QueryOnly); Box->SetCollisionObjectType(ECC_WorldStatic);
        Box->SetCollisionResponseToAllChannels(ECR_Block); Box->RegisterComponentWithWorld(World);
        Wall->SetActorLocation({200,0,0}); return Wall;
    }
};
bool WakeKnight(FDungeonStoneKnightDriver& D, FKnightDriverWorld& F)
{
    auto B=D.ApplyResolvedHit(1,0,F.Frame(0,0));
    return B.Accepted && D.StepTo(.85,F.Frame(0,.85)).Accepted && D.State().Awakened;
}
DungeonStoneKnight::FSweepRequest ChargeQuery(const FDungeonStoneKnightDriver& D)
{
    DungeonStoneKnight::FSweepRequest Q; Q.Charge=true; Q.FromTime=1.75; Q.ToTime=2.55;
    Q.From={0,0}; Q.To={496,0}; Q.Action=D.State().Action; return Q;
}
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FKnightDriverDormancyTest,"CodexDungeon.Content.StoneKnightDriver.DormancyAndResolvedDamage",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)
bool FKnightDriverDormancyTest::RunTest(const FString& Parameters)
{
    FKnightDriverWorld F; if (!TestTrue(TEXT("Real isolated world created"),F.Create())) return false;
    FDungeonStoneKnightDriver D(F.Owner,71);
    TestTrue(TEXT("Dormant step accepted"),D.StepTo(0,F.Frame(0,0)).Accepted);
    TestTrue(TEXT("No empty-set implicit wake"),D.State().Phase==DungeonStoneKnight::EPhase::Dormant);
    auto B=D.ApplyResolvedHit(17,0,F.Frame(0,0));
    TestTrue(TEXT("Actual damage enters wake in existing kernel"),B.Accepted&&D.State().Phase==DungeonStoneKnight::EPhase::Waking);
    TestEqual(TEXT("Kernel keeps actual lost HP"),D.State().HP,93.0);
    TestEqual(TEXT("Driver has not separately committed actor HP"),F.Owner->Health,110.f);
    D.StepTo(.849,F.Frame(0,.849)); TestFalse(TEXT("Warning is still active"),D.State().Awakened);
    D.StepTo(.85,F.Frame(.849,.85)); TestTrue(TEXT("Full warning completes"),D.State().Awakened);
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FKnightDriverChargeTest,"CodexDungeon.Content.StoneKnightDriver.ChargeQueryHasNoSideEffects",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)
bool FKnightDriverChargeTest::RunTest(const FString& Parameters)
{
    FKnightDriverWorld F; if (!TestTrue(TEXT("Real isolated world created"),F.Create())) return false;
    FDungeonStoneKnightDriver D(F.Owner,71); if (!TestTrue(TEXT("Kernel wakes"),WakeKnight(D,F))) return false;
    D.StepTo(.85,F.Frame(.85,.85,{300,0}));
    auto Frame=F.Frame(.85,2.55,{300,0}); const auto Before=D.Capture();
    const auto Q=ChargeQuery(D); const auto Hit=D.QuerySweep(Q,Frame);
    TestTrue(TEXT("Actual player center is hit at front reach before body contact"),Hit.Stop==DungeonStoneKnight::EStop::ValidHit&&FMath::IsNearlyEqual(Hit.Fraction,235.0/496.0,1.e-8)&&Hit.TargetId==99);
    TestEqual(TEXT("Query does not mutate actor HP"),F.Player->Health,100.f);
    TestEqual(TEXT("Query does not mutate owner position"),F.Owner->GetGroundPosition(),FVector2D::ZeroVector);
    TestEqual(TEXT("Query does not consume event IDs"),D.State().NextEventId,Before.NextEventId);
    auto B=D.StepTo(2.55,Frame);
    TestTrue(TEXT("One accepted batch hit returned"),B.Accepted&&B.Hits.Num()==1);
    if (B.Hits.Num()==1) TestTrue(TEXT("Correct raw damage and stable target"),B.Hits[0].Damage==20&&B.Hits[0].TargetId==99&&B.Hits[0].AttackId==1);
    TestEqual(TEXT("Returned batch still has not applied damage"),F.Player->Health,100.f);
    TestTrue(TEXT("Contact position is kernel output awaiting root commit"),FMath::IsNearlyEqual(D.State().Position.X,235.0,1.e-7));
    TestTrue(TEXT("Same clock cannot duplicate hit"),D.StepTo(2.55,F.Frame(2.55,2.55,{300,0})).Hits.IsEmpty());
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FKnightDriverWallTest,"CodexDungeon.Content.StoneKnightDriver.StaticWallAndBodyStops",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)
bool FKnightDriverWallTest::RunTest(const FString& Parameters)
{
    {
        FKnightDriverWorld F; if (!TestTrue(TEXT("Physics query world created"),F.Create())) return false;
        F.AddWall(); FDungeonStoneKnightDriver D(F.Owner,71);
        auto Q=ChargeQuery(D); auto Hit=D.QuerySweep(Q,F.Frame(1.75,2.55,{300,0}));
        TestTrue(TEXT("Real registered static box stops swept 24cm body at X166"),Hit.Stop==DungeonStoneKnight::EStop::Wall&&FMath::IsNearlyEqual(Hit.Fraction,166.0/496.0,1.e-5));
        TestEqual(TEXT("Wall query never changes owner transform"),F.Owner->GetGroundPosition(),FVector2D::ZeroVector);
    }
    {
        FKnightDriverWorld F; if (!TestTrue(TEXT("Body query world created"),F.Create())) return false;
        FDungeonStoneKnightDriver D(F.Owner,71); auto Frame=F.Frame(1.75,2.55,{300,0});
        Frame.Bodies[0].bCanTakeDamage=false;
        const auto Hit=D.QuerySweep(ChargeQuery(D),Frame);
        TestTrue(TEXT("Old invulnerability blocks damage, actual body still stops at X258"),Hit.Stop==DungeonStoneKnight::EStop::Body&&Hit.TargetId==0&&FMath::IsNearlyEqual(Hit.Fraction,258.0/496.0,1.e-8));
        auto AllyActor=F.World->SpawnActor<ADungeonFighter>();
        if (!TestNotNull(TEXT("Real allied actor"),AllyActor)) return false;
        AllyActor->bEnemy=true; AllyActor->bAIEnabled=false; AllyActor->ResetFighter({120,0});
        auto Ally=Frame.Bodies[0]; Ally.Fighter=AllyActor; Ally.EntityId=100; Ally.bSameTeam=true;
        Ally.bCanTakeDamage=true; Ally.Start=Ally.End={120,0}; Ally.BodyHalfExtent={18,18}; Frame.Bodies.Add(Ally);
        const auto Allied=D.QuerySweep(ChargeQuery(D),Frame);
        TestTrue(TEXT("Earlier allied body blocks without friendly damage"),Allied.Stop==DungeonStoneKnight::EStop::Body&&Allied.TargetId==0&&FMath::IsNearlyEqual(Allied.Fraction,78.0/496.0,1.e-8));
    }
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FKnightDriverShieldTest,"CodexDungeon.Content.StoneKnightDriver.ShieldPoiseResumeAndReward",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)
bool FKnightDriverShieldTest::RunTest(const FString& Parameters)
{
    FKnightDriverWorld F; if (!TestTrue(TEXT("Isolated world created"),F.Create())) return false;
    FDungeonStoneKnightDriver D(F.Owner,71); if (!TestTrue(TEXT("Kernel wakes"),WakeKnight(D,F))) return false;
    D.StepTo(.85,F.Frame(.85,.85,{50,0})); auto B=D.StepTo(1.56,F.Frame(.85,1.56,{50,0}));
    TestTrue(TEXT("A2 window returns one raw 13 damage hit"),B.Hits.Num()==1&&B.Hits[0].Damage==13);
    D.ApplyResolvedHit(0,59,F.Frame(1.56,1.56,{50,0}));
    TestTrue(TEXT("Unbroken poise preserves primary"),D.State().Action.InProgress);
    D.ApplyResolvedHit(0,1,F.Frame(1.56,1.56,{50,0}));
    TestTrue(TEXT("True break cancels via kernel"),D.State().Phase==DungeonStoneKnight::EPhase::Stunned);
    const auto Saved=D.Capture(); FDungeonStoneKnightDriver R(F.Owner,71);
    TestTrue(TEXT("Driver restores exact kernel state"),R.Restore(Saved));
    TestEqual(TEXT("Continue preserves accepted shield CD"),R.State().ShieldReadyAt,Saved.ShieldReadyAt);
    TestTrue(TEXT("Continue does not duplicate old shield hit"),R.StepTo(Saved.StunUntil,F.Frame(1.56,Saved.StunUntil,{900,0})).Hits.IsEmpty());
    R.ApplyResolvedHit(200,0,F.Frame(R.State().Time,R.State().Time));
    TestTrue(TEXT("Death reward claim once"),R.ClaimDeathReward()&&!R.ClaimDeathReward());
    FDungeonStoneKnightDriver C(F.Owner,71); TestTrue(TEXT("Dead restore does not reset reward"),C.Restore(R.Capture())&&!C.ClaimDeathReward());
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FKnightDriverMovingTargetTest,"CodexDungeon.Content.StoneKnightDriver.MovingTargetContinuousContact",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)
bool FKnightDriverMovingTargetTest::RunTest(const FString& Parameters)
{
    FKnightDriverWorld F; if (!TestTrue(TEXT("Isolated world created"),F.Create())) return false;
    FDungeonStoneKnightDriver D(F.Owner,71); if (!TestTrue(TEXT("Kernel wakes"),WakeKnight(D,F))) return false;
    D.StepTo(.85,F.Frame(.85,.85,{300,0})); D.StepTo(1.75,F.Frame(.85,1.75,{300,0}));
    auto Frame=F.Frame(1.75,1.85,{100,-60}); Frame.Bodies[0].Start={100,60};
    auto B=D.StepTo(1.85,Frame);
    TestTrue(TEXT("Player crosses live corridor between render endpoints and is hit exactly once"),B.Accepted&&B.Hits.Num()==1);
    if (B.Hits.Num()==1) TestTrue(TEXT("Contact timestamp is inside actual interval"),B.Hits[0].AtTime>1.75&&B.Hits[0].AtTime<1.85);
    TestEqual(TEXT("Continuous query only returns pending damage"),F.Player->Health,100.f);
    return true;
}
#endif
