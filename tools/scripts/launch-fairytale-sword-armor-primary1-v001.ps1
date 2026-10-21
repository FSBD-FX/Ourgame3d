param([string]$EngineRoot = 'G:\UE_5.5')
$ErrorActionPreference = 'Stop'
$workspace = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\..'))
$project = Join-Path $workspace 'UnrealGame\CodexDungeon.uproject'
$map = Join-Path $workspace 'UnrealGame\Content\Maps\FirstRoom.umap'
$editor = Join-Path $EngineRoot 'Engine\Binaries\Win64\UnrealEditor.exe'
$python = Join-Path $workspace 'tools\runtime\asset-gen\Scripts\python.exe'
$checker = Join-Path $PSScriptRoot 'verify-sword-armor-primary1-v001.py'
foreach ($path in @($project, $map, $editor, $python, $checker)) {
    if (-not (Test-Path -LiteralPath $path -PathType Leaf)) { throw "Required preview file is missing: $path" }
}
& $python -B -X utf8 $checker --preflight-only
if ($LASTEXITCODE -ne 0) { throw 'Imported matching armor trial preflight failed.' }
$logDirectory = Join-Path $workspace 'UnrealGame\Saved\Bootstrap'
[IO.Directory]::CreateDirectory($logDirectory) | Out-Null
$log = Join-Path $logDirectory ('play-fairytale-sword-armor-primary1-v001-{0}.log' -f (Get-Date -Format 'yyyyMMdd-HHmmss-fff'))
$arguments = @(
    ('"{0}"' -f $project), '/Game/Maps/FirstRoom', '-game', '-windowed',
    '-ResX=1280', '-ResY=720', '-NoSplash', '-NoLiveCoding', '-nop4',
    '-DungeonCandidateSprites', '-DungeonSceneExplorationPreview',
    '-DungeonFairytaleSwordBodyPreview', '-DungeonFairytaleSwordBodyV002Preview', '-DungeonFairytaleSwordArmorPrimary1Preview',
    ('-abslog="{0}"' -f $log)
)
$process = Start-Process -FilePath $editor -ArgumentList $arguments -WindowStyle Normal -PassThru
Write-Output "Ready and first-cut chest/shoulders preview started: PID $($process.Id)"
Write-Output 'Enter starts. WASD/arrows move, Space jumps, J/left mouse attacks, E interacts, Q switches weapon, R restarts.'
Write-Output 'For this first-stage body trial, tap J once and wait over 1.1s before the next attack; A/D changes facing.'
Write-Output 'Maximum body height 72px at 1280x720; interface hidden. Close the game window to exit.'
Write-Output 'Chest and shoulders cover four Ready and six first-cut phases. Other states/second and third combo stages remain placeholders; actual equipment IDs/full motion are unfinished.'
Write-Output "Log: $log"
