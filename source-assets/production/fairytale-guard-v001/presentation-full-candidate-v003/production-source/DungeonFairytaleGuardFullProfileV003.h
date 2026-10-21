#pragma once
#include "CoreMinimal.h"
#include "DungeonFairytaleGuardFullPoseV003.h"
namespace DungeonFairytaleGuardFullV003
{
struct FFrame
{FString TexturePath,SourceSHA256,SourceRGBASHA256;FVector2D FloorPivot=FVector2D::ZeroVector;EPivotAuthority PivotAuthority=EPivotAuthority::Unconfigured;};
struct FRow
{
 EClip Clip=EClip::Invalid,AliasTarget=EClip::Invalid;int32 AliasFrame=0;
 int32 NativeSourceId=0,PendingNativeCandidateId=0,StandingBasisFrame=-1,StandingCrownY=0,StandingSoleY=0;
 int32 CanvasWidth=512,CanvasHeight=512;double StandingExtent=0.,TargetBodyHeight=100.8;
 bool SourcePoseApproved=false,TrialAllowed=false,FinalAccepted=false,IndependentPoseOnly=true;
 FString TrialApprovalRecord,RegistrationEvidenceSHA256,SourceIndexSHA256,GapReason;
 TArray<FFrame> Frames;
 bool IsAlias() const{return AliasTarget!=EClip::Invalid;}
 double Scale() const{return StandingExtent>0.?TargetBodyHeight/StandingExtent:0.;}
};
inline const TArray<FRow>& ProfileFull();
inline const FRow* FindRowFull(EClip C)
{for(const auto& R:ProfileFull())if(R.Clip==C)return &R;return nullptr;}
inline FString TrialGateFull(const FRow& R)
{
 if(R.NativeSourceId==211||R.NativeSourceId==221||R.NativeSourceId==223)return TEXT("Rejected native source row211/221/223: grip exchange or missing opposite-foot phases");
 if(!R.SourcePoseApproved||R.NativeSourceId<=0)return R.GapReason.IsEmpty()?TEXT("Accepted full-state source row missing"):R.GapReason;
 if(!R.TrialAllowed||R.TrialApprovalRecord.IsEmpty())return TEXT("Explicit Root full-v003 row trial record required");
 if(R.IsAlias())
  return R.Clip==EClip::Dormant&&R.AliasTarget==EClip::Wake&&R.AliasFrame==0&&R.Frames.IsEmpty()?FString():TEXT("Only explicit Dormant to Wake0 alias is legal");
 if(!R.IndependentPoseOnly)return TEXT("Wholebody independent poses required; raw strip atlas is not admitted");
 if(R.CanvasWidth!=512||R.CanvasHeight!=512)return TEXT("Unsupported canvas dimensions; square HUD quad requires an explicit extension");
 if(!FMath::IsFinite(R.StandingExtent)||R.StandingExtent<=0.||R.StandingSoleY-R.StandingCrownY+1!=R.StandingExtent||R.TargetBodyHeight!=100.8
  ||R.StandingBasisFrame<0||R.StandingBasisFrame>=RequiredFrames(R.Clip)||R.RegistrationEvidenceSHA256.Len()!=64||R.SourceIndexSHA256.Len()!=64)return TEXT("Standing body-only row basis / source registration pins incomplete");
 if(R.Frames.Num()!=RequiredFrames(R.Clip))return TEXT("Full native phase row is incomplete");
 for(const auto& F:R.Frames)
  if(F.TexturePath.IsEmpty()||F.SourceSHA256.Len()!=64||F.SourceRGBASHA256.Len()!=64||F.PivotAuthority==EPivotAuthority::Unconfigured
   ||!FMath::IsFinite(F.FloorPivot.X)||!FMath::IsFinite(F.FloorPivot.Y)||F.FloorPivot.X<0.||F.FloorPivot.X>R.CanvasWidth||F.FloorPivot.Y<0.||F.FloorPivot.Y>R.CanvasHeight)return TEXT("Exact frame source / measured or artist-reference floor metadata missing");
 return FString();
}
struct FBodyPlan
{
 bool Valid=false;EClip RequestedClip=EClip::Invalid,AssetClip=EClip::Invalid;int32 Frame=-1;
 const FRow* RequestedRow=nullptr;const FRow* Row=nullptr;FString MissingReason;
 TArray<FString> WholebodyLayers;FVector2D SourcePivot=FVector2D::ZeroVector;double DisplayPivotX=0.;
 EPivotAuthority PivotAuthority=EPivotAuthority::Unconfigured;
};
inline FBodyPlan PlanFull(const FSelection& S)
{
 FBodyPlan P;P.RequestedClip=P.AssetClip=S.Clip;P.Frame=S.Frame;
 if(!S.Valid){P.MissingReason=TEXT("Native full-state selection invalid");return P;}
 P.RequestedRow=FindRowFull(S.Clip);if(!P.RequestedRow){P.MissingReason=TEXT("Full-state row not declared");return P;}
 P.Row=P.RequestedRow;FString AliasGate;
 if(P.Row->IsAlias())
 {AliasGate=TrialGateFull(*P.Row);P.AssetClip=P.Row->AliasTarget;P.Frame=P.Row->AliasFrame;P.Row=FindRowFull(P.AssetClip);if(!P.Row||P.Row->IsAlias()){P.MissingReason=TEXT("Alias target missing or recursive");return P;}}
 if(!P.Row->Frames.IsValidIndex(P.Frame)){P.MissingReason=TrialGateFull(*P.Row);if(P.MissingReason.IsEmpty())P.MissingReason=TEXT("Requested full native frame absent");return P;}
 const auto& F=P.Row->Frames[P.Frame];P.SourcePivot=F.FloorPivot;P.PivotAuthority=F.PivotAuthority;
 P.DisplayPivotX=S.Facing<0?P.Row->CanvasWidth-F.FloorPivot.X:F.FloorPivot.X;P.WholebodyLayers.Add(F.TexturePath);
 P.MissingReason=AliasGate.IsEmpty()?TrialGateFull(*P.Row):AliasGate;P.Valid=P.MissingReason.IsEmpty();return P;
}
inline int AvailableUniqueBindingsFull(){int N=0;for(const auto& R:ProfileFull())N+=R.Frames.Num();return N;}
}
#include "DungeonFairytaleGuardFullDataV003.inl"
