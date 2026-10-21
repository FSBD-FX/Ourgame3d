#include "DungeonHUD.h"
#include "DungeonFighter.h"
#include "DungeonGameMode.h"
#include "DungeonStoneGuardDriver.h"
#include "DungeonFairytaleGuardFullProfileV003.h"
#include "Engine/Texture2D.h"
#include "Kismet/GameplayStatics.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"

void ADungeonHUD::LoadFairytaleGuardFullTrial()
{
 bUseFairytaleGuardFullPreview=FParse::Param(FCommandLine::Get(),TEXT("DungeonFairytaleGuardFullPreview"));
 if(!bUseFairytaleGuardFullPreview)return;
 for(const auto& Row:DungeonFairytaleGuardFullV003::ProfileFull())
 {
  if(Row.IsAlias())continue; // Target row owns the only Texture2D; alias has its own explicit trial gate.
  const FString Gate=DungeonFairytaleGuardFullV003::TrialGateFull(Row);
  if(!Gate.IsEmpty())
  {UE_LOG(LogTemp,Display,TEXT("Guard full-v003 trial: %s unavailable: %s"),UTF8_TO_TCHAR(DungeonFairytaleGuardFullV003::ClipName(Row.Clip)),*Gate);continue;}
  // Preload the complete approved row. Draw requires every frame resident with exact dimensions.
  for(const auto& Frame:Row.Frames)
   if(!Frames.Contains(Frame.TexturePath))
    Frames.Add(Frame.TexturePath,LoadObject<UTexture2D>(nullptr,*Frame.TexturePath));
 }
}

