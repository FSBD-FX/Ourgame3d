#pragma once
namespace DungeonCandidateAssemblyTuning {
inline constexpr float WeaponScale=.40f;
inline float Angle(const FString& Clip,int32,float Authored)
{
    if(Clip==TEXT("idle")) return 35.f;
    if(Clip==TEXT("walk")) return 30.f;
    // Corrected primary angles already include measured face/ground clearance.
    return Authored;
}
}
