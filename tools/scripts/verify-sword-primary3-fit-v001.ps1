param(
    [string]$EngineRoot='G:\UE_5.5',
    [ValidateRange(1,999)][int]$Version=1,
    [string]$Snapshot='source-assets/production/backups/2026-10-16_Primary3Armor48-fit-full141GREEN-v116'
)
$ErrorActionPreference='Stop'
$workspace=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\..'))
$python=Join-Path $workspace 'tools\runtime\asset-gen\Scripts\python.exe'
$checker=Join-Path $PSScriptRoot 'verify-sword-primary3-fit-v001.py'
if(@(Get-Process -Name 'UnrealEditor*','UnrealBuildTool' -ErrorAction SilentlyContinue).Count){throw 'Sequential capture requires no existing UE/UBT.'}
& $python -B -X utf8 $checker --preflight-only --snapshot $Snapshot
if($LASTEXITCODE -ne 0){throw 'Imported-source/full141 immutable snapshot preflight failed.'}
$topic=(Get-Date -Format 'yyyy-MM-dd')+'_钟盔军剑三段真实连击试装_v'+$Version.ToString('000')
$archive=Join-Path $workspace ('过程图稿与视频\'+$topic)
if(Test-Path -LiteralPath $archive){throw 'Choose an unused version; preserve prior evidence.'}
$original=Join-Path $archive '原件'
$presentation=Join-Path $archive '展示副本'
[IO.Directory]::CreateDirectory($original)|Out-Null
[IO.Directory]::CreateDirectory($presentation)|Out-Null
$index=[ordered]@{
    status='capture_started';profile='fairytale_sword_normal_input_v001';formal_complete_units=0;audio_recorded=$false;
    scope='Native175 Primary3 body with48 source/body/armor textures from176/177/178, existing Ready/P1/P2 armor retained. Real sixJ/grounded three-stage kernel candidates; no hit/grasp/footlock/fullmotion/audio acceptance.';
    snapshot=$Snapshot;observations=$null;capture_duration_s=$null;
    module_sha256=(Get-FileHash -LiteralPath (Join-Path $workspace 'UnrealGame\Binaries\Win64\UnrealEditor-CodexDungeon.dll') -Algorithm SHA256).Hash
}
$sources=[ordered]@{}
foreach($source in Get-ChildItem -LiteralPath (Join-Path $workspace 'UnrealGame\Source\CodexDungeon') -Recurse -File){$sources[$source.FullName.Substring($workspace.Length+1)]=(Get-FileHash -LiteralPath $source.FullName -Algorithm SHA256).Hash}
$index['source_sha256_at_capture']=$sources
$indexPath=Join-Path $archive 'index.json'
$index | ConvertTo-Json -Depth 9 | Set-Content -LiteralPath $indexPath -Encoding utf8
$project=Join-Path $workspace 'UnrealGame\CodexDungeon.uproject'
$argsList=@(('"{0}"' -f $project),'/Game/Maps/FirstRoom','-game','-windowed','-ResX=1280','-ResY=720','-NoSplash','-NoLiveCoding','-nop4','-unattended','-DungeonSceneExplorationPreview','-DungeonCandidateSprites','-DungeonFairytaleSwordBodyPreview','-DungeonFairytaleSwordBodyV002Preview','-DungeonFairytaleSwordArmorPrimary1Preview','-DungeonFairytaleSwordPrimary2Preview','-DungeonFairytaleSwordPrimary2ArcPreview','-DungeonFairytaleSwordPrimary2BodyPreview','-DungeonFairytaleSwordPrimary2ArmorPreview','-DungeonFairytaleSwordPrimary3ArmorPreview','-DungeonFairytaleSwordBodyProof','-DungeonContentProof','-DungeonFastLosslessCapture','-DungeonAsyncLosslessCapture',('-DungeonContentProofDir="{0}"' -f $original),'-ExecCmds="t.MaxFPS 30,r.ScreenshotDelegate 1"',('-abslog="{0}"' -f (Join-Path $archive 'runtime.log')))
try{
    $process=Start-Process -FilePath (Join-Path $EngineRoot 'Engine\Binaries\Win64\UnrealEditor.exe') -ArgumentList $argsList -WindowStyle Hidden -PassThru
    $index['process_id']=$process.Id
    Write-Output "Normal-input three-stage capture PID $($process.Id), archive $archive"
    if(-not $process.WaitForExit(240000)){Stop-Process -Id $process.Id -Force;throw 'Capture timeout; interrupted originals retained.'}
    $process.Refresh();$index['exit_code']=$process.ExitCode
    if($process.ExitCode -ne 0){throw 'Capture process failed; original evidence retained.'}
    & $python -B -X utf8 (Join-Path $PSScriptRoot 'verify-native-sword-capture-pixels.py') --archive $archive --write-receipt
    if($LASTEXITCODE -ne 0){throw 'Original native BGRA CRC/FIFO/flush verification failed.'}
    & $python -B -X utf8 $checker --archive $archive --snapshot $Snapshot
    if($LASTEXITCODE -ne 0){throw 'Three-stage source/stack/phase/pending/exact-transition verification failed.'}
    & $python -B -X utf8 (Join-Path $PSScriptRoot 'verify-ready-primary3-body-pixel-presence-v001.py') --archive $archive
    if($LASTEXITCODE -ne 0){throw 'Unrelaxed bounded warm-head signal failed; originals retained.'}
    $report=Get-Content -LiteralPath (Join-Path $original 'runtime-report.json') -Raw|ConvertFrom-Json
    $index['observations']=@($report.observations).Count
    $index['capture_duration_s']=$report.capture_timing.requested_video_wall_duration_s
    $index['status']='native_pixels_real_three_stage_input_and_bounded_head_signal_passed_art_review_pending'
}catch{
    $index['status']='failed_preserved';$index['failure']=$_.Exception.Message
    $index | ConvertTo-Json -Depth 9 | Set-Content -LiteralPath $indexPath -Encoding utf8
    throw
}
$index | ConvertTo-Json -Depth 9 | Set-Content -LiteralPath $indexPath -Encoding utf8
Write-Output $archive
