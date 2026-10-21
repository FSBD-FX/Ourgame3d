#pragma once
#include "CoreMinimal.h"
#include <limits>
#include "DungeonGroundWalkPhase.h"
#include "DungeonFairytaleSwordBodyV001.inl"

namespace DungeonFairytaleSwordWalkV001
{
inline constexpr TCHAR AnimationLabel[]=TEXT("walk_distance_v001");
struct FFrame
{
    FString Body,BodyRest,NearArmWithoutHand,HelmetForeground,NearHand;
    FString ShoulderFar,Chest,ShoulderNear;
    DungeonFairytaleSwordBodyV001::FMarker Marker{};
    bool MeasurementsSupplied=false;
};
struct FProfile
{
    DungeonGroundWalk::FPolicy Gait;
    std::array<FFrame,6> Frames;
    // Set only from a retained, verified six-phase assembly and measurements.
    bool SourceClosureVerified=false;
};
const FProfile& Profile();
inline bool Valid()
{
    const auto& P=Profile();
    if(!P.SourceClosureVerified||!DungeonGroundWalk::Valid(P.Gait)
        ||P.Gait.CycleSeconds>double(std::numeric_limits<float>::max()))return false;
    for(const auto& F:P.Frames)
    {
        const auto InCanvas=[](const FVector2D& V){return FMath::IsFinite(V.X)&&FMath::IsFinite(V.Y)
            &&V.X>=0.&&V.X<=512.&&V.Y>=0.&&V.Y<=512.;};
        if(!F.MeasurementsSupplied||!InCanvas(F.Marker.Root)||!InCanvas(F.Marker.Grip)
            ||!FMath::IsFinite(F.Marker.Axis.X)||!FMath::IsFinite(F.Marker.Axis.Y)
            ||F.Marker.Axis==FVector2D::ZeroVector)return false;
        TSet<FString> Unique;
        for(const FString* Path:{&F.Body,&F.BodyRest,&F.NearArmWithoutHand,&F.HelmetForeground,&F.NearHand,
            &F.ShoulderFar,&F.Chest,&F.ShoulderNear})
        {
            if(!Path->StartsWith(TEXT("/Game/Production/"))||!Path->Contains(TEXT("."))||Unique.Contains(*Path))return false;
            Unique.Add(*Path);
        }
    }
    return true;
}
inline const FFrame* Find(int32 Index)
{return Valid()&&Index>=0&&Index<6?&Profile().Frames[Index]:nullptr;}
}
#include "DungeonFairytaleSwordWalkDataV001.inl"
