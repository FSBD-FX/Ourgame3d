#if WITH_DEV_AUTOMATION_TESTS
#include "Misc/AutomationTest.h"
#include "StoneGuardDiskV2Fixture_v001.h"
namespace
{
using namespace DiskV2Tests;
}
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDungeonGuardDiskV2Typed,
 "CodexDungeon.Content.StoneGuardDiskV2.TypedEnvelopeVersionsAndV1BytePreservation",
 EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FDungeonGuardDiskV2Typed::RunTest(const FString& Parameters)
{
 (void)Parameters;using namespace DiskV2Tests;FGuardWorld W(*this);FDungeonRunSnapshot S,Legacy;FDungeonValidatedRun Valid;if(!Source(W,S,Valid,&Legacy))return false;
 FDisk D(*this);auto R=D.Request(S);FString Why;
 DungeonRunSaveAdapter::FWriteRequest V1;V1.Context.ProfilesDirectory=D.Root/DungeonRunSaveAdapter::DirectoryName;V1.Context.ProfileId=D.Context.ProfileId;
 V1.RunGuid=Legacy.RunGuid;V1.OwnerId=Legacy.OwnerId;V1.GenerationId=1;V1.BuildId=R.BuildId;
 Store::FGeneration Old;if(!TestTrue(TEXT("Actual unchanged V1 MakeGeneration bytes equal independent complete old envelope before V2 stub"),DungeonRunSaveAdapter::MakeGeneration(Legacy,V1,Old,Why)&&GenerationSig(Old)==GenerationSig(Expected(Legacy,R,true))))return false;
 R.BuildId=TEXT("guard-v2 quoted \"identity\" 中文");const auto Oracle=Expected(S,R);Store::FGeneration Out=Old;
 const bool Made=Save::MakeGeneration(S,R,Out,Why);if(!TestTrue(TEXT("Implemented explicitV2 MakeGeneration accepts the genuinely legal guardedRoot (Stage0 RED)"),Made)){AddInfo(Why);return false;}
 TestTrue(TEXT("V2 allheader/envelope/codec/clock/identity values exactly match independent named-field oracle"),GenerationSig(Out)==GenerationSig(Oracle)&&Why.IsEmpty());
 FDungeonValidatedRun Decoded;if(!TestTrue(TEXT("V2 mandatory validator seals independent envelope bytes"),Save::ValidateGeneration(Oracle,D.Context,Decoded,Why)&&Decoded.IsValid()))return false;
 TestTrue(TEXT("V2 decoded root includes every actual Guard policy/state/history/nativeobserver bit"),RunSig(*Decoded.Get())==RunSig(S));
 const auto* Ptr=Decoded.Get();const auto Exact=RunSig(*Ptr);
 const auto Reject=[&](Store::FGeneration G,const Save::FReadContext& C,const TCHAR* Label)
 {TestFalse(Label,Save::ValidateGeneration(G,C,Decoded,Why));TestTrue(TEXT("V2 version/header/label refusal preserves sealedpointer and allvalues"),Decoded.Get()==Ptr&&RunSig(*Decoded.Get())==Exact&&!Why.IsEmpty());};
 auto Bad=Oracle;Bad.Versions.Schema=TEXT("bound-run-generation-v99");Reject(Bad,D.Context,TEXT("Unknown diskversion rejects"));
 Bad=Oracle;Bad.Versions.ContentRules=DungeonRunSaveAdapter::CurrentVersions.ContentRules;Reject(Bad,D.Context,TEXT("Mixed oldcontent rules andV2schema rejects"));
 Bad=Oracle;Bad.Versions.Coordinates=TEXT("WORLD-CM-V1");Reject(Bad,D.Context,TEXT("Version spelling is ordinal"));
 Bad=Oracle;Bad.RunSimulationTime=S.SimulationTime+.1;Reject(Bad,D.Context,TEXT("Original headerclock must match root bits"));
 Bad=Oracle;
 // Construct a wrong-label negative by changing only the exact existing ASCII label.
 FString Text;{FUTF8ToTCHAR U(reinterpret_cast<const ANSICHAR*>(Bad.CanonicalPayload.GetData()),Bad.CanonicalPayload.Num());Text=FString(U.Length(),U.Get());}
 Text=Text.Replace(TEXT("bound-run-only-v2"),TEXT("bound-run-only-v1"),ESearchCase::CaseSensitive);FTCHARToUTF8 UTF(*Text,Text.Len());Bad.CanonicalPayload.Reset();Bad.CanonicalPayload.Append(reinterpret_cast<const uint8*>(UTF.Get()),UTF.Length());Reject(Bad,D.Context,TEXT("V2 cannot read wrongV1 wrapperlabel around validV2 root"));
 auto C=D.Context;C.ProfilesDirectory=D.Root/DungeonRunSaveAdapter::DirectoryName;Reject(Oracle,C,TEXT("V2 cannot alias old namespace"));
 C=D.Context;C.Scope=Save::EScope::Unsupported;Reject(Oracle,C,TEXT("Unknown V2 scope rejects"));
 C=D.Context;C.ExpectedRunGuid=FGuid::NewGuid();Reject(Oracle,C,TEXT("Expected Run identity binds wholeV2"));
 auto LegacyOut=Out;const auto Before=GenerationSig(LegacyOut);auto LegacyRequest=R;LegacyRequest.RunGuid=Legacy.RunGuid;LegacyRequest.OwnerId=Legacy.OwnerId;
 TestTrue(TEXT("V2 refuses oldRoot without silently migrating and preservesoutput"),!Save::MakeGeneration(Legacy,LegacyRequest,LegacyOut,Why)&&GenerationSig(LegacyOut)==Before);
 auto OldOut=Old;V1.RunGuid=S.RunGuid;V1.OwnerId=S.OwnerId;TestTrue(TEXT("Existing V1 still refuses GuardRoot2 byteatomically"),!DungeonRunSaveAdapter::MakeGeneration(S,V1,OldOut,Why)&&GenerationSig(OldOut)==GenerationSig(Old));
 V1.RunGuid=Legacy.RunGuid;V1.OwnerId=Legacy.OwnerId;Store::FGeneration OldAgain;
 TestTrue(TEXT("Old V1 bytes stay unchanged after V2 operations"),DungeonRunSaveAdapter::MakeGeneration(Legacy,V1,OldAgain,Why)&&GenerationSig(OldAgain)==GenerationSig(Old));return true;
}
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDungeonGuardDiskV2Slots,
 "CodexDungeon.Content.StoneGuardDiskV2.RealSlotsFreshStoreAndHighestBadHead",
 EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FDungeonGuardDiskV2Slots::RunTest(const FString& Parameters)
{
 (void)Parameters;using namespace DiskV2Tests;FGuardWorld W(*this);FDungeonRunSnapshot S;FDungeonValidatedRun V;if(!Source(W,S,V))return false;
 FDisk D(*this);if(!D.IO())return false;Store::FGenerationStore Disk(D.Context.ProfilesDirectory,D.Context.ProfileId,Save::CurrentVersions);
 auto R=D.Request(S);const auto G1=Expected(S,R);if(!Seed(D,Disk,S,G1))return false;
 Store::FGenerationStore Contender(D.Context.ProfilesDirectory,D.Context.ProfileId,Save::CurrentVersions);
 if(!TestEqual(TEXT("Real secondOS writer is excluded fromV2 profile"),int32(Contender.OpenWriter()),int32(Store::EStatus::WriterBusy)))return false;
 R.GenerationId=2;R.ParentGeneration=1;const auto G2=Expected(S,R);const auto Commit=Save::Commit(Disk,S,R);
 if(!TestEqual(TEXT("Implemented V2 commits actualgen2 through full mandatorycallback (Stage0 RED)"),int32(Commit.Status),int32(Store::EStatus::Ok))){AddInfo(Commit.Diagnostic);return false;}
 TestTrue(TEXT("Successful newV2 publication reports exactgeneration and unambiguous receipt"),Commit.GenerationId==2&&!Commit.Replayed&&!Commit.PublicationMayHaveSucceeded&&Commit.BundleByteLength>0);
 Disk.CloseWriter();Store::FGenerationStore Fresh(D.Context.ProfilesDirectory,D.Context.ProfileId,Save::CurrentVersions);Save::FLoadedRun Loaded;
 const auto Read=Save::Load(Fresh,D.Context,Loaded);if(!TestTrue(TEXT("Fresh Store object reads actualhighestB2 and sealedGuard root"),Read.Status==Store::EStatus::Ok&&Read.ObservedHeadGeneration==2&&Read.Slot==Store::ESlot::B&&Loaded.Run.IsValid()))return false;
 TestTrue(TEXT("Fresh diskheader/payload/allnativevalues exact against independentgen2 oracle"),GenerationSig(Loaded.Generation)==GenerationSig(G2)&&RunSig(*Loaded.Run.Get())==RunSig(S));
 auto Previous=Loaded;const auto* Pointer=Previous.Run.Get();const auto Before=LoadedSig(Previous);
 auto WrongContext=D.Context;WrongContext.ExpectedOwnerId=S.OwnerId+1;const auto WrongRead=Save::Load(Fresh,WrongContext,Previous);
 TestTrue(TEXT("Semantic callerbinding failure leaves previous loadedhead/slot/sealedpointer/values unchanged"),WrongRead.Status==Store::EStatus::RecoveryRequired&&WrongRead.ObservedHeadGeneration==2&&Previous.Run.Get()==Pointer&&LoadedSig(Previous)==Before);
 const FString Bundle=Fresh.GetProfileDirectory()/TEXT("slot-B.bundle.json");TArray<uint8> Bytes;
 if(!TestTrue(TEXT("Actual legalB2 persistedbundle exists before deliberate tamper"),FFileHelper::LoadFileToArray(Bytes,*Bundle)&&!Bytes.IsEmpty()))return false;
 Bytes.Last()^=1;if(!TestTrue(TEXT("Actually corrupt currenthighestB2 bytes while preserving olderA1"),FFileHelper::SaveArrayToFile(Bytes,*Bundle)))return false;
 const auto Bad=Save::Load(Fresh,D.Context,Previous);
 TestTrue(TEXT("Bad highestB2 is RecoveryRequired withobserved2 and never quietlyfallbackA1"),Bad.Status==Store::EStatus::RecoveryRequired&&Bad.ObservedHeadGeneration==2&&Previous.Run.Get()==Pointer&&LoadedSig(Previous)==Before);
 return true;
}
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDungeonGuardDiskV2Pristine,
 "CodexDungeon.Content.StoneGuardDiskV2.PristineInstallDeadlinesAndDeathObserver",
 EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FDungeonGuardDiskV2Pristine::RunTest(const FString& Parameters)
{
 (void)Parameters;using namespace DiskV2Tests;FGuardWorld W(*this);FDungeonRunSnapshot S;FDungeonValidatedRun Valid;if(!Source(W,S,Valid))return false;
 FDisk D(*this);if(!D.IO())return false;{Store::FGenerationStore Writer(D.Context.ProfilesDirectory,D.Context.ProfileId,Save::CurrentVersions);if(!Seed(D,Writer,S,Expected(S,D.Request(S))))return false;}
 FV2PristineNativeWorld T(*this);if(!T.Create(true))return false;FString Why;
 if(!TestTrue(TEXT("Actual nativeInit/Login/BeginPlay target is closed noPawn/noRun/noStarter/noCombatRNG"),NoPublishedRun(T)&&T.Fighters()==0&&T.Pawns()==0&&T.Game->IsPristineContinueBootstrap(Why)&&T.Game->GetRunInstallGate()==EDungeonRunInstallGate::PristineBootstrap))return false;
 Store::FGenerationStore Fresh(D.Context.ProfilesDirectory,D.Context.ProfileId,Save::CurrentVersions);FDungeonPreparedRun Prepared;Save::FLoadedRun Loaded;
 const auto R=Save::LoadAndPreparePristine(*T.Game,Fresh,D.Context,Prepared,Loaded);
 if(!TestTrue(TEXT("Implemented V2 diskLoad fullyseals and prepares real pristine group (Stage0 RED)"),R.Status==Store::EStatus::Ok&&Prepared.IsReady()&&Loaded.Run.IsValid())){AddInfo(R.Diagnostic);return false;}
 TestTrue(TEXT("Pristine preparation doesnot publishRun/createStarter/advanceclocks"),NoPublishedRun(T)&&T.Game->GetRunInstallGate()==EDungeonRunInstallGate::Preparing&&T.Controller->GetPawn()==nullptr&&RunSig(*Loaded.Run.Get())==RunSig(S));
 for(const auto& A:Prepared.GetStagedActors())TestTrue(TEXT("Every genuinely staged resource stays hidden/tickoff/collisionoff"),A.IsValid()&&A->IsHidden()&&!A->IsActorTickEnabled()&&!A->GetActorEnableCollision());
 FGuardWorld Ordinary(*this);if(!TestTrue(TEXT("Genuine ordinarytarget exists forpristine refusal"),Ordinary.Create()))return false;FDungeonRunSnapshot Old;if(!Ordinary.Game->CaptureRunSnapshot(Old,Why))return false;
 const auto* PreparedPtr=Prepared.GetSavedSnapshot();const auto Staged=Prepared.GetStagedActors();const auto* LoadedPtr=Loaded.Run.Get();const auto LoadedBefore=LoadedSig(Loaded);
 const auto Refused=Save::LoadAndPreparePristine(*Ordinary.Game,Fresh,D.Context,Prepared,Loaded);FDungeonRunSnapshot OrdinaryAfter;
 TestTrue(TEXT("Pristine refusal is outputatomic even for nonempty unrelated prepared/loaded outputs and ordinaryliveRun"),Refused.Status==Store::EStatus::ValidatorRejected&&Prepared.GetSavedSnapshot()==PreparedPtr&&Prepared.GetStagedActors()==Staged&&Loaded.Run.Get()==LoadedPtr&&LoadedSig(Loaded)==LoadedBefore&&Ordinary.Game->CaptureRunSnapshot(OrdinaryAfter,Why)&&RunSig(Old)==RunSig(OrdinaryAfter));
 if(!TestTrue(TEXT("Actual existing Installer atomically installs fullyloaded GuardV2 without beginning newRun"),FDungeonRunInstaller::Install(*T.Game,Prepared,Why)&&!Prepared.IsReady()))return false;
 FDungeonRunSnapshot Back;if(!TestTrue(TEXT("Actual paused native readback includes allGuard/other owners exact"),T.Game->CaptureRunSnapshot(Back,Why)&&RunSig(Back)==RunSig(S)&&T.Game->GetRunRestartSerial()==0&&T.Game->GetRunInstallGate()==EDungeonRunInstallGate::AwaitExplicitContinue&&T.Controller->GetPawn()==T.Game->PlayerFighter))return false;
 T.Frame(.2f);FDungeonRunSnapshot Paused;TestTrue(TEXT("Paused diskContinue preserves allsaved nativeproducer/display/history/deadlines"),T.Game->CaptureRunSnapshot(Paused,Why)&&RunSig(Paused)==RunSig(S));
 T.Frame(.005f);if(!T.Key(EKeys::Enter,true))return false;T.Frame(.005f);if(!T.Key(EKeys::Enter,false))return false;
 if(!TestTrue(TEXT("Real neutralfreshEnter opensgate without RunRestart or advancing admissionclock"),T.Game->GetRunInstallGate()==EDungeonRunInstallGate::Open&&T.Game->GetSimulationTime()==S.SimulationTime&&T.Game->GetRunRestartSerial()==0))return false;
 ADungeonFighter* GuardActor=nullptr;const uint64 GuardId=W.Guard->GetRuntimeEntityId();for(auto E:T.Game->Enemies)if(E&&E->GetRuntimeEntityId()==GuardId)GuardActor=E;
 if(!TestTrue(TEXT("Installed actual003 hasdedicated Driver/birth/policy"),GuardActor&&GuardActor->GetStoneGuardDriver()))return false;
 const auto SavedState=W.State();const double End=SavedState.Action.ActiveEnd+.02;
 if(!TestTrue(TEXT("Both real original anddiskrestored Guard reach original absoluteaction deadline"),W.AdvanceTo(End)&&T.AdvanceTo(End)))return false;
 TestTrue(TEXT("Guard samefuture clocks/windows/hits and onceoutgoing receipt survive diskContinue"),StateSig(W.State())==StateSig(GuardActor->GetStoneGuardDriver()->State())&&W.Player->Health==T.Game->PlayerFighter->Health);
 W.Guard->ApplyCombatHit(1.6f,W.Player,0.f);GuardActor->ApplyCombatHit(1.6f,T.Game->PlayerFighter,0.f);
 TestTrue(TEXT("Next actualnative mitigation receipt advances exactlyfrom savedcursor without heal/reset"),StateSig(W.State())==StateSig(GuardActor->GetStoneGuardDriver()->State())&&GuardActor->GetStoneGuardDriver()->State().LastDamageReceiptId==SavedState.LastDamageReceiptId+1);
 GuardActor->ApplyCombatHit(100000.f,T.Game->PlayerFighter,85.f);if(!TestTrue(TEXT("Actual lethal native death is observed andlocaleligibility claimed once withoutformaldeath"),GuardActor->bDead&&GuardActor->IsStoneGuardDeathObserved()&&!GuardActor->bDeathReported&&GuardActor->ClaimStoneGuardDeathEligibility()&&!GuardActor->ClaimStoneGuardDeathEligibility()))return false;
 T.Game->LastMessage=TEXT("disk-v2-death-observer-no-replay");FDungeonRunSnapshot Dead;
 if(!TestTrue(TEXT("Actual deadlocalclaimed Guard still captures completelegal Root2"),T.Game->CaptureRunSnapshot(Dead,Why)))return false;
 {Store::FGenerationStore Writer(D.Context.ProfilesDirectory,D.Context.ProfileId,Save::CurrentVersions);if(!TestEqual(TEXT("Actual V2 deathsave writer opens"),int32(Writer.OpenWriter()),int32(Store::EStatus::Ok)))return false;const auto C=Save::Commit(Writer,Dead,D.Request(Dead,2,1));if(!TestEqual(TEXT("Actual deadGuard completegeneration2 publishes"),int32(C.Status),int32(Store::EStatus::Ok)))return false;}
 FV2PristineNativeWorld DT(*this);if(!DT.Create(true))return false;Store::FGenerationStore DeadFresh(D.Context.ProfilesDirectory,D.Context.ProfileId,Save::CurrentVersions);FDungeonPreparedRun DP;Save::FLoadedRun DL;
 if(!TestTrue(TEXT("Fresh actualV2 head2 loads/prepares/installs into second nativepristine target"),Save::LoadAndPreparePristine(*DT.Game,DeadFresh,D.Context,DP,DL).Status==Store::EStatus::Ok&&DL.ObservedHeadGeneration==2&&FDungeonRunInstaller::Install(*DT.Game,DP,Why)))return false;
 FDungeonRunSnapshot DeadBack;if(!TestTrue(TEXT("Dead observer/localclaim/formaldeath allsurvive full disk/native readback independently"),DT.Game->CaptureRunSnapshot(DeadBack,Why)&&RunSig(DeadBack)==RunSig(Dead)))return false;
 ADungeonFighter* DeadActor=nullptr;for(auto E:DT.Game->Enemies)if(E&&E->GetRuntimeEntityId()==GuardId)DeadActor=E;
 if(!TestTrue(TEXT("Dedicated native deadGuard is observed/localclaimed butnotformallysettled"),DeadActor&&DeadActor->GetStoneGuardDriver()&&DeadActor->IsStoneGuardDeathObserved()&&DeadActor->GetStoneGuardDriver()->State().RewardClaimed&&!DeadActor->bDeathReported))return false;
 DT.Frame(.005f);if(!DT.Key(EKeys::Enter,true))return false;DT.Frame(.005f);if(!DT.Key(EKeys::Enter,false))return false;
 const auto Cursor=DeadActor->GetStoneGuardDriver()->State().NextEventId;const auto Histories=DeadActor->GetStoneGuardDriver()->State().Issued.size();const int32 Coins=DT.Game->PlayerFighter->Coins,Pickups=DT.Game->Pickups.Num();DT.Game->OnFighterDied(DeadActor);DT.Game->OnFighterDied(DeadActor);DT.Frame(.02f);
 TestTrue(TEXT("Resumed deadobserver neverreplays Died/eligibility/message/coins/pickups or newRun"),DeadActor->GetStoneGuardDriver()->State().NextEventId==Cursor&&DeadActor->GetStoneGuardDriver()->State().Issued.size()==Histories&&!DeadActor->ClaimStoneGuardDeathEligibility()&&DT.Game->LastMessage==Dead.LastMessage&&DT.Game->PlayerFighter->Coins==Coins&&DT.Game->Pickups.Num()==Pickups&&DT.Game->GetRunRestartSerial()==0);
 return true;
}
#endif
