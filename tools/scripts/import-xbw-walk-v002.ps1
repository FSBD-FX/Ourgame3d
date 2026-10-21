param([string]$EngineRoot='G:\UE_5.5')
$ErrorActionPreference='Stop'
$workspace=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\..'))
$editor=Join-Path $EngineRoot 'Engine\Binaries\Win64\UnrealEditor.exe'
$project=Join-Path $workspace 'UnrealGame\CodexDungeon.uproject'
$bootstrap=Join-Path $workspace 'UnrealGame\Saved\Bootstrap'
if(Get-Process UnrealEditor,UnrealEditor-Cmd,UnrealBuildTool -ErrorAction SilentlyContinue){throw 'Close existing UE/UBT before the sequential asset import.'}
$jobs=@(
    @{Script='ue-import-xbw-walk-v002.py';Pattern='xbw-walk-v002-import-*.json';Count=18},
    @{Script='ue-import-xbw-armor-walk-v002.py';Pattern='xbw-armor-walk-v002-import-*.json';Count=48}
)
foreach($job in $jobs){
    $previous=@(Get-ChildItem -LiteralPath $bootstrap -Filter $job.Pattern -File | ForEach-Object FullName)
    $script=Join-Path $PSScriptRoot $job.Script
    $log=Join-Path $bootstrap ('{0}-{1}.log' -f $job.Script.Replace('.py',''),(Get-Date -Format 'yyyyMMdd-HHmmss'))
    $arguments=@(('"{0}"' -f $project),'-unattended','-nosplash','-nop4',('-ExecutePythonScript="{0}"' -f $script),('-abslog="{0}"' -f $log))
    $process=Start-Process -FilePath $editor -ArgumentList $arguments -WindowStyle Hidden -PassThru
    Write-Output "Actual UE asset import $($job.Script), PID $($process.Id), log $log"
    $process.WaitForExit()
    $created=@(Get-ChildItem -LiteralPath $bootstrap -Filter $job.Pattern -File | Where-Object {$_.FullName -notin $previous})
    if($process.ExitCode -ne 0 -or $created.Count -ne 1){throw "Import failed or fresh receipt missing: $log"}
    $receipt=Get-Content -LiteralPath $created[0].FullName -Raw | ConvertFrom-Json
    if(-not $receipt.success -or -not $receipt.registry_exact_set_passed -or $receipt.actual_count -ne $job.Count -or $receipt.saved_count -ne $job.Count){throw "Actual import receipt rejected: $($created[0].FullName)"}
    Write-Output "Actual imported/saved $($receipt.actual_count)/$($job.Count): $($created[0].FullName)"
}
Write-Output 'Actual XBW walk body18 plus four-armor48 import complete; runtime adaptation remains unverified.'
