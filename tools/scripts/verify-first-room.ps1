param(
    [string]$EngineRoot = 'G:\UE_5.5',
    [string]$Version = 'v001'
)
$ErrorActionPreference = 'Stop'
$workspace = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\..'))
$project = Join-Path $workspace 'UnrealGame\CodexDungeon.uproject'
$archive = Join-Path $workspace ("过程图稿与视频\{0}_首个2.5D战斗房间_{1}" -f (Get-Date -Format 'yyyy-MM-dd'),$Version)
if (Test-Path -LiteralPath $archive) { throw "Keep earlier versions. Choose a fresh Version: $archive" }
$original = Join-Path $archive '原件'
$presentation = Join-Path $archive '展示副本'
New-Item -ItemType Directory -Path $original,$presentation | Out-Null
$index = [ordered]@{date=(Get-Date -Format o);version=$Version;status='capturing';source=$project;map='/Game/Maps/FirstRoom';scope='Live UE viewport frames with fixed 30 FPS simulation; automated gameplay through runtime methods, not realtime performance measurement';paid_generation_cost=0}
$index | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $archive 'index.json') -Encoding utf8
$log = Join-Path $archive 'runtime.log'
$arguments = @(('"{0}"' -f $project),'/Game/Maps/FirstRoom','-game','-windowed','-ResX=1280','-ResY=720','-NoSplash','-NoLiveCoding','-nop4','-unattended','-DungeonProof',('-DungeonProofDir="{0}"' -f $original),'-DUMPMOVIE','-UseFixedTimeStep','-FPS=30','-SECONDS=19',('-abslog="{0}"' -f $log))
$process = Start-Process -FilePath (Join-Path $EngineRoot 'Engine\Binaries\Win64\UnrealEditor.exe') -ArgumentList $arguments -WindowStyle Hidden -PassThru
Write-Output "Graphical first-room proof PID $($process.Id), archive $archive"
$process.WaitForExit()
$code = $process.ExitCode
$frames = @(Get-ChildItem -LiteralPath $original -Filter 'MovieFrame*.png' | Sort-Object Name)
$index['exit_code'] = $code
$index['frame_count'] = $frames.Count
$reportPath = Join-Path $original 'runtime-report.json'
$validReport = $false
if (Test-Path -LiteralPath $reportPath) {
    $runtime = Get-Content -LiteralPath $reportPath -Raw | ConvertFrom-Json
    $validReport = $runtime.passed -eq $true -and $runtime.demo_room_cleared -eq $true
}
$success = $code -eq 0 -and $frames.Count -gt 500 -and $validReport
$index['runtime_checks_passed'] = $validReport
$index['status'] = if ($success) { 'captured_pending_review' } else { 'failed_preserved' }
$index | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $archive 'index.json') -Encoding utf8
Write-Output "Graphical proof exit $code, frames $($frames.Count)"
if ($frames.Count -gt 30) {
    $ffmpeg = Join-Path $workspace 'tools\runtime\asset-gen\Lib\site-packages\imageio_ffmpeg\binaries\ffmpeg-win-x86_64-v7.1.exe'
    $list = Join-Path $archive 'frames.txt'
    $lines = @()
    foreach ($frame in $frames) {
        $escaped = $frame.FullName.Replace('\','/').Replace("'", "'\''")
        $lines += "file '$escaped'"
        $lines += 'duration 0.0333333333'
    }
    [IO.File]::WriteAllLines($list,$lines,[Text.UTF8Encoding]::new($false))
    $movie = Join-Path $presentation 'first-room-proof.mp4'
    & $ffmpeg -hide_banner -loglevel error -f concat -safe 0 -i $list -vf fps=30 -c:v libx264 -crf 20 -pix_fmt yuv420p -movflags +faststart $movie
    if ($LASTEXITCODE -ne 0) { throw 'FFmpeg encoding failed; originals preserved' }
    $mid = $frames[[Math]::Floor($frames.Count * 0.5)]
    Copy-Item -LiteralPath $mid.FullName -Destination (Join-Path $presentation 'gameplay.png')
    $report = Join-Path $original 'runtime-report.json'
    if (Test-Path -LiteralPath $report) { Copy-Item -LiteralPath $report -Destination (Join-Path $archive 'runtime-report.json') }
    Write-Output "Proof movie: $movie"
}
if (-not $success) { Write-Error 'Proof verification failed: require exit 0, over 500 frames, and a passing runtime report with cleared room.' -ErrorAction Continue; exit 1 }
exit 0
