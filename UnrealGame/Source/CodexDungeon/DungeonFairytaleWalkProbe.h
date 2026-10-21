#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "DungeonFairytaleWalkProbe.generated.h"
struct FDungeonFairytaleWalkProofState;
struct FDungeonFairytaleWalkProofDeleter {void operator()(FDungeonFairytaleWalkProofState* Value)const;};
// Opt-in real-input observer. Native GameMode owns every clock/movement/gear/attack.
UCLASS()
class CODEXDUNGEON_API ADungeonFairytaleWalkProbe:public AActor
{
    GENERATED_BODY()
public:
    ADungeonFairytaleWalkProbe();
    virtual ~ADungeonFairytaleWalkProbe() override;
    virtual void BeginPlay()override;
    virtual void Tick(float DeltaSeconds)override;
    virtual void EndPlay(const EEndPlayReason::Type Reason)override;
private:
    void ScreenshotProcessed();
    TUniquePtr<FDungeonFairytaleWalkProofState,FDungeonFairytaleWalkProofDeleter> Proof;
};
