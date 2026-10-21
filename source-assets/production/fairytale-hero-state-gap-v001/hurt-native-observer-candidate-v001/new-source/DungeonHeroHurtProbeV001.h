#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "DungeonHeroHurtProbeV001.generated.h"
struct FDungeonHeroHurtProofState;
struct FDungeonHeroHurtProofDeleter {void operator()(FDungeonHeroHurtProofState*)const;};
UCLASS()
class CODEXDUNGEON_API ADungeonHeroHurtProbeV001:public AActor
{
 GENERATED_BODY()
public:
 ADungeonHeroHurtProbeV001();
 virtual ~ADungeonHeroHurtProbeV001()override;
 virtual void BeginPlay()override;
 virtual void Tick(float DeltaSeconds)override;
 virtual void EndPlay(const EEndPlayReason::Type Reason)override;
private:
 void ScreenshotProcessed();
 TUniquePtr<FDungeonHeroHurtProofState,FDungeonHeroHurtProofDeleter> Proof;
};
