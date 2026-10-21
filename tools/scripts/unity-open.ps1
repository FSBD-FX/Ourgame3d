param(
    [string]$UnityPath = 'G:\UNITY\6000.0.43f1\Editor\Unity.exe',
    [switch]$PlayProof
)
$ErrorActionPreference = 'Stop'
$workspace = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\..'))
$project = Join-Path $workspace 'Game'
$logs = Join-Path $project 'Logs'
New-Item -ItemType Directory -Path $logs -Force | Out-Null
$existing = @(Get-CimInstance Win32_Process -Filter "Name='Unity.exe'" | Where-Object { $_.CommandLine -and $_.CommandLine.Contains($project) })
if ($existing.Count -eq 0) {
    if (-not (Test-Path -LiteralPath $UnityPath)) { throw "Unity Editor not found: $UnityPath" }
    $log = Join-Path $logs ('editor-{0}.log' -f (Get-Date -Format 'yyyyMMdd-HHmmss'))
    $arguments = @('-projectPath', ('"{0}"' -f $project), '-executeMethod', 'CodexGame.Editor.WorkspaceBootstrap.OpenProject', '-logFile', ('"{0}"' -f $log))
    $editor = Start-Process -FilePath $UnityPath -ArgumentList $arguments -WindowStyle Hidden -PassThru
    Write-Output "Unity Editor started: PID $($editor.Id), log $log"
} else {
    Write-Output "This project already has a Unity Editor process: $($existing.ProcessId -join ', ')"
}
if ($PlayProof) {
    $commands = Join-Path $project 'Temp\CodexAutomation'
    New-Item -ItemType Directory -Path $commands -Force | Out-Null
    Set-Content -LiteralPath (Join-Path $commands 'play-proof.request') -Value (Get-Date).ToUniversalTime().ToString('O') -Encoding utf8
    Write-Output 'Queued a four second Foundation Play Mode check after import and compilation.'
}
