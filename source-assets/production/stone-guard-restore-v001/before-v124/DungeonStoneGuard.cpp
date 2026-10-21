#include "DungeonStoneGuard.h"
#include <algorithm>
#include <cmath>
#include <limits>

namespace DungeonStoneGuard
{
namespace
{
constexpr std::size_t MaxRecords=65536;
bool Finite(double V) { return std::isfinite(V); }
bool PointValid(FPoint P) { return Finite(P.X)&&Finite(P.Y)&&Finite(P.Z)&&P.Z>=0; }
bool WorldValid(const FWorldInput& W) { return PointValid(W.Target); }
bool AttackKind(EAttack K) { return K==EAttack::AxeSweep||K==EAttack::Stomp; }
bool Ellipse(FPoint P,FPoint C,double X,double Y)
{
    const double DX=(P.X-C.X)/X, DY=(P.Y-C.Y)/Y;
    return DX*DX+DY*DY<=1;
}
bool AxeRange(FPoint P,FPoint C) { return std::abs(P.X-C.X)<=180&&std::abs(P.Y-C.Y)<=65; }
int FacingToward(FPoint From,FPoint Target,int Previous)
{
    return Target.X==From.X?Previous:(Target.X<From.X?-1:1);
}
bool Increasing(double A,double B) { return Finite(B)&&B>A; }
bool InAttackRange(FPoint Target,FPoint Center)
{
    return AxeRange(Target,Center)||Ellipse(Target,Center,160,90);
}
enum class EAxisEntry { Unreachable, Found, Invalid };
EAxisEntry FirstAxisAttackEntry(FPoint From,FPoint Target,bool AlongY,FPoint& Entry)
{
    // On either axis, both attack cross-sections are concentric intervals.
    // Their union therefore has the greater of the two available half-reaches.
    const double Fixed=std::abs(AlongY?Target.X-From.X:Target.Y-From.Y);
    const double FixedRadius=AlongY?160.:90.;
    const double MovingRadius=AlongY?90.:160.;
    double Reach=-1;
    if(Fixed<=(AlongY?180.:65.))Reach=AlongY?65.:180.;
    if(Fixed<=FixedRadius)
    {
        const double Ratio=Fixed/FixedRadius;
        Reach=std::max(Reach,MovingRadius*std::sqrt(std::max(0.,1.-Ratio*Ratio)));
    }
    if(Reach<0)return EAxisEntry::Unreachable;
    const double Start=AlongY?From.Y:From.X, Goal=AlongY?Target.Y:Target.X;
    const double Sign=Goal<Start?-1.:1.;
    Entry=From;
    double Coordinate=Goal-Sign*Reach;
    // A rounded analytical boundary must not reverse the pursuit direction.
    if(Sign*(Coordinate-Start)<0)Coordinate=Start;
    if(AlongY)Entry.Y=Coordinate;else Entry.X=Coordinate;
    if(InAttackRange(Target,Entry))return EAxisEntry::Found;

    // Only correct analytical-boundary rounding. This searches representable
    // coordinates, not simulation substeps or a world-space epsilon. The target
    // coordinate is inside this nonempty cross-section; the boundary is outside.
    double Outside=Coordinate, Inside=Goal;
    constexpr int MaxRefinements=std::numeric_limits<double>::max_exponent
        -std::numeric_limits<double>::min_exponent+std::numeric_limits<double>::digits+4;
    for(int I=0;I<MaxRefinements;++I)
    {
        const double Mid=Outside+(Inside-Outside)*.5;
        if(Mid==Outside||Mid==Inside)
        {
            if(AlongY)Entry.Y=Inside;else Entry.X=Inside;
            return InAttackRange(Target,Entry)?EAxisEntry::Found:EAxisEntry::Invalid;
        }
        FPoint Probe=From;if(AlongY)Probe.Y=Mid;else Probe.X=Mid;
        if(InAttackRange(Target,Probe))Inside=Mid;else Outside=Mid;
    }
    return EAxisEntry::Invalid;
}
}

FGuardKernel::FGuardKernel(std::uint64_t Id,double Time,FPoint P,int Face,FPolicy InPolicy)
    : Policy(InPolicy)
{
    S.EntityId=Id; S.InitialTime=S.Time=Time; S.InitialPosition=S.Position=P; S.Facing=Face;
    Initialized=Id!=0&&Finite(Time)&&Time>=0&&PointValid(P)&&(Face==1||Face==-1)
        &&Finite(Policy.ExtremelyCloseRadius)&&Policy.ExtremelyCloseRadius>=0&&Policy.ExtremelyCloseRadius<=160;
}
FDefinition FGuardKernel::Definition() { return {}; }
FAttackDefinition FGuardKernel::AttackDefinition(EAttack K)
{
    if(K==EAttack::AxeSweep)return {"ENM-STN-003-A1",1,.5,.2,1.4,3.1,24,30,180,65,65};
    if(K==EAttack::Stomp)return {"ENM-STN-003-A2",.9,.45,.15,1.5,3,18,25,160,90,65};
    return {};
}
bool FGuardKernel::CapacityValid() const
{
    return S.Issued.size()<=MaxRecords&&S.Windows.size()<=MaxRecords&&S.Closures.size()<=MaxRecords
        &&S.HitReceipts.size()<=MaxRecords&&S.ReceivedHits.size()<=MaxRecords
        &&S.NextEventId!=0&&S.NextAttackId!=0;
}
bool FGuardKernel::Visible(const FWorldInput& W) const
{
    return W.HasTarget&&W.TargetAlive&&W.LOS&&std::abs(W.Target.X-S.Position.X)<=650
        &&std::abs(W.Target.Y-S.Position.Y)<=250;
}
bool FGuardKernel::NearWake(const FWorldInput& W) const
{
    return W.HasTarget&&W.TargetAlive&&W.LOS&&Ellipse(W.Target,S.Position,235,110);
}
bool FGuardKernel::Eligible(EAttack K,const FWorldInput& W) const
{
    if(!Initialized||!WorldValid(W)||!AttackKind(K)||S.Phase!=EPhase::Idle||!S.Awakened
        ||!W.CanStartAttack||!Visible(W)||S.Time<S.IdleReadyAt||S.Time<S.OccupiedUntil)return false;
    if(K==EAttack::AxeSweep)return S.Time>=S.AxeReadyAt&&AxeRange(W.Target,S.Position);
    return S.Time>=S.StompReadyAt&&Ellipse(W.Target,S.Position,160,90);
}
EAttack FGuardKernel::ChooseAttack(const FWorldInput& W) const
{
    const bool Axe=Eligible(EAttack::AxeSweep,W), Stomp=Eligible(EAttack::Stomp,W);
    if(!Axe&&!Stomp)return EAttack::None;
    const bool Close=std::hypot(W.Target.X-S.Position.X,W.Target.Y-S.Position.Y)<=Policy.ExtremelyCloseRadius;
    if(Stomp&&(Close||!AxeRange(W.Target,S.Position)))return EAttack::Stomp;
    if(Axe)return EAttack::AxeSweep;
    return Stomp?EAttack::Stomp:EAttack::None;
}
bool FGuardKernel::Advance(double To)
{
    if(!Finite(To)||To<S.Time)return false;
    if(S.LastPoiseAt>=0)
        S.PoiseAccum=std::max(0.,S.PoiseDecayOrigin-20.*std::max(0.,To-(S.LastPoiseAt+1.)));
    S.Time=To; return true;
}
bool FGuardKernel::Emit(FResult& R,EEventKind Kind,double End,double Amount,std::uint64_t Target,FPoint From,FPoint To)
{
    if(S.NextEventId==std::numeric_limits<std::uint64_t>::max()||S.Issued.size()>=MaxRecords)return false;
    FEvent E; E.EventId=S.NextEventId++; E.EntityId=S.EntityId; E.TargetId=Target; E.Kind=Kind;
    E.AtTime=S.Time; E.EndTime=End; E.Amount=Amount; E.From=From; E.To=To; E.Action=S.Action;
    R.Events.push_back(E); S.Issued.push_back(E); return true;
}
bool FGuardKernel::BeginWake(FResult& R)
{
    const double End=S.Time+1.; if(!Increasing(S.Time,End))return false;
    S.WakeQueued=false; S.WakeStartedAt=S.Time; S.WakeEnd=End;
    if(S.Phase!=EPhase::Stunned)S.Phase=EPhase::Waking;
    return Emit(R,EEventKind::WakeStarted,End);
}
bool FGuardKernel::Pump(const FWorldInput& W,FResult& R,bool& Changed)
{
    Changed=true;
    if(S.Phase==EPhase::Dead){Changed=false;return true;}
    // Completing the already-owned recovery is independent of the hurt pose.
    if(S.Action.AttackId&&S.Action.Interrupted&&S.Action.CompletedAt<0&&S.Time>=S.OccupiedUntil)
    {
        S.Action.CompletedAt=S.Time;
        if(S.Phase==EPhase::Recovery)S.Phase=EPhase::Idle;
        return Emit(R,EEventKind::AttackCompleted);
    }
    if(!S.Awakened&&S.WakeStartedAt<0)
    {
        if(S.Phase==EPhase::Dormant&&(NearWake(W)||(S.CombatStartedAt>=0&&S.Time>=S.CombatStartedAt+12)))
            S.WakeQueued=true;
        if(S.WakeQueued&&W.CanBeginWake)return BeginWake(R);
    }
    if(!S.Awakened&&S.WakeStartedAt>=0&&S.Time>=S.WakeEnd)
    {
        S.Awakened=true; S.WakeQueued=false;
        if(S.Phase==EPhase::Waking)S.Phase=EPhase::Idle;
        return Emit(R,EEventKind::WakeCompleted);
    }
    if(S.Phase==EPhase::Stunned)
    {
        if(S.Time<S.StunUntil){Changed=false;return true;}
        if(!S.Awakened)S.Phase=S.WakeStartedAt>=0?EPhase::Waking:EPhase::Dormant;
        else if(S.Action.AttackId&&S.Action.Interrupted&&S.Time<S.OccupiedUntil)
        {
            S.Phase=EPhase::Recovery; return Emit(R,EEventKind::RecoveryStarted,S.OccupiedUntil);
        }
        else S.Phase=EPhase::Idle;
        return true;
    }
    if(S.Phase==EPhase::Windup)
    {
        if(!S.Action.Locked&&S.Time>=S.Action.LockAt)
        {
            S.Action.Locked=true; S.Action.LockedCenter=S.Position;
            if(Visible(W))S.Action.Target=W.Target;
            if(S.Action.Kind==EAttack::AxeSweep)
                S.Action.Facing=FacingToward(S.Position,S.Action.Target,S.Action.Facing);
            S.Facing=S.Action.Facing;
            return Emit(R,EEventKind::AimLocked);
        }
        if(S.Time>=S.Action.ActiveAt)
        {
            S.Action.WindowIssued=true; S.Phase=EPhase::Active;
            FDamageWindow Window; Window.AttackId=S.Action.AttackId; Window.EventId=S.NextEventId;
            Window.Kind=S.Action.Kind; Window.Start=S.Action.ActiveAt; Window.End=S.Action.ActiveEnd;
            Window.Damage=S.Action.Damage; Window.Stagger=S.Action.Stagger;
            Window.Center=S.Action.LockedCenter; Window.Facing=S.Action.Facing;
            S.Windows.push_back(Window);
            return Emit(R,EEventKind::ActiveWindow,Window.End,Window.Damage);
        }
    }
    if(S.Phase==EPhase::Active&&S.Time>=S.Action.ActiveEnd)
    {
        S.Phase=EPhase::Recovery; return Emit(R,EEventKind::RecoveryStarted,S.Action.RecoveryEnd);
    }
    if(S.Phase==EPhase::Recovery&&S.Time>=S.OccupiedUntil)
    {
        S.Action.InProgress=false; S.Action.CompletedAt=S.Time; S.Phase=EPhase::Idle;
        return Emit(R,EEventKind::AttackCompleted);
    }
    Changed=false; return true;
}
bool FGuardKernel::MoveIdle(double To,const FWorldInput& W,FResult& R)
{
    if(!Visible(W))return Advance(To);
    S.Facing=FacingToward(S.Position,W.Target,S.Facing);
    // Do not walk into a player merely because both attack cooldowns are closed.
    if(InAttackRange(W.Target,S.Position))return Advance(To);
    for(int Axis=0;Axis<3&&S.Time<To;++Axis)
    {
        const double DX=W.Target.X-S.Position.X, DY=W.Target.Y-S.Position.Y;
        const bool AlignY=DY!=0;
        FPoint Endpoint=S.Position;
        const auto Entry=FirstAxisAttackEntry(S.Position,W.Target,AlignY,Endpoint);
        if(Entry==EAxisEntry::Invalid)return false;
        if(Entry==EAxisEntry::Unreachable)
        {
            // No attack shape can be entered on this alignment segment.
            if(AlignY)Endpoint.Y=W.Target.Y;else Endpoint.X=W.Target.X;
        }
        const double Gap=std::abs(AlignY?Endpoint.Y-S.Position.Y:Endpoint.X-S.Position.X);
        if(Gap==0)return Advance(To);
        const double Travel=std::min(Gap,160.*(To-S.Time));
        const bool ReachedEndpoint=Travel==Gap;
        double End=ReachedEndpoint?std::min(To,S.Time+Gap/160.):To;
        if(!(End>S.Time))End=std::nextafter(S.Time,To);
        if(!(End>S.Time)||!W.Sweep)return false;
        FPoint Goal=Endpoint;
        if(!ReachedEndpoint)
        {
            Goal=S.Position;
            if(AlignY)Goal.Y+=DY>0?Travel:-Travel;else Goal.X+=DX>0?Travel:-Travel;
        }
        const auto Q=W.Sweep({S.Time,End,S.Position,Goal,40,28});
        if(!Q.Accepted||!Finite(Q.Fraction)||Q.Fraction<0||Q.Fraction>1
            ||static_cast<unsigned>(Q.Stop)>static_cast<unsigned>(EStop::Body)
            ||(Q.Stop==EStop::None&&Q.Fraction!=1))return false;
        const auto From=S.Position;
        // Preserve the absolute analytical endpoint instead of re-adding a
        // rounded difference to a partition-dependent intermediate position.
        S.Position=Q.Fraction==1?Goal:FPoint{From.X+(Goal.X-From.X)*Q.Fraction,
            From.Y+(Goal.Y-From.Y)*Q.Fraction,From.Z};
        if(!PointValid(S.Position)||!Advance(End)||!Emit(R,EEventKind::Movement,End,0,0,From,S.Position))return false;
        if(Q.Stop!=EStop::None||InAttackRange(W.Target,S.Position))return Advance(To);
    }
    return Advance(To);
}
bool FGuardKernel::Interrupt(FResult& R)
{
    if(!S.Action.AttackId||S.Action.CompletedAt>=0||S.Action.Interrupted)return true;
    S.Action.InProgress=false; S.Action.Interrupted=true; S.Action.InterruptedAt=S.Time;
    if(S.Action.WindowIssued)S.Closures.push_back({S.Action.AttackId,S.Time});
    return Emit(R,EEventKind::AttackInterrupted);
}
bool FGuardKernel::ApplyHits(const std::vector<FIncomingHit>& Hits,std::size_t& Index,const FWorldInput& W,FResult& R)
{
    const bool AlreadyDead=S.Phase==EPhase::Dead;
    double Stagger=0; bool TookDamage=false;
    while(Index<Hits.size()&&Hits[Index].AtTime==S.Time)
    {
        const auto H=Hits[Index++]; const double Actual=std::min(S.HP,H.HPLoss);
        S.HP-=Actual; S.LastDamageReceiptId=H.ReceiptId;
        S.ReceivedHits.push_back({H.ReceiptId,S.Time,Actual,H.Stagger});
        Stagger+=H.Stagger; if(!Finite(Stagger))return false;
        if(Actual>0){TookDamage=true;if(!Emit(R,EEventKind::Damaged,0,Actual))return false;}
    }
    // A later receipt from this already validated batch is acknowledged without
    // reissuing death, waking or control effects.
    if(AlreadyDead)return true;
    // At a shared boundary, death/break wins before an unissued active window.
    if(S.HP==0)
    {
        if(!Interrupt(R))return false;
        S.Action.InProgress=false; if(S.Action.AttackId)S.Action.CompletedAt=S.Time;
        S.WakeQueued=false; S.Phase=EPhase::Dead;
        return Emit(R,EEventKind::Died);
    }
    if(TookDamage&&!S.Awakened&&S.WakeStartedAt<0)
    {
        S.WakeQueued=true; if(W.CanBeginWake&&!BeginWake(R))return false;
    }
    if(Stagger>0&&S.Time>=S.ProtectionUntil)
    {
        S.PoiseAccum+=Stagger; if(!Finite(S.PoiseAccum))return false; S.LastPoiseAt=S.Time;
        if(S.PoiseAccum>=85)
        {
            if(!Interrupt(R))return false;
            S.PoiseAccum=0; S.StunUntil=S.Time+.4; S.ProtectionUntil=S.Time+1.;
            if(!Increasing(S.Time,S.StunUntil)||!Increasing(S.Time,S.ProtectionUntil))return false;
            S.Phase=EPhase::Stunned; if(!Emit(R,EEventKind::PoiseBroken,S.StunUntil))return false;
        }
        S.PoiseDecayOrigin=S.PoiseAccum;
    }
    return true;
}
FResult FGuardKernel::StepTo(double Now,const FWorldInput& W,const std::vector<FIncomingHit>& Hits)
{
    if(!Initialized||!Finite(Now)||Now<S.Time||!WorldValid(W)||!CapacityValid()
        ||Hits.size()>MaxRecords-S.ReceivedHits.size()||(S.Phase==EPhase::Dead&&!Hits.empty()))return {};
    double LastAt=S.Time; auto Receipt=S.LastDamageReceiptId;
    for(const auto& H:Hits)
    {
        if(!H.ReceiptId||H.ReceiptId<=Receipt||!Finite(H.AtTime)||H.AtTime<LastAt||H.AtTime>Now
            ||!Finite(H.HPLoss)||H.HPLoss<0||!Finite(H.Stagger)||H.Stagger<0)return {};
        Receipt=H.ReceiptId; LastAt=H.AtTime;
    }
    const auto Before=S; FResult R; std::size_t Index=0;
    for(std::size_t Guard=0;Guard<MaxRecords*4;++Guard)
    {
        if(Index<Hits.size()&&Hits[Index].AtTime==S.Time&&!ApplyHits(Hits,Index,W,R))break;
        bool Changed=false; if(!Pump(W,R,Changed)||!CapacityValid())break;
        if(Changed)continue;
        if(S.Time==Now){R.Accepted=true;return R;}
        double Next=Now;
        const auto Bound=[this,&Next](double At){if(At>S.Time)Next=std::min(Next,At);};
        if(Index<Hits.size())Bound(Hits[Index].AtTime);
        if(!S.Awakened&&S.WakeStartedAt>=0)Bound(S.WakeEnd);
        if(S.Phase==EPhase::Dormant&&S.CombatStartedAt>=0)Bound(S.CombatStartedAt+12);
        if(S.Phase==EPhase::Stunned)Bound(S.StunUntil);
        if(S.Phase==EPhase::Windup){if(!S.Action.Locked)Bound(S.Action.LockAt);Bound(S.Action.ActiveAt);}
        if(S.Phase==EPhase::Active)Bound(S.Action.ActiveEnd);
        if(S.Phase==EPhase::Recovery||(S.Action.Interrupted&&S.Action.CompletedAt<0))Bound(S.OccupiedUntil);
        if(!(Next>S.Time))break;
        if(S.Phase==EPhase::Idle){if(!MoveIdle(Next,W,R))break;}
        else if(!Advance(Next))break;
    }
    S=Before; return {};
}
FResult FGuardKernel::TryStartAttack(EAttack Kind,const FWorldInput& W)
{
    if(!Eligible(Kind,W)||!CapacityValid()||S.NextAttackId==std::numeric_limits<std::uint64_t>::max())return {};
    const auto Before=S; const auto D=AttackDefinition(Kind); FAction A;
    A.AttackId=S.NextAttackId++; A.Kind=Kind; A.InProgress=true; A.Start=S.Time;
    A.LockAt=A.Start+D.LockDelay; A.ActiveAt=A.Start+D.Windup; A.ActiveEnd=A.ActiveAt+D.Active;
    A.RecoveryEnd=A.ActiveEnd+D.Recovery; A.CooldownEnd=A.Start+D.Cooldown;
    A.Origin=A.LockedCenter=S.Position; A.Target=W.Target; A.Facing=FacingToward(S.Position,W.Target,S.Facing);
    A.Damage=D.Damage; A.Stagger=D.Stagger;
    if(!Increasing(A.Start,A.LockAt)||!Increasing(A.LockAt,A.ActiveAt)||!Increasing(A.ActiveAt,A.ActiveEnd)
        ||!Increasing(A.ActiveEnd,A.RecoveryEnd)||!Increasing(A.RecoveryEnd,A.RecoveryEnd+.3)
        ||!Increasing(A.RecoveryEnd,A.CooldownEnd)){S=Before;return {};}
    S.Action=A; S.Facing=A.Facing; S.Phase=EPhase::Windup;
    S.OccupiedUntil=A.RecoveryEnd; S.IdleReadyAt=A.RecoveryEnd+.3;
    if(Kind==EAttack::AxeSweep)S.AxeReadyAt=A.CooldownEnd;else S.StompReadyAt=A.CooldownEnd;
    FResult R; if(!Emit(R,EEventKind::AttackStarted)||!CapacityValid()){S=Before;return {};}
    R.Accepted=true; return R;
}
FResult FGuardKernel::ApplyResolvedHit(std::uint64_t ReceiptId,double HPLoss,double Stagger,const FWorldInput& W)
{
    return StepTo(S.Time,W,{{ReceiptId,S.Time,HPLoss,Stagger}});
}
FResult FGuardKernel::TryHit(const FTarget& T)
{
    if(!Initialized||!T.EntityId||T.EntityId==S.EntityId||!PointValid(T.Position)||!T.Alive||!T.Hostile||!T.LOS||T.Invulnerable
        ||S.Phase!=EPhase::Active||S.Action.Interrupted||!S.Action.WindowIssued
        ||S.Time<S.Action.ActiveAt||S.Time>=S.Action.ActiveEnd||!CapacityValid())return {};
    const FDamageWindow* Window=nullptr;
    for(const auto& W:S.Windows)if(W.AttackId==S.Action.AttackId){Window=&W;break;}
    if(!Window)return {};
    for(const auto& C:S.Closures)if(C.AttackId==Window->AttackId&&S.Time>=C.AtTime)return {};
    if(std::abs(T.Position.Z-Window->Center.Z)>65)return {};
    const double X=(T.Position.X-Window->Center.X)*Window->Facing, Y=T.Position.Y-Window->Center.Y;
    if(Window->Kind==EAttack::AxeSweep){if(X<0||X>180||std::abs(Y)>65)return {};}
    else if(!Ellipse(T.Position,Window->Center,160,90))return {};
    for(const auto& H:S.HitReceipts)if(H.AttackId==Window->AttackId&&H.TargetId==T.EntityId)return {};
    const auto Before=S; S.HitReceipts.push_back({Window->AttackId,T.EntityId,S.Time}); FResult R;
    if(!Emit(R,EEventKind::Hit,Window->End,Window->Damage,T.EntityId)||!CapacityValid()){S=Before;return {};}
    R.Accepted=true; return R;
}
bool FGuardKernel::BeginCombat()
{
    if(!Initialized||S.CombatStartedAt>=0||S.Phase==EPhase::Dead||!Increasing(S.Time,S.Time+12))return false;
    S.CombatStartedAt=S.Time; return true;
}
bool FGuardKernel::NotifyOtherAcceptedEnemiesCleared()
{
    if(!Initialized||S.Awakened||S.WakeStartedAt>=0||S.Phase==EPhase::Dead||S.WakeQueued)return false;
    S.WakeQueued=true; return true;
}
FResult FGuardKernel::ClaimDeathReward()
{
    if(!Initialized||S.Phase!=EPhase::Dead||S.RewardClaimed||!CapacityValid())return {};
    const auto Before=S; S.RewardClaimed=true; FResult R;
    // The room allocator owns source ID / budget / player-live admission / coin spawn.
    if(!Emit(R,EEventKind::RewardClaimed)||!CapacityValid()){S=Before;return {};}
    R.Accepted=true; return R;
}
bool FGuardKernel::GroundBodyEnabled() const { return Initialized&&S.Phase!=EPhase::Dead; }
bool FGuardKernel::CounterWindowOpen() const { return Initialized&&S.HP>0&&S.Phase==EPhase::Recovery; }
bool FGuardKernel::ResetForNewEntity(std::uint64_t Id,double Now,FPoint P,int Face)
{
    if(!Initialized||!Id||Id==S.EntityId||!Finite(Now)||Now<S.Time)return false;
    FGuardKernel Candidate(Id,Now,P,Face,Policy); if(!Candidate.IsValid())return false;
    *this=Candidate; return true;
}
}
