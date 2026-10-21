#pragma once
#include "DungeonFairytaleSwordHurtProfile.h"
#include "Engine/Texture2D.h"
#include "Misc/PackageName.h"

namespace DungeonFairytaleSwordHurtV001
{
// Startup-only loader. Actual Draw reads the preloaded exact path cache, never first-use repairs.
inline UTexture2D* PreloadTexture(const FString& Path,TMap<FString,TObjectPtr<UTexture2D>>& Cache)
{
 if(const auto Found=Cache.Find(Path))return Found->Get();
 const FString Package=FPackageName::ObjectPathToPackageName(Path);
 UTexture2D* T=FPackageName::DoesPackageExist(Package)?LoadObject<UTexture2D>(nullptr,*Path):nullptr;
 Cache.Add(Path,T);return T;
}
}
