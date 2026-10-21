#include "DungeonProbe.h"
#include "DungeonGameMode.h"
#include "DungeonFighter.h"
#include "Engine/Engine.h"
#include "Engine/World.h"
#include "Misc/EngineVersion.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
#include "Misc/Paths.h"
#include "Misc/FileHelper.h"
#include "HAL/FileManager.h"
#include "Kismet/GameplayStatics.h"
#include "Dom/JsonObject.h"
#include "Serialization/JsonWriter.h"
#include "Serialization/JsonSerializer.h"
#include "GameFramework/PlayerController.h"
#include "GameFramework/PlayerInput.h"

ADungeonProbe::ADungeonProbe() { PrimaryActorTick.bCanEverTick=true; }
void ADungeonProbe::BeginPlay()
{
    Super::BeginPlay();
    FParse::Value(FCommandLine::Get(),TEXT("DungeonProofDir="),ProofDirectory);
    if(ProofDirectory.IsEmpty()) ProofDirectory=FPaths::ProjectSavedDir()/TEXT("FirstRoomProof")/FDateTime::Now().ToString(TEXT("%Y%m%d-%H%M%S"));
    IFileManager::Get().MakeDirectory(*ProofDirectory,true);
    GetMutableDefault<UEngine>()->GameScreenshotSaveDirectory.Path=ProofDirectory;
    if(auto Controller=UGameplayStatics::GetPlayerController(this,0)) Controller->AddTickPrerequisiteActor(this);
}
void ADungeonProbe::Key(FKey Input,bool Down)
{
    const bool WasDown=HeldKeys.FindRef(Input); if(WasDown==Down) return;
    if(auto Controller=UGameplayStatics::GetPlayerController(this,0))
        Controller->InputKey(FInputKeyParams(Input,Down?IE_Pressed:IE_Released,Down?1.0:0.0));
    HeldKeys.Add(Input,Down);
}
void ADungeonProbe::MoveInput(FVector2D Direction)
{
    Key(EKeys::D,Direction.X>.1); Key(EKeys::A,Direction.X<-.1);
    Key(EKeys::W,Direction.Y>.1); Key(EKeys::S,Direction.Y<-.1);
}
void ADungeonProbe::Check(const FString& Name,bool Passed)
{
    auto Item=MakeShared<FJsonObject>(); Item->SetStringField(TEXT("name"),Name); Item->SetBoolField(TEXT("passed"),Passed);
    Results.Add(MakeShared<FJsonValueObject>(Item));
    UE_LOG(LogTemp,Display,TEXT("DungeonProof %s: %s"),*Name,Passed?TEXT("PASS"):TEXT("FAIL"));
}
void ADungeonProbe::RunChecks(ADungeonGameMode* Game)
{
    Game->RestartRun(); auto P=Game->GetPlayerFighter();
    Check(TEXT("three_enemies_and_player_spawned"),P&&Game->Enemies.Num()==3);
    if(!P||Game->Enemies.Num()!=3) return;
    for(auto E:Game->Enemies) E->bAIEnabled=false;
    auto Target=Game->Enemies[0];
    P->ResetFighter({-200,0}); P->Facing=1;
    Target->ResetFighter({-120,140}); Target->bAIEnabled=false;
    for(int I=1;I<Game->Enemies.Num();++I) { Game->Enemies[I]->ResetFighter({600.f,-180.f+I*180.f}); Game->Enemies[I]->bAIEnabled=false; }
    const float HP=Target->Health;
    Game->ResolveAttack(P);
    Check(TEXT("different_ground_depth_misses_in_world"),Target->Health==HP);
    Target->ResetFighter({-120,0}); Target->bAIEnabled=false;
    Game->ResolveAttack(P);
    Check(TEXT("same_depth_forward_attack_hits_in_world"),Target->Health<HP);
    Target->ResetFighter({-280,0}); Target->bAIEnabled=false;
    Game->ResolveAttack(P);
    Check(TEXT("target_behind_attacker_misses_in_world"),Target->Health==Target->MaxHealth);
    Target->ResetFighter({-120,0}); Target->bAIEnabled=false;
    Target->ApplyCombatHit(999,P);
    const int DropCount=Game->Pickups.Num();
    Target->ApplyCombatHit(999,P); Game->OnFighterDied(Target);
    Check(TEXT("death_reward_only_once"),Target->bDead&&Game->Pickups.Num()==DropCount);
    Game->Pickups.Empty();
    FDungeonPickup Potion; Potion.Kind=TEXT("potion"); Potion.Position=P->GetGroundPosition(); Game->Pickups.Add(Potion);
    Game->TryInteract();
    Check(TEXT("full_health_preserves_potion"),!Game->Pickups[0].bConsumed&&P->Health==P->MaxHealth);
    P->Health=90.f; Game->TryInteract();
    Check(TEXT("potion_restores_and_caps_health"),Game->Pickups[0].bConsumed&&P->Health==P->MaxHealth);
    FDungeonPickup Axe; Axe.Kind=TEXT("axe"); Axe.Position=P->GetGroundPosition(); Game->Pickups.Add(Axe); Game->TryInteract();
    Check(TEXT("axe_pickup_unlocks_weapon"),P->bHasAxe);
    const FString Before=P->WeaponId; P->SwitchWeapon();
    Check(TEXT("weapon_switch_changes_equipped_id"),P->WeaponId!=Before);
    for(auto E:Game->Enemies) E->ApplyCombatHit(999,P);
    Check(TEXT("all_enemies_dead_opens_room"),Game->bRoomCleared);
    P->SetActorLocation(FVector(660,0,0)); Game->TryInteract();
    Check(TEXT("nearby_pickup_takes_priority_over_exit"),Game->RoomNumber==1&&P->Coins>0);
    Game->TryInteract();
    Check(TEXT("exit_advances_room"),Game->RoomNumber==2&&!Game->bRoomCleared);
    P->ApplyCombatHit(999,nullptr);
    Check(TEXT("player_death_ends_run"),Game->bGameOver&&P->bDead);
    Game->RestartRun(); P=Game->GetPlayerFighter();
    Check(TEXT("restart_restores_run_state"),Game->RoomNumber==1&&P->Health==P->MaxHealth&&!Game->bGameOver&&P->Coins==0);
    P->ResetFighter({0,0}); P->MoveOnGround({1,0},.1f); const double Straight=P->GetGroundPosition().Size();
    P->ResetFighter({0,0}); P->MoveOnGround({1,1},.1f); const double Diagonal=P->GetGroundPosition().Size();
    Check(TEXT("diagonal_movement_has_equal_speed"),FMath::IsNearlyEqual(Straight,Diagonal,.01));
    P->ResetFighter({699,219}); P->MoveOnGround({1,1},1.f);
    Check(TEXT("movement_clamps_room_boundaries"),P->GetGroundPosition().X<=700&&P->GetGroundPosition().Y<=220);
    for(auto E:Game->Enemies) E->bAIEnabled=false;
    P->ResetFighter({-350,100}); GroundBeforeJump=P->GetGroundPosition().Y; P->StartJump();
    Game->bWaitingForStart=true; Key(EKeys::Enter,true);
}
void ADungeonProbe::SaveReport(ADungeonGameMode* Game)
{
    auto Report=MakeShared<FJsonObject>();
    Report->SetStringField(TEXT("engine"),FEngineVersion::Current().ToString());
    Report->SetStringField(TEXT("map"),GetWorld()->GetMapName());
    Report->SetStringField(TEXT("capture_scope"),TEXT("Continuous viewport frames with fixed 30 FPS simulation; not a realtime performance benchmark. Opt-in automated inputs use live game methods."));
    Report->SetArrayField(TEXT("checks"),Results);
    bool Passed=Results.Num()>0; for(auto R:Results) Passed&=R->AsObject()->GetBoolField(TEXT("passed"));
    Report->SetBoolField(TEXT("passed"),Passed);
    Report->SetNumberField(TEXT("elapsed_simulation_seconds"),Elapsed);
    Report->SetNumberField(TEXT("demo_room"),Game->RoomNumber);
    Report->SetBoolField(TEXT("demo_room_cleared"),Game->bRoomCleared);
    FString JSON; auto Writer=TJsonWriterFactory<>::Create(&JSON); FJsonSerializer::Serialize(Report,Writer);
    FFileHelper::SaveStringToFile(JSON,*(ProofDirectory/TEXT("runtime-report.json")),FFileHelper::EEncodingOptions::ForceUTF8WithoutBOM);
}
void ADungeonProbe::Tick(float Delta)
{
    Super::Tick(Delta); Elapsed+=Delta;
    auto Game=Cast<ADungeonGameMode>(UGameplayStatics::GetGameMode(this)); if(!Game) return;
    if(!bChecked&&Elapsed>.5f) { RunChecks(Game); bChecked=true; }
    if(!bChecked) return;
    auto P=Game->GetPlayerFighter(); if(!P) return;
    if(!bJumpChecked&&Elapsed>.75f)
    {
        Check(TEXT("jump_elevation_independent_of_ground_depth"),P->JumpHeight>1.f&&FMath::IsNearlyEqual(P->GetGroundPosition().Y,GroundBeforeJump,.01f));
        Check(TEXT("enter_starts_play_through_controller"),!Game->bWaitingForStart); Key(EKeys::Enter,false);
        bJumpChecked=true; Game->RestartRun();
    }
    if(!bJumpChecked) return;
    P=Game->GetPlayerFighter();
    if(!bWalkChecked&&Elapsed>1.2f)
    {
        Check(TEXT("controller_movement_drives_walk_animation"),P->AnimationName==TEXT("walk")); bWalkChecked=true;
    }
    Key(EKeys::J,false); Key(EKeys::E,false); Key(EKeys::SpaceBar,false);
    // A simple automated player drives the normal movement/attack/interact entry points.
    if(Elapsed<3.f)
    {
        MoveInput({.8f,.35f});
        Key(EKeys::SpaceBar,Elapsed>1.5f&&Elapsed<1.55f);
    }
    else
    {
        ADungeonFighter* Closest=nullptr; float Distance=MAX_flt;
        for(auto E:Game->Enemies) if(E&&!E->bDead)
        { float D=FVector2D::Distance(P->GetGroundPosition(),E->GetGroundPosition()); if(D<Distance) {Distance=D;Closest=E;} }
        if(Closest&&!P->bDead)
        {
            FVector2D Offset=Closest->GetGroundPosition()-P->GetGroundPosition();
            FVector2D Direction(FMath::Abs(Offset.X)>65.f?FMath::Sign(Offset.X):0.f,FMath::Abs(Offset.Y)>22.f?FMath::Sign(Offset.Y):0.f);
            MoveInput(Direction);
            if(FMath::Abs(Offset.X)>1.f) P->Facing=Offset.X>=0?1.f:-1.f;
            Key(EKeys::J,FMath::Sin(Elapsed*16.f)>0.f);
        }
        else if(Game->bRoomCleared)
        {
            const FDungeonPickup* Nearest=nullptr; float D=MAX_flt;
            for(const auto& Item:Game->Pickups) if(!Item.bConsumed&&(Item.Kind!=TEXT("potion")||P->Health<P->MaxHealth))
            { float V=FVector2D::Distance(P->GetGroundPosition(),Item.Position); if(V<D) {D=V;Nearest=&Item;} }
            if(Nearest)
            {
                const auto Offset=Nearest->Position-P->GetGroundPosition();
                MoveInput({FMath::Abs(Offset.X)>18?FMath::Sign(Offset.X):0,FMath::Abs(Offset.Y)>18?FMath::Sign(Offset.Y):0});
                Key(EKeys::E,D<60&&FMath::Sin(Elapsed*16.f)>0);
            }
            else MoveInput(FVector2D::ZeroVector);
        }
        else MoveInput(FVector2D::ZeroVector);
    }
    if(Elapsed>17.f&&!bSaved) { SaveReport(Game); bSaved=true; }
}
