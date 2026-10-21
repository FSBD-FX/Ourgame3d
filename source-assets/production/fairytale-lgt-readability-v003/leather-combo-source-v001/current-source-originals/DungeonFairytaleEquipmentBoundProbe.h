#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "InputCoreTypes.h"
#include "DungeonFairytaleEquipmentBoundProbe.generated.h"
class FJsonValue;class ADungeonGameMode;class ADungeonHUD;class APlayerController;
// Process-only QA using normal input and existing registered sources, never direct gear writes.
UCLASS()
class CODEXDUNGEON_API ADungeonFairytaleEquipmentBoundProbe:public AActor
{
    GENERATED_BODY()
public:
    ADungeonFairytaleEquipmentBoundProbe();
    virtual void BeginPlay() override;
    virtual void Tick(float Dt) override;
    virtual void EndPlay(const EEndPlayReason::Type Reason) override;
private:
    FString Directory;FGuid InitialRun;
    uint64 InitialOwner=0,InitialRunAlias=0,InitialRestartSerial=0,SwordId=0;
    uint64 LightSource=0,LightId=0,MediumSource=0,MediumId=0,DroppedLightSource=0;
    uint64 InitialOperation=0,InitialOperationCount=0,InitialLightVersion=0,QueuedAttack=0;
    int32 Step=0,ReadySeen[14]={},StageFrames[3]={},StageMasks[3]={};
    double WarmStart=0.,CaptureStart=0.,CaptureStop=0.,StepStart=0.,PulseReleaseAt=0.,NeutralUntil=0.,CancelDeadline=0.;
    bool Prewarm=false,Started=false,Stopped=false,FlowComplete=false;
    bool LeatherReadyOnly=false,LeatherTurnRequested=false;
    int32 LeatherReadyMasks[2]={};
    bool LeatherPrimary1Only=false,LeatherPrimaryTurnRequested=false;
    int32 LeatherPrimary1Masks[2]={};
    uint64 LeatherPrimary1AttackIds[2]={};
    FKey PulseKey;TMap<FKey,bool> Keys;
    TArray<TSharedPtr<FJsonValue>> Observations,Offsets,Inputs,PhaseChecks,Mismatches;
    TSet<FString> MismatchKeys;
    ADungeonGameMode* Game() const;APlayerController* Controller() const;ADungeonHUD* HUD() const;
    const TCHAR* StepName() const;
    void Next(int32 Value);void Key(FKey Code,bool Down);bool CanPulse() const;bool Pulse(FKey Code);
    void Mismatch(const FString& Reason,int32 Observation);void ScreenshotProcessed();
    void Finish(const FString& Reason=FString());
};
