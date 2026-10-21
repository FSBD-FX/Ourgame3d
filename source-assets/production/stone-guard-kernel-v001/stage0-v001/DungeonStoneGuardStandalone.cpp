#include "DungeonStoneGuard.h"
#include <cmath>
#include <iomanip>
#include <iostream>
#include <limits>
#include <sstream>
#include <string>
using namespace DungeonStoneGuard;
namespace
{
int Checks=0, Failures=0;
void Check(bool Value,const char* Name)
{++Checks;if(!Value)++Failures;std::cout<<(Value?"PASS ":"FAIL ")<<Name<<'\n';}
bool Near(double A,double B){return std::abs(A-B)<1e-9;}
int Count(const FResult& R,EEventKind K){int N=0;for(const auto& E:R.Events)N+=E.Kind==K;return N;}
void Point(std::ostream& O,FPoint P){O<<P.X<<','<<P.Y<<','<<P.Z<<';';}
void Action(std::ostream& O,const FAction& A)
{
 O<<A.AttackId<<','<<int(A.Kind)<<','<<A.InProgress<<A.Locked<<A.WindowIssued<<A.Interrupted<<';'
  <<A.Start<<','<<A.LockAt<<','<<A.ActiveAt<<','<<A.ActiveEnd<<','<<A.RecoveryEnd<<','<<A.CooldownEnd<<','
  <<A.InterruptedAt<<','<<A.CompletedAt<<','<<A.Damage<<','<<A.Stagger<<','<<A.Facing<<';';
 Point(O,A.Origin);Point(O,A.LockedCenter);Point(O,A.Target);
}
// Independent full-state oracle for rejected-call atomicity, including all receipts/events.
std::string Signature(const FState& S)
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
FWorldInput World(double X=100,double Y=0,double Z=0)
{FWorldInput W;W.HasTarget=true;W.Target={X,Y,Z};W.Sweep=[](const FSweepRequest&){return FSweepResult{};};return W;}
bool Awake(FGuardKernel& K,FWorldInput W=World())
{
 auto R=K.StepTo(K.State().Time,W);Check(R.Accepted&&Count(R,EEventKind::WakeStarted)==1,"real proximity starts one full warning");
 if(!R.Accepted)return false;
 R=K.StepTo(K.State().WakeEnd,W);Check(R.Accepted&&K.State().Phase==EPhase::Idle,"real warning reaches awake idle");return R.Accepted&&K.State().Phase==EPhase::Idle;
}
bool Start(FGuardKernel& K,EAttack A,FWorldInput W)
{const auto R=K.TryStartAttack(A,W);Check(R.Accepted&&Count(R,EEventKind::AttackStarted)==1,"accepted real attack start");return R.Accepted;}
void DefinitionAndWake()
{
 std::cout<<"GROUP DefinitionAndWake\n";
 const auto D=FGuardKernel::Definition();Check(std::string(D.ContentId)=="ENM-STN-003"&&D.HP==185&&D.Armor==60&&D.Ward==15&&D.Poise==85&&D.MoveSpeed==160,"distinct stone guard balance");
 Check(D.BodyHalfX==40&&D.BodyHalfY==28&&D.HurtHalfX==40&&D.HurtHalfY==28,"large independent body and hurt extents");
 const auto A=FGuardKernel::AttackDefinition(EAttack::AxeSweep),B=FGuardKernel::AttackDefinition(EAttack::Stomp);
 Check(A.Windup==1&&A.LockDelay==.5&&A.Active==.2&&A.Recovery==1.4&&A.Cooldown==3.1&&A.Damage==24&&A.Stagger==30,"axe exact authored timing and damage");
 Check(B.Windup==.9&&B.LockDelay==.45&&B.Active==.15&&B.Recovery==1.5&&B.Cooldown==3&&B.Damage==18&&B.Stagger==25,"stomp exact authored timing and damage");
 FGuardKernel K(3);auto W=World(236);auto R=K.StepTo(0,W);Check(R.Accepted&&K.State().Phase==EPhase::Dormant,"outside proximity remains dormant");
 W=World(235);W.LOS=false;R=K.StepTo(0,W);Check(R.Accepted&&K.State().Phase==EPhase::Dormant,"LOS is required at ellipse boundary");
 W.LOS=true;W.CanBeginWake=false;R=K.StepTo(0,W);Check(R.Accepted&&K.State().WakeQueued&&K.State().WakeStartedAt==-1,"shared wake slot queues without shortening warning");
 W.CanBeginWake=true;R=K.StepTo(.2,W);Check(R.Accepted&&K.State().WakeStartedAt==0&&K.State().WakeEnd==1,"queued warning starts at authoritative cursor");
 R=K.StepTo(.999,W);Check(R.Accepted&&!K.State().Awakened&&!K.TryStartAttack(EAttack::AxeSweep,W).Accepted,"cannot attack before complete warning");
 R=K.StepTo(1,W);Check(R.Accepted&&Count(R,EEventKind::WakeCompleted)==1&&K.State().HP==185,"wake completion no healing no new identity");
 Check(K.StepTo(1,W).Events.empty(),"equal clock never repeats wake events");
 FGuardKernel F(4);auto Far=World(900);Check(F.BeginCombat()&&!F.BeginCombat(),"explicit combat fallback arms once");
 R=F.StepTo(12,Far);Check(R.Accepted&&F.State().WakeStartedAt==12&&F.State().WakeEnd==13,"12 second fallback retains entire warning");
 FGuardKernel C(5);Check(C.NotifyOtherAcceptedEnemiesCleared()&&!C.NotifyOtherAcceptedEnemiesCleared(),"other-enemies-cleared queues once");R=C.StepTo(1,Far);Check(R.Accepted&&C.State().Awakened,"cleared fallback completes its actual warning");
 FGuardKernel H(6);R=H.ApplyResolvedHit(1,0,0,Far);Check(R.Accepted&&!H.State().WakeQueued&&H.State().WakeStartedAt==-1,"zero HP loss does not invent damage wake");
 R=H.ApplyResolvedHit(2,10,0,Far);Check(R.Accepted&&H.State().HP==175&&H.State().WakeEnd==1,"positive resolved HP loss wakes without double armor mitigation");
}
void AxeTimelineAndFacing()
{
 std::cout<<"GROUP AxeTimelineAndFacing\n";FGuardKernel K(20);auto W=World(170);if(!Awake(K,W)||!Start(K,EAttack::AxeSweep,W))return;
 Check(K.State().Action.Start==1&&K.State().Action.LockAt==1.5&&K.State().Action.ActiveAt==2&&Near(K.State().Action.ActiveEnd,2.2)&&Near(K.State().Action.RecoveryEnd,3.6)&&Near(K.State().AxeReadyAt,4.1),"one authoritative axe schedule");
 W.Target={-170,0,0};auto R=K.StepTo(1.5,W);Check(R.Accepted&&Count(R,EEventKind::AimLocked)==1&&K.State().Action.Facing==-1,"prelock target switch locks left");
 W.Target={170,0,0};R=K.StepTo(2,W);Check(R.Accepted&&Count(R,EEventKind::ActiveWindow)==1&&K.State().Windows.size()==1&&K.State().Action.Facing==-1,"postlock target never tracks right");
 Check(K.State().Position.X==0&&K.State().Position.Y==0,"windup and active stand still");
 const auto Original=K.State().Windows.front();R=K.StepTo(3.6,W);Check(R.Accepted&&Count(R,EEventKind::RecoveryStarted)==1&&Count(R,EEventKind::AttackCompleted)==1&&K.State().Phase==EPhase::Idle,"large step emits exact phase boundaries once");
 Check(K.State().Windows.front().Start==Original.Start&&K.State().Windows.front().End==Original.End&&K.State().Windows.front().Facing==Original.Facing,"issued damage window survives completion unchanged");
 Check(K.StepTo(3.6,W).Events.empty(),"equal time never reissues window or completion");
 Check(!K.TryStartAttack(EAttack::Stomp,World(50)).Accepted,"cross-kind minimum idle gap cannot bypass recovery");
 K.StepTo(3.9,World(50));Check(K.TryStartAttack(EAttack::Stomp,World(50)).Accepted,"other attack only after full recovery plus idle gap");
}
void ExactGeometryAndOnceHits()
{
 std::cout<<"GROUP ExactGeometryAndOnceHits\n";
 for(int Face:{-1,1})
 {
  FGuardKernel K(Face<0?30:31);auto W=World(Face*170.);if(!Awake(K,W)||!Start(K,EAttack::AxeSweep,W))continue;K.StepTo(2,W);
  auto T=FTarget{100,{Face*180.,65,65}};auto R=K.TryHit(T);Check(R.Accepted&&Count(R,EEventKind::Hit)==1&&R.Events.front().Amount==24,"mirrored rectangle boundary and actual height inclusive");
  Check(!K.TryHit(T).Accepted,"one target once per attack not once per frame");
  T.EntityId=101;T.Position={Face*180.0001,0,0};Check(!K.TryHit(T).Accepted,"no rectangle range inflation");
  T.Position={-Face*1.,0,0};Check(!K.TryHit(T).Accepted,"locked axe cannot damage its rear");
  T.Position={Face*100.,65.0001,0};Check(!K.TryHit(T).Accepted,"depth center strict no hurtbox inflation");
  T.Position={Face*100.,0,65.0001};Check(!K.TryHit(T).Accepted,"jump height above low axe misses");
  T.Position={Face*100.,0,0};T.LOS=false;Check(!K.TryHit(T).Accepted,"wall LOS blocks legal geometry");T.LOS=true;T.Invulnerable=true;Check(!K.TryHit(T).Accepted,"invulnerability blocks without consuming hit");T.Invulnerable=false;T.Hostile=false;Check(!K.TryHit(T).Accepted,"allied body never friendly damage");T.Hostile=true;Check(K.TryHit(T).Accepted,"failed admission did not consume receipt");
  K.StepTo(K.State().Action.ActiveEnd,W);T.EntityId=102;Check(!K.TryHit(T).Accepted&&K.CounterWindowOpen(),"active end exclusive recovery counterwindow");
 }
 FGuardKernel S(32);auto W=World(0,80);if(!Awake(S,W)||!Start(S,EAttack::Stomp,W))return;auto R=S.StepTo(1.45,W);Check(R.Accepted&&S.State().Action.LockedCenter.X==0&&S.State().Action.LockedCenter.Y==0,"stomp locks own center not target");
 R=S.StepTo(1.9,World(600));Check(R.Accepted&&Count(R,EEventKind::ActiveWindow)==1,"single stomp emission despite lost target");
 FTarget T{110,{160,0,65}};Check(S.TryHit(T).Accepted,"ellipse X boundary height65 admitted");T.EntityId=111;T.Position={0,90,0};Check(S.TryHit(T).Accepted,"ellipse side boundary admitted");T.EntityId=112;T.Position={160,90,0};Check(!S.TryHit(T).Accepted,"ellipse is not its bounding rectangle");T.Position={0,0,66};Check(!S.TryHit(T).Accepted,"real jump above shock height avoids stomp");T.Position={0,0,0};Check(S.TryHit(T).Accepted&&!S.TryHit(T).Accepted,"one stomp pulse receipt per target");
 S.StepTo(S.State().Action.ActiveEnd,W);Check(!S.TryHit({113,{0,0,0}}).Accepted&&S.CounterWindowOpen(),"no residual every-frame damage after stomp");
}
void InterruptionAndOverlap()
{
 std::cout<<"GROUP InterruptionAndOverlap\n";FGuardKernel K(40);auto W=World(150);if(!Awake(K,W)||!Start(K,EAttack::AxeSweep,W))return;
 auto R=K.StepTo(1.2,W,{{1,1.2,10,20}});Check(R.Accepted&&K.State().Phase==EPhase::Windup&&K.State().HP==175,"ordinary HP loss and subthreshold poise do not cancel");
 R=K.StepTo(2,W,{{2,2,1,65}});Check(R.Accepted&&K.State().Phase==EPhase::Stunned&&Count(R,EEventKind::PoiseBroken)==1&&Count(R,EEventKind::ActiveWindow)==0,"same-time poise break precedes active issue");
 Check(Near(K.State().AxeReadyAt,4.1)&&Near(K.State().OccupiedUntil,3.6)&&Near(K.State().StunUntil,2.4)&&K.State().ProtectionUntil==3,"cancel preserves cooldown and complete action occupancy");
 R=K.StepTo(2.2,W,{{3,2.2,2,1000}});Check(R.Accepted&&Near(K.State().StunUntil,2.4)&&K.State().PoiseAccum==0,"protection refuses repeated stun extension");
 K.StepTo(2.4,W);Check(K.State().Phase==EPhase::Recovery&&!K.TryStartAttack(EAttack::Stomp,World(30)).Accepted,"stun end retains original recovery commitment");K.StepTo(3.6,W);Check(K.State().Phase==EPhase::Idle,"interrupted action eventually completes once");
 FGuardKernel A(41);if(!Awake(A,W)||!Start(A,EAttack::AxeSweep,W))return;A.StepTo(2,W);const auto Window=A.State().Windows.front();R=A.StepTo(2.1,W,{{1,2.1,0,85}});
 Check(R.Accepted&&A.State().Closures.size()==1&&A.State().Closures.front().AtTime==2.1,"active cancellation uses independent closing receipt");Check(A.State().Windows.front().Start==Window.Start&&A.State().Windows.front().End==Window.End&&A.State().Windows.front().Damage==24,"cancellation cannot rewrite issued window");Check(!A.TryHit({120,{100,0,0}}).Accepted,"closed active window no postcancel hit");
 FGuardKernel D(42);auto Far=World(900);R=D.StepTo(.2,Far,{{1,.2,1,85}});Check(R.Accepted&&D.State().WakeStartedAt==.2&&D.State().WakeEnd==1.2&&Near(D.State().StunUntil,.6),"damage wake and poise clocks coexist");D.StepTo(.6,Far);Check(D.State().Phase==EPhase::Waking&&!D.State().Awakened,"stun cannot erase uncompleted warning");D.StepTo(1.2,Far);Check(D.State().Awakened&&D.State().HP==184,"warning cannot heal damage or replace entity");
 FGuardKernel P(43);P.ApplyResolvedHit(1,0,40,Far);P.StepTo(1,Far);Check(P.State().PoiseAccum==40,"decay waits full one second");P.StepTo(2,Far);Check(P.State().PoiseAccum==20,"poise decays20 per second after delay");
}
void LocomotionAndAtomicRejects()
{
 std::cout<<"GROUP LocomotionAndAtomicRejects\n";FGuardKernel K(50);if(!Awake(K))return;auto W=World(600,100);int Sweeps=0;W.Sweep=[&](const FSweepRequest& Q){++Sweeps;Check(Q.BodyHalfX==40&&Q.BodyHalfY==28&&Q.From.Z==Q.To.Z,"large grounded read-only idle sweep");return FSweepResult{};};
 auto R=K.StepTo(1.5,W);Check(R.Accepted&&K.State().Position.Y==80&&K.State().Position.X==0&&Sweeps==1,"slow160 movement aligns Y no teleport");
 auto Before=Signature(K.Capture());auto Bad=W;Bad.Sweep=[](const FSweepRequest&){return FSweepResult{true,1.1,EStop::Wall};};R=K.StepTo(2,Bad);Check(!R.Accepted&&Signature(K.Capture())==Before,"invalid sweep rolls back time position and all events");
 Bad.Sweep={};R=K.StepTo(2,Bad);Check(!R.Accepted&&Signature(K.Capture())==Before,"missing query does not assume empty world");
 R=K.StepTo(1,W);Check(!R.Accepted&&Signature(K.Capture())==Before,"rewound clock rejects atomically");R=K.StepTo(std::numeric_limits<double>::quiet_NaN(),W);Check(!R.Accepted&&Signature(K.Capture())==Before,"NaN clock rejects atomically");Bad=W;Bad.Target.X=std::numeric_limits<double>::infinity();Check(!K.StepTo(2,Bad).Accepted&&Signature(K.Capture())==Before,"nonfinite world rejects atomically");
 Check(!K.StepTo(2,W,{{1,1.8,1,0},{1,1.9,1,0}}).Accepted&&Signature(K.Capture())==Before,"duplicate incoming receipt rolls back whole batch");Check(!K.StepTo(2,W,{{1,1.9,1,0},{2,1.8,1,0}}).Accepted&&Signature(K.Capture())==Before,"unordered hit time rejects whole batch");
 W.Sweep=[](const FSweepRequest&){return FSweepResult{true,.5,EStop::Wall};};R=K.StepTo(2,W);Check(R.Accepted&&K.State().Position.Y==90&&K.State().Time==2,"blocked idle movement clamps no invented contact damage");Check(Count(R,EEventKind::Hit)==0,"walking body contact has no damage event");
 auto Far=World(900);R=K.StepTo(3,Far);Check(R.Accepted&&K.State().HP==185&&K.State().Awakened,"losing sight never leash heals or sleeps");
 FGuardKernel N(0);Check(!N.IsValid()&&!N.StepTo(0,World()).Accepted,"zero entity cannot operate");FGuardKernel Q(51,-1);Check(!Q.IsValid()&&!Q.StepTo(0,World()).Accepted,"negative initial time cannot operate");
}
void DeathRewardResetAndEquivalence()
{
 std::cout<<"GROUP DeathRewardResetAndEquivalence\n";FGuardKernel K(60);auto W=World(150);if(!Awake(K,W)||!Start(K,EAttack::AxeSweep,W))return;auto R=K.StepTo(2,W,{{1,2,185,100}});
 Check(R.Accepted&&K.State().Phase==EPhase::Dead&&Count(R,EEventKind::Died)==1&&Count(R,EEventKind::ActiveWindow)==0,"death wins exact active boundary and emits once");Check(!K.GroundBodyEnabled()&&!K.CounterWindowOpen(),"corpse stops blocking and countering");R=K.StepTo(5,W);Check(R.Accepted&&R.Events.empty()&&!K.TryStartAttack(EAttack::AxeSweep,W).Accepted,"dead clock advances without attacks or second death");R=K.ClaimDeathReward();Check(R.Accepted&&Count(R,EEventKind::RewardClaimed)==1&&R.Events.front().Amount==0&&!K.ClaimDeathReward().Accepted,"reward eligibility consumed once without invented gold");
 auto Before=Signature(K.Capture());Check(!K.ResetForNewEntity(60,5)&&Signature(K.Capture())==Before,"same-ID reset cannot duplicate reward");Check(!K.ResetForNewEntity(61,4)&&Signature(K.Capture())==Before,"new spawn cannot rewind authoritative clock");Check(K.ResetForNewEntity(61,5,{30,40,0},-1)&&K.State().HP==185&&K.State().Phase==EPhase::Dormant&&!K.State().RewardClaimed&&K.State().Issued.empty()&&K.State().EntityId==61,"explicit new entity clears only its own state");
 FGuardKernel A(62),B(62);if(!Awake(A,W)||!Awake(B,W)||!Start(A,EAttack::AxeSweep,W)||!Start(B,EAttack::AxeSweep,W))return;
 A.StepTo(3.6,W);for(double T:{1.3,1.5,1.9,2.,2.1,2.2,2.9,3.6})B.StepTo(T,W);Check(Signature(A.Capture())==Signature(B.Capture()),"large step and partitioned phase schedule exact equivalence");
 FGuardKernel C(63);if(!Awake(C,W))return;auto Denied=W;Denied.CanStartAttack=false;Before=Signature(C.Capture());Check(!C.TryStartAttack(EAttack::AxeSweep,Denied).Accepted&&Signature(C.Capture())==Before,"denied attack slot spends no IDs cooldown or action");
 Check(C.ChooseAttack(World(50))==EAttack::Stomp&&C.ChooseAttack(World(150))==EAttack::AxeSweep&&C.ChooseAttack(World(0,80))==EAttack::Stomp,"explicit documented close/front/side choice proposal");
}
}
int main()
{
 DefinitionAndWake();AxeTimelineAndFacing();ExactGeometryAndOnceHits();InterruptionAndOverlap();LocomotionAndAtomicRejects();DeathRewardResetAndEquivalence();
 std::cout<<"SUMMARY groups=6 checks="<<Checks<<" failed="<<Failures<<'\n';return Failures?1:0;
}
