#include "DungeonHeroAirProductionProbeV001.h"
#include "DungeonGameMode.h"
#include "DungeonFighter.h"
#include "DungeonHUD.h"
#include "DungeonContentProbe.h"
#include "DungeonNativeMainSubmixCaptureV001.h"
#include "DungeonFairytaleSwordEquipmentBinding.h"
#include "DungeonFairytaleSwordAirV001.h"
#include "DungeonProofScreenshots.h"
#include "Engine/Engine.h"
#include "Engine/Texture2D.h"
#include "TextureResource.h"
#include "RenderingThread.h"
#include "RHICommandList.h"
#include "Misc/Crc.h"
#include "Engine/World.h"
#include "EngineUtils.h"
#include "GameFramework/PlayerController.h"
#include "GameFramework/PlayerInput.h"
#include "Kismet/GameplayStatics.h"
#include "UnrealClient.h"
#include "HAL/FileManager.h"
#include "HAL/PlatformMisc.h"
#include "HAL/PlatformProcess.h"
#include "HAL/PlatformTime.h"
#include "Misc/App.h"
#include "Misc/CommandLine.h"
#include "Misc/FileHelper.h"
#include "Misc/Parse.h"
#include "Misc/Paths.h"
#include "Dom/JsonObject.h"
#include "Serialization/JsonSerializer.h"
#include "Serialization/JsonWriter.h"
#if PLATFORM_WINDOWS
#include "Windows/AllowWindowsPlatformTypes.h"
#include <Windows.h>
#include "Windows/HideWindowsPlatformTypes.h"
#endif

namespace
{
using JO=TSharedPtr<FJsonObject>;using JV=TSharedPtr<FJsonValue>;
namespace Air=DungeonFairytaleSwordAirV001;
constexpr const TCHAR* ExpectedClosure=TEXT("5df0479bd1689b8adeb525255e748db13288839bbc1b8523f7ec012f404bdaec");
bool WriteNewBytes(const FString& Path,const uint8* Bytes,uint64 Length)
{
#if PLATFORM_WINDOWS
 if(Length>MAX_uint32)return false;
 HANDLE File=::CreateFileW(*Path,GENERIC_WRITE,0,nullptr,CREATE_NEW,FILE_ATTRIBUTE_NORMAL,nullptr);
 if(File==INVALID_HANDLE_VALUE)return false;
 DWORD Written=0;const bool Ok=::WriteFile(File,Bytes,DWORD(Length),&Written,nullptr)!=0&&Written==Length&&::FlushFileBuffers(File)!=0;
 ::CloseHandle(File);return Ok; // Failed partial bytes are preserved, never replaced.
#else
 return false;
#endif
}
bool WriteNewUTF8(const FString& Path,const FString& Text)
{
#if PLATFORM_WINDOWS
 const FTCHARToUTF8 UTF8(*Text,Text.Len());
 HANDLE File=::CreateFileW(*Path,GENERIC_WRITE,0,nullptr,CREATE_NEW,FILE_ATTRIBUTE_NORMAL,nullptr);
 if(File==INVALID_HANDLE_VALUE)return false;
 DWORD Written=0;const DWORD Length=DWORD(UTF8.Length());
 const bool Ok=::WriteFile(File,UTF8.Get(),Length,&Written,nullptr)!=0&&Written==Length&&::FlushFileBuffers(File)!=0;
 ::CloseHandle(File);return Ok; // Failed partial bytes remain owned evidence; never overwrite/retry.
#else
 return false; // This isolated native proof contract is Windows-only.
#endif
}
TArray<JV> XY(FVector2D V){return {MakeShared<FJsonValueNumber>(V.X),MakeShared<FJsonValueNumber>(V.Y)};}
TArray<JV> Strings(const TArray<FString>& V){TArray<JV> A;for(const auto& S:V)A.Add(MakeShared<FJsonValueString>(S));return A;}
void Id(JO O,const TCHAR* Key,uint64 V){O->SetStringField(Key,FString::Printf(TEXT("%llu"),V));}
int32 PhysicalPose(float H,float V,float Age)
{if(H>0.f||V>0.f)return V>315.f?0:V>90.f?1:V>=-90.f?2:3;return H==0.f&&V==0.f&&Age>=0.f&&Age<.12f?(Age<.06f?4:5):-1;}
bool SwordDrawn(const FDungeonFairytaleSwordDraw& D){return !D.WeaponPath.IsEmpty()&&D.DrawStack.Contains(D.WeaponPath);}
JO OldDraw(const FDungeonFairytaleSwordDraw& D)
{
 auto O=MakeShared<FJsonObject>();Id(O,TEXT("draw_id"),D.DrawId);O->SetNumberField(TEXT("sim"),D.SimulationTime);O->SetStringField(TEXT("clip"),D.Clip);O->SetNumberField(TEXT("frame"),D.Frame);O->SetNumberField(TEXT("facing"),D.Facing);
 O->SetBoolField(TEXT("active"),D.Active);O->SetBoolField(TEXT("supported"),D.Supported);O->SetBoolField(TEXT("action_pose_supported"),D.ActionPoseSupported);O->SetBoolField(TEXT("gear_placeholder"),D.GearPlaceholder);O->SetBoolField(TEXT("texture_ready"),D.TextureReady);
 O->SetBoolField(TEXT("armor_drawn"),D.ArmorDrawn);O->SetBoolField(TEXT("sword_drawn"),SwordDrawn(D));O->SetStringField(TEXT("body_texture"),D.TexturePath);O->SetStringField(TEXT("sword_texture"),D.WeaponPath);O->SetArrayField(TEXT("actual_stack"),Strings(D.DrawStack));
 O->SetArrayField(TEXT("root_source"),XY(D.Root));O->SetArrayField(TEXT("grip_source"),XY(D.Grip));O->SetArrayField(TEXT("grip_screen"),XY(D.GripScreen));O->SetNumberField(TEXT("canvas_size"),D.CanvasSize);
 if(auto* T=FindObject<UTexture2D>(nullptr,*D.TexturePath)){O->SetStringField(TEXT("body_class"),T->GetClass()->GetName());O->SetNumberField(TEXT("body_width"),T->GetSizeX());O->SetNumberField(TEXT("body_height"),T->GetSizeY());O->SetBoolField(TEXT("body_resource_ready"),T->GetResource()!=nullptr);O->SetBoolField(TEXT("body_pending_initialization"),T->HasPendingRenderResourceInitialization());}
 return O;
}
JO NewDraw(const FDungeonFairytaleSwordAirDrawV001& D)
{
 const auto& P=D.Plan;const auto& Q=P.Sample;const auto& B=P.Binding;
 auto O=MakeShared<FJsonObject>();Id(O,TEXT("draw_id"),D.DrawId);Id(O,TEXT("player_entity"),D.PlayerEntityId);O->SetNumberField(TEXT("sim"),D.SimulationTime);O->SetBoolField(TEXT("opt_in"),D.OptIn);O->SetBoolField(TEXT("drawn"),D.Drawn);O->SetBoolField(TEXT("atomic_preflight_ready"),D.AtomicPreflightReady);O->SetStringField(TEXT("missing_reason"),D.MissingReason);
 O->SetBoolField(TEXT("supported"),P.Supported);O->SetStringField(TEXT("profile"),P.ProfileId);O->SetNumberField(TEXT("frame"),P.Frame);O->SetNumberField(TEXT("pose"),int32(P.Pose));O->SetNumberField(TEXT("facing"),P.Facing);O->SetNumberField(TEXT("nonempty_count"),P.NonemptyDrawCount);
 O->SetBoolField(TEXT("sample_valid"),Q.Valid);O->SetStringField(TEXT("sample_run"),Q.RunGuid.ToString(EGuidFormats::Digits));Id(O,TEXT("sample_owner"),Q.OwnerId);Id(O,TEXT("sample_room"),Q.RoomInstanceId);Id(O,TEXT("sample_epoch"),Q.PresentationEpoch);O->SetNumberField(TEXT("sample_native_time"),Q.NativeTime);O->SetArrayField(TEXT("sample_ground"),XY(Q.GroundPosition));O->SetNumberField(TEXT("sample_H"),Q.JumpHeight);O->SetNumberField(TEXT("sample_V"),Q.VerticalVelocity);O->SetNumberField(TEXT("sample_landing_age"),Q.LandingVisualAge);
 O->SetStringField(TEXT("binding_run"),B.RunGuid.ToString(EGuidFormats::Digits));Id(O,TEXT("binding_owner"),B.OwnerId);Id(O,TEXT("weapon_instance"),B.WeaponInstanceId);Id(O,TEXT("weapon_version"),B.WeaponVersion);Id(O,TEXT("armor_instance"),B.ArmorInstanceId);Id(O,TEXT("armor_version"),B.ArmorVersion);O->SetNumberField(TEXT("armor_kind"),int32(B.Armor));O->SetStringField(TEXT("weapon_content"),B.WeaponContentId);O->SetStringField(TEXT("armor_content"),B.ArmorContentId);
 O->SetArrayField(TEXT("context_ground"),XY(D.Context.GroundScreen));O->SetNumberField(TEXT("ui_scale"),D.Context.UIScale);O->SetNumberField(TEXT("jump_height"),D.Context.JumpHeight);O->SetArrayField(TEXT("root_source"),XY(P.RootSource));O->SetArrayField(TEXT("grip_source"),XY(P.GripSource));O->SetArrayField(TEXT("axis_artist"),XY(P.AxisArtist));O->SetArrayField(TEXT("body_top"),XY(P.BodyTop));O->SetArrayField(TEXT("grip_screen"),XY(P.GripScreen));O->SetArrayField(TEXT("sword_top"),XY(P.SwordTop));O->SetArrayField(TEXT("sword_pivot_uv"),XY(P.SwordPivotUV));O->SetNumberField(TEXT("canvas_size"),P.CanvasSize);O->SetNumberField(TEXT("source_to_screen_scale"),P.SourceToScreenScale);O->SetNumberField(TEXT("weapon_scale"),P.WeaponScale);O->SetNumberField(TEXT("weapon_width"),P.WeaponWidth);O->SetNumberField(TEXT("weapon_angle"),P.WeaponAngle);O->SetNumberField(TEXT("texture_u"),P.TextureU);O->SetNumberField(TEXT("texture_du"),P.TextureDU);
 TArray<JV> Tint;for(double V:{double(D.Tint.R),double(D.Tint.G),double(D.Tint.B),double(D.Tint.A)})Tint.Add(MakeShared<FJsonValueNumber>(V));O->SetArrayField(TEXT("tint"),Tint);
 O->SetNumberField(TEXT("slot_count"),D.Slots.Num());O->SetNumberField(TEXT("resident_count"),D.ResidentTextures.Num());O->SetArrayField(TEXT("actual_stack"),Strings(D.ActualRenderedStack));TArray<JV> Slots;
 for(const auto& S:D.Slots){auto X=MakeShared<FJsonObject>();X->SetNumberField(TEXT("slot"),S.SlotIndex);X->SetNumberField(TEXT("component"),int32(S.Component));X->SetStringField(TEXT("texture"),S.TexturePath);X->SetBoolField(TEXT("drawn"),S.Drawn);X->SetBoolField(TEXT("known_empty"),S.KnownOptionalEmpty);X->SetBoolField(TEXT("texture_ready"),S.TextureReady);X->SetArrayField(TEXT("top"),XY(S.Top));X->SetArrayField(TEXT("size"),XY(S.Size));X->SetArrayField(TEXT("uv"),XY(S.UV));X->SetArrayField(TEXT("uv_size"),XY(S.UVSize));X->SetNumberField(TEXT("rotation"),S.RotationDegrees);X->SetArrayField(TEXT("rotation_pivot"),XY(S.RotationPivot));X->SetNumberField(TEXT("draw_scale"),S.DrawScale);X->SetBoolField(TEXT("scale_position"),S.ScalePosition);TArray<JV> C;for(double V:{double(S.TraceTint.R),double(S.TraceTint.G),double(S.TraceTint.B),double(S.TraceTint.A)})C.Add(MakeShared<FJsonValueNumber>(V));X->SetArrayField(TEXT("trace_tint"),C);Slots.Add(MakeShared<FJsonValueObject>(X));}
 O->SetArrayField(TEXT("slots"),Slots);TArray<JV> Residents;for(const auto& T:D.ResidentTextures){auto X=MakeShared<FJsonObject>();X->SetStringField(TEXT("texture"),T.TexturePath);X->SetStringField(TEXT("class"),T.ClassName);X->SetNumberField(TEXT("width"),T.Width);X->SetNumberField(TEXT("height"),T.Height);X->SetBoolField(TEXT("resource_ready"),T.ResourceReady);X->SetBoolField(TEXT("pending_initialization"),T.PendingInitialization);Residents.Add(MakeShared<FJsonValueObject>(X));}O->SetArrayField(TEXT("resident_textures"),Residents);return O;
}
}

