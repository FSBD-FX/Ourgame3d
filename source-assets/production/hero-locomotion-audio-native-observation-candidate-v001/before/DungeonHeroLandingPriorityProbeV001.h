#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "DungeonHeroLandingPriorityProbeV001.generated.h"

class UDungeonNativeMainSubmixCaptureV001;
struct FDungeonHeroLandingPriorityProofStateV001;
struct FDungeonHeroLandingPriorityProofDeleterV001{void operator()(FDungeonHeroLandingPriorityProofStateV001*)const;};
// Isolated normal-input observer. It never supplies jump/position/HP/AI/clock values.
UCLASS()
class CODEXDUNGEON_API ADungeonHeroLandingPriorityProbeV001:public AActor
{
 GENERATED_BODY()
public:
 ADungeonHeroLandingPriorityProbeV001();
 virtual ~ADungeonHeroLandingPriorityProbeV001()override;
 virtual void BeginPlay()override;
 virtual void Tick(float DeltaSeconds)override;
 virtual void EndPlay(const EEndPlayReason::Type Reason)override;
private:
 friend struct FDungeonHeroLandingPriorityProofStateV001;
 void ScreenshotProcessed();
 TUniquePtr<FDungeonHeroLandingPriorityProofStateV001,FDungeonHeroLandingPriorityProofDeleterV001> Proof;
 UPROPERTY(Transient) TObjectPtr<UDungeonNativeMainSubmixCaptureV001> MainMixCapture;
};
