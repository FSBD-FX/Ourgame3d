#include "DungeonHUD.h"
#include "DungeonFighter.h"
#include "DungeonGameMode.h"
#include "DungeonFairytaleSwordDeathPlan.h"
#include "Engine/Texture2D.h"
#include "Engine/World.h"
#include "TextureResource.h"
#include "UnrealClient.h"

bool ADungeonHUD::DrawFairytaleSwordDeathBody(ADungeonFighter* F)
{
 using namespace DungeonFairytaleSwordDeathV001;
 auto& Trace=FairytaleSwordDeathDraw;
 const auto Game=GetWorld()?GetWorld()->GetAuthGameMode<ADungeonGameMode>():nullptr;
 Trace.PlayerEntityId=F->GetRuntimeEntityId();Trace.OptIn=bUseFairytaleSwordDeathPreview;
 Trace.SimulationTime=Game?Game->GetSimulationTime():F->GetMeleeCombatState().Time;
 const auto G=Ground(F->GetGroundPosition());Trace.Context.GroundScreen=Screen(float(G.X),float(G.Y));
 Trace.Context.UIScale=double(UIScale);Trace.Context.JumpHeight=double(F->JumpHeight);
 if(!Game){Trace.MissingReason=TEXT("Death5 actual world GameMode is absent; retain identifiable current fallback");return false;}
 if(!BuildDrawPlan(*Game,*F,Trace.Context,Trace.Plan,Trace.MissingReason))
 {
  // Unsupported combinations stay in the current clock-helmet presenter. Returning
  // false here only continues DrawFairytaleSwordBody; it never reaches old human art.
  DungeonFairytaleSwordEquipmentBinding::FBinding Binding;FString BindingWhy;
  if(!DungeonFairytaleSwordEquipmentBinding::Resolve(*Game,*F,Binding,BindingWhy)
   ||Binding.Armor!=DungeonFairytaleSwordEquipmentBinding::EArmor::LightArmor)return false;
  // A supported committed identity with an invalid/missing plan owns a closed draw.
 }
 const uint64 PreviousHurtDrawId=FairytaleSwordHurtDraw.DrawId;
 FairytaleSwordHurtDraw=FDungeonFairytaleSwordHurtDraw();FairytaleSwordHurtDraw.DrawId=PreviousHurtDrawId;
 FairytaleSwordHurtDraw.OptIn=bUseFairytaleSwordHurtPreview;
 const uint64 PreviousDrawId=FairytaleSwordDraw.DrawId;FairytaleSwordDraw=FDungeonFairytaleSwordDraw();auto& Record=FairytaleSwordDraw;
 Record.Active=true;Record.DrawId=PreviousDrawId;Record.EquipmentBoundMode=bUseFairytaleSwordEquipmentBoundPreview;
 Record.Clip=TEXT("sword_death");Record.Facing=F->Facing<0?-1:1;Record.SimulationTime=Trace.SimulationTime;
 Record.NativeScreenshotPath=FScreenshotRequest::IsScreenshotRequested()?FScreenshotRequest::GetFilename():FString();
 bRenderedArmorLayersUsed=false;RenderedArmorLayerPaths.Reset();RenderedPlayerDrawStack.Reset();RenderedPlayerTexturePath.Reset();
 bRenderedWeaponBodyUsed=false;RenderedWeaponBodyFrame=-1;RenderedWeaponBodyFacing=0;RenderedWeaponBodyClip.Reset();
 RenderedWeaponBodyActionId=0;RenderedWeaponBodySampleTime=0.;RenderedWeaponBodyInstanceId=0;RenderedWeaponStateIndex=-1;
 RenderedWeaponBodyEmitScreen=FVector2D::ZeroVector;
 if(!Trace.Plan.Supported){Record.EquipmentBindingDiagnostic=Trace.MissingReason;return true;}
 const auto& P=Trace.Plan;
 Trace.Tint=P.Tint; // White terminal base. Persistent actual HitFlash is untouched.
 Record.Supported=Record.ActionPoseSupported=true;Record.EquipmentBindingValid=true;Record.EquipmentBinding=P.Binding;
 Record.InstanceId=P.Binding.WeaponInstanceId;Record.Frame=P.Frame;Record.Facing=P.Facing;Record.CanvasSize=P.CanvasSize;
 Record.Root=P.RootSource;Record.Grip=P.SwordAnchorSource;Record.GripScreen=P.SwordAnchorScreen;Record.WeaponAngle=P.WeaponAngle;
 Record.WeaponScale=P.WeaponScale;Record.WeaponWidth=P.WeaponWidth;Record.ArmorPreview=true;
 RenderedPlayerSpriteSize=float(P.CanvasSize);RenderedActorSpriteSizes.Add(F,float(P.CanvasSize));
 const auto CacheReady=[this](const FString& Path)
 {
  const UTexture2D* Texture=Frames.FindRef(Path);
  return Texture&&Texture->GetClass()==UTexture2D::StaticClass()&&Texture->GetResource()&&!Texture->HasPendingRenderResourceInitialization()
   &&Texture->GetPathName()==Path&&Texture->GetSizeX()==512&&Texture->GetSizeY()==512;
 };
 Trace.AtomicPreflightReady=true;Trace.ResidentTextures.Reserve(41);
 const auto AdmitResident=[&](const FString& Path)
 {
  const UTexture2D* Texture=Frames.FindRef(Path);FDungeonFairytaleSwordDeathResidentTexture Resource;
  Resource.TexturePath=Texture?Texture->GetPathName():Path;Resource.ClassName=Texture?Texture->GetClass()->GetName():FString();
  Resource.Width=Texture?Texture->GetSizeX():0;Resource.Height=Texture?Texture->GetSizeY():0;Resource.ResourceReady=CacheReady(Path);
  Trace.AtomicPreflightReady=Trace.AtomicPreflightReady&&Resource.ResourceReady;Trace.ResidentTextures.Add(MoveTemp(Resource));
 };
 // All five rows and the reused sword must already be ready, even when only the
 // first row is selected. No LoadObject, import, pixel transform or first-use repair.
 for(const auto& Phase:Profile().Frames)for(const auto& Layer:Phase.Layers)AdmitResident(Layer.TexturePath);
 AdmitResident(Profile().SwordTexturePath);
 UTexture2D* Textures[9]={};Trace.Slots.Reserve(9);
 for(int32 I=0;I<9;++I)
 {
  const auto& Slot=P.Slots[I];UTexture2D* Texture=Frames.FindRef(Slot.TexturePath);Textures[I]=Texture;
  FDungeonFairytaleSwordDeathSlotDraw Quad;Quad.SlotIndex=I;Quad.Component=Slot.Component;
  Quad.TexturePath=Texture?Texture->GetPathName():Slot.TexturePath;Quad.KnownOptionalEmpty=Slot.KnownOptionalEmpty;Quad.TextureReady=CacheReady(Slot.TexturePath);
  const bool Sword=Slot.Component==EComponent::IndependentSword;const auto Top=Sword?P.SwordTop:P.BodyTop;
  const double Width=Sword?P.WeaponWidth:P.CanvasSize*Trace.Context.UIScale;
  // Keep exact actual float AHUD arguments apart from the shared double source plan.
  Quad.Top={float(Top.X),float(Top.Y)};Quad.Size={float(Width),float(Width)};
  Quad.UV={float(P.TextureU),0.f};Quad.UVSize={float(P.TextureDU),1.f};
  Quad.RotationDegrees=Sword?double(float(P.WeaponAngle)):0.;Quad.RotationPivot=Sword?P.SwordPivotUV:FVector2D::ZeroVector;
  Quad.DrawScale=1.;Quad.ScalePosition=false;Trace.AtomicPreflightReady=Trace.AtomicPreflightReady&&Quad.TextureReady;
  Trace.Slots.Add(MoveTemp(Quad));
 }
 Record.TextureReady=Record.ArmorReady=Trace.AtomicPreflightReady;
 if(!Trace.AtomicPreflightReady){Trace.MissingReason=TEXT("Death5 complete40/sword41 cache resource is not ready; no partial draw");return true;}
 if(!Canvas){Trace.MissingReason=TEXT("Death5 plan/resources ready but actual Canvas is absent; no rendered claim");return true;}
 ++Record.DrawId;Trace.DrawId=Record.DrawId;
 for(int32 I=0;I<9;++I)
 {
  auto& Slot=Trace.Slots[I];if(Slot.KnownOptionalEmpty)continue;
  DrawTexture(Textures[I],float(Slot.Top.X),float(Slot.Top.Y),float(Slot.Size.X),float(Slot.Size.Y),float(Slot.UV.X),float(Slot.UV.Y),
   float(Slot.UVSize.X),float(Slot.UVSize.Y),Trace.Tint,BLEND_Translucent,float(Slot.DrawScale),Slot.ScalePosition,float(Slot.RotationDegrees),Slot.RotationPivot);
  Slot.Drawn=true;Trace.ActualRenderedStack.Add(Textures[I]->GetPathName());Record.DrawStack.Add(Textures[I]->GetPathName());
  RenderedPlayerDrawStack.Add(Textures[I]->GetPathName());
  FActorQuad Quad;Quad.Owner=F;Quad.Texture=Textures[I];Quad.Top=Slot.Top;Quad.Size=float(Slot.Size.X);Quad.Tint=Trace.Tint;
  Quad.Rotation=float(Slot.RotationDegrees);Quad.Pivot=Slot.RotationPivot;Quad.Weapon=Slot.Component==EComponent::IndependentSword;ActorQuads.Add(Quad);
  if(Slot.Component==EComponent::ShoulderFar||Slot.Component==EComponent::Chest||Slot.Component==EComponent::ShoulderNear)
   RenderedArmorLayerPaths.Add(Textures[I]->GetPathName());
  if(Slot.Component==EComponent::IndependentSword)Record.WeaponPath=Textures[I]->GetPathName();
  if(Slot.Component==EComponent::BodyRest)Record.TexturePath=RenderedPlayerTexturePath=Textures[I]->GetPathName();
 }
 Trace.Drawn=Trace.ActualRenderedStack.Num()==P.NonemptyDrawCount;
 if(!Trace.Drawn)Trace.MissingReason=TEXT("Death5 actual submission count differs from shared complete plan");
 Record.ArmorDrawn=bRenderedArmorLayersUsed=Trace.Drawn;bRenderedWeaponBodyUsed=Trace.Drawn;
 RenderedWeaponBodyClip=Record.Clip;RenderedWeaponBodyFrame=P.Frame;RenderedWeaponBodyFacing=P.Facing;
 RenderedWeaponBodyActionId=0;RenderedWeaponBodySampleTime=Record.SimulationTime;RenderedWeaponBodyInstanceId=P.Binding.WeaponInstanceId;RenderedWeaponStateIndex=P.Frame;
 return true;
}
