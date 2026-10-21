#pragma once
#include "CoreMinimal.h"
#include "DungeonStoneBat.h"
#include "DungeonStoneKnightDriver.h"

class ADungeonFighter;
struct FDungeonBatBatch
{
    bool Accepted=false;
    std::vector<DungeonStoneBat::FEvent> Events;
    TArray<FDungeonKnightHit> Hits;
    TArray<FDungeonMotionSegment> MotionSegments;
};
// One central-clock driver, never an Actor tick or a second HP authority.
class CODEXDUNGEON_API FDungeonStoneBatDriver
{
public:
    FDungeonStoneBatDriver(ADungeonFighter* InOwner,uint64 EntityId,double StartTime=0.);
    FDungeonStoneBatDriver(ADungeonFighter* InOwner,uint64 EntityId,double InitialTime,
        DungeonStoneBat::FPoint InitialPosition);
    bool Restore(const DungeonStoneBat::FState& Saved);
    const DungeonStoneBat::FState& State() const {return Kernel.State();}
    DungeonStoneBat::FState Capture() const {return Kernel.Capture();}
    bool BeginCombat();
    bool NotifyOtherAcceptedEnemiesCleared();
    bool ClaimDeathReward();
    FDungeonBatBatch StepTo(double Now,const FDungeonKnightFrame& Frame,const std::vector<DungeonStoneBat::FIncomingHit>& Hits={});
    FDungeonBatBatch ApplyResolvedHit(double ActualHPLoss,double LegalStagger,const FDungeonKnightFrame& Frame);
    DungeonStoneBat::FSweepResult QuerySweep(const DungeonStoneBat::FSweepRequest& Query,const FDungeonKnightFrame& Frame) const;
private:
    TWeakObjectPtr<ADungeonFighter> Owner;
    DungeonStoneBat::FBatKernel Kernel;
    bool ValidFrame(const FDungeonKnightFrame& Frame) const;
    bool HasLineOfSight(FVector2D From,FVector2D To) const;
    bool LegalLowPoint(const DungeonStoneBat::FLowPointRequest& Request,const FDungeonKnightFrame& Frame) const;
    DungeonStoneBat::FNearestLowResult NearestLowPoint(DungeonStoneBat::FPoint From,const FDungeonKnightFrame& Frame) const;
    DungeonStoneBat::FWorldInput InputAt(const FDungeonKnightFrame& Frame,double At,TArray<FDungeonMotionSegment>* Motion=nullptr) const;
};
