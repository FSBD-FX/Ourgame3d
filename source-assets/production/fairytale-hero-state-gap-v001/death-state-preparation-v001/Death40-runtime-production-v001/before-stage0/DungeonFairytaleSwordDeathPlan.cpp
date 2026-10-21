#include "DungeonFairytaleSwordDeathPlan.h"

namespace DungeonFairytaleSwordDeathV001
{
bool BuildDrawPlan(const ADungeonGameMode&,const ADungeonFighter&,const FDrawContext&,FDrawPlan&,FString& Diagnostic)
{
 Diagnostic=TEXT("Stage0: actual terminal Death5 draw plan is not implemented");return false;
}
bool BuildDrawPlanFromCommitted(const DungeonFairytaleSwordEquipmentBinding::FBinding&,const FDungeonDeathPresentationSample&,
 double,const FProfile&,const FDrawContext&,FDrawPlan&,FString& Diagnostic)
{
 Diagnostic=TEXT("Stage0: committed Death5 draw plan is not implemented");return false;
}
}
