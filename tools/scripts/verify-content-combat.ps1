param(
    [string]$EngineRoot='G:\UE_5.5',
    [ValidatePattern('^v[0-9]+$')][string]$Version='v001',
    [string]$InspectArchive='',
    [switch]$CandidateSprites,
    [switch]$FirstUnit,
    [switch]$FirstUnitSkill,
    [switch]$FirstUnitExplore,
    [switch]$EquipmentAdapter,
    [switch]$ArmorLayers,
    [switch]$ArmorComboLayers,
    [switch]$ArmorSleevesLayers,
    [switch]$RangedWeapons,
    [switch]$XBWReadyBody,
    [switch]$XBWHeldIdentity,
    [switch]$XBWPrimaryBody,
    [switch]$SceneExploration,
    [switch]$XBWReloadSocket,
    [switch]$XBWArmorSocket,
    [switch]$FastLosslessCapture,
    [switch]$AsyncLosslessCapture,
    [ValidateRange(30,300)][int]$ProcessTimeoutSeconds=90
)
$ErrorActionPreference='Stop'
if($AsyncLosslessCapture -and -not $FastLosslessCapture){throw 'AsyncLosslessCapture requires FastLosslessCapture.'}
if($XBWArmorSocket -and ($FirstUnit -or $FirstUnitSkill -or $FirstUnitExplore -or $EquipmentAdapter -or $ArmorLayers -or $ArmorComboLayers -or $ArmorSleevesLayers -or $RangedWeapons -or $XBWReadyBody -or $XBWHeldIdentity -or $XBWPrimaryBody -or $SceneExploration -or $XBWReloadSocket)){throw 'XBWArmorSocket is an independent proof profile.'}
if($XBWArmorSocket -and -not $CandidateSprites){throw 'XBWArmorSocket requires CandidateSprites.'}
if($XBWReloadSocket -and ($FirstUnit -or $FirstUnitSkill -or $FirstUnitExplore -or $EquipmentAdapter -or $ArmorLayers -or $ArmorComboLayers -or $ArmorSleevesLayers -or $RangedWeapons -or $XBWReadyBody -or $XBWHeldIdentity -or $XBWPrimaryBody -or $SceneExploration)){throw 'XBWReloadSocket is an independent proof profile.'}
if($XBWReloadSocket -and -not $CandidateSprites){throw 'XBWReloadSocket requires CandidateSprites.'}
if($SceneExploration -and ($FirstUnit -or $FirstUnitSkill -or $FirstUnitExplore -or $EquipmentAdapter -or $ArmorLayers -or $ArmorComboLayers -or $ArmorSleevesLayers -or $RangedWeapons -or $XBWReadyBody -or $XBWHeldIdentity -or $XBWPrimaryBody)){throw 'SceneExploration is an independent proof profile.'}
if($SceneExploration -and -not $CandidateSprites){throw 'SceneExploration requires CandidateSprites.'}
$ArmorComboLayers=$ArmorComboLayers -or $ArmorSleevesLayers
$XBWHeldIdentity=$XBWHeldIdentity -or $XBWPrimaryBody
$XBWReadyBody=$XBWReadyBody -or $XBWHeldIdentity
$RangedWeapons=$RangedWeapons -or $XBWReadyBody
$ArmorLayers=$ArmorLayers -or $ArmorComboLayers
if($RangedWeapons -and ($ArmorLayers -or $EquipmentAdapter -or $FirstUnit -or $FirstUnitSkill -or $FirstUnitExplore)){throw 'RangedWeapons is an independent proof profile.'}
if($RangedWeapons -and -not $CandidateSprites){throw 'RangedWeapons requires CandidateSprites for the actual presentation evidence.'}
if($EquipmentAdapter -and ($FirstUnit -or $FirstUnitSkill -or $FirstUnitExplore)){throw 'EquipmentAdapter is an independent proof profile; do not combine old unit flags.'}
if($ArmorLayers -and ($EquipmentAdapter -or $FirstUnit -or $FirstUnitSkill -or $FirstUnitExplore)){throw 'ArmorLayers is an independent proof profile.'}
if($ArmorLayers -and -not $CandidateSprites){throw 'ArmorLayers requires actual CandidateSprites.'}

