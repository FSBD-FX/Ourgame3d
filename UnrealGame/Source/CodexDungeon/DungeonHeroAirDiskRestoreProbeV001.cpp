#include "DungeonHeroAirDiskRestoreProbeV001.h"
#include "DungeonGameMode.h"
#include "DungeonFighter.h"
#include "DungeonHUD.h"
#include "DungeonContentProbe.h"
#include "DungeonNativeMainSubmixCaptureV001.h"
#include "DungeonFairytaleSwordEquipmentBinding.h"
#include "DungeonFairytaleSwordAirV001.h"
#include "DungeonProofScreenshots.h"
#include "DungeonRoomLayout.h"
#include "DungeonRunSaveAdapterV2.h"
#include "DungeonFairytaleSwordWalkProfile.h"
#include "GameFramework/PlayerState.h"
#include "GameFramework/Pawn.h"
#include "GameFramework/SpectatorPawn.h"
#include "Modules/ModuleManager.h"
#if WITH_EDITOR
#include "TextureCompiler.h"
#endif
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

namespace D144
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
 Id(O,TEXT("action_id"),D.ActionId);Id(O,TEXT("instance_id"),D.InstanceId);O->SetNumberField(TEXT("action_start"),D.ActionStart);O->SetNumberField(TEXT("action_end"),D.ActionEnd);O->SetNumberField(TEXT("stage"),D.Stage);
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

namespace D144
{
JO EquipmentAction(const FDungeonEquipmentActionView& E)
{
 auto O=MakeShared<FJsonObject>();O->SetNumberField(TEXT("kind"),int32(E.Kind));O->SetBoolField(TEXT("active"),E.Active);Id(O,TEXT("action_id"),E.ActionId);Id(O,TEXT("operation_id"),E.OperationId);Id(O,TEXT("source_id"),E.SourceId);Id(O,TEXT("instance_id"),E.InstanceId);O->SetNumberField(TEXT("slot"),E.Slot);O->SetNumberField(TEXT("start"),E.Start);O->SetNumberField(TEXT("deadline"),E.Deadline);return O;
}
bool SameSample(const FDungeonHeroAirSample& A,const FDungeonHeroAirSample& B)
{return A.Valid==B.Valid&&A.RunGuid==B.RunGuid&&A.OwnerId==B.OwnerId&&A.RoomInstanceId==B.RoomInstanceId&&A.PresentationEpoch==B.PresentationEpoch&&A.NativeTime==B.NativeTime&&A.GroundPosition==B.GroundPosition&&A.Facing==B.Facing&&A.JumpHeight==B.JumpHeight&&A.VerticalVelocity==B.VerticalVelocity&&A.LandingVisualAge==B.LandingVisualAge;}
bool Brown(const FDungeonFairytaleSwordDraw& D,bool Primary)
{
 if(!D.Active||!D.Supported||!D.ActionPoseSupported||!D.TextureReady||!D.ArmorDrawn||!SwordDrawn(D)||D.GearPlaceholder||D.Frame<0||D.Frame>=(Primary?6:4)||D.DrawStack.Num()!=(Primary?8:7))return false;
 if(D.Clip!=(Primary?TEXT("sword_primary_1"):TEXT("sword_ready_idle")))return false;
 const TCHAR* Parts[]={TEXT("ShoulderFar"),TEXT("Chest"),TEXT("ShoulderNear")};const int32 Slots[]={1,2,4};
 for(int32 I=0;I<3;++I){const FString Name=Primary?FString::Printf(TEXT("T_Fairytale_LeatherPrimary1%s_%03d_v001"),Parts[I],D.Frame):FString::Printf(TEXT("T_Fairytale_LeatherReady%s_%03d_v001"),Parts[I],D.Frame);
  const FString Expected=FString(Primary?TEXT("/Game/Production/ArtTrials/EV048/v013/HeroLeatherPrimary1/"):TEXT("/Game/Production/ArtTrials/EV048/v012/HeroLeatherReady/"))+Name+TEXT(".")+Name;if(D.DrawStack[Slots[I]]!=Expected)return false;}
 return true;
}
}

namespace D144
{
namespace Store=DungeonSaveGenerationStore;
namespace Adapter=DungeonRunSaveAdapterV2;
FString Bits(double Value){uint64 Raw=0;FMemory::Memcpy(&Raw,&Value,sizeof(Raw));return FString::Printf(TEXT("%016llx"),(unsigned long long)Raw);}
bool SHA(const FString& Value){if(Value.Len()!=64)return false;for(TCHAR C:Value)if(!((C>='0'&&C<='9')||(C>='a'&&C<='f')))return false;return true;}
TArray<FKey> NeutralKeys()
{
 TArray<FKey> Out={EKeys::W,EKeys::A,EKeys::S,EKeys::D,EKeys::Up,EKeys::Down,EKeys::Left,EKeys::Right,EKeys::J,EKeys::K,EKeys::E,EKeys::Q,EKeys::T,EKeys::R,EKeys::Tab,EKeys::Escape,EKeys::SpaceBar,EKeys::LeftShift,EKeys::RightShift,EKeys::LeftMouseButton,EKeys::RightMouseButton,EKeys::Enter};
 TArray<FKey> All;EKeys::GetAllKeys(All);for(const auto& K:All)if(K.IsGamepadKey())Out.AddUnique(K);return Out;
}
}

