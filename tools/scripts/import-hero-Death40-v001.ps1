param([string]$EngineRoot='G:\UE_5.5')
$ErrorActionPreference='Stop'
$workspace=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\..'))
if(Get-Process -Name 'UnrealEditor','UnrealEditor-Cmd','UnrealBuildTool' -ErrorAction SilentlyContinue){throw 'Sequential import requires no UE/UBT.'}
$python=Join-Path $workspace 'tools\runtime\asset-gen\Scripts\python.exe'
$script=Join-Path $PSScriptRoot 'ue-import-hero-Death40-v001.py'
& $python -B -X utf8 $script --validate-only
if($LASTEXITCODE -ne 0){throw 'Death40 preflight failed; UE not started.'}
$bootstrap=Join-Path $workspace 'UnrealGame\Saved\Bootstrap'
$before=@(Get-ChildItem -LiteralPath $bootstrap -Filter 'hero-Death40-v001-import-*.json' -File | ForEach-Object FullName)
$log=Join-Path $bootstrap ('hero-Death40-import-{0}.log' -f (Get-Date -Format 'yyyyMMdd-HHmmss-fffffff'))
$argsList=@(('"{0}"' -f (Join-Path $workspace 'UnrealGame\CodexDungeon.uproject')),'-unattended','-nosplash','-nop4','-NoLiveCoding',('-ExecutePythonScript="{0}"' -f $script),('-abslog="{0}"' -f $log))
$process=Start-Process -FilePath (Join-Path $EngineRoot 'Engine\Binaries\Win64\UnrealEditor.exe') -ArgumentList $argsList -WindowStyle Hidden -PassThru
Write-Output "Native Death40 import PID $($process.Id), log $log"
$process.WaitForExit()
$fresh=@(Get-ChildItem -LiteralPath $bootstrap -Filter 'hero-Death40-v001-import-*.json' -File | Where-Object {$_.FullName -notin $before})
if($process.ExitCode -ne 0 -or $fresh.Count -ne 1){throw 'Actual import failed or unique fresh receipt missing.'}
& $python -B -X utf8 $script --verify-receipt $fresh[0].FullName
if($LASTEXITCODE -ne 0){throw 'Actual independent40/old1286 verification failed.'}
Write-Output ('Native saved40, Production1326, independent twoSHA: '+$fresh[0].FullName)
