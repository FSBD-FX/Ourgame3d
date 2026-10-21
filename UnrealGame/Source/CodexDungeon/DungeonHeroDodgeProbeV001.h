#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "DungeonHeroDodgeProbeV001.generated.h"
struct FDungeonHeroDodgeProofState;
struct FDungeonHeroDodgeProofDeleter {void operator()(FDungeonHeroDodgeProofState*)const;};
UCLASS()
class CODEXDUNGEON_API ADungeonHeroDodgeProbeV001:public AActor
{
 GENERATED_BODY()
public:
 ADungeonHeroDodgeProbeV001();
 virtual ~ADungeonHeroDodgeProbeV001()override;
 virtual void BeginPlay()override;
 virtual void Tick(float DeltaSeconds)override;
 virtual void EndPlay(const EEndPlayReason::Type Reason)override;
private:
 void ScreenshotProcessed();
 TUniquePtr<FDungeonHeroDodgeProofState,FDungeonHeroDodgeProofDeleter> Proof;
};
