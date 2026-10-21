#include "DungeonSwdForwardStepProbeV001.h"
#include "DungeonGameMode.h"
#include "DungeonFighter.h"
#include "DungeonHUD.h"
#include "DungeonContentProbe.h"
#include "DungeonNativeMainSubmixCaptureV001.h"
#include "DungeonFairytaleSwordSecondaryPlanV001.h"
#include "DungeonFairytaleSwordEquipmentBinding.h"
#include "DungeonProofScreenshots.h"
#include "Engine/Engine.h"
#include "Engine/Texture2D.h"
#include "Engine/World.h"
#include "EngineUtils.h"
#include "TextureResource.h"
#include "UObject/StrongObjectPtr.h"
#if WITH_EDITOR
#include "TextureCompiler.h"
#endif
#include "RenderingThread.h"
#include "RHICommandList.h"
#include "Misc/Crc.h"
#include "GameFramework/PlayerController.h"
#include "GameFramework/PlayerInput.h"
#include "Kismet/GameplayStatics.h"
#include "UnrealClient.h"
#include "HAL/FileManager.h"
#include "HAL/PlatformMisc.h"
#include "HAL/PlatformProcess.h"
#include "HAL/PlatformTime.h"
#include "HAL/IConsoleManager.h"
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
#include "DungeonGameMode.h"
#include "DungeonFighter.h"
#include "DungeonHUD.h"
#include "Dom/JsonObject.h"
#include "HAL/PlatformTime.h"
namespace DungeonSwdForwardStepObservationV001 {
using JO=TSharedPtr<FJsonObject>; using JV=TSharedPtr<FJsonValue>;
inline void Id(JO O,const TCHAR* K,uint64 V){O->SetStringField(K,FString::Printf(TEXT("%llu"),(unsigned long long)V));}
inline TArray<JV> XY(FVector2D V){return {MakeShared<FJsonValueNumber>(V.X),MakeShared<FJsonValueNumber>(V.Y)};}
inline JO Action(const DungeonWeaponActions::FAction& A,double Now){
 auto O=MakeShared<FJsonObject>();Id(O,TEXT("action_id"),A.ActionId);Id(O,TEXT("instance_id"),A.InstanceId);
 O->SetNumberField(TEXT("type"),int32(A.Type));O->SetNumberField(TEXT("weapon"),int32(A.Weapon));O->SetNumberField(TEXT("phase"),int32(A.Phase));
 O->SetBoolField(TEXT("active"),A.Active);O->SetBoolField(TEXT("locked"),A.Locked);O->SetBoolField(TEXT("started_airborne"),A.StartedAirborne);O->SetBoolField(TEXT("forward_step_issued"),A.ForwardStepIssued);O->SetNumberField(TEXT("next_subhit"),A.NextSubhit);
 O->SetNumberField(TEXT("speed_pct"),A.SpeedPct);O->SetNumberField(TEXT("cooldown_duration"),A.CooldownDuration);O->SetNumberField(TEXT("facing"),A.Facing);O->SetNumberField(TEXT("start"),A.Start);O->SetNumberField(TEXT("lock_at"),A.LockAt);O->SetNumberField(TEXT("active_at"),A.ActiveAt);O->SetNumberField(TEXT("active_end"),A.ActiveEnd);O->SetNumberField(TEXT("end"),A.End);O->SetNumberField(TEXT("sample_time"),Now);O->SetNumberField(TEXT("terminal"),int32(A.Terminal));return O;
}
inline JO Fact(const FDungeonActionAudioRecord& R){
 auto O=MakeShared<FJsonObject>();Id(O,TEXT("sequence"),R.Sequence);O->SetStringField(TEXT("cue"),R.Cue);O->SetNumberField(TEXT("at_time"),R.AtTime);O->SetStringField(TEXT("run"),R.RunGuid.ToString(EGuidFormats::Digits));
 Id(O,TEXT("room"),R.RoomInstanceId);Id(O,TEXT("owner"),R.OwnerId);Id(O,TEXT("action_id"),R.ActionId);Id(O,TEXT("instance_id"),R.InstanceId);Id(O,TEXT("operation_id"),R.OperationId);Id(O,TEXT("revision"),R.Revision);
 auto W=MakeShared<FJsonObject>();W->SetBoolField(TEXT("present"),R.ForwardStep.Present);
 if(R.ForwardStep.Present){Id(W,TEXT("event_id"),R.ForwardStep.EventId);Id(W,TEXT("subhit_id"),R.ForwardStep.SubhitId);W->SetNumberField(TEXT("requested_signed_distance"),R.ForwardStep.RequestedSignedDistance);W->SetArrayField(TEXT("before"),XY(R.ForwardStep.Before));W->SetArrayField(TEXT("after"),XY(R.ForwardStep.After));W->SetArrayField(TEXT("committed_delta"),XY(R.ForwardStep.CommittedDelta));}
 else for(const TCHAR* K:{TEXT("event_id"),TEXT("subhit_id"),TEXT("requested_signed_distance"),TEXT("before"),TEXT("after"),TEXT("committed_delta")})W->SetField(K,MakeShared<FJsonValueNull>());
 O->SetObjectField(TEXT("forward_step"),W);return O;
}
struct FCursor {
 FString Scope;uint64 LastFact=0,LastRequest=0;int32 ScopeChanges=0;uint64 FactGaps=0;double PreviousWall=0.;TArray<JV> Facts,Requests;
 JO Observe(const ADungeonGameMode& G,const ADungeonFighter& P,const ADungeonHUD& H,int32 Callback,double Start){
  const double Wall=FPlatformTime::Seconds();const auto& V=G.GetEquipmentView();const FString S=V.RunGuid.ToString(EGuidFormats::Digits)+FString::Printf(TEXT("/%llu/%llu/%llu/%llu"),(unsigned long long)V.RoomInstanceId,(unsigned long long)V.OwnerId,(unsigned long long)G.GetRunRestartSerial(),(unsigned long long)G.GetRunPresentationEpoch());
  if(!Scope.IsEmpty()&&Scope!=S){++ScopeChanges;LastFact=LastRequest=0;}Scope=S;
  auto O=MakeShared<FJsonObject>();O->SetStringField(TEXT("scope"),Scope);O->SetNumberField(TEXT("callback_index"),Callback);O->SetNumberField(TEXT("first_seen_wall_min_s"),PreviousWall>0.?PreviousWall-Start:0.);O->SetNumberField(TEXT("first_seen_wall_max_s"),Wall-Start);O->SetNumberField(TEXT("observed_sim"),G.GetSimulationTime());
  TArray<JV> NewFacts,NewRequests;
  for(const auto& R:G.GetActionAudioState().Records)if(R.Sequence>LastFact){FactGaps+=R.Sequence-LastFact-1;auto F=Fact(R);F->SetNumberField(TEXT("first_seen_callback"),Callback);F->SetNumberField(TEXT("first_seen_wall_min_s"),PreviousWall>0.?PreviousWall-Start:0.);F->SetNumberField(TEXT("first_seen_wall_max_s"),Wall-Start);F->SetNumberField(TEXT("observed_sim"),G.GetSimulationTime());NewFacts.Add(MakeShared<FJsonValueObject>(F));Facts.Add(MakeShared<FJsonValueObject>(F));LastFact=R.Sequence;}
  for(const auto& R:H.GetActionAudioPlayReceipts())if(R.Source.Sequence>LastRequest){auto Q=MakeShared<FJsonObject>();Q->SetObjectField(TEXT("source"),Fact(R.Source));Q->SetStringField(TEXT("sound_path"),R.SoundPath);Q->SetNumberField(TEXT("requested_at"),R.RequestedAt);Q->SetNumberField(TEXT("volume"),R.Volume);Q->SetNumberField(TEXT("pitch"),R.Pitch);Q->SetNumberField(TEXT("first_seen_callback"),Callback);Q->SetNumberField(TEXT("first_seen_wall_min_s"),PreviousWall>0.?PreviousWall-Start:0.);Q->SetNumberField(TEXT("first_seen_wall_max_s"),Wall-Start);NewRequests.Add(MakeShared<FJsonValueObject>(Q));Requests.Add(MakeShared<FJsonValueObject>(Q));LastRequest=R.Source.Sequence;}
  O->SetArrayField(TEXT("new_facts"),NewFacts);O->SetArrayField(TEXT("new_requests"),NewRequests);O->SetNumberField(TEXT("fact_snapshot_count"),G.GetActionAudioState().Records.Num());O->SetNumberField(TEXT("request_snapshot_count"),H.GetActionAudioPlayReceipts().Num());PreviousWall=Wall;return O;
 }
 JO Final()const{auto O=MakeShared<FJsonObject>();O->SetStringField(TEXT("schema"),TEXT("swd-forward-step-action-audio-observation-v001"));O->SetArrayField(TEXT("facts"),Facts);O->SetArrayField(TEXT("requests"),Requests);O->SetNumberField(TEXT("scope_changes"),ScopeChanges);O->SetNumberField(TEXT("fact_sequence_gaps"),double(FactGaps));O->SetBoolField(TEXT("request_only"),true);O->SetBoolField(TEXT("source_epoch_available"),false);O->SetBoolField(TEXT("device_onset_measured"),false);return O;}
};
}

