#pragma once
#include "CoreMinimal.h"
#include "DungeonWorldProjectiles.h"

class ADungeonFighter;

// Recorder observations only. This is separate from the independent Actor
// acceptance tests and has no equipment, combat, timing or save authority.
struct FXBWReloadSocketProofState
{
    static constexpr double DeadlineSeconds=55.;
    struct FShot
    {
        int32 Side=-1;
        DungeonWeaponActions::FAction Action;
        FDungeonWorldProjectile Emission;
        uint64 TargetId=0;
        bool EmissionObserved=false;
    };
    int32 Phase=0,Side=0,CurrentShot=-1;
    double PhaseAt=0,InputAt=-1,PendingShotInput=-1,ArrivalAt=-1;
    FVector2D Origin=FVector2D::ZeroVector,TargetPositions[2];
    TWeakObjectPtr<ADungeonFighter> Targets[2];
    FGuid RunGuid;
    uint64 RoomId=0,StarterId=0,SourceId=0,InstanceId=0,InitialCritDraw=0,WorldCursor=0;
    int32 ShotsPerSide[2]={0,0},ReadyMask[2]={0,0},PrimaryMask[2]={0,0},ReloadMask[2]={0,0};
    bool ReadyValid[2]={true,true},PrimaryValid[2]={true,true},ReloadValid[2]={true,true};
    bool InputIssued=false,ActionObserved=false,PickupOldHeld=true,PickupDuration=true;
    bool SwitchOldHeld=true,SwitchDuration=true,RestartHeldEmpty=true,CancelShotChecked=false;
    double CancelledAt=-1,RefillsBeforeCancel=0;
    DungeonWeaponActions::FAction CurrentReload,CancelledReload,RestartedReload;
    TArray<FShot> Shots;
    TArray<DungeonWeaponActions::FAction> Reloads;
    TSet<FString> Checked;

    static TArray<FString> RequiredChecks()
    {
        return {
            TEXT("xbw_socket_fixture_real_run_single_source_two_static_targets"),
            TEXT("xbw_socket_fresh_enter_opens_qa_initialized_start_gate"),
            TEXT("xbw_socket_normal_e_035_commits_acquired_instance"),
            TEXT("xbw_socket_right_ready_all6_native_stack"),
            TEXT("xbw_socket_right_primary_all6_actor_clock"),
            TEXT("xbw_socket_right_world_bolt_hit_frozen_hand_origin"),
            TEXT("xbw_socket_right_reload_all4_actor_clock"),
            TEXT("xbw_socket_right_loaded3_after_real_reload_commit"),
            TEXT("xbw_socket_left_ready_all6_native_stack"),
            TEXT("xbw_socket_left_primary_all6_actor_clock"),
            TEXT("xbw_socket_left_world_bolt_hit_frozen_hand_origin"),
            TEXT("xbw_socket_left_reload_all4_actor_clock"),
            TEXT("xbw_socket_left_loaded3_after_real_reload_commit"),
            TEXT("xbw_socket_normal_q_roundtrip_same_loaded_instance"),
            TEXT("xbw_socket_real_shot_changes_loaded_to_empty0"),
            TEXT("xbw_socket_insert_frame2_is_visual_without_early_refill"),
            TEXT("xbw_socket_fresh_t_cancel_stays_empty_past_old_deadline"),
            TEXT("xbw_socket_fresh_t_restart_full_duration_then_one_bolt"),
            TEXT("xbw_socket_history_immutable_and_once_only"),
            TEXT("xbw_socket_completed_within_55s")};
    }
};
