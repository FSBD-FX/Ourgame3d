[CmdletBinding()]
param(
    [string]$BlenderExecutable = 'E:\SteamLibrary\steamapps\common\Blender\blender.exe'
)
$ErrorActionPreference = 'Stop'
$projectRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..\..')).Path
$runtimeRoot = Join-Path $projectRoot 'tools\runtime\blender-mcp'
$profileRoot = Join-Path $runtimeRoot 'blender-profile'
$logRoot = Join-Path $runtimeRoot 'logs'
$serverPython = Join-Path $runtimeRoot '.venv\Scripts\python.exe'
$serverScript = Join-Path $PSScriptRoot 'run-blender-mcp.py'
$bootstrapScript = Join-Path $PSScriptRoot 'blender-bootstrap.py'
foreach ($requiredPath in @($BlenderExecutable, $serverPython, $serverScript, $bootstrapScript)) {
    if (-not (Test-Path -LiteralPath $requiredPath -PathType Leaf)) {
        throw "Required file not found: $requiredPath"
    }
}
$listener = Get-NetTCPConnection -State Listen -LocalPort 9876 -ErrorAction SilentlyContinue
if ($listener) {
    $existingProcess = Get-CimInstance Win32_Process -Filter "ProcessId=$($listener[0].OwningProcess)"
    if ($listener[0].LocalAddress -eq '127.0.0.1' -and $existingProcess.CommandLine.Contains($bootstrapScript)) {
        Write-Output "Project Blender MCP is already listening at 127.0.0.1:9876 (PID $($existingProcess.ProcessId))."
        return
    }
    throw 'Port 9876 is already owned by another process. It was left untouched.'
}
New-Item -ItemType Directory -Path $profileRoot, $logRoot -Force | Out-Null
$env:BLENDER_USER_RESOURCES = $profileRoot
$env:BLENDER_USER_CONFIG = Join-Path $profileRoot 'config'
$env:BLENDER_USER_SCRIPTS = Join-Path $profileRoot 'scripts'
$env:BLENDER_USER_EXTENSIONS = Join-Path $profileRoot 'extensions'
$env:BLENDERMCP_ADDONS_DIR = Join-Path $env:BLENDER_USER_SCRIPTS 'addons'
$env:BLENDERMCP_NO_UPDATE_CHECK = '1'
$env:DISABLE_TELEMETRY = 'true'
$env:BLENDER_MCP_DISABLE_TELEMETRY = 'true'
$env:BLENDER_HOST = '127.0.0.1'
$env:BLENDER_PORT = '9876'
New-Item -ItemType Directory -Path $env:BLENDER_USER_CONFIG, $env:BLENDER_USER_SCRIPTS, $env:BLENDER_USER_EXTENSIONS -Force | Out-Null
& $serverPython $serverScript install-addon --addons-dir $env:BLENDERMCP_ADDONS_DIR
if ($LASTEXITCODE -ne 0) { throw 'Blender addon installation failed.' }
$runStamp = Get-Date -Format 'yyyyMMdd-HHmmss'
$stdoutPath = Join-Path $logRoot "blender-$runStamp.stdout.log"
$stderrPath = Join-Path $logRoot "blender-$runStamp.stderr.log"
$blenderProcess = Start-Process -FilePath $BlenderExecutable -ArgumentList @(
    '--no-window-focus', '--factory-startup', '--python', ('"' + $bootstrapScript + '"')
) -WorkingDirectory $projectRoot -WindowStyle Hidden -RedirectStandardOutput $stdoutPath -RedirectStandardError $stderrPath -PassThru
$blenderProcess.Id | Set-Content -LiteralPath (Join-Path $runtimeRoot 'blender.pid') -Encoding ascii
$deadline = (Get-Date).AddSeconds(45)
do {
    if ($blenderProcess.HasExited) { throw "Blender exited. Inspect $stderrPath and $stdoutPath" }
    $readyListener = Get-NetTCPConnection -State Listen -LocalPort 9876 -ErrorAction SilentlyContinue |
        Where-Object { $_.OwningProcess -eq $blenderProcess.Id -and $_.LocalAddress -eq '127.0.0.1' }
    if ($readyListener) {
        Write-Output "Blender MCP listening at 127.0.0.1:9876 (PID $($blenderProcess.Id))."
        Write-Output "Logs: $stdoutPath ; $stderrPath"
        return
    }
    Start-Sleep -Milliseconds 500
} while ((Get-Date) -lt $deadline)
throw "Blender did not open its local MCP socket within 45 seconds. Inspect $stderrPath and $stdoutPath"
