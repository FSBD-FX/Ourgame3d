param(
 [ValidateSet('left','right')][string]$Side='left',
 [Parameter(Mandatory=$true)][string]$Compiled296,
 [ValidatePattern('^v[0-9]{3}$')][string]$Version='v001'
)
$ErrorActionPreference='Stop'
$airRoot='F:\Ourgame'
$airPython=Join-Path $airRoot 'tools\runtime\asset-gen\Scripts\python.exe'
$airChecker=Join-Path $airRoot 'source-assets\production\fairytale-hero-air-v001\production-observer-candidate-v001\tooling-freeze-relative-v002\verify-Air-production-native-v001.py'
if(Get-Process -Name UnrealEditor,UnrealEditor-Cmd,UnrealBuildTool -ErrorAction SilentlyContinue){throw 'Sequential native capture requires no UE/UBT process'}
& $airPython -B -X utf8 (Join-Path $airRoot 'tools\scripts\prepare-hero-Air6-production-prereg-v001.py') --side $Side --compiled296 $Compiled296 --version $Version
if($LASTEXITCODE -ne 0){throw 'Current296/full203 Root prereg failed; preserve outputs'}
$airMedia=Join-Path $airRoot ('过程图稿与视频\2026-10-19_钟盔装备跳跃三连实录_{0}_{1}' -f $Side,$Version)
$airPrereg=Join-Path $airMedia 'preregistration-v001.json'
& $airPython -B -X utf8 $airChecker --verify-preflight --root-prereg $airPrereg
if($LASTEXITCODE -ne 0){throw 'Independent preflight failed; no UE started; preserve archive/version'}
$airReg=Get-Content -LiteralPath $airPrereg -Raw | ConvertFrom-Json
$airNative=Join-Path $airMedia '原件'
$airFacing=if($Side -eq 'left'){'-1'}else{'1'}
$airTokens=@('F:/Ourgame/UnrealGame/CodexDungeon.uproject','/Game/Maps/FirstRoom?DungeonFirstBatchGuardRoom','-game','-d3d11','-windowed','-ResX=1280','-ResY=720','-NoSplash','-NoLiveCoding','-nop4','-DungeonCandidateSprites','-DungeonFairytaleSwordEquipmentBoundPreview','-DungeonFairytaleSwordWalkPreview','-DungeonFairytaleSwordHurtPreview','-DungeonFairytaleSwordDeathPreview','-DungeonFairytaleSwordDodgePreview','-DungeonFairytaleSwordAirPreview','-DungeonFairytaleGuardFullPreview','-DungeonFairytaleGuardStompPreview','-DungeonFairytaleGuardMoveRigPreview','-DungeonContentProof','-DungeonHeroAirProductionProofV001',('-DungeonHeroAirProductionFacing='+$airFacing),'-DungeonHeroAirProductionClearKnightDiagnostic','-DungeonFastLosslessCapture','-DungeonAsyncLosslessCapture',('-DungeonContentProofDir='+$airNative),('-abslog='+(Join-Path $airMedia 'native-engine.log')))
function Write-AirNewJson([string]$Path,[object]$Value){
 $airStream=[IO.FileStream]::new($Path,[IO.FileMode]::CreateNew,[IO.FileAccess]::Write,[IO.FileShare]::Read)
 try{$airBytes=[Text.UTF8Encoding]::new($false).GetBytes(($Value | ConvertTo-Json -Depth 12));$airStream.Write($airBytes,0,$airBytes.Length);$airStream.Flush($true)}finally{$airStream.Dispose()}
}
function Get-AirPin([string]$Path){$airItem=Get-Item -LiteralPath $Path;return @{path=$airItem.FullName.Replace('\','/');bytes=$airItem.Length;sha256=(Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()}}
$airArguments=($airTokens | ForEach-Object {'"{0}"' -f $_}) -join ' '
$airProcess=Start-Process -FilePath 'G:/UE_5.5/Engine/Binaries/Win64/UnrealEditor.exe' -ArgumentList $airArguments -WindowStyle Hidden -PassThru
Write-AirNewJson (Join-Path $airMedia 'launch-receipt-v001.json') @{process_id=$airProcess.Id;requested_facing=$airReg.requested_facing;arguments=$airTokens;requested_fixed_time_step=$false;human_input=$false;diagnostic_clear_knight=$true;started_utc=(Get-Date).ToUniversalTime().ToString('O')}
Write-Output ('Hero Air production PID {0}, side {1}, archive {2}' -f $airProcess.Id,$Side,$airMedia)
$airProcess.WaitForExit()
Write-AirNewJson (Join-Path $airMedia 'index.json') @{schema='hero-Air6-production-native-session-v001';process_id=$airProcess.Id;exit_code=$airProcess.ExitCode;root_prereg_pin=(Get-AirPin $airPrereg);compiled_manifest_pin=$airReg.compiled_manifest_pin;checker_freeze_pin=$airReg.checker_freeze_pin;source_probe_freeze_pin=$airReg.source_probe_freeze_pin;finished_utc=(Get-Date).ToUniversalTime().ToString('O');FinalAccepted=$false;native_independent_verification_pending=$true}
Write-Output ('Hero Air production exit {0}: {1}' -f $airProcess.ExitCode,$airMedia)
exit $airProcess.ExitCode
