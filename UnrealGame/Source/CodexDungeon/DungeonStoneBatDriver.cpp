#include "DungeonStoneBatDriver.h"
#include "DungeonFighter.h"
#include "CollisionQueryParams.h"
#include "CollisionShape.h"
#include "Components/PrimitiveComponent.h"
#include "Components/BoxComponent.h"
#include "Engine/World.h"
#include "EngineUtils.h"
#include <cmath>

using BatPoint=DungeonStoneBat::FPoint;
using BatState=DungeonStoneBat::FState;
using BatPhase=DungeonStoneBat::EPhase;
using BatAttack=DungeonStoneBat::EAttack;
using BatStop=DungeonStoneBat::EStop;
using BatSweep=DungeonStoneBat::FSweepResult;
using BatSweepRequest=DungeonStoneBat::FSweepRequest;
using BatLowRequest=DungeonStoneBat::FLowPointRequest;
using BatNearest=DungeonStoneBat::FNearestLowResult;
using BatWorld=DungeonStoneBat::FWorldInput;
using BatIncoming=DungeonStoneBat::FIncomingHit;
using BatResult=DungeonStoneBat::FResult;
namespace
{
FVector2D BatXY(BatPoint P){return {P.X,P.Y};}
double BatAlpha(const FDungeonKnightFrame& F,double At){return F.ToTime>F.FromTime?FMath::Clamp((At-F.FromTime)/(F.ToTime-F.FromTime),0.,1.):1.;}
FVector2D BatPositionAt(const FDungeonKnightBody& B,const FDungeonKnightFrame& F,double At)
{
    for(int32 I=B.MotionSegments.Num()-1;I>=0;--I){const auto& M=B.MotionSegments[I];
        if(At>=M.FromTime&&(At<M.ToTime||(!M.bEndExclusive&&At==M.ToTime)))return FMath::Lerp(M.From,M.To,M.ToTime>M.FromTime?(At-M.FromTime)/(M.ToTime-M.FromTime):1.);}
    return FMath::Lerp(B.Start,B.End,BatAlpha(F,At));
}
double BatHeightAt(const FDungeonKnightBody& B,const FDungeonKnightFrame& F,double At)
{
    for(int32 I=B.MotionSegments.Num()-1;I>=0;--I){const auto& M=B.MotionSegments[I];
        if(At>=M.FromTime&&(At<M.ToTime||(!M.bEndExclusive&&At==M.ToTime)))return FMath::Lerp(M.FromHeight,M.ToHeight,M.ToTime>M.FromTime?(At-M.FromTime)/(M.ToTime-M.FromTime):1.);}
    return FMath::Lerp(B.StartHeight,B.EndHeight,BatAlpha(F,At));
}
const FDungeonKnightBody* BatTargetBody(const FDungeonKnightFrame& F){for(const auto& B:F.Bodies)if(B.Fighter==F.Target)return &B;return nullptr;}
FCollisionObjectQueryParams BatWallObjects(){FCollisionObjectQueryParams O;O.AddObjectTypesToQuery(ECC_WorldStatic);O.AddObjectTypesToQuery(ECC_WorldDynamic);return O;}
bool BatClip(double A,double Z,double Low,double High,double& Entry,double& Exit)
{
    if(A==Z)return A>=Low&&A<=High;double P=(Low-A)/(Z-A),Q=(High-A)/(Z-A);if(P>Q)Swap(P,Q);
    Entry=FMath::Max(Entry,P);Exit=FMath::Min(Exit,Q);return Entry<=Exit&&Entry<=1.&&Exit>=0.;
}
bool BatEllipse(FVector2D P0,FVector2D P1,double RX,double RY,double& Entry,double& Exit)
{
    const FVector2D P(P0.X/RX,P0.Y/RY),D((P1.X-P0.X)/RX,(P1.Y-P0.Y)/RY);
    const double A=D.SizeSquared(),B=2.*FVector2D::DotProduct(P,D),C=P.SizeSquared()-1.;
    if(A==0.)return C<=0.;const double Disc=B*B-4.*A*C;if(Disc<0.)return false;
    const double Root=FMath::Sqrt(Disc);Entry=FMath::Max(Entry,(-B-Root)/(2.*A));Exit=FMath::Min(Exit,(-B+Root)/(2.*A));return Entry<=Exit&&Entry<=1.&&Exit>=0.;
}
bool BatAdmittedAt(const FDungeonKnightBody& B,double At)
{if(!B.bUseTimedDamageAdmission)return B.bCanTakeDamage;for(const auto& I:B.DirectInvulnerabilityIntervals)if(At>=I.Start&&At<I.EndExclusive)return false;return true;}
bool BatGroundedAt(const FDungeonKnightBody& B,const FDungeonKnightFrame& F,double At)
{return BatHeightAt(B,F,At)==0.&&!(At==F.FromTime&&B.Fighter.IsValid()&&B.Fighter->GetVerticalVelocity()>0.f);}
BatPoint BatMotionAt(const TArray<FDungeonMotionSegment>& Segments,BatPoint Before,BatPoint After,double From,double To,double At)
{
    for(int32 I=Segments.Num()-1;I>=0;--I){const auto& M=Segments[I];if(At>=M.FromTime&&At<=M.ToTime){const double T=M.ToTime>M.FromTime?(At-M.FromTime)/(M.ToTime-M.FromTime):1.;
        const auto P=FMath::Lerp(M.From,M.To,T);return {P.X,P.Y,FMath::Lerp(M.FromHeight,M.ToHeight,T)};}}
    const double T=To>From?(At-From)/(To-From):1.;return {FMath::Lerp(Before.X,After.X,T),FMath::Lerp(Before.Y,After.Y,T),FMath::Lerp(Before.Z,After.Z,T)};
}
double BatNextBoundary(const BatState& S,double Limit)
{
    const auto Bound=[&](double At){if(At>S.Time)Limit=FMath::Min(Limit,At);};
    if(!S.Awakened&&S.WakeStartedAt>=0.)Bound(S.WakeEnd);if(S.Phase==BatPhase::Dormant&&S.CombatStartedAt>=0.)Bound(S.CombatStartedAt+12.);
    if(S.Phase==BatPhase::Stunned)Bound(S.StunUntil);if(S.PendingLow&&S.LowStartedAt>=0.)Bound(S.LowReadyAt);
    if(S.Phase==BatPhase::HighIdle&&S.HighIdleEligibleSince>=0.)Bound(S.HighIdleEligibleSince+2.4);
    const auto& A=S.Action;if(S.Phase==BatPhase::Windup){Bound(A.LockAt);Bound(A.ActiveAt);}if(S.Phase==BatPhase::Active||S.Phase==BatPhase::SeekingLow)Bound(A.ActiveEnd);
    const auto Heights=[&](BatPoint From,BatPoint To,double Start,double End)
    {if(From.Z!=To.Z)for(double Z:{65.,40.,20.,90.})if(Z>=FMath::Min(From.Z,To.Z)&&Z<=FMath::Max(From.Z,To.Z))Bound(Start+(End-Start)*(Z-From.Z)/(To.Z-From.Z));};
    if(S.Phase==BatPhase::Active&&A.Kind==BatAttack::Peck&&!A.PathBlocked)Heights(A.Origin,A.Endpoint,A.ActiveAt,A.ActiveEnd);
    if(S.Phase==BatPhase::Windup&&A.Locked&&A.Kind==BatAttack::Wing&&!A.PathBlocked)Heights(A.Origin,A.Endpoint,A.LockAt,A.ActiveAt);
    if(S.Phase==BatPhase::Rising){auto Goal=S.RiseOrigin;Goal.Z=90.;const double End=S.RiseStartedAt+(90.-S.RiseOrigin.Z)/(70./.3);Bound(End);Heights(S.RiseOrigin,Goal,S.RiseStartedAt,End);}
    return Limit;
}
}

