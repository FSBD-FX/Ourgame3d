#pragma once
#include "DungeonStoneGuard.h"
#include <algorithm>
#include <cmath>
namespace DungeonFairytaleGuard
{
enum class EClip { Dormant, Wake, Ready, Move, AxeWindup, AxeFollow, StompWindup, StompFollow, Stunned, Death, InterruptedRecovery, Count, Invalid };
struct FSelection
{
 bool Valid=false,MaterialHit=false,TerminalPresentation=false;
 EClip Clip=EClip::Invalid;
 int Frame=-1,Facing=1;
 std::uint64_t EntityId=0,AttackId=0,SourceEventId=0,MaterialEventId=0;
 DungeonStoneGuard::EPhase Phase=DungeonStoneGuard::EPhase::Dormant;
 double SampleTime=0,IntervalStart=0,IntervalEnd=0,AcceptedDistance=0,DistancePhase=0;
};
inline const char* ClipName(EClip C)
{switch(C){case EClip::Dormant:return "Dormant";case EClip::Wake:return "Wake";case EClip::Ready:return "Ready";case EClip::Move:return "Move";
case EClip::AxeWindup:return "AxeWindup";case EClip::AxeFollow:return "AxeFollow";case EClip::StompWindup:return "StompWindup";case EClip::StompFollow:return "StompFollow";
case EClip::Stunned:return "Stunned";case EClip::Death:return "Death";case EClip::InterruptedRecovery:return "InterruptedRecovery";default:return "Invalid";}}
inline FSelection Select(const DungeonStoneGuard::FState& S,double TerminalDeathAge=-1.)
{
 using namespace DungeonStoneGuard;FSelection R;R.EntityId=S.EntityId;R.AttackId=S.Action.AttackId;R.Phase=S.Phase;R.SampleTime=S.Time;R.Facing=S.Facing;
 if(!S.EntityId||!std::isfinite(S.Time)||S.Time<S.InitialTime||(S.Facing!=1&&S.Facing!=-1))return R;
 const FEvent* Died=nullptr;const FEvent* Broken=nullptr;const FEvent* LastMove=nullptr;const FEvent* Wake=nullptr;
 for(const auto& E:S.Issued)
 {
  if(E.EntityId!=S.EntityId||!std::isfinite(E.AtTime)||E.AtTime>S.Time)return R;
  if(E.Kind==EEventKind::Movement)
  {
   const double Length=std::hypot(E.To.X-E.From.X,E.To.Y-E.From.Y);if(!std::isfinite(Length))return R;
   R.AcceptedDistance+=Length;if(Length>0)LastMove=&E;
  }
  else if(E.Kind==EEventKind::Died){if(Died)return R;Died=&E;}
  else if(E.Kind==EEventKind::PoiseBroken)Broken=&E;
  else if(E.Kind==EEventKind::WakeStarted)Wake=&E;
  else if(E.Kind==EEventKind::Damaged&&E.Amount>0&&S.Time-E.AtTime>=0&&S.Time-E.AtTime<.22)
  {R.MaterialHit=true;R.MaterialEventId=E.EventId;}
 }
 if(!std::isfinite(R.AcceptedDistance))return R;
 R.DistancePhase=std::fmod(R.AcceptedDistance,128.)/128.;
 const auto Finish=[&](EClip C,int F,double Start,double End,std::uint64_t Event=0)
 {R.Valid=true;R.Clip=C;R.Frame=F;R.IntervalStart=Start;R.IntervalEnd=End;R.SourceEventId=Event;return R;};
 const auto Timed=[&](double Start,const double* Offsets,int Count)
 {int I=0;for(int J=1;J<Count;++J)if(S.Time>=Start+Offsets[J])I=J;return I;};
 if(S.Phase==EPhase::Dead)
 {
  if(!Died)return R;double Age=S.Time-Died->AtTime;
  if(std::isfinite(TerminalDeathAge)&&TerminalDeathAge>=0){Age=std::max(Age,TerminalDeathAge);R.TerminalPresentation=true;}
  // Lethal positive Damaged and Died share AtTime; terminal display age must expire the same finite tint.
  if(Age>=.22){R.MaterialHit=false;R.MaterialEventId=0;}
  const double Starts[]={0,.1,.2,.35,.55,.75};int F=0;for(int I=1;I<6;++I)if(Age>=Starts[I])F=I;
  return Finish(EClip::Death,F,Died->AtTime,Died->AtTime+1.,Died->EventId); // Last frame holds; no gameplay delay.
 }
 if(S.Phase==EPhase::Stunned)
 {
  if(!Broken||Broken->EndTime!=S.StunUntil||S.Time>=S.StunUntil)return R;
  const double Starts[]={0,.1,.2,.3};return Finish(EClip::Stunned,Timed(Broken->AtTime,Starts,4),Broken->AtTime,S.StunUntil,Broken->EventId);
 }
 if(S.Phase==EPhase::Dormant)return Finish(EClip::Dormant,0,S.InitialTime,S.InitialTime); // Explicit Wake0 resource alias.
 if(S.Phase==EPhase::Waking)
 {
  if(!Wake||S.WakeStartedAt<0||S.Time<S.WakeStartedAt||S.Time>=S.WakeEnd)return R;
  const double Starts[]={0,.167,.333,.5,.667,.833};return Finish(EClip::Wake,Timed(S.WakeStartedAt,Starts,6),S.WakeStartedAt,S.WakeEnd,Wake->EventId);
 }
 const auto& A=S.Action;
 if(S.Phase==EPhase::Windup)
 {
  if(!A.InProgress||A.Interrupted||S.Time<A.Start||S.Time>=A.ActiveAt)return R;R.Facing=A.Facing;
  const double Axe[]={0,.167,.333,.5,.667,.833},Stomp[]={0,.15,.3,.45,.6,.75};
  if(A.Kind==EAttack::AxeSweep)return Finish(EClip::AxeWindup,Timed(A.Start,Axe,6),A.Start,A.ActiveAt);
  if(A.Kind==EAttack::Stomp)return Finish(EClip::StompWindup,Timed(A.Start,Stomp,6),A.Start,A.ActiveAt);return R;
 }
 if(S.Phase==EPhase::Recovery&&A.Interrupted)
 {
  if(A.CompletedAt>=0||S.Time<S.StunUntil||S.Time>=S.OccupiedUntil||S.OccupiedUntil<=S.StunUntil)return R;R.Facing=A.Facing;
  const double U=(S.Time-S.StunUntil)/(S.OccupiedUntil-S.StunUntil);
  return Finish(EClip::InterruptedRecovery,std::min(3,int(std::floor(U*4.))),S.StunUntil,S.OccupiedUntil);
 }
 if(S.Phase==EPhase::Active||S.Phase==EPhase::Recovery)
 {
  if(A.Interrupted||!A.WindowIssued||S.Time<A.ActiveAt||S.Time>=A.RecoveryEnd)return R;R.Facing=A.Facing;
  EClip C=A.Kind==EAttack::AxeSweep?EClip::AxeFollow:A.Kind==EAttack::Stomp?EClip::StompFollow:EClip::Invalid;if(C==EClip::Invalid)return R;
  if(S.Phase==EPhase::Active)return Finish(C,S.Time>=A.ActiveAt+(A.ActiveEnd-A.ActiveAt)*.5?1:0,A.ActiveAt,A.RecoveryEnd);
  const double Axe[]={0,.3,.65,1.},Stomp[]={0,.35,.7,1.1};
  return Finish(C,2+Timed(A.ActiveEnd,A.Kind==EAttack::AxeSweep?Axe:Stomp,4),A.ActiveAt,A.RecoveryEnd);
 }
 if(S.Phase==EPhase::Idle)
 {
  // A positive accepted Movement at this completed native boundary is required.
  // Actor bMoving or held input alone cannot credit a blocked/idle interval.
  if(LastMove&&LastMove->AtTime==S.Time)return Finish(EClip::Move,std::min(5,int(std::floor(R.DistancePhase*6.))),LastMove->AtTime,LastMove->AtTime,LastMove->EventId);
  const double Since=std::max(0.,S.Time-(S.WakeEnd>=0?S.WakeEnd:S.InitialTime));
  return Finish(EClip::Ready,int(std::floor(std::fmod(Since,1.)/.25)),S.WakeEnd>=0?S.WakeEnd:S.InitialTime,S.Time);
 }
 return R;
}
}
