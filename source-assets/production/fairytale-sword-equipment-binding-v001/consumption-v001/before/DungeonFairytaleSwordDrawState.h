#pragma once

#include "CoreMinimal.h"

// EV048 ordinary-input presentation trial only. Active means this opt-in
// presenter was called, not that the combat kernel currently has an action.
// Supported covers only new Ready idle and grounded SWD primary stage0 sources.
// Thumb, axis sign, hand masks, foot drift and blade/helmet clearance are unaccepted.
struct FDungeonFairytaleSwordDraw
{
    bool Active=false, Supported=false, TextureReady=false;
    // Opt-in candidates: Ready4 and six grounded Primary1 source phases only.
    bool ArmorPreview=false, ArmorReady=false, ArmorDrawn=false;
    uint64 DrawId=0, ActionId=0, InstanceId=0;
    double SimulationTime=0., ActionStart=0., ActiveAt=0., ActiveEnd=0., ActionEnd=0.;
    double CanvasSize=0., WeaponAngle=0., WeaponScale=0., WeaponWidth=0.;
    int32 Facing=0, Frame=-1, Stage=-1;
    FString Clip, TexturePath, WeaponPath, NativeScreenshotPath;
    FVector2D Root=FVector2D::ZeroVector, Grip=FVector2D::ZeroVector, GripScreen=FVector2D::ZeroVector;
    TArray<FString> DrawStack;
};
