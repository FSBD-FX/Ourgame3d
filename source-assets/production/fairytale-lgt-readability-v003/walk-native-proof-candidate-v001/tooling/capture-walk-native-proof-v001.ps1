param(
 [string]$EngineRoot='G:\UE_5.5',
 [string]$WorkspaceRoot='',
 [string]$SnapshotManifest='',
 [string]$ExpectedProfile='',
 [string]$ArchiveRoot='',
 [ValidatePattern('^[A-Za-z0-9_-]+$')][string]$Version='v001',
 [switch]$Run
)
$ErrorActionPreference='Stop'
$workspace=if([string]::IsNullOrWhiteSpace($WorkspaceRoot)){[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\..\..\..\..'))}else{[IO.Path]::GetFullPath($WorkspaceRoot)}
$candidate=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
$python=Join-Path $workspace 'tools\runtime\asset-gen\Scripts\python.exe'
$checker=Join-Path $PSScriptRoot 'verify-walk-native-proof-v001.py'
foreach($file in @($checker,(Join-Path $PSScriptRoot 'verify-native-walk-pixels-v001.py'))){
 & $python -B -X utf8 -c 'import ast,sys;from pathlib import Path;ast.parse(Path(sys.argv[1]).read_text(encoding="utf-8"));print("Walk verifier syntax parsed; no UE launched")' $file
 if($LASTEXITCODE -ne 0){throw 'Candidate verifier syntax failed'}
}
if(-not $Run){[ordered]@{mode='tooling_only';UE_started=$false;candidate_source=(Join-Path $candidate 'count-boundaries-v003');requires='Root v003 source/HUD admission, measured Profile80/.498/48paths configuration, actual build/full checks, frozen snapshot manifest and independent expected profile'}|ConvertTo-Json;return}
if([string]::IsNullOrWhiteSpace($SnapshotManifest)-or[string]::IsNullOrWhiteSpace($ExpectedProfile)){throw 'Run requires concrete frozen SnapshotManifest and independent measured ExpectedProfile; template fails closed.'}
$SnapshotManifest=[IO.Path]::GetFullPath($SnapshotManifest);$ExpectedProfile=[IO.Path]::GetFullPath($ExpectedProfile)
if(@(Get-Process -Name 'UnrealEditor*','UnrealBuildTool' -ErrorAction SilentlyContinue).Count){throw 'Root sequential capture requires no live UE/UBT.'}
& $python -B -X utf8 $checker --snapshot-manifest $SnapshotManifest --expected-profile $ExpectedProfile --preflight
if($LASTEXITCODE -ne 0){throw 'Current Source/DLL/snapshot/measured profile/oldProbe-tool pins preflight failed before native launch.'}
$manifest=Get-Content -LiteralPath $SnapshotManifest -Raw|ConvertFrom-Json
function Check-TaskPins{
 foreach($row in $manifest.files){$path=Join-Path $workspace $row.path;if((Get-Item -LiteralPath $path).Length -ne $row.bytes -or (Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash.ToLowerInvariant() -cne $row.sha256){throw "Actual compiled input changed: $($row.path)"}}
}
if([string]::IsNullOrWhiteSpace($ArchiveRoot)){$ArchiveRoot=Join-Path $workspace ('过程图稿与视频\'+(Get-Date -Format 'yyyy-MM-dd_HHmmss')+'_棕皮军剑真实行走_'+$Version)}
$ArchiveRoot=[IO.Path]::GetFullPath($ArchiveRoot)
if(Test-Path -LiteralPath $ArchiveRoot){throw 'Use a fresh archive; never overwrite previous originals or failed proof.'}
$original=Join-Path $ArchiveRoot '原件';[IO.Directory]::CreateDirectory($original)|Out-Null;[IO.Directory]::CreateDirectory((Join-Path $ArchiveRoot '展示副本'))|Out-Null
$index=[ordered]@{schema='walk-native-proof-capture-v1';status='started';snapshot_manifest=$SnapshotManifest;snapshot_manifest_sha256=(Get-FileHash -LiteralPath $SnapshotManifest -Algorithm SHA256).Hash.ToLowerInvariant();expected_profile=$ExpectedProfile;expected_profile_sha256=(Get-FileHash -LiteralPath $ExpectedProfile -Algorithm SHA256).Hash.ToLowerInvariant();process_id=$null;exit_code=$null;actual_native_verified=$false;wall_stop_visually_recorded=$false;art_accepted=$false;formal_complete_units=0}
$indexPath=Join-Path $ArchiveRoot 'index.json'
function Write-TaskIndex{[IO.File]::WriteAllText($indexPath,($index|ConvertTo-Json -Depth 8),[Text.UTF8Encoding]::new($false))}
Write-TaskIndex
$arguments=@(('"{0}"' -f (Join-Path $workspace 'UnrealGame\CodexDungeon.uproject')),'/Game/Maps/FirstRoom','-game','-windowed','-ResX=1280','-ResY=720','-NoSplash','-NoLiveCoding','-nop4','-unattended',
 '-DungeonSceneExplorationPreview','-DungeonCandidateSprites','-DungeonFairytaleSwordBodyPreview','-DungeonFairytaleSwordBodyV002Preview','-DungeonFairytaleSwordArmorPrimary1Preview','-DungeonFairytaleSwordPrimary2Preview','-DungeonFairytaleSwordPrimary2BodyPreview','-DungeonFairytaleSwordPrimary2ArmorPreview','-DungeonFairytaleSwordPrimary3ArmorPreview',
 '-DungeonFairytaleLeatherReadyPreview','-DungeonFairytaleLeatherPrimary1Preview','-DungeonFairytaleLeatherPrimary2Preview','-DungeonFairytaleLeatherPrimary3Preview','-DungeonFairytaleSwordEquipmentBoundPreview','-DungeonFairytaleSwordWalkPreview','-DungeonFairytaleWalkProof',
 '-DungeonContentProof','-DungeonFastLosslessCapture','-DungeonAsyncLosslessCapture',('-DungeonContentProofDir="{0}"' -f $original),'-ExecCmds="t.MaxFPS 30,r.ScreenshotDelegate 1"',('-abslog="{0}"' -f (Join-Path $ArchiveRoot 'runtime.log')))
try{
 Check-TaskPins
 $process=Start-Process -FilePath (Join-Path $EngineRoot 'Engine\Binaries\Win64\UnrealEditor.exe') -ArgumentList $arguments -WindowStyle Hidden -PassThru
 $index.process_id=$process.Id;$index['arguments']=$arguments;Write-TaskIndex;Write-Output "Native Walk PID $($process.Id); original frames $original"
 $deadline=[DateTime]::UtcNow.AddSeconds(120)
 while(-not $process.WaitForExit(30000)){if([DateTime]::UtcNow -ge $deadline){Stop-Process -Id $process.Id -Force;throw 'Owned Walk capture timed out; native log/partial originals preserved.'};Write-Output "Owned Walk PID $($process.Id) still active; no second UE started."}
 $process.Refresh();$index.exit_code=$process.ExitCode;Write-TaskIndex
 if($process.ExitCode -ne 0){throw "Native Walk failed with exit $($process.ExitCode); preserve all originals and use a new archive for retry."}
 Check-TaskPins
 $verificationLog=Join-Path $ArchiveRoot 'independent-verification-output.txt'
 & $python -B -X utf8 $checker --snapshot-manifest $SnapshotManifest --expected-profile $ExpectedProfile --original $original --write-receipt *> $verificationLog
 $verificationExit=$LASTEXITCODE;Get-Content -LiteralPath $verificationLog|Write-Output
 if($verificationExit -ne 0){throw 'Independent motion/phase/instance/Renderedstack/Jchain/native CRC verification failed; outputs preserved.'}
 $index.actual_native_verified=$true;$index.status='native_core_passed_visual_review_wall_stop_art_audio_pending';Write-TaskIndex
}catch{$index.status='failed_preserved';$index['failure']=$_.Exception.Message;Write-TaskIndex;throw}
Write-Output $ArchiveRoot
