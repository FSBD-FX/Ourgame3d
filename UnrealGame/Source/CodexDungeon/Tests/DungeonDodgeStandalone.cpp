#if defined(DUNGEON_DODGE_STANDALONE)
#include "../DungeonDodge.h"
#include <algorithm>
#include <cmath>
#include <iostream>
#include <limits>
#include <string>
#include <utility>

using namespace DungeonDodge;
namespace {
int Checks=0, Failures=0;
void Check(bool V, const std::string& Name) { ++Checks; if(!V) { ++Failures; std::cout << "FAIL " << Name << '\n'; } }
bool Near(double A,double B,double E=1.e-9) { return std::abs(A-B)<=E; }
bool SamePoint(FPoint A,FPoint B) { return A.X==B.X&&A.Y==B.Y; }
bool SamePositionReceipt(const FPositionReceipt& A,const FPositionReceipt& B) { return A.Id==B.Id&&A.AfterActionId==B.AfterActionId&&A.AtTime==B.AtTime&&SamePoint(A.Position,B.Position); }
bool SameRecord(const FRecord& A,const FRecord& B) {
 return A.ActionId==B.ActionId&&A.StartEventId==B.StartEventId&&A.BlockEventId==B.BlockEventId&&A.FinishEventId==B.FinishEventId&&SamePoint(A.Origin,B.Origin)&&SamePoint(A.Direction,B.Direction)&&A.Start==B.Start&&A.End==B.End&&A.ReadyAt==B.ReadyAt&&A.Travelled==B.Travelled&&A.BlockedAt==B.BlockedAt&&A.FinishedAt==B.FinishedAt&&A.Block==B.Block&&A.Finish==B.Finish&&SamePositionReceipt(A.OriginReceipt,B.OriginReceipt);
}
bool Same(const FState& A,const FState& B) {
 if(A.Version!=B.Version||A.OwnerId!=B.OwnerId||A.NextActionId!=B.NextActionId||A.NextEventId!=B.NextEventId||A.DeathEventId!=B.DeathEventId||A.NextPositionReceiptId!=B.NextPositionReceiptId||!SamePositionReceipt(A.LastPositionReceipt,B.LastPositionReceipt)||A.InitialTime!=B.InitialTime||A.Time!=B.Time||A.ReadyAt!=B.ReadyAt||A.DeadAt!=B.DeadAt||!SamePoint(A.InitialPosition,B.InitialPosition)||!SamePoint(A.Position,B.Position)||A.Phase!=B.Phase||A.Records.size()!=B.Records.size())return false;
 for(std::size_t I=0;I<A.Records.size();++I)if(!SameRecord(A.Records[I],B.Records[I]))return false;
 return true;
}
FContext Intent(double X=1,double Y=0) { FContext C;C.FreshPress=C.Grounded=C.CanStart=true; C.MoveIntent={X,Y}; return C; }
const FSweep Free=[](const FSweepRequest&){ return FSweepResult{}; };
FSweep WallAt(double X) { return [X](const FSweepRequest& Q) { FSweepResult R; if(Q.To.X>=X&&Q.To.X>Q.From.X){R.HitWall=true; R.WallFraction=std::clamp((X-Q.From.X)/(Q.To.X-Q.From.X),0.,1.);} return R; }; }
FSweep BodyAt(double X,double HalfX) { return [X,HalfX](const FSweepRequest& Q) { FSweepResult R; const double Legal=X-HalfX-Q.BodyHalfX; if(Q.To.X>=Legal&&Q.To.X>Q.From.X){R.HitBody=true;R.BodyFraction=std::clamp((Legal-Q.From.X)/(Q.To.X-Q.From.X),0.,1.);}return R; }; }
bool OneEvent(const FResult& R,EEventKind K,double T) { return R.Accepted&&R.Events.size()==1&&R.Events[0].Kind==K&&R.Events[0].AtTime==T; }
void Admission() {
 FDodgeKernel K(7); const auto Initial=K.Capture(); auto C=Intent();
 Check(!K.TryStart(0,FContext{}).Accepted&&Same(Initial,K.State()),"default context cannot grant unverified admission");
 C.FreshPress=false; Check(!K.TryStart(0,C).Accepted&&Same(Initial,K.State()),"held input atomic rejection");
 C=Intent(); C.Grounded=false; Check(!K.TryStart(0,C).Accepted&&Same(Initial,K.State()),"air atomic rejection");
 C=Intent(); C.CanStart=false; Check(!K.TryStart(0,C).Accepted&&Same(Initial,K.State()),"outer attack skill Q stun gate has no reverse cancel");
 Check(!K.TryStart(.01,Intent()).Accepted&&Same(Initial,K.State()),"future start requires clock advance first");
 Check(OneEvent(K.TryStart(0,Intent()),EEventKind::Started,0),"fresh grounded admitted start event");
 Check(K.State().Phase==EPhase::Dodging&&K.State().ReadyAt==1.2,"start commits global cooldown and action");
 const auto Active=K.Capture(); Check(!K.TryStart(0,Intent()).Accepted&&Same(Active,K.State()),"active dodge has no free restart");
 Check(K.StepTo(0).Accepted&&Same(Active,K.State()),"same clock step needs no moving sweep and emits nothing");
 Check(K.StepTo(.4,Free).Accepted&&K.State().Phase==EPhase::Idle,"completion at .4");
 Check(!K.TryStart(.4,Intent()).Accepted,"completed action cooldown remains");
 K.StepTo(std::nextafter(1.2,0.)); Check(!K.TryStart(K.State().Time,Intent()).Accepted,"cooldown left boundary rejected");
 K.StepTo(1.2); Check(K.TryStart(1.2,Intent(-1)).Accepted,"cooldown exact end allowed");
 Check(K.State().Records.size()==2&&K.State().ReadyAt==2.4,"all directions share same persistent cooldown");
}
void DirectionsAndTiming() {
 for(int X=-1;X<=1;++X)for(int Y=-1;Y<=1;++Y){
  if(!X&&!Y)continue; FDodgeKernel K(1); const double D=std::hypot(static_cast<double>(X),static_cast<double>(Y));
  K.TryStart(0,Intent(X,Y)); K.StepTo(.4,Free);
  Check(Near(K.State().Position.X,185*X/D)&&Near(K.State().Position.Y,185*Y/D)&&Near(std::hypot(K.State().Position.X,K.State().Position.Y),185),"normalized eight direction "+std::to_string(X)+","+std::to_string(Y));
 }
 FDodgeKernel Left(2); auto C=Intent(0,0); C.Facing=-1; Left.TryStart(0,C); Left.StepTo(.4,Free); Check(Left.State().Position.X==-185&&Left.State().Position.Y==0,"zero intent uses facing");
 FDodgeKernel Slow(3); Slow.TryStart(0,Intent()); Slow.StepTo(.1,Free); Check(Near(Slow.State().Position.X,46.25),"fixed speed .1s ignores armor modifiers");
 Slow.StepTo(std::nextafter(.4,0.),Free); Check(Slow.State().Phase==EPhase::Dodging,"duration left boundary still exclusive action");
 Check(OneEvent(Slow.StepTo(.4,Free),EEventKind::Completed,.4)&&Slow.State().Position.X==185,"exact completion includes final movement");
 const auto Count=Slow.State().NextEventId; Slow.StepTo(5); Check(Slow.State().Time==5&&Slow.State().Position.X==185&&Slow.State().NextEventId==Count,"long idle step no extra move or events");
 FDodgeKernel Long(5),Split(5); Long.TryStart(0,Intent(1,1)); Split.TryStart(0,Intent(1,1)); Long.StepTo(2,Free); for(double T:{.01,.06,.15,.2,.399,.4,1.,2.})Split.StepTo(T,Free);
 Check(Same(Long.State(),Split.State()),"split versus long step exact unblocked state and ids");
 FDodgeKernel Huge(6); Huge.TryStart(0,Intent(std::numeric_limits<double>::max(),std::numeric_limits<double>::max())); Huge.StepTo(.4,Free); Check(Near(std::hypot(Huge.State().Position.X,Huge.State().Position.Y),185),"finite large direction avoids normalization overflow");
}
void Invulnerability() {
 FDodgeKernel K(1); K.TryStart(0,Intent());
 Check(!K.IsDirectInvulnerableAt(std::nextafter(.06,0.)),"iframe just before .06 absent");
 Check(K.IsDirectInvulnerableAt(.06),"iframe exact .06 included");
 Check(K.IsDirectInvulnerableAt(std::nextafter(.2,0.)),"iframe just before .20 included");
 Check(!K.IsDirectInvulnerableAt(.2),"iframe exact .20 excluded");
 auto Windows=K.DirectInvulnerabilityIntervals(); Check(Windows.size()==1&&Windows[0].Start==.06&&Windows[0].EndExclusive==.2,"explicit half-open scheduled contact interval");
 K.StepTo(.4,Free); Check(K.IsDirectInvulnerableAt(.1)&&!K.IsDirectInvulnerableAt(.4),"finished dodge retains historical direct interval");
 K.StepTo(1.2); K.TryStart(1.2,Intent()); Windows=K.DirectInvulnerabilityIntervals(); Check(Windows.size()==2&&Windows[1].Start==1.2+.06&&Windows[1].EndExclusive==1.2+.2,"later action does not erase historical interval");
 FDodgeKernel Early(2); Early.TryStart(0,Intent()); Early.StepTo(.02,Free); Check(OneEvent(Early.Interrupt(.02,EFinish::PoiseBreak),EEventKind::Interrupted,.02),"resolved poise break interrupts early");
 Check(!Early.IsDirectInvulnerableAt(.06)&&Early.DirectInvulnerabilityIntervals().empty()&&Early.State().ReadyAt==1.2,"early interruption never activates scheduled iframe and preserves cooldown");
 const double Stopped=Early.State().Position.X; Early.StepTo(.4); Check(Early.State().Position.X==Stopped&&Early.State().Phase==EPhase::Idle,"interrupted remainder does not move");
 FDodgeKernel Late(3); Late.TryStart(0,Intent()); Late.StepTo(.2,Free); Check(Late.Interrupt(.2,EFinish::PoiseBreak).Accepted&&Late.IsDirectInvulnerableAt(.1)&&!Late.IsDirectInvulnerableAt(.2),"tail interruption preserves historical protected part");
 FDodgeKernel Protected(4); Protected.TryStart(0,Intent()); Protected.StepTo(.06,Free); const auto Before=Protected.Capture(); Check(!Protected.Interrupt(.06,EFinish::PoiseBreak).Accepted&&Same(Before,Protected.State()),"protected direct contact cannot create poise interrupt");
 FDodgeKernel Death(5); Death.TryStart(0,Intent()); Death.StepTo(.1,Free); const auto Died=Death.Interrupt(.1,EFinish::Death); Check(Died.Accepted&&Died.Events.size()==2&&Died.Events[0].Kind==EEventKind::Interrupted&&Died.Events[1].Kind==EEventKind::Died,"death cuts active action and emits one death fact");
 Check(Death.IsDirectInvulnerableAt(std::nextafter(.1,0.))&&!Death.IsDirectInvulnerableAt(.1)&&Death.State().ReadyAt==1.2,"death clips remaining interval at exact time without refund");
 Death.StepTo(2); Check(!Death.TryStart(2,Intent()).Accepted&&!Death.Interrupt(2,EFinish::Death).Accepted&&Death.State().Position.X==46.25,"dead clock progresses without restart or duplicate death");
 FDodgeKernel IdleDeath(6); Check(OneEvent(IdleDeath.Interrupt(0,EFinish::Death),EEventKind::Died,0)&&IdleDeath.State().Phase==EPhase::Dead,"idle death supported without fake dodge");
 FDodgeKernel AfterDodge(7);AfterDodge.TryStart(0,Intent());AfterDodge.StepTo(.4,Free);const auto AfterDeath=AfterDodge.Interrupt(.4,EFinish::Death);Check(OneEvent(AfterDeath,EEventKind::Died,.4)&&AfterDeath.Events[0].ActionId==0,"idle death does not attribute itself to completed dodge");
 Check(!K.IsDirectInvulnerableAt(std::numeric_limits<double>::quiet_NaN())&&!K.IsDirectInvulnerableAt(-1),"invalid contact times never protected");
}
void Collision() {
 FDodgeKernel Body(1); Body.TryStart(0,Intent()); const auto R=Body.StepTo(.4,BodyAt(100,24));
 Check(R.Accepted&&Near(Body.State().Position.X,58)&&Body.State().Records.size()==1&&Body.State().Records[0].Block==EBlock::Body,"live body 100 minus 18 plus24 leaves58cm");
 Check(R.Events.size()==2&&R.Events[0].Kind==EEventKind::Blocked&&Near(R.Events[0].AtTime,58/462.5)&&R.Events[1].Kind==EEventKind::Completed&&R.Events[1].AtTime==.4,"body stop contact time differs from promised completion");
 Check(Body.State().ReadyAt==1.2&&Body.IsDirectInvulnerableAt(.15),"blocked retains cooldown and iframe");
 FDodgeKernel Wall(2); Wall.TryStart(0,Intent()); Wall.StepTo(.01,WallAt(0)); Check(Wall.State().Position.X==0&&Wall.State().Phase==EPhase::Dodging&&Wall.State().ReadyAt==1.2,"zero fraction wall keeps action and cooldown");
 Check(Wall.StepTo(.4).Accepted&&Wall.State().Phase==EPhase::Idle&&Wall.IsDirectInvulnerableAt(.06),"already blocked can finish without new sweep and still protects");
 FDodgeKernel First(3); First.TryStart(0,Intent()); First.StepTo(.4,[](const FSweepRequest&){FSweepResult H;H.HitWall=H.HitBody=true;H.WallFraction=.7;H.BodyFraction=.3;return H;}); Check(Near(First.State().Position.X,55.5)&&!First.State().Records.empty()&&First.State().Records[0].Block==EBlock::Body,"earliest body versus wall fraction");
 FDodgeKernel Tie(4); Tie.TryStart(0,Intent()); Tie.StepTo(.4,[](const FSweepRequest&){FSweepResult H;H.HitWall=H.HitBody=true;H.WallFraction=H.BodyFraction=.5;return H;}); Check(!Tie.State().Records.empty()&&Tie.State().Records[0].Block==EBlock::Wall,"equal fractions stable wall precedence");
 FDodgeKernel End(5); End.TryStart(0,Intent()); End.StepTo(.4,WallAt(185)); Check(End.State().Position.X==185&&!End.State().Records.empty()&&End.State().Records[0].Block==EBlock::Wall&&End.State().Records[0].BlockedAt==.4,"endpoint collision reported without shortening duration");
 FDodgeKernel Long(6),Split(6); Long.TryStart(0,Intent());Split.TryStart(0,Intent());Long.StepTo(3,BodyAt(100,24));for(double T:{.02,.06,.1,.15,.2,.4,3.})Split.StepTo(T,BodyAt(100,24));
 Check(Near(Long.State().Position.X,Split.State().Position.X)&&Long.State().Phase==Split.State().Phase&&Long.State().ReadyAt==Split.State().ReadyAt&&Long.State().NextEventId==Split.State().NextEventId&&!Long.State().Records.empty()&&!Split.State().Records.empty()&&Near(Long.State().Records[0].BlockedAt,Split.State().Records[0].BlockedAt),"blocked split and long semantic state event consistency");
}
void AtomicInvalidInput() {
 const double NaN=std::numeric_limits<double>::quiet_NaN(), Inf=std::numeric_limits<double>::infinity(); FDodgeKernel K(1); const auto Initial=K.Capture();
 for(double T:{NaN,Inf,-1.})Check(!K.TryStart(T,Intent()).Accepted&&Same(Initial,K.State()),"invalid start time atomic");
 for(auto P:{FPoint{NaN,0},FPoint{0,Inf}}){auto C=Intent();C.MoveIntent=P;Check(!K.TryStart(0,C).Accepted&&Same(Initial,K.State()),"invalid direction atomic");}
 auto C=Intent(); C.Facing=0; Check(!K.TryStart(0,C).Accepted&&Same(Initial,K.State()),"invalid facing atomic");
 K.TryStart(0,Intent()); K.StepTo(.03,Free); const auto Before=K.Capture();
 for(double T:{NaN,Inf,-1.,.02})Check(!K.StepTo(T,Free).Accepted&&Same(Before,K.State()),"invalid or reversed step atomic");
 Check(!K.StepTo(.4).Accepted&&Same(Before,K.State()),"missing moving sweep atomic");
 for(int N=0;N<8;++N){const FSweep Bad=[N,NaN,Inf](const FSweepRequest&){FSweepResult H;switch(N){case 0:H.Accepted=false;break;case 1:H.HitWall=true;H.WallFraction=NaN;break;case 2:H.HitBody=true;H.BodyFraction=Inf;break;case 3:H.HitWall=true;H.WallFraction=-.1;break;case 4:H.HitBody=true;H.BodyFraction=1.1;break;case 5:H.WallFraction=.2;break;case 6:H.HitWall=true;H.WallFraction=.3;H.BodyFraction=NaN;break;default:H.HitBody=true;H.BodyFraction=.2;H.WallFraction=-1;break;}return H;}; const auto R=K.StepTo(2,Bad);Check(!R.Accepted&&R.Events.empty()&&Same(Before,K.State()),"invalid sweep result atomic "+std::to_string(N));}
 const FSweep Throws=[](const FSweepRequest&)->FSweepResult{throw 7;}; Check(!K.StepTo(.4,Throws).Accepted&&Same(Before,K.State()),"throwing read-only sweep rejected atomic");
 Check(!K.Interrupt(.02,EFinish::PoiseBreak).Accepted&&!K.Interrupt(.03,EFinish::Completed).Accepted&&Same(Before,K.State()),"interrupt reversed time or forged completion atomic");
 FDodgeKernel InvalidOwner(0),InvalidTime(2,NaN); Check(!InvalidOwner.TryStart(0,Intent()).Accepted&&!InvalidTime.StepTo(0,Free).Accepted,"invalid construction cannot mutate");
}
void Restore() {
 FDodgeKernel K(8,2,{5,-3}); Check(K.Restore(K.Capture()),"virgin snapshot roundtrip"); K.TryStart(2,Intent(1,1)); K.StepTo(2.1,Free); const auto Snapshot=K.Capture();
 FDodgeKernel Restored(8,2,{5,-3}); Check(Restored.Restore(Snapshot)&&Same(Restored.State(),K.State()),"active state full roundtrip");
 if(Snapshot.Records.empty()){Check(false,"snapshot requires accepted dodge record before corruption cases");return;}
 const auto A=K.StepTo(2.4,Free), B=Restored.StepTo(2.4,Free); Check(Same(K.State(),Restored.State())&&A.Events.size()==B.Events.size()&&A.Events.size()==1&&A.Events[0].EventId==B.Events[0].EventId,"resume does not replay start or alter completion ids");
 const auto Good=Snapshot; const auto Stable=Restored.Capture(); auto Reject=[&](FState Bad,const std::string& Name){Check(!Restored.Restore(Bad)&&Same(Stable,Restored.State()),"restore atomic "+Name);};
 auto V=Good;V.Version=99;Reject(V,"version"); V=Good;V.OwnerId=9;Reject(V,"owner");V=Good;V.InitialTime=0;Reject(V,"initial clock");V=Good;V.InitialPosition.X=9;Reject(V,"initial position");
 V=Good;V.Time=std::numeric_limits<double>::quiet_NaN();Reject(V,"nan time");V=Good;V.Time=1;Reject(V,"before initial time");V=Good;V.ReadyAt=0;Reject(V,"forged cooldown");V=Good;V.Position.Y+=1;Reject(V,"unearned position");
 V=Good;V.Phase=EPhase::Idle;Reject(V,"active flag");V=Good;V.Phase=static_cast<EPhase>(99);Reject(V,"invalid phase");V=Good;V.NextActionId=1;Reject(V,"action cursor");V=Good;V.NextEventId=50;Reject(V,"event cursor");
 V=Good;V.Records.clear();Reject(V,"missing history");V=Good;V.Records[0].Direction={2,0};Reject(V,"nonunit direction");V=Good;V.Records[0].End+=.01;Reject(V,"duration");V=Good;V.Records[0].ReadyAt+=.01;Reject(V,"action cooldown");
 V=Good;V.Records[0].Travelled+=1;Reject(V,"distance");V=Good;V.Records[0].StartEventId=2;Reject(V,"start receipt");V=Good;V.Records[0].FinishedAt=2.02;Reject(V,"missing finish reason");V=Good;V.Records[0].Block=EBlock::Body;Reject(V,"missing block time receipt");
 V=Good;V.Records[0].Finish=static_cast<EFinish>(99);Reject(V,"invalid finish enum");V=Good;V.Records[0].Origin.X+=1;Reject(V,"origin continuity");V=Good;V.DeadAt=2.1;Reject(V,"idle death contradiction");V=Good;V.DeathEventId=1;Reject(V,"unearned death receipt");
 FDodgeKernel Blocked(10);Blocked.TryStart(0,Intent());Blocked.StepTo(.2,BodyAt(100,24));FDodgeKernel BlockCopy(10);Check(BlockCopy.Restore(Blocked.Capture()),"blocked active restore"); Blocked.StepTo(.4);BlockCopy.StepTo(.4);Check(Same(Blocked.State(),BlockCopy.State()),"blocked resume same remaining commitment");
 FDodgeKernel Interrupted(11);Interrupted.TryStart(0,Intent());Interrupted.StepTo(.02,Free);Interrupted.Interrupt(.02,EFinish::PoiseBreak);FDodgeKernel IntCopy(11);Check(IntCopy.Restore(Interrupted.Capture())&&!IntCopy.IsDirectInvulnerableAt(.1)&&IntCopy.State().ReadyAt==1.2,"interrupted restore no future iframe and no refund");
 FDodgeKernel Dead(12);Dead.TryStart(0,Intent());Dead.StepTo(.1,Free);Dead.Interrupt(.1,EFinish::Death);FDodgeKernel DeadCopy(12);Check(DeadCopy.Restore(Dead.Capture())&&!DeadCopy.TryStart(.1,Intent()).Accepted,"dead restore retains terminal state");
 auto Mal=Dead.Capture();Mal.Records[0].FinishedAt=.15;const auto DeadGood=DeadCopy.Capture();Check(!DeadCopy.Restore(Mal)&&Same(DeadGood,DeadCopy.State()),"death record and global death must match");
 FDodgeKernel Multi(13);Multi.TryStart(0,Intent());Multi.StepTo(1.2,Free);Multi.TryStart(1.2,Intent(-1));Multi.StepTo(1.6,Free);FDodgeKernel MultiCopy(13);Check(MultiCopy.Restore(Multi.Capture())&&Same(MultiCopy.State(),Multi.State()),"multi action complete restore");
 auto Dup=Multi.Capture();if(Dup.Records.size()>1)Dup.Records[1].ActionId=1;Check(!MultiCopy.Restore(Dup),"duplicate action rejected");
 FDodgeKernel IdleDead(14);IdleDead.Interrupt(0,EFinish::Death);IdleDead.StepTo(1);FDodgeKernel IdleDeadCopy(14);Check(IdleDeadCopy.Restore(IdleDead.Capture()),"dead without action snapshot restore");
}
void IdlePositionHandoff() {
 FDodgeKernel K(50);const auto Initial=K.Capture();
 Check(K.CommitResolvedIdlePosition(0,{10,20},1),"idle resolved actor position accepted");
 Check(SamePoint(K.State().Position,{10,20})&&K.State().Time==0&&K.State().ReadyAt==0&&K.State().Phase==EPhase::Idle&&K.State().NextActionId==Initial.NextActionId&&K.State().NextEventId==Initial.NextEventId,"handoff changes only position receipt not clock cooldown phase events");
 Check(K.State().NextPositionReceiptId==2&&K.State().LastPositionReceipt.Id==1&&K.State().LastPositionReceipt.AtTime==0&&K.State().LastPositionReceipt.AfterActionId==0,"handoff persistent cursor and factual timestamp");
 Check(K.TryStart(0,Intent()).Accepted,"dodge begins after resolved walk handoff");K.StepTo(.4,Free);
 Check(SamePoint(K.State().Position,{195,20})&&!K.State().Records.empty()&&SamePoint(K.State().Records[0].Origin,{10,20})&&K.State().Records[0].OriginReceipt.Id==1,"dodge uses actual handed off origin and freezes receipt");
 K.StepTo(.5);const auto Before=K.Capture();Check(K.CommitResolvedIdlePosition(.5,{40,30},2),"resolved landing knockback position accepted during cooldown");
 Check(K.State().ReadyAt==Before.ReadyAt&&K.IsDirectInvulnerableAt(.1)&&K.State().NextActionId==Before.NextActionId&&K.State().NextEventId==Before.NextEventId&&K.State().DeadAt==Before.DeadAt&&K.State().Records.size()==Before.Records.size(),"idle handoff preserves cooldown historical iframe events death and actions");
 Check(!K.TryStart(.5,Intent()).Accepted,"handoff cannot bypass existing cooldown");K.StepTo(1.2);Check(K.TryStart(1.2,Intent()).Accepted,"same long lived kernel accepts after old cooldown");K.StepTo(1.6,Free);
 Check(SamePoint(K.State().Position,{225,30})&&K.State().ReadyAt==2.4&&K.State().Records.size()==2&&K.State().Records[1].OriginReceipt.Id==2&&K.State().Records[1].OriginReceipt.AfterActionId==1,"next dodge starts from landed position with original shared cooldown");
 FDodgeKernel Copy(50);Check(Copy.Restore(K.Capture())&&Same(Copy.State(),K.State()),"position history multi dodge snapshot roundtrip");
 const auto Stable=Copy.Capture();Check(!Copy.CommitResolvedIdlePosition(1.6,{99,99},2)&&Same(Stable,Copy.State()),"restored receipt dedup rejects duplicate atomically");
 Check(Copy.CommitResolvedIdlePosition(1.6,{225,30},20)&&Copy.State().NextPositionReceiptId==21,"strictly increasing receipt permits reserved ID gaps and same position");
 const auto Gap=Copy.Capture();Check(!Copy.CommitResolvedIdlePosition(1.6,{5,6},19)&&Same(Gap,Copy.State()),"lower unused but old receipt rejected without consuming ID");
 FDodgeKernel Many(51);bool All=true;for(std::uint64_t Id=1;Id<=100;++Id)All=Many.CommitResolvedIdlePosition(0,{static_cast<double>(Id),-3},Id)&&All;
 Check(All&&Many.State().Records.empty()&&Many.State().LastPositionReceipt.Id==100&&Many.State().NextPositionReceiptId==101,"many idle commits retain one latest receipt not per tick vector");
 FDodgeKernel ManyCopy(51);Check(ManyCopy.Restore(Many.Capture())&&ManyCopy.State().Position.X==100&&!ManyCopy.CommitResolvedIdlePosition(0,{0,0},99),"compressed idle receipt survives restore with persistent dedup");
}
void InvalidHandoffAndRestore() {
 const double NaN=std::numeric_limits<double>::quiet_NaN(),Inf=std::numeric_limits<double>::infinity();FDodgeKernel K(60);const auto Initial=K.Capture();
 for(double T:{NaN,Inf,-1.,.01})Check(!K.CommitResolvedIdlePosition(T,{1,2},7)&&Same(Initial,K.State()),"invalid handoff time atomic");
 for(auto P:{FPoint{NaN,0},FPoint{0,Inf},FPoint{-Inf,1}})Check(!K.CommitResolvedIdlePosition(0,P,7)&&Same(Initial,K.State()),"invalid handoff coordinate atomic");
 Check(!K.CommitResolvedIdlePosition(0,{1,2},0)&&!K.CommitResolvedIdlePosition(0,{1,2},std::numeric_limits<std::uint64_t>::max())&&Same(Initial,K.State()),"zero and overflow receipt atomic");
 Check(K.CommitResolvedIdlePosition(0,{1,2},7)&&K.State().NextPositionReceiptId==8,"invalid requests did not consume fresh receipt ID");
 K.TryStart(0,Intent());K.StepTo(.03,Free);const auto Active=K.Capture();Check(!K.CommitResolvedIdlePosition(.03,{50,60},9)&&Same(Active,K.State()),"active dodge rejects external position handoff atomically");K.StepTo(.4,Free);
 Check(K.CommitResolvedIdlePosition(.4,{50,60},9)&&K.State().ReadyAt==1.2,"rejected active receipt remains available after completion with no CD refund");
 const auto Good=K.Capture();FDodgeKernel Copy(60);Check(Copy.Restore(Good)&&Same(Copy.State(),Good),"idle position after completed dodge restore");
 auto Reject=[&](FState Bad,const std::string& Name){const auto Before=Copy.Capture();Check(!Copy.Restore(Bad)&&Same(Before,Copy.State()),"handoff restore rejects "+Name);};
 auto V=Good;V.NextPositionReceiptId=9;Reject(V,"cursor contradictory to last receipt");V=Good;V.LastPositionReceipt.Id=7;Reject(V,"duplicate historical ID");V=Good;V.LastPositionReceipt.Id=0;Reject(V,"missing last receipt");
 V=Good;V.Version=1;Reject(V,"legacy schema lacks persistent handoff receipts");
 V=Good;V.LastPositionReceipt.AtTime=.5;Reject(V,"future handoff");V=Good;V.LastPositionReceipt.AtTime=.3;Reject(V,"handoff during old active action");V=Good;V.LastPositionReceipt.AtTime=NaN;Reject(V,"nan receipt time");
 V=Good;V.LastPositionReceipt.AfterActionId=0;Reject(V,"forged action epoch");V=Good;V.LastPositionReceipt.Position.X+=1;Reject(V,"receipt position differs from authority");V=Good;V.Position.Y+=1;Reject(V,"authority differs from position receipt");
 V=Good;V.Records[0].OriginReceipt.Id=9;Reject(V,"origin and current ID order");V=Good;V.Records[0].OriginReceipt.AfterActionId=1;Reject(V,"origin receipt applied after self");V=Good;V.Records[0].OriginReceipt.AtTime=.01;Reject(V,"origin receipt after start");
 V=Good;V.Records[0].OriginReceipt.Position.X+=1;Reject(V,"origin receipt coordinate");V=Good;V.Records[0].OriginReceipt.Id=0;Reject(V,"nonempty zero receipt");
 FDodgeKernel ActiveCopy(60);Check(ActiveCopy.Restore(Active),"active state with prior idle receipt restores");auto ForgedActive=Active;ForgedActive.LastPositionReceipt.AfterActionId=1;ForgedActive.LastPositionReceipt.AtTime=.03;ForgedActive.LastPositionReceipt.Position=Active.Position;ForgedActive.LastPositionReceipt.Id=9;ForgedActive.NextPositionReceiptId=10;const auto ActiveStable=ActiveCopy.Capture();Check(!ActiveCopy.Restore(ForgedActive)&&Same(ActiveStable,ActiveCopy.State()),"restore cannot smuggle a handoff inside current dodge");
 K.Interrupt(.4,EFinish::Death);const auto Dead=K.Capture();Check(!K.CommitResolvedIdlePosition(.4,{0,0},10)&&Same(Dead,K.State()),"dead character rejects position commit and cannot resurrect");
 FDodgeKernel DeadCopy(60);Check(DeadCopy.Restore(Dead)&&!DeadCopy.CommitResolvedIdlePosition(.4,{0,0},10),"dead handoff state persists on restore");
 auto Late=Dead;Late.Time=.5;Late.LastPositionReceipt.AtTime=.5;const auto DeadStable=DeadCopy.Capture();Check(!DeadCopy.Restore(Late)&&Same(DeadStable,DeadCopy.State()),"restore rejects handoff after recorded death");
 FDodgeKernel Interrupted(61);Interrupted.TryStart(0,Intent());Interrupted.StepTo(.02,Free);Interrupted.Interrupt(.02,EFinish::PoiseBreak);Check(Interrupted.CommitResolvedIdlePosition(.02,{-25,5},1)&&Interrupted.State().ReadyAt==1.2&&!Interrupted.IsDirectInvulnerableAt(.1),"resolved knockback after real break preserves clipped iframe and CD");
 FDodgeKernel InterruptedCopy(61);Check(InterruptedCopy.Restore(Interrupted.Capture()),"post poise idle position restores");
 FDodgeKernel Invalid(0);Check(!Invalid.CommitResolvedIdlePosition(0,{1,2},1),"invalid owner cannot commit position");
}
}
int main() { Admission(); DirectionsAndTiming(); Invulnerability(); Collision(); AtomicInvalidInput(); Restore(); IdlePositionHandoff(); InvalidHandoffAndRestore(); std::cout << "CHECKS=" << Checks << " FAILURES=" << Failures << '\n'; return Failures?1:0; }
#endif
