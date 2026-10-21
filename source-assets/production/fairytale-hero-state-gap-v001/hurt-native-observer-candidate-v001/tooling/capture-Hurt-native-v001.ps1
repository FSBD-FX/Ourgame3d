param(
 [string]$EngineRoot='G:\UE_5.5',
 [Parameter(Mandatory=$true)][ValidatePattern('^[A-Za-z0-9_-]+$')][string]$Version,
 [Parameter(Mandatory=$true)][string]$Snapshot,
 [Parameter(Mandatory=$true)][string]$RootPrereg,
 [ValidateSet(-1,0,1)][int]$ApproachSide=0,
 [switch]$ExecuteNative
)
$ErrorActionPreference='Stop'
$workspace='F:\Ourgame'
$candidate=Split-Path $PSScriptRoot -Parent
$python=Join-Path $workspace 'tools\runtime\asset-gen\Scripts\python.exe'
$checker=Join-Path $PSScriptRoot 'verify-Hurt-native-v001.py'
$snapshotDirectory=if([IO.Path]::IsPathRooted($Snapshot)){[IO.Path]::GetFullPath($Snapshot)}else{[IO.Path]::GetFullPath((Join-Path $workspace $Snapshot))}
$rootPreregPath=[IO.Path]::GetFullPath($RootPrereg)
$manifestPath=Join-Path $snapshotDirectory 'compiled-source-manifest.json'
$preflight=& $python -B -X utf8 $checker --snapshot $snapshotDirectory --root-prereg $rootPreregPath --source-only
if($LASTEXITCODE -ne 0){throw 'Fresh compiled1286/approved extension/Hurt source32/semantic GREEN preflight failed; no UE launch.'}
$facts=$preflight|ConvertFrom-Json
if($facts.approach_side -ne $ApproachSide){throw 'Root prereg and requested native approach side differ.'}
if(-not $ExecuteNative){$facts|ConvertTo-Json -Depth 8;return}
if(@(Get-Process -Name 'UnrealEditor*','UnrealBuildTool' -ErrorAction SilentlyContinue).Count){throw 'Sequential native observer requires UE/UBT closed.'}
$archive=Join-Path $workspace ('过程图稿与视频\'+(Get-Date -Format 'yyyy-MM-dd')+'_钟盔真实守卫重斧Hurt四相试样_'+$Version)
if(Test-Path -LiteralPath $archive){throw 'Preserve all earlier originals; choose a new version.'}
$original=Join-Path $archive '原件'
[IO.Directory]::CreateDirectory($original)|Out-Null
[IO.Directory]::CreateDirectory((Join-Path $archive '展示副本'))|Out-Null
$indexPath=Join-Path $archive 'index.json'
$index=[ordered]@{schema='hero-Hurt4-native-session-v001';status='capture_started';snapshot=$snapshotDirectory;snapshot_manifest_sha256=(Get-FileHash -LiteralPath $manifestPath -Algorithm SHA256).Hash.ToLowerInvariant();root_prereg=$rootPreregPath;root_prereg_sha256=(Get-FileHash -LiteralPath $rootPreregPath -Algorithm SHA256).Hash.ToLowerInvariant();candidate_freeze_sha256=(Get-FileHash -LiteralPath (Join-Path $candidate 'Hurt-native-observer-freeze-v001.json') -Algorithm SHA256).Hash.ToLowerInvariant();requested_approach_side=$ApproachSide;process_id=$null;exit_code=$null;native_reported_passed=$null;independent_passed=$false;diagnostic_Knight_Bat=$true;player_or_Guard_public_damage=$false;audio_recorded=$false;visual_reviewed=$false;formal_complete_units=0;E_before_view=$true}
$index|ConvertTo-Json -Depth 10|Set-Content -LiteralPath $indexPath -Encoding utf8
$art=@('-DungeonCandidateSprites','-DungeonFairytaleSwordBodyPreview','-DungeonFairytaleSwordBodyV002Preview','-DungeonFairytaleSwordArmorPrimary1Preview','-DungeonFairytaleSwordPrimary2Preview','-DungeonFairytaleSwordPrimary2BodyPreview','-DungeonFairytaleSwordPrimary2ArmorPreview','-DungeonFairytaleSwordPrimary3ArmorPreview','-DungeonFairytaleLeatherReadyPreview','-DungeonFairytaleLeatherPrimary1Preview','-DungeonFairytaleLeatherPrimary2Preview','-DungeonFairytaleLeatherPrimary3Preview','-DungeonFairytaleSwordEquipmentBoundPreview','-DungeonFairytaleSwordWalkPreview','-DungeonFairytaleGuardFullPreview','-DungeonFairytaleSwordHurtPreview')
$arguments=@(('"{0}"' -f (Join-Path $workspace 'UnrealGame\CodexDungeon.uproject')),'/Game/Maps/FirstRoom?DungeonFirstBatchGuardRoom','-game','-windowed','-ResX=1280','-ResY=720','-NoSplash','-NoLiveCoding','-nop4','-unattended','-DungeonHeroHurtProofV001','-DungeonContentProof','-DungeonFastLosslessCapture','-DungeonAsyncLosslessCapture',('-DungeonHeroHurtApproachSide={0}' -f $ApproachSide),('-DungeonContentProofDir="{0}"' -f $original),'-ExecCmds="t.MaxFPS 30,r.ScreenshotDelegate 1"',('-abslog="{0}"' -f (Join-Path $archive 'runtime.log')))+$art
try{
 $process=Start-Process -FilePath (Join-Path $EngineRoot 'Engine\Binaries\Win64\UnrealEditor.exe') -ArgumentList $arguments -WorkingDirectory $workspace -WindowStyle Hidden -PassThru
 $index.process_id=$process.Id;$index|ConvertTo-Json -Depth 10|Set-Content -LiteralPath $indexPath -Encoding utf8;Write-Output "Native real Guard-Axe→Hero Hurt4 PID $($process.Id), archive $archive"
 $deadline=[DateTime]::UtcNow.AddSeconds(180)
 while(-not $process.WaitForExit(30000)){if([DateTime]::UtcNow -ge $deadline){Stop-Process -Id $process.Id -Force;throw 'Native observer timeout; failed originals preserved.'};Write-Output "Native observer PID $($process.Id) continues at normal engine pacing."}
 $process.Refresh();$index.exit_code=$process.ExitCode
 $reportPath=Join-Path $original 'runtime-report.json'
 if(-not(Test-Path -LiteralPath $reportPath)){throw 'Native runtime report missing; preserve all failed originals.'}
 $report=Get-Content -LiteralPath $reportPath -Raw -Encoding UTF8|ConvertFrom-Json;$index.native_reported_passed=$report.passed
 $index|ConvertTo-Json -Depth 10|Set-Content -LiteralPath $indexPath -Encoding utf8
 if($process.ExitCode -ne 0 -or -not $report.passed){$index.status='actual_native_RED_preserved';throw ('Actual Hurt observer RED: '+$report.failure)}
 & $python -B -X utf8 $checker --snapshot $snapshotDirectory --root-prereg $rootPreregPath --archive $archive --write-receipt
 if($LASTEXITCODE -ne 0){throw 'Independent real-Hurt/source32/quad pixels/full mirror/CRC/FIFO verification failed; preserve originals.'}
 $index.independent_passed=$true;$index.status='native_Hurt4_trial_verified_visual_review_pending'
}catch{
 if($index.status -ne 'actual_native_RED_preserved'){$index.status='failed_preserved'}
 $index['failure']=$_.Exception.Message;$index|ConvertTo-Json -Depth 10|Set-Content -LiteralPath $indexPath -Encoding utf8;throw
}
$index|ConvertTo-Json -Depth 10|Set-Content -LiteralPath $indexPath -Encoding utf8
Write-Output $archive
