#pragma once
#include "CoreMinimal.h"
#include <array>

namespace DungeonFairytaleSwordDeathV001
{
inline constexpr const TCHAR* CommandLineFlag=TEXT("DungeonFairytaleSwordDeathPreview");
enum class EComponent:uint8 {BodyRest,ShoulderFar,Chest,NearArmWithoutHand,ShoulderNear,HelmetForeground,FarHandForeground,NearHand,IndependentSword};
struct FTextureSource
{
 EComponent Component=EComponent::BodyRest;
 FString TexturePath,SourceSHA256,SourceRGBASHA256;
 uint32 SourceAlphaNonzero=0;
 bool KnownOptionalEmpty=false;
};
struct FFrame
{
 int32 Frame=-1;
 double KeyAge=0.;
 FVector2D Root=FVector2D::ZeroVector,SwordAnchor=FVector2D::ZeroVector,AxisArtist=FVector2D::ZeroVector;
 bool VisualSwordReleased=false;
 // Five exclusive original body owners plus three armor layers; never WholeBody.
 std::array<FTextureSource,8> Layers;
 std::array<EComponent,9> SlotOrder;
 int32 ExpectedNonemptyDrawCount=0;
};
struct FProfile
{
 FString ProfileId,SourceClosureSHA256,SwordTexturePath,SwordSourceSHA256;
 bool SourceClosureVerified=false; // Source closure only, never native/final acceptance.
 int32 CanvasSource=512;
 double StandingExtent=416.,StandingDisplay=72.,WeaponScale=.5;
 FVector2D ComponentGrip=FVector2D(99.,256.);
 std::array<FFrame,5> Frames;
};
CODEXDUNGEON_API const FProfile& Profile();
}
