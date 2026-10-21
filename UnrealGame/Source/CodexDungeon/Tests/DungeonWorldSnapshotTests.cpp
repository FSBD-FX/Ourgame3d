#if WITH_DEV_AUTOMATION_TESTS
#include "Misc/AutomationTest.h"
#include "../DungeonWorldSnapshot.h"
#include "../DungeonFighter.h"
#include "../DungeonGameMode.h"
#include "Components/SceneComponent.h"
#include "Engine/Engine.h"
#include "Engine/GameInstance.h"
#include "Engine/World.h"
#include "GameFramework/PlayerController.h"
#include "GameFramework/PlayerInput.h"
#include "InputCoreTypes.h"
#include "Serialization/BufferArchive.h"
#include <cmath>
#include <limits>

namespace
{
namespace WA=DungeonWeaponActions;
// Independent field-wise proof encoding: never hashes struct padding/pointers.
struct FWorldProof
{
    FBufferArchive Bytes;
    template<class T> void N(T Value){Bytes.Serialize(&Value,sizeof(Value));}
    void Origin(const WA::FOrigin& O){N(O.X);N(O.Y);N(O.Height);}
    void Point(FVector2D P){N(P.X);N(P.Y);}
    void Key(const FDungeonWorldWeaponKey& K){N(K.OwnerId);N(K.ActionId);N(K.EventId);N(K.SubhitId);N(K.RoomInstanceId);}
    void Action(const WA::FAction& A)
    {
        N(A.Type);N(A.Phase);N(A.Weapon);N(A.InstanceId);N(A.ActionId);N(A.Active);N(A.Locked);N(A.StartedAirborne);
        N(A.ForwardStepIssued);N(A.NextSubhit);N(A.Critical);N(A.Terminal);
        for(double V:{A.Facing,A.Start,A.LockAt,A.ActiveAt,A.ActiveEnd,A.End,A.SpeedPct,A.DamagePct,A.StaggerPct,
            A.ReachPct,A.CritMultiplier,A.AmmoCost,A.FocusCost,A.CooldownDuration,A.ReloadSpeedPct,A.FocusCostPct,A.SkillCooldownPct})N(V);
    }
    void Source(const WA::FEvent& E)
    {
        N(E.EventId);N(E.ActionId);N(E.InstanceId);N(E.SubhitId);N(E.Kind);N(E.MaxTargets);N(E.Shape);N(E.OriginPolicy);
        for(double V:{E.AtTime,E.WindowEnd,E.Damage,E.Stagger,E.MinRange,E.Range,E.Depth,E.ProjectileSpeed,E.SecondTargetRatio,
            E.BurnDps,E.BurnDuration,E.ForwardStep,E.AmmoConsumed,E.FocusConsumed})N(V);
        Origin(E.Origin);Action(E.Action);
    }
    void Pose(const DungeonWeaponPoseSocket::FResolved& P)
    {
        N(P.Supported);N(P.CustomOverride);N(P.GroundPoseFallback);N(P.Clip);N(P.Frame);N(P.WeaponStateIndex);N(P.InstanceId);N(P.ActionId);
        for(double V:{P.SampleTime,P.Facing,P.RootX,P.RootY,P.BodySize,P.GripX,P.GripY,P.SupportX,P.SupportY,
            P.ComponentSupportX,P.ComponentSupportY,P.ComponentEmitX,P.ComponentEmitY,P.ComponentGripX,P.ComponentGripY,
            P.EmitX,P.EmitY,P.Angle,P.Scale})N(V);
        Origin(P.ActorOrigin);Origin(P.CombatOrigin);Origin(P.PresentationOrigin);
    }
    explicit FWorldProof(const FDungeonWeaponWorldState& S)
    {
        N(S.RunGuid.A);N(S.RunGuid.B);N(S.RunGuid.C);N(S.RunGuid.D);N(S.RoomInstanceId);N(S.Time);N(S.NextEntityId);N(S.NextEventSequence);
        N(S.ActorBindings.Num());for(const auto& B:S.ActorBindings){N(B.EntityId);N(B.RoomInstanceId);FString Text=B.ContentId;Bytes<<Text;}
        N(S.Projectiles.Num());for(const auto& P:S.Projectiles){Key(P.Key);Source(P.Source);Point(P.Position);N(P.Traveled);N(P.Active);N(P.Stop);
            N(P.HasPoseSocket);Pose(P.PoseSocket);Origin(P.RangeAnchor);N(P.UsesActorRangeAnchor);N(P.LaunchForwardDistance);N(P.LaunchClearancePending);N(P.LaunchObstructed);}
        N(S.Windows.Num());for(const auto& W:S.Windows){Key(W.Key);Source(W.Source);N(W.Active);}
        N(S.HitReceipts.Num());for(const auto& H:S.HitReceipts){Key(H.Key);N(H.TargetId);N(H.AtTime);N(H.Damage);N(H.Stagger);N(H.Magic);
            N(H.HasPoseSocket);Pose(H.PoseSocket);Origin(H.RangeAnchor);N(H.LaunchObstructed);}
        N(S.Burns.Num());for(const auto& B:S.Burns){Key(B.Key);N(B.TargetId);N(B.Dps);N(B.AppliedAt);N(B.ExpiresAt);N(B.NextTickAt);N(B.Active);}
        N(S.Events.Num());for(const auto& E:S.Events){N(E.Sequence);N(E.Kind);Key(E.Key);N(E.TargetId);N(E.AtTime);Point(E.Position);
            N(E.Height);N(E.Damage);N(E.Stagger);N(E.ActualHPLoss);N(E.Magic);N(E.HasPoseSocket);Pose(E.PoseSocket);Origin(E.RangeAnchor);N(E.LaunchObstructed);}
    }
};
bool SameWorld(const FDungeonWeaponWorldState& A,const FDungeonWeaponWorldState& B){return FWorldProof(A).Bytes==FWorldProof(B).Bytes;}

struct FWorldSnapshotFixture
{
    FAutomationTestBase* Test;
    UWorld* World=nullptr;ADungeonGameMode* Game=nullptr;ADungeonFighter* Player=nullptr;APlayerController* Controller=nullptr;
    explicit FWorldSnapshotFixture(FAutomationTestBase* T):Test(T){}
    ~FWorldSnapshotFixture(){if(World){World->DestroyWorld(false);if(GEngine)GEngine->DestroyWorldContext(World);}}
    bool Create(const char* Content="WPN-XBW-001",bool Custom=false,bool Scene=false)
    {
        if(!GEngine)return false;
        const auto Settings=UWorld::InitializationValues().AllowAudioPlayback(false).CreatePhysicsScene(true).RequiresHitProxies(false)
            .CreateNavigation(false).CreateAISystem(false).ShouldSimulatePhysics(false).SetTransactional(false);
        World=UWorld::CreateWorld(EWorldType::Game,false,NAME_None,nullptr,true,ERHIFeatureLevel::Num,&Settings);
        if(!World)return false;GEngine->CreateNewWorldContext(EWorldType::Game).SetCurrentWorld(World);
        World->SetGameInstance(NewObject<UGameInstance>(GEngine));FURL URL;URL.AddOption(TEXT("game=/Script/CodexDungeon.DungeonGameMode"));
        if(!World->SetGameMode(URL))return false;Game=World->GetAuthGameMode<ADungeonGameMode>();
        Player=World->SpawnActor<ADungeonFighter>();Controller=World->SpawnActor<APlayerController>();if(!Game||!Player||!Controller)return false;
        Player->SetActorTickEnabled(false);Player->ResetFighter({0,0});Game->PlayerFighter=Player;Game->bWaitingForStart=false;
        World->AddController(Controller);Controller->Possess(Player);if(!Controller->PlayerInput)Controller->PlayerInput=NewObject<UPlayerInput>(Controller);
        if(Scene)
        {
            if(!Game->BeginSceneExplorationPreview()||Game->Enemies.Num()!=1||Game->GetSimulationTime()!=0.)return false;
            Game->Enemies[0]->bAIEnabled=false; // Explicit initial fixture; later death/clear use normal input.
            return Pulse(EKeys::Enter)&&!Game->bWaitingForStart;
        }
        if(!Game->BeginEquipmentRun(EDungeonEquipmentRunConfig::IntegrationPreview,1))return false;
        DungeonEquipmentInventory::FItem Item;Item.ContentId=Content;if(Item.ContentId=="WPN-XBW-001")Item.Ammo=1;
        const auto Registered=Game->RegisterEquipmentSource(TEXT("qa.world-snapshot.weapon"),Item,{40,0});
        if(!Registered.Ok()||!Pulse(EKeys::E)||!Game->GetEquipmentView().Action.Active||!Advance(Game->GetEquipmentView().Action.Deadline))return false;
        if(Player->WeaponId!=UTF8_TO_TCHAR(Content))return false;
        if(Custom)Player->GetWeaponMuzzleComponent()->SetRelativeLocation({24,7,0});
        return true;
    }
    void Frame(float Dt){Game->Tick(Dt);Controller->PlayerInput->Tick(Dt);TArray<UInputComponent*> Stack;Controller->PlayerInput->ProcessInputStack(Stack,Dt,false);}
    bool Key(FKey K,bool Down){Controller->InputKey(FInputKeyParams(K,Down?IE_Pressed:IE_Released,Down?1.:0.));Controller->PlayerInput->Tick(.005f);
        TArray<UInputComponent*> Stack;Controller->PlayerInput->ProcessInputStack(Stack,.005f,false);return Controller->IsInputKeyDown(K)==Down;}
    bool Pulse(FKey K){if(!Key(K,true))return false;Frame(.005f);if(!Key(K,false))return false;Frame(.005f);return true;}
    bool Advance(double At)
    {
        if(At<Game->GetSimulationTime())return false;
        for(int32 I=0;I<64&&Game->GetSimulationTime()<At;++I){const double Before=Game->GetSimulationTime(),Remaining=At-Before;
            float Dt=float(Remaining);if(double(Dt)>Remaining)Dt=std::nextafter(Dt,0.f);if(!(Dt>0))return false;Frame(Dt);if(Game->GetSimulationTime()<=Before)return false;}
        return Game->GetSimulationTime()==At;
    }
    bool MoveX(double Target)
    {
        for(int32 I=0;I<1600;++I)
        {
            const double Delta=Target-Player->GetGroundPosition().X;
            if(FMath::Abs(Delta)<.002){Frame(.005f);return true;}
            const FKey Direction=Delta>0.?EKeys::D:EKeys::A;
            if(!Key(Direction,true))return false;
            Frame(float(FMath::Min(.02,FMath::Abs(Delta)/double(Player->GetMoveSpeed()))));
            if(!Key(Direction,false)||Game->bGameOver)return false;
        }
        Test->AddError(TEXT("Normal scene movement failed to reach world snapshot waypoint"));return false;
    }
    ADungeonFighter* Target(FVector2D At)
    {
        auto T=World->SpawnActor<ADungeonFighter>();if(!T)return nullptr;T->SetActorTickEnabled(false);T->bEnemy=true;T->bAIEnabled=false;
        T->MaxHealth=1000;T->ResetFighter(At);Game->Enemies.Add(T);return T;
    }
    const FDungeonWeaponWorldState& State()const{return Game->GetWeaponWorldState();}
    FDungeonWeaponWorldRestoreContext Context()const
    {const auto& E=Game->GetEquipmentView();return {E.RunGuid,E.RoomInstanceId,E.OwnerId,Game->GetSimulationTime(),&Player->GetWeaponActionsState()};}
};
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDungeonWorldSnapshotFlight,
    "CodexDungeon.Content.WorldOwnerSnapshot.LiveFlightFrozenSocketsAndDeepValues",EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FDungeonWorldSnapshotFlight::RunTest(const FString&)
{
    for(bool Custom:{false,true})
    {
        FWorldSnapshotFixture F(this);if(!TestTrue(TEXT("Real bound pickup/controller fixture"),F.Create("WPN-XBW-001",Custom)))return false;
        if(!F.Pulse(EKeys::J))return false;const auto A=F.Player->GetWeaponSkillAction();
        if(!TestTrue(TEXT("Real accepted emission endpoint"),A.Active&&F.Advance(A.ActiveAt+.08)))return false;
        if(!TestTrue(TEXT("Actual live projectile with original ammo spend"),F.State().Projectiles.Num()==1&&F.State().Projectiles[0].Active
            &&F.Player->GetWeaponActionsState().Instances.back().Ammo==0))return false;
        const auto Original=F.State();const auto Saved=DungeonWorldSnapshot::Capture(F.State());
        TestTrue(TEXT("Capture includes every world owner field"),SameWorld(Saved.State,Original));
        FDungeonWeaponWorldState Out;Out.NextEventSequence=71001;FString Why;
        if(!TestTrue(TEXT("Independent world value accepts actual live candidate"),DungeonWorldSnapshot::Restore(Saved,F.Context(),Out,Why)))return false;
        TestTrue(TEXT("Frozen sockets, original emission, range origin, cursors and histories roundtrip exactly"),SameWorld(Out,Original));
        const auto Before=DungeonWorldProjectiles::PositionAt(Original.Projectiles[0],Original.Time+.03);
        const auto After=DungeonWorldProjectiles::PositionAt(Out.Projectiles[0],Out.Time+.03);
        TestTrue(TEXT("Next ballistic query has identical original origin/time"),Before.X==After.X&&Before.Y==After.Y);
        // Independent review counterexample: a live projectile cannot be reclassified as Range before its intrinsic deadline.
        auto Early=Saved;auto& EarlyP=Early.State.Projectiles[0];EarlyP.Active=false;EarlyP.Stop=EDungeonWorldProjectileStop::Range;
        FDungeonWorldWeaponEvent Stop;Stop.Sequence=Early.State.NextEventSequence++;Stop.Kind=EDungeonWorldWeaponEventKind::ProjectileStopped;
        Stop.Key=EarlyP.Key;Stop.AtTime=Early.State.Time;Stop.Position=EarlyP.Position;Stop.Height=EarlyP.Source.Origin.Height;
        Stop.HasPoseSocket=EarlyP.HasPoseSocket;Stop.PoseSocket=EarlyP.PoseSocket;Stop.RangeAnchor=EarlyP.RangeAnchor;
        Early.State.Events.Add(Stop);auto EarlyOut=Original;FString EarlyWhy;
        TestFalse(TEXT("Counterexample: early Range stop cannot erase an actual in-flight obligation"),DungeonWorldSnapshot::Restore(Early,F.Context(),EarlyOut,EarlyWhy));
        TestTrue(TEXT("Rejected early stop leaves complete output unchanged"),SameWorld(EarlyOut,Original));
        if(!F.Advance(A.ActiveAt+.14))return false;
        TestTrue(TEXT("Later live world tick cannot change captured/installed value arrays"),SameWorld(Saved.State,Original)&&SameWorld(Out,Original));
        Out.Projectiles[0].Position.X+=9.;TestTrue(TEXT("Candidate arrays do not alias original snapshot/live state"),Saved.State.Projectiles[0].Position.X==Original.Projectiles[0].Position.X);
        const auto& OriginalP=Original.Projectiles[0];const double RangeDeadline=OriginalP.Source.AtTime
            +FMath::Max(0.,OriginalP.Source.Range-OriginalP.LaunchForwardDistance)/OriginalP.Source.ProjectileSpeed;
        if(!F.Advance(RangeDeadline))return false;FDungeonWeaponWorldState RangeOut;FString RangeWhy;
        TestTrue(TEXT("Actual intrinsic range endpoint remains a valid stopped world value"),!F.State().Projectiles[0].Active
            &&F.State().Projectiles[0].Stop==EDungeonWorldProjectileStop::Range&&DungeonWorldSnapshot::Restore(
                DungeonWorldSnapshot::Capture(F.State()),F.Context(),RangeOut,RangeWhy)&&SameWorld(RangeOut,F.State()));
    }
    // The real damage batch consumes a hit before checking the positive HP delta.
    // A finite large float HP demonstrates a spent receipt without a damage fact.
    FWorldSnapshotFixture NoLoss(this);if(!NoLoss.Create())return false;auto Target=NoLoss.Target({180,0});if(!Target)return false;
    Target->MaxHealth=Target->Health=1.e30f;if(!NoLoss.Pulse(EKeys::J))return false;const auto Action=NoLoss.Player->GetWeaponSkillAction();
    if(!NoLoss.Advance(Action.ActiveAt+.16))return false;bool PositiveFact=false;
    for(const auto& E:NoLoss.State().Events)PositiveFact|=E.Kind==EDungeonWorldWeaponEventKind::DirectHitCommitted;
    if(!TestTrue(TEXT("Actual spent receipt can have zero representable HP loss and no positive-loss journal"),NoLoss.State().HitReceipts.Num()==1
        &&Target->Health==1.e30f&&!PositiveFact))return false;
    FDungeonWeaponWorldState NoLossOut;FString NoLossWhy;
    TestTrue(TEXT("Zero-loss consumed hit remains a legitimate complete world value"),DungeonWorldSnapshot::Restore(
        DungeonWorldSnapshot::Capture(NoLoss.State()),NoLoss.Context(),NoLossOut,NoLossWhy)&&SameWorld(NoLossOut,NoLoss.State()));
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDungeonWorldSnapshotBurn,
    "CodexDungeon.Content.WorldOwnerSnapshot.BurnTickPhaseReceiptsAndStoppedHistory",EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FDungeonWorldSnapshotBurn::RunTest(const FString&)
{
    FWorldSnapshotFixture F(this);if(!F.Create("WPN-STF-001"))return false;auto Target=F.Target({160,0});if(!Target||!F.Pulse(EKeys::K))return false;
    const auto A=F.Player->GetWeaponSkillAction();if(!TestTrue(TEXT("Real fireline emission and positive loss"),A.Active&&F.Advance(A.ActiveAt+.05)
        &&F.State().Windows.Num()==1&&F.State().HitReceipts.Num()==1&&F.State().Burns.Num()==1&&F.State().Burns[0].Active&&Target->Health<1000))return false;
    const double FirstTick=F.State().Burns[0].NextTickAt;
    if(!F.Advance(FirstTick+.125))return false;
    const auto Original=F.State();const auto Saved=DungeonWorldSnapshot::Capture(Original);FDungeonWeaponWorldState Out;FString Why;
    TestTrue(TEXT("Complete burn/window/receipt/event arrays captured"),SameWorld(Saved.State,Original));
    if(!TestTrue(TEXT("Actual post-tick world value accepted"),DungeonWorldSnapshot::Restore(Saved,F.Context(),Out,Why)))return false;
    TestTrue(TEXT("Consumed hit and exact next tick/expiry phase preserved, never reapplied"),SameWorld(Out,Original)
        &&Out.Burns[0].NextTickAt==FirstTick+1&&Out.HitReceipts.Num()==1&&!Out.Windows[0].Active);
    const auto RejectBurnHistory=[&](const TCHAR* Label,TFunctionRef<void(FDungeonWeaponWorldSnapshot&)> Mutate)
    {auto Bad=Saved;Mutate(Bad);auto Candidate=Original;FString Reason;
        TestFalse(FString(Label)+TEXT(" rejected"),DungeonWorldSnapshot::Restore(Bad,F.Context(),Candidate,Reason));
        TestTrue(FString(Label)+TEXT(" output unchanged"),SameWorld(Candidate,Original));};
    RejectBurnHistory(TEXT("Counterexample: entire world attack history cannot disappear while WA issued remains"),[](auto& S){
        S.State.Projectiles.Reset();S.State.Windows.Reset();S.State.HitReceipts.Reset();S.State.Burns.Reset();S.State.Events.Reset();S.State.NextEventSequence=1;});
    RejectBurnHistory(TEXT("Counterexample: burn requires its actual application journal"),[](auto& S){
        S.State.Events.RemoveAll([](const auto& E){return E.Kind==EDungeonWorldWeaponEventKind::BurnApplied;});
        uint64 Sequence=1;for(auto& E:S.State.Events)E.Sequence=Sequence++;S.State.NextEventSequence=Sequence;});
    RejectBurnHistory(TEXT("Counterexample: burn tick cannot move off inherited phase"),[](auto& S){
        for(auto& E:S.State.Events)if(E.Kind==EDungeonWorldWeaponEventKind::BurnTickCommitted){E.AtTime=std::nextafter(E.AtTime,S.State.Time);break;}});
    auto Shifted=Saved;Shifted.State.Burns[0].NextTickAt=std::nextafter(Shifted.State.Burns[0].NextTickAt,Shifted.State.Burns[0].ExpiresAt);
    auto ShiftedOut=Original;FString ShiftedWhy;
    TestFalse(TEXT("Counterexample: burn next tick cannot drift from the actual applied/tick journal"),DungeonWorldSnapshot::Restore(Shifted,F.Context(),ShiftedOut,ShiftedWhy));
    TestTrue(TEXT("Rejected burn phase leaves complete output unchanged"),SameWorld(ShiftedOut,Original));
    if(F.Game->GetSimulationTime()<A.End&&!F.Advance(A.End))return false;
    DungeonEquipmentInventory::FItem SecondStaff;SecondStaff.ContentId="WPN-STF-001";
    const auto Source=F.Game->RegisterEquipmentSource(TEXT("qa.world-snapshot.second-staff"),SecondStaff,F.Player->GetGroundPosition()+FVector2D(40,0));
    if(!Source.Ok()||!F.Game->SelectEquipmentSource(Source.SourceId))return false;
    F.Game->TryInteractEquipment();if(!F.Game->GetEquipmentView().NeedsSlotSelection||!F.Game->ConfirmEquipmentSlot(0)
        ||!F.Advance(F.Game->GetEquipmentView().Action.Deadline)||!F.Game->TrySwitchEquipment()
        ||!F.Advance(F.Game->GetEquipmentView().Action.Deadline)||!F.Pulse(EKeys::K))return false;
    const auto Second=F.Player->GetWeaponSkillAction();if(!Second.Active||!F.Advance(std::nextafter(Second.ActiveAt,Second.Start)))return false;
    const double PhaseBeforeRefresh=F.State().Burns[0].NextTickAt;
    if(!F.Advance(Second.ActiveAt))return false;
    const double ExpectedNext=PhaseBeforeRefresh<=Second.ActiveAt?PhaseBeforeRefresh+1.:PhaseBeforeRefresh;
    bool Refreshed=false;for(const auto& E:F.State().Events)Refreshed|=E.Kind==EDungeonWorldWeaponEventKind::BurnRefreshed;
    if(!TestTrue(TEXT("Actual equal refresh preserves old tick phase with new source/application"),Refreshed&&F.State().Burns.Num()==1
        &&F.State().Burns[0].AppliedAt==Second.ActiveAt&&F.State().Burns[0].NextTickAt==ExpectedNext
        &&F.State().Burns[0].NextTickAt!=Second.ActiveAt+1.))return false;
    FDungeonWeaponWorldState RefreshedOut;
    TestTrue(TEXT("Refreshed status with inherited phase roundtrips exactly"),DungeonWorldSnapshot::Restore(
        DungeonWorldSnapshot::Capture(F.State()),F.Context(),RefreshedOut,Why)&&SameWorld(RefreshedOut,F.State()));
    if(!F.Advance(F.State().Burns[0].ExpiresAt))return false;
    const auto End=DungeonWorldSnapshot::Capture(F.State());FDungeonWeaponWorldState EndOut;
    if(!TestTrue(TEXT("Inactive expired burns and consumed window history remain restorable"),DungeonWorldSnapshot::Restore(End,F.Context(),EndOut,Why)))return false;
    TestTrue(TEXT("Expired history retains every exact field and cursor"),!EndOut.Burns[0].Active&&SameWorld(EndOut,F.State())&&SameWorld(Out,Original));
    // A large but finite initial HP permits the initial 18 damage to commit,
    // while intrinsic 2-damage burn ticks have zero representable float loss.
    FWorldSnapshotFixture Tickless(this);if(!Tickless.Create("WPN-STF-001"))return false;auto Large=Tickless.Target({160,0});if(!Large)return false;
    Large->MaxHealth=Large->Health=1.e8f;if(!Tickless.Pulse(EKeys::K))return false;const auto TicklessAction=Tickless.Player->GetWeaponSkillAction();
    if(!Tickless.Advance(TicklessAction.ActiveAt+.05)||Tickless.State().Burns.Num()!=1)return false;
    const double TicklessFirst=Tickless.State().Burns[0].NextTickAt;if(!Tickless.Advance(TicklessFirst+.125))return false;
    bool PositiveTick=false;for(const auto& E:Tickless.State().Events)PositiveTick|=E.Kind==EDungeonWorldWeaponEventKind::BurnTickCommitted;
    FDungeonWeaponWorldState TicklessOut;FString TicklessWhy;
    TestTrue(TEXT("Actual zero-loss burn tick advances phase without a positive-loss tick journal"),!PositiveTick&&Large->Health<1.e8f
        &&Tickless.State().Burns[0].Active&&Tickless.State().Burns[0].NextTickAt==TicklessFirst+1.
        &&DungeonWorldSnapshot::Restore(DungeonWorldSnapshot::Capture(Tickless.State()),Tickless.Context(),TicklessOut,TicklessWhy)
        &&SameWorld(TicklessOut,Tickless.State()));
    // A genuinely expired status can later be freshly applied, never refreshed through the gap.
    const double Ready=F.Player->GetWeaponActionsState().Instances.back().CooldownDeadline;
    if(F.Game->GetSimulationTime()<Ready&&!F.Advance(Ready))return false;
    if(!F.Pulse(EKeys::K))return false;const auto Late=F.Player->GetWeaponSkillAction();
    if(!Late.Active||!F.Advance(Late.ActiveAt+.05))return false;
    const auto LateSaved=DungeonWorldSnapshot::Capture(F.State());FDungeonWeaponWorldState LateOut;FString LateWhy;
    if(!TestTrue(TEXT("Actual fresh application after expiry remains restorable"),DungeonWorldSnapshot::Restore(LateSaved,F.Context(),LateOut,LateWhy)
        &&SameWorld(LateOut,F.State())))return false;
    auto GapRefresh=LateSaved;
    GapRefresh.State.Events.RemoveAll([](const auto& E){return E.Kind==EDungeonWorldWeaponEventKind::BurnExpired;});
    for(auto& E:GapRefresh.State.Events)if(E.Kind==EDungeonWorldWeaponEventKind::BurnApplied&&E.Key.EventId==GapRefresh.State.Burns[0].Key.EventId)
        E.Kind=EDungeonWorldWeaponEventKind::BurnRefreshed;
    uint64 Sequence=1;for(auto& E:GapRefresh.State.Events)E.Sequence=Sequence++;GapRefresh.State.NextEventSequence=Sequence;
    double OldNext=End.State.Burns[0].NextTickAt;while(OldNext<=GapRefresh.State.Time)OldNext+=1.;
    GapRefresh.State.Burns[0].NextTickAt=OldNext;
    TestFalse(TEXT("Counterexample: removed expiry cannot turn later fresh application into an inherited-phase refresh"),
        DungeonWorldSnapshot::Restore(GapRefresh,F.Context(),LateOut,LateWhy));
    TestTrue(TEXT("Rejected refresh through expired gap leaves complete output unchanged"),SameWorld(LateOut,LateSaved.State));
    // The actual free exit retains old room emissions, consumed hits and binding tombstones.
    FWorldSnapshotFixture Exit(this);if(!Exit.Create("WPN-SWD-001",false,true)||!Exit.MoveX(220.))return false;
    const auto OldRoom=Exit.Game->GetEquipmentView().RoomInstanceId;const auto Run=Exit.Game->GetEquipmentView().RunGuid;
    const uint64 OldKnight=Exit.Game->Enemies[0]->GetRuntimeEntityId();
    DungeonEquipmentInventory::FItem Staff;Staff.ContentId="WPN-STF-001";
    const auto StaffSource=Exit.Game->RegisterEquipmentSource(TEXT("qa.world-snapshot.exit-staff"),Staff,Exit.Player->GetGroundPosition()+FVector2D(40,0));
    if(!StaffSource.Ok()||!Exit.Pulse(EKeys::E)||!Exit.Game->GetEquipmentView().Action.Active
        ||!Exit.Advance(Exit.Game->GetEquipmentView().Action.Deadline)||!Exit.Pulse(EKeys::K))return false;
    const auto Fire=Exit.Player->GetWeaponSkillAction();
    if(!TestTrue(TEXT("Actual old-room fireline creates window, consumed knight hit and burn"),Fire.Active&&Exit.Advance(Fire.ActiveAt+.05)
        &&Exit.State().Windows.Num()==1&&Exit.State().HitReceipts.Num()==1&&Exit.State().Burns.Num()==1))return false;
    if(!Exit.Advance(Fire.End)||!Exit.Pulse(EKeys::Q)||!Exit.Advance(Exit.Game->GetEquipmentView().Action.Deadline))return false;
    for(int32 I=0;I<12&&!Exit.Game->Enemies[0]->bDead;++I)
    {if(!Exit.Pulse(EKeys::J)||!Exit.Advance(Exit.Game->GetSimulationTime()+.8))return false;}
    if(!TestTrue(TEXT("Normal sword attacks actually kill admitted knight and clear room"),Exit.Game->Enemies[0]->bDead
        &&Exit.Game->Enemies[0]->bDeathReported&&Exit.Game->bRoomCleared))return false;
    if(!Exit.MoveX(1180.)||!Exit.Pulse(EKeys::Q)||!Exit.Advance(Exit.Game->GetEquipmentView().Action.Deadline)
        ||!Exit.Key(EKeys::A,true))return false;
    Exit.Frame(.005f);if(!Exit.Key(EKeys::A,false))return false;Exit.Frame(.005f);
    if(!Exit.Pulse(EKeys::J))return false;const auto Shot=Exit.Player->GetWeaponSkillAction();
    if(!TestTrue(TEXT("Real staff shot remains in flight after its action becomes idle"),Shot.Active&&Exit.Advance(Shot.End)
        &&Exit.State().Projectiles.Num()==1&&Exit.State().Projectiles[0].Active))return false;
    if(!Exit.Pulse(EKeys::E))return false;
    if(!TestTrue(TEXT("Fresh exit interaction opens confirmation in old room"),Exit.Game->GetSceneInteractionView().Pending
        &&Exit.Game->GetSceneInteractionView().NeedsConfirmation&&Exit.Game->GetEquipmentView().RoomInstanceId==OldRoom))return false;
    if(!Exit.Pulse(EKeys::Enter))return false;
    const auto& History=Exit.State();bool OldBinding=false,NewBinding=false;
    for(const auto& B:History.ActorBindings){OldBinding|=B.EntityId==OldKnight&&B.RoomInstanceId==OldRoom;
        NewBinding|=B.EntityId==Exit.Game->Enemies[0]->GetRuntimeEntityId()&&B.RoomInstanceId==OldRoom+1;}
    if(!TestTrue(TEXT("Real transfer keeps same Run, old tombstone and consumed histories while new enemy gets new identity"),History.RunGuid==Run
        &&History.RoomInstanceId==OldRoom+1&&OldBinding&&NewBinding&&History.Windows.Num()==1&&History.HitReceipts.Num()==1
        &&History.Burns.Num()==1&&!History.Burns[0].Active&&History.Projectiles.Num()==1&&!History.Projectiles[0].Active
        &&History.Projectiles[0].Stop==EDungeonWorldProjectileStop::RoomExit&&History.Projectiles[0].Key.RoomInstanceId==OldRoom))return false;
    FDungeonWeaponWorldState HistoryOut;FString HistoryWhy;
    TestTrue(FString(TEXT("Actual transferred world history restores exactly: "))+HistoryWhy,DungeonWorldSnapshot::Restore(
        DungeonWorldSnapshot::Capture(History),Exit.Context(),HistoryOut,HistoryWhy)&&SameWorld(HistoryOut,History));
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDungeonWorldSnapshotInvalid,
    "CodexDungeon.Content.WorldOwnerSnapshot.CrossReferenceAndNumericRejectionIsAtomic",EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FDungeonWorldSnapshotInvalid::RunTest(const FString&)
{
    FWorldSnapshotFixture F(this);if(!F.Create())return false;auto T=F.Target({180,0});if(!T||!F.Pulse(EKeys::J))return false;
    const auto A=F.Player->GetWeaponSkillAction();if(!F.Advance(A.ActiveAt+.16)||F.State().HitReceipts.Num()!=1)return false;
    const auto Saved=DungeonWorldSnapshot::Capture(F.State());auto Out=F.State();const auto Original=Out;FString Why;
    if(!TestTrue(TEXT("Actual complete baseline accepted before negative cases"),DungeonWorldSnapshot::Restore(Saved,F.Context(),Out,Why)))return false;
    const auto Reject=[&](const TCHAR* Label,TFunctionRef<void(FDungeonWeaponWorldSnapshot&)> Mutate)
    {Out=Original;auto Bad=Saved;Mutate(Bad);Why.Reset();const bool Accepted=DungeonWorldSnapshot::Restore(Bad,F.Context(),Out,Why);
        TestFalse(FString(Label)+TEXT(" candidate rejected"),Accepted);TestFalse(FString(Label)+TEXT(" diagnostic supplied"),Why.IsEmpty());
        TestTrue(FString(Label)+TEXT(" complete output remains unchanged"),SameWorld(Out,Original));};
    const auto RejectContext=[&](const TCHAR* Label,TFunctionRef<void(FDungeonWeaponWorldRestoreContext&)> Mutate)
    {Out=Original;auto Bad=F.Context();Mutate(Bad);Why.Reset();const bool Accepted=DungeonWorldSnapshot::Restore(Saved,Bad,Out,Why);
        TestFalse(FString(Label)+TEXT(" context rejected"),Accepted);TestFalse(FString(Label)+TEXT(" context diagnostic supplied"),Why.IsEmpty());
        TestTrue(FString(Label)+TEXT(" context leaves complete output unchanged"),SameWorld(Out,Original));};
    RejectContext(TEXT("missing action owner"),[](auto& C){C.PlayerActions=nullptr;});
    RejectContext(TEXT("foreign context owner"),[](auto& C){++C.OwnerId;});
    RejectContext(TEXT("foreign context room"),[](auto& C){++C.RoomInstanceId;});
    RejectContext(TEXT("context time mismatch"),[](auto& C){C.SimulationTime+=.125;});
    RejectContext(TEXT("nonfinite context clock"),[](auto& C){C.SimulationTime=std::numeric_limits<double>::infinity();});
    Reject(TEXT("schema"),[](auto& S){S.Schema=99;});
    Reject(TEXT("Run"),[](auto& S){S.State.RunGuid=FGuid::NewGuid();});
    Reject(TEXT("clock nan"),[](auto& S){S.State.Time=std::numeric_limits<double>::quiet_NaN();});
    Reject(TEXT("entity cursor alias"),[](auto& S){S.State.NextEntityId=S.State.ActorBindings.Last().EntityId;});
    Reject(TEXT("duplicate binding"),[](auto& S){const auto Copy=S.State.ActorBindings.Last();S.State.ActorBindings.Add(Copy);});
    Reject(TEXT("missing target history"),[](auto& S){S.State.ActorBindings.RemoveAt(1);});
    Reject(TEXT("foreign emission"),[](auto& S){S.State.Projectiles[0].Key.EventId+=100;});
    Reject(TEXT("source nan"),[](auto& S){S.State.Projectiles[0].Source.Origin.X=std::numeric_limits<double>::quiet_NaN();});
    Reject(TEXT("negative travel"),[](auto& S){S.State.Projectiles[0].Traveled=-1;});
    Reject(TEXT("position nan"),[](auto& S){S.State.Projectiles[0].Position.Y=std::numeric_limits<double>::quiet_NaN();});
    Reject(TEXT("pose nan"),[](auto& S){S.State.Projectiles[0].PoseSocket.GripX=std::numeric_limits<double>::quiet_NaN();});
    Reject(TEXT("range anchor changed"),[](auto& S){S.State.Projectiles[0].RangeAnchor.X+=1;});
    Reject(TEXT("launch allowance changed"),[](auto& S){S.State.Projectiles[0].LaunchForwardDistance+=1;});
    Reject(TEXT("stopped without reason"),[](auto& S){S.State.Projectiles[0].Stop=EDungeonWorldProjectileStop::None;});
    Reject(TEXT("foreign receipt target"),[](auto& S){S.State.HitReceipts[0].TargetId=99999;});
    Reject(TEXT("duplicate consumed hit"),[](auto& S){const auto Copy=S.State.HitReceipts[0];S.State.HitReceipts.Add(Copy);});
    Reject(TEXT("receipt damage changed"),[](auto& S){S.State.HitReceipts[0].Damage+=1;});
    Reject(TEXT("receipt future"),[](auto& S){S.State.HitReceipts[0].AtTime=S.State.Time+1;});
    Reject(TEXT("duplicate positive-loss direct hit fact"),[](auto& S){
        for(const auto& E:S.State.Events)if(E.Kind==EDungeonWorldWeaponEventKind::DirectHitCommitted)
        {auto Copy=E;Copy.Sequence=S.State.NextEventSequence++;S.State.Events.Add(Copy);break;}});
    Reject(TEXT("journal sequence gap"),[](auto& S){S.State.Events[0].Sequence=2;});
    Reject(TEXT("unknown journal event"),[](auto& S){S.State.Events[0].Kind=EDungeonWorldWeaponEventKind(255);});
    Reject(TEXT("journal position nan"),[](auto& S){S.State.Events[0].Position.X=std::numeric_limits<double>::quiet_NaN();});
    return true;
}
#endif
