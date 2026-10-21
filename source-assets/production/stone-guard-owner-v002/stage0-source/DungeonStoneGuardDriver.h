#pragma once
#include "CoreMinimal.h"
#include "DungeonStoneGuard.h"
#include "DungeonStoneKnightDriver.h"
class ADungeonFighter;
struct FDungeonGuardBatch
{
    bool Accepted=false;
    std::vector<DungeonStoneGuard::FEvent> Events;
    TArray<FDungeonKnightHit> Hits;
    TArray<FDungeonMotionSegment> MotionSegments;
};
// Pure central-clock adapter. No Actor tick, raw damage mitigation or currency writes.
class CODEXDUNGEON_API FDungeonStoneGuardDriver
{
public:
    FDungeonStoneGuardDriver(ADungeonFighter* Owner,uint64 EntityId,double StartTime=0.);
    FDungeonStoneGuardDriver(ADungeonFighter* Owner,uint64 EntityId,double InitialTime,
        DungeonStoneGuard::FPoint InitialPosition,DungeonStoneGuard::FPolicy SavedPolicy);
    DungeonStoneGuard::FPolicy CapturePolicy() const {return Kernel.CapturePolicy();}
    // Validated same-birth replacement. No Step/BeginCombat/Sync/world query.
    bool Restore(const DungeonStoneGuard::FState& Saved);
    const DungeonStoneGuard::FState& State() const {return Kernel.State();}
    DungeonStoneGuard::FState Capture() const {return Kernel.Capture();} // Readback only, not a D13 schema.
    FDungeonGuardBatch StepTo(double Now,const FDungeonKnightFrame& Frame,
        const std::vector<DungeonStoneGuard::FIncomingHit>& Hits={});
    FDungeonGuardBatch ApplyResolvedHit(double ActualHPLoss,double LegalStagger,const FDungeonKnightFrame& Frame);
    DungeonStoneGuard::FSweepResult QuerySweep(const DungeonStoneGuard::FSweepRequest& Query,const FDungeonKnightFrame& Frame) const;
    bool BeginCombat();
    bool NotifyOtherAcceptedEnemiesCleared();
    bool ClaimDeathReward(); // Once local eligibility; no reward allocation or pickup.
private:
    TWeakObjectPtr<ADungeonFighter> Owner;
    DungeonStoneGuard::FGuardKernel Kernel;
    bool ValidFrame(const FDungeonKnightFrame& Frame) const;
    bool HasLineOfSight(FVector2D From,FVector2D To) const;
    DungeonStoneGuard::FWorldInput InputAt(const FDungeonKnightFrame& Frame,double At,
        TArray<FDungeonMotionSegment>* Motion=nullptr) const;
};
