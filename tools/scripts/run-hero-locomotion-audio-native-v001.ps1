param(
 [Parameter(Mandatory=$true)][string]$CompiledManifest,
 [Parameter(Mandatory=$true)][string]$SourceAdmission,
 [Parameter(Mandatory=$true)][string]$Checker,
 [Parameter(Mandatory=$true)][string]$CheckerFreeze,
 [ValidatePattern('^v[0-9]{3}$')][string]$Version='v001'
)
$ErrorActionPreference='Stop'
$locomotionRoot='F:/Ourgame'
$locomotionPython=Join-Path $locomotionRoot 'tools/runtime/asset-gen/Scripts/python.exe'
if(Get-Process -Name UnrealEditor,UnrealEditor-Cmd,UnrealBuildTool -ErrorAction SilentlyContinue){throw 'Sequential native capture requires no UE/UBT process'}
$locomotionMedia=Join-Path $locomotionRoot ('过程图稿与视频/2026-10-19_钟盔移动音效实机_Shift_right_'+$Version)
if(Test-Path -LiteralPath $locomotionMedia){throw 'Preserve all previous runs: fresh version required'}
function Write-LocomotionNewJson([string]$Path,[object]$Value){
 $locomotionStream=[IO.FileStream]::new($Path,[IO.FileMode]::CreateNew,[IO.FileAccess]::Write,[IO.FileShare]::Read)
 try{$locomotionBytes=[Text.UTF8Encoding]::new($false).GetBytes(($Value|ConvertTo-Json -Depth 20));$locomotionStream.Write($locomotionBytes,0,$locomotionBytes.Length);$locomotionStream.Flush($true)}finally{$locomotionStream.Dispose()}
}
function Get-LocomotionPin([string]$Path){$locomotionItem=Get-Item -LiteralPath $Path;return @{path=$locomotionItem.FullName;bytes=$locomotionItem.Length;sha256=(Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()}}
New-Item -ItemType Directory -Path $locomotionMedia | Out-Null
$locomotionNative=Join-Path $locomotionMedia '原件'
New-Item -ItemType Directory -Path $locomotionNative | Out-Null
New-Item -ItemType Directory -Path (Join-Path $locomotionMedia '展示副本') | Out-Null
$locomotionPrereg=Join-Path $locomotionMedia 'preregistration-v001.json'
$locomotionRegistration=@{schema='Root-hero-locomotion-audio-native-prereg-v001';RootApproved=$true;is_template=$false;pre_registered_before_capture=$true;created_utc=(Get-Date).ToUniversalTime().ToString('O');requested_action='Shift';requested_facing=1;diagnostic_clear_knight=$true;run_directory=$locomotionMedia;compiled_manifest_pin=(Get-LocomotionPin $CompiledManifest);source_admission_pin=(Get-LocomotionPin $SourceAdmission);checker_freeze_pin=(Get-LocomotionPin $CheckerFreeze);checker_pin=(Get-LocomotionPin $Checker);launcher_pin=(Get-LocomotionPin $PSCommandPath);correlation_threshold=0.75;correlation_window_policy='Actual first-seen completed callback interval expanded by fixed -0.10/+0.25s in pinned template_search; no SimulationTime as PCM time';capture_scope='Normal controller Enter/D/E/Space/landing Shift; explicit Knight diagnostic and display light-armor source. Five naturally covered cue types; Light untriggered. Requests/correlation are not listening, codec, latency or exclusive attribution.';FinalAccepted=$false}
Write-LocomotionNewJson $locomotionPrereg $locomotionRegistration
Write-LocomotionNewJson (Join-Path $locomotionMedia '来源-版本-状态索引.json') @{schema='Root-hero-locomotion-audio-native-source-index-v001';version=$Version;prereg=(Get-LocomotionPin $locomotionPrereg);originals='原件';presentation='展示副本';status='PRE_REGISTERED_NOT_YET_CAPTURED';E_retention='PENDING_ROOT_BEFORE_VIEW';FinalAccepted=$false}
[IO.File]::WriteAllText((Join-Path $locomotionMedia 'README.md'),'正常输入移动音效实机实录。原件包括完整原生PNG、真实MainMix、具名请求与输入回执。Knight明确诊断清理、轻甲为受控显示来源。请求／相关性不代表听感、设备延迟或逐codec验收；未E保全前不View。',[Text.UTF8Encoding]::new($false))
& $locomotionPython -B -X utf8 $Checker --preflight --compiled-manifest $CompiledManifest --source-admission $SourceAdmission --out (Join-Path $locomotionMedia 'independent-preflight-v001.json')
if($LASTEXITCODE -ne 0){throw 'Current lineage preflight failed; UE not started'}
$locomotionArgs=@('F:/Ourgame/UnrealGame/CodexDungeon.uproject','/Game/Maps/FirstRoom?DungeonFirstBatchGuardRoom','-game','-d3d11','-windowed','-ResX=1280','-ResY=720','-NoSplash','-NoLiveCoding','-nop4','-DungeonCandidateSprites','-DungeonFairytaleSwordBodyPreview','-DungeonFairytaleSwordBodyV002Preview','-DungeonFairytaleSwordArmorPrimary1Preview','-DungeonFairytaleSwordPrimary2Preview','-DungeonFairytaleSwordPrimary2BodyPreview','-DungeonFairytaleSwordPrimary2ArmorPreview','-DungeonFairytaleSwordPrimary3ArmorPreview','-DungeonFairytaleLeatherReadyPreview','-DungeonFairytaleLeatherPrimary1Preview','-DungeonFairytaleLeatherPrimary2Preview','-DungeonFairytaleLeatherPrimary3Preview','-DungeonFairytaleSwordEquipmentBoundPreview','-DungeonFairytaleSwordWalkPreview','-DungeonFairytaleSwordHurtPreview','-DungeonFairytaleSwordDeathPreview','-DungeonFairytaleSwordDodgePreview','-DungeonFairytaleSwordAirPreview','-DungeonFairytaleGuardFullPreview','-DungeonFairytaleGuardStompPreview','-DungeonFairytaleGuardMoveRigPreview','-DungeonContentProof','-DungeonHeroLandingPriorityProofV001','-DungeonHeroLandingPriorityAction=Shift','-DungeonHeroLandingPriorityFacing=1','-DungeonHeroLandingPriorityClearKnightDiagnostic','-DungeonFastLosslessCapture','-DungeonAsyncLosslessCapture',('-DungeonContentProofDir='+$locomotionNative),('-abslog='+(Join-Path $locomotionMedia 'native-engine.log')))
$locomotionArgumentLine=($locomotionArgs|ForEach-Object {'"{0}"' -f $_}) -join ' '
$locomotionProcess=Start-Process -FilePath 'G:/UE_5.5/Engine/Binaries/Win64/UnrealEditor.exe' -ArgumentList $locomotionArgumentLine -WorkingDirectory 'F:/Ourgame/UnrealGame' -WindowStyle Hidden -PassThru
Write-LocomotionNewJson (Join-Path $locomotionMedia 'launch-receipt-v001.json') @{schema='Root-hero-locomotion-audio-native-launch-v001';process_id=$locomotionProcess.Id;requested_action='Shift';requested_facing=1;arguments=$locomotionArgs;started_utc=(Get-Date).ToUniversalTime().ToString('O');human_input=$false;diagnostic_clear_knight=$true;fixed_time_step_requested=$false;FinalAccepted=$false}
Write-Output ('Locomotion native Shift right PID '+$locomotionProcess.Id)
$locomotionProcess.WaitForExit()
Write-LocomotionNewJson (Join-Path $locomotionMedia 'index.json') @{schema='Root-hero-locomotion-audio-native-session-v001';process_id=$locomotionProcess.Id;exit_code=$locomotionProcess.ExitCode;root_prereg_pin=(Get-LocomotionPin $locomotionPrereg);compiled_manifest_pin=$locomotionRegistration.compiled_manifest_pin;source_admission_pin=$locomotionRegistration.source_admission_pin;checker_freeze_pin=$locomotionRegistration.checker_freeze_pin;finished_utc=(Get-Date).ToUniversalTime().ToString('O');native_independent_verification_pending=$true;FinalAccepted=$false}
if($locomotionProcess.ExitCode -ne 0){Write-Output ('Actual native exit '+$locomotionProcess.ExitCode+' preserved');exit $locomotionProcess.ExitCode}
& $locomotionPython -B -X utf8 $Checker --archive $locomotionMedia --compiled-manifest $CompiledManifest --source-admission $SourceAdmission --out (Join-Path $locomotionMedia 'independent-native-verification-v001.json')
exit $LASTEXITCODE
