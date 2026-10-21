param([string]$EngineRoot='G:\UE_5.5')
$ErrorActionPreference='Stop'
$workspace=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\..'))
$python=Join-Path $workspace 'tools\runtime\asset-gen\Scripts\python.exe'
$script=Join-Path $PSScriptRoot 'ue-import-fairytale-limb-lookdev-v001.py'
if(Get-Process -Name 'UnrealEditor','UnrealEditor-Cmd','UnrealBuildTool' -ErrorAction SilentlyContinue){throw 'Sequential import requires no existing UE/UBT.'}
& $python -B -X utf8 $script --validate-only
if($LASTEXITCODE -ne 0){throw 'Frozen eight-source preflight failed; UE was not started.'}
$bootstrap=Join-Path $workspace 'UnrealGame\Saved\Bootstrap'
$before=@(Get-ChildItem -LiteralPath $bootstrap -Filter 'fairytale-limb-lookdev-v001-import-*.json' -File | ForEach-Object FullName)
$log=Join-Path $bootstrap ('fairytale-limb-lookdev-v001-import-{0}.log' -f (Get-Date -Format 'yyyyMMdd-HHmmss-fffffff'))
$argsList=@(('"{0}"' -f (Join-Path $workspace 'UnrealGame\CodexDungeon.uproject')),'-unattended','-nosplash','-nop4','-NoLiveCoding',('-ExecutePythonScript="{0}"' -f $script),('-abslog="{0}"' -f $log))
$process=Start-Process -FilePath (Join-Path $EngineRoot 'Engine\Binaries\Win64\UnrealEditor.exe') -ArgumentList $argsList -WindowStyle Hidden -PassThru
Write-Output "Actual limb-eight import PID $($process.Id), log $log"
$process.WaitForExit()
$fresh=@(Get-ChildItem -LiteralPath $bootstrap -Filter 'fairytale-limb-lookdev-v001-import-*.json' -File | Where-Object {$_.FullName -notin $before})
if($process.ExitCode -ne 0 -or $fresh.Count -ne 1){throw 'Native import process failed or fresh receipt missing.'}
$receipt=Get-Content -LiteralPath $fresh[0].FullName -Raw | ConvertFrom-Json
if(-not $receipt.success -or $receipt.actual_count -ne 8 -or $receipt.saved_count -ne 8 -or $receipt.old_packages_unchanged -ne 881){throw ('Native eight import receipt failed: '+$fresh[0].FullName)}
Write-Output ('Actual imported/saved eight, old881 unchanged: '+$fresh[0].FullName)
