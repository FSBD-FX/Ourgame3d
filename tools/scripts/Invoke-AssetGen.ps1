param([Parameter(ValueFromRemainingArguments=$true)][string[]]$GeneratorArgs)
$ErrorActionPreference = 'Stop'
$projectRoot = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\..'))
$pythonExe = Join-Path $projectRoot 'tools\runtime\asset-gen\Scripts\python.exe'
$generator = Join-Path $projectRoot '.agents\skills\asset-gen\tools\asset_gen.py'
if (-not (Test-Path -LiteralPath $pythonExe)) { throw "Missing asset-gen environment: $pythonExe" }
$env:PYTHONUTF8 = '1'
$env:PYTHONIOENCODING = 'utf-8'
Push-Location $projectRoot
try {
    & $pythonExe $generator @GeneratorArgs
    exit $LASTEXITCODE
} finally {
    Pop-Location
}
