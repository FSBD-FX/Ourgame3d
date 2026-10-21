#pragma once
#include "CoreMinimal.h"
class ADungeonGameMode{public:double Time=0.;uint64 Epoch=0;double GetSimulationTime()const{return Time;}uint64 GetRunPresentationEpoch()const{return Epoch;}};
