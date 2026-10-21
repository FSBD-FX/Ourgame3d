#include "DungeonStoneGuard.h"
#include <algorithm>
#include <cmath>
#include <limits>
#include <set>
#include <utility>

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
// Pure saved-state validation. These helpers never mutate a kernel or call a world query.
bool SamePoint(FPoint A,FPoint B) { return A.X==B.X&&A.Y==B.Y&&A.Z==B.Z; }
bool SameAction(const FAction& A,const FAction& B)
{
    return A.AttackId==B.AttackId&&A.Kind==B.Kind&&A.InProgress==B.InProgress
        &&A.Locked==B.Locked&&A.WindowIssued==B.WindowIssued&&A.Interrupted==B.Interrupted
        &&A.Start==B.Start&&A.LockAt==B.LockAt&&A.ActiveAt==B.ActiveAt&&A.ActiveEnd==B.ActiveEnd
        &&A.RecoveryEnd==B.RecoveryEnd&&A.CooldownEnd==B.CooldownEnd
        &&A.InterruptedAt==B.InterruptedAt&&A.CompletedAt==B.CompletedAt
        &&A.Damage==B.Damage&&A.Stagger==B.Stagger&&SamePoint(A.Origin,B.Origin)
        &&SamePoint(A.LockedCenter,B.LockedCenter)&&SamePoint(A.Target,B.Target)&&A.Facing==B.Facing;
}
bool FacingValid(int Face) { return Face==1||Face==-1; }
bool TimeOrUnset(double At,const FState& S)
{
    return At==-1||(Finite(At)&&At>=S.InitialTime&&At<=S.Time);
}
bool SavedActionValid(const FAction& A,const FState& S)
{
    if(!A.AttackId)return SameAction(A,FAction{});
    if(!AttackKind(A.Kind)||!FacingValid(A.Facing)||!PointValid(A.Origin)
        ||!PointValid(A.LockedCenter)||!PointValid(A.Target)||A.Origin.Z!=S.InitialPosition.Z
        ||!SamePoint(A.Origin,A.LockedCenter)||!Finite(A.Start)||A.Start<S.InitialTime||A.Start>S.Time)return false;
    const auto D=FGuardKernel::AttackDefinition(A.Kind);
    if(A.LockAt!=A.Start+D.LockDelay||A.ActiveAt!=A.Start+D.Windup
        ||A.ActiveEnd!=A.ActiveAt+D.Active||A.RecoveryEnd!=A.ActiveEnd+D.Recovery
        ||A.CooldownEnd!=A.Start+D.Cooldown||A.Damage!=D.Damage||A.Stagger!=D.Stagger
        ||!Increasing(A.Start,A.LockAt)||!Increasing(A.LockAt,A.ActiveAt)
        ||!Increasing(A.ActiveAt,A.ActiveEnd)||!Increasing(A.ActiveEnd,A.RecoveryEnd)
        ||!Increasing(A.RecoveryEnd,A.RecoveryEnd+.3)||!Increasing(A.RecoveryEnd,A.CooldownEnd))return false;
    if(A.Interrupted)
    {
        if(!Finite(A.InterruptedAt)||A.InterruptedAt<A.Start||A.InterruptedAt>A.RecoveryEnd
            ||A.InterruptedAt>S.Time)return false;
    }
    else if(A.InterruptedAt!=-1)return false;
    if(A.CompletedAt!=-1&&(!Finite(A.CompletedAt)||A.CompletedAt<A.Start||A.CompletedAt>S.Time))return false;
    if(A.InProgress!=(!A.Interrupted&&A.CompletedAt<0)||(!A.Locked&&A.WindowIssued))return false;
    return true;
}
struct FPoiseRange
{
    double Low=0,High=0,Last=-1;
};
double DecayPoise(double Origin,double Last,double Now)
{
    return Last<0?0:std::max(0.,Origin-20.*std::max(0.,Now-(Last+1.)));
}
FPoiseRange AddPoise(const FPoiseRange& Before,double At,double Sum,std::size_t Count)
{
    const double L=DecayPoise(Before.Low,Before.Last,At),H=DecayPoise(Before.High,Before.Last,At);
    // State v1 omits same-cursor call boundaries. Bound the rounding of any
    // positive-addition partition by its operation count, not a gameplay epsilon.
    const double Upper=H+Sum;
    if(!Finite(Upper)||Upper>86)return {85,std::numeric_limits<double>::max(),At};
    const double Operations=4.*static_cast<double>(Count)+8.;
    const double Error=Operations*std::numeric_limits<double>::epsilon()*Upper
        +Operations*std::numeric_limits<double>::denorm_min();
    return {std::max(0.,L+Sum-Error),Upper+Error,At};
}
bool PoiseMatches(const FPoiseRange& R,const FState& S)
{
    return S.LastPoiseAt==R.Last&&S.PoiseDecayOrigin>=R.Low&&S.PoiseDecayOrigin<=R.High;
}
bool SavedPoiseValid(const FState& S,const std::vector<std::size_t>& DamageEvents,double DeathAt)
{
    std::vector<std::size_t> Breaks;
    for(std::size_t I=0;I<S.Issued.size();++I)
        if(S.Issued[I].Kind==EEventKind::PoiseBroken)Breaks.push_back(I);
    FPoiseRange R;double Protection=0,Stun=0;std::size_t BreakIndex=0;
    bool MatchedDeath=false;
    for(std::size_t Begin=0;Begin<S.ReceivedHits.size();)
    {
        const double At=S.ReceivedHits[Begin].AtTime;
        std::size_t End=Begin;while(End<S.ReceivedHits.size()&&S.ReceivedHits[End].AtTime==At)++End;
        if(DeathAt>=0&&At>DeathAt){Begin=End;continue;}
        const bool BreakHere=BreakIndex<Breaks.size()&&S.Issued[Breaks[BreakIndex]].AtTime==At;
        if(BreakIndex<Breaks.size()&&S.Issued[Breaks[BreakIndex]].AtTime<At)return false;
        if(At<Protection)
        {
            if(BreakHere)return false;
            if(At==DeathAt)MatchedDeath=PoiseMatches(R,S);
            Begin=End;continue;
        }
        std::size_t Lethal=End;
        if(At==DeathAt)
        {
            double HP=185;
            for(std::size_t I=0;I<End;++I)
            {
                HP-=S.ReceivedHits[I].ActualHPLoss;
                if(HP==0){Lethal=I;break;}
            }
            if(Lethal<Begin||Lethal>=End)return false;
        }
        if(BreakHere)
        {
            const auto EventIndex=Breaks[BreakIndex++];
            if(BreakIndex<Breaks.size()&&S.Issued[Breaks[BreakIndex]].AtTime==At)return false;
            // A positive damage event after the break belongs to a later call.
            // The lethal call suppresses its whole batch's stagger.
            std::size_t Upper=std::min(End,Lethal);
            for(std::size_t I=Begin;I<Upper;++I)
                if(DamageEvents[I]!=std::numeric_limits<std::size_t>::max()&&DamageEvents[I]>EventIndex)
                {Upper=I;break;}
            double Sum=0;
            for(std::size_t I=Begin;I<Upper;++I)
            {
                const double V=S.ReceivedHits[I].Stagger;
                Sum=V>std::numeric_limits<double>::max()-Sum?std::numeric_limits<double>::max():Sum+V;
            }
            if(Sum<=0||AddPoise(R,At,Sum,Upper-Begin).High<85)return false;
            R={0,0,At};Protection=At+1.;Stun=At+.4;
            if(!Increasing(At,Protection)||!Increasing(At,Stun))return false;
            if(At==DeathAt)MatchedDeath=PoiseMatches(R,S);
        }
        else if(At==DeathAt)
        {
            // Any prefix before the first lethal receipt may have been submitted
            // in earlier calls at this cursor. Keep the saved value; do not heal
            // or recompute it by merging the unknown lethal batch.
            MatchedDeath=PoiseMatches(R,S);
            double Sum=0;
            for(std::size_t I=Begin;I<Lethal&&!MatchedDeath;++I)
            {
                const double V=S.ReceivedHits[I].Stagger;
                Sum=V>std::numeric_limits<double>::max()-Sum?std::numeric_limits<double>::max():Sum+V;
                if(Sum>0)
                {
                    const auto Candidate=AddPoise(R,At,Sum,I-Begin+1);
                    if(Candidate.Low<85&&PoiseMatches(Candidate,S))MatchedDeath=true;
                }
            }
        }
        else
        {
            double Sum=0;
            for(std::size_t I=Begin;I<End;++I)
            {
                const double V=S.ReceivedHits[I].Stagger;
                if(V>std::numeric_limits<double>::max()-Sum)return false;
                Sum+=V;
            }
            if(Sum>0)
            {
                R=AddPoise(R,At,Sum,End-Begin);
                if(R.Low>=85)return false;
                R.High=std::min(R.High,std::nextafter(85.,0.));
            }
        }
        Begin=End;
    }
    if(BreakIndex!=Breaks.size()||S.ProtectionUntil!=Protection||S.StunUntil!=Stun)return false;
    if(DeathAt>=0?!MatchedDeath:!PoiseMatches(R,S))return false;
    return S.PoiseAccum==DecayPoise(S.PoiseDecayOrigin,S.LastPoiseAt,S.Time);
}
bool SavedStateValid(const FState& S)
{
    if(S.Version!=1||!S.EntityId||!Finite(S.InitialTime)||S.InitialTime<0||!Finite(S.Time)||S.Time<S.InitialTime
        ||!PointValid(S.InitialPosition)||!PointValid(S.Position)||S.Position.Z!=S.InitialPosition.Z
        ||!FacingValid(S.Facing)||static_cast<unsigned>(S.Phase)>static_cast<unsigned>(EPhase::Dead)
        ||S.Issued.size()>MaxRecords||S.Windows.size()>MaxRecords||S.Closures.size()>MaxRecords
        ||S.HitReceipts.size()>MaxRecords||S.ReceivedHits.size()>MaxRecords
        ||S.NextEventId!=S.Issued.size()+1||!S.NextAttackId
        ||!Finite(S.HP)||S.HP<0||S.HP>185||!Finite(S.PoiseAccum)||S.PoiseAccum<0||S.PoiseAccum>=85
        ||!Finite(S.PoiseDecayOrigin)||S.PoiseDecayOrigin<0||S.PoiseDecayOrigin>=85
        ||!TimeOrUnset(S.LastPoiseAt,S)||!TimeOrUnset(S.CombatStartedAt,S)
        ||!TimeOrUnset(S.WakeStartedAt,S)||!Finite(S.WakeEnd)
        ||!Finite(S.ProtectionUntil)||S.ProtectionUntil<0||!Finite(S.StunUntil)||S.StunUntil<0
        ||!Finite(S.AxeReadyAt)||!Finite(S.StompReadyAt)||!Finite(S.OccupiedUntil)||!Finite(S.IdleReadyAt)
        ||!SavedActionValid(S.Action,S))return false;

    const auto NoIndex=std::numeric_limits<std::size_t>::max();
    std::vector<std::size_t> DamageEvents(S.ReceivedHits.size(),NoIndex);
    double HP=185,ReceivedAt=S.InitialTime,DeathAt=-1;std::uint64_t ReceiptId=0;
    for(const auto& H:S.ReceivedHits)
    {
        if(!H.ReceiptId||H.ReceiptId<=ReceiptId||!Finite(H.AtTime)||H.AtTime<ReceivedAt||H.AtTime>S.Time
            ||!Finite(H.ActualHPLoss)||H.ActualHPLoss<0||H.ActualHPLoss>HP
            ||!Finite(H.Stagger)||H.Stagger<0)return false;
        ReceiptId=H.ReceiptId;ReceivedAt=H.AtTime;HP-=H.ActualHPLoss;
        if(HP==0&&DeathAt<0)DeathAt=H.AtTime;
    }
    if(S.HP!=HP||S.LastDamageReceiptId!=ReceiptId)return false;

    FAction Current;FPoint Position=S.InitialPosition;double LastAt=S.InitialTime;
    double AxeReady=0,StompReady=0,Occupied=0,IdleReady=0,WakeStart=-1,WakeEnd=-1,LastBreak=-1;
    bool Awakened=false,Dead=false,Claimed=false,NormalRecovery=false;
    std::uint64_t AttackId=0;std::size_t WindowIndex=0,ClosureIndex=0,HitIndex=0,DamageIndex=0;
    std::set<std::pair<std::uint64_t,std::uint64_t>> Hits;
    for(std::size_t I=0;I<S.Issued.size();++I)
    {
        const auto& E=S.Issued[I];
        if(E.EventId!=I+1||E.EntityId!=S.EntityId||!Finite(E.AtTime)||E.AtTime<LastAt||E.AtTime>S.Time
            ||!Finite(E.EndTime)||!Finite(E.Amount)||!PointValid(E.From)||!PointValid(E.To)
            ||static_cast<unsigned>(E.Kind)>static_cast<unsigned>(EEventKind::RewardClaimed)
            ||!SavedActionValid(E.Action,S)||(Dead&&E.Kind!=EEventKind::RewardClaimed))return false;
        double End=0,Amount=0;std::uint64_t Target=0;FAction Expected=Current;
        if(E.Kind!=EEventKind::Movement&&(!SamePoint(E.From,{})||!SamePoint(E.To,{})))return false;
        switch(E.Kind)
        {
        case EEventKind::WakeStarted:
            if(WakeStart>=0||Awakened)return false;
            WakeStart=E.AtTime;WakeEnd=WakeStart+1.;End=WakeEnd;
            if(!Increasing(WakeStart,WakeEnd))return false;
            break;
        case EEventKind::WakeCompleted:
            if(WakeStart<0||Awakened||E.AtTime!=WakeEnd)return false;
            Awakened=true;break;
        case EEventKind::AttackStarted:
        {
            const auto& A=E.Action;
            if(!Awakened||E.AtTime<IdleReady||E.AtTime<Occupied||(LastBreak>=0&&E.AtTime<LastBreak+.4)
                ||(Current.AttackId&&Current.CompletedAt<0)||A.AttackId!=AttackId+1||A.Start!=E.AtTime
                ||!SamePoint(A.Origin,Position)||!A.InProgress||A.Locked||A.WindowIssued||A.Interrupted
                ||A.InterruptedAt!=-1||A.CompletedAt!=-1||A.Facing!=FacingToward(Position,A.Target,A.Facing))return false;
            if(A.Kind==EAttack::AxeSweep)
            {if(E.AtTime<AxeReady||!AxeRange(A.Target,Position))return false;AxeReady=A.CooldownEnd;}
            else
            {if(E.AtTime<StompReady||!Ellipse(A.Target,Position,160,90))return false;StompReady=A.CooldownEnd;}
            Expected=A;AttackId=A.AttackId;Occupied=A.RecoveryEnd;IdleReady=Occupied+.3;NormalRecovery=false;
            break;
        }
        case EEventKind::AimLocked:
            if(!Current.AttackId||!Current.InProgress||Current.Locked||E.AtTime!=Current.LockAt)return false;
            Expected.Locked=true;Expected.LockedCenter=Position;Expected.Target=E.Action.Target;
            if(std::abs(Expected.Target.X-Position.X)>650||std::abs(Expected.Target.Y-Position.Y)>250)return false;
            if(Current.Kind==EAttack::AxeSweep)Expected.Facing=FacingToward(Position,Expected.Target,Current.Facing);
            break;
        case EEventKind::ActiveWindow:
        {
            if(!Current.InProgress||!Current.Locked||Current.WindowIssued||E.AtTime!=Current.ActiveAt
                ||WindowIndex>=S.Windows.size())return false;
            Expected.WindowIssued=true;End=Current.ActiveEnd;Amount=Current.Damage;
            const auto& W=S.Windows[WindowIndex++];
            if(W.AttackId!=Current.AttackId||W.EventId!=E.EventId||W.Kind!=Current.Kind
                ||W.Start!=Current.ActiveAt||W.End!=Current.ActiveEnd||W.Damage!=Current.Damage
                ||W.Stagger!=Current.Stagger||W.Facing!=Current.Facing||!SamePoint(W.Center,Current.LockedCenter))return false;
            break;
        }
        case EEventKind::RecoveryStarted:
            if(!Current.AttackId||Current.CompletedAt>=0)return false;
            if(Current.Interrupted)
            {if(LastBreak<0||E.AtTime!=LastBreak+.4||E.AtTime>=Occupied)return false;}
            else
            {if(!Current.WindowIssued||NormalRecovery||E.AtTime!=Current.ActiveEnd)return false;NormalRecovery=true;}
            End=Occupied;break;
        case EEventKind::AttackCompleted:
            if(!Current.AttackId||Current.CompletedAt>=0||E.AtTime!=Occupied
                ||(!Current.Interrupted&&!NormalRecovery))return false;
            Expected.InProgress=false;Expected.CompletedAt=E.AtTime;break;
        case EEventKind::Movement:
            if(!Awakened||E.AtTime<=LastAt||E.AtTime<Occupied||(LastBreak>=0&&E.AtTime<LastBreak+.4)
                ||Current.InProgress||!SamePoint(E.From,Position)||E.To.Z!=Position.Z
                ||(E.To.X!=Position.X&&E.To.Y!=Position.Y))return false;
            Position=E.To;End=E.AtTime;break;
        case EEventKind::Damaged:
            while(DamageIndex<S.ReceivedHits.size()&&S.ReceivedHits[DamageIndex].ActualHPLoss==0)++DamageIndex;
            if(DamageIndex>=S.ReceivedHits.size()||E.AtTime!=S.ReceivedHits[DamageIndex].AtTime)return false;
            Amount=S.ReceivedHits[DamageIndex].ActualHPLoss;DamageEvents[DamageIndex++]=I;break;
        case EEventKind::PoiseBroken:
            if(LastBreak>=0&&E.AtTime<LastBreak+1.)return false;
            if(Current.InProgress)return false;
            LastBreak=E.AtTime;End=LastBreak+.4;if(!Increasing(LastBreak,End))return false;
            break;
        case EEventKind::AttackInterrupted:
            if(!Current.AttackId||Current.CompletedAt>=0||Current.Interrupted||E.AtTime<Current.Start
                ||E.AtTime>Occupied||I+1>=S.Issued.size()||S.Issued[I+1].AtTime!=E.AtTime
                ||(S.Issued[I+1].Kind!=EEventKind::PoiseBroken&&S.Issued[I+1].Kind!=EEventKind::Died))return false;
            Expected.InProgress=false;Expected.Interrupted=true;Expected.InterruptedAt=E.AtTime;
            if(Current.WindowIssued)
            {
                if(ClosureIndex>=S.Closures.size())return false;
                const auto& C=S.Closures[ClosureIndex++];
                if(C.AttackId!=Current.AttackId||C.AtTime!=E.AtTime)return false;
            }
            break;
        case EEventKind::Hit:
        {
            if(!Current.InProgress||Current.Interrupted||!Current.WindowIssued
                ||E.AtTime<Current.ActiveAt||E.AtTime>=Current.ActiveEnd||HitIndex>=S.HitReceipts.size())return false;
            const auto& H=S.HitReceipts[HitIndex++];
            if(H.AttackId!=Current.AttackId||!H.TargetId||H.TargetId==S.EntityId||H.AtTime!=E.AtTime
                ||!Hits.insert({H.AttackId,H.TargetId}).second)return false;
            End=Current.ActiveEnd;Amount=Current.Damage;Target=H.TargetId;break;
        }
        case EEventKind::Died:
            if(Dead||DeathAt<0||E.AtTime!=DeathAt||Current.InProgress)return false;
            Expected.InProgress=false;if(Current.AttackId)Expected.CompletedAt=E.AtTime;Dead=true;break;
        case EEventKind::RewardClaimed:
            if(!Dead||Claimed)return false;Claimed=true;break;
        }
        if(!SameAction(E.Action,Expected)||E.EndTime!=End||E.Amount!=Amount||E.TargetId!=Target)return false;
        Current=E.Action;LastAt=E.AtTime;
    }
    while(DamageIndex<S.ReceivedHits.size()&&S.ReceivedHits[DamageIndex].ActualHPLoss==0)++DamageIndex;
    if(DamageIndex!=S.ReceivedHits.size()||WindowIndex!=S.Windows.size()||ClosureIndex!=S.Closures.size()
        ||HitIndex!=S.HitReceipts.size()||S.NextAttackId!=AttackId+1||!SameAction(S.Action,Current)
        ||!SamePoint(S.Position,Position)||S.AxeReadyAt!=AxeReady||S.StompReadyAt!=StompReady
        ||S.OccupiedUntil!=Occupied||S.IdleReadyAt!=IdleReady||S.WakeStartedAt!=WakeStart||S.WakeEnd!=WakeEnd
        ||S.Awakened!=Awakened||S.RewardClaimed!=Claimed||Dead!=(S.HP==0)
        ||(DeathAt>=0&&S.CombatStartedAt>DeathAt))return false;
    if((S.Awakened||S.WakeStartedAt>=0||Dead)&&S.WakeQueued)return false;
    if(!Dead&&!Awakened&&WakeStart<0&&S.HP<185&&!S.WakeQueued)return false;
    if(!Dead&&WakeStart>=0&&S.Time>=WakeEnd&&!Awakened)return false;
    if(!SavedPoiseValid(S,DamageEvents,DeathAt))return false;
    EPhase Phase=EPhase::Dormant;
    if(Dead)Phase=EPhase::Dead;
    else if(LastBreak>=0&&S.Time<LastBreak+.4)Phase=EPhase::Stunned;
    else if(!Awakened)Phase=WakeStart>=0?EPhase::Waking:EPhase::Dormant;
    else if(Current.InProgress)
    {
        if(S.Time<Current.ActiveAt)
        {if(Current.Locked!=(S.Time>=Current.LockAt)||Current.WindowIssued)return false;Phase=EPhase::Windup;}
        else if(S.Time<Current.ActiveEnd)
        {if(!Current.WindowIssued)return false;Phase=EPhase::Active;}
        else if(S.Time<Occupied)
        {if(!NormalRecovery)return false;Phase=EPhase::Recovery;}
        else return false;
    }
    else if(Current.AttackId&&Current.CompletedAt<0)
    {if(!Current.Interrupted||S.Time>=Occupied)return false;Phase=EPhase::Recovery;}
    else Phase=EPhase::Idle;
    if(S.Phase!=Phase)return false;
    if(Current.AttackId&&Current.CompletedAt<0&&S.Facing!=Current.Facing)return false;
    return true;
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
bool FGuardKernel::Restore(const FState& Saved)
{
    if(!Initialized||!Finite(Policy.ExtremelyCloseRadius)||Policy.ExtremelyCloseRadius<0
        ||Policy.ExtremelyCloseRadius>160||Saved.EntityId!=S.EntityId||Saved.InitialTime!=S.InitialTime
        ||!SamePoint(Saved.InitialPosition,S.InitialPosition)||!SavedStateValid(Saved))return false;
    FState Candidate=Saved;
    S=std::move(Candidate);
    return true;
}
}