FDungeonStoneBatDriver::FDungeonStoneBatDriver(ADungeonFighter* InOwner,uint64 EntityId,double StartTime)
    :Owner(InOwner),Kernel(EntityId,StartTime,{InOwner->GetGroundPosition().X,InOwner->GetGroundPosition().Y,90.}) {}
FDungeonStoneBatDriver::FDungeonStoneBatDriver(ADungeonFighter* InOwner,uint64 EntityId,double InitialTime,
    DungeonStoneBat::FPoint InitialPosition)
    :Owner(InOwner),Kernel(EntityId,InitialTime,InitialPosition) {}
bool FDungeonStoneBatDriver::Restore(const DungeonStoneBat::FState& Saved)
{
    return Kernel.Restore(Saved);
}
bool FDungeonStoneBatDriver::BeginCombat(){return Kernel.BeginCombat();}
bool FDungeonStoneBatDriver::NotifyOtherAcceptedEnemiesCleared(){return Kernel.NotifyOtherAcceptedEnemiesCleared();}
bool FDungeonStoneBatDriver::ClaimDeathReward(){return Kernel.ClaimDeathReward().Accepted;}
bool FDungeonStoneBatDriver::ValidFrame(const FDungeonKnightFrame& F) const
{
    if(!Owner.IsValid()||!Owner->GetWorld()||!FMath::IsFinite(F.FromTime)||!FMath::IsFinite(F.ToTime)||F.FromTime<0.||F.FromTime>F.ToTime)return false;
    if(F.bUseCenterBounds&&(!F.CenterBounds.bIsValid||!FMath::IsFinite(F.CenterBounds.Min.X)||!FMath::IsFinite(F.CenterBounds.Min.Y)
        ||!FMath::IsFinite(F.CenterBounds.Max.X)||!FMath::IsFinite(F.CenterBounds.Max.Y)||F.CenterBounds.Min.X>F.CenterBounds.Max.X||F.CenterBounds.Min.Y>F.CenterBounds.Max.Y))return false;
    for(int32 I=0;I<F.Bodies.Num();++I){const auto& B=F.Bodies[I];if(!B.EntityId||!B.Fighter.IsValid()||!FMath::IsFinite(B.Start.X)||!FMath::IsFinite(B.Start.Y)
        ||!FMath::IsFinite(B.End.X)||!FMath::IsFinite(B.End.Y)||!FMath::IsFinite(B.StartHeight)||!FMath::IsFinite(B.EndHeight)||B.StartHeight<0.||B.EndHeight<0.
        ||!FMath::IsFinite(B.BodyHalfExtent.X)||!FMath::IsFinite(B.BodyHalfExtent.Y)||B.BodyHalfExtent.X<=0.||B.BodyHalfExtent.Y<=0.)return false;
        for(int32 J=0;J<I;++J)if(F.Bodies[J].EntityId==B.EntityId)return false;
        for(const auto& V:B.DirectInvulnerabilityIntervals)if(!FMath::IsFinite(V.Start)||!FMath::IsFinite(V.EndExclusive)||V.Start<0.||V.Start>=V.EndExclusive)return false;
        for(const auto& M:B.MotionSegments)if(!FMath::IsFinite(M.FromTime)||!FMath::IsFinite(M.ToTime)||M.FromTime<0.||M.FromTime>M.ToTime
            ||!FMath::IsFinite(M.From.X)||!FMath::IsFinite(M.From.Y)||!FMath::IsFinite(M.To.X)||!FMath::IsFinite(M.To.Y)
            ||!FMath::IsFinite(M.FromHeight)||!FMath::IsFinite(M.ToHeight)||M.FromHeight<0.||M.ToHeight<0.)return false;}
    return !F.Target.IsValid()||BatTargetBody(F)!=nullptr;
}
bool FDungeonStoneBatDriver::HasLineOfSight(FVector2D From,FVector2D To) const
{
    if(!Owner.IsValid()||!Owner->GetWorld())return false;FCollisionQueryParams Q(SCENE_QUERY_STAT(StoneBatLOS),false);Q.AddIgnoredActor(Owner.Get());
    TArray<FHitResult> Hits;Owner->GetWorld()->LineTraceMultiByObjectType(Hits,{From.X,From.Y,0},{To.X,To.Y,0},BatWallObjects(),Q);
    for(const auto& H:Hits)if(H.bBlockingHit&&FMath::Abs(H.ImpactNormal.Z)<.5)return false;return true;
}
BatSweep FDungeonStoneBatDriver::QuerySweep(const BatSweepRequest& Q,const FDungeonKnightFrame& F) const
{
    BatSweep R;if(!ValidFrame(F)||!FMath::IsFinite(Q.FromTime)||!FMath::IsFinite(Q.ToTime)||Q.FromTime<F.FromTime||Q.ToTime>F.ToTime||Q.ToTime<Q.FromTime
        ||!FMath::IsFinite(Q.From.X)||!FMath::IsFinite(Q.From.Y)||!FMath::IsFinite(Q.From.Z)||!FMath::IsFinite(Q.To.X)||!FMath::IsFinite(Q.To.Y)||!FMath::IsFinite(Q.To.Z))
        {R.Accepted=false;return R;}
    const auto From=BatXY(Q.From),To=BatXY(Q.To),D=To-From;double Raw=1.,Resolved=1.;bool Found=false;BatStop Stop=BatStop::None;
    const auto Consider=[&](double Fraction,BatStop Kind,double Safe=-1.)
    {if(Fraction<0.||Fraction>1.)return;if(!Found||Fraction<Raw||(Fraction==Raw&&Kind==BatStop::Wall)){Found=true;Raw=Fraction;Resolved=Safe<0.?Fraction:Safe;Stop=Kind;}};
    if(F.bUseCenterBounds){const auto& B=F.CenterBounds;if(!B.IsInsideOrOn(From))Consider(0.,BatStop::Wall);
        if(D.X>0.&&To.X>B.Max.X)Consider((B.Max.X-From.X)/D.X,BatStop::Wall);if(D.X<0.&&To.X<B.Min.X)Consider((B.Min.X-From.X)/D.X,BatStop::Wall);
        if(D.Y>0.&&To.Y>B.Max.Y)Consider((B.Max.Y-From.Y)/D.Y,BatStop::Wall);if(D.Y<0.&&To.Y<B.Min.Y)Consider((B.Min.Y-From.Y)/D.Y,BatStop::Wall);}
    FCollisionQueryParams Params(SCENE_QUERY_STAT(StoneBatSweep),false);Params.AddIgnoredActor(Owner.Get());TArray<FHitResult> Walls;
    Owner->GetWorld()->SweepMultiByObjectType(Walls,{From.X,From.Y,0},{To.X,To.Y,0},FQuat::Identity,BatWallObjects(),FCollisionShape::MakeBox(FVector(16,12,1)),Params);
    for(const auto& H:Walls)if(H.bBlockingHit&&FMath::Abs(H.ImpactNormal.Z)<.5)Consider(H.Time,BatStop::Wall);
    for(const auto& B:F.Bodies)
    {
        if(!B.bAlive||B.Fighter==Owner||(!B.bBlocksBody&&!B.Fighter->GetStoneBatDriver()))continue;
        double Begin=0.,End=1.;if(!BatClip(Q.From.Z,Q.To.Z,0.,Q.BodyThresholdZ,Begin,End))continue;
        if(B.Fighter->GetStoneBatDriver()&&!BatClip(BatHeightAt(B,F,Q.FromTime),BatHeightAt(B,F,Q.ToTime),0.,40.,Begin,End))continue;
        const double Admission=Begin;
        const auto P0=BatPositionAt(B,F,Q.FromTime)-From,P1=BatPositionAt(B,F,Q.ToTime)-To;const auto Extent=B.BodyHalfExtent+FVector2D(16,12);
        if(!BatClip(P0.X,P1.X,-Extent.X,Extent.X,Begin,End)||!BatClip(P0.Y,P1.Y,-Extent.Y,Extent.Y,Begin,End))continue;
        // A terminal face touch has no interior overlap and is a legal low anchor.
        if(Begin==1.&&!(FMath::Abs(P1.X)<Extent.X&&FMath::Abs(P1.Y)<Extent.Y))continue;
        if(Begin==0.&&FMath::Abs(P0.X)<Extent.X&&FMath::Abs(P0.Y)<Extent.Y)
        {const auto Motion=P1-P0;const bool X=Extent.X-FMath::Abs(P0.X)<=Extent.Y-FMath::Abs(P0.Y);if(X?P0.X*Motion.X>=0.:P0.Y*Motion.Y>=0.)continue;}
        else if(Begin==0.)
        {const auto Inside=FMath::Lerp(P0,P1,FMath::Min(End*.5,1.e-6));if(End<=0.||!(FMath::Abs(Inside.X)<Extent.X&&FMath::Abs(Inside.Y)<Extent.Y))continue;}
        const auto RelativeAt=[&](double T){return BatPositionAt(B,F,Q.FromTime+(Q.ToTime-Q.FromTime)*T)-(From+D*T);};
        const double Safe=DungeonContactGeometry::ConservativeBodyFraction(Admission,Begin,RelativeAt(Admission),P1,Extent,RelativeAt);
        Consider(Begin,BatStop::Body,Safe);
    }
    if(Found){R.Fraction=Resolved;R.Stop=Stop;}return R;
}
bool FDungeonStoneBatDriver::LegalLowPoint(const BatLowRequest& Q,const FDungeonKnightFrame& F) const
{
    if(Q.Candidate.Z!=20.||(F.bUseCenterBounds&&!F.CenterBounds.IsInsideOrOn(BatXY(Q.Candidate))))return false;
    for(const auto& B:F.Bodies)if(B.bAlive&&B.Fighter!=Owner&&(B.bBlocksBody||(B.Fighter->GetStoneBatDriver()&&BatHeightAt(B,F,Q.AtTime)<=40.)))
    {const auto D=BatPositionAt(B,F,Q.AtTime)-BatXY(Q.Candidate),E=B.BodyHalfExtent+FVector2D(16,12);if(FMath::Abs(D.X)<E.X&&FMath::Abs(D.Y)<E.Y)return false;}
    const auto At=QuerySweep({Q.Candidate,Q.Candidate,Q.AtTime,Q.AtTime,40,Q.Attack,false},F);if(!At.Accepted||At.Stop!=BatStop::None)return false;
    const auto Path=QuerySweep({Q.From,Q.Candidate,Q.AtTime,Q.AtTime,40,Q.Attack,false},F);return Path.Accepted&&Path.Stop==BatStop::None;
}
BatNearest FDungeonStoneBatDriver::NearestLowPoint(BatPoint From,const FDungeonKnightFrame& F) const
{
    BatNearest R;BatPoint Current=From;Current.Z=20.;
    const auto Legal=[&](BatPoint P){return LegalLowPoint({From,P,Kernel.State().Action.LockedTarget,Kernel.State().Action.Kind,Kernel.State().Time},F);};
    if(Legal(Current)){R.Found=true;R.Point=Current;return R;}
    TArray<double> Xs,Ys;Xs.Add(FMath::Clamp(From.X,F.CenterBounds.Min.X,F.CenterBounds.Max.X));Ys.Add(FMath::Clamp(From.Y,F.CenterBounds.Min.Y,F.CenterBounds.Max.Y));
    Xs.Append({F.CenterBounds.Min.X,F.CenterBounds.Max.X});Ys.Append({F.CenterBounds.Min.Y,F.CenterBounds.Max.Y});
    for(const auto& B:F.Bodies)if(B.bAlive&&B.Fighter!=Owner&&(B.bBlocksBody||(B.Fighter->GetStoneBatDriver()&&BatHeightAt(B,F,Kernel.State().Time)<=40.)))
    {const auto P=BatPositionAt(B,F,Kernel.State().Time),E=B.BodyHalfExtent+FVector2D(16,12);Xs.Append({P.X-E.X,P.X+E.X});Ys.Append({P.Y-E.Y,P.Y+E.Y});}
    // The flat room's boxes/body rectangles yield a finite closest-free-point set.
    for(TActorIterator<AActor> It(Owner->GetWorld());It;++It)if(*It!=Owner.Get()&&!Cast<ADungeonFighter>(*It))
    {TInlineComponentArray<UPrimitiveComponent*> Components(*It);for(const auto C:Components)if(C&&C->IsCollisionEnabled()&&C->IsA<UBoxComponent>())
        {const auto B=C->Bounds.GetBox();Xs.Append({B.Min.X-16.,B.Max.X+16.});Ys.Append({B.Min.Y-12.,B.Max.Y+12.});}}
    double Best=std::numeric_limits<double>::infinity();
    for(double X:Xs)for(double Y:Ys)
    {BatPoint P{X,Y,20.};const double D=FMath::Square(X-From.X)+FMath::Square(Y-From.Y);if(D>Best||!Legal(P))continue;
        if(!R.Found||D<Best||(D==Best&&(X<R.Point.X||(X==R.Point.X&&Y<R.Point.Y)))){R.Found=true;R.Point=P;Best=D;}}
    return R;
}
BatWorld FDungeonStoneBatDriver::InputAt(const FDungeonKnightFrame& F,double At,TArray<FDungeonMotionSegment>* Motion) const
{
    BatWorld W;W.CanBeginWake=F.bCanBeginWake;W.CanStartAttack=F.bCanStartAttack;
    if(const auto B=BatTargetBody(F)){const auto P=BatPositionAt(*B,F,At);W.HasTarget=true;W.TargetAlive=B->bAlive;W.Target={P.X,P.Y,BatHeightAt(*B,F,At)};W.LOS=HasLineOfSight(BatXY(Kernel.State().Position),P);}
    W.LegalLowPoint=[this,&F](const BatLowRequest& Q){return LegalLowPoint(Q,F);};W.NearestLegalLowPoint=[this,&F](BatPoint P){return NearestLowPoint(P,F);};
    W.Sweep=[this,&F,Motion](const BatSweepRequest& Q)
    {
        const auto R=QuerySweep(Q,F);if(Motion&&R.Accepted){const double End=R.Fraction==1.?Q.ToTime:Q.FromTime+(Q.ToTime-Q.FromTime)*R.Fraction;
            const BatPoint P{Q.From.X+(Q.To.X-Q.From.X)*R.Fraction,Q.From.Y+(Q.To.Y-Q.From.Y)*R.Fraction,Q.From.Z+(Q.To.Z-Q.From.Z)*R.Fraction};
            Motion->Add({Q.FromTime,End,BatXY(Q.From),BatXY(P),Q.From.Z,P.Z,false});if(End<Q.ToTime)Motion->Add({End,Q.ToTime,BatXY(P),BatXY(P),P.Z,P.Z,false});}return R;
    };
    const auto Last=Kernel.State().Action.Kind;
    W.SelectDueAttack=[Last](bool Peck,bool Wing){if(Last==BatAttack::Peck&&Wing)return BatAttack::Wing;if(Peck)return BatAttack::Peck;return Wing?BatAttack::Wing:BatAttack::None;};return W;
}
FDungeonBatBatch FDungeonStoneBatDriver::StepTo(double Now,const FDungeonKnightFrame& Frame,const std::vector<BatIncoming>& Hits)
{
    FDungeonBatBatch Batch;
    if(!ValidFrame(Frame)||Frame.FromTime!=Kernel.State().Time||Frame.ToTime!=Now||!FMath::IsFinite(Now))return Batch;
    double LastAt=Frame.FromTime;uint64 LastId=Kernel.State().LastDamageReceiptId;
    for(const auto& H:Hits){if(H.ReceiptId<=LastId||!FMath::IsFinite(H.AtTime)||H.AtTime<LastAt||H.AtTime>Now
        ||!FMath::IsFinite(H.HPLoss)||H.HPLoss<0.||!FMath::IsFinite(H.Stagger)||H.Stagger<0.)return {};LastAt=H.AtTime;LastId=H.ReceiptId;}
    auto Candidate=*this;size_t Index=0;
    const auto Append=[&Batch](const BatResult& R){Batch.Events.insert(Batch.Events.end(),R.Events.begin(),R.Events.end());};
    for(int Guard=0;Guard<65536;++Guard)
    {
        const double Cursor=Candidate.State().Time;std::vector<BatIncoming> Here;
        while(Index<Hits.size()&&Hits[Index].AtTime==Cursor)Here.push_back(Hits[Index++]);
        auto R=Candidate.Kernel.StepTo(Cursor,Candidate.InputAt(Frame,Cursor),Here);if(!R.Accepted)return {};Append(R);
        for(const auto& B:Frame.Bodies)if(B.bAlive&&!B.bSameTeam&&B.Fighter!=Owner)
        {
            const auto P=BatPositionAt(B,Frame,Cursor);R=Candidate.Kernel.TryHit(B.EntityId,{P.X,P.Y,BatHeightAt(B,Frame,Cursor)},BatGroundedAt(B,Frame,Cursor),
                Candidate.HasLineOfSight(BatXY(Candidate.State().Position),P),!BatAdmittedAt(B,Cursor));
            if(R.Accepted){Append(R);const auto& A=Candidate.State().Action;Batch.Hits.Add({B.Fighter,A.AttackId,B.EntityId,A.Damage,A.Stagger,Cursor});}
        }
        if(Cursor==Now){if(Index!=Hits.size())return {};Kernel=MoveTemp(Candidate.Kernel);Batch.Accepted=true;return Batch;}
        double Next=BatNextBoundary(Candidate.State(),Now);if(Index<Hits.size())Next=FMath::Min(Next,Hits[Index].AtTime);
        if(Candidate.State().Phase==BatPhase::Dormant)if(const auto B=BatTargetBody(Frame))
        {double Entry=0.,Exit=1.;if(BatEllipse(BatPositionAt(*B,Frame,Cursor)-BatXY(Candidate.State().Position),BatPositionAt(*B,Frame,Next)-BatXY(Candidate.State().Position),180.,85.,Entry,Exit)
            &&Entry>0.)Next=Cursor+(Next-Cursor)*Entry;}
        auto Preview=Candidate;TArray<FDungeonMotionSegment> Motion;
        const auto Sample=Candidate.State().Phase==BatPhase::Dormant||Candidate.State().Phase==BatPhase::HighIdle?Cursor:Next;
        R=Preview.Kernel.StepTo(Next,Preview.InputAt(Frame,Sample,&Motion));if(!R.Accepted)return {};
        const auto& S=Candidate.State();const auto& A=S.Action;
        if(S.Phase==BatPhase::Active&&A.Emitted&&!A.Interrupted&&!A.Missed)
        for(const auto& B:Frame.Bodies)if(B.bAlive&&!B.bSameTeam&&B.Fighter!=Owner)
        {
            bool Already=false;for(const auto& H:S.HitReceipts)Already|=H.AttackId==A.AttackId&&H.TargetId==B.EntityId;if(Already)continue;
            TArray<double> Cuts{Cursor,Next};for(const auto& M:Motion){if(M.FromTime>Cursor&&M.FromTime<Next)Cuts.Add(M.FromTime);if(M.ToTime>Cursor&&M.ToTime<Next)Cuts.Add(M.ToTime);}
            for(const auto& M:B.MotionSegments){if(M.FromTime>Cursor&&M.FromTime<Next)Cuts.Add(M.FromTime);if(M.ToTime>Cursor&&M.ToTime<Next)Cuts.Add(M.ToTime);}Cuts.Sort();
            for(int32 I=1;I<Cuts.Num();++I)
            {
                const double From=Cuts[I-1],To=Cuts[I];if(To<=From)continue;
                const auto P0=BatMotionAt(Motion,S.Position,Preview.State().Position,Cursor,Next,From),P1=BatMotionAt(Motion,S.Position,Preview.State().Position,Cursor,Next,To);
                const auto T0=BatPositionAt(B,Frame,From),T1=BatPositionAt(B,Frame,To);double Entry=0.,Exit=1.;
                if(!BatEllipse(T0-BatXY(P0),T1-BatXY(P1),A.RadiusX,A.RadiusY,Entry,Exit)
                    ||!BatClip(BatHeightAt(B,Frame,From)-P0.Z,BatHeightAt(B,Frame,To)-P1.Z,-65.,65.,Entry,Exit))continue;
                if(A.Kind==BatAttack::Peck&&BatGroundedAt(B,Frame,From)&&BatGroundedAt(B,Frame,To)&&!BatClip(P0.Z,P1.Z,0.,65.,Entry,Exit))continue;
                double Begin=From+(To-From)*Entry,End=FMath::Min(From+(To-From)*Exit,std::nextafter(A.ActiveEnd,A.ActiveAt));if(Begin>End)continue;
                const auto Legal=[&](double At)
                {auto Check=Candidate;auto Q=Check.Kernel.StepTo(At,Check.InputAt(Frame,At));if(!Q.Accepted)return false;const auto P=BatPositionAt(B,Frame,At);
                    return Check.Kernel.TryHit(B.EntityId,{P.X,P.Y,BatHeightAt(B,Frame,At)},BatGroundedAt(B,Frame,At),Check.HasLineOfSight(BatXY(Check.State().Position),P),!BatAdmittedAt(B,At)).Accepted;};
                double Contact=Begin;
                if(!Legal(Contact))
                {bool Found=false;double Blocked=Begin;for(int J=1;J<=16;++J){const double Probe=Begin+(End-Begin)*double(J)/16.;if(!Legal(Probe)){Blocked=Probe;continue;}
                    Contact=Probe;for(int K=0;K<64;++K){const double Mid=Blocked+(Contact-Blocked)*.5;if(Mid==Blocked||Mid==Contact)break;if(Legal(Mid))Contact=Mid;else Blocked=Mid;}Found=true;break;}if(!Found)continue;}
                if(Contact>Cursor)Next=FMath::Min(Next,Contact);break;
            }
        }
        if(!(Next>Cursor))return {};std::vector<BatIncoming> EndpointHits;while(Index<Hits.size()&&Hits[Index].AtTime==Next)EndpointHits.push_back(Hits[Index++]);
        Motion.Reset();const auto Observe=Candidate.State().Phase==BatPhase::Dormant||Candidate.State().Phase==BatPhase::HighIdle?Cursor:Next;
        R=Candidate.Kernel.StepTo(Next,Candidate.InputAt(Frame,Observe,&Motion),EndpointHits);if(!R.Accepted)return {};Append(R);Batch.MotionSegments.Append(Motion);
    }
    return {};
}
FDungeonBatBatch FDungeonStoneBatDriver::ApplyResolvedHit(double ActualHPLoss,double LegalStagger,const FDungeonKnightFrame& F)
{return StepTo(F.ToTime,F,{{Kernel.State().LastDamageReceiptId+1,F.ToTime,FMath::Min(Kernel.State().HP,ActualHPLoss),LegalStagger}});}
