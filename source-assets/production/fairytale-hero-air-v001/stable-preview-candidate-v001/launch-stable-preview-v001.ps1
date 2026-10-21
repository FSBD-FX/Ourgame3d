param([string]$StageRoot='F:/Ourgame/Playables/钟盔轻甲-v142-CM52f906',[string]$RootApproval='',[switch]$LightArtTrial,[switch]$GuardFullArt,[switch]$ValidateOnly)
$ErrorActionPreference='Stop'
$StageRoot=[IO.Path]::GetFullPath($StageRoot)
if(-not $RootApproval){$RootApproval=Join-Path $StageRoot '_proof/Root-stable-approval-v001.json'}
$approval=Get-Content -LiteralPath $RootApproval -Raw|ConvertFrom-Json
if($approval.schema -ne 'HeroAir6-Root-stable-manual-approval-v001' -or $approval.RootApproved -ne $true -or $approval.is_template -ne $false -or $approval.approval_scope -ne 'LIMITED_WIP' -or $approval.manual_trial_allowed -ne $true -or $approval.Root_staged_visible_keyframes_reviewed -ne $true -or $approval.full_realtime_playback_reviewed -ne $false -or $approval.audio_listened -ne $false -or $approval.known_pose_join_refinement_open -ne $true -or $approval.FinalAccepted -ne $false){throw 'Stable candidate lacks actual Root LIMITED_WIP approval; UE has not been started.'}
if($StageRoot -ne [IO.Path]::GetFullPath('F:/Ourgame/Playables/钟盔轻甲-v142-CM52f906') -or $StageRoot -ne [IO.Path]::GetFullPath($approval.stage_root)){throw 'Different stable project root.'}
function Assert-PhysicalPath([string]$Path,[switch]$File){
 $current=[IO.Path]::GetFullPath($Path)
 while($current){
  if(Test-Path -LiteralPath $current){$item=Get-Item -LiteralPath $current -Force;if(($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -or $item.LinkType){throw "Linked path rejected: $current"}}
  $parent=[IO.Path]::GetDirectoryName($current);if($parent -eq $current){break};$current=$parent
 }
 if($File -and -not (Test-Path -LiteralPath $Path -PathType Leaf)){throw "Physical file missing: $Path"}
}
function Stage-Path([string]$Member){
 if([IO.Path]::IsPathRooted($Member) -or $Member.Contains('\') -or @($Member.Split('/')|Where-Object {$_ -eq '..'}).Count){throw 'Expected a clean staged relative member.'}
 $path=[IO.Path]::GetFullPath((Join-Path $StageRoot $Member))
 if(-not $path.StartsWith($StageRoot+[IO.Path]::DirectorySeparatorChar,[StringComparison]::OrdinalIgnoreCase)){throw 'Member leaves physical stage.'}
 Assert-PhysicalPath $path
 $path
}
function Assert-StagePin($Pin){
 if(-not $Pin){throw 'Required staged pin missing.'}
 $path=Stage-Path $Pin.path;Assert-PhysicalPath $path -File;$file=Get-Item -LiteralPath $path -Force
 if($file.Length -ne $Pin.bytes -or (Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash.ToLowerInvariant() -ne $Pin.sha256){throw "Staged bytes/SHA differ: $path"}
}
function Read-StageJson($Pin){Assert-StagePin $Pin;Get-Content -LiteralPath (Stage-Path $Pin.path) -Raw|ConvertFrom-Json}
function Same-StagePin($A,$B){$A -and $B -and $A.path -ceq $B.path -and $A.bytes -eq $B.bytes -and $A.sha256 -eq $B.sha256}
Assert-PhysicalPath $StageRoot
if([IO.Path]::GetFullPath($RootApproval) -ne (Stage-Path '_proof/Root-stable-approval-v001.json')){throw 'Root approval must be local to the stable stage.'}
$manifest=Read-StageJson $approval.runtime_manifest_pin
if($manifest.schema -ne 'HeroAir6-physical-runtime-snapshot-v001' -or $manifest.actual_stage_copy_succeeded -ne $true -or $manifest.source_CM_sha256 -ne '52f906018a042d006db3470ec2fa7b4603a6b54e2489ab33d2bdff0bf309cd62' -or $manifest.runtime_count -ne 1778 -or $manifest.runtime_bytes -ne 143122086 -or $manifest.engine_build_id -ne '37670630' -or $manifest.live_development_Source_needed_at_launch -ne $false -or $manifest.source_copied -ne $false -or $manifest.source_and_target_links_created -ne $false){throw 'Stable runtime snapshot differs.'}
if([IO.Path]::GetFullPath($manifest.stage_root) -ne $StageRoot -or $manifest.source_runtime_two_pass_verified -ne $true -or $manifest.target_runtime_two_pass_verified -ne $true){throw 'Actual two-pass physical copy required.'}
$receipt=Read-StageJson $approval.stage_copy_receipt_pin
if($receipt.schema -ne 'HeroAir6-actual-stage-copy-receipt-v001' -or $receipt.success -ne $true -or $receipt.verification_passes -ne 2 -or $receipt.source_and_target_twoSHA_mismatches -ne 0 -or $receipt.physical_copy_no_links -ne $true -or $receipt.exact_runtime_membership_verified -ne $true -or -not (Same-StagePin $receipt.runtime_manifest_pin $approval.runtime_manifest_pin)){throw 'Actual stable copy receipt differs.'}
$names=[System.Collections.Generic.HashSet[string]]::new([StringComparer]::Ordinal)
[long]$total=0
foreach($row in $manifest.runtime_files){if(-not $names.Add([string]$row.path)){throw 'Duplicate staged runtime member.'};Assert-StagePin $row;$total+=$row.bytes}
if($names.Count -ne 1778 -or $total -ne 143122086 -or -not $names.Contains('CodexDungeon.uproject') -or -not $names.Contains('Binaries/Win64/UnrealEditor-CodexDungeon.dll')){throw 'Stable runtime totals/core membership differ.'}
foreach($directory in @('Config','Content','Binaries','Plugins')){
 $expected=[System.Collections.Generic.HashSet[string]]::new([StringComparer]::Ordinal)
 foreach($name in $names){if($name.StartsWith($directory+'/',[StringComparison]::Ordinal)){[void]$expected.Add($name)}}
 $actual=[System.Collections.Generic.HashSet[string]]::new([StringComparer]::Ordinal)
 $base=Stage-Path $directory
 foreach($item in Get-ChildItem -LiteralPath $base -Recurse -Force){Assert-PhysicalPath $item.FullName;if(-not $item.PSIsContainer){[void]$actual.Add($item.FullName.Substring($StageRoot.Length+1).Replace('\','/'))}}
 if(-not $actual.SetEquals($expected)){throw "Stable runtime directory membership differs: $directory"}
}
if(@(Get-ChildItem -LiteralPath $StageRoot -File -Force -Filter '*.uproject').Count -ne 1 -or (Test-Path -LiteralPath (Join-Path $StageRoot 'Source'))){throw 'Unexpected source/project in stable stage.'}
foreach($row in $manifest.metadata_files){Assert-StagePin $row}
if(-not @($manifest.metadata_files|Where-Object {(Stage-Path $_.path) -eq [IO.Path]::GetFullPath($PSCommandPath)}).Count){throw 'Running stable launcher is absent from copied manifest.'}
$cmRow=@($manifest.metadata_files|Where-Object {$_.path -ceq '_proof/evidence/compiled-source-manifest.json'})
if($cmRow.Count -ne 1 -or $cmRow[0].sha256 -ne '52f906018a042d006db3470ec2fa7b4603a6b54e2489ab33d2bdff0bf309cd62'){throw 'Fixed compilation history capsule missing.'}
$cm=Read-StageJson $cmRow[0]
if($cm.source_files -ne 296 -or $cm.production_files -ne 1419 -or $cm.registered_tests -ne 203 -or $cm.passed -ne 203 -or $cm.failed -ne 0 -or $cm.notRun -ne 0){throw 'Retained compilation evidence differs.'}
# Historical CM/freezes retain old paths as evidence only. Never resolve their member paths here.
$EngineRoot=[IO.Path]::GetFullPath('G:/UE_5.5')
foreach($row in $manifest.engine_files){
 $path=[IO.Path]::GetFullPath($row.path)
 if(-not $path.StartsWith($EngineRoot+[IO.Path]::DirectorySeparatorChar,[StringComparison]::OrdinalIgnoreCase)){throw 'Different installed engine dependency.'}
 Assert-PhysicalPath $path -File;$file=Get-Item -LiteralPath $path -Force
 if($file.Length -ne $row.bytes -or (Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash.ToLowerInvariant() -ne $row.sha256){throw 'Installed fixed engine marker/EXE changed.'}
}
foreach($path in @((Join-Path $EngineRoot 'Engine/Binaries/Win64/UnrealEditor.modules'),(Stage-Path 'Binaries/Win64/UnrealEditor.modules'),(Stage-Path 'Plugins/UnrealMCP/Binaries/Win64/UnrealEditor.modules'))){if((Get-Content -LiteralPath $path -Raw|ConvertFrom-Json).BuildId -ne '37670630'){throw 'Installed engine/project/plugin BuildId differs.'}}
$native=Read-StageJson $approval.staged_native_proof_pin
if($native.schema -ne 'HeroAir6-Root-staged-native-proof-v001' -or $native.RootApproved -ne $true -or $native.is_template -ne $false -or $native.actual_editor_game_native_execution -ne $true -or $native.actual_staged_project_and_DLL_loaded -ne $true -or $native.actual_process_id -le 0 -or $native.native_process_exit_code -ne 0 -or $native.Root_verified_before_and_after_runtime_equal -ne $true -or $native.normal_manual_flags_verified -ne $true -or $native.engine_build_id -ne '37670630' -or $native.source_CM_sha256 -ne $manifest.source_CM_sha256 -or -not (Same-StagePin $native.runtime_manifest_pin $approval.runtime_manifest_pin) -or [IO.Path]::GetFullPath($native.staged_project_path) -ne (Stage-Path 'CodexDungeon.uproject') -or $native.FinalAccepted -ne $false){throw 'Root actual staged native proof required.'}
if(-not @($native.evidence_pins).Count){throw 'Actual staged native evidence pins missing.'}
foreach($row in $native.evidence_pins){Assert-StagePin $row}
$null=Read-StageJson $approval.Root_visible_review_receipt_pin
if($ValidateOnly){[ordered]@{stable_runtime_verified=$true;runtime_files=1778;runtime_bytes=143122086;physical_copies=$true;source_CM_sha256=$manifest.source_CM_sha256;live_development_Source_verified=$false;retained_compilation_history_verified=$true;Root_staged_native_proof_verified=$true;approval_scope='LIMITED_WIP';full_realtime_playback_reviewed=$false;audio_listened=$false;known_pose_join_refinement_open=$true;automatic_inputs=$false;diagnostic_damage=$false;UE_started=$false;FinalAccepted=$false}|ConvertTo-Json;return}
if(@(Get-Process -Name 'UnrealEditor*','UnrealBuildTool' -ErrorAction SilentlyContinue).Count){throw 'Close UE/UBT before the stable manual trial.'}
$log=Join-Path $StageRoot ('Saved/Bootstrap/stable-manual-'+(Get-Date -Format 'yyyyMMdd-HHmmss-fffffff')+'.log')
$arguments=@(('"{0}"' -f (Stage-Path 'CodexDungeon.uproject')),'/Game/Maps/FirstRoom?DungeonFirstBatchGuardRoom','-game','-windowed','-ResX=1280','-ResY=720','-NoSplash','-NoLiveCoding','-nop4','-DungeonCandidateSprites','-DungeonFairytaleSwordBodyPreview','-DungeonFairytaleSwordBodyV002Preview','-DungeonFairytaleSwordArmorPrimary1Preview','-DungeonFairytaleSwordPrimary2Preview','-DungeonFairytaleSwordPrimary2BodyPreview','-DungeonFairytaleSwordPrimary2ArmorPreview','-DungeonFairytaleSwordPrimary3ArmorPreview','-DungeonFairytaleLeatherReadyPreview','-DungeonFairytaleLeatherPrimary1Preview','-DungeonFairytaleLeatherPrimary2Preview','-DungeonFairytaleLeatherPrimary3Preview','-DungeonFairytaleSwordEquipmentBoundPreview','-DungeonFairytaleSwordWalkPreview','-DungeonFairytaleSwordHurtPreview','-DungeonFairytaleSwordDeathPreview','-DungeonFairytaleSwordDodgePreview','-DungeonFairytaleSwordAirPreview',('-abslog="{0}"' -f $log))
if($LightArtTrial){$arguments+='-DungeonGuardRoomManualLightSource'}
if($GuardFullArt -or $LightArtTrial){$arguments+=@('-DungeonFairytaleGuardFullPreview','-DungeonFairytaleGuardStompPreview','-DungeonFairytaleGuardMoveRigPreview')}
$process=Start-Process -FilePath (Join-Path $EngineRoot 'Engine/Binaries/Win64/UnrealEditor.exe') -ArgumentList $arguments -WorkingDirectory $StageRoot -WindowStyle Normal -PassThru
Write-Output "Stable WIP PID $($process.Id). Enter starts; WASD moves; J attacks; Shift dodges; Space jumps; E interacts; R restarts."
Write-Output 'After Enter press E and wait for the normal .50s equipment commit. Landing/Ready joins remain under refinement.'
