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
double PoiseQuantum(double Value)
{
    if(Value==0)return std::numeric_limits<double>::max();
    int Exponent=0;const double Fraction=std::frexp(Value,&Exponent);
    auto Mantissa=static_cast<std::uint64_t>(std::ldexp(Fraction,53));
    int Zeros=0;while((Mantissa&1)==0){Mantissa>>=1;++Zeros;}
    return std::max(std::numeric_limits<double>::denorm_min(),std::ldexp(1.,Exponent-53+Zeros));
}
FPoiseRange AddPoise(const FPoiseRange& Before,double At,double Sum,std::size_t Count,double Quantum)
{
    const double L=DecayPoise(Before.Low,Before.Last,At),H=DecayPoise(Before.High,Before.Last,At);
    // State v1 omits same-cursor call boundaries. Bound the rounding of any
    // positive-addition partition by its operation count, not a gameplay epsilon.
    const double Upper=H+Sum;
    if(!Finite(Upper)||Upper>86)return {85,std::numeric_limits<double>::max(),At};
    const double CommonQuantum=std::min(Quantum,PoiseQuantum(H));
    // If every value lies on this binary lattice and the complete positive sum
    // fits its 53-bit significand, every possible parenthesization is exact.
    if(L==H&&(Count==1||Upper<std::ldexp(CommonQuantum,53)))return {Upper,Upper,At};
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
    struct FBoundary { double At=0;std::size_t Event=0,ReceivedEnd=0;bool BeforeBreak=true; };
    std::vector<FBoundary> Boundaries;
    std::vector<std::size_t> ReceiptEnds(S.Issued.size(),0);
    for(std::size_t I=0;I<DamageEvents.size();++I)
        if(DamageEvents[I]!=std::numeric_limits<std::size_t>::max())ReceiptEnds[DamageEvents[I]]=I+1;
    std::size_t ReceivedEnd=0;bool Dead=false;
    for(std::size_t I=0;I<S.Issued.size();++I)
    {
        const auto& E=S.Issued[I];
        if(E.Kind==EEventKind::Damaged)ReceivedEnd=ReceiptEnds[I];
        else if(E.Kind==EEventKind::PoiseBroken)Breaks.push_back(I);
        else if(E.Kind==EEventKind::Died)Dead=true;
        else if(!Dead&&E.Kind!=EEventKind::AttackInterrupted)
            // WakeStarted may precede poise inside ApplyHits, but cannot belong
            // to a lethal batch: death is checked before waking.
            Boundaries.push_back({E.AtTime,I,ReceivedEnd,E.Kind!=EEventKind::WakeStarted});
    }
    FPoiseRange R;double Protection=0,Stun=0;std::size_t BreakIndex=0;
    bool MatchedDeath=false;std::size_t BoundaryIndex=0;
    for(std::size_t Begin=0;Begin<S.ReceivedHits.size();)
    {
        const double At=S.ReceivedHits[Begin].AtTime;
        std::size_t End=Begin;while(End<S.ReceivedHits.size()&&S.ReceivedHits[End].AtTime==At)++End;
        if(DeathAt>=0&&At>DeathAt){Begin=End;continue;}
        const bool BreakHere=BreakIndex<Breaks.size()&&S.Issued[Breaks[BreakIndex]].AtTime==At;
        std::size_t ForcedEnd=Begin,BeforeBreakEnd=Begin;
        while(BoundaryIndex<Boundaries.size()&&Boundaries[BoundaryIndex].At<=At)
        {
            const auto B=Boundaries[BoundaryIndex++];
            if(B.At==At)
            {
                ForcedEnd=std::max(ForcedEnd,B.ReceivedEnd);
                if(B.BeforeBreak&&BreakHere&&B.Event<Breaks[BreakIndex])BeforeBreakEnd=std::max(BeforeBreakEnd,B.ReceivedEnd);
            }
        }
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
            double BeforeSum=0,BeforeQuantum=std::numeric_limits<double>::max();
            for(std::size_t I=Begin;I<BeforeBreakEnd;++I)
            {
                const double V=S.ReceivedHits[I].Stagger;
                BeforeQuantum=std::min(BeforeQuantum,PoiseQuantum(V));
                BeforeSum=V>std::numeric_limits<double>::max()-BeforeSum?std::numeric_limits<double>::max():BeforeSum+V;
            }
            if(BeforeSum>0&&AddPoise(R,At,BeforeSum,BeforeBreakEnd-Begin,BeforeQuantum).Low>=85)return false;
            // A positive damage event after the break belongs to a later call.
            // The lethal call suppresses its whole batch's stagger.
            std::size_t Upper=std::min(End,Lethal);
            for(std::size_t I=Begin;I<Upper;++I)
                if(DamageEvents[I]!=std::numeric_limits<std::size_t>::max()&&DamageEvents[I]>EventIndex)
                {Upper=I;break;}
            double Sum=0,Quantum=std::numeric_limits<double>::max();
            for(std::size_t I=Begin;I<Upper;++I)
            {
                const double V=S.ReceivedHits[I].Stagger;
                Quantum=std::min(Quantum,PoiseQuantum(V));
                Sum=V>std::numeric_limits<double>::max()-Sum?std::numeric_limits<double>::max():Sum+V;
            }
            if(Sum<=0||AddPoise(R,At,Sum,Upper-Begin,Quantum).High<85)return false;
            R={0,0,At};Protection=At+1.;Stun=At+.4;
            if(!Increasing(At,Protection)||!Increasing(At,Stun))return false;
            if(At==DeathAt)MatchedDeath=PoiseMatches(R,S);
        }
        else if(At==DeathAt)
        {
            // Any prefix before the first lethal receipt may have been submitted
            // in earlier calls at this cursor. Keep the saved value; do not heal
            // or recompute it by merging the unknown lethal batch.
            MatchedDeath=ForcedEnd==Begin&&PoiseMatches(R,S);
            double Sum=0,Quantum=std::numeric_limits<double>::max();
            for(std::size_t I=Begin;I<Lethal&&!MatchedDeath;++I)
            {
                const double V=S.ReceivedHits[I].Stagger;
                Quantum=std::min(Quantum,PoiseQuantum(V));
                Sum=V>std::numeric_limits<double>::max()-Sum?std::numeric_limits<double>::max():Sum+V;
                if(Sum>0)
                {
                    const auto Candidate=AddPoise(R,At,Sum,I-Begin+1,Quantum);
                    if(I+1>=ForcedEnd&&Candidate.Low<85&&PoiseMatches(Candidate,S))MatchedDeath=true;
                }
                else if(I+1>=ForcedEnd&&PoiseMatches(R,S))MatchedDeath=true;
            }
        }
        else
        {
            double Sum=0,Quantum=std::numeric_limits<double>::max();
            for(std::size_t I=Begin;I<End;++I)
            {
                const double V=S.ReceivedHits[I].Stagger;
                Quantum=std::min(Quantum,PoiseQuantum(V));
                if(V>std::numeric_limits<double>::max()-Sum)return false;
                Sum+=V;
            }
            if(Sum>0)
            {
                R=AddPoise(R,At,Sum,End-Begin,Quantum);
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
    if(S.CombatStartedAt>=0&&!Increasing(S.CombatStartedAt,S.CombatStartedAt+12.))return false;
    if(S.Phase==EPhase::Dormant&&S.CombatStartedAt>=0&&S.Time>=S.CombatStartedAt+12.&&!S.WakeQueued)return false;

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
    double AxeReady=0,StompReady=0,Occupied=0,IdleReady=0,WakeStart=-1,WakeEnd=-1,LastBreak=-1,EventHP=185;
    bool Awakened=false,Dead=false,Claimed=false,NormalRecovery=false,Resumed=true;
    std::uint64_t AttackId=0;std::size_t WindowIndex=0,ClosureIndex=0,HitIndex=0,DamageIndex=0;
    std::set<std::pair<std::uint64_t,std::uint64_t>> Hits;
    for(std::size_t I=0;I<S.Issued.size();++I)
    {
        const auto& E=S.Issued[I];
        if(E.EventId!=I+1||E.EntityId!=S.EntityId||!Finite(E.AtTime)||E.AtTime<LastAt||E.AtTime>S.Time
            ||!Finite(E.EndTime)||!Finite(E.Amount)||!PointValid(E.From)||!PointValid(E.To)
            ||static_cast<unsigned>(E.Kind)>static_cast<unsigned>(EEventKind::RewardClaimed)
            ||!SavedActionValid(E.Action,S)||(Dead&&E.Kind!=EEventKind::RewardClaimed))return false;
        if(!Dead&&EventHP==0&&E.Kind!=EEventKind::AttackInterrupted&&E.Kind!=EEventKind::Died)return false;
        if(!Dead)
        {
            if(WakeStart>=0&&!Awakened&&E.AtTime>WakeEnd)return false;
            if(Current.AttackId&&Current.CompletedAt<0&&E.AtTime>Occupied)return false;
            if(Current.InProgress&&((!Current.Locked&&E.AtTime>Current.LockAt)
                ||(!Current.WindowIssued&&E.AtTime>Current.ActiveAt)
                ||(!NormalRecovery&&E.AtTime>Current.ActiveEnd)))return false;
            if(Current.Interrupted&&Current.CompletedAt<0&&!Resumed&&LastBreak+.4<Occupied
                &&E.AtTime>LastBreak+.4)return false;
        }
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
            Expected=A;AttackId=A.AttackId;Occupied=A.RecoveryEnd;IdleReady=Occupied+.3;NormalRecovery=false;Resumed=true;
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
            {if(LastBreak<0||Resumed||E.AtTime!=LastBreak+.4||E.AtTime>=Occupied)return false;Resumed=true;}
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
            Amount=S.ReceivedHits[DamageIndex].ActualHPLoss;EventHP-=Amount;DamageEvents[DamageIndex++]=I;break;
        case EEventKind::PoiseBroken:
            if(LastBreak>=0&&E.AtTime<LastBreak+1.)return false;
            if(Current.InProgress)return false;
            LastBreak=E.AtTime;End=LastBreak+.4;if(!Increasing(LastBreak,End))return false;
            if(Current.AttackId&&Current.CompletedAt<0)Resumed=false;
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
            if(Dead||EventHP!=0||DeathAt<0||E.AtTime!=DeathAt||Current.InProgress)return false;
            Expected.InProgress=false;if(Current.AttackId)Expected.CompletedAt=E.AtTime;Dead=true;break;
        case EEventKind::RewardClaimed:
            if(!Dead||Claimed||E.AtTime<ReceivedAt)return false;Claimed=true;break;
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
    {if(!Current.Interrupted||S.Time>=Occupied||!Resumed)return false;Phase=EPhase::Recovery;}
    else Phase=EPhase::Idle;
    if(S.Phase!=Phase)return false;
    if(Current.AttackId&&Current.CompletedAt<0&&S.Facing!=Current.Facing)return false;
    return true;
}
