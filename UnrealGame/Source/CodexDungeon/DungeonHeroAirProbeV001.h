#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "DungeonHeroAirProbeV001.generated.h"

class UDungeonNativeMainSubmixCaptureV001;
struct FDungeonHeroAirProofStateV001;
struct FDungeonHeroAirProofDeleterV001{void operator()(FDungeonHeroAirProofStateV001*)const;};
// Isolated normal-input observer. It never supplies jump/position/HP/AI/clock values.
UCLASS()
class CODEXDUNGEON_API ADungeonHeroAirProbeV001:public AActor
{
 GENERATED_BODY()
public:
 ADungeonHeroAirProbeV001();
 virtual ~ADungeonHeroAirProbeV001()override;
 virtual void BeginPlay()override;
 virtual void Tick(float DeltaSeconds)override;
 virtual void EndPlay(const EEndPlayReason::Type Reason)override;
private:
 friend struct FDungeonHeroAirProofStateV001;
 void ScreenshotProcessed();
 TUniquePtr<FDungeonHeroAirProofStateV001,FDungeonHeroAirProofDeleterV001> Proof;
 UPROPERTY(Transient) TObjectPtr<UDungeonNativeMainSubmixCaptureV001> MainMixCapture;
};
