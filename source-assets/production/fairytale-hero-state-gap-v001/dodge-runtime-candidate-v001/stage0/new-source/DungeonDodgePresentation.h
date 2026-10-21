#pragma once
#include "CoreMinimal.h"
#include "DungeonDodge.h"

// Read-only actual owner/action facts. This is neither a second clock nor a save schema.
struct FDungeonDodgePresentationSample
{
 bool Active=false,Invulnerable=false;
 uint64 OwnerId=0,ActionId=0,StartEventId=0;
 double SampleTime=0.,Start=0.,End=0.,ReadyAt=0.,Elapsed=0.,Remaining=0.,Travelled=0.;
 FVector2D Direction=FVector2D::ZeroVector;
 DungeonDodge::EBlock Block=DungeonDodge::EBlock::None;
 DungeonDodge::EFinish Finish=DungeonDodge::EFinish::None;
};
