#pragma once
#include "CoreMinimal.h"

// Runtime room-center space (cm). Presentation/camera reads the same source.
// EV-042: assistant-proposed larger space; spawn/content/combat rules are unchanged.
namespace DungeonRoomLayout
{
inline constexpr double MinX = -1350.0;
inline constexpr double MaxX = 1350.0;
inline constexpr double MinY = -420.0;
inline constexpr double MaxY = 440.0;

inline FBox2D CenterBounds()
{
    return FBox2D(FVector2D(MinX,MinY),FVector2D(MaxX,MaxY));
}

// Development exploration layout. A single record is shared by gameplay and
// presentation; this is not a D07 node graph or a formal D08 reward source.
struct FDescription
{
    FName Id = FName(TEXT("qa.scene.exploration.v001"));
    uint32 Version = 1;
    FVector2D Entry = {-1180.,0.};
    FVector2D Exit = {1180.,0.};
    FVector2D ExitHalfExtent = {80.,40.};
    FBox2D Barrier = FBox2D(FVector2D(-1100.,60.),FVector2D(-700.,160.));
    FVector2D Survey = {-920.,300.};
};

inline FDescription ExplorationPreview() { return {}; }
}
