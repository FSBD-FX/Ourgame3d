#pragma once
#include "CoreMinimal.h"
class ADungeonGameMode;class ADungeonFighter;
namespace DungeonFairytaleSwordEquipmentBinding{
inline constexpr const TCHAR* CommandLineFlag=TEXT("DungeonFairytaleSwordEquipmentBoundPreview");
enum class EArmor : uint8 { NoArmor, LightArmor };
// Successful read-only authorization, never a writable owner or saved schema.
// Failure of either API preserves every Out field and only writes Diagnostic.
struct FBinding
{
    FGuid RunGuid;
    uint64 RunAlias=0,OwnerId=0,Revision=0;
    int32 ActiveSlot=-1;
    uint64 WeaponInstanceId=0,WeaponVersion=0,ArmorInstanceId=0,ArmorVersion=0;
    FString WeaponContentId,ArmorContentId;
    EArmor Armor=EArmor::NoArmor;
};
// Production entry point: verifies actual world/AuthGameMode/main player before
// reading committed owners. An installed AwaitExplicitContinue is drawable;
// this resolver does not advance clocks, change a gate, or replay audio.
CODEXDUNGEON_API bool Resolve(const ADungeonGameMode& Game,const ADungeonFighter& Fighter,
    FBinding& Out,FString& Diagnostic);
}
