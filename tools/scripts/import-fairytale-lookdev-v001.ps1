param([string]$EngineRoot='G:\UE_5.5')
$ErrorActionPreference='Stop'
$workspace=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\..'))
$editor=Join-Path $EngineRoot 'Engine\Binaries\Win64\UnrealEditor.exe'
$project=Join-Path $workspace 'UnrealGame\CodexDungeon.uproject'
$bootstrap=Join-Path $workspace 'UnrealGame\Saved\Bootstrap'
$script=Join-Path $PSScriptRoot 'ue-import-fairytale-lookdev-v001.py'
$python=Join-Path $workspace 'tools\runtime\asset-gen\Scripts\python.exe'
foreach($path in @($editor,$project,$script,$python)){
    if(-not (Test-Path -LiteralPath $path -PathType Leaf)){throw "Missing exact import prerequisite: $path"}
}
if(Get-Process -Name 'UnrealEditor','UnrealEditor-Cmd','UnrealBuildTool' -ErrorAction SilentlyContinue){throw 'Close existing UE/UBT before the sequential new-namespace import.'}
& $python -B -X utf8 $script --validate-only
if($LASTEXITCODE -ne 0){throw 'Frozen candidate8 source preflight failed; UE was not started.'}
[IO.Directory]::CreateDirectory($bootstrap) | Out-Null
$pattern='fairytale-lookdev-v001-import-*.json'
$previous=@(Get-ChildItem -LiteralPath $bootstrap -Filter $pattern -File | ForEach-Object FullName)
$log=Join-Path $bootstrap ('fairytale-lookdev-v001-import-{0}.log' -f (Get-Date -Format 'yyyyMMdd-HHmmss-fffffff'))
$arguments=@(('"{0}"' -f $project),'-unattended','-nosplash','-nop4',('-ExecutePythonScript="{0}"' -f $script),('-abslog="{0}"' -f $log))
$process=Start-Process -FilePath $editor -ArgumentList $arguments -WindowStyle Hidden -PassThru
Write-Output "Actual candidate8 import, PID $($process.Id), log $log"
$process.WaitForExit()
$created=@(Get-ChildItem -LiteralPath $bootstrap -Filter $pattern -File | Where-Object {$_.FullName -notin $previous})
if($process.ExitCode -ne 0 -or $created.Count -ne 1){throw "Actual import failed or fresh receipt missing: $log"}
$receipt=Get-Content -LiteralPath $created[0].FullName -Raw | ConvertFrom-Json
if(-not $receipt.success -or -not $receipt.registry_exact_set_passed -or -not $receipt.disk_exact_set_passed -or $receipt.actual_count -ne 8 -or $receipt.saved_count -ne 8 -or $receipt.assets.Count -ne 8){throw "Actual candidate8 receipt rejected: $($created[0].FullName)"}
Write-Output "Actual imported/saved8, new unused EV047/v001 namespace only: $($created[0].FullName)"
Write-Output 'Candidate visual trial only; actual UE loop/motion/style and full units remain unaccepted.'
