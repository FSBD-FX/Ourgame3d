param(
    [string]$EngineRoot='G:\UE_5.5',
    [string]$Manifest='F:\Ourgame\source-assets\production\fairytale-hero-state-gap-v001\dodge-state-preparation-v001\Root-Dodge32-import-v001\import-manifest.json',
    [switch]$ValidateOnly
)
$ErrorActionPreference='Stop'
$workspace='F:\Ourgame'
$python=Join-Path $workspace 'tools\runtime\asset-gen\Scripts\python.exe'
$script=Join-Path $PSScriptRoot 'ue-import-hero-Dodge32-v001.py'
$Manifest=[IO.Path]::GetFullPath($Manifest)
& $python -B -X utf8 $script --manifest $Manifest --validate-only
if($LASTEXITCODE -ne 0){throw 'Dodge32 host preflight failed; UE not started.'}
if($ValidateOnly){Write-Output 'Dodge32 validate-only passed; no UE started.';return}
if(Get-Process -Name 'UnrealEditor','UnrealEditor-Cmd','UnrealBuildTool' -ErrorAction SilentlyContinue){throw 'Sequential import requires no UE/UBT.'}
$bootstrap=Join-Path $workspace 'UnrealGame\Saved\Bootstrap'
$before=@(Get-ChildItem -LiteralPath $bootstrap -Filter 'hero-Dodge32-v001-import-*.json' -File | ForEach-Object FullName)
$log=Join-Path $bootstrap ('hero-Dodge32-import-{0}.log' -f (Get-Date -Format 'yyyyMMdd-HHmmss-fffffff'))
$arguments=@(('"{0}"' -f (Join-Path $workspace 'UnrealGame\CodexDungeon.uproject')),'-unattended','-nosplash','-nop4','-NoLiveCoding',('-ExecutePythonScript="{0}"' -f $script),('-abslog="{0}"' -f $log))
$previousManifest=$env:DUNGEON_DODGE32_IMPORT_MANIFEST
try {
    $env:DUNGEON_DODGE32_IMPORT_MANIFEST=$Manifest
    $process=Start-Process -FilePath (Join-Path $EngineRoot 'Engine\Binaries\Win64\UnrealEditor.exe') -ArgumentList $arguments -WindowStyle Hidden -PassThru
    Write-Output ('Dodge32 native import PID {0}; log {1}' -f $process.Id,$log)
    $process.WaitForExit()
} finally {$env:DUNGEON_DODGE32_IMPORT_MANIFEST=$previousManifest}
$fresh=@(Get-ChildItem -LiteralPath $bootstrap -Filter 'hero-Dodge32-v001-import-*.json' -File | Where-Object {$_.FullName -notin $before})
if($process.ExitCode -ne 0 -or $fresh.Count -ne 1){throw 'Actual Dodge32 import failed or unique fresh receipt missing; preserve partial outputs.'}
& $python -B -X utf8 $script --manifest $Manifest --verify-receipt $fresh[0].FullName
if($LASTEXITCODE -ne 0){throw 'Dodge32 independent1332+32 saved-byte verification failed.'}
Write-Output ('Native saved32, Production1364; independent twoSHA: '+$fresh[0].FullName)
