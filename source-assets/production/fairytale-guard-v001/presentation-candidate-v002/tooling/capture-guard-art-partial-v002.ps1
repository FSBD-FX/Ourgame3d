param(
 [string]$EngineRoot='G:\UE_5.5',
 [Parameter(Mandatory=$true)][ValidatePattern('^[A-Za-z0-9_-]+$')][string]$Version,
 [Parameter(Mandatory=$true)][string]$Snapshot,
 [Parameter(Mandatory=$true)][string]$RootPrereg,
 [ValidateSet(-1,0,1)][int]$ApproachSide=0,
 [switch]$ValidateOnly
)
$ErrorActionPreference='Stop'
$workspace=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\..\..\..\..'))
$candidate=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
$python=Join-Path $workspace 'tools/runtime/asset-gen/Scripts/python.exe'
$checker=Join-Path $PSScriptRoot 'verify-guard-art-partial-v002.py'
$snapshotDirectory=if([IO.Path]::IsPathRooted($Snapshot)){[IO.Path]::GetFullPath($Snapshot)}else{[IO.Path]::GetFullPath((Join-Path $workspace $Snapshot))}
$rootPreregPath=[IO.Path]::GetFullPath($RootPrereg)
$manifestPath=Join-Path $snapshotDirectory 'compiled-source-manifest.json'
$preflight=& $python -B -X utf8 $checker --snapshot $snapshotDirectory --root-prereg $rootPreregPath --source-only
if($LASTEXITCODE -ne 0){throw 'Concrete compiled Source/DLL/full-suite/16 exact partial trial profile preflight failed.'}
$facts=$preflight|ConvertFrom-Json
if($ValidateOnly){[ordered]@{compiled_inputs_verified=$true;registry=$facts.strict_registry;partial_rows=3;unique_texture_bindings=16;UE_started=$false}|ConvertTo-Json;return}
if(@(Get-Process -Name 'UnrealEditor*','UnrealBuildTool' -ErrorAction SilentlyContinue).Count){throw 'Sequential native trial requires no live UE/UBT.'}
$archive=Join-Path $workspace ('过程图稿与视频\'+(Get-Date -Format 'yyyy-MM-dd')+'_石守卫三行整身原生试样_'+$Version)
if(Test-Path -LiteralPath $archive){throw 'Preserve earlier originals; choose new version.'}
$original=Join-Path $archive '原件'
[IO.Directory]::CreateDirectory($original)|Out-Null
[IO.Directory]::CreateDirectory((Join-Path $archive '展示副本'))|Out-Null
$indexPath=Join-Path $archive 'index.json'
$index=[ordered]@{schema='guard-art-partial-native-session-v002';status='capture_started';snapshot=$snapshotDirectory;snapshot_manifest_sha256=(Get-FileHash -LiteralPath $manifestPath -Algorithm SHA256).Hash.ToLowerInvariant();root_prereg_sha256=(Get-FileHash -LiteralPath $rootPreregPath -Algorithm SHA256).Hash.ToLowerInvariant();candidate_freeze_sha256=(Get-FileHash -LiteralPath (Join-Path $candidate 'observer-freeze-v002.json') -Algorithm SHA256).Hash.ToLowerInvariant();process_id=$null;exit_code=$null;native_reported_passed=$null;independent_passed=$false;normal_J_full_clear=$false;diagnostic_Knight_Bat=$true;guard_spawned_by_probe=$false;audio_recorded=$false;visual_reviewed=$false;formal_complete_units=0;E_before_view=$true;requested_approach_side=$ApproachSide}
$index|ConvertTo-Json -Depth 8|Set-Content -LiteralPath $indexPath -Encoding utf8
$art=@('-DungeonCandidateSprites','-DungeonFairytaleSwordBodyPreview','-DungeonFairytaleSwordBodyV002Preview','-DungeonFairytaleSwordArmorPrimary1Preview','-DungeonFairytaleSwordPrimary2Preview','-DungeonFairytaleSwordPrimary2BodyPreview','-DungeonFairytaleSwordPrimary2ArmorPreview','-DungeonFairytaleSwordPrimary3ArmorPreview','-DungeonFairytaleLeatherReadyPreview','-DungeonFairytaleLeatherPrimary1Preview','-DungeonFairytaleLeatherPrimary2Preview','-DungeonFairytaleLeatherPrimary3Preview','-DungeonFairytaleSwordEquipmentBoundPreview','-DungeonFairytaleSwordWalkPreview','-DungeonFairytaleGuardPartialPreview')
$arguments=@(('"{0}"' -f (Join-Path $workspace 'UnrealGame\CodexDungeon.uproject')),'/Game/Maps/FirstRoom?DungeonFirstBatchGuardRoom','-game','-windowed','-ResX=1280','-ResY=720','-NoSplash','-NoLiveCoding','-nop4','-unattended','-DungeonGuardArtPartialProof','-DungeonContentProof','-DungeonFastLosslessCapture','-DungeonAsyncLosslessCapture',('-DungeonGuardArtApproachSide={0}' -f $ApproachSide),('-DungeonContentProofDir="{0}"' -f $original),'-ExecCmds="t.MaxFPS 30,r.ScreenshotDelegate 1"',('-abslog="{0}"' -f (Join-Path $archive 'runtime.log')))+$art
try{
 $process=Start-Process -FilePath (Join-Path $EngineRoot 'Engine\Binaries\Win64\UnrealEditor.exe') -ArgumentList $arguments -WindowStyle Hidden -PassThru
 $index.process_id=$process.Id;Write-Output "Formal Guard partial art observer PID $($process.Id), archive $archive"
 $deadline=[DateTime]::UtcNow.AddSeconds(180)
 while(-not $process.WaitForExit(30000)){if([DateTime]::UtcNow -ge $deadline){Stop-Process -Id $process.Id -Force;throw 'Native observer timeout; all failed originals preserved.'};Write-Output "Native observer PID $($process.Id) still running; preserve normal engine pacing."}
 $process.Refresh();$index.exit_code=$process.ExitCode
 $reportPath=Join-Path $original 'runtime-report.json'
 if(-not(Test-Path -LiteralPath $reportPath)){throw 'Native report missing; failed originals preserved.'}
 $report=Get-Content -LiteralPath $reportPath -Raw -Encoding UTF8|ConvertFrom-Json;$index.native_reported_passed=$report.passed
 if($process.ExitCode -ne 0 -or -not $report.passed){$index.status='actual_native_RED_preserved';throw ('Actual observer RED: '+$report.failure)}
 & $python -B -X utf8 $checker --snapshot $snapshotDirectory --root-prereg $rootPreregPath --archive $archive --write-receipt
 if($LASTEXITCODE -ne 0){throw 'Independent native clocks/source/floor/single-layer/all-phase/CRC/FIFO verification failed; keep originals.'}
 $index.independent_passed=$true;$index.status='native_partial_trial_passed_visual_review_pending'
}catch{
 if($index.status -ne 'actual_native_RED_preserved'){$index.status='failed_preserved'}
 $index['failure']=$_.Exception.Message;$index|ConvertTo-Json -Depth 8|Set-Content -LiteralPath $indexPath -Encoding utf8;throw
}
$index|ConvertTo-Json -Depth 8|Set-Content -LiteralPath $indexPath -Encoding utf8
Write-Output $archive
