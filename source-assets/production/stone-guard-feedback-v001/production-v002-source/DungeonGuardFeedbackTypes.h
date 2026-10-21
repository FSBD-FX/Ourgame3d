#pragma once
#include "CoreMinimal.h"
#include "DungeonStoneGuardFeedback.h"
struct FDungeonGuardAudioPlayRequest
{
 DungeonGuardFeedback::FRecord Source;
 FString Cue,SoundPath;
 double RequestedAt=0;
 float Volume=0,Pitch=1;
};
struct FDungeonGuardEffectSpawnRequest
{
 DungeonGuardFeedback::FRecord Source;
 double StartedAt=0,ExpiresAt=0;
};
