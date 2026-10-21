#pragma once
#include "CoreMinimal.h"
#include "DungeonFairytaleSwordAirV001.h"

struct FDungeonFairytaleSwordAirSlotDrawV001
{
 int32 SlotIndex=-1;
 DungeonFairytaleSwordAirV001::EComponent Component=DungeonFairytaleSwordAirV001::EComponent::BodyRest;
 FString TexturePath;
 bool KnownOptionalEmpty=false,TextureReady=false,Drawn=false;
 FVector2D Top=FVector2D::ZeroVector,Size=FVector2D::ZeroVector,UV=FVector2D::ZeroVector,UVSize=FVector2D::ZeroVector;
 double RotationDegrees=0.,DrawScale=1.;
 FVector2D RotationPivot=FVector2D::ZeroVector;
 bool ScalePosition=false;
 FLinearColor TraceTint=FLinearColor::White;
};
struct FDungeonFairytaleSwordAirDrawV001
{
 uint64 DrawId=0,PlayerEntityId=0;
 double SimulationTime=0.;
 bool OptIn=false,Drawn=false,AtomicPreflightReady=false;
 FString MissingReason;
 DungeonFairytaleSwordAirV001::FDrawContext Context;
 DungeonFairytaleSwordAirV001::FDrawPlan Plan;
 FLinearColor Tint=FLinearColor::White;
 TArray<FString> ActualRenderedStack;
 TArray<FDungeonFairytaleSwordAirSlotDrawV001> Slots;
 TArray<DungeonFairytaleSwordAirV001::FResidentTexture> ResidentTextures;
};
