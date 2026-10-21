#pragma once
#include "CoreMinimal.h"
#include "DungeonDodgePresentation.h"
#include "DungeonFairytaleSwordDodgeProfile.h"
#include "DungeonFairytaleSwordEquipmentBinding.h"

class ADungeonGameMode;
class ADungeonFighter;
namespace DungeonFairytaleSwordDodgeV001
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
 bool Supported=false;
 int32 Frame=-1,Facing=0,NonemptyDrawCount=0;
 FString ProfileId;
 FDungeonDodgePresentationSample Dodge;
 DungeonFairytaleSwordEquipmentBinding::FBinding Binding;
 FVector2D RootSource=FVector2D::ZeroVector,GripSource=FVector2D::ZeroVector,AxisArtist=FVector2D::ZeroVector;
 FVector2D BodyTop=FVector2D::ZeroVector,GripScreen=FVector2D::ZeroVector,SwordTop=FVector2D::ZeroVector,SwordPivotUV=FVector2D::ZeroVector;
 double CanvasSize=0.,SourceToScreenScale=0.,WeaponScale=0.,WeaponWidth=0.,WeaponAngle=0.,TextureU=0.,TextureDU=0.;
 std::array<FDrawSlot,9> Slots;
};
// Actual main player/World and current committed SWD/LGT authorization.
// The future renderer must consume this SAME complete plan after atomic33-resource preflight.
CODEXDUNGEON_API bool BuildDrawPlan(const ADungeonGameMode& Game,const ADungeonFighter& Fighter,
 const FDrawContext& Context,FDrawPlan& Out,FString& Diagnostic);
// Committed-value seam only; it cannot authorize an Actor or invent a valid owner/action.
CODEXDUNGEON_API bool BuildDrawPlanFromCommitted(const DungeonFairytaleSwordEquipmentBinding::FBinding& Binding,
 const FDungeonDodgePresentationSample& Dodge,double Facing,const FProfile& Source,const FDrawContext& Context,
 FDrawPlan& Out,FString& Diagnostic);
}
