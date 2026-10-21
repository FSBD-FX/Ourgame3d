#include "../fragments/portable-cursor.inc"
#include "DungeonHeroLocomotionAudioV001.h"
#include <iostream>
namespace O=DungeonHeroLocomotionObservationV001;
namespace A=DungeonHeroLocomotionAudioV001;
int Checks=0,Failures=0;
void Check(bool Yes,const char* Name){++Checks;if(!Yes){++Failures;std::cout<<"FAIL "<<Name<<'\n';}}
int main()
{
 O::FRequestCursor C;O::FRequestScopeKey K{{1,2,3,4,7,3,1,0}};std::uint64_t Gap=0;
 Check(C.Observe(K,1,Gap)&&Gap==0,"first existing request captured");
 Check(!C.Observe(K,1,Gap),"same callback snapshot never duplicates request");
 Check(C.Observe(K,3,Gap)&&Gap==1,"sequence gap reported without inventing missing request");
 Check(!C.Observe(K,2,Gap),"older existing ring entry not recaptured");
 auto Epoch=K;++Epoch.Fields[7];Check(C.Observe(Epoch,1,Gap)&&Gap==0,"new epoch sequence1 distinct");
 auto Run=K;++Run.Fields[0];Check(C.Observe(Run,1,Gap)&&Gap==0,"new run sequence1 distinct");
 auto Room=K;++Room.Fields[5];Check(C.Observe(Room,1,Gap)&&Gap==0,"new room sequence1 distinct");
 auto Owner=K;++Owner.Fields[4];Check(C.Observe(Owner,1,Gap)&&Gap==0,"new owner sequence1 distinct");
 auto Restart=K;++Restart.Fields[6];Check(C.Observe(Restart,1,Gap)&&Gap==0,"restart sequence1 distinct");
 Check(!C.Observe(K,0,Gap),"zero sequence does not capture");
 // Real existing portable producer, no fake cue or playback call. 280cm yields
 // seven real distance thresholds; observer must capture all exactly once.
 A::FState State;A::FScope Scope{7,3,1,0};Check(State.Attach(Scope,0,0,0,0),"real producer attaches");
 State.GroundDistance(Scope,0,.1,280,true,true,true,true);auto Requests=State.Consume(.1,true);
 Check(Requests.size()==7,"actual producer distance fixture has seven requests");
 O::FRequestCursor Real;int Unique=0;for(int Repeat=0;Repeat<3;++Repeat)for(const auto& R:Requests)if(Real.Observe(K,R.Sequence,Gap))++Unique;
 Check(Unique==7,"repeated real snapshots preserve all seven once");
 State.AcceptedTakeoff(Scope,.1,true);Requests=State.Consume(.1,true);Check(Requests.size()==1&&Requests[0].Cue==A::ECue::TakeoffLight01,"actual accepted takeoff fixture");
 for(const auto& R:Requests)if(Real.Observe(K,R.Sequence,Gap))++Unique;
 State.AirMotion(Scope,.1,.2,110,0,630,true);Requests=State.Consume(.2,true);Check(Requests.size()==1&&Requests[0].Cue==A::ECue::LandFirm01,"actual natural firm land fixture");
 for(const auto& R:Requests)if(Real.Observe(K,R.Sequence,Gap))++Unique;
 Check(Unique==9,"observer captures movement takeoff and natural land");
 O::FRequestCursor Truncated;Check(Truncated.Observe(K,44,Gap)&&Gap==43,"first ring tail flags possible earlier history");
 Check(!Truncated.Observe(K,44,Gap)&&Gap==0,"gap not counted again on repeated callback");
 std::cout<<"CHECKS="<<Checks<<" FAILURES="<<Failures<<" HOST_ONLY=true UE_RUN=false\n";return Failures?1:0;
}
