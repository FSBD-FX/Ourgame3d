#include "DungeonStoneKnightDriver.h"
#include "DungeonFighter.h"
#include "CollisionQueryParams.h"
#include "CollisionShape.h"
#include "Engine/World.h"
#include <cmath>

namespace
{
using namespace DungeonStoneKnight;

bool FinitePoint(FVector2D P) { return FMath::IsFinite(P.X) && FMath::IsFinite(P.Y); }
FVector2D Point(FPoint P) { return {P.X,P.Y}; }
double Alpha(const FDungeonKnightFrame& F,double At)
{
    return F.ToTime>F.FromTime ? FMath::Clamp((At-F.FromTime)/(F.ToTime-F.FromTime),0.0,1.0) : 1.0;
}
FVector2D PositionAt(const FDungeonKnightBody& B,const FDungeonKnightFrame& F,double At)
{
    for (int32 I=B.MotionSegments.Num()-1;I>=0;--I)
    {
        const auto& M=B.MotionSegments[I];
        if (At>=M.FromTime && (At<M.ToTime || (!M.bEndExclusive && At==M.ToTime)))
            return FMath::Lerp(M.From,M.To,M.ToTime>M.FromTime?(At-M.FromTime)/(M.ToTime-M.FromTime):1.0);
    }
    return FMath::Lerp(B.Start,B.End,Alpha(F,At));
}
double HeightAt(const FDungeonKnightBody& B,const FDungeonKnightFrame& F,double At)
{
    for (int32 I=B.MotionSegments.Num()-1;I>=0;--I)
    {
        const auto& M=B.MotionSegments[I];
        if (At>=M.FromTime && (At<M.ToTime || (!M.bEndExclusive && At==M.ToTime)))
            return FMath::Lerp(M.FromHeight,M.ToHeight,M.ToTime>M.FromTime?(At-M.FromTime)/(M.ToTime-M.FromTime):1.0);
    }
    return FMath::Lerp(B.StartHeight,B.EndHeight,Alpha(F,At));
}
TArray<TPair<double,double>> MotionSlices(const FDungeonKnightBody& B,double Begin,double End)
{
    TArray<TPair<double,double>> Out;
    if (B.MotionSegments.IsEmpty()) { Out.Add({Begin,End}); return Out; }
    for (const auto& M:B.MotionSegments)
    {
        const double A=FMath::Max(Begin,M.FromTime);
        double Z=FMath::Min(End,M.ToTime);
        if (M.bEndExclusive && Z==M.ToTime) Z=std::nextafter(Z,A);
        if (A<=Z && !(M.bEndExclusive && A==M.ToTime)) Out.Add({A,Z});
    }
    return Out;
}
bool FirstAdmittedTime(const FDungeonKnightBody& B,double Begin,double End,double& At)
{
    if (!B.bUseTimedDamageAdmission) { At=Begin; return B.bCanTakeDamage; }
    At=Begin;
    // Intervals need not be sorted; advancing through their union is monotonic.
    for (;;)
    {
        double Next=At;
        for (const auto& I:B.DirectInvulnerabilityIntervals)
            if (At>=I.Start && At<I.EndExclusive) Next=FMath::Max(Next,I.EndExclusive);
        if (Next==At) return At<=End;
        At=Next;
        if (At>End) return false;
    }
}
template<class TVisible>
bool FirstVisibleAdmittedTime(const FDungeonKnightBody& B,double Begin,double End,TVisible Visible,double& At)
{
    if (!FirstAdmittedTime(B,Begin,End,At)) return false;
    if (Visible(At)) return true;
    double Blocked=At;
    for (int I=1;I<=16;++I)
    {
        double Probe=0;
        if (!FirstAdmittedTime(B,FMath::Lerp(At,End,double(I)/16.0),End,Probe)) continue;
        if (!Visible(Probe)) {Blocked=Probe;continue;}
        double Clear=Probe;
        for (int J=0;J<48;++J)
        {
            const double Mid=(Blocked+Clear)*.5;if (Mid==Blocked||Mid==Clear) break;
            double Legal=0;
            if (FirstAdmittedTime(B,Mid,Clear,Legal)&&Visible(Legal)) Clear=Legal;else Blocked=Mid;
        }
        At=Clear;return true;
    }
    return false;
}
const FDungeonKnightBody* TargetBody(const FDungeonKnightFrame& F)
{
    for (const auto& B:F.Bodies) if (B.Fighter==F.Target) return &B;
    return nullptr;
}
bool Clip(double P0,double P1,double Low,double High,double& Entry,double& Exit)
{
    const double D=P1-P0;
    if (D==0) return P0>=Low && P0<=High;
    double A=(Low-P0)/D,B=(High-P0)/D;
    if (A>B) Swap(A,B);
    Entry=FMath::Max(Entry,A); Exit=FMath::Min(Exit,B);
    return Entry<=Exit && Entry<=1 && Exit>=0;
}
bool RectangleContact(FVector2D R0,FVector2D R1,FVector2D Axis,double Front,double HalfY,
    double H0,double H1,double HeightCenter,double HeightTolerance,double& Entry,double& Exit)
{
    const FVector2D Side(-Axis.Y,Axis.X); Exit=1; Entry=0;
    return Clip(FVector2D::DotProduct(R0,Axis),FVector2D::DotProduct(R1,Axis),0,Front,Entry,Exit)
        && Clip(FVector2D::DotProduct(R0,Side),FVector2D::DotProduct(R1,Side),-HalfY,HalfY,Entry,Exit)
        && Clip(H0,H1,HeightCenter-HeightTolerance,HeightCenter+HeightTolerance,Entry,Exit);
}
bool BodyContact(FVector2D R0,FVector2D R1,FVector2D Extent,double& Entry)
{
    double Exit=1; Entry=0;
    if (!Clip(R0.X,R1.X,-Extent.X,Extent.X,Entry,Exit)
        || !Clip(R0.Y,R1.Y,-Extent.Y,Extent.Y,Entry,Exit)) return false;
    // Touching while moving away or sliding along an edge is not penetration.
    if (Entry==0 && FMath::Abs(R0.X)<Extent.X && FMath::Abs(R0.Y)<Extent.Y)
    {
        const auto Motion=R1-R0;
        const bool NearestX=Extent.X-FMath::Abs(R0.X)<=Extent.Y-FMath::Abs(R0.Y);
        if (NearestX ? R0.X*Motion.X>=0.0 : R0.Y*Motion.Y>=0.0) return false;
    }
    else if (Entry==0)
    {
        if (Exit<=0) return false;
        const auto Inside=FMath::Lerp(R0,R1,FMath::Min(Exit*.5,1.e-6));
        if (!(FMath::Abs(Inside.X)<Extent.X && FMath::Abs(Inside.Y)<Extent.Y)) return false;
    }
    return true;
}
FCollisionObjectQueryParams WallObjects()
{
    FCollisionObjectQueryParams Objects;
    Objects.AddObjectTypesToQuery(ECC_WorldStatic);
    Objects.AddObjectTypesToQuery(ECC_WorldDynamic);
    return Objects;
}
void Append(FDungeonKnightBatch& Batch,const FResult& R)
{
    Batch.Events.insert(Batch.Events.end(),R.Events.begin(),R.Events.end());
}
}

