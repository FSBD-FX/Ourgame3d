param([string]$EngineRoot='G:\UE_5.5')
$ErrorActionPreference='Stop'
$workspace=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\..'))
if(Get-Process -Name 'UnrealEditor','UnrealEditor-Cmd','UnrealBuildTool' -ErrorAction SilentlyContinue){throw 'Sequential native import requires no UE/UBT.'}
$python=Join-Path $workspace 'tools\runtime\asset-gen\Scripts\python.exe'
$script=Join-Path $PSScriptRoot 'ue-import-leather-combo-v001.py'
& $python -B -X utf8 $script --validate-only
if($LASTEXITCODE -ne 0){throw '36-source preflight failed; UE not started.'}
$bootstrap=Join-Path $workspace 'UnrealGame\Saved\Bootstrap'
$before=@(Get-ChildItem -LiteralPath $bootstrap -Filter 'leather-primary*-combo-v001-import-*.json' -File | ForEach-Object FullName)
$log=Join-Path $bootstrap ('leather-combo-v001-import-{0}.log' -f (Get-Date -Format 'yyyyMMdd-HHmmss-fffffff'))
$argList=@(('"{0}"' -f (Join-Path $workspace 'UnrealGame\CodexDungeon.uproject')),'-unattended','-nosplash','-nop4','-NoLiveCoding',('-ExecutePythonScript="{0}"' -f $script),('-abslog="{0}"' -f $log))
$process=Start-Process -FilePath (Join-Path $EngineRoot 'Engine\Binaries\Win64\UnrealEditor.exe') -ArgumentList $argList -WindowStyle Hidden -PassThru
Write-Output "Native 36 Texture2D import PID $($process.Id), log $log"
$process.WaitForExit()
$fresh=@(Get-ChildItem -LiteralPath $bootstrap -Filter 'leather-primary*-combo-v001-import-*.json' -File | Where-Object {$_.FullName -notin $before})
if($process.ExitCode -ne 0 -or $fresh.Count -ne 2){throw 'Native import failed or fresh receipts missing.'}
foreach($file in $fresh){$r=Get-Content -LiteralPath $file.FullName -Raw | ConvertFrom-Json;if(-not $r.success -or $r.actual_count -ne 18 -or $r.saved_count -ne 18 -or $r.old_packages_unchanged -ne 1115){throw ('Failed receipt: '+$file.FullName)};Write-Output ('Actual saved18: '+$file.FullName)}
Write-Output 'Saved36 new textures; old1115 unchanged; expected total1151.'