#include "DungeonFairytaleSwordSecondaryDrawStateV001.h"
namespace DungeonSwdForwardStepObservationV001 {
inline JO Point(DungeonFairytaleSwordSecondaryV001::FPoint V){auto O=MakeShared<FJsonObject>();O->SetNumberField(TEXT("x"),V.X);O->SetNumberField(TEXT("y"),V.Y);return O;}
inline JO Secondary(const ADungeonHUD& H){
 const auto& D=H.GetFairytaleSwordSecondaryDraw();auto O=MakeShared<FJsonObject>();
 Id(O,TEXT("draw_id"),D.DrawId);Id(O,TEXT("player_entity_id"),D.PlayerEntityId);
 O->SetBoolField(TEXT("opt_in"),D.OptIn);O->SetBoolField(TEXT("owns_branch"),D.OwnsBranch);O->SetBoolField(TEXT("profile_ready"),D.ProfileReady);O->SetBoolField(TEXT("atomic_preflight_ready"),D.AtomicPreflightReady);O->SetBoolField(TEXT("drawn"),D.Drawn);O->SetStringField(TEXT("missing_reason"),D.MissingReason);O->SetStringField(TEXT("profile_id"),D.ProfileId);O->SetStringField(TEXT("source_contract_sha256"),D.SourceContractSha256);
 auto S=MakeShared<FJsonObject>();S->SetObjectField(TEXT("action"),Action(D.Sample.Action,D.Sample.SampleTime));S->SetNumberField(TEXT("decision"),int32(D.Sample.Decision));S->SetNumberField(TEXT("reason"),int32(D.Sample.Reason));S->SetNumberField(TEXT("frame"),D.Sample.Frame);S->SetNumberField(TEXT("facing"),D.Sample.Facing);TArray<JV> Times;for(double T:D.Sample.Boundaries)Times.Add(MakeShared<FJsonValueNumber>(T));S->SetArrayField(TEXT("boundaries"),Times);O->SetObjectField(TEXT("sample"),S);
 const auto& B=D.Binding;auto Binding=MakeShared<FJsonObject>();Binding->SetStringField(TEXT("run"),B.RunGuid.ToString(EGuidFormats::Digits));Id(Binding,TEXT("owner"),B.OwnerId);Id(Binding,TEXT("revision"),B.Revision);Binding->SetNumberField(TEXT("active_slot"),B.ActiveSlot);Id(Binding,TEXT("weapon_instance"),B.WeaponInstanceId);Id(Binding,TEXT("weapon_version"),B.WeaponVersion);Id(Binding,TEXT("armor_instance"),B.ArmorInstanceId);Id(Binding,TEXT("armor_version"),B.ArmorVersion);Binding->SetStringField(TEXT("weapon_content"),B.WeaponContentId);Binding->SetStringField(TEXT("armor_content"),B.ArmorContentId);Binding->SetNumberField(TEXT("armor"),int32(B.Armor));O->SetObjectField(TEXT("binding"),Binding);
 auto G=MakeShared<FJsonObject>();G->SetObjectField(TEXT("ground_screen"),Point(D.Context.GroundScreen));G->SetNumberField(TEXT("ui_scale"),D.Context.UIScale);G->SetObjectField(TEXT("body_top"),Point(D.Geometry.BodyTop));G->SetObjectField(TEXT("grip_screen"),Point(D.Geometry.GripScreen));G->SetObjectField(TEXT("sword_top"),Point(D.Geometry.SwordTop));G->SetObjectField(TEXT("sword_pivot"),Point(D.Geometry.SwordPivot));G->SetNumberField(TEXT("body_width"),D.Geometry.BodyWidth);G->SetNumberField(TEXT("sword_width"),D.Geometry.SwordWidth);G->SetNumberField(TEXT("angle"),D.Geometry.Angle);G->SetNumberField(TEXT("u"),D.Geometry.U);G->SetNumberField(TEXT("du"),D.Geometry.DU);O->SetObjectField(TEXT("geometry"),G);
 O->SetNumberField(TEXT("expected_draw_count"),D.ExpectedDrawCount);TArray<JV> Stack,Slots,Resident;
 for(const auto& P:D.ActualRenderedStack)Stack.Add(MakeShared<FJsonValueString>(P));O->SetArrayField(TEXT("actual_stack"),Stack);
 for(const auto& T:D.ResidentTextures){auto X=MakeShared<FJsonObject>();X->SetStringField(TEXT("texture"),T.TexturePath);X->SetStringField(TEXT("class"),T.ClassName);X->SetNumberField(TEXT("width"),T.Width);X->SetNumberField(TEXT("height"),T.Height);X->SetBoolField(TEXT("ready"),T.Ready);X->SetBoolField(TEXT("pending_initialization"),T.PendingInitialization);Resident.Add(MakeShared<FJsonValueObject>(X));}O->SetArrayField(TEXT("residents"),Resident);
 for(const auto& T:D.Slots){auto X=MakeShared<FJsonObject>();X->SetNumberField(TEXT("slot"),T.SlotIndex);X->SetNumberField(TEXT("component"),int32(T.Component));X->SetStringField(TEXT("texture"),T.TexturePath);X->SetBoolField(TEXT("selected"),T.Selected);X->SetBoolField(TEXT("texture_ready"),T.TextureReady);X->SetBoolField(TEXT("drawn"),T.Drawn);X->SetArrayField(TEXT("top"),XY(T.Top));X->SetArrayField(TEXT("size"),XY(T.Size));X->SetArrayField(TEXT("uv"),XY(T.UV));X->SetArrayField(TEXT("uv_size"),XY(T.UVSize));X->SetNumberField(TEXT("rotation"),T.RotationDegrees);X->SetArrayField(TEXT("rotation_pivot"),XY(T.RotationPivot));X->SetNumberField(TEXT("draw_scale"),T.DrawScale);X->SetBoolField(TEXT("scale_position"),T.ScalePosition);TArray<JV> Tint;for(double V:{double(T.Tint.R),double(T.Tint.G),double(T.Tint.B),double(T.Tint.A)})Tint.Add(MakeShared<FJsonValueNumber>(V));X->SetArrayField(TEXT("tint"),Tint);Slots.Add(MakeShared<FJsonValueObject>(X));}O->SetArrayField(TEXT("slots"),Slots);return O;
}
}

