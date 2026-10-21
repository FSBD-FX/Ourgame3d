param(
    [string]$EngineRoot = 'G:\UE_5.5',
    [ValidatePattern('^[A-Za-z0-9_.]+$')][string]$TestFilter = 'CodexDungeon',
    [ValidateRange(1,10000)][int]$ExpectedTests = 161
)
$ErrorActionPreference = 'Stop'
$workspace = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\..'))
$run = Get-Date -Format 'yyyyMMdd-HHmmss'
$log = Join-Path $workspace ("UnrealGame\Saved\Bootstrap\first-room-tests-$run.log")
$report = Join-Path $workspace ("UnrealGame\Saved\Automation\FirstRoom-$run")
$arguments = @(('"{0}"' -f (Join-Path $workspace 'UnrealGame\CodexDungeon.uproject')),'-unattended','-nullrhi','-nop4','-nosplash',('-ExecCmds="Automation RunTests {0}"' -f $TestFilter),'-TestExit="Automation Test Queue Empty"',('-ReportExportPath="{0}"' -f $report),('-abslog="{0}"' -f $log))
$process = Start-Process -FilePath (Join-Path $EngineRoot 'Engine\Binaries\Win64\UnrealEditor-Cmd.exe') -ArgumentList $arguments -WindowStyle Hidden -PassThru
Write-Output "UE gameplay automation PID $($process.Id)"
$process.WaitForExit()
$index = Join-Path $report 'index.json'
if ($process.ExitCode -ne 0 -or -not (Test-Path -LiteralPath $index)) { throw "Automation failed or report missing: $log" }
$result = Get-Content -LiteralPath $index -Raw | ConvertFrom-Json
if ($result.failed -ne 0 -or $result.notRun -ne 0 -or $result.succeeded -ne $ExpectedTests) { throw "Gameplay tests not all passed (expected $ExpectedTests, passed $($result.succeeded), failed $($result.failed)): $index" }
Write-Output "Gameplay automation passed: $($result.succeeded)/$ExpectedTests. Report: $index"
