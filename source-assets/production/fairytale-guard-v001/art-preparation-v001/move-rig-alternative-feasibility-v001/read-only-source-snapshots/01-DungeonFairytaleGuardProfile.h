#pragma once
#include "CoreMinimal.h"
#include "DungeonFairytaleGuardPose.h"
namespace DungeonFairytaleGuard
{
struct FFrame
{
 FString TexturePath,SourceSHA256;
 FVector2D FloorPivot=FVector2D::ZeroVector;
};
struct FRow
{
 EClip Clip=EClip::Invalid;
 int32 NativeSourceId=0,StandingBasisFrame=-1,StandingCrownY=0,StandingSoleY=0;
 int32 CanvasWidth=512,CanvasHeight=512;
 double StandingExtent=0.,TargetBodyHeight=100.8;
 bool SourcePoseApproved=false,TrialAllowed=false,FinalAccepted=false;
 FString TrialApprovalRecord,RegistrationEvidenceSHA256;
 TArray<FFrame> Frames;
 double Scale() const {return StandingExtent>0.?TargetBodyHeight/StandingExtent:0.;}
};
inline const TArray<FRow>& Profile();
inline int32 RequiredFrames(EClip C)
{switch(C){case EClip::Ready:case EClip::Stunned:case EClip::InterruptedRecovery:return 4;
case EClip::Wake:case EClip::Move:case EClip::AxeWindup:case EClip::AxeFollow:case EClip::StompWindup:case EClip::StompFollow:case EClip::Death:return 6;default:return 0;}}
inline FString TrialGate(const FRow& R)
{
 if(R.NativeSourceId==211)return TEXT("Native211 entire row rejected: grip topology");
 if(!R.SourcePoseApproved||R.NativeSourceId<=0)return TEXT("Reviewed wholebody source row missing");
 if(!R.TrialAllowed||R.TrialApprovalRecord.IsEmpty())return TEXT("Root explicit partial trial registration required");
 if(!FMath::IsFinite(R.StandingExtent)||R.StandingExtent<=0.||R.StandingSoleY-R.StandingCrownY+1!=R.StandingExtent
  ||R.TargetBodyHeight!=100.8||R.StandingBasisFrame<0||R.StandingBasisFrame>=RequiredFrames(R.Clip))return TEXT("Standing body-only row basis invalid");
 // Current HUD occlusion quad is square. Fail closed instead of silently stretching a future wide canvas.
 if(R.CanvasWidth!=512||R.CanvasHeight!=512)return TEXT("Non-square canvas needs a separate HUD quad change");
 if(R.Frames.Num()!=RequiredFrames(R.Clip)||R.RegistrationEvidenceSHA256.Len()!=64)return TEXT("Whole row frames or registration pin missing");
 for(const auto& F:R.Frames)
  if(F.TexturePath.IsEmpty()||F.SourceSHA256.Len()!=64||!FMath::IsFinite(F.FloorPivot.X)||!FMath::IsFinite(F.FloorPivot.Y)
   ||F.FloorPivot.X<0.||F.FloorPivot.X>R.CanvasWidth||F.FloorPivot.Y<0.||F.FloorPivot.Y>R.CanvasHeight)return TEXT("Frame texture/source pin/floor pivot invalid");
 return FString();
}
struct FBodyPlan
{
 bool Valid=false;EClip AssetClip=EClip::Invalid;int32 Frame=-1;FString MissingReason;
 const FRow* Row=nullptr;TArray<FString> WholebodyLayers;FVector2D SourcePivot=FVector2D::ZeroVector;double DisplayPivotX=0.;
};
inline const FRow* FindRow(EClip C)
{for(const auto& R:Profile())if(R.Clip==C)return &R;return nullptr;}
inline FBodyPlan Plan(const FSelection& S)
{
 FBodyPlan P;if(!S.Valid){P.MissingReason=TEXT("Native Guard phase/clock is not selectable");return P;}
 P.AssetClip=S.Clip==EClip::Dormant?EClip::Wake:S.Clip;P.Frame=S.Clip==EClip::Dormant?0:S.Frame;
 P.Row=FindRow(P.AssetClip);if(!P.Row){P.MissingReason=TEXT("Wholebody action row missing");return P;}
 if(!P.Row->Frames.IsValidIndex(P.Frame)){P.MissingReason=TEXT("Requested native frame absent");return P;}
 const auto& F=P.Row->Frames[P.Frame];P.SourcePivot=F.FloorPivot;
 P.DisplayPivotX=S.Facing<0?P.Row->CanvasWidth-F.FloorPivot.X:F.FloorPivot.X;
 P.WholebodyLayers.Add(F.TexturePath); // Planned source layer, not a rendered receipt.
 P.MissingReason=TrialGate(*P.Row);P.Valid=P.MissingReason.IsEmpty();return P;
}
}
#include "DungeonFairytaleGuardDataV001.inl"
