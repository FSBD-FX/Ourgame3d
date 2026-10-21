#include "DungeonFairytaleSwordEquipmentBinding.h"

namespace DungeonFairytaleSwordEquipmentBinding
{
bool Resolve(const ADungeonGameMode&,const ADungeonFighter&,FBinding&,FString& Diagnostic)
{
    Diagnostic=TEXT("Equipment-bound sword resolver Stage0 is not implemented");
    return false;
}
bool ValidateCommitted(const FDungeonEquipmentView&,const DungeonEquipmentInventory::FState&,
    const DungeonContentCombat::FCombatState&,const FString&,const FString&,
    FBinding&,FString& Diagnostic)
{
    Diagnostic=TEXT("Equipment-bound committed-value validator Stage0 is not implemented");
    return false;
}
}
