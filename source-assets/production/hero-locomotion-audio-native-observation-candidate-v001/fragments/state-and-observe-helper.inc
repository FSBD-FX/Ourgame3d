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
