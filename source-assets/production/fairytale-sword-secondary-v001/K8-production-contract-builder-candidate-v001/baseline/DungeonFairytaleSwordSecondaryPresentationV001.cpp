#include "DungeonHUD.h"
#include "DungeonFighter.h"
#include "DungeonGameMode.h"
#include "DungeonFairytaleSwordSecondaryPlanV001.h"
#include "Engine/Texture2D.h"
#include "Engine/World.h"
#include "Misc/PackageName.h"
#include "TextureResource.h"
#include "UnrealClient.h"

namespace DungeonFairytaleSwordSecondaryV001
{
const FProfile& Profile()
{
 // TODO ROOT DATA ADMISSION: replace this WHOLE value with actual measured
 // eight-frame Root/Grip/Axis, 56 layer object paths + source bytes/SHA256,
 // reused sword pin and the reviewed source-contract SHA. Never toggle only
 // RuntimeReady or populate synthetic paths. This is intentionally NOT READY.
 static const FProfile NotAdmitted;
 return NotAdmitted;
}
}

void ADungeonHUD::ResetFairytaleSwordSecondaryDraw()
{
 const uint64 Previous=FairytaleSwordSecondaryDraw.DrawId;
 FairytaleSwordSecondaryDraw=FDungeonFairytaleSwordSecondaryDrawV001();
 FairytaleSwordSecondaryDraw.DrawId=Previous;
 FairytaleSwordSecondaryDraw.OptIn=bUseFairytaleSwordSecondaryPreview;
}

void ADungeonHUD::PreloadFairytaleSwordSecondary(TArray<UTexture*>& Textures)
{
 using namespace DungeonFairytaleSwordSecondaryV001;
 if(!bUseFairytaleSwordSecondaryPreview||!bUseFairytaleSwordEquipmentBoundPreview)return;
 const auto& P=Profile();if(!ProfileValid(P))return;
 const auto Preload=[&](const FLayer& Layer)
 {
  const FString Path=UTF8_TO_TCHAR(Layer.TexturePath);
  UTexture2D* T=Frames.FindRef(Path);
  if(!Frames.Contains(Path))
  {
   const FString Package=FPackageName::ObjectPathToPackageName(Path);
   T=FPackageName::DoesPackageExist(Package)?LoadObject<UTexture2D>(nullptr,*Path):nullptr;
   Frames.Add(Path,T); // Strong UPROPERTY ownership; full object path key.
  }
  if(T)Textures.AddUnique(T);
 };
 for(const auto& F:P.Frames)for(const auto& Layer:F.Layers)Preload(Layer);
 Preload(P.Sword);
 // Caller uses the EXISTING FinishCompilation and startup render flush.
 // Drawing reads this cache only, never loads or waits on the render thread.
}

