#if WITH_DEV_AUTOMATION_TESTS
#include "Misc/AutomationTest.h"
#include "../DungeonFighter.h"
#include "Engine/World.h"

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDungeonArmorContentTest,"CodexDungeon.Content.ArmorSwapAndStats",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)
bool FDungeonArmorContentTest::RunTest(const FString& Parameters)
{
    const auto Settings=UWorld::InitializationValues().AllowAudioPlayback(false).CreatePhysicsScene(false)
        .RequiresHitProxies(false).CreateNavigation(false).CreateAISystem(false).ShouldSimulatePhysics(false).SetTransactional(false);
    UWorld* World=UWorld::CreateWorld(EWorldType::Game,false,NAME_None,nullptr,true,ERHIFeatureLevel::Num,&Settings);
    if(!TestNotNull(TEXT("Armor test world"),World)) return false;
    auto P=World->SpawnActor<ADungeonFighter>();
    P->ResetFighter({0,0});
    TestTrue(TEXT("QA inventory adapter can request light armor"),P->BeginArmorChange(TEXT("ARM-LGT-001")));
    P->Tick(.25f);
    TestEqual(TEXT("Old armor remains before completion"),P->ArmorId,FString());
    P->BeginAttack();
    TestEqual(TEXT("Armor change cannot overlap an attack"),P->AttackTime,0.f);
    P->Tick(.25f);
    TestEqual(TEXT("Armor commits only after full half second"),P->ArmorId,FString(TEXT("ARM-LGT-001")));
    TestTrue(TEXT("Light armor actual movement is 286.2"),FMath::IsNearlyEqual(P->GetMoveSpeed(),286.2f,.001f));
    P->MoveOnGround({1,0},.1f);
    TestTrue(TEXT("Actual movement uses equipped armor"),FMath::IsNearlyEqual(P->GetGroundPosition().X,28.62f,.001f));
    P->ApplyCombatHit(114.f/10.f,nullptr,0.f);
    TestTrue(TEXT("Armor14 mitigates 11.4 physical damage to 10"),FMath::IsNearlyEqual(P->Health,90.f,.001f));
    P->Tick(.66f);
    TestTrue(TEXT("Heavy armor change begins"),P->BeginArmorChange(TEXT("ARM-HVY-001")));
    P->Tick(.25f);
    P->ApplyCombatHit(1.f,nullptr,0.f);
    P->Tick(.25f);
    TestEqual(TEXT("Real damage cancels uncommitted armor swap"),P->ArmorId,FString(TEXT("ARM-LGT-001")));
    TestTrue(TEXT("Canceled swap cannot complete itself"),P->GetArmorChangeRemaining()<=0.f);
    P->Tick(.66f);
    const FString Ids[]={TEXT("ARM-MED-001"),TEXT("ARM-HVY-001"),TEXT("ARM-ROB-001")};
    const float Moves[]={265.f,222.6f,265.f}, Poise[]={40.f,70.f,30.f}, Wards[]={18.f,12.f,50.f};
    for(int32 I=0;I<3;++I)
    {
        TestTrue(TEXT("Armor change accepted while idle"),P->BeginArmorChange(Ids[I]));
        P->Tick(.5f);
        TestTrue(TEXT("Armor movement profile applied"),FMath::IsNearlyEqual(P->GetMoveSpeed(),Moves[I],.001f));
        TestEqual(TEXT("Armor poise profile applied"),P->GetPoiseThreshold(),Poise[I]);
        TestEqual(TEXT("Armor ward profile applied"),P->GetArmorRating(true),Wards[I]);
    }
    const float PriorHealth=P->Health;
    TestTrue(TEXT("Actual focus consumption accepted"),P->SpendFocus(50.f));
    TestEqual(TEXT("Actual focus is deducted"),P->Focus,50.f);
    P->Tick(.5f);
    TestEqual(TEXT("Robe does not bypass one second regen delay"),P->Focus,50.f);
    P->Tick(.5f);P->Tick(.5f);
    TestTrue(TEXT("Robe regenerates16/s, replacing12/s"),FMath::IsNearlyEqual(P->Focus,58.f,.001f));
    TestEqual(TEXT("Equipment changes did not heal missing HP"),P->Health,PriorHealth);
    P->ApplyCombatHit(15.f,nullptr,0.f,true);
    TestTrue(TEXT("Robe50 ward mitigates actual magic15 to10"),FMath::IsNearlyEqual(P->Health,PriorHealth-10.f,.001f));
    TestFalse(TEXT("Insufficient focus cannot be spent"),P->SpendFocus(100.f));
    TestTrue(TEXT("Failed spend preserves available focus"),FMath::IsNearlyEqual(P->Focus,58.f,.001f));
    TestFalse(TEXT("Unknown armor template rejected"),P->BeginArmorChange(TEXT("ARM-UNKNOWN-999")));
    World->DestroyWorld(false);
    return true;
}
#endif
