#if WITH_DEV_AUTOMATION_TESTS
#include "Misc/AutomationTest.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
#include "../DungeonFairytaleSwordHurtPlan.h"
#include "../DungeonRunInstaller.h"
#include "../DungeonRunSnapshotCodec.h"
#include "RunCodecFixture_v001.h"
#include <algorithm>
#include <cmath>

namespace
{
namespace H=DungeonFairytaleSwordHurtV001;
namespace B=DungeonFairytaleSwordEquipmentBinding;
struct FHurtOptInScope
{
 const FString Original=FCommandLine::Get();
 FHurtOptInScope()
 {
  FString Next=Original;
  for(const TCHAR* Flag:{B::CommandLineFlag,H::CommandLineFlag})
   if(!FParse::Param(*Next,Flag))Next+=FString(TEXT(" -"))+Flag;
  FCommandLine::Set(*Next);
 }
 ~FHurtOptInScope(){FCommandLine::Set(*Original);}
};
bool EquipLight(FCodecWorld& W,const TCHAR* Key)
{
 IV::FItem Item;Item.ContentId="ARM-LGT-001";
 const auto R=W.Game->RegisterEquipmentSource(Key,Item,W.Player->GetGroundPosition()+FVector2D(24,0),true);
 if(!W.Test.TestTrue(TEXT("PRECONDITION real legal LGT source selects and begins existing armor pickup"),R.Ok()&&W.Game->SelectEquipmentSource(R.SourceId)))return false;
 W.Game->TryInteractEquipment();const auto A=W.Game->GetEquipmentView().Action;
 if(!W.Test.TestTrue(TEXT("PRECONDITION actual armor transaction owns its original .5s deadline"),A.Active&&A.InstanceId==R.InstanceId
  &&A.Deadline==W.Game->GetSimulationTime()+.5&&W.AdvanceTo(A.Deadline)))return false;
 B::FBinding Binding;FString Why;
 return W.Test.TestTrue(TEXT("PRECONDITION existing real binding accepts actually committed SWD/LGT"),
  W.Player->ArmorId==TEXT("ARM-LGT-001")&&B::Resolve(*W.Game,*W.Player,Binding,Why)&&Binding.Armor==B::EArmor::LightArmor
  &&Binding.ArmorInstanceId==R.InstanceId&&!W.Game->GetEquipmentView().Action.Active);
}
bool CaptureActual(FCodecWorld& W,FDungeonRunSnapshot& Out,const TCHAR* Label)
{
 FString Why;const bool Ok=W.Game->CaptureRunSnapshot(Out,Why);
 if(!Ok)W.Test.AddInfo(FString(Label)+TEXT(" capture diagnosis: ")+Why);
 return W.Test.TestTrue(Label,Ok&&Out.Fighters.Num()>0);
}
bool TriggerRealHurt(FCodecWorld& W,FDungeonRunSnapshot& Out)
{
 if(!W.Test.TestTrue(TEXT("PRECONDITION normal J starts an actual grounded SWD primary before hit"),W.Pulse(EKeys::J)
  &&W.Player->GetMeleeCombatState().Action.Active&&!W.Player->GetMeleeCombatState().Action.StartedAirborne))return false;
 const float BeforeHP=W.Player->Health;const float Threshold=W.Player->GetPoiseThreshold();
 W.Player->ApplyCombatHit(5.f,nullptr,Threshold);W.Frame(.02f);
 if(!CaptureActual(W,Out,TEXT("PRECONDITION completed real nonlethal poise-hit Run captures")))return false;
 const auto& S=Out.Fighters[0];
 return W.Test.TestTrue(TEXT("PRECONDITION actual positive hit broke current poise and interrupted J; private hurt was not assigned"),
  Threshold==30.f&&S.Health<BeforeHP&&S.Health>0.f&&!S.Dead&&S.AnimationName==TEXT("hurt")
  &&S.AnimationTime>0.f&&S.AnimationTime<.1f&&S.HurtTime>0.f&&S.HurtTime<.4f
  &&S.PoiseAccumulation==0.f&&S.PoiseProtection>0.f&&!W.Player->GetMeleeCombatState().Action.Active);
}
H::FDrawContext ActualContext(const FCodecWorld& W)
{
 H::FDrawContext C;const auto P=W.Player->GetGroundPosition();const auto Camera=W.HUD->GetCameraGroundCenter();
 C.GroundScreen={640.+(P.X-Camera.X)*.65,490.-P.Y*.38};C.UIScale=1.;C.JumpHeight=W.Player->JumpHeight;return C;
}
TArray<uint8> PlanSignature(const H::FDrawPlan& P)
{
 FSignature S;S.V(P.Supported,P.Frame,P.Facing,P.Hurt.Elapsed,P.Hurt.Remaining,P.Hurt.Active,P.CanvasSize,P.SourceToScreenScale,
  P.WeaponScale,P.WeaponWidth,P.WeaponAngle,P.TextureU,P.TextureDU,P.NonemptyDrawCount);
 S.String(P.ProfileId);S.V(P.Binding.RunGuid.A,P.Binding.RunGuid.B,P.Binding.RunGuid.C,P.Binding.RunGuid.D,P.Binding.RunAlias,
  P.Binding.OwnerId,P.Binding.Revision,P.Binding.ActiveSlot,P.Binding.WeaponInstanceId,P.Binding.WeaponVersion,P.Binding.ArmorInstanceId,P.Binding.ArmorVersion,P.Binding.Armor);
 S.String(P.Binding.WeaponContentId);S.String(P.Binding.ArmorContentId);
 for(auto V:{P.RootSource,P.GripSource,P.AxisArtist,P.BodyTop,P.GripScreen,P.SwordTop,P.SwordPivotUV})S.V(V.X,V.Y);
 for(const auto& V:P.Slots){S.V(V.Component,V.KnownOptionalEmpty);S.String(V.TexturePath);}return S.Bytes;
}
H::FDrawPlan SentinelPlan()
{
 H::FDrawPlan P;P.Supported=true;P.Frame=91;P.Facing=17;P.ProfileId=TEXT("sentinel.plan");P.Binding.OwnerId=995;
 P.Hurt={true,9.f,8.f};P.RootSource={71,72};P.GripScreen={73,74};P.CanvasSize=75.;P.WeaponScale=76.;
 P.Slots[0].TexturePath=TEXT("sentinel.texture");P.NonemptyDrawCount=77;return P;
}
TArray<uint8> HurtSignature(const FDungeonHurtPresentationSample& P){FSignature S;S.V(P.Active,P.Elapsed,P.Remaining);return S.Bytes;}
bool Prepared32Precondition(FAutomationTestBase& T)
{
 const auto& P=H::Profile();TSet<FString> Paths;int32 Empty=0;
 bool Ok=P.SourceClosureVerified&&P.ProfileId==TEXT("EV048-v017-HeroLeatherHurt-v001")&&P.SourceClosureSHA256==TEXT("38e3a3c90eeda66842a2f2d5c53260832c226d18ca58640ee0720dc9271a1f28")
  &&P.CanvasSource==512&&P.StandingExtent==416.&&P.StandingDisplay==72.&&P.WeaponScale==.5&&P.ComponentGrip==FVector2D(99,256);
 for(int32 I=0;I<4;++I)
 {
  const auto& F=P.Frames[I];Ok&=F.Frame==I&&F.ExpectedNonemptyDrawCount==(I==0?9:8)&&F.Grip==FVector2D(I==0?236:I==1?194:I==2?205:218,I==0||I==3?303:289);
  for(const auto& L:F.Layers)
  {
   Ok&=!L.TexturePath.IsEmpty()&&L.TexturePath.StartsWith(TEXT("/Game/Production/ArtTrials/EV048/v017/HeroLeatherHurt/"))
    &&L.TexturePath.Contains(TEXT("."))&&!Paths.Contains(L.TexturePath)&&L.SourceSHA256.Len()==64&&L.SourceRGBASHA256.Len()==64;
   Paths.Add(L.TexturePath);if(L.KnownOptionalEmpty){++Empty;Ok&=I>0&&L.Component==H::EComponent::FarHandForeground&&L.SourceAlphaNonzero==0;}
   else Ok&=L.SourceAlphaNonzero>0;
  }
 }
 return T.TestTrue(TEXT("PRECONDITION immutable actual E454 source contract is exactly5 owners+3 armor x4, no WholeBody, three documented empty farhands"),Ok&&Paths.Num()==32&&Empty==3);
}
bool CheckPlan(FAutomationTestBase& T,const H::FDrawPlan& P,const FDungeonFighterOwnerSnapshot& Actual,const H::FDrawContext& C,int32 Frame)
{
 const auto& Source=H::Profile().Frames[Frame];const int32 Facing=Actual.Facing<0?-1:1;const double Scale=72./416.*C.UIScale;
 const auto& V=Source.Grip;const auto& R=Source.Root;const FVector2D Grip=C.GroundScreen+FVector2D(Facing*(V.X-R.X)*Scale,(V.Y-R.Y)*Scale-C.JumpHeight*.70*C.UIScale);
 const FVector2D Top=C.GroundScreen-FVector2D((Facing<0?512.-R.X:R.X)*Scale,R.Y*Scale+C.JumpHeight*.70*C.UIScale);
 const H::EComponent Order[]={H::EComponent::BodyRest,H::EComponent::ShoulderFar,H::EComponent::Chest,H::EComponent::NearArmWithoutHand,
  H::EComponent::ShoulderNear,H::EComponent::HelmetForeground,H::EComponent::FarHandForeground,H::EComponent::IndependentSword,H::EComponent::NearHand};
 bool Ok=P.Supported&&P.ProfileId==H::Profile().ProfileId&&P.Frame==Frame&&P.Facing==Facing&&P.Hurt.Active
  &&P.Hurt.Elapsed==Actual.AnimationTime&&P.Hurt.Remaining==Actual.HurtTime&&P.Binding.Armor==B::EArmor::LightArmor
  &&FMath::IsNearlyEqual(P.CanvasSize,72.*512./416.,1.e-10)&&FMath::IsNearlyEqual(P.SourceToScreenScale,Scale,1.e-12)&&P.WeaponScale==.5
  &&FMath::IsNearlyEqual(P.WeaponWidth,72.*512./416.*.5*C.UIScale,1.e-10)&&P.RootSource==Source.Root&&P.GripSource==Source.Grip
  &&P.AxisArtist==Source.AxisArtist&&P.GripScreen.Equals(Grip,1.e-7)&&P.BodyTop.Equals(Top,1.e-7)&&P.NonemptyDrawCount==(Frame==0?9:8);
 for(int32 I=0;I<9;++I)
 {
  const auto& Slot=P.Slots[I];Ok&=Slot.Component==Order[I];
  if(I==7){Ok&=Slot.TexturePath==H::Profile().SwordTexturePath&&!Slot.KnownOptionalEmpty;continue;}
  const auto L=std::find_if(Source.Layers.begin(),Source.Layers.end(),[&](const auto& X){return X.Component==Order[I];});
  Ok&=L!=Source.Layers.end()&&Slot.TexturePath==L->TexturePath&&Slot.KnownOptionalEmpty==L->KnownOptionalEmpty;
 }
 const double Angle=FMath::RadiansToDegrees(FMath::Atan2(Source.AxisArtist.Y,Source.AxisArtist.X))*(Facing<0?-1.:1.);
 const FVector2D Pivot(Facing<0?1.-99./512.:99./512.,256./512.);
 Ok&=FMath::IsNearlyEqual(P.WeaponAngle,Angle,1.e-10)&&P.SwordPivotUV==Pivot&&P.SwordTop.Equals(Grip-Pivot*P.WeaponWidth,1.e-7)
  &&P.TextureU==(Facing<0?1.:0.)&&P.TextureDU==(Facing<0?-1.:1.);
 return T.TestTrue(TEXT("Shared production plan uses exact source owners/order/optional empties, actual hurt age and one72scale/mirror/independent .50 sword"),Ok);
}
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FFairytaleHurtActualPhases,
 "CodexDungeon.Content.FairytaleSwordHurtV001.ActualPoiseBreakFourPhasesAndExclusions",EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FFairytaleHurtActualPhases::RunTest(const FString&)
{
 FHurtOptInScope Flags;FCodecWorld W(*this);if(!W.Create()||!EquipLight(W,TEXT("hurt.phases.light"))||!Prepared32Precondition(*this))return false;
 FDungeonRunSnapshot Actual;if(!TriggerRealHurt(W,Actual))return false;
 const uint64 Sword=W.Game->GetEquipmentView().Slots[W.Game->GetEquipmentView().ActiveSlot].InstanceId,Armor=W.Game->GetEquipmentView().Slots[2].InstanceId;
 // This actual native float counterexample runs even before the Stage0 target
 // failure. It uses an independent unbound Actor, never manual Tick on main Run.
 auto Legacy=W.World->SpawnActor<ADungeonFighter>();
 if(!TestNotNull(TEXT("PRECONDITION actual unbound Fighter exists for real four-Tick float counterexample"),Legacy))return false;
 const double LegacyMainTime=W.Game->GetSimulationTime();Legacy->ApplyCombatHit(5.f,nullptr,30.f);
 for(int32 I=0;I<4;++I)Legacy->Tick(.1f);
 AddInfo(FString::Printf(TEXT("Observed real legacy4Tick: age=%.9g label=%s CanStartAttack=%d mainSim=%.17g"),
  double(Legacy->AnimationTime),*Legacy->AnimationName,int32(Legacy->CanStartAttack()),W.Game->GetSimulationTime()));
 if(!TestTrue(TEXT("PRECONDITION real Actor .4f-minus-four-.1f ticks still hurt at .4f while main Run time is untouched"),
  Legacy->AnimationName==TEXT("hurt")&&Legacy->AnimationTime==.4f&&!Legacy->CanStartAttack()&&W.Game->GetSimulationTime()==LegacyMainTime))return false;
 FDungeonHurtPresentationSample Q;
 if(!TestTrue(TEXT("TARGET Stage0 RED: genuine Fighter exposes read-only active Hurt sample"),W.Player->QueryHurtPresentation(Q)))return false;
 for(int32 I=0;I<4;++I)
 {
  if(I){W.Frame(.1f);if(!CaptureActual(W,Actual,TEXT("Actual consecutive Hurt phase captures")))return false;}
  const auto& S=Actual.Fighters[0];if(!TestTrue(TEXT("Actual age lies in independently expected100ms phase, remaining is genuinely positive"),S.AnimationName==TEXT("hurt")&&S.HurtTime>0.f&&S.AnimationTime>=I*.1f&&S.AnimationTime<(I+1)*.1f))return false;
  const auto Before=CodecSignature(Actual);H::FDrawPlan Plan;FString Why;const auto C=ActualContext(W);
  if(!TestTrue(TEXT("TARGET real Hurt owner admits source4 shared draw plan"),W.Player->QueryHurtPresentation(Q)&&Q.Active&&Q.Elapsed==S.AnimationTime&&Q.Remaining==S.HurtTime
   &&H::BuildDrawPlan(*W.Game,*W.Player,C,Plan,Why)))return false;
  CheckPlan(*this,Plan,S,C,I);FDungeonRunSnapshot After;if(!CaptureActual(W,After,TEXT("Read-only Hurt plan retains capturable owner")))return false;
  TestTrue(TEXT("Repeated Hurt query/plan cannot alter any captured owner/resource/Run clock or equipment ID"),CodecSignature(After)==Before
   &&Plan.Binding.WeaponInstanceId==Sword&&Plan.Binding.ArmorInstanceId==Armor);
 }
 // Termination follows the actual float countdown, not an invented absolute .4double deadline.
 for(int32 N=0;N<40&&Actual.Fighters[0].HurtTime>0.f;++N){W.Frame(.02f);if(!CaptureActual(W,Actual,TEXT("Actual Hurt countdown termination captures")))return false;}
 auto Rejected=FDungeonHurtPresentationSample{true,7.f,6.f};const auto Bytes=HurtSignature(Rejected);
 TestTrue(TEXT("Actual zero remaining ends Hurt selection atomically without gameplay delay or loop"),Actual.Fighters[0].HurtTime==0.f&&Actual.Fighters[0].AnimationName!=TEXT("hurt")
  &&!W.Player->QueryHurtPresentation(Rejected)&&HurtSignature(Rejected)==Bytes);
 // Direct Actor Tick is a real supported legacy path, but never manually Tick
 // the bound main player. A separate unbound actual Fighter demonstrates float tail.
 const double MainTime=W.Game->GetSimulationTime(); // Legacy remains at the actual four-Tick state measured before Stage0 assertion.
 FDungeonHurtPresentationSample Tail;
 if(!TestTrue(TEXT("Actual .4f minus four real Actor .1f Ticks remains genuinely active at a tiny positive float tail"),
  Legacy->AnimationName==TEXT("hurt")&&Legacy->AnimationTime==.4f&&!Legacy->CanStartAttack()
  &&Legacy->QueryHurtPresentation(Tail)&&Tail.Active&&Tail.Elapsed==Legacy->AnimationTime&&Tail.Remaining>0.f&&Tail.Remaining<1.e-6f))return false;
 // Pure seam uses the unedited sample read from those real ticks, not a
 // manufactured .4double age. It cannot authorize Legacy as a World owner.
 B::FBinding TailBinding;FString TailWhy;H::FDrawPlan TailValue;
 if(!B::Resolve(*W.Game,*W.Player,TailBinding,TailWhy))return false;
 if(!TestTrue(TEXT("The same production value selector clamps an actually observed active float tail to phase3"),
  H::BuildDrawPlanFromCommitted(TailBinding,Tail,Legacy->Facing,H::Profile(),ActualContext(W),TailValue,TailWhy)
  &&TailValue.Supported&&TailValue.Frame==3&&TailValue.Hurt.Elapsed==Tail.Elapsed&&TailValue.Hurt.Remaining==Tail.Remaining))return false;
 auto TailPlan=SentinelPlan();const auto TailBytes=PlanSignature(TailPlan);
 TestTrue(TEXT("A real legacy Hurt query does not authorize that non-main Actor to use committed player gear"),
  !H::BuildDrawPlan(*W.Game,*Legacy,ActualContext(W),TailPlan,TailWhy)&&PlanSignature(TailPlan)==TailBytes);
 Legacy->Tick(.001f);Rejected={true,7.f,6.f};
 TestTrue(TEXT("Only the next real Actor Tick ends its actual float tail; no plan/query clock write touches main Run"),Legacy->AnimationName!=TEXT("hurt")
  &&Legacy->CanStartAttack()&&!Legacy->QueryHurtPresentation(Rejected)&&HurtSignature(Rejected)==Bytes&&W.Game->GetSimulationTime()==MainTime);

 FCodecWorld Central(*this);if(!Central.Create()||!EquipLight(Central,TEXT("hurt.central.float")))return false;
 const double CentralHitTime=Central.Game->GetSimulationTime();Central.Player->ApplyCombatHit(5.f,nullptr,30.f);
 FDungeonRunSnapshot CentralActual;
 for(int32 I=0;I<4;++I)
 {
  Central.Frame(.1f);if(!CaptureActual(Central,CentralActual,TEXT("Actual central GameMode100ms outer-frame state captures")))return false;
  const auto& S=CentralActual.Fighters[0];FDungeonHurtPresentationSample CQ;H::FDrawPlan CP;FString CW;
  AddInfo(FString::Printf(TEXT("Actual central outerFrame=%d elapsedSim=%.17g AnimationTime=%.9g HurtRemaining=%.9g label=%s; GameMode subdivides<=5ms and native Hurt boundary"),
   I+1,Central.Game->GetSimulationTime()-CentralHitTime,double(S.AnimationTime),double(S.HurtTime),*S.AnimationName));
  if(S.HurtTime>0.f)
  {
   if(!TestTrue(TEXT("Any truly active central float tail stays frame3 instead of premature bareReady0"),Central.Player->QueryHurtPresentation(CQ)
    &&CQ.Elapsed==S.AnimationTime&&CQ.Remaining==S.HurtTime&&H::BuildDrawPlan(*Central.Game,*Central.Player,ActualContext(Central),CP,CW)))return false;
   CheckPlan(*this,CP,S,ActualContext(Central),FMath::Clamp(int32(std::floor(double(S.AnimationTime)/.1)),0,3));
  }
  else TestTrue(TEXT("Actual central end, rather than nominal .4double alone, excludes Hurt"),S.AnimationName!=TEXT("hurt")&&!Central.Player->QueryHurtPresentation(CQ));
 }
 FCodecWorld Small(*this);if(!Small.Create()||!EquipLight(Small,TEXT("hurt.small.light")))return false;
 Small.Player->ApplyCombatHit(1.f,nullptr,1.f);Small.Frame(.02f);FDungeonRunSnapshot SmallActual;if(!CaptureActual(Small,SmallActual,TEXT("Actual non-breaking positive hit captures")))return false;
 TestTrue(TEXT("Positive HP loss without actual poise break is not a Hurt pose"),SmallActual.Fighters[0].Health<100.f&&SmallActual.Fighters[0].HurtTime==0.f
  &&!Small.Player->QueryHurtPresentation(Rejected)&&HurtSignature(Rejected)==Bytes);
 FCodecWorld Dead(*this);if(!Dead.Create()||!EquipLight(Dead,TEXT("hurt.dead.light")))return false;
 Dead.Player->ApplyCombatHit(100000.f,nullptr,30.f);Dead.Frame(.02f);
 TestTrue(TEXT("True lethal hit chooses Death and cannot authorize Hurt"),Dead.Player->bDead&&Dead.Game->bGameOver&&Dead.Player->AnimationName==TEXT("death")
  &&!Dead.Player->QueryHurtPresentation(Rejected)&&HurtSignature(Rejected)==Bytes);
 return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FFairytaleHurtSourceAdmission,
 "CodexDungeon.Content.FairytaleSwordHurtV001.RealBindingSource32MirrorAndAtomicRejection",EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FFairytaleHurtSourceAdmission::RunTest(const FString&)
{
 FHurtOptInScope Flags;if(!Prepared32Precondition(*this))return false;
 for(int32 Facing:{-1,1})
 {
  FCodecWorld W(*this);if(!W.Create()||!EquipLight(W,Facing<0?TEXT("hurt.mirror.left"):TEXT("hurt.mirror.right")))return false;
  const auto K=Facing<0?EKeys::A:EKeys::D;if(!W.Key(K,true))return false;W.Frame(.01f);if(!W.Key(K,false))return false;W.Frame(.005f);
  if(!TestTrue(TEXT("PRECONDITION actual ordinary input establishes requested player facing"),W.Player->Facing==float(Facing)))return false;
  FDungeonRunSnapshot Actual;if(!TriggerRealHurt(W,Actual))return false;
  auto P=SentinelPlan();FString Why;const auto C=ActualContext(W);
  if(!TestTrue(TEXT("TARGET Stage0 RED: actual committed SWD/LGT Hurt admits the complete source32 plan"),H::BuildDrawPlan(*W.Game,*W.Player,C,P,Why)))return false;
  CheckPlan(*this,P,Actual.Fighters[0],C,0);B::FBinding Binding;if(!B::Resolve(*W.Game,*W.Player,Binding,Why))return false;
  FDungeonHurtPresentationSample Sample;if(!W.Player->QueryHurtPresentation(Sample))return false;
  const auto Reject=[&](const TCHAR* Label,auto Alter)
  {
   auto Bad=H::Profile();Alter(Bad);auto Out=SentinelPlan();const auto Bytes=PlanSignature(Out);const auto Before=CodecSignature(Actual);FString Diagnostic;
   TestTrue(Label,!H::BuildDrawPlanFromCommitted(Binding,Sample,Actual.Fighters[0].Facing,Bad,C,Out,Diagnostic)&&!Diagnostic.IsEmpty()&&PlanSignature(Out)==Bytes);
   FDungeonRunSnapshot After;if(CaptureActual(W,After,TEXT("Rejected profile preserves actual Run")))TestTrue(TEXT("Negative value-seam profile cannot mutate native live owners"),CodecSignature(After)==Before);
  };
  Reject(TEXT("Missing mandatory Chest refuses atomically"),[](auto& X){X.Frames[0].Layers[2].TexturePath.Reset();});
  Reject(TEXT("Frame0 far fist cannot masquerade as optional empty"),[](auto& X){X.Frames[0].Layers[6].KnownOptionalEmpty=true;});
  Reject(TEXT("A missing optional-empty texture still refuses complete source closure"),[](auto& X){X.Frames[1].Layers[6].TexturePath.Reset();});
  Reject(TEXT("Zero artist axis cannot invent a held sword direction"),[](auto& X){X.Frames[0].AxisArtist=FVector2D::ZeroVector;});
  Reject(TEXT("Unclosed source contract cannot authorize any layer"),[](auto& X){X.SourceClosureVerified=false;});
  auto Wrong=Binding;Wrong.Armor=B::EArmor::NoArmor;Wrong.ArmorInstanceId=0;Wrong.ArmorVersion=0;Wrong.ArmorContentId.Reset();auto Out=SentinelPlan();const auto Bytes=PlanSignature(Out);
  TestTrue(TEXT("No-armor committed value cannot receive this explicitly SWD+LGT-only Hurt profile"),!H::BuildDrawPlanFromCommitted(Wrong,Sample,Actual.Fighters[0].Facing,H::Profile(),C,Out,Why)&&PlanSignature(Out)==Bytes);
 }
 FCodecWorld Other(*this);if(!Other.Create())return false;IV::FItem Medium;Medium.ContentId="ARM-MED-001";
 const auto M=Other.Game->RegisterEquipmentSource(TEXT("hurt.actual.medium"),Medium,Other.Player->GetGroundPosition()+FVector2D(24,0),true);
 if(!TestTrue(TEXT("PRECONDITION unsupported armor is genuinely acquired through the existing transaction"),M.Ok()&&Other.Game->SelectEquipmentSource(M.SourceId)))return false;
 Other.Game->TryInteractEquipment();if(!TestTrue(TEXT("PRECONDITION actual MED transaction commits legally"),Other.Game->GetEquipmentView().Action.Active
  &&Other.AdvanceTo(Other.Player->GetEquipmentActionDeadline())&&Other.Player->ArmorId==TEXT("ARM-MED-001")))return false;
 Other.Player->ApplyCombatHit(5.f,nullptr,Other.Player->GetPoiseThreshold());Other.Frame(.02f);FDungeonRunSnapshot Before;if(!CaptureActual(Other,Before,TEXT("Actual MED Hurt captures")))return false;
 auto Out=SentinelPlan();const auto Bytes=PlanSignature(Out);FString Why;
 TestTrue(TEXT("Actually committed MED cannot draw SWD+LGT Hurt or partially publish a plan"),!H::BuildDrawPlan(*Other.Game,*Other.Player,ActualContext(Other),Out,Why)&&!Why.IsEmpty()&&PlanSignature(Out)==Bytes);
 FDungeonRunSnapshot After;if(CaptureActual(Other,After,TEXT("Wrong equipment rejection stays capturable")))TestTrue(TEXT("Unsupported real gear rejection is read-only"),CodecSignature(Before)==CodecSignature(After));
 return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FFairytaleHurtPausedContinuation,
 "CodexDungeon.Content.FairytaleSwordHurtV001.RealCodecPauseContinueKeepsAgeAndEquipment",EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FFairytaleHurtPausedContinuation::RunTest(const FString&)
{
 FHurtOptInScope Flags;FCodecWorld Source(*this);if(!Source.Create()||!EquipLight(Source,TEXT("hurt.pause.light"))||!Prepared32Precondition(*this))return false;
 FDungeonRunSnapshot Initial;if(!TriggerRealHurt(Source,Initial))return false;Source.Frame(.13f);
 FDungeonRunSnapshot Saved;if(!CaptureActual(Source,Saved,TEXT("PRECONDITION actual mid-Hurt complete Run captures")))return false;
 const auto& Owner=Saved.Fighters[0];if(!TestTrue(TEXT("PRECONDITION saved native hurt is genuinely in phase1 with positive remaining"),Owner.AnimationName==TEXT("hurt")&&Owner.HurtTime>0.f&&Owner.AnimationTime>=.1f&&Owner.AnimationTime<.2f))return false;
 TArray<uint8> Encoded;FDungeonValidatedRun Decoded;FString Why;
 if(!TestTrue(TEXT("PRECONDITION unchanged real codec preserves actual HurtTime/AnimationTime exactly"),DungeonRunSnapshotCodec::Encode(Saved,Encoded,Why)
  &&DungeonRunSnapshotCodec::Decode(Encoded,Decoded,Why)&&Decoded.IsValid()&&Decoded.Get()->Fighters[0].HurtTime==Owner.HurtTime
  &&Decoded.Get()->Fighters[0].AnimationTime==Owner.AnimationTime))return false;
 FCodecWorld Target(*this);if(!Target.Create())return false;FDungeonPreparedRun Prepared;
 if(!TestTrue(TEXT("PRECONDITION actual grouped Prepare/Install accepts saved Hurt without forged owners"),FDungeonRunInstaller::Prepare(*Target.Game,Decoded,Prepared,Why)
  &&Prepared.IsReady()&&FDungeonRunInstaller::Install(*Target.Game,Prepared,Why)))return false;
 Target.Player=Target.Game->PlayerFighter;Target.Frame(.25f);FDungeonRunSnapshot Paused;
 if(!CaptureActual(Target,Paused,TEXT("PRECONDITION actual installed Hurt remains capturable while paused")))return false;
 if(!TestTrue(TEXT("PRECONDITION Continue gate is truly closed and all saved values stay exact despite real paused ticks"),Target.Game->GetRunInstallGate()==EDungeonRunInstallGate::AwaitExplicitContinue
  &&CodecSignature(Paused)==CodecSignature(Saved)&&Target.Controller->GetPawn()==Target.Player))return false;
 H::FDrawPlan P;
 if(!TestTrue(TEXT("TARGET Stage0 RED: already-published paused real Hurt draws its saved phase and committed gear without advancing"),H::BuildDrawPlan(*Target.Game,*Target.Player,ActualContext(Target),P,Why)))return false;
 CheckPlan(*this,P,Paused.Fighters[0],ActualContext(Target),1);FDungeonRunSnapshot Still;if(!CaptureActual(Target,Still,TEXT("Paused read-only plan captures")))return false;
 TestTrue(TEXT("Paused Hurt presentation cannot open Continue, rewind age or replace equipped instances"),CodecSignature(Still)==CodecSignature(Saved)
  &&P.Binding.WeaponInstanceId==Saved.Equipment.View.Slots[Saved.Equipment.View.ActiveSlot].InstanceId&&P.Binding.ArmorInstanceId==Saved.Equipment.View.Slots[2].InstanceId);
 Target.Frame(.005f);if(!Target.Key(EKeys::Enter,true))return false;Target.Frame(.005f);
 if(!TestTrue(TEXT("Fresh actual Enter opens existing Continue gate without consuming hurt time at gate boundary"),Target.Game->GetRunInstallGate()==EDungeonRunInstallGate::Open
  &&Target.Player->AnimationTime==Owner.AnimationTime))return false;
 if(!Target.Key(EKeys::Enter,false))return false;Target.Frame(.02f);FDungeonRunSnapshot Continued;if(!CaptureActual(Target,Continued,TEXT("Actual continued Hurt captures")))return false;
 if(!TestTrue(TEXT("Native action batch resumes actual saved age/remaining, never restarts Hurt0"),Continued.Fighters[0].AnimationTime>Owner.AnimationTime
  &&Continued.Fighters[0].HurtTime>0.f&&Continued.Fighters[0].HurtTime<Owner.HurtTime&&H::BuildDrawPlan(*Target.Game,*Target.Player,ActualContext(Target),P,Why)))return false;
 CheckPlan(*this,P,Continued.Fighters[0],ActualContext(Target),1);
 TestTrue(TEXT("Continuation preserves committed native equipment identity"),P.Binding.WeaponInstanceId==Saved.Equipment.View.Slots[Saved.Equipment.View.ActiveSlot].InstanceId
  &&P.Binding.ArmorInstanceId==Saved.Equipment.View.Slots[2].InstanceId);
 return true;
}
#endif
