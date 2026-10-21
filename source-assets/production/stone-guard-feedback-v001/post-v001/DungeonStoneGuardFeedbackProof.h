#pragma once
// Optional read-only native proof export. Root calls once at its real probe completion.
// Does not claim captured device audio or validated visual/timbre acceptance.
#include "DungeonGameMode.h"
#include "DungeonHUD.h"
#include "Engine/World.h"
#include "Dom/JsonObject.h"
#include "Serialization/JsonSerializer.h"
#include "Serialization/JsonWriter.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"
#include "HAL/FileManager.h"
#include "HAL/PlatformProcess.h"
namespace DungeonGuardFeedbackProof
{
inline TSharedRef<FJsonObject> Source(const DungeonGuardFeedback::FRecord& R)
{
 auto J=MakeShared<FJsonObject>();J->SetStringField(TEXT("sequence"),LexToString(uint64(R.Sequence)));
 J->SetStringField(TEXT("event_id"),LexToString(uint64(R.EventId)));J->SetStringField(TEXT("entity_id"),LexToString(uint64(R.EntityId)));
 J->SetStringField(TEXT("attack_id"),LexToString(uint64(R.AttackId)));J->SetStringField(TEXT("target_id"),LexToString(uint64(R.TargetId)));
 J->SetStringField(TEXT("foot_ordinal"),LexToString(uint64(R.FootOrdinal)));J->SetNumberField(TEXT("source_kind"),int32(R.SourceKind));
 J->SetNumberField(TEXT("at_time"),R.AtTime);J->SetNumberField(TEXT("actual_hp_loss"),R.ActualHPLoss);J->SetNumberField(TEXT("facing"),R.Facing);
 J->SetNumberField(TEXT("world_x"),R.Position.X);J->SetNumberField(TEXT("world_y"),R.Position.Y);J->SetNumberField(TEXT("world_z"),R.Position.Z);
 return J;
}
inline bool WriteNativeRequests(const ADungeonGameMode& Game,const ADungeonHUD& HUD,const FString& Filename,FString& Why)
{
 if(!IsInGameThread()||!Game.GetWorld()||HUD.GetWorld()!=Game.GetWorld()||FPaths::IsRelative(Filename))
 {Why=TEXT("Require actual matching native world, game thread and absolute fresh filename");return false;}
 if(IFileManager::Get().FileExists(*Filename)||HUD.GetGuardAudioPlayReceipts().IsEmpty())
 {Why=TEXT("Preserve existing report; actual nonempty play-request receipts required");return false;}
 auto O=MakeShared<FJsonObject>();O->SetStringField(TEXT("schema"),TEXT("guard-feedback-native-request-report-v1"));
 O->SetBoolField(TEXT("native_requests"),true);O->SetBoolField(TEXT("recorded_engine_audio"),false);O->SetBoolField(TEXT("audio_device_auditioned"),false);
 O->SetBoolField(TEXT("visual_feedback_accepted"),false);O->SetBoolField(TEXT("final_mix_accepted"),false);
 O->SetBoolField(TEXT("windup_stop_clock_captured"),false);O->SetStringField(TEXT("run_guid"),Game.GetEquipmentView().RunGuid.ToString(EGuidFormats::DigitsWithHyphens));
 O->SetStringField(TEXT("room_instance_id"),LexToString(Game.GetEquipmentView().RoomInstanceId));O->SetStringField(TEXT("process_id"),LexToString(FPlatformProcess::GetCurrentProcessId()));
 O->SetNumberField(TEXT("simulation_time"),Game.GetSimulationTime());TArray<TSharedPtr<FJsonValue>> Audio,Fx;
 for(const auto& R:HUD.GetGuardAudioPlayReceipts())
 {
  auto J=Source(R.Source);J->SetStringField(TEXT("cue"),R.Cue);J->SetStringField(TEXT("sound_path"),R.SoundPath);
  J->SetNumberField(TEXT("requested_at"),R.RequestedAt);J->SetNumberField(TEXT("volume"),R.Volume);J->SetNumberField(TEXT("pitch"),R.Pitch);
  Audio.Add(MakeShared<FJsonValueObject>(J));
 }
 for(const auto& R:HUD.GetGuardEffectSpawnRequests())
 {
  auto J=Source(R.Source);J->SetNumberField(TEXT("effect"),int32(R.Source.Effect));J->SetNumberField(TEXT("started_at"),R.StartedAt);J->SetNumberField(TEXT("expires_at"),R.ExpiresAt);
  Fx.Add(MakeShared<FJsonValueObject>(J));
 }
 O->SetArrayField(TEXT("requests"),Audio);O->SetArrayField(TEXT("effect_requests"),Fx);FString Text;
 auto Writer=TJsonWriterFactory<>::Create(&Text);if(!FJsonSerializer::Serialize(O,Writer)){Why=TEXT("Native request JSON failed");return false;}
 if(!IFileManager::Get().MakeDirectory(*FPaths::GetPath(Filename),true)
   ||!FFileHelper::SaveStringToFile(Text,*Filename,FFileHelper::EEncodingOptions::ForceUTF8WithoutBOM,&IFileManager::Get(),FILEWRITE_NoReplaceExisting))
 {Why=TEXT("Native request report fresh write failed");return false;}
 Why.Reset();return true;
}
}
