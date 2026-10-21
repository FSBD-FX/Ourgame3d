param([string]$EngineRoot='G:\UE_5.5',[string]$Snapshot='source-assets/production/backups/v130-guard-partial-181G',[switch]$LightArtTrial,[switch]$GuardPartialArt,[switch]$ValidateOnly)
$ErrorActionPreference='Stop';$workspace='F:\Ourgame'
$python=Join-Path $workspace 'tools/runtime/asset-gen/Scripts/python.exe'
$checker=Join-Path $workspace 'source-assets/production/fairytale-guard-v001/presentation-candidate-v002/tooling/verify-guard-art-partial-v002.py'
$prereg=Join-Path $workspace 'source-assets/production/fairytale-guard-v001/root-trial-registration-v001/v130-partial-art-root-prereg-v001.json'
& $python -B -X utf8 $checker --snapshot $Snapshot --root-prereg $prereg --source-only | Out-Null
if($LASTEXITCODE -ne 0){throw 'Current Source/Content/DLL/strict181/Guard16 prereg validation failed.'}
if($ValidateOnly){[ordered]@{compiled_inputs_verified=$true;strict_registry=181;manual_light_source=[bool]$LightArtTrial;guard_partial_art=[bool]$GuardPartialArt;automatic_inputs=$false;diagnostic_damage=$false;UE_started=$false}|ConvertTo-Json;return}
if(@(Get-Process -Name 'UnrealEditor*','UnrealBuildTool' -ErrorAction SilentlyContinue).Count){throw 'Close UE/UBT before starting the visible native trial.'}
$log=Join-Path $workspace ('UnrealGame\Saved\Bootstrap\guard-room-trial-'+(Get-Date -Format 'yyyyMMdd-HHmmss-fffffff')+'.log')
$arguments=@(('"{0}"' -f (Join-Path $workspace 'UnrealGame\CodexDungeon.uproject')),'/Game/Maps/FirstRoom?DungeonFirstBatchGuardRoom','-game','-windowed','-ResX=1280','-ResY=720','-NoSplash','-NoLiveCoding','-nop4','-DungeonCandidateSprites','-DungeonFairytaleSwordBodyPreview','-DungeonFairytaleSwordBodyV002Preview','-DungeonFairytaleSwordArmorPrimary1Preview','-DungeonFairytaleSwordPrimary2Preview','-DungeonFairytaleSwordPrimary2BodyPreview','-DungeonFairytaleSwordPrimary2ArmorPreview','-DungeonFairytaleSwordPrimary3ArmorPreview','-DungeonFairytaleLeatherReadyPreview','-DungeonFairytaleLeatherPrimary1Preview','-DungeonFairytaleLeatherPrimary2Preview','-DungeonFairytaleLeatherPrimary3Preview','-DungeonFairytaleSwordEquipmentBoundPreview','-DungeonFairytaleSwordWalkPreview',('-abslog="{0}"' -f $log))
if($LightArtTrial){$arguments+='-DungeonGuardRoomManualLightSource'}
if($GuardPartialArt){$arguments+='-DungeonFairytaleGuardPartialPreview'}
$process=Start-Process -FilePath (Join-Path $EngineRoot 'Engine\Binaries\Win64\UnrealEditor.exe') -ArgumentList $arguments -WindowStyle Normal -PassThru
Write-Output "Native room PID $($process.Id). Enter starts; WASD moves; J attacks; Shift dodges; Space jumps; E interacts; R starts a fresh Run."
if($LightArtTrial){Write-Output 'Entry display LGT: after Enter press E and wait for the actual .50s equipment commit.'}
if($GuardPartialArt){Write-Output 'Guard partial art: Wake/Ready/AxeWindup only. All remaining Guard actions retain explicit procedural gaps.'}
Write-Output "Log $log"
