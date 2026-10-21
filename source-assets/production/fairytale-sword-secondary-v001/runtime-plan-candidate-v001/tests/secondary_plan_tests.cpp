#include "DungeonFairytaleSwordSecondaryPlanV001.h"
#include <iostream>
#include <limits>
#include <string>

namespace S=DungeonFairytaleSwordSecondaryV001;
namespace WA=DungeonWeaponActions;
static int Checks=0,Failures=0;
void Expect(bool Value,const char* Name){++Checks;if(!Value){++Failures;std::cout<<"FAIL "<<Name<<'\n';}}
WA::FAction Action(double Speed=0.)
{
 WA::FAction A;A.Active=true;A.Type=WA::EAction::Skill;A.Weapon=WA::EWeapon::SWD001;
 A.ActionId=71;A.InstanceId=29;A.Facing=1.;A.SpeedPct=Speed;
 const double Rate=1.+Speed/100.;A.Start=0.;A.LockAt=.08/Rate;A.ActiveAt=.20/Rate;A.ActiveEnd=.30/Rate;A.End=.68/Rate;
 return A;
}
S::FContext Context(double Now)
{
 S::FContext C;C.OptIn=C.EquipmentBound=C.OwnerAuthorized=C.Grounded=true;C.BoundWeaponInstanceId=29;
 C.WeaponTime=C.StateTime=C.SimulationTime=Now;C.Armor=S::EArmor::Light;return C;
}
S::FSample At(WA::FAction A,double Now)
{
 A.Phase=Now<A.ActiveAt?WA::EPhase::Windup:Now<A.ActiveEnd?WA::EPhase::Active:WA::EPhase::Recovery;
 A.Locked=Now>=A.LockAt;return S::Sample(A,Context(Now));
}
int main()
{
 // A wrong old 6-frame/fixed-FPS sampler breaks these hand-derived base boundaries.
 const double Times[]={0.,.079,.08,.139,.14,.199,.20,.249,.25,.299,.30,.419,.42,.549,.55,.679};
 const int Want[]={0,0,1,1,2,2,3,3,4,4,5,5,6,6,7,7};
 for(int I=0;I<16;++I){const auto R=At(Action(),Times[I]);Expect(R.Decision==S::EDecision::Sampled&&R.Frame==Want[I],("base-boundary-"+std::to_string(I)).c_str());}
 // Speed must come exclusively from actual absolute deadlines, without changing rule time.
 // Base nominal .42/1.2 is one ULP BEFORE (.30/1.2)+(.68/1.2-.30/1.2)*12/38.
 // Use explicit phase interiors for speed and retain exact base/real deadline gates.
 const double SpeedTimes[]={0.,.04,.080001,.11,.140001,.17,.200001,.225,.250001,.275,.300001,.36,.420001,.485,.550001,.615};
 for(double Speed:{-20.,20.})for(int I=0;I<16;++I)
 {const auto R=At(Action(Speed),SpeedTimes[I]/(1.+Speed/100.));Expect(R.Decision==S::EDecision::Sampled&&R.Frame==Want[I],("deadline-speed-"+std::to_string(int(Speed))+"-index-"+std::to_string(I)+"-got-"+std::to_string(R.Frame)).c_str());}
 for(double Speed:{-20.,20.}){const auto T=Action(Speed);Expect(At(T,T.LockAt).Frame==1,"speed-real-LockAt");Expect(At(T,T.ActiveAt).Frame==3,"speed-real-ActiveAt");Expect(At(T,T.ActiveEnd).Frame==5,"speed-real-ActiveEnd");Expect(At(T,T.End).Decision==S::EDecision::Closed,"speed-real-End");}
 Expect(At(Action(),.68).Decision==S::EDecision::Closed,"active-at-End-never-holds-K7");
 for(int I=0;I<8;++I){auto Shifted=Action();for(double* T:{&Shifted.Start,&Shifted.LockAt,&Shifted.ActiveAt,&Shifted.ActiveEnd,&Shifted.End})*T+=37.5;
  const double Absolute[]={37.54,37.61,37.67,37.725,37.775,37.86,37.985,38.115};Expect(At(Shifted,Absolute[I]).Frame==I,"nonzero-absolute-Start");}
 auto A=Action();A.Active=false;Expect(At(A,.68).Decision==S::EDecision::PassThrough,"actual-completed-skill-returns-to-old-ready");
 A=Action();auto C=Context(.01);C.WeaponTime=.02;Expect(S::Sample(A,C).Decision==S::EDecision::Closed,"no-independent-clock");
 C=Context(.01);C.StateTime=.02;Expect(S::Sample(A,C).Decision==S::EDecision::Closed,"state-clock-must-match");
 C=Context(.01);C.SimulationTime=std::numeric_limits<double>::quiet_NaN();Expect(S::Sample(A,C).Decision==S::EDecision::Closed,"nan-clock");
 C=Context(.01);A.ActiveEnd=A.ActiveAt;Expect(S::Sample(A,C).Decision==S::EDecision::Closed,"bad-deadline-order");
 A=Action();A.LockAt=.07;Expect(S::Sample(A,C).Decision==S::EDecision::Closed,"wrong-lock-proportion");
 A=Action();A.InstanceId=30;Expect(S::Sample(A,C).Decision==S::EDecision::Closed,"wrong-action-instance");
 A=Action();A.Weapon=WA::EWeapon::GSW001;Expect(S::Sample(A,C).Decision==S::EDecision::Closed,"wrong-action-weapon");
 A=Action();A.StartedAirborne=true;Expect(S::Sample(A,C).Decision==S::EDecision::Closed,"air-start-rejected");
 A=Action();A.Phase=WA::EPhase::Active;Expect(S::Sample(A,C).Decision==S::EDecision::Closed,"actual-phase-mismatch-closed");
 A=Action();A.Locked=true;Expect(S::Sample(A,C).Decision==S::EDecision::Closed,"actual-lock-mismatch-closed");
 A=Action();C=Context(.01);C.Dead=true;Expect(S::Sample(A,C).Decision==S::EDecision::Closed,"death-no-secondary-draw");
 C=Context(.01);C.Hurt=true;Expect(S::Sample(A,C).Decision==S::EDecision::Closed,"poise-hurt-no-secondary-draw");
 C=Context(.01);C.Dodging=true;Expect(S::Sample(A,C).Decision==S::EDecision::Closed,"dodge-no-secondary-draw");
 C=Context(.01);C.MeleeActive=true;Expect(S::Sample(A,C).Decision==S::EDecision::Closed,"no-J-and-K-double-draw");
 C=Context(.01);C.Equipping=true;Expect(S::Sample(A,C).Decision==S::EDecision::Closed,"equip-no-secondary-draw");
 C=Context(.01);C.Height=1.;Expect(S::Sample(A,C).Decision==S::EDecision::Closed,"actual-height-ground-check");
 C=Context(.01);C.VerticalVelocity=1.;Expect(S::Sample(A,C).Decision==S::EDecision::Closed,"actual-velocity-ground-check");
 C=Context(.01);C.OptIn=false;Expect(S::Sample(A,C).Decision==S::EDecision::PassThrough,"default-off-untouched");
 C=Context(.01);C.OwnerAuthorized=false;Expect(S::Sample(A,C).Decision==S::EDecision::PassThrough,"unsupported-identity-no-borrowed-armor");
 C=Context(.01);C.Armor=S::EArmor::Unsupported;Expect(S::Sample(A,C).Decision==S::EDecision::PassThrough,"unsupported-armor-no-LGT");
 C=Context(.01);A.Type=WA::EAction::Primary;Expect(S::Sample(A,C).Decision==S::EDecision::PassThrough,"J-remains-J");
 Expect(S::SelectedSlotCount(S::EArmor::None)==5&&S::SelectedSlotCount(S::EArmor::Light)==8,"None5-LGT8");
 std::array<bool,57> Resident;Resident.fill(true);Expect(S::AllResident(Resident),"full-closure");
 Resident[55]=false;Expect(!S::AllResident(Resident),"missing-future-K7-layer-closes-entire-draw");
 Resident.fill(true);Resident[56]=false;Expect(!S::AllResident(Resident),"missing-independent-sword-closes-draw");
 S::FProfile P;Expect(!S::ProfileValid(P),"unadmitted-default-profile-closed");
 // Test-only provenance literals exercise the validator; never candidate runtime data.
 const char* Hash="0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef";
 P.RuntimeReady=true;P.ProfileId="TEST-ONLY-secondary-fixture";P.SourceContractSha256=Hash;
 P.Sword={"/Game/Production/TestOnly/T_Sword.T_Sword",{"source-assets/test-only/sword.png",Hash,111}};
 for(auto& F:P.Frames){F.Root={256.,464.};F.Grip={211.,343.};F.Axis={1.,-1.};for(auto& L:F.Layers)L={"/Game/Production/TestOnly/T_Layer.T_Layer",{"source-assets/test-only/layer.png",Hash,111}};}
 Expect(S::ProfileValid(P),"complete-profile-can-be-validated");
 P.Frames[7].Layers[6].Source.Sha256=nullptr;Expect(!S::ProfileValid(P),"missing-future-source-pin-closed");
 P.Frames[7].Layers[6].Source.Sha256=Hash;P.Frames[2].Axis={0.,0.};Expect(!S::ProfileValid(P),"zero-axis-closed");
 P.Frames[2].Axis={1.,-1.};P.Frames[2].Root.Y=465.;Expect(!S::ProfileValid(P),"incompatible-author-root-closed");
 P.Frames[2].Root.Y=464.;P.RuntimeReady=false;Expect(!S::ProfileValid(P),"explicit-unadmitted-data-gate-closed");
 // A second flip, reversed pivot or world-space canvas offset breaks these.
 S::FGeometryContext G;G.GroundScreen={640.,360.};S::FGeometry Right,Left;
 const bool RightOK=S::Geometry(P.Frames[0],1,G,Right),LeftOK=S::Geometry(P.Frames[0],-1,G,Left);
 Expect(RightOK&&LeftOK,"both-facing-geometry");
 Expect(std::abs(Right.GripScreen.X+Left.GripScreen.X-1280.)<1.e-9&&std::abs(Right.GripScreen.Y-Left.GripScreen.Y)<1.e-9,"single-reflected-grip");
 Expect(Right.U==0.&&Right.DU==1.&&Left.U==1.&&Left.DU==-1.,"one-UV-mirror");
 Expect(std::abs(Right.Angle+45.)<1.e-9&&std::abs(Left.Angle-45.)<1.e-9,"reflected-axis-rotation");
 Expect(std::abs(Right.SwordPivot.X+Left.SwordPivot.X-1.)<1.e-9&&Right.SwordPivot.Y==.5&&Left.SwordPivot.Y==.5,"reflected-existing-sword-grip");
 Expect(std::abs(Right.BodyTop.X-Left.BodyTop.X)<1.e-9&&std::abs(Right.BodyTop.Y-Left.BodyTop.Y)<1.e-9,"root-is-actor-no-local-forward-step");
 G.UIScale=0.;Expect(!S::Geometry(P.Frames[0],1,G,Right),"invalid-UI-scale-closes-geometry");
 // Consume actual public WA kernel results, not a forged J stage or animation clock.
 const double Interior[]={.04,.11,.17,.225,.275,.36,.485,.615};
 for(double Speed:{-20.,0.,20.})
 {
  WA::FWeaponActionsKernel K(WA::EWeapon::SWD001,29);WA::FContext Real;Real.ActionSpeedPct=Speed;
  Expect(K.TryStart(WA::EAction::Skill,0.,Real),"real-WA-skill-accepted");
  for(int I=0;I<8;++I)
  {
   const double Now=Interior[I]/(1.+Speed/100.);K.StepTo(Now,Real);
   auto Actual=Context(K.State().Time);const auto R=S::Sample(K.State().Action,Actual);
   Expect(R.Decision==S::EDecision::Sampled&&R.Frame==I&&R.Action.ActionId==K.State().Action.ActionId&&R.Action.InstanceId==29,"real-WA-eight-frame-consumer");
  }
  const double End=K.State().Action.End;K.StepTo(End,Real);
  Expect(S::Sample(K.State().Action,Context(End)).Decision==S::EDecision::PassThrough,"real-WA-completed-no-last-frame-hold");
 }
 WA::FWeaponActionsKernel Interrupted(WA::EWeapon::SWD001,29);Interrupted.TryStart(WA::EAction::Skill,0.);
 Interrupted.StepTo(.1);Interrupted.Interrupt(WA::EInterrupt::PoiseBreak);
 Expect(S::Sample(Interrupted.State().Action,Context(.1)).Decision==S::EDecision::PassThrough,"real-WA-poise-break-does-not-resurrect-K");
 std::cout<<"checks="<<Checks<<" failures="<<Failures<<'\n';return Failures?1:0;
}