FDungeonStoneKnightDriver::FDungeonStoneKnightDriver(ADungeonFighter* InOwner, uint64 EntityId, double StartTime)
    : Owner(InOwner), Kernel(EntityId, StartTime, InOwner
        ? DungeonStoneKnight::FPoint{InOwner->GetGroundPosition().X, InOwner->GetGroundPosition().Y}
        : DungeonStoneKnight::FPoint{}) {}

bool FDungeonStoneKnightDriver::Restore(const FState& Saved) { return Kernel.Restore(Saved); }
bool FDungeonStoneKnightDriver::BeginCombat() { return Kernel.BeginCombat(); }
bool FDungeonStoneKnightDriver::NotifyOtherAcceptedEnemiesCleared() { return Kernel.NotifyOtherAcceptedEnemiesCleared(); }
bool FDungeonStoneKnightDriver::ClaimDeathReward() { return Kernel.ClaimDeathReward(); }

bool FDungeonStoneKnightDriver::ValidFrame(const FDungeonKnightFrame& F) const
{
    if (!Owner.IsValid() || !Owner->GetWorld() || !FMath::IsFinite(F.FromTime) || !FMath::IsFinite(F.ToTime)
        || F.FromTime<0 || F.ToTime<F.FromTime) return false;
    if (F.bUseCenterBounds && (!F.CenterBounds.bIsValid || !FinitePoint(F.CenterBounds.Min)
        || !FinitePoint(F.CenterBounds.Max) || F.CenterBounds.Min.X>F.CenterBounds.Max.X || F.CenterBounds.Min.Y>F.CenterBounds.Max.Y)) return false;
    for (int32 I=0;I<F.Bodies.Num();++I)
    {
        const auto& B=F.Bodies[I];
        if (!B.EntityId || (B.bAlive&&!B.Fighter.IsValid()) || !FinitePoint(B.Start) || !FinitePoint(B.End)
            || !FinitePoint(B.BodyHalfExtent) || B.BodyHalfExtent.X<=0 || B.BodyHalfExtent.Y<=0
            || !FMath::IsFinite(B.StartHeight) || !FMath::IsFinite(B.EndHeight)) return false;
        for (int32 J=0;J<I;++J) if (F.Bodies[J].EntityId==B.EntityId) return false;
        for (const auto& V:B.DirectInvulnerabilityIntervals)
            if (!FMath::IsFinite(V.Start)||!FMath::IsFinite(V.EndExclusive)||V.Start<0||V.EndExclusive<=V.Start) return false;
        for (const auto& M:B.MotionSegments)
            if (!FMath::IsFinite(M.FromTime)||!FMath::IsFinite(M.ToTime)||M.FromTime<F.FromTime||M.ToTime>F.ToTime||M.FromTime>M.ToTime
                ||!FinitePoint(M.From)||!FinitePoint(M.To)||!FMath::IsFinite(M.FromHeight)||!FMath::IsFinite(M.ToHeight)) return false;
    }
    return !F.Target.IsValid() || TargetBody(F)!=nullptr;
}

