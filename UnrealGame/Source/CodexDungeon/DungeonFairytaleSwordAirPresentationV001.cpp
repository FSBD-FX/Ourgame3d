#include "DungeonHUD.h"
#include "DungeonFighter.h"
#include "DungeonGameMode.h"
#include "DungeonFairytaleSwordAirV001.h"
#include "Engine/Texture2D.h"
#include "Engine/World.h"
#include "TextureResource.h"
#include "UnrealClient.h"
#if WITH_EDITOR
#include "TextureCompiler.h"
#endif

void ADungeonHUD::LoadFairytaleSwordAirTrial()
{
 using namespace DungeonFairytaleSwordAirV001;
 if(!bUseFairytaleSwordAirPreview||!Profile().SourceClosureVerified)return;
 TArray<UTexture*> Pending;
 const auto Load=[this,&Pending](const FString& Path)
 {
  if(Path.IsEmpty()||FairytaleSwordAirTextures.Contains(Path))return;
  UTexture2D* Texture=LoadObject<UTexture2D>(nullptr,*Path);
  FairytaleSwordAirTextures.Add(Path,Texture);
  if(Texture)Pending.Add(Texture);
 };
 // The complete 48 body/armor owners plus existing independent sword finish
 // before the original BeginPlay render flush, even for a None six-slot draw.
 for(const auto& Frame:Profile().Frames)for(const auto& Layer:Frame.Layers)Load(Layer.TexturePath);
 Load(Profile().SwordTexturePath);
#if WITH_EDITOR
 FTextureCompilingManager::Get().FinishCompilation(Pending);
#endif
}

