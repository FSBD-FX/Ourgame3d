#pragma once
#include "CoreMinimal.h"

class ADungeonFighter;

// Explicit normal-input QA observations, never gameplay or persistence authority.
struct FSceneProofState
{
    static constexpr double DeadlineSeconds=55.;
    int32 Phase=0,InitialGameRoom=0,InitialExplored=0,RevealedExplored=0;
    double PhaseAt=0,ArrivalAt=-1,InputAt=-1,LastKnightHP=110.;
    bool InputIssued=false,SwordActionObserved=false;
    FGuid RunGuid;
    uint64 RoomId=0,StarterId=0,KnightId=0,SurveyId=0,ExitId=0,ResetSerial=0;
    uint64 SurveyNextInstance=0,ExitNextInstance=0,ExitCritDraw=0;
    int32 SurveyCoins=0,SurveyPickups=0,SurveySources=0,ExitCoins=0;
    double ExitHP=0,ExitFocus=0,ExitAmmo=0,ExitCooldown=0;
    FVector2D Entry=FVector2D::ZeroVector,Survey=FVector2D::ZeroVector,Exit=FVector2D::ZeroVector;
    FBox2D Barrier;
    TWeakObjectPtr<ADungeonFighter> Knight;

    static TArray<FString> RequiredChecks()
    {
        return {
            TEXT("scene_real_run_starter_unique_knight_and_two_objects"),
            TEXT("scene_fresh_enter_opens_real_start_gate"),
            TEXT("scene_normal_w_blocked_by_actual_world_wall"),
            TEXT("scene_normal_west_bypass_reveals_survey"),
            TEXT("scene_fresh_e_survey_once_without_reward"),
            TEXT("scene_repeat_e_never_repeats_survey_or_income"),
            TEXT("scene_retreat_keeps_memory_outside_visibility"),
            TEXT("scene_normal_sword_damage_clears_unique_knight"),
            TEXT("scene_old_665_e_cannot_open_or_change_room"),
            TEXT("scene_actual_1180_e_opens_current_room_confirmation"),
            TEXT("scene_normal_escape_cancels_without_travel"),
            TEXT("scene_fresh_enter_keeps_run_instances_and_resets_new_room_hud"),
            TEXT("scene_completed_within_55s")};
    }
};
