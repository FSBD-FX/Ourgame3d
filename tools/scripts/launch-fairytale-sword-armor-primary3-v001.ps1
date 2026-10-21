param(
 [string]$EngineRoot = 'G:\UE_5.5',
 [string]$Snapshot = 'source-assets/production/backups/2026-10-16_Primary3Armor48-fit-full141GREEN-v116'
)
$ErrorActionPreference = 'Stop'
$workspace = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\..'))
$python = Join-Path $workspace 'tools\runtime\asset-gen\Scripts\python.exe'
$checker = Join-Path $PSScriptRoot 'verify-sword-primary3-fit-v001.py'
& $python -B -X utf8 $checker --preflight-only --snapshot $Snapshot
if ($LASTEXITCODE -ne 0) { throw 'Three-stage matching armor preflight failed.' }
$project = Join-Path $workspace 'UnrealGame\CodexDungeon.uproject'
$editor = Join-Path $EngineRoot 'Engine\Binaries\Win64\UnrealEditor.exe'
$log = Join-Path $workspace ('UnrealGame\Saved\Bootstrap\play-fairytale-sword-armor-primary3-v001-{0}.log' -f (Get-Date -Format 'yyyyMMdd-HHmmss-fff'))
$arguments = @(('"{0}"' -f $project),'/Game/Maps/FirstRoom','-game','-windowed','-ResX=1280','-ResY=720','-NoSplash','-NoLiveCoding','-nop4',
 '-DungeonCandidateSprites','-DungeonSceneExplorationPreview','-DungeonFairytaleSwordBodyPreview','-DungeonFairytaleSwordBodyV002Preview',
 '-DungeonFairytaleSwordArmorPrimary1Preview','-DungeonFairytaleSwordPrimary2Preview','-DungeonFairytaleSwordPrimary2BodyPreview',
 '-DungeonFairytaleSwordPrimary2ArmorPreview','-DungeonFairytaleSwordPrimary3ArmorPreview',('-abslog="{0}"' -f $log))
# User-facing interactive preview, not a background proof helper.
$process = Start-Process -FilePath $editor -ArgumentList $arguments -WindowStyle Normal -PassThru
Write-Output "Three-stage armor art trial started: PID $($process.Id)"
Write-Output 'Enter starts; WASD/arrows move; J/left mouse attacks. A fresh press during the final120ms recovery queues the next stage.'
Write-Output 'Ready and three ground attacks have matching chest/shoulders. Walk/air/hurt/death/skills and complete weapon/armor identity remain unfinished.'
Write-Output 'Body max72px; interface hidden. This is an art trial; close its window to exit.'
Write-Output "Log: $log"
