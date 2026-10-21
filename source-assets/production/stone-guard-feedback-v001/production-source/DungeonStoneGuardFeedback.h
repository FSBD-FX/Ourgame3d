#pragma once
#include "DungeonStoneGuard.h"
#include <algorithm>
#include <cmath>
#include <cstdint>
#include <deque>
#include <limits>
#include <utility>
namespace DungeonGuardFeedback
{
enum class ECue { None, Wake, Step, AxeWindup, AxeRelease, StompWindup, StompImpact, HitStone, HitFleshLeather, HitMetal, Stun, Death };
enum class EFx { None, WakeCracks, FootDust, WindupGrit, AxeDustCut, StompBurst, StoneChips, HitSparks, StunChips, DeathChunks, CancelAttack, HitPuff };
enum class EMaterial { FleshLeather, Metal, Stone };
inline const char* CueName(ECue C)
{
 switch(C){case ECue::Wake:return "GUARD_WAKE_01";case ECue::Step:return "GUARD_STEP_01";
 case ECue::AxeWindup:return "GUARD_AXE_WINDUP_01";case ECue::AxeRelease:return "GUARD_AXE_RELEASE_01";
 case ECue::StompWindup:return "GUARD_STOMP_WINDUP_01";case ECue::StompImpact:return "GUARD_STOMP_IMPACT_01";
 case ECue::HitStone:return "GUARD_HIT_STONE_01";case ECue::HitFleshLeather:return "GUARD_HIT_FLESH_LEATHER_01";
 case ECue::HitMetal:return "GUARD_HIT_METAL_01";case ECue::Stun:return "GUARD_STUN_01";case ECue::Death:return "GUARD_DEATH_01";default:return "";}
}
struct FRecord
{
 std::uint64_t Sequence=0,EventId=0,EntityId=0,AttackId=0,TargetId=0,FootOrdinal=0;
 DungeonStoneGuard::EEventKind SourceKind=DungeonStoneGuard::EEventKind::Movement;
 double AtTime=0,ActualHPLoss=0;
 DungeonStoneGuard::FPoint Position;
 int Facing=1;
 ECue Cue=ECue::None;EFx Effect=EFx::None;
};
// Presentation only: no combat/owner writes, no clock advance and no saved schema.
class FJournal
{
 using GEvent=DungeonStoneGuard::FEvent;using GPoint=DungeonStoneGuard::FPoint;using GKind=DungeonStoneGuard::EEventKind;
 std::uint64_t Entity=0,Last=0,Serial=0,Foot=0;
 double Distance=0;
 GPoint Position;int Facing=1;
 std::deque<FRecord> Records;
 std::deque<GEvent> PendingHits;
 static constexpr std::size_t Capacity=128;
 static constexpr double Stride=64.; // Proposed feedback stride, not a combat stat.
 static bool Point(GPoint P){return std::isfinite(P.X)&&std::isfinite(P.Y)&&std::isfinite(P.Z);}
 static bool Same(GPoint A,GPoint B){return A.X==B.X&&A.Y==B.Y&&A.Z==B.Z;}
 static bool Valid(const GEvent& E,std::uint64_t Id)
 {return E.EventId&&E.EntityId==Id&&static_cast<unsigned>(E.Kind)<=static_cast<unsigned>(GKind::RewardClaimed)
   &&std::isfinite(E.AtTime)&&E.AtTime>=0&&std::isfinite(E.EndTime)&&std::isfinite(E.Amount)&&Point(E.From)&&Point(E.To)
   &&(E.Action.Facing==1||E.Action.Facing==-1);}
 bool Add(const GEvent& E,ECue C,EFx Fx,GPoint P,double Loss=0,std::uint64_t Ordinal=0)
 {
  if(Serial==std::numeric_limits<std::uint64_t>::max()||!Point(P))return false;
  FRecord R;R.Sequence=++Serial;R.EventId=E.EventId;R.EntityId=Entity;R.AttackId=E.Action.AttackId;R.TargetId=E.TargetId;
  R.SourceKind=E.Kind;R.AtTime=E.AtTime;R.ActualHPLoss=Loss;R.Position=P;R.Facing=E.Kind==GKind::Movement?Facing:E.Action.AttackId?E.Action.Facing:Facing;
  R.Cue=C;R.Effect=Fx;R.FootOrdinal=Ordinal;Records.push_back(R);if(Records.size()>Capacity)Records.pop_front();return true;
 }
 bool Movement(const GEvent& E,bool Emit)
 {
  if(!Same(E.From,Position))return false;
  const double Length=std::hypot(E.To.X-E.From.X,E.To.Y-E.From.Y),Total=Distance+Length;
  if(!std::isfinite(Total)||Total>1.e12)return false;
  if(E.To.X!=E.From.X)Facing=E.To.X>E.From.X?1:-1;
  const auto Next=static_cast<std::uint64_t>(std::floor(Total/Stride));
  if(Emit&&Length>0)for(auto I=Foot+1;I<=Next;++I)
  {
   const double T=std::clamp((double(I)*Stride-Distance)/Length,0.,1.);
   GPoint P{E.From.X+(E.To.X-E.From.X)*T,E.From.Y+(E.To.Y-E.From.Y)*T,E.From.Z+(E.To.Z-E.From.Z)*T};
   // Kernel Movement.AtTime is the completed receipt boundary, not interval start.
   if(!Add(E,ECue::Step,EFx::FootDust,P,0,I))return false;
  }
  Distance=Total;Foot=Next;Position=E.To;return true;
 }
 bool Apply(const GEvent& E)
 {
  if(E.Kind==GKind::Movement)return Movement(E,true);
  if(E.Action.AttackId)Facing=E.Action.Facing;
  switch(E.Kind)
  {
  case GKind::WakeStarted:return Add(E,ECue::Wake,EFx::WakeCracks,Position);
  case GKind::AttackStarted:
   return Add(E,E.Action.Kind==DungeonStoneGuard::EAttack::AxeSweep?ECue::AxeWindup:ECue::StompWindup,EFx::WindupGrit,Position);
  case GKind::ActiveWindow:
   return Add(E,E.Action.Kind==DungeonStoneGuard::EAttack::AxeSweep?ECue::AxeRelease:ECue::StompImpact,
    E.Action.Kind==DungeonStoneGuard::EAttack::AxeSweep?EFx::AxeDustCut:EFx::StompBurst,E.Action.LockedCenter);
  case GKind::Damaged:return E.Amount>0?Add(E,ECue::HitStone,EFx::StoneChips,Position,E.Amount):true;
  case GKind::PoiseBroken:return Add(E,ECue::Stun,EFx::StunChips,Position);
  case GKind::AttackInterrupted:return Add(E,ECue::None,EFx::CancelAttack,Position);
  case GKind::Died:return Add(E,ECue::Death,EFx::DeathChunks,Position);
  case GKind::Hit:PendingHits.push_back(E);if(PendingHits.size()>64)PendingHits.pop_front();return true;
  default:return true;
  }
 }
public:
 bool Begin(const DungeonStoneGuard::FState& Saved)
 {
  if(!Saved.EntityId||!Saved.NextEventId||!Point(Saved.InitialPosition)||!Point(Saved.Position))return false;
  FJournal C;C.Entity=Saved.EntityId;C.Position=Saved.InitialPosition;C.Facing=Saved.Facing;
  for(const auto& E:Saved.Issued)
  {
   if(!Valid(E,C.Entity)||E.EventId!=C.Last+1)return false;C.Last=E.EventId;
   if(E.Kind==GKind::Movement&&!C.Movement(E,false))return false;
  }
  if(C.Last!=Saved.NextEventId-1||!Same(C.Position,Saved.Position))return false;
  C.Facing=Saved.Facing;*this=std::move(C);return true; // No historical outputs or pending Hit authorizations.
 }
 bool Observe(const std::vector<GEvent>& Events,GPoint CurrentPosition)
 {
  if(!Entity||!Point(CurrentPosition))return false;FJournal C=*this;
  for(const auto& E:Events)
  {
   if(!Valid(E,C.Entity))return false;if(E.EventId<=C.Last)continue;
   if(E.EventId!=C.Last+1||!C.Apply(E))return false;C.Last=E.EventId;
  }
  if(!Same(C.Position,CurrentPosition))return false;*this=std::move(C);return true;
 }
 bool ConfirmHit(std::uint64_t EventId,std::uint64_t TargetId,double AtTime,GPoint TargetPosition,EMaterial Material,double ActualLoss)
 {
  if(!EventId||!TargetId||!std::isfinite(AtTime)||!Point(TargetPosition)||!std::isfinite(ActualLoss)||ActualLoss<=0
    ||static_cast<unsigned>(Material)>static_cast<unsigned>(EMaterial::Stone))return false;
  const auto It=std::find_if(PendingHits.begin(),PendingHits.end(),[&](const auto& E){return E.EventId==EventId&&E.TargetId==TargetId&&E.AtTime==AtTime;});
  if(It==PendingHits.end())return false;
  const ECue Cue=Material==EMaterial::Stone?ECue::HitStone:Material==EMaterial::Metal?ECue::HitMetal:ECue::HitFleshLeather;
  if(!Add(*It,Cue,Material==EMaterial::Metal?EFx::HitSparks:Material==EMaterial::Stone?EFx::StoneChips:EFx::HitPuff,TargetPosition,ActualLoss))return false;
  PendingHits.erase(It);return true;
 }
 std::uint64_t LastEventId() const { return Last; }
 std::uint64_t LastSequence() const { return Serial; }
 const std::deque<FRecord>& Entries() const { return Records; }
};
}
