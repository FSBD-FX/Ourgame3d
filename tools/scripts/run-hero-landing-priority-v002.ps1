param([Parameter(Mandatory=$true)][ValidateSet('J','Shift')][string]$Action,[Parameter(Mandatory=$true)][ValidateSet('left','right')][string]$Side,[ValidatePattern('^v[0-9]{3}$')][string]$Version='v001',[Parameter(Mandatory=$true)][string]$CheckerFreeze,[Parameter(Mandatory=$true)][string]$CheckerDirectory)
$ErrorActionPreference='Stop'
$landingRoot='F:/Ourgame'
$landingPython=Join-Path $landingRoot 'tools/runtime/asset-gen/Scripts/python.exe'
$landingChecker=Join-Path ([IO.Path]::GetFullPath($CheckerDirectory)) 'verify-landing-priority-native-v001.py'
if(Get-Process -Name UnrealEditor,UnrealEditor-Cmd,UnrealBuildTool -ErrorAction SilentlyContinue){throw 'Sequential native landing capture requires no UE/UBT process.'}
& $landingPython -B -X utf8 (Join-Path $landingRoot 'tools/scripts/prepare-hero-landing-priority-prereg-v002.py') --action $Action --side $Side --version $Version --checker-freeze $CheckerFreeze --checker-directory $CheckerDirectory
if($LASTEXITCODE -ne 0){throw 'Actual Root prereg failed; preserve new archive.'}
$landingMedia=Join-Path $landingRoot ('过程图稿与视频/2026-10-19_钟盔落地{0}_{1}_{2}' -f $Action,$Side,$Version)
$landingPrereg=Join-Path $landingMedia 'preregistration-v001.json'
& $landingPython -B -X utf8 $landingChecker --preflight --prereg $landingPrereg --out (Join-Path $landingMedia 'independent-preflight-v001.json')
if($LASTEXITCODE -ne 0){throw 'Frozen landing preflight failed; UE was not started.'}
$landingReg=Get-Content -LiteralPath $landingPrereg -Raw|ConvertFrom-Json
$landingNative=Join-Path $landingMedia '原件'
$landingFacing=if($Side -eq 'left'){'-1'}else{'1'}
$landingArgs=@('F:/Ourgame/UnrealGame/CodexDungeon.uproject','/Game/Maps/FirstRoom?DungeonFirstBatchGuardRoom','-game','-d3d11','-windowed','-ResX=1280','-ResY=720','-NoSplash','-NoLiveCoding','-nop4','-DungeonCandidateSprites','-DungeonFairytaleSwordBodyPreview','-DungeonFairytaleSwordBodyV002Preview','-DungeonFairytaleSwordArmorPrimary1Preview','-DungeonFairytaleSwordPrimary2Preview','-DungeonFairytaleSwordPrimary2BodyPreview','-DungeonFairytaleSwordPrimary2ArmorPreview','-DungeonFairytaleSwordPrimary3ArmorPreview','-DungeonFairytaleLeatherReadyPreview','-DungeonFairytaleLeatherPrimary1Preview','-DungeonFairytaleLeatherPrimary2Preview','-DungeonFairytaleLeatherPrimary3Preview','-DungeonFairytaleSwordEquipmentBoundPreview','-DungeonFairytaleSwordWalkPreview','-DungeonFairytaleSwordHurtPreview','-DungeonFairytaleSwordDeathPreview','-DungeonFairytaleSwordDodgePreview','-DungeonFairytaleSwordAirPreview','-DungeonFairytaleGuardFullPreview','-DungeonFairytaleGuardStompPreview','-DungeonFairytaleGuardMoveRigPreview','-DungeonContentProof','-DungeonHeroLandingPriorityProofV001',('-DungeonHeroLandingPriorityAction='+$Action),('-DungeonHeroLandingPriorityFacing='+$landingFacing),'-DungeonHeroLandingPriorityClearKnightDiagnostic','-DungeonFastLosslessCapture','-DungeonAsyncLosslessCapture',('-DungeonContentProofDir='+$landingNative),('-abslog='+(Join-Path $landingMedia 'native-engine.log')))
function Write-LandingNewJson([string]$Path,[object]$Value){
 $landingStream=[IO.FileStream]::new($Path,[IO.FileMode]::CreateNew,[IO.FileAccess]::Write,[IO.FileShare]::Read)
 try{$landingBytes=[Text.UTF8Encoding]::new($false).GetBytes(($Value|ConvertTo-Json -Depth 16));$landingStream.Write($landingBytes,0,$landingBytes.Length);$landingStream.Flush($true)}finally{$landingStream.Dispose()}
}
function Get-LandingPin([string]$Path){$landingItem=Get-Item -LiteralPath $Path;return @{path=$landingItem.FullName;bytes=$landingItem.Length;sha256=(Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()}}
$landingArgumentLine=($landingArgs|ForEach-Object {'"{0}"' -f $_}) -join ' '
$landingProcess=Start-Process -FilePath 'G:/UE_5.5/Engine/Binaries/Win64/UnrealEditor.exe' -ArgumentList $landingArgumentLine -WorkingDirectory 'F:/Ourgame/UnrealGame' -WindowStyle Hidden -PassThru
Write-LandingNewJson (Join-Path $landingMedia 'launch-receipt-v001.json') @{schema='Root-hero-landing-priority-launch-v001';process_id=$landingProcess.Id;requested_action=$Action;requested_facing=$landingReg.requested_facing;arguments=$landingArgs;started_utc=(Get-Date).ToUniversalTime().ToString('O');human_input=$false;diagnostic_clear_knight=$true;fixed_time_step_requested=$false;FinalAccepted=$false}
Write-Output ('Landing '+$Action+' '+$Side+' PID '+$landingProcess.Id)
$landingProcess.WaitForExit()
$landingRuntimePath=Join-Path $landingNative 'runtime-report.json'
$landingFlowPassed=$false
if(Test-Path -LiteralPath $landingRuntimePath){try{$landingRuntime=Get-Content -LiteralPath $landingRuntimePath -Raw|ConvertFrom-Json;$landingFlowPassed=$landingRuntime.passed -eq $true -and $landingRuntime.flow_complete -eq $true}catch{$landingFlowPassed=$false}}
Write-LandingNewJson (Join-Path $landingMedia 'index.json') @{schema='hero-landing-priority-native-session-v001';process_id=$landingProcess.Id;exit_code=$landingProcess.ExitCode;root_prereg_pin=(Get-LandingPin $landingPrereg);compiled_manifest_pin=$landingReg.compiled_manifest_pin;source_admission_pin=$landingReg.source_admission_pin;source_repair_admission_pin=$landingReg.source_repair_admission_pin;source_candidate_freeze_pin=$landingReg.source_candidate_freeze_pin;checker_freeze_pin=$landingReg.checker_freeze_pin;finished_utc=(Get-Date).ToUniversalTime().ToString('O');workflow_native_flow_passed=$landingFlowPassed;native_independent_verification_pending=$true;FinalAccepted=$false}
if(-not $landingFlowPassed){Write-Output ('Native flow did not pass; actual OS exit '+$landingProcess.ExitCode+' preserved. Workflow exits3.');exit 3}
Write-Output ('Native landing flow passed '+$landingMedia)
exit $landingProcess.ExitCode
