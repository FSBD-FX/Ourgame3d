#pragma once
// Rendering-only candidate tuning. Original authored .55 scale/angles remain in
// assembly-markers-v001.json. At .55 the idle blade tip was50 source pixels below
// the foot root; use a compact sword and keep relaxed carry above the ground plane.
namespace DungeonCandidateAssemblyTuning {
inline constexpr float WeaponScale = .40f;
inline float Angle(const FString& Clip,int32 Index,float Authored)
{
    if (Clip==TEXT("idle")) return 35.f;
    if (Clip==TEXT("walk")) return 30.f;
    if (Clip==TEXT("primary_3") && Index==3) return 25.f;
    if (Clip==TEXT("primary_3") && Index==4) return 40.f;
    return Authored;
}
}
