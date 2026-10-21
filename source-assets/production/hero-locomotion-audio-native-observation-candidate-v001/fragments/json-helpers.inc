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
