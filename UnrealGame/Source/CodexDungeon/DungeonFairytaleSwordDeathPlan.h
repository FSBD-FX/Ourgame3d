#pragma once
#include "CoreMinimal.h"
#include "DungeonDeathPresentation.h"
#include "DungeonFairytaleSwordDeathProfile.h"
#include "DungeonFairytaleSwordEquipmentBinding.h"

class ADungeonGameMode;
class ADungeonFighter;
namespace DungeonFairytaleSwordDeathV001
{
struct FDrawContext
{
 FVector2D GroundScreen=FVector2D::ZeroVector;
 double UIScale=1.,JumpHeight=0.;
};
struct FDrawSlot
{
 EComponent Component=EComponent::BodyRest;
 FString TexturePath;
 bool KnownOptionalEmpty=false;
};
struct FDrawPlan
{
 bool Supported=false,VisualSwordReleased=false,LastFrameHeld=false;
 int32 Frame=-1,Facing=0,NonemptyDrawCount=0;
 FString ProfileId;
 FDungeonDeathPresentationSample Death;
 DungeonFairytaleSwordEquipmentBinding::FBinding Binding;
 FVector2D RootSource=FVector2D::ZeroVector,SwordAnchorSource=FVector2D::ZeroVector,AxisArtist=FVector2D::ZeroVector;
 FVector2D BodyTop=FVector2D::ZeroVector,SwordAnchorScreen=FVector2D::ZeroVector,SwordTop=FVector2D::ZeroVector,SwordPivotUV=FVector2D::ZeroVector;
 double CanvasSize=0.,SourceToScreenScale=0.,WeaponScale=0.,WeaponWidth=0.,WeaponAngle=0.,TextureU=0.,TextureDU=0.;
 FLinearColor Tint=FLinearColor::White; // Terminal HitFlash is not a new material clock.
 std::array<FDrawSlot,9> Slots;
};
CODEXDUNGEON_API bool BuildDrawPlan(const ADungeonGameMode& Game,const ADungeonFighter& Fighter,
 const FDrawContext& Context,FDrawPlan& Out,FString& Diagnostic);
// Value seam only. Actual player/World authorization belongs to BuildDrawPlan.
// Both successful and rejected planning must leave every native owner unchanged.
CODEXDUNGEON_API bool BuildDrawPlanFromCommitted(const DungeonFairytaleSwordEquipmentBinding::FBinding& Binding,
 const FDungeonDeathPresentationSample& Death,double Facing,const FProfile& Source,const FDrawContext& Context,
 FDrawPlan& Out,FString& Diagnostic);
}
