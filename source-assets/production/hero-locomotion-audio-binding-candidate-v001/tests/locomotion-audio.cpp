#include "DungeonHeroLocomotionAudioV001.h"
#include "DungeonDodge.h"
#include <cmath>
#include <iostream>
#include <limits>
#include <string>
namespace A=DungeonHeroLocomotionAudioV001;
int Failures=0,Checks=0;
void Check(bool Yes,const char* Name){++Checks;if(!Yes){++Failures;std::cout<<"FAIL "<<Name<<'\n';}}
A::FScope Scope{7,3,1,0};
A::FState New(double Height=0,double Velocity=0,std::uint64_t DodgeTail=0)
{A::FState S;Check(S.Attach(Scope,10,DodgeTail,Height,Velocity),"valid attach");return S;}
int main(){
 // Break caught: attach creates an event or infers a takeoff from restored H/V.
 {auto S=New();Check(S.Consume(10,true).empty(),"ground attach silent");auto Air=New(80,-90);Check(Air.Consume(10,true).empty(),"air attach never replays takeoff");}
 // Break caught: timer/intent/camera observation emits without physical distance.
 {auto S=New();S.GroundDistance(Scope,10,10.1,0,true,true,true,true);Check(S.Consume(10.1,true).empty(),"stationary intent silent");}
 // Break caught: threshold remainder or alternating feet is lost.
 {auto S=New();S.GroundDistance(Scope,10,10.1,39,true,true,true,true);Check(S.Consume(10.1,true).empty(),"substride silent");S.GroundDistance(Scope,10.1,10.2,1,true,true,true,true);auto E=S.Consume(10.2,true);Check(E.size()==1&&E[0].Cue==A::ECue::StepLight01&&E[0].StepOrdinal==1,"first threshold step1");S.GroundDistance(Scope,10.2,10.3,40,true,true,true,true);E=S.Consume(10.3,true);Check(E.size()==1&&E[0].Cue==A::ECue::StepLight02&&E[0].StepOrdinal==2,"second threshold step2");}
 // Break caught: modulo animation phase drops multiple real footfalls in one call.
 {auto S=New();S.GroundDistance(Scope,10,10.12,120,true,true,true,true);auto E=S.Consume(10.12,true);Check(E.size()==3,"three strides are three events");Check(E.size()==3&&std::abs(E[0].AtTime-10.04)<1.e-9&&std::abs(E[2].AtTime-10.12)<1.e-9,"distance crossing timestamps");S.GroundDistance(Scope,10,10.12,120,true,true,true,true);Check(S.Consume(10.12,true).empty(),"completed distance cannot replay");}
 // Break caught: airborne, action/dodge, no intent, or paused distance accumulates.
 for(int I=0;I<4;++I){auto S=New();S.GroundDistance(Scope,10,10.1,80,I!=0,I!=1,I!=2,I!=3);Check(S.Consume(10.1,true).empty(),"ineligible distance silent");S.GroundDistance(Scope,10.1,10.2,39,true,true,true,true);Check(S.Consume(10.2,true).empty(),"ineligible distance did not accumulate");}
 // Break caught: invalid data contaminates future real movement.
 {auto S=New();S.GroundDistance(Scope,10,10.1,std::numeric_limits<double>::quiet_NaN(),true,true,true,true);S.GroundDistance(Scope,10,10.1,40,true,true,true,true);Check(S.Consume(10.1,true).size()==1,"invalid distance rejected atomically");}
 // Break caught: repeated successful-boundary notification duplicates takeoff.
 {auto S=New();S.AcceptedTakeoff(Scope,10,true);S.AcceptedTakeoff(Scope,10,true);auto E=S.Consume(10,true);Check(E.size()==1&&E[0].Cue==A::ECue::TakeoffLight01,"one successful takeoff");}
 // Break caught: rendered Land4/Land5 or duplicate physical interval replays landing.
 {auto S=New(20,-100);S.AirMotion(Scope,10,10.1,20,0,200,true);auto E=S.Consume(10.1,true);Check(E.size()==1&&E[0].Cue==A::ECue::LandLight01,"restored air natural light landing");S.AirMotion(Scope,10,10.1,20,0,200,true);S.AirMotion(Scope,10.1,10.2,0,0,0,true);Check(S.Consume(10.2,true).empty(),"landing interval and grounded pose never replay");}
 // Break caught: selection ignores real speed or real downward travel.
 {auto S=New(100,-600);S.AirMotion(Scope,10,10.1,100,0,600,true);auto E=S.Consume(10.1,true);Check(E.size()==1&&E[0].Cue==A::ECue::LandFirm01&&E[0].FallSpeed==600,"firm landing from real speed");auto T=New(130,-50);T.AirMotion(Scope,10,10.1,130,0,50,true);E=T.Consume(10.1,true);Check(E.size()==1&&E[0].Cue==A::ECue::LandFirm01&&E[0].FallDistance==130,"firm landing from real travel");}
 // Break caught: restored epoch leaks queued takeoff or resets a duplicate attach.
 {auto S=New();S.GroundDistance(Scope,10,10.1,20,true,true,true,true);S.Attach(Scope,10.1,0,0,0);S.GroundDistance(Scope,10.1,10.2,20,true,true,true,true);Check(S.Consume(10.2,true).size()==1,"same scope attach preserves remainder");S.AcceptedTakeoff(Scope,10.2,true);auto Next=Scope;++Next.Epoch;S.Attach(Next,10.2,12,60,-30);Check(S.Consume(10.2,true).empty(),"new epoch drops historical queued takeoff");S.AirMotion(Scope,10.2,10.3,60,0,300,true);Check(S.Consume(10.3,true).empty(),"old epoch rejected");S.AirMotion(Next,10.2,10.3,60,0,300,true);Check(S.Consume(10.3,true).size()==1,"restored epoch future landing emits");}
 // Break caught: actual Dodge Started identity is ignored or old journal replays.
 {DungeonDodge::FDodgeKernel D(7,10,{0,0});DungeonDodge::FContext C;C.FreshPress=C.Grounded=C.CanStart=true;C.Facing=1;const auto R=D.TryStart(10,C);Check(R.Accepted&&R.Events.size()==1,"actual Dodge kernel accepted start");auto S=New();for(int Repeat=0;Repeat<2;++Repeat)for(const auto& E:R.Events)S.DodgeEvent(Scope,E.EventId,E.OwnerId,E.ActionId,E.AtTime,E.Kind==DungeonDodge::EEventKind::Started,true);auto E=S.Consume(10,true);Check(E.size()==1&&E[0].Cue==A::ECue::DodgeShort01&&E[0].DodgeEventId==1&&E[0].DodgeActionId==1,"real dodge started once");Check(!D.TryStart(10,C).Accepted,"second real Dodge request rejected");auto Restored=New(0,0,D.State().NextEventId-1);for(const auto& V:R.Events)Restored.DodgeEvent(Scope,V.EventId,V.OwnerId,V.ActionId,V.AtTime,true,true);Check(Restored.Consume(10,true).empty(),"restored dodge tail does not replay");}
 // Break caught: owner mismatch or non-Started events are audible.
 {auto S=New();S.DodgeEvent(Scope,1,99,1,10,true,true);S.DodgeEvent(Scope,2,7,1,10,false,true);Check(S.Consume(10,true).empty(),"wrong owner and nonstart silent");}
 // Break caught: pause/death suppression retries queued events after continue.
 {auto S=New();S.AcceptedTakeoff(Scope,10,true);Check(S.Consume(10,false).empty(),"paused consumer drops request");Check(S.Consume(10.1,true).empty(),"no delayed replay after resume");auto T=New();T.AcceptedTakeoff(Scope,10,false);T.AirMotion(Scope,10,10.1,20,0,200,false);Check(T.Consume(10.1,true).empty(),"paused producer silent");}
 // Break caught: stale audio retries at every tick or invalid attach emits.
 {auto S=New();S.AcceptedTakeoff(Scope,10,true);Check(S.Consume(10.3,true).empty(),"stale cue discarded");Check(S.Consume(10.31,true).empty(),"stale cue cursor advances");A::FState V;Check(!V.Attach({},10,0,0,0),"invalid owner rejected");}
 std::cout<<"CHECKS="<<Checks<<" FAILURES="<<Failures<<" HOST_ONLY=true UE_RUN=false\n";return Failures?1:0;
}
