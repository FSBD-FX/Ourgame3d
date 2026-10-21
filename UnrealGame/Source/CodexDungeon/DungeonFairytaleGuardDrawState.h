#pragma once
#include "CoreMinimal.h"
#include "DungeonFairytaleGuardPose.h"
/** Readback of this actual DrawFighter invocation; never a gameplay state or save wire. */
struct FDungeonFairytaleGuardDraw
{
 uint64 DrawId=0,EntityId=0;
 DungeonFairytaleGuard::FSelection Selection;
 bool OptIn=false,TrialAllowed=false,FinalAccepted=false,RegistrationReady=false,TextureReady=false,Drawn=false;
 bool ProceduralFallback=true,WholebodyIncludesAxe=true;
 int32 NativeSourceId=0,AssetFrame=-1;
 FString AssetClip,TexturePath,SourceSHA256,TrialApprovalRecord,RegistrationEvidenceSHA256,MissingReason;
 double StandingExtent=0.,TargetBodyHeight=100.8,RowScale=0.,CanvasSize=0.;
 FVector2D SourceFloorPivot=FVector2D::ZeroVector,GroundScreen=FVector2D::ZeroVector,TopScreen=FVector2D::ZeroVector;
 TArray<FString> DrawStack;
};
