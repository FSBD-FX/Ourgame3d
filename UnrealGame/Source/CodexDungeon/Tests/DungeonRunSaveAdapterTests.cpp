#if WITH_DEV_AUTOMATION_TESTS
#include "Misc/AutomationTest.h"
#include "../DungeonRunSaveAdapter.h"
#include "RunCodecFixture_v001.h"
#include "HAL/FileManager.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"

namespace
{
namespace Save=DungeonRunSaveAdapter;
namespace SG=DungeonSaveGenerationStore;
namespace Codec=DungeonRunSnapshotCodec;
TArray<uint8> SaveUtf8(const FString& S)
{FTCHARToUTF8 U(*S,S.Len());TArray<uint8> B;B.Append(reinterpret_cast<const uint8*>(U.Get()),U.Length());return B;}
TArray<uint8> GenerationSignature(const SG::FGeneration& G)
{
    FSignature S;S.V(G.ProfileId.A,G.ProfileId.B,G.ProfileId.C,G.ProfileId.D,G.GenerationId,G.ParentGeneration,G.RestoredFromGeneration);
    S.String(G.Versions.Schema);S.String(G.Versions.ContentRules);S.String(G.Versions.Coordinates);S.String(G.BuildId);
    S.V(G.RunSimulationTime.IsSet());if(G.RunSimulationTime.IsSet())S.V(G.RunSimulationTime.GetValue());
    S.V(G.CanonicalPayload.Num());S.Bytes.Append(G.CanonicalPayload);return S.Bytes;
}
TArray<uint8> LoadedSignature(const Save::FLoadedRun& L)
{
    FSignature S;S.Bytes.Append(GenerationSignature(L.Generation));S.V(L.Run.IsValid(),L.Slot,L.ObservedHeadGeneration);
    if(L.Run.IsValid())S.Bytes.Append(CodecSignature(*L.Run.Get()));return S.Bytes;
}
bool SaveStatus(FAutomationTestBase& T,const TCHAR* Label,SG::EStatus Actual,SG::EStatus Expected)
{return T.TestEqual(Label,int32(Actual),int32(Expected));}
bool ProveSaved(FCodecWorld& World,FDungeonRunSnapshot& Out,FDungeonValidatedRun& Sealed,const TCHAR* Label)
{
    if(!CodecSeal(World,Out,Sealed,Label))return false;TArray<uint8> Actual;FString Why;FDungeonValidatedRun Decoded;
    const auto Expected=FCodecOracle::Bytes(Out);
    if(!World.Test.TestTrue(TEXT("Independent actual Codec/Aggregate positive controls precede SaveAdapter"),
        Codec::Encode(Out,Actual,Why)&&Actual==Expected&&Codec::Decode(Expected,Decoded,Why)&&Decoded.IsValid()
        &&CodecSignature(*Decoded.Get())==CodecSignature(Out)))
    {World.Test.AddInfo(TEXT("Actual Codec positive-control diagnosis: ")+Why);return false;}return true;
}
bool SaveHistory(FCodecWorld& W,FDungeonRunSnapshot& Saved,FDungeonValidatedRun& Sealed)
{
    if(!W.Test.TestTrue(TEXT("Actual bound Run normally kills knight, collects coin and reaches original exit"),W.Create()&&W.KillKnight()&&W.ReachExit()))return false;
    if(!W.Test.TestTrue(TEXT("Actual normal Enter transfers same Run to room2 with already collected five coins"),W.Pulse(EKeys::Enter)&&W.Game->RoomNumber==2&&W.Player->Coins==5&&W.BankAdmitted()))return false;
    auto* Bat=W.Game->SpawnStoneBat({800.,80.});if(!W.Test.TestTrue(TEXT("Actual room2 bat admission creates its supported owner"),Bat&&Bat->GetStoneBatDriver()))return false;
    W.Frame(.01f);if(!ProveSaved(W,Saved,Sealed,TEXT("Actual cross-room rich adapter source")))return false;
    return W.Test.TestTrue(TEXT("Real current bat, retired dead actor, consumed coin receipt and both observed fog banks are present"),Saved.Fighters.Num()==3&&Saved.Fighters[2].Bat.IsSet()
        &&Saved.Rewards.RetiredEntities.Num()==1&&Saved.Rewards.Collections.Num()==1&&Saved.Rewards.Objects[0].Consumed&&Saved.Rewards.Objects[0].Retired&&Saved.Exploration.Rooms.Num()==2);
}
bool SaveReload(FCodecWorld& W,FDungeonRunSnapshot& Saved,FDungeonValidatedRun& Sealed)
{
    if(!W.Test.TestTrue(TEXT("Actual normal Enter source for disk reload continuation"),W.Create()))return false;
    IV::FItem X;X.ContentId="WPN-XBW-001";X.Ammo=0.;
    const auto R=W.Game->RegisterEquipmentSource(TEXT("save.adapter.real.empty-xbw"),X,W.Player->GetGroundPosition()+FVector2D(30.,0.),true);
    if(!W.Test.TestTrue(TEXT("Real E acquires empty crossbow at original deadline, then T starts actual reload"),R.Ok()&&W.Pulse(EKeys::E)
        &&W.Game->GetEquipmentView().Action.Active&&W.AdvanceTo(W.Player->GetEquipmentActionDeadline())&&W.Player->WeaponId==TEXT("WPN-XBW-001")&&W.Pulse(EKeys::T)))return false;
    const auto Reload=W.Player->GetWeaponActionsState().Action;W.Player->GetWeaponMuzzleComponent()->SetRelativeLocation(FVector(24.,7.,65.));
    if(!W.Test.TestTrue(TEXT("Actual original post-insert boundary retains future reload completion"),Reload.Active&&Reload.Type==WA::EAction::Reload&&W.AdvanceTo(Reload.Start+.65)
        &&W.Player->GetWeaponActionsState().Action.Active&&W.HUD->GetActionAudioPlayRequests(TEXT("XBW_RELOAD_DRAW_01"))==1&&W.HUD->GetActionAudioPlayRequests(TEXT("XBW_RELOAD_INSERT_01"))==1))return false;
    return ProveSaved(W,Saved,Sealed,TEXT("Actual mid-reload disk source with native muzzle and audio cursors"));
}
struct FSaveDisk
{
    FAutomationTestBase& Test;FString Root;Save::FReadContext Context;
    explicit FSaveDisk(FAutomationTestBase& T):Test(T)
    {
        Root=FPaths::ConvertRelativePathToFull(FPaths::ProjectSavedDir()/TEXT("Automation/RunSaveAdapter")/FGuid::NewGuid().ToString(EGuidFormats::Digits));
        Context.ProfilesDirectory=Root/Save::DirectoryName;Context.ProfileId=FGuid::NewGuid();
        Test.AddInfo(TEXT("Retained real isolated run-only save IO: ")+Root);
    }
    bool ProveIO()
    {
        const auto Bytes=SaveUtf8(TEXT("actual isolated run-only IO; no invented Account owner\n"));TArray<uint8> Read;
        return Test.TestTrue(TEXT("Create actual isolated run-only namespace"),IFileManager::Get().MakeDirectory(*Context.ProfilesDirectory,true))
            &&Test.TestTrue(TEXT("Write/read actual fixture bytes before adapter semantics"),FFileHelper::SaveArrayToFile(Bytes,*(Root/TEXT("io-proof.txt")))
            &&FFileHelper::LoadFileToArray(Read,*(Root/TEXT("io-proof.txt")))&&Read==Bytes);
    }
    Save::FWriteRequest Request(const FDungeonRunSnapshot& S,uint64 Id=1,uint64 Parent=0)const
    {
        Save::FWriteRequest R;R.Context=Context;R.RunGuid=S.RunGuid;R.OwnerId=S.OwnerId;R.GenerationId=Id;R.ParentGeneration=Parent;
        R.BuildId=TEXT("automation-bound-run-save-v1");return R;
    }
    TArray<uint8> ReadFile(const FString& P)
    {TArray<uint8> Bytes;Test.TestTrue(TEXT("Read retained actual published disk bytes"),FFileHelper::LoadFileToArray(Bytes,*P));return Bytes;}
};
// Independent fixed-shape envelope oracle. All inserted metadata is the
// proven ASCII fixture contract; the Run bytes are the independent full codec
// oracle. It does not call the new production MakeGeneration/Validate methods.
SG::FGeneration ExpectedGeneration(const FDungeonRunSnapshot& S,const Save::FWriteRequest& R)
{
    SG::FGeneration G;G.ProfileId=R.Context.ProfileId;G.GenerationId=R.GenerationId;G.ParentGeneration=R.ParentGeneration;
    G.Versions=Save::CurrentVersions;G.BuildId=R.BuildId;G.RunSimulationTime=S.SimulationTime;
    const auto Profile=G.ProfileId.ToString(EGuidFormats::Digits).ToLower(),Run=S.RunGuid.ToString(EGuidFormats::Digits).ToLower();
    const auto Prefix=FString::Printf(TEXT("{\"adapter\":\"bound-run-only-v1\",\"buildId\":\"%s\",\"generationId\":\"%llu\",\"parentGeneration\":\"%llu\",\"profileId\":\"%s\",\"run\":"),*G.BuildId,G.GenerationId,G.ParentGeneration,*Profile);
    uint64 Bits;FMemory::Memcpy(&Bits,&S.SimulationTime,8);
    const auto Suffix=FString::Printf(TEXT(",\"runGuid\":\"%s\",\"runSimulationTime\":\"%016llx\",\"scope\":\"BoundDevelopmentRunV1\",\"versions\":{\"contentRules\":\"%s\",\"coordinates\":\"%s\",\"schema\":\"%s\"}}"),*Run,Bits,*G.Versions.ContentRules,*G.Versions.Coordinates,*G.Versions.Schema);
    G.CanonicalPayload=SaveUtf8(Prefix);G.CanonicalPayload.Append(FCodecOracle::Bytes(S));G.CanonicalPayload.Append(SaveUtf8(Suffix));return G;
}
bool SeedIndependent(FSaveDisk& F,SG::FGenerationStore& Disk,const SG::FGeneration& Expected,const FDungeonRunSnapshot& Saved)
{
    const auto HeaderAndBytes=GenerationSignature(Expected),RunBytes=FCodecOracle::Bytes(Saved),ExactRun=CodecSignature(Saved);
    const SG::FPayloadValidator FixtureValidator=[&](const SG::FGeneration& G,FString& Why)
    {
        FDungeonValidatedRun V;
        if(GenerationSignature(G)!=HeaderAndBytes||!G.RunSimulationTime.IsSet()||G.RunSimulationTime.GetValue()!=Saved.SimulationTime
            ||!Codec::Decode(RunBytes,V,Why)||!V.IsValid()||CodecSignature(*V.Get())!=ExactRun)
        {Why=TEXT("Independent complete source/header/byte fixture does not match");return false;}return true;
    };
    if(!SaveStatus(F.Test,TEXT("Real run-only fixture writer opens"),Disk.OpenWriter(),SG::EStatus::Ok))return false;
    const auto C=Disk.Commit(Expected,FixtureValidator);
    if(!SaveStatus(F.Test,TEXT("Independent legal actual Run envelope really publishes through existing Store"),C.Status,SG::EStatus::Ok))return false;
    const auto L=Disk.Load(FixtureValidator);
    return F.Test.TestTrue(TEXT("Actual freshly read fixture is byte/header exact before new adapter is tested"),L.Status==SG::EStatus::Ok&&GenerationSignature(L.Generation)==HeaderAndBytes);
}
Save::FLoadedRun ExistingLoaded(const SG::FGeneration& G,const FDungeonValidatedRun& V)
{Save::FLoadedRun L;L.Generation=G;L.Run=V;L.ObservedHeadGeneration=G.GenerationId;return L;}
bool ResumeDiskTarget(FCodecWorld& W)
{W.Frame(.005f);return W.Pulse(EKeys::Enter)&&W.Game->GetRunInstallGate()==EDungeonRunInstallGate::Open;}
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRunSaveGeneration,
    "CodexDungeon.Content.RunSaveAdapter.TypedCandidateHeaderBindingsAndAtomicValidation",
    EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FRunSaveGeneration::RunTest(const FString&)
{
    FCodecWorld W(*this);FDungeonRunSnapshot Saved;FDungeonValidatedRun Valid;if(!SaveReload(W,Saved,Valid))return false;
    FSaveDisk F(*this);if(!F.ProveIO())return false;const auto Request=F.Request(Saved);const auto Expected=ExpectedGeneration(Saved,Request);
    const auto Original=CodecSignature(Saved);SG::FGeneration Out;Out.GenerationId=99;Out.CanonicalPayload={0xee,0,0x42};FString Why;
    const bool Made=Save::MakeGeneration(Saved,Request,Out,Why);
    TestTrue(TEXT("Implemented adapter creates exact complete run-only typed/header generation"),Made);
    if(Made)TestTrue(TEXT("Actual candidate is byte/header exact against independent envelope and full Codec oracle"),GenerationSignature(Out)==GenerationSignature(Expected)&&Why.IsEmpty());
    FDungeonValidatedRun Sealed=Valid;const auto* Pointer=Sealed.Get();const bool Accepted=Save::ValidateGeneration(Expected,F.Context,Sealed,Why);
    TestTrue(TEXT("Mandatory adapter validator accepts independently legal whole header/envelope/Run"),Accepted&&Sealed.IsValid());
    if(Accepted)TestTrue(TEXT("Sealed decoded Run retains every original value"),CodecSignature(*Sealed.Get())==Original);
    Sealed=Valid;
    auto IdentityContext=F.Context;IdentityContext.ExpectedRunGuid=Saved.RunGuid;IdentityContext.ExpectedOwnerId=Saved.OwnerId;
    FDungeonValidatedRun IdentityOut;
    TestTrue(TEXT("Matching caller Run and owner expectations bind the whole decoded Run"),Save::ValidateGeneration(Expected,IdentityContext,IdentityOut,Why)
        &&IdentityOut.IsValid()&&CodecSignature(*IdentityOut.Get())==Original);
    IdentityContext.ExpectedRunGuid=FGuid::NewGuid();
    TestFalse(TEXT("Caller Run mismatch cannot accept otherwise valid saved Run"),Save::ValidateGeneration(Expected,IdentityContext,Sealed,Why));
    IdentityContext.ExpectedRunGuid=Saved.RunGuid;++IdentityContext.ExpectedOwnerId;
    TestFalse(TEXT("Caller owner mismatch cannot accept otherwise valid saved Run"),Save::ValidateGeneration(Expected,IdentityContext,Sealed,Why));
    TestTrue(TEXT("Caller identity failures preserve original sealed pointer and every value"),Sealed.Get()==Pointer&&CodecSignature(*Sealed.Get())==Original);
    const auto Reject=[&](const TCHAR* Label,auto Change)
    {
        auto Bad=Expected;Change(Bad);FString Invalid;
        TestFalse(*(FString(Label)+TEXT(" rejects whole generation")),Save::ValidateGeneration(Bad,F.Context,Sealed,Invalid));
        TestTrue(*(FString(Label)+TEXT(" preserves sealed pointer, complete values and live source")),!Invalid.IsEmpty()&&Sealed.Get()==Pointer&&CodecSignature(*Sealed.Get())==Original&&CodecSignature(Saved)==Original);
    };
    Reject(TEXT("Wrong enclosing Profile"),[](auto& G){G.ProfileId=FGuid::NewGuid();});
    Reject(TEXT("Changed generation identity"),[](auto& G){++G.GenerationId;});
    Reject(TEXT("Changed parent identity"),[](auto& G){++G.ParentGeneration;});
    Reject(TEXT("Missing header clock"),[](auto& G){G.RunSimulationTime.Reset();});
    Reject(TEXT("Mismatched header/root clock"),[](auto& G){G.RunSimulationTime=G.RunSimulationTime.GetValue()+1.;});
    Reject(TEXT("Wrong content rules version"),[](auto& G){G.Versions.ContentRules=TEXT("bound-development-v99");});
    Reject(TEXT("Wrong coordinate version case"),[](auto& G){G.Versions.Coordinates=TEXT("WORLD-CM-V1");});
    Reject(TEXT("Changed Build metadata"),[](auto& G){G.BuildId=TEXT("different-build");});
    Reject(TEXT("Unknown wrapper field"),[](auto& G){G.CanonicalPayload.Insert(SaveUtf8(TEXT("\"future\":true,")),1);});
    Reject(TEXT("Duplicate escaped wrapper field"),[](auto& G){G.CanonicalPayload.Insert(SaveUtf8(TEXT("\"\\u0061dapter\":\"bound-run-only-v1\",")),1);});
    auto InvalidRun=Saved;++InvalidRun.OwnerId;FDungeonValidatedRun InvalidSeal;FString AggregateWhy;
    if(!TestFalse(TEXT("Independent real Aggregate rejects otherwise complete Run with inconsistent owner references"),
        FDungeonRunAggregate::Validate(InvalidRun,InvalidSeal,AggregateWhy)))return false;
    const auto SemanticBad=ExpectedGeneration(InvalidRun,F.Request(InvalidRun));
    TestFalse(TEXT("Syntactically complete envelope cannot bypass nested Run semantic validation"),Save::ValidateGeneration(SemanticBad,F.Context,Sealed,Why));
    TestTrue(TEXT("Nested semantic failure preserves prior sealed native Run pointer and values"),Sealed.Get()==Pointer&&CodecSignature(*Sealed.Get())==Original);
    const auto RejectRequest=[&](const TCHAR* Label,auto Change)
    {
        auto Bad=Request;Change(Bad);SG::FGeneration Untouched=Expected;const auto Before=GenerationSignature(Untouched);const auto* PayloadPointer=Untouched.CanonicalPayload.GetData();FString Invalid;
        TestFalse(Label,Save::MakeGeneration(Saved,Bad,Untouched,Invalid));TestTrue(TEXT("Failed typed candidate leaves complete prior output, byte allocation and real source untouched"),!Invalid.IsEmpty()&&GenerationSignature(Untouched)==Before&&Untouched.CanonicalPayload.GetData()==PayloadPointer&&CodecSignature(Saved)==Original);
    };
    RejectRequest(TEXT("Complete Profile scope cannot be invented as empty owners"),[](auto& R){R.Context.Scope=Save::EScope::CompleteProfileV1;});
    RejectRequest(TEXT("Foreign namespace cannot receive run-only writes"),[](auto& R){R.Context.ProfilesDirectory=FPaths::GetPath(R.Context.ProfilesDirectory)/TEXT("FullProfiles");});
    RejectRequest(TEXT("Wrong request Run identity"),[](auto& R){R.RunGuid=FGuid::NewGuid();});
    RejectRequest(TEXT("Wrong request owner"),[](auto& R){++R.OwnerId;});
    RejectRequest(TEXT("Unknown write parent"),[](auto& R){R.ParentGeneration=R.GenerationId;});
    FDungeonRunSnapshot After;FDungeonValidatedRun AV;if(!ProveSaved(W,After,AV,TEXT("Live source after pure save validation")))return false;
    TestTrue(TEXT("Pure save metadata work never advances or changes actual GameMode state"),CodecSignature(After)==Original);
    return Made&&Accepted;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRunSaveCommit,
    "CodexDungeon.Content.RunSaveAdapter.CommitFaultPublicationAndFreshDisk",
    EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FRunSaveCommit::RunTest(const FString&)
{
    FCodecWorld Source(*this);FDungeonRunSnapshot First;FDungeonValidatedRun FV;
    if(!SaveHistory(Source,First,FV))return false;
    FSaveDisk F(*this);if(!F.ProveIO())return false;
    SG::FGenerationStore Disk(F.Context.ProfilesDirectory,F.Context.ProfileId,Save::CurrentVersions);
    const auto FirstGeneration=ExpectedGeneration(First,F.Request(First));
    if(!SeedIndependent(F,Disk,FirstGeneration,First))return false;
    const auto ProfileDirectory=Disk.GetProfileDirectory();
    const auto BundleA=F.ReadFile(ProfileDirectory/TEXT("slot-A.bundle.json"));
    const auto MarkerA=F.ReadFile(ProfileDirectory/TEXT("slot-A.commit.json"));
    Source.Frame(.02f);FDungeonRunSnapshot Second;FDungeonValidatedRun SV;
    if(!ProveSaved(Source,Second,SV,TEXT("Actual next complete Run boundary for generation2")))return false;
    const auto Request2=F.Request(Second,2,1);const auto Expected2=ExpectedGeneration(Second,Request2);
    const auto Interrupted=Save::Commit(Disk,Second,Request2,SG::EFaultPoint::BundleWrittenBeforeFlush);
    SaveStatus(*this,TEXT("Actual pre-flush injection is reported by adapter/Store commit"),Interrupted.Status,SG::EStatus::InjectedFailure);
    TestTrue(TEXT("Before publication, real old published bundle and marker stay exact, no new marker exists"),
        !Interrupted.PublicationMayHaveSucceeded&&F.ReadFile(ProfileDirectory/TEXT("slot-A.bundle.json"))==BundleA
        &&F.ReadFile(ProfileDirectory/TEXT("slot-A.commit.json"))==MarkerA
        &&!IFileManager::Get().FileExists(*(ProfileDirectory/TEXT("slot-B.commit.json"))));
    const auto Committed=Save::Commit(Disk,Second,Request2);
    if(!SaveStatus(*this,TEXT("Same real candidate and same identity retry publishes generation2"),Committed.Status,SG::EStatus::Ok))return false;
    SG::FGenerationStore Fresh(F.Context.ProfilesDirectory,F.Context.ProfileId,Save::CurrentVersions);
    Save::FLoadedRun Loaded;const auto Read2=Save::Load(Fresh,F.Context,Loaded);
    if(!SaveStatus(*this,TEXT("Fresh Store object loads actual generation2 through mandatory adapter validator"),Read2.Status,SG::EStatus::Ok))return false;
    TestTrue(TEXT("Fresh disk read preserves exact envelope/header and every sealed native Run value"),
        Read2.ObservedHeadGeneration==2&&Read2.Slot==SG::ESlot::B&&Loaded.ObservedHeadGeneration==2&&Loaded.Slot==SG::ESlot::B
        &&GenerationSignature(Loaded.Generation)==GenerationSignature(Expected2)&&Loaded.Run.IsValid()
        &&CodecSignature(*Loaded.Run.Get())==CodecSignature(Second));
    Source.Frame(.03f);FDungeonRunSnapshot Third;FDungeonValidatedRun TV;
    if(!ProveSaved(Source,Third,TV,TEXT("Actual next complete Run boundary for lost acknowledgement")))return false;
    const auto Request3=F.Request(Third,3,2);const auto Expected3=ExpectedGeneration(Third,Request3);
    const auto LostAck=Save::Commit(Disk,Third,Request3,SG::EFaultPoint::AfterMarkerPublish);
    SaveStatus(*this,TEXT("Lost published acknowledgement is explicit injection, not assumed rollback"),LostAck.Status,SG::EStatus::InjectedFailure);
    TestTrue(TEXT("Published acknowledgement loss explicitly signals ambiguous commit"),LostAck.PublicationMayHaveSucceeded);
    SG::FGenerationStore AfterLoss(F.Context.ProfilesDirectory,F.Context.ProfileId,Save::CurrentVersions);
    const auto Read3=Save::Load(AfterLoss,F.Context,Loaded);
    TestTrue(TEXT("Actual marker resolves lost acknowledgement to whole new generation3"),Read3.Status==SG::EStatus::Ok
        &&Read3.ObservedHeadGeneration==3&&Read3.Slot==SG::ESlot::A&&GenerationSignature(Loaded.Generation)==GenerationSignature(Expected3)
        &&Loaded.Run.IsValid()&&CodecSignature(*Loaded.Run.Get())==CodecSignature(Third));
    const auto Retry3=Save::Commit(Disk,Third,Request3);
    TestTrue(TEXT("Retry of identical published generation is a replay, never a new logical generation"),Retry3.Status==SG::EStatus::Ok&&Retry3.Replayed&&Retry3.GenerationId==3);
    FDungeonRunSnapshot After;FDungeonValidatedRun AV;if(!ProveSaved(Source,After,AV,TEXT("Actual live source after IO/fault/retry")))return false;
    TestTrue(TEXT("Saving and lost-ack resolution never alter any authoritative Run value"),CodecSignature(After)==CodecSignature(Third));
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRunSaveBadHead,
    "CodexDungeon.Content.RunSaveAdapter.NewestSemanticHeadNamespaceAndPreparedOutputsAtomic",
    EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FRunSaveBadHead::RunTest(const FString&)
{
    FCodecWorld Source(*this);FDungeonRunSnapshot Saved;FDungeonValidatedRun Valid;
    if(!SaveHistory(Source,Saved,Valid))return false;
    FSaveDisk F(*this);if(!F.ProveIO())return false;
    SG::FGenerationStore Disk(F.Context.ProfilesDirectory,F.Context.ProfileId,Save::CurrentVersions);
    const auto Good=ExpectedGeneration(Saved,F.Request(Saved));
    if(!SeedIndependent(F,Disk,Good,Saved))return false;
    auto Bad=ExpectedGeneration(Saved,F.Request(Saved,2,1));Bad.RunSimulationTime=Saved.SimulationTime+1.;
    if(!TestTrue(TEXT("Bad-head premise changes header clock only; legal full Run oracle remains independently proven"),
        Bad.RunSimulationTime.IsSet()&&Bad.RunSimulationTime.GetValue()!=Saved.SimulationTime))return false;
    const SG::FPayloadValidator DeliberatelyPermissiveFixtureWriter=[](const SG::FGeneration&,FString&){return true;};
    if(!SaveStatus(*this,TEXT("Fixture publishes actual structurally/checksum-correct but semantically mismatched newest head"),
        Disk.Commit(Bad,DeliberatelyPermissiveFixtureWriter).Status,SG::EStatus::Ok))return false;
    const SG::FPayloadValidator IndependentClockCheck=[&](const SG::FGeneration& G,FString& Why)
    {if(!G.RunSimulationTime.IsSet()||G.RunSimulationTime.GetValue()!=Saved.SimulationTime){Why=TEXT("Actual header/root clock mismatch");return false;}return true;};
    const auto ProvenBadHead=Disk.Load(IndependentClockCheck);
    if(!TestTrue(TEXT("Existing Store independently proves newest semantic head requires recovery and never falls back to legal A1"),
        ProvenBadHead.Status==SG::EStatus::RecoveryRequired&&ProvenBadHead.ObservedHeadGeneration==2&&ProvenBadHead.Generation.CanonicalPayload.IsEmpty()))return false;
    const auto ProfileDirectory=Disk.GetProfileDirectory();
    const TArray<FString> PublishedPaths={ProfileDirectory/TEXT("slot-A.bundle.json"),ProfileDirectory/TEXT("slot-A.commit.json"),
        ProfileDirectory/TEXT("slot-B.bundle.json"),ProfileDirectory/TEXT("slot-B.commit.json")};
    TArray<TArray<uint8>> PublishedBytes;for(const auto& Path:PublishedPaths)PublishedBytes.Add(F.ReadFile(Path));
    Disk.CloseWriter();SG::FGenerationStore Fresh(F.Context.ProfilesDirectory,F.Context.ProfileId,Save::CurrentVersions);
    auto Loaded=ExistingLoaded(Good,Valid);const auto LoadedBefore=LoadedSignature(Loaded);const auto* LoadedPointer=Loaded.Run.Get();const auto* LoadedBytesPointer=Loaded.Generation.CanonicalPayload.GetData();
    const auto Read=Save::Load(Fresh,F.Context,Loaded);
    SaveStatus(*this,TEXT("Adapter refuses actual newest semantically bad head"),Read.Status,SG::EStatus::RecoveryRequired);
    TestTrue(TEXT("Failed read reports newest head and leaves complete prior loaded output pointer and values untouched"),
        Read.ObservedHeadGeneration==2&&!Read.Diagnostic.IsEmpty()&&Loaded.Run.Get()==LoadedPointer&&Loaded.Generation.CanonicalPayload.GetData()==LoadedBytesPointer&&LoadedSignature(Loaded)==LoadedBefore);

    FCodecWorld Target(*this);FDungeonRunSnapshot TargetSaved;FDungeonValidatedRun TargetValid;
    if(!Target.Create()||!ProveSaved(Target,TargetSaved,TargetValid,TEXT("Existing legal target for failed disk preparation")))return false;
    FDungeonPreparedRun PreviousPrepared;FString Why;
    if(!TestTrue(TEXT("Independent existing Installer really prepares nonempty separate source resources before failure test"),
        FDungeonRunInstaller::Prepare(*Source.Game,Valid,PreviousPrepared,Why)&&PreviousPrepared.IsReady()))return false;
    const auto* PreparedPointer=PreviousPrepared.GetSavedSnapshot();const auto StagedBefore=PreviousPrepared.GetStagedActors();
    const auto* TargetPlayer=Target.Player;
    const auto Preparation=Save::LoadAndPrepare(*Target.Game,Fresh,F.Context,PreviousPrepared,Loaded);
    SaveStatus(*this,TEXT("Load/preparation refuses corrupt newest head before touching legal target"),Preparation.Status,SG::EStatus::RecoveryRequired);
    TestTrue(TEXT("Failure keeps preexisting prepared group, its staged actor identities, loaded pointer and both live gates intact"),
        PreviousPrepared.IsReady()&&PreviousPrepared.GetSavedSnapshot()==PreparedPointer&&PreviousPrepared.GetStagedActors()==StagedBefore
        &&Loaded.Run.Get()==LoadedPointer&&Loaded.Generation.CanonicalPayload.GetData()==LoadedBytesPointer&&LoadedSignature(Loaded)==LoadedBefore
        &&Source.Game->GetRunInstallGate()==EDungeonRunInstallGate::Preparing
        &&Target.Game->GetRunInstallGate()==EDungeonRunInstallGate::Open&&Target.Game->PlayerFighter==TargetPlayer);
    FDungeonRunSnapshot TargetAfter;FDungeonValidatedRun TargetAfterValid;
    if(!ProveSaved(Target,TargetAfter,TargetAfterValid,TEXT("Actual target after refused semantic head")))return false;
    TestTrue(TEXT("Refused disk preparation changes no complete target Run value"),CodecSignature(TargetAfter)==CodecSignature(TargetSaved));

    const auto ForeignRoot=F.Root/TEXT("FullProfiles");
    SG::FGenerationStore Foreign(ForeignRoot,F.Context.ProfileId,Save::CurrentVersions);
    if(!SaveStatus(*this,TEXT("Independent foreign namespace writer lease opens for refusal test"),Foreign.OpenWriter(),SG::EStatus::Ok))return false;
    const auto SentinelPath=Foreign.GetProfileDirectory()/TEXT("unrelated-owner.sentinel");
    const auto Sentinel=SaveUtf8(TEXT("Unrelated namespace data. This is not a fabricated complete Profile owner."));
    if(!TestTrue(TEXT("Unrelated actual foreign namespace bytes are retained before adapter call"),FFileHelper::SaveArrayToFile(Sentinel,*SentinelPath)))return false;
    const auto ForeignCommit=Save::Commit(Foreign,Saved,F.Request(Saved));
    SaveStatus(*this,TEXT("Run-only adapter refuses Store/context path mismatch without touching foreign namespace"),ForeignCommit.Status,SG::EStatus::InvalidRequest);
    TestTrue(TEXT("Foreign owner bytes remain exact and no run-only slot marker is published outside isolated namespace"),F.ReadFile(SentinelPath)==Sentinel
        &&!IFileManager::Get().FileExists(*(Foreign.GetProfileDirectory()/TEXT("slot-A.commit.json")))
        &&!IFileManager::Get().FileExists(*(Foreign.GetProfileDirectory()/TEXT("slot-B.commit.json"))));
    auto Unsupported=F.Context;Unsupported.Scope=Save::EScope::CompleteProfileV1;
    SaveStatus(*this,TEXT("Missing real Account/settings/journal owners cannot be advertised as complete Profile support"),
        Save::Load(Fresh,Unsupported,Loaded).Status,SG::EStatus::InvalidRequest);
    TestTrue(TEXT("Unsupported scope preserves complete prior loaded result"),Loaded.Run.Get()==LoadedPointer&&LoadedSignature(Loaded)==LoadedBefore);
    for(int32 Index=0;Index<PublishedPaths.Num();++Index)
        TestTrue(TEXT("All published disk bytes remain unchanged after failed loads/preparation/scope checks"),F.ReadFile(PublishedPaths[Index])==PublishedBytes[Index]);
    FDungeonRunSnapshot SourceAfter;FDungeonValidatedRun SourceAfterValid;
    if(!ProveSaved(Source,SourceAfter,SourceAfterValid,TEXT("Actual prepared source after all failed adapter calls")))return false;
    TestTrue(TEXT("All source authoritative values remain intact while original prepared resources are retained"),CodecSignature(SourceAfter)==CodecSignature(Saved));
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRunSaveReload,
    "CodexDungeon.Content.RunSaveAdapter.FreshDiskPrepareInstallAndOriginalReloadContinuation",
    EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FRunSaveReload::RunTest(const FString&)
{
    FCodecWorld Source(*this);FDungeonRunSnapshot Saved;FDungeonValidatedRun Valid;
    if(!SaveReload(Source,Saved,Valid))return false;
    const auto Reload=Source.Player->GetWeaponActionsState().Action;
    const auto Updates=Saved.Equipment.InventoryState.RuntimeUpdates.size();const auto Draw=Saved.Equipment.View.NextCritDraw;
    const auto OriginalInstance=Reload.InstanceId;
    FSaveDisk F(*this);if(!F.ProveIO())return false;
    SG::FGenerationStore Writer(F.Context.ProfilesDirectory,F.Context.ProfileId,Save::CurrentVersions);
    const auto Expected=ExpectedGeneration(Saved,F.Request(Saved));if(!SeedIndependent(F,Writer,Expected,Saved))return false;
    Writer.CloseWriter();SG::FGenerationStore Fresh(F.Context.ProfilesDirectory,F.Context.ProfileId,Save::CurrentVersions);
    FCodecWorld Target(*this);FDungeonRunSnapshot Before;FDungeonValidatedRun BeforeValid;
    if(!Target.Create()||!ProveSaved(Target,Before,BeforeValid,TEXT("Existing legal target before disk continuation")))return false;
    auto Loaded=ExistingLoaded(ExpectedGeneration(Before,F.Request(Before,99,98)),BeforeValid);
    const auto PriorLoaded=LoadedSignature(Loaded);const auto* PriorPointer=Loaded.Run.Get();const auto* OldPlayer=Target.Player;
    {
        FDungeonPreparedRun Blocking;FString Why;
        if(!TestTrue(TEXT("Existing Installer positive control closes target with a real nonempty prepared group"),
            FDungeonRunInstaller::Prepare(*Target.Game,BeforeValid,Blocking,Why)&&Blocking.IsReady()))return false;
        const auto* SavedPointer=Blocking.GetSavedSnapshot();const auto Actors=Blocking.GetStagedActors();
        const auto Refused=Save::LoadAndPrepare(*Target.Game,Fresh,F.Context,Blocking,Loaded);
        SaveStatus(*this,TEXT("Valid disk load followed by target gate rejection remains a failed atomic preparation"),Refused.Status,SG::EStatus::ValidatorRejected);
        TestTrue(TEXT("A later Prepare failure publishes neither decoded output nor partial staged replacement"),
            Blocking.IsReady()&&Blocking.GetSavedSnapshot()==SavedPointer&&Blocking.GetStagedActors()==Actors
            &&Loaded.Run.Get()==PriorPointer&&LoadedSignature(Loaded)==PriorLoaded&&Target.Game->PlayerFighter==OldPlayer
            &&Target.Game->GetRunInstallGate()==EDungeonRunInstallGate::Preparing);
    }
    if(!TestTrue(TEXT("Independent staged RAII release restores original valid target gate"),Target.Game->GetRunInstallGate()==EDungeonRunInstallGate::Open))return false;
    FDungeonPreparedRun Prepared;const auto Read=Save::LoadAndPrepare(*Target.Game,Fresh,F.Context,Prepared,Loaded);
    if(!SaveStatus(*this,TEXT("Fresh Store instance decodes and prepares actual saved Run through original Installer"),Read.Status,SG::EStatus::Ok))
    {
        FDungeonRunSnapshot AfterFailure;FDungeonValidatedRun AfterFailureValid;
        if(ProveSaved(Target,AfterFailure,AfterFailureValid,TEXT("Actual target after unimplemented/failed disk continuation")))
            TestTrue(TEXT("Failed initial preparation leaves complete live Run, old loaded output and empty Prepared unchanged"),
                CodecSignature(AfterFailure)==CodecSignature(Before)&&!Prepared.IsReady()&&Loaded.Run.Get()==PriorPointer
                &&LoadedSignature(Loaded)==PriorLoaded&&Target.Game->PlayerFighter==OldPlayer&&Target.Game->GetRunInstallGate()==EDungeonRunInstallGate::Open);
        return false;
    }
    TestTrue(TEXT("Read output and staged resources bind exact generation/header/clock/whole sealed Run"),
        Read.ObservedHeadGeneration==1&&Read.Slot==SG::ESlot::A&&Loaded.ObservedHeadGeneration==1&&Loaded.Slot==SG::ESlot::A
        &&GenerationSignature(Loaded.Generation)==GenerationSignature(Expected)&&Loaded.Run.IsValid()
        &&CodecSignature(*Loaded.Run.Get())==CodecSignature(Saved)&&Prepared.IsReady()&&Prepared.GetSavedSnapshot()
        &&CodecSignature(*Prepared.GetSavedSnapshot())==CodecSignature(Saved)&&Target.Game->GetRunInstallGate()==EDungeonRunInstallGate::Preparing);
    FString Why;
    if(!TestTrue(TEXT("Existing Installer really installs the loaded independent actor/owner group"),FDungeonRunInstaller::Install(*Target.Game,Prepared,Why)&&!Prepared.IsReady()))return false;
    Target.Player=Target.Game->PlayerFighter;
    TestTrue(TEXT("Actual restored player is newly possessed while run stays paused awaiting explicit Continue"),Target.Player&&Target.Player!=OldPlayer
        &&Target.Controller->GetPawn()==Target.Player&&Target.Game->GetRunInstallGate()==EDungeonRunInstallGate::AwaitExplicitContinue);
    FDungeonRunSnapshot Installed;FDungeonValidatedRun InstalledValid;
    if(!ProveSaved(Target,Installed,InstalledValid,TEXT("Actual paused disk-installed complete native Run")))return false;
    TestTrue(TEXT("Every installed typed field exactly equals original saved source including native muzzle and spent audio cursors"),CodecSignature(Installed)==CodecSignature(Saved));
    TestTrue(TEXT("Paused attachment replays no elapsed reload audio"),Target.HUD->GetActionAudioPlayReceipts().IsEmpty()&&Target.Game->GetActionAudioState().Records.IsEmpty());
    if(!TestTrue(TEXT("Real neutral and fresh Enter resume actual installed Run"),ResumeDiskTarget(Target)))return false;
    if(!TestTrue(TEXT("Source and restored target both reach original absolute reload deadline"),Source.AdvanceTo(Reload.End)&&Target.AdvanceTo(Reload.End)))return false;
    const auto& Action=Target.Player->GetWeaponActionsState();const auto* Inventory=Target.Game->GetEquipmentInventoryState();
    const auto* SourceInventory=Source.Game->GetEquipmentInventoryState();
    TestTrue(TEXT("Original action and instance commit exactly one real refill at original deadline without new action/crit draw"),
        Action.Action.ActionId==Reload.ActionId&&!Action.Action.Active&&Inventory&&Inventory->RuntimeUpdates.size()==Updates+1
        &&Inventory->RuntimeUpdates.back().InstanceId==OriginalInstance&&Inventory->RuntimeUpdates.back().BeforeAmmo==0.
        &&Inventory->RuntimeUpdates.back().Ammo==1.&&Inventory->RuntimeUpdates.back().AtTime==Reload.End
        &&Target.Game->GetEquipmentView().NextCritDraw==Draw&&Target.Game->GetEquipmentView().RunGuid==Saved.RunGuid
        &&SourceInventory&&SourceInventory->RuntimeUpdates.size()==Inventory->RuntimeUpdates.size()
        &&SourceInventory->RuntimeUpdates.back().InstanceId==OriginalInstance&&SourceInventory->RuntimeUpdates.back().Ammo==Inventory->RuntimeUpdates.back().Ammo
        &&Source.Player->GetWeaponActionsState().Action.ActionId==Action.Action.ActionId&&!Source.Player->GetWeaponActionsState().Action.Active);
    TestTrue(TEXT("Restored consumer requests future completion once without replaying elapsed draw or insert"),
        Target.HUD->GetActionAudioPlayRequests(TEXT("XBW_RELOAD_COMPLETE_01"))==1&&Target.HUD->GetActionAudioPlayRequests(TEXT("XBW_RELOAD_DRAW_01"))==0
        &&Target.HUD->GetActionAudioPlayRequests(TEXT("XBW_RELOAD_INSERT_01"))==0);
    Target.Frame(.2f);TestTrue(TEXT("Later ordinary ticks cannot duplicate committed refill or completion audio"),
        Target.Game->GetEquipmentInventoryState()->RuntimeUpdates.size()==Updates+1&&Target.HUD->GetActionAudioPlayRequests(TEXT("XBW_RELOAD_COMPLETE_01"))==1);
    AddInfo(TEXT("Fresh Store and separate existing legal target are proven here; pristine process/bootstrap/menu Continue remains separate required work."));
    return true;
}
#endif
