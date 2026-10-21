#include "DungeonFairytaleSwordDeathPlan.h"
#include "DungeonFighter.h"
#include "DungeonGameMode.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"

namespace DungeonFairytaleSwordDeathV001
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
bool ValidProfile(const FProfile& P)
{
 const auto& Approved=Profile();
 if(!P.SourceClosureVerified||P.ProfileId!=Approved.ProfileId||P.SourceClosureSHA256!=Approved.SourceClosureSHA256
  ||!SHA256(P.SourceClosureSHA256)||P.CanvasSource!=512||P.StandingExtent!=416.||P.StandingDisplay!=72.
  ||P.WeaponScale!=.5||P.ComponentGrip!=FVector2D(99.,256.)||P.SwordTexturePath!=Approved.SwordTexturePath
  ||P.SwordSourceSHA256!=Approved.SwordSourceSHA256||!SHA256(P.SwordSourceSHA256))return false;
 const EComponent Owners[]={EComponent::BodyRest,EComponent::ShoulderFar,EComponent::Chest,EComponent::NearArmWithoutHand,
  EComponent::ShoulderNear,EComponent::HelmetForeground,EComponent::FarHandForeground,EComponent::NearHand};
 TSet<FString> Paths;
 for(int32 I=0;I<5;++I)
 {
  const auto& F=P.Frames[I];const auto& Ref=Approved.Frames[I];
  if(F.Frame!=I||F.KeyAge!=Ref.KeyAge||F.ExpectedNonemptyDrawCount!=9||!InCanvas(F.Root)||!InCanvas(F.SwordAnchor)
   ||!FinitePoint(F.AxisArtist)||F.AxisArtist==FVector2D::ZeroVector||F.Root!=Ref.Root||F.SwordAnchor!=Ref.SwordAnchor
   ||F.AxisArtist!=Ref.AxisArtist||F.VisualSwordReleased!=(I>0)||F.SlotOrder!=Ref.SlotOrder)return false;
  for(int32 J=0;J<8;++J)
  {
   const auto& L=F.Layers[J];const auto& A=Ref.Layers[J];
   if(L.Component!=Owners[J]||L.KnownOptionalEmpty||!L.SourceAlphaNonzero||L.SourceAlphaNonzero>512u*512u
    ||!L.TexturePath.StartsWith(TEXT("/Game/Production/ArtTrials/EV048/v019/HeroLeatherDeath/"))||Paths.Contains(L.TexturePath)
    ||!SHA256(L.SourceSHA256)||!SHA256(L.SourceRGBASHA256)||L.TexturePath!=A.TexturePath||L.SourceSHA256!=A.SourceSHA256
    ||L.SourceRGBASHA256!=A.SourceRGBASHA256||L.SourceAlphaNonzero!=A.SourceAlphaNonzero)return false;
   Paths.Add(L.TexturePath);
  }
 }
 return Paths.Num()==40&&!Paths.Contains(P.SwordTexturePath);
}
}
bool BuildDrawPlanFromCommitted(const DungeonFairytaleSwordEquipmentBinding::FBinding& Binding,const FDungeonDeathPresentationSample& Death,
 double Facing,const FProfile& Source,const FDrawContext& Context,FDrawPlan& Out,FString& Diagnostic)
{
 if(!ValidBinding(Binding))return Reject(Diagnostic,TEXT("Death5 requires actual committed SWD001 and LGT001 identity"));
 if(!Death.Active||!Death.Dead||Death.Health!=0.f||Death.AnimationName!=TEXT("death")
  ||!FMath::IsFinite(Death.Elapsed)||Death.Elapsed<0.f||(Facing!=-1.&&Facing!=1.))
  return Reject(Diagnostic,TEXT("No valid actual terminal Death sample/facing"));
 if(!ValidProfile(Source))return Reject(Diagnostic,TEXT("Death5 complete40 retained source profile is missing, changed or invalid"));
 if(!ScreenPoint(Context.GroundScreen)||!FMath::IsFinite(Context.UIScale)||Context.UIScale<=0.
  ||!FMath::IsFinite(Context.JumpHeight)||Context.JumpHeight<0.)return Reject(Diagnostic,TEXT("Death5 actual HUD projection context is invalid"));
 // Clamp the terminal branch BEFORE integer conversion: a legitimate long-held
 // dead age may exceed int32. No second timer, epsilon or simulated DiedAt clock.
 const double Age=double(Death.Elapsed);const int32 Index=Age>=.8?4:FMath::FloorToInt(Age/.2);
 const auto& F=Source.Frames[Index];FDrawPlan P;
 P.Supported=true;P.Frame=Index;P.Facing=Facing<0.?-1:1;P.ProfileId=Source.ProfileId;
 P.Death=Death;P.Binding=Binding;P.RootSource=F.Root;P.SwordAnchorSource=F.SwordAnchor;P.AxisArtist=F.AxisArtist;
 P.VisualSwordReleased=F.VisualSwordReleased;P.LastFrameHeld=Index==4;P.Tint=FLinearColor::White;
 P.CanvasSize=Source.StandingDisplay*double(Source.CanvasSource)/Source.StandingExtent;
 P.SourceToScreenScale=Source.StandingDisplay/Source.StandingExtent*Context.UIScale;
 P.WeaponScale=Source.WeaponScale;P.WeaponWidth=P.CanvasSize*P.WeaponScale*Context.UIScale;
 const double Scale=P.SourceToScreenScale,Height=Context.JumpHeight*.70*Context.UIScale;
 P.SwordAnchorScreen=Context.GroundScreen+FVector2D(P.Facing*(F.SwordAnchor.X-F.Root.X)*Scale,(F.SwordAnchor.Y-F.Root.Y)*Scale-Height);
 P.BodyTop=Context.GroundScreen-FVector2D((P.Facing<0?512.-F.Root.X:F.Root.X)*Scale,F.Root.Y*Scale+Height);
 P.WeaponAngle=FMath::RadiansToDegrees(FMath::Atan2(F.AxisArtist.Y,F.AxisArtist.X))*(P.Facing<0?-1.:1.);
 P.SwordPivotUV=FVector2D(P.Facing<0?1.-Source.ComponentGrip.X/512.:Source.ComponentGrip.X/512.,Source.ComponentGrip.Y/512.);
 P.SwordTop=P.SwordAnchorScreen-P.SwordPivotUV*P.WeaponWidth;P.TextureU=P.Facing<0?1.:0.;P.TextureDU=P.Facing<0?-1.:1.;
 if(!FMath::IsFinite(P.SourceToScreenScale)||P.SourceToScreenScale<=0.||!FMath::IsFinite(P.WeaponWidth)||P.WeaponWidth<=0.
  ||P.WeaponWidth>double(TNumericLimits<float>::Max())||P.CanvasSize*Context.UIScale>double(TNumericLimits<float>::Max())
  ||!ScreenPoint(P.SwordAnchorScreen)||!ScreenPoint(P.BodyTop)||!ScreenPoint(P.SwordTop))
  return Reject(Diagnostic,TEXT("Death5 screen geometry is not finitely representable"));
 for(int32 I=0;I<9;++I)
 {
  auto& Slot=P.Slots[I];Slot.Component=F.SlotOrder[I];
  if(Slot.Component==EComponent::IndependentSword)Slot.TexturePath=Source.SwordTexturePath;
  else
  {
   const FTextureSource* Layer=nullptr;
   for(const auto& L:F.Layers)if(L.Component==Slot.Component){Layer=&L;break;}
   if(!Layer)return Reject(Diagnostic,TEXT("Death5 ordered slot has no exclusive source owner"));
   Slot.TexturePath=Layer->TexturePath;Slot.KnownOptionalEmpty=Layer->KnownOptionalEmpty;
  }
  if(!Slot.KnownOptionalEmpty)++P.NonemptyDrawCount;
 }
 if(P.NonemptyDrawCount!=F.ExpectedNonemptyDrawCount)return Reject(Diagnostic,TEXT("Death5 source owner order changed its complete draw count"));
 Out=MoveTemp(P);Diagnostic.Reset();return true;
}
bool BuildDrawPlan(const ADungeonGameMode& Game,const ADungeonFighter& Fighter,const FDrawContext& Context,FDrawPlan& Out,FString& Diagnostic)
{
 if(!FParse::Param(FCommandLine::Get(),CommandLineFlag)||!FParse::Param(FCommandLine::Get(),DungeonFairytaleSwordEquipmentBinding::CommandLineFlag))
  return Reject(Diagnostic,TEXT("Death5 requires explicit Death and committed Bound presentation opt-ins"));
 DungeonFairytaleSwordEquipmentBinding::FBinding Binding;
 if(!DungeonFairytaleSwordEquipmentBinding::Resolve(Game,Fighter,Binding,Diagnostic))return false;
 FDungeonDeathPresentationSample Death;
 if(!Fighter.QueryDeathPresentation(Death))return Reject(Diagnostic,TEXT("Actual player is not in native terminal Death"));
 if(Context.JumpHeight!=double(Fighter.JumpHeight))return Reject(Diagnostic,TEXT("HUD Death projection height differs from actual player"));
 return BuildDrawPlanFromCommitted(Binding,Death,double(Fighter.Facing),Profile(),Context,Out,Diagnostic);
}
}
