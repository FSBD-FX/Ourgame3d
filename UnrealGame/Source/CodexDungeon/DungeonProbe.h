#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "InputCoreTypes.h"
#include "DungeonProbe.generated.h"

class FJsonObject;
class FJsonValue;
class ADungeonGameMode;
class ADungeonFighter;

/** Opt-in deterministic integration checks and captured gameplay, never enabled for normal play. */
UCLASS()
class CODEXDUNGEON_API ADungeonProbe : public AActor
{
    GENERATED_BODY()
public:
    ADungeonProbe();
    virtual void BeginPlay() override;
    virtual void Tick(float DeltaSeconds) override;
private:
    float Elapsed=0.f;
    bool bChecked=false;
    bool bJumpChecked=false;
    bool bSaved=false;
    bool bWalkChecked=false;
    float GroundBeforeJump=0.f;
    FString ProofDirectory;
    TArray<TSharedPtr<FJsonValue>> Results;
    TMap<FKey,bool> HeldKeys;
    void Key(FKey Input,bool Down);
    void MoveInput(FVector2D Direction);
    void Check(const FString& Name,bool Passed);
    void RunChecks(ADungeonGameMode* Game);
    void SaveReport(ADungeonGameMode* Game);
};
