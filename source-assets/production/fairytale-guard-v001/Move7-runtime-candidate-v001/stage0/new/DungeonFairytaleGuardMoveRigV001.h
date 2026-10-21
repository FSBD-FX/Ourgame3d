#pragma once
#include "CoreMinimal.h"
#include "DungeonGuardMovePresentation.h"
namespace DungeonFairytaleGuardMoveRigV001
{
inline constexpr const TCHAR* CommandLineFlag=TEXT("DungeonFairytaleGuardMoveRigPreview");
enum class EComponent:uint8 {BodyRest,NearThigh,NearShin,NearFoot,FarThigh,FarShin,FarFoot};
struct FSurfaceMarker
{FString Name;FVector2D Point=FVector2D::ZeroVector;FColor SurfaceRGBA=FColor::Transparent;};
struct FSourcePart
{
 EComponent Component=EComponent::BodyRest;
 FString TexturePath,SourceSHA256,SourceRGBASHA256;
 int32 NativeBatchId=0;double ComponentToRestScale=0.;
 TArray<FSurfaceMarker> Markers;
};
struct FProfile
{
 FString ProfileId,ProfileSHA256,SourceSnapshotSHA256,RegistrationEvidenceSHA256,TrialApprovalRecord;
 bool SourceClosureVerified=false,TrialAllowed=false,FinalAccepted=false;
 int32 CanvasSize=512,NearBranch=-1,FarBranch=1;
 double StandingExtent=449.,TargetBodyHeight=100.8,CycleWorld=128.,HalfCycleWorld=64.;
 double FootHalfStance=20.8,SwingLift=2.,BodyBob=4.;
 FVector2D SourceGround=FVector2D(250.,580.);
 TArray<FSourcePart> Sources;
 TArray<EComponent> LayerOrder;
};
struct FDrawContext
{FVector2D GroundScreen=FVector2D::ZeroVector;double UIScale=1.,JumpHeight=0.;};
// Direct DrawTexture values: scalar position/size/angle/UV arguments are float;
// FVector2D RotationPivotUV remains UE5.5 double, and tint remains FLinearColor.
struct FSubmittedQuad
{
 float X=0.f,Y=0.f,Width=0.f,Height=0.f,U=0.f,V=0.f,UL=1.f,VL=1.f;
 float RotationDegrees=0.f,DrawScale=1.f;
 bool ScalePosition=false;
 FVector2D RotationPivotUV=FVector2D::ZeroVector;
 FLinearColor Tint=FLinearColor::White;
};
struct FSolveInput
{
 uint64 EntityId=0,AcceptedPathOwnerId=0;
 double AcceptedDistance=0.;int32 Facing=0;
 FDrawContext Context;
};
struct FPartPose
{
 EComponent Component=EComponent::BodyRest;
 FString TexturePath,SourceSHA256,SourceRGBASHA256;
 int32 NativeBatchId=0;
 double ComponentToRestScale=0.,SourceRotationRadians=0.;
 FVector2D SourcePivot=FVector2D::ZeroVector,ArtAnchorFromGround=FVector2D::ZeroVector,ScreenAnchor=FVector2D::ZeroVector;
 FSubmittedQuad Quad;
};
struct FRigSolution
{
 bool Valid=false;int32 Facing=0,Half=0,ReflectionCount=0;
 double AcceptedDistance=0.,CyclePosition=0.,U=0.,BodyRise=0.;
 FString ProfileId,ProfileSHA256,SourceSnapshotSHA256;
 TArray<FPartPose> Parts;
};
struct FResidentTexture
{
 EComponent Component=EComponent::BodyRest;
 FString TexturePath,ClassName,SourceSHA256,SourceRGBASHA256;
 int32 Width=0,Height=0;
 bool ResourceReady=false,PendingInitialization=false;
};
struct FDrawPlan
{
 bool Valid=false,WholebodyIncludesAxe=true;
 int32 RequiredResources=0,IndependentAxeLayers=0;
 FDungeonGuardMoveSample Sample;
 FRigSolution Rig;
 TArray<FResidentTexture> Residents;
 FString TrialApprovalRecord;
};
CODEXDUNGEON_API const FProfile& Profile();
// Pure committed-value geometry seam; it cannot authorize an Actor. Reject
// invalid profile/domain atomically without clamping, source replacement,
// phase clocks, mutable caches, movement reset, stretch or partial output.
CODEXDUNGEON_API bool Solve(const FSolveInput& Input,const FProfile& Source,FRigSolution& Out,FString& Diagnostic);
// Complete seven-resource resident preflight. Renderer must submit this SAME
// completed plan only after actual QueryCompletedGuardMove succeeds.
CODEXDUNGEON_API bool PlanFromSample(const FDungeonGuardMoveSample& Sample,const FProfile& Source,
 const TArray<FResidentTexture>& Residents,const FDrawContext& Context,FDrawPlan& Out,FString& Diagnostic);
}
