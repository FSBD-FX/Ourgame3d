param(
 [Parameter(Mandatory=$true)][string]$Snapshot,
 [Parameter(Mandatory=$true)][string]$Archive,
 [string]$ProjectRoot='F:\Ourgame',
 [string]$EngineRoot='G:\UE_5.5',
 [switch]$ValidateOnly
)
$ErrorActionPreference='Stop'
$workspace=[IO.Path]::GetFullPath($ProjectRoot)
$python=Join-Path $workspace 'tools\runtime\asset-gen\Scripts\python.exe'
$verifier=Join-Path $PSScriptRoot 'verify-leather-combo-proof-v001.py'
Push-Location -LiteralPath $workspace
try {
 $verified=& $python -B -X utf8 $verifier --snapshot $Snapshot --archive $Archive
 if($LASTEXITCODE -ne 0){throw 'Current build and native leather combo proof verification failed.'}
 $proof=$verified | ConvertFrom-Json
 if(-not $proof.actual_native_technical_verified -or $proof.current_full_automation_succeeded -ne 161 -or $proof.selected_phase_facing_pairs -ne 36){throw 'Current161/native36 proof missing.'}
 if($ValidateOnly){$verified;return}
 if(@(Get-Process -Name 'UnrealEditor*','UnrealBuildTool' -ErrorAction SilentlyContinue).Count){throw 'Close the existing Unreal session before starting this trial.'}
 $log=Join-Path $workspace ('UnrealGame\Saved\Bootstrap\play-leather-combo-{0}.log' -f (Get-Date -Format 'yyyyMMdd-HHmmss-fff'))
 $arguments=@(('"{0}"' -f (Join-Path $workspace 'UnrealGame\CodexDungeon.uproject')),'/Game/Maps/FirstRoom','-game','-windowed','-ResX=1280','-ResY=720','-NoSplash','-NoLiveCoding','-nop4',
  '-DungeonSceneExplorationPreview','-DungeonCandidateSprites','-DungeonFairytaleSwordBodyPreview','-DungeonFairytaleSwordBodyV002Preview','-DungeonFairytaleSwordArmorPrimary1Preview','-DungeonFairytaleSwordPrimary2Preview','-DungeonFairytaleSwordPrimary2BodyPreview','-DungeonFairytaleSwordPrimary2ArmorPreview','-DungeonFairytaleSwordPrimary3ArmorPreview',
  '-DungeonFairytaleLeatherReadyPreview','-DungeonFairytaleLeatherPrimary1Preview','-DungeonFairytaleLeatherPrimary2Preview','-DungeonFairytaleLeatherPrimary3Preview','-DungeonFairytaleSwordEquipmentBoundPreview',('-abslog="{0}"' -f $log))
 # Interactive trial: no automatic input or capture/proof actor.
 $process=Start-Process -FilePath (Join-Path $EngineRoot 'Engine\Binaries\Win64\UnrealEditor.exe') -ArgumentList $arguments -WindowStyle Normal -PassThru
 Write-Output "Soft leather combo trial started: PID $($process.Id). Enter starts; WASD moves; J attacks; E interacts."
 Write-Output 'Matching leather Ready and three attacks only. Other states are still being made; this is an art trial.'
 Write-Output "Log: $log"
} finally {Pop-Location}
