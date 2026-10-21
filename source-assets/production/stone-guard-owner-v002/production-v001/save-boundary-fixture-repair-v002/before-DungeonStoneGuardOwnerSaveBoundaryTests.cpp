#if WITH_DEV_AUTOMATION_TESTS
#include "Misc/AutomationTest.h"
#include "StoneGuardOwnerFixture_v002.h"
#include "../DungeonRunSaveAdapter.h"
#include "HAL/FileManager.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"
namespace
{
namespace BoundarySave=DungeonRunSaveAdapter;
namespace BoundaryStore=DungeonSaveGenerationStore;
TArray<uint8> BoundaryGenerationSignature(const BoundaryStore::FGeneration& G)
{
 FSignature S;S.V(G.ProfileId.A,G.ProfileId.B,G.ProfileId.C,G.ProfileId.D,G.GenerationId,G.ParentGeneration,G.RestoredFromGeneration);
 S.String(G.Versions.Schema);S.String(G.Versions.ContentRules);S.String(G.Versions.Coordinates);S.String(G.BuildId);S.V(G.RunSimulationTime.IsSet());
 if(G.RunSimulationTime.IsSet())S.V(G.RunSimulationTime.GetValue());S.V(G.CanonicalPayload.Num());S.Bytes.Append(G.CanonicalPayload);return S.Bytes;
}
TArray<uint8> BoundaryUtf8(const FString& S){FTCHARToUTF8 U(*S,S.Len());TArray<uint8> B;B.Append(reinterpret_cast<const uint8*>(U.Get()),U.Length());return B;}
TMap<FString,TArray<uint8>> BoundaryDiskBytes(FAutomationTestBase& T,const FString& Directory)
{
 TMap<FString,TArray<uint8>> Result;TArray<FString> Paths;IFileManager::Get().FindFilesRecursive(Paths,*Directory,TEXT("*"),true,false,false);
 for(const auto& P:Paths){TArray<uint8> B;T.TestTrue(TEXT("Actually read every retained published profile file"),FFileHelper::LoadFileToArray(B,*P));Result.Add(P,MoveTemp(B));}return Result;
}
bool BoundarySameDisk(const TMap<FString,TArray<uint8>>& A,const TMap<FString,TArray<uint8>>& B)
{if(A.Num()!=B.Num())return false;for(const auto& E:A){const auto* V=B.Find(E.Key);if(!V||*V!=E.Value)return false;}return true;}
// Deliberately malicious V1 metadata around a separately legal actual V2 Run.
// This is a negative input, never a fabricated supported positive generation.
BoundaryStore::FGeneration BoundaryMislabel(const FDungeonRunSnapshot& S,const BoundarySave::FWriteRequest& R)
{
 BoundaryStore::FGeneration G;G.ProfileId=R.Context.ProfileId;G.GenerationId=R.GenerationId;G.ParentGeneration=R.ParentGeneration;
 G.Versions=BoundarySave::CurrentVersions;G.BuildId=R.BuildId;G.RunSimulationTime=S.SimulationTime;
 const auto Profile=G.ProfileId.ToString(EGuidFormats::Digits).ToLower(),Run=S.RunGuid.ToString(EGuidFormats::Digits).ToLower();uint64 Bits=0;FMemory::Memcpy(&Bits,&S.SimulationTime,8);
 const auto Prefix=FString::Printf(TEXT("{\"adapter\":\"bound-run-only-v1\",\"buildId\":\"%s\",\"generationId\":\"%llu\",\"parentGeneration\":\"%llu\",\"profileId\":\"%s\",\"run\":"),*G.BuildId,G.GenerationId,G.ParentGeneration,*Profile);
 const auto Suffix=FString::Printf(TEXT(",\"runGuid\":\"%s\",\"runSimulationTime\":\"%016llx\",\"scope\":\"BoundDevelopmentRunV1\",\"versions\":{\"contentRules\":\"%s\",\"coordinates\":\"%s\",\"schema\":\"%s\"}}"),*Run,Bits,*G.Versions.ContentRules,*G.Versions.Coordinates,*G.Versions.Schema);
 G.CanonicalPayload=BoundaryUtf8(Prefix);G.CanonicalPayload.Append(FCodecOracle::Bytes(GuardOwnerTests::FGuardWire::DocumentV2(S)));G.CanonicalPayload.Append(BoundaryUtf8(Suffix));return G;
}
}
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDungeonStoneGuardOwnerSaveBoundary,
 "CodexDungeon.Content.StoneGuardOwner.V1DiskBoundaryRejectsRealV2Atomically",
 EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FDungeonStoneGuardOwnerSaveBoundary::RunTest(const FString& Parameters)
{
 (void)Parameters;using namespace GuardOwnerTests;FGuardWorld W(*this);if(!TestTrue(TEXT("Real Scene/normalEnter before version boundary"),W.Create()))return false;
 FDungeonRunSnapshot Legacy;FDungeonValidatedRun LegacySealed;if(!CodecSeal(W,Legacy,LegacySealed,TEXT("Real V1 root seals before guarded source exists")))return false;
 TArray<uint8> LegacyBytes;FString Why;if(!TestTrue(TEXT("Immutable V1 fullCodec independent byteoracle remains legal"),DungeonRunSnapshotCodec::Encode(Legacy,LegacyBytes,Why)&&LegacyBytes==FCodecOracle::Bytes(Legacy)))return false;
 const FString Retained=FPaths::ConvertRelativePathToFull(FPaths::ProjectSavedDir()/TEXT("Automation/StoneGuardV1Boundary")/FGuid::NewGuid().ToString(EGuidFormats::Digits));
 BoundarySave::FReadContext C;C.ProfilesDirectory=Retained/BoundarySave::DirectoryName;C.ProfileId=FGuid::NewGuid();AddInfo(TEXT("Retained real V1 boundary disk IO: ")+Retained);
 if(!TestTrue(TEXT("Create actual isolated namedV1 namespace"),IFileManager::Get().MakeDirectory(*C.ProfilesDirectory,true)))return false;
 BoundarySave::FWriteRequest Request;Request.Context=C;Request.RunGuid=Legacy.RunGuid;Request.OwnerId=Legacy.OwnerId;Request.GenerationId=1;Request.BuildId=TEXT("actual-guard-v1-version-boundary");
 BoundaryStore::FGenerationStore Disk(C.ProfilesDirectory,C.ProfileId,BoundarySave::CurrentVersions);
 if(!TestEqual(TEXT("Actual existing V1 writer lease opens"),int32(Disk.OpenWriter()),int32(BoundaryStore::EStatus::Ok)))return false;
 const auto First=BoundarySave::Commit(Disk,Legacy,Request);if(!TestEqual(TEXT("Actual supported V1 generation publishes through mandatory validator"),int32(First.Status),int32(BoundaryStore::EStatus::Ok)))return false;
 BoundarySave::FLoadedRun Original;if(!TestEqual(TEXT("Published V1 actually reads and fullyseals"),int32(BoundarySave::Load(Disk,C,Original).Status),int32(BoundaryStore::EStatus::Ok)))return false;
 const auto DiskBefore=BoundaryDiskBytes(*this,Disk.GetProfileDirectory());if(!TestTrue(TEXT("Real published slot/marker files exist before newV2 rejection"),DiskBefore.Num()>=2))return false;
 if(!W.Rich())return false;FDungeonRunSnapshot V2;FDungeonValidatedRun V2Sealed;if(!SealGuard(W,V2,V2Sealed))return false;
 TArray<uint8> V2Bytes;if(!TestTrue(TEXT("Genuine guardedRoot independently encodes exactV2 before V1Adapter rejection"),V2.Schema==2&&V2.Scope==EDungeonRunScope::BoundDevelopmentV2&&DungeonRunSnapshotCodec::Encode(V2,V2Bytes,Why)&&V2Bytes==FCodecOracle::Bytes(FGuardWire::DocumentV2(V2))))return false;
 Request.GenerationId=2;Request.ParentGeneration=1;Request.RunGuid=V2.RunGuid;Request.OwnerId=V2.OwnerId;
 auto Out=Original.Generation;const auto OutBefore=BoundaryGenerationSignature(Out);
 TestFalse(TEXT("V1 MakeGeneration rejects a fullylegal GuardV2 instead of mislabeling old descriptors"),BoundarySave::MakeGeneration(V2,Request,Out,Why));
 TestTrue(TEXT("Version rejection preserves every outputheader field and exact payload bytes"),BoundaryGenerationSignature(Out)==OutBefore&&!Why.IsEmpty());
 auto SealedOut=LegacySealed;const auto* SealedPointer=SealedOut.Get();
 TestFalse(TEXT("Mandatory V1 read-validator rejects deliberate oldenvelope around legalV2 codec"),BoundarySave::ValidateGeneration(BoundaryMislabel(V2,Request),C,SealedOut,Why));
 TestTrue(TEXT("Mislabel failure preserves prior sealedpointer and allV1 owning values"),SealedOut.Get()==SealedPointer&&CodecSignature(*SealedOut.Get())==CodecSignature(Legacy));
 const auto Rejected=BoundarySave::Commit(Disk,V2,Request);TestEqual(TEXT("Actual V1Commit failsclosed before Store publication"),int32(Rejected.Status),int32(BoundaryStore::EStatus::InvalidRequest));
 TestFalse(TEXT("Rejected V2 writer never claims possiblypublished acknowledgement"),Rejected.PublicationMayHaveSucceeded);
 TestTrue(TEXT("Actual rejected V2 leaves every existing profile slot/marker/lease filebyte unchanged with no new files"),BoundarySameDisk(DiskBefore,BoundaryDiskBytes(*this,Disk.GetProfileDirectory())));
 BoundarySave::FLoadedRun StillV1;if(!TestEqual(TEXT("Previouslypublished V1 remains fresh-readable at original head"),int32(BoundarySave::Load(Disk,C,StillV1).Status),int32(BoundaryStore::EStatus::Ok)))return false;
 TestTrue(TEXT("No unsupported V2 head or payload was published"),StillV1.ObservedHeadGeneration==1&&BoundaryGenerationSignature(StillV1.Generation)==BoundaryGenerationSignature(Original.Generation));
 Request.RunGuid=Legacy.RunGuid;Request.OwnerId=Legacy.OwnerId;const auto Second=BoundarySave::Commit(Disk,Legacy,Request);
 if(!TestEqual(TEXT("Same V1 writer still normally publishes validgen2 after refusedV2"),int32(Second.Status),int32(BoundaryStore::EStatus::Ok)))return false;
 BoundaryStore::FGenerationStore Fresh(C.ProfilesDirectory,C.ProfileId,BoundarySave::CurrentVersions);BoundarySave::FLoadedRun Read;
 TestTrue(TEXT("FreshStore reads existing V1 scope/header/completeRun unchanged at newgen2"),BoundarySave::Load(Fresh,C,Read).Status==BoundaryStore::EStatus::Ok&&Read.ObservedHeadGeneration==2&&Read.Run.IsValid()&&CodecSignature(*Read.Run.Get())==CodecSignature(Legacy));
 return true;
}
#endif
