#include "DungeonRunSaveAdapterV2.h"
namespace DungeonRunSaveAdapterV2
{
namespace
{
const TCHAR* Unimplemented=TEXT("Explicit Guard Run DiskV2 is not implemented (Stage0)");
FReadResult NotImplemented(){FReadResult R;R.Status=Store::EStatus::NotImplemented;R.Diagnostic=Unimplemented;return R;}
}
bool MakeGeneration(const FDungeonRunSnapshot& Saved,const FWriteRequest& Request,Store::FGeneration& Out,FString& Diagnostic)
{(void)Saved;(void)Request;(void)Out;Diagnostic=Unimplemented;return false;}
bool ValidateGeneration(const Store::FGeneration& Generation,const FReadContext& Context,FDungeonValidatedRun& Out,FString& Diagnostic)
{(void)Generation;(void)Context;(void)Out;Diagnostic=Unimplemented;return false;}
Store::FCommitResult Commit(Store::FGenerationStore& Disk,const FDungeonRunSnapshot& Saved,const FWriteRequest& Request,Store::EFaultPoint Fault)
{(void)Disk;(void)Saved;(void)Request;(void)Fault;Store::FCommitResult R;R.Status=Store::EStatus::NotImplemented;R.Diagnostic=Unimplemented;return R;}
FReadResult Load(const Store::FGenerationStore& Disk,const FReadContext& Context,FLoadedRun& Out)
{(void)Disk;(void)Context;(void)Out;return NotImplemented();}
FReadResult LoadAndPrepare(ADungeonGameMode& Game,const Store::FGenerationStore& Disk,const FReadContext& Context,FDungeonPreparedRun& OutPrepared,FLoadedRun& OutLoaded)
{(void)Game;(void)Disk;(void)Context;(void)OutPrepared;(void)OutLoaded;return NotImplemented();}
FReadResult LoadAndPreparePristine(ADungeonGameMode& Game,const Store::FGenerationStore& Disk,const FReadContext& Context,FDungeonPreparedRun& OutPrepared,FLoadedRun& OutLoaded)
{(void)Game;(void)Disk;(void)Context;(void)OutPrepared;(void)OutLoaded;return NotImplemented();}
}
