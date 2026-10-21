#if WITH_DEV_AUTOMATION_TESTS
#include "Misc/AutomationTest.h"
#include "StoneGuardMovementCases.h"
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDungeonStoneGuardMovementFirstEntry,
 "CodexDungeon.Content.StoneGuardKernel.MovementFirstEntryPartitionAndZeroReceipts",
 EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FDungeonStoneGuardMovementFirstEntry::RunTest(const FString& Parameters)
{
 (void)Parameters;
 return StoneGuardMovementCases::Run([this](bool Value,const char* Name){TestTrue(FString(UTF8_TO_TCHAR(Name)),Value);});
}
#endif
