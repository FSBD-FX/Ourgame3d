#pragma once
#include "CoreMinimal.h"
#include "DungeonEquipmentRuntime.h"
#include "DungeonWorldProjectiles.h"

class ADungeonFighter;

// Draft recorder observations only; not connected to UnrealGame Source.
struct FXBWArmorSocketProofState
{
    static constexpr double DeadlineSeconds=55.;
    static constexpr int32 ArmorCount=4,MaxGlobalRetries=2;
    struct FArmor
    {
        FString Id,Token,OldId;
        uint64 SourceId=0,InstanceId=0,OldInstanceId=0;
        FDungeonEquipmentActionView Pickup;
        bool PickupObserved=false,PickupOldHeld=true,PickupDuration=true,Confirmed=false,Committed=false;
        int32 ReadyMask[2]={0,0},PrimaryMask[2]={0,0},ReloadMask[2]={0,0};
        bool ReadyValid[2]={true,true},PrimaryValid[2]={true,true},ReloadValid[2]={true,true};
        bool LoadedAfterCommit[2]={false,false};
        int32 ShotsPerSide[2]={0,0};
    };
    struct FShot
    {
        int32 Armor=-1,Side=-1;
        uint64 TargetId=0;
        DungeonWeaponActions::FAction Action,Reload;
        FDungeonWorldProjectile Emission;
        bool EmissionObserved=false,ReloadObserved=false,NoEarlyRefill=true,LoadedAfterCommit=false;
    };
    FArmor Armors[ArmorCount];
    int32 Phase=0,ArmorIndex=0,Side=0,CurrentShot=-1,GlobalRetries=0,TabPulses=0;
    double PhaseAt=0,InputAt=-1,PendingShotInput=-1,LastTabAt=-1;
    bool InputIssued=false,ActionObserved=false,WeaponOldHeld=true,WeaponDuration=true;
    FDungeonEquipmentActionView WeaponPickup;
    FGuid RunGuid;
    uint64 RoomId=0,StarterId=0,SourceId=0,InstanceId=0,InitialCritDraw=0,WorldCursor=0;
    FVector2D Origin=FVector2D::ZeroVector,TargetPositions[2];
    TWeakObjectPtr<ADungeonFighter> Targets[2];
    TArray<FShot> Shots;
    TSet<FString> Checked;

    static FString ArmorCheck(const FString& Token,const TCHAR* Suffix)
    {return TEXT("xbw_armor_")+Token+TEXT("_")+Suffix;}
    static TArray<FString> RequiredChecks()
    {
        TArray<FString> R={
            TEXT("xbw_armor_fixture_real_run_five_qa_sources_two_static_targets"),
            TEXT("xbw_armor_fresh_enter_opens_initialized_start_gate"),
            TEXT("xbw_armor_normal_e_035_commits_single_xbw_instance")};
        for(const TCHAR* Token:{TEXT("lgt"),TEXT("med"),TEXT("hvy"),TEXT("rob")})
            for(const TCHAR* Suffix:{TEXT("normal_e_050_commit"),TEXT("ready_both_facings_all6_six_stack"),
                TEXT("primary_both_facings_all6_actor_clock"),TEXT("bolts_both_facings_frozen_socket_once"),
                TEXT("reload_both_facings_all4_full_clock"),TEXT("loaded3_only_after_real_commits")})
                R.Add(ArmorCheck(Token,Suffix));
        R.Add(TEXT("xbw_armor_history_immutable_once_same_weapon_instance"));
        R.Add(TEXT("xbw_armor_completed_within_55s"));
        return R;
    }
};
