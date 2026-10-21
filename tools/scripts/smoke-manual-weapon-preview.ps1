param([string]$EngineRoot='G:\UE_5.5',[ValidatePattern('^v[0-9]+$')][string]$Version='v002')
$ErrorActionPreference='Stop'
$workspace=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\..'))
$project=Join-Path $workspace 'UnrealGame\CodexDungeon.uproject'
$archive=Join-Path $workspace ('过程图稿与视频\2026-10-15_手动猎弩入口启动运行_'+$Version)
if(Test-Path -LiteralPath $archive){throw 'Preserve the existing startup evidence; use a new version.'}
$existing=@(Get-CimInstance Win32_Process -Filter "Name='UnrealEditor.exe' OR Name='UnrealEditor-Cmd.exe'" | Where-Object {$_.CommandLine -and $_.CommandLine.Contains($project)})
if($existing.Count){throw 'Close this project before the isolated startup smoke.'}
$original=Join-Path $archive '原件'
$presentation=Join-Path $archive '展示副本'
New-Item -ItemType Directory -Path $original,$presentation | Out-Null
$screens=Join-Path $workspace 'UnrealGame\Saved\Screenshots'
$before=@(Get-ChildItem -LiteralPath $screens -Recurse -File -Filter '*.png' -ErrorAction SilentlyContinue | ForEach-Object {$_.FullName})
$arguments=@(('"{0}"' -f $project),'/Game/Maps/FirstRoom','-game','-windowed','-ResX=1280','-ResY=720','-NoSplash','-NoLiveCoding','-nop4','-unattended',
    '-DungeonCandidateSprites','-DungeonWeaponBodyPreview','-DungeonXBWPrimaryBodyPreview','-DungeonXBWReloadBodyPreview','-DungeonManualWeaponPreview',
    '-ExecCmds="GetAll DungeonGameMode bWaitingForStart,GetAll DungeonGameMode LastMessage,GetAll DungeonFighter WeaponId,Shot"',
    ('-abslog="{0}"' -f (Join-Path $original 'runtime.log')))
$receipt=[ordered]@{scope='Isolated actual CLI manual-startup and native viewport only; no automatic E/J/R input or full combat/save acceptance';project=$project;arguments=$arguments;started_utc=(Get-Date).ToUniversalTime().ToString('O');screenshot_received=$false;status='running';microphone_capture=$false}
$process=Start-Process -FilePath (Join-Path $EngineRoot 'Engine\Binaries\Win64\UnrealEditor.exe') -ArgumentList $arguments -WindowStyle Hidden -PassThru
$receipt.pid=$process.Id
Write-Output "Isolated manual startup PID $($process.Id)"
try {
    $deadline=(Get-Date).AddSeconds(55)
    do {
        Start-Sleep -Milliseconds 500
        $new=@(Get-ChildItem -LiteralPath $screens -Recurse -File -Filter '*.png' -ErrorAction SilentlyContinue | Where-Object {$_.FullName -notin $before} | Sort-Object LastWriteTimeUtc -Descending)
        if($new.Count){
            Start-Sleep -Milliseconds 500
            $source=$new[0].FullName
            Copy-Item -LiteralPath $source -Destination (Join-Path $original 'manual-startup-native.png')
            Copy-Item -LiteralPath $source -Destination (Join-Path $presentation 'manual-startup.png')
            $receipt.screenshot_received=$true;$receipt.source_screenshot=$source
            $receipt.screenshot_sha256=(Get-FileHash -LiteralPath $source -Algorithm SHA256).Hash
            $receipt.status='native_startup_captured_pending_review'
            break
        }
        $process.Refresh()
    } while(-not $process.HasExited -and (Get-Date) -lt $deadline)
    if(-not $receipt.screenshot_received){throw 'Actual startup screenshot was not received.'}
} finally {
    $process.Refresh()
    if(-not $process.HasExited){
        $owned=Get-CimInstance Win32_Process -Filter ("ProcessId={0}" -f $process.Id)
        if(-not $owned.CommandLine -or -not $owned.CommandLine.Contains($project) -or -not $owned.CommandLine.Contains('-DungeonManualWeaponPreview')){throw 'Refuse to close a process whose task ownership is not verified.'}
        Stop-Process -Id $process.Id
        $process.WaitForExit()
    }
    $receipt.stopped_owned_isolated_process=$true
    $receipt | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath (Join-Path $archive 'index.json') -Encoding utf8
}
$receipt | ConvertTo-Json -Depth 6
