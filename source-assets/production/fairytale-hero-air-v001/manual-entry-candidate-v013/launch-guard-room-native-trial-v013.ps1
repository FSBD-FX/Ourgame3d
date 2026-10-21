param([string]$EngineRoot='G:\UE_5.5',[string]$Snapshot='',[string]$RootCheckpoint='',[switch]$LightArtTrial,[switch]$GuardFullArt,[switch]$ValidateOnly)
$ErrorActionPreference='Stop';$workspace='F:\Ourgame'
if(-not $RootCheckpoint){throw 'Root must select a v013 manual admission after actual Air keyframe review for LIMITED_WIP.'}
function Resolve-PinPath($Pin){
 if(-not $Pin){throw 'Required Root actual pin is missing.'}
 if([IO.Path]::IsPathRooted($Pin.path)){[IO.Path]::GetFullPath($Pin.path)}else{[IO.Path]::GetFullPath((Join-Path $workspace $Pin.path))}
}
function Assert-PinnedFile($Pin){
 $path=Resolve-PinPath $Pin;$item=Get-Item -LiteralPath $path
 if($item.Length -ne $Pin.bytes -or (Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash.ToLowerInvariant() -ne $Pin.sha256){throw "Root actual pin changed: $path"}
}
function Read-PinnedJson($Pin){
 Assert-PinnedFile $Pin
 Get-Content -LiteralPath (Resolve-PinPath $Pin) -Raw|ConvertFrom-Json
}
function Same-Pin($A,$B){
 $A -and $B -and $A.bytes -eq $B.bytes -and $A.sha256 -eq $B.sha256 -and (Resolve-PinPath $A) -eq (Resolve-PinPath $B)
}
$checkpointPath=if([IO.Path]::IsPathRooted($RootCheckpoint)){[IO.Path]::GetFullPath($RootCheckpoint)}else{[IO.Path]::GetFullPath((Join-Path $workspace $RootCheckpoint))}
$checkpoint=Get-Content -LiteralPath $checkpointPath -Raw|ConvertFrom-Json
if($checkpoint.schema -ne 'HeroAir6-Root-manual-entry-v013' -or $checkpoint.RootApproved -ne $true -or $checkpoint.is_template -ne $false -or $checkpoint.approval_scope -ne 'LIMITED_WIP' -or $checkpoint.Root_visible_keyframes_reviewed -ne $true -or $checkpoint.manual_trial_allowed -ne $true -or $checkpoint.full_realtime_playback_reviewed -ne $false -or $checkpoint.audio_listened -ne $false -or $checkpoint.known_pose_join_refinement_open -ne $true -or $checkpoint.FinalAccepted -ne $false){throw 'Candidate lacks actual LIMITED_WIP Root manual-trial approval; UE has not been started.'}
if($checkpoint.compiled_manifest_pin.sha256 -ne '52f906018a042d006db3470ec2fa7b4603a6b54e2489ab33d2bdff0bf309cd62'){throw 'Manual v013 must bind its actual current CM296/1419/203.'}
$compiled=Read-PinnedJson $checkpoint.compiled_manifest_pin
if($compiled.source_files -ne 296 -or $compiled.production_files -ne 1419 -or $compiled.registered_tests -ne 203 -or $compiled.passed -ne 203 -or $compiled.failed -ne 0 -or $compiled.notRun -ne 0){throw 'Current compiled registry/counts differ.'}
if($Snapshot){$selected=[IO.Path]::GetFullPath($Snapshot);$bound=[IO.Path]::GetFullPath($checkpoint.compiled_manifest_pin.path);if($selected -ne $bound -and $selected -ne [IO.Path]::GetDirectoryName($bound)){throw 'Snapshot override differs from Root approved current CM.'}}
$prereg=Read-PinnedJson $checkpoint.native_prereg_pin
if($prereg.compiled_manifest_pin.sha256 -ne '52f906018a042d006db3470ec2fa7b4603a6b54e2489ab33d2bdff0bf309cd62' -or $prereg.checker_freeze_pin.sha256 -ne 'a6bb3f8bd3127aa49b788f72ec1e7d9c9a9bddf8d790eb3c80c1de45e8166a46'){throw 'Root native prerequisite binds different compiled/checker inputs.'}
$pair=Read-PinnedJson $checkpoint.native_pair_result_pin
if($pair.schema -ne 'hero-Air6-production-independent-pair-v001' -or $pair.passed -ne $true -or $pair.actual_two_fresh_PIDs -ne $true -or $pair.both6pose_None6_LGT9_rejump_Ready_verified -ne $true -or $checkpoint.full_preflight_evidence -ne 'frozen_v003_paircheck_each_native_branch'){throw 'Actual fresh left/right Air validation and retained complete preflight evidence are required.'}
foreach($branch in @($pair.left,$pair.right)){
 if($branch.schema -ne 'hero-Air6-production-independent-native-v001' -or $branch.passed -ne $true -or -not (Same-Pin $branch.compiled_manifest_pin $checkpoint.compiled_manifest_pin) -or -not (Same-Pin $branch.checker_freeze_pin $prereg.checker_freeze_pin) -or -not (Same-Pin $branch.source_probe_freeze_pin $prereg.source_probe_freeze_pin)){throw 'Native pair branch binds different compiled/source/checker inputs.'}
}
if(-not ((Same-Pin $pair.left.root_prereg_pin $checkpoint.native_prereg_pin) -or (Same-Pin $pair.right.root_prereg_pin $checkpoint.native_prereg_pin))){throw 'Selected actual prereg is absent from the approved native pair.'}
$checkerFreeze=Read-PinnedJson $prereg.checker_freeze_pin
foreach($member in $checkerFreeze.members){Assert-PinnedFile $member}
$null=Read-PinnedJson $checkpoint.Root_visual_review_receipt_pin
$candidateFreeze=Read-PinnedJson $checkpoint.manual_candidate_freeze_pin
if(-not @($candidateFreeze.members|Where-Object {[IO.Path]::GetFullPath($_.path) -eq [IO.Path]::GetFullPath($PSCommandPath)}).Count){throw 'Current manual launcher is absent from Root approved candidate freeze.'}
foreach($member in $candidateFreeze.members){
 $file=Get-Item -LiteralPath $member.path
 if($file.Length -ne $member.bytes -or (Get-FileHash -LiteralPath $member.path -Algorithm SHA256).Hash.ToLowerInvariant() -ne $member.sha256){throw "Manual candidate changed: $($member.path)"}
}
# Full v003 paircheck calls verify_native -> complete C.preflight for each branch.
# Root pins that actual result at admission; each launch verifies all current CM bytes/membership.
$names=[System.Collections.Generic.HashSet[string]]::new([StringComparer]::Ordinal)
foreach($member in $compiled.files){
 if(-not $names.Add([string]$member.path)){throw 'Duplicate current compiled membership.'}
 Assert-PinnedFile $member
}
if(-not $names.Contains('UnrealGame/Binaries/Win64/UnrealEditor-CodexDungeon.dll')){throw 'Current compiled game DLL pin is missing.'}
foreach($directory in @(@{prefix='UnrealGame/Source/';count=296},@{prefix='UnrealGame/Content/Production/';count=1419})){
 $expected=[System.Collections.Generic.HashSet[string]]::new([StringComparer]::Ordinal)
 foreach($name in $names){if($name.StartsWith($directory.prefix,[StringComparison]::Ordinal)){[void]$expected.Add($name)}}
 $actual=[System.Collections.Generic.HashSet[string]]::new([StringComparer]::Ordinal)
 foreach($file in Get-ChildItem -LiteralPath (Join-Path $workspace $directory.prefix) -Recurse -File -Force){[void]$actual.Add($file.FullName.Substring($workspace.Length+1).Replace('\','/'))}
 if($actual.Count -ne $directory.count -or -not $actual.SetEquals($expected)){throw "Current compiled directory membership differs: $($directory.prefix)"}
}
if($ValidateOnly){[ordered]@{compiled_inputs_verified=$true;actual_CM_members_checked=$names.Count;full_preflight_evidence='frozen_v003_paircheck_each_native_branch';historical_E_closure_reexpanded=$false;strict_registry=203;source_files=296;production_files=1419;manual_light_source=[bool]$LightArtTrial;guard_full_art=[bool]$GuardFullArt;death_art=$true;dodge_art=$true;dodge_preload=33;stomp_overlay=[bool]($GuardFullArt -or $LightArtTrial);oldGuardProfileUnique=44;StompOverlayUnique=50;Move7_enabled=[bool]($GuardFullArt -or $LightArtTrial);Move7_parts=7;Move7_required_resources=7;Move7_flag='DungeonFairytaleGuardMoveRigPreview';Air6_enabled=$true;Air6_flag='DungeonFairytaleSwordAirPreview';Air6_source_textures=49;Air6_None_slots=6;Air6_LGT_slots=9;automatic_inputs=$false;diagnostic_damage=$false;debug_range_enabled=$false;traditional_HUD_shown=$false;approval_scope='LIMITED_WIP';content_status='WIP limited manual preview; joins under refinement';full_realtime_playback_reviewed=$false;audio_listened=$false;known_pose_join_refinement_open=$true;UE_started=$false;FinalAccepted=$false}|ConvertTo-Json;return}
if(@(Get-Process -Name 'UnrealEditor*','UnrealBuildTool' -ErrorAction SilentlyContinue).Count){throw 'Close UE/UBT before starting the visible native trial.'}
$log=Join-Path $workspace ('UnrealGame\Saved\Bootstrap\guard-room-Air6-v013-trial-'+(Get-Date -Format 'yyyyMMdd-HHmmss-fffffff')+'.log')
$arguments=@(('"{0}"' -f (Join-Path $workspace 'UnrealGame\CodexDungeon.uproject')),'/Game/Maps/FirstRoom?DungeonFirstBatchGuardRoom','-game','-windowed','-ResX=1280','-ResY=720','-NoSplash','-NoLiveCoding','-nop4','-DungeonCandidateSprites','-DungeonFairytaleSwordBodyPreview','-DungeonFairytaleSwordBodyV002Preview','-DungeonFairytaleSwordArmorPrimary1Preview','-DungeonFairytaleSwordPrimary2Preview','-DungeonFairytaleSwordPrimary2BodyPreview','-DungeonFairytaleSwordPrimary2ArmorPreview','-DungeonFairytaleSwordPrimary3ArmorPreview','-DungeonFairytaleLeatherReadyPreview','-DungeonFairytaleLeatherPrimary1Preview','-DungeonFairytaleLeatherPrimary2Preview','-DungeonFairytaleLeatherPrimary3Preview','-DungeonFairytaleSwordEquipmentBoundPreview','-DungeonFairytaleSwordWalkPreview','-DungeonFairytaleSwordHurtPreview','-DungeonFairytaleSwordDeathPreview','-DungeonFairytaleSwordDodgePreview','-DungeonFairytaleSwordAirPreview',('-abslog="{0}"' -f $log))
if($LightArtTrial){$arguments+='-DungeonGuardRoomManualLightSource'}
if($GuardFullArt -or $LightArtTrial){$arguments+=@('-DungeonFairytaleGuardFullPreview','-DungeonFairytaleGuardStompPreview','-DungeonFairytaleGuardMoveRigPreview')}
$process=Start-Process -FilePath (Join-Path $EngineRoot 'Engine\Binaries\Win64\UnrealEditor.exe') -ArgumentList $arguments -WindowStyle Normal -PassThru
Write-Output "Native room PID $($process.Id). Enter starts; WASD moves; J attacks; Shift dodges; Space jumps; E interacts; R starts a fresh Run."
if($LightArtTrial){Write-Output 'Entry display LGT: after Enter press E and wait for the actual .50s equipment commit.'}
Write-Output 'Normal3-enemy room; manual input only. Original SWD/LGT Ready/Walk/primaries/Hurt/Death/Dodge and Guard Stomp50 gates remain. No automatic input or diagnostic damage.'
Write-Output 'Guard Move7 is one bounded seven-component trial; fixed axe is included once. Rotated-leg outline, diagonal/reversal contact and final content acceptance remain open.'
Write-Output "Log $log"
Write-Output 'Hero Air6 is a bounded SWD/NoArmor and SWD/LGT preview. Landing/Ready joins remain WIP; no formal unit acceptance.'
