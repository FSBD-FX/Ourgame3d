// Real immutable weapon kernel + projected eligibility helper; UE types are a host shim.
// No UE world/collision/audio-device behavior is simulated or claimed by these tests.
#include "DungeonActionAudioFeedback.h"
#include <iostream>
#include <limits>
namespace W=DungeonWeaponActions;
int Checks=0,Failures=0;
void Check(bool Pass,const char* Name){++Checks;if(!Pass)++Failures;std::cout<<(Pass?"PASS ":"FAIL ")<<Name<<'\n';}
int main()
{
 W::FWeaponActionsKernel Kernel(W::EWeapon::SWD001,41);W::FContext Context;Context.FocusRegen=0;
 const bool Started=Kernel.TryStart(W::EAction::Skill,0,Context);
 const auto Events=Kernel.StepTo(.20,Context);const W::FEvent* Found=nullptr;
 for(const auto& E:Events)if(E.Kind==W::EEvent::ForwardStep)Found=&E;
 Check(Started&&Found&&Found->AtTime==.20&&Found->ForwardStep==30.,"real SWD kernel emits accepted ForwardStep at active boundary");
 if(!Found)return 2;
 const auto Event=*Found;const auto Current=Kernel.State().Action;
 const auto Eligible=[&](FVector2D After,uint64 Owner=7,uint64 Expected=7,bool GroundedScope=true,double Now=.20)
 {return DungeonHeroForwardStepAudioV001::Eligible(Event,Current,Owner,Expected,GroundedScope,Now,{100,20},After);};
 Check(!Eligible({100,20}),"zero actual committed displacement stays silent");
 Check(Eligible({112,20}),"partial actual committed displacement produces one eligible fact");
 Check(Eligible({130,20}),"full actual committed displacement produces one eligible fact");
 W::FWeaponActionsKernel Left(W::EWeapon::SWD001,44);auto LeftContext=Context;LeftContext.Facing=-1;Left.TryStart(W::EAction::Skill,0,LeftContext);
 bool LeftEligible=false;for(const auto& E:Left.StepTo(.20,LeftContext))if(E.Kind==W::EEvent::ForwardStep)
  LeftEligible=E.ForwardStep==-30.&&DungeonHeroForwardStepAudioV001::Eligible(E,Left.State().Action,7,7,true,.20,{100,20},{70,20});
 Check(LeftEligible,"real left-facing signed request uses actual left committed displacement");
 Check(!Eligible({130,20},8),"wrong live owner cannot emit hero foot audio");
 Check(!Eligible({130,20},7,7,false),"inactive airborne or wrong scope stays silent");
 auto Stale=Current;++Stale.ActionId;
 Check(!DungeonHeroForwardStepAudioV001::Eligible(Event,Stale,7,7,true,.20,{100,20},{130,20}),"stale ActionId cannot reuse current action");
 auto Switched=Current;++Switched.InstanceId;
 Check(!DungeonHeroForwardStepAudioV001::Eligible(Event,Switched,7,7,true,.20,{100,20},{130,20}),"wrong current InstanceId stays silent");
 Kernel.Interrupt(W::EInterrupt::PoiseBreak);
 Check(!DungeonHeroForwardStepAudioV001::Eligible(Event,Kernel.State().Action,7,7,true,.20,{100,20},{130,20}),"real post-emission interruption blocks an old event");
 W::FWeaponActionsKernel Cancelled(W::EWeapon::SWD001,42);Cancelled.TryStart(W::EAction::Skill,0,Context);Cancelled.StepTo(.19,Context);Cancelled.Interrupt(W::EInterrupt::PoiseBreak);
 bool CancelledStep=false;for(const auto& E:Cancelled.StepTo(.21,Context))CancelledStep|=E.Kind==W::EEvent::ForwardStep;
 Check(!CancelledStep,"real pre-active cancellation emits no ForwardStep source");
 W::FWeaponActionsKernel Air(W::EWeapon::SWD001,43);Air.NotifyTakeoff();Context.Grounded=false;
 const bool Rejected=Air.TryStart(W::EAction::Skill,0,Context);bool RejectedStep=false;for(const auto& E:Air.StepTo(.20,Context))RejectedStep|=E.Kind==W::EEvent::ForwardStep;
 Check(!Rejected&&!RejectedStep,"real airborne K rejection emits no ForwardStep source");
 Check(!Eligible({std::numeric_limits<double>::quiet_NaN(),20}),"nonfinite actual committed position stays silent");
 Check(!Eligible({130,20},7,7,true,.199),"future event time stays silent");
 Check(!Eligible({130,20},7,7,true,.451),"expired event time stays silent");
 auto BadSource=Event;++BadSource.ActionId;
 Check(!DungeonHeroForwardStepAudioV001::Eligible(BadSource,Current,7,7,true,.20,{100,20},{130,20}),"event source ActionId must match frozen action");
 auto Other=Event;Other.Kind=W::EEvent::Started;
 Check(!DungeonHeroForwardStepAudioV001::Eligible(Other,Current,7,7,true,.20,{100,20},{130,20}),"Started is not a successful ForwardStep source");
 std::cout<<"CHECKS="<<Checks<<" FAILURES="<<Failures<<" HOST_SHIM_ONLY=true UE_RUN=false\n";return Failures?1:0;
}
