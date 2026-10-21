#include "DungeonFairytaleSwordHurtPlan.h"
#include "DungeonFighter.h"
#include "DungeonGameMode.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"

namespace DungeonFairytaleSwordHurtV001
{
namespace
{
bool Reject(FString& Diagnostic,const TCHAR* Why){Diagnostic=Why;return false;}
bool FinitePoint(FVector2D P){return FMath::IsFinite(P.X)&&FMath::IsFinite(P.Y);}
bool InCanvas(FVector2D P){return FinitePoint(P)&&P.X>=0.&&P.X<=512.&&P.Y>=0.&&P.Y<=512.;}
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
  ||P.WeaponScale!=.5||P.ComponentGrip!=FVector2D(99.,256.)||P.SwordTexturePath!=Approved.SwordTexturePath)return false;
 const EComponent Order[]={EComponent::BodyRest,EComponent::ShoulderFar,EComponent::Chest,EComponent::NearArmWithoutHand,
  EComponent::ShoulderNear,EComponent::HelmetForeground,EComponent::FarHandForeground,EComponent::NearHand};
 TSet<FString> Paths;
 for(int32 I=0;I<4;++I)
 {
  const auto& F=P.Frames[I];const auto& Ref=Approved.Frames[I];
  if(F.Frame!=I||F.ExpectedNonemptyDrawCount!=(I==0?9:8)||!InCanvas(F.Root)||!InCanvas(F.Grip)
   ||!FinitePoint(F.AxisArtist)||F.AxisArtist==FVector2D::ZeroVector||F.Root!=Ref.Root||F.Grip!=Ref.Grip||F.AxisArtist!=Ref.AxisArtist)return false;
  for(int32 J=0;J<8;++J)
  {
   const auto& L=F.Layers[J];const auto& A=Ref.Layers[J];const bool Empty=I>0&&Order[J]==EComponent::FarHandForeground;
   if(L.Component!=Order[J]||L.KnownOptionalEmpty!=Empty||(Empty?L.SourceAlphaNonzero!=0:L.SourceAlphaNonzero==0)
    ||L.SourceAlphaNonzero>512u*512u||!L.TexturePath.StartsWith(TEXT("/Game/Production/ArtTrials/EV048/v017/HeroLeatherHurt/"))
    ||!L.TexturePath.Contains(TEXT("."))||Paths.Contains(L.TexturePath)||!SHA256(L.SourceSHA256)||!SHA256(L.SourceRGBASHA256)
    ||L.TexturePath!=A.TexturePath||L.SourceSHA256!=A.SourceSHA256||L.SourceRGBASHA256!=A.SourceRGBASHA256||L.SourceAlphaNonzero!=A.SourceAlphaNonzero)return false;
   Paths.Add(L.TexturePath);
  }
 }
 return Paths.Num()==32&&!Paths.Contains(P.SwordTexturePath);
}
}
bool BuildDrawPlanFromCommitted(const DungeonFairytaleSwordEquipmentBinding::FBinding& Binding,const FDungeonHurtPresentationSample& Hurt,
 double Facing,const FProfile& Source,const FDrawContext& Context,FDrawPlan& Out,FString& Diagnostic)
{
 if(!ValidBinding(Binding))return Reject(Diagnostic,TEXT("Hurt4 requires actual committed SWD001 and LGT001 identity"));
 if(!Hurt.Active||!FMath::IsFinite(Hurt.Elapsed)||Hurt.Elapsed<0.f||!FMath::IsFinite(Hurt.Remaining)||Hurt.Remaining<=0.f
  ||(Facing!=-1.&&Facing!=1.))return Reject(Diagnostic,TEXT("No valid actual living Hurt sample/facing"));
 if(!ValidProfile(Source))return Reject(Diagnostic,TEXT("Hurt4 complete32 retained source profile is missing, changed or invalid"));
 if(!FinitePoint(Context.GroundScreen)||!FMath::IsFinite(Context.UIScale)||Context.UIScale<=0.
  ||!FMath::IsFinite(Context.JumpHeight)||Context.JumpHeight<0.)return Reject(Diagnostic,TEXT("Hurt4 actual HUD projection context is invalid"));
 // Native positive remaining owns the end. Do not force nominal400ms, create a
 // second timer or turn a genuinely active tiny float tail into bare Ready0.
 const double Age=double(Hurt.Elapsed);const int32 Index=Age>=.3?3:Age>=.2?2:Age>=.1?1:0;
 const auto& F=Source.Frames[Index];FDrawPlan P;P.Supported=true;P.Frame=Index;P.Facing=Facing<0.?-1:1;P.ProfileId=Source.ProfileId;
 P.Hurt=Hurt;P.Binding=Binding;P.RootSource=F.Root;P.GripSource=F.Grip;P.AxisArtist=F.AxisArtist;
 P.CanvasSize=Source.StandingDisplay*double(Source.CanvasSource)/Source.StandingExtent;
 P.SourceToScreenScale=Source.StandingDisplay/Source.StandingExtent*Context.UIScale;
 P.WeaponScale=Source.WeaponScale;P.WeaponWidth=P.CanvasSize*P.WeaponScale*Context.UIScale;
 const double Scale=P.SourceToScreenScale,Height=Context.JumpHeight*.70*Context.UIScale;
 P.GripScreen=Context.GroundScreen+FVector2D(P.Facing*(F.Grip.X-F.Root.X)*Scale,(F.Grip.Y-F.Root.Y)*Scale-Height);
 P.BodyTop=Context.GroundScreen-FVector2D((P.Facing<0?512.-F.Root.X:F.Root.X)*Scale,F.Root.Y*Scale+Height);
 P.WeaponAngle=FMath::RadiansToDegrees(FMath::Atan2(F.AxisArtist.Y,F.AxisArtist.X))*(P.Facing<0?-1.:1.);
 P.SwordPivotUV=FVector2D(P.Facing<0?1.-Source.ComponentGrip.X/512.:Source.ComponentGrip.X/512.,Source.ComponentGrip.Y/512.);
 P.SwordTop=P.GripScreen-P.SwordPivotUV*P.WeaponWidth;P.TextureU=P.Facing<0?1.:0.;P.TextureDU=P.Facing<0?-1.:1.;
 if(!FMath::IsFinite(P.SourceToScreenScale)||P.SourceToScreenScale<=0.||!FMath::IsFinite(P.WeaponWidth)||P.WeaponWidth<=0.
  ||!FinitePoint(P.GripScreen)||!FinitePoint(P.BodyTop)||!FinitePoint(P.SwordTop))
  return Reject(Diagnostic,TEXT("Hurt4 screen geometry is not finitely representable"));
 const EComponent Stack[]={EComponent::BodyRest,EComponent::ShoulderFar,EComponent::Chest,EComponent::NearArmWithoutHand,
  EComponent::ShoulderNear,EComponent::HelmetForeground,EComponent::FarHandForeground,EComponent::IndependentSword,EComponent::NearHand};
 for(int32 I=0;I<9;++I)
 {
  auto& Slot=P.Slots[I];Slot.Component=Stack[I];
  if(Stack[I]==EComponent::IndependentSword)Slot.TexturePath=Source.SwordTexturePath;
  else{const auto& L=F.Layers[I<7?I:7];Slot.TexturePath=L.TexturePath;Slot.KnownOptionalEmpty=L.KnownOptionalEmpty;}
  if(!Slot.KnownOptionalEmpty)++P.NonemptyDrawCount;
 }
 if(P.NonemptyDrawCount!=F.ExpectedNonemptyDrawCount)return Reject(Diagnostic,TEXT("Hurt4 known-empty policy changed its complete draw count"));
 Out=MoveTemp(P);Diagnostic.Reset();return true;
}
bool BuildDrawPlan(const ADungeonGameMode& Game,const ADungeonFighter& Fighter,const FDrawContext& Context,FDrawPlan& Out,FString& Diagnostic)
{
 if(!FParse::Param(FCommandLine::Get(),CommandLineFlag)||!FParse::Param(FCommandLine::Get(),DungeonFairytaleSwordEquipmentBinding::CommandLineFlag))
  return Reject(Diagnostic,TEXT("Hurt4 requires explicit Hurt and committed Bound presentation opt-ins"));
 DungeonFairytaleSwordEquipmentBinding::FBinding Binding;
 if(!DungeonFairytaleSwordEquipmentBinding::Resolve(Game,Fighter,Binding,Diagnostic))return false;
 FDungeonHurtPresentationSample Hurt;
 if(!Fighter.QueryHurtPresentation(Hurt))return Reject(Diagnostic,TEXT("Actual player is not in living active native Hurt"));
 if(Context.JumpHeight!=double(Fighter.JumpHeight))return Reject(Diagnostic,TEXT("HUD Hurt projection height differs from actual player"));
 return BuildDrawPlanFromCommitted(Binding,Hurt,double(Fighter.Facing),Profile(),Context,Out,Diagnostic);
}
}
