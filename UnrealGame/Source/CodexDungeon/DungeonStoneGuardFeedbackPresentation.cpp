#include "DungeonHUD.h"
#include "DungeonFighter.h"
#include "DungeonGameMode.h"
#include "DungeonRunSnapshot.h"
#include "Components/AudioComponent.h"
#include "Engine/World.h"
#include "Kismet/GameplayStatics.h"
#include "Sound/SoundBase.h"
namespace
{
namespace GF=DungeonGuardFeedback;
float GuardGain(GF::ECue C)
{
 switch(C){case GF::ECue::Step:return .25f;case GF::ECue::AxeWindup:case GF::ECue::StompWindup:return .27f;
 case GF::ECue::AxeRelease:return .34f;case GF::ECue::StompImpact:return .44f;case GF::ECue::Death:return .45f;
 case GF::ECue::Wake:return .34f;default:return .30f;}
}
double GuardFxDuration(GF::EFx F)
{switch(F){case GF::EFx::CancelAttack:case GF::EFx::None:return 0.;case GF::EFx::DeathChunks:return .85;case GF::EFx::WakeCracks:return .75;case GF::EFx::WindupGrit:return .48;case GF::EFx::StompBurst:return .5;default:return .32;}}
}
void ADungeonHUD::LoadGuardFeedbackSounds()
{
 for(int32 I=int32(GF::ECue::Wake);I<=int32(GF::ECue::Death);++I)
 {
  const FString Cue=UTF8_TO_TCHAR(GF::CueName(GF::ECue(I)));const FString Name=TEXT("SW_AUD_")+Cue+TEXT("_v001");
  const FString Path=TEXT("/Game/Production/FirstBatch/v028/GuardAudio/")+Name+TEXT(".")+Name;
  if(auto* Sound=LoadObject<USoundBase>(nullptr,*Path))GuardSounds.Add(Cue,Sound);
 }
}
void ADungeonHUD::ResetGuardFeedback(ADungeonGameMode* Game)
{
 for(auto& W:GuardWindups)if(auto* C=W.Component.Get())C->Stop();
 GuardWindups.Reset();GuardEffects.Reset();GuardEventCursors.Reset();GuardAudioPlayRequests.Reset();
 GuardAudioPlayReceipts.Reset();GuardEffectSpawnRequests.Reset();bGuardFeedbackAttached=false;GuardFeedbackRun.Invalidate();
 if(!Game||!Game->GetEquipmentView().RunGuid.IsValid())return;
 GuardFeedbackRun=Game->GetEquipmentView().RunGuid;bGuardFeedbackAttached=true;
 for(const auto F:Game->Enemies)if(IsValid(F)&&F->GetStoneGuardDriver())GuardEventCursors.Add(F,F->GetGuardFeedback().LastSequence());
}
void ADungeonHUD::UpdateGuardFeedback(ADungeonGameMode* Game)
{
 if(!Game||Game->IsRunInstallGated())return;const auto& View=Game->GetEquipmentView();
 if(!bGuardFeedbackAttached||GuardFeedbackRun!=View.RunGuid){ResetGuardFeedback(Game);return;}
 const double Now=Game->GetSimulationTime();
 GuardEffects.RemoveAll([Now](const FGuardEffect& F){return !F.Owner.IsValid()||Now>=F.Request.ExpiresAt;});
 GuardWindups.RemoveAll([](const FGuardWindup& W){return !W.Owner.IsValid()||!W.Component.IsValid();});
 for(auto It=GuardEventCursors.CreateIterator();It;++It)if(!It.Key().IsValid())It.RemoveCurrent();
 for(const auto FighterPtr:Game->Enemies)
 {
  ADungeonFighter* F=FighterPtr.Get();
  if(!IsValid(F)||!F->GetStoneGuardDriver())continue;
  auto& Cursor=GuardEventCursors.FindOrAdd(F); // Spawn after HUD attachment starts at its actual sequence0.
  for(const auto& R:F->GetGuardFeedback().Entries())
  {
   if(R.Sequence<=Cursor)continue;Cursor=R.Sequence; // Advance even if stale or missing assets; never retry history.
   const bool Cancel=R.Effect==GF::EFx::CancelAttack,Dead=R.Effect==GF::EFx::DeathChunks;
   if(Cancel||Dead)
   {
    for(int32 I=GuardWindups.Num()-1;I>=0;--I)if(GuardWindups[I].Owner==F&&(Dead||GuardWindups[I].AttackId==R.AttackId))
    {if(auto* C=GuardWindups[I].Component.Get())C->Stop();GuardWindups.RemoveAt(I);}
    GuardEffects.RemoveAll([&](const FGuardEffect& E){return E.Owner==F&&(Dead||(E.Request.Source.AttackId==R.AttackId&&E.Request.Source.Effect==GF::EFx::WindupGrit));});
   }
   const double Age=Now-R.AtTime;if(Age<0.)continue;
   const double Duration=GuardFxDuration(R.Effect);
   if((Cancel||Age<Duration)&&R.Effect!=GF::EFx::None)
   {
    FDungeonGuardEffectSpawnRequest Request;Request.Source=R;Request.StartedAt=R.AtTime;Request.ExpiresAt=R.AtTime+Duration;
    GuardEffectSpawnRequests.Add(Request);
    if(Duration>0)GuardEffects.Add({F,Request});
   }
   const FString Cue=UTF8_TO_TCHAR(GF::CueName(R.Cue));if(Cue.IsEmpty()||Age>.25)continue;
   const auto* Sound=GuardSounds.Find(Cue);if(!Sound||!Sound->Get())continue; // No silent resource substitution.
   const float Volume=GuardGain(R.Cue);const bool Windup=R.Cue==GF::ECue::AxeWindup||R.Cue==GF::ECue::StompWindup;
   if(Windup)
   {
    auto* Component=UGameplayStatics::SpawnSound2D(this,Sound->Get(),Volume,1.f);
    if(Component)GuardWindups.Add({F,R.AttackId,Component});
   }
   else UGameplayStatics::PlaySound2D(this,Sound->Get(),Volume,1.f);
   ++GuardAudioPlayRequests.FindOrAdd(Cue);FDungeonGuardAudioPlayRequest Request;Request.Source=R;Request.Cue=Cue;
   Request.SoundPath=Sound->Get()->GetPathName();Request.RequestedAt=Now;Request.Volume=Volume;Request.Pitch=1.f;GuardAudioPlayReceipts.Add(MoveTemp(Request));
  }
 }
 if(GuardEffects.Num()>128)GuardEffects.RemoveAt(0,GuardEffects.Num()-128,EAllowShrinking::No);
 if(GuardAudioPlayReceipts.Num()>256)GuardAudioPlayReceipts.RemoveAt(0,GuardAudioPlayReceipts.Num()-256,EAllowShrinking::No);
 if(GuardEffectSpawnRequests.Num()>256)GuardEffectSpawnRequests.RemoveAt(0,GuardEffectSpawnRequests.Num()-256,EAllowShrinking::No);
}
void ADungeonHUD::DrawGuardFeedback(ADungeonFighter* Fighter)
{
 if(!Canvas||!Fighter)return;auto* Game=GetWorld()?GetWorld()->GetAuthGameMode<ADungeonGameMode>():nullptr;if(!Game)return;
 const double Now=Game->GetSimulationTime();
 for(const auto& Fx:GuardEffects)
 {
  if(Fx.Owner!=Fighter)continue;const auto& Q=Fx.Request;const auto& R=Q.Source;
  if(Now<Q.StartedAt||Now>=Q.ExpiresAt)continue;
  const float T=float((Now-Q.StartedAt)/(Q.ExpiresAt-Q.StartedAt)),Fade=1.f-T;
  FVector2D P=Ground({R.Position.X,R.Position.Y});const float Side=float(R.Facing);
  const bool GroundFx=R.Effect==GF::EFx::FootDust||R.Effect==GF::EFx::StompBurst||R.Effect==GF::EFx::AxeDustCut;
  const bool Death=R.Effect==GF::EFx::DeathChunks,Metal=R.Effect==GF::EFx::HitSparks;
  const int32 Count=Death?13:GroundFx?7:5;
  FLinearColor C=Metal?FLinearColor(.94f,.69f,.34f,Fade):R.Effect==GF::EFx::HitPuff?FLinearColor(.36f,.20f,.12f,Fade*.7f):FLinearColor(.48f,.43f,.34f,Fade*.72f);
  if(R.Effect==GF::EFx::AxeDustCut)P.X+=Side*(16.f+T*50.f);
  if(R.Effect==GF::EFx::WakeCracks||R.Effect==GF::EFx::WindupGrit||R.Effect==GF::EFx::StoneChips||R.Effect==GF::EFx::StunChips||Metal)P.Y-=24.f;
  for(int32 I=0;I<Count;++I)
  {
   // Fixed event-derived chip directions; finite ballistic shards, no ambient rings.
   const float Seed=float((R.EventId*17+uint64(I)*31)%97)/97.f;
   const float X=(Seed-.5f)*(Death?90.f:GroundFx?60.f:34.f)*(T+.12f);
   const float Y=GroundFx?-(1.f-Seed)*10.f*FMath::Sin(T*PI):-(12.f+Seed*25.f)*T+(Death?38.f:22.f)*T*T;
   const float Size=(Death?3.8f:Metal?1.2f:2.4f)*(1.f-.5f*T);const FVector2D A=P+FVector2D(X,Y);
   if(Metal)Line(A.X,A.Y,A.X+Side*(2.f+Seed*4.f),A.Y-2.f,C,1.f);
   else Triangle(A+FVector2D(-Size,Size*.4f),A+FVector2D(Size,Size*.7f),A+FVector2D(.3f*Size,-Size),C);
  }
  if(R.Effect==GF::EFx::WakeCracks)for(int32 I=0;I<3;++I)
  {const float X=P.X-9.f+I*8.f;Line(X,P.Y-10.f,X+Side*3.f,P.Y-3.f,C,1.f);Line(X+Side*3.f,P.Y-3.f,X-Side*2.f,P.Y+3.f,C,1.f);}
 }
}
