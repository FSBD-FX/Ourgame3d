param([switch]$ExecuteNative)
$ErrorActionPreference='Stop'
$workspace='F:\Ourgame'
$python=Join-Path $workspace 'tools\runtime\asset-gen\Scripts\python.exe'
$script=Join-Path $PSScriptRoot 'ue-import-guard-whole16-v001.py'
& $python -B -X utf8 $script --validate-only
if($LASTEXITCODE -ne 0){throw 'Guard16 source and old1210 preflight failed.'}
if(-not $ExecuteNative){return}
if(Get-Process -Name 'UnrealEditor','UnrealEditor-Cmd','UnrealBuildTool' -ErrorAction SilentlyContinue){throw 'Root sequential import requires UE/UBT closed.'}
$bootstrap=Join-Path $workspace 'UnrealGame\Saved\Bootstrap'
$before=@(Get-ChildItem -LiteralPath $bootstrap -Filter 'guard-whole16-v001-import-*.json' -File | ForEach-Object FullName)
$log=Join-Path $bootstrap ('guard-whole16-import-'+(Get-Date -Format 'yyyyMMdd-HHmmss-fffffff')+'.log')
$arguments=@(('"{0}"' -f (Join-Path $workspace 'UnrealGame\CodexDungeon.uproject')),'-unattended','-nosplash','-nop4','-NoLiveCoding',('-ExecutePythonScript="{0}"' -f $script),('-abslog="{0}"' -f $log))
$process=Start-Process -FilePath 'G:\UE_5.5\Engine\Binaries\Win64\UnrealEditor.exe' -ArgumentList $arguments -WindowStyle Hidden -PassThru
Write-Output "Actual Guard16 native import PID $($process.Id), log $log"
$process.WaitForExit()
$fresh=@(Get-ChildItem -LiteralPath $bootstrap -Filter 'guard-whole16-v001-import-*.json' -File | Where-Object {$_.FullName -notin $before})
if($process.ExitCode -ne 0 -or $fresh.Count -ne 1){throw 'Actual Guard16 import failed or unique receipt missing; preserve outputs.'}
& $python -B -X utf8 $script --verify-receipt $fresh[0].FullName
if($LASTEXITCODE -ne 0){throw 'Guard16 receipt/source/native files/old1210 verification failed.'}
