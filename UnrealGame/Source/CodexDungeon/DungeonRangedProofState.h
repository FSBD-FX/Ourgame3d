#pragma once
#include "CoreMinimal.h"
#include "DungeonWeaponActions.h"

class ADungeonFighter;

// Opt-in QA observations only. No authority, save schema or gameplay state lives here.
struct FRangedProofState
{
    static constexpr double DeadlineSeconds=45.;
    int32 Phase=0;
    double PhaseAt=0,ArrivalAt=-1,InputAt=-1;
    FVector2D Origin=FVector2D::ZeroVector;
    uint64 StarterId=0,SourceIds[3]={0,0,0},InstanceIds[3]={0,0,0};
    TWeakObjectPtr<ADungeonFighter> RangedTargets[3],SpearTargets[3];
    DungeonWeaponActions::FAction Actions[5]; // XBW J/K, STF J/K, SPR K.
    double FocusAtInput[5]={0,0,0,0,0};
    uint64 CritAtInput[5]={0,0,0,0,0};
    double ReloadStarts[2]={-1,-1},ReloadEnds[2]={-1,-1};
    bool ReloadValid[2]={true,true};
    bool InputIssued=false,ActionObserved=false,OldHeld=true,DurationValid=true,SelectionObserved=false;
    uint64 SelectionRevision=0,WorldCursor=0;
    double CrossbowCooldown=0,StaffCooldown=0,FinalSwitchAt=0,FocusBeforeFinalSwitch=0,LastSpendBeforeFinalSwitch=0;
    uint64 FocusCursorBeforeFinalSwitch=0;
    int32 FocusHistoryBeforeFinalSwitch=0;
    int32 ReadyFrameMask[2]={0,0};
    bool ReadyStackValid[2]={true,true};
    bool HeldFiringSeen=false,HeldActionIdentityValid=true;
    int32 HeldReloadFrameMask=0;
    int32 PrimaryFrameMask=0,PrimaryPhaseMask=0;
    bool PrimaryClockStackValid=true;

    static TArray<FString> ReadyChecks(bool HeldIdentity=false,bool PrimaryBody=false)
    {
        TArray<FString> Names={TEXT("xbw_ready_real_run_starter_and_single_qa_source"),TEXT("xbw_ready_single_authored_ground_target"),
            TEXT("xbw_normal_e_035_commit_real_instance"),TEXT("xbw_ready_right_all6_actual_four_layer_stack"),
            TEXT("xbw_ready_left_all6_actual_four_layer_stack"),TEXT("xbw_normal_j_single_world_bolt_and_real_hit"),
            TEXT("xbw_last_shot_full_recovery_then_110_reload"),TEXT("xbw_ready_real_release_audio_request"),
            TEXT("ranged_completed_within_45s")};
        if(HeldIdentity) Names.Add(TEXT("xbw_ground_firing_and_all6_reload_keep_held_body_without_blade_trail"));
        if(PrimaryBody) Names.Add(TEXT("xbw_authored_primary_all_three_phases_match_drawn_actor_clock_and_stack"));
        return Names;
    }

    static TArray<FString> RequiredChecks()
    {
        return {
            TEXT("ranged_real_run_starter_and_qa_sources"),
            TEXT("ranged_fixture_authored_targets_and_ground_positions"),
            TEXT("xbw_normal_e_035_commit_real_instance"),
            TEXT("xbw_normal_j_single_world_bolt_and_real_hit"),
            TEXT("xbw_last_shot_full_recovery_then_110_reload"),
            TEXT("xbw_normal_k_nearest_two_second_sixty_percent"),
            TEXT("xbw_skill_single_crit_and_instance_cooldown"),
            TEXT("xbw_second_full_reload_no_repeat_or_refund"),
            TEXT("ranged_normal_q_preserves_crossbow_instance"),
            TEXT("stf_full_slots_fresh_e_enter_slot0_commit"),
            TEXT("stf_normal_j_magic_fireball_focus10_no_burn"),
            TEXT("stf_normal_d_enters_actual_fireline_range"),
            TEXT("stf_normal_k_real_ground_window_focus24"),
            TEXT("stf_actual_burn_three_ticks_fixed2_per_target"),
            TEXT("spr_full_slots_e_right_enter_backup_commit"),
            TEXT("spr_normal_q_activates_acquired_instance"),
            TEXT("spr_normal_k_three_independent_nearest_targets"),
            TEXT("ranged_normal_q_back_to_same_staff_without_reset"),
            TEXT("ranged_hud_real_release_launch_burn_audio_requests"),
            TEXT("ranged_completed_within_45s")};
    }
};
