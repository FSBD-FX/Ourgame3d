#pragma once
#include <algorithm>
#include <cmath>
#include <cstdint>
#include <functional>
#include <limits>
#include <vector>

namespace DungeonStoneBat {
struct FPoint { double X=0,Y=0,Z=90; };
enum class EAttack { None,Peck,Wing };
enum class EPhase { Dormant,Waking,HighIdle,Windup,Active,SeekingLow,LowRecovery,Rising,Stunned,Dead };
enum class EStop { None,Wall,Body };
enum class EEventKind { WakeStarted,WakeCompleted,AttackStarted,AimLocked,ActiveWindow,MissedDescent,Movement,LowStarted,LowCompleted,RiseStarted,AttackCompleted,PoiseBroken,Damaged,Hit,Died,RewardClaimed,DescentDue };
struct FDefinition { const char* ContentId="ENM-STN-002"; double HP=55,Armor=15,Ward=10,Poise=25,MoveSpeed=220,BodyHalfX=16,BodyHalfY=12,HurtHalfX=16,HurtHalfY=12; };
struct FAction {
 std::uint64_t AttackId=0,StartEventId=0,LockEventId=0,WindowEventId=0,FinishEventId=0;
 EAttack Kind=EAttack::None; bool InProgress=false,Locked=false,Emitted=false,Interrupted=false,Missed=false,PathBlocked=false,EndpointFound=false;
 double Start=0,LockAt=0,ActiveAt=0,ActiveEnd=0,NominalEnd=0,CooldownDeadline=0,InterruptedAt=-1,CompletedAt=-1;
 double Damage=0,Stagger=0,RadiusX=80,RadiusY=0,HorizontalBudget=0,HorizontalSpeed=0;
 FPoint Origin,LockedTarget,Endpoint;
};
struct FEvent { std::uint64_t EventId=0,EntityId=0,TargetId=0; EEventKind Kind=EEventKind::Movement; double AtTime=0,EndTime=0,Amount=0; FPoint From,To; FAction Action; };
struct FResult { bool Accepted=false; std::vector<FEvent> Events; };
struct FLowPointRequest { FPoint From,Candidate,LockedTarget; EAttack Attack=EAttack::None; double AtTime=0; };
struct FNearestLowResult { bool Accepted=true,Found=false; FPoint Point{0,0,20}; };
struct FSweepRequest { FPoint From,To; double FromTime=0,ToTime=0,BodyThresholdZ=40; EAttack Attack=EAttack::None; bool Damaging=false; };
struct FSweepResult { bool Accepted=true; double Fraction=1; EStop Stop=EStop::None; };
struct FWorldInput {
 bool HasTarget=false,TargetAlive=true,LOS=true,CanBeginWake=true,CanStartAttack=true;
 FPoint Target;
 // These are observations, not permission to teleport or edit the kernel.
 std::function<bool(const FLowPointRequest&)> LegalLowPoint;
 std::function<FNearestLowResult(FPoint)> NearestLegalLowPoint;
 std::function<FSweepResult(const FSweepRequest&)> Sweep;
 // No invented AI weighting: caller chooses among the two legal options at the high-idle deadline.
 std::function<EAttack(bool,bool)> SelectDueAttack;
};
struct FIncomingHit { std::uint64_t ReceiptId=0; double AtTime=0,HPLoss=0,Stagger=0; };
struct FHitReceipt { std::uint64_t AttackId=0,TargetId=0; double AtTime=0; };
struct FState {
 std::uint32_t Version=1; std::uint64_t EntityId=1,NextAttackId=1,NextEventId=1,LastDamageReceiptId=0;
 double InitialTime=0,Time=0,HP=55,PoiseAccum=0,PoiseDecayOrigin=0,LastPoiseAt=-1,ProtectionUntil=0,StunUntil=0;
 double CombatStartedAt=-1,WakeStartedAt=-1,WakeEnd=-1,PeckReadyAt=0,WingReadyAt=0;
 double LowStartedAt=-1,LowReadyAt=-1,RiseStartedAt=-1,HighIdleEligibleSince=-1;
 bool WakeQueued=false,Awakened=false,PendingLow=false,RewardClaimed=false,LowLegal=false;
 EPhase Phase=EPhase::Dormant,ResumePhase=EPhase::Dormant;
 FPoint InitialPosition,Position,RiseOrigin;
 FAction Action;
 std::vector<FAction> Actions;
 std::vector<FIncomingHit> ReceivedHits;
 std::vector<FHitReceipt> HitReceipts;
 std::vector<FEvent> Issued;
};
class FBatKernel {
 FState S;
 static bool Finite(double N) { return std::isfinite(N); }
 static bool PointValid(FPoint P) { return Finite(P.X)&&Finite(P.Y)&&Finite(P.Z)&&P.Z>=0; }
 static bool SamePoint(FPoint A,FPoint B) { return A.X==B.X&&A.Y==B.Y&&A.Z==B.Z; }
 static double XYDistance(FPoint A,FPoint B) { return std::hypot(A.X-B.X,A.Y-B.Y); }
 static FPoint Lerp(FPoint A,FPoint B,double T) { return {A.X+(B.X-A.X)*T,A.Y+(B.Y-A.Y)*T,A.Z+(B.Z-A.Z)*T}; }
 static bool WorldValid(const FWorldInput& W) { return PointValid(W.Target); }
 static bool AttackKind(EAttack A) { return A==EAttack::Peck||A==EAttack::Wing; }
 static FAction DefinitionAction(EAttack Kind,double Start,std::uint64_t Id) {
  const bool Peck=Kind==EAttack::Peck;FAction A;A.Kind=Kind;A.AttackId=Id;A.InProgress=true;
  A.Start=Start;A.LockAt=Start+.4;A.ActiveAt=Start+.8;A.ActiveEnd=A.ActiveAt+(Peck?.25:.2);
  A.NominalEnd=A.ActiveEnd+2.1;A.CooldownDeadline=Start+(Peck?3.7:3.6);
  A.Damage=Peck?12:10;A.Stagger=Peck?10:12;A.RadiusY=Peck?30:35;
  A.HorizontalBudget=Peck?260:140;A.HorizontalSpeed=Peck?1040:350;return A;
 }
 static bool ActionValid(const FAction& A) {
  if(!A.AttackId||!AttackKind(A.Kind)||!PointValid(A.Origin)||!PointValid(A.LockedTarget)||!PointValid(A.Endpoint))return false;
  for(double N:{A.Start,A.LockAt,A.ActiveAt,A.ActiveEnd,A.NominalEnd,A.CooldownDeadline,A.InterruptedAt,A.CompletedAt,A.Damage,A.Stagger,A.RadiusX,A.RadiusY,A.HorizontalBudget,A.HorizontalSpeed})if(!Finite(N))return false;
  const auto D=DefinitionAction(A.Kind,A.Start,A.AttackId);
  if(A.Start<0||A.LockAt!=D.LockAt||A.ActiveAt!=D.ActiveAt||A.ActiveEnd!=D.ActiveEnd||A.NominalEnd!=D.NominalEnd
   ||A.CooldownDeadline!=D.CooldownDeadline||A.Damage!=D.Damage||A.Stagger!=D.Stagger||A.RadiusX!=80||A.RadiusY!=D.RadiusY
   ||A.HorizontalBudget!=D.HorizontalBudget||A.HorizontalSpeed!=D.HorizontalSpeed||A.Origin.Z!=90)return false;
  if(A.Locked!=(A.LockEventId!=0)||A.Emitted!=(A.WindowEventId!=0)||!A.StartEventId||(A.Emitted&&!A.Locked)
   ||(A.Interrupted!=(A.InterruptedAt>=0))||(A.InProgress!=(A.CompletedAt<0))||(A.FinishEventId!=0)!=(A.CompletedAt>=0))return false;
  if(A.EndpointFound) {
   if(!A.Locked||A.Endpoint.Z!=20||XYDistance(A.Origin,A.Endpoint)>A.HorizontalBudget)return false;
   bool Candidate=false;for(const auto P:{FPoint{70,0,20},FPoint{-70,0,20},FPoint{60,18,20},FPoint{60,-18,20},FPoint{-60,18,20},FPoint{-60,-18,20},FPoint{50,0,20},FPoint{-50,0,20}})
    Candidate|=A.Endpoint.X==A.LockedTarget.X+P.X&&A.Endpoint.Y==A.LockedTarget.Y+P.Y;
   if(!Candidate)return false;
  }
  return true;
 }
 static bool SameAction(const FAction& A,const FAction& B) {
  return A.AttackId==B.AttackId&&A.StartEventId==B.StartEventId&&A.LockEventId==B.LockEventId&&A.WindowEventId==B.WindowEventId&&A.FinishEventId==B.FinishEventId
   &&A.Kind==B.Kind&&A.InProgress==B.InProgress&&A.Locked==B.Locked&&A.Emitted==B.Emitted&&A.Interrupted==B.Interrupted&&A.Missed==B.Missed
   &&A.PathBlocked==B.PathBlocked&&A.EndpointFound==B.EndpointFound&&A.Start==B.Start&&A.LockAt==B.LockAt&&A.ActiveAt==B.ActiveAt&&A.ActiveEnd==B.ActiveEnd
   &&A.NominalEnd==B.NominalEnd&&A.CooldownDeadline==B.CooldownDeadline&&A.InterruptedAt==B.InterruptedAt&&A.CompletedAt==B.CompletedAt
   &&A.Damage==B.Damage&&A.Stagger==B.Stagger&&A.RadiusX==B.RadiusX&&A.RadiusY==B.RadiusY&&A.HorizontalBudget==B.HorizontalBudget&&A.HorizontalSpeed==B.HorizontalSpeed
   &&SamePoint(A.Origin,B.Origin)&&SamePoint(A.LockedTarget,B.LockedTarget)&&SamePoint(A.Endpoint,B.Endpoint);
 }
 bool StateValid(const FState& V) const {
  if(V.Version!=1||!V.EntityId||V.EntityId!=S.EntityId||V.InitialTime!=S.InitialTime||!SamePoint(V.InitialPosition,S.InitialPosition)
   ||!PointValid(V.Position)||V.Position.Z>90||!PointValid(V.InitialPosition)||!PointValid(V.RiseOrigin)||V.RiseOrigin.Z>90||V.InitialPosition.Z!=90
   ||V.NextAttackId!=V.Actions.size()+1||V.NextEventId!=V.Issued.size()+1||V.NextEventId>std::numeric_limits<std::uint64_t>::max()-1024
   ||static_cast<unsigned>(V.Phase)>static_cast<unsigned>(EPhase::Dead)||static_cast<unsigned>(V.ResumePhase)>static_cast<unsigned>(EPhase::Dead))return false;
  for(double N:{V.InitialTime,V.Time,V.HP,V.PoiseAccum,V.PoiseDecayOrigin,V.LastPoiseAt,V.ProtectionUntil,V.StunUntil,V.CombatStartedAt,V.WakeStartedAt,V.WakeEnd,V.PeckReadyAt,V.WingReadyAt,V.LowStartedAt,V.LowReadyAt,V.RiseStartedAt,V.HighIdleEligibleSince})if(!Finite(N))return false;
  if(V.InitialTime<0||V.Time<V.InitialTime||V.HP<0||V.HP>55||V.PoiseAccum<0||V.PoiseAccum>=25||V.LastPoiseAt < -1||V.LastPoiseAt>V.Time
   ||V.ProtectionUntil<0||V.StunUntil<0||V.PeckReadyAt<0||V.WingReadyAt<0||V.CombatStartedAt < -1||V.CombatStartedAt>V.Time
   ||V.WakeStartedAt < -1||V.LowStartedAt < -1||V.RiseStartedAt < -1||V.HighIdleEligibleSince < -1||V.HighIdleEligibleSince>V.Time)return false;
  double HP=55,LastHitAt=V.InitialTime;std::uint64_t LastReceipt=0;
  for(const auto& H:V.ReceivedHits) {
   if(!H.ReceiptId||H.ReceiptId<=LastReceipt||!Finite(H.AtTime)||H.AtTime<LastHitAt||H.AtTime>V.Time||!Finite(H.HPLoss)||H.HPLoss<0||H.HPLoss>HP||!Finite(H.Stagger)||H.Stagger<0)return false;
   HP-=H.HPLoss;LastReceipt=H.ReceiptId;LastHitAt=H.AtTime;
  }
  if(HP!=V.HP||V.LastDamageReceiptId!=LastReceipt||(V.HP==0)!=(V.Phase==EPhase::Dead)||(V.RewardClaimed&&V.HP!=0))return false;
  // Rebuild control facts from actual received receipts, not writable snapshot timers.
  double ExpectedHP=55,Poise=0,Origin=0,LastPoise=-1,Protect=0,Stun=0,DeathAt=V.Time;
  for(std::size_t I=0;I<V.ReceivedHits.size();) {
   const double At=V.ReceivedHits[I].AtTime;double Stagger=0;
   if(LastPoise>=0)Poise=std::max(0.,Origin-20.*std::max(0.,At-(LastPoise+1.)));
   do {ExpectedHP-=V.ReceivedHits[I].HPLoss;Stagger+=V.ReceivedHits[I].Stagger;++I;}while(I<V.ReceivedHits.size()&&V.ReceivedHits[I].AtTime==At);
   if(ExpectedHP==0){DeathAt=At;break;}
   if(Stagger>0&&At>=Protect){Poise+=Stagger;LastPoise=At;if(Poise>=25){Poise=0;Protect=At+1.;Stun=At+.4;}Origin=Poise;}
  }
  if(LastPoise>=0)Poise=std::max(0.,Origin-20.*std::max(0.,DeathAt-(LastPoise+1.)));
  if(V.PoiseAccum!=Poise||V.PoiseDecayOrigin!=Origin||V.LastPoiseAt!=LastPoise||V.ProtectionUntil!=Protect||V.StunUntil!=Stun)return false;
  FPoint Position=V.InitialPosition;double LastEventAt=V.InitialTime;int Deaths=0,Rewards=0,WakeStarts=0,WakeEnds=0,LowStarts=0,LowEnds=0;
  std::size_t DamageCursor=0,HitCount=0;double PeckCD=0,WingCD=0;
  for(std::size_t I=0;I<V.Issued.size();++I) {
   const auto& E=V.Issued[I];if(E.EventId!=I+1||E.EntityId!=V.EntityId||!Finite(E.AtTime)||E.AtTime<LastEventAt||E.AtTime>V.Time
    ||!Finite(E.EndTime)||!Finite(E.Amount)||static_cast<unsigned>(E.Kind)>static_cast<unsigned>(EEventKind::DescentDue)||!PointValid(E.From)||!PointValid(E.To)||E.From.Z>90||E.To.Z>90)return false;
   LastEventAt=E.AtTime;if(E.Kind==EEventKind::Movement){if(!SamePoint(E.From,Position))return false;Position=E.To;}
   Deaths+=E.Kind==EEventKind::Died;Rewards+=E.Kind==EEventKind::RewardClaimed;
   if(E.Kind==EEventKind::WakeStarted){++WakeStarts;if(E.AtTime!=V.WakeStartedAt||E.EndTime!=V.WakeEnd)return false;}
   if(E.Kind==EEventKind::WakeCompleted){++WakeEnds;if(E.AtTime!=V.WakeEnd)return false;}
   if(E.Kind==EEventKind::Damaged){while(DamageCursor<V.ReceivedHits.size()&&V.ReceivedHits[DamageCursor].HPLoss==0)++DamageCursor;
    if(DamageCursor==V.ReceivedHits.size()||E.Amount!=V.ReceivedHits[DamageCursor].HPLoss||E.AtTime!=V.ReceivedHits[DamageCursor].AtTime)return false;++DamageCursor;}
   if(E.Kind==EEventKind::Hit){++HitCount;int Matches=0;for(const auto& H:V.HitReceipts)Matches+=H.AttackId==E.Action.AttackId&&H.TargetId==E.TargetId&&H.AtTime==E.AtTime;
    if(Matches!=1||E.Amount!=E.Action.Damage)return false;}
   if(E.Action.AttackId==V.Action.AttackId&&E.Kind==EEventKind::LowStarted){++LowStarts;if(E.AtTime!=V.LowStartedAt||E.EndTime!=V.LowReadyAt)return false;}
   if(E.Action.AttackId==V.Action.AttackId&&E.Kind==EEventKind::LowCompleted){++LowEnds;if(E.AtTime!=V.LowReadyAt)return false;}
  }
  while(DamageCursor<V.ReceivedHits.size()&&V.ReceivedHits[DamageCursor].HPLoss==0)++DamageCursor;
  if(DamageCursor!=V.ReceivedHits.size()||HitCount!=V.HitReceipts.size()||WakeStarts!=(V.WakeStartedAt>=0?1:0)||WakeEnds!=(V.Awakened?1:0)||LowStarts!=(V.LowStartedAt>=0?1:0)||LowEnds>1)return false;
  if(!SamePoint(Position,V.Position)||Deaths!=(V.HP==0?1:0)||Rewards!=(V.RewardClaimed?1:0))return false;
  for(std::size_t I=0;I<V.Actions.size();++I) {
   const auto& A=V.Actions[I];if(!ActionValid(A)||A.AttackId!=I+1||A.Start<V.InitialTime||A.Start>V.Time||A.StartEventId>=V.NextEventId)return false;
   const auto EventIs=[&V,&A](std::uint64_t Id,EEventKind Kind,double At){return Id>0&&Id<V.NextEventId&&V.Issued[Id-1].Kind==Kind&&V.Issued[Id-1].AtTime==At&&V.Issued[Id-1].Action.AttackId==A.AttackId;};
   if(!EventIs(A.StartEventId,EEventKind::AttackStarted,A.Start)||(A.Locked&&!EventIs(A.LockEventId,EEventKind::AimLocked,A.LockAt))
    ||(A.Emitted&&!EventIs(A.WindowEventId,EEventKind::ActiveWindow,A.ActiveAt)))return false;
   if(A.CompletedAt>=0&&(!EventIs(A.FinishEventId,EEventKind::AttackCompleted,A.CompletedAt)&&!EventIs(A.FinishEventId,EEventKind::Died,A.CompletedAt)))return false;
   if(I+1<V.Actions.size()&&A.InProgress)return false;
   if(A.Kind==EAttack::Peck)PeckCD=A.CooldownDeadline;else WingCD=A.CooldownDeadline;
  }
  if(V.PeckReadyAt!=PeckCD||V.WingReadyAt!=WingCD)return false;
  if(V.Actions.empty()){if(V.Action.AttackId||V.PendingLow)return false;}else if(!SameAction(V.Action,V.Actions.back()))return false;
  if(V.WakeStartedAt<0){if(V.WakeEnd!=-1||V.Awakened)return false;}else if(V.WakeStartedAt<V.InitialTime||V.WakeEnd!=V.WakeStartedAt+.8||(V.Awakened&&V.Time<V.WakeEnd))return false;
  if(V.Awakened&&V.WakeQueued)return false;
  if(V.PendingLow!=(V.Action.InProgress&&LowEnds==0&&V.Phase!=EPhase::Dead))return false;
  if(V.LowStartedAt>=0){if(V.LowStartedAt>V.Time||V.LowReadyAt!=V.LowStartedAt+1.8||!V.LowLegal)return false;}else if(V.LowReadyAt!=-1||V.LowLegal)return false;
  if(V.Phase==EPhase::HighIdle&&(!V.Awakened||V.PendingLow||V.Action.InProgress||V.Position.Z!=90))return false;
  if(V.Phase==EPhase::Waking&&(V.WakeStartedAt<0||V.Awakened||V.Time>=V.WakeEnd))return false;
  if(V.Phase==EPhase::Dormant&&(V.Awakened||V.WakeStartedAt>=0))return false;
  if(V.Phase==EPhase::Stunned&&V.Time>=V.StunUntil)return false;
  if(V.Phase==EPhase::Windup&&(V.Action.Interrupted||V.Time>=V.Action.ActiveAt||V.Action.Locked!=(V.Time>=V.Action.LockAt)))return false;
  if(V.Phase==EPhase::Active&&(!V.Action.Emitted||V.Action.Interrupted||V.Time<V.Action.ActiveAt||V.Time>=V.Action.ActiveEnd))return false;
  if(V.Phase==EPhase::SeekingLow&&(!V.PendingLow||(!V.Action.Missed&&!V.Action.Interrupted&&V.Time<V.Action.ActiveEnd)))return false;
  if(V.LowStartedAt>=0&&V.PendingLow&&V.Position.Z!=20)return false;
  if(V.Phase==EPhase::LowRecovery&&(!V.PendingLow||V.LowStartedAt<0||V.Position.Z!=20))return false;
  if(V.Phase==EPhase::Rising&&(V.PendingLow||V.LowStartedAt<0||V.Time<V.LowReadyAt||V.RiseStartedAt<0))return false;
  if((V.Phase==EPhase::Windup||V.Phase==EPhase::Active||V.Phase==EPhase::SeekingLow||V.Phase==EPhase::LowRecovery||V.Phase==EPhase::Rising)&&!V.Action.InProgress)return false;
  for(std::size_t I=0;I<V.HitReceipts.size();++I) {
   const auto& H=V.HitReceipts[I];if(!H.AttackId||H.AttackId>=V.NextAttackId||!H.TargetId||!Finite(H.AtTime))return false;
   const auto& A=V.Actions[H.AttackId-1];if(!A.Emitted||H.AtTime<A.ActiveAt||H.AtTime>=A.ActiveEnd||(A.Interrupted&&H.AtTime>=A.InterruptedAt))return false;
   for(std::size_t J=0;J<I;++J)if(V.HitReceipts[J].AttackId==H.AttackId&&V.HitReceipts[J].TargetId==H.TargetId)return false;
  }
  return true;
 }
 void SyncRecord() { if(S.Action.AttackId)S.Actions[S.Action.AttackId-1]=S.Action; }
 void Emit(FResult& R,EEventKind Kind,double End=0,double Amount=0,std::uint64_t Target=0,FPoint From={},FPoint To={}) {
  SyncRecord();FEvent E;E.EventId=S.NextEventId++;E.EntityId=S.EntityId;E.TargetId=Target;E.Kind=Kind;E.AtTime=S.Time;E.EndTime=End;E.Amount=Amount;E.From=From;E.To=To;E.Action=S.Action;S.Issued.push_back(E);R.Events.push_back(E);
 }
 void Advance(double At) { if(S.Phase!=EPhase::Dead&&S.LastPoiseAt>=0)S.PoiseAccum=std::max(0.,S.PoiseDecayOrigin-20.*std::max(0.,At-(S.LastPoiseAt+1.)));S.Time=At; }
 bool Visible(const FWorldInput& W) const { return W.HasTarget&&W.TargetAlive&&W.LOS&&std::abs(W.Target.X-S.Position.X)<=650&&std::abs(W.Target.Y-S.Position.Y)<=250; }
 bool NearWake(const FWorldInput& W) const { return W.HasTarget&&W.TargetAlive&&W.LOS&&std::hypot((W.Target.X-S.Position.X)/180.,(W.Target.Y-S.Position.Y)/85.)<=1.; }
 bool Legal(FPoint P,const FWorldInput& W) const { return W.LegalLowPoint&&P.Z==20&&W.LegalLowPoint({S.Position,P,S.Action.LockedTarget,S.Action.Kind,S.Time}); }
 bool Candidate(EAttack Kind,FPoint Target,const FWorldInput& W,FPoint& Out) const {
  if(!AttackKind(Kind)||!W.LegalLowPoint)return false;const auto A=DefinitionAction(Kind,S.Time,1);
  for(const auto P:{FPoint{70,0,20},FPoint{-70,0,20},FPoint{60,18,20},FPoint{60,-18,20},FPoint{-60,18,20},FPoint{-60,-18,20},FPoint{50,0,20},FPoint{-50,0,20}}) {
   const FPoint C{Target.X+P.X,Target.Y+P.Y,20};if(XYDistance(S.Position,C)>A.HorizontalBudget)continue;
   if(W.LegalLowPoint({S.Position,C,Target,Kind,S.Time})){Out=C;return true;}
  }return false;
 }
 bool Eligible(EAttack Kind,const FWorldInput& W) const { FPoint P;return W.CanStartAttack&&Visible(W)&&S.Time>=(Kind==EAttack::Peck?S.PeckReadyAt:S.WingReadyAt)&&Candidate(Kind,W.Target,W,P); }
 void BeginWake(FResult& R) { S.WakeQueued=false;S.WakeStartedAt=S.Time;S.WakeEnd=S.Time+.8;if(S.Phase!=EPhase::Stunned)S.Phase=EPhase::Waking;Emit(R,EEventKind::WakeStarted,S.WakeEnd); }
 void StartAction(EAttack Kind,const FWorldInput& W,FResult& R) {
  S.Action=DefinitionAction(Kind,S.Time,S.NextAttackId++);S.Action.Origin=S.Position;S.Action.LockedTarget=W.Target;S.Action.StartEventId=S.NextEventId;
  S.Actions.push_back(S.Action);S.Phase=EPhase::Windup;S.PendingLow=true;S.LowLegal=false;S.LowStartedAt=S.LowReadyAt=S.RiseStartedAt=-1;S.HighIdleEligibleSince=-1;
  if(Kind==EAttack::Peck)S.PeckReadyAt=S.Action.CooldownDeadline;else S.WingReadyAt=S.Action.CooldownDeadline;Emit(R,EEventKind::AttackStarted);
 }
 void BeginLow(FResult& R) { S.LowLegal=true;S.LowStartedAt=S.Time;S.LowReadyAt=S.Time+1.8;S.Phase=EPhase::LowRecovery;Emit(R,EEventKind::LowStarted,S.LowReadyAt); }
 void BeginRise(FResult& R) { S.Phase=EPhase::Rising;S.RiseStartedAt=S.Time;S.RiseOrigin=S.Position;Emit(R,EEventKind::RiseStarted,S.Time+(90-S.Position.Z)/ (70./.3)); }
 void ApplyHits(const std::vector<FIncomingHit>& Hits,std::size_t& Index,const FWorldInput&,FResult& R) {
  double Stagger=0,Loss=0;while(Index<Hits.size()&&Hits[Index].AtTime==S.Time) {
   auto H=Hits[Index++];H.HPLoss=std::min(S.HP,H.HPLoss);S.HP-=H.HPLoss;Loss+=H.HPLoss;Stagger+=H.Stagger;S.LastDamageReceiptId=H.ReceiptId;S.ReceivedHits.push_back(H);
   if(H.HPLoss>0)Emit(R,EEventKind::Damaged,0,H.HPLoss);
  }
  if(S.HP==0&&S.Phase!=EPhase::Dead) {
   S.PendingLow=false;S.WakeQueued=false;S.Phase=EPhase::Dead;
   if(S.Action.InProgress){S.Action.InProgress=false;S.Action.CompletedAt=S.Time;S.Action.FinishEventId=S.NextEventId;}
   Emit(R,EEventKind::Died);return;
  }
  if(S.Phase==EPhase::Dead)return;
  if(Loss>0&&!S.Awakened&&S.WakeStartedAt<0)S.WakeQueued=true;
  if(Stagger>0&&S.Time>=S.ProtectionUntil) {
   S.PoiseAccum+=Stagger;S.LastPoiseAt=S.Time;
   if(S.PoiseAccum>=25) {
    S.PoiseAccum=0;S.ProtectionUntil=S.Time+1.;S.StunUntil=S.Time+.4;S.ResumePhase=S.Phase;S.Phase=EPhase::Stunned;
    if(S.Action.InProgress&&!S.Action.Interrupted){S.Action.Interrupted=true;S.Action.InterruptedAt=S.Time;}
    Emit(R,EEventKind::PoiseBroken,S.StunUntil);
   }
   S.PoiseDecayOrigin=S.PoiseAccum;
  }
 }
 bool Pump(const FWorldInput& W,FResult& R,bool& Changed) {
  Changed=true;
  if(S.Phase==EPhase::Dead){Changed=false;return true;}
  if(!S.Awakened&&S.WakeStartedAt<0) {
   if(S.Phase==EPhase::Dormant&&(NearWake(W)||(S.CombatStartedAt>=0&&S.Time>=S.CombatStartedAt+12)))S.WakeQueued=true;
   if(S.WakeQueued&&W.CanBeginWake){BeginWake(R);return true;}
  }
  if(!S.Awakened&&S.WakeStartedAt>=0&&S.Time>=S.WakeEnd) {
   S.Awakened=true;S.WakeQueued=false;if(S.Phase!=EPhase::Stunned)S.Phase=EPhase::HighIdle;Emit(R,EEventKind::WakeCompleted);return true;
  }
  if(S.PendingLow&&S.LowStartedAt>=0&&S.Time>=S.LowReadyAt) {
   S.PendingLow=false;Emit(R,EEventKind::LowCompleted);if(S.Phase!=EPhase::Stunned)BeginRise(R);return true;
  }
  if(S.Phase==EPhase::Stunned) {
   if(S.Time<S.StunUntil){Changed=false;return true;}
   if(!S.Awakened)S.Phase=S.WakeStartedAt>=0?EPhase::Waking:EPhase::Dormant;
   else if(S.Action.InProgress) {
    if(S.PendingLow)S.Phase=S.LowStartedAt>=0?EPhase::LowRecovery:EPhase::SeekingLow;
    else BeginRise(R);
   }else S.Phase=EPhase::HighIdle;
   return true;
  }
  if(S.Phase==EPhase::HighIdle) {
   const bool Peck=Eligible(EAttack::Peck,W),Wing=Eligible(EAttack::Wing,W);
   if(!Peck&&!Wing){S.HighIdleEligibleSince=-1;Changed=false;return true;}
   if(S.HighIdleEligibleSince<0)S.HighIdleEligibleSince=S.Time;
   if(S.Time>=S.HighIdleEligibleSince+2.4) {
    if(!W.SelectDueAttack)return false;const auto Choice=W.SelectDueAttack(Peck,Wing);
    if((Choice!=EAttack::Peck||!Peck)&&(Choice!=EAttack::Wing||!Wing))return false;
    Emit(R,EEventKind::DescentDue);StartAction(Choice,W,R);return true;
   }Changed=false;return true;
  }
  if(S.Phase==EPhase::Windup) {
   if(!S.Action.Locked&&S.Time>=S.Action.LockAt) {
    S.Action.Locked=true;S.Action.LockEventId=S.NextEventId;if(Visible(W))S.Action.LockedTarget=W.Target;
    S.Action.EndpointFound=Candidate(S.Action.Kind,S.Action.LockedTarget,W,S.Action.Endpoint);Emit(R,EEventKind::AimLocked);
    if(!S.Action.EndpointFound){S.Action.Missed=true;S.Phase=EPhase::SeekingLow;Emit(R,EEventKind::MissedDescent);}return true;
   }
   if(S.Time>=S.Action.ActiveAt) {
    if(S.Action.Missed||(S.Action.Kind==EAttack::Wing&&(S.Position.Z!=20||!Legal(S.Position,W)))||!Legal(S.Action.Endpoint,W)) {
     S.Action.Missed=true;S.Phase=EPhase::SeekingLow;Emit(R,EEventKind::MissedDescent);return true;
    }
    S.Action.Emitted=true;S.Action.WindowEventId=S.NextEventId;S.Phase=EPhase::Active;Emit(R,EEventKind::ActiveWindow,S.Action.ActiveEnd,S.Action.Damage);return true;
   }
  }
  if(S.Phase==EPhase::Active&&S.Time>=S.Action.ActiveEnd){S.Phase=EPhase::SeekingLow;return true;}
  if(S.Phase==EPhase::SeekingLow&&S.Position.Z==20&&Legal(S.Position,W)
   &&(S.Action.Interrupted||S.Time>=S.Action.ActiveEnd)){BeginLow(R);return true;}
  if(S.Phase==EPhase::Rising&&S.Position.Z==90) {
   S.Action.InProgress=false;S.Action.CompletedAt=S.Time;S.Action.FinishEventId=S.NextEventId;S.Phase=EPhase::HighIdle;Emit(R,EEventKind::AttackCompleted);return true;
  }
  Changed=false;return true;
 }
 bool Move(FPoint To,double Next,const FWorldInput& W,FResult& R,bool Damaging,bool& Blocked) {
  if(!W.Sweep)return false;const FPoint From=S.Position;const double Start=S.Time;
  const auto Hit=W.Sweep({From,To,Start,Next,40,S.Action.Kind,Damaging});
  if(!Hit.Accepted||!Finite(Hit.Fraction)||Hit.Fraction<0||Hit.Fraction>1||static_cast<unsigned>(Hit.Stop)>static_cast<unsigned>(EStop::Body)
   ||(Hit.Stop==EStop::None&&Hit.Fraction!=1))return false;
  Blocked=Hit.Stop!=EStop::None;const double At=Hit.Fraction==1?Next:Start+(Next-Start)*Hit.Fraction;
  S.Position=Hit.Fraction==1?To:Lerp(From,To,Hit.Fraction);Advance(At);Emit(R,EEventKind::Movement,Next,0,0,From,S.Position);
  if(Blocked)Advance(Next);return true;
 }
 static double ZBoundary(FPoint From,FPoint To,double Start,double End,double Cursor,double Limit) {
  if(From.Z==To.Z)return Limit;
  for(double Z:{65.,40.,20.,90.})if((Z>std::min(From.Z,To.Z))&&(Z<std::max(From.Z,To.Z))) {
   const double At=Start+(End-Start)*(Z-From.Z)/(To.Z-From.Z);if(At>Cursor)Limit=std::min(Limit,At);
  }return Limit;
 }
 static FPoint PathPoint(FPoint From,FPoint To,double Start,double End,double At) {
  if(At==End)return To;if(At==Start)return From;auto P=Lerp(From,To,(At-Start)/(End-Start));
  // Exact analytic boundaries are represented as their declared height, not
  // a tolerance band which would grant early damage/body/low permission.
  if(From.Z!=To.Z)for(double Z:{65.,40.,20.,90.})
   if(At==Start+(End-Start)*(Z-From.Z)/(To.Z-From.Z))P.Z=Z;
  return P;
 }
 bool AdvanceInterval(double Next,const FWorldInput& W,FResult& R) {
  const bool Descent=(S.Phase==EPhase::Active&&S.Action.Kind==EAttack::Peck)
   ||(S.Phase==EPhase::Windup&&S.Action.Locked&&S.Action.Kind==EAttack::Wing);
  if(Descent&&!S.Action.PathBlocked) {
   const double Start=S.Action.Kind==EAttack::Peck?S.Action.ActiveAt:S.Action.LockAt;
   const double End=S.Action.Kind==EAttack::Peck?S.Action.ActiveEnd:S.Action.ActiveAt;
   Next=ZBoundary(S.Action.Origin,S.Action.Endpoint,Start,End,S.Time,Next);
   const auto To=PathPoint(S.Action.Origin,S.Action.Endpoint,Start,End,Next);
   bool Blocked=false;if(!Move(To,Next,W,R,S.Phase==EPhase::Active,Blocked))return false;
   if(Blocked){S.Action.PathBlocked=true;if(S.Action.Kind==EAttack::Wing)S.Action.Missed=true;}return true;
  }
  if(S.Phase==EPhase::SeekingLow) {
   if(S.Position.Z==20&&Legal(S.Position,W)&&!S.Action.Interrupted&&S.Time<S.Action.ActiveEnd){Advance(Next);return true;}
   if(!W.NearestLegalLowPoint)return false;const auto Goal=W.NearestLegalLowPoint(S.Position);
   if(!Goal.Accepted||!PointValid(Goal.Point)||Goal.Point.Z!=20)return false;
   if(!Goal.Found){Advance(Next);return true;}
   if(!Legal(Goal.Point,W)){Advance(Next);return true;}
   const double Rate=S.Action.Kind==EAttack::Peck?280.:175.;
   const double Duration=std::max(XYDistance(S.Position,Goal.Point)/220.,std::abs(S.Position.Z-20)/Rate);
   if(Duration==0){Advance(Next);return true;}
   const double End=S.Time+Duration;Next=ZBoundary(S.Position,Goal.Point,S.Time,End,S.Time,std::min(Next,End));
   const auto To=PathPoint(S.Position,Goal.Point,S.Time,End,Next);bool Blocked=false;
   return Move(To,Next,W,R,false,Blocked);
  }
  if(S.Phase==EPhase::Rising) {
   const double End=S.RiseStartedAt+(90-S.RiseOrigin.Z)/(70./.3);FPoint Goal=S.RiseOrigin;Goal.Z=90;
   Next=ZBoundary(S.RiseOrigin,Goal,S.RiseStartedAt,End,S.Time,std::min(Next,End));
   const auto To=PathPoint(S.RiseOrigin,Goal,S.RiseStartedAt,End,Next);bool Blocked=false;
   if(!Move(To,Next,W,R,false,Blocked))return false;
   if(Blocked){S.RiseOrigin=S.Position;S.RiseStartedAt=S.Time;}return true;
  }
  Advance(Next);return true;
 }
public:
 explicit FBatKernel(std::uint64_t EntityId,double StartTime=0,FPoint Position={}) { S.EntityId=EntityId;S.InitialTime=S.Time=StartTime;S.InitialPosition=S.Position=Position; }
 static constexpr FDefinition Definition() { return {}; }
 const FState& State() const { return S; }
 FState Capture() const { return S; }
 FResult StepTo(double Now,const FWorldInput& W,const std::vector<FIncomingHit>& Hits = {}) {
  if(!StateValid(S)||!Finite(Now)||Now<S.Time||!WorldValid(W))return {};
  double LastAt=S.Time;auto Receipt=S.LastDamageReceiptId;
  for(const auto& H:Hits){if(!H.ReceiptId||H.ReceiptId<=Receipt||!Finite(H.AtTime)||H.AtTime<LastAt||H.AtTime>Now||!Finite(H.HPLoss)||H.HPLoss<0||!Finite(H.Stagger)||H.Stagger<0)return {};Receipt=H.ReceiptId;LastAt=H.AtTime;}
  const auto Before=S;FResult R;std::size_t Index=0;
  for(int Guard=0;Guard<65536;++Guard) {
   if(Index<Hits.size()&&Hits[Index].AtTime==S.Time)ApplyHits(Hits,Index,W,R);
   bool Changed=false;if(!Pump(W,R,Changed)){S=Before;return {};}
   if(Changed)continue;
   if(S.Time==Now){SyncRecord();if(!StateValid(S)){S=Before;return {};}R.Accepted=true;return R;}
   double Next=Now;const auto Bound=[this,&Next](double At){if(At>S.Time)Next=std::min(Next,At);};
   if(Index<Hits.size())Bound(Hits[Index].AtTime);
   if(!S.Awakened&&S.WakeStartedAt>=0)Bound(S.WakeEnd);
   if(S.Phase==EPhase::Dormant&&S.CombatStartedAt>=0)Bound(S.CombatStartedAt+12);
   if(S.Phase==EPhase::Stunned)Bound(S.StunUntil);
   if(S.PendingLow&&S.LowStartedAt>=0)Bound(S.LowReadyAt);
   if(S.Phase==EPhase::HighIdle){Bound(S.PeckReadyAt);Bound(S.WingReadyAt);if(S.HighIdleEligibleSince>=0)Bound(S.HighIdleEligibleSince+2.4);}
   if(S.Phase==EPhase::Windup){if(!S.Action.Locked)Bound(S.Action.LockAt);Bound(S.Action.ActiveAt);}
   if(S.Phase==EPhase::Active||S.Phase==EPhase::SeekingLow)Bound(S.Action.ActiveEnd);
   if(!AdvanceInterval(Next,W,R)){S=Before;return {};}
  }
  S=Before;return {};
 }
 FResult TryStartAttack(EAttack Kind,const FWorldInput& W) {
  if(!StateValid(S)||!WorldValid(W)||S.Phase!=EPhase::HighIdle||!AttackKind(Kind)||!Eligible(Kind,W))return {};
  const auto Before=S;FResult R;StartAction(Kind,W,R);SyncRecord();if(!StateValid(S)){S=Before;return {};}R.Accepted=true;return R;
 }
 FResult TryHit(std::uint64_t Target,FPoint Point,bool Grounded,bool LOS=true,bool Invulnerable=false) {
  if(!StateValid(S)||!Target||!PointValid(Point)||!LOS||Invulnerable||S.Phase!=EPhase::Active||!S.Action.Emitted||S.Action.Interrupted||S.Action.Missed
   ||S.Time<S.Action.ActiveAt||S.Time>=S.Action.ActiveEnd||(Grounded&&S.Action.Kind==EAttack::Peck&&S.Position.Z>65)||std::abs(Point.Z-S.Position.Z)>65)return {};
  const double X=(Point.X-S.Position.X)/S.Action.RadiusX,Y=(Point.Y-S.Position.Y)/S.Action.RadiusY;if(X*X+Y*Y>1)return {};
  for(const auto& H:S.HitReceipts)if(H.AttackId==S.Action.AttackId&&H.TargetId==Target)return {};
  FResult R;S.HitReceipts.push_back({S.Action.AttackId,Target,S.Time});Emit(R,EEventKind::Hit,S.Action.ActiveEnd,S.Action.Damage,Target);R.Accepted=true;return R;
 }
 FResult ClaimDeathReward() {
  if(!StateValid(S)||S.Phase!=EPhase::Dead||S.RewardClaimed)return {};FResult R;S.RewardClaimed=true;Emit(R,EEventKind::RewardClaimed);R.Accepted=true;return R;
 }
 bool BeginCombat() { if(!StateValid(S)||S.CombatStartedAt>=0||S.Phase==EPhase::Dead)return false;S.CombatStartedAt=S.Time;return true; }
 bool NotifyOtherAcceptedEnemiesCleared() { if(!StateValid(S)||S.Awakened||S.WakeStartedAt>=0||S.Phase==EPhase::Dead||S.WakeQueued)return false;S.WakeQueued=true;return true; }
 bool GroundBodyEnabled() const { return S.Phase!=EPhase::Dead&&S.Position.Z<=40; }
 bool IncomingMeleeHeightLegal(double AttackerZ,double Tolerance=65) const { return S.Phase!=EPhase::Dead&&Finite(AttackerZ)&&AttackerZ>=0&&Finite(Tolerance)&&Tolerance>=0&&std::abs(AttackerZ-S.Position.Z)<=Tolerance; }
 bool Restore(const FState& V) { if(!StateValid(V))return false;S=V;return true; }
};
}
