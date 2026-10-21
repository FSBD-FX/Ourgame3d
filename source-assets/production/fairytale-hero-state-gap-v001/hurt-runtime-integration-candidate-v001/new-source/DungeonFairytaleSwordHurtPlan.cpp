#include "DungeonFairytaleSwordHurtPlan.h"

namespace DungeonFairytaleSwordHurtV001
{
bool BuildDrawPlan(const ADungeonGameMode&,const ADungeonFighter&,const FDrawContext&,FDrawPlan&,FString& Diagnostic)
{
 Diagnostic=TEXT("Stage0 unsupported: actual SWD+LGT Hurt4 shared draw plan is not implemented");
 return false;
}
bool BuildDrawPlanFromCommitted(const DungeonFairytaleSwordEquipmentBinding::FBinding&,const FDungeonHurtPresentationSample&,
 double,const FProfile&,const FDrawContext&,FDrawPlan&,FString& Diagnostic)
{
 Diagnostic=TEXT("Stage0 unsupported: committed Hurt4 admission/selector/geometry is not implemented");
 return false;
}
}