bool FDungeonStoneKnightDriver::HasLineOfSight(FVector2D From,FVector2D To) const
{
    if (!Owner.IsValid() || !Owner->GetWorld()) return false;
    FCollisionQueryParams Params(SCENE_QUERY_STAT(StoneKnightDriverLOS),false);
    Params.AddIgnoredActor(Owner.Get());
    return !Owner->GetWorld()->LineTraceTestByObjectType(FVector(From.X,From.Y,0),FVector(To.X,To.Y,0),WallObjects(),Params);
}

FWorldInput FDungeonStoneKnightDriver::InputAt(const FDungeonKnightFrame& F,double At) const
{
    FWorldInput W; W.CanStartAttack=F.bCanStartAttack; W.CanBeginWake=F.bCanBeginWake;
    if (const auto* B=TargetBody(F))
    {
        const auto P=PositionAt(*B,F,At); W.HasTarget=B->Fighter.IsValid(); W.TargetAlive=B->bAlive;
        W.Target={P.X,P.Y}; W.TargetZ=HeightAt(*B,F,At); W.LOS=HasLineOfSight(Point(Kernel.State().Position),P);
    }
    W.Sweep=[this,&F](const FSweepRequest& Q){return QuerySweep(Q,F);};
    return W;
}

FSweepResult FDungeonStoneKnightDriver::QuerySweep(const FSweepRequest& Q,const FDungeonKnightFrame& F) const
{
    if (!ValidFrame(F) || !FinitePoint(Point(Q.From)) || !FinitePoint(Point(Q.To))
        || !FMath::IsFinite(Q.FromTime) || !FMath::IsFinite(Q.ToTime) || Q.FromTime<F.FromTime || Q.ToTime>F.ToTime || Q.ToTime<Q.FromTime)
        return {0,EStop::Wall,0}; // Invalid observations cannot authorize movement or damage.
    FSweepResult Best; bool Found=false; int32 BestPriority=-1; double BestResolvedFraction=1.0;
    const auto Consider=[&Best,&Found,&BestPriority,&BestResolvedFraction](double Fraction,EStop Stop,uint64 Target,int32 Priority,double ResolvedFraction=-1.0)
    {
        if (Fraction<0 || Fraction>1) return;
        if (!Found || Fraction<Best.Fraction || (Fraction==Best.Fraction && Priority>BestPriority))
        { Best={Fraction,Stop,Target}; Found=true; BestPriority=Priority;BestResolvedFraction=ResolvedFraction>=0.0?ResolvedFraction:Fraction; }
        else if (Fraction==Best.Fraction && Stop==EStop::Body && Best.Stop==EStop::Body && ResolvedFraction>=0.0)
            BestResolvedFraction=FMath::Min(BestResolvedFraction,ResolvedFraction);
    };
    const auto From=Point(Q.From),To=Point(Q.To),Delta=To-From;
    if (F.bUseCenterBounds)
    {
        if (From.X<F.CenterBounds.Min.X || From.X>F.CenterBounds.Max.X || From.Y<F.CenterBounds.Min.Y || From.Y>F.CenterBounds.Max.Y) Consider(0,EStop::Wall,0,1);
        if (To.X<F.CenterBounds.Min.X && Delta.X<0) Consider((F.CenterBounds.Min.X-From.X)/Delta.X,EStop::Wall,0,1);
        if (To.X>F.CenterBounds.Max.X && Delta.X>0) Consider((F.CenterBounds.Max.X-From.X)/Delta.X,EStop::Wall,0,1);
        if (To.Y<F.CenterBounds.Min.Y && Delta.Y<0) Consider((F.CenterBounds.Min.Y-From.Y)/Delta.Y,EStop::Wall,0,1);
        if (To.Y>F.CenterBounds.Max.Y && Delta.Y>0) Consider((F.CenterBounds.Max.Y-From.Y)/Delta.Y,EStop::Wall,0,1);
    }
    FCollisionQueryParams Params(SCENE_QUERY_STAT(StoneKnightDriverSweep),false); Params.AddIgnoredActor(Owner.Get());
    TArray<FHitResult> Walls;
    Owner->GetWorld()->SweepMultiByObjectType(Walls,FVector(From.X,From.Y,0),FVector(To.X,To.Y,0),FQuat::Identity,
        WallObjects(),FCollisionShape::MakeBox(FVector(Q.BodyHalfX,Q.BodyHalfY,1)),Params);
    for (const auto& Wall:Walls)
        if (Wall.bBlockingHit && FMath::Abs(Wall.ImpactNormal.Z)<.5) Consider(Wall.Time,EStop::Wall,0,1);
    for (const auto& B:F.Bodies)
    {
        if (!B.bAlive || !B.Fighter.IsValid() || B.Fighter==Owner || B.EntityId==Kernel.State().EntityId) continue;
        for (const auto& Slice:MotionSlices(B,Q.FromTime,Q.ToTime))
        {
            const double A=Slice.Key,Z=Slice.Value;
            const auto FractionAt=[&Q](double T){return Q.ToTime>Q.FromTime?(T-Q.FromTime)/(Q.ToTime-Q.FromTime):1.0;};
            const auto K0=FMath::Lerp(From,To,FractionAt(A)),K1=FMath::Lerp(From,To,FractionAt(Z));
            const auto R0=PositionAt(B,F,A)-K0,R1=PositionAt(B,F,Z)-K1;
            double Entry=0,Exit=1;
            const auto Extent=B.BodyHalfExtent+FVector2D(Q.BodyHalfX,Q.BodyHalfY);
            bool BodyAdmitted=B.bBlocksBody&&BodyContact(R0,R1,Extent,Entry);
            double HeightEntry=0.,HeightExit=1.;
            if(BodyAdmitted&&B.Fighter->GetStoneBatDriver())
            {
                BodyAdmitted=Clip(HeightAt(B,F,A),HeightAt(B,F,Z),0.,40.,HeightEntry,HeightExit)
                    &&Clip(R0.X,R1.X,-Extent.X,Extent.X,Entry,HeightExit)&&Clip(R0.Y,R1.Y,-Extent.Y,Extent.Y,Entry,HeightExit);
                Entry=FMath::Max(Entry,HeightEntry);BodyAdmitted=BodyAdmitted&&Entry<=HeightExit;
            }
            if(BodyAdmitted)
            {
                const double RawFraction=FractionAt(FMath::Lerp(A,Z,Entry));
                const auto RelativeAt=[&B,&F,&Q,&From,&To](double Fraction)
                    {
                        const double At=Q.FromTime+(Q.ToTime-Q.FromTime)*Fraction;
                        // Exactly FKnightKernel::Move's reconstruction, not a separately pushed Actor.
                        const FVector2D Knight(From.X+(To.X-From.X)*Fraction,From.Y+(To.Y-From.Y)*Fraction);
                        return PositionAt(B,F,At)-Knight;
                    };
                // Conservative XY rounding cannot retreat before the actual
                // height admission and turn a future low body into a high one.
                const double Admission=FractionAt(FMath::Lerp(A,Z,HeightEntry));
                const auto AdmittedRelative=B.Fighter->GetStoneBatDriver()?RelativeAt(Admission):R0;
                const double SafeFraction=DungeonContactGeometry::ConservativeBodyFraction(Admission,RawFraction,AdmittedRelative,R1,Extent,RelativeAt);
                Consider(RawFraction,EStop::Body,0,0,SafeFraction);
            }
            if (Q.Charge && !B.bSameTeam && RectangleContact(R0,R1,Point(Q.Action.Direction),Q.FrontReach,Q.HalfDepth,
                HeightAt(B,F,A),HeightAt(B,F,Z),Q.HeightCenter,Q.HeightTolerance,Entry,Exit))
            {
                double At=0;
                if (FirstVisibleAdmittedTime(B,FMath::Lerp(A,Z,Entry),FMath::Lerp(A,Z,Exit),
                    [this,&From,&To,&FractionAt,&B,&F](double T){return HasLineOfSight(FMath::Lerp(From,To,FractionAt(T)),PositionAt(B,F,T));},At))
                    Consider(FractionAt(At),EStop::ValidHit,B.EntityId,2);
            }
        }
    }
    // Select by raw geometry first (valid hit > wall > body at equal contact).
    // Only the selected stop is rounded conservatively; time and position share it.
    if (Found) Best.Fraction=BestResolvedFraction;
    return Best;
}

