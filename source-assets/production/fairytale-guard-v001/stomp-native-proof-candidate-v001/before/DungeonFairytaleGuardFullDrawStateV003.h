#pragma once
#include "CoreMinimal.h"
#include "DungeonFairytaleGuardFullPoseV003.h"
/** Full-v003 actual draw readback; legacy partial readback/profile remain separate. */
struct FDungeonFairytaleGuardFullDrawV003
{
 uint64 DrawId=0,EntityId=0;DungeonFairytaleGuardFullV003::FSelection Selection;
 bool OptIn=false,TrialAllowed=false,FinalAccepted=false,RegistrationReady=false,TextureReady=false,Drawn=false;
 bool ProceduralFallback=true,WholebodyIncludesAxe=true,RequestedRowTrialAllowed=false;
 int32 NativeSourceId=0,AssetFrame=-1;
 FString ProfileId=TEXT("GuardKnown44FullV003");
 FString RequestedClip,AssetClip,TexturePath,SourceSHA256,SourceRGBASHA256,TrialApprovalRecord,RequestedTrialApprovalRecord,RegistrationEvidenceSHA256,SourceIndexSHA256,MissingReason;
 double StandingExtent=0.,TargetBodyHeight=100.8,RowScale=0.,CanvasSize=0.;
 FVector2D SourceFloorPivot=FVector2D::ZeroVector,GroundScreen=FVector2D::ZeroVector,TopScreen=FVector2D::ZeroVector;
 DungeonFairytaleGuardFullV003::EPivotAuthority PivotAuthority=DungeonFairytaleGuardFullV003::EPivotAuthority::Unconfigured;
 TArray<FString> DrawStack;
};
