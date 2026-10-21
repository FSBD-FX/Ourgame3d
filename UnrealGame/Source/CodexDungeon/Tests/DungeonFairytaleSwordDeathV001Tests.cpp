#if WITH_DEV_AUTOMATION_TESTS
#include "Misc/AutomationTest.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
#include "../DungeonFairytaleSwordDeathPlan.h"
#include "../DungeonRunInstaller.h"
#include "../DungeonRunSnapshotCodec.h"
#include "RunCodecFixture_v001.h"
#include <algorithm>

namespace
{
namespace D=DungeonFairytaleSwordDeathV001;
namespace B=DungeonFairytaleSwordEquipmentBinding;
struct FDeathOptInScope
{
 const FString Original=FCommandLine::Get();
 FDeathOptInScope()
 {
  FString Next=Original;
  for(const TCHAR* Flag:{B::CommandLineFlag,D::CommandLineFlag})
   if(!FParse::Param(*Next,Flag))Next+=FString(TEXT(" -"))+Flag;
  FCommandLine::Set(*Next);
 }
 ~FDeathOptInScope(){FCommandLine::Set(*Original);}
};
bool AcquireArmor(FCodecWorld& W,const TCHAR* Key,const char* Content)
{
 IV::FItem Item;Item.ContentId=Content;
 const auto R=W.Game->RegisterEquipmentSource(Key,Item,W.Player->GetGroundPosition()+FVector2D(24,0),true);
 if(!W.Test.TestTrue(TEXT("PRECONDITION real armor source is selected through existing transaction"),R.Ok()&&W.Game->SelectEquipmentSource(R.SourceId)))return false;
 W.Game->TryInteractEquipment();const auto A=W.Game->GetEquipmentView().Action;
 return W.Test.TestTrue(TEXT("PRECONDITION actual armor pickup commits at its original deadline"),A.Active&&A.InstanceId==R.InstanceId
  &&A.Deadline==W.Game->GetSimulationTime()+.5&&W.AdvanceTo(A.Deadline)
  &&W.Game->GetEquipmentView().Slots[2].InstanceId==R.InstanceId&&W.Player->ArmorId==UTF8_TO_TCHAR(Content));
}
bool CaptureActual(FCodecWorld& W,FDungeonRunSnapshot& Out,const TCHAR* Label)
{
 FString Why;const bool OK=W.Game->CaptureRunSnapshot(Out,Why);
 if(!OK)W.Test.AddInfo(FString(Label)+TEXT(" capture diagnosis: ")+Why);
 return W.Test.TestTrue(Label,OK&&!Out.Fighters.IsEmpty());
}
bool Fatal(FCodecWorld& W,FDungeonRunSnapshot& Out)
{
 W.Player->ApplyCombatHit(100000.f,nullptr,0.f);W.Frame(.01f);
 if(!CaptureActual(W,Out,TEXT("PRECONDITION genuinely dead main owner remains capturable")))return false;
 const auto& S=Out.Fighters[0];
 return W.Test.TestTrue(TEXT("PRECONDITION actual fatal damage already committed HP0/Death/GameOver/once report, with genuine residual Hurt and HitFlash"),
  S.Health==0.f&&S.Dead&&S.DeathReported&&Out.GameOver&&S.AnimationName==TEXT("death")
  &&S.AnimationTime>0.f&&S.AnimationTime<.2f&&S.HurtTime>0.f&&S.HitFlash>0.f
  &&!W.Player->GetMeleeCombatState().Action.Active&&W.Player->GetMeleeCombatState().Dead
  &&W.Player->GetWeaponActionsState().Budget.Dead&&W.Player->GetDodgeState().Phase==DK::EPhase::Dead);
}
D::FDrawContext ActualContext(const FCodecWorld& W)
{
 D::FDrawContext C;const auto P=W.Player->GetGroundPosition(),Camera=W.HUD->GetCameraGroundCenter();
 C.GroundScreen={640.+(P.X-Camera.X)*.65,490.-P.Y*.38};C.UIScale=1.;C.JumpHeight=W.Player->JumpHeight;return C;
}
TArray<uint8> SampleSignature(const FDungeonDeathPresentationSample& Q)
{FSignature S;S.V(Q.Active,Q.Dead,Q.DeathReported,Q.Health,Q.Elapsed);S.String(Q.AnimationName);return S.Bytes;}
TArray<uint8> PlanSignature(const D::FDrawPlan& P)
{
 FSignature S;S.V(P.Supported,P.VisualSwordReleased,P.LastFrameHeld,P.Frame,P.Facing,P.NonemptyDrawCount,
  P.CanvasSize,P.SourceToScreenScale,P.WeaponScale,P.WeaponWidth,P.WeaponAngle,P.TextureU,P.TextureDU,
  P.Tint.R,P.Tint.G,P.Tint.B,P.Tint.A);S.String(P.ProfileId);
 S.Bytes.Append(SampleSignature(P.Death));
 S.V(P.Binding.RunGuid.A,P.Binding.RunGuid.B,P.Binding.RunGuid.C,P.Binding.RunGuid.D,P.Binding.RunAlias,
  P.Binding.OwnerId,P.Binding.Revision,P.Binding.ActiveSlot,P.Binding.WeaponInstanceId,P.Binding.WeaponVersion,
  P.Binding.ArmorInstanceId,P.Binding.ArmorVersion,P.Binding.Armor);
 S.String(P.Binding.WeaponContentId);S.String(P.Binding.ArmorContentId);
 for(auto V:{P.RootSource,P.SwordAnchorSource,P.AxisArtist,P.BodyTop,P.SwordAnchorScreen,P.SwordTop,P.SwordPivotUV})S.Point(V);
 for(const auto& Slot:P.Slots){S.V(Slot.Component,Slot.KnownOptionalEmpty);S.String(Slot.TexturePath);}return S.Bytes;
}
D::FDrawPlan SentinelPlan()
{
 D::FDrawPlan P;P.Supported=true;P.Frame=93;P.Facing=17;P.ProfileId=TEXT("sentinel.death");P.Binding.OwnerId=995;
 P.Death={true,true,true,7.f,8.f,TEXT("sentinel")};P.RootSource={71,72};P.SwordAnchorScreen={73,74};
 P.CanvasSize=75.;P.WeaponScale=76.;P.Slots[0].TexturePath=TEXT("sentinel.texture");return P;
}
bool Source40(FAutomationTestBase& T)
{
 const auto& P=D::Profile();TSet<FString> Paths;
 bool OK=P.SourceClosureVerified&&P.SourceClosureSHA256==TEXT("5f6506b609440d8cfda40b493b7ce9b23131b0f83aa09add333f8d8e74ef788c")
  &&P.Frames.size()==5&&P.CanvasSource==512&&P.StandingExtent==416.&&P.StandingDisplay==72.&&P.WeaponScale==.5;
 for(const auto& F:P.Frames)for(const auto& L:F.Layers)
 {
  OK&=!L.TexturePath.IsEmpty()&&!Paths.Contains(L.TexturePath)&&L.TexturePath.StartsWith(TEXT("/Game/Production/ArtTrials/EV048/v019/HeroLeatherDeath/"))
   &&L.SourceSHA256.Len()==64&&L.SourceRGBASHA256.Len()==64&&L.SourceAlphaNonzero>0&&!L.KnownOptionalEmpty;
  Paths.Add(L.TexturePath);
 }
 return T.TestTrue(TEXT("PRECONDITION exact retained E505 source closure has40 distinct ownBody/LGT textures, with independent sword reused"),OK&&Paths.Num()==40
  &&P.SwordTexturePath==TEXT("/Game/Production/FirstBatch/v002/CandidateComponents/T_military_sword_v002.T_military_sword_v002"));
}
bool CheckPlan(FAutomationTestBase& T,const D::FDrawPlan& P,const FDungeonFighterOwnerSnapshot& Actual,const D::FDrawContext& C,int32 Frame)
{
 // Literal artist release-v002 points independently copied from the approved source contract.
 const FVector2D Anchor[]={FVector2D(183,311),FVector2D(296,430),FVector2D(480,442),FVector2D(480,442),FVector2D(480,442)};
 const int32 Facing=Actual.Facing<0?-1:1;const double Scale=72./416.*C.UIScale;const FVector2D Root(242,464);
 const auto AnchorScreen=C.GroundScreen+FVector2D(Facing*(Anchor[Frame].X-Root.X)*Scale,(Anchor[Frame].Y-Root.Y)*Scale-C.JumpHeight*.70*C.UIScale);
 const auto Top=C.GroundScreen-FVector2D((Facing<0?270.:242.)*Scale,464.*Scale+C.JumpHeight*.70*C.UIScale);
 const D::EComponent Held[]={D::EComponent::BodyRest,D::EComponent::ShoulderFar,D::EComponent::Chest,D::EComponent::NearArmWithoutHand,
  D::EComponent::ShoulderNear,D::EComponent::HelmetForeground,D::EComponent::FarHandForeground,D::EComponent::IndependentSword,D::EComponent::NearHand};
 const D::EComponent Released[]={D::EComponent::IndependentSword,D::EComponent::BodyRest,D::EComponent::ShoulderFar,D::EComponent::Chest,
  D::EComponent::NearArmWithoutHand,D::EComponent::ShoulderNear,D::EComponent::HelmetForeground,D::EComponent::FarHandForeground,D::EComponent::NearHand};
 bool OK=P.Supported&&P.Frame==Frame&&P.Facing==Facing&&P.Death.Active&&P.Death.Dead&&P.Death.Health==0.f
  &&P.Death.AnimationName==TEXT("death")&&P.Death.Elapsed==Actual.AnimationTime&&P.Death.DeathReported==Actual.DeathReported
  &&P.Binding.Armor==B::EArmor::LightArmor&&P.VisualSwordReleased==(Frame>0)&&P.LastFrameHeld==(Frame==4)
  &&P.RootSource==Root&&P.SwordAnchorSource==Anchor[Frame]&&P.BodyTop.Equals(Top,1.e-7)&&P.SwordAnchorScreen.Equals(AnchorScreen,1.e-7)
  &&FMath::IsNearlyEqual(P.CanvasSize,72.*512./416.,1.e-10)&&FMath::IsNearlyEqual(P.SourceToScreenScale,Scale,1.e-12)
  &&P.WeaponScale==.5&&FMath::IsNearlyEqual(P.WeaponWidth,72.*512./416.*.5*C.UIScale,1.e-10)&&P.NonemptyDrawCount==9
  &&P.TextureU==(Facing<0?1.:0.)&&P.TextureDU==(Facing<0?-1.:1.)&&P.Tint==FLinearColor::White;
 const FVector2D Pivot(Facing<0?1.-99./512.:99./512.,256./512.);
 OK&=P.SwordPivotUV==Pivot&&P.SwordTop.Equals(AnchorScreen-Pivot*P.WeaponWidth,1.e-7)
  &&FMath::IsNearlyEqual(P.WeaponAngle,(Frame==0?-20.:0.)*(Facing<0?-1.:1.),1.e-10);
 for(int32 I=0;I<9;++I)
 {
  const auto Expected=Frame==0?Held[I]:Released[I];const auto& Slot=P.Slots[I];OK&=Slot.Component==Expected&&!Slot.KnownOptionalEmpty;
  if(Expected==D::EComponent::IndependentSword)OK&=Slot.TexturePath==D::Profile().SwordTexturePath;
  else
  {
   const auto& Layers=D::Profile().Frames[Frame].Layers;const auto L=std::find_if(Layers.begin(),Layers.end(),[&](const auto& X){return X.Component==Expected;});
   OK&=L!=Layers.end()&&Slot.TexturePath==L->TexturePath;
  }
 }
 return T.TestTrue(TEXT("Actual terminal age selects own Death row with constant body72, LGT, dynamic9slot release order, white material and one .50 mirror"),OK);
}
bool FrozenExceptDisplay(const FDungeonRunSnapshot& Before,FDungeonRunSnapshot After)
{
 // Expected delta is limited to the two pre-existing terminal display fields.
 After.Fighters[0].AnimationTime=Before.Fighters[0].AnimationTime;After.Fighters[0].JumpHeight=Before.Fighters[0].JumpHeight;
 return CodecSignature(Before)==CodecSignature(After);
}
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FFairytaleDeathActual,
 "CodexDungeon.Content.FairytaleSwordDeathV001.ActualFatalTerminalFivePhasesAndExclusions",EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FFairytaleDeathActual::RunTest(const FString&)
{
 FDeathOptInScope Flags;FCodecWorld W(*this);if(!W.Create()||!AcquireArmor(W,TEXT("death.actual.light"),"ARM-LGT-001")||!Source40(*this))return false;
 if(!TestTrue(TEXT("PRECONDITION normal Space and J establish genuine airborne primary before lethal interruption"),W.Pulse(EKeys::SpaceBar)
  &&W.Player->JumpHeight>0.f&&W.Pulse(EKeys::J)&&W.Player->GetMeleeCombatState().Action.Active))return false;
 FDungeonRunSnapshot Actual;if(!Fatal(W,Actual))return false;const auto Initial=Actual;
 FDungeonDeathPresentationSample Q;
 if(!TestTrue(TEXT("TARGET Stage0 RED: genuine dead Fighter exposes its original terminal display sample despite residual Hurt and jump"),W.Player->QueryDeathPresentation(Q)))return false;
 for(int32 I=0;I<5;++I)
 {
  if(I){W.Frame(.21f);if(!CaptureActual(W,Actual,TEXT("Actual terminal consecutive phase captures")))return false;}
  const auto& S=Actual.Fighters[0];
  if(!TestTrue(TEXT("Real terminal age lies in independent200ms half-open phase while master/kernels/inventory/loot stay frozen"),
   S.AnimationTime>=I*.2f&&(I==4||S.AnimationTime<(I+1)*.2f)&&FrozenExceptDisplay(Initial,Actual)))return false;
  const auto Before=CodecSignature(Actual);D::FDrawPlan P;FString Why;
  if(!TestTrue(TEXT("Actual Death query and same production plan remain available after simulation clock stops"),W.Player->QueryDeathPresentation(Q)
   &&D::BuildDrawPlan(*W.Game,*W.Player,ActualContext(W),P,Why)))return false;
  CheckPlan(*this,P,S,ActualContext(W),I);FDungeonRunSnapshot After;
  if(CaptureActual(W,After,TEXT("Read-only terminal plan leaves the actual Run capturable")))TestTrue(TEXT("Query/plan never advances clock, awards, drops or consumes equipment"),CodecSignature(After)==Before);
 }
 W.Frame(2.f);FDungeonRunSnapshot Held;if(!CaptureActual(W,Held,TEXT("Real terminal final hold captures")))return false;
 D::FDrawPlan P;FString Why;
 TestTrue(TEXT("Death4 remains indefinitely while native dead and GameOver remain; persistent HitFlash cannot color Death red"),
  Held.Fighters[0].AnimationTime>2.f&&Held.Fighters[0].HitFlash==Initial.Fighters[0].HitFlash&&FrozenExceptDisplay(Initial,Held)
  &&D::BuildDrawPlan(*W.Game,*W.Player,ActualContext(W),P,Why)&&P.Frame==4&&P.LastFrameHeld&&P.Tint==FLinearColor::White);
 FCodecWorld Live(*this);if(!Live.Create())return false;auto Rejected=FDungeonDeathPresentationSample{true,true,true,7.f,8.f,TEXT("sentinel")};const auto Bytes=SampleSignature(Rejected);
 Live.Player->ApplyCombatHit(1.f,nullptr,0.f);Live.Frame(.02f);
 TestTrue(TEXT("Actual living positive HP loss is not Death and query failure is atomic"),!Live.Player->bDead
  &&!Live.Player->QueryDeathPresentation(Rejected)&&SampleSignature(Rejected)==Bytes);
 return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FFairytaleDeathSource,
 "CodexDungeon.Content.FairytaleSwordDeathV001.RealBindingSource40MirrorAndAtomicRejection",EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FFairytaleDeathSource::RunTest(const FString&)
{
 FDeathOptInScope Flags;if(!Source40(*this))return false;
 for(int32 Facing:{-1,1})
 {
  FCodecWorld W(*this);if(!W.Create()||!AcquireArmor(W,TEXT("death.mirror.light"),"ARM-LGT-001"))return false;
  if(!W.Key(Facing<0?EKeys::A:EKeys::D,true))return false;W.Frame(.01f);if(!W.Key(Facing<0?EKeys::A:EKeys::D,false))return false;W.Frame(.005f);
  if(!TestTrue(TEXT("PRECONDITION actual normal input establishes mirror facing"),W.Player->Facing==float(Facing)))return false;
  FDungeonRunSnapshot Actual;if(!Fatal(W,Actual))return false;auto P=SentinelPlan();FString Why;
  if(!TestTrue(TEXT("TARGET Stage0 RED: actual committed dead SWD/LGT admits complete source40 plan"),D::BuildDrawPlan(*W.Game,*W.Player,ActualContext(W),P,Why)))return false;
  CheckPlan(*this,P,Actual.Fighters[0],ActualContext(W),0);
  W.Frame(.21f);if(!CaptureActual(W,Actual,TEXT("Actual released-sword frame1 captures")))return false;
  if(!TestTrue(TEXT("Actual next terminal frame uses release-v002 rather than held Sword layer"),D::BuildDrawPlan(*W.Game,*W.Player,ActualContext(W),P,Why)))return false;
  CheckPlan(*this,P,Actual.Fighters[0],ActualContext(W),1);
  B::FBinding Binding;FDungeonDeathPresentationSample Q;if(!B::Resolve(*W.Game,*W.Player,Binding,Why)||!W.Player->QueryDeathPresentation(Q))return false;
  const auto Reject=[&](const TCHAR* Label,auto Alter)
  {
   auto Bad=D::Profile();Alter(Bad);auto Out=SentinelPlan();const auto Bytes=PlanSignature(Out);const auto Before=CodecSignature(Actual);FString Diagnostic;
   TestTrue(Label,!D::BuildDrawPlanFromCommitted(Binding,Q,Actual.Fighters[0].Facing,Bad,ActualContext(W),Out,Diagnostic)&&!Diagnostic.IsEmpty()&&PlanSignature(Out)==Bytes);
   FDungeonRunSnapshot After;if(CaptureActual(W,After,TEXT("Rejected source profile preserves actual Run")))TestTrue(TEXT("Bad source cannot alter any native owner"),CodecSignature(After)==Before);
  };
  Reject(TEXT("Missing later frame4 Chest rejects whole source40 atomically even while drawing frame1"),[](auto& X){X.Frames[4].Layers[2].TexturePath.Reset();});
  Reject(TEXT("Released frame cannot duplicate Sword and silently discard a body owner"),[](auto& X){X.Frames[1].SlotOrder[1]=D::EComponent::IndependentSword;});
  Reject(TEXT("Real nonempty body layer cannot masquerade as an optional transparent layer"),[](auto& X){X.Frames[1].Layers[6].KnownOptionalEmpty=true;});
  Reject(TEXT("Zero author sword axis cannot invent a release transform"),[](auto& X){X.Frames[0].AxisArtist=FVector2D::ZeroVector;});
  Reject(TEXT("Unclosed source profile cannot authorize partial drawing"),[](auto& X){X.SourceClosureVerified=false;});
  auto Legacy=W.World->SpawnActor<ADungeonFighter>();if(!TestNotNull(TEXT("PRECONDITION different actual Fighter exists"),Legacy))return false;
  Legacy->ApplyCombatHit(100000.f,nullptr,0.f);auto Out=SentinelPlan();const auto Bytes=PlanSignature(Out);
  TestTrue(TEXT("A different actual dead Actor cannot borrow committed main-player gear"),!D::BuildDrawPlan(*W.Game,*Legacy,ActualContext(W),Out,Why)&&PlanSignature(Out)==Bytes);
 }
 FCodecWorld Other(*this);if(!Other.Create()||!AcquireArmor(Other,TEXT("death.actual.medium"),"ARM-MED-001"))return false;
 FDungeonRunSnapshot Actual;if(!Fatal(Other,Actual))return false;auto Out=SentinelPlan();const auto Bytes=PlanSignature(Out);FString Why;
 TestTrue(TEXT("Actually committed MED is unsupported and cannot publish this LGT-only Death plan"),!D::BuildDrawPlan(*Other.Game,*Other.Player,ActualContext(Other),Out,Why)
  &&!Why.IsEmpty()&&PlanSignature(Out)==Bytes);
 return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FFairytaleDeathContinue,
 "CodexDungeon.Content.FairytaleSwordDeathV001.RealCodecPauseContinueKeepsTerminalAgeAndEquipment",EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FFairytaleDeathContinue::RunTest(const FString&)
{
 FDeathOptInScope Flags;FCodecWorld Source(*this);if(!Source.Create()||!AcquireArmor(Source,TEXT("death.pause.light"),"ARM-LGT-001")||!Source40(*this))return false;
 FDungeonRunSnapshot Initial;if(!Fatal(Source,Initial))return false;Source.Frame(.43f);
 FDungeonRunSnapshot Saved;if(!CaptureActual(Source,Saved,TEXT("PRECONDITION actual dead phase2 Run captures")))return false;
 const auto& Owner=Saved.Fighters[0];if(!TestTrue(TEXT("PRECONDITION terminal age progressed into phase2 while master and all authority froze"),Owner.AnimationTime>=.4f&&Owner.AnimationTime<.6f
  &&Saved.GameOver&&FrozenExceptDisplay(Initial,Saved)))return false;
 TArray<uint8> Encoded;FDungeonValidatedRun Decoded;FString Why;
 if(!TestTrue(TEXT("PRECONDITION unchanged native codec preserves terminal age/GameOver/committed gear"),DungeonRunSnapshotCodec::Encode(Saved,Encoded,Why)
  &&DungeonRunSnapshotCodec::Decode(Encoded,Decoded,Why)&&Decoded.IsValid()&&Decoded.Get()->Fighters[0].AnimationTime==Owner.AnimationTime))return false;
 FCodecWorld Target(*this);if(!Target.Create())return false;FDungeonPreparedRun Prepared;
 if(!TestTrue(TEXT("PRECONDITION genuine grouped installer accepts saved dead owners without reset"),FDungeonRunInstaller::Prepare(*Target.Game,Decoded,Prepared,Why)
  &&Prepared.IsReady()&&FDungeonRunInstaller::Install(*Target.Game,Prepared,Why)))return false;
 Target.Player=Target.Game->PlayerFighter;Target.Frame(.3f);FDungeonRunSnapshot Paused;
 if(!CaptureActual(Target,Paused,TEXT("PRECONDITION actual installed dead Run captures while paused")))return false;
 if(!TestTrue(TEXT("PRECONDITION real Continue gate holds complete saved dead state despite paused ticks"),Target.Game->GetRunInstallGate()==EDungeonRunInstallGate::AwaitExplicitContinue
  &&CodecSignature(Paused)==CodecSignature(Saved)))return false;
 D::FDrawPlan P;
 if(!TestTrue(TEXT("TARGET Stage0 RED: published paused dead player draws original phase2 and original equipment without opening Continue"),D::BuildDrawPlan(*Target.Game,*Target.Player,ActualContext(Target),P,Why)))return false;
 CheckPlan(*this,P,Paused.Fighters[0],ActualContext(Target),2);
 FDungeonRunSnapshot Still;if(!CaptureActual(Target,Still,TEXT("Paused Death planning is read-only")))return false;
 TestTrue(TEXT("Death renderer cannot consume Continue or modify frozen native owners"),CodecSignature(Still)==CodecSignature(Saved));
 if(!Target.Key(EKeys::Enter,true))return false;Target.Frame(.005f);
 if(!TestTrue(TEXT("Real fresh Enter opens existing gate without consuming terminal age at boundary"),Target.Game->GetRunInstallGate()==EDungeonRunInstallGate::Open
  &&Target.Player->AnimationTime==Owner.AnimationTime))return false;
 if(!Target.Key(EKeys::Enter,false))return false;Target.Frame(.21f);FDungeonRunSnapshot Continued;
 if(!CaptureActual(Target,Continued,TEXT("Real continued terminal phase3 captures")))return false;
 TestTrue(TEXT("Continue resumes original terminal display age only; sim/kernels/resources/equipment remain frozen"),Continued.Fighters[0].AnimationTime>Owner.AnimationTime
  &&FrozenExceptDisplay(Saved,Continued)&&D::BuildDrawPlan(*Target.Game,*Target.Player,ActualContext(Target),P,Why)&&P.Frame==3
  &&P.Binding.WeaponInstanceId==Saved.Equipment.View.Slots[Saved.Equipment.View.ActiveSlot].InstanceId&&P.Binding.ArmorInstanceId==Saved.Equipment.View.Slots[2].InstanceId);
 return true;
}
#endif