void FDungeonStoneKnightDriver::CollectHits(const FDungeonKnightFrame& F,double From,double To,FDungeonKnightBatch& Batch)
{
    // Charge hits are already accepted by the kernel after its read-only query.
    for (const auto& E:Batch.Events)
    {
        if (E.Kind!=EEventKind::Hit || E.AtTime<From || E.AtTime>To) continue;
        bool Existing=false; for (const auto& H:Batch.Hits) Existing|=H.AttackId==E.Action.AttackId && H.TargetId==E.TargetId;
        if (Existing) continue;
        for (const auto& B:F.Bodies) if (B.EntityId==E.TargetId)
        { Batch.Hits.Add({B.Fighter,E.Action.AttackId,E.TargetId,E.Action.Damage,E.Action.Stagger,E.AtTime}); break; }
    }
    for (const auto& W:Kernel.State().ActiveReceipts)
    {
        const auto& A=W.FrozenAction;
        if (A.Kind!=EAttack::Shield) continue;
        const double Begin=FMath::Max(From,A.ActiveAt),End=FMath::Min(To,W.End);
        if (Begin>End || Begin>=W.End) continue;
        for (const auto& B:F.Bodies)
        {
            if (!B.bAlive || !B.Fighter.IsValid() || B.bSameTeam || B.Fighter==Owner) continue;
            for (const auto& Slice:MotionSlices(B,Begin,End))
            {
                double Entry=0,Exit=1,At=0;
                if (!RectangleContact(PositionAt(B,F,Slice.Key)-Point(A.Origin),PositionAt(B,F,Slice.Value)-Point(A.Origin),Point(A.Direction),90,32,
                    HeightAt(B,F,Slice.Key),HeightAt(B,F,Slice.Value),0,65,Entry,Exit)
                    || !FirstVisibleAdmittedTime(B,FMath::Lerp(Slice.Key,Slice.Value,Entry),
                        FMath::Min(FMath::Lerp(Slice.Key,Slice.Value,Exit),std::nextafter(W.End,A.ActiveAt)),
                        [this,&A,&B,&F](double T){return HasLineOfSight(Point(A.Origin),PositionAt(B,F,T));},At)
                    || At>=W.End) continue;
                if (Kernel.TryMarkMeleeHit(A.AttackId,B.EntityId)) Batch.Hits.Add({B.Fighter,A.AttackId,B.EntityId,A.Damage,A.Stagger,At});
                break;
            }
        }
    }
}

