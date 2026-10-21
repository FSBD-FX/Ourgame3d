#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "InputCoreTypes.h"
#include "DungeonFairytaleLookdevProbe.generated.h"

class FJsonObject;
class FJsonValue;

/** Silent, isolated observation capture. Does not create or advance a combat fixture. */
UCLASS()
class CODEXDUNGEON_API ADungeonFairytaleLookdevProbe : public AActor
{
    GENERATED_BODY()
public:
    ADungeonFairytaleLookdevProbe();
    virtual void BeginPlay() override;
    virtual void Tick(float DeltaSeconds) override;
    virtual void EndPlay(const EEndPlayReason::Type Reason) override;
private:
    FString Directory;
    TArray<TSharedPtr<FJsonValue>> Observations, FrameOffsets, Inputs;
    TArray<FString> Failures;
    TMap<FKey,bool> Keys;
    double WarmStart=0., PrewarmRequested=0., PrewarmCompleted=0., CaptureStart=0., CaptureStop=0., FlushCompleted=0.;
    bool PrewarmPending=false, Started=false, Stopped=false, Saved=false;
    TSharedPtr<FJsonObject> Baseline;
    void Key(FKey Code,bool Down);
    void ScreenshotProcessed();
    void Finish(const FString& Failure=FString());
};