struct FDungeonHeroAirProductionProofStateV001
{
 FString Directory,Failure;int32 Side=0,Phase=0,JumpInputs=0,AirTransitions=0,LandingTransitions=0,NoArmorFrames=0,LightFrames=0,LandingFrames=0,ReadyJoinFrames=0;
 bool Stopped=false,EvidenceClaimed=false,PrewarmRequested=false,PrewarmDone=false,AudioRequested=false,Capturing=false,Stopping=false,FlowComplete=false;
 bool PreviousAir=false,FirstLandingObserved=false,SecondLandingObserved=false,ThirdLandingObserved=false,GearPinned=false,KnightCleared=false,AllowKnightDiagnostic=false,StartupReadbackComplete=false,RejumpIssuedInsideLanding=false;
 double WarmStarted=0.,Start=0.,Stop=0.,ReleaseAt=0.,NeutralUntil=0.,PhaseAt=0.,InitialHP=0.,CaptureFinalHP=0.,StartupReadbackStop=0.,RejumpInputLandingAge=-1.;
 FKey PulseKey;TMap<FKey,bool> Keys;uint32 NoArmorMask=0,LightFirstMask=0,LightSecondMask=0;uint64 LastNewDraw=0;
 TWeakObjectPtr<ADungeonGameMode> Game;TWeakObjectPtr<APlayerController> Controller;TWeakObjectPtr<ADungeonHUD> HUD;
 FGuid Run;uint64 Owner=0,Room=0,Epoch=0,Restart=0,LightSource=0,Light=0,Sword=0,SwordVersion=0,LightVersion=0;
 TArray<JV> Inputs,Steps,Observations,Offsets,DiagnosticHits,StartupTextures;

