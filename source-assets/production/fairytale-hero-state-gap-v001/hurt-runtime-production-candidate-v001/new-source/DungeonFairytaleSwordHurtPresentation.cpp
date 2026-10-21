#include "DungeonHUD.h"
#include "DungeonFighter.h"
#include "DungeonGameMode.h"
#include "DungeonFairytaleSwordHurtPlan.h"
#include "Engine/Texture2D.h"
#include "Engine/World.h"
#include "TextureResource.h"
#include "UnrealClient.h"

bool ADungeonHUD::DrawFairytaleSwordHurtBody(ADungeonFighter* F)
{
 using namespace DungeonFairytaleSwordHurtV001;
 auto& Trace=FairytaleSwordHurtDraw;
 const uint64 PreviousDrawId=FairytaleSwordDraw.DrawId;FairytaleSwordDraw=FDungeonFairytaleSwordDraw();auto& Record=FairytaleSwordDraw;
 Record.Active=true;Record.DrawId=PreviousDrawId;Record.EquipmentBoundMode=bUseFairytaleSwordEquipmentBoundPreview;
 Record.Clip=TEXT("sword_hurt");Record.Facing=F->Facing<0?-1:1;
 Record.NativeScreenshotPath=FScreenshotRequest::IsScreenshotRequested()?FScreenshotRequest::GetFilename():FString();
 const auto Game=GetWorld()?GetWorld()->GetAuthGameMode<ADungeonGameMode>():nullptr;
 Record.SimulationTime=Trace.SimulationTime=Game?Game->GetSimulationTime():F->GetMeleeCombatState().Time;
 Trace.PlayerEntityId=F->GetRuntimeEntityId();Trace.OptIn=bUseFairytaleSwordHurtPreview;
 const auto G=Ground(F->GetGroundPosition());Trace.Context.GroundScreen=Screen(float(G.X),float(G.Y));
 Trace.Context.UIScale=double(UIScale);Trace.Context.JumpHeight=double(F->JumpHeight);
 Trace.Tint=F->HitFlash>0.f?FLinearColor(1.7f,.6f,.4f,1.f):FLinearColor::White;
 // Close the whole candidate path on any failure. No earlier body/armor quad or
 // fallback can hide a missing slot. This source has NO whole Body texture.
 bRenderedArmorLayersUsed=false;RenderedArmorLayerPaths.Reset();RenderedPlayerDrawStack.Reset();RenderedPlayerTexturePath.Reset();
 bRenderedWeaponBodyUsed=false;RenderedWeaponBodyFrame=-1;RenderedWeaponBodyFacing=0;RenderedWeaponBodyClip.Reset();
 RenderedWeaponBodyActionId=0;RenderedWeaponBodySampleTime=0.;RenderedWeaponBodyInstanceId=0;RenderedWeaponStateIndex=-1;
 RenderedWeaponBodyEmitScreen=FVector2D::ZeroVector;
 if(!Game){Trace.MissingReason=TEXT("Hurt4 actual world GameMode is absent");Record.EquipmentBindingDiagnostic=Trace.MissingReason;return true;}
 if(!BuildDrawPlan(*Game,*F,Trace.Context,Trace.Plan,Trace.MissingReason))
 {Record.EquipmentBindingDiagnostic=Trace.MissingReason;return true;}
 const auto& P=Trace.Plan;
 Record.Supported=Record.ActionPoseSupported=true;Record.EquipmentBindingValid=true;Record.EquipmentBinding=P.Binding;
 Record.InstanceId=P.Binding.WeaponInstanceId;Record.Frame=P.Frame;Record.Facing=P.Facing;Record.CanvasSize=P.CanvasSize;
 Record.Root=P.RootSource;Record.Grip=P.GripSource;Record.GripScreen=P.GripScreen;Record.WeaponAngle=P.WeaponAngle;
 Record.WeaponScale=P.WeaponScale;Record.WeaponWidth=P.WeaponWidth;Record.ArmorPreview=true;
 RenderedPlayerSpriteSize=float(P.CanvasSize);RenderedActorSpriteSizes.Add(F,float(P.CanvasSize));
 UTexture2D* Textures[9]={};Trace.AtomicPreflightReady=true;Trace.Slots.Reserve(9);
 const auto CacheReady=[this](const FString& Path)
 {
  UTexture2D* T=Frames.FindRef(Path);
  return T&&T->GetResource()&&!T->HasPendingRenderResourceInitialization()&&T->GetPathName()==Path&&T->GetSizeX()==512&&T->GetSizeY()==512;
 };
 // Admission remains atomic across the whole source row, including the three
 // declared transparent textures and phases that are not selected this draw.
 // A valid current phase must not conceal a missing later phase. Cache only.
 for(const auto& Phase:Profile().Frames)
  for(const auto& Layer:Phase.Layers)
   Trace.AtomicPreflightReady=CacheReady(Layer.TexturePath)&&Trace.AtomicPreflightReady;
 Trace.AtomicPreflightReady=CacheReady(Profile().SwordTexturePath)&&Trace.AtomicPreflightReady;
 for(int32 I=0;I<9;++I)
 {
  const auto& S=P.Slots[I];UTexture2D* T=Frames.FindRef(S.TexturePath);Textures[I]=T;
  FDungeonFairytaleSwordHurtSlotDraw Q;Q.SlotIndex=I;Q.Component=S.Component;Q.TexturePath=T?T->GetPathName():S.TexturePath;
  Q.KnownOptionalEmpty=S.KnownOptionalEmpty;
  Q.TextureReady=CacheReady(S.TexturePath);
  const bool Sword=S.Component==EComponent::IndependentSword;
  const auto Top=Sword?P.SwordTop:P.BodyTop;const double Width=Sword?P.WeaponWidth:P.CanvasSize*Trace.Context.UIScale;
  // Trace the exact float arguments submitted to AHUD::DrawTexture, including
  // the one UV reflection and signed rotation; retain the source plan separately.
  Q.Top=FVector2D(float(Top.X),float(Top.Y));Q.Size=FVector2D(float(Width),float(Width));
  Q.UV=FVector2D(float(P.TextureU),0.f);Q.UVSize=FVector2D(float(P.TextureDU),1.f);
  Q.RotationDegrees=Sword?double(float(P.WeaponAngle)):0.;Q.RotationPivot=Sword?P.SwordPivotUV:FVector2D::ZeroVector;
  Q.DrawScale=1.;Q.ScalePosition=false;
  Trace.AtomicPreflightReady=Trace.AtomicPreflightReady&&Q.TextureReady;Trace.Slots.Add(MoveTemp(Q));
 }
 Record.TextureReady=Record.ArmorReady=Trace.AtomicPreflightReady;
 if(!Trace.AtomicPreflightReady){Trace.MissingReason=TEXT("Hurt4 complete32/sword cache resource is not ready; no partial draw");return true;}
 if(!Canvas){Trace.MissingReason=TEXT("Hurt4 plan/resources ready but actual Canvas is absent; no rendered claim");return true;}
 // The renderer consumes exactly this validated shared plan and slot order.
 ++Record.DrawId;Trace.DrawId=Record.DrawId;
 for(int32 I=0;I<9;++I)
 {
  auto& Q=Trace.Slots[I];if(Q.KnownOptionalEmpty)continue;
  DrawTexture(Textures[I],float(Q.Top.X),float(Q.Top.Y),float(Q.Size.X),float(Q.Size.Y),float(Q.UV.X),float(Q.UV.Y),
   float(Q.UVSize.X),float(Q.UVSize.Y),Trace.Tint,BLEND_Translucent,float(Q.DrawScale),Q.ScalePosition,float(Q.RotationDegrees),Q.RotationPivot);
  Q.Drawn=true;Trace.ActualRenderedStack.Add(Textures[I]->GetPathName());
  Record.DrawStack.Add(Textures[I]->GetPathName());RenderedPlayerDrawStack.Add(Textures[I]->GetPathName());
  FActorQuad Quad;Quad.Owner=F;Quad.Texture=Textures[I];Quad.Top=Q.Top;Quad.Size=float(Q.Size.X);Quad.Tint=Trace.Tint;
  Quad.Rotation=float(Q.RotationDegrees);Quad.Pivot=Q.RotationPivot;Quad.Weapon=Q.Component==EComponent::IndependentSword;ActorQuads.Add(Quad);
  if(Q.Component==EComponent::ShoulderFar||Q.Component==EComponent::Chest||Q.Component==EComponent::ShoulderNear)
   RenderedArmorLayerPaths.Add(Textures[I]->GetPathName());
  if(Q.Component==EComponent::IndependentSword)Record.WeaponPath=Textures[I]->GetPathName();
 }
 Trace.Drawn=Trace.ActualRenderedStack.Num()==P.NonemptyDrawCount;
 if(!Trace.Drawn)Trace.MissingReason=TEXT("Hurt4 actual submission count differs from shared complete plan");
 Record.ArmorDrawn=bRenderedArmorLayersUsed=Trace.Drawn;
 bRenderedWeaponBodyUsed=Trace.Drawn;RenderedWeaponBodyClip=Record.Clip;RenderedWeaponBodyFrame=P.Frame;RenderedWeaponBodyFacing=P.Facing;
 RenderedWeaponBodyActionId=0;RenderedWeaponBodySampleTime=Record.SimulationTime;RenderedWeaponBodyInstanceId=P.Binding.WeaponInstanceId;RenderedWeaponStateIndex=P.Frame;
 return true;
}