struct FDungeonHeroAirDiskRestoreProofStateV001
{
 using JO=D144::JO;using JV=D144::JV;
 FString Directory,Failure,Role,ProfilesDirectory,ProfileDirectory,BuildId,CompiledSHA,DLLSHA,ExpectedCodecSHA;
 FGuid ProfileId,ExpectedRun,Run;uint64 ExpectedOwner=0,SourcePID=0,Owner=0,Room=0,Epoch=0,Restart=0;
 uint64 Sword=0,SwordVersion=0,Light=0,LightVersion=0,LightSource=0,LastDraw=0,EquipActionId=0,EquipOperationId=0;
 double WarmStarted=0.,Start=0.,Stop=0.,PhaseAt=0.,ReleaseAt=0.,NeutralUntil=0.,StartupReadbackStop=0.,InitialHP=0.,CaptureFinalHP=0.,EquipStart=-1.,EquipDeadline=-1.,InstalledWall=0.,LastPausedWall=0.;
 int32 Phase=0,JumpInputs=0,EquipInputIndex=INDEX_NONE,EquipStartedIndex=INDEX_NONE,EquipCommitIndex=INDEX_NONE,ReadyIndex=INDEX_NONE,PristineIndex=INDEX_NONE,ApexIndex=INDEX_NONE,PauseCount=0,NeutralCount=0,ResumeInputIndex=INDEX_NONE,FirstOpenIndex=INDEX_NONE,ReadyJoinFrames=0;
 uint32 ContinuedMask=0;
 bool Restore=false,Stopped=false,Stopping=false,EvidenceClaimed=false,Capturing=false,PrewarmRequested=false,PrewarmDone=false,AudioRequested=false,Preloaded=false,StartupReadbackComplete=false,GearPinned=false,AllowKnightDiagnostic=false,KnightCleared=false,EIssued=false,ReadyConsumed=false,FlowComplete=false,NeutralReleased=false,ResumeIssued=false,SaveAttempted=false;
 FKey PulseKey;TMap<FKey,bool> Keys;
 TWeakObjectPtr<ADungeonGameMode> Game;TWeakObjectPtr<APlayerController> Controller;TWeakObjectPtr<ADungeonHUD> HUD;
 TArray<JV> Inputs,Steps,Observations,Offsets,DiagnosticHits,StartupTextures,PauseChecks,NeutralChecks;
 JO Report=MakeShared<FJsonObject>(),Equipment=MakeShared<FJsonObject>(),Checkpoint=MakeShared<FJsonObject>(),DiskFacts=MakeShared<FJsonObject>(),PrepareFacts=MakeShared<FJsonObject>(),ResumeFacts=MakeShared<FJsonObject>(),PristineFacts;
 FDungeonRunSnapshot Saved;FDungeonPreparedRun Prepared;D144::Adapter::FLoadedRun Loaded;TArray<uint8> SavedCodec;
 bool Need(bool Yes,const FString& Why){if(!Yes&&Failure.IsEmpty())Failure=Why;return Yes;}
 void Next(int32 Value){Phase=Value;PhaseAt=FPlatformTime::Seconds();auto O=MakeShared<FJsonObject>();O->SetNumberField(TEXT("phase"),Value);O->SetNumberField(TEXT("wall_offset_s"),PhaseAt-Start);O->SetNumberField(TEXT("sim"),Game.IsValid()?Game->GetSimulationTime():0.);Steps.Add(MakeShared<FJsonValueObject>(O));}
 void Key(FKey Code,bool Down,bool Force=false,bool AnalogZero=false)
 {
  if(!Controller.IsValid()||(!Force&&Keys.FindRef(Code)==Down))return;
  auto O=MakeShared<FJsonObject>();const auto G=Game.Get();const auto P=G?G->PlayerFighter.Get():nullptr;
  O->SetBoolField(TEXT("context_sampled_before_InputKey"),true);O->SetNumberField(TEXT("wall_offset_s"),FPlatformTime::Seconds()-Start);O->SetNumberField(TEXT("sim"),G?G->GetSimulationTime():0.);O->SetStringField(TEXT("key"),Code.ToString());O->SetBoolField(TEXT("down"),Down);O->SetBoolField(TEXT("forced_release"),Force&&!Down);O->SetBoolField(TEXT("analog_zero_event"),AnalogZero);
  if(G){const auto& V=G->GetEquipmentView();O->SetStringField(TEXT("run"),V.RunGuid.ToString(EGuidFormats::Digits));D144::Id(O,TEXT("owner"),V.OwnerId);D144::Id(O,TEXT("current_room"),V.RoomInstanceId);D144::Id(O,TEXT("epoch"),G->GetRunPresentationEpoch());D144::Id(O,TEXT("restart_serial"),G->GetRunRestartSerial());O->SetNumberField(TEXT("install_gate"),int32(G->GetRunInstallGate()));D144::Id(O,TEXT("selected_source_id"),V.SelectedSourceId);O->SetObjectField(TEXT("before_equipment_action"),D144::EquipmentAction(V.Action));if(V.ActiveSlot>=0&&V.ActiveSlot<3){D144::Id(O,TEXT("weapon_instance"),V.Slots[V.ActiveSlot].InstanceId);D144::Id(O,TEXT("weapon_version"),V.Slots[V.ActiveSlot].Version);}D144::Id(O,TEXT("armor_instance"),V.Slots[2].InstanceId);D144::Id(O,TEXT("armor_version"),V.Slots[2].Version);}
  if(P){D144::Id(O,TEXT("player_entity"),P->GetRuntimeEntityId());O->SetNumberField(TEXT("facing"),P->Facing);O->SetNumberField(TEXT("before_H"),P->JumpHeight);O->SetNumberField(TEXT("before_V"),P->GetVerticalVelocity());O->SetNumberField(TEXT("before_landing_age"),P->GetLandingVisualAge());}
  Controller->InputKey(FInputKeyParams(Code,AnalogZero?IE_Axis:Down?IE_Pressed:IE_Released,Down?1.:0.,Code.IsGamepadKey()));Keys.Add(Code,Down);
  if(P){O->SetNumberField(TEXT("after_H"),P->JumpHeight);O->SetNumberField(TEXT("after_V"),P->GetVerticalVelocity());O->SetNumberField(TEXT("after_landing_age"),P->GetLandingVisualAge());}
  Inputs.Add(MakeShared<FJsonValueObject>(O));
 }
 bool CanPulse()const{return !PulseKey.IsValid()&&FPlatformTime::Seconds()>=NeutralUntil;}
 bool Pulse(FKey Code){if(!CanPulse())return false;Key(Code,true);PulseKey=Code;ReleaseAt=FPlatformTime::Seconds()+.04;return true;}
 void ReleaseKeys(){TArray<FKey> Held;Keys.GetKeys(Held);for(const auto& Code:Held)Key(Code,false);PulseKey=FKey();}
 void ReleaseAllControls(){for(const auto& Code:D144::NeutralKeys())Key(Code,false,true,Code.IsAnalog());NeutralReleased=true;}
 JO Controls(int32 Index)const
 {
  auto O=MakeShared<FJsonObject>();TArray<JV> Held,Analog;const auto C=Controller.Get();bool Neutral=C&&C->PlayerInput;
  if(C)for(const auto& Code:D144::NeutralKeys()){if(C->IsInputKeyDown(Code)){Held.Add(MakeShared<FJsonValueString>(Code.ToString()));Neutral=false;}if(Code.IsGamepadKey()&&C->GetInputAnalogKeyState(Code)!=0.f){auto A=MakeShared<FJsonObject>();A->SetStringField(TEXT("key"),Code.ToString());A->SetNumberField(TEXT("value"),C->GetInputAnalogKeyState(Code));Analog.Add(MakeShared<FJsonValueObject>(A));Neutral=false;}}
  O->SetNumberField(TEXT("observation_index"),Index);O->SetNumberField(TEXT("wall_offset_s"),FPlatformTime::Seconds()-Start);O->SetNumberField(TEXT("sim"),Game.IsValid()?Game->GetSimulationTime():0.);O->SetNumberField(TEXT("install_gate"),Game.IsValid()?int32(Game->GetRunInstallGate()):-1);O->SetBoolField(TEXT("enter_down"),C&&C->IsInputKeyDown(EKeys::Enter));O->SetBoolField(TEXT("enter_just_pressed"),C&&C->WasInputKeyJustPressed(EKeys::Enter));O->SetArrayField(TEXT("held_gameplay_keys"),Held);O->SetArrayField(TEXT("nonzero_gamepad_axes"),Analog);O->SetBoolField(TEXT("neutral_all"),Neutral);return O;
 }
 void BeginStop(ADungeonHeroAirDiskRestoreProbeV001& Actor)
 {
  if(Stopping||Stopped)return;Stopping=true;Capturing=false;GIsDumpingMovie=0;ReleaseKeys();
  if(Actor.MainMixCapture){const auto MixPhase=Actor.MainMixCapture->Status().Phase;if(MixPhase==EDungeonNativeMixCapturePhaseV001::Recording||MixPhase==EDungeonNativeMixCapturePhaseV001::ExportPending){if(!Actor.MainMixCapture->Stop())Need(false,TEXT("Native mix Stop failed after final callback"));}else if(!Actor.MainMixCapture->IsTerminal())Actor.MainMixCapture->Abort(Failure.IsEmpty()?TEXT("Stopped before actual Recording"):Failure);Stop=Actor.MainMixCapture->Status().StopMonotonic;}
  if(Stop<=0.)Stop=FPlatformTime::Seconds();
 }
 JO SaveBytes(const FString& Name,const TArray<uint8>& Bytes)
 {
  const FString Path=Directory/Name;if(!Need(D144::WriteNewBytes(Path,Bytes.GetData(),uint64(Bytes.Num())),TEXT("Exclusive original byte creation failed: ")+Path))return nullptr;
  TArray<uint8> ReadBack;if(!Need(FFileHelper::LoadFileToArray(ReadBack,*Path)&&ReadBack==Bytes,TEXT("Original bytes readback mismatch: ")+Path))return nullptr;
  auto O=MakeShared<FJsonObject>();O->SetStringField(TEXT("path"),Path);O->SetNumberField(TEXT("bytes"),Bytes.Num());O->SetStringField(TEXT("sha256"),D144::Store::FGenerationStore::Sha256(Bytes));return O;
 }
 bool CaptureCodec(TArray<uint8>& Bytes,FDungeonRunSnapshot* Out=nullptr)
 {
  FDungeonRunSnapshot Current;FString Why;if(!Need(IsInGameThread()&&Game.IsValid()&&Game->CaptureRunSnapshot(Current,Why),TEXT("Real completed boundary Capture rejected: ")+Why)||!Need(DungeonRunSnapshotCodec::Encode(Current,Bytes,Why),TEXT("Whole Codec Encode rejected: ")+Why))return false;if(Out)*Out=MoveTemp(Current);return true;
 }
 bool ClearKnightIfRequested(ADungeonFighter* Player,const FDungeonFirstBatchGuardRoomView& View)
 {
  if(!AllowKnightDiagnostic||KnightCleared)return true;ADungeonFighter* Knight=nullptr;for(auto E:Game->Enemies)if(E&&E->GetRuntimeEntityId()==View.Slots[0].EntityId)Knight=E;
  if(!Need(!Restore&&Knight&&Knight->GetStoneKnightDriver()&&!Knight->GetStoneGuardDriver()&&Knight->EnemyContentId==TEXT("ENM-STN-001"),TEXT("Explicit diagnostic applies only to source predecessor Knight")))return false;
  if(Knight->bDead){KnightCleared=true;return true;}if(!Knight->CanReceiveDirectHit())return false;auto O=MakeShared<FJsonObject>();D144::Id(O,TEXT("entity"),Knight->GetRuntimeEntityId());O->SetStringField(TEXT("content"),Knight->EnemyContentId);O->SetStringField(TEXT("api"),TEXT("ADungeonFighter::ApplyCombatHit"));O->SetBoolField(TEXT("explicit_cli_authorization"),true);O->SetNumberField(TEXT("sim"),Game->GetSimulationTime());O->SetNumberField(TEXT("before_hp"),Knight->Health);Knight->ApplyCombatHit(100000.f,Player,85.f);O->SetNumberField(TEXT("after_hp"),Knight->Health);O->SetBoolField(TEXT("dead"),Knight->bDead);DiagnosticHits.Add(MakeShared<FJsonValueObject>(O));KnightCleared=Knight->bDead;return Need(KnightCleared,TEXT("Public Knight diagnostic failed; no direct state repair"));
 }
 bool PinGear(ADungeonFighter* Player)
 {
  DungeonFairytaleSwordEquipmentBinding::FBinding Binding;FString Why;if(!Need(DungeonFairytaleSwordEquipmentBinding::Resolve(*Game.Get(),*Player,Binding,Why),TEXT("Real committed binding missing: ")+Why))return false;
  if(!Need(Binding.RunGuid==Run&&Binding.OwnerId==Owner&&Binding.Armor==DungeonFairytaleSwordEquipmentBinding::EArmor::LightArmor&&Binding.WeaponContentId==TEXT("WPN-SWD-001")&&Binding.ArmorContentId==TEXT("ARM-LGT-001")&&Binding.WeaponInstanceId==Sword&&Binding.WeaponVersion==SwordVersion&&Binding.ArmorInstanceId==Light,TEXT("Actual same SWD/LGT binding changed")))return false;
  if(!GearPinned){LightVersion=Binding.ArmorVersion;GearPinned=true;}return Need(Binding.ArmorVersion==LightVersion,TEXT("Actual LGT binding version changed"));
 }
 bool CaptureTextureBytesBeforeAudio(ADungeonHeroAirDiskRestoreProbeV001& Actor)
 {
  if(StartupReadbackComplete)return true;
  const auto& Profile=D144::Air::Profile();
  if(!Need(Profile.SourceClosureVerified&&Profile.SourceClosureSHA256==D144::ExpectedClosure&&Profile.CanvasSource==512&&Profile.StandingExtent==416.&&Profile.StandingDisplay==72.&&Profile.HeightProjection==.70&&Profile.WeaponScale==.5,TEXT("Exact retained Air49 profile is not admitted")))return false;
  if(!Need(!Capturing&&!AudioRequested&&GIsDumpingMovie==0,TEXT("Texture GPU/source readback must precede audio/movie/input")))return false;
  if(!Preloaded)
  {
   TArray<UTexture*> Pending;const auto Load=[&](const FString& Path){if(Actor.ProofTextures.Contains(Path))return;auto T=LoadObject<UTexture2D>(nullptr,*Path);Actor.ProofTextures.Add(Path,T);if(T)Pending.Add(T);};
   for(const auto& F:Profile.Frames)for(const auto& L:F.Layers)Load(L.TexturePath);Load(Profile.SwordTexturePath);
   for(int32 Frame=0;Frame<4;++Frame)for(const TCHAR* Component:{TEXT("BodyRest"),TEXT("ShoulderFar"),TEXT("Chest"),TEXT("NearArmWithoutHand"),TEXT("ShoulderNear"),TEXT("NearHand")}){const bool Armor=FString(Component)==TEXT("ShoulderFar")||FString(Component)==TEXT("Chest")||FString(Component)==TEXT("ShoulderNear");const FString Name=Armor?FString::Printf(TEXT("T_Fairytale_LeatherReady%s_%03d_v001"),Component,Frame):FString::Printf(TEXT("T_Fairytale_SwordReady%s_%03d_v001"),Component,Frame);Load(FString(Armor?TEXT("/Game/Production/ArtTrials/EV048/v012/HeroLeatherReady/"):TEXT("/Game/Production/ArtTrials/EV048/v006/HeroSwordArmorReady/"))+Name+TEXT(".")+Name);}
   for(const auto& F:DungeonFairytaleSwordWalkV001::Profile().Frames)for(const FString* Path:{&F.BodyRest,&F.ShoulderFar,&F.Chest,&F.NearArmWithoutHand,&F.ShoulderNear,&F.HelmetForeground,&F.NearHand})Load(*Path);
#if WITH_EDITOR
   FTextureCompilingManager::Get().FinishCompilation(Pending);
#endif
   FlushRenderingCommands();Preloaded=true;
  }
  IFileManager::Get().MakeDirectory(*(Directory/TEXT("texture-readback")),false);
  TSet<FString> Unique;
  const auto Capture=[&](const FString& Path,const FString& PNGSHA,const FString& RGBASHA,int32 Frame,int32 Component)
  {
   UTexture2D* T=FindObject<UTexture2D>(nullptr,*Path);
   if(!Need(!Unique.Contains(Path)&&T&&T->GetClass()==UTexture2D::StaticClass()&&T->GetPathName()==Path&&T->GetSizeX()==512&&T->GetSizeY()==512&&T->GetResource()&&!T->HasPendingRenderResourceInitialization(),TEXT("All49 exact preloaded Texture2D512 resources required before normal input")))return false;
   Unique.Add(Path);const FTextureRHIRef RHI=T->GetResource()->TextureRHI;
   if(!Need(RHI.IsValid()&&RHI->GetDesc().Extent==FIntPoint(512,512)&&(RHI->GetFormat()==PF_B8G8R8A8||RHI->GetFormat()==PF_R8G8B8A8),TEXT("GPU readback requires actual uncompressed BGRA8/RGBA8 mip0 512; no lossy fallback")))return false;
   TArray<FColor> GPU;const double ReadStart=FPlatformTime::Seconds();
   ENQUEUE_RENDER_COMMAND(AirDisk115OriginalGPUReadback)([RHI,&GPU](FRHICommandListImmediate& Cmd)
   {FReadSurfaceDataFlags Flags(RCM_UNorm);Flags.SetLinearToGamma(false);Flags.SetMip(0);Cmd.ReadSurfaceData(RHI,FIntRect(0,0,512,512),GPU,Flags);});
   FlushRenderingCommands();const double ReadStop=FPlatformTime::Seconds();
   static_assert(sizeof(FColor)==4,"Native original GPU proof requires packed BGRA8 FColor");
   const int32 ByteCount=512*512*4;
   if(!Need(GPU.Num()==512*512,TEXT("Actual original GPU mip0 readback is incomplete")))return false;
   const FString Stem=FString::Printf(TEXT("texture-readback/%03d"),StartupTextures.Num());const FString GPUFile=Stem+TEXT(".gpu-bgra8.bin");
   if(!Need(D144::WriteNewBytes(Directory/GPUFile,reinterpret_cast<const uint8*>(GPU.GetData()),uint64(GPU.Num())*sizeof(FColor)),TEXT("GPU original bytes could not be preserved exclusively")))return false;
   auto O=MakeShared<FJsonObject>();O->SetStringField(TEXT("texture"),Path);O->SetStringField(TEXT("class"),T->GetClass()->GetName());O->SetNumberField(TEXT("width"),T->GetSizeX());O->SetNumberField(TEXT("height"),T->GetSizeY());O->SetNumberField(TEXT("frame"),Frame);O->SetNumberField(TEXT("component"),Component);O->SetStringField(TEXT("source_SHA_metadata"),PNGSHA);O->SetStringField(TEXT("source_RGBA_SHA_metadata"),RGBASHA);O->SetBoolField(TEXT("resource_ready"),true);O->SetBoolField(TEXT("pending_initialization"),false);O->SetBoolField(TEXT("sRGB"),T->SRGB);O->SetNumberField(TEXT("RHI_format"),int32(RHI->GetFormat()));O->SetStringField(TEXT("GPU_file"),GPUFile);O->SetNumberField(TEXT("GPU_BGRA8_CRC32"),FCrc::MemCrc32(GPU.GetData(),ByteCount));O->SetStringField(TEXT("read_flags"),TEXT("RCM_UNorm/Mip0/LinearToGamma=false; BGRA8/RGBA8 UNORM(_SRGB) byte copy"));O->SetNumberField(TEXT("read_start_monotonic_s"),ReadStart);O->SetNumberField(TEXT("read_stop_monotonic_s"),ReadStop);
#if WITH_EDITOR && WITH_EDITORONLY_DATA
   TArray64<uint8> Mip;
   if(!Need(T->Source.IsValid()&&T->Source.GetSizeX()==512&&T->Source.GetSizeY()==512&&T->Source.GetFormat()==TSF_BGRA8&&T->Source.GetMipData(Mip,0)&&Mip.Num()==512*512*4,TEXT("Actual imported editor source mip0 BGRA8 unavailable; no metadata substitute")))return false;
   const FString SourceFile=Stem+TEXT(".editor-source-bgra8.bin");if(!Need(D144::WriteNewBytes(Directory/SourceFile,Mip.GetData(),uint64(Mip.Num())),TEXT("Imported source mip0 original bytes could not be preserved")))return false;
   O->SetStringField(TEXT("editor_source_file"),SourceFile);O->SetStringField(TEXT("editor_source_format"),TEXT("TSF_BGRA8"));O->SetNumberField(TEXT("editor_source_BGRA8_CRC32"),FCrc::MemCrc32(Mip.GetData(),ByteCount));
#else
   return Need(false,TEXT("This isolated exact source proof requires editor source data"));
#endif
   StartupTextures.Add(MakeShared<FJsonValueObject>(O));return true;
  };
  for(const auto& F:Profile.Frames)for(const auto& L:F.Layers)if(!Capture(L.TexturePath,L.SourceSHA256,L.SourceRGBASHA256,F.Frame,int32(L.Component)))return false;
  if(!Capture(Profile.SwordTexturePath,Profile.SwordSourceSHA256,TEXT(""),-1,int32(D144::Air::EComponent::IndependentSword)))return false;
  int32 ExpectedReadbacks=49;
  for(int32 Frame=0;Frame<4;++Frame)for(const TCHAR* Component:{TEXT("BodyRest"),TEXT("ShoulderFar"),TEXT("Chest"),TEXT("NearArmWithoutHand"),TEXT("ShoulderNear"),TEXT("NearHand")})
  {const bool Armor=FString(Component)==TEXT("ShoulderFar")||FString(Component)==TEXT("Chest")||FString(Component)==TEXT("ShoulderNear");
   const FString Name=Armor?FString::Printf(TEXT("T_Fairytale_LeatherReady%s_%03d_v001"),Component,Frame):FString::Printf(TEXT("T_Fairytale_SwordReady%s_%03d_v001"),Component,Frame);
   const FString Path=FString(Armor?TEXT("/Game/Production/ArtTrials/EV048/v012/HeroLeatherReady/"):TEXT("/Game/Production/ArtTrials/EV048/v006/HeroSwordArmorReady/"))+Name+TEXT(".")+Name;
   if(!Capture(Path,TEXT(""),TEXT(""),Frame,-1))return false;++ExpectedReadbacks;}
  for(int32 Frame=0;Frame<6;++Frame){const auto& F=DungeonFairytaleSwordWalkV001::Profile().Frames[Frame];for(const FString* Path:{&F.BodyRest,&F.ShoulderFar,&F.Chest,&F.NearArmWithoutHand,&F.ShoulderNear,&F.HelmetForeground,&F.NearHand}){if(!Capture(*Path,TEXT(""),TEXT(""),Frame,-1))return false;++ExpectedReadbacks;}}
  FlushRenderingCommands();StartupReadbackStop=FPlatformTime::Seconds();StartupReadbackComplete=Need(ExpectedReadbacks==115&&Unique.Num()==ExpectedReadbacks&&StartupTextures.Num()==ExpectedReadbacks,TEXT("All49 independent GPU/source mip originals must finish before capture"));return StartupReadbackComplete;
 }

