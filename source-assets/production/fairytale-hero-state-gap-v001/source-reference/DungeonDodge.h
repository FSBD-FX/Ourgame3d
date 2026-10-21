#pragma once
#include <algorithm>
#include <cmath>
#include <cstdint>
#include <functional>
#include <limits>
#include <utility>
#include <vector>

namespace DungeonDodge {
inline constexpr double Duration = .40;
inline constexpr double Distance = 185.;
inline constexpr double Speed = 462.5;
inline constexpr double IFrameStart = .06;
inline constexpr double IFrameEnd = .20;
inline constexpr double Cooldown = 1.20;
struct FPoint { double X=0, Y=0; };
enum class EPhase { Idle, Dodging, Dead };
enum class EBlock { None, Wall, Body };
enum class EFinish { None, Completed, PoiseBreak, Death };
enum class EEventKind { Started, Blocked, Completed, Interrupted, Died };
// CanStart is the caller's strict exclusive-action admission. This kernel cannot
// cancel attack/skill/switch, reload/equipment, or award any input priority.
struct FContext { bool FreshPress=false, Grounded=false, CanStart=false; int Facing=1; FPoint MoveIntent; };
struct FSweepRequest { FPoint From, To; double FromTime=0, ToTime=0; double BodyHalfX=18, BodyHalfY=16; std::uint64_t ActionId=0; };
struct FSweepResult { bool Accepted=true, HitWall=false, HitBody=false; double WallFraction=1, BodyFraction=1; };
// Query only. No UObject movement, resources, damage or external side effects.
// False/invalid result rejects the entire StepTo, including time and events.
using FSweep = std::function<FSweepResult(const FSweepRequest&)>;
// Dedicated owner-scoped actor-resolved-position-v1 receipt domain. IDs must be
// persistent and strictly increasing; skipped IDs are permitted, reuse is not.
struct FPositionReceipt { std::uint64_t Id=0, AfterActionId=0; double AtTime=-1; FPoint Position; };
struct FRecord {
 std::uint64_t ActionId=0, StartEventId=0, BlockEventId=0, FinishEventId=0;
 FPoint Origin, Direction{1,0}; double Start=0, End=0, ReadyAt=0, Travelled=0, BlockedAt=-1, FinishedAt=-1;
 EBlock Block=EBlock::None; EFinish Finish=EFinish::None;
 FPositionReceipt OriginReceipt;
};
struct FInterval { std::uint64_t ActionId=0; double Start=0, EndExclusive=0; };
struct FEvent { std::uint64_t EventId=0, OwnerId=0, ActionId=0; EEventKind Kind=EEventKind::Started; double AtTime=0; FPoint Position; EBlock Block=EBlock::None; EFinish Finish=EFinish::None; };
struct FResult { bool Accepted=false; std::vector<FEvent> Events; };
struct FState {
 std::uint32_t Version=2; std::uint64_t OwnerId=1, NextActionId=1, NextEventId=1, DeathEventId=0, NextPositionReceiptId=1;
 double InitialTime=0, Time=0, ReadyAt=0, DeadAt=-1; FPoint InitialPosition, Position;
 EPhase Phase=EPhase::Idle; std::vector<FRecord> Records;
 FPositionReceipt LastPositionReceipt;
};
class FDodgeKernel {
 FState S;
 static bool Finite(double V) { return std::isfinite(V); }
 static bool ValidPoint(FPoint P) { return Finite(P.X)&&Finite(P.Y); }
 static bool SamePoint(FPoint A,FPoint B) { return A.X==B.X&&A.Y==B.Y; }
 static bool EmptyReceipt(const FPositionReceipt& R) { return !R.Id&&!R.AfterActionId&&R.AtTime==-1&&SamePoint(R.Position,{}); }
 static bool SameReceipt(const FPositionReceipt& A,const FPositionReceipt& B) { return A.Id==B.Id&&A.AfterActionId==B.AfterActionId&&A.AtTime==B.AtTime&&SamePoint(A.Position,B.Position); }
 static bool ValidReceipt(const FPositionReceipt& R,double Initial,double Now,std::uint64_t LastAction) { return R.Id&&R.Id<std::numeric_limits<std::uint64_t>::max()&&R.AfterActionId<=LastAction&&Finite(R.AtTime)&&R.AtTime>=Initial&&R.AtTime<=Now&&ValidPoint(R.Position); }
 static FPoint PositionAt(const FRecord& R,double Travel) { return {R.Origin.X+R.Direction.X*Travel,R.Origin.Y+R.Direction.Y*Travel}; }
 static double TravelAt(const FRecord& R,double T) { return T>=R.End?Distance:std::clamp((T-R.Start)*Speed,0.,Distance); }
 static bool Protected(const FRecord& R,double T) {
  const double End=R.Finish==EFinish::None?R.Start+IFrameEnd:std::min(R.Start+IFrameEnd,R.FinishedAt);
  return T>=R.Start+IFrameStart&&T<End;
 }
 static bool TimingsValid(const FRecord& R) {
  return Finite(R.Start)&&Finite(R.End)&&Finite(R.ReadyAt)&&R.End==R.Start+Duration&&R.ReadyAt==R.Start+Cooldown&&R.Start<R.Start+IFrameStart&&R.Start+IFrameStart<R.Start+IFrameEnd&&R.Start+IFrameEnd<R.End&&R.End<R.ReadyAt;
 }
 static void Emit(FState& V,FResult& Out,EEventKind Kind,double At,EBlock Block=EBlock::None,EFinish Finish=EFinish::None) {
  FEvent E;E.EventId=V.NextEventId++;E.OwnerId=V.OwnerId;E.ActionId=Kind==EEventKind::Died||V.Records.empty()?0:V.Records.back().ActionId;E.Kind=Kind;E.AtTime=At;E.Position=V.Position;E.Block=Block;E.Finish=Finish;Out.Events.push_back(E);
 }
 bool ValidState(const FState& V) const {
  const auto MaxId=std::numeric_limits<std::uint64_t>::max();
  if(V.Version!=2||!V.OwnerId||V.OwnerId!=S.OwnerId||!Finite(V.InitialTime)||V.InitialTime<0||V.InitialTime!=S.InitialTime||!ValidPoint(V.InitialPosition)||!SamePoint(V.InitialPosition,S.InitialPosition)||!Finite(V.Time)||V.Time<V.InitialTime||!ValidPoint(V.Position)||!Finite(V.ReadyAt)||V.ReadyAt<0||!Finite(V.DeadAt)||V.DeadAt < -1||static_cast<unsigned>(V.Phase)>static_cast<unsigned>(EPhase::Dead)||!V.NextActionId||!V.NextEventId||!V.NextPositionReceiptId||V.NextActionId>MaxId-4||V.NextEventId>MaxId-4)return false;
  std::uint64_t ActionId=1, EventId=1;FPoint LastPosition=V.InitialPosition;double LastReady=0,LastFinish=V.InitialTime;bool Active=false;FPositionReceipt LastFrozenReceipt;
  for(std::size_t I=0;I<V.Records.size();++I) {
   const auto& R=V.Records[I];const bool Last=I+1==V.Records.size();
   if(R.ActionId!=ActionId++||R.StartEventId!=EventId++||!ValidPoint(R.Origin)||!ValidPoint(R.Direction)||std::abs(std::hypot(R.Direction.X,R.Direction.Y)-1)>1.e-12||!TimingsValid(R)||R.Start<V.InitialTime||R.Start<LastReady||R.Start>V.Time||!Finite(R.Travelled)||R.Travelled<0||R.Travelled>Distance||!Finite(R.BlockedAt)||!Finite(R.FinishedAt)||static_cast<unsigned>(R.Block)>static_cast<unsigned>(EBlock::Body)||static_cast<unsigned>(R.Finish)>static_cast<unsigned>(EFinish::Death))return false;
   if(R.OriginReceipt.Id) {
    if(!ValidReceipt(R.OriginReceipt,V.InitialTime,R.Start,R.ActionId-1)||R.OriginReceipt.AfterActionId!=R.ActionId-1||R.OriginReceipt.Id<=LastFrozenReceipt.Id||R.OriginReceipt.AtTime<LastFinish||!SamePoint(R.Origin,R.OriginReceipt.Position))return false;
    LastFrozenReceipt=R.OriginReceipt;
   } else if(!EmptyReceipt(R.OriginReceipt)||!SamePoint(R.Origin,LastPosition))return false;
   double KnownEnd=V.Time;
   if(R.Finish==EFinish::None) {
    if(!Last||V.Phase!=EPhase::Dodging||R.FinishedAt!=-1||R.FinishEventId||V.Time>=R.End)return false;
    Active=true;
   } else {
    KnownEnd=R.FinishedAt;
    if(KnownEnd<R.Start||KnownEnd>V.Time)return false;
    if(R.Finish==EFinish::Completed) { if(KnownEnd!=R.End)return false; }
    else {
     if(KnownEnd>=R.End)return false;
     if(R.Finish==EFinish::PoiseBreak&&KnownEnd>=R.Start+IFrameStart&&KnownEnd<R.Start+IFrameEnd)return false;
     if(R.Finish==EFinish::Death&&(!Last||V.Phase!=EPhase::Dead||KnownEnd!=V.DeadAt))return false;
    }
   }
   if(R.Block==EBlock::None) {
    if(R.BlockedAt!=-1||R.BlockEventId||R.Travelled!=TravelAt(R,KnownEnd))return false;
   } else {
    if(R.BlockEventId!=EventId++||R.BlockedAt<R.Start||R.BlockedAt>KnownEnd||R.BlockedAt>R.End||std::abs(R.Travelled-TravelAt(R,R.BlockedAt))>1.e-7)return false;
   }
   if(R.Finish!=EFinish::None&&R.FinishEventId!=EventId++)return false;
   LastPosition=PositionAt(R,R.Travelled);if(!ValidPoint(LastPosition))return false;LastReady=R.ReadyAt;LastFinish=KnownEnd;
  }
  if(V.NextActionId!=ActionId||V.ReadyAt!=LastReady)return false;
  const auto& PositionReceipt=V.LastPositionReceipt;
  if(PositionReceipt.Id) {
   if(!ValidReceipt(PositionReceipt,V.InitialTime,V.Time,ActionId-1)||V.NextPositionReceiptId!=PositionReceipt.Id+1)return false;
   if(PositionReceipt.AfterActionId==ActionId-1) {
    if(Active||PositionReceipt.Id<=LastFrozenReceipt.Id||PositionReceipt.AtTime<LastFinish||(V.Phase==EPhase::Dead&&PositionReceipt.AtTime>V.DeadAt)||(!V.Records.empty()&&V.Records.back().Finish==EFinish::Death))return false;
    LastPosition=PositionReceipt.Position;
   } else if(!SameReceipt(PositionReceipt,LastFrozenReceipt))return false;
  } else if(!EmptyReceipt(PositionReceipt)||LastFrozenReceipt.Id||V.NextPositionReceiptId!=1)return false;
  if(!SamePoint(V.Position,LastPosition))return false;
  if(V.Phase==EPhase::Dead) {
   if(Active||V.DeadAt<V.InitialTime||V.DeadAt>V.Time||V.DeadAt<LastFinish||V.DeathEventId!=EventId++)return false;
  } else if(V.DeadAt!=-1||V.DeathEventId||Active!=(V.Phase==EPhase::Dodging))return false;
  return V.NextEventId==EventId;
 }
 static bool ReadSweep(const FSweep& Sweep,const FSweepRequest& Q,FSweepResult& Hit) {
  if(!Sweep)return false;
#if defined(__cpp_exceptions) || defined(_CPPUNWIND)
  try { Hit=Sweep(Q); } catch(...) { return false; }
#else
  // UE builds without C++ exceptions require a nonthrowing query implementation.
  Hit=Sweep(Q);
#endif
  return Hit.Accepted&&Finite(Hit.WallFraction)&&Finite(Hit.BodyFraction)&&Hit.WallFraction>=0&&Hit.WallFraction<=1&&Hit.BodyFraction>=0&&Hit.BodyFraction<=1&&(Hit.HitWall||Hit.WallFraction==1)&&(Hit.HitBody||Hit.BodyFraction==1);
 }
public:
 explicit FDodgeKernel(std::uint64_t OwnerId, double StartTime=0, FPoint Position={}) { S.OwnerId=OwnerId; S.InitialTime=S.Time=StartTime; S.InitialPosition=S.Position=Position; }
 const FState& State() const { return S; }
 // Trust boundary: caller has already resolved legal ordinary movement, landing
 // or knockback and collision. This confirms its position fact, never grants
 // locomotion permission, teleports a UObject, runs collision, or resets CD.
 // Save the dedicated receipt allocator with this kernel in the same batch.
 bool CommitResolvedIdlePosition(double Now,FPoint Position,std::uint64_t ReceiptId) {
  if(!ValidState(S)||!Finite(Now)||Now!=S.Time||S.Phase!=EPhase::Idle||!ValidPoint(Position)||ReceiptId<S.NextPositionReceiptId||ReceiptId==std::numeric_limits<std::uint64_t>::max())return false;
  auto Next=S;Next.Position=Position;Next.LastPositionReceipt={ReceiptId,S.NextActionId-1,Now,Position};Next.NextPositionReceiptId=ReceiptId+1;
  if(!ValidState(Next))return false;S=std::move(Next);return true;
 }
 FResult TryStart(double Now,const FContext& C) {
  if(!ValidState(S)||!Finite(Now)||Now!=S.Time||S.Phase!=EPhase::Idle||Now<S.ReadyAt||!C.FreshPress||!C.Grounded||!C.CanStart||(C.Facing!=1&&C.Facing!=-1)||!ValidPoint(C.MoveIntent))return {};
  FRecord R;R.ActionId=S.NextActionId;R.StartEventId=S.NextEventId;R.Origin=S.Position;R.Start=Now;R.End=Now+Duration;R.ReadyAt=Now+Cooldown;
  if(S.LastPositionReceipt.Id&&S.LastPositionReceipt.AfterActionId==S.NextActionId-1)R.OriginReceipt=S.LastPositionReceipt;
  const double Scale=std::max(std::abs(C.MoveIntent.X),std::abs(C.MoveIntent.Y));
  if(Scale>0) { const FPoint Small{C.MoveIntent.X/Scale,C.MoveIntent.Y/Scale};const double Norm=std::hypot(Small.X,Small.Y);R.Direction={Small.X/Norm,Small.Y/Norm}; }
  else R.Direction={static_cast<double>(C.Facing),0};
  if(!TimingsValid(R)||!ValidPoint(PositionAt(R,Distance)))return {};
  auto Next=S;FResult Out;Next.Records.push_back(R);++Next.NextActionId;Next.ReadyAt=R.ReadyAt;Next.Phase=EPhase::Dodging;Emit(Next,Out,EEventKind::Started,Now);
  if(!ValidState(Next))return {};S=std::move(Next);Out.Accepted=true;return Out;
 }
 FResult StepTo(double Now,const FSweep& Sweep={}) {
  if(!ValidState(S)||!Finite(Now)||Now<S.Time)return {};
  auto Next=S;FResult Out;
  if(Next.Phase==EPhase::Dodging) {
   auto& R=Next.Records.back();const double MoveEnd=std::min(Now,R.End);
   if(MoveEnd>Next.Time&&R.Block==EBlock::None) {
    const double TargetTravel=TravelAt(R,MoveEnd);FSweepRequest Q;Q.From=Next.Position;Q.To=PositionAt(R,TargetTravel);Q.FromTime=Next.Time;Q.ToTime=MoveEnd;Q.ActionId=R.ActionId;FSweepResult Hit;
    if(!ValidPoint(Q.To)||!ReadSweep(Sweep,Q,Hit))return {};
    if(Hit.HitWall||Hit.HitBody) {
     const bool Wall=Hit.HitWall&&(!Hit.HitBody||Hit.WallFraction<=Hit.BodyFraction);const double Fraction=Wall?Hit.WallFraction:Hit.BodyFraction;
     R.Block=Wall?EBlock::Wall:EBlock::Body;R.BlockedAt=Fraction==1?MoveEnd:Next.Time+(MoveEnd-Next.Time)*Fraction;
     R.Travelled=Fraction==1?TargetTravel:R.Travelled+(TargetTravel-R.Travelled)*Fraction;Next.Position=PositionAt(R,R.Travelled);R.BlockEventId=Next.NextEventId;Emit(Next,Out,EEventKind::Blocked,R.BlockedAt,R.Block);
    } else { R.Travelled=TargetTravel;Next.Position=Q.To; }
   }
   Next.Time=MoveEnd;
   if(MoveEnd==R.End) { R.Finish=EFinish::Completed;R.FinishedAt=R.End;R.FinishEventId=Next.NextEventId;Next.Phase=EPhase::Idle;Emit(Next,Out,EEventKind::Completed,R.End,R.Block,R.Finish); }
  }
  Next.Time=Now;if(!ValidState(Next))return {};S=std::move(Next);Out.Accepted=true;return Out;
 }
 // Call only after a real resolved poise break or death, at the current clock.
 // Protected direct contacts cannot be submitted as a poise break. This API
 // does not derive damage, grant hurt iframes, cancel freely, or refund CD.
 FResult Interrupt(double Now,EFinish Reason) {
  if(!ValidState(S)||!Finite(Now)||Now!=S.Time||S.Phase==EPhase::Dead||(Reason!=EFinish::PoiseBreak&&Reason!=EFinish::Death))return {};
  if(Reason==EFinish::PoiseBreak&&(S.Phase!=EPhase::Dodging||Protected(S.Records.back(),Now)))return {};
  auto Next=S;FResult Out;
  if(Next.Phase==EPhase::Dodging) { auto& R=Next.Records.back();R.Finish=Reason;R.FinishedAt=Now;R.FinishEventId=Next.NextEventId;Next.Phase=EPhase::Idle;Emit(Next,Out,EEventKind::Interrupted,Now,R.Block,Reason); }
  if(Reason==EFinish::Death) { Next.Phase=EPhase::Dead;Next.DeadAt=Now;Next.DeathEventId=Next.NextEventId;Emit(Next,Out,EEventKind::Died,Now,EBlock::None,Reason); }
  if(!ValidState(Next))return {};S=std::move(Next);Out.Accepted=true;return Out;
 }
 // While active, future scheduled intervals are promises subject to subsequent
 // real interruption. Refresh intervals after each interruption before contacts.
 // Historical intervals remain available for continuous caller damage queries.
 bool IsDirectInvulnerableAt(double HitTime) const { if(!Finite(HitTime))return false;for(const auto& R:S.Records)if(Protected(R,HitTime))return true;return false; }
 std::vector<FInterval> DirectInvulnerabilityIntervals() const { std::vector<FInterval> Out;for(const auto& R:S.Records){const double End=R.Finish==EFinish::None?R.Start+IFrameEnd:std::min(R.Start+IFrameEnd,R.FinishedAt);if(End>R.Start+IFrameStart)Out.push_back({R.ActionId,R.Start+IFrameStart,End});}return Out; }
 FState Capture() const { return S; }
 bool Restore(const FState& V) { if(!ValidState(V))return false;S=V;return true; }
};
}
