param([string]$EngineRoot='G:\UE_5.5',[string]$Snapshot='source-assets/production/backups/v132-guard-known44-184G',[switch]$LightArtTrial,[switch]$GuardFullArt,[switch]$ValidateOnly)
$ErrorActionPreference='Stop';$workspace='F:\Ourgame'
$python=Join-Path $workspace 'tools/runtime/asset-gen/Scripts/python.exe'
$checker=Join-Path $workspace 'source-assets/production/fairytale-guard-v001/presentation-full-known44-observer-tooling-candidate-v002/tooling/verify-known44-axecycle-v002.py'
$prereg=Join-Path $workspace 'source-assets/production/fairytale-guard-v001/root-full-registration-v001/v132-known44-AxeCycle-Root-prereg-v002.json'
& $python -B -X utf8 $checker --snapshot $Snapshot --root-prereg $prereg --source-only | Out-Null
if($LASTEXITCODE -ne 0){throw 'Current Source/Content/DLL/strict184/Guard44 prereg validation failed.'}
if($ValidateOnly){[ordered]@{compiled_inputs_verified=$true;strict_registry=184;manual_light_source=[bool]$LightArtTrial;guard_full_art=[bool]$GuardFullArt;automatic_inputs=$false;diagnostic_damage=$false;UE_started=$false}|ConvertTo-Json;return}
if(@(Get-Process -Name 'UnrealEditor*','UnrealBuildTool' -ErrorAction SilentlyContinue).Count){throw 'Close UE/UBT before starting the visible native trial.'}
$log=Join-Path $workspace ('UnrealGame\Saved\Bootstrap\guard-room-trial-'+(Get-Date -Format 'yyyyMMdd-HHmmss-fffffff')+'.log')
$arguments=@(('"{0}"' -f (Join-Path $workspace 'UnrealGame\CodexDungeon.uproject')),'/Game/Maps/FirstRoom?DungeonFirstBatchGuardRoom','-game','-windowed','-ResX=1280','-ResY=720','-NoSplash','-NoLiveCoding','-nop4','-DungeonCandidateSprites','-DungeonFairytaleSwordBodyPreview','-DungeonFairytaleSwordBodyV002Preview','-DungeonFairytaleSwordArmorPrimary1Preview','-DungeonFairytaleSwordPrimary2Preview','-DungeonFairytaleSwordPrimary2BodyPreview','-DungeonFairytaleSwordPrimary2ArmorPreview','-DungeonFairytaleSwordPrimary3ArmorPreview','-DungeonFairytaleLeatherReadyPreview','-DungeonFairytaleLeatherPrimary1Preview','-DungeonFairytaleLeatherPrimary2Preview','-DungeonFairytaleLeatherPrimary3Preview','-DungeonFairytaleSwordEquipmentBoundPreview','-DungeonFairytaleSwordWalkPreview',('-abslog="{0}"' -f $log))
if($LightArtTrial){$arguments+='-DungeonGuardRoomManualLightSource'}
if($GuardFullArt){$arguments+='-DungeonFairytaleGuardFullPreview'}
$process=Start-Process -FilePath (Join-Path $EngineRoot 'Engine\Binaries\Win64\UnrealEditor.exe') -ArgumentList $arguments -WindowStyle Normal -PassThru
Write-Output "Native room PID $($process.Id). Enter starts; WASD moves; J attacks; Shift dodges; Space jumps; E interacts; R starts a fresh Run."
if($LightArtTrial){Write-Output 'Entry display LGT: after Enter press E and wait for the actual .50s equipment commit.'}
if($GuardFullArt){Write-Output 'Guard known44 scoped art trial. Move/StompActive/StompRecovery remain explicit procedural gaps; final complete enemy and audio review pending.'}
Write-Output "Log $log"
