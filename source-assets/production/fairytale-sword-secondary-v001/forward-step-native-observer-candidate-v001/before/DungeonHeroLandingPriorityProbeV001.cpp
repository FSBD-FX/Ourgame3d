#include "DungeonHeroLandingPriorityProbeV001.h"
#include "DungeonGameMode.h"
#include "DungeonFighter.h"
#include "DungeonHUD.h"
#include "DungeonContentProbe.h"
#include "DungeonNativeMainSubmixCaptureV001.h"
#include "DungeonFairytaleSwordEquipmentBinding.h"
#include "DungeonFairytaleSwordAirV001.h"
#include "DungeonProofScreenshots.h"
#include "DungeonRoomLayout.h"
#include "Engine/Engine.h"
#include "UObject/StrongObjectPtr.h"
#include "Engine/Texture2D.h"
#include "TextureResource.h"
#if WITH_EDITOR
#include "TextureCompiler.h"
#endif
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

#include <array>
#include <cstdint>
#include <vector>
namespace DungeonHeroLocomotionObservationV001
{
struct FRequestScopeKey { std::array<std::uint64_t,8> Fields{}; };
class FRequestCursor
{
 struct FThrough {FRequestScopeKey Scope;std::uint64_t Sequence=0;};
 std::vector<FThrough> Through;
public:
 bool Observe(const FRequestScopeKey& Scope,std::uint64_t Sequence,std::uint64_t& Gap)
 {
  Gap=0;if(!Sequence)return false;
  for(auto& T:Through)if(T.Scope.Fields==Scope.Fields)
  {
   if(Sequence<=T.Sequence)return false;
   Gap=Sequence-T.Sequence-1;T.Sequence=Sequence;return true;
  }
  Through.push_back({Scope,Sequence});Gap=Sequence-1;return true;
 }
};
}

namespace DungeonHeroLocomotionObservationV001
{
using FAudioJO=TSharedPtr<FJsonObject>;using FAudioJV=TSharedPtr<FJsonValue>;
void AudioId(FAudioJO O,const TCHAR* Key,uint64 Value){O->SetStringField(Key,FString::Printf(TEXT("%llu"),Value));}
void AudioNull(FAudioJO O,const TCHAR* Key){O->SetField(Key,MakeShared<FJsonValueNull>());}
TArray<FAudioJV> AudioXY(FVector2D V){return {MakeShared<FJsonValueNumber>(V.X),MakeShared<FJsonValueNumber>(V.Y)};}
FAudioJO CurrentScope(const ADungeonGameMode& G,const ADungeonFighter& P)
{
 auto O=MakeShared<FJsonObject>();const auto& V=G.GetEquipmentView();O->SetStringField(TEXT("run"),V.RunGuid.ToString(EGuidFormats::Digits));AudioId(O,TEXT("owner"),P.GetRuntimeEntityId());AudioId(O,TEXT("room"),V.RoomInstanceId);AudioId(O,TEXT("epoch"),G.GetRunPresentationEpoch());AudioId(O,TEXT("restart"),G.GetRunRestartSerial());return O;
}
FAudioJO RequestScope(const DungeonHeroLocomotionAudioV001::FScope& S)
{
 auto O=MakeShared<FJsonObject>();AudioId(O,TEXT("owner"),S.Owner);AudioId(O,TEXT("room"),S.Room);AudioId(O,TEXT("epoch"),S.Epoch);AudioId(O,TEXT("restart"),S.Restart);O->SetBoolField(TEXT("run_available"),false);AudioNull(O,TEXT("run"));return O;
}
FRequestScopeKey RequestKey(FGuid Run,const DungeonHeroLocomotionAudioV001::FScope& S)
{return {{{Run.A,Run.B,Run.C,Run.D,S.Owner,S.Room,S.Restart,S.Epoch}}};}
FAudioJO GroundWitness(const ADungeonFighter& P)
{
 auto O=MakeShared<FJsonObject>();FDungeonCompletedGroundMotion M;const bool Available=P.QueryCompletedGroundMotion(M);O->SetBoolField(TEXT("available"),Available);O->SetStringField(TEXT("semantics"),TEXT("actual_completed_callback_motion_not_event_source_interval"));
 if(Available){O->SetStringField(TEXT("run"),M.RunGuid.ToString(EGuidFormats::Digits));AudioId(O,TEXT("owner"),M.OwnerId);AudioId(O,TEXT("room"),M.RoomInstanceId);O->SetNumberField(TEXT("from_time_s"),M.FromTime);O->SetNumberField(TEXT("to_time_s"),M.ToTime);O->SetArrayField(TEXT("from_xy"),AudioXY(M.From));O->SetArrayField(TEXT("to_xy"),AudioXY(M.To));O->SetNumberField(TEXT("accepted_distance_cm"),M.AcceptedDistance);O->SetNumberField(TEXT("walk_distance_cm"),M.WalkDistance);O->SetBoolField(TEXT("grounded"),M.Grounded);O->SetBoolField(TEXT("ordinary_eligible"),M.OrdinaryEligible);O->SetBoolField(TEXT("had_move_intent"),M.HadMoveIntent);}
 return O;
}
FAudioJO WallWindow(double Lower,double Upper,double Start)
{
 auto O=MakeShared<FJsonObject>();O->SetNumberField(TEXT("lower_monotonic_s"),Lower);O->SetNumberField(TEXT("upper_monotonic_s"),Upper);O->SetNumberField(TEXT("lower_offset_s"),Lower-Start);O->SetNumberField(TEXT("upper_offset_s"),Upper-Start);O->SetStringField(TEXT("semantics"),TEXT("first_seen_between_completed_callbacks_not_emission_timestamp"));return O;
}
FAudioJO RequestRow(const FDungeonHeroLocomotionAudioPlayRequestV001& R,int32 Callback,int32 Phase,double Sim,FAudioJO Window,FAudioJO Current)
{
 namespace A=DungeonHeroLocomotionAudioV001;const auto& E=R.Source;auto O=MakeShared<FJsonObject>();AudioId(O,TEXT("sequence"),E.Sequence);O->SetObjectField(TEXT("request_scope"),RequestScope(E.Scope));O->SetObjectField(TEXT("first_seen_current_scope"),Current);
 O->SetStringField(TEXT("cue"),R.Cue.ToString());O->SetNumberField(TEXT("cue_enum"),int32(E.Cue));O->SetStringField(TEXT("asset_path"),R.SoundPath);O->SetNumberField(TEXT("volume"),R.Volume);O->SetNumberField(TEXT("pitch"),R.Pitch);O->SetNumberField(TEXT("at_time_s"),E.AtTime);O->SetNumberField(TEXT("requested_at_time_s"),R.RequestedAt);O->SetArrayField(TEXT("ground_position_at_dispatch"),AudioXY(R.GroundPosition));
 O->SetNumberField(TEXT("first_seen_callback_index"),Callback);O->SetNumberField(TEXT("first_seen_phase"),Phase);O->SetNumberField(TEXT("first_seen_sim_time_s"),Sim);O->SetObjectField(TEXT("first_seen_wall_window"),Window);O->SetBoolField(TEXT("request_wall_time_available"),false);AudioNull(O,TEXT("request_monotonic_s"));
 const TCHAR* Cause=TEXT("unknown_existing_cue");switch(E.Cue){case A::ECue::StepLight01:case A::ECue::StepLight02:Cause=TEXT("ground_distance_threshold");break;case A::ECue::TakeoffLight01:Cause=TEXT("successful_takeoff");break;case A::ECue::LandLight01:case A::ECue::LandFirm01:Cause=TEXT("natural_landing");break;case A::ECue::DodgeShort01:Cause=TEXT("dodge_started");break;}
 O->SetStringField(TEXT("source_cause"),Cause);O->SetStringField(TEXT("source_cause_basis"),TEXT("mapped_existing_cue_enum_not_new_gameplay_event"));O->SetBoolField(TEXT("source_interval_available"),false);AudioNull(O,TEXT("source_from_time_s"));AudioNull(O,TEXT("source_to_time_s"));O->SetBoolField(TEXT("source_distance_available"),false);AudioNull(O,TEXT("source_distance_cm"));
 AudioId(O,TEXT("step_ordinal"),E.StepOrdinal);O->SetNumberField(TEXT("fall_speed_cm_s"),E.FallSpeed);O->SetNumberField(TEXT("fall_distance_cm"),E.FallDistance);AudioId(O,TEXT("dodge_event_id"),E.DodgeEventId);AudioId(O,TEXT("dodge_action_id"),E.DodgeActionId);O->SetBoolField(TEXT("event_id_available"),E.DodgeEventId!=0);if(E.DodgeEventId)AudioId(O,TEXT("event_id"),E.DodgeEventId);else AudioNull(O,TEXT("event_id"));
 const bool Landing=E.Cue==A::ECue::LandLight01||E.Cue==A::ECue::LandFirm01;O->SetBoolField(TEXT("landing_fields_applicable"),Landing);O->SetBoolField(TEXT("step_fields_applicable"),E.Cue==A::ECue::StepLight01||E.Cue==A::ECue::StepLight02);O->SetBoolField(TEXT("dodge_fields_applicable"),E.Cue==A::ECue::DodgeShort01);O->SetBoolField(TEXT("request_only"),true);O->SetBoolField(TEXT("audible_or_mix_attribution_proven"),false);return O;
}
}

