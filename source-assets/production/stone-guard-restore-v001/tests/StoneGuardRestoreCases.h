#pragma once
#if WITH_DEV_AUTOMATION_TESTS
#include "../DungeonStoneGuard.h"
#else
#include "DungeonStoneGuard.h"
#endif
#include <cmath>
#include <functional>
#include <iomanip>
#include <limits>
#include <sstream>
#include <string>
#include <utility>
#include <vector>

namespace StoneGuardRestoreCases
{
using namespace DungeonStoneGuard;
using FCheck=std::function<void(bool,const char*)>;
inline void Point(std::ostream& O,FPoint P){O<<P.X<<','<<P.Y<<','<<P.Z<<';';}
inline void Action(std::ostream& O,const FAction& A)
{
 O<<A.AttackId<<','<<int(A.Kind)<<','<<A.InProgress<<A.Locked<<A.WindowIssued<<A.Interrupted<<';'
  <<A.Start<<','<<A.LockAt<<','<<A.ActiveAt<<','<<A.ActiveEnd<<','<<A.RecoveryEnd<<','<<A.CooldownEnd<<','
  <<A.InterruptedAt<<','<<A.CompletedAt<<','<<A.Damage<<','<<A.Stagger<<','<<A.Facing<<';';
 Point(O,A.Origin);Point(O,A.LockedCenter);Point(O,A.Target);
}
inline std::string Signature(const FState& S)
{
 std::ostringstream O;O<<std::setprecision(17)<<S.Version<<','<<S.EntityId<<','<<S.NextAttackId<<','<<S.NextEventId<<','<<S.LastDamageReceiptId<<';'
  <<S.InitialTime<<','<<S.Time<<','<<S.HP<<','<<S.PoiseAccum<<','<<S.PoiseDecayOrigin<<','<<S.LastPoiseAt<<','<<S.ProtectionUntil<<','<<S.StunUntil<<','
  <<S.CombatStartedAt<<','<<S.WakeStartedAt<<','<<S.WakeEnd<<','<<S.AxeReadyAt<<','<<S.StompReadyAt<<','<<S.OccupiedUntil<<','<<S.IdleReadyAt<<';'
  <<S.WakeQueued<<S.Awakened<<S.RewardClaimed<<','<<int(S.Phase)<<','<<S.Facing<<';';
 Point(O,S.InitialPosition);Point(O,S.Position);Action(O,S.Action);
 O<<S.Windows.size()<<';';for(const auto& W:S.Windows){O<<W.AttackId<<','<<W.EventId<<','<<int(W.Kind)<<','<<W.Start<<','<<W.End<<','<<W.Damage<<','<<W.Stagger<<','<<W.Facing<<';';Point(O,W.Center);}
 O<<S.Closures.size()<<';';for(const auto& C:S.Closures)O<<C.AttackId<<','<<C.AtTime<<';';
 O<<S.HitReceipts.size()<<';';for(const auto& H:S.HitReceipts)O<<H.AttackId<<','<<H.TargetId<<','<<H.AtTime<<';';
 O<<S.ReceivedHits.size()<<';';for(const auto& H:S.ReceivedHits)O<<H.ReceiptId<<','<<H.AtTime<<','<<H.ActualHPLoss<<','<<H.Stagger<<';';
 O<<S.Issued.size()<<';';for(const auto& E:S.Issued){O<<E.EventId<<','<<E.EntityId<<','<<E.TargetId<<','<<int(E.Kind)<<','<<E.AtTime<<','<<E.EndTime<<','<<E.Amount<<';';Point(O,E.From);Point(O,E.To);Action(O,E.Action);}
 return O.str();
}
inline FWorldInput World(double X=150,double Y=0,double Z=0)
{FWorldInput W;W.HasTarget=true;W.Target={X,Y,Z};W.Sweep=[](const FSweepRequest&){return FSweepResult{};};return W;}
inline bool Awake(FGuardKernel& K)
{
 const auto P=K.State().Position;const auto W=World(P.X+150,P.Y,P.Z);
 return K.StepTo(K.State().Time,W).Accepted&&K.StepTo(K.State().WakeEnd,W).Accepted&&K.State().Phase==EPhase::Idle;
}
inline bool ActiveAxe(FGuardKernel& K)
{const auto W=World();return Awake(K)&&K.TryStartAttack(EAttack::AxeSweep,W).Accepted&&K.StepTo(K.State().Action.ActiveAt,W).Accepted;}
inline bool Continue(FGuardKernel& Original,FGuardKernel& Restored,const FCheck& Check)
{
 bool All=true;const auto C=[&](bool V,const char* N){All&=V;Check(V,N);};
 const auto S=Original.Capture();
 if(S.Phase==EPhase::Active)
 {
  auto P=S.Action.LockedCenter;P.X+=S.Action.Kind==EAttack::AxeSweep?S.Action.Facing*50.:0.;
  const auto A=Original.TryHit({9001,P}),B=Restored.TryHit({9001,P});
  C(A.Accepted==B.Accepted&&Signature(Original.Capture())==Signature(Restored.Capture()),"continuation preserves new outgoing receipt exactly");
 }
 if(S.Phase!=EPhase::Dead)
 {
  const auto Id=S.LastDamageReceiptId+17;
  const auto A=Original.ApplyResolvedHit(Id,.25,5,World(900)),B=Restored.ApplyResolvedHit(Id,.25,5,World(900));
  C(A.Accepted&&B.Accepted&&Signature(Original.Capture())==Signature(Restored.Capture()),"continuation preserves actual HP poise and incoming cursor");
 }
 const double Future=S.Time+4.;const auto A=Original.StepTo(Future,World(900)),B=Restored.StepTo(Future,World(900));
 C(A.Accepted&&B.Accepted&&Signature(Original.Capture())==Signature(Restored.Capture()),"continuation preserves every future deadline and historical value");
 if(Original.State().Phase==EPhase::Dead)
 {
  const auto R1=Original.ClaimDeathReward(),R2=Restored.ClaimDeathReward();
  C(R1.Accepted==R2.Accepted&&Signature(Original.Capture())==Signature(Restored.Capture()),"continuation preserves once death eligibility without reissuing death");
 }
 return All;
}
inline bool StageRoundTrips(const FCheck& Check)
{
 FGuardKernel K(501);const auto Far=World(900),Near=World();
 if(!K.BeginCombat()||!K.StepTo(.25,Far).Accepted){Check(false,"real dormant fixture prerequisite");return false;}
 FGuardKernel Probe(501);const auto First=K.Capture();
 if(!Probe.Restore(First)){Check(false,"Restore admits real dormant same-birth state (Stage0 RED)");return false;}
 Check(true,"Restore admits real dormant same-birth state (Stage0 RED)");
 bool All=true;const auto C=[&](bool V,const char* N){All&=V;Check(V,N);};
 std::vector<std::pair<std::string,FGuardKernel>> Cases;Cases.emplace_back("Dormant",K);
 C(K.StepTo(.25,Near).Accepted&&K.State().WakeEnd==1.25,"real full wake starts from existing dormant clock");Cases.emplace_back("Waking",K);
 C(K.StepTo(1.25,Near).Accepted&&K.State().Phase==EPhase::Idle,"real warning completed");Cases.emplace_back("Idle",K);
 C(K.TryStartAttack(EAttack::AxeSweep,Near).Accepted&&K.StepTo(1.5,Near).Accepted,"real axe unlocked windup");Cases.emplace_back("AxeWindup",K);
 C(K.StepTo(K.State().Action.LockAt,World(-150)).Accepted&&K.State().Action.Locked,"real mirrored axe locked windup");Cases.emplace_back("AxeLocked",K);
 C(K.StepTo(K.State().Action.ActiveAt,World(-150)).Accepted&&K.TryHit({5000,{-100,0,0}}).Accepted,"real axe active once-hit receipt");
 C(K.ApplyResolvedHit(5,.625,12,World(-150)).Accepted,"real noninterrupting received receipt with ID gap");Cases.emplace_back("AxeActive",K);
 C(K.StepTo(K.State().Action.ActiveEnd+.05,Near).Accepted&&K.State().Phase==EPhase::Recovery,"real axe recovery");Cases.emplace_back("AxeRecovery",K);
 C(K.StepTo(K.State().Action.RecoveryEnd,Near).Accepted&&K.State().Action.CompletedAt>=0,"real axe completion");Cases.emplace_back("AxeCompletedIdleGap",K);
 C(K.StepTo(K.State().IdleReadyAt,World(50)).Accepted&&K.TryStartAttack(EAttack::Stomp,World(50)).Accepted,"real cross-kind stomp after retained idle gap");Cases.emplace_back("StompWindup",K);
 C(K.StepTo(K.State().Action.LockAt,World(50)).Accepted,"real stomp center lock");Cases.emplace_back("StompLocked",K);
 C(K.StepTo(K.State().Action.ActiveAt,World(50)).Accepted&&K.TryHit({5001,{0,80,0}}).Accepted,"real stomp single active impulse");Cases.emplace_back("StompActive",K);
 C(K.StepTo(K.State().Action.ActiveEnd,World(50)).Accepted,"real stomp recovery");Cases.emplace_back("StompRecovery",K);
 C(K.StepTo(K.State().Action.RecoveryEnd,World(50)).Accepted,"real second action completion");Cases.emplace_back("StompCompleted",K);
 FGuardKernel Queued(502);auto NoSlot=Near;NoSlot.CanBeginWake=false;
 C(Queued.StepTo(.5,NoSlot).Accepted&&Queued.State().WakeQueued&&Queued.State().WakeStartedAt<0,"real queued wake without consumed warning");Cases.emplace_back("QueuedWake",Queued);
 FGuardKernel Moving(503);C(Awake(Moving)&&Moving.StepTo(1.3,World(300,100)).Accepted,"real read-only movement history fixture");Cases.emplace_back("IdleMovement",Moving);
 for(auto& Item:Cases)
 {
  auto Original=Item.second;const auto Saved=Original.Capture();FGuardKernel Restored(Saved.EntityId,Saved.InitialTime,Saved.InitialPosition,Saved.Facing,Original.CapturePolicy());
  const bool Accepted=Restored.Restore(Saved);const std::string Name=Item.first+" exact complete value Restore";
  C(Accepted&&Signature(Restored.Capture())==Signature(Saved),Name.c_str());
  if(Accepted)All&=Continue(Original,Restored,Check);
 }
 const FPolicy Policy{123};FGuardKernel Custom(504,7,{23,-40,0},-1,Policy);
 C(Awake(Custom),"real nonzero birth custom-policy fixture");const auto Saved=Custom.Capture();FGuardKernel CustomRestored(504,7,{23,-40,0},-1,Policy);
 C(CustomRestored.Restore(Saved)&&CustomRestored.CapturePolicy().ExtremelyCloseRadius==123
   &&CustomRestored.ChooseAttack(World(123,-40))==EAttack::Stomp,"Restore retains explicitly reconstructed nondefault policy and behavior");
 return All;
}
inline bool HistoriesAndObligations(const FCheck& Check)
{
 FGuardKernel Closed(601);if(!ActiveAxe(Closed)||!Closed.TryHit({6000,{100,0,0}}).Accepted||!Closed.StepTo(2.1,World(),{{11,2.1,1,85}}).Accepted)
 {Check(false,"real active closure prerequisite");return false;}
 FGuardKernel R(601);if(!R.Restore(Closed.Capture())){Check(false,"Restore admits real independent closure and stun (Stage0 RED)");return false;}
 Check(true,"Restore admits real independent closure and stun (Stage0 RED)");
 bool All=true;const auto C=[&](bool V,const char* N){All&=V;Check(V,N);};
 C(R.State().Windows.size()==1&&R.State().Closures.size()==1&&R.State().Windows.front().End==Closed.State().Windows.front().End
   &&!R.TryHit({6001,{100,0,0}}).Accepted,"restored independent closure never reopens or rewrites issued window");
 All&=Continue(Closed,R,Check);
 FGuardKernel Straddled(602);C(ActiveAxe(Straddled),"real late recovery fixture");const double End=Straddled.State().Action.RecoveryEnd;
 C(Straddled.StepTo(End+.1,World(),{{5,End-.1,1,85}}).Accepted&&Straddled.State().Phase==EPhase::Stunned
   &&Straddled.State().Action.CompletedAt==End,"real recovery completion occurs inside stun at original deadline");
 FGuardKernel SR(602);C(SR.Restore(Straddled.Capture()),"Restore admits completed recovery still inside hurt pose");All&=Continue(Straddled,SR,Check);
 FGuardKernel Overlap(603);C(Overlap.StepTo(0,World()).Accepted&&Overlap.StepTo(1.1,World(),{{7,.9,1,85}}).Accepted
   &&Overlap.State().Awakened&&Overlap.State().Phase==EPhase::Stunned,"real wake completes while stun remains owned");
 FGuardKernel OR(603);C(OR.Restore(Overlap.Capture()),"Restore preserves overlapping independent wake/stun clocks");All&=Continue(Overlap,OR,Check);
 FGuardKernel Dead(604);C(ActiveAxe(Dead)&&Dead.StepTo(3,World(),{{17,2,185,100},{29,2.5,10,85}}).Accepted,"real prevalidated lethal then later receipt fixture");
 FGuardKernel DR(604);C(DR.Restore(Dead.Capture())&&DR.State().ReceivedHits.size()==2&&DR.State().ReceivedHits.back().ActualHPLoss==0
   &&DR.State().LastDamageReceiptId==29,"Restore preserves later zero actual damage receipt after lethal boundary");All&=Continue(Dead,DR,Check);
 const auto Claimed=Dead.Capture();FGuardKernel CR(604);C(CR.Restore(Claimed)&&!CR.ClaimDeathReward().Accepted
   &&Signature(CR.Capture())==Signature(Claimed),"claimed death Restore neither resets eligibility nor reissues events");
 FGuardKernel SameCursor(605);C(SameCursor.ApplyResolvedHit(3,0,85,World(900)).Accepted
   &&SameCursor.ApplyResolvedHit(9,185,0,World(900)).Accepted,"real same-cursor break then lethal separate transactions");
 FGuardKernel SC(605);C(SC.Restore(SameCursor.Capture())&&SC.State().StunUntil==.4&&SC.State().ProtectionUntil==1
   &&SC.State().Phase==EPhase::Dead,"Restore does not erase prior same-cursor break by regrouping lethal receipts");All&=Continue(SameCursor,SC,Check);
 FGuardKernel SameWeak(606);C(SameWeak.ApplyResolvedHit(1,0,40,World(900)).Accepted&&SameWeak.ApplyResolvedHit(4,185,0,World(900)).Accepted,"real same-cursor weak poise then death transactions");
 FGuardKernel SW(606);C(SW.Restore(SameWeak.Capture())&&SW.State().PoiseDecayOrigin==40,"Restore preserves effective subthreshold poise before separate lethal batch");All&=Continue(SameWeak,SW,Check);
 FGuardKernel CompletedDeath(607);C(ActiveAxe(CompletedDeath)&&CompletedDeath.StepTo(4.5,World()).Accepted
   &&CompletedDeath.ApplyResolvedHit(1,185,0,World()).Accepted,"real death after already completed action");
 FGuardKernel CD(607);C(CD.Restore(CompletedDeath.Capture())&&CD.State().Action.CompletedAt==4.5,"Restore retains death-time current completion and immutable old completion event");
 return All;
}
inline bool CorruptionAndAtomicity(const FCheck& Check)
{
 FGuardKernel Source(701);if(!ActiveAxe(Source)||!Source.TryHit({7000,{100,0,0}}).Accepted
  ||!Source.ApplyResolvedHit(5,1,20,World()).Accepted||!Source.StepTo(2.1,World(),{{11,2.1,2,65}}).Accepted)
 {Check(false,"real rich damaged closed fixture prerequisite");return false;}
 const auto Saved=Source.Capture();FGuardKernel Receiver(701,0,{},1,FPolicy{123});
 if(!Receiver.Restore(Saved)){Check(false,"Restore admits rich validated positive premise before rejection matrix (Stage0 RED)");return false;}
 Check(true,"Restore admits rich validated positive premise before rejection matrix (Stage0 RED)");
 bool All=true;const auto C=[&](bool V,const char* N){All&=V;Check(V,N);};const auto Before=Signature(Receiver.Capture());
 using FMutate=std::function<void(FState&)>;const double NaN=std::numeric_limits<double>::quiet_NaN();
 const std::vector<std::pair<const char*,FMutate>> Mutations={
 {"unknown state version",[](auto& S){++S.Version;}},{"different entity",[](auto& S){++S.EntityId;}},
 {"changed birth time",[](auto& S){S.InitialTime=.1;}},{"changed birth position",[](auto& S){S.InitialPosition.X=1;}},
 {"nonfinite clock",[NaN](auto& S){S.Time=NaN;}},{"clock before history",[](auto& S){S.Time=1;}},
 {"HP detached from actual damage receipts",[](auto& S){++S.HP;}},{"dead phase with positive HP",[](auto& S){S.Phase=EPhase::Dead;}},
 {"poise decay origin corruption",[](auto& S){++S.PoiseDecayOrigin;}},{"poise accumulator corruption",[](auto& S){++S.PoiseAccum;}},
 {"future last poise",[](auto& S){S.LastPoiseAt=S.Time+1;}},{"protection detached from break",[](auto& S){S.ProtectionUntil+=.1;}},
 {"stun detached from break",[](auto& S){S.StunUntil+=.1;}},{"bad combat sentinel",[](auto& S){S.CombatStartedAt=-.5;}},
 {"bad wake end",[](auto& S){S.WakeEnd+=.01;}},{"queued after awake",[](auto& S){S.WakeQueued=true;}},
 {"axe cooldown corruption",[](auto& S){S.AxeReadyAt+=.01;}},{"unused stomp cooldown invented",[](auto& S){S.StompReadyAt=.01;}},
 {"occupancy corruption",[](auto& S){S.OccupiedUntil+=.01;}},{"minimum idle gap corruption",[](auto& S){S.IdleReadyAt+=.01;}},
 {"invalid facing",[](auto& S){S.Facing=0;}},{"phase detached from live stun",[](auto& S){S.Phase=EPhase::Idle;}},
 {"next attack cursor corruption",[](auto& S){++S.NextAttackId;}},{"next event cursor corruption",[](auto& S){++S.NextEventId;}},
 {"last incoming cursor corruption",[](auto& S){++S.LastDamageReceiptId;}},{"current action mismatch",[](auto& S){++S.Action.Damage;}},
 {"nonfinite action target",[NaN](auto& S){S.Action.Target.X=NaN;}},{"illegal interrupted action flag",[](auto& S){S.Action.Interrupted=false;}},
 {"duplicate window",[](auto& S){S.Windows.push_back(S.Windows.front());}},{"wrong window event link",[](auto& S){S.Windows.front().EventId=1;}},
 {"rewritten immutable window end",[](auto& S){S.Windows.front().End=S.Time;}},{"wrong locked window center",[](auto& S){S.Windows.front().Center.X=1;}},
 {"missing closing receipt",[](auto& S){S.Closures.clear();}},{"duplicate closing receipt",[](auto& S){S.Closures.push_back(S.Closures.front());}},
 {"unknown closure action",[](auto& S){++S.Closures.front().AttackId;}},{"preactive closure time",[](auto& S){S.Closures.front().AtTime=1;}},
 {"duplicate target hit receipt",[](auto& S){S.HitReceipts.push_back(S.HitReceipts.front());}},
 {"self hit receipt",[](auto& S){S.HitReceipts.front().TargetId=S.EntityId;}},{"hit at exclusive active end",[](auto& S){S.HitReceipts.front().AtTime=S.Windows.front().End;}},
 {"unknown hit action",[](auto& S){++S.HitReceipts.front().AttackId;}},{"duplicate incoming ID",[](auto& S){S.ReceivedHits.back().ReceiptId=S.ReceivedHits.front().ReceiptId;}},
 {"unordered incoming time",[](auto& S){S.ReceivedHits.front().AtTime=2.2;}},{"nonfinite incoming stagger",[NaN](auto& S){S.ReceivedHits.front().Stagger=NaN;}},
 {"negative incoming actual loss",[](auto& S){S.ReceivedHits.front().ActualHPLoss=-1;}},{"missing actual loss history",[](auto& S){S.ReceivedHits.clear();}},
 {"duplicate issued event ID",[](auto& S){S.Issued.back().EventId=1;}},{"foreign issued entity",[](auto& S){S.Issued.back().EntityId=999;}},
 {"future issued event",[](auto& S){S.Issued.back().AtTime=S.Time+1;}},{"unknown issued kind",[](auto& S){S.Issued.back().Kind=static_cast<EEventKind>(255);}},
 {"issued action damage tampered",[](auto& S){++S.Issued.back().Action.Damage;}},{"invented alive reward claim",[](auto& S){S.RewardClaimed=true;}},
 {"exceeded bounded window storage",[](auto& S){S.Windows.resize(65537);}}
 };
 for(const auto& M:Mutations)
 {
  auto Bad=Saved;M.second(Bad);const bool Rejected=!Receiver.Restore(Bad);const std::string Name=std::string(M.first)+" rejects atomically";
  C(Rejected&&Signature(Receiver.Capture())==Before&&Receiver.CapturePolicy().ExtremelyCloseRadius==123,Name.c_str());
 }
 auto External=Saved;External.Windows.clear();External.Closures.clear();External.HitReceipts.clear();External.ReceivedHits.clear();External.Issued.clear();External.Position.X=999;
 C(Signature(Receiver.Capture())==Before,"Restore does not alias caller state or nested historical vectors");
 auto Readback=Receiver.Capture();Readback.HP=0;Readback.Issued.clear();C(Signature(Receiver.Capture())==Before,"Capture result cannot mutate restored history");
 FGuardKernel Invalid(701,0,{},1,FPolicy{std::numeric_limits<double>::quiet_NaN()});C(!Invalid.Restore(Saved),"invalid receiving policy rejects Restore");
 FGuardKernel OtherBirth(701,1);C(!OtherBirth.Restore(Saved),"receiver birth identity cannot be silently replaced");
 FGuardKernel OtherOwner(702);C(!OtherOwner.Restore(Saved),"receiver entity identity cannot be silently replaced");
 return All;
}
}
