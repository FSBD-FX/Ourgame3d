param(
 [string]$EngineRoot='G:\UE_5.5',
 [Parameter(Mandatory=$true)][ValidatePattern('^[A-Za-z0-9_-]+$')][string]$Version,
 [string]$DiagnosticInputs='source-assets/production/leather-combo-diagnostic-root-input-v002/diagnostic-compiled-inputs-v002.json'
)
$ErrorActionPreference='Stop'
$workspace='F:\Ourgame'
if(@(Get-Process -Name 'UnrealEditor*','UnrealBuildTool' -ErrorAction SilentlyContinue).Count){throw 'Sequential proof requires no live UE/UBT.'}
$manifestPath=Join-Path $workspace $DiagnosticInputs
$manifest=Get-Content -LiteralPath $manifestPath -Raw|ConvertFrom-Json
foreach($row in $manifest.files){
 $live=Join-Path $workspace $row.path
 if((Get-Item -LiteralPath $live).Length -ne $row.bytes -or (Get-FileHash -LiteralPath $live -Algorithm SHA256).Hash.ToLowerInvariant() -ne $row.sha256){throw "Source freeze mismatch: $live"}
}
& (Join-Path $workspace 'tools/runtime/asset-gen/Scripts/python.exe') -B -X utf8 (Join-Path $PSScriptRoot 'verify-leather-combo-art-diagnostic-v003.py') --diagnostic-inputs $DiagnosticInputs --source-only
if($LASTEXITCODE -ne 0){throw 'Concrete combo Source/DLL/production/receipts/current full-suite contract preflight failed before capture.'}
$archive=Join-Path $workspace ('过程图稿与视频\'+(Get-Date -Format 'yyyy-MM-dd')+'_NONRELEASE软皮连招美术诊断_'+$Version)
if(Test-Path -LiteralPath $archive){throw 'Preserve previous capture; choose new version.'}
$original=Join-Path $archive '原件';$presentation=Join-Path $archive '展示副本'
[IO.Directory]::CreateDirectory($original)|Out-Null;[IO.Directory]::CreateDirectory($presentation)|Out-Null
$index=[ordered]@{schema='NONRELEASE_ART_DIAGNOSTIC-v001';current_full_GREEN=$false;current_automation_succeeded=$null;status='NONRELEASE_ART_DIAGNOSTIC_capture_started';snapshot=$DiagnosticInputs;formal_complete_units=0;audio_recorded=$false;source_manifest_SHA256=(Get-FileHash -LiteralPath $manifestPath -Algorithm SHA256).Hash.ToLowerInvariant();process_id=$null;exit_code=$null;runtime_passed=$null;observations=$null}
$indexPath=Join-Path $archive 'index.json'
$index|ConvertTo-Json -Depth 8|Set-Content -LiteralPath $indexPath -Encoding utf8
$arguments=@(('"{0}"' -f (Join-Path $workspace 'UnrealGame\CodexDungeon.uproject')),'/Game/Maps/FirstRoom','-game','-windowed','-ResX=1280','-ResY=720','-NoSplash','-NoLiveCoding','-nop4','-unattended',
 '-DungeonSceneExplorationPreview','-DungeonCandidateSprites','-DungeonFairytaleSwordBodyPreview','-DungeonFairytaleSwordBodyV002Preview','-DungeonFairytaleSwordArmorPrimary1Preview','-DungeonFairytaleSwordPrimary2Preview','-DungeonFairytaleSwordPrimary2BodyPreview','-DungeonFairytaleSwordPrimary2ArmorPreview','-DungeonFairytaleSwordPrimary3ArmorPreview',
 '-DungeonFairytaleLeatherReadyPreview','-DungeonFairytaleLeatherPrimary1Preview','-DungeonFairytaleLeatherPrimary2Preview','-DungeonFairytaleLeatherPrimary3Preview','-DungeonFairytaleLeatherComboOnlyProof','-DungeonFairytaleSwordEquipmentBoundPreview','-DungeonFairytaleEquipmentBoundProof','-DungeonContentProof','-DungeonFastLosslessCapture','-DungeonAsyncLosslessCapture',('-DungeonContentProofDir="{0}"' -f $original),'-ExecCmds="t.MaxFPS 30,r.ScreenshotDelegate 1"',('-abslog="{0}"' -f (Join-Path $archive 'runtime.log')))
try{
 $process=Start-Process -FilePath (Join-Path $EngineRoot 'Engine\Binaries\Win64\UnrealEditor.exe') -ArgumentList $arguments -WindowStyle Hidden -PassThru
 $index.process_id=$process.Id;Write-Output "Bound flow PID $($process.Id), archive $archive"
 if(-not $process.WaitForExit(240000)){Stop-Process -Id $process.Id -Force;throw 'Timed out; failed originals retained.'}
 $process.Refresh();$index.exit_code=$process.ExitCode
 if($process.ExitCode -ne 0){throw 'Native process failed; preserve originals.'}
 $reportPath=Join-Path $original 'runtime-report.json'
 if(-not(Test-Path -LiteralPath $reportPath)){throw 'Native report missing.'}
 $report=Get-Content -LiteralPath $reportPath -Raw|ConvertFrom-Json
 & (Join-Path $workspace 'tools\runtime\asset-gen\Scripts\python.exe') -B -X utf8 (Join-Path $workspace 'tools/scripts/verify-native-bound-capture-pixels-v001.py') --archive $archive --write-receipt
 if($LASTEXITCODE -ne 0){throw 'Original native CRC/FIFO/stop-flush verification failed.'}
 foreach($row in $manifest.files){
  $live=Join-Path $workspace $row.path
  if((Get-Item -LiteralPath $live).Length -ne $row.bytes -or (Get-FileHash -LiteralPath $live -Algorithm SHA256).Hash.ToLowerInvariant() -ne $row.sha256){throw "Capture changed frozen input: $live"}
 }
 $index.runtime_passed=$report.passed;$index['native_reported_passed']=$report.passed;$index.observations=@($report.observations).Count
 $index.status=if($report.passed){'NONRELEASE_ART_DIAGNOSTIC_native_flow_passed_art_review_pending'}else{'actual_native_RED_preserved'}
 $index|ConvertTo-Json -Depth 8|Set-Content -LiteralPath $indexPath -Encoding utf8
 & (Join-Path $workspace 'tools/runtime/asset-gen/Scripts/python.exe') -B -X utf8 (Join-Path $PSScriptRoot 'verify-leather-combo-art-diagnostic-v003.py') --diagnostic-inputs $DiagnosticInputs --source-only
 if($LASTEXITCODE -ne 0){throw 'Capture changed combo Source/compiled inputs/original RGBA contract.'}
 if($report.passed){
  & (Join-Path $workspace 'tools/runtime/asset-gen/Scripts/python.exe') -B -X utf8 (Join-Path $PSScriptRoot 'verify-leather-combo-art-diagnostic-v003.py') --diagnostic-inputs $DiagnosticInputs --archive $archive
  if($LASTEXITCODE -ne 0){$index.runtime_passed=$false;throw 'Native reported passed but independent combo technical verification failed; preserve all originals.'}
 }
 # A native behavior RED is evidence, not an execution error. Do not disguise it as GREEN.
}catch{
 $index.status='execution_failed_preserved';$index['failure']=$_.Exception.Message
 $index|ConvertTo-Json -Depth 8|Set-Content -LiteralPath $indexPath -Encoding utf8
 throw
}
$index|ConvertTo-Json -Depth 8|Set-Content -LiteralPath $indexPath -Encoding utf8
Write-Output $archive
