param([string]$UnityPath = 'G:\UNITY\6000.0.43f1\Editor\Unity.exe')
$ErrorActionPreference = 'Stop'
$workspace = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\..'))
$project = Join-Path $workspace 'Game'
if (-not (Test-Path -LiteralPath $UnityPath)) { throw "Unity Editor not found: $UnityPath" }
$existing = @(Get-CimInstance Win32_Process -Filter "Name='Unity.exe'" | Where-Object { $_.CommandLine -and $_.CommandLine.Contains($project) })
if ($existing.Count -gt 0) { throw 'This project is already open. Use the running Editor/MCP to refresh and inspect compilation instead of launching a second process.' }
$logs = Join-Path $project 'Logs'
New-Item -ItemType Directory -Path $logs -Force | Out-Null
$log = Join-Path $logs ('compile-{0}.log' -f (Get-Date -Format 'yyyyMMdd-HHmmss'))
$arguments = @('-batchmode', '-nographics', '-projectPath', ('"{0}"' -f $project), '-executeMethod', 'CodexGame.Editor.WorkspaceBootstrap.Initialize', '-quit', '-logFile', ('"{0}"' -f $log))
$editor = Start-Process -FilePath $UnityPath -ArgumentList $arguments -WindowStyle Hidden -PassThru
Write-Output "Unity validation started: PID $($editor.Id), log $log"
$editor.WaitForExit()
Write-Output "Unity exited with code $($editor.ExitCode). Log: $log"
if ($editor.ExitCode -ne 0) { Get-Content -LiteralPath $log -Tail 35; exit $editor.ExitCode }
