[CmdletBinding()]
param(
    [string]$UvExecutable = 'C:\Users\22499\AppData\Roaming\Python\Python314\Scripts\uv.exe',
    [string]$PythonExecutable = 'C:\Users\22499\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
)
$ErrorActionPreference = 'Stop'
$projectRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..\..')).Path
$sourceRoot = Join-Path $projectRoot 'tools\unreal-mcp'
$runtimeRoot = Join-Path $projectRoot 'tools\runtime\unreal-mcp'
$venvRoot = Join-Path $runtimeRoot '.venv'
$venvPython = Join-Path $venvRoot 'Scripts\python.exe'
$expectedCommit = '4e5f00da50733190481311e254d16d137a84ef33'
$actualCommit = git -C $sourceRoot rev-parse HEAD
if ($LASTEXITCODE -ne 0 -or $actualCommit -ne $expectedCommit) {
    throw "Expected Unreal MCP checkout $expectedCommit; source was left untouched."
}
foreach ($requiredPath in @($UvExecutable, $PythonExecutable)) {
    if (-not (Test-Path -LiteralPath $requiredPath -PathType Leaf)) { throw "Required file not found: $requiredPath" }
}
New-Item -ItemType Directory -Path (Join-Path $runtimeRoot 'logs') -Force | Out-Null
if (-not (Test-Path -LiteralPath $venvPython)) {
    if (Test-Path -LiteralPath $venvRoot) { throw 'A partial Unreal MCP .venv exists; it was left untouched.' }
    & $UvExecutable venv --python $PythonExecutable $venvRoot
    if ($LASTEXITCODE -ne 0) { throw 'Unreal MCP environment creation failed.' }
}
$actualPythonVersion = & $venvPython -c 'import sys; print(sys.version.split()[0])'
if ($LASTEXITCODE -ne 0 -or $actualPythonVersion -ne '3.12.14') { throw 'Expected verified Python 3.12.14.' }
$env:UV_PROJECT_ENVIRONMENT = $venvRoot
$env:UV_LINK_MODE = 'copy'
& $UvExecutable sync --directory (Join-Path $sourceRoot 'Python') --frozen --no-install-project
if ($LASTEXITCODE -ne 0) { throw 'Pinned upstream Unreal MCP dependencies failed to install.' }
& $UvExecutable pip check --python $venvPython
if ($LASTEXITCODE -ne 0) { throw 'Unreal MCP dependency check failed.' }
Write-Output "Unreal MCP Python environment ready: $venvPython"
