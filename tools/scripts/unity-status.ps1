$ErrorActionPreference = 'Stop'
$workspace = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\..'))
$project = Join-Path $workspace 'Game'
$processes = @(Get-CimInstance Win32_Process -Filter "Name='Unity.exe'" | Where-Object { $_.CommandLine -and $_.CommandLine.Contains($project) } | Select-Object ProcessId,CommandLine)
$statusPath = Join-Path $project 'Logs\workspace-status.json'
$runtimePath = Join-Path $project 'Logs\play-proof-runtime.json'
$latestLog = Get-ChildItem -LiteralPath (Join-Path $project 'Logs') -Filter '*.log' -ErrorAction SilentlyContinue | Sort-Object LastWriteTimeUtc -Descending | Select-Object -First 1
$summary = [ordered]@{
    project = $project
    processes = $processes
    editor = $(if (Test-Path -LiteralPath $statusPath) { Get-Content -LiteralPath $statusPath -Raw | ConvertFrom-Json } else { $null })
    runtimeProof = $(if (Test-Path -LiteralPath $runtimePath) { Get-Content -LiteralPath $runtimePath -Raw | ConvertFrom-Json } else { $null })
    dependencyLockExists = Test-Path -LiteralPath (Join-Path $project 'Packages\packages-lock.json')
    latestLog = $latestLog.FullName
}
$summary | ConvertTo-Json -Depth 6
if ($latestLog) { Get-Content -LiteralPath $latestLog.FullName -Tail 15 }
