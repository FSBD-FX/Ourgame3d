param([string]$EngineRoot = 'G:\UE_5.5')
$ErrorActionPreference = 'Stop'
$workspace = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\..'))
$project = Join-Path $workspace 'UnrealGame\CodexDungeon.uproject'
$existing = @(Get-CimInstance Win32_Process -Filter "Name='UnrealEditor.exe'" | Where-Object { $_.CommandLine -and $_.CommandLine.Contains($project) })
if ($existing.Count -gt 0) { Write-Output "This project's Unreal Editor is already running: $($existing.ProcessId -join ', ')"; return }
$logs = Join-Path $workspace 'UnrealGame\Saved\Bootstrap'
New-Item -ItemType Directory -Path $logs -Force | Out-Null
$log = Join-Path $logs ('editor-{0}.log' -f (Get-Date -Format 'yyyyMMdd-HHmmss'))
$editor = Join-Path $EngineRoot 'Engine\Binaries\Win64\UnrealEditor.exe'
$arguments = @(('"{0}"' -f $project), '-NoSplash', '-NoLiveCoding', '-nop4', ('-abslog="{0}"' -f $log))
$process = Start-Process -FilePath $editor -ArgumentList $arguments -WindowStyle Hidden -PassThru
[pscustomobject]@{Utc=(Get-Date).ToUniversalTime().ToString('O');EditorPid=$process.Id;Project=$project;Log=$log} | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $logs 'last-editor-start.json') -Encoding utf8
Write-Output "Unreal Editor started: PID $($process.Id), log $log"
