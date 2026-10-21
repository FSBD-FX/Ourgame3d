#pragma once
#include "CoreMinimal.h"
#include "DungeonFairytaleSwordSecondaryPlanV001.h"
#include "DungeonFairytaleSwordEquipmentBinding.h"

struct FDungeonFairytaleSwordSecondaryResidentV001
{
 FString TexturePath,ClassName;
 int32 Width=0,Height=0;
 bool Ready=false,PendingInitialization=false;
};
struct FDungeonFairytaleSwordSecondarySlotV001
{
 int32 SlotIndex=-1;
 DungeonFairytaleSwordSecondaryV001::EComponent Component=DungeonFairytaleSwordSecondaryV001::EComponent::BodyRest;
 FString TexturePath;
 bool Selected=false,TextureReady=false,Drawn=false;
 FVector2D Top=FVector2D::ZeroVector,Size=FVector2D::ZeroVector;
 FVector2D UV=FVector2D::ZeroVector,UVSize=FVector2D::ZeroVector,RotationPivot=FVector2D::ZeroVector;
 float RotationDegrees=0.f,DrawScale=1.f;
 bool ScalePosition=false;
 FLinearColor Tint=FLinearColor::White;
};
// Same-callback sample, binding, resource closure and submitted float values.
// DrawId is monotonic; all other fields clear before Death/Hurt/no-Canvas/restore.
struct FDungeonFairytaleSwordSecondaryDrawV001
{
 uint64 DrawId=0,PlayerEntityId=0;
 bool OptIn=false,OwnsBranch=false,ProfileReady=false,AtomicPreflightReady=false,Drawn=false;
 FString MissingReason,ProfileId,SourceContractSha256;
 DungeonFairytaleSwordSecondaryV001::FSample Sample;
 DungeonFairytaleSwordSecondaryV001::FGeometryContext Context;
 DungeonFairytaleSwordSecondaryV001::FGeometry Geometry;
 DungeonFairytaleSwordEquipmentBinding::FBinding Binding;
 int32 ExpectedDrawCount=0;
 TArray<FDungeonFairytaleSwordSecondaryResidentV001> ResidentTextures;
 TArray<FDungeonFairytaleSwordSecondarySlotV001> Slots;
 TArray<FString> ActualRenderedStack;
};
