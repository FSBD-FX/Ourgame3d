param(
 [ValidateSet('left','right')][string]$Side='left',
 [Parameter(Mandatory=$true)][string]$Compiled296,
 [ValidatePattern('^v[0-9]{3}$')][string]$Version='v004',
 [Parameter(Mandatory=$true)][string]$ObserverSourceFreeze,
 [Parameter(Mandatory=$true)][string]$ObserverAdmission,
 [Parameter(Mandatory=$true)][string]$CheckerDirectory,
 [Parameter(Mandatory=$true)][string]$CheckerProtocol
)
$ErrorActionPreference='Stop'
$airRoot='F:\Ourgame'
$airStage='F:/Ourgame/Playables/钟盔轻甲-v142-CM52f906'
$airStageManifest=Get-Content -LiteralPath (Join-Path $airStage '_proof/runtime-snapshot-manifest-v001.json') -Raw | ConvertFrom-Json
function Assert-AirStageRuntime {
 foreach($row in $airStageManifest.runtime_files){$p=Join-Path $airStage $row.path;$f=Get-Item -LiteralPath $p -Force;if($f.LinkType -or ($f.Attributes -band [IO.FileAttributes]::ReparsePoint) -or $f.Length -ne $row.bytes -or (Get-FileHash -LiteralPath $p -Algorithm SHA256).Hash.ToLowerInvariant() -ne $row.sha256){throw 'Actual staged runtime changed: '+$p}}
}
Assert-AirStageRuntime
$airPython=Join-Path $airRoot 'tools\runtime\asset-gen\Scripts\python.exe'
$airChecker=Join-Path ([IO.Path]::GetFullPath($CheckerDirectory)) 'verify-Air-production-native-v001.py'
if(Get-Process -Name UnrealEditor,UnrealEditor-Cmd,UnrealBuildTool -ErrorAction SilentlyContinue){throw 'Sequential native capture requires no UE/UBT process'}
& $airPython -B -X utf8 (Join-Path $airRoot 'tools\scripts\prepare-hero-Air6-production-prereg-v002.py') --side $Side --compiled296 $Compiled296 --version $Version --observer-source-freeze $ObserverSourceFreeze --observer-admission $ObserverAdmission --checker-directory $CheckerDirectory --checker-protocol $CheckerProtocol
if($LASTEXITCODE -ne 0){throw 'Current296/full203 Root prereg failed; preserve outputs'}
$airMedia=Join-Path $airRoot ('过程图稿与视频\2026-10-19_钟盔装备跳跃三连实录_{0}_{1}' -f $Side,$Version)
$airPrereg=Join-Path $airMedia 'preregistration-v001.json'
& $airPython -B -X utf8 $airChecker --verify-preflight --root-prereg $airPrereg
if($LASTEXITCODE -ne 0){throw 'Independent preflight failed; no UE started; preserve archive/version'}
$airReg=Get-Content -LiteralPath $airPrereg -Raw | ConvertFrom-Json
$airNative=Join-Path $airMedia '原件'
$airFacing=if($Side -eq 'left'){'-1'}else{'1'}
$airTokens=@((Join-Path $airStage 'CodexDungeon.uproject'),'/Game/Maps/FirstRoom?DungeonFirstBatchGuardRoom','-game','-d3d11','-windowed','-ResX=1280','-ResY=720','-NoSplash','-NoLiveCoding','-nop4','-DungeonCandidateSprites','-DungeonFairytaleSwordEquipmentBoundPreview','-DungeonFairytaleLeatherReadyPreview','-DungeonFairytaleSwordBodyPreview','-DungeonFairytaleSwordBodyV002Preview','-DungeonFairytaleSwordArmorPrimary1Preview','-DungeonFairytaleSwordPrimary2Preview','-DungeonFairytaleSwordPrimary2BodyPreview','-DungeonFairytaleSwordPrimary2ArmorPreview','-DungeonFairytaleSwordPrimary3ArmorPreview','-DungeonFairytaleLeatherPrimary1Preview','-DungeonFairytaleLeatherPrimary2Preview','-DungeonFairytaleLeatherPrimary3Preview','-DungeonFairytaleSwordWalkPreview','-DungeonFairytaleSwordHurtPreview','-DungeonFairytaleSwordDeathPreview','-DungeonFairytaleSwordDodgePreview','-DungeonFairytaleSwordAirPreview','-DungeonFairytaleGuardFullPreview','-DungeonFairytaleGuardStompPreview','-DungeonFairytaleGuardMoveRigPreview','-DungeonContentProof','-DungeonHeroAirProductionProofV001',('-DungeonHeroAirProductionFacing='+$airFacing),'-DungeonHeroAirProductionClearKnightDiagnostic','-DungeonFastLosslessCapture','-DungeonAsyncLosslessCapture',('-DungeonContentProofDir='+$airNative),('-abslog='+(Join-Path $airMedia 'native-engine.log')))
function Write-AirNewJson([string]$Path,[object]$Value){
 $airStream=[IO.FileStream]::new($Path,[IO.FileMode]::CreateNew,[IO.FileAccess]::Write,[IO.FileShare]::Read)
 try{$airBytes=[Text.UTF8Encoding]::new($false).GetBytes(($Value | ConvertTo-Json -Depth 12));$airStream.Write($airBytes,0,$airBytes.Length);$airStream.Flush($true)}finally{$airStream.Dispose()}
}
function Get-AirPin([string]$Path){$airItem=Get-Item -LiteralPath $Path;return @{path=$airItem.FullName.Replace('\','/');bytes=$airItem.Length;sha256=(Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()}}
$airArguments=($airTokens | ForEach-Object {'"{0}"' -f $_}) -join ' '
$airProcess=Start-Process -FilePath 'G:/UE_5.5/Engine/Binaries/Win64/UnrealEditor.exe' -ArgumentList $airArguments -WorkingDirectory $airStage -WindowStyle Hidden -PassThru
Write-AirNewJson (Join-Path $airMedia 'launch-receipt-v001.json') @{process_id=$airProcess.Id;requested_facing=$airReg.requested_facing;arguments=$airTokens;requested_fixed_time_step=$false;human_input=$false;diagnostic_clear_knight=$true;started_utc=(Get-Date).ToUniversalTime().ToString('O')}
Write-Output ('Hero Air production PID {0}, side {1}, archive {2}' -f $airProcess.Id,$Side,$airMedia)
$airModule=$null
$airModuleDeadline=[DateTime]::UtcNow.AddSeconds(20)
while(-not $airProcess.HasExited -and [DateTime]::UtcNow -lt $airModuleDeadline){
 try{$airProcess.Refresh();$airModule=@($airProcess.Modules | Where-Object {$_.ModuleName -eq 'UnrealEditor-CodexDungeon.dll'} | Select-Object -First 1);if($airModule.Count){break}}catch{}
 Start-Sleep -Milliseconds 100
}
if($airModule -and $airModule.Count){
 $airLoadedPath=[IO.Path]::GetFullPath($airModule[0].FileName)
 Write-AirNewJson (Join-Path $airMedia 'actual-loaded-staged-module-v001.json') @{schema='Root-actual-native-staged-module-observation-v001';process_id=$airProcess.Id;actual_loaded_DLL=$airLoadedPath.Replace('\','/');module_pin=(Get-AirPin $airLoadedPath);expected_staged_DLL=(Join-Path $airStage 'Binaries/Win64/UnrealEditor-CodexDungeon.dll').Replace('\','/');staged_project_path=$airTokens[0];observed_utc=(Get-Date).ToUniversalTime().ToString('O');observation_method='System.Diagnostics.Process.Modules actual live process';FinalAccepted=$false}
}
$airProcess.WaitForExit()
Assert-AirStageRuntime

$airNativeFlowPassed=$false
$airReportPath=Join-Path $airNative 'runtime-report.json'
if(Test-Path -LiteralPath $airReportPath){try{$airRuntimeReport=Get-Content -LiteralPath $airReportPath -Raw | ConvertFrom-Json;$airNativeFlowPassed=($airRuntimeReport.passed -eq $true -and $airRuntimeReport.flow_complete -eq $true)}catch{$airNativeFlowPassed=$false}}
Write-AirNewJson (Join-Path $airMedia 'index.json') @{schema='hero-Air6-production-native-session-v001';process_id=$airProcess.Id;exit_code=$airProcess.ExitCode;root_prereg_pin=(Get-AirPin $airPrereg);compiled_manifest_pin=$airReg.compiled_manifest_pin;checker_freeze_pin=$airReg.checker_freeze_pin;source_probe_freeze_pin=$airReg.source_probe_freeze_pin;finished_utc=(Get-Date).ToUniversalTime().ToString('O');FinalAccepted=$false;native_independent_verification_pending=$true;workflow_native_flow_report_passed=$airNativeFlowPassed}
Write-Output ('Hero Air production exit {0}: {1}' -f $airProcess.ExitCode,$airMedia)
if(-not $airNativeFlowPassed){Write-Output ('Native core flow did not pass; actual OS exit '+$airProcess.ExitCode+' preserved in index; workflow exits3');exit 3}
exit $airProcess.ExitCode
