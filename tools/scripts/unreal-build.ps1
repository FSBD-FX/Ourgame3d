param(
    [string]$EngineRoot = 'G:\UE_5.5',
    [ValidateSet('Editor','Game')][string]$Target = 'Editor',
    [ValidateRange(1,16)][int]$MaxParallelActions = 2
)
$ErrorActionPreference = 'Stop'
$workspace = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\..'))
$project = Join-Path $workspace 'UnrealGame\CodexDungeon.uproject'
$logs = Join-Path $workspace 'UnrealGame\Saved\Bootstrap'
New-Item -ItemType Directory -Path $logs -Force | Out-Null
$build = Join-Path $EngineRoot 'Engine\Build\BatchFiles\Build.bat'
if (-not (Test-Path -LiteralPath $build)) { throw "UE build script not found: $build" }
$targetName = if ($Target -eq 'Editor') { 'CodexDungeonEditor' } else { 'CodexDungeon' }
$log = Join-Path $logs ('build-{0}-{1}.log' -f $Target.ToLowerInvariant(),(Get-Date -Format 'yyyyMMdd-HHmmss'))
& $build $targetName Win64 Development "-Project=$project" -WaitMutex -NoHotReloadFromIDE "-MaxParallelActions=$MaxParallelActions" 2>&1 | Tee-Object -FilePath $log
$result = $LASTEXITCODE
[pscustomobject]@{Utc=(Get-Date).ToUniversalTime().ToString('O');Target=$targetName;ExitCode=$result;Log=$log} | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $logs 'last-build.json') -Encoding utf8
Write-Output "Unreal build exited with code $result. Log: $log"
exit $result
