#pragma once
#include <algorithm>
#include <cmath>
#include <cstdint>
#include <functional>
#include <limits>
#include <vector>
namespace DungeonStoneKnight {
struct FPoint { double X=0,Y=0; };
enum class EPhase { Dormant,Waking,Idle,Windup,Active,Recovery,Stunned,Dead };
enum class EAttack { None,Charge,Shield };
enum class EStop { None,Wall,Body,ValidHit };
enum class EEventKind { WakeStarted,WakeCompleted,AttackStarted,AimLocked,ChargeStarted,ActiveWindow,Movement,Hit,ChargeStopped,RecoveryStarted,AttackCompleted,PoiseBroken,Damaged,Died };
struct FDefinition { const char* ContentId="ENM-STN-001"; double HP=110,Armor=45,Ward=20,Poise=60,MoveSpeed=185,BodyHalfX=24,BodyHalfY=20,HurtHalfX=24,HurtHalfY=20; };
struct FAction {
 std::uint64_t AttackId=0; EAttack Kind=EAttack::None; bool InProgress=false,Locked=false,ActiveIssued=false;
 double Start=0,LockAt=0,ActiveAt=0,PlannedActiveEnd=0,ActiveEnd=0,RecoveryEnd=0,Damage=0,Stagger=0;
 FPoint Origin,Target,Direction{1,0}; EStop Stop=EStop::None;
};
struct FActiveReceipt { FAction FrozenAction; double End=0; std::uint64_t EventId=0; };
struct FHitReceipt { std::uint64_t AttackId=0,TargetId=0; };
struct FEvent { std::uint64_t EventId=0,EntityId=0,TargetId=0; EEventKind Kind=EEventKind::WakeStarted; double AtTime=0,EndTime=0,Amount=0; FPoint From,To; FAction Action; };
struct FSweepRequest {
 bool Charge=false; double FromTime=0,ToTime=0; FPoint From,To; FAction Action;
 double BodyHalfX=24,BodyHalfY=20,HurtHalfX=24,HurtHalfY=20,FrontReach=65,HalfDepth=24,HeightCenter=0,HeightTolerance=65;
};
struct FSweepResult { double Fraction=1; EStop Stop=EStop::None; std::uint64_t TargetId=0; };
struct FWorldInput {
 bool HasTarget=false,TargetAlive=true,LOS=true,CanStartAttack=true,CanBeginWake=true;
 FPoint Target; double TargetZ=0;
 // Query only: return the first legal contact. The adapter commits movement from State().Position.
 std::function<FSweepResult(const FSweepRequest&)> Sweep;
};
struct FResult { bool Accepted=false; std::vector<FEvent> Events; };
struct FState {
 std::uint32_t Version=1; std::uint64_t EntityId=1,NextAttackId=1,NextEventId=1;
 double Time=0,HP=110,PoiseAccum=0,LastPoiseAt=-1,ProtectionUntil=0,StunUntil=0;
 double CombatStartedAt=-1,WakeStartedAt=-1,WakeEnd=-1,ChargeReadyAt=0,ShieldReadyAt=0;
 bool WakeQueued=false,Awakened=false,RewardClaimed=false; EPhase Phase=EPhase::Dormant;
 FPoint Position; FAction Action; std::vector<FActiveReceipt> ActiveReceipts; std::vector<FHitReceipt> HitReceipts;
};
class FKnightKernel {
 FState S;
 static bool Finite(double N){return std::isfinite(N);}
 static bool ValidPoint(FPoint P){return Finite(P.X)&&Finite(P.Y);}
 static double Distance(FPoint A,FPoint B){return std::hypot(A.X-B.X,A.Y-B.Y);}
 static FPoint Direction(FPoint A,FPoint B,EAttack Kind){const double X=B.X-A.X,Y=B.Y-A.Y,D=std::hypot(X,Y);if(Kind==EAttack::Shield)return {X<0?-1.:1.,0};return D>0?FPoint{X/D,Y/D}:FPoint{1,0};}
 static bool ValidWorld(const FWorldInput& W){return ValidPoint(W.Target)&&Finite(W.TargetZ);}
 bool CanEmit()const{return S.NextEventId>0&&S.NextEventId<std::numeric_limits<std::uint64_t>::max()-32;}
 bool Visible(const FWorldInput& W)const{return W.HasTarget&&W.TargetAlive&&W.LOS&&std::abs(W.Target.X-S.Position.X)<=650&&std::abs(W.Target.Y-S.Position.Y)<=250;}
 bool NearWake(const FWorldInput& W)const{const double X=(W.Target.X-S.Position.X)/260.,Y=(W.Target.Y-S.Position.Y)/110.;return W.HasTarget&&W.TargetAlive&&W.LOS&&X*X+Y*Y<=1;}
 void Emit(FResult& R,EEventKind Kind,double At,double End=0,double Amount=0,std::uint64_t Target=0,FPoint From={},FPoint To={}){
  FEvent E;E.EventId=S.NextEventId++;E.EntityId=S.EntityId;E.TargetId=Target;E.Kind=Kind;E.AtTime=At;E.EndTime=End;E.Amount=Amount;E.From=From;E.To=To;E.Action=S.Action;R.Events.push_back(E);
 }
 void Advance(double At){if(S.LastPoiseAt>=0){const double Decay=std::max(0.,At-std::max(S.Time,S.LastPoiseAt+1));S.PoiseAccum=std::max(0.,S.PoiseAccum-20*Decay);}S.Time=At;}
 void BeginWake(FResult& R){S.WakeQueued=false;S.WakeStartedAt=S.Time;S.WakeEnd=S.Time+.85;S.Phase=EPhase::Waking;Emit(R,EEventKind::WakeStarted,S.Time,S.WakeEnd);}
 void CompleteWake(FResult& R){S.Awakened=true;S.WakeQueued=false;S.Phase=EPhase::Idle;Emit(R,EEventKind::WakeCompleted,S.Time);}
 void CloseReceipt(double At){for(auto& W:S.ActiveReceipts)if(W.FrozenAction.AttackId==S.Action.AttackId)W.End=std::min(W.End,At);}
 void Recovery(FResult& R){S.Phase=EPhase::Recovery;Emit(R,EEventKind::RecoveryStarted,S.Time,S.Action.RecoveryEnd);}
 bool RegisterHit(std::uint64_t AttackId,std::uint64_t TargetId){if(!TargetId)return false;for(const auto& H:S.HitReceipts)if(H.AttackId==AttackId&&H.TargetId==TargetId)return false;S.HitReceipts.push_back({AttackId,TargetId});return true;}
 bool Move(double End,FPoint To,bool Charge,const FWorldInput& W,FResult& R){
  if(!W.Sweep)return false;FSweepRequest Q;Q.Charge=Charge;Q.FromTime=S.Time;Q.ToTime=End;Q.From=S.Position;Q.To=To;Q.Action=S.Action;
  const auto Hit=W.Sweep(Q);if(!Finite(Hit.Fraction)||Hit.Fraction<0||Hit.Fraction>1||static_cast<unsigned>(Hit.Stop)>static_cast<unsigned>(EStop::ValidHit)||(Hit.Stop==EStop::None&&Hit.Fraction!=1)||(Hit.Stop==EStop::ValidHit)!=(Hit.TargetId!=0)||(!Charge&&Hit.Stop==EStop::ValidHit))return false;
  const auto From=S.Position;const double Contact=S.Time+(End-S.Time)*Hit.Fraction;S.Position={From.X+(To.X-From.X)*Hit.Fraction,From.Y+(To.Y-From.Y)*Hit.Fraction};
  Advance(Charge&&Hit.Stop!=EStop::None?Contact:End);Emit(R,EEventKind::Movement,S.Time,0,0,0,From,S.Position);
  if(Charge&&Hit.Stop!=EStop::None){
   if(Hit.Stop==EStop::ValidHit&&RegisterHit(S.Action.AttackId,Hit.TargetId))Emit(R,EEventKind::Hit,S.Time,0,S.Action.Damage,Hit.TargetId);
   S.Action.Stop=Hit.Stop;S.Action.ActiveEnd=S.Time;S.Action.RecoveryEnd=S.Time+1.6;CloseReceipt(S.Time);Emit(R,EEventKind::ChargeStopped,S.Time);Recovery(R);
  }return true;
 }
 static bool ValidAction(const FAction& A){
  if(A.AttackId==0||A.Kind==EAttack::None||static_cast<unsigned>(A.Kind)>static_cast<unsigned>(EAttack::Shield)||static_cast<unsigned>(A.Stop)>static_cast<unsigned>(EStop::ValidHit)||!ValidPoint(A.Origin)||!ValidPoint(A.Target)||!ValidPoint(A.Direction))return false;
  for(double T:{A.Start,A.LockAt,A.ActiveAt,A.PlannedActiveEnd,A.ActiveEnd,A.RecoveryEnd,A.Damage,A.Stagger})if(!Finite(T))return false;
  const bool Charge=A.Kind==EAttack::Charge;const auto D=Direction(A.Origin,A.Target,A.Kind);
  if(A.Start<0||A.LockAt!=A.Start+(Charge?.45:.35)||A.ActiveAt!=A.Start+(Charge?.9:.7)||A.PlannedActiveEnd!=A.Start+(Charge?1.7:.82)||A.ActiveEnd<A.ActiveAt||A.ActiveEnd>A.PlannedActiveEnd||A.RecoveryEnd!=A.ActiveEnd+(Charge?1.6:.9)||A.Damage!=(Charge?20:13)||A.Stagger!=(Charge?24:18)||A.Direction.X!=D.X||A.Direction.Y!=D.Y||(A.ActiveIssued&&!A.Locked))return false;
  if(!Charge&&(A.Stop!=EStop::None||A.ActiveEnd!=A.PlannedActiveEnd))return false;
  if(Charge&&A.Stop==EStop::None&&A.ActiveEnd!=A.PlannedActiveEnd)return false;
  return true;
 }
 static bool SameFrozenFacts(const FAction& A,const FAction& B){return A.AttackId==B.AttackId&&A.Kind==B.Kind&&A.Start==B.Start&&A.LockAt==B.LockAt&&A.ActiveAt==B.ActiveAt&&A.PlannedActiveEnd==B.PlannedActiveEnd&&A.Damage==B.Damage&&A.Stagger==B.Stagger&&A.Origin.X==B.Origin.X&&A.Origin.Y==B.Origin.Y&&A.Target.X==B.Target.X&&A.Target.Y==B.Target.Y&&A.Direction.X==B.Direction.X&&A.Direction.Y==B.Direction.Y;}
 bool ValidState(const FState& V)const{
  if(V.Version!=1||V.EntityId==0||V.EntityId!=S.EntityId||V.NextAttackId==0||V.NextEventId<V.NextAttackId||V.NextEventId>std::numeric_limits<std::uint64_t>::max()-32||static_cast<unsigned>(V.Phase)>static_cast<unsigned>(EPhase::Dead)||!ValidPoint(V.Position))return false;
  for(double T:{V.Time,V.HP,V.PoiseAccum,V.LastPoiseAt,V.ProtectionUntil,V.StunUntil,V.CombatStartedAt,V.WakeStartedAt,V.WakeEnd,V.ChargeReadyAt,V.ShieldReadyAt})if(!Finite(T))return false;
  if(V.Time<0||V.HP<0||V.HP>110||V.PoiseAccum<0||V.PoiseAccum>=60||V.LastPoiseAt < -1||V.LastPoiseAt>V.Time||V.ProtectionUntil<0||V.StunUntil<0||V.CombatStartedAt < -1||V.CombatStartedAt>V.Time||V.WakeStartedAt < -1||V.WakeStartedAt>V.Time||V.ChargeReadyAt<0||V.ShieldReadyAt<0||V.ChargeReadyAt>V.Time+3.8||V.ShieldReadyAt>V.Time+2.2)return false;
  if((V.HP==0)!=(V.Phase==EPhase::Dead)||(V.RewardClaimed&&V.Phase!=EPhase::Dead))return false;
  if(V.WakeStartedAt<0){if(V.WakeEnd!=-1||V.Awakened)return false;}else if(V.WakeEnd!=V.WakeStartedAt+.85||(V.Awakened&&V.Time<V.WakeEnd))return false;
  const bool ActionPhase=V.Phase==EPhase::Windup||V.Phase==EPhase::Active||V.Phase==EPhase::Recovery;
  if(V.Action.InProgress!=ActionPhase||(ActionPhase&&!V.Awakened)||(V.Awakened&&(V.Phase==EPhase::Dormant||V.Phase==EPhase::Waking||V.WakeQueued))||(V.Phase==EPhase::Idle&&!V.Awakened)||(V.Phase==EPhase::Dormant&&V.WakeStartedAt>=0)||(V.Phase==EPhase::Waking&&(V.WakeStartedAt<0||V.Time>=V.WakeEnd)))return false;
  if(V.Phase==EPhase::Stunned&&(V.Time>=V.StunUntil||V.ProtectionUntil<V.StunUntil||V.StunUntil>V.Time+.4||V.ProtectionUntil>V.Time+1))return false;
  if(V.Action.AttackId){const auto& A=V.Action;if(!ValidAction(A)||A.AttackId>=V.NextAttackId||A.Start>V.Time||(A.Kind==EAttack::Charge?V.ChargeReadyAt:V.ShieldReadyAt)!=A.Start+(A.Kind==EAttack::Charge?3.8:2.2))return false;
   if(ActionPhase){if(A.Locked!=(V.Time>=A.LockAt)||A.ActiveIssued!=(V.Time>=A.ActiveAt)||V.Time>=A.RecoveryEnd)return false;const auto P=V.Time<A.ActiveAt?EPhase::Windup:V.Time<A.ActiveEnd?EPhase::Active:EPhase::Recovery;if(V.Phase!=P)return false;}
  }else if(ActionPhase||V.Action.Kind!=EAttack::None)return false;
  bool CurrentReceipt=false;for(std::size_t I=0;I<V.ActiveReceipts.size();++I){const auto& W=V.ActiveReceipts[I];const auto& A=W.FrozenAction;
   if(!ValidAction(A)||!A.InProgress||!A.Locked||!A.ActiveIssued||A.Stop!=EStop::None||A.AttackId>=V.NextAttackId||A.ActiveAt>V.Time||!Finite(W.End)||W.End<A.ActiveAt||W.End>A.PlannedActiveEnd||W.EventId==0||W.EventId>=V.NextEventId)return false;
   for(std::size_t J=0;J<I;++J)if(V.ActiveReceipts[J].FrozenAction.AttackId==A.AttackId||V.ActiveReceipts[J].EventId==W.EventId)return false;
   if(V.Action.AttackId==A.AttackId){if(!SameFrozenFacts(V.Action,A))return false;CurrentReceipt=true;}
  }
  if(V.Action.ActiveIssued!=CurrentReceipt)return false;
  for(std::size_t I=0;I<V.HitReceipts.size();++I){const auto& H=V.HitReceipts[I];if(!H.TargetId)return false;bool Found=false;for(const auto& W:V.ActiveReceipts)Found|=W.FrozenAction.AttackId==H.AttackId;if(!Found)return false;for(std::size_t J=0;J<I;++J)if(V.HitReceipts[J].AttackId==H.AttackId&&V.HitReceipts[J].TargetId==H.TargetId)return false;}
  return true;
 }
public:
 explicit FKnightKernel(std::uint64_t EntityId,double StartTime=0,FPoint Position={}){S.EntityId=EntityId;S.Time=StartTime;S.Position=Position;}
 static FDefinition Definition(){return {};}
 const FState& State()const{return S;}
 FResult StepTo(double Now,const FWorldInput& W){
  FResult R;if(!Finite(Now)||Now<S.Time||!ValidWorld(W)||!CanEmit()||S.EntityId==0)return R;const auto Before=S;
  for(;;){
   if(S.Phase==EPhase::Dead){Advance(Now);break;}
   if(S.Phase==EPhase::Dormant){
    if(NearWake(W)||(S.CombatStartedAt>=0&&S.Time>=S.CombatStartedAt+12))S.WakeQueued=true;
    if(S.WakeQueued&&W.CanBeginWake){BeginWake(R);continue;}
    if(S.Time==Now)break;const double Fallback=S.CombatStartedAt>=0?S.CombatStartedAt+12:Now;Advance(Fallback>S.Time?std::min(Now,Fallback):Now);continue;
   }
   if(S.Phase==EPhase::Waking){if(S.Time>=S.WakeEnd){CompleteWake(R);continue;}if(S.Time==Now)break;Advance(std::min(Now,S.WakeEnd));continue;}
   if(S.Phase==EPhase::Stunned){if(S.Time>=S.StunUntil){S.Phase=S.Awakened?EPhase::Idle:S.WakeStartedAt>=0?EPhase::Waking:EPhase::Dormant;continue;}if(S.Time==Now)break;Advance(std::min(Now,S.StunUntil));continue;}
   if(S.Phase==EPhase::Idle){
    if(S.Time==Now)break;if(!Visible(W)||ChooseAttack(W)!=EAttack::None){Advance(Now);break;}
    const double DX=W.Target.X-S.Position.X,DY=W.Target.Y-S.Position.Y;const bool AlignY=DY!=0;const double Gap=AlignY?std::abs(DY):std::max(0.,std::abs(DX)-42.);
    if(Gap==0){Advance(Now);break;}const double Travel=std::min(Gap,185*(Now-S.Time));const double End=S.Time+Travel/185;auto To=S.Position;if(AlignY)To.Y+=DY>0?Travel:-Travel;else To.X+=DX>0?Travel:-Travel;
    if(!Move(End,To,false,W,R)){S=Before;return {};}
     if(S.Position.X!=To.X||S.Position.Y!=To.Y||(!AlignY&&Travel==Gap)){Advance(Now);break;}continue;
   }
   if(S.Phase==EPhase::Windup){
    if(!S.Action.Locked&&S.Time>=S.Action.LockAt){S.Action.Locked=true;if(Visible(W))S.Action.Target=W.Target;S.Action.Direction=Direction(S.Action.Origin,S.Action.Target,S.Action.Kind);Emit(R,EEventKind::AimLocked,S.Time);continue;}
    if(S.Time>=S.Action.ActiveAt){S.Action.ActiveIssued=true;S.ActiveReceipts.push_back({S.Action,S.Action.PlannedActiveEnd,S.NextEventId});S.Phase=EPhase::Active;Emit(R,S.Action.Kind==EAttack::Charge?EEventKind::ChargeStarted:EEventKind::ActiveWindow,S.Time,S.Action.ActiveEnd);continue;}
    if(S.Time==Now)break;Advance(std::min(Now,S.Action.Locked?S.Action.ActiveAt:S.Action.LockAt));continue;
   }
   if(S.Phase==EPhase::Active){
    if(S.Time>=S.Action.ActiveEnd){Recovery(R);continue;}if(S.Time==Now)break;const double End=std::min(Now,S.Action.ActiveEnd);
    if(S.Action.Kind==EAttack::Charge){const double Travel=620*(End-S.Time);const FPoint To{S.Position.X+S.Action.Direction.X*Travel,S.Position.Y+S.Action.Direction.Y*Travel};if(!Move(End,To,true,W,R)){S=Before;return {};}}
    else Advance(End);continue;
   }
   if(S.Phase==EPhase::Recovery){if(S.Time>=S.Action.RecoveryEnd){S.Action.InProgress=false;S.Phase=EPhase::Idle;Emit(R,EEventKind::AttackCompleted,S.Time);continue;}if(S.Time==Now)break;Advance(std::min(Now,S.Action.RecoveryEnd));continue;}
  }R.Accepted=true;return R;
 }
 EAttack ChooseAttack(const FWorldInput& W)const{
  if(!ValidWorld(W)||S.Phase!=EPhase::Idle||!S.Awakened||!Visible(W)||!W.CanStartAttack)return EAttack::None;const double X=std::abs(W.Target.X-S.Position.X),Y=std::abs(W.Target.Y-S.Position.Y);
  if(X<=90&&Y<=32&&S.Time>=S.ShieldReadyAt)return EAttack::Shield;const double D=Distance(S.Position,W.Target);if(D>=140&&D<=500&&Y<=55&&S.Time>=S.ChargeReadyAt)return EAttack::Charge;return EAttack::None;
 }
 FResult TryStartAttack(EAttack Kind,const FWorldInput& W){
  FResult R;if(Kind==EAttack::None||ChooseAttack(W)!=Kind||!CanEmit()||S.NextAttackId==std::numeric_limits<std::uint64_t>::max())return R;const bool Charge=Kind==EAttack::Charge;
  FAction A;A.AttackId=S.NextAttackId++;A.Kind=Kind;A.InProgress=true;A.Start=S.Time;A.LockAt=S.Time+(Charge?.45:.35);A.ActiveAt=S.Time+(Charge?.9:.7);A.PlannedActiveEnd=S.Time+(Charge?1.7:.82);A.ActiveEnd=A.PlannedActiveEnd;A.RecoveryEnd=A.ActiveEnd+(Charge?1.6:.9);A.Damage=Charge?20:13;A.Stagger=Charge?24:18;A.Origin=S.Position;A.Target=W.Target;A.Direction=Direction(A.Origin,A.Target,Kind);S.Action=A;S.Phase=EPhase::Windup;if(Charge)S.ChargeReadyAt=S.Time+3.8;else S.ShieldReadyAt=S.Time+2.2;Emit(R,EEventKind::AttackStarted,S.Time);R.Accepted=true;return R;
 }
 FResult ApplyResolvedHit(double HPLoss,double Stagger,const FWorldInput& W){
  FResult R;if(!Finite(HPLoss)||HPLoss<0||!Finite(Stagger)||Stagger<0||!ValidWorld(W)||!CanEmit())return R;R.Accepted=true;if(S.Phase==EPhase::Dead)return R;
  const double Actual=std::min(S.HP,HPLoss);S.HP-=Actual;if(Actual>0)Emit(R,EEventKind::Damaged,S.Time,0,Actual);
  if(S.HP==0){CloseReceipt(S.Time);S.Action.InProgress=false;S.WakeQueued=false;S.Phase=EPhase::Dead;Emit(R,EEventKind::Died,S.Time);return R;}
  if(Actual>0&&!S.Awakened&&S.WakeStartedAt<0){S.WakeQueued=true;if(S.Phase==EPhase::Dormant&&W.CanBeginWake)BeginWake(R);}
  if(Stagger>0&&S.Time>=S.ProtectionUntil){S.PoiseAccum+=Stagger;S.LastPoiseAt=S.Time;if(S.PoiseAccum>=60){S.PoiseAccum=0;CloseReceipt(S.Time);S.Action.InProgress=false;S.StunUntil=S.Time+.4;S.ProtectionUntil=S.Time+1;S.Phase=EPhase::Stunned;Emit(R,EEventKind::PoiseBroken,S.Time,S.StunUntil);}}
  return R;
 }
 bool BeginCombat(){if(S.CombatStartedAt>=0||S.Phase==EPhase::Dead)return false;S.CombatStartedAt=S.Time;return true;}
 bool NotifyOtherAcceptedEnemiesCleared(){if(S.Awakened||S.WakeStartedAt>=0||S.Phase==EPhase::Dead||S.WakeQueued)return false;S.WakeQueued=true;return true;}
 bool TryMarkMeleeHit(std::uint64_t AttackId,std::uint64_t TargetId){for(const auto& W:S.ActiveReceipts)if(W.FrozenAction.AttackId==AttackId&&W.FrozenAction.Kind==EAttack::Shield&&W.End>W.FrozenAction.ActiveAt)return RegisterHit(AttackId,TargetId);return false;}
 bool ClaimDeathReward(){if(S.Phase!=EPhase::Dead||S.RewardClaimed)return false;S.RewardClaimed=true;return true;}
 FState Capture()const{return S;}
 bool Restore(const FState& V){if(!ValidState(V))return false;S=V;return true;}
};
}
