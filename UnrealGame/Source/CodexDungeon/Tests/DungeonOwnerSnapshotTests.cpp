#if WITH_DEV_AUTOMATION_TESTS
#include "Misc/AutomationTest.h"
#include "../DungeonExploration.h"
#include "../DungeonSceneObjects.h"
#include <limits>

namespace
{
using DungeonExploration::FExploration;
bool SameFog(const DungeonExploration::FState& A,const DungeonExploration::FState& B)
{
    return A.Schema==B.Schema&&A.RoomId==B.RoomId&&A.Bounds.MinX==B.Bounds.MinX
        &&A.Bounds.MaxX==B.Bounds.MaxX&&A.Bounds.MinY==B.Bounds.MinY&&A.Bounds.MaxY==B.Bounds.MaxY&&A.Memory==B.Memory;
}
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDungeonFogSnapshotRoundTrip,
    "CodexDungeon.Content.RunOwnerSnapshot.ExplorationExactMemoryAndContinuation",
    EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FDungeonFogSnapshotRoundTrip::RunTest(const FString&)
{
    FExploration Live({-256,2304,-640,640},17);Live.Reveal({0,0});Live.Reveal({1024,128});
    const auto Saved=Live.Capture();
    TestEqual(TEXT("Capture real room identity"),Saved.RoomId,17);
    TestTrue(TEXT("Capture actual revealed vertex data"),!Saved.Memory.empty());
    FExploration Restored({0,64,0,64},99);
    if(!TestTrue(TEXT("Restore into an independent owner"),Restored.Restore(Saved)))return false;
    TestTrue(TEXT("Every stored double survives exactly"),SameFog(Saved,Restored.Capture()));
    TestEqual(TEXT("Explored count derived without a new reveal"),Restored.ExploredVertexCount(),Live.ExploredVertexCount());
    for(const auto Point:{DungeonExploration::FPoint{0,0},{512,96},{1024,128},{2304,640}})
        TestEqual(TEXT("Restored bilinear memory is exact"),Restored.MemoryAt(Point),Live.MemoryAt(Point));
    Live.Reveal({1792,-128});Restored.Reveal({1792,-128});
    TestTrue(TEXT("Next reveal has identical outcome and preserves older regions"),SameFog(Live.Capture(),Restored.Capture()));
    auto Detached=Saved;Detached.Memory[0]=.123;
    TestTrue(TEXT("Value snapshot has no alias to live memory"),SameFog(Live.Capture(),Restored.Capture()));
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDungeonFogSnapshotReject,
    "CodexDungeon.Content.RunOwnerSnapshot.ExplorationInvalidRestoreIsAtomic",
    EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FDungeonFogSnapshotReject::RunTest(const FString&)
{
    FExploration Live({0,70,0,300},9);Live.Reveal({32,256});const auto Before=Live.Capture();
    if(!TestTrue(TEXT("Valid roundtrip control"),Live.Restore(Before)))return false;
    const auto Count=Live.ExploredVertexCount();
    const auto Reject=[&](const DungeonExploration::FState& Bad)
    {
        TestFalse(TEXT("Malformed candidate rejected"),Live.Restore(Bad));
        TestTrue(TEXT("Rejected candidate leaves complete memory/bounds/room unchanged"),SameFog(Before,Live.Capture()));
        TestEqual(TEXT("Rejected candidate leaves derived count unchanged"),Live.ExploredVertexCount(),Count);
    };
    auto Bad=Before;++Bad.Schema;Reject(Bad);
    Bad=Before;Bad.RoomId=0;Reject(Bad);
    Bad=Before;Bad.Memory.pop_back();Reject(Bad);
    Bad=Before;Bad.Memory.push_back(0.);Reject(Bad);
    for(double Value:{-0.01,1.01,std::numeric_limits<double>::quiet_NaN(),std::numeric_limits<double>::infinity()})
    {Bad=Before;Bad.Memory[0]=Value;Reject(Bad);}
    Bad=Before;Bad.Bounds.MaxX=Bad.Bounds.MinX;Reject(Bad);
    Bad=Before;Bad.Bounds.MaxY=std::numeric_limits<double>::quiet_NaN();Reject(Bad);
    Bad=Before;Bad.Bounds.MaxX=1e100;Reject(Bad);
    // Finite dimensions can still collapse 64-unit vertices at a very large
    // binary64 origin. This is 257 X vertices * 2 Y vertices, not huge allocation.
    Bad=Before;Bad.Bounds={1e20,1e20+16384.,0.,64.};Bad.Memory.assign(514,.5);
    FExploration Probe({0,64,0,64},1);
    const bool InstalledCollapsed=Probe.Restore(Bad);
    const double AtMaximum=Probe.MemoryAt({Bad.Bounds.MaxX,0.});uint64 QueryBits=0;
    FMemory::Memcpy(&QueryBits,&AtMaximum,sizeof(QueryBits));
    const bool FiniteAtMaximum=std::isfinite(AtMaximum);
    AddInfo(FString::Printf(TEXT("Actual collapsed-axis candidate installed=%d query-finite=%d query=%.17g query-bits=%016llx"),InstalledCollapsed,FiniteAtMaximum,AtMaximum,QueryBits));
    if(InstalledCollapsed)
    {
        TestTrue(TEXT("Accepted finite-bound memory must not produce NaN"),FiniteAtMaximum);
        TestEqual(TEXT("Accepted constant memory must interpolate to the same constant"),AtMaximum,.5);
    }
    Reject(Bad);
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDungeonSceneSnapshotRoundTrip,
    "CodexDungeon.Content.RunOwnerSnapshot.SceneHistoryAndPendingInteraction",
    EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FDungeonSceneSnapshotRoundTrip::RunTest(const FString&)
{
    const FGuid Run=FGuid::NewGuid();FDungeonSceneObjects Live;
    if(!TestTrue(TEXT("Begin actual first scene owner room"),Live.BeginRoom(Run,101)))return false;
    TestTrue(TEXT("Survey actual first room once"),Live.MarkSurvey(101,1));
    TestTrue(TEXT("Enter second room without resetting previous facts"),Live.BeginRoom(Run,102));
    Live.Interaction={true,false,EDungeonSceneInteractionKind::Survey,102,1,12.5,EDungeonSceneFailure::None};
    const auto Saved=Live.Capture();FString Why;FDungeonSceneObjects Restored;
    if(!TestTrue(TEXT("Restore actual history and in-flight survey"),Restored.Restore(Saved,Why)))return false;
    TestTrue(TEXT("Current Run and room are preserved"),Restored.Current().RunGuid==Run&&Restored.Current().RoomInstanceId==102);
    const auto* Old=Restored.FindRoom(101);
    TestTrue(TEXT("Previous room survey is not forgotten/reissued"),Old&&Old->Objects[0].Surveyed&&Old->Objects[0].SurveyCount==1);
    TestTrue(TEXT("Pending survey retains time and identity"),Restored.Interaction.Pending&&!Restored.Interaction.NeedsConfirmation
        &&Restored.Interaction.Kind==EDungeonSceneInteractionKind::Survey&&Restored.Interaction.RoomInstanceId==102
        &&Restored.Interaction.ObjectId==1&&Restored.Interaction.AtTime==12.5);
    TestTrue(TEXT("Existing in-flight survey completes once"),Restored.MarkSurvey(102,1));
    TestFalse(TEXT("Repeated survey remains consumed"),Restored.MarkSurvey(102,1));
    Restored.Interaction={true,true,EDungeonSceneInteractionKind::Exit,102,2,14.25,EDungeonSceneFailure::None};
    const auto Confirmation=Restored.Capture();FDungeonSceneObjects Confirmed;
    TestTrue(TEXT("Pending exit confirmation roundtrips"),Confirmed.Restore(Confirmation,Why));
    TestTrue(TEXT("Restore does not auto-confirm or switch room"),Confirmed.Current().RoomInstanceId==102&&Confirmed.Interaction.Pending
        &&Confirmed.Interaction.NeedsConfirmation&&Confirmed.Interaction.AtTime==14.25);
    Confirmed.Interaction.NeedsConfirmation=false; // Accepted exit awaiting its semantic commit is also a real owner state.
    FDungeonSceneObjects AcceptedExit;
    TestTrue(TEXT("Already-confirmed pending exit also roundtrips"),AcceptedExit.Restore(Confirmed.Capture(),Why));
    TestTrue(TEXT("Restore never commits an already-confirmed exit itself"),AcceptedExit.Current().RoomInstanceId==102
        &&AcceptedExit.Interaction.Pending&&!AcceptedExit.Interaction.NeedsConfirmation
        &&AcceptedExit.Interaction.Kind==EDungeonSceneInteractionKind::Exit);
    TestTrue(TEXT("Return to remembered room after restore"),Confirmed.BeginRoom(Run,101));
    TestFalse(TEXT("Prior surveyed room is still consumed after normal revisit"),Confirmed.MarkSurvey(101,1));
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDungeonSceneSnapshotReject,
    "CodexDungeon.Content.RunOwnerSnapshot.SceneCrossReferenceRejectionIsAtomic",
    EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FDungeonSceneSnapshotReject::RunTest(const FString&)
{
    const FGuid Run=FGuid::NewGuid();FDungeonSceneObjects Live;Live.BeginRoom(Run,9);Live.MarkSurvey(9,1);
    Live.Interaction={true,true,EDungeonSceneInteractionKind::Exit,9,2,5.,EDungeonSceneFailure::None};
    const auto Before=Live.Capture();FString Why;
    if(!TestTrue(TEXT("Valid active-state control"),Live.Restore(Before,Why)))return false;
    const auto Reject=[&](const TCHAR* Label,const FDungeonSceneObjectsSnapshot& Bad)
    {
        const bool Accepted=Live.Restore(Bad,Why);
        AddInfo(FString::Printf(TEXT("Actual scene rejection case %s accepted=%d"),Label,Accepted));
        TestFalse(*(FString(Label)+TEXT(" scene candidate rejected")),Accepted);
        const auto After=Live.Capture();const auto* Room=Live.FindRoom(9);
        TestTrue(TEXT("Rejected restore preserves Run, history, survey and confirmation"),After.CurrentRoom.RunGuid==Run
            &&After.CurrentRoom.RoomInstanceId==9&&After.Rooms.Num()==Before.Rooms.Num()&&Room&&Room->Objects[0].SurveyCount==1
            &&After.Interaction.Pending&&After.Interaction.NeedsConfirmation&&After.Interaction.AtTime==5.);
        TestFalse(*(FString(Label)+TEXT(" rejection gives a diagnostic")),Why.IsEmpty());
    };
    auto Bad=Before;++Bad.Schema;Reject(TEXT("unknown-schema"),Bad);
    Bad=Before;Bad.CurrentRoom.RunGuid=FGuid::NewGuid();Reject(TEXT("current-run-mismatch"),Bad);
    Bad=Before;Bad.Rooms.Reset();Reject(TEXT("missing-history"),Bad);
    Bad=Before;Bad.Rooms[9].RoomInstanceId=10;Reject(TEXT("history-key-mismatch"),Bad);
    Bad=Before;Bad.CurrentRoom.Objects[0].SurveyCount=2;Reject(TEXT("survey-count"),Bad);
    Bad=Before;Bad.CurrentRoom.Objects[1].ObjectId=1;Reject(TEXT("duplicate-object-id"),Bad);
    Bad=Before;Bad.CurrentRoom.Layout.Version=2;Reject(TEXT("unknown-layout-version"),Bad);
    Bad=Before;Bad.CurrentRoom.Layout.Survey.X=std::numeric_limits<double>::quiet_NaN();Reject(TEXT("layout-survey-nan"),Bad);
    Bad=Before;Bad.CurrentRoom.Objects[0].Position.X=std::numeric_limits<double>::quiet_NaN();Reject(TEXT("object-position-nan"),Bad);
    Bad=Before;Bad.Interaction.RoomInstanceId=10;Reject(TEXT("interaction-room"),Bad);
    Bad=Before;Bad.Interaction.ObjectId=77;Reject(TEXT("interaction-object"),Bad);
    Bad=Before;Bad.Interaction.Kind=EDungeonSceneInteractionKind(255);Reject(TEXT("interaction-kind"),Bad);
    Bad=Before;Bad.Interaction.AtTime=std::numeric_limits<double>::quiet_NaN();Reject(TEXT("interaction-time-nan"),Bad);
    Bad=Before;Bad.Interaction.Pending=false;Reject(TEXT("inactive-confirmation"),Bad);
    FDungeonSceneObjects Empty;TestTrue(TEXT("Uninitialized scene owner roundtrips without starting a room"),Live.Restore(Empty.Capture(),Why));
    TestFalse(TEXT("Empty restore does not generate room objects"),Live.Current().Active);
    return true;
}
#endif
