param([string]$EngineRoot='G:\UE_5.5')
$ErrorActionPreference='Stop'
$workspace=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\..'))
$bootstrap=Join-Path $workspace 'UnrealGame\Saved\Bootstrap'
if(Get-Process UnrealEditor,UnrealEditor-Cmd,UnrealBuildTool -ErrorAction SilentlyContinue){throw 'Close existing UE/UBT before the sequential audio import.'}
$pattern='first-batch-audio-v002-import-*.json'
$previous=@(Get-ChildItem -LiteralPath $bootstrap -Filter $pattern -File | ForEach-Object FullName)
$script=Join-Path $PSScriptRoot 'ue-import-first-batch-audio-v002.py'
$log=Join-Path $bootstrap ('dedicated-audio-v002-import-{0}.log' -f (Get-Date -Format 'yyyyMMdd-HHmmss'))
$arguments=@(('"{0}"' -f (Join-Path $workspace 'UnrealGame\CodexDungeon.uproject')),'-unattended','-nosplash','-nop4',('-ExecutePythonScript="{0}"' -f $script),('-abslog="{0}"' -f $log))
$process=Start-Process -FilePath (Join-Path $EngineRoot 'Engine\Binaries\Win64\UnrealEditor.exe') -ArgumentList $arguments -WindowStyle Hidden -PassThru
Write-Output "Actual dedicated audio import PID $($process.Id), log $log"
$process.WaitForExit()
$created=@(Get-ChildItem -LiteralPath $bootstrap -Filter $pattern -File | Where-Object {$_.FullName -notin $previous})
if($process.ExitCode -ne 0 -or $created.Count -ne 1){throw "Import failed or fresh receipt missing: $log"}
$receipt=Get-Content -LiteralPath $created[0].FullName -Raw | ConvertFrom-Json
if(-not $receipt.success -or -not $receipt.registry_exact_set_passed -or -not $receipt.old17_unchanged -or $receipt.actual_count -ne 5 -or $receipt.saved_count -ne 5){throw "Actual audio receipt rejected: $($created[0].FullName)"}
Write-Output "Actual five SoundWaves imported/saved; original17 unchanged: $($created[0].FullName)"
Write-Output 'Runtime binding, audition and final mix remain separate unfulfilled checks.'
