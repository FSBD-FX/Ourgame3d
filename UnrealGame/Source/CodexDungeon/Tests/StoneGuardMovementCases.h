#pragma once
#include "../DungeonStoneGuard.h"
#include <algorithm>
#include <cmath>
#include <functional>
#include <string>
#include <vector>
namespace StoneGuardMovementCases
{
using namespace DungeonStoneGuard;
using FCheck=std::function<void(bool,const char*)>;
struct FCase {const char* Name;FPoint Target,Expected;double StopDistance=0,SplitAt=0;};
inline bool Near(double A,double B){return std::abs(A-B)<1e-9;}
inline bool Same(FPoint A,FPoint B){return Near(A.X,B.X)&&Near(A.Y,B.Y)&&Near(A.Z,B.Z);}
inline FWorldInput World(FPoint Target,std::vector<FSweepRequest>* Trace=nullptr)
{
 FWorldInput W;W.HasTarget=true;W.Target=Target;
 W.Sweep=[Trace](const FSweepRequest& Q){if(Trace)Trace->push_back(Q);return FSweepResult{};};return W;
}
inline bool Awake(FGuardKernel& K)
{
 const auto W=World({100,0,0});const auto A=K.StepTo(0,W),B=K.StepTo(1,W);
 return A.Accepted&&B.Accepted&&K.State().Awakened&&K.State().Phase==EPhase::Idle&&K.State().Time==1;
}
inline FPoint Sample(const std::vector<FSweepRequest>& Trace,double At)
{
 FPoint P{};for(const auto& Q:Trace)
 {
  if(At<Q.FromTime)return P;
  if(At<=Q.ToTime)
  {
   const double F=(At-Q.FromTime)/(Q.ToTime-Q.FromTime);
   return {Q.From.X+(Q.To.X-Q.From.X)*F,Q.From.Y+(Q.To.Y-Q.From.Y)*F,Q.From.Z};
  }
  P=Q.To;
 }
 return P;
}
// Independent hand-derived expected path for six cases, not the production intersection formula.
inline FPoint Expected(const FCase& C,double At)
{
 const double Travel=std::min(C.StopDistance,std::max(0.,At-1)*160.);
 const double YTravel=std::min(std::abs(C.Target.Y),Travel),XTravel=Travel-YTravel;
 return {(C.Target.X<0?-1:1)*XTravel,(C.Target.Y<0?-1:1)*YTravel,0};
}
inline bool Run(const FCheck& Check)
{
 bool All=true;const auto Ck=[&](bool Value,const std::string& Name){All&=Value;Check(Value,Name.c_str());};
 const FCase Cases[]={
  {"stomp_y_positive",{0,100,0},{0,10,0},10,1.1},
  {"stomp_y_negative",{0,-100,0},{0,-10,0},10,1.1},
  {"axe_y_positive",{150,100,0},{0,35,0},35,1.3},
  {"axe_y_negative",{-150,-100,0},{0,-35,0},35,1.3},
  {"two_axes_right",{300,100,0},{120,100,0},220,1.1},
  {"two_axes_left",{-300,-100,0},{-120,-100,0},220,1.1}};
 std::uint64_t Id=400;
 for(const auto& C:Cases)
 {
  const std::string Name=C.Name;FGuardKernel Whole(Id),Split(Id),Zero(Id);++Id;
  const bool Ready=Awake(Whole)&&Awake(Split)&&Awake(Zero);Ck(Ready,Name+" real wake prerequisite");if(!Ready)continue;
  std::vector<FSweepRequest> WholeTrace,SplitTrace,ZeroTrace;
  auto W=World(C.Target,&WholeTrace);const auto WholeResult=Whole.StepTo(2.7,W);
  W=World(C.Target,&SplitTrace);const auto First=Split.StepTo(C.SplitAt,W);const auto Last=Split.StepTo(2.7,W);
  W=World(C.Target,&ZeroTrace);const auto ZeroResult=Zero.StepTo(2.7,W,{{1,C.SplitAt,0,0}});
  Ck(WholeResult.Accepted&&First.Accepted&&Last.Accepted&&ZeroResult.Accepted,Name+" whole split zero-receipt accepted");
  Ck(Same(Whole.State().Position,C.Expected),Name+" whole stops at first shape entry");
  Ck(Same(Split.State().Position,C.Expected),Name+" split stops at first shape entry");
  Ck(Same(Zero.State().Position,C.Expected),Name+" zero receipt cannot change stop point");
  Ck(Same(Whole.State().Position,Split.State().Position)&&Same(Whole.State().Position,Zero.State().Position),Name+" final positions partition invariant");
  const double Stop=1+C.StopDistance/160.;
  Ck(!WholeTrace.empty()&&!SplitTrace.empty()&&!ZeroTrace.empty()&&Near(WholeTrace.back().ToTime,Stop)&&Near(SplitTrace.back().ToTime,Stop)&&Near(ZeroTrace.back().ToTime,Stop),Name+" movement ends at first-entry clock");
  bool Paths=true;for(double At:{1.,1.01,1.03,1.05,1.0625,1.1,1.21875,1.3,1.7,2.375,2.7})
  {const auto P=Expected(C,At);Paths&=Same(Sample(WholeTrace,At),P)&&Same(Sample(SplitTrace,At),P)&&Same(Sample(ZeroTrace,At),P);}
  Ck(Paths,Name+" complete sampled trajectories match analytic path");
  Ck(Whole.State().Time==2.7&&Split.State().Time==2.7&&Zero.State().Time==2.7&&Whole.State().HP==185&&Split.State().HP==185&&Zero.State().HP==185&&Zero.State().PoiseAccum==0,Name+" time HP poise unaffected");
  Ck(Whole.State().NextAttackId==1&&Split.State().NextAttackId==1&&Zero.State().NextAttackId==1&&Whole.State().AxeReadyAt==0&&Zero.State().StompReadyAt==0,Name+" no invented attacks or cooldown spending");
  Ck(Zero.State().ReceivedHits.size()==1&&Zero.State().ReceivedHits.front().ActualHPLoss==0&&Zero.State().ReceivedHits.front().Stagger==0&&Whole.State().ReceivedHits.empty(),Name+" zero receipt acknowledged without combat effects");
 }
 return All;
}
}
