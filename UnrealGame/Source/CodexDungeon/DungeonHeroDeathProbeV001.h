#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "DungeonHeroDeathProbeV001.generated.h"
struct FDungeonHeroDeathProofState;
struct FDungeonHeroDeathProofDeleter {void operator()(FDungeonHeroDeathProofState*)const;};
UCLASS()
class CODEXDUNGEON_API ADungeonHeroDeathProbeV001:public AActor
{
 GENERATED_BODY()
public:
 ADungeonHeroDeathProbeV001();
 virtual ~ADungeonHeroDeathProbeV001()override;
 virtual void BeginPlay()override;
 virtual void Tick(float DeltaSeconds)override;
 virtual void EndPlay(const EEndPlayReason::Type Reason)override;
private:
 void ScreenshotProcessed();
 TUniquePtr<FDungeonHeroDeathProofState,FDungeonHeroDeathProofDeleter> Proof;
};
