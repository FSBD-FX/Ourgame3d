#pragma once
#include "CoreMinimal.h"
#include <array>

namespace DungeonFairytaleSwordHurtV001
{
inline constexpr const TCHAR* CommandLineFlag=TEXT("DungeonFairytaleSwordHurtPreview");
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
 FVector2D Root=FVector2D::ZeroVector,Grip=FVector2D::ZeroVector,AxisArtist=FVector2D::ZeroVector;
 // 5 real body owners + 3 real armor layers. NO whole Body texture exists here.
 std::array<FTextureSource,8> Layers;
 int32 ExpectedNonemptyDrawCount=0; // Includes exactly one existing independent sword.
};
struct FProfile
{
 FString ProfileId,SourceClosureSHA256,SwordTexturePath;
 bool SourceClosureVerified=false; // Retained source preparation; NOT a native/art acceptance flag.
 int32 CanvasSource=512;
 double StandingExtent=416.,StandingDisplay=72.,WeaponScale=.5;
 FVector2D ComponentGrip=FVector2D(99.,256.);
 std::array<FFrame,4> Frames;
};
CODEXDUNGEON_API const FProfile& Profile();
}
