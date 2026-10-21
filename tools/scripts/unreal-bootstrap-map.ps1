param([string]$EngineRoot = 'G:\UE_5.5')
$ErrorActionPreference = 'Stop'
$workspace = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\..'))
$project = Join-Path $workspace 'UnrealGame\CodexDungeon.uproject'
$existing = @(Get-CimInstance Win32_Process -Filter "Name='UnrealEditor.exe' OR Name='UnrealEditor-Cmd.exe'" | Where-Object { $_.CommandLine -and $_.CommandLine.Contains($project) })
if ($existing.Count -gt 0) { throw "Close this project's existing editor before running the map commandlet: $($existing.ProcessId -join ', ')" }
$script = Join-Path $workspace 'UnrealGame\Content\Python\bootstrap_foundation.py'
$logs = Join-Path $workspace 'UnrealGame\Saved\Bootstrap'
New-Item -ItemType Directory -Path $logs -Force | Out-Null
$log = Join-Path $logs ('map-{0}.log' -f (Get-Date -Format 'yyyyMMdd-HHmmss'))
$editor = Join-Path $EngineRoot 'Engine\Binaries\Win64\UnrealEditor-Cmd.exe'
$arguments = @(('"{0}"' -f $project), '-run=pythonscript', ('-script="{0}"' -f $script), '-unattended', '-nullrhi', '-nop4', ('-abslog="{0}"' -f $log))
$process = Start-Process -FilePath $editor -ArgumentList $arguments -WindowStyle Hidden -PassThru
Write-Output "Foundation commandlet started: PID $($process.Id), log $log"
$process.WaitForExit()
Write-Output "Foundation commandlet exit code: $($process.ExitCode)"
exit $process.ExitCode
