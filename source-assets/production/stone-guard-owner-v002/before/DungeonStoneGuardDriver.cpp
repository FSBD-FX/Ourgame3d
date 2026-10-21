#include "DungeonStoneGuardDriver.h"
#include "DungeonFighter.h"
#include "CollisionQueryParams.h"
#include "CollisionShape.h"
#include "Engine/World.h"
#include <cmath>
#include <limits>
namespace
{
namespace Guard=DungeonStoneGuard;
FVector2D XY(Guard::FPoint P){return {P.X,P.Y};}
bool Finite(FVector2D P){return FMath::IsFinite(P.X)&&FMath::IsFinite(P.Y);}
double Alpha(const FDungeonKnightFrame& F,double At){return F.ToTime>F.FromTime?FMath::Clamp((At-F.FromTime)/(F.ToTime-F.FromTime),0.,1.):1.;}
FVector2D PositionAt(const FDungeonKnightBody& B,const FDungeonKnightFrame& F,double At)
{
    for(int32 I=B.MotionSegments.Num()-1;I>=0;--I)
    {
        const auto& M=B.MotionSegments[I];
        if(At>=M.FromTime&&(At<M.ToTime||(!M.bEndExclusive&&At==M.ToTime)))
            return FMath::Lerp(M.From,M.To,M.ToTime>M.FromTime?(At-M.FromTime)/(M.ToTime-M.FromTime):1.);
    }
    return FMath::Lerp(B.Start,B.End,Alpha(F,At));
}
double HeightAt(const FDungeonKnightBody& B,const FDungeonKnightFrame& F,double At)
{
    for(int32 I=B.MotionSegments.Num()-1;I>=0;--I)
    {
        const auto& M=B.MotionSegments[I];
        if(At>=M.FromTime&&(At<M.ToTime||(!M.bEndExclusive&&At==M.ToTime)))
            return FMath::Lerp(M.FromHeight,M.ToHeight,M.ToTime>M.FromTime?(At-M.FromTime)/(M.ToTime-M.FromTime):1.);
    }
    return FMath::Lerp(B.StartHeight,B.EndHeight,Alpha(F,At));
}
const FDungeonKnightBody* TargetBody(const FDungeonKnightFrame& F)
{for(const auto& B:F.Bodies)if(B.Fighter==F.Target)return &B;return nullptr;}
FCollisionObjectQueryParams WallObjects()
{FCollisionObjectQueryParams O;O.AddObjectTypesToQuery(ECC_WorldStatic);O.AddObjectTypesToQuery(ECC_WorldDynamic);return O;}
bool Clip(double A,double Z,double Low,double High,double& Entry,double& Exit)
{
    if(A==Z)return A>=Low&&A<=High;
    double P=(Low-A)/(Z-A),Q=(High-A)/(Z-A);if(P>Q)Swap(P,Q);
    Entry=FMath::Max(Entry,P);Exit=FMath::Min(Exit,Q);return Entry<=Exit&&Entry<=1.&&Exit>=0.;
}
bool EllipseContact(FVector2D P0,FVector2D P1,double RX,double RY,double& Entry,double& Exit)
{
    const FVector2D P(P0.X/RX,P0.Y/RY),D((P1.X-P0.X)/RX,(P1.Y-P0.Y)/RY);
    const double A=D.SizeSquared(),B=2.*FVector2D::DotProduct(P,D),C=P.SizeSquared()-1.;
    if(A==0.)return C<=0.;
    const double Disc=B*B-4.*A*C;if(Disc<0.)return false;
    const double Root=FMath::Sqrt(Disc);
    Entry=FMath::Max(Entry,(-B-Root)/(2.*A));Exit=FMath::Min(Exit,(-B+Root)/(2.*A));
    return Entry<=Exit&&Entry<=1.&&Exit>=0.;
}
bool BodyContact(FVector2D A,FVector2D Z,FVector2D Extent,double& Entry,double& Exit)
{
    if(!Clip(A.X,Z.X,-Extent.X,Extent.X,Entry,Exit)||!Clip(A.Y,Z.Y,-Extent.Y,Extent.Y,Entry,Exit))return false;
    if(Entry==0.)
    {
        const auto D=Z-A;
        if(FMath::Abs(A.X)<Extent.X&&FMath::Abs(A.Y)<Extent.Y)
        {
            const bool X=Extent.X-FMath::Abs(A.X)<=Extent.Y-FMath::Abs(A.Y);
            if(X?A.X*D.X>=0.:A.Y*D.Y>=0.)return false;
        }
        else
        {
            const bool X=FMath::Abs(A.X)<Extent.X||(A.X==Extent.X&&D.X<0.)||(A.X==-Extent.X&&D.X>0.);
            const bool Y=FMath::Abs(A.Y)<Extent.Y||(A.Y==Extent.Y&&D.Y<0.)||(A.Y==-Extent.Y&&D.Y>0.);
            if(!X||!Y||Exit<=0.)return false; // Touching/sliding away is not entry.
        }
    }
    return true;
}
TArray<TPair<double,double>> Slices(const FDungeonKnightBody& B,double Begin,double End)
{
    TArray<TPair<double,double>> Out;
    if(B.MotionSegments.IsEmpty()){Out.Add({Begin,End});return Out;}
    for(const auto& M:B.MotionSegments)
    {
        const double A=FMath::Max(Begin,M.FromTime);double Z=FMath::Min(End,M.ToTime);
        if(M.bEndExclusive&&Z==M.ToTime)Z=std::nextafter(Z,A);
        if(A<=Z&&!(M.bEndExclusive&&A==M.ToTime))Out.Add({A,Z});
    }
    return Out;
}
bool AdmittedAt(const FDungeonKnightBody& B,double At)
{
    if(!B.bUseTimedDamageAdmission)return B.bCanTakeDamage;
    for(const auto& I:B.DirectInvulnerabilityIntervals)if(At>=I.Start&&At<I.EndExclusive)return false;
    return true;
}
bool FirstAdmitted(const FDungeonKnightBody& B,double Begin,double End,double& At)
{
    if(!B.bUseTimedDamageAdmission){At=Begin;return B.bCanTakeDamage;}
    At=Begin;
    for(int32 N=0;N<=B.DirectInvulnerabilityIntervals.Num();++N)
    {
        double Next=At;for(const auto& I:B.DirectInvulnerabilityIntervals)
            if(At>=I.Start&&At<I.EndExclusive)Next=FMath::Max(Next,I.EndExclusive);
        if(Next==At)return At<=End;At=Next;if(At>End)return false;
    }
    return false;
}
double NextBoundary(const Guard::FState& S,const FDungeonKnightFrame& F,double Limit)
{
    const auto Bound=[&](double At){if(At>S.Time)Limit=FMath::Min(Limit,At);};
    if(!S.Awakened&&S.WakeStartedAt>=0.)Bound(S.WakeEnd);
    if(S.Phase==Guard::EPhase::Dormant&&S.CombatStartedAt>=0.)Bound(S.CombatStartedAt+12.);
    if(S.Phase==Guard::EPhase::Stunned)Bound(S.StunUntil);
    if(S.Phase==Guard::EPhase::Idle){Bound(S.IdleReadyAt);Bound(S.AxeReadyAt);Bound(S.StompReadyAt);}
    const auto& A=S.Action;
    if(S.Phase==Guard::EPhase::Windup){if(!A.Locked)Bound(A.LockAt);Bound(A.ActiveAt);}
    if(S.Phase==Guard::EPhase::Active)Bound(A.ActiveEnd);
    if(S.Phase==Guard::EPhase::Recovery||(A.Interrupted&&A.CompletedAt<0.))Bound(S.OccupiedUntil);
    for(const auto& B:F.Bodies)
    {
        for(const auto& I:B.DirectInvulnerabilityIntervals){Bound(I.Start);Bound(I.EndExclusive);}
        for(const auto& M:B.MotionSegments){Bound(M.FromTime);Bound(M.ToTime);}
    }
    return Limit;
}
void Append(FDungeonGuardBatch& B,const Guard::FResult& R)
{B.Events.insert(B.Events.end(),R.Events.begin(),R.Events.end());}
}
FDungeonStoneGuardDriver::FDungeonStoneGuardDriver(ADungeonFighter* InOwner,uint64 Id,double Time)
    :Owner(InOwner),Kernel(Id,Time,InOwner?Guard::FPoint{InOwner->GetGroundPosition().X,InOwner->GetGroundPosition().Y,0.}:Guard::FPoint{}){}
