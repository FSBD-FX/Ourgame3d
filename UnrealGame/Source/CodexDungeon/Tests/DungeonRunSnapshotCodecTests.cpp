#if WITH_DEV_AUTOMATION_TESTS
#include "Misc/AutomationTest.h"
#include "../DungeonRunSnapshotCodec.h"
#include "../DungeonSaveGenerationStore.h"
#include "RunCodecFixture_v001.h"
#include "HAL/FileManager.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"
#include <limits>

namespace
{
namespace Codec=DungeonRunSnapshotCodec;
namespace SaveGen=DungeonSaveGenerationStore;
TArray<uint8> CodecUtf8(const FString& S)
{FTCHARToUTF8 U(*S,S.Len());TArray<uint8> B;B.Append(reinterpret_cast<const uint8*>(U.Get()),U.Length());return B;}
FString CodecText(const TArray<uint8>& B)
{FUTF8ToTCHAR U(reinterpret_cast<const ANSICHAR*>(B.GetData()),B.Num());return FString(U.Length(),U.Get());}
bool CodecRoundTrip(FAutomationTestBase& T,const FDungeonRunSnapshot& Saved,const TCHAR* Label)
{
    FString Why;FDungeonValidatedRun Positive;
    if(!T.TestTrue(*(FString(Label)+TEXT(" independent Aggregate positive control")),FDungeonRunAggregate::Validate(Saved,Positive,Why)&&Positive.IsValid()))
    {T.AddInfo(TEXT("Aggregate diagnosis: ")+Why);return false;}
    const auto Exact=CodecSignature(Saved),Expected=FCodecOracle::Bytes(Saved);TArray<uint8> Encoded{0x7a,0x00,0x31};
    const bool EncodedOk=Codec::Encode(Saved,Encoded,Why);
    if(!T.TestTrue(*(FString(Label)+TEXT(" implemented codec encodes the independently legal complete Run")),EncodedOk))
    {T.AddInfo(TEXT("Codec diagnosis: ")+Why);return false;}
    T.TestTrue(*(FString(Label)+TEXT(" exact canonical bytes equal the separate named-field wire oracle")),Encoded==Expected&&Why.IsEmpty());
    TArray<uint8> Twice;T.TestTrue(*(FString(Label)+TEXT(" repeated encode is byte-identical without mutation")),Codec::Encode(Saved,Twice,Why)&&Twice==Expected&&CodecSignature(Saved)==Exact);
    // Decode independent oracle bytes, never merely Decode(Encode(x)).
    FDungeonValidatedRun Decoded;
    if(!T.TestTrue(*(FString(Label)+TEXT(" Decode accepts independent oracle bytes and seals only after full validation")),Codec::Decode(Expected,Decoded,Why)&&Decoded.IsValid()))
    {T.AddInfo(TEXT("Decode diagnosis: ")+Why);return false;}
    T.TestTrue(*(FString(Label)+TEXT(" every owning value including native transforms, PendingPrimary and Box validity is bit exact")),CodecSignature(*Decoded.Get())==Exact&&Why.IsEmpty());
    TArray<uint8> Reencoded;T.TestTrue(*(FString(Label)+TEXT(" decoded owning value has the same canonical bytes")),Codec::Encode(*Decoded.Get(),Reencoded,Why)&&Reencoded==Expected);
    return true;
}
bool CodecHistory(FCodecWorld& F,FDungeonRunSnapshot& Saved,FDungeonValidatedRun& Sealed)
{
    if(!F.Test.TestTrue(TEXT("Real Scene Enter, normal J kill and actual automatic five-coin collection"),F.Create()&&F.KillKnight()&&F.ReachExit()))return false;
    FDungeonRunSnapshot Dead;FDungeonValidatedRun DeadSealed;
    if(!CodecSeal(F,Dead,DeadSealed,TEXT("Actual dead current knight with coin receipt")))return false;
    if(!F.Test.TestTrue(TEXT("Real dead knight, stable three objects and one consumed currency receipt"),Dead.Fighters.Num()==2&&Dead.Fighters[1].Dead&&Dead.Pickups.Num()==3&&Dead.Pickups[0].Consumed&&Dead.Rewards.Collections.Num()==1&&F.Player->Coins==5))return false;
    if(!F.Test.TestTrue(TEXT("Actual normal Enter transfers the same Run without reset or coin loss"),F.Pulse(EKeys::Enter)&&F.Game->RoomNumber==2&&F.Player->Coins==5&&F.BankAdmitted()))return false;
    auto* Bat=F.Game->SpawnStoneBat({800.,80.});
    if(!F.Test.TestTrue(TEXT("Real public room2 bat admission produces its supported owner"),Bat&&Bat->GetStoneBatDriver()))return false;
    F.Frame(.01f);if(!CodecSeal(F,Saved,Sealed,TEXT("Actual cross-room rich source")))return false;
    return F.Test.TestTrue(TEXT("Historical dead binding, consumed/retired reward, both fog banks and current bat are all present"),
        Saved.Fighters.Num()==3&&Saved.Fighters[2].Bat.IsSet()&&Saved.EnemyOrder.Num()==2&&Saved.Rewards.RetiredEntities.Num()==1
        &&Saved.Rewards.Objects.Num()==3&&Saved.Rewards.Objects[0].Consumed&&Saved.Rewards.Objects[0].Retired
        &&Saved.Rewards.Collections.Num()==1&&Saved.Exploration.Rooms.Num()==2&&Saved.WeaponWorld.State.ActorBindings[0].RoomInstanceId==1);
}
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRunCodecAccepted,
    "CodexDungeon.Content.RunCodec.AcceptedEquipmentReloadAndLargeRng",
    EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FRunCodecAccepted::RunTest(const FString&)
{
    bool BufferPassed=false;
    {
        FCodecWorld Buffer(*this);
        if(!TestTrue(TEXT("Separate genuine normal-input combo buffer fixture"),Buffer.Create()&&Buffer.Pulse(EKeys::J)))return false;
        const auto A=Buffer.Player->GetMeleeCombatState().Action;
        if(!TestTrue(TEXT("Normal late-window J queues an actual not-yet-consumed primary request"),A.Active&&Buffer.AdvanceTo(A.End-.1)
            &&Buffer.Pulse(EKeys::J)&&Buffer.Player->GetMeleeCombatState().PendingPrimary))return false;
        FDungeonRunSnapshot Queued;FDungeonValidatedRun QueuedSealed;
        if(!CodecSeal(Buffer,Queued,QueuedSealed,TEXT("Actual pending primary value")))return false;
        if(!TestTrue(TEXT("Captured true PendingPrimary differs from an otherwise identical false value in both independent oracles"),Queued.Fighters[0].Player.GetValue().Combat.PendingPrimary))return false;
        auto Cleared=Queued;Cleared.Fighters[0].Player.GetValue().Combat.PendingPrimary=false;
        TestTrue(TEXT("Independent typed signature and named wire both cover PendingPrimary"),CodecSignature(Cleared)!=CodecSignature(Queued)&&FCodecOracle::Bytes(Cleared)!=FCodecOracle::Bytes(Queued));
        BufferPassed=CodecRoundTrip(*this,Queued,TEXT("Actual PendingPrimary preserves saved value"));
    }
    FCodecWorld F(*this);if(!TestTrue(TEXT("Genuine Scene/PC/HUD normal Enter fixture"),F.Create()))return false;
    if(!TestTrue(TEXT("Normal J creates and locks a real seed-one starter melee"),F.Pulse(EKeys::J)&&F.Player->GetMeleeCombatState().Action.Active))return false;
    const auto Melee=F.Player->GetMeleeCombatState().Action;
    if(!TestTrue(TEXT("Actual melee advances through its original lock and end"),F.AdvanceTo(Melee.LockTime)&&F.AdvanceTo(Melee.End)))return false;
    IV::FItem X;X.ContentId="WPN-XBW-001";X.Ammo=0.;
    const auto R=F.Game->RegisterEquipmentSource(TEXT("run.codec.real.empty-xbw"),X,F.Player->GetGroundPosition()+FVector2D(30.,0.),true);
    if(!TestTrue(TEXT("Normal E starts a real accepted source/instance pickup"),R.Ok()&&F.Pulse(EKeys::E)&&F.Game->GetEquipmentView().Action.Active))return false;
    const auto Pick=F.Game->GetEquipmentView().Action;
    if(!TestTrue(TEXT("Original pickup reaches middle .125 boundary without granting the item"),F.AdvanceTo(Pick.Start+.125)))return false;
    FDungeonRunSnapshot Pending;FDungeonValidatedRun PendingSealed;
    if(!CodecSeal(F,Pending,PendingSealed,TEXT("Actual accepted pending equipment")))return false;
    if(!TestTrue(TEXT("Original pending plan/source IDs and original absolute deadline are independently real"),Pending.Equipment.View.Action.Active
        &&Pending.Equipment.PendingPlan.SourceId==R.SourceId&&Pending.Equipment.PendingPlan.InstanceId==R.InstanceId
        &&Pending.Equipment.InventoryState.Weapons[1]==0&&Pending.Equipment.View.Action.Deadline==Pick.Deadline))return false;
    // Do not stop fixture construction when Encode is still the honest stub.
    const bool PendingPassed=CodecRoundTrip(*this,Pending,TEXT("Pending equipment"));
    if(!TestTrue(TEXT("Normal pickup finishes and normal T starts empty-magazine reload"),F.AdvanceTo(Pick.Deadline)&&F.Player->WeaponId==TEXT("WPN-XBW-001")&&F.Pulse(EKeys::T)))return false;
    const auto Reload=F.Player->GetWeaponActionsState().Action;
    F.Player->GetWeaponMuzzleComponent()->SetRelativeLocation(FVector(24.,7.,65.));
    if(!TestTrue(TEXT("Actual reload reaches insert boundary while still active"),Reload.Active&&Reload.Type==WA::EAction::Reload&&F.AdvanceTo(Reload.Start+.65)
        &&F.Player->GetWeaponActionsState().Action.Active&&F.HUD->GetActionAudioPlayRequests(TEXT("XBW_RELOAD_DRAW_01"))==1&&F.HUD->GetActionAudioPlayRequests(TEXT("XBW_RELOAD_INSERT_01"))==1))return false;
    FDungeonRunSnapshot Loading;FDungeonValidatedRun LoadingSealed;
    if(!CodecSeal(F,Loading,LoadingSealed,TEXT("Actual post-insert pre-complete reload")))return false;
    const auto* Cursor=Loading.Audio.WeaponCursors.FindByPredicate([&](const auto& C){return C.OwnerId==Loading.OwnerId;});
    if(!TestTrue(TEXT("Custom actual muzzle and spent draw/insert cursors retain the still-pending original reload"),Loading.Fighters[0].CustomMuzzle
        &&Loading.Fighters[0].CustomMuzzleRelative.GetTranslation()==FVector(24.,7.,65.)&&Cursor&&Cursor->Cursor.DrawObserved&&Cursor->Cursor.InsertObserved
        &&Cursor->Cursor.Reload.ActionId==Reload.ActionId&&Cursor->Cursor.Reload.End==Reload.End))return false;
    const bool LoadingPassed=CodecRoundTrip(*this,Loading,TEXT("Reload native and audio continuation"));
    if(!TestTrue(TEXT("Original reload completes and real normal J starts loaded crossbow primary"),F.AdvanceTo(Reload.End)&&F.Pulse(EKeys::J)&&F.Player->GetWeaponActionsState().Action.Active))return false;
    const auto Shot=F.Player->GetWeaponActionsState().Action;
    if(!TestTrue(TEXT("Real crossbow lock consumes a second accepted RNG draw"),Shot.Type==WA::EAction::Primary&&F.AdvanceTo(Shot.LockAt)))return false;
    FDungeonRunSnapshot Locked;FDungeonValidatedRun LockedSealed;
    if(!CodecSeal(F,Locked,LockedSealed,TEXT("Actual second accepted RNG domain")))return false;
    if(!TestTrue(TEXT("Independent seed-one literals both exceed JSON exact-integer range and match real receipts"),Locked.Equipment.View.CombatSeed==1&&Locked.Equipment.View.NextCritDraw==2
        &&Locked.Equipment.CritReceipts.Num()==2&&Locked.Equipment.CritReceipts[0].Bits==2009361098267089954ULL
        &&Locked.Equipment.CritReceipts[1].Bits==8859251267152808453ULL&&!Locked.Equipment.CritReceipts[0].WeaponAction&&Locked.Equipment.CritReceipts[1].WeaponAction))return false;
    const bool LockedPassed=CodecRoundTrip(*this,Locked,TEXT("Large RNG exact values"));
    return BufferPassed&&PendingPassed&&LoadingPassed&&LockedPassed;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRunCodecHistory,
    "CodexDungeon.Content.RunCodec.CanonicalCrossRoomHistoryAndNativeBits",
    EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FRunCodecHistory::RunTest(const FString&)
{
    FCodecWorld F(*this);FDungeonRunSnapshot Saved;FDungeonValidatedRun Sealed;if(!CodecHistory(F,Saved,Sealed))return false;
    const auto Source=CodecSignature(Saved);const bool RealPassed=CodecRoundTrip(*this,Saved,TEXT("Actual cross-room history"));
    // Explicit legal typed variants are independently validated before encoding;
    // they are not represented as facts observed from normal player input.
    auto Variant=Saved;const TCHAR Embedded[]={TCHAR(0x949f),TCHAR(0x76d4),TCHAR(0),TEXT('"'),TEXT('\\'),TEXT('\n')};
    Variant.LastMessage=FString(UE_ARRAY_COUNT(Embedded),Embedded);Variant.Fighters[0].HitFlash=-0.0f;
    FDungeonValidatedRun VariantSealed;FString Why;
    if(!TestTrue(TEXT("Typed Unicode embedded-NUL and signed-zero variant remains semantically legal"),FDungeonRunAggregate::Validate(Variant,VariantSealed,Why)&&VariantSealed.IsValid()))return false;
    const auto Oracle=CodecText(FCodecOracle::Bytes(Variant));
    TestTrue(TEXT("Independent oracle represents signed float zero and embedded NUL without loss"),Oracle.Contains(TEXT("\"HitFlash\":\"80000000\""))&&Oracle.Contains(TEXT("\\u0000")));
    auto Reordered=Variant;Reordered.Scene.Rooms.Reset();TArray<uint64> Keys;Variant.Scene.Rooms.GetKeys(Keys);Keys.Sort(TGreater<uint64>());
    for(uint64 K:Keys)Reordered.Scene.Rooms.Add(K,Variant.Scene.Rooms[K]);
    TestTrue(TEXT("Independent map oracle sorts numeric keys rather than relying on TMap insertion"),FCodecOracle::Bytes(Reordered)==FCodecOracle::Bytes(Variant));
    TArray<uint8> A,B;const bool One=Codec::Encode(Variant,A,Why),Two=Codec::Encode(Reordered,B,Why);
    TestTrue(TEXT("Production canonical bytes are exact for legal Unicode/native-bit values and numeric map order"),One&&Two&&A==FCodecOracle::Bytes(Variant)&&B==A);
    const bool VariantPassed=CodecRoundTrip(*this,Variant,TEXT("Legal embedded NUL, signed-zero and native transform"));
    TestTrue(TEXT("All codec observations leave original actual cross-room source unchanged"),CodecSignature(Saved)==Source);
    return RealPassed&&VariantPassed&&One&&Two;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRunCodecReject,
    "CodexDungeon.Content.RunCodec.MalformedAndSemanticFailureIsAtomic",
    EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FRunCodecReject::RunTest(const FString&)
{
    FCodecWorld F(*this);FDungeonRunSnapshot Saved;FDungeonValidatedRun Sealed;if(!CodecHistory(F,Saved,Sealed))return false;
    const auto Exact=CodecSignature(Saved);const auto* Pointer=Sealed.Get();FString Why;
    FDungeonValidatedRun Positive;const bool Decoded=Codec::Decode(FCodecOracle::Bytes(Saved),Positive,Why);
    TestTrue(TEXT("Positive control: independently encoded legal full Run must Decode before negative cases"),Decoded&&Positive.IsValid()&&CodecSignature(*Positive.Get())==Exact);
    const auto Reject=[&](const TCHAR* Label,const TArray<uint8>& Bad)
    {
        FString Invalid;TestFalse(*(FString(Label)+TEXT(" is rejected")),Codec::Decode(Bad,Sealed,Invalid));
        TestTrue(*(FString(Label)+TEXT(" retains original sealed pointer and every owned value atomically")),!Invalid.IsEmpty()&&Sealed.Get()==Pointer&&CodecSignature(*Sealed.Get())==Exact&&CodecSignature(Saved)==Exact);
    };
    const auto Good=FCodecOracle::Bytes(Saved);const auto Text=CodecText(Good);
    Reject(TEXT("Empty payload"),{});auto Truncated=Good;Truncated.SetNum(Truncated.Num()/2);Reject(TEXT("Truncated JSON"),Truncated);
    auto InvalidUtf8=Good;InvalidUtf8.Insert(0xff,1);Reject(TEXT("Invalid UTF8"),InvalidUtf8);
    auto Bom=Good;Bom.Insert(0xbf,0);Bom.Insert(0xbb,0);Bom.Insert(0xef,0);Reject(TEXT("BOM is not canonical UTF8"),Bom);
    Reject(TEXT("Trailing data"),CodecUtf8(Text+TEXT("{}")));
    Reject(TEXT("Noncanonical whitespace"),CodecUtf8(TEXT(" ")+Text));
    Reject(TEXT("Repeated literal field"),CodecUtf8(TEXT("{\"codec\":\"bound-run-v1\",")+Text.Mid(1)));
    Reject(TEXT("Escaped repeated field"),CodecUtf8(TEXT("{\"\\u0063odec\":\"bound-run-v1\",")+Text.Mid(1)));
    const auto JsonBad=[&](const TCHAR* Label,auto Mutate){auto Doc=FCodecOracle::Document(Saved);Mutate(Doc,Doc->GetObjectField(TEXT("snapshot")));Reject(Label,FCodecOracle::Bytes(Doc));};
    JsonBad(TEXT("Unknown document field"),[](auto D,auto){D->SetBoolField(TEXT("future"),true);});
    JsonBad(TEXT("Missing required root field"),[](auto,auto S){S->RemoveField(TEXT("SimulationTime"));});
    JsonBad(TEXT("Unknown nested owner field"),[](auto,auto S){S->GetObjectField(TEXT("Audio"))->SetStringField(TEXT("FutureCursor"),TEXT("1"));});
    JsonBad(TEXT("Wrong integer token type"),[](auto,auto S){S->SetNumberField(TEXT("OwnerId"),1.);});
    JsonBad(TEXT("Leading zero integer"),[](auto,auto S){S->SetStringField(TEXT("OwnerId"),TEXT("01"));});
    JsonBad(TEXT("Overflow integer"),[](auto,auto S){S->SetStringField(TEXT("OwnerId"),TEXT("18446744073709551616"));});
    JsonBad(TEXT("Overflow uint32 schema"),[](auto,auto S){S->SetStringField(TEXT("Schema"),TEXT("4294967296"));});
    JsonBad(TEXT("Negative unsigned identity"),[](auto,auto S){S->SetStringField(TEXT("OwnerId"),TEXT("-1"));});
    JsonBad(TEXT("Missing explicit optional field"),[](auto,auto S){S->GetArrayField(TEXT("Fighters"))[0]->AsObject()->RemoveField(TEXT("Knight"));});
    JsonBad(TEXT("Duplicate numeric map entry"),[](auto,auto S){auto Scene=S->GetObjectField(TEXT("Scene"));auto Rooms=Scene->GetArrayField(TEXT("Rooms"));const auto Copy=Rooms[0];Rooms.Add(Copy);Scene->SetArrayField(TEXT("Rooms"),Rooms);});
    JsonBad(TEXT("Changed array traversal order"),[](auto,auto S){auto Order=S->GetArrayField(TEXT("EnemyOrder"));Order.Swap(0,1);S->SetArrayField(TEXT("EnemyOrder"),Order);});
    JsonBad(TEXT("Invalid hex width"),[](auto,auto S){S->SetStringField(TEXT("SimulationTime"),TEXT("0000"));});
    JsonBad(TEXT("Uppercase hex is not canonical"),[](auto,auto S){S->SetStringField(TEXT("SimulationTime"),TEXT("3FF0000000000000"));});
    JsonBad(TEXT("Nonfinite double hex"),[](auto,auto S){S->SetStringField(TEXT("SimulationTime"),TEXT("7ff8000000000000"));});
    JsonBad(TEXT("Unknown codec version"),[](auto D,auto){D->SetStringField(TEXT("codec"),TEXT("bound-run-v99"));});
    const auto SemanticBad=[&](const TCHAR* Label,auto Mutate)
    {
        auto Bad=Saved;Mutate(Bad);FDungeonValidatedRun Check;FString BadWhy;
        TestFalse(*(FString(Label)+TEXT(" independent Aggregate proves semantic negative premise")),FDungeonRunAggregate::Validate(Bad,Check,BadWhy));
        TestTrue(*(FString(Label)+TEXT(" semantic premise diagnoses without sealing")),!BadWhy.IsEmpty()&&!Check.IsValid());
        Reject(Label,FCodecOracle::Bytes(Bad));TArray<uint8> Out{0x12,0x00,0xee};const auto Original=Out;
        TestFalse(*(FString(Label)+TEXT(" invalid owning input cannot Encode")),Codec::Encode(Bad,Out,BadWhy));
        TestTrue(*(FString(Label)+TEXT(" failed Encode retains original output bytes")),Out==Original&&!BadWhy.IsEmpty());
    };
    SemanticBad(TEXT("Unknown snapshot scope"),[](auto& S){S.Scope=EDungeonRunScope::Unsupported;});
    SemanticBad(TEXT("Wrong enclosing room"),[](auto& S){++S.RoomInstanceId;});
    SemanticBad(TEXT("Duplicated enemy order"),[](auto& S){const auto Id=S.EnemyOrder[0];S.EnemyOrder.Add(Id);});
    SemanticBad(TEXT("Missing current bat owner"),[](auto& S){S.Fighters.RemoveAt(2);});
    SemanticBad(TEXT("Missing original consumed coin receipt"),[](auto& S){S.Rewards.Collections.Reset();});
    SemanticBad(TEXT("Missing observed fog bank"),[](auto& S){S.Exploration.Rooms.Reset();});
    SemanticBad(TEXT("Invalid audio continuation tail"),[](auto& S){S.Audio.NextActionSequence=0;});
    SemanticBad(TEXT("Old Fighter schema"),[](auto& S){S.Fighters[0].Schema=1;});
    SemanticBad(TEXT("Invalid native barrier flag"),[](auto& S){S.Scene.CurrentRoom.Layout.Barrier.bIsValid=0;});
    return Decoded;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRunCodecStore,
    "CodexDungeon.Content.RunCodec.MandatoryStoreDecodeAndHeaderClock",
    EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FRunCodecStore::RunTest(const FString&)
{
    FCodecWorld F(*this);FDungeonRunSnapshot Saved;FDungeonValidatedRun Sealed;if(!CodecHistory(F,Saved,Sealed))return false;
    const auto Exact=CodecSignature(Saved);const double Time=F.Game->GetSimulationTime();const auto Player=F.Game->PlayerFighter;
    const FString Root=FPaths::ConvertRelativePathToFull(FPaths::ProjectSavedDir()/TEXT("Automation/RunSnapshotCodec")/FGuid::NewGuid().ToString(EGuidFormats::Digits));
    AddInfo(TEXT("Retained real isolated Codec/Store IO: ")+Root);
    if(!TestTrue(TEXT("Create actual isolated Store directory"),IFileManager::Get().MakeDirectory(*Root,true)))return false;
    const auto Probe=CodecUtf8(TEXT("real codec store fixture\n"));TArray<uint8> Read;
    if(!TestTrue(TEXT("Real Store fixture writes and reads exact independent bytes"),FFileHelper::SaveArrayToFile(Probe,*(Root/TEXT("io-proof.txt")))&&FFileHelper::LoadFileToArray(Read,*(Root/TEXT("io-proof.txt")))&&Read==Probe))return false;
    const FGuid Profile=FGuid::NewGuid();const SaveGen::FVersions Versions{TEXT("bound-run-codec-v1"),TEXT("bound-development-v1"),TEXT("world-cm-v1")};
    SaveGen::FGenerationStore Store(Root,Profile,Versions);TestEqual(TEXT("Actual exclusive writer opens"),int32(Store.OpenWriter()),int32(SaveGen::EStatus::Ok));
    SaveGen::FGeneration G;G.ProfileId=Profile;G.GenerationId=1;G.Versions=Versions;G.BuildId=TEXT("run-codec-stage0-v1");G.RunSimulationTime=Saved.SimulationTime;G.CanonicalPayload=FCodecOracle::Bytes(Saved);
    int32 Calls=0;const auto* OldSealed=Sealed.Get();
    const SaveGen::FPayloadValidator Validator=[&](const SaveGen::FGeneration& Candidate,FString& Why)
    {
        ++Calls;FDungeonValidatedRun Valid;
        if(!Codec::Decode(Candidate.CanonicalPayload,Valid,Why))return false;
        if(!Candidate.RunSimulationTime.IsSet()||Candidate.RunSimulationTime.GetValue()!=Valid.Get()->SimulationTime)
        {Why=TEXT("Store envelope time differs from decoded authoritative root time");return false;}
        return true;
    };
    TestEqual(TEXT("Store never accepts missing mandatory semantic validator"),int32(Store.Commit(G,{}).Status),int32(SaveGen::EStatus::InvalidRequest));
    const auto Committed=Store.Commit(G,Validator);
    if(!TestEqual(TEXT("Independent legal complete Run passes real Decode callback and actually publishes"),int32(Committed.Status),int32(SaveGen::EStatus::Ok)))
    {AddInfo(TEXT("Store/Codec diagnosis: ")+Committed.Diagnostic);return false;}
    TestTrue(TEXT("Actual disk publication invoked pure semantic Decode"),Calls>0);
    const FString ProfileDir=Store.GetProfileDirectory();TArray<uint8> OldBundle,OldMarker;
    if(!TestTrue(TEXT("Read genuine published A bundle and marker"),FFileHelper::LoadFileToArray(OldBundle,*(ProfileDir/TEXT("slot-A.bundle.json")))&&FFileHelper::LoadFileToArray(OldMarker,*(ProfileDir/TEXT("slot-A.commit.json")))))return false;
    auto Bad=G;Bad.GenerationId=2;Bad.ParentGeneration=1;Bad.RunSimulationTime=Saved.SimulationTime+1.;
    TestEqual(TEXT("Mismatched envelope/root simulation clock refuses publication"),int32(Store.Commit(Bad,Validator).Status),int32(SaveGen::EStatus::ValidatorRejected));
    Bad.RunSimulationTime.Reset();TestEqual(TEXT("Missing envelope Run clock refuses publication"),int32(Store.Commit(Bad,Validator).Status),int32(SaveGen::EStatus::ValidatorRejected));
    Bad=G;Bad.GenerationId=2;Bad.ParentGeneration=1;auto Semantic=Saved;Semantic.Audio.NextActionSequence=0;Bad.CanonicalPayload=FCodecOracle::Bytes(Semantic);
    TestEqual(TEXT("Valid JSON with wrong owner semantics refuses publication via Decode"),int32(Store.Commit(Bad,Validator).Status),int32(SaveGen::EStatus::ValidatorRejected));
    TestFalse(TEXT("No rejected next generation has a B marker"),IFileManager::Get().FileExists(*(ProfileDir/TEXT("slot-B.commit.json"))));
    TArray<uint8> B,M;TestTrue(TEXT("Rejected candidates retain original whole A bundle/marker bytes"),FFileHelper::LoadFileToArray(B,*(ProfileDir/TEXT("slot-A.bundle.json")))&&FFileHelper::LoadFileToArray(M,*(ProfileDir/TEXT("slot-A.commit.json")))&&B==OldBundle&&M==OldMarker);
    Store.CloseWriter();SaveGen::FGenerationStore Fresh(Root,Profile,Versions);
    TestEqual(TEXT("Fresh disk object also refuses missing semantic callback"),int32(Fresh.Load({}).Status),int32(SaveGen::EStatus::InvalidRequest));
    const auto Loaded=Fresh.Load(Validator);TestEqual(TEXT("Fresh actual disk read revalidates the exact owning payload"),int32(Loaded.Status),int32(SaveGen::EStatus::Ok));
    TestTrue(TEXT("Fresh disk object receives byte-exact complete payload and unchanged clock"),Loaded.Generation.CanonicalPayload==G.CanonicalPayload&&Loaded.Generation.RunSimulationTime.IsSet()&&Loaded.Generation.RunSimulationTime.GetValue()==Saved.SimulationTime);
    // Produce a real integrity-correct but semantically invalid highest B2 via
    // an explicitly permissive fixture writer. The actual reader must use the
    // mandatory Decode callback and must never fall back to good A1.
    TestEqual(TEXT("Fixture writer reopens to seed a real invalid-semantic published head"),int32(Store.OpenWriter()),int32(SaveGen::EStatus::Ok));
    const SaveGen::FPayloadValidator FixtureOnlyAccept=[](const SaveGen::FGeneration&,FString&){return true;};
    const auto BadPublished=Store.Commit(Bad,FixtureOnlyAccept);
    if(!TestEqual(TEXT("Fixture creates a genuine SHA/CRC/marker-valid B2 with wrong owner semantics"),int32(BadPublished.Status),int32(SaveGen::EStatus::Ok)))return false;
    Store.CloseWriter();TArray<uint8> BadBundle,BadMarker;
    if(!TestTrue(TEXT("Read original real invalid-semantic B2 before reader rejection"),FFileHelper::LoadFileToArray(BadBundle,*(ProfileDir/TEXT("slot-B.bundle.json")))&&FFileHelper::LoadFileToArray(BadMarker,*(ProfileDir/TEXT("slot-B.commit.json")))))return false;
    SaveGen::FGenerationStore StrictReader(Root,Profile,Versions);const auto Rejected=StrictReader.Load(Validator);
    TestTrue(TEXT("Actual latest B2 semantic rejection requires explicit recovery without loading older valid A1"),Rejected.Status==SaveGen::EStatus::RecoveryRequired&&Rejected.ObservedHeadGeneration==2&&Rejected.Generation.CanonicalPayload.IsEmpty());
    TestTrue(TEXT("Semantic read rejection retains original invalid head bytes for recovery evidence"),FFileHelper::LoadFileToArray(B,*(ProfileDir/TEXT("slot-B.bundle.json")))&&FFileHelper::LoadFileToArray(M,*(ProfileDir/TEXT("slot-B.commit.json")))&&B==BadBundle&&M==BadMarker);
    TestTrue(TEXT("Disk callbacks never Prepare/Install, advance source, replace actors, emit sounds or change old sealed value"),F.Game->PlayerFighter==Player&&F.Game->GetSimulationTime()==Time&&Sealed.Get()==OldSealed&&CodecSignature(*Sealed.Get())==Exact);
    FDungeonRunSnapshot After;FDungeonValidatedRun AfterSealed;if(!CodecSeal(F,After,AfterSealed,TEXT("Actual live source after all disk callbacks")))return false;
    TestTrue(TEXT("Every authoritative live field including IDs/RNG/fog/audio remains exact after Store IO"),CodecSignature(After)==Exact);
    return true;
}
#endif
