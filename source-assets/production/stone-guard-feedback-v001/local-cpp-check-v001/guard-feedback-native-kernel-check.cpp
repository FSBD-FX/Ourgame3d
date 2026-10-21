#include "DungeonStoneGuardFeedback.h"
#include <cassert>
#include <iostream>
namespace G=DungeonStoneGuard;namespace F=DungeonGuardFeedback;
int main(){
 G::FGuardKernel K(23);assert(K.BeginCombat());assert(K.NotifyOtherAcceptedEnemiesCleared());G::FWorldInput W;W.HasTarget=true;W.Target={450,0,0};W.CanStartAttack=false;W.Sweep=[](const G::FSweepRequest&){return G::FSweepResult{};};
 F::FJournal A;assert(A.Begin(K.State()));
 for(int i=0;i<160&&K.State().Position.X<90.;++i){const auto R=K.StepTo((i+1)*.01,W);assert(R.Accepted);assert(A.Observe(R.Events,K.State().Position));}
 const auto S=K.State();F::FJournal B;assert(B.Begin(S)&&B.Entries().empty());
 for(int i=0;i<30;++i){const auto R=K.StepTo(S.Time+(i+1)*.01,W);assert(R.Accepted);assert(A.Observe(R.Events,K.State().Position));assert(B.Observe(R.Events,K.State().Position));}
 const F::FRecord *X=nullptr,*Y=nullptr;for(const auto& R:A.Entries())if(R.Cue==F::ECue::Step&&R.EventId>=S.NextEventId)X=&R;for(const auto& R:B.Entries())if(R.Cue==F::ECue::Step)Y=&R;assert(X&&Y&&X->FootOrdinal==Y->FootOrdinal&&X->AtTime==Y->AtTime&&X->Position.X==Y->Position.X);
 // Real kernel hit authorization must remain silent until an actual-loss confirmation.
 G::FGuardKernel H(24);assert(H.BeginCombat());G::FWorldInput V;V.HasTarget=true;V.Target={150,0,0};V.Sweep=W.Sweep;F::FJournal J;assert(J.Begin(H.State()));
 for(int i=0;i<301;++i){auto R=H.StepTo((i+1)*.01,V);assert(R.Accepted);assert(J.Observe(R.Events,H.State().Position));if(H.State().Phase==G::EPhase::Active)break;}
 const auto Hit=H.TryHit({31,{150,0,0}});assert(Hit.Accepted&&J.Observe(Hit.Events,H.State().Position));const auto E=Hit.Events.back();int Old=0;for(const auto& R:J.Entries())if(R.SourceKind==G::EEventKind::Hit)++Old;assert(Old==0);
 assert(!J.ConfirmHit(E.EventId,31,E.AtTime,{150,0,0},F::EMaterial::Metal,0));assert(J.ConfirmHit(E.EventId,31,E.AtTime,{150,0,0},F::EMaterial::Metal,24));assert(!J.ConfirmHit(E.EventId,31,E.AtTime,{150,0,0},F::EMaterial::Metal,24));
 auto Invalid=Hit.Events;Invalid[0].EntityId=99;const auto Cursor=J.LastEventId(),Serial=J.LastSequence();assert(!J.Observe(Invalid,H.State().Position)&&J.LastEventId()==Cursor&&J.LastSequence()==Serial);
 std::cout<<"native kernel feedback check passed; NOT UE HUD/audio proof\n";
}
