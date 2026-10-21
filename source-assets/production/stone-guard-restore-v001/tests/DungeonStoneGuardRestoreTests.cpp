#if WITH_DEV_AUTOMATION_TESTS
#include "Misc/AutomationTest.h"
#include "StoneGuardRestoreCases.h"
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDungeonGuardRestoreStages,"CodexDungeon.Content.StoneGuardRestore.RealStagesAndFutureContinuation",EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FDungeonGuardRestoreStages::RunTest(const FString& Parameters)
{(void)Parameters;return StoneGuardRestoreCases::StageRoundTrips([this](bool V,const char* N){TestTrue(UTF8_TO_TCHAR(N),V);});}
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDungeonGuardRestoreHistories,"CodexDungeon.Content.StoneGuardRestore.ClosedWindowsSameCursorDeathAndIndependentObligations",EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FDungeonGuardRestoreHistories::RunTest(const FString& Parameters)
{(void)Parameters;return StoneGuardRestoreCases::HistoriesAndObligations([this](bool V,const char* N){TestTrue(UTF8_TO_TCHAR(N),V);});}
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDungeonGuardRestoreRejects,"CodexDungeon.Content.StoneGuardRestore.CorruptionAtomicityPolicyAndDeepOwnership",EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FDungeonGuardRestoreRejects::RunTest(const FString& Parameters)
{(void)Parameters;return StoneGuardRestoreCases::CorruptionAndAtomicity([this](bool V,const char* N){TestTrue(UTF8_TO_TCHAR(N),V);});}
#endif
