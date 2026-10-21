#include "DungeonHUD.h"
#include "DungeonFighter.h"
#include "DungeonStoneGuardDriver.h"
#include "Engine/Texture2D.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
#if WITH_EDITOR
#include "TextureCompiler.h"
#endif

void ADungeonHUD::LoadFairytaleGuardMoveRigTrial()
{
 using namespace DungeonFairytaleGuardMoveRigV001;
 bUseFairytaleGuardMoveRigPreview=FParse::Param(FCommandLine::Get(),CommandLineFlag);
 if(!bUseFairytaleGuardMoveRigPreview)return;
 const auto& P=Profile();
 if(!P.SourceClosureVerified||!P.TrialAllowed||P.FinalAccepted||P.TrialApprovalRecord.IsEmpty()||P.Sources.Num()!=7)return;
 TArray<UTexture*> Textures;
 for(const auto& S:P.Sources)
 {
  if(!Frames.Contains(S.TexturePath))Frames.Add(S.TexturePath,LoadObject<UTexture2D>(nullptr,*S.TexturePath));
  if(auto* Texture=Frames.FindRef(S.TexturePath).Get())Textures.Add(Texture);
 }
#if WITH_EDITOR
 // Complete all seven before BeginPlay's existing render flush and observer.
 FTextureCompilingManager::Get().FinishCompilation(Textures);
#endif
}

bool ADungeonHUD::DrawFairytaleGuardMoveRigBody(ADungeonFighter* F)
{
 using namespace DungeonFairytaleGuardMoveRigV001;
 if(!bUseFairytaleGuardMoveRigPreview||!F||!F->GetStoneGuardDriver())return false;
 // Other native phases continue through the existing Stomp50 Full renderer.
 // Genuine Move failure is recorded with zero parts and reaches the existing
 // grey procedural fallback; it cannot borrow a Ready resource or partial rig.
 const auto Native=DungeonFairytaleGuardFullV003::SelectFull(F->GetStoneGuardDriver()->State());
 if(!Native.Valid||Native.Clip!=DungeonFairytaleGuardFullV003::EClip::Move)return false;
 const auto& P=Profile();FDungeonFairytaleGuardMoveRigDrawV001 R;
 R.DrawId=++FairytaleGuardMoveRigDrawSerial;R.EntityId=F->GetRuntimeEntityId();R.OptIn=true;
 R.TrialAllowed=P.TrialAllowed;R.FinalAccepted=P.FinalAccepted;
 R.RegistrationReady=P.SourceClosureVerified&&P.TrialAllowed&&!P.FinalAccepted&&!P.TrialApprovalRecord.IsEmpty()&&P.Sources.Num()==7;
 R.Plan.RequiredResources=7;R.Plan.TrialApprovalRecord=P.TrialApprovalRecord;
 const auto Reject=[this,&R](const FString& Why)
 {R.MissingReason=Why;FairytaleGuardMoveRigDraws.Add(MoveTemp(R));return false;};
 FDungeonGuardMoveSample Sample;
 if(!F->QueryCompletedGuardMove(Sample))return Reject(TEXT("Actual completed Guard owner/run/room/time/root/facing Move query rejected"));
 R.Plan.Sample=Sample;
 for(const auto& S:P.Sources)
 {
  UTexture2D* Texture=Frames.FindRef(S.TexturePath);
  FResidentTexture Resident;Resident.Component=S.Component;
  Resident.TexturePath=Texture?Texture->GetPathName():S.TexturePath;Resident.ClassName=Texture?Texture->GetClass()->GetName():FString();
  Resident.Width=Texture?Texture->GetSizeX():0;Resident.Height=Texture?Texture->GetSizeY():0;
  Resident.ResourceReady=Texture&&Texture->GetResource();Resident.PendingInitialization=Texture&&Texture->HasPendingRenderResourceInitialization();
  // These source pins bind the independently verified native import. Readiness
  // below is observed from this actual Texture2D, never inferred from the pins.
  Resident.SourceSHA256=S.SourceSHA256;Resident.SourceRGBASHA256=S.SourceRGBASHA256;
  R.Plan.Residents.Add(MoveTemp(Resident));
 }
 const FVector2D WorldScreen=Ground(F->GetGroundPosition());FDrawContext Context;
 Context.GroundScreen=Screen(float(WorldScreen.X),float(WorldScreen.Y));Context.UIScale=double(UIScale);Context.JumpHeight=double(F->JumpHeight);
 FDrawPlan Plan;FString Why;
 if(!PlanFromSample(Sample,P,R.Plan.Residents,Context,Plan,Why))return Reject(Why);
 // Resolve every exact pointer once before any submission. There is no load,
 // resource mutation or observer callback between this preflight and DrawTexture.
 TArray<UTexture2D*> OrderedTextures;
 for(const auto& Part:Plan.Rig.Parts)
 {
  UTexture2D* Texture=Frames.FindRef(Part.TexturePath);
  if(!Texture||Texture->GetPathName()!=Part.TexturePath||Texture->GetClass()!=UTexture2D::StaticClass()
   ||Texture->GetSizeX()!=512||Texture->GetSizeY()!=512||!Texture->GetResource()||Texture->HasPendingRenderResourceInitialization())
   return Reject(TEXT("Move7 final atomic native Texture2D preflight failed"));
  OrderedTextures.Add(Texture);
 }
 if(OrderedTextures.Num()!=7||Plan.Rig.Parts.Num()!=7)return Reject(TEXT("Move7 final complete layer plan missing"));
 R.Plan=MoveTemp(Plan);R.TextureReady=true;
 Oval(float(WorldScreen.X-24.),float(WorldScreen.Y-5.),48.f,10.f,FLinearColor(0,0,0,.25f));
 for(int32 I=0;I<R.Plan.Rig.Parts.Num();++I)
 {
  const auto& Part=R.Plan.Rig.Parts[I];const auto& Q=Part.Quad;UTexture2D* Texture=OrderedTextures[I];
  DrawTexture(Texture,Q.X,Q.Y,Q.Width,Q.Height,Q.U,Q.V,Q.UL,Q.VL,Q.Tint,BLEND_Translucent,
   Q.DrawScale,Q.ScalePosition,Q.RotationDegrees,Q.RotationPivotUV);
  FDungeonFairytaleGuardMoveSubmittedPartV001 Submitted;
  Submitted.Component=Part.Component;Submitted.TexturePath=Texture->GetPathName();Submitted.SourceSHA256=Part.SourceSHA256;
  Submitted.SourceRGBASHA256=Part.SourceRGBASHA256;Submitted.NativeBatchId=Part.NativeBatchId;Submitted.Quad=Q;Submitted.Submitted=true;
  R.Parts.Add(MoveTemp(Submitted));
  if(Part.Component==EComponent::BodyRest)
  {
   // Legacy outline masks assume unrotated square enemy quads. Register only
   // Rest body; rotated leg occlusion outlines remain an explicit trial limit.
   FActorQuad Quad;Quad.Owner=F;Quad.Texture=Texture;Quad.Top={Q.X,Q.Y};Quad.Size=Q.Width;Quad.Tint=Q.Tint;
   ActorQuads.Add(Quad);
  }
 }
 RenderedActorSpriteSizes.Add(F,float(512.*P.TargetBodyHeight/P.StandingExtent));
 R.Drawn=true;R.ProceduralFallback=false;FairytaleGuardMoveRigDraws.Add(MoveTemp(R));
 DrawGuardFeedback(F); // Existing event consumer once; no new sound or gameplay event.
 return true;
}
