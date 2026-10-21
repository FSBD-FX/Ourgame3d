#pragma once
#include "CoreMinimal.h"
#include "DungeonStoneKnight.h"
#include <limits>

class ADungeonFighter;

namespace DungeonContactGeometry
{
// Keep the contact's geometric priority separate from its representable stop.
// RelativeAt must use the receiving kernel's actual position/time formula.
template<class TRelativeAt>
double ConservativeBodyFraction(double BeginFraction,double ContactFraction,
    FVector2D RelativeFrom,FVector2D RelativeTo,FVector2D Extent,TRelativeAt RelativeAt)
{
    if (ContactFraction<=BeginFraction) return ContactFraction;
    const auto AxisEntry=[](double A,double Z,double Half)
    {
        if (A>Half && Z<A) return (Half-A)/(Z-A);
        if (A<-Half && Z>A) return (-Half-A)/(Z-A);
        return -1.0;
    };
    const double X=AxisEntry(RelativeFrom.X,RelativeTo.X,Extent.X);
    const double Y=AxisEntry(RelativeFrom.Y,RelativeTo.Y,Extent.Y);
    if (X<0.0 && Y<0.0) return ContactFraction; // Existing overlap, not a new entry face.
    const bool UseX=X>=Y;
    const double Sign=(UseX?RelativeFrom.X:RelativeFrom.Y)<0.0?-1.0:1.0;
    const double Half=UseX?Extent.X:Extent.Y;
    const auto Outside=[&RelativeAt,UseX,Sign,Half](double Fraction)
    {
        const auto R=RelativeAt(Fraction);
        return Sign*(UseX?R.X:R.Y)>Half;
    };
    if (Outside(ContactFraction)) return ContactFraction;
    if (!Outside(BeginFraction)) return BeginFraction;
    double OutsideFraction=BeginFraction,InsideFraction=ContactFraction;
    // Adjacent representable fractions, never a world-space distance epsilon.
    for (int I=0;I<std::numeric_limits<double>::digits+2;++I)
    {
        const double Mid=OutsideFraction+(InsideFraction-OutsideFraction)*.5;
        if (Mid==OutsideFraction || Mid==InsideFraction) break;
        if (Outside(Mid)) OutsideFraction=Mid;else InsideFraction=Mid;
    }
    return OutsideFraction;
}
}

struct FDungeonDirectInvulnerabilityInterval
{
    double Start = 0.0;
    double EndExclusive = 0.0;
};

struct FDungeonMotionSegment
{
    double FromTime = 0.0, ToTime = 0.0;
    FVector2D From = FVector2D::ZeroVector, To = FVector2D::ZeroVector;
    double FromHeight = 0.0, ToHeight = 0.0;
    bool bEndExclusive = false; // An instantaneous step at ToTime belongs to the next segment.
};

// Frozen actor observations for this one simulation batch; never UObject addresses as saved IDs.
struct FDungeonKnightBody
{
    TWeakObjectPtr<ADungeonFighter> Fighter;
    uint64 EntityId = 0;
    FVector2D Start = FVector2D::ZeroVector;
    FVector2D End = FVector2D::ZeroVector;
    double StartHeight = 0.0;
    double EndHeight = 0.0;
    FVector2D BodyHalfExtent = FVector2D(18.0, 16.0);
    bool bAlive = true;
    bool bCanTakeDamage = true; // The interval which existed before this batch, not newly granted iframes.
    bool bBlocksBody = true;
    bool bSameTeam = false;
    // Legacy callers retain their whole-interval boolean until opted in.
    bool bUseTimedDamageAdmission = false;
    TArray<FDungeonDirectInvulnerabilityInterval> DirectInvulnerabilityIntervals;
    TArray<FDungeonMotionSegment> MotionSegments;
};

struct FDungeonKnightFrame
{
    double FromTime = 0.0;
    double ToTime = 0.0;
    TWeakObjectPtr<ADungeonFighter> Target;
    TArray<FDungeonKnightBody> Bodies;
    FBox2D CenterBounds = FBox2D(FVector2D(-700.0, -200.0), FVector2D(700.0, 220.0));
    bool bUseCenterBounds = true;
    bool bCanStartAttack = true;
    bool bCanBeginWake = true;
};

struct FDungeonKnightHit
{
    TWeakObjectPtr<ADungeonFighter> Target;
    uint64 AttackId = 0;
    uint64 TargetId = 0;
    double Damage = 0.0;
    double Stagger = 0.0;
    double AtTime = 0.0;
};

struct FDungeonKnightBatch
{
    bool Accepted = false;
    std::vector<DungeonStoneKnight::FEvent> Events;
    TArray<FDungeonKnightHit> Hits;
};

// No actor/component tick. All queries are read-only; caller commits State and Hits together.
class CODEXDUNGEON_API FDungeonStoneKnightDriver
{
public:
    FDungeonStoneKnightDriver(ADungeonFighter* InOwner, uint64 EntityId, double StartTime = 0.0);
    const DungeonStoneKnight::FState& State() const { return Kernel.State(); }
    DungeonStoneKnight::FState Capture() const { return Kernel.Capture(); }
    bool Restore(const DungeonStoneKnight::FState& Saved);
    FDungeonKnightBatch StepTo(double Now, const FDungeonKnightFrame& Frame);
    FDungeonKnightBatch ApplyResolvedHit(double ActualHPLoss, double LegalStagger, const FDungeonKnightFrame& Frame);
    bool BeginCombat();
    bool NotifyOtherAcceptedEnemiesCleared();
    bool ClaimDeathReward();

    // Also exposed for callers inspecting a real query. Does not mutate kernel, actor, HP or events.
    DungeonStoneKnight::FSweepResult QuerySweep(const DungeonStoneKnight::FSweepRequest& Query, const FDungeonKnightFrame& Frame) const;

private:
    TWeakObjectPtr<ADungeonFighter> Owner;
    DungeonStoneKnight::FKnightKernel Kernel;
    bool ValidFrame(const FDungeonKnightFrame& Frame) const;
    bool HasLineOfSight(FVector2D From, FVector2D To) const;
    DungeonStoneKnight::FWorldInput InputAt(const FDungeonKnightFrame& Frame, double AtTime) const;
    void CollectHits(const FDungeonKnightFrame& Frame, double FromTime, double ToTime, FDungeonKnightBatch& Batch);
};
