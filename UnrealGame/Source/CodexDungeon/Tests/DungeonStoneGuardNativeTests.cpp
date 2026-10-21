#if WITH_DEV_AUTOMATION_TESTS
#include "Misc/AutomationTest.h"
#include "../DungeonFighter.h"
#include "../DungeonGameMode.h"
#include "../DungeonRoomLayout.h"
#include "Components/BoxComponent.h"
#include "CollisionQueryParams.h"
#include "CollisionShape.h"
#include "Engine/Engine.h"
#include "Engine/GameInstance.h"
#include "Engine/World.h"
#include <cmath>
namespace StoneGuardNativeTests
{
namespace Guard=DungeonStoneGuard;
bool Near(double A,double B,double T=2.e-4){return std::abs(A-B)<=T;}
struct FWorld
{
 UWorld* World=nullptr;ADungeonGameMode* Game=nullptr;ADungeonFighter* Player=nullptr;ADungeonFighter* Enemy=nullptr;
 FAutomationTestBase& Test;
 explicit FWorld(FAutomationTestBase& T):Test(T){}
 ~FWorld(){if(World){if(World->HasBegunPlay())World->EndPlay(EEndPlayReason::Quit);World->DestroyWorld(false);if(GEngine)GEngine->DestroyWorldContext(World);}}
 bool Create()
 {
  if(!Test.TestNotNull(TEXT("Existing GEngine fixture prerequisite"),GEngine))return false;
  const auto Settings=UWorld::InitializationValues().AllowAudioPlayback(false).CreatePhysicsScene(true)
   .RequiresHitProxies(false).CreateNavigation(false).CreateAISystem(false).ShouldSimulatePhysics(false).SetTransactional(false);
  World=UWorld::CreateWorld(EWorldType::Game,false,NAME_None,nullptr,true,ERHIFeatureLevel::Num,&Settings);
  if(!Test.TestNotNull(TEXT("Real physics UWorld fixture prerequisite"),World))return false;
  GEngine->CreateNewWorldContext(EWorldType::Game).SetCurrentWorld(World);World->SetGameInstance(NewObject<UGameInstance>(GEngine));
  FURL URL;URL.AddOption(TEXT("game=/Script/CodexDungeon.DungeonGameMode"));
  if(!Test.TestTrue(TEXT("Existing actual GameMode construction prerequisite"),World->SetGameMode(URL)))return false;
  Game=World->GetAuthGameMode<ADungeonGameMode>();Player=World->SpawnActor<ADungeonFighter>();
  if(!Test.TestNotNull(TEXT("Existing native GameMode"),Game)||!Test.TestNotNull(TEXT("Existing native player actor"),Player))return false;
  Player->SetActorTickEnabled(false);Player->ResetFighter({0,0});Game->PlayerFighter=Player;Game->bWaitingForStart=false;
  if(!Test.TestTrue(TEXT("Existing real bound integration Run prerequisite"),Game->BeginEquipmentRun(EDungeonEquipmentRunConfig::IntegrationPreview,1)))return false;
  const auto& V=Game->GetEquipmentView();const auto& W=Game->GetWeaponWorldState();
  return Test.TestTrue(TEXT("Normal owner/room/Run identity positive premise"),V.Bound&&V.RunGuid.IsValid()&&V.OwnerId==Player->GetRuntimeEntityId()
   &&V.OwnerId>0&&V.RoomInstanceId>0&&W.RunGuid==V.RunGuid&&W.RoomInstanceId==V.RoomInstanceId&&Game->GetSimulationTime()==0&&Player->Health==100);
 }
 bool Spawn(FVector2D P)
 {
  Enemy=Game->SpawnStoneGuard(P);
  if(!Test.TestNotNull(TEXT("STN003 new API must create a genuine admitted Guard (Stage0 semantic stub)"),Enemy))return false;
  return Test.TestNotNull(TEXT("STN003 dedicated driver must be attached"),Enemy->GetStoneGuardDriver());
 }
 const Guard::FState& State()const{return Enemy->GetStoneGuardDriver()->State();}
 bool AdvanceTo(double At)
 {
  if(!std::isfinite(At)||At<Game->GetSimulationTime())return false;
  for(int32 I=0;I<64&&Game->GetSimulationTime()<At;++I)
  {
   const double Remaining=At-Game->GetSimulationTime();float Dt=float(Remaining);
   if(double(Dt)>Remaining)Dt=std::nextafter(Dt,0.f);if(!(Dt>0))return false;
   const double Before=Game->GetSimulationTime();Game->Tick(Dt);if(Game->GetSimulationTime()<=Before)return false;
  }
  return Game->GetSimulationTime()==At;
 }
 bool AwaitAction()
 {for(int32 I=0;I<350&&!State().Action.InProgress&&!Game->bGameOver;++I)Game->Tick(.01f);return State().Action.InProgress;}
 int32 Count(Guard::EEventKind Kind)const{int32 N=0;for(const auto& E:State().Issued)N+=E.Kind==Kind;return N;}
 AActor* Wall(FVector2D P,FVector Extent)
 {
  auto A=World->SpawnActor<AActor>();if(!A)return nullptr;auto Box=NewObject<UBoxComponent>(A);A->SetRootComponent(Box);
  Box->SetBoxExtent(Extent);Box->SetCollisionEnabled(ECollisionEnabled::QueryOnly);Box->SetCollisionObjectType(ECC_WorldStatic);
  Box->SetCollisionResponseToAllChannels(ECR_Block);Box->RegisterComponentWithWorld(World);A->SetActorLocation({P.X,P.Y,50});return A;
 }
};
}
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDungeonStoneGuardNativeIdentityAndResolvedHP,
 "CodexDungeon.Content.StoneGuardNative.IdentityDefenseAndSingleResolvedHPMirror",
 EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FDungeonStoneGuardNativeIdentityAndResolvedHP::RunTest(const FString& Parameters)
{
 (void)Parameters;using namespace StoneGuardNativeTests;FWorld F(*this);if(!F.Create()||!F.Spawn({100,0}))return false;
 const uint64 Id=F.Enemy->GetRuntimeEntityId();const auto& V=F.Game->GetEquipmentView();
 const auto* Binding=F.Game->GetWeaponWorldState().ActorBindings.FindByPredicate([Id](const auto& B){return B.EntityId==Id;});
 TestTrue(TEXT("Exact Guard identity belongs to the real current room rather than a pointer/generic alias"),Id>V.OwnerId&&Id<(uint64(1)<<63)
  &&Binding&&Binding->RoomInstanceId==V.RoomInstanceId&&Binding->ContentId==TEXT("ENM-STN-003")
  &&F.Enemy->EnemyContentId==TEXT("ENM-STN-003")&&F.State().EntityId==Id&&F.Enemy->bEnemy);
 TestTrue(TEXT("Guard initial Actor and kernel are 185HP ground dormant without invented events"),F.Enemy->Health==185&&F.Enemy->MaxHealth==185
  &&F.State().HP==185&&F.State().Phase==Guard::EPhase::Dormant&&F.State().Issued.empty()&&F.Enemy->JumpHeight==0&&!F.Enemy->IsActorTickEnabled());
 TestTrue(TEXT("Exact passive armor60 ward15 poise85 speed160, no shield multiplier"),F.Enemy->GetArmorRating()==60&&F.Enemy->GetArmorRating(true)==15&&F.Enemy->GetPoiseThreshold()==85&&F.Enemy->GetMoveSpeed()==160);
 TestTrue(TEXT("Independent native body and projectile hurt profile40x28"),F.Enemy->GetCombatBodyHalfExtent()==FVector2D(40,28)&&F.Enemy->GetProjectileHurtHalfExtent()==FVector2D(40,28));
 const auto Cursor=F.Game->GetWeaponWorldState().NextEntityId;
 TestNull(TEXT("Invalid room spawn rejected"),F.Game->SpawnStoneGuard({DungeonRoomLayout::MaxX+1,0}));
 TestEqual(TEXT("Invalid spawn does not allocate a logical ID"),F.Game->GetWeaponWorldState().NextEntityId,Cursor);
 F.Enemy->ApplyCombatHit(16.f,F.Player,0.f); // 60/160 mitigation: exactly10, not6.25.
 TestTrue(TEXT("Physical mitigation once then exactly one actual10 HP receipt"),Near(F.Enemy->Health,175)&&Near(F.State().HP,175)
  &&F.State().ReceivedHits.size()==1&&Near(F.State().ReceivedHits.front().ActualHPLoss,10)&&F.State().LastDamageReceiptId==1);
 F.Enemy->ApplyCombatHit(11.5f,F.Player,0.f,true);
 TestTrue(TEXT("Magic ward15 applies once and preserves mirror with second10 receipt"),Near(F.Enemy->Health,165)&&Near(F.State().HP,165)
  &&F.State().ReceivedHits.size()==2&&Near(F.State().ReceivedHits.back().ActualHPLoss,10));
 TestTrue(TEXT("Real positive HP loss begins full warning without healing or immediate generic hurt"),F.State().WakeStartedAt==0&&F.State().WakeEnd==1
  &&F.State().Phase==Guard::EPhase::Waking&&F.Enemy->AnimationName==TEXT("stone_guard_placeholder_wake")&&F.Enemy->CanReceiveDirectHit());
 F.Game->Tick(.02f);TestTrue(TEXT("Only central GameMode clock advances actual Guard"),F.State().Time==F.Game->GetSimulationTime()&&F.State().Time>0);
 TestFalse(TEXT("Duplicate initialization is not an owner/health reset"),F.Enemy->InitializeStoneGuard(Id,F.Game->GetSimulationTime()));
 TestTrue(TEXT("Rejected reinitialization preserves actual HP and Run ID"),Near(F.Enemy->Health,165)&&Near(F.State().HP,165)&&F.State().EntityId==Id);
 return true;
}
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDungeonStoneGuardNativeAttacksAndInterrupt,
 "CodexDungeon.Content.StoneGuardNative.RealClockAxeStompLockAndPoiseCancellation",
 EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FDungeonStoneGuardNativeAttacksAndInterrupt::RunTest(const FString& Parameters)
{
 (void)Parameters;using namespace StoneGuardNativeTests;
 for(int Face:{-1,1})
 {
  FWorld F(*this);if(!F.Create()||!F.Spawn({-Face*150.,0}))return false;
  if(!TestTrue(TEXT("Normal central AI accepts authored axe after actual warning"),F.AwaitAction()))return false;
  const auto A=F.State().Action;
  TestTrue(TEXT("Twohand axe exact accepted clock, damage24/stagger30 and stationary owner"),A.Kind==Guard::EAttack::AxeSweep&&A.Start==F.State().WakeEnd
   &&A.LockAt==A.Start+.5&&A.ActiveAt==A.Start+1&&Near(A.ActiveEnd,A.ActiveAt+.2)&&A.RecoveryEnd==A.ActiveEnd+1.4&&A.Damage==24&&A.Stagger==30);
  const auto Position=F.Enemy->GetGroundPosition();if(!TestTrue(TEXT("Reach actual lock deadline through public GameMode Tick"),F.AdvanceTo(A.LockAt)))return false;
  TestTrue(TEXT("Mirrored actual half-windup facing lock"),F.State().Action.Locked&&F.State().Action.Facing==Face&&F.Enemy->Facing==Face);
  const double Before=F.Player->Health,Rating=F.Player->GetArmorRating();const double Loss=24*(1-FMath::Min(.6,Rating/(100+Rating)));
  if(!TestTrue(TEXT("Reach actual active deadline"),F.AdvanceTo(A.ActiveAt)))return false;
  TestTrue(TEXT("One actual native24 raw axe hit uses real target defense, not generic13"),Near(F.Player->Health,Before-Loss)&&F.Count(Guard::EEventKind::Hit)==1&&F.State().HitReceipts.size()==1);
  F.AdvanceTo(A.ActiveEnd+.01);TestTrue(TEXT("Active200ms never redamages same target and enters real counter recovery"),Near(F.Player->Health,Before-Loss)
   &&F.State().Phase==Guard::EPhase::Recovery&&F.Enemy->AttackPhase==TEXT("recovery")&&F.Enemy->GetGroundPosition()==Position);
 }
 {
  FWorld F(*this);if(!F.Create()||!F.Spawn({0,80})||!TestTrue(TEXT("Real side approach selects stomp"),F.AwaitAction()))return false;
  const auto A=F.State().Action;TestTrue(TEXT("Stomp own-center .45 lock/.9 warning/.15 active/1.5 recovery"),A.Kind==Guard::EAttack::Stomp&&A.LockAt==A.Start+.45&&A.ActiveAt==A.Start+.9&&Near(A.ActiveEnd,A.ActiveAt+.15)&&A.RecoveryEnd==A.ActiveEnd+1.5&&A.Damage==18&&A.Stagger==25);
  const double Before=F.Player->Health,Rating=F.Player->GetArmorRating();if(!F.AdvanceTo(A.ActiveAt))return false;
  TestTrue(TEXT("One actual native ellipse stomp hit18"),Near(F.Player->Health,Before-18*(1-FMath::Min(.6,Rating/(100+Rating))))&&F.Count(Guard::EEventKind::Hit)==1);
  F.AdvanceTo(A.ActiveEnd+.05);TestEqual(TEXT("Stomp has one impulse event rather than per-frame pulses"),F.Count(Guard::EEventKind::Hit),1);
 }
 {
  FWorld F(*this);if(!F.Create()||!F.Spawn({-150,0})||!F.AwaitAction())return false;const auto A=F.State().Action;
  if(!F.AdvanceTo(A.Start+.8))return false;F.Enemy->ApplyCombatHit(1.6f,F.Player,85.f);F.Enemy->bAIEnabled=false;
  TestTrue(TEXT("Real buffered85 stagger breaks and cancels before window without refund"),F.State().Phase==Guard::EPhase::Stunned&&F.State().Action.Interrupted
   &&F.Count(Guard::EEventKind::PoiseBroken)==1&&F.State().Windows.empty()&&F.State().AxeReadyAt==A.CooldownEnd&&Near(F.Enemy->Health,184));
  F.AdvanceTo(A.RecoveryEnd+.3);TestTrue(TEXT("Cancelled action cannot release a delayed native hit or skip its recovery"),F.Player->Health==100&&F.Count(Guard::EEventKind::Hit)==0
   &&F.Count(Guard::EEventKind::AttackCompleted)==1&&F.State().Action.AttackId==A.AttackId&&F.State().Phase==Guard::EPhase::Idle);
 }
 return true;
}
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDungeonStoneGuardNativeGeometryAndDeath,
 "CodexDungeon.Content.StoneGuardNative.NativeWideSweepBodyBlockingAndUnrewardedDeath",
 EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FDungeonStoneGuardNativeGeometryAndDeath::RunTest(const FString& Parameters)
{
 (void)Parameters;using namespace StoneGuardNativeTests;FWorld F(*this);if(!F.Create())return false;
 auto Wall=F.Wall({-225,30},{2,8,120});if(!TestNotNull(TEXT("Real registered off-center blocking UBox prerequisite"),Wall))return false;
 FCollisionObjectQueryParams Objects;Objects.AddObjectTypesToQuery(ECC_WorldStatic);FCollisionQueryParams Params;
 FHitResult Line;const bool CenterLOS=F.World->LineTraceSingleByObjectType(Line,{-300,0,0},{0,0,0},Objects,Params);
 TArray<FHitResult> Wide;F.World->SweepMultiByObjectType(Wide,{-300,0,0},{-180,0,0},FQuat::Identity,Objects,FCollisionShape::MakeBox(FVector(40,28,1)),Params);
 TestFalse(TEXT("Off-center wall leaves center LOS clear (native positive premise)"),CenterLOS&&Line.bBlockingHit);
 if(!TestTrue(TEXT("Same actual wall blocks a real40x28 sweep (native positive premise)"),Wide.ContainsByPredicate([Wall](const FHitResult& H){return H.GetActor()==Wall&&H.bBlockingHit;})))return false;
 if(!F.Spawn({-300,0}))return false;F.Enemy->ApplyCombatHit(1.6f,F.Player,0.f);F.Game->Tick(2.5f);
 const auto P=F.Enemy->GetGroundPosition();
 TestTrue(TEXT("Native Guard body sweep stops at wall before generic small body would"),P.X>-300&&P.X<=-267+.02&&F.State().Position.X==P.X&&F.State().Position.Y==P.Y&&F.State().Time==F.Game->GetSimulationTime());
 TestTrue(TEXT("Wall stop does not invent contact damage or bypass declared range"),F.Player->Health==100&&F.Count(Guard::EEventKind::Hit)==0&&F.State().Action.AttackId==0);
 Wall->Destroy();F.Enemy->bAIEnabled=false;F.Game->Tick(1.f);
 const auto GuardPosition=F.Enemy->GetGroundPosition();F.Player->MoveOnGround({-1,0},2.f);const auto Blocked=F.Player->GetGroundPosition();
 TestTrue(TEXT("Normal actual player motion blocks at18+40 body sum, not generic18+18"),Blocked.X<-.1&&Blocked.X>=GuardPosition.X+58-.02);
 const int32 Pickups=F.Game->Pickups.Num();const int32 Coins=F.Player->Coins;F.Enemy->ApplyCombatHit(100000.f,F.Player,85.f);
 TestTrue(TEXT("Actual lethal loss synchronizes dead Actor, authoritative HP and one Died"),F.Enemy->bDead&&F.Enemy->Health==0&&F.State().HP==0&&F.State().Phase==Guard::EPhase::Dead&&F.Count(Guard::EEventKind::Died)==1);
 TestTrue(TEXT("Unsupported reward consumer is explicit and produces no fake5coin or completion"),!F.Enemy->IsStoneGuardDeathSettled()&&F.Game->Pickups.Num()==Pickups&&F.Player->Coins==Coins&&!F.Game->bRoomCleared);
 TestTrue(TEXT("Actual local death eligibility can be claimed exactly once without granting currency"),F.Enemy->ClaimStoneGuardDeathEligibility()&&!F.Enemy->ClaimStoneGuardDeathEligibility()&&F.State().RewardClaimed&&F.Game->Pickups.Num()==Pickups);
 F.Game->LastMessage=TEXT("guard-death-observed-sentinel");F.Game->OnFighterDied(F.Enemy);F.Game->OnFighterDied(F.Enemy);
 TestTrue(TEXT("Repeated death notifications neither repeat feedback nor mint rewards"),F.Game->LastMessage==TEXT("guard-death-observed-sentinel")&&F.Count(Guard::EEventKind::Died)==1&&F.Game->Pickups.Num()==Pickups);
 F.Player->MoveOnGround({-1,0},1.f);TestTrue(TEXT("Actual dead Guard body no longer blocks normal player motion"),F.Player->GetGroundPosition().X<GuardPosition.X);
 return true;
}
#endif
