param(
 [string]$EngineRoot='G:\UE_5.5',
 [string]$Snapshot='source-assets/production/backups/2026-10-16_EquipmentBound-V002-current141GREEN-beforeNative-v118'
)
$ErrorActionPreference='Stop'
$workspace=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\..'))
& (Join-Path $workspace 'tools\runtime\asset-gen\Scripts\python.exe') -B -X utf8 (Join-Path $PSScriptRoot 'verify-equipment-bound-current-build-v001.py') --snapshot $Snapshot
if($LASTEXITCODE -ne 0){throw 'Current native equipment-bound build preflight failed.'}
$log=Join-Path $workspace ('UnrealGame\Saved\Bootstrap\play-equipment-bound-{0}.log' -f (Get-Date -Format 'yyyyMMdd-HHmmss-fff'))
$arguments=@(('"{0}"' -f (Join-Path $workspace 'UnrealGame\CodexDungeon.uproject')),'/Game/Maps/FirstRoom','-game','-windowed','-ResX=1280','-ResY=720','-NoSplash','-NoLiveCoding','-nop4','-DungeonCandidateSprites','-DungeonSceneExplorationPreview','-DungeonFairytaleSwordEquipmentBoundPreview',('-abslog="{0}"' -f $log))
# Explicit interactive preview. No QA Actor, generated QA sources or automatic input.
$process=Start-Process -FilePath (Join-Path $EngineRoot 'Engine\Binaries\Win64\UnrealEditor.exe') -ArgumentList $arguments -WindowStyle Normal -PassThru
Write-Output "Equipment-bound preview started: PID $($process.Id)"
Write-Output 'Enter starts. WASD/arrows move. J/left mouse attacks; fresh press near the end queues the next stage. E interacts with a nearby real source; Enter confirms an opened slot selection.'
Write-Output 'Military sword with no armor or actual light armor has current Ready/three-stage art. Other armor and unsupported movement/equip states remain explicit bell placeholders; full states and audio acceptance are unfinished.'
Write-Output 'Body max72px; game interface hidden. Close the game window to exit.'
Write-Output "Log: $log"