 TMap<FString,TArray<uint8>> PublishedBytes;
 bool StoreCopies(bool Before)
 {
  const FString Subdir=Before?TEXT("disk-before"):TEXT("disk-after");if(!Need(IFileManager::Get().MakeDirectory(*(Directory/Subdir),false),TEXT("Cannot create exclusive disk evidence leaf")))return false;TArray<JV> Rows;
  for(const TCHAR* Name:{TEXT("slot-A.bundle.json"),TEXT("slot-A.commit.json")})
  {
   const FString Original=ProfileDirectory/Name;TArray<uint8> Bytes;if(!Need(FFileHelper::LoadFileToArray(Bytes,*Original),TEXT("Published gen1 originals missing: ")+Original))return false;
   if(Before)PublishedBytes.Add(Name,Bytes);else if(Restore&&!Need(PublishedBytes.Contains(Name)&&PublishedBytes[Name]==Bytes,TEXT("Published store bytes changed in target")))return false;
   auto Copy=SaveBytes(Subdir/Name,Bytes);if(!Copy)return false;auto O=MakeShared<FJsonObject>();O->SetStringField(TEXT("original_path"),Original);O->SetNumberField(TEXT("bytes"),Bytes.Num());O->SetStringField(TEXT("sha256"),D144::Store::FGenerationStore::Sha256(Bytes));O->SetObjectField(TEXT("evidence_file"),Copy);Rows.Add(MakeShared<FJsonValueObject>(O));
  }
  DiskFacts->SetArrayField(Before?TEXT("published_before"):TEXT("published_after"),Rows);if(!Before&&Restore)DiskFacts->SetBoolField(TEXT("published_files_unchanged"),true);return true;
 }
 JO ReadResult(const D144::Adapter::FReadResult& Result,const D144::Adapter::FLoadedRun& Value)
 {
  auto O=MakeShared<FJsonObject>();O->SetNumberField(TEXT("load_status"),int32(Result.Status));O->SetNumberField(TEXT("slot"),int32(Result.Slot));D144::Id(O,TEXT("observed_head_generation"),Result.ObservedHeadGeneration);D144::Id(O,TEXT("generation_id"),Value.Generation.GenerationId);D144::Id(O,TEXT("parent_generation"),Value.Generation.ParentGeneration);O->SetStringField(TEXT("loaded_build_id"),Value.Generation.BuildId);O->SetStringField(TEXT("diagnostic"),Result.Diagnostic);return O;
 }
 bool ValidLoaded(const D144::Adapter::FReadResult& Result,const D144::Adapter::FLoadedRun& Value)const
 {return Result.Status==D144::Store::EStatus::Ok&&Result.ObservedHeadGeneration==1&&Value.Run.IsValid()&&Value.Generation.GenerationId==1&&Value.Generation.ParentGeneration==0&&Value.Generation.ProfileId==ProfileId&&Value.Generation.BuildId==BuildId&&Value.Generation.Versions==D144::Adapter::CurrentVersions&&Value.Run.Get()->Schema==2&&Value.Run.Get()->Scope==EDungeonRunScope::BoundDevelopmentV2;}
 bool SaveApex(int32 Index,const FDungeonFairytaleSwordAirDrawV001& Draw,ADungeonFighter* Player)
 {
  if(!Need(!SaveAttempted&&!Restore&&IsInGameThread()&&Draw.Drawn&&Draw.Plan.Frame==2&&Player->JumpHeight>0.f&&Player->GetVerticalVelocity()>=-90.f&&Player->GetVerticalVelocity()<=90.f,TEXT("Save requires the same actual completed Apex callback")))return false;SaveAttempted=true;
  if(!CaptureCodec(SavedCodec,&Saved))return false;
  if(!Need(Saved.Schema==2&&Saved.Scope==EDungeonRunScope::BoundDevelopmentV2&&Saved.RunGuid==Run&&Saved.OwnerId==Owner&&Saved.RoomInstanceId==Room&&Saved.SimulationTime==Game->GetSimulationTime()&&!Saved.WaitingForStart&&!Saved.GameOver&&!Saved.Fighters.IsEmpty(),TEXT("Whole source snapshot/root/time differs from completed Apex")))return false;
  const auto& PF=Saved.Fighters[0];const auto& EV=Saved.Equipment.View;
  if(!Need(PF.Kind==EDungeonFighterOwnerKind::BoundPlayer&&PF.EntityId==Owner&&PF.RunGuid==Run&&PF.GroundPosition==Player->GetGroundPosition()&&PF.JumpHeight==Player->JumpHeight&&PF.JumpVelocity==Player->GetVerticalVelocity()&&PF.LandingVisualAge==Player->GetLandingVisualAge()&&PF.Facing==1.f&&PF.Health==InitialHP&&!PF.Dead&&EV.Slots[2].InstanceId==Light&&EV.Slots[2].Version==LightVersion&&EV.ActiveSlot>=0&&EV.ActiveSlot<3&&EV.Slots[EV.ActiveSlot].InstanceId==Sword&&EV.Slots[EV.ActiveSlot].Version==SwordVersion,TEXT("Whole Codec player/HVAge/equipment differs from native completed draw")))return false;
  auto Codec=SaveBytes(TEXT("source-codec.json"),SavedCodec);if(!Codec)return false;
  Checkpoint->SetNumberField(TEXT("observation_index"),Index);Checkpoint->SetBoolField(TEXT("same_completed_game_thread_boundary"),true);Checkpoint->SetBoolField(TEXT("is_game_thread"),IsInGameThread());Checkpoint->SetStringField(TEXT("run"),Run.ToString(EGuidFormats::Digits));D144::Id(Checkpoint,TEXT("owner"),Owner);D144::Id(Checkpoint,TEXT("current_room"),Room);D144::Id(Checkpoint,TEXT("epoch"),Epoch);D144::Id(Checkpoint,TEXT("restart_serial"),Restart);Checkpoint->SetNumberField(TEXT("sim"),Saved.SimulationTime);Checkpoint->SetArrayField(TEXT("ground"),D144::XY(PF.GroundPosition));Checkpoint->SetNumberField(TEXT("H"),PF.JumpHeight);Checkpoint->SetNumberField(TEXT("V"),PF.JumpVelocity);Checkpoint->SetNumberField(TEXT("landing_age"),PF.LandingVisualAge);D144::Id(Checkpoint,TEXT("weapon_instance"),Sword);D144::Id(Checkpoint,TEXT("weapon_version"),SwordVersion);D144::Id(Checkpoint,TEXT("armor_instance"),Light);D144::Id(Checkpoint,TEXT("armor_version"),LightVersion);Checkpoint->SetObjectField(TEXT("codec"),Codec);
  if(!Need(!IFileManager::Get().DirectoryExists(*ProfileDirectory),TEXT("Source Profile already exists before writer; never overwrite/retry")))return false;
  D144::Store::FGenerationStore Store(ProfilesDirectory,ProfileId,D144::Adapter::CurrentVersions);DiskFacts->SetArrayField(TEXT("published_before"),{});DiskFacts->SetNumberField(TEXT("writer_open_monotonic_s"),FPlatformTime::Seconds());const auto Lease=Store.OpenWriter();DiskFacts->SetNumberField(TEXT("writer_status"),int32(Lease));
  if(!Need(Lease==D144::Store::EStatus::Ok,TEXT("Real exclusive source writer acquisition failed")))return false;
  D144::Adapter::FWriteRequest Request;Request.Context.ProfilesDirectory=ProfilesDirectory;Request.Context.ProfileId=ProfileId;Request.Context.ExpectedRunGuid=Run;Request.Context.ExpectedOwnerId=Owner;Request.RunGuid=Run;Request.OwnerId=Owner;Request.GenerationId=1;Request.ParentGeneration=0;Request.BuildId=BuildId;
  DiskFacts->SetNumberField(TEXT("commit_start_monotonic_s"),FPlatformTime::Seconds());const auto Result=D144::Adapter::Commit(Store,Saved,Request);DiskFacts->SetNumberField(TEXT("commit_stop_monotonic_s"),FPlatformTime::Seconds());Store.CloseWriter();DiskFacts->SetBoolField(TEXT("close_writer_called"),true);DiskFacts->SetNumberField(TEXT("closed_monotonic_s"),FPlatformTime::Seconds());
  auto Commit=MakeShared<FJsonObject>();Commit->SetNumberField(TEXT("status"),int32(Result.Status));D144::Id(Commit,TEXT("generation_id"),Result.GenerationId);Commit->SetBoolField(TEXT("replayed"),Result.Replayed);Commit->SetBoolField(TEXT("publication_may_have_succeeded"),Result.PublicationMayHaveSucceeded);Commit->SetStringField(TEXT("bundle_sha256"),Result.BundleSha256);Commit->SetNumberField(TEXT("bundle_crc32"),Result.BundleCrc32);Commit->SetNumberField(TEXT("bundle_byte_length"),double(Result.BundleByteLength));Commit->SetStringField(TEXT("diagnostic"),Result.Diagnostic);DiskFacts->SetObjectField(TEXT("commit"),Commit);
  // No retry, recovery, profile reset or deletion on any status, including lost acknowledgement.
  if(!Need(Result.Status==D144::Store::EStatus::Ok&&!Result.Replayed&&Result.GenerationId==1,TEXT("Actual gen1parent0 Commit failed: ")+Result.Diagnostic))return false;
  D144::Adapter::FLoadedRun ReadBack;const auto ResultRead=D144::Adapter::Load(Store,Request.Context,ReadBack);DiskFacts->SetObjectField(TEXT("source_load_receipt"),ReadResult(ResultRead,ReadBack));TArray<uint8> Bytes;FString Why;
  if(!Need(ValidLoaded(ResultRead,ReadBack)&&DungeonRunSnapshotCodec::Encode(*ReadBack.Run.Get(),Bytes,Why)&&Bytes==SavedCodec,TEXT("Actual full disk Codec readback differs: ")+Why+ResultRead.Diagnostic))return false;
  DiskFacts->SetNumberField(TEXT("load_status"),int32(ResultRead.Status));D144::Id(DiskFacts,TEXT("observed_head_generation"),ResultRead.ObservedHeadGeneration);D144::Id(DiskFacts,TEXT("generation_id"),ReadBack.Generation.GenerationId);D144::Id(DiskFacts,TEXT("parent_generation"),ReadBack.Generation.ParentGeneration);DiskFacts->SetStringField(TEXT("loaded_build_id"),ReadBack.Generation.BuildId);auto ReadCodec=SaveBytes(TEXT("source-readback-codec.json"),Bytes);if(!ReadCodec)return false;DiskFacts->SetObjectField(TEXT("source_readback_codec"),ReadCodec);return StoreCopies(false);
 }
 JO NoRunFacts()
 {
  auto O=MakeShared<FJsonObject>();const auto G=Game.Get();const auto C=Controller.Get();FString Why;
  const auto E=G->CaptureEquipmentSnapshot();const auto Rewards=G->CaptureRunRewardsSnapshot();const auto Fog=G->CaptureRunExplorationSnapshot();const auto& World=G->GetWeaponWorldState();const auto& Audio=G->GetActionAudioState();int32 Pawns=0,Fighters=0;
  for(TActorIterator<APawn> It(G->GetWorld());It;++It)if(!It->IsActorBeingDestroyed())++Pawns;for(TActorIterator<ADungeonFighter> It(G->GetWorld());It;++It)if(!It->IsActorBeingDestroyed())++Fighters;
  O->SetBoolField(TEXT("pristine_api"),G->IsPristineContinueBootstrap(Why));O->SetStringField(TEXT("api_diagnostic"),Why);O->SetBoolField(TEXT("controller_local"),C->IsLocalController());O->SetBoolField(TEXT("controller_authoritative"),C->HasAuthority());O->SetBoolField(TEXT("controller_input_present"),C->PlayerInput!=nullptr);O->SetBoolField(TEXT("controller_player_state_present"),C->PlayerState!=nullptr);O->SetBoolField(TEXT("controller_only_spectator"),C->PlayerState&&C->PlayerState->IsOnlyASpectator());O->SetBoolField(TEXT("controller_spectator_pawn_null"),!C->GetSpectatorPawn());O->SetBoolField(TEXT("default_pawn_class_null"),!G->DefaultPawnClass);O->SetBoolField(TEXT("spectator_class_null"),!G->SpectatorClass);O->SetBoolField(TEXT("world_begun_play"),G->GetWorld()->GetBegunPlay());O->SetBoolField(TEXT("player_null"),!G->PlayerFighter);O->SetBoolField(TEXT("controller_pawn_null"),!C->GetPawn());O->SetBoolField(TEXT("inventory_null"),!G->GetEquipmentInventoryState());O->SetBoolField(TEXT("equipment_bound"),E.View.Bound);O->SetBoolField(TEXT("run_guid_invalid"),!E.View.RunGuid.IsValid());O->SetBoolField(TEXT("scene_active"),G->GetSceneRoomView().Active);O->SetBoolField(TEXT("rewards_bound"),Rewards.Bound);O->SetBoolField(TEXT("world_run_valid"),World.RunGuid.IsValid());O->SetBoolField(TEXT("audio_run_valid"),Audio.RunGuid.IsValid());
  D144::Id(O,TEXT("native_pawns"),Pawns);D144::Id(O,TEXT("native_fighters"),Fighters);D144::Id(O,TEXT("restart_serial"),G->GetRunRestartSerial());D144::Id(O,TEXT("epoch"),G->GetRunPresentationEpoch());D144::Id(O,TEXT("combat_seed"),E.View.CombatSeed);D144::Id(O,TEXT("next_crit_draw"),E.View.NextCritDraw);D144::Id(O,TEXT("fog_rooms"),Fog.Rooms.Num());D144::Id(O,TEXT("world_bindings"),World.ActorBindings.Num());D144::Id(O,TEXT("audio_records"),Audio.Records.Num());D144::Id(O,TEXT("gate"),uint64(G->GetRunInstallGate()));O->SetStringField(TEXT("simulation_time_bits"),D144::Bits(G->GetSimulationTime()));O->SetBoolField(TEXT("enter_down"),C->IsInputKeyDown(EKeys::Enter));return O;
 }
 bool ValidPristine(const JO& O)
 {
  for(const TCHAR* K:{TEXT("pristine_api"),TEXT("controller_local"),TEXT("controller_authoritative"),TEXT("controller_input_present"),TEXT("controller_player_state_present"),TEXT("controller_spectator_pawn_null"),TEXT("default_pawn_class_null"),TEXT("spectator_class_null"),TEXT("world_begun_play"),TEXT("player_null"),TEXT("controller_pawn_null"),TEXT("inventory_null"),TEXT("run_guid_invalid")})if(!O->GetBoolField(K))return false;
  for(const TCHAR* K:{TEXT("controller_only_spectator"),TEXT("equipment_bound"),TEXT("scene_active"),TEXT("rewards_bound"),TEXT("world_run_valid"),TEXT("audio_run_valid"),TEXT("enter_down")})if(O->GetBoolField(K))return false;
  for(const TCHAR* K:{TEXT("native_pawns"),TEXT("native_fighters"),TEXT("restart_serial"),TEXT("epoch"),TEXT("combat_seed"),TEXT("next_crit_draw"),TEXT("fog_rooms"),TEXT("world_bindings"),TEXT("audio_records")})if(O->GetStringField(K)!=TEXT("0"))return false;
  return O->GetStringField(TEXT("gate"))==TEXT("3")&&O->GetStringField(TEXT("simulation_time_bits"))==TEXT("0000000000000000");
 }
 bool LoadAndInstall()
 {
  auto G=Game.Get();auto C=Controller.Get();if(!Need(Restore&&PristineIndex!=INDEX_NONE&&PristineFacts&&ValidPristine(PristineFacts)&&ValidPristine(NoRunFacts()),TEXT("Target lost its real pristine no-Run origin"))||!StoreCopies(true))return false;
  D144::Store::FGenerationStore Store(ProfilesDirectory,ProfileId,D144::Adapter::CurrentVersions);D144::Adapter::FReadContext Context;Context.ProfilesDirectory=ProfilesDirectory;Context.ProfileId=ProfileId;Context.ExpectedRunGuid=ExpectedRun;Context.ExpectedOwnerId=ExpectedOwner;
  D144::Id(PrepareFacts,TEXT("before_epoch"),G->GetRunPresentationEpoch());D144::Id(PrepareFacts,TEXT("before_restart_serial"),G->GetRunRestartSerial());const auto Result=D144::Adapter::LoadAndPreparePristine(*G,Store,Context,Prepared,Loaded);
  PrepareFacts->SetNumberField(TEXT("load_status"),int32(Result.Status));D144::Id(PrepareFacts,TEXT("observed_head_generation"),Result.ObservedHeadGeneration);D144::Id(PrepareFacts,TEXT("generation_id"),Loaded.Generation.GenerationId);D144::Id(PrepareFacts,TEXT("parent_generation"),Loaded.Generation.ParentGeneration);PrepareFacts->SetStringField(TEXT("loaded_build_id"),Loaded.Generation.BuildId);PrepareFacts->SetBoolField(TEXT("prepared_ready"),Prepared.IsReady());
  if(!Need(ValidLoaded(Result,Loaded)&&Prepared.IsReady(),TEXT("Actual highest gen1/parent0 pristine load/prepare failed: ")+Result.Diagnostic))return false;Saved=*Loaded.Run.Get();FString Why;
  if(!Need(Saved.RunGuid==ExpectedRun&&Saved.OwnerId==ExpectedOwner&&!Saved.Fighters.IsEmpty()&&DungeonRunSnapshotCodec::Encode(Saved,SavedCodec,Why)&&D144::Store::FGenerationStore::Sha256(SavedCodec)==ExpectedCodecSHA,TEXT("Loaded whole Codec differs from expected exited source: ")+Why))return false;
  auto LoadedFact=SaveBytes(TEXT("loaded-codec.json"),SavedCodec);if(!LoadedFact)return false;PrepareFacts->SetObjectField(TEXT("loaded_codec"),LoadedFact);
  const auto& PF=Saved.Fighters[0];const auto& EV=Saved.Equipment.View;
  if(!Need(PF.Kind==EDungeonFighterOwnerKind::BoundPlayer&&PF.EntityId==Saved.OwnerId&&PF.JumpHeight>0.f&&PF.JumpVelocity>=-90.f&&PF.JumpVelocity<=90.f&&PF.Facing==1.f&&!PF.Dead&&EV.ActiveSlot>=0&&EV.ActiveSlot<3,TEXT("Loaded source is not a real right-facing player Apex")))return false;
  Run=Saved.RunGuid;Owner=Saved.OwnerId;Room=Saved.RoomInstanceId;InitialHP=PF.Health;Sword=EV.Slots[EV.ActiveSlot].InstanceId;SwordVersion=EV.Slots[EV.ActiveSlot].Version;Light=EV.Slots[2].InstanceId;LightVersion=EV.Slots[2].Version;GearPinned=true;
  bool Hidden=!Prepared.GetStagedActors().IsEmpty();FString StagedPlayerPath;TArray<JV> StagedRows;
  for(const auto& Weak:Prepared.GetStagedActors())
  {auto A=Weak.Get();auto O=MakeShared<FJsonObject>();const auto F=Cast<ADungeonFighter>(A);const bool IsPlayer=F&&!F->bEnemy;O->SetStringField(TEXT("local_actor_path"),A?A->GetPathName():FString());O->SetStringField(TEXT("class"),A?A->GetClass()->GetName():FString());O->SetBoolField(TEXT("hidden"),A&&A->IsHidden());O->SetBoolField(TEXT("tick_enabled"),A&&A->IsActorTickEnabled());O->SetBoolField(TEXT("collision_enabled"),A&&A->GetActorEnableCollision());O->SetBoolField(TEXT("is_player"),IsPlayer);Hidden=Hidden&&A&&A->IsHidden()&&!A->IsActorTickEnabled()&&!A->GetActorEnableCollision();if(IsPlayer)StagedPlayerPath=A->GetPathName();StagedRows.Add(MakeShared<FJsonValueObject>(O));}
  PrepareFacts->SetArrayField(TEXT("staged_actors"),StagedRows);PrepareFacts->SetNumberField(TEXT("staged_actor_count"),StagedRows.Num());PrepareFacts->SetStringField(TEXT("prepared_player_actor_path"),StagedPlayerPath);PrepareFacts->SetBoolField(TEXT("all_staged_hidden_tick_collision_off"),Hidden);PrepareFacts->SetNumberField(TEXT("gate_preparing"),int32(G->GetRunInstallGate()));const bool Unpublished=!G->PlayerFighter&&!C->GetPawn()&&!G->GetEquipmentView().Bound&&G->GetRunInstallGate()==EDungeonRunInstallGate::Preparing;PrepareFacts->SetBoolField(TEXT("unpublished_during_prepare"),Unpublished);
  if(!Need(Hidden&&Unpublished&&!StagedPlayerPath.IsEmpty(),TEXT("Staged actors were not hidden/private/tick-collision-off")))return false;
  const bool Installed=FDungeonRunInstaller::Install(*G,Prepared,Why);PrepareFacts->SetBoolField(TEXT("install_ok"),Installed);PrepareFacts->SetBoolField(TEXT("prepared_consumed"),!Prepared.IsReady());auto P=G->PlayerFighter.Get();PrepareFacts->SetBoolField(TEXT("controller_possesses_restored_player"),P&&C->GetPawn()==P);PrepareFacts->SetStringField(TEXT("installed_player_actor_path"),P?P->GetPathName():FString());D144::Id(PrepareFacts,TEXT("after_epoch"),G->GetRunPresentationEpoch());D144::Id(PrepareFacts,TEXT("after_restart_serial"),G->GetRunRestartSerial());PrepareFacts->SetNumberField(TEXT("installed_gate"),int32(G->GetRunInstallGate()));InstalledWall=FPlatformTime::Seconds();PrepareFacts->SetNumberField(TEXT("installed_monotonic_s"),InstalledWall);
  if(!Need(Installed&&!Prepared.IsReady()&&P&&P->GetPathName()==StagedPlayerPath&&C->GetPawn()==P&&G->GetRunInstallGate()==EDungeonRunInstallGate::AwaitExplicitContinue&&G->GetRunPresentationEpoch()==1&&G->GetRunRestartSerial()==0,TEXT("Actual Install/Possess/epoch0to1/restart0 failed: ")+Why))return false;
  Epoch=G->GetRunPresentationEpoch();Restart=G->GetRunRestartSerial();TArray<uint8> Bytes;if(!CaptureCodec(Bytes)||!Need(Bytes==SavedCodec,TEXT("Installed complete Run Codec differs from disk")))return false;auto InstalledFact=SaveBytes(TEXT("installed-codec.json"),Bytes);if(!InstalledFact)return false;PrepareFacts->SetObjectField(TEXT("installed_codec"),InstalledFact);ReleaseAllControls();Next(11);return true;
 }
 bool FinalDiskCheck()
 {
  D144::Store::FGenerationStore Store(ProfilesDirectory,ProfileId,D144::Adapter::CurrentVersions);D144::Adapter::FReadContext Context;Context.ProfilesDirectory=ProfilesDirectory;Context.ProfileId=ProfileId;Context.ExpectedRunGuid=Run;Context.ExpectedOwnerId=Owner;D144::Adapter::FLoadedRun ReadBack;const auto Result=D144::Adapter::Load(Store,Context,ReadBack);DiskFacts->SetObjectField(TEXT("target_final_load_receipt"),ReadResult(Result,ReadBack));TArray<uint8> Bytes;FString Why;
  if(!Need(ValidLoaded(Result,ReadBack)&&DungeonRunSnapshotCodec::Encode(*ReadBack.Run.Get(),Bytes,Why)&&Bytes==SavedCodec,TEXT("Published disk changed during continued target Run: ")+Why))return false;auto Copy=SaveBytes(TEXT("target-final-readback-codec.json"),Bytes);if(!Copy)return false;DiskFacts->SetObjectField(TEXT("target_final_readback_codec"),Copy);return StoreCopies(false);
 }