 void Next(int32 P){Phase=P;PhaseAt=FPlatformTime::Seconds();auto O=MakeShared<FJsonObject>();O->SetNumberField(TEXT("phase"),P);O->SetNumberField(TEXT("wall_offset_s"),PhaseAt-Start);O->SetNumberField(TEXT("sim"),Game.IsValid()?Game->GetSimulationTime():0.);Steps.Add(MakeShared<FJsonValueObject>(O));}
 bool Need(bool Yes,const FString& Why){if(!Yes&&Failure.IsEmpty())Failure=Why;return Yes;}
 void Key(FKey K,bool Down)
 {
  if(!Controller.IsValid()||Keys.FindRef(K)==Down)return;
  auto P=Game.IsValid()?Game->PlayerFighter.Get():nullptr;auto O=MakeShared<FJsonObject>();
  if(P){O->SetNumberField(TEXT("before_H"),P->JumpHeight);O->SetNumberField(TEXT("before_V"),P->GetVerticalVelocity());O->SetNumberField(TEXT("before_landing_age"),P->GetLandingVisualAge());}
  O->SetNumberField(TEXT("wall_offset_s"),FPlatformTime::Seconds()-Start);O->SetNumberField(TEXT("sim"),Game.IsValid()?Game->GetSimulationTime():0.);
  Controller->InputKey(FInputKeyParams(K,Down?IE_Pressed:IE_Released,Down?1.:0.));Keys.Add(K,Down);
  O->SetStringField(TEXT("key"),K.GetFName().ToString());O->SetBoolField(TEXT("down"),Down);
  if(P){O->SetNumberField(TEXT("after_H"),P->JumpHeight);O->SetNumberField(TEXT("after_V"),P->GetVerticalVelocity());O->SetNumberField(TEXT("after_landing_age"),P->GetLandingVisualAge());}
  Inputs.Add(MakeShared<FJsonValueObject>(O));
 }
 bool CanPulse()const{return !PulseKey.IsValid()&&FPlatformTime::Seconds()>=NeutralUntil;}
 bool Pulse(FKey K){if(!CanPulse())return false;Key(K,true);PulseKey=K;ReleaseAt=FPlatformTime::Seconds()+.04;return true;}
 void ReleaseKeys(){TArray<FKey> Held;Keys.GetKeys(Held);for(FKey K:Held)Key(K,false);PulseKey=FKey();}
 void BeginStop(ADungeonHeroAirProductionProbeV001& Actor)
 {
  if(Stopping||Stopped)return;Stopping=true;Capturing=false;GIsDumpingMovie=0;ReleaseKeys();
  if(Actor.MainMixCapture)
  {
   const auto MixPhase=Actor.MainMixCapture->Status().Phase;
   if(MixPhase==EDungeonNativeMixCapturePhaseV001::Recording||MixPhase==EDungeonNativeMixCapturePhaseV001::ExportPending)
   {if(!Actor.MainMixCapture->Stop())Need(false,TEXT("Native main mix could not stop after final actual callback"));}
   else if(!Actor.MainMixCapture->IsTerminal())Actor.MainMixCapture->Abort(Failure.IsEmpty()?TEXT("Capture stopped before Recording"):Failure);
   Stop=Actor.MainMixCapture->Status().StopMonotonic;
  }
  if(Stop<=0.)Stop=FPlatformTime::Seconds();
 }
 bool ClearKnightIfRequested(ADungeonFighter* Player,const FDungeonFirstBatchGuardRoomView& View)
 {
  if(!AllowKnightDiagnostic||KnightCleared)return true;
  ADungeonFighter* Knight=nullptr;for(auto E:Game->Enemies)if(E&&E->GetRuntimeEntityId()==View.Slots[0].EntityId)Knight=E;
  if(!Need(Knight&&Knight->GetStoneKnightDriver()&&!Knight->GetStoneGuardDriver()&&Knight->EnemyContentId==TEXT("ENM-STN-001"),TEXT("Explicit diagnostic requires the actual first Knight only")))return false;
  if(Knight->bDead){KnightCleared=true;return true;}if(!Knight->CanReceiveDirectHit())return false;
  auto O=MakeShared<FJsonObject>();Id(O,TEXT("entity"),Knight->GetRuntimeEntityId());O->SetStringField(TEXT("content"),Knight->EnemyContentId);O->SetStringField(TEXT("api"),TEXT("ADungeonFighter::ApplyCombatHit"));O->SetBoolField(TEXT("explicit_cli_authorization"),true);O->SetNumberField(TEXT("sim"),Game->GetSimulationTime());O->SetNumberField(TEXT("before_hp"),Knight->Health);
  Knight->ApplyCombatHit(100000.f,Player,85.f);O->SetNumberField(TEXT("after_hp"),Knight->Health);O->SetBoolField(TEXT("dead"),Knight->bDead);DiagnosticHits.Add(MakeShared<FJsonValueObject>(O));KnightCleared=Knight->bDead;return Need(KnightCleared,TEXT("Public predecessor diagnostic did not complete; no HP assignment fallback"));
 }
 bool PinGear(ADungeonFighter* P)
 {
  DungeonFairytaleSwordEquipmentBinding::FBinding B;FString Why;if(!DungeonFairytaleSwordEquipmentBinding::Resolve(*Game.Get(),*P,B,Why))return Need(false,TEXT("Actual committed SWD/LGT binding: ")+Why);
  if(!Need(B.Armor==DungeonFairytaleSwordEquipmentBinding::EArmor::LightArmor&&B.ArmorInstanceId==Light&&B.WeaponContentId==TEXT("WPN-SWD-001"),TEXT("Real E did not commit the requested SWD/LGT pair")))return false;
  if(!GearPinned){if(!Need(B.WeaponInstanceId==Sword&&B.WeaponVersion==SwordVersion,TEXT("Normal E changed the pinned starter sword")))return false;LightVersion=B.ArmorVersion;GearPinned=true;}
  return Need(B.WeaponInstanceId==Sword&&B.WeaponVersion==SwordVersion&&B.ArmorInstanceId==Light&&B.ArmorVersion==LightVersion,TEXT("Pinned committed equipment identity/version changed"));
 }
 bool PinNoArmorSword(ADungeonFighter* P)
 {
  DungeonFairytaleSwordEquipmentBinding::FBinding B;FString Why;
  if(!Need(DungeonFairytaleSwordEquipmentBinding::Resolve(*Game.Get(),*P,B,Why),TEXT("Real starter binding unavailable: ")+Why))return false;
  if(!Need(B.Armor==DungeonFairytaleSwordEquipmentBinding::EArmor::NoArmor&&B.ArmorInstanceId==0&&B.WeaponContentId==TEXT("WPN-SWD-001"),TEXT("Starter must use actual committed SWD/NoArmor; do not force inventory")))return false;
  if(!Sword){Sword=B.WeaponInstanceId;SwordVersion=B.WeaponVersion;}
  return Need(Sword&&B.WeaponInstanceId==Sword&&B.WeaponVersion==SwordVersion,TEXT("Pinned starter sword identity changed"));
 }
 bool CaptureTextureBytesBeforeAudio()
 {
  if(StartupReadbackComplete)return true;
  const auto& Profile=Air::Profile();
  if(!Need(Profile.SourceClosureVerified&&Profile.SourceClosureSHA256==ExpectedClosure&&Profile.CanvasSource==512&&Profile.StandingExtent==416.&&Profile.StandingDisplay==72.&&Profile.HeightProjection==.70&&Profile.WeaponScale==.5,TEXT("Exact retained Air49 profile is not admitted")))return false;
  if(!Need(!Capturing&&!AudioRequested&&GIsDumpingMovie==0,TEXT("Texture GPU/source readback must precede audio/movie/input")))return false;
  IFileManager::Get().MakeDirectory(*(Directory/TEXT("texture-readback")),false);
  TSet<FString> Unique;
  const auto Capture=[&](const FString& Path,const FString& PNGSHA,const FString& RGBASHA,int32 Frame,int32 Component)
  {
   UTexture2D* T=FindObject<UTexture2D>(nullptr,*Path);
   if(!Need(!Unique.Contains(Path)&&T&&T->GetClass()==UTexture2D::StaticClass()&&T->GetPathName()==Path&&T->GetSizeX()==512&&T->GetSizeY()==512&&T->GetResource()&&!T->HasPendingRenderResourceInitialization(),TEXT("All49 exact preloaded Texture2D512 resources required before normal input")))return false;
   Unique.Add(Path);const FTextureRHIRef RHI=T->GetResource()->TextureRHI;
   if(!Need(RHI.IsValid()&&RHI->GetDesc().Extent==FIntPoint(512,512)&&(RHI->GetFormat()==PF_B8G8R8A8||RHI->GetFormat()==PF_R8G8B8A8),TEXT("GPU readback requires actual uncompressed BGRA8/RGBA8 mip0 512; no lossy fallback")))return false;
   TArray<FColor> GPU;const double ReadStart=FPlatformTime::Seconds();
   ENQUEUE_RENDER_COMMAND(Air49OriginalGPUReadback)([RHI,&GPU](FRHICommandListImmediate& Cmd)
   {FReadSurfaceDataFlags Flags(RCM_UNorm);Flags.SetLinearToGamma(false);Flags.SetMip(0);Cmd.ReadSurfaceData(RHI,FIntRect(0,0,512,512),GPU,Flags);});
   FlushRenderingCommands();const double ReadStop=FPlatformTime::Seconds();
   static_assert(sizeof(FColor)==4,"Native original GPU proof requires packed BGRA8 FColor");
   const int32 ByteCount=512*512*4;
   if(!Need(GPU.Num()==512*512,TEXT("Actual original GPU mip0 readback is incomplete")))return false;
   const FString Stem=FString::Printf(TEXT("texture-readback/%03d"),StartupTextures.Num());const FString GPUFile=Stem+TEXT(".gpu-bgra8.bin");
   if(!Need(WriteNewBytes(Directory/GPUFile,reinterpret_cast<const uint8*>(GPU.GetData()),uint64(GPU.Num())*sizeof(FColor)),TEXT("GPU original bytes could not be preserved exclusively")))return false;
   auto O=MakeShared<FJsonObject>();O->SetStringField(TEXT("texture"),Path);O->SetStringField(TEXT("class"),T->GetClass()->GetName());O->SetNumberField(TEXT("width"),T->GetSizeX());O->SetNumberField(TEXT("height"),T->GetSizeY());O->SetNumberField(TEXT("frame"),Frame);O->SetNumberField(TEXT("component"),Component);O->SetStringField(TEXT("source_SHA_metadata"),PNGSHA);O->SetStringField(TEXT("source_RGBA_SHA_metadata"),RGBASHA);O->SetBoolField(TEXT("resource_ready"),true);O->SetBoolField(TEXT("pending_initialization"),false);O->SetBoolField(TEXT("sRGB"),T->SRGB);O->SetNumberField(TEXT("RHI_format"),int32(RHI->GetFormat()));O->SetStringField(TEXT("GPU_file"),GPUFile);O->SetNumberField(TEXT("GPU_BGRA8_CRC32"),FCrc::MemCrc32(GPU.GetData(),ByteCount));O->SetStringField(TEXT("read_flags"),TEXT("RCM_UNorm/Mip0/LinearToGamma=false; BGRA8/RGBA8 UNORM(_SRGB) byte copy"));O->SetNumberField(TEXT("read_start_monotonic_s"),ReadStart);O->SetNumberField(TEXT("read_stop_monotonic_s"),ReadStop);
#if WITH_EDITOR && WITH_EDITORONLY_DATA
   TArray64<uint8> Mip;
   if(!Need(T->Source.IsValid()&&T->Source.GetSizeX()==512&&T->Source.GetSizeY()==512&&T->Source.GetFormat()==TSF_BGRA8&&T->Source.GetMipData(Mip,0)&&Mip.Num()==512*512*4,TEXT("Actual imported editor source mip0 BGRA8 unavailable; no metadata substitute")))return false;
   const FString SourceFile=Stem+TEXT(".editor-source-bgra8.bin");if(!Need(WriteNewBytes(Directory/SourceFile,Mip.GetData(),uint64(Mip.Num())),TEXT("Imported source mip0 original bytes could not be preserved")))return false;
   O->SetStringField(TEXT("editor_source_file"),SourceFile);O->SetStringField(TEXT("editor_source_format"),TEXT("TSF_BGRA8"));O->SetNumberField(TEXT("editor_source_BGRA8_CRC32"),FCrc::MemCrc32(Mip.GetData(),ByteCount));
#else
   return Need(false,TEXT("This isolated exact source proof requires editor source data"));
#endif
   StartupTextures.Add(MakeShared<FJsonValueObject>(O));return true;
  };
  for(const auto& F:Profile.Frames)for(const auto& L:F.Layers)if(!Capture(L.TexturePath,L.SourceSHA256,L.SourceRGBASHA256,F.Frame,int32(L.Component)))return false;
  if(!Capture(Profile.SwordTexturePath,Profile.SwordSourceSHA256,TEXT(""),-1,int32(Air::EComponent::IndependentSword)))return false;
  FlushRenderingCommands();StartupReadbackStop=FPlatformTime::Seconds();StartupReadbackComplete=Need(Unique.Num()==49&&StartupTextures.Num()==49,TEXT("All49 independent GPU/source mip originals must finish before capture"));return StartupReadbackComplete;
 }
 void Observe(ADungeonHeroAirProductionProbeV001& Actor)
 {
  if(Stopped||Stopping)return;if(PrewarmRequested&&!PrewarmDone){PrewarmDone=Need(IFileManager::Get().FileSize(*(Directory/TEXT("prewarm-viewport.png")))>8,TEXT("Actual prewarm image missing"));return;}if(!Capturing)return;
  auto G=Game.Get();auto H=HUD.Get();auto P=G?G->PlayerFighter.Get():nullptr;if(!Need(G&&H&&P,TEXT("Actual callback lost native owner"))){BeginStop(Actor);return;}
  const auto& V=G->GetEquipmentView();const auto& B=H->GetFairytaleSwordDraw();const auto& A=H->GetFairytaleSwordAirDraw();const bool bAir=P->JumpHeight>0.f||P->GetVerticalVelocity()>0.f;
  const int32 Pose=PhysicalPose(P->JumpHeight,P->GetVerticalVelocity(),P->GetLandingVisualAge());auto O=MakeShared<FJsonObject>();const double Offset=FPlatformTime::Seconds()-Start;
  O->SetNumberField(TEXT("wall_offset_s"),Offset);O->SetNumberField(TEXT("phase"),Phase);O->SetNumberField(TEXT("sim"),G->GetSimulationTime());O->SetStringField(TEXT("run"),V.RunGuid.ToString(EGuidFormats::Digits));Id(O,TEXT("owner"),V.OwnerId);Id(O,TEXT("current_room"),V.RoomInstanceId);Id(O,TEXT("epoch"),G->GetRunPresentationEpoch());Id(O,TEXT("player_entity"),P->GetRuntimeEntityId());
  O->SetArrayField(TEXT("ground"),XY(P->GetGroundPosition()));O->SetArrayField(TEXT("camera_ground"),XY(H->GetCameraGroundCenter()));O->SetNumberField(TEXT("facing"),P->Facing);O->SetNumberField(TEXT("jump_height"),P->JumpHeight);O->SetNumberField(TEXT("vertical_velocity"),P->GetVerticalVelocity());O->SetNumberField(TEXT("landing_visual_age"),P->GetLandingVisualAge());O->SetNumberField(TEXT("physical_visual_key"),Pose);
  O->SetNumberField(TEXT("hp"),P->Health);O->SetBoolField(TEXT("dead"),P->bDead);O->SetStringField(TEXT("animation"),P->AnimationName);O->SetNumberField(TEXT("animation_time"),P->AnimationTime);O->SetBoolField(TEXT("melee_grounded"),P->GetMeleeCombatState().Grounded);O->SetBoolField(TEXT("wa_grounded"),P->GetWeaponActionsState().Budget.Grounded);O->SetBoolField(TEXT("melee_active"),P->GetMeleeCombatState().Action.Active);O->SetBoolField(TEXT("wa_active"),P->GetWeaponSkillAction().Active);
  O->SetNumberField(TEXT("melee_time"),P->GetMeleeCombatState().Time);O->SetNumberField(TEXT("wa_time"),P->GetWeaponActionsState().Time);O->SetNumberField(TEXT("dodge_time"),P->GetDodgeState().Time);O->SetNumberField(TEXT("weapon_world_time"),G->GetWeaponWorldState().Time);O->SetNumberField(TEXT("native_actor_root_z"),P->GetActorLocation().Z);Id(O,TEXT("melee_attack_id"),P->GetMeleeCombatState().Action.AttackId);Id(O,TEXT("wa_action_id"),P->GetWeaponSkillAction().ActionId);
  FDungeonHeroAirSample Q;const bool QueryOK=P->QueryHeroNonAttackAir(Q);O->SetBoolField(TEXT("new_air_query_ok"),QueryOK);O->SetObjectField(TEXT("old_draw"),OldDraw(B));O->SetObjectField(TEXT("new_air_draw"),NewDraw(A));O->SetArrayField(TEXT("rendered_player_stack"),Strings(H->GetRenderedPlayerDrawStack()));O->SetStringField(TEXT("rendered_player_texture"),H->GetRenderedPlayerTexturePath());
  O->SetBoolField(TEXT("interface_visible"),H->GetInterfaceVisible());O->SetNumberField(TEXT("text_calls"),H->GetRenderedTextDrawCalls());O->SetBoolField(TEXT("range_debug"),H->IsCombatRangeDebugEnabled());O->SetNumberField(TEXT("range_lines"),H->GetCombatRangeDebugLineCount());
  Id(O,TEXT("weapon_instance"),V.Slots[V.ActiveSlot].InstanceId);Id(O,TEXT("weapon_version"),V.Slots[V.ActiveSlot].Version);Id(O,TEXT("armor_instance"),V.Slots[2].InstanceId);Id(O,TEXT("armor_version"),V.Slots[2].Version);
  if(bAir&&!PreviousAir)++AirTransitions;
  if(!bAir&&PreviousAir){++LandingTransitions;if(AirTransitions==1)FirstLandingObserved=true;if(AirTransitions==2)SecondLandingObserved=true;if(AirTransitions==3)ThirdLandingObserved=true;}
  PreviousAir=bAir;O->SetNumberField(TEXT("observed_air_transition_ordinal"),AirTransitions);O->SetBoolField(TEXT("transition_ordinal_is_gameplay_jump_id"),false);
  Observations.Add(MakeShared<FJsonValueObject>(O));Offsets.Add(MakeShared<FJsonValueNumber>(Offset));
  if(!Need(V.RunGuid==Run&&V.OwnerId==Owner&&V.RoomInstanceId==Room&&G->GetRunPresentationEpoch()==Epoch&&G->GetRunRestartSerial()==Restart&&P->GetRuntimeEntityId()==Owner,TEXT("Native owner/run/room/epoch changed during isolated baseline"))
   ||!Need(!H->GetInterfaceVisible()&&H->GetRenderedTextDrawCalls()==0&&!H->IsCombatRangeDebugEnabled()&&H->GetCombatRangeDebugLineCount()==0,TEXT("Traditional HUD/range must remain hidden"))
   ||!Need(P->Health==InitialHP&&!P->bDead&&!G->bGameOver,TEXT("Baseline player took damage or died; no state repair allowed"))){BeginStop(Actor);return;}
  if(GearPinned&&!PinGear(P)){BeginStop(Actor);return;}
  if(Pose>=0)
  {
   const bool LightNow=AirTransitions>=2;const int32 ExpectedCount=LightNow?9:6;
   const auto& Plan=A.Plan;const auto& Bound=Plan.Binding;
   if(!Need(QueryOK&&Q.Valid&&A.Drawn&&A.OptIn&&A.AtomicPreflightReady&&A.DrawId>LastNewDraw&&A.PlayerEntityId==Owner&&A.SimulationTime==G->GetSimulationTime()
     &&Plan.Supported&&Plan.Frame==Pose&&int32(Plan.Pose)==Pose+1&&Plan.Facing==Side&&P->Facing==float(Side)
     &&Plan.Sample.Valid&&Plan.Sample.RunGuid==Q.RunGuid&&Plan.Sample.OwnerId==Q.OwnerId&&Plan.Sample.RoomInstanceId==Q.RoomInstanceId
     &&Plan.Sample.PresentationEpoch==Q.PresentationEpoch&&Plan.Sample.NativeTime==Q.NativeTime&&Q.NativeTime==G->GetSimulationTime()
     &&Plan.Sample.GroundPosition==Q.GroundPosition&&Plan.Sample.JumpHeight==Q.JumpHeight&&Plan.Sample.VerticalVelocity==Q.VerticalVelocity&&Plan.Sample.LandingVisualAge==Q.LandingVisualAge
     &&A.ResidentTextures.Num()==49&&A.Slots.Num()==ExpectedCount&&A.ActualRenderedStack.Num()==ExpectedCount&&Plan.NonemptyDrawCount==ExpectedCount
     &&H->GetRenderedPlayerDrawStack()==A.ActualRenderedStack&&B.DrawStack==A.ActualRenderedStack&&B.Supported&&B.ActionPoseSupported&&B.TextureReady
     &&B.Clip==TEXT("sword_nonattack_air")&&SwordDrawn(B)&&B.ArmorDrawn==LightNow&&Plan.WeaponScale==.5
     &&Bound.WeaponInstanceId==Sword&&Bound.WeaponVersion==SwordVersion&&Bound.Armor==(LightNow?DungeonFairytaleSwordEquipmentBinding::EArmor::LightArmor:DungeonFairytaleSwordEquipmentBinding::EArmor::NoArmor)
     &&Bound.ArmorInstanceId==(LightNow?Light:0),TEXT("Actual production query/profile/committed None6 or LGT9 full draw differs"))){BeginStop(Actor);return;}
   for(const auto& R:A.ResidentTextures)if(!Need(R.ClassName==TEXT("Texture2D")&&R.Width==512&&R.Height==512&&R.ResourceReady&&!R.PendingInitialization,TEXT("Complete actual source49 resident/GPU set lost"))){BeginStop(Actor);return;}
   int32 SubmittedIndex=0;
   for(int32 Slot=0;Slot<9;++Slot)
   {
    const auto& Expected=Plan.Slots[Slot];if(!Expected.Enabled)continue;
    if(!Need(SubmittedIndex<A.Slots.Num(),TEXT("Missing actual enabled slot"))){BeginStop(Actor);return;}
    const auto& S=A.Slots[SubmittedIndex++];
    if(!Need(S.SlotIndex==Slot&&S.Component==Expected.Component&&S.TexturePath==Expected.TexturePath&&S.Drawn&&S.TextureReady&&!S.KnownOptionalEmpty&&S.TraceTint==A.Tint&&S.DrawScale==1.&&!S.ScalePosition,TEXT("Actual submitted slot order/path/tint differs from plan"))){BeginStop(Actor);return;}
   }
   LastNewDraw=A.DrawId;if(LightNow)++LightFrames;else ++NoArmorFrames;if(Pose>=4)++LandingFrames;
   if(AirTransitions==1)NoArmorMask|=1u<<Pose;else if(AirTransitions==2)LightFirstMask|=1u<<Pose;else if(AirTransitions==3)LightSecondMask|=1u<<Pose;
   else {Need(false,TEXT("Unexpected fourth/native transition; never invent jump event IDs"));BeginStop(Actor);return;}
  }
  if(Phase==9&&ThirdLandingObserved&&!bAir&&P->GetLandingVisualAge()==.12f)
  {
   if(B.Active&&B.Supported&&B.TextureReady&&B.Clip==TEXT("sword_ready_idle")&&B.ArmorDrawn&&SwordDrawn(B)&&!A.Drawn)++ReadyJoinFrames;
   if(ReadyJoinFrames>=2){FlowComplete=Need(JumpInputs==3&&AirTransitions==3&&LandingTransitions==3&&NoArmorMask==63&&LightFirstMask==63&&LightSecondMask==63&&RejumpIssuedInsideLanding&&NoArmorFrames>=6&&LightFrames>=12,TEXT("Three real jumps lack starterNone6/LGT9/rejump and six-pose/Ready coverage"));CaptureFinalHP=P->Health;Next(10);BeginStop(Actor);}
  }
 }
 void Finalize(ADungeonHeroAirProductionProbeV001& Actor)
 {
  if(Stopped)return;Stopped=true;GIsDumpingMovie=0;ReleaseKeys();const bool Flushed=FlushFastLosslessProofScreenshots();auto R=MakeShared<FJsonObject>();
  const bool AudioComplete=Actor.MainMixCapture&&Actor.MainMixCapture->Status().Phase==EDungeonNativeMixCapturePhaseV001::Complete;
  const bool Passed=Failure.IsEmpty()&&FlowComplete&&Flushed&&AudioComplete&&StartupReadbackComplete&&Start>StartupReadbackStop&&!Observations.IsEmpty();
  R->SetStringField(TEXT("schema"),TEXT("hero-nonattack-air-production-native-observer-v001"));R->SetStringField(TEXT("scenario"),TEXT("NormalEnter_StarterNone6_E_LGT9_LandingRejump"));R->SetStringField(TEXT("pass_scope"),TEXT("actual_core_native_None6_LGT9_three_jumps_only; formal20_and_final_art_remain_open"));R->SetBoolField(TEXT("passed"),Passed);R->SetBoolField(TEXT("flow_complete"),FlowComplete);R->SetBoolField(TEXT("final_accepted"),false);R->SetBoolField(TEXT("visual_reviewed"),false);R->SetBoolField(TEXT("audio_listened"),false);R->SetStringField(TEXT("failure"),Failure);
  R->SetStringField(TEXT("profile_id"),Air::Profile().ProfileId);R->SetStringField(TEXT("profile_closure"),Air::Profile().SourceClosureSHA256);R->SetStringField(TEXT("native_ready_freeze_SHA256"),TEXT("e3786b74ac2292479780368531a99ebc097ec8df3c70629d8168a39ff75dfea7"));R->SetBoolField(TEXT("NoArmor_is_formal20_pair"),false);R->SetBoolField(TEXT("transition_ordinals_are_gameplay_jump_ids"),false);R->SetBoolField(TEXT("native_async_capture_writes_flushed"),Flushed);R->SetBoolField(TEXT("player_Guard_HP_position_AI_time_writes"),false);
  Id(R,TEXT("process_id"),FPlatformProcess::GetCurrentProcessId());R->SetNumberField(TEXT("requested_facing"),Side);R->SetStringField(TEXT("run"),Run.ToString(EGuidFormats::Digits));Id(R,TEXT("owner"),Owner);Id(R,TEXT("current_room"),Room);Id(R,TEXT("epoch"),Epoch);Id(R,TEXT("restart_serial"),Restart);Id(R,TEXT("weapon_instance"),Sword);Id(R,TEXT("weapon_version"),SwordVersion);Id(R,TEXT("armor_instance"),Light);Id(R,TEXT("armor_version"),LightVersion);
  R->SetNumberField(TEXT("normal_space_inputs"),JumpInputs);R->SetNumberField(TEXT("air_transitions"),AirTransitions);R->SetNumberField(TEXT("landing_transitions"),LandingTransitions);R->SetNumberField(TEXT("starter_NoArmor_mask"),NoArmorMask);R->SetNumberField(TEXT("light_first_mask"),LightFirstMask);R->SetNumberField(TEXT("light_second_mask"),LightSecondMask);R->SetNumberField(TEXT("starter_NoArmor_frames"),NoArmorFrames);R->SetNumberField(TEXT("light_frames"),LightFrames);R->SetNumberField(TEXT("landing_frames"),LandingFrames);R->SetNumberField(TEXT("Ready_join_frames"),ReadyJoinFrames);R->SetNumberField(TEXT("initial_hp"),InitialHP);R->SetNumberField(TEXT("capture_final_hp"),CaptureFinalHP);R->SetBoolField(TEXT("normal_rejump_issued_inside_original_landing"),RejumpIssuedInsideLanding);R->SetNumberField(TEXT("rejump_input_landing_age"),RejumpInputLandingAge);
  R->SetArrayField(TEXT("normal_inputs"),Inputs);R->SetArrayField(TEXT("steps"),Steps);R->SetArrayField(TEXT("observations"),Observations);R->SetArrayField(TEXT("diagnostic_knight_hits"),DiagnosticHits);R->SetArrayField(TEXT("startup_actual_GPU_source_textures49"),StartupTextures);R->SetBoolField(TEXT("startup_readback_complete"),StartupReadbackComplete);R->SetNumberField(TEXT("startup_readback_stop_monotonic_s"),StartupReadbackStop);
  auto Open=MakeShared<FJsonObject>();Open->SetStringField(TEXT("normal_landing_J_priority"),TEXT("OPEN_not_run"));Open->SetStringField(TEXT("normal_landing_Shift_priority"),TEXT("OPEN_not_run"));Open->SetStringField(TEXT("real_save_restore"),TEXT("OPEN_not_run"));R->SetObjectField(TEXT("additional_scenarios"),Open);
  auto Timing=MakeShared<FJsonObject>();Timing->SetBoolField(TEXT("use_fixed_time_step"),FApp::UseFixedTimeStep());Timing->SetNumberField(TEXT("capture_start_monotonic_s"),Start);Timing->SetNumberField(TEXT("capture_stop_monotonic_s"),Stop);Timing->SetArrayField(TEXT("frame_wall_offsets_s"),Offsets);R->SetObjectField(TEXT("capture_timing"),Timing);
  if(Actor.MainMixCapture)R->SetObjectField(TEXT("main_submix_capture"),Actor.MainMixCapture->SerializeReport());
  FString Text;auto Writer=TJsonWriterFactory<>::Create(&Text);const bool Serialized=FJsonSerializer::Serialize(R,Writer);const FString Path=Directory/TEXT("runtime-report.json");
  const bool Written=Serialized&&EvidenceClaimed&&!Directory.IsEmpty()&&WriteNewUTF8(Path,Text);
  if(!Failure.IsEmpty())UE_LOG(LogTemp,Error,TEXT("Hero Air baseline: %s"),*Failure);FPlatformMisc::RequestExitWithStatus(false,Passed&&Written?0:3);
 }
 void Tick(ADungeonHeroAirProductionProbeV001& Actor)
 {
  if(Stopped)return;const double Now=FPlatformTime::Seconds();if(Actor.MainMixCapture)Actor.MainMixCapture->Poll();
  if(Stopping){if(!Actor.MainMixCapture||Actor.MainMixCapture->IsTerminal())Finalize(Actor);return;}
  if(!Failure.IsEmpty()){BeginStop(Actor);return;}
  auto World=Actor.GetWorld();auto G=World?World->GetAuthGameMode<ADungeonGameMode>():nullptr;auto C=UGameplayStatics::GetPlayerController(&Actor,0);auto H=C?Cast<ADungeonHUD>(C->GetHUD()):nullptr;
  if(!Game.IsValid()&&Now-WarmStarted>12.){Need(false,TEXT("Native owner startup timeout"));BeginStop(Actor);return;}
  if(!Game.IsValid()&&G&&C&&C->PlayerInput&&H)
  {
   auto* P=G->PlayerFighter.Get();const auto& V=G->GetEquipmentView();if(!P||!V.Bound||!V.RunGuid.IsValid())return;
   Game=G;Controller=C;HUD=H;Run=V.RunGuid;Owner=V.OwnerId;Room=V.RoomInstanceId;Epoch=G->GetRunPresentationEpoch();Restart=G->GetRunRestartSerial();InitialHP=P->Health;
   Actor.AddTickPrerequisiteActor(G);Actor.AddTickPrerequisiteActor(H);return;
  }
  if(!Game.IsValid())return;
  if(PulseKey.IsValid()&&Now>=ReleaseAt){Key(PulseKey,false);PulseKey=FKey();NeutralUntil=Now+.04;}
  if(!Capturing)
  {
   if(!StartupReadbackComplete){CaptureTextureBytesBeforeAudio();return;}
   if(!PrewarmRequested&&Now-WarmStarted>=2.){PrewarmRequested=true;FScreenshotRequest::RequestScreenshot(Directory/TEXT("prewarm-viewport.png"),false,false,false);}
   if(PrewarmDone&&!AudioRequested){AudioRequested=true;Actor.MainMixCapture=NewObject<UDungeonNativeMainSubmixCaptureV001>(&Actor);if(!Actor.MainMixCapture->Begin(Actor.GetWorld(),Directory/TEXT("audio-v001")))Need(false,TEXT("Native main mix Begin request rejected"));}
   if(AudioRequested&&Actor.MainMixCapture&&Actor.MainMixCapture->Status().Phase==EDungeonNativeMixCapturePhaseV001::Recording)
   {
    const auto& Status=Actor.MainMixCapture->Status();if(!Need(Status.StartRequested&&Status.StartMonotonic>0.,TEXT("Recording state has no actual monotonic origin")))return;
    Start=Status.StartMonotonic;Capturing=true;GIsDumpingMovie=-1;Next(0);
   }
   if(Now-WarmStarted>20.)Need(false,TEXT("Prewarm/native mix arming timeout"));return;
  }
  auto P=G?G->PlayerFighter.Get():nullptr;if(!Need(G&&C&&H&&P&&G==Game.Get()&&C==Controller.Get()&&H==HUD.Get()&&C->GetPawn()==P&&C->IsLocalController()&&Now-Start<12.&&Now-PhaseAt<5.,TEXT("Normal-input production owner/phase timeout")))return;
  FDungeonFirstBatchGuardRoomView View;if(!Need(G->QueryFirstBatchGuardRoom(View)&&View.Slots.Num()==3&&G->GetEquipmentView().Config==EDungeonEquipmentRunConfig::FirstBatch,TEXT("Actual finite FirstBatchGuardRoom required")))return;
  if(!Run.IsValid()){const auto& V=G->GetEquipmentView();Run=V.RunGuid;Owner=V.OwnerId;Room=V.RoomInstanceId;Epoch=G->GetRunPresentationEpoch();Restart=G->GetRunRestartSerial();InitialHP=P->Health;}
  switch(Phase)
  {
   case 0:if(!Need(G->bWaitingForStart&&G->GetSimulationTime()==0.,TEXT("Baseline must start with real Enter, not Space releasing waiting")))return;if(Pulse(EKeys::Enter))Next(1);break;
   case 1:if(!G->bWaitingForStart&&CanPulse()&&ClearKnightIfRequested(P,View)&&PinNoArmorSword(P)&&Pulse(Side<0?EKeys::A:EKeys::D))Next(2);break;
   case 2:if(CanPulse()&&P->Facing==float(Side)&&PinNoArmorSword(P)&&Pulse(EKeys::SpaceBar)){++JumpInputs;Next(3);}break;
   case 3:if(FirstLandingObserved&&NoArmorMask==63&&P->JumpHeight==0.f&&P->GetVerticalVelocity()==0.f&&P->GetLandingVisualAge()==.12f&&CanPulse())
    {DungeonEquipmentInventory::FItem I;I.ContentId="ARM-LGT-001";const auto R=G->RegisterEquipmentSource(TEXT("display.hero.air.production.light.v001"),I,P->GetGroundPosition()+FVector2D(24,0),true);if(!Need(R.Ok()&&!R.Replayed,TEXT("Actual display LGT registration failed")))return;LightSource=R.SourceId;Light=R.InstanceId;Next(4);}break;
   case 4:if(CanPulse()&&G->GetEquipmentView().SelectedSourceId==LightSource&&Pulse(EKeys::E))Next(5);break;
   case 5:if(!G->GetEquipmentView().Action.Active&&G->GetEquipmentView().Slots[2].InstanceId==Light&&CanPulse()&&PinGear(P))
    {const auto& D=H->GetFairytaleSwordDraw();if(!Need(D.Active&&D.Supported&&D.ArmorDrawn&&SwordDrawn(D)&&P->Facing==float(Side),TEXT("Real committed LGT/sword/facing not visible before normal Space")))return;if(Pulse(EKeys::SpaceBar)){++JumpInputs;Next(6);}}break;
   case 6:if(SecondLandingObserved&&LightFirstMask==63&&CanPulse())
    {const double Before=P->GetLandingVisualAge();if(!Need(P->JumpHeight==0.f&&P->GetVerticalVelocity()==0.f&&Before>=.06f&&Before<.12f,TEXT("Normal re-jump missed original half-open .12 landing window after real Land5 callback")))return;if(Pulse(EKeys::SpaceBar)){RejumpInputLandingAge=Before;RejumpIssuedInsideLanding=true;++JumpInputs;Next(7);}}break;
   case 7:if(AirTransitions==3)Next(8);break;
   case 8:if(ThirdLandingObserved)Next(9);break;
   case 9:break; // Stop only after final actual callbacks prove Land5 and ordinary Ready.
   default:Need(false,TEXT("Unexpected baseline observer state"));break;
  }
 }
};

