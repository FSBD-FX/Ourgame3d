#pragma once
#include "CoreMinimal.h"
#include "DungeonHeroLocomotionAudioV001.h"
// A playback API request, not an audible PCM receipt or mix approval.
struct FDungeonHeroLocomotionAudioPlayRequestV001
{
 DungeonHeroLocomotionAudioV001::FEvent Source;
 FName Cue;
 FString SoundPath;
 FVector2D GroundPosition=FVector2D::ZeroVector;
 double RequestedAt=0.;
 float Volume=0.f,Pitch=1.f;
};
