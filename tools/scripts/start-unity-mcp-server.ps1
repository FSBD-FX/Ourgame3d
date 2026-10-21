param([int]$Port = 8080)
$ErrorActionPreference = 'Stop'
$projectRoot = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\..'))
$serverExe = Join-Path $projectRoot 'tools\runtime\unity-mcp\Scripts\mcp-for-unity.exe'
$logDir = Join-Path $projectRoot 'logs\unity-mcp'
if (-not (Test-Path -LiteralPath $serverExe)) { throw "Missing server environment: $serverExe" }
$listener = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
if ($listener) {
    $health = Invoke-RestMethod -Uri "http://127.0.0.1:$Port/health" -TimeoutSec 5
    if ($health.status -ne 'healthy') { throw "Port $Port belongs to an unexpected service." }
    [pscustomobject]@{status='already_running'; url="http://127.0.0.1:$Port/mcp"; pid=$listener[0].OwningProcess; health=$health} | ConvertTo-Json -Depth 4
    exit 0
}
New-Item -ItemType Directory -Path $logDir -Force | Out-Null
$env:UNITY_MCP_DISABLE_TELEMETRY = 'true'
$env:DISABLE_TELEMETRY = 'true'
$env:UNITY_MCP_LOG_DIR = $logDir
$env:UNITY_MCP_SKIP_STARTUP_CONNECT = 'true'
$launchStamp = Get-Date -Format 'yyyyMMdd-HHmmss-fff'
$pidFile = Join-Path $logDir 'server.pid'
$serverArgs = @('--transport','http','--http-host','127.0.0.1','--http-port',"$Port",'--project-scoped-tools','--pidfile',"`"$pidFile`"")
$process = Start-Process -FilePath $serverExe -ArgumentList $serverArgs -WorkingDirectory $projectRoot -WindowStyle Hidden -RedirectStandardOutput (Join-Path $logDir "$launchStamp.stdout.log") -RedirectStandardError (Join-Path $logDir "$launchStamp.stderr.log") -PassThru
[pscustomobject]@{status='started'; url="http://127.0.0.1:$Port/mcp"; launcher_pid=$process.Id; logs=$logDir; pid_file=$pidFile} | ConvertTo-Json
