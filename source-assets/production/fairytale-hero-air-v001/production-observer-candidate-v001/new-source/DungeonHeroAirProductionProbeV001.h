#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "DungeonHeroAirProductionProbeV001.generated.h"

class UDungeonNativeMainSubmixCaptureV001;
struct FDungeonHeroAirProductionProofStateV001;
struct FDungeonHeroAirProductionProofDeleterV001{void operator()(FDungeonHeroAirProductionProofStateV001*)const;};
// Isolated normal-input observer. It never supplies jump/position/HP/AI/clock values.
UCLASS()
class CODEXDUNGEON_API ADungeonHeroAirProductionProbeV001:public AActor
{
 GENERATED_BODY()
public:
 ADungeonHeroAirProductionProbeV001();
 virtual ~ADungeonHeroAirProductionProbeV001()override;
 virtual void BeginPlay()override;
 virtual void Tick(float DeltaSeconds)override;
 virtual void EndPlay(const EEndPlayReason::Type Reason)override;
private:
 friend struct FDungeonHeroAirProductionProofStateV001;
 void ScreenshotProcessed();
 TUniquePtr<FDungeonHeroAirProductionProofStateV001,FDungeonHeroAirProductionProofDeleterV001> Proof;
 UPROPERTY(Transient) TObjectPtr<UDungeonNativeMainSubmixCaptureV001> MainMixCapture;
};
