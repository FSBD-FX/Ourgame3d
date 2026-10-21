#if WITH_DEV_AUTOMATION_TESTS
#include "Misc/AutomationTest.h"
#include "../DungeonSaveGenerationStore.h"
#include "HAL/FileManager.h"
#include "Misc/FileHelper.h"
#include "Misc/Crc.h"
#include "Misc/Paths.h"

namespace
{
namespace SaveGen=DungeonSaveGenerationStore;
TArray<uint8> Utf8(const FString& Text)
{
    FTCHARToUTF8 Converted(*Text);TArray<uint8> Out;
    Out.Append(reinterpret_cast<const uint8*>(Converted.Get()),Converted.Length());return Out;
}
const SaveGen::FVersions CurrentVersions{TEXT("save-root-v1"),TEXT("content-frozen-v1"),TEXT("world-cm-v1")};
const SaveGen::FPayloadValidator Accept=[](const SaveGen::FGeneration& G,FString& Why)
{
    if(G.CanonicalPayload.IsEmpty()){Why=TEXT("Missing complete caller payload");return false;}return true;
};
bool Status(FAutomationTestBase& Test,const TCHAR* Label,SaveGen::EStatus Actual,SaveGen::EStatus Expected)
{return Test.TestEqual(Label,int32(Actual),int32(Expected));}
struct FDiskFixture
{
    FAutomationTestBase& Test;FGuid Profile=FGuid::NewGuid();FString Root;
    explicit FDiskFixture(FAutomationTestBase& InTest):Test(InTest)
    {
        Root=FPaths::ConvertRelativePathToFull(FPaths::ProjectSavedDir()/TEXT("Automation/SaveGenerationStore")/
            FGuid::NewGuid().ToString(EGuidFormats::Digits));
        Test.AddInfo(TEXT("Retained real isolated IO evidence: ")+Root);
    }
    bool ProveFixtureIO()
    {
        const FString Path=Root/TEXT("fixture-io-proof.txt");
        const auto Expected=Utf8(TEXT("real temporary-directory IO; no game state\n"));TArray<uint8> Read;
        return Test.TestTrue(TEXT("Create isolated IO directory"),IFileManager::Get().MakeDirectory(*Root,true))
            &&Test.TestTrue(TEXT("Fixture really writes bytes"),FFileHelper::SaveArrayToFile(Expected,*Path))
            &&Test.TestTrue(TEXT("Fixture really reads bytes"),FFileHelper::LoadFileToArray(Read,*Path))
            &&Test.TestTrue(TEXT("Fixture disk bytes match"),Read==Expected);
    }
    SaveGen::FGeneration Candidate(uint64 Id=1,uint64 Parent=0,const SaveGen::FVersions& Versions=CurrentVersions)const
    {
        SaveGen::FGeneration G;G.ProfileId=Profile;G.GenerationId=Id;G.ParentGeneration=Parent;
        G.Versions=Versions;G.BuildId=TEXT("automation-save-store-v1");G.RunSimulationTime=60.407882462998735;
        G.CanonicalPayload=Utf8(TEXT("{\"account\":{\"active_run\":\"same-run\",\"shards\":7},\"activeRun\":{\"action\":{\"deadline\":60.407882462998735,\"emitted\":[\"18446744073709551614\"],\"future\":[1,2]},\"armor\":{\"affix\":-13,\"q\":[-5,17]},\"owner_tombstone\":\"dead-owner\"},\"journal\":[{\"operation\":\"18446744073709551613\",\"result\":\"committed\"}],\"settings\":{\"name\":\"钟盔\"}}"));
        return G;
    }
    bool Seed(SaveGen::FGenerationStore& Store,uint64 Count=1)
    {
        Status(Test,TEXT("Real profile writer opens"),Store.OpenWriter(),SaveGen::EStatus::Ok);
        for(uint64 N=1;N<=Count;++N)
        {
            const auto R=Store.Commit(Candidate(N,N-1),Accept);
            if(!Status(Test,TEXT("Seed complete real published generation"),R.Status,SaveGen::EStatus::Ok))return false;
        }
        return true;
    }
    FString File(const SaveGen::FGenerationStore& Store,SaveGen::ESlot Slot,const TCHAR* Suffix)const
    {return Store.GetProfileDirectory()/(FString(Slot==SaveGen::ESlot::A?TEXT("slot-A."):TEXT("slot-B."))+Suffix);}
    TArray<uint8> Read(const FString& Path)
    {TArray<uint8> B;Test.TestTrue(TEXT("Read actual generation file"),FFileHelper::LoadFileToArray(B,*Path));return B;}
    bool Write(const FString& Path,const TArray<uint8>& Bytes)
    {return Test.TestTrue(TEXT("Inject actual fixture bytes"),FFileHelper::SaveArrayToFile(Bytes,*Path));}
};
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDungeonSaveGenerationRoundTrip,
    "CodexDungeon.Content.SaveGenerationStore.ByteRoundTripAndGenerationIdentity",
    EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FDungeonSaveGenerationRoundTrip::RunTest(const FString&)
{
    FDiskFixture F(*this);if(!F.ProveFixtureIO())return false;
    TestEqual(TEXT("Independent published SHA256 abc vector"),SaveGen::FGenerationStore::Sha256(Utf8(TEXT("abc"))),
        FString(TEXT("ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad")));
    SaveGen::FGenerationStore S(F.Root,F.Profile,CurrentVersions);
    Status(*this,TEXT("Only genuinely absent profile is Empty"),S.Load(Accept).Status,SaveGen::EStatus::Empty);
    if(!F.Seed(S))return false;
    auto L=S.Load(Accept);Status(*this,TEXT("First real generation loads"),L.Status,SaveGen::EStatus::Ok);
    TestTrue(TEXT("Whole Unicode payload is byte exact, including high integer strings and future state"),L.Generation.CanonicalPayload==F.Candidate().CanonicalPayload);
    TestTrue(TEXT("Exact simulation double survives"),L.Generation.RunSimulationTime.IsSet()&&L.Generation.RunSimulationTime.GetValue()==F.Candidate().RunSimulationTime.GetValue());
    TestTrue(TEXT("Profile and all three versions survive"),L.Generation.ProfileId==F.Profile&&L.Generation.Versions==CurrentVersions);
    TestTrue(TEXT("First generation is A with no parent"),L.Slot==SaveGen::ESlot::A&&L.Generation.GenerationId==1&&L.Generation.ParentGeneration==0);
    const auto OldBundle=F.Read(F.File(S,SaveGen::ESlot::A,TEXT("bundle.json")));
    const auto OldMarker=F.Read(F.File(S,SaveGen::ESlot::A,TEXT("commit.json")));
    auto Next=F.Candidate(2,1);Next.CanonicalPayload=Utf8(TEXT("{\"account\":{\"shards\":6},\"activeRun\":{\"sameRun\":true},\"journal\":[1,2],\"settings\":{}}"));
    const auto R=S.Commit(Next,Accept);Status(*this,TEXT("Second complete generation publishes"),R.Status,SaveGen::EStatus::Ok);
    TestTrue(TEXT("Actual bundle SHA/CRC/length receipt is present"),R.BundleSha256.Len()==64&&R.BundleByteLength>Next.CanonicalPayload.Num());
    const auto ActualBundle=F.Read(F.File(S,SaveGen::ESlot::B,TEXT("bundle.json")));
    TestEqual(TEXT("Receipt CRC equals independent actual disk bytes"),R.BundleCrc32,FCrc::MemCrc32(ActualBundle.GetData(),ActualBundle.Num()));
    TestTrue(TEXT("Receipt byte length and SHA bind actual entire envelope"),R.BundleByteLength==ActualBundle.Num()&&R.BundleSha256==SaveGen::FGenerationStore::Sha256(ActualBundle));
    L=S.Load(Accept);Status(*this,TEXT("Latest complete generation loads"),L.Status,SaveGen::EStatus::Ok);
    TestTrue(TEXT("B generation2 is exact new whole payload"),L.Slot==SaveGen::ESlot::B&&L.Generation.GenerationId==2&&L.Generation.ParentGeneration==1&&L.Generation.CanonicalPayload==Next.CanonicalPayload);
    TestTrue(TEXT("Publishing B preserves A bundle and marker byte for byte"),OldBundle==F.Read(F.File(S,SaveGen::ESlot::A,TEXT("bundle.json")))&&OldMarker==F.Read(F.File(S,SaveGen::ESlot::A,TEXT("commit.json"))));
    S.CloseWriter();SaveGen::FGenerationStore Reopened(F.Root,F.Profile,CurrentVersions);
    L=Reopened.Load(Accept);Status(*this,TEXT("Fresh storage object reads real files, no cached candidate"),L.Status,SaveGen::EStatus::Ok);
    TestTrue(TEXT("Fresh object gets exact committed bytes"),L.Generation.CanonicalPayload==Next.CanonicalPayload);return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDungeonSaveGenerationValidation,
    "CodexDungeon.Content.SaveGenerationStore.WholePayloadValidatorAndVersionGates",
    EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FDungeonSaveGenerationValidation::RunTest(const FString&)
{
    FDiskFixture F(*this);if(!F.ProveFixtureIO())return false;SaveGen::FGenerationStore S(F.Root,F.Profile,CurrentVersions);
    if(!F.Seed(S))return false;const auto Old=F.Read(F.File(S,SaveGen::ESlot::A,TEXT("bundle.json")));
    int32 Calls=0;const SaveGen::FPayloadValidator Reject=[&](const SaveGen::FGeneration& G,FString& Why)
    {++Calls;TestTrue(TEXT("Validator sees complete original candidate bytes"),G.CanonicalPayload==F.Candidate(2,1).CanonicalPayload);Why=TEXT("Authoritative cross-scope mismatch");return false;};
    Status(*this,TEXT("Semantic validator denies publication"),S.Commit(F.Candidate(2,1),Reject).Status,SaveGen::EStatus::ValidatorRejected);
    TestEqual(TEXT("Validator called exactly once before publication"),Calls,1);
    TestFalse(TEXT("Rejected candidate has no published marker"),IFileManager::Get().FileExists(*F.File(S,SaveGen::ESlot::B,TEXT("commit.json"))));
    TestTrue(TEXT("Rejected candidate leaves old bytes"),Old==F.Read(F.File(S,SaveGen::ESlot::A,TEXT("bundle.json"))));
    Status(*this,TEXT("Missing caller validator rejected"),S.Commit(F.Candidate(2,1),{}).Status,SaveGen::EStatus::InvalidRequest);
    for(const FString Bad:{TEXT("{\"a\":1,\"a\":2}"),TEXT("{\"a\":1,\"\\u0061\":2}"),TEXT("{\"x\":NaN}"),TEXT("{\"x\":1e999}"),TEXT("[]")})
    {
        auto G=F.Candidate(2,1);G.CanonicalPayload=Utf8(Bad);
        Status(*this,TEXT("Invalid full JSON object cannot be published"),S.Commit(G,Accept).Status,SaveGen::EStatus::InvalidRequest);
    }
    auto G=F.Candidate(2,1);G.CanonicalPayload={uint8('{'),uint8('"'),0xff,uint8('"'),uint8(':'),uint8('0'),uint8('}')};
    Status(*this,TEXT("Invalid UTF8 cannot be laundered by replacement characters"),S.Commit(G,Accept).Status,SaveGen::EStatus::InvalidRequest);
    S.CloseWriter();
    for(int32 Kind=0;Kind<3;++Kind)
    {
    SaveGen::FVersions Future=CurrentVersions;
    if(Kind==0)Future.Schema=TEXT("future-root-v2");
    if(Kind==1)Future.ContentRules=TEXT("future-rules-v9");
    if(Kind==2)Future.Coordinates=TEXT("future-coordinate-v9");
    // Produce both version branches through actual commits. Copy an intact
    // compatible A1 pair under the same ProfileID into the newer fixture;
    // never manufacture a successful marker or bypass production integrity.
    FDiskFixture N(*this);N.Profile=F.Profile;if(!N.ProveFixtureIO())return false;
    SaveGen::FGenerationStore Newer(N.Root,N.Profile,Future);
    Status(*this,TEXT("Known future-format writer opens"),Newer.OpenWriter(),SaveGen::EStatus::Ok);
    Status(*this,TEXT("Real unknown-to-reader first version publishes"),Newer.Commit(N.Candidate(1,0,Future),Accept).Status,SaveGen::EStatus::Ok);
    Status(*this,TEXT("Real unknown-to-reader newest B2 publishes"),Newer.Commit(N.Candidate(2,1,Future),Accept).Status,SaveGen::EStatus::Ok);Newer.CloseWriter();
    for(const TCHAR* Suffix:{TEXT("bundle.json"),TEXT("commit.json")})
        if(!N.Write(N.File(Newer,SaveGen::ESlot::A,Suffix),F.Read(F.File(S,SaveGen::ESlot::A,Suffix))))return false;
    SaveGen::FGenerationStore OlderReader(N.Root,N.Profile,CurrentVersions);
    const auto Unknown=OlderReader.Load(Accept);
    Status(*this,TEXT("Unknown newest B2 requires recovery despite compatible intact A1"),Unknown.Status,SaveGen::EStatus::RecoveryRequired);
    TestEqual(TEXT("Select highest published before checking compatibility"),Unknown.ObservedHeadGeneration,uint64(2));
    Status(*this,TEXT("Normal commit cannot overwrite unknown newest version"),OlderReader.OpenWriter(),SaveGen::EStatus::Ok);
    Status(*this,TEXT("No implicit version migration through ordinary Commit"),OlderReader.Commit(N.Candidate(3,2),Accept).Status,SaveGen::EStatus::RecoveryRequired);
    }
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDungeonSaveGenerationCorruption,
    "CodexDungeon.Content.SaveGenerationStore.CorruptionRequiresExplicitRecovery",
    EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FDungeonSaveGenerationCorruption::RunTest(const FString&)
{
    for(int32 Kind=0;Kind<4;++Kind)
    {
        FDiskFixture F(*this);if(!F.ProveFixtureIO())return false;SaveGen::FGenerationStore S(F.Root,F.Profile,CurrentVersions);
        if(!F.Seed(S,2))return false;const FString Bundle=F.File(S,SaveGen::ESlot::B,TEXT("bundle.json"));
        const FString Marker=F.File(S,SaveGen::ESlot::B,TEXT("commit.json"));
        if(Kind==0){auto B=F.Read(Bundle);B.SetNum(B.Num()/2);if(!F.Write(Bundle,B))return false;}
        if(Kind==1){auto B=F.Read(Bundle);B[B.Num()/2]^=1;if(!F.Write(Bundle,B))return false;}
        if(Kind==2)TestTrue(TEXT("Delete actual highest bundle fixture"),IFileManager::Get().Delete(*Bundle));
        if(Kind==3){auto B=F.Read(Marker);B.SetNum(7);if(!F.Write(Marker,B))return false;}
        const auto Old=F.Read(F.File(S,SaveGen::ESlot::A,TEXT("bundle.json")));
        Status(*this,TEXT("Damaged highest generation never silently falls back to valid A"),S.Load(Accept).Status,SaveGen::EStatus::RecoveryRequired);
        Status(*this,TEXT("Ordinary commit cannot overwrite unresolved recovery evidence"),S.Commit(F.Candidate(3,2),Accept).Status,SaveGen::EStatus::RecoveryRequired);
        TestTrue(TEXT("Read/failed normal commit retain backup bytes"),Old==F.Read(F.File(S,SaveGen::ESlot::A,TEXT("bundle.json"))));
    }
    // Both pairs are genuine published outputs, with valid SHA/CRC/length.
    // Reintroducing intact A1 beside B4 leaves an unexplained parent3 gap.
    // Ordinary Commit must preserve that evidence just as ordinary Load does.
    FDiskFixture Gap(*this);if(!Gap.ProveFixtureIO())return false;
    SaveGen::FGenerationStore BrokenChain(Gap.Root,Gap.Profile,CurrentVersions);
    if(!Gap.Seed(BrokenChain))return false;
    const auto OriginalA=Gap.Read(Gap.File(BrokenChain,SaveGen::ESlot::A,TEXT("bundle.json")));
    const auto OriginalAMarker=Gap.Read(Gap.File(BrokenChain,SaveGen::ESlot::A,TEXT("commit.json")));
    for(uint64 N=2;N<=4;++N)
        if(!Status(*this,TEXT("Produce real generation chain through B4"),BrokenChain.Commit(Gap.Candidate(N,N-1),Accept).Status,SaveGen::EStatus::Ok))return false;
    const auto CurrentB=Gap.Read(Gap.File(BrokenChain,SaveGen::ESlot::B,TEXT("bundle.json")));
    const auto CurrentBMarker=Gap.Read(Gap.File(BrokenChain,SaveGen::ESlot::B,TEXT("commit.json")));
    if(!Gap.Write(Gap.File(BrokenChain,SaveGen::ESlot::A,TEXT("bundle.json")),OriginalA)
        ||!Gap.Write(Gap.File(BrokenChain,SaveGen::ESlot::A,TEXT("commit.json")),OriginalAMarker))return false;
    const auto Before=BrokenChain.Load(Accept);
    Status(*this,TEXT("Valid A1/B4 pairs still require parent-gap recovery"),Before.Status,SaveGen::EStatus::RecoveryRequired);
    TestEqual(TEXT("Parent-gap diagnosis retains true highest published identity"),Before.ObservedHeadGeneration,uint64(4));
    Status(*this,TEXT("Same-generation B4 retry cannot bypass parent-gap recovery"),BrokenChain.Commit(Gap.Candidate(4,3),Accept).Status,SaveGen::EStatus::RecoveryRequired);
    TestTrue(TEXT("Rejected gap replay leaves both pairs byte exact"),
        OriginalA==Gap.Read(Gap.File(BrokenChain,SaveGen::ESlot::A,TEXT("bundle.json")))
        &&OriginalAMarker==Gap.Read(Gap.File(BrokenChain,SaveGen::ESlot::A,TEXT("commit.json")))
        &&CurrentB==Gap.Read(Gap.File(BrokenChain,SaveGen::ESlot::B,TEXT("bundle.json")))
        &&CurrentBMarker==Gap.Read(Gap.File(BrokenChain,SaveGen::ESlot::B,TEXT("commit.json"))));
    Status(*this,TEXT("Normal Commit5 cannot wash unresolved parent gap"),BrokenChain.Commit(Gap.Candidate(5,4),Accept).Status,SaveGen::EStatus::RecoveryRequired);
    TestTrue(TEXT("Rejected gap commit leaves both original pairs byte exact"),
        OriginalA==Gap.Read(Gap.File(BrokenChain,SaveGen::ESlot::A,TEXT("bundle.json")))
        &&OriginalAMarker==Gap.Read(Gap.File(BrokenChain,SaveGen::ESlot::A,TEXT("commit.json")))
        &&CurrentB==Gap.Read(Gap.File(BrokenChain,SaveGen::ESlot::B,TEXT("bundle.json")))
        &&CurrentBMarker==Gap.Read(Gap.File(BrokenChain,SaveGen::ESlot::B,TEXT("commit.json"))));
    AddInfo(TEXT("Actual parent-gap fixture uses intact original A1 beside intact published B4; normal commit5 must remain refused."));
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDungeonSaveGenerationFaults,
    "CodexDungeon.Content.SaveGenerationStore.EveryCommitBoundaryRetainsPublishedBytes",
    EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FDungeonSaveGenerationFaults::RunTest(const FString&)
{
    for(int32 P=int32(SaveGen::EFaultPoint::PartialBundleWrite);P<=int32(SaveGen::EFaultPoint::AfterMarkerPublish);++P)
    {
        FDiskFixture F(*this);if(!F.ProveFixtureIO())return false;SaveGen::FGenerationStore S(F.Root,F.Profile,CurrentVersions);
        if(!F.Seed(S,2))return false;const auto Bundle=F.Read(F.File(S,SaveGen::ESlot::B,TEXT("bundle.json")));
        const auto Marker=F.Read(F.File(S,SaveGen::ESlot::B,TEXT("commit.json")));
        const auto R=S.Commit(F.Candidate(3,2),Accept,SaveGen::EFaultPoint(P));
        Status(*this,TEXT("Real IO fault hook reports interrupted commit"),R.Status,SaveGen::EStatus::InjectedFailure);
        TestTrue(TEXT("Prior published active slot remains exact at every boundary"),Bundle==F.Read(F.File(S,SaveGen::ESlot::B,TEXT("bundle.json")))&&Marker==F.Read(F.File(S,SaveGen::ESlot::B,TEXT("commit.json"))));
        S.CloseWriter();SaveGen::FGenerationStore Fresh(F.Root,F.Profile,CurrentVersions);
        const auto L=Fresh.Load(Accept);Status(*this,TEXT("Fresh object selects only actual published bytes"),L.Status,SaveGen::EStatus::Ok);
        const bool Published=P==int32(SaveGen::EFaultPoint::AfterMarkerPublish);
        TestTrue(TEXT("Commit marker is sole logical boundary; unpublished inactive file not promoted"),L.Generation.GenerationId==(Published?3u:2u));
        TestEqual(TEXT("Lost ACK explicitly warns publication may have succeeded"),R.PublicationMayHaveSucceeded,Published);
        Status(*this,TEXT("Retry reacquires lease"),Fresh.OpenWriter(),SaveGen::EStatus::Ok);
        const auto Retry=Fresh.Commit(F.Candidate(3,2),Accept);Status(*this,TEXT("Same immutable candidate retries safely"),Retry.Status,SaveGen::EStatus::Ok);
        TestEqual(TEXT("Only already-published candidate is a replay"),Retry.Replayed,Published);
        AddInfo(FString::Printf(TEXT("Actual named IO boundary %d inspected, old=%llu selected=%llu"),P,2ull,L.Generation.GenerationId));
    }return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDungeonSaveGenerationWriter,
    "CodexDungeon.Content.SaveGenerationStore.ExclusiveWriterAndLostAcknowledgement",
    EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FDungeonSaveGenerationWriter::RunTest(const FString&)
{
    FDiskFixture F(*this);if(!F.ProveFixtureIO())return false;SaveGen::FGenerationStore A(F.Root,F.Profile,CurrentVersions),B(F.Root,F.Profile,CurrentVersions);
    Status(*this,TEXT("First real OS writer lease opens"),A.OpenWriter(),SaveGen::EStatus::Ok);
    Status(*this,TEXT("Independent writer handle is denied by OS, not a static bool"),B.OpenWriter(),SaveGen::EStatus::WriterBusy);
    if(!Status(*this,TEXT("First writer commits"),A.Commit(F.Candidate(),Accept).Status,SaveGen::EStatus::Ok))return false;
    const auto First=F.Read(F.File(A,SaveGen::ESlot::A,TEXT("bundle.json")));
    auto R=A.Commit(F.Candidate(),Accept);Status(*this,TEXT("Same generation/bytes returns durable result"),R.Status,SaveGen::EStatus::Ok);TestTrue(TEXT("Same generation query is replay"),R.Replayed);
    auto Changed=F.Candidate();Changed.CanonicalPayload=Utf8(TEXT("{\"account\":{},\"activeRun\":null,\"journal\":[],\"settings\":{}}"));
    Status(*this,TEXT("Reusing a generation with changed bytes is conflict"),A.Commit(Changed,Accept).Status,SaveGen::EStatus::Conflict);
    TestTrue(TEXT("Conflict does not overwrite bytes"),First==F.Read(F.File(A,SaveGen::ESlot::A,TEXT("bundle.json"))));
    A.CloseWriter();Status(*this,TEXT("Closing owner releases actual OS lease"),B.OpenWriter(),SaveGen::EStatus::Ok);
    Status(*this,TEXT("Former owner without lease cannot commit"),A.Commit(F.Candidate(2,1),Accept).Status,SaveGen::EStatus::WriterBusy);
    Status(*this,TEXT("Read-only observer still loads published state"),A.Load(Accept).Status,SaveGen::EStatus::Ok);return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDungeonSaveGenerationRecovery,
    "CodexDungeon.Content.SaveGenerationStore.UnknownHeadAndExplicitWholeBackupRecovery",
    EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FDungeonSaveGenerationRecovery::RunTest(const FString&)
{
    FDiskFixture F(*this);if(!F.ProveFixtureIO())return false;SaveGen::FGenerationStore S(F.Root,F.Profile,CurrentVersions);
    if(!F.Seed(S,2))return false;const auto Backup=F.Read(F.File(S,SaveGen::ESlot::A,TEXT("bundle.json")));
    const FString BadPath=F.File(S,SaveGen::ESlot::B,TEXT("bundle.json"));auto Bad=F.Read(BadPath);Bad.SetNum(Bad.Num()/2);
    if(!F.Write(BadPath,Bad))return false;
    Status(*this,TEXT("Normal Continue exposes recovery requirement"),S.Load(Accept).Status,SaveGen::EStatus::RecoveryRequired);
    const auto R=S.Recover(SaveGen::ESlot::A,Accept);Status(*this,TEXT("Explicit verified whole A backup publishes new generation"),R.Status,SaveGen::EStatus::Ok);
    TestTrue(TEXT("Recovery archives originals before replacement"),!R.RecoveryArchiveDirectory.IsEmpty()&&Bad==F.Read(R.RecoveryArchiveDirectory/TEXT("slot-B.bundle.json"))&&Backup==F.Read(R.RecoveryArchiveDirectory/TEXT("slot-A.bundle.json")));
    const auto L=S.Load(Accept);Status(*this,TEXT("Recovered complete generation loads"),L.Status,SaveGen::EStatus::Ok);
    TestTrue(TEXT("Recovery is greater than observed head with explicit audit"),L.Generation.GenerationId==3&&L.Generation.ParentGeneration==2&&L.Generation.RestoredFromGeneration==1);
    TestTrue(TEXT("Whole payload copied; no account/Run mixing or new Run initialization"),L.Generation.CanonicalPayload==F.Candidate().CanonicalPayload);
    TestTrue(TEXT("Original backup slot remains intact"),Backup==F.Read(F.File(S,SaveGen::ESlot::A,TEXT("bundle.json"))));
    Status(*this,TEXT("A valid recovered head with existing archive remains readable"),S.Load(Accept).Status,SaveGen::EStatus::Ok);
    Status(*this,TEXT("A valid head with existing archive may commit next normal generation"),S.Commit(F.Candidate(4,3),Accept).Status,SaveGen::EStatus::Ok);
    TestEqual(TEXT("Legal continued generation after archived recovery"),S.Load(Accept).Generation.GenerationId,uint64(4));
    // Use this actual Recover archive, then simulate losing only the rolling
    // root slots. Retained history must never become a first-launch profile.
    TMap<FString,TArray<uint8>> ArchiveBefore;
    for(SaveGen::ESlot Slot:{SaveGen::ESlot::A,SaveGen::ESlot::B})for(const TCHAR* Suffix:{TEXT("bundle.json"),TEXT("commit.json")})
    {
        const FString Name=FString(Slot==SaveGen::ESlot::A?TEXT("slot-A."):TEXT("slot-B."))+Suffix;
        const FString Original=R.RecoveryArchiveDirectory/Name;ArchiveBefore.Add(Original,F.Read(Original));
        const FString RootFile=F.File(S,Slot,Suffix);
        if(!TestTrue(TEXT("Only delete slots inside owned real IO fixture"),RootFile.StartsWith(F.Root+TEXT("/")))
            ||!TestTrue(TEXT("Simulate loss of actual root slot only"),IFileManager::Get().Delete(*RootFile)))return false;
    }
    Status(*this,TEXT("Existing real recovery archive with missing root slots is not Empty"),S.Load(Accept).Status,SaveGen::EStatus::RecoveryRequired);
    Status(*this,TEXT("Commit1 cannot bootstrap over archived Profile history"),S.Commit(F.Candidate(),Accept).Status,SaveGen::EStatus::RecoveryRequired);
    bool ArchiveIntact=true;for(const auto& Entry:ArchiveBefore)ArchiveIntact&=Entry.Value==F.Read(Entry.Key);
    TestTrue(TEXT("Archive-only diagnosis and refused bootstrap preserve every original byte"),ArchiveIntact);
    // Existing unknown evidence is never a fresh launch, even with no marker.
    FDiskFixture U(*this);if(!U.ProveFixtureIO())return false;SaveGen::FGenerationStore Unknown(U.Root,U.Profile,CurrentVersions);
    TestTrue(TEXT("Create unknown-evidence profile directory"),IFileManager::Get().MakeDirectory(*Unknown.GetProfileDirectory(),true));
    if(!U.Write(Unknown.GetProfileDirectory()/TEXT("unknown-legacy.save"),Utf8(TEXT("unresolved evidence"))))return false;
    Status(*this,TEXT("Unknown existing evidence blocks default bootstrap"),Unknown.Load(Accept).Status,SaveGen::EStatus::RecoveryRequired);
    Status(*this,TEXT("Unknown-evidence writer can acquire lease for diagnosis"),Unknown.OpenWriter(),SaveGen::EStatus::Ok);
    Status(*this,TEXT("Unknown evidence cannot be overwritten by new generation1"),Unknown.Commit(U.Candidate(),Accept).Status,SaveGen::EStatus::RecoveryRequired);
    Status(*this,TEXT("Cannot guess an old backup when no trustworthy generation identity exists"),Unknown.Recover(SaveGen::ESlot::A,Accept).Status,SaveGen::EStatus::RecoveryRequired);
    FDiskFixture M(*this);if(!M.ProveFixtureIO())return false;SaveGen::FGenerationStore MigrationOnly(M.Root,M.Profile,CurrentVersions);
    Status(*this,TEXT("Migration evidence fixture owns real writer"),MigrationOnly.OpenWriter(),SaveGen::EStatus::Ok);
    const FString MigrationDir=MigrationOnly.GetProfileDirectory()/TEXT("migration");
    if(!TestTrue(TEXT("Create actual migration-evidence directory"),IFileManager::Get().MakeDirectory(*MigrationDir,true)))return false;
    const FString MigrationFile=MigrationDir/TEXT("unresolved-prior-generation.json");
    const auto MigrationBytes=Utf8(TEXT("{\"unresolved_migration_evidence\":true,\"generation\":\"14\"}"));
    if(!M.Write(MigrationFile,MigrationBytes))return false;
    Status(*this,TEXT("Nonempty migration directory without root markers is not Empty"),MigrationOnly.Load(Accept).Status,SaveGen::EStatus::RecoveryRequired);
    Status(*this,TEXT("Commit1 cannot bootstrap over unresolved migration evidence"),MigrationOnly.Commit(M.Candidate(),Accept).Status,SaveGen::EStatus::RecoveryRequired);
    TestTrue(TEXT("Blocked migration bootstrap retains exact original bytes"),M.Read(MigrationFile)==MigrationBytes);
    FDiskFixture E(*this);if(!E.ProveFixtureIO())return false;SaveGen::FGenerationStore EmptyHistory(E.Root,E.Profile,CurrentVersions);
    Status(*this,TEXT("Empty history fixture writer opens"),EmptyHistory.OpenWriter(),SaveGen::EStatus::Ok);
    for(const TCHAR* Name:{TEXT("recovery"),TEXT("migration")})
        if(!TestTrue(TEXT("Create legal empty history directory"),IFileManager::Get().MakeDirectory(*(EmptyHistory.GetProfileDirectory()/Name),true)))return false;
    Status(*this,TEXT("Truly empty history directories are not historical progress"),EmptyHistory.Load(Accept).Status,SaveGen::EStatus::Empty);
    Status(*this,TEXT("Empty history permits first complete generation"),EmptyHistory.Commit(E.Candidate(),Accept).Status,SaveGen::EStatus::Ok);
    const auto UnmarkedFirst=E.Read(E.File(EmptyHistory,SaveGen::ESlot::A,TEXT("bundle.json")));
    const FString HistoryFile=EmptyHistory.GetProfileDirectory()/TEXT("recovery/unresolved-history.json");
    if(!E.Write(HistoryFile,Utf8(TEXT("{\"prior_profile_evidence\":true}"))))return false;
    const FString LostMarker=E.File(EmptyHistory,SaveGen::ESlot::A,TEXT("commit.json"));
    if(!TestTrue(TEXT("Lost marker remains inside owned fixture"),LostMarker.StartsWith(E.Root+TEXT("/")))
        ||!TestTrue(TEXT("Remove only this fixture marker"),IFileManager::Get().Delete(*LostMarker)))return false;
    Status(*this,TEXT("History plus unmarked matching first bundle still requires recovery"),EmptyHistory.Load(Accept).Status,SaveGen::EStatus::RecoveryRequired);
    Status(*this,TEXT("Identical first-candidate retry exception cannot bypass historical evidence"),EmptyHistory.Commit(E.Candidate(),Accept).Status,SaveGen::EStatus::RecoveryRequired);
    TestTrue(TEXT("Blocked first retry preserves unmarked complete original bytes"),E.Read(E.File(EmptyHistory,SaveGen::ESlot::A,TEXT("bundle.json")))==UnmarkedFirst);
    for(const TCHAR* Name:{TEXT("recovery"),TEXT("migration")})
    {
        FDiskFixture C(*this);if(!C.ProveFixtureIO())return false;SaveGen::FGenerationStore Collision(C.Root,C.Profile,CurrentVersions);
        Status(*this,TEXT("History-name file collision fixture writer opens"),Collision.OpenWriter(),SaveGen::EStatus::Ok);
        const FString File=Collision.GetProfileDirectory()/Name;const auto Bytes=Utf8(TEXT("unresolved history path occupied by a file"));
        if(!C.Write(File,Bytes))return false;
        Status(*this,TEXT("History directory name occupied by a file is unresolved evidence"),Collision.Load(Accept).Status,SaveGen::EStatus::RecoveryRequired);
        Status(*this,TEXT("Directory-name collision cannot bootstrap a Profile"),Collision.Commit(C.Candidate(),Accept).Status,SaveGen::EStatus::RecoveryRequired);
        TestTrue(TEXT("Refused collision bootstrap retains exact original file"),C.Read(File)==Bytes);
    }
    return true;
}
#endif
