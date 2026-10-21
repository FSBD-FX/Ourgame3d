#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "DungeonGuardRunContinueProbe.generated.h"

struct FDungeonGuardRunContinueProofState;
struct FDungeonGuardRunContinueProofDeleter
{
    void operator()(FDungeonGuardRunContinueProofState* State) const;
};

// Opt-in proof coordinator, not a save menu or a gameplay clock owner.
// It observes completed native GM ticks and sends genuine Controller InputKey.
UCLASS()
class CODEXDUNGEON_API ADungeonGuardRunContinueProbe : public AActor
{
    GENERATED_BODY()
public:
    ADungeonGuardRunContinueProbe();
    virtual ~ADungeonGuardRunContinueProbe() override;
    virtual void BeginPlay() override;
    virtual void Tick(float DeltaSeconds) override;
    virtual void EndPlay(const EEndPlayReason::Type Reason) override;
private:
    void ScreenshotProcessed();
    TUniquePtr<FDungeonGuardRunContinueProofState,FDungeonGuardRunContinueProofDeleter> Proof;
};
