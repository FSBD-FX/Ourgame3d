#pragma once
#include "CoreMinimal.h"
#include "DungeonHurtPresentation.h"
#include "DungeonFairytaleSwordHurtProfile.h"
#include "DungeonFairytaleSwordEquipmentBinding.h"

class ADungeonGameMode;
class ADungeonFighter;
namespace DungeonFairytaleSwordHurtV001
{
struct FDrawContext
{
 // Final screen pixel coordinate of actual actor Ground, supplied by HUD Screen(Ground()).
 FVector2D GroundScreen=FVector2D::ZeroVector;
 double UIScale=1.,JumpHeight=0.;
};
struct FDrawSlot
{
 EComponent Component=EComponent::BodyRest;
 FString TexturePath;
 bool KnownOptionalEmpty=false; // Source still must exist/load/validate; never count as drawn.
};
struct FDrawPlan
{
 bool Supported=false;
 int32 Frame=-1,Facing=0,NonemptyDrawCount=0;
 FString ProfileId;
 FDungeonHurtPresentationSample Hurt;
 DungeonFairytaleSwordEquipmentBinding::FBinding Binding;
 FVector2D RootSource=FVector2D::ZeroVector,GripSource=FVector2D::ZeroVector,AxisArtist=FVector2D::ZeroVector;
 FVector2D BodyTop=FVector2D::ZeroVector,GripScreen=FVector2D::ZeroVector,SwordTop=FVector2D::ZeroVector,SwordPivotUV=FVector2D::ZeroVector;
 double CanvasSize=0.,SourceToScreenScale=0.,WeaponScale=0.,WeaponWidth=0.,WeaponAngle=0.,TextureU=0.,TextureDU=0.;
 // BodyRest,Far,Chest,NearArm,Near,Helmet,FarHand,IndependentSword,NearHand.
 // The future actual renderer MUST consume this exact complete plan, preflight all
 // 8 source textures + sword before any quad, and skip only declared known-empty sources.
 std::array<FDrawSlot,9> Slots;
};
// Production entry: actual World/player ownership and committed Binding; real Fighter
// QueryHurtPresentation; immutable source Profile. Failure is atomic/read-only.
CODEXDUNGEON_API bool BuildDrawPlan(const ADungeonGameMode& Game,const ADungeonFighter& Fighter,
 const FDrawContext& Context,FDrawPlan& Out,FString& Diagnostic);
// Pure committed-value seam, NOT actor authorization. Real entry above must call this
// SAME planner; tests may reject copied bad source data without mutating any native owner.
CODEXDUNGEON_API bool BuildDrawPlanFromCommitted(const DungeonFairytaleSwordEquipmentBinding::FBinding& Binding,
 const FDungeonHurtPresentationSample& Hurt,double Facing,const FProfile& Source,const FDrawContext& Context,
 FDrawPlan& Out,FString& Diagnostic);
}
