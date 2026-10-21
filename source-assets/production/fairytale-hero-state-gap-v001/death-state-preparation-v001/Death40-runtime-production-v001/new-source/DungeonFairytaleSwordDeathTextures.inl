#pragma once
#include "DungeonFairytaleSwordDeathProfile.h"
#include "Engine/Texture2D.h"
#include "Misc/PackageName.h"

namespace DungeonFairytaleSwordDeathV001
{
// Configured startup only. The renderer/observer use the exact cache without loading.
inline UTexture2D* PreloadTexture(const FString& Path,TMap<FString,TObjectPtr<UTexture2D>>& Cache)
{
 if(const auto Found=Cache.Find(Path))return Found->Get();
 const FString Package=FPackageName::ObjectPathToPackageName(Path);
 UTexture2D* Texture=FPackageName::DoesPackageExist(Package)?LoadObject<UTexture2D>(nullptr,*Path):nullptr;
 Cache.Add(Path,Texture);return Texture;
}
}