bool ADungeonHUD::DrawFairytaleSwordSecondaryBody(ADungeonFighter* F)
{
 using namespace DungeonFairytaleSwordSecondaryV001;
 namespace BindingNS=DungeonFairytaleSwordEquipmentBinding;
 if(!F||!bUseFairytaleSwordSecondaryPreview||!bUseFairytaleSwordEquipmentBoundPreview)return false;
 const auto& A=F->GetWeaponSkillAction();
 if(!A.Active||A.Type!=DungeonWeaponActions::EAction::Skill)return false;
 const auto* Game=GetWorld()?GetWorld()->GetAuthGameMode<ADungeonGameMode>():nullptr;
 BindingNS::FBinding Binding;FString Why;
 if(!Game||!BindingNS::Resolve(*Game,*F,Binding,Why))return false;
 // Resolve is the one real owner/instance/skin authorizer for this K draw.
 // Unsupported MED/HVY/ROB/other weapon continues the existing closed path.
 const EArmor Armor=Binding.Armor==BindingNS::EArmor::LightArmor?EArmor::Light:EArmor::None;
 const auto& WA=F->GetWeaponActionsState();
 FContext C;C.OptIn=bUseFairytaleSwordSecondaryPreview;C.EquipmentBound=bUseFairytaleSwordEquipmentBoundPreview;
 C.OwnerAuthorized=true;C.BoundWeaponInstanceId=Binding.WeaponInstanceId;C.Armor=Armor;
 C.Grounded=WA.Budget.Grounded&&F->GetMeleeCombatState().Grounded;
 C.Dead=F->bDead||WA.Budget.Dead;C.Hurt=F->AnimationName==TEXT("hurt");
 C.Dodging=F->GetDodgeState().Phase!=DungeonDodge::EPhase::Idle;
 C.Equipping=F->GetArmorChangeRemaining()>0.f||Game->GetEquipmentView().Action.Active;
 C.MeleeActive=F->GetMeleeCombatState().Action.Active;
 C.WeaponTime=F->GetWeaponSkillTime();C.StateTime=WA.Time;C.SimulationTime=Game->GetSimulationTime();
 C.Height=double(F->JumpHeight);C.VerticalVelocity=double(F->GetVerticalVelocity());
 auto& Trace=FairytaleSwordSecondaryDraw;Trace.Sample=Sample(A,C);
 if(Trace.Sample.Decision==EDecision::PassThrough)return false;
 Trace.OwnsBranch=true;Trace.PlayerEntityId=F->GetRuntimeEntityId();Trace.Binding=Binding;
 Trace.ExpectedDrawCount=SelectedSlotCount(Armor);
 const uint64 Previous=FairytaleSwordDraw.DrawId;FairytaleSwordDraw=FDungeonFairytaleSwordDraw();
 auto& Record=FairytaleSwordDraw;Record.Active=true;Record.DrawId=Previous;
 Record.EquipmentBoundMode=true;Record.EquipmentBindingValid=true;Record.EquipmentBinding=Binding;
 Record.Clip=TEXT("sword_secondary");Record.ActionId=A.ActionId;Record.InstanceId=A.InstanceId;
 Record.SimulationTime=C.SimulationTime;Record.ActionStart=A.Start;Record.ActiveAt=A.ActiveAt;
 Record.ActiveEnd=A.ActiveEnd;Record.ActionEnd=A.End; // Stage remains -1; K is NOT a J AttackId.
 Record.NativeScreenshotPath=FScreenshotRequest::IsScreenshotRequested()?FScreenshotRequest::GetFilename():FString();
 bRenderedArmorLayersUsed=false;RenderedArmorLayerPaths.Reset();RenderedPlayerDrawStack.Reset();RenderedPlayerTexturePath.Reset();
 bRenderedWeaponBodyUsed=false;RenderedWeaponBodyFrame=-1;RenderedWeaponBodyFacing=0;RenderedWeaponBodyClip.Reset();
 RenderedWeaponBodyActionId=0;RenderedWeaponBodySampleTime=0.;RenderedWeaponBodyInstanceId=0;RenderedWeaponStateIndex=-1;
 RenderedWeaponBodyEmitScreen=FVector2D::ZeroVector;
 if(Trace.Sample.Decision!=EDecision::Sampled)
 {
  Trace.MissingReason=FString::Printf(TEXT("Secondary8 actual action/priority/clock rejected (%d); closed draw"),int32(Trace.Sample.Reason));
  Record.EquipmentBindingDiagnostic=Trace.MissingReason;return true;
 }
 const auto& P=Profile();Trace.ProfileReady=ProfileValid(P);
 if(!Trace.ProfileReady)
 {
  Trace.MissingReason=TEXT("Secondary8 final measured/pinned profile is not admitted; runtime_not_ready; no partial draw");
  Record.EquipmentBindingDiagnostic=Trace.MissingReason;return true;
 }
 Trace.ProfileId=UTF8_TO_TCHAR(P.ProfileId);Trace.SourceContractSha256=UTF8_TO_TCHAR(P.SourceContractSha256);
 const auto GroundPoint=Ground(F->GetGroundPosition());const auto ScreenGround=Screen(float(GroundPoint.X),float(GroundPoint.Y));
 Trace.Context.GroundScreen={double(ScreenGround.X),double(ScreenGround.Y)};Trace.Context.UIScale=double(UIScale);
 const auto& Frame=P.Frames[Trace.Sample.Frame];
 if(!Geometry(Frame,Trace.Sample.Facing,Trace.Context,Trace.Geometry))
 {Trace.MissingReason=TEXT("Secondary8 actual screen context or measured marker is invalid; closed draw");return true;}
 const auto& G=Trace.Geometry;
 Record.Supported=Record.ActionPoseSupported=true;Record.Frame=Trace.Sample.Frame;Record.Facing=Trace.Sample.Facing;
 Record.CanvasSize=CanvasSize;Record.Root={Frame.Root.X,Frame.Root.Y};Record.Grip={Frame.Grip.X,Frame.Grip.Y};
 Record.GripScreen={G.GripScreen.X,G.GripScreen.Y};Record.WeaponAngle=G.Angle;Record.WeaponScale=WeaponScale;Record.WeaponWidth=G.SwordWidth;
 Record.ArmorPreview=Armor==EArmor::Light;RenderedPlayerSpriteSize=float(CanvasSize);RenderedActorSpriteSizes.Add(F,float(CanvasSize));
 const auto CacheReady=[&](const FString& Path)
 {
  const UTexture2D* T=Frames.FindRef(Path);
  return T&&T->GetClass()==UTexture2D::StaticClass()&&T->GetPathName()==Path&&T->GetSizeX()==512&&T->GetSizeY()==512
   &&T->GetResource()&&!T->HasPendingRenderResourceInitialization();
 };
 std::array<bool,ClosureCount> Resident{};int32 ResidentIndex=0;Trace.ResidentTextures.Reserve(ClosureCount);
 const auto CheckResident=[&](const FLayer& Layer)
 {
  const FString Path=UTF8_TO_TCHAR(Layer.TexturePath);const UTexture2D* T=Frames.FindRef(Path);
  FDungeonFairytaleSwordSecondaryResidentV001 R;R.TexturePath=T?T->GetPathName():Path;R.ClassName=T?T->GetClass()->GetName():FString();
  R.Width=T?T->GetSizeX():0;R.Height=T?T->GetSizeY():0;R.Ready=CacheReady(Path);R.PendingInitialization=T&&T->HasPendingRenderResourceInitialization();
  Resident[ResidentIndex++]=R.Ready;Trace.ResidentTextures.Add(MoveTemp(R));
 };
 // Full future closure is required even for None: K0 cannot hide missing K7.
 for(const auto& Future:P.Frames)for(const auto& Layer:Future.Layers)CheckResident(Layer);
 CheckResident(P.Sword);Trace.AtomicPreflightReady=AllResident(Resident);
 UTexture2D* Textures[SlotCount]={};Trace.Slots.Reserve(SlotCount);
 const FLinearColor Tint=F->HitFlash>0.f?FLinearColor(1.7f,.6f,.4f,1.f):FLinearColor::White;
 for(int32 I=0;I<SlotCount;++I)
 {
  const bool Sword=I==6;const FLayer& Layer=Sword?P.Sword:Frame.Layers[I<6?I:6];
  const FString Path=UTF8_TO_TCHAR(Layer.TexturePath);Textures[I]=Frames.FindRef(Path);
  FDungeonFairytaleSwordSecondarySlotV001 Q;Q.SlotIndex=I;Q.Component=static_cast<EComponent>(I);
  Q.TexturePath=Textures[I]?Textures[I]->GetPathName():Path;Q.Selected=SelectedSlot(Armor,I);Q.TextureReady=CacheReady(Path);
  const FPoint Top=Sword?G.SwordTop:G.BodyTop;const double Width=Sword?G.SwordWidth:G.BodyWidth;
  // Store precisely the float parameters actually sent to DrawTexture below.
  Q.Top={float(Top.X),float(Top.Y)};Q.Size={float(Width),float(Width)};Q.UV={float(G.U),0.f};Q.UVSize={float(G.DU),1.f};
  Q.RotationDegrees=Sword?float(G.Angle):0.f;Q.RotationPivot=Sword?FVector2D(float(G.SwordPivot.X),float(G.SwordPivot.Y)):FVector2D::ZeroVector;
  Q.Tint=Tint;Trace.Slots.Add(MoveTemp(Q));
 }
 Record.TextureReady=Record.ArmorReady=Trace.AtomicPreflightReady;
 if(!Trace.AtomicPreflightReady){Trace.MissingReason=TEXT("Secondary8 complete56/sword57 cache is not ready; no partial draw");return true;}
 if(!Canvas){Trace.MissingReason=TEXT("Secondary8 actual Canvas absent; no rendered claim");return true;}
 ++Record.DrawId;Trace.DrawId=Record.DrawId;
 for(int32 I=0;I<SlotCount;++I)
 {
  auto& Q=Trace.Slots[I];if(!Q.Selected)continue;
  DrawTexture(Textures[I],float(Q.Top.X),float(Q.Top.Y),float(Q.Size.X),float(Q.Size.Y),float(Q.UV.X),float(Q.UV.Y),
   float(Q.UVSize.X),float(Q.UVSize.Y),Q.Tint,BLEND_Translucent,Q.DrawScale,Q.ScalePosition,Q.RotationDegrees,Q.RotationPivot);
  Q.Drawn=true;Trace.ActualRenderedStack.Add(Q.TexturePath);Record.DrawStack.Add(Q.TexturePath);RenderedPlayerDrawStack.Add(Q.TexturePath);
  FActorQuad Quad;Quad.Owner=F;Quad.Texture=Textures[I];Quad.Top=Q.Top;Quad.Size=float(Q.Size.X);Quad.Rotation=Q.RotationDegrees;
  Quad.Pivot=Q.RotationPivot;Quad.Tint=Q.Tint;Quad.Weapon=I==6;ActorQuads.Add(Quad);
  if(I==1||I==2||I==4)RenderedArmorLayerPaths.Add(Q.TexturePath);
  if(I==0)Record.TexturePath=RenderedPlayerTexturePath=Q.TexturePath;
  if(I==6)Record.WeaponPath=Q.TexturePath;
 }
 Trace.Drawn=Trace.ActualRenderedStack.Num()==Trace.ExpectedDrawCount;
 if(!Trace.Drawn)Trace.MissingReason=TEXT("Secondary8 actual submission count differs from selected None5/LGT8 slots");
 Record.ArmorDrawn=bRenderedArmorLayersUsed=Trace.Drawn&&Armor==EArmor::Light;bRenderedWeaponBodyUsed=Trace.Drawn;
 RenderedWeaponBodyClip=Record.Clip;RenderedWeaponBodyFrame=Record.Frame;RenderedWeaponBodyFacing=Record.Facing;
 RenderedWeaponBodyActionId=A.ActionId;RenderedWeaponBodySampleTime=C.WeaponTime;RenderedWeaponBodyInstanceId=A.InstanceId;RenderedWeaponStateIndex=Record.Frame;
 return true;
}
