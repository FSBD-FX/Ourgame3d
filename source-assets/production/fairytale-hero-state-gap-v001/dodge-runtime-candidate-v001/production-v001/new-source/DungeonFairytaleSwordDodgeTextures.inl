#pragma once
#include "DungeonFairytaleSwordDodgeProfile.h"
#include "Engine/Texture2D.h"
#include "Misc/PackageName.h"

namespace DungeonFairytaleSwordDodgeV001
{
// Startup only. Actual draw reads the exact preloaded cache; no first-use repair.
inline UTexture2D* PreloadTexture(const FString& Path,TMap<FString,TObjectPtr<UTexture2D>>& Cache)
{
 if(const auto Found=Cache.Find(Path))return Found->Get();
 const FString Package=FPackageName::ObjectPathToPackageName(Path);
 UTexture2D* Texture=FPackageName::DoesPackageExist(Package)?LoadObject<UTexture2D>(nullptr,*Path):nullptr;
 Cache.Add(Path,Texture);return Texture;
}
}
