param(
    [string]$ArchiveDirectory = '',
    [string]$FFmpeg = ''
)
$ErrorActionPreference = 'Stop'
$workspace = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\..'))
if (-not $ArchiveDirectory) { $ArchiveDirectory = Join-Path $workspace ('过程图稿与视频\{0}_UE55实跑采样_v001' -f (Get-Date -Format 'yyyy-MM-dd')) }
if (-not $FFmpeg) { $FFmpeg = Join-Path $workspace 'tools\runtime\asset-gen\Lib\site-packages\imageio_ffmpeg\binaries\ffmpeg-win-x86_64-v7.1.exe' }
$saved = Join-Path $workspace 'UnrealGame\Saved\Bootstrap'
$report = Get-Content -LiteralPath (Join-Path $saved 'pie-report.json') -Raw | ConvertFrom-Json
if ($report.status -ne 'passed' -or -not $report.capture_complete -or $report.sample_frames.Count -ne 6) { throw 'Six completed real PIE sample frames are required.' }
if (Test-Path -LiteralPath $ArchiveDirectory) { throw 'Choose a new archive version; existing versions are never overwritten.' }
if (-not (Test-Path -LiteralPath $FFmpeg)) { throw 'The existing local FFmpeg executable was not found.' }
$originals = Join-Path $ArchiveDirectory '原件'
$presentation = Join-Path $ArchiveDirectory '展示副本'
$originalFrames = Join-Path $originals 'frames'
$presentationFrames = Join-Path $presentation 'frames'
$decode = Join-Path $presentation '解码检查'
New-Item -ItemType Directory -Path $originalFrames,$presentationFrames,$decode -Force | Out-Null
foreach ($frame in $report.sample_frames) {
    if (-not (Test-Path -LiteralPath $frame.path) -or (Get-Item -LiteralPath $frame.path).Length -eq 0) { throw "Missing engine frame: $($frame.path)" }
    Copy-Item -LiteralPath $frame.path -Destination $originalFrames
    Copy-Item -LiteralPath $frame.path -Destination $presentationFrames
}
foreach ($name in @('pie-report.json','character-axis-repair-report.json','asset-import-report.json','asset-validation-map-report.json','font-import-report.json')) {
    Copy-Item -LiteralPath (Join-Path $saved $name) -Destination $originals
}
$frameDirectory = Split-Path -Path $report.sample_frames[0].path -Parent
$video = Join-Path $frameDirectory 'asset-intake-low-fps-pie-samples.mp4'
if (Test-Path -LiteralPath $video) { throw 'The source video already exists; keep it and choose a new source run.' }
& $FFmpeg -hide_banner -loglevel error -framerate 1 -start_number 0 -i (Join-Path $originalFrames 'frame-%03d.png') -t 6 -c:v libx264 -pix_fmt yuv420p -r 30 -movflags +faststart -metadata 'title=UE 5.5 asset intake - low frame rate PIE samples' -metadata 'comment=Six actual PIE samples at approximately 1 FPS, held for 1 second each. No realtime gameplay claim. Actual engine timestamps preserved in pie-report.json.' $video
if ($LASTEXITCODE -ne 0) { throw "FFmpeg encoding failed: $LASTEXITCODE" }
Copy-Item -LiteralPath $video -Destination $originals
Copy-Item -LiteralPath $video -Destination $presentation
foreach ($sample in @(@{Time=0;Name='start.png'},@{Time=3;Name='middle.png'},@{Time=5;Name='end.png'})) {
    & $FFmpeg -hide_banner -loglevel error -ss $sample.Time -i $video -frames:v 1 -update 1 (Join-Path $decode $sample.Name)
    if ($LASTEXITCODE -ne 0) { throw "FFmpeg decode check failed: $LASTEXITCODE" }
}
$index = [ordered]@{
    version='v004'; utc=(Get-Date).ToUniversalTime().ToString('O'); status='Archived; pending first/middle/last visual review'
    source='Real UE 5.5.4 D3D11 PIE /Game/Tests/Preparation/AssetIntake'; sourceRun=$report.run_id_utc
    sourceEditorPid=$report.editor_pid; sourceFrameDirectory=$frameDirectory; sourceVideo=$video
    scope='Infrastructure and imported asset/material/idle verification only; no gameplay, audio audition, real-time recording or player-input claim.'
    sampleRequestsInPIESeconds=@($report.sample_frames | ForEach-Object {$_.request_play_seconds})
    sampleSavedObservationsInPIESeconds=@($report.sample_frames | ForEach-Object {$_.save_observed_play_seconds})
    sourceObservedPlaySeconds=$report.observed_play_seconds
    video='展示副本/asset-intake-low-fps-pie-samples.mp4'; videoPresentationSeconds=6; encoding='H264 1280x720 30 FPS with held 1 FPS source frames'
    originals='原件/'; presentation='展示副本/'; timestamps='原件/pie-report.json'; decodeChecks='展示副本/解码检查/'
}
$index | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath (Join-Path $ArchiveDirectory 'index.json') -Encoding utf8
Get-ChildItem -LiteralPath $ArchiveDirectory -File -Recurse | Get-FileHash -Algorithm SHA256 | Select-Object Path,Hash | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $ArchiveDirectory 'sha256-manifest.json') -Encoding utf8
Write-Output "Archived proof: $ArchiveDirectory"
Write-Output "Low frame rate sampled video: $(Join-Path $presentation 'asset-intake-low-fps-pie-samples.mp4')"
