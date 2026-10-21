param([string]$EngineRoot='G:\UE_5.5',[string]$Snapshot='',[string]$RootCheckpoint='',[switch]$LightArtTrial,[switch]$GuardFullArt,[switch]$ValidateOnly)
$ErrorActionPreference='Stop';$workspace='F:\Ourgame'
if(-not $RootCheckpoint){throw 'Root must select one non-template approved Dodge1364 checkpoint with an actual196 GREEN compiled snapshot.'}
$python=Join-Path $workspace 'tools/runtime/asset-gen/Scripts/python.exe'
$checker=Join-Path $PSScriptRoot 'verify-Dodge1364-manual-input-v001.py'
$checkpointPath=if([IO.Path]::IsPathRooted($RootCheckpoint)){[IO.Path]::GetFullPath($RootCheckpoint)}else{[IO.Path]::GetFullPath((Join-Path $workspace $RootCheckpoint))}
$verifyArguments=@('-B','-X','utf8',$checker,'--manual-input',$checkpointPath)
if($Snapshot){$verifyArguments+=@('--snapshot',$Snapshot)}
$verified=& $python @verifyArguments
if($LASTEXITCODE -ne 0){throw 'Fresh compiled196/dynamicSource/1364/DLL/Dodge33/Death40/Guard44+Stomp6 inputs failed; UE has not been started.'}
$facts=$verified|ConvertFrom-Json
if($ValidateOnly){[ordered]@{compiled_inputs_verified=$true;strict_registry=$facts.strict_registry;source_files=$facts.source_files;production_files=$facts.production_files;manual_light_source=[bool]$LightArtTrial;guard_full_art=[bool]$GuardFullArt;death_art=$true;dodge_art=$true;dodge_preload=33;stomp_overlay=[bool]($GuardFullArt -or $LightArtTrial);oldGuardProfileUnique=44;StompOverlayUnique=50;automatic_inputs=$false;diagnostic_damage=$false;debug_range_enabled=$false;traditional_HUD_shown=$false;UE_started=$false}|ConvertTo-Json;return}
if(@(Get-Process -Name 'UnrealEditor*','UnrealBuildTool' -ErrorAction SilentlyContinue).Count){throw 'Close UE/UBT before starting the visible native trial.'}
$log=Join-Path $workspace ('UnrealGame\Saved\Bootstrap\guard-room-Dodge1364-trial-'+(Get-Date -Format 'yyyyMMdd-HHmmss-fffffff')+'.log')
$arguments=@(('"{0}"' -f (Join-Path $workspace 'UnrealGame\CodexDungeon.uproject')),'/Game/Maps/FirstRoom?DungeonFirstBatchGuardRoom','-game','-windowed','-ResX=1280','-ResY=720','-NoSplash','-NoLiveCoding','-nop4','-DungeonCandidateSprites','-DungeonFairytaleSwordBodyPreview','-DungeonFairytaleSwordBodyV002Preview','-DungeonFairytaleSwordArmorPrimary1Preview','-DungeonFairytaleSwordPrimary2Preview','-DungeonFairytaleSwordPrimary2BodyPreview','-DungeonFairytaleSwordPrimary2ArmorPreview','-DungeonFairytaleSwordPrimary3ArmorPreview','-DungeonFairytaleLeatherReadyPreview','-DungeonFairytaleLeatherPrimary1Preview','-DungeonFairytaleLeatherPrimary2Preview','-DungeonFairytaleLeatherPrimary3Preview','-DungeonFairytaleSwordEquipmentBoundPreview','-DungeonFairytaleSwordWalkPreview','-DungeonFairytaleSwordHurtPreview','-DungeonFairytaleSwordDeathPreview','-DungeonFairytaleSwordDodgePreview',('-abslog="{0}"' -f $log))
if($LightArtTrial){$arguments+='-DungeonGuardRoomManualLightSource'}
if($GuardFullArt -or $LightArtTrial){$arguments+=@('-DungeonFairytaleGuardFullPreview','-DungeonFairytaleGuardStompPreview')}
$process=Start-Process -FilePath (Join-Path $EngineRoot 'Engine\Binaries\Win64\UnrealEditor.exe') -ArgumentList $arguments -WindowStyle Normal -PassThru
Write-Output "Native room PID $($process.Id). Enter starts; WASD moves; J attacks; Shift dodges; Space jumps; E interacts; R starts a fresh Run."
if($LightArtTrial){Write-Output 'Entry display LGT: after Enter press E and wait for the actual .50s equipment commit.'}
Write-Output 'Normal3-enemy room; manual input only. SWD/LGT Death5 is a scoped trial; source readiness does not claim native visual/final acceptance.'
if($GuardFullArt -or $LightArtTrial){Write-Output 'Guard scoped Stomp50 overlay: old44 + approvedStomp6; Move6 remains gap. Manual input only; no forced damage. Join/floor/final acceptance is separate.'}
Write-Output "Log $log"