bool ADungeonHUD::DrawFairytaleSwordAirBody(ADungeonFighter* Fighter)
{
 using namespace DungeonFairytaleSwordAirV001;
 if(!bUseFairytaleSwordAirPreview||!Fighter||Fighter->bEnemy||Fighter->bDead)return false;
 // Preserve the real gameplay priorities, including actual airborne attacks.
 // A stale visual name never authorizes a pose over an active native action.
 if(Fighter->AttackTime>0.f||Fighter->GetMeleeCombatState().Action.Active||Fighter->GetWeaponSkillAction().Active
  ||Fighter->GetDodgeState().Phase!=DungeonDodge::EPhase::Idle||Fighter->GetArmorChangeRemaining()>0.f
  ||Fighter->GetEquipmentActionDeadline()>0.||Fighter->AnimationName==TEXT("hurt"))return false;
 const float H=Fighter->JumpHeight,V=Fighter->GetVerticalVelocity(),Age=Fighter->GetLandingVisualAge();
 if(!(H>0.f||V>0.f||(H==0.f&&V==0.f&&Age>=0.f&&Age<.12f)))return false;
 auto& Trace=FairytaleSwordAirDraw;
 Trace.OptIn=true;Trace.PlayerEntityId=Fighter->GetRuntimeEntityId();
 const auto* Game=GetWorld()?GetWorld()->GetAuthGameMode<ADungeonGameMode>():nullptr;
 if(!Game){Trace.MissingReason=TEXT("Nonattack Air actual authority GameMode is absent");return false;}
 DungeonFairytaleSwordEquipmentBinding::FBinding Binding;FString BindingWhy;
 if(!DungeonFairytaleSwordEquipmentBinding::Resolve(*Game,*Fighter,Binding,BindingWhy))
 {Trace.MissingReason=BindingWhy;return false;}
 Trace.SimulationTime=Game->GetSimulationTime();
 const auto GroundPoint=Ground(Fighter->GetGroundPosition());
 Trace.Context.GroundScreen=Screen(float(GroundPoint.X),float(GroundPoint.Y));
 Trace.Context.UIScale=double(UIScale);Trace.Context.JumpHeight=double(H);
 Trace.Tint=Fighter->HitFlash>0.f?FLinearColor(1.7f,.6f,.4f,1.f):FLinearColor::White;Trace.Context.Tint=Trace.Tint;
 const uint64 PreviousDrawId=FairytaleSwordDraw.DrawId;FairytaleSwordDraw=FDungeonFairytaleSwordDraw();auto& Record=FairytaleSwordDraw;
 Record.Active=true;Record.DrawId=PreviousDrawId;Record.EquipmentBoundMode=bUseFairytaleSwordEquipmentBoundPreview;
 Record.EquipmentBindingValid=true;Record.EquipmentBinding=Binding;Record.Clip=TEXT("sword_nonattack_air");
 Record.Facing=Fighter->Facing<0?-1:1;Record.SimulationTime=Trace.SimulationTime;
 Record.NativeScreenshotPath=FScreenshotRequest::IsScreenshotRequested()?FScreenshotRequest::GetFilename():FString();
 bRenderedArmorLayersUsed=false;RenderedArmorLayerPaths.Reset();RenderedPlayerDrawStack.Reset();RenderedPlayerTexturePath.Reset();
 bRenderedWeaponBodyUsed=false;RenderedWeaponBodyFrame=-1;RenderedWeaponBodyFacing=0;RenderedWeaponBodyClip.Reset();
 RenderedWeaponBodyActionId=0;RenderedWeaponBodySampleTime=0.;RenderedWeaponBodyInstanceId=0;RenderedWeaponStateIndex=-1;
 RenderedWeaponBodyEmitScreen=FVector2D::ZeroVector;
 // Supported committed gear with a missing sample/profile/resource owns a
 // closed zero-part branch; do not relabel a bare Ready0 as successful Air.
 if(!BuildDrawPlan(*Game,*Fighter,Trace.Context,Trace.Plan,Trace.MissingReason))
 {Record.EquipmentBindingDiagnostic=Trace.MissingReason;return true;}
 const auto& Plan=Trace.Plan;
 const bool Light=Plan.Binding.Armor==DungeonFairytaleSwordEquipmentBinding::EArmor::LightArmor;
 Record.Supported=Record.ActionPoseSupported=true;Record.InstanceId=Plan.Binding.WeaponInstanceId;
 Record.Frame=Plan.Frame;Record.Facing=Plan.Facing;Record.CanvasSize=Plan.CanvasSize;
 Record.Root=Plan.RootSource;Record.Grip=Plan.GripSource;Record.GripScreen=Plan.GripScreen;Record.WeaponAngle=Plan.WeaponAngle;
 Record.WeaponScale=Plan.WeaponScale;Record.WeaponWidth=Plan.WeaponWidth;Record.ArmorPreview=Light;
 RenderedPlayerSpriteSize=float(Plan.CanvasSize);RenderedActorSpriteSizes.Add(Fighter,float(Plan.CanvasSize));
 const auto CacheReady=[this](const FString& Path)
 {
  const UTexture2D* Texture=FairytaleSwordAirTextures.FindRef(Path);
  return Texture&&Texture->GetClass()==UTexture2D::StaticClass()&&Texture->GetResource()
   &&!Texture->HasPendingRenderResourceInitialization()&&Texture->GetPathName()==Path
   &&Texture->GetSizeX()==512&&Texture->GetSizeY()==512;
 };
 Trace.ResidentTextures.Reserve(ResidentCount);
 const auto AddResident=[&](const FString& Path)
 {
  const UTexture2D* Texture=FairytaleSwordAirTextures.FindRef(Path);FResidentTexture Fact;
  Fact.TexturePath=Texture?Texture->GetPathName():Path;Fact.ClassName=Texture?Texture->GetClass()->GetName():FString();
  Fact.Width=Texture?Texture->GetSizeX():0;Fact.Height=Texture?Texture->GetSizeY():0;
  Fact.ResourceReady=CacheReady(Path);Fact.PendingInitialization=Texture&&Texture->HasPendingRenderResourceInitialization();
  Trace.ResidentTextures.Add(MoveTemp(Fact));
 };
 for(const auto& Frame:Profile().Frames)for(const auto& Layer:Frame.Layers)AddResident(Layer.TexturePath);
 AddResident(Profile().SwordTexturePath);
 Trace.AtomicPreflightReady=ValidateResidentSet(Profile(),Trace.ResidentTextures,Trace.MissingReason);
 TArray<FDungeonFairytaleSwordAirSlotDrawV001> Submitted;
 TArray<UTexture2D*> Textures;Submitted.Reserve(Plan.NonemptyDrawCount);Textures.Reserve(Plan.NonemptyDrawCount);
 for(int32 Index=0;Index<SlotCount;++Index)
 {
  const auto& Slot=Plan.Slots[Index];if(!Slot.Enabled)continue;
  UTexture2D* Texture=FairytaleSwordAirTextures.FindRef(Slot.TexturePath);
  FDungeonFairytaleSwordAirSlotDrawV001 Quad;Quad.SlotIndex=Index;Quad.Component=Slot.Component;
  Quad.TexturePath=Texture?Texture->GetPathName():Slot.TexturePath;Quad.KnownOptionalEmpty=Slot.KnownOptionalEmpty;
  Quad.TextureReady=CacheReady(Slot.TexturePath);Quad.TraceTint=Trace.Tint;
  const bool Sword=Slot.Component==EComponent::IndependentSword;const auto Top=Sword?Plan.SwordTop:Plan.BodyTop;
  const double Width=Sword?Plan.WeaponWidth:Plan.CanvasSize*Trace.Context.UIScale;
  // Exact submitted float geometry; the pivot stays FVector2D double as HUD does.
  Quad.Top={float(Top.X),float(Top.Y)};Quad.Size={float(Width),float(Width)};
  Quad.UV={float(Plan.TextureU),0.f};Quad.UVSize={float(Plan.TextureDU),1.f};
  Quad.RotationDegrees=Sword?double(float(Plan.WeaponAngle)):0.;Quad.RotationPivot=Sword?Plan.SwordPivotUV:FVector2D::ZeroVector;
  Quad.DrawScale=1.;Quad.ScalePosition=false;
  Trace.AtomicPreflightReady=Trace.AtomicPreflightReady&&Quad.TextureReady&&!Quad.KnownOptionalEmpty;
  Submitted.Add(MoveTemp(Quad));Textures.Add(Texture);
 }
 Trace.AtomicPreflightReady=Trace.AtomicPreflightReady&&Submitted.Num()==Plan.NonemptyDrawCount;
 Record.TextureReady=Trace.AtomicPreflightReady;Record.ArmorReady=Light&&Trace.AtomicPreflightReady;
 if(!Trace.AtomicPreflightReady)
 {if(Trace.MissingReason.IsEmpty())Trace.MissingReason=TEXT("Air complete source49 resource preflight failed; zero submitted parts");return true;}
 if(!Canvas){Trace.MissingReason=TEXT("Air full preflight ready but actual Canvas is absent; zero submitted parts");return true;}
 ++Record.DrawId;Trace.DrawId=Record.DrawId;
 for(int32 Index=0;Index<Submitted.Num();++Index)
 {
  auto& Quad=Submitted[Index];UTexture2D* Texture=Textures[Index];
  DrawTexture(Texture,float(Quad.Top.X),float(Quad.Top.Y),float(Quad.Size.X),float(Quad.Size.Y),float(Quad.UV.X),float(Quad.UV.Y),
   float(Quad.UVSize.X),float(Quad.UVSize.Y),Quad.TraceTint,BLEND_Translucent,float(Quad.DrawScale),Quad.ScalePosition,float(Quad.RotationDegrees),Quad.RotationPivot);
  Quad.Drawn=true;Trace.ActualRenderedStack.Add(Texture->GetPathName());Record.DrawStack.Add(Texture->GetPathName());
  RenderedPlayerDrawStack.Add(Texture->GetPathName());
  FActorQuad Occlusion;Occlusion.Owner=Fighter;Occlusion.Texture=Texture;Occlusion.Top=Quad.Top;Occlusion.Size=float(Quad.Size.X);
  Occlusion.Tint=Quad.TraceTint;Occlusion.Rotation=float(Quad.RotationDegrees);Occlusion.Pivot=Quad.RotationPivot;
  Occlusion.Weapon=Quad.Component==EComponent::IndependentSword;ActorQuads.Add(Occlusion);
  if(Quad.Component==EComponent::ShoulderFar||Quad.Component==EComponent::Chest||Quad.Component==EComponent::ShoulderNear)
   RenderedArmorLayerPaths.Add(Texture->GetPathName());
  if(Quad.Component==EComponent::IndependentSword)Record.WeaponPath=Texture->GetPathName();
  if(Quad.Component==EComponent::BodyRest)Record.TexturePath=RenderedPlayerTexturePath=Texture->GetPathName();
  Trace.Slots.Add(MoveTemp(Quad)); // Actual submissions only; failures leave this empty.
 }
 Trace.Drawn=Trace.ActualRenderedStack.Num()==Plan.NonemptyDrawCount;
 if(!Trace.Drawn)Trace.MissingReason=TEXT("Air actual submitted count differs from complete None6/LGT9 plan");
 Record.ArmorDrawn=bRenderedArmorLayersUsed=Light&&Trace.Drawn;bRenderedWeaponBodyUsed=Trace.Drawn;
 RenderedWeaponBodyClip=Record.Clip;RenderedWeaponBodyFrame=Plan.Frame;RenderedWeaponBodyFacing=Plan.Facing;
 RenderedWeaponBodySampleTime=Plan.Sample.NativeTime;RenderedWeaponBodyInstanceId=Plan.Binding.WeaponInstanceId;RenderedWeaponStateIndex=Plan.Frame;
 return true;
}
