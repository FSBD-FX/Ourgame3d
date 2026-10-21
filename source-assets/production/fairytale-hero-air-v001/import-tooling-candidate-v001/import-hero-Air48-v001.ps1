param(
    [Parameter(Mandatory=$true)][string]$Manifest,
    [string]$EngineRoot='G:\UE_5.5',
    [switch]$ValidateOnly
)
$ErrorActionPreference='Stop'
$airWorkspace='F:\Ourgame'
$airPython=Join-Path $airWorkspace 'tools\runtime\asset-gen\Scripts\python.exe'
$airScript=Join-Path $PSScriptRoot 'ue-import-hero-Air48-v001.py'
$Manifest=[IO.Path]::GetFullPath($Manifest)
& $airPython -B -X utf8 $airScript --manifest $Manifest --validate-only
if($LASTEXITCODE -ne 0){throw 'Air48 host preflight failed; UE not started.'}
if($ValidateOnly){Write-Output 'Air48 read-only host preflight passed; UE not started.';return}
if(Get-Process -Name 'UnrealEditor','UnrealEditor-Cmd','UnrealBuildTool' -ErrorAction SilentlyContinue){throw 'Air48 sequential import requires no UE/UBT processes.'}
$airParent=Split-Path -Parent $Manifest
$airRun=Join-Path $airParent ('native-run-{0}' -f (Get-Date -Format 'yyyyMMdd-HHmmss-fffffff'))
if(Test-Path -LiteralPath $airRun){throw 'Unique run directory already exists; retain prior outputs.'}
[IO.Directory]::CreateDirectory($airRun) | Out-Null
$airReceipt=Join-Path $airRun 'actual-native-import-receipt.json'
$airProof=Join-Path $airRun 'independent-saved-byte-verification.json'
$airLog=Join-Path $airRun 'UnrealEditor-native-import.log'
$airArgs=@(('"{0}"' -f (Join-Path $airWorkspace 'UnrealGame\CodexDungeon.uproject')),'-unattended','-nosplash','-nop4','-NoLiveCoding',('-ExecutePythonScript="{0}"' -f $airScript),('-abslog="{0}"' -f $airLog))
$airPreviousManifest=$env:DUNGEON_AIR48_IMPORT_MANIFEST
$airPreviousReceipt=$env:DUNGEON_AIR48_RECEIPT_OUTPUT
$airPreviousNative=$env:DUNGEON_AIR48_NATIVE
try {
    $env:DUNGEON_AIR48_IMPORT_MANIFEST=$Manifest
    $env:DUNGEON_AIR48_RECEIPT_OUTPUT=$airReceipt
    $env:DUNGEON_AIR48_NATIVE='1'
    $airProcess=Start-Process -FilePath (Join-Path $EngineRoot 'Engine\Binaries\Win64\UnrealEditor.exe') -ArgumentList $airArgs -WindowStyle Hidden -PassThru
    Write-Output ('Air48 native import PID {0}; retained run {1}' -f $airProcess.Id,$airRun)
    $airProcess.WaitForExit()
} finally {
    $env:DUNGEON_AIR48_IMPORT_MANIFEST=$airPreviousManifest
    $env:DUNGEON_AIR48_RECEIPT_OUTPUT=$airPreviousReceipt
    $env:DUNGEON_AIR48_NATIVE=$airPreviousNative
}
if($airProcess.ExitCode -ne 0 -or -not(Test-Path -LiteralPath $airReceipt -PathType Leaf)){throw 'Air48 native import failed/missing receipt; retain all partial outputs, do not retry.'}
& $airPython -B -X utf8 $airScript --manifest $Manifest --verify-receipt $airReceipt --verification-output $airProof
if($LASTEXITCODE -ne 0){throw 'Air48 independent1371+48 saved-byte verification failed; retain originals.'}
Write-Output ('Native48 saved; Production1419 independent twoSHA passed. '+$airProof)
