#pragma once
#include "CoreMinimal.h"
#include "DungeonFairytaleGuardMoveRigV001.h"
struct FDungeonFairytaleGuardMoveSubmittedPartV001
{
 DungeonFairytaleGuardMoveRigV001::EComponent Component=DungeonFairytaleGuardMoveRigV001::EComponent::BodyRest;
 FString TexturePath,SourceSHA256,SourceRGBASHA256;
 int32 NativeBatchId=0;
 bool Submitted=false;
 // Exactly the values passed to DrawTexture, including native double pivot.
 DungeonFairytaleGuardMoveRigV001::FSubmittedQuad Quad;
};
struct FDungeonFairytaleGuardMoveRigDrawV001
{
 uint64 DrawId=0,EntityId=0;
 bool OptIn=false,TrialAllowed=false,FinalAccepted=false,RegistrationReady=false,TextureReady=false,Drawn=false;
 bool ProceduralFallback=true,WholebodyIncludesAxe=true;
 FString PresentationType=TEXT("GuardMoveSevenComponentRigDerived"),MissingReason;
 DungeonFairytaleGuardMoveRigV001::FDrawPlan Plan;
 // Must contain the same ordered seven submitted part arguments, never a
 // reconstruction of a separately rounded optical or canonical transform.
 TArray<FDungeonFairytaleGuardMoveSubmittedPartV001> Parts;
};
