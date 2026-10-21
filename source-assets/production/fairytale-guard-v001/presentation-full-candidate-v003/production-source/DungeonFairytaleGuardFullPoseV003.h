#pragma once
#include "DungeonFairytaleGuardPose.h"
#include <algorithm>
#include <cmath>
namespace DungeonFairytaleGuardFullV003
{
enum class EPivotAuthority {Unconfigured,VisibleShoeSupport,ArtistStandingRootPropagation,ArtistNearSupportDeltaPropagation};
enum class EClip {Dormant,Wake,Ready,Move,AxeWindup,AxeActive,AxeRecovery,StompWindup,StompActive,StompRecovery,Stunned,Death,InterruptedRecovery,Count,Invalid};
struct FSelection
{
 bool Valid=false,MaterialHit=false,TerminalPresentation=false,DeathAfterglow=false;
 EClip Clip=EClip::Invalid;int Frame=-1,Facing=1;
 std::uint64_t EntityId=0,AttackId=0,SourceEventId=0,MaterialEventId=0;
 DungeonStoneGuard::EPhase Phase=DungeonStoneGuard::EPhase::Dormant;
 double SampleTime=0.,IntervalStart=0.,IntervalEnd=0.,AcceptedDistance=0.,DistancePhase=0.,DeathAge=-1.;
};
inline const char* ClipName(EClip C)
{switch(C){case EClip::Dormant:return "Dormant";case EClip::Wake:return "Wake";case EClip::Ready:return "Ready";case EClip::Move:return "Move";
case EClip::AxeWindup:return "AxeWindup";case EClip::AxeActive:return "AxeActive";case EClip::AxeRecovery:return "AxeRecovery";
case EClip::StompWindup:return "StompWindup";case EClip::StompActive:return "StompActive";case EClip::StompRecovery:return "StompRecovery";
case EClip::Stunned:return "Stunned";case EClip::Death:return "Death";case EClip::InterruptedRecovery:return "InterruptedRecovery";default:return "Invalid";}}
inline int RequiredFrames(EClip C)
{switch(C){case EClip::Dormant:return 1;case EClip::Ready:case EClip::AxeActive:case EClip::AxeRecovery:case EClip::StompRecovery:case EClip::Stunned:case EClip::InterruptedRecovery:return 4;
case EClip::StompActive:return 2;case EClip::Wake:case EClip::Move:case EClip::AxeWindup:case EClip::StompWindup:case EClip::Death:return 6;default:return 0;}}
inline int LogicalFrameBudget(){int N=0;for(int I=0;I<int(EClip::Count);++I)N+=RequiredFrames(EClip(I));return N;}
inline FSelection SelectFull(const DungeonStoneGuard::FState& S,double TerminalDeathAge=-1.)
{
 // Shared unchanged phases delegate to the actual legacy selector. The legacy
 // partial profile/Plan/tests are never expanded or rewritten by this version.
 const auto Base=DungeonFairytaleGuard::Select(S,TerminalDeathAge);FSelection R;
 R.Valid=Base.Valid;R.MaterialHit=Base.MaterialHit;R.TerminalPresentation=Base.TerminalPresentation;
 R.Frame=Base.Frame;R.Facing=Base.Facing;R.EntityId=Base.EntityId;R.AttackId=Base.AttackId;
 R.SourceEventId=Base.SourceEventId;R.MaterialEventId=Base.MaterialEventId;R.Phase=Base.Phase;
 R.SampleTime=Base.SampleTime;R.IntervalStart=Base.IntervalStart;R.IntervalEnd=Base.IntervalEnd;
 R.AcceptedDistance=Base.AcceptedDistance;R.DistancePhase=Base.DistancePhase;if(!Base.Valid)return R;
 using L=DungeonFairytaleGuard::EClip;using N=DungeonStoneGuard::EPhase;
 switch(Base.Clip)
 {
 case L::Dormant:R.Clip=EClip::Dormant;break;case L::Wake:R.Clip=EClip::Wake;break;case L::Ready:R.Clip=EClip::Ready;break;
 case L::Move:R.Clip=EClip::Move;break;case L::AxeWindup:R.Clip=EClip::AxeWindup;break;case L::StompWindup:R.Clip=EClip::StompWindup;break;
 case L::Stunned:R.Clip=EClip::Stunned;break;case L::InterruptedRecovery:R.Clip=EClip::InterruptedRecovery;break;
 case L::Death:
  R.Clip=EClip::Death;R.DeathAge=S.Time-Base.IntervalStart;
  if(Base.TerminalPresentation)R.DeathAge=std::max(R.DeathAge,TerminalDeathAge);
  R.DeathAfterglow=R.DeathAge>=0.&&R.DeathAge<.1;break;
 case L::AxeFollow:case L::StompFollow:
 {
  const auto& A=S.Action;const bool Axe=A.Kind==DungeonStoneGuard::EAttack::AxeSweep;
  if(A.Interrupted||!A.InProgress||!A.WindowIssued){R.Valid=false;return R;}
  if(S.Phase==N::Active)
  {
   if(S.Time<A.ActiveAt||S.Time>=A.ActiveEnd){R.Valid=false;return R;}
   R.Clip=Axe?EClip::AxeActive:EClip::StompActive;R.IntervalStart=A.ActiveAt;R.IntervalEnd=A.ActiveEnd;R.Frame=0;
   const double AxeStarts[]={0.,.05,.1,.15},StompStarts[]={0.,.075};const int Count=Axe?4:2;
   for(int I=1;I<Count;++I)if(S.Time>=A.ActiveAt+(Axe?AxeStarts[I]:StompStarts[I]))R.Frame=I;
  }
  else if(S.Phase==N::Recovery)
  {
   if(S.Time<A.ActiveEnd||S.Time>=A.RecoveryEnd){R.Valid=false;return R;}
   R.Clip=Axe?EClip::AxeRecovery:EClip::StompRecovery;R.IntervalStart=A.ActiveEnd;R.IntervalEnd=A.RecoveryEnd;R.Frame=0;
   // v005: Axe4x350ms / Stomp4x375ms; never the obsolete combined Follow index.
   const double AxeStarts[]={0.,.35,.7,1.05},StompStarts[]={0.,.375,.75,1.125};
   for(int I=1;I<4;++I)if(S.Time>=A.ActiveEnd+(Axe?AxeStarts[I]:StompStarts[I]))R.Frame=I;
  }
  else {R.Valid=false;return R;}break;
 }
 default:R.Valid=false;return R;
 }
 // Keep immutable native phase receipt IDs when a split phase has its own event.
 if(R.Clip==EClip::AxeWindup||R.Clip==EClip::StompWindup||R.Clip==EClip::AxeActive||R.Clip==EClip::StompActive||R.Clip==EClip::AxeRecovery||R.Clip==EClip::StompRecovery)
 {
  const auto Kind=S.Phase==N::Windup?DungeonStoneGuard::EEventKind::AttackStarted:S.Phase==N::Active?DungeonStoneGuard::EEventKind::ActiveWindow:DungeonStoneGuard::EEventKind::RecoveryStarted;
  R.SourceEventId=0;for(const auto& E:S.Issued)if(E.Kind==Kind&&E.Action.AttackId==S.Action.AttackId)R.SourceEventId=E.EventId;
  if(!R.SourceEventId){R.Valid=false;return R;}
 }
 if(R.Frame<0||R.Frame>=RequiredFrames(R.Clip))R.Valid=false;return R;
}
}
