#pragma once
#include "CoreMinimal.h"
#include "DungeonFairytaleSwordDodgePlan.h"

struct FDungeonFairytaleSwordDodgeResidentTexture
{
 FString TexturePath,ClassName;
 int32 Width=0,Height=0;
 bool ResourceReady=false,PendingInitialization=false;
};
struct FDungeonFairytaleSwordDodgeSlotDraw
{
 int32 SlotIndex=-1;
 DungeonFairytaleSwordDodgeV001::EComponent Component=DungeonFairytaleSwordDodgeV001::EComponent::BodyRest;
 FString TexturePath;
 bool KnownOptionalEmpty=false,TextureReady=false,Drawn=false;
 FVector2D Top=FVector2D::ZeroVector,Size=FVector2D::ZeroVector,UV=FVector2D::ZeroVector,UVSize=FVector2D::ZeroVector;
 double RotationDegrees=0.,DrawScale=1.;
 FVector2D RotationPivot=FVector2D::ZeroVector;
 bool ScalePosition=false;
 FLinearColor TraceTint=FLinearColor::White;
};
struct FDungeonFairytaleSwordDodgeDraw
{
 uint64 DrawId=0,PlayerEntityId=0;
 double SimulationTime=0.;
 bool OptIn=false,Drawn=false,AtomicPreflightReady=false;
 FString MissingReason;
 DungeonFairytaleSwordDodgeV001::FDrawContext Context;
 DungeonFairytaleSwordDodgeV001::FDrawPlan Plan; // The exact plan actually consumed, never a second observer planner.
 TArray<FString> ActualRenderedStack;
 FLinearColor Tint=FLinearColor::White;
 TArray<FDungeonFairytaleSwordDodgeSlotDraw> Slots; // All nine are nonempty in every Dodge phase.
 TArray<FDungeonFairytaleSwordDodgeResidentTexture> ResidentTextures; // Complete32 plus existing sword33.
};