namespace
{
using JO=TSharedPtr<FJsonObject>;using JV=TSharedPtr<FJsonValue>;
namespace Air=DungeonFairytaleSwordAirV001;
namespace DodgeArt=DungeonFairytaleSwordDodgeV001;
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

namespace
{
JO EquipmentAction(const FDungeonEquipmentActionView& E)
{
 auto O=MakeShared<FJsonObject>();O->SetNumberField(TEXT("kind"),int32(E.Kind));O->SetBoolField(TEXT("active"),E.Active);Id(O,TEXT("action_id"),E.ActionId);Id(O,TEXT("operation_id"),E.OperationId);Id(O,TEXT("source_id"),E.SourceId);Id(O,TEXT("instance_id"),E.InstanceId);O->SetNumberField(TEXT("slot"),E.Slot);O->SetNumberField(TEXT("start"),E.Start);O->SetNumberField(TEXT("deadline"),E.Deadline);return O;
}
bool SameSample(const FDungeonHeroAirSample& A,const FDungeonHeroAirSample& B)
{return A.Valid==B.Valid&&A.RunGuid==B.RunGuid&&A.OwnerId==B.OwnerId&&A.RoomInstanceId==B.RoomInstanceId&&A.PresentationEpoch==B.PresentationEpoch&&A.NativeTime==B.NativeTime&&A.GroundPosition==B.GroundPosition&&A.Facing==B.Facing&&A.JumpHeight==B.JumpHeight&&A.VerticalVelocity==B.VerticalVelocity&&A.LandingVisualAge==B.LandingVisualAge;}
// Request258 immutable contract only; no loading, simulation or input.
bool Bridge258ObservationEnabled()
{
 FString RequestedAction;
 return FParse::Param(FCommandLine::Get(),TEXT("DungeonFairytalePrimary1Bridge258Preview"))
  &&FParse::Value(FCommandLine::Get(),TEXT("DungeonHeroLandingPriorityAction="),RequestedAction)&&RequestedAction==TEXT("J");
}
struct FBridge258SourcePin{int32 Frame;const TCHAR* Component;const TCHAR* ObjectPath;const TCHAR* SourcePNG;uint64 SourceBytes;const TCHAR* SourceSHA256;};
const FBridge258SourcePin Bridge258SourcePins[]={
 {0,TEXT("BodyRest"),TEXT("/Game/Production/ArtTrials/Request258/v001/HeroPrimary1Bridge/T_Fairytale_Bridge258_BodyRest_000_v001.T_Fairytale_Bridge258_BodyRest_000_v001"),TEXT("F:/Ourgame/source-assets/production/fairytale-hero-four-pose-polish-v001/request258-primary1-body-correction/matte-edge-clean-candidate-v002/body-layers/BodyRest/frame-0.png"),187738ULL,TEXT("6bb844ea18ace3a17ad86e744ebfbf5b1143b1cafb8d7a3436ac96f4500010a8")},
 {0,TEXT("ShoulderFar"),TEXT("/Game/Production/ArtTrials/Request258/v001/HeroPrimary1Bridge/T_Fairytale_Bridge258_ShoulderFar_000_v001.T_Fairytale_Bridge258_ShoulderFar_000_v001"),TEXT("F:/Ourgame/source-assets/production/fairytale-hero-four-pose-polish-v001/request258-primary1-body-correction/body-partition-fit-candidate-v001/armor-integer-fit/FarShoulder/frame-0.png"),2947ULL,TEXT("75a095689770e42697306a4308642f12f86293668e875865313a2e74dc107e94")},
 {0,TEXT("Chest"),TEXT("/Game/Production/ArtTrials/Request258/v001/HeroPrimary1Bridge/T_Fairytale_Bridge258_Chest_000_v001.T_Fairytale_Bridge258_Chest_000_v001"),TEXT("F:/Ourgame/source-assets/production/fairytale-hero-four-pose-polish-v001/request258-primary1-body-correction/body-partition-fit-candidate-v001/armor-integer-fit/Chest/frame-0.png"),18191ULL,TEXT("c6e93fa5efa376d4c0425f097cba4d699a156861bce8222710ea3b6223f44732")},
 {0,TEXT("NearArmWithoutHand"),TEXT("/Game/Production/ArtTrials/Request258/v001/HeroPrimary1Bridge/T_Fairytale_Bridge258_NearArmWithoutHand_000_v001.T_Fairytale_Bridge258_NearArmWithoutHand_000_v001"),TEXT("F:/Ourgame/source-assets/production/fairytale-hero-four-pose-polish-v001/request258-primary1-body-correction/matte-edge-clean-candidate-v002/body-layers/NearArmWithoutHand/frame-0.png"),6059ULL,TEXT("f45a082a6bf3e33eb6308d5da6528d462bced57ab5a27fbf102b996274efa7b8")},
 {0,TEXT("ShoulderNear"),TEXT("/Game/Production/ArtTrials/Request258/v001/HeroPrimary1Bridge/T_Fairytale_Bridge258_ShoulderNear_000_v001.T_Fairytale_Bridge258_ShoulderNear_000_v001"),TEXT("F:/Ourgame/source-assets/production/fairytale-hero-four-pose-polish-v001/request258-primary1-body-correction/body-partition-fit-candidate-v001/armor-integer-fit/NearShoulder/frame-0.png"),6405ULL,TEXT("9978b306fe5b564a4f1f5b39ad341df773b5dc42cd2bc00846d48a655f3f1ea4")},
 {0,TEXT("HelmetForeground"),TEXT("/Game/Production/ArtTrials/Request258/v001/HeroPrimary1Bridge/T_Fairytale_Bridge258_HelmetForeground_000_v001.T_Fairytale_Bridge258_HelmetForeground_000_v001"),TEXT("F:/Ourgame/source-assets/production/fairytale-hero-four-pose-polish-v001/request258-primary1-body-correction/matte-edge-clean-candidate-v002/body-layers/HelmetForeground/frame-0.png"),64363ULL,TEXT("3daebe6bd7d59cd59b8dde96bc020cbc717d54b9ec76dd5b37ee8d7117562ce5")},
 {0,TEXT("NearHand"),TEXT("/Game/Production/ArtTrials/Request258/v001/HeroPrimary1Bridge/T_Fairytale_Bridge258_NearHand_000_v001.T_Fairytale_Bridge258_NearHand_000_v001"),TEXT("F:/Ourgame/source-assets/production/fairytale-hero-four-pose-polish-v001/request258-primary1-body-correction/matte-edge-clean-candidate-v002/body-layers/NearHand/frame-0.png"),10182ULL,TEXT("bd6e6a18c91cc0ecea7d2a999251f7f752904df49ab0e679a575152faf86d938")},
 {1,TEXT("BodyRest"),TEXT("/Game/Production/ArtTrials/Request258/v001/HeroPrimary1Bridge/T_Fairytale_Bridge258_BodyRest_001_v001.T_Fairytale_Bridge258_BodyRest_001_v001"),TEXT("F:/Ourgame/source-assets/production/fairytale-hero-four-pose-polish-v001/request258-primary1-body-correction/matte-edge-clean-candidate-v002/body-layers/BodyRest/frame-1.png"),197214ULL,TEXT("1653e5f403e457270b4537433526390c1a5a7420970ba97f77789ef4f8819766")},
 {1,TEXT("ShoulderFar"),TEXT("/Game/Production/ArtTrials/Request258/v001/HeroPrimary1Bridge/T_Fairytale_Bridge258_ShoulderFar_001_v001.T_Fairytale_Bridge258_ShoulderFar_001_v001"),TEXT("F:/Ourgame/source-assets/production/fairytale-hero-four-pose-polish-v001/request258-primary1-body-correction/body-partition-fit-candidate-v001/armor-integer-fit/FarShoulder/frame-1.png"),3080ULL,TEXT("db8ca9de168204a5bf7f13d4ae86de4838eead663206cba5204698368991c3db")},
 {1,TEXT("Chest"),TEXT("/Game/Production/ArtTrials/Request258/v001/HeroPrimary1Bridge/T_Fairytale_Bridge258_Chest_001_v001.T_Fairytale_Bridge258_Chest_001_v001"),TEXT("F:/Ourgame/source-assets/production/fairytale-hero-four-pose-polish-v001/request258-primary1-body-correction/body-partition-fit-candidate-v001/armor-integer-fit/Chest/frame-1.png"),17913ULL,TEXT("04dfebd2c8b66015b4067a2eb1f6b8684507e3d0df5ccaca734e8807dd790575")},
 {1,TEXT("NearArmWithoutHand"),TEXT("/Game/Production/ArtTrials/Request258/v001/HeroPrimary1Bridge/T_Fairytale_Bridge258_NearArmWithoutHand_001_v001.T_Fairytale_Bridge258_NearArmWithoutHand_001_v001"),TEXT("F:/Ourgame/source-assets/production/fairytale-hero-four-pose-polish-v001/request258-primary1-body-correction/matte-edge-clean-candidate-v002/body-layers/NearArmWithoutHand/frame-1.png"),6425ULL,TEXT("fdd0dd4fda28d0877eae70d636733daa4227a36c1ea34d70f22500479fde575c")},
 {1,TEXT("ShoulderNear"),TEXT("/Game/Production/ArtTrials/Request258/v001/HeroPrimary1Bridge/T_Fairytale_Bridge258_ShoulderNear_001_v001.T_Fairytale_Bridge258_ShoulderNear_001_v001"),TEXT("F:/Ourgame/source-assets/production/fairytale-hero-four-pose-polish-v001/request258-primary1-body-correction/body-partition-fit-candidate-v001/armor-integer-fit/NearShoulder/frame-1.png"),6925ULL,TEXT("6100c5f1af39f77693a8e9ef258cd5a909596c9fff7c506d37d795669f745e6c")},
 {1,TEXT("HelmetForeground"),TEXT("/Game/Production/ArtTrials/Request258/v001/HeroPrimary1Bridge/T_Fairytale_Bridge258_HelmetForeground_001_v001.T_Fairytale_Bridge258_HelmetForeground_001_v001"),TEXT("F:/Ourgame/source-assets/production/fairytale-hero-four-pose-polish-v001/request258-primary1-body-correction/matte-edge-clean-candidate-v002/body-layers/HelmetForeground/frame-1.png"),56945ULL,TEXT("621f27b84218ce75402c86e4e61f39184e1cc5385f34967510d793ee2e8996c9")},
 {1,TEXT("NearHand"),TEXT("/Game/Production/ArtTrials/Request258/v001/HeroPrimary1Bridge/T_Fairytale_Bridge258_NearHand_001_v001.T_Fairytale_Bridge258_NearHand_001_v001"),TEXT("F:/Ourgame/source-assets/production/fairytale-hero-four-pose-polish-v001/request258-primary1-body-correction/matte-edge-clean-candidate-v002/body-layers/NearHand/frame-1.png"),10387ULL,TEXT("e55f4a43ec7fc795561e63a19e8ee7f46d2fff0354371f66e566684a2cc7ea7a")},
};
bool Brown(const FDungeonFairytaleSwordDraw& D,bool Primary)
{
 if(!D.Active||!D.Supported||!D.ActionPoseSupported||!D.TextureReady||!D.ArmorDrawn||!SwordDrawn(D)||D.GearPlaceholder||D.Frame<0||D.Frame>=(Primary?6:4)||D.DrawStack.Num()!=(Primary?8:7))return false;
 if(D.Clip!=(Primary?TEXT("sword_primary_1"):TEXT("sword_ready_idle")))return false;
 if(Primary&&D.Frame<2&&Bridge258ObservationEnabled())
 {
  const FString Sword=TEXT("/Game/Production/FirstBatch/v002/CandidateComponents/T_military_sword_v002.T_military_sword_v002");
  const FVector2D Grip=D.Frame==0?FVector2D(211.,343.):FVector2D(159.,213.);
  const FVector2D Axis=D.Frame==0?FVector2D(.94,-.341):FVector2D(-.2,-.98);
  const double Angle=FMath::RadiansToDegrees(FMath::Atan2(Axis.Y,Axis.X))*(D.Facing<0?-1.:1.);
  if((D.Facing!=1&&D.Facing!=-1)||D.Root!=FVector2D(256.,464.)||D.Grip!=Grip||D.WeaponPath!=Sword||D.WeaponScale!=.5||D.WeaponAngle!=Angle)return false;
  const TCHAR* Parts[]={TEXT("BodyRest"),TEXT("ShoulderFar"),TEXT("Chest"),TEXT("NearArmWithoutHand"),TEXT("ShoulderNear"),TEXT("HelmetForeground"),TEXT(""),TEXT("NearHand")};
  for(int32 I=0;I<8;++I)
  {
   FString Expected=Sword;
   if(I!=6){const FString Name=FString::Printf(TEXT("T_Fairytale_Bridge258_%s_%03d_v001"),Parts[I],D.Frame);Expected=FString(TEXT("/Game/Production/ArtTrials/Request258/v001/HeroPrimary1Bridge/"))+Name+TEXT(".")+Name;}
   if(D.DrawStack[I]!=Expected)return false;
  }
  return true;
 }
 const TCHAR* Parts[]={TEXT("ShoulderFar"),TEXT("Chest"),TEXT("ShoulderNear")};const int32 Slots[]={1,2,4};
 for(int32 I=0;I<3;++I){const FString Name=Primary?FString::Printf(TEXT("T_Fairytale_LeatherPrimary1%s_%03d_v001"),Parts[I],D.Frame):FString::Printf(TEXT("T_Fairytale_LeatherReady%s_%03d_v001"),Parts[I],D.Frame);
  const FString Expected=FString(Primary?TEXT("/Game/Production/ArtTrials/EV048/v013/HeroLeatherPrimary1/"):TEXT("/Game/Production/ArtTrials/EV048/v012/HeroLeatherReady/"))+Name+TEXT(".")+Name;if(D.DrawStack[Slots[I]]!=Expected)return false;}
 return true;
}
JO Bridge258LegacyResidencyStatus(const FString& RequestedPath,const UTexture2D* Texture)
{
 auto O=MakeShared<FJsonObject>();O->SetStringField(TEXT("requested_path"),RequestedPath);
 O->SetNumberField(TEXT("observed_monotonic_s"),FPlatformTime::Seconds());
 O->SetBoolField(TEXT("object_present"),Texture!=nullptr);
 if(!Texture)
 {
  for(const TCHAR* Key:{TEXT("actual_path"),TEXT("class"),TEXT("width"),TEXT("height"),TEXT("object_flags"),TEXT("is_compiling"),TEXT("async_cache_complete"),TEXT("pending_initialization"),TEXT("resource_initialized"),TEXT("resource_is_proxy")})O->SetField(Key,MakeShared<FJsonValueNull>());
  O->SetBoolField(TEXT("resource_present"),false);O->SetBoolField(TEXT("editor_status_available"),false);return O;
 }
 O->SetStringField(TEXT("actual_path"),Texture->GetPathName());O->SetStringField(TEXT("class"),Texture->GetClass()->GetName());
 O->SetNumberField(TEXT("width"),Texture->GetSizeX());O->SetNumberField(TEXT("height"),Texture->GetSizeY());Id(O,TEXT("object_flags"),uint64(Texture->GetFlags()));
 O->SetBoolField(TEXT("pending_initialization"),Texture->HasPendingRenderResourceInitialization());
 const FTextureResource* Resource=Texture->GetResource();O->SetBoolField(TEXT("resource_present"),Resource!=nullptr);
 if(Resource){O->SetBoolField(TEXT("resource_initialized"),Resource->IsInitialized());O->SetBoolField(TEXT("resource_is_proxy"),Resource->IsProxy());}
 else{O->SetField(TEXT("resource_initialized"),MakeShared<FJsonValueNull>());O->SetField(TEXT("resource_is_proxy"),MakeShared<FJsonValueNull>());}
#if WITH_EDITOR
 O->SetBoolField(TEXT("editor_status_available"),true);O->SetBoolField(TEXT("is_compiling"),Texture->IsCompiling());O->SetBoolField(TEXT("async_cache_complete"),Texture->IsAsyncCacheComplete());
#else
 O->SetBoolField(TEXT("editor_status_available"),false);O->SetField(TEXT("is_compiling"),MakeShared<FJsonValueNull>());O->SetField(TEXT("async_cache_complete"),MakeShared<FJsonValueNull>());
#endif
 return O;
}

JO DodgeDraw(const FDungeonFairytaleSwordDodgeDraw& D)
{
 auto O=MakeShared<FJsonObject>();Id(O,TEXT("draw_id"),D.DrawId);Id(O,TEXT("player_entity"),D.PlayerEntityId);O->SetNumberField(TEXT("sim"),D.SimulationTime);O->SetBoolField(TEXT("drawn"),D.Drawn);O->SetBoolField(TEXT("atomic_preflight_ready"),D.AtomicPreflightReady);O->SetNumberField(TEXT("frame"),D.Plan.Frame);O->SetNumberField(TEXT("facing"),D.Plan.Facing);O->SetNumberField(TEXT("slot_count"),D.Slots.Num());O->SetNumberField(TEXT("resident_count"),D.ResidentTextures.Num());O->SetArrayField(TEXT("actual_stack"),Strings(D.ActualRenderedStack));
 O->SetArrayField(TEXT("context_ground"),XY(D.Context.GroundScreen));O->SetNumberField(TEXT("ui_scale"),D.Context.UIScale);O->SetArrayField(TEXT("root_source"),XY(D.Plan.RootSource));O->SetArrayField(TEXT("grip_source"),XY(D.Plan.GripSource));O->SetArrayField(TEXT("axis_artist"),XY(D.Plan.AxisArtist));O->SetArrayField(TEXT("body_top"),XY(D.Plan.BodyTop));O->SetArrayField(TEXT("sword_top"),XY(D.Plan.SwordTop));O->SetArrayField(TEXT("sword_pivot_uv"),XY(D.Plan.SwordPivotUV));O->SetNumberField(TEXT("canvas_size"),D.Plan.CanvasSize);O->SetNumberField(TEXT("weapon_width"),D.Plan.WeaponWidth);O->SetNumberField(TEXT("weapon_angle"),D.Plan.WeaponAngle);O->SetNumberField(TEXT("source_to_screen_scale"),D.Plan.SourceToScreenScale);
 TArray<JV> Slots;for(const auto& S:D.Slots){auto X=MakeShared<FJsonObject>();X->SetNumberField(TEXT("slot"),S.SlotIndex);X->SetNumberField(TEXT("component"),int32(S.Component));X->SetStringField(TEXT("texture"),S.TexturePath);X->SetBoolField(TEXT("drawn"),S.Drawn);X->SetBoolField(TEXT("texture_ready"),S.TextureReady);X->SetBoolField(TEXT("known_empty"),S.KnownOptionalEmpty);X->SetArrayField(TEXT("top"),XY(S.Top));X->SetArrayField(TEXT("size"),XY(S.Size));X->SetArrayField(TEXT("uv"),XY(S.UV));X->SetArrayField(TEXT("uv_size"),XY(S.UVSize));X->SetNumberField(TEXT("rotation"),S.RotationDegrees);X->SetArrayField(TEXT("rotation_pivot"),XY(S.RotationPivot));X->SetNumberField(TEXT("draw_scale"),S.DrawScale);X->SetBoolField(TEXT("scale_position"),S.ScalePosition);TArray<JV> Tint;for(double V:{double(S.TraceTint.R),double(S.TraceTint.G),double(S.TraceTint.B),double(S.TraceTint.A)})Tint.Add(MakeShared<FJsonValueNumber>(V));X->SetArrayField(TEXT("trace_tint"),Tint);Slots.Add(MakeShared<FJsonValueObject>(X));}O->SetArrayField(TEXT("slots"),Slots);
 TArray<JV> Residents;for(const auto& T:D.ResidentTextures){auto X=MakeShared<FJsonObject>();X->SetStringField(TEXT("texture"),T.TexturePath);X->SetStringField(TEXT("class"),T.ClassName);X->SetNumberField(TEXT("width"),T.Width);X->SetNumberField(TEXT("height"),T.Height);X->SetBoolField(TEXT("resource_ready"),T.ResourceReady);X->SetBoolField(TEXT("pending_initialization"),T.PendingInitialization);Residents.Add(MakeShared<FJsonValueObject>(X));}O->SetArrayField(TEXT("resident_textures"),Residents);return O;
}
}

struct FDungeonHeroLandingPriorityProofStateV001
{
 FString Directory,Failure,Action;int32 Side=0,Phase=0,JumpInputs=0,AirTransitions=0;
 bool Stopped=false,Stopping=false,EvidenceClaimed=false,Capturing=false,PrewarmRequested=false,PrewarmDone=false,AudioRequested=false,StartupReadbackComplete=false,GearPinned=false,KnightCleared=false,AllowKnightDiagnostic=false,EIssued=false,ReadyConsumed=false,LandConsumed=false,FlowComplete=false;
 double WarmStarted=0.,Start=0.,Stop=0.,PhaseAt=0.,ReleaseAt=0.,NeutralUntil=0.,InitialHP=0.,CaptureFinalHP=0.,StartupReadbackStop=0.,ActionStart=-1.,ActionEnd=-1.,StartLandingAge=-1.;
 uint64 Owner=0,Room=0,Epoch=0,Restart=0,LightSource=0,Light=0,Sword=0,SwordVersion=0,LightVersion=0,LastDraw=0,ActualActionId=0,PriorActionId=0;
 uint64 EquipActionId=0,EquipOperationId=0;double EquipStart=-1.,EquipDeadline=-1.;
 int32 EquipInputIndex=INDEX_NONE,EquipStartedIndex=INDEX_NONE,EquipCommitIndex=INDEX_NONE;
 int32 ReadyIndex=INDEX_NONE,LandIndex=INDEX_NONE,InputIndex=INDEX_NONE,FirstActionIndex=INDEX_NONE,ReadyJoinFrames=0;uint32 AirMask=0,PrimaryMask=0,DodgeMask=0;
 FGuid Run;FKey PulseKey;TMap<FKey,bool> Keys;
 TWeakObjectPtr<ADungeonGameMode> Game;TWeakObjectPtr<APlayerController> Controller;TWeakObjectPtr<ADungeonHUD> HUD;
 TArray<JV> Inputs,Steps,Observations,Offsets,DiagnosticHits,StartupTextures;
 TArray<JV> Bridge258LegacyResidencyBefore,Bridge258LegacyResidencyAfter;
 bool Bridge258LegacyFinishRequested=false;int32 Bridge258LegacyFinishTargetCount=0;
 TArray<JV> HeroAudioCapturedRequests;
 DungeonHeroLocomotionObservationV001::FRequestCursor HeroAudioCursor;
 FString HeroAudioLastCurrentScope;
 double HeroAudioPreviousCallbackWall=0.;int32 HeroAudioCallbackCount=0,HeroAudioScopeChanges=0,HeroAudioSequenceGaps=0;
 uint64 HeroAudioGapMissingSequences=0;bool HeroAudioRingLimitSeen=false,HeroAudioFirstSnapshotTruncationPossible=false;
 JO ObserveHeroAudioRequests(ADungeonGameMode& G,ADungeonFighter& P,int32 Callback,double Wall)
 {
  namespace O=DungeonHeroLocomotionObservationV001;const auto& V=G.GetEquipmentView();const auto& Ring=G.GetHeroLocomotionAudioPlayRequestsV001();auto Out=MakeShared<FJsonObject>();auto Current=O::CurrentScope(G,P);auto Window=O::WallWindow(HeroAudioPreviousCallbackWall>0.?HeroAudioPreviousCallbackWall:Start,Wall,Start);
  const FString Context=V.RunGuid.ToString(EGuidFormats::Digits)+FString::Printf(TEXT("/%llu/%llu/%llu/%llu"),P.GetRuntimeEntityId(),V.RoomInstanceId,G.GetRunRestartSerial(),G.GetRunPresentationEpoch());const bool First=HeroAudioLastCurrentScope.IsEmpty(),Changed=!First&&Context!=HeroAudioLastCurrentScope;
  if(Changed)++HeroAudioScopeChanges;HeroAudioLastCurrentScope=Context;HeroAudioRingLimitSeen|=Ring.Num()>=256;
  if((First||Changed)&&Ring.Num()>0&&Ring[0].Source.Sequence>1)HeroAudioFirstSnapshotTruncationPossible=true;
  Out->SetStringField(TEXT("schema"),TEXT("hero-locomotion-request-observation-v001"));Out->SetNumberField(TEXT("callback_index"),Callback);Out->SetObjectField(TEXT("current_scope"),Current);Out->SetObjectField(TEXT("callback_wall_window"),Window);Out->SetObjectField(TEXT("ground_witness"),O::GroundWitness(P));Out->SetNumberField(TEXT("ring_snapshot_count"),Ring.Num());O::AudioId(Out,TEXT("ring_first_sequence"),Ring.Num()?Ring[0].Source.Sequence:0);O::AudioId(Out,TEXT("ring_last_sequence"),Ring.Num()?Ring.Last().Source.Sequence:0);Out->SetBoolField(TEXT("scope_changed"),Changed);Out->SetNumberField(TEXT("ring_limit"),256);
  TArray<JV> New;for(const auto& R:Ring)
  {
   uint64 Gap=0;if(!HeroAudioCursor.Observe(O::RequestKey(V.RunGuid,R.Source.Scope),R.Source.Sequence,Gap))continue;
   if(Gap){++HeroAudioSequenceGaps;HeroAudioGapMissingSequences+=Gap;}
   auto Row=O::RequestRow(R,Callback,Phase,G.GetSimulationTime(),Window,Current);const auto& S=R.Source.Scope;Row->SetBoolField(TEXT("request_scope_matches_current"),S.Owner==P.GetRuntimeEntityId()&&S.Room==V.RoomInstanceId&&S.Restart==G.GetRunRestartSerial()&&S.Epoch==G.GetRunPresentationEpoch());O::AudioId(Row,TEXT("sequence_gap_before"),Gap);const auto Value=MakeShared<FJsonValueObject>(Row);New.Add(Value);HeroAudioCapturedRequests.Add(Value);
  }
  Out->SetNumberField(TEXT("new_request_count"),New.Num());Out->SetNumberField(TEXT("captured_request_prefix_count"),HeroAudioCapturedRequests.Num());Out->SetArrayField(TEXT("new_requests"),New);Out->SetBoolField(TEXT("request_only"),true);Out->SetBoolField(TEXT("audible_or_mix_attribution_proven"),false);HeroAudioPreviousCallbackWall=Wall;++HeroAudioCallbackCount;return Out;
 }
 JO FinalHeroAudioRequests() const
 {
  auto O=MakeShared<FJsonObject>();O->SetStringField(TEXT("schema"),TEXT("hero-locomotion-request-observation-v001"));O->SetArrayField(TEXT("captured_requests"),HeroAudioCapturedRequests);O->SetNumberField(TEXT("captured_request_count"),HeroAudioCapturedRequests.Num());O->SetNumberField(TEXT("callback_count"),HeroAudioCallbackCount);O->SetNumberField(TEXT("scope_change_count"),HeroAudioScopeChanges);O->SetNumberField(TEXT("sequence_gap_count"),HeroAudioSequenceGaps);DungeonHeroLocomotionObservationV001::AudioId(O,TEXT("sequence_gap_missing_sequence_total"),HeroAudioGapMissingSequences);O->SetNumberField(TEXT("ring_limit"),256);O->SetBoolField(TEXT("ring_limit_seen"),HeroAudioRingLimitSeen);O->SetBoolField(TEXT("first_snapshot_truncation_possible"),HeroAudioFirstSnapshotTruncationPossible);O->SetStringField(TEXT("scope_reset_policy"),TEXT("existing_getter_resets_on_owner_run_room_restart_epoch; only_first_seen_requests_retained_here"));O->SetStringField(TEXT("sequence_gap_semantics"),TEXT("missing_producer_sequences_are_not_proven_ring_loss_or_missing_playback"));O->SetStringField(TEXT("completeness"),TEXT("complete_first_seen_sequence_only; unobserved_ring_eviction_or_scope_reset_cannot_be_reconstructed"));O->SetBoolField(TEXT("request_only"),true);O->SetBoolField(TEXT("audible_or_mix_attribution_proven"),false);return O;
 }
 void Next(int32 P){Phase=P;PhaseAt=FPlatformTime::Seconds();auto O=MakeShared<FJsonObject>();O->SetNumberField(TEXT("phase"),P);O->SetNumberField(TEXT("wall_offset_s"),PhaseAt-Start);O->SetNumberField(TEXT("sim"),Game.IsValid()?Game->GetSimulationTime():0.);Steps.Add(MakeShared<FJsonValueObject>(O));}
 bool Need(bool Yes,const FString& Why){if(!Yes&&Failure.IsEmpty())Failure=Why;return Yes;}
 void Key(FKey K,bool Down)
 {
  if(!Controller.IsValid()||Keys.FindRef(K)==Down)return;
  auto P=Game.IsValid()?Game->PlayerFighter.Get():nullptr;auto O=MakeShared<FJsonObject>();
  if(Game.IsValid())
  {
   const auto& InputView=Game->GetEquipmentView();
   Id(O,TEXT("selected_source_id"),InputView.SelectedSourceId);O->SetObjectField(TEXT("before_equipment_action"),EquipmentAction(InputView.Action));
   O->SetBoolField(TEXT("context_sampled_before_InputKey"),true);
   O->SetStringField(TEXT("run"),InputView.RunGuid.ToString(EGuidFormats::Digits));Id(O,TEXT("owner"),InputView.OwnerId);
   Id(O,TEXT("current_room"),InputView.RoomInstanceId);Id(O,TEXT("epoch"),Game->GetRunPresentationEpoch());
   Id(O,TEXT("player_entity"),P?P->GetRuntimeEntityId():0);
   if(InputView.ActiveSlot>=0&&InputView.ActiveSlot<3)
   {Id(O,TEXT("weapon_instance"),InputView.Slots[InputView.ActiveSlot].InstanceId);Id(O,TEXT("weapon_version"),InputView.Slots[InputView.ActiveSlot].Version);}
   Id(O,TEXT("armor_instance"),InputView.Slots[2].InstanceId);Id(O,TEXT("armor_version"),InputView.Slots[2].Version);
   O->SetNumberField(TEXT("observed_air_transition_ordinal_before"),AirTransitions);
   O->SetNumberField(TEXT("space_enqueue_observer_ordinal"),Down&&K==EKeys::SpaceBar?JumpInputs+1:0);
   O->SetBoolField(TEXT("space_enqueue_ordinal_is_gameplay_jump_id"),false);
  }
  if(P){const uint64 BeforeId=Action==TEXT("J")?P->GetMeleeCombatState().Action.AttackId:P->GetDodgeState().Records.empty()?0:P->GetDodgeState().Records.back().ActionId;Id(O,TEXT("before_action_id"),BeforeId);O->SetBoolField(TEXT("before_melee_grounded"),P->GetMeleeCombatState().Grounded);O->SetBoolField(TEXT("before_wa_grounded"),P->GetWeaponActionsState().Budget.Grounded);O->SetNumberField(TEXT("facing"),P->Facing);O->SetNumberField(TEXT("before_H"),P->JumpHeight);O->SetNumberField(TEXT("before_V"),P->GetVerticalVelocity());O->SetNumberField(TEXT("before_landing_age"),P->GetLandingVisualAge());}
  O->SetNumberField(TEXT("wall_offset_s"),FPlatformTime::Seconds()-Start);O->SetNumberField(TEXT("sim"),Game.IsValid()?Game->GetSimulationTime():0.);
  Controller->InputKey(FInputKeyParams(K,Down?IE_Pressed:IE_Released,Down?1.:0.));Keys.Add(K,Down);
  O->SetStringField(TEXT("key"),K.GetFName().ToString());O->SetBoolField(TEXT("down"),Down);
  if(P){const uint64 AfterId=Action==TEXT("J")?P->GetMeleeCombatState().Action.AttackId:P->GetDodgeState().Records.empty()?0:P->GetDodgeState().Records.back().ActionId;Id(O,TEXT("after_action_id"),AfterId);O->SetNumberField(TEXT("after_H"),P->JumpHeight);O->SetNumberField(TEXT("after_V"),P->GetVerticalVelocity());O->SetNumberField(TEXT("after_landing_age"),P->GetLandingVisualAge());}
  Inputs.Add(MakeShared<FJsonValueObject>(O));
 }
 bool CanPulse()const{return !PulseKey.IsValid()&&FPlatformTime::Seconds()>=NeutralUntil;}
 bool Pulse(FKey K){if(!CanPulse())return false;Key(K,true);PulseKey=K;ReleaseAt=FPlatformTime::Seconds()+.04;return true;}
 void ReleaseKeys(){TArray<FKey> Held;Keys.GetKeys(Held);for(FKey K:Held)Key(K,false);PulseKey=FKey();}
 void BeginStop(ADungeonHeroLandingPriorityProbeV001& Actor)
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