 void Observe(ADungeonHeroAirDiskRestoreProbeV001& Actor)
 {
  if(Stopped||Stopping)return;if(PrewarmRequested&&!PrewarmDone){PrewarmDone=Need(IFileManager::Get().FileSize(*(Directory/TEXT("prewarm-viewport.png")))>8,TEXT("Real synchronous prewarm image missing"));return;}if(!Capturing)return;
  const auto G=Game.Get();const auto H=HUD.Get();const auto C=Controller.Get();const auto P=G?G->PlayerFighter.Get():nullptr;
  if(!Need(IsInGameThread()&&G&&H&&C,TEXT("Completed callback lost native Game/PC/HUD"))){BeginStop(Actor);return;}
  const auto& V=G->GetEquipmentView();const auto& B=H->GetFairytaleSwordDraw();const auto& A=H->GetFairytaleSwordAirDraw();const double Offset=FPlatformTime::Seconds()-Start;auto O=MakeShared<FJsonObject>();
  O->SetBoolField(TEXT("completed_callback"),true);O->SetBoolField(TEXT("has_player"),P!=nullptr);O->SetNumberField(TEXT("wall_offset_s"),Offset);O->SetNumberField(TEXT("phase"),Phase);O->SetNumberField(TEXT("sim"),G->GetSimulationTime());O->SetStringField(TEXT("run"),V.RunGuid.ToString(EGuidFormats::Digits));D144::Id(O,TEXT("owner"),V.OwnerId);D144::Id(O,TEXT("current_room"),V.RoomInstanceId);D144::Id(O,TEXT("epoch"),G->GetRunPresentationEpoch());D144::Id(O,TEXT("restart_serial"),G->GetRunRestartSerial());O->SetNumberField(TEXT("install_gate"),int32(G->GetRunInstallGate()));O->SetObjectField(TEXT("equipment_action"),D144::EquipmentAction(V.Action));D144::Id(O,TEXT("selected_source_id"),V.SelectedSourceId);D144::Id(O,TEXT("next_operation_id"),V.NextOperationId);O->SetArrayField(TEXT("camera_ground"),D144::XY(H->GetCameraGroundCenter()));O->SetObjectField(TEXT("old_draw"),D144::OldDraw(B));O->SetObjectField(TEXT("new_air_draw"),D144::NewDraw(A));O->SetArrayField(TEXT("rendered_player_stack"),D144::Strings(H->GetRenderedPlayerDrawStack()));O->SetBoolField(TEXT("interface_visible"),H->GetInterfaceVisible());O->SetNumberField(TEXT("text_calls"),H->GetRenderedTextDrawCalls());O->SetBoolField(TEXT("range_debug"),H->IsCombatRangeDebugEnabled());O->SetNumberField(TEXT("range_lines"),H->GetCombatRangeDebugLineCount());
  const int32 Index=Observations.Num();
  if(!P)
  {
   Observations.Add(MakeShared<FJsonValueObject>(O));Offsets.Add(MakeShared<FJsonValueNumber>(Offset));
   if(!Need(Restore&&Phase==10&&G->GetRunInstallGate()==EDungeonRunInstallGate::PristineBootstrap,TEXT("Missing Pawn outside true pristine target"))){BeginStop(Actor);return;}
   auto Facts=NoRunFacts();if(!Need(ValidPristine(Facts),TEXT("Actual target no-Run/noPawn origin violated"))){BeginStop(Actor);return;}if(PristineIndex==INDEX_NONE){PristineIndex=Index;PristineFacts=Facts;PristineFacts->SetNumberField(TEXT("observation_index"),Index);PristineFacts->SetNumberField(TEXT("wall_offset_s"),Offset);}return;
  }
  const auto& M=P->GetMeleeCombatState();const auto& DS=P->GetDodgeState();const int32 Pose=D144::PhysicalPose(P->JumpHeight,P->GetVerticalVelocity(),P->GetLandingVisualAge());
  D144::Id(O,TEXT("player_entity"),P->GetRuntimeEntityId());O->SetArrayField(TEXT("ground"),D144::XY(P->GetGroundPosition()));O->SetNumberField(TEXT("facing"),P->Facing);O->SetNumberField(TEXT("jump_height"),P->JumpHeight);O->SetNumberField(TEXT("vertical_velocity"),P->GetVerticalVelocity());O->SetNumberField(TEXT("landing_visual_age"),P->GetLandingVisualAge());O->SetNumberField(TEXT("physical_visual_key"),Pose);O->SetNumberField(TEXT("hp"),P->Health);O->SetBoolField(TEXT("dead"),P->bDead);O->SetStringField(TEXT("animation"),P->AnimationName);O->SetBoolField(TEXT("melee_grounded"),M.Grounded);O->SetBoolField(TEXT("wa_grounded"),P->GetWeaponActionsState().Budget.Grounded);O->SetNumberField(TEXT("melee_time"),M.Time);O->SetNumberField(TEXT("wa_time"),P->GetWeaponActionsState().Time);O->SetNumberField(TEXT("dodge_time"),DS.Time);O->SetNumberField(TEXT("weapon_world_time"),G->GetWeaponWorldState().Time);O->SetNumberField(TEXT("native_actor_root_z"),P->GetActorLocation().Z);
  FDungeonHeroAirSample Q;Q.Valid=true;Q.RunGuid=FGuid(1,2,3,4);Q.OwnerId=91;Q.RoomInstanceId=92;Q.PresentationEpoch=93;Q.NativeTime=-94.;Q.GroundPosition={95.,96.};Q.Facing=-1.f;Q.JumpHeight=97.f;Q.VerticalVelocity=-98.f;Q.LandingVisualAge=99.f;const auto Sentinel=Q;const bool QueryOK=P->QueryHeroNonAttackAir(Q);O->SetBoolField(TEXT("new_air_query_ok"),QueryOK);O->SetBoolField(TEXT("air_query_out_unchanged"),D144::SameSample(Q,Sentinel));
  if(V.ActiveSlot>=0&&V.ActiveSlot<3){D144::Id(O,TEXT("weapon_instance"),V.Slots[V.ActiveSlot].InstanceId);D144::Id(O,TEXT("weapon_version"),V.Slots[V.ActiveSlot].Version);}D144::Id(O,TEXT("armor_instance"),V.Slots[2].InstanceId);D144::Id(O,TEXT("armor_version"),V.Slots[2].Version);Observations.Add(MakeShared<FJsonValueObject>(O));Offsets.Add(MakeShared<FJsonValueNumber>(Offset));
  if(!Need(V.Bound&&V.RunGuid==Run&&V.OwnerId==Owner&&V.RoomInstanceId==Room&&P->GetRuntimeEntityId()==Owner&&G->GetRunPresentationEpoch()==Epoch&&G->GetRunRestartSerial()==Restart&&C->GetPawn()==P&&P->Health==InitialHP&&!P->bDead&&!G->bGameOver,TEXT("Real player identity/epoch/HP changed"))||!Need(!H->GetInterfaceVisible()&&!H->IsCombatRangeDebugEnabled()&&H->GetRenderedTextDrawCalls()==0&&H->GetCombatRangeDebugLineCount()==0,TEXT("Traditional HUD/range must remain hidden"))||(GearPinned&&!PinGear(P))){BeginStop(Actor);return;}
  if(!Restore&&Phase==5&&EIssued)
  {
   const auto& E=V.Action;
   if(E.Active)
   {if(!Need(E.Kind==EDungeonEquipmentActionKind::PickupArmor&&E.ActionId>0&&E.OperationId>0&&E.SourceId==LightSource&&E.InstanceId==Light&&E.Slot==2&&E.Start>=Inputs[EquipInputIndex]->AsObject()->GetNumberField(TEXT("sim"))&&E.Deadline==E.Start+.50&&E.Start<=G->GetSimulationTime()&&G->GetSimulationTime()<E.Deadline,TEXT("Actual normal E identity/.50 start/deadline differs"))){BeginStop(Actor);return;}if(EquipStartedIndex==INDEX_NONE){EquipStartedIndex=Index;EquipActionId=E.ActionId;EquipOperationId=E.OperationId;EquipStart=E.Start;EquipDeadline=E.Deadline;}if(!Need(E.ActionId==EquipActionId&&E.OperationId==EquipOperationId&&E.Start==EquipStart&&E.Deadline==EquipDeadline&&V.NextOperationId==EquipOperationId,TEXT("Actual E operation changed before commit"))){BeginStop(Actor);return;}}
   else if(EquipStartedIndex!=INDEX_NONE&&EquipCommitIndex==INDEX_NONE)
   {if(!Need(E.Kind==EDungeonEquipmentActionKind::PickupArmor&&E.ActionId==EquipActionId&&E.OperationId==EquipOperationId&&E.SourceId==LightSource&&E.InstanceId==Light&&E.Slot==2&&E.Start==EquipStart&&E.Deadline==EquipDeadline&&G->GetSimulationTime()>=EquipDeadline&&V.Slots[2].InstanceId==Light&&V.Slots[2].Version>0&&V.NextOperationId==EquipOperationId+1,TEXT("Actual E active-to-commit receipt differs"))){BeginStop(Actor);return;}EquipCommitIndex=Index;}
  }
  const bool Fresh=B.DrawId>LastDraw&&B.SimulationTime==G->GetSimulationTime()&&B.DrawStack==H->GetRenderedPlayerDrawStack();
  if(!Fresh){if(Restore||Phase==6){Need(false,TEXT("Formal Air/target completed draw is stale or mismatches actual stack"));BeginStop(Actor);}return;}LastDraw=B.DrawId;
  if(!Restore&&Phase==5&&GearPinned&&EquipCommitIndex!=INDEX_NONE&&Index>=EquipCommitIndex&&ReadyIndex==INDEX_NONE&&P->Facing==1.f&&P->JumpHeight==0.f&&P->GetVerticalVelocity()==0.f&&P->GetLandingVisualAge()==.12f&&D144::Brown(B,false)&&!A.Drawn)ReadyIndex=Index;
  if((!Restore&&Phase==6)||(Restore&&(Phase==11||Phase==12)))
  {
   if(Pose>=0)
   {
    if(!Need(QueryOK&&Q.Valid&&A.Drawn&&A.AtomicPreflightReady&&A.PlayerEntityId==Owner&&A.SimulationTime==G->GetSimulationTime()&&A.Plan.Frame==Pose&&A.Plan.Facing==1&&A.Plan.Sample.PresentationEpoch==Epoch&&A.Slots.Num()==9&&A.ResidentTextures.Num()==49&&A.ActualRenderedStack==B.DrawStack,TEXT("Actual same-epoch Air callback lacks complete native nine layers"))){BeginStop(Actor);return;}
    if(Restore){if(!Need(Pose>=2,TEXT("Target reset into Rise instead of continuing the saved Apex"))){BeginStop(Actor);return;}ContinuedMask|=1u<<Pose;}
   }
   if(!Restore&&Pose==2)
   {ApexIndex=Index;if(SaveApex(Index,A,P)){FlowComplete=Need(ReadyConsumed&&JumpInputs==1&&EquipStartedIndex!=INDEX_NONE&&EquipCommitIndex!=INDEX_NONE,TEXT("Source save lacks normal E/Ready/one Space lineage"));CaptureFinalHP=P->Health;}BeginStop(Actor);return;}
   // InputKey enqueues Enter after the GM Tick; the same frame can legitimately
   // finish one more Await callback before the following native Tick opens it.
   if(Restore&&(Phase==11||(Phase==12&&G->GetRunInstallGate()==EDungeonRunInstallGate::AwaitExplicitContinue)))
   {
    if(!Need(G->GetRunInstallGate()==EDungeonRunInstallGate::AwaitExplicitContinue&&Pose==2&&G->GetSimulationTime()==Saved.SimulationTime,TEXT("Published target did not remain on gated original Apex"))){BeginStop(Actor);return;}
    TArray<uint8> Bytes;if(!CaptureCodec(Bytes)||!Need(Bytes==SavedCodec,TEXT("Whole target Codec changed while AwaitExplicitContinue"))){BeginStop(Actor);return;}auto Copy=SaveBytes(FString::Printf(TEXT("pause-codec-%06d.json"),PauseCount),Bytes);if(!Copy){BeginStop(Actor);return;}auto Check=MakeShared<FJsonObject>();Check->SetNumberField(TEXT("observation_index"),Index);Check->SetNumberField(TEXT("wall_offset_s"),Offset);Check->SetNumberField(TEXT("sim"),G->GetSimulationTime());Check->SetNumberField(TEXT("install_gate"),int32(G->GetRunInstallGate()));D144::Id(Check,TEXT("epoch"),Epoch);D144::Id(Check,TEXT("restart_serial"),Restart);Check->SetObjectField(TEXT("codec"),Copy);Check->SetBoolField(TEXT("whole_equal_loaded"),Bytes==SavedCodec);PauseChecks.Add(MakeShared<FJsonValueObject>(Check));LastPausedWall=Start+Offset;++PauseCount;auto Neutral=Controls(Index);NeutralChecks.Add(MakeShared<FJsonValueObject>(Neutral));if(Phase==11){if(NeutralReleased&&Neutral->GetBoolField(TEXT("neutral_all"))&&!Neutral->GetBoolField(TEXT("enter_just_pressed")))++NeutralCount;else NeutralCount=0;}return;
   }
   if(Restore&&Phase==12)
   {
    if(!Need(ResumeIssued&&G->GetRunInstallGate()==EDungeonRunInstallGate::Open&&G->GetSimulationTime()>=Saved.SimulationTime,TEXT("Fresh Enter did not open the original Run gate"))){BeginStop(Actor);return;}if(FirstOpenIndex==INDEX_NONE)FirstOpenIndex=Index;
    if(Pose<0&&D144::Brown(B,false)&&!A.Drawn&&P->JumpHeight==0.f&&P->GetVerticalVelocity()==0.f&&P->GetLandingVisualAge()==.12f)
    {++ReadyJoinFrames;if(ReadyJoinFrames>=2){FlowComplete=Need((ContinuedMask&60u)==60u&&JumpInputs==0&&G->GetSimulationTime()>Saved.SimulationTime&&PauseCount>=3&&NeutralCount>=1,TEXT("Original target trajectory/paused neutral/Ready coverage incomplete"))&&FinalDiskCheck();CaptureFinalHP=P->Health;BeginStop(Actor);return;}}
   }
  }
 }

