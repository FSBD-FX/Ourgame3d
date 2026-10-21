#pragma once
#include "CoreMinimal.h"
#include "DungeonFairytaleSwordDeathPlan.h"

struct FDungeonFairytaleSwordDeathResidentTexture
{
 FString TexturePath,ClassName;
 int32 Width=0,Height=0;
 bool ResourceReady=false;
};
struct FDungeonFairytaleSwordDeathSlotDraw
{
 int32 SlotIndex=-1;
 DungeonFairytaleSwordDeathV001::EComponent Component=DungeonFairytaleSwordDeathV001::EComponent::BodyRest;
 FString TexturePath;
 bool KnownOptionalEmpty=false,TextureReady=false,Drawn=false;
 FVector2D Top=FVector2D::ZeroVector,Size=FVector2D::ZeroVector,UV=FVector2D::ZeroVector,UVSize=FVector2D::ZeroVector;
 double RotationDegrees=0.;
 FVector2D RotationPivot=FVector2D::ZeroVector;
 double DrawScale=1.;
 bool ScalePosition=false;
};
// Process-local actual submissions only. Nothing here enters saves/gameplay.
struct FDungeonFairytaleSwordDeathDraw
{
 uint64 DrawId=0,PlayerEntityId=0;
 double SimulationTime=0.;
 bool OptIn=false,Drawn=false,AtomicPreflightReady=false;
 FString MissingReason;
 DungeonFairytaleSwordDeathV001::FDrawContext Context;
 DungeonFairytaleSwordDeathV001::FDrawPlan Plan; // SAME plan actually consumed by renderer.
 FLinearColor Tint=FLinearColor::White;
 TArray<FDungeonFairytaleSwordDeathResidentTexture> ResidentTextures; // Actual complete40 + reusedSword41.
 TArray<FDungeonFairytaleSwordDeathSlotDraw> Slots;
 TArray<FString> ActualRenderedStack;
};
