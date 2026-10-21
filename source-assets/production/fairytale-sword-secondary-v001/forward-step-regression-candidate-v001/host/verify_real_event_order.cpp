#include "DungeonWeaponActions.h"
#include <iostream>
#include <limits>
namespace WA=DungeonWeaponActions;
int main()
{
 int Checks=0,Failures=0;
 const auto Check=[&](bool B,const char* Label){++Checks;if(!B){++Failures;std::cout<<"FAIL "<<Label<<'\n';}};
 for(double Speed:{-20.,0.,20.})for(double Facing:{-1.,1.})
 {
  WA::FWeaponActionsKernel K(WA::EWeapon::SWD001,29);WA::FContext C;C.ActionSpeedPct=Speed;C.Facing=Facing;
  K.StepTo(5.,C);Check(K.TryStart(WA::EAction::Skill,5.,C),"actual-SWD-skill-start");
  const auto Started=K.State().Action;const double At=Started.ActiveAt;
  auto Previous=K.StepTo(std::nextafter(At,-std::numeric_limits<double>::infinity()),C);
  bool Early=false;for(const auto& E:Previous)Early|=E.Kind==WA::EEvent::ForwardStep;
  Check(!Early&&K.State().Action.Locked&&K.State().Action.NextSubhit==0&&!K.State().Action.ForwardStepIssued,"no-step-at-real-predecessor");
  const auto BeforeEventId=K.State().NextEventId;const auto Events=K.StepTo(At,C);
  Check(Events.size()==2,"only-forward-step-then-window-at-real-At");
  if(Events.size()!=2)continue;
  const auto& Step=Events[0];const auto& Window=Events[1];const auto& Current=K.State().Action;
  Check(Step.Kind==WA::EEvent::ForwardStep&&Window.Kind==WA::EEvent::ActiveWindow,"real-ordered-kinds");
  Check(Step.EventId==BeforeEventId&&Window.EventId==BeforeEventId+1&&K.State().NextEventId==BeforeEventId+2,"read-before-next-ID-backs-step-and-window");
  Check(Step.ActionId==Started.ActionId&&Step.InstanceId==29&&Step.SubhitId==0&&Step.AtTime==At,"real-step-parent-key");
  Check(Step.ForwardStep==30.*Facing&&Step.Action.ActiveAt==At,"authored-signed-request-and-actual-ActiveAt");
  Check(Current.Active&&Current.Locked&&Current.NextSubhit==1&&Current.ForwardStepIssued&&K.State().Time==At,"post-At-live-current-state");
 }
 for(auto Weapon:{WA::EWeapon::GSW001,WA::EWeapon::SPR001})
 {
  WA::FWeaponActionsKernel K(Weapon,29);K.TryStart(WA::EAction::Skill,0.);const auto A=K.State().Action;
  K.StepTo(std::nextafter(A.ActiveAt,-std::numeric_limits<double>::infinity()));const auto Next=K.State().NextEventId;
  const auto Events=K.StepTo(A.ActiveAt);int Steps=0,Windows=0;for(const auto& E:Events){Steps+=E.Kind==WA::EEvent::ForwardStep;Windows+=E.Kind==WA::EEvent::ActiveWindow;}
  Check(Steps==0&&Windows==1&&K.State().NextEventId==Next+1,"non-SWD-first-real-window-has-no-forward-step");
 }
 std::cout<<"checks="<<Checks<<" failures="<<Failures<<'\n';return Failures?1:0;
}