 bool CheckActualModule()
 {
  const FString Path=FPaths::ConvertRelativePathToFull(FModuleManager::Get().GetModuleFilename(FName(TEXT("CodexDungeon"))));TArray<uint8> Bytes;
  if(!Need(!Path.IsEmpty()&&FFileHelper::LoadFileToArray(Bytes,*Path),TEXT("Cannot read actual loaded CodexDungeon module")))return false;const FString ActualSHA=D144::Store::FGenerationStore::Sha256(Bytes);auto O=MakeShared<FJsonObject>();O->SetStringField(TEXT("path"),Path);O->SetNumberField(TEXT("bytes"),Bytes.Num());O->SetStringField(TEXT("sha256"),ActualSHA);Report->SetObjectField(TEXT("actual_game_module"),O);return Need(ActualSHA==DLLSHA,TEXT("Root GameDLL parameter differs from actual loaded module; V2 does not imply binary compatibility"));
 }
 void Finalize(ADungeonHeroAirDiskRestoreProbeV001& Actor)
 {
  if(Stopped)return;Stopped=true;GIsDumpingMovie=0;ReleaseKeys();if(Prepared.IsReady())Prepared=FDungeonPreparedRun();const bool Flushed=FlushFastLosslessProofScreenshots();const bool AudioComplete=Actor.MainMixCapture&&Actor.MainMixCapture->Status().Phase==EDungeonNativeMixCapturePhaseV001::Complete;
  auto R=Report;R->SetStringField(TEXT("schema"),TEXT("hero-air-disk-restore-native-observer-v001"));R->SetStringField(TEXT("role"),Role);D144::Id(R,TEXT("process_id"),FPlatformProcess::GetCurrentProcessId());R->SetBoolField(TEXT("passed"),Failure.IsEmpty()&&FlowComplete&&Flushed&&AudioComplete&&StartupReadbackComplete&&Start>StartupReadbackStop);R->SetBoolField(TEXT("flow_complete"),FlowComplete);R->SetStringField(TEXT("failure"),Failure);R->SetStringField(TEXT("build_id"),BuildId);R->SetStringField(TEXT("compiled_manifest_sha256"),CompiledSHA);R->SetStringField(TEXT("expected_game_dll_sha256"),DLLSHA);R->SetStringField(TEXT("profile_id"),ProfileId.ToString(EGuidFormats::DigitsWithHyphensLower));R->SetStringField(TEXT("profiles_directory"),ProfilesDirectory);R->SetStringField(TEXT("profile_directory"),ProfileDirectory);R->SetStringField(TEXT("run"),Run.ToString(EGuidFormats::Digits));D144::Id(R,TEXT("owner"),Owner);D144::Id(R,TEXT("current_room"),Room);D144::Id(R,TEXT("epoch"),Epoch);D144::Id(R,TEXT("restart_serial"),Restart);D144::Id(R,TEXT("weapon_instance"),Sword);D144::Id(R,TEXT("weapon_version"),SwordVersion);D144::Id(R,TEXT("armor_instance"),Light);D144::Id(R,TEXT("armor_version"),LightVersion);R->SetNumberField(TEXT("requested_facing"),1);R->SetNumberField(TEXT("initial_hp"),InitialHP);R->SetNumberField(TEXT("capture_final_hp"),CaptureFinalHP);R->SetNumberField(TEXT("normal_space_down_inputs"),JumpInputs);
  D144::Id(Equipment,TEXT("light_source_id"),LightSource);Equipment->SetNumberField(TEXT("equipment_input_index"),EquipInputIndex);Equipment->SetNumberField(TEXT("equipment_started_callback_index"),EquipStartedIndex);Equipment->SetNumberField(TEXT("equipment_commit_callback_index"),EquipCommitIndex);Equipment->SetNumberField(TEXT("equipment_start"),EquipStart);Equipment->SetNumberField(TEXT("equipment_deadline"),EquipDeadline);Equipment->SetNumberField(TEXT("ready_callback_index"),ReadyIndex);Equipment->SetBoolField(TEXT("ready_consumed_once"),ReadyConsumed);R->SetObjectField(TEXT("equipment"),Equipment);R->SetObjectField(TEXT("checkpoint"),Checkpoint);R->SetObjectField(TEXT("disk"),DiskFacts);if(PristineFacts)R->SetObjectField(TEXT("pristine_before"),PristineFacts);R->SetObjectField(TEXT("prepare_install"),PrepareFacts);R->SetArrayField(TEXT("pause_checks"),PauseChecks);R->SetArrayField(TEXT("neutral_checks"),NeutralChecks);
  ResumeFacts->SetNumberField(TEXT("enter_input_index"),ResumeInputIndex);ResumeFacts->SetNumberField(TEXT("first_open_callback_index"),FirstOpenIndex);ResumeFacts->SetNumberField(TEXT("continued_mask"),ContinuedMask);ResumeFacts->SetNumberField(TEXT("ready_join_frames"),ReadyJoinFrames);ResumeFacts->SetNumberField(TEXT("normal_space_down_inputs"),JumpInputs);ResumeFacts->SetBoolField(TEXT("simulation_advanced_from_saved"),Game.IsValid()&&Game->GetSimulationTime()>Saved.SimulationTime);R->SetObjectField(TEXT("resume"),ResumeFacts);
  R->SetArrayField(TEXT("normal_inputs"),Inputs);R->SetArrayField(TEXT("observations"),Observations);R->SetArrayField(TEXT("steps"),Steps);R->SetArrayField(TEXT("diagnostic_knight_hits"),DiagnosticHits);R->SetArrayField(TEXT("startup_resource_readbacks"),StartupTextures);TArray<JV> Air49;for(int32 I=0;I<FMath::Min(49,StartupTextures.Num());++I)Air49.Add(StartupTextures[I]);R->SetArrayField(TEXT("startup_actual_GPU_source_textures49"),Air49);R->SetBoolField(TEXT("startup_readback_complete"),StartupReadbackComplete);R->SetNumberField(TEXT("startup_readback_stop_monotonic_s"),StartupReadbackStop);R->SetBoolField(TEXT("native_async_capture_writes_flushed"),Flushed);auto Timing=MakeShared<FJsonObject>();Timing->SetBoolField(TEXT("use_fixed_time_step"),FApp::UseFixedTimeStep());Timing->SetNumberField(TEXT("capture_start_monotonic_s"),Start);Timing->SetNumberField(TEXT("capture_stop_monotonic_s"),Stop);Timing->SetArrayField(TEXT("frame_wall_offsets_s"),Offsets);R->SetObjectField(TEXT("capture_timing"),Timing);if(Actor.MainMixCapture)R->SetObjectField(TEXT("main_submix_capture"),Actor.MainMixCapture->SerializeReport());
  R->SetBoolField(TEXT("final_accepted"),false);R->SetBoolField(TEXT("visual_reviewed"),false);R->SetBoolField(TEXT("audio_listened"),false);R->SetBoolField(TEXT("observer_forced_gameplay_writes"),false);R->SetBoolField(TEXT("snapshot_restoration_via_actual_installer"),Restore&&PrepareFacts->HasField(TEXT("install_ok"))&&PrepareFacts->GetBoolField(TEXT("install_ok")));R->SetBoolField(TEXT("game_tick_called_manually"),false);R->SetBoolField(TEXT("V2_itself_proves_running_binary_compatibility"),false);FString Text;auto Writer=TJsonWriterFactory<>::Create(&Text);const bool Serialized=FJsonSerializer::Serialize(R.ToSharedRef(),Writer);const bool Written=Serialized&&EvidenceClaimed&&D144::WriteNewUTF8(Directory/TEXT("runtime-report.json"),Text);if(!Failure.IsEmpty())UE_LOG(LogTemp,Error,TEXT("Air disk restore %s: %s"),*Role,*Failure);FPlatformMisc::RequestExitWithStatus(false,Failure.IsEmpty()&&FlowComplete&&Flushed&&AudioComplete&&Written?0:3);
 }
 void Tick(ADungeonHeroAirDiskRestoreProbeV001& Actor)
 {
  if(Stopped)return;const double Now=FPlatformTime::Seconds();if(Actor.MainMixCapture)Actor.MainMixCapture->Poll();if(Stopping){if(!Actor.MainMixCapture||Actor.MainMixCapture->IsTerminal())Finalize(Actor);return;}if(!Failure.IsEmpty()){BeginStop(Actor);return;}
  const auto W=Actor.GetWorld();const auto G=W?W->GetAuthGameMode<ADungeonGameMode>():nullptr;const auto C=UGameplayStatics::GetPlayerController(&Actor,0);const auto H=C?Cast<ADungeonHUD>(C->GetHUD()):nullptr;
  if(!Game.IsValid()&&Now-WarmStarted>12.){Need(false,TEXT("Native PC/HUD/role bootstrap timeout"));BeginStop(Actor);return;}
  if(!Game.IsValid()&&G&&C&&C->IsLocalController()&&C->HasAuthority()&&C->PlayerInput&&C->PlayerState&&H)
  {
   if(Restore){FString Why;if(!G->IsPristineContinueBootstrap(Why))return;}
   else{const auto P=G->PlayerFighter.Get();const auto& V=G->GetEquipmentView();if(!P||!V.Bound||!V.RunGuid.IsValid()||V.ActiveSlot<0||V.ActiveSlot>=3)return;Run=V.RunGuid;Owner=V.OwnerId;Room=V.RoomInstanceId;Epoch=G->GetRunPresentationEpoch();Restart=G->GetRunRestartSerial();InitialHP=P->Health;Sword=V.Slots[V.ActiveSlot].InstanceId;SwordVersion=V.Slots[V.ActiveSlot].Version;if(!Need(Epoch==0&&Restart==1,TEXT("Source must be its fresh formal FirstBatch run")))return;}
   Game=G;Controller=C;HUD=H;Report->SetStringField(TEXT("world_map_url"),W->URL.ToString());const bool FirstBatchURL=W->URL.HasOption(TEXT("DungeonFirstBatchGuardRoom"));const bool PristineURL=W->URL.HasOption(TEXT("DungeonContinuePristine"));Report->SetBoolField(TEXT("source_first_batch_url"),FirstBatchURL);Report->SetBoolField(TEXT("target_pristine_url"),PristineURL);if(!Need(Restore?(PristineURL&&!FirstBatchURL):(FirstBatchURL&&!PristineURL),TEXT("Actual world URL differs from the disjoint formal/pristine role")))return;Actor.AddTickPrerequisiteActor(G);Actor.AddTickPrerequisiteActor(H);if(!CheckActualModule())return;return;
  }
  if(!Game.IsValid())return;if(PulseKey.IsValid()&&Now>=ReleaseAt){Key(PulseKey,false);PulseKey=FKey();NeutralUntil=Now+.04;}
  if(!Capturing)
  {
   if(!StartupReadbackComplete){CaptureTextureBytesBeforeAudio(Actor);return;}
   if(!PrewarmRequested){PrewarmRequested=true;FScreenshotRequest::RequestScreenshot(Directory/TEXT("prewarm-viewport.png"),false,false,false);}
   if(PrewarmDone&&!AudioRequested){AudioRequested=true;Actor.MainMixCapture=NewObject<UDungeonNativeMainSubmixCaptureV001>(&Actor);if(!Actor.MainMixCapture->Begin(Actor.GetWorld(),Directory/TEXT("audio-v001")))Need(false,TEXT("Native main mix Arming rejected"));}
   if(AudioRequested&&Actor.MainMixCapture&&Actor.MainMixCapture->Status().Phase==EDungeonNativeMixCapturePhaseV001::Recording){const auto& Status=Actor.MainMixCapture->Status();if(!Need(Status.StartRequested&&Status.StartMonotonic>0.,TEXT("Actual shared Recording origin absent")))return;Start=Status.StartMonotonic;Capturing=true;GIsDumpingMovie=-1;Next(Restore?10:0);}
   if(Now-WarmStarted>45.)Need(false,TEXT("Native readback/prewarm/Recording timeout"));return;
  }
  if(!Need(G&&C&&H&&G==Game.Get()&&C==Controller.Get()&&H==HUD.Get()&&Now-Start<15.&&Now-PhaseAt<7.,TEXT("Role/owner/capture timeout")))return;
  if(Restore)
  {
   if(Phase==10){if(PristineIndex!=INDEX_NONE)LoadAndInstall();return;}
   const auto P=G->PlayerFighter.Get();if(!Need(P&&C->GetPawn()==P&&PinGear(P),TEXT("Target lost its installed native player")))return;
   if(Phase==11&&PauseCount>=3&&NeutralCount>=1&&LastPausedWall-InstalledWall>=.20&&CanPulse())
   {if(!Need(G->GetRunInstallGate()==EDungeonRunInstallGate::AwaitExplicitContinue&&!Observations.IsEmpty()&&Controls(Observations.Num()-1)->GetBoolField(TEXT("neutral_all")),TEXT("Full controls not neutral before fresh target Enter")))return;ResumeFacts->SetNumberField(TEXT("last_paused_callback_index"),Observations.Num()-1);ResumeInputIndex=Inputs.Num();if(Pulse(EKeys::Enter)){ResumeIssued=true;Next(12);}return;}
   if(Phase!=11&&Phase!=12)Need(false,TEXT("Unexpected target role phase"));return;
  }
  const auto P=G->PlayerFighter.Get();FDungeonFirstBatchGuardRoomView View;if(!Need(P&&C->GetPawn()==P&&G->QueryFirstBatchGuardRoom(View)&&View.Slots.Num()==3,TEXT("Source requires real formal FirstBatch/native player")))return;
  switch(Phase)
  {
   case 0:if(!Need(G->bWaitingForStart&&G->GetSimulationTime()==0.,TEXT("Source normal Enter must start original waiting Run")))return;if(Pulse(EKeys::Enter))Next(1);break;
   case 1:if(!G->bWaitingForStart&&CanPulse()&&ClearKnightIfRequested(P,View)){Key(EKeys::D,true);Next(2);}break;
   case 2:if(P->GetGroundPosition().X>=DungeonRoomLayout::ExplorationPreview().Entry.X+280.){Key(EKeys::D,false);NeutralUntil=Now+.04;Next(3);}break;
   case 3:if(CanPulse()&&Pulse(EKeys::D))Next(4);break;
   case 4:if(CanPulse()&&P->Facing==1.f){DungeonEquipmentInventory::FItem Item;Item.ContentId="ARM-LGT-001";const auto Registered=G->RegisterEquipmentSource(TEXT("display.hero.air.disk.light.v001"),Item,P->GetGroundPosition()+FVector2D(24.,0.),true);if(!Need(Registered.Ok()&&!Registered.Replayed,TEXT("Actual source display LGT registration failed")))return;LightSource=Registered.SourceId;Light=Registered.InstanceId;Next(5);}break;
   case 5:if(!EIssued){if(CanPulse()&&G->GetEquipmentView().SelectedSourceId==LightSource){EquipInputIndex=Inputs.Num();if(Pulse(EKeys::E))EIssued=true;}break;}if(!G->GetEquipmentView().Action.Active&&G->GetEquipmentView().Slots[2].InstanceId==Light&&PinGear(P)&&CanPulse()&&ReadyIndex!=INDEX_NONE){const auto Ready=Observations[ReadyIndex]->AsObject();if(!Need(!ReadyConsumed&&Ready->GetNumberField(TEXT("sim"))<=G->GetSimulationTime()&&Now-Start>Ready->GetNumberField(TEXT("wall_offset_s")),TEXT("Source completed Ready token stale/reused")))return;if(Pulse(EKeys::SpaceBar)){ReadyConsumed=true;++JumpInputs;Next(6);}}break;
   case 6:break;default:Need(false,TEXT("Unexpected source role phase"));break;
  }
 }
};

