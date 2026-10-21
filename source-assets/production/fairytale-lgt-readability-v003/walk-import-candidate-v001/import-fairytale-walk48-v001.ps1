param([string]$EngineRoot='G:\UE_5.5',[switch]$ExecuteNative)
$ErrorActionPreference='Stop'
$workspace='F:\Ourgame'
$python=Join-Path $workspace 'tools\runtime\asset-gen\Scripts\python.exe'
$script=Join-Path $PSScriptRoot 'ue-import-fairytale-walk48-v001.py'
$checks=Join-Path $PSScriptRoot 'ue_walk48_checks_v001.py'
& $python -B -X utf8 $script --validate-only
if($LASTEXITCODE -ne 0){throw 'Exact48 source/old1151 preflight failed; UE not started.'}
if(-not $ExecuteNative){Write-Output 'Offline preflight only. Root may admit scripts and explicitly use -ExecuteNative.';return}
if(Get-Process -Name 'UnrealEditor','UnrealEditor-Cmd','UnrealBuildTool' -ErrorAction SilentlyContinue){throw 'Root sequential native import requires no existing UE/UBT process.'}
$bootstrap=Join-Path $workspace 'UnrealGame\Saved\Bootstrap'
New-Item -ItemType Directory -Path $bootstrap -Force | Out-Null
$before=@(Get-ChildItem -LiteralPath $bootstrap -Filter 'fairytale-walk48-v001-import-*.json' -File | ForEach-Object FullName)
$log=Join-Path $bootstrap ('fairytale-walk48-v001-import-{0}.log' -f (Get-Date -Format 'yyyyMMdd-HHmmss-fffffff'))
$argList=@(('"{0}"' -f (Join-Path $workspace 'UnrealGame\CodexDungeon.uproject')),'-unattended','-nosplash','-nop4','-NoLiveCoding',('-ExecutePythonScript="{0}"' -f $script),('-abslog="{0}"' -f $log))
$process=Start-Process -FilePath (Join-Path $EngineRoot 'Engine\Binaries\Win64\UnrealEditor.exe') -ArgumentList $argList -WindowStyle Hidden -PassThru
Write-Output "Root native Walk48 PID $($process.Id), log $log"
$process.WaitForExit()
$fresh=@(Get-ChildItem -LiteralPath $bootstrap -Filter 'fairytale-walk48-v001-import-*.json' -File | Where-Object {$_.FullName -notin $before})
if($process.ExitCode -ne 0 -or $fresh.Count -ne 1){throw 'Native import failed or unique fresh receipt missing.'}
& $python -B -X utf8 $checks --verify-receipt $fresh[0].FullName
if($LASTEXITCODE -ne 0){throw ('Native receipt/disk/old1151 verification failed: '+$fresh[0].FullName)}
Write-Output ('Saved exact48; old1151 two-pass SHA/bytes unchanged; actual total1199. Receipt '+$fresh[0].FullName)
