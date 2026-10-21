#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "DungeonRunContinueProbe.generated.h"

struct FDungeonRunContinueProofState;
struct FDungeonRunContinueProofDeleter
{
    void operator()(FDungeonRunContinueProofState* State) const;
};

// Opt-in proof coordinator, not a save menu or a gameplay clock owner.
// It observes completed native GM ticks and sends genuine Controller InputKey.
UCLASS()
class CODEXDUNGEON_API ADungeonRunContinueProbe : public AActor
{
    GENERATED_BODY()
public:
    ADungeonRunContinueProbe();
    virtual ~ADungeonRunContinueProbe() override;
    virtual void BeginPlay() override;
    virtual void Tick(float DeltaSeconds) override;
    virtual void EndPlay(const EEndPlayReason::Type Reason) override;
private:
    TUniquePtr<FDungeonRunContinueProofState,FDungeonRunContinueProofDeleter> Proof;
};
