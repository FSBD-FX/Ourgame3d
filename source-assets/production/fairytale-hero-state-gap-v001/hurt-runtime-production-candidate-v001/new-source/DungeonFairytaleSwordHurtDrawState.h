#pragma once
#include "CoreMinimal.h"
#include "DungeonFairytaleSwordHurtPlan.h"

// Process-only exact actual HUD submissions. This does not enter saves/gameplay.
struct FDungeonFairytaleSwordHurtSlotDraw
{
 int32 SlotIndex=-1;
 DungeonFairytaleSwordHurtV001::EComponent Component=DungeonFairytaleSwordHurtV001::EComponent::BodyRest;
 FString TexturePath;
 bool KnownOptionalEmpty=false,TextureReady=false,Drawn=false;
 FVector2D Top=FVector2D::ZeroVector,Size=FVector2D::ZeroVector,UV=FVector2D::ZeroVector,UVSize=FVector2D::ZeroVector;
 double RotationDegrees=0.;
 FVector2D RotationPivot=FVector2D::ZeroVector;
 double DrawScale=1.;
 bool ScalePosition=false;
};
struct FDungeonFairytaleSwordHurtDraw
{
 uint64 DrawId=0,PlayerEntityId=0;
 double SimulationTime=0.;
 bool OptIn=false,Drawn=false,AtomicPreflightReady=false;
 FString MissingReason;
 DungeonFairytaleSwordHurtV001::FDrawContext Context;
 // The SAME complete plan used by renderer. Observer must not substitute a second planner.
 DungeonFairytaleSwordHurtV001::FDrawPlan Plan;
 TArray<FString> ActualRenderedStack;
 FLinearColor Tint=FLinearColor::White;
 // Nine declared slots including known-transparent FarHand1/2/3; Drawn=false there.
 TArray<FDungeonFairytaleSwordHurtSlotDraw> Slots;
};
