#include "DungeonFairytaleGuardFullPoseV003.h"
#include <iostream>
#include <cmath>
namespace G=DungeonStoneGuard;namespace F=DungeonFairytaleGuardFullV003;
int Fail(const char* S){std::cerr<<S<<"\n";return 1;}
G::FWorldInput World(double X=150.){G::FWorldInput W;W.HasTarget=true;W.Target={X,0,0};W.Sweep=[](const G::FSweepRequest&){return G::FSweepResult{};};return W;}
int main(){
 G::FGuardKernel K(94001);auto W=World();if(!K.BeginCombat()||!K.StepTo(1.,W).Accepted||!K.TryStartAttack(G::EAttack::AxeSweep,W).Accepted)return Fail("actual Axe setup failed");auto A=K.State().Action;
 const double AA[]={0.,.05,.1,.15};for(int I=0;I<4;++I){if(!K.StepTo(A.ActiveAt+AA[I],W).Accepted)return Fail("actual active boundary refused");auto R=F::SelectFull(K.State());if(!R.Valid||R.Clip!=F::EClip::AxeActive||R.Frame!=I||R.IntervalEnd!=A.ActiveEnd)return Fail("Stage0 semantic RED: native AxeActive must be independent4 row at actual boundary");}
 const double AR[]={0.,.35,.7,1.05};for(int I=0;I<4;++I){if(!K.StepTo(A.ActiveEnd+AR[I],W).Accepted)return Fail("actual recovery refused");auto R=F::SelectFull(K.State());if(R.Clip!=F::EClip::AxeRecovery||R.Frame!=I||R.IntervalStart!=A.ActiveEnd||R.IntervalEnd!=A.RecoveryEnd)return Fail("AxeRecovery4 original bounds");}
 G::FGuardKernel T(94002);auto TW=World(55.);T.BeginCombat();if(!T.StepTo(1.,TW).Accepted||!T.TryStartAttack(G::EAttack::Stomp,TW).Accepted)return Fail("actual Stomp setup");A=T.State().Action;
 const double SW[]={0.,.15,.3,.45,.6,.75};for(int I=0;I<6;++I){if(!T.StepTo(A.Start+SW[I],TW).Accepted)return Fail("native Stomp windup");auto R=F::SelectFull(T.State());if(R.Clip!=F::EClip::StompWindup||R.Frame!=I)return Fail("StompWindup6");}
 for(int I=0;I<2;++I){if(!T.StepTo(A.ActiveAt+double(I)*.075,TW).Accepted)return Fail("native Stomp active");auto R=F::SelectFull(T.State());if(R.Clip!=F::EClip::StompActive||R.Frame!=I)return Fail("StompActive2");}
 const double SR[]={0.,.375,.75,1.125};for(int I=0;I<4;++I){if(!T.StepTo(A.ActiveEnd+SR[I],TW).Accepted)return Fail("native Stomp recovery");auto R=F::SelectFull(T.State());if(R.Clip!=F::EClip::StompRecovery||R.Frame!=I||R.IntervalEnd!=A.RecoveryEnd)return Fail("StompRecovery4 v005");}
 if(F::LogicalFrameBudget()!=57)return Fail("logical frame budget");std::cout<<"Actual pure kernel full split-phase selector passed. NOT UE/world/render/art acceptance.\n";return 0;}
