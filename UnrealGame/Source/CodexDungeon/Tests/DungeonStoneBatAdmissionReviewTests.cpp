#if WITH_DEV_AUTOMATION_TESTS
#include "Misc/AutomationTest.h"
#include "../DungeonFighter.h"
#include "../DungeonGameMode.h"
#include "../DungeonStoneBatDriver.h"
#include "Components/BoxComponent.h"
#include "Engine/Engine.h"
#include "Engine/GameInstance.h"
#include "Engine/World.h"
#include <cmath>
#include <limits>

namespace
{
namespace BatReview=DungeonStoneBat;
struct FBatReviewWorld
{
    UWorld* World=nullptr;ADungeonGameMode* Game=nullptr;ADungeonFighter* Player=nullptr;ADungeonFighter* Bat=nullptr;
    FAutomationTestBase* Test=nullptr;
    explicit FBatReviewWorld(FAutomationTestBase* InTest):Test(InTest) {}
    ~FBatReviewWorld(){if(World){World->DestroyWorld(false);if(GEngine)GEngine->DestroyWorldContext(World);}}
    bool Fail(const TCHAR* Stage){Test->AddError(FString::Printf(TEXT("StoneBat review fixture failed at %s"),Stage));return false;}
    bool AdvanceTo(double At)
    {
        if(!std::isfinite(At)||At<Game->GetSimulationTime())return false;
        for(int32 I=0;I<32&&Game->GetSimulationTime()<At;++I)
        {
            const double Before=Game->GetSimulationTime(),Remaining=At-Before;float Delta=float(Remaining);
            if(double(Delta)>Remaining)Delta=std::nextafter(Delta,0.f);
            if(!(Delta>0.f))return false;Game->Tick(Delta);
            if(Game->GetSimulationTime()<=Before)return false;
        }
        return Game->GetSimulationTime()==At;
    }
    bool Create(FVector2D BatPosition={60,0},const char* Weapon=nullptr)
    {
        if(!GEngine)return Fail(TEXT("engine"));
        const auto Settings=UWorld::InitializationValues().AllowAudioPlayback(false).CreatePhysicsScene(true)
            .RequiresHitProxies(false).CreateNavigation(false).CreateAISystem(false).ShouldSimulatePhysics(false).SetTransactional(false);
        World=UWorld::CreateWorld(EWorldType::Game,false,NAME_None,nullptr,true,ERHIFeatureLevel::Num,&Settings);
        if(!World)return Fail(TEXT("world"));
        GEngine->CreateNewWorldContext(EWorldType::Game).SetCurrentWorld(World);
        World->SetGameInstance(NewObject<UGameInstance>(GEngine));FURL URL;URL.AddOption(TEXT("game=/Script/CodexDungeon.DungeonGameMode"));
        if(!World->SetGameMode(URL))return Fail(TEXT("authority"));
        Game=World->GetAuthGameMode<ADungeonGameMode>();Player=World->SpawnActor<ADungeonFighter>();
        if(!Game||!Player)return Fail(TEXT("player"));Player->SetActorTickEnabled(false);Player->ResetFighter({0,0});Game->PlayerFighter=Player;
        if(!Game->BeginEquipmentRun(EDungeonEquipmentRunConfig::IntegrationPreview,1))return Fail(TEXT("bound run"));
        if(Weapon)
        {
            DungeonEquipmentInventory::FItem Item;Item.ContentId=Weapon;
            if(Item.ContentId=="WPN-XBW-001")Item.Ammo=1; // Explicitly loaded QA source; pickup never refills it.
            const auto Source=Game->RegisterEquipmentSource(TEXT("qa.bat-review.weapon"),Item,{40,0});
            if(!Source.Ok()||!Game->SelectEquipmentSource(Source.SourceId)||!Game->TryInteractEquipment()
                ||!AdvanceTo(Player->GetEquipmentActionDeadline())
                ||Game->GetEquipmentView().Slots[Game->GetEquipmentView().ActiveSlot].InstanceId!=Source.InstanceId)return Fail(TEXT("real E weapon"));
        }
        Bat=Game->SpawnStoneBat(BatPosition);
        if(!Bat||!Bat->GetStoneBatDriver())return Fail(TEXT("real bat spawn"));
        const auto& S=State();
        if(S.HP!=55||S.Position.Z!=90||S.Phase!=BatReview::EPhase::Dormant||Bat->Health!=55||Bat->JumpHeight!=90
            ||!Bat->GetRuntimeEntityId()||S.EntityId!=Bat->GetRuntimeEntityId()||Bat->IsActorTickEnabled())return Fail(TEXT("authored initial mirror/identity"));
        return true;
    }
    const BatReview::FState& State()const{return Bat->GetStoneBatDriver()->State();}
    int32 Events(BatReview::EEventKind Kind,uint64 Attack=0)const
    {int32 N=0;for(const auto& E:State().Issued)if(E.Kind==Kind&&(!Attack||E.Action.AttackId==Attack))++N;return N;}
    bool FirstAttack()
    {
        const double Limit=Game->GetSimulationTime()+4.;
        for(int32 I=0;I<420&&!State().Action.InProgress&&Game->GetSimulationTime()<Limit;++I)
            if(!AdvanceTo(Game->GetSimulationTime()+.01))return false;
        return State().Action.InProgress&&State().Action.Kind==BatReview::EAttack::Peck;
    }
    AActor* Wall()
    {
        auto A=World->SpawnActor<AActor>();if(!A)return nullptr;auto Box=NewObject<UBoxComponent>(A);
        A->SetRootComponent(Box);Box->SetBoxExtent({5,100,100});Box->SetCollisionEnabled(ECollisionEnabled::QueryOnly);
        Box->SetCollisionObjectType(ECC_WorldStatic);Box->SetCollisionResponseToAllChannels(ECR_Block);Box->RegisterComponent();A->SetActorLocation({100,0,0});return A;
    }
};
bool BatNear(double A,double B,double T=.0002){return std::abs(A-B)<=T;}
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBatReviewDormancy,
    "CodexDungeon.Content.StoneBatAdmissionReview.DormantLOSAndFullWake",EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FBatReviewDormancy::RunTest(const FString& Parameters)
{
    {
        FBatReviewWorld F(this);if(!F.Create({200,0}))return false;auto Wall=F.Wall();if(!TestNotNull(TEXT("Actual registered LOS wall"),Wall))return false;
        F.Player->MoveOnGround({1,0},40.f/F.Player->GetMoveSpeed());
        TestTrue(TEXT("Normal movement enters near ellipse on the player side of the wall"),BatNear(F.Player->GetGroundPosition().X,40));
        F.AdvanceTo(.9);
        TestTrue(TEXT("LOS-blocked near dormant bat emits no wake, attack or damage and still counts for room clear"),
            F.State().Phase==BatReview::EPhase::Dormant&&F.Events(BatReview::EEventKind::WakeStarted)==0
            &&F.State().Actions.empty()&&F.State().HitReceipts.empty()&&F.Player->Health==100&&!F.Game->bRoomCleared);
        Wall->SetActorEnableCollision(false);F.Game->Tick(.001f);
        if(!TestTrue(TEXT("Removing actual obstruction admits a real wake"),F.State().Phase==BatReview::EPhase::Waking))return false;
        const double Wake=F.State().WakeEnd;
        TestTrue(TEXT("Actual .80 warning retains stable same entity"),Wake==F.State().WakeStartedAt+.8&&F.State().EntityId==F.Bat->GetRuntimeEntityId());
        F.AdvanceTo(Wake-.001);TestTrue(TEXT("Warning cannot attack early"),!F.State().Awakened&&F.State().Actions.empty()&&F.Player->Health==100);
        F.AdvanceTo(Wake);TestTrue(TEXT("Exact warning endpoint wakes once without an early attack"),F.State().Awakened&&F.Events(BatReview::EEventKind::WakeCompleted)==1&&F.State().Actions.empty());
    }
    {
        FBatReviewWorld F(this);if(!F.Create({600,0}))return false;
        const double Due=F.State().CombatStartedAt+12.;F.AdvanceTo(Due-.001);
        TestTrue(TEXT("Far admitted bat remains dormant until real12s fallback"),F.State().Phase==BatReview::EPhase::Dormant&&F.State().Actions.empty());
        F.AdvanceTo(Due);TestTrue(TEXT("Real combat fallback starts full warning without HP reset"),
            F.State().Phase==BatReview::EPhase::Waking&&F.State().WakeStartedAt==Due&&F.State().WakeEnd==Due+.8&&F.State().HP==55&&F.State().Actions.empty());
    }
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBatReviewIncomingHeight,
    "CodexDungeon.Content.StoneBatAdmissionReview.ActualHighHeightRejectsGroundAndAcceptsJump",EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FBatReviewIncomingHeight::RunTest(const FString& Parameters)
{
    FBatReviewWorld F(this);if(!F.Create())return false;
    F.Player->BeginAttack();const auto Ground=F.Player->GetMeleeCombatState().Action;
    if(!TestTrue(TEXT("Real bound starter ground SWD begins"),Ground.Active&&!Ground.StartedAirborne))return false;
    F.AdvanceTo(Ground.End);
    TestTrue(TEXT("Full ground window misses actual high90 without imaginary immunity or HP change"),F.Bat->JumpHeight==90&&F.Bat->Health==55&&F.State().HP==55&&F.State().ReceivedHits.empty());
    F.Player->StartJump();F.Player->BeginAttack();const auto Air=F.Player->GetMeleeCombatState().Action;
    if(!TestTrue(TEXT("Actual jump accepts the next airborne sword primary"),Air.Active&&Air.StartedAirborne))return false;
    F.AdvanceTo(Air.ActiveStart);
    const auto& Locked=F.Player->GetMeleeCombatState().Action;
    TestTrue(TEXT("Real ballistic attack height can reach high90 and applies actual armor15"),
        F.Player->JumpHeight>25&&F.Bat->JumpHeight==90&&F.State().ReceivedHits.size()==1
        &&BatNear(55-F.Bat->Health,Locked.Damage/1.15)&&BatNear(F.State().HP,F.Bat->Health)
        &&BatNear(F.Bat->GetArmorRating(),15)&&BatNear(F.Bat->GetArmorRating(true),10));
    const double HP=F.State().HP;F.AdvanceTo(F.State().WakeEnd);
    TestTrue(TEXT("Full wake preserves real damage instead of restoring55"),F.State().Awakened&&F.State().HP==HP&&F.Events(BatReview::EEventKind::Damaged)==1);
    for(int32 Staff=0;Staff<2;++Staff)
    {
        FBatReviewWorld R(this);if(!R.Create({180,0},Staff?"WPN-STF-001":"WPN-XBW-001"))return false;
        const FVector2D Initial=R.Player->GetGroundPosition(),HighPoint=R.Bat->GetGroundPosition();
        R.Player->MoveOnGround({1,0},230.f/R.Player->GetMoveSpeed());
        TestTrue(TEXT("Actual swept ground movement passes beneath high90 without a ground body"),
            R.Bat->JumpHeight==90&&R.State().Position.Z==90&&R.Player->GetGroundPosition().X>HighPoint.X+34.);
        const double Return=R.Player->GetGroundPosition().X-Initial.X;
        if(Return>0)R.Player->MoveOnGround({-1,0},float(Return/R.Player->GetMoveSpeed()));
        R.Player->MoveOnGround({1,0},.001f); // Normal facing input; no direct Facing or muzzle assignment.
        R.Player->StartJump();R.Player->BeginAttack();const auto A=R.Player->GetWeaponActionsState().Action;
        if(!TestTrue(TEXT("Real acquired ranged instance accepts its actual airborne primary"),
            A.Active&&A.StartedAirborne&&A.InstanceId==R.Game->GetEquipmentView().Slots[R.Game->GetEquipmentView().ActiveSlot].InstanceId))return false;
        if(!TestTrue(TEXT("Reach real ranged emission deadline"),R.AdvanceTo(A.ActiveAt)))return false;
        const DungeonWeaponActions::FEvent* Issued=nullptr;
        for(const auto& E:R.Player->GetWeaponActionsState().Issued)if(E.ActionId==A.ActionId)Issued=&E;
        if(!TestNotNull(TEXT("Actual airborne projectile has an authoritative emission receipt"),Issued))return false;
        const auto E=*Issued;const auto Muzzle=R.Player->GetWeaponMuzzleOrigin();
        bool MouthBinding=BatNear(E.Origin.X,Muzzle.X,1.e-7)&&BatNear(E.Origin.Y,Muzzle.Y,1.e-7);
        if(!Staff)
        {
            // The actual shot changes this instance from neutral-loaded to
            // empty0. Compare the emission to its frozen pre-spend mouth;
            // the current physical getter must remain the current empty mouth.
            const auto* Emission=R.Player->FindWeaponEmissionPoseSocket(A.ActionId,E.SubhitId);
            const auto Current=R.Player->GetWeaponPoseSocket();
            constexpr double Angle=-5.*3.14159265358979323846/180.;
            const double NativeX=(224.+.48*(361.*std::cos(Angle)+29.*std::sin(Angle))-256.)*120./512./.65;
            const auto ActorXY=R.Player->GetGroundPosition();
            MouthBinding=Emission&&Emission->WeaponStateIndex==-1&&Emission->GroundPoseFallback
                &&Emission->SampleTime==E.AtTime&&Emission->InstanceId==A.InstanceId
                &&BatNear(E.Origin.X,ActorXY.X+E.Action.Facing*NativeX,1.e-7)
                &&BatNear(E.Origin.Y,ActorXY.Y,1.e-7)
                &&BatNear(E.Origin.X,Emission->CombatOrigin.X,1.e-7)
                &&BatNear(E.Origin.Y,Emission->CombatOrigin.Y,1.e-7)
                &&BatNear(E.Origin.Height,Emission->CombatOrigin.Height,.0001)
                &&Current.WeaponStateIndex==0&&Current.GroundPoseFallback
                &&BatNear(Muzzle.X,Current.CombatOrigin.X,1.e-7)&&BatNear(Muzzle.Y,Current.CombatOrigin.Y,1.e-7);
        }
        TestTrue(TEXT("Actual emitted jump plane and immutable per-shot mouth are legal for high90, without fake origin or down aim"),
            E.Origin.Height>25&&std::abs(E.Origin.Height-90)<=65&&BatNear(E.Origin.Height,Muzzle.Height,.0001)&&MouthBinding);
        const double Contact=E.AtTime+(HighPoint.X-16.-E.Origin.X)/E.ProjectileSpeed;
        R.AdvanceTo(A.Start+.65);
        const FDungeonWorldWeaponEvent* Hit=nullptr;int32 Emissions=0,Hits=0;
        for(const auto& Fact:R.Game->GetWeaponWorldState().Events)if(Fact.Key.ActionId==A.ActionId)
        {
            if(Fact.Kind==EDungeonWorldWeaponEventKind::ProjectileEmitted)++Emissions;
            if(Fact.Kind==EDungeonWorldWeaponEventKind::DirectHitCommitted&&Fact.TargetId==R.Bat->GetRuntimeEntityId()){Hit=&Fact;++Hits;}
        }
        const double Expected=E.Damage*100./(100.+(Staff?10.:15.));
        AddInfo(FString::Printf(TEXT("Air %s high bat: emitted=%.17g height=%.9g originX=%.9g expectedContact16=%.17g hit=%.17g hp=%.9g received=%d"),
            Staff?TEXT("STF"):TEXT("XBW"),E.AtTime,E.Origin.Height,E.Origin.X,Contact,Hit?Hit->AtTime:-1.,double(R.Bat->Health),int32(R.State().ReceivedHits.size())));
        TestTrue(TEXT("Nonblocking high flight still exposes an independent16x12 hurtbox to a legal-height real projectile"),
            R.Bat->JumpHeight==90&&R.Bat->GetGroundPosition()==HighPoint&&Emissions==1&&Hits==1&&Hit
            &&Hit->Magic==bool(Staff)&&BatNear(Hit->AtTime,Contact,1.e-7)&&BatNear(Hit->Height,E.Origin.Height,1.e-7)
            &&BatNear(Hit->ActualHPLoss,Expected)&&BatNear(55-R.Bat->Health,Expected)&&BatNear(R.State().HP,R.Bat->Health)
            &&R.State().ReceivedHits.size()==1&&BatNear(R.State().ReceivedHits[0].HPLoss,Expected));
    }
    for(int32 Staff=0;Staff<2;++Staff)
    {
        FBatReviewWorld R(this);if(!R.Create({180,0},Staff?"WPN-STF-001":"WPN-XBW-001"))return false;
        auto GroundTarget=R.World->SpawnActor<ADungeonFighter>();if(!TestNotNull(TEXT("Real rear ground target"),GroundTarget))return false;
        GroundTarget->bEnemy=true;GroundTarget->bAIEnabled=false;GroundTarget->MaxHealth=100.f;
        GroundTarget->ResetFighter({300,0});GroundTarget->SetActorTickEnabled(false);R.Game->Enemies.Add(GroundTarget);
        R.Game->Tick(.001f); // Normal Run admission allocates the rear target's identity.
        if(!TestTrue(TEXT("Rear ground actor is admitted after the actual high bat with distinct stable IDs"),
            GroundTarget->GetRuntimeEntityId()!=0&&GroundTarget->GetRuntimeEntityId()!=R.Bat->GetRuntimeEntityId()
            &&GroundTarget->JumpHeight==0&&R.Bat->GetCombatHeight()==90))return false;
        R.Player->BeginAttack();const auto A=R.Player->GetWeaponActionsState().Action;
        if(!TestTrue(TEXT("Real acquired ranged instance accepts its ground primary"),A.Active&&!A.StartedAirborne
            &&A.InstanceId==R.Game->GetEquipmentView().Slots[R.Game->GetEquipmentView().ActiveSlot].InstanceId))return false;
        if(!TestTrue(TEXT("Reach actual ground projectile emission"),R.AdvanceTo(A.ActiveAt)))return false;
        const DungeonWeaponActions::FEvent* Issued=nullptr;
        for(const auto& E:R.Player->GetWeaponActionsState().Issued)if(E.ActionId==A.ActionId)Issued=&E;
        if(!TestNotNull(TEXT("Ground primary has an actual emission receipt"),Issued))return false;
        const auto E=*Issued;const auto Muzzle=R.Player->GetWeaponMuzzleOrigin();
        if(!TestTrue(TEXT("Actual ground emission remains below high bat's independent hurt height"),E.Origin.Height==0
            &&Muzzle.Height==0&&std::abs(R.Bat->GetCombatHeight()-E.Origin.Height)>65))return false;
        const double Contact=E.AtTime+(GroundTarget->GetGroundPosition().X-18.-E.Origin.X)/E.ProjectileSpeed;
        if(!TestTrue(TEXT("Reach rear ground contact before actual high bat finishes wake"),R.AdvanceTo(A.Start+.75)))return false;
        int32 Emissions=0,GroundHits=0,BatHits=0;const FDungeonWorldWeaponEvent* Hit=nullptr;
        for(const auto& Fact:R.Game->GetWeaponWorldState().Events)if(Fact.Key.ActionId==A.ActionId)
        {
            if(Fact.Kind==EDungeonWorldWeaponEventKind::ProjectileEmitted)++Emissions;
            if(Fact.Kind==EDungeonWorldWeaponEventKind::DirectHitCommitted)
            {if(Fact.TargetId==GroundTarget->GetRuntimeEntityId()){++GroundHits;Hit=&Fact;}
                if(Fact.TargetId==R.Bat->GetRuntimeEntityId())++BatHits;}
        }
        const double Rating=GroundTarget->GetArmorRating(bool(Staff));
        const double Expected=E.Damage*(1.-FMath::Min(.6,Rating/(100.+Rating)));
        AddInfo(FString::Printf(TEXT("Ground %s beneath bat: emissionHeight=%.9g batHeight=%.9g groundID=%llu expectedContact=%.17g hit=%.17g groundHP=%.9g batHP=%.9g"),
            Staff?TEXT("STF"):TEXT("XBW"),E.Origin.Height,R.Bat->GetCombatHeight(),GroundTarget->GetRuntimeEntityId(),Contact,Hit?Hit->AtTime:-1.,double(GroundTarget->Health),double(R.Bat->Health)));
        TestTrue(TEXT("Height-disjoint real high bat cannot stop a ground projectile from hitting the rear ground actor once"),
            R.State().Position.Z==90&&R.Bat->GetCombatHeight()==90&&R.State().HP==55&&R.State().ReceivedHits.empty()&&BatHits==0
            &&Emissions==1&&GroundHits==1&&Hit&&Hit->Magic==bool(Staff)&&BatNear(Hit->AtTime,Contact,1.e-7)
            &&Hit->Height==0&&BatNear(Hit->ActualHPLoss,Expected)&&BatNear(100.-GroundTarget->Health,Expected));
    }
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBatReviewOutgoingHeight,
    "CodexDungeon.Content.StoneBatAdmissionReview.PeckActualZ65BoundaryAndSingleContact",EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FBatReviewOutgoingHeight::RunTest(const FString& Parameters)
{
    FBatReviewWorld F(this);if(!F.Create())return false;
    if(!TestTrue(TEXT("Normal central AI starts its first real Peck"),F.FirstAttack()))return false;
    const auto A=F.State().Action;const double Z65=A.ActiveAt+(A.ActiveEnd-A.ActiveAt)*(90.-65.)/70.;
    F.AdvanceTo(A.ActiveAt);TestTrue(TEXT("Peck active opens high90 and cannot damage ground yet"),F.Bat->JumpHeight==90&&F.Player->Health==100&&F.State().HitReceipts.empty());
    if(!TestTrue(TEXT("Reach preceding representable real height boundary"),F.AdvanceTo(std::nextafter(Z65,-std::numeric_limits<double>::infinity()))))return false;
    TestTrue(TEXT("No tolerance band grants ground damage before actual65"),F.State().Position.Z>65&&F.Player->Health==100&&F.State().HitReceipts.empty());
    F.AdvanceTo(Z65);
    TestTrue(TEXT("Exact actual65 admits raw12/10 once through central damage"),F.State().Position.Z==65&&F.Player->Health==88
        &&F.State().HitReceipts.size()==1&&F.State().HitReceipts[0].AtTime==Z65&&F.State().HitReceipts[0].TargetId==F.Player->GetRuntimeEntityId());
    F.AdvanceTo(A.ActiveEnd+.1);
    TestTrue(TEXT("Continuing the same active path cannot duplicate target receipt or actual HP loss"),F.Player->Health==88
        &&F.Events(BatReview::EEventKind::Hit,A.AttackId)==1&&F.State().HitReceipts.size()==1&&A.Damage==12&&A.Stagger==10);
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBatReviewFullRecovery,
    "CodexDungeon.Content.StoneBatAdmissionReview.FullAnchoredLowRecoveryAndRealWingHeight",EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FBatReviewFullRecovery::RunTest(const FString& Parameters)
{
    FBatReviewWorld F(this);if(!F.Create()||!TestTrue(TEXT("Central first Peck accepted"),F.FirstAttack()))return false;
    const auto A=F.State().Action;F.AdvanceTo(A.ActiveEnd);
    if(!TestTrue(TEXT("Real Peck finishes active at legal20 and starts fresh1.80 low clock"),F.State().Position.Z==20
        &&F.State().Phase==BatReview::EPhase::LowRecovery&&F.State().LowStartedAt==A.ActiveEnd&&F.State().LowReadyAt==A.ActiveEnd+1.8))return false;
    const auto Anchor=F.Bat->GetGroundPosition();const double LowEnd=F.State().LowReadyAt;
    F.AdvanceTo(LowEnd-.2);F.Player->MoveOnGround({0,1},.1f);F.AdvanceTo(LowEnd-.001);
    TestTrue(TEXT("Moving real player never shortens or drags full low anchor"),F.State().PendingLow&&F.Bat->JumpHeight==20
        &&F.Bat->GetGroundPosition()==Anchor&&F.State().Actions.size()==1);
    F.AdvanceTo(LowEnd);TestTrue(TEXT("Only exact full low deadline permits rise"),!F.State().PendingLow&&F.State().Phase==BatReview::EPhase::Rising&&F.Bat->JumpHeight==20);
    const double RiseEnd=F.State().RiseStartedAt+(90-F.State().RiseOrigin.Z)/(70./.3);
    F.AdvanceTo(LowEnd+.15);TestTrue(TEXT("Rise is real .30 motion, not a teleport"),BatNear(F.Bat->JumpHeight,55));
    F.AdvanceTo(RiseEnd-.001);TestTrue(TEXT("No early high idle during final rise interval"),F.State().Action.InProgress&&F.State().Position.Z<90);
    F.AdvanceTo(RiseEnd);TestTrue(TEXT("Entire2.10 recovery completes before high idle"),F.State().Position.Z==90
        &&!F.State().Action.InProgress&&F.State().Action.CompletedAt==RiseEnd&&BatNear(RiseEnd-LowEnd,.3,1.e-12)&&F.State().Actions.size()==1);
    for(int32 I=0;I<300&&F.State().Actions.size()<2;++I)if(!F.AdvanceTo(F.Game->GetSimulationTime()+.01))return false;
    if(!TestTrue(TEXT("Normal next legal AI choice is Wing after completed first attack"),F.State().Actions.size()==2&&F.State().Action.Kind==BatReview::EAttack::Wing))return false;
    const auto W=F.State().Action;F.AdvanceTo(W.LockAt+.2);
    TestTrue(TEXT("Wing descends during actual second half windup"),BatNear(F.Bat->JumpHeight,55)&&F.Events(BatReview::EEventKind::ActiveWindow,W.AttackId)==0);
    F.AdvanceTo(W.ActiveAt);
    TestTrue(TEXT("Wing active begins at real20 and commits one10/12 contact"),F.Bat->JumpHeight==20&&F.Player->Health==78
        &&F.Events(BatReview::EEventKind::Hit,W.AttackId)==1&&W.Damage==10&&W.Stagger==12);
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBatReviewSamePoint,
    "CodexDungeon.Content.StoneBatAdmissionReview.SamePointPlayerPoiseOrDeathPreemptsBatWindow",EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FBatReviewSamePoint::RunTest(const FString& Parameters)
{
    for(int32 Lethal=0;Lethal<2;++Lethal)
    {
        FBatReviewWorld F(this);if(!F.Create({60,0},"WPN-GSW-001"))return false;
        if(Lethal)F.Bat->ApplyCombatHit(25,F.Player,0); // Real defended HP loss, no live HP assignment or raw incoming receipt.
        if(!TestTrue(TEXT("Actual central first attack establishes common endpoint"),F.FirstAttack()))return false;
        const auto A=F.State().Action;const double Impact=A.ActiveAt;
        if(!TestTrue(TEXT("Reach actual bat active minus frozen GSW windup"),F.AdvanceTo(Impact-.45)))return false;
        const double BeforeHP=F.State().HP;
        F.Player->StartJump();F.Player->BeginAttack();const auto P=F.Player->GetMeleeCombatState().Action;
        if(!TestTrue(TEXT("Real airborne GSW active endpoint is exactly the bat unprocessed emission"),P.Active&&P.StartedAirborne&&P.ActiveStart==Impact))return false;
        F.AdvanceTo(Impact);
        AddInfo(FString::Printf(TEXT("Bat endpoint lethal=%d sim=%.17g bat=%.17g sword=%.17g HP=%.9g received=%d interrupted=%d emitted=%d hits=%d playerHP=%.9g"),
            Lethal,F.Game->GetSimulationTime(),Impact,P.ActiveStart,double(F.Bat->Health),int32(F.State().ReceivedHits.size()),
            int32(F.State().Action.Interrupted),int32(F.State().Action.Emitted),int32(F.State().HitReceipts.size()),double(F.Player->Health)));
        if(!TestTrue(TEXT("Actual player window caused defended40 HP loss and real42 poise or death at the endpoint"),
            F.State().ReceivedHits.size()==std::size_t(Lethal+1)&&BatNear(F.State().ReceivedHits.back().HPLoss,FMath::Min(BeforeHP,40.))
            &&F.State().ReceivedHits.back().Stagger==42&&F.State().ReceivedHits.back().AtTime==Impact
            &&(Lethal?F.Bat->bDead:F.State().Phase==BatReview::EPhase::Stunned)))return false;
        TestTrue(TEXT("Same-point actual damage precedes unprocessed bat active window and contact"),!F.State().Action.Emitted
            &&F.Events(BatReview::EEventKind::ActiveWindow,A.AttackId)==0&&F.Events(BatReview::EEventKind::Hit,A.AttackId)==0&&F.Player->Health==100
            &&(Lethal?F.State().Phase==BatReview::EPhase::Dead:F.State().Action.Interrupted));
    }
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBatReviewDeathReward,
    "CodexDungeon.Content.StoneBatAdmissionReview.ActualLowCounterKillClaimsRewardOnce",EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FBatReviewDeathReward::RunTest(const FString& Parameters)
{
    FBatReviewWorld F(this);if(!F.Create({60,0},"WPN-GSW-001")||!TestTrue(TEXT("Real AI attack before counter window"),F.FirstAttack()))return false;
    F.AdvanceTo(F.State().Action.ActiveEnd);
    F.Player->BeginAttack();const auto One=F.Player->GetMeleeCombatState().Action;
    if(!TestTrue(TEXT("First actual ground greatsword counter accepted at low20"),One.Active&&!One.StartedAirborne&&F.Bat->JumpHeight==20))return false;
    F.AdvanceTo(One.ActiveStart);TestTrue(TEXT("Real first40 defended damage breaks poise without killing"),BatNear(F.Bat->Health,15)&&F.State().Phase==BatReview::EPhase::Stunned);
    F.AdvanceTo(One.End);F.Player->BeginAttack();const auto Two=F.Player->GetMeleeCombatState().Action;
    if(!TestTrue(TEXT("Second real primary fits inside the source low window"),Two.Active&&Two.ActiveStart<F.State().LowReadyAt))return false;
    F.AdvanceTo(Two.ActiveStart);
    if(!TestTrue(TEXT("Actual low counter damage kills and claims reward once"),F.Bat->bDead&&F.Bat->Health==0&&F.State().Phase==BatReview::EPhase::Dead
        &&F.State().RewardClaimed&&F.Events(BatReview::EEventKind::Died)==1&&F.Events(BatReview::EEventKind::RewardClaimed)==1))return false;
    const int32 Pickups=F.Game->Pickups.Num();const auto Events=F.State().NextEventId;
    F.Game->OnFighterDied(F.Bat);F.Game->OnFighterDied(F.Bat);F.Game->Tick(.5f);
    TestTrue(TEXT("Repeated real death notification and central tick never duplicate rewards or body/attack"),F.Game->Pickups.Num()==Pickups
        &&F.State().NextEventId==Events&&F.Events(BatReview::EEventKind::RewardClaimed)==1&&!F.State().PendingLow&&!F.State().Action.InProgress&&F.Game->bRoomCleared);
    return true;
}
#endif
