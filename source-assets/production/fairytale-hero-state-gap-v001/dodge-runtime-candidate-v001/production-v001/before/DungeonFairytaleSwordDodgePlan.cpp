#include "DungeonFairytaleSwordDodgePlan.h"

namespace DungeonFairytaleSwordDodgeV001
{
bool BuildDrawPlan(const ADungeonGameMode&,const ADungeonFighter&,const FDrawContext&,FDrawPlan&,FString& Diagnostic)
{
 Diagnostic=TEXT("Stage0 unsupported: actual Dodge shared World draw plan is not implemented");return false;
}
bool BuildDrawPlanFromCommitted(const DungeonFairytaleSwordEquipmentBinding::FBinding&,const FDungeonDodgePresentationSample&,
 double,const FProfile&,const FDrawContext&,FDrawPlan&,FString& Diagnostic)
{
 Diagnostic=TEXT("Stage0 unsupported: actual Dodge committed-value draw plan is not implemented");return false;
}
}