 bool CaptureTextureBytesBeforeAudio()
 {
  if(StartupReadbackComplete)return true;
  const auto& Profile=Air::Profile();
  if(!Need(Profile.SourceClosureVerified&&Profile.SourceClosureSHA256==ExpectedClosure&&Profile.CanvasSource==512&&Profile.StandingExtent==416.&&Profile.StandingDisplay==72.&&Profile.HeightProjection==.70&&Profile.WeaponScale==.5,TEXT("Exact retained Air49 profile is not admitted")))return false;
  if(!Need(!Capturing&&!AudioRequested&&GIsDumpingMovie==0,TEXT("Texture GPU/source readback must precede audio/movie/input")))return false;
  // The new renderer selects Bridge258 J0/J1, so explicitly retain the old
  // fourteen layers still required by the unchanged old115 readback contract.
  TArray<TStrongObjectPtr<UTexture2D>> Bridge258LegacyReadbackRefs;
  if(Bridge258ObservationEnabled()&&Action==TEXT("J"))
  {
   TArray<FString> Bridge258LegacyRequestedPaths;
   for(int32 Frame=0;Frame<2;++Frame)for(const TCHAR* Component:{TEXT("BodyRest"),TEXT("ShoulderFar"),TEXT("Chest"),TEXT("NearArmWithoutHand"),TEXT("ShoulderNear"),TEXT("HelmetForeground"),TEXT("NearHand")})
   {
    const bool Armor=FString(Component)==TEXT("ShoulderFar")||FString(Component)==TEXT("Chest")||FString(Component)==TEXT("ShoulderNear");
    const FString Name=Armor?FString::Printf(TEXT("T_Fairytale_LeatherPrimary1%s_%03d_v001"),Component,Frame):FString::Printf(TEXT("T_Fairytale_SwordPrimary1%s_%03d_v001"),Component,Frame);
    const FString Path=FString(Armor?TEXT("/Game/Production/ArtTrials/EV048/v013/HeroLeatherPrimary1/"):TEXT("/Game/Production/ArtTrials/EV048/v007/HeroSwordArmorPrimary1/"))+Name+TEXT(".")+Name;
    Bridge258LegacyReadbackRefs.Emplace(LoadObject<UTexture2D>(nullptr,*Path));
    Bridge258LegacyRequestedPaths.Add(Path);
   }
   for(int32 Index=0;Index<Bridge258LegacyReadbackRefs.Num();++Index)
    Bridge258LegacyResidencyBefore.Add(MakeShared<FJsonValueObject>(Bridge258LegacyResidencyStatus(Bridge258LegacyRequestedPaths[Index],Bridge258LegacyReadbackRefs[Index].Get())));
#if WITH_EDITOR
   // UObject load/render flush do not complete editor platform-data compilation.
   // Restrict this pre-audio/pre-input barrier to the fourteen retained old layers.
   TArray<UTexture*> Bridge258LegacyCompilationTargets;
   for(const auto& Ref:Bridge258LegacyReadbackRefs)if(Ref.Get())Bridge258LegacyCompilationTargets.Add(Ref.Get());
   Bridge258LegacyFinishRequested=true;Bridge258LegacyFinishTargetCount=Bridge258LegacyCompilationTargets.Num();
   FTextureCompilingManager::Get().FinishCompilation(Bridge258LegacyCompilationTargets);
#endif
   FlushRenderingCommands(); // Before the original strict FindObject/RHI/pending checks, before audio/input.
   for(int32 Index=0;Index<Bridge258LegacyReadbackRefs.Num();++Index)
    Bridge258LegacyResidencyAfter.Add(MakeShared<FJsonValueObject>(Bridge258LegacyResidencyStatus(Bridge258LegacyRequestedPaths[Index],Bridge258LegacyReadbackRefs[Index].Get())));
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
  int32 ExpectedReadbacks=49;
  for(int32 Frame=0;Frame<4;++Frame)for(const TCHAR* Component:{TEXT("BodyRest"),TEXT("ShoulderFar"),TEXT("Chest"),TEXT("NearArmWithoutHand"),TEXT("ShoulderNear"),TEXT("NearHand")})
  {const bool Armor=FString(Component)==TEXT("ShoulderFar")||FString(Component)==TEXT("Chest")||FString(Component)==TEXT("ShoulderNear");
   const FString Name=Armor?FString::Printf(TEXT("T_Fairytale_LeatherReady%s_%03d_v001"),Component,Frame):FString::Printf(TEXT("T_Fairytale_SwordReady%s_%03d_v001"),Component,Frame);
   const FString Path=FString(Armor?TEXT("/Game/Production/ArtTrials/EV048/v012/HeroLeatherReady/"):TEXT("/Game/Production/ArtTrials/EV048/v006/HeroSwordArmorReady/"))+Name+TEXT(".")+Name;
   if(!Capture(Path,TEXT(""),TEXT(""),Frame,-1))return false;++ExpectedReadbacks;}
  if(Action==TEXT("J"))
  {for(int32 Frame=0;Frame<6;++Frame)for(const TCHAR* Component:{TEXT("BodyRest"),TEXT("ShoulderFar"),TEXT("Chest"),TEXT("NearArmWithoutHand"),TEXT("ShoulderNear"),TEXT("HelmetForeground"),TEXT("NearHand")})
   {const bool Armor=FString(Component)==TEXT("ShoulderFar")||FString(Component)==TEXT("Chest")||FString(Component)==TEXT("ShoulderNear");
    const FString Name=Armor?FString::Printf(TEXT("T_Fairytale_LeatherPrimary1%s_%03d_v001"),Component,Frame):FString::Printf(TEXT("T_Fairytale_SwordPrimary1%s_%03d_v001"),Component,Frame);
    const FString Path=FString(Armor?TEXT("/Game/Production/ArtTrials/EV048/v013/HeroLeatherPrimary1/"):TEXT("/Game/Production/ArtTrials/EV048/v007/HeroSwordArmorPrimary1/"))+Name+TEXT(".")+Name;
    if(!Capture(Path,TEXT(""),TEXT(""),Frame,-1))return false;++ExpectedReadbacks;}}
  else for(const auto& Frame:DodgeArt::Profile().Frames)for(const auto& Layer:Frame.Layers)
  {if(!Capture(Layer.TexturePath,Layer.SourceSHA256,Layer.SourceRGBASHA256,Frame.Frame,int32(Layer.Component)))return false;++ExpectedReadbacks;}
  if(Bridge258ObservationEnabled()&&Action==TEXT("J"))
  {
   for(const auto& Pin:Bridge258SourcePins)
   {if(!Capture(Pin.ObjectPath,Pin.SourceSHA256,TEXT(""),Pin.Frame,-1))return false;++ExpectedReadbacks;}
  }
  FlushRenderingCommands();StartupReadbackStop=FPlatformTime::Seconds();StartupReadbackComplete=Need(Unique.Num()==ExpectedReadbacks&&StartupTextures.Num()==ExpectedReadbacks,TEXT("All49 independent GPU/source mip originals must finish before capture"));return StartupReadbackComplete;
 }

 void Observe(ADungeonHeroLandingPriorityProbeV001& Actor)
 {
  if(Stopped||Stopping)return;if(PrewarmRequested&&!PrewarmDone){PrewarmDone=Need(IFileManager::Get().FileSize(*(Directory/TEXT("prewarm-viewport.png")))>8,TEXT("Actual synchronous prewarm image missing"));return;}if(!Capturing)return;
  auto G=Game.Get();auto H=HUD.Get();auto P=G?G->PlayerFighter.Get():nullptr;if(!Need(G&&H&&P,TEXT("Completed callback lost owner"))){BeginStop(Actor);return;}
  const auto& V=G->GetEquipmentView();const auto& B=H->GetFairytaleSwordDraw();const auto& A=H->GetFairytaleSwordAirDraw();const auto& D=H->GetFairytaleSwordDodgeDraw();const auto& M=P->GetMeleeCombatState();const auto& DS=P->GetDodgeState();
  if(!Need(V.ActiveSlot>=0&&V.ActiveSlot<3,TEXT("Actual active slot is invalid"))){BeginStop(Actor);return;}
  const auto* Roll=DS.Records.empty()?nullptr:&DS.Records.back();const bool ActionActive=Action==TEXT("J")?M.Action.Active:DS.Phase==DungeonDodge::EPhase::Dodging;
  const uint64 ActionId=Action==TEXT("J")?M.Action.AttackId:Roll?Roll->ActionId:0;
  auto O=MakeShared<FJsonObject>();const double Offset=FPlatformTime::Seconds()-Start;const int32 Pose=PhysicalPose(P->JumpHeight,P->GetVerticalVelocity(),P->GetLandingVisualAge());
  O->SetBoolField(TEXT("completed_callback"),true);O->SetNumberField(TEXT("wall_offset_s"),Offset);O->SetNumberField(TEXT("phase"),Phase);O->SetNumberField(TEXT("sim"),G->GetSimulationTime());O->SetStringField(TEXT("run"),V.RunGuid.ToString(EGuidFormats::Digits));Id(O,TEXT("owner"),V.OwnerId);Id(O,TEXT("current_room"),V.RoomInstanceId);Id(O,TEXT("epoch"),G->GetRunPresentationEpoch());Id(O,TEXT("player_entity"),P->GetRuntimeEntityId());
  O->SetObjectField(TEXT("equipment_action"),EquipmentAction(V.Action));Id(O,TEXT("selected_source_id"),V.SelectedSourceId);Id(O,TEXT("next_operation_id"),V.NextOperationId);
  O->SetArrayField(TEXT("ground"),XY(P->GetGroundPosition()));O->SetArrayField(TEXT("camera_ground"),XY(H->GetCameraGroundCenter()));O->SetNumberField(TEXT("facing"),P->Facing);O->SetNumberField(TEXT("jump_height"),P->JumpHeight);O->SetNumberField(TEXT("vertical_velocity"),P->GetVerticalVelocity());O->SetNumberField(TEXT("landing_visual_age"),P->GetLandingVisualAge());O->SetNumberField(TEXT("physical_visual_key"),Pose);O->SetNumberField(TEXT("hp"),P->Health);O->SetBoolField(TEXT("dead"),P->bDead);O->SetStringField(TEXT("animation"),P->AnimationName);O->SetBoolField(TEXT("melee_grounded"),M.Grounded);O->SetBoolField(TEXT("wa_grounded"),P->GetWeaponActionsState().Budget.Grounded);
  O->SetNumberField(TEXT("melee_time"),M.Time);O->SetNumberField(TEXT("wa_time"),P->GetWeaponActionsState().Time);O->SetNumberField(TEXT("dodge_time"),DS.Time);O->SetNumberField(TEXT("weapon_world_time"),G->GetWeaponWorldState().Time);O->SetNumberField(TEXT("native_actor_root_z"),P->GetActorLocation().Z);
  FDungeonHeroAirSample Q;Q.Valid=true;Q.RunGuid=FGuid(1,2,3,4);Q.OwnerId=91;Q.RoomInstanceId=92;Q.PresentationEpoch=93;Q.NativeTime=-94.;Q.GroundPosition={95.,96.};Q.Facing=-1.f;Q.JumpHeight=97.f;Q.VerticalVelocity=-98.f;Q.LandingVisualAge=99.f;const auto Sentinel=Q;
  const bool QueryOK=P->QueryHeroNonAttackAir(Q);O->SetBoolField(TEXT("new_air_query_ok"),QueryOK);O->SetBoolField(TEXT("air_query_out_unchanged"),SameSample(Q,Sentinel));O->SetObjectField(TEXT("old_draw"),OldDraw(B));O->SetObjectField(TEXT("new_air_draw"),NewDraw(A));O->SetObjectField(TEXT("dodge_draw"),DodgeDraw(D));O->SetArrayField(TEXT("rendered_player_stack"),Strings(H->GetRenderedPlayerDrawStack()));O->SetStringField(TEXT("rendered_player_texture"),H->GetRenderedPlayerTexturePath());
  Id(O,TEXT("weapon_instance"),V.Slots[V.ActiveSlot].InstanceId);Id(O,TEXT("weapon_version"),V.Slots[V.ActiveSlot].Version);Id(O,TEXT("armor_instance"),V.Slots[2].InstanceId);Id(O,TEXT("armor_version"),V.Slots[2].Version);O->SetBoolField(TEXT("interface_visible"),H->GetInterfaceVisible());O->SetNumberField(TEXT("text_calls"),H->GetRenderedTextDrawCalls());O->SetBoolField(TEXT("range_debug"),H->IsCombatRangeDebugEnabled());O->SetNumberField(TEXT("range_lines"),H->GetCombatRangeDebugLineCount());
  auto X=MakeShared<FJsonObject>();X->SetBoolField(TEXT("active"),ActionActive);Id(X,TEXT("id"),ActionId);X->SetNumberField(TEXT("start"),Action==TEXT("J")?M.Action.Start:Roll?Roll->Start:-1.);X->SetNumberField(TEXT("end"),Action==TEXT("J")?M.Action.End:Roll?Roll->End:-1.);X->SetBoolField(TEXT("started_airborne"),Action==TEXT("J")&&M.Action.StartedAirborne);X->SetNumberField(TEXT("stage"),int32(M.Action.Stage));X->SetNumberField(TEXT("action_speed_pct"),M.Action.ActionSpeedPct);X->SetBoolField(TEXT("invulnerable"),P->IsDodgeInvulnerableAt(G->GetSimulationTime()));
  if(Roll){Id(X,TEXT("start_event_id"),Roll->StartEventId);Id(X,TEXT("finish_event_id"),Roll->FinishEventId);Id(X,TEXT("block_event_id"),Roll->BlockEventId);X->SetNumberField(TEXT("blocked_at"),Roll->BlockedAt);X->SetNumberField(TEXT("finished_at"),Roll->FinishedAt);X->SetNumberField(TEXT("block"),int32(Roll->Block));X->SetNumberField(TEXT("finish"),int32(Roll->Finish));X->SetNumberField(TEXT("travelled"),Roll->Travelled);X->SetArrayField(TEXT("origin"),{MakeShared<FJsonValueNumber>(Roll->Origin.X),MakeShared<FJsonValueNumber>(Roll->Origin.Y)});X->SetArrayField(TEXT("direction"),{MakeShared<FJsonValueNumber>(Roll->Direction.X),MakeShared<FJsonValueNumber>(Roll->Direction.Y)});}
  O->SetObjectField(TEXT("hero_locomotion_audio"),ObserveHeroAudioRequests(*G,*P,Observations.Num(),Start+Offset));
  O->SetObjectField(TEXT("action"),X);Observations.Add(MakeShared<FJsonValueObject>(O));Offsets.Add(MakeShared<FJsonValueNumber>(Offset));const int32 Index=Observations.Num()-1;
  if(!Need(V.RunGuid==Run&&V.OwnerId==Owner&&V.RoomInstanceId==Room&&G->GetRunPresentationEpoch()==Epoch&&G->GetRunRestartSerial()==Restart&&P->GetRuntimeEntityId()==Owner&&P->Health==InitialHP&&!P->bDead&&!G->bGameOver,TEXT("Owner/epoch/HP changed; no repair permitted"))||!Need(!H->GetInterfaceVisible()&&!H->IsCombatRangeDebugEnabled()&&H->GetRenderedTextDrawCalls()==0&&H->GetCombatRangeDebugLineCount()==0,TEXT("HUD/range visibility differs"))||(GearPinned&&!PinGear(P))){BeginStop(Actor);return;}
  if(Phase==5&&EIssued)
  {
   const auto& Equip=V.Action;
   if(Equip.Active)
   {
    if(!Need(Equip.Kind==EDungeonEquipmentActionKind::PickupArmor&&Equip.ActionId>0&&Equip.OperationId>0&&Equip.SourceId==LightSource&&Equip.InstanceId==Light&&Equip.Slot==2&&Equip.Start>=Inputs[EquipInputIndex]->AsObject()->GetNumberField(TEXT("sim"))&&Equip.Deadline==Equip.Start+.50&&Equip.Start<=G->GetSimulationTime()&&G->GetSimulationTime()<Equip.Deadline,TEXT("Actual E armor Action identity/Start/.50 Deadline differs"))){BeginStop(Actor);return;}
    if(EquipStartedIndex==INDEX_NONE){EquipStartedIndex=Index;EquipActionId=Equip.ActionId;EquipOperationId=Equip.OperationId;EquipStart=Equip.Start;EquipDeadline=Equip.Deadline;}
    if(!Need(Equip.ActionId==EquipActionId&&Equip.OperationId==EquipOperationId&&Equip.Start==EquipStart&&Equip.Deadline==EquipDeadline&&V.NextOperationId==EquipOperationId,TEXT("Observed E Action changed before commit"))){BeginStop(Actor);return;}
   }
   else if(EquipStartedIndex!=INDEX_NONE&&EquipCommitIndex==INDEX_NONE)
   {
    if(!Need(Equip.Kind==EDungeonEquipmentActionKind::PickupArmor&&Equip.ActionId==EquipActionId&&Equip.OperationId==EquipOperationId&&Equip.SourceId==LightSource&&Equip.InstanceId==Light&&Equip.Slot==2&&Equip.Start==EquipStart&&Equip.Deadline==EquipDeadline&&G->GetSimulationTime()>=EquipDeadline&&V.Slots[2].InstanceId==Light&&V.Slots[2].Version>0&&V.NextOperationId==EquipOperationId+1,TEXT("Actual E active-to-commit binding/timing/operation differs"))){BeginStop(Actor);return;}
    EquipCommitIndex=Index;
   }
  }
  const bool Fresh=B.DrawId>LastDraw&&B.SimulationTime==G->GetSimulationTime()&&B.DrawStack==H->GetRenderedPlayerDrawStack();if(!Fresh)return;LastDraw=B.DrawId;
  if(Phase==5&&GearPinned&&EquipCommitIndex!=INDEX_NONE&&Index>=EquipCommitIndex&&ReadyIndex==INDEX_NONE&&P->Facing==float(Side)&&P->JumpHeight==0.f&&P->GetVerticalVelocity()==0.f&&P->GetLandingVisualAge()==.12f&&Brown(B,false)&&!A.Drawn)ReadyIndex=Index;
  if(Phase==6&&Pose>=0&&!ActionActive)
  {
   if(!Need(QueryOK&&Q.Valid&&A.Drawn&&A.AtomicPreflightReady&&A.PlayerEntityId==Owner&&A.SimulationTime==G->GetSimulationTime()&&A.Plan.Frame==Pose&&A.Plan.Facing==Side&&A.Slots.Num()==9&&A.ResidentTextures.Num()==49&&A.ActualRenderedStack==B.DrawStack,TEXT("Real LGT Air callback lacks full current nine-layer draw"))){BeginStop(Actor);return;}
   if(Pose<4){AirMask|=1u<<Pose;if(P->JumpHeight>0.f||P->GetVerticalVelocity()>0.f)AirTransitions=1;}
   if(Pose==4&&LandIndex==INDEX_NONE){if(!Need(AirMask==15&&P->JumpHeight==0.f&&P->GetVerticalVelocity()==0.f&&M.Grounded&&P->GetWeaponActionsState().Budget.Grounded,TEXT("First real Land4 lacks four airborne poses/grounded budgets"))){BeginStop(Actor);return;}LandIndex=Index;}
  }
  if(LandConsumed&&ActionActive)
  {
   if(FirstActionIndex==INDEX_NONE)
   {ActualActionId=ActionId;ActionStart=Action==TEXT("J")?M.Action.Start:Roll?Roll->Start:-1.;ActionEnd=Action==TEXT("J")?M.Action.End:Roll?Roll->End:-1.;const auto Land=Observations[LandIndex]->AsObject();StartLandingAge=Land->GetNumberField(TEXT("landing_visual_age"))+ActionStart-Land->GetNumberField(TEXT("sim"));FirstActionIndex=Index;
    if(!Need(ActualActionId>PriorActionId&&ActionStart>=Inputs[InputIndex]->AsObject()->GetNumberField(TEXT("sim"))&&ActionStart<=G->GetSimulationTime()&&StartLandingAge>=0.&&StartLandingAge<.12&&M.Grounded&&P->GetWeaponActionsState().Budget.Grounded&&P->JumpHeight==0.f&&P->GetVerticalVelocity()==0.f,TEXT("Actual action Start missed original landing or grounded identity"))){BeginStop(Actor);return;}}
   if(!Need(ActionId==ActualActionId&&!QueryOK&&SameSample(Q,Sentinel)&&!A.Drawn&&A.Slots.Num()==0&&A.ActualRenderedStack.Num()==0&&B.Facing==Side,TEXT("Action failed to preempt Air atomically"))){BeginStop(Actor);return;}
   if(Action==TEXT("J"))
   {if(!Need(Brown(B,true)&&!M.Action.StartedAirborne&&M.Action.Stage==0&&B.ActionId==ActualActionId&&B.ActionStart==ActionStart&&B.InstanceId==Sword,TEXT("Grounded real Primary1 brown draw differs"))){BeginStop(Actor);return;}PrimaryMask|=1u<<B.Frame;}
   else
   {if(!Need(D.Drawn&&D.AtomicPreflightReady&&D.SimulationTime==G->GetSimulationTime()&&D.PlayerEntityId==Owner&&D.Plan.Dodge.ActionId==ActualActionId&&D.Plan.Dodge.Start==ActionStart&&D.Plan.Dodge.End==ActionEnd&&D.Plan.Facing==Side&&D.Plan.Frame>=0&&D.Plan.Frame<4&&D.Slots.Num()==9&&D.ResidentTextures.Num()==33&&D.ActualRenderedStack==B.DrawStack&&B.Clip==TEXT("sword_dodge"),TEXT("Actual Dodge nine-layer/33-resource action differs"))){BeginStop(Actor);return;}DodgeMask|=1u<<D.Plan.Frame;}
  }
  if(FirstActionIndex!=INDEX_NONE&&!ActionActive&&Brown(B,false)&&!A.Drawn&&P->GetLandingVisualAge()==.12f)
  {
   if(Action==TEXT("Shift")&&!Need(Roll&&Roll->ActionId==ActualActionId&&Roll->Finish==DungeonDodge::EFinish::Completed&&Roll->FinishedAt==ActionEnd&&Roll->End==Roll->Start+DungeonDodge::Duration,TEXT("Real Dodge did not complete its unchanged .40 duration"))){BeginStop(Actor);return;}
   ++ReadyJoinFrames;if(ReadyJoinFrames>=2){FlowComplete=Need(EquipStartedIndex!=INDEX_NONE&&EquipCommitIndex!=INDEX_NONE&&ReadyIndex>=EquipCommitIndex&&AirMask==15&&ReadyConsumed&&LandConsumed&&JumpInputs==1&&(Action==TEXT("J")?PrimaryMask==63:DodgeMask==15),TEXT("Incomplete real Air/action/Ready pose coverage"));CaptureFinalHP=P->Health;BeginStop(Actor);}
  }
 }
 void Finalize(ADungeonHeroLandingPriorityProbeV001& Actor)
 {
  if(Stopped)return;Stopped=true;GIsDumpingMovie=0;ReleaseKeys();const bool Flushed=FlushFastLosslessProofScreenshots();const bool AudioComplete=Actor.MainMixCapture&&Actor.MainMixCapture->Status().Phase==EDungeonNativeMixCapturePhaseV001::Complete;
  auto R=MakeShared<FJsonObject>();R->SetStringField(TEXT("schema"),TEXT("hero-landing-priority-native-observer-v001"));R->SetStringField(TEXT("requested_action"),Action);R->SetNumberField(TEXT("requested_facing"),Side);R->SetBoolField(TEXT("passed"),Failure.IsEmpty()&&FlowComplete&&Flushed&&AudioComplete&&StartupReadbackComplete&&Start>StartupReadbackStop);R->SetBoolField(TEXT("flow_complete"),FlowComplete);R->SetStringField(TEXT("failure"),Failure);R->SetBoolField(TEXT("final_accepted"),false);R->SetBoolField(TEXT("visual_reviewed"),false);R->SetBoolField(TEXT("audio_listened"),false);R->SetStringField(TEXT("real_save_restore"),TEXT("OPEN_not_run"));R->SetBoolField(TEXT("player_Guard_HP_position_AI_time_writes"),false);
  Id(R,TEXT("process_id"),FPlatformProcess::GetCurrentProcessId());R->SetStringField(TEXT("run"),Run.ToString(EGuidFormats::Digits));Id(R,TEXT("owner"),Owner);Id(R,TEXT("current_room"),Room);Id(R,TEXT("epoch"),Epoch);Id(R,TEXT("restart_serial"),Restart);Id(R,TEXT("weapon_instance"),Sword);Id(R,TEXT("weapon_version"),SwordVersion);Id(R,TEXT("armor_instance"),Light);Id(R,TEXT("armor_version"),LightVersion);
  Id(R,TEXT("light_source_id"),LightSource);R->SetNumberField(TEXT("equipment_input_index"),EquipInputIndex);R->SetNumberField(TEXT("equipment_started_callback_index"),EquipStartedIndex);R->SetNumberField(TEXT("equipment_commit_callback_index"),EquipCommitIndex);R->SetNumberField(TEXT("equipment_start"),EquipStart);R->SetNumberField(TEXT("equipment_deadline"),EquipDeadline);
  R->SetNumberField(TEXT("initial_hp"),InitialHP);R->SetNumberField(TEXT("capture_final_hp"),CaptureFinalHP);R->SetNumberField(TEXT("ready_callback_index"),ReadyIndex);R->SetNumberField(TEXT("landing_callback_index"),LandIndex);R->SetNumberField(TEXT("priority_input_index"),InputIndex);R->SetNumberField(TEXT("first_action_callback_index"),FirstActionIndex);R->SetNumberField(TEXT("action_start"),ActionStart);R->SetNumberField(TEXT("action_end"),ActionEnd);R->SetNumberField(TEXT("action_start_landing_age"),StartLandingAge);R->SetNumberField(TEXT("air_mask"),AirMask);R->SetNumberField(TEXT("primary_mask"),PrimaryMask);R->SetNumberField(TEXT("dodge_mask"),DodgeMask);R->SetNumberField(TEXT("ready_join_frames"),ReadyJoinFrames);
  R->SetBoolField(TEXT("request258_primary1_bridge_optin"),Bridge258ObservationEnabled());
  R->SetStringField(TEXT("request258_primary1_bridge_source_contract_sha256"),TEXT("f85284dc25d0a5f0be5bf09aa7b9f7dbdf2a62bccbb61e4ca0c5ce0ef1238f6e"));
  TArray<JV> Bridge258Pins;
  if(Bridge258ObservationEnabled())for(const auto& Pin:Bridge258SourcePins)
  {auto S=MakeShared<FJsonObject>();S->SetNumberField(TEXT("frame"),Pin.Frame);S->SetStringField(TEXT("component"),Pin.Component);S->SetStringField(TEXT("object_path"),Pin.ObjectPath);S->SetStringField(TEXT("source_png"),Pin.SourcePNG);Id(S,TEXT("source_png_bytes"),Pin.SourceBytes);S->SetStringField(TEXT("source_png_sha256"),Pin.SourceSHA256);Bridge258Pins.Add(MakeShared<FJsonValueObject>(S));}
  R->SetArrayField(TEXT("request258_primary1_bridge_source_pins"),Bridge258Pins);
  auto LegacyResidency=MakeShared<FJsonObject>();LegacyResidency->SetStringField(TEXT("schema"),TEXT("request258-old14-residency-diagnostics-v003"));
  LegacyResidency->SetBoolField(TEXT("requested"),Bridge258ObservationEnabled()&&Action==TEXT("J"));LegacyResidency->SetBoolField(TEXT("finish_compilation_requested"),Bridge258LegacyFinishRequested);LegacyResidency->SetNumberField(TEXT("finish_target_count"),Bridge258LegacyFinishTargetCount);
  LegacyResidency->SetArrayField(TEXT("before_finish"),Bridge258LegacyResidencyBefore);LegacyResidency->SetArrayField(TEXT("after_finish_and_render_flush"),Bridge258LegacyResidencyAfter);
  LegacyResidency->SetBoolField(TEXT("diagnostics_replace_strict_GPU_source_capture"),false);R->SetObjectField(TEXT("request258_primary1_legacy_residency"),LegacyResidency);
  R->SetObjectField(TEXT("hero_locomotion_audio"),FinalHeroAudioRequests());
  R->SetArrayField(TEXT("normal_inputs"),Inputs);R->SetArrayField(TEXT("steps"),Steps);R->SetArrayField(TEXT("observations"),Observations);R->SetArrayField(TEXT("diagnostic_knight_hits"),DiagnosticHits);R->SetArrayField(TEXT("startup_resource_readbacks"),StartupTextures);TArray<JV> Air49;for(int32 I=0;I<FMath::Min(49,StartupTextures.Num());++I)Air49.Add(StartupTextures[I]);R->SetArrayField(TEXT("startup_actual_GPU_source_textures49"),Air49);R->SetBoolField(TEXT("startup_readback_complete"),StartupReadbackComplete);R->SetNumberField(TEXT("startup_readback_stop_monotonic_s"),StartupReadbackStop);R->SetBoolField(TEXT("native_async_capture_writes_flushed"),Flushed);
  auto Timing=MakeShared<FJsonObject>();Timing->SetBoolField(TEXT("use_fixed_time_step"),FApp::UseFixedTimeStep());Timing->SetNumberField(TEXT("capture_start_monotonic_s"),Start);Timing->SetNumberField(TEXT("capture_stop_monotonic_s"),Stop);Timing->SetArrayField(TEXT("frame_wall_offsets_s"),Offsets);R->SetObjectField(TEXT("capture_timing"),Timing);if(Actor.MainMixCapture)R->SetObjectField(TEXT("main_submix_capture"),Actor.MainMixCapture->SerializeReport());FString Text;auto Writer=TJsonWriterFactory<>::Create(&Text);const bool Serialized=FJsonSerializer::Serialize(R,Writer);const bool Written=Serialized&&EvidenceClaimed&&WriteNewUTF8(Directory/TEXT("runtime-report.json"),Text);if(!Failure.IsEmpty())UE_LOG(LogTemp,Error,TEXT("Landing priority: %s"),*Failure);FPlatformMisc::RequestExitWithStatus(false,Failure.IsEmpty()&&FlowComplete&&Flushed&&AudioComplete&&Written?0:3);
 }
 void Tick(ADungeonHeroLandingPriorityProbeV001& Actor)
 {
  if(Stopped)return;const double Now=FPlatformTime::Seconds();if(Actor.MainMixCapture)Actor.MainMixCapture->Poll();if(Stopping){if(!Actor.MainMixCapture||Actor.MainMixCapture->IsTerminal())Finalize(Actor);return;}if(!Failure.IsEmpty()){BeginStop(Actor);return;}
  auto W=Actor.GetWorld();auto G=W?W->GetAuthGameMode<ADungeonGameMode>():nullptr;auto C=UGameplayStatics::GetPlayerController(&Actor,0);auto H=C?Cast<ADungeonHUD>(C->GetHUD()):nullptr;
  if(!Game.IsValid()&&Now-WarmStarted>12.){Need(false,TEXT("Startup owner timeout"));BeginStop(Actor);return;}
  if(!Game.IsValid()&&G&&C&&C->PlayerInput&&H){auto P=G->PlayerFighter.Get();const auto& V=G->GetEquipmentView();if(!P||!V.Bound||!V.RunGuid.IsValid()||V.ActiveSlot<0||V.ActiveSlot>=3)return;Game=G;Controller=C;HUD=H;Run=V.RunGuid;Owner=V.OwnerId;Room=V.RoomInstanceId;Epoch=G->GetRunPresentationEpoch();Restart=G->GetRunRestartSerial();InitialHP=P->Health;Sword=V.Slots[V.ActiveSlot].InstanceId;SwordVersion=V.Slots[V.ActiveSlot].Version;Actor.AddTickPrerequisiteActor(G);Actor.AddTickPrerequisiteActor(H);return;}
  if(!Game.IsValid())return;if(PulseKey.IsValid()&&Now>=ReleaseAt){Key(PulseKey,false);PulseKey=FKey();NeutralUntil=Now+.04;}
  if(!Capturing){if(!StartupReadbackComplete){CaptureTextureBytesBeforeAudio();return;}if(!PrewarmRequested){PrewarmRequested=true;FScreenshotRequest::RequestScreenshot(Directory/TEXT("prewarm-viewport.png"),false,false,false);}if(PrewarmDone&&!AudioRequested){AudioRequested=true;Actor.MainMixCapture=NewObject<UDungeonNativeMainSubmixCaptureV001>(&Actor);if(!Actor.MainMixCapture->Begin(Actor.GetWorld(),Directory/TEXT("audio-v001")))Need(false,TEXT("Native mix Arming rejected"));}if(AudioRequested&&Actor.MainMixCapture&&Actor.MainMixCapture->Status().Phase==EDungeonNativeMixCapturePhaseV001::Recording){const auto& Status=Actor.MainMixCapture->Status();if(!Need(Status.StartRequested&&Status.StartMonotonic>0.,TEXT("Actual recording origin absent")))return;Start=Status.StartMonotonic;Capturing=true;GIsDumpingMovie=-1;Next(0);}if(Now-WarmStarted>45.)Need(false,TEXT("Prewarm/audio startup timeout"));return;}
  auto P=G?G->PlayerFighter.Get():nullptr;if(!Need(G&&C&&H&&P&&G==Game.Get()&&C==Controller.Get()&&H==HUD.Get()&&C->GetPawn()==P&&C->IsLocalController()&&Now-Start<12.&&Now-PhaseAt<5.,TEXT("Native owner/phase timeout")))return;FDungeonFirstBatchGuardRoomView View;if(!Need(G->QueryFirstBatchGuardRoom(View)&&View.Slots.Num()==3,TEXT("Real finite FirstBatch room required")))return;
  switch(Phase){
   case 0:if(!Need(G->bWaitingForStart&&G->GetSimulationTime()==0.,TEXT("Normal Enter must start waiting run")))return;if(Pulse(EKeys::Enter))Next(1);break;
   case 1:if(!G->bWaitingForStart&&CanPulse()&&ClearKnightIfRequested(P,View)){Key(EKeys::D,true);Next(2);}break;
   case 2:if(P->GetGroundPosition().X>=DungeonRoomLayout::ExplorationPreview().Entry.X+280.){Key(EKeys::D,false);NeutralUntil=Now+.04;Next(3);}break;
   case 3:if(CanPulse()&&Pulse(Side<0?EKeys::A:EKeys::D))Next(4);break;
   case 4:if(CanPulse()&&P->Facing==float(Side)){DungeonEquipmentInventory::FItem I;I.ContentId="ARM-LGT-001";const auto Registered=G->RegisterEquipmentSource(TEXT("display.hero.landing.priority.light.v001"),I,P->GetGroundPosition()+FVector2D(24.,0.),true);if(!Need(Registered.Ok()&&!Registered.Replayed,TEXT("Real display source registration rejected")))return;LightSource=Registered.SourceId;Light=Registered.InstanceId;Next(5);}break;
   case 5:if(!EIssued){if(CanPulse()&&G->GetEquipmentView().SelectedSourceId==LightSource){EquipInputIndex=Inputs.Num();if(Pulse(EKeys::E))EIssued=true;}break;}if(!G->GetEquipmentView().Action.Active&&G->GetEquipmentView().Slots[2].InstanceId==Light&&PinGear(P)&&CanPulse()&&ReadyIndex!=INDEX_NONE){const auto R=Observations[ReadyIndex]->AsObject();if(!Need(!ReadyConsumed&&R->GetNumberField(TEXT("sim"))<=G->GetSimulationTime()&&Now-Start>R->GetNumberField(TEXT("wall_offset_s")),TEXT("Ready callback token stale/reused")))return;if(Pulse(EKeys::SpaceBar)){ReadyConsumed=true;++JumpInputs;Next(6);}}break;
   case 6:if(LandIndex!=INDEX_NONE&&CanPulse()){const auto Land=Observations[LandIndex]->AsObject();if(!Need(!LandConsumed&&Now-Start>Land->GetNumberField(TEXT("wall_offset_s"))&&P->JumpHeight==0.f&&P->GetVerticalVelocity()==0.f&&P->GetLandingVisualAge()>=0.f&&P->GetLandingVisualAge()<.12f,TEXT("Normal priority input missed actual landing window")))return;PriorActionId=Action==TEXT("J")?P->GetMeleeCombatState().Action.AttackId:P->GetDodgeState().Records.empty()?0:P->GetDodgeState().Records.back().ActionId;InputIndex=Inputs.Num();if(Pulse(Action==TEXT("J")?EKeys::J:EKeys::LeftShift)){LandConsumed=true;Next(7);}}break;
   case 7:break;default:Need(false,TEXT("Unexpected observer phase"));break;
  }
 }
};

void FDungeonHeroLandingPriorityProofDeleterV001::operator()(FDungeonHeroLandingPriorityProofStateV001* P)const{delete P;}
ADungeonHeroLandingPriorityProbeV001::ADungeonHeroLandingPriorityProbeV001(){PrimaryActorTick.bCanEverTick=true;}
ADungeonHeroLandingPriorityProbeV001::~ADungeonHeroLandingPriorityProbeV001()=default;
void ADungeonHeroLandingPriorityProbeV001::BeginPlay()
{
 Super::BeginPlay();Proof.Reset(new FDungeonHeroLandingPriorityProofStateV001);Proof->WarmStarted=FPlatformTime::Seconds();FParse::Value(FCommandLine::Get(),TEXT("DungeonContentProofDir="),Proof->Directory);FParse::Value(FCommandLine::Get(),TEXT("DungeonHeroLandingPriorityFacing="),Proof->Side);FParse::Value(FCommandLine::Get(),TEXT("DungeonHeroLandingPriorityAction="),Proof->Action);Proof->AllowKnightDiagnostic=FParse::Param(FCommandLine::Get(),TEXT("DungeonHeroLandingPriorityClearKnightDiagnostic"));
 if(!Proof->Need(!Proof->Directory.IsEmpty()&&!FPaths::IsRelative(Proof->Directory)&&(Proof->Side==-1||Proof->Side==1)&&(Proof->Action==TEXT("J")||Proof->Action==TEXT("Shift")),TEXT("Absolute unused directory and exact J/Shift/facing CLI required")))return;Proof->Directory=FPaths::ConvertRelativePathToFull(Proof->Directory);FPaths::NormalizeDirectoryName(Proof->Directory);IFileManager::Get().MakeDirectory(*Proof->Directory,true);TArray<FString> Prior;IFileManager::Get().FindFiles(Prior,*(Proof->Directory/TEXT("*")),true,false);Prior.Remove(TEXT("native-lossless-capture.json"));TArray<FString> Subdirs;IFileManager::Get().FindFiles(Subdirs,*(Proof->Directory/TEXT("*")),false,true);if(!Proof->Need(Prior.Num()==0&&Subdirs.Num()==0,TEXT("Evidence directory already occupied")))return;
 if(!Proof->Need(WriteNewUTF8(Proof->Directory/TEXT("observer-process-claim-v001.json"),FString::Printf(TEXT("{\"schema\":\"hero-landing-priority-process-claim-v001\",\"process_id\":\"%u\"}"),FPlatformProcess::GetCurrentProcessId())),TEXT("Exclusive process claim failed")))return;Proof->EvidenceClaimed=true;
 for(const TCHAR* Flag:{TEXT("DungeonHeroLandingPriorityProofV001"),TEXT("DungeonContentProof"),TEXT("DungeonFastLosslessCapture"),TEXT("DungeonAsyncLosslessCapture"),TEXT("DungeonCandidateSprites"),TEXT("DungeonFairytaleSwordEquipmentBoundPreview"),TEXT("DungeonFairytaleLeatherReadyPreview"),TEXT("DungeonFairytaleLeatherPrimary1Preview"),TEXT("DungeonFairytaleLeatherPrimary2Preview"),TEXT("DungeonFairytaleLeatherPrimary3Preview"),TEXT("DungeonFairytaleSwordWalkPreview"),TEXT("DungeonFairytaleSwordHurtPreview"),TEXT("DungeonFairytaleSwordDeathPreview"),TEXT("DungeonFairytaleSwordDodgePreview"),TEXT("DungeonFairytaleSwordAirPreview"),TEXT("DungeonFairytaleGuardFullPreview"),TEXT("DungeonFairytaleGuardStompPreview"),TEXT("DungeonFairytaleGuardMoveRigPreview")})if(!Proof->Need(FParse::Param(FCommandLine::Get(),Flag),TEXT("Required existing brown-art/capture flag missing: ")+FString(Flag)))return;
 for(const TCHAR* Flag:{TEXT("DungeonProof"),TEXT("DungeonHeroAirProductionProofV001"),TEXT("DungeonHeroAirProofV001"),TEXT("DungeonHeroDodgeProofV001"),TEXT("DungeonHeroHurtProofV001"),TEXT("DungeonHeroDeathProofV001"),TEXT("DungeonGuardMoveProofV001"),TEXT("DungeonGuardStompProofV001"),TEXT("DungeonGuardArtCombatProofV003"),TEXT("DungeonGuardArtDeathProofV005"),TEXT("DungeonGuardArtKnown44Proof"),TEXT("DungeonGuardArtPartialProof"),TEXT("DungeonGuardRoomFlowProof"),TEXT("DungeonGuardRoomManualLightSource"),TEXT("DungeonFairytaleWalkProof"),TEXT("DungeonFairytaleEquipmentBoundProof"),TEXT("DungeonFairytaleSwordBodyProof"),TEXT("DungeonRunSaveProof"),TEXT("DungeonRunRestoreProof"),TEXT("DungeonGuardRunSaveProof"),TEXT("DungeonGuardRunRestoreProof"),TEXT("DungeonFairytaleLookdevProof"),TEXT("DungeonFairytaleLookdevPreview"),TEXT("DungeonCombatRangeDebug"),TEXT("DungeonCombatRangeProof"),TEXT("DungeonShowInterface")})if(!Proof->Need(!FParse::Param(FCommandLine::Get(),Flag),TEXT("Other proof/HUD/range flag cannot share observer")))return;
 for(TActorIterator<ADungeonContentProbe> It(GetWorld());It;++It)if(IsValid(*It)){Proof->Need(false,TEXT("Old ContentProbe already running"));return;}if(!Proof->Need(!FApp::UseFixedTimeStep(),TEXT("Native variable pacing required")))return;GetMutableDefault<UEngine>()->GameScreenshotSaveDirectory.Path=Proof->Directory;FScreenshotRequest::OnScreenshotRequestProcessed().AddUObject(this,&ADungeonHeroLandingPriorityProbeV001::ScreenshotProcessed);
}
void ADungeonHeroLandingPriorityProbeV001::ScreenshotProcessed(){if(Proof)Proof->Observe(*this);}
void ADungeonHeroLandingPriorityProbeV001::Tick(float D){Super::Tick(D);if(Proof)Proof->Tick(*this);}
void ADungeonHeroLandingPriorityProbeV001::EndPlay(const EEndPlayReason::Type R)
{FScreenshotRequest::OnScreenshotRequestProcessed().RemoveAll(this);if(Proof&&!Proof->Stopped){Proof->Need(false,TEXT("Landing priority world ended before capture/export completed"));GIsDumpingMovie=0;if(MainMixCapture&&!MainMixCapture->IsTerminal())MainMixCapture->Abort(TEXT("Landing priority world ended before export completed"));Proof->BeginStop(*this);Proof->Finalize(*this);}Super::EndPlay(R);}