bool ADungeonHUD::DrawFairytaleGuardFullBody(ADungeonFighter* F)
{
 using namespace DungeonFairytaleGuardFullV003;
 if(!bUseFairytaleGuardFullPreview||!F||!F->GetStoneGuardDriver())return false;
 FDungeonFairytaleGuardFullDrawV003 R;R.DrawId=++FairytaleGuardFullDrawSerial;R.OptIn=true;R.EntityId=F->GetRuntimeEntityId();
 const auto& S=F->GetStoneGuardDriver()->State();
 const auto Game=Cast<ADungeonGameMode>(UGameplayStatics::GetGameMode(this));
 // Only terminal death may use the existing central terminal presentation clock.
 const double TerminalAge=Game&&Game->bGameOver&&F->bDead?double(F->AnimationTime):-1.;
 R.Selection=SelectFull(S,TerminalAge);
 const auto Reject=[this,&R](const FString& Why)
 {R.MissingReason=Why;FairytaleGuardFullDraws.Add(R);return false;};
 const FBodyPlan Body=PlanFull(R.Selection);
 R.RequestedClip=UTF8_TO_TCHAR(ClipName(Body.RequestedClip));R.AssetClip=UTF8_TO_TCHAR(ClipName(Body.AssetClip));R.AssetFrame=Body.Frame;
 const FRow* Row=Body.Row;
 if(!Row)return Reject(Body.MissingReason);
 R.NativeSourceId=Row->NativeSourceId;R.RequestedRowTrialAllowed=Body.RequestedRow&&Body.RequestedRow->TrialAllowed;
 R.TrialAllowed=Row->TrialAllowed&&R.RequestedRowTrialAllowed;R.FinalAccepted=Row->FinalAccepted&&Body.RequestedRow&&Body.RequestedRow->FinalAccepted;
 if(Body.RequestedRow)R.RequestedTrialApprovalRecord=Body.RequestedRow->TrialApprovalRecord;
 R.TrialApprovalRecord=Row->TrialApprovalRecord;R.RegistrationEvidenceSHA256=Row->RegistrationEvidenceSHA256;R.SourceIndexSHA256=Row->SourceIndexSHA256;
 R.StandingExtent=Row->StandingExtent;R.TargetBodyHeight=Row->TargetBodyHeight;R.RowScale=Row->Scale();
 R.CanvasSize=Row->CanvasWidth*R.RowScale;
 if(!Body.Valid)return Reject(Body.MissingReason);
 if(Body.WholebodyLayers.Num()!=1)return Reject(TEXT("Fixed axe wholebody must have exactly one layer"));
 R.RegistrationReady=true;
 if(!Row->Frames.IsValidIndex(R.AssetFrame))return Reject(TEXT("Requested native frame absent"));
 for(const auto& Candidate:Row->Frames)
 {
  UTexture2D* T=Frames.FindRef(Candidate.TexturePath);
  if(!T||!T->GetResource()||T->GetSizeX()!=Row->CanvasWidth||T->GetSizeY()!=Row->CanvasHeight)
   return Reject(FString::Printf(TEXT("Complete row not resident / dimensions differ: %s"),*Candidate.TexturePath));
 }
 const auto& Frame=Row->Frames[R.AssetFrame];UTexture2D* Texture=Frames.FindRef(Frame.TexturePath);
 R.TextureReady=true;R.TexturePath=Texture->GetPathName();R.SourceSHA256=Frame.SourceSHA256;R.SourceRGBASHA256=Frame.SourceRGBASHA256;R.SourceFloorPivot=Frame.FloorPivot;R.PivotAuthority=Frame.PivotAuthority;
 if(R.TexturePath!=Frame.TexturePath)return Reject(TEXT("Actual texture object path differs from registered source import"));
 const FVector2D P=Ground(F->GetGroundPosition());
 R.GroundScreen=Screen(float(P.X),float(P.Y));
 const double PivotX=Body.DisplayPivotX;
 R.TopScreen=Screen(float(P.X-PivotX*R.RowScale),float(P.Y-Frame.FloorPivot.Y*R.RowScale));
 Oval(float(P.X-24.),float(P.Y-5.),48.f,10.f,FLinearColor(0,0,0,.25f));
 // Preserve native locked hit geometry; these are telegraphs, not a second axe sprite.
 const auto& A=S.Action;
 if(S.Phase==DungeonStoneGuard::EPhase::Windup||S.Phase==DungeonStoneGuard::EPhase::Active)
 {
  const auto C=A.LockedCenter;const FLinearColor Hint=S.Phase==DungeonStoneGuard::EPhase::Windup
   ?FLinearColor(.95f,.50f,.12f,.55f):FLinearColor(1.f,.72f,.20f,.8f);
  if(A.Kind==DungeonStoneGuard::EAttack::AxeSweep)
  {
   const FVector2D V[]={Ground({C.X,C.Y-65.}),Ground({C.X+180.*A.Facing,C.Y-65.}),
    Ground({C.X+180.*A.Facing,C.Y+65.}),Ground({C.X,C.Y+65.})};
   for(int32 I=0;I<4;++I)Line(float(V[I].X),float(V[I].Y),float(V[(I+1)%4].X),float(V[(I+1)%4].Y),Hint,1.5f);
  }
  else for(int32 I=0;I<32;++I)
  {
   const double T=2.*PI*double(I)/32.,U=2.*PI*double(I+1)/32.;
   const auto V=Ground({C.X+160.*FMath::Cos(T),C.Y+90.*FMath::Sin(T)});
   const auto W=Ground({C.X+160.*FMath::Cos(U),C.Y+90.*FMath::Sin(U)});
   Line(float(V.X),float(V.Y),float(W.X),float(W.Y),Hint,1.5f);
  }
 }
 const float Width=float(R.CanvasSize)*UIScale;
 // Ordinary real positive Damaged receipt permits tint; it never switches to Stunned art.
 const FLinearColor Tint=R.Selection.MaterialHit?FLinearColor(1.45f,.85f,.62f,1.f):FLinearColor::White;
 // Plan has one wholebody layer; no independent axe/grip submission exists.
 DrawTexture(Texture,float(R.TopScreen.X),float(R.TopScreen.Y),Width,Width,
  R.Selection.Facing<0?1.f:0.f,0.f,R.Selection.Facing<0?-1.f:1.f,1.f,Tint);
 FActorQuad Quad;Quad.Owner=F;Quad.Texture=Texture;Quad.Top=R.TopScreen;Quad.Size=Width;Quad.Tint=Tint;
 ActorQuads.Add(Quad);RenderedActorSpriteSizes.Add(F,float(R.CanvasSize));
 R.DrawStack.Add(Texture->GetPathName());R.Drawn=true;R.ProceduralFallback=false;
 FairytaleGuardFullDraws.Add(R);
 DrawGuardFeedback(F); // Existing finite event consumer exactly once; no sound emission here.
 return true; // Wholebody already owns fixed axe and both grips. Skip old procedural body/weapon.
}
