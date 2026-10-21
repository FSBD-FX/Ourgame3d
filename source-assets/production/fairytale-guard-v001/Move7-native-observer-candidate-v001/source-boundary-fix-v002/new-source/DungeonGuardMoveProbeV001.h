#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "DungeonGuardMoveProbeV001.generated.h"
struct FDungeonGuardMoveProofState;
struct FDungeonGuardMoveProofDeleter {void operator()(FDungeonGuardMoveProofState*)const;};
UCLASS()
class CODEXDUNGEON_API ADungeonGuardMoveProbeV001:public AActor
{
 GENERATED_BODY()
public:
 ADungeonGuardMoveProbeV001();
 virtual ~ADungeonGuardMoveProbeV001()override;
 virtual void BeginPlay()override;
 virtual void Tick(float DeltaSeconds)override;
 virtual void EndPlay(const EEndPlayReason::Type Reason)override;
private:
 void ScreenshotProcessed();
 TUniquePtr<FDungeonGuardMoveProofState,FDungeonGuardMoveProofDeleter> Proof;
};
