[CmdletBinding()]
param(
    [string]$UvExecutable = 'C:\Users\22499\AppData\Roaming\Python\Python314\Scripts\uv.exe',
    [string]$PythonExecutable = 'C:\Users\22499\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
)
$ErrorActionPreference = 'Stop'
$projectRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..\..')).Path
$runtimeRoot = Join-Path $projectRoot 'tools\runtime\blender-mcp'
$wheelRoot = Join-Path $runtimeRoot 'packages'
$wheelPath = Join-Path $wheelRoot 'mcp_for_blender-2.1.3-py3-none-any.whl'
$wheelUrl = 'https://files.pythonhosted.org/packages/fa/37/f77c0b5f7ae3afdc1653fee46b99f234e722754668121d4888005741ff0d/mcp_for_blender-2.1.3-py3-none-any.whl'
$expectedWheelHash = 'ca4bd001b317019ff888820317c10e8c533f9a31532f980310f82af30c450b20'
$venvRoot = Join-Path $runtimeRoot '.venv'
$venvPython = Join-Path $venvRoot 'Scripts\python.exe'
foreach ($requiredPath in @($UvExecutable, $PythonExecutable)) {
    if (-not (Test-Path -LiteralPath $requiredPath -PathType Leaf)) {
        throw "Required file not found: $requiredPath"
    }
}
New-Item -ItemType Directory -Path $wheelRoot -Force | Out-Null
if (-not (Test-Path -LiteralPath $wheelPath)) {
    Invoke-WebRequest -Uri $wheelUrl -OutFile $wheelPath
}
if ((Get-FileHash -LiteralPath $wheelPath -Algorithm SHA256).Hash.ToLowerInvariant() -ne $expectedWheelHash) {
    throw "Release wheel hash does not match. The existing file was left untouched: $wheelPath"
}
if (-not (Test-Path -LiteralPath $venvPython)) {
    if (Test-Path -LiteralPath $venvRoot) { throw 'A partial .venv exists; it was left untouched.' }
    & $UvExecutable venv --python $PythonExecutable $venvRoot
    if ($LASTEXITCODE -ne 0) { throw 'Virtual environment creation failed.' }
}
$actualPythonVersion = & $venvPython -c 'import sys; print(sys.version.split()[0])'
if ($LASTEXITCODE -ne 0 -or $actualPythonVersion -ne '3.12.14') {
    throw "Expected verified Python 3.12.14; found '$actualPythonVersion'. The environment was left untouched."
}
$env:UV_LINK_MODE = 'copy'
& $UvExecutable pip sync --python $venvPython (Join-Path $runtimeRoot 'requirements.lock')
if ($LASTEXITCODE -ne 0) { throw 'Pinned Blender MCP dependencies could not be synchronized.' }
# Reinstall the exact archived wheel after resolving the locked dependency set.
& $UvExecutable pip install --python $venvPython --reinstall --no-deps $wheelPath
if ($LASTEXITCODE -ne 0) { throw 'Pinned Blender MCP release wheel installation failed.' }
Write-Output "Blender MCP 2.1.3 installed in $venvRoot. Run start-blender-mcp.ps1 next."
