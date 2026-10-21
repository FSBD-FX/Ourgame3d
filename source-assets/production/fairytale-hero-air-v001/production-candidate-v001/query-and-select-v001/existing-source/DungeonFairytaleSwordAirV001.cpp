#include "DungeonFairytaleSwordAirV001.h"

namespace DungeonFairytaleSwordAirV001
{
const FProfile& Profile(){static const FProfile Pending;return Pending;}
bool Select(const FDungeonHeroAirSample& Q,FSelection& Out,FString& Diagnostic)
{
 if(!Q.Valid||!Q.RunGuid.IsValid()||!Q.OwnerId||!Q.RoomInstanceId||!FMath::IsFinite(Q.NativeTime)||Q.NativeTime<0.
  ||!FMath::IsFinite(Q.GroundPosition.X)||!FMath::IsFinite(Q.GroundPosition.Y)||(Q.Facing!=-1.f&&Q.Facing!=1.f)
  ||!FMath::IsFinite(Q.JumpHeight)||Q.JumpHeight<0.f||!FMath::IsFinite(Q.VerticalVelocity)
  ||!FMath::IsFinite(Q.LandingVisualAge)||Q.LandingVisualAge<0.f||Q.LandingVisualAge>.12f)
 {Diagnostic=TEXT("Nonattack Air requires complete finite actual-owner sample facts");return false;}
 FSelection Candidate;
 if(Q.JumpHeight>0.f||Q.VerticalVelocity>0.f)
 {
  Candidate.Frame=Q.VerticalVelocity>315.f?0:Q.VerticalVelocity>90.f?1:Q.VerticalVelocity>=-90.f?2:3;
 }
 else if(Q.JumpHeight==0.f&&Q.VerticalVelocity==0.f&&Q.LandingVisualAge<.12f)
  Candidate.Frame=Q.LandingVisualAge<.06f?4:5;
 else{Diagnostic=TEXT("Actual owner is outside nonattack Air and original landing window");return false;}
 Candidate.Valid=true;Candidate.Pose=static_cast<EPose>(Candidate.Frame+1);Out=Candidate;Diagnostic.Reset();return true;
}
bool BuildDrawPlanFromCommitted(const DungeonFairytaleSwordEquipmentBinding::FBinding&,
 const FDungeonHeroAirSample&,const FProfile&,const FDrawContext&,FDrawPlan&,FString& Diagnostic)
{Diagnostic=TEXT("Stage0: no retained six-pose source closure or atomic Air plan");return false;}
bool BuildDrawPlan(const ADungeonGameMode&,const ADungeonFighter&,const FDrawContext&,FDrawPlan&,FString& Diagnostic)
{Diagnostic=TEXT("Stage0: actual-owner nonattack Air plan is not implemented");return false;}
bool ValidateResidentSet(const FProfile&,const TArray<FResidentTexture>&,FString& Diagnostic)
{Diagnostic=TEXT("Stage0: actual complete49 resident preflight is not implemented");return false;}
}
