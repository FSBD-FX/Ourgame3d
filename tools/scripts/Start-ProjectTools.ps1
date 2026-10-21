[CmdletBinding()]
param([string]$EngineRoot = 'G:\UE_5.5')
$ErrorActionPreference = 'Stop'
$workspace = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\..'))
$projectFile = Join-Path $workspace 'UnrealGame\CodexDungeon.uproject'
$requiredFiles = @(
    $projectFile,
    (Join-Path $EngineRoot 'Engine\Binaries\Win64\UnrealEditor.exe'),
    (Join-Path $workspace 'UnrealGame\Binaries\Win64\UnrealEditor-CodexDungeon.dll'),
    (Join-Path $workspace 'UnrealGame\Plugins\UnrealMCP\Binaries\Win64\UnrealEditor-UnrealMCP.dll'),
    (Join-Path $PSScriptRoot 'start-blender-mcp.ps1'),
    (Join-Path $PSScriptRoot 'unreal-open.ps1')
)
foreach ($requiredFile in $requiredFiles) {
    if (-not (Test-Path -LiteralPath $requiredFile -PathType Leaf)) {
        throw "Required file missing: $requiredFile. Build the Unreal Editor target first if its DLL is missing."
    }
}
$unrealListener = @(Get-NetTCPConnection -LocalPort 55557 -State Listen -ErrorAction SilentlyContinue)
foreach ($connection in $unrealListener) {
    $ownerProcess = Get-CimInstance Win32_Process -Filter "ProcessId=$($connection.OwningProcess)"
    if ($connection.LocalAddress -ne '127.0.0.1' -or -not $ownerProcess.CommandLine -or -not $ownerProcess.CommandLine.Contains($projectFile)) {
        throw 'Port 55557 belongs to another process. It has been left untouched.'
    }
}
& (Join-Path $PSScriptRoot 'start-blender-mcp.ps1')
& (Join-Path $PSScriptRoot 'unreal-open.ps1') -EngineRoot $EngineRoot
Write-Output 'Blender and Unreal Editor launch requested. Codex owns the STDIO MCP server processes.'
Write-Output 'Use unreal-status.ps1 and verify-unreal-mcp.py --global-config to check readiness after startup.'
