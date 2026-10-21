param(
    [string]$EngineRoot='G:\UE_5.5',
    [int]$Version=2,
    [int]$ProcessTimeoutSeconds=120,
    [string]$InspectArchive=''
)
$ErrorActionPreference='Stop'
$workspace=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\..'))
$python=Join-Path $workspace 'tools\runtime\asset-gen\Scripts\python.exe'
$checker=Join-Path $PSScriptRoot 'verify-fairytale-limb-lookdev-v002.py'
$manifest=Join-Path $workspace 'source-assets\production\fairytale-limb-lookdev-v002\manifests\import-limb-lookdev-v002.json'
if($InspectArchive){
    & $python -X utf8 -B $checker --archive ([IO.Path]::GetFullPath($InspectArchive)) --manifest $manifest
    if($LASTEXITCODE -ne 0){throw 'Read-only lookdev inspection failed.'}
    return
}
if($Version -lt 1 -or $ProcessTimeoutSeconds -lt 30){throw 'Invalid version/timeout.'}
$project=Join-Path $workspace 'UnrealGame\CodexDungeon.uproject'
$engine=Join-Path $EngineRoot 'Engine\Binaries\Win64\UnrealEditor.exe'
$ffmpeg=Join-Path $workspace 'tools\runtime\asset-gen\Lib\site-packages\imageio_ffmpeg\binaries\ffmpeg-win-x86_64-v7.1.exe'
foreach($path in @($python,$checker,$manifest,$project,$engine,$ffmpeg)){
    if(-not(Test-Path -LiteralPath $path -PathType Leaf)){throw "Missing lookdev dependency: $path"}
}
# Exclusive UE process; never borrow an editor or operate a concurrent capture.
if(@(Get-Process -Name 'UnrealEditor*','UnrealBuildTool' -ErrorAction SilentlyContinue).Count){throw 'Close the existing UE process before this isolated capture.'}
& $python -B -X utf8 $checker --preflight-only --manifest $manifest
if($LASTEXITCODE -ne 0){throw 'Source/native-package preflight failed; capture was not started.'}
$assetManifest=Get-Content -LiteralPath $manifest -Raw | ConvertFrom-Json
if($assetManifest.schema -ne 'frozen-fairytale-near-limb-lookdev-eight-v2' -or @($assetManifest.assets).Count -ne 8){throw 'Eight-source manifest required.'}
foreach($asset in $assetManifest.assets){
    $relative=([string]$asset.package_path).Substring('/Game/'.Length)+'.uasset'
    if(-not(Test-Path -LiteralPath (Join-Path $workspace ('UnrealGame\Content\'+$relative)) -PathType Leaf)){
        throw "Import the frozen new Texture2D packages first: $($asset.package_path)"
    }
}
$topic=(Get-Date -Format 'yyyy-MM-dd')+'_暗黑童话护腕护胫明暗双向真实观察_v'+$Version.ToString('000')
$archive=Join-Path $workspace ('过程图稿与视频\'+$topic)
if(Test-Path -LiteralPath $archive){throw 'Never overwrite prior lookdev evidence; choose an unused version.'}
$original=Join-Path $archive '原件'
$presentation=Join-Path $archive '展示副本'
[IO.Directory]::CreateDirectory($original)|Out-Null
[IO.Directory]::CreateDirectory($presentation)|Out-Null
$index=[ordered]@{
    date=(Get-Date -Format 'yyyy-MM-dd');version=$Version;status='capture_started';
    project=$project;profile='fairytale_near_limb_observation_silent_v001';
    scope='Eight real near-bracer/shin sources over fixed131/147/149/150 baseline: sixteen1.5s bright/dark/facing/both-on-off/isolated-limb combinations, fixed72px presentation and inert gameplay inputs. No actual gameplay equipping, combat or complete armor.';
    silent_video=$true;audio_recorded=$false;microphone_capture=$false;offline_audio_substitution=$false;
    motion_reviewed=$false;new_style_accepted=$false;formal_complete_units=0;
    manifest_sha256=(Get-FileHash -LiteralPath $manifest -Algorithm SHA256).Hash;
    capture_script_sha256=(Get-FileHash -LiteralPath $PSCommandPath -Algorithm SHA256).Hash;
    verifier_sha256=(Get-FileHash -LiteralPath $checker -Algorithm SHA256).Hash;
    module_sha256=(Get-FileHash -LiteralPath (Join-Path $workspace 'UnrealGame\Binaries\Win64\UnrealEditor-CodexDungeon.dll') -Algorithm SHA256).Hash
}
$sources=[ordered]@{}
foreach($source in Get-ChildItem -LiteralPath (Join-Path $workspace 'UnrealGame\Source\CodexDungeon') -File -Recurse){
    $sources[$source.FullName.Substring($workspace.Length+1)]=(Get-FileHash -LiteralPath $source.FullName -Algorithm SHA256).Hash
}
$index['source_sha256_at_capture']=$sources
$indexPath=Join-Path $archive 'index.json'
$index | ConvertTo-Json -Depth 12 | Set-Content -LiteralPath $indexPath -Encoding utf8
try {
    # DungeonContentProof/Dir solely installs the unchanged native helper.
    # The new HUD branch never creates ADungeonContentProbe or old fixtures.
    $arguments=@(('"{0}"' -f $project),'/Game/Maps/FirstRoom','-game','-windowed','-ResX=1280','-ResY=720',
        '-NoSplash','-NoLiveCoding','-nop4','-unattended','-DungeonFairytaleLookdevPreview','-DungeonFairytaleLookdevProof','-DungeonFairytaleChestLookdev','-DungeonFairytaleShoulderLookdev','-DungeonFairytaleLimbLookdev',
        '-DungeonContentProof','-DungeonFastLosslessCapture','-DungeonAsyncLosslessCapture',
        ('-DungeonContentProofDir="{0}"' -f $original),'-ExecCmds="t.MaxFPS 30,r.ScreenshotDelegate 1"',
        ('-abslog="{0}"' -f (Join-Path $archive 'runtime.log')))
    $process=Start-Process -FilePath $engine -ArgumentList $arguments -WindowStyle Hidden -PassThru
    Write-Output "Silent lookdev PID $($process.Id), archive $archive"
    if(-not $process.WaitForExit($ProcessTimeoutSeconds*1000)){
        Stop-Process -Id $process.Id -Force
        throw 'Lookdev capture timed out; interrupted originals preserved.'
    }
    $process.Refresh();$index['exit_code']=$process.ExitCode
    if($process.ExitCode -ne 0){throw 'UE process failed; original evidence preserved.'}
    $auditText=@(& $python -X utf8 -B $checker --archive $archive --manifest $manifest 2>&1)
    if($LASTEXITCODE -ne 0){throw ('Lookdev/native validation failed: '+($auditText -join ' '))}
    $audit=($auditText -join "`n") | ConvertFrom-Json
    $audit | ConvertTo-Json -Depth 12 | Set-Content -LiteralPath (Join-Path $original 'lookdev-verification.json') -Encoding utf8
    $index['verification']=$audit
    $report=Get-Content -LiteralPath (Join-Path $original 'runtime-report.json') -Raw | ConvertFrom-Json
    $frames=@(Get-ChildItem -LiteralPath $original -Filter 'MovieFrame*.png' -File | Sort-Object Name)
    $offsets=@($report.capture_timing.frame_wall_offsets_s)
    $duration=[double]$report.capture_timing.requested_video_wall_duration_s
    $list=Join-Path $archive 'frames.txt'
    $lines=[Collections.Generic.List[string]]::new()
    $culture=[Globalization.CultureInfo]::InvariantCulture
    for($i=0;$i -lt $frames.Count;$i++){
        $start=if($i -eq 0){0.0}else{[double]$offsets[$i]}
        $next=if($i+1 -lt $frames.Count){[double]$offsets[$i+1]}else{$duration}
        $lines.Add("file '"+$frames[$i].FullName.Replace('\','/').Replace("'","'\''")+"'")
        $lines.Add('duration '+($next-$start).ToString('F9',$culture))
    }
    $lines.Add("file '"+$frames[-1].FullName.Replace('\','/').Replace("'","'\''")+"'")
    [IO.File]::WriteAllLines($list,$lines,[Text.UTF8Encoding]::new($false))
    $video=Join-Path $presentation 'fairytale-limb-lookdev-silent.mp4'
    $videoFrames=[int][Math]::Ceiling($duration*30)
    & $ffmpeg -nostdin -hide_banner -loglevel error -n -f concat -safe 0 -i $list -map 0:v:0 -an -vf fps=30 -frames:v $videoFrames -c:v libx264 -crf 18 -pix_fmt yuv420p -movflags +faststart $video
    if($LASTEXITCODE -ne 0){throw 'Silent MP4 encoding failed; originals preserved.'}
    $decodeLog=@(& $ffmpeg -nostdin -hide_banner -loglevel info -i $video -map 0:v:0 -an -f null - 2>&1)
    $audioStreamDeclaration='(?im)^\s*Stream\s+#\d+:\d+(?:\[[^\]\r\n]*\])?(?:\([^\)\r\n]*\))?\s*:\s*Audio\s*:'
    if($LASTEXITCODE -ne 0 -or ($decodeLog -join "`n") -match $audioStreamDeclaration){throw 'Full video decode failed or unexpected audio stream appeared.'}
    $index['frame_count']=$frames.Count
    $index['presentation_video_frames_target']=$videoFrames
    $index['presentation_sha256']=(Get-FileHash -LiteralPath $video -Algorithm SHA256).Hash
    $index['complete_video_decode']=$true
    $index['presentation_audio_stream']=$false
    $index['presentation_timing']='Actual monotonic original frame intervals resampled to30fps; no generated intermediate artwork, retiming of source rows, or audio track.'
    $index['status']='captured_pending_visual_motion_review'
} catch {
    $index['status']='failed_preserved'
    $index['failure']=$_.Exception.Message
    throw
} finally {
    $index | ConvertTo-Json -Depth 12 | Set-Content -LiteralPath $indexPath -Encoding utf8
}
Write-Output ("Preserved silent lookdev: "+$archive)
