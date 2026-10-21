#pragma once
#include <algorithm>
#include <cmath>
#include <cstdint>
#include <limits>
#include <vector>
namespace DungeonHeroLocomotionAudioV001 {
enum class ECue : std::uint8_t { StepLight01,StepLight02,TakeoffLight01,LandLight01,LandFirm01,DodgeShort01 };
struct FScope { std::uint64_t Owner=0,Room=0,Restart=0,Epoch=0; };
struct FEvent { std::uint64_t Sequence=0; FScope Scope; ECue Cue=ECue::StepLight01; double AtTime=0; std::uint64_t DodgeEventId=0,DodgeActionId=0,StepOrdinal=0; double FallSpeed=0,FallDistance=0; };
inline bool Same(FScope A,FScope B){return A.Owner==B.Owner&&A.Room==B.Room&&A.Restart==B.Restart&&A.Epoch==B.Epoch;}
// Transient presentation state: never installed into Schema1 save data. A new
// owner/room/restart/epoch starts silent at current H/V and real Dodge tail.
// Foot cadence intentionally restarts at zero on that attach; no saved parity
// or pre-restore travel is invented. Only post-attach physical intervals count.
class FState {
 FScope Scope;
 bool Attached=false,Airborne=false;
 double AttachedAt=0,GroundThrough=0,AirThrough=0,StepRemainder=0,FallDistance=0;
 std::uint64_t NextSequence=1,ConsumedThrough=0,DodgeThrough=0,StepOrdinal=0;
 std::vector<FEvent> Pending;
 bool InScope(FScope S) const{return Attached&&Same(S,Scope);}
 static bool Number(double X){return std::isfinite(X);}
 bool Interval(double From,double To,double Through) const
 {return Number(From)&&Number(To)&&From>=AttachedAt&&From>=Through&&To>From;}
 void Emit(FEvent E)
 {
  if(NextSequence==std::numeric_limits<std::uint64_t>::max())return;
  E.Sequence=NextSequence++;E.Scope=Scope;
  if(Pending.size()==256)Pending.erase(Pending.begin());
  Pending.push_back(E);
 }
public:
 bool Attach(FScope S,double At,std::uint64_t RealDodgeTail,double Height,double Velocity)
 {
  if(!S.Owner||!S.Room||!Number(At)||At<0||!Number(Height)||Height<0||!Number(Velocity))return false;
  if(InScope(S))return true;
  Scope=S;Attached=true;AttachedAt=GroundThrough=AirThrough=At;
  Airborne=Height>0||Velocity>0;DodgeThrough=RealDodgeTail;
  StepRemainder=FallDistance=0;NextSequence=1;ConsumedThrough=StepOrdinal=0;Pending.clear();return true;
 }
 void GroundDistance(FScope S,double From,double To,double Distance,bool Grounded,bool Eligible,bool Intent,bool Active)
 {
  if(!InScope(S)||!Interval(From,To,GroundThrough)||!Number(Distance)||Distance<0)return;
  GroundThrough=To; // Consume rejected/inactive intervals too: never replay them.
  if(!Active||!Grounded||!Eligible||!Intent||Airborne||Distance==0)return;
  // Current source gait is an 80cm cycle; two contacts per cycle =>40cm.
  // Reject discontinuous/absurd input rather than overflowing a cursor/queue.
  // Normal native simulation commits <=5ms collision-resolved segments.
  const double Total=StepRemainder+Distance;
  if(!Number(Total)||Total>40.*256.){StepRemainder=0;return;}
  const auto Count=static_cast<std::uint64_t>(std::floor(Total/40.));
  for(std::uint64_t I=0;I<Count;++I)
  {
   if(StepOrdinal==std::numeric_limits<std::uint64_t>::max())break;
   const double Along=40.-StepRemainder+40.*double(I);
   FEvent E;E.Cue=(++StepOrdinal%2)?ECue::StepLight01:ECue::StepLight02;
   E.StepOrdinal=StepOrdinal;E.AtTime=From+(To-From)*std::clamp(Along/Distance,0.,1.);Emit(E);
  }
  StepRemainder=std::fmod(Total,40.);
 }
 // Call only inside the actual accepted StartJump branch, not a pose sample.
 void AcceptedTakeoff(FScope S,double At,bool Active)
 {
  if(!InScope(S)||!Number(At)||At<AttachedAt||At<AirThrough||Airborne)return;
  Airborne=true;FallDistance=0;StepRemainder=0;
  if(Active){FEvent E;E.Cue=ECue::TakeoffLight01;E.AtTime=At;Emit(E);}
 }
 // H and speed are observations of committed physics, not a new physics clock.
 // Call once per actual interval, after canonical height placement. Land4/5
 // visual age never enters this API. A restored airborne attach arms landing.
 void AirMotion(FScope S,double From,double To,double FromHeight,double ToHeight,double FallingSpeed,bool Active)
 {
  if(!InScope(S)||!Interval(From,To,AirThrough)||!Number(FromHeight)||FromHeight<0
   ||!Number(ToHeight)||ToHeight<0||!Number(FallingSpeed)||FallingSpeed<0)return;
  AirThrough=To;
  Airborne=Airborne||FromHeight>0||ToHeight>0;
  if(Airborne)FallDistance+=std::max(0.,FromHeight-ToHeight);
  if(!Airborne||FromHeight<=0||ToHeight!=0)return;
  if(Active)
  {
   FEvent E;E.Cue=FallingSpeed>=540.||FallDistance>=110.?ECue::LandFirm01:ECue::LandLight01;
   E.AtTime=To;E.FallSpeed=FallingSpeed;E.FallDistance=FallDistance;Emit(E);
  }
  Airborne=false;FallDistance=0;StepRemainder=0;
 }
 // Inputs are the actual accepted Dodge kernel FEvent fields. No scanning of
 // restored Records, no draw callback, and no synthetic combat ActionId.
 void DodgeEvent(FScope S,std::uint64_t EventId,std::uint64_t Owner,std::uint64_t Action,double At,bool Started,bool Active)
 {
  if(!InScope(S)||Owner!=Scope.Owner||!EventId||EventId<=DodgeThrough||!Number(At)||At<AttachedAt)return;
  DodgeThrough=EventId;
  if(!Started||!Action||!Active)return;
  FEvent E;E.Cue=ECue::DodgeShort01;E.AtTime=At;E.DodgeEventId=EventId;E.DodgeActionId=Action;Emit(E);
 }
 std::vector<FEvent> Consume(double Now,bool Active)
 {
  std::vector<FEvent> Out;
  for(const auto& E:Pending)
  {
   if(E.Sequence<=ConsumedThrough)continue;
   ConsumedThrough=E.Sequence; // Advance before stale/missing asset/pause filters.
   if(Active&&Number(Now)&&Same(E.Scope,Scope)&&Now>=E.AtTime&&Now-E.AtTime<=.25)Out.push_back(E);
  }
  Pending.clear();return Out;
 }
};
}