function Read-GameMixWav([string]$Path) {
    $result=[ordered]@{path=$Path;complete_decode=$false;non_silent=$false;error='';source='PCM file validation only; runtime origin additionally requires the UE export receipt in the same archive'}
    if(-not (Test-Path -LiteralPath $Path -PathType Leaf)) {$result.error='runtime_mix_missing';return $result}
    $reader=$null
    try {
        $raw=[IO.File]::ReadAllBytes($Path)
        if($raw.Length -lt 44){throw 'WAV shorter than a PCM header'}
        $reader=[IO.BinaryReader]::new([IO.MemoryStream]::new($raw,$false))
        if([Text.Encoding]::ASCII.GetString($reader.ReadBytes(4)) -ne 'RIFF'){throw 'Not RIFF'}
        [long]$riffEnd=[long]$reader.ReadUInt32()+8
        if($riffEnd -ne $raw.Length){throw 'Incomplete RIFF payload or trailing bytes'}
        if([Text.Encoding]::ASCII.GetString($reader.ReadBytes(4)) -ne 'WAVE'){throw 'Not WAVE'}
        $format=$null;$channels=0;$rate=0;$align=0;$bits=0;$byteRate=0
        [long]$dataOffset=-1;[long]$dataBytes=0
        while($reader.BaseStream.Position+8 -le $riffEnd) {
            $chunk=[Text.Encoding]::ASCII.GetString($reader.ReadBytes(4))
            [long]$length=$reader.ReadUInt32();[long]$start=$reader.BaseStream.Position
            if($start+$length -gt $riffEnd){throw "Incomplete WAV chunk: $chunk"}
            if($chunk -eq 'fmt ') {
                if($length -lt 16){throw 'Incomplete format chunk'}
                $format=$reader.ReadUInt16();$channels=$reader.ReadUInt16();$rate=$reader.ReadUInt32()
                $byteRate=$reader.ReadUInt32();$align=$reader.ReadUInt16();$bits=$reader.ReadUInt16()
            }
            if($chunk -eq 'data') {
                if($dataOffset -ge 0){throw 'Unexpected multiple PCM payloads'}
                $dataOffset=$start;$dataBytes=$length
            }
            $reader.BaseStream.Position=$start+$length+($length%2)
        }
        if($reader.BaseStream.Position -ne $riffEnd){throw 'Incomplete WAV chunk boundary'}
        if($format -ne 1 -or $bits -ne 16){throw 'Expected the UE WavFile export signed PCM16 format'}
        if($channels -lt 1 -or $channels -gt 8 -or $rate -lt 8000 -or $rate -gt 192000){throw 'Invalid PCM rate/channels'}
        if($align -ne $channels*2 -or $byteRate -ne $rate*$align){throw 'Invalid PCM alignment/byte rate'}
        if($dataOffset -lt 0 -or $dataBytes -le 0 -or $dataBytes%$align -ne 0){throw 'Missing or incomplete PCM samples'}
        $samples=[Int16[]]::new([int]($dataBytes/2))
        [Buffer]::BlockCopy($raw,[int]$dataOffset,$samples,0,[int]$dataBytes)
        [double]$sumSquares=0;[int]$peak=0;[long]$nonzero=0;[long]$clipped=0
        foreach($sample in $samples) {
            [int]$absolute=[Math]::Abs([int]$sample)
            if($absolute -gt $peak){$peak=$absolute}
            if($absolute -gt 0){$nonzero++}
            if($absolute -ge 32767){$clipped++}
            $sumSquares+=[double]$sample*[double]$sample
        }
        [double]$peakLinear=$peak/32768.0
        [double]$rms=[Math]::Sqrt($sumSquares/$samples.Length)/32768.0
        $result['complete_decode']=$true
        $result['non_silent']=$peakLinear -ge 0.001 -and $rms -ge 0.00001
        $result['non_silence_rule']='sample peak >= -60dBFS and whole-file RMS >= -100dBFS; not listening acceptance'
        $result['sample_rate_hz']=$rate;$result['channels']=$channels;$result['pcm_bits']=$bits
        $result['frames']=[long]($dataBytes/$align);$result['decoded_samples']=$samples.Length
        $result['duration_s']=$dataBytes/[double]$byteRate;$result['bytes']=$raw.Length
        $result['sample_peak_dbfs']=if($peak -gt 0){20*[Math]::Log10($peakLinear)}else{$null}
        $result['rms_dbfs']=if($rms -gt 0){20*[Math]::Log10($rms)}else{$null}
        $result['nonzero_samples']=$nonzero;$result['fullscale_samples']=$clipped
        $result['sha256']=(Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash
        if(-not $result.non_silent){$result.error='runtime_mix_silent_or_below_recorded_signal_threshold'}
    } catch {$result.error=$_.Exception.Message}
    finally {if($reader){$reader.Dispose()}}
    return $result
}

function Test-EngineExportReceipt([string]$OriginalDirectory,$Report) {
    $result=[ordered]@{passed=$false;error='';original_file='runtime-mix-engine-export.wav';canonical_file='runtime-mix.wav';policy='Preserve engine bytes; only canonical BlockAlign header bytes may differ; PCM payload hashes and every other byte must match'}
    $enginePath=Join-Path $OriginalDirectory $result.original_file
    $canonicalPath=Join-Path $OriginalDirectory $result.canonical_file
    try {
        if(-not (Test-Path -LiteralPath $enginePath -PathType Leaf)){throw 'preserved_engine_export_missing'}
        if(-not (Test-Path -LiteralPath $canonicalPath -PathType Leaf)){throw 'canonical_export_missing'}
        $engineBytes=[IO.File]::ReadAllBytes($enginePath)
        $canonicalBytes=[IO.File]::ReadAllBytes($canonicalPath)
        $result['original_sha256']=(Get-FileHash -LiteralPath $enginePath -Algorithm SHA256).Hash
        $result['canonical_sha256']=(Get-FileHash -LiteralPath $canonicalPath -Algorithm SHA256).Hash
        if($engineBytes.Length -le 44 -or $engineBytes.Length -ne $canonicalBytes.Length){throw 'original_canonical_length_mismatch'}
        if([Text.Encoding]::ASCII.GetString($engineBytes,0,4) -ne 'RIFF' -or [Text.Encoding]::ASCII.GetString($engineBytes,8,8) -ne 'WAVEfmt ' -or [BitConverter]::ToUInt32($engineBytes,16) -ne 16 -or [BitConverter]::ToUInt16($engineBytes,20) -ne 1 -or [Text.Encoding]::ASCII.GetString($engineBytes,36,4) -ne 'data'){throw 'unexpected_engine_export_layout'}
        [int]$channels=[BitConverter]::ToUInt16($engineBytes,22)
        [long]$rate=[BitConverter]::ToUInt32($engineBytes,24)
        [int]$expectedAlign=$channels*2
        [int]$engineAlign=[BitConverter]::ToUInt16($engineBytes,32)
        if($channels -lt 1 -or $channels -gt 8 -or $rate -lt 8000 -or $rate -gt 192000 -or [BitConverter]::ToUInt16($engineBytes,34) -ne 16 -or [BitConverter]::ToUInt32($engineBytes,28) -ne $rate*$expectedAlign){throw 'unexpected_engine_PCM_format'}
        if([long][BitConverter]::ToUInt32($engineBytes,4)+8 -ne $engineBytes.Length -or [long][BitConverter]::ToUInt32($engineBytes,40)+44 -ne $engineBytes.Length -or ($engineBytes.Length-44)%$expectedAlign -ne 0){throw 'incomplete_engine_PCM_payload'}
        if($engineAlign -ne 2 -and $engineAlign -ne $expectedAlign){throw 'unrecognized_engine_BlockAlign_error'}
        if([BitConverter]::ToUInt16($canonicalBytes,32) -ne $expectedAlign){throw 'canonical_BlockAlign_invalid'}
        $differences=[Collections.Generic.List[int]]::new()
        for($i=0;$i -lt $engineBytes.Length;$i++) {
            if($engineBytes[$i] -ne $canonicalBytes[$i]) {
                if($i -ne 32 -and $i -ne 33){throw "original_canonical_unapproved_byte_change_at_$i"}
                $differences.Add($i)
            }
        }
        $sha=[Security.Cryptography.SHA256]::Create()
        try {
            $originalPCM=$sha.ComputeHash($engineBytes,44,$engineBytes.Length-44)
            $canonicalPCM=$sha.ComputeHash($canonicalBytes,44,$canonicalBytes.Length-44)
            $result['original_PCM_sha256']=([BitConverter]::ToString($originalPCM)).Replace('-','')
            $result['canonical_PCM_sha256']=([BitConverter]::ToString($canonicalPCM)).Replace('-','')
        } finally {$sha.Dispose()}
        $result['PCM_payload_bytes']=$engineBytes.Length-44
        $result['PCM_payload_identical']=$result.original_PCM_sha256 -eq $result.canonical_PCM_sha256
        $result['changed_byte_offsets']=@($differences)
        $result['original_BlockAlign']=$engineAlign;$result['canonical_BlockAlign']=$expectedAlign
        $result['header_repair_applied']=$engineAlign -ne $expectedAlign
        if(-not $result.PCM_payload_identical){throw 'PCM_payload_hash_mismatch'}
        if(-not $Report -or $Report.audio_engine_original -ne $result.original_file -or $Report.audio_file -ne $result.canonical_file -or $Report.audio_PCM_payload_unchanged -ne $true -or $Report.audio_header_block_align_repaired -ne $result.header_repair_applied){throw 'UE_original_canonical_receipt_missing_or_disagrees'}
        $result.passed=$true
    } catch {$result.error=$_.Exception.Message}
    return $result
}

function Get-CaptureAssessment([string]$Archive,[string]$ExpectedProfile='') {
    $original=Join-Path $Archive '原件'
    $frames=@(Get-ChildItem -LiteralPath $original -Filter 'MovieFrame*.png' -File | Sort-Object Name)
    $failures=[Collections.Generic.List[string]]::new()
    $report=$null;$reportPath=Join-Path $original 'runtime-report.json'
    if(Test-Path -LiteralPath $reportPath){
        try {$report=Get-Content -LiteralPath $reportPath -Raw | ConvertFrom-Json}
        catch {$failures.Add('runtime_report_invalid_json')}
    } else {$failures.Add('runtime_report_missing')}
    $profile=if($report.profile){[string]$report.profile}else{'melee_benchmark'}
    if($ExpectedProfile -and $profile -ne $ExpectedProfile){$failures.Add('requested_runtime_profile_not_executed')}
    $requiredChecks=if($profile -in @('first_unit_swd_lgt_stone','first_unit_swd_skill_lgt_stone','first_unit_swd_skill_lgt_stone_explore')){
        @('first_unit_single_development_knight_and_default_sword','qa_light_armor_completed_after_half_second','stone_proximity_wake_completed_full_085','charge_direction_locked_after_player_y_change','charge_jump_avoided_real_damage','charge_full_160_recovery_before_next_attack','shield_y_escape_avoided_real_damage','sword_normal_input_all_three_stages','sword_first_chain_real_damage_without_stone_poise_break','player_nonpoise_hit_did_not_interrupt_primary','air_primary_rejected_second_start_and_continued_after_landing','stone_naturally_killed_by_accepted_air_primary','normal_left_walk_changes_position_and_facing','ground_primary_after_landed_air_action_completion','real_death_single_receipt_and_stable_prototype_rewards','first_unit_completed_within_30s')
    }else{
        @('player_uses_only_game_mode_simulation_clock','sword_normal_key_chain_all_three_stages','sword_three_hits_total_78_no_duplicate_damage','jump_apex_matches_630_1800','up_input_increases_ground_y','greatsword_normal_key_chain_all_three_stages','greatsword_three_hits_total_138','spear_normal_key_chain_all_three_stages','spear_nearest_target_three_hits_total_63')
    }
    if($profile -in @('first_unit_swd_skill_lgt_stone','first_unit_swd_skill_lgt_stone_explore')){
        $requiredChecks+=@('swd_skill_normal_k_accepted_real_timeline_and_lock_cooldown','swd_skill_one_real_armored_hit_without_repeat','swd_skill_full_recovery_and_fresh_k_rejected_same_action')
    }
    if($profile -eq 'first_unit_swd_skill_lgt_stone_explore'){
        $requiredChecks+=@('explore_initial_u_v_r_unknown','explore_normal_a_revealed_u_r_and_memory_grew','explore_normal_d_retreat_kept_u_memory_outside_visibility','explore_unvisited_v_stayed_unknown_through_retreat','explore_fresh_e_changed_room_and_hud_reset_once','explore_new_room_cleared_r_and_u_matches_fresh_visibility','explore_completed_within_45s')
    }
    if($profile -eq 'equipment_adapter_sources_and_normal_inputs'){
        $requiredChecks=@('equipment_real_run_starter_and_registered_sources','normal_k_lock_single_crit_and_real_cooldown','normal_e_weapon_035_kept_old_until_commit','normal_q_035_kept_instances_and_cooldown','normal_e_armor_050_single_stats_and_hp_cap','full_slots_e_requires_explicit_fresh_selection','normal_enter_backup_replacement_dropped_old_instance','normal_e_repickup_preserved_old_instance','equipment_completed_within_40s')
    }
    if($profile -in @('armor_idle_primary1_layers_normal_inputs','armor_idle_walk_primary123_layers_normal_inputs','armor_idle_walk_primary123_sleeves_normal_inputs')){
        $requiredChecks=@('armor_layer_real_starter_no_armor')
        foreach($armorName in @('none','LGT','MED','HVY','ROB')){
            $requiredChecks+=@("armor_${armorName}_idle_both_facings","armor_${armorName}_walk_both_facings_all6","armor_${armorName}_primary1_both_facings_all6")
            if($profile -in @('armor_idle_walk_primary123_layers_normal_inputs','armor_idle_walk_primary123_sleeves_normal_inputs')){$requiredChecks+=@("armor_${armorName}_primary2_both_facings_all6","armor_${armorName}_primary3_both_facings_all6","armor_${armorName}_three_stage_chain_continuous_both_facings")}
            if($profile -eq 'armor_idle_walk_primary123_sleeves_normal_inputs' -and $armorName -eq 'ROB'){$requiredChecks+=@('armor_ROB_primary2_near_after_weapon_before_hand_both_facings','armor_ROB_primary3_near_after_weapon_before_hand_both_facings')}
            if($armorName -ne 'none'){$requiredChecks+="armor_${armorName}_normal_e_050_commit"}
        }
        $requiredChecks+=if($profile -in @('armor_idle_walk_primary123_layers_normal_inputs','armor_idle_walk_primary123_sleeves_normal_inputs')){'armor_combo_completed_within_55s'}else{'armor_layer_completed_within_40s'}
    }
    if($profile -eq 'ranged_spear_adapter_normal_inputs'){
        $requiredChecks=@('ranged_real_run_starter_and_qa_sources','ranged_fixture_authored_targets_and_ground_positions','xbw_normal_e_035_commit_real_instance','xbw_normal_j_single_world_bolt_and_real_hit','xbw_last_shot_full_recovery_then_110_reload','xbw_normal_k_nearest_two_second_sixty_percent','xbw_skill_single_crit_and_instance_cooldown','xbw_second_full_reload_no_repeat_or_refund','ranged_normal_q_preserves_crossbow_instance','stf_full_slots_fresh_e_enter_slot0_commit','stf_normal_j_magic_fireball_focus10_no_burn','stf_normal_d_enters_actual_fireline_range','stf_normal_k_real_ground_window_focus24','stf_actual_burn_three_ticks_fixed2_per_target','spr_full_slots_e_right_enter_backup_commit','spr_normal_q_activates_acquired_instance','spr_normal_k_three_independent_nearest_targets','ranged_normal_q_back_to_same_staff_without_reset','ranged_hud_real_release_launch_burn_audio_requests','ranged_completed_within_45s')
    }
    if($profile -in @('xbw_ready_body_normal_inputs','xbw_held_body_identity_normal_inputs','xbw_authored_primary_body_normal_inputs')){
        $requiredChecks=@('xbw_ready_real_run_starter_and_single_qa_source','xbw_ready_single_authored_ground_target','xbw_normal_e_035_commit_real_instance','xbw_ready_right_all6_actual_four_layer_stack','xbw_ready_left_all6_actual_four_layer_stack','xbw_normal_j_single_world_bolt_and_real_hit','xbw_last_shot_full_recovery_then_110_reload','xbw_ready_real_release_audio_request','ranged_completed_within_45s')
        if($profile -in @('xbw_held_body_identity_normal_inputs','xbw_authored_primary_body_normal_inputs')){$requiredChecks+='xbw_ground_firing_and_all6_reload_keep_held_body_without_blade_trail'}
        if($profile -eq 'xbw_authored_primary_body_normal_inputs'){$requiredChecks+='xbw_authored_primary_all_three_phases_match_drawn_actor_clock_and_stack'}
    }
    if($profile -eq 'xbw_reload_socket_normal_inputs'){
        $requiredChecks=@('xbw_socket_fixture_real_run_single_source_two_static_targets','xbw_socket_fresh_enter_opens_qa_initialized_start_gate','xbw_socket_normal_e_035_commits_acquired_instance','xbw_socket_right_ready_all6_native_stack','xbw_socket_right_primary_all6_actor_clock','xbw_socket_right_world_bolt_hit_frozen_hand_origin','xbw_socket_right_reload_all4_actor_clock','xbw_socket_right_loaded3_after_real_reload_commit','xbw_socket_left_ready_all6_native_stack','xbw_socket_left_primary_all6_actor_clock','xbw_socket_left_world_bolt_hit_frozen_hand_origin','xbw_socket_left_reload_all4_actor_clock','xbw_socket_left_loaded3_after_real_reload_commit','xbw_socket_normal_q_roundtrip_same_loaded_instance','xbw_socket_real_shot_changes_loaded_to_empty0','xbw_socket_insert_frame2_is_visual_without_early_refill','xbw_socket_fresh_t_cancel_stays_empty_past_old_deadline','xbw_socket_fresh_t_restart_full_duration_then_one_bolt','xbw_socket_history_immutable_and_once_only','xbw_socket_completed_within_55s')
    }
    if($profile -eq 'xbw_four_armor_socket_normal_inputs'){
        $requiredChecks=@('xbw_armor_fixture_real_run_five_qa_sources_two_static_targets','xbw_armor_fresh_enter_opens_initialized_start_gate','xbw_armor_normal_e_035_commits_single_xbw_instance')
        foreach($armorToken in @('lgt','med','hvy','rob')){
            foreach($checkSuffix in @('normal_e_050_commit','ready_both_facings_all6_six_stack','primary_both_facings_all6_actor_clock','bolts_both_facings_frozen_socket_once','reload_both_facings_all4_full_clock','loaded3_only_after_real_commits')){
                $requiredChecks+=('xbw_armor_'+$armorToken+'_'+$checkSuffix)
            }
        }
        $requiredChecks+=@('xbw_armor_history_immutable_once_same_weapon_instance','xbw_armor_completed_within_55s')
    }
    if($profile -eq 'scene_exploration_normal_inputs'){$requiredChecks=@('scene_real_run_starter_unique_knight_and_two_objects','scene_fresh_enter_opens_real_start_gate','scene_normal_w_blocked_by_actual_world_wall','scene_normal_west_bypass_reveals_survey','scene_fresh_e_survey_once_without_reward','scene_repeat_e_never_repeats_survey_or_income','scene_retreat_keeps_memory_outside_visibility','scene_normal_sword_damage_clears_unique_knight','scene_old_665_e_cannot_open_or_change_room','scene_actual_1180_e_opens_current_room_confirmation','scene_normal_escape_cancels_without_travel','scene_fresh_enter_keeps_run_instances_and_resets_new_room_hud','scene_completed_within_55s')}
    $checksPassed=$report -and $report.passed -eq $true -and $profile -in @('melee_benchmark','first_unit_swd_lgt_stone','first_unit_swd_skill_lgt_stone','first_unit_swd_skill_lgt_stone_explore','equipment_adapter_sources_and_normal_inputs','armor_idle_primary1_layers_normal_inputs','armor_idle_walk_primary123_layers_normal_inputs','armor_idle_walk_primary123_sleeves_normal_inputs','ranged_spear_adapter_normal_inputs','xbw_ready_body_normal_inputs','xbw_held_body_identity_normal_inputs','xbw_authored_primary_body_normal_inputs','scene_exploration_normal_inputs','xbw_reload_socket_normal_inputs','xbw_four_armor_socket_normal_inputs') -and @($report.checks).Count -eq $requiredChecks.Count
    # v005 predates profile/declared-name fields. Its actual nine names remain
    # mandatory; modern profiles also require the exact declared-name contract.
    $validateDeclaredNames=-not (-not $report.profile -and $profile -eq 'melee_benchmark' -and $null -eq $report.required_check_names)
    $declaredChecks=@($report.required_check_names)
    if($validateDeclaredNames -and $declaredChecks.Count -ne $requiredChecks.Count){$checksPassed=$false}
    $missingChecks=[Collections.Generic.List[string]]::new()
    foreach($name in $requiredChecks){
        $matches=@($report.checks | Where-Object {$_.name -eq $name})
        if($matches.Count -ne 1 -or $matches[0].passed -ne $true -or ($validateDeclaredNames -and @($declaredChecks | Where-Object {$_ -eq $name}).Count -ne 1)){$checksPassed=$false;$missingChecks.Add($name)}
    }
    if($profile -in @('first_unit_swd_skill_lgt_stone','first_unit_swd_skill_lgt_stone_explore') -and $report.first_unit_skill_requested -ne $true){$checksPassed=$false;$failures.Add('skill_runtime_flag_not_confirmed')}
    if($profile -eq 'first_unit_swd_skill_lgt_stone_explore' -and $report.first_unit_explore_requested -ne $true){$checksPassed=$false;$failures.Add('explore_runtime_flag_not_confirmed')}
    if($profile -eq 'equipment_adapter_sources_and_normal_inputs' -and $report.equipment_adapter_requested -ne $true){$checksPassed=$false;$failures.Add('equipment_runtime_flag_not_confirmed')}
    if($profile -in @('armor_idle_primary1_layers_normal_inputs','armor_idle_walk_primary123_layers_normal_inputs','armor_idle_walk_primary123_sleeves_normal_inputs') -and ($report.armor_layer_proof_requested -ne $true -or $report.armor_layer_preview_requested -ne $true)){$checksPassed=$false;$failures.Add('armor_layer_runtime_flags_not_confirmed')}
    if($profile -in @('armor_idle_walk_primary123_layers_normal_inputs','armor_idle_walk_primary123_sleeves_normal_inputs') -and $report.armor_combo_proof_requested -ne $true){$checksPassed=$false;$failures.Add('armor_combo_runtime_flag_not_confirmed')}
    if($profile -eq 'armor_idle_walk_primary123_sleeves_normal_inputs' -and ($report.armor_sleeves_proof_requested -ne $true -or $report.armor_sleeves_preview_requested -ne $true)){$checksPassed=$false;$failures.Add('armor_sleeves_runtime_flags_not_confirmed')}
    if($profile -eq 'ranged_spear_adapter_normal_inputs' -and $report.ranged_weapons_proof_requested -ne $true){$checksPassed=$false;$failures.Add('ranged_runtime_flag_not_confirmed')}
    if($profile -in @('xbw_ready_body_normal_inputs','xbw_held_body_identity_normal_inputs','xbw_authored_primary_body_normal_inputs') -and ($report.xbw_ready_proof_requested -ne $true -or $report.weapon_body_preview_requested -ne $true)){$checksPassed=$false;$failures.Add('xbw_ready_runtime_flags_not_confirmed')}
    if($profile -eq 'xbw_held_body_identity_normal_inputs' -and $report.xbw_held_identity_proof_requested -ne $true){$checksPassed=$false;$failures.Add('xbw_held_identity_flag_not_confirmed')}
    if($profile -eq 'xbw_authored_primary_body_normal_inputs' -and $report.xbw_primary_body_proof_requested -ne $true){$checksPassed=$false;$failures.Add('xbw_primary_body_flag_not_confirmed')}
    if($profile -eq 'scene_exploration_normal_inputs' -and $report.scene_exploration_proof_requested -ne $true){$checksPassed=$false;$failures.Add('scene_runtime_flag_not_confirmed')}
    if($profile -eq 'xbw_reload_socket_normal_inputs' -and ($report.xbw_reload_socket_proof_requested -ne $true -or $report.weapon_body_preview_requested -ne $true -or $report.capture_frame_cap_fps -ne 60)){$checksPassed=$false;$failures.Add('xbw_reload_socket_runtime_flags_or_60_cap_not_confirmed')}
    if($profile -eq 'xbw_four_armor_socket_normal_inputs' -and ($report.xbw_armor_socket_proof_requested -ne $true -or $report.weapon_body_preview_requested -ne $true -or $report.xbw_reload_body_preview_requested -ne $true -or $report.armor_layer_preview_requested -ne $true -or $report.capture_frame_cap_fps -ne 60)){$checksPassed=$false;$failures.Add('xbw_four_armor_runtime_flags_or_60_cap_not_confirmed')}
    if(@($report.checks | Where-Object {$_.passed -ne $true}).Count){$checksPassed=$false}
    if($report.native_async_capture_requested -eq $true -and ($report.native_async_capture_writes_flushed -ne $true -or $report.native_async_flush_after_audio_stop -ne $true)){$failures.Add('native_async_writer_not_drained_after_audio_stop')}
    if(-not $checksPassed){$failures.Add('runtime_required_profile_checks_not_passed')}
    $audio=Read-GameMixWav (Join-Path $original 'runtime-mix.wav')
    $receipt=Test-EngineExportReceipt $original $report
    if(-not $receipt.passed){$failures.Add('preserved_engine_export_receipt_or_PCM_identity_failed')}
    $controls=$report.audio_capture_controls
    $controlsValid=$controls -and $controls.au_disable_app_volume_at_capture -eq 1 -and $controls.primary_volume_at_capture -gt 0 -and $controls.primary_volume_at_stop -gt 0 -and $controls.main_submix_auto_disable_requested -eq $false -and $controls.main_submix_auto_disable_request_queued -eq $true -and $controls.restore_requested -eq $true -and $controls.app_volume_restored -eq $true
    if(-not $controlsValid){$failures.Add('QA_audio_controls_receipt_missing_or_not_restored')}
    $audioRecorded=$audio.complete_decode -and $audio.non_silent -and $receipt.passed -and $report.audio_recorded -eq $true -and $report.audio_export_callback_received -eq $true
    if(-not $audioRecorded){$failures.Add('game_audio_export_decode_or_non_silence_failed')}
    $offsets=@();[double]$wallDuration=0
    if($report -and $report.capture_timing -and $null -ne $report.capture_timing.frame_wall_offsets_s){
        $offsets=@($report.capture_timing.frame_wall_offsets_s | ForEach-Object {[double]$_})
        $wallDuration=[double]$report.capture_timing.requested_audio_wall_duration_s
    }
    $ordered=$offsets.Count -eq $frames.Count -and $frames.Count -ge 2 -and $wallDuration -gt 0
    [double]$largestGap=0
    for($i=0;$i -lt $offsets.Count;$i++){
        if([double]::IsNaN($offsets[$i]) -or [double]::IsInfinity($offsets[$i]) -or $offsets[$i] -lt 0 -or $offsets[$i] -ge $wallDuration){$ordered=$false}
        if($i -gt 0){
            $gap=$offsets[$i]-$offsets[$i-1]
            if($gap -le 0){$ordered=$false}
            $largestGap=[Math]::Max($largestGap,$gap)
        }
    }
    $firstOffset=if($offsets.Count){$offsets[0]}else{$null}
    $durationDifference=if($audio.complete_decode){[Math]::Abs([double]$audio.duration_s-$wallDuration)}else{$null}
    $realClock=$report -and $report.capture_timing -and $report.capture_timing.use_fixed_time_step -eq $false
    $prewarm=[ordered]@{passed=$false;file='prewarm-viewport.png';used_as_recording_frame=$false;error='prewarm_receipt_or_file_missing'}
    $prewarmPath=Join-Path $original $prewarm.file
    if($report.prewarm_screenshot -and (Test-Path -LiteralPath $prewarmPath -PathType Leaf)){
        try {
            $prewarmBytes=[IO.File]::ReadAllBytes($prewarmPath)
            $validPNG=$prewarmBytes.Length -gt 8 -and [BitConverter]::ToString($prewarmBytes,0,8) -eq '89-50-4E-47-0D-0A-1A-0A'
            $request=[double]$report.prewarm_screenshot.request_monotonic_s
            $complete=[double]$report.prewarm_screenshot.complete_monotonic_s
            $start=[double]$report.capture_timing.capture_start_monotonic_s
            $prewarm['sha256']=(Get-FileHash -LiteralPath $prewarmPath -Algorithm SHA256).Hash
            $prewarm['request_to_complete_s']=$complete-$request
            $prewarm['recording_start_minus_prewarm_complete_s']=$start-$complete
            $prewarm['passed']=$validPNG -and $report.prewarm_screenshot.file -eq $prewarm.file -and $report.prewarm_screenshot.requested -eq $true -and $report.prewarm_screenshot.completed_file_received -eq $true -and $report.prewarm_screenshot.used_as_recording_frame -eq $false -and $request -gt 0 -and $complete -ge $request -and $start -ge $complete
            $prewarm.error=if($prewarm.passed){''}else{'invalid_prewarm_png_or_recording_origin_receipt'}
        }catch{$prewarm.error=$_.Exception.Message}
    }
    if(-not $prewarm.passed){$failures.Add('preserved_prewarm_frame_and_actual_recording_origin_not_verified')}
    $syncPassed=$ordered -and $realClock -and $null -ne $durationDifference -and $durationDifference -le 0.15 -and $firstOffset -le 0.10
    $sync=[ordered]@{
        passed=$syncPassed;frame_timestamps_match_original_files=$ordered;real_delta_clock=$realClock
        requested_wall_duration_s=$wallDuration;audio_minus_wall_abs_s=$durationDifference
        maximum_duration_difference_s=0.15;first_frame_offset_s=$firstOffset;maximum_first_frame_offset_s=0.10
        largest_source_frame_interval_s=$largestGap;output_fps=30
        method='actual monotonic frame intervals resampled to 30fps; first source frame held from requested audio origin; no audio stretch/async resample/offline replacement'
        limitation='Audio-thread start/render latency is not measured sample-accurately. Duration agreement is only a bounded sync check; audiovisual review is still required. Not a performance test.'
    }
    if(-not $syncPassed){$failures.Add('audio_video_wall_clock_sync_not_verified')}
    return [pscustomobject]@{frames=$frames;report=$report;profile=$profile;required_check_count=$requiredChecks.Count;missing_or_failed_checks=@($missingChecks);runtime_checks_passed=$checksPassed;audio=$audio;original_export_verification=$receipt;audio_capture_controls=$controls;prewarm_validation=$prewarm;audio_recorded=$audioRecorded;offsets=$offsets;sync=$sync;failure_reasons=@($failures);passed=$failures.Count -eq 0}
}

function Get-NativePixelAssessment([string]$Archive,[bool]$Required=$false,[bool]$WriteReceipt=$false) {
    $captureIndexPath=Join-Path $Archive 'index.json'
    if(Test-Path -LiteralPath $captureIndexPath){
        $captureIndex=Get-Content -LiteralPath $captureIndexPath -Raw | ConvertFrom-Json
        $Required=$Required -or $captureIndex.fast_lossless_capture_requested -eq $true
    }
    $Required=$Required -or (Test-Path -LiteralPath (Join-Path $Archive '原件\native-lossless-capture.json'))
    if(-not $Required){return [pscustomobject]@{required=$false;passed=$true}}
    $nativeRoot=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\..'))
    $nativeArguments=@((Join-Path $nativeRoot 'tools\scripts\verify-native-capture-pixels.py'),'--archive',$Archive)
    if($WriteReceipt){$nativeArguments+='--write-receipt'}
    try {
        $nativeOutput=@(& (Join-Path $nativeRoot 'tools\runtime\asset-gen\Scripts\python.exe') @nativeArguments 2>&1)
        if($LASTEXITCODE -ne 0){throw ($nativeOutput -join "`n")}
        return [pscustomobject]@{required=$true;passed=$true;verification=(($nativeOutput -join "`n") | ConvertFrom-Json)}
    } catch {return [pscustomobject]@{required=$true;passed=$false;error=$_.Exception.Message}}
}

# Read-only inspection of an actual prior capture. It never starts UE, encodes media,
# updates the previous index, or promotes a legacy silent recording to accepted proof.
if($InspectArchive){
    $assessment=Get-CaptureAssessment ([IO.Path]::GetFullPath($InspectArchive))
    $native=Get-NativePixelAssessment ([IO.Path]::GetFullPath($InspectArchive))
    $inspectionPassed=$assessment.passed -and $native.passed
    $inspectionFailures=@($assessment.failure_reasons)
    if(-not $native.passed){$inspectionFailures+='native_viewport_pixel_verification_failed'}
    [ordered]@{mode='read_only_prior_capture_inspection';passed=$inspectionPassed;profile=$assessment.profile;required_check_count=$assessment.required_check_count;missing_or_failed_checks=$assessment.missing_or_failed_checks;frame_count=$assessment.frames.Count;runtime_checks_passed=$assessment.runtime_checks_passed;audio_recorded=$assessment.audio_recorded;audio=$assessment.audio;original_export_verification=$assessment.original_export_verification;audio_capture_controls=$assessment.audio_capture_controls;prewarm_validation=$assessment.prewarm_validation;sync=$assessment.sync;native_lossless_pixel_verification=$native;failure_reasons=$inspectionFailures} | ConvertTo-Json -Depth 8
    if(-not $inspectionPassed){exit 1}
    exit 0
}

$workspace=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\..'))
$project=Join-Path $workspace 'UnrealGame\CodexDungeon.uproject'
$ffmpeg=Join-Path $workspace 'tools\runtime\asset-gen\Lib\site-packages\imageio_ffmpeg\binaries\ffmpeg-win-x86_64-v7.1.exe'
$engine=Join-Path $EngineRoot 'Engine\Binaries\Win64\UnrealEditor.exe'
foreach($required in @($project,$ffmpeg,$engine)){if(-not (Test-Path -LiteralPath $required -PathType Leaf)){throw "Missing capture dependency: $required"}}
$unitProfile=[bool]($FirstUnit -or $FirstUnitSkill -or $FirstUnitExplore)
$skillProfile=[bool]($FirstUnitSkill -or $FirstUnitExplore)
$profile=if($RangedWeapons){'ranged_spear_adapter_normal_inputs'}elseif($ArmorSleevesLayers){'armor_idle_walk_primary123_sleeves_normal_inputs'}elseif($ArmorComboLayers){'armor_idle_walk_primary123_layers_normal_inputs'}elseif($ArmorLayers){'armor_idle_primary1_layers_normal_inputs'}elseif($EquipmentAdapter){'equipment_adapter_sources_and_normal_inputs'}elseif($FirstUnitExplore){'first_unit_swd_skill_lgt_stone_explore'}elseif($FirstUnitSkill){'first_unit_swd_skill_lgt_stone'}elseif($FirstUnit){'first_unit_swd_lgt_stone'}else{'melee_benchmark'}
$topic=if($RangedWeapons){'弩法杖长枪真实取得战斗动效音轨运行'}elseif($ArmorSleevesLayers){'四甲近袖分层三段连招左右运行'}elseif($ArmorComboLayers){'四甲实际换装三段连招左右分层运行'}elseif($ArmorLayers){'四甲实际换装待机首斩左右分层运行'}elseif($EquipmentAdapter){'真实装备拾取切换替换落地运行'}elseif($FirstUnitExplore){'军剑技能单石骑探索记忆换房运行'}elseif($FirstUnitSkill){'军剑技能轻甲单石骑状态驱动运行'}elseif($FirstUnit){'军剑轻甲单石骑状态驱动运行'}else{'三近战连段运行'}
$visualScope=if($EquipmentAdapter){'Round-helmet candidate body; new read-only source/slot/affix UI and transaction-driven equip poses. Ground tokens and GSW/armor imagery remain development placeholders, not accepted complete assets.'}elseif($CandidateSprites){
    if($unitProfile){'Candidate SWD/LGT/stone-knight preview requested. Round-helmet hero uses74 unique source frames in80 logical Texture2D assets: walk v007, other states v006. Actual walk contact/slide, motion/opacity/mirroring require review. Armor action has authored presentation but no interchangeable armor layers; weapon equip clip is source-only because Q remains instant. Explore receipts record actual last-draw texture paths and sprite sizes.'}
    else{'Candidate SWD hero preview requested; GSW/SPR retain placeholder art. Rendered animation/opacity/mirroring awaits visual review.'}
}else{'Existing prototype placeholder visuals requested.'}
$fixtureScope=if($EquipmentAdapter){'Opt-in inventory adapter fixture with explicitly registered QA ground sources. Normal K/E/Q/Right/Enter plus walking exercise actual ownership transfer, action deadlines and drop/re-pick. Does not certify production loot/shop provenance, armor-layer art, enemy combat or disk save/load.'}elseif($FirstUnitExplore){'Independent Explore profile: original 19-check normal-input SWD skill encounter, followed by normal A/D world exploration and fresh E at the actual old exit; seven additional memory/reset checks, 45s overall deadline, 64s audio preallocation. Combat retains its 30s deadline. Explicit QA armor action, prototype rewards; actual acquisition and save/load not exercised.'}elseif($FirstUnitSkill){'State-driven single stone-knight encounter: normal K SWD skill and fresh-K rejection, one ground J then original natural air finisher; explicit QA armor action; prototype rewards, actual acquisition and save/load not exercised.'}elseif($FirstUnit){'State-driven single stone-knight development encounter via normal controller inputs; explicit QA armor-change action; prototype rewards, actual acquisition and save/load not exercised.'}else{'QA normal input edges, three melee chains, air primary and Y movement.'}
if($ArmorLayers){$fixtureScope='Opt-in real QA armor sources and normal E/Enter .50 commits plus A/D/J; no direct armor/HUD edits.';$visualScope='Frozen idle60/walk36/P1four36 native components; actual layer-path observations for no armor/four armors, full walk and first slash in both facings. Other clips remain old candidates, not full armor/all-state/20-combination or disk acceptance.'}
if($ArmorComboLayers){$visualScope='Native idle60/walk36/P1four36/P2four36/P3four36 partial armor components, ten normal buffered three-stage J chains and actual layer paths. ROB sleeves, footlock, other states, full20 combinations and disk acceptance remain pending.'}
if($ArmorSleevesLayers){$visualScope='Native P2/P3 revised common body and real ROB near-cloth cuffs, separate84 textures. Same36 normal input checks plus2 actual draw-stack/facing/six-pose near checks. P3 source has cuff skin; complete long sleeves, footlock/fullstate/20 combinations/disk/listening remain pending.'}
if($RangedWeapons){$fixtureScope='Explicit QA sources, authored stationary initial targets/positions/HP, real normal E/Q/J/K/Right/Enter and walking; no direct hit/resource edits during proof.';$visualScope='Actual world projectile/fireline/burn presentation and audio play requests; incomplete ranged body/weapon art and authored muzzle sockets, listening/mix and full production content remain pending.'}
if($XBWReadyBody){
    $profile='xbw_ready_body_normal_inputs';$topic='弩真实拾取双向双手持握运行'
    $fixtureScope='Actual QA source normal E .35s acquisition, A/D and full six-frame ready idle both facings, then real J single shot/hit/full1.10 reload.'
    $visualScope='Opt-in common-underclothes XBW far/weapon/support/near native tracks only. Attack/reload and four-armor art, authored world muzzle, footlock, audio listening and full weapon remain unfinished.'
}
if($XBWHeldIdentity){
    $profile='xbw_held_body_identity_normal_inputs';$topic='猎弩射击装填造型保持运行'
    $visualScope='Same native ready pose explicitly retained during ground firing/reload to prevent sword/geometric identity fallback; real reload all6 render frames and no unrelated melee trail. This is a pose placeholder, not finished firing/cocking or four-armor/world-muzzle/listening acceptance.'
}
if($XBWPrimaryBody){
    $profile='xbw_authored_primary_body_normal_inputs';$topic='猎弩专属射击三阶段运行'
    $visualScope='Native primary18 tracks sample the accepted Actor phase clock; normal right-facing firing observes all three phases and validates actual draw stack. Observed frame mask is reported honestly; this does not certify every six pose in both facings. Reload still uses explicit ready placeholder. String mechanics, armor compatibility, world muzzle and listening pending.'
}
if($SceneExploration){
    $profile='scene_exploration_normal_inputs';$topic='侧路碎碑迷雾记忆真实出口探索运行'
    $fixtureScope='Explicit Scene preview genuine Run initialization and single Knight; only at initialization time0 disable its autonomous attack starts for this traversal proof; normal tracking movement remains active. All subsequent movement, sword combat, investigation and exit confirmation use normal controller inputs. Normal manual Scene preview keeps attacks and tracking enabled.'
    $visualScope='Actual wall and sign read shared gameplay layout, fog reveal and memory, no-income investigation, old665 refusal, actual1180 E/Esc/freshEnter same-Run room transfer. QA traversal is not production loot/D07 graph/D08 hidden income/D13 or final art/AI acceptance.'
}
if($XBWReloadSocket){
    $profile='xbw_reload_socket_normal_inputs';$topic='猎弩装填发射口状态运行'
    $fixtureScope='One genuine equipment Run/source and two stationary QA targets; phase0 initializes start gate, then normal Enter/E/WASD/J/T/Q only. No live HP/position/ammo or action repair.'
    $visualScope='Native primary6/reload4 both facings, actual Actor hand source and separate immutable presentation/range facts; loaded/empty, switch retention, cancel after inserted-image and fresh restart. Four armor/fullstate/20mix/production loot/D13/listening remain unfulfilled.'
}
if($XBWArmorSocket){
    $profile='xbw_four_armor_socket_normal_inputs';$topic='猎弩四甲双向射击装填实际换装运行'
    $fixtureScope='Phase0 initializes one genuine equipment Run, one Ammo1 XBW and four unenchanted armor QA sources, two stationary HP2000 targets and one start gate. Later only normal Enter/E/Tab/A/D/J; no live state repairs.'
    $visualScope='Actual .35 weapon and .50 armor commits, replacement old-held, four armor instances each with both facings of native ready6/primary6/reload4 exact six layers and immutable hand-origin bolts. Eight mandatory plus at most two retry shots,55s deadline; no walk/skill/air/coverage/20mix/formal loot/D13/listening/full units acceptance.'
}
$captureRate=if($XBWReloadSocket -or $XBWArmorSocket){60}else{30}
$archive=Join-Path $workspace ("过程图稿与视频\{0}_{1}_{2}" -f (Get-Date -Format 'yyyy-MM-dd'),$topic,$Version)
if(Test-Path -LiteralPath $archive){throw "Preserve old evidence; choose a new version: $archive"}
$original=Join-Path $archive '原件';$presentation=Join-Path $archive '展示副本'
New-Item -ItemType Directory -Path $original,$presentation | Out-Null
$index=[ordered]@{
    date=(Get-Date -Format o);version=$Version;status='capturing';project=$project
    profile=$profile;scope="$fixtureScope $visualScope Real delta with ${captureRate}fps cap; audio signal analysis only, listening/mix and visual acceptance pending. Not a performance test."
    visual_scope=$visualScope
    audio_recorded=$false;audio_source='UE main game submix only';microphone_capture=$false;desktop_loopback_capture=$false
    audio_time_stretch=$false;offline_audio_substitution=$false;failure_reasons=@()
    candidate_sprites_requested=[bool]$CandidateSprites
    first_unit_requested=$unitProfile
    first_unit_skill_requested=$skillProfile
    first_unit_explore_requested=[bool]$FirstUnitExplore
    equipment_adapter_requested=[bool]$EquipmentAdapter
    armor_layer_preview_requested=[bool]($ArmorLayers -or $XBWArmorSocket)
    armor_combo_proof_requested=[bool]$ArmorComboLayers
    armor_sleeves_proof_requested=[bool]$ArmorSleevesLayers
    ranged_weapons_proof_requested=[bool]$RangedWeapons
    xbw_ready_proof_requested=[bool]$XBWReadyBody
    xbw_held_identity_proof_requested=[bool]$XBWHeldIdentity
    xbw_primary_body_proof_requested=[bool]$XBWPrimaryBody
    scene_exploration_proof_requested=[bool]$SceneExploration
    xbw_reload_socket_proof_requested=[bool]$XBWReloadSocket
    xbw_armor_socket_proof_requested=[bool]$XBWArmorSocket
    capture_frame_cap_fps=$captureRate
    fast_lossless_capture_requested=[bool]$FastLosslessCapture
    async_lossless_capture_requested=[bool]$AsyncLosslessCapture
}
$index['module_sha256']=(Get-FileHash -LiteralPath (Join-Path $workspace 'UnrealGame\Binaries\Win64\UnrealEditor-CodexDungeon.dll') -Algorithm SHA256).Hash
$sourceHashes=[ordered]@{}
foreach($source in Get-ChildItem -LiteralPath (Join-Path $workspace 'UnrealGame\Source\CodexDungeon') -File){$sourceHashes[$source.Name]=(Get-FileHash -LiteralPath $source.FullName -Algorithm SHA256).Hash}
$index['source_sha256_at_capture']=$sourceHashes
$index['capture_script_sha256']=(Get-FileHash -LiteralPath $PSCommandPath -Algorithm SHA256).Hash
$indexPath=Join-Path $archive 'index.json'
$index | ConvertTo-Json -Depth 12 | Set-Content -LiteralPath $indexPath -Encoding utf8
try {
    # Fixed-step engine time does not pace the realtime audio mixer; do not use
    # -UseFixedTimeStep/-FPS/-SECONDS. Probe stops movie capture and waits for export.
    # Probe alone enables GIsDumpingMovie after prewarm; the command-line flag
    # would permit un-stamped startup screenshots before recording begins.
    $arguments=@(('"{0}"' -f $project),'/Game/Maps/FirstRoom','-game','-windowed','-ResX=1280','-ResY=720','-NoSplash','-NoLiveCoding','-nop4','-unattended','-DungeonContentProof',('-DungeonContentProofDir="{0}"' -f $original),('-ExecCmds="t.MaxFPS {0}"' -f $captureRate),('-abslog="{0}"' -f (Join-Path $archive 'runtime.log')))
    if($CandidateSprites){$arguments+='-DungeonCandidateSprites'}
    if($unitProfile){$arguments+=@('-DungeonFirstUnitProof','-DungeonStoneKnightPreview')}
    if($skillProfile){$arguments+='-DungeonFirstUnitSkillProof'}
    if($FirstUnitExplore){$arguments+='-DungeonFirstUnitExploreProof'}
    if($EquipmentAdapter){$arguments+=@('-DungeonEquipmentAdapterProof','-DungeonStoneKnightPreview')}
    if($ArmorLayers){$arguments+=@('-DungeonArmorLayerProof','-DungeonArmorLayerPreview','-DungeonStoneKnightPreview')}
    if($ArmorComboLayers){$arguments+='-DungeonArmorComboProof'}
    if($ArmorSleevesLayers){$arguments+=@('-DungeonArmorSleevesProof','-DungeonArmorSleevesPreview')}
    if($RangedWeapons){$arguments+=@('-DungeonRangedWeaponsProof','-DungeonArmorLayerPreview','-DungeonStoneKnightPreview')}
    if($XBWReadyBody){$arguments+=@('-DungeonXBWReadyProof','-DungeonWeaponBodyPreview')}
    if($XBWPrimaryBody){$arguments+=@('-DungeonXBWPrimaryProof','-DungeonXBWPrimaryBodyPreview')}
    if($SceneExploration){$arguments+=@('-DungeonSceneExplorationProof','-DungeonStoneKnightPreview')}
    if($XBWReloadSocket){$arguments+=@('-DungeonXBWReloadSocketProof','-DungeonWeaponBodyPreview','-DungeonXBWPrimaryBodyPreview','-DungeonXBWReloadBodyPreview')}
    if($XBWArmorSocket){$arguments+=@('-DungeonXBWArmorSocketProof','-DungeonWeaponBodyPreview','-DungeonXBWReloadBodyPreview','-DungeonArmorLayerPreview')}
    if($XBWHeldIdentity){$arguments+='-DungeonXBWHeldIdentityProof'}
    if($FastLosslessCapture){$arguments+='-DungeonFastLosslessCapture'}
    if($AsyncLosslessCapture){$arguments+='-DungeonAsyncLosslessCapture'}
    $process=Start-Process -FilePath $engine -ArgumentList $arguments -WindowStyle Hidden -PassThru
    Write-Output "Content proof PID $($process.Id), archive $archive"
    if(-not $process.WaitForExit($ProcessTimeoutSeconds*1000)){
        Stop-Process -Id $process.Id -Force
        $index['failure_reasons']=@('capture_process_timeout')
        throw 'Capture process timed out; interrupted originals preserved'
    }
    $process.Refresh();$index['exit_code']=$process.ExitCode
    $assessment=Get-CaptureAssessment $archive $profile
    $index['frame_count']=$assessment.frames.Count
    $index['runtime_checks_passed']=$assessment.runtime_checks_passed
    $index['runtime_profile']=$assessment.profile
    $index['required_check_count']=$assessment.required_check_count
    $index['missing_or_failed_checks']=$assessment.missing_or_failed_checks
    if($AsyncLosslessCapture -and $assessment.report.native_async_capture_requested -ne $true){$index['failure_reasons']+=@('requested_async_native_writer_not_executed');throw 'Requested async native writer was not executed; evidence preserved.'}
    if($unitProfile){$index['first_unit_receipt']=$assessment.report.first_unit}
    $index['first_unit_skill_runtime_flag']=$assessment.report.first_unit_skill_requested
    $index['first_unit_explore_runtime_flag']=$assessment.report.first_unit_explore_requested
    if($FirstUnitExplore){$index['exploration_receipt']=$assessment.report.first_unit.exploration}
    $index['audio_recorded']=$assessment.audio_recorded
    $index['audio_validation']=$assessment.audio
    $index['original_export_verification']=$assessment.original_export_verification
    $index['audio_capture_controls']=$assessment.audio_capture_controls
    $index['prewarm_validation']=$assessment.prewarm_validation
    $index['candidate_sprites_runtime_flag']=$assessment.report.candidate_sprites_requested
    $index['audio_video_sync']=$assessment.sync
    $index['failure_reasons']=$assessment.failure_reasons
    $index['mux_status']='skipped_without_valid_runtime_audio_and_timestamps'
    $native=Get-NativePixelAssessment $archive ([bool]$FastLosslessCapture) $true
    $index['native_lossless_pixel_verification']=$native
    if($AsyncLosslessCapture -and $native.verification.native_async_writer_verified -ne $true){$index['failure_reasons']=@($index['failure_reasons'])+'native_async_writer_count_crc_or_drain_verification_missing';throw 'Actual async pixel writer verification missing; preserved.'}
    if(-not $native.passed){
        $index['failure_reasons']=@($index['failure_reasons'])+'native_viewport_pixel_verification_failed'
        throw 'Native viewport/PNG pixel verification failed; diagnostics and originals preserved'
    }
    if($assessment.audio_recorded -and $assessment.sync.passed){
        $list=Join-Path $archive 'frames.txt'
        $lines=[Collections.Generic.List[string]]::new()
        $culture=[Globalization.CultureInfo]::InvariantCulture
        for($i=0;$i -lt $assessment.frames.Count;$i++){
            $next=if($i+1 -lt $assessment.frames.Count){$assessment.offsets[$i+1]}else{$assessment.sync.requested_wall_duration_s}
            $start=if($i -eq 0){0.0}else{$assessment.offsets[$i]}
            $lines.Add("file '"+$assessment.frames[$i].FullName.Replace('\','/').Replace("'","'\''")+"'")
            $lines.Add('duration '+([double]($next-$start)).ToString('F9',$culture))
        }
        # The concat demuxer needs a final repeated frame to honor its last duration.
        $lines.Add("file '"+$assessment.frames[-1].FullName.Replace('\','/').Replace("'","'\''")+"'")
        [IO.File]::WriteAllLines($list,$lines,[Text.UTF8Encoding]::new($false))
        $video=Join-Path $presentation $(if($XBWArmorSocket){'xbw-four-armor-socket-normal-inputs.mp4'}elseif($XBWReloadSocket){'xbw-reload-socket-normal-inputs.mp4'}elseif($SceneExploration){'scene-exploration-normal-inputs.mp4'}elseif($XBWPrimaryBody){'xbw-primary-normal-inputs.mp4'}elseif($XBWHeldIdentity){'xbw-held-identity-normal-inputs.mp4'}elseif($XBWReadyBody){'xbw-ready-normal-inputs.mp4'}elseif($RangedWeapons){'ranged-spear-normal-inputs.mp4'}elseif($ArmorSleevesLayers){'armor-sleeves-layers-normal-inputs.mp4'}elseif($ArmorComboLayers){'armor-combo-layers-normal-inputs.mp4'}elseif($ArmorLayers){'armor-layers-normal-inputs.mp4'}elseif($EquipmentAdapter){'equipment-adapter-normal-inputs.mp4'}elseif($FirstUnitExplore){'first-unit-swd-skill-exploration.mp4'}elseif($FirstUnitSkill){'first-unit-swd-skill-lgt-stone.mp4'}elseif($FirstUnit){'first-unit-swd-lgt-stone.mp4'}else{'combat-foundation.mp4'})
        $mix=Join-Path $original 'runtime-mix.wav'
        $videoFrames=[int][Math]::Ceiling($assessment.sync.requested_wall_duration_s*30)
        & $ffmpeg -nostdin -hide_banner -loglevel error -n -f concat -safe 0 -i $list -i $mix -map 0:v:0 -map 1:a:0 -vf fps=30 -frames:v $videoFrames -c:v libx264 -crf 20 -pix_fmt yuv420p -c:a aac -b:a 192k -movflags +faststart $video
        if($LASTEXITCODE -ne 0){throw 'Runtime audio/video mux failed; originals preserved'}
        # Both real encoded streams must decode. No source sample library is an input.
        $decodeLog=@(& $ffmpeg -nostdin -hide_banner -loglevel error -i $video -map 0:v:0 -map 0:a:0 -f null - 2>&1)
        if($LASTEXITCODE -ne 0){throw ('Encoded runtime streams failed complete decode: '+($decodeLog -join ' '))}
        $index['mux_status']='actual_runtime_WAV_muxed_both_streams_decoded'
        $index['presentation_sha256']=(Get-FileHash -LiteralPath $video -Algorithm SHA256).Hash
        $index['presentation_video_frames_target']=$videoFrames
        $index['presentation_audio_codec']='AAC 192k from runtime-mix.wav canonical header copy; PCM identical to preserved runtime-mix-engine-export.wav; no gain/tempo filters'
    }
    $index['status']=if($process.ExitCode -eq 0 -and $assessment.passed -and $index.mux_status -eq 'actual_runtime_WAV_muxed_both_streams_decoded'){'captured_pending_visual_audio_review'}else{'failed_preserved'}
    $index | ConvertTo-Json -Depth 12 | Set-Content -LiteralPath $indexPath -Encoding utf8
} catch {
    $index['status']='failed_preserved'
    $index['capture_exception']=$_.Exception.Message
    $index | ConvertTo-Json -Depth 12 | Set-Content -LiteralPath $indexPath -Encoding utf8
    throw
}
Write-Output ($index | ConvertTo-Json -Depth 12 -Compress)
if($index.status -eq 'failed_preserved'){exit 1}
