#include "DungeonFairytaleGuardPose.h"
#include <iostream>
#include <cmath>
namespace G=DungeonStoneGuard;namespace P=DungeonFairytaleGuard;
int Fail(const char* S){std::cerr<<S<<"\n";return 1;}
G::FWorldInput World(double X=150,double Y=0){G::FWorldInput W;W.HasTarget=true;W.Target={X,Y,0};W.Sweep=[](const G::FSweepRequest&){return G::FSweepResult{};};return W;}
int main(){
 G::FGuardKernel K(91);auto W=World();if(!K.BeginCombat()||!K.StepTo(0,W).Accepted)return Fail("precondition Wake source");
 auto R=P::Select(K.State());if(!R.Valid||R.Clip!=P::EClip::Wake||R.Frame!=0)return Fail("Stage0 RED: actual native Wake selects six-phase row, not Ready");
 if(!K.ApplyResolvedHit(1,1.,0.,W).Accepted)return Fail("native ordinary hit precondition");R=P::Select(K.State());if(R.Clip!=P::EClip::Wake||!R.MaterialHit)return Fail("ordinary actual hit must remain Wake+material only");
 if(!K.StepTo(1.,W).Accepted||!K.TryStartAttack(G::EAttack::AxeSweep,W).Accepted)return Fail("native axe admission");const auto A=K.State().Action;
 if(!K.StepTo(A.ActiveAt,W).Accepted)return Fail("native active boundary");R=P::Select(K.State());if(R.Clip!=P::EClip::AxeFollow||R.Frame!=0)return Fail("native active0 frame");
 if(!K.StepTo(A.ActiveEnd,W).Accepted)return Fail("native recovery boundary");R=P::Select(K.State());if(R.Clip!=P::EClip::AxeFollow||R.Frame!=2)return Fail("actual ActiveEnd must select recovery frame2");
 G::FGuardKernel M(92);auto MW=World(450);MW.CanStartAttack=false;M.BeginCombat();M.NotifyOtherAcceptedEnemiesCleared();if(!M.StepTo(0,MW).Accepted)return Fail("native locomotion source");
 const double Distances[]={2.,24.,46.,68.,90.,112.,134.};const int Frames[]={0,1,2,3,4,5,0};
 for(int I=0;I<7;++I){if(!M.StepTo(1.+Distances[I]/160.,MW).Accepted)return Fail("accepted native move");R=P::Select(M.State());if(R.Clip!=P::EClip::Move||R.Frame!=Frames[I])return Fail("128world distance phase must select all6 frames across true accepted path");}
 const double Before=R.AcceptedDistance;MW.Target=M.State().Position;if(!M.StepTo(M.State().Time+.5,MW).Accepted)return Fail("native stopped interval");R=P::Select(M.State());if(R.Clip!=P::EClip::Ready||R.AcceptedDistance!=Before)return Fail("stopped elapsed clock cannot advance distance phase");
 MW.Target={450,0,0};MW.Sweep=[](const G::FSweepRequest&){return G::FSweepResult{true,0.,G::EStop::Wall};};if(!M.StepTo(M.State().Time+.1,MW).Accepted)return Fail("native blocked interval");R=P::Select(M.State());if(R.Clip!=P::EClip::Ready||R.AcceptedDistance!=Before)return Fail("blocked zero-distance receipt cannot select Move");
 G::FGuardKernel I(93);auto IW=World();I.BeginCombat();if(!I.StepTo(1.,IW).Accepted||!I.TryStartAttack(G::EAttack::AxeSweep,IW).Accepted)return Fail("native interrupt source");const auto Original=I.State().Action;
 if(!I.StepTo(Original.ActiveAt-.1,IW).Accepted||!I.ApplyResolvedHit(1,1.,85.,IW).Accepted)return Fail("actual poise85 break");R=P::Select(I.State());if(R.Clip!=P::EClip::Stunned||R.Frame!=0)return Fail("poise85 real Stunned priority");
 const double StunEnd=I.State().StunUntil;if(!I.StepTo(StunEnd,IW).Accepted)return Fail("actual stun ends");R=P::Select(I.State());if(R.Clip!=P::EClip::InterruptedRecovery||R.Frame!=0||R.IntervalEnd!=Original.RecoveryEnd)return Fail("interrupted recovery begins only after real stun, retaining original deadline");
 if(!I.StepTo(Original.RecoveryEnd,IW).Accepted)return Fail("original recovery completed");R=P::Select(I.State());if(R.Clip==P::EClip::InterruptedRecovery)return Fail("no extra interrupted recovery after actual occupied deadline");
 if(!I.ApplyResolvedHit(2,184.,0.,IW).Accepted||!I.StepTo(I.State().Time+1.5,IW).Accepted)return Fail("real lethal death source");R=P::Select(I.State());if(R.Clip!=P::EClip::Death||R.Frame!=5)return Fail("actual death completes visual row and holds last frame");
 const auto Saved=I.Capture();G::FGuardKernel Copy(93);if(!Copy.Restore(Saved))return Fail("native full restore control");auto Same=P::Select(Copy.State());if(Same.Clip!=R.Clip||Same.Frame!=R.Frame||Same.SourceEventId!=R.SourceEventId)return Fail("restored selector is pure and same-event");
 std::cout<<"Pure native-kernel Guard selector tests passed; NOT UE renderer/art acceptance.\n";return 0;}