void FDungeonHeroAirDiskRestoreProofDeleterV001::operator()(FDungeonHeroAirDiskRestoreProofStateV001* Value)const{delete Value;}
ADungeonHeroAirDiskRestoreProbeV001::ADungeonHeroAirDiskRestoreProbeV001(){PrimaryActorTick.bCanEverTick=true;}
ADungeonHeroAirDiskRestoreProbeV001::~ADungeonHeroAirDiskRestoreProbeV001()=default;
void ADungeonHeroAirDiskRestoreProbeV001::BeginPlay()
{
 Super::BeginPlay();Proof.Reset(new FDungeonHeroAirDiskRestoreProofStateV001);Proof->WarmStarted=FPlatformTime::Seconds();const TCHAR* Cmd=FCommandLine::Get();FParse::Value(Cmd,TEXT("DungeonContentProofDir="),Proof->Directory);FParse::Value(Cmd,TEXT("DungeonHeroAirDiskRole="),Proof->Role);Proof->Restore=Proof->Role==TEXT("target");FParse::Value(Cmd,TEXT("DungeonHeroAirDiskProfilesDir="),Proof->ProfilesDirectory);FParse::Value(Cmd,TEXT("DungeonHeroAirDiskBuildId="),Proof->BuildId);FParse::Value(Cmd,TEXT("DungeonHeroAirDiskCompiledManifestSHA="),Proof->CompiledSHA);FParse::Value(Cmd,TEXT("DungeonHeroAirDiskGameDLLSHA="),Proof->DLLSHA);FString ProfileText,RunText;FParse::Value(Cmd,TEXT("DungeonHeroAirDiskProfileGuid="),ProfileText);FParse::Value(Cmd,TEXT("DungeonHeroAirDiskExpectedRun="),RunText);FParse::Value(Cmd,TEXT("DungeonHeroAirDiskExpectedOwner="),Proof->ExpectedOwner);FParse::Value(Cmd,TEXT("DungeonHeroAirDiskExpectedCodecSHA="),Proof->ExpectedCodecSHA);FParse::Value(Cmd,TEXT("DungeonHeroAirDiskSourcePID="),Proof->SourcePID);Proof->AllowKnightDiagnostic=FParse::Param(Cmd,TEXT("DungeonHeroAirDiskClearKnightDiagnostic"));
 if(!Proof->Need((Proof->Role==TEXT("source")||Proof->Restore)&&!Proof->Directory.IsEmpty()&&!FPaths::IsRelative(Proof->Directory)&&FGuid::ParseExact(ProfileText,EGuidFormats::DigitsWithHyphensLower,Proof->ProfileId)&&Proof->ProfileId.IsValid()&&Proof->ProfileId.ToString(EGuidFormats::DigitsWithHyphensLower)==ProfileText&&!Proof->ProfilesDirectory.IsEmpty()&&!FPaths::IsRelative(Proof->ProfilesDirectory)&&D144::SHA(Proof->CompiledSHA)&&D144::SHA(Proof->DLLSHA)&&Proof->BuildId==TEXT("v144-")+Proof->CompiledSHA+TEXT("-")+Proof->DLLSHA,TEXT("Exact disjoint role/absolute paths/new ProfileGuid/Root current CM-DLL BuildId parameters required")))return;
 const FString NormalProfiles=FPaths::ConvertRelativePathToFull(Proof->ProfilesDirectory);FString Normalized=NormalProfiles;FPaths::NormalizeDirectoryName(Normalized);if(!Proof->Need(Normalized==Proof->ProfilesDirectory&&FPaths::GetCleanFilename(Normalized)==D144::Adapter::DirectoryName,TEXT("Profiles path must already be normalized BoundRunOnly-v2")))return;Proof->ProfileDirectory=Proof->ProfilesDirectory/ProfileText;
 if(Proof->Restore){if(!Proof->Need(!Proof->AllowKnightDiagnostic&&FGuid::ParseExact(RunText,EGuidFormats::Digits,Proof->ExpectedRun)&&Proof->ExpectedRun.IsValid()&&Proof->ExpectedOwner>0&&D144::SHA(Proof->ExpectedCodecSHA)&&Proof->SourcePID>0&&Proof->SourcePID<=MAX_uint32&&Proof->SourcePID!=FPlatformProcess::GetCurrentProcessId(),TEXT("Target needs exact exited source identity/whole Codec/PID and forbids diagnostics")))return;const bool Running=FPlatformProcess::IsApplicationRunning(uint32(Proof->SourcePID));Proof->Report->SetBoolField(TEXT("source_process_running_at_target_begin"),Running);D144::Id(Proof->Report,TEXT("expected_source_pid"),Proof->SourcePID);if(!Proof->Need(!Running&&IFileManager::Get().DirectoryExists(*Proof->ProfileDirectory),TEXT("Source process still alive or real published Profile missing")))return;}
 else if(!Proof->Need(RunText.IsEmpty()&&Proof->ExpectedOwner==0&&Proof->ExpectedCodecSHA.IsEmpty()&&Proof->SourcePID==0&&!IFileManager::Get().DirectoryExists(*Proof->ProfileDirectory),TEXT("Source must own a completely unused Profile and no target-only parameters")))return;
 Proof->Directory=FPaths::ConvertRelativePathToFull(Proof->Directory);FPaths::NormalizeDirectoryName(Proof->Directory);IFileManager::Get().MakeDirectory(*Proof->Directory,true);TArray<FString> Prior,Subdirs;IFileManager::Get().FindFiles(Prior,*(Proof->Directory/TEXT("*")),true,false);Prior.Remove(TEXT("native-lossless-capture.json"));IFileManager::Get().FindFiles(Subdirs,*(Proof->Directory/TEXT("*")),false,true);if(!Proof->Need(Prior.Num()==0&&Subdirs.Num()==0,TEXT("Evidence directory already occupied")))return;
 if(!Proof->Need(D144::WriteNewUTF8(Proof->Directory/TEXT("observer-process-claim-v001.json"),FString::Printf(TEXT("{\"schema\":\"hero-air-disk-restore-process-claim-v001\",\"process_id\":\"%u\"}"),FPlatformProcess::GetCurrentProcessId())),TEXT("Exclusive process claim failed")))return;Proof->EvidenceClaimed=true;
 for(const TCHAR* Flag:{TEXT("DungeonHeroAirDiskRestoreProofV001"),TEXT("DungeonContentProof"),TEXT("DungeonFastLosslessCapture"),TEXT("DungeonAsyncLosslessCapture"),TEXT("DungeonCandidateSprites"),TEXT("DungeonFairytaleSwordEquipmentBoundPreview"),TEXT("DungeonFairytaleLeatherReadyPreview"),TEXT("DungeonFairytaleLeatherPrimary1Preview"),TEXT("DungeonFairytaleLeatherPrimary2Preview"),TEXT("DungeonFairytaleLeatherPrimary3Preview"),TEXT("DungeonFairytaleSwordWalkPreview"),TEXT("DungeonFairytaleSwordHurtPreview"),TEXT("DungeonFairytaleSwordDeathPreview"),TEXT("DungeonFairytaleSwordDodgePreview"),TEXT("DungeonFairytaleSwordAirPreview"),TEXT("DungeonFairytaleGuardFullPreview"),TEXT("DungeonFairytaleGuardStompPreview"),TEXT("DungeonFairytaleGuardMoveRigPreview")})if(!Proof->Need(FParse::Param(Cmd,Flag),TEXT("Minimum original visual/capture flag missing: ")+FString(Flag)))return;
 for(const TCHAR* Flag:{TEXT("FirstBatchSchema2"),TEXT("DungeonProof"),TEXT("DungeonHeroLandingPriorityProofV001"),TEXT("DungeonHeroAirProductionProofV001"),TEXT("DungeonHeroAirProofV001"),TEXT("DungeonHeroDodgeProofV001"),TEXT("DungeonHeroHurtProofV001"),TEXT("DungeonHeroDeathProofV001"),TEXT("DungeonGuardMoveProofV001"),TEXT("DungeonGuardStompProofV001"),TEXT("DungeonGuardArtCombatProofV003"),TEXT("DungeonGuardArtDeathProofV005"),TEXT("DungeonGuardArtKnown44Proof"),TEXT("DungeonGuardArtPartialProof"),TEXT("DungeonGuardRoomFlowProof"),TEXT("DungeonGuardRoomManualLightSource"),TEXT("DungeonFairytaleWalkProof"),TEXT("DungeonFairytaleEquipmentBoundProof"),TEXT("DungeonFairytaleSwordBodyProof"),TEXT("DungeonRunSaveProof"),TEXT("DungeonRunRestoreProof"),TEXT("DungeonGuardRunSaveProof"),TEXT("DungeonGuardRunRestoreProof"),TEXT("DungeonFairytaleLookdevProof"),TEXT("DungeonFairytaleLookdevPreview"),TEXT("DungeonCombatRangeDebug"),TEXT("DungeonCombatRangeProof"),TEXT("DungeonShowInterface")})if(!Proof->Need(!FParse::Param(Cmd,Flag),TEXT("Other proof/HUD/range flag cannot share disk observer")))return;
 for(TActorIterator<ADungeonContentProbe> It(GetWorld());It;++It)if(IsValid(*It)){Proof->Need(false,TEXT("Old ContentProbe already exists"));return;}if(!Proof->Need(!FApp::UseFixedTimeStep(),TEXT("Original variable native pacing required")))return;GetMutableDefault<UEngine>()->GameScreenshotSaveDirectory.Path=Proof->Directory;FScreenshotRequest::OnScreenshotRequestProcessed().AddUObject(this,&ADungeonHeroAirDiskRestoreProbeV001::ScreenshotProcessed);
}
void ADungeonHeroAirDiskRestoreProbeV001::ScreenshotProcessed(){if(Proof)Proof->Observe(*this);}
void ADungeonHeroAirDiskRestoreProbeV001::Tick(float Delta){Super::Tick(Delta);if(Proof)Proof->Tick(*this);}
void ADungeonHeroAirDiskRestoreProbeV001::EndPlay(const EEndPlayReason::Type Reason)
{FScreenshotRequest::OnScreenshotRequestProcessed().RemoveAll(this);if(Proof&&!Proof->Stopped){Proof->Need(false,TEXT("Disk observer world ended before complete export"));GIsDumpingMovie=0;if(MainMixCapture&&!MainMixCapture->IsTerminal())MainMixCapture->Abort(TEXT("Disk observer world ended before export"));Proof->BeginStop(*this);Proof->Finalize(*this);}Super::EndPlay(Reason);}
