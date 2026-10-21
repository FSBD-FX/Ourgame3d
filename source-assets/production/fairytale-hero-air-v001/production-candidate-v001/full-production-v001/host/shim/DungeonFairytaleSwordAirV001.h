#pragma once
#include "CoreMinimal.h"
#include "DungeonHeroAirPresentation.h"
#include "DungeonFairytaleSwordEquipmentBinding.h"
#include <array>

class ADungeonGameMode;
class ADungeonFighter;
namespace DungeonFairytaleSwordAirV001
{
inline constexpr const TCHAR* CommandLineFlag=TEXT("DungeonFairytaleSwordAirPreview");
inline constexpr int32 PoseCount=6,LayersPerPose=8,SlotCount=9,ResidentCount=49;
enum class EPose:uint8 {None,RiseEarly,RiseLate,Apex,Fall,LandingImpact,LandingSettle};
enum class EComponent:uint8 {BodyRest,ShoulderFar,Chest,NearArmWithoutHand,ShoulderNear,HelmetForeground,FarHandForeground,NearHand,IndependentSword};
struct FSelection
{
 bool Valid=false;
 EPose Pose=EPose::None;
 int32 Frame=-1;
};
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
 EPose Pose=EPose::None;
 FVector2D Root=FVector2D::ZeroVector,Grip=FVector2D::ZeroVector,AxisArtist=FVector2D::ZeroVector;
 std::array<FTextureSource,LayersPerPose> Layers{};
 std::array<EComponent,SlotCount> SlotOrder{};
 int32 ExpectedNonemptyDrawCount=0;
};
struct FProfile
{
 // Stage0 deliberately has no artist source/path/hash/marker approval.
 FString ProfileId,SourceClosureSHA256,SwordTexturePath,SwordSourceSHA256;
 bool SourceClosureVerified=false;
 int32 CanvasSource=512;
 double StandingExtent=416.,StandingDisplay=72.,HeightProjection=.70,WeaponScale=.5;
 FVector2D ComponentGrip=FVector2D::ZeroVector;
 std::array<FFrame,PoseCount> Frames{};
};
struct FDrawContext
{
 FVector2D GroundScreen=FVector2D::ZeroVector;
 double UIScale=1.,JumpHeight=0.;
 FLinearColor Tint=FLinearColor::White;
};
struct FDrawSlot
{
 EComponent Component=EComponent::BodyRest;
 FString TexturePath;
 bool KnownOptionalEmpty=false,Enabled=false; // None disables three armor slots, never changes source alpha ownership.
};
struct FResidentTexture
{
 FString TexturePath,ClassName;
 int32 Width=0,Height=0;
 bool ResourceReady=false,PendingInitialization=false;
};
struct FDrawPlan
{
 bool Supported=false;
 int32 Frame=-1,Facing=0,NonemptyDrawCount=0;
 EPose Pose=EPose::None;
 FString ProfileId;
 FDungeonHeroAirSample Sample;
 DungeonFairytaleSwordEquipmentBinding::FBinding Binding;
 FVector2D RootSource=FVector2D::ZeroVector,GripSource=FVector2D::ZeroVector,AxisArtist=FVector2D::ZeroVector;
 FVector2D BodyTop=FVector2D::ZeroVector,GripScreen=FVector2D::ZeroVector,SwordTop=FVector2D::ZeroVector,SwordPivotUV=FVector2D::ZeroVector;
 double CanvasSize=0.,SourceToScreenScale=0.,WeaponScale=0.,WeaponWidth=0.,WeaponAngle=0.,TextureU=0.,TextureDU=0.;
 FLinearColor Tint=FLinearColor::White;
 std::array<FDrawSlot,SlotCount> Slots{};
};
CODEXDUNGEON_API const FProfile& Profile();
// Future pure visual rule: air iff H>0 OR V>0; >315, (90,315], [-90,90], <-90.
// Landing only H=V=0 and age [0,.06),[.06,.12); never locks input/movement.
CODEXDUNGEON_API bool Select(const FDungeonHeroAirSample& Sample,FSelection& Out,FString& Diagnostic);
CODEXDUNGEON_API bool BuildDrawPlanFromCommitted(const DungeonFairytaleSwordEquipmentBinding::FBinding& Binding,
 const FDungeonHeroAirSample& Sample,const FProfile& Source,const FDrawContext& Context,FDrawPlan& Out,FString& Diagnostic);
CODEXDUNGEON_API bool BuildDrawPlan(const ADungeonGameMode& Game,const ADungeonFighter& Fighter,
 const FDrawContext& Context,FDrawPlan& Out,FString& Diagnostic);
// Actual texture facts only; all48 body/armor sources plus the independent sword.
// Production must run this complete preflight before submitting any of nine slots.
CODEXDUNGEON_API bool ValidateResidentSet(const FProfile& Source,const TArray<FResidentTexture>& Residents,FString& Diagnostic);
}
