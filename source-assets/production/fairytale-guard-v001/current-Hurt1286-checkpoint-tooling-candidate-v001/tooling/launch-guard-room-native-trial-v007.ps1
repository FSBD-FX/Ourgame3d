param([string]$EngineRoot='G:\UE_5.5',[string]$Snapshot='',[string]$RootCheckpoint='source-assets/production/fairytale-guard-v001/root-Hurt1286-checkpoint-v001/manual-input-v001.json',[switch]$LightArtTrial,[switch]$GuardFullArt,[switch]$ValidateOnly)
$ErrorActionPreference='Stop';$workspace='F:\Ourgame'
$python=Join-Path $workspace 'tools/runtime/asset-gen/Scripts/python.exe'
$checker=Join-Path $PSScriptRoot 'verify-Hurt1286-manual-input-v001.py'
$checkpointPath=if([IO.Path]::IsPathRooted($RootCheckpoint)){[IO.Path]::GetFullPath($RootCheckpoint)}else{[IO.Path]::GetFullPath((Join-Path $workspace $RootCheckpoint))}
$verified=& $python -B -X utf8 $checker --manual-input $checkpointPath
if($LASTEXITCODE -ne 0){throw 'Actual fresh Source/Content1286/DLL/full187/Guard44/Hurt32 source-profile validation failed.'}
$facts=$verified|ConvertFrom-Json
if($Snapshot){$requestedSnapshot=if([IO.Path]::IsPathRooted($Snapshot)){[IO.Path]::GetFullPath($Snapshot)}else{[IO.Path]::GetFullPath((Join-Path $workspace $Snapshot))};$checkpointData=Get-Content -LiteralPath $checkpointPath -Raw -Encoding UTF8|ConvertFrom-Json;if($requestedSnapshot -ne [IO.Path]::GetFullPath($checkpointData.snapshot_directory)){throw 'Explicit Snapshot differs from fresh Root checkpoint.'}}
if($ValidateOnly){[ordered]@{compiled_inputs_verified=$true;strict_registry=$facts.strict_registry;source_files=$facts.source_files;production_files=$facts.production_files;manual_light_source=[bool]$LightArtTrial;guard_full_art=[bool]$GuardFullArt;hurt_art=$true;automatic_inputs=$false;diagnostic_damage=$false;UE_started=$false}|ConvertTo-Json;return}
if(@(Get-Process -Name 'UnrealEditor*','UnrealBuildTool' -ErrorAction SilentlyContinue).Count){throw 'Close UE/UBT before starting the visible native trial.'}
$log=Join-Path $workspace ('UnrealGame\Saved\Bootstrap\guard-room-Hurt1286-trial-'+(Get-Date -Format 'yyyyMMdd-HHmmss-fffffff')+'.log')
$arguments=@(('"{0}"' -f (Join-Path $workspace 'UnrealGame\CodexDungeon.uproject')),'/Game/Maps/FirstRoom?DungeonFirstBatchGuardRoom','-game','-windowed','-ResX=1280','-ResY=720','-NoSplash','-NoLiveCoding','-nop4','-DungeonCandidateSprites','-DungeonFairytaleSwordBodyPreview','-DungeonFairytaleSwordBodyV002Preview','-DungeonFairytaleSwordArmorPrimary1Preview','-DungeonFairytaleSwordPrimary2Preview','-DungeonFairytaleSwordPrimary2BodyPreview','-DungeonFairytaleSwordPrimary2ArmorPreview','-DungeonFairytaleSwordPrimary3ArmorPreview','-DungeonFairytaleLeatherReadyPreview','-DungeonFairytaleLeatherPrimary1Preview','-DungeonFairytaleLeatherPrimary2Preview','-DungeonFairytaleLeatherPrimary3Preview','-DungeonFairytaleSwordEquipmentBoundPreview','-DungeonFairytaleSwordWalkPreview','-DungeonFairytaleSwordHurtPreview',('-abslog="{0}"' -f $log))
if($LightArtTrial){$arguments+='-DungeonGuardRoomManualLightSource'}
if($GuardFullArt){$arguments+='-DungeonFairytaleGuardFullPreview'}
$process=Start-Process -FilePath (Join-Path $EngineRoot 'Engine\Binaries\Win64\UnrealEditor.exe') -ArgumentList $arguments -WindowStyle Normal -PassThru
Write-Output "Native room PID $($process.Id). Enter starts; WASD moves; J attacks; Shift dodges; Space jumps; E interacts; R starts a fresh Run."
if($LightArtTrial){Write-Output 'Entry display LGT: after Enter press E and wait for the actual .50s equipment commit.'}
Write-Output 'SWD/LGT Hurt4 scoped trial. Manual input only; current source readiness does not claim a recorded Hurt/native visual pass.'
if($GuardFullArt){Write-Output 'Guard known44 scoped art trial; Move/StompActive/StompRecovery remain procedural gaps. Final enemy/foot-lock/audio acceptance pending.'}
Write-Output "Log $log"