bool FDungeonStoneGuardDriver::BeginCombat(){return Kernel.BeginCombat();}
bool FDungeonStoneGuardDriver::NotifyOtherAcceptedEnemiesCleared(){return Kernel.NotifyOtherAcceptedEnemiesCleared();}
bool FDungeonStoneGuardDriver::ClaimDeathReward(){return Kernel.ClaimDeathReward().Accepted;}
bool FDungeonStoneGuardDriver::ValidFrame(const FDungeonKnightFrame& F) const
{
    if(!Kernel.IsValid()||!Owner.IsValid()||!Owner->GetWorld()||!Owner->bEnemy||Owner->EnemyContentId!=TEXT("ENM-STN-003")
        ||Owner->GetRuntimeEntityId()!=State().EntityId||!FMath::IsFinite(F.FromTime)||!FMath::IsFinite(F.ToTime)
        ||F.FromTime<0.||F.ToTime<F.FromTime||F.Bodies.Num()>4096)return false;
    if(F.bUseCenterBounds&&(!F.CenterBounds.bIsValid||!Finite(F.CenterBounds.Min)||!Finite(F.CenterBounds.Max)
        ||F.CenterBounds.Min.X>F.CenterBounds.Max.X||F.CenterBounds.Min.Y>F.CenterBounds.Max.Y))return false;
    bool HasOwner=false;
    for(int32 I=0;I<F.Bodies.Num();++I)
    {
        const auto& B=F.Bodies[I];
        if(!B.EntityId||!B.Fighter.IsValid()||B.Fighter->GetWorld()!=Owner->GetWorld()||!Finite(B.Start)||!Finite(B.End)
            ||!FMath::IsFinite(B.StartHeight)||!FMath::IsFinite(B.EndHeight)||B.StartHeight<0.||B.EndHeight<0.
            ||!Finite(B.BodyHalfExtent)||B.BodyHalfExtent.X<=0.||B.BodyHalfExtent.Y<=0.
            ||B.DirectInvulnerabilityIntervals.Num()>4096||B.MotionSegments.Num()>65536)return false;
        if(B.EntityId==State().EntityId){if(B.Fighter!=Owner)return false;HasOwner=true;}
        for(int32 J=0;J<I;++J)if(F.Bodies[J].EntityId==B.EntityId||F.Bodies[J].Fighter==B.Fighter)return false;
        for(const auto& IFrame:B.DirectInvulnerabilityIntervals)
            if(!FMath::IsFinite(IFrame.Start)||!FMath::IsFinite(IFrame.EndExclusive)||IFrame.Start<0.||IFrame.EndExclusive<=IFrame.Start)return false;
        double Last=-1.;for(const auto& M:B.MotionSegments)
        {
            if(!FMath::IsFinite(M.FromTime)||!FMath::IsFinite(M.ToTime)||M.FromTime<0.
                ||(M.FromTime<M.ToTime&&M.FromTime<Last)||M.FromTime>M.ToTime||!Finite(M.From)||!Finite(M.To)
                ||!FMath::IsFinite(M.FromHeight)||!FMath::IsFinite(M.ToHeight)||M.FromHeight<0.||M.ToHeight<0.)return false;
            Last=M.ToTime;
        }
    }
    return HasOwner&&(!F.Target.IsValid()||TargetBody(F)!=nullptr);
}
bool FDungeonStoneGuardDriver::HasLineOfSight(FVector2D From,FVector2D To) const
{
    if(!Owner.IsValid()||!Owner->GetWorld()||!Finite(From)||!Finite(To))return false;
    FCollisionQueryParams Params(SCENE_QUERY_STAT(StoneGuardLOS),false);Params.AddIgnoredActor(Owner.Get());
    TArray<FHitResult> Hits;Owner->GetWorld()->LineTraceMultiByObjectType(Hits,{From.X,From.Y,0},{To.X,To.Y,0},WallObjects(),Params);
    for(const auto& H:Hits)if(H.bBlockingHit&&FMath::Abs(H.ImpactNormal.Z)<.5)return false;
    return true;
}
Guard::FSweepResult FDungeonStoneGuardDriver::QuerySweep(const Guard::FSweepRequest& Q,const FDungeonKnightFrame& F) const
{
    if(!ValidFrame(F)||!Finite(XY(Q.From))||!Finite(XY(Q.To))||Q.From.Z!=0.||Q.To.Z!=0.
        ||!FMath::IsFinite(Q.FromTime)||!FMath::IsFinite(Q.ToTime)||Q.FromTime<F.FromTime||Q.ToTime>F.ToTime||Q.FromTime>Q.ToTime
        ||Q.BodyHalfX!=40.||Q.BodyHalfY!=28.)return {false,0,Guard::EStop::None};
    Guard::FSweepResult Best;double Raw=1.;int Priority=-1;
    const auto Consider=[&](double At,Guard::EStop Stop,int P,double Safe)
    {
        if(!FMath::IsFinite(At)||At<0.||At>1.)return;
        if(Priority<0||At<Raw||(At==Raw&&P>Priority)){Raw=At;Priority=P;Best={true,Safe,Stop};}
        else if(At==Raw&&P==Priority)Best.Fraction=FMath::Min(Best.Fraction,Safe);
    };
    const auto From=XY(Q.From),To=XY(Q.To),D=To-From;
    if(F.bUseCenterBounds)
    {
        if(!F.CenterBounds.IsInsideOrOn(From))Consider(0.,Guard::EStop::Wall,1,0.);
        if(To.X<F.CenterBounds.Min.X&&D.X<0.){const double A=(F.CenterBounds.Min.X-From.X)/D.X;Consider(A,Guard::EStop::Wall,1,A);}
        if(To.X>F.CenterBounds.Max.X&&D.X>0.){const double A=(F.CenterBounds.Max.X-From.X)/D.X;Consider(A,Guard::EStop::Wall,1,A);}
        if(To.Y<F.CenterBounds.Min.Y&&D.Y<0.){const double A=(F.CenterBounds.Min.Y-From.Y)/D.Y;Consider(A,Guard::EStop::Wall,1,A);}
        if(To.Y>F.CenterBounds.Max.Y&&D.Y>0.){const double A=(F.CenterBounds.Max.Y-From.Y)/D.Y;Consider(A,Guard::EStop::Wall,1,A);}
    }
    FCollisionQueryParams Params(SCENE_QUERY_STAT(StoneGuardBodySweep),false);Params.AddIgnoredActor(Owner.Get());
    // Bodies below are queried against frozen trajectories, never their final native pose twice.
    for(const auto& B:F.Bodies)if(B.Fighter.IsValid())Params.AddIgnoredActor(B.Fighter.Get());
    TArray<FHitResult> Hits;Owner->GetWorld()->SweepMultiByObjectType(Hits,{From.X,From.Y,0},{To.X,To.Y,0},FQuat::Identity,
        WallObjects(),FCollisionShape::MakeBox(FVector(40.,28.,1.)),Params);
    for(const auto& H:Hits)if(H.bBlockingHit&&FMath::Abs(H.ImpactNormal.Z)<.5)Consider(H.Time,Guard::EStop::Wall,1,H.Time);
    for(const auto& B:F.Bodies)
    {
        if(!B.bAlive||B.Fighter==Owner||(!B.bBlocksBody&&!B.Fighter->GetStoneBatDriver()))continue;
        for(const auto& Slice:Slices(B,Q.FromTime,Q.ToTime))
        {
            const double A=Slice.Key,Z=Slice.Value;
            const auto Fraction=[&](double At){return Q.ToTime>Q.FromTime?(At-Q.FromTime)/(Q.ToTime-Q.FromTime):1.;};
            const auto K0=FMath::Lerp(From,To,Fraction(A)),K1=FMath::Lerp(From,To,Fraction(Z));
            const auto R0=PositionAt(B,F,A)-K0,R1=PositionAt(B,F,Z)-K1,Extent=B.BodyHalfExtent+FVector2D(40.,28.);
            double Entry=0.,Exit=1.;if(!BodyContact(R0,R1,Extent,Entry,Exit))continue;
            double HeightEntry=0.;
            if(B.Fighter->GetStoneBatDriver())
            {
                if(!Clip(HeightAt(B,F,A),HeightAt(B,F,Z),0.,40.,HeightEntry,Exit))continue;
                Entry=FMath::Max(Entry,HeightEntry);if(Entry>Exit)continue;
            }
            const double Contact=Fraction(A+(Z-A)*Entry),Admission=Fraction(A+(Z-A)*HeightEntry);
            const auto RelativeAt=[&](double V)
            {
                const double At=Q.FromTime+(Q.ToTime-Q.FromTime)*V;
                const FVector2D P=V==1.?To:FVector2D(From.X+(To.X-From.X)*V,From.Y+(To.Y-From.Y)*V);
                return PositionAt(B,F,At)-P;
            };
            const double Safe=DungeonContactGeometry::ConservativeBodyFraction(Admission,Contact,RelativeAt(Admission),R1,Extent,RelativeAt);
            Consider(Contact,Guard::EStop::Body,0,Safe);
        }
    }
    return Best;
}
Guard::FWorldInput FDungeonStoneGuardDriver::InputAt(const FDungeonKnightFrame& F,double At,TArray<FDungeonMotionSegment>* Motion) const
{
    Guard::FWorldInput W;W.CanBeginWake=F.bCanBeginWake;W.CanStartAttack=F.bCanStartAttack;
    if(const auto B=TargetBody(F))
    {
        const auto P=PositionAt(*B,F,At);W.HasTarget=true;W.TargetAlive=B->bAlive;W.Target={P.X,P.Y,HeightAt(*B,F,At)};
        W.LOS=HasLineOfSight(XY(State().Position),P);
    }
    W.Sweep=[this,&F,Motion](const Guard::FSweepRequest& Q)
    {
        const auto R=QuerySweep(Q,F);
        if(Motion&&R.Accepted)
        {
            const double End=R.Fraction==1.?Q.ToTime:Q.FromTime+(Q.ToTime-Q.FromTime)*R.Fraction;
            const auto P=R.Fraction==1.?XY(Q.To):FVector2D(Q.From.X+(Q.To.X-Q.From.X)*R.Fraction,Q.From.Y+(Q.To.Y-Q.From.Y)*R.Fraction);
            if(End>Q.FromTime)Motion->Add({Q.FromTime,End,XY(Q.From),P,0.,0.,false});
            if(End<Q.ToTime)Motion->Add({End,Q.ToTime,P,P,0.,0.,false});
        }
        return R;
    };
    return W;
}
FDungeonGuardBatch FDungeonStoneGuardDriver::StepTo(double Now,const FDungeonKnightFrame& Frame,const std::vector<Guard::FIncomingHit>& Hits)
{
    if(!ValidFrame(Frame)||!FMath::IsFinite(Now)||Frame.FromTime!=State().Time||Frame.ToTime!=Now||Hits.size()>65536)return {};
    double Last=Frame.FromTime;uint64 Receipt=State().LastDamageReceiptId;
    for(const auto& H:Hits)
    {
        if(!H.ReceiptId||H.ReceiptId<=Receipt||!FMath::IsFinite(H.AtTime)||H.AtTime<Last||H.AtTime>Now
            ||!FMath::IsFinite(H.HPLoss)||H.HPLoss<0.||!FMath::IsFinite(H.Stagger)||H.Stagger<0.)return {};
        Last=H.AtTime;Receipt=H.ReceiptId;
    }
    auto Candidate=*this;FDungeonGuardBatch Batch;std::size_t Index=0;
    for(int32 Iteration=0;Iteration<65536;++Iteration)
    {
        const double Cursor=Candidate.State().Time;std::vector<Guard::FIncomingHit> Here;
        while(Index<Hits.size()&&Hits[Index].AtTime==Cursor)Here.push_back(Hits[Index++]);
        auto R=Candidate.Kernel.StepTo(Cursor,Candidate.InputAt(Frame,Cursor),Here);if(!R.Accepted)return {};Append(Batch,R);
        const auto Choice=Candidate.Kernel.ChooseAttack(Candidate.InputAt(Frame,Cursor));
        if(Choice!=Guard::EAttack::None)
        {
            R=Candidate.Kernel.TryStartAttack(Choice,Candidate.InputAt(Frame,Cursor));if(!R.Accepted)return {};Append(Batch,R);
        }
        for(const auto& B:Frame.Bodies)if(B.bAlive&&!B.bSameTeam&&B.Fighter!=Owner)
        {
            const auto P=PositionAt(B,Frame,Cursor);
            R=Candidate.Kernel.TryHit({B.EntityId,{P.X,P.Y,HeightAt(B,Frame,Cursor)},true,true,
                Candidate.HasLineOfSight(XY(Candidate.State().Action.LockedCenter),P),!AdmittedAt(B,Cursor)});
            if(R.Accepted)
            {
                Append(Batch,R);const auto& A=Candidate.State().Action;
                Batch.Hits.Add({B.Fighter,A.AttackId,B.EntityId,A.Damage,A.Stagger,Cursor});
            }
        }
        if(Cursor==Now){if(Index!=Hits.size())return {};Kernel=MoveTemp(Candidate.Kernel);Batch.Accepted=true;return Batch;}
        double Next=NextBoundary(Candidate.State(),Frame,Now);if(Index<Hits.size())Next=FMath::Min(Next,Hits[Index].AtTime);
        if(Candidate.State().Phase==Guard::EPhase::Dormant)if(const auto B=TargetBody(Frame))
        {
            double Entry=0.,Exit=1.;if(EllipseContact(PositionAt(*B,Frame,Cursor)-XY(Candidate.State().Position),
                PositionAt(*B,Frame,Next)-XY(Candidate.State().Position),235.,110.,Entry,Exit)&&Entry>0.)
                Next=Cursor+(Next-Cursor)*Entry;
        }
        // Preview is a value copy: no Actor location, HP, sound or reward effects.
        auto Preview=Candidate;TArray<FDungeonMotionSegment> Motion;
        const bool ObserveStart=Candidate.State().Phase==Guard::EPhase::Dormant||Candidate.State().Phase==Guard::EPhase::Idle;
        R=Preview.Kernel.StepTo(Next,Preview.InputAt(Frame,ObserveStart?Cursor:Next,&Motion));if(!R.Accepted)return {};
        for(const auto& M:Motion)if(M.ToTime>Cursor&&M.ToTime<Next)Next=M.ToTime;
        const auto& S=Candidate.State();const auto& A=S.Action;
        if(S.Phase==Guard::EPhase::Active&&A.WindowIssued&&!A.Interrupted)
        for(const auto& B:Frame.Bodies)
        {
            if(!B.bAlive||B.bSameTeam||B.Fighter==Owner)continue;
            bool Used=false;for(const auto& H:S.HitReceipts)if(H.AttackId==A.AttackId&&H.TargetId==B.EntityId)Used=true;
            if(Used)continue;
            for(const auto& Slice:Slices(B,Cursor,Next))
            {
                const double From=Slice.Key,To=Slice.Value;double Entry=0.,Exit=1.;
                const auto P0=PositionAt(B,Frame,From)-XY(A.LockedCenter),P1=PositionAt(B,Frame,To)-XY(A.LockedCenter);
                bool Geometry=false;
                if(A.Kind==Guard::EAttack::AxeSweep)
                    Geometry=Clip(P0.X*A.Facing,P1.X*A.Facing,0.,180.,Entry,Exit)&&Clip(P0.Y,P1.Y,-65.,65.,Entry,Exit);
                else Geometry=EllipseContact(P0,P1,160.,90.,Entry,Exit);
                if(!Geometry||!Clip(HeightAt(B,Frame,From)-A.LockedCenter.Z,HeightAt(B,Frame,To)-A.LockedCenter.Z,-65.,65.,Entry,Exit))continue;
                const double Begin=From+(To-From)*Entry,End=FMath::Min(From+(To-From)*Exit,std::nextafter(A.ActiveEnd,A.ActiveAt));
                double Contact=0.;if(Begin>End||!FirstAdmitted(B,Begin,End,Contact))continue;
                const auto Legal=[&](double At)
                {
                    auto Probe=Candidate;const auto Q=Probe.Kernel.StepTo(At,Probe.InputAt(Frame,At));if(!Q.Accepted)return false;
                    const auto P=PositionAt(B,Frame,At);
                    return Probe.Kernel.TryHit({B.EntityId,{P.X,P.Y,HeightAt(B,Frame,At)},true,true,
                        Probe.HasLineOfSight(XY(A.LockedCenter),P),!AdmittedAt(B,At)}).Accepted;
                };
                if(!Legal(Contact))
                {
                    // Preserve the existing native LOS/admission search policy;
                    // every accepted contact is rechecked by the real native query.
                    bool Found=false;double Blocked=Contact;
                    for(int32 J=1;J<=16;++J)
                    {
                        double Clear=0.;if(!FirstAdmitted(B,Contact+(End-Contact)*double(J)/16.,End,Clear))continue;
                        if(!Legal(Clear)){Blocked=Clear;continue;}
                        for(int32 K=0;K<64;++K){const double Mid=Blocked+(Clear-Blocked)*.5;if(Mid==Blocked||Mid==Clear)break;if(Legal(Mid))Clear=Mid;else Blocked=Mid;}
                        Contact=Clear;Found=true;break;
                    }
                    if(!Found)continue;
                }
                if(Contact>Cursor)Next=FMath::Min(Next,Contact);break;
            }
        }
        if(!(Next>Cursor))return {};
        std::vector<Guard::FIncomingHit> Endpoint;while(Index<Hits.size()&&Hits[Index].AtTime==Next)Endpoint.push_back(Hits[Index++]);
        Motion.Reset();const auto Before=Candidate.State().Position;
        R=Candidate.Kernel.StepTo(Next,Candidate.InputAt(Frame,ObserveStart?Cursor:Next,&Motion),Endpoint);if(!R.Accepted)return {};Append(Batch,R);
        const auto After=Candidate.State().Position;
        if(Motion.IsEmpty())Motion.Add({Cursor,Next,XY(Before),XY(After),0.,0.,false});
        else if(Motion.Last().ToTime<Next)Motion.Add({Motion.Last().ToTime,Next,XY(After),XY(After),0.,0.,false});
        Batch.MotionSegments.Append(Motion);
    }
    return {};
}
FDungeonGuardBatch FDungeonStoneGuardDriver::ApplyResolvedHit(double Loss,double Stagger,const FDungeonKnightFrame& Frame)
{
    if(!ValidFrame(Frame)||Frame.FromTime!=State().Time||Frame.ToTime!=State().Time
        ||State().LastDamageReceiptId==std::numeric_limits<uint64>::max()||!FMath::IsFinite(Loss)||Loss<0.
        ||!FMath::IsFinite(Stagger)||Stagger<0.)return {};
    // A direct incoming owner receipt must not consume outgoing hits while the
    // GameMode PendingDamage transaction is closed. The next central batch owns those.
    const auto R=Kernel.ApplyResolvedHit(State().LastDamageReceiptId+1,FMath::Min(Loss,State().HP),Stagger,InputAt(Frame,State().Time));
    FDungeonGuardBatch B;B.Accepted=R.Accepted;B.Events=R.Events;return B;
}
