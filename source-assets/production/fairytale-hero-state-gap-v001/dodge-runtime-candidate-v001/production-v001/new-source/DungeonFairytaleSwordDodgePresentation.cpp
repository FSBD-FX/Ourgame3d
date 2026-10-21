#include "DungeonHUD.h"
#include "DungeonFighter.h"
#include "DungeonGameMode.h"
#include "DungeonFairytaleSwordDodgePlan.h"
#include "Engine/Texture2D.h"
#include "Engine/World.h"
#include "TextureResource.h"
#include "UnrealClient.h"

bool ADungeonHUD::DrawFairytaleSwordDodgeBody(ADungeonFighter* F)
{
 using namespace DungeonFairytaleSwordDodgeV001;
 auto& Trace=FairytaleSwordDodgeDraw;
 const auto Game=GetWorld()?GetWorld()->GetAuthGameMode<ADungeonGameMode>():nullptr;
 Trace.PlayerEntityId=F->GetRuntimeEntityId();Trace.OptIn=bUseFairytaleSwordDodgePreview;
 Trace.SimulationTime=Game?Game->GetSimulationTime():F->GetDodgeState().Time;
 const auto G=Ground(F->GetGroundPosition());Trace.Context.GroundScreen=Screen(float(G.X),float(G.Y));
 Trace.Context.UIScale=double(UIScale);Trace.Context.JumpHeight=double(F->JumpHeight);
 if(!Game){Trace.MissingReason=TEXT("Dodge4 actual world GameMode is absent");return false;}
 if(!BuildDrawPlan(*Game,*F,Trace.Context,Trace.Plan,Trace.MissingReason))
 {
  DungeonFairytaleSwordEquipmentBinding::FBinding Binding;FString Why;
  if(!DungeonFairytaleSwordEquipmentBinding::Resolve(*Game,*F,Binding,Why)
   ||Binding.Armor!=DungeonFairytaleSwordEquipmentBinding::EArmor::LightArmor)return false;
  // A supported identity with an invalid plan owns a closed draw, never a
  // partially rendered Dodge or a static Ready mask labelled successful Dodge.
 }
 const uint64 PreviousDrawId=FairytaleSwordDraw.DrawId;FairytaleSwordDraw=FDungeonFairytaleSwordDraw();auto& Record=FairytaleSwordDraw;
 Record.Active=true;Record.DrawId=PreviousDrawId;Record.EquipmentBoundMode=bUseFairytaleSwordEquipmentBoundPreview;
 Record.Clip=TEXT("sword_dodge");Record.Facing=F->Facing<0?-1:1;Record.SimulationTime=Trace.SimulationTime;
 Record.NativeScreenshotPath=FScreenshotRequest::IsScreenshotRequested()?FScreenshotRequest::GetFilename():FString();
 bRenderedArmorLayersUsed=false;RenderedArmorLayerPaths.Reset();RenderedPlayerDrawStack.Reset();RenderedPlayerTexturePath.Reset();
 bRenderedWeaponBodyUsed=false;RenderedWeaponBodyFrame=-1;RenderedWeaponBodyFacing=0;RenderedWeaponBodyClip.Reset();
 RenderedWeaponBodyActionId=0;RenderedWeaponBodySampleTime=0.;RenderedWeaponBodyInstanceId=0;RenderedWeaponStateIndex=-1;
 RenderedWeaponBodyEmitScreen=FVector2D::ZeroVector;
 if(!Trace.Plan.Supported){Record.EquipmentBindingDiagnostic=Trace.MissingReason;return true;}
 const auto& P=Trace.Plan;
 // Ordinary real positive-hit tint may coexist with a nonbreaking dodge hit.
 // The actual timer remains gameplay-owned; no presentation timer is created.
 Trace.Tint=F->HitFlash>0.f?FLinearColor(1.7f,.6f,.4f,1.f):FLinearColor::White;
 Record.Supported=Record.ActionPoseSupported=true;Record.EquipmentBindingValid=true;Record.EquipmentBinding=P.Binding;
 Record.InstanceId=P.Binding.WeaponInstanceId;Record.ActionId=P.Dodge.ActionId;Record.Frame=P.Frame;Record.Facing=P.Facing;Record.CanvasSize=P.CanvasSize;
 Record.Root=P.RootSource;Record.Grip=P.GripSource;Record.GripScreen=P.GripScreen;Record.WeaponAngle=P.WeaponAngle;
 Record.WeaponScale=P.WeaponScale;Record.WeaponWidth=P.WeaponWidth;Record.ArmorPreview=true;
 RenderedPlayerSpriteSize=float(P.CanvasSize);RenderedActorSpriteSizes.Add(F,float(P.CanvasSize));
 const auto CacheReady=[this](const FString& Path)
 {
  const UTexture2D* T=Frames.FindRef(Path);
  return T&&T->GetClass()==UTexture2D::StaticClass()&&T->GetResource()&&!T->HasPendingRenderResourceInitialization()
   &&T->GetPathName()==Path&&T->GetSizeX()==512&&T->GetSizeY()==512;
 };
 Trace.AtomicPreflightReady=true;Trace.ResidentTextures.Reserve(33);
 const auto AdmitResident=[&](const FString& Path)
 {
  const UTexture2D* T=Frames.FindRef(Path);FDungeonFairytaleSwordDodgeResidentTexture Resource;
  Resource.TexturePath=T?T->GetPathName():Path;Resource.ClassName=T?T->GetClass()->GetName():FString();
  Resource.Width=T?T->GetSizeX():0;Resource.Height=T?T->GetSizeY():0;Resource.ResourceReady=CacheReady(Path);
  Resource.PendingInitialization=T&&T->HasPendingRenderResourceInitialization();
  Trace.AtomicPreflightReady=Trace.AtomicPreflightReady&&Resource.ResourceReady;Trace.ResidentTextures.Add(MoveTemp(Resource));
 };
 // Entire32 plus reused sword33. Cache only: the startup loader and existing
 // FinishCompilation/render flush must have completed before this branch.
 for(const auto& Phase:Profile().Frames)for(const auto& Layer:Phase.Layers)AdmitResident(Layer.TexturePath);
 AdmitResident(Profile().SwordTexturePath);
 UTexture2D* Textures[9]={};Trace.Slots.Reserve(9);
 for(int32 I=0;I<9;++I)
 {
  const auto& Slot=P.Slots[I];UTexture2D* T=Frames.FindRef(Slot.TexturePath);Textures[I]=T;
  FDungeonFairytaleSwordDodgeSlotDraw Q;Q.SlotIndex=I;Q.Component=Slot.Component;Q.TexturePath=T?T->GetPathName():Slot.TexturePath;
  Q.KnownOptionalEmpty=Slot.KnownOptionalEmpty;Q.TextureReady=CacheReady(Slot.TexturePath);
  const bool Sword=Slot.Component==EComponent::IndependentSword;const auto Top=Sword?P.SwordTop:P.BodyTop;
  const double Width=Sword?P.WeaponWidth:P.CanvasSize*Trace.Context.UIScale;
  // These exact float values are submitted below; do not replace them in observers
  // with a second geometry calculation from animation elapsed or world position.
  Q.Top={float(Top.X),float(Top.Y)};Q.Size={float(Width),float(Width)};
  Q.UV={float(P.TextureU),0.f};Q.UVSize={float(P.TextureDU),1.f};Q.TraceTint=Trace.Tint;
  Q.RotationDegrees=Sword?double(float(P.WeaponAngle)):0.;Q.RotationPivot=Sword?P.SwordPivotUV:FVector2D::ZeroVector;
  Q.DrawScale=1.;Q.ScalePosition=false;
  Trace.AtomicPreflightReady=Trace.AtomicPreflightReady&&Q.TextureReady&&!Q.KnownOptionalEmpty;Trace.Slots.Add(MoveTemp(Q));
 }
 Record.TextureReady=Record.ArmorReady=Trace.AtomicPreflightReady;
 if(!Trace.AtomicPreflightReady){Trace.MissingReason=TEXT("Dodge4 complete32/sword33 cache resource is not ready; no partial draw");return true;}
 if(!Canvas){Trace.MissingReason=TEXT("Dodge4 plan/resources ready but actual Canvas is absent; no rendered claim");return true;}
 ++Record.DrawId;Trace.DrawId=Record.DrawId;
 for(int32 I=0;I<9;++I)
 {
  auto& Q=Trace.Slots[I];
  DrawTexture(Textures[I],float(Q.Top.X),float(Q.Top.Y),float(Q.Size.X),float(Q.Size.Y),float(Q.UV.X),float(Q.UV.Y),
   float(Q.UVSize.X),float(Q.UVSize.Y),Q.TraceTint,BLEND_Translucent,float(Q.DrawScale),Q.ScalePosition,float(Q.RotationDegrees),Q.RotationPivot);
  Q.Drawn=true;Trace.ActualRenderedStack.Add(Textures[I]->GetPathName());Record.DrawStack.Add(Textures[I]->GetPathName());
  RenderedPlayerDrawStack.Add(Textures[I]->GetPathName());
  FActorQuad Quad;Quad.Owner=F;Quad.Texture=Textures[I];Quad.Top=Q.Top;Quad.Size=float(Q.Size.X);Quad.Tint=Q.TraceTint;
  Quad.Rotation=float(Q.RotationDegrees);Quad.Pivot=Q.RotationPivot;Quad.Weapon=Q.Component==EComponent::IndependentSword;ActorQuads.Add(Quad);
  if(Q.Component==EComponent::ShoulderFar||Q.Component==EComponent::Chest||Q.Component==EComponent::ShoulderNear)RenderedArmorLayerPaths.Add(Textures[I]->GetPathName());
  if(Q.Component==EComponent::IndependentSword)Record.WeaponPath=Textures[I]->GetPathName();
  if(Q.Component==EComponent::BodyRest)Record.TexturePath=RenderedPlayerTexturePath=Textures[I]->GetPathName();
 }
 Trace.Drawn=Trace.ActualRenderedStack.Num()==P.NonemptyDrawCount;
 if(!Trace.Drawn)Trace.MissingReason=TEXT("Dodge4 actual submission count differs from shared complete plan");
 Record.ArmorDrawn=bRenderedArmorLayersUsed=Trace.Drawn;bRenderedWeaponBodyUsed=Trace.Drawn;
 RenderedWeaponBodyClip=Record.Clip;RenderedWeaponBodyFrame=P.Frame;RenderedWeaponBodyFacing=P.Facing;
 RenderedWeaponBodyActionId=P.Dodge.ActionId;RenderedWeaponBodySampleTime=P.Dodge.SampleTime;RenderedWeaponBodyInstanceId=P.Binding.WeaponInstanceId;RenderedWeaponStateIndex=P.Frame;
 return true;
}
