#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "DungeonSwdForwardStepProbeV002.generated.h"
class UDungeonNativeMainSubmixCaptureV001;
struct FDungeonSwdForwardStepProofV002;
struct FDungeonSwdForwardStepProofDeleterV002{void operator()(FDungeonSwdForwardStepProofV002*)const;};
UCLASS()
class CODEXDUNGEON_API ADungeonSwdForwardStepProbeV002:public AActor {
 GENERATED_BODY()
public:
 ADungeonSwdForwardStepProbeV002();
 virtual ~ADungeonSwdForwardStepProbeV002()override;
 virtual void BeginPlay()override;
 virtual void Tick(float DeltaSeconds)override;
 virtual void EndPlay(const EEndPlayReason::Type Reason)override;
private:
 friend struct FDungeonSwdForwardStepProofV002;
 void ScreenshotProcessed();
 TUniquePtr<FDungeonSwdForwardStepProofV002,FDungeonSwdForwardStepProofDeleterV002> Proof;
 UPROPERTY(Transient) TObjectPtr<UDungeonNativeMainSubmixCaptureV001> MainMix;
};
