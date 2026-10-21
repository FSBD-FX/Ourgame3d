#include "DungeonStoneGuard.h"
#include <iostream>
#include <iomanip>
#include <cmath>
#include <stdexcept>
using namespace DungeonStoneGuard;
void need(bool p,const char* why){if(!p)throw std::runtime_error(why);}
const char* phase(EPhase p){switch(p){case EPhase::Dormant:return "Dormant";case EPhase::Waking:return "Waking";case EPhase::Idle:return "Idle";case EPhase::Windup:return "Windup";case EPhase::Active:return "Active";case EPhase::Recovery:return "Recovery";case EPhase::Stunned:return "Stunned";case EPhase::Dead:return "Dead";}return "bad";}
int count(const FResult&r,EEventKind k){int n=0;for(auto&e:r.Events)n+=e.Kind==k;return n;}
void witness(int id,EAttack kind,double relativeBreak,bool expectedInterval){
 FGuardKernel k(id);need(k.IsValid(),"kernel init");FWorldInput w;w.HasTarget=true;w.Target={kind==EAttack::Stomp?50.:150.,0,0};w.Sweep=[](const FSweepRequest&){return FSweepResult{};};
 need(k.StepTo(0,w).Accepted,"wake start");need(k.StepTo(k.State().WakeEnd,w).Accepted,"wake end");need(k.State().Phase==EPhase::Idle,"awake idle");need(k.TryStartAttack(kind,w).Accepted,"real attack start");auto original=k.State().Action;
 double breakAt=original.Start+relativeBreak;need(k.StepTo(breakAt,w,{{1,breakAt,1,85}}).Accepted,"real85poise receipt");need(k.State().Phase==EPhase::Stunned&&k.State().Action.Interrupted,"actual interrupted stun");double stunEnd=k.State().StunUntil,occupied=k.State().OccupiedUntil;
 auto r=k.StepTo(stunEnd,w);need(r.Accepted,"resume clock");bool interval=k.State().Phase==EPhase::Recovery&&stunEnd<occupied;need(interval==expectedInterval,"interval expectation");need(count(r,EEventKind::ActiveWindow)==0,"no delayed active at resume");double recoveryStart=-1;for(auto&e:r.Events)if(e.Kind==EEventKind::RecoveryStarted)recoveryStart=e.AtTime;
 need(!interval||recoveryStart==stunEnd,"recovery exactly stun end");need(k.State().OccupiedUntil==original.RecoveryEnd,"no deadline rewrite");
 auto resumedPhase=k.State().Phase;int laterActive=0;bool midRecovery=false;double completeAt=-1;
 if(interval){auto m=k.StepTo((stunEnd+occupied)/2,w);need(m.Accepted&&k.State().Phase==EPhase::Recovery,"actual mid interval consumed");midRecovery=true;laterActive+=count(m,EEventKind::ActiveWindow);auto e=k.StepTo(occupied,w);need(e.Accepted&&k.State().Phase==EPhase::Idle,"original end idle");laterActive+=count(e,EEventKind::ActiveWindow);for(auto&v:e.Events)if(v.Kind==EEventKind::AttackCompleted)completeAt=v.AtTime;need(completeAt==occupied,"completion exact original end");}
 else{need(k.State().Phase==EPhase::Idle,"late break skips recovery after stun");for(auto&e:r.Events)if(e.Kind==EEventKind::AttackCompleted)completeAt=e.AtTime;need(completeAt==occupied,"late break still original completion");}
 need(laterActive==0,"no delayed active in interrupted recovery");
 std::cout<<"{\"entity\":"<<id<<",\"kind\":\""<<(kind==EAttack::AxeSweep?"AxeSweep":"Stomp")<<"\",\"attack_start\":"<<original.Start<<",\"break_at\":"<<breakAt<<",\"stun_until\":"<<stunEnd<<",\"original_occupied_until\":"<<occupied<<",\"phase_after_stun\":\""<<phase(resumedPhase)<<"\",\"actual_interrupted_recovery_interval\":"<<(interval?"true":"false")<<",\"actual_interval_seconds\":"<<(interval?occupied-stunEnd:0)<<",\"RecoveryStarted_at\":"<<recoveryStart<<",\"consumed_midpoint_Recovery\":"<<(midRecovery?"true":"false")<<",\"AttackCompleted_at\":"<<completeAt<<",\"later_ActiveWindow_count\":"<<laterActive<<",\"passed\":true}";
}
int main(){try{std::cout<<std::setprecision(17)<<"{\"actual_same_kernel_witnesses\":[";witness(7001,EAttack::AxeSweep,.8,true);std::cout<<",";witness(7002,EAttack::Stomp,.3,true);std::cout<<",";witness(7003,EAttack::AxeSweep,2.5,false);std::cout<<"],\"all_passed\":true}\n";return 0;}catch(const std::exception&e){std::cerr<<e.what()<<"\n";return 1;}}
