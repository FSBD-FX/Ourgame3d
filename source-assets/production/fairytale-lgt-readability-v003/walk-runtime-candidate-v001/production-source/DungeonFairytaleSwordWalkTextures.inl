#pragma once
#include "DungeonFairytaleSwordWalkProfile.h"
#include "Engine/Texture2D.h"
#include "Misc/PackageName.h"

namespace DungeonFairytaleSwordWalkV001
{
inline UTexture2D* GetTexture(const FString& Component,int32 Index,TMap<FString,TObjectPtr<UTexture2D>>& Cache)
{
    const auto* F=Find(Index);if(!F)return nullptr;
    const FString* Path=Component==TEXT("Body")?&F->Body:Component==TEXT("BodyRest")?&F->BodyRest
        :Component==TEXT("NearArmWithoutHand")?&F->NearArmWithoutHand:Component==TEXT("HelmetForeground")?&F->HelmetForeground
        :Component==TEXT("NearHand")?&F->NearHand:Component==TEXT("ShoulderFar")?&F->ShoulderFar
        :Component==TEXT("Chest")?&F->Chest:Component==TEXT("ShoulderNear")?&F->ShoulderNear:nullptr;
    if(!Path)return nullptr;
    if(const auto Found=Cache.Find(*Path))return Found->Get();
    const FString Package=FPackageName::ObjectPathToPackageName(*Path);
    UTexture2D* Texture=FPackageName::DoesPackageExist(Package)?LoadObject<UTexture2D>(nullptr,**Path):nullptr;
    Cache.Add(*Path,Texture);return Texture;
}
}