void FDungeonHeroAirProductionProofDeleterV001::operator()(FDungeonHeroAirProductionProofStateV001* P)const{delete P;}
ADungeonHeroAirProductionProbeV001::ADungeonHeroAirProductionProbeV001(){PrimaryActorTick.bCanEverTick=true;}
ADungeonHeroAirProductionProbeV001::~ADungeonHeroAirProductionProbeV001()=default;
void ADungeonHeroAirProductionProbeV001::BeginPlay()
{
 Super::BeginPlay();Proof.Reset(new FDungeonHeroAirProductionProofStateV001());Proof->WarmStarted=FPlatformTime::Seconds();GIsDumpingMovie=0;
 FParse::Value(FCommandLine::Get(),TEXT("DungeonContentProofDir="),Proof->Directory);FParse::Value(FCommandLine::Get(),TEXT("DungeonHeroAirProductionFacing="),Proof->Side);Proof->AllowKnightDiagnostic=FParse::Param(FCommandLine::Get(),TEXT("DungeonHeroAirProductionClearKnightDiagnostic"));
 if(!Proof->Need(!Proof->Directory.IsEmpty()&&!FPaths::IsRelative(Proof->Directory)&&(Proof->Side==-1||Proof->Side==1),TEXT("Absolute unused evidence directory and explicit facing[-1,+1] required")))return;
 Proof->Directory=FPaths::ConvertRelativePathToFull(Proof->Directory);FPaths::NormalizeDirectoryName(Proof->Directory);IFileManager::Get().MakeDirectory(*Proof->Directory,true);
 TArray<FString> Prior;IFileManager::Get().FindFiles(Prior,*(Proof->Directory/TEXT("*")),true,false);Prior.Remove(TEXT("native-lossless-capture.json"));TArray<FString> Subdirs;IFileManager::Get().FindFiles(Subdirs,*(Proof->Directory/TEXT("*")),false,true);
 if(!Proof->Need(Prior.IsEmpty()&&Subdirs.IsEmpty(),TEXT("Baseline output directory already contains prior evidence")))return;
 const FString Claim=FString::Printf(TEXT("{\"schema\":\"hero-air-production-process-claim-v001\",\"pid\":%u}\n"),FPlatformProcess::GetCurrentProcessId());
 if(!Proof->Need(WriteNewUTF8(Proof->Directory/TEXT("observer-process-claim-v001.json"),Claim),TEXT("Evidence claim already exists or cannot be created")))return;
 Proof->EvidenceClaimed=true;
 for(const TCHAR* Flag:{TEXT("DungeonHeroAirProductionProofV001"),TEXT("DungeonFairytaleSwordAirPreview"),TEXT("DungeonFairytaleSwordEquipmentBoundPreview"),TEXT("DungeonContentProof"),TEXT("DungeonFastLosslessCapture"),TEXT("DungeonAsyncLosslessCapture")})if(!Proof->Need(FParse::Param(FCommandLine::Get(),Flag),FString(TEXT("Missing explicit production opt-in: "))+Flag))return;
 for(const TCHAR* Flag:{TEXT("DungeonHeroAirProofV001"),TEXT("DungeonHeroAirBaselineV001"),TEXT("DungeonProof"),TEXT("DungeonGuardMoveProofV001"),TEXT("DungeonHeroDodgeProofV001"),TEXT("DungeonHeroHurtProofV001"),TEXT("DungeonHeroDeathProofV001"),TEXT("DungeonGuardStompProofV001"),TEXT("DungeonGuardArtCombatProofV003"),TEXT("DungeonGuardArtDeathProofV005"),TEXT("DungeonGuardArtKnown44Proof"),TEXT("DungeonGuardArtPartialProof"),TEXT("DungeonGuardRoomFlowProof"),TEXT("DungeonGuardRoomManualLightSource"),TEXT("DungeonFairytaleWalkProof"),TEXT("DungeonFairytaleEquipmentBoundProof"),TEXT("DungeonFairytaleSwordBodyProof"),TEXT("DungeonRunSaveProof"),TEXT("DungeonRunRestoreProof"),TEXT("DungeonGuardRunSaveProof"),TEXT("DungeonGuardRunRestoreProof"),TEXT("DungeonFairytaleLookdevProof"),TEXT("DungeonFairytaleLookdevPreview"),TEXT("DungeonCombatRangeDebug"),TEXT("DungeonCombatRangeProof"),TEXT("DungeonShowInterface")})if(!Proof->Need(!FParse::Param(FCommandLine::Get(),Flag),TEXT("Independent proof/visible HUD/range cannot share this observer")))return;
 for(TActorIterator<ADungeonContentProbe> It(GetWorld());It;++It)if(IsValid(*It)){Proof->Need(false,TEXT("Old ContentProbe is already running"));return;}
 if(!Proof->Need(!FApp::UseFixedTimeStep(),TEXT("Native variable pacing required")))return;
 GetMutableDefault<UEngine>()->GameScreenshotSaveDirectory.Path=Proof->Directory;FScreenshotRequest::OnScreenshotRequestProcessed().AddUObject(this,&ADungeonHeroAirProductionProbeV001::ScreenshotProcessed);
}
void ADungeonHeroAirProductionProbeV001::ScreenshotProcessed(){if(Proof)Proof->Observe(*this);}
void ADungeonHeroAirProductionProbeV001::Tick(float D){Super::Tick(D);if(Proof)Proof->Tick(*this);}
void ADungeonHeroAirProductionProbeV001::EndPlay(const EEndPlayReason::Type R)
{
 FScreenshotRequest::OnScreenshotRequestProcessed().RemoveAll(this);
 if(Proof&&!Proof->Stopped)
 {
  Proof->Need(false,TEXT("Air baseline world ended before capture/export completed"));GIsDumpingMovie=0;
  if(MainMixCapture&&!MainMixCapture->IsTerminal())MainMixCapture->Abort(TEXT("Air baseline world ended before export completed"));
  Proof->BeginStop(*this);Proof->Finalize(*this);
 }
 Super::EndPlay(R);
}
