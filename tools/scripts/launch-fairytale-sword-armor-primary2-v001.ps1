param([string]$EngineRoot = 'G:\UE_5.5')
$ErrorActionPreference = 'Stop'
$workspace = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\..'))
$python = Join-Path $workspace 'tools\runtime\asset-gen\Scripts\python.exe'
$checker = Join-Path $PSScriptRoot 'verify-sword-primary2-fit-v004.py'
& $python -B -X utf8 $checker --preflight-only
if ($LASTEXITCODE -ne 0) { throw 'Two-stage matching armor preflight failed.' }
$project=Join-Path $workspace 'UnrealGame\CodexDungeon.uproject'
$editor=Join-Path $EngineRoot 'Engine\Binaries\Win64\UnrealEditor.exe'
$log=Join-Path $workspace ('UnrealGame\Saved\Bootstrap\play-fairytale-sword-armor-primary2-v001-{0}.log' -f (Get-Date -Format 'yyyyMMdd-HHmmss-fff'))
$arguments=@(('"{0}"' -f $project),'/Game/Maps/FirstRoom','-game','-windowed','-ResX=1280','-ResY=720','-NoSplash','-NoLiveCoding','-nop4',
 '-DungeonCandidateSprites','-DungeonSceneExplorationPreview','-DungeonFairytaleSwordBodyPreview','-DungeonFairytaleSwordBodyV002Preview',
 '-DungeonFairytaleSwordArmorPrimary1Preview','-DungeonFairytaleSwordPrimary2Preview','-DungeonFairytaleSwordPrimary2BodyPreview','-DungeonFairytaleSwordPrimary2ArmorPreview',('-abslog="{0}"' -f $log))
# This launcher is for the user's interactive preview, not a background proof helper.
$process=Start-Process -FilePath $editor -ArgumentList $arguments -WindowStyle Normal -PassThru
Write-Output "Two-stage matching armor trial started: PID $($process.Id)"
Write-Output 'Enter starts; WASD/arrows move; J/left mouse attacks; press again in the final120ms recovery window to continue; A/D changes facing.'
Write-Output 'Ready and the first two attacks have matching chest/shoulders. Third attack and other visual states remain unfinished; gameplay mechanism may still enter third-stage placeholder.'
Write-Output 'Body max72px, interface hidden. Close the game window to exit.'
Write-Output "Log: $log"
