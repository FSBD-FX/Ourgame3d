#include "DungeonFairytaleSwordDodgePlan.h"
#include "DungeonFighter.h"
#include "DungeonGameMode.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"

namespace DungeonFairytaleSwordDodgeV001
{
namespace
{
bool Reject(FString& Diagnostic,const TCHAR* Why){Diagnostic=Why;return false;}
bool FinitePoint(FVector2D P){return FMath::IsFinite(P.X)&&FMath::IsFinite(P.Y);}
bool InCanvas(FVector2D P){return FinitePoint(P)&&P.X>=0.&&P.X<=512.&&P.Y>=0.&&P.Y<=512.;}
bool ScreenPoint(FVector2D P)
{return FinitePoint(P)&&FMath::Abs(P.X)<=double(TNumericLimits<float>::Max())&&FMath::Abs(P.Y)<=double(TNumericLimits<float>::Max());}
bool SHA256(const FString& S)
{
 if(S.Len()!=64)return false;
 for(int32 I=0;I<S.Len();++I)if(!((S[I]>=TEXT('0')&&S[I]<=TEXT('9'))||(S[I]>=TEXT('a')&&S[I]<=TEXT('f'))))return false;
 return true;
}
bool ValidBinding(const DungeonFairytaleSwordEquipmentBinding::FBinding& B)
{
 using A=DungeonFairytaleSwordEquipmentBinding::EArmor;
 return B.RunGuid.IsValid()&&B.RunAlias&&B.OwnerId&&B.Revision&&B.Revision!=TNumericLimits<uint64>::Max()
  &&B.ActiveSlot>=0&&B.ActiveSlot<=1&&B.WeaponInstanceId&&B.WeaponVersion&&B.WeaponVersion!=TNumericLimits<uint64>::Max()
  &&B.WeaponContentId==TEXT("WPN-SWD-001")&&B.Armor==A::LightArmor&&B.ArmorInstanceId&&B.ArmorVersion
  &&B.ArmorVersion!=TNumericLimits<uint64>::Max()&&B.ArmorInstanceId!=B.WeaponInstanceId&&B.ArmorContentId==TEXT("ARM-LGT-001");
}
bool ValidSample(const FDungeonDodgePresentationSample& D,uint64 OwnerId)
{
 if(!D.Active||!D.OwnerId||D.OwnerId!=OwnerId||!D.ActionId||!D.StartEventId||D.Finish!=DungeonDodge::EFinish::None
  ||uint32(D.Block)>uint32(DungeonDodge::EBlock::Body)||!FinitePoint(D.Direction)
  ||!FMath::IsNearlyEqual(D.Direction.SizeSquared(),1.,1.e-12))return false;
 for(double T:{D.SampleTime,D.Start,D.End,D.ReadyAt,D.Elapsed,D.Remaining,D.Travelled})if(!FMath::IsFinite(T))return false;
 return D.Start>=0.&&D.End==D.Start+DungeonDodge::Duration&&D.ReadyAt==D.Start+DungeonDodge::Cooldown
  &&D.SampleTime>=D.Start&&D.SampleTime<D.End&&D.Elapsed==D.SampleTime-D.Start&&D.Remaining==D.End-D.SampleTime
  &&D.Elapsed>=0.&&D.Remaining>0.&&D.Travelled>=0.&&D.Travelled<=DungeonDodge::Distance
  &&D.Invulnerable==(D.SampleTime>=D.Start+DungeonDodge::IFrameStart&&D.SampleTime<D.Start+DungeonDodge::IFrameEnd);
}
bool ValidProfile(const FProfile& P)
{
 const auto& Approved=Profile();
 if(!P.SourceClosureVerified||P.ProfileId!=Approved.ProfileId||P.SourceClosureSHA256!=Approved.SourceClosureSHA256
  ||!SHA256(P.SourceClosureSHA256)||P.CanvasSource!=512||P.StandingExtent!=416.||P.StandingDisplay!=72.
  ||P.WeaponScale!=.5||P.ComponentGrip!=FVector2D(99.,256.)||P.SwordTexturePath!=Approved.SwordTexturePath
  ||P.SwordSourceSHA256!=Approved.SwordSourceSHA256||!SHA256(P.SwordSourceSHA256))return false;
 const EComponent Owners[]={EComponent::BodyRest,EComponent::ShoulderFar,EComponent::Chest,EComponent::NearArmWithoutHand,
  EComponent::ShoulderNear,EComponent::HelmetForeground,EComponent::FarHandForeground,EComponent::NearHand};
 const double Starts[]={0.,.1,.2,.3};TSet<FString> Paths;
 for(int32 I=0;I<4;++I)
 {
  const auto& F=P.Frames[I];const auto& Ref=Approved.Frames[I];
  if(F.Frame!=I||F.KeyAge!=Starts[I]||F.ExpectedNonemptyDrawCount!=9||!InCanvas(F.Root)||!InCanvas(F.Grip)
   ||!FinitePoint(F.AxisArtist)||F.AxisArtist==FVector2D::ZeroVector||F.Root!=Ref.Root||F.Grip!=Ref.Grip
   ||F.AxisArtist!=Ref.AxisArtist||F.SlotOrder!=Ref.SlotOrder)return false;
  for(int32 J=0;J<8;++J)
  {
   const auto& L=F.Layers[J];const auto& A=Ref.Layers[J];
   if(L.Component!=Owners[J]||L.KnownOptionalEmpty||!L.SourceAlphaNonzero||L.SourceAlphaNonzero>512u*512u
    ||!L.TexturePath.StartsWith(TEXT("/Game/Production/ArtTrials/EV048/v018/HeroLeatherDodge/"))||Paths.Contains(L.TexturePath)
    ||!SHA256(L.SourceSHA256)||!SHA256(L.SourceRGBASHA256)||L.TexturePath!=A.TexturePath||L.SourceSHA256!=A.SourceSHA256
    ||L.SourceRGBASHA256!=A.SourceRGBASHA256||L.SourceAlphaNonzero!=A.SourceAlphaNonzero)return false;
   Paths.Add(L.TexturePath);
  }
 }
 return Paths.Num()==32&&!Paths.Contains(P.SwordTexturePath);
}
}
bool BuildDrawPlanFromCommitted(const DungeonFairytaleSwordEquipmentBinding::FBinding& Binding,const FDungeonDodgePresentationSample& Dodge,
 double Facing,const FProfile& Source,const FDrawContext& Context,FDrawPlan& Out,FString& Diagnostic)
{
 if(!ValidBinding(Binding))return Reject(Diagnostic,TEXT("Dodge4 requires actual committed SWD001 and LGT001 identity"));
 if(!ValidSample(Dodge,Binding.OwnerId)||(Facing!=-1.&&Facing!=1.))return Reject(Diagnostic,TEXT("No valid actual same-owner active native Dodge sample/facing"));
 if(!ValidProfile(Source))return Reject(Diagnostic,TEXT("Dodge4 complete32 retained source profile is missing, changed or invalid"));
 if(!ScreenPoint(Context.GroundScreen)||!FMath::IsFinite(Context.UIScale)||Context.UIScale<=0.
  ||!FMath::IsFinite(Context.JumpHeight)||Context.JumpHeight!=0.)return Reject(Diagnostic,TEXT("Dodge4 requires actual finite grounded HUD context"));
 // Absolute thresholds of THIS actual action avoid cancellation in Time-Start.
 // The raw double elapsed/remaining are retained unchanged; original End owns exit.
 int32 Index=0;for(int32 I=1;I<4;++I)if(Dodge.SampleTime>=Dodge.Start+Source.Frames[I].KeyAge)Index=I;
 const auto& F=Source.Frames[Index];FDrawPlan P;P.Supported=true;P.Frame=Index;P.Facing=Facing<0.?-1:1;P.ProfileId=Source.ProfileId;
 P.Dodge=Dodge;P.Binding=Binding;P.RootSource=F.Root;P.GripSource=F.Grip;P.AxisArtist=F.AxisArtist;
 P.CanvasSize=Source.StandingDisplay*double(Source.CanvasSource)/Source.StandingExtent;
 P.SourceToScreenScale=Source.StandingDisplay/Source.StandingExtent*Context.UIScale;
 P.WeaponScale=Source.WeaponScale;P.WeaponWidth=P.CanvasSize*P.WeaponScale*Context.UIScale;
 const double Scale=P.SourceToScreenScale;
 P.GripScreen=Context.GroundScreen+FVector2D(P.Facing*(F.Grip.X-F.Root.X)*Scale,(F.Grip.Y-F.Root.Y)*Scale);
 P.BodyTop=Context.GroundScreen-FVector2D((P.Facing<0?512.-F.Root.X:F.Root.X)*Scale,F.Root.Y*Scale);
 // UV reflection and negative angle implement ONE full X reflection of the
 // right-facing parent transform, including the sword's component grip pivot.
 P.WeaponAngle=FMath::RadiansToDegrees(FMath::Atan2(F.AxisArtist.Y,F.AxisArtist.X))*(P.Facing<0?-1.:1.);
 P.SwordPivotUV=FVector2D(P.Facing<0?1.-Source.ComponentGrip.X/512.:Source.ComponentGrip.X/512.,Source.ComponentGrip.Y/512.);
 P.SwordTop=P.GripScreen-P.SwordPivotUV*P.WeaponWidth;P.TextureU=P.Facing<0?1.:0.;P.TextureDU=P.Facing<0?-1.:1.;
 if(!FMath::IsFinite(P.SourceToScreenScale)||P.SourceToScreenScale<=0.||!FMath::IsFinite(P.WeaponWidth)||P.WeaponWidth<=0.
  ||P.WeaponWidth>double(TNumericLimits<float>::Max())||P.CanvasSize*Context.UIScale>double(TNumericLimits<float>::Max())
  ||!ScreenPoint(P.GripScreen)||!ScreenPoint(P.BodyTop)||!ScreenPoint(P.SwordTop))return Reject(Diagnostic,TEXT("Dodge4 actual screen geometry is not finitely representable"));
 for(int32 I=0;I<9;++I)
 {
  auto& Slot=P.Slots[I];Slot.Component=F.SlotOrder[I];
  if(Slot.Component==EComponent::IndependentSword)Slot.TexturePath=Source.SwordTexturePath;
  else
  {
   const FTextureSource* Layer=nullptr;for(const auto& L:F.Layers)if(L.Component==Slot.Component){Layer=&L;break;}
   if(!Layer)return Reject(Diagnostic,TEXT("Dodge4 ordered slot has no exclusive source owner"));
   Slot.TexturePath=Layer->TexturePath;Slot.KnownOptionalEmpty=Layer->KnownOptionalEmpty;
  }
  if(Slot.KnownOptionalEmpty)return Reject(Diagnostic,TEXT("Dodge4 cannot skip any of its nine nonempty sources"));
  ++P.NonemptyDrawCount;
 }
 if(P.NonemptyDrawCount!=F.ExpectedNonemptyDrawCount)return Reject(Diagnostic,TEXT("Dodge4 source owner order changed complete draw count"));
 Out=MoveTemp(P);Diagnostic.Reset();return true;
}
bool BuildDrawPlan(const ADungeonGameMode& Game,const ADungeonFighter& Fighter,const FDrawContext& Context,FDrawPlan& Out,FString& Diagnostic)
{
 if(!FParse::Param(FCommandLine::Get(),CommandLineFlag)||!FParse::Param(FCommandLine::Get(),DungeonFairytaleSwordEquipmentBinding::CommandLineFlag))
  return Reject(Diagnostic,TEXT("Dodge4 requires explicit Dodge and committed Bound presentation opt-ins"));
 DungeonFairytaleSwordEquipmentBinding::FBinding Binding;
 if(!DungeonFairytaleSwordEquipmentBinding::Resolve(Game,Fighter,Binding,Diagnostic))return false;
 FDungeonDodgePresentationSample Dodge;
 if(!Fighter.QueryDodgePresentation(Dodge))return Reject(Diagnostic,TEXT("Actual player is not in living grounded active native Dodge"));
 if(Context.JumpHeight!=double(Fighter.JumpHeight))return Reject(Diagnostic,TEXT("HUD Dodge projection height differs from actual player"));
 return BuildDrawPlanFromCommitted(Binding,Dodge,double(Fighter.Facing),Profile(),Context,Out,Diagnostic);
}
}