namespace {using namespace DungeonSwdForwardStepObservationV001;
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

JO Equipment(const FDungeonEquipmentView& V){auto O=MakeShared<FJsonObject>();const auto& A=V.Action;O->SetBoolField(TEXT("active"),A.Active);O->SetNumberField(TEXT("kind"),int32(A.Kind));Id(O,TEXT("action_id"),A.ActionId);Id(O,TEXT("operation_id"),A.OperationId);Id(O,TEXT("source_id"),A.SourceId);Id(O,TEXT("instance_id"),A.InstanceId);O->SetNumberField(TEXT("slot"),A.Slot);O->SetNumberField(TEXT("start"),A.Start);O->SetNumberField(TEXT("deadline"),A.Deadline);Id(O,TEXT("selected_source"),V.SelectedSourceId);Id(O,TEXT("armor_instance"),V.Slots[2].InstanceId);Id(O,TEXT("armor_version"),V.Slots[2].Version);return O;}
JO CommonDraw(const FDungeonFairytaleSwordDraw& D){auto O=MakeShared<FJsonObject>();Id(O,TEXT("draw_id"),D.DrawId);O->SetNumberField(TEXT("sim"),D.SimulationTime);O->SetStringField(TEXT("clip"),D.Clip);O->SetNumberField(TEXT("frame"),D.Frame);O->SetNumberField(TEXT("facing"),D.Facing);O->SetBoolField(TEXT("supported"),D.Supported);O->SetBoolField(TEXT("active"),D.Active);O->SetBoolField(TEXT("gear_placeholder"),D.GearPlaceholder);TArray<JV> A;for(const auto& T:D.DrawStack)A.Add(MakeShared<FJsonValueString>(T));O->SetArrayField(TEXT("actual_stack"),A);return O;}
}
struct FDungeonSwdForwardStepProofV001 {
 using JO=TSharedPtr<FJsonObject>;using JV=TSharedPtr<FJsonValue>;
 FString Directory,Case,Failure,PreregFile;JO Prereg,Route;TWeakObjectPtr<ADungeonGameMode> G;TWeakObjectPtr<APlayerController>C;TWeakObjectPtr<ADungeonHUD>H;
 TArray<JV> Inputs,Observations,Offsets,StartupTextures;DungeonSwdForwardStepObservationV001::FCursor Audio;
 TArray<TStrongObjectPtr<UTexture2D>> Loaded;
 TMap<FKey,bool> Keys;FKey PulseKey;double ReleaseAt=0,NeutralUntil=0,Warm=0,Start=0,Stop=0,ReadStop=0,PhaseWall=0,AcceptedSampleTime=0,LockedSampleTime=0;
 int32 Phase=0,Waypoint=0,Frames=0,ReadyBefore=0,ReadyAfter=0,Mask=0,Facing=0,StillFrames=0;FVector2D PreviousPosition=FVector2D::ZeroVector;
 uint64 Sword=0,SwordVersion=0,SwordObservedVersion=0,Light=0,LightSource=0,LightVersion=0,Owner=0,Room=0,Epoch=0,Restart=0,ActionId=0;FGuid Run;
 DungeonWeaponActions::FAction Accepted,LockedSnapshot;bool PrewarmRequested=false,PrewarmDone=false,AudioRequested=false,Capturing=false,Stopping=false,Stopped=false,ReadComplete=false,Claimed=false,FlowComplete=false,EIssued=false,KIssued=false,LockedCaptured=false;
 bool Need(bool B,const FString& Why){if(!B&&Failure.IsEmpty())Failure=Why;return B;}
 void Next(int32 V){Phase=V;PhaseWall=FPlatformTime::Seconds();}
 void Key(FKey K,bool Down){if(Keys.FindRef(K)==Down)return;auto PC=C.Get();if(!PC)return;auto P=G.IsValid()?G->GetPlayerFighter():nullptr;auto O=MakeShared<FJsonObject>();O->SetStringField(TEXT("key"),K.GetFName().ToString());O->SetBoolField(TEXT("down"),Down);O->SetNumberField(TEXT("wall_offset_s"),FPlatformTime::Seconds()-Start);O->SetNumberField(TEXT("sim"),G->GetSimulationTime());if(P){O->SetObjectField(TEXT("action_before_input_queue"),DungeonSwdForwardStepObservationV001::Action(P->GetWeaponSkillAction(),P->GetWeaponSkillTime()));O->SetArrayField(TEXT("ground_before_input_queue"),DungeonSwdForwardStepObservationV001::XY(P->GetGroundPosition()));}PC->InputKey(FInputKeyParams(K,Down?IE_Pressed:IE_Released,Down?1.:0.));Keys.Add(K,Down);O->SetBoolField(TEXT("InputKey_is_queued_not_action_commit"),true);Inputs.Add(MakeShared<FJsonValueObject>(O));}
 bool CanPulse()const{return !PulseKey.IsValid()&&FPlatformTime::Seconds()>=NeutralUntil;}
 bool Pulse(FKey K){if(!CanPulse())return false;Key(K,true);PulseKey=K;ReleaseAt=FPlatformTime::Seconds()+.04;return true;}
 void Move(int32 X,int32 Y){Key(EKeys::A,X<0);Key(EKeys::D,X>0);Key(EKeys::S,Y<0);Key(EKeys::W,Y>0);}
 void Release(){Move(0,0);TArray<FKey> Held;Keys.GetKeys(Held);for(FKey K:Held)Key(K,false);PulseKey=FKey();}
 bool Scope(const ADungeonFighter& P){const auto& V=G->GetEquipmentView();return Need(V.Bound&&V.RunGuid==Run&&V.OwnerId==Owner&&V.RoomInstanceId==Room&&P.GetRuntimeEntityId()==Owner&&G->GetRunPresentationEpoch()==Epoch&&G->GetRunRestartSerial()==Restart,TEXT("Actual run/room/owner/epoch/restart changed"));}
 bool Gear(const ADungeonFighter& P){DungeonFairytaleSwordEquipmentBinding::FBinding B;FString Why;if(!DungeonFairytaleSwordEquipmentBinding::Resolve(*G.Get(),P,B,Why))return Need(false,TEXT("Committed SWD/LGT resolve failed: ")+Why);if(!LightVersion)LightVersion=B.ArmorVersion;
  if(B.WeaponVersion!=SwordObservedVersion){const auto* I=G->GetEquipmentInventoryState();bool Legal=false;if(I&&ActionId&&LockedCaptured&&B.WeaponVersion==SwordObservedVersion+1&&SwordObservedVersion==SwordVersion)for(const auto& R:I->RuntimeUpdates)if(R.InstanceId==Sword&&R.BeforeVersion==SwordObservedVersion&&R.AfterVersion==B.WeaponVersion&&R.AtTime>=Accepted.LockAt&&R.AtTime<=G->GetSimulationTime()&&R.BeforeAmmo==R.Ammo&&R.SkillCooldownDeadline==LockedSnapshot.LockAt+LockedSnapshot.CooldownDuration&&R.Result.Ok()&&!R.Result.Replayed)Legal=true;if(!Need(Legal,TEXT("Weapon version changed without actual single K cooldown runtime receipt")))return false;SwordObservedVersion=B.WeaponVersion;}
  return Need(B.WeaponContentId==TEXT("WPN-SWD-001")&&B.WeaponInstanceId==Sword&&B.WeaponVersion==SwordObservedVersion&&B.Armor==DungeonFairytaleSwordEquipmentBinding::EArmor::LightArmor&&B.ArmorInstanceId==Light&&B.ArmorVersion==LightVersion,TEXT("Actual SWD/LGT identity or armor version changed"));}
 JO RuntimeInventory()const{auto O=MakeShared<FJsonObject>();const auto* I=G->GetEquipmentInventoryState();O->SetBoolField(TEXT("available"),I!=nullptr);TArray<JV> Rows;if(I)for(const auto& R:I->RuntimeUpdates){auto X=MakeShared<FJsonObject>();DungeonSwdForwardStepObservationV001::Id(X,TEXT("receipt_id"),R.ReceiptId);DungeonSwdForwardStepObservationV001::Id(X,TEXT("instance_id"),R.InstanceId);DungeonSwdForwardStepObservationV001::Id(X,TEXT("before_version"),R.BeforeVersion);DungeonSwdForwardStepObservationV001::Id(X,TEXT("after_version"),R.AfterVersion);DungeonSwdForwardStepObservationV001::Id(X,TEXT("base_revision"),R.BaseRevision);X->SetNumberField(TEXT("at_time"),R.AtTime);X->SetNumberField(TEXT("before_ammo"),R.BeforeAmmo);X->SetNumberField(TEXT("ammo"),R.Ammo);X->SetNumberField(TEXT("before_cooldown"),R.BeforeCooldown);X->SetNumberField(TEXT("cooldown_deadline"),R.SkillCooldownDeadline);X->SetBoolField(TEXT("ok"),R.Result.Ok());X->SetBoolField(TEXT("replayed"),R.Result.Replayed);Rows.Add(MakeShared<FJsonValueObject>(X));}O->SetArrayField(TEXT("runtime_updates"),Rows);return O;}
 bool Readback(){
  if(!Need(!Capturing&&!AudioRequested&&GIsDumpingMovie==0,TEXT("Pre-audio/pre-input readback required")))return false;
  const auto& Pins=Prereg->GetArrayField(TEXT("resource_pins"));if(!Need(Pins.Num()==81,TEXT("Actual K57 + retained Ready24 resources required")))return false;
  TArray<UTexture*> Targets;for(const auto& V:Pins){auto Pin=V->AsObject();const FString Path=Pin->GetStringField(TEXT("texture"));Loaded.Emplace(LoadObject<UTexture2D>(nullptr,*Path));if(Loaded.Last().Get())Targets.Add(Loaded.Last().Get());}
#if WITH_EDITOR
  FTextureCompilingManager::Get().FinishCompilation(Targets);
#endif
  FlushRenderingCommands();IFileManager::Get().MakeDirectory(*(Directory/TEXT("texture-readback")),false);TSet<FString>Unique;
const auto Capture=[&](const FString& Path,const FString& PNGSHA,const FString& RGBASHA,int32 Frame,int32 Component)
  {
   UTexture2D* T=FindObject<UTexture2D>(nullptr,*Path);
   if(!Need(!Unique.Contains(Path)&&T&&T->GetClass()==UTexture2D::StaticClass()&&T->GetPathName()==Path&&T->GetSizeX()==512&&T->GetSizeY()==512&&T->GetResource()&&!T->HasPendingRenderResourceInitialization(),TEXT("All requested exact preloaded Texture2D512 resources required before normal input")))return false;
   Unique.Add(Path);const FTextureRHIRef RHI=T->GetResource()->TextureRHI;
   if(!Need(RHI.IsValid()&&RHI->GetDesc().Extent==FIntPoint(512,512)&&(RHI->GetFormat()==PF_B8G8R8A8||RHI->GetFormat()==PF_R8G8B8A8),TEXT("GPU readback requires actual uncompressed BGRA8/RGBA8 mip0 512; no lossy fallback")))return false;
   TArray<FColor> GPU;const double ReadStart=FPlatformTime::Seconds();
   ENQUEUE_RENDER_COMMAND(SwdForwardStepOriginalGPUReadback)([RHI,&GPU](FRHICommandListImmediate& Cmd)
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
  
  for(const auto& V:Pins){auto Pin=V->AsObject();if(!Capture(Pin->GetStringField(TEXT("texture")),Pin->GetStringField(TEXT("sha256")),Pin->GetStringField(TEXT("rgba_sha256")),int32(Pin->GetNumberField(TEXT("frame"))),int32(Pin->GetNumberField(TEXT("component")))))return false;}
  ReadStop=FPlatformTime::Seconds();ReadComplete=Need(StartupTextures.Num()==81&&Unique.Num()==81,TEXT("Full distinct K57/Ready24 original readback incomplete"));return ReadComplete;
 }
 void StopNow(ADungeonSwdForwardStepProbeV001& A){if(Stopping||Stopped)return;Stopping=true;Capturing=false;GIsDumpingMovie=0;Release();if(A.MainMix){if(A.MainMix->Status().Phase==EDungeonNativeMixCapturePhaseV001::Recording)A.MainMix->Stop();else if(!A.MainMix->IsTerminal()&&A.MainMix->Status().Phase!=EDungeonNativeMixCapturePhaseV001::ExportPending)A.MainMix->Abort(Failure.IsEmpty()?TEXT("Observer stop before recording"):Failure);Stop=A.MainMix->Status().StopMonotonic;}if(Stop<=0.)Stop=FPlatformTime::Seconds();}
 void Observe(ADungeonSwdForwardStepProbeV001& A){
  if(Stopped||Stopping)return;if(PrewarmRequested&&!PrewarmDone){PrewarmDone=Need(IFileManager::Get().FileSize(*(Directory/TEXT("prewarm-viewport.png")))>8,TEXT("Prewarm callback without original PNG"));return;}if(!Capturing)return;
  auto P=G.IsValid()?G->GetPlayerFighter():nullptr;if(!Need(P&&H.IsValid(),TEXT("Completed native callback lost owner"))||!Scope(*P)){StopNow(A);return;}
  const auto& Skill=P->GetWeaponSkillAction();const auto& Draw=H->GetFairytaleSwordSecondaryDraw();const auto& B=H->GetFairytaleSwordDraw();const double Sim=G->GetSimulationTime(),Wall=FPlatformTime::Seconds()-Start;
  auto O=MakeShared<FJsonObject>();O->SetNumberField(TEXT("callback_index"),Frames);O->SetNumberField(TEXT("wall_offset_s"),Wall);O->SetNumberField(TEXT("sim"),Sim);O->SetObjectField(TEXT("action"),DungeonSwdForwardStepObservationV001::Action(Skill,P->GetWeaponSkillTime()));O->SetArrayField(TEXT("ground"),DungeonSwdForwardStepObservationV001::XY(P->GetGroundPosition()));O->SetNumberField(TEXT("height"),P->JumpHeight);O->SetNumberField(TEXT("vertical_velocity"),P->GetVerticalVelocity());O->SetBoolField(TEXT("melee_grounded"),P->GetMeleeCombatState().Grounded);O->SetBoolField(TEXT("weapon_grounded"),P->GetWeaponActionsState().Budget.Grounded);O->SetObjectField(TEXT("equipment_action"),Equipment(G->GetEquipmentView()));O->SetObjectField(TEXT("runtime_inventory"),RuntimeInventory());O->SetObjectField(TEXT("secondary"),DungeonSwdForwardStepObservationV001::Secondary(*H.Get()));O->SetObjectField(TEXT("common_draw"),CommonDraw(B));O->SetObjectField(TEXT("action_audio_poll"),Audio.Observe(*G.Get(),*P,*H.Get(),Frames,Start));
  auto W=MakeShared<FJsonObject>();W->SetBoolField(TEXT("available"),false);W->SetStringField(TEXT("reason"),TEXT("positive DTO is not an independent zero-placement commit reader"));O->SetObjectField(TEXT("zero_placement_witness"),W);
  Observations.Add(MakeShared<FJsonValueObject>(O));Offsets.Add(MakeShared<FJsonValueNumber>(Wall));++Frames;
  const bool Ready=B.Active&&B.Supported&&!B.GearPlaceholder&&B.Clip==TEXT("sword_ready_idle")&&!Draw.Drawn;
  if(Phase==4&&Ready&&!Skill.Active&&Gear(*P))++ReadyBefore;
  if(KIssued&&Skill.Active&&Skill.Type==DungeonWeaponActions::EAction::Skill&&Skill.Weapon==DungeonContentCombat::EWeapon::SWD001){
   if(!ActionId){Accepted=Skill;AcceptedSampleTime=P->GetWeaponSkillTime();ActionId=Skill.ActionId;Need(ActionId>0&&Skill.InstanceId==Sword&&!Skill.StartedAirborne,TEXT("Normal K did not create actual grounded SWD action"));}
   if(Skill.Locked&&!LockedCaptured){LockedSnapshot=Skill;LockedSampleTime=P->GetWeaponSkillTime();LockedCaptured=true;}
   if(!Need(Skill.ActionId==ActionId&&Skill.InstanceId==Accepted.InstanceId&&Skill.Start==Accepted.Start&&Skill.LockAt==Accepted.LockAt&&Skill.ActiveAt==Accepted.ActiveAt&&Skill.ActiveEnd==Accepted.ActiveEnd&&Skill.End==Accepted.End,TEXT("K action identity/deadlines changed"))||!Gear(*P))return;
   if(!Need(Draw.Drawn&&Draw.AtomicPreflightReady&&Draw.ProfileReady&&Draw.Sample.Action.ActionId==ActionId&&Draw.Sample.Action.InstanceId==Sword&&Draw.Sample.SampleTime==Sim&&Draw.Sample.Frame>=0&&Draw.Sample.Frame<8&&Draw.ExpectedDrawCount==8&&B.Clip==TEXT("sword_secondary"),TEXT("Actual same-draw K8 trace missing/stale")))return;Mask|=1<<Draw.Sample.Frame;
  }
  if(ActionId&&!Skill.Active&&Sim>=Accepted.End&&Ready){++ReadyAfter;if(ReadyAfter>=2){FlowComplete=Need(Mask==255&&ReadyBefore>=3,TEXT("K8 or actual Ready entry/End join missing"));StopNow(A);}}
 }
 void Finalize(ADungeonSwdForwardStepProbeV001& A){if(Stopped)return;Stopped=true;GIsDumpingMovie=0;Release();const bool Flushed=FlushFastLosslessProofScreenshots(),Mix=A.MainMix&&A.MainMix->Status().Phase==EDungeonNativeMixCapturePhaseV001::Complete;auto R=MakeShared<FJsonObject>();R->SetStringField(TEXT("schema"),TEXT("swd-forward-step-native-observer-v001"));R->SetStringField(TEXT("case"),Case);R->SetStringField(TEXT("failure"),Failure);R->SetBoolField(TEXT("passed"),Failure.IsEmpty()&&FlowComplete&&Flushed&&Mix&&ReadComplete);R->SetBoolField(TEXT("flow_complete"),FlowComplete);R->SetBoolField(TEXT("formal_accepted"),false);R->SetBoolField(TEXT("audio_listened"),false);R->SetBoolField(TEXT("device_onset_measured"),false);R->SetBoolField(TEXT("player_enemy_HP_position_AI_clock_writes"),false);R->SetBoolField(TEXT("enemy_diagnostic_used"),false);R->SetStringField(TEXT("QA_source_boundary"),TEXT("one display ARM-LGT-001 registered at actual player position; normal E commits; no lawful acquisition claim"));Id(R,TEXT("process_id"),FPlatformProcess::GetCurrentProcessId());R->SetStringField(TEXT("run"),Run.ToString(EGuidFormats::Digits));Id(R,TEXT("room"),Room);Id(R,TEXT("owner"),Owner);Id(R,TEXT("epoch"),Epoch);Id(R,TEXT("restart"),Restart);Id(R,TEXT("weapon_instance"),Sword);Id(R,TEXT("weapon_version"),SwordVersion);Id(R,TEXT("weapon_version_end"),SwordObservedVersion);Id(R,TEXT("armor_instance"),Light);Id(R,TEXT("light_source"),LightSource);Id(R,TEXT("armor_version"),LightVersion);R->SetNumberField(TEXT("requested_facing"),Facing);R->SetNumberField(TEXT("secondary_frame_mask"),Mask);R->SetNumberField(TEXT("ready_before_frames"),ReadyBefore);R->SetNumberField(TEXT("ready_after_frames"),ReadyAfter);R->SetObjectField(TEXT("accepted_action"),DungeonSwdForwardStepObservationV001::Action(Accepted,AcceptedSampleTime));R->SetObjectField(TEXT("locked_action_source"),DungeonSwdForwardStepObservationV001::Action(LockedSnapshot,LockedSampleTime));R->SetArrayField(TEXT("normal_inputs"),Inputs);R->SetArrayField(TEXT("observations"),Observations);R->SetObjectField(TEXT("action_audio"),Audio.Final());R->SetArrayField(TEXT("startup_resource_readbacks"),StartupTextures);R->SetBoolField(TEXT("startup_readback_complete"),ReadComplete);R->SetNumberField(TEXT("startup_readback_stop_monotonic_s"),ReadStop);R->SetBoolField(TEXT("native_async_capture_requested"),FParse::Param(FCommandLine::Get(),TEXT("DungeonAsyncLosslessCapture")));R->SetBoolField(TEXT("native_async_capture_writes_flushed"),Flushed);R->SetBoolField(TEXT("native_async_flush_after_audio_stop"),Mix&&Stop>0.);auto T=MakeShared<FJsonObject>();T->SetBoolField(TEXT("use_fixed_time_step"),FApp::UseFixedTimeStep());T->SetNumberField(TEXT("capture_start_monotonic_s"),Start);T->SetNumberField(TEXT("capture_stop_monotonic_s"),Stop);T->SetArrayField(TEXT("frame_wall_offsets_s"),Offsets);R->SetObjectField(TEXT("capture_timing"),T);if(A.MainMix)R->SetObjectField(TEXT("main_submix_capture"),A.MainMix->SerializeReport());FString Text;auto Writer=TJsonWriterFactory<>::Create(&Text);const bool W=FJsonSerializer::Serialize(R,Writer)&&Claimed&&WriteNewUTF8(Directory/TEXT("runtime-report.json"),Text);FPlatformMisc::RequestExitWithStatus(false,Failure.IsEmpty()&&FlowComplete&&Flushed&&Mix&&W?0:3);}
 void Tick(ADungeonSwdForwardStepProbeV001& A){
  if(Stopped)return;const double Now=FPlatformTime::Seconds();if(A.MainMix)A.MainMix->Poll();if(Stopping){if(!A.MainMix||A.MainMix->IsTerminal())Finalize(A);return;}if(!Failure.IsEmpty()){StopNow(A);return;}
  auto Game=A.GetWorld()?A.GetWorld()->GetAuthGameMode<ADungeonGameMode>():nullptr;auto PC=UGameplayStatics::GetPlayerController(&A,0);auto HUD=PC?Cast<ADungeonHUD>(PC->GetHUD()):nullptr;
  if(!G.IsValid()&&Game&&PC&&PC->PlayerInput&&HUD){auto P=Game->GetPlayerFighter();const auto& V=Game->GetEquipmentView();if(!P||!V.Bound||!V.RunGuid.IsValid()||V.ActiveSlot<0||V.ActiveSlot>=3)return;G=Game;C=PC;H=HUD;Run=V.RunGuid;Owner=V.OwnerId;Room=V.RoomInstanceId;Epoch=Game->GetRunPresentationEpoch();Restart=Game->GetRunRestartSerial();Sword=V.Slots[V.ActiveSlot].InstanceId;SwordVersion=V.Slots[V.ActiveSlot].Version;SwordObservedVersion=SwordVersion;A.AddTickPrerequisiteActor(Game);A.AddTickPrerequisiteActor(HUD);return;}
  if(!G.IsValid()){if(Now-Warm>12.)Need(false,TEXT("Startup owner timeout"));return;}
  if(PulseKey.IsValid()&&Now>=ReleaseAt){Key(PulseKey,false);PulseKey=FKey();NeutralUntil=Now+.04;}
  if(!Capturing){if(!ReadComplete){Readback();return;}if(!PrewarmRequested){PrewarmRequested=true;FScreenshotRequest::RequestScreenshot(Directory/TEXT("prewarm-viewport.png"),false,false,false);}if(PrewarmDone&&!AudioRequested){AudioRequested=true;A.MainMix=NewObject<UDungeonNativeMainSubmixCaptureV001>(&A);if(!A.MainMix->Begin(A.GetWorld(),Directory/TEXT("audio-v001")))Need(false,TEXT("Native mix arming rejected"));}if(AudioRequested&&A.MainMix&&A.MainMix->Status().Phase==EDungeonNativeMixCapturePhaseV001::Recording){Start=A.MainMix->Status().StartMonotonic;Capturing=Need(Start>ReadStop,TEXT("Invalid recording origin"));GIsDumpingMovie=-1;Next(0);}if(Now-Warm>45.)Need(false,TEXT("Readback/prewarm/audio timeout"));return;}
  auto P=Game?Game->GetPlayerFighter():nullptr;if(!Need(P&&Game==G.Get()&&PC==C.Get()&&HUD==H.Get()&&PC->GetPawn()==P&&PC->IsLocalController()&&Now-Start<45.&&Now-PhaseWall<12.,TEXT("Native owner/phase timeout"))||!Scope(*P))return;
  switch(Phase){
   case 0:if(!Need(G->bWaitingForStart&&G->GetSimulationTime()==0.,TEXT("Fresh run must await actual Enter")))return;if(Pulse(EKeys::Enter))Next(1);break;
   case 1:if(!G->bWaitingForStart&&CanPulse()){DungeonEquipmentInventory::FItem I;I.ContentId="ARM-LGT-001";const auto R=G->RegisterEquipmentSource(TEXT("display.swd.forward.step.light.v001"),I,P->GetGroundPosition()+FVector2D(24.,0.),true);if(!Need(R.Ok()&&!R.Replayed,TEXT("QA display LGT source rejected")))return;Light=R.InstanceId;LightSource=R.SourceId;Next(2);}break;
   case 2:if(!EIssued){if(CanPulse()&&G->GetEquipmentView().SelectedSourceId==LightSource&&Pulse(EKeys::E))EIssued=true;}else if(!G->GetEquipmentView().Action.Active&&G->GetEquipmentView().Slots[2].InstanceId==Light&&Gear(*P)&&CanPulse())Next(3);break;
   case 3:{const auto& Waypoints=Route->GetArrayField(TEXT("waypoints"));if(Waypoint>=Waypoints.Num()){Move(0,0);if(CanPulse()){if(P->Facing==float(Facing))Next(4);else if(Pulse(Facing<0?EKeys::A:EKeys::D))Next(4);}break;}const auto W=Waypoints[Waypoint]->AsObject();const auto& XY=W->GetArrayField(TEXT("xy"));const FVector2D Goal(XY[0]->AsNumber(),XY[1]->AsNumber()),At=P->GetGroundPosition(),Delta=Goal-At;const double Tol=W->GetNumberField(TEXT("tolerance_cm"));StillFrames=At.Equals(PreviousPosition,.0001)?StillFrames+1:0;PreviousPosition=At;const bool Contact=W->GetBoolField(TEXT("allow_blocked_contact"))&&StillFrames>=4&&Delta.Size()<20.;if((FMath::Abs(Delta.X)<=Tol&&FMath::Abs(Delta.Y)<=Tol)||Contact){Move(0,0);++Waypoint;StillFrames=0;}else Move(FMath::Abs(Delta.X)>Tol?(Delta.X>0?1:-1):0,FMath::Abs(Delta.Y)>Tol?(Delta.Y>0?1:-1):0);break;}
   case 4:if(CanPulse()&&P->Facing==float(Facing)&&ReadyBefore>=3&&P->CanStartAttack()&&Pulse(EKeys::K)){KIssued=true;Next(5);}break;
   case 5:break;default:Need(false,TEXT("Unexpected observer phase"));break;
  }
 }
};
void FDungeonSwdForwardStepProofDeleterV001::operator()(FDungeonSwdForwardStepProofV001* P)const{delete P;}
ADungeonSwdForwardStepProbeV001::ADungeonSwdForwardStepProbeV001(){PrimaryActorTick.bCanEverTick=true;}
ADungeonSwdForwardStepProbeV001::~ADungeonSwdForwardStepProbeV001()=default;
void ADungeonSwdForwardStepProbeV001::BeginPlay(){Super::BeginPlay();Proof.Reset(new FDungeonSwdForwardStepProofV001);auto& S=*Proof;S.Warm=FPlatformTime::Seconds();FParse::Value(FCommandLine::Get(),TEXT("DungeonContentProofDir="),S.Directory);FParse::Value(FCommandLine::Get(),TEXT("DungeonSwdForwardStepCase="),S.Case);FParse::Value(FCommandLine::Get(),TEXT("DungeonSwdForwardStepPrereg="),S.PreregFile);FString Text;if(!S.Need(FFileHelper::LoadFileToString(Text,*S.PreregFile)&&FJsonSerializer::Deserialize(TJsonReaderFactory<>::Create(Text),S.Prereg),TEXT("NotReady: actual prereg missing")))return;
 if(!S.Need(S.Prereg->GetBoolField(TEXT("ready"))&&DungeonFairytaleSwordSecondaryV001::Profile().RuntimeReady,TEXT("NotReady: K8 Profile or prereg not admitted")))return;
 S.Route=S.Prereg->GetObjectField(TEXT("cases"))->GetObjectField(S.Case);S.Facing=int32(S.Route->GetNumberField(TEXT("facing")));if(!S.Need((S.Facing==-1||S.Facing==1)&&S.Route->GetBoolField(TEXT("normal_route_native_verified")),TEXT("NotReady: exact normal input route unverified")))return;
 if(S.Case.StartsWith(TEXT("blocked_zero"))){S.Need(false,TEXT("NotReady: independent actual zero-placement commit reader not available"));return;}
 for(const TCHAR* Flag:{TEXT("DungeonSwdForwardStepProofV001"),TEXT("DungeonContentProof"),TEXT("DungeonFastLosslessCapture"),TEXT("DungeonAsyncLosslessCapture"),TEXT("DungeonCandidateSprites"),TEXT("DungeonFairytaleSwordEquipmentBoundPreview"),TEXT("DungeonFairytaleLeatherReadyPreview"),TEXT("DungeonFairytaleSwordSecondaryPreview")})if(!S.Need(FParse::Param(FCommandLine::Get(),Flag),TEXT("Missing required flag: ")+FString(Flag)))return;
 for(const TCHAR* Flag:{TEXT("DungeonProof"),TEXT("DungeonHeroAirProductionProofV001"),TEXT("DungeonHeroAirProofV001"),TEXT("DungeonHeroDodgeProofV001"),TEXT("DungeonHeroHurtProofV001"),TEXT("DungeonHeroDeathProofV001"),TEXT("DungeonGuardMoveProofV001"),TEXT("DungeonGuardStompProofV001"),TEXT("DungeonGuardArtCombatProofV003"),TEXT("DungeonGuardArtDeathProofV005"),TEXT("DungeonGuardArtKnown44Proof"),TEXT("DungeonGuardArtPartialProof"),TEXT("DungeonGuardRoomFlowProof"),TEXT("DungeonGuardRoomManualLightSource"),TEXT("DungeonFairytaleWalkProof"),TEXT("DungeonFairytaleEquipmentBoundProof"),TEXT("DungeonFairytaleSwordBodyProof"),TEXT("DungeonRunSaveProof"),TEXT("DungeonRunRestoreProof"),TEXT("DungeonGuardRunSaveProof"),TEXT("DungeonGuardRunRestoreProof"),TEXT("DungeonFairytaleLookdevProof"),TEXT("DungeonFairytaleLookdevPreview"),TEXT("DungeonCombatRangeDebug"),TEXT("DungeonCombatRangeProof"),TEXT("DungeonShowInterface"),TEXT("DungeonHeroAirDiskRestoreProofV001"),TEXT("DungeonHeroLandingPriorityProofV001"),TEXT("DungeonFirstUnitProof"),TEXT("DungeonFirstUnitSkillProof"),TEXT("DungeonFirstUnitExploreProof"),TEXT("DungeonEquipmentAdapterProof"),TEXT("DungeonSceneExplorationProof")})if(!S.Need(!FParse::Param(FCommandLine::Get(),Flag),TEXT("Other observer/HUD flag cannot share capture")))return;
 for(TActorIterator<ADungeonContentProbe> It(GetWorld());It;++It){S.Need(false,TEXT("Old ContentProbe cannot share actual recording"));return;}
 if(!S.Need(!FApp::UseFixedTimeStep()&&!S.Directory.IsEmpty()&&!FPaths::IsRelative(S.Directory),TEXT("Absolute unused directory and native variable pacing required")))return;IFileManager::Get().MakeDirectory(*S.Directory,true);TArray<FString> Files,Dirs;IFileManager::Get().FindFiles(Files,*(S.Directory/TEXT("*")),true,false);Files.Remove(TEXT("native-lossless-capture.json"));IFileManager::Get().FindFiles(Dirs,*(S.Directory/TEXT("*")),false,true);if(!S.Need(Files.IsEmpty()&&Dirs.IsEmpty(),TEXT("Evidence directory occupied")))return;S.Claimed=WriteNewUTF8(S.Directory/TEXT("observer-process-claim-v001.json"),FString::Printf(TEXT("{\"schema\":\"swd-forward-step-process-claim-v001\",\"process_id\":\"%u\"}"),FPlatformProcess::GetCurrentProcessId()));if(!S.Need(S.Claimed,TEXT("Exclusive process claim rejected")))return;GetMutableDefault<UEngine>()->GameScreenshotSaveDirectory.Path=S.Directory;FScreenshotRequest::OnScreenshotRequestProcessed().AddUObject(this,&ADungeonSwdForwardStepProbeV001::ScreenshotProcessed);
}
void ADungeonSwdForwardStepProbeV001::ScreenshotProcessed(){if(Proof)Proof->Observe(*this);}
void ADungeonSwdForwardStepProbeV001::Tick(float Delta){Super::Tick(Delta);if(Proof)Proof->Tick(*this);}
void ADungeonSwdForwardStepProbeV001::EndPlay(const EEndPlayReason::Type Reason){FScreenshotRequest::OnScreenshotRequestProcessed().RemoveAll(this);if(Proof&&!Proof->Stopped){Proof->Need(false,TEXT("World ended before capture/export complete"));if(MainMix&&!MainMix->IsTerminal())MainMix->Abort(TEXT("World ended before export"));Proof->StopNow(*this);Proof->Finalize(*this);}Super::EndPlay(Reason);}
