#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "InputCoreTypes.h"
#include "DungeonFairytaleSwordProbe.generated.h"
class FJsonValue;
/** Opt-in QA: normal Enter/A/J input, silent native capture; no combat state injection. */
UCLASS()
class CODEXDUNGEON_API ADungeonFairytaleSwordProbe:public AActor
{
    GENERATED_BODY()
public:
    ADungeonFairytaleSwordProbe();
    virtual void BeginPlay() override;
    virtual void Tick(float Dt) override;
    virtual void EndPlay(const EEndPlayReason::Type Reason) override;
private:
    FString Directory;
    TArray<TSharedPtr<FJsonValue>> Observations,Offsets,Inputs;
    TMap<FKey,bool> Keys;
    double WarmStart=0.,CaptureStart=0.,CaptureStop=0.;
    bool Prewarm=false,Started=false,Stopped=false;
    void Key(FKey Code,bool Down);
    void ScreenshotProcessed();
    void Finish(const FString& Failure=FString());
};
