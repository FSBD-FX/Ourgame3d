param([switch]$ExecuteNative)
$ErrorActionPreference='Stop'
$workspace='F:\Ourgame'
$python=Join-Path $workspace 'tools\runtime\asset-gen\Scripts\python.exe'
$script=Join-Path $PSScriptRoot 'ue-import-Hurt32-v002.py'
$validation=Join-Path (Split-Path $PSScriptRoot -Parent) 'validation-runs'
$stamp=[DateTime]::UtcNow.ToString('yyyyMMdd-HHmmss-fffffff')
$preflight=Join-Path $validation ('host-source-preflight-'+$stamp+'.json')
& $python -B -X utf8 $script --validate-only --preflight-receipt $preflight
if($LASTEXITCODE -ne 0){throw 'Hurt32 source RGBA / old1254 / empty namespace preflight failed.'}
if(-not $ExecuteNative){return}
if(Get-Process -Name 'UnrealEditor','UnrealEditor-Cmd','UnrealBuildTool' -ErrorAction SilentlyContinue){throw 'Root sequential import requires UE/UBT closed.'}
$bootstrap=Join-Path $workspace 'UnrealGame\Saved\Bootstrap'
$before=@(Get-ChildItem -LiteralPath $bootstrap -Filter 'hurt32-v002-import-*.json' -File | ForEach-Object FullName)
$log=Join-Path $bootstrap ('hurt32-import-'+$stamp+'.log')
$oldExecute=[Environment]::GetEnvironmentVariable('OURGAME_HURT32_EXECUTE','Process')
$oldPreflight=[Environment]::GetEnvironmentVariable('OURGAME_HURT32_PREFLIGHT','Process')
try {
    [Environment]::SetEnvironmentVariable('OURGAME_HURT32_EXECUTE','1','Process')
    [Environment]::SetEnvironmentVariable('OURGAME_HURT32_PREFLIGHT',$preflight,'Process')
    $arguments=@(('"{0}"' -f (Join-Path $workspace 'UnrealGame\CodexDungeon.uproject')),'-unattended','-nosplash','-nop4','-NoLiveCoding',('-ExecutePythonScript="{0}"' -f $script),('-abslog="{0}"' -f $log))
    $process=Start-Process -FilePath 'G:\UE_5.5\Engine\Binaries\Win64\UnrealEditor.exe' -ArgumentList $arguments -WorkingDirectory $workspace -WindowStyle Hidden -PassThru
    Write-Output "Actual Hurt32 native import PID $($process.Id), log $log"
    $process.WaitForExit()
    $fresh=@(Get-ChildItem -LiteralPath $bootstrap -Filter 'hurt32-v002-import-*.json' -File | Where-Object {$_.FullName -notin $before})
    if($process.ExitCode -ne 0 -or $fresh.Count -ne 1){throw 'Actual Hurt32 import failed or unique receipt missing; preserve outputs.'}
    & $python -B -X utf8 $script --verify-receipt $fresh[0].FullName
    if($LASTEXITCODE -ne 0){throw 'Hurt32 native receipt/source/saved32/old1254 verification failed; preserve outputs.'}
} finally {
    [Environment]::SetEnvironmentVariable('OURGAME_HURT32_EXECUTE',$oldExecute,'Process')
    [Environment]::SetEnvironmentVariable('OURGAME_HURT32_PREFLIGHT',$oldPreflight,'Process')
}
