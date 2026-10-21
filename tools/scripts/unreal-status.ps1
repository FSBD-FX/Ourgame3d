$ErrorActionPreference = 'Stop'
$workspace = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\..'))
$project = Join-Path $workspace 'UnrealGame\CodexDungeon.uproject'
$saved = Join-Path $workspace 'UnrealGame\Saved\Bootstrap'
$processes = @(Get-CimInstance Win32_Process | Where-Object { $_.Name -in @('UnrealEditor.exe','UnrealEditor-Cmd.exe') -and $_.CommandLine -and $_.CommandLine.Contains($project) } | Select-Object Name,ProcessId,CommandLine)
$port = @(Get-NetTCPConnection -LocalPort 55557 -State Listen -ErrorAction SilentlyContinue | Select-Object LocalAddress,LocalPort,OwningProcess)
$summary = [ordered]@{
    project = $project
    processes = $processes
    mcpListener = $port
    moduleExists = Test-Path -LiteralPath (Join-Path $workspace 'UnrealGame\Binaries\Win64\UnrealEditor-CodexDungeon.dll')
    pluginExists = Test-Path -LiteralPath (Join-Path $workspace 'UnrealGame\Plugins\UnrealMCP\Binaries\Win64\UnrealEditor-UnrealMCP.dll')
    foundationMapExists = Test-Path -LiteralPath (Join-Path $workspace 'UnrealGame\Content\Maps\Foundation.umap')
    assetValidationMapExists = Test-Path -LiteralPath (Join-Path $workspace 'UnrealGame\Content\Tests\Preparation\AssetIntake.umap')
}
foreach ($name in @('last-build.json','foundation-report.json','last-editor-start.json')) {
    $file = Join-Path $saved $name
    $summary[$name] = if (Test-Path -LiteralPath $file) { Get-Content -LiteralPath $file -Raw | ConvertFrom-Json } else { $null }
}
$importFile = Join-Path $saved 'asset-import-report.json'
if (Test-Path -LiteralPath $importFile) {
    $intake = Get-Content -LiteralPath $importFile -Raw | ConvertFrom-Json
    $summary['assetImport'] = [ordered]@{run=$intake.run_id_utc;status=$intake.status;currentlyImporting=$intake.currently_importing;summary=$intake.summary}
}
$playFile = Join-Path $saved 'pie-report.json'
if (Test-Path -LiteralPath $playFile) {
    $play = Get-Content -LiteralPath $playFile -Raw | ConvertFrom-Json
    $summary['playInEditor'] = [ordered]@{run=$play.run_id_utc;status=$play.status;editorPid=$play.editor_pid;map=$play.map;observedPlaySeconds=$play.observed_play_seconds;stopped=$play.is_in_play_in_editor_after_stop -eq $false;screenshotPath=$play.screenshot_path;screenshotExists=Test-Path -LiteralPath $play.screenshot_path}
}
$summary | ConvertTo-Json -Depth 7
