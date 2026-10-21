#include "DungeonGameMode.h"
#include "DungeonFighter.h"
#include "Engine/World.h"
#include "Kismet/GameplayStatics.h"
#include "Sound/SoundBase.h"
#include "Sound/SoundConcurrency.h"
namespace HA=DungeonHeroLocomotionAudioV001;
namespace
{
const TCHAR* HeroLocomotionCue(HA::ECue Cue)
{
 switch(Cue)
 {
 case HA::ECue::StepLight01:return TEXT("HERO_STEP_LIGHT_01");
 case HA::ECue::StepLight02:return TEXT("HERO_STEP_LIGHT_02");
 case HA::ECue::TakeoffLight01:return TEXT("HERO_TAKEOFF_LIGHT_01");
 case HA::ECue::LandLight01:return TEXT("HERO_LAND_LIGHT_01");
 case HA::ECue::LandFirm01:return TEXT("HERO_LAND_FIRM_01");
 case HA::ECue::DodgeShort01:return TEXT("HERO_DODGE_SHORT_01");
 default:return TEXT("");
 }
}
}
void ADungeonGameMode::LoadHeroLocomotionAudioV001()
{
 if(bHeroLocomotionSoundsLoaded)return;
 bHeroLocomotionSoundsLoaded=true;HeroLocomotionSounds.SetNum(6);
 for(int32 I=0;I<6;++I)
 {
  const FString Name=FString(TEXT("SW_AUD_"))+HeroLocomotionCue(HA::ECue(I))+TEXT("_v001");
  const FString Path=TEXT("/Game/Production/HeroLocomotion/v001/Audio/")+Name+TEXT(".")+Name;
  HeroLocomotionSounds[I]=LoadObject<USoundBase>(nullptr,*Path);
 }
 HeroLocomotionConcurrency=NewObject<USoundConcurrency>(this);
 HeroLocomotionConcurrency->Concurrency.MaxCount=6;
 HeroLocomotionConcurrency->Concurrency.bLimitToOwner=false;
 HeroLocomotionConcurrency->Concurrency.ResolutionRule=EMaxConcurrentResolutionRule::StopQuietest;
 HeroLocomotionConcurrency->Concurrency.VoiceStealReleaseTime=.025f;
}
HA::FScope ADungeonGameMode::HeroLocomotionScopeV001() const
{
 const auto& V=GetEquipmentView();
 return {IsValid(PlayerFighter)?PlayerFighter->GetRuntimeEntityId():0,
  V.Bound?V.RoomInstanceId:uint64(FMath::Max(1,RoomNumber)),RunRestartSerial,RunPresentationEpoch};
}
bool ADungeonGameMode::HeroLocomotionAudioActiveV001() const
{
 return GetWorld()&&!UGameplayStatics::IsGamePaused(this)&&!IsRunInstallGated()&&!bWaitingForStart
  &&!bGameOver&&!bFairytaleLookdevPreview&&IsValid(PlayerFighter)&&!PlayerFighter->bEnemy&&!PlayerFighter->bDead;
}
bool ADungeonGameMode::RefreshHeroLocomotionAudioV001()
{
 // Only the already published actual owner is eligible. Staging actors never
 // attach or append. Seeding reads current facts and emits no event.
 if(!IsValid(PlayerFighter)||PlayerFighter->bEnemy)return false;
 const auto Scope=HeroLocomotionScopeV001();const auto& V=GetEquipmentView();
 if(HeroLocomotionOwner.Get()!=PlayerFighter||HeroLocomotionRun!=V.RunGuid||!HA::Same(Scope,HeroLocomotionAttachedScope))
 {
  HeroLocomotionState=HA::FState();HeroLocomotionPlayRequests.Reset();
  HeroLocomotionOwner=PlayerFighter;HeroLocomotionRun=V.RunGuid;HeroLocomotionAttachedScope=Scope;
 }
 const auto& D=PlayerFighter->Dodge.State();
 return HeroLocomotionState.Attach(Scope,SimulationTime,D.NextEventId?D.NextEventId-1:0,
  double(PlayerFighter->JumpHeight),double(PlayerFighter->JumpVelocity));
}
void ADungeonGameMode::ObserveHeroGroundDistanceV001(ADungeonFighter* Fighter,double From,double To,double Distance,
 bool Grounded,bool OrdinaryEligible,bool HadIntent)
{
 if(Fighter!=PlayerFighter||!RefreshHeroLocomotionAudioV001())return;
 HeroLocomotionState.GroundDistance(HeroLocomotionScopeV001(),From,To,Distance,
  Grounded,OrdinaryEligible,HadIntent,HeroLocomotionAudioActiveV001());
}
void ADungeonGameMode::ObserveHeroTakeoffV001(ADungeonFighter* Fighter,double AtTime)
{
 if(Fighter!=PlayerFighter||!RefreshHeroLocomotionAudioV001())return;
 HeroLocomotionState.AcceptedTakeoff(HeroLocomotionScopeV001(),AtTime,HeroLocomotionAudioActiveV001());
}
void ADungeonGameMode::ObserveHeroAirMotionV001(ADungeonFighter* Fighter,double From,double To,
 double FromHeight,double ToHeight,double FallingSpeed)
{
 if(Fighter!=PlayerFighter||!RefreshHeroLocomotionAudioV001())return;
 HeroLocomotionState.AirMotion(HeroLocomotionScopeV001(),From,To,FromHeight,ToHeight,FallingSpeed,HeroLocomotionAudioActiveV001());
}
void ADungeonGameMode::ObserveHeroDodgeV001(ADungeonFighter* Fighter,const std::vector<DungeonDodge::FEvent>& Events)
{
 if(Fighter!=PlayerFighter||!RefreshHeroLocomotionAudioV001())return;
 for(const auto& E:Events)HeroLocomotionState.DodgeEvent(HeroLocomotionScopeV001(),E.EventId,E.OwnerId,E.ActionId,E.AtTime,
  E.Kind==DungeonDodge::EEventKind::Started,HeroLocomotionAudioActiveV001());
}
void ADungeonGameMode::DispatchHeroLocomotionAudioV001()
{
 if(!RefreshHeroLocomotionAudioV001())return;
 const auto Events=HeroLocomotionState.Consume(SimulationTime,HeroLocomotionAudioActiveV001());
 for(const auto& E:Events)
 {
  const int32 Index=int32(E.Cue);
  if(!HeroLocomotionSounds.IsValidIndex(Index)||!HeroLocomotionSounds[Index])continue;
  const bool Step=E.Cue==HA::ECue::StepLight01||E.Cue==HA::ECue::StepLight02;
  const float Volume=Step?.25f:.32f;
  // Existing native prototype event sink, centralized here rather than in
  // gameplay/draw code. bIsUISound=false respects engine pause. This candidate
  // does not claim production middleware/3D spatial/occlusion acceptance.
  UGameplayStatics::PlaySound2D(this,HeroLocomotionSounds[Index],Volume,1.f,0.f,HeroLocomotionConcurrency,PlayerFighter,false);
  FDungeonHeroLocomotionAudioPlayRequestV001 R;R.Source=E;R.Cue=HeroLocomotionCue(E.Cue);
  R.SoundPath=HeroLocomotionSounds[Index]->GetPathName();R.GroundPosition=PlayerFighter->GetGroundPosition();
  R.RequestedAt=SimulationTime;R.Volume=Volume;HeroLocomotionPlayRequests.Add(MoveTemp(R));
 }
 if(HeroLocomotionPlayRequests.Num()>256)
  HeroLocomotionPlayRequests.RemoveAt(0,HeroLocomotionPlayRequests.Num()-256,EAllowShrinking::No);
}
