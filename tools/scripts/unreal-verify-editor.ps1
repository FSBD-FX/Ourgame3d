param([string]$EngineRoot = 'G:\UE_5.5', [switch]$RepairCharacterAnimations, [switch]$CharacterAxisDiagnostic, [switch]$RepairCharacterAxis)
$ErrorActionPreference = 'Stop'
$workspace = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\..'))
$project = Join-Path $workspace 'UnrealGame\CodexDungeon.uproject'
$existing = @(Get-CimInstance Win32_Process -Filter "Name='UnrealEditor.exe' OR Name='UnrealEditor-Cmd.exe'" | Where-Object { $_.CommandLine -and $_.CommandLine.Contains($project) })
if ($existing.Count -gt 0) { throw "Close this project's existing editor before verification: $($existing.ProcessId -join ', ')" }
$logs = Join-Path $workspace 'UnrealGame\Saved\Bootstrap'
New-Item -ItemType Directory -Path $logs -Force | Out-Null
$log = Join-Path $logs ('editor-verification-{0}.log' -f (Get-Date -Format 'yyyyMMdd-HHmmss'))
$editor = Join-Path $EngineRoot 'Engine\Binaries\Win64\UnrealEditor.exe'
$script = Join-Path $PSScriptRoot 'unreal-verify-editor.py'
$arguments = @(('"{0}"' -f $project), '-NoSplash', '-NoLiveCoding', '-nop4', '-unattended', ('-abslog="{0}"' -f $log), ('-ExecutePythonScript="{0}"' -f $script))
$oldReplace = $env:CODEX_ASSET_IMPORT_REPLACE
$oldOnly = $env:CODEX_ASSET_IMPORT_ONLY
$oldDiagnostic = $env:CODEX_CHARACTER_AXIS_DIAGNOSTIC
$oldAxisRepair = $env:CODEX_CHARACTER_AXIS_REPAIR
$oldAxisApply = $env:CODEX_CHARACTER_AXIS_APPLY_CANONICAL
$oldAxisBackup = $env:CODEX_CHARACTER_AXIS_BACKUP
try {
    if ($RepairCharacterAnimations) {
        $env:CODEX_ASSET_IMPORT_REPLACE = '1'
        $env:CODEX_ASSET_IMPORT_ONLY = 'human,orc'
    }
    if ($CharacterAxisDiagnostic) { $env:CODEX_CHARACTER_AXIS_DIAGNOSTIC = '1' }
    if ($RepairCharacterAxis) {
        $env:CODEX_CHARACTER_AXIS_DIAGNOSTIC = '1'
        $env:CODEX_CHARACTER_AXIS_REPAIR = '1'
        $env:CODEX_CHARACTER_AXIS_APPLY_CANONICAL = '1'
        $env:CODEX_CHARACTER_AXIS_BACKUP = Join-Path $logs 'asset-backups\20261010-before-animation-axis-normalization'
    }
    $process = Start-Process -FilePath $editor -ArgumentList $arguments -WindowStyle Hidden -PassThru
} finally {
    $env:CODEX_ASSET_IMPORT_REPLACE = $oldReplace
    $env:CODEX_ASSET_IMPORT_ONLY = $oldOnly
    $env:CODEX_CHARACTER_AXIS_DIAGNOSTIC = $oldDiagnostic
    $env:CODEX_CHARACTER_AXIS_REPAIR = $oldAxisRepair
    $env:CODEX_CHARACTER_AXIS_APPLY_CANONICAL = $oldAxisApply
    $env:CODEX_CHARACTER_AXIS_BACKUP = $oldAxisBackup
}
[pscustomobject]@{Utc=(Get-Date).ToUniversalTime().ToString('O');EditorPid=$process.Id;Project=$project;Log=$log;VerificationScript=$script} | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $logs 'last-editor-start.json') -Encoding utf8
Write-Output "Graphical verification editor started: PID $($process.Id), log $log"
