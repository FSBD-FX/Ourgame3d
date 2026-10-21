param([string]$EngineRoot='G:\UE_5.5',[string[]]$PresentationArgs=@('-DungeonFairytaleSwordEquipmentBoundPreview','-DungeonFairytaleSwordWalkPreview'))
$ErrorActionPreference='Stop'
$workspace='F:\Ourgame'
$project=Join-Path $workspace 'UnrealGame\CodexDungeon.uproject'
$editor=Join-Path $EngineRoot 'Engine\Binaries\Win64\UnrealEditor.exe'
if(-not (Test-Path -LiteralPath $project) -or -not (Test-Path -LiteralPath $editor)){throw 'Actual project/UE executable missing.'}
$log=Join-Path $workspace ('UnrealGame\Saved\Bootstrap\guard-bridge-play-{0}.log' -f (Get-Date -Format 'yyyyMMdd-HHmmss-fffffff'))
$arguments=@(('"{0}"' -f $project),'/Game/Maps/FirstRoom?DungeonFirstBatchGuardRoom','-game','-windowed','-ResX=1280','-ResY=720','-NoSplash','-NoLiveCoding','-nop4',('-abslog="{0}"' -f $log))
$arguments+=$PresentationArgs
$process=Start-Process -FilePath $editor -ArgumentList $arguments -WindowStyle Normal -PassThru
Write-Output "Native Bridge game PID $($process.Id); Enter starts, WASD moves, J attacks, Space jumps, E exits only after all3 slots, R restarts. Log $log"