FDungeonKnightBatch FDungeonStoneKnightDriver::StepTo(double Now,const FDungeonKnightFrame& F)
{
    FDungeonKnightBatch Batch;
    if (!ValidFrame(F) || !FMath::IsFinite(Now) || F.FromTime!=Kernel.State().Time || F.ToTime!=Now) return Batch;
    const auto Before=Kernel; bool Started=false;
    for (;;)
    {
        const double Cursor=Kernel.State().Time;
        const auto AtCursor=InputAt(F,Cursor); auto R=Kernel.StepTo(Cursor,AtCursor);
        if (!R.Accepted) { Kernel=Before; return {}; } Append(Batch,R); CollectHits(F,Cursor,Cursor,Batch);
        if (!Started)
        {
            const auto Choice=Kernel.ChooseAttack(AtCursor);
            if (Choice!=EAttack::None)
            {
                R=Kernel.TryStartAttack(Choice,AtCursor); if (!R.Accepted) { Kernel=Before; return {}; }
                Append(Batch,R); Started=true;
            }
        }
        if (Cursor==Now) break;
        double Next=Now; const auto& S=Kernel.State();
        const auto Bound=[&Next,Cursor](double At){if (At>Cursor) Next=FMath::Min(Next,At);};
        if (S.Phase==EPhase::Dormant)
        {
            if (S.CombatStartedAt>=0) Bound(S.CombatStartedAt+12);
            if (const auto* B=TargetBody(F))
            {
                const auto P0=PositionAt(*B,F,Cursor)-Point(S.Position),P1=PositionAt(*B,F,Now)-Point(S.Position);
                const FVector2D R0(P0.X/260,P0.Y/110),D((P1.X-P0.X)/260,(P1.Y-P0.Y)/110);
                const double A=D.SizeSquared(),Bq=2*FVector2D::DotProduct(R0,D),C=R0.SizeSquared()-1,Disc=Bq*Bq-4*A*C;
                if (A>0 && C>0 && Disc>=0)
                { const double Entry=(-Bq-FMath::Sqrt(Disc))/(2*A); if (Entry>0 && Entry<=1) Bound(FMath::Lerp(Cursor,Now,Entry)); }
            }
        }
        else if (S.Phase==EPhase::Waking) Bound(S.WakeEnd);
        else if (S.Phase==EPhase::Stunned) Bound(S.StunUntil);
        else if (S.Action.InProgress)
        {
            if (!S.Action.Locked) Bound(S.Action.LockAt);
            if (!S.Action.ActiveIssued) Bound(S.Action.ActiveAt);
            Bound(S.Action.ActiveEnd); Bound(S.Action.RecoveryEnd);
        }
        // Dormancy/idle observe the start of the interval; lock events observe their real endpoint.
        const auto W=InputAt(F,(S.Phase==EPhase::Dormant || S.Phase==EPhase::Idle)?Cursor:Next);
        R=Kernel.StepTo(Next,W);
        if (!R.Accepted || Kernel.State().Time!=Next) { Kernel=Before; return {}; }
        Append(Batch,R); CollectHits(F,Cursor,Next,Batch);
    }
    Batch.Accepted=true; return Batch;
}

FDungeonKnightBatch FDungeonStoneKnightDriver::ApplyResolvedHit(double ActualHPLoss,double LegalStagger,const FDungeonKnightFrame& F)
{
    FDungeonKnightBatch B;
    if (!ValidFrame(F) || F.ToTime!=Kernel.State().Time) return B;
    const auto R=Kernel.ApplyResolvedHit(ActualHPLoss,LegalStagger,InputAt(F,F.ToTime));
    B.Accepted=R.Accepted; Append(B,R); return B;
}
