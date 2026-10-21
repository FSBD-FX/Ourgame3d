#pragma once
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
