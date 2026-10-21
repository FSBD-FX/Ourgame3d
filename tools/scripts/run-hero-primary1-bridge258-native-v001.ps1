param(
 [Parameter(Mandatory=$true)][string]$CompiledManifest,
 [Parameter(Mandatory=$true)][string]$SourceAdmission,
 [Parameter(Mandatory=$true)][string]$Checker,
 [Parameter(Mandatory=$true)][string]$CheckerFreeze,
 [ValidatePattern('^v[0-9]{3}$')][string]$Version='v001',
 [ValidateSet('left','right')][string]$Side='right'
)
$ErrorActionPreference='Stop'
$bridgeCaptureRoot='F:/Ourgame'
$bridgeCapturePython=Join-Path $bridgeCaptureRoot 'tools/runtime/asset-gen/Scripts/python.exe'
if(Get-Process -Name UnrealEditor,UnrealEditor-Cmd,UnrealBuildTool -ErrorAction SilentlyContinue){throw 'Sequential native capture requires no UE/UBT process'}
$bridgeFacing=if($Side -eq 'left'){-1}else{1}
$bridgeCaptureMedia=Join-Path $bridgeCaptureRoot ('过程图稿与视频/2026-10-19_钟盔起手258实机_J_'+$Side+'_'+$Version)
if(Test-Path -LiteralPath $bridgeCaptureMedia){throw 'Preserve all previous runs: fresh version required'}
function Write-BridgeCaptureNewJson([string]$Path,[object]$Value){
 $bridgeCaptureStream=[IO.FileStream]::new($Path,[IO.FileMode]::CreateNew,[IO.FileAccess]::Write,[IO.FileShare]::Read)
 try{$bridgeCaptureBytes=[Text.UTF8Encoding]::new($false).GetBytes(($Value|ConvertTo-Json -Depth 20));$bridgeCaptureStream.Write($bridgeCaptureBytes,0,$bridgeCaptureBytes.Length);$bridgeCaptureStream.Flush($true)}finally{$bridgeCaptureStream.Dispose()}
}
function Get-BridgeCapturePin([string]$Path){$bridgeCaptureItem=Get-Item -LiteralPath $Path;return @{path=$bridgeCaptureItem.FullName;bytes=$bridgeCaptureItem.Length;sha256=(Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()}}
New-Item -ItemType Directory -Path $bridgeCaptureMedia | Out-Null
$bridgeCaptureNative=Join-Path $bridgeCaptureMedia '原件'
New-Item -ItemType Directory -Path $bridgeCaptureNative | Out-Null
New-Item -ItemType Directory -Path (Join-Path $bridgeCaptureMedia '展示副本') | Out-Null
$bridgeCapturePrereg=Join-Path $bridgeCaptureMedia 'preregistration-v001.json'
$bridgeCaptureRegistration=@{schema='Root-primary1-bridge258-native-prereg-v001';RootApproved=$true;is_template=$false;pre_registered_before_capture=$true;created_utc=(Get-Date).ToUniversalTime().ToString('O');requested_action='J';requested_facing=$bridgeFacing;diagnostic_clear_knight=$true;run_directory=$bridgeCaptureMedia;compiled_manifest_pin=(Get-BridgeCapturePin $CompiledManifest);source_admission_pin=(Get-BridgeCapturePin $SourceAdmission);checker_freeze_pin=(Get-BridgeCapturePin $CheckerFreeze);checker_pin=(Get-BridgeCapturePin $Checker);launcher_pin=(Get-BridgeCapturePin $PSCommandPath);capture_scope='Normal controller Enter/D/facing/E/Space/landing J; explicit Knight diagnostic and display light armor. New J0/J1 actual layers and source points followed by unchanged J2-5 and Ready. No art/listening/final acceptance from metadata alone.';FinalAccepted=$false}
Write-BridgeCaptureNewJson $bridgeCapturePrereg $bridgeCaptureRegistration
Write-BridgeCaptureNewJson (Join-Path $bridgeCaptureMedia '来源-版本-状态索引.json') @{schema='Root-primary1-bridge258-native-source-index-v001';version=$Version;prereg=(Get-BridgeCapturePin $bridgeCapturePrereg);originals='原件';presentation='展示副本';status='PRE_REGISTERED_NOT_YET_CAPTURED';E_retention='PENDING_ROOT_BEFORE_VIEW';FinalAccepted=$false}
[IO.File]::WriteAllText((Join-Path $bridgeCaptureMedia 'README.md'),'新起手两帧实机试装。完整原生PNG、实际14纹理GPU/source读回、真实MainMix和输入回执。Knight明确诊断清理，轻甲为受控显示来源。旧完整Body metadata非新body像素；验证实际8层绘制与源点。未E保全前不View。',[Text.UTF8Encoding]::new($false))
& $bridgeCapturePython -B -X utf8 $Checker --preflight --compiled-manifest $CompiledManifest --source-admission $SourceAdmission --out (Join-Path $bridgeCaptureMedia 'independent-preflight-v001.json')
if($LASTEXITCODE -ne 0){throw 'Current lineage preflight failed; UE not started'}
$bridgeCaptureArgs=@('F:/Ourgame/UnrealGame/CodexDungeon.uproject','/Game/Maps/FirstRoom?DungeonFirstBatchGuardRoom','-game','-d3d11','-windowed','-ResX=1280','-ResY=720','-NoSplash','-NoLiveCoding','-nop4','-DungeonCandidateSprites','-DungeonFairytaleSwordBodyPreview','-DungeonFairytaleSwordBodyV002Preview','-DungeonFairytaleSwordArmorPrimary1Preview','-DungeonFairytaleSwordPrimary2Preview','-DungeonFairytaleSwordPrimary2BodyPreview','-DungeonFairytaleSwordPrimary2ArmorPreview','-DungeonFairytaleSwordPrimary3ArmorPreview','-DungeonFairytaleLeatherReadyPreview','-DungeonFairytaleLeatherPrimary1Preview','-DungeonFairytaleLeatherPrimary2Preview','-DungeonFairytaleLeatherPrimary3Preview','-DungeonFairytaleSwordEquipmentBoundPreview','-DungeonFairytaleSwordWalkPreview','-DungeonFairytaleSwordHurtPreview','-DungeonFairytaleSwordDeathPreview','-DungeonFairytaleSwordDodgePreview','-DungeonFairytaleSwordAirPreview','-DungeonFairytaleGuardFullPreview','-DungeonFairytaleGuardStompPreview','-DungeonFairytaleGuardMoveRigPreview','-DungeonFairytalePrimary1Bridge258Preview','-DungeonContentProof','-DungeonHeroLandingPriorityProofV001','-DungeonHeroLandingPriorityAction=J',('-DungeonHeroLandingPriorityFacing='+$bridgeFacing),'-DungeonHeroLandingPriorityClearKnightDiagnostic','-DungeonFastLosslessCapture','-DungeonAsyncLosslessCapture',('-DungeonContentProofDir='+$bridgeCaptureNative),('-abslog='+(Join-Path $bridgeCaptureMedia 'native-engine.log')))
$bridgeCaptureArgumentLine=($bridgeCaptureArgs|ForEach-Object {'"{0}"' -f $_}) -join ' '
$bridgeCaptureProcess=Start-Process -FilePath 'G:/UE_5.5/Engine/Binaries/Win64/UnrealEditor.exe' -ArgumentList $bridgeCaptureArgumentLine -WorkingDirectory 'F:/Ourgame/UnrealGame' -WindowStyle Hidden -PassThru
Write-BridgeCaptureNewJson (Join-Path $bridgeCaptureMedia 'launch-receipt-v001.json') @{schema='Root-primary1-bridge258-native-launch-v001';process_id=$bridgeCaptureProcess.Id;requested_action='J';requested_facing=$bridgeFacing;arguments=$bridgeCaptureArgs;started_utc=(Get-Date).ToUniversalTime().ToString('O');human_input=$false;diagnostic_clear_knight=$true;fixed_time_step_requested=$false;FinalAccepted=$false}
Write-Output (('Bridge258 native J '+$Side+' PID ')+$bridgeCaptureProcess.Id)
$bridgeCaptureProcess.WaitForExit()
Write-BridgeCaptureNewJson (Join-Path $bridgeCaptureMedia 'index.json') @{schema='Root-primary1-bridge258-native-session-v001';process_id=$bridgeCaptureProcess.Id;exit_code=$bridgeCaptureProcess.ExitCode;root_prereg_pin=(Get-BridgeCapturePin $bridgeCapturePrereg);compiled_manifest_pin=$bridgeCaptureRegistration.compiled_manifest_pin;source_admission_pin=$bridgeCaptureRegistration.source_admission_pin;checker_freeze_pin=$bridgeCaptureRegistration.checker_freeze_pin;finished_utc=(Get-Date).ToUniversalTime().ToString('O');native_independent_verification_pending=$true;FinalAccepted=$false}
if($bridgeCaptureProcess.ExitCode -ne 0){Write-Output ('Actual native exit '+$bridgeCaptureProcess.ExitCode+' preserved');exit $bridgeCaptureProcess.ExitCode}
& $bridgeCapturePython -B -X utf8 $Checker --archive $bridgeCaptureMedia --compiled-manifest $CompiledManifest --source-admission $SourceAdmission --out (Join-Path $bridgeCaptureMedia 'independent-native-verification-v001.json')
exit $LASTEXITCODE
